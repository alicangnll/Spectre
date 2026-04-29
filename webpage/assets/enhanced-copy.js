/**
 * Enhanced Copy Button for All Code Types
 * Supports: Markdown code blocks, inline code, syntax highlighted blocks
 *
 * Features:
 * - Automatic detection of code block types
 * - Support for GitHub-style markdown code blocks
 * - Inline code copy functionality
 * - Batch copy for multiple blocks
 * - Language-specific formatting
 */

(function() {
  'use strict';

  const CONFIG = {
    selectors: [
      'pre code',           // Standard markdown code blocks
      'pre[class*="language-"] code',  // Syntax highlighted blocks
      'code.highlight',      // Manually highlighted blocks
      '.code-block',         // Custom code block containers
      'blockquote code',    // Code in blockquotes
      '.example code'        // Code in example containers
    ],
    inlineSelectors: [
      'p code',              // Inline code in paragraphs
      'li code',             // Inline code in lists
      'td code',             // Inline code in tables
      ':not(pre) > code'     // Any inline code not in pre
    ],
    buttonText: '📋',
    successText: '✓',
    tooltipText: 'Click to copy',
    successDuration: 1500
  };

  /**
   * Initialize copy buttons for all code block types
   */
  function initEnhancedCopyButtons() {
    // Handle block-level code
    CONFIG.selectors.forEach(selector => {
      document.querySelectorAll(selector).forEach(addBlockCopyButton);
    });

    // Handle inline code
    if (window.innerWidth > 768) { // Only on desktop
      CONFIG.inlineSelectors.forEach(selector => {
        document.querySelectorAll(selector).forEach(addInlineCopyButton);
      });
    }

    // Add keyboard shortcuts
    initKeyboardShortcuts();

    // Observe dynamic content
    observeContentChanges();
  }

  /**
   * Add copy button to block-level code
   */
  function addBlockCopyButton(codeElement) {
    const pre = codeElement.closest('pre') || codeElement.parentElement;

    // Skip if already has button
    if (pre && pre.querySelector('.copy-btn')) {
      return;
    }

    const button = createCopyButton('block');

    if (pre && pre !== codeElement) {
      pre.style.position = 'relative';
      pre.appendChild(button);
    } else {
      const wrapper = document.createElement('div');
      wrapper.className = 'code-block-wrapper';
      wrapper.style.position = 'relative';
      codeElement.parentNode.insertBefore(wrapper, codeElement);
      wrapper.appendChild(codeElement);
      wrapper.appendChild(button);
    }

    // Store reference to code
    button.dataset.codeTarget = getElementSelector(codeElement);

    button.addEventListener('click', (e) => {
      e.preventDefault();
      copyBlockCode(codeElement, button);
    });
  }

  /**
   * Add copy button to inline code
   */
  function addInlineCopyButton(codeElement) {
    // Skip if too short
    const text = codeElement.textContent.trim();
    if (text.length < 5) {
      return;
    }

    // Skip if already processed
    if (codeElement.hasAttribute('data-copy-enabled')) {
      return;
    }

    codeElement.setAttribute('data-copy-enabled', 'true');
    codeElement.style.cursor = 'pointer';
    codeElement.style.position = 'relative';

    // Add tooltip
    const tooltip = document.createElement('span');
    tooltip.className = 'inline-copy-tooltip';
    tooltip.textContent = 'Click to copy';
    tooltip.style.cssText = `
      position: absolute;
      bottom: 100%;
      left: 50%;
      transform: translateX(-50%);
      background: var(--bg-card, #1a1a2e);
      color: var(--text, #e2e2ea);
      padding: 4px 8px;
      border-radius: 4px;
      font-size: 12px;
      white-space: nowrap;
      opacity: 0;
      pointer-events: none;
      transition: opacity 0.2s;
      z-index: 100;
      border: 1px solid var(--border, #282840);
    `;

    codeElement.appendChild(tooltip);

    codeElement.addEventListener('click', (e) => {
      e.preventDefault();
      copyInlineCode(codeElement, tooltip);
    });

    codeElement.addEventListener('mouseenter', () => {
      tooltip.style.opacity = '1';
    });

    codeElement.addEventListener('mouseleave', () => {
      tooltip.style.opacity = '0';
    });
  }

  /**
   * Create copy button element
   */
  function createCopyButton(type = 'block') {
    const button = document.createElement('button');
    button.className = `copy-btn copy-btn-${type}`;
    button.innerHTML = CONFIG.buttonText;
    button.setAttribute('data-tooltip', CONFIG.tooltipText);
    button.setAttribute('aria-label', 'Copy code to clipboard');
    button.setAttribute('type', 'button');

    // Add keyboard accessibility
    button.setAttribute('tabindex', '0');

    return button;
  }

  /**
   * Copy block-level code
   */
  async function copyBlockCode(codeElement, button) {
    try {
      let code = codeElement.textContent;

      // Clean up common formatting issues
      code = code
        .replace(/^\s+|\s+$/g, '')  // Trim leading/trailing whitespace
        .replace(/\r\n/g, '\n')      // Normalize line endings
        .replace(/\t/g, '  ');       // Convert tabs to spaces

      // Remove language identifier if present (e.g., "python:", "bash:")
      code = code.replace(/^(python|bash|javascript|java|cpp|c|json|xml|html|css|sql|ruby|php|go|rust|swift|kotlin|yaml|toml|markdown|text|sh|shell|cmd|powershell|docker|dockerfile|git|graphql|yaml|yml|makefile|cmake|nginx|apache|conf|cfg|ini|toml|json|xml|html|css|js|ts|tsx|jsx|vue|svelte|scala|groovy|perl|lua|r|matlab|latex|tex|asm|assembly|nasm|yasm|gas|lldb|gdb|adb|log|txt|md|markdown):\s*/im, '');

      await copyToClipboard(code);
      showSuccess(button);
      trackCopy('block', codeElement);

    } catch (error) {
      console.error('Failed to copy code:', error);
      showError(button);
    }
  }

  /**
   * Copy inline code
   */
  async function copyInlineCode(codeElement, tooltip) {
    try {
      const code = codeElement.textContent.trim();
      await copyToClipboard(code);

      // Visual feedback
      tooltip.textContent = 'Copied!';
      tooltip.style.opacity = '1';
      tooltip.style.background = 'var(--green, #50c878)';

      setTimeout(() => {
        tooltip.textContent = 'Click to copy';
        tooltip.style.background = '';
        tooltip.style.opacity = '0';
      }, CONFIG.successDuration);

      trackCopy('inline', codeElement);

    } catch (error) {
      console.error('Failed to copy inline code:', error);
      tooltip.textContent = 'Failed!';
      tooltip.style.background = 'var(--pink, #e06090)';
      tooltip.style.opacity = '1';

      setTimeout(() => {
        tooltip.textContent = 'Click to copy';
        tooltip.style.background = '';
        tooltip.style.opacity = '0';
      }, CONFIG.successDuration);
    }
  }

  /**
   * Copy to clipboard using modern API or fallback
   */
  async function copyToClipboard(text) {
    if (navigator.clipboard && window.isSecureContext) {
      await navigator.clipboard.writeText(text);
    } else {
      fallbackCopy(text);
    }
  }

  /**
   * Fallback copy method
   */
  function fallbackCopy(text) {
    const textArea = document.createElement('textarea');
    textArea.value = text;
    textArea.style.position = 'fixed';
    textArea.style.left = '-999999px';
    textArea.style.top = '-999999px';
    document.body.appendChild(textArea);
    textArea.select();

    try {
      const successful = document.execCommand('copy');
      if (!successful) {
        throw new Error('execCommand failed');
      }
    } finally {
      document.body.removeChild(textArea);
    }
  }

  /**
   * Show success state
   */
  function showSuccess(button) {
    button.innerHTML = CONFIG.successText;
    button.classList.add('copied');
    button.setAttribute('data-tooltip', 'Copied to clipboard!');

    setTimeout(() => {
      resetButton(button);
    }, CONFIG.successDuration);
  }

  /**
   * Show error state
   */
  function showError(button) {
    button.innerHTML = '❌';
    button.classList.add('error');
    button.setAttribute('data-tooltip', 'Failed to copy');

    setTimeout(() => {
      resetButton(button);
    }, CONFIG.successDuration);
  }

  /**
   * Reset button to default state
   */
  function resetButton(button) {
    button.innerHTML = CONFIG.buttonText;
    button.classList.remove('copied', 'error');
    button.setAttribute('data-tooltip', CONFIG.tooltipText);
  }

  /**
   * Track copy events for analytics
   */
  function trackCopy(type, element) {
    const language = detectLanguage(element);
    const length = element.textContent.length;

    console.log(`Copied ${type} code (language: ${language}, length: ${length} chars)`);

    // Send to analytics if available
    if (window.gtag) {
      gtag('event', 'copy_code', {
        'code_type': type,
        'language': language,
        'content_length': length
      });
    }
  }

  /**
   * Detect programming language from code element
   */
  function detectLanguage(element) {
    // Check class names
    const classes = element.className || '';
    const langMatch = classes.match(/language-(\w+)/);
    if (langMatch) {
      return langMatch[1];
    }

    // Check parent pre element
    const pre = element.closest('pre');
    if (pre) {
      const preClasses = pre.className || '';
      const preLangMatch = preClasses.match(/language-(\w+)/);
      if (preLangMatch) {
        return preLangMatch[1];
      }
    }

    // Try to detect from content
    const code = element.textContent;

    // Simple detection patterns
    const patterns = {
      'python': /^(\s*(import|from|def|class)\s)/m,
      'javascript': /^(\s*(function|const|let|var|=>)\s)/m,
      'java': /^(\s*(public|private|protected|class|interface)\s)/m,
      'cpp': /^(\s*(#include|namespace|class|template)\s)/m,
      'bash': /^(\s*(#!/bin/bash|#!/bin/sh|if \[|fi|done|esac)\s)/m,
      'sql': /^(\s*(SELECT|INSERT|UPDATE|DELETE|CREATE|ALTER)\s)/mi,
      'json': /^\s*[{[].*\n.*[}\]]\s*$/s,
      'xml': /^(\s*<\?xml|<[^!?][^>]*>\s)/m,
      'html': /^(\s*<!DOCTYPE|<html|<head|<body)\s)/mi,
      'css': /^([.#][a-z-]+\s*:\s)/mi,
      'yaml': /^(\s*[a-z-]+:\s*\n)/m
    };

    for (const [lang, pattern] of Object.entries(patterns)) {
      if (pattern.test(code)) {
        return lang;
      }
    }

    return 'unknown';
  }

  /**
   * Get unique selector for element
   */
  function getElementSelector(element) {
    // Generate a simple selector
    const id = element.id;
    const className = element.className;
    const tagName = element.tagName.toLowerCase();

    if (id) {
      return `#${id}`;
    }

    if (className) {
      return `${tagName}.${className.split(' ')[0]}`;
    }

    return tagName;
  }

  /**
   * Initialize keyboard shortcuts
   */
  function initKeyboardShortcuts() {
    document.addEventListener('keydown', (e) => {
      // Ctrl/Cmd + Shift + C: Copy focused code block
      if ((e.ctrlKey || e.metaKey) && e.shiftKey && e.key === 'C') {
        const activeElement = document.activeElement;

        if (activeElement) {
          const codeElement = activeElement.closest('pre code, code');
          if (codeElement) {
            e.preventDefault();
            codeElement.click();
          }
        }
      }

      // Ctrl/Cmd + C: Copy inline code when clicked
      if ((e.ctrlKey || e.metaKey) && e.key === 'c') {
        const activeElement = document.activeElement;

        if (activeElement && activeElement.tagName === 'CODE' &&
            !activeElement.closest('pre')) {
          e.preventDefault();
          activeElement.click();
        }
      }
    });
  }

  /**
   * Observe DOM changes for dynamic content
   */
  function observeContentChanges() {
    const observer = new MutationObserver((mutations) => {
      mutations.forEach((mutation) => {
        mutation.addedNodes.forEach((node) => {
          if (node.nodeType === Node.ELEMENT_NODE) {
            // Check if node contains code
            const codeBlocks = node.querySelectorAll?.(
              CONFIG.selectors.join(', ')
            ) || [];

            const inlineCode = node.querySelectorAll?.(
              CONFIG.inlineSelectors.join(', ')
            ) || [];

            codeBlocks.forEach(addBlockCopyButton);
            inlineCode.forEach(addInlineCopyButton);
          }
        });
      });
    });

    observer.observe(document.body, {
      childList: true,
      subtree: true
    });
  }

  /**
   * Auto-initialize when DOM is ready
   */
  if (document.readyState === 'loading') {
    document.addEventListener('DOMContentLoaded', initEnhancedCopyButtons);
  } else {
    // Small delay to ensure other scripts have loaded
    setTimeout(initEnhancedCopyButtons, 100);
  }

  // Re-initialize on page changes (for SPA-like behavior)
  let lastUrl = location.href;
  new MutationObserver(() => {
    const url = location.href;
    if (url !== lastUrl) {
      lastUrl = url;
      setTimeout(initEnhancedCopyButtons, 500);
    }
  }).observe(document, { childList: true, subtree: true });

  // Expose public API
  window.RikuganEnhancedCopy = {
    init: initEnhancedCopyButtons,
    copyBlock: copyBlockCode,
    copyInline: copyInlineCode,
    detectLanguage: detectLanguage
  };

})();
