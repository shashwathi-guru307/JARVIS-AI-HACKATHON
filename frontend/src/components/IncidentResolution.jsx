import { useEffect, useState } from "react";
import { API_BASE_URL } from "../config";

const BASE = API_BASE_URL;

export default function IncidentResolution({ token, incident, onChange }) {
  const [busy, setBusy] = useState(false);
  const [error, setError] = useState(null);

  useEffect(() => {
    if (!incident?.incident_id) return undefined;
    const poll = async () => {
      const response = await fetch(`${BASE}/incidents/${incident.incident_id}`);
      if (response.ok) onChange(await response.json());
    };
    poll();
    const timer = setInterval(poll, 5000);
    return () => clearInterval(timer);
  }, [incident?.incident_id, onChange]);

  if (!incident) {
    return (
      <section className="border border-slate-800 rounded p-4">
        <p className="text-[10px] tracking-widest text-slate-500">AI-01 INCIDENT RESOLUTION</p>
        <p className="text-xs text-slate-600 mt-3">No active incident. Run the AI-01 machine incident scenario to begin.</p>
      </section>
    );
  }

  const request = async (action) => {
    setBusy(true);
    setError(null);
    try {
      const response = await fetch(`${BASE}/incidents/${incident.incident_id}/${action}`, {
        method: "POST",
        headers: token ? { Authorization: `Bearer ${token}` } : {},
      });
      const data = await response.json();
      if (!response.ok) throw new Error(data.detail ?? "Incident action failed.");
      onChange(data);
    } catch (err) {
      setError(err.message);
    } finally {
      setBusy(false);
    }
  };

  const impact = incident.operational_impact ?? {};
  const lifecycle = [
    ["1", "Detection"], ["2", "Correlation"], ["3", "Investigation"], ["4", "RCA"],
    ["5", "Impact"], ["6", "Priority"], ["7", "Remediation"], ["8", "Approval"],
    ["9", "Execution"], ["10", "Verification"], ["11", "Resolved"],
  ];
  const completed = incident.status === "RESOLVED" ? 11 : incident.status === "REMEDIATING" ? 8 : 7;
  return (
    <section className="border border-cyan-500/30 bg-cyan-500/[0.03] rounded p-4 space-y-4">
      <div className="flex items-center justify-between gap-3">
        <div>
          <p className="text-[10px] tracking-widest text-cyan-400">ACTIVE INCIDENT</p>
          <h2 className="text-base text-slate-200 mt-1">{incident.title}</h2>
          <p className="text-[10px] text-slate-600">{incident.incident_id}</p>
        </div>
        <div className="text-right text-[10px] tracking-wider">
          <p className="text-amber-400">{incident.status}</p>
          <p className="text-slate-500">{incident.severity} / {incident.priority}</p>
          <p className="text-slate-500">RISK {incident.risk_score}</p>
        </div>
      </div>

      <div className="overflow-x-auto">
        <div className="flex min-w-[700px] items-center gap-1">
          {lifecycle.map(([number, label], index) => (
            <div key={label} className={`flex-1 text-center border-b-2 pb-2 ${index < completed ? "border-cyan-400 text-cyan-400" : "border-slate-800 text-slate-600"}`}>
              <p className="text-[9px]">{number}</p><p className="text-[9px] tracking-wider mt-1">{label}</p>
            </div>
          ))}
        </div>
      </div>

      <div className="grid grid-cols-2 md:grid-cols-4 gap-3 border border-slate-800 rounded p-3">
        <div><p className="text-[9px] text-slate-600">MACHINE</p><p className="text-xs text-slate-300 mt-1">{incident.machine_id}</p></div>
        <div><p className="text-[9px] text-slate-600">LINE</p><p className="text-xs text-slate-300 mt-1">{incident.production_line}</p></div>
        <div><p className="text-[9px] text-slate-600">CRITICALITY</p><p className="text-xs text-amber-400 mt-1">{incident.machine_criticality}</p></div>
        <div><p className="text-[9px] text-slate-600">RELATED ALERTS</p><p className="text-xs text-cyan-400 mt-1">{incident.source_event_ids.length} signals</p></div>
      </div>

      <div className="grid grid-cols-1 md:grid-cols-2 gap-3">
        <div className="border border-slate-800 rounded p-3">
          <p className="text-[10px] tracking-widest text-slate-500">CORRELATED ALERTS</p>
          {incident.correlated_conditions.map((condition) => <p key={condition} className="text-xs text-slate-400 mt-1">• {condition}</p>)}
        </div>
        <div className="border border-slate-800 rounded p-3">
          <p className="text-[10px] tracking-widest text-slate-500">INVESTIGATION</p>
          <p className="text-xs text-slate-300 mt-1">{incident.probable_root_causes?.[0]}</p>
          <p className="text-[10px] text-cyan-400 mt-2">CONFIDENCE {Math.round((incident.root_cause_confidence ?? 0) * 100)}%</p>
          {incident.evidence?.map((item) => <p key={item} className="text-[10px] text-slate-500 mt-1">{item}</p>)}
        </div>
        <div className="border border-slate-800 rounded p-3">
          <p className="text-[10px] tracking-widest text-slate-500">IMPACT</p>
          <p className="text-xs text-slate-300 mt-1">{impact.operational_impact}</p>
          <p className="text-[10px] text-amber-400 mt-1">SAFETY: {impact.safety_impact}</p>
          <p className="text-[10px] text-slate-500 mt-1">URGENCY: {impact.urgency}</p>
        </div>
        <div className="border border-slate-800 rounded p-3">
          <p className="text-[10px] tracking-widest text-slate-500">REMEDIATION PLAN</p>
          <p className="text-xs text-slate-300 mt-1">{incident.recommended_remediation}</p>
          <p className="text-[10px] text-slate-500 mt-1">Approval: {incident.approval_status}</p>
          <p className="text-[10px] text-emerald-400 mt-1">SAFE SIMULATION ONLY</p>
        </div>
      </div>

      {incident.status === "AWAITING_APPROVAL" && (
        <div className="flex flex-wrap gap-2">
          <button onClick={() => request("approve")} disabled={busy} className="text-[10px] tracking-wider px-3 py-2 rounded border text-emerald-400 border-emerald-500/40">APPROVE REMEDIATION</button>
          <button onClick={() => request("reject")} disabled={busy} className="text-[10px] tracking-wider px-3 py-2 rounded border text-red-400 border-red-500/40">REJECT</button>
        </div>
      )}
      {incident.status === "APPROVED" && <button onClick={() => request("execute")} disabled={busy} className="text-[10px] tracking-wider px-3 py-2 rounded border text-cyan-400 border-cyan-500/40">EXECUTE SAFE SIMULATION</button>}
      {incident.status === "REMEDIATING" && <button onClick={() => request("verify")} disabled={busy} className="text-[10px] tracking-wider px-3 py-2 rounded border text-cyan-400 border-cyan-500/40">VERIFY RESULT</button>}

      {(incident.action_status !== "NOT_STARTED" || incident.verification_status !== "NOT_STARTED") && (
        <div className="border border-slate-800 rounded p-3 text-xs text-slate-400">
          <p className="text-[10px] tracking-widest text-slate-500">EXECUTION / VERIFICATION</p>
          <p className="mt-1">Action: {incident.action_status}</p>
          <p>Verification: {incident.verification_status}</p>
          {incident.verification_summary && <p className="text-slate-500 mt-1">{incident.verification_summary}</p>}
        </div>
      )}

      <div className="border border-slate-800 rounded p-3">
        <p className="text-[10px] tracking-widest text-slate-500">AUDIT TRAIL</p>
        <p className="text-[10px] text-slate-500 mt-1">{incident.audit_event_ids?.length ?? 0} auditable transitions recorded</p>
        <p className="text-[10px] text-slate-600 mt-1">{incident.audit_event_ids?.join("  •  ")}</p>
      </div>
      {error && <p className="text-xs text-red-400">{error}</p>}
    </section>
  );
}
