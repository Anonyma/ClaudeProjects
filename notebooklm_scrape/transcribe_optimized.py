#!/usr/bin/env python3
"""
Optimized transcription for NotebookLM audio files.

Cost optimizations:
1. Uses whisper-1 ($0.006/min) instead of gpt-4o-transcribe ($0.04/min)
2. Speeds up audio 1.5x to reduce billable duration by 33%
3. Converts to mono mp3 for faster uploads

Estimated cost: ~$0.72 for 3 hours of audio (after 1.5x speedup)
"""

import os
import sys
import subprocess
import tempfile
from pathlib import Path
from dotenv import load_dotenv

# Load environment variables
load_dotenv(Path(__file__).parent.parent / '.env')

AUDIO_EXTENSIONS = {".wav", ".mp3", ".m4a", ".mp4", ".webm", ".ogg"}
SPEEDUP_FACTOR = 1.5  # 1.5x speed = 33% cost reduction


def get_audio_files(folder: Path) -> list[Path]:
    """Return list of audio files in the folder."""
    files = []
    for ext in AUDIO_EXTENSIONS:
        files.extend(folder.glob(f"*{ext}"))
    return sorted(files)


def transcript_exists(audio_file: Path) -> bool:
    """Check if a transcript file already exists."""
    return audio_file.with_suffix(".txt").exists()


def preprocess_audio(audio_file: Path, speedup: float = SPEEDUP_FACTOR) -> Path:
    """
    Preprocess audio for cheaper transcription:
    - Speed up by given factor (reduces duration = reduces cost)
    - Convert to mono mp3 (smaller file, faster upload)
    """
    temp_file = tempfile.NamedTemporaryFile(suffix=".mp3", delete=False)
    temp_path = temp_file.name
    temp_file.close()

    # ffmpeg command: speed up audio and convert to mono mp3
    # atempo filter only accepts 0.5-2.0, so we use it directly for 1.5x
    cmd = [
        "ffmpeg", "-y", "-i", str(audio_file),
        "-filter:a", f"atempo={speedup}",
        "-ac", "1",  # mono
        "-b:a", "64k",  # lower bitrate (speech doesn't need high quality)
        temp_path
    ]

    try:
        subprocess.run(cmd, capture_output=True, check=True)
        return Path(temp_path)
    except subprocess.CalledProcessError as e:
        print(f"FFmpeg error: {e.stderr.decode()}")
        raise


def transcribe_file(audio_file: Path, client) -> str:
    """Transcribe a single audio file using OpenAI Whisper API."""
    with open(audio_file, "rb") as f:
        response = client.audio.transcriptions.create(
            model="whisper-1",  # Much cheaper than gpt-4o-transcribe
            file=f,
            response_format="text"
        )
    return response


def save_transcript(audio_file: Path, transcript: str) -> Path:
    """Save transcript to a .txt file alongside the original audio file."""
    transcript_path = audio_file.with_suffix(".txt")
    transcript_path.write_text(transcript, encoding="utf-8")
    return transcript_path


def get_duration_minutes(audio_file: Path) -> float:
    """Get audio duration in minutes using ffprobe."""
    cmd = [
        "ffprobe", "-v", "error",
        "-show_entries", "format=duration",
        "-of", "default=noprint_wrappers=1:nokey=1",
        str(audio_file)
    ]
    result = subprocess.run(cmd, capture_output=True, text=True)
    return float(result.stdout.strip()) / 60


def main():
    import argparse
    parser = argparse.ArgumentParser(description="Transcribe NotebookLM audio (optimized)")
    parser.add_argument("folder", nargs="?", default="./notebooklm-audio")
    parser.add_argument("--test-one", action="store_true", help="Only transcribe first file")
    parser.add_argument("--no-speedup", action="store_true", help="Don't speed up audio")
    args = parser.parse_args()

    folder = Path(args.folder)
    if not folder.exists():
        print(f"Error: Folder '{folder}' does not exist.")
        sys.exit(1)

    # Check for API key
    api_key = os.environ.get("OPENAI_API_KEY")
    if not api_key:
        print("Error: OPENAI_API_KEY environment variable is not set.")
        sys.exit(1)

    # Initialize OpenAI client
    try:
        from openai import OpenAI
        client = OpenAI(api_key=api_key)
    except ImportError:
        print("Error: openai package not installed. Run: pip install openai")
        sys.exit(1)

    # Get audio files
    audio_files = get_audio_files(folder)
    if not audio_files:
        print(f"No audio files found in '{folder}'")
        sys.exit(0)

    # Calculate total duration and estimated cost
    total_minutes = sum(get_duration_minutes(f) for f in audio_files)
    speedup = 1.0 if args.no_speedup else SPEEDUP_FACTOR
    billed_minutes = total_minutes / speedup
    estimated_cost = billed_minutes * 0.006  # whisper-1 rate

    print(f"Found {len(audio_files)} audio files")
    print(f"Total duration: {total_minutes:.1f} minutes")
    print(f"After {speedup}x speedup: {billed_minutes:.1f} billed minutes")
    print(f"Estimated cost: ${estimated_cost:.2f}")
    print("-" * 60)

    if args.test_one:
        audio_files = audio_files[:1]
        print("TEST MODE: Processing only the first file.\n")

    success_count = 0
    skip_count = 0
    error_count = 0

    for i, audio_file in enumerate(audio_files, 1):
        print(f"\n[{i}/{len(audio_files)}] {audio_file.name}")

        if transcript_exists(audio_file):
            print(f"  SKIPPED: Transcript already exists")
            skip_count += 1
            continue

        try:
            # Preprocess (speedup + convert)
            if not args.no_speedup:
                print(f"  Preprocessing ({speedup}x speedup)...")
                processed_file = preprocess_audio(audio_file, speedup)
            else:
                processed_file = audio_file

            # Transcribe
            print(f"  Transcribing with whisper-1...")
            transcript = transcribe_file(processed_file, client)

            # Clean up temp file
            if not args.no_speedup:
                os.unlink(processed_file)

            # Save
            transcript_path = save_transcript(audio_file, transcript)
            word_count = len(transcript.split())
            print(f"  DONE: {word_count} words saved to {transcript_path.name}")
            success_count += 1

        except Exception as e:
            print(f"  ERROR: {e}")
            error_count += 1

    print("\n" + "=" * 60)
    print(f"Summary: {success_count} transcribed, {skip_count} skipped, {error_count} errors")


if __name__ == "__main__":
    main()
