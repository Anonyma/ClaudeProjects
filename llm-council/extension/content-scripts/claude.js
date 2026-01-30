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

  // Human-like random delay (100-400ms)
  function humanDelay() {
    const delay = 100 + Math.random() * 300;
    return new Promise(r => setTimeout(r, delay));
  }

  // Longer random delay for actions (500-1500ms)
  function actionDelay() {
    const delay = 500 + Math.random() * 1000;
    return new Promise(r => setTimeout(r, delay));
  }

  // Get the current conversation URL
  function getConversationUrl() {
    // Claude URLs look like: https://claude.ai/chat/abc123...
    const url = window.location.href;
    if (url.includes('/chat/')) {
      return url;
    }
    return null;
  }

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

  // Set contenteditable value with human-like typing
  async function setContentEditableValue(element, value) {
    element.focus();
    element.innerHTML = '';

    // Type first few characters for human-like behavior
    const typePrefix = value.substring(0, Math.min(10, value.length));
    const restValue = value.substring(typePrefix.length);

    for (const char of typePrefix) {
      document.execCommand('insertText', false, char);
      await new Promise(r => setTimeout(r, 20 + Math.random() * 30)); // 20-50ms per char
    }

    // Paste the rest
    if (restValue) {
      document.execCommand('insertText', false, restValue);
    }

    // Dispatch input event
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

    // Focus and set value with human-like delays
    await humanDelay();
    input.focus();
    await humanDelay();
    await setContentEditableValue(input, prompt);

    // Delay before clicking send (like a human reviewing)
    await actionDelay();

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

  // Wait for URL to update (Claude creates conversation after first message)
  async function waitForConversationUrl(timeout = 10000) {
    const startTime = Date.now();

    return new Promise((resolve) => {
      const checkUrl = () => {
        const url = getConversationUrl();
        if (url) {
          resolve(url);
          return;
        }

        if (Date.now() - startTime > timeout) {
          resolve(null); // Timeout, but don't fail - URL is optional
          return;
        }

        setTimeout(checkUrl, 500);
      };

      setTimeout(checkUrl, 1000); // Wait a bit before first check
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

        // Wait for both response and URL
        const [response, conversationUrl] = await Promise.all([
          waitForResponse(),
          waitForConversationUrl()
        ]);

        chrome.runtime.sendMessage({
          type: 'QUERY_RESPONSE',
          queryId,
          response,
          conversationUrl
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
