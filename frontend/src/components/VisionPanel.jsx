// VisionPanel.jsx — J.A.R.V.I.S. vision intelligence panel
import { useState } from "react";
import { useVision } from "../hooks/useVision";
import { getStatusColors } from "../utils/statusColors";

export default function VisionPanel() {
  const [enabled, setEnabled] = useState(false);
  const { visionConnected, latestVision, visionAlerts } = useVision(enabled);

  const risk      = latestVision?.risk_level ?? "NORMAL";
  const colors    = getStatusColors(risk);
  const camStatus = latestVision
    ? (latestVision.summary?.includes("[DEMO]") ? "DEMO" : "CONNECTED")
    : (enabled ? "CONNECTING" : "OFF");

  return (
    <div className="border border-slate-800 rounded p-4 space-y-4">
      {/* Header row */}
      <div className="flex items-center justify-between">
        <p className="text-[10px] tracking-widest text-slate-500">VISION INTELLIGENCE</p>
        <button
          onClick={() => setEnabled((v) => !v)}
          className={`text-[10px] tracking-widest px-3 py-1 rounded border transition-colors ${
            enabled
              ? "border-red-500/40 text-red-400 hover:bg-red-500/10"
              : "border-cyan-500/40 text-cyan-400 hover:bg-cyan-500/10"
          }`}
        >
          {enabled ? "STOP CAMERA" : "START CAMERA"}
        </button>
      </div>

      {/* Camera preview area */}
      <div className="flex items-center justify-center h-28 bg-slate-900/50 rounded border border-slate-800 text-slate-600 text-xs tracking-wider">
        {!enabled && "Camera OFF"}
        {enabled && !latestVision && "Initializing vision stream..."}
        {enabled && latestVision && (
          <div className="text-center space-y-1">
            <p className={`text-lg font-bold ${colors.text}`}>{risk}</p>
            <p className="text-slate-500 text-[10px]">{latestVision.event?.replace(/_/g, " ").toUpperCase()}</p>
          </div>
        )}
      </div>

      {/* Status grid */}
      {enabled && (
        <div className="space-y-1.5">
          {[
            ["CAMERA",     camStatus],
            ["MODE",       latestVision?.summary?.includes("[DEMO]") ? "DEMO" : "LOCAL"],
            ["LAST EVENT", latestVision?.event?.replace(/_/g, " ") ?? "—"],
            ["RISK",       risk],
            ["CONFIDENCE", latestVision ? `${Math.round(latestVision.confidence * 100)}%` : "—"],
          ].map(([label, val]) => (
            <div key={label} className="flex justify-between items-center text-xs">
              <span className="text-slate-500 tracking-wider">{label}</span>
              <span className={label === "RISK" ? colors.text : "text-slate-300"}>{val}</span>
            </div>
          ))}
        </div>
      )}

      {/* Current alert */}
      {enabled && latestVision && risk !== "NORMAL" && (
        <div className={`border ${colors.border} ${colors.bg} rounded p-3 text-xs`}>
          <p className={`font-bold tracking-widest ${colors.text} mb-1`}>⚠ VISION ALERT</p>
          <p className="text-slate-400">{latestVision.summary}</p>
          <p className="text-slate-500 mt-1">→ {latestVision.recommended_action}</p>
        </div>
      )}

      {/* Vision alert history */}
      {visionAlerts.length > 0 && (
        <div>
          <p className="text-[10px] tracking-widest text-slate-600 mb-1.5">VISION HISTORY</p>
          <div className="space-y-1 max-h-32 overflow-y-auto">
            {visionAlerts.map((a) => {
              const c = getStatusColors(a.risk);
              return (
                <div key={a.id} className="flex gap-2 text-[11px]">
                  <span className="text-slate-600 shrink-0">{a.time}</span>
                  <span className={`shrink-0 ${c.text}`}>{a.risk}</span>
                  <span className="text-slate-500 truncate">{a.event?.replace(/_/g, " ")}</span>
                </div>
              );
            })}
          </div>
        </div>
      )}
    </div>
  );
}