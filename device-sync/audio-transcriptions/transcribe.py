#!/usr/bin/env python3
"""
Custom transcription script using faster-whisper with word corrections and formatting
"""

import json
import re
import sys
from pathlib import Path
from faster_whisper import WhisperModel

def load_config(config_path="transcribe-config.json"):
    """Load configuration from JSON file"""
    with open(config_path) as f:
        return json.load(f)

def apply_word_replacements(text, replacements):
    """Apply word replacements case-insensitively"""
    for wrong, correct in replacements.items():
        # Case-insensitive replacement
        pattern = re.compile(re.escape(wrong), re.IGNORECASE)
        text = pattern.sub(correct, text)
    return text

def format_transcript(segments, config):
    """Format transcript with custom line break logic and word replacements"""
    replacements = config["word_replacements"]
    formatting = config["formatting"]
    min_silence = formatting["min_silence_for_paragraph"]

    lines = []
    current_paragraph = []
    last_end = 0

    for segment in segments:
        # Apply word replacements
        text = apply_word_replacements(segment.text.strip(), replacements)

        # Check silence duration since last segment
        silence_duration = segment.start - last_end

        # Start new paragraph if silence is long enough
        if silence_duration >= min_silence and current_paragraph:
            lines.append(" ".join(current_paragraph))
            lines.append("")  # Empty line between paragraphs
            current_paragraph = []

        # Add timestamp if enabled
        if formatting["add_timestamps"]:
            timestamp = f"[{format_time(segment.start)} --> {format_time(segment.end)}]"
            current_paragraph.append(f"{timestamp} {text}")
        else:
            current_paragraph.append(text)

        last_end = segment.end

    # Add remaining paragraph
    if current_paragraph:
        lines.append(" ".join(current_paragraph))

    return "\n".join(lines)

def format_time(seconds):
    """Convert seconds to HH:MM:SS.mmm format"""
    hours = int(seconds // 3600)
    minutes = int((seconds % 3600) // 60)
    secs = seconds % 60
    return f"{hours:02d}:{minutes:02d}:{secs:06.3f}"

def transcribe_file(audio_path, config):
    """Transcribe audio file using faster-whisper"""
    print(f"Loading model: {config['model']}...")
    model = WhisperModel(
        config["model"],
        device=config["device"],
        compute_type=config["compute_type"]
    )

    print(f"Transcribing: {audio_path}...")
    transcription_opts = config["transcription_options"]

    segments, info = model.transcribe(
        audio_path,
        **transcription_opts
    )

    print(f"Detected language: {info.language} (probability: {info.language_probability:.2f})")
    print(f"Duration: {info.duration:.2f}s")

    # Convert generator to list and format
    segments_list = list(segments)
    formatted_text = format_transcript(segments_list, config)

    return formatted_text

def main():
    if len(sys.argv) < 2:
        print("Usage: python transcribe.py <audio_file> [config_file]")
        sys.exit(1)

    audio_path = sys.argv[1]
    config_path = sys.argv[2] if len(sys.argv) > 2 else "transcribe-config.json"

    # Load configuration
    config = load_config(config_path)

    # Transcribe
    transcript = transcribe_file(audio_path, config)

    # Save output
    output_path = Path(audio_path).stem + "_transcript.txt"
    with open(output_path, "w") as f:
        f.write(transcript)

    print(f"\n✓ Transcript saved to: {output_path}")
    print(f"\n--- Preview (first 500 chars) ---")
    print(transcript[:500])

if __name__ == "__main__":
    main()
