export function Topbar({ title, subtitle, actions }) {
  return (
    <div className="flex items-center justify-between px-6 py-3.5 border-b border-[rgba(255,255,255,0.06)] bg-[#0b0d11] flex-shrink-0">
      <div>
        <h1 className="text-[15px] font-semibold text-[#e8eaf0]">{title}</h1>
        {subtitle && <p className="text-[12px] text-[#4d5669] mt-0.5">{subtitle}</p>}
      </div>
      {actions && <div className="flex items-center gap-3">{actions}</div>}
    </div>
  );
}
