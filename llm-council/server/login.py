#!/usr/bin/env python3
"""
LLM Council - Login Script

Opens a browser for each provider so you can log in manually.
Sessions are saved to ~/.llm-council/profiles/ for reuse.

Usage:
    python login.py --provider chatgpt
    python login.py --provider claude
    python login.py --provider gemini
    python login.py --provider perplexity
    python login.py --all
"""

import argparse
import os
import sys
from pathlib import Path

try:
    from playwright.sync_api import sync_playwright
except ImportError:
    print("Playwright not installed. Run:")
    print("  pip install playwright")
    print("  playwright install chromium")
    sys.exit(1)

# Provider URLs
PROVIDERS = {
    'chatgpt': {
        'name': 'ChatGPT',
        'url': 'https://chatgpt.com/',
        'check_selector': 'textarea, #prompt-textarea',  # Input field = logged in
    },
    'claude': {
        'name': 'Claude',
        'url': 'https://claude.ai/',
        'check_selector': '[contenteditable="true"], .ProseMirror',  # Chat input = logged in
    },
    'gemini': {
        'name': 'Gemini',
        'url': 'https://gemini.google.com/app',
        'check_selector': '.ql-editor, [contenteditable="true"]',  # Input = logged in
    },
    'perplexity': {
        'name': 'Perplexity',
        'url': 'https://www.perplexity.ai/',
        'check_selector': 'textarea',  # Search input = logged in
    },
}

def get_profile_dir(provider: str) -> Path:
    """Get the profile directory for a provider."""
    base = Path.home() / '.llm-council' / 'profiles' / provider
    base.mkdir(parents=True, exist_ok=True)
    return base

def login(provider: str):
    """Open browser for manual login and save session."""
    if provider not in PROVIDERS:
        print(f"Unknown provider: {provider}")
        print(f"Available: {', '.join(PROVIDERS.keys())}")
        sys.exit(1)

    config = PROVIDERS[provider]
    profile_dir = get_profile_dir(provider)

    print(f"\n{'='*60}")
    print(f"  Logging into {config['name']}")
    print(f"{'='*60}")
    print(f"\nProfile will be saved to: {profile_dir}")
    print(f"\nA browser window will open. Please:")
    print(f"  1. Log in to {config['name']}")
    print(f"  2. Make sure you can see the chat input")
    print(f"  3. Close the browser window when done")
    print(f"\nOpening {config['url']}...\n")

    with sync_playwright() as p:
        # Launch browser with persistent context (saves cookies, localStorage, etc.)
        context = p.chromium.launch_persistent_context(
            user_data_dir=str(profile_dir),
            headless=False,  # Must be visible for manual login
            viewport={'width': 1280, 'height': 900},
            args=['--disable-blink-features=AutomationControlled'],  # Less bot-like
        )

        page = context.pages[0] if context.pages else context.new_page()
        page.goto(config['url'])

        print("Waiting for you to log in...")
        print("(Close the browser window when done)")

        # Wait for the browser to be closed by the user
        try:
            page.wait_for_event('close', timeout=0)  # Wait forever
        except:
            pass

        context.close()

    print(f"\n✓ Session saved for {config['name']}")
    print(f"  Profile: {profile_dir}")

def check_session(provider: str) -> bool:
    """Check if a saved session exists and is valid."""
    if provider not in PROVIDERS:
        return False

    profile_dir = get_profile_dir(provider)
    # Check if profile has any data
    return any(profile_dir.iterdir()) if profile_dir.exists() else False

def list_sessions():
    """List all saved sessions."""
    print("\nSaved Sessions:")
    print("-" * 40)

    for provider, config in PROVIDERS.items():
        profile_dir = get_profile_dir(provider)
        has_session = any(profile_dir.iterdir()) if profile_dir.exists() else False
        status = "✓ Logged in" if has_session else "✗ Not logged in"
        print(f"  {config['name']:12} {status}")

    print()

def main():
    parser = argparse.ArgumentParser(
        description='Log into AI providers and save sessions for LLM Council'
    )
    parser.add_argument(
        '--provider', '-p',
        choices=list(PROVIDERS.keys()),
        help='Provider to log into'
    )
    parser.add_argument(
        '--all', '-a',
        action='store_true',
        help='Log into all providers one by one'
    )
    parser.add_argument(
        '--list', '-l',
        action='store_true',
        help='List saved sessions'
    )
    parser.add_argument(
        '--clear',
        choices=list(PROVIDERS.keys()) + ['all'],
        help='Clear saved session(s)'
    )

    args = parser.parse_args()

    if args.list:
        list_sessions()
        return

    if args.clear:
        import shutil
        if args.clear == 'all':
            for provider in PROVIDERS:
                profile_dir = get_profile_dir(provider)
                if profile_dir.exists():
                    shutil.rmtree(profile_dir)
                    print(f"Cleared session for {provider}")
        else:
            profile_dir = get_profile_dir(args.clear)
            if profile_dir.exists():
                shutil.rmtree(profile_dir)
                print(f"Cleared session for {args.clear}")
        return

    if args.all:
        for provider in PROVIDERS:
            login(provider)
            print()
        print("\n✓ All providers configured!")
        list_sessions()
        return

    if args.provider:
        login(args.provider)
        return

    # No args - show help
    parser.print_help()
    print()
    list_sessions()

if __name__ == '__main__':
    main()
