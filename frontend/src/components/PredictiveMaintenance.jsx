// PredictiveMaintenance.jsx — health, risk, status, contributors
import HealthScore from "./HealthScore";
import { getStatusColors } from "../utils/statusColors";

export default function PredictiveMaintenance({ prediction }) {
  if (!prediction || prediction.message) {
    return (
      <div className="border border-slate-800 rounded p-4 text-slate-600 text-xs tracking-wider">
        PREDICTIVE MAINTENANCE<br /><br />Awaiting first prediction cycle…
      </div>
    );
  }

  const riskColors = getStatusColors(
    prediction.risk_level === "LOW" ? "NORMAL" : prediction.risk_level === "MEDIUM" ? "WARNING" : "CRITICAL"
  );

  return (
    <div className="border border-slate-800 rounded p-4 space-y-4">
      <p className="text-[10px] tracking-widest text-slate-500">PREDICTIVE MAINTENANCE</p>

      <HealthScore score={prediction.health_score} label={prediction.health_label} />

      <div className="grid grid-cols-2 gap-3 text-xs">
        <div>
          <p className="text-slate-500 tracking-wider mb-1">FAILURE RISK</p>
          <p className={`text-xl font-bold ${riskColors.text}`}>
            {(prediction.failure_risk * 100).toFixed(0)}%
          </p>
          <p className={`text-[10px] tracking-widest ${riskColors.text}`}>{prediction.risk_level}</p>
        </div>
        <div>
          <p className="text-slate-500 tracking-wider mb-1">STATUS</p>
          <p className={`text-sm font-bold ${riskColors.text}`}>{prediction.degradation_status}</p>
          <p className="text-[10px] tracking-widest text-slate-500">{prediction.maintenance_priority}</p>
        </div>
      </div>

      {/* Top contributors */}
      {prediction.contributors?.length > 0 && (
        <div>
          <p className="text-[10px] tracking-widest text-slate-600 mb-1.5">WHY IS THIS MACHINE AT RISK?</p>
          <ul className="space-y-1">
            {prediction.contributors.slice(0, 4).map((c, i) => (
              <li key={i} className="text-[11px] text-slate-400">• {c.description}</li>
            ))}
          </ul>
        </div>
      )}

      {/* Recommendation */}
      <div className={`border ${riskColors.border} ${riskColors.bg} rounded p-2 text-[11px] text-slate-300`}>
        {prediction.recommendation}
      </div>
    </div>
  );
}