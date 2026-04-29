/**
 * Rikugan Code Block Copy Button
 * Adds copy-to-clipboard functionality to all code blocks
 *
 * Features:
 * - One-click copy for individual code blocks
 * - Success feedback with visual state changes
 * - Keyboard shortcut support (Ctrl/Cmd + Shift + C)
 * - Mobile-friendly with long-press support
 * - Multiple code block handling
 * - Copy all blocks functionality
 */

(function() {
  'use strict';

  // Configuration
  const CONFIG = {
    buttonText: 'Copy',
    successText: 'Copied!',
    successDuration: 2000,
    longPressDuration: 500,
    keyboardShortcut: true
  };

  /**
   * Initialize copy buttons for all code blocks
   */
  function initCopyButtons() {
    const codeBlocks = document.querySelectorAll('pre code');

    codeBlocks.forEach((codeBlock, index) => {
      const pre = codeBlock.parentElement;
      const button = createCopyButton(index);
      pre.appendChild(button);

      // Add event listeners
      button.addEventListener('click', (e) => {
        e.preventDefault();
        copyCode(codeBlock, button);
      });

      // Touch events for mobile
      button.addEventListener('touchstart', handleTouchStart, { passive: true });
      button.addEventListener('touchend', handleTouchEnd);

      // Keyboard accessibility
      button.addEventListener('keydown', (e) => {
        if (e.key === 'Enter' || e.key === ' ') {
          e.preventDefault();
          copyCode(codeBlock, button);
        }
      });
    });

    // Add keyboard shortcut listener
    if (CONFIG.keyboardShortcut) {
      document.addEventListener('keydown', handleKeyboardShortcut);
    }

    // Add "Copy All" button if multiple code blocks exist
    if (codeBlocks.length > 1) {
      addCopyAllButton(codeBlocks);
    }
  }

  /**
   * Create a copy button element
   */
  function createCopyButton(index) {
    const button = document.createElement('button');
    button.className = 'copy-btn';
    button.textContent = CONFIG.buttonText;
    button.setAttribute('data-tooltip', 'Click to copy');
    button.setAttribute('aria-label', `Copy code block ${index + 1}`);
    button.setAttribute('type', 'button');
    button.setAttribute('data-index', index);

    return button;
  }

  /**
   * Copy code to clipboard
   */
  async function copyCode(codeBlock, button) {
    try {
      const code = codeBlock.textContent;

      // Use modern Clipboard API
      if (navigator.clipboard && window.isSecureContext) {
        await navigator.clipboard.writeText(code);
        showSuccess(button);
      } else {
        // Fallback for older browsers
        fallbackCopy(code, button);
      }

      // Track copy event (analytics)
      trackCopyEvent(button);
    } catch (error) {
      console.error('Failed to copy code:', error);
      showError(button);
    }
  }

  /**
   * Fallback copy method for older browsers
   */
  function fallbackCopy(text, button) {
    const textArea = document.createElement('textarea');
    textArea.value = text;
    textArea.style.position = 'fixed';
    textArea.style.left = '-999999px';
    textArea.style.top = '-999999px';
    document.body.appendChild(textArea);
    textArea.focus();
    textArea.select();

    try {
      const successful = document.execCommand('copy');
      if (successful) {
        showSuccess(button);
      } else {
        showError(button);
      }
    } catch (err) {
      showError(button);
    }

    document.body.removeChild(textArea);
  }

  /**
   * Show success state
   */
  function showSuccess(button) {
    button.classList.add('copied');
    button.textContent = CONFIG.successText;
    button.setAttribute('data-tooltip', 'Successfully copied!');

    setTimeout(() => {
      resetButton(button);
    }, CONFIG.successDuration);
  }

  /**
   * Show error state
   */
  function showError(button) {
    button.textContent = 'Failed!';
    button.setAttribute('data-tooltip', 'Failed to copy. Try again.');
    button.style.borderColor = 'var(--pink)';

    setTimeout(() => {
      resetButton(button);
    }, CONFIG.successDuration);
  }

  /**
   * Reset button to default state
   */
  function resetButton(button) {
    button.classList.remove('copied', 'loading');
    button.textContent = CONFIG.buttonText;
    button.setAttribute('data-tooltip', 'Click to copy');
    button.style.borderColor = '';
  }

  /**
   * Handle keyboard shortcut for focused code block
   */
  function handleKeyboardShortcut(e) {
    // Ctrl/Cmd + Shift + C to copy focused code block
    if ((e.ctrlKey || e.metaKey) && e.shiftKey && e.key === 'C') {
      const activeElement = document.activeElement;
      const pre = activeElement?.closest('pre');

      if (pre) {
        e.preventDefault();
        const button = pre.querySelector('.copy-btn');
        const codeBlock = pre.querySelector('code');

        if (button && codeBlock) {
          copyCode(codeBlock, button);
        }
      }
    }
  }

  /**
   * Touch start handler for mobile long-press
   */
  let longPressTimer = null;

  function handleTouchStart(e) {
    longPressTimer = setTimeout(() => {
      e.target.classList.add('long-press');
    }, CONFIG.longPressDuration);
  }

  function handleTouchEnd(e) {
    if (longPressTimer) {
      clearTimeout(longPressTimer);
      longPressTimer = null;
    }
    e.target.classList.remove('long-press');
  }

  /**
   * Add "Copy All" button for multiple code blocks
   */
  function addCopyAllButton(codeBlocks) {
    const firstPre = codeBlocks[0]?.parentElement;
    if (!firstPre) return;

    const container = document.createElement('div');
    container.className = 'copy-all-container';
    container.style.cssText = 'text-align: center; margin: 20px 0;';

    const button = document.createElement('button');
    button.className = 'copy-all-btn';
    button.innerHTML = `
      <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
        <rect x="9" y="9" width="13" height="13" rx="2" ry="2"></rect>
        <path d="M5 15H4a2 2 0 0 1-2-2V4a2 2 0 0 1 2-2h9a2 2 0 0 1 2 2v1"></path>
      </svg>
      Copy All Code Blocks
    `;

    button.addEventListener('click', async () => {
      const allCode = Array.from(codeBlocks)
        .map(block => block.textContent)
        .join('\n\n' + '='.repeat(50) + '\n\n');

      try {
        if (navigator.clipboard && window.isSecureContext) {
          await navigator.clipboard.writeText(allCode);
          button.innerHTML = `
            <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
              <polyline points="20 6 9 17 4 12"></polyline>
            </svg>
            All Copied!
          `;
          setTimeout(() => resetCopyAllButton(button), CONFIG.successDuration);
        }
      } catch (error) {
        console.error('Failed to copy all code:', error);
        button.textContent = 'Failed to copy';
        setTimeout(() => resetCopyAllButton(button), CONFIG.successDuration);
      }
    });

    container.appendChild(button);
    firstPre.parentNode.insertBefore(container, firstPre);
  }

  function resetCopyAllButton(button) {
    button.innerHTML = `
      <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
        <rect x="9" y="9" width="13" height="13" rx="2" ry="2"></rect>
        <path d="M5 15H4a2 2 0 0 1-2-2V4a2 2 0 0 1 2-2h9a2 2 0 0 1 2 2v1"></path>
      </svg>
      Copy All Code Blocks
    `;
  }

  /**
   * Track copy events (placeholder for analytics)
   */
  function trackCopyEvent(button) {
    const index = button.getAttribute('data-index');
    const language = button.closest('pre')?.querySelector('code')?.className || 'unknown';

    // Send to analytics if available
    if (window.gtag) {
      gtag('event', 'copy_code', {
        'code_block_index': index,
        'language': language
      });
    }

    // Log for debugging
    console.log(`Code block ${index} copied (language: ${language})`);
  }

  /**
   * Auto-initialize when DOM is ready
   */
  if (document.readyState === 'loading') {
    document.addEventListener('DOMContentLoaded', initCopyButtons);
  } else {
    initCopyButtons();
  }

  // Re-initialize when content changes (for dynamic content)
  const observer = new MutationObserver(() => {
    const existingButtons = document.querySelectorAll('.copy-btn');
    const codeBlocks = document.querySelectorAll('pre code');

    if (existingButtons.length !== codeBlocks.length) {
      // Remove existing buttons
      existingButtons.forEach(btn => btn.remove());
      // Re-initialize
      initCopyButtons();
    }
  });

  observer.observe(document.body, {
    childList: true,
    subtree: true
  });

  // Expose public API
  window.RikuganCopyButton = {
    init: initCopyButtons,
    copy: copyCode,
    copyAll: (codeBlocks) => {
      const allCode = Array.from(codeBlocks)
        .map(block => block.textContent)
        .join('\n\n' + '='.repeat(50) + '\n\n');
      return navigator.clipboard.writeText(allCode);
    }
  };

})();
