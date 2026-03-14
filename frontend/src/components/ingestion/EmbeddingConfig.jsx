import { EMBED_PROVIDERS, EMBED_MODELS } from "../../constants/embedModels";
import { Input, Select, RangeInput, Toggle } from "../ui/FormControls";
import { Card, SectionTitle } from "../ui/Primitives";

export function EmbeddingConfig({ config, onChange }) {
  const modelOptions = EMBED_MODELS[config.embedProvider] ?? [];

  const handleProviderChange = (provider) => {
    const models = EMBED_MODELS[provider] ?? [];
    onChange({ embedProvider: provider, embedModel: models[0] ?? "" });
  };

  return (
    <Card className="p-4">
      <SectionTitle>Embedding Model</SectionTitle>

      <div className="grid grid-cols-2 gap-3 mb-3">
        <Select
          label="Provider"
          options={EMBED_PROVIDERS}
          value={config.embedProvider}
          onChange={(e) => handleProviderChange(e.target.value)}
        />
        <Select
          label="Model"
          options={modelOptions}
          value={config.embedModel}
          onChange={(e) => onChange({ embedModel: e.target.value })}
        />
        <Input
          label="API Key"
          type="password"
          placeholder="sk-…"
          className="col-span-2"
        />
      </div>

      <RangeInput
        label="Batch size"
        min={1} max={256} step={1}
        value={config.batchSize}
        onChange={(v) => onChange({ batchSize: v })}
      />

      <div className="mt-3">
        <Toggle
          checked={config.normalizeEmbed}
          onChange={(v) => onChange({ normalizeEmbed: v })}
          label="Normalize embeddings"
          sub="L2-normalize all vectors before storing"
        />
        <Toggle
          checked={config.cacheEmbed}
          onChange={(v) => onChange({ cacheEmbed: v })}
          label="Cache embeddings"
          sub="Skip re-embedding unchanged documents"
        />
      </div>
    </Card>
  );
}
