#!/usr/bin/env bash
# RipWave — macOS installer
set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"

echo ""
echo " ================================"
echo "   RipWave  —  macOS Setup"
echo " ================================"
echo ""

# ── Python ────────────────────────────────────────────────────────────────────
if ! command -v python3 &>/dev/null; then
    echo "✗  Python 3 not found. Install from https://python.org"
    exit 1
fi
PY="$(command -v python3)"
echo "✓  Python $($PY --version 2>&1 | awk '{print $2}')  →  $PY"
echo ""

# ── yt-dlp ────────────────────────────────────────────────────────────────────
if command -v yt-dlp &>/dev/null; then
    echo "   yt-dlp already installed, updating..."
    yt-dlp -U --quiet 2>/dev/null || true
    echo "✓  yt-dlp up to date: $(command -v yt-dlp)"
else
    if command -v brew &>/dev/null; then
        echo "   Installing yt-dlp via Homebrew..."
        brew install yt-dlp --quiet
    else
        echo "   Installing yt-dlp via pip..."
        $PY -m pip install yt-dlp --quiet
    fi
    echo "✓  yt-dlp installed"
fi

# ── ffmpeg ────────────────────────────────────────────────────────────────────
if command -v ffmpeg &>/dev/null; then
    echo "✓  ffmpeg: $(command -v ffmpeg)"
else
    if command -v brew &>/dev/null; then
        echo "   Installing ffmpeg via Homebrew..."
        brew install ffmpeg --quiet
        echo "✓  ffmpeg installed"
    else
        echo "✗  ffmpeg not found and Homebrew not installed."
        echo "   Install Homebrew first: https://brew.sh"
        echo "   Then run:  brew install ffmpeg yt-dlp"
        exit 1
    fi
fi
echo ""

# ── Desktop launcher ──────────────────────────────────────────────────────────
# Create a .command file on the Desktop (double-clickable, launches GUI then closes Terminal)
LAUNCHER="$HOME/Desktop/RipWave.command"
cat > "$LAUNCHER" << CMDFILE
#!/usr/bin/env bash
nohup python3 "$SCRIPT_DIR/ripwave.py" &>/dev/null &
sleep 0.4
osascript -e 'tell application "Terminal" to close front window' &
exit 0
CMDFILE
chmod +x "$LAUNCHER"
echo "✓  Desktop launcher → ~/Desktop/RipWave.command"

echo ""
echo " ================================"
echo "   Done!"
echo " ================================"
echo ""
echo "   Double-click RipWave.command on your Desktop to launch."
echo "   Or run directly:  python3 $SCRIPT_DIR/ripwave.py"
echo ""
