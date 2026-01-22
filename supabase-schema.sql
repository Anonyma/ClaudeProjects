-- Reading Status Schema for Multiple Projects
-- Run this in your Supabase SQL Editor

-- Create reading status table (supports multiple projects)
CREATE TABLE IF NOT EXISTS reading_status (
    id BIGSERIAL PRIMARY KEY,
    project TEXT NOT NULL,           -- e.g., 'substack', 'notebooklm', 'telegram'
    article_id TEXT NOT NULL,        -- article identifier within the project
    status TEXT NOT NULL CHECK (status IN ('unread', 'in-progress', 'read')),
    updated_at TIMESTAMPTZ DEFAULT NOW(),

    -- Ensure unique combination of project + article_id
    UNIQUE(project, article_id)
);

-- Create indexes for faster lookups
CREATE INDEX IF NOT EXISTS idx_reading_status_project ON reading_status(project);
CREATE INDEX IF NOT EXISTS idx_reading_status_project_article ON reading_status(project, article_id);

-- Enable Row Level Security
ALTER TABLE reading_status ENABLE ROW LEVEL SECURITY;

-- Create a policy that allows all operations (for personal use)
-- Drop existing policy if it exists, then create
DROP POLICY IF EXISTS "Allow all" ON reading_status;
CREATE POLICY "Allow all" ON reading_status FOR ALL USING (true) WITH CHECK (true);

-- Function to update the updated_at timestamp automatically
CREATE OR REPLACE FUNCTION update_updated_at_column()
RETURNS TRIGGER AS $$
BEGIN
    NEW.updated_at = NOW();
    RETURN NEW;
END;
$$ language 'plpgsql';

-- Trigger to auto-update updated_at on row update
DROP TRIGGER IF EXISTS update_reading_status_updated_at ON reading_status;
CREATE TRIGGER update_reading_status_updated_at
    BEFORE UPDATE ON reading_status
    FOR EACH ROW
    EXECUTE FUNCTION update_updated_at_column();
