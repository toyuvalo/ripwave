#!/usr/bin/env bash
# RipWave — Linux installer
set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"

echo ""
echo " ================================"
echo "   RipWave  —  Linux Setup"
echo " ================================"
echo ""

# ── Python ────────────────────────────────────────────────────────────────────
if ! command -v python3 &>/dev/null; then
    echo "✗  Python 3 not found."
    echo "   Ubuntu/Debian:  sudo apt install python3 python3-pip"
    exit 1
fi
PY="$(command -v python3)"
echo "✓  Python $($PY --version 2>&1 | awk '{print $2}')  →  $PY"
echo ""

# ── yt-dlp ────────────────────────────────────────────────────────────────────
if command -v yt-dlp &>/dev/null; then
    echo "   yt-dlp already installed, updating..."
    yt-dlp -U --quiet 2>/dev/null || true
    echo "✓  yt-dlp: $(command -v yt-dlp)"
else
    echo "   Installing yt-dlp via pip..."
    $PY -m pip install yt-dlp --quiet --break-system-packages 2>/dev/null \
        || $PY -m pip install yt-dlp --quiet
    echo "✓  yt-dlp installed"
fi

# ── ffmpeg ────────────────────────────────────────────────────────────────────
if command -v ffmpeg &>/dev/null; then
    echo "✓  ffmpeg: $(command -v ffmpeg)"
else
    echo "   Installing ffmpeg..."
    if command -v apt-get &>/dev/null; then
        sudo apt-get install -y ffmpeg
    elif command -v dnf &>/dev/null; then
        sudo dnf install -y ffmpeg
    elif command -v pacman &>/dev/null; then
        sudo pacman -S --noconfirm ffmpeg
    else
        echo "✗  Cannot auto-install ffmpeg. Please install it manually."
        exit 1
    fi
    echo "✓  ffmpeg installed"
fi
echo ""

# ── Desktop launcher ──────────────────────────────────────────────────────────
mkdir -p "$HOME/Desktop"
DESKTOP_FILE="$HOME/Desktop/RipWave.desktop"
cat > "$DESKTOP_FILE" << DESKTOP
[Desktop Entry]
Version=1.0
Type=Application
Name=RipWave
Comment=Download audio/video from 1000+ sites
Exec=python3 $SCRIPT_DIR/ripwave.py
Terminal=false
Categories=Audio;Video;Network;
DESKTOP
chmod +x "$DESKTOP_FILE"
echo "✓  Desktop launcher → ~/Desktop/RipWave.desktop"

# Also register in applications menu
mkdir -p "$HOME/.local/share/applications"
cp "$DESKTOP_FILE" "$HOME/.local/share/applications/ripwave.desktop"
echo "✓  App menu entry registered"

echo ""
echo " ================================"
echo "   Done!"
echo " ================================"
echo ""
echo "   Launch from your Desktop or Applications menu."
echo "   Or run directly:  python3 $SCRIPT_DIR/ripwave.py"
echo ""
