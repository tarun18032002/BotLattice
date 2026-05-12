const API_BASE_URL = "http://127.0.0.1:8000";
import { getJson } from "./httpCache";

export async function fetchChunkingOptions(type) {
  return getJson(`${API_BASE_URL}/chunking/options/${type}`, {
    errorMessage: "Failed to fetch chunking options",
  });
}