-- Life Management System Schema
-- Run this against your Supabase project

-- Daily intentions (morning "ONE thing" responses)
CREATE TABLE IF NOT EXISTS life_daily_intentions (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    date DATE NOT NULL DEFAULT CURRENT_DATE,
    one_thing TEXT NOT NULL,
    energy_level TEXT CHECK (energy_level IN ('high', 'medium', 'low')),
    completed BOOLEAN DEFAULT FALSE,
    notes TEXT,
    created_at TIMESTAMPTZ DEFAULT NOW(),
    UNIQUE(date)
);

-- Hourly check-ins
CREATE TABLE IF NOT EXISTS life_checkins (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    timestamp TIMESTAMPTZ DEFAULT NOW(),
    status TEXT NOT NULL CHECK (status IN ('on_track', 'distracted', 'switched', 'break')),
    current_task TEXT,
    notes TEXT
);

-- Time tracking entries
CREATE TABLE IF NOT EXISTS life_time_entries (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    task_name TEXT NOT NULL,
    category TEXT,
    estimated_minutes INTEGER,
    actual_minutes INTEGER,
    started_at TIMESTAMPTZ,
    ended_at TIMESTAMPTZ,
    completed BOOLEAN DEFAULT FALSE,
    notes TEXT,
    created_at TIMESTAMPTZ DEFAULT NOW()
);

-- Spillover tasks (tasks that got pushed/lost)
CREATE TABLE IF NOT EXISTS life_spillover (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    task_name TEXT NOT NULL,
    original_date DATE NOT NULL,
    source TEXT, -- 'calendar', 'ticktick', 'manual'
    priority INTEGER DEFAULT 3,
    rescheduled_to DATE,
    dropped BOOLEAN DEFAULT FALSE,
    created_at TIMESTAMPTZ DEFAULT NOW()
);

-- Focus blocks
CREATE TABLE IF NOT EXISTS life_focus_blocks (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    task_name TEXT NOT NULL,
    planned_minutes INTEGER NOT NULL,
    actual_minutes INTEGER,
    started_at TIMESTAMPTZ,
    ended_at TIMESTAMPTZ,
    rating INTEGER CHECK (rating BETWEEN 1 AND 5),
    notes TEXT,
    created_at TIMESTAMPTZ DEFAULT NOW()
);

-- Income opportunities tracked
CREATE TABLE IF NOT EXISTS life_opportunities (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    title TEXT NOT NULL,
    platform TEXT,
    url TEXT,
    type TEXT CHECK (type IN ('gig', 'contract', 'fulltime', 'teaching', 'writing')),
    status TEXT DEFAULT 'new' CHECK (status IN ('new', 'applied', 'interviewing', 'rejected', 'accepted', 'passed')),
    pay_range TEXT,
    notes TEXT,
    deadline DATE,
    discovered_at TIMESTAMPTZ DEFAULT NOW(),
    updated_at TIMESTAMPTZ DEFAULT NOW()
);

-- O-1 visa evidence tracker
CREATE TABLE IF NOT EXISTS life_o1_evidence (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    category TEXT NOT NULL CHECK (category IN ('publications', 'judging', 'awards', 'press', 'salary', 'other')),
    title TEXT NOT NULL,
    description TEXT,
    url TEXT,
    date DATE,
    strength TEXT CHECK (strength IN ('strong', 'medium', 'weak')),
    documents TEXT[], -- array of file paths or URLs
    created_at TIMESTAMPTZ DEFAULT NOW()
);

-- Weekly digests log
CREATE TABLE IF NOT EXISTS life_weekly_digests (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    week_start DATE NOT NULL,
    digest_type TEXT NOT NULL CHECK (digest_type IN ('time_tracking', 'opportunities', 'o1_progress')),
    content JSONB,
    sent_at TIMESTAMPTZ DEFAULT NOW()
);

-- Indexes for common queries
CREATE INDEX IF NOT EXISTS idx_checkins_timestamp ON life_checkins(timestamp DESC);
CREATE INDEX IF NOT EXISTS idx_time_entries_started ON life_time_entries(started_at DESC);
CREATE INDEX IF NOT EXISTS idx_spillover_date ON life_spillover(original_date DESC);
CREATE INDEX IF NOT EXISTS idx_opportunities_status ON life_opportunities(status);
