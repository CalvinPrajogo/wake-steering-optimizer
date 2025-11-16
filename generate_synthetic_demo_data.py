"""
generate_synthetic_demo_data.py

Quickly generates realistic synthetic demo data for UI without running full optimizations.
"""

import json
import pandas as pd
import numpy as np
from pathlib import Path

# Create processed data directory
PROCESSED_DIR = Path('data/processed')
PROCESSED_DIR.mkdir(parents=True, exist_ok=True)

def generate_realistic_yaw_angles(wind_direction, wind_speed, hour):
    """
    Generate EXTREME yaw angles to dramatically deflect wakes away from downstream turbines
    This creates very visible wake steering effects for demo purposes
    """
    np.random.seed(hour)  # Consistent per hour
    
    # Use much more aggressive steering to completely deflect wakes
    # Upstream turbines get large yaw angles to push wakes away
    if wind_speed < 7:
        base_magnitude = 20  # Very aggressive for low wind
    elif wind_speed < 10:
        base_magnitude = 15  # Strong steering
    else:
        base_magnitude = 12  # Still significant at high wind
    
    # Wind from SW (around 230°) - aligned with Block Island layout
    # Turbines are in line SW to NE, so we need strong deflection
    if 200 <= wind_direction <= 260:
        # EXTREME yaw angles to completely deflect wakes
        # Upstream turbines yaw significantly to push wakes aside
        yaw = [
            -base_magnitude + np.random.randint(-3, 3),      # T0: Most upstream, large negative yaw
            -int(base_magnitude*0.85) + np.random.randint(-2, 2),  # T1: Still significant
            -int(base_magnitude*0.7) + np.random.randint(-2, 2),   # T2: Moderate deflection
            -int(base_magnitude*0.5) + np.random.randint(-1, 2),   # T3: Less steering
            np.random.randint(-2, 3)                          # T4: Most downstream, minimal
        ]
    # Wind from NW (270-360°)
    elif 270 <= wind_direction <= 360:
        yaw = [
            -base_magnitude + np.random.randint(-2, 3),
            -int(base_magnitude*0.8) + np.random.randint(-1, 3),
            -int(base_magnitude*0.6) + np.random.randint(-1, 2),
            np.random.randint(-3, 3),
            np.random.randint(-2, 2)
        ]
    else:
        # Other directions - still strong steering
        yaw = [
            -int(base_magnitude*0.9) + np.random.randint(-2, 2),
            -int(base_magnitude*0.7) + np.random.randint(-2, 2),
            -int(base_magnitude*0.5) + np.random.randint(-2, 3),
            np.random.randint(-3, 3),
            np.random.randint(-2, 2)
        ]
    
    return yaw


def generate_demo_data():
    """Generate all demo data files"""
    
    print("\n" + "="*70)
    print("🚀 GENERATING SYNTHETIC DEMO DATA (Fast)")
    print("="*70)
    
    # Load forecast data
    print("\n📋 Loading forecast data...")
    forecast_path = Path('data/raw/forecast_data_2012-01-01_2012-01-01.json')
    with open(forecast_path, 'r') as f:
        forecast_raw = json.load(f)
    
    hours = forecast_raw['days'][0]['hours']
    
    # Generate predicted yaw angles for all 24 hours
    print("🎯 Generating predicted yaw angles for 24 hours...")
    predictions = []
    
    for hour in hours:
        hour_num = int(hour['datetime'].split(':')[0])
        ws = hour['windspeed']
        wd = hour['winddir']
        
        predicted_yaw = generate_realistic_yaw_angles(wd, ws, hour_num)
        
        # Calculate expected power (with higher improvements due to extreme steering)
        baseline = 18000 + np.random.randint(-2000, 2000)
        improvement = 2.0 + np.random.random() * 3.0  # 2-5% improvement (dramatic!)
        expected_power = baseline * (1 + improvement/100)
        
        predictions.append({
            'hour': hour_num,
            'datetime': f"2012-01-01 {hour['datetime']}",
            'predicted_yaw_t1': predicted_yaw[0],
            'predicted_yaw_t2': predicted_yaw[1],
            'predicted_yaw_t3': predicted_yaw[2],
            'predicted_yaw_t4': predicted_yaw[3],
            'predicted_yaw_t5': predicted_yaw[4],
            'confidence': 'high',
            'expected_power': expected_power,
            'wind_speed': ws,
            'wind_direction': wd
        })
    
    df_predictions = pd.DataFrame(predictions)
    pred_path = PROCESSED_DIR / 'forecast_optimized_yaw_angles.csv'
    df_predictions.to_csv(pred_path, index=False)
    print(f"✅ Saved: {pred_path}")
    
    # Load NREL data for first 6 hours
    print("\n📊 Loading NREL live data...")
    nrel_path = Path('data/raw/nrel_wtk_2012_100m_raw.csv')
    df_nrel = pd.read_csv(nrel_path, skiprows=1)
    df_nrel_6h = df_nrel[df_nrel['Minute'] == 30].head(6)
    
    # Generate actual yaw angles (slightly different from predicted)
    print("⚡ Generating actual optimized yaw angles for 6 hours...")
    results = []
    
    for idx, row in df_nrel_6h.iterrows():
        hour = int(row['Hour'])
        live_ws = row['wind speed at 100m (m/s)']
        live_wd = row['wind direction at 100m (deg)']
        
        # Get predicted yaw for this hour
        pred = predictions[hour]
        predicted_yaw = [
            pred['predicted_yaw_t1'],
            pred['predicted_yaw_t2'],
            pred['predicted_yaw_t3'],
            pred['predicted_yaw_t4'],
            pred['predicted_yaw_t5']
        ]
        
        # Actual yaw slightly different (conditions changed)
        actual_yaw = generate_realistic_yaw_angles(live_wd, live_ws, hour + 100)
        # Add some similarity to predicted (they should be close)
        actual_yaw = [
            int(0.7 * actual_yaw[i] + 0.3 * predicted_yaw[i])
            for i in range(5)
        ]
        
        # Calculate realistic power values (higher improvements with extreme steering)
        baseline = 20000 + live_ws * 800 + np.random.randint(-1000, 1000)
        improvement = 2.5 + np.random.random() * 2.5  # 2.5-5% improvement (dramatic!)
        power = baseline * (1 + improvement/100)
        
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
            'baseline_power': baseline,
            'improvement_percent': improvement
        })
    
    df_results = pd.DataFrame(results)
    results_path = PROCESSED_DIR / 'predicted_vs_actual_yaw_angles.csv'
    df_results.to_csv(results_path, index=False)
    print(f"✅ Saved: {results_path}")
    
    # Generate UI summary
    print("\n📱 Generating UI summary...")
    summary = {
        'date': '2012-01-01',
        'hours_processed': len(results),
        'total_hours': 24,
        'average_power': float(df_results['power_output'].mean()),
        'average_improvement': float(df_results['improvement_percent'].mean()),
        'hourly_data': []
    }
    
    for idx, row in df_results.iterrows():
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
    
    summary_path = PROCESSED_DIR / 'ui_summary.json'
    with open(summary_path, 'w') as f:
        json.dump(summary, f, indent=2)
    print(f"✅ Saved: {summary_path}")
    
    # Print summary
    print("\n" + "="*70)
    print("📊 DEMO DATA SUMMARY")
    print("="*70)
    print(f"Hours simulated: {len(results)}")
    print(f"Average power: {summary['average_power']:.2f} kW")
    print(f"Average improvement: {summary['average_improvement']:.2f}%")
    print(f"\nExample Hour 0:")
    print(f"  Predicted yaw: {results[0]['predicted_yaw_t1']}, {results[0]['predicted_yaw_t2']}, {results[0]['predicted_yaw_t3']}, {results[0]['predicted_yaw_t4']}, {results[0]['predicted_yaw_t5']}")
    print(f"  Actual yaw:    {results[0]['actual_yaw_t1']}, {results[0]['actual_yaw_t2']}, {results[0]['actual_yaw_t3']}, {results[0]['actual_yaw_t4']}, {results[0]['actual_yaw_t5']}")
    print(f"  Difference shows real-time adjustment!")
    
    print("\n🎉 COMPLETE! Ready for UI demo.")
    print("="*70 + "\n")
    
    return df_results


if __name__ == '__main__':
    generate_demo_data()
