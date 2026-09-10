// DeviceInfo.jsx — device summary panel
export default function DeviceInfo({ latest }) {
  if (!latest) return null;

  const t  = latest.telemetry ?? {};
  const ts = latest.timestamp
    ? new Date(latest.timestamp).toLocaleTimeString()
    : '—';

  return (
    <div className="border border-slate-800 rounded p-4">
      <p className="text-[10px] tracking-widest text-slate-500 mb-3">DEVICE INFORMATION</p>
      <div className="space-y-2">
        {[
          ['Device ID',    latest.device_id],
          ['Status',       latest.analysis?.status ?? '—'],
          ['Last Update',  ts],
          ['Temperature',  `${t.temperature ?? '—'} °C`],
          ['RPM',          t.rpm ?? '—'],
          ['Battery',      `${t.battery ?? '—'} %`],
        ].map(([label, value]) => (
          <div key={label} className="flex justify-between items-center">
            <span className="text-xs text-slate-500">{label}</span>
            <span className="text-xs text-slate-300">{value}</span>
          </div>
        ))}
      </div>
    </div>
  );
}