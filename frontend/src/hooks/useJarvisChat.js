/**
 * useJarvisChat — shared X.A.Z.E.L. agent pipeline for voice AND text input.
 *
 * Both voice transcripts and typed commands flow through this hook.
 * It fetches live system context before each call so the conversational
 * agent is always grounded in real data.
 */
import { useState, useCallback, useRef } from "react";
import { API_BASE_URL } from "../config";

const BASE = API_BASE_URL;
const MAX_HISTORY = 6; // turns kept for follow-up context

export function useJarvisChat(token) {
  const [messages,  setMessages]  = useState([]);   // [{role, content}]
  const [loading,   setLoading]   = useState(false);
  const [error,     setError]     = useState(null);
  const historyRef = useRef([]);

  const getHeaders = useCallback(() => ({
    "Content-Type": "application/json",
    ...(token ? { Authorization: `Bearer ${token}` } : {}),
  }), [token]);

  /** Fetch live system context snapshot */
  const fetchContext = useCallback(async () => {
    try {
      const res = await fetch(`${BASE}/agent/context`, { headers: getHeaders() });
      if (res.ok) {
        const data = await res.json();
        return data.context ?? "";
      }
    } catch {
      return "";
    }
    return "";
  }, [getHeaders]);

  /**
   * sendCommand — used by BOTH voice and text.
   * @param {string} command  The user's natural-language command
   * @param {string} mode     "chat" (default) | "analyze"
   */
  const sendCommand = useCallback(async (command, mode = "chat") => {
    if (!command?.trim()) return null;
    setLoading(true);
    setError(null);

    // Add user turn to display
    setMessages(prev => [...prev, { role: "user", content: command }]);

    try {
      // Fetch live context for grounding
      const systemContext = await fetchContext();

      const res = await fetch(`${BASE}/agent/analyze`, {
        method: "POST",
        headers: getHeaders(),
        body: JSON.stringify({
          message:              command,
          mode,
          system_context:       systemContext,
          conversation_history: historyRef.current,
        }),
      });

      const data = await res.json();

      if (data.status === "error") {
        const errMsg = data.error ?? "X.A.Z.E.L. encountered an error.";
        setError(errMsg);
        setMessages(prev => [...prev, { role: "assistant", content: errMsg }]);
        setLoading(false);
        return null;
      }

      // For chat mode, use the plain-language response field
      // For analyze mode, use narrative_answer
      const reply =
        mode === "chat"
          ? (data.response ?? data.narrative_answer ?? data.summary ?? "Analysis complete.")
          : (data.narrative_answer ?? data.summary ?? JSON.stringify(data));

      // Update conversation history for follow-up context (bounded)
      historyRef.current = [
        ...historyRef.current,
        { role: "user",      content: command },
        { role: "assistant", content: reply   },
      ].slice(-(MAX_HISTORY * 2));

      setMessages(prev => [...prev, { role: "assistant", content: reply }]);
      setLoading(false);
      return { reply, raw: data };

    } catch {
      const errMsg = "X.A.Z.E.L. backend is unavailable. Deterministic analysis continues.";
      setError(errMsg);
      setMessages(prev => [...prev, { role: "assistant", content: errMsg }]);
      setLoading(false);
      return null;
    }
  }, [fetchContext, getHeaders]);

  const clearHistory = useCallback(() => {
    historyRef.current = [];
    setMessages([]);
    setError(null);
  }, []);

  return {
    messages,
    loading,
    error,
    sendCommand,
    clearHistory,
  };
}