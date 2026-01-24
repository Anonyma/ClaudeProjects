# Remote Compute Setup Progress

**Last Updated:** 2026-01-24
**Status:** Code complete, pending machine setup

---

## What's Done (Mac Side)

- [x] `config.json` - Backend configuration
- [x] `scripts/transcribe_remote.py` - Remote transcription CLI
- [x] `server.py` - Updated with faster-whisper support
- [x] `dashboard/index.html` - Backend selector added
- [x] `setup/asus-setup.sh` - ASUS setup script
- [x] `setup/windows-setup.ps1` - Windows setup script
- [x] `requirements-linux.txt` and `requirements-windows.txt`

---

## What's Next

### Step 1: ASUS Setup (On ASUS Machine)

```bash
# 1. Get the setup script onto ASUS (choose one method):

# Option A: If you have the repo cloned on ASUS
cd ~/voice-memo-transcriber
git pull
bash setup/asus-setup.sh

# Option B: Copy from Mac via SCP (get ASUS IP first)
# On Mac:
scp setup/asus-setup.sh username@ASUS_IP:~/
# On ASUS:
bash ~/asus-setup.sh

# Option C: Copy-paste the script manually
# Open setup/asus-setup.sh in a text editor, copy contents
# SSH to ASUS, paste into a file, run it
```

The script will:
- Install NVIDIA drivers + CUDA (if needed)
- Set up Python venv with faster-whisper
- Enable SSH server
- Test GPU transcription
- Optionally create systemd service for auto-start

### Step 2: Windows Setup (On Windows Machine)

```powershell
# Run PowerShell as Administrator
Set-ExecutionPolicy Bypass -Scope Process -Force

# Option A: If repo is cloned
cd C:\path\to\voice-memo-transcriber
.\setup\windows-setup.ps1

# Option B: Copy script from Mac and run
```

### Step 3: Mac SSH Configuration

After ASUS and Windows are set up, add to `~/.ssh/config`:

```
Host asus
    HostName 192.168.X.X    # Replace with ASUS IP
    User YOUR_ASUS_USERNAME

Host windows
    HostName 192.168.X.Y    # Replace with Windows IP
    User YOUR_WINDOWS_USERNAME
```

Then copy your SSH key:
```bash
# Generate key if you don't have one
ssh-keygen -t ed25519 -C "mac-to-remote"

# Copy to remote machines
ssh-copy-id asus
ssh-copy-id windows
```

### Step 4: Copy Project Files to Remote Machines

**On ASUS:**
```bash
mkdir -p ~/voice-memo-transcriber/{scripts,audio/inbox,transcripts}
```

**On Mac, copy essential files:**
```bash
scp server.py scripts/transcribe.py scripts/preprocess.py asus:~/voice-memo-transcriber/
scp -r scripts asus:~/voice-memo-transcriber/
```

**On Windows:** Same process, adjust paths to `C:\voice-memo-transcriber\`

### Step 5: Start Servers on Remote Machines

**On ASUS:**
```bash
source ~/whisper-env/bin/activate
cd ~/voice-memo-transcriber
python server.py --host 0.0.0.0 --port 5111
```

**On Windows:**
```powershell
C:\whisper-env\Scripts\Activate.ps1
cd C:\voice-memo-transcriber
python server.py --host 0.0.0.0 --port 5112
```

### Step 6: Verify from Mac

```bash
# Check all backends
python3 scripts/transcribe_remote.py --status

# Test SSH connections
ssh asus nvidia-smi          # Should show RTX 2060
ssh asus echo ok              # Should print "ok"
ssh windows echo ok           # Should print "ok"

# Test transcription (with a short file first!)
python3 scripts/transcribe_remote.py audio/test.m4a --backend asus
```

---

## Quick Reference

| Machine | SSH Host | Server Port | GPU |
|---------|----------|-------------|-----|
| Mac | localhost | 5111 | Apple Silicon (MLX) |
| ASUS | asus | 5111 | RTX 2060 (CUDA) |
| Windows | windows | 5112 | CPU (or GPU if available) |

---

## Troubleshooting

**SSH connection refused:**
- Ensure SSH server is running: `sudo systemctl status ssh` (Linux) or check Services (Windows)
- Check firewall allows port 22

**Server not responding:**
- Check server is running on remote machine
- Check firewall allows port 5111/5112
- Try `curl http://asus:5111/health` from Mac

**GPU not detected on ASUS:**
- Run `nvidia-smi` to verify driver
- Check CUDA: `nvcc --version`
- Reinstall: `sudo apt install nvidia-driver-535 nvidia-cuda-toolkit`

---

## Resume This Conversation

To continue where we left off, tell Claude:

> "I'm setting up remote compute for voice-memo-transcriber. Read SETUP_PROGRESS.md in the project directory - I need help with [Step X]."

Or just open the dashboard and try the backend selector - it will show which backends are online.
