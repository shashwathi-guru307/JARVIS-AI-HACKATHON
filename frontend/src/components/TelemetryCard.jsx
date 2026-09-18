// TelemetryCard.jsx — single sensor reading card
import { getStatusColors } from '../utils/statusColors';

export default function TelemetryCard({ label, value, unit, status = 'NORMAL', subtitle, onOpen, active = false }) {
  const colors = getStatusColors(status);

  return (
    <button
      type="button"
      className={`mc-telemetry-card border ${colors.border} ${colors.bg} rounded p-4 flex flex-col gap-2 text-left ${active ? 'selected' : ''}`}
      onClick={onOpen}
      aria-label={`Open ${label.toLowerCase()} details for machine M-101`}
    >
      <p className="text-[10px] tracking-widest text-slate-500">{label}</p>
      <p className={`text-2xl font-bold ${colors.text}`}>
        {value !== null && value !== undefined ? value : '—'}
        <span className="text-sm font-normal text-slate-400 ml-1">{unit}</span>
      </p>
      <span className={`text-[10px] tracking-widest ${colors.text}`}>{status}</span>
      <span className="mc-telemetry-subtitle">{subtitle}</span>
      <span className="mc-telemetry-link">VIEW DETAILS <span aria-hidden="true">→</span></span>
    </button>
  );
}