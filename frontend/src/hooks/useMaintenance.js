// useMaintenance.js — polls maintenance and digital-twin APIs
import { useState, useEffect } from "react";
import { API_BASE_URL } from "../config";

const BASE  = API_BASE_URL;
const POLL  = 5000;   // ms — matches backend PREDICTION_INTERVAL

export function useMaintenance() {
  const [prediction, setPrediction] = useState(null);
  const [history,    setHistory]    = useState([]);
  const [twin,       setTwin]       = useState(null);

  useEffect(() => {
    async function fetchAll() {
      try {
        const [statusRes, historyRes, twinRes] = await Promise.all([
          fetch(`${BASE}/maintenance/status`),
          fetch(`${BASE}/maintenance/history`),
          fetch(`${BASE}/digital-twin/MACHINE_01`),
        ]);
        if (statusRes.ok)  setPrediction(await statusRes.json());
        if (historyRes.ok) {
          const data = await historyRes.json();
          setHistory(data.history ?? []);
        }
        if (twinRes.ok)    setTwin(await twinRes.json());
      } catch {
        // backend unreachable — keep showing last known state
      }
    }

    fetchAll();
    const id = setInterval(fetchAll, POLL);
    return () => clearInterval(id);
  }, []);

  return { prediction, history, twin };
}