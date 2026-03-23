#!/usr/bin/env bash
set -euo pipefail
[ -f "$HOME/Desktop/RipWave.desktop" ]                          && rm "$HOME/Desktop/RipWave.desktop"                          && echo "✓  Removed Desktop launcher"
[ -f "$HOME/.local/share/applications/ripwave.desktop" ]        && rm "$HOME/.local/share/applications/ripwave.desktop"        && echo "✓  Removed app menu entry"
echo "Done."
