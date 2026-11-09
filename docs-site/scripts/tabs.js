/* ==========================================================================
   TokenSentry Documentation - Tabs
   ========================================================================== */

(function() {
  'use strict';

  function initTabs() {
    document.querySelectorAll('.tabs').forEach(container => {
      const buttons = container.querySelectorAll('.tab-btn');
      const panels = container.querySelectorAll('.tab-panel');

      if (!buttons.length || !panels.length) return;

      buttons.forEach(btn => {
        btn.addEventListener('click', () => {
          const tabId = btn.dataset.tab;
          if (!tabId) return;

          // Update buttons
          buttons.forEach(b => b.classList.remove('active'));
          btn.classList.add('active');

          // Update panels
          panels.forEach(panel => {
            const isActive = panel.id === `tab-${tabId}`;
            panel.hidden = !isActive;
            panel.classList.toggle('active', isActive);
          });
        });
      });
    });
  }

  // Initialize on DOM ready
  if (document.readyState === 'loading') {
    document.addEventListener('DOMContentLoaded', initTabs);
  } else {
    initTabs();
  }

  // Re-initialize on dynamic content
  document.addEventListener('tokensentry:content-loaded', initTabs);
})();