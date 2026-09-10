// SystemStatus.jsx — backend/WebSocket/telemetry status panel
import { getStatusColors } from '../utils/statusColors';

function Row({ label, value, status }) {
  const colors = getStatusColors(status);
  return (
    <div className="flex justify-between items-center py-1.5 border-b border-slate-800 last:border-0">
      <span className="text-xs text-slate-500 tracking-wider">{label}</span>
      <span className={`text-xs tracking-wider ${colors.text}`}>{value}</span>
    </div>
  );
}

export default function SystemStatus({ connected, latest, streamStatus }) {
  const clients = streamStatus?.connected_clients ?? '—';
  const interval = streamStatus?.interval_seconds ?? 1;

  return (
    <div className="border border-slate-800 rounded p-4">
      <p className="text-[10px] tracking-widest text-slate-500 mb-3">SYSTEM STATUS</p>
      <Row label="Backend"    value={connected ? 'ONLINE'     : 'OFFLINE'}    status={connected ? 'NORMAL' : 'OFFLINE'} />
      <Row label="WebSocket"  value={connected ? 'CONNECTED'  : 'DISCONNECTED'} status={connected ? 'NORMAL' : 'OFFLINE'} />
      <Row label="Telemetry"  value={connected && latest ? 'STREAMING' : 'IDLE'} status={connected && latest ? 'NORMAL' : 'OFFLINE'} />
      <Row label="Devices"    value={streamStatus?.devices ?? 1} status="NORMAL" />
      <Row label="Update Rate" value={`${interval} sec`}         status="NORMAL" />
      <Row label="Clients"    value={clients}                    status="NORMAL" />
    </div>
  );
}