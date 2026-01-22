#!/usr/bin/env python3
"""
Supabase sync utilities for voice memo transcription.
Handles persistence of memos and transcripts to Supabase.
"""

import os
import sys
from pathlib import Path
from datetime import datetime
from typing import Optional, List

from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Supabase configuration
SUPABASE_URL = os.getenv('SUPABASE_URL')
SUPABASE_KEY = os.getenv('SUPABASE_ANON_KEY') or os.getenv('SUPABASE_KEY')  # Use anon/public key


def get_supabase_client():
    """Get Supabase client instance."""
    if not SUPABASE_URL or not SUPABASE_KEY:
        raise ValueError(
            "SUPABASE_URL and SUPABASE_KEY must be set in environment.\n"
            "Add them to your .env file."
        )

    try:
        from supabase import create_client
    except ImportError:
        print("Error: supabase not installed. Run: pip install supabase")
        sys.exit(1)

    return create_client(SUPABASE_URL, SUPABASE_KEY)


def create_memo(
    file_hash: str,
    filename: str,
    duration_seconds: float,
    model_used: Optional[str] = None,
    preprocessing_applied: bool = False,
    estimated_seconds: Optional[float] = None
) -> dict:
    """
    Create a new voice memo record.

    Args:
        file_hash: SHA256 hash of the file (for deduplication)
        filename: Original filename
        duration_seconds: Audio duration in seconds
        model_used: Transcription model used
        preprocessing_applied: Whether preprocessing was applied
        estimated_seconds: Estimated transcription time

    Returns:
        Created memo record
    """
    client = get_supabase_client()

    data = {
        'file_hash': file_hash,
        'filename': filename,
        'duration_seconds': duration_seconds,
        'status': 'pending',
        'model_used': model_used,
        'preprocessing_applied': preprocessing_applied,
        'estimated_seconds': estimated_seconds
    }

    result = client.table('voice_memos').insert(data).execute()
    return result.data[0] if result.data else None


def get_memo_by_hash(file_hash: str) -> Optional[dict]:
    """
    Get a memo by its file hash.

    Args:
        file_hash: SHA256 hash of the file

    Returns:
        Memo record or None if not found
    """
    client = get_supabase_client()
    result = client.table('voice_memos').select('*').eq('file_hash', file_hash).execute()
    return result.data[0] if result.data else None


def get_memo_by_id(memo_id: str) -> Optional[dict]:
    """Get a memo by its ID."""
    client = get_supabase_client()
    result = client.table('voice_memos').select('*').eq('id', memo_id).execute()
    return result.data[0] if result.data else None


def update_memo_status(
    memo_id: str,
    status: str,
    actual_seconds: Optional[float] = None,
    model_used: Optional[str] = None
) -> dict:
    """
    Update memo status.

    Args:
        memo_id: Memo UUID
        status: New status (pending/processing/completed/failed)
        actual_seconds: Actual transcription time (if completed)
        model_used: Model used for transcription

    Returns:
        Updated memo record
    """
    client = get_supabase_client()

    data = {'status': status}
    if actual_seconds is not None:
        data['actual_seconds'] = actual_seconds
    if model_used is not None:
        data['model_used'] = model_used

    result = client.table('voice_memos').update(data).eq('id', memo_id).execute()
    return result.data[0] if result.data else None


def create_transcript(
    memo_id: str,
    transcript_text: str,
    word_count: Optional[int] = None
) -> dict:
    """
    Create a transcript for a memo.

    Args:
        memo_id: Associated memo UUID
        transcript_text: Full transcript text
        word_count: Number of words in transcript

    Returns:
        Created transcript record
    """
    client = get_supabase_client()

    if word_count is None:
        word_count = len(transcript_text.split())

    data = {
        'memo_id': memo_id,
        'transcript_text': transcript_text,
        'word_count': word_count
    }

    result = client.table('voice_transcripts').insert(data).execute()
    return result.data[0] if result.data else None


def update_transcript(transcript_id: str, transcript_text: str) -> dict:
    """
    Update an existing transcript.

    Args:
        transcript_id: Transcript UUID
        transcript_text: Updated transcript text

    Returns:
        Updated transcript record
    """
    client = get_supabase_client()

    word_count = len(transcript_text.split())
    data = {
        'transcript_text': transcript_text,
        'word_count': word_count
    }

    result = client.table('voice_transcripts').update(data).eq('id', transcript_id).execute()
    return result.data[0] if result.data else None


def get_transcript_by_memo(memo_id: str) -> Optional[dict]:
    """Get transcript for a memo."""
    client = get_supabase_client()
    result = client.table('voice_transcripts').select('*').eq('memo_id', memo_id).execute()
    return result.data[0] if result.data else None


def list_memos(status: Optional[str] = None, limit: int = 100) -> List[dict]:
    """
    List all memos, optionally filtered by status.

    Args:
        status: Filter by status (pending/processing/completed/failed)
        limit: Maximum number of records to return

    Returns:
        List of memo records
    """
    client = get_supabase_client()

    query = client.table('voice_memos').select('*').order('created_at', desc=True).limit(limit)
    if status:
        query = query.eq('status', status)

    result = query.execute()
    return result.data or []


def list_memos_with_transcripts(limit: int = 100) -> List[dict]:
    """
    List all memos with their transcripts joined.

    Returns:
        List of memos with transcript data
    """
    client = get_supabase_client()

    result = client.table('voice_memos').select(
        '*, voice_transcripts(*)'
    ).order('created_at', desc=True).limit(limit).execute()

    return result.data or []


def delete_memo(memo_id: str) -> bool:
    """
    Delete a memo and its transcript (cascade).

    Args:
        memo_id: Memo UUID

    Returns:
        True if deleted successfully
    """
    client = get_supabase_client()
    result = client.table('voice_memos').delete().eq('id', memo_id).execute()
    return len(result.data) > 0


def sync_transcription_result(result: dict) -> dict:
    """
    Sync a transcription result to Supabase.
    Creates memo if not exists, updates if exists, and saves transcript.

    Args:
        result: Result dict from transcribe_file()

    Returns:
        dict with memo_id and transcript_id
    """
    # Check if memo exists
    existing = get_memo_by_hash(result['file_hash'])

    if existing:
        memo_id = existing['id']
        # Update memo status
        update_memo_status(
            memo_id,
            status='completed',
            actual_seconds=result['transcription_time'],
            model_used=result['model_used']
        )

        # Check if transcript exists
        existing_transcript = get_transcript_by_memo(memo_id)
        if existing_transcript:
            # Update existing transcript
            transcript = update_transcript(
                existing_transcript['id'],
                result['transcript_text']
            )
            transcript_id = existing_transcript['id']
        else:
            # Create new transcript
            transcript = create_transcript(
                memo_id,
                result['transcript_text'],
                result['word_count']
            )
            transcript_id = transcript['id']
    else:
        # Create new memo
        memo = create_memo(
            file_hash=result['file_hash'],
            filename=result['filename'],
            duration_seconds=result['duration_seconds'],
            model_used=result['model_used'],
            preprocessing_applied=result.get('preprocessing_applied', False)
        )
        memo_id = memo['id']

        # Update to completed
        update_memo_status(
            memo_id,
            status='completed',
            actual_seconds=result['transcription_time']
        )

        # Create transcript
        transcript = create_transcript(
            memo_id,
            result['transcript_text'],
            result['word_count']
        )
        transcript_id = transcript['id']

    return {
        'memo_id': memo_id,
        'transcript_id': transcript_id
    }


def get_stats() -> dict:
    """
    Get summary statistics.

    Returns:
        dict with counts and totals
    """
    client = get_supabase_client()

    memos = client.table('voice_memos').select('status, duration_seconds').execute()

    stats = {
        'total_files': len(memos.data),
        'pending': 0,
        'processing': 0,
        'completed': 0,
        'failed': 0,
        'total_duration_hours': 0
    }

    for memo in memos.data:
        status = memo.get('status', 'pending')
        stats[status] = stats.get(status, 0) + 1
        if memo.get('duration_seconds'):
            stats['total_duration_hours'] += memo['duration_seconds'] / 3600

    return stats


if __name__ == "__main__":
    import argparse

    parser = argparse.ArgumentParser(description="Supabase sync utilities")
    parser.add_argument("--list", action="store_true", help="List all memos")
    parser.add_argument("--pending", action="store_true", help="List pending memos")
    parser.add_argument("--stats", action="store_true", help="Show statistics")
    parser.add_argument("--check-hash", help="Check if file hash exists")

    args = parser.parse_args()

    try:
        if args.stats:
            stats = get_stats()
            print("Voice Memo Statistics:")
            print(f"  Total files: {stats['total_files']}")
            print(f"  Pending: {stats['pending']}")
            print(f"  Processing: {stats['processing']}")
            print(f"  Completed: {stats['completed']}")
            print(f"  Failed: {stats['failed']}")
            print(f"  Total duration: {stats['total_duration_hours']:.1f} hours")

        elif args.pending:
            memos = list_memos(status='pending')
            print(f"Pending memos: {len(memos)}")
            for memo in memos:
                print(f"  - {memo['filename']} ({memo['duration_seconds']/60:.1f} min)")

        elif args.list:
            memos = list_memos_with_transcripts()
            print(f"All memos: {len(memos)}")
            for memo in memos:
                transcript_preview = ""
                if memo.get('voice_transcripts'):
                    text = memo['voice_transcripts'][0].get('transcript_text', '')[:50]
                    transcript_preview = f" - {text}..."
                print(f"  [{memo['status']}] {memo['filename']}{transcript_preview}")

        elif args.check_hash:
            memo = get_memo_by_hash(args.check_hash)
            if memo:
                print(f"Found: {memo['filename']} (status: {memo['status']})")
            else:
                print("Not found")

        else:
            parser.print_help()

    except Exception as e:
        print(f"Error: {e}")
        sys.exit(1)
