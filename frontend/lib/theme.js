// Color themes. The page is always black; the theme changes the accent colors.
// The colors themselves live in app/globals.css (one block per theme id).

export const THEMES = [
  { id: "aurora", label: "Aurora", colors: ["#22d3ee", "#a78bfa", "#f472b6"] },
  { id: "ocean", label: "Ocean", colors: ["#2dd4bf", "#38bdf8", "#6366f1"] },
  { id: "emerald", label: "Emerald", colors: ["#bef264", "#34d399", "#22d3ee"] },
  { id: "sunset", label: "Sunset", colors: ["#fbbf24", "#fb7185", "#e879f9"] },
  { id: "gold", label: "Gold", colors: ["#fde047", "#fbbf24", "#fb923c"] },
];

export const DEFAULT_THEME = "aurora";

const STORAGE_KEY = "rag-chatbot-theme";
const CHANGE_EVENT = "rag-chatbot-theme-change";

// Runs in the <head> before the page is painted, so the saved theme
// is applied immediately and the page does not flash the default colors.
export const themeInitScript = `(function(){try{var ids=${JSON.stringify(
  THEMES.map((t) => t.id)
)};var t=localStorage.getItem("${STORAGE_KEY}");document.documentElement.dataset.theme=ids.indexOf(t)>-1?t:"${DEFAULT_THEME}";}catch(e){}})();`;

// ---- Browser-only helpers (used by components/ThemePicker.jsx) ----

export function getTheme() {
  const current = document.documentElement.dataset.theme;
  return THEMES.some((theme) => theme.id === current) ? current : DEFAULT_THEME;
}

export function setTheme(id) {
  document.documentElement.dataset.theme = id;
  try {
    window.localStorage.setItem(STORAGE_KEY, id);
  } catch {
    // Storage can be blocked. The theme still changes for this visit.
  }
  window.dispatchEvent(new Event(CHANGE_EVENT));
}

export function subscribeTheme(callback) {
  window.addEventListener(CHANGE_EVENT, callback);
  return () => window.removeEventListener(CHANGE_EVENT, callback);
}
