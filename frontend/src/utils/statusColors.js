// statusColors.js — one place for all status → color mappings
export const STATUS_COLORS = {
  NORMAL:   { text: 'text-emerald-400',  bg: 'bg-emerald-400/10', border: 'border-emerald-400/30', dot: 'bg-emerald-400' },
  WARNING:  { text: 'text-amber-400',    bg: 'bg-amber-400/10',   border: 'border-amber-400/30',   dot: 'bg-amber-400'   },
  CRITICAL: { text: 'text-red-400',      bg: 'bg-red-400/10',     border: 'border-red-400/30',     dot: 'bg-red-500'     },
  OFFLINE:  { text: 'text-slate-500',    bg: 'bg-slate-500/10',   border: 'border-slate-500/30',   dot: 'bg-slate-500'   },
};

/**
 * Centralized color mapping — one source of truth for all severity/risk colors.
 * Usage: const { text, border, bg, dot } = getStatusColors("CRITICAL")
 */
export function getStatusColors(status) {
  switch ((status ?? "").toUpperCase()) {
    case "CRITICAL":
    case "HIGH":
    case "DANGER":
      return {
        text:   "text-red-400",
        border: "border-red-500/30",
        bg:     "bg-red-500/10",
        dot:    "bg-red-500",
        badge:  "bg-red-500/20 text-red-400",
      };
    case "WARNING":
    case "MEDIUM":
    case "CAUTION":
      return {
        text:   "text-amber-400",
        border: "border-amber-500/30",
        bg:     "bg-amber-500/10",
        dot:    "bg-amber-400",
        badge:  "bg-amber-500/20 text-amber-400",
      };
    case "NORMAL":
    case "LOW":
    case "OPTIMAL":
    case "EXCELLENT":
    case "ONLINE":
    case "PROTECTED":
    case "OPERATIONAL":
      return {
        text:   "text-emerald-400",
        border: "border-emerald-500/30",
        bg:     "bg-emerald-500/10",
        dot:    "bg-emerald-400",
        badge:  "bg-emerald-500/20 text-emerald-400",
      };
    default:
      return {
        text:   "text-slate-400",
        border: "border-slate-700",
        bg:     "bg-slate-800/30",
        dot:    "bg-slate-500",
        badge:  "bg-slate-700 text-slate-400",
      };
  }
}