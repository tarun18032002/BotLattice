# RAG SDK

Full-stack Retrieval-Augmented Generation (RAG) workspace with:

- FastAPI backend for ingestion, embeddings, vector DB, query, settings, and auth
- React + Vite frontend for configuration, ingestion, collections, and chat
- PostgreSQL-backed runtime state for settings/provider metadata/auth sessions

## Repository Layout

- `backend/`: FastAPI app and pipeline code
- `frontend/`: React app
- `docker-compose.yml`: local PostgreSQL + backend services

## Quick Start

### 1) Run with Docker Compose (backend + postgres)

From repository root:

```bash
docker compose up -d --build
```

Backend API is available at `http://localhost:8000`.

### 2) Run frontend locally

From `frontend/`:

```bash
npm install
npm run dev
```

Frontend UI is available at `http://localhost:5173`.

## Environment Variables

### Backend

Set in your backend environment (or export in shell):

- `POSTGRES_USER`
- `POSTGRES_PASSWORD`
- `POSTGRES_DB`
- `POSTGRES_HOST` (defaults to `localhost`, compose uses `postgres`)
- `POSTGRES_PORT` (defaults to `5432`)
- `GOOGLE_CLIENT_ID` (required only for Google auth)

### Frontend

Set in `frontend/.env`:

- `VITE_WS_URL=ws://localhost:8000/ws/chat`
- `VITE_GOOGLE_CLIENT_ID=<google-oauth-web-client-id>` (optional unless Google auth is used)

## Core Features

- Dynamic chunking options and ingestion forms
- Embedding provider selection and persisted embedding state
- Vector DB provider selection and collection operations
- LLM/retrieval settings persisted in PostgreSQL
- Email/password auth and Google sign-in
- WebSocket chat streaming support

## Deployment

For production deployment (Vercel + Railway/Render/etc.):

See [DEPLOYMENT.md](DEPLOYMENT.md) for:
- Frontend deployment to Vercel
- Backend deployment options (Railway, Render, AWS, etc.)
- Environment configuration for production
- Cost and monitoring guidance

## Notes

- If using Docker Compose backend, keep frontend running locally unless you add a frontend service.
- A large model artifact is currently tracked in git; consider Git LFS for files over 50MB.

## Detailed Docs

- Backend setup and API notes: `backend/README.md`
- Frontend setup and configuration: `frontend/README.md`
- Production deployment: `DEPLOYMENT.md`