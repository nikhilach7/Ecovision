import { BellRing, Leaf, MapPin } from "lucide-react";

export default function HeaderBar({ location, full, userName, onLogout }) {
  return (
    <header className="mb-6 rounded-2xl bg-white/90 p-5 shadow-panel backdrop-blur">
      <div className="flex flex-col gap-4 md:flex-row md:items-center md:justify-between">
        <div>
          <p className="text-xs uppercase tracking-[0.25em] text-emerald-700">Smart City Command Center</p>
          <h1 className="mt-2 flex items-center gap-2 font-title text-3xl font-bold text-slate-800">
            <Leaf className="text-emerald-600" /> EcoVision AI Dashboard
          </h1>
        </div>

        <div className="flex flex-wrap items-center gap-3 text-sm">
          <span className="inline-flex items-center gap-1 rounded-full bg-slate-100 px-3 py-1.5 text-slate-700">
            User: {userName}
          </span>
          <span className="inline-flex items-center gap-1 rounded-full bg-slate-100 px-3 py-1.5 text-slate-700">
            <MapPin size={14} /> {location}
          </span>
          <span
            className={`inline-flex items-center gap-1 rounded-full px-3 py-1.5 ${
              full ? "bg-rose-100 text-rose-700" : "bg-emerald-100 text-emerald-700"
            }`}
          >
            <BellRing size={14} /> {full ? "Bin Full" : "Normal"}
          </span>
          <button
            onClick={onLogout}
            className="rounded-full bg-slate-800 px-3 py-1.5 text-xs font-semibold uppercase tracking-wider text-white transition hover:bg-slate-900"
          >
            Logout
          </button>
        </div>
      </div>
    </header>
  );
}
