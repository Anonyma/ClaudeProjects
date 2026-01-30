#!/usr/bin/env python3
"""
LLM Council - Playwright Server

HTTP server that queries AI providers using saved browser sessions.
Run login.py first to set up sessions.

Usage:
    python server.py              # Start server on port 8881
    python server.py --port 9000  # Custom port

API:
    POST /query
    {
        "provider": "chatgpt",
        "prompt": "Hello, how are you?"
    }
"""

import argparse
import asyncio
import json
import os
import sys
import time
from http.server import HTTPServer, BaseHTTPRequestHandler
from pathlib import Path
from threading import Thread
from typing import Optional

try:
    from playwright.sync_api import sync_playwright, Browser, BrowserContext, Page
except ImportError:
    print("Playwright not installed. Run:")
    print("  pip install playwright")
    print("  playwright install chromium")
    sys.exit(1)

# Provider configurations
PROVIDERS = {
    'chatgpt': {
        'name': 'ChatGPT',
        'url': 'https://chatgpt.com/',
        'new_chat_url': 'https://chatgpt.com/',
        'input_selector': '#prompt-textarea, textarea[data-id="root"]',
        'send_selector': 'button[data-testid="send-button"]',
        'response_selector': '[data-message-author-role="assistant"]',
        'loading_selector': '.result-streaming',
    },
    'claude': {
        'name': 'Claude',
        'url': 'https://claude.ai/new',
        'new_chat_url': 'https://claude.ai/new',
        'input_selector': '[contenteditable="true"].ProseMirror',
        'send_selector': 'button[aria-label="Send Message"]',
        'response_selector': '[class*="font-claude-message"], [class*="prose"]',
        'loading_selector': '[data-is-streaming="true"]',
    },
    'gemini': {
        'name': 'Gemini',
        'url': 'https://gemini.google.com/app',
        'new_chat_url': 'https://gemini.google.com/app',
        'input_selector': '.ql-editor, [contenteditable="true"], rich-textarea',
        'send_selector': 'button[aria-label*="Send"]',
        'response_selector': '.response-content, .model-response, message-content',
        'loading_selector': '.loading-indicator, [class*="loading"]',
    },
    'perplexity': {
        'name': 'Perplexity',
        'url': 'https://www.perplexity.ai/',
        'new_chat_url': 'https://www.perplexity.ai/',
        'input_selector': 'textarea[placeholder*="Ask"]',
        'send_selector': 'button[aria-label*="Submit"], button[type="submit"]',
        'response_selector': '.prose, [class*="answer"]',
        'loading_selector': '[class*="loading"], .animate-pulse',
    },
}

def get_profile_dir(provider: str) -> Path:
    """Get the profile directory for a provider."""
    return Path.home() / '.llm-council' / 'profiles' / provider

class ProviderSession:
    """Manages a browser session for a single provider."""

    def __init__(self, provider: str, playwright):
        self.provider = provider
        self.config = PROVIDERS[provider]
        self.playwright = playwright
        self.context: Optional[BrowserContext] = None
        self.page: Optional[Page] = None

    def start(self):
        """Start the browser session."""
        profile_dir = get_profile_dir(self.provider)

        if not profile_dir.exists() or not any(profile_dir.iterdir()):
            raise Exception(f"No session saved for {self.provider}. Run: python login.py --provider {self.provider}")

        print(f"Starting {self.config['name']} session...")

        self.context = self.playwright.chromium.launch_persistent_context(
            user_data_dir=str(profile_dir),
            headless=True,  # Run headless for queries
            viewport={'width': 1280, 'height': 900},
            args=['--disable-blink-features=AutomationControlled'],
        )

        self.page = self.context.pages[0] if self.context.pages else self.context.new_page()
        print(f"✓ {self.config['name']} ready")

    def stop(self):
        """Stop the browser session."""
        if self.context:
            self.context.close()
            self.context = None
            self.page = None

    def query(self, prompt: str, timeout: int = 120) -> str:
        """Send a query and get the response."""
        if not self.page:
            raise Exception("Session not started")

        # Navigate to new chat
        self.page.goto(self.config['new_chat_url'])
        self.page.wait_for_load_state('networkidle', timeout=30000)

        # Wait for input to be ready
        self.page.wait_for_selector(self.config['input_selector'], timeout=10000)

        # Find and fill the input
        input_el = self.page.query_selector(self.config['input_selector'])
        if not input_el:
            raise Exception(f"Could not find input field for {self.provider}")

        # Handle different input types
        tag = input_el.evaluate('el => el.tagName.toLowerCase()')

        if tag == 'textarea':
            input_el.fill(prompt)
        else:
            # contenteditable
            input_el.focus()
            input_el.evaluate('el => el.textContent = ""')
            self.page.keyboard.type(prompt)

        # Small delay for UI to update
        self.page.wait_for_timeout(500)

        # Click send button
        send_btn = self.page.query_selector(self.config['send_selector'])
        if send_btn:
            send_btn.click()
        else:
            # Try Enter key
            self.page.keyboard.press('Enter')

        # Wait for response
        start_time = time.time()
        response_text = ""

        while time.time() - start_time < timeout:
            # Check if still loading
            loading = self.page.query_selector(self.config['loading_selector'])

            if not loading or not loading.is_visible():
                # Get response text
                self.page.wait_for_timeout(1000)  # Small delay for final render

                responses = self.page.query_selector_all(self.config['response_selector'])
                if responses:
                    # Get the last response
                    last_response = responses[-1]
                    response_text = last_response.text_content() or ""

                    if response_text.strip():
                        return response_text.strip()

            self.page.wait_for_timeout(1000)

        if response_text:
            return response_text.strip()

        raise Exception(f"Timeout waiting for response from {self.provider}")


class LLMCouncilServer:
    """HTTP server for LLM Council queries."""

    def __init__(self, port: int = 8881):
        self.port = port
        self.playwright = None
        self.sessions: dict[str, ProviderSession] = {}

    def start_sessions(self, providers: list[str]):
        """Start browser sessions for specified providers."""
        self.playwright = sync_playwright().start()

        for provider in providers:
            if provider in PROVIDERS:
                try:
                    session = ProviderSession(provider, self.playwright)
                    session.start()
                    self.sessions[provider] = session
                except Exception as e:
                    print(f"Warning: Could not start {provider}: {e}")

    def stop_sessions(self):
        """Stop all browser sessions."""
        for session in self.sessions.values():
            session.stop()
        if self.playwright:
            self.playwright.stop()

    def query(self, provider: str, prompt: str) -> dict:
        """Query a provider."""
        if provider not in self.sessions:
            return {'error': f"Provider {provider} not available. Available: {list(self.sessions.keys())}"}

        try:
            start_time = time.time()
            response = self.sessions[provider].query(prompt)
            elapsed = time.time() - start_time

            return {
                'success': True,
                'provider': provider,
                'response': response,
                'elapsed': round(elapsed, 2),
            }
        except Exception as e:
            return {'error': str(e)}


# Global server instance
server_instance: Optional[LLMCouncilServer] = None


class RequestHandler(BaseHTTPRequestHandler):
    """HTTP request handler."""

    def do_OPTIONS(self):
        """Handle CORS preflight."""
        self.send_response(200)
        self.send_header('Access-Control-Allow-Origin', '*')
        self.send_header('Access-Control-Allow-Methods', 'GET, POST, OPTIONS')
        self.send_header('Access-Control-Allow-Headers', 'Content-Type')
        self.end_headers()

    def do_GET(self):
        """Handle GET requests."""
        if self.path == '/health':
            self.send_json({'status': 'ok', 'providers': list(server_instance.sessions.keys())})
        elif self.path == '/providers':
            self.send_json({
                'available': list(server_instance.sessions.keys()),
                'all': list(PROVIDERS.keys()),
            })
        else:
            self.send_json({'error': 'Not found'}, 404)

    def do_POST(self):
        """Handle POST requests."""
        if self.path == '/query':
            content_length = int(self.headers.get('Content-Length', 0))
            body = self.rfile.read(content_length).decode('utf-8')

            try:
                data = json.loads(body)
            except json.JSONDecodeError:
                self.send_json({'error': 'Invalid JSON'}, 400)
                return

            provider = data.get('provider')
            prompt = data.get('prompt')

            if not provider or not prompt:
                self.send_json({'error': 'Missing provider or prompt'}, 400)
                return

            result = server_instance.query(provider, prompt)
            self.send_json(result)
        else:
            self.send_json({'error': 'Not found'}, 404)

    def send_json(self, data: dict, status: int = 200):
        """Send JSON response."""
        self.send_response(status)
        self.send_header('Content-Type', 'application/json')
        self.send_header('Access-Control-Allow-Origin', '*')
        self.end_headers()
        self.wfile.write(json.dumps(data).encode('utf-8'))

    def log_message(self, format, *args):
        """Custom log format."""
        print(f"[{self.log_date_time_string()}] {args[0]}")


def main():
    global server_instance

    parser = argparse.ArgumentParser(description='LLM Council Playwright Server')
    parser.add_argument('--port', '-p', type=int, default=8881, help='Port to listen on')
    parser.add_argument('--providers', '-P', nargs='+', default=list(PROVIDERS.keys()),
                        choices=list(PROVIDERS.keys()), help='Providers to enable')
    args = parser.parse_args()

    print("\n" + "="*60)
    print("  LLM Council - Playwright Server")
    print("="*60 + "\n")

    # Check for saved sessions
    available = []
    for provider in args.providers:
        profile_dir = get_profile_dir(provider)
        if profile_dir.exists() and any(profile_dir.iterdir()):
            available.append(provider)
        else:
            print(f"⚠ No session for {provider} - run: python login.py --provider {provider}")

    if not available:
        print("\n❌ No provider sessions found!")
        print("Run login.py first to set up sessions.")
        sys.exit(1)

    print(f"\nStarting sessions for: {', '.join(available)}")

    server_instance = LLMCouncilServer(args.port)

    try:
        server_instance.start_sessions(available)

        print(f"\n✓ Server starting on http://localhost:{args.port}")
        print(f"  Available providers: {', '.join(server_instance.sessions.keys())}")
        print("\nEndpoints:")
        print(f"  GET  /health     - Check server status")
        print(f"  GET  /providers  - List available providers")
        print(f"  POST /query      - Query a provider")
        print("\nPress Ctrl+C to stop\n")

        httpd = HTTPServer(('localhost', args.port), RequestHandler)
        httpd.serve_forever()

    except KeyboardInterrupt:
        print("\n\nShutting down...")
    finally:
        server_instance.stop_sessions()
        print("Server stopped.")


if __name__ == '__main__':
    main()
