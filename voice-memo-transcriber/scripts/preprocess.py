#!/usr/bin/env python3
"""
Audio preprocessing for voice memo transcription.
Uses FFmpeg for silence removal and compression to speed up transcription.
"""

import subprocess
import tempfile
import os
import sys
from pathlib import Path


def get_audio_duration(file_path: str) -> float:
    """Get audio duration in seconds using ffprobe."""
    cmd = [
        'ffprobe', '-v', 'quiet', '-show_entries', 'format=duration',
        '-of', 'default=noprint_wrappers=1:nokey=1', file_path
    ]
    try:
        result = subprocess.run(cmd, capture_output=True, text=True, check=True)
        return float(result.stdout.strip())
    except (subprocess.CalledProcessError, ValueError):
        return 0.0


def remove_silence(input_path: str, output_path: str,
                   noise_threshold: str = "-50dB",
                   min_silence_duration: float = 0.5) -> bool:
    """
    Remove silence from audio file.

    Args:
        input_path: Input audio file path
        output_path: Output audio file path
        noise_threshold: Volume threshold for silence detection (default -50dB)
        min_silence_duration: Minimum duration to consider as silence (default 0.5s)

    Returns:
        True if successful, False otherwise
    """
    # FFmpeg silenceremove filter
    # stop_periods=-1 means process entire file
    # stop_duration is minimum silence duration
    # stop_threshold is the volume threshold
    filter_complex = (
        f"silenceremove=stop_periods=-1:stop_duration={min_silence_duration}:"
        f"stop_threshold={noise_threshold}"
    )

    cmd = [
        'ffmpeg', '-y', '-i', input_path,
        '-af', filter_complex,
        '-c:a', 'copy' if output_path.endswith('.m4a') else 'libmp3lame',
        output_path
    ]

    try:
        subprocess.run(cmd, capture_output=True, check=True)
        return True
    except subprocess.CalledProcessError as e:
        print(f"Error removing silence: {e.stderr.decode() if e.stderr else str(e)}")
        return False


def compress_audio(input_path: str, output_path: str,
                   sample_rate: int = 16000,
                   bitrate: str = "64k",
                   mono: bool = True) -> bool:
    """
    Compress audio for faster transcription.
    Whisper works best with 16kHz mono audio.

    Args:
        input_path: Input audio file path
        output_path: Output audio file path (should be .wav or .mp3)
        sample_rate: Target sample rate (default 16000 for Whisper)
        bitrate: Target bitrate for lossy formats
        mono: Convert to mono (default True)

    Returns:
        True if successful, False otherwise
    """
    cmd = [
        'ffmpeg', '-y', '-i', input_path,
        '-ar', str(sample_rate),
        '-ac', '1' if mono else '2',
    ]

    # Add codec based on output format
    if output_path.endswith('.wav'):
        cmd.extend(['-c:a', 'pcm_s16le'])
    elif output_path.endswith('.mp3'):
        cmd.extend(['-c:a', 'libmp3lame', '-b:a', bitrate])
    elif output_path.endswith('.m4a'):
        cmd.extend(['-c:a', 'aac', '-b:a', bitrate])

    cmd.append(output_path)

    try:
        subprocess.run(cmd, capture_output=True, check=True)
        return True
    except subprocess.CalledProcessError as e:
        print(f"Error compressing audio: {e.stderr.decode() if e.stderr else str(e)}")
        return False


def preprocess_audio(input_path: str, output_path: str = None,
                     remove_silence_enabled: bool = True,
                     compress_enabled: bool = True) -> tuple[str, dict]:
    """
    Full preprocessing pipeline: silence removal + compression.

    Args:
        input_path: Input audio file path
        output_path: Output file path (default: input with _preprocessed suffix)
        remove_silence_enabled: Whether to remove silence
        compress_enabled: Whether to compress audio

    Returns:
        Tuple of (output_path, stats_dict)
    """
    input_path = Path(input_path)

    if output_path is None:
        output_path = input_path.parent / f"{input_path.stem}_preprocessed.wav"
    output_path = Path(output_path)

    stats = {
        'original_duration': get_audio_duration(str(input_path)),
        'original_size': input_path.stat().st_size,
        'final_duration': 0,
        'final_size': 0,
        'silence_removed': remove_silence_enabled,
        'compressed': compress_enabled,
    }

    current_file = str(input_path)
    temp_files = []

    try:
        # Step 1: Remove silence
        if remove_silence_enabled:
            temp_silence = tempfile.NamedTemporaryFile(suffix='.wav', delete=False)
            temp_silence.close()
            temp_files.append(temp_silence.name)

            print(f"  Removing silence...")
            if remove_silence(current_file, temp_silence.name):
                current_file = temp_silence.name
                duration_after_silence = get_audio_duration(current_file)
                stats['duration_after_silence'] = duration_after_silence
                reduction = (1 - duration_after_silence / stats['original_duration']) * 100
                print(f"  Silence removal: {stats['original_duration']:.1f}s -> {duration_after_silence:.1f}s ({reduction:.1f}% reduction)")

        # Step 2: Compress
        if compress_enabled:
            print(f"  Compressing to 16kHz mono...")
            if compress_audio(current_file, str(output_path)):
                current_file = str(output_path)
            else:
                # If compression fails, just copy
                import shutil
                shutil.copy(current_file, str(output_path))
        else:
            # Just copy without compression
            import shutil
            shutil.copy(current_file, str(output_path))

        stats['final_duration'] = get_audio_duration(str(output_path))
        stats['final_size'] = output_path.stat().st_size

        size_reduction = (1 - stats['final_size'] / stats['original_size']) * 100
        print(f"  Size: {stats['original_size'] / 1024 / 1024:.1f}MB -> {stats['final_size'] / 1024 / 1024:.1f}MB ({size_reduction:.1f}% reduction)")

        return str(output_path), stats

    finally:
        # Clean up temp files
        for temp_file in temp_files:
            try:
                os.unlink(temp_file)
            except:
                pass


def estimate_transcription_time(duration_seconds: float, model: str = "large-v3",
                                preprocessed: bool = False) -> float:
    """
    Estimate transcription time based on audio duration and model.

    These estimates are for M1/M2/M3 Macs with MLX Whisper.
    Actual times may vary based on hardware and content.

    Args:
        duration_seconds: Audio duration in seconds
        model: Whisper model name
        preprocessed: Whether audio has been preprocessed

    Returns:
        Estimated transcription time in seconds
    """
    # Approximate real-time factors for MLX Whisper on Apple Silicon
    # (transcription_time / audio_duration)
    model_factors = {
        'tiny': 0.02,      # ~50x real-time
        'base': 0.04,      # ~25x real-time
        'small': 0.08,     # ~12x real-time
        'medium': 0.15,    # ~7x real-time
        'large-v3': 0.1,   # ~10x real-time (optimized for MLX)
        'large-v3-turbo': 0.07,  # ~14x real-time
    }

    factor = model_factors.get(model, 0.1)

    # Preprocessing typically reduces duration by 10-30%
    if preprocessed:
        duration_seconds *= 0.8  # Assume 20% reduction

    return duration_seconds * factor


if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Usage: python preprocess.py <audio_file> [--no-silence] [--no-compress]")
        sys.exit(1)

    input_file = sys.argv[1]
    remove_silence_flag = "--no-silence" not in sys.argv
    compress_flag = "--no-compress" not in sys.argv

    if not os.path.exists(input_file):
        print(f"Error: File not found: {input_file}")
        sys.exit(1)

    print(f"Preprocessing: {input_file}")
    output_file, stats = preprocess_audio(
        input_file,
        remove_silence_enabled=remove_silence_flag,
        compress_enabled=compress_flag
    )

    print(f"\nOutput: {output_file}")
    print(f"Original duration: {stats['original_duration']:.1f}s")
    print(f"Final duration: {stats['final_duration']:.1f}s")

    # Estimate transcription time
    est_time = estimate_transcription_time(stats['final_duration'], preprocessed=True)
    print(f"Estimated transcription time: {est_time / 60:.1f} minutes")
