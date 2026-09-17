// useVision.js — manages vision WebSocket state
import { useState, useEffect, useRef } from "react";
import { createVisionSocket } from "../services/vision";

const MAX_VISION_ALERTS = 10;

export function useVision(enabled) {
  const [connected, setConnected]     = useState(false);
  const [latest, setLatest]           = useState(null);
  const [visionAlerts, setVisionAlerts] = useState([]);
  const socketRef = useRef(null);

  useEffect(() => {
    if (!enabled) {
      socketRef.current?.destroy();
      socketRef.current = null;
      return;
    }

    const socket = createVisionSocket({
      onOpen:    () => setConnected(true),
      onClose:   () => setConnected(false),
      onError:   () => setConnected(false),
      onMessage: (data) => {
        setLatest(data);
        if (data.risk_level && data.risk_level !== "NORMAL") {
          setVisionAlerts((prev) => {
            const entry = {
              id:     Date.now(),
              time:   new Date(data.timestamp).toLocaleTimeString(),
              event:  data.event,
              risk:   data.risk_level,
              conf:   data.confidence,
            };
            const next = [entry, ...prev];
            return next.length > MAX_VISION_ALERTS ? next.slice(0, MAX_VISION_ALERTS) : next;
          });
        }
      },
    });

    socketRef.current = socket;
    return () => socket.destroy();
  }, [enabled]);

  return { visionConnected: enabled && connected, latestVision: latest, visionAlerts };
}