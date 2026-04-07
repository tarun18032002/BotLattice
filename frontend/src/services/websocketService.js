/**
 * src/services/websocketService.js
 *
 * Manages the WebSocket connection to the BotLattice FastAPI backend.
 * Endpoint: ws://localhost:8000/ws/chat
 *
 * Protocol (matches your FastAPI router):
 *   SEND:    { question: string, collection_name: string }
 *   RECEIVE: { question: string, answer: string }
 */

const WS_URL = import.meta.env.VITE_WS_URL ?? "ws://localhost:8000/ws/chat";

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
   * Open the WebSocket connection.
   * @param {Function} onMessage     - called with each parsed response
   * @param {Function} onStateChange - called when connection state changes
   */
  connect(onMessage, onStateChange) {
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
   * Send a chat message to the backend.
   * @param {string} question        - The user's question
   * @param {string} collection_name - Active collection name
   * @returns {boolean}              - false if socket not open
   */
  send(question, collection_name) {
    if (!this._socket || this._socket.readyState !== WebSocket.OPEN) return false;
    this._socket.send(JSON.stringify({ question, collection_name }));
    return true;
  }

  // ── Private ────────────────────────────────────────────────────────────────

  _open() {
    this._emit(WS_STATE.CONNECTING);

    try {
      this._socket = new WebSocket(WS_URL);
    } catch (err) {
      console.error("[WS] Failed to construct WebSocket:", err);
      this._emit(WS_STATE.ERROR);
      this._scheduleReconnect();
      return;
    }

    this._socket.onopen = () => {
      console.log("[WS] Connected →", WS_URL);
      this._emit(WS_STATE.OPEN);
    };

    this._socket.onmessage = (event) => {
      try {
        const data = JSON.parse(event.data);
        this._onMessage?.(data);
      } catch (err) {
        console.error("[WS] Failed to parse message:", err, event.data);
      }
    };

    this._socket.onerror = (err) => {
      console.error("[WS] Error:", err);
      this._emit(WS_STATE.ERROR);
    };

    this._socket.onclose = (event) => {
      console.log(`[WS] Closed — code: ${event.code}`);
      this._emit(WS_STATE.CLOSED);
      if (this._shouldReconnect) this._scheduleReconnect();
    };
  }

  _scheduleReconnect(delay = 3000) {
    console.log(`[WS] Reconnecting in ${delay}ms…`);
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
    if (!this._socket || this._socket.readyState !== WebSocket.OPEN) return false;
    this._socket.send(JSON.stringify(payload));
    return true;
  }
}

// Export a single shared instance
export const wsManager = new WebSocketManager();
