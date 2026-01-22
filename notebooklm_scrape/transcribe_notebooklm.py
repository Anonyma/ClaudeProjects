#!/usr/bin/env python3
"""
Transcribe NotebookLM audio files using OpenAI's speech-to-text API.

COST & SAFETY NOTES:
--------------------
- OpenAI speech-to-text is billed per minute of audio transcribed.
- As of early 2025, gpt-4o-transcribe costs ~$2.50 per hour of audio.
- To test safely:
    1. Start with a SINGLE short file: python transcribe_notebooklm.py --test-one
    2. Check your OpenAI billing dashboard after the test.
    3. To cap spending, only load a small prepaid amount in OpenAI billing settings.
- The script is resumable: it skips files that already have .txt transcripts.

Usage:
    python transcribe_notebooklm.py [folder_path]
    python transcribe_notebooklm.py --test-one  # Transcribe only the first file found
"""

import os
import sys
import argparse
from pathlib import Path

# Supported audio extensions
AUDIO_EXTENSIONS = {".wav", ".mp3", ".m4a"}


def get_audio_files(folder: Path) -> list[Path]:
    """Return list of audio files in the folder."""
    files = []
    for ext in AUDIO_EXTENSIONS:
        files.extend(folder.glob(f"*{ext}"))
    return sorted(files)


def transcript_exists(audio_file: Path) -> bool:
    """Check if a transcript file already exists for the audio file."""
    transcript_path = audio_file.with_suffix(".txt")
    return transcript_path.exists()


def transcribe_file(audio_file: Path, client) -> str:
    """Transcribe a single audio file using OpenAI API."""
    with open(audio_file, "rb") as f:
        response = client.audio.transcriptions.create(
            model="gpt-4o-transcribe",
            file=f,
            response_format="text"
        )
    return response


def save_transcript(audio_file: Path, transcript: str) -> Path:
    """Save transcript to a .txt file alongside the audio file."""
    transcript_path = audio_file.with_suffix(".txt")
    transcript_path.write_text(transcript, encoding="utf-8")
    return transcript_path


def main():
    parser = argparse.ArgumentParser(
        description="Transcribe NotebookLM audio files using OpenAI speech-to-text."
    )
    parser.add_argument(
        "folder",
        nargs="?",
        default="./notebooklm-audio",
        help="Folder containing audio files (default: ./notebooklm-audio)"
    )
    parser.add_argument(
        "--test-one",
        action="store_true",
        help="Only transcribe the first file found (for testing)"
    )
    args = parser.parse_args()

    folder = Path(args.folder)

    if not folder.exists():
        print(f"Error: Folder '{folder}' does not exist.")
        sys.exit(1)

    # Check for API key
    api_key = os.environ.get("OPENAI_API_KEY")
    if not api_key:
        print("Error: OPENAI_API_KEY environment variable is not set.")
        print("Set it with: export OPENAI_API_KEY='your-api-key-here'")
        sys.exit(1)

    # Import and initialize OpenAI client
    try:
        from openai import OpenAI
        client = OpenAI(api_key=api_key)
    except ImportError:
        print("Error: openai package not installed.")
        print("Install it with: pip install openai")
        sys.exit(1)

    # Get audio files
    audio_files = get_audio_files(folder)

    if not audio_files:
        print(f"No audio files found in '{folder}'.")
        print(f"Supported extensions: {', '.join(AUDIO_EXTENSIONS)}")
        sys.exit(0)

    print(f"Found {len(audio_files)} audio file(s) in '{folder}'")
    print("-" * 60)

    # Limit to one file if testing
    if args.test_one:
        audio_files = audio_files[:1]
        print("TEST MODE: Processing only the first file.\n")

    success_count = 0
    skip_count = 0
    error_count = 0

    for i, audio_file in enumerate(audio_files, 1):
        print(f"[{i}/{len(audio_files)}] {audio_file.name}")

        # Skip if transcript exists
        if transcript_exists(audio_file):
            print(f"    SKIPPED: Transcript already exists.")
            skip_count += 1
            continue

        # Transcribe
        try:
            print(f"    Transcribing...")
            transcript = transcribe_file(audio_file, client)
            transcript_path = save_transcript(audio_file, transcript)
            print(f"    DONE: Saved to {transcript_path.name}")
            success_count += 1
        except Exception as e:
            print(f"    ERROR: {e}")
            error_count += 1
            continue

    # Summary
    print("-" * 60)
    print(f"Summary: {success_count} transcribed, {skip_count} skipped, {error_count} errors")


if __name__ == "__main__":
    main()
