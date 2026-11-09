/* ==========================================================================
   TokenSentry Documentation - Main JavaScript
   Core functionality and initialization
   ========================================================================== */

(function() {
  'use strict';

  // Global state
  const state = {
    theme: 'light',
    isNavOpen: false,
    isCmdPaletteOpen: false,
    scrollY: 0,
    observer: null
  };

  // DOM Elements
  const elements = {};

  // Initialize on DOM ready
  document.addEventListener('DOMContentLoaded', init);

  function init() {
    cacheElements();
    initTheme();
    initNavigation();
    initProgressBar();
    initBackToTop();
    initScrollSpy();
    initTabs();
    initCodeBlocks();
    initAnimations();
    initSearch();
    initCommandPalette();
    initSmoothScroll();
    initCopyButtons();
    initImages();
    initModals();
    initTooltips();
    initDropdowns();
    initAccordions();
    
    // Mark page as loaded
    document.body.classList.add('loaded');
    
    // Dispatch ready event
    document.dispatchEvent(new CustomEvent('tokensentry:ready'));
  }

  function cacheElements() {
    elements = {
      themeToggle: document.getElementById('themeToggle'),
      nav: document.getElementById('nav'),
      navToggle: document.getElementById('navToggle'),
      navMenu: document.getElementById('navMenu'),
      navOverlay: document.getElementById('navOverlay'),
      progressBar: document.getElementById('progressBar'),
      backToTop: document.getElementById('backToTop'),
      navLinks: document.querySelectorAll('.nav-link'),
      tabBtns: document.querySelectorAll('.tab-btn'),
      tabPanels: document.querySelectorAll('.tab-panel'),
      codeBlocks: document.querySelectorAll('pre code'),
      images: document.querySelectorAll('img:not([loading="eager"])'),
      modals: document.querySelectorAll('.modal'),
      dropdowns: document.querySelectorAll('.dropdown'),
      accordions: document.querySelectorAll('.accordion'),
      tooltips: document.querySelectorAll('.tooltip'),
      copyButtons: document.querySelectorAll('.code-action-btn'),
      backToTop: document.getElementById('backToTop')
    };
  }

  // ==========================================================================
  // Theme Management
  // ==========================================================================
  function initTheme() {
    // Get saved theme or detect system preference
    const savedTheme = localStorage.getItem('tokensentry-theme');
    const prefersDark = window.matchMedia('(prefers-color-scheme: dark)').matches;
    const theme = savedTheme || (prefersDark ? 'dark' : 'light');
    
    applyTheme(theme);
    
    if (elements.themeToggle) {
      elements.themeToggle.addEventListener('click', toggleTheme);
    }
    
    // Listen for system theme changes
    window.matchMedia('(prefers-color-scheme: dark)').addEventListener('change', (e) => {
      if (!localStorage.getItem('tokensentry-theme')) {
        applyTheme(e.matches ? 'dark' : 'light');
      }
    });
  }

  function applyTheme(theme) {
    document.documentElement.setAttribute('data-theme', theme);
    localStorage.setItem('tokensentry-theme', theme);
    state.theme = theme;
    
    // Update meta theme-color
    const metaThemeColor = document.querySelector('meta[name="theme-color"]');
    if (metaThemeColor) {
      metaThemeColor.setAttribute('content', theme === 'dark' ? '#1a1a18' : '#fefef8');
    }
    
    // Dispatch theme change event
    document.dispatchEvent(new CustomEvent('themechange', { detail: { theme } }));
  }

  function toggleTheme() {
    const newTheme = state.theme === 'light' ? 'dark' : 'light';
    
    // Add transition class for smooth animation
    document.body.classList.add('theme-transitioning');
    
    applyTheme(newTheme);
    
    // Show toast notification
    showThemeToast(newTheme);
    
    // Remove transition class after animation
    setTimeout(() => {
      document.body.classList.remove('theme-transitioning');
    }, 300);
  }

  function showThemeToast(theme) {
    const toast = document.createElement('div');
    toast.className = 'theme-toast';
    toast.innerHTML = `
      <i data-lucide="${theme === 'dark' ? 'moon' : 'sun'}"></i>
      <span>Switched to ${theme} mode</span>
    `;
    document.body.appendChild(toast);
    
    // Trigger reflow
    toast.offsetHeight;
    toast.classList.add('show');
    
    setTimeout(() => {
      toast.classList.remove('show');
      setTimeout(() => toast.remove(), 300);
    }, 2000);
  }

  // ==========================================================================
  // Navigation
  // ==========================================================================
  function initNavigation() {
    if (!elements.navToggle || !elements.navMenu || !elements.navOverlay) return;

    // Toggle mobile menu
    elements.navToggle.addEventListener('click', toggleMobileMenu);
    elements.navOverlay.addEventListener('click', closeMobileMenu);

    // Close menu on link click
    elements.navMenu.querySelectorAll('.nav-link').forEach(link => {
      link.addEventListener('click', closeMobileMenu);
    });

    // Close on escape
    document.addEventListener('keydown', (e) => {
      if (e.key === 'Escape' && state.isNavOpen) {
        closeMobileMenu();
      }
    });

    // Scroll effect on nav
    let lastScroll = 0;
    window.addEventListener('scroll', throttle(() => {
      const currentScroll = window.scrollY;
      const nav = elements.nav;
      
      if (currentScroll > 100) {
        nav.classList.add('scrolled');
      } else {
        nav.classList.remove('scrolled');
      }
      
      if (currentScroll > lastScroll && currentScroll > 100) {
        nav.style.transform = 'translateY(-100%)';
      } else {
        nav.style.transform = 'translateY(0)';
      }
      
      lastScroll = currentScroll;
    }, 100));
  }

  function toggleMobileMenu() {
    state.isNavOpen = !state.isNavOpen;
    elements.navToggle.setAttribute('aria-expanded', state.isNavOpen);
    elements.navMenu.classList.toggle('open', state.isNavOpen);
    elements.navOverlay.classList.toggle('visible', state.isNavOpen);
    document.body.style.overflow = state.isNavOpen ? 'hidden' : '';
  }

  function closeMobileMenu() {
    if (!state.isNavOpen) return;
    state.isNavOpen = false;
    elements.navToggle.setAttribute('aria-expanded', 'false');
    elements.navMenu.classList.remove('open');
    elements.navOverlay.classList.remove('visible');
    document.body.style.overflow = '';
  }

  // ==========================================================================
  // Progress Bar
  // ==========================================================================
  function initProgressBar() {
    if (!elements.progressBar) return;

    window.addEventListener('scroll', throttle(() => {
      const scrollTop = window.scrollY;
      const docHeight = document.documentElement.scrollHeight - window.innerHeight;
      const progress = (scrollTop / docHeight) * 100;
      elements.progressBar.style.transform = `scaleX(${progress / 100})`;
    }, 50));
  }

  // ==========================================================================
  // Back to Top
  // ==========================================================================
  function initBackToTop() {
    if (!elements.backToTop) return;

    window.addEventListener('scroll', throttle(() => {
      if (window.scrollY > 300) {
        elements.backToTop.classList.add('visible');
      } else {
        elements.backToTop.classList.remove('visible');
      }
    }, 200));

    elements.backToTop.addEventListener('click', () => {
      window.scrollTo({ top: 0, behavior: 'smooth' });
    });
  }

  // ==========================================================================
  // Scroll Spy
  ==========================================================================
  function initScrollSpy() {
    const sections = document.querySelectorAll('section[id]');
    const navLinks = document.querySelectorAll('.nav-link[href^="#"]');
    
    if (!sections.length || !navLinks.length) return;

    const observer = new IntersectionObserver((entries) => {
      entries.forEach(entry => {
        if (entry.isIntersecting) {
          const id = entry.target.getAttribute('id');
          navLinks.forEach(link => {
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

  // ==========================================================================
  // Tabs
  ==========================================================================
  function initTabs() {
    const tabContainers = document.querySelectorAll('.tabs');
    
    tabContainers.forEach(container => {
      const buttons = container.querySelectorAll('.tab-btn');
      const panels = container.querySelectorAll('.tab-panel');
      
      buttons.forEach(btn => {
        btn.addEventListener('click', () => {
          const tabId = btn.dataset.tab;
          
          // Update buttons
          buttons.forEach(b => b.classList.remove('active'));
          btn.classList.add('active');
          
          // Update panels
          panels.forEach(panel => {
            panel.hidden = panel.id !== `tab-${tabId}`;
            panel.classList.toggle('active', panel.id === `tab-${tabId}`);
          });
        });
      });
    });
  }

  // ==========================================================================
  // Code Blocks
  ==========================================================================
  function initCodeBlocks() {
    // Add copy buttons
    document.querySelectorAll('pre').forEach(pre => {
      if (pre.querySelector('.code-actions')) return;
      
      const header = document.createElement('div');
      header.className = 'code-header';
      header.innerHTML = `
        <span class="code-language">${getLanguage(pre)}</span>
        <div class="code-actions">
          <button class="code-action-btn" aria-label="Copy code" title="Copy to clipboard">
            <svg xmlns="http://www.w3.org/2000/svg" width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><rect x="9" y="9" width="13" height="13" rx="2" ry="2"></rect><path d="M5 15H4a2 2 0 0 1-2-2V4a2 2 0 0 1 2-2h9a2 2 0 0 1 2 2v1"></path></svg>
          </button>
        </div>
      `;
      
      pre.insertBefore(header, pre.firstChild);
      
      const copyBtn = header.querySelector('.code-action-btn');
      copyBtn.addEventListener('click', () => copyCode(pre));
    });

    // Initialize syntax highlighting if Prism is available
    if (window.Prism) {
      Prism.highlightAll();
    }
  }

  function getLanguage(pre) {
    const code = pre.querySelector('code');
    if (!code) return 'text';
    
    const className = code.className || '';
    const match = className.match(/language-(\w+)/);
    return match ? match[1] : 'text';
  }

  async function copyCode(pre) {
    const code = pre.querySelector('code').textContent;
    
    try {
      await navigator.clipboard.writeText(code);
      showCopyNotification('Copied!');
    } catch (err) {
      fallbackCopy(code);
      showCopyNotification('Copied!');
    }
  }

  function fallbackCopy(text) {
    const textarea = document.createElement('textarea');
    textarea.value = text;
    textarea.style.position = 'fixed';
    textarea.style.opacity = '0';
    document.body.appendChild(textarea);
    textarea.select();
    document.execCommand('copy');
    document.body.removeChild(textarea);
  }

  function showCopyNotification(message) {
    const notification = document.createElement('div');
    notification.className = 'copy-notification';
    notification.innerHTML = `
      <svg xmlns="http://www.w3.org/2000/svg" width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><polyline points="20 6 9 17 4 12"></polyline></svg>
      <span>${message}</span>
    `;
    
    document.body.appendChild(notification);
    
    requestAnimationFrame(() => {
      notification.classList.add('show');
    });
    
    setTimeout(() => {
      notification.classList.remove('show');
      setTimeout(() => notification.remove(), 300);
    }, 2000);
  }

  // ==========================================================================
   // Animations & Scroll Reveal
  // ==========================================================================
  function initAnimations() {
    // Intersection Observer for scroll reveal
    const revealObserver = new IntersectionObserver((entries) => {
      entries.forEach(entry => {
        if (entry.isIntersecting) {
          entry.target.classList.add('revealed');
        }
      });
    }, {
      rootMargin: '0px 0px -50px 0px',
      threshold: 0.1
    });

    document.querySelectorAll('.reveal-on-scroll, [data-animate]').forEach(el => {
      revealObserver.observe(el);
    });

    // Staggered animations for grid items
    const grids = document.querySelectorAll('.features-grid, .docs-grid, .contribute-grid, .quickstart-grid, .examples-grid');
    
    grids.forEach(grid => {
      const items = grid.children;
      const observer = new IntersectionObserver((entries) => {
        entries.forEach((entry, index) => {
          if (entry.isIntersecting) {
            const children = Array.from(entry.target.children);
            children.forEach((child, i) => {
              child.style.animationDelay = `${i * 100}ms`;
              child.classList.add('visible');
            });
            observer.unobserve(entry.target);
          }
        });
      }, { threshold: 0.1 });
      
      observer.observe(grid);
    });
  }

  // ==========================================================================
  // Search
  // ==========================================================================
  function initSearch() {
    const searchInput = document.querySelector('.search-input');
    if (!searchInput) return;

    const searchResults = searchInput.closest('.search').querySelector('.search-results');
    let debounceTimer = null;

    searchInput.addEventListener('input', () => {
      clearTimeout(debounceTimer);
      debounceTimer = setTimeout(() => {
        const query = searchInput.value.toLowerCase().trim();
        if (query.length < 2) {
          closeSearchResults();
          return;
        }
        showSearchResults(query);
      }, 200);
    });

    searchInput.addEventListener('focus', () => {
      if (searchInput.value.trim().length >= 2) {
        showSearchResults(searchInput.value.toLowerCase().trim());
      }
    });

    document.addEventListener('click', (e) => {
      if (!e.target.closest('.search')) {
        closeSearchResults();
      }
    });

    function showSearchResults(query) {
      // This would integrate with a search index
      // For now, we'll just show a placeholder
      const results = searchIndex(query);
      renderSearchResults(results);
    }

    function closeSearchResults() {
      const results = document.querySelector('.search-results');
      if (results) results.classList.remove('open');
    }
  }

  function searchIndex(query) {
    // Placeholder - would integrate with actual search index
    return [];
  }

  function renderSearchResults(results) {
    // Implementation would render search results
  }

  // ==========================================================================
  // Command Palette
  // ==========================================================================
  function initCommandPalette() {
    const palette = document.querySelector('.cmd-palette');
    const overlay = document.querySelector('.cmd-palette-overlay');
    const input = document.querySelector('.cmd-palette-input');
    const results = document.querySelector('.cmd-palette-results');
    
    if (!palette || !input) return;

    // Open with Cmd/Ctrl + K
    document.addEventListener('keydown', (e) => {
      if ((e.metaKey || e.ctrlKey) && e.key === 'k') {
        e.preventDefault();
        openCommandPalette();
      }
    });

    if (overlay) {
      overlay.addEventListener('click', closeCommandPalette);
    }

    input.addEventListener('keydown', (e) => {
      if (e.key === 'Escape') {
        closeCommandPalette();
      }
    });

    // Close on overlay click
    document.addEventListener('keydown', (e) => {
      if (e.key === 'Escape' && palette.classList.contains('open')) {
        closeCommandPalette();
      }
    });
  }

  function openCommandPalette() {
    const palette = document.querySelector('.cmd-palette');
    const overlay = document.querySelector('.cmd-palette-overlay');
    const input = document.querySelector('.cmd-palette-input');
    
    if (!palette || !overlay) return;
    
    palette.classList.add('open');
    overlay.classList.add('visible');
    document.body.style.overflow = 'hidden';
    
    setTimeout(() => {
      const input = document.querySelector('.cmd-palette-input');
      if (input) input.focus();
    }, 50);
  }

  function closeCommandPalette() {
    const palette = document.querySelector('.cmd-palette');
    const overlay = document.querySelector('.cmd-palette-overlay');
    
    if (!palette) return;
    
    palette.classList.remove('open');
    overlay.classList.remove('visible');
    document.body.style.overflow = '';
  }

  // ==========================================================================
  // Smooth Scroll
  // ==========================================================================
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
        
        // Update URL without scroll
        history.pushState(null, '', targetId);
      });
    });
  }

  // ==========================================================================
  // Copy Buttons
  // ==========================================================================
  function initCopyButtons() {
    document.addEventListener('click', async (e) => {
      const btn = e.target.closest('[data-copy]');
      if (!btn) return;
      
      const text = btn.dataset.copy;
      if (!text) return;
      
      try {
        await navigator.clipboard.writeText(text);
        showToast('Copied to clipboard!');
      } catch (err) {
        fallbackCopyToClipboard(text);
        showToast('Copied!');
      }
    });
  }

  function showToast(message) {
    const toast = document.createElement('div');
    toast.className = 'theme-toast';
    toast.textContent = message;
    document.body.appendChild(toast);
    
    requestAnimationFrame(() => toast.classList.add('show'));
    
    setTimeout(() => {
      toast.classList.remove('show');
      setTimeout(() => toast.remove(), 300);
    }, 2000);
  }

  function fallbackCopyToClipboard(text) {
    const textarea = document.createElement('textarea');
    textarea.value = text;
    textarea.style.position = 'fixed';
    textarea.style.opacity = '0';
    document.body.appendChild(textarea);
    textarea.select();
    document.execCommand('copy');
    document.body.removeChild(textarea);
  }

  // ==========================================================================
  // Images
  // ==========================================================================
  function initImages() {
    const images = document.querySelectorAll('img[loading="lazy"]');
    
    if ('IntersectionObserver' in window) {
      const imageObserver = new IntersectionObserver((entries) => {
        entries.forEach(entry => {
          if (entry.isIntersecting) {
            const img = entry.target;
            img.src = img.dataset.src || img.src;
            img.classList.add('loaded');
            imageObserver.unobserve(img);
          }
        }, { rootMargin: '50px' });
        
        document.querySelectorAll('img[loading="lazy"]').forEach(img => {
          imageObserver.observe(img);
        });
      });
    }
  }

  // ==========================================================================
  // Modals
  // ==========================================================================
  function initModals() {
    // Open modal triggers
    document.addEventListener('click', (e) => {
      const trigger = e.target.closest('[data-modal]');
      if (trigger) {
        const modalId = trigger.dataset.modal;
        openModal(modalId);
      }
    });

    // Close on overlay click
    document.addEventListener('click', (e) => {
      if (e.target.classList.contains('modal-overlay')) {
        closeModal(e.target.closest('.modal'));
      }
    });

    // Close on escape
    document.addEventListener('keydown', (e) => {
      if (e.key === 'Escape') {
        const openModal = document.querySelector('.modal-overlay.open');
        if (openModal) {
          const modal = openModal.querySelector('.modal');
          closeModal(modal);
        }
      }
    });

    // Close buttons
    document.addEventListener('click', (e) => {
      const closeBtn = e.target.closest('.modal-close');
      if (closeBtn) {
        closeModal(closeBtn.closest('.modal'));
      }
    });
  }

  function openModal(modalId) {
    const overlay = document.getElementById(`${modalId}-overlay`);
    const modal = document.getElementById(modalId);
    
    if (!overlay || !modal) return;
    
    overlay.classList.add('open');
    modal.style.display = 'flex';
    document.body.style.overflow = 'hidden';
    
    // Focus first focusable element
    setTimeout(() => {
      const focusable = modal.querySelector('button, input, select, textarea, a[href]');
      if (focusable) focusable.focus();
    }, 50);
  }

  function closeModal(modal) {
    if (!modal) return;
    
    const overlay = modal.closest('.modal-overlay');
    if (overlay) {
      overlay.classList.remove('open');
    }
    
    modal.style.display = 'none';
    document.body.style.overflow = '';
  }

  // ==========================================================================
  // Tooltips
  // ==========================================================================
  function initTooltips() {
    const tooltips = document.querySelectorAll('[data-tooltip]');
    
    tooltips.forEach(el => {
      const tooltip = document.createElement('div');
      tooltip.className = 'tooltip-content';
      tooltip.textContent = el.dataset.tooltip;
      tooltip.style.position = 'absolute';
      tooltip.style.zIndex = '1000';
      tooltip.style.opacity = '0';
      tooltip.style.visibility = 'hidden';
      tooltip.style.transition = 'all 0.2s ease';
      tooltip.style.whiteSpace = 'nowrap';
      tooltip.style.padding = '0.5rem 0.75rem';
      tooltip.style.background = 'var(--color-text-primary)';
      tooltip.style.color = 'var(--color-text-inverse)';
      tooltip.style.borderRadius = 'var(--radius-md)';
      tooltip.style.fontSize = 'var(--text-xs)';
      tooltip.style.fontWeight = '500';
      tooltip.style.pointerEvents = 'none';
      tooltip.style.zIndex = '9999';
      
      document.body.appendChild(tooltip);
      
      const updatePosition = () => {
        const rect = el.getBoundingClientRect();
        tooltip.style.left = `${rect.left + rect.width / 2}px`;
        tooltip.style.top = `${rect.top - 8}px`;
        tooltip.style.transform = 'translateX(-50%) translateY(-100%)';
      };
      
      const show = () => {
        tooltip.style.opacity = '1';
        tooltip.style.visibility = 'visible';
        tooltip.style.transform = 'translateX(-50%) translateY(0)';
      };
      
      const hide = () => {
        tooltip.style.opacity = '0';
        tooltip.style.visibility = 'hidden';
        tooltip.style.transform = 'translateX(-50%) translateY(-8px)';
      };
      
      el.addEventListener('mouseenter', () => {
        updatePosition();
        show();
      });
      
      el.addEventListener('mouseleave', hide);
      el.addEventListener('focus', show);
      el.addEventListener('blur', hide);
    });
  }

  // ==========================================================================
  // Dropdowns
  // ==========================================================================
  function initDropdowns() {
    document.addEventListener('click', (e) => {
      const trigger = e.target.closest('.dropdown-trigger');
      if (trigger) {
        e.preventDefault();
        const dropdown = trigger.closest('.dropdown');
        dropdown.classList.toggle('open');
      } else if (!e.target.closest('.dropdown')) {
        document.querySelectorAll('.dropdown.open').forEach(d => d.classList.remove('open'));
      }
    });
  }

  // ==========================================================================
  // Accordions
  // ==========================================================================
  function initAccordions() {
    document.addEventListener('click', (e) => {
      const header = e.target.closest('.accordion-header');
      if (!header) return;
      
      const item = header.closest('.accordion-item');
      const content = item.querySelector('.accordion-content');
      const icon = header.querySelector('.accordion-icon');
      
      const isOpen = item.classList.contains('open');
      
      // Close all other items in same accordion
      const accordion = item.closest('.accordion');
      if (accordion) {
        accordion.querySelectorAll('.accordion-item').forEach(item => {
          if (item !== item) {
            item.classList.remove('open');
            const c = item.querySelector('.accordion-content');
            const i = item.querySelector('.accordion-icon');
            if (c) c.style.maxHeight = '0';
            if (i) i.style.transform = 'rotate(0deg)';
          });
        });
      }
      
      if (isOpen) {
        item.classList.remove('open');
        if (content) content.style.maxHeight = '0';
        if (icon) icon.style.transform = 'rotate(0deg)';
      } else {
        item.classList.add('open');
        if (content) content.style.maxHeight = content.scrollHeight + 'px';
        if (icon) icon.style.transform = 'rotate(180deg)';
      }
    });
  }

  // ==========================================================================
  // Utility Functions
  // ==========================================================================

  function throttle(fn, delay) {
    let lastCall = 0;
    return function(...args) {
      const now = Date.now();
      if (now - lastCall >= delay) {
        lastCall = now;
        fn.apply(this, args);
      }
    };
  }

  function debounce(fn, delay) {
    let timeoutId;
    return function(...args) {
      clearTimeout(timeoutId);
      timeoutId = setTimeout(() => fn.apply(this, args), delay);
    };
  }

  // ==========================================================================
   // Keyboard Shortcuts
  // ==========================================================================
  document.addEventListener('keydown', (e) => {
    // Cmd/Ctrl + K for command palette
    if ((e.metaKey || e.ctrlKey) && e.key === 'k') {
      e.preventDefault();
      const palette = document.querySelector('.cmd-palette');
      if (palette) openCommandPalette();
    }
    
    // Escape to close modals/dropdowns
    if (e.key === 'Escape') {
      document.querySelectorAll('.modal-overlay.open').forEach(overlay => {
        const modal = overlay.querySelector('.modal');
        if (modal) closeModal(modal);
      });
      document.querySelectorAll('.dropdown.open').forEach(d => d.classList.remove('open'));
    }
  });

  // Export for global access
  window.TokensentryDocs = {
    openModal,
    closeModal,
    openCommandPalette,
    closeCommandPalette,
    showToast: (msg) => {
      const toast = document.createElement('div');
      toast.className = 'theme-toast';
      toast.textContent = msg;
      document.body.appendChild(toast);
      requestAnimationFrame(() => toast.classList.add('show'));
      setTimeout(() => {
        toast.classList.remove('show');
        setTimeout(() => toast.remove(), 300);
      }, 2000);
    }
  };
})();

// Initialize Lucide icons when available
if (typeof lucide !== 'undefined') {
  lucide.createIcons();
}

// Re-initialize icons when DOM changes
const iconObserver = new MutationObserver(() => {
  if (typeof lucide !== 'undefined') {
    lucide.createIcons();
  }
});

iconObserver.observe(document.body, {
  childList: true,
  subtree: true
});

// Handle Lucide icons for dynamically added content
document.addEventListener('tokensentry:ready', () => {
  if (typeof lucide !== 'undefined') {
    lucide.createIcons();
  }
});

// Re-initialize icons after theme change
document.addEventListener('themechange', () => {
  if (typeof lucide !== 'undefined') {
    lucide.createIcons();
  }
});