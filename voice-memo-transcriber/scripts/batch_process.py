#!/usr/bin/env python3
"""
Batch processing for voice memo transcription.
Process all pending files from inbox folder or Supabase queue.
"""

import os
import sys
from pathlib import Path
from datetime import datetime
from typing import List, Optional

from dotenv import load_dotenv
from tqdm import tqdm

# Local imports
from transcribe import transcribe_file, compute_file_hash, estimate_cost_and_time, MLX_MODELS
from sync_to_supabase import (
    get_supabase_client, list_memos, get_memo_by_hash,
    create_memo, update_memo_status, sync_transcription_result, get_stats
)
from preprocess import get_audio_duration

# Load environment variables
load_dotenv()

# Project paths
PROJECT_DIR = Path(__file__).parent.parent
AUDIO_INBOX = PROJECT_DIR / "audio" / "inbox"
AUDIO_COMPLETED = PROJECT_DIR / "audio" / "completed"
TRANSCRIPTS_DIR = PROJECT_DIR / "transcripts"

# Supported audio formats
AUDIO_EXTENSIONS = {'.mp3', '.m4a', '.wav', '.ogg', '.flac', '.aac', '.wma', '.opus'}


def scan_inbox() -> List[Path]:
    """
    Scan inbox folder for audio files.

    Returns:
        List of audio file paths
    """
    if not AUDIO_INBOX.exists():
        AUDIO_INBOX.mkdir(parents=True)
        return []

    files = []
    for ext in AUDIO_EXTENSIONS:
        files.extend(AUDIO_INBOX.glob(f"*{ext}"))
        files.extend(AUDIO_INBOX.glob(f"*{ext.upper()}"))

    return sorted(files, key=lambda f: f.stat().st_mtime)


def get_new_files() -> List[dict]:
    """
    Get files from inbox that haven't been processed yet.
    Checks against Supabase by file hash.

    Returns:
        List of dicts with file info
    """
    files = scan_inbox()
    new_files = []

    for file_path in files:
        file_hash = compute_file_hash(str(file_path))
        existing = get_memo_by_hash(file_hash)

        file_info = {
            'path': file_path,
            'filename': file_path.name,
            'hash': file_hash,
            'duration': get_audio_duration(str(file_path)),
            'size': file_path.stat().st_size,
            'existing': existing
        }

        if existing and existing.get('status') == 'completed':
            file_info['status'] = 'already_completed'
        elif existing and existing.get('status') == 'processing':
            file_info['status'] = 'processing'
        elif existing and existing.get('status') == 'pending':
            file_info['status'] = 'pending_in_queue'
        else:
            file_info['status'] = 'new'

        new_files.append(file_info)

    return new_files


def add_to_queue(file_path: Path, preprocess: bool = True) -> dict:
    """
    Add a file to the processing queue in Supabase.

    Args:
        file_path: Path to audio file
        preprocess: Whether preprocessing will be applied

    Returns:
        Created memo record
    """
    file_hash = compute_file_hash(str(file_path))
    duration = get_audio_duration(str(file_path))

    # Check if already exists
    existing = get_memo_by_hash(file_hash)
    if existing:
        return existing

    # Estimate time
    estimate = estimate_cost_and_time(str(file_path), use_openai=False, preprocess=preprocess)

    memo = create_memo(
        file_hash=file_hash,
        filename=file_path.name,
        duration_seconds=duration,
        preprocessing_applied=preprocess,
        estimated_seconds=estimate['estimated_time_seconds']
    )

    return memo


def process_file(
    file_path: Path,
    model: str = "mlx-community/whisper-large-v3-mlx",
    preprocess: bool = True,
    sync_to_db: bool = True,
    move_completed: bool = True
) -> dict:
    """
    Process a single file: transcribe and optionally sync to Supabase.

    Args:
        file_path: Path to audio file
        model: MLX Whisper model to use
        preprocess: Apply preprocessing
        sync_to_db: Sync results to Supabase
        move_completed: Move file to completed folder

    Returns:
        Transcription result dict
    """
    # Mark as processing in Supabase
    file_hash = compute_file_hash(str(file_path))
    existing = get_memo_by_hash(file_hash)

    if existing:
        update_memo_status(existing['id'], 'processing')
    else:
        # Add to queue first
        memo = add_to_queue(file_path, preprocess)
        update_memo_status(memo['id'], 'processing')

    try:
        # Transcribe
        result = transcribe_file(
            str(file_path),
            model=model,
            preprocess=preprocess,
            move_completed=move_completed
        )

        # Sync to Supabase
        if sync_to_db:
            sync_result = sync_transcription_result(result)
            result['memo_id'] = sync_result['memo_id']
            result['transcript_id'] = sync_result['transcript_id']

        return result

    except Exception as e:
        # Mark as failed
        if existing:
            update_memo_status(existing['id'], 'failed')
        raise


def batch_process(
    model: str = "mlx-community/whisper-large-v3-mlx",
    preprocess: bool = True,
    limit: Optional[int] = None,
    skip_completed: bool = True
) -> List[dict]:
    """
    Process all files in inbox.

    Args:
        model: MLX Whisper model to use
        preprocess: Apply preprocessing
        limit: Maximum number of files to process
        skip_completed: Skip files that have already been transcribed

    Returns:
        List of transcription results
    """
    files = get_new_files()

    if skip_completed:
        files = [f for f in files if f['status'] in ('new', 'pending_in_queue')]

    if limit:
        files = files[:limit]

    if not files:
        print("No files to process.")
        return []

    # Calculate totals
    total_duration = sum(f['duration'] for f in files)
    total_estimate = sum(
        estimate_cost_and_time(str(f['path']), preprocess=preprocess)['estimated_time_seconds']
        for f in files
    )

    print(f"\n{'='*60}")
    print(f"Batch Processing: {len(files)} files")
    print(f"{'='*60}")
    print(f"Total audio duration: {total_duration/60:.1f} minutes ({total_duration/3600:.1f} hours)")
    print(f"Estimated processing time: {total_estimate/60:.1f} minutes")
    print(f"Model: {model}")
    print(f"Preprocessing: {'enabled' if preprocess else 'disabled'}")
    print(f"{'='*60}\n")

    results = []

    for i, file_info in enumerate(files, 1):
        print(f"\n[{i}/{len(files)}] Processing: {file_info['filename']}")
        print(f"Duration: {file_info['duration']/60:.1f} min")

        try:
            result = process_file(
                file_info['path'],
                model=model,
                preprocess=preprocess,
                sync_to_db=True,
                move_completed=True
            )
            results.append(result)
            print(f"Completed: {result['word_count']} words in {result['transcription_time']:.1f}s")

        except Exception as e:
            print(f"Error: {e}")
            results.append({
                'filename': file_info['filename'],
                'error': str(e),
                'status': 'failed'
            })

    # Summary
    print(f"\n{'='*60}")
    print("Batch Processing Complete")
    print(f"{'='*60}")

    successful = [r for r in results if 'error' not in r]
    failed = [r for r in results if 'error' in r]

    print(f"Successful: {len(successful)}/{len(results)}")
    if failed:
        print(f"Failed: {len(failed)}")
        for f in failed:
            print(f"  - {f['filename']}: {f['error']}")

    if successful:
        total_time = sum(r['transcription_time'] for r in successful)
        total_words = sum(r['word_count'] for r in successful)
        print(f"Total transcription time: {total_time/60:.1f} minutes")
        print(f"Total words: {total_words}")

    return results


def show_queue_status():
    """Display current queue status."""
    files = get_new_files()

    print(f"\n{'='*60}")
    print("Inbox Status")
    print(f"{'='*60}")

    if not files:
        print("No files in inbox.")
        return

    new_files = [f for f in files if f['status'] == 'new']
    pending = [f for f in files if f['status'] == 'pending_in_queue']
    completed = [f for f in files if f['status'] == 'already_completed']
    processing = [f for f in files if f['status'] == 'processing']

    print(f"\nNew files (not in database): {len(new_files)}")
    for f in new_files:
        est = estimate_cost_and_time(str(f['path']))
        print(f"  - {f['filename']} ({f['duration']/60:.1f} min, ~{est['estimated_time_minutes']:.1f} min to process)")

    if pending:
        print(f"\nPending in queue: {len(pending)}")
        for f in pending:
            print(f"  - {f['filename']}")

    if processing:
        print(f"\nCurrently processing: {len(processing)}")
        for f in processing:
            print(f"  - {f['filename']}")

    if completed:
        print(f"\nAlready completed: {len(completed)}")
        for f in completed:
            print(f"  - {f['filename']}")

    # Overall stats
    try:
        stats = get_stats()
        print(f"\nDatabase totals:")
        print(f"  Total files: {stats['total_files']}")
        print(f"  Hours transcribed: {stats['total_duration_hours']:.1f}")
    except:
        pass


if __name__ == "__main__":
    import argparse

    parser = argparse.ArgumentParser(description="Batch process voice memos")
    parser.add_argument("--status", action="store_true",
                        help="Show queue status without processing")
    parser.add_argument("--model", default="large-v3", choices=list(MLX_MODELS.keys()),
                        help="MLX Whisper model size (default: large-v3)")
    parser.add_argument("--no-preprocess", action="store_true",
                        help="Skip preprocessing")
    parser.add_argument("--limit", type=int,
                        help="Maximum number of files to process")
    parser.add_argument("--include-completed", action="store_true",
                        help="Re-process files that were already completed")
    parser.add_argument("--add-only", action="store_true",
                        help="Only add files to queue, don't process")

    args = parser.parse_args()

    if args.status:
        show_queue_status()
        sys.exit(0)

    if args.add_only:
        files = get_new_files()
        new_files = [f for f in files if f['status'] == 'new']

        if not new_files:
            print("No new files to add.")
            sys.exit(0)

        print(f"Adding {len(new_files)} files to queue...")
        for f in new_files:
            memo = add_to_queue(f['path'], preprocess=not args.no_preprocess)
            print(f"  Added: {f['filename']}")

        print("Done.")
        sys.exit(0)

    # Full batch processing
    model = MLX_MODELS.get(args.model, args.model)

    results = batch_process(
        model=model,
        preprocess=not args.no_preprocess,
        limit=args.limit,
        skip_completed=not args.include_completed
    )
