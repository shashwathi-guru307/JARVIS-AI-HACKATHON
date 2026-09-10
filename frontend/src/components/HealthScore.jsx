// HealthScore.jsx — health score bar and label
import { getStatusColors } from "../utils/statusColors";

const LABEL_TO_STATUS = {
  EXCELLENT: "NORMAL", GOOD: "NORMAL",
  WARNING: "WARNING",  POOR: "WARNING", CRITICAL: "CRITICAL",
};

export default function HealthScore({ score, label }) {
  const status = LABEL_TO_STATUS[label] ?? "NORMAL";
  const colors = getStatusColors(status);
  const pct    = Math.max(0, Math.min(100, score ?? 0));

  return (
    <div className="space-y-2">
      <div className="flex justify-between items-baseline">
        <span className="text-slate-500 text-xs tracking-wider">MACHINE HEALTH</span>
        <span className={`text-2xl font-bold ${colors.text}`}>{pct.toFixed(0)}<span className="text-sm text-slate-400 font-normal"> / 100</span></span>
      </div>
      {/* Bar */}
      <div className="h-2 bg-slate-800 rounded-full overflow-hidden">
        <div
          className={`h-full rounded-full transition-all duration-700 ${
            status === "CRITICAL" ? "bg-red-500" : status === "WARNING" ? "bg-amber-400" : "bg-emerald-400"
          }`}
          style={{ width: `${pct}%` }}
        />
      </div>
      <span className={`text-[10px] tracking-widest ${colors.text}`}>{label}</span>
    </div>
  );
}