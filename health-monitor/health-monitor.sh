#!/bin/bash
# System Health Monitor - Collects metrics, detects anomalies, sends alerts
# Runs every 10 minutes via launchd

set -e

DATA_DIR="$HOME/.health-monitor"
METRICS_FILE="$DATA_DIR/metrics.json"
HISTORY_FILE="$DATA_DIR/history.json"
ALERTS_LOG="$DATA_DIR/alerts.log"

# Pushover credentials (for critical alerts)
PUSHOVER_TOKEN="aabpf2tb7a9p3tnhdw3vzfb6hyxcna"
PUSHOVER_USER="u8wpte8pqd3snj75s2n8gxqdzq94xj"

# Get CPU count for relative thresholds
CPU_COUNT=$(sysctl -n hw.ncpu)

# Thresholds (load is relative to CPU count)
LOAD_CRITICAL=$(echo "$CPU_COUNT * 1.5" | bc)  # 1.5x CPU cores = critical (12 for 8-core)
RAM_CRITICAL_MB=200
APP_MEMORY_CRITICAL_PCT=50
LOAD_ANOMALY_MULTIPLIER=2
MEMORY_SPIKE_PCT=20

# Ensure data directory exists
mkdir -p "$DATA_DIR"

# Initialize history file if needed
if [[ ! -f "$HISTORY_FILE" ]]; then
    echo '[]' > "$HISTORY_FILE"
fi

# Get current timestamp
TIMESTAMP=$(date -u +"%Y-%m-%dT%H:%M:%SZ")
TIMESTAMP_EPOCH=$(date +%s)

# Collect CPU load averages
LOAD_1=$(sysctl -n vm.loadavg | awk '{print $2}')
LOAD_5=$(sysctl -n vm.loadavg | awk '{print $3}')
LOAD_15=$(sysctl -n vm.loadavg | awk '{print $4}')

# Collect memory stats (macOS)
VM_STAT=$(vm_stat)
PAGE_SIZE=$(sysctl -n hw.pagesize)

# Parse vm_stat output
PAGES_FREE=$(echo "$VM_STAT" | awk '/Pages free/ {gsub(/\./,"",$3); print $3}')
PAGES_ACTIVE=$(echo "$VM_STAT" | awk '/Pages active/ {gsub(/\./,"",$3); print $3}')
PAGES_INACTIVE=$(echo "$VM_STAT" | awk '/Pages inactive/ {gsub(/\./,"",$3); print $3}')
PAGES_SPECULATIVE=$(echo "$VM_STAT" | awk '/Pages speculative/ {gsub(/\./,"",$3); print $3}')
PAGES_WIRED=$(echo "$VM_STAT" | awk '/Pages wired/ {gsub(/\./,"",$3); print $3}')
PAGES_COMPRESSED=$(echo "$VM_STAT" | awk '/Pages occupied by compressor/ {gsub(/\./,"",$3); print $3}')

# Calculate memory in MB
TOTAL_RAM_MB=$(sysctl -n hw.memsize | awk '{print int($1/1024/1024)}')
FREE_MB=$(echo "$PAGES_FREE $PAGE_SIZE" | awk '{print int($1*$2/1024/1024)}')
ACTIVE_MB=$(echo "$PAGES_ACTIVE $PAGE_SIZE" | awk '{print int($1*$2/1024/1024)}')
INACTIVE_MB=$(echo "$PAGES_INACTIVE $PAGE_SIZE" | awk '{print int($1*$2/1024/1024)}')
WIRED_MB=$(echo "$PAGES_WIRED $PAGE_SIZE" | awk '{print int($1*$2/1024/1024)}')
COMPRESSED_MB=$(echo "${PAGES_COMPRESSED:-0} $PAGE_SIZE" | awk '{print int($1*$2/1024/1024)}')

# Available = free + inactive (can be reclaimed)
AVAILABLE_MB=$((FREE_MB + INACTIVE_MB))
USED_MB=$((TOTAL_RAM_MB - AVAILABLE_MB))
MEMORY_PCT=$(echo "$USED_MB $TOTAL_RAM_MB" | awk '{printf "%.1f", ($1/$2)*100}')

# Get top 10 processes by memory
TOP_PROCS_MEM=$(ps aux | sort -k4 -rn | head -11 | tail -10 | awk '{
    mem_pct = $4
    cpu_pct = $3
    pid = $2
    # Get command name (last field, may have spaces)
    cmd = $11
    for(i=12; i<=NF; i++) cmd = cmd " " $i
    # Truncate long commands
    if(length(cmd) > 40) cmd = substr(cmd, 1, 40) "..."
    printf "{\"pid\":%s,\"name\":\"%s\",\"memory_pct\":%.1f,\"cpu_pct\":%.1f},", pid, cmd, mem_pct, cpu_pct
}' | sed 's/,$//')

# Get top 5 by CPU
TOP_PROCS_CPU=$(ps aux | sort -k3 -rn | head -6 | tail -5 | awk '{
    mem_pct = $4
    cpu_pct = $3
    pid = $2
    cmd = $11
    for(i=12; i<=NF; i++) cmd = cmd " " $i
    if(length(cmd) > 40) cmd = substr(cmd, 1, 40) "..."
    printf "{\"pid\":%s,\"name\":\"%s\",\"memory_pct\":%.1f,\"cpu_pct\":%.1f},", pid, cmd, mem_pct, cpu_pct
}' | sed 's/,$//')

# Count processes
PROC_COUNT=$(ps aux | wc -l | tr -d ' ')

# Get disk usage for main volume
DISK_USAGE=$(df -h / | tail -1 | awk '{print $5}' | tr -d '%')
DISK_AVAILABLE=$(df -h / | tail -1 | awk '{print $4}')

# Build current metrics JSON
CURRENT_METRICS=$(cat <<EOF
{
  "timestamp": "$TIMESTAMP",
  "timestamp_epoch": $TIMESTAMP_EPOCH,
  "cpu_count": $CPU_COUNT,
  "load": {
    "avg_1m": $LOAD_1,
    "avg_5m": $LOAD_5,
    "avg_15m": $LOAD_15,
    "critical_threshold": $LOAD_CRITICAL
  },
  "memory": {
    "total_mb": $TOTAL_RAM_MB,
    "used_mb": $USED_MB,
    "available_mb": $AVAILABLE_MB,
    "free_mb": $FREE_MB,
    "wired_mb": $WIRED_MB,
    "compressed_mb": $COMPRESSED_MB,
    "used_pct": $MEMORY_PCT
  },
  "disk": {
    "used_pct": $DISK_USAGE,
    "available": "$DISK_AVAILABLE"
  },
  "processes": {
    "count": $PROC_COUNT,
    "top_by_memory": [$TOP_PROCS_MEM],
    "top_by_cpu": [$TOP_PROCS_CPU]
  },
  "alerts": []
}
EOF
)

# Function to send Pushover alert (critical)
send_pushover() {
    local title="$1"
    local message="$2"
    curl -s -X POST https://api.pushover.net/1/messages.json \
        -d "token=$PUSHOVER_TOKEN" \
        -d "user=$PUSHOVER_USER" \
        -d "title=$title" \
        -d "message=$message" \
        -d "priority=1" > /dev/null 2>&1
    echo "$(date -u +"%Y-%m-%dT%H:%M:%SZ") [CRITICAL] $title: $message" >> "$ALERTS_LOG"
}

# Function to send macOS notification (warning)
send_notification() {
    local title="$1"
    local message="$2"
    osascript -e "display notification \"$message\" with title \"$title\"" 2>/dev/null || true
    echo "$(date -u +"%Y-%m-%dT%H:%M:%SZ") [WARNING] $title: $message" >> "$ALERTS_LOG"
}

# Alert collection
ALERTS=()

# Get top CPU process for context in alerts
TOP_CPU_PROC=$(ps aux | sort -k3 -rn | head -2 | tail -1 | awk '{print $11}' | xargs basename 2>/dev/null || echo "unknown")
TOP_CPU_PCT=$(ps aux | sort -k3 -rn | head -2 | tail -1 | awk '{print $3}')

# Check critical thresholds
if (( $(echo "$LOAD_1 > $LOAD_CRITICAL" | bc -l) )); then
    send_pushover "System Overloaded" "Load $LOAD_1 (you have $CPU_COUNT cores, threshold $LOAD_CRITICAL). Top: $TOP_CPU_PROC at ${TOP_CPU_PCT}%"
    ALERTS+=("\"critical: load_high\"")
fi

if (( AVAILABLE_MB < RAM_CRITICAL_MB )); then
    send_pushover "Low Memory Alert" "Available RAM (${AVAILABLE_MB}MB) below threshold (${RAM_CRITICAL_MB}MB)"
    ALERTS+=("\"critical: memory_low\"")
fi

# Check if any single app using > 50% memory
TOP_APP_MEM=$(ps aux | sort -k4 -rn | head -2 | tail -1 | awk '{print $4}')
TOP_APP_NAME=$(ps aux | sort -k4 -rn | head -2 | tail -1 | awk '{print $11}')
if (( $(echo "$TOP_APP_MEM > $APP_MEMORY_CRITICAL_PCT" | bc -l) )); then
    send_pushover "Memory Hog Alert" "$TOP_APP_NAME using ${TOP_APP_MEM}% of memory"
    ALERTS+=("\"critical: app_memory_hog\"")
fi

# Anomaly detection (compare with history)
if [[ -f "$HISTORY_FILE" ]] && [[ $(wc -c < "$HISTORY_FILE") -gt 10 ]]; then
    # Get 1-hour baseline (6 samples at 10-min intervals)
    ONE_HOUR_AGO=$((TIMESTAMP_EPOCH - 3600))

    # Calculate average load from last hour using jq
    if command -v jq &> /dev/null; then
        BASELINE_LOAD=$(jq -r --arg since "$ONE_HOUR_AGO" '
            [.[] | select(.timestamp_epoch > ($since | tonumber)) | .load.avg_1m] |
            if length > 0 then add/length else 0 end
        ' "$HISTORY_FILE" 2>/dev/null || echo "0")

        # Get previous memory reading
        PREV_MEMORY_PCT=$(jq -r '.[-1].memory.used_pct // 0' "$HISTORY_FILE" 2>/dev/null || echo "0")

        # Get previous top 5 app names
        PREV_TOP_APPS=$(jq -r '[.[-1].processes.top_by_memory[:5][]?.name] | join(",")' "$HISTORY_FILE" 2>/dev/null || echo "")

        # Check load anomaly (2x baseline)
        if (( $(echo "$BASELINE_LOAD > 0" | bc -l) )); then
            LOAD_THRESHOLD=$(echo "$BASELINE_LOAD * $LOAD_ANOMALY_MULTIPLIER" | bc -l)
            if (( $(echo "$LOAD_1 > $LOAD_THRESHOLD" | bc -l) )); then
                send_notification "Load Spike" "Load ($LOAD_1) is ${LOAD_ANOMALY_MULTIPLIER}x above baseline ($BASELINE_LOAD)"
                ALERTS+=("\"warning: load_spike\"")
            fi
        fi

        # Check memory spike (>20% increase in 10 min)
        if (( $(echo "$PREV_MEMORY_PCT > 0" | bc -l) )); then
            MEMORY_DIFF=$(echo "$MEMORY_PCT - $PREV_MEMORY_PCT" | bc -l)
            if (( $(echo "$MEMORY_DIFF > $MEMORY_SPIKE_PCT" | bc -l) )); then
                send_notification "Memory Spike" "Memory usage jumped ${MEMORY_DIFF}% in 10 minutes"
                ALERTS+=("\"warning: memory_spike\"")
            fi
        fi

        # Check for new apps in top 5
        CURRENT_TOP_APPS=$(echo "$TOP_PROCS_MEM" | grep -o '"name":"[^"]*"' | head -5 | cut -d'"' -f4 | tr '\n' ',' | sed 's/,$//')
        if [[ -n "$PREV_TOP_APPS" ]] && [[ -n "$CURRENT_TOP_APPS" ]]; then
            # Simple check - look for new entries
            IFS=',' read -ra CURRENT_ARR <<< "$CURRENT_TOP_APPS"
            for app in "${CURRENT_ARR[@]}"; do
                if [[ ! "$PREV_TOP_APPS" == *"$app"* ]] && [[ -n "$app" ]]; then
                    send_notification "New Top Process" "$app entered top 5 by memory"
                    ALERTS+=("\"info: new_top_app\"")
                    break
                fi
            done
        fi
    fi
fi

# Add alerts to metrics
ALERTS_JSON=$(IFS=,; echo "${ALERTS[*]}")
CURRENT_METRICS=$(echo "$CURRENT_METRICS" | sed "s/\"alerts\": \[\]/\"alerts\": [$ALERTS_JSON]/")

# Write current metrics
echo "$CURRENT_METRICS" > "$METRICS_FILE"

# Append to history (with 24h rolling window)
if command -v jq &> /dev/null; then
    # Keep only last 24 hours (144 samples at 10-min intervals)
    TWENTY_FOUR_HOURS_AGO=$((TIMESTAMP_EPOCH - 86400))

    # Read existing history, filter old entries, append new
    jq --argjson new "$CURRENT_METRICS" --arg since "$TWENTY_FOUR_HOURS_AGO" '
        [.[] | select(.timestamp_epoch > ($since | tonumber))] + [$new]
    ' "$HISTORY_FILE" > "${HISTORY_FILE}.tmp" && mv "${HISTORY_FILE}.tmp" "$HISTORY_FILE"
else
    # Fallback: just append (no cleanup)
    if [[ $(cat "$HISTORY_FILE") == "[]" ]]; then
        echo "[$CURRENT_METRICS]" > "$HISTORY_FILE"
    else
        sed -i '' 's/]$//' "$HISTORY_FILE"
        echo ",$CURRENT_METRICS]" >> "$HISTORY_FILE"
    fi
fi

echo "Health check completed at $TIMESTAMP"
