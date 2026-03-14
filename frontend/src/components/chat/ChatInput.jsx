import { useRef } from "react";
import { SendIcon } from "../ui/Icons";

export function ChatInput({ value, onChange, onSend, disabled, placeholder }) {
  const textareaRef = useRef(null);

  const autoResize = (el) => {
    el.style.height = "auto";
    el.style.height = Math.min(el.scrollHeight, 120) + "px";
  };

  const handleKeyDown = (e) => {
    if (e.key === "Enter" && !e.shiftKey) {
      e.preventDefault();
      onSend();
    }
  };

  const handleChange = (e) => {
    onChange(e.target.value);
    autoResize(e.target);
  };

  return (
    <div className="px-5 pb-4 pt-2 border-t border-[rgba(255,255,255,0.04)] bg-[#0b0d11] flex-shrink-0">
      <div className="flex items-end gap-2 bg-[#161b25] border border-[rgba(255,255,255,0.06)] rounded-[14px] px-3 py-2 focus-within:border-[rgba(0,229,160,0.25)] transition-colors">
        <textarea
          ref={textareaRef}
          value={value}
          onChange={handleChange}
          onKeyDown={handleKeyDown}
          placeholder={placeholder}
          rows={1}
          style={{ maxHeight: 120 }}
          className="flex-1 bg-transparent text-[13px] text-[#e8eaf0] placeholder:text-[#4d5669] outline-none resize-none leading-relaxed"
        />
        <button
          onClick={onSend}
          disabled={disabled || !value.trim()}
          className="w-8 h-8 bg-[#00e5a0] rounded-[8px] flex items-center justify-center text-[#0b0d11] hover:bg-white transition-colors disabled:opacity-40 disabled:cursor-not-allowed flex-shrink-0"
        >
          <SendIcon />
        </button>
      </div>
      <p className="text-[10px] text-[#4d5669] mt-1.5 px-1">
        Shift+Enter for new line · Responses grounded in selected collection
      </p>
    </div>
  );
}
