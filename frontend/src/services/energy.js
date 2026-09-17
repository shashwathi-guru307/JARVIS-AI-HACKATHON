import { WS_BASE_URL } from "../config";

const WS_URL = `${WS_BASE_URL}/ws/energy`;
const RECONNECT_DELAY_MS = 4000;

export function createEnergySocket({ onMessage, onOpen, onClose, onError }) {
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
      catch { console.error("Energy WS: invalid JSON"); }
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