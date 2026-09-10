// TelemetryCard.jsx — single sensor reading card
import { getStatusColors } from '../utils/statusColors';

export default function TelemetryCard({ label, value, unit, status = 'NORMAL' }) {
  const colors = getStatusColors(status);

  return (
    <div className={`border ${colors.border} ${colors.bg} rounded p-4 flex flex-col gap-2`}>
      <p className="text-[10px] tracking-widest text-slate-500">{label}</p>
      <p className={`text-2xl font-bold ${colors.text}`}>
        {value !== null && value !== undefined ? value : '—'}
        <span className="text-sm font-normal text-slate-400 ml-1">{unit}</span>
      </p>
      <span className={`text-[10px] tracking-widest ${colors.text}`}>{status}</span>
    </div>
  );
}