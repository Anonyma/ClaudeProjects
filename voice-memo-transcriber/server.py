#!/usr/bin/env python3
"""
Local transcription server for Voice Memo Transcriber.
Provides REST API for the web dashboard to transcribe audio files.
"""

import os
import sys
import json
import tempfile
import hashlib
import subprocess
from pathlib import Path
from datetime import datetime
from flask import Flask, request, jsonify
from flask_cors import CORS
from werkzeug.utils import secure_filename
from dotenv import load_dotenv

# Add scripts directory to path
sys.path.insert(0, str(Path(__file__).parent / "scripts"))
from preprocess import preprocess_audio, get_audio_duration, estimate_transcription_time
from transcribe import transcribe_with_mlx, transcribe_with_openai, MLX_MODELS

load_dotenv()

app = Flask(__name__)
CORS(app)  # Allow cross-origin requests from file:// and localhost

# Configuration
UPLOAD_FOLDER = Path(__file__).parent / "audio" / "uploads"
UPLOAD_FOLDER.mkdir(parents=True, exist_ok=True)
ALLOWED_EXTENSIONS = {'mp3', 'm4a', 'wav', 'ogg', 'flac', 'aac', 'wma', 'opus', 'webm'}
MAX_CONTENT_LENGTH = 500 * 1024 * 1024  # 500MB max

app.config['MAX_CONTENT_LENGTH'] = MAX_CONTENT_LENGTH


def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS


def compute_file_hash(file_path: str) -> str:
    """Compute SHA256 hash of a file."""
    sha256 = hashlib.sha256()
    with open(file_path, 'rb') as f:
        for chunk in iter(lambda: f.read(8192), b''):
            sha256.update(chunk)
    return sha256.hexdigest()


def speed_up_audio(input_path: str, output_path: str, speed: float = 1.5) -> bool:
    """Speed up audio using FFmpeg atempo filter."""
    # atempo filter only supports 0.5 to 2.0, chain for higher speeds
    filters = []
    remaining_speed = speed
    while remaining_speed > 2.0:
        filters.append("atempo=2.0")
        remaining_speed /= 2.0
    while remaining_speed < 0.5:
        filters.append("atempo=0.5")
        remaining_speed /= 0.5
    filters.append(f"atempo={remaining_speed}")

    filter_str = ",".join(filters)

    cmd = [
        'ffmpeg', '-y', '-i', input_path,
        '-af', filter_str,
        '-c:a', 'libmp3lame', '-b:a', '128k',
        output_path
    ]

    try:
        subprocess.run(cmd, capture_output=True, check=True)
        return True
    except subprocess.CalledProcessError as e:
        print(f"Error speeding up audio: {e}")
        return False


@app.route('/health', methods=['GET'])
def health_check():
    """Health check endpoint."""
    return jsonify({
        'status': 'ok',
        'service': 'voice-memo-transcriber',
        'mlx_available': True,
        'openai_available': bool(os.getenv('OPENAI_API_KEY'))
    })


@app.route('/estimate', methods=['POST'])
def estimate():
    """
    Estimate transcription time and cost.

    Expects multipart form with:
    - file: Audio file
    OR
    - duration: Duration in seconds (if file not provided)

    Optional:
    - speed: Speed multiplier (1.0 = normal, 1.5 = 1.5x faster)
    - remove_silence: Whether silence removal is enabled
    - compress: Whether compression is enabled
    """
    duration = None

    if 'file' in request.files:
        file = request.files['file']
        if file.filename == '':
            return jsonify({'error': 'No file selected'}), 400

        # Save temporarily to get duration
        temp_file = tempfile.NamedTemporaryFile(delete=False, suffix='.tmp')
        file.save(temp_file.name)
        duration = get_audio_duration(temp_file.name)
        os.unlink(temp_file.name)
    elif 'duration' in request.form:
        duration = float(request.form['duration'])
    else:
        return jsonify({'error': 'No file or duration provided'}), 400

    # Get preprocessing options
    speed = float(request.form.get('speed', 1.0))
    remove_silence = request.form.get('remove_silence', 'true').lower() == 'true'
    compress = request.form.get('compress', 'true').lower() == 'true'

    # Adjust duration for speed
    effective_duration = duration / speed

    # Estimate preprocessing reduction
    if remove_silence:
        effective_duration *= 0.8  # ~20% reduction from silence removal

    # MLX Whisper estimate (large-v3)
    mlx_time = estimate_transcription_time(effective_duration, "large-v3", preprocessed=compress)

    # OpenAI estimate (~2s per minute + 30s upload)
    openai_time = 30 + (effective_duration / 60) * 2
    openai_cost = (duration / 60) * 0.006  # $0.006 per minute of ORIGINAL audio

    return jsonify({
        'original_duration_seconds': duration,
        'original_duration_minutes': duration / 60,
        'effective_duration_seconds': effective_duration,
        'effective_duration_minutes': effective_duration / 60,
        'estimates': {
            'mlx_whisper': {
                'time_seconds': mlx_time,
                'time_minutes': mlx_time / 60,
                'cost_usd': 0,
                'method': 'local'
            },
            'openai': {
                'time_seconds': openai_time,
                'time_minutes': openai_time / 60,
                'cost_usd': openai_cost,
                'method': 'cloud'
            }
        },
        'preprocessing': {
            'speed': speed,
            'remove_silence': remove_silence,
            'compress': compress
        }
    })


@app.route('/transcribe', methods=['POST'])
def transcribe():
    """
    Transcribe an audio file.

    Expects multipart form with:
    - file: Audio file (required)
    - method: 'mlx' or 'openai' (default: 'mlx')
    - model: Model to use (default: 'large-v3' for mlx, 'whisper-1' for openai)
    - speed: Speed multiplier (default: 1.0)
    - remove_silence: 'true' or 'false' (default: 'true')
    - compress: 'true' or 'false' (default: 'true')
    """
    if 'file' not in request.files:
        return jsonify({'error': 'No file provided'}), 400

    file = request.files['file']
    if file.filename == '':
        return jsonify({'error': 'No file selected'}), 400

    if not allowed_file(file.filename):
        return jsonify({'error': f'Invalid file type. Allowed: {", ".join(ALLOWED_EXTENSIONS)}'}), 400

    # Get options
    method = request.form.get('method', 'mlx')
    model = request.form.get('model', 'large-v3' if method == 'mlx' else 'whisper-1')
    speed = float(request.form.get('speed', 1.0))
    remove_silence = request.form.get('remove_silence', 'true').lower() == 'true'
    compress = request.form.get('compress', 'true').lower() == 'true'

    # Save uploaded file
    filename = secure_filename(file.filename)
    upload_path = UPLOAD_FOLDER / filename
    file.save(str(upload_path))

    temp_files = [str(upload_path)]

    try:
        current_file = str(upload_path)
        original_duration = get_audio_duration(current_file)
        preprocess_stats = {
            'original_duration': original_duration,
            'speed_applied': speed,
            'silence_removed': remove_silence,
            'compressed': compress
        }

        # Step 1: Speed up if requested
        if speed != 1.0:
            sped_up_file = tempfile.NamedTemporaryFile(delete=False, suffix='.mp3')
            sped_up_file.close()
            temp_files.append(sped_up_file.name)

            if speed_up_audio(current_file, sped_up_file.name, speed):
                current_file = sped_up_file.name
                preprocess_stats['duration_after_speed'] = get_audio_duration(current_file)

        # Step 2: Preprocess (silence removal + compression)
        if remove_silence or compress:
            preprocessed_file = tempfile.NamedTemporaryFile(delete=False, suffix='.wav')
            preprocessed_file.close()
            temp_files.append(preprocessed_file.name)

            current_file, pp_stats = preprocess_audio(
                current_file,
                preprocessed_file.name,
                remove_silence_enabled=remove_silence,
                compress_enabled=compress
            )
            preprocess_stats.update(pp_stats)

        # Step 3: Transcribe
        file_hash = compute_file_hash(str(upload_path))

        if method == 'openai':
            if not os.getenv('OPENAI_API_KEY'):
                return jsonify({'error': 'OpenAI API key not configured'}), 500
            result = transcribe_with_openai(current_file, model)
        else:
            # Get full MLX model path
            mlx_model = MLX_MODELS.get(model, model)
            result = transcribe_with_mlx(current_file, mlx_model)

        # Build response
        transcript_text = result.get('text', '').strip()
        word_count = len(transcript_text.split())

        return jsonify({
            'success': True,
            'file_hash': file_hash,
            'filename': filename,
            'transcript': transcript_text,
            'word_count': word_count,
            'duration_seconds': original_duration,
            'transcription_time_seconds': result.get('transcription_time', 0),
            'method': method,
            'model': model,
            'cost_usd': result.get('cost_usd', 0),
            'preprocessing': preprocess_stats,
            'language': result.get('language', 'en'),
            'timestamp': datetime.now().isoformat()
        })

    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

    finally:
        # Clean up temp files
        for temp_file in temp_files:
            try:
                if os.path.exists(temp_file):
                    os.unlink(temp_file)
            except:
                pass


@app.route('/models', methods=['GET'])
def get_models():
    """List available models."""
    return jsonify({
        'mlx': [
            {'id': 'large-v3', 'name': 'Large V3 (Best quality)', 'speed': '~10x realtime'},
            {'id': 'large-v3-turbo', 'name': 'Large V3 Turbo (Fast)', 'speed': '~14x realtime'},
            {'id': 'medium', 'name': 'Medium (Balanced)', 'speed': '~7x realtime'},
            {'id': 'small', 'name': 'Small (Quick)', 'speed': '~12x realtime'},
            {'id': 'base', 'name': 'Base (Very quick)', 'speed': '~25x realtime'},
            {'id': 'tiny', 'name': 'Tiny (Fastest)', 'speed': '~50x realtime'},
        ],
        'openai': [
            {'id': 'whisper-1', 'name': 'Whisper (Cloud)', 'cost': '$0.006/min'}
        ]
    })


if __name__ == '__main__':
    print("\n" + "="*60)
    print("Voice Memo Transcriber - Local Server")
    print("="*60)
    print(f"MLX Whisper: Available")
    print(f"OpenAI API: {'Configured' if os.getenv('OPENAI_API_KEY') else 'Not configured'}")
    print(f"\nServer running at: http://localhost:5111")
    print("="*60 + "\n")

    app.run(host='0.0.0.0', port=5111, debug=False)
