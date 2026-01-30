# LLM Council

Query multiple LLMs simultaneously and synthesize their responses into a comprehensive analysis.

![LLM Council Screenshot](docs/screenshot.png)

## Features

- **Multi-provider support**: ChatGPT, Claude, Gemini, Perplexity, Ollama (local)
- **Exact model selection**: Choose specific models (GPT-4o, o1, Claude Opus, Gemini 2.0 Flash, etc.)
- **Feature toggles**: Web search, deep research, extended thinking per provider
- **Web UI Mode**: Use your paid subscriptions instead of API credits (via browser extension)
- **Incognito mode**: Don't store queries in provider history (where supported)
- **Synthesis**: Send all responses to a final AI for comprehensive analysis
  - Agreements & disagreements
  - Unique insights
  - Accuracy assessment
  - Final conclusion

## Quick Start

```bash
cd llm-council
python3 -m http.server 8880
# Open http://localhost:8880
```

## Using API Keys

1. Click the 🔑 key icon
2. Enter your API keys for each provider
3. Enable providers and select models
4. Send your query

## Using Your Subscriptions (Web UI Mode)

To use your ChatGPT Plus, Claude Max, or Gemini Advanced subscription instead of API credits:

### 1. Install the Bridge Extension

1. Open Chrome and go to `chrome://extensions`
2. Enable "Developer mode"
3. Click "Load unpacked"
4. Select the `extension` folder from this project

### 2. Configure the Extension

1. Copy the Extension ID from `chrome://extensions`
2. In LLM Council, click 🔑 and paste the ID
3. For each provider, click "🌐 Web UI (Subscription)" instead of "🔑 API Key"

### 3. Usage Notes

- The extension opens background tabs for each provider
- You must be logged into each service in Chrome
- Web UI mode is slower than API but uses your subscription
- Note: Web interfaces change frequently; selectors may need updates

## Providers & Models

| Provider | Models | Features |
|----------|--------|----------|
| **ChatGPT** | GPT-4o, GPT-4o Mini, o1, o1 Mini, o3 Mini | Web Search |
| **Claude** | Opus 4.5, Sonnet 4, Haiku 3.5 | Extended Thinking |
| **Gemini** | 2.0 Flash, 2.0 Flash Thinking, 1.5 Pro | Web Search (Grounding) |
| **Perplexity** | Sonar Pro, Sonar Reasoning, Deep Research | Web Search (always on), Deep Research |
| **Ollama** | Llama 3.3, Mistral, Mixtral, Qwen, DeepSeek, custom | Local only |

## Synthesis

After receiving responses, click "✨ Synthesize" to generate:

- **Summary of Each Response** - Key points from each AI
- **Points of Agreement** - Where all AIs aligned
- **Points of Disagreement** - Contradictions and different perspectives
- **Unique Insights** - Valuable points only one AI mentioned
- **Accuracy Assessment** - Conflicting facts to verify
- **Final Synthesis** - Comprehensive conclusion preserving all nuances

## Architecture

```
llm-council/
├── index.html          # Main web app (single file)
├── extension/          # Chrome extension for Web UI mode
│   ├── manifest.json
│   ├── background.js
│   └── content-scripts/
│       ├── chatgpt.js
│       ├── claude.js
│       ├── gemini.js
│       └── perplexity.js
└── README.md
```

## Known Limitations

- **Web UI Mode**: Content scripts may break when providers update their UIs
- **Anthropic CORS**: Requires the `anthropic-dangerous-direct-browser-access` header
- **Ollama CORS**: Ollama server must allow localhost connections
- **Perplexity**: Always performs web search (it's their core feature)

## Privacy

- API keys are stored in browser localStorage only
- Keys are never sent anywhere except to their respective provider APIs
- Incognito mode prevents query storage where providers support it

## License

MIT
