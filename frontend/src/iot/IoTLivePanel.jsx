import { AlertTriangle } from "lucide-react";
import { toBinStatus } from "./utils";

function MetricItem({ label, value }) {
  return (
    <div className="soft-card p-4">
      <p className="text-xs uppercase tracking-[0.14em] text-[var(--text-muted)]">{label}</p>
      <p className="mt-2 font-title text-2xl font-semibold text-[var(--text-main)]">{value}</p>
    </div>
  );
}

export default function IoTLivePanel({ latest, loading, error }) {
  if (loading) {
    return <div className="panel p-4 text-sm text-[var(--text-soft)]">Loading live IoT feed...</div>;
  }

  const safeLatest = latest || { fillLevel: 0, binStatus: 0, distance: 0, wasteLevel: 0 };
  const hasWarning = Boolean(error);
  const fill = Math.max(0, Math.min(100, Number(safeLatest.fillLevel) || 0));

  return (
    <div className="panel space-y-4 p-5">
      {hasWarning && (
        <div className="rounded-xl border border-rose-500/35 bg-rose-500/12 px-4 py-3 text-sm text-rose-300">
          Live ThingSpeak data is unavailable. Showing last known values.
        </div>
      )}

      {safeLatest.fillLevel > 80 && (
        <div className="flex items-center gap-2 rounded-xl border border-rose-500/35 bg-rose-500/12 px-4 py-3 text-sm text-rose-300">
          <AlertTriangle size={16} />
          <span>Bin is almost full 🚨</span>
        </div>
      )}

      <div className="soft-card p-4">
        <div className="flex items-center justify-between gap-3">
          <p className="text-xs uppercase tracking-[0.14em] text-[var(--text-muted)]">Latest Fill Level</p>
          <p className="font-title text-sm font-semibold text-[var(--text-main)]">{Math.round(fill)}%</p>
        </div>
        <div className="mt-3 h-2 w-full overflow-hidden rounded-full bg-[var(--soft-panel)]">
          <div
            className="h-full rounded-full bg-emerald-400 transition-[width] duration-700 ease-out"
            style={{ width: `${fill}%` }}
          />
        </div>
      </div>

      <div className="grid gap-4 md:grid-cols-2 xl:grid-cols-4">
        <MetricItem label="Latest Fill Level" value={`${Math.round(fill)}%`} />
        <MetricItem label="Latest Bin Status" value={toBinStatus(safeLatest.binStatus)} />
        <MetricItem label="Latest Distance" value={`${Math.round(Number(safeLatest.distance) || 0)} cm`} />
        <MetricItem label="Latest Waste Level" value={`${Math.round(Number(safeLatest.wasteLevel) || 0)}%`} />
      </div>

      <p className="text-xs text-[var(--text-muted)]">
        Auto-refresh enabled every few seconds.
      </p>
    </div>
  );
}
