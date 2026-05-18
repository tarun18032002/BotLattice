const API_BASE_URL = "http://127.0.0.1:8000";
import { getJson } from "./httpCache";

function authHeaders(token) {
  if (!token) return {};
  return { Authorization: `Bearer ${token}` };
}

export async function fetchChunkingOptions(type) {
  return getJson(`${API_BASE_URL}/chunking/options/${type}`, {
    errorMessage: "Failed to fetch chunking options",
  });
}

export async function fetchCurrentChunking(token) {
  const res = await fetch(`${API_BASE_URL}/chunking/current/`, {
    method: "GET",
    headers: {
      ...authHeaders(token),
    },
  });

  const data = await res.json().catch(() => ({}));
  if (!res.ok) {
    throw new Error(data?.detail || "Failed to fetch current chunking config");
  }
  return data;
}

export async function saveChunking(payload, token) {
  const res = await fetch(`${API_BASE_URL}/chunking/save/`, {
    method: "POST",
    headers: {
      "Content-Type": "application/json",
      ...authHeaders(token),
    },
    body: JSON.stringify(payload),
  });

  const data = await res.json().catch(() => ({}));
  if (!res.ok) {
    throw new Error(data?.detail || "Failed to save chunking config");
  }
  return data?.chunking || payload;
}

export async function fetchCurrentCollection(token) {
  const res = await fetch(`${API_BASE_URL}/collection/current/`, {
    method: "GET",
    headers: {
      ...authHeaders(token),
    },
  });

  const data = await res.json().catch(() => ({}));
  if (!res.ok) {
    throw new Error(data?.detail || "Failed to fetch current collection config");
  }
  return data;
}

export async function saveCollection(payload, token) {
  const res = await fetch(`${API_BASE_URL}/collection/save/`, {
    method: "POST",
    headers: {
      "Content-Type": "application/json",
      ...authHeaders(token),
    },
    body: JSON.stringify(payload),
  });

  const data = await res.json().catch(() => ({}));
  if (!res.ok) {
    throw new Error(data?.detail || "Failed to save collection config");
  }
  return data?.collection || payload;
}