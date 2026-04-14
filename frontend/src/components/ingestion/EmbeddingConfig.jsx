import { useEffect, useMemo, useState } from "react";
import { EMBED_PROVIDERS, EMBED_MODELS } from "../../constants/embedModels";
import { fetchEmbeddingProviders } from "../../api/embeddings";
import { Input, Select, RangeInput, Toggle } from "../ui/FormControls";
import { Button, Badge } from "../ui/Primitives";
import { Card, SectionTitle } from "../ui/Primitives";

export function EmbeddingConfig({
  config,
  onChange,
  loading,
  saving,
  configured,
  editing,
  error,
  onEdit,
  onCancel,
  onSave,
}) {
  const [providerMeta, setProviderMeta] = useState(null);

  useEffect(() => {
    let active = true;
    (async () => {
      try {
        const rows = await fetchEmbeddingProviders();
        if (!active) return;
        const map = rows.reduce((acc, row) => {
          acc[row.provider] = {
            models: row.models,
            requiresApiKey: Boolean(row.requiresApiKey),
          };
          return acc;
        }, {});
        setProviderMeta(map);
      } catch {
        // Keep local fallback constants when API is unavailable.
      }
    })();
    return () => {
      active = false;
    };
  }, []);

  const providers = useMemo(() => {
    if (!providerMeta) return EMBED_PROVIDERS;
    return Object.keys(providerMeta).map((value) => ({
      value,
      label: value[0].toUpperCase() + value.slice(1),
    }));
  }, [providerMeta]);

  const modelsByProvider = providerMeta
    ? Object.fromEntries(
        Object.entries(providerMeta).map(([provider, meta]) => [provider, meta.models])
      )
    : EMBED_MODELS;
  const modelOptions = modelsByProvider[config.embedProvider] ?? [];
  const requiresApiKey = providerMeta
    ? Boolean(providerMeta[config.embedProvider]?.requiresApiKey)
    : ["openai", "google"].includes(config.embedProvider);

  const handleProviderChange = (provider) => {
    const models = modelsByProvider[provider] ?? [];
    onChange({ embedProvider: provider, embedModel: models[0] ?? "" });
  };

  return (
    <Card className="p-4">
      <SectionTitle
        badge={
          configured && !editing
            ? { variant: "green", label: "configured" }
            : loading
              ? { variant: "running", label: "loading" }
              : { variant: "amber", label: "setup required" }
        }
      >
        Embedding Model
      </SectionTitle>

      {loading ? (
        <p className="text-[12px] text-[#8892a4]">Checking existing embedding configuration...</p>
      ) : configured && !editing ? (
        <div className="space-y-3">
          <div className="grid grid-cols-2 gap-3 text-[12px] text-[#c8cfdd]">
            <div className="bg-[#161b25] border border-[rgba(255,255,255,0.06)] rounded-[10px] p-2.5">
              <div className="text-[#8892a4] text-[10px] uppercase tracking-widest">Provider</div>
              <div className="mt-1">{config.embedProvider}</div>
            </div>
            <div className="bg-[#161b25] border border-[rgba(255,255,255,0.06)] rounded-[10px] p-2.5">
              <div className="text-[#8892a4] text-[10px] uppercase tracking-widest">Model</div>
              <div className="mt-1 break-all">{config.embedModel}</div>
            </div>
          </div>

          <div className="flex items-center gap-2">
            <Badge variant={config.normalizeEmbed ? "green" : "default"}>
              normalize: {String(config.normalizeEmbed)}
            </Badge>
            <Badge variant={config.cacheEmbed ? "green" : "default"}>
              cache: {String(config.cacheEmbed)}
            </Badge>
          </div>

          <Button variant="outline" size="sm" onClick={onEdit}>
            Edit embedding model
          </Button>
        </div>
      ) : (
        <>
          <div className="grid grid-cols-2 gap-3 mb-3">
            <Select
              label="Provider"
              options={providers}
              value={config.embedProvider}
              onChange={(e) => handleProviderChange(e.target.value)}
            />
            <Select
              label="Model"
              options={modelOptions}
              value={config.embedModel}
              onChange={(e) => onChange({ embedModel: e.target.value })}
            />
            {requiresApiKey && (
              <Input
                label="API Key (required)"
                type="password"
                placeholder="Enter API key"
                value={config.embedApiKey || ""}
                onChange={(e) => onChange({ embedApiKey: e.target.value })}
                hint="Leave empty only when reusing the same saved provider key."
                className="col-span-2"
              />
            )}
          </div>

          <RangeInput
            label="Batch size"
            min={1} max={1024} step={1}
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
              sub="Reuse cached vectors when supported by the provider"
            />
          </div>

          {error && (
            <p className="mt-3 text-[12px] text-[#ff5577]">{error}</p>
          )}

          <div className="mt-4 flex items-center gap-2">
            <Button variant="primary" size="sm" onClick={onSave} disabled={saving}>
              {saving ? "Saving..." : configured ? "Update model" : "Connect model"}
            </Button>
            {configured && (
              <Button variant="ghost" size="sm" onClick={onCancel} disabled={saving}>
                Cancel
              </Button>
            )}
          </div>
        </>
      )}
    </Card>
  );
}
