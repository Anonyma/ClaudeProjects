// Supabase Edge Function: notify-status
// Purpose: Forward claude_session_status updates to Pushover
// Triggered by: Database webhook on claude_session_status insert

import { serve } from "https://deno.land/std@0.168.0/http/server.ts"

const PUSHOVER_TOKEN = 'aabpf2tb7a9p3tnhdw3vzfb6hyxcna'
const PUSHOVER_USER = 'u8wpte8pqd3snj75s2n8gxqdzq94xj'
const PUSHOVER_URL = 'https://api.pushover.net/1/messages.json'

interface StatusRecord {
  id: string
  session_id: string
  session_type: string
  session_url?: string
  current_task: string
  project_id?: string
  status: string
  blocked_on?: string
  progress_notes?: string
  files_modified?: string[]
  context?: Record<string, unknown>
  created_at: string
}

interface WebhookPayload {
  type: 'INSERT' | 'UPDATE' | 'DELETE'
  table: string
  record: StatusRecord
  schema: string
  old_record?: StatusRecord
}

// Determine if this status update warrants a notification
function shouldNotify(record: StatusRecord): boolean {
  const notifyStatuses = ['blocked', 'completed', 'error']
  return notifyStatuses.includes(record.status.toLowerCase())
}

// Get notification priority based on status
function getPriority(status: string): number {
  switch (status.toLowerCase()) {
    case 'blocked':
    case 'error':
      return 1  // High priority (bypass quiet hours)
    case 'completed':
      return 0  // Normal priority
    default:
      return -1 // Low priority
  }
}

// Get emoji and title based on status
function getNotificationTitle(status: string): string {
  switch (status.toLowerCase()) {
    case 'blocked':
      return '🆘 Agent Blocked'
    case 'error':
      return '⚠️ Agent Error'
    case 'completed':
      return '✅ Task Completed'
    default:
      return '📝 Agent Update'
  }
}

// Build notification message
function buildMessage(record: StatusRecord): string {
  const lines: string[] = []

  // Session info
  lines.push(`Session: ${record.session_type} (${record.session_id})`)

  // Project if available
  if (record.project_id) {
    lines.push(`Project: ${record.project_id}`)
  }

  // Current task
  lines.push(`Task: ${record.current_task}`)

  // Blocked reason if applicable
  if (record.blocked_on) {
    lines.push(`Blocked on: ${record.blocked_on}`)
  }

  // Progress notes if available
  if (record.progress_notes) {
    lines.push(`Notes: ${record.progress_notes}`)
  }

  // Session URL if available
  if (record.session_url) {
    lines.push(`URL: ${record.session_url}`)
  }

  return lines.join('\n')
}

// Send Pushover notification
async function sendPushover(title: string, message: string, priority: number): Promise<Response> {
  const formData = new FormData()
  formData.append('token', PUSHOVER_TOKEN)
  formData.append('user', PUSHOVER_USER)
  formData.append('title', title)
  formData.append('message', message)
  formData.append('priority', priority.toString())

  // For high priority, add sound
  if (priority >= 1) {
    formData.append('sound', 'persistent')
  }

  return fetch(PUSHOVER_URL, {
    method: 'POST',
    body: formData,
  })
}

serve(async (req) => {
  // Handle CORS
  if (req.method === 'OPTIONS') {
    return new Response('ok', {
      headers: {
        'Access-Control-Allow-Origin': '*',
        'Access-Control-Allow-Headers': 'authorization, x-client-info, apikey, content-type',
      },
    })
  }

  try {
    const payload: WebhookPayload = await req.json()

    // Only process INSERTs (new status updates)
    if (payload.type !== 'INSERT') {
      return new Response(
        JSON.stringify({ message: 'Ignoring non-INSERT event' }),
        { status: 200, headers: { 'Content-Type': 'application/json' } }
      )
    }

    const record = payload.record

    // Check if notification is warranted
    if (!shouldNotify(record)) {
      return new Response(
        JSON.stringify({
          message: 'Status does not require notification',
          status: record.status
        }),
        { status: 200, headers: { 'Content-Type': 'application/json' } }
      )
    }

    // Build and send notification
    const title = getNotificationTitle(record.status)
    const message = buildMessage(record)
    const priority = getPriority(record.status)

    const pushoverResponse = await sendPushover(title, message, priority)
    const pushoverResult = await pushoverResponse.json()

    if (pushoverResult.status !== 1) {
      throw new Error(`Pushover error: ${JSON.stringify(pushoverResult)}`)
    }

    return new Response(
      JSON.stringify({
        success: true,
        message: 'Notification sent',
        title,
        priority,
        pushover_request: pushoverResult.request,
      }),
      { status: 200, headers: { 'Content-Type': 'application/json' } }
    )

  } catch (error) {
    console.error('Error processing webhook:', error)
    return new Response(
      JSON.stringify({ error: error.message }),
      { status: 500, headers: { 'Content-Type': 'application/json' } }
    )
  }
})
