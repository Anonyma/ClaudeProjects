# LLM Council

## Purpose
Send the same query to multiple LLMs at once, compare their responses side-by-side, and synthesize a final analysis highlighting agreements, disagreements, and conclusions.

## Quick Start
```bash
cd /Users/z/Desktop/PersonalProjects/ClaudeProjects/llm-council
python3 -m http.server 8880
# Open http://localhost:8880/index.html
```

## Use Your Subscriptions (No API Credits!)
Instead of paying for API credits, use your existing subscriptions (ChatGPT Plus, Claude Max, Gemini Advanced, Perplexity Pro):

```bash
# 1. Install dependencies
cd server
pip install -r requirements.txt
playwright install chromium

# 2. Log into each provider (opens browser for manual login)
python login.py --provider chatgpt   # Log into ChatGPT Plus
python login.py --provider claude    # Log into Claude Max
python login.py --provider gemini    # Log into Gemini Advanced
python login.py --provider perplexity # Log into Perplexity Pro
# Or all at once: python login.py --all

# 3. Start the Playwright server
python server.py  # Runs on http://localhost:8881

# 4. Open the web app - it will auto-detect the server
cd .. && python3 -m http.server 8880
# Open http://localhost:8880/index.html
```

The web app will show "Server: X providers" when connected, and you can toggle "Web UI (Server)" mode for each provider.

## Features
- **Multi-provider support**: Query multiple AI providers simultaneously
- **Model selection**: Choose exact model for each provider
- **Feature toggles**: Enable web search, deep research, extended thinking per provider
- **Side-by-side comparison**: View all responses in a grid layout
- **Synthesis**: Send all outputs to a final AI for comprehensive analysis
- **API key management**: Stored securely in localStorage
- **Keyboard shortcuts**: Cmd/Ctrl+Enter to submit

## Supported Providers & Models

### OpenAI
- GPT-4o, GPT-4o Mini, GPT-4 Turbo
- o1, o1 Mini, o3 Mini (reasoning models)
- Features: Web Search

### Anthropic (Claude)
- Claude Opus 4.5, Claude Sonnet 4, Claude 3.5 Haiku
- Features: Extended Thinking

### Google (Gemini)
- Gemini 2.0 Flash, Gemini 2.0 Flash Thinking
- Gemini 1.5 Pro, Gemini 1.5 Flash
- Features: Web Search (Grounding)

### Perplexity
- Sonar Pro, Sonar, Sonar Reasoning Pro/Regular
- Sonar Deep Research
- Features: Web Search (always on), Deep Research

### Local (Ollama)
- Llama 3.3 70B, Llama 3.2, Mistral, Mixtral
- Qwen 2.5 72B, DeepSeek R1 70B, Phi-4
- Custom model support
- Configurable endpoint (default: http://localhost:11434)

## Synthesis Feature
After receiving responses, click "Synthesize" to generate:
- Summary of each response
- Points of agreement across all AIs
- Points of disagreement/contradictions
- Unique insights from each AI
- Accuracy assessment (flagging conflicting facts)
- Final comprehensive conclusion

Choose which AI performs the synthesis: Claude, GPT-4o, or Gemini.

## Architecture
Single-page web app (`index.html`) with:
- All HTML, CSS, and JavaScript in one file
- API keys stored in browser localStorage
- Direct API calls to each provider (API mode)
- Playwright server for subscription-based access (Web UI mode)
- Parallel request execution

### Playwright Server (`server/`)
- `login.py` - Opens browser for manual login, saves session to `~/.llm-council/profiles/`
- `server.py` - HTTP server (port 8881) that uses saved sessions to query providers headlessly
- Sessions persist until cleared or expired
- No credentials stored - only browser cookies/localStorage

## Configuration
Click the 🔑 key icon to configure API keys for each provider.

## Notes
- Anthropic requires `anthropic-dangerous-direct-browser-access` header for browser calls
- Ollama must have CORS enabled or be accessed from localhost
- API usage incurs costs based on each provider's pricing
- Perplexity always performs web search (it's their core feature)
