# Backend (FastAPI)

Backend API for RAG ingestion/query, settings, provider catalogs, and authentication.

## Prerequisites

- Python 3.14+
- uv (recommended) or pip
- PostgreSQL (local or via docker compose)

## Environment

Configure these variables before running backend:

- `POSTGRES_USER`
- `POSTGRES_PASSWORD`
- `POSTGRES_DB`
- `POSTGRES_HOST` (default: `localhost`)
- `POSTGRES_PORT` (default: `5432`)
- `GOOGLE_CLIENT_ID` (only needed for Google auth)

Example values:

```env
POSTGRES_USER=rag_user
POSTGRES_PASSWORD=rag_password
POSTGRES_DB=rag_sdk
POSTGRES_HOST=localhost
POSTGRES_PORT=5432
GOOGLE_CLIENT_ID=
```

## Install

From `backend/`:

```bash
uv sync
```

## Run (local)

From `backend/`:

```bash
uv run uvicorn main:app --reload --host 0.0.0.0 --port 8000
```

API base URL: `http://localhost:8000`

## Run with Compose

From repo root:

```bash
docker compose up -d --build
```

This starts:

- `postgres` on `localhost:5432`
- `backend` on `localhost:8000`

## API Areas

- `/auth/*`: register, login, google login, me, logout
- `/settings/*`: current settings and provider options
- `/embeddings/*`: provider list/current config/connect
- `/vector-db/*`: providers/options/current/connect/collections
- `/chunking/*`: chunking option schemas
- `/query/*`: query endpoints
- `/ws/chat`: websocket chat stream

## Notes

- Runtime states (embedding, vector DB, LLM settings) are persisted in PostgreSQL.
- Provider options are DB-backed and can be managed through settings option endpoints.
- Backend includes CORS configuration for local frontend development.

## Troubleshooting

- DB connection errors: verify host/port/user/password/db match your PostgreSQL instance.
- Auth token issues: clear stale tokens and re-login.
- Google auth errors: verify `GOOGLE_CLIENT_ID` and frontend client ID are the same.
