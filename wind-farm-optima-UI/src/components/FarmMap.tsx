import { useMemo } from "react";
import { useNavigate } from "react-router-dom";
import Plot from "react-plotly.js";
import type { Turbine } from "@/lib/types";
import { Wind } from "lucide-react";

interface FarmMapProps {
  turbines: Turbine[];
}

export function FarmMap({ turbines }: FarmMapProps) {
  const navigate = useNavigate();

  const plotData = useMemo(() => {
    const x = turbines.map(t => t.x);
    const y = turbines.map(t => t.y);
    const text = turbines.map(t => 
      `Turbine ${t.id}<br>Yaw: ${t.yaw_angle.toFixed(1)}°`
    );

    return [{
      type: 'scatter' as const,
      mode: 'markers+text' as const,
      x,
      y,
      text: turbines.map(t => t.id.toString()),
      textposition: 'top center' as const,
      textfont: {
        size: 12,
        color: 'hsl(180 100% 70%)',
        family: 'monospace',
      },
      marker: {
        size: 30,
        color: 'hsl(180 100% 50%)',
        symbol: 'circle',
        line: {
          color: 'hsl(180 100% 70%)',
          width: 2,
        },
      },
      hovertemplate: text.map(t => `${t}<extra></extra>`),
      customdata: turbines.map(t => t.id),
    }];
  }, [turbines]);

  const layout = {
    paper_bgcolor: 'transparent',
    plot_bgcolor: 'transparent',
    xaxis: {
      title: 'X Position (m)',
      gridcolor: 'hsl(220 25% 25%)',
      zerolinecolor: 'hsl(220 25% 30%)',
      color: 'hsl(180 30% 70%)',
    },
    yaxis: {
      title: 'Y Position (m)',
      gridcolor: 'hsl(220 25% 25%)',
      zerolinecolor: 'hsl(220 25% 30%)',
      color: 'hsl(180 30% 70%)',
    },
    margin: { t: 40, r: 40, b: 60, l: 60 },
    hovermode: 'closest' as const,
    dragmode: 'pan' as const,
    font: {
      color: 'hsl(180 100% 95%)',
    },
  };

  const config = {
    responsive: true,
    displayModeBar: false,
    displaylogo: false,
  };

  return (
    <div className="relative w-full h-full">
      <div className="absolute top-4 left-4 z-10 bg-card/80 backdrop-blur-sm border border-border rounded-lg p-4">
        <div className="flex items-center gap-2 mb-2">
          <Wind className="w-5 h-5 text-primary" />
          <h3 className="font-semibold text-foreground">Wind Farm Layout</h3>
        </div>
        <p className="text-sm text-muted-foreground">
          Click any turbine for detailed analysis
        </p>
      </div>
      
      <Plot
        data={plotData}
        layout={layout}
        config={config}
        style={{ width: '100%', height: '100%' }}
        onClick={(data) => {
          if (data.points && data.points[0]) {
            const turbineId = data.points[0].customdata;
            navigate(`/turbine/${turbineId}`);
          }
        }}
      />
    </div>
  );
}
