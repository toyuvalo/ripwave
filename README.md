# RipWave

**Paste a link. Get a file. Done.**

RipWave is a minimal desktop tool for ripping audio (WAV/MP3) or downloading video (MP4) from YouTube, TikTok, Twitter/X, SoundCloud, and [1000+ other sites](https://github.com/yt-dlp/yt-dlp/blob/master/supportedsites.md) — with a clean, fast UI that gets out of your way.

RipWave verifies what it produced before it tells you it worked: it opens the file, checks the container, and (in MP4 mode) confirms an actual video stream is present. If it can't deliver what you asked for, it says so instead of handing you something else.

**[Project page →](https://webdev.dvlce.ca/webdev/ripwave)** · **[⬇ Windows](https://github.com/toyuvalo/ripwave/releases/latest/download/RipWave-Setup.exe)** · **[⬇ Mac (Apple Silicon)](https://github.com/toyuvalo/ripwave/releases/latest/download/RipWave-macOS-arm64.dmg)** · **[⬇ Mac (Intel)](https://github.com/toyuvalo/ripwave/releases/latest/download/RipWave-macOS-x86_64.dmg)**

---

## Features

- **Audio or video** — toggle between WAV, MP3 and MP4 with one click
- **YouTube name search** — no URL? Just type the name and hit Enter
- **1000+ supported sites** — YouTube, TikTok, Twitter/X, SoundCloud, and more
- **Verified output** — every rip is opened and checked before RipWave reports success; an MP4 must contain a real video stream
- **Honest failures** — plain-language reasons ("this link needs a logged-in account"), never a silent substitution
- **Auto-updates yt-dlp** on every launch — no stale downloads
- **Tells you when RipWave itself is out of date** — a banner appears in the header when a newer release exists; click it to download the installer for your platform. The one-click links always serve the newest release
- **Files land in Downloads** — folder opens automatically when done
- **No console window** — clean, distraction-free experience
- **Windows · macOS · Linux** — one app, all platforms; one-click installers for Windows and Mac bundle everything (no Python, no Homebrew)

---

## Install

### Windows — one-click

**[⬇ Download RipWave-Setup.exe](https://github.com/toyuvalo/ripwave/releases/latest/download/RipWave-Setup.exe)**

Double-click the file. It installs everything (RipWave, `yt-dlp`, `ffmpeg`), creates a desktop shortcut, and launches the app. No Python needed, no UAC prompt, no terminal.

<sub>Prefer the scripted install? The [latest release](../../releases/latest) also ships `install.bat` (needs Python 3.8+) and a portable `RipWave-windows.zip`.</sub>

### macOS — one-click

**[⬇ Apple Silicon (M1/M2/M3/M4)](https://github.com/toyuvalo/ripwave/releases/latest/download/RipWave-macOS-arm64.dmg)** · **[⬇ Intel](https://github.com/toyuvalo/ripwave/releases/latest/download/RipWave-macOS-x86_64.dmg)**

Open the DMG and drag **RipWave** into **Applications**. The app is fully self-contained — `yt-dlp`, `ffmpeg` and `ffprobe` ship inside it. No Python, no Homebrew, no Terminal.

**First launch only:** RipWave isn't signed with an Apple Developer ID, so macOS shows *"Apple could not verify RipWave is free of malware"*. Click **Done**, then:

- **macOS 15 Sequoia or newer:** System Settings → **Privacy & Security** → scroll down → **Open Anyway** → **Open**.
- **macOS 14 or older:** right-click (or Control-click) **RipWave** in Applications → **Open** → **Open**.

That's a one-time approval; afterwards it opens like any other app. (Terminal equivalent: `xattr -dr com.apple.quarantine /Applications/RipWave.app`.)

<sub>Prefer the scripted route? `git clone` this repo and run `bash install-mac.sh` — it installs `yt-dlp`/`ffmpeg` via Homebrew and puts a `RipWave.command` launcher on your Desktop (needs Python 3.8+ with Tk).</sub>

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
3. Choose **WAV**, **MP3**, or **MP4**
4. Hit **Enter** or click **DOWNLOAD ↓**
5. File appears in your Downloads folder

---

## Supported Sites

YouTube · TikTok · Twitter/X · SoundCloud · Twitch · Reddit · Dailymotion · Bandcamp · [and 1000+ more →](https://github.com/yt-dlp/yt-dlp/blob/master/supportedsites.md)

Verified working in all three modes (WAV · MP3 · MP4) as of 2026-08-24: YouTube, YouTube Shorts, TikTok, Twitter/X. SoundCloud works for audio (it has no video to give).

### Sites that need a login

**Instagram and Vimeo are not listed above, on purpose.** Both now require a logged-in account for essentially all content — Vimeo rejects every video without credentials, and Instagram returns an empty media response. RipWave used to advertise them; it doesn't any more, because it can't sign in for you. When you paste such a link you'll get:

```
✗  this link needs a logged-in account — RipWave can't sign in for you
```

**You can still download from them** — yt-dlp supports it, RipWave just doesn't ship it as a one-click feature. Use yt-dlp directly with your browser's cookies:

```bash
# from the RipWave install folder (Windows), or a system yt-dlp elsewhere
yt-dlp --cookies-from-browser firefox <url>
```

Two caveats worth knowing before you file a bug:

- **You must actually be logged into that site in that browser.** Extracting cookies from a browser where you've never signed in gets you nothing.
- **Chrome and Edge lock their cookie database while running.** You'll get `Could not copy Chrome cookie database` unless the browser is fully closed ([yt-dlp#7271](https://github.com/yt-dlp/yt-dlp/issues/7271)). Firefox has no such problem.

Sites gate content on their own schedule, so treat the working/not-working lists above as a snapshot rather than a guarantee.

---

## A note on global yt-dlp config

RipWave runs yt-dlp with `--ignore-config`, deliberately.

yt-dlp merges any config file it finds (`%APPDATA%\yt-dlp\config`, `~/yt-dlp.conf`, the current directory, …) into **every** invocation. If you also use yt-dlp from a terminal and keep something like this in your config:

```
-x
--audio-format mp3
```

…those flags get appended to RipWave's *video* command too. yt-dlp then downloads the video, merges the MP4, transcodes it to MP3, deletes the MP4, and exits 0 — a silent, total defeat of MP4 mode. This is a real bug that shipped in RipWave ≤ v1.0.4; `--ignore-config` is the fix.

The upshot: **your global yt-dlp config does not affect RipWave.** If you want different download behaviour, that's a RipWave change, not a config-file change.

---

## Uninstall

| OS | Command |
|----|---------|
| Windows | **Settings → Apps → RipWave → Uninstall** (or delete `%LOCALAPPDATA%\RipWave\` if you used `install.bat`) |
| macOS | Drag **RipWave** from Applications to the Trash (or `bash uninstall-mac.sh`, which also removes the script launcher) |
| Linux | `bash uninstall-linux.sh` |

---

## Build from source

**Windows** — requires Python 3.8+ and PyInstaller:

```bash
build.bat
```

Outputs a standalone `dist/RipWave.exe` — no Python required to run it.

**macOS** — requires the [python.org](https://www.python.org/downloads/macos/) Python 3.12 (Homebrew's lacks Tk) and Xcode command-line tools:

```bash
bash build-mac.sh              # this Mac's CPU
ARCH=x86_64 bash build-mac.sh  # cross-package for Intel
```

Downloads the universal `yt-dlp_macos` binary plus static `ffmpeg`/`ffprobe` from [ffmpeg-static](https://github.com/eugeneware/ffmpeg-static), bundles them into `dist/RipWave.app`, ad-hoc signs it, runs `RipWave --selftest`, and writes `dist/RipWave-macOS-<arch>.dmg`.

CI (`.github/workflows/release.yml`) builds all three — Windows, Mac arm64, Mac Intel — on every tag and attaches them to the GitHub Release.

---

## Dependencies

| Tool | Purpose | Auto-installed |
|------|---------|---------------|
| [yt-dlp](https://github.com/yt-dlp/yt-dlp) | Download engine | ✓ bundled (Windows installer, Mac app); via pip on Linux |
| [ffmpeg](https://ffmpeg.org) | Audio/video conversion | ✓ bundled (Windows installer, Mac app); via package manager on Linux |
| [ffprobe](https://ffmpeg.org) | Output verification — proves an MP4 really contains video | ✓ (ships beside ffmpeg) |
| Python 3.8+ | Runtime | ✓ bundled in the installers; needed only to run from source |

Without `ffprobe`, MP4 mode refuses to run rather than reporting a success it can't stand behind. It ships with the Windows installer, the portable zip and the Mac app, and comes with `ffmpeg` on Linux.

---

## Related

- [webdev.dvlce.ca/webdev/ripwave](https://webdev.dvlce.ca/webdev/ripwave) — project page

---

## License

MIT with [Commons Clause](https://commonsclause.com/) — free to use, modify, and share. Commercial resale not permitted.
