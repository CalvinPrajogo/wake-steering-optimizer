import { FarmMap } from "@/components/FarmMap";
import { SummaryCards } from "@/components/SummaryCards";
import { LiveFarmOutputChart } from "@/components/LiveFarmOutputChart";
import { useFarmLayout, useFarmPrediction, useFarmActual, useFarmSummary } from "@/lib/api";
import { Wind } from "lucide-react";

const Index = () => {
  const { data: turbines, isLoading: loadingLayout } = useFarmLayout();
  const { data: prediction, isLoading: loadingPrediction } = useFarmPrediction();
  const { data: actual, isLoading: loadingActual } = useFarmActual();
  const { data: summary, isLoading: loadingSummary } = useFarmSummary();

  if (loadingLayout || !turbines) {
    return (
      <div className="min-h-screen bg-background flex items-center justify-center">
        <div className="text-center space-y-4">
          <div className="w-16 h-16 border-4 border-primary border-t-transparent rounded-full animate-spin mx-auto" />
          <p className="text-muted-foreground">Loading wind farm data...</p>
        </div>
      </div>
    );
  }

  return (
    <div className="min-h-screen bg-background">
      {/* Hero Header */}
      <header className="border-b border-border bg-gradient-to-r from-card/80 to-card/60 backdrop-blur-sm">
        <div className="px-4 py-6">
          <div className="flex items-center gap-3">
            <img 
              src="/assets/turbine-logo.svg" 
              alt="Wind Turbine Logo" 
              className="w-12 h-12"
            />
            <div>
              <h1 className="text-3xl font-bold text-foreground">
                Zephyr Dashboard
              </h1>
              <p className="text-muted-foreground">
                Real-time wind farm performance monitoring and optimization
              </p>
            </div>
          </div>
        </div>
      </header>

      {/* Main Map Section */}
      <section className="h-[70vh] bg-gradient-to-b from-background to-card/20">
        <FarmMap turbines={turbines} />
      </section>

      {/* Dashboard Section */}
      <section className="container mx-auto px-4 py-12 space-y-12">
        {/* Summary Cards */}
        {!loadingSummary && summary && (
          <div className="animate-in fade-in slide-in-from-bottom-4 duration-700">
            <h2 className="text-2xl font-bold text-foreground mb-6">
              Farm Performance Overview
            </h2>
            <SummaryCards summary={summary} />
          </div>
        )}

        {/* Live Chart */}
        {!loadingPrediction && !loadingActual && prediction && actual && 
         prediction.predicted_power?.length > 0 && actual.actual_power?.length > 0 && (
          <div className="animate-in fade-in slide-in-from-bottom-4 duration-700 delay-200">
            <LiveFarmOutputChart prediction={prediction} actual={actual} />
          </div>
        )}
      </section>
    </div>
  );
};

export default Index;
