const WS_URL = "ws://localhost:8000/ws/safety";
const RECONNECT_DELAY_MS = 4000;

export function createSafetySocket({ onMessage, onOpen, onClose, onError }) {
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
      catch { console.error("Safety WS: invalid JSON"); }
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

export async function triggerEmergency(deviceId) {
  const res = await fetch("http://localhost:8000/safety/emergency", {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ device_id: deviceId, trigger: "MANUAL_SOS" }),
  });
  return res.json();
}

export async function resetEmergency() {
  const res = await fetch("http://localhost:8000/safety/emergency/reset", { method: "POST" });
  return res.json();
}