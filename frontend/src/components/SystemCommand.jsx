// SystemCommand.jsx — top-level unified command center panel
import { getStatusColors } from "../utils/statusColors";

const SCORE_COLORS = (score) =>
  score >= 75 ? "text-emerald-400" : score >= 50 ? "text-amber-400" : "text-red-400";

const STATUS_COLORS = {
  OPERATIONAL: "text-emerald-400",
  CAUTION:     "text-amber-400",
  DEGRADED:    "text-red-400",
  CRITICAL:    "text-red-500",
};

function ModuleRow({ label, status }) {
  const online = status === "ONLINE" || status === "PROTECTED" || status === "AVAILABLE";
  const warn   = status === "WARMING_UP" || status === "ELEVATED";
  const color  = online ? "text-emerald-400" : warn ? "text-amber-400" : "text-slate-500";
  return (
    <div className="flex justify-between items-center text-[10px]">
      <span className="text-slate-500 tracking-wider">{label}</span>
      <span className={`tracking-wider ${color}`}>● {status}</span>
    </div>
  );
}

export default function SystemCommand({ snapshot }) {
  if (!snapshot) {
    return (
      <div className="border border-slate-800 rounded p-4 col-span-2 text-slate-600 text-xs tracking-wider">
        X.A.Z.E.L. COMMAND CENTER<br /><br />Initializing unified intelligence…
      </div>
    );
  }

  const statusColor = STATUS_COLORS[snapshot.system_status] ?? "text-slate-400";
  const scoreColor  = SCORE_COLORS(snapshot.system_score);
  const riskColors  = getStatusColors(
    snapshot.system_risk === "LOW" ? "NORMAL" :
    snapshot.system_risk === "MEDIUM" ? "WARNING" : "CRITICAL"
  );

  return (
    <div className="border border-slate-800 rounded p-5 col-span-2 space-y-4">
      {/* Header row */}
      <div className="flex items-start justify-between">
        <div>
          <p className="text-[10px] tracking-widest text-slate-500">X.A.Z.E.L. COMMAND CENTER</p>
          <p className={`text-2xl font-bold tracking-widest mt-1 ${statusColor}`}>
            {snapshot.system_status}
          </p>
        </div>
        <div className="text-right">
          <p className="text-[10px] tracking-widest text-slate-500">SYSTEM SCORE</p>
          <p className={`text-3xl font-bold ${scoreColor}`}>{snapshot.system_score.toFixed(0)}</p>
          <p className="text-[10px] text-slate-600">/ 100</p>
        </div>
      </div>

      {/* System health bar */}
      <div className="h-2 bg-slate-800 rounded-full overflow-hidden">
        <div
          className={`h-full rounded-full transition-all duration-700 ${
            snapshot.system_score >= 75 ? "bg-emerald-400" :
            snapshot.system_score >= 50 ? "bg-amber-400" : "bg-red-500"
          }`}
          style={{ width: `${snapshot.system_score}%` }}
        />
      </div>

      {/* Metrics row */}
      <div className="grid grid-cols-3 gap-3 text-center">
        <div>
          <p className="text-[10px] tracking-widest text-slate-500">RISK</p>
          <p className={`text-sm font-bold ${riskColors.text}`}>{snapshot.system_risk}</p>
        </div>
        <div>
          <p className="text-[10px] tracking-widest text-slate-500">ALERTS</p>
          <p className={`text-sm font-bold ${snapshot.active_alerts > 0 ? "text-amber-400" : "text-emerald-400"}`}>
            {snapshot.active_alerts}
          </p>
        </div>
        <div>
          <p className="text-[10px] tracking-widest text-slate-500">PRIORITY</p>
          <p className={`text-sm font-bold ${
            snapshot.priority === "IMMEDIATE" ? "text-red-400" :
            snapshot.priority === "URGENT"    ? "text-amber-400" : "text-slate-400"
          }`}>{snapshot.priority}</p>
        </div>
      </div>

      {/* Module status */}
      {snapshot.modules && (
        <div className="grid grid-cols-2 gap-x-6 gap-y-1 border-t border-slate-800 pt-3">
          {Object.entries(snapshot.modules).map(([mod, status]) => (
            <ModuleRow key={mod} label={mod.toUpperCase()} status={status} />
          ))}
        </div>
      )}

      {/* Correlated conditions */}
      {snapshot.correlated_conditions?.length > 0 && (
        <div className={`border ${riskColors.border} ${riskColors.bg} rounded p-3 space-y-1`}>
          <p className={`text-[10px] tracking-widest font-bold ${riskColors.text}`}>
            ⚡ CORRELATED CONDITIONS
          </p>
          {snapshot.correlated_conditions.map((c, i) => (
            <p key={i} className="text-[11px] text-slate-400">• {c}</p>
          ))}
        </div>
      )}

      {/* Unified recommendation */}
      {snapshot.recommendation && (
        <div className="text-xs text-slate-300 border-t border-slate-800 pt-3">
          <span className="text-slate-500 text-[10px] tracking-wider">RECOMMENDATION: </span>
          {snapshot.recommendation}
        </div>
      )}
    </div>
  );
}