/* ==========================================================================
   TokenSentry Documentation - Scroll Spy
   ========================================================================== */

(function() {
  'use strict';

  function initScrollSpy() {
    const sections = document.querySelectorAll('section[id]');
    const navLinks = document.querySelectorAll('.nav-link[href^="#"]');

    if (!sections.length || !navLinks.length) return;

    const observer = new IntersectionObserver((entries) => {
      entries.forEach(entry => {
        if (entry.isIntersecting) {
          const id = entry.target.getAttribute('id');
          document.querySelectorAll('.nav-link[href^="#"]').forEach(link => {
            link.classList.toggle('active', link.getAttribute('href') === `#${id}`);
          });
        }
      });
    }, {
      rootMargin: '-20% 0px -60% 0px',
      threshold: 0.1
    });

    sections.forEach(section => observer.observe(section));
  }

  // Initialize on DOM ready
  if (document.readyState === 'loading') {
    document.addEventListener('DOMContentLoaded', initScrollSpy);
  } else {
    initScrollSpy();
  }

  // Re-initialize on dynamic content
  document.addEventListener('tokensentry:content-loaded', initScrollSpy);
})();