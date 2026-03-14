const ANTHROPIC_API = "https://api.anthropic.com/v1/messages";

/**
 * Send a chat request to the Anthropic API.
 *
 * ⚠️  In production, proxy this through your backend — never expose API keys
 *      client-side. Point `apiBase` at your server's `/api/chat` endpoint instead.
 *
 * @param {object}   opts
 * @param {string}   opts.model          - e.g. "claude-sonnet-4-20250514"
 * @param {string}   opts.systemPrompt   - System instructions
 * @param {Array}    opts.messages        - [{role, content}]
 * @param {number}   [opts.maxTokens=1000]
 * @returns {Promise<string>}            - Assistant reply text
 */
export async function sendChatMessage({ model, systemPrompt, messages, maxTokens = 1000 }) {
  const response = await fetch(ANTHROPIC_API, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({
      model,
      max_tokens: maxTokens,
      system: systemPrompt,
      messages,
    }),
  });

  if (!response.ok) {
    const err = await response.json().catch(() => ({}));
    throw new Error(err?.error?.message || `API error ${response.status}`);
  }

  const data = await response.json();
  const textBlock = data.content?.find(b => b.type === "text");
  if (!textBlock) throw new Error("No text content in response");
  return textBlock.text;
}

/**
 * Build the RAG-aware system prompt injected before each chat turn.
 *
 * @param {string}  basePrompt    - User-configured system prompt
 * @param {object}  [collection]  - Active collection metadata
 * @param {string}  mode          - "rag" | "direct"
 * @param {number}  topK
 * @returns {string}
 */
export function buildSystemPrompt(basePrompt, collection, mode, topK) {
  if (!collection) {
    return basePrompt + "\n\nNo collection selected. Answer from general knowledge.";
  }

  const context =
    mode === "rag"
      ? `Active collection: "${collection.name}" (${collection.chunks} chunks, embedded with ${collection.embed}, stored in ${collection.db}).
Retrieval: top-${topK} chunks by similarity.
Instructions: simulate realistic retrieval and answer from the collection context. Cite chunks as [source: filename, chunk #N].`
      : `Collection "${collection.name}" is available but Direct LLM mode is active. Answer from general knowledge.`;

  return `${basePrompt}\n\n${context}`;
}

/**
 * Simulate ingestion steps for demo purposes.
 * Replace each step with a real API call to your BotLattice backend.
 *
 * @param {object}   config     - Ingestion configuration
 * @param {File[]}   files      - Uploaded files
 * @param {Function} onLog      - (message: string, level: "info"|"success"|"warn") => void
 * @returns {Promise<{chunks: number}>}
 */
export async function runIngestionPipeline(config, files, onLog) {
  const sleep = (ms) => new Promise((r) => setTimeout(r, ms));
  const chunks = Math.floor(Math.random() * 300) + 80;

  // ── Step 1: Load documents ─────────────────────────────────────────────────
  // Replace with: POST /api/ingest/load  { files, collectionName, collectionMode }
  onLog(`Starting ingestion for collection: "${config.collectionName}"`, "info");
  await sleep(300);
  onLog(`Loading ${files.length} document(s)…`, "info");
  for (const f of files) {
    await sleep(150);
    onLog(`  ✓  ${f.name}  (${(f.size / 1024).toFixed(0)} KB)`, "success");
  }

  // ── Step 2: Chunk ─────────────────────────────────────────────────────────
  // Replace with: POST /api/ingest/chunk  { strategy, chunkSize, chunkOverlap, … }
  await sleep(300);
  onLog(`Chunking — strategy: ${config.chunkStrategy} | size: ${config.chunkSize} | overlap: ${config.chunkOverlap}`, "info");
  await sleep(400);
  onLog(`  ✓  ${chunks} chunks created`, "success");

  // ── Step 3: Embed ─────────────────────────────────────────────────────────
  // Replace with: POST /api/ingest/embed  { provider, model, batchSize, normalize }
  await sleep(200);
  onLog(`Embedding with ${config.embedProvider}/${config.embedModel} (batch=${config.batchSize})…`, "info");
  await sleep(600);
  onLog(`  ✓  ${chunks} vectors generated`, "success");

  // ── Step 4: Index ─────────────────────────────────────────────────────────
  // Replace with: POST /api/ingest/index  { vectorDB, host, distanceMetric, hybridSearch }
  await sleep(300);
  onLog(`Indexing into ${config.vectorDB} at ${config.vdbHost}…`, "info");
  await sleep(500);
  onLog(`  ✓  Collection "${config.collectionName}" ready in ${config.vectorDB}`, "success");
  onLog(`Pipeline complete — ${files.length} docs → ${chunks} chunks → ${config.vectorDB}`, "success");

  return { chunks };
}
