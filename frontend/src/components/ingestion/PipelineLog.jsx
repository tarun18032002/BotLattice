import { Card, SectionTitle } from "../ui/Primitives";

const LOG_COLORS = {
  success: "#00e5a0",
  warn:    "#ffb84d",
  info:    "#4d9eff",
};

export function PipelineLog({ logs, logRef }) {
  return (
    <Card className="p-4">
      <SectionTitle>Pipeline Log</SectionTitle>
      <div
        ref={logRef}
        className="rounded-[10px] p-3 h-32 overflow-y-auto border border-[rgba(255,255,255,0.04)]"
        style={{ background: "#080a0f", fontFamily: "'IBM Plex Mono', monospace", fontSize: 11, lineHeight: 1.8 }}
      >
        {logs.length === 0 ? (
          <span style={{ color: "#4d5669" }}>
            No ingestion run yet. Configure pipeline and click Run Ingestion.
          </span>
        ) : (
          logs.map((l, i) => (
            <div key={i} style={{ color: LOG_COLORS[l.level] ?? "#4d9eff" }}>
              <span style={{ color: "#4d5669" }}>[{l.ts}] </span>
              {l.msg}
            </div>
          ))
        )}
      </div>
    </Card>
  );
}
