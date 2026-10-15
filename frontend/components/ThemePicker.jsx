"use client";

import { useEffect, useRef, useState, useSyncExternalStore } from "react";
import {
  DEFAULT_MODE,
  DEFAULT_THEME,
  MODES,
  THEMES,
  getMode,
  getTheme,
  setMode,
  setTheme,
  subscribeTheme,
} from "@/lib/theme";

const gradient = (colors) => `linear-gradient(135deg, ${colors.join(", ")})`;

export default function ThemePicker() {
  const [open, setOpen] = useState(false);
  const rootRef = useRef(null);
  const buttonRef = useRef(null);

  // The current choice is read from the <html> element (the server always says mono + dark)
  const theme = useSyncExternalStore(subscribeTheme, getTheme, () => DEFAULT_THEME);
  const mode = useSyncExternalStore(subscribeTheme, getMode, () => DEFAULT_MODE);
  const currentTheme = THEMES.find((item) => item.id === theme) ?? THEMES[0];

  // Close the menu when the user clicks outside it or presses Escape
  useEffect(() => {
    if (!open) return undefined;

    function handlePointerDown(event) {
      if (rootRef.current && !rootRef.current.contains(event.target)) setOpen(false);
    }
    function handleKeyDown(event) {
      if (event.key === "Escape") {
        setOpen(false);
        buttonRef.current?.focus();
      }
    }

    document.addEventListener("pointerdown", handlePointerDown);
    document.addEventListener("keydown", handleKeyDown);
    return () => {
      document.removeEventListener("pointerdown", handlePointerDown);
      document.removeEventListener("keydown", handleKeyDown);
    };
  }, [open]);

  return (
    <div ref={rootRef} className="relative self-start">
      <button
        ref={buttonRef}
        type="button"
        onClick={() => setOpen((value) => !value)}
        aria-haspopup="dialog"
        aria-expanded={open}
        className="btn-ghost !rounded-full !py-2 !pl-3 !pr-3.5"
      >
        <span
          className="h-4 w-4 rounded-full ring-1 ring-line-strong"
          style={{ backgroundImage: gradient(currentTheme.colors) }}
          aria-hidden="true"
        />
        <span>Theme</span>
        <svg
          viewBox="0 0 20 20"
          className={`h-4 w-4 text-subtle transition-transform ${open ? "rotate-180" : ""}`}
          fill="none"
          stroke="currentColor"
          strokeWidth="2"
          strokeLinecap="round"
          strokeLinejoin="round"
          aria-hidden="true"
        >
          <path d="M5 8l5 5 5-5" />
        </svg>
      </button>

      {open && (
        <div
          role="dialog"
          aria-label="Theme settings"
          className="absolute left-0 z-20 mt-2 w-72 max-w-[calc(100vw-2rem)] rounded-2xl border border-line-strong bg-panel p-3 shadow-2xl shadow-black/30 sm:left-auto sm:right-0"
        >
          <p className="px-1 text-[11px] font-semibold uppercase tracking-wider text-subtle">Mode</p>
          <div role="radiogroup" aria-label="Mode" className="mt-2 grid grid-cols-2 gap-1 rounded-xl bg-field p-1">
            {MODES.map((item) => {
              const active = item.id === mode;
              return (
                <button
                  key={item.id}
                  type="button"
                  role="radio"
                  aria-checked={active}
                  onClick={() => setMode(item.id)}
                  className={`rounded-lg px-3 py-2 text-sm font-medium transition ${
                    active ? "bg-fg text-page" : "text-muted hover:text-fg"
                  }`}
                >
                  {item.label}
                </button>
              );
            })}
          </div>

          <p className="mt-4 px-1 text-[11px] font-semibold uppercase tracking-wider text-subtle">Color</p>
          <div role="radiogroup" aria-label="Color" className="mt-2 space-y-1">
            {THEMES.map((item) => {
              const active = item.id === theme;
              return (
                <button
                  key={item.id}
                  type="button"
                  role="radio"
                  aria-checked={active}
                  onClick={() => setTheme(item.id)}
                  className={`flex w-full items-center gap-3 rounded-xl px-2.5 py-2 text-left text-sm transition ${
                    active ? "bg-hover text-fg" : "text-muted hover:bg-hover hover:text-fg"
                  }`}
                >
                  <span
                    className="h-5 w-5 shrink-0 rounded-full ring-1 ring-line-strong"
                    style={{ backgroundImage: gradient(item.colors) }}
                    aria-hidden="true"
                  />
                  <span className="flex-1">{item.label}</span>
                  {active && (
                    <svg viewBox="0 0 20 20" className="h-4 w-4" fill="none" stroke="currentColor" strokeWidth="2.5" strokeLinecap="round" strokeLinejoin="round" aria-hidden="true">
                      <path d="M4 10.5l4 4 8-9" />
                    </svg>
                  )}
                </button>
              );
            })}
          </div>
        </div>
      )}
    </div>
  );
}
