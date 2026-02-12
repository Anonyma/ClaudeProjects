## Session: 2026-02-12 ~13:00-20:00 CET
**Status:** in-progress (21/24 deep dives generating, 3 need retry)

### Done:
- Added 695 sources to 8 NotebookLM notebooks via Selenium on CandyPop (0 failures)
- Created 4 missing notebooks (Japanese History, Neuroscience, Microbiome, Senolytics) automatically
- Fixed source-adding script: was targeting wrong textarea (search bar vs URL input)
- Kicked off 21/24 deep dive audio overviews (Long format, extensive prompts)
- Updated Linear project with full status table
- Created Linear issue Z-13 for Japanese History retry
- Updated CONTINUE.md with comprehensive continuation instructions
- Committed and deployed HTGAA Week 2 study guide to Netlify

### Issues:
- 3 Japanese History deep dives failed: notebook auto-created as "The Cambridge History of Japan: The Nineteenth Century" but script searched for "Japanese History"
- Google session expires when Selenium driver.quit() runs — workaround: use window.close() instead
- Need to re-login via VNC each time session expires

### Next:
1. Retry 3 Japanese History deep dives (fix notebook name in script, Z-13)
2. Wait for 21 deep dives to finish generating on NLM's side
3. Download all 24 audio files
4. Transcribe with faster-whisper on CandyPop
5. Generate study materials from transcripts
6. Update study hub and deploy

### Files Changed:
- `_scratch/add_sources_to_nlm.py` — fixed textarea targeting
- `_scratch/batch_deep_dives.py` — new batch deep dive script
- `_scratch/create_and_add_remaining.py` — script for 4 missing notebooks
- `_scratch/probe_audio_ui.py`, `probe_audio_step2.py` — UI probing scripts
- `notebooklm_scrape/batch-2026-02/CONTINUE.md` — updated status & instructions
- `htgaa-biobootcamp/week2/` — committed and pushed to GitHub/Netlify

### Access:
- **Study hub:** https://notebooklmstudyhub.netlify.app/
- **HTGAA Week 2:** https://htgaa-biobootcamp.netlify.app/week2/index.html
- **Linear project:** https://linear.app/z-z-z/project/notebooklm-study-hub-076cf8c1a53e
- **Monitor deep dives:** `ssh CandyPop 'tail -f /tmp/nlm_deepdives.log'`
- **Progress files:** `CandyPop:~/Projects/notebooklm/batch-2026-02/*.json`
