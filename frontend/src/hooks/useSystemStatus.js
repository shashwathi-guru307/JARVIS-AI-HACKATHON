import { useState, useEffect } from "react";

const BASE   = "http://localhost:8000";
const POLL   = 5000;

export function useSystemStatus(token) {
  const [snapshot, setSnapshot] = useState(null);
  const [health,   setHealth]   = useState(null);

  useEffect(() => {
    const headers = token ? { Authorization: `Bearer ${token}` } : {};

    async function fetchAll() {
      try {
        const [sRes, hRes] = await Promise.all([
          fetch(`${BASE}/system/status`, { headers }),
          fetch(`${BASE}/system/health`,  { headers }),
        ]);
        if (sRes.ok) setSnapshot(await sRes.json());
        if (hRes.ok) setHealth(await hRes.json());
      } catch { /* backend unreachable */ }
    }

    fetchAll();
    const id = setInterval(fetchAll, POLL);
    return () => clearInterval(id);
  }, [token]);

  return { snapshot, health };
}