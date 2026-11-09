/* ==========================================================================
   TokenSentry Documentation - Theme Management
   ========================================================================== */

(function() {
  'use strict';

  // Theme management
  const THEME_KEY = 'tokensentry-theme';
  const THEME_ATTR = 'data-theme';

  function getTheme() {
    return localStorage.getItem(THEME_KEY) || 
           (window.matchMedia('(prefers-color-scheme: dark)').matches ? 'dark' : 'light');
  }

  function setTheme(theme) {
    document.documentElement.setAttribute('data-theme', theme);
    localStorage.setItem(THEME_KEY, theme);
    document.dispatchEvent(new CustomEvent('themechange', { detail: { theme } }));
  }

  function toggleTheme() {
    const current = getTheme();
    const next = current === 'light' ? 'dark' : 'light';
    setTheme(next);
  }

  function getTheme() {
    return document.documentElement.getAttribute('data-theme') || getTheme();
  }

  // Initialize theme on load
  function initTheme() {
    const theme = getTheme();
    document.documentElement.setAttribute('data-theme', theme);
    
    const toggle = document.getElementById('themeToggle');
    if (toggle) {
      toggle.addEventListener('click', toggleTheme);
    }

    // Listen for system changes
    window.matchMedia('(prefers-color-scheme: dark)').addEventListener('change', (e) => {
      if (!localStorage.getItem('tokensentry-theme')) {
        setTheme(e.matches ? 'dark' : 'light');
      }
    });
  }

  // Initialize on DOM ready
  if (document.readyState === 'loading') {
    document.addEventListener('DOMContentLoaded', initTheme);
  } else {
    initTheme();
  }

  // Expose globally
  window.TokensentryTheme = {
    getTheme,
    setTheme,
    toggleTheme
  };
})();