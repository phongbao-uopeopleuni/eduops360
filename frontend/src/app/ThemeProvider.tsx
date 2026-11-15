import { createContext, useContext, useEffect, useState } from 'react';
import type { ReactNode } from 'react';

type ThemeMode = 'light' | 'dark';
type ThemeContextValue = { mode: ThemeMode; setMode: (mode: ThemeMode) => void };
const ThemeContext = createContext<ThemeContextValue | null>(null);

function readPreference(): ThemeMode {
  try {
    const value = localStorage.getItem('eduops.theme');
    if (value === 'light' || value === 'dark') return value;
  } catch {
    // Theme controls remain usable when the browser blocks storage.
  }
  return 'light';
}

export function ThemeProvider({ children }: { children: ReactNode }) {
  const [mode, updateMode] = useState<ThemeMode>(readPreference);

  useEffect(() => {
    document.documentElement.dataset.theme = mode;
  }, [mode]);

  function setMode(value: ThemeMode) {
    updateMode(value);
    try {
      localStorage.setItem('eduops.theme', value);
    } catch {
      // Keep the selection for this tab when persistent storage is unavailable.
    }
  }

  return <ThemeContext.Provider value={{ mode, setMode }}>{children}</ThemeContext.Provider>;
}

export function useTheme() {
  const context = useContext(ThemeContext);
  if (!context) throw new Error('ThemeProvider is required');
  return context;
}
