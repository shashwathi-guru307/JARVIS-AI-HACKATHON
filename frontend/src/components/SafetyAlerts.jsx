import { getStatusColors } from "../utils/statusColors";

export default function SafetyAlerts({ latest, latestEvent, timeline }) {
  if (!latest) return null;

  const overallColors = getStatusColors(
    latest.overall_risk === "NORMAL" || latest.overall_risk === "LOW" ? "NORMAL" :
    latest.overall_risk === "MEDIUM" ? "WARNING" : "CRITICAL"
  );

  return (
    <div className="border border-slate-800 rounded p-4 space-y-4">
      <p className="text-[10px] tracking-widest text-slate-500">SAFETY ALERTS</p>

      {/* Current status */}
      {latest.overall_risk === "NORMAL" || latest.overall_risk === "LOW" ? (
        <div className="flex items-center gap-2 text-emerald-400 text-xs tracking-wider">
          <span>✓</span><span>No active safety concerns</span>
        </div>
      ) : (
        <div className={`border ${overallColors.border} ${overallColors.bg} rounded p-3 space-y-2`}>
          <p className={`text-xs font-bold tracking-widest ${overallColors.text}`}>
            ⚠ SAFETY RISK: {latest.overall_risk}
          </p>
          <p className="text-xs text-slate-300">{latest.recommended_action}</p>
          {latest.contributors.length > 0 && (
            <ul className="space-y-0.5">
              {latest.contributors.map((c, i) => (
                <li key={i} className="text-[11px] text-slate-400">• {c}</li>
              ))}
            </ul>
          )}
        </div>
      )}

      {/* Latest event */}
      {latestEvent && latestEvent.severity !== "NORMAL" && (
        <div>
          <p className="text-[10px] tracking-widest text-slate-600 mb-1.5">LATEST EVENT</p>
          <div className="text-[11px] text-slate-400 space-y-0.5">
            <p><span className="text-slate-600">Type:</span> {latestEvent.event_type}</p>
            <p><span className="text-slate-600">Severity:</span> {latestEvent.severity}</p>
            <p><span className="text-slate-600">Note:</span> {latestEvent.description}</p>
          </div>
        </div>
      )}

      {/* Timeline */}
      {timeline.length > 0 && (
        <div>
          <p className="text-[10px] tracking-widest text-slate-600 mb-1.5">SAFETY TIMELINE</p>
          <div className="space-y-1 max-h-44 overflow-y-auto">
            {timeline.map((entry) => {
              const c = getStatusColors(
                entry.risk === "NORMAL" || entry.risk === "LOW" ? "NORMAL" :
                entry.risk === "MEDIUM" ? "WARNING" : "CRITICAL"
              );
              return (
                <div key={entry.id} className="flex gap-2 text-[10px] items-center">
                  <span className="text-slate-600 shrink-0 w-16">{entry.time}</span>
                  <span className={`shrink-0 ${c.text}`}>{entry.risk}</span>
                  <span className="text-slate-500 truncate">{entry.label}</span>
                  <span className="text-slate-600 ml-auto shrink-0">{entry.score.toFixed(0)}</span>
                </div>
              );
            })}
          </div>
        </div>
      )}
    </div>
  );
}