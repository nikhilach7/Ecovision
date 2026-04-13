export default function StatCard({ title, value, subtitle, icon: Icon, tone = "green" }) {
  const toneStyles = {
    green: "bg-emerald-50 text-emerald-700",
    amber: "bg-amber-50 text-amber-700",
    blue: "bg-cyan-50 text-cyan-700",
  };

  return (
    <div className="animate-rise rounded-2xl bg-white/95 p-5 shadow-panel backdrop-blur">
      <div className="mb-3 flex items-center justify-between">
        <p className="text-sm uppercase tracking-[0.18em] text-slate-500">{title}</p>
        <div className={`rounded-xl p-2 ${toneStyles[tone]}`}>
          <Icon size={18} />
        </div>
      </div>
      <p className="font-title text-3xl font-bold text-slate-800">{value}</p>
      <p className="mt-2 text-sm text-slate-500">{subtitle}</p>
    </div>
  );
}
