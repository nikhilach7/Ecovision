import { CartesianGrid, Legend, Line, LineChart, ResponsiveContainer, Tooltip, XAxis, YAxis } from "recharts";

function MetricChart({ title, data, dataKey, stroke }) {
  return (
    <div className="panel p-5">
      <h4 className="mb-3 font-title text-lg font-semibold text-[var(--text-main)]">{title}</h4>
      <div className="h-[240px]">
        <ResponsiveContainer width="100%" height="100%">
          <LineChart data={data}>
            <CartesianGrid strokeDasharray="3 3" stroke="rgba(127, 151, 139, 0.26)" />
            <XAxis dataKey="createdAt" minTickGap={24} stroke="var(--text-muted)" />
            <YAxis stroke="var(--text-muted)" />
            <Tooltip />
            <Legend />
            <Line type="monotone" dataKey={dataKey} stroke={stroke} strokeWidth={2.5} dot={{ r: 2 }} />
          </LineChart>
        </ResponsiveContainer>
      </div>
    </div>
  );
}

export default function IoTGraphs({ history, loading, error }) {
  if (loading) {
    return <div className="panel p-4 text-sm text-[var(--text-soft)]">Loading IoT graph data...</div>;
  }
  if (error) {
    return <div className="panel border border-rose-500/35 p-4 text-sm text-rose-300">Unable to load ThingSpeak history.</div>;
  }
  if (!history?.length) {
    return <div className="panel p-4 text-sm text-[var(--text-soft)]">No ThingSpeak history available yet.</div>;
  }
  return (
    <div className="grid gap-5 xl:grid-cols-2">
      <MetricChart title="Fill Level Trend (%)" data={history} dataKey="fillLevel" stroke="#22c55e" />
      <MetricChart title="Bin Status Trend (0/1)" data={history} dataKey="binStatus" stroke="#f59e0b" />
      <MetricChart title="Distance Trend (cm)" data={history} dataKey="distance" stroke="#06b6d4" />
      <MetricChart title="Waste Level Trend (%)" data={history} dataKey="wasteLevel" stroke="#8b5cf6" />
    </div>
  );
}
