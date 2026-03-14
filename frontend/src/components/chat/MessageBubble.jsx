import { BotIcon, UserIcon } from "../ui/Icons";

export function MessageBubble({ message }) {
  const isUser = message.role === "user";

  return (
    <div className={`flex gap-3 ${isUser ? "flex-row-reverse" : ""}`} style={{ animation: "fadeIn .2s ease both" }}>
      {/* Avatar */}
      <div
        className={`w-7 h-7 rounded-lg flex items-center justify-center flex-shrink-0 mt-0.5
          ${isUser
            ? "bg-[#00e5a0] text-[#0b0d11]"
            : "bg-[#161b25] border border-[rgba(255,255,255,0.06)] text-[#8892a4]"
          }`}
      >
        {isUser ? <UserIcon /> : <BotIcon />}
      </div>

      {/* Body */}
      <div className={`max-w-[72%] flex flex-col gap-1.5 ${isUser ? "items-end" : "items-start"}`}>
        {/* Bubble */}
        <div
          className={`px-4 py-3 rounded-[14px] text-[13px] leading-relaxed
            ${isUser
              ? "bg-[#00e5a0] text-[#0b0d11] rounded-tr-[4px]"
              : "bg-[#161b25] border border-[rgba(255,255,255,0.06)] text-[#e8eaf0] rounded-tl-[4px]"
            }`}
          style={{ whiteSpace: "pre-wrap", wordBreak: "break-word" }}
        >
          {message.content}
        </div>

        {/* Source chips */}
        {message.sources?.length > 0 && (
          <div className="flex flex-wrap gap-1.5">
            {message.sources.map((src, i) => (
              <span
                key={i}
                className="text-[10px] bg-[rgba(77,158,255,0.1)] text-[#4d9eff] border border-[rgba(77,158,255,0.2)] px-2 py-0.5 rounded-full font-mono"
              >
                {src}
              </span>
            ))}
          </div>
        )}

        {/* Timestamp */}
        <span className="text-[10px] text-[#4d5669] px-1">{message.ts}</span>
      </div>
    </div>
  );
}

export function ThinkingIndicator() {
  return (
    <div className="flex gap-3" style={{ animation: "fadeIn .2s ease both" }}>
      <div className="w-7 h-7 rounded-lg bg-[#161b25] border border-[rgba(255,255,255,0.06)] flex items-center justify-center flex-shrink-0 text-[#8892a4]">
        <BotIcon />
      </div>
      <div className="bg-[#161b25] border border-[rgba(255,255,255,0.06)] rounded-[14px] rounded-tl-[4px] px-4 py-3 flex items-center gap-1.5">
        {[0, 1, 2].map((i) => (
          <div
            key={i}
            className="w-1.5 h-1.5 rounded-full bg-[#00e5a0]"
            style={{ animation: `dotBounce .9s ease ${i * 0.15}s infinite` }}
          />
        ))}
      </div>
    </div>
  );
}
