import React from 'react';
import ReactDOM from 'react-dom/client';
import { BrowserRouter, HashRouter } from 'react-router-dom';

const Router =
  import.meta.env.VITE_GITHUB_PAGES === 'true'
    ? HashRouter
    : BrowserRouter;
// Self-hosted fonts (EDU-0044): Be Vietnam Pro for headings (Poppins has no Vietnamese
// glyphs), Inter for body. Only the three weights allowed by the UI spec: 400/600/700.
// Per-weight files declare unicode-range per subset, so browsers fetch only the latin and
// vietnamese files that a page needs (per-subset files omit unicode-range).
import '@fontsource/be-vietnam-pro/600.css';
import '@fontsource/be-vietnam-pro/700.css';
import '@fontsource/inter/400.css';
import '@fontsource/inter/600.css';
import { App } from './app/App';
import { ThemeProvider } from './app/ThemeProvider';
import './app/styles.css';

ReactDOM.createRoot(document.getElementById('root')!).render(
  <React.StrictMode>
    <ThemeProvider>
       <Router>
          <App />
      </Router>
    </ThemeProvider>
  </React.StrictMode>,
);
