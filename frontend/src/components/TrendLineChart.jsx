import { CartesianGrid, Line, LineChart, ResponsiveContainer, Tooltip, XAxis, YAxis } from "recharts";

export default function TrendLineChart({ trend }) {
  return (
    <div className="panel p-6">
      <h3 className="mb-4 font-title text-xl font-semibold text-[var(--text-main)]">Hourly Waste Trend</h3>
      <div className="h-[280px]">
        <ResponsiveContainer width="100%" height="100%">
          <LineChart data={trend}>
            <CartesianGrid strokeDasharray="3 3" stroke="rgba(127, 151, 139, 0.26)" />
            <XAxis dataKey="hour" stroke="var(--text-muted)" />
            <YAxis allowDecimals={false} stroke="var(--text-muted)" />
            <Tooltip />
            <Line type="monotone" dataKey="count" stroke="#198f4a" strokeWidth={3} dot={{ r: 4 }} />
          </LineChart>
        </ResponsiveContainer>
      </div>
    </div>
  );
}
