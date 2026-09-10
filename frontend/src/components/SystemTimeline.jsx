import { getStatusColors } from "../utils/statusColors";

export default function SystemTimeline({ snapshot, alerts, timeline, secHistory }) {
  // Merge all timestamped entries into one timeline
  const entries = [];

  alerts.slice(0, 5).forEach((a) => entries.push({
    id: `tel-${a.id}`, time: a.time,
    severity: a.status, source: "TELEMETRY",
    label: `${a.status} anomaly — ${a.reasons[0]?.slice(0, 40) ?? ""}`,
  }));

  timeline.slice(0, 5).forEach((e) => entries.push({
    id: `safe-${e.id}`, time: e.time,
    severity: e.risk, source: "SAFETY",
    label: e.label,
  }));

  secHistory.slice(0, 5).forEach((e, i) => entries.push({
    id: `sec-${i}`, time: new Date(e.timestamp).toLocaleTimeString(),
    severity: e.severity, source: "SECURITY",
    label: e.event_type?.replace(/_/g, " ") ?? "Security event",
  }));

  // Sort descending by time (string sort works for HH:MM:SS within same day)
  entries.sort((a, b) => b.time.localeCompare(a.time));

  return (
    <div className="border border-slate-800 rounded p-4 space-y-3">
      <p className="text-[10px] tracking-widest text-slate-500">SYSTEM TIMELINE</p>
      {entries.length === 0 ? (
        <p className="text-slate-600 text-xs tracking-wider">No events yet</p>
      ) : (
        <div className="space-y-1 max-h-52 overflow-y-auto">
          {entries.map((e) => {
            const colors = getStatusColors(
              e.severity === "LOW" || e.severity === "INFO" || e.severity === "NORMAL" ? "NORMAL" :
              e.severity === "MEDIUM" ? "WARNING" : "CRITICAL"
            );
            return (
              <div key={e.id} className="flex gap-2 items-center text-[10px]">
                <span className="text-slate-600 shrink-0 w-16">{e.time}</span>
                <span className={`shrink-0 w-16 ${colors.text}`}>{e.severity}</span>
                <span className="text-slate-500 shrink-0 w-16">{e.source}</span>
                <span className="text-slate-400 truncate">{e.label}</span>
              </div>
            );
          })}
        </div>
      )}
    </div>
  );
}