import TrendLineChart from "../components/TrendLineChart";
import WastePieChart from "../components/WastePieChart";
import IoTGraphs from "../iot/IoTGraphs";
import { useIoTData } from "../iot/IoTDataContext";

export default function AnalyticsPage({ dashboard }) {
  const { history, hourlyWasteTrend, loading, error } = useIoTData();
  const trendData = hourlyWasteTrend.length ? hourlyWasteTrend : dashboard.daily_trend;

  return (
    <section className="space-y-5">
      <div className="panel p-5 md:p-6">
        <h3 className="font-title text-2xl font-semibold text-[var(--text-main)]">Waste Analytics</h3>
        <p className="mt-1 text-sm text-[var(--text-soft)]">
          Live distribution and hourly trend insights for segregation and collection planning.
        </p>
      </div>

      <div className="grid gap-5 xl:grid-cols-2">
        <WastePieChart distribution={dashboard.distribution} />
        <TrendLineChart trend={trendData} />
      </div>

      <div className="panel p-5 md:p-6">
        <h3 className="font-title text-xl font-semibold text-[var(--text-main)]">ThingSpeak IoT Trends</h3>
        <p className="mt-1 text-sm text-[var(--text-soft)]">
          Last 20 smart-bin readings for fill level, status, distance, and waste level.
        </p>
      </div>
      <IoTGraphs history={history} loading={loading} error={error} />
    </section>
  );
}
