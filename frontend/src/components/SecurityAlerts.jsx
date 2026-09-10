import { getStatusColors } from "../utils/statusColors";

export default function SecurityAlerts({ history }) {
  if (!history || history.length === 0) {
    return (
      <div className="border border-slate-800 rounded p-4 text-slate-600 text-xs tracking-wider">
        SECURITY AUDIT TIMELINE<br /><br />No events yet…
      </div>
    );
  }

  return (
    <div className="border border-slate-800 rounded p-4 space-y-3">
      <p className="text-[10px] tracking-widest text-slate-500">SECURITY AUDIT TIMELINE</p>
      <div className="space-y-1.5 max-h-64 overflow-y-auto">
        {history.map((e, i) => {
          const colors = getStatusColors(
            e.severity === "LOW"    ? "NORMAL" :
            e.severity === "MEDIUM" ? "WARNING" : "CRITICAL"
          );
          const ts = new Date(e.timestamp).toLocaleTimeString();
          return (
            <div key={i} className="flex gap-2 items-start text-[10px]">
              <span className="text-slate-600 shrink-0 w-16">{ts}</span>
              <span className={`shrink-0 ${colors.text} w-16 truncate`}>{e.severity}</span>
              <span className="text-slate-500 truncate">{e.event_type.replace(/_/g, " ")}</span>
            </div>
          );
        })}
      </div>
    </div>
  );
}