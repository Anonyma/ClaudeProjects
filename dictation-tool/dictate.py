#!/usr/bin/env python3
"""
Simple dictation tool - hold a key to record, release to transcribe and paste.

Usage:
    python3 dictate.py                    # Use OpenAI Whisper API
    python3 dictate.py --local            # Use local Whisper (faster-whisper)
    python3 dictate.py --groq             # Use Groq's Whisper API (faster, cheaper)

Hotkey: Hold Right Option (Alt) key to record, release to transcribe.
        Press Escape to quit.

Requirements:
    pip3 install sounddevice numpy openai pynput

For local mode:
    pip3 install faster-whisper

For Groq mode:
    pip3 install groq
"""

import argparse
import io
import os
import subprocess
import sys
import tempfile
import threading
import time
import wave
from pathlib import Path

import numpy as np
import sounddevice as sd
from pynput import keyboard

# Configuration
SAMPLE_RATE = 16000  # Whisper expects 16kHz
CHANNELS = 1
HOTKEY = keyboard.Key.alt_r  # Right Option/Alt key - change this if needed

# State
recording = False
audio_chunks = []
current_keys = set()


def get_transcription_backend(args):
    """Return the appropriate transcription function based on args."""
    if args.local:
        return transcribe_local
    elif args.groq:
        return transcribe_groq
    else:
        return transcribe_openai


def transcribe_openai(audio_path: str) -> str:
    """Transcribe using OpenAI Whisper API."""
    from openai import OpenAI

    client = OpenAI()  # Uses OPENAI_API_KEY env var

    with open(audio_path, "rb") as audio_file:
        transcript = client.audio.transcriptions.create(
            model="whisper-1",
            file=audio_file,
            language="en",  # Helps with accent recognition
        )
    return transcript.text


def transcribe_groq(audio_path: str) -> str:
    """Transcribe using Groq's Whisper API (faster, cheaper)."""
    from groq import Groq

    client = Groq()  # Uses GROQ_API_KEY env var

    with open(audio_path, "rb") as audio_file:
        transcript = client.audio.transcriptions.create(
            model="whisper-large-v3",
            file=audio_file,
            language="en",
        )
    return transcript.text


def transcribe_local(audio_path: str) -> str:
    """Transcribe using local faster-whisper."""
    from faster_whisper import WhisperModel

    # Use medium model for good balance of speed/accuracy
    # Change to "large-v3" for best accuracy with accents
    model_size = os.environ.get("WHISPER_MODEL", "medium")

    # Cache model in module for reuse
    if not hasattr(transcribe_local, "_model"):
        print(f"Loading local Whisper model ({model_size})... ", end="", flush=True)
        transcribe_local._model = WhisperModel(
            model_size,
            device="auto",  # Uses GPU if available (MPS on Mac)
            compute_type="auto",
        )
        print("done!")

    model = transcribe_local._model
    segments, _ = model.transcribe(audio_path, language="en")
    return " ".join(segment.text for segment in segments).strip()


def save_audio_to_wav(chunks: list, path: str):
    """Save audio chunks to a WAV file."""
    audio_data = np.concatenate(chunks, axis=0)

    with wave.open(path, "wb") as wf:
        wf.setnchannels(CHANNELS)
        wf.setsampwidth(2)  # 16-bit
        wf.setframerate(SAMPLE_RATE)
        wf.writeframes((audio_data * 32767).astype(np.int16).tobytes())


def paste_text(text: str):
    """Copy text to clipboard and paste it."""
    # Copy to clipboard
    process = subprocess.Popen(
        ["pbcopy"],
        stdin=subprocess.PIPE,
    )
    process.communicate(text.encode("utf-8"))

    # Paste using AppleScript
    subprocess.run([
        "osascript", "-e",
        'tell application "System Events" to keystroke "v" using command down'
    ], check=True)


def play_sound(sound_type: str):
    """Play a system sound for feedback."""
    sounds = {
        "start": "/System/Library/Sounds/Pop.aiff",
        "stop": "/System/Library/Sounds/Blow.aiff",
        "error": "/System/Library/Sounds/Basso.aiff",
    }
    sound_path = sounds.get(sound_type)
    if sound_path and os.path.exists(sound_path):
        subprocess.run(["afplay", sound_path], check=False)


class DictationApp:
    def __init__(self, transcribe_fn):
        self.transcribe_fn = transcribe_fn
        self.recording = False
        self.audio_chunks = []
        self.stream = None
        self.processing = False

    def audio_callback(self, indata, frames, time_info, status):
        """Called for each audio block during recording."""
        if self.recording:
            self.audio_chunks.append(indata.copy())

    def start_recording(self):
        """Start recording audio."""
        if self.recording or self.processing:
            return

        self.recording = True
        self.audio_chunks = []

        self.stream = sd.InputStream(
            samplerate=SAMPLE_RATE,
            channels=CHANNELS,
            dtype=np.float32,
            callback=self.audio_callback,
        )
        self.stream.start()
        play_sound("start")
        print("🎙️  Recording...", end="", flush=True)

    def stop_recording(self):
        """Stop recording and transcribe."""
        if not self.recording:
            return

        self.recording = False
        self.processing = True

        if self.stream:
            self.stream.stop()
            self.stream.close()
            self.stream = None

        print(" done!")
        play_sound("stop")

        if not self.audio_chunks:
            print("⚠️  No audio recorded")
            self.processing = False
            return

        # Process in background thread
        threading.Thread(target=self._process_audio, daemon=True).start()

    def _process_audio(self):
        """Process recorded audio (runs in background thread)."""
        try:
            # Save to temp file
            with tempfile.NamedTemporaryFile(suffix=".wav", delete=False) as f:
                temp_path = f.name

            save_audio_to_wav(self.audio_chunks, temp_path)

            # Calculate duration
            duration = len(np.concatenate(self.audio_chunks)) / SAMPLE_RATE
            print(f"📝 Transcribing {duration:.1f}s of audio...")

            # Transcribe
            start_time = time.time()
            text = self.transcribe_fn(temp_path)
            elapsed = time.time() - start_time

            print(f"✅ Transcribed in {elapsed:.1f}s: \"{text[:50]}{'...' if len(text) > 50 else ''}\"")

            # Paste
            if text.strip():
                paste_text(text)

            # Cleanup
            os.unlink(temp_path)

        except Exception as e:
            print(f"❌ Error: {e}")
            play_sound("error")
        finally:
            self.processing = False


def main():
    parser = argparse.ArgumentParser(description="Simple dictation tool")
    parser.add_argument("--local", action="store_true", help="Use local Whisper model")
    parser.add_argument("--groq", action="store_true", help="Use Groq's Whisper API")
    parser.add_argument("--test", action="store_true", help="Test recording without transcription")
    args = parser.parse_args()

    # Check dependencies
    if not args.local and not args.groq:
        if not os.environ.get("OPENAI_API_KEY"):
            print("❌ OPENAI_API_KEY not set. Set it or use --local/--groq")
            sys.exit(1)
    elif args.groq:
        if not os.environ.get("GROQ_API_KEY"):
            print("❌ GROQ_API_KEY not set.")
            sys.exit(1)

    transcribe_fn = get_transcription_backend(args)
    app = DictationApp(transcribe_fn)

    print("=" * 50)
    print("🎤 Dictation Tool")
    print("=" * 50)
    print(f"Backend: {'Local Whisper' if args.local else 'Groq' if args.groq else 'OpenAI Whisper API'}")
    print(f"Hotkey: Hold Right Option (⌥) to record")
    print(f"Press Escape to quit")
    print("=" * 50)
    print("Ready! Hold Right Option key and speak...")
    print()

    def on_press(key):
        if key == HOTKEY:
            app.start_recording()
        elif key == keyboard.Key.esc:
            print("\n👋 Goodbye!")
            return False  # Stop listener

    def on_release(key):
        if key == HOTKEY:
            app.stop_recording()

    # Start keyboard listener
    with keyboard.Listener(on_press=on_press, on_release=on_release) as listener:
        listener.join()


if __name__ == "__main__":
    main()
