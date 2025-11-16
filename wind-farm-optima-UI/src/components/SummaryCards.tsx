import { Card } from "@/components/ui/card";
import { Zap, TrendingUp, Wind, Activity } from "lucide-react";
import type { FarmSummary } from "@/lib/types";

interface SummaryCardsProps {
  summary: FarmSummary;
}

export function SummaryCards({ summary }: SummaryCardsProps) {
  return (
    <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6">
      <Card className="p-6 bg-gradient-to-br from-card/90 to-card/70 backdrop-blur-sm border-border/50">
        <div className="flex items-start justify-between mb-4">
          <div className="p-3 rounded-lg bg-primary/10 border border-primary/20">
            <Zap className="w-6 h-6 text-primary" />
          </div>
        </div>
        <div className="space-y-1">
          <p className="text-sm text-muted-foreground">Total Power Now</p>
          <p className="text-3xl font-bold text-foreground">
            {summary.total_power_now.toFixed(1)}
            <span className="text-xl text-muted-foreground ml-1">MW</span>
          </p>
        </div>
      </Card>

      <Card className="p-6 bg-gradient-to-br from-card/90 to-card/70 backdrop-blur-sm border-border/50">
        <div className="flex items-start justify-between mb-4">
          <div className="p-3 rounded-lg bg-secondary/10 border border-secondary/20">
            <TrendingUp className="w-6 h-6 text-secondary" />
          </div>
        </div>
        <div className="space-y-1">
          <p className="text-sm text-muted-foreground">Predicted Total</p>
          <p className="text-3xl font-bold text-foreground">
            {summary.predicted_total_power.toFixed(1)}
            <span className="text-xl text-muted-foreground ml-1">MW</span>
          </p>
        </div>
      </Card>

      <Card className="p-6 bg-gradient-to-br from-card/90 to-card/70 backdrop-blur-sm border-border/50">
        <div className="flex items-start justify-between mb-4">
          <div className="p-3 rounded-lg bg-turbine-active/10 border border-turbine-active/20">
            <Activity className="w-6 h-6 text-turbine-active" />
          </div>
        </div>
        <div className="space-y-1">
          <p className="text-sm text-muted-foreground">Wake Steering Uplift</p>
          <p className="text-3xl font-bold text-turbine-active">
            +{summary.wake_steering_uplift.toFixed(1)}
            <span className="text-xl text-muted-foreground ml-1">%</span>
          </p>
        </div>
      </Card>

      <Card className="p-6 bg-gradient-to-br from-card/90 to-card/70 backdrop-blur-sm border-border/50">
        <div className="flex items-start justify-between mb-4">
          <div className="p-3 rounded-lg bg-accent/10 border border-accent/20">
            <Wind className="w-6 h-6 text-accent" />
          </div>
        </div>
        <div className="space-y-1">
          <p className="text-sm text-muted-foreground">Mean Wind Direction</p>
          <p className="text-3xl font-bold text-foreground">
            {summary.mean_wind_direction.toFixed(0)}
            <span className="text-xl text-muted-foreground ml-1">°</span>
          </p>
          <p className="text-xs text-muted-foreground mt-1">
            TI: {summary.turbulence_intensity_range[0].toFixed(2)} - {summary.turbulence_intensity_range[1].toFixed(2)}
          </p>
        </div>
      </Card>
    </div>
  );
}
