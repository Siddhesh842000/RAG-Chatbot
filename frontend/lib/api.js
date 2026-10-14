// Real API calls to the FastAPI backend.
// Every screen talks to the server only through these three functions.

const API_URL = (process.env.NEXT_PUBLIC_API_URL || "http://localhost:8000").replace(/\/+$/, "");

// The free Render server can take a while to wake up, so the timeouts are generous.
const UPLOAD_TIMEOUT_MS = 120000;
const CHAT_TIMEOUT_MS = 60000;
const CLEAR_TIMEOUT_MS = 20000;

// An error that also remembers the HTTP status (for example 404).
export class ApiError extends Error {
  constructor(message, status) {
    super(message);
    this.name = "ApiError";
    this.status = status;
  }
}

function errorMessage(data, status) {
  // Our backend sends { "detail": "a clear message" }
  if (data && typeof data.detail === "string") return data.detail;
  if (status === 422) return "The request was not valid. Please check your input.";
  return `Something went wrong (error ${status}). Please try again.`;
}

async function request(path, { sessionId, json, formData, timeoutMs }) {
  const headers = {};
  if (sessionId) headers["X-Session-ID"] = sessionId;

  let body;
  if (json !== undefined) {
    headers["Content-Type"] = "application/json";
    body = JSON.stringify(json);
  } else if (formData) {
    body = formData; // the browser sets the multipart header by itself
  }

  const controller = new AbortController();
  const timer = setTimeout(() => controller.abort(), timeoutMs);

  let response;
  try {
    response = await fetch(`${API_URL}${path}`, {
      method: "POST",
      headers,
      body,
      signal: controller.signal,
    });
  } catch (error) {
    if (error.name === "AbortError") {
      throw new Error(
        "The server took too long to respond. It may be waking up, so please try again in a minute."
      );
    }
    throw new Error("Cannot reach the server. Please check your connection or try again later.");
  } finally {
    clearTimeout(timer);
  }

  let data = null;
  try {
    data = await response.json();
  } catch {
    // The response was not JSON
  }

  if (!response.ok) {
    throw new ApiError(errorMessage(data, response.status), response.status);
  }
  return data;
}

export function uploadPdf(file, sessionId) {
  const formData = new FormData();
  formData.append("file", file);
  return request("/api/upload", { sessionId, formData, timeoutMs: UPLOAD_TIMEOUT_MS });
}

export function askQuestion(question, sessionId) {
  return request("/api/chat", { sessionId, json: { question }, timeoutMs: CHAT_TIMEOUT_MS });
}

export function clearDocument(sessionId) {
  return request("/api/clear", { sessionId, timeoutMs: CLEAR_TIMEOUT_MS });
}
