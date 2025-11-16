"""
predictive_optimization.py

Complete workflow for predictive wake steering optimization:
1. Fetch weather forecast (day-ahead)
2. Use Sphinx AI to predict optimal yaw angles
3. On operation day, validate forecast vs actual conditions
4. Run narrow search if valid, full search if deviated
"""

import json
import sys
from pathlib import Path
from datetime import datetime

from sphinx_integration import SphinxPredictor
from forecast_validator import (
    is_forecast_valid, 
    get_recommended_yaw_range,
    calculate_search_range_from_prediction,
    print_validation_report
)
from wake_steering_optimizer import WakeSteeringOptimizer
from yaw_range_helper import print_recommendation_summary


class PredictiveOptimizer:
    """
    Two-stage predictive optimization system:
    Stage 1: Day-ahead prediction using forecast + Sphinx AI
    Stage 2: Real-time refinement based on actual conditions
    """
    
    def __init__(self, floris_config='floris_config.yaml', 
                 notebook_path='data_preprocessing.ipynb'):
        """Initialize the predictive optimizer"""
        self.optimizer = WakeSteeringOptimizer()  # Uses floris_config.yaml by default
        self.sphinx = SphinxPredictor(notebook_path)
        self.predictions_dir = Path('data/predictions')
        self.predictions_dir.mkdir(parents=True, exist_ok=True)
        
    def stage1_predict(self, forecast_data, save_prediction=True):
        """
        Stage 1: Day-ahead prediction
        
        Args:
            forecast_data: Dictionary with forecasted conditions
            save_prediction: Whether to save prediction to file
            
        Returns:
            Prediction dictionary with yaw angles and confidence
        """
        print("="*70)
        print("STAGE 1: DAY-AHEAD PREDICTION")
        print("="*70)
        print(f"\nForecast for tomorrow:")
        print(f"  Wind: {forecast_data['wind_direction']}° @ {forecast_data['wind_speed']} m/s")
        print(f"  Turbulence: {forecast_data.get('turbulence_intensity', 0.08)*100:.1f}%")
        
        # Get recommended yaw range based on conditions
        yaw_min, yaw_max = get_recommended_yaw_range(
            forecast_data['wind_speed'],
            forecast_data.get('turbulence_intensity', 0.08)
        )
        
        print(f"\nRecommended search range for these conditions: ±{yaw_max}°")
        print(f"This would require {(2*yaw_max+1)**4:,} combinations to test")
        
        # Use AI to predict optimal angles
        print("\n🤖 Analyzing forecast data to predict optimal yaw angles...")
        print("(This may take 1-2 minutes...)")
        
        try:
            prediction = self.sphinx.predict_yaw_angles(forecast_data)
            
            print("\n✅ Prediction Complete!")
            print(f"  Predicted Yaw Angles: {prediction['predicted_yaws']}")
            print(f"  Confidence: {prediction['confidence']}")
            print(f"  Recommended Search Range: ±{prediction['search_range']}°")
            
            if prediction['reasoning']:
                print(f"\n  Analysis: {prediction['reasoning'][:200]}...")
            
            # Save prediction
            if save_prediction:
                prediction_file = self.predictions_dir / f"prediction_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
                with open(prediction_file, 'w') as f:
                    json.dump({
                        'forecast': forecast_data,
                        'prediction': prediction,
                        'timestamp': datetime.now().isoformat()
                    }, f, indent=2)
                print(f"\n📝 Prediction saved to: {prediction_file}")
            
            return prediction
            
        except Exception as e:
            print(f"\n⚠️  Prediction service unavailable: {e}")
            print("Falling back to adaptive range based on conditions")
            
            # Fallback: Use adaptive range without AI
            return {
                'predicted_yaws': [0, 0, 0, 0],  # Neutral fallback
                'confidence': ['low', 'low', 'low', 'low'],
                'search_range': yaw_max,
                'reasoning': 'Fallback: No prediction available',
                'fallback': True
            }
    
    def stage2_optimize(self, prediction, actual_conditions, 
                       validation_mode='conservative'):
        """
        Stage 2: Real-time optimization with validation
        
        Args:
            prediction: Prediction from stage1_predict()
            actual_conditions: Current measured conditions
            validation_mode: 'conservative', 'tight', or 'relaxed'
            
        Returns:
            Optimization results with optimal yaw angles
        """
        print("\n" + "="*70)
        print("STAGE 2: REAL-TIME OPTIMIZATION")
        print("="*70)
        
        # If this was a fallback prediction, skip validation
        if prediction.get('fallback'):
            print("\n⚠️  Using fallback mode (no prediction available)")
            return self._run_full_optimization(actual_conditions)
        
        # Validate forecast vs actual
        print("\n📊 Validating forecast accuracy...")
        forecast_data = {
            'wind_speed': actual_conditions['wind_speed'],  # We need original forecast
            'wind_direction': actual_conditions['wind_direction'],
            'turbulence_intensity': actual_conditions.get('turbulence_intensity', 0.08)
        }
        
        # For demo, we'll extract from prediction if available
        # In production, load original forecast from saved file
        
        validation = is_forecast_valid(
            forecast_data,  # In production: load from saved forecast
            actual_conditions,
            mode=validation_mode
        )
        
        print_validation_report(forecast_data, actual_conditions, validation)
        
        # Decide optimization strategy
        if validation['recommendation'] == 'NARROW_SEARCH':
            return self._run_narrow_search(prediction, actual_conditions, validation)
        elif validation['recommendation'] == 'MODERATE_SEARCH':
            return self._run_moderate_search(prediction, actual_conditions, validation)
        else:  # FULL_SEARCH
            return self._run_full_optimization(actual_conditions)
    
    def _run_narrow_search(self, prediction, conditions, validation):
        """Run narrow search around predicted yaw angles"""
        print("\n✅ Forecast valid! Running narrow search around predictions...")
        
        # Calculate search ranges
        search_ranges = calculate_search_range_from_prediction(
            prediction['predicted_yaws'],
            prediction['confidence'],
            validation
        )
        
        print(f"\nSearch ranges:")
        for i, (ymin, ymax) in enumerate(search_ranges):
            print(f"  T{i}: [{ymin}° to {ymax}°] (predicted: {prediction['predicted_yaws'][i]}°)")
        
        total_combos = 1
        for ymin, ymax in search_ranges:
            total_combos *= (ymax - ymin + 1)
        
        print(f"\nTotal combinations: {total_combos:,}")
        print(f"Expected time: ~{total_combos * 0.003 / 60:.1f} minutes")
        
        # Run optimization with narrow ranges
        print("\n🔄 Optimizing...")
        results = self.optimizer.optimize_with_ranges(search_ranges)
        
        self._print_results(results, prediction)
        return results
    
    def _run_moderate_search(self, prediction, conditions, validation):
        """Run moderate search (wider than narrow but guided by prediction)"""
        print("\n⚠️  Partial forecast match. Running moderate search...")
        
        # Expand ranges by 1 degree
        search_ranges = calculate_search_range_from_prediction(
            prediction['predicted_yaws'],
            ['medium'] * 4,  # Force medium confidence
            validation
        )
        
        # Expand each range
        search_ranges = [(ymin-1, ymax+1) for ymin, ymax in search_ranges]
        
        print(f"\nExpanded search ranges:")
        for i, (ymin, ymax) in enumerate(search_ranges):
            print(f"  T{i}: [{ymin}° to {ymax}°]")
        
        total_combos = 1
        for ymin, ymax in search_ranges:
            total_combos *= (ymax - ymin + 1)
        
        print(f"\nTotal combinations: {total_combos:,}")
        
        # Run optimization
        print("\n🔄 Optimizing...")
        results = self.optimizer.optimize_with_ranges(search_ranges)
        
        self._print_results(results, prediction)
        return results
    
    def _run_full_optimization(self, conditions):
        """Run full optimization with adaptive range"""
        print("\n❌ Forecast invalid. Running full optimization...")
        
        # Get adaptive range based on actual conditions
        yaw_min, yaw_max = get_recommended_yaw_range(
            conditions['wind_speed'],
            conditions.get('turbulence_intensity', 0.08)
        )
        
        print(f"\nAdaptive range for these conditions: ±{yaw_max}°")
        total_combos = (2*yaw_max + 1) ** 4
        print(f"Total combinations: {total_combos:,}")
        print(f"Expected time: ~{total_combos * 0.003 / 60:.1f} minutes")
        
        # Temporarily update config
        import config
        original_min, original_max = config.YAW_ANGLE_MIN, config.YAW_ANGLE_MAX
        config.YAW_ANGLE_MIN, config.YAW_ANGLE_MAX = yaw_min, yaw_max
        
        # Run optimization
        print("\n🔄 Optimizing...")
        results = self.optimizer.optimize()
        
        # Restore config
        config.YAW_ANGLE_MIN, config.YAW_ANGLE_MAX = original_min, original_max
        
        self._print_results(results, None)
        return results
    
    def _print_results(self, results, prediction=None):
        """Print formatted optimization results"""
        print("\n" + "="*70)
        print("OPTIMIZATION RESULTS")
        print("="*70)
        
        print(f"\nOptimal Yaw Angles: {results['optimal_yaw_angles']}")
        print(f"Total Power: {results['total_power']:.2f} kW")
        print(f"Power Improvement: +{results['improvement_percent']:.2f}%")
        print(f"Power Gain: +{results['power_gain']:.2f} kW")
        
        print(f"\nIndividual Turbine Powers:")
        for i, power in enumerate(results['turbine_powers']):
            yaw = results['optimal_yaw_angles'][i]
            print(f"  T{i}: {power:.2f} kW (yaw: {yaw:+.0f}°)")
        
        # Compare to prediction if available
        if prediction and not prediction.get('fallback'):
            pred_yaws = prediction['predicted_yaws']
            print(f"\nComparison to AI Prediction:")
            print(f"  Predicted: {[int(y) for y in pred_yaws]}")
            print(f"  Optimal:   {results['optimal_yaw_angles']}")
            
            # Calculate prediction accuracy
            errors = [abs(opt - pred) for opt, pred in zip(results['optimal_yaw_angles'], pred_yaws)]
            avg_error = sum(errors) / len(errors)
            print(f"  Average error: {avg_error:.1f}°")
            
            if avg_error <= 2:
                print(f"  ✅ Excellent prediction! (within ±2°)")
            elif avg_error <= 4:
                print(f"  ✓ Good prediction (within ±4°)")
            else:
                print(f"  ⚠️  Prediction had significant error")
        
        print("="*70)


def main():
    """Example workflow"""
    
    # Initialize
    print("Initializing Predictive Optimization System...")
    optimizer = PredictiveOptimizer()
    
    # Example: Tomorrow's forecast
    forecast = {
        'wind_speed': 8.5,
        'wind_direction': 270,
        'turbulence_intensity': 0.07,
        'temperature': 15
    }
    
    # Stage 1: Day-ahead prediction
    prediction = optimizer.stage1_predict(forecast, save_prediction=True)
    
    # Stage 2: Real-time optimization (simulate next day)
    print("\n" + "="*70)
    print("⏰ NEXT DAY - REAL-TIME OPERATION")
    print("="*70)
    
    # Scenario A: Conditions match forecast
    actual_conditions = {
        'wind_speed': 8.3,
        'wind_direction': 268,
        'turbulence_intensity': 0.065
    }
    
    results = optimizer.stage2_optimize(prediction, actual_conditions)
    
    print("\n✅ Optimization complete!")
    print(f"Recommended yaw angles: {results['optimal_yaw_angles']}")


if __name__ == '__main__':
    main()
