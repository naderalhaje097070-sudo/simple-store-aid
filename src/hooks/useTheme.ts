import { useState, useEffect, useCallback } from "react";

type Theme = "light" | "dark";
const STORAGE_KEY = "mongezz-theme";

export function useTheme() {
  const [theme, setThemeState] = useState<Theme>(() => {
    if (typeof window === "undefined") return "light";
    try {
      const stored = window.localStorage.getItem(STORAGE_KEY) as Theme | null;
      if (stored === "dark" || stored === "light") return stored;
    } catch { /* ignore */ }
    return "light";
  });

  useEffect(() => {
    const root = document.documentElement;
    const isDark = theme === "dark";
    root.classList.toggle("dark", isDark);

    // Update theme-color meta for mobile browsers
    const meta = document.querySelector('meta[name="theme-color"]') as HTMLMetaElement | null;
    if (meta) {
      meta.content = isDark ? "#0a1a16" : "#0E7C66";
    }

    try {
      window.localStorage.setItem(STORAGE_KEY, theme);
    } catch { /* ignore */ }
  }, [theme]);

  const setTheme = useCallback((t: Theme) => setThemeState(t), []);
  const toggleTheme = useCallback(() => setThemeState((prev) => (prev === "dark" ? "light" : "dark")), []);

  return { theme, setTheme, toggleTheme };
}
