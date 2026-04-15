import { Activity, CheckCircle2, Database, Recycle } from "lucide-react";
import StatCard from "../components/StatCard";
import TrendLineChart from "../components/TrendLineChart";
import WastePieChart from "../components/WastePieChart";
import IoTCards from "../iot/IoTCards";
import { useIoTData } from "../iot/IoTDataContext";

export default function HomePage({ dashboard, offlineMode }) {
  const { latest, summary, loading, error } = useIoTData();

  return (
    <section className="space-y-6">
      <div className="panel p-6 md:p-7">
        <div className="grid gap-6 lg:grid-cols-3">
          <div className="lg:col-span-2">
            <p className="text-xs uppercase tracking-[0.26em] text-emerald-300">EcoVision Dashboard</p>
            <h2 className="mt-2 font-title text-2xl font-bold text-[var(--text-main)]">Smart Waste Intelligence Platform</h2>
            <p className="mt-4 text-[var(--text-soft)] leading-relaxed">
              EcoVision AI combines IoT sensors, image classification, and live analytics to help teams monitor waste, improve segregation, and optimize pickup cycles.
            </p>
            <div className="mt-5 flex flex-wrap gap-2">
              <span className="pill">Real-time Monitoring</span>
              <span className="pill">AI Classification</span>
              <span className="pill">Actionable Analytics</span>
            </div>
          </div>

          <div className="soft-card p-4 md:p-5">
            <h3 className="font-title text-base font-semibold text-[var(--text-main)]">Quick Workflow</h3>
            <ul className="mt-3 space-y-3 text-sm text-[var(--text-soft)]">
              <li className="flex items-start gap-2">
                <CheckCircle2 size={16} className="mt-0.5 text-emerald-300" />
                Monitor fill levels from sensors in Monitoring.
              </li>
              <li className="flex items-start gap-2">
                <CheckCircle2 size={16} className="mt-0.5 text-emerald-300" />
                Classify waste images from Classification.
              </li>
              <li className="flex items-start gap-2">
                <CheckCircle2 size={16} className="mt-0.5 text-emerald-300" />
                Track trends and distribution in Analytics.
              </li>
            </ul>
          </div>
        </div>
      </div>

      <div className="grid gap-4 md:grid-cols-4">
        <StatCard
          title="Total Waste"
          value={`${Math.round((summary?.totalWaste ?? 0) * 100) / 100}`}
          subtitle="Sum of last 20 readings"
          icon={Recycle}
          tone="green"
        />

        <StatCard
          title="Fill Level"
          value={loading ? "..." : `${Math.round(Number(latest?.fillLevel) || 0)}%`}
          subtitle="ThingSpeak field1"
          icon={Activity}
          tone="blue"
        />

        <StatCard
          title="Bin Status"
          value={summary?.binStatusText || "Normal 🟢"}
          subtitle="ThingSpeak field2"
          icon={Database}
          tone="amber"
        />

        <StatCard
          title="Waste Level"
          value={`${Math.round(summary?.wasteLevelLatest ?? 0)}%`}
          subtitle="ThingSpeak field4"
          icon={Recycle}
          tone="green"
        />
      </div>
    </section>
  );
}
