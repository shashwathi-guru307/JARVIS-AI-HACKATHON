// AlertPanel.jsx — current anomaly state + scrollable alert history
import { getStatusColors } from '../utils/statusColors';

function CurrentAlert({ latest }) {
  const analysis = latest?.analysis;
  const status   = analysis?.status ?? 'NORMAL';
  const colors   = getStatusColors(status);

  if (status === 'NORMAL') {
    return (
      <div className="flex items-center gap-2 text-emerald-400 text-xs tracking-wider">
        <span>✓</span>
        <span>No active anomalies</span>
      </div>
    );
  }

  return (
    <div className={`border ${colors.border} ${colors.bg} rounded p-3`}>
      <p className={`text-xs font-bold tracking-widest ${colors.text} mb-1`}>
        ⚠ {status} ALERT — {latest?.device_id}
      </p>
      <ul className="mt-2 space-y-1">
        {(analysis?.reasons ?? []).map((r, i) => (
          <li key={i} className="text-xs text-slate-400">• {r}</li>
        ))}
      </ul>
    </div>
  );
}

export default function AlertPanel({ latest, alerts }) {
  return (
    <div className="border border-slate-800 rounded p-4 flex flex-col gap-4">
      <p className="text-[10px] tracking-widest text-slate-500">SYSTEM ALERTS</p>
      <CurrentAlert latest={latest} />

      {alerts.length > 0 && (
        <div>
          <p className="text-[10px] tracking-widest text-slate-600 mb-2">ALERT HISTORY</p>
          <div className="space-y-1 max-h-48 overflow-y-auto">
            {alerts.map((a) => {
              const colors = getStatusColors(a.status);
              return (
                <div key={a.id} className="flex items-start gap-2 text-xs">
                  <span className="text-slate-600 shrink-0">{a.time}</span>
                  <span className={`shrink-0 ${colors.text}`}>{a.status}</span>
                  <span className="text-slate-500 truncate">{a.reasons[0]}</span>
                </div>
              );
            })}
          </div>
        </div>
      )}
    </div>
  );
}