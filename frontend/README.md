# Frontend (React + Vite)

Frontend UI for ingestion, collections, settings, and chat.

## Prerequisites

- Node.js 20+
- npm 10+

## Setup

```bash
cd frontend
npm install
```

Create `frontend/.env` (or copy from `.env.example`) and set:

```env
VITE_WS_URL=ws://localhost:8000/ws/chat
VITE_GOOGLE_CLIENT_ID=your-google-oauth-web-client-id.apps.googleusercontent.com
```

## Run

```bash
npm run dev
```

App runs at `http://localhost:5173`.

## Build

```bash
npm run build
npm run preview
```

## Main Areas

- Auth: email/password and Google sign-in
- Ingestion: dynamic chunking form and collection mode support
- Collections: list and inspect vector DB collections
- Settings: provider/model/retrieval configuration
- Chat: websocket-based response stream

## Troubleshooting

- If API requests fail, verify backend is running on `http://localhost:8000`.
- If Google login fails, ensure `VITE_GOOGLE_CLIENT_ID` matches backend `GOOGLE_CLIENT_ID`.
- If websocket chat fails, confirm `VITE_WS_URL` points to the active backend endpoint.
