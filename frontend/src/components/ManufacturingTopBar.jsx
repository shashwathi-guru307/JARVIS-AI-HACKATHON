import { Bell, Search, Settings2 } from "lucide-react";
import NotificationCenter from "./NotificationCenter";
import SettingsPanel from "./SettingsPanel";

export default function ManufacturingTopBar({ security, notifications, unreadCount, onNotificationToggle, settings, onSettingChange }) {
  const now = new Date();
  const date = now.toLocaleDateString("en-GB", { day: "2-digit", month: "short", year: "numeric" }).toUpperCase();
  const time = now.toLocaleTimeString("en-US", { hour: "2-digit", minute: "2-digit", second: "2-digit" });

  return (
    <header className="mc-topbar">
      <div className="mc-top-identity"><span className="mc-top-x">X</span><div><strong>X.A.Z.E.L.</strong><small>SMART MANUFACTURING</small></div></div>
      <div className="mc-clock"><span>{date}</span><strong>{time}</strong></div>
      <div className="mc-top-actions">
        <button type="button" aria-label="Search" className="cursor-target"><Search size={16} /></button>
        <div className="mc-top-popover-anchor"><button type="button" aria-label={`Notifications${unreadCount ? `, ${unreadCount} unread` : ""}`} className="cursor-target" onClick={onNotificationToggle}><Bell size={16} />{unreadCount > 0 && <b className="mc-notification-badge">{unreadCount}</b>}</button>{notifications?.open && <NotificationCenter notifications={notifications.items} onClose={notifications.close} onOpen={notifications.openItem} />}</div>
        <div className="mc-top-popover-anchor"><button type="button" aria-label="Settings" className="cursor-target" onClick={settings.toggle}><Settings2 size={16} /></button>{settings.open && <SettingsPanel settings={settings.values} onChange={onSettingChange} onClose={settings.close} />}</div>
        <div className="mc-operator"><span className="mc-avatar">{(security?.username ?? "OP").slice(0, 2).toUpperCase()}</span><div><strong>{security?.username ?? "Operator"}</strong><small>{security?.role ?? "OPERATIONS CONTROL"}</small></div></div>
      </div>
    </header>
  );
}
