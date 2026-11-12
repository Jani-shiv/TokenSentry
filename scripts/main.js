(function() {
  'use strict';

  // Theme Management
  function initTheme() {
    const toggle = document.getElementById('themeToggle');
    const html = document.documentElement;
    
    const saved = localStorage.getItem('tokensentry-theme');
    if (saved) {
      html.setAttribute('data-theme', saved);
      updateThemeIcon(saved);
    } else if (window.matchMedia('(prefers-color-scheme: dark)').matches) {
      html.setAttribute('data-theme', 'dark');
      updateThemeIcon('dark');
    }

    toggle?.addEventListener('click', () => {
      const current = html.getAttribute('data-theme');
      const next = current === 'dark' ? 'light' : 'dark';
      html.setAttribute('data-theme', next);
      localStorage.setItem('tokensentry-theme', next);
      updateThemeIcon(next);
    });

    window.matchMedia('(prefers-color-scheme: dark)').addEventListener('change', (e) => {
      if (!localStorage.getItem('tokensentry-theme')) {
        const theme = e.matches ? 'dark' : 'light';
        html.setAttribute('data-theme', theme);
        updateThemeIcon(theme);
      }
    });
  }

  function updateThemeIcon(theme) {
    const toggle = document.getElementById('themeToggle');
    if (toggle) {
      toggle.textContent = theme === 'dark' ? '☀️' : '🌙';
    }
  }

  // Mobile Menu
  function initMobileMenu() {
    const toggle = document.getElementById('mobileMenuToggle');
    const links = document.getElementById('navLinks');
    
    toggle?.addEventListener('click', () => {
      links.classList.toggle('active');
      toggle.setAttribute('aria-expanded', links.classList.contains('active'));
    });

    // Close on link click
    links?.querySelectorAll('.nav-link').forEach(link => {
      link.addEventListener('click', () => {
        links.classList.remove('active');
        toggle?.setAttribute('aria-expanded', 'false');
      });
    });

    // Close on escape
    document.addEventListener('keydown', (e) => {
      if (e.key === 'Escape' && links?.classList.contains('active')) {
        links.classList.remove('active');
        toggle?.setAttribute('aria-expanded', 'false');
      }
    });
  }

  // Search
  function initSearch() {
    const input = document.getElementById('searchInput');
    if (!input) return;

    const pages = [
      { title: 'Getting Started', url: 'docs-site/getting-started.html', keywords: 'install quickstart first steps' },
      { title: 'CLI Reference', url: 'docs-site/cli-reference.html', keywords: 'analyze optimize validate skill workflow benchmark' },
      { title: 'Analyzer Engine', url: 'docs-site/analyzer.html', keywords: 'structure redundancy ambiguity contradiction complexity quality security' },
      { title: 'Optimizer Profiles', url: 'docs-site/optimizer.html', keywords: 'conservative balanced aggressive literal preservation' },
      { title: 'Validator Engine', url: 'docs-site/validator.html', keywords: 'exact structural probable uncertain modified missing weakened' },
      { title: 'Tokenizers', url: 'docs-site/tokenizers.html', keywords: 'tiktoken huggingface sentencepiece character estimate' },
      { title: 'Benchmarks', url: 'docs-site/benchmarks.html', keywords: 'results token reduction preservation quality' },
      { title: 'AI Skills Overview', url: 'docs-site/skills/overview.html', keywords: 'analyzer optimizer validator token auditor context security cost model composer' },
      { title: 'Configuration', url: 'docs-site/configuration.html', keywords: 'env vars yaml config project settings' },
      { title: 'Contributing', url: 'docs-site/contributing.html', keywords: 'contribute guidelines code docs skills' },
      { title: 'Features', url: 'features.html', keywords: 'features overview engines tokenizers skills reporting' },
    ];

    let resultsContainer = null;

    function showResults(query) {
      if (!resultsContainer) {
        resultsContainer = document.createElement('div');
        resultsContainer.className = 'search-results';
        resultsContainer.style.cssText = `
          position: absolute;
          top: 100%;
          left: 0;
          right: 0;
          background: var(--bg-secondary);
          border: 2px solid var(--paper-border);
          border-radius: var(--radius-md);
          box-shadow: var(--shadow-paper);
          margin-top: .5rem;
          max-height: 400px;
          overflow-y: auto;
          z-index: 1000;
        `;
        input.parentNode.style.position = 'relative';
        input.parentNode.appendChild(resultsContainer);
      }

      const results = pages.filter(page => 
        page.title.toLowerCase().includes(query) || 
        page.keywords.toLowerCase().includes(query)
      ).slice(0, 8);

      if (results.length === 0) {
        resultsContainer.innerHTML = '<div style="padding: 1.5rem; text-align: center; color: var(--text-muted);">No results found</div>';
      } else {
        resultsContainer.innerHTML = results.map(page => `
          <a href="${page.url}" style="
            display: block;
            padding: .85rem 1.15rem;
            color: var(--text-primary);
            text-decoration: none;
            border-bottom: 1px solid var(--paper-border-soft);
            transition: background var(--transition-fast);
          " onmouseover="this.style.background='var(--bg-tertiary)'" onmouseout="this.style.background='transparent'">
            <strong>${page.title}</strong>
          </a>
        `).join('');
      }
      resultsContainer.style.display = 'block';
    }

    function hideResults() {
      if (resultsContainer) {
        resultsContainer.style.display = 'none';
      }
    }

    input.addEventListener('input', (e) => {
      const query = e.target.value.toLowerCase().trim();
      if (query.length >= 2) {
        showResults(query);
      } else {
        hideResults();
      }
    });

    input.addEventListener('focus', () => {
      if (input.value.trim().length >= 2) {
        showResults(input.value.toLowerCase().trim());
      }
    });

    document.addEventListener('click', (e) => {
      if (!e.target.closest('.nav-search')) {
        hideResults();
      }
    });

    input.addEventListener('keydown', (e) => {
      if (e.key === 'Escape') {
        hideResults();
        input.blur();
      }
    });
  }

  // Smooth scroll for anchor links
  function initSmoothScroll() {
    document.querySelectorAll('a[href^="#"]').forEach(anchor => {
      anchor.addEventListener('click', function(e) {
        const targetId = this.getAttribute('href');
        if (targetId === '#') return;
        
        const target = document.querySelector(targetId);
        if (!target) return;
        
        e.preventDefault();
        
        const navHeight = document.querySelector('.navbar')?.offsetHeight || 0;
        const targetPosition = target.getBoundingClientRect().top + window.scrollY - navHeight - 20;
        
        window.scrollTo({
          top: targetPosition,
          behavior: 'smooth'
        });
        
        history.pushState(null, '', targetId);
      });
    });
  }

  // Scroll animations
  function initScrollAnimations() {
    const observer = new IntersectionObserver((entries) => {
      entries.forEach(entry => {
        if (entry.isIntersecting) {
          entry.target.classList.add('fade-in');
          observer.unobserve(entry.target);
        }
      });
    }, { threshold: 0.1, rootMargin: '0px 0px -50px 0px' });

    document.querySelectorAll('.about-card, .chapter-card, .feature-item, .hero-content > *').forEach(el => {
      observer.observe(el);
    });
  }

  // Copy code blocks
  function initCodeCopy() {
    document.querySelectorAll('pre code').forEach(codeBlock => {
      const pre = codeBlock.parentElement;
      if (pre.querySelector('.copy-btn')) return;

      const btn = document.createElement('button');
      btn.className = 'copy-btn';
      btn.textContent = 'Copy';
      btn.style.cssText = `
        position: absolute;
        top: .75rem;
        right: .75rem;
        padding: .35rem .75rem;
        background: var(--bg-primary);
        border: 2px solid var(--paper-border);
        border-radius: var(--radius-sm);
        font-family: inherit;
        font-size: .75rem;
        font-weight: 700;
        color: var(--text-primary);
        cursor: pointer;
        opacity: 0;
        transition: opacity var(--transition-fast);
        box-shadow: 1px 1px 0 var(--paper-border);
      `;

      pre.style.position = 'relative';
      pre.appendChild(btn);

      pre.addEventListener('mouseenter', () => btn.style.opacity = '1');
      pre.addEventListener('mouseleave', () => btn.style.opacity = '0');

      btn.addEventListener('click', async () => {
        const code = codeBlock.textContent;
        try {
          await navigator.clipboard.writeText(code);
          btn.textContent = 'Copied!';
          setTimeout(() => btn.textContent = 'Copy', 1500);
        } catch (err) {
          const textarea = document.createElement('textarea');
          textarea.value = code;
          document.body.appendChild(textarea);
          textarea.select();
          document.execCommand('copy');
          document.body.removeChild(textarea);
          btn.textContent = 'Copied!';
          setTimeout(() => btn.textContent = 'Copy', 1500);
        }
      });
    });
  }

  // Initialize everything
  function init() {
    initTheme();
    initMobileMenu();
    initSearch();
    initSmoothScroll();
    initScrollAnimations();
    initCodeCopy();
    
    // Add loaded class
    document.body.classList.add('loaded');
  }

  if (document.readyState === 'loading') {
    document.addEventListener('DOMContentLoaded', init);
  } else {
    init();
  }
})();