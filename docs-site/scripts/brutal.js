/* ==========================================================================
   TOKENSENTRY DOCS — NEO-BRUTALIST JAVASCRIPT
   Raw. Sharp. Morphing. Unapologetic.
   ========================================================================== */

(function() {
  'use strict';

  // ── INITIALIZE LUCIDE ICONS ──
  if (typeof lucide !== 'undefined') {
    lucide.createIcons();
  }

  // ── DATA ──
  const features = [
    {
      icon: `<svg xmlns="http://www.w3.org/2000/svg" width="32" height="32" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.5" stroke-linecap="round" stroke-linejoin="round"><circle cx="11" cy="11" r="8"></circle><line x1="21" y1="21" x2="16.65" y2="16.65"></line></svg>`,
      title: 'DEEP ANALYSIS',
      desc: '7 MODULAR ANALYZERS DETECT STRUCTURE, REDUNDANCY, AMBIGUITY, CONTRADICTIONS, COMPLEXITY, QUALITY ISSUES, AND SECURITY RISKS.',
      items: ['STRUCTURE PARSING (HEADINGS, CODE FENCES, LISTS)', 'REDUNDANCY DETECTION (LINES, PHRASES, REQUIREMENTS)', 'AMBIGUITY & CONTRADICTION DETECTION', 'COMPLEXITY METRICS & QUALITY SCORING', 'SECURITY AUDIT (INJECTION, SECRETS, UNSAFE)'],
      variant: 'default'
    },
    {
      icon: `<svg xmlns="http://www.w3.org/2000/svg" width="32" height="32" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.5" stroke-linecap="round" stroke-linejoin="round"><polyline points="23 4 23 10 17 10"></polyline><path d="M20.49 15a9 9 0 1 1-2.12-9.36L23 10"></path></svg>`,
      title: 'SMART OPTIMIZATION',
      desc: 'THREE PROFILES — CONSERVATIVE, BALANCED, AGGRESSIVE — WITH FULL TRANSFORMATION TRACKING AND TECHNICAL LITERAL PRESERVATION.',
      items: ['CONSERVATIVE: WHITESPACE, DUPLICATES ONLY', 'BALANCED: PHRASE CONSOLIDATION, TRANSITIONS', 'AGGRESSIVE: FILLER REMOVAL, COMPRESSION', 'TECHNICAL LITERAL PRESERVATION', 'TRANSFORMATION DELTA TRACKING'],
      variant: 'cyan'
    },
    {
      icon: `<svg xmlns="http://www.w3.org/2000/svg" width="32" height="32" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.5" stroke-linecap="round" stroke-linejoin="round"><path d="M22 11.08V12a10 10 0 1 1-5.93-9.14"></path><polyline points="22 4 12 14.01 9 11.01"></polyline></svg>`,
      title: 'SEMANTIC VALIDATION',
      desc: '7-STATUS CLASSIFICATION (EXACT/STRUCTURAL/PROBABLE/UNCERTAIN/MODIFIED/MISSING/WEAKENED) WITH BYTE-FOR-BYTE LITERAL PRESERVATION.',
      items: ['REQUIREMENT PRESERVATION CHECKING', 'NEGATIVE CONSTRAINT WEAKENING DETECTION', 'TECHNICAL LITERAL BYTE-FOR-BYTE VERIFICATION', 'OUTPUT SCHEMA PRESERVATION', 'DETAILED DIFF WITH CONFIDENCE SCORES'],
      variant: 'magenta'
    },
    {
      icon: `<svg xmlns="http://www.w3.org/2000/svg" width="32" height="32" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.5" stroke-linecap="round" stroke-linejoin="round"><rect x="2" y="3" width="20" height="14" rx="0"></rect><path d="M8 21h13a2 2 0 0 0 2-2V5"></path></svg>`,
      title: 'TOKENIZER SUPPORT',
      desc: 'EXACT TOKEN COUNTING WITH TIKTOKEN (OPENAI), HUGGINGFACE TOKENIZERS, SENTENCEPIECE — NO SILENT FALLBACKS, EXPLICIT EXACTNESS METADATA.',
      items: ['TIKTOKEN: GPT-4, GPT-3.5, GPT-4O, ETC.', 'HUGGINGFACE: LLAMA, MISTRAL, GEMMA, ETC.', 'SENTENCEPIECE: CUSTOM MODELS', 'EXACT VS ESTIMATE CLASSIFICATION', 'MODEL-AWARE CONTEXT WINDOW WARNINGS'],
      variant: 'lime'
    },
    {
      icon: `<svg xmlns="http://www.w3.org/2000/svg" width="32" height="32" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.5" stroke-linecap="round" stroke-linejoin="round"><path d="M12 22s8-4 8-10V5l-8-3-8 3v7c0 6 8 10 8 10z"></path></svg>`,
      title: '15 AI AGENT SKILLS',
      desc: 'COMPOSABLE, REUSABLE SKILLS FOR ANALYZER, OPTIMIZER, VALIDATOR, SECURITY AUDITOR, COST ANALYST, AND MORE.',
      items: ['ANALYZER, OPTIMIZER, VALIDATOR, TOKEN AUDITOR', 'SECURITY AUDITOR, CONTEXT ENGINEER', 'COST ANALYST, MODEL ADAPTER', 'SKILL COMPOSER FOR ORCHESTRATION', 'STRUCTURED OUTPUT, FEW-SHOT, AGENT WORKFLOW'],
      variant: 'default'
    },
    {
      icon: `<svg xmlns="http://www.w3.org/2000/svg" width="32" height="32" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.5" stroke-linecap="round" stroke-linejoin="round"><path d="M14 2H6a2 2 0 0 0-2 2v16a2 2 0 0 0 2 2h12a2 2 0 0 0 2-2V8z"></path><polyline points="14 2 14 8 20 8"></polyline></svg>`,
      title: 'RICH REPORTING',
      desc: 'EXPORT RESULTS AS JSON, MARKDOWN, OR BEAUTIFUL TERMINAL OUTPUT WITH SYNTAX HIGHLIGHTING AND INTERACTIVE TABLES.',
      items: ['JSON EXPORT WITH SCHEMA VERSIONING', 'MARKDOWN REPORTS FOR DOCUMENTATION', 'RICH TERMINAL UI WITH TABLES', 'BENCHMARK COMPARISON REPORTS', 'SCHEMA VERSIONING FOR COMPATIBILITY'],
      variant: 'default'
    }
  ];

  const docsSections = [
    { href: 'getting-started.html', icon: `<svg xmlns="http://www.w3.org/2000/svg" width="28" height="28" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.5" stroke-linecap="round" stroke-linejoin="round"><path d="M13 2L3 14h9l-1 8 10-12h-9l1-8z"></path></svg>`, title: 'GETTING STARTED', desc: 'INSTALLATION, QUICK START GUIDE, AND FIRST STEPS WITH TOKENSENTRY.', featured: false },
    { href: 'cli-reference.html', icon: `<svg xmlns="http://www.w3.org/2000/svg" width="28" height="28" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.5" stroke-linecap="round" stroke-linejoin="round"><polyline points="4 17 10 11 4 5"></polyline><line x1="9" y1="19" x2="20" y2="19"></line></svg>`, title: 'CLI REFERENCE', desc: 'COMPLETE COMMAND REFERENCE FOR ANALYZE, OPTIMIZE, VALIDATE, AND MORE.', featured: false },
    { href: 'analyzer.html', icon: `<svg xmlns="http://www.w3.org/2000/svg" width="28" height="28" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.5" stroke-linecap="round" stroke-linejoin="round"><circle cx="11" cy="11" r="8"></circle><line x1="21" y1="21" x2="16.65" y2="16.65"></line></svg>`, title: 'ANALYZER ENGINE', desc: 'DEEP DIVE INTO THE 7 ANALYSIS MODULES: STRUCTURE, REDUNDANCY, AMBIGUITY, CONTRADICTIONS, COMPLEXITY, QUALITY, SECURITY.', featured: false },
    { href: 'optimizer.html', icon: `<svg xmlns="http://www.w3.org/2000/svg" width="28" height="28" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.5" stroke-linecap="round" stroke-linejoin="round"><polyline points="23 4 23 10 17 10"></polyline><path d="M20.49 15a9 9 0 1 1-2.12-9.36L23 10"></path></svg>`, title: 'OPTIMIZER PROFILES', desc: 'CONSERVATIVE, BALANCED, AGGRESSIVE — TRANSFORMATION TRACKING WITH LITERAL PRESERVATION.', featured: false },
    { href: 'validator.html', icon: `<svg xmlns="http://www.w3.org/2000/svg" width="28" height="28" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.5" stroke-linecap="round" stroke-linejoin="round"><path d="M22 11.08V12a10 10 0 1 1-5.93-9.14"></path><polyline points="22 4 12 14.01 9 11.01"></polyline></svg>`, title: 'VALIDATOR ENGINE', desc: '7-STATUS CLASSIFICATION, LITERAL PRESERVATION, NEGATIVE CONSTRAINT CHECKING, SCHEMA VALIDATION.', featured: false },
    { href: 'tokenizers.html', icon: `<svg xmlns="http://www.w3.org/2000/svg" width="28" height="28" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.5" stroke-linecap="round" stroke-linejoin="round"><rect x="2" y="3" width="20" height="14" rx="0"></rect><path d="M8 21h13a2 2 0 0 0 2-2V5"></path></svg>`, title: 'TOKENIZER ADAPTERS', desc: 'TIKTOKEN (OPENAI), HUGGINGFACE TOKENIZERS, SENTENCEPIECE WITH EXACT/ESTIMATE METADATA.', featured: false },
    { href: 'skills/overview.html', icon: `<svg xmlns="http://www.w3.org/2000/svg" width="28" height="28" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.5" stroke-linecap="round" stroke-linejoin="round"><path d="M12 22s8-4 8-10V5l-8-3-8 3v7c0 6 8 10 8 10z"></path></svg>`, title: '15 AI AGENT SKILLS', desc: 'COMPOSABLE SKILLS FOR ANALYSIS, OPTIMIZATION, VALIDATION, SECURITY, COST ANALYSIS, AND WORKFLOW ORCHESTRATION.', featured: true },
    { href: 'benchmarks.html', icon: `<svg xmlns="http://www.w3.org/2000/svg" width="28" height="28" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.5" stroke-linecap="round" stroke-linejoin="round"><line x1="18" y1="20" x2="18" y2="10"></line><line x1="12" y1="20" x2="12" y2="4"></line><line x1="6" y1="20" x2="6" y2="14"></line></svg>`, title: 'BENCHMARKS', desc: '13 CURATED PROMPTS ACROSS 7 CATEGORIES WITH TOKEN REDUCTION, PRESERVATION, AND QUALITY METRICS.', featured: false },
    { href: 'reports.html', icon: `<svg xmlns="http://www.w3.org/2000/svg" width="28" height="28" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.5" stroke-linecap="round" stroke-linejoin="round"><path d="M14 2H6a2 2 0 0 0-2 2v16a2 2 0 0 0 2 2h12a2 2 0 0 0 2-2V8z"></path><polyline points="14 2 14 8 20 8"></polyline><line x1="16" y1="13" x2="8" y2="13"></line><line x1="16" y1="17" x2="8" y2="17"></line><polyline points="10 9 9 9 8 9"></polyline></svg>`, title: 'REPORT EXPORTERS', desc: 'JSON, MARKDOWN, AND RICH TERMINAL OUTPUT WITH SCHEMA VERSIONING AND COMBINED REPORTS.', featured: false }
  ];

  const archLayers = [
    { title: 'CLI LAYER', components: ['ANALYZE', 'OPTIMIZE', 'VALIDATE', 'TOKENIZERS', 'SKILL', 'WORKFLOW', 'BENCHMARK'], variant: 'default' },
    { title: 'CORE ENGINES', components: ['ANALYZER', 'OPTIMIZER', 'VALIDATOR'], variant: 'core' },
    { title: 'ANALYSIS MODULES', components: ['STRUCTURE', 'REDUNDANCY', 'AMBIGUITY', 'CONTRADICTIONS', 'COMPLEXITY', 'QUALITY', 'SECURITY'], variant: 'mod' },
    { title: 'OPTIMIZATION PIPELINE', components: ['CONSERVATIVE', 'BALANCED', 'AGGRESSIVE'], variant: 'opt' },
    { title: 'TOKENIZER REGISTRY', components: ['TIKTOKEN', 'HUGGINGFACE', 'SENTENCEPIECE', 'CHARACTER ESTIMATE'], variant: 'tok' },
    { title: 'SKILL ECOSYSTEM', components: ['ANALYZER', 'OPTIMIZER', 'VALIDATOR', 'TOKEN AUDITOR', 'CONTEXT ENGINEER', 'SECURITY AUDITOR', 'COST ANALYST', 'MODEL ADAPTER', 'SKILL COMPOSER', '+ 5 MORE'], variant: 'skill' }
  ];

  // ── DOM ELEMENTS ──
  const featuresGrid = document.getElementById('featuresGrid');
  const docsGrid = document.getElementById('docsGrid');
  const architectureDiagram = document.getElementById('architectureDiagram');
  const floatingElements = document.getElementById('floatingElements');
  const gridPattern = document.getElementById('gridPattern');
  const scanline = document.getElementById('scanline');

  // ── RENDER FUNCTIONS ──
  function renderFeatures() {
    if (!featuresGrid) return;
    featuresGrid.innerHTML = features.map((feature, i) => `
      <article class="feature-card card ${feature.variant !== 'default' ? 'card-' + feature.variant : ''}" style="animation-delay: ${i * 100}ms">
        <div class="feature-icon">${feature.icon}</div>
        <h3>${feature.title}</h3>
        <p>${feature.desc}</p>
        <ul class="feature-list">
          ${feature.items.map(item => `<li>${item}</li>`).join('')}
        </ul>
      </article>
    `).join('');
  }

  function renderDocs() {
    if (!docsGrid) return;
    docsGrid.innerHTML = docsSections.map(section => `
      <a href="${section.href}" class="doc-card card ${section.featured ? 'featured card-cyan' : ''}">
        <div class="doc-icon">${section.icon}</div>
        <h3>${section.title}</h3>
        <p>${section.desc}</p>
        <span class="doc-link">READ MORE <i data-lucide="arrow-right"></i></span>
      </a>
    `).join('');
    if (typeof lucide !== 'undefined') lucide.createIcons();
  }

  function renderArchitecture() {
    if (!architectureDiagram) return;
    architectureDiagram.innerHTML = archLayers.map((layer, i) => `
      <div class="arch-layer card ${layer.variant !== 'default' ? 'card-' + layer.variant : ''}" style="animation-delay: ${i * 100}ms">
        <h3>${layer.title}</h3>
        <div class="arch-components">
          ${layer.components.map(comp => `<span class="arch-comp ${layer.variant}">${comp}</span>`).join('')}
        </div>
      </div>
    `).join('');
  }

  function createFloatingElements() {
    if (!floatingElements) return;
    const shapes = ['▲', '■', '◆', '●', '▼', '◆', '▲', '■'];
    floatingElements.innerHTML = shapes.map((shape, i) => `
      <div class="float-shape" style="
        --delay: ${i * 0.5}s;
        --duration: ${8 + Math.random() * 4}s;
        --x: ${Math.random() * 100}%;
        --y: ${Math.random() * 100}%;
        --size: ${12 + Math.random() * 24}px;
        --color: ${['var(--accent-cyan)', 'var(--accent-magenta)', 'var(--accent-lime)', 'var(--accent-gold)'][Math.floor(Math.random() * 4)]};
      ">${shape}</div>
    `).join('');
  }

  function createGridPattern() {
    if (!gridPattern) return;
    const size = 40;
    const cols = Math.ceil(window.innerWidth / size) + 1;
    const rows = Math.ceil(window.innerHeight / size) + 1;
    let pattern = '';
    for (let y = 0; y < rows; y++) {
      for (let x = 0; x < cols; x++) {
        pattern += `<div class="grid-dot" style="left: ${x * size}px; top: ${y * size}px;"></div>`;
      }
    }
    gridPattern.innerHTML = pattern;
  }

  function createScanline() {
    if (!scanline) return;
    scanline.innerHTML = '<div class="scanline-bar"></div>';
  }

  // ── COUNTER ANIMATION ──
  function animateCounters() {
    const counters = document.querySelectorAll('.stat-value[data-count]');
    const observer = new IntersectionObserver((entries) => {
      entries.forEach(entry => {
        if (entry.isIntersecting) {
          const el = entry.target;
          const target = parseInt(el.dataset.count, 10);
          const duration = 1500;
          const start = performance.now();
          
          function update(time) {
            const progress = Math.min((time - start) / duration, 1);
            const eased = 1 - Math.pow(1 - progress, 3);
            el.textContent = Math.floor(eased * target);
            if (progress < 1) requestAnimationFrame(update);
            else el.textContent = target;
          }
          requestAnimationFrame(update);
          observer.unobserve(el);
        }
      });
    }, { threshold: 0.5 });
    
    counters.forEach(el => observer.observe(el));
  }

  // ── HERO TITLE MORPHING ──
  function initTitleMorph() {
    const titles = document.querySelectorAll('.hero-title .title-line');
    titles.forEach((title, i) => {
      const text = title.dataset.text;
      title.innerHTML = text.split('').map((char, j) => 
        `<span style="animation-delay: ${j * 30 + i * 200}ms">${char === ' ' ? '&nbsp;' : char}</span>`
      ).join('');
    });
  }

  // ── TAB SWITCHING ──
  function initTabs() {
    const tabBtns = document.querySelectorAll('.tab-btn');
    const tabPanels = document.querySelectorAll('.tab-panel');
    
    tabBtns.forEach(btn => {
      btn.addEventListener('click', () => {
        const tab = btn.dataset.tab;
        
        tabBtns.forEach(b => {
          b.classList.remove('active');
          b.setAttribute('aria-selected', 'false');
        });
        btn.classList.add('active');
        btn.setAttribute('aria-selected', 'true');
        
        tabPanels.forEach(panel => {
          panel.hidden = true;
          panel.classList.remove('active');
        });
        
        const activePanel = document.getElementById(`tab-${tab}`);
        if (activePanel) {
          activePanel.hidden = false;
          requestAnimationFrame(() => activePanel.classList.add('active'));
        }
      });
    });
  }

  // ── NAVIGATION ──
  function initNavigation() {
    const navToggle = document.getElementById('navToggle');
    const navMenu = document.getElementById('navMenu');
    const navOverlay = document.getElementById('navOverlay');
    const navLinks = document.querySelectorAll('.nav-link');
    
    function closeNav() {
      navMenu.classList.remove('open');
      navOverlay.classList.remove('open');
      navToggle.setAttribute('aria-expanded', 'false');
      document.body.style.overflow = '';
    }
    
    function openNav() {
      navMenu.classList.add('open');
      navOverlay.classList.add('open');
      navToggle.setAttribute('aria-expanded', 'true');
      document.body.style.overflow = 'hidden';
    }
    
    navToggle?.addEventListener('click', () => {
      if (navMenu.classList.contains('open')) closeNav();
      else openNav();
    });
    
    navOverlay?.addEventListener('click', closeNav);
    navLinks.forEach(link => link.addEventListener('click', closeNav));
    
    // Close on escape
    document.addEventListener('keydown', e => {
      if (e.key === 'Escape') closeNav();
    });
  }

  // ── THEME TOGGLE ──
  function initTheme() {
    const toggle = document.getElementById('themeToggle');
    const html = document.documentElement;
    
    // Load saved theme
    const saved = localStorage.getItem('tokensentry-theme');
    if (saved) html.setAttribute('data-theme', saved);
    else if (window.matchMedia('(prefers-color-scheme: dark)').matches) {
      html.setAttribute('data-theme', 'dark');
    }
    
    toggle?.addEventListener('click', () => {
      const current = html.getAttribute('data-theme');
      const next = current === 'dark' ? 'light' : 'dark';
      html.setAttribute('data-theme', next);
      localStorage.setItem('tokensentry-theme', next);
      
      // Add rotation animation
      toggle.style.transform = 'rotate(180deg) scale(1.1)';
      setTimeout(() => toggle.style.transform = '', 300);
    });
    
    // Keyboard shortcut
    document.addEventListener('keydown', e => {
      if (e.ctrlKey && e.shiftKey && e.key === 'T') {
        e.preventDefault();
        toggle?.click();
      }
    });
  }

  // ── PROGRESS BAR ──
  function initProgressBar() {
    const bar = document.getElementById('progressBar');
    let ticking = false;
    
    function update() {
      const scrollTop = window.scrollY;
      const docHeight = document.documentElement.scrollHeight - window.innerHeight;
      const progress = docHeight > 0 ? scrollTop / docHeight : 0;
      bar.style.transform = `scaleX(${progress})`;
      ticking = false;
    }
    
    window.addEventListener('scroll', () => {
      if (!ticking) {
        requestAnimationFrame(update);
        ticking = true;
      }
    }, { passive: true });
  }

  // ── BACK TO TOP ──
  function initBackToTop() {
    const btn = document.getElementById('backToTop');
    if (!btn) return;
    
    window.addEventListener('scroll', () => {
      if (window.scrollY > 300) btn.classList.add('visible');
      else btn.classList.remove('visible');
    }, { passive: true });
    
    btn.addEventListener('click', () => {
      window.scrollTo({ top: 0, behavior: 'smooth' });
    });
  }

  // ── SCROLL REVEAL ──
  function initScrollReveal() {
    const observer = new IntersectionObserver((entries) => {
      entries.forEach(entry => {
        if (entry.isIntersecting) {
          entry.target.classList.add('revealed');
          observer.unobserve(entry.target);
        }
      });
    }, { threshold: 0.1, rootMargin: '0px 0px -50px 0px' });
    
    document.querySelectorAll('.section, .feature-card, .quickstart-step, .doc-card, .arch-layer, .contribute-card').forEach(el => {
      el.style.opacity = '0';
      el.style.transform = 'translateY(30px)';
      el.style.transition = 'opacity 0.6s var(--ease-expo), transform 0.6s var(--ease-expo)';
      observer.observe(el);
    });
    
    // Add revealed class styles
    const style = document.createElement('style');
    style.textContent = `
      .revealed { opacity: 1 !important; transform: translateY(0) !important; }
      @media (prefers-reduced-motion: reduce) {
        .section, .feature-card, .quickstart-step, .doc-card, .arch-layer, .contribute-card {
          opacity: 1 !important; transform: none !important; transition: none !important;
        }
      }
    `;
    document.head.appendChild(style);
  }

  // ── PARALLAX HERO ──
  function initParallax() {
    const hero = document.querySelector('.hero');
    const heroBg = document.querySelector('.hero-background');
    if (!hero || !heroBg) return;
    
    let ticking = false;
    window.addEventListener('scroll', () => {
      if (!ticking) {
        requestAnimationFrame(() => {
          const scrolled = window.scrollY;
          const rate = scrolled * -0.3;
          heroBg.style.transform = `translateY(${rate}px)`;
          
          const shapes = document.querySelectorAll('.float-shape');
          shapes.forEach((shape, i) => {
            const speed = 0.1 + (i % 3) * 0.05;
            shape.style.transform = `translateY(${scrolled * speed}px) rotate(${scrolled * 0.02}deg)`;
          });
          ticking = false;
        });
        ticking = true;
      }
    }, { passive: true });
  }

  // ── MORPHING GRID ──
  function initMorphingGrid() {
    const dots = document.querySelectorAll('.grid-dot');
    if (dots.length === 0) return;
    
    let time = 0;
    function animate() {
      time += 0.005;
      dots.forEach((dot, i) => {
        const delay = (i * 0.01) % 1;
        const scale = 0.5 + 0.5 * Math.sin(time * 2 + delay * Math.PI * 2);
        const opacity = 0.1 + 0.3 * Math.sin(time + delay * Math.PI * 2);
        dot.style.transform = `scale(${scale})`;
        dot.style.opacity = opacity;
      });
      requestAnimationFrame(animate);
    }
    // Only animate if not reduced motion
    if (!window.matchMedia('(prefers-reduced-motion: reduce)').matches) {
      animate();
    }
  }

  // ── KEYBOARD NAVIGATION ──
  function initKeyboardNav() {
    document.addEventListener('keydown', e => {
      // Navigate tabs with arrow keys
      if (e.target.classList.contains('tab-btn')) {
        const tabs = Array.from(document.querySelectorAll('.tab-btn'));
        const index = tabs.indexOf(e.target);
        let nextIndex = index;
        
        if (e.key === 'ArrowRight') nextIndex = (index + 1) % tabs.length;
        else if (e.key === 'ArrowLeft') nextIndex = (index - 1 + tabs.length) % tabs.length;
        else if (e.key === 'Home') nextIndex = 0;
        else if (e.key === 'End') nextIndex = tabs.length - 1;
        else return;
        
        e.preventDefault();
        tabs[nextIndex].focus();
        tabs[nextIndex].click();
      }
    });
  }

  // ── REDUCED MOTION ──
  function checkReducedMotion() {
    const mediaQuery = window.matchMedia('(prefers-reduced-motion: reduce)');
    if (mediaQuery.matches) {
      document.documentElement.style.setProperty('--dur-base', '0ms');
      document.documentElement.style.setProperty('--dur-smooth', '0ms');
      document.documentElement.style.setProperty('--dur-slow', '0ms');
    }
    mediaQuery.addEventListener('change', checkReducedMotion);
  }

  // ── INITIALIZE EVERYTHING ──
  function init() {
    renderFeatures();
    renderDocs();
    renderArchitecture();
    createFloatingElements();
    createGridPattern();
    createScanline();
    
    // Initialize Lucide icons after rendering
    if (typeof lucide !== 'undefined') {
      lucide.createIcons();
    }
    
    initTitleMorph();
    animateCounters();
    initTabs();
    initNavigation();
    initTheme();
    initProgressBar();
    initBackToTop();
    initScrollReveal();
    initParallax();
    initMorphingGrid();
    initKeyboardNav();
    checkReducedMotion();
    
    // Add loaded class for entrance animations
    document.body.classList.add('loaded');
  }

  // Run on DOM ready
  if (document.readyState === 'loading') {
    document.addEventListener('DOMContentLoaded', init);
  } else {
    init();
  }

  // Export for potential external use
  window.TokenSentryDocs = {
    features,
    docsSections,
    archLayers,
    init
  };

})();