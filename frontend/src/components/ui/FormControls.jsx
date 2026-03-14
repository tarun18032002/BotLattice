// ── Shared input base class ────────────────────────────────────────────────────

const inputBase =
  "bg-[#161b25] border border-[rgba(255,255,255,0.06)] text-[#e8eaf0] text-[13px] px-3 py-2 rounded-[10px] outline-none focus:border-[rgba(0,229,160,0.4)] placeholder:text-[#4d5669] transition-colors w-full";

const labelClass =
  "text-[11px] font-medium text-[#8892a4] uppercase tracking-widest";

// ── Input ─────────────────────────────────────────────────────────────────────

export const Input = ({ label, hint, className = "", ...props }) => (
  <div className={`flex flex-col gap-1.5 ${className}`}>
    {label && <label className={labelClass}>{label}</label>}
    <input {...props} className={inputBase} />
    {hint && <span className="text-[10px] text-[#4d5669]">{hint}</span>}
  </div>
);

// ── Select ────────────────────────────────────────────────────────────────────

export const Select = ({ label, options = [], className = "", ...props }) => (
  <div className={`flex flex-col gap-1.5 ${className}`}>
    {label && <label className={labelClass}>{label}</label>}
    <select
      {...props}
      className={`${inputBase} appearance-none cursor-pointer`}
      style={{
        backgroundImage: `url("data:image/svg+xml,%3Csvg xmlns='http://www.w3.org/2000/svg' width='12' height='8' viewBox='0 0 12 8'%3E%3Cpath d='M1 1l5 5 5-5' stroke='%238892a4' fill='none' stroke-width='1.5'/%3E%3C/svg%3E")`,
        backgroundRepeat: "no-repeat",
        backgroundPosition: "right 10px center",
        paddingRight: 28,
      }}
    >
      {options.map((o) => {
        const value = typeof o === "string" ? o : o.value;
        const label = typeof o === "string" ? o : o.label;
        return <option key={value} value={value}>{label}</option>;
      })}
    </select>
  </div>
);

// ── Toggle ────────────────────────────────────────────────────────────────────

export const Toggle = ({ checked, onChange, label, sub }) => (
  <div className="flex items-center justify-between py-2.5 border-b border-[rgba(255,255,255,0.04)] last:border-0">
    <div>
      <div className="text-[13px] text-[#e8eaf0]">{label}</div>
      {sub && <div className="text-[11px] text-[#4d5669] mt-0.5">{sub}</div>}
    </div>
    <div
      onClick={() => onChange(!checked)}
      className="relative cursor-pointer flex-shrink-0"
      style={{ width: 36, height: 20 }}
    >
      <div
        className="absolute inset-0 rounded-full transition-colors duration-200"
        style={{ background: checked ? "#00b87e" : "rgba(255,255,255,0.1)" }}
      />
      <div
        className="absolute top-[3px] w-[14px] h-[14px] rounded-full bg-white transition-transform duration-200"
        style={{ left: 3, transform: checked ? "translateX(16px)" : "translateX(0)" }}
      />
    </div>
  </div>
);

// ── RangeInput ────────────────────────────────────────────────────────────────

export const RangeInput = ({ label, min, max, step, value, onChange, unit = "" }) => (
  <div className="flex flex-col gap-2">
    {label && <label className={labelClass}>{label}</label>}
    <div className="flex items-center gap-3">
      <input
        type="range"
        min={min} max={max} step={step} value={value}
        onChange={(e) => onChange(Number(e.target.value))}
        className="flex-1 h-[3px] rounded-full cursor-pointer appearance-none bg-[#1d2535]"
        style={{ accentColor: "#00e5a0" }}
      />
      <span className="text-[12px] font-medium text-[#00e5a0] min-w-[40px] text-right font-mono">
        {value}{unit}
      </span>
    </div>
  </div>
);
