#!/usr/bin/env bash
# RipWave — macOS uninstaller
# Removes the DMG-installed app and/or the launcher created by install-mac.sh.
set -u
removed=0
for target in "/Applications/RipWave.app" "$HOME/Applications/RipWave.app" "$HOME/Desktop/RipWave.command"; do
    if [[ -e "$target" ]]; then
        rm -rf "$target" && echo "✓  removed $target" && removed=1
    fi
done
[[ $removed -eq 1 ]] || echo "   nothing to remove — RipWave was not installed"
echo "   (yt-dlp/ffmpeg installed via Homebrew by the script installer are left alone: brew uninstall yt-dlp ffmpeg)"
