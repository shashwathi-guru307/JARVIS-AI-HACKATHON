import { useState } from "react";
import { getStatusColors } from "../utils/statusColors";

const SEVERITY_ORDER = { CRITICAL: 4, HIGH: 3, MEDIUM: 2, LOW: 1, INFO: 0 };

function buildUnifiedAlerts(alerts, visionAlerts, energyAlerts, timeline, txRisks, secHistory) {
  const all = [];

  // Telemetry alerts
  alerts.forEach((a) => {
    all.push({
      id: `tel-${a.id}`, source: "TELEMETRY",
      severity: a.status, time: a.time,
      title: `${a.status} anomaly detected`,
      desc: a.reasons[0] ?? "Telemetry anomaly",
    });
  });

  // Vision alerts
  visionAlerts.forEach((a) => {
    all.push({
      id: `vis-${a.id}`, source: "VISION",
      severity: a.risk, time: a.time,
      title: "Vision alert",
      desc: a.event?.replace(/_/g, " ") ?? "Vision event",
    });
  });

  // Energy alerts
  energyAlerts.forEach((a) => {
    all.push({
      id: `eng-${a.id}`, source: "ENERGY",
      severity: a.status === "OPTIMAL" ? "LOW" : a.priority,
      time: a.time,
      title: `Energy ${a.status}`,
      desc: a.action,
    });
  });

  // Safety events from timeline
  timeline.filter(e => e.risk !== "NORMAL" && e.risk !== "LOW").forEach((e) => {
    all.push({
      id: `safe-${e.id}`, source: "SAFETY",
      severity: e.risk, time: e.time,
      title: "Safety alert",
      desc: e.label,
    });
  });

  // Suspicious transactions
  txRisks.filter(r => r.is_suspicious).forEach((r) => {
    all.push({
      id: `tx-${r.transaction_id}`, source: "SECURITY",
      severity: r.risk_level, time: new Date(r.timestamp).toLocaleTimeString(),
      title: "Suspicious transaction",
      desc: r.contributors[0] ?? r.recommendation,
    });
  });

  // Security events
  secHistory.filter(e => e.severity !== "LOW").forEach((e, i) => {
    all.push({
      id: `sec-${i}`, source: "SECURITY",
      severity: e.severity, time: new Date(e.timestamp).toLocaleTimeString(),
      title: e.event_type?.replace(/_/g, " ") ?? "Security event",
      desc: e.description ?? "",
    });
  });

  // Sort by severity then time
  all.sort((a, b) => (SEVERITY_ORDER[b.severity] ?? 0) - (SEVERITY_ORDER[a.severity] ?? 0));
  return all.slice(0, 25);
}

const FILTERS = ["ALL", "CRITICAL", "HIGH", "MEDIUM", "TELEMETRY", "VISION", "ENERGY", "SAFETY", "SECURITY"];

export default function UnifiedAlertCenter({
  alerts, visionAlerts, energyAlerts, timeline, txRisks, secHistory
}) {
  const [filter, setFilter] = useState("ALL");

  const all = buildUnifiedAlerts(alerts, visionAlerts, energyAlerts, timeline, txRisks, secHistory);
  const filtered = filter === "ALL"
    ? all
    : ["CRITICAL", "HIGH", "MEDIUM"].includes(filter)
    ? all.filter(a => a.severity === filter)
    : all.filter(a => a.source === filter);

  return (
    <div className="border border-slate-800 rounded p-4 space-y-3">
      <div className="flex items-center justify-between">
        <p className="text-[10px] tracking-widest text-slate-500">UNIFIED ALERT CENTER</p>
        <span className="text-[10px] text-slate-600">{all.length} events</span>
      </div>

      {/* Filter chips */}
      <div className="flex flex-wrap gap-1">
        {FILTERS.map((f) => (
          <button
            key={f}
            onClick={() => setFilter(f)}
            className={`text-[9px] tracking-widest px-2 py-0.5 rounded border transition-colors ${
              filter === f
                ? "border-cyan-500/60 text-cyan-400 bg-cyan-500/10"
                : "border-slate-700 text-slate-600 hover:text-slate-400"
            }`}
          >
            {f}
          </button>
        ))}
      </div>

      {/* Alert list */}
      {filtered.length === 0 ? (
        <p className="text-emerald-400 text-xs tracking-wider">✓ No active alerts for this filter</p>
      ) : (
        <div className="space-y-1.5 max-h-56 overflow-y-auto">
          {filtered.map((a) => {
            const colors = getStatusColors(
              a.severity === "LOW" || a.severity === "INFO" ? "NORMAL" :
              a.severity === "MEDIUM" ? "WARNING" : "CRITICAL"
            );
            return (
              <div key={a.id} className={`border ${colors.border} ${colors.bg} rounded px-3 py-2 flex gap-3 items-start`}>
                <span className={`text-[9px] tracking-widest shrink-0 mt-0.5 ${colors.text}`}>{a.severity}</span>
                <div className="flex-1 min-w-0">
                  <p className={`text-[10px] font-medium ${colors.text}`}>{a.title}</p>
                  <p className="text-[10px] text-slate-500 truncate">{a.desc}</p>
                </div>
                <div className="text-right shrink-0">
                  <p className="text-[9px] text-slate-600">{a.source}</p>
                  <p className="text-[9px] text-slate-700">{a.time}</p>
                </div>
              </div>
            );
          })}
        </div>
      )}
    </div>
  );
}