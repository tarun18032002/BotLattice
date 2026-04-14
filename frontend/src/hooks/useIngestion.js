import { useState, useCallback, useRef, useEffect } from "react";
import { runIngestionPipeline } from "../services/ingestionService";
import { useChunkingOptions } from "./useChunkingOptions";
import { connectEmbedding, fetchCurrentEmbedding } from "../api/embeddings";
import { connectVectordb, fetchCurrentVectordb } from "../api/vectordb";

const API_KEY_REQUIRED_PROVIDERS = new Set(["openai", "google"]);

export function useIngestion() {
  const [files, setFiles] = useState([]);
  const [running, setRunning] = useState(false);
  const [logs, setLogs] = useState([]);
  const [embeddingLoading, setEmbeddingLoading] = useState(true);
  const [embeddingSaving, setEmbeddingSaving] = useState(false);
  const [embeddingConfigured, setEmbeddingConfigured] = useState(false);
  const [embeddingEditing, setEmbeddingEditing] = useState(false);
  const [embeddingError, setEmbeddingError] = useState("");
  const [savedEmbedding, setSavedEmbedding] = useState(null);
  const [vectordbLoading, setVectordbLoading] = useState(true);
  const [vectordbSaving, setVectordbSaving] = useState(false);
  const [vectordbConfigured, setVectordbConfigured] = useState(false);
  const [vectordbEditing, setVectordbEditing] = useState(false);
  const [vectordbError, setVectordbError] = useState("");
  const [savedVectordb, setSavedVectordb] = useState(null);

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

    embedProvider: "openai",
    embedModel: "text-embedding-3-small",
    embedApiKey: "",
    batchSize: 512,
    normalizeEmbed: false,
    cacheEmbed: false,

    vectorDB: "qdrant",
    vdbHost: "http://localhost:6333",
    vdbApiKey: "",
    distanceMetric: "Cosine",
    hybridSearch: false,
    storeMeta: true,

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

  const beginEmbeddingEdit = useCallback(() => {
    setEmbeddingError("");
    setEmbeddingEditing(true);
  }, []);

  const cancelEmbeddingEdit = useCallback(() => {
    if (savedEmbedding) {
      setIngestion((prev) => ({
        ...prev,
        embedProvider: savedEmbedding.provider,
        embedModel: savedEmbedding.model,
        batchSize: savedEmbedding.batch_size,
        normalizeEmbed: savedEmbedding.normalize,
        cacheEmbed: savedEmbedding.cache,
        embedApiKey: "",
      }));
    }
    setEmbeddingError("");
    setEmbeddingEditing(false);
  }, [savedEmbedding]);

  const beginVectordbEdit = useCallback(() => {
    setVectordbError("");
    setVectordbEditing(true);
  }, []);

  const cancelVectordbEdit = useCallback(() => {
    if (savedVectordb) {
      setIngestion((prev) => ({
        ...prev,
        vectorDB: savedVectordb.vectordb_type,
        vdbHost: savedVectordb.url || "",
        distanceMetric: savedVectordb.distance_metric || "Cosine",
        hybridSearch: Boolean(savedVectordb.hybrid_search),
        storeMeta: Boolean(savedVectordb.store_meta),
        vdbApiKey: "",
      }));
    }
    setVectordbError("");
    setVectordbEditing(false);
  }, [savedVectordb]);

  const saveVectordb = useCallback(async () => {
    setVectordbSaving(true);
    setVectordbError("");
    try {
      const connected = await connectVectordb({
        vectordbType: ingestion.vectorDB,
        url: ingestion.vdbHost,
        apiKey: ingestion.vdbApiKey,
        distanceMetric: ingestion.distanceMetric,
        hybridSearch: ingestion.hybridSearch,
        storeMeta: ingestion.storeMeta,
      });

      setIngestion((prev) => ({
        ...prev,
        vectorDB: connected.vectordb_type,
        vdbHost: connected.url || "",
        distanceMetric: connected.distance_metric || "Cosine",
        hybridSearch: Boolean(connected.hybrid_search),
        storeMeta: Boolean(connected.store_meta),
        vdbApiKey: "",
      }));

      setSavedVectordb(connected);
      setVectordbConfigured(true);
      setVectordbEditing(false);
      addLog(`Vector DB connected: ${connected.vectordb_type}`, "success");
      return true;
    } catch (err) {
      const message = err?.message || "Failed to connect vector DB";
      setVectordbError(message);
      addLog(`Vector DB connection failed: ${message}`, "warn");
      return false;
    } finally {
      setVectordbSaving(false);
    }
  }, [ingestion]);

  const saveEmbedding = useCallback(async () => {
    const providerNeedsApiKey = API_KEY_REQUIRED_PROVIDERS.has(ingestion.embedProvider);
    const canReuseSavedKey = savedEmbedding?.provider === ingestion.embedProvider;
    if (providerNeedsApiKey && !ingestion.embedApiKey && !canReuseSavedKey) {
      setEmbeddingError(`API key is required for provider '${ingestion.embedProvider}'.`);
      return false;
    }

    setEmbeddingSaving(true);
    setEmbeddingError("");
    try {
      const connected = await connectEmbedding({
        provider: ingestion.embedProvider,
        model: ingestion.embedModel,
        apiKey: ingestion.embedApiKey,
        batchSize: ingestion.batchSize,
        normalize: ingestion.normalizeEmbed,
        cache: ingestion.cacheEmbed,
      });

      setIngestion((prev) => ({
        ...prev,
        embedProvider: connected.provider,
        embedModel: connected.model,
        batchSize: connected.batch_size,
        normalizeEmbed: connected.normalize,
        cacheEmbed: connected.cache,
        // Avoid keeping secret in memory once saved
        embedApiKey: "",
      }));

      setEmbeddingConfigured(true);
      setEmbeddingEditing(false);
      setSavedEmbedding({
        provider: connected.provider,
        model: connected.model,
        batch_size: connected.batch_size,
        normalize: connected.normalize,
        cache: connected.cache,
      });
      addLog(`Embedding connected: ${connected.provider}/${connected.model}`, "success");
      return true;
    } catch (err) {
      const message = err?.message || "Failed to connect embedding model";
      setEmbeddingError(message);
      addLog(`Embedding connection failed: ${message}`, "warn");
      return false;
    } finally {
      setEmbeddingSaving(false);
    }
  }, [ingestion, savedEmbedding]);

  useEffect(() => {
    (async () => {
      try {
        const current = await fetchCurrentEmbedding();
        if (!current) {
          setEmbeddingConfigured(false);
          setEmbeddingEditing(true);
          return;
        }

        setIngestion((prev) => ({
          ...prev,
          embedProvider: current.provider,
          embedModel: current.model,
          batchSize: current.batch_size,
          normalizeEmbed: current.normalize,
          cacheEmbed: current.cache,
          embedApiKey: "",
        }));
        setEmbeddingConfigured(true);
        setEmbeddingEditing(false);
        setSavedEmbedding(current);
      } catch (err) {
        setEmbeddingError(err?.message || "Failed to load current embedding config");
        setEmbeddingEditing(true);
      } finally {
        setEmbeddingLoading(false);
      }
    })();
  }, []);

  useEffect(() => {
    (async () => {
      try {
        const current = await fetchCurrentVectordb();
        if (!current) {
          setVectordbConfigured(false);
          setVectordbEditing(true);
          return;
        }

        setIngestion((prev) => ({
          ...prev,
          vectorDB: current.vectordb_type,
          vdbHost: current.url || "",
          distanceMetric: current.distance_metric || "Cosine",
          hybridSearch: Boolean(current.hybrid_search),
          storeMeta: Boolean(current.store_meta),
          vdbApiKey: "",
        }));
        setSavedVectordb(current);
        setVectordbConfigured(true);
        setVectordbEditing(false);
      } catch (err) {
        setVectordbError(err?.message || "Failed to load current vector DB config");
        setVectordbEditing(true);
      } finally {
        setVectordbLoading(false);
      }
    })();
  }, []);

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
    embeddingLoading,
    embeddingSaving,
    embeddingConfigured,
    embeddingEditing,
    beginEmbeddingEdit,
    cancelEmbeddingEdit,
    embeddingError,
    saveEmbedding,
    vectordbLoading,
    vectordbSaving,
    vectordbConfigured,
    vectordbEditing,
    beginVectordbEdit,
    cancelVectordbEdit,
    vectordbError,
    saveVectordb,
    logs,
    logRef,
    stats
  };
}
