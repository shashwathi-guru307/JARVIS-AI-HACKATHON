/**
 * JarvisAIPanel — the "Ask J.A.R.V.I.S." panel.
 * Sends a natural-language question (or a pre-built system summary request)
 * to POST /agent/analyze and displays the narrative_answer.
 */
import { useState, useCallback } from "react";
import { API_BASE_URL } from "../config";

const BASE = API_BASE_URL;
const QUICK_QUESTIONS = [
  "How is the system doing right now?",
  "What is the biggest problem?",
  "Is the machine safe to operate?",
  "Why is the system risk high?",
  "What maintenance is recommended?",
  "Are there any security concerns?",
  "What caused the energy increase?",
];

export default function JarvisAIPanel({ token, snapshot }) {
  const [query,    setQuery]    = useState("");
  const [answer,   setAnswer]   = useState(null);
  const [loading,  setLoading]  = useState(false);
  const [error,    setError]    = useState(null);
  const [lastData, setLastData] = useState(null);

  const buildContext = useCallback(() => {
    if (!snapshot) return "";
    const d = snapshot.domain_risks ?? {};
    const c = (snapshot.correlated_conditions ?? []).join("; ");
    return (
      `System score: ${snapshot.system_score ?? "N/A"}. ` +
      `System risk: ${snapshot.system_risk ?? "N/A"}. ` +
      `Status: ${snapshot.system_status ?? "N/A"}. ` +
      `Machine risk: ${d.machine ?? "N/A"}. ` +
      `Energy risk: ${d.energy ?? "N/A"}. ` +
      `Safety risk: ${d.safety ?? "N/A"}. ` +
      `Security risk: ${d.security ?? "N/A"}. ` +
      `Transaction risk: ${d.transaction ?? "N/A"}. ` +
      (c ? `Correlated conditions: ${c}. ` : "") +
      `Active alerts: ${snapshot.active_alerts ?? 0}.`
    );
  }, [snapshot]);

  const ask = useCallback(
    async (question) => {
      const q = question ?? query.trim();
      if (!q) return;
      setLoading(true);
      setError(null);
      setAnswer(null);

      const context = buildContext();
      const message = context ? `${context}\n\n${q}` : q;

      try {
        const headers = {
          "Content-Type": "application/json",
          ...(token ? { Authorization: `Bearer ${token}` } : {}),
        };
        const res  = await fetch(`${BASE}/agent/analyze`, {
          method: "POST",
          headers,
          body: JSON.stringify({ message }),
        });
        const data = await res.json();
        setLastData(data);

        if (data.status === "error") {
          setError(data.error ?? "Analysis failed.");
        } else {
          setAnswer(data.narrative_answer ?? data.summary ?? "No narrative returned.");
        }
      } catch {
        setError("AI unavailable. Deterministic analysis is still running.");
      } finally {
        setLoading(false);
      }
    },
    [query, token, buildContext]
  );

  return (
    <div className="border border-slate-800 rounded p-4 space-y-3">
      <p className="text-[10px] tracking-widest text-slate-500">J.A.R.V.I.S. AI EXPLANATION</p>

      {/* Quick question chips */}
      <div className="flex flex-wrap gap-1">
        {QUICK_QUESTIONS.map((q) => (
          <button
            key={q}
            onClick={() => { setQuery(q); ask(q); }}
            disabled={loading}
            className="text-[9px] tracking-wide px-2 py-0.5 rounded border border-slate-700
                       text-slate-500 hover:text-cyan-400 hover:border-cyan-500/40 transition-colors
                       disabled:opacity-40"
          >
            {q}
          </button>
        ))}
      </div>

      {/* Free-text input */}
      <div className="flex gap-2">
        <input
          className="flex-1 bg-slate-900 border border-slate-700 rounded px-3 py-1.5
                     text-xs text-slate-300 placeholder:text-slate-600
                     focus:outline-none focus:border-cyan-500/60"
          placeholder="Ask J.A.R.V.I.S. anything about the system…"
          value={query}
          onChange={(e) => setQuery(e.target.value)}
          onKeyDown={(e) => e.key === "Enter" && ask()}
          disabled={loading}
        />
        <button
          onClick={() => ask()}
          disabled={loading || !query.trim()}
          className="px-3 py-1.5 rounded bg-cyan-500/20 text-cyan-400 text-xs tracking-wider
                     border border-cyan-500/40 hover:bg-cyan-500/30 transition-colors
                     disabled:opacity-40"
        >
          {loading ? "…" : "ASK"}
        </button>
      </div>

      {/* Answer / Error / Scores */}
      {loading && (
        <p className="text-cyan-400/70 text-xs tracking-wider animate-pulse">
          J.A.R.V.I.S. is analyzing…
        </p>
      )}
      {error && (
        <div className="border border-amber-500/30 bg-amber-500/10 rounded p-3 text-amber-400 text-xs">
          {error}
        </div>
      )}
      {answer && !loading && (
        <div className="border border-cyan-500/20 bg-cyan-500/5 rounded p-4 space-y-2">
          <p className="text-[9px] tracking-widest text-cyan-500/60">J.A.R.V.I.S. RESPONSE</p>
          <p className="text-sm text-slate-300 leading-relaxed">{answer}</p>

          {/* Key scores from the response */}
          {lastData && lastData.status === "success" && (
            <div className="grid grid-cols-4 gap-2 pt-2 border-t border-slate-800">
              {[
                ["RISK",       lastData.risk_level],
                ["CONFIDENCE", `${((lastData.confidence ?? 0) * 100).toFixed(0)}%`],
                ["SYS SCORE",  lastData.system_score ?? "—"],
                ["PRIORITY",   lastData.priority ?? "—"],
              ].map(([label, val]) => (
                <div key={label} className="text-center">
                  <p className="text-[9px] text-slate-600 tracking-wider">{label}</p>
                  <p className="text-[11px] text-slate-300 font-medium">{val}</p>
                </div>
              ))}
            </div>
          )}
        </div>
      )}
    </div>
  );
}