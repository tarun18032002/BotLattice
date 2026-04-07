import { TrashIcon } from "../ui/Icons";
import { Button } from "../ui/Primitives";

export function ChatControls({
  collections,
  collection,
  onCollectionChange,
  mode,
  onModeChange,
  topK,
  onTopKChange,
  onClear,
  agent,
  onAgentChange,
}) {
  return (
    <div className="flex items-center gap-4 px-5 py-2.5 border-b border-[rgba(255,255,255,0.04)] bg-[#0d1018] flex-shrink-0">
      {/* Collection selector */}
      <div className="flex items-center gap-2 flex-1 min-w-0">
        <span className="text-[11px] text-[#4d5669] uppercase tracking-widest font-medium whitespace-nowrap">
          Collection
        </span>
        <select
          value={collection}
          onChange={(e) => onCollectionChange(e.target.value)}
          className="bg-[#161b25] border border-[rgba(255,255,255,0.06)] text-[#e8eaf0] text-[12px] px-3 py-1.5 rounded-[10px] outline-none focus:border-[rgba(0,229,160,0.4)] transition-colors max-w-[220px] cursor-pointer"
          style={{
            backgroundImage: `url("data:image/svg+xml,%3Csvg xmlns='http://www.w3.org/2000/svg' width='12' height='8' viewBox='0 0 12 8'%3E%3Cpath d='M1 1l5 5 5-5' stroke='%238892a4' fill='none' stroke-width='1.5'/%3E%3C/svg%3E")`,
            backgroundRepeat: "no-repeat",
            backgroundPosition: "right 10px center",
            paddingRight: 28,
            appearance: "none",
          }}
        >
          <option value="">— select collection —</option>
          {/* Static Resume Collection */}
          <option value="resume">
            Resume (static · local)
          </option>
          <option value="prompt_guide">Prompt Guide (static · local) </option>
          {/* Dynamic Collections */}
          {collections.map((c) => (
            <option key={c.name} value={c.name}>
              {c.name} ({c.chunks} chunks · {c.db})
            </option>
          ))}
        </select>
      </div>

      {/* Mode toggle */}
      <div className="flex items-center gap-1 bg-[#161b25] border border-[rgba(255,255,255,0.06)] rounded-[10px] p-0.5 flex-shrink-0">
        {[
          { id: "rag",    label: "RAG mode" },
          { id: "direct", label: "Direct LLM" },
        ].map(({ id, label }) => (
          <button
            key={id}
            onClick={() => onModeChange(id)}
            disabled={agent !== "none"}
            className={`px-3 py-1 rounded-[8px] text-[11px] font-medium transition-all cursor-pointer
              disabled:opacity-30 disabled:cursor-not-allowed
              ${mode === id
                ? "bg-[rgba(0,229,160,0.12)] text-[#00e5a0]"
                : "text-[#4d5669] hover:text-[#8892a4]"
              }`}
          >
            {label}
          </button>
        ))}
      </div>

      {/* Agent selector */}
      <div className="flex items-center gap-2 flex-shrink-0">
        <span className="text-[11px] text-[#4d5669] uppercase tracking-widest font-medium whitespace-nowrap">
          Agent
        </span>
        <select
          value={agent}
          onChange={(e) => onAgentChange(e.target.value)}
          className="bg-[#161b25] border border-[rgba(255,255,255,0.06)] text-[#e8eaf0] text-[12px] px-3 py-1.5 rounded-[10px] outline-none focus:border-[rgba(0,229,160,0.4)] transition-colors cursor-pointer"
          style={{
            backgroundImage: `url("data:image/svg+xml,%3Csvg xmlns='http://www.w3.org/2000/svg' width='12' height='8' viewBox='0 0 12 8'%3E%3Cpath d='M1 1l5 5 5-5' stroke='%238892a4' fill='none' stroke-width='1.5'/%3E%3C/svg%3E")`,
            backgroundRepeat: "no-repeat",
            backgroundPosition: "right 10px center",
            paddingRight: 28,
            appearance: "none",
            borderColor: agent !== "none" ? "rgba(0,229,160,0.4)" : undefined,
            color: agent !== "none" ? "#00e5a0" : undefined,
          }}
        >
          <option value="none">— none —</option>
          <option value="prompt_builder">Prompt Builder</option>
        </select>
      </div>

      {/* Top-K slider */}
      <div className="flex items-center gap-2 flex-shrink-0">
        <span className="text-[11px] text-[#4d5669] whitespace-nowrap">Top-K</span>
        <input
          type="range"
          min={1}
          max={20}
          step={1}
          value={topK}
          onChange={(e) => onTopKChange(Number(e.target.value))}
          className="w-20 h-[3px] rounded-full cursor-pointer appearance-none bg-[#1d2535]"
          style={{ accentColor: "#00e5a0" }}
        />
        <span className="text-[11px] font-mono text-[#00e5a0] w-4 text-right">{topK}</span>
      </div>

      {/* Clear */}
      <Button
        variant="ghost"
        size="xs"
        onClick={onClear}
        icon={<TrashIcon />}
        className="flex-shrink-0"
      >
        Clear
      </Button>
    </div>
  );
}
