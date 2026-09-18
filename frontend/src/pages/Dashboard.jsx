/**
 * Dashboard.jsx — Final Day 10 + Voice Access unified command center.
 */
import { useState } from 'react';
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
import OfflineState          from '../components/OfflineState';
import VoiceAccessPanel      from '../components/VoiceAccessPanel';
import { useMaintenance }    from '../hooks/useMaintenance';
import { useEnergy }         from '../hooks/useEnergy';
import { useSafety }         from '../hooks/useSafety';
import { useSystemStatus }   from '../hooks/useSystemStatus';
import { getStatusColors }   from '../utils/statusColors';

export default function Dashboard({ connected, latest, history, alerts, streamStatus, security }) {
  const [incident, setIncident] = useState(null);
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

  return (
    <main className="p-4 sm:p-6 space-y-5 max-w-screen-xl mx-auto">

      {/* Demo controller */}
      <DemoController token={security?.token} onIncident={setIncident} />
      <section className="border border-slate-800 rounded p-4 grid grid-cols-2 md:grid-cols-4 gap-3">
        <div><p className="text-[9px] tracking-widest text-slate-600">PLANT</p><p className="text-xs text-slate-300 mt-1">Smart Manufacturing Plant</p></div>
        <div><p className="text-[9px] tracking-widest text-slate-600">PRODUCTION LINE</p><p className="text-xs text-slate-300 mt-1">Assembly Line A</p></div>
        <div><p className="text-[9px] tracking-widest text-slate-600">MACHINE</p><p className="text-xs text-slate-300 mt-1">M-101 · Rotating production machine</p></div>
        <div><p className="text-[9px] tracking-widest text-slate-600">CRITICALITY</p><p className="text-xs text-amber-400 mt-1">HIGH</p></div>
      </section>
      <IncidentResolution token={security?.token} incident={incident} onChange={setIncident} />

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
      <section className="grid grid-cols-2 sm:grid-cols-3 lg:grid-cols-6 gap-3">
        <TelemetryCard label="TEMPERATURE" value={t.temperature} unit="°C"  status={overallStatus} />
        <TelemetryCard label="HUMIDITY"    value={t.humidity}    unit="%"   status="NORMAL" />
        <TelemetryCard label="PRESSURE"    value={t.pressure}    unit="hPa" status="NORMAL" />
        <TelemetryCard label="VIBRATION"   value={t.vibration}   unit="g"   status={overallStatus} />
        <TelemetryCard label="RPM"         value={t.rpm}         unit="rpm" status={overallStatus} />
        <TelemetryCard label="BATTERY"     value={t.battery}     unit="%"   status="NORMAL" />
      </section>

      {/* Live charts */}
      <section className="grid grid-cols-1 md:grid-cols-3 gap-4">
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
      <section className="grid grid-cols-1 md:grid-cols-2 gap-4">
        <EnergyOverview   latest={latestEnergy} />
        <EnergyFlow       latest={latestEnergy} />
      </section>
      <section className="grid grid-cols-1 md:grid-cols-2 gap-4">
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
  );
}