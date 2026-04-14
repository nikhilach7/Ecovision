export default function StatCard({ title, value, subtitle, icon: Icon, tone = "green" }) {
  const toneStyles = {
    green: "bg-emerald-500/15 text-emerald-400",
    amber: "bg-amber-500/15 text-amber-300",
    blue: "bg-teal-500/15 text-teal-300",
  };

  return (
    <div className="panel animate-rise p-5">
      <div className="mb-3 flex items-center justify-between">
        <p className="text-sm uppercase tracking-[0.18em] text-[var(--text-muted)]">{title}</p>
        <div className={`rounded-xl p-2 ${toneStyles[tone]}`}>
          <Icon size={18} />
        </div>
      </div>
      <p className="font-title text-3xl font-bold text-[var(--text-main)]">{value}</p>
      <p className="mt-2 text-sm text-[var(--text-soft)]">{subtitle}</p>
    </div>
  );
}
