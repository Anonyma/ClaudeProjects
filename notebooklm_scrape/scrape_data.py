#!/usr/bin/env python3
"""
NotebookLM scrape data processing script.
Processes raw DOM data into structured JSON files.
"""
import json
import os
from datetime import datetime

SCRAPE_DIR = "/Users/z/Desktop/PersonalProjects/ClaudeProjects/notebooklm_scrape"

# Initial notebook data extracted from DOM (from read_page tool output)
RAW_NOTEBOOKS = [
    {"title": "Work, Wealth, and Automation: Navigating the New Social Question", "sources": 71, "date_raw": "Mon Jan 19 2026 01:13:17 GMT+0100 (Central European Standard Time)", "ref": "ref_41"},
    {"title": "Urban Imaginings and the Aesthetics of Design", "sources": 89, "date_raw": "Tue Jan 13 2026 21:19:36 GMT+0100 (Central European Standard Time)", "ref": "ref_47"},
    {"title": "Patterns and Thresholds of Cosmic and Human History", "sources": 52, "date_raw": "Mon Jan 19 2026 01:31:54 GMT+0100 (Central European Standard Time)", "ref": "ref_53"},
    {"title": "Materials and Commodities: Shaping Human History and the Environment", "sources": 73, "date_raw": "Sat Jan 17 2026 08:33:31 GMT+0100 (Central European Standard Time)", "ref": "ref_59"},
    {"title": "Power and Prestige of the Ancien Régime", "sources": 58, "date_raw": "Sat Jan 17 2026 08:25:30 GMT+0100 (Central European Standard Time)", "ref": "ref_65"},
    {"title": "The Shift to In Silico Medicine: Ending Animal Testing", "sources": 17, "date_raw": "Fri Aug 22 2025 13:51:43 GMT+0200 (Central European Summer Time)", "ref": "ref_71"},
    {"title": "raising exceptional children", "sources": 28, "date_raw": "Fri Jan 09 2026 16:20:32 GMT+0100 (Central European Standard Time)", "ref": "ref_77"},
    {"title": "Cognitive Plasticity and Occupational Complexity in Aging Research", "sources": 85, "date_raw": "Fri Jan 09 2026 16:23:41 GMT+0100 (Central European Standard Time)", "ref": "ref_83"},
    {"title": "Metabolic Pathways, Aging, and Longevity", "sources": 10, "date_raw": "Sun Aug 03 2025 21:58:34 GMT+0200 (Central European Summer Time)", "ref": "ref_89"},
    {"title": "Fetal Cells Repair Maternal Heart after Injury", "sources": 24, "date_raw": "Tue Dec 16 2025 04:43:22 GMT+0100 (Central European Standard Time)", "ref": "ref_95"},
    {"title": "Vienna: A Legacy of Art, History, and Culture", "sources": 25, "date_raw": "Thu Jan 15 2026 10:33:32 GMT+0100 (Central European Standard Time)", "ref": "ref_102"},
    {"title": "Transformers ML AI", "sources": 9, "date_raw": "Fri Jan 09 2026 13:27:41 GMT+0100 (Central European Standard Time)", "ref": "ref_108"},
    {"title": "Systems Thinking and the Dynamics of Complex Networks", "sources": 39, "date_raw": "Thu Jan 15 2026 19:58:55 GMT+0100 (Central European Standard Time)", "ref": "ref_114"},
    {"title": "Evolution and Identity in the East Slavic World", "sources": 45, "date_raw": "Thu Jan 15 2026 09:56:44 GMT+0100 (Central European Standard Time)", "ref": "ref_121"},
    {"title": "China biotech", "sources": 10, "date_raw": "Fri Jan 09 2026 15:55:59 GMT+0100 (Central European Standard Time)", "ref": "ref_127"},
    {"title": "Advances in Nucleic Acid Gene Therapies", "sources": 23, "date_raw": "Thu Sep 11 2025 17:52:28 GMT+0200 (Central European Summer Time)", "ref": "ref_133"},
    {"title": "Cellular Reprogramming: Advancing Longevity and Health", "sources": 36, "date_raw": "Thu Sep 11 2025 17:54:49 GMT+0200 (Central European Summer Time)", "ref": "ref_139"},
    {"title": "Gene Therapies: Advancements, Challenges, and Future Prospects", "sources": 16, "date_raw": "Tue Aug 19 2025 13:22:30 GMT+0200 (Central European Summer Time)", "ref": "ref_145"},
    {"title": "Targeting Amyloidogenesis: Therapies and Mechanisms", "sources": 18, "date_raw": "Mon Sep 01 2025 23:00:17 GMT+0200 (Central European Summer Time)", "ref": "ref_151"},
    {"title": "Mitochondrial Medicine: Therapies and Innovations", "sources": 23, "date_raw": "Tue Aug 19 2025 13:28:54 GMT+0200 (Central European Summer Time)", "ref": "ref_157"},
    {"title": "RNA Editing: Expanding Gene Therapy's Horizons", "sources": 25, "date_raw": "Wed Aug 20 2025 19:52:51 GMT+0200 (Central European Summer Time)", "ref": "ref_163"},
    {"title": "HeLa Cells: Cultivation, Applications, and Milestones", "sources": 7, "date_raw": "Fri Aug 15 2025 15:21:16 GMT+0200 (Central European Summer Time)", "ref": "ref_169"},
    {"title": "Culturing and Clinical Application of iPSCs", "sources": 23, "date_raw": "Wed Aug 20 2025 19:48:04 GMT+0200 (Central European Summer Time)", "ref": "ref_175"},
    {"title": "Longevity Research Project Portfolio: Cost-Effective Approaches", "sources": 11, "date_raw": "Fri Aug 15 2025 15:14:51 GMT+0200 (Central European Summer Time)", "ref": "ref_181"},
    {"title": "Red Blood Cells: Next-Gen Therapy and Drug Delivery", "sources": 9, "date_raw": "Wed Aug 06 2025 23:56:52 GMT+0200 (Central European Summer Time)", "ref": "ref_187"},
    {"title": "Artificial Wombs: Technology, Ethics, and Future of Reproduction", "sources": 10, "date_raw": "Mon Aug 11 2025 12:31:48 GMT+0200 (Central European Summer Time)", "ref": "ref_193"},
    {"title": "Revolutionizing Medicine: Nanoparticle and Oligonucleotide Therapies", "sources": 9, "date_raw": "Sun Aug 03 2025 21:31:22 GMT+0200 (Central European Summer Time)", "ref": "ref_199"},
]

def generate_notebook_id(title):
    """Generate a stable ID from the title."""
    return title.lower().replace(" ", "-").replace(":", "").replace(",", "").replace("'", "")[:60]

def parse_date_display(date_raw):
    """Extract display date from raw date string."""
    # Example: "Mon Jan 19 2026 01:13:17 GMT+0100 (Central European Standard Time)"
    # Return something like "19 Jan 2026"
    parts = date_raw.split()
    if len(parts) >= 4:
        day = parts[2]
        month = parts[1]
        year = parts[3]
        return f"{day} {month} {year}"
    return date_raw

def create_notebooks_json():
    """Create the notebooks.json file."""
    notebooks = []
    for nb in RAW_NOTEBOOKS:
        notebooks.append({
            "notebook_id": generate_notebook_id(nb["title"]),
            "title": nb["title"],
            "description": None,  # Will be updated when we visit each notebook
            "topic_tags": [],  # Will be updated when we visit each notebook
            "source_count": nb["sources"],
            "created_display": parse_date_display(nb["date_raw"]),
            "updated_display": None,
            "first_seen_at": datetime.utcnow().isoformat() + "Z"
        })

    output_path = os.path.join(SCRAPE_DIR, "notebooks.json")
    with open(output_path, "w") as f:
        json.dump(notebooks, f, indent=2)

    return notebooks

def init_sources_json():
    """Initialize empty sources.json file."""
    output_path = os.path.join(SCRAPE_DIR, "sources.json")
    with open(output_path, "w") as f:
        json.dump([], f, indent=2)

def init_assets_json():
    """Initialize empty assets.json file."""
    output_path = os.path.join(SCRAPE_DIR, "assets.json")
    with open(output_path, "w") as f:
        json.dump([], f, indent=2)

if __name__ == "__main__":
    notebooks = create_notebooks_json()
    init_sources_json()
    init_assets_json()
    print(f"Created notebooks.json with {len(notebooks)} notebooks")
    print("Initialized sources.json and assets.json")
