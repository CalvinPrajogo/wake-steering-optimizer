"""
Compare wake steering optimization for different turbine spacings
Tests original layout vs 20% closer spacing
"""
import config
from wake_steering_optimizer import WakeSteeringOptimizer


def scale_turbine_positions(positions, scale_factor):
    """
    Scale turbine positions relative to the first turbine
    
    Args:
        positions: List of (x, y) tuples
        scale_factor: Multiplier (0.8 = 20% closer, 1.2 = 20% farther)
    
    Returns:
        Scaled positions list
    """
    if not positions:
        return positions
    
    # Keep first turbine at origin
    scaled = [positions[0]]
    
    # Scale all other positions relative to origin
    for x, y in positions[1:]:
        scaled.append((x * scale_factor, y * scale_factor))
    
    return scaled


def calculate_distances(positions):
    """
    Calculate distances between consecutive turbines
    
    Args:
        positions: List of (x, y) tuples
    
    Returns:
        List of distances between turbines
    """
    distances = []
    for i in range(len(positions) - 1):
        x1, y1 = positions[i]
        x2, y2 = positions[i+1]
        dist = ((x2 - x1)**2 + (y2 - y1)**2)**0.5
        distances.append(dist)
    return distances


def compare_layouts(wind_direction=240, wind_speed=8.0):
    """
    Compare optimization results for original vs 20% closer layout
    
    Args:
        wind_direction: Wind direction in degrees (default: 240° - best case)
        wind_speed: Wind speed in m/s
    """
    print("\n" + "="*80)
    print("COMPARING TURBINE LAYOUTS: ORIGINAL vs 20% CLOSER")
    print("="*80)
    
    # Original layout
    original_positions = config.TURBINE_POSITIONS
    closer_positions = scale_turbine_positions(original_positions, 0.8)
    
    # Calculate distances
    orig_distances = calculate_distances(original_positions)
    closer_distances = calculate_distances(closer_positions)
    
    print("\n" + "-"*80)
    print("LAYOUT COMPARISON")
    print("-"*80)
    print(f"\n{'Turbine':<12} {'Original Position':<25} {'20% Closer Position':<25} {'Distance Change':<15}")
    print("-"*80)
    
    for i, ((x_orig, y_orig), (x_close, y_close)) in enumerate(zip(original_positions, closer_positions), 1):
        if i == 1:
            print(f"T{i:<11} ({x_orig:>8.2f}, {y_orig:>8.2f})     ({x_close:>8.2f}, {y_close:>8.2f})     {'Reference':<15}")
        else:
            dist_orig = orig_distances[i-2]
            dist_close = closer_distances[i-2]
            change_pct = ((dist_close - dist_orig) / dist_orig) * 100
            print(f"T{i:<11} ({x_orig:>8.2f}, {y_orig:>8.2f})     ({x_close:>8.2f}, {y_close:>8.2f})     {change_pct:>6.1f}%")
    
    print("\n" + "-"*80)
    print("INTER-TURBINE DISTANCES")
    print("-"*80)
    print(f"{'Turbine Pair':<15} {'Original (m)':<18} {'20% Closer (m)':<18} {'Change %':<12}")
    print("-"*80)
    for i, (d_orig, d_close) in enumerate(zip(orig_distances, closer_distances), 1):
        change_pct = ((d_close - d_orig) / d_orig) * 100
        print(f"T{i} → T{i+1}        {d_orig:<18.2f} {d_close:<18.2f} {change_pct:>6.1f}%")
    
    # Test both layouts
    results = {}
    
    for layout_name, positions in [("Original", original_positions), 
                                   ("20% Closer", closer_positions)]:
        print(f"\n{'='*80}")
        print(f"Testing {layout_name} Layout")
        print(f"{'='*80}")
        
        optimizer = WakeSteeringOptimizer(
            wind_direction=wind_direction,
            wind_speed=wind_speed,
            turbine_positions=positions
        )
        
        results[layout_name] = optimizer.optimize()
        optimizer.print_summary()
    
    # Comparison summary
    print("\n" + "="*80)
    print("LAYOUT COMPARISON SUMMARY")
    print("="*80)
    print(f"Wind Conditions: {wind_direction}° @ {wind_speed} m/s")
    print("\n" + "-"*80)
    print(f"{'Layout':<20} {'Baseline (kW)':<18} {'Optimal (kW)':<18} {'Improvement %':<15} {'Max Yaw (°)':<12}")
    print("-"*80)
    
    for layout_name in ["Original", "20% Closer"]:
        r = results[layout_name]
        max_yaw = max([abs(y) for y in r['optimal_yaw_angles']])
        print(f"{layout_name:<20} {r['baseline_power']:<18.2f} "
              f"{r['optimal_power']:<18.2f} {r['improvement_percent']:<15.2f} {max_yaw:<12.2f}")
    
    # Calculate differences
    orig_baseline = results["Original"]['baseline_power']
    closer_baseline = results["20% Closer"]['baseline_power']
    baseline_diff = closer_baseline - orig_baseline
    baseline_diff_pct = (baseline_diff / orig_baseline) * 100
    
    orig_optimal = results["Original"]['optimal_power']
    closer_optimal = results["20% Closer"]['optimal_power']
    optimal_diff = closer_optimal - orig_optimal
    optimal_diff_pct = (optimal_diff / orig_optimal) * 100
    
    orig_improvement = results["Original"]['improvement_percent']
    closer_improvement = results["20% Closer"]['improvement_percent']
    improvement_diff = closer_improvement - orig_improvement
    
    print("\n" + "-"*80)
    print("KEY INSIGHTS")
    print("-"*80)
    print(f"Baseline Power Change: {baseline_diff:+.2f} kW ({baseline_diff_pct:+.2f}%)")
    print(f"  → Closer spacing {'reduces' if baseline_diff < 0 else 'increases'} baseline power")
    print(f"\nOptimal Power Change: {optimal_diff:+.2f} kW ({optimal_diff_pct:+.2f}%)")
    print(f"  → Closer spacing {'reduces' if optimal_diff < 0 else 'increases'} optimal power")
    print(f"\nImprovement % Change: {improvement_diff:+.2f} percentage points")
    print(f"  → Wake steering benefit is {'lower' if improvement_diff < 0 else 'higher'} with closer spacing")
    
    # Power gain comparison
    orig_gain = results["Original"]['power_gain']
    closer_gain = results["20% Closer"]['power_gain']
    gain_diff = closer_gain - orig_gain
    
    print(f"\nAbsolute Power Gain:")
    print(f"  Original layout: {orig_gain:.2f} kW")
    print(f"  20% Closer:      {closer_gain:.2f} kW")
    print(f"  Difference:      {gain_diff:+.2f} kW")
    
    return results


def test_multiple_wind_directions():
    """
    Test both layouts across multiple wind directions
    """
    wind_directions = [30, 60, 210, 240]  # Directions that showed improvement
    wind_speed = 8.0
    
    print("\n" + "="*80)
    print("MULTI-DIRECTION LAYOUT COMPARISON")
    print("="*80)
    
    original_positions = config.TURBINE_POSITIONS
    closer_positions = scale_turbine_positions(original_positions, 0.8)
    
    all_results = {}
    
    for wind_dir in wind_directions:
        print(f"\n{'='*80}")
        print(f"Testing Wind Direction: {wind_dir}°")
        print(f"{'='*80}")
        
        results = {}
        for layout_name, positions in [("Original", original_positions), 
                                       ("20% Closer", closer_positions)]:
            print(f"\n{layout_name} Layout:")
            optimizer = WakeSteeringOptimizer(
                wind_direction=wind_dir,
                wind_speed=wind_speed,
                turbine_positions=positions
            )
            results[layout_name] = optimizer.optimize()
        
        all_results[wind_dir] = results
    
    # Summary table
    print("\n" + "="*80)
    print("MULTI-DIRECTION COMPARISON SUMMARY")
    print("="*80)
    print(f"{'Wind Dir':<12} {'Layout':<15} {'Baseline (kW)':<18} {'Optimal (kW)':<18} {'Improvement %':<15}")
    print("-"*80)
    
    for wind_dir in wind_directions:
        for layout_name in ["Original", "20% Closer"]:
            r = all_results[wind_dir][layout_name]
            print(f"{wind_dir:<12} {layout_name:<15} {r['baseline_power']:<18.2f} "
                  f"{r['optimal_power']:<18.2f} {r['improvement_percent']:<15.2f}")
    
    return all_results


if __name__ == "__main__":
    import sys
    
    if len(sys.argv) > 1 and sys.argv[1] == "--multi":
        # Test multiple wind directions
        test_multiple_wind_directions()
    else:
        # Single wind direction comparison (default: 240° - best case)
        compare_layouts(wind_direction=240, wind_speed=8.0)
        
        print("\n" + "="*80)
        print("TIP: Run with --multi flag to test multiple wind directions")
        print("="*80)

