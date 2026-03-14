import { useState, useCallback, useRef } from "react";
import { runIngestionPipeline } from "../services/anthropicApi";
import { useStore } from "../store/useStore";

/**
 * Manages file uploads, pipeline execution state, and logs
 * for the Ingestion page.
 */
export function useIngestion() {
  const { state, dispatch } = useStore();
  const { ingestion } = state;

  const [files,   setFiles]   = useState([]);
  const [running, setRunning] = useState(false);
  const [logs,    setLogs]    = useState([]);
  const [stats,   setStats]   = useState({ chunks: 0, embeddings: 0, docs: 0, time: "—" });

  const logRef = useRef(null);

  // ── File management ────────────────────────────────────────────────────────

  const addFiles = useCallback((incoming) => {
    const arr = Array.from(incoming);
    setFiles((prev) => {
      const existing = new Set(prev.map((f) => f.name));
      return [...prev, ...arr.filter((f) => !existing.has(f.name))];
    });
  }, []);

  const removeFile = useCallback((index) => {
    setFiles((prev) => prev.filter((_, i) => i !== index));
  }, []);

  // ── Config updater ─────────────────────────────────────────────────────────

  const updateIngestion = useCallback((patch) => {
    dispatch({ type: "UPDATE_INGESTION", payload: patch });
  }, [dispatch]);

  // ── Pipeline execution ─────────────────────────────────────────────────────

  const addLog = useCallback((msg, level = "info") => {
    setLogs((prev) => [...prev, { msg, level, ts: new Date().toLocaleTimeString() }]);
    setTimeout(() => {
      if (logRef.current) logRef.current.scrollTop = logRef.current.scrollHeight;
    }, 0);
  }, []);

  const run = useCallback(async () => {
    if (!files.length)                  return alert("Upload at least one document.");
    if (!ingestion.collectionName.trim()) return alert("Enter a collection name.");

    setRunning(true);
    setLogs([]);

    try {
      const { chunks } = await runIngestionPipeline(ingestion, files, addLog);

      setStats({
        chunks,
        embeddings: chunks,
        docs:  files.length,
        time:  new Date().toLocaleTimeString(),
      });

      dispatch({
        type: "ADD_OR_UPDATE_COLLECTION",
        payload: {
          name:     ingestion.collectionName,
          db:       ingestion.vectorDB,
          embed:    ingestion.embedModel,
          strategy: ingestion.chunkStrategy,
          chunks,
          docs:     files.length,
          created:  new Date().toLocaleDateString(),
        },
      });
    } catch (err) {
      addLog(`Error: ${err.message}`, "warn");
    } finally {
      setRunning(false);
    }
  }, [files, ingestion, addLog, dispatch]);

  return {
    files, addFiles, removeFile,
    ingestion, updateIngestion,
    running, run,
    logs, logRef,
    stats,
  };
}
