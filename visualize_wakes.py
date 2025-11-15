"""
Generate wake steering flow visualization comparing baseline vs optimized yaw angles
Based on FLORIS documentation example
"""

import numpy as np
import matplotlib.pyplot as plt
from floris import FlorisModel
from floris.flow_visualization import visualize_cut_plane
from floris.layout_visualization import plot_turbine_labels


def visualize_wake_steering_comparison():
    """
    Create side-by-side comparison of wake patterns with and without yaw optimization
    """
    # Initialize FLORIS model
    print("Loading FLORIS model...")
    fmodel = FlorisModel("floris_config.yaml")
    
    # Wind conditions
    wind_direction = 270.0  # Wind from west
    wind_speed = 8.0  # m/s
    turbulence_intensity = 0.06
    
    # Example optimal yaw angles (you can replace these with actual optimized values)
    # Format: [T1, T2, T3, T4] in degrees
    optimal_yaw_angles = np.array([[-5.0, 3.0, 0.0, 0.0]])  # Example yaw configuration
    
    # Create figure with 1 row, 2 columns
    fig, axarr = plt.subplots(1, 2, figsize=(16, 6))
    
    print("Generating baseline (aligned) flow field...")
    # LEFT PLOT: Baseline (no yaw, all turbines aligned)
    fmodel.reset_operation()
    fmodel.set(
        wind_speeds=[wind_speed],
        wind_directions=[wind_direction],
        turbulence_intensities=[turbulence_intensity]
    )
    fmodel.run()
    
    # Calculate horizontal plane at hub height (90m)
    horizontal_plane = fmodel.calculate_horizontal_plane(height=90.0)
    
    # Visualize the flow field
    visualize_cut_plane(
        horizontal_plane,
        ax=axarr[0],
        title=f"{wind_direction}° - Baseline (0° Yaw)",
        color_bar=True,
        cmap='coolwarm'
    )
    plot_turbine_labels(fmodel, axarr[0])
    
    # Get baseline power
    baseline_powers = fmodel.get_turbine_powers()[0] / 1000.0
    baseline_total = np.sum(baseline_powers)
    axarr[0].text(
        0.02, 0.98,
        f'Total: {baseline_total:.1f} kW',
        transform=axarr[0].transAxes,
        fontsize=12,
        verticalalignment='top',
        bbox=dict(boxstyle='round', facecolor='white', alpha=0.8)
    )
    
    print("Generating optimized (yawed) flow field...")
    # RIGHT PLOT: Optimized with yaw angles
    fmodel.reset_operation()
    fmodel.set(
        wind_speeds=[wind_speed],
        wind_directions=[wind_direction],
        turbulence_intensities=[turbulence_intensity],
        yaw_angles=optimal_yaw_angles
    )
    fmodel.run()
    
    # Calculate horizontal plane
    horizontal_plane = fmodel.calculate_horizontal_plane(height=90.0)
    
    # Visualize the flow field
    visualize_cut_plane(
        horizontal_plane,
        ax=axarr[1],
        title=f"{wind_direction}° - Optimized Yaw {optimal_yaw_angles[0]}",
        color_bar=True,
        cmap='coolwarm'
    )
    plot_turbine_labels(fmodel, axarr[1])
    
    # Get optimized power
    optimized_powers = fmodel.get_turbine_powers()[0] / 1000.0
    optimized_total = np.sum(optimized_powers)
    improvement = ((optimized_total - baseline_total) / baseline_total) * 100
    
    axarr[1].text(
        0.02, 0.98,
        f'Total: {optimized_total:.1f} kW\n+{improvement:.2f}%',
        transform=axarr[1].transAxes,
        fontsize=12,
        verticalalignment='top',
        bbox=dict(boxstyle='round', facecolor='lightgreen', alpha=0.8)
    )
    
    # Overall title
    fig.suptitle(
        'Wake Steering Flow Field Comparison',
        fontsize=16,
        fontweight='bold',
        y=0.98
    )
    
    plt.tight_layout()
    
    # Save figure
    output_path = 'figures/wake_flow_comparison.png'
    plt.savefig(output_path, dpi=150, bbox_inches='tight')
    print(f"\n✓ Figure saved to: {output_path}")
    
    # Print summary
    print("\n" + "="*60)
    print("WAKE STEERING FLOW VISUALIZATION")
    print("="*60)
    print(f"Wind Conditions: {wind_direction}° @ {wind_speed} m/s")
    print(f"\nBaseline Power:")
    for i, power in enumerate(baseline_powers):
        print(f"  T{i}: {power:.2f} kW")
    print(f"  Total: {baseline_total:.2f} kW")
    
    print(f"\nOptimized Power (Yaw: {optimal_yaw_angles[0]}):")
    for i, power in enumerate(optimized_powers):
        print(f"  T{i}: {power:.2f} kW")
    print(f"  Total: {optimized_total:.2f} kW")
    
    print(f"\nImprovement: +{improvement:.2f}%")
    print("="*60)
    
    plt.show()
    
    return fig, baseline_total, optimized_total, improvement


if __name__ == "__main__":
    visualize_wake_steering_comparison()
