"""
Main optimization script for wake steering
Implements fast continuous optimization using SciPy SLSQP to find optimal yaw angles
"""

import numpy as np
import pandas as pd
from itertools import product
from time import time
from floris import FlorisModel
import config


class WakeSteeringOptimizer:
    """
    Wake steering optimizer using fast continuous optimization (SLSQP)
    """
    
    def __init__(self, wind_direction=None, wind_speed=None, turbine_positions=None):
        """
        Initialize the optimizer with wind farm configuration
        
        Args:
            wind_direction: Wind direction in degrees (default from config)
            wind_speed: Wind speed in m/s (default from config)
            turbine_positions: List of (x, y) tuples for turbine positions (default from config)
        """
        self.wind_direction = wind_direction or config.WIND_DIRECTION
        self.wind_speed = wind_speed or config.WIND_SPEED
        self.turbine_positions = turbine_positions or config.TURBINE_POSITIONS
        self.n_turbines = len(self.turbine_positions)
        
        # Initialize FLORIS model
        self.fmodel = self._setup_floris()
        
        # Storage for optimization results
        self.baseline_power = None
        self.baseline_turbine_powers = None
        self.optimal_yaw_angles = None
        self.optimal_power = None
        self.optimal_turbine_powers = None
        self.all_results = []
        
    def _setup_floris(self):
        """
        Set up FLORIS model with turbine layout and wind conditions
        
        Returns:
            FlorisModel instance
        """
        print("Setting up FLORIS model...")
        print(f"Wind conditions: {self.wind_direction}° @ {self.wind_speed} m/s")
        print(f"Turbine layout: {self.n_turbines} turbines")
        
        # Initialize FLORIS with configuration file
        fmodel = FlorisModel("floris_config.yaml")
        
        # Set wind farm layout and conditions
        layout_x = [pos[0] for pos in self.turbine_positions]
        layout_y = [pos[1] for pos in self.turbine_positions]
        
        fmodel.set(
            layout_x=layout_x,
            layout_y=layout_y,
            wind_directions=[self.wind_direction],
            wind_speeds=[self.wind_speed],
            turbulence_intensities=[0.06]
        )
        
        print("FLORIS model initialized successfully")
        return fmodel
    
    def run_simulation(self, yaw_angles):
        """
        Run FLORIS simulation for given yaw angles
        
        Args:
            yaw_angles: Array of yaw angles for each turbine (degrees)
            
        Returns:
            Total farm power output (kW)
        """
        # Set yaw angles - FLORIS expects shape (n_findex, n_turbines) and float dtype
        yaw_array = np.array([yaw_angles], dtype=float)  # Add findex dimension and ensure float
        
        # Set yaw angles and run simulation
        self.fmodel.set(yaw_angles=yaw_array)
        self.fmodel.run()
        
        # Get turbine powers (in Watts, convert to kW)
        turbine_powers = self.fmodel.get_turbine_powers()[0] / 1000.0  # First findex
        
        # Return total farm power
        return np.sum(turbine_powers)
    
    def get_turbine_powers(self, yaw_angles):
        """
        Get individual turbine powers for given yaw angles
        
        Args:
            yaw_angles: Array of yaw angles for each turbine (degrees)
            
        Returns:
            Array of individual turbine powers (kW)
        """
        # Set yaw angles and run simulation - ensure float dtype
        yaw_array = np.array([yaw_angles], dtype=float)
        self.fmodel.set(yaw_angles=yaw_array)
        self.fmodel.run()
        
        # Get turbine powers (in Watts, convert to kW)
        turbine_powers = self.fmodel.get_turbine_powers()[0] / 1000.0
        
        return turbine_powers
    
    def optimize_with_ranges(self, search_ranges, progress_interval=100):
        """
        Run optimization with custom search ranges for each turbine
        (Used for narrow search around predicted yaw angles)
        
        Args:
            search_ranges: List of (min, max) tuples for each turbine
                          e.g., [(-6, -2), (1, 5), (-2, 2), (-1, 3)]
            progress_interval: Print progress every N combinations
            
        Returns:
            Dictionary with optimization results
        """
        print("\n" + "="*60)
        print("STARTING OPTIMIZATION WITH CUSTOM RANGES")
        print("="*60)
        
        # Calculate baseline (all turbines at 0° yaw)
        baseline_yaw = [0] * self.n_turbines
        self.baseline_power = self.run_simulation(baseline_yaw)
        self.baseline_turbine_powers = self.get_turbine_powers(baseline_yaw)
        print(f"\nBaseline power (0° yaw): {self.baseline_power:.2f} kW")
        
        # Generate ranges for each turbine
        ranges = []
        for ymin, ymax in search_ranges:
            ranges.append(range(ymin, ymax + 1))
        
        # Generate all combinations
        yaw_combinations = list(product(*ranges))
        total_combinations = len(yaw_combinations)
        print(f"\nTesting {total_combinations:,} yaw angle combinations...")
        
        # Run optimization
        start_time = time()
        best_power = 0
        best_yaw = None
        
        for idx, yaw_angles in enumerate(yaw_combinations):
            # Run simulation
            power = self.run_simulation(list(yaw_angles))
            
            # Store result
            self.all_results.append({
                'yaw_angles': yaw_angles,
                'power': power
            })
            
            # Track best result
            if power > best_power:
                best_power = power
                best_yaw = yaw_angles
            
            # Print progress
            if (idx + 1) % progress_interval == 0:
                elapsed = time() - start_time
                progress = (idx + 1) / total_combinations * 100
                print(f"Progress: {idx + 1:,}/{total_combinations:,} ({progress:.1f}%) - Elapsed: {elapsed:.1f}s")
        
        # Store optimal results
        self.optimal_power = best_power
        self.optimal_yaw_angles = list(best_yaw)
        self.optimal_turbine_powers = self.get_turbine_powers(self.optimal_yaw_angles)
        
        elapsed_time = time() - start_time
        print(f"\nOptimization complete in {elapsed_time:.1f} seconds")
        
        return self.get_results()
    
    def optimize(self, yaw_range=None, progress_interval=1000):
        """
        Run fast continuous optimization using SciPy SLSQP
        
        Args:
            yaw_range: Range of yaw angles (kept for compatibility, not used)
            progress_interval: Not used (kept for compatibility)
            
        Returns:
            Dictionary with optimization results
        """
        from scipy.optimize import minimize
        import numpy as np
        
        print("\n" + "="*60)
        print("STARTING FAST CONTINUOUS OPTIMIZATION (L-BFGS-B)")
        print("="*60)
        
        # Calculate baseline (all turbines at 0° yaw)
        baseline_yaw = [0.0] * self.n_turbines
        self.baseline_power = self.run_simulation(baseline_yaw)
        self.baseline_turbine_powers = self.get_turbine_powers(baseline_yaw)
        print(f"\nBaseline power (0° yaw): {self.baseline_power:.2f} kW")
        
        def objective(yaws):
            # Ensure yaws is converted to list/array format that run_simulation expects
            yaw_list = yaws.tolist() if isinstance(yaws, np.ndarray) else list(yaws)
            power = self.run_simulation(yaw_list)
            return -power
        
        # Test that simulation responds to non-zero yaw angles
        test_yaw = [5.0] * self.n_turbines
        test_power = self.run_simulation(test_yaw)
        print(f"Test power at [5°] yaw: {test_power:.2f} kW (should differ from baseline)")
        
        # Set up optimization bounds
        bounds = [(-25, 25)] * self.n_turbines
        
        print(f"\nOptimizing with differential_evolution (global optimizer)...")
        print(f"Yaw angle bounds: -25° to +25° for each turbine")
        print(f"This method explores the entire space and doesn't get stuck at local minima")
        
        # Use differential_evolution for global optimization - it explores the whole space
        from scipy.optimize import differential_evolution
        start_time = time()
        result = differential_evolution(
            objective,
            bounds=bounds,
            seed=42,
            maxiter=100,
            popsize=15,
            atol=1e-3,
            tol=1e-3,
            polish=True  # Polish the result with L-BFGS-B
        )
        
        # Verify optimization ran successfully
        print(f"\nOptimization status: {result.message}")
        print(f"Number of iterations: {result.nit}")
        print(f"Number of function evaluations: {result.nfev}")
        print(f"Success: {result.success}")
        
        # Store optimal results
        self.optimal_yaw_angles = result.x.tolist()
        self.optimal_power = -result.fun
        self.optimal_turbine_powers = self.get_turbine_powers(self.optimal_yaw_angles)
        
        # Show improvement over baseline
        improvement = ((self.optimal_power - self.baseline_power) / self.baseline_power) * 100
        print(f"Power improvement: {improvement:.2f}%")
        
        elapsed_time = time() - start_time
        print(f"\nOptimization complete in {elapsed_time:.2f} seconds")
        print(f"Optimal yaw angles: {self.optimal_yaw_angles}")
        print(f"Optimal power: {self.optimal_power:.2f} kW")
        
        return self.get_results()
    
    def optimize_fast(self):
        """
        Fast continuous optimization using SciPy SLSQP.
        """
        from scipy.optimize import minimize
        import numpy as np

        def objective(yaws):
            # Ensure yaws is converted to list/array format that run_simulation expects
            yaw_list = yaws.tolist() if isinstance(yaws, np.ndarray) else list(yaws)
            power = self.run_simulation(yaw_list)
            return -power

        # Calculate baseline (all turbines at 0° yaw)
        baseline_yaw = [0.0] * self.n_turbines
        self.baseline_power = self.run_simulation(baseline_yaw)
        self.baseline_turbine_powers = self.get_turbine_powers(baseline_yaw)

        x0 = np.zeros(self.n_turbines)
        bounds = [(-25, 25)] * self.n_turbines

        result = minimize(
            objective,
            x0,
            bounds=bounds,
            method="SLSQP",
            options={'maxiter': 1000, 'ftol': 1e-6, 'disp': False}
        )

        self.optimal_yaw_angles = result.x.tolist()
        self.optimal_power = -result.fun
        self.optimal_turbine_powers = self.get_turbine_powers(self.optimal_yaw_angles)

        return self.get_results()
    
    def get_results(self):
        """
        Get optimization results as a dictionary
        
        Returns:
            Dictionary with all optimization results
        """
        if self.optimal_power is None:
            raise ValueError("Optimization has not been run yet")
        
        improvement = ((self.optimal_power - self.baseline_power) / self.baseline_power) * 100
        
        results = {
            'baseline_power': self.baseline_power,
            'optimal_power': self.optimal_power,
            'total_power': self.optimal_power,  # Alias for compatibility
            'optimal_yaw_angles': self.optimal_yaw_angles,
            'turbine_powers': self.optimal_turbine_powers,
            'improvement_percent': improvement,
            'power_gain': self.optimal_power - self.baseline_power,
            'all_results': self.all_results
        }
        
        return results
    
    def print_summary(self):
        """
        Print formatted summary of optimization results
        """
        results = self.get_results()
        
        print("\n" + "="*60)
        print("WAKE STEERING OPTIMIZATION RESULTS")
        print("="*60)
        print(f"Wind Conditions: {self.wind_direction}° @ {self.wind_speed} m/s")
        print(f"Turbine Layout: 5-turbine linear layout")
        
        print("\nBASELINE (No Steering):")
        print(f"  Total Power: {results['baseline_power']:.2f} kW")
        for i, power in enumerate(self.baseline_turbine_powers):
            print(f"  T{i+1}: {power:.2f} kW")
        
        print("\nOPTIMIZED (Wake Steering):")
        print(f"  Optimal Yaw Angles: {results['optimal_yaw_angles']}")
        print(f"  Total Power: {results['optimal_power']:.2f} kW")
        for i, power in enumerate(self.optimal_turbine_powers):
            print(f"  T{i+1}: {power:.2f} kW")
        
        print("\nIMPROVEMENT:")
        print(f"  Power Gain: +{results['improvement_percent']:.2f}%")
        print(f"  Additional Power: +{results['power_gain']:.2f} kW")
        
        # Calculate annual impact
        annual_energy = results['power_gain'] * config.HOURS_PER_YEAR / 1000  # MWh/year
        annual_revenue = annual_energy * config.ELECTRICITY_PRICE
        
        print("\nANNUAL IMPACT (8760 hours/year):")
        print(f"  Additional Energy: {annual_energy:.2f} MWh/year")
        print(f"  Additional Revenue: ${annual_revenue:,.2f}/year")
        
        print("\nOptimization Details:")
        print(f"  Method: Differential Evolution (global optimizer)")


def test_multiple_wind_directions(wind_directions=None, wind_speed=8.0):
    """
    Test optimization across multiple wind directions to find where wake steering is most beneficial
    
    Args:
        wind_directions: List of wind directions to test (default: 0-360 in 30° steps)
        wind_speed: Wind speed to use for all tests
    """
    import config
    
    if wind_directions is None:
        # Test every 30 degrees
        wind_directions = list(range(0, 360, 30))
    
    print("\n" + "="*80)
    print("TESTING MULTIPLE WIND DIRECTIONS FOR WAKE STEERING BENEFIT")
    print("="*80)
    
    results_summary = []
    
    for wind_dir in wind_directions:
        print(f"\n{'='*80}")
        print(f"Testing wind direction: {wind_dir}°")
        print(f"{'='*80}")
        
        # Create optimizer for this wind direction
        optimizer = WakeSteeringOptimizer(wind_direction=wind_dir, wind_speed=wind_speed)
        
        # Run optimization
        try:
            results = optimizer.optimize()
            improvement = results['improvement_percent']
            optimal_yaws = results['optimal_yaw_angles']
            
            # Calculate max yaw angle magnitude
            max_yaw = max([abs(y) for y in optimal_yaws])
            
            results_summary.append({
                'wind_direction': wind_dir,
                'baseline_power': results['baseline_power'],
                'optimal_power': results['optimal_power'],
                'improvement_percent': improvement,
                'power_gain': results['power_gain'],
                'max_yaw_angle': max_yaw,
                'optimal_yaw_angles': optimal_yaws
            })
            
            print(f"\nResults for {wind_dir}°:")
            print(f"  Improvement: {improvement:.2f}%")
            print(f"  Max yaw angle: {max_yaw:.2f}°")
            print(f"  Optimal yaw angles: {[f'{y:.2f}' for y in optimal_yaws]}")
            
        except Exception as e:
            print(f"  Error testing {wind_dir}°: {e}")
            results_summary.append({
                'wind_direction': wind_dir,
                'error': str(e)
            })
    
    # Print summary
    print("\n" + "="*80)
    print("SUMMARY: WAKE STEERING BENEFIT BY WIND DIRECTION")
    print("="*80)
    print(f"{'Wind Dir':<12} {'Baseline (kW)':<15} {'Optimal (kW)':<15} {'Improvement %':<15} {'Max Yaw (°)':<12}")
    print("-"*80)
    
    best_improvement = -999
    best_direction = None
    
    for r in results_summary:
        if 'error' not in r:
            print(f"{r['wind_direction']:<12} {r['baseline_power']:<15.2f} {r['optimal_power']:<15.2f} "
                  f"{r['improvement_percent']:<15.2f} {r['max_yaw_angle']:<12.2f}")
            if r['improvement_percent'] > best_improvement:
                best_improvement = r['improvement_percent']
                best_direction = r['wind_direction']
        else:
            print(f"{r['wind_direction']:<12} ERROR: {r['error']}")
    
    if best_direction is not None:
        print("\n" + "="*80)
        print(f"BEST WIND DIRECTION FOR WAKE STEERING: {best_direction}°")
        print(f"Improvement: {best_improvement:.2f}%")
        print("="*80)
    
    return results_summary


def main():
    """
    Main execution function
    """
    import config
    
    # Ask user if they want to test multiple wind directions
    print("\n" + "="*60)
    print("WAKE STEERING OPTIMIZER")
    print("="*60)
    print("\nOptions:")
    print("1. Run optimization for default wind conditions")
    print("2. Test multiple wind directions to find best conditions")
    
    try:
        choice = input("\nEnter choice (1 or 2, default=1): ").strip()
    except:
        choice = "1"
    
    if choice == "2":
        # Test multiple wind directions
        test_multiple_wind_directions()
    else:
        # Create optimizer instance
        optimizer = WakeSteeringOptimizer()
        
        # Run optimization
        results = optimizer.optimize()
        
        # Print results
        optimizer.print_summary()
        
        # TODO: Generate visualizations (will implement in visualization.py)
        print("\n" + "="*60)
        print("Next: Run visualization.py to generate plots")
        print("="*60)


if __name__ == "__main__":
    main()
