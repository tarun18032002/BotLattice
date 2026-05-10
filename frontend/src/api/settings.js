const API_BASE_URL = "http://127.0.0.1:8000";

export async function fetchCurrentSettings() {
  const res = await fetch(`${API_BASE_URL}/settings/current/`, {
    method: "GET",
  });

  if (!res.ok) {
    throw new Error("Failed to fetch current settings");
  }

  return res.json();
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

  return data;
}