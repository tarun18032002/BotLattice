import { createContext, useContext, useEffect, useReducer } from "react";
import {
  DEFAULT_EMBED_PROVIDER, DEFAULT_EMBED_MODEL,
} from "../constants/embedModels";
import {
  DEFAULT_VECTOR_DB, VDB_DEFAULTS,
} from "../constants/vectorDbs";
import {
  DEFAULT_LLM_PROVIDER, DEFAULT_LLM_MODEL,
  DEFAULT_CHUNK_STRATEGY, DEFAULT_SYSTEM_PROMPT,
} from "../constants/pipeline";

// ── Initial State ─────────────────────────────────────────────────────────────

const initialState = {
  // Active page
  page: "ingest",

  // Ingestion config
  ingestion: {
    collectionName:  "",
    collectionMode:  "Create new",
    chunkStrategy:   DEFAULT_CHUNK_STRATEGY,
    chunkSize:       512,
    chunkOverlap:    50,
    bufferSize:      3,
    separators:      "\\n\\n, \\n, ., ,",
    embedProvider:   DEFAULT_EMBED_PROVIDER,
    embedModel:      DEFAULT_EMBED_MODEL,
    batchSize:       32,
    normalizeEmbed:  true,
    cacheEmbed:      true,
    vectorDB:        DEFAULT_VECTOR_DB,
    vdbHost:         VDB_DEFAULTS[DEFAULT_VECTOR_DB].host,
    distanceMetric:  "Cosine",
    hybridSearch:    false,
    storeMeta:       true,
  },

  // Global LLM / retrieval settings
  settings: {
    llmProvider:     DEFAULT_LLM_PROVIDER,
    llmModel:        DEFAULT_LLM_MODEL,
    apiKey:          "",
    temperature:     0.2,
    maxTokens:       1024,
    defaultTopK:     5,
    simThreshold:    0.75,
    reranking:       false,
    multiQuery:      true,
    compression:     false,
    showSources:     true,
    streamResponses: false,
    systemPrompt:    DEFAULT_SYSTEM_PROMPT,
  },

  // Ingested collections
  collections: [],

  auth: {
    token: localStorage.getItem("auth_token") || "",
    user: (() => {
      try {
        const raw = localStorage.getItem("auth_user");
        return raw ? JSON.parse(raw) : null;
      } catch {
        return null;
      }
    })(),
    isAuthenticated: Boolean(localStorage.getItem("auth_token")),
  },
};

// ── Reducer ───────────────────────────────────────────────────────────────────

function reducer(state, action) {
  switch (action.type) {
    case "SET_PAGE":
      return { ...state, page: action.payload };

    case "UPDATE_INGESTION":
      return { ...state, ingestion: { ...state.ingestion, ...action.payload } };

    case "UPDATE_SETTINGS":
      return { ...state, settings: { ...state.settings, ...action.payload } };

    case "ADD_OR_UPDATE_COLLECTION": {
      const idx = state.collections.findIndex(c => c.name === action.payload.name);
      const next = [...state.collections];
      if (idx >= 0) next[idx] = action.payload;
      else next.push(action.payload);
      return { ...state, collections: next };
    }

    case "DELETE_COLLECTION":
      return { ...state, collections: state.collections.filter(c => c.name !== action.payload) };

    case "SET_AUTH":
      return {
        ...state,
        auth: {
          token: action.payload?.token || "",
          user: action.payload?.user || null,
          isAuthenticated: Boolean(action.payload?.token),
        },
      };

    case "CLEAR_AUTH":
      return {
        ...state,
        auth: {
          token: "",
          user: null,
          isAuthenticated: false,
        },
      };

    default:
      return state;
  }
}

// ── Context ───────────────────────────────────────────────────────────────────

const StoreContext = createContext(null);

export function StoreProvider({ children }) {
  const [state, dispatch] = useReducer(reducer, initialState);

  useEffect(() => {
    if (state.auth.token) {
      localStorage.setItem("auth_token", state.auth.token);
    } else {
      localStorage.removeItem("auth_token");
    }

    if (state.auth.user) {
      localStorage.setItem("auth_user", JSON.stringify(state.auth.user));
    } else {
      localStorage.removeItem("auth_user");
    }
  }, [state.auth.token, state.auth.user]);

  return (
    <StoreContext.Provider value={{ state, dispatch }}>
      {children}
    </StoreContext.Provider>
  );
}

export function useStore() {
  const ctx = useContext(StoreContext);
  if (!ctx) throw new Error("useStore must be used inside <StoreProvider>");
  return ctx;
}
