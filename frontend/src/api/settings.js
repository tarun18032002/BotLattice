const API_BASE_URL = "http://127.0.0.1:8000";
import { getJson, invalidateGetCache } from "./httpCache";

export async function fetchCurrentSettings() {
  return getJson(`${API_BASE_URL}/settings/current/`, {
    errorMessage: "Failed to fetch current settings",
  });
}

export async function fetchSettingsOptions() {
  return getJson(`${API_BASE_URL}/settings/options/`, {
    errorMessage: "Failed to fetch settings options",
  });
}

export async function saveSettings(payload) {
  const res = await fetch(`${API_BASE_URL}/settings/save/`, {
    method: "POST",
    headers: {
      "Content-Type": "application/json",
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