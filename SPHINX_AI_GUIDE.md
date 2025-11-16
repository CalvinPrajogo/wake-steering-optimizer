# Sphinx AI Integration Guide

## Overview

This project uses Sphinx AI to predict optimal yaw angles based on weather forecasts, enabling a **two-stage predictive optimization** strategy that reduces computation time by up to 60%.

## How It Works

### Traditional Approach (Without Prediction)
- Every hour: Test all 14,641 combinations (±5° × 4 turbines)
- Computation time: ~45 seconds per optimization
- **Total daily compute: ~18 minutes**

### Predictive Approach (With Sphinx AI)
1. **Day-Ahead (Once per day):**
   - Fetch tomorrow's weather forecast
   - Sphinx AI analyzes forecast and predicts optimal yaw angles
   - Runs full search with forecast data (~45 seconds)

2. **Real-Time (Every hour):**
   - Measure actual conditions from SCADA
   - Validate: Does actual ≈ forecast?
   - **If YES:** Narrow search around predictions (625 combos, ~3 seconds) ✅
   - **If NO:** Fall back to full search (14,641 combos, ~45 seconds)

3. **Result:**
   - Assuming 80% forecast accuracy: **~7 minutes/day** (60% reduction!)
   - Faster response time: Can optimize every 15 minutes instead of hourly
   - Smoother turbine operation: Small adjustments vs large angle changes

---

## Installation

Sphinx AI uses a CLI tool instead of HTTP API:

```bash
# Already installed in requirements.txt
pip install sphinx-ai-cli

# Set up API key in .env file
# Add this line to .env:
SPHINX_API_KEY="your-api-key-here"
```

**Note:** No manual login required! The system uses your API key from `.env` automatically.
Get your API key from: https://sphinx.ai/settings/api-keys

---

## Quick Start

### 1. Simple Prediction Example

```python
from sphinx_integration import SphinxPredictor

# Initialize
predictor = SphinxPredictor(notebook_path='data_preprocessing.ipynb')

# Tomorrow's forecast
forecast = {
    'wind_speed': 8.5,           # m/s
    'wind_direction': 270,       # degrees (270° = West)
    'turbulence_intensity': 0.07 # 7%
}

# Get prediction
prediction = predictor.predict_yaw_angles(forecast)

print(f"Predicted yaw angles: {prediction['predicted_yaws']}")
# Output: Predicted yaw angles: [-4, 3, 0, 1]

print(f"Confidence: {prediction['confidence']}")
# Output: Confidence: ['high', 'high', 'medium', 'medium']

print(f"Search range: ±{prediction['search_range']}°")
# Output: Search range: ±2°
```

### 2. Full Two-Stage Workflow

```python
from predictive_optimization import PredictiveOptimizer

# Initialize
optimizer = PredictiveOptimizer()

# Stage 1: Day-ahead prediction
forecast = {
    'wind_speed': 8.5,
    'wind_direction': 270,
    'turbulence_intensity': 0.07
}

prediction = optimizer.stage1_predict(forecast, save_prediction=True)
# Saves to: data/predictions/prediction_YYYYMMDD_HHMMSS.json

# Stage 2: Real-time optimization (next day)
actual = {
    'wind_speed': 8.3,    # Slightly different from forecast
    'wind_direction': 268, # 2° off
    'turbulence_intensity': 0.065
}

results = optimizer.stage2_optimize(prediction, actual)
# Output:
# ✅ Forecast valid! Running narrow search...
# Optimal yaw angles: [-4, 3, 0, 1]
# Power improvement: +0.52%
```

### 3. Forecast Validation Only

```python
from forecast_validator import is_forecast_valid, print_validation_report

forecast = {'wind_speed': 8.5, 'wind_direction': 270, 'turbulence_intensity': 0.07}
actual = {'wind_speed': 8.3, 'wind_direction': 268, 'turbulence_intensity': 0.065}

validation = is_forecast_valid(forecast, actual, mode='conservative')

print_validation_report(forecast, actual, validation)
# Output:
# ✅ Wind Speed: PASS (0.20 m/s deviation)
# ✅ Wind Direction: PASS (2° deviation)
# ✅ Turbulence: PASS (0.5% deviation)
# Recommendation: NARROW_SEARCH
```

---

## Configuration

### Tolerance Thresholds

Three preset modes in `forecast_validator.py`:

#### Conservative (Default - Recommended)
```python
TOLERANCE_THRESHOLDS = {
    'wind_speed': {'absolute': 1.0, 'relative': 0.12},  # ±1 m/s or ±12%
    'wind_direction': {'absolute': 8.0},                # ±8°
    'turbulence_intensity': {'absolute': 0.02}          # ±2 percentage points
}
```

#### Tight (More Accurate, More Fallbacks)
```python
TOLERANCE_THRESHOLDS_TIGHT = {
    'wind_speed': {'absolute': 0.5, 'relative': 0.08},  # ±0.5 m/s or ±8%
    'wind_direction': {'absolute': 5.0},                # ±5°
    'turbulence_intensity': {'absolute': 0.015}         # ±1.5%
}
```

#### Relaxed (Faster, Less Accurate)
```python
TOLERANCE_THRESHOLDS_RELAXED = {
    'wind_speed': {'absolute': 1.5, 'relative': 0.15},  # ±1.5 m/s or ±15%
    'wind_direction': {'absolute': 12.0},               # ±12°
    'turbulence_intensity': {'absolute': 0.03}          # ±3%
}
```

### Adaptive Yaw Ranges

The system automatically adjusts yaw search ranges based on physics:

| Condition | Yaw Range | Why |
|-----------|-----------|-----|
| Low wind (5 m/s) + Low TI (4%) | ±10-12° | Wakes strong, power loss small → aggressive works |
| Medium wind (8 m/s) + Medium TI (8%) | ±5-8° | Balanced optimization |
| High wind (13 m/s) or High TI (15%) | ±3° or OFF | Steering ineffective or counterproductive |

```python
from forecast_validator import get_recommended_yaw_range

# Example: 8 m/s wind, 6% turbulence
yaw_min, yaw_max = get_recommended_yaw_range(wind_speed=8.0, turbulence_intensity=0.06)
print(f"Recommended range: ±{yaw_max}°")  # Output: ±5°
```

---

## Environment Variables

Add to `.env` file:

```bash
# Weather API (required)
WEATHER_API_KEY="your-visual-crossing-api-key"

# Sphinx AI (required for predictions)
SPHINX_API_KEY="your-sphinx-api-key"
```

**Getting API Keys:**
- Weather: https://www.visualcrossing.com/weather-api
- Sphinx AI: https://sphinx.ai/settings/api-keys

**Note:** The system runs completely automatically once keys are set. No interactive login required.

---

## Sphinx AI Prompts

The system uses structured prompts to guide Sphinx AI:

### Yaw Angle Prediction
```
Predict optimal yaw angles for a 4-turbine wind farm based on these forecasted conditions:

Forecast Data:
- Wind Speed: 8.5 m/s
- Wind Direction: 270°
- Turbulence Intensity: 7%

Turbine Layout:
- T0: (0, 0) - Upstream left
- T1: (0, 630) - Upstream right  
- T2: (630, 0) - Downstream left
- T3: (630, 630) - Downstream right

Tasks:
1. Load and analyze historical NREL wind data
2. Find similar historical conditions
3. Analyze what yaw angles worked best
4. Predict optimal yaw angles for each turbine
5. Provide confidence levels
6. Suggest search range around predictions
```

### Forecast Accuracy Analysis
```
Analyze this forecast vs actual comparison:

Forecasted: 270° @ 8.5 m/s, TI=7%
Actual: 268° @ 8.3 m/s, TI=6.5%
Optimal Yaw Found: [-4°, +3°, 0°, +1°]

Questions:
1. How accurate was the forecast?
2. Would predicted angles have been close?
3. What patterns can we learn?
4. Update the prediction model
```

---

## Files Overview

```
wake-steering-optimizer/
├── sphinx_integration.py          # Sphinx CLI wrapper
├── forecast_validator.py          # Forecast validation logic
├── predictive_optimization.py     # Two-stage workflow
├── weather_forecast.py            # Weather API fetching
├── yaw_range_helper.py           # Adaptive range calculator
├── wake_steering_optimizer.py    # FLORIS optimization (updated)
└── data_preprocessing.ipynb       # Sphinx AI workspace notebook
```

### Key Classes

**SphinxPredictor** (`sphinx_integration.py`)
- `predict_yaw_angles()` - Get prediction from forecast
- `analyze_forecast_accuracy()` - Learn from results
- `determine_optimal_search_range()` - Adaptive ranging

**PredictiveOptimizer** (`predictive_optimization.py`)
- `stage1_predict()` - Day-ahead prediction
- `stage2_optimize()` - Real-time optimization

**Validation Functions** (`forecast_validator.py`)
- `is_forecast_valid()` - Check forecast accuracy
- `get_recommended_yaw_range()` - Physics-based ranging
- `calculate_search_range_from_prediction()` - Narrow search ranges

---

## Troubleshooting

### Sphinx CLI Not Found
```bash
pip install sphinx-ai-cli
```

### Authentication Issues
```bash
# Check if API key is set in .env
cat .env | grep SPHINX_API_KEY

# If missing, add it:
echo 'SPHINX_API_KEY="your-key-here"' >> .env
```

Get your API key from: https://sphinx.ai/settings/api-keys

### Slow Predictions
Sphinx AI typically takes 1-2 minutes for analysis. This is normal for the first prediction. Subsequent predictions may be faster as patterns are learned.

### Notebook Not Found
Ensure `data_preprocessing.ipynb` exists:
```python
predictor = SphinxPredictor(notebook_path='data_preprocessing.ipynb')
```

### API Key Errors
If you see authentication errors:
1. Verify SPHINX_API_KEY is in .env file
2. Check the key hasn't expired at https://sphinx.ai/settings/api-keys
3. Ensure .env file is in the project root directory
4. Try regenerating the API key if needed

---

## Performance Comparison

| Scenario | Combinations | Time | When |
|----------|--------------|------|------|
| **Narrow Search** | 625 | ~3s | Forecast valid (80% of time) |
| **Moderate Search** | 2,401 | ~8s | Partial match (10%) |
| **Full Search** | 14,641 | ~45s | Forecast invalid (10%) |
| **Aggressive Full** | 194,481 | ~10min | Low wind + low TI |

**Daily savings:** Traditional (18 min) → Predictive (7 min) = **60% reduction**

---

## Next Steps

1. **Collect Historical Data:**
   ```bash
   python nrel_fetch.py --api-key YOUR_KEY --email your@email.com \
     --lat 41.119917 --lon -71.516111 --years 2012
   ```

2. **Train Sphinx AI:**
   - Load historical data into `data_preprocessing.ipynb`
   - Run Sphinx analysis to learn patterns
   - Export trained insights

3. **Run Daily Predictions:**
   ```bash
   # Fetch tomorrow's forecast
   python weather_forecast.py
   
   # Generate prediction
   python -c "
   from predictive_optimization import PredictiveOptimizer
   import json
   
   optimizer = PredictiveOptimizer()
   forecast = json.load(open('data/raw/forecast_data_2024-11-16.json'))
   prediction = optimizer.stage1_predict(forecast)
   "
   ```

4. **Automate with Cron:**
   ```bash
   # Crontab: Run prediction at 6 PM daily
   0 18 * * * cd /path/to/project && python predictive_optimization.py
   ```

---

## References

- [Sphinx AI CLI Documentation](https://docs.sphinx.ai/)
- [Visual Crossing Weather API](https://www.visualcrossing.com/weather-api)
- [FLORIS Documentation](https://nrel.github.io/floris/)
- [NREL Wind Toolkit](https://www.nrel.gov/grid/wind-toolkit.html)
