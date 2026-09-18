import { getStatusColors } from "../utils/statusColors";

function Row({ label, value, status }) {
  const colors = getStatusColors(status ?? "NORMAL");
  return (
    <div className="flex justify-between items-center py-1.5 border-b border-slate-800 last:border-0">
      <span className="text-xs text-slate-500 tracking-wider">{label}</span>
      <span className={`text-xs tracking-wider ${colors.text}`}>{value}</span>
    </div>
  );
}

export default function SecurityOverview({ status, username, role, onLogout }) {
  if (!status) {
    return (
      <div className="border border-slate-800 rounded p-4 text-slate-600 text-xs tracking-wider">
        X.A.Z.E.L. SECURITY<br /><br />Awaiting security data…
      </div>
    );
  }

  const statusColors = getStatusColors(
    status.security_status === "PROTECTED" ? "NORMAL" :
    status.security_status === "ELEVATED"  ? "WARNING" : "CRITICAL"
  );
  const riskColors = getStatusColors(
    status.risk_level === "LOW" ? "NORMAL" : status.risk_level === "MEDIUM" ? "WARNING" : "CRITICAL"
  );

  return (
    <div className="border border-slate-800 rounded p-4 space-y-3">
      <div className="flex items-center justify-between">
        <p className="text-[10px] tracking-widest text-slate-500">X.A.Z.E.L. SECURITY</p>
        <span className={`text-[10px] tracking-widest font-bold ${statusColors.text}`}>
          ● {status.security_status}
        </span>
      </div>

      {/* Risk score bar */}
      <div className="space-y-1">
        <div className="flex justify-between items-baseline">
          <span className="text-slate-500 text-xs tracking-wider">RISK SCORE</span>
          <span className={`text-xl font-bold ${riskColors.text}`}>
            {status.risk_score.toFixed(0)}<span className="text-sm font-normal text-slate-400"> / 100</span>
          </span>
        </div>
        <div className="h-1.5 bg-slate-800 rounded-full overflow-hidden">
          <div
            className={`h-full rounded-full transition-all duration-700 ${
              riskColors.text.includes("red") ? "bg-red-500" :
              riskColors.text.includes("amber") ? "bg-amber-400" : "bg-emerald-400"
            }`}
            style={{ width: `${status.risk_score}%` }}
          />
        </div>
      </div>

      <Row label="AUTHENTICATION"  value={status.authentication}  status="NORMAL" />
      <Row label="AUTHORIZATION"   value={status.authorization}   status="NORMAL" />
      <Row label="RATE LIMITING"   value={status.rate_limiting}   status="NORMAL" />
      <Row label="AUDIT LOGGING"   value={status.audit_logging}   status="NORMAL" />
      <Row label="ACTIVE ALERTS"   value={status.active_alerts}   status={status.active_alerts > 0 ? "WARNING" : "NORMAL"} />
      <Row label="OVERALL RISK"    value={status.risk_level}      status={status.risk_level === "LOW" ? "NORMAL" : status.risk_level === "MEDIUM" ? "WARNING" : "CRITICAL"} />

      {username && (
        <div className="pt-1 flex items-center justify-between">
          <span className="text-[10px] text-slate-600">
            {username} · {role}
          </span>
          <button
            onClick={onLogout}
            className="text-[10px] tracking-widest text-slate-500 hover:text-red-400 transition-colors"
          >
            LOGOUT
          </button>
        </div>
      )}
    </div>
  );
}