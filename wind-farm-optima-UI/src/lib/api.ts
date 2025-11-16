import { useQuery } from "@tanstack/react-query";
import type { Turbine, TurbineDetail, TurbineForecast, HourlyData, FarmSummary, FarmPrediction, FarmActual } from "./types";

// Mock data generators based on your actual data structure
const TURBINE_POSITIONS = [
  [0.0, 0.0],
  [-534.64, -643.26],
  [-1139.06, -1221.17],
  [-1805.23, -1726.18],
  [-2520.37, -2148.10]
];

// Farm Layout Hook
export function useFarmLayout() {
  return useQuery<Turbine[]>({
    queryKey: ["farmLayout"],
    queryFn: async () => {
      // Try to load actual data
      try {
        const response = await fetch('/data/processed/ui_summary.json');
        if (response.ok) {
          const data: FarmSummary = await response.json();
          const latestHour = data.hourly_data[data.hourly_data.length - 1];
          
          // Return turbines with actual yaw angles and power from data
          return TURBINE_POSITIONS.map((pos, idx) => ({
            id: idx,
            x: pos[0],
            y: pos[1],
            name: `T${idx + 1}`,
            status: "operational" as const,
            yaw_angle: latestHour.actual_yaw[idx],
            power: latestHour.power_output / 5, // Approximate per turbine
          }));
        }
      } catch (error) {
        console.log("Using mock layout data");
      }

      // Fallback: Return Block Island Wind Farm layout with mock data
      return TURBINE_POSITIONS.map((pos, idx) => ({
        id: idx,
        x: pos[0],
        y: pos[1],
        name: `T${idx + 1}`,
        status: "operational" as const,
        yaw_angle: 0,
        power: 5000,
      }));
    },
  });
}

// Farm Prediction Hook (day-ahead forecast)
export function useFarmPrediction() {
  return useQuery<FarmPrediction>({
    queryKey: ["farmPrediction"],
    queryFn: async () => {
      // For demo: Show baseline power (no wake steering) varying throughout day
      // Average ~18.5 MW (matching visualization baseline)
      const hours = Array.from({ length: 24 }, (_, i) => i);
      const predicted_power = hours.map((hour) => {
        // Simulate natural wind variation throughout the day
        // Morning: lower winds, Afternoon: peak winds, Evening: moderate
        const timeOfDayFactor = 1 + 0.15 * Math.sin((hour - 6) * Math.PI / 12); // Peak at noon-ish
        const baselinePower = 18.5; // 18,500 kW baseline
        const naturalVariation = (Math.random() - 0.5) * 1.5; // ±0.75 MW random
        return baselinePower * timeOfDayFactor + naturalVariation;
      });
      return { hours, predicted_power };
    },
  });
}

// Farm Actual Hook (real-time optimized)
export function useFarmActual() {
  return useQuery<FarmActual>({
    queryKey: ["farmActual"],
    queryFn: async () => {
      // For demo: Show optimized power (with wake steering) for first 6 hours
      // Average ~19.75 MW (matching visualization optimized: +6.76%)
      const hours = Array.from({ length: 6 }, (_, i) => i);
      const actual_power = hours.map((hour) => {
        // Similar time-of-day pattern but with wake steering uplift
        const timeOfDayFactor = 1 + 0.15 * Math.sin((hour - 6) * Math.PI / 12);
        const optimizedPower = 19.75; // 19,750 kW with wake steering
        const naturalVariation = (Math.random() - 0.5) * 1.5; // ±0.75 MW random
        return optimizedPower * timeOfDayFactor + naturalVariation;
      });
      return { hours, actual_power };
    },
  });
}

// Farm Summary Hook
export function useFarmSummary() {
  return useQuery<FarmSummary>({
    queryKey: ["farmSummary"],
    queryFn: async () => {
      // Try to fetch your actual generated summary
      try {
        const response = await fetch('/data/processed/ui_summary.json');
        if (response.ok) {
          const data = await response.json();
          const latestHour = data.hourly_data[data.hourly_data.length - 1];
          const avgWindDir = data.hourly_data.reduce((sum: number, h: any) => sum + h.wind_direction, 0) / data.hourly_data.length;
          
          // Calculate additional properties from the data
          return {
            ...data,
            total_power_now: latestHour.power_output / 1000, // Convert to MW
            predicted_total_power: data.average_power / 1000, // Convert to MW
            wake_steering_uplift: data.average_improvement,
            mean_wind_direction: avgWindDir,
            turbulence_intensity_range: [0.05, 0.08] as [number, number],
          };
        }
      } catch (error) {
        console.log("Using mock summary data");
      }

      // Fallback mock summary
      return {
        date: new Date().toISOString().split('T')[0],
        hours_processed: 6,
        total_hours: 24,
        average_power: 28500,
        average_improvement: 3.8,
        hourly_data: [],
        total_power_now: 28.5,
        predicted_total_power: 29.0,
        wake_steering_uplift: 3.8,
        mean_wind_direction: 310,
        turbulence_intensity_range: [0.05, 0.08],
      };
    },
  });
}

// Turbine Detail Hook
export function useTurbineDetail(turbineId: number) {
  return useQuery<TurbineDetail>({
    queryKey: ["turbineDetail", turbineId],
    queryFn: async () => {      
      // Try to get latest data from summary
      try {
        const response = await fetch('/data/processed/ui_summary.json');
        if (response.ok) {
          const data: FarmSummary = await response.json();
          const latestHour = data.hourly_data[data.hourly_data.length - 1];
          
          const powerPerTurbine = latestHour.power_output / 5;
          
          return {
            id: turbineId,
            name: `Turbine ${turbineId + 1}`,
            position: TURBINE_POSITIONS[turbineId] as [number, number],
            currentPower: powerPerTurbine,
            yaw_angle: latestHour.actual_yaw[turbineId],
            currentYaw: latestHour.actual_yaw[turbineId],
            predictedYaw: latestHour.predicted_yaw[turbineId],
            wind_speed: latestHour.wind_speed,
            windSpeed: latestHour.wind_speed,
            windDirection: latestHour.wind_direction,
            wind_direction: latestHour.wind_direction,
            status: "Operational",
            efficiency: 85 + Math.random() * 10,
            power_output: powerPerTurbine,
            power_now: powerPerTurbine / 1000, // Convert to MW
            ti: 0.06, // Typical turbulence intensity
          };
        }
      } catch (error) {
        console.log("Using mock turbine detail");
      }

      // Fallback mock
      const mockPower = 4000 + Math.random() * 2000;
      return {
        id: turbineId,
        name: `Turbine ${turbineId + 1}`,
        position: TURBINE_POSITIONS[turbineId] as [number, number],
        currentPower: mockPower,
        yaw_angle: Math.floor(-20 + Math.random() * 40),
        currentYaw: Math.floor(-20 + Math.random() * 40),
        predictedYaw: Math.floor(-20 + Math.random() * 40),
        wind_speed: 8 + Math.random() * 4,
        windSpeed: 8 + Math.random() * 4,
        windDirection: 310 + Math.random() * 10,
        wind_direction: 310 + Math.random() * 10,
        status: "Operational",
        efficiency: 85 + Math.random() * 10,
        power_output: mockPower,
        power_now: mockPower / 1000, // Convert to MW
        ti: 0.06,
      };
    },
  });
}

// Turbine Forecast Hook
export function useTurbineForecast(turbineId: number) {
  return useQuery<TurbineForecast>({
    queryKey: ["turbineForecast", turbineId],
    queryFn: async () => {
      // Try to get forecast data
      try {
        const response = await fetch('/data/processed/ui_summary.json');
        if (response.ok) {
          const data: FarmSummary = await response.json();
          
          const hourlyData = data.hourly_data.map(hour => ({
            hour: hour.hour,
            predictedYaw: hour.predicted_yaw[turbineId],
            actualYaw: hour.actual_yaw[turbineId],
            power: hour.power_output / 5, // Approximate per turbine
            windSpeed: hour.wind_speed,
            windDirection: hour.wind_direction,
          }));

          return {
            turbineId,
            hourly: hourlyData,
            yaw_angles_day: data.hourly_data.map(h => h.predicted_yaw[turbineId]),
            yaw_angles_actual: data.hourly_data.map(h => h.actual_yaw[turbineId]),
            power_day: data.hourly_data.map(h => h.power_output / 5),
            power_actual: data.hourly_data.slice(0, data.hours_processed).map(h => h.power_output / 5),
          };
        }
      } catch (error) {
        console.log("Using mock turbine forecast");
      }

      // Fallback mock
      const mockHourly = Array.from({ length: 24 }, (_, hour) => ({
        hour,
        predictedYaw: Math.floor(-20 + Math.random() * 40),
        actualYaw: hour < 6 ? Math.floor(-18 + Math.random() * 36) : 0,
        power: 4000 + Math.random() * 2000,
        windSpeed: 8 + Math.random() * 4,
        windDirection: 310 + Math.random() * 10,
      }));

      return {
        turbineId,
        hourly: mockHourly,
        yaw_angles_day: mockHourly.map(h => h.predictedYaw),
        yaw_angles_actual: mockHourly.slice(0, 6).map(h => h.actualYaw),
        power_day: mockHourly.map(h => h.power),
        power_actual: mockHourly.slice(0, 6).map(h => h.power),
      };
    },
  });
}
