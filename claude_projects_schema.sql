-- Claude Projects Index Table
CREATE TABLE IF NOT EXISTS claude_projects (
    id TEXT PRIMARY KEY,
    name TEXT NOT NULL,
    description TEXT,
    path TEXT,
    type TEXT,
    created DATE,
    tags TEXT[],
    status TEXT DEFAULT 'active',
    access_method TEXT,
    access_url TEXT,
    access_instructions TEXT,
    requires_server BOOLEAN DEFAULT false,
    server_command TEXT,
    hosted_url TEXT,
    supabase_project_id TEXT,
    supabase_table TEXT,
    files TEXT[],
    updated_at TIMESTAMPTZ DEFAULT NOW()
);

-- Enable RLS
ALTER TABLE claude_projects ENABLE ROW LEVEL SECURITY;
DROP POLICY IF EXISTS "Allow all" ON claude_projects;
CREATE POLICY "Allow all" ON claude_projects FOR ALL USING (true) WITH CHECK (true);

-- Insert projects
INSERT INTO claude_projects (id, name, description, path, type, created, tags, status, access_method, access_url, access_instructions, requires_server, supabase_project_id, supabase_table, files)
VALUES
('substack-dashboard', 'Substack Reads Dashboard', 'Dashboard to track reading status of 93 saved Substack articles. Syncs with Supabase for cross-device access.', '/Users/z/Desktop/PersonalProjects/ClaudeProjects/substack-dashboard', 'web-app', '2025-01-20', ARRAY['dashboard', 'substack', 'reading-tracker', 'supabase', 'pwa'], 'active', 'file', 'file:///Users/z/Desktop/PersonalProjects/ClaudeProjects/substack-dashboard/index.html', 'Open directly in browser. Works offline. Data syncs to Supabase automatically.', false, 'substack', 'reading_status', ARRAY['index.html', 'articles.json', 'manifest.json']),

('reading-dashboard', 'NotebookLM Reading Dashboard', 'Dashboard for NotebookLM sources. Original version before Substack dashboard was created separately.', '/Users/z/Desktop/PersonalProjects/ClaudeProjects/reading-dashboard', 'web-app', '2025-01-19', ARRAY['dashboard', 'notebooklm', 'reading-tracker'], 'deprecated', 'file-or-localhost', 'file:///Users/z/Desktop/PersonalProjects/ClaudeProjects/reading-dashboard/index.html', 'Can open directly (uses embedded-data.js). For localhost: python3 -m http.server 8000', false, NULL, NULL, ARRAY['index.html', 'embedded-data.js', 'start-server.sh']),

('notebooklm-scrape', 'NotebookLM Scraper', 'Python scripts for scraping NotebookLM notebooks, sources, and audio transcriptions.', '/Users/z/Desktop/PersonalProjects/ClaudeProjects/notebooklm_scrape', 'python-scripts', '2025-01-19', ARRAY['scraper', 'notebooklm', 'data', 'python'], 'active', 'cli', NULL, 'Run: cd path && python3 <script>.py. Install deps: pip install -r requirements.txt', false, NULL, NULL, ARRAY['scrape_data.py', 'process_notebook.py', 'transcribe_optimized.py']),

('htgaa-biobootcamp', 'HTGAA BioBootcamp Course Materials', 'How to Grow Almost Anything - BioBootcamp course pages and learning materials', '/Users/z/Desktop/PersonalProjects/ClaudeProjects/htgaa-biobootcamp', 'web-app', '2025-01-20', ARRAY['biotech', 'learning', 'htgaa', 'course'], 'active', 'file', 'file:///Users/z/Desktop/PersonalProjects/ClaudeProjects/htgaa-biobootcamp/index.html', 'Open directly in browser. Static HTML.', false, NULL, NULL, ARRAY['index.html', 'htgaa-day1-course.html']),

('htgaa-learning-guide', 'HTGAA BioBootcamp Learning Guide', 'Comprehensive learning guide document for HTGAA BioBootcamp program', '/Users/z/Desktop/PersonalProjects/ClaudeProjects', 'document', '2025-01-19', ARRAY['biotech', 'learning', 'guide', 'htgaa'], 'active', 'file', 'file:///Users/z/Desktop/PersonalProjects/ClaudeProjects/HTGAA_BioBootcamp_Learning_Guide.html', 'Open directly in browser. Single HTML document.', false, NULL, NULL, ARRAY['HTGAA_BioBootcamp_Learning_Guide.html', 'HTGAA_BioBootcamp_Learning_Guide.md'])

ON CONFLICT (id) DO UPDATE SET
    name = EXCLUDED.name,
    description = EXCLUDED.description,
    access_url = EXCLUDED.access_url,
    access_instructions = EXCLUDED.access_instructions,
    status = EXCLUDED.status,
    updated_at = NOW();
