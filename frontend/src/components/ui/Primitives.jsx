// ── Badge ─────────────────────────────────────────────────────────────────────

const BADGE_STYLES = {
  default: "bg-white/5 text-[#8892a4] border-white/10",
  green:   "bg-[rgba(0,229,160,0.1)] text-[#00e5a0] border-[rgba(0,229,160,0.2)]",
  amber:   "bg-[rgba(255,184,77,0.1)] text-[#ffb84d] border-[rgba(255,184,77,0.2)]",
  red:     "bg-[rgba(255,85,119,0.1)] text-[#ff5577] border-[rgba(255,85,119,0.2)]",
  blue:    "bg-[rgba(77,158,255,0.1)] text-[#4d9eff] border-[rgba(77,158,255,0.2)]",
  running: "bg-[rgba(77,158,255,0.1)] text-[#4d9eff] border-[rgba(77,158,255,0.2)]",
};

export const Badge = ({ children, variant = "default" }) => (
  <span className={`inline-flex items-center gap-1 text-[10px] font-medium px-2 py-0.5 rounded-full border ${BADGE_STYLES[variant] ?? BADGE_STYLES.default}`}>
    {variant === "green"   && <span className="w-1.5 h-1.5 rounded-full bg-[#00e5a0]" />}
    {variant === "running" && <span className="w-1.5 h-1.5 rounded-full bg-[#4d9eff] animate-pulse" />}
    {children}
  </span>
);

// ── Button ────────────────────────────────────────────────────────────────────

const BTN_VARIANTS = {
  ghost:   "bg-white/5 border-white/10 text-[#8892a4] hover:bg-white/10 hover:text-[#e8eaf0]",
  primary: "bg-[#00e5a0] border-[#00e5a0] text-[#0b0d11] hover:bg-white hover:border-white font-semibold",
  danger:  "bg-[rgba(255,85,119,0.1)] border-[rgba(255,85,119,0.2)] text-[#ff5577] hover:bg-[rgba(255,85,119,0.2)]",
  outline: "bg-transparent border-[rgba(0,229,160,0.4)] text-[#00e5a0] hover:bg-[rgba(0,229,160,0.08)]",
};

const BTN_SIZES = {
  xs: "text-[11px] px-2.5 py-1",
  sm: "text-[12px] px-3 py-1.5",
  md: "text-[13px] px-4 py-2",
};

export const Button = ({ children, onClick, variant = "ghost", size = "sm", disabled, icon, className = "" }) => (
  <button
    onClick={onClick}
    disabled={disabled}
    className={`
      inline-flex items-center gap-1.5 font-medium transition-all duration-150
      rounded-[10px] cursor-pointer border select-none
      disabled:opacity-40 disabled:cursor-not-allowed
      ${BTN_SIZES[size]} ${BTN_VARIANTS[variant]} ${className}
    `}
  >
    {icon && icon}
    {children}
  </button>
);

// ── Card ──────────────────────────────────────────────────────────────────────

export const Card = ({ children, className = "", accent = false }) => (
  <div className={`bg-[#10131a] border ${accent ? "border-[rgba(0,229,160,0.15)]" : "border-[rgba(255,255,255,0.06)]"} rounded-[14px] ${className}`}>
    {children}
  </div>
);

// ── SectionTitle ──────────────────────────────────────────────────────────────

export const SectionTitle = ({ children, badge }) => (
  <div className="flex items-center gap-2 mb-4">
    <h3 className="text-[10px] font-semibold text-[#4d5669] uppercase tracking-[0.12em] whitespace-nowrap">{children}</h3>
    {badge && <Badge variant={badge.variant}>{badge.label}</Badge>}
    <div className="flex-1 h-px bg-[rgba(255,255,255,0.04)]" />
  </div>
);

// ── StatCard ──────────────────────────────────────────────────────────────────

export const StatCard = ({ value, label }) => (
  <div className="bg-[#161b25] border border-[rgba(255,255,255,0.06)] rounded-[10px] p-3">
    <div className="text-[22px] font-bold text-[#e8eaf0] font-mono leading-none">{value}</div>
    <div className="text-[11px] text-[#8892a4] mt-1">{label}</div>
  </div>
);
