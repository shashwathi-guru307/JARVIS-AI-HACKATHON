import { useState, useEffect, useCallback } from "react";
import {
  login as apiLogin,
  fetchSecurityStatus,
  fetchSecurityHistory,
  fetchTransactionSummary,
  fetchTransactionRisks,
} from "../services/security";

const POLL_MS = 6000;

export function useSecurity() {
  const [token, setToken] = useState(
    () => sessionStorage.getItem("jarvis_token") || null
  );

  const [role, setRole] = useState(
    () => sessionStorage.getItem("jarvis_role") || null
  );

  const [username, setUsername] = useState(
    () => sessionStorage.getItem("jarvis_user") || null
  );

  const [status, setStatus] = useState(null);
  const [history, setHistory] = useState([]);
  const [txSummary, setTxSummary] = useState(null);
  const [txRisks, setTxRisks] = useState([]);
  const [loginError, setLoginError] = useState(null);

  const login = useCallback(async (user, pass) => {
    setLoginError(null);

    // Prevent empty login requests
    if (!user.trim() || !pass) {
      setLoginError("Please enter username and password.");
      return false;
    }

    try {
      const data = await apiLogin(user.trim(), pass);

      // Validate backend response
      if (!data?.access_token) {
        throw new Error("Authentication token was not returned.");
      }

      setToken(data.access_token);
      setRole(data.role);
      setUsername(data.username);

      sessionStorage.setItem("jarvis_token", data.access_token);
      sessionStorage.setItem("jarvis_role", data.role);
      sessionStorage.setItem("jarvis_user", data.username);

      return true;
    } catch (error) {
      console.error("Login error:", error);
      setLoginError(
        error?.message || "ACCESS DENIED — invalid credentials."
      );
      return false;
    }
  }, []);

  const logout = useCallback(() => {
    setToken(null);
    setRole(null);
    setUsername(null);
    setStatus(null);
    setHistory([]);
    setTxSummary(null);
    setTxRisks([]);

    sessionStorage.removeItem("jarvis_token");
    sessionStorage.removeItem("jarvis_role");
    sessionStorage.removeItem("jarvis_user");
  }, []);

  useEffect(() => {
    async function poll() {
      // Don't make protected API calls before login
      if (!token) {
        return;
      }

      try {
        const [s, h, ts, tr] = await Promise.all([
          fetchSecurityStatus(token),
          fetchSecurityHistory(token),
          fetchTransactionSummary(),
          fetchTransactionRisks(token),
        ]);

        if (s) setStatus(s);
        if (h) setHistory(h.events ?? []);
        if (ts) setTxSummary(ts);
        if (tr) setTxRisks(tr.risks ?? []);
      } catch (error) {
        console.warn("Security polling failed:", error);
      }
    }

    poll();

    const id = setInterval(poll, POLL_MS);

    return () => clearInterval(id);
  }, [token]);

  return {
    token,
    role,
    username,
    status,
    history,
    txSummary,
    txRisks,
    loginError,
    login,
    logout,
  };
}