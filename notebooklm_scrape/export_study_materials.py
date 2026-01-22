#!/usr/bin/env python3
"""
Export study materials (summaries + quizzes) to markdown files.
These can be:
1. Synced to phone via iCloud/Dropbox
2. Shared with Claude mobile app
3. Used for hands-free study sessions
"""

import os
import json
from pathlib import Path
from datetime import datetime
from dotenv import load_dotenv

load_dotenv(Path(__file__).parent.parent / '.env')

SUPABASE_URL = os.getenv('SUPABASE_URL')
SUPABASE_KEY = os.getenv('SUPABASE_ANON_KEY')


def get_supabase_client():
    from supabase import create_client
    return create_client(SUPABASE_URL, SUPABASE_KEY)


def export_summary(asset_title: str, summary_data: dict, output_dir: Path):
    """Export a summary to markdown."""
    filename = asset_title.replace(" ", "_").replace("/", "-")[:50] + "_summary.md"
    filepath = output_dir / filename

    content = f"""# {asset_title}

## Summary
{summary_data.get('summary_text', 'No summary available')}

## Key Takeaways
"""
    key_points = summary_data.get('key_points', [])
    if key_points:
        for point in key_points:
            content += f"- {point}\n"

    # Add TLDR if available
    if summary_data.get('tldr'):
        content += f"\n## TL;DR\n{summary_data['tldr']}\n"

    filepath.write_text(content, encoding='utf-8')
    return filepath


def export_quiz(asset_title: str, quiz_data: dict, output_dir: Path):
    """Export a quiz to markdown (questions only, answers separate)."""
    filename = asset_title.replace(" ", "_").replace("/", "-")[:50] + "_quiz.md"
    filepath = output_dir / filename

    questions = quiz_data.get('questions', [])

    # Quiz questions (no answers - for testing yourself)
    content = f"""# Quiz: {asset_title}

**Instructions:** Answer each question, then check your answers at the bottom.

---

"""
    for i, q in enumerate(questions, 1):
        content += f"### Question {i}\n{q['question']}\n\n"
        for letter, option in q['options'].items():
            content += f"- **{letter})** {option}\n"
        content += "\n---\n\n"

    # Answer key at the bottom
    content += "## Answer Key\n\n"
    content += "*Scroll down only after you've answered all questions!*\n\n"
    content += "<details>\n<summary>Click to reveal answers</summary>\n\n"

    for i, q in enumerate(questions, 1):
        content += f"**Q{i}:** {q['correct_answer']} - {q['explanation']}\n\n"

    content += "</details>\n"

    filepath.write_text(content, encoding='utf-8')
    return filepath


def export_combined_quiz_for_voice(quizzes: list, output_dir: Path):
    """Export all quizzes in a format optimized for voice interaction."""
    filepath = output_dir / "ALL_QUIZZES_VOICE.md"

    content = f"""# NotebookLM Study Quizzes
*Generated: {datetime.now().strftime('%Y-%m-%d')}*

## How to Use (Voice Mode)
1. Open this file in Claude mobile app
2. Say: "Quiz me on [topic name]" or "Give me a random question"
3. Answer verbally
4. Ask Claude to check your answer

---

"""
    for quiz in quizzes:
        title = quiz['notebooklm_assets']['asset_title']
        questions = quiz['questions']

        content += f"## {title}\n\n"

        for i, q in enumerate(questions, 1):
            content += f"**Q{i}:** {q['question']}\n"
            for letter, option in q['options'].items():
                content += f"  {letter}) {option}\n"
            content += f"  *Answer: {q['correct_answer']} - {q['explanation']}*\n\n"

        content += "---\n\n"

    filepath.write_text(content, encoding='utf-8')
    return filepath


def main():
    client = get_supabase_client()

    # Create export directory
    export_dir = Path(__file__).parent / "study_materials"
    export_dir.mkdir(exist_ok=True)

    print(f"Exporting study materials to: {export_dir}")
    print("=" * 60)

    # Get summaries with asset info
    summaries_result = client.table("notebooklm_summaries").select(
        "*, notebooklm_assets(asset_title)"
    ).eq("summary_type", "standard").execute()

    # Get TLDRs
    tldrs_result = client.table("notebooklm_summaries").select(
        "summary_text, asset_id"
    ).eq("summary_type", "tldr").execute()

    tldr_map = {t['asset_id']: t['summary_text'] for t in tldrs_result.data}

    # Export summaries
    print("\nExporting summaries...")
    for s in summaries_result.data:
        title = s['notebooklm_assets']['asset_title']
        s['tldr'] = tldr_map.get(s['asset_id'])
        filepath = export_summary(title, s, export_dir)
        print(f"  ✓ {filepath.name}")

    # Get quizzes with asset info
    quizzes_result = client.table("notebooklm_quizzes").select(
        "*, notebooklm_assets(asset_title)"
    ).execute()

    # Export individual quizzes
    print("\nExporting quizzes...")
    for q in quizzes_result.data:
        title = q['notebooklm_assets']['asset_title']
        filepath = export_quiz(title, q, export_dir)
        print(f"  ✓ {filepath.name}")

    # Export combined voice-optimized quiz
    print("\nExporting combined voice quiz...")
    voice_file = export_combined_quiz_for_voice(quizzes_result.data, export_dir)
    print(f"  ✓ {voice_file.name}")

    print("\n" + "=" * 60)
    print(f"Done! Files exported to: {export_dir}")
    print("\nTo use on your phone:")
    print("1. Sync this folder to iCloud/Dropbox")
    print("2. Open files in Claude mobile app")
    print("3. Ask Claude to quiz you!")


if __name__ == "__main__":
    main()
