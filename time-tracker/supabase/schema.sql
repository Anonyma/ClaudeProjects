-- ============================================
-- TIME TRACKER SCHEMA
-- Supabase project: ydwjzlikslebokuxzwco
-- ============================================

-- Activity logs - the core table for tracking what user is doing
CREATE TABLE IF NOT EXISTS activity_logs (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    timestamp TIMESTAMPTZ NOT NULL DEFAULT NOW(),

    -- What the user was doing
    activity_text TEXT NOT NULL,

    -- Input method for analytics
    input_method TEXT NOT NULL DEFAULT 'text' CHECK (input_method IN ('text', 'voice', 'screenshot')),

    -- Device that logged this
    device TEXT NOT NULL CHECK (device IN ('mac', 'iphone', 'web')),

    -- Was this a response to a ping or manual entry?
    entry_type TEXT NOT NULL DEFAULT 'manual' CHECK (entry_type IN ('ping_response', 'manual', 'afk_return')),

    -- Optional: which ping triggered this (for sync)
    ping_id UUID,

    -- Optional metadata
    duration_minutes INTEGER,
    tags TEXT[],
    screenshot_url TEXT,

    -- Timestamps
    created_at TIMESTAMPTZ DEFAULT NOW(),
    updated_at TIMESTAMPTZ DEFAULT NOW()
);

-- Pings - tracks notification state across devices
CREATE TABLE IF NOT EXISTS pings (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    scheduled_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),

    -- Status for cross-device sync
    status TEXT NOT NULL DEFAULT 'pending' CHECK (status IN ('pending', 'sent', 'answered', 'expired', 'skipped')),

    -- Which device answered (if answered)
    answered_by_device TEXT,
    answered_at TIMESTAMPTZ,
    activity_log_id UUID,

    -- Notification IDs for cancellation
    pushover_receipt TEXT,
    mac_notification_id TEXT,

    created_at TIMESTAMPTZ DEFAULT NOW(),
    updated_at TIMESTAMPTZ DEFAULT NOW()
);

-- Add foreign key after both tables exist
ALTER TABLE activity_logs
    ADD CONSTRAINT fk_activity_logs_ping
    FOREIGN KEY (ping_id) REFERENCES pings(id) ON DELETE SET NULL;

ALTER TABLE pings
    ADD CONSTRAINT fk_pings_activity_log
    FOREIGN KEY (activity_log_id) REFERENCES activity_logs(id) ON DELETE SET NULL;

-- Device state - tracks AFK status, last activity, etc.
CREATE TABLE IF NOT EXISTS device_state (
    device TEXT PRIMARY KEY CHECK (device IN ('mac', 'iphone', 'web')),

    -- Last known activity
    last_activity_at TIMESTAMPTZ,
    last_activity_log_id UUID REFERENCES activity_logs(id) ON DELETE SET NULL,

    -- AFK tracking (Mac only)
    is_afk BOOLEAN DEFAULT FALSE,
    afk_started_at TIMESTAMPTZ,

    -- Connection status
    last_seen_at TIMESTAMPTZ DEFAULT NOW(),

    updated_at TIMESTAMPTZ DEFAULT NOW()
);

-- User settings (singleton table)
CREATE TABLE IF NOT EXISTS time_tracker_settings (
    id INTEGER PRIMARY KEY DEFAULT 1 CHECK (id = 1),

    -- Ping intervals
    ping_interval_minutes INTEGER DEFAULT 60,
    skip_if_activity_within_minutes INTEGER DEFAULT 15,

    -- Quiet hours (null = no quiet hours)
    quiet_hours_start TIME,
    quiet_hours_end TIME,

    -- AFK settings
    afk_threshold_minutes INTEGER DEFAULT 5,

    -- Pushover settings (stored here for convenience, but use env vars in production)
    pushover_user_key TEXT,
    pushover_api_token TEXT,

    created_at TIMESTAMPTZ DEFAULT NOW(),
    updated_at TIMESTAMPTZ DEFAULT NOW()
);

-- Insert default settings
INSERT INTO time_tracker_settings (id) VALUES (1) ON CONFLICT (id) DO NOTHING;

-- Insert default device states
INSERT INTO device_state (device) VALUES ('mac') ON CONFLICT (device) DO NOTHING;
INSERT INTO device_state (device) VALUES ('iphone') ON CONFLICT (device) DO NOTHING;
INSERT INTO device_state (device) VALUES ('web') ON CONFLICT (device) DO NOTHING;

-- Indexes for common queries
CREATE INDEX IF NOT EXISTS idx_activity_logs_timestamp ON activity_logs(timestamp DESC);
CREATE INDEX IF NOT EXISTS idx_activity_logs_device ON activity_logs(device);
CREATE INDEX IF NOT EXISTS idx_activity_logs_entry_type ON activity_logs(entry_type);
CREATE INDEX IF NOT EXISTS idx_pings_status ON pings(status);
CREATE INDEX IF NOT EXISTS idx_pings_scheduled ON pings(scheduled_at DESC);

-- Row Level Security (allow all for personal use)
ALTER TABLE activity_logs ENABLE ROW LEVEL SECURITY;
ALTER TABLE pings ENABLE ROW LEVEL SECURITY;
ALTER TABLE device_state ENABLE ROW LEVEL SECURITY;
ALTER TABLE time_tracker_settings ENABLE ROW LEVEL SECURITY;

-- Policies - allow all operations (personal project)
CREATE POLICY "Allow all on activity_logs" ON activity_logs FOR ALL USING (true) WITH CHECK (true);
CREATE POLICY "Allow all on pings" ON pings FOR ALL USING (true) WITH CHECK (true);
CREATE POLICY "Allow all on device_state" ON device_state FOR ALL USING (true) WITH CHECK (true);
CREATE POLICY "Allow all on time_tracker_settings" ON time_tracker_settings FOR ALL USING (true) WITH CHECK (true);

-- Auto-update updated_at trigger function
CREATE OR REPLACE FUNCTION update_updated_at_column()
RETURNS TRIGGER AS $$
BEGIN
    NEW.updated_at = NOW();
    RETURN NEW;
END;
$$ language 'plpgsql';

-- Apply triggers
DROP TRIGGER IF EXISTS update_activity_logs_updated_at ON activity_logs;
CREATE TRIGGER update_activity_logs_updated_at
    BEFORE UPDATE ON activity_logs
    FOR EACH ROW
    EXECUTE FUNCTION update_updated_at_column();

DROP TRIGGER IF EXISTS update_pings_updated_at ON pings;
CREATE TRIGGER update_pings_updated_at
    BEFORE UPDATE ON pings
    FOR EACH ROW
    EXECUTE FUNCTION update_updated_at_column();

DROP TRIGGER IF EXISTS update_device_state_updated_at ON device_state;
CREATE TRIGGER update_device_state_updated_at
    BEFORE UPDATE ON device_state
    FOR EACH ROW
    EXECUTE FUNCTION update_updated_at_column();

DROP TRIGGER IF EXISTS update_time_tracker_settings_updated_at ON time_tracker_settings;
CREATE TRIGGER update_time_tracker_settings_updated_at
    BEFORE UPDATE ON time_tracker_settings
    FOR EACH ROW
    EXECUTE FUNCTION update_updated_at_column();

-- Enable realtime for cross-device sync
ALTER PUBLICATION supabase_realtime ADD TABLE pings;
ALTER PUBLICATION supabase_realtime ADD TABLE activity_logs;
