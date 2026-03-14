import { BotIcon } from "../ui/Icons";
import { Button } from "../ui/Primitives";
import { useStore } from "../../store/useStore";

export function ChatEmptyState({ hasCollections, onGoToIngest }) {
  return (
    <div className="flex flex-col items-center justify-center h-full gap-4 text-center px-8">
      <div className="w-14 h-14 rounded-2xl bg-[#161b25] border border-[rgba(255,255,255,0.06)] flex items-center justify-center text-[#4d5669]">
        <BotIcon />
      </div>

      {hasCollections ? (
        <>
          <p className="text-[14px] font-medium text-[#8892a4]">Ready to answer questions</p>
          <p className="text-[12px] text-[#4d5669] max-w-xs leading-relaxed">
            Select a collection from the dropdown above, then type your first question.
          </p>
          <div className="flex flex-wrap gap-2 justify-center mt-2">
            {["What is this document about?", "Summarize the key points", "What are the main topics?"].map((q) => (
              <span
                key={q}
                className="text-[11px] bg-[#161b25] border border-[rgba(255,255,255,0.06)] text-[#8892a4] px-3 py-1.5 rounded-full cursor-default hover:border-[rgba(0,229,160,0.2)] hover:text-[#00e5a0] transition-colors"
              >
                {q}
              </span>
            ))}
          </div>
        </>
      ) : (
        <>
          <p className="text-[14px] font-medium text-[#8892a4]">No collections yet</p>
          <p className="text-[12px] text-[#4d5669] max-w-xs leading-relaxed">
            Ingest some documents first to create a collection, then come back to chat.
          </p>
          <Button variant="outline" size="sm" onClick={onGoToIngest}>
            Go to Ingestion
          </Button>
        </>
      )}
    </div>
  );
}
