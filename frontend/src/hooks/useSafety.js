import { useState, useEffect, useRef } from "react";
import { createSafetySocket } from "../services/safety";

const MAX_TIMELINE = 20;

export function useSafety() {
  const [connected,    setConnected]    = useState(false);
  const [latest,       setLatest]       = useState(null);
  const [latestEvent,  setLatestEvent]  = useState(null);
  const [timeline,     setTimeline]     = useState([]);
  const socketRef = useRef(null);

  useEffect(() => {
    const socket = createSafetySocket({
      onOpen:    () => setConnected(true),
      onClose:   () => setConnected(false),
      onError:   () => setConnected(false),
      onMessage: ({ status, latest_event }) => {
        setLatest(status);
        if (latest_event) setLatestEvent(latest_event);

        setTimeline((prev) => {
          const entry = {
            id:        Date.now(),
            time:      new Date(status.timestamp).toLocaleTimeString(),
            risk:      status.overall_risk,
            score:     status.safety_score,
            emergency: status.emergency_status !== "NONE",
            label:     status.emergency_status !== "NONE"
              ? "EMERGENCY"
              : status.proximity_risk !== "NORMAL" && status.proximity_risk !== "LOW"
              ? "PROXIMITY WARNING"
              : status.environmental_risk !== "NORMAL" && status.environmental_risk !== "LOW"
              ? "ENVIRONMENT WARNING"
              : status.fatigue_indicator !== "NONE"
              ? "FATIGUE PATTERN"
              : status.inactivity_duration_seconds > 300
              ? "INACTIVITY"
              : "NORMAL",
          };
          const next = [entry, ...prev];
          return next.length > MAX_TIMELINE ? next.slice(0, MAX_TIMELINE) : next;
        });
      },
    });
    socketRef.current = socket;
    return () => socket.destroy();
  }, []);

  return { safetyConnected: connected, latestSafety: latest, latestSafetyEvent: latestEvent, timeline };
}