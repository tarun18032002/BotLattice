/**
 * src/hooks/useChat.js
 *
 * Manages chat state and drives the WebSocket connection.
 *
 * Flow:
 *   1. On mount   → wsManager.connect()
 *   2. On send    → wsManager.send(question, collection_name)
 *   3. On reply   → append assistant message from WebSocket response
 *   4. On unmount → wsManager.disconnect()
 */

import { useState, useEffect, useRef, useCallback } from "react";
import { wsManager, WS_STATE } from "../services/websocketService";
import { useStore } from "../store/useStore";

export function useChat() {
  const { state } = useStore();
  const { collections, settings } = state;

  // ── Local state ─────────────────────────────────────────────────────────────
  const [messages,   setMessages]   = useState([]);
  const [input,      setInput]      = useState("");
  const [collection, setCollection] = useState("");
  const [mode,       setMode]       = useState("rag");    // "rag" | "direct"
  const [topK,       setTopK]       = useState(settings.defaultTopK ?? 5);
  const [thinking,   setThinking]   = useState(false);
  const [wsState,    setWsState]    = useState(WS_STATE.CLOSED);

  // Pending question reference — used to detect dropped replies
  const pendingQuestion = useRef(null);
  const messagesEndRef  = useRef(null);

  // ── Auto-scroll ──────────────────────────────────────────────────────────────
  useEffect(() => {
    messagesEndRef.current?.scrollIntoView({ behavior: "smooth" });
  }, [messages, thinking]);

  // ── WebSocket lifecycle ──────────────────────────────────────────────────────
  useEffect(() => {
    wsManager.connect(
      // onMessage — backend sends { question, answer }
      (data) => {
        setThinking(false);
        pendingQuestion.current = null;

        // Use real sources from backend if provided,
        // otherwise fall back to placeholder chips.
        // To send real sources, add a "sources" array to your
        // FastAPI response: { question, answer, sources: ["file.pdf", ...] }
        const sources = settings.showSources
          ? (Array.isArray(data.sources) && data.sources.length > 0
              ? data.sources
              : collection ? buildFakeSources(collection, collections) : [])
          : [];

        setMessages((prev) => [
          ...prev,
          {
            role:    "assistant",
            content: data.answer ?? "(empty response)",
            sources,
            ts: new Date().toLocaleTimeString(),
          },
        ]);
      },
      // onStateChange
      (newState) => {
        setWsState(newState);

        // Socket dropped while waiting for a reply → show error bubble
        if (newState === WS_STATE.CLOSED && pendingQuestion.current) {
          setThinking(false);
          setMessages((prev) => [
            ...prev,
            {
              role:    "assistant",
              content: "⚠ Connection lost. Reconnecting…",
              sources: [],
              ts: new Date().toLocaleTimeString(),
            },
          ]);
          pendingQuestion.current = null;
        }
      },
    );

    return () => wsManager.disconnect();
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, []); // mount only

  // ── Send ─────────────────────────────────────────────────────────────────────
  const send = useCallback(() => {
    const text = input.trim();
    if (!text || thinking) return;

    if (mode === "rag" && !collection) {
      alert("Select a collection before sending in RAG mode.");
      return;
    }

    if (wsState !== WS_STATE.OPEN) {
      alert("WebSocket is not connected yet. Please wait a moment.");
      return;
    }

    // Append user bubble immediately
    setMessages((prev) => [
      ...prev,
      { role: "user", content: text, ts: new Date().toLocaleTimeString() },
    ]);

    setInput("");
    setThinking(true);
    pendingQuestion.current = text;

    // ── Send to FastAPI WebSocket ─────────────────────────────────────────────
    // Payload shape: { question: string, collection_name: string }
    const sent = wsManager.send(text, collection || "default");

    if (!sent) {
      setThinking(false);
      pendingQuestion.current = null;
      setMessages((prev) => [
        ...prev,
        {
          role:    "assistant",
          content: "⚠ Failed to send — socket is not open.",
          sources: [],
          ts: new Date().toLocaleTimeString(),
        },
      ]);
    }
  }, [input, thinking, collection, mode, wsState]);

  const clearChat = useCallback(() => setMessages([]), []);

  const activeCollection = collections.find((c) => c.name === collection) ?? null;

  return {
    messages, thinking, messagesEndRef, clearChat,
    input, setInput, send,
    collections, collection, setCollection, activeCollection,
    mode, setMode,
    topK, setTopK,
    wsState,
  };
}

// ── Helpers ───────────────────────────────────────────────────────────────────

/**
 * Placeholder source chips. Replace with real sources from your
 * backend response payload when you add source tracking.
 */
function buildFakeSources(collectionName, collections) {
  const col = collections.find((c) => c.name === collectionName);
  if (!col) return [];
  return [
    `${collectionName}/chunk_${Math.floor(Math.random() * (col.chunks || 10))}.txt`,
    `${collectionName}/doc_${Math.floor(Math.random() * (col.docs || 2)) + 1}.pdf`,
  ];
}
