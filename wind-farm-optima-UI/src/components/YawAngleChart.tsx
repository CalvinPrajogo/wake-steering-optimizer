import Plot from "react-plotly.js";
import { Card } from "@/components/ui/card";

interface YawAngleChartProps {
  yawAngles: number[];
  actualYawAngles: number[];
}

export function YawAngleChart({ yawAngles, actualYawAngles }: YawAngleChartProps) {
  const data = [
    {
      x: Array.from({ length: 24 }, (_, i) => i),
      y: yawAngles,
      type: 'scatter' as const,
      mode: 'lines' as const,
      name: 'Predicted Yaw Angle',
      line: {
        color: 'hsl(180 100% 50%)',
        width: 2,
        dash: 'dash',
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
    font: {
      color: 'hsl(180 100% 95%)',
    },
  };

  const config = {
    responsive: true,
    displayModeBar: true,
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
