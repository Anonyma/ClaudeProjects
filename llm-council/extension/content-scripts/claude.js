/**
 * Claude Content Script
 * Interacts with claude.ai web interface
 *
 * NOTE: Claude's DOM structure may change.
 * Update selectors as needed when the interface changes.
 */

(function () {
  const PROVIDER = 'claude';

  // Selectors (update these when Claude changes their UI)
  const SELECTORS = {
    // Main chat input - Claude uses contenteditable div
    input: '[contenteditable="true"].ProseMirror, div[data-placeholder*="Reply"]',
    // Send button
    sendButton: 'button[aria-label="Send Message"], button:has(svg[viewBox*="send"])',
    // Message containers - Claude's response blocks
    messageContainer: '[data-is-streaming], .font-claude-message, [class*="claude-message"]',
    // Loading/streaming indicator
    loading: '[data-is-streaming="true"], .animate-pulse',
    // New chat
    newChat: 'a[href="/new"], button[aria-label="New chat"]'
  };

  let isReady = false;

  // Notify background script that we're ready
  function notifyReady() {
    chrome.runtime.sendMessage({
      type: 'CONTENT_SCRIPT_READY',
      provider: PROVIDER
    });
    isReady = true;
    console.log(`[LLM Council] ${PROVIDER} content script ready`);
  }

  // Wait for page to be fully loaded
  function waitForPage() {
    return new Promise((resolve) => {
      const checkReady = () => {
        const input = document.querySelector(SELECTORS.input);
        if (input) {
          resolve();
        } else {
          setTimeout(checkReady, 500);
        }
      };
      checkReady();
    });
  }

  // Set contenteditable value
  function setContentEditableValue(element, value) {
    element.focus();
    element.innerHTML = '';

    // Use execCommand for better compatibility with ProseMirror
    document.execCommand('insertText', false, value);

    // Also dispatch input event
    element.dispatchEvent(new InputEvent('input', {
      bubbles: true,
      cancelable: true,
      inputType: 'insertText',
      data: value
    }));
  }

  // Send a query
  async function sendQuery(prompt) {
    const input = document.querySelector(SELECTORS.input);
    if (!input) {
      throw new Error('Could not find Claude input field');
    }

    // Focus and set value
    input.focus();
    setContentEditableValue(input, prompt);

    // Small delay for React/ProseMirror to process
    await new Promise(r => setTimeout(r, 200));

    // Click send button
    const sendBtn = document.querySelector(SELECTORS.sendButton);
    if (sendBtn) {
      sendBtn.click();
    } else {
      // Try pressing Enter
      input.dispatchEvent(new KeyboardEvent('keydown', {
        key: 'Enter',
        code: 'Enter',
        keyCode: 13,
        which: 13,
        bubbles: true
      }));
    }
  }

  // Wait for response to complete
  async function waitForResponse(timeout = 120000) {
    const startTime = Date.now();

    // Wait for response to start
    await new Promise(r => setTimeout(r, 1000));

    return new Promise((resolve, reject) => {
      const checkComplete = () => {
        if (Date.now() - startTime > timeout) {
          reject(new Error('Response timeout'));
          return;
        }

        // Check if still streaming
        const streaming = document.querySelector('[data-is-streaming="true"]');
        if (streaming) {
          setTimeout(checkComplete, 500);
          return;
        }

        // Get all Claude message blocks
        // Look for the response content - Claude wraps responses in specific elements
        const allMessages = document.querySelectorAll('[class*="message"], [class*="response"]');
        let lastResponse = '';

        // Find the most recent assistant/Claude message
        for (const msg of allMessages) {
          // Skip user messages
          if (msg.closest('[class*="user"]') || msg.querySelector('[class*="user"]')) continue;

          const text = msg.textContent || msg.innerText;
          if (text && text.length > lastResponse.length) {
            lastResponse = text;
          }
        }

        if (lastResponse) {
          resolve(lastResponse.trim());
        } else {
          // No response yet, keep waiting
          setTimeout(checkComplete, 500);
        }
      };

      setTimeout(checkComplete, 2000);
    });
  }

  // Handle incoming query from background script
  chrome.runtime.onMessage.addListener((message, sender, sendResponse) => {
    if (message.type !== 'SEND_QUERY') return;

    const { queryId, prompt } = message;
    console.log(`[LLM Council] ${PROVIDER} received query:`, queryId);

    (async () => {
      try {
        await sendQuery(prompt);
        const response = await waitForResponse();

        chrome.runtime.sendMessage({
          type: 'QUERY_RESPONSE',
          queryId,
          response
        });
      } catch (error) {
        chrome.runtime.sendMessage({
          type: 'QUERY_RESPONSE',
          queryId,
          error: error.message
        });
      }
    })();

    sendResponse({ received: true });
    return true;
  });

  // Initialize
  waitForPage().then(notifyReady);
})();
