/* ==========================================================================
   TOKENSENTRY — ENHANCED NEO-BRUTALIST JAVASCRIPT
   Raw. Sharp. Morphing. Paper-Animated. Unapologetic.
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

  const skills = [
    { name: 'ANALYZER', icon: 'search', desc: 'DEEP PROMPT ANALYSIS WITH 7 MODULES', href: 'docs-site/skills/analyzer.html', color: 'cyan' },
    { name: 'OPTIMIZER', icon: 'zap', desc: 'SMART TOKEN REDUCTION WITH 3 PROFILES', href: 'docs-site/skills/optimizer.html', color: 'magenta' },
    { name: 'VALIDATOR', icon: 'shield-check', desc: 'SEMANTIC PRESERVATION VERIFICATION', href: 'docs-site/skills/validator.html', color: 'lime' },
    { name: 'TOKEN AUDITOR', icon: 'cpu', desc: 'DETAILED TOKEN USAGE BREAKDOWN', href: 'docs-site/skills/token-auditor.html', color: 'gold' },
    { name: 'CONTEXT ENGINEER', icon: 'layers', desc: 'OPTIMIZE CONTEXT WINDOW USAGE', href: 'docs-site/skills/context-engineer.html', color: 'cyan' },
    { name: 'SECURITY AUDITOR', icon: 'shield-alert', desc: 'DETECT INJECTION & SECRET LEAKS', href: 'docs-site/skills/security-auditor.html', color: 'red' },
    { name: 'COST ANALYST', icon: 'dollar-sign', desc: 'ESTIMATE API COSTS PER PROMPT', href: 'docs-site/skills/cost-analyst.html', color: 'green' },
    { name: 'MODEL ADAPTER', icon: 'cpu', desc: 'ADAPT PROMPTS FOR DIFFERENT MODELS', href: 'docs-site/skills/model-adapter.html', color: 'magenta' },
    { name: 'SKILL COMPOSER', icon: 'git-merge', desc: 'ORCHESTRATE MULTI-SKILL WORKFLOWS', href: 'docs-site/skills/composer.html', color: 'cyan' },
    { name: 'STRUCTURED OUTPUT', icon: 'braces', desc: 'ENFORCE JSON/SCHEMA OUTPUTS', href: 'docs-site/skills/structured-output.html', color: 'lime' },
    { name: 'FEW-SHOT OPTIMIZER', icon: 'copy', desc: 'OPTIMIZE FEW-SHOT EXAMPLES', href: 'docs-site/skills/few-shot.html', color: 'gold' },
    { name: 'AGENT WORKFLOW', icon: 'git-branch', desc: 'BUILD MULTI-AGENT PIPELINES', href: 'docs-site/skills/agent-workflow.html', color: 'red' },
    { name: 'PROMPT EVALUATOR', icon: 'award', desc: 'SCORE PROMPT QUALITY METRICS', href: 'docs-site/skills/evaluator.html', color: 'green' },
    { name: 'PROMPT DOCUMENTER', icon: 'file-text', desc: 'AUTO-GENERATE PROMPT DOCS', href: 'docs-site/skills/documenter.html', color: 'cyan' },
    { name: 'SYSTEM PROMPT DESIGNER', icon: 'bot', desc: 'CRAFT OPTIMAL SYSTEM PROMPTS', href: 'docs-site/skills/system-prompt-designer.html', color: 'magenta' }
  ];

  // ── DOM ELEMENTS ──
  const featuresGrid = document.getElementById('featuresGrid');
  const skillsGrid = document.getElementById('skillsGrid');
  const floatingElements = document.getElementById('floatingElements');
  const gridPattern = document.getElementById('gridPattern');
  const scanline = document.getElementById('scanline');
  const paperFloatShapes = document.getElementById('paperFloatShapes');

  // ── RENDER FUNCTIONS ──
  function renderFeatures() {
    if (!featuresGrid) return;
    featuresGrid.innerHTML = features.map((feature, i) => `
      <article class="feature-card card paper-brutal ${feature.variant !== 'default' ? 'paper-brutal-' + feature.variant : ''} paper-stack-reveal stagger-${i + 1}" style="animation-delay: ${i * 100}ms; padding: var(--space-6);">
        <div class="feature-icon" style="color: var(--accent-${feature.variant !== 'default' ? feature.variant : 'cyan'});">${feature.icon}</div>
        <h3>${feature.title}</h3>
        <p>${feature.desc}</p>
        <ul class="feature-list">
          ${feature.items.map(item => `<li>${item}</li>`).join('')}
        </ul>
      </article>
    `).join('');
  }

  function renderSkills() {
    if (!skillsGrid) return;
    skillsGrid.innerHTML = skills.map((skill, i) => `
      <a href="${skill.href}" class="doc-card card paper-brutal paper-brutal-${skill.color} paper-stack-reveal stagger-${(i % 8) + 1}" style="padding: var(--space-6); display: flex; flex-direction: column; height: 100%; text-decoration: none; color: inherit; transition: all var(--dur-base) var(--ease-expo);">
        <div class="doc-icon" style="color: var(--accent-${skill.color});">${getSkillIcon(skill.icon)}</div>
        <h3>${skill.name}</h3>
        <p style="font-size: var(--text-sm); flex: 1; margin-bottom: var(--space-4);">${skill.desc}</p>
        <span class="doc-link" style="font-family: var(--font-mono); font-size: var(--text-xs); font-weight: var(--font-weight-bold); color: var(--accent-${skill.color}); text-transform: uppercase; letter-spacing: 0.05em;">VIEW SKILL <i data-lucide="arrow-right" style="width: 14px; height: 14px;"></i></span>
      </a>
    `).join('');
    if (typeof lucide !== 'undefined') lucide.createIcons();
  }

  function getSkillIcon(name) {
    const icons = {
      search: `<svg xmlns="http://www.w3.org/2000/svg" width="28" height="28" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.5" stroke-linecap="round" stroke-linejoin="round"><circle cx="11" cy="11" r="8"></circle><line x1="21" y1="21" x2="16.65" y2="16.65"></line></svg>`,
      zap: `<svg xmlns="http://www.w3.org/2000/svg" width="28" height="28" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.5" stroke-linecap="round" stroke-linejoin="round"><polyline points="23 4 23 10 17 10"></polyline><path d="M20.49 15a9 9 0 1 1-2.12-9.36L23 10"></path></svg>`,
      'shield-check': `<svg xmlns="http://www.w3.org/2000/svg" width="28" height="28" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.5" stroke-linecap="round" stroke-linejoin="round"><path d="M22 11.08V12a10 10 0 1 1-5.93-9.14"></path><polyline points="22 4 12 14.01 9 11.01"></polyline></svg>`,
      cpu: `<svg xmlns="http://www.w3.org/2000/svg" width="28" height="28" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.5" stroke-linecap="round" stroke-linejoin="round"><rect x="2" y="3" width="20" height="14" rx="0"></rect><path d="M8 21h13a2 2 0 0 0 2-2V5"></path></svg>`,
      layers: `<svg xmlns="http://www.w3.org/2000/svg" width="28" height="28" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.5" stroke-linecap="round" stroke-linejoin="round"><polygon points="12 2 2 7 12 12 22 7 12 2"></polygon><polyline points="2 17 12 22 22 17"></polyline><polyline points="2 12 12 17 22 12"></polyline></svg>`,
      'shield-alert': `<svg xmlns="http://www.w3.org/2000/svg" width="28" height="28" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.5" stroke-linecap="round" stroke-linejoin="round"><path d="M12 22s8-4 8-10V5l-8-3-8 3v7c0 6 8 10 8 10z"></path><line x1="12" y1="8" x2="12.01" y2="8"></line><line x1="12" y1="16" x2="12.01" y2="16"></line></svg>`,
      'dollar-sign': `<svg xmlns="http://www.w3.org/2000/svg" width="28" height="28" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.5" stroke-linecap="round" stroke-linejoin="round"><line x1="12" y1="1" x2="12" y2="23"></line><path d="M17 5H9.5a3.5 3.5 0 0 0 0 7h5a3.5 3.5 0 0 1 0 7H6"></path></svg>`,
      'git-merge': `<svg xmlns="http://www.w3.org/2000/svg" width="28" height="28" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.5" stroke-linecap="round" stroke-linejoin="round"><circle cx="18" cy="18" r="3"></circle><circle cx="6" cy="6" r="3"></circle><path d="M6 21V9a9 9 0 0 0 9 9"></path></svg>`,
      braces: `<svg xmlns="http://www.w3.org/2000/svg" width="28" height="28" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.5" stroke-linecap="round" stroke-linejoin="round"><path d="M8 3H7a2 2 0 0 0-2 2v5a2 2 0 0 1-2 2 2 2 0 0 1 2 2v5a2 2 0 0 0 2 2h1"></path><path d="M16 21h1a2 2 0 0 0 2-2v-5a2 2 0 0 1 2-2 2 2 0 0 1-2-2V5a2 2 0 0 0-2-2h-1"></path></svg>`,
      copy: `<svg xmlns="http://www.w3.org/2000/svg" width="28" height="28" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.5" stroke-linecap="round" stroke-linejoin="round"><rect x="9" y="9" width="13" height="13" rx="2" ry="2"></rect><path d="M5 15H4a2 2 0 0 1-2-2V4a2 2 0 0 1 2-2h9a2 2 0 0 1 2 2v1"></path></svg>`,
      'git-branch': `<svg xmlns="http://www.w3.org/2000/svg" width="28" height="28" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.5" stroke-linecap="round" stroke-linejoin="round"><line x1="6" y1="3" x2="6" y2="15"></line><circle cx="18" cy="6" r="3"></circle><circle cx="6" cy="18" r="3"></circle><path d="M18 9a9 9 0 0 1 0 18"></path></svg>`,
      award: `<svg xmlns="http://www.w3.org/2000/svg" width="28" height="28" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.5" stroke-linecap="round" stroke-linejoin="round"><circle cx="12" cy="8" r="7"></circle><polyline points="8.21 13.89 7 23 12 20 17 23 15.79 13.88"></polyline></svg>`,
      'file-text': `<svg xmlns="http://www.w3.org/2000/svg" width="28" height="28" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.5" stroke-linecap="round" stroke-linejoin="round"><path d="M14 2H6a2 2 0 0 0-2 2v16a2 2 0 0 0 2 2h12a2 2 0 0 0 2-2V8z"></path><polyline points="14 2 14 8 20 8"></polyline><line x1="16" y1="13" x2="8" y2="13"></line><line x1="16" y1="17" x2="8" y2="17"></line><polyline points="10 9 9 9 8 9"></polyline></svg>`,
      bot: `<svg xmlns="http://www.w3.org/2000/svg" width="28" height="28" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.5" stroke-linecap="round" stroke-linejoin="round"><rect x="2" y="9" width="20" height="12" rx="2"></rect><path d="M6 13V9"></path><path d="M10 13V9"></path><path d="M14 17V13"></path><path d="M18 13V9"></path></svg>`
    };
    return icons[name] || icons.search;
  }

  // ── PAPER BACKGROUND EFFECTS ──
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

  function createPaperFloatShapes() {
    if (!paperFloatShapes) return;
    const paperShapes = [
      { char: '☐', color: 'var(--accent-cyan)' },
      { char: '☑', color: 'var(--accent-magenta)' },
      { char: '☒', color: 'var(--accent-lime)' },
      { char: '▢', color: 'var(--accent-gold)' },
      { char: '▣', color: 'var(--accent-cyan)' },
      { char: '▤', color: 'var(--accent-magenta)' },
      { char: '▥', color: 'var(--accent-lime)' },
      { char: '▦', color: 'var(--accent-gold)' }
    ];
    
    paperFloatShapes.innerHTML = paperShapes.map((shape, i) => `
      <div class="float-shape-item" style="
        --size: ${16 + Math.random() * 20}px;
        --color: ${shape.color};
        --opacity: ${0.05 + Math.random() * 0.08};
        --duration: ${10 + Math.random() * 8}s;
        --delay: ${i * 0.8}s;
        --x: ${10 + Math.random() * 80}%;
        --y: ${10 + Math.random() * 80}%;
      ">${shape.char}</div>
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
    
    // Observe elements with paper-reveal classes
    document.querySelectorAll('.paper-reveal, .paper-stack-reveal, .feature-card, .doc-card, .contribute-card').forEach(el => {
      observer.observe(el);
    });
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
          
          // Parallax paper shapes
          const paperShapes = document.querySelectorAll('.float-shape-item');
          paperShapes.forEach((shape, i) => {
            const speed = 0.05 + (i % 3) * 0.03;
            shape.style.transform = `translateY(${scrolled * speed}px) rotate(${scrolled * 0.01}deg)`;
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
      document.documentElement.style.setProperty('--dur-slower', '0ms');
    }
    mediaQuery.addEventListener('change', checkReducedMotion);
  }

  // ── INTERACTIVE PAPER FLIP HOVER EFFECTS ──
  function initPaperInteractions() {
    // Add hover effects to paper-interactive-flip elements
    document.querySelectorAll('.paper-interactive-flip').forEach(card => {
      card.addEventListener('mouseenter', () => {
        card.style.transform = 'translate(-4px, -4px)';
      });
      card.addEventListener('mouseleave', () => {
        card.style.transform = '';
      });
    });
    
    // Add click ripple effect to buttons
    document.querySelectorAll('.btn').forEach(btn => {
      btn.addEventListener('click', function(e) {
        const ripple = document.createElement('span');
        const rect = this.getBoundingClientRect();
        const size = Math.max(rect.width, rect.height);
        const x = e.clientX - rect.left - size / 2;
        const y = e.clientY - rect.top - size / 2;
        
        ripple.style.cssText = `
          position: absolute;
          width: ${size}px;
          height: ${size}px;
          left: ${x}px;
          top: ${y}px;
          background: rgba(255,255,255,0.3);
          border-radius: 0;
          transform: scale(0);
          animation: ripple 0.4s var(--ease-expo) forwards;
          pointer-events: none;
          z-index: 1;
        `;
        
        this.appendChild(ripple);
        setTimeout(() => ripple.remove(), 400);
      });
    });
    
    // Add ripple keyframes if not exists
    if (!document.getElementById('ripple-style')) {
      const style = document.createElement('style');
      style.id = 'ripple-style';
      style.textContent = `
        @keyframes ripple {
          to {
            transform: scale(2);
            opacity: 0;
          }
        }
      `;
      document.head.appendChild(style);
    }
  }

  // ── SMOOTH SCROLL FOR ANCHOR LINKS ──
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

  // ── COPY CODE BUTTONS ──
  function initCodeCopy() {
    document.querySelectorAll('.code-block, .code-block-paper').forEach(block => {
      if (block.querySelector('.copy-btn')) return;
      
      const pre = block.querySelector('pre');
      if (!pre) return;
      
      const copyBtn = document.createElement('button');
      copyBtn.className = 'copy-btn';
      copyBtn.innerHTML = '<svg xmlns="http://www.w3.org/2000/svg" width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><rect x="9" y="9" width="13" height="13" rx="2" ry="2"></rect><path d="M5 15H4a2 2 0 0 1-2-2V4a2 2 0 0 1 2-2h9a2 2 0 0 1 2 2v1"></path></svg>';
      copyBtn.style.cssText = `
        position: absolute;
        top: var(--space-3);
        right: var(--space-3);
        background: var(--bg-elevated);
        border: var(--border-thin) solid var(--border);
        padding: var(--space-1);
        cursor: pointer;
        opacity: 0;
        transition: opacity var(--dur-fast);
      `;
      
      block.style.position = 'relative';
      block.appendChild(copyBtn);
      
      block.addEventListener('mouseenter', () => copyBtn.style.opacity = '1');
      block.addEventListener('mouseleave', () => copyBtn.style.opacity = '0');
      
      copyBtn.addEventListener('click', async () => {
        const code = pre.querySelector('code')?.textContent || pre.textContent;
        try {
          await navigator.clipboard.writeText(code);
          copyBtn.innerHTML = '<svg xmlns="http://www.w3.org/2000/svg" width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><polyline points="20 6 9 17 4 12"></polyline></svg>';
          setTimeout(() => {
            copyBtn.innerHTML = '<svg xmlns="http://www.w3.org/2000/svg" width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><rect x="9" y="9" width="13" height="13" rx="2" ry="2"></rect><path d="M5 15H4a2 2 0 0 1-2-2V4a2 2 0 0 1 2-2h9a2 2 0 0 1 2 2v1"></path></svg>';
          }, 1500);
        } catch (err) {
          // Fallback
          const textarea = document.createElement('textarea');
          textarea.value = code;
          document.body.appendChild(textarea);
          textarea.select();
          document.execCommand('copy');
          document.body.removeChild(textarea);
        }
      });
    });
  }

  // ── IMAGE LAZY LOADING ──
  function initLazyImages() {
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

  // ── INITIALIZE EVERYTHING ──
  function init() {
    renderFeatures();
    renderSkills();
    createFloatingElements();
    createPaperFloatShapes();
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
    initPaperInteractions();
    initSmoothScroll();
    initCodeCopy();
    initLazyImages();
    
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
    skills,
    init
  };

})();

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