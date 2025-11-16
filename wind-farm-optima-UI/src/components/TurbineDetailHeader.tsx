import { Card } from "@/components/ui/card";
import { Wind, Gauge, Activity, TrendingUp, Fan } from "lucide-react";
import type { TurbineDetail } from "@/lib/types";

interface TurbineDetailHeaderProps {
  turbine: TurbineDetail;
}

export function TurbineDetailHeader({ turbine }: TurbineDetailHeaderProps) {
  return (
    <Card className="p-8 bg-gradient-to-br from-card/90 to-card/70 backdrop-blur-sm border-border/50">
      <div className="grid grid-cols-1 lg:grid-cols-2 gap-8">
        {/* Left: Turbine Visual */}
        <div className="flex items-center justify-center">
          <div className="relative">
            <div className="w-64 h-64 rounded-full bg-gradient-to-br from-primary/20 to-secondary/20 flex items-center justify-center border-4 border-primary/30 animate-pulse">
              <Fan className="w-32 h-32 text-primary animate-spin" style={{ animationDuration: '3s' }} />
            </div>
          </div>
        </div>

        {/* Right: Key Metrics */}
        <div className="space-y-6">
          <div>
            <h1 className="text-4xl font-bold text-foreground mb-2">
              Turbine {turbine.id}
            </h1>
            <p className="text-muted-foreground">Real-time performance monitoring</p>
            <p className="text-sm text-muted-foreground mt-1">
              Position: ({turbine.position[0].toFixed(1)}m, {turbine.position[1].toFixed(1)}m)
            </p>
          </div>

          <div className="grid grid-cols-2 gap-4">
            <div className="bg-muted/20 rounded-lg p-4 border border-border/50">
              <div className="flex items-center gap-2 mb-2">
                <Gauge className="w-4 h-4 text-primary" />
                <p className="text-sm text-muted-foreground">Current Yaw Angle</p>
              </div>
              <p className="text-3xl font-bold text-primary">
                {turbine.yaw_angle.toFixed(1)}°
              </p>
            </div>

            <div className="bg-muted/20 rounded-lg p-4 border border-border/50">
              <div className="flex items-center gap-2 mb-2">
                <Wind className="w-4 h-4 text-secondary" />
                <p className="text-sm text-muted-foreground">Wind Speed</p>
              </div>
              <p className="text-3xl font-bold text-secondary">
                {turbine.wind_speed.toFixed(1)} m/s
              </p>
            </div>

            <div className="bg-muted/20 rounded-lg p-4 border border-border/50">
              <div className="flex items-center gap-2 mb-2">
                <Activity className="w-4 h-4 text-accent" />
                <p className="text-sm text-muted-foreground">Turbulence Intensity</p>
              </div>
              <p className="text-3xl font-bold text-accent">
                {(turbine.ti * 100).toFixed(1)}%
              </p>
            </div>

            <div className="bg-muted/20 rounded-lg p-4 border border-border/50">
              <div className="flex items-center gap-2 mb-2">
                <TrendingUp className="w-4 h-4 text-turbine-active" />
                <p className="text-sm text-muted-foreground">Power Output</p>
              </div>
              <p className="text-3xl font-bold text-turbine-active">
                {turbine.power_now.toFixed(2)} MW
              </p>
            </div>
          </div>
        </div>
      </div>
    </Card>
  );
}
