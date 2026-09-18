import { useEffect, useState } from 'react';
import { useTelemetry }       from './hooks/useTelemetry';
import { useSecurity }        from './hooks/useSecurity';
import Dashboard              from './pages/Dashboard';
import ConnectionStatus       from './components/ConnectionStatus';
import LoginScreen            from './components/LoginScreen';
import { API_BASE_URL }       from './config';

const STATUS_URL = `${API_BASE_URL}/telemetry/status`;
const POLL_MS    = 5000;

export default function App() {
  const { connected, latest, history, alerts } = useTelemetry();
  const [streamStatus, setStreamStatus] = useState(null);
  const security = useSecurity();

  useEffect(() => {
    async function fetchStatus() {
      try {
        const res  = await fetch(STATUS_URL);
        const data = await res.json();
        setStreamStatus(data);
      } catch { /* backend unreachable */ }
    }
    fetchStatus();
    const id = setInterval(fetchStatus, POLL_MS);
    return () => clearInterval(id);
  }, []);

  // Show login if not authenticated
  if (!security.token) {
    return <LoginScreen onLogin={security.login} error={security.loginError} />;
  }

  return (
    <div className="min-h-screen">
      <ConnectionStatus connected={connected} hasData={!!latest} />
      <Dashboard
        connected={connected}
        latest={latest}
        history={history}
        alerts={alerts}
        streamStatus={streamStatus}
        security={security}
      />
    </div>
  );
}