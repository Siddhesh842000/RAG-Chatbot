// Each visitor gets a random id, saved in the browser.
// The backend uses it (header X-Session-ID) to keep one document per visitor.

const STORAGE_KEY = "rag-chatbot-session-id";

function randomId() {
  if (typeof crypto !== "undefined" && crypto.randomUUID) {
    return crypto.randomUUID();
  }
  return Math.random().toString(36).slice(2) + Date.now().toString(36);
}

// Call this only in the browser (inside event handlers).
export function getSessionId() {
  let id = null;
  try {
    id = window.localStorage.getItem(STORAGE_KEY);
  } catch {
    // Storage can be blocked (private mode). We create a temporary id instead.
  }

  if (!id) {
    id = randomId();
    try {
      window.localStorage.setItem(STORAGE_KEY, id);
    } catch {
      // ignore
    }
  }
  return id;
}
