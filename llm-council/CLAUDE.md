# LLM Council

## Purpose
Send the same query to multiple LLMs at once and compare their responses side-by-side.

## Quick Start
```bash
cd /Users/z/Desktop/PersonalProjects/ClaudeProjects/llm-council
python3 -m http.server 8880
# Open http://localhost:8880/index.html
```

## Features
- Text input for queries/prompts
- Toggle selection for multiple LLM providers
- Side-by-side response comparison
- API key configuration (stored in localStorage)
- Copy individual responses
- Clear all responses

## Supported Providers
- OpenAI (GPT-4o, GPT-4o-mini)
- Anthropic (Claude Sonnet 4, Claude Haiku)
- Google (Gemini 2.0 Flash)

## Architecture
Single-page web app with:
- `index.html` - All HTML, CSS, and JavaScript in one file
- API keys stored in browser localStorage
- Direct API calls to each provider (requires CORS-friendly endpoints or browser extension)

## Configuration
Click the gear icon to configure API keys for each provider. Keys are stored locally and never transmitted except to their respective API endpoints.

## Notes
- Some providers may require CORS browser extensions for local development
- API usage incurs costs based on each provider's pricing
