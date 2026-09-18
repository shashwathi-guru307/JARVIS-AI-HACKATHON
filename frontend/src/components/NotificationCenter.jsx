import { ExternalLink, X } from "lucide-react";

export default function NotificationCenter({ notifications, onClose, onOpen }) {
  return (
    <div className="mc-popover mc-notifications" role="dialog" aria-label="Notifications">
      <div className="mc-popover-head"><div><span className="mc-kicker">NOTIFICATIONS</span><h2>{notifications.length ? `${notifications.length} operational alerts` : "No new notifications"}</h2></div><button type="button" className="mc-icon-button cursor-target" aria-label="Close notifications" onClick={onClose}><X size={15} /></button></div>
      {notifications.length === 0 ? <p className="mc-popover-empty">No new notifications.</p> : <div className="mc-notification-list">{notifications.map((item) => <button type="button" className="mc-notification cursor-target" key={item.id} onClick={() => onOpen?.(item)}><span className={`mc-notification-severity ${item.severity.toLowerCase()}`} /><span className="mc-notification-copy"><strong>{item.title}</strong><small>{item.source} · {item.time}</small></span><ExternalLink size={13} /></button>)}</div>}
    </div>
  );
}
