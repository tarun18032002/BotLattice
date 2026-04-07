/**
 * src/components/chat/AgentUpdateBubble.jsx
 *
 * Renders per-node agent update cards and the confirm-intent card
 * for the prompt_builder multi-agent stream.
 *
 * Supported message roles:
 *   "agent-update"    — { node, data }
 *   "confirm-intent"  — { intent, message, confirmed? }
 */

import { useState } from "react";
import { Button }   from "../ui/Primitives";
import { BotIcon }  from "../ui/Icons";

// ── Node metadata ─────────────────────────────────────────────────────────────

const NODE_META = {
  orchestrator:        { label: "Orchestrator",        color: "#4d9eff" },
  intent_analyzer:     { label: "Intent Analyzer",     color: "#4d9eff" },
  context_builder:     { label: "Context Builder",     color: "#ffb84d" },
  prompt_writer:       { label: "Prompt Writer",       color: "#00e5a0" },
  evaluator:           { label: "Evaluator",           color: "#ff5577" },
  decision_controller: { label: "Decision Controller", color: "#a78bfa" },
  prompt_refiner:      { label: "Prompt Refiner",      color: "#00e5a0" },
  synthesizer:         { label: "Final Output",        color: "#00e5a0" },
};

// ── Sub-components ────────────────────────────────────────────────────────────

function CodeBlock({ title, content }) {
  const [open, setOpen] = useState(false);
  return (
    <div>
      <button
        onClick={() => setOpen((o) => !o)}
        className="flex items-center gap-1 text-[11px] text-[#8892a4] hover:text-[#e8eaf0] transition-colors cursor-pointer select-none"
      >
        <span>{open ? "▾" : "▸"}</span>
        <span>{title}</span>
      </button>
      {open && (
        <pre className="mt-2 p-3 bg-[#0b0d11] border border-[rgba(255,255,255,0.06)] rounded-[10px] text-[11px] text-[#e8eaf0] overflow-x-auto whitespace-pre-wrap break-words max-h-64 overflow-y-auto">
          {content}
        </pre>
      )}
    </div>
  );
}

function StatusBadge({ status }) {
  const styles = {
    passed:  "bg-[rgba(0,229,160,0.1)]   text-[#00e5a0] border-[rgba(0,229,160,0.2)]",
    failed:  "bg-[rgba(255,85,119,0.1)]  text-[#ff5577] border-[rgba(255,85,119,0.2)]",
    pending: "bg-[rgba(255,184,77,0.1)]  text-[#ffb84d] border-[rgba(255,184,77,0.2)]",
    skipped: "bg-white/5                 text-[#8892a4] border-white/10",
  };
  const icons = { passed: "✓", failed: "✗", pending: "⏱", skipped: "—" };
  const key   = status?.toLowerCase() ?? "skipped";
  return (
    <span className={`text-[10px] font-medium px-2 py-0.5 rounded-full border ${styles[key] ?? styles.skipped}`}>
      {icons[key] ?? ""} {status?.toUpperCase()}
    </span>
  );
}

function DecisionBadge({ decision }) {
  const styles = {
    accept: "bg-[rgba(0,229,160,0.1)]  text-[#00e5a0] border-[rgba(0,229,160,0.2)]",
    retry:  "bg-[rgba(255,184,77,0.1)] text-[#ffb84d] border-[rgba(255,184,77,0.2)]",
    stop:   "bg-[rgba(255,85,119,0.1)] text-[#ff5577] border-[rgba(255,85,119,0.2)]",
  };
  const icons = { accept: "✓", retry: "↺", stop: "■" };
  const key   = decision?.toLowerCase() ?? "stop";
  return (
    <span className={`text-[10px] font-medium px-2 py-0.5 rounded-full border ${styles[key] ?? styles.stop}`}>
      {icons[key] ?? ""} {decision?.toUpperCase()}
    </span>
  );
}

// ── Node card ─────────────────────────────────────────────────────────────────

function NodeCard({ node, data }) {
  const meta = NODE_META[node] ?? { label: node, color: "#8892a4" };

  return (
    <div
      className="pl-3 py-2.5 pr-3 rounded-[12px] bg-[#0d1018] border border-[rgba(255,255,255,0.05)]"
      style={{ borderLeft: `2px solid ${meta.color}` }}
    >
      {/* Node label */}
      <div
        className="text-[10px] font-semibold uppercase tracking-widest mb-2"
        style={{ color: meta.color }}
      >
        {meta.label}
      </div>

      <div className="flex flex-col gap-2 text-[12px] text-[#c4cad8]">

        {/* orchestrator */}
        {data.intent && (
          <div><span className="text-[#8892a4]">Intent: </span>{data.intent}</div>
        )}
        {data.error && (
          <div className="text-[#ff5577]"><span className="text-[#8892a4]">Error: </span>{data.error}</div>
        )}

        {/* intent_analyzer */}
        {data.analyzed_intent && (
          <div><span className="text-[#8892a4]">Analyzed: </span>{data.analyzed_intent}</div>
        )}

        {/* context_builder */}
        {data.context_summary && (
          <div><span className="text-[#8892a4]">Context: </span>{data.context_summary}</div>
        )}

        {/* prompt_writer */}
        {data.description && (
          <div><span className="text-[#8892a4]">Description: </span>{data.description}</div>
        )}
        {data.prompt_draft && (
          <CodeBlock title="Prompt Draft" content={data.prompt_draft} />
        )}

        {/* evaluator */}
        {data.validation_status && (
          <div className="flex items-center gap-2">
            <span className="text-[#8892a4]">Status:</span>
            <StatusBadge status={data.validation_status} />
          </div>
        )}
        {data.critique && (
          <div><span className="text-[#8892a4]">Critique: </span>{data.critique}</div>
        )}
        {data.validation_errors?.length > 0 && (
          <div>
            <span className="text-[#8892a4]">Errors:</span>
            <ul className="mt-1 pl-3 list-disc text-[#ff5577] text-[11px] space-y-0.5">
              {data.validation_errors.map((e, i) => <li key={i}>{e}</li>)}
            </ul>
          </div>
        )}
        {data.hallucination_flags?.length > 0 && (
          <div>
            <span className="text-[#8892a4]">Hallucination flags:</span>
            <ul className="mt-1 pl-3 list-disc text-[#ffb84d] text-[11px] space-y-0.5">
              {data.hallucination_flags.map((f, i) => <li key={i}>{f}</li>)}
            </ul>
          </div>
        )}

        {/* decision_controller */}
        {data.decision && (
          <div className="flex items-center gap-2">
            <span className="text-[#8892a4]">Decision:</span>
            <DecisionBadge decision={data.decision} />
          </div>
        )}

        {/* prompt_refiner */}
        {data.refined_prompt && (
          <CodeBlock title="Refined Prompt" content={data.refined_prompt} />
        )}

        {/* synthesizer — final output */}
        {data.final_output && (
          <div className="mt-1 p-3 bg-[rgba(0,229,160,0.05)] border border-[rgba(0,229,160,0.15)] rounded-[10px] text-[13px] text-[#e8eaf0] whitespace-pre-wrap leading-relaxed">
            {data.final_output}
          </div>
        )}
        {data.metadata && Object.keys(data.metadata).length > 0 && (
          <div className="text-[10px] text-[#4d5669]">
            {Object.entries(data.metadata)
              .map(([k, v]) => `${k}: ${v}`)
              .join(" · ")}
          </div>
        )}
      </div>
    </div>
  );
}

// ── Confirm-intent card ───────────────────────────────────────────────────────

function ConfirmIntentCard({ message, onConfirm, msgIdx }) {
  const { confirmed } = message;

  return (
    <div
      className="pl-3 py-2.5 pr-3 rounded-[12px] bg-[#0d1018] border border-[rgba(255,255,255,0.05)]"
      style={{ borderLeft: "2px solid #ffb84d" }}
    >
      <div className="text-[10px] font-semibold uppercase tracking-widest mb-2 text-[#ffb84d]">
        Intent Confirmation
      </div>

      <div className="flex flex-col gap-2 text-[12px] text-[#c4cad8]">
        <div className="text-[#8892a4]">{message.message}</div>
        <div className="px-3 py-2 bg-[#161b25] border border-[rgba(255,255,255,0.06)] rounded-[8px] text-[13px] text-[#e8eaf0] italic">
          "{message.intent}"
        </div>

        {confirmed === null || confirmed === undefined ? (
          <div className="flex gap-2 mt-1">
            <Button variant="primary" size="xs" onClick={() => onConfirm(true, msgIdx)}>
              ✓ Confirm
            </Button>
            <Button variant="danger" size="xs" onClick={() => onConfirm(false, msgIdx)}>
              ✗ Reject
            </Button>
          </div>
        ) : (
          <div className={`text-[11px] font-semibold mt-1 ${confirmed ? "text-[#00e5a0]" : "text-[#ff5577]"}`}>
            {confirmed ? "✓ Confirmed — continuing…" : "✗ Rejected"}
          </div>
        )}
      </div>
    </div>
  );
}

// ── Public export ─────────────────────────────────────────────────────────────

export function AgentUpdateBubble({ message, onConfirm, msgIdx }) {
  return (
    <div className="flex gap-3" style={{ animation: "fadeIn .2s ease both" }}>
      {/* Avatar — matches assistant bubble sizing */}
      <div className="w-7 h-7 rounded-lg bg-[#161b25] border border-[rgba(255,255,255,0.06)] flex items-center justify-center flex-shrink-0 mt-0.5 text-[#8892a4]">
        <BotIcon />
      </div>

      <div className="flex-1 min-w-0 max-w-[78%] flex flex-col gap-1">
        {message.role === "agent-update" && (
          <NodeCard node={message.node} data={message.data} />
        )}
        {message.role === "confirm-intent" && (
          <ConfirmIntentCard message={message} onConfirm={onConfirm} msgIdx={msgIdx} />
        )}
        <span className="text-[10px] text-[#4d5669] px-1">{message.ts}</span>
      </div>
    </div>
  );
}
