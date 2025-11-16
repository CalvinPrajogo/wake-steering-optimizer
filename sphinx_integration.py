"""
sphinx_integration.py

Integration module for Sphinx AI CLI to predict optimal yaw angles
based on weather forecast data.

Sphinx AI uses the CLI tool to analyze notebooks and provide predictions.
This module wraps the sphinx-cli commands to work with our optimization pipeline.
"""

import subprocess
import json
import os
from pathlib import Path
from datetime import datetime
import tempfile


class SphinxPredictor:
    """
    Interface to Sphinx AI for predicting optimal yaw angles
    based on weather forecast data.
    """
    
    def __init__(self, notebook_path='data_preprocessing.ipynb', api_key=None):
        """
        Initialize Sphinx AI predictor
        
        Args:
            notebook_path: Path to the Jupyter notebook for Sphinx to work with
            api_key: Optional Sphinx AI API key for programmatic access
                    If None, will use interactive browser login
        """
        self.notebook_path = Path(notebook_path)
        self.api_key = api_key or os.getenv('SPHINX_API_KEY')
        
        if not self.notebook_path.exists():
            raise FileNotFoundError(f"Notebook not found: {self.notebook_path}")
    
    def predict_yaw_angles(self, forecast_data, historical_results=None):
        """
        Use Sphinx AI to predict optimal yaw angles based on forecast
        
        Args:
            forecast_data: Dictionary with wind_speed, wind_direction, turbulence_intensity
            historical_results: Optional historical optimization results for training
            
        Returns:
            Dictionary with:
                - predicted_yaws: List of predicted yaw angles [T0, T1, T2, T3]
                - confidence: Confidence scores for each prediction
                - search_range: Recommended search range around predictions
        """
        # Create prompt for Sphinx AI
        prompt = self._create_prediction_prompt(forecast_data, historical_results)
        
        # Run Sphinx CLI
        result = self._run_sphinx_cli(prompt)
        
        # Parse Sphinx's response
        prediction = self._parse_sphinx_response(result)
        
        return prediction
    
    def analyze_forecast_accuracy(self, forecast_data, actual_data, optimal_yaws):
        """
        Use Sphinx AI to analyze forecast accuracy and learn patterns
        
        Args:
            forecast_data: Dictionary with forecasted conditions
            actual_data: Dictionary with actual measured conditions
            optimal_yaws: List of optimal yaw angles found for actual conditions
            
        Returns:
            Analysis results and updated predictions
        """
        prompt = f"""
        Analyze this forecast vs actual comparison:
        
        Forecasted Conditions:
        - Wind Speed: {forecast_data['wind_speed']} m/s
        - Wind Direction: {forecast_data['wind_direction']}°
        - Turbulence: {forecast_data.get('turbulence_intensity', 'estimated')}
        
        Actual Conditions:
        - Wind Speed: {actual_data['wind_speed']} m/s
        - Wind Direction: {actual_data['wind_direction']}°
        - Turbulence: {actual_data.get('turbulence_intensity', 'measured')}
        
        Optimal Yaw Angles Found:
        - Turbine 0: {optimal_yaws[0]}°
        - Turbine 1: {optimal_yaws[1]}°
        - Turbine 2: {optimal_yaws[2]}°
        - Turbine 3: {optimal_yaws[3]}°
        
        Questions:
        1. How accurate was the forecast? Calculate deviation metrics.
        2. Would the predicted yaw angles have been close to optimal?
        3. What patterns can we learn from this comparison?
        4. Update the prediction model based on this feedback.
        """
        
        return self._run_sphinx_cli(prompt)
    
    def determine_optimal_search_range(self, forecast_data):
        """
        Use Sphinx AI to determine optimal yaw search range based on conditions
        
        Args:
            forecast_data: Dictionary with wind conditions
            
        Returns:
            Recommended yaw range (e.g., 5 for ±5°)
        """
        prompt = f"""
        Based on these forecasted wind conditions, determine the optimal yaw angle search range:
        
        Wind Speed: {forecast_data['wind_speed']} m/s
        Wind Direction: {forecast_data['wind_direction']}°
        Turbulence Intensity: {forecast_data.get('turbulence_intensity', 0.08)}
        
        Use the yaw_range_helper.py functions to:
        1. Calculate expected power loss at different yaw angles
        2. Estimate computation time for different search ranges
        3. Recommend optimal range balancing accuracy vs computation time
        
        Consider:
        - Low wind + low TI → larger range (±10° to ±12°)
        - Medium wind + medium TI → standard range (±5° to ±8°)
        - High wind or high TI → smaller range (±3° to ±5°)
        
        Return your recommendation as a single integer (e.g., 5 for ±5°).
        """
        
        result = self._run_sphinx_cli(prompt)
        
        # Extract recommended range from response
        try:
            # Look for number in response
            import re
            match = re.search(r'±?(\d+)°?', result)
            if match:
                return int(match.group(1))
            else:
                return 5  # Default fallback
        except:
            return 5  # Default fallback
    
    def _create_prediction_prompt(self, forecast_data, historical_results=None):
        """Create detailed prompt for Sphinx AI to predict yaw angles"""
        
        prompt = f"""
        Predict optimal yaw angles for a 4-turbine wind farm based on these forecasted conditions:
        
        Forecast Data:
        - Wind Speed: {forecast_data['wind_speed']} m/s
        - Wind Direction: {forecast_data['wind_direction']}°
        - Turbulence Intensity: {forecast_data.get('turbulence_intensity', 'estimate from data')}
        - Temperature: {forecast_data.get('temperature', 'N/A')}°C
        
        Turbine Layout:
        - T0: (0, 0) - Upstream left
        - T1: (0, 630) - Upstream right  
        - T2: (630, 0) - Downstream left
        - T3: (630, 630) - Downstream right
        
        Wind is from {forecast_data['wind_direction']}° (270° = West, directly aligned with turbine rows)
        
        Tasks:
        1. Load and analyze the historical NREL wind data if available
        2. Find similar historical conditions (wind speed ±1 m/s, direction ±10°)
        3. Analyze what yaw angles worked best for those conditions
        4. Predict optimal yaw angles for each turbine [T0, T1, T2, T3]
        5. Provide confidence level (high/medium/low) for each prediction
        6. Suggest search range around predictions (±1° for high confidence, ±2° for medium, ±3° for low)
        
        """
        
        if historical_results:
            prompt += f"\n\nHistorical Results Available:\n{json.dumps(historical_results, indent=2)}\n"
        
        prompt += """
        Return your prediction in this format:
        Predicted Yaw Angles: [T0, T1, T2, T3]
        Confidence: [high/medium/low for each turbine]
        Recommended Search Range: ±X°
        Reasoning: <explanation>
        """
        
        return prompt
    
    def _run_sphinx_cli(self, prompt, timeout=300):
        """
        Execute sphinx-cli command
        
        Args:
            prompt: The prompt to send to Sphinx AI
            timeout: Maximum execution time in seconds
            
        Returns:
            Sphinx AI response as string
        """
        # Build command
        cmd = [
            'sphinx-cli', 'chat',
            '--notebook-filepath', str(self.notebook_path),
            '--prompt', prompt
        ]
        
        # Add API key if available (for programmatic use)
        if self.api_key:
            cmd.extend(['--api-key', self.api_key])
        
        # Add environment variables
        env = os.environ.copy()
        if self.api_key:
            env['SPHINX_API_KEY'] = self.api_key
        
        try:
            # Run sphinx-cli
            result = subprocess.run(
                cmd,
                capture_output=True,
                text=True,
                timeout=timeout,
                env=env
            )
            
            if result.returncode != 0:
                raise RuntimeError(f"Sphinx CLI failed: {result.stderr}")
            
            return result.stdout
            
        except subprocess.TimeoutExpired:
            raise TimeoutError(f"Sphinx CLI timed out after {timeout} seconds")
        except FileNotFoundError:
            raise RuntimeError(
                "sphinx-cli not found. Install with: pip install sphinx-ai-cli"
            )
    
    def _parse_sphinx_response(self, response):
        """
        Parse Sphinx AI response to extract predictions
        
        Args:
            response: Raw text response from Sphinx CLI
            
        Returns:
            Dictionary with parsed predictions
        """
        # Initialize default values
        prediction = {
            'predicted_yaws': [0, 0, 0, 0],
            'confidence': ['medium', 'medium', 'medium', 'medium'],
            'search_range': 2,
            'reasoning': '',
            'raw_response': response
        }
        
        try:
            # Look for predicted yaw angles in format: [a, b, c, d]
            import re
            
            # Extract yaw angles
            yaw_match = re.search(r'Predicted Yaw Angles?:\s*\[([^\]]+)\]', response, re.IGNORECASE)
            if yaw_match:
                yaw_str = yaw_match.group(1)
                yaws = [float(x.strip().replace('°', '')) for x in yaw_str.split(',')]
                if len(yaws) == 4:
                    prediction['predicted_yaws'] = yaws
            
            # Extract search range
            range_match = re.search(r'Search Range:\s*±?(\d+)°?', response, re.IGNORECASE)
            if range_match:
                prediction['search_range'] = int(range_match.group(1))
            
            # Extract confidence levels
            conf_match = re.search(r'Confidence:\s*\[([^\]]+)\]', response, re.IGNORECASE)
            if conf_match:
                conf_str = conf_match.group(1)
                confidences = [x.strip().lower() for x in conf_str.split(',')]
                if len(confidences) == 4:
                    prediction['confidence'] = confidences
            
            # Extract reasoning
            reason_match = re.search(r'Reasoning:\s*(.+?)(?:\n\n|\Z)', response, re.IGNORECASE | re.DOTALL)
            if reason_match:
                prediction['reasoning'] = reason_match.group(1).strip()
            
        except Exception as e:
            print(f"Warning: Could not fully parse Sphinx response: {e}")
            print(f"Raw response: {response}")
        
        return prediction


def create_sphinx_training_data(optimization_results, output_file='data/processed/sphinx_training_data.json'):
    """
    Format optimization results for Sphinx AI training
    
    Args:
        optimization_results: List of dicts with conditions and optimal yaws
        output_file: Where to save training data
    """
    training_data = {
        'created_at': datetime.now().isoformat(),
        'description': 'Historical wind conditions and optimal yaw angles for training',
        'data': optimization_results
    }
    
    output_path = Path(output_file)
    output_path.parent.mkdir(parents=True, exist_ok=True)
    
    with open(output_path, 'w') as f:
        json.dump(training_data, f, indent=2)
    
    print(f"Training data saved to: {output_path}")
    return output_path


# Example usage
if __name__ == '__main__':
    # Example: Predict yaw angles for tomorrow's forecast
    
    # Load forecast data (from weather_forecast.py output)
    forecast = {
        'wind_speed': 8.5,
        'wind_direction': 270,
        'turbulence_intensity': 0.07,
        'temperature': 15
    }
    
    print("Initializing Sphinx AI predictor...")
    predictor = SphinxPredictor(notebook_path='data_preprocessing.ipynb')
    
    print("\nAsking Sphinx AI to predict optimal yaw angles...")
    print(f"Forecast: {forecast['wind_direction']}° @ {forecast['wind_speed']} m/s, TI={forecast['turbulence_intensity']}")
    
    try:
        prediction = predictor.predict_yaw_angles(forecast)
        
        print("\n" + "="*60)
        print("SPHINX AI PREDICTION")
        print("="*60)
        print(f"Predicted Yaw Angles: {prediction['predicted_yaws']}")
        print(f"Confidence: {prediction['confidence']}")
        print(f"Recommended Search Range: ±{prediction['search_range']}°")
        print(f"\nReasoning:\n{prediction['reasoning']}")
        print("="*60)
        
    except Exception as e:
        print(f"Error: {e}")
        print("\nNote: Make sure sphinx-cli is installed and you're logged in:")
        print("  pip install sphinx-ai-cli")
        print("  sphinx-cli login")
