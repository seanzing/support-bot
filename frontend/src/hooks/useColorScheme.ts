import { useCallback, useEffect, useState } from "react";

import { THEME_STORAGE_KEY } from "../lib/config";

export type ColorScheme = "light" | "dark";

function getInitialScheme(): ColorScheme {
  // Always default to dark mode (ZING brand preference)
  // User can toggle to light during session, but each new session starts dark
  return "dark";
}

export function useColorScheme() {
  const [scheme, setScheme] = useState<ColorScheme>(getInitialScheme);

  useEffect(() => {
    if (typeof document === "undefined") return;
    const root = document.documentElement;
    if (scheme === "dark") {
      root.classList.add("dark");
    } else {
      root.classList.remove("dark");
    }
    window.localStorage.setItem(THEME_STORAGE_KEY, scheme);
  }, [scheme]);

  const toggle = useCallback(() => {
    setScheme((current) => (current === "dark" ? "light" : "dark"));
  }, []);

  const setExplicit = useCallback((value: ColorScheme) => {
    setScheme(value);
  }, []);

  return { scheme, toggle, setScheme: setExplicit };
}
