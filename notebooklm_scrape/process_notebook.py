#!/usr/bin/env python3
"""
Process and save notebook data scraped from NotebookLM.
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

def update_notebook(notebook_id, updates):
    """Update a notebook entry with new data."""
    notebooks = load_json("notebooks.json")
    for nb in notebooks:
        if nb.get("notebook_id") == notebook_id or nb.get("title") == updates.get("title"):
            nb.update(updates)
            break
    save_json("notebooks.json", notebooks)

def add_sources(sources_list):
    """Add sources to sources.json, avoiding duplicates."""
    existing = load_json("sources.json")
    existing_keys = {(s.get("notebook_id"), s.get("source_title")) for s in existing}

    for source in sources_list:
        key = (source.get("notebook_id"), source.get("source_title"))
        if key not in existing_keys:
            existing.append(source)
            existing_keys.add(key)

    save_json("sources.json", existing)
    return len(sources_list)

def add_assets(assets_list):
    """Add assets to assets.json, avoiding duplicates."""
    existing = load_json("assets.json")
    existing_keys = {(a.get("notebook_id"), a.get("asset_title")) for a in existing}

    for asset in assets_list:
        key = (asset.get("notebook_id"), asset.get("asset_title"))
        if key not in existing_keys:
            existing.append(asset)
            existing_keys.add(key)

    save_json("assets.json", existing)
    return len(assets_list)

def log_progress(message):
    """Append to progress log."""
    path = os.path.join(SCRAPE_DIR, "progress.log")
    timestamp = get_timestamp()
    with open(path, 'a') as f:
        f.write(f"{timestamp} - {message}\n")

# Data for first notebook: Work, Wealth, and Automation
NOTEBOOK_1 = {
    "notebook_id": "a8e34a7e-bb2d-47b3-8356-3228b22464dd",
    "title": "Work, Wealth, and Automation: Navigating the New Social Question",
    "source_count": 79,
    "description": "These sources examine the complex intersection of artificial intelligence, automation, and the future of global labour markets. Research indicates that while AI can significantly boost productivity, it also risks displacing workers across both routine and high-skilled occupations, potentially necessitating radical shifts in social policy. Proposed solutions include Universal Basic Income (UBI), Negative Income Tax, and job guarantees, though these face significant hurdles regarding financing, political feasibility, and administrative implementation.",
    "topic_tags": ["artificial intelligence", "automation", "global labour markets", "productivity", "social policy", "Universal Basic Income (UBI)", "Negative Income Tax", "job guarantees", "Engels' Pause", "human rights implications"]
}

SOURCES_1 = [
    {"source_title": "Deep Research report: The Great Decoupling: Cognitive Automation, Labor Displacement, and the Reconfiguration of Work", "source_type": "markdown"},
    {"source_title": "Scenario planning for an A(G)I future by Anton Korinek - Paris School of Economics", "source_type": "web"},
    {"source_title": "(PDF) The Political Economy of Universal Basic Income - ResearchGate", "source_type": "web"},
    {"source_title": "A Negative Income Tax for the 21st Century - Oshan Jarow", "source_type": "web"},
    {"source_title": "A Proactive Response to AI-Driven Job Displacement | Mercatus Center", "source_type": "web"},
    {"source_title": "AI Will Transform the Global Economy. Let's Make Sure It Benefits...", "source_type": "web"},
    {"source_title": "AI and the Future of Work: Assessing the Human Rights Implications of Job Displacement", "source_type": "web"},
    {"source_title": "AI, universal basic income, and power: symbolic violence in the tech elite's narrative - PMC", "source_type": "web"},
    {"source_title": "Artificial Intelligence, Automation and Work - NBER", "source_type": "pdf"},
    {"source_title": "Automation and New Tasks: How Technology Displaces and Reinstates Labor", "source_type": "web"},
    {"source_title": "Automation and New Tasks: How Technology Displaces and Reinstates Labor - MIT Economics", "source_type": "pdf"},
    {"source_title": "Automation and New Tasks: How Technology Displaces and Reinstates Labor | Concetti Contrastivi", "source_type": "pdf"},
    {"source_title": "Automation as Retaliation: Technology Adoption During Economic Strikes - OnLabor", "source_type": "web"},
    {"source_title": "Automation, AI & Work | American Academy of Arts and Sciences", "source_type": "web"},
    {"source_title": "BEHAVIORAL RESPONSES TO TAXES: LESSONS FROM THE EITC AND LABOR SUPPLY", "source_type": "pdf"},
    {"source_title": "Basic Income, Automation, and Labour Market Change - University of Bath", "source_type": "pdf"},
    {"source_title": "Center for Full Employment and Price Stability Research Archive Job or Income Guarantee?", "source_type": "pdf"},
    {"source_title": "Chapter: 3 Artificial Intelligence and Productivity - National Academies of Sciences", "source_type": "web"},
    {"source_title": "DOL Issues Framework to Guide Employers Using AI Recruiting and Hiring Tools", "source_type": "web"},
    {"source_title": "Disruption and Civil Unrest: The Role of AGI in Shaping Future Conflicts in the 2025-2035 decade", "source_type": "web"},
    {"source_title": "Engels' pause: Technical change, capital... - Nuffield College", "source_type": "pdf"},
    {"source_title": "Exploring Universal Basic Income: A Guide to Navigating Concepts...", "source_type": "pdf"},
    {"source_title": "Future Protest Made Risky: Examining Social Media Based Civil Unrest Prediction Research and Production", "source_type": "web"},
    {"source_title": "Future of Work with AI Agents: Auditing Automation and Augmentation Potential across the U.S. Workforce", "source_type": "web"},
    {"source_title": "Generative Artificial Intelligence Shatters Models of AI and Labor - arXiv", "source_type": "pdf"},
    {"source_title": "Governance of Generative AI | Policy and Society - Oxford Academic", "source_type": "web"},
    {"source_title": "Guaranteed Jobs: Too Big to Succeed - Progressive Policy Institute", "source_type": "pdf"},
    {"source_title": "History says AI will boost productivity, wages and employment - CIPD Community", "source_type": "web"},
    {"source_title": "How 2025 Will Change the Future of Work - Newsweek", "source_type": "web"},
    {"source_title": "Industrial Policy for Emerging Technologies: The Case of Narrow AI and the Manufacturing Value Chain", "source_type": "pdf"},
    {"source_title": "Is automation labor-displacing? Productivity growth, employment, and the labor share - Brookings", "source_type": "pdf"},
    {"source_title": "Is the EITC as Good as an NIT? Conditional Cash Transfers and Tax Incidence", "source_type": "pdf"},
    {"source_title": "Lessons for the AI Revolution from the Industrial Revolution - Innovation Vista", "source_type": "web"},
    {"source_title": "Machine learning will redesign, not replace, work | MIT Sloan", "source_type": "web"},
    {"source_title": "Navigating Uncertain Times - A Scenario Planning Toolkit for the Arts & Culture Sector", "source_type": "pdf"},
    {"source_title": "No, AI won't take all the jobs. Here's why. - Freethink Media", "source_type": "web"},
    {"source_title": "Preparing workers for AI: new report highlights policy gaps and solutions", "source_type": "web"},
    {"source_title": "Q&A | AI and the Future of Work with Erik Brynjolfsson and Tom Mitchell", "source_type": "web"},
    {"source_title": "Robots and Jobs: Evidence from US Labor Markets - IDEAS/RePEc", "source_type": "web"},
    {"source_title": "Robots and Jobs: Evidence from US Labor Markets - NBER", "source_type": "pdf"},
    {"source_title": "SCENARIO PLANNING FOR AN A(G)I FUTURE", "source_type": "pdf"},
    {"source_title": "Sam Altman and Bill Gale on Taxation Solutions for Advanced AI | GovAI Blog", "source_type": "web"},
    {"source_title": "Scenario Planning for an A(G)I Future - SCOR Foundation", "source_type": "pdf"},
    {"source_title": "Scenario Planning for an AGI Future-Anton Korinek - International Monetary Fund", "source_type": "web"},
    {"source_title": "Scenarios for the Transition to AGI - NBER", "source_type": "pdf"},
    {"source_title": "Senators Weigh Whether AI Can Shorten the Workweek - Legal.io", "source_type": "web"},
    {"source_title": "Social question - Wikipedia", "source_type": "web"},
    {"source_title": "THE SOCIO-ECONOMIC IMPLICATIONS OF AUTOMATION: NIT AND UBI AS ALTERNATIVE POLICY RESPONSES", "source_type": "pdf"},
    {"source_title": "Technological unemployment - Wikipedia", "source_type": "web"},
    {"source_title": "The AI Economy Is Here: Layoffs, Shorter Work Weeks, and the Race to Automate Work", "source_type": "web"},
    {"source_title": "The Earned Income Tax Credit (EITC) - The University of North Carolina at Chapel Hill", "source_type": "pdf"},
    {"source_title": "The Earned Income Tax Credit and Occupational Skill Mismatch - American Economic Association", "source_type": "pdf"},
    {"source_title": "The Federal Job Guarantee - Intereconomics", "source_type": "web"},
    {"source_title": "The Labor Market Impacts of Technological Change: From Unbridled Enthusiasm to Qualified Optimism", "source_type": "pdf"},
    {"source_title": "The Past and Future of Work: How History Can Inform the Age of Automation - ifo Institut", "source_type": "pdf"},
    {"source_title": "The Problem With a Job Guarantee - Dissent Magazine", "source_type": "web"},
    {"source_title": "The Shortened Working Week and Its Impact on Workplace Sustainability - SGH Journals", "source_type": "pdf"},
    {"source_title": "The United States ought to provide a federal jobs guarantee. DEFINITIONS", "source_type": "pdf"},
    {"source_title": "The job guarantee: MMT's proposal for full employment and price stability - EconStor", "source_type": "pdf"},
    {"source_title": "US Department of Labor announces framework to help employers promote inclusive hiring as AI-powered tools", "source_type": "web"},
    {"source_title": "Universal basic income as a new social contract for the age of AI - LSE Business Review", "source_type": "web"},
    {"source_title": "Unleashing possibilities, ignoring risks: Why we need tools to manage AI's impact on jobs", "source_type": "web"},
    {"source_title": "Using AI as a weapon of repression and its impact on human rights - European Parliament", "source_type": "pdf"},
    {"source_title": "What Can Machines Learn, and What Does It Mean for Occupations and the Economy?", "source_type": "web"},
    {"source_title": "What Does the Debate on Automation Mean for Basic Income...", "source_type": "web"},
    {"source_title": "What Job Displacement Scenario Do you Think is Most Likely? : r/singularity - Reddit", "source_type": "web"},
    {"source_title": "What we know and what we don't about universal basic income | World Economic Forum", "source_type": "web"},
    {"source_title": "Why Universal Basic Income Is a Bad Idea - Free", "source_type": "pdf"},
    {"source_title": "acemoglu-restrepo-2019-automation-and-new-tasks-how...", "source_type": "pdf"},
]

ASSETS_1 = [
    {
        "asset_title": "Automation Shock and the Post-Work Transition",
        "asset_type": "audio",
        "description": "Deep dive into automation and post-work transition",
        "play_or_download_target": None,
        "topics_inferred": ["automation", "post-work", "AI", "labor displacement"],
        "related_sources_titles": ["71 sources used"],
        "created_display": "34m ago",
        "updated_display": None,
    },
    {
        "asset_title": "Universal Basic Income vs The Jobless Future",
        "asset_type": "audio",
        "description": "Debate format audio overview",
        "play_or_download_target": None,
        "topics_inferred": ["UBI", "jobless future", "policy debate"],
        "related_sources_titles": ["71 sources used"],
        "created_display": "35m ago",
        "updated_display": None,
    }
]

if __name__ == "__main__":
    timestamp = get_timestamp()
    notebook_id = NOTEBOOK_1["notebook_id"]

    # Update notebook
    notebooks = load_json("notebooks.json")
    for nb in notebooks:
        if "work-wealth-and-automation" in nb.get("notebook_id", "").lower() or \
           nb.get("title", "").startswith("Work, Wealth, and Automation"):
            nb["notebook_id"] = notebook_id
            nb["description"] = NOTEBOOK_1["description"]
            nb["topic_tags"] = NOTEBOOK_1["topic_tags"]
            nb["source_count"] = NOTEBOOK_1["source_count"]
            break
    save_json("notebooks.json", notebooks)

    # Add sources
    sources_to_add = []
    for s in SOURCES_1:
        sources_to_add.append({
            "notebook_id": notebook_id,
            "source_title": s["source_title"],
            "source_type": s["source_type"],
            "source_url": None,
            "extra_metadata": None,
            "created_display": None,
            "updated_display": None,
            "first_seen_at": timestamp
        })
    num_sources = add_sources(sources_to_add)

    # Add assets
    assets_to_add = []
    for a in ASSETS_1:
        assets_to_add.append({
            "notebook_id": notebook_id,
            "asset_title": a["asset_title"],
            "asset_type": a["asset_type"],
            "description": a["description"],
            "play_or_download_target": a["play_or_download_target"],
            "topics_inferred": a["topics_inferred"],
            "related_sources_titles": a["related_sources_titles"],
            "created_display": a["created_display"],
            "updated_display": a["updated_display"],
            "first_seen_at": timestamp
        })
    num_assets = add_assets(assets_to_add)

    log_progress(f'scraped notebook "Work, Wealth, and Automation" with {num_sources} sources and {num_assets} assets.')
    print(f"Processed notebook: Work, Wealth, and Automation")
    print(f"  - {num_sources} sources added")
    print(f"  - {num_assets} assets added")
