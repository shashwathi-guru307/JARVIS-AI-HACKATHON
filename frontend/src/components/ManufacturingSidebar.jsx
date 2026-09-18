import { Activity, AlertTriangle, Bot, Factory, Gauge, History, LayoutDashboard, Mic, Settings, Wrench } from "lucide-react";

const ITEMS = [
  [LayoutDashboard, "Command Center"],
  [Factory, "Plant Overview"],
  [Gauge, "Machine Health"],
  [AlertTriangle, "Incidents"],
  [Bot, "AI Investigation"],
  [Wrench, "Maintenance"],
  [Activity, "Live Alerts"],
  [History, "Audit Trail"],
  [Mic, "Voice Control"],
  [Settings, "Settings"],
];

export default function ManufacturingSidebar({ activeSection = "Command Center", onNavigate }) {
  return (
    <aside className="mc-sidebar">
      <div className="mc-brand">
        <div className="mc-emblem"><span>J</span></div>
        <div>
          <p className="mc-brand-name">X.A.Z.E.L.</p>
          <p className="mc-brand-sub">SMART MANUFACTURING</p>
        </div>
      </div>
      <div className="mc-side-label">OPERATIONS CONSOLE</div>
      <nav className="mc-nav" aria-label="Manufacturing navigation">
        {ITEMS.map(([Icon, label], index) => (
          <button key={label} className={`mc-nav-item ${activeSection === label ? "active" : ""}`} type="button" onClick={() => onNavigate?.(label)}>
            <Icon size={15} strokeWidth={1.6} aria-hidden="true" />
            <span>{label}</span>
            {label === "Incidents" && <span className="mc-nav-count">{index === 3 ? "01" : ""}</span>}
          </button>
        ))}
      </nav>
      <div className="mc-side-footer">
        <div className="mc-side-footer-line"><span className="mc-dot green" /> All systems monitored</div>
        <div className="mc-side-footer-line muted">Prototype control surface</div>
      </div>
    </aside>
  );
}
