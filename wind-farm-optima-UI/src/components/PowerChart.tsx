import Plot from "react-plotly.js";
import { Card } from "@/components/ui/card";

interface PowerChartProps {
  powerOutput: number[];
  actualPowerOutput: number[];
}

export function PowerChart({ powerOutput, actualPowerOutput }: PowerChartProps) {
  // Only show actual power output
  const data = [
    {
      x: Array.from({ length: actualPowerOutput.length }, (_, i) => i),
      y: actualPowerOutput.map(p => p / 1000), // Convert to MW
      type: 'scatter' as const,
      mode: 'lines+markers' as const,
      name: 'Actual Power',
      fill: 'tozeroy' as const,
      line: {
        color: 'hsl(140 80% 50%)',
        width: 3,
      },
      marker: {
        size: 6,
        color: 'hsl(140 80% 60%)',
      },
      fillcolor: 'hsl(140 80% 50% / 0.2)',
      hovertemplate: '<b>Hour %{x}</b><br>Power: %{y:.2f} MW<extra></extra>',
    },
  ];

  const layout = {
    title: {
      text: 'Turbine Energy Output',
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
      title: {
        text: 'Power Output (MW)',
        font: {
          color: 'hsl(180 100% 95%)',
          size: 14,
        },
      },
      gridcolor: 'hsl(220 25% 25%)',
      zerolinecolor: 'hsl(220 25% 30%)',
      color: 'hsl(180 30% 70%)',
    },
    margin: { t: 60, r: 40, b: 60, l: 60 },
    hovermode: 'x unified' as const,
    hoverlabel: {
      bgcolor: 'hsl(220 25% 15%)',
      bordercolor: 'hsl(140 80% 50%)',
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
