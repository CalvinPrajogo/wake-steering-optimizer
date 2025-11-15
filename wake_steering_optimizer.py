"""
Main optimization script for wake steering
Implements brute force optimization to find optimal yaw angles
"""

import numpy as np
import pandas as pd
from itertools import product
from time import time
from floris import FlorisModel
import config


class WakeSteeringOptimizer:
    """
    Wake steering optimizer using brute force search
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
        # Set yaw angles - FLORIS expects shape (n_findex, n_turbines)
        yaw_array = np.array([yaw_angles])  # Add findex dimension
        
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
        # Set yaw angles and run simulation
        yaw_array = np.array([yaw_angles])
        self.fmodel.set(yaw_angles=yaw_array)
        self.fmodel.run()
        
        # Get turbine powers (in Watts, convert to kW)
        turbine_powers = self.fmodel.get_turbine_powers()[0] / 1000.0
        
        return turbine_powers
    
    def optimize(self, yaw_range=None, progress_interval=1000):
        """
        Run brute force optimization over all yaw angle combinations
        
        Args:
            yaw_range: Range of yaw angles to test (default from config)
            progress_interval: Print progress every N combinations
            
        Returns:
            Dictionary with optimization results
        """
        if yaw_range is None:
            yaw_range = range(config.YAW_ANGLE_MIN, config.YAW_ANGLE_MAX + 1, config.YAW_ANGLE_STEP)
        
        print("\n" + "="*60)
        print("STARTING BRUTE FORCE OPTIMIZATION")
        print("="*60)
        
        # Calculate baseline (all turbines at 0° yaw)
        baseline_yaw = [0] * self.n_turbines
        self.baseline_power = self.run_simulation(baseline_yaw)
        self.baseline_turbine_powers = self.get_turbine_powers(baseline_yaw)
        print(f"\nBaseline power (0° yaw): {self.baseline_power:.2f} kW")
        
        # Generate all combinations of yaw angles
        yaw_combinations = list(product(yaw_range, repeat=self.n_turbines))
        total_combinations = len(yaw_combinations)
        print(f"\nTesting {total_combinations:,} yaw angle combinations...")
        print(f"Yaw range: {min(yaw_range)}° to {max(yaw_range)}° (step: {config.YAW_ANGLE_STEP}°)")
        
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
            'optimal_yaw_angles': self.optimal_yaw_angles,
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
        print(f"Turbine Layout: 2x2 grid, 5D spacing")
        
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
        print(f"  Combinations Tested: {len(results['all_results']):,}")


def main():
    """
    Main execution function
    """
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
