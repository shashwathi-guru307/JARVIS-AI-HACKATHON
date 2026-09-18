import { Factory, Server, ShieldAlert, Wrench } from "lucide-react";

export default function PlantOperationsPanel({ incident, snapshot }) {
  const stats = [[Factory, "PLANT", "SMART MANUFACTURING"], [Server, "MACHINES", "M-101 ONLINE"], [ShieldAlert, "ACTIVE INCIDENTS", incident ? "01" : "00"], [Wrench, "PRODUCTION STATUS", incident ? "DEGRADED" : "OPERATIONAL"]];
  return <section className="mc-panel mc-plant"><div className="mc-section-heading"><div><span className="mc-kicker">PLANT OPERATIONS</span><h2>Assembly Line A</h2></div><span className="mc-tag">LIVE CONTEXT</span></div><div className="mc-plant-grid">{stats.map(([Icon, label, value]) => <div className="mc-plant-stat" key={label}><Icon size={15} /><span>{label}</span><strong>{value}</strong></div>)}</div><div className="mc-plant-bottom"><span>Correlated conditions</span><b>{snapshot?.correlated_conditions?.length ?? (incident ? 4 : 0)}</b><span>Machine criticality</span><b className="amber">HIGH</b></div></section>;
}
