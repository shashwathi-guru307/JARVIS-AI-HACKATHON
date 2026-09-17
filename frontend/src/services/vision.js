// vision.js — REST helpers and WebSocket factory for vision data
import { API_BASE_URL, WS_BASE_URL } from "../config";

const BASE_URL = API_BASE_URL;
const WS_URL   = `${WS_BASE_URL}/ws/vision`;
const RECONNECT_DELAY_MS = 4000;

export async function fetchVisionStatus() {
  const res = await fetch(`${BASE_URL}/vision/status`);
  if (!res.ok) throw new Error("Vision status unavailable");
  return res.json();
}

export async function fetchLatestVision() {
  const res = await fetch(`${BASE_URL}/vision/latest`);
  if (!res.ok) throw new Error("Vision latest unavailable");
  return res.json();
}

export async function triggerVisionAnalyze() {
  const res = await fetch(`${BASE_URL}/vision/analyze`, { method: "POST" });
  if (!res.ok) throw new Error("Vision analyze failed");
  return res.json();
}

export function createVisionSocket({ onMessage, onOpen, onClose, onError }) {
  let ws = null;
  let reconnectTimer = null;
  let destroyed = false;

  function connect() {
    if (destroyed) return;
    ws = new WebSocket(WS_URL);

    ws.onopen  = () => { if (!destroyed) onOpen?.(); };
    ws.onclose = () => {
      if (destroyed) return;
      onClose?.();
      reconnectTimer = setTimeout(connect, RECONNECT_DELAY_MS);
    };
    ws.onerror = (err) => { onError?.(err); ws.close(); };
    ws.onmessage = (event) => {
      try { onMessage?.(JSON.parse(event.data)); }
      catch { console.error("Vision WS: invalid JSON"); }
    };
  }

  function destroy() {
    destroyed = true;
    clearTimeout(reconnectTimer);
    ws?.close();
  }

  connect();
  return { destroy };
}