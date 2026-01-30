#!/usr/bin/env python3
"""
System-wide dictation app - runs in menu bar, works in any app.

Usage:
    python3 dictate.py                    # Use OpenAI Whisper API
    python3 dictate.py --groq             # Use Groq's Whisper API (faster, cheaper)
    python3 dictate.py --local            # Use local Whisper (no API needed)

Hotkey: Press Right Option (⌥) to start recording, press again to stop.
        Text is automatically pasted into the current app.

The app runs in your menu bar - look for the 🎙️ icon.
"""

import argparse
import os
import subprocess
import sys
import tempfile
import threading
import time
import wave
from enum import Enum

import numpy as np
import rumps
import sounddevice as sd
from pynput import keyboard

# Configuration
SAMPLE_RATE = 16000
CHANNELS = 1

# Hotkey options - change this to your preference
# Options: keyboard.Key.alt_r (Right Option), keyboard.Key.f5, etc.
TOGGLE_KEY = keyboard.Key.alt_r  # Right Option - press to start, press again to stop


class RecordingState(Enum):
    IDLE = "idle"
    RECORDING = "recording"
    PROCESSING = "processing"


class DictationApp(rumps.App):
    def __init__(self, backend="openai"):
        super().__init__("🎙️", quit_button=None)

        self.backend = backend
        self.state = RecordingState.IDLE
        self.audio_chunks = []
        self.stream = None

        # Menu items
        self.status_item = rumps.MenuItem("Ready - Press ⌥ to dictate")
        self.backend_display = rumps.MenuItem(f"Backend: {backend.title()}")
        self.backend_display.set_callback(None)  # Non-clickable

        self.menu = [
            self.status_item,
            None,  # Separator
            self.backend_display,
            None,
            rumps.MenuItem("Quit", callback=self.quit_app),
        ]

        # Start keyboard listener in background
        self.keyboard_listener = keyboard.Listener(
            on_press=self.on_key_press,
            on_release=self.on_key_release
        )
        self.keyboard_listener.start()

        # Load transcription backend
        self.transcribe_fn = self._get_transcribe_fn()

    def _get_transcribe_fn(self):
        """Get the transcription function based on backend."""
        if self.backend == "local":
            return self._transcribe_local
        elif self.backend == "groq":
            return self._transcribe_groq
        else:
            return self._transcribe_openai

    def _transcribe_openai(self, audio_path: str) -> str:
        from openai import OpenAI
        client = OpenAI()
        with open(audio_path, "rb") as f:
            result = client.audio.transcriptions.create(
                model="whisper-1",
                file=f,
                language="en",
            )
        return result.text

    def _transcribe_groq(self, audio_path: str) -> str:
        from groq import Groq
        client = Groq()
        with open(audio_path, "rb") as f:
            result = client.audio.transcriptions.create(
                model="whisper-large-v3",
                file=f,
                language="en",
            )
        return result.text

    def _transcribe_local(self, audio_path: str) -> str:
        from faster_whisper import WhisperModel
        model_size = os.environ.get("WHISPER_MODEL", "medium")
        if not hasattr(self, "_local_model"):
            self._local_model = WhisperModel(model_size, device="auto", compute_type="auto")
        segments, _ = self._local_model.transcribe(audio_path, language="en")
        return " ".join(s.text for s in segments).strip()

    def on_key_press(self, key):
        """Handle key press events."""
        # Toggle recording with the hotkey
        if key == TOGGLE_KEY:
            if self.state == RecordingState.IDLE:
                self.start_recording()
            elif self.state == RecordingState.RECORDING:
                self.stop_recording()

    def on_key_release(self, key):
        """Handle key release events."""
        pass  # We use press-to-toggle, not hold-to-record

    def start_recording(self):
        """Start recording audio."""
        if self.state != RecordingState.IDLE:
            return

        self.state = RecordingState.RECORDING
        self.audio_chunks = []
        self.title = "🔴"
        self.status_item.title = "Recording... Press ⌥ to stop"

        # Play start sound
        self._play_sound("start")

        # Start audio stream
        self.stream = sd.InputStream(
            samplerate=SAMPLE_RATE,
            channels=CHANNELS,
            dtype=np.float32,
            callback=self._audio_callback,
        )
        self.stream.start()

    def _audio_callback(self, indata, frames, time_info, status):
        """Capture audio data."""
        if self.state == RecordingState.RECORDING:
            self.audio_chunks.append(indata.copy())

    def stop_recording(self):
        """Stop recording and transcribe."""
        if self.state != RecordingState.RECORDING:
            return

        self.state = RecordingState.PROCESSING
        self.title = "⏳"
        self.status_item.title = "Transcribing..."

        # Stop audio stream
        if self.stream:
            self.stream.stop()
            self.stream.close()
            self.stream = None

        self._play_sound("stop")

        # Process in background
        threading.Thread(target=self._process_audio, daemon=True).start()

    def _process_audio(self):
        """Process and transcribe audio."""
        try:
            if not self.audio_chunks:
                self._finish_processing("No audio captured")
                return

            # Save to temp file
            with tempfile.NamedTemporaryFile(suffix=".wav", delete=False) as f:
                temp_path = f.name

            audio_data = np.concatenate(self.audio_chunks, axis=0)
            with wave.open(temp_path, "wb") as wf:
                wf.setnchannels(CHANNELS)
                wf.setsampwidth(2)
                wf.setframerate(SAMPLE_RATE)
                wf.writeframes((audio_data * 32767).astype(np.int16).tobytes())

            duration = len(audio_data) / SAMPLE_RATE

            # Transcribe
            start = time.time()
            text = self.transcribe_fn(temp_path)
            elapsed = time.time() - start

            # Cleanup temp file
            os.unlink(temp_path)

            if text.strip():
                self._paste_text(text)
                preview = text[:30] + "..." if len(text) > 30 else text
                self._finish_processing(f"✓ {preview}")
            else:
                self._finish_processing("No speech detected")

        except Exception as e:
            self._play_sound("error")
            self._finish_processing(f"Error: {str(e)[:30]}")

    def _paste_text(self, text: str):
        """Copy to clipboard and paste."""
        # Copy to clipboard
        subprocess.run(["pbcopy"], input=text.encode(), check=True)

        # Small delay to ensure clipboard is ready
        time.sleep(0.05)

        # Paste using AppleScript
        subprocess.run([
            "osascript", "-e",
            'tell application "System Events" to keystroke "v" using command down'
        ], check=True)

    def _finish_processing(self, message: str):
        """Reset state after processing."""
        self.state = RecordingState.IDLE
        self.title = "🎙️"
        self.status_item.title = f"Ready - {message}"

        # Reset status after 3 seconds
        def reset_status():
            time.sleep(3)
            if self.state == RecordingState.IDLE:
                self.status_item.title = "Ready - Press ⌥ to dictate"
        threading.Thread(target=reset_status, daemon=True).start()

    def _play_sound(self, sound_type: str):
        """Play feedback sound."""
        sounds = {
            "start": "/System/Library/Sounds/Pop.aiff",
            "stop": "/System/Library/Sounds/Blow.aiff",
            "error": "/System/Library/Sounds/Basso.aiff",
        }
        path = sounds.get(sound_type)
        if path and os.path.exists(path):
            subprocess.run(["afplay", path], check=False,
                         stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)

    def quit_app(self, _):
        """Quit the application."""
        self.keyboard_listener.stop()
        rumps.quit_application()


def main():
    parser = argparse.ArgumentParser(description="System-wide dictation app")
    parser.add_argument("--groq", action="store_true", help="Use Groq Whisper API")
    parser.add_argument("--local", action="store_true", help="Use local Whisper")
    args = parser.parse_args()

    # Determine backend
    if args.local:
        backend = "local"
    elif args.groq:
        backend = "groq"
        if not os.environ.get("GROQ_API_KEY"):
            print("❌ GROQ_API_KEY not set")
            sys.exit(1)
    else:
        backend = "openai"
        if not os.environ.get("OPENAI_API_KEY"):
            print("❌ OPENAI_API_KEY not set. Use --groq or --local, or set OPENAI_API_KEY")
            sys.exit(1)

    print(f"🎙️ Starting dictation app with {backend} backend...")
    print("   Look for 🎙️ in your menu bar")
    print("   Press Right Option (⌥) to start/stop recording")

    app = DictationApp(backend=backend)
    app.run()


if __name__ == "__main__":
    main()
