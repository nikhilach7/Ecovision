import { Cell, Pie, PieChart, ResponsiveContainer, Tooltip } from "recharts";

const COLORS = ["#3ab86f", "#4f8ed7", "#db8c35"];

export default function WastePieChart({ distribution }) {
  const data = [
    { name: "Plastic", value: distribution.plastic || 0 },
    { name: "Metal", value: distribution.metal || 0 },
    { name: "Organic", value: distribution.organic || 0 },
  ];

  return (
    <div className="rounded-2xl bg-white/95 p-6 shadow-panel">
      <h3 className="mb-4 font-title text-xl font-semibold text-slate-800">Waste Distribution</h3>
      <div className="h-[280px]">
        <ResponsiveContainer width="100%" height="100%">
          <PieChart>
            <Pie data={data} dataKey="value" nameKey="name" outerRadius={95} innerRadius={58} paddingAngle={4}>
              {data.map((entry, index) => (
                <Cell key={entry.name} fill={COLORS[index % COLORS.length]} />
              ))}
            </Pie>
            <Tooltip />
          </PieChart>
        </ResponsiveContainer>
      </div>
      <div className="mt-2 grid grid-cols-3 gap-2 text-center text-xs text-slate-600">
        {data.map((item, idx) => (
          <div key={item.name} className="rounded-lg bg-slate-100 px-2 py-1">
            <span className="inline-flex items-center gap-1">
              <span className="h-2 w-2 rounded-full" style={{ backgroundColor: COLORS[idx] }} />
              {item.name}: {item.value}
            </span>
          </div>
        ))}
      </div>
    </div>
  );
}
