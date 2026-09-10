/**
 * useVoiceAccess — complete voice access lifecycle management.
 *
 * OFF  → no microphone, no recognition, no background activity
 * ON   → speech recognition active, transcript sent to the shared agent
 *
 * Uses the Web Speech API (browser-native). Falls back gracefully when
 * the browser does not support it.
 */
import { useState, useEffect, useRef, useCallback } from "react";

const SpeechRecognition =
  typeof window !== "undefined"
    ? window.SpeechRecognition || window.webkitSpeechRecognition
    : null;

export const VOICE_STATES = {
  OFF:        "OFF",
  IDLE:       "IDLE",
  LISTENING:  "LISTENING",
  PROCESSING: "PROCESSING",
  EXECUTING:  "EXECUTING",
  SPEAKING:   "SPEAKING",
  ERROR:      "ERROR",
};

/**
 * @param {function} onTranscript  Called with the final transcript string
 * @param {boolean}  enabled       External enabled flag (e.g. from settings)
 */
export function useVoiceAccess({ onTranscript, enabled = true }) {
  const [voiceState, setVoiceState] = useState(VOICE_STATES.OFF);
  const [transcript, setTranscript] = useState("");
  const [error,      setError]      = useState(null);
  const [supported,  setSupported]  = useState(!!SpeechRecognition);

  const recognitionRef  = useRef(null);
  const isOnRef         = useRef(false);   // true while voice access is enabled
  const restartTimerRef = useRef(null);
  const synth           = useRef(typeof window !== "undefined" ? window.speechSynthesis : null);

  // ── TTS ────────────────────────────────────────────────────────────────────
  const speak = useCallback((text) => {
    if (!synth.current || !text) return;
    synth.current.cancel();
    const utter = new SpeechSynthesisUtterance(text);
    utter.rate   = 0.95;
    utter.pitch  = 0.9;
    utter.volume = 1.0;
    // Prefer a natural-sounding en-US voice
    const voices = synth.current.getVoices();
    const preferred = voices.find(v =>
      v.lang === "en-US" && (v.name.includes("Google") || v.name.includes("Daniel") || v.name.includes("Samantha"))
    ) ?? voices.find(v => v.lang.startsWith("en"));
    if (preferred) utter.voice = preferred;

    utter.onstart = () => setVoiceState(VOICE_STATES.SPEAKING);
    utter.onend   = () => {
      if (isOnRef.current) setVoiceState(VOICE_STATES.LISTENING);
      else                 setVoiceState(VOICE_STATES.OFF);
    };
    utter.onerror = () => {
      if (isOnRef.current) setVoiceState(VOICE_STATES.LISTENING);
    };
    synth.current.speak(utter);
  }, []);

  const stopSpeaking = useCallback(() => {
    synth.current?.cancel();
  }, []);

  // ── Speech recognition lifecycle ───────────────────────────────────────────
  const startListening = useCallback(() => {
    if (!SpeechRecognition || !isOnRef.current) return;
    if (recognitionRef.current) {
      try { recognitionRef.current.abort(); } catch (_) {}
    }

    const rec = new SpeechRecognition();
    rec.continuous      = false;
    rec.interimResults  = false;
    rec.lang            = "en-US";
    rec.maxAlternatives = 1;

    rec.onstart = () => setVoiceState(VOICE_STATES.LISTENING);

    rec.onresult = (event) => {
      const text = event.results?.[0]?.[0]?.transcript?.trim();
      if (!text) return;
      setTranscript(text);
      setVoiceState(VOICE_STATES.PROCESSING);
      onTranscript?.(text);
    };

    rec.onerror = (event) => {
      if (event.error === "not-allowed" || event.error === "service-not-allowed") {
        setError("Microphone access denied. Text input is still available.");
        setVoiceState(VOICE_STATES.ERROR);
        isOnRef.current = false;
        return;
      }
      if (event.error === "no-speech") {
        // no-speech is normal — just restart
        if (isOnRef.current) scheduleRestart();
        return;
      }
      setError(`Recognition error: ${event.error}`);
      if (isOnRef.current) scheduleRestart();
    };

    rec.onend = () => {
      // If voice is still ON and we're not speaking, restart listening
      if (isOnRef.current && voiceState !== VOICE_STATES.SPEAKING) {
        scheduleRestart();
      }
    };

    recognitionRef.current = rec;
    try {
      rec.start();
    } catch (e) {
      setError("Could not start speech recognition. Try refreshing.");
      setVoiceState(VOICE_STATES.ERROR);
    }
  }, [onTranscript]); // eslint-disable-line react-hooks/exhaustive-deps

  const scheduleRestart = useCallback(() => {
    clearTimeout(restartTimerRef.current);
    restartTimerRef.current = setTimeout(() => {
      if (isOnRef.current) startListening();
    }, 400);
  }, [startListening]);

  // ── Public ON/OFF toggle ───────────────────────────────────────────────────
  const turnOn = useCallback(() => {
    if (!SpeechRecognition) {
      setError("Speech recognition is not supported in this browser. Text input is still available.");
      setSupported(false);
      return;
    }
    setError(null);
    isOnRef.current = true;
    startListening();
  }, [startListening]);

  const turnOff = useCallback(() => {
    isOnRef.current = false;
    clearTimeout(restartTimerRef.current);
    stopSpeaking();
    try { recognitionRef.current?.abort(); } catch (_) {}
    recognitionRef.current = null;
    setVoiceState(VOICE_STATES.OFF);
    setTranscript("");
  }, [stopSpeaking]);

  // ── Cleanup on unmount ─────────────────────────────────────────────────────
  useEffect(() => {
    return () => {
      isOnRef.current = false;
      clearTimeout(restartTimerRef.current);
      try { recognitionRef.current?.abort(); } catch (_) {}
      synth.current?.cancel();
    };
  }, []);

  return {
    voiceState,
    transcript,
    error,
    supported,
    isOn: voiceState !== VOICE_STATES.OFF,
    turnOn,
    turnOff,
    speak,
    stopSpeaking,
    setVoiceState,
  };
}