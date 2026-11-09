/* ==========================================================================
   TokenSentry Documentation - Navigation
   Mobile menu, scroll effects, active states
   ========================================================================== */

(function() {
  'use strict';

  let state = {
    isNavOpen: false,
    lastScroll: 0
  };

  const elements = {
    nav: null,
    navToggle: null,
    navMenu: null,
    navOverlay: null,
    navLinks: null,
    progressBar: null,
    backToTop: null
  };

  function init() {
    cacheElements();
    initMobileMenu();
    initScrollEffects();
    initProgressBar();
    initBackToTop();
    initScrollSpy();
    initSmoothScroll();
  }

  function cacheElements() {
    elements.nav = document.querySelector('.nav');
    elements.navToggle = document.getElementById('navToggle');
    elements.navMenu = document.getElementById('navMenu');
    elements.navOverlay = document.getElementById('navOverlay');
    elements.navLinks = document.querySelectorAll('.nav-link[href^="#"]');
    elements.progressBar = document.getElementById('progressBar');
    elements.backToTop = document.getElementById('backToTop');
  }

  function initMobileMenu() {
    if (!elements.navToggle || !elements.navMenu || !elements.navOverlay) return;

    elements.navToggle.addEventListener('click', toggleMobileMenu);
    elements.navOverlay.addEventListener('click', closeMobileMenu);

    // Close on link click
    document.querySelectorAll('.nav-link').forEach(link => {
      link.addEventListener('click', closeMobileMenu);
    });

    // Close on escape
    document.addEventListener('keydown', (e) => {
      if (e.key === 'Escape' && state.isNavOpen) {
        closeMobileMenu();
      }
    });
  }

  function toggleMobileMenu() {
    state.isNavOpen = !state.isNavOpen;
    document.body.style.overflow = state.isNavOpen ? 'hidden' : '';
    document.getElementById('navToggle')?.setAttribute('aria-expanded', state.isNavOpen);
    document.getElementById('navMenu')?.classList.toggle('open', state.isNavOpen);
    document.getElementById('navOverlay')?.classList.toggle('visible', state.isNavOpen);
  }

  function closeMobileMenu() {
    if (!state.isNavOpen) return;
    state.isNavOpen = false;
    document.getElementById('navToggle')?.setAttribute('aria-expanded', 'false');
    document.getElementById('navMenu')?.classList.remove('open');
    document.getElementById('navOverlay')?.classList.remove('visible');
    document.body.style.overflow = '';
  }

  function initScrollEffects() {
    if (!elements.nav) return;

    let lastScroll = 0;
    let ticking = false;

    window.addEventListener('scroll', () => {
      if (!ticking) {
        window.requestAnimationFrame(() => {
          const currentScroll = window.scrollY;
          const nav = document.querySelector('.nav');

          // Add scrolled class
          if (window.scrollY > 20) {
            nav?.classList.add('scrolled');
          } else {
            nav?.classList.remove('scrolled');
          }

          // Hide/show nav on scroll
          if (currentScroll > lastScroll && currentScroll > 100) {
            nav.style.transform = 'translateY(-100%)';
          } else {
            nav.style.transform = 'translateY(0)';
          }

          lastScroll = currentScroll;
          ticking = false;
        });
      ticking = true;
    }, { passive: true });
  }

  function initProgressBar() {
    const progressBar = document.getElementById('progressBar');
    if (!progressBar) return;

    window.addEventListener('scroll', throttle(() => {
      const scrollTop = window.scrollY;
      const docHeight = document.documentElement.scrollHeight - window.innerHeight;
      const progress = (window.scrollY / (document.documentElement.scrollHeight - window.innerHeight)) * 100;
      document.getElementById('progressBar').style.transform = `scaleX(${progress / 100})`;
    }, 50));
  }

  function initBackToTop() {
    const btn = document.getElementById('backToTop');
    if (!btn) return;

    window.addEventListener('scroll', throttle(() => {
      if (window.scrollY > 300) {
        btn.classList.add('visible');
      } else {
        btn.classList.remove('visible');
      }
    }, 200));

    btn.addEventListener('click', () => {
      window.scrollTo({ top: 0, behavior: 'smooth' });
    });
  }

  function initScrollSpy() {
    const sections = document.querySelectorAll('section[id]');
    const navLinks = document.querySelectorAll('.nav-link[href^="#"]');

    if (!sections.length || !navLinks.length) return;

    const observer = new IntersectionObserver((entries) => {
      entries.forEach(entry => {
        if (entry.isIntersecting) {
          const id = entry.target.getAttribute('id');
          document.querySelectorAll('.nav-link[href^="#"]').forEach(link => {
            link.classList.toggle('active', link.getAttribute('href') === `#${entry.target.id}`);
          });
        }
      });
    }, {
      rootMargin: '-20% 0px -60% 0px',
      threshold: 0.1
    });

    sections.forEach(section => observer.observe(section));
  }

  function initSmoothScroll() {
    document.querySelectorAll('a[href^="#"]').forEach(anchor => {
      anchor.addEventListener('click', function(e) {
        const targetId = this.getAttribute('href');
        if (targetId === '#') return;

        const target = document.querySelector(targetId);
        if (!target) return;

        e.preventDefault();

        const navHeight = document.querySelector('.nav')?.offsetHeight || 0;
        const targetPosition = target.getBoundingClientRect().top + window.scrollY - navHeight - 20;

        window.scrollTo({
          top: targetPosition,
          behavior: 'smooth'
        });

        history.pushState(null, '', targetId);
      });
    });
  }

  function throttle(fn, delay) {
    let lastCall = 0;
    return function(...args) {
      const now = Date.now();
      if (now - lastCall >= delay) {
        fn.apply(this, args);
        lastCall = now;
      }
    };
  }

  if (document.readyState === 'loading') {
    document.addEventListener('DOMContentLoaded', init);
  } else {
    init();
  }
})();