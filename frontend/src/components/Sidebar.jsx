import { Activity, BarChart3, Home, Leaf, ScanLine } from "lucide-react";

const NAV_ITEMS = [
  { id: "home", label: "Home", icon: Home },
  { id: "monitoring", label: "Monitoring", icon: Activity },
  { id: "classification", label: "Classification", icon: ScanLine },
  { id: "analytics", label: "Analytics", icon: BarChart3 },
];

export default function Sidebar({ activePage, onNavigate, mobile = false }) {
  return (
    <aside
      className={`${mobile ? "flex" : "hidden lg:flex"} w-72 shrink-0 flex-col border-r border-[var(--line)] bg-[var(--sidebar-bg)] px-5 py-6`}
    >
      <div className="mb-8 flex items-center gap-3 px-3">
        <div className="inline-flex h-10 w-10 items-center justify-center rounded-xl bg-teal-500/15 text-teal-300">
          <Leaf size={20} />
        </div>
        <div>
          <p className="text-[10px] uppercase tracking-[0.28em] text-[var(--text-muted)]">Smart City</p>
          <h1 className="font-title text-xl font-semibold text-[var(--text-main)]">EcoVision AI</h1>
        </div>
      </div>

      <nav className="space-y-1.5">
        {NAV_ITEMS.map((item) => {
          const Icon = item.icon;
          const active = activePage === item.id;
          return (
            <button
              key={item.id}
              type="button"
              onClick={() => onNavigate(item.id)}
              className={`group flex w-full items-center gap-3 rounded-lg px-3 py-2.5 text-left text-sm transition-all duration-200 ${
                active
                  ? "bg-gradient-to-r from-emerald-500/25 to-teal-500/20 text-white shadow-sm"
                  : "text-[var(--text-soft)] hover:bg-[var(--soft-panel)] hover:text-[var(--text-main)]"
              }`}
            >
              <span
                className={`inline-flex h-8 w-8 items-center justify-center rounded-lg transition ${
                  active ? "bg-emerald-400/25 text-emerald-200" : "bg-black/20 text-[var(--text-muted)] group-hover:text-emerald-200"
                }`}
              >
                <Icon size={16} />
              </span>
              <span className="font-medium">{item.label}</span>
            </button>
          );
        })}
      </nav>
    </aside>
  );
}
