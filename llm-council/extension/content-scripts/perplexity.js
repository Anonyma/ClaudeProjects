/**
 * Perplexity Content Script
 * Interacts with perplexity.ai web interface
 *
 * NOTE: Perplexity's DOM structure may change.
 * Update selectors as needed when the interface changes.
 */

(function () {
  const PROVIDER = 'perplexity';

  // Selectors (update these when Perplexity changes their UI)
  const SELECTORS = {
    // Main chat input
    input: 'textarea[placeholder*="Ask" i], textarea[aria-label*="search" i], .search-input textarea',
    // Send button
    sendButton: 'button[aria-label*="Submit" i], button[type="submit"], button.submit-button',
    // Response container
    messageContainer: '.prose, .answer-content, [class*="answer"], [class*="response"]',
    // Loading indicator
    loading: '[class*="loading"], [class*="typing"], .animate-pulse',
    // Sources section
    sources: '.sources, [class*="sources"], [class*="citations"]'
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
    // Perplexity URLs look like: https://www.perplexity.ai/search/abc123...
    const url = window.location.href;
    if (url.includes('/search/')) {
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

  // Set textarea value with human-like typing
  async function setInputValue(element, value) {
    element.focus();

    const nativeInputValueSetter = Object.getOwnPropertyDescriptor(
      window.HTMLTextAreaElement.prototype,
      'value'
    ).set;

    // Type first few characters
    const typePrefix = value.substring(0, Math.min(10, value.length));
    const restValue = value.substring(typePrefix.length);

    for (const char of typePrefix) {
      nativeInputValueSetter.call(element, element.value + char);
      element.dispatchEvent(new Event('input', { bubbles: true }));
      await new Promise(r => setTimeout(r, 20 + Math.random() * 30));
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
      throw new Error('Could not find Perplexity input field');
    }

    // Focus and set value with human-like delays
    await humanDelay();
    input.focus();
    await humanDelay();
    await setInputValue(input, prompt);

    // Delay before clicking send
    await actionDelay();

    // Click send button or press Enter
    const sendBtn = document.querySelector(SELECTORS.sendButton);
    if (sendBtn && !sendBtn.disabled) {
      sendBtn.click();
    } else {
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
    await new Promise(r => setTimeout(r, 2000));

    return new Promise((resolve, reject) => {
      const checkComplete = () => {
        if (Date.now() - startTime > timeout) {
          reject(new Error('Response timeout'));
          return;
        }

        // Check if still loading
        const loading = document.querySelector(SELECTORS.loading);
        if (loading && loading.offsetParent !== null) {
          setTimeout(checkComplete, 500);
          return;
        }

        // Get the answer content
        const answers = document.querySelectorAll(SELECTORS.messageContainer);
        if (answers.length > 0) {
          const lastAnswer = answers[answers.length - 1];
          let content = lastAnswer.textContent || lastAnswer.innerText;

          // Try to get sources too
          const sourcesEl = document.querySelector(SELECTORS.sources);
          if (sourcesEl) {
            const sources = sourcesEl.textContent || sourcesEl.innerText;
            if (sources) {
              content += '\n\n---\nSources:\n' + sources;
            }
          }

          if (content && content.trim()) {
            resolve(content.trim());
            return;
          }
        }

        // No response yet, keep waiting
        setTimeout(checkComplete, 500);
      };

      setTimeout(checkComplete, 3000);
    });
  }

  // Wait for URL to update
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
          resolve(null);
          return;
        }

        setTimeout(checkUrl, 500);
      };

      setTimeout(checkUrl, 1000);
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
