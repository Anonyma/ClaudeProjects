#!/usr/bin/env python3
"""
Generate summaries and quizzes from NotebookLM transcripts using OpenAI.
"""

import os
import json
from pathlib import Path
from dotenv import load_dotenv

load_dotenv(Path(__file__).parent.parent / '.env')

SUPABASE_URL = os.getenv('SUPABASE_URL')
SUPABASE_KEY = os.getenv('SUPABASE_ANON_KEY')
OPENAI_API_KEY = os.getenv('OPENAI_API_KEY')

MODEL = "gpt-4o-mini"  # Cost-effective, good quality


def get_supabase_client():
    from supabase import create_client
    return create_client(SUPABASE_URL, SUPABASE_KEY)


def get_openai_client():
    from openai import OpenAI
    return OpenAI(api_key=OPENAI_API_KEY)


def generate_summary(openai_client, transcript: str, title: str) -> dict:
    """Generate a structured summary with key points."""

    prompt = f"""You are summarizing a NotebookLM podcast episode titled "{title}".

Based on the transcript below, create:
1. A concise summary (2-3 paragraphs) covering the main themes and arguments
2. 5-8 key takeaways as bullet points
3. A one-sentence "TLDR"

Format your response as JSON:
{{
    "summary": "...",
    "key_points": ["point 1", "point 2", ...],
    "tldr": "..."
}}

TRANSCRIPT:
{transcript[:12000]}  # Limit to avoid token limits
"""

    response = openai_client.chat.completions.create(
        model=MODEL,
        messages=[{"role": "user", "content": prompt}],
        response_format={"type": "json_object"},
        temperature=0.3
    )

    return json.loads(response.choices[0].message.content)


def generate_quiz(openai_client, transcript: str, title: str, difficulty: str = "medium") -> dict:
    """Generate quiz questions from the transcript."""

    prompt = f"""You are creating a quiz for a NotebookLM podcast episode titled "{title}".
Difficulty level: {difficulty}

Create 8-10 multiple choice questions that test understanding of the key concepts.
Each question should have 4 options (A, B, C, D) with exactly one correct answer.

Format your response as JSON:
{{
    "questions": [
        {{
            "question": "What is...",
            "options": {{
                "A": "option 1",
                "B": "option 2",
                "C": "option 3",
                "D": "option 4"
            }},
            "correct_answer": "B",
            "explanation": "Brief explanation of why B is correct"
        }},
        ...
    ]
}}

TRANSCRIPT:
{transcript[:12000]}
"""

    response = openai_client.chat.completions.create(
        model=MODEL,
        messages=[{"role": "user", "content": prompt}],
        response_format={"type": "json_object"},
        temperature=0.5
    )

    return json.loads(response.choices[0].message.content)


def main():
    supabase = get_supabase_client()
    openai = get_openai_client()

    # Get all transcripts with asset info
    result = supabase.table("notebooklm_transcripts").select(
        "id, asset_id, transcript_text, notebooklm_assets(id, asset_title)"
    ).execute()

    transcripts = result.data
    print(f"Found {len(transcripts)} transcripts to process")
    print("=" * 60)

    for i, t in enumerate(transcripts, 1):
        asset_id = t["asset_id"]
        asset_title = t["notebooklm_assets"]["asset_title"]
        transcript_text = t["transcript_text"]

        print(f"\n[{i}/{len(transcripts)}] {asset_title}")

        # Check if summary already exists
        existing_summary = supabase.table("notebooklm_summaries").select("id").eq(
            "asset_id", asset_id
        ).execute()

        if not existing_summary.data:
            print("  Generating summary...")
            try:
                summary_data = generate_summary(openai, transcript_text, asset_title)

                supabase.table("notebooklm_summaries").insert({
                    "asset_id": asset_id,
                    "summary_type": "standard",
                    "summary_text": summary_data["summary"],
                    "key_points": summary_data["key_points"],
                    "model_used": MODEL
                }).execute()

                # Also save TLDR as separate entry
                supabase.table("notebooklm_summaries").upsert({
                    "asset_id": asset_id,
                    "summary_type": "tldr",
                    "summary_text": summary_data["tldr"],
                    "key_points": None,
                    "model_used": MODEL
                }, on_conflict="asset_id,summary_type").execute()

                print(f"  ✓ Summary created ({len(summary_data['key_points'])} key points)")
            except Exception as e:
                print(f"  ✗ Summary error: {e}")
        else:
            print("  ✓ Summary already exists")

        # Check if quiz already exists
        existing_quiz = supabase.table("notebooklm_quizzes").select("id").eq(
            "asset_id", asset_id
        ).execute()

        if not existing_quiz.data:
            print("  Generating quiz...")
            try:
                quiz_data = generate_quiz(openai, transcript_text, asset_title)

                supabase.table("notebooklm_quizzes").insert({
                    "asset_id": asset_id,
                    "quiz_type": "recall",
                    "questions": quiz_data["questions"],
                    "difficulty": "medium",
                    "question_count": len(quiz_data["questions"]),
                    "model_used": MODEL
                }).execute()

                print(f"  ✓ Quiz created ({len(quiz_data['questions'])} questions)")
            except Exception as e:
                print(f"  ✗ Quiz error: {e}")
        else:
            print("  ✓ Quiz already exists")

    print("\n" + "=" * 60)
    print("Done! All study materials generated.")


if __name__ == "__main__":
    main()
