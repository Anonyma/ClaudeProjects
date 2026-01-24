#!/usr/bin/env python3
"""
Local transcription server for Voice Memo Transcriber.
Provides REST API with real-time progress streaming via SSE.
Supports both MLX Whisper (Apple Silicon) and faster-whisper (CUDA/CPU).
"""

import os
import sys
import json
import tempfile
import hashlib
import subprocess
import threading
import time
import uuid
import platform
from pathlib import Path
from datetime import datetime
from flask import Flask, request, jsonify, Response
from flask_cors import CORS
from werkzeug.utils import secure_filename
from dotenv import load_dotenv

# Add scripts directory to path
sys.path.insert(0, str(Path(__file__).parent / "scripts"))
from preprocess import preprocess_audio, get_audio_duration, estimate_transcription_time

# Detect platform and available backends
IS_APPLE_SILICON = platform.processor() == 'arm' and platform.system() == 'Darwin'
MLX_AVAILABLE = False
FASTER_WHISPER_AVAILABLE = False
GPU_AVAILABLE = False

# Try to import MLX Whisper (Apple Silicon only)
if IS_APPLE_SILICON:
    try:
        import mlx_whisper
        MLX_AVAILABLE = True
    except ImportError:
        pass

# Try to import faster-whisper (CUDA/CPU)
if not MLX_AVAILABLE:
    try:
        from faster_whisper import WhisperModel
        FASTER_WHISPER_AVAILABLE = True
        # Check for CUDA GPU
        try:
            import torch
            GPU_AVAILABLE = torch.cuda.is_available()
        except ImportError:
            GPU_AVAILABLE = False
    except ImportError:
        pass

# Import MLX_MODELS if available
try:
    from transcribe import MLX_MODELS
except ImportError:
    MLX_MODELS = {
        'tiny': 'mlx-community/whisper-tiny-mlx',
        'base': 'mlx-community/whisper-base-mlx',
        'small': 'mlx-community/whisper-small-mlx',
        'medium': 'mlx-community/whisper-medium-mlx',
        'large-v3': 'mlx-community/whisper-large-v3-mlx',
        'large-v3-turbo': 'mlx-community/whisper-large-v3-turbo',
    }

# faster-whisper model names (same as OpenAI model names)
FASTER_WHISPER_MODELS = {
    'tiny': 'tiny',
    'base': 'base',
    'small': 'small',
    'medium': 'medium',
    'large-v3': 'large-v3',
    'large-v3-turbo': 'large-v3-turbo',
}

load_dotenv()

app = Flask(__name__)
CORS(app)

# Configuration
UPLOAD_FOLDER = Path(__file__).parent / "audio" / "uploads"
UPLOAD_FOLDER.mkdir(parents=True, exist_ok=True)
ALLOWED_EXTENSIONS = {'mp3', 'm4a', 'wav', 'ogg', 'flac', 'aac', 'wma', 'opus', 'webm'}
MAX_CONTENT_LENGTH = 500 * 1024 * 1024  # 500MB max

app.config['MAX_CONTENT_LENGTH'] = MAX_CONTENT_LENGTH

# Job tracking for progress updates
jobs = {}  # job_id -> {status, progress, message, result, error}


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
    except subprocess.CalledProcessError:
        return False


def update_job(job_id: str, **kwargs):
    """Update job status."""
    if job_id in jobs:
        jobs[job_id].update(kwargs)
        jobs[job_id]['updated_at'] = time.time()


def transcribe_with_mlx_progress(audio_path: str, model: str, job_id: str) -> dict:
    """Transcribe with MLX Whisper, updating job progress."""
    if not MLX_AVAILABLE:
        raise RuntimeError("mlx-whisper not available on this platform")

    update_job(job_id, status='transcribing', message=f'Loading model: {model}', progress=5)

    start_time = time.time()
    duration = get_audio_duration(audio_path)

    # MLX Whisper doesn't have a built-in progress callback, but we can estimate
    # based on time elapsed vs expected time
    expected_time = duration * 0.1  # ~10x realtime for large-v3

    def progress_thread():
        """Background thread to estimate and update progress."""
        while job_id in jobs and jobs[job_id]['status'] == 'transcribing':
            elapsed = time.time() - start_time
            # Progress from 10% to 95% based on elapsed/expected time
            estimated_progress = min(95, 10 + (elapsed / expected_time) * 85)
            update_job(job_id,
                progress=int(estimated_progress),
                message=f'Transcribing... {int(elapsed)}s elapsed'
            )
            time.sleep(2)

    # Start progress estimation thread
    progress_estimator = threading.Thread(target=progress_thread, daemon=True)
    progress_estimator.start()

    # Run transcription
    import mlx_whisper
    result = mlx_whisper.transcribe(
        audio_path,
        path_or_hf_repo=model,
        verbose=False
    )

    elapsed = time.time() - start_time

    return {
        'text': result.get('text', ''),
        'segments': result.get('segments', []),
        'language': result.get('language', 'en'),
        'duration': duration,
        'transcription_time': elapsed,
        'model': model,
        'method': 'mlx_whisper'
    }


def transcribe_with_faster_whisper_progress(audio_path: str, model: str, job_id: str) -> dict:
    """Transcribe with faster-whisper (CUDA/CPU), updating job progress."""
    if not FASTER_WHISPER_AVAILABLE:
        raise RuntimeError("faster-whisper not installed")

    from faster_whisper import WhisperModel

    update_job(job_id, status='transcribing', message=f'Loading model: {model}', progress=5)

    start_time = time.time()
    duration = get_audio_duration(audio_path)

    # Determine compute device and type
    if GPU_AVAILABLE:
        device = "cuda"
        compute_type = "float16"
        update_job(job_id, message=f'Loading model on GPU: {model}', progress=8)
    else:
        device = "cpu"
        compute_type = "int8"
        update_job(job_id, message=f'Loading model on CPU: {model}', progress=8)

    # Load model
    whisper_model = WhisperModel(model, device=device, compute_type=compute_type)

    # Expected transcription speed
    if GPU_AVAILABLE:
        expected_time = duration * 0.05  # ~20x realtime with GPU
    else:
        expected_time = duration * 0.3   # ~3x realtime on CPU

    def progress_thread():
        """Background thread to estimate and update progress."""
        while job_id in jobs and jobs[job_id]['status'] == 'transcribing':
            elapsed = time.time() - start_time
            estimated_progress = min(95, 10 + (elapsed / expected_time) * 85)
            gpu_status = " (GPU)" if GPU_AVAILABLE else " (CPU)"
            update_job(job_id,
                progress=int(estimated_progress),
                message=f'Transcribing{gpu_status}... {int(elapsed)}s elapsed'
            )
            time.sleep(2)

    # Start progress estimation thread
    progress_estimator = threading.Thread(target=progress_thread, daemon=True)
    progress_estimator.start()

    # Run transcription
    segments, info = whisper_model.transcribe(audio_path, beam_size=5)

    # Collect all segments
    all_segments = []
    full_text = []
    for segment in segments:
        all_segments.append({
            'start': segment.start,
            'end': segment.end,
            'text': segment.text
        })
        full_text.append(segment.text)

    elapsed = time.time() - start_time

    return {
        'text': ' '.join(full_text),
        'segments': all_segments,
        'language': info.language,
        'duration': duration,
        'transcription_time': elapsed,
        'model': model,
        'method': 'faster_whisper',
        'device': device
    }


def transcribe_with_openai_progress(audio_path: str, model: str, job_id: str) -> dict:
    """Transcribe with OpenAI API, updating job progress."""
    api_key = os.getenv('OPENAI_API_KEY')
    if not api_key:
        raise ValueError("OPENAI_API_KEY not set")

    try:
        from openai import OpenAI
    except ImportError:
        raise RuntimeError("openai not installed")

    client = OpenAI(api_key=api_key)
    duration = get_audio_duration(audio_path)

    update_job(job_id, status='transcribing', message='Uploading to OpenAI...', progress=20)

    start_time = time.time()

    with open(audio_path, 'rb') as audio_file:
        update_job(job_id, message='Processing with OpenAI...', progress=50)
        response = client.audio.transcriptions.create(
            model=model,
            file=audio_file,
            response_format="verbose_json"
        )

    elapsed = time.time() - start_time
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


def process_transcription(job_id: str, file_path: str, options: dict):
    """Background worker for transcription."""
    temp_files = [file_path]

    try:
        current_file = file_path
        original_duration = get_audio_duration(current_file)

        update_job(job_id,
            status='preprocessing',
            message=f'Processing {original_duration/60:.1f} min audio...',
            progress=2,
            duration=original_duration
        )

        preprocess_stats = {
            'original_duration': original_duration,
            'speed_applied': options.get('speed', 1.0),
            'silence_removed': options.get('remove_silence', True),
            'compressed': options.get('compress', True)
        }

        # Speed up if requested
        speed = options.get('speed', 1.0)
        if speed != 1.0:
            update_job(job_id, message=f'Speeding up audio ({speed}x)...', progress=3)
            sped_up_file = tempfile.NamedTemporaryFile(delete=False, suffix='.mp3')
            sped_up_file.close()
            temp_files.append(sped_up_file.name)
            if speed_up_audio(current_file, sped_up_file.name, speed):
                current_file = sped_up_file.name

        # Preprocess (silence removal + compression)
        remove_silence = options.get('remove_silence', True)
        compress = options.get('compress', True)

        if remove_silence or compress:
            update_job(job_id, message='Removing silence & compressing...', progress=5)
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

        # Transcribe
        method = options.get('method', 'auto')
        model = options.get('model', 'large-v3')

        update_job(job_id, status='transcribing', message='Starting transcription...', progress=10)

        if method == 'openai':
            result = transcribe_with_openai_progress(current_file, 'whisper-1', job_id)
        elif method == 'mlx' or (method == 'auto' and MLX_AVAILABLE):
            mlx_model = MLX_MODELS.get(model, model)
            result = transcribe_with_mlx_progress(current_file, mlx_model, job_id)
        elif method == 'faster-whisper' or (method == 'auto' and FASTER_WHISPER_AVAILABLE):
            fw_model = FASTER_WHISPER_MODELS.get(model, model)
            result = transcribe_with_faster_whisper_progress(current_file, fw_model, job_id)
        else:
            raise RuntimeError("No transcription backend available. Install mlx-whisper or faster-whisper.")

        # Build final result
        transcript_text = result.get('text', '').strip()
        word_count = len(transcript_text.split())

        final_result = {
            'success': True,
            'filename': options.get('filename', 'audio'),
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
        }

        update_job(job_id,
            status='completed',
            message='Transcription complete!',
            progress=100,
            result=final_result
        )

        # Send macOS notification
        try:
            subprocess.run([
                'osascript', '-e',
                f'display notification "Transcription complete: {word_count} words" with title "Voice Memo Transcriber"'
            ], capture_output=True)
        except:
            pass

    except Exception as e:
        update_job(job_id,
            status='error',
            message=str(e),
            progress=0,
            error=str(e)
        )

    finally:
        # Clean up temp files
        for temp_file in temp_files:
            try:
                if os.path.exists(temp_file):
                    os.unlink(temp_file)
            except:
                pass


@app.route('/health', methods=['GET'])
def health_check():
    """Health check endpoint."""
    # Determine backend type
    if MLX_AVAILABLE:
        backend_type = 'mlx'
    elif FASTER_WHISPER_AVAILABLE:
        backend_type = 'faster-whisper'
    else:
        backend_type = 'none'

    return jsonify({
        'status': 'ok',
        'service': 'voice-memo-transcriber',
        'platform': platform.system(),
        'processor': platform.processor(),
        'backend_type': backend_type,
        'mlx_available': MLX_AVAILABLE,
        'faster_whisper_available': FASTER_WHISPER_AVAILABLE,
        'gpu_available': GPU_AVAILABLE,
        'openai_available': bool(os.getenv('OPENAI_API_KEY')),
        'active_jobs': len([j for j in jobs.values() if j['status'] in ('preprocessing', 'transcribing')])
    })


@app.route('/transcribe', methods=['POST'])
def transcribe():
    """
    Start transcription job. Returns job_id immediately.
    Poll /job/<job_id> or subscribe to /progress/<job_id> for updates.
    """
    if 'file' not in request.files:
        return jsonify({'error': 'No file provided'}), 400

    file = request.files['file']
    if file.filename == '':
        return jsonify({'error': 'No file selected'}), 400

    if not allowed_file(file.filename):
        return jsonify({'error': f'Invalid file type'}), 400

    # Create job
    job_id = str(uuid.uuid4())[:8]
    filename = secure_filename(file.filename)

    # Save uploaded file
    upload_path = UPLOAD_FOLDER / f"{job_id}_{filename}"
    file.save(str(upload_path))

    # Initialize job
    jobs[job_id] = {
        'id': job_id,
        'filename': filename,
        'status': 'queued',
        'progress': 0,
        'message': 'Starting...',
        'result': None,
        'error': None,
        'created_at': time.time(),
        'updated_at': time.time()
    }

    # Get options
    options = {
        'method': request.form.get('method', 'mlx'),
        'model': request.form.get('model', 'large-v3'),
        'speed': float(request.form.get('speed', 1.0)),
        'remove_silence': request.form.get('remove_silence', 'true').lower() == 'true',
        'compress': request.form.get('compress', 'true').lower() == 'true',
        'filename': filename
    }

    # Start background processing
    thread = threading.Thread(
        target=process_transcription,
        args=(job_id, str(upload_path), options),
        daemon=True
    )
    thread.start()

    return jsonify({
        'job_id': job_id,
        'filename': filename,
        'status': 'queued',
        'message': 'Transcription started'
    })


@app.route('/job/<job_id>', methods=['GET'])
def get_job(job_id):
    """Get job status."""
    if job_id not in jobs:
        return jsonify({'error': 'Job not found'}), 404
    return jsonify(jobs[job_id])


@app.route('/progress/<job_id>', methods=['GET'])
def progress_stream(job_id):
    """Server-Sent Events stream for real-time progress updates."""
    def generate():
        if job_id not in jobs:
            yield f"data: {json.dumps({'error': 'Job not found'})}\n\n"
            return

        last_update = 0
        while True:
            job = jobs.get(job_id)
            if not job:
                break

            # Send update if changed
            if job['updated_at'] > last_update:
                last_update = job['updated_at']
                yield f"data: {json.dumps(job)}\n\n"

            # Stop if completed or errored
            if job['status'] in ('completed', 'error'):
                break

            time.sleep(0.5)

    return Response(
        generate(),
        mimetype='text/event-stream',
        headers={
            'Cache-Control': 'no-cache',
            'Connection': 'keep-alive',
            'Access-Control-Allow-Origin': '*'
        }
    )


@app.route('/jobs', methods=['GET'])
def list_jobs():
    """List all jobs."""
    return jsonify({
        'jobs': list(jobs.values()),
        'active': len([j for j in jobs.values() if j['status'] in ('queued', 'preprocessing', 'transcribing')])
    })


@app.route('/models', methods=['GET'])
def get_models():
    """List available models."""
    return jsonify({
        'mlx': [
            {'id': 'large-v3', 'name': 'Large V3 (Best quality)', 'speed': '~10x realtime'},
            {'id': 'large-v3-turbo', 'name': 'Large V3 Turbo (Fast)', 'speed': '~14x realtime'},
            {'id': 'medium', 'name': 'Medium (Balanced)', 'speed': '~7x realtime'},
            {'id': 'small', 'name': 'Small (Quick)', 'speed': '~12x realtime'},
        ],
        'openai': [
            {'id': 'whisper-1', 'name': 'Whisper (Cloud)', 'cost': '$0.006/min'}
        ]
    })


if __name__ == '__main__':
    import argparse

    parser = argparse.ArgumentParser(description='Voice Memo Transcriber Server')
    parser.add_argument('--host', default='0.0.0.0', help='Host to bind to')
    parser.add_argument('--port', type=int, default=5111, help='Port to listen on')
    args = parser.parse_args()

    print("\n" + "="*60)
    print("Voice Memo Transcriber - Local Server")
    print("="*60)
    print(f"Platform: {platform.system()} ({platform.processor()})")

    if MLX_AVAILABLE:
        print(f"Backend: MLX Whisper (Apple Silicon)")
    elif FASTER_WHISPER_AVAILABLE:
        device = "CUDA GPU" if GPU_AVAILABLE else "CPU"
        print(f"Backend: faster-whisper ({device})")
    else:
        print(f"Backend: None available (install mlx-whisper or faster-whisper)")

    print(f"OpenAI API: {'Configured' if os.getenv('OPENAI_API_KEY') else 'Not configured'}")
    print(f"\nServer running at: http://{args.host}:{args.port}")
    print("="*60 + "\n")

    app.run(host=args.host, port=args.port, debug=False, threaded=True)
