#!/usr/bin/env python3
"""
Remote transcription CLI for Voice Memo Transcriber.
Orchestrates transcription across Mac (local), ASUS (GPU), and Windows backends.
"""

import os
import sys
import json
import time
import hashlib
import tempfile
import argparse
import subprocess
from pathlib import Path
from datetime import datetime
from typing import Optional

# Project paths
PROJECT_DIR = Path(__file__).parent.parent
CONFIG_PATH = PROJECT_DIR / "config.json"
TRANSCRIPTS_DIR = PROJECT_DIR / "transcripts"


def load_config() -> dict:
    """Load backend configuration."""
    if CONFIG_PATH.exists():
        with open(CONFIG_PATH) as f:
            return json.load(f)
    return {
        "backends": {
            "local": {"name": "Mac (Local)", "url": "http://localhost:5111", "priority": 2, "enabled": True}
        },
        "default_backend": "local"
    }


def check_backend_health(backend: dict, timeout: int = 5) -> dict:
    """Check if a backend server is available."""
    import urllib.request
    import urllib.error

    url = backend.get("url", "").rstrip("/") + "/health"
    try:
        req = urllib.request.Request(url, method="GET")
        with urllib.request.urlopen(req, timeout=timeout) as response:
            if response.status == 200:
                data = json.loads(response.read().decode())
                return {
                    "available": True,
                    "gpu": data.get("gpu_available", False),
                    "backend_type": data.get("backend_type", "unknown"),
                    "active_jobs": data.get("active_jobs", 0)
                }
    except (urllib.error.URLError, TimeoutError, json.JSONDecodeError):
        pass

    return {"available": False}


def check_ssh_connection(host: str, timeout: int = 5) -> bool:
    """Check if SSH connection to host is available."""
    try:
        result = subprocess.run(
            ["ssh", "-o", f"ConnectTimeout={timeout}", "-o", "BatchMode=yes", host, "echo ok"],
            capture_output=True,
            timeout=timeout + 2
        )
        return result.returncode == 0
    except (subprocess.TimeoutExpired, subprocess.SubprocessError):
        return False


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


def compute_file_hash(file_path: str) -> str:
    """Compute SHA256 hash of a file."""
    sha256 = hashlib.sha256()
    with open(file_path, 'rb') as f:
        for chunk in iter(lambda: f.read(8192), b''):
            sha256.update(chunk)
    return sha256.hexdigest()[:16]


def transfer_file_to_remote(local_path: str, remote_host: str, remote_path: str, timeout: int = 300) -> bool:
    """Copy file to remote machine via SCP."""
    print(f"  Transferring to {remote_host}...")
    try:
        # Ensure remote directory exists
        remote_dir = str(Path(remote_path).parent)
        subprocess.run(
            ["ssh", remote_host, f"mkdir -p {remote_dir}"],
            capture_output=True,
            timeout=30
        )

        # Transfer file
        result = subprocess.run(
            ["scp", "-q", local_path, f"{remote_host}:{remote_path}"],
            capture_output=True,
            timeout=timeout
        )
        return result.returncode == 0
    except subprocess.TimeoutExpired:
        print(f"  Transfer timed out after {timeout}s")
        return False
    except subprocess.SubprocessError as e:
        print(f"  Transfer error: {e}")
        return False


def transfer_file_from_remote(remote_host: str, remote_path: str, local_path: str, timeout: int = 60) -> bool:
    """Copy file from remote machine via SCP."""
    try:
        result = subprocess.run(
            ["scp", "-q", f"{remote_host}:{remote_path}", local_path],
            capture_output=True,
            timeout=timeout
        )
        return result.returncode == 0
    except (subprocess.TimeoutExpired, subprocess.SubprocessError):
        return False


def run_remote_transcription(
    audio_path: str,
    backend_config: dict,
    model: str = "large-v3",
    preprocess: bool = True
) -> dict:
    """Run transcription on a remote machine via SSH."""
    ssh_host = backend_config.get("ssh_host")
    remote_project = backend_config.get("remote_path", "~/voice-memo-transcriber")
    venv_path = backend_config.get("venv_path", "~/whisper-env")

    audio_path = Path(audio_path)
    file_hash = compute_file_hash(str(audio_path))

    # Remote paths
    remote_audio = f"/tmp/transcribe_{file_hash}{audio_path.suffix}"
    remote_transcript = f"/tmp/transcribe_{file_hash}.txt"

    print(f"\n{'='*60}")
    print(f"Remote Transcription: {audio_path.name}")
    print(f"Backend: {backend_config.get('name', ssh_host)}")
    print(f"{'='*60}")

    start_time = time.time()
    duration = get_audio_duration(str(audio_path))
    print(f"Duration: {duration/60:.1f} minutes")

    # Step 1: Transfer audio to remote
    if not transfer_file_to_remote(str(audio_path), ssh_host, remote_audio):
        raise RuntimeError(f"Failed to transfer file to {ssh_host}")

    transfer_time = time.time() - start_time
    print(f"  Transfer completed in {transfer_time:.1f}s")

    # Step 2: Run transcription remotely
    print(f"  Starting remote transcription...")
    preprocess_flag = "" if preprocess else "--no-preprocess"

    # Build the remote command
    if "windows" in ssh_host.lower() or backend_config.get("type") == "windows":
        # Windows command
        activate_cmd = f"{venv_path}\\Scripts\\activate.ps1"
        transcribe_cmd = f"cd {remote_project} && python scripts/transcribe.py \"{remote_audio}\" --model {model} {preprocess_flag} -o \"{remote_transcript}\""
    else:
        # Linux command
        activate_cmd = f"source {venv_path}/bin/activate"
        transcribe_cmd = f"{activate_cmd} && cd {remote_project} && python3 scripts/transcribe.py \"{remote_audio}\" --model {model} {preprocess_flag} -o \"{remote_transcript}\""

    try:
        result = subprocess.run(
            ["ssh", ssh_host, transcribe_cmd],
            capture_output=True,
            text=True,
            timeout=1800  # 30 minute timeout for long files
        )

        if result.returncode != 0:
            print(f"  Remote transcription failed:")
            print(f"  {result.stderr}")
            raise RuntimeError("Remote transcription failed")

        # Print remote output for visibility
        if result.stdout:
            for line in result.stdout.strip().split("\n"):
                if line.strip():
                    print(f"  [remote] {line}")

    except subprocess.TimeoutExpired:
        raise RuntimeError("Remote transcription timed out")

    transcription_time = time.time() - start_time - transfer_time
    print(f"  Transcription completed in {transcription_time:.1f}s")

    # Step 3: Retrieve transcript
    local_transcript = TRANSCRIPTS_DIR / f"{audio_path.stem}.txt"
    TRANSCRIPTS_DIR.mkdir(parents=True, exist_ok=True)

    if not transfer_file_from_remote(ssh_host, remote_transcript, str(local_transcript)):
        raise RuntimeError("Failed to retrieve transcript from remote")

    # Read transcript
    with open(local_transcript) as f:
        transcript_text = f.read().strip()

    # Step 4: Cleanup remote files
    subprocess.run(
        ["ssh", ssh_host, f"rm -f {remote_audio} {remote_transcript}"],
        capture_output=True,
        timeout=30
    )

    total_time = time.time() - start_time
    word_count = len(transcript_text.split())

    result = {
        "success": True,
        "filename": audio_path.name,
        "transcript_text": transcript_text,
        "transcript_path": str(local_transcript),
        "word_count": word_count,
        "duration_seconds": duration,
        "transcription_time": transcription_time,
        "transfer_time": transfer_time,
        "total_time": total_time,
        "model": model,
        "backend": backend_config.get("name", ssh_host),
        "method": "remote_ssh",
        "timestamp": datetime.now().isoformat()
    }

    print(f"\n{'='*60}")
    print("Summary:")
    print(f"{'='*60}")
    print(f"Words: {word_count}")
    print(f"Transfer time: {transfer_time:.1f}s")
    print(f"Transcription time: {transcription_time:.1f}s")
    print(f"Total time: {total_time:.1f}s")
    print(f"Speed: {duration/transcription_time:.1f}x real-time")
    print(f"Transcript: {local_transcript}")

    return result


def run_local_transcription(audio_path: str, model: str = "large-v3", preprocess: bool = True) -> dict:
    """Run transcription locally using the existing transcribe.py script."""
    from transcribe import transcribe_file, MLX_MODELS

    model_path = MLX_MODELS.get(model, model)
    return transcribe_file(
        audio_path,
        model=model_path,
        preprocess=preprocess
    )


def run_server_transcription(audio_path: str, backend_url: str, model: str = "large-v3") -> dict:
    """Run transcription via HTTP server API."""
    import urllib.request
    import urllib.error
    from urllib.parse import urljoin

    url = urljoin(backend_url.rstrip("/") + "/", "transcribe")
    audio_path = Path(audio_path)

    print(f"\n{'='*60}")
    print(f"Server Transcription: {audio_path.name}")
    print(f"Backend: {backend_url}")
    print(f"{'='*60}")

    # Build multipart form data
    boundary = "----WebKitFormBoundary" + hashlib.md5(str(time.time()).encode()).hexdigest()[:16]

    with open(audio_path, 'rb') as f:
        file_data = f.read()

    body = []

    # Add file field
    body.append(f'--{boundary}'.encode())
    body.append(f'Content-Disposition: form-data; name="file"; filename="{audio_path.name}"'.encode())
    body.append(b'Content-Type: audio/mpeg')
    body.append(b'')
    body.append(file_data)

    # Add model field
    body.append(f'--{boundary}'.encode())
    body.append(b'Content-Disposition: form-data; name="model"')
    body.append(b'')
    body.append(model.encode())

    body.append(f'--{boundary}--'.encode())
    body.append(b'')

    body_bytes = b'\r\n'.join(body)

    req = urllib.request.Request(
        url,
        data=body_bytes,
        headers={
            'Content-Type': f'multipart/form-data; boundary={boundary}',
            'Content-Length': str(len(body_bytes))
        },
        method='POST'
    )

    try:
        print("  Uploading file to server...")
        with urllib.request.urlopen(req, timeout=300) as response:
            data = json.loads(response.read().decode())

            if "job_id" in data:
                job_id = data["job_id"]
                print(f"  Job started: {job_id}")

                # Poll for completion
                job_url = urljoin(backend_url.rstrip("/") + "/", f"job/{job_id}")
                while True:
                    time.sleep(2)
                    job_req = urllib.request.Request(job_url, method='GET')
                    with urllib.request.urlopen(job_req, timeout=30) as job_resp:
                        job_data = json.loads(job_resp.read().decode())

                        status = job_data.get("status")
                        progress = job_data.get("progress", 0)
                        message = job_data.get("message", "")

                        print(f"  [{progress}%] {message}", end="\r")

                        if status == "completed":
                            print()
                            result = job_data.get("result", {})

                            # Save transcript locally
                            transcript_text = result.get("transcript", "")
                            local_transcript = TRANSCRIPTS_DIR / f"{audio_path.stem}.txt"
                            TRANSCRIPTS_DIR.mkdir(parents=True, exist_ok=True)
                            with open(local_transcript, 'w') as f:
                                f.write(transcript_text)

                            result["transcript_path"] = str(local_transcript)
                            return result

                        elif status == "error":
                            raise RuntimeError(job_data.get("error", "Unknown error"))

            return data

    except urllib.error.URLError as e:
        raise RuntimeError(f"Server request failed: {e}")


def select_best_backend(config: dict) -> tuple[str, dict]:
    """Select the best available backend based on priority and availability."""
    backends = config.get("backends", {})
    timeout = config.get("health_check_timeout", 5)

    available = []

    for name, backend in backends.items():
        if not backend.get("enabled", True):
            continue

        health = check_backend_health(backend, timeout)
        if health["available"]:
            available.append({
                "name": name,
                "config": backend,
                "priority": backend.get("priority", 99),
                "gpu": health.get("gpu", False)
            })

    if not available:
        # Try SSH fallback for remote backends
        for name, backend in backends.items():
            if not backend.get("enabled", True):
                continue
            if backend.get("ssh_host") and check_ssh_connection(backend["ssh_host"]):
                available.append({
                    "name": name,
                    "config": backend,
                    "priority": backend.get("priority", 99),
                    "ssh_only": True
                })

    if not available:
        raise RuntimeError("No backends available. Start a server or check SSH connections.")

    # Sort by priority (lower = better)
    available.sort(key=lambda x: x["priority"])
    best = available[0]

    return best["name"], best["config"]


def show_status(config: dict):
    """Show status of all configured backends."""
    backends = config.get("backends", {})
    timeout = config.get("health_check_timeout", 5)

    print("\nBackend Status:")
    print("="*60)

    for name, backend in backends.items():
        enabled = backend.get("enabled", True)
        status_parts = []

        if not enabled:
            status_parts.append("DISABLED")
        else:
            # Check HTTP server
            health = check_backend_health(backend, timeout)
            if health["available"]:
                status_parts.append("SERVER: OK")
                if health.get("gpu"):
                    status_parts.append("GPU")
            else:
                status_parts.append("SERVER: offline")

            # Check SSH if configured
            ssh_host = backend.get("ssh_host")
            if ssh_host:
                if check_ssh_connection(ssh_host):
                    status_parts.append("SSH: OK")
                else:
                    status_parts.append("SSH: no connection")

        priority = backend.get("priority", 99)
        status_str = " | ".join(status_parts)
        print(f"  [{priority}] {backend.get('name', name)}: {status_str}")

    print("="*60)


def main():
    parser = argparse.ArgumentParser(
        description="Remote transcription CLI for Voice Memo Transcriber",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  %(prog)s audio/memo.m4a                    # Auto-select best backend
  %(prog)s audio/memo.m4a --backend asus     # Use ASUS GPU backend
  %(prog)s audio/memo.m4a --backend local    # Use local Mac (MLX)
  %(prog)s --status                          # Show backend status
  %(prog)s audio/*.m4a --auto                # Batch process with auto selection
        """
    )

    parser.add_argument("files", nargs="*", help="Audio file(s) to transcribe")
    parser.add_argument("--backend", "-b", choices=["auto", "local", "asus", "windows"],
                        default="auto", help="Backend to use (default: auto)")
    parser.add_argument("--model", "-m", default="large-v3",
                        help="Whisper model to use (default: large-v3)")
    parser.add_argument("--no-preprocess", action="store_true",
                        help="Skip preprocessing (silence removal)")
    parser.add_argument("--status", action="store_true",
                        help="Show status of all backends")
    parser.add_argument("--config", type=Path, default=CONFIG_PATH,
                        help="Path to config file")

    args = parser.parse_args()

    # Load config
    if args.config.exists():
        with open(args.config) as f:
            config = json.load(f)
    else:
        config = load_config()

    # Status check
    if args.status:
        show_status(config)
        return 0

    # Validate files
    if not args.files:
        parser.print_help()
        return 1

    for file_path in args.files:
        if not os.path.exists(file_path):
            print(f"Error: File not found: {file_path}")
            return 1

    # Process each file
    for file_path in args.files:
        try:
            # Select backend
            if args.backend == "auto":
                backend_name, backend_config = select_best_backend(config)
                print(f"Auto-selected backend: {backend_config.get('name', backend_name)}")
            else:
                backend_name = args.backend
                backend_config = config.get("backends", {}).get(backend_name, {})
                if not backend_config:
                    print(f"Error: Unknown backend: {backend_name}")
                    return 1

            # Run transcription based on backend type
            if backend_name == "local":
                result = run_local_transcription(
                    file_path,
                    model=args.model,
                    preprocess=not args.no_preprocess
                )
            elif backend_config.get("ssh_host"):
                # Check if server is available first
                health = check_backend_health(backend_config)
                if health["available"]:
                    result = run_server_transcription(
                        file_path,
                        backend_config["url"],
                        model=args.model
                    )
                else:
                    # Fall back to SSH
                    result = run_remote_transcription(
                        file_path,
                        backend_config,
                        model=args.model,
                        preprocess=not args.no_preprocess
                    )
            else:
                # Use HTTP server
                result = run_server_transcription(
                    file_path,
                    backend_config["url"],
                    model=args.model
                )

            if result.get("success", True):
                print(f"\nTranscript saved: {result.get('transcript_path', result.get('output_path'))}")

        except Exception as e:
            print(f"Error transcribing {file_path}: {e}")
            if len(args.files) == 1:
                return 1

    return 0


if __name__ == "__main__":
    sys.exit(main())
