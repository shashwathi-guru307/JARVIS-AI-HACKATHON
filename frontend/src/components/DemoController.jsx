/**
 * DemoController — only shown when DEMO_MODE is active.
 * Lets the presenter switch scenarios from the dashboard without restarting the server.
 */
import { useState, useEffect } from "react";
import { API_BASE_URL } from "../config";

const BASE = API_BASE_URL;

const SCENARIO_LABELS = {
  NORMAL:             { label: "NORMAL",             color: "emerald" },
  MACHINE_DEGRADATION:{ label: "MACHINE DEGRADATION", color: "amber"   },
  ENERGY_PEAK:        { label: "ENERGY PEAK",         color: "amber"   },
  SAFETY_WARNING:     { label: "SAFETY WARNING",      color: "orange"  },
  SECURITY_INCIDENT:  { label: "SECURITY INCIDENT",   color: "red"     },
  MULTI_RISK:         { label: "MULTI-RISK INCIDENT", color: "red"     },
  FULL_CRISIS:        { label: "FULL SYSTEM CRISIS",  color: "red"     },
  RECOVERY:           { label: "RECOVERY",            color: "emerald" },
};

export default function DemoController({ token }) {
  const [status,   setStatus]   = useState(null);
  const [loading,  setLoading]  = useState(false);
  const [message,  setMessage]  = useState(null);

  useEffect(() => {
    fetch(`${BASE}/demo/status`)
      .then(r => r.json())
      .then(setStatus)
      .catch(() => {});
  }, []);

  if (!status?.demo_mode) return null;

  const activate = async (scenario) => {
    setLoading(true);
    setMessage(null);
    try {
      const res = await fetch(`${BASE}/demo/scenario`, {
        method: "POST",
        headers: {
          "Content-Type": "application/json",
          ...(token ? { Authorization: `Bearer ${token}` } : {}),
        },
        body: JSON.stringify({ scenario }),
      });
      const data = await res.json();
      if (data.success) {
        setStatus(s => ({ ...s, current_scenario: data.scenario }));
        setMessage(`Scenario → ${data.scenario}`);
      } else {
        setMessage(data.detail ?? "Failed.");
      }
    } catch {
      setMessage("Demo endpoint unreachable.");
    } finally {
      setLoading(false);
      setTimeout(() => setMessage(null), 3000);
    }
  };

  const current = status.current_scenario ?? "NORMAL";

  return (
    <div className="border border-slate-700/60 rounded p-4 space-y-3">
      <div className="flex items-center gap-2">
        <span className="w-1.5 h-1.5 rounded-full bg-amber-400 animate-pulse" />
        <p className="text-[10px] tracking-widest text-amber-400/80">DEMO CONTROLLER</p>
      </div>

      <div className="grid grid-cols-2 sm:grid-cols-4 gap-1.5">
        {Object.entries(SCENARIO_LABELS).map(([key, meta]) => {
          const active = key === current;
          const colorMap = {
            emerald: active ? "border-emerald-500/70 bg-emerald-500/15 text-emerald-400" : "border-slate-700 text-slate-500 hover:text-emerald-400/70",
            amber:   active ? "border-amber-500/70 bg-amber-500/15 text-amber-400"       : "border-slate-700 text-slate-500 hover:text-amber-400/70",
            orange:  active ? "border-orange-500/70 bg-orange-500/15 text-orange-400"    : "border-slate-700 text-slate-500 hover:text-orange-400/70",
            red:     active ? "border-red-500/70 bg-red-500/15 text-red-400"             : "border-slate-700 text-slate-500 hover:text-red-400/70",
          };
          return (
            <button
              key={key}
              onClick={() => activate(key)}
              disabled={loading || active}
              className={`text-[9px] tracking-wider px-2 py-1.5 rounded border transition-colors
                          disabled:opacity-60 ${colorMap[meta.color]}`}
            >
              {meta.label}
            </button>
          );
        })}
      </div>

      {message && (
        <p className="text-[10px] text-cyan-400 tracking-wider">{message}</p>
      )}
    </div>
  );
}