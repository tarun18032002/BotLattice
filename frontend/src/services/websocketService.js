/**
 * src/services/websocketService.js
 *
 * Manages the WebSocket connection to the BotLattice FastAPI backend.
 * Endpoint: ws://127.0.0.1:8000/ws/chat
 *
 * Protocol (matches your FastAPI router):
 *   SEND:    { question: string, collection_name: string, top_k?: number, retrieval_settings?: object }
 *   RECEIVE: { question: string, answer: string }
 */

const WS_BASE_URL = import.meta.env.VITE_WS_URL ?? "ws://127.0.0.1:8000/ws/chat";

// ── Connection states ─────────────────────────────────────────────────────────
export const WS_STATE = {
  CONNECTING:  "connecting",
  OPEN:        "open",
  CLOSED:      "closed",
  ERROR:       "error",
};

// ── Singleton socket manager ──────────────────────────────────────────────────
class WebSocketManager {
  constructor() {
    this._socket        = null;
    this._onMessage     = null;   // (data: {question, answer}) => void
    this._onStateChange = null;   // (state: WS_STATE) => void
    this._reconnectTimer = null;
    this._shouldReconnect = false;
    this._token         = null;   // Store token for reconnections
  }

  /** Current raw WebSocket readyState mapped to WS_STATE */
  get state() {
    if (!this._socket) return WS_STATE.CLOSED;
    switch (this._socket.readyState) {
      case WebSocket.CONNECTING: return WS_STATE.CONNECTING;
      case WebSocket.OPEN:       return WS_STATE.OPEN;
      default:                   return WS_STATE.CLOSED;
    }
  }

  /**
   * Open the WebSocket connection with authentication token.
   * @param {string} token           - Authentication token from localStorage
   * @param {Function} onMessage     - called with each parsed response
   * @param {Function} onStateChange - called when connection state changes
   */
  connect(token, onMessage, onStateChange) {
    if (!token) {
      console.error("[WS] Authentication token is required");
      throw new Error("Authentication token is required for WebSocket connection");
    }
    
    this._token = token;
    this._onMessage     = onMessage;
    this._onStateChange = onStateChange;
    this._shouldReconnect = true;
    this._open();
  }

  /** Close the connection and stop reconnect attempts. */
  disconnect() {
    this._shouldReconnect = false;
    clearTimeout(this._reconnectTimer);
    if (this._socket) {
      this._socket.close();
      this._socket = null;
    }
    this._emit(WS_STATE.CLOSED);
  }

  /**
   * Send a RAG chat message to the backend.
   * @param {string} question        - The user's question
   * @param {string} collection_name - Active collection name (defaults to 'resume')
   * @param {object} options         - Optional query overrides
   * @returns {boolean}              - false if socket not open
   */
  send(question, collection_name = "resume", options = {}) {
    if (!this._socket || this._socket.readyState !== WebSocket.OPEN) {
      console.warn("[WS] Socket not open. State:", this._socket?.readyState, "Expected:", WebSocket.OPEN);
      return false;
    }
    const payload = {
      question,
      collection_name,
      ...(options || {}),
    };
    console.log("[WS] Sending RAG query:", payload);
    this._socket.send(JSON.stringify(payload));
    return true;
  }

  // ── Private ────────────────────────────────────────────────────────────────

  _open() {
    this._emit(WS_STATE.CONNECTING);

    try {
      // Append token to WebSocket URL as query parameter
      const wsUrl = `${WS_BASE_URL}?token=${encodeURIComponent(this._token)}`;
      this._socket = new WebSocket(wsUrl);
      console.log("[WS] Attempting to connect to:", wsUrl.replace(/token=[^&]*/g, 'token=***'), {
        timestamp: new Date().toISOString(),
        readyState: this._socket?.readyState,
        hasToken: !!this._token,
        fullUrl: wsUrl.substring(0, 50) + "...",
      });
    } catch (err) {
      console.error("[WS] Failed to construct WebSocket:", err);
      this._emit(WS_STATE.ERROR);
      this._scheduleReconnect();
      return;
    }

    this._socket.onopen = () => {
      console.log("[WS] Connected ✓", WS_BASE_URL, {
        timestamp: new Date().toISOString(),
        readyState: this._socket?.readyState,
      });
      this._emit(WS_STATE.OPEN);
    };

    this._socket.onmessage = (event) => {
      console.log("[WS] Received:", event.data);
      try {
        const data = JSON.parse(event.data);
        this._onMessage?.(data);
      } catch (err) {
        console.error("[WS] Failed to parse message:", err, event.data);
      }
    };

    this._socket.onerror = (err) => {
      console.error("[WS] Error Event:", {
        type: err.type,
        message: err.message,
        readyState: this._socket?.readyState,
        url: this._socket?.url,
        timestamp: new Date().toISOString(),
        browserInfo: navigator.userAgent,
      });
      this._emit(WS_STATE.ERROR);
    };

    this._socket.onclose = (event) => {
      const closeReason = (() => {
        if (event.code === 4001) return "Authentication failed or expired";
        if (!event.wasClean) return `Unexpected close (code: ${event.code})`;
        return event.reason || "(no reason)";
      })();
      
      console.log(`[WS] Closed — code: ${event.code}, wasClean: ${event.wasClean}`, {
        reason: closeReason,
        timestamp: new Date().toISOString(),
        url: this._socket?.url,
      });
      this._emit(WS_STATE.CLOSED);
      if (this._shouldReconnect) this._scheduleReconnect();
    };
  }

  _scheduleReconnect(delay = 3000) {
    console.log(`[WS] Reconnecting in ${delay}ms…`);
    clearTimeout(this._reconnectTimer);
    this._reconnectTimer = setTimeout(() => {
      if (this._shouldReconnect) this._open();
    }, delay);
  }

  _emit(state) {
    this._onStateChange?.(state);
  }

  /**
   * Send any raw JSON payload to the backend.
   * Used for agent messages and confirm/reject responses.
   * @param {object} payload
   * @returns {boolean}
   */
  sendRaw(payload) {
    if (!this._socket || this._socket.readyState !== WebSocket.OPEN) {
      console.warn("[WS] Socket not open for raw send");
      return false;
    }
    console.log("[WS] Sending raw payload:", payload);
    this._socket.send(JSON.stringify(payload));
    return true;
  }
}

// Export a single shared instance
export const wsManager = new WebSocketManager();
