// The page has two settings:
//   mode  = the base: "dark" (black) or "light" (white)
//   theme = the accent color: "mono" (black and white) or a color theme
// The actual colors live in app/globals.css.

export const MODES = [
  { id: "dark", label: "Black" },
  { id: "light", label: "White" },
];

export const THEMES = [
  { id: "mono", label: "Mono", colors: ["#fafafa", "#a1a1aa", "#3f3f46"] },
  { id: "aurora", label: "Aurora", colors: ["#22d3ee", "#a78bfa", "#f472b6"] },
  { id: "ocean", label: "Ocean", colors: ["#2dd4bf", "#38bdf8", "#6366f1"] },
  { id: "emerald", label: "Emerald", colors: ["#bef264", "#34d399", "#22d3ee"] },
  { id: "sunset", label: "Sunset", colors: ["#fbbf24", "#fb7185", "#e879f9"] },
  { id: "gold", label: "Gold", colors: ["#fde047", "#fbbf24", "#fb923c"] },
];

// Default look: black and white
export const DEFAULT_MODE = "dark";
export const DEFAULT_THEME = "mono";

const THEME_KEY = "rag-chatbot-theme";
const MODE_KEY = "rag-chatbot-mode";
const CHANGE_EVENT = "rag-chatbot-theme-change";

// Runs in the <head> before the page is painted, so the saved choice
// is applied immediately and the page does not flash the default look.
export const themeInitScript = `(function(){try{var d=document.documentElement;var themes=${JSON.stringify(
  THEMES.map((t) => t.id)
)};var modes=${JSON.stringify(MODES.map((m) => m.id))};var t=localStorage.getItem("${THEME_KEY}");var m=localStorage.getItem("${MODE_KEY}");d.dataset.theme=themes.indexOf(t)>-1?t:"${DEFAULT_THEME}";d.dataset.mode=modes.indexOf(m)>-1?m:"${DEFAULT_MODE}";}catch(e){}})();`;

// ---- Browser-only helpers (used by components/ThemePicker.jsx) ----

export function getTheme() {
  const current = document.documentElement.dataset.theme;
  return THEMES.some((theme) => theme.id === current) ? current : DEFAULT_THEME;
}

export function getMode() {
  const current = document.documentElement.dataset.mode;
  return MODES.some((mode) => mode.id === current) ? current : DEFAULT_MODE;
}

function save(key, value) {
  try {
    window.localStorage.setItem(key, value);
  } catch {
    // Storage can be blocked. The choice still works for this visit.
  }
}

export function setTheme(id) {
  document.documentElement.dataset.theme = id;
  save(THEME_KEY, id);
  window.dispatchEvent(new Event(CHANGE_EVENT));
}

export function setMode(id) {
  document.documentElement.dataset.mode = id;
  save(MODE_KEY, id);
  window.dispatchEvent(new Event(CHANGE_EVENT));
}

export function subscribeTheme(callback) {
  window.addEventListener(CHANGE_EVENT, callback);
  return () => window.removeEventListener(CHANGE_EVENT, callback);
}
