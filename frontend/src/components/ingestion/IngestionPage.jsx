import { useIngestion }    from "../../hooks/useIngestion";
import { Topbar }          from "../layout/Topbar";
import { UploadZone }      from "./UploadZone";
import { ChunkingConfig }  from "./ChunkingConfig";
import { EmbeddingConfig } from "./EmbeddingConfig";
import { VectorDBConfig }  from "./VectorDBConfig";
import { PipelineLog }     from "./PipelineLog";
import { Badge, StatCard, Card, SectionTitle } from "../ui/Primitives";
import { Button }          from "../ui/Primitives";
import { Input, Select }   from "../ui/FormControls";
import { SpinnerIcon, ZapIcon } from "../ui/Icons";

const COLLECTION_MODES = ["Create new", "Append to existing", "Replace existing"];

export function IngestionPage() {
  const {
    files, addFiles, removeFile,
    ingestion, updateIngestion,
    running, run,
    logs, logRef,
    stats,
  } = useIngestion();

  return (
    <div className="flex flex-col h-full overflow-hidden">
      <Topbar
        title="Document Ingestion"
        subtitle="Configure pipeline · Upload · Embed · Index"
        actions={
          <>
            <Badge variant={running ? "running" : stats.docs > 0 ? "green" : "default"}>
              {running ? "running" : stats.docs > 0 ? "ready" : "idle"}
            </Badge>
            <Button
              variant="primary"
              size="md"
              onClick={run}
              disabled={running}
              icon={running ? <SpinnerIcon size={12} /> : <ZapIcon />}
            >
              {running ? "Running…" : "Run Ingestion"}
            </Button>
          </>
        }
      />

      <div className="flex-1 overflow-y-auto p-5 space-y-4">
        {/* Stats row */}
        <div className="grid grid-cols-4 gap-3">
          <StatCard value={stats.docs}       label="Documents uploaded" />
          <StatCard value={stats.chunks}     label="Chunks created" />
          <StatCard value={stats.embeddings} label="Embeddings generated" />
          <StatCard value={stats.time}       label="Last run" />
        </div>

        <div className="grid grid-cols-2 gap-4">
          {/* ── Left column ── */}
          <div className="space-y-4">
            <UploadZone files={files} onAdd={addFiles} onRemove={removeFile} />

            {/* Collection config */}
            <Card className="p-4">
              <SectionTitle>Collection</SectionTitle>
              <div className="grid grid-cols-2 gap-3">
                <Input
                  label="Collection name"
                  placeholder="my_knowledge_base"
                  value={ingestion.collectionName}
                  onChange={(e) => updateIngestion({ collectionName: e.target.value })}
                />
                <Select
                  label="Mode"
                  options={COLLECTION_MODES}
                  value={ingestion.collectionMode}
                  onChange={(e) => updateIngestion({ collectionMode: e.target.value })}
                />
                <Input label="Description" placeholder="What does this collection contain?" className="col-span-2" />
                <Input label="Tags" placeholder="prod, v2, legal (comma-separated)" className="col-span-2" />
              </div>
            </Card>

            <VectorDBConfig config={ingestion} onChange={updateIngestion} />
          </div>

          {/* ── Right column ── */}
          <div className="space-y-4">
            <ChunkingConfig  config={ingestion} onChange={updateIngestion} />
            <EmbeddingConfig config={ingestion} onChange={updateIngestion} />
          </div>
        </div>

        <PipelineLog logs={logs} logRef={logRef} />
      </div>
    </div>
  );
}
