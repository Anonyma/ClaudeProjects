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
    """Generate an article-style summary that teaches the content directly."""

    prompt = f"""You are creating an educational article based on a deep-dive discussion titled "{title}".

CRITICAL: Write as if TEACHING the reader directly. Do NOT write meta descriptions like "The podcast explores..." or "This episode discusses...". Instead, present the actual knowledge and insights as if you're writing a well-researched article.

Based on the transcript below, create:

1. A TEACHING-STYLE SUMMARY (3-4 paragraphs):
   - Address the reader with "you"
   - Present the actual content, facts, and insights directly
   - Include specific examples, dates, names, and case studies from the transcript
   - Write as if you're teaching the material, not describing a podcast

2. KEY INSIGHTS (5-8 points):
   - Specific, actionable insights
   - Include supporting details

3. A one-sentence TLDR (what the reader will learn, not what "the episode covers")

4. CONCEPT LINKS: List 3-5 concepts that connect to other topics (for building a knowledge latticework)

5. SUGGESTED EXTERNAL LINKS: 3-5 Wikipedia or educational resource topics that would help deepen understanding

Format your response as JSON:
{{
    "summary": "Teaching-style article text...",
    "key_points": ["specific insight with detail", ...],
    "tldr": "You'll learn that...",
    "concepts": ["concept1", "concept2", ...],
    "external_topics": ["Wikipedia: Topic Name", "Resource: Topic Name", ...]
}}

EXAMPLE of good vs bad summary:
BAD: "The podcast explores how materials shaped history..."
GOOD: "Materials don't just serve human needs—they actively shape the course of civilizations. Consider glass: its chemical properties enabled the microscope, which revealed bacteria and transformed medicine..."

TRANSCRIPT:
{transcript[:15000]}
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

        # Always regenerate summaries (delete existing first for article-style format)
        if existing_summary.data:
            supabase.table("notebooklm_summaries").delete().eq("asset_id", asset_id).execute()
            print("  Deleted old meta-style summary")

        print("  Generating article-style summary...")
        try:
            summary_data = generate_summary(openai, transcript_text, asset_title)

            # Build metadata with concepts and external links
            metadata = {
                "concepts": summary_data.get("concepts", []),
                "external_topics": summary_data.get("external_topics", []),
                "format": "article-style"
            }

            supabase.table("notebooklm_summaries").insert({
                "asset_id": asset_id,
                "summary_type": "standard",
                "summary_text": summary_data["summary"],
                "key_points": summary_data["key_points"],
                "model_used": MODEL,
                "metadata": metadata
            }).execute()

            # Also save TLDR as separate entry
            supabase.table("notebooklm_summaries").insert({
                "asset_id": asset_id,
                "summary_type": "tldr",
                "summary_text": summary_data["tldr"],
                "key_points": None,
                "model_used": MODEL,
                "metadata": metadata
            }).execute()

            print(f"  ✓ Summary created ({len(summary_data['key_points'])} key points, {len(metadata['concepts'])} concepts)")
        except Exception as e:
            print(f"  ✗ Summary error: {e}")

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
