import { useEffect, useMemo, useState } from "react";
import { VECTOR_DBS, VDB_DEFAULTS, DISTANCE_METRICS } from "../../constants/vectorDbs";
import { fetchVectordbProviders } from "../../api/vectordb";
import { Input, Select, Toggle } from "../ui/FormControls";
import { Button, Badge, Card, SectionTitle } from "../ui/Primitives";

export function VectorDBConfig({
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
        const rows = await fetchVectordbProviders();
        if (!active) return;
        const map = rows.reduce((acc, row) => {
          acc[row.db] = {
            requiresApiKey: Boolean(row.requiresApiKey),
            showApiKey: row.showApiKey !== false,
            urlPlaceholder: row.urlPlaceholder,
          };
          return acc;
        }, {});
        setProviderMeta(map);
      } catch {
        // keep local defaults when backend metadata isn't available
      }
    })();

    return () => {
      active = false;
    };
  }, []);

  const dbOptions = useMemo(() => {
    if (!providerMeta) return VECTOR_DBS;
    return Object.keys(providerMeta).map((value) => ({
      value,
      label: value[0].toUpperCase() + value.slice(1),
    }));
  }, [providerMeta]);

  const handleDBChange = (db) => {
    const backendDefault = providerMeta?.[db]?.urlPlaceholder;
    onChange({
      vectorDB: db,
      vdbHost: backendDefault || VDB_DEFAULTS[db]?.host || "",
    });
  };

  const keyNote = VDB_DEFAULTS[config.vectorDB]?.keyNote ?? "Optional";
  const requiresApiKey = providerMeta
    ? Boolean(providerMeta[config.vectorDB]?.requiresApiKey)
    : ["pinecone"].includes(config.vectorDB);
  const showApiKey = providerMeta
    ? Boolean(providerMeta[config.vectorDB]?.showApiKey)
    : true;

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
        Vector Database
      </SectionTitle>

      {loading ? (
        <p className="text-[12px] text-[#8892a4]">Checking existing vector DB configuration...</p>
      ) : configured && !editing ? (
        <div className="space-y-3">
          <div className="grid grid-cols-2 gap-3 text-[12px] text-[#c8cfdd]">
            <div className="bg-[#161b25] border border-[rgba(255,255,255,0.06)] rounded-[10px] p-2.5">
              <div className="text-[#8892a4] text-[10px] uppercase tracking-widest">Database</div>
              <div className="mt-1">{config.vectorDB}</div>
            </div>
            <div className="bg-[#161b25] border border-[rgba(255,255,255,0.06)] rounded-[10px] p-2.5">
              <div className="text-[#8892a4] text-[10px] uppercase tracking-widest">Host / URL</div>
              <div className="mt-1 break-all">{config.vdbHost || "-"}</div>
            </div>
          </div>

          <div className="flex items-center gap-2">
            <Badge variant={config.hybridSearch ? "green" : "default"}>
              hybrid: {String(config.hybridSearch)}
            </Badge>
            <Badge variant={config.storeMeta ? "green" : "default"}>
              store meta: {String(config.storeMeta)}
            </Badge>
          </div>

          <Button variant="outline" size="sm" onClick={onEdit}>
            Edit vector DB
          </Button>
        </div>
      ) : (
        <>
          <div className="grid grid-cols-2 gap-3 mb-3">
            <Select
              label="Database"
              options={dbOptions}
              value={config.vectorDB}
              onChange={(e) => handleDBChange(e.target.value)}
            />
            <Select
              label="Distance metric"
              options={DISTANCE_METRICS}
              value={config.distanceMetric}
              onChange={(e) => onChange({ distanceMetric: e.target.value })}
            />
            <Input
              label="Host / URL"
              value={config.vdbHost}
              onChange={(e) => onChange({ vdbHost: e.target.value })}
              placeholder={providerMeta?.[config.vectorDB]?.urlPlaceholder || "localhost:6333"}
            />
            {showApiKey && (
              <Input
                label={requiresApiKey ? "API Key (required)" : "API Key (optional)"}
                type="password"
                placeholder={keyNote}
                value={config.vdbApiKey || ""}
                onChange={(e) => onChange({ vdbApiKey: e.target.value })}
              />
            )}
          </div>

          <Toggle
            checked={config.hybridSearch}
            onChange={(v) => onChange({ hybridSearch: v })}
            label="Hybrid search (BM25 + vector)"
            sub="Combine sparse lexical and dense semantic retrieval"
          />
          <Toggle
            checked={config.storeMeta}
            onChange={(v) => onChange({ storeMeta: v })}
            label="Store document metadata"
            sub="Attach source, page number, and timestamp to each chunk"
          />

          {error && <p className="mt-3 text-[12px] text-[#ff5577]">{error}</p>}

          <div className="mt-4 flex items-center gap-2">
            <Button variant="primary" size="sm" onClick={onSave} disabled={saving}>
              {saving ? "Saving..." : configured ? "Update DB" : "Connect DB"}
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
