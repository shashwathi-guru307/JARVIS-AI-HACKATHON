import { Settings2, X } from "lucide-react";

function Toggle({ label, checked, onChange }) {
  return <label className="mc-setting-row"><span>{label}</span><input type="checkbox" checked={checked} onChange={(event) => onChange(event.target.checked)} /><i aria-hidden="true" /></label>;
}

export default function SettingsPanel({ settings, onChange, onClose }) {
  return <div className="mc-popover mc-settings" role="dialog" aria-label="Settings">
    <div className="mc-popover-head"><div><span className="mc-kicker">SYSTEM SETTINGS</span><h2>X.A.Z.E.L. control surface</h2></div><button type="button" className="mc-icon-button cursor-target" aria-label="Close settings" onClick={onClose}><X size={15} /></button></div>
    <div className="mc-settings-section"><span className="mc-setting-label">DISPLAY</span><Toggle label="Animation" checked={settings.animation} onChange={(value) => onChange("animation", value)} /><Toggle label="Target cursor" checked={settings.targetCursor} onChange={(value) => onChange("targetCursor", value)} /><Toggle label="Compact density" checked={settings.compact} onChange={(value) => onChange("compact", value)} /></div>
    <div className="mc-settings-section"><span className="mc-setting-label">SAFETY</span><Toggle label="Safety monitoring" checked={settings.safetyVisible} onChange={(value) => onChange("safetyVisible", value)} /><Toggle label="Safety notifications" checked={settings.safetyNotifications} onChange={(value) => onChange("safetyNotifications", value)} /></div>
    <div className="mc-settings-section"><span className="mc-setting-label">VOICE</span><Toggle label="Voice access" checked={settings.voiceEnabled} onChange={(value) => onChange("voiceEnabled", value)} /></div>
    <div className="mc-settings-about"><Settings2 size={14} /><span>X.A.Z.E.L.<small>Smart Manufacturing Incident Resolution</small></span></div>
  </div>;
}
