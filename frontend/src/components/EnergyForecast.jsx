import { LineChart, Line, XAxis, YAxis, CartesianGrid, Tooltip, ResponsiveContainer, ReferenceLine } from "recharts";
import { useState, useEffect } from "react";

export default function EnergyForecast({ history }) {
  const [forecast, setForecast] = useState(null);

  useEffect(() => {
    async function fetchForecast() {
      try {
        const res = await fetch("http://localhost:8000/energy/forecast");
        if (res.ok) setForecast(await res.json());
      } catch { /* backend unreachable */ }
    }
    fetchForecast();
    const id = setInterval(fetchForecast, 10000);
    return () => clearInterval(id);
  }, []);

  if (!history || history.length === 0) {
    return (
      <div className="border border-slate-800 rounded p-4 flex items-center justify-center h-40 text-slate-600 text-xs tracking-wider">
        AWAITING ENERGY HISTORY…
      </div>
    );
  }

  const chartData = history.slice(-40).map((h) => ({ time: h.time, demand: h.demand, solar: h.solar }));

  // Append forecast points
  if (forecast && !forecast.message) {
    chartData.push({ time: "+5m",  demand: forecast.forecast_5min_kw,  solar: null, predicted: true });
    chartData.push({ time: "+10m", demand: forecast.forecast_10min_kw, solar: null, predicted: true });
    chartData.push({ time: "+15m", demand: forecast.forecast_15min_kw, solar: null, predicted: true });
  }

  return (
    <div className="border border-slate-800 rounded p-4 space-y-2">
      <div className="flex justify-between items-center">
        <p className="text-[10px] tracking-widest text-slate-500">ENERGY FORECAST</p>
        {forecast && !forecast.message && (
          <span className="text-[10px] text-slate-600 tracking-wider">
            TREND: {forecast.trend}  CONF: {Math.round(forecast.confidence * 100)}%
          </span>
        )}
      </div>
      <ResponsiveContainer width="100%" height={140}>
        <LineChart data={chartData} margin={{ top: 0, right: 8, left: -20, bottom: 0 }}>
          <CartesianGrid strokeDasharray="3 3" stroke="#1e2d3d" />
          <XAxis dataKey="time" tick={{ fontSize: 9, fill: "#475569" }} interval="preserveStartEnd" />
          <YAxis tick={{ fontSize: 9, fill: "#475569" }} />
          <Tooltip
            contentStyle={{ background: "#0f172a", border: "1px solid #1e293b", fontSize: 11 }}
            labelStyle={{ color: "#94a3b8" }}
          />
          <Line type="monotone" dataKey="demand" stroke="#22d3ee" strokeWidth={1.5} dot={false} isAnimationActive={false} name="Demand kW" />
          <Line type="monotone" dataKey="solar"  stroke="#fbbf24" strokeWidth={1.5} dot={false} isAnimationActive={false} name="Solar kW" />
        </LineChart>
      </ResponsiveContainer>
      {forecast && !forecast.message && (
        <div className="grid grid-cols-3 gap-2 text-[10px] text-center">
          {[["5 min", forecast.forecast_5min_kw], ["10 min", forecast.forecast_10min_kw], ["15 min", forecast.forecast_15min_kw]].map(([label, val]) => (
            <div key={label} className="border border-slate-800 rounded py-1">
              <p className="text-slate-600">{label}</p>
              <p className="text-cyan-400 font-bold">{val} kW</p>
            </div>
          ))}
        </div>
      )}
    </div>
  );
}
