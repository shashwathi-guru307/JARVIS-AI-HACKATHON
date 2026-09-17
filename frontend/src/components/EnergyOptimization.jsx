import { getStatusColors } from "../utils/statusColors";
import { useState, useEffect } from "react";
import { API_BASE_URL } from "../config";

export default function EnergyOptimization({ optimization, alerts }) {
  const [schedule, setSchedule] = useState([]);

  useEffect(() => {
    async function fetchSchedule() {
      try {
        const res = await fetch(`${API_BASE_URL}/energy/schedule`);
        if (res.ok) { const d = await res.json(); setSchedule(d.schedule ?? []); }
      } catch { /* backend unreachable */ }
    }
    fetchSchedule();
    const id = setInterval(fetchSchedule, 30000);
    return () => clearInterval(id);
  }, []);

  if (!optimization) {
    return (
      <div className="border border-slate-800 rounded p-4 text-slate-600 text-xs tracking-wider">
        ENERGY OPTIMIZATION<br /><br />Awaiting data…
      </div>
    );
  }

  const colors = getStatusColors(
    optimization.optimization_status === "OPTIMAL" ? "NORMAL" :
    optimization.optimization_status === "RECOMMENDED" ? "WARNING" : "CRITICAL"
  );

  const prioritySlots = {
    CRITICAL: "text-red-400", IMPORTANT: "text-amber-400",
    FLEXIBLE: "text-cyan-400", OPTIONAL: "text-slate-400",
  };

  return (
    <div className="border border-slate-800 rounded p-4 space-y-4">
      <p className="text-[10px] tracking-widest text-slate-500">ENERGY OPTIMIZATION</p>

      {/* Current recommendation */}
      <div className={`border ${colors.border} ${colors.bg} rounded p-3 space-y-2`}>
        <p className={`text-[10px] tracking-widest font-bold ${colors.text}`}>
          {optimization.optimization_status}
        </p>
        <p className="text-xs text-slate-300">{optimization.recommended_action}</p>
        {optimization.estimated_saving_kw > 0 && (
          <p className="text-[10px] text-slate-500">
            ESTIMATED SAVING: {optimization.estimated_saving_kw} kW ({optimization.estimated_saving_percentage}%) — SIMULATED
          </p>
        )}
      </div>

      {/* Load schedule */}
      {schedule.length > 0 && (
        <div>
          <p className="text-[10px] tracking-widest text-slate-600 mb-2">OPTIMIZED LOAD SCHEDULE</p>
          <div className="space-y-1.5 max-h-40 overflow-y-auto">
            {schedule.map((slot, i) => (
              <div key={i} className="flex gap-2 items-start text-[10px]">
                <span className="text-slate-600 shrink-0 w-20">{slot.start_time}–{slot.end_time}</span>
                <span className={`shrink-0 ${prioritySlots[slot.priority] ?? "text-slate-400"}`}>{slot.action}</span>
              </div>
            ))}
          </div>
        </div>
      )}

      {/* Energy alert history */}
      {alerts.length > 0 && (
        <div>
          <p className="text-[10px] tracking-widest text-slate-600 mb-1.5">ENERGY ALERT HISTORY</p>
          <div className="space-y-1 max-h-28 overflow-y-auto">
            {alerts.map((a) => {
              const c = getStatusColors(a.status === "OPTIMAL" ? "NORMAL" : a.status === "RECOMMENDED" ? "WARNING" : "CRITICAL");
              return (
                <div key={a.id} className="flex gap-2 text-[10px]">
                  <span className="text-slate-600 shrink-0">{a.time}</span>
                  <span className={`shrink-0 ${c.text}`}>{a.priority}</span>
                  <span className="text-slate-500 truncate">{a.action}</span>
                </div>
              );
            })}
          </div>
        </div>
      )}
    </div>
  );
}