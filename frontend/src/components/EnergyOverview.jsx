import { getStatusColors } from "../utils/statusColors";

function Row({ label, value, highlight }) {
  return (
    <div className="flex justify-between items-center py-1.5 border-b border-slate-800 last:border-0">
      <span className="text-xs text-slate-500 tracking-wider">{label}</span>
      <span className={`text-xs font-medium ${highlight ?? "text-slate-300"}`}>{value}</span>
    </div>
  );
}

export default function EnergyOverview({ latest }) {
  if (!latest) {
    return (
      <div className="border border-slate-800 rounded p-4 text-slate-600 text-xs tracking-wider">
        ENERGY INTELLIGENCE<br /><br />Awaiting energy data…
      </div>
    );
  }

  const effColors = getStatusColors(
    latest.efficiency_score >= 75 ? "NORMAL" : latest.efficiency_score >= 50 ? "WARNING" : "CRITICAL"
  );
  const battColors = getStatusColors(
    latest.battery_level > 30 ? "NORMAL" : latest.battery_level > 10 ? "WARNING" : "CRITICAL"
  );
  const wasteColors = getStatusColors(
    latest.wastage?.waste_level === "NONE" || latest.wastage?.waste_level === "LOW" ? "NORMAL" :
    latest.wastage?.waste_level === "MEDIUM" ? "WARNING" : "CRITICAL"
  );

  const statusLabel =
    latest.wastage?.waste_level === "HIGH" ? "WASTEFUL" :
    latest.efficiency_score >= 75 ? "OPTIMIZED" : "SUBOPTIMAL";

  const statusColors = getStatusColors(
    statusLabel === "OPTIMIZED" ? "NORMAL" : statusLabel === "SUBOPTIMAL" ? "WARNING" : "CRITICAL"
  );

  return (
    <div className="border border-slate-800 rounded p-4 space-y-3">
      <div className="flex justify-between items-center">
        <p className="text-[10px] tracking-widest text-slate-500">ENERGY INTELLIGENCE</p>
        <span className={`text-[10px] tracking-widest ${statusColors.text}`}>{statusLabel}</span>
      </div>

      <Row label="CURRENT DEMAND"  value={`${latest.current_demand_kw} kW`} />
      <Row label="SOLAR GENERATION" value={`${latest.solar_generation_kw} kW`} highlight="text-yellow-400" />
      <Row label="GRID POWER"      value={`${latest.grid_power_kw} kW`} />
      <Row
        label="BATTERY"
        value={`${latest.battery_level.toFixed(0)}%  ${latest.battery_state}`}
        highlight={battColors.text}
      />
      <Row label="RENEWABLE SHARE" value={`${latest.renewable_percentage.toFixed(1)}%`} highlight="text-emerald-400" />
      <Row
        label="EFFICIENCY"
        value={`${latest.efficiency_score.toFixed(0)} / 100  ${latest.efficiency_label}`}
        highlight={effColors.text}
      />
      <Row
        label="WASTE LEVEL"
        value={latest.wastage?.waste_level ?? "—"}
        highlight={wasteColors.text}
      />
      {latest.solar_surplus_kw > 0 && (
        <Row label="SOLAR SURPLUS" value={`${latest.solar_surplus_kw} kW`} highlight="text-yellow-300" />
      )}
    </div>
  );
}