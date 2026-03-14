import { Toggle, RangeInput } from "../ui/FormControls";
import { Card, SectionTitle } from "../ui/Primitives";

const TOGGLES = [
  {
    key: "reranking",
    label: "Re-ranking",
    sub: "Cross-encoder reranking of retrieved chunks before generation",
  },
  {
    key: "multiQuery",
    label: "Multi-query expansion",
    sub: "Generate query variants to improve recall across the collection",
  },
  {
    key: "compression",
    label: "Contextual compression",
    sub: "Extract only the relevant portion from each retrieved chunk",
  },
  {
    key: "showSources",
    label: "Show source citations",
    sub: "Display source chips under assistant responses in the chat",
  },
  {
    key: "streamResponses",
    label: "Stream responses",
    sub: "Display tokens as they arrive (requires streaming-compatible endpoint)",
  },
];

export function RetrievalSettings({ settings, onChange }) {
  return (
    <Card className="p-4">
      <SectionTitle>Retrieval Options</SectionTitle>

      <div className="space-y-0 mb-4">
        {TOGGLES.map(({ key, label, sub }) => (
          <Toggle
            key={key}
            checked={settings[key] ?? false}
            onChange={(v) => onChange({ [key]: v })}
            label={label}
            sub={sub}
          />
        ))}
      </div>

      <div className="space-y-3 pt-2 border-t border-[rgba(255,255,255,0.04)]">
        <RangeInput
          label="Default top-K"
          min={1} max={20} step={1}
          value={settings.defaultTopK}
          onChange={(v) => onChange({ defaultTopK: v })}
        />
        <RangeInput
          label="Similarity threshold"
          min={0} max={1} step={0.05}
          value={settings.simThreshold}
          onChange={(v) => onChange({ simThreshold: v })}
        />
      </div>
    </Card>
  );
}
