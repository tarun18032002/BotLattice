import { CHUNK_STRATEGIES } from "../../constants/pipeline";
import { useChunkingOptions } from "../../hooks/useChunkingOptions";
import { Input, RangeInput } from "../ui/FormControls";
import { Card, SectionTitle } from "../ui/Primitives";
import { useEffect, useRef } from "react";

export function ChunkingConfig({ config, onChange }) {
  const { fields, loading } = useChunkingOptions(config.chunkStrategy);
  // Track previous strategy to detect manual changes
  const prevStrategy = useRef(config.chunkStrategy);

  // ✅ Auto-apply defaults when fields load or strategy changes
  useEffect(() => {
    if (!fields.length) return;

    const updates = {};
    const strategyChanged = prevStrategy.current !== config.chunkStrategy;

    fields.forEach((f) => {
      // Apply defaults if:
      // 1. The value is missing (undefined) or invalid (0)
      // 2. OR the user just switched the strategy (reset to strategy-specific defaults)
      const isMissing = config[f.name] === undefined || config[f.name] === 0;
      
      if ((isMissing || strategyChanged) && f.default !== undefined) {
        updates[f.name] = f.default;
      }
    });

    if (Object.keys(updates).length > 0) {
      onChange(updates);
    }
    
    prevStrategy.current = config.chunkStrategy;
  }, [fields, config.chunkStrategy]); // Only trigger when fields fetch finishes or strategy changes

  return (
    <Card className="p-4">
      <SectionTitle>Chunking Strategy</SectionTitle>

      {/* Strategy grid selector */}
      <div className="mb-4">
        <label className="text-[11px] font-medium text-[#8892a4] uppercase tracking-widest block mb-2">
          Strategy
        </label>
        <div className="grid grid-cols-2 gap-1.5">
          {CHUNK_STRATEGIES.map((s) => {
            const active = config.chunkStrategy === s.value;
            return (
              <button
                key={s.value}
                type="button"
                onClick={() => onChange({ 
                  chunkStrategy: s.value
                })}
                className={`
                  text-left px-3 py-2 rounded-[10px] border text-[12px] transition-all cursor-pointer
                  ${
                    active
                      ? "border-[rgba(0,229,160,0.4)] bg-[rgba(0,229,160,0.06)] text-[#00e5a0]"
                      : "border-[rgba(255,255,255,0.06)] text-[#8892a4] hover:border-[rgba(255,255,255,0.12)] hover:text-[#e8eaf0]"
                  }
                `}
              >
                <div className="font-medium">{s.label}</div>
                <div className="text-[10px] opacity-60 mt-0.5">
                  {s.desc}
                </div>
              </button>
            );
          })}
        </div>
      </div>

      {/* ✅ Dynamic controls (API-driven) */}
      <div className="space-y-3">
        {loading && (
          <div className="text-xs text-gray-400">Loading options...</div>
        )}

        {!loading && fields.map((field) => {
          // Fallback to the default if the current config is empty/zero
          const value = config[field.name] || field.default || "";

          // 🔢 Number → Range slider
          if (field.type === "int" || field.type === "number") {
            return (
              <RangeInput
                key={field.name}
                label={`${field.label || field.name} ${field.required ? "*" : ""}`}
                min={field.min ?? 0}
                max={field.max ?? 2000}
                step={field.step ?? 1}
                value={Number(value)}
                onChange={(v) => onChange({ [field.name]: Number(v) })}
              />
            );
          }

          // 🔽 Select dropdown
          if (field.type === "select") {
            return (
              <div key={field.name}>
                <label className="text-[11px] text-[#8892a4] mb-1 block">
                  {field.label || field.name} {field.required && "*"}
                </label>
                <select
                  className="w-full p-2 rounded bg-[#0b0f17] border border-[rgba(255,255,255,0.1)] text-sm text-white"
                  value={value}
                  onChange={(e) => onChange({ [field.name]: e.target.value })}
                >
                  {field.options?.map((opt) => (
                    <option key={opt} value={opt}>{opt}</option>
                  ))}
                </select>
              </div>
            );
          }

          // 🔤 Default text input
          return (
            <Input
              key={field.name}
              label={`${field.label || field.name} ${field.required ? "*" : ""}`}
              value={value}
              onChange={(e) => onChange({ [field.name]: e.target.value })}
              placeholder={field.placeholder || ""}
            />
          );
        })}
      </div>
    </Card>
  );
}