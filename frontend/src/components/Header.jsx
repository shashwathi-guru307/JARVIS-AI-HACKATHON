// Header.jsx — top bar with system name and live connection status
import { getStatusColors } from '../utils/statusColors';

export default function Header({ connected, latest }) {
  const colors = getStatusColors(connected ? 'NORMAL' : 'OFFLINE');

  return (
    <header className="border-b border-slate-800 px-6 py-4 flex items-center justify-between">
      <div>
        <h1 className="text-xl font-bold tracking-[0.3em] text-cyan-400">J.A.R.V.I.S.</h1>
        <p className="text-xs tracking-widest text-slate-500 mt-0.5">REAL-TIME INTELLIGENCE SYSTEM</p>
      </div>

      <div className="flex items-center gap-6">
        {/* Live badge */}
        {connected && latest && (
          <span className="text-xs tracking-widest text-emerald-400 flex items-center gap-1.5">
            <span className="w-1.5 h-1.5 rounded-full bg-emerald-400 animate-pulse" />
            LIVE
          </span>
        )}

        {/* Connection status */}
        <div className={`flex items-center gap-2 text-xs tracking-widest ${colors.text}`}>
          <span className={`w-2 h-2 rounded-full ${colors.dot}`} />
          {connected ? 'SYSTEM ONLINE' : 'SYSTEM OFFLINE'}
        </div>
      </div>
    </header>
  );
}