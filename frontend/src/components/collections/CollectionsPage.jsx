import { useStore }           from "../../store/useStore";
import { Topbar }             from "../layout/Topbar";
import { CollectionsTable }   from "./CollectionsTable";
import { Button, Card }       from "../ui/Primitives";
import { DatabaseIcon, PlusIcon } from "../ui/Icons";

export function CollectionsPage() {
  const { state, dispatch } = useStore();
  const { collections } = state;

  const deleteCollection = (name) =>
    dispatch({ type: "DELETE_COLLECTION", payload: name });

  const goToIngest = () =>
    dispatch({ type: "SET_PAGE", payload: "ingest" });

  return (
    <div className="flex flex-col h-full overflow-hidden">
      <Topbar
        title="Collections"
        subtitle={`${collections.length} collection${collections.length !== 1 ? "s" : ""} indexed`}
        actions={
          <Button variant="primary" size="sm" onClick={goToIngest} icon={<PlusIcon />}>
            New ingestion
          </Button>
        }
      />

      <div className="flex-1 overflow-y-auto p-5">
        {/* Summary stats */}
        {collections.length > 0 && (
          <div className="grid grid-cols-4 gap-3 mb-5">
            {[
              { label: "Collections",    value: collections.length },
              { label: "Total chunks",   value: collections.reduce((s, c) => s + c.chunks, 0).toLocaleString() },
              { label: "Total documents",value: collections.reduce((s, c) => s + (c.docs ?? 0), 0) },
              { label: "Vector DBs",     value: [...new Set(collections.map((c) => c.db))].join(", ") || "—" },
            ].map(({ label, value }) => (
              <div key={label} className="bg-[#161b25] border border-[rgba(255,255,255,0.06)] rounded-[10px] p-3">
                <div className="text-[18px] font-bold text-[#e8eaf0] font-mono leading-none">{value}</div>
                <div className="text-[11px] text-[#8892a4] mt-1">{label}</div>
              </div>
            ))}
          </div>
        )}

        <Card>
          {collections.length === 0 ? (
            <EmptyCollections onGoToIngest={goToIngest} />
          ) : (
            <CollectionsTable collections={collections} onDelete={deleteCollection} />
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
