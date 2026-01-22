#!/usr/bin/env python3
"""
Bidirectional sync between local projects.json and Supabase claude_projects table.
Run manually or via launchd for automatic sync.

Usage:
    python3 sync_projects.py           # Sync both directions
    python3 sync_projects.py --dry-run # Show what would be synced without making changes
    python3 sync_projects.py --local   # Only push local -> Supabase
    python3 sync_projects.py --remote  # Only pull Supabase -> local
"""

import json
import os
import sys
import argparse
from datetime import datetime
from pathlib import Path

# Supabase config
SUPABASE_URL = "https://ydwjzlikslebokuxzwco.supabase.co"
SUPABASE_ANON_KEY = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6Inlkd2p6bGlrc2xlYm9rdXh6d2NvIiwicm9sZSI6ImFub24iLCJpYXQiOjE3Njg4NTEwODAsImV4cCI6MjA4NDQyNzA4MH0.CUPTmjww31xOS0-qknpQHByC3ACZ4lk1CiBcVZXHThU"
LOG_PROJECT_ENDPOINT = f"{SUPABASE_URL}/functions/v1/log-project"

# Local paths
PROJECTS_JSON = Path("/Users/z/Desktop/PersonalProjects/ClaudeProjects/projects.json")
SYNC_LOG = Path("/Users/z/Desktop/PersonalProjects/ClaudeProjects/scripts/sync.log")

def log(message: str):
    """Log to file and stdout"""
    timestamp = datetime.now().isoformat()
    log_line = f"[{timestamp}] {message}"
    print(log_line)
    with open(SYNC_LOG, "a") as f:
        f.write(log_line + "\n")

def load_local_projects() -> dict:
    """Load projects from local JSON file"""
    if not PROJECTS_JSON.exists():
        return {}

    with open(PROJECTS_JSON) as f:
        data = json.load(f)

    # Convert to dict keyed by project ID
    projects = {}
    for p in data.get("projects", []):
        projects[p["id"]] = p
    return projects

def get_ssl_context():
    """Get SSL context with proper certificate handling for macOS"""
    import ssl
    try:
        # Try to use certifi if available
        import certifi
        return ssl.create_default_context(cafile=certifi.where())
    except ImportError:
        # Fall back to default context
        ctx = ssl.create_default_context()
        # On macOS, try to load system certificates
        try:
            ctx.load_default_certs()
        except Exception:
            pass
        return ctx

def fetch_supabase_projects() -> dict:
    """Fetch projects from Supabase"""
    import urllib.request
    import urllib.error

    url = f"{SUPABASE_URL}/rest/v1/claude_projects?select=*"
    headers = {
        "apikey": SUPABASE_ANON_KEY,
        "Authorization": f"Bearer {SUPABASE_ANON_KEY}"
    }

    req = urllib.request.Request(url, headers=headers)
    ssl_context = get_ssl_context()
    try:
        with urllib.request.urlopen(req, context=ssl_context) as response:
            data = json.loads(response.read().decode())
            return {p["id"]: p for p in data}
    except urllib.error.HTTPError as e:
        log(f"Error fetching from Supabase: {e}")
        return {}

def push_to_supabase(project: dict, dry_run: bool = False) -> bool:
    """Push a project to Supabase via Edge Function"""
    import urllib.request
    import urllib.error

    # Map local format to API format
    payload = {
        "id": project["id"],
        "name": project["name"],
        "description": project.get("description"),
        "path": project.get("path"),
        "type": project.get("type"),
        "status": project.get("status", "active"),
        "tags": project.get("tags", []),
        "hosted_url": project.get("access", {}).get("hosted"),
        "access_url": project.get("access", {}).get("url"),
        "localhost_command": project.get("access", {}).get("serverCommand"),
        "github_repo": project.get("github", {}).get("repo"),
        "github_branch": project.get("github", {}).get("branch"),
        "claude_session_url": project.get("claudeCodeSession"),
        "deployment_platform": None
    }

    # Detect deployment platform from various fields
    if project.get("deployments"):
        if "netlify" in project["deployments"]:
            payload["deployment_platform"] = "netlify"
        elif "railway" in project["deployments"]:
            payload["deployment_platform"] = "railway"
        elif "replit" in project["deployments"]:
            payload["deployment_platform"] = "replit"

    if dry_run:
        log(f"  [DRY RUN] Would push: {project['id']}")
        return True

    data = json.dumps(payload).encode()
    req = urllib.request.Request(
        LOG_PROJECT_ENDPOINT,
        data=data,
        headers={"Content-Type": "application/json"},
        method="POST"
    )

    ssl_context = get_ssl_context()
    try:
        with urllib.request.urlopen(req, context=ssl_context) as response:
            result = json.loads(response.read().decode())
            if result.get("success"):
                log(f"  Pushed to Supabase: {project['id']}")
                return True
            else:
                log(f"  Error pushing {project['id']}: {result.get('error')}")
                return False
    except urllib.error.HTTPError as e:
        log(f"  HTTP Error pushing {project['id']}: {e}")
        return False

def add_to_local(project: dict, local_data: dict, dry_run: bool = False) -> bool:
    """Add a project from Supabase to local JSON"""
    if dry_run:
        log(f"  [DRY RUN] Would add to local: {project['id']}")
        return True

    # Convert Supabase format to local format
    local_project = {
        "id": project["id"],
        "name": project["name"],
        "description": project.get("description"),
        "path": project.get("path"),
        "type": project.get("type", "web-app"),
        "created": project.get("created", datetime.now().strftime("%Y-%m-%d")),
        "tags": project.get("tags", []),
        "status": project.get("status", "active"),
        "access": {
            "method": project.get("access_method", "file"),
            "url": project.get("access_url"),
            "hosted": project.get("hosted_url"),
            "requiresServer": project.get("requires_server", False)
        }
    }

    if project.get("github_repo"):
        local_project["github"] = {
            "repo": project["github_repo"],
            "branch": project.get("github_branch")
        }

    if project.get("claude_session_url"):
        local_project["claudeCodeSession"] = project["claude_session_url"]

    # Load full JSON, add project, save
    with open(PROJECTS_JSON) as f:
        full_data = json.load(f)

    full_data["projects"].append(local_project)
    full_data["meta"]["lastUpdated"] = datetime.now().strftime("%Y-%m-%d")

    with open(PROJECTS_JSON, "w") as f:
        json.dump(full_data, f, indent=2)

    log(f"  Added to local: {project['id']}")
    return True

def sync(dry_run: bool = False, local_only: bool = False, remote_only: bool = False):
    """Main sync function"""
    log("=" * 50)
    log("Starting project sync...")

    local_projects = load_local_projects()
    supabase_projects = fetch_supabase_projects()

    log(f"Local projects: {len(local_projects)}")
    log(f"Supabase projects: {len(supabase_projects)}")

    local_ids = set(local_projects.keys())
    supabase_ids = set(supabase_projects.keys())

    # Projects only in local -> push to Supabase
    only_local = local_ids - supabase_ids
    # Projects only in Supabase -> add to local
    only_supabase = supabase_ids - local_ids
    # Projects in both -> check for updates (by updated_at if available)
    in_both = local_ids & supabase_ids

    pushed = 0
    pulled = 0

    if not remote_only and only_local:
        log(f"\nPushing {len(only_local)} local-only projects to Supabase:")
        for pid in only_local:
            if push_to_supabase(local_projects[pid], dry_run):
                pushed += 1

    if not local_only and only_supabase:
        log(f"\nAdding {len(only_supabase)} Supabase-only projects to local:")
        for pid in only_supabase:
            if add_to_local(supabase_projects[pid], local_projects, dry_run):
                pulled += 1

    # For projects in both, we could compare updated_at timestamps
    # For now, we'll skip updating existing projects (they're already synced)

    log(f"\nSync complete: {pushed} pushed, {pulled} pulled")
    log("=" * 50)

def main():
    parser = argparse.ArgumentParser(description="Sync projects between local JSON and Supabase")
    parser.add_argument("--dry-run", action="store_true", help="Show what would be synced without making changes")
    parser.add_argument("--local", action="store_true", help="Only push local -> Supabase")
    parser.add_argument("--remote", action="store_true", help="Only pull Supabase -> local")
    args = parser.parse_args()

    # Ensure log directory exists
    SYNC_LOG.parent.mkdir(parents=True, exist_ok=True)

    sync(
        dry_run=args.dry_run,
        local_only=args.local,
        remote_only=args.remote
    )

if __name__ == "__main__":
    main()
