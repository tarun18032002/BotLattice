/**
 * src/components/chat/ChatPage.jsx
 *
 * Assembles the full chat UI.
 * Uses WebSocket (via useChat) instead of direct Anthropic API calls.
 */

import { useChat }              from "../../hooks/useChat";
import { useStore }             from "../../store/useStore";
import { Topbar }               from "../layout/Topbar";
import { ChatControls }         from "./ChatControls";
import { ChatInput }            from "./ChatInput";
import { ChatEmptyState }       from "./ChatEmptyState";
import { WsStatusBadge }        from "./WsStatusBadge";
import { MessageBubble, ThinkingIndicator } from "./MessageBubble";
import { AgentUpdateBubble }    from "./AgentUpdateBubble";

export function ChatPage() {
  const { dispatch } = useStore();

  const {
    messages,
    input, setInput,
    collections,
    collection, setCollection,
    mode, setMode,
    topK, setTopK,
    thinking,
    send,
    clearChat,
    messagesEndRef,
    wsState,
    agent, setAgent,
    sendConfirm,
  } = useChat();

  const goToIngest = () => dispatch({ type: "SET_PAGE", payload: "ingest" });

  return (
    <div className="flex flex-col h-full overflow-hidden">
      {/* Topbar — shows live WS connection badge */}
      <Topbar
        title="Chatbot"
        subtitle="WebSocket · BotLattice RAG backend"
        actions={<WsStatusBadge wsState={wsState} />}
      />

      {/* Collection / mode / top-K controls */}
      <ChatControls
        collections={collections}
        collection={collection}
        onCollectionChange={setCollection}
        mode={mode}
        onModeChange={setMode}
        topK={topK}
        onTopKChange={setTopK}
        onClear={clearChat}
        agent={agent}
        onAgentChange={setAgent}
      />

      {/* Message list */}
      <div className="flex-1 overflow-y-auto px-5 py-4 space-y-4">
        {messages.length === 0 && !thinking ? (
          <ChatEmptyState
            hasCollections={collections.length > 0}
            onGoToIngest={goToIngest}
          />
        ) : (
          <>
            {messages.map((m, i) => (
              <MessageBubble key={i} message={m} />
            ))}
            {messages.map((m, i) => {
              if (m.role === "agent-update") {
                return <AgentUpdateBubble key={i} message={m} />;
              }
              if (m.role === "confirm-intent") {
                return (
                  <AgentUpdateBubble
                    key={i}
                    message={m}
                    onConfirm={sendConfirm}
                    msgIdx={i}
                  />
                );
              }
              return <MessageBubble key={i} message={m} />;
            })}
            {thinking && <ThinkingIndicator />}
            <div ref={messagesEndRef} />
          </>
        )}
      </div>

      <ChatInput
        value={input}
        onChange={setInput}
        onSend={send}
        disabled={thinking}
        placeholder={
          collection
            ? `Ask about "${collection}"…`
            : "Select a collection to get started…"
        }
      />
    </div>
  );
}
