import { DEFAULT_SYSTEM_PROMPT } from "../../constants/pipeline";
import { Card, SectionTitle, Button } from "../ui/Primitives";

export function SystemPromptEditor({ value, onChange }) {
  return (
    <Card className="p-4">
      <div className="flex items-center justify-between mb-4">
        <SectionTitle>System Prompt</SectionTitle>
        <Button
          variant="ghost"
          size="xs"
          onClick={() => onChange(DEFAULT_SYSTEM_PROMPT)}
        >
          Reset to default
        </Button>
      </div>

      <textarea
        value={value}
        onChange={(e) => onChange(e.target.value)}
        rows={7}
        className="
          w-full bg-[#161b25] border border-[rgba(255,255,255,0.06)] text-[#e8eaf0]
          text-[13px] px-3 py-2.5 rounded-[10px] outline-none
          focus:border-[rgba(0,229,160,0.4)] transition-colors resize-y leading-relaxed
        "
        style={{ fontFamily: "'IBM Plex Mono', monospace" }}
        spellCheck={false}
      />

      <p className="text-[11px] text-[#4d5669] mt-2">
        This prompt is prepended to every chat request. In RAG mode, collection context is appended automatically.
      </p>
    </Card>
  );
}
