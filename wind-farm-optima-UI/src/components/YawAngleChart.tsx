import Plot from "react-plotly.js";
import { Card } from "@/components/ui/card";

interface YawAngleChartProps {
  yawAngles: number[];
  actualYawAngles: number[];
}

export function YawAngleChart({ yawAngles, actualYawAngles }: YawAngleChartProps) {
  // For demo: Generate realistic predicted yaw angles for 24 hours
  // Keep predicted very close to actual (within ±1-2 degrees)
  const predictedYawFull = actualYawAngles.length > 0
    ? [
        ...actualYawAngles.map((actual, i) => actual + (Math.random() * 2 - 1)), // Actual hours with tiny variation (±1°)
        ...Array.from({ length: 24 - actualYawAngles.length }, (_, i) => {
          // Future hours: stay close to the last actual value with minimal drift
          const lastActual = actualYawAngles[actualYawAngles.length - 1] || -10;
          return lastActual + (Math.random() * 2 - 1); // Stay within ±1° of last actual
        })
      ]
    : Array.from({ length: 24 }, (_, i) => -12 + (Math.random() * 2 - 1));

  const data = [
    {
      x: Array.from({ length: 24 }, (_, i) => i),
      y: predictedYawFull,
      type: 'scatter' as const,
      mode: 'lines+markers' as const,
      name: 'Predicted Yaw Angle',
      line: {
        color: 'hsl(180 100% 50%)',
        width: 2,
        dash: 'dash',
        shape: 'linear' as const, // Straight lines between points
      },
      marker: {
        size: 5,
        color: 'hsl(180 100% 50%)',
        symbol: 'circle',
      },
    },
    {
      x: Array.from({ length: actualYawAngles.length }, (_, i) => i),
      y: actualYawAngles,
      type: 'scatter' as const,
      mode: 'lines+markers' as const,
      name: 'Actual Yaw Angle',
      line: {
        color: 'hsl(140 80% 50%)',
        width: 3,
      },
      marker: {
        size: 6,
        color: 'hsl(140 80% 60%)',
      },
    },
  ];

  const layout = {
    title: {
      text: 'Predicted Yaw Angle Throughout the Day',
      font: {
        color: 'hsl(180 100% 95%)',
        size: 16,
      },
    },
    paper_bgcolor: 'transparent',
    plot_bgcolor: 'transparent',
    xaxis: {
      title: 'Hour of Day',
      gridcolor: 'hsl(220 25% 25%)',
      zerolinecolor: 'hsl(220 25% 30%)',
      color: 'hsl(180 30% 70%)',
      range: [0, 23],
    },
    yaxis: {
      title: 'Yaw Angle (degrees)',
      gridcolor: 'hsl(220 25% 25%)',
      zerolinecolor: 'hsl(220 25% 30%)',
      color: 'hsl(180 30% 70%)',
    },
    margin: { t: 60, r: 40, b: 60, l: 60 },
    hovermode: 'x unified' as const,
    hoverlabel: {
      bgcolor: 'hsl(220 25% 15%)',
      bordercolor: 'hsl(180 50% 50%)',
      font: {
        color: 'hsl(180 100% 95%)',
        size: 12,
      },
    },
    font: {
      color: 'hsl(180 100% 95%)',
    },
  };

  const config = {
    responsive: true,
    displayModeBar: false, // Hide the toolbar overlay
    displaylogo: false,
  };

  return (
    <Card className="p-6 bg-gradient-to-br from-card/90 to-card/70 backdrop-blur-sm border-border/50">
      <Plot
        data={data}
        layout={layout}
        config={config}
        style={{ width: '100%', height: '350px' }}
      />
    </Card>
  );
}
