import { Thermometer, Gauge, RotateCw, Wind, Droplets, BatteryCharging } from "lucide-react";

const PARAMS = [
  ["Temperature", "temperature", "°C", Thermometer],
  ["Vibration", "vibration", "g", Wind],
  ["RPM", "rpm", "RPM", RotateCw],
  ["Pressure", "pressure", "hPa", Gauge],
  ["Humidity", "humidity", "%", Droplets],
  ["Power", "battery", "%", BatteryCharging],
];

function stateFor(key, value) {
  if (value == null) return "WAITING";
  if (key === "temperature") return value >= 95 ? "CRITICAL" : value >= 85 ? "WARNING" : "NORMAL";
  if (key === "vibration") return value >= 0.9 ? "CRITICAL" : value >= 0.6 ? "WARNING" : "NORMAL";
  if (key === "rpm") return value > 2100 ? "WARNING" : "NORMAL";
  if (key === "battery") return value <= 10 ? "CRITICAL" : value <= 30 ? "WARNING" : "NORMAL";
  return "NORMAL";
}

export default function MachineHealthPanel({ telemetry, incident }) {
  return (
    <section className="mc-panel machine-panel">
      <div className="mc-section-heading"><div><span className="mc-kicker">MACHINE HEALTH</span><h2>M-101 <em>·</em> Assembly Line A</h2></div><span className={`mc-state ${incident ? "critical" : "green"}`}><i />{incident ? "CRITICAL" : "NORMAL"}</span></div>
      <div className="mc-machine-meta"><span>INDUSTRIAL ROTATING PRODUCTION MACHINE</span><span>CRITICALITY <b>HIGH</b></span></div>
      <div className="mc-parameter-grid">
        {PARAMS.map(([label, key, unit, Icon]) => {
          const value = telemetry?.[key];
          const state = stateFor(key, value);
          return <div className={`mc-parameter ${state.toLowerCase()}`} key={key}><Icon size={14} /><span className="mc-parameter-name">{label}</span><strong>{value == null ? "--" : Number(value).toFixed(key === "vibration" ? 2 : 1)} <small>{unit}</small></strong><span className="mc-parameter-state">{state === "WAITING" ? "NO DATA" : state}</span></div>;
        })}
      </div>
      <p className="mc-simulated-note">SIMULATED MANUFACTURING TELEMETRY · CONFIGURABLE DEMO THRESHOLDS</p>
    </section>
  );
}
