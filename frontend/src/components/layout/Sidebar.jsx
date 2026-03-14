import { useStore } from "../../store/useStore";
import { UploadIcon, ChatIcon, DatabaseIcon, SettingsIcon } from "../ui/Icons";

const NAV_ITEMS = [
  { id: "ingest",      label: "Ingestion",   Icon: UploadIcon },
  { id: "chat",        label: "Chatbot",     Icon: ChatIcon },
  { id: "collections", label: "Collections", Icon: DatabaseIcon },
  { id: "settings",    label: "Settings",    Icon: SettingsIcon },
];

export function Sidebar() {
  const { state, dispatch } = useStore();
  const { page, ingestion, collections } = state;

  const setPage = (id) => dispatch({ type: "SET_PAGE", payload: id });

  const summary = [
    ["Collection", ingestion.collectionName || "—"],
    ["Chunker",    ingestion.chunkStrategy],
    ["Embedder",   ingestion.embedProvider],
    ["Vector DB",  ingestion.vectorDB],
  ];

  return (
    <aside className="w-[216px] min-w-[216px] bg-[#0b0d11] border-r border-[rgba(255,255,255,0.06)] flex flex-col h-screen">
      {/* Logo */}
      <div className="p-4 pb-3 border-b border-[rgba(255,255,255,0.04)]">
        <div className="flex items-center gap-2.5">
          <div className="w-8 h-8 rounded-lg bg-[#00e5a0] flex items-center justify-center flex-shrink-0">
            <span className="text-[#0b0d11] font-bold text-[13px]" style={{ fontFamily: "'IBM Plex Mono', monospace" }}>
              BL
            </span>
          </div>
          <div>
            <div className="text-[14px] font-semibold text-[#e8eaf0]">BotLattice</div>
            <div className="text-[10px] text-[#4d5669] mt-0.5">RAG Pipeline v2</div>
          </div>
        </div>
      </div>

      {/* Nav */}
      <nav className="flex-1 p-2 pt-3">
        <div className="text-[9px] font-semibold text-[#4d5669] uppercase tracking-[0.14em] px-2 mb-2">
          Pipeline
        </div>
        {NAV_ITEMS.map(({ id, label, Icon }) => {
          const active = page === id;
          return (
            <button
              key={id}
              onClick={() => setPage(id)}
              className={`
                w-full flex items-center gap-2.5 px-2.5 py-2 rounded-[10px] text-[13px]
                transition-all mb-0.5 cursor-pointer text-left border
                ${active
                  ? "bg-[rgba(0,229,160,0.08)] text-[#00e5a0] border-[rgba(0,229,160,0.15)]"
                  : "text-[#8892a4] hover:bg-white/5 hover:text-[#e8eaf0] border-transparent"
                }
              `}
            >
              <Icon />
              {label}
              {id === "collections" && collections.length > 0 && (
                <span className="ml-auto text-[10px] bg-[#161b25] text-[#4d5669] px-1.5 py-0.5 rounded-full font-mono">
                  {collections.length}
                </span>
              )}
            </button>
          );
        })}
      </nav>

      {/* Active config summary */}
      <div className="m-2 p-3 rounded-[10px] bg-[#0d1018] border-t border-[rgba(255,255,255,0.04)]">
        <div className="text-[9px] text-[#4d5669] uppercase tracking-[0.12em] mb-2">Active config</div>
        {summary.map(([k, v]) => (
          <div key={k} className="flex items-center justify-between gap-2 mb-1 last:mb-0">
            <span className="text-[10px] text-[#4d5669]">{k}</span>
            <span className="text-[10px] text-[#8892a4] font-medium truncate max-w-[100px] text-right">{v}</span>
          </div>
        ))}
      </div>
    </aside>
  );
}
