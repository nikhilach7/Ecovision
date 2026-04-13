import { AlertTriangle, MapPin } from "lucide-react";
import { percentage } from "../utils/format";

export default function FillLevelCard({ fill, location }) {
  const isFull = fill > 90;

  return (
    <div className="rounded-2xl bg-white/95 p-6 shadow-panel">
      <div className="mb-4 flex items-center justify-between">
        <h3 className="font-title text-xl font-semibold text-slate-800">Bin Fill Level</h3>
        <div className="flex items-center gap-1 text-sm text-slate-500">
          <MapPin size={15} /> {location}
        </div>
      </div>

      <div className="h-4 overflow-hidden rounded-full bg-slate-200">
        <div
          className={`h-full rounded-full transition-all duration-700 ${
            isFull ? "bg-rose-500" : "bg-emerald-500"
          }`}
          style={{ width: `${Math.min(100, fill)}%` }}
        />
      </div>

      <div className="mt-3 flex items-center justify-between">
        <span className="text-sm text-slate-500">Current Level</span>
        <span className="font-title text-2xl font-semibold text-slate-800">{percentage(fill)}</span>
      </div>

      {isFull && (
        <div className="mt-4 flex items-center gap-2 rounded-xl border border-rose-200 bg-rose-50 p-3 text-rose-700">
          <AlertTriangle size={18} />
          <p className="text-sm font-medium">Bin Full: Immediate collection required.</p>
        </div>
      )}
    </div>
  );
}
