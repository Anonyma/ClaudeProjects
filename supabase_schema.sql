-- ============================================================
-- MULTI-PROJECT SCHEMA FOR CLAUDE PROJECTS
-- ============================================================
-- Designed to support multiple projects under ClaudeProjects/
-- including NotebookLM content, reading-dashboard, and future projects
-- ============================================================

-- Enable UUID extension
CREATE EXTENSION IF NOT EXISTS "uuid-ossp";

-- ============================================================
-- PROJECTS TABLE (top-level, shared across all projects)
-- ============================================================
CREATE TABLE IF NOT EXISTS projects (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    name TEXT NOT NULL UNIQUE,
    local_path TEXT,
    description TEXT,
    created_at TIMESTAMPTZ DEFAULT NOW(),
    updated_at TIMESTAMPTZ DEFAULT NOW()
);

-- ============================================================
-- NOTEBOOKLM: NOTEBOOKS
-- ============================================================
CREATE TABLE IF NOT EXISTS notebooklm_notebooks (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    project_id UUID REFERENCES projects(id) ON DELETE CASCADE,
    notebook_id TEXT NOT NULL UNIQUE,  -- NotebookLM's ID (from URL)
    title TEXT NOT NULL,
    description TEXT,
    topic_tags TEXT[],  -- Array of tags
    source_count INTEGER,
    created_display TEXT,  -- e.g., "19 Jan 2026"
    first_seen_at TIMESTAMPTZ,
    created_at TIMESTAMPTZ DEFAULT NOW(),
    updated_at TIMESTAMPTZ DEFAULT NOW()
);

-- ============================================================
-- NOTEBOOKLM: ASSETS (audio, quizzes, flashcards, etc.)
-- ============================================================
CREATE TABLE IF NOT EXISTS notebooklm_assets (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    notebook_id TEXT REFERENCES notebooklm_notebooks(notebook_id) ON DELETE CASCADE,
    asset_title TEXT NOT NULL,
    asset_type TEXT NOT NULL,  -- 'audio', 'quiz', 'flashcards', 'infographic', 'mindmap'
    description TEXT,
    topics_inferred TEXT[],
    source_count_display TEXT,
    created_display TEXT,
    first_seen_at TIMESTAMPTZ,
    created_at TIMESTAMPTZ DEFAULT NOW(),

    -- Unique constraint to prevent duplicates
    UNIQUE(notebook_id, asset_title, asset_type)
);

-- ============================================================
-- NOTEBOOKLM: TRANSCRIPTS (text content from audio overviews)
-- ============================================================
CREATE TABLE IF NOT EXISTS notebooklm_transcripts (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    asset_id UUID REFERENCES notebooklm_assets(id) ON DELETE CASCADE UNIQUE,
    transcript_text TEXT NOT NULL,
    word_count INTEGER,
    source TEXT DEFAULT 'notebooklm_pdf',  -- 'notebooklm_pdf', 'whisper', 'manual'
    created_at TIMESTAMPTZ DEFAULT NOW()
);

-- ============================================================
-- NOTEBOOKLM: SUMMARIES (AI-generated summaries)
-- ============================================================
CREATE TABLE IF NOT EXISTS notebooklm_summaries (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    asset_id UUID REFERENCES notebooklm_assets(id) ON DELETE CASCADE,
    summary_type TEXT NOT NULL DEFAULT 'standard',  -- 'standard', 'key_points', 'tldr'
    summary_text TEXT NOT NULL,
    key_points JSONB,  -- Array of key takeaways
    generated_at TIMESTAMPTZ DEFAULT NOW(),
    model_used TEXT,

    UNIQUE(asset_id, summary_type)
);

-- ============================================================
-- NOTEBOOKLM: QUIZZES (AI-generated quiz questions)
-- ============================================================
CREATE TABLE IF NOT EXISTS notebooklm_quizzes (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    asset_id UUID REFERENCES notebooklm_assets(id) ON DELETE CASCADE,
    quiz_type TEXT NOT NULL DEFAULT 'recall',  -- 'recall', 'comprehension', 'application'
    questions JSONB NOT NULL,  -- Array of {question, options, correct_answer, explanation}
    difficulty TEXT DEFAULT 'medium',  -- 'easy', 'medium', 'hard'
    question_count INTEGER,
    generated_at TIMESTAMPTZ DEFAULT NOW(),
    model_used TEXT,

    UNIQUE(asset_id, quiz_type, difficulty)
);

-- ============================================================
-- NOTEBOOKLM: QUIZ ATTEMPTS (track user quiz performance)
-- ============================================================
CREATE TABLE IF NOT EXISTS notebooklm_quiz_attempts (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    quiz_id UUID REFERENCES notebooklm_quizzes(id) ON DELETE CASCADE,
    answers JSONB NOT NULL,  -- User's answers
    score INTEGER,
    total_questions INTEGER,
    feedback JSONB,  -- AI-generated feedback on wrong answers
    attempted_at TIMESTAMPTZ DEFAULT NOW()
);

-- ============================================================
-- INDEXES FOR PERFORMANCE
-- ============================================================
CREATE INDEX IF NOT EXISTS idx_notebooks_title ON notebooklm_notebooks USING gin(to_tsvector('english', title));
CREATE INDEX IF NOT EXISTS idx_notebooks_tags ON notebooklm_notebooks USING gin(topic_tags);
CREATE INDEX IF NOT EXISTS idx_assets_notebook ON notebooklm_assets(notebook_id);
CREATE INDEX IF NOT EXISTS idx_assets_type ON notebooklm_assets(asset_type);
CREATE INDEX IF NOT EXISTS idx_transcripts_fulltext ON notebooklm_transcripts USING gin(to_tsvector('english', transcript_text));

-- ============================================================
-- ROW LEVEL SECURITY (open for now, can restrict later)
-- ============================================================
ALTER TABLE projects ENABLE ROW LEVEL SECURITY;
ALTER TABLE notebooklm_notebooks ENABLE ROW LEVEL SECURITY;
ALTER TABLE notebooklm_assets ENABLE ROW LEVEL SECURITY;
ALTER TABLE notebooklm_transcripts ENABLE ROW LEVEL SECURITY;
ALTER TABLE notebooklm_summaries ENABLE ROW LEVEL SECURITY;
ALTER TABLE notebooklm_quizzes ENABLE ROW LEVEL SECURITY;
ALTER TABLE notebooklm_quiz_attempts ENABLE ROW LEVEL SECURITY;

-- Allow public read/write for now (you can restrict later with auth)
CREATE POLICY "Allow all on projects" ON projects FOR ALL USING (true) WITH CHECK (true);
CREATE POLICY "Allow all on notebooks" ON notebooklm_notebooks FOR ALL USING (true) WITH CHECK (true);
CREATE POLICY "Allow all on assets" ON notebooklm_assets FOR ALL USING (true) WITH CHECK (true);
CREATE POLICY "Allow all on transcripts" ON notebooklm_transcripts FOR ALL USING (true) WITH CHECK (true);
CREATE POLICY "Allow all on summaries" ON notebooklm_summaries FOR ALL USING (true) WITH CHECK (true);
CREATE POLICY "Allow all on quizzes" ON notebooklm_quizzes FOR ALL USING (true) WITH CHECK (true);
CREATE POLICY "Allow all on quiz_attempts" ON notebooklm_quiz_attempts FOR ALL USING (true) WITH CHECK (true);

-- ============================================================
-- INSERT DEFAULT PROJECT
-- ============================================================
INSERT INTO projects (name, local_path, description)
VALUES ('notebooklm_scrape', '/Users/z/Desktop/PersonalProjects/ClaudeProjects/notebooklm_scrape', 'NotebookLM audio overviews, transcripts, and study materials')
ON CONFLICT (name) DO NOTHING;

-- ============================================================
-- DONE! Tables created successfully.
-- ============================================================
