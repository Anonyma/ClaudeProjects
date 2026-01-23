-- Migration: Claude Session Status Tracking
-- Purpose: Unified status reporting for ALL Claude instances (CLI, Web, Desktop, Chrome)
-- Created: 2026-01-23

CREATE TABLE IF NOT EXISTS claude_session_status (
  id uuid DEFAULT gen_random_uuid() PRIMARY KEY,
  session_id text NOT NULL,           -- Unique session identifier (e.g. "claude-web-2026-01-23-afternoon")
  session_type text NOT NULL,         -- "cli" | "web" | "desktop" | "chrome" | "clawdbot"
  session_url text,                   -- Link back to session (claude.ai/chat/xyz, etc)
  current_task text NOT NULL,         -- What are you working on right now?
  project_id text,                    -- Reference to projects.json id
  status text DEFAULT 'active',       -- "active" | "blocked" | "completed" | "idle"
  blocked_on text,                    -- If blocked, describe the blocker
  progress_notes text,                -- Free-form progress update
  files_modified text[],              -- Array of file paths changed
  context jsonb,                      -- Extra structured data
  last_activity timestamp DEFAULT now(),
  created_at timestamp DEFAULT now()
);

-- Indexes for efficient queries
CREATE INDEX IF NOT EXISTS idx_session_status_last_activity 
  ON claude_session_status(last_activity DESC);

CREATE INDEX IF NOT EXISTS idx_session_status_session_id 
  ON claude_session_status(session_id);

CREATE INDEX IF NOT EXISTS idx_session_status_project_id 
  ON claude_session_status(project_id);

CREATE INDEX IF NOT EXISTS idx_session_status_status 
  ON claude_session_status(status);

-- View: Most recent status per session
CREATE OR REPLACE VIEW session_status_latest AS
SELECT DISTINCT ON (session_id)
  id,
  session_id,
  session_type,
  session_url,
  current_task,
  project_id,
  status,
  blocked_on,
  progress_notes,
  files_modified,
  context,
  last_activity,
  created_at
FROM claude_session_status
ORDER BY session_id, last_activity DESC;

-- Enable Row Level Security (optional - set to permissive for now)
ALTER TABLE claude_session_status ENABLE ROW LEVEL SECURITY;

CREATE POLICY "Allow all operations for anon" 
  ON claude_session_status
  FOR ALL 
  USING (true)
  WITH CHECK (true);

-- Comment
COMMENT ON TABLE claude_session_status IS 
'Status reports from all Claude instances (CLI, Web, Desktop, Chrome, Clawdbot) for coordination and continuity';
