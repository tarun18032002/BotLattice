import { CHUNK_STRATEGIES, getChunkControls } from "../../constants/pipeline";
import { Input, RangeInput } from "../ui/FormControls";
import { Card, SectionTitle } from "../ui/Primitives";

export function ChunkingConfig({ config, onChange }) {
  const controls = getChunkControls(config.chunkStrategy);

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
                onClick={() => onChange({ chunkStrategy: s.value })}
                className={`
                  text-left px-3 py-2 rounded-[10px] border text-[12px] transition-all cursor-pointer
                  ${active
                    ? "border-[rgba(0,229,160,0.4)] bg-[rgba(0,229,160,0.06)] text-[#00e5a0]"
                    : "border-[rgba(255,255,255,0.06)] text-[#8892a4] hover:border-[rgba(255,255,255,0.12)] hover:text-[#e8eaf0]"
                  }
                `}
              >
                <div className="font-medium">{s.label}</div>
                <div className="text-[10px] opacity-60 mt-0.5">{s.desc}</div>
              </button>
            );
          })}
        </div>
      </div>

      {/* Dynamic controls */}
      <div className="space-y-3">
        {controls.hasSize && (
          <RangeInput
            label="Chunk size (tokens)"
            min={64} max={2048} step={64}
            value={config.chunkSize}
            onChange={(v) => onChange({ chunkSize: v })}
          />
        )}
        {controls.hasOverlap && (
          <RangeInput
            label="Overlap (tokens)"
            min={0} max={500} step={10}
            value={config.chunkOverlap}
            onChange={(v) => onChange({ chunkOverlap: v })}
          />
        )}
        {controls.hasBuffer && (
          <RangeInput
            label="Buffer sentences (semantic)"
            min={1} max={10} step={1}
            value={config.bufferSize}
            onChange={(v) => onChange({ bufferSize: v })}
          />
        )}
        {controls.hasSeparator && (
          <Input
            label="Separators"
            value={config.separators}
            onChange={(e) => onChange({ separators: e.target.value })}
            placeholder="\n\n, \n, ., ,"
          />
        )}
        <Input
          label="Min chunk size (chars)"
          type="number"
          defaultValue={20}
          placeholder="20"
        />
      </div>
    </Card>
  );
}
