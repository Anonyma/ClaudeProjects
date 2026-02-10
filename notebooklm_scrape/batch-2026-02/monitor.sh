#!/bin/bash
# Monitor NotebookLM batch progress from Mac
# Usage: bash monitor.sh [--watch]

REMOTE="CandyPop"
PROGRESS_FILE="~/Projects/notebooklm/batch-2026-02/progress.json"

show_progress() {
    clear
    echo "╔══════════════════════════════════════════════════════════════╗"
    echo "║        NotebookLM Batch Generation - Progress              ║"
    echo "╚══════════════════════════════════════════════════════════════╝"
    echo ""

    # Fetch and display progress
    ssh "$REMOTE" "cat $PROGRESS_FILE 2>/dev/null" | python3 -c "
import json, sys
try:
    data = json.load(sys.stdin)
    print(f\"Overall: {data['overall_status']}  |  Last updated: {data.get('last_updated', 'never')}\")
    print()
    print(f\"{'Topic':<45} {'Phase':<20} {'Sources':<12} {'Dives':<10} {'Status'}\")
    print('─' * 100)
    for tid, t in data['topics'].items():
        src = f\"{t['sources_found']}/{t['sources_target']}\"
        dives = f\"{t['deep_dives_generated']}/{t['deep_dives_target']}\"
        status = '✓' if t['phase'] == 'complete' else ('⚠' if t.get('errors') else '○')
        phase = t['phase']
        title = t.get('title', tid)[:44]
        print(f\"{title:<45} {phase:<20} {src:<12} {dives:<10} {status}\")
        if t.get('errors'):
            for err in t['errors'][-1:]:
                print(f\"  └─ ⚠ {err}\")
    print()
except Exception as e:
    print(f'Error reading progress: {e}')
" 2>/dev/null

    echo ""
    echo "─── Agent Hub Status ───"
    agent-status 2>/dev/null | grep -E "nlm-|notebooklm" || echo "  No active notebooklm agents"
    echo ""
    echo "Last check: $(date '+%H:%M:%S')"
}

if [ "$1" = "--watch" ]; then
    while true; do
        show_progress
        sleep 30
    done
else
    show_progress
fi
