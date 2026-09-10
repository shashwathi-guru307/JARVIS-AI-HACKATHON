// DigitalTwin.jsx — 2D machine schematic driven by real telemetry
import { getStatusColors } from "../utils/statusColors";

const STATUS_TO_COLOR = {
  HEALTHY:   "#34d399",
  WARNING:   "#fbbf24",
  DEGRADING: "#f97316",
  HIGH_RISK: "#ef4444",
  CRITICAL:  "#dc2626",
  OFFLINE:   "#475569",
};

export default function DigitalTwin({ twin }) {
  if (!twin) {
    return (
      <div className="border border-slate-800 rounded p-4 flex items-center justify-center h-48 text-slate-600 text-xs tracking-wider">
        AWAITING TELEMETRY…
      </div>
    );
  }

  const color  = STATUS_TO_COLOR[twin.status] ?? "#475569";
  const colors = getStatusColors(
    twin.status === "HEALTHY" ? "NORMAL" : twin.status === "DEGRADING" || twin.status === "WARNING" ? "WARNING" : "CRITICAL"
  );

  return (
    <div className="border border-slate-800 rounded p-4 space-y-3">
      <p className="text-[10px] tracking-widest text-slate-500">DIGITAL TWIN — {twin.device_id}</p>

      {/* SVG schematic */}
      <svg viewBox="0 0 200 120" className="w-full h-28" style={{ color }}>
        {/* Machine body */}
        <rect x="40" y="20" width="120" height="70" rx="4" fill="none" stroke="currentColor" strokeWidth="1.5" opacity="0.6" />
        {/* Motor circle */}
        <circle cx="100" cy="55" r="22" fill="none" stroke="currentColor" strokeWidth="2" />
        {/* Gear icon lines */}
        <line x1="100" y1="33" x2="100" y2="77" stroke="currentColor" strokeWidth="1" opacity="0.4" />
        <line x1="78"  y1="55" x2="122" y2="55" stroke="currentColor" strokeWidth="1" opacity="0.4" />
        {/* Sensor box */}
        <rect x="82" y="96" width="36" height="14" rx="2" fill="none" stroke="currentColor" strokeWidth="1" opacity="0.5" />
        <text x="100" y="107" textAnchor="middle" fontSize="6" fill="currentColor" opacity="0.7">SENSOR</text>
        {/* Status dot */}
        <circle cx="150" cy="30" r="5" fill={color} />
        {/* RPM label */}
        <text x="100" y="58" textAnchor="middle" fontSize="9" fill="currentColor">⚙</text>
      </svg>

      {/* Live values */}
      <div className="grid grid-cols-2 gap-x-4 gap-y-1 text-xs">
        {[
          ["STATUS",  twin.status],
          ["HEALTH",  `${twin.health_score?.toFixed(0)} / 100`],
          ["TEMP",    `${twin.temperature?.toFixed(1)} °C`],
          ["VIBRATION", `${twin.vibration?.toFixed(2)} g`],
          ["RPM",     twin.rpm?.toFixed(0)],
          ["BATTERY", `${twin.battery?.toFixed(0)} %`],
        ].map(([label, val]) => (
          <div key={label} className="flex justify-between">
            <span className="text-slate-500">{label}</span>
            <span className={label === "STATUS" ? colors.text : "text-slate-300"}>{val}</span>
          </div>
        ))}
      </div>
    </div>
  );
}