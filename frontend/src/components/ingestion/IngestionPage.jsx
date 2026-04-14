import { useIngestion } from "../../hooks/useIngestion";
import { useCollections } from "../../hooks/useCollections";

import { Topbar } from "../layout/Topbar";
import { UploadZone } from "./UploadZone";
import { ChunkingConfig } from "./ChunkingConfig";
import { EmbeddingConfig } from "./EmbeddingConfig";
import { VectorDBConfig } from "./VectorDBConfig";
import { PipelineLog } from "./PipelineLog";
import { Badge, StatCard, Card, SectionTitle } from "../ui/Primitives";
import { Button } from "../ui/Primitives";
import { Input, Select } from "../ui/FormControls";
import { SpinnerIcon, ZapIcon } from "../ui/Icons";

const COLLECTION_MODES = [
  { label: "Create new", value: "Create_new" },
  { label: "Append to existing", value: "Append_to_existing" },
  { label: "Replace existing", value: "Replace_existing" }
];

export function IngestionPage() {
  const {
    files,
    addFiles,
    removeFile,
    ingestion,
    updateIngestion,
    running,
    run,
    embeddingLoading,
    embeddingSaving,
    embeddingConfigured,
    embeddingEditing,
    beginEmbeddingEdit,
    cancelEmbeddingEdit,
    embeddingError,
    saveEmbedding,
    vectordbLoading,
    vectordbSaving,
    vectordbConfigured,
    vectordbEditing,
    beginVectordbEdit,
    cancelVectordbEdit,
    vectordbError,
    saveVectordb,
    logs,
    logRef,
    stats,
  } = useIngestion();

  const { collections, loading } = useCollections();

  // Helper to determine if we can run the pipeline
  const isRunDisabled = 
    running || 
    files.length === 0 || 
    !ingestion.collectionName;

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
              disabled={isRunDisabled}
              icon={running ? <SpinnerIcon size={12} /> : <ZapIcon />}
            >
              {running ? "Running…" : "Run Ingestion"}
            </Button>
          </>
        }
      />

      <div className="flex-1 overflow-y-auto p-5 space-y-4">
        {/* Stats */}
        <div className="grid grid-cols-4 gap-3">
          <StatCard value={stats.docs} label="Documents uploaded" />
          <StatCard value={stats.chunks} label="Chunks created" />
          <StatCard value={stats.embeddings} label="Embeddings generated" />
          <StatCard value={stats.time} label="Last run" />
        </div>

        <div className="grid grid-cols-2 gap-4">
          {/* LEFT */}
          <div className="space-y-4">
            <UploadZone files={files} onAdd={addFiles} onRemove={removeFile} />

            {/* COLLECTION */}
            <Card className="p-4">
              <SectionTitle>Collection</SectionTitle>

              <div className="grid grid-cols-2 gap-3">

                {/* MODE */}
                <Select
                  label="Mode"
                  options={COLLECTION_MODES}
                  value={ingestion.collectionMode}
                  onChange={(e) =>
                    updateIngestion({
                      collectionMode: e.target.value,
                      collectionName: "" // reset name when switching modes
                    })
                  }
                  className="col-span-2"
                />

                {/* CREATE NEW MODE */}
                {ingestion.collectionMode === "Create_new" && (
                  <Input
                    label="Collection name"
                    placeholder="my_knowledge_base"
                    value={ingestion.collectionName}
                    onChange={(e) =>
                      updateIngestion({ collectionName: e.target.value })
                    }
                    className="col-span-2"
                  />
                )}

                {/* APPEND / OVERWRITE MODE */}
                {ingestion.collectionMode !== "Create_new" && (
                  <div className="col-span-2 space-y-1">
                    <Select
                      label="Select existing collection"
                      options={[
                        { label: "Choose a collection...", value: "" },
                        ...collections.map((c) => ({
                          label: c.name,
                          value: c.name,
                        })),
                      ]}
                      value={ingestion.collectionName || ""}
                      onChange={(e) =>
                        updateIngestion({ collectionName: e.target.value })
                      }
                    />

                    {loading && (
                      <div className="text-xs text-gray-400 flex items-center gap-2">
                        <SpinnerIcon size={10} className="animate-spin" />
                        Loading collections...
                      </div>
                    )}
                  </div>
                )}

                {/* OPTIONAL INFO */}
                <Input
                  label="Description"
                  placeholder="Optional details..."
                  value={ingestion.Description || ""}
                  onChange={(e) =>
                    updateIngestion({ Description: e.target.value })
                  }
                  className="col-span-2"
                />

                <Input
                  label="Tags"
                  placeholder="e.g. documentation, legal"
                  value={ingestion.Tags || ""}
                  onChange={(e) =>
                    updateIngestion({ Tags: e.target.value })
                  }
                  className="col-span-2"
                />
              </div>
            </Card>

            <VectorDBConfig
              config={ingestion}
              onChange={updateIngestion}
              loading={vectordbLoading}
              saving={vectordbSaving}
              configured={vectordbConfigured}
              editing={vectordbEditing}
              error={vectordbError}
              onEdit={beginVectordbEdit}
              onCancel={cancelVectordbEdit}
              onSave={saveVectordb}
            />
          </div>

          {/* RIGHT */}
          <div className="space-y-4">
            <ChunkingConfig config={ingestion} onChange={updateIngestion} />
            <EmbeddingConfig
              config={ingestion}
              onChange={updateIngestion}
              loading={embeddingLoading}
              saving={embeddingSaving}
              configured={embeddingConfigured}
              editing={embeddingEditing}
              error={embeddingError}
              onEdit={beginEmbeddingEdit}
              onCancel={cancelEmbeddingEdit}
              onSave={saveEmbedding}
            />
          </div>
        </div>

        <PipelineLog logs={logs} logRef={logRef} />
      </div>
    </div>
  );
}