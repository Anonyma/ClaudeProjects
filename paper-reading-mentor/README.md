# Paper Reading Mentor

A learning app that teaches critical paper reading skills through AI-guided sessions. Think of it as having a senior researcher sitting next to you, walking you through each paper section-by-section.

## Features

- **Guided Reading Path** - 8-step expert reading strategy (Abstract -> Figures -> Methods -> Results, etc.)
- **AI Mentor** - Dr. Reading guides you with Socratic questioning
- **PDF Viewer** - Built-in PDF rendering with zoom and navigation
- **Cornell Notes** - Organized note-taking linked to each reading step
- **Paper Library** - Import from arXiv, Semantic Scholar, URL, or local files

## AI Provider Options

| Provider | Cost | Quality | Setup |
|----------|------|---------|-------|
| **Ollama (default)** | Free | Good | `ollama run llama3.1:8b-instruct-q4_K_M` |
| **Gemini Flash** | ~$0.01/100 papers | Good | API key from Google AI Studio |
| **Claude Haiku** | ~$0.05/paper | Best | API key from Anthropic Console |

## Quick Start

1. Open `index.html` in your browser
2. Click "+ Import" to add a paper
3. Start reading with AI guidance

## Paper Import Methods

- **Upload** - Drag and drop local PDF files
- **URL** - Any direct PDF link
- **arXiv** - Enter ID like `2301.07041`
- **Search** - Search Semantic Scholar by title/topic

## Tech Stack

- React 18 (UMD)
- PDF.js for PDF rendering
- Tailwind CSS
- IndexedDB for PDF storage
- LocalStorage for settings and progress

## Data Privacy

All data stays in your browser:
- PDFs stored in IndexedDB
- Settings and notes in LocalStorage
- API keys never leave your browser (except to the actual API)

## Development

This is a single-file React app. Just edit `index.html` and refresh.

To serve locally:
```bash
cd paper-reading-mentor
python3 -m http.server 8080
```

## License

MIT
