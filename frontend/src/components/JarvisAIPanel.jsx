/**
 * JarvisAIPanel — the "Ask J.A.R.V.I.S." panel.
 * Sends a natural-language question (or a pre-built system summary request)
 * to POST /agent/analyze and displays the narrative_answer.
 */
import { useState, useCallback } from "react";
import { API_BASE_URL } from "../config";
import MagicRings from "./MagicRings";

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
    <div className="relative overflow-hidden rounded border border-slate-800 bg-slate-950/80 min-h-[360px]">
      <div className="absolute inset-0 opacity-90" aria-hidden="true">
        <MagicRings
          color="#fc42ff"
          colorTwo="#42fcff"
          ringCount={6}
          speed={1.2}
          attenuation={12}
          lineThickness={2}
          baseRadius={0.38}
          radiusStep={0.12}
          scaleRate={0.12}
          opacity={0.9}
          noiseAmount={0.08}
          rotation={8}
          ringGap={1.5}
          fadeIn={0.75}
          fadeOut={0.55}
          hoverScale={1.2}
          parallax={0.05}
          clickBurst={true}
        />
      </div>

      <div className="relative z-10 space-y-3 p-4">
        <p className="text-[10px] tracking-[0.28rem] text-cyan-300/80">AI INCIDENT ENGINE</p>

        {/* Quick question chips */}
        <div className="flex flex-wrap gap-1">
          {QUICK_QUESTIONS.map((q) => (
            <button
              key={q}
              onClick={() => { setQuery(q); ask(q); }}
              disabled={loading}
              className="text-[9px] tracking-wide px-2 py-0.5 rounded border border-slate-700
                         text-slate-200/80 hover:text-cyan-300 hover:border-cyan-500/40 transition-colors
                         disabled:opacity-40 bg-slate-950/40 backdrop-blur-sm"
            >
              {q}
            </button>
          ))}
        </div>

        {/* Free-text input */}
        <div className="flex gap-2">
          <input
            className="flex-1 bg-slate-950/50 border border-slate-700/80 rounded px-3 py-1.5
                       text-xs text-slate-200 placeholder:text-slate-500
                       focus:outline-none focus:border-cyan-500/60 backdrop-blur-sm"
            placeholder="Ask J.A.R.V.I.S. anything about the system…"
            value={query}
            onChange={(e) => setQuery(e.target.value)}
            onKeyDown={(e) => e.key === "Enter" && ask()}
            disabled={loading}
          />
          <button
            onClick={() => ask()}
            disabled={loading || !query.trim()}
            className="px-3 py-1.5 rounded bg-cyan-500/20 text-cyan-300 text-xs tracking-wider
                       border border-cyan-500/40 hover:bg-cyan-500/30 transition-colors
                       disabled:opacity-40"
          >
            {loading ? "…" : "ASK"}
          </button>
        </div>

        {/* Answer / Error / Scores */}
        {loading && (
          <p className="text-cyan-300/80 text-xs tracking-wider animate-pulse">
            J.A.R.V.I.S. is analyzing incident patterns…
          </p>
        )}
        {error && (
          <div className="border border-amber-500/30 bg-amber-500/10 rounded p-3 text-amber-300 text-xs">
            {error}
          </div>
        )}
        {answer && !loading && (
          <div className="border border-cyan-500/20 bg-slate-950/60 rounded p-4 space-y-2 backdrop-blur-sm">
            <p className="text-[9px] tracking-[0.24rem] text-cyan-300/70">ENGINE RESPONSE</p>
            <p className="text-sm text-slate-200 leading-relaxed">{answer}</p>

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
                    <p className="text-[9px] text-slate-500 tracking-wider">{label}</p>
                    <p className="text-[11px] text-slate-200 font-medium">{val}</p>
                  </div>
                ))}
              </div>
            )}
          </div>
        )}
      </div>
    </div>
  );
}