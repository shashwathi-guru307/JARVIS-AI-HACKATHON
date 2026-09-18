import { Bell, Search, Settings2 } from "lucide-react";

export default function ManufacturingTopBar({ connected, security }) {
  const now = new Date();
  const date = now.toLocaleDateString("en-GB", { day: "2-digit", month: "short", year: "numeric" }).toUpperCase();
  const time = now.toLocaleTimeString("en-US", { hour: "2-digit", minute: "2-digit", second: "2-digit" });

  return (
    <header className="mc-topbar">
      <div className="mc-status-capsule">
        <span className={`mc-dot ${connected ? "green" : "red"}`} />
        <span className="mc-top-label">SYSTEM STATUS</span>
        <strong>{connected ? "OPERATIONAL" : "OFFLINE"}</strong>
      </div>
      <div className="mc-clock"><span>{date}</span><strong>{time}</strong></div>
      <div className="mc-top-actions">
        <button type="button" aria-label="Search"><Search size={16} /></button>
        <button type="button" aria-label="Notifications"><Bell size={16} /><i /></button>
        <button type="button" aria-label="Settings"><Settings2 size={16} /></button>
        <div className="mc-operator"><span className="mc-avatar">{(security?.username ?? "OP").slice(0, 2).toUpperCase()}</span><div><strong>{security?.username ?? "Operator"}</strong><small>{security?.role ?? "OPERATIONS CONTROL"}</small></div></div>
      </div>
    </header>
  );
}
