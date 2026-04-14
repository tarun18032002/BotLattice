git commit -m  "fix: fix ingest pipeline — API contract, chunking payload, and Replace mode

Backend:
- Add GET /chunking/options/{type} endpoint to expose per-strategy field schema
- Add GET /vectordb/collections endpoint
- Fix pipeline.py: wrong attribute names (CollectionName → collection_name, Mode → mode)
- Fix vector_store.py: implement missing _delete_collection for Replace_existing mode
- Fix vector_store.py: f-string syntax error (nested double quotes)
- Fix chunking_config.py: add missing 'simple' strategy entry
- Add CollectionMode enum and CollectionRequest schema
- Extend ChunkingType enum with all supported strategies

Frontend:
- Fix useIngestion.js: was passing nested apiConfig to service causing
  chunking_type: undefined → backend 400; now builds chunking payload
  dynamically using only fields declared by GET /chunking/options/{type}
- Fix useIngestion.js: collectionMode initial value "append" → "Append_to_existing"
- Fix ingestionService.js: update signature to accept pre-built chunking
  and collection objects; append as separate form fields matching backend
- Add useChunkingOptions hook: fetches field schema from backend on strategy change
- Add useCollections hook: fetches existing collection names from backend
- Update ChunkingConfig.jsx: render controls dynamically from API field schema
- Update IngestionPage.jsx: collection mode uses backend enum values directly"


                ┌────────────────────┐
                │   Orchestrator     │
                └────────┬───────────┘
                         │
                ┌────────▼────────┐
                │ Intent Analyzer │
                └────────┬────────┘
                         │
                ┌────────▼────────┐
                │ Context Builder │  ← (RAG + templates)
                └────────┬────────┘
                         │
                ┌────────▼────────┐
                │ Prompt Writer   │
                └────────┬────────┘
                         │
        ┌────────────────▼──────────────┐
        │ Multi-Evaluator Layer        │
        │ ┌──────────┬──────────────┐  │
        │ │ Critic   │ Validator    │  │
        │ └──────────┴──────────────┘  │
        └────────────┬─────────────────┘
                     │
        ┌────────────▼────────────┐
        │ Decision Controller     │
        │ (retry / accept / stop) │
        └────────────┬────────────┘
                     │
        ┌────────────▼────────────┐
        │ Prompt Refiner (optional)│
        └────────────┬────────────┘
                     │
                ┌────▼────┐
                │  Output │
                └─────────┘