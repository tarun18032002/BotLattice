/**
 * src/components/chat/WsStatusBadge.jsx
 *
 * Shows the live WebSocket connection state.
 * Displayed in the ChatPage topbar actions slot.
 */

import { WS_STATE } from "../../services/websocketService";

const CONFIG = {
  [WS_STATE.OPEN]:       { dot: "bg-[#00e5a0]",                   text: "connected",    label: "text-[#00e5a0]" },
  [WS_STATE.CONNECTING]: { dot: "bg-[#4d9eff] animate-pulse",     text: "connecting…",  label: "text-[#4d9eff]" },
  [WS_STATE.CLOSED]:     { dot: "bg-[#ffb84d] animate-pulse",     text: "reconnecting", label: "text-[#ffb84d]" },
  [WS_STATE.ERROR]:      { dot: "bg-[#ff5577]",                   text: "error",        label: "text-[#ff5577]" },
};

export function WsStatusBadge({ wsState }) {
  const cfg = CONFIG[wsState] ?? CONFIG[WS_STATE.CLOSED];

  return (
    <div className="flex items-center gap-2 bg-[#161b25] border border-[rgba(255,255,255,0.06)] rounded-full px-3 py-1">
      <span className={`w-1.5 h-1.5 rounded-full flex-shrink-0 ${cfg.dot}`} />
      <span className={`text-[11px] font-medium ${cfg.label}`}>
        ws — {cfg.text}
      </span>
    </div>
  );
}
