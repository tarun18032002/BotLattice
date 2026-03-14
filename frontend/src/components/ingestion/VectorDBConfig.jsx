import { VECTOR_DBS, VDB_DEFAULTS, DISTANCE_METRICS } from "../../constants/vectorDbs";
import { Input, Select, Toggle } from "../ui/FormControls";
import { Card, SectionTitle } from "../ui/Primitives";

export function VectorDBConfig({ config, onChange }) {
  const handleDBChange = (db) => {
    onChange({
      vectorDB: db,
      vdbHost:  VDB_DEFAULTS[db]?.host ?? "",
    });
  };

  const keyNote = VDB_DEFAULTS[config.vectorDB]?.keyNote ?? "Optional";

  return (
    <Card className="p-4">
      <SectionTitle>Vector Database</SectionTitle>

      <div className="grid grid-cols-2 gap-3 mb-3">
        <Select
          label="Database"
          options={VECTOR_DBS}
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
          placeholder="localhost:8000"
        />
        <Input
          label="API Key"
          type="password"
          placeholder={keyNote}
        />
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
    </Card>
  );
}
