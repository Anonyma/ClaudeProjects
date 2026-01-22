#!/usr/bin/env python3
"""
Batch add all remaining notebook data from the initial DOM scrape.
This adds basic metadata for notebooks that haven't been fully scraped yet.
"""
import json
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

# All notebooks from initial DOM scrape with their metadata
ALL_NOTEBOOKS = [
    {"title": "Work, Wealth, and Automation: Navigating the New Social Question", "sources": 71, "date": "19 Jan 2026", "notebook_id": "a8e34a7e-bb2d-47b3-8356-3228b22464dd"},
    {"title": "Urban Imaginings and the Aesthetics of Design", "sources": 89, "date": "13 Jan 2026", "notebook_id": "b9eba7aa-1a19-45a1-8807-aed8ca61c396"},
    {"title": "Patterns and Thresholds of Cosmic and Human History", "sources": 52, "date": "19 Jan 2026", "notebook_id": "d832d9c4-ba5d-40dc-b9ef-c4eebb34263e"},
    {"title": "Materials and Commodities: Shaping Human History and the Environment", "sources": 73, "date": "17 Jan 2026", "notebook_id": "ce87dcca-5698-4987-97d2-0c38162b87ed"},
    {"title": "Power and Prestige of the Ancien Régime", "sources": 58, "date": "17 Jan 2026", "notebook_id": "cdfce2fe-1e01-4f64-ae89-91b316865770"},
    {"title": "The Shift to In Silico Medicine: Ending Animal Testing", "sources": 17, "date": "22 Aug 2025"},
    {"title": "raising exceptional children", "sources": 28, "date": "9 Jan 2026"},
    {"title": "Cognitive Plasticity and Occupational Complexity in Aging Research", "sources": 85, "date": "9 Jan 2026"},
    {"title": "Metabolic Pathways, Aging, and Longevity", "sources": 10, "date": "3 Aug 2025"},
    {"title": "Fetal Cells Repair Maternal Heart after Injury", "sources": 24, "date": "16 Dec 2025"},
    {"title": "Vienna: A Legacy of Art, History, and Culture", "sources": 25, "date": "15 Jan 2026"},
    {"title": "Transformers ML AI", "sources": 9, "date": "9 Jan 2026"},
    {"title": "Systems Thinking and the Dynamics of Complex Networks", "sources": 39, "date": "15 Jan 2026"},
    {"title": "Evolution and Identity in the East Slavic World", "sources": 45, "date": "15 Jan 2026"},
    {"title": "China biotech", "sources": 10, "date": "9 Jan 2026"},
    {"title": "Advances in Nucleic Acid Gene Therapies", "sources": 23, "date": "11 Sep 2025"},
    {"title": "Cellular Reprogramming: Advancing Longevity and Health", "sources": 36, "date": "11 Sep 2025"},
    {"title": "Gene Therapies: Advancements, Challenges, and Future Prospects", "sources": 16, "date": "19 Aug 2025"},
    {"title": "Targeting Amyloidogenesis: Therapies and Mechanisms", "sources": 18, "date": "1 Sep 2025"},
    {"title": "Mitochondrial Medicine: Therapies and Innovations", "sources": 23, "date": "19 Aug 2025"},
    {"title": "RNA Editing: Expanding Gene Therapy's Horizons", "sources": 25, "date": "20 Aug 2025"},
    {"title": "HeLa Cells: Cultivation, Applications, and Milestones", "sources": 7, "date": "15 Aug 2025"},
    {"title": "Culturing and Clinical Application of iPSCs", "sources": 23, "date": "20 Aug 2025"},
    {"title": "Longevity Research Project Portfolio: Cost-Effective Approaches", "sources": 11, "date": "15 Aug 2025"},
    {"title": "Red Blood Cells: Next-Gen Therapy and Drug Delivery", "sources": 9, "date": "6 Aug 2025"},
    {"title": "Artificial Wombs: Technology, Ethics, and Future of Reproduction", "sources": 10, "date": "11 Aug 2025"},
    {"title": "Revolutionizing Medicine: Nanoparticle and Oligonucleotide Therapies", "sources": 9, "date": "3 Aug 2025"},
]

def generate_notebook_id(title):
    """Generate a stable slug-based ID from the title."""
    return title.lower().replace(" ", "-").replace(":", "").replace(",", "").replace("'", "").replace("é", "e")[:60]

def update_all_notebooks():
    """Update notebooks.json with all notebook metadata."""
    timestamp = get_timestamp()
    notebooks = load_json("notebooks.json")
    existing_titles = {nb.get("title") for nb in notebooks}

    added = 0
    for nb_data in ALL_NOTEBOOKS:
        title = nb_data["title"]
        if title not in existing_titles:
            notebook_id = nb_data.get("notebook_id") or generate_notebook_id(title)
            notebooks.append({
                "notebook_id": notebook_id,
                "title": title,
                "description": None,
                "topic_tags": [],
                "source_count": nb_data["sources"],
                "created_display": nb_data["date"],
                "updated_display": None,
                "first_seen_at": timestamp
            })
            added += 1
        else:
            # Update existing notebook with notebook_id if available
            if nb_data.get("notebook_id"):
                for nb in notebooks:
                    if nb.get("title") == title:
                        nb["notebook_id"] = nb_data["notebook_id"]
                        break

    save_json("notebooks.json", notebooks)
    return added

if __name__ == "__main__":
    added = update_all_notebooks()
    log_progress(f"Batch update: ensured all {len(ALL_NOTEBOOKS)} notebooks are in notebooks.json")
    print(f"Notebooks updated: {added} new entries added")
    print(f"Total notebooks in database: {len(ALL_NOTEBOOKS)}")
