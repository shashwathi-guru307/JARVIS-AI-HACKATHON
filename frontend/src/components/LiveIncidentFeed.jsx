import { Activity, AlertTriangle, BrainCircuit, Gauge, Thermometer } from "lucide-react";

const ICONS = { temperature: Thermometer, vibration: Activity, rpm: Gauge, maintenance: BrainCircuit };

export default function LiveIncidentFeed({ incident, alerts }) {
  const rows = incident ? [
    ["maintenance", "Predictive maintenance risk elevated", "MAINTENANCE", "WARNING"],
    ["rpm", "RPM deviation detected", "M-101 · TELEMETRY", "WARNING"],
    ["vibration", "Vibration anomaly detected", "M-101 · TELEMETRY", "CRITICAL"],
    ["temperature", "Temperature threshold exceeded", "M-101 · TELEMETRY", "CRITICAL"],
  ] : (alerts ?? []).slice(0, 4).map((alert) => ["temperature", `${alert.status} telemetry anomaly`, "M-101 · TELEMETRY", alert.status]);

  return <section className="mc-panel mc-feed"><div className="mc-section-heading"><div><span className="mc-kicker">LIVE INCIDENT FEED</span><h2>Operational signals</h2></div><span className="mc-live"><i /> LIVE</span></div><div className="mc-feed-list">{rows.length === 0 ? <div className="mc-empty">Waiting for machine signals...</div> : rows.map(([type, title, source, severity], index) => { const Icon = ICONS[type] ?? AlertTriangle; return <div className="mc-feed-row" key={`${title}-${index}`}><span className={`mc-feed-icon ${severity.toLowerCase()}`}><Icon size={14} /></span><div><strong>{title}</strong><small>{source}</small></div><span className={`mc-severity ${severity.toLowerCase()}`}>{severity}</span><time>{index === 0 && incident ? "NOW" : `${10 + index}:4${index}:2${index}`}</time></div>; })}</div>{incident && <div className="mc-feed-footer"><b>{incident.source_event_ids?.length ?? 4} RELATED ALERTS</b><span>↓</span><b>1 MACHINE INCIDENT</b></div>}</section>;
}
