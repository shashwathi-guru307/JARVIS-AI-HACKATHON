import { BrainCircuit, ShieldCheck } from "lucide-react";

export default function JarvisCorePanel({ incident }) {
  return <section className="mc-panel mc-core"><div className="mc-orbit orbit-one" /><div className="mc-orbit orbit-two" /><div className="mc-core-grid" /><div className="mc-core-content"><div className="mc-core-rings"><div className="mc-core-ring ring-outer" /><div className="mc-core-ring ring-inner" /><div className="mc-core-node"><BrainCircuit size={22} /></div></div><p className="mc-core-brand">X.A.Z.E.L.</p><h2>AI INCIDENT ENGINE</h2><span className="mc-core-sub">SMART MANUFACTURING</span><div className="mc-core-active"><span className="mc-dot green" /> AI ENGINE <b>ACTIVE</b></div></div><div className="mc-core-foot"><span><ShieldCheck size={13} /> POLICY CONTROLLED</span><span>{incident ? "INCIDENT CONTEXT LOADED" : "MONITORING MACHINE SIGNALS"}</span></div></section>;
}
