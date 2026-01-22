#!/usr/bin/env python3
"""
Playwright automation for NotebookLM daily sync.

Features:
- Persistent browser profile (keeps Google login)
- Incremental sync (only processes new notebooks/audio)
- Downloads audio files automatically
- Integrates with existing transcription pipeline

Usage:
    # First run - will open browser for you to login
    python playwright_sync.py --login

    # Daily sync (can run headless after login)
    python playwright_sync.py

    # Sync specific notebook
    python playwright_sync.py --notebook "Work, Wealth, and Automation"
"""

import os
import re
import json
import asyncio
import argparse
from pathlib import Path
from datetime import datetime
from dotenv import load_dotenv

load_dotenv(Path(__file__).parent.parent / '.env')

# Paths
SCRIPT_DIR = Path(__file__).parent
BROWSER_DATA_DIR = SCRIPT_DIR / ".playwright_profile"
AUDIO_DIR = SCRIPT_DIR / "notebooklm-audio"
DOWNLOADS_DIR = SCRIPT_DIR / "downloads_temp"

# Supabase
SUPABASE_URL = os.getenv('SUPABASE_URL')
SUPABASE_KEY = os.getenv('SUPABASE_ANON_KEY')


def get_supabase_client():
    from supabase import create_client
    return create_client(SUPABASE_URL, SUPABASE_KEY)


def get_known_notebooks(supabase) -> set:
    """Get notebook IDs we've already processed."""
    result = supabase.table("notebooklm_notebooks").select("notebook_id").execute()
    return {r["notebook_id"] for r in result.data}


def get_known_assets(supabase) -> set:
    """Get asset titles we've already processed."""
    result = supabase.table("notebooklm_assets").select("asset_title, notebook_id").execute()
    return {(r["notebook_id"], r["asset_title"]) for r in result.data}


def sanitize_filename(name: str) -> str:
    """Convert title to safe filename."""
    # Remove/replace problematic characters
    name = re.sub(r'[<>:"/\\|?*]', '', name)
    name = name.replace(' ', '_')
    return name[:80]  # Limit length


async def login_flow(page):
    """Interactive login - user logs in manually."""
    print("\n" + "=" * 60)
    print("LOGIN REQUIRED")
    print("=" * 60)
    print("1. A browser window has opened")
    print("2. Log into your Google account")
    print("3. Navigate to NotebookLM and ensure you see your notebooks")
    print("4. The script will auto-detect when you're logged in")
    print("=" * 60 + "\n")

    await page.goto("https://notebooklm.google.com")

    print("Waiting for login... (you have 2 minutes)")

    # Wait for notebooks to appear (indicates successful login)
    try:
        # Wait up to 2 minutes for login
        await page.wait_for_selector(
            'a[href*="/notebook/"], [class*="notebook"], [class*="ProjectCard"]',
            timeout=120000
        )
        print("\n✓ Login successful! Notebooks detected.")
        print("✓ Session saved to .playwright_profile/")

        # Give a moment for everything to settle
        await page.wait_for_timeout(2000)
        return True

    except Exception as e:
        print(f"\n✗ Login timed out or failed: {e}")
        print("Try running --login again")
        return False


async def get_notebook_list(page) -> list:
    """Scrape the notebook list from the main page."""
    await page.goto("https://notebooklm.google.com")
    await page.wait_for_timeout(3000)

    # Wait for notebooks to load
    await page.wait_for_selector('[class*="notebook"]', timeout=10000)

    notebooks = []

    # Get all notebook cards
    cards = await page.query_selector_all('[class*="ProjectCard"], [class*="notebook-card"], a[href*="/notebook/"]')

    for card in cards:
        try:
            # Get href to extract notebook ID
            href = await card.get_attribute("href")
            if href and "/notebook/" in href:
                notebook_id = href.split("/notebook/")[-1].split("?")[0]

                # Get title
                title_el = await card.query_selector('h2, h3, [class*="title"]')
                title = await title_el.inner_text() if title_el else "Unknown"

                # Get date if available
                date_el = await card.query_selector('[class*="date"], [class*="time"]')
                date = await date_el.inner_text() if date_el else None

                notebooks.append({
                    "notebook_id": notebook_id,
                    "title": title.strip(),
                    "date": date
                })
        except Exception as e:
            continue

    return notebooks


async def get_audio_overviews(page, notebook_id: str) -> list:
    """Get list of audio overviews in a notebook."""
    url = f"https://notebooklm.google.com/notebook/{notebook_id}"
    await page.goto(url)
    await page.wait_for_timeout(3000)

    audio_items = []

    # Look for audio items in the Studio panel
    # NotebookLM typically shows audio overviews with a waveform icon
    items = await page.query_selector_all('[class*="audio"], [class*="Audio"], [data-type="audio"]')

    # Also try to find items in the right panel
    studio_items = await page.query_selector_all('[class*="studio"] [class*="item"], [class*="Studio"] [class*="asset"]')

    for item in list(items) + list(studio_items):
        try:
            title_el = await item.query_selector('[class*="title"], h3, h4, span')
            if title_el:
                title = await title_el.inner_text()
                if title and len(title) > 3:
                    audio_items.append({
                        "title": title.strip(),
                        "element": item
                    })
        except:
            continue

    return audio_items


async def download_audio(page, audio_element, notebook_title: str, audio_title: str, download_dir: Path) -> Path | None:
    """Download an audio file from NotebookLM."""
    try:
        # Click on the audio item to open it
        await audio_element.click()
        await page.wait_for_timeout(2000)

        # Look for the three-dot menu on the audio player
        menu_button = await page.query_selector('[class*="player"] [class*="menu"], [class*="audio"] [class*="more"]')
        if menu_button:
            await menu_button.click()
            await page.wait_for_timeout(500)

            # Click download option
            download_option = await page.query_selector('text=Download')
            if download_option:
                # Set up download handler
                async with page.expect_download() as download_info:
                    await download_option.click()

                download = await download_info.value

                # Save with meaningful name
                filename = f"{sanitize_filename(audio_title)}.m4a"
                save_path = download_dir / filename
                await download.save_as(save_path)

                print(f"    ✓ Downloaded: {filename}")
                return save_path
    except Exception as e:
        print(f"    ✗ Download failed: {e}")

    return None


async def sync_notebook(page, notebook: dict, known_assets: set, supabase) -> dict:
    """Sync a single notebook - download new audio overviews."""
    notebook_id = notebook["notebook_id"]
    notebook_title = notebook["title"]

    print(f"\n  Checking: {notebook_title}")

    results = {"downloaded": 0, "skipped": 0, "errors": 0}

    # Get audio overviews in this notebook
    audio_items = await get_audio_overviews(page, notebook_id)

    for audio in audio_items:
        audio_title = audio["title"]

        # Check if we already have this asset
        if (notebook_id, audio_title) in known_assets:
            print(f"    - {audio_title}: already synced")
            results["skipped"] += 1
            continue

        print(f"    + {audio_title}: NEW - downloading...")

        # Download the audio
        save_path = await download_audio(
            page,
            audio["element"],
            notebook_title,
            audio_title,
            AUDIO_DIR
        )

        if save_path:
            # Add to Supabase
            try:
                supabase.table("notebooklm_assets").insert({
                    "notebook_id": notebook_id,
                    "asset_title": audio_title,
                    "asset_type": "audio",
                    "first_seen_at": datetime.utcnow().isoformat()
                }).execute()
                results["downloaded"] += 1
            except Exception as e:
                print(f"    ✗ DB error: {e}")
                results["errors"] += 1
        else:
            results["errors"] += 1

    return results


async def main_async(args):
    from playwright.async_api import async_playwright

    # Ensure directories exist
    BROWSER_DATA_DIR.mkdir(exist_ok=True)
    AUDIO_DIR.mkdir(exist_ok=True)
    DOWNLOADS_DIR.mkdir(exist_ok=True)

    async with async_playwright() as p:
        # Use Chrome browser
        # --login mode: visible for manual Google login
        # Normal mode: headless (won't interrupt you)
        browser = await p.chromium.launch_persistent_context(
            user_data_dir=str(BROWSER_DATA_DIR),
            channel="chrome",
            headless=not args.login and not args.visible,
            downloads_path=str(DOWNLOADS_DIR),
            accept_downloads=True,
        )

        page = await browser.new_page()

        # Login mode
        if args.login:
            success = await login_flow(page)
            await browser.close()
            return

        print("=" * 60)
        print("NotebookLM Sync")
        print("=" * 60)

        # Initialize Supabase
        supabase = get_supabase_client()
        known_notebooks = get_known_notebooks(supabase)
        known_assets = get_known_assets(supabase)

        print(f"Known notebooks in DB: {len(known_notebooks)}")
        print(f"Known assets in DB: {len(known_assets)}")

        # Get current notebooks from NotebookLM
        print("\nFetching notebook list...")
        notebooks = await get_notebook_list(page)
        print(f"Found {len(notebooks)} notebooks on NotebookLM")

        # Filter to new or specific notebooks
        if args.notebook:
            notebooks = [n for n in notebooks if args.notebook.lower() in n["title"].lower()]
            print(f"Filtered to {len(notebooks)} matching '{args.notebook}'")

        # Sync each notebook
        total_downloaded = 0
        total_skipped = 0
        total_errors = 0

        for notebook in notebooks:
            # Add notebook to DB if new
            if notebook["notebook_id"] not in known_notebooks:
                try:
                    supabase.table("notebooklm_notebooks").insert({
                        "notebook_id": notebook["notebook_id"],
                        "title": notebook["title"],
                        "created_display": notebook.get("date"),
                        "first_seen_at": datetime.utcnow().isoformat()
                    }).execute()
                    print(f"\n+ New notebook: {notebook['title']}")
                except:
                    pass  # May already exist

            # Sync audio overviews
            results = await sync_notebook(page, notebook, known_assets, supabase)
            total_downloaded += results["downloaded"]
            total_skipped += results["skipped"]
            total_errors += results["errors"]

        await browser.close()

        # Summary
        print("\n" + "=" * 60)
        print("Sync Complete")
        print("=" * 60)
        print(f"Downloaded: {total_downloaded}")
        print(f"Skipped (already synced): {total_skipped}")
        print(f"Errors: {total_errors}")

        if total_downloaded > 0:
            print("\n→ Run these commands to process new audio:")
            print("  python transcribe_optimized.py")
            print("  python upload_transcripts.py")
            print("  python generate_study_materials.py")
            print("  python export_study_materials.py")


def main():
    parser = argparse.ArgumentParser(description="Sync NotebookLM to Supabase")
    parser.add_argument("--login", action="store_true", help="Interactive login mode")
    parser.add_argument("--visible", action="store_true", help="Show browser window")
    parser.add_argument("--notebook", type=str, help="Sync specific notebook by name")
    args = parser.parse_args()

    asyncio.run(main_async(args))


if __name__ == "__main__":
    main()
