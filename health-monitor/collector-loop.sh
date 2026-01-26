#!/bin/bash
# Runs health-monitor.sh every 60 seconds in a loop

while true; do
    /Users/z/.health-monitor/health-monitor.sh >> /Users/z/.health-monitor/stdout.log 2>> /Users/z/.health-monitor/stderr.log
    sleep 60
done
