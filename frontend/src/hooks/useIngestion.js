import { useState, useCallback, useRef } from "react";
import { runIngestionPipeline } from "../services/ingestionService";
import { useChunkingOptions } from "./useChunkingOptions";

export function useIngestion() {
  const [files, setFiles] = useState([]);
  const [running, setRunning] = useState(false);
  const [logs, setLogs] = useState([]);

  const logRef = useRef(null);

  const [stats, setStats] = useState({
    docs: 0,
    chunks: 0,
    embeddings: 0,
    time: "-"
  });

  const [ingestion, setIngestion] = useState({
    chunkStrategy: "sentence",
    // Field values are stored under snake_case keys matching backend field names.
    // ChunkingConfig auto-applies defaults from the API when strategy changes.
    chunk_size: 512,
    chunk_overlap: 50,
    language: "python",
    chunk_lines: 40,
    chunk_lines_overlap: 10,
    chunk_sizes: [2048, 512, 128],

    collectionMode: "Append_to_existing",
    collectionName: "",
    Description: "",
    Tags: ""
  });

  // Get the field definitions for the currently selected strategy from the backend
  const { fields: chunkingFields } = useChunkingOptions(ingestion.chunkStrategy);

  const addLog = (msg, level = "info") => {
    setLogs((prev) => [...prev, { msg, level }]);
  };

  const addFiles = (newFiles) => {
    setFiles((prev) => [...prev, ...newFiles]);
  };

  const removeFile = (index) => {
    setFiles((prev) => prev.filter((_, i) => i !== index));
  };

  const updateIngestion = (payload) => {
    setIngestion((prev) => ({ ...prev, ...payload }));
  };

  // Build the chunking payload using ONLY the fields the backend declared for this type
  const buildChunking = (ing, fields) => {
    const payload = { chunking_type: ing.chunkStrategy };
    for (const field of fields) {
      const val = ing[field.name] !== undefined ? ing[field.name] : field.default;
      if (field.type === "int") {
        payload[field.name] = Number(val) || Number(field.default);
      } else if (field.type === "list[int]") {
        payload[field.name] = Array.isArray(val) ? val : field.default;
      } else {
        payload[field.name] = val;
      }
    }
    return payload;
  };

  const run = useCallback(async () => {
    if (!files.length) {
      alert("Upload at least one document.");
      return;
    }

    if (!ingestion.collectionName?.trim()) {
      alert("Enter a collection name.");
      return;
    }

    if (ingestion.collectionMode === "Replace_existing") {
      const ok = window.confirm("⚠️ This will delete existing data. Continue?");
      if (!ok) return;
    }

    setRunning(true);
    setLogs([]);

    try {
      addLog("Starting ingestion pipeline...");

      const chunking = buildChunking(ingestion, chunkingFields);

      const collection = {
        collection_name: ingestion.collectionName,
        mode: ingestion.collectionMode,
        description: ingestion.Description || "",
        tags: ingestion.Tags || ""
      };

      const { chunks } = await runIngestionPipeline(
        chunking,
        collection,
        files,
        (msg, level = "info") => addLog(msg, level)
      );

      addLog("Pipeline finished successfully", "success");

      setStats({
        chunks,
        embeddings: chunks,
        docs: files.length,
        time: new Date().toLocaleTimeString()
      });

    } catch (err) {
      console.error(err);
      addLog(`Error: ${err.message}`, "warn");
    } finally {
      setRunning(false);
    }
  }, [files, ingestion, chunkingFields]);

  return {
    files,
    addFiles,
    removeFile,
    ingestion,
    updateIngestion,
    running,
    run,
    logs,
    logRef,
    stats
  };
}
