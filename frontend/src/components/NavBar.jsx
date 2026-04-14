import { BellRing, Leaf, LogOut, MapPin, Moon, Sun } from "lucide-react";

const NAV_ITEMS = [
  { id: "home", label: "Home" },
  { id: "monitoring", label: "Monitoring" },
  { id: "classification", label: "Classification" },
];

export default function NavBar({
  activePage,
  onNavigate,
  userName,
  location,
  isBinFull,
  onLogout,
  theme,
  onToggleTheme,
}) {
  return (
    <header className="panel mb-6 px-5 py-4 md:px-6">
      <div className="flex flex-col gap-4 lg:flex-row lg:items-center lg:justify-between">
        <div className="flex flex-wrap items-center gap-3">
          <div className="inline-flex h-11 w-11 items-center justify-center rounded-2xl bg-emerald-500/15 text-emerald-400">
            <Leaf size={22} />
          </div>
          <div>
            <p className="text-xs uppercase tracking-[0.28em] text-[var(--text-muted)]">Smart City Command Center</p>
            <h1 className="font-title text-3xl font-bold text-[var(--text-main)]">EcoVision AI</h1>
          </div>
        </div>

        <nav className="flex flex-wrap items-center gap-2">
          {NAV_ITEMS.map((item) => (
            <button
              key={item.id}
              type="button"
              onClick={() => onNavigate(item.id)}
              className={`rounded-full px-4 py-2 text-sm font-medium transition ${
                activePage === item.id
                  ? "bg-emerald-500 text-white shadow-lg shadow-emerald-500/30"
                  : "bg-[var(--pill-bg)] text-[var(--text-main)] hover:bg-[var(--pill-hover)]"
              }`}
            >
              {item.label}
            </button>
          ))}
        </nav>

        <div className="flex flex-wrap items-center gap-2 text-sm">
          <span className="pill">User: {userName}</span>
          <span className="pill">
            <MapPin size={14} /> {location}
          </span>
          <span className={`pill ${isBinFull ? "pill-alert" : "pill-ok"}`}>
            <BellRing size={14} /> {isBinFull ? "Bin Full" : "Normal"}
          </span>
          <button
            type="button"
            onClick={onToggleTheme}
            className="pill border border-[var(--line)] hover:bg-[var(--pill-hover)]"
            aria-label="Toggle theme"
            title="Toggle theme"
          >
            {theme === "dark" ? <Sun size={16} /> : <Moon size={16} />}
          </button>
          <button
            type="button"
            onClick={onLogout}
            className="inline-flex items-center gap-1 rounded-full bg-slate-900 px-3 py-1.5 text-xs font-semibold uppercase tracking-wider text-white transition hover:bg-black"
          >
            <LogOut size={14} /> Logout
          </button>
        </div>
      </div>
    </header>
  );
}
