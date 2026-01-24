#!/bin/bash
#
# ASUS ROG (KDE Neon) Setup Script
# Sets up the voice-memo-transcriber on Linux with NVIDIA GPU
#
# Run this script on the ASUS machine:
#   curl -fsSL https://raw.githubusercontent.com/.../setup/asus-setup.sh | bash
# Or copy and run locally:
#   bash setup/asus-setup.sh
#

set -e  # Exit on error

echo "=============================================="
echo "Voice Memo Transcriber - ASUS Setup"
echo "=============================================="
echo ""

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

success() { echo -e "${GREEN}✓ $1${NC}"; }
warn() { echo -e "${YELLOW}⚠ $1${NC}"; }
error() { echo -e "${RED}✗ $1${NC}"; exit 1; }

# Check if running on Linux
if [[ "$(uname)" != "Linux" ]]; then
    error "This script is for Linux only"
fi

# 1. Check for NVIDIA GPU
echo "Checking NVIDIA GPU..."
if command -v nvidia-smi &> /dev/null; then
    nvidia-smi --query-gpu=name,driver_version,memory.total --format=csv,noheader
    success "NVIDIA GPU detected"
else
    warn "nvidia-smi not found. Installing NVIDIA drivers..."
    sudo apt update
    sudo apt install -y nvidia-driver-535 nvidia-cuda-toolkit
    echo ""
    warn "NVIDIA drivers installed. Please reboot and run this script again."
    exit 0
fi

# 2. Check CUDA
echo ""
echo "Checking CUDA..."
if command -v nvcc &> /dev/null; then
    nvcc --version | head -4
    success "CUDA toolkit installed"
else
    warn "CUDA not found. Installing..."
    sudo apt install -y nvidia-cuda-toolkit
fi

# 3. Install system dependencies
echo ""
echo "Installing system dependencies..."
sudo apt update
sudo apt install -y \
    python3 python3-pip python3-venv \
    ffmpeg \
    openssh-server \
    git

success "System dependencies installed"

# 4. Enable and start SSH
echo ""
echo "Configuring SSH..."
sudo systemctl enable ssh
sudo systemctl start ssh
SSH_STATUS=$(systemctl is-active ssh)
if [[ "$SSH_STATUS" == "active" ]]; then
    success "SSH server running"
else
    error "SSH server failed to start"
fi

# 5. Create virtual environment
echo ""
echo "Creating Python virtual environment..."
VENV_PATH="$HOME/whisper-env"
if [[ -d "$VENV_PATH" ]]; then
    warn "Virtual environment already exists at $VENV_PATH"
else
    python3 -m venv "$VENV_PATH"
    success "Virtual environment created at $VENV_PATH"
fi

# Activate virtual environment
source "$VENV_PATH/bin/activate"

# 6. Install Python dependencies
echo ""
echo "Installing Python dependencies..."
pip install --upgrade pip

# Install PyTorch with CUDA support
pip install torch --index-url https://download.pytorch.org/whl/cu118

# Install faster-whisper and other dependencies
pip install faster-whisper>=1.0.0
pip install flask flask-cors python-dotenv tqdm pydub supabase openai

success "Python dependencies installed"

# 7. Clone or update project
echo ""
echo "Setting up project..."
PROJECT_PATH="$HOME/voice-memo-transcriber"

if [[ -d "$PROJECT_PATH" ]]; then
    warn "Project directory already exists"
    # If it's a git repo, pull latest
    if [[ -d "$PROJECT_PATH/.git" ]]; then
        cd "$PROJECT_PATH"
        git pull origin master || true
    fi
else
    # Create project directory structure
    mkdir -p "$PROJECT_PATH"/{scripts,audio/{inbox,completed},transcripts,dashboard}
fi

success "Project directory ready at $PROJECT_PATH"

# 8. Test faster-whisper with GPU
echo ""
echo "Testing faster-whisper with GPU..."
python3 -c "
from faster_whisper import WhisperModel
import torch

if torch.cuda.is_available():
    print(f'CUDA device: {torch.cuda.get_device_name(0)}')
    print(f'CUDA memory: {torch.cuda.get_device_properties(0).total_memory / 1024**3:.1f} GB')

# Load a small model to test
print('Loading tiny model for test...')
model = WhisperModel('tiny', device='cuda', compute_type='float16')
print('faster-whisper with CUDA is ready!')
" || error "faster-whisper test failed"

success "faster-whisper GPU test passed"

# 9. Create systemd service (optional)
echo ""
read -p "Create systemd service for auto-start? [y/N] " -n 1 -r
echo
if [[ $REPLY =~ ^[Yy]$ ]]; then
    SERVICE_FILE="/etc/systemd/system/voice-transcriber.service"
    sudo tee "$SERVICE_FILE" > /dev/null << EOF
[Unit]
Description=Voice Memo Transcriber Server
After=network.target

[Service]
Type=simple
User=$USER
WorkingDirectory=$PROJECT_PATH
Environment="PATH=$VENV_PATH/bin:/usr/local/bin:/usr/bin"
ExecStart=$VENV_PATH/bin/python server.py --host 0.0.0.0 --port 5111
Restart=on-failure
RestartSec=5

[Install]
WantedBy=multi-user.target
EOF

    sudo systemctl daemon-reload
    sudo systemctl enable voice-transcriber
    success "Systemd service created (start with: sudo systemctl start voice-transcriber)"
fi

# 10. Print summary
echo ""
echo "=============================================="
echo "Setup Complete!"
echo "=============================================="
echo ""
echo "IP Address: $(hostname -I | awk '{print $1}')"
echo "Project: $PROJECT_PATH"
echo "Virtual env: $VENV_PATH"
echo ""
echo "To start the server manually:"
echo "  source $VENV_PATH/bin/activate"
echo "  cd $PROJECT_PATH"
echo "  python server.py --host 0.0.0.0 --port 5111"
echo ""
echo "From Mac, test connection with:"
echo "  ssh $(whoami)@$(hostname -I | awk '{print $1}')"
echo ""
echo "Add to Mac's ~/.ssh/config:"
echo "  Host asus"
echo "      HostName $(hostname -I | awk '{print $1}')"
echo "      User $(whoami)"
echo ""
