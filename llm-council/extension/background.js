/**
 * LLM Council Bridge - Background Service Worker
 *
 * Coordinates communication between LLM Council web app and chat web interfaces.
 * Opens tabs for ChatGPT, Claude, Gemini and injects queries.
 */

// Track active tabs for each provider
const providerTabs = {
  chatgpt: null,
  claude: null,
  gemini: null,
  perplexity: null
};

// Pending queries waiting for responses
const pendingQueries = new Map();

// Provider URLs
const PROVIDER_URLS = {
  chatgpt: 'https://chatgpt.com/',
  claude: 'https://claude.ai/new',
  gemini: 'https://gemini.google.com/app',
  perplexity: 'https://www.perplexity.ai/'
};

// Listen for messages from content scripts
chrome.runtime.onMessage.addListener((message, sender, sendResponse) => {
  console.log('[LLM Council Bridge] Message received:', message.type);

  switch (message.type) {
    case 'CONTENT_SCRIPT_READY':
      handleContentScriptReady(message.provider, sender.tab.id);
      sendResponse({ success: true });
      break;

    case 'QUERY_RESPONSE':
      handleQueryResponse(message.queryId, message.response, message.error, message.conversationUrl);
      sendResponse({ success: true });
      break;

    case 'QUERY_STREAMING':
      handleStreamingUpdate(message.queryId, message.content);
      sendResponse({ success: true });
      break;

    default:
      sendResponse({ success: false, error: 'Unknown message type' });
  }

  return true; // Keep channel open for async response
});

// Listen for external connections from the LLM Council web app
chrome.runtime.onMessageExternal.addListener((message, sender, sendResponse) => {
  console.log('[LLM Council Bridge] External message:', message.type);

  switch (message.type) {
    case 'PING':
      sendResponse({ success: true, version: '1.0.0' });
      break;

    case 'QUERY':
      handleQuery(message)
        .then(result => sendResponse(result))
        .catch(err => sendResponse({ success: false, error: err.message }));
      return true; // Async response

    case 'GET_STATUS':
      sendResponse({
        success: true,
        tabs: {
          chatgpt: providerTabs.chatgpt !== null,
          claude: providerTabs.claude !== null,
          gemini: providerTabs.gemini !== null,
          perplexity: providerTabs.perplexity !== null
        }
      });
      break;

    case 'OPEN_PROVIDER':
      openProviderTab(message.provider)
        .then(() => sendResponse({ success: true }))
        .catch(err => sendResponse({ success: false, error: err.message }));
      return true;

    default:
      sendResponse({ success: false, error: 'Unknown message type' });
  }

  return true;
});

// Handle content script ready notification
function handleContentScriptReady(provider, tabId) {
  console.log(`[LLM Council Bridge] ${provider} content script ready on tab ${tabId}`);
  providerTabs[provider] = tabId;
}

// Handle incoming query from LLM Council
async function handleQuery(message) {
  const { provider, prompt, queryId, model, features } = message;

  // Ensure we have a tab for this provider
  if (!providerTabs[provider]) {
    await openProviderTab(provider);
    // Wait for content script to be ready
    await new Promise(resolve => setTimeout(resolve, 2000));
  }

  const tabId = providerTabs[provider];
  if (!tabId) {
    throw new Error(`No tab available for ${provider}`);
  }

  // Store pending query
  return new Promise((resolve, reject) => {
    const timeout = setTimeout(() => {
      pendingQueries.delete(queryId);
      reject(new Error('Query timed out after 120 seconds'));
    }, 120000);

    pendingQueries.set(queryId, {
      resolve: (response) => {
        clearTimeout(timeout);
        pendingQueries.delete(queryId);
        resolve(response);
      },
      reject: (error) => {
        clearTimeout(timeout);
        pendingQueries.delete(queryId);
        reject(error);
      }
    });

    // Send query to content script
    chrome.tabs.sendMessage(tabId, {
      type: 'SEND_QUERY',
      queryId,
      prompt,
      model,
      features
    }).catch(err => {
      pendingQueries.get(queryId)?.reject(err);
    });
  });
}

// Handle query response from content script
function handleQueryResponse(queryId, response, error, conversationUrl) {
  const pending = pendingQueries.get(queryId);
  if (!pending) {
    console.warn('[LLM Council Bridge] No pending query for:', queryId);
    return;
  }

  if (error) {
    pending.reject(new Error(error));
  } else {
    pending.resolve({ success: true, content: response, conversationUrl });
  }
}

// Handle streaming updates
function handleStreamingUpdate(queryId, content) {
  // For now, we'll wait for complete response
  // In future, could emit streaming events
  console.log(`[LLM Council Bridge] Streaming update for ${queryId}: ${content.length} chars`);
}

// Open a tab for a provider
async function openProviderTab(provider) {
  const url = PROVIDER_URLS[provider];
  if (!url) {
    throw new Error(`Unknown provider: ${provider}`);
  }

  // Check if we already have a tab
  if (providerTabs[provider]) {
    try {
      const tab = await chrome.tabs.get(providerTabs[provider]);
      if (tab) {
        await chrome.tabs.update(tab.id, { active: false });
        return tab;
      }
    } catch (e) {
      // Tab no longer exists
      providerTabs[provider] = null;
    }
  }

  // Create new tab (in background)
  const tab = await chrome.tabs.create({
    url,
    active: false
  });

  providerTabs[provider] = tab.id;
  return tab;
}

// Clean up closed tabs
chrome.tabs.onRemoved.addListener((tabId) => {
  for (const [provider, id] of Object.entries(providerTabs)) {
    if (id === tabId) {
      providerTabs[provider] = null;
      console.log(`[LLM Council Bridge] Tab closed for ${provider}`);
    }
  }
});

console.log('[LLM Council Bridge] Background service worker started');
