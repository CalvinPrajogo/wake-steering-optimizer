"""
forecast_validator.py

Validates if actual real-time conditions match forecasted conditions
to determine if narrow search around predicted yaw angles can be used.
"""

import numpy as np
from typing import Dict, Tuple


# Conservative tolerance thresholds (recommended for production)
TOLERANCE_THRESHOLDS = {
    'wind_speed': {
        'absolute': 1.0,      # ±1.0 m/s
        'relative': 0.12      # ±12% of forecasted speed
    },
    'wind_direction': {
        'absolute': 8.0       # ±8 degrees
    },
    'turbulence_intensity': {
        'absolute': 0.02      # ±2 percentage points (e.g., 6% → 4-8%)
    }
}

# Aggressive thresholds (tighter - more fallbacks to full search)
TOLERANCE_THRESHOLDS_TIGHT = {
    'wind_speed': {'absolute': 0.5, 'relative': 0.08},      # ±0.5 m/s or ±8%
    'wind_direction': {'absolute': 5.0},                     # ±5°
    'turbulence_intensity': {'absolute': 0.015}              # ±1.5 percentage points
}

# Relaxed thresholds (wider - fewer fallbacks)
TOLERANCE_THRESHOLDS_RELAXED = {
    'wind_speed': {'absolute': 1.5, 'relative': 0.15},      # ±1.5 m/s or ±15%
    'wind_direction': {'absolute': 12.0},                    # ±12°
    'turbulence_intensity': {'absolute': 0.03}               # ±3 percentage points
}


def is_forecast_valid(forecast: Dict, actual: Dict, 
                     thresholds: Dict = None,
                     mode: str = 'conservative') -> Dict:
    """
    Check if actual conditions are close enough to forecast
    
    Args:
        forecast: Dictionary with forecasted conditions
            - wind_speed (m/s)
            - wind_direction (degrees)
            - turbulence_intensity (decimal, e.g., 0.06 for 6%)
        actual: Dictionary with actual measured conditions (same format)
        thresholds: Custom threshold dictionary (overrides mode)
        mode: 'conservative', 'tight', or 'relaxed' (default: 'conservative')
        
    Returns:
        Dictionary with:
            - valid: bool - True if all conditions within tolerance
            - speed_ok: bool
            - direction_ok: bool
            - turbulence_ok: bool
            - deviations: dict with actual deviation values
            - recommendation: str - What action to take
    """
    # Select thresholds
    if thresholds is None:
        if mode == 'tight':
            thresholds = TOLERANCE_THRESHOLDS_TIGHT
        elif mode == 'relaxed':
            thresholds = TOLERANCE_THRESHOLDS_RELAXED
        else:  # conservative (default)
            thresholds = TOLERANCE_THRESHOLDS
    
    # Wind speed check (use whichever is more lenient)
    speed_diff_abs = abs(actual['wind_speed'] - forecast['wind_speed'])
    speed_diff_rel = speed_diff_abs / forecast['wind_speed'] if forecast['wind_speed'] > 0 else 0
    speed_ok = (speed_diff_abs <= thresholds['wind_speed']['absolute'] or 
                speed_diff_rel <= thresholds['wind_speed']['relative'])
    
    # Wind direction check (handle wrapping: 359° and 1° are only 2° apart)
    dir_diff = abs(actual['wind_direction'] - forecast['wind_direction'])
    dir_diff = min(dir_diff, 360 - dir_diff)  # Handle wrap-around
    direction_ok = dir_diff <= thresholds['wind_direction']['absolute']
    
    # Turbulence check
    ti_diff = abs(actual['turbulence_intensity'] - forecast['turbulence_intensity'])
    turbulence_ok = ti_diff <= thresholds['turbulence_intensity']['absolute']
    
    # Overall validity
    valid = speed_ok and direction_ok and turbulence_ok
    
    # Determine recommendation
    if valid:
        recommendation = "NARROW_SEARCH"  # Use predicted yaws with ±2° search
    elif speed_ok and direction_ok:
        recommendation = "MODERATE_SEARCH"  # TI different but wind ok, use ±3° search
    else:
        recommendation = "FULL_SEARCH"  # Conditions changed significantly
    
    return {
        'valid': valid,
        'speed_ok': speed_ok,
        'direction_ok': direction_ok,
        'turbulence_ok': turbulence_ok,
        'deviations': {
            'speed_abs': speed_diff_abs,
            'speed_rel': speed_diff_rel,
            'direction': dir_diff,
            'turbulence': ti_diff
        },
        'recommendation': recommendation,
        'threshold_mode': mode
    }


def get_recommended_yaw_range(wind_speed: float, turbulence_intensity: float) -> Tuple[int, int]:
    """
    Determine optimal yaw range based on atmospheric conditions
    
    Args:
        wind_speed: Wind speed in m/s
        turbulence_intensity: Turbulence intensity (decimal, e.g., 0.06 for 6%)
        
    Returns:
        Tuple of (min_yaw, max_yaw) in degrees
    """
    
    # Low wind + Low TI = Most beneficial for wake steering
    if wind_speed < 7 and turbulence_intensity < 0.06:
        return (-12, 12)  # Aggressive
    
    # Low wind + Medium TI = Beneficial
    elif wind_speed < 7 and turbulence_intensity < 0.12:
        return (-10, 10)  # Moderate-aggressive
    
    # Low wind + High TI = Less beneficial but still worth it
    elif wind_speed < 7:
        return (-8, 8)    # Moderate
    
    # Medium wind + Low TI = Good balance
    elif wind_speed < 11 and turbulence_intensity < 0.06:
        return (-8, 8)    # Moderate
    
    # Medium wind + Medium TI = Standard case
    elif wind_speed < 11 and turbulence_intensity < 0.12:
        return (-5, 5)    # Conservative (typical case)
    
    # Medium wind + High TI = Minimal steering
    elif wind_speed < 11:
        return (-3, 3)    # Very conservative
    
    # High wind = Minimal or no steering
    else:  # wind_speed >= 11
        if turbulence_intensity > 0.12:
            return (0, 0)     # Disable steering
        else:
            return (-3, 3)    # Very conservative


def calculate_search_range_from_prediction(predicted_yaws: list, 
                                           confidence: list,
                                           validation_result: Dict) -> list:
    """
    Calculate search ranges around predicted yaw angles based on confidence and validation
    
    Args:
        predicted_yaws: List of predicted yaw angles [T0, T1, T2, T3]
        confidence: List of confidence levels ['high', 'medium', 'low']
        validation_result: Result from is_forecast_valid()
        
    Returns:
        List of (min, max) tuples for each turbine's search range
    """
    search_ranges = []
    
    for i, (pred_yaw, conf) in enumerate(zip(predicted_yaws, confidence)):
        # Base range on confidence
        if conf == 'high':
            base_range = 1  # ±1°
        elif conf == 'medium':
            base_range = 2  # ±2°
        else:  # low
            base_range = 3  # ±3°
        
        # Adjust based on validation result
        if validation_result['recommendation'] == 'NARROW_SEARCH':
            # Forecast valid, use narrow range
            delta = base_range
        elif validation_result['recommendation'] == 'MODERATE_SEARCH':
            # Forecast partially valid, expand range
            delta = base_range + 1
        else:  # FULL_SEARCH
            # Forecast invalid, don't use predictions (return None)
            return None
        
        # Calculate min/max for this turbine
        yaw_min = int(pred_yaw - delta)
        yaw_max = int(pred_yaw + delta)
        
        # Clamp to reasonable bounds (±15° max)
        yaw_min = max(-15, yaw_min)
        yaw_max = min(15, yaw_max)
        
        search_ranges.append((yaw_min, yaw_max))
    
    return search_ranges


def print_validation_report(forecast: Dict, actual: Dict, validation: Dict):
    """Print formatted validation report"""
    
    print("="*60)
    print("FORECAST VALIDATION REPORT")
    print("="*60)
    
    print("\nForecasted Conditions:")
    print(f"  Wind Speed: {forecast['wind_speed']:.1f} m/s")
    print(f"  Wind Direction: {forecast['wind_direction']:.0f}°")
    print(f"  Turbulence: {forecast['turbulence_intensity']*100:.1f}%")
    
    print("\nActual Conditions:")
    print(f"  Wind Speed: {actual['wind_speed']:.1f} m/s")
    print(f"  Wind Direction: {actual['wind_direction']:.0f}°")
    print(f"  Turbulence: {actual['turbulence_intensity']*100:.1f}%")
    
    print("\nDeviations:")
    dev = validation['deviations']
    print(f"  Wind Speed: {dev['speed_abs']:.2f} m/s ({dev['speed_rel']*100:.1f}%)")
    print(f"  Wind Direction: {dev['direction']:.1f}°")
    print(f"  Turbulence: {dev['turbulence']*100:.1f} percentage points")
    
    print("\nValidation Results:")
    status = "✅ PASS" if validation['valid'] else "❌ FAIL"
    print(f"  Overall: {status}")
    print(f"  Wind Speed: {'✅' if validation['speed_ok'] else '❌'}")
    print(f"  Wind Direction: {'✅' if validation['direction_ok'] else '❌'}")
    print(f"  Turbulence: {'✅' if validation['turbulence_ok'] else '❌'}")
    
    print(f"\nRecommendation: {validation['recommendation']}")
    
    if validation['recommendation'] == 'NARROW_SEARCH':
        print("  → Use predicted yaw angles with ±1-2° refinement search")
        print("  → Expected computation time: ~3 seconds (625 combinations)")
    elif validation['recommendation'] == 'MODERATE_SEARCH':
        print("  → Use predicted yaw angles with ±2-3° search")
        print("  → Expected computation time: ~8 seconds (2,401 combinations)")
    else:  # FULL_SEARCH
        print("  → Conditions deviated from forecast")
        print("  → Run full optimization with adaptive range")
        print("  → Expected computation time: ~45 seconds (14,641+ combinations)")
    
    print("="*60)


# Example usage
if __name__ == '__main__':
    # Example: Check if actual conditions match forecast
    
    forecast = {
        'wind_speed': 8.5,
        'wind_direction': 270,
        'turbulence_intensity': 0.07
    }
    
    # Scenario 1: Conditions match forecast
    actual_match = {
        'wind_speed': 8.3,      # Within ±1 m/s
        'wind_direction': 268,  # Within ±8°
        'turbulence_intensity': 0.065  # Within ±2%
    }
    
    print("SCENARIO 1: Conditions match forecast")
    validation = is_forecast_valid(forecast, actual_match)
    print_validation_report(forecast, actual_match, validation)
    
    print("\n" * 2)
    
    # Scenario 2: Conditions deviated
    actual_deviated = {
        'wind_speed': 10.2,     # +1.7 m/s (outside tolerance)
        'wind_direction': 285,  # +15° (outside tolerance)
        'turbulence_intensity': 0.09
    }
    
    print("SCENARIO 2: Conditions deviated from forecast")
    validation = is_forecast_valid(forecast, actual_deviated)
    print_validation_report(forecast, actual_deviated, validation)
    
    print("\n" * 2)
    
    # Scenario 3: Calculate search ranges with predictions
    predicted_yaws = [-4, 3, 0, 1]
    confidence = ['high', 'high', 'medium', 'medium']
    
    validation = is_forecast_valid(forecast, actual_match)
    search_ranges = calculate_search_range_from_prediction(
        predicted_yaws, confidence, validation
    )
    
    print("SCENARIO 3: Search ranges from predictions")
    print(f"Predicted yaws: {predicted_yaws}")
    print(f"Confidence: {confidence}")
    print(f"Search ranges:")
    for i, (ymin, ymax) in enumerate(search_ranges):
        print(f"  T{i}: [{ymin}° to {ymax}°] ({ymax-ymin+1} values)")
    total_combinations = np.prod([ymax-ymin+1 for ymin, ymax in search_ranges])
    print(f"  Total combinations: {total_combinations:,}")
