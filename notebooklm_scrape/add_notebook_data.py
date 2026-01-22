#!/usr/bin/env python3
"""
Add scraped notebook data to JSON files.
Usage: python add_notebook_data.py '<json_data>'
"""
import json
import sys
import os
from datetime import datetime, timezone

SCRAPE_DIR = "/Users/z/Desktop/PersonalProjects/ClaudeProjects/notebooklm_scrape"

def get_timestamp():
    return datetime.now(timezone.utc).isoformat().replace('+00:00', 'Z')

def load_json(filename):
    path = os.path.join(SCRAPE_DIR, filename)
    if os.path.exists(path):
        with open(path, 'r') as f:
            return json.load(f)
    return []

def save_json(filename, data):
    path = os.path.join(SCRAPE_DIR, filename)
    with open(path, 'w') as f:
        json.dump(data, f, indent=2, ensure_ascii=False)

def log_progress(message):
    path = os.path.join(SCRAPE_DIR, "progress.log")
    timestamp = get_timestamp()
    with open(path, 'a') as f:
        f.write(f"{timestamp} - {message}\n")

def add_notebook_data(data):
    """Add notebook, sources, and assets data."""
    timestamp = get_timestamp()
    notebook_id = data.get("notebook_id")
    title = data.get("title")

    # Update notebooks.json
    notebooks = load_json("notebooks.json")
    found = False
    for nb in notebooks:
        # Match by title prefix since we generated IDs differently initially
        if nb.get("title", "").startswith(title[:30]) or nb.get("notebook_id") == notebook_id:
            nb["notebook_id"] = notebook_id
            nb["description"] = data.get("description")
            nb["topic_tags"] = data.get("topic_tags", [])
            nb["source_count"] = data.get("source_count")
            found = True
            break

    if not found:
        notebooks.append({
            "notebook_id": notebook_id,
            "title": title,
            "description": data.get("description"),
            "topic_tags": data.get("topic_tags", []),
            "source_count": data.get("source_count"),
            "created_display": data.get("created_display"),
            "updated_display": None,
            "first_seen_at": timestamp
        })

    save_json("notebooks.json", notebooks)

    # Add sources
    existing_sources = load_json("sources.json")
    existing_keys = {(s.get("notebook_id"), s.get("source_title")) for s in existing_sources}

    sources_added = 0
    for source in data.get("sources", []):
        key = (notebook_id, source.get("source_title"))
        if key not in existing_keys:
            existing_sources.append({
                "notebook_id": notebook_id,
                "source_title": source.get("source_title"),
                "source_type": source.get("source_type", "web"),
                "source_url": source.get("source_url"),
                "extra_metadata": source.get("extra_metadata"),
                "created_display": source.get("created_display"),
                "updated_display": source.get("updated_display"),
                "first_seen_at": timestamp
            })
            existing_keys.add(key)
            sources_added += 1

    save_json("sources.json", existing_sources)

    # Add assets
    existing_assets = load_json("assets.json")
    existing_asset_keys = {(a.get("notebook_id"), a.get("asset_title")) for a in existing_assets}

    assets_added = 0
    for asset in data.get("assets", []):
        key = (notebook_id, asset.get("asset_title"))
        if key not in existing_asset_keys:
            existing_assets.append({
                "notebook_id": notebook_id,
                "asset_title": asset.get("asset_title"),
                "asset_type": asset.get("asset_type", "audio"),
                "description": asset.get("description"),
                "play_or_download_target": asset.get("play_or_download_target"),
                "topics_inferred": asset.get("topics_inferred", []),
                "related_sources_titles": asset.get("related_sources_titles", []),
                "created_display": asset.get("created_display"),
                "updated_display": asset.get("updated_display"),
                "first_seen_at": timestamp
            })
            existing_asset_keys.add(key)
            assets_added += 1

    save_json("assets.json", existing_assets)

    log_progress(f'scraped notebook "{title}" with {sources_added} sources and {assets_added} assets.')

    return {
        "notebook": title,
        "sources_added": sources_added,
        "assets_added": assets_added
    }

if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Usage: python add_notebook_data.py '<json_data>'")
        sys.exit(1)

    try:
        data = json.loads(sys.argv[1])
        result = add_notebook_data(data)
        print(f"Processed: {result['notebook']}")
        print(f"  Sources added: {result['sources_added']}")
        print(f"  Assets added: {result['assets_added']}")
    except json.JSONDecodeError as e:
        print(f"Error parsing JSON: {e}")
        sys.exit(1)
