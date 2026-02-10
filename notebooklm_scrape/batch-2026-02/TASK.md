# NotebookLM Batch Content Generation - February 2026

## Mission

Generate comprehensive NotebookLM study content for 8 new topics. Each topic needs:
1. **50+ curated sources** added to a NotebookLM notebook
2. **3+ deep dive audio overviews** covering different angles
3. **Transcription, summaries, and quizzes** generated from each audio
4. **Architecture topic**: also generate a full study hub article with images

## Topic Configuration

All topic details are in `topics.json`. Read it first.

## Progress Tracking

**CRITICAL: Report status at every phase transition using report-status.**

```bash
# Starting a topic's source research
report-status --name "nlm-{topic_id}" --project "notebooklm-batch" running "Phase 1: Researching sources for {topic_name}"

# Source research complete
report-status --name "nlm-{topic_id}" --project "notebooklm-batch" running "Phase 1 complete: {N} sources found. Starting Phase 2."

# Blocked (e.g., login needed)
report-status --name "nlm-{topic_id}" --project "notebooklm-batch" blocked "Playwright login expired. Run setup_login.sh on CandyPop"

# Error
report-status --name "nlm-{topic_id}" --project "notebooklm-batch" error "Audio generation failed: {reason}"

# Topic complete
report-status --name "nlm-{topic_id}" --project "notebooklm-batch" completed "All phases done: {N} sources, {N} deep dives, {N} articles"
```

Also update `progress.json` after each step (see format below).

## Phase 1: Source Research (ALL TOPICS - No NotebookLM needed)

For each topic in priority order:

1. **Read topic config** from `topics.json`
2. **Research sources** using web search:
   - Find 50+ high-quality URLs (papers, articles, Wikipedia, reviews)
   - Prioritize: peer-reviewed papers > review articles > quality journalism > Wikipedia
   - Follow the `source_guidance` in the topic config
   - For biotech/science topics: PubMed, Nature, Science, Cell
   - For history/humanities: JSTOR, academic press, quality magazines (Aeon, The Atlantic)
3. **Save source list** to `sources/{topic_id}_sources.md`:
   ```markdown
   # Sources for {Topic Name}

   ## Core Sources (must include)
   1. [Title](URL) - Type: {paper|review|article|wikipedia} - Why: {brief reason}
   2. ...

   ## Supporting Sources
   1. ...

   ## Total: {N} sources
   ```
4. **Update progress.json**
5. **Report status**

**IMPORTANT**: Do all 8 topics' source research before moving to Phase 2. This phase doesn't need NotebookLM access and can proceed even if login is expired.

## Phase 2: NotebookLM Notebook Creation (Needs Playwright)

**Before starting**: Test Playwright login by navigating to NotebookLM. If redirected to Google login, report `blocked` status and stop.

For each topic:
1. **Create a new notebook** on NotebookLM with the title from `topics.json`
2. **Add sources**: paste URLs and text from the source lists
3. **Verify source count** reaches 50+
4. **Record notebook_id** in progress.json

### If Login Is Expired:
```bash
report-status --name "nlm-batch" --project "notebooklm-batch" blocked "Playwright login expired. Need user to run: cd ~/Projects/notebooklm && DISPLAY=:1 bash setup_login.sh"
```
Then STOP and wait. Do NOT retry repeatedly.

## Phase 3: Audio Deep Dive Generation (Rate-Limited)

**Daily quota: ~3 audio generations per day on NotebookLM.**

For each topic:
1. **Generate deep dives** using the prompts from `topics.json`
2. **Use generate_deep_dive.py**:
   ```bash
   cd ~/Projects/notebooklm
   python3.12 generate_deep_dive.py --notebook "{notebook_name}" --prompt "{prompt}" --length long
   ```
3. **Download audio** to `~/Projects/notebooklm/notebooklm-audio/`
4. **Report progress** after each generation

### Rate Limit Strategy:
- Generate 3 per day maximum
- Prioritize: one deep dive per topic before second passes
- Expected timeline: ~8-10 days for all 24 deep dives

## Phase 4: Processing Pipeline

After audio is downloaded:

```bash
cd ~/Projects/notebooklm

# Transcribe new audio
python3.12 transcribe_optimized.py

# Upload transcripts
python3.12 upload_transcripts.py

# Generate study materials
python3.12 generate_study_materials.py

# Export to markdown
python3.12 export_study_materials.py
```

## Phase 5: Architecture Article (Special Task)

For the Architecture topic specifically, generate a full study hub article:

1. **Research images**: Find 10-15 high-quality images from Wikipedia Commons / CC-licensed sources
   - Zaha Hadid buildings (Heydar Aliyev Center, MAXXI, Guangzhou Opera House)
   - BIG projects (CopenHill, Vancouver House, The Spiral)
   - Mass timber buildings (Mjostårnet, Brock Commons)
   - 3D-printed structures (ICON houses, Apis Cor)
   - Biomimetic architecture (ICD/ITKE Stuttgart pavilions)
   - Parametric facades (Al Bahar Towers)

2. **Generate article** (3000-5000 words) in the study hub lesson JSON format:
   ```json
   {
     "id": "architecture-beyond-postmodernism",
     "title": "Architecture Beyond Postmodernism",
     "subtitle": "From Deconstructivism to AI-Assisted Design",
     "category": "Architecture",
     "content": "...(HTML with embedded images)...",
     "entities": [...],
     "quiz": [...],
     "timeline": {...}
   }
   ```

3. **Save to**: `~/Projects/notebooklm-study-hub/generated/Architecture_Beyond_Postmodernism.json`

## Progress File Format

Maintain `progress.json`:

```json
{
  "batch_id": "2026-02-batch",
  "started_at": "2026-02-11T...",
  "last_updated": "2026-02-11T...",
  "overall_status": "in_progress",
  "topics": {
    "bbb-crossing": {
      "phase": "source_research",
      "phase_status": "in_progress",
      "sources_found": 0,
      "sources_target": 50,
      "notebook_created": false,
      "notebook_id": null,
      "deep_dives_generated": 0,
      "deep_dives_target": 3,
      "transcribed": false,
      "articles_generated": false,
      "errors": [],
      "last_updated": "2026-02-11T..."
    }
  }
}
```

## Error Handling

- **Login expired**: Report `blocked`, stop, wait for user
- **Audio generation failed**: Report `error`, log details, try next topic
- **Rate limit hit**: Report status, schedule retry for tomorrow
- **Script crash**: Report `error` with stack trace
- **Source research hitting dead ends**: Report status, note gaps, continue with available sources

## File Locations on CandyPop

- **This task**: `~/Projects/notebooklm/batch-2026-02/`
- **Topic configs**: `~/Projects/notebooklm/batch-2026-02/topics.json`
- **Source lists**: `~/Projects/notebooklm/batch-2026-02/sources/`
- **Progress**: `~/Projects/notebooklm/batch-2026-02/progress.json`
- **Audio files**: `~/Projects/notebooklm/notebooklm-audio/`
- **Study hub**: `~/Projects/notebooklm-study-hub/`
- **Deep dive script**: `~/Projects/notebooklm/generate_deep_dive.py`

## Completion Criteria

A topic is DONE when:
- [x] 50+ sources researched and listed
- [x] Notebook created on NotebookLM with sources added
- [x] 3+ deep dive audios generated and downloaded
- [x] All audios transcribed
- [x] Summaries and quizzes generated
- [x] (Architecture only) Study hub article with images generated

The batch is DONE when all 8 topics are complete.

Report final status:
```bash
report-status --name "nlm-batch" --project "notebooklm-batch" completed "All 8 topics complete: {total_sources} sources, {total_dives} deep dives, {total_articles} articles"
```
