import { useRef, useState } from "react";
import { FileIcon, TrashIcon } from "../ui/Icons";
import { Card, SectionTitle } from "../ui/Primitives";

export function UploadZone({ files, onAdd, onRemove }) {
  const [dragging, setDragging] = useState(false);
  const inputRef = useRef(null);

  return (
    <Card className="p-4">
      <SectionTitle>Upload Documents</SectionTitle>

      {/* Drop target */}
      <div
        onClick={() => inputRef.current?.click()}
        onDragOver={(e) => { e.preventDefault(); setDragging(true); }}
        onDragLeave={() => setDragging(false)}
        onDrop={(e) => { e.preventDefault(); setDragging(false); onAdd(e.dataTransfer.files); }}
        className={`
          border-2 border-dashed rounded-[10px] p-6 text-center cursor-pointer transition-all
          ${dragging
            ? "border-[#00e5a0] bg-[rgba(0,229,160,0.04)]"
            : "border-[rgba(255,255,255,0.08)] hover:border-[rgba(255,255,255,0.15)]"
          }
        `}
      >
        <div className="flex justify-center mb-2 text-[#4d5669]">
          <svg viewBox="0 0 36 36" fill="none" stroke="currentColor" strokeWidth="1.5" className="w-8 h-8">
            <path d="M18 24V12M13 17l5-5 5 5"/>
            <path d="M6 26a3 3 0 01-3-3V7a3 3 0 013-3h24a3 3 0 013 3v16a3 3 0 01-3 3H6z"/>
          </svg>
        </div>
        <p className="text-[13px] text-[#8892a4]">Drop files here or click to browse</p>
        <p className="text-[11px] text-[#4d5669] mt-1">PDF · TXT · DOCX · MD · CSV · JSON</p>
      </div>

      <input
        ref={inputRef}
        type="file"
        multiple
        accept=".pdf,.txt,.docx,.md,.csv,.json"
        className="hidden"
        onChange={(e) => onAdd(e.target.files)}
      />

      {/* File list */}
      {files.length > 0 && (
        <div className="mt-3 space-y-1.5 max-h-44 overflow-y-auto pr-1">
          {files.map((f, i) => (
            <div
              key={i}
              className="flex items-center gap-2 bg-[#161b25] border border-[rgba(255,255,255,0.04)] rounded-[10px] px-3 py-2"
            >
              <span className="text-[#4d5669]"><FileIcon /></span>
              <span className="flex-1 text-[12px] text-[#e8eaf0] truncate">{f.name}</span>
              <span className="text-[10px] text-[#4d5669] font-mono flex-shrink-0">
                {(f.size / 1024).toFixed(0)} KB
              </span>
              <button
                onClick={() => onRemove(i)}
                className="text-[#4d5669] hover:text-[#ff5577] transition-colors"
              >
                <TrashIcon />
              </button>
            </div>
          ))}
        </div>
      )}
    </Card>
  );
}
