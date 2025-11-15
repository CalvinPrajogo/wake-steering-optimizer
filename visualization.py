"""
Visualization functions for wake steering optimization results
"""

import numpy as np
import matplotlib.pyplot as plt
import pandas as pd
import config


class OptimizationVisualizer:
    """
    Create visualizations for wake steering optimization results
    """
    
    def __init__(self, optimizer):
        """
        Initialize visualizer with optimizer instance
        
        Args:
            optimizer: WakeSteeringOptimizer instance with completed optimization
        """
        self.optimizer = optimizer
        self.results = optimizer.get_results()
        
    def plot_flow_comparison(self, save_path=None):
        """
        Create side-by-side flow field comparison (baseline vs optimized)
        
        Args:
            save_path: Optional path to save figure
        """
        print("Generating flow field comparison...")
        
        fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(16, 6))
        
        # TODO: Implement FLORIS flow field visualization
        # Left: Baseline flow field (0° yaw)
        # Right: Optimized flow field (optimal yaw angles)
        
        ax1.set_title("Baseline (0° Yaw)", fontsize=14, fontweight='bold')
        ax2.set_title(f"Optimized ({self.results['improvement_percent']:.2f}% Improvement)", 
                     fontsize=14, fontweight='bold')
        
        plt.tight_layout()
        
        if save_path:
            plt.savefig(save_path, dpi=config.FIGURE_DPI, bbox_inches='tight')
            print(f"Saved flow comparison to {save_path}")
        
        plt.show()
    
    def plot_power_comparison(self, save_path=None):
        """
        Create bar chart comparing individual turbine power outputs
        
        Args:
            save_path: Optional path to save figure
        """
        print("Generating power comparison chart...")
        
        # TODO: Get individual turbine powers from FLORIS
        # For now, use placeholder data
        turbine_labels = [f'T{i+1}' for i in range(self.optimizer.n_turbines)]
        
        fig, ax = plt.subplots(figsize=(10, 6))
        
        x = np.arange(len(turbine_labels))
        width = 0.35
        
        # TODO: Replace with actual turbine powers
        baseline_powers = [0] * self.optimizer.n_turbines
        optimized_powers = [0] * self.optimizer.n_turbines
        
        ax.bar(x - width/2, baseline_powers, width, label='Baseline', alpha=0.8)
        ax.bar(x + width/2, optimized_powers, width, label='Optimized', alpha=0.8)
        
        ax.set_xlabel('Turbine', fontsize=12, fontweight='bold')
        ax.set_ylabel('Power (kW)', fontsize=12, fontweight='bold')
        ax.set_title('Individual Turbine Power Comparison', fontsize=14, fontweight='bold')
        ax.set_xticks(x)
        ax.set_xticklabels(turbine_labels)
        ax.legend()
        ax.grid(axis='y', alpha=0.3)
        
        plt.tight_layout()
        
        if save_path:
            plt.savefig(save_path, dpi=config.FIGURE_DPI, bbox_inches='tight')
            print(f"Saved power comparison to {save_path}")
        
        plt.show()
    
    def plot_optimization_distribution(self, save_path=None):
        """
        Create histogram showing distribution of power outputs tested
        
        Args:
            save_path: Optional path to save figure
        """
        print("Generating optimization distribution plot...")
        
        # Extract all power values
        all_powers = [result['power'] for result in self.results['all_results']]
        
        fig, ax = plt.subplots(figsize=(10, 6))
        
        # Create histogram
        n, bins, patches = ax.hist(all_powers, bins=50, alpha=0.7, color='skyblue', edgecolor='black')
        
        # Mark baseline and optimal
        ax.axvline(self.results['baseline_power'], color='red', linestyle='--', 
                  linewidth=2, label=f'Baseline: {self.results["baseline_power"]:.0f} kW')
        ax.axvline(self.results['optimal_power'], color='green', linestyle='--', 
                  linewidth=2, label=f'Optimal: {self.results["optimal_power"]:.0f} kW')
        
        ax.set_xlabel('Total Power Output (kW)', fontsize=12, fontweight='bold')
        ax.set_ylabel('Number of Configurations', fontsize=12, fontweight='bold')
        ax.set_title('Distribution of All Tested Yaw Configurations', fontsize=14, fontweight='bold')
        ax.legend()
        ax.grid(axis='y', alpha=0.3)
        
        plt.tight_layout()
        
        if save_path:
            plt.savefig(save_path, dpi=config.FIGURE_DPI, bbox_inches='tight')
            print(f"Saved distribution plot to {save_path}")
        
        plt.show()
    
    def plot_annual_impact(self, save_path=None):
        """
        Create visualization of annual energy and revenue impact
        
        Args:
            save_path: Optional path to save figure
        """
        print("Generating annual impact projection...")
        
        # Calculate annual impacts
        power_gain = self.results['power_gain']
        annual_energy = power_gain * config.HOURS_PER_YEAR / 1000  # MWh/year
        annual_revenue = annual_energy * config.ELECTRICITY_PRICE
        
        fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(14, 5))
        
        # Energy gain bar chart
        categories = ['Baseline', 'Wake Steering', 'Additional']
        baseline_annual = self.results['baseline_power'] * config.HOURS_PER_YEAR / 1000
        optimized_annual = self.results['optimal_power'] * config.HOURS_PER_YEAR / 1000
        
        ax1.bar(['Baseline', 'With Wake Steering'], 
               [baseline_annual, optimized_annual], 
               color=['gray', 'green'], alpha=0.7)
        ax1.set_ylabel('Annual Energy (MWh/year)', fontsize=12, fontweight='bold')
        ax1.set_title('Annual Energy Production', fontsize=14, fontweight='bold')
        ax1.grid(axis='y', alpha=0.3)
        
        # Add value labels on bars
        for i, v in enumerate([baseline_annual, optimized_annual]):
            ax1.text(i, v, f'{v:.0f}', ha='center', va='bottom', fontweight='bold')
        
        # Revenue gain bar chart
        baseline_revenue = baseline_annual * config.ELECTRICITY_PRICE
        optimized_revenue = optimized_annual * config.ELECTRICITY_PRICE
        
        ax2.bar(['Baseline', 'With Wake Steering'], 
               [baseline_revenue, optimized_revenue], 
               color=['gray', 'green'], alpha=0.7)
        ax2.set_ylabel('Annual Revenue ($)', fontsize=12, fontweight='bold')
        ax2.set_title('Annual Revenue Impact', fontsize=14, fontweight='bold')
        ax2.grid(axis='y', alpha=0.3)
        
        # Add value labels on bars
        for i, v in enumerate([baseline_revenue, optimized_revenue]):
            ax2.text(i, v, f'${v:,.0f}', ha='center', va='bottom', fontweight='bold')
        
        plt.tight_layout()
        
        if save_path:
            plt.savefig(save_path, dpi=config.FIGURE_DPI, bbox_inches='tight')
            print(f"Saved annual impact to {save_path}")
        
        plt.show()
    
    def generate_all_plots(self, output_dir='figures'):
        """
        Generate all visualization plots
        
        Args:
            output_dir: Directory to save figures
        """
        import os
        os.makedirs(output_dir, exist_ok=True)
        
        print("\n" + "="*60)
        print("GENERATING ALL VISUALIZATIONS")
        print("="*60)
        
        self.plot_flow_comparison(save_path=f'{output_dir}/flow_comparison.png')
        self.plot_power_comparison(save_path=f'{output_dir}/power_comparison.png')
        self.plot_optimization_distribution(save_path=f'{output_dir}/optimization_distribution.png')
        self.plot_annual_impact(save_path=f'{output_dir}/annual_impact.png')
        
        print("\n" + "="*60)
        print(f"All visualizations saved to '{output_dir}/' directory")
        print("="*60)


def main():
    """
    Main execution - load results and generate plots
    """
    from wake_steering_optimizer import WakeSteeringOptimizer
    
    print("Loading optimization results...")
    # TODO: Either load saved results or run new optimization
    
    print("This script should be run after wake_steering_optimizer.py")
    print("It will generate visualizations from the optimization results")


if __name__ == "__main__":
    main()
