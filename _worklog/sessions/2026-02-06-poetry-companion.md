# Poetry Reading Companion - Flight Edition

## Session: 2026-02-06
**Status:** completed

### Done:
- Built single-file Poetry Reading Companion web app (216KB, fully self-contained)
- 24 curated poems across 6 categories (Metaphysical+Cosmic, Abyss but Intelligent, Dream Logic+Uncanny, Precision-Built, Science/Modernity, Wit+Depth)
- Rich educational content per poem: Reflect prompts, About the Poem, About the Author, Historical Context, Connections
- All poems as paste-in areas (copyright-safe) with source URLs for quick copy-paste
- 10 bilingual poems with dual paste areas (original language + English translation)
- Dark/light theme toggle, font size controls (S/M/L), Georgia serif typography
- Reading progress + personal notes saved to localStorage
- Pre-flight preparation banner showing paste progress
- Hash-based routing for direct poem links
- Fixed CSS display toggle bug (style.display='' vs explicit 'block')
- Deployed to Netlify for mobile/tablet access

### Issues:
- Content filtering API 400 errors when generating poem text — solved by making all poems paste-in
- CSS display bug: `style.display = ''` falls back to CSS rules, must use explicit values like `'block'`
- Linear MCP token expired — could not create Linear project/issues

### Files:
- `/Users/z/Desktop/PersonalProjects/ClaudeProjects/_scratch/poetry-companion/index.html` — the full app

### Access:
- **Live:** https://poetry-companion-flight.netlify.app
- **Local:** http://localhost:8877/poetry-companion/index.html (if server running)
- **Netlify site ID:** e0c06902-e47e-45bb-ba61-7a842cd2dabc

### Notes:
- localStorage is per-domain, so poems pasted on localhost won't appear on Netlify version (and vice versa)
- Poem source file: `/Users/z/Desktop/PersonalProjects/ClaudeProjects/filesforAI/First batch of recommended poems. - 6feb26.md`
- Poems NOT in source file (need to find separately): Rilke Duino Elegies VII & VIII, Trakl's Grodek, Valery's Le Cimetiere marin, Pizarnik's Stone of Madness
