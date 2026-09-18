import { getStatusColors } from "../utils/statusColors";
import { triggerEmergency, resetEmergency } from "../services/safety";
import { useState } from "react";

function Row({ label, value, status }) {
  const colors = getStatusColors(status ?? "NORMAL");
  return (
    <div className="flex justify-between items-center py-1.5 border-b border-slate-800 last:border-0">
      <span className="text-xs text-slate-500 tracking-wider">{label}</span>
      <span className={`text-xs tracking-wider ${colors.text}`}>{value}</span>
    </div>
  );
}

function scoreStatus(score) {
  if (score >= 75) return "NORMAL";
  if (score >= 50) return "WARNING";
  return "CRITICAL";
}

export default function SafetyOverview({ latest, connected, events = [] }) {
  const [emergency, setEmergency] = useState(false);

  async function handleSOS() {
    await triggerEmergency("MACHINE_01");
    setEmergency(true);
  }

  async function handleReset() {
    await resetEmergency();
    setEmergency(false);
  }

  if (!connected && !latest) {
    return (
      <div className="border border-red-500/30 rounded p-4 text-red-400 text-xs tracking-wider">
        HUMAN SAFETY MONITOR<br /><br />SERVICE OFFLINE<br /><span className="text-slate-500">Safety data unavailable. Monitoring will resume when the backend reconnects.</span>
      </div>
    );
  }
  if (!latest) return <div className="border border-slate-800 rounded p-4 text-slate-500 text-xs tracking-wider">HUMAN SAFETY MONITOR<br /><br />LOADING SAFETY DATA…</div>;

  const overallColors = getStatusColors(
    latest.overall_risk === "NORMAL" || latest.overall_risk === "LOW" ? "NORMAL" :
    latest.overall_risk === "MEDIUM" ? "WARNING" : "CRITICAL"
  );
  const scoreColors = getStatusColors(scoreStatus(latest.safety_score));
  const ts = new Date(latest.timestamp).toLocaleTimeString();
  const isEmergency = latest.emergency_status !== "NONE" || emergency;

  return (
    <div className="border border-slate-800 rounded p-4 space-y-3">
      <div className="flex items-center justify-between">
        <p className="text-[10px] tracking-widest text-slate-500">HUMAN SAFETY MONITOR</p>
        <span className={`text-[10px] tracking-widest font-bold ${overallColors.text}`}>
          {latest.overall_risk}
        </span>
      </div>

      {/* Score bar */}
      <div className="space-y-1">
        <div className="flex justify-between items-baseline">
          <span className="text-slate-500 text-xs tracking-wider">SYSTEM SAFETY SCORE</span>
          <span className={`text-xl font-bold ${scoreColors.text}`}>
            {latest.safety_score.toFixed(0)}<span className="text-sm font-normal text-slate-400"> / 100</span>
          </span>
        </div>
        <div className="h-1.5 bg-slate-800 rounded-full overflow-hidden">
          <div
            className={`h-full rounded-full transition-all duration-700 ${
              scoreColors.text.includes("red") ? "bg-red-500" :
              scoreColors.text.includes("amber") ? "bg-amber-400" : "bg-emerald-400"
            }`}
            style={{ width: `${latest.safety_score}%` }}
          />
        </div>
      </div>

      <Row label="OPERATOR"    value={latest.operator_present ? "● PRESENT" : "○ NOT DETECTED"} status={latest.operator_present ? "NORMAL" : "WARNING"} />
      <Row label="ACTIVITY"    value={`${(latest.activity_level * 100).toFixed(0)}%`}           status={latest.activity_level > 0.3 ? "NORMAL" : "WARNING"} />
      <Row label="ENVIRONMENT" value={latest.environmental_risk}  status={latest.environmental_risk === "NORMAL" ? "NORMAL" : latest.environmental_risk === "LOW" ? "NORMAL" : "WARNING"} />
      <Row label="PROXIMITY"   value={latest.proximity_risk}       status={latest.proximity_risk === "NORMAL" || latest.proximity_risk === "LOW" ? "NORMAL" : "WARNING"} />
      <Row label="FATIGUE"     value={latest.fatigue_indicator}    status={latest.fatigue_indicator === "NONE" ? "NORMAL" : "WARNING"} />
      <Row label="EMERGENCY"   value={latest.emergency_status}     status={latest.emergency_status === "NONE" ? "NORMAL" : "CRITICAL"} />
      <Row label="LAST UPDATE" value={ts}                          status="NORMAL" />

      {/* Emergency controls */}
      <div className="flex gap-2 pt-1">
        {!isEmergency ? (
          <button
            onClick={handleSOS}
            className="flex-1 text-[10px] tracking-widest px-2 py-1.5 rounded border border-red-500/40 text-red-400 hover:bg-red-500/10 transition-colors"
          >
            🚨 SIMULATE SOS
          </button>
        ) : (
          <button
            onClick={handleReset}
            className="flex-1 text-[10px] tracking-widest px-2 py-1.5 rounded border border-emerald-500/40 text-emerald-400 hover:bg-emerald-500/10 transition-colors"
          >
            ✓ RESET EMERGENCY
          </button>
        )}
      </div>

      {/* Emergency banner */}
      {isEmergency && (
        <div className="border border-red-500/40 bg-red-500/10 rounded p-2 text-xs text-red-400 text-center tracking-wider font-bold animate-pulse">
          🚨 EMERGENCY ACTIVE — SIMULATED DEMO ONLY
        </div>
      )}

      <div className="mc-safety-events"><p className="text-[9px] tracking-widest text-slate-500">RECENT SAFETY EVENTS</p>{events.slice(0, 5).map((event) => <div key={event.id ?? event.event_id} className="mc-safety-event"><span>{event.time ?? new Date(event.timestamp).toLocaleTimeString()}</span><b>{event.label ?? event.event_type?.replaceAll("_", " ")}</b></div>)}</div>

      {/* Privacy note */}
      <p className="text-[9px] text-slate-700 leading-relaxed">
        ⓘ Safety monitoring uses simulated signals. No facial ID or biometric profiling.
      </p>
    </div>
  );
}