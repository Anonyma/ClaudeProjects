# Reading Dashboard Setup

A beautiful, mobile-friendly dashboard to track your reading progress across NotebookLM sources.

## Quick Start (Local Only)

1. Open `index.html` in a browser
2. Click "Skip for now" when prompted for Supabase
3. Your reading status will be saved in browser localStorage

## Full Setup with Supabase (Cross-Device Sync)

### 1. Create a Supabase Project

1. Go to [supabase.com](https://supabase.com) and sign up (free)
2. Create a new project (any name, choose closest region)
3. Wait for the project to initialize

### 2. Create the Database Table

Go to **SQL Editor** in your Supabase dashboard and run:

```sql
-- Create reading status table
CREATE TABLE reading_status (
    id BIGSERIAL PRIMARY KEY,
    article_id TEXT UNIQUE NOT NULL,
    status TEXT NOT NULL CHECK (status IN ('unread', 'in-progress', 'read')),
    updated_at TIMESTAMPTZ DEFAULT NOW()
);

-- Create index for faster lookups
CREATE INDEX idx_reading_status_article ON reading_status(article_id);

-- Enable Row Level Security (optional but recommended)
ALTER TABLE reading_status ENABLE ROW LEVEL SECURITY;

-- Create a policy that allows all operations (for personal use)
CREATE POLICY "Allow all" ON reading_status FOR ALL USING (true) WITH CHECK (true);
```

### 3. Get Your API Credentials

1. Go to **Settings** > **API** in your Supabase dashboard
2. Copy the **Project URL** (looks like `https://xxxxx.supabase.co`)
3. Copy the **anon/public** key (the long JWT string)

### 4. Connect the Dashboard

1. Open `index.html` in a browser
2. Paste your Project URL and anon key
3. Click "Connect & Sync"

Your reading status will now sync across all devices!

## Running on Mobile

### Option A: Local Network (Same WiFi)

1. Run a local server:
   ```bash
   cd reading-dashboard
   python3 -m http.server 8000
   ```
2. Find your computer's local IP: `ifconfig | grep inet`
3. On your phone, visit: `http://YOUR_IP:8000`
4. Add to home screen for app-like experience

### Option B: Deploy to the Web (Free)

**GitHub Pages:**
1. Push to a GitHub repo
2. Go to Settings > Pages > Deploy from main branch
3. Access at `https://yourusername.github.io/repo-name`

**Netlify:**
1. Drag the `reading-dashboard` folder to [app.netlify.com/drop](https://app.netlify.com/drop)
2. Get an instant URL

**Vercel:**
1. Install: `npm i -g vercel`
2. Run: `vercel` in the dashboard folder
3. Follow prompts

## Updating Your Articles

When you scrape new articles from NotebookLM:

1. Replace `data/sources.json` and `data/notebooks.json` with your new files
2. Refresh the dashboard
3. New articles will appear, existing reading status preserved

## Storage Options Comparison

| Option | Sync Across Devices | Offline Support | Setup Complexity |
|--------|---------------------|-----------------|------------------|
| LocalStorage | No | Yes | None |
| Supabase | Yes | Limited | Low |
| JSON file + iCloud | Yes (Apple devices) | Yes | Medium |
| Firebase | Yes | Yes | Medium |

## File Structure

```
reading-dashboard/
├── index.html      # Main dashboard
├── manifest.json   # PWA manifest
├── sw.js          # Service worker for offline
├── data/
│   ├── sources.json    # Article data
│   └── notebooks.json  # Notebook metadata
├── icon-192.png   # PWA icon (create your own)
└── icon-512.png   # PWA icon large
```

## Customization

### Change Theme Colors

Edit the CSS variables in `index.html`:

```css
:root {
    --bg-primary: #0f0f1a;
    --accent: #e94560;
    /* ... */
}
```

### Add More Metadata

If you scrape additional fields (reading time, word count, etc.), update the `loadArticles()` function to include them.
