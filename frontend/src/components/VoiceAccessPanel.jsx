/**
 * VoiceAccessPanel — J.A.R.V.I.S. voice access + conversational text panel.
 *
 * Voice and text share the same useJarvisChat pipeline.
 * Voice state machine: OFF → IDLE → LISTENING → PROCESSING → EXECUTING → SPEAKING → LISTENING → …
 */
import { useState, useCallback, useEffect, useRef } from "react";
import { useVoiceAccess, VOICE_STATES } from "../hooks/useVoiceAccess";
import { useJarvisChat }                from "../hooks/useJarvisChat";

const STATE_LABELS = {
  [VOICE_STATES.OFF]:        { label: "VOICE OFF",   color: "text-slate-500",  pulse: false },
  [VOICE_STATES.IDLE]:       { label: "READY",        color: "text-cyan-400",   pulse: false },
  [VOICE_STATES.LISTENING]:  { label: "LISTENING…",   color: "text-emerald-400",pulse: true  },
  [VOICE_STATES.PROCESSING]: { label: "THINKING…",    color: "text-amber-400",  pulse: true  },
  [VOICE_STATES.EXECUTING]:  { label: "ANALYZING…",   color: "text-amber-400",  pulse: true  },
  [VOICE_STATES.SPEAKING]:   { label: "SPEAKING…",    color: "text-cyan-400",   pulse: true  },
  [VOICE_STATES.ERROR]:      { label: "ERROR",        color: "text-red-400",    pulse: false },
};

const QUICK_COMMANDS = [
  "How is the system doing?",
  "What is the biggest problem?",
  "Is the machine safe?",
  "Check energy status",
  "Any security concerns?",
  "What maintenance is recommended?",
];

export default function VoiceAccessPanel({ token }) {
  const [textInput, setTextInput] = useState("");
  const [isVoiceOn, setIsVoiceOn] = useState(false);
  const bottomRef = useRef(null);
  const voiceRef = useRef(null);

  const { messages, loading, error: chatError, sendCommand, clearHistory } = useJarvisChat(token);

  // When the conversational agent replies, speak it and update the voice state
  const handleReply = useCallback(async (command) => {
    voiceRef.current?.setVoiceState(VOICE_STATES.EXECUTING);
    const result = await sendCommand(command, "chat");
    if (result?.reply && isVoiceOn) {
      voiceRef.current?.speak(result.reply);
    } else if (!isVoiceOn) {
      voiceRef.current?.setVoiceState(VOICE_STATES.OFF);
    }
  }, [isVoiceOn, sendCommand]);

  const voice = useVoiceAccess({
    onTranscript: handleReply,
  });
  useEffect(() => {
    voiceRef.current = voice;
  }, [voice]);

  // Sync voice on/off
  const toggleVoice = useCallback(() => {
    if (voice.isOn) {
      voice.turnOff();
      setIsVoiceOn(false);
    } else {
      voice.turnOn();
      setIsVoiceOn(true);
    }
  }, [voice]);

  // Text command submit (works regardless of voice state)
  const handleText = useCallback(async (cmd) => {
    const command = cmd ?? textInput.trim();
    if (!command || loading) return;
    setTextInput("");
    if (voice.voiceState !== VOICE_STATES.OFF) {
      voice.setVoiceState(VOICE_STATES.EXECUTING);
    }
    const result = await sendCommand(command, "chat");
    if (result?.reply && voice.isOn) {
      voice.speak(result.reply);
    }
  }, [textInput, loading, voice, sendCommand]);

  // Auto-scroll to latest message
  useEffect(() => {
    bottomRef.current?.scrollIntoView({ behavior: "smooth" });
  }, [messages]);

  const stateMeta = STATE_LABELS[voice.voiceState] ?? STATE_LABELS[VOICE_STATES.OFF];
  const voiceError = voice.error ?? chatError;

  return (
    <div className="border border-slate-800 rounded p-4 space-y-4">
      {/* ── Header ── */}
      <div className="flex items-center justify-between">
        <div className="flex items-center gap-2">
          <span className={`text-base ${stateMeta.color} ${stateMeta.pulse ? "animate-pulse" : ""}`}>🎙</span>
          <p className="text-[10px] tracking-widest text-slate-500">J.A.R.V.I.S. VOICE ACCESS</p>
        </div>
        <span className={`text-[10px] tracking-widest font-bold ${stateMeta.color} ${stateMeta.pulse ? "animate-pulse" : ""}`}>
          {stateMeta.label}
        </span>
      </div>

      {/* ── Voice toggle ── */}
      <button
        onClick={toggleVoice}
        disabled={!voice.supported && !voice.isOn}
        className={`w-full py-2 rounded border text-xs tracking-widest font-bold transition-all duration-200
          ${voice.isOn
            ? "border-red-500/60 bg-red-500/10 text-red-400 hover:bg-red-500/20"
            : "border-cyan-500/40 bg-cyan-500/10 text-cyan-400 hover:bg-cyan-500/20"
          } disabled:opacity-40 disabled:cursor-not-allowed`}
      >
        {voice.isOn ? "⬛  TURN OFF VOICE ACCESS" : "🎙  TURN ON VOICE ACCESS"}
      </button>

      {/* Browser not supported warning */}
      {!voice.supported && (
        <p className="text-[10px] text-amber-400 tracking-wider">
          ⚠ Speech recognition is not supported in this browser. Text input is fully available.
        </p>
      )}

      {/* Error */}
      {voiceError && (
        <div className="border border-amber-500/30 bg-amber-500/10 rounded px-3 py-2 text-amber-400 text-[10px] tracking-wide">
          {voiceError}
        </div>
      )}

      {/* ── Quick command chips ── */}
      <div className="flex flex-wrap gap-1">
        {QUICK_COMMANDS.map((q) => (
          <button
            key={q}
            onClick={() => handleText(q)}
            disabled={loading}
            className="text-[9px] tracking-wide px-2 py-0.5 rounded border border-slate-700
                       text-slate-500 hover:text-cyan-400 hover:border-cyan-500/40 transition-colors
                       disabled:opacity-40"
          >
            {q}
          </button>
        ))}
      </div>

      {/* ── Live transcript (voice) ── */}
      {voice.transcript && voice.isOn && (
        <div className="border border-slate-700 rounded px-3 py-2">
          <p className="text-[9px] text-slate-500 tracking-wider mb-1">RECOGNIZED</p>
          <p className="text-xs text-slate-300 italic">"{voice.transcript}"</p>
        </div>
      )}

      {/* ── Conversation history ── */}
      {messages.length > 0 && (
        <div className="space-y-2 max-h-60 overflow-y-auto">
          {messages.map((m, i) => (
            <div
              key={i}
              className={`rounded px-3 py-2 ${
                m.role === "user"
                  ? "bg-slate-800/60 text-right"
                  : "border border-cyan-500/20 bg-cyan-500/5"
              }`}
            >
              <p className={`text-[9px] tracking-widest mb-1 ${
                m.role === "user" ? "text-slate-500" : "text-cyan-500/60"
              }`}>
                {m.role === "user" ? "YOU" : "J.A.R.V.I.S."}
              </p>
              <p className={`text-xs leading-relaxed ${
                m.role === "user" ? "text-slate-400" : "text-slate-300"
              }`}>
                {m.content}
              </p>
            </div>
          ))}
          {loading && (
            <div className="border border-slate-700 rounded px-3 py-2">
              <p className="text-[9px] text-slate-500 tracking-widest mb-1">J.A.R.V.I.S.</p>
              <p className="text-[10px] text-cyan-400/70 animate-pulse">Processing…</p>
            </div>
          )}
          <div ref={bottomRef} />
        </div>
      )}

      {/* ── Text input ── */}
      <div className="flex gap-2">
        <input
          className="flex-1 bg-slate-900 border border-slate-700 rounded px-3 py-1.5
                     text-xs text-slate-300 placeholder:text-slate-600
                     focus:outline-none focus:border-cyan-500/60"
          placeholder={voice.isOn ? "Type or speak a command…" : "Type a command…"}
          value={textInput}
          onChange={(e) => setTextInput(e.target.value)}
          onKeyDown={(e) => e.key === "Enter" && handleText()}
          disabled={loading}
        />
        <button
          onClick={() => handleText()}
          disabled={loading || !textInput.trim()}
          className="px-3 py-1.5 rounded bg-cyan-500/20 text-cyan-400 text-xs tracking-wider
                     border border-cyan-500/40 hover:bg-cyan-500/30 transition-colors
                     disabled:opacity-40"
        >
          SEND
        </button>
      </div>

      {/* ── Clear conversation ── */}
      {messages.length > 0 && (
        <button
          onClick={clearHistory}
          className="text-[9px] text-slate-600 hover:text-slate-400 tracking-wider transition-colors"
        >
          Clear conversation
        </button>
      )}
    </div>
  );
}