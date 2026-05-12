import { LLM_PROVIDERS, LLM_MODELS } from "../../constants/pipeline";
import { Input, Select, RangeInput } from "../ui/FormControls";
import { Card, SectionTitle } from "../ui/Primitives";

export function LLMSettings({ settings, onChange, providerMeta }) {
  const providers = providerMeta
    ? Object.entries(providerMeta).map(([value, meta]) => ({
        value,
        label: meta?.label || value[0].toUpperCase() + value.slice(1),
      }))
    : LLM_PROVIDERS;

  const modelsByProvider = providerMeta
    ? Object.fromEntries(
        Object.entries(providerMeta).map(([provider, meta]) => [provider, meta?.models || []])
      )
    : LLM_MODELS;

  const handleProviderChange = (provider) => {
    const models = modelsByProvider[provider] ?? [];
    onChange({ llmProvider: provider, llmModel: models[0] ?? "" });
  };

  return (
    <Card className="p-4">
      <SectionTitle>LLM Configuration</SectionTitle>
      <div className="space-y-3">
        <Select
          label="Provider"
          options={providers}
          value={settings.llmProvider}
          onChange={(e) => handleProviderChange(e.target.value)}
        />
        <Select
          label="Model"
          options={modelsByProvider[settings.llmProvider] ?? []}
          value={settings.llmModel}
          onChange={(e) => onChange({ llmModel: e.target.value })}
        />
        <Input
          label="API Key"
          type="password"
          placeholder="sk-ant-…"
          value={settings.apiKey ?? ""}
          onChange={(e) => onChange({ apiKey: e.target.value })}
          hint="⚠ Use a backend proxy in production — never expose keys client-side."
        />
        <RangeInput
          label="Temperature"
          min={0} max={1} step={0.05}
          value={settings.temperature}
          onChange={(v) => onChange({ temperature: v })}
        />
        <Input
          label="Max tokens"
          type="number"
          value={settings.maxTokens}
          onChange={(e) => onChange({ maxTokens: Number(e.target.value) })}
        />
      </div>
    </Card>
  );
}
