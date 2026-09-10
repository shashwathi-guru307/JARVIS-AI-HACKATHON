import { useState } from "react";

export default function LoginScreen({ onLogin, error }) {
  const [username, setUsername] = useState("");
  const [password, setPassword] = useState("");

  function handleSubmit(e) {
    e.preventDefault();
    onLogin(username, password);
  }

  return (
    <div className="fixed inset-0 z-50 flex flex-col items-center justify-center bg-[#020c14]">
      <div className="border border-cyan-900/40 rounded p-8 w-80 space-y-6">
        <div className="text-center">
          <h1 className="text-2xl font-bold tracking-[0.3em] text-cyan-400">J.A.R.V.I.S.</h1>
          <p className="text-[10px] tracking-widest text-slate-500 mt-1">SECURE ACCESS</p>
        </div>

        <form onSubmit={handleSubmit} className="space-y-4">
          <div>
            <label className="text-[10px] tracking-widest text-slate-500 block mb-1">USERNAME</label>
            <input
              type="text"
              value={username}
              onChange={(e) => setUsername(e.target.value)}
              className="w-full bg-slate-900 border border-slate-700 rounded px-3 py-2 text-sm text-slate-300 focus:outline-none focus:border-cyan-500"
              autoComplete="username"
            />
          </div>
          <div>
            <label className="text-[10px] tracking-widest text-slate-500 block mb-1">PASSWORD</label>
            <input
              type="password"
              value={password}
              onChange={(e) => setPassword(e.target.value)}
              className="w-full bg-slate-900 border border-slate-700 rounded px-3 py-2 text-sm text-slate-300 focus:outline-none focus:border-cyan-500"
              autoComplete="current-password"
            />
          </div>

          {error && (
            <p className="text-red-400 text-[10px] tracking-widest text-center">{error}</p>
          )}

          <button
            type="submit"
            className="w-full py-2 text-xs tracking-widest border border-cyan-500/40 text-cyan-400 rounded hover:bg-cyan-500/10 transition-colors"
          >
            LOGIN
          </button>
        </form>

        <p className="text-[9px] text-slate-700 text-center">
          Demo: admin/admin123 · operator/operator123 · viewer/viewer123
        </p>
      </div>
    </div>
  );
}