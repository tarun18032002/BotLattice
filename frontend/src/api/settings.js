const API_BASE_URL = "http://127.0.0.1:8000";
import { getJson, invalidateGetCache } from "./httpCache";

function authHeaders(token) {
  if (!token) return {};
  return { Authorization: `Bearer ${token}` };
}

export async function fetchCurrentSettings(token) {
  const res = await fetch(`${API_BASE_URL}/settings/current/`, {
    method: "GET",
    headers: {
      ...authHeaders(token),
    },
  });

  const data = await res.json().catch(() => ({}));
  if (!res.ok) {
    const detail = data?.detail || "Failed to fetch current settings";
    throw new Error(detail);
  }
  return data;
}

export async function fetchSettingsOptions() {
  return getJson(`${API_BASE_URL}/settings/options/`, {
    errorMessage: "Failed to fetch settings options",
  });
}

export async function saveSettings(payload, token) {
  const res = await fetch(`${API_BASE_URL}/settings/save/`, {
    method: "POST",
    headers: {
      "Content-Type": "application/json",
      ...authHeaders(token),
    },
    body: JSON.stringify(payload),
  });

  const data = await res.json().catch(() => ({}));
  if (!res.ok) {
    const detail = data?.detail || "Failed to save settings";
    throw new Error(detail);
  }

  invalidateGetCache("/settings/");

  return data;
}