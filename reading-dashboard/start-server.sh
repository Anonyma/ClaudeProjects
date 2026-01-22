#!/bin/bash

# Start local server for Reading Dashboard
# Access at http://localhost:8000 on your computer
# Access at http://YOUR_IP:8000 from your phone (same WiFi)

echo "Starting Reading Dashboard server..."
echo ""
echo "Access locally: http://localhost:8000"
echo ""
echo "For mobile access, find your IP and use:"
IP=$(ipconfig getifaddr en0 2>/dev/null || hostname -I 2>/dev/null | awk '{print $1}')
echo "  http://$IP:8000"
echo ""
echo "Press Ctrl+C to stop"
echo ""

cd "$(dirname "$0")"
python3 -m http.server 8000
