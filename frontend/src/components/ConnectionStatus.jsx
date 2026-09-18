// ConnectionStatus.jsx — full-screen overlay shown while disconnected
export default function ConnectionStatus({ connected, hasData }) {
  if (connected && hasData) return null;

  return (
    <div className="fixed inset-0 z-50 flex flex-col items-center justify-center bg-[#020c14]">
      <div className="text-cyan-400 text-4xl tracking-widest font-bold mb-4">X.A.Z.E.L.</div>
      {!connected ? (
        <>
          <p className="text-red-400 text-sm tracking-widest mb-2">● CONNECTION LOST</p>
          <p className="text-slate-500 text-xs tracking-wider">Attempting to reconnect...</p>
        </>
      ) : (
        <>
          <p className="text-cyan-400 text-sm tracking-widest mb-2">CONNECTING TO X.A.Z.E.L....</p>
          <p className="text-slate-500 text-xs tracking-wider">Initializing telemetry stream...</p>
        </>
      )}
    </div>
  );
}