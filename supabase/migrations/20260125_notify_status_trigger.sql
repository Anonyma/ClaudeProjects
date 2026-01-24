-- Migration: Auto-notify on claude_session_status inserts
-- Uses pg_net to call the notify-status Edge Function

-- Enable pg_net extension if not already enabled
CREATE EXTENSION IF NOT EXISTS pg_net WITH SCHEMA extensions;

-- Create function to send notification via Edge Function
CREATE OR REPLACE FUNCTION notify_on_status_insert()
RETURNS TRIGGER AS $$
DECLARE
  payload jsonb;
  supabase_url text := 'https://ydwjzlikslebokuxzwco.supabase.co';
  anon_key text := 'eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6Inlkd2p6bGlrc2xlYm9rdXh6d2NvIiwicm9sZSI6ImFub24iLCJpYXQiOjE3Njg4NTEwODAsImV4cCI6MjA4NDQyNzA4MH0.CUPTmjww31xOS0-qknpQHByC3ACZ4lk1CiBcVZXHThU';
BEGIN
  -- Build webhook payload
  payload := jsonb_build_object(
    'type', 'INSERT',
    'table', TG_TABLE_NAME,
    'schema', TG_TABLE_SCHEMA,
    'record', row_to_json(NEW)::jsonb
  );

  -- Call Edge Function via pg_net (async, non-blocking)
  PERFORM net.http_post(
    url := supabase_url || '/functions/v1/notify-status',
    headers := jsonb_build_object(
      'Content-Type', 'application/json',
      'Authorization', 'Bearer ' || anon_key
    ),
    body := payload
  );

  RETURN NEW;
END;
$$ LANGUAGE plpgsql SECURITY DEFINER;

-- Create trigger on claude_session_status table
DROP TRIGGER IF EXISTS trigger_notify_on_status_insert ON public.claude_session_status;

CREATE TRIGGER trigger_notify_on_status_insert
  AFTER INSERT ON public.claude_session_status
  FOR EACH ROW
  EXECUTE FUNCTION notify_on_status_insert();

-- Add comment for documentation
COMMENT ON TRIGGER trigger_notify_on_status_insert ON public.claude_session_status IS
'Triggers Pushover notification via Edge Function when status is blocked, completed, or error';
