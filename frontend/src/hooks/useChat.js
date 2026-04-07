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

  // ── Agent mode ──────────────────────────────────────────────────────────────
  const [agent, setAgent] = useState("none"); // "none" | "prompt_builder"
  const threadIdRef     = useRef(null);

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
      // onMessage — handles both RAG { question, answer } and agent stream types
      (data) => {
        const msgType = data.type;

        if (msgType === "session_start") {
          threadIdRef.current = data.thread_id;
          return;
        }

        if (msgType === "agent_update") {
          setMessages((prev) => [
            ...prev,
            {
              role: "agent-update",
              node: data.node,
              data: data.data,
              ts: new Date().toLocaleTimeString(),
            },
          ]);
          return;
        }

        if (msgType === "confirm_intent") {
          setThinking(false);
          setMessages((prev) => [
            ...prev,
            {
              role:      "confirm-intent",
              intent:    data.intent,
              message:   data.message,
              thread_id: data.thread_id,
              confirmed: null,
              ts: new Date().toLocaleTimeString(),
            },
          ]);
          return;
        }

        if (msgType === "done") {
          setThinking(false);
          pendingQuestion.current = null;
          return;
        }

        // Default: RAG response { question, answer }
        setThinking(false);
        pendingQuestion.current = null;

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

    if (agent === "none" && mode === "rag" && !collection) {
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
    let sent;
    if (agent === "prompt_builder") {
      sent = wsManager.sendRaw({
        agent:           "prompt_builder",
        question:        text,
        collection_name: collection || "resume",
        thread_id:       threadIdRef.current || undefined,
      });
    } else {
      sent = wsManager.send(text, collection || "default");
    }

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

  const clearChat = useCallback(() => {
    setMessages([]);
    threadIdRef.current = null;
  }, []);

  // ── Confirm / Reject intent (prompt_builder HitL) ─────────────────────────
  const sendConfirm = useCallback((confirmed, msgIdx) => {
    wsManager.sendRaw({ type: "confirm", confirmed });
    setThinking(true);
    setMessages((prev) =>
      prev.map((m, i) => (i === msgIdx ? { ...m, confirmed } : m))
    );
  }, []);

  const activeCollection = collections.find((c) => c.name === collection) ?? null;

  return {
    messages, thinking, messagesEndRef, clearChat,
    input, setInput, send,
    collections, collection, setCollection, activeCollection,
    mode, setMode,
    topK, setTopK,
    wsState,
    agent, setAgent,
    sendConfirm,
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
