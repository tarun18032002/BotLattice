const s = "currentColor";
const n = "none";

export const UploadIcon   = () => <svg viewBox="0 0 20 20" fill={n} stroke={s} strokeWidth="1.5" className="w-4 h-4"><path d="M10 12V4M7 7l3-3 3 3"/><path d="M3 16h14"/></svg>;
export const ChatIcon     = () => <svg viewBox="0 0 20 20" fill={n} stroke={s} strokeWidth="1.5" className="w-4 h-4"><path d="M17 7H3a1 1 0 00-1 1v7a1 1 0 001 1h3l4 2 4-2h3a1 1 0 001-1V8a1 1 0 00-1-1z"/></svg>;
export const DatabaseIcon = () => <svg viewBox="0 0 20 20" fill={n} stroke={s} strokeWidth="1.5" className="w-4 h-4"><ellipse cx="10" cy="5" rx="7" ry="2.5"/><path d="M3 5v10c0 1.38 3.13 2.5 7 2.5s7-1.12 7-2.5V5"/><path d="M3 10c0 1.38 3.13 2.5 7 2.5s7-1.12 7-2.5"/></svg>;
export const SettingsIcon = () => <svg viewBox="0 0 20 20" fill={n} stroke={s} strokeWidth="1.5" className="w-4 h-4"><circle cx="10" cy="10" r="2.5"/><path d="M10 2v2M10 16v2M2 10h2M16 10h2M4.22 4.22l1.42 1.42M14.36 14.36l1.42 1.42M4.22 15.78l1.42-1.42M14.36 5.64l1.42-1.42"/></svg>;
export const FileIcon     = () => <svg viewBox="0 0 20 20" fill={n} stroke={s} strokeWidth="1.5" className="w-4 h-4"><path d="M12 2H5a1 1 0 00-1 1v14a1 1 0 001 1h10a1 1 0 001-1V7l-4-5z"/><polyline points="12 2 12 7 17 7"/></svg>;
export const SendIcon     = () => <svg viewBox="0 0 20 20" fill={s}              className="w-4 h-4"><path d="M2.5 2l16 8-16 8V12l11-2-11-2V2z"/></svg>;
export const TrashIcon    = () => <svg viewBox="0 0 20 20" fill={n} stroke={s} strokeWidth="1.5" className="w-4 h-4"><path d="M4 6h12M8 6V4h4v2M6 6v10a1 1 0 001 1h6a1 1 0 001-1V6"/></svg>;
export const BotIcon      = () => <svg viewBox="0 0 20 20" fill={n} stroke={s} strokeWidth="1.5" className="w-4 h-4"><rect x="3" y="6" width="14" height="11" rx="2"/><path d="M7 10h.01M13 10h.01M7 14h6"/><path d="M10 6V3M7 3h6"/></svg>;
export const UserIcon     = () => <svg viewBox="0 0 20 20" fill={n} stroke={s} strokeWidth="1.5" className="w-4 h-4"><circle cx="10" cy="7" r="3"/><path d="M3 17c0-3.31 3.13-6 7-6s7 2.69 7 6"/></svg>;
export const PlusIcon     = () => <svg viewBox="0 0 20 20" fill={n} stroke={s} strokeWidth="2"   className="w-4 h-4"><path d="M10 4v12M4 10h12"/></svg>;
export const ZapIcon      = () => <svg viewBox="0 0 20 20" fill={s}              className="w-3 h-3"><path d="M11 2L3 12h7l-1 6 9-10h-7l1-6z"/></svg>;
export const TerminalIcon = () => <svg viewBox="0 0 20 20" fill={n} stroke={s} strokeWidth="1.5" className="w-4 h-4"><rect x="2" y="3" width="16" height="14" rx="2"/><path d="M6 8l3 3-3 3M11 14h3"/></svg>;
export const SpinnerIcon  = ({ size = 12 }) => (
  <span
    style={{ width: size, height: size, borderWidth: 2 }}
    className="border-2 border-current border-t-transparent rounded-full inline-block animate-spin"
  />
);
