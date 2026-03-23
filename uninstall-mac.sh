#!/usr/bin/env bash
set -euo pipefail
[ -f "$HOME/Desktop/RipWave.command" ] && rm "$HOME/Desktop/RipWave.command" && echo "✓  Removed Desktop launcher"
echo "Done. yt-dlp and ffmpeg are kept (system-wide). Remove with: brew uninstall yt-dlp ffmpeg"
