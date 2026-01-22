#!/usr/bin/env python3
"""
Upload NotebookLM scraped data to Supabase.
"""

import json
import os
from pathlib import Path
from datetime import datetime
from dotenv import load_dotenv

# Load environment variables from parent directory
load_dotenv(Path(__file__).parent.parent / '.env')

SUPABASE_URL = os.getenv('SUPABASE_URL')
SUPABASE_KEY = os.getenv('SUPABASE_ANON_KEY')

def get_supabase_client():
    """Initialize Supabase client."""
    try:
        from supabase import create_client
        return create_client(SUPABASE_URL, SUPABASE_KEY)
    except ImportError:
        print("Error: supabase package not installed.")
        print("Install it with: pip install supabase")
        raise

def load_json(filepath: Path) -> list:
    """Load JSON file."""
    with open(filepath) as f:
        return json.load(f)

def upload_notebooks(client, notebooks: list) -> dict:
    """Upload notebooks to Supabase."""
    results = {"inserted": 0, "skipped": 0, "errors": []}

    for nb in notebooks:
        try:
            data = {
                "notebook_id": nb["notebook_id"],
                "title": nb["title"],
                "description": nb.get("description"),
                "topic_tags": nb.get("topic_tags", []),
                "source_count": nb.get("source_count"),
                "created_display": nb.get("created_display"),
                "first_seen_at": nb.get("first_seen_at"),
            }

            # Upsert (insert or update on conflict)
            response = client.table("notebooklm_notebooks").upsert(
                data,
                on_conflict="notebook_id"
            ).execute()

            results["inserted"] += 1
            print(f"  ✓ {nb['title'][:50]}...")

        except Exception as e:
            error_msg = str(e)
            if "duplicate" in error_msg.lower():
                results["skipped"] += 1
            else:
                results["errors"].append({"notebook": nb["title"], "error": error_msg})
                print(f"  ✗ {nb['title'][:50]}: {error_msg}")

    return results

def upload_assets(client, assets: list) -> dict:
    """Upload assets to Supabase."""
    results = {"inserted": 0, "skipped": 0, "errors": []}

    for asset in assets:
        try:
            # Extract source count from related_sources_titles if present
            source_count_display = None
            if asset.get("related_sources_titles"):
                source_count_display = asset["related_sources_titles"][0] if asset["related_sources_titles"] else None

            data = {
                "notebook_id": asset["notebook_id"],
                "asset_title": asset["asset_title"],
                "asset_type": asset["asset_type"],
                "description": asset.get("description"),
                "topics_inferred": asset.get("topics_inferred", []),
                "source_count_display": source_count_display,
                "created_display": asset.get("created_display"),
                "first_seen_at": asset.get("first_seen_at"),
            }

            # Upsert
            response = client.table("notebooklm_assets").upsert(
                data,
                on_conflict="notebook_id,asset_title,asset_type"
            ).execute()

            results["inserted"] += 1
            print(f"  ✓ [{asset['asset_type']}] {asset['asset_title'][:40]}...")

        except Exception as e:
            error_msg = str(e)
            if "duplicate" in error_msg.lower():
                results["skipped"] += 1
            else:
                results["errors"].append({"asset": asset["asset_title"], "error": error_msg})
                print(f"  ✗ {asset['asset_title'][:40]}: {error_msg}")

    return results

def main():
    if not SUPABASE_URL or not SUPABASE_KEY:
        print("Error: Missing SUPABASE_URL or SUPABASE_ANON_KEY in .env file")
        return

    print(f"Connecting to Supabase: {SUPABASE_URL}")
    client = get_supabase_client()

    # Load data
    script_dir = Path(__file__).parent
    notebooks = load_json(script_dir / "notebooks.json")
    assets = load_json(script_dir / "assets.json")

    print(f"\nFound {len(notebooks)} notebooks and {len(assets)} assets")

    # Upload notebooks
    print(f"\n{'='*60}")
    print("Uploading notebooks...")
    print('='*60)
    nb_results = upload_notebooks(client, notebooks)
    print(f"\nNotebooks: {nb_results['inserted']} inserted, {nb_results['skipped']} skipped, {len(nb_results['errors'])} errors")

    # Upload assets
    print(f"\n{'='*60}")
    print("Uploading assets...")
    print('='*60)
    asset_results = upload_assets(client, assets)
    print(f"\nAssets: {asset_results['inserted']} inserted, {asset_results['skipped']} skipped, {len(asset_results['errors'])} errors")

    print(f"\n{'='*60}")
    print("Upload complete!")
    print('='*60)

if __name__ == "__main__":
    main()
