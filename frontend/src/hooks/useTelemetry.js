// useTelemetry.js — single source of truth for live telemetry state
import { useState, useEffect, useRef } from 'react';
import { createTelemetrySocket } from '../services/websocket';

const MAX_HISTORY = 60;      // rolling window
const MAX_ALERTS  = 20;      // alert history entries

export function useTelemetry() {
  const [connected, setConnected]   = useState(false);
  const [latest, setLatest]         = useState(null);
  const [history, setHistory]       = useState([]);   // [{timestamp, temperature, vibration, rpm}]
  const [alerts, setAlerts]         = useState([]);   // [{time, status, reasons}]
  const socketRef = useRef(null);

  useEffect(() => {
    const socket = createTelemetrySocket({
      onOpen:    () => setConnected(true),
      onClose:   () => setConnected(false),
      onError:   () => setConnected(false),
      onMessage: (data) => {
        setLatest(data);

        // Rolling telemetry history for charts
        setHistory(prev => {
          const point = {
            timestamp:   new Date(data.timestamp).toLocaleTimeString(),
            temperature: data.telemetry?.temperature ?? 0,
            vibration:   data.telemetry?.vibration   ?? 0,
            rpm:         data.telemetry?.rpm         ?? 0,
          };
          const next = [...prev, point];
          return next.length > MAX_HISTORY ? next.slice(next.length - MAX_HISTORY) : next;
        });

        // Alert history — only log non-NORMAL events
        const status = data.analysis?.status;
        if (status && status !== 'NORMAL') {
          setAlerts(prev => {
            const entry = {
              id:      Date.now(),
              time:    new Date(data.timestamp).toLocaleTimeString(),
              status,
              reasons: data.analysis?.reasons ?? [],
              device:  data.device_id,
            };
            const next = [entry, ...prev];
            return next.length > MAX_ALERTS ? next.slice(0, MAX_ALERTS) : next;
          });
        }
      },
    });

    socketRef.current = socket;
    return () => socket.destroy();
  }, []);

  return { connected, latest, history, alerts };
}