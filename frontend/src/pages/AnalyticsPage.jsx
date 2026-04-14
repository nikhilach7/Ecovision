import TrendLineChart from "../components/TrendLineChart";
import WastePieChart from "../components/WastePieChart";

export default function AnalyticsPage({ dashboard }) {
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
        <TrendLineChart trend={dashboard.daily_trend} />
      </div>
    </section>
  );
}
