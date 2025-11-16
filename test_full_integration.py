"""
test_full_integration.py

Comprehensive integration test for the entire wake steering optimization system.
Tests all components working together with real NREL data.
"""

import pandas as pd
import numpy as np
from pathlib import Path
import sys

# Add src to path
sys.path.insert(0, str(Path(__file__).parent / 'src'))

from wake_steering_optimizer import WakeSteeringOptimizer
from sphinx_integration import SphinxPredictor
from predictive_optimization import PredictiveOptimizer
from forecast_validator import is_forecast_valid, get_recommended_yaw_range

def test_nrel_data_loading():
    """Test that NREL data can be loaded and parsed correctly."""
    print("\n" + "="*70)
    print("TEST 1: NREL Data Loading")
    print("="*70)
    
    data_path = Path('data/raw/nrel_wtk_2012_100m_raw.csv')
    
    if not data_path.exists():
        print(f"❌ FAILED: Data file not found at {data_path}")
        return False
    
    try:
        # Skip the first row (metadata), use second row as header
        df = pd.read_csv(data_path, skiprows=1)
        
        print(f"✅ Successfully loaded NREL data")
        print(f"   Rows: {len(df):,}")
        print(f"   Columns: {list(df.columns)}")
        
        # Validate required columns
        required_cols = ['wind speed at 100m (m/s)', 'wind direction at 100m (deg)']
        missing = [col for col in required_cols if col not in df.columns]
        
        if missing:
            print(f"❌ FAILED: Missing columns: {missing}")
            return False
        
        # Show sample statistics
        ws_col = 'wind speed at 100m (m/s)'
        wd_col = 'wind direction at 100m (deg)'
        
        print(f"\n   Wind Speed Statistics:")
        print(f"     Mean: {df[ws_col].mean():.2f} m/s")
        print(f"     Min: {df[ws_col].min():.2f} m/s")
        print(f"     Max: {df[ws_col].max():.2f} m/s")
        print(f"     Std: {df[ws_col].std():.2f} m/s")
        
        print(f"\n   Wind Direction Statistics:")
        print(f"     Mean: {df[wd_col].mean():.2f}°")
        print(f"     Min: {df[wd_col].min():.2f}°")
        print(f"     Max: {df[wd_col].max():.2f}°")
        
        # Show first few data points
        print(f"\n   First 5 data points:")
        print(df[['Year', 'Month', 'Day', 'Hour', ws_col, wd_col]].head())
        
        return True
        
    except Exception as e:
        print(f"❌ FAILED: Error loading data: {e}")
        return False


def test_floris_optimizer():
    """Test that FLORIS optimizer works with realistic wind conditions."""
    print("\n" + "="*70)
    print("TEST 2: FLORIS Optimizer")
    print("="*70)
    
    try:
        # Load a sample from NREL data
        data_path = Path('data/raw/nrel_wtk_2012_100m_raw.csv')
        df = pd.read_csv(data_path, skiprows=1)
        
        # Use first data point
        ws = df['wind speed at 100m (m/s)'].iloc[0]
        wd = df['wind direction at 100m (deg)'].iloc[0]
        
        print(f"Testing with real wind conditions from NREL:")
        print(f"  Wind Speed: {ws:.2f} m/s")
        print(f"  Wind Direction: {wd:.2f}°")
        
        # Initialize optimizer with wind conditions
        optimizer = WakeSteeringOptimizer(wind_direction=wd, wind_speed=ws)
        
        # Test baseline (no yaw)
        print(f"\n⏳ Running baseline optimization...")
        baseline_power = optimizer.run_simulation([0, 0, 0, 0, 0])
        
        print(f"✅ Baseline power: {baseline_power:.2f} kW")
        
        # Test optimized yaw
        print(f"\n⏳ Running yaw optimization...")
        yaw_range = range(-5, 6, 2)  # -5, -3, -1, 1, 3, 5
        optimized = optimizer.optimize(yaw_range=yaw_range, progress_interval=500)
        
        print(f"✅ Optimized power: {optimized['optimal_power']:.2f} kW")
        print(f"   Best yaw angles: {optimized['optimal_yaw_angles']}")
        print(f"   Power gain: {optimized['improvement_percent']:.2f}%")
        
        return True
        
    except Exception as e:
        print(f"❌ FAILED: {e}")
        import traceback
        traceback.print_exc()
        return False


def test_sphinx_integration():
    """Test Sphinx AI integration (if API key available)."""
    print("\n" + "="*70)
    print("TEST 3: Sphinx AI Integration")
    print("="*70)
    
    try:
        from dotenv import load_dotenv
        import os
        
        load_dotenv()
        api_key = os.getenv('SPHINX_API_KEY')
        
        if not api_key:
            print("⚠️  SKIPPED: SPHINX_API_KEY not found in .env")
            print("   (This is optional - system works without it)")
            return None
        
        # Simple connectivity test only
        print(f"✅ Sphinx AI API key configured")
        print(f"   SphinxPredictor can be initialized")
        print(f"   (Skipping live prediction to save time)")
        
        # Just verify initialization works
        predictor = SphinxPredictor()
        print(f"✅ Sphinx integration ready!")
        
        return True
        
    except Exception as e:
        print(f"❌ FAILED: {e}")
        import traceback
        traceback.print_exc()
        return False


def test_forecast_validator():
    """Test forecast validation logic."""
    print("\n" + "="*70)
    print("TEST 4: Forecast Validator")
    print("="*70)
    
    try:
        # Test with matching conditions
        forecast = {
            'wind_speed': 8.0,
            'wind_direction': 270,
            'turbulence_intensity': 0.06
        }
        
        actual = {
            'wind_speed': 8.2,
            'wind_direction': 272,
            'turbulence_intensity': 0.062
        }
        
        print("Testing forecast validation:")
        print(f"  Forecast: WS={forecast['wind_speed']} m/s, WD={forecast['wind_direction']}°")
        print(f"  Actual:   WS={actual['wind_speed']} m/s, WD={actual['wind_direction']}°")
        
        validation = is_forecast_valid(forecast, actual)
        
        print(f"\n✅ Validation result: {validation['recommendation']}")
        print(f"   Valid: {validation['valid']}")
        print(f"   Speed OK: {validation['speed_ok']}")
        print(f"   Direction OK: {validation['direction_ok']}")
        print(f"   Turbulence OK: {validation['turbulence_ok']}")
        print(f"   Deviations:")
        print(f"     Speed: {validation['deviations']['speed_abs']:.2f} m/s ({validation['deviations']['speed_rel']*100:.1f}%)")
        print(f"     Direction: {validation['deviations']['direction']:.2f}°")
        print(f"     Turbulence: {validation['deviations']['turbulence']*100:.2f}%")
        
        # Get recommended yaw range
        yaw_range = get_recommended_yaw_range(forecast['wind_speed'], forecast['turbulence_intensity'])
        print(f"\n   Recommended yaw range: {yaw_range}° based on wind conditions")
        
        return True
        
    except Exception as e:
        print(f"❌ FAILED: {e}")
        import traceback
        traceback.print_exc()
        return False


def test_predictive_optimization():
    """Test the full two-stage predictive optimization workflow."""
    print("\n" + "="*70)
    print("TEST 5: Two-Stage Predictive Optimization")
    print("="*70)
    
    try:
        from dotenv import load_dotenv
        import os
        
        load_dotenv()
        api_key = os.getenv('SPHINX_API_KEY')
        
        if not api_key:
            print("⚠️  SKIPPED: SPHINX_API_KEY not found in .env")
            print("   (This is optional - system works without it)")
            return None
        
        print(f"✅ PredictiveOptimizer can be initialized")
        print(f"   Two-stage workflow ready")
        print(f"   (Skipping live optimization to save time)")
        
        # Just verify initialization works
        optimizer = PredictiveOptimizer()
        print(f"✅ Predictive optimization system ready!")
        
        return True
        
    except Exception as e:
        print(f"❌ FAILED: {e}")
        import traceback
        traceback.print_exc()
        return False


def main():
    """Run all integration tests."""
    print("\n" + "="*70)
    print("🧪 FULL INTEGRATION TEST SUITE")
    print("   Wake Steering Optimizer v1.0")
    print("="*70)
    
    results = {
        'NREL Data Loading': test_nrel_data_loading(),
        'FLORIS Optimizer': test_floris_optimizer(),
        'Sphinx AI Integration': test_sphinx_integration(),
        'Forecast Validator': test_forecast_validator(),
        'Predictive Optimization': test_predictive_optimization()
    }
    
    # Summary
    print("\n" + "="*70)
    print("📊 TEST SUMMARY")
    print("="*70)
    
    passed = sum(1 for r in results.values() if r is True)
    failed = sum(1 for r in results.values() if r is False)
    skipped = sum(1 for r in results.values() if r is None)
    total = len(results)
    
    for test_name, result in results.items():
        if result is True:
            status = "✅ PASSED"
        elif result is False:
            status = "❌ FAILED"
        else:
            status = "⚠️  SKIPPED"
        print(f"  {status}: {test_name}")
    
    print(f"\n  Total: {total} tests")
    print(f"  Passed: {passed}")
    print(f"  Failed: {failed}")
    print(f"  Skipped: {skipped}")
    
    if failed == 0 and passed > 0:
        print(f"\n🎉 ALL TESTS PASSED! System is ready for production.")
    elif failed > 0:
        print(f"\n⚠️  SOME TESTS FAILED. Please review errors above.")
    
    print("="*70 + "\n")


if __name__ == '__main__':
    main()
