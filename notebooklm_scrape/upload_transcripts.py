#!/usr/bin/env python3
"""
Upload transcripts to Supabase, linking them to the correct assets.
"""

import os
from pathlib import Path
from dotenv import load_dotenv

load_dotenv(Path(__file__).parent.parent / '.env')

SUPABASE_URL = os.getenv('SUPABASE_URL')
SUPABASE_KEY = os.getenv('SUPABASE_ANON_KEY')

# Mapping from audio filename to asset title in Supabase
FILENAME_TO_ASSET = {
    # Original 13
    "Art_Deco_Fused_King_Tut_With_Chrome": "Art Deco Fused King Tut With Chrome",
    "Art_Nouveau_The_Brief_Beautiful_Dream": "Art Nouveau The Brief Beautiful Dream",
    "Automation_Shock_and_the_Post-Work_Transition": "Automation Shock and the Post-Work Transition",
    "Big_History_in_25_Anchor_Dates": "Big History in 25 Anchor Dates",
    "How_Materials_Rewired_Human_History": "How Materials Rewired Human History",
    "How_Physical_Materials_Dictate_History": "How Physical Materials Dictate History",
    "Iron_Sugar_and_Mirrors_Rewired_Humanity": "Iron Sugar and Mirrors Rewired Humanity",
    "Ornament_to_Austerity_Political_Necessity_or_Purity": "Ornament to Austerity Political Necessity or Purity",
    "Rococo_curves_to_Brutalist_blocks": "Rococo curves to Brutalist blocks",
    "The_Glamour_and_Geometry_of_Art_Deco": "The Glamour and Geometry of Art Deco",
    "The_Six_Materials_That_Built_Civilization": "The Six Materials That Built Civilization",
    "Universal_Basic_Income_vs_The_Jobless_Future": "Universal Basic Income vs The Jobless Future",
    "Versailles_Was_Actually_A_Golden_Prison": "Versailles Was Actually A Golden Prison",
    # Architecture/Brutalism (Urban Imaginings notebook)
    "Architecture_as_a_Trauma_Response": "Architecture as a Trauma Response",
    "Why_Brutalism_Started_With_Floral_Wallpaper": "Why Brutalism Started With Floral Wallpaper",
    "How_Irony_Killed_the_Glass_Box": "How Irony Killed the Glass Box",
    "Exploding_Buildings_And_The_End_Of_Truth": "Exploding Buildings And The End Of Truth",
    # American History
    "The_American_Experiment_From_Cahokia_to_Reconstruction": "The American Experiment From Cahokia to Reconstruction",
    "How_American_Literature_Shattered_Reality": "How American Literature Shattered Reality",
    "Mapping_America_s_Inner_Life_Through_Fiction": "Mapping Americas Inner Life Through Fiction",
    "The_Great_Refusal_of_the_American_Dream": "The Great Refusal of the American Dream",
    "The_Rise_and_Fracture_of_Modern_America": "The Rise and Fracture of Modern America",
    "Washington_the_Town_Destroyer_and_Fragile_Experiments": "Washington the Town Destroyer and Fragile Experiments",
    "Native_Cities_and_the_Sovereignty_Straitjacket": "Native Cities and the Sovereignty Straitjacket",
    # Beat Generation
    "The_Beat_Generation_Started_With_Murder": "The Beat Generation Started With Murder",
    "Murder,_Jazz,_and_the_Birth_of_the_Beats": "Murder Jazz and the Birth of the Beats",
    "The_Bomb,_LSD,_and_Silicon_Valley": "The Bomb LSD and Silicon Valley",
    "Selling_The_Revolution_At_A_Markup": "Selling The Revolution At A Markup",
}


def get_supabase_client():
    from supabase import create_client
    return create_client(SUPABASE_URL, SUPABASE_KEY)


def main():
    client = get_supabase_client()
    audio_folder = Path(__file__).parent / "notebooklm-audio"

    print("Uploading transcripts to Supabase...")
    print("=" * 60)

    success = 0
    errors = []

    for txt_file in audio_folder.glob("*.txt"):
        filename_stem = txt_file.stem
        asset_title = FILENAME_TO_ASSET.get(filename_stem)

        if not asset_title:
            print(f"  ? {filename_stem}: No mapping found, skipping")
            continue

        # Read transcript
        transcript_text = txt_file.read_text(encoding="utf-8")
        word_count = len(transcript_text.split())

        # Find the asset in Supabase
        result = client.table("notebooklm_assets").select("id").eq(
            "asset_title", asset_title
        ).eq("asset_type", "audio").execute()

        if not result.data:
            print(f"  ✗ {asset_title}: Asset not found in database")
            errors.append(asset_title)
            continue

        asset_id = result.data[0]["id"]

        # Upsert transcript
        try:
            client.table("notebooklm_transcripts").upsert({
                "asset_id": asset_id,
                "transcript_text": transcript_text,
                "word_count": word_count,
                "source": "whisper"
            }, on_conflict="asset_id").execute()

            print(f"  ✓ {asset_title} ({word_count} words)")
            success += 1

        except Exception as e:
            print(f"  ✗ {asset_title}: {e}")
            errors.append(asset_title)

    print("=" * 60)
    print(f"Uploaded: {success}, Errors: {len(errors)}")


if __name__ == "__main__":
    main()
