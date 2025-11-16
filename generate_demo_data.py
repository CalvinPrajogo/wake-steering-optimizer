"""
generate_demo_data.py

Generates demo data for UI by:
1. Processing forecast data and getting Sphinx AI predictions
2. Processing first 6 hours of NREL data as "live" sensor data
3. Running narrow search optimization based on predictions
4. Saving predicted vs actual yaw angles for UI display
"""

import json
import pandas as pd
import numpy as np
from pathlib import Path
from datetime import datetime
import sys

# Force unbuffered output
sys.stdout.reconfigure(line_buffering=True)

# Add current directory to path for imports
sys.path.insert(0, str(Path(__file__).parent))

from sphinx_integration import SphinxPredictor
from wake_steering_optimizer import WakeSteeringOptimizer
from forecast_validator import get_recommended_yaw_range

# Create processed data directory
PROCESSED_DIR = Path('data/processed')
PROCESSED_DIR.mkdir(parents=True, exist_ok=True)

def load_and_clean_forecast():
    """Load and clean forecast data"""
    print("\n" + "="*70)
    print("STEP 1: Loading and Cleaning Forecast Data")
    print("="*70)
    
    forecast_path = Path('data/raw/forecast_data_2012-01-01_2012-01-01.json')
    
    with open(forecast_path, 'r') as f:
        forecast_raw = json.load(f)
    
    # Extract hourly data
    hours = forecast_raw['days'][0]['hours']
    
    forecast_data = []
    for hour in hours:
        forecast_data.append({
            'datetime': f"2012-01-01 {hour['datetime']}",
            'hour': int(hour['datetime'].split(':')[0]),
            'wind_speed': hour['windspeed'],
            'wind_direction': hour['winddir'],
            'turbulence_intensity': 0.06  # Typical value
        })
    
    df_forecast = pd.DataFrame(forecast_data)
    
    # Save cleaned forecast
    output_path = PROCESSED_DIR / 'forecast_cleaned_2012-01-01.csv'
    df_forecast.to_csv(output_path, index=False)
    
    print(f"✅ Cleaned forecast data saved to {output_path}")
    print(f"   Hours: {len(df_forecast)}")
    print(f"   Wind Speed Range: {df_forecast['wind_speed'].min():.1f} - {df_forecast['wind_speed'].max():.1f} m/s")
    print(f"\n   First 6 hours preview:")
    print(df_forecast.head(6)[['hour', 'wind_speed', 'wind_direction']].to_string(index=False))
    
    return df_forecast


def get_sphinx_predictions(forecast_df):
    """Get optimal yaw angles by running FULL optimization on forecast data"""
    print("\n" + "="*70)
    print("STEP 2: Pre-computing Optimal Yaw Angles from Forecast")
    print("         (Running full optimization on forecasted conditions)")
    print("="*70)
    
    predictions = []
    
    print(f"\n⏳ Optimizing for {len(forecast_df)} forecasted hours...")
    print("   This simulates the day-ahead batch processing")
    
    for idx, row in forecast_df.iterrows():
        forecast_ws = row['wind_speed']
        forecast_wd = row['wind_direction']
        forecast_ti = row['turbulence_intensity']
        
        print(f"\n  Hour {row['hour']:02d}: WS={forecast_ws:.1f} m/s, WD={forecast_wd:.0f}°")
        print(f"    ⏳ Running full optimization on forecast conditions...")
        
        try:
            # Initialize optimizer with FORECAST conditions
            optimizer = WakeSteeringOptimizer(
                wind_direction=forecast_wd,
                wind_speed=forecast_ws
            )
            
            # Run FULL optimization on forecast (±5° range)
            yaw_range = range(-5, 6, 1)  # -5 to 5 degrees
            result = optimizer.optimize(yaw_range=yaw_range, progress_interval=1000)
            
            optimal_yaw = result['optimal_yaw_angles']
            power = result['optimal_power']
            
            print(f"    ✓ Optimal yaw from forecast: {optimal_yaw}")
            print(f"    ✓ Expected power: {power:.2f} kW")
            
            predictions.append({
                'hour': row['hour'],
                'datetime': row['datetime'],
                'predicted_yaw_t1': optimal_yaw[0],
                'predicted_yaw_t2': optimal_yaw[1],
                'predicted_yaw_t3': optimal_yaw[2],
                'predicted_yaw_t4': optimal_yaw[3],
                'predicted_yaw_t5': optimal_yaw[4],
                'confidence': 'high',  # High confidence from full optimization
                'expected_power': power,
                'wind_speed': forecast_ws,
                'wind_direction': forecast_wd
            })
            
        except Exception as e:
            print(f"    ✗ Error: {e}")
            import traceback
            traceback.print_exc()
            # Use neutral angles as fallback (5 turbines)
            predictions.append({
                'hour': row['hour'],
                'datetime': row['datetime'],
                'predicted_yaw_t1': 0,
                'predicted_yaw_t2': 0,
                'predicted_yaw_t3': 0,
                'predicted_yaw_t4': 0,
                'predicted_yaw_t5': 0,
                'confidence': 'low',
                'expected_power': 0,
                'wind_speed': forecast_ws,
                'wind_direction': forecast_wd
            })
            continue  # Skip to next hour
    
    df_predictions = pd.DataFrame(predictions)
    
    # Save predictions
    output_path = PROCESSED_DIR / 'forecast_optimized_yaw_angles.csv'
    df_predictions.to_csv(output_path, index=False)
    
    print(f"\n✅ Pre-computed optimal yaw angles saved to {output_path}")
    print(f"   This represents the 'day-ahead' batch optimization")
    
    return df_predictions


def load_and_clean_nrel_data(num_hours=6):
    """Load and clean first N hours of NREL data"""
    print("\n" + "="*70)
    print(f"STEP 3: Loading NREL 'Live' Sensor Data (First {num_hours} Hours)")
    print("="*70)
    
    nrel_path = Path('data/raw/nrel_wtk_2012_100m_raw.csv')
    
    # Skip metadata row, use second row as header
    df_nrel = pd.read_csv(nrel_path, skiprows=1)
    
    # Get first N hours (30-minute intervals, so 2 rows per hour)
    df_nrel_subset = df_nrel.head(num_hours * 2)
    
    # Aggregate to hourly (take first measurement of each hour)
    df_hourly = df_nrel_subset[df_nrel_subset['Minute'] == 30].copy()
    df_hourly = df_hourly.head(num_hours)
    
    # Clean column names
    df_hourly = df_hourly.rename(columns={
        'wind speed at 100m (m/s)': 'wind_speed',
        'wind direction at 100m (deg)': 'wind_direction',
        'air temperature at 100m (C)': 'temperature',
        'air pressure at 100m (Pa)': 'pressure'
    })
    
    df_hourly['hour'] = df_hourly['Hour']
    df_hourly['turbulence_intensity'] = 0.06  # Typical value
    
    # Save cleaned NREL data
    output_path = PROCESSED_DIR / 'nrel_live_first_6hours.csv'
    df_hourly[['hour', 'wind_speed', 'wind_direction', 'temperature', 'pressure', 'turbulence_intensity']].to_csv(
        output_path, index=False
    )
    
    print(f"✅ Cleaned NREL data saved to {output_path}")
    print(f"\n   Live sensor data:")
    print(df_hourly[['hour', 'wind_speed', 'wind_direction']].to_string(index=False))
    
    return df_hourly


def run_narrow_search_optimization(predictions_df, nrel_df):
    """Run narrow search optimization for first 6 hours using pre-computed angles"""
    print("\n" + "="*70)
    print("STEP 4: Real-Time Narrow Search Optimization")
    print("         (Using pre-computed angles from forecast)")
    print("="*70)
    
    results = []
    
    for idx in range(len(nrel_df)):
        hour = int(nrel_df.iloc[idx]['hour'])
        
        # Get live conditions
        live_ws = nrel_df.iloc[idx]['wind_speed']
        live_wd = nrel_df.iloc[idx]['wind_direction']
        live_ti = nrel_df.iloc[idx]['turbulence_intensity']
        
        # Get pre-computed optimal angles for this hour
        pred_row = predictions_df[predictions_df['hour'] == hour].iloc[0]
        predicted_yaw = [
            pred_row['predicted_yaw_t1'],
            pred_row['predicted_yaw_t2'],
            pred_row['predicted_yaw_t3'],
            pred_row['predicted_yaw_t4'],
            pred_row['predicted_yaw_t5']
        ]
        
        print(f"\n  Hour {hour:02d}:")
        print(f"    Forecast used: WS={pred_row['wind_speed']:.1f} m/s, WD={pred_row['wind_direction']:.0f}°")
        print(f"    Live conditions: WS={live_ws:.2f} m/s, WD={live_wd:.2f}°")
        print(f"    Pre-computed optimal yaw: {predicted_yaw}")
        
        # Determine narrow search range width based on atmospheric conditions
        # Uses physics-based logic: high wind/TI = smaller range, low wind/TI = larger range
        yaw_range = get_recommended_yaw_range(live_ws, live_ti)
        range_width = (yaw_range[1] - yaw_range[0]) // 2  # Convert full range to half-width
        # For narrow search, use half of the recommended full range (more conservative)
        narrow_range_width = max(2, range_width // 2)  # At least ±2°
        
        print(f"    Atmospheric-based range width: ±{narrow_range_width}° (WS={live_ws:.1f} m/s, TI={live_ti*100:.1f}%)")
        
        # Calculate narrow search ranges using intelligent width
        search_ranges = []
        for pred_yaw in predicted_yaw:
            yaw_min = int(pred_yaw - narrow_range_width)
            yaw_max = int(pred_yaw + narrow_range_width)
            # Clamp to reasonable bounds
            yaw_min = max(-15, yaw_min)
            yaw_max = min(15, yaw_max)
            search_ranges.append((yaw_min, yaw_max))
        
        print(f"    Narrow search ranges: {search_ranges}")
        
        # Initialize optimizer with LIVE conditions
        optimizer = WakeSteeringOptimizer(
            wind_direction=live_wd,
            wind_speed=live_ws
        )
        
        # Run narrow search
        print(f"    ⏳ Optimizing with narrow search...")
        result = optimizer.optimize_with_ranges(search_ranges, progress_interval=500)
        
        actual_yaw = result['optimal_yaw_angles']
        power = result['optimal_power']
        
        print(f"    ✓ Actual optimal yaw: {actual_yaw}")
        print(f"    ✓ Power: {power:.2f} kW")
        print(f"    ✓ Improvement: {result['improvement_percent']:.2f}%")
        
        results.append({
            'hour': hour,
            'wind_speed': live_ws,
            'wind_direction': live_wd,
            'predicted_yaw_t1': predicted_yaw[0],
            'predicted_yaw_t2': predicted_yaw[1],
            'predicted_yaw_t3': predicted_yaw[2],
            'predicted_yaw_t4': predicted_yaw[3],
            'predicted_yaw_t5': predicted_yaw[4],
            'actual_yaw_t1': actual_yaw[0],
            'actual_yaw_t2': actual_yaw[1],
            'actual_yaw_t3': actual_yaw[2],
            'actual_yaw_t4': actual_yaw[3],
            'actual_yaw_t5': actual_yaw[4],
            'power_output': power,
            'baseline_power': result['baseline_power'],
            'improvement_percent': result['improvement_percent']
        })
    
    df_results = pd.DataFrame(results)
    
    # Save comparison data for UI
    output_path = PROCESSED_DIR / 'predicted_vs_actual_yaw_angles.csv'
    df_results.to_csv(output_path, index=False)
    
    print(f"\n✅ Optimization results saved to {output_path}")
    
    return df_results


def generate_ui_summary(results_df):
    """Generate summary JSON for UI"""
    print("\n" + "="*70)
    print("STEP 5: Generating UI Summary")
    print("="*70)
    
    summary = {
        'date': '2012-01-01',
        'hours_processed': len(results_df),
        'total_hours': 24,
        'average_power': float(results_df['power_output'].mean()),
        'average_improvement': float(results_df['improvement_percent'].mean()),
        'hourly_data': []
    }
    
    for idx, row in results_df.iterrows():
        summary['hourly_data'].append({
            'hour': int(row['hour']),
            'wind_speed': float(row['wind_speed']),
            'wind_direction': float(row['wind_direction']),
            'predicted_yaw': [
                float(row['predicted_yaw_t1']),
                float(row['predicted_yaw_t2']),
                float(row['predicted_yaw_t3']),
                float(row['predicted_yaw_t4']),
                float(row['predicted_yaw_t5'])
            ],
            'actual_yaw': [
                float(row['actual_yaw_t1']),
                float(row['actual_yaw_t2']),
                float(row['actual_yaw_t3']),
                float(row['actual_yaw_t4']),
                float(row['actual_yaw_t5'])
            ],
            'power_output': float(row['power_output']),
            'improvement_percent': float(row['improvement_percent'])
        })
    
    output_path = PROCESSED_DIR / 'ui_summary.json'
    with open(output_path, 'w') as f:
        json.dump(summary, f, indent=2)
    
    print(f"✅ UI summary saved to {output_path}")
    print(f"\n   Summary:")
    print(f"   - Hours processed: {summary['hours_processed']} / {summary['total_hours']}")
    print(f"   - Average power: {summary['average_power']:.2f} kW")
    print(f"   - Average improvement: {summary['average_improvement']:.2f}%")
    
    return summary


def main():
    """Main execution"""
    print("\n" + "="*70)
    print("🚀 GENERATING DEMO DATA FOR UI")
    print("   Simulating Two-Stage Predictive Optimization")
    print("="*70)
    
    try:
        # Step 1: Load and clean forecast
        forecast_df = load_and_clean_forecast()
        
        # Step 2: Pre-compute optimal yaw angles from forecast (day-ahead batch processing)
        predictions_df = get_sphinx_predictions(forecast_df)
        
        # Step 3: Load NREL "live" data
        nrel_df = load_and_clean_nrel_data(num_hours=6)
        
        # Step 4: Run narrow search optimization (real-time with pre-computed angles)
        results_df = run_narrow_search_optimization(predictions_df, nrel_df)
        
        # Step 5: Generate UI summary
        summary = generate_ui_summary(results_df)
        
        print("\n" + "="*70)
        print("🎉 DEMO DATA GENERATION COMPLETE!")
        print("="*70)
        print(f"\nFiles created in {PROCESSED_DIR}:")
        print(f"  ✓ forecast_cleaned_2012-01-01.csv")
        print(f"  ✓ forecast_optimized_yaw_angles.csv (day-ahead batch results)")
        print(f"  ✓ nrel_live_first_6hours.csv")
        print(f"  ✓ predicted_vs_actual_yaw_angles.csv (comparison)")
        print(f"  ✓ ui_summary.json")
        print(f"\n💡 This demonstrates the two-stage approach:")
        print(f"   Stage 1: Full optimization on forecast (done once per day)")
        print(f"   Stage 2: Narrow search on live data (fast real-time adjustments)")
        print("="*70 + "\n")
        
    except Exception as e:
        print(f"\n❌ ERROR: {e}")
        import traceback
        traceback.print_exc()
        return 1
    
    return 0


if __name__ == '__main__':
    exit(main())
