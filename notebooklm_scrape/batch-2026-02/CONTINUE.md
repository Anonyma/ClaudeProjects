# NotebookLM Batch Feb 2026 - Continuation Instructions

## Current Status (as of 2026-02-12 20:00 CET)

### Sources: COMPLETE
All 695 sources added across 8 notebooks, 0 failures.

| Topic | Sources | Notebook Title on NLM |
|-------|---------|----------------------|
| bbb-crossing | 93 | The Blood-Brain Barrier: Structure, Function, and Therapeutics |
| crispr-precision | 83 | Biotech Breakthroughs 2023-2026: CRISPR, Gene Therapy & AI |
| japanese-history | 90 | The Cambridge History of Japan: The Nineteenth Century |
| neuroscience-rigorous | 81 | (search: "Neuroscience") |
| architecture-parametric | 92 | Postmodernism and Deconstruction in Architecture and Art Theory |
| microbiome | 82 | (search: "Microbiome") |
| senolytics | 78 | (search: "Senolytics") |
| philosophy-tech | 96 | (search: "Philosophy") |

### Deep Dives: 21/24 GENERATING
21 deep dives kicked off (Long format + extensive prompts). 3 Japanese History dives failed due to notebook name mismatch.

**Completed (21):** All 3 dives for BBB, CRISPR, Neuroscience, Architecture, Microbiome, Senolytics, Philosophy

**Failed (3):** japanese-history_dive1, dive2, dive3
- **Cause:** Script searched for "Japanese History" but notebook is titled "The Cambridge History of Japan: The Nineteenth Century"
- **Fix:** Change notebook search to "Cambridge History" in batch_deep_dives.py, remove failed entries from deep_dive_progress.json, re-run
- **Linear issue:** Z-13

### Study Hub Articles: DEPLOYED
8 articles (38,328 words) deployed to https://notebooklmstudyhub.netlify.app/

### What NEEDS DOING:
1. **Retry 3 Japanese History deep dives** (see Z-13)
2. **Wait for deep dives to finish generating** (NLM processes them server-side, ~20-45min each)
3. **Download audio files** from NotebookLM (24 total, each notebook's Audio Overview section)
4. **Transcribe with faster-whisper** on CandyPop
5. **Generate enhanced study materials** from transcripts
6. **Update study hub** with new content and deploy

## Critical Files

### On CandyPop (`ssh CandyPop`):
- **Source adding script**: `~/Projects/notebooklm/add_sources_to_nlm.py`
- **Deep dive batch script**: `~/Projects/notebooklm/batch_deep_dives.py`
- **Source files**: `~/Projects/notebooklm/batch-2026-02/sources/*.md` (8 files)
- **Source progress**: `~/Projects/notebooklm/batch-2026-02/source_add_progress.json` (all complete)
- **Deep dive progress**: `~/Projects/notebooklm/batch-2026-02/deep_dive_progress.json`
- **Firefox profile**: `~/Projects/notebooklm/.clean_firefox_profile`
- **Deep dive generator (old)**: `~/Projects/notebooklm/generate_deep_dive.py`
- **Study hub**: `~/Projects/notebooklm-study-hub/`
- **Generated articles**: `~/Projects/notebooklm-study-hub/generated/*.json`
- **Geckodriver**: `~/.local/bin/geckodriver`

### On Mac:
- **Script sources**: `/Users/z/Desktop/PersonalProjects/ClaudeProjects/_scratch/batch_deep_dives.py`
- **Batch config**: `/Users/z/Desktop/PersonalProjects/ClaudeProjects/notebooklm_scrape/batch-2026-02/`

## Automation Details

### Source Adding Script (`add_sources_to_nlm.py`)
- Selenium + system Firefox on VNC display :2
- Targets `textarea[aria-label="Enter URLs"]` (NOT the search textarea)
- Uses `send_keys` via `driver.switch_to.active_element` (NOT JS native setter)
- ~22s per URL, handles account chooser, creates notebooks
- Progress saved every 5 URLs to `source_add_progress.json`

### Deep Dive Script (`batch_deep_dives.py`)
- Clicks `button[aria-label="Customise Audio Overview"]`
- Sets length to "Long" via radio button
- Enters prompt in `textarea[aria="What should the AI hosts focus on in this episode?"]`
- Prepends "Be as extensive and thorough as possible..." to all prompts
- 3-minute delay between generations
- Progress tracked in `deep_dive_progress.json`

### Known Issues
- **Google session expires** when Selenium `driver.quit()` runs — scripts use `window.close()` instead
- **Profile lock files** persist after Firefox crashes — delete `.clean_firefox_profile/lock` and `.parentlock`
- **VNC display :2** must be running: `vncserver -list` to check, `vncserver :2` to start
- **Only ONE Firefox** can use the profile at a time

## Retrying Japanese History Deep Dives

```bash
# On CandyPop:
# 1. Edit deep_dive_progress.json - remove japanese-history entries from "failed" array
# 2. Edit batch_deep_dives.py - change notebook search from "Japanese History" to "Cambridge History"
#    (3 entries in DEEP_DIVES list)
# 3. Ensure Google login is fresh (VNC → Firefox → login → close)
# 4. Run:
cd ~/Projects/notebooklm
DISPLAY=:2 python3.12 -u batch_deep_dives.py 2>&1 | tee /tmp/nlm_deepdives_retry.log
```

## Deep Dive Prompts Reference

### BBB Crossing (3 dives) — DONE
1. Focused ultrasound + microbubbles: ExAblate, SonoCloud, Alzheimer's/cancer trials, safety
2. Receptor-mediated transcytosis: transferrin receptor, bispecific antibodies, Denali/Roche
3. Nanoparticles + emerging: LNPs, exosomes, CPPs, intranasal, gene therapy vectors

### CRISPR 2.0 (3 dives) — DONE
1. Base editing: CBEs/ABEs, sickle cell/FH trials, Beam Therapeutics, off-targets
2. Prime editing: pegRNA + RT mechanism, advantages, delivery, clinical path
3. Epigenetic editing: CRISPRi/CRISPRa, gene modulation without cuts, therapeutic apps

### Japanese History (3 dives) — NEEDS RETRY
1. Feudal → modern: Tokugawa fall, Meiji Restoration, industrialization
2. Cultural traditions: bushido, tea ceremony, ukiyo-e, kabuki, Zen Buddhism
3. 20th century: militarism, WWII, occupation, economic miracle

### Neuroscience (3 dives) — DONE
1. Consciousness theories: IIT, Global Workspace, Higher-Order, Predictive Processing
2. Neural correlates: brain imaging, PFC/thalamus, anesthesia, disorders
3. Perception: reality construction, multisensory integration, attention, illusions

### Architecture (3 dives) — DONE
1. Parametric design: Zaha Hadid, Schumacher, algorithmic tools, landmarks
2. Sustainable/biophilic: mass timber, passive house, living buildings, climate
3. Philosophy/theory: postmodernism critique, digital tectonics, materials, future

### Microbiome (3 dives) — DONE
1. Gut-brain axis: vagus nerve, SCFAs, tryptophan, enteric NS, mood/cognition
2. Disease: IBD, obesity, ASD, depression, Parkinson's, dysbiosis evidence
3. Therapeutics: probiotics, prebiotics, FMT, diet, engineered bacteria, trials

### Senolytics (3 dives) — DONE
1. Senescence biology: triggers, SASP, accumulation, role in aging
2. Senolytic drugs: D+Q, fisetin, navitoclax, Unity/Oisin, human trials
3. Longevity context: rapamycin, NAD+, CR, animal→human translation

### Philosophy of Tech (3 dives) — DONE
1. Foundations: Heidegger, McLuhan, Ellul, predictions of current situation
2. AI ethics: alignment problem, value alignment, Bostrom/Russell, governance
3. Practical ethics: algorithmic bias, surveillance capitalism, privacy, digital labor

## After Deep Dives Are Ready

### Download audio:
Audio files appear in each notebook's Audio Overview section once generation completes. They can be downloaded via the UI or potentially scraped with Selenium.

### Transcribe:
```bash
# On CandyPop with faster-whisper:
cd ~/Projects/notebooklm
python3.12 transcribe_optimized.py  # or use faster-whisper directly
```

### Generate study materials:
```bash
python3.12 generate_study_materials.py
python3.12 export_study_materials.py
```

### Deploy:
```bash
cd ~/Projects/notebooklm-study-hub
git add -A && git commit -m "Add new study materials" && git push
```

## VNC Access
```bash
ssh CandyPop 'vncserver -list'          # Check
ssh CandyPop 'vncserver :2'             # Start if needed
ssh -L 6080:localhost:6080 CandyPop -N & # Tunnel for noVNC
# Access: http://localhost:6080/vnc.html (password: candypop)
```
