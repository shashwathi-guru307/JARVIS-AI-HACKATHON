import { getStatusColors } from "../utils/statusColors";

export default function TransactionRisk({ summary, risks }) {
  if (!summary) {
    return (
      <div className="border border-slate-800 rounded p-4 text-slate-600 text-xs tracking-wider">
        FINANCIAL RISK MONITOR<br /><br />Awaiting transaction data…
      </div>
    );
  }

  const trendIcon = summary.risk_trend === "RISING" ? "↗" : summary.risk_trend === "FALLING" ? "↘" : "→";
  const trendColor = summary.risk_trend === "RISING" ? "text-red-400" : summary.risk_trend === "FALLING" ? "text-emerald-400" : "text-slate-400";

  // Latest high-risk entry
  const latestHighRisk = risks.find(r => r.risk_level === "HIGH" || r.risk_level === "CRITICAL");
  const lhrColors = latestHighRisk ? getStatusColors("CRITICAL") : null;

  return (
    <div className="border border-slate-800 rounded p-4 space-y-4">
      <div className="flex items-center justify-between">
        <p className="text-[10px] tracking-widest text-slate-500">FINANCIAL RISK MONITOR</p>
        <span className={`text-sm font-bold ${trendColor}`}>{trendIcon}</span>
      </div>

      <div className="grid grid-cols-2 gap-3 text-xs">
        {[
          ["TOTAL", summary.total_count],
          ["HIGH RISK", summary.high_risk],
          ["MEDIUM RISK", summary.medium_risk],
          ["LOW RISK", summary.low_risk],
        ].map(([label, val]) => (
          <div key={label}>
            <p className="text-slate-500 tracking-wider text-[10px]">{label}</p>
            <p className={`text-lg font-bold ${
              label === "HIGH RISK" && val > 0 ? "text-red-400" :
              label === "MEDIUM RISK" && val > 0 ? "text-amber-400" :
              "text-slate-300"
            }`}>{val}</p>
          </div>
        ))}
      </div>

      <div className="text-[10px] text-slate-500 flex justify-between">
        <span>AVG: ₹{summary.avg_amount.toLocaleString("en-IN", { maximumFractionDigits: 0 })}</span>
        <span>TOTAL: ₹{summary.total_amount.toLocaleString("en-IN", { maximumFractionDigits: 0 })}</span>
      </div>

      {/* Latest suspicious */}
      {latestHighRisk && (
        <div className={`border ${lhrColors.border} ${lhrColors.bg} rounded p-2 text-xs space-y-1`}>
          <p className={`font-bold tracking-widest ${lhrColors.text} text-[10px]`}>
            ⚠ SUSPICIOUS TRANSACTION PATTERN
          </p>
          <p className="text-slate-400">ID: {latestHighRisk.transaction_id}</p>
          <p className={`${lhrColors.text}`}>Risk: {latestHighRisk.risk_level} ({latestHighRisk.risk_score.toFixed(0)}/100)</p>
          {latestHighRisk.contributors.slice(0, 3).map((c, i) => (
            <p key={i} className="text-slate-500 text-[10px]">• {c}</p>
          ))}
          <p className="text-slate-400 text-[10px] italic">{latestHighRisk.recommendation}</p>
        </div>
      )}
    </div>
  );
}