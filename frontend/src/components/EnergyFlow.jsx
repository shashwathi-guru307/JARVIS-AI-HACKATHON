export default function EnergyFlow({ latest }) {
  if (!latest) return null;

  const solar   = latest.solar_generation_kw;
  const demand  = latest.current_demand_kw;
  const grid    = latest.grid_power_kw;
  const battery = latest.battery_level;
  const surplus = latest.solar_surplus_kw;
  const batState = latest.battery_state;

  const nodeClass = "border border-slate-700 rounded px-3 py-2 text-center text-[10px] tracking-widest";

  return (
    <div className="border border-slate-800 rounded p-4 space-y-3">
      <p className="text-[10px] tracking-widest text-slate-500">ENERGY FLOW</p>

      <div className="flex flex-col items-center gap-2 text-xs">
        {/* Solar */}
        <div className={`${nodeClass} text-yellow-400 border-yellow-400/30 w-36`}>
          ☀ SOLAR<br />
          <span className="font-bold">{solar} kW</span>
        </div>

        <div className="text-slate-600 text-xs">↓</div>

        {/* Hub */}
        <div className={`${nodeClass} text-cyan-400 border-cyan-400/30 w-36`}>
          ENERGY HUB
        </div>

        <div className="flex gap-6 text-slate-600 text-xs">
          <span>↙</span><span>↓</span><span>↘</span>
        </div>

        {/* Outputs */}
        <div className="flex gap-3 justify-center">
          <div className={`${nodeClass} text-slate-300 w-24`}>
            MACHINE<br />
            <span className="font-bold">{demand} kW</span>
          </div>
          <div className={`${nodeClass} w-24 ${
            batState === "CHARGING" ? "text-emerald-400 border-emerald-400/30" :
            batState === "DISCHARGING" ? "text-red-400 border-red-400/30" :
            "text-slate-400"
          }`}>
            BATTERY<br />
            <span className="font-bold">{battery.toFixed(0)}%</span><br />
            <span className="text-[9px]">{batState}</span>
          </div>
          <div className={`${nodeClass} w-24 ${grid > 5 ? "text-amber-400 border-amber-400/30" : "text-slate-400"}`}>
            GRID<br />
            <span className="font-bold">{grid} kW</span>
          </div>
        </div>

        {surplus > 0 && (
          <p className="text-[10px] text-yellow-300 tracking-wider mt-1">
            ☀ SURPLUS: {surplus} kW available
          </p>
        )}
      </div>
    </div>
  );
}