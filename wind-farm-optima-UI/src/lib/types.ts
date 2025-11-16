// Turbine data types
export interface Turbine {
  id: number;
  x: number;
  y: number;
  name: string;
  status: "operational" | "warning" | "offline";
  yaw_angle: number;
  power: number;
}

export interface TurbineDetail {
  id: number;
  name: string;
  position: [number, number];
  currentPower: number;
  yaw_angle: number;  // Current yaw angle
  currentYaw: number;
  predictedYaw: number;
  wind_speed: number;  // Current wind speed
  windSpeed: number;
  windDirection: number;
  wind_direction: number;  // Current wind direction
  status: string;
  efficiency: number;
  power_output: number;  // Current power output
  power_now: number;  // Power output in MW
  ti: number;  // Turbulence intensity (0-1)
}

export interface TurbineForecast {
  turbineId: number;
  hourly: Array<{
    hour: number;
    predictedYaw: number;
    actualYaw: number;
    power: number;
    windSpeed: number;
    windDirection: number;
  }>;
  // Additional properties for chart components
  yaw_angles_day: number[];
  yaw_angles_actual: number[];
  power_day: number[];
  power_actual: number[];
}

// Farm data types
export interface HourlyData {
  hour: number;
  wind_speed: number;
  wind_direction: number;
  predicted_yaw: number[];
  actual_yaw: number[];
  power_output: number;
  improvement_percent: number;
}

export interface FarmSummary {
  date: string;
  hours_processed: number;
  total_hours: number;
  average_power: number;
  average_improvement: number;
  hourly_data: HourlyData[];
  // Additional properties for UI cards
  total_power_now: number;
  predicted_total_power: number;
  wake_steering_uplift: number;
  mean_wind_direction: number;
  turbulence_intensity_range: [number, number];
}

export interface FarmPrediction {
  hours: number[];
  predicted_power: number[];
}

export interface FarmActual {
  hours: number[];
  actual_power: number[];
}
