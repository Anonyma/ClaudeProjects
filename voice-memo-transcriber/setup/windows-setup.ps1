# Windows Setup Script for Voice Memo Transcriber
# Run in PowerShell as Administrator:
#   Set-ExecutionPolicy Bypass -Scope Process -Force
#   .\setup\windows-setup.ps1

$ErrorActionPreference = "Stop"

Write-Host "=============================================="
Write-Host "Voice Memo Transcriber - Windows Setup"
Write-Host "=============================================="
Write-Host ""

# Helper functions
function Write-Success { param($msg) Write-Host "[OK] $msg" -ForegroundColor Green }
function Write-Warn { param($msg) Write-Host "[!] $msg" -ForegroundColor Yellow }
function Write-Err { param($msg) Write-Host "[X] $msg" -ForegroundColor Red; exit 1 }

# 1. Check for admin rights
$isAdmin = ([Security.Principal.WindowsPrincipal] [Security.Principal.WindowsIdentity]::GetCurrent()).IsInRole([Security.Principal.WindowsBuiltInRole]::Administrator)
if (-not $isAdmin) {
    Write-Warn "Some features require Administrator privileges"
}

# 2. Install Python if needed
Write-Host "`nChecking Python..."
try {
    $pythonVersion = python --version 2>&1
    Write-Success "Python installed: $pythonVersion"
} catch {
    Write-Host "Python not found. Installing via winget..."
    winget install Python.Python.3.11 --accept-package-agreements --accept-source-agreements
    # Refresh PATH
    $env:Path = [System.Environment]::GetEnvironmentVariable("Path","Machine") + ";" + [System.Environment]::GetEnvironmentVariable("Path","User")
}

# 3. Install FFmpeg if needed
Write-Host "`nChecking FFmpeg..."
try {
    $ffmpegVersion = ffmpeg -version 2>&1 | Select-Object -First 1
    Write-Success "FFmpeg installed"
} catch {
    Write-Host "FFmpeg not found. Installing via winget..."
    winget install FFmpeg --accept-package-agreements --accept-source-agreements
    $env:Path = [System.Environment]::GetEnvironmentVariable("Path","Machine") + ";" + [System.Environment]::GetEnvironmentVariable("Path","User")
}

# 4. Enable OpenSSH Server
Write-Host "`nConfiguring OpenSSH Server..."
try {
    # Check if OpenSSH Server is installed
    $sshServer = Get-WindowsCapability -Online | Where-Object Name -like 'OpenSSH.Server*'
    if ($sshServer.State -ne 'Installed') {
        Write-Host "Installing OpenSSH Server..."
        Add-WindowsCapability -Online -Name OpenSSH.Server~~~~0.0.1.0
    }

    # Start and enable the service
    Start-Service sshd
    Set-Service -Name sshd -StartupType 'Automatic'

    # Configure firewall
    $firewallRule = Get-NetFirewallRule -Name "OpenSSH-Server-In-TCP" -ErrorAction SilentlyContinue
    if (-not $firewallRule) {
        New-NetFirewallRule -Name "OpenSSH-Server-In-TCP" -DisplayName "OpenSSH Server (sshd)" -Enabled True -Direction Inbound -Protocol TCP -Action Allow -LocalPort 22
    }

    Write-Success "OpenSSH Server enabled and running"
} catch {
    Write-Warn "Could not configure OpenSSH Server. Run as Administrator."
}

# 5. Create virtual environment
Write-Host "`nCreating Python virtual environment..."
$VenvPath = "C:\whisper-env"
if (Test-Path $VenvPath) {
    Write-Warn "Virtual environment already exists at $VenvPath"
} else {
    python -m venv $VenvPath
    Write-Success "Virtual environment created at $VenvPath"
}

# Activate virtual environment
& "$VenvPath\Scripts\Activate.ps1"

# 6. Install Python dependencies
Write-Host "`nInstalling Python dependencies..."
pip install --upgrade pip

# Check for NVIDIA GPU
$hasNvidiaGpu = $false
try {
    $gpuInfo = nvidia-smi --query-gpu=name --format=csv,noheader 2>&1
    if ($LASTEXITCODE -eq 0) {
        Write-Success "NVIDIA GPU detected: $gpuInfo"
        $hasNvidiaGpu = $true
    }
} catch {
    Write-Warn "No NVIDIA GPU detected. Using CPU mode."
}

# Install PyTorch
if ($hasNvidiaGpu) {
    Write-Host "Installing PyTorch with CUDA support..."
    pip install torch --index-url https://download.pytorch.org/whl/cu118
} else {
    Write-Host "Installing PyTorch (CPU only)..."
    pip install torch
}

# Install faster-whisper and other dependencies
pip install faster-whisper
pip install flask flask-cors python-dotenv tqdm pydub supabase openai

Write-Success "Python dependencies installed"

# 7. Create project directory
Write-Host "`nSetting up project..."
$ProjectPath = "C:\voice-memo-transcriber"
if (-not (Test-Path $ProjectPath)) {
    New-Item -ItemType Directory -Path $ProjectPath -Force | Out-Null
    New-Item -ItemType Directory -Path "$ProjectPath\scripts" -Force | Out-Null
    New-Item -ItemType Directory -Path "$ProjectPath\audio\inbox" -Force | Out-Null
    New-Item -ItemType Directory -Path "$ProjectPath\audio\completed" -Force | Out-Null
    New-Item -ItemType Directory -Path "$ProjectPath\transcripts" -Force | Out-Null
    New-Item -ItemType Directory -Path "$ProjectPath\dashboard" -Force | Out-Null
}
Write-Success "Project directory ready at $ProjectPath"

# 8. Test faster-whisper
Write-Host "`nTesting faster-whisper..."
$testScript = @"
from faster_whisper import WhisperModel
import torch

if torch.cuda.is_available():
    print(f'CUDA device: {torch.cuda.get_device_name(0)}')
    device = 'cuda'
    compute_type = 'float16'
else:
    print('Using CPU mode')
    device = 'cpu'
    compute_type = 'int8'

print('Loading tiny model for test...')
model = WhisperModel('tiny', device=device, compute_type=compute_type)
print('faster-whisper is ready!')
"@

python -c $testScript
if ($LASTEXITCODE -eq 0) {
    Write-Success "faster-whisper test passed"
} else {
    Write-Warn "faster-whisper test failed"
}

# 9. Get IP address
$ipAddress = (Get-NetIPAddress -AddressFamily IPv4 | Where-Object { $_.InterfaceAlias -notmatch 'Loopback' -and $_.PrefixOrigin -eq 'Dhcp' } | Select-Object -First 1).IPAddress
if (-not $ipAddress) {
    $ipAddress = (Get-NetIPAddress -AddressFamily IPv4 | Where-Object { $_.InterfaceAlias -notmatch 'Loopback' } | Select-Object -First 1).IPAddress
}

# 10. Print summary
Write-Host ""
Write-Host "=============================================="
Write-Host "Setup Complete!"
Write-Host "=============================================="
Write-Host ""
Write-Host "IP Address: $ipAddress"
Write-Host "Project: $ProjectPath"
Write-Host "Virtual env: $VenvPath"
Write-Host ""
Write-Host "To start the server:"
Write-Host "  & '$VenvPath\Scripts\Activate.ps1'"
Write-Host "  cd $ProjectPath"
Write-Host "  python server.py --host 0.0.0.0 --port 5112"
Write-Host ""
Write-Host "From Mac, test connection with:"
Write-Host "  ssh $env:USERNAME@$ipAddress"
Write-Host ""
Write-Host "Add to Mac's ~/.ssh/config:"
Write-Host "  Host windows"
Write-Host "      HostName $ipAddress"
Write-Host "      User $env:USERNAME"
Write-Host ""
