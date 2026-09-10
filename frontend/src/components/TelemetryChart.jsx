// TelemetryChart.jsx — rolling line chart for a single metric
import {
  LineChart, Line, XAxis, YAxis, CartesianGrid, Tooltip, ResponsiveContainer
} from 'recharts';

export default function TelemetryChart({ title, data, dataKey, color, unit }) {
  return (
    <div className="border border-slate-800 rounded p-4">
      <p className="text-[10px] tracking-widest text-slate-500 mb-4">{title}</p>
      <ResponsiveContainer width="100%" height={160}>
        <LineChart data={data} margin={{ top: 0, right: 8, left: -20, bottom: 0 }}>
          <CartesianGrid strokeDasharray="3 3" stroke="#1e2d3d" />
          <XAxis
            dataKey="timestamp"
            tick={{ fontSize: 9, fill: '#475569' }}
            interval="preserveStartEnd"
          />
          <YAxis tick={{ fontSize: 9, fill: '#475569' }} />
          <Tooltip
            contentStyle={{ background: '#0f172a', border: '1px solid #1e293b', fontSize: 11 }}
            formatter={(v) => [`${v} ${unit}`, dataKey]}
            labelStyle={{ color: '#94a3b8' }}
          />
          <Line
            type="monotone"
            dataKey={dataKey}
            stroke={color}
            strokeWidth={1.5}
            dot={false}
            isAnimationActive={false}
          />
        </LineChart>
      </ResponsiveContainer>
    </div>
  );
}