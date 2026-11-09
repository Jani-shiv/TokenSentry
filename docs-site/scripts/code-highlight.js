/* ==========================================================================
   TokenSentry Documentation - Code Highlighting
   ========================================================================== */

(function() {
  'use strict';

  function initCodeHighlight() {
    // Add copy buttons to code blocks
    document.querySelectorAll('pre').forEach(pre => {
      if (pre.querySelector('.code-actions')) return;

      const header = document.createElement('div');
      header.className = 'code-header';
      header.innerHTML = `
        <span class="code-language">${getLanguage(pre)}</span>
        <div class="code-actions">
          <button class="code-action-btn" aria-label="Copy code" title="Copy to clipboard">
            <svg xmlns="http://www.w3.org/2000/svg" width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round">
              <rect x="9" y="9" width="13" height="13" rx="2" ry="2"></rect>
              <path d="M5 15H4a2 2 0 0 1-2-2V4a2 2 0 0 1 2-2h9a2 2 0 0 1 2 2v1"></path>
            </svg>
          </button>
        </div>
      `;

      pre.insertBefore(header, pre.firstChild);

      const copyBtn = header.querySelector('.code-action-btn');
      copyBtn?.addEventListener('click', () => copyCode(pre));
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
      <svg xmlns="http://www.w3.org/2000/svg" width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round">
        <polyline points="20 6 9 17 4 12"></polyline>
      </svg>
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

  function getLanguage(pre) {
    const code = pre.querySelector('code');
    if (!code) return 'text';

    const className = code.className || '';
    const match = className.match(/language-(\w+)/);
    return match ? match[1] : 'text';
  }

  // Initialize on DOM ready
  if (document.readyState === 'loading') {
    document.addEventListener('DOMContentLoaded', () => {
      initCodeHighlight();
      if (window.Prism) {
        Prism.highlightAll();
      }
    });
  } else {
    initCodeHighlight();
    if (window.Prism) {
      Prism.highlightAll();
    }
  }

  // Re-initialize on dynamic content
  document.addEventListener('tokensentry:content-loaded', () => {
    initCodeHighlight();
    if (window.Prism) {
      Prism.highlightAll();
    }
  });
})();