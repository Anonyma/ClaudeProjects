#!/usr/bin/env python3
"""
Generate rich, article-style summaries from NotebookLM transcripts.
Includes: content summaries, relevant links, visual suggestions, and Claude reference format.
"""

import os
import json
from pathlib import Path
from dotenv import load_dotenv

load_dotenv(Path(__file__).parent.parent / '.env')

SUPABASE_URL = os.getenv('SUPABASE_URL')
SUPABASE_KEY = os.getenv('SUPABASE_ANON_KEY')
OPENAI_API_KEY = os.getenv('OPENAI_API_KEY')

MODEL = "gpt-4o"  # Use full GPT-4o for higher quality summaries


def get_supabase_client():
    from supabase import create_client
    return create_client(SUPABASE_URL, SUPABASE_KEY)


def get_openai_client():
    from openai import OpenAI
    return OpenAI(api_key=OPENAI_API_KEY)


def generate_rich_summary(openai_client, transcript: str, title: str) -> dict:
    """Generate a rich, article-style summary with links and Claude reference format."""

    prompt = f"""You are creating a comprehensive study guide from a NotebookLM podcast episode titled "{title}".

Your task is to create TWO outputs:

## 1. HUMAN-READABLE SUMMARY (article_summary)
Write this as an educational article that TEACHES the content directly. DO NOT write meta descriptions like "The podcast discusses..." or "The hosts talk about...". Instead:

- Start with an engaging introduction that frames why this topic matters
- Break into clear sections with descriptive headers
- Explain each concept as if teaching a student who wasn't there
- Include specific examples, statistics, dates, names, and case studies mentioned
- Use clear, engaging prose - not bullet points for the main content
- End with synthesis: what are the key takeaways and why they matter
- Aim for 800-1200 words of substantive content

## 2. CLAUDE REFERENCE FORMAT (claude_reference)
A structured JSON object for AI continuity across sessions:
- topics_covered: List of main topics/themes covered
- key_concepts: Dictionary mapping concept names to brief explanations
- notable_facts: List of specific facts, statistics, or examples worth remembering
- connections: Topics that relate to other domains of knowledge
- suggested_follow_ups: What topics could be explored deeper
- questions_raised: Open questions or debates mentioned

## 3. LEARNING RESOURCES (resources)
Based on the topics covered, suggest:
- 3-5 search queries for finding relevant articles/papers
- 2-3 Wikipedia article titles that would provide background
- 1-2 suggested image searches for visual learning

Format your ENTIRE response as JSON:
{{
    "article_summary": "Full article text with markdown formatting...",
    "tldr": "One sentence capturing the essence",
    "key_takeaways": ["takeaway 1", "takeaway 2", ...],
    "claude_reference": {{
        "topics_covered": ["topic1", "topic2"],
        "key_concepts": {{"concept": "explanation"}},
        "notable_facts": ["fact1", "fact2"],
        "connections": ["related domain 1"],
        "suggested_follow_ups": ["topic for deeper exploration"],
        "questions_raised": ["open question"]
    }},
    "resources": {{
        "search_queries": ["query 1", "query 2"],
        "wikipedia_articles": ["Article Title 1"],
        "image_searches": ["search term for relevant diagram"]
    }}
}}

TRANSCRIPT:
{transcript[:15000]}
"""

    response = openai_client.chat.completions.create(
        model=MODEL,
        messages=[{"role": "user", "content": prompt}],
        response_format={"type": "json_object"},
        temperature=0.4,
        max_tokens=4000
    )

    return json.loads(response.choices[0].message.content)


def main():
    import argparse
    parser = argparse.ArgumentParser(description="Generate rich summaries from transcripts")
    parser.add_argument("--asset-id", help="Process specific asset ID only")
    parser.add_argument("--dry-run", action="store_true", help="Print output without saving to DB")
    parser.add_argument("--force", action="store_true", help="Regenerate even if summary exists")
    args = parser.parse_args()

    supabase = get_supabase_client()
    openai = get_openai_client()

    # Get transcripts
    query = supabase.table("notebooklm_transcripts").select(
        "id, asset_id, transcript_text, notebooklm_assets(id, asset_title)"
    )

    if args.asset_id:
        query = query.eq("asset_id", args.asset_id)

    result = query.execute()
    transcripts = result.data

    print(f"Found {len(transcripts)} transcript(s) to process")
    print("=" * 60)

    for i, t in enumerate(transcripts, 1):
        asset_id = t["asset_id"]
        asset_title = t["notebooklm_assets"]["asset_title"]
        transcript_text = t["transcript_text"]

        print(f"\n[{i}/{len(transcripts)}] {asset_title}")

        # Check if rich summary already exists
        if not args.force:
            existing = supabase.table("notebooklm_summaries").select("id").eq(
                "asset_id", asset_id
            ).eq("summary_type", "rich").execute()

            if existing.data:
                print("  ✓ Rich summary already exists (use --force to regenerate)")
                continue

        print("  Generating rich summary...")
        try:
            data = generate_rich_summary(openai, transcript_text, asset_title)

            if args.dry_run:
                print("\n--- DRY RUN OUTPUT ---")
                print(f"TLDR: {data['tldr']}")
                print(f"\nKey Takeaways ({len(data['key_takeaways'])}):")
                for kt in data['key_takeaways']:
                    print(f"  • {kt}")
                print(f"\nArticle length: {len(data['article_summary'])} chars")
                print(f"Topics covered: {data['claude_reference']['topics_covered']}")
                print(f"Search queries: {data['resources']['search_queries']}")
                continue

            # Save rich summary
            supabase.table("notebooklm_summaries").upsert({
                "asset_id": asset_id,
                "summary_type": "rich",
                "summary_text": data["article_summary"],
                "key_points": data["key_takeaways"],
                "model_used": MODEL,
                "metadata": {
                    "tldr": data["tldr"],
                    "claude_reference": data["claude_reference"],
                    "resources": data["resources"]
                }
            }, on_conflict="asset_id,summary_type").execute()

            print(f"  ✓ Rich summary created")
            print(f"    - {len(data['article_summary'])} chars")
            print(f"    - {len(data['key_takeaways'])} takeaways")
            print(f"    - {len(data['claude_reference']['topics_covered'])} topics")
            print(f"    - {len(data['resources']['search_queries'])} resource links")

        except Exception as e:
            print(f"  ✗ Error: {e}")
            import traceback
            traceback.print_exc()

    print("\n" + "=" * 60)
    print("Done!")


if __name__ == "__main__":
    main()
