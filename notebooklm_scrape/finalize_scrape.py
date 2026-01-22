#!/usr/bin/env python3
"""
Finalize the NotebookLM scrape by updating all notebook IDs and validating JSON files.
"""
import json
import os
from datetime import datetime, timezone

SCRAPE_DIR = "/Users/z/Desktop/PersonalProjects/ClaudeProjects/notebooklm_scrape"

# Notebook IDs collected from browser scraping
NOTEBOOK_IDS = {
    "Work, Wealth, and Automation: Navigating the New Social Question": "a8e34a7e-bb2d-47b3-8356-3228b22464dd",
    "Urban Imaginings and the Aesthetics of Design": "b9eba7aa-1a19-45a1-8807-aed8ca61c396",
    "Patterns and Thresholds of Cosmic and Human History": "d832d9c4-ba5d-40dc-b9ef-c4eebb34263e",
    "Materials and Commodities: Shaping Human History and the Environment": "ce87dcca-5698-4987-97d2-0c38162b87ed",
    "Power and Prestige of the Ancien Régime": "cdfce2fe-1e01-4f64-ae89-91b316865770",
    "The Shift to In Silico Medicine: Ending Animal Testing": "b005fd54-85b3-4b34-af3a-a8260b35c217",
    "raising exceptional children": "27e177f7-b331-4150-b0b6-caa442abd293",
}

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

def generate_notebook_id(title):
    """Generate a stable slug-based ID from the title for notebooks without scraped IDs."""
    slug = title.lower().replace(" ", "-").replace(":", "").replace(",", "").replace("'", "").replace("é", "e")
    return f"slug-{slug[:50]}"

def finalize_notebooks():
    """Update notebooks with collected IDs and ensure consistency."""
    notebooks = load_json("notebooks.json")

    for nb in notebooks:
        title = nb.get("title", "")
        # Update with scraped ID if available
        if title in NOTEBOOK_IDS:
            nb["notebook_id"] = NOTEBOOK_IDS[title]
        # Ensure notebook has an ID (generate if missing)
        elif not nb.get("notebook_id") or nb["notebook_id"].startswith("slug-") == False:
            if not nb.get("notebook_id"):
                nb["notebook_id"] = generate_notebook_id(title)

    save_json("notebooks.json", notebooks)
    return notebooks

def validate_json_files():
    """Validate that all JSON files are properly formatted."""
    files = ["notebooks.json", "sources.json", "assets.json"]
    results = {}

    for filename in files:
        path = os.path.join(SCRAPE_DIR, filename)
        try:
            with open(path, 'r') as f:
                data = json.load(f)
            results[filename] = {"valid": True, "count": len(data)}
        except Exception as e:
            results[filename] = {"valid": False, "error": str(e)}

    return results

def print_summary():
    """Print a comprehensive summary of the scrape."""
    notebooks = load_json("notebooks.json")
    sources = load_json("sources.json")
    assets = load_json("assets.json")

    # Count audio assets
    audio_assets = [a for a in assets if a.get("asset_type") == "audio"]
    audio_with_timestamp = [a for a in audio_assets if a.get("created_display") or a.get("first_seen_at")]

    # Count notebooks with real IDs
    real_id_notebooks = [n for n in notebooks if n.get("notebook_id") and not n["notebook_id"].startswith("slug-")]

    print("=" * 60)
    print("NOTEBOOKLM SCRAPE SUMMARY")
    print("=" * 60)
    print(f"\nNotebooks discovered: {len(notebooks)}")
    print(f"  - With real IDs from browser: {len(real_id_notebooks)}")
    print(f"  - With generated IDs: {len(notebooks) - len(real_id_notebooks)}")
    print(f"\nSources collected: {len(sources)}")
    print(f"Assets collected: {len(assets)}")
    print(f"  - Audio assets: {len(audio_assets)}")
    print(f"  - Audio with timestamps: {len(audio_with_timestamp)}")

    print("\n" + "-" * 60)
    print("NOTEBOOKS LIST:")
    print("-" * 60)
    for i, nb in enumerate(notebooks, 1):
        id_type = "browser" if nb.get("notebook_id") and not nb["notebook_id"].startswith("slug-") else "generated"
        print(f"{i:2}. {nb['title'][:55]}...")
        print(f"    Sources: {nb.get('source_count', 'N/A')} | ID: {id_type} | Date: {nb.get('created_display', 'N/A')}")

    print("\n" + "=" * 60)
    print("FILES CREATED:")
    print("=" * 60)
    for filename in ["notebooks.json", "sources.json", "assets.json", "progress.log"]:
        path = os.path.join(SCRAPE_DIR, filename)
        if os.path.exists(path):
            size = os.path.getsize(path)
            print(f"  {filename}: {size:,} bytes")

    return {
        "notebooks": len(notebooks),
        "sources": len(sources),
        "assets": len(assets),
        "audio_assets": len(audio_assets),
        "audio_with_timestamps": len(audio_with_timestamp)
    }

if __name__ == "__main__":
    print("Finalizing NotebookLM scrape...")

    # Update notebooks with collected IDs
    notebooks = finalize_notebooks()
    print(f"Updated {len(notebooks)} notebooks")

    # Validate JSON files
    validation = validate_json_files()
    all_valid = all(v["valid"] for v in validation.values())
    print(f"JSON validation: {'PASSED' if all_valid else 'FAILED'}")

    # Print summary
    summary = print_summary()

    # Log completion
    log_progress(f"Scrape finalized: {summary['notebooks']} notebooks, {summary['sources']} sources, {summary['assets']} assets")
