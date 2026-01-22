#!/usr/bin/env python3
"""
Voice memo transcription using MLX Whisper (local) or OpenAI API (cloud).
Optimized for Apple Silicon Macs.
"""

import os
import sys
import json
import time
import hashlib
import tempfile
from pathlib import Path
from datetime import datetime
from typing import Optional

from dotenv import load_dotenv
from tqdm import tqdm

# Local imports
from preprocess import preprocess_audio, get_audio_duration, estimate_transcription_time

# Load environment variables
load_dotenv()

# Project paths
PROJECT_DIR = Path(__file__).parent.parent
AUDIO_INBOX = PROJECT_DIR / "audio" / "inbox"
AUDIO_COMPLETED = PROJECT_DIR / "audio" / "completed"
TRANSCRIPTS_DIR = PROJECT_DIR / "transcripts"


def compute_file_hash(file_path: str) -> str:
    """Compute SHA256 hash of a file."""
    sha256 = hashlib.sha256()
    with open(file_path, 'rb') as f:
        for chunk in iter(lambda: f.read(8192), b''):
            sha256.update(chunk)
    return sha256.hexdigest()


def transcribe_with_mlx(audio_path: str, model: str = "mlx-community/whisper-large-v3-mlx") -> dict:
    """
    Transcribe audio using MLX Whisper (local, Apple Silicon optimized).

    Args:
        audio_path: Path to audio file
        model: MLX Whisper model to use

    Returns:
        dict with 'text' and 'segments' keys
    """
    try:
        import mlx_whisper
    except ImportError:
        print("Error: mlx-whisper not installed. Run: pip install mlx-whisper")
        sys.exit(1)

    print(f"  Loading MLX Whisper model: {model}")
    start_time = time.time()

    result = mlx_whisper.transcribe(
        audio_path,
        path_or_hf_repo=model,
        verbose=False
    )

    elapsed = time.time() - start_time
    duration = get_audio_duration(audio_path)

    print(f"  Transcription completed in {elapsed:.1f}s ({duration/elapsed:.1f}x real-time)")

    return {
        'text': result.get('text', ''),
        'segments': result.get('segments', []),
        'language': result.get('language', 'en'),
        'duration': duration,
        'transcription_time': elapsed,
        'model': model,
        'method': 'mlx_whisper'
    }


def transcribe_with_openai(audio_path: str, model: str = "whisper-1") -> dict:
    """
    Transcribe audio using OpenAI API (cloud).

    Args:
        audio_path: Path to audio file
        model: OpenAI Whisper model to use

    Returns:
        dict with 'text' key
    """
    api_key = os.getenv('OPENAI_API_KEY')
    if not api_key:
        raise ValueError("OPENAI_API_KEY not set in environment")

    try:
        from openai import OpenAI
    except ImportError:
        print("Error: openai not installed. Run: pip install openai")
        sys.exit(1)

    client = OpenAI(api_key=api_key)
    duration = get_audio_duration(audio_path)

    print(f"  Uploading to OpenAI ({duration/60:.1f} min audio)...")
    start_time = time.time()

    with open(audio_path, 'rb') as audio_file:
        response = client.audio.transcriptions.create(
            model=model,
            file=audio_file,
            response_format="verbose_json"
        )

    elapsed = time.time() - start_time
    print(f"  Transcription completed in {elapsed:.1f}s")

    # Calculate cost (~$0.006 per minute)
    cost = (duration / 60) * 0.006

    return {
        'text': response.text,
        'segments': [{'text': s.text, 'start': s.start, 'end': s.end}
                     for s in getattr(response, 'segments', [])] if hasattr(response, 'segments') else [],
        'language': getattr(response, 'language', 'en'),
        'duration': duration,
        'transcription_time': elapsed,
        'model': model,
        'method': 'openai_api',
        'cost_usd': cost
    }


def transcribe_file(
    input_path: str,
    output_path: Optional[str] = None,
    model: str = "mlx-community/whisper-large-v3-mlx",
    use_openai: bool = False,
    preprocess: bool = True,
    move_completed: bool = False
) -> dict:
    """
    Full transcription pipeline for a single file.

    Args:
        input_path: Path to input audio file
        output_path: Path for transcript output (default: transcripts/<filename>.txt)
        model: Model to use for transcription
        use_openai: Use OpenAI API instead of local MLX
        preprocess: Apply preprocessing (silence removal + compression)
        move_completed: Move file to completed folder after transcription

    Returns:
        dict with transcription result and metadata
    """
    input_path = Path(input_path)
    if not input_path.exists():
        raise FileNotFoundError(f"Audio file not found: {input_path}")

    # Compute file hash for deduplication
    file_hash = compute_file_hash(str(input_path))

    # Set up output path
    if output_path is None:
        output_path = TRANSCRIPTS_DIR / f"{input_path.stem}.txt"
    output_path = Path(output_path)
    output_path.parent.mkdir(parents=True, exist_ok=True)

    print(f"\n{'='*60}")
    print(f"Transcribing: {input_path.name}")
    print(f"{'='*60}")

    original_duration = get_audio_duration(str(input_path))
    print(f"Duration: {original_duration/60:.1f} minutes")

    # Preprocessing
    preprocess_stats = None
    audio_to_transcribe = str(input_path)

    if preprocess:
        print("\nPreprocessing...")
        temp_preprocessed = tempfile.NamedTemporaryFile(suffix='.wav', delete=False)
        temp_preprocessed.close()

        try:
            audio_to_transcribe, preprocess_stats = preprocess_audio(
                str(input_path),
                temp_preprocessed.name,
                remove_silence_enabled=True,
                compress_enabled=True
            )
        except Exception as e:
            print(f"  Preprocessing failed: {e}, using original file")
            audio_to_transcribe = str(input_path)

    # Transcription
    print("\nTranscribing...")
    if use_openai:
        result = transcribe_with_openai(audio_to_transcribe, model if model != "mlx-community/whisper-large-v3-mlx" else "whisper-1")
    else:
        result = transcribe_with_mlx(audio_to_transcribe, model)

    # Clean up temp file
    if preprocess and audio_to_transcribe != str(input_path):
        try:
            os.unlink(audio_to_transcribe)
        except:
            pass

    # Save transcript
    transcript_text = result['text'].strip()
    with open(output_path, 'w') as f:
        f.write(transcript_text)
    print(f"\nTranscript saved: {output_path}")

    # Move to completed folder if requested
    if move_completed:
        completed_path = AUDIO_COMPLETED / input_path.name
        AUDIO_COMPLETED.mkdir(parents=True, exist_ok=True)
        input_path.rename(completed_path)
        print(f"Moved to: {completed_path}")

    # Build result
    word_count = len(transcript_text.split())
    return {
        'file_hash': file_hash,
        'filename': input_path.name,
        'input_path': str(input_path),
        'output_path': str(output_path),
        'duration_seconds': original_duration,
        'transcript_text': transcript_text,
        'word_count': word_count,
        'model_used': result['model'],
        'method': result['method'],
        'transcription_time': result['transcription_time'],
        'preprocessing_applied': preprocess,
        'preprocess_stats': preprocess_stats,
        'cost_usd': result.get('cost_usd'),
        'timestamp': datetime.now().isoformat()
    }


def estimate_cost_and_time(file_path: str, use_openai: bool = False, preprocess: bool = True) -> dict:
    """
    Estimate transcription cost and time for a file.

    Returns:
        dict with duration, estimated_time, and cost (if OpenAI)
    """
    duration = get_audio_duration(file_path)

    if use_openai:
        cost = (duration / 60) * 0.006  # $0.006 per minute
        est_time = 30 + (duration / 60) * 2  # ~2s per minute + upload time
    else:
        est_time = estimate_transcription_time(duration, "large-v3", preprocessed=preprocess)
        cost = 0

    return {
        'duration_seconds': duration,
        'duration_minutes': duration / 60,
        'estimated_time_seconds': est_time,
        'estimated_time_minutes': est_time / 60,
        'estimated_cost_usd': cost,
        'method': 'openai' if use_openai else 'mlx_whisper'
    }


# Available MLX Whisper models
MLX_MODELS = {
    'tiny': 'mlx-community/whisper-tiny-mlx',
    'base': 'mlx-community/whisper-base-mlx',
    'small': 'mlx-community/whisper-small-mlx',
    'medium': 'mlx-community/whisper-medium-mlx',
    'large-v3': 'mlx-community/whisper-large-v3-mlx',
    'large-v3-turbo': 'mlx-community/whisper-large-v3-turbo',
}


if __name__ == "__main__":
    import argparse

    parser = argparse.ArgumentParser(description="Transcribe voice memos")
    parser.add_argument("file", help="Audio file to transcribe")
    parser.add_argument("--model", default="large-v3", choices=list(MLX_MODELS.keys()),
                        help="MLX Whisper model size (default: large-v3)")
    parser.add_argument("--openai", action="store_true",
                        help="Use OpenAI API instead of local MLX Whisper")
    parser.add_argument("--no-preprocess", action="store_true",
                        help="Skip preprocessing (silence removal + compression)")
    parser.add_argument("--output", "-o", help="Output transcript file path")
    parser.add_argument("--estimate", action="store_true",
                        help="Only estimate time/cost, don't transcribe")
    parser.add_argument("--move", action="store_true",
                        help="Move file to completed folder after transcription")

    args = parser.parse_args()

    if not os.path.exists(args.file):
        print(f"Error: File not found: {args.file}")
        sys.exit(1)

    if args.estimate:
        estimate = estimate_cost_and_time(args.file, args.openai, not args.no_preprocess)
        print(f"\nFile: {args.file}")
        print(f"Duration: {estimate['duration_minutes']:.1f} minutes")
        print(f"Estimated transcription time: {estimate['estimated_time_minutes']:.1f} minutes")
        if estimate['estimated_cost_usd'] > 0:
            print(f"Estimated cost: ${estimate['estimated_cost_usd']:.2f}")
        sys.exit(0)

    # Get full model path
    model = MLX_MODELS.get(args.model, args.model)

    result = transcribe_file(
        args.file,
        output_path=args.output,
        model=model,
        use_openai=args.openai,
        preprocess=not args.no_preprocess,
        move_completed=args.move
    )

    print(f"\n{'='*60}")
    print("Summary:")
    print(f"{'='*60}")
    print(f"File: {result['filename']}")
    print(f"Duration: {result['duration_seconds']/60:.1f} minutes")
    print(f"Words: {result['word_count']}")
    print(f"Transcription time: {result['transcription_time']:.1f}s")
    if result.get('cost_usd'):
        print(f"Cost: ${result['cost_usd']:.2f}")
    print(f"Transcript: {result['output_path']}")
