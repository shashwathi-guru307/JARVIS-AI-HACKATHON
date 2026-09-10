// DegradationChart.jsx — health score over time
import {
  LineChart, Line, XAxis, YAxis, CartesianGrid, Tooltip, ResponsiveContainer, ReferenceLine
} from "recharts";

export default function DegradationChart({ history }) {
  if (!history || history.length === 0) {
    return (
      <div className="border border-slate-800 rounded p-4 flex items-center justify-center h-36 text-slate-600 text-xs tracking-wider">
        AWAITING HEALTH HISTORY…
      </div>
    );
  }

  const data = history.slice(-60).map((h) => ({
    time:   new Date(h.timestamp).toLocaleTimeString(),
    health: Math.round(h.health_score),
    risk:   Math.round(h.failure_risk * 100),
  }));

  return (
    <div className="border border-slate-800 rounded p-4">
      <p className="text-[10px] tracking-widest text-slate-500 mb-3">HEALTH TREND</p>
      <ResponsiveContainer width="100%" height={140}>
        <LineChart data={data} margin={{ top: 0, right: 8, left: -20, bottom: 0 }}>
          <CartesianGrid strokeDasharray="3 3" stroke="#1e2d3d" />
          <XAxis dataKey="time" tick={{ fontSize: 9, fill: "#475569" }} interval="preserveStartEnd" />
          <YAxis domain={[0, 100]} tick={{ fontSize: 9, fill: "#475569" }} />
          <Tooltip
            contentStyle={{ background: "#0f172a", border: "1px solid #1e293b", fontSize: 11 }}
            labelStyle={{ color: "#94a3b8" }}
          />
          <ReferenceLine y={50} stroke="#f59e0b" strokeDasharray="4 4" opacity={0.5} />
          <ReferenceLine y={25} stroke="#ef4444" strokeDasharray="4 4" opacity={0.5} />
          <Line type="monotone" dataKey="health" stroke="#22d3ee" strokeWidth={1.5} dot={false} isAnimationActive={false} name="Health" />
        </LineChart>
      </ResponsiveContainer>
    </div>
  );
}