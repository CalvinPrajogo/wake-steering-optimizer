"""
Helper functions for determining optimal yaw angle ranges
Based on wind farm data characteristics
"""

import numpy as np
import pandas as pd
import matplotlib.pyplot as plt


def calculate_power_loss(yaw_angles):
    """
    Calculate power loss percentage for given yaw angles
    
    Power loss follows: P_yawed = P_aligned * cos³(yaw_angle)
    
    Args:
        yaw_angles: Array of yaw angles in degrees
        
    Returns:
        Power loss percentages for each angle
    """
    return (1 - np.cos(np.radians(yaw_angles))**3) * 100


def estimate_computation_time(yaw_range, n_turbines=4, time_per_sim=0.003):
    """
    Estimate computation time for brute force optimization
    
    Args:
        yaw_range: Max yaw angle (e.g., 5 means -5 to +5)
        n_turbines: Number of turbines
        time_per_sim: Seconds per FLORIS simulation (default ~3ms)
        
    Returns:
        Estimated time in seconds and number of combinations
    """
    n_angles = 2 * yaw_range + 1
    n_combinations = n_angles ** n_turbines
    est_time = n_combinations * time_per_sim
    
    return {
        'n_combinations': n_combinations,
        'estimated_seconds': est_time,
        'estimated_minutes': est_time / 60
    }


def recommend_yaw_range(wind_speed_mean, wind_speed_std, turbulence_intensity_mean,
                       max_power_loss_pct=5.0, max_computation_minutes=5.0):
    """
    Recommend optimal yaw range based on wind characteristics
    
    Args:
        wind_speed_mean: Average wind speed (m/s)
        wind_speed_std: Standard deviation of wind speed (m/s)
        turbulence_intensity_mean: Average turbulence intensity (decimal, e.g., 0.06)
        max_power_loss_pct: Maximum acceptable power loss per turbine (%)
        max_computation_minutes: Maximum computation time (minutes)
        
    Returns:
        Dictionary with recommendation and analysis
    """
    recommendations = []
    
    # Test different yaw ranges
    test_ranges = [3, 5, 8, 10, 12, 15, 20, 25]
    
    results = []
    for yaw_range in test_ranges:
        power_loss = calculate_power_loss([yaw_range])[0]
        comp_info = estimate_computation_time(yaw_range)
        
        # Check if meets constraints
        meets_power_constraint = power_loss <= max_power_loss_pct
        meets_time_constraint = comp_info['estimated_minutes'] <= max_computation_minutes
        
        results.append({
            'yaw_range': yaw_range,
            'max_power_loss': power_loss,
            'n_combinations': comp_info['n_combinations'],
            'est_time_min': comp_info['estimated_minutes'],
            'meets_constraints': meets_power_constraint and meets_time_constraint
        })
    
    # Convert to DataFrame for easy analysis
    df = pd.DataFrame(results)
    
    # Find best option that meets constraints
    valid_options = df[df['meets_constraints']]
    
    if len(valid_options) > 0:
        # Choose largest yaw range that meets constraints
        recommended = valid_options.iloc[-1]
    else:
        # If nothing meets constraints, choose smallest yaw range
        recommended = df.iloc[0]
    
    # Additional logic based on wind conditions
    reasoning = []
    
    if wind_speed_mean > 10:
        reasoning.append(f"High wind speed ({wind_speed_mean:.1f} m/s) → smaller yaw angles recommended")
        suggested_adjustment = -2
    elif wind_speed_mean < 6:
        reasoning.append(f"Low wind speed ({wind_speed_mean:.1f} m/s) → larger yaw angles can be beneficial")
        suggested_adjustment = 2
    else:
        reasoning.append(f"Moderate wind speed ({wind_speed_mean:.1f} m/s) → standard yaw range appropriate")
        suggested_adjustment = 0
    
    if turbulence_intensity_mean > 0.15:
        reasoning.append(f"High turbulence (TI={turbulence_intensity_mean:.2f}) → wakes disperse quickly, smaller yaw range")
        suggested_adjustment -= 1
    elif turbulence_intensity_mean < 0.05:
        reasoning.append(f"Low turbulence (TI={turbulence_intensity_mean:.2f}) → wakes persist, larger yaw range beneficial")
        suggested_adjustment += 1
    
    if wind_speed_std > 3:
        reasoning.append(f"High wind variability (σ={wind_speed_std:.1f} m/s) → consider wider range")
        suggested_adjustment += 1
    
    # Adjust recommendation
    final_yaw_range = int(recommended['yaw_range'] + suggested_adjustment)
    final_yaw_range = max(3, min(25, final_yaw_range))  # Clamp between 3 and 25
    
    return {
        'recommended_yaw_range': final_yaw_range,
        'yaw_angles': list(range(-final_yaw_range, final_yaw_range + 1)),
        'power_loss_at_max': calculate_power_loss([final_yaw_range])[0],
        'n_combinations': (2 * final_yaw_range + 1) ** 4,
        'estimated_time_min': estimate_computation_time(final_yaw_range)['estimated_minutes'],
        'reasoning': reasoning,
        'all_options': df
    }


def plot_yaw_range_analysis(results):
    """
    Visualize trade-offs between yaw range, power loss, and computation time
    
    Args:
        results: DataFrame with columns yaw_range, max_power_loss, est_time_min, n_combinations
    """
    fig, axes = plt.subplots(1, 3, figsize=(16, 5))
    
    # Plot 1: Power loss vs yaw range
    axes[0].plot(results['yaw_range'], results['max_power_loss'], 'o-', linewidth=2, markersize=8)
    axes[0].axhline(y=5, color='r', linestyle='--', label='5% loss threshold')
    axes[0].set_xlabel('Yaw Range (degrees)', fontsize=12, fontweight='bold')
    axes[0].set_ylabel('Maximum Power Loss (%)', fontsize=12, fontweight='bold')
    axes[0].set_title('Power Loss vs Yaw Range', fontsize=14, fontweight='bold')
    axes[0].grid(alpha=0.3)
    axes[0].legend()
    
    # Plot 2: Computation time vs yaw range
    axes[1].plot(results['yaw_range'], results['est_time_min'], 'o-', linewidth=2, markersize=8, color='orange')
    axes[1].axhline(y=5, color='r', linestyle='--', label='5 min threshold')
    axes[1].set_xlabel('Yaw Range (degrees)', fontsize=12, fontweight='bold')
    axes[1].set_ylabel('Estimated Time (minutes)', fontsize=12, fontweight='bold')
    axes[1].set_title('Computation Time vs Yaw Range', fontsize=14, fontweight='bold')
    axes[1].grid(alpha=0.3)
    axes[1].legend()
    
    # Plot 3: Number of combinations
    axes[2].semilogy(results['yaw_range'], results['n_combinations'], 'o-', linewidth=2, markersize=8, color='green')
    axes[2].set_xlabel('Yaw Range (degrees)', fontsize=12, fontweight='bold')
    axes[2].set_ylabel('Number of Combinations (log scale)', fontsize=12, fontweight='bold')
    axes[2].set_title('Search Space Size', fontsize=14, fontweight='bold')
    axes[2].grid(alpha=0.3)
    
    plt.tight_layout()
    return fig


def print_recommendation_summary(recommendation):
    """
    Print a formatted summary of the yaw range recommendation
    
    Args:
        recommendation: Dictionary from recommend_yaw_range()
    """
    print("="*60)
    print("YAW RANGE RECOMMENDATION")
    print("="*60)
    print(f"\nRecommended Yaw Range: ±{recommendation['recommended_yaw_range']}°")
    print(f"Yaw Angles to Test: {recommendation['yaw_angles'][0]}° to {recommendation['yaw_angles'][-1]}° (step: 1°)")
    print(f"\nOptimization Details:")
    print(f"  Number of combinations: {recommendation['n_combinations']:,}")
    print(f"  Estimated computation time: {recommendation['estimated_time_min']:.1f} minutes")
    print(f"  Max power loss at extreme yaw: {recommendation['power_loss_at_max']:.1f}%")
    
    print(f"\nReasoning:")
    for reason in recommendation['reasoning']:
        print(f"  • {reason}")
    
    print("\n" + "="*60)


# Example usage
if __name__ == "__main__":
    # Example wind farm data
    wind_speed_mean = 8.5  # m/s
    wind_speed_std = 2.1   # m/s
    ti_mean = 0.06         # 6% turbulence
    
    print("Example Analysis:")
    print(f"Wind Speed: {wind_speed_mean} ± {wind_speed_std} m/s")
    print(f"Turbulence Intensity: {ti_mean*100:.0f}%\n")
    
    # Get recommendation
    rec = recommend_yaw_range(
        wind_speed_mean=wind_speed_mean,
        wind_speed_std=wind_speed_std,
        turbulence_intensity_mean=ti_mean,
        max_power_loss_pct=5.0,
        max_computation_minutes=5.0
    )
    
    # Print results
    print_recommendation_summary(rec)
    
    # Plot analysis
    fig = plot_yaw_range_analysis(rec['all_options'])
    plt.savefig('figures/yaw_range_analysis.png', dpi=150, bbox_inches='tight')
    print("\nAnalysis plot saved to: figures/yaw_range_analysis.png")
    plt.show()
