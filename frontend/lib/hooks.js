import { useEffect, useState } from "react";

// Becomes true when something has been "active" (loading) for longer than delayMs.
// We use it to show "the server may be waking up" on the free Render plan.
export function useSlowFlag(active, delayMs = 8000) {
  const [slow, setSlow] = useState(false);

  useEffect(() => {
    if (!active) return undefined;

    const timer = setTimeout(() => setSlow(true), delayMs);
    return () => {
      clearTimeout(timer);
      setSlow(false);
    };
  }, [active, delayMs]);

  return active && slow;
}
