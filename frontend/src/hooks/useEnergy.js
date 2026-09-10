import { useState, useEffect, useRef } from "react";
import { createEnergySocket } from "../services/energy";

const MAX_ENERGY_HISTORY = 60;
const MAX_ENERGY_ALERTS  = 15;

export function useEnergy() {
  const [connected,    setConnected]    = useState(false);
  const [latest,       setLatest]       = useState(null);
  const [optimization, setOptimization] = useState(null);
  const [history,      setHistory]      = useState([]);
  const [alerts,       setAlerts]       = useState([]);
  const socketRef = useRef(null);

  useEffect(() => {
    const socket = createEnergySocket({
      onOpen:    () => setConnected(true),
      onClose:   () => setConnected(false),
      onError:   () => setConnected(false),
      onMessage: ({ metrics, optimization: opt }) => {
        setLatest(metrics);
        if (opt) setOptimization(opt);

        setHistory((prev) => {
          const point = {
            time:     new Date(metrics.timestamp).toLocaleTimeString(),
            demand:   metrics.current_demand_kw,
            solar:    metrics.solar_generation_kw,
            efficiency: metrics.efficiency_score,
          };
          const next = [...prev, point];
          return next.length > MAX_ENERGY_HISTORY ? next.slice(next.length - MAX_ENERGY_HISTORY) : next;
        });

        // Log energy alerts for non-optimal states
        if (opt && opt.optimization_status !== "OPTIMAL") {
          setAlerts((prev) => {
            const entry = {
              id:     Date.now(),
              time:   new Date(metrics.timestamp).toLocaleTimeString(),
              status: opt.optimization_status,
              action: opt.recommended_action,
              priority: opt.priority,
            };
            const next = [entry, ...prev];
            return next.length > MAX_ENERGY_ALERTS ? next.slice(0, MAX_ENERGY_ALERTS) : next;
          });
        }
      },
    });
    socketRef.current = socket;
    return () => socket.destroy();
  }, []);

  return { energyConnected: connected, latestEnergy: latest, optimization, energyHistory: history, energyAlerts: alerts };
}