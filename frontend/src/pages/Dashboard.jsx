/**
 * Dashboard.jsx — Final Day 10 + Voice Access unified command center.
 */
import { useEffect, useState } from 'react';
import TelemetryCard         from '../components/TelemetryCard';
import TelemetryChart        from '../components/TelemetryChart';
import AlertPanel            from '../components/AlertPanel';
import SystemStatus          from '../components/SystemStatus';
import DeviceInfo            from '../components/DeviceInfo';
import VisionPanel           from '../components/VisionPanel';
import DigitalTwin           from '../components/DigitalTwin';
import PredictiveMaintenance from '../components/PredictiveMaintenance';
import DegradationChart      from '../components/DegradationChart';
import EnergyOverview        from '../components/EnergyOverview';
import EnergyFlow            from '../components/EnergyFlow';
import EnergyForecast        from '../components/EnergyForecast';
import EnergyOptimization    from '../components/EnergyOptimization';
import SafetyOverview        from '../components/SafetyOverview';
import SafetyAlerts          from '../components/SafetyAlerts';
import SecurityOverview      from '../components/SecurityOverview';
import TransactionRisk       from '../components/TransactionRisk';
import SecurityAlerts        from '../components/SecurityAlerts';
import SystemCommand         from '../components/SystemCommand';
import UnifiedAlertCenter    from '../components/UnifiedAlertCenter';
import SystemTimeline        from '../components/SystemTimeline';
import JarvisAIPanel         from '../components/JarvisAIPanel';
import DemoController        from '../components/DemoController';
import IncidentResolution    from '../components/IncidentResolution';
import ManufacturingSidebar  from '../components/ManufacturingSidebar';
import ManufacturingTopBar   from '../components/ManufacturingTopBar';
import MachineHealthPanel    from '../components/MachineHealthPanel';
import LiveIncidentFeed      from '../components/LiveIncidentFeed';
import JarvisCorePanel       from '../components/JarvisCorePanel';
import PlantOperationsPanel  from '../components/PlantOperationsPanel';
import OfflineState          from '../components/OfflineState';
import VoiceAccessPanel      from '../components/VoiceAccessPanel';
import { useMaintenance }    from '../hooks/useMaintenance';
import { useEnergy }         from '../hooks/useEnergy';
import { useSafety }         from '../hooks/useSafety';
import { useSystemStatus }   from '../hooks/useSystemStatus';
import { getStatusColors }   from '../utils/statusColors';

export default function Dashboard({ connected, latest, history, alerts, streamStatus, security }) {
  const [incident, setIncident] = useState(null);
  const [activeSection, setActiveSection] = useState('Command Center');
  const [selectedParameter, setSelectedParameter] = useState(null);
  const t        = latest?.telemetry ?? {};
  const analysis = latest?.analysis  ?? {};
  const overallStatus = analysis.status ?? 'NORMAL';
  const colors        = getStatusColors(overallStatus);

  const { prediction, history: maintHistory, twin } = useMaintenance();
  const { latestEnergy, optimization, energyHistory, energyAlerts } = useEnergy();
  const { latestSafety, latestSafetyEvent, timeline } = useSafety();
  const { snapshot, health } = useSystemStatus(security?.token);

  const txRisks    = security?.txRisks  ?? [];
  const secHistory = security?.history  ?? [];
  const backendDown = !snapshot && !connected;

  const destinations = {
    TEMPERATURE: { section: 'Machine Health', target: 'machine-health', chart: 'temperature', label: 'Temperature', subtitle: 'M-101 Machine Health' },
    VIBRATION: { section: 'Machine Health', target: 'machine-health', chart: 'vibration', label: 'Vibration', subtitle: 'Mechanical Condition' },
    RPM: { section: 'Machine Health', target: 'machine-health', chart: 'rpm', label: 'RPM', subtitle: 'Machine Performance' },
    PRESSURE: { section: 'Plant Overview', target: 'telemetry-detail', chart: 'pressure', label: 'Pressure', subtitle: 'Operating Condition' },
    HUMIDITY: { section: 'Plant Overview', target: 'telemetry-detail', chart: 'humidity', label: 'Humidity', subtitle: 'Environment' },
    BATTERY: { section: 'Maintenance', target: 'energy-monitoring', chart: null, label: 'Power', subtitle: 'Energy Monitoring' },
  };

  const navigateTo = (section, parameter = null) => {
    const destination = parameter ? destinations[parameter] : null;
    const target = destination?.target ?? ({
      'Command Center': 'command-center', 'Plant Overview': 'plant-overview', 'Machine Health': 'machine-health',
      Incidents: 'incident-resolution', 'AI Investigation': 'incident-resolution', Maintenance: 'energy-monitoring',
      'Live Alerts': 'live-alerts', 'Audit Trail': 'incident-resolution', 'Voice Control': 'voice-control', Settings: 'system-monitor',
    }[section] ?? 'command-center');
    setActiveSection(destination?.section ?? section);
    setSelectedParameter(destination ?? null);
    requestAnimationFrame(() => document.getElementById(target)?.scrollIntoView({ behavior: 'smooth', block: 'start' }));
  };

  const openParameter = (label) => navigateTo(destinations[label].section, label);

  useEffect(() => {
    if (!selectedParameter?.chart) return;
    requestAnimationFrame(() => document.getElementById('parameter-detail')?.scrollIntoView({ behavior: 'smooth', block: 'start' }));
  }, [selectedParameter]);

  return (
    <div className="mc-shell">
      <ManufacturingSidebar activeSection={activeSection} onNavigate={navigateTo} />
      <div className="mc-workspace">
        <ManufacturingTopBar connected={connected} security={security} />
        <main className="mc-main" id="command-center">
          <section className="mc-context-bar">
            <div><span className="mc-kicker">MANUFACTURING PLANT</span><strong>Smart Manufacturing Plant</strong></div>
            <span className="mc-context-divider" />
            <div><span className="mc-kicker">PRODUCTION LINE</span><strong>Assembly Line A</strong></div>
            <span className="mc-context-divider" />
            <div><span className="mc-kicker">PRIMARY MACHINE</span><strong>M-101 <em>·</em> High criticality</strong></div>
            <div className="mc-context-purpose">MULTIPLE SIGNALS <b>→</b> ONE INCIDENT</div>
          </section>
          <div className="mc-breadcrumb"><button type="button" onClick={() => navigateTo('Command Center')}>COMMAND CENTER</button><span>/</span><strong>{activeSection.toUpperCase()}</strong>{selectedParameter && <><span>/</span><strong>M-101 / {selectedParameter.label.toUpperCase()}</strong></>}</div>

      {/* Demo controller */}
      <DemoController token={security?.token} onIncident={setIncident} />
      <section className="mc-command-grid" id="machine-health">
        <div className="mc-command-left"><JarvisCorePanel incident={incident} /><MachineHealthPanel telemetry={t} incident={incident} /></div>
        <LiveIncidentFeed incident={incident} alerts={alerts} />
      </section>
      <div id="incident-resolution"><IncidentResolution token={security?.token} incident={incident} onChange={setIncident} /></div>
      <div id="plant-overview"><PlantOperationsPanel incident={incident} snapshot={snapshot} /></div>

      {/* Unified command center / offline state */}
      {backendDown ? (
        <section className="grid grid-cols-1 md:grid-cols-2 gap-4">
          <OfflineState modules={health?.modules} />
        </section>
      ) : (
        <section className="grid grid-cols-1 md:grid-cols-2 gap-4">
          <SystemCommand snapshot={snapshot} />
        </section>
      )}

      {/* Anomaly banner */}
      {overallStatus !== 'NORMAL' && (
        <div className={`border ${colors.border} ${colors.bg} rounded px-4 py-2 flex items-center gap-3`}>
          <span className={`w-2 h-2 rounded-full ${colors.dot} animate-pulse`} />
          <span className={`text-xs tracking-widest font-bold ${colors.text}`}>
            {overallStatus} — {analysis.reasons?.[0] ?? analysis.summary ?? ''}
          </span>
        </div>
      )}

      {/* Telemetry cards */}
      <section className="grid grid-cols-2 sm:grid-cols-3 lg:grid-cols-6 gap-3" id="telemetry-detail">
        <TelemetryCard label="TEMPERATURE" value={t.temperature} unit="°C" status={overallStatus} subtitle="M-101 Machine Health" active={selectedParameter?.label === 'Temperature'} onOpen={() => openParameter('TEMPERATURE')} />
        <TelemetryCard label="HUMIDITY" value={t.humidity} unit="%" status="NORMAL" subtitle="Environment" active={selectedParameter?.label === 'Humidity'} onOpen={() => openParameter('HUMIDITY')} />
        <TelemetryCard label="PRESSURE" value={t.pressure} unit="hPa" status="NORMAL" subtitle="Operating Condition" active={selectedParameter?.label === 'Pressure'} onOpen={() => openParameter('PRESSURE')} />
        <TelemetryCard label="VIBRATION" value={t.vibration} unit="g" status={overallStatus} subtitle="Mechanical Condition" active={selectedParameter?.label === 'Vibration'} onOpen={() => openParameter('VIBRATION')} />
        <TelemetryCard label="RPM" value={t.rpm} unit="rpm" status={overallStatus} subtitle="Machine Performance" active={selectedParameter?.label === 'RPM'} onOpen={() => openParameter('RPM')} />
        <TelemetryCard label="BATTERY" value={t.battery} unit="%" status="NORMAL" subtitle="Energy Monitoring" active={selectedParameter?.label === 'Power'} onOpen={() => openParameter('BATTERY')} />
      </section>

      {/* Live charts */}
      {selectedParameter && selectedParameter.chart && <section className="mc-parameter-detail" id="parameter-detail" aria-live="polite"><div><span className="mc-kicker">M-101 / {selectedParameter.label.toUpperCase()} DETAIL</span><h2>{selectedParameter.label} trend and machine context</h2><p>Live value, historical trend, configurable threshold state, and related operational alerts.</p></div><TelemetryChart title={selectedParameter.label.toUpperCase()} data={history} dataKey={selectedParameter.chart} color="#5ee7f4" unit={selectedParameter.label === 'Vibration' ? 'g' : selectedParameter.label === 'RPM' ? 'rpm' : '°C'} /></section>}
      <section className="grid grid-cols-1 md:grid-cols-3 gap-4" id="live-alerts">
        <TelemetryChart title="TEMPERATURE" data={history} dataKey="temperature" color="#22d3ee" unit="°C"  />
        <TelemetryChart title="VIBRATION"   data={history} dataKey="vibration"   color="#f59e0b" unit="g"   />
        <TelemetryChart title="RPM"         data={history} dataKey="rpm"         color="#a78bfa" unit="rpm" />
      </section>

      {/* Day 5 — Digital Twin + Predictive */}
      <section className="grid grid-cols-1 md:grid-cols-3 gap-4">
        <DigitalTwin             twin={twin} />
        <PredictiveMaintenance   prediction={prediction} />
        <DegradationChart        history={maintHistory} />
      </section>

      {/* Day 6 — Energy */}
      <section className="grid grid-cols-1 md:grid-cols-2 gap-4" id="energy-monitoring">
        <EnergyOverview   latest={latestEnergy} />
        <EnergyFlow       latest={latestEnergy} />
      </section>
      <section className="grid grid-cols-1 md:grid-cols-2 gap-4" id="voice-control">
        <EnergyForecast     history={energyHistory} />
        <EnergyOptimization optimization={optimization} alerts={energyAlerts} />
      </section>

      {/* Day 7 — Safety */}
      <section className="grid grid-cols-1 md:grid-cols-2 gap-4">
        <SafetyOverview latest={latestSafety} />
        <SafetyAlerts   latest={latestSafety} latestEvent={latestSafetyEvent} timeline={timeline} />
      </section>

      {/* Day 8 — Security */}
      <section className="grid grid-cols-1 md:grid-cols-3 gap-4">
        <SecurityOverview
          status={security?.status}
          username={security?.username}
          role={security?.role}
          onLogout={security?.logout}
        />
        <TransactionRisk summary={security?.txSummary} risks={txRisks} />
        <SecurityAlerts  history={secHistory} />
      </section>

      {/* Voice Access + AI Panels (side by side on wide screens) */}
      <section className="grid grid-cols-1 md:grid-cols-2 gap-4">
        <VoiceAccessPanel token={security?.token} />
        <JarvisAIPanel    token={security?.token} snapshot={snapshot} />
      </section>

      {/* Unified Alert Center + Timeline */}
      <section className="grid grid-cols-1 md:grid-cols-2 gap-4">
        <UnifiedAlertCenter
          alerts={alerts}
          visionAlerts={[]}
          energyAlerts={energyAlerts}
          timeline={timeline}
          txRisks={txRisks}
          secHistory={secHistory}
        />
        <SystemTimeline
          snapshot={snapshot}
          alerts={alerts}
          timeline={timeline}
          secHistory={secHistory}
        />
      </section>

      {/* Legacy bottom row */}
      <section className="grid grid-cols-1 md:grid-cols-4 gap-4">
        <AlertPanel   latest={latest} alerts={alerts} />
        <DeviceInfo   latest={latest} />
        <SystemStatus connected={connected} latest={latest} streamStatus={streamStatus} />
        <VisionPanel />
      </section>

        </main>
      </div>
    </div>
  );
}