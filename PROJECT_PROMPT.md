# Wake Steering Optimization Project - Implementation Prompt

## Project Overview
We're building a wind farm wake steering optimization tool for the MIT Energy and Climate Hackathon. The goal is to demonstrate how intelligently yawing (rotating) wind turbines can deflect their wakes and increase total farm energy production.

## Core Objective
Create a Python-based tool that:
1. Uses FLORIS (wind farm wake modeling library) to simulate a 4-turbine wind farm
2. Implements a brute force optimization algorithm to find optimal yaw angles for each turbine
3. Generates compelling visualizations showing the impact of wake steering
4. Calculates and displays energy/revenue gains

## Technical Requirements

### 1. Setup & Dependencies
- Use FLORIS for all wake modeling and flow field calculations
- Primary dependencies: `floris`, `numpy`, `matplotlib`, `pandas`
- Target Python 3.8+

### 2. Wind Farm Configuration
**4-Turbine Layout:**
- Simple 2x2 grid arrangement
- Turbine spacing: 5D x 5D (where D = rotor diameter, ~126m for NREL 5MW turbine)
- Positions (in meters):
  - Turbine 1: (0, 0)
  - Turbine 2: (0, 630)  
  - Turbine 3: (630, 0)
  - Turbine 4: (630, 630)

**Wind Conditions:**
- Wind direction: 270° (wind from west, blowing east)
- Wind speed: 8 m/s (good operating speed)
- Use NREL 5MW reference turbine (available in FLORIS)

### 3. Brute Force Optimization Algorithm

**Algorithm Logic:**
```
For each possible combination of yaw angles:
    - Turbine 1 yaw: -5° to +5° (in 1° increments = 11 options)
    - Turbine 2 yaw: -5° to +5° (in 1° increments = 11 options)
    - Turbine 3 yaw: -5° to +5° (in 1° increments = 11 options)
    - Turbine 4 yaw: -5° to +5° (in 1° increments = 11 options)
    - Total combinations: 11^4 = 14,641

    For each combination:
        1. Set yaw angles in FLORIS
        2. Run FLORIS simulation
        3. Calculate total farm power output
        4. Track this combination and its power output
    
    Return:
        - Best yaw configuration (the one with maximum total power)
        - All tested configurations (for visualization)
```

**Key Points:**
- Yaw angle of 0° means turbine faces directly into wind
- Negative yaw = counterclockwise rotation
- Positive yaw = clockwise rotation
- Each turbine gets its OWN optimal angle (not all the same)

### 4. Required Outputs

#### A. Optimization Results
- Best yaw angles: array of 4 values, e.g., `[-3°, 2°, 0°, 0°]`
- Baseline power (all turbines at 0° yaw)
- Optimized power (with best yaw angles)
- Percent improvement
- Individual turbine power outputs (baseline vs optimized)

#### B. Visualizations (using FLORIS built-in visualization)

**Visualization 1: Side-by-side Flow Field Comparison**
- Left panel: Flow field with baseline (0° yaw for all turbines)
- Right panel: Flow field with optimized yaw angles
- Show wind speed contours
- Mark turbine locations
- Title should include percent improvement

**Visualization 2: Power Output Bar Chart**
- Compare individual turbine power: baseline vs optimized
- 4 turbines, 2 bars each (baseline and optimized)
- Include total farm output

**Visualization 3: Optimization Analysis**
- Histogram of all 14,641 power outputs tested
- Mark baseline and optimal solutions
- Shows distribution of results

**Visualization 4: Annual Impact Projection**
- Extrapolate to annual energy gain (MWh/year)
- Calculate revenue impact (assume $50/MWh)
- Bar charts showing energy and revenue gains

#### C. Summary Statistics to Print
```
WAKE STEERING OPTIMIZATION RESULTS
====================================
Wind Conditions: 270° @ 8 m/s
Turbine Layout: 2x2 grid, 5D spacing

BASELINE (No Steering):
  Total Power: XXX kW
  T1: XXX kW | T2: XXX kW | T3: XXX kW | T4: XXX kW

OPTIMIZED (Wake Steering):
  Optimal Yaw Angles: [X°, X°, X°, X°]
  Total Power: XXX kW
  T1: XXX kW | T2: XXX kW | T3: XXX kW | T4: XXX kW

IMPROVEMENT:
  Power Gain: +XX.X%
  Additional Power: +XXX kW

ANNUAL IMPACT (8760 hours/year):
  Additional Energy: XXX MWh/year
  Additional Revenue: $XXX,XXX/year

Optimization Details:
  Combinations Tested: 14,641
  Computation Time: XX seconds
```

### 5. Code Structure

**Recommended file organization:**
```
wake_steering_optimizer.py    # Main optimization script
visualization.py              # All visualization functions
config.py                     # Configuration parameters
README.md                     # Project documentation
requirements.txt              # Python dependencies
```

**Key Functions to Implement:**
1. `setup_floris()` - Initialize FLORIS with 4-turbine farm
2. `run_simulation(yaw_angles)` - Run FLORIS for given yaw configuration
3. `brute_force_optimize()` - Main optimization loop
4. `plot_flow_comparison()` - Side-by-side flow fields
5. `plot_power_comparison()` - Bar chart of turbine outputs
6. `plot_optimization_analysis()` - Distribution of results
7. `calculate_annual_impact()` - Extrapolate to yearly numbers

### 6. FLORIS-Specific Implementation Notes

**Initialization:**
- Use FLORIS v3+ API
- Load NREL 5MW turbine model
- Set up GaussianModel or Jensen model for wake calculations
- Define 4-turbine layout with specified positions

**Running Simulations:**
- Use `fi.calculate_wake()` to compute flow field
- Access power with `fi.get_turbine_powers()`
- Set yaw angles with `fi.calculate_wake(yaw_angles=...)`

**Visualizations:**
- Use `fi.get_flow_data()` for flow field data
- FLORIS has built-in plotting utilities for horizontal plane cuts
- Can extract wind speed, turbulence intensity, power data

### 7. Important Considerations

**Physics Reminders:**
- Upstream turbines (west side) should steer wakes AWAY from downstream turbines
- Yawing costs power at the yawed turbine: P_yawed ≈ P_aligned × cos³(yaw)
- But can gain MORE power downstream by avoiding wakes
- Optimal solution balances this tradeoff

**Performance:**
- 14,641 simulations should take ~30-60 seconds on modern hardware
- Print progress updates every 1000 combinations
- Consider parallelization if time allows (not required for hackathon)

**Validation:**
- Sanity check: optimal yaw angles should be small (±5° range)
- Upstream turbines should have non-zero yaw, downstream often near 0°
- Improvement should be 1-5% (realistic for wake steering)

## Deliverables Checklist

- [ ] Working brute force optimization script
- [ ] Baseline vs optimized comparison (numerical results)
- [ ] Flow field visualization (side-by-side comparison)
- [ ] Power output bar charts
- [ ] Optimization distribution plot
- [ ] Annual impact calculations
- [ ] Clean console output with all key metrics
- [ ] README with usage instructions
- [ ] requirements.txt with all dependencies

## Success Criteria

The implementation is successful if:
1. ✓ All 14,641 yaw combinations are tested
2. ✓ Optimal configuration shows 1-5% improvement over baseline
3. ✓ Flow field visualizations clearly show wake deflection
4. ✓ Code runs in under 2 minutes
5. ✓ Results are reproducible
6. ✓ Visualizations are publication-quality for hackathon presentation

## Example Usage (Target API)

```python
# Initialize
optimizer = WakeSteeringOptimizer(
    n_turbines=4,
    layout='2x2_grid',
    wind_direction=270,
    wind_speed=8
)

# Run optimization
results = optimizer.optimize(yaw_range=range(-5, 6))

# Display results
results.print_summary()
results.plot_flow_comparison()
results.plot_power_comparison()
results.plot_optimization_analysis()
results.calculate_annual_impact()
```

---

## Additional Context for Hackathon Pitch

**Why this matters:**
- Wind farms lose 10-40% of potential energy to wake effects
- Wake steering is a proven technology (GE, Vestas use it commercially)
- Pure software solution = near-zero marginal cost, huge scalability
- 2-5% gain on 100MW farm = $500k-$1.5M additional revenue/year

**Limitations to acknowledge:**
- Simplified: steady wind conditions (real wind varies)
- Small farm: 4 turbines (real farms have 50-100+)
- Brute force: exponential complexity (real systems use gradient descent, RL)
- No turbulence modeling, terrain effects, or dynamic optimization

**Future extensions:**
- Machine learning to predict optimal angles from wind conditions
- Real-time SCADA integration
- Multi-objective optimization (power + structural loads)
- Stochastic wind modeling

Good luck with the hackathon! 🚀
