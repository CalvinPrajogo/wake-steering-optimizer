"""
Quick test script to verify FLORIS installation and basic functionality
Tests both basic FLORIS functionality and wake steering optimization with 5-turbine configuration
"""

import numpy as np
from floris import FlorisModel
from wake_steering_optimizer import WakeSteeringOptimizer
import config

def test_floris_basic():
    """Test basic FLORIS initialization and simulation"""
    print("="*60)
    print("Testing FLORIS Installation")
    print("="*60)
    
    try:
        # Initialize FLORIS
        print("\n1. Initializing FLORIS model...")
        fmodel = FlorisModel("floris_config.yaml")
        print("   [OK] FLORIS model created successfully")
        
        # Check turbine layout
        print("\n2. Checking turbine layout...")
        x, y = fmodel.get_turbine_layout()
        print(f"   [OK] Found {len(x)} turbines")
        print("   Turbine positions:")
        for i, (_x, _y) in enumerate(zip(x, y)):
            print(f"     T{i+1}: ({_x:.1f}, {_y:.1f})")
        
        # Run baseline simulation
        print("\n3. Running baseline simulation (0° yaw)...")
        n_turbines = len(x)
        yaw_angles = np.array([[0.0] * n_turbines], dtype=float)
        fmodel.set(yaw_angles=yaw_angles)
        fmodel.run()
        print("   [OK] Simulation completed")
        
        # Get turbine powers
        print("\n4. Getting turbine powers...")
        powers = fmodel.get_turbine_powers()[0] / 1000.0  # Convert to kW
        total_power = np.sum(powers)
        print(f"   Total farm power: {total_power:.2f} kW")
        print("   Individual turbine powers:")
        for i, power in enumerate(powers):
            print(f"     T{i+1}: {power:.2f} kW")
        
        # Test with yaw angles
        print("\n5. Testing with yaw angles...")
        yaw_angles = np.array([[-5.0, 3.0, 0.0, -2.0, 1.0]], dtype=float)  # Example yaw configuration for 5 turbines
        fmodel.set(yaw_angles=yaw_angles)
        fmodel.run()
        powers_yawed = fmodel.get_turbine_powers()[0] / 1000.0
        total_power_yawed = np.sum(powers_yawed)
        print(f"   Yaw angles: {yaw_angles[0]}")
        print(f"   Total farm power: {total_power_yawed:.2f} kW")
        improvement = ((total_power_yawed - total_power) / total_power) * 100
        print(f"   Change from baseline: {improvement:+.2f}%")
        
        print("\n" + "="*60)
        print("[PASS] All tests passed! FLORIS is working correctly.")
        print("="*60)
        return True
        
    except Exception as e:
        print(f"\n[ERROR] Error: {e}")
        print("\nPlease check:")
        print("  1. FLORIS is installed: pip install floris")
        print("  2. floris_config.yaml exists in the current directory")
        print("  3. All dependencies are installed")
        return False


def test_wake_steering_optimizer():
    """Test wake steering optimizer with 5-turbine linear configuration"""
    print("\n" + "="*60)
    print("Testing Wake Steering Optimizer (5-Turbine Configuration)")
    print("="*60)
    
    try:
        # Test 1: Initialize optimizer
        print("\n1. Initializing WakeSteeringOptimizer...")
        optimizer = WakeSteeringOptimizer()
        print(f"   [OK] Optimizer initialized with {optimizer.n_turbines} turbines")
        print(f"   [OK] Wind conditions: {optimizer.wind_direction}° @ {optimizer.wind_speed} m/s")
        
        # Verify turbine positions match config
        print("\n2. Verifying turbine configuration...")
        assert len(optimizer.turbine_positions) == 5, f"Expected 5 turbines, got {len(optimizer.turbine_positions)}"
        print("   [OK] Correct number of turbines (5)")
        print("   Turbine positions:")
        for i, pos in enumerate(optimizer.turbine_positions):
            print(f"     T{i+1}: ({pos[0]:.2f}, {pos[1]:.2f})")
        
        # Test 2: Run baseline simulation
        print("\n3. Running baseline simulation (0° yaw)...")
        baseline_yaw = [0.0] * 5
        baseline_power = optimizer.run_simulation(baseline_yaw)
        baseline_turbine_powers = optimizer.get_turbine_powers(baseline_yaw)
        print(f"   [OK] Baseline simulation completed")
        print(f"   Total baseline power: {baseline_power:.2f} kW")
        print("   Individual turbine powers:")
        for i, power in enumerate(baseline_turbine_powers):
            print(f"     T{i+1}: {power:.2f} kW")
        
        # Verify power is reasonable (should be > 0 and < rated power * 5)
        max_rated_power = 5000 * 5  # 5MW per turbine * 5 turbines
        assert baseline_power > 0, "Baseline power should be positive"
        assert baseline_power < max_rated_power, f"Baseline power ({baseline_power:.2f} kW) seems unreasonably high"
        print("   [OK] Baseline power is within reasonable range")
        
        # Test 3: Test with different yaw angles
        print("\n4. Testing with yaw angles...")
        test_yaw = [-5.0, 3.0, 0.0, -2.0, 1.0]
        yawed_power = optimizer.run_simulation(test_yaw)
        yawed_turbine_powers = optimizer.get_turbine_powers(test_yaw)
        print(f"   [OK] Yawed simulation completed")
        print(f"   Yaw angles: {test_yaw}")
        print(f"   Total power: {yawed_power:.2f} kW")
        print("   Individual turbine powers:")
        for i, power in enumerate(yawed_turbine_powers):
            print(f"     T{i+1}: {power:.2f} kW")
        
        # Test 4: Run a small optimization (limited search space for quick test)
        print("\n5. Running limited optimization test...")
        print("   Using reduced search space: -2° to 2° (step: 2°) for quick testing")
        limited_range = range(-2, 3, 2)  # Only test -2, 0, 2 degrees
        results = optimizer.optimize(yaw_range=limited_range, progress_interval=10)
        
        print("\n6. Verifying optimization results...")
        assert results['baseline_power'] > 0, "Baseline power should be positive"
        assert results['optimal_power'] > 0, "Optimal power should be positive"
        assert len(results['optimal_yaw_angles']) == 5, "Should have 5 optimal yaw angles"
        assert all(isinstance(yaw, (int, float)) for yaw in results['optimal_yaw_angles']), "Yaw angles should be numbers"
        
        print("   [OK] Optimization results are valid")
        print(f"   Baseline power: {results['baseline_power']:.2f} kW")
        print(f"   Optimal power: {results['optimal_power']:.2f} kW")
        print(f"   Optimal yaw angles: {results['optimal_yaw_angles']}")
        print(f"   Improvement: {results['improvement_percent']:+.2f}%")
        print(f"   Power gain: {results['power_gain']:+.2f} kW")
        
        # Test 5: Verify wake effects are present (downstream turbines should have less power)
        print("\n7. Verifying wake effects...")
        # In a linear layout with wind from west (270°), turbines 2-5 should be downstream
        # and typically have less power than turbine 1
        if baseline_turbine_powers[0] > baseline_turbine_powers[1]:
            print("   [OK] Wake effects detected (upstream turbine has more power)")
        else:
            print("   [NOTE] Wake effects may be minimal for this configuration")
        
        print("\n" + "="*60)
        print("[PASS] All wake steering optimizer tests passed!")
        print("[PASS] 5-turbine linear configuration is working correctly")
        print("="*60)
        return True
        
    except Exception as e:
        print(f"\n[ERROR] Error: {e}")
        import traceback
        traceback.print_exc()
        print("\nPlease check:")
        print("  1. wake_steering_optimizer.py exists and is correct")
        print("  2. config.py has correct 5-turbine configuration")
        print("  3. floris_config.yaml has 5 turbines configured")
        print("  4. All dependencies are installed")
        return False


if __name__ == "__main__":
    # Run both tests
    test1_passed = test_floris_basic()
    test2_passed = test_wake_steering_optimizer()
    
    if test1_passed and test2_passed:
        print("\n" + "="*60)
        print("[SUCCESS] ALL TESTS PASSED!")
        print("Your 5-turbine linear configuration is ready for wake steering optimization!")
        print("="*60)
    else:
        print("\n" + "="*60)
        print("[WARNING] Some tests failed. Please review the errors above.")
        print("="*60)
