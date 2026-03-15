import { useState, useCallback, useRef } from "react";
import { runIngestionPipeline } from "../services/ingestionService";

/**
 * Manages file uploads, pipeline execution state, and logs
 * for the Ingestion page.
 */
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
    chunkSize: 512,
    chunkOverlap: 50,
    vectorDB: "qdrant",
    collectionName: "",
    embedModel: "text-embedding-3-small",
    embeddingProvider: "openai"
  });

  const addLog = (msg, level = "info") => {
    setLogs((prev) => [...prev, { msg, level }]);
  };

  const addFiles = (newFiles) => {
    setFiles((prev) => [...prev, ...newFiles]);
  };

  const removeFile = (index) => {
    setFiles((prev) => prev.filter((_, i) => i !== index));
  };

  const updateIngestion = (data) => {
    setIngestion((prev) => ({ ...prev, ...data }));
  };

  const run = useCallback(async () => {

    if (!files.length) {
      alert("Upload at least one document.");
      return;
    }

    if (!ingestion?.collectionName?.trim()) {
      alert("Enter a collection name.");
      return;
    }

    setRunning(true);
    setLogs([]);

    try {

      addLog("Starting ingestion pipeline...");

      const apiConfig = {
        chunking: {
          chunking_type: ingestion.chunkStrategy,
          chunk_size: Number(ingestion.chunkSize) || 512,
          chunk_overlap: Number(ingestion.chunkOverlap) || 50
        },

        embedding: {
          provider: ingestion.embeddingProvider || "openai",
          model_name: ingestion.embedModel || "text-embedding-3-small",
          batch_size: 32
        },

        vectordb: {
          vectordb_type: ingestion.vectorDB || "qdrant",
          collection_name: ingestion.collectionName,
          url: ingestion.vdbHost || null,
          api_key: ingestion.vectorApiKey || null
        }
      };

      const { chunks } = await runIngestionPipeline(
        apiConfig,
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

  }, [files, ingestion]);

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