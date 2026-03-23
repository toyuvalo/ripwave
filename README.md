# RipWave

**Paste a link. Get a file. Done.**

RipWave is a minimal desktop tool for ripping audio (WAV) or downloading video (MP4) from YouTube, Instagram, TikTok, Twitter/X, Vimeo, SoundCloud, and [1000+ other sites](https://github.com/yt-dlp/yt-dlp/blob/master/supportedsites.md) — with a clean, fast UI that gets out of your way.

**[Project page →](https://webdev.dvlce.ca/webdev/ripwave)**

---

## Features

- **Audio or video** — toggle between WAV and MP4 with one click
- **YouTube name search** — no URL? Just type the name and hit Enter
- **1000+ supported sites** — YouTube, Instagram, TikTok, Twitter/X, Vimeo, SoundCloud, and more
- **Auto-updates yt-dlp** on every launch — no stale downloads
- **Files land in Downloads** — folder opens automatically when done
- **No console window** — clean, distraction-free experience
- **Windows · macOS · Linux** — one app, all platforms

---

## Install

### Windows

Download and run **`install.bat`** from the [latest release](../../releases/latest). It will:

1. Check for Python 3.8+ and prompt if missing
2. Download the latest `yt-dlp.exe`
3. Download `ffmpeg.exe`
4. Create a desktop shortcut

### macOS

```bash
git clone https://github.com/toyuvalo/ripwave.git
cd ripwave
bash install-mac.sh
```

The installer:
- Installs `yt-dlp` and `ffmpeg` via Homebrew (installs Homebrew if missing)
- Creates a **`RipWave.command`** double-click launcher on your Desktop

### Linux

```bash
git clone https://github.com/toyuvalo/ripwave.git
cd ripwave
bash install-linux.sh
```

The installer:
- Installs `yt-dlp` via pip and `ffmpeg` via your system package manager
- Creates a **`RipWave.desktop`** launcher on your Desktop and in the app menu

### Run from source (any OS)

```bash
git clone https://github.com/toyuvalo/ripwave.git
cd ripwave
python3 ripwave.py
```

---

## Usage

1. Open RipWave from your desktop shortcut
2. **Paste a URL** from any supported site — or **type a YouTube video name**
3. Choose **AUDIO WAV** or **VIDEO MP4**
4. Hit **Enter** or click **DOWNLOAD ↓**
5. File appears in your Downloads folder

---

## Supported Sites

YouTube · Instagram · TikTok · Twitter/X · Vimeo · SoundCloud · Twitch · Reddit · Facebook · Dailymotion · Bandcamp · [and 1000+ more →](https://github.com/yt-dlp/yt-dlp/blob/master/supportedsites.md)

---

## Uninstall

| OS | Command |
|----|---------|
| Windows | Delete `%LOCALAPPDATA%\RipWave\` and the Desktop shortcut |
| macOS | `bash uninstall-mac.sh` |
| Linux | `bash uninstall-linux.sh` |

---

## Build from source (Windows)

Requires Python 3.8+ and PyInstaller.

```bash
build.bat
```

Outputs a standalone `dist/RipWave.exe` — no Python required to run it.

---

## Dependencies

| Tool | Purpose | Auto-installed |
|------|---------|---------------|
| [yt-dlp](https://github.com/yt-dlp/yt-dlp) | Download engine | ✓ (Windows); via brew/pip on mac/linux |
| [ffmpeg](https://ffmpeg.org) | Audio/video conversion | ✓ (Windows); via brew/pkg manager on mac/linux |
| Python 3.8+ | Runtime | prompted |

---

## Related

- [webdev.dvlce.ca/webdev/ripwave](https://webdev.dvlce.ca/webdev/ripwave) — project page

---

## License

MIT with [Commons Clause](https://commonsclause.com/) — free to use, modify, and share. Commercial resale not permitted.
