import { CartesianGrid, Line, LineChart, ResponsiveContainer, Tooltip, XAxis, YAxis } from "recharts";

export default function TrendLineChart({ trend }) {
  return (
    <div className="rounded-2xl bg-white/95 p-6 shadow-panel">
      <h3 className="mb-4 font-title text-xl font-semibold text-slate-800">Hourly Waste Trend</h3>
      <div className="h-[280px]">
        <ResponsiveContainer width="100%" height="100%">
          <LineChart data={trend}>
            <CartesianGrid strokeDasharray="3 3" stroke="#d8e2d8" />
            <XAxis dataKey="hour" stroke="#71848f" />
            <YAxis allowDecimals={false} stroke="#71848f" />
            <Tooltip />
            <Line type="monotone" dataKey="count" stroke="#198f4a" strokeWidth={3} dot={{ r: 4 }} />
          </LineChart>
        </ResponsiveContainer>
      </div>
    </div>
  );
}
