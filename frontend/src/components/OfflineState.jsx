/**
 * OfflineState — shown when the backend is unreachable.
 * Never crashes the dashboard; always gives a clear status.
 */
export default function OfflineState({ modules }) {
  // modules is the snapshot.modules dict (may be undefined if backend is down)
  const items = modules
    ? Object.entries(modules)
    : [["backend", "OFFLINE"]];

  return (
    <div className="border border-slate-800 rounded p-6 space-y-4 col-span-2">
      <div className="flex items-center gap-3">
        <span className="w-2 h-2 rounded-full bg-red-500 animate-pulse" />
        <p className="text-sm tracking-widest text-red-400">J.A.R.V.I.S. — CONNECTING…</p>
      </div>
      <p className="text-xs text-slate-500">
        One or more services are unavailable. Deterministic intelligence continues where possible.
      </p>
      <div className="grid grid-cols-2 gap-x-6 gap-y-1">
        {items.map(([mod, status]) => {
          const ok   = ["ONLINE","PROTECTED","AVAILABLE","OPTIMAL"].includes(status);
          const warn = ["WARMING_UP","ELEVATED","DEGRADED"].includes(status);
          const color = ok ? "text-emerald-400" : warn ? "text-amber-400" : "text-red-400";
          return (
            <div key={mod} className="flex justify-between text-[10px]">
              <span className="text-slate-600 tracking-wider">{mod.toUpperCase()}</span>
              <span className={`tracking-wider ${color}`}>● {status}</span>
            </div>
          );
        })}
      </div>
    </div>
  );
}