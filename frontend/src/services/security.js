const BASE = "http://localhost:8000";

export async function login(username, password) {
  const res = await fetch(`${BASE}/auth/login`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ username, password }),
  });
  if (!res.ok) throw new Error("Invalid credentials.");
  return res.json();
}

export async function fetchSecurityStatus(token) {
  const res = await fetch(`${BASE}/security/status`, {
    headers: token ? { Authorization: `Bearer ${token}` } : {},
  });
  if (!res.ok) throw new Error("Security status unavailable");
  return res.json();
}

export async function fetchSecurityHistory(token) {
  const res = await fetch(`${BASE}/security/history`, {
    headers: token ? { Authorization: `Bearer ${token}` } : {},
  });
  if (!res.ok) return { events: [] };
  return res.json();
}

export async function fetchTransactionSummary() {
  const res = await fetch(`${BASE}/transactions/summary`);
  if (!res.ok) return null;
  return res.json();
}

export async function fetchTransactionRisks(token) {
  const res = await fetch(`${BASE}/transactions/risk`, {
    headers: token ? { Authorization: `Bearer ${token}` } : {},
  });
  if (!res.ok) return { risks: [] };
  return res.json();
}