# LLM Council - Playwright Server

Use your ChatGPT Plus, Claude Max, Gemini Advanced, and Perplexity Pro subscriptions instead of API credits.

## Setup

### 1. Install Dependencies

```bash
cd server
pip install -r requirements.txt
playwright install chromium
```

### 2. Log Into Providers

Run the login script for each provider you want to use. A browser will open - log in manually, then close it:

```bash
# Log into each provider one by one
python login.py --provider chatgpt
python login.py --provider claude
python login.py --provider gemini
python login.py --provider perplexity

# Or log into all at once
python login.py --all

# Check which sessions are saved
python login.py --list
```

Sessions are saved to `~/.llm-council/profiles/` and persist until you clear them or they expire.

### 3. Start the Server

```bash
python server.py
# Server runs on http://localhost:8881
```

## Usage

### API Endpoints

**Check health:**
```bash
curl http://localhost:8881/health
```

**List available providers:**
```bash
curl http://localhost:8881/providers
```

**Query a provider:**
```bash
curl -X POST http://localhost:8881/query \
  -H "Content-Type: application/json" \
  -d '{"provider": "chatgpt", "prompt": "Hello!"}'
```

### From LLM Council Web App

The web app can call this server when you select "Web UI (Subscription)" mode for a provider.

## Managing Sessions

```bash
# List all sessions
python login.py --list

# Clear a specific session (forces re-login)
python login.py --clear chatgpt

# Clear all sessions
python login.py --clear all
```

## Troubleshooting

### Session Expired
If queries fail with auth errors, clear the session and log in again:
```bash
python login.py --clear chatgpt
python login.py --provider chatgpt
```

### Provider UI Changed
The server uses CSS selectors to find input fields and responses. If a provider updates their UI, the selectors in `server.py` may need updating.

### Running Headless
After initial login, the server runs headless (no visible browser). If you need to debug, edit `server.py` and change `headless=True` to `headless=False`.
