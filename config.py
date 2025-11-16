"""
Configuration parameters for wake steering optimization
"""

# Wind Farm Layout Configuration
TURBINE_POSITIONS = [
    (0.0, 0.0),           # Turbine 1
    (-534.64, -643.26),   # Turbine 2  
    (-1139.06, -1221.17), # Turbine 3
    (-1805.23, -1726.18), # Turbine 4
    (-2520.37, -2148.10)  # Turbine 5
]

# Wind Conditions
WIND_DIRECTION = 270  # degrees (wind from west, blowing east)
WIND_SPEED = 8.0      # m/s

# Turbine Specifications
TURBINE_TYPE = "nrel_5MW"  # NREL 5MW reference turbine
ROTOR_DIAMETER = 126       # meters

# Optimization Parameters
YAW_ANGLE_MIN = -5   # degrees
YAW_ANGLE_MAX = 5    # degrees
YAW_ANGLE_STEP = 1   # degrees
N_TURBINES = 5

# Economic Parameters
ELECTRICITY_PRICE = 50  # $/MWh
HOURS_PER_YEAR = 8760   # hours

# FLORIS Model Configuration
WAKE_MODEL = "gauss"  # Options: "gauss", "jensen", "curl", "turbopark"

# Visualization Settings
FLOW_FIELD_RESOLUTION = 100  # Grid resolution for flow field visualization
FIGURE_DPI = 150             # DPI for saved figures
