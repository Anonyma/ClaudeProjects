/**
 * ChatGPT Content Script
 * Interacts with chatgpt.com web interface
 *
 * NOTE: ChatGPT's DOM structure changes frequently.
 * Update selectors as needed when the interface changes.
 */

(function () {
  const PROVIDER = 'chatgpt';

  // Selectors (update these when ChatGPT changes their UI)
  const SELECTORS = {
    // Main chat input textarea
    input: '#prompt-textarea, textarea[data-id="root"]',
    // Send button
    sendButton: 'button[data-testid="send-button"], button[aria-label="Send prompt"]',
    // Message containers
    messageContainer: '[data-message-author-role="assistant"]',
    // Loading indicator
    loading: '.result-streaming, [data-testid*="loading"]',
    // New chat button
    newChat: 'a[href="/"], button:has-text("New chat")'
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
    // ChatGPT URLs look like: https://chatgpt.com/c/abc123...
    const url = window.location.href;
    // Wait a moment for URL to update after sending
    if (url.includes('/c/') || url.includes('/g/')) {
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

  // Set input value (React-compatible)
  async function setInputValue(element, value) {
    const nativeInputValueSetter = Object.getOwnPropertyDescriptor(
      window.HTMLTextAreaElement.prototype,
      'value'
    ).set;

    // Type character by character for more human-like behavior (first 10 chars, then paste rest)
    const typePrefix = value.substring(0, Math.min(10, value.length));
    const restValue = value.substring(typePrefix.length);

    for (const char of typePrefix) {
      nativeInputValueSetter.call(element, element.value + char);
      element.dispatchEvent(new Event('input', { bubbles: true }));
      await new Promise(r => setTimeout(r, 20 + Math.random() * 30)); // 20-50ms per char
    }

    // Paste the rest
    if (restValue) {
      nativeInputValueSetter.call(element, element.value + restValue);
      element.dispatchEvent(new Event('input', { bubbles: true }));
    }
  }

  // Send a query
  async function sendQuery(prompt) {
    const input = document.querySelector(SELECTORS.input);
    if (!input) {
      throw new Error('Could not find ChatGPT input field');
    }

    // Focus and set value with human-like delays
    await humanDelay();
    input.focus();
    await humanDelay();
    await setInputValue(input, prompt);

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

    // Wait for loading to start
    await new Promise(r => setTimeout(r, 1000));

    return new Promise((resolve, reject) => {
      const checkComplete = () => {
        if (Date.now() - startTime > timeout) {
          reject(new Error('Response timeout'));
          return;
        }

        const loading = document.querySelector(SELECTORS.loading);
        if (loading) {
          // Still loading, check again
          setTimeout(checkComplete, 500);
          return;
        }

        // Get the last assistant message
        const messages = document.querySelectorAll(SELECTORS.messageContainer);
        if (messages.length > 0) {
          const lastMessage = messages[messages.length - 1];
          const content = lastMessage.textContent || lastMessage.innerText;
          resolve(content.trim());
        } else {
          // No messages yet, keep waiting
          setTimeout(checkComplete, 500);
        }
      };

      setTimeout(checkComplete, 2000);
    });
  }

  // Wait for URL to update (ChatGPT creates conversation after first message)
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
