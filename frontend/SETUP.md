# BotLattice UI — Setup Guide

## Quick Start

### 1. Install dependencies

```bash
npm create vite@latest botlattice-ui -- --template react
cd botlattice-ui
npm install
npm install -D tailwindcss postcss autoprefixer
npx tailwindcss init -p
```

### 2. Configure Tailwind (`tailwind.config.js`)

```js
export default {
  content: ["./index.html", "./src/**/*.{js,jsx}"],
  theme: { extend: {} },
  plugins: [],
}
```

### 3. Add Tailwind to `src/index.css`

```css
@tailwind base;
@tailwind components;
@tailwind utilities;
```

### 4. Drop in the component

Copy `BotLattice.jsx` into `src/` then update `src/main.jsx`:

```jsx
import React from 'react'
import ReactDOM from 'react-dom/client'
import BotLatticeApp from './BotLattice'
import './index.css'

ReactDOM.createRoot(document.getElementById('root')).render(
  <React.StrictMode>
    <BotLatticeApp />
  </React.StrictMode>
)
```

### 5. Run

```bash
npm run dev
```

---

## ⚠️ Production API Key Handling

The chatbot calls the Anthropic API directly from the browser for demo purposes.
**In production, never expose API keys client-side.** Instead:

1. Create a backend endpoint (FastAPI, Express, etc.) that proxies `/v1/messages`
2. Replace the `fetch("https://api.anthropic.com/v1/messages", ...)` call in `ChatPage`
   with `fetch("/api/chat", ...)`
3. Store your `ANTHROPIC_API_KEY` in a `.env` file on the server

---

## Wiring to Your BotLattice Backend

Replace the simulated ingestion in `runIngestion()` with real API calls:

```js
// In IngestionPage → runIngestion()
const res = await fetch("/api/ingest", {
  method: "POST",
  body: formData,   // files + config
});
const { chunks, collection } = await res.json();
```

Your FastAPI endpoints to implement:
- `POST /api/ingest`   — chunking + embedding + indexing
- `POST /api/chat`     — RAG retrieval + LLM generation
- `GET  /api/collections` — list all collections
- `DELETE /api/collections/:name` — delete a collection

---

## Features

| Feature | Details |
|---|---|
| **Chunking** | Fixed, Recursive, Sentence, Semantic, Token, Markdown, Paragraph |
| **Embeddings** | OpenAI, Cohere, HuggingFace, Voyage AI, Google, Mistral, Local/Ollama |
| **Vector DBs** | Chroma, Pinecone, Qdrant, Weaviate, FAISS, Milvus, pgvector, OpenSearch |
| **LLMs** | Anthropic, OpenAI, Groq, Ollama, Mistral |
| **Retrieval** | RAG mode, Direct LLM mode, Top-K control, hybrid search toggle |
| **Chat** | Multi-turn, collection selector, source citations, thinking indicator |
| **Collections** | Create / append / replace, metadata tags, per-collection stats |
