import { useStore }             from "../../store/useStore";
import { useCollections }       from "../../hooks/useCollections";
import { Topbar }               from "../layout/Topbar";
import { CollectionsTable }     from "./CollectionsTable";
import { Button, Card }         from "../ui/Primitives";
import { DatabaseIcon, PlusIcon, SpinnerIcon } from "../ui/Icons";

export function CollectionsPage() {
  const { dispatch } = useStore();
  const { collections, loading, error, refresh, removeCollection } = useCollections();

  const handleDelete = async (name) => {
    if (!window.confirm(`Delete collection "${name}"? This cannot be undone.`)) return;
    try {
      await removeCollection(name);
    } catch (err) {
      alert(`Failed to delete "${name}": ${err.message}`);
    }
  };

  const goToIngest = () => dispatch({ type: "SET_PAGE", payload: "ingest" });

  const totalChunks = collections.reduce((s, c) => s + (c.chunks ?? 0), 0);
  const uniqueDBs   = [...new Set(collections.map((c) => c.db))].join(", ") || "—";

  return (
    <div className="flex flex-col h-full overflow-hidden">
      <Topbar
        title="Collections"
        subtitle={
          loading
            ? "Loading…"
            : `${collections.length} collection${collections.length !== 1 ? "s" : ""} in ${uniqueDBs}`
        }
        actions={
          <div className="flex items-center gap-2">
            <Button variant="ghost" size="sm" onClick={refresh} disabled={loading}>
              {loading ? <SpinnerIcon size={12} /> : "↻"}&nbsp;Refresh
            </Button>
            <Button variant="primary" size="sm" onClick={goToIngest} icon={<PlusIcon />}>
              New ingestion
            </Button>
          </div>
        }
      />

      <div className="flex-1 overflow-y-auto p-5">
        {/* Error banner */}
        {error && (
          <div className="mb-4 px-4 py-3 rounded-[10px] bg-[rgba(255,85,119,0.08)] border border-[rgba(255,85,119,0.2)] text-[#ff5577] text-[12px]">
            ⚠ Could not load collections: {error.message}
            <button className="ml-3 underline" onClick={refresh}>Retry</button>
          </div>
        )}

        {/* Summary stats */}
        {collections.length > 0 && (
          <div className="grid grid-cols-4 gap-3 mb-5">
            {[
              { label: "Collections",  value: collections.length },
              { label: "Total vectors", value: totalChunks.toLocaleString() },
              { label: "Total docs",    value: collections.reduce((s, c) => s + (c.docs ?? 0), 0) },
              { label: "Vector DB",     value: uniqueDBs },
            ].map(({ label, value }) => (
              <div key={label} className="bg-[#161b25] border border-[rgba(255,255,255,0.06)] rounded-[10px] p-3">
                <div className="text-[18px] font-bold text-[#e8eaf0] font-mono leading-none">{value}</div>
                <div className="text-[11px] text-[#8892a4] mt-1">{label}</div>
              </div>
            ))}
          </div>
        )}

        <Card>
          {loading && collections.length === 0 ? (
            <div className="flex items-center justify-center py-20 gap-3 text-[#4d5669]">
              <SpinnerIcon size={18} /> <span className="text-[13px]">Loading collections…</span>
            </div>
          ) : collections.length === 0 ? (
            <EmptyCollections onGoToIngest={goToIngest} />
          ) : (
            <CollectionsTable collections={collections} onDelete={handleDelete} />
          )}
        </Card>
      </div>
    </div>
  );
}

function EmptyCollections({ onGoToIngest }) {
  return (
    <div className="flex flex-col items-center justify-center py-20 gap-4">
      <div className="w-14 h-14 rounded-2xl bg-[#161b25] border border-[rgba(255,255,255,0.06)] flex items-center justify-center text-[#4d5669]">
        <DatabaseIcon />
      </div>
      <p className="text-[14px] font-medium text-[#8892a4]">No collections yet</p>
      <p className="text-[12px] text-[#4d5669] max-w-xs text-center leading-relaxed">
        Run an ingestion pipeline to create your first collection.
      </p>
      <Button variant="outline" size="sm" onClick={onGoToIngest}>
        Go to Ingestion
      </Button>
    </div>
  );
}
