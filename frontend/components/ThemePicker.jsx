"use client";

import { useSyncExternalStore } from "react";
import { DEFAULT_THEME, THEMES, getTheme, setTheme, subscribeTheme } from "@/lib/theme";

export default function ThemePicker() {
  // Reads the current theme from the <html> element (the server always says "aurora")
  const current = useSyncExternalStore(subscribeTheme, getTheme, () => DEFAULT_THEME);

  return (
    <div
      role="radiogroup"
      aria-label="Color theme"
      className="flex items-center gap-2.5 self-start rounded-full border border-white/10 bg-white/5 px-3 py-2"
    >
      <span className="hidden text-xs font-medium text-zinc-500 sm:inline">Theme</span>
      {THEMES.map((theme) => {
        const active = theme.id === current;
        return (
          <button
            key={theme.id}
            type="button"
            role="radio"
            aria-checked={active}
            aria-label={`${theme.label} theme`}
            title={theme.label}
            onClick={() => setTheme(theme.id)}
            className={`h-7 w-7 rounded-full transition focus-visible:outline-2 focus-visible:outline-offset-2 focus-visible:outline-white ${
              active
                ? "scale-110 ring-2 ring-white ring-offset-2 ring-offset-black"
                : "opacity-60 hover:opacity-100"
            }`}
            style={{ backgroundImage: `linear-gradient(135deg, ${theme.colors.join(", ")})` }}
          />
        );
      })}
    </div>
  );
}
