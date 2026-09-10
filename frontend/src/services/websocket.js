// websocket.js — single WebSocket manager, not recreated on every render
const WS_URL = 'ws://localhost:8000/ws/telemetry';
const RECONNECT_DELAY_MS = 3000;

export function createTelemetrySocket({ onMessage, onOpen, onClose, onError }) {
  let ws = null;
  let reconnectTimer = null;
  let destroyed = false;

  function connect() {
    if (destroyed) return;

    ws = new WebSocket(WS_URL);

    ws.onopen = () => {
      if (destroyed) { ws.close(); return; }
      onOpen?.();
    };

    ws.onmessage = (event) => {
      try {
        const data = JSON.parse(event.data);
        onMessage?.(data);
      } catch {
        console.error('JARVIS WS: invalid JSON', event.data);
      }
    };

    ws.onclose = () => {
      if (destroyed) return;
      onClose?.();
      // Attempt reconnect after delay
      reconnectTimer = setTimeout(connect, RECONNECT_DELAY_MS);
    };

    ws.onerror = (err) => {
      onError?.(err);
      ws.close(); // triggers onclose → reconnect
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