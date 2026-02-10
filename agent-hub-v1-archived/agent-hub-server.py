#!/usr/bin/env python3
"""
Agent Hub Server
Serves the dashboard and provides API endpoints for agent status management.
Designed to be the central hub for both Mac and CandyPop agents.
"""

import json
import os
from http.server import HTTPServer, SimpleHTTPRequestHandler
from urllib.parse import urlparse, parse_qs
from datetime import datetime
import socket

PORT = 8766
AGENT_HUB_DIR = os.path.dirname(os.path.abspath(__file__))
STATUSES_FILE = os.path.join(AGENT_HUB_DIR, "statuses.json")

# Bind to all interfaces so CandyPop can reach us via Tailscale
BIND_ADDRESS = '0.0.0.0'


def load_statuses():
    if os.path.exists(STATUSES_FILE):
        with open(STATUSES_FILE, 'r') as f:
            return json.load(f)
    return {"agents": {}}


def save_statuses(data):
    with open(STATUSES_FILE, 'w') as f:
        json.dump(data, f, indent=2)


class AgentHubHandler(SimpleHTTPRequestHandler):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, directory=AGENT_HUB_DIR, **kwargs)

    def do_GET(self):
        parsed = urlparse(self.path)

        if parsed.path == '/api/statuses':
            self.send_response(200)
            self.send_header('Content-Type', 'application/json')
            self.send_header('Access-Control-Allow-Origin', '*')
            self.end_headers()
            self.wfile.write(json.dumps(load_statuses()).encode())
            return

        if parsed.path == '/api/clear-completed':
            data = load_statuses()
            data["agents"] = {
                k: v for k, v in data.get("agents", {}).items()
                if v.get("status") not in ["completed", "idle"]
            }
            save_statuses(data)
            self.send_response(200)
            self.send_header('Content-Type', 'application/json')
            self.send_header('Access-Control-Allow-Origin', '*')
            self.end_headers()
            self.wfile.write(json.dumps({"ok": True}).encode())
            return

        if parsed.path == '/api/clear-all':
            save_statuses({"agents": {}})
            self.send_response(200)
            self.send_header('Content-Type', 'application/json')
            self.send_header('Access-Control-Allow-Origin', '*')
            self.end_headers()
            self.wfile.write(json.dumps({"ok": True}).encode())
            return

        # Serve static files
        if parsed.path == '/':
            self.path = '/dashboard.html'

        super().do_GET()

    def do_POST(self):
        parsed = urlparse(self.path)

        if parsed.path in ['/api/status', '/status']:
            content_length = int(self.headers['Content-Length'])
            post_data = json.loads(self.rfile.read(content_length))

            name = post_data.get('name', 'unknown')
            status = post_data.get('status', 'idle')
            message = post_data.get('message') or post_data.get('task', '')
            timestamp = datetime.utcnow().strftime("%Y-%m-%dT%H:%M:%SZ")

            # New fields
            host = post_data.get('host', 'unknown')
            ai_type = post_data.get('ai_type') or post_data.get('session_type', 'claude')
            project = post_data.get('project', '')
            path = post_data.get('path', '')

            data = load_statuses()
            if "agents" not in data:
                data["agents"] = {}

            agent = data["agents"].get(name, {"history": []})
            agent["status"] = status
            agent["message"] = message
            agent["updated_at"] = timestamp
            agent["host"] = host
            agent["ai_type"] = ai_type
            if project:
                agent["project"] = project
            if path:
                agent["path"] = path

            agent["history"].insert(0, {
                "status": status,
                "message": message,
                "timestamp": timestamp,
                "host": host
            })
            agent["history"] = agent["history"][:20]

            if "created_at" not in agent:
                agent["created_at"] = timestamp

            data["agents"][name] = agent
            save_statuses(data)

            self.send_response(200)
            self.send_header('Content-Type', 'application/json')
            self.send_header('Access-Control-Allow-Origin', '*')
            self.end_headers()
            self.wfile.write(json.dumps({"ok": True}).encode())
            return

        self.send_response(404)
        self.end_headers()

    def do_OPTIONS(self):
        self.send_response(200)
        self.send_header('Access-Control-Allow-Origin', '*')
        self.send_header('Access-Control-Allow-Methods', 'GET, POST, OPTIONS')
        self.send_header('Access-Control-Allow-Headers', 'Content-Type')
        self.end_headers()

    def log_message(self, format, *args):
        # Quieter logging
        if '/api/' in args[0]:
            return
        super().log_message(format, *args)


def main():
    server = HTTPServer((BIND_ADDRESS, PORT), AgentHubHandler)
    hostname = socket.gethostname()
    print(f"🚀 Agent Hub running on {BIND_ADDRESS}:{PORT}")
    print(f"📊 Dashboard: http://localhost:{PORT}/dashboard.html")
    print(f"🌐 Remote access: http://{hostname}.local:{PORT} or via Tailscale IP")
    print(f"📁 Serving from: {AGENT_HUB_DIR}")
    print("Press Ctrl+C to stop")
    try:
        server.serve_forever()
    except KeyboardInterrupt:
        print("\n👋 Agent Hub stopped")
        server.shutdown()


if __name__ == '__main__':
    main()
