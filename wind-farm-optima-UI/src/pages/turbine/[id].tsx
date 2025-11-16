import { useParams, useNavigate } from "react-router-dom";
import { ArrowLeft } from "lucide-react";
import { Button } from "@/components/ui/button";
import { TurbineDetailHeader } from "@/components/TurbineDetailHeader";
import { YawAngleChart } from "@/components/YawAngleChart";
import { PowerChart } from "@/components/PowerChart";
import { useTurbineDetail, useTurbineForecast } from "@/lib/api";

export default function TurbineDetail() {
  const { id } = useParams<{ id: string }>();
  const navigate = useNavigate();
  const turbineId = parseInt(id || "1");

  const { data: turbine, isLoading: loadingDetail } = useTurbineDetail(turbineId);
  const { data: forecast, isLoading: loadingForecast } = useTurbineForecast(turbineId);

  if (loadingDetail || loadingForecast || !turbine || !forecast) {
    return (
      <div className="min-h-screen bg-background flex items-center justify-center">
        <div className="text-center space-y-4">
          <div className="w-16 h-16 border-4 border-primary border-t-transparent rounded-full animate-spin mx-auto" />
          <p className="text-muted-foreground">Loading turbine data...</p>
        </div>
      </div>
    );
  }

  return (
    <div className="min-h-screen bg-background">
      {/* Header */}
      <header className="border-b border-border bg-card/50 backdrop-blur-sm sticky top-0 z-50">
        <div className="container mx-auto px-4 py-4 flex items-center justify-between">
          <Button
            variant="ghost"
            onClick={() => navigate("/")}
            className="gap-2"
          >
            <ArrowLeft className="w-4 h-4" />
            Back to Farm
          </Button>
          <h1 className="text-xl font-bold text-foreground absolute left-1/2 transform -translate-x-1/2">
            Turbine {turbineId} Analysis
          </h1>
          <div />
        </div>
      </header>

      {/* Content */}
      <main className="container mx-auto px-4 py-8 space-y-8">
        <TurbineDetailHeader turbine={turbine} />

        <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
          <YawAngleChart 
            yawAngles={forecast.yaw_angles_day} 
            actualYawAngles={forecast.yaw_angles_actual}
          />
          <PowerChart 
            powerOutput={forecast.power_day}
            actualPowerOutput={forecast.power_actual}
          />
        </div>
      </main>
    </div>
  );
}
