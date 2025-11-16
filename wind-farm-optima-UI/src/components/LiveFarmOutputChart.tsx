import Plot from "react-plotly.js";
import { Card } from "@/components/ui/card";
import type { FarmPrediction, FarmActual } from "@/lib/types";

interface LiveFarmOutputChartProps {
  prediction: FarmPrediction;
  actual: FarmActual;
}

export function LiveFarmOutputChart({ prediction, actual }: LiveFarmOutputChartProps) {
  const data = [
    {
      x: prediction.hours,
      y: prediction.predicted_power,
      type: 'scatter' as const,
      mode: 'lines' as const,
      name: 'Predicted',
      line: {
        color: 'hsl(180 100% 50%)',
        width: 2,
        dash: 'dash' as const,
      },
    },
    {
      x: actual.hours,
      y: actual.actual_power,
      type: 'scatter' as const,
      mode: 'lines' as const,
      name: 'Actual',
      line: {
        color: 'hsl(140 80% 50%)',
        width: 3,
      },
    },
  ];

  const layout = {
    title: {
      text: 'Expected Farm Power Output vs Actual',
      font: {
        color: 'hsl(180 100% 95%)',
        size: 18,
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
      title: 'Power Output (MW)',
      gridcolor: 'hsl(220 25% 25%)',
      zerolinecolor: 'hsl(220 25% 30%)',
      color: 'hsl(180 30% 70%)',
    },
    margin: { t: 60, r: 40, b: 60, l: 60 },
    hovermode: 'x unified' as const,
    legend: {
      x: 0.02,
      y: 0.98,
      bgcolor: 'hsl(220 30% 15% / 0.8)',
      bordercolor: 'hsl(220 25% 25%)',
      borderwidth: 1,
      font: {
        color: 'hsl(180 100% 95%)',
      },
    },
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
        style={{ width: '100%', height: '400px' }}
      />
    </Card>
  );
}
