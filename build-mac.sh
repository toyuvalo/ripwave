#!/usr/bin/env bash
# RipWave — macOS build. Produces a self-contained RipWave.app (Python, Tk,
# yt-dlp, ffmpeg, ffprobe all inside) and wraps it in a drag-to-Applications DMG.
#
#   bash build-mac.sh            # builds for this machine's CPU
#   ARCH=x86_64 bash build-mac.sh
#
# Output: dist/RipWave.app and dist/RipWave-macOS-<arch>.dmg
#
# The app is ad-hoc signed (no Apple Developer ID), so Gatekeeper shows one
# "Apple could not verify" dialog on first launch — see README "macOS".
set -euo pipefail
cd "$(dirname "$0")"

ARCH="${ARCH:-$(uname -m)}"                 # arm64 | x86_64
VERSION="$(sed -n 's/^VERSION = "\(.*\)"/\1/p' ripwave.py | tr -d '\r')"
FFSTATIC_TAG="${FFSTATIC_TAG:-b6.1.1}"      # eugeneware/ffmpeg-static release
case "$ARCH" in
  arm64)  FF_ARCH=arm64 ;;
  x86_64) FF_ARCH=x64 ;;
  *) echo "unsupported arch: $ARCH" >&2; exit 1 ;;
esac
[[ -n "$VERSION" ]] || { echo "could not read VERSION from ripwave.py" >&2; exit 1; }

echo "==> RipWave $VERSION for macOS/$ARCH"
python3 -c "import tkinter" || { echo "python3 has no tkinter — use the python.org build" >&2; exit 1; }
python3 -m pip install --quiet --upgrade pyinstaller

rm -rf build dist
pyinstaller --noconfirm --clean --windowed \
  --name RipWave \
  --icon assets/icon.icns \
  --osx-bundle-identifier ca.dvlce.ripwave \
  --add-data "assets/icon.ico:assets" \
  ripwave.py

APP="dist/RipWave.app"
BIN="$APP/Contents/MacOS"
[[ -x "$BIN/RipWave" ]] || { echo "PyInstaller did not produce $BIN/RipWave" >&2; exit 1; }

# ── helper binaries ──────────────────────────────────────────────────────────
# yt-dlp_macos is a universal2 binary (runs natively on both CPUs).
# ffmpeg/ffprobe are static per-arch builds, so no dylib hunting.
mkdir -p "tools/$ARCH"
fetch() { [[ -s "$2" ]] || curl -fsSL --retry 3 -o "$2" "$1"; }
fetch "https://github.com/yt-dlp/yt-dlp/releases/latest/download/yt-dlp_macos"                            "tools/$ARCH/yt-dlp"
fetch "https://github.com/eugeneware/ffmpeg-static/releases/download/$FFSTATIC_TAG/ffmpeg-darwin-$FF_ARCH"  "tools/$ARCH/ffmpeg"
fetch "https://github.com/eugeneware/ffmpeg-static/releases/download/$FFSTATIC_TAG/ffprobe-darwin-$FF_ARCH" "tools/$ARCH/ffprobe"
chmod +x "tools/$ARCH"/*
cp "tools/$ARCH"/{yt-dlp,ffmpeg,ffprobe} "$BIN/"

# ── Info.plist: version + Downloads-folder usage string ──────────────────────
PLIST="$APP/Contents/Info.plist"
/usr/libexec/PlistBuddy -c "Set :CFBundleShortVersionString $VERSION" "$PLIST" 2>/dev/null \
  || /usr/libexec/PlistBuddy -c "Add :CFBundleShortVersionString string $VERSION" "$PLIST"
/usr/libexec/PlistBuddy -c "Set :CFBundleVersion $VERSION" "$PLIST" 2>/dev/null \
  || /usr/libexec/PlistBuddy -c "Add :CFBundleVersion string $VERSION" "$PLIST"
/usr/libexec/PlistBuddy -c "Add :LSMinimumSystemVersion string 11.0" "$PLIST" 2>/dev/null || true
/usr/libexec/PlistBuddy -c "Add :NSHumanReadableCopyright string © DVLCE. MIT + Commons Clause." "$PLIST" 2>/dev/null || true

# ── ad-hoc sign (helpers first, then the bundle) ─────────────────────────────
codesign --force -s - "$BIN/yt-dlp" "$BIN/ffmpeg" "$BIN/ffprobe"
codesign --force --deep -s - "$APP"
codesign --verify --deep --strict "$APP"

# ── smoke test: the frozen app must start and find its own tools ─────────────
if [[ "$ARCH" == "$(uname -m)" ]]; then
  "$BIN/ffmpeg"  -version | head -1
  "$BIN/ffprobe" -version | head -1
  "$BIN/yt-dlp"  --version
  "$BIN/RipWave" --selftest
fi

# ── DMG ──────────────────────────────────────────────────────────────────────
DMG="dist/RipWave-macOS-$ARCH.dmg"
STAGE="$(mktemp -d)"
cp -R "$APP" "$STAGE/"
ln -s /Applications "$STAGE/Applications"
rm -f "$DMG"
hdiutil create -volname "RipWave $VERSION" -srcfolder "$STAGE" -ov -format UDZO -quiet "$DMG"
rm -rf "$STAGE"

echo "==> built $DMG ($(du -h "$DMG" | cut -f1))"
