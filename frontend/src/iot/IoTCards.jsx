import { AlertTriangle, BarChart3, Gauge, Trash2 } from "lucide-react";
import StatCard from "../components/StatCard";
import { toBinStatus } from "./utils";

export default function IoTCards({ latest, summary, loading, error }) {
  if (loading) {
    return (
      <div className="panel p-4 text-sm text-[var(--text-soft)]">
        Loading IoT summary...
      </div>
    );
  }

  const safeLatest = latest || { fillLevel: 0, binStatus: 0, wasteLevel: 0, distance: 0 };
  const safeSummary = summary || {
    totalWaste: 0,
    fillLevel: 0,
    binStatusRaw: 0,
    binStatusText: "Normal 🟢",
    distance: 0,
    wasteLevelLatest: 0,
    wasteLevelAvg10: 0,
  };
  const hasWarning = Boolean(error);

  return (
    <div className="space-y-3">
      {hasWarning && (
        <div className="panel border border-rose-500/35 p-4 text-sm text-rose-300">
          Live ThingSpeak data is unavailable. Showing last known values.
        </div>
      )}
      {safeLatest.fillLevel > 80 && (
        <div className="flex items-center gap-2 rounded-xl border border-rose-500/35 bg-rose-500/12 px-4 py-3 text-sm text-rose-300">
          <AlertTriangle size={16} />
          <span>Bin is almost full 🚨</span>
        </div>
      )}
      <div className="grid gap-4 md:grid-cols-4">
        <StatCard title="Total Waste" value={`${Math.round(safeSummary.totalWaste * 100) / 100}`} subtitle="ThingSpeak entries" icon={BarChart3} tone="green" />
        <StatCard title="Fill Level" value={`${Math.round(safeLatest.fillLevel)}%`} subtitle="ThingSpeak field1" icon={Gauge} tone="blue" />
        <StatCard title="Bin Status" value={toBinStatus(safeLatest.binStatus)} subtitle="ThingSpeak field2" icon={Trash2} tone="amber" />
        <StatCard title="Waste Level" value={`${Math.round(safeSummary.wasteLevelLatest)}%`} subtitle="ThingSpeak field4" icon={BarChart3} tone="green" />
      </div>
    </div>
  );
}
