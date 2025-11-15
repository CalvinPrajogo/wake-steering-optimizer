"""
Quick test script to verify FLORIS installation and basic functionality
"""

import numpy as np
from floris import FlorisModel

def test_floris_basic():
    """Test basic FLORIS initialization and simulation"""
    print("="*60)
    print("Testing FLORIS Installation")
    print("="*60)
    
    try:
        # Initialize FLORIS
        print("\n1. Initializing FLORIS model...")
        fmodel = FlorisModel("floris_config.yaml")
        print("   ✓ FLORIS model created successfully")
        
        # Check turbine layout
        print("\n2. Checking turbine layout...")
        x, y = fmodel.get_turbine_layout()
        print(f"   ✓ Found {len(x)} turbines")
        print("   Turbine positions:")
        for i, (_x, _y) in enumerate(zip(x, y)):
            print(f"     T{i+1}: ({_x:.1f}, {_y:.1f})")
        
        # Run baseline simulation
        print("\n3. Running baseline simulation (0° yaw)...")
        yaw_angles = np.array([[0.0, 0.0, 0.0, 0.0]], dtype=float)
        fmodel.set(yaw_angles=yaw_angles)
        fmodel.run()
        print("   ✓ Simulation completed")
        
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
        yaw_angles = np.array([[-5.0, 3.0, 0.0, 0.0]], dtype=float)  # Example yaw configuration
        fmodel.set(yaw_angles=yaw_angles)
        fmodel.run()
        powers_yawed = fmodel.get_turbine_powers()[0] / 1000.0
        total_power_yawed = np.sum(powers_yawed)
        print(f"   Yaw angles: {yaw_angles[0]}")
        print(f"   Total farm power: {total_power_yawed:.2f} kW")
        improvement = ((total_power_yawed - total_power) / total_power) * 100
        print(f"   Change from baseline: {improvement:+.2f}%")
        
        print("\n" + "="*60)
        print("✓ All tests passed! FLORIS is working correctly.")
        print("="*60)
        return True
        
    except Exception as e:
        print(f"\n✗ Error: {e}")
        print("\nPlease check:")
        print("  1. FLORIS is installed: pip install floris")
        print("  2. floris_config.yaml exists in the current directory")
        print("  3. All dependencies are installed")
        return False


if __name__ == "__main__":
    test_floris_basic()
