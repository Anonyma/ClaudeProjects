# Audio Transcription System

Custom voice transcription setup using `faster-whisper` running locally on CandyPop.

## Features

- ✅ **Fully local & private** - No API calls, everything on CandyPop
- ✅ **GPU accelerated** - Uses RTX 2060 (6GB VRAM)
- ✅ **Large model** - Running `large-v2` for best accuracy
- ✅ **Custom word corrections** - Fixes common misheard words (Ritalin, NotebookLM, etc.)
- ✅ **Smart line breaks** - Configurable pause detection (2s default)
- ✅ **Timestamps** - Optional SRT-style timestamps
- ✅ **4x faster** - Than standard openai-whisper

## Hardware

**CandyPop specs:**
- GPU: NVIDIA RTX 2060 (6GB VRAM)
- RAM: 16GB
- CPU: 12 cores
- Model: large-v2 (~5GB VRAM)

## Usage

### Quick transcription

```bash
# On CandyPop
cd ~/device-sync/audio-transcriptions
python3 transcribe.py /path/to/audio.m4a
```

Output: `audio_transcript.txt` in the same directory

### From Mac

```bash
# Copy audio to CandyPop
scp ~/path/to/audio.m4a CandyPop:~/device-sync/audio-transcriptions/

# SSH and transcribe
ssh CandyPop 'cd ~/device-sync/audio-transcriptions && python3 transcribe.py audio.m4a'

# Copy result back
scp CandyPop:~/device-sync/audio-transcriptions/audio_transcript.txt ~/Desktop/
```

### With notification

```bash
ssh CandyPop 'cd ~/device-sync/audio-transcriptions && python3 transcribe.py audio.m4a && report-status --name transcription completed "Finished: audio.m4a" || report-status --name transcription error "Failed: audio.m4a"'
```

## Configuration

Edit `transcribe-config.json` to customize:

### Word Replacements

```json
"word_replacements": {
  "ridlin": "Ritalin",
  "notebooklm": "NotebookLM",
  "clawed": "Claude"
}
```

Add any words that frequently get misheard.

### Line Break Timing

```json
"vad_parameters": {
  "min_silence_duration_ms": 2000  // Wait 2 seconds before line break
}
```

- Increase for fewer line breaks (longer paragraphs)
- Decrease for more frequent breaks (shorter paragraphs)

### Paragraph Breaks

```json
"formatting": {
  "min_silence_for_paragraph": 3.0  // 3 second pause = new paragraph
}
```

### Model Selection

```json
"model": "large-v2"
```

Options:
- `large-v3` - Best accuracy, ~6GB VRAM (tight fit)
- `large-v2` - Excellent accuracy, ~5GB VRAM (recommended)
- `medium` - Good accuracy, ~2.5GB VRAM (faster)
- `small` - Decent accuracy, ~1GB VRAM (very fast)

### Disable Timestamps

```json
"formatting": {
  "add_timestamps": false
}
```

## Files

- `transcribe.py` - Main transcription script
- `transcribe-config.json` - Configuration file
- `README.md` - This file

## Tips

1. **For long recordings** - The script processes in chunks, no length limit
2. **For better accuracy** - Use `large-v3` if you have the VRAM headroom
3. **For speed** - Use `medium` model (still very good quality)
4. **Custom vocabulary** - Add common names, technical terms to word_replacements
5. **Formatting tweaks** - Adjust `min_silence_duration_ms` to match your speaking style

## Comparison

| Feature | openai-whisper | faster-whisper |
|---------|---------------|----------------|
| Speed | 1x | 4x |
| VRAM | High | Low |
| Customization | None | Full |
| Local | ✅ | ✅ |
| Word corrections | ❌ | ✅ |
| Format control | ❌ | ✅ |

## Next Steps

- Fine-tune line break timing to your preference
- Add more word replacements as you notice errors
- Consider `large-v3` once you test memory usage
- Add speaker diarization if needed (future enhancement)
