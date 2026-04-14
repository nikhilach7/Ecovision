import { ChevronDown, Circle, Leaf, Sun, Moon } from "lucide-react";
import { useEffect, useRef, useState } from "react";

const NAV_ITEMS = [
  { id: "home", label: "Home" },
  { id: "monitoring", label: "Monitoring" },
  { id: "classification", label: "Classification" },
  { id: "analytics", label: "Analytics" },
];

export default function TopNavbar({ userName, offlineMode, location, onLogout, onThemeToggle, theme, activePage, onNavigate }) {
  const [menuOpen, setMenuOpen] = useState(false);
  const menuRef = useRef(null);

  useEffect(() => {
    const handleClickOutside = (event) => {
      if (menuRef.current && !menuRef.current.contains(event.target)) {
        setMenuOpen(false);
      }
    };

    document.addEventListener("mousedown", handleClickOutside);
    return () => document.removeEventListener("mousedown", handleClickOutside);
  }, []);

  return (
    <header className="sticky top-0 z-30 border-b border-[var(--line)] bg-[var(--topbar-bg)]/92 px-4 py-3 backdrop-blur md:px-6">
      <div className="mx-auto flex w-full max-w-[1400px] items-center justify-between gap-3">
        <div className="min-w-0">
          <h2 className="truncate font-title text-lg font-semibold text-[var(--text-main)]">
            <span className="inline-flex items-center gap-2">
              <Leaf size={18} className="text-emerald-300" />
              EcoVision AI
            </span>
          </h2>
          <p className="truncate text-xs text-[var(--text-muted)]">Smart Waste Intelligence Platform</p>
        </div>

        <div className="hidden items-center gap-2 lg:flex">
          {NAV_ITEMS.map((item) => {
            const isActive = activePage === item.id;
            return (
              <button
                key={item.id}
                type="button"
                onClick={() => onNavigate(item.id)}
                className={`rounded-full px-3.5 py-1.5 text-sm font-medium transition ${
                  isActive
                    ? "border border-emerald-300/35 bg-emerald-500/18 text-[var(--text-main)]"
                    : "border border-transparent bg-transparent text-[var(--text-soft)] hover:border-[var(--line)] hover:bg-[var(--soft-panel)] hover:text-[var(--text-main)]"
                }`}
              >
                {item.label}
              </button>
            );
          })}
        </div>

        <div className="flex items-center gap-2.5 md:gap-3">
          <div className={`hidden items-center gap-2 rounded-full border border-[var(--line)] px-3 py-1.5 text-xs md:inline-flex ${offlineMode ? "bg-amber-500/12 text-amber-300" : "bg-emerald-500/12 text-emerald-300"}`}>
            <Circle size={10} className="fill-current" />
            {offlineMode ? "Offline" : "Live"}
          </div>

          <button
            type="button"
            onClick={onThemeToggle}
            className="inline-flex h-10 w-10 items-center justify-center rounded-full border border-[var(--line)] bg-[var(--soft-panel)] text-[var(--text-main)] transition hover:bg-[var(--card-hover)]"
            aria-label="Toggle theme"
          >
            {theme === "dark" ? <Sun size={18} /> : <Moon size={18} />}
          </button>

          <div className="relative" ref={menuRef}>
            <button
              type="button"
              onClick={() => setMenuOpen((prev) => !prev)}
              className="inline-flex items-center gap-2 rounded-full border border-[var(--line)] bg-[var(--soft-panel)] px-2.5 py-1.5 text-sm text-[var(--text-main)] transition hover:bg-[var(--card-hover)]"
            >
              <span className="inline-flex h-8 w-8 items-center justify-center rounded-full bg-gradient-to-br from-emerald-400 to-teal-500 text-xs font-semibold text-slate-900">
                {(userName || "U").slice(0, 1).toUpperCase()}
              </span>
              <span className="hidden max-w-28 truncate md:block">{userName}</span>
              <ChevronDown size={14} className={`transition ${menuOpen ? "rotate-180" : ""}`} />
            </button>

            {menuOpen && (
              <div className="absolute right-0 top-12 w-44 rounded-xl border border-[var(--line)] bg-[var(--panel)] p-1.5 shadow-xl">
                <button type="button" className="menu-item">Profile</button>
                <button type="button" className="menu-item">Settings</button>
                <button
                  type="button"
                  className="menu-item text-rose-300 hover:bg-rose-500/15"
                  onClick={onLogout}
                >
                  Logout
                </button>
              </div>
            )}
          </div>
        </div>
      </div>

      <div className="mx-auto mt-3 flex w-full max-w-[1400px] items-center gap-2 overflow-x-auto pb-1 lg:hidden">
        {NAV_ITEMS.map((item) => {
          const isActive = activePage === item.id;
          return (
            <button
              key={item.id}
              type="button"
              onClick={() => onNavigate(item.id)}
              className={`rounded-lg px-3 py-1.5 text-sm font-medium transition ${
                isActive
                  ? "border border-emerald-300/35 bg-emerald-500/18 text-[var(--text-main)]"
                  : "border border-[var(--line)] bg-[var(--soft-panel)] text-[var(--text-soft)] hover:bg-[var(--card-hover)] hover:text-[var(--text-main)]"
              }`}
            >
              {item.label}
            </button>
          );
        })}
      </div>
    </header>
  );
}
