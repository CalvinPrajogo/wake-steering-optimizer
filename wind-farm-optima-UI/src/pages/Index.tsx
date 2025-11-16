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
        <div className="container mx-auto px-4 py-6">
          <div className="flex items-center gap-3">
            <div className="p-3 rounded-lg bg-primary/10 border border-primary/20">
              <Wind className="w-8 h-8 text-primary" />
            </div>
            <div>
              <h1 className="text-3xl font-bold text-foreground">
                Wake-Steering Optimizer
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
        {!loadingPrediction && !loadingActual && prediction && actual && (
          <div className="animate-in fade-in slide-in-from-bottom-4 duration-700 delay-200">
            <LiveFarmOutputChart prediction={prediction} actual={actual} />
          </div>
        )}

        {/* Instructions */}
        <div className="bg-card/60 backdrop-blur-sm border border-border rounded-lg p-8 animate-in fade-in slide-in-from-bottom-4 duration-700 delay-300">
          <h3 className="text-xl font-semibold text-foreground mb-4">
            Getting Started
          </h3>
          <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
            <div>
              <div className="inline-flex items-center justify-center w-10 h-10 rounded-full bg-primary/10 border border-primary/20 mb-3">
                <span className="text-primary font-bold">1</span>
              </div>
              <h4 className="font-semibold text-foreground mb-2">Click Any Turbine</h4>
              <p className="text-sm text-muted-foreground">
                Select a turbine on the map to view detailed analytics and optimization data
              </p>
            </div>
            <div>
              <div className="inline-flex items-center justify-center w-10 h-10 rounded-full bg-secondary/10 border border-secondary/20 mb-3">
                <span className="text-secondary font-bold">2</span>
              </div>
              <h4 className="font-semibold text-foreground mb-2">Monitor Performance</h4>
              <p className="text-sm text-muted-foreground">
                Track real-time power output, yaw angles, and wake effects across the farm
              </p>
            </div>
            <div>
              <div className="inline-flex items-center justify-center w-10 h-10 rounded-full bg-accent/10 border border-accent/20 mb-3">
                <span className="text-accent font-bold">3</span>
              </div>
              <h4 className="font-semibold text-foreground mb-2">Optimize Operations</h4>
              <p className="text-sm text-muted-foreground">
                Use the re-run optimization feature to adjust yaw angles for maximum efficiency
              </p>
            </div>
          </div>
        </div>

        {/* Backend Connection Info */}
        <div className="bg-muted/20 backdrop-blur-sm border border-border rounded-lg p-6">
          <h3 className="text-lg font-semibold text-foreground mb-3">
            Backend Integration
          </h3>
          <p className="text-sm text-muted-foreground mb-4">
            Currently using mock data for demonstration. To connect to your backend at{" "}
            <code className="bg-card px-2 py-1 rounded text-primary">
              https://github.com/CalvinPrajogo/wake-steering-optimizer
            </code>
          </p>
          <ol className="text-sm text-muted-foreground space-y-2 list-decimal list-inside">
            <li>Set the <code className="bg-card px-1 rounded">VITE_API_URL</code> environment variable</li>
            <li>Ensure backend endpoints match the API client in <code className="bg-card px-1 rounded">src/lib/api.ts</code></li>
            <li>Remove mock data and uncomment actual fetch calls</li>
          </ol>
        </div>
      </section>
    </div>
  );
};

export default Index;
