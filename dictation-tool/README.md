# Dictation Tool

A system-wide dictation app for macOS - like Willow or Wispr Flow, but using your own API credits.

## Status: MVP Working, Needs Testing

**Last updated:** 2025-01-30

## Quick Start

```bash
# 1. Set API key (get free key at https://console.groq.com/keys)
echo 'export GROQ_API_KEY="gsk_your_key_here"' >> ~/.zshrc
source ~/.zshrc

# 2. Run
~/bin/dictate

# 3. Use: Press Right Option (⌥) to start, press again to stop
```

## How It Works

1. App runs in menu bar (🎙️ icon)
2. Press **Right Option (⌥)** anywhere → starts recording (icon turns 🔴)
3. Press **Right Option** again → stops, transcribes via Groq/Whisper, pastes text
4. Works in any app - browser, VS Code, Notes, etc.

## Files

| File | Purpose |
|------|---------|
| `dictate.py` | Main app - menu bar + hotkey + transcription |
| `start-dictation.sh` | Launcher script (configure backend here) |
| `Dictation.app` | macOS app bundle for Spotlight/shortcuts |
| `requirements.txt` | Python dependencies |

## Configuration

Edit `start-dictation.sh` line 5 to change backend:
- `groq` - Fast (~1s), cheap, recommended
- `openai` - Reliable, needs OPENAI_API_KEY
- `local` - Free, needs `pip3 install faster-whisper`

To change the hotkey, edit `dictate.py` line 33:
```python
TOGGLE_KEY = keyboard.Key.alt_r  # Change to keyboard.Key.f5, etc.
```

## Requirements

- macOS (uses Accessibility APIs for paste)
- Python 3.10+
- Permissions: Accessibility + Microphone for Terminal

## Dependencies

```bash
pip3 install sounddevice numpy openai pynput rumps groq
```

## TODO / Next Steps

- [ ] Test with user's Spanish-accented English
- [ ] Add visual feedback (maybe a small overlay when recording)
- [ ] Consider adding language selection in menu
- [ ] Add option to copy instead of paste
- [ ] Add sound customization (or disable sounds)
- [ ] Package as proper .app with py2app for easier distribution
- [ ] Add auto-start on login option
- [ ] Consider adding Deepgram as backend option (has streaming)

## Known Issues

- First run requires granting Accessibility + Microphone permissions
- If paste doesn't work, check Accessibility permissions for Terminal
- Menu bar icon may not update immediately on some macOS versions

## Why This Exists

Commercial dictation apps (Willow, Wispr Flow) cost $10-20/month. This uses:
- Groq Whisper API: ~$0.004/min (15 min/day = ~$1.80/month)
- Or local Whisper: free (but slower on older Macs)

Built for a Spanish speaker with accent speaking English - Whisper handles accents well.

## Architecture

```
┌─────────────────┐     ┌──────────────┐     ┌─────────────┐
│  Menu Bar App   │────▶│ Audio Record │────▶│ Whisper API │
│  (rumps/pynput) │     │ (sounddevice)│     │ (groq/openai)│
└─────────────────┘     └──────────────┘     └─────────────┘
                                                    │
                                                    ▼
                                            ┌─────────────┐
                                            │ Paste Text  │
                                            │ (pbcopy+⌘V) │
                                            └─────────────┘
```
