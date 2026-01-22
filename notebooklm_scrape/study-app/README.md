# NotebookLM Study Hub

A web app for studying with AI-generated summaries and quizzes from NotebookLM audio overviews.

## Features

- **Summaries**: Read AI-generated summaries with key takeaways and TL;DR sections
- **Quizzes**: Test your knowledge with interactive quizzes
- **Progress Tracking**: Your quiz scores are saved locally
- **Dark Theme**: Easy on the eyes for late-night study sessions

## Architecture

```
NotebookLM Audio Overviews
         ↓ (Whisper transcription)
     Transcripts
         ↓ (GPT-4o-mini)
  Summaries + Quizzes
         ↓
     Supabase DB
         ↓
    This Web App
```

## Tech Stack

- **Frontend**: Vanilla HTML/CSS/JS (single file)
- **Backend**: Supabase (PostgreSQL + REST API)
- **Hosting**: Netlify

## Local Development

Simply open `index.html` in a browser. The app connects to Supabase directly.

## Deployment

Deployed to Netlify. Push to main to auto-deploy.

## Database Tables

| Table | Purpose |
|-------|---------|
| `notebooklm_notebooks` | Notebook metadata |
| `notebooklm_assets` | Audio overviews, quizzes, flashcards |
| `notebooklm_transcripts` | Full text transcripts |
| `notebooklm_summaries` | AI summaries (standard + TLDR) |
| `notebooklm_quizzes` | Quiz questions with explanations |

## Related

- **Scraper/Pipeline**: See parent directory `notebooklm_scrape/` for data pipeline scripts
- **Supabase Project**: `ydwjzlikslebokuxzwco`
