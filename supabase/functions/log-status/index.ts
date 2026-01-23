// Supabase Edge Function: log-status
// Purpose: Accept status updates from ANY Claude instance
// Usage: curl -X POST 'https://PROJECT.supabase.co/functions/v1/log-status' -d '{...}'

import { serve } from "https://deno.land/std@0.168.0/http/server.ts"
import { createClient } from 'https://esm.sh/@supabase/supabase-js@2'

const corsHeaders = {
  'Access-Control-Allow-Origin': '*',
  'Access-Control-Allow-Headers': 'authorization, x-client-info, apikey, content-type',
}

serve(async (req) => {
  // Handle CORS preflight
  if (req.method === 'OPTIONS') {
    return new Response('ok', { headers: corsHeaders })
  }

  try {
    const supabaseClient = createClient(
      Deno.env.get('SUPABASE_URL') ?? '',
      Deno.env.get('SUPABASE_ANON_KEY') ?? '',
    )

    const body = await req.json()

    // Required fields
    const {
      session_id,
      session_type,
      current_task,
    } = body

    if (!session_id || !session_type || !current_task) {
      return new Response(
        JSON.stringify({
          error: 'Missing required fields: session_id, session_type, current_task'
        }),
        {
          status: 400,
          headers: { ...corsHeaders, 'Content-Type': 'application/json' },
        }
      )
    }

    // Validate session_type
    const validTypes = ['cli', 'web', 'desktop', 'chrome', 'clawdbot']
    if (!validTypes.includes(session_type)) {
      return new Response(
        JSON.stringify({
          error: `Invalid session_type. Must be one of: ${validTypes.join(', ')}`
        }),
        {
          status: 400,
          headers: { ...corsHeaders, 'Content-Type': 'application/json' },
        }
      )
    }

    // Insert status update
    const { data, error } = await supabaseClient
      .from('claude_session_status')
      .insert({
        session_id,
        session_type,
        session_url: body.session_url || null,
        current_task,
        project_id: body.project_id || null,
        status: body.status || 'active',
        blocked_on: body.blocked_on || null,
        progress_notes: body.progress_notes || null,
        files_modified: body.files_modified || null,
        context: body.context || null,
      })
      .select()

    if (error) throw error

    return new Response(
      JSON.stringify({
        success: true,
        message: 'Status logged successfully',
        data: data[0]
      }),
      {
        headers: { ...corsHeaders, 'Content-Type': 'application/json' },
        status: 200,
      },
    )

  } catch (error) {
    return new Response(
      JSON.stringify({ error: error.message }),
      {
        headers: { ...corsHeaders, 'Content-Type': 'application/json' },
        status: 400,
      },
    )
  }
})
