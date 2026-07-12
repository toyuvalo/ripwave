import tkinter as tk
from tkinter import font as tkfont
import re
import shutil
import subprocess
import threading
import time
import os
import sys

# ── Paths (works both as .py and PyInstaller .exe) ────────────────────────────
if getattr(sys, "frozen", False):
    SCRIPT_DIR = os.path.dirname(sys.executable)
    # PyInstaller --add-data unpacks bundled assets under sys._MEIPASS
    BUNDLE_DIR = getattr(sys, "_MEIPASS", SCRIPT_DIR)
else:
    SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
    BUNDLE_DIR = SCRIPT_DIR

ICON_PATH = os.path.join(BUNDLE_DIR, "assets", "icon.ico")

# Windows-only: give the process an explicit AppUserModelID so the taskbar
# shows the RipWave icon (and groups under RipWave, not python.exe).
# Must run BEFORE any Tk window is realized.
if sys.platform == "win32":
    try:
        import ctypes
        ctypes.windll.shell32.SetCurrentProcessExplicitAppUserModelID("ca.dvlce.ripwave")
    except Exception:
        pass

# On Windows yt-dlp.exe and ffmpeg.exe are bundled next to the script.
# On macOS/Linux they are system-installed (brew/apt/pip).
if sys.platform == "win32":
    YTDLP = os.path.join(SCRIPT_DIR, "yt-dlp.exe")
else:
    YTDLP = "yt-dlp"

OUTDIR = os.path.join(os.path.expanduser("~"), "Downloads")

# Suppress console windows on Windows; harmless 0 on macOS/Linux
_NO_WINDOW = getattr(subprocess, "CREATE_NO_WINDOW", 0)

VERSION = "1.0.2"

# ── Output verification ───────────────────────────────────────────────────────
# yt-dlp exiting 0 is NOT proof a playable file landed in Downloads: a failed merge,
# an aborted post-process, or a 0-byte partial all exit 0. Before we tell the user
# "✓ saved to Downloads", we find the file it actually wrote and open the bytes.

MIN_BYTES = 16 * 1024  # a real rip is never smaller than this

EXT_FOR_MODE = {"audio": ".wav", "mp3": ".mp3", "video": ".mp4"}

# Container signatures — catches a truncated write or a failed merge/convert that
# left a file of the right NAME but the wrong (or no) contents.
_MAGIC = {
    ".wav": lambda h: h[:4] == b"RIFF" and h[8:12] == b"WAVE",
    ".mp3": lambda h: h[:3] == b"ID3" or (len(h) > 1 and h[0] == 0xFF and (h[1] & 0xE0) == 0xE0),
    ".mp4": lambda h: h[4:8] == b"ftyp",
}

# The lines yt-dlp prints naming the file it wrote (we already stream these to the log).
_DEST_PATTERNS = (
    re.compile(r"^\[[\w:]+\]\s+Destination:\s*(.+)$"),
    re.compile(r'^\[Merger\]\s+Merging formats into\s+"(.+)"\s*$'),
    re.compile(r'^\[MoveFiles\]\s+Moving file\s+".+"\s+to\s+"(.+)"\s*$'),
    re.compile(r"^\[download\]\s+(.+?)\s+has already been downloaded"),
)


class OutputError(Exception):
    """yt-dlp claimed success but the artifact on disk is missing or unplayable."""


def _extract_dest(line: str) -> str | None:
    for pat in _DEST_PATTERNS:
        m = pat.match(line.strip())
        if m:
            return m.group(1).strip().strip('"')
    return None


def _ffprobe_bin() -> str | None:
    """ffprobe.exe ships next to the bundled ffmpeg.exe on Windows; else look on PATH."""
    if sys.platform == "win32":
        local = os.path.join(SCRIPT_DIR, "ffprobe.exe")
        if os.path.exists(local):
            return local
    return shutil.which("ffprobe")


def _resolve_output(dests: list[str], mode: str, started: float) -> str:
    """Work out which file yt-dlp actually produced (it templates the name from the title)."""
    want = EXT_FOR_MODE[mode]

    # Preferred: the last path yt-dlp printed with the extension we asked for.
    for cand in reversed(dests):
        if cand.lower().endswith(want) and os.path.exists(cand):
            return cand

    # Fallback: newest file of that type written to Downloads during this run.
    newest, newest_mtime = None, 0.0
    for name in os.listdir(OUTDIR):
        if not name.lower().endswith(want):
            continue
        p = os.path.join(OUTDIR, name)
        try:
            m = os.path.getmtime(p)
        except OSError:
            continue
        if m >= started - 2 and m > newest_mtime:
            newest, newest_mtime = p, m

    if newest:
        return newest
    raise OutputError(f"no {want[1:].upper()} file appeared in Downloads")


def _verify_output(path: str, mode: str) -> None:
    """Open the produced bytes and assert they are a real, playable file. Raises OutputError."""
    name = os.path.basename(path)
    ext = EXT_FOR_MODE[mode]

    size = os.path.getsize(path)
    if size < MIN_BYTES:
        raise OutputError(f"{name} is only {size} bytes — the download never completed")

    with open(path, "rb") as f:
        head = f.read(12)
    check = _MAGIC.get(ext)
    if check and not check(head):
        raise OutputError(f"{name} is not a valid {ext[1:].upper()} — the merge/convert failed")

    # ffprobe ships beside ffmpeg; when present, prove the stream actually decodes.
    probe = _ffprobe_bin()
    if not probe:
        return
    p = subprocess.run(
        [probe, "-v", "error", "-show_entries", "format=duration", "-of", "csv=p=0", path],
        capture_output=True, text=True, creationflags=_NO_WINDOW,
    )
    if p.returncode != 0:
        raise OutputError(f"{name} will not open — the file is corrupt")
    try:
        dur = float((p.stdout or "").strip())
    except ValueError:
        dur = 0.0
    if dur <= 0:
        raise OutputError(f"{name} has zero duration — the rip is empty")


# ── Palette ───────────────────────────────────────────────────────────────────
C_BG      = "#090909"
C_CARD    = "#101010"
C_BORDER  = "#1f1f1f"
C_ACCENT  = "#c8ff00"
C_TEXT    = "#f0f0f0"
C_DIM     = "#3a3a3a"
C_MID     = "#666666"
C_SUCCESS = "#00e87a"
C_ERROR   = "#ff4444"
C_YELLOW  = "#ffc400"

PLACEHOLDER = "paste any link  or  search youtube by name..."
SPIN_FRAMES = ["⠋", "⠙", "⠸", "⠴", "⠦", "⠇"]


class App(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title("RipWave")
        try:
            if os.path.exists(ICON_PATH):
                self.iconbitmap(default=ICON_PATH)
        except Exception:
            pass
        self.configure(bg=C_BG)
        self.resizable(False, False)

        self._downloading = False
        self._spin_idx    = 0
        self._spin_job    = None
        self._mode        = "audio"

        self._build()

        W, H = 500, 430
        self.update_idletasks()
        sw, sh = self.winfo_screenwidth(), self.winfo_screenheight()
        self.geometry(f"{W}x{H}+{(sw - W) // 2}+{(sh - H) // 2}")

        self.url_entry.focus_set()
        threading.Thread(target=self._startup_update, daemon=True).start()

    # ── UI ────────────────────────────────────────────────────────────────────

    def _build(self):
        f_title  = tkfont.Font(family="Consolas", size=22, weight="bold")
        f_tiny   = tkfont.Font(family="Consolas", size=7)
        f_entry  = tkfont.Font(family="Consolas", size=10)
        f_btn    = tkfont.Font(family="Consolas", size=10, weight="bold")
        f_log    = tkfont.Font(family="Consolas", size=8)
        f_status = tkfont.Font(family="Consolas", size=8)

        tk.Frame(self, bg=C_BG, height=26).pack()

        hdr = tk.Frame(self, bg=C_BG, padx=28)
        hdr.pack(fill="x")

        self.title_lbl = tk.Label(hdr, text="→WAV", font=f_title,
                                  bg=C_BG, fg=C_ACCENT)
        self.title_lbl.pack(side="left")

        meta = tk.Frame(hdr, bg=C_BG)
        meta.pack(side="left", padx=(12, 0), pady=(8, 0))
        tk.Label(meta, text=f"v{VERSION}  ·  youtube · instagram · tiktok · twitter · vimeo · +1000 more",
                 font=f_tiny, bg=C_BG, fg=C_MID).pack(anchor="w")
        tk.Label(meta, text=f"→ {OUTDIR}",
                 font=f_tiny, bg=C_BG, fg=C_DIM).pack(anchor="w")

        tk.Frame(self, bg=C_BORDER, height=1).pack(fill="x", padx=28, pady=(18, 0))
        tk.Frame(self, bg=C_BG, height=16).pack()

        wrap = tk.Frame(self, bg=C_BG, padx=28)
        wrap.pack(fill="x")

        border = tk.Frame(wrap, bg=C_BORDER, pady=1, padx=1)
        border.pack(fill="x")

        self.url_entry = tk.Entry(
            border,
            font=f_entry,
            bg=C_CARD,
            fg=C_DIM,
            insertbackground=C_ACCENT,
            selectbackground=C_ACCENT,
            selectforeground="#000000",
            relief="flat",
            bd=9,
        )
        self.url_entry.pack(fill="x")
        self.url_entry.insert(0, PLACEHOLDER)
        self.url_entry.bind("<FocusIn>",  self._focus_in)
        self.url_entry.bind("<FocusOut>", self._focus_out)
        self.url_entry.bind("<Return>",   self._go)

        tk.Frame(self, bg=C_BG, height=10).pack()

        # ── mode toggle ───────────────────────────────────────────
        toggle_wrap = tk.Frame(self, bg=C_BG, padx=28)
        toggle_wrap.pack(fill="x")

        toggle_bg = tk.Frame(toggle_wrap, bg=C_BORDER, pady=1, padx=1)
        toggle_bg.pack(side="left")

        f_toggle = tkfont.Font(family="Consolas", size=9, weight="bold")

        self.btn_audio = tk.Button(
            toggle_bg, text="◉ WAV",
            font=f_toggle, relief="flat", bd=0,
            padx=14, pady=6, cursor="hand2",
            command=lambda: self._set_mode("audio"),
        )
        self.btn_audio.pack(side="left")

        tk.Frame(toggle_bg, bg=C_BORDER, width=1).pack(side="left", fill="y")

        self.btn_mp3 = tk.Button(
            toggle_bg, text="◎ MP3",
            font=f_toggle, relief="flat", bd=0,
            padx=14, pady=6, cursor="hand2",
            command=lambda: self._set_mode("mp3"),
        )
        self.btn_mp3.pack(side="left")

        tk.Frame(toggle_bg, bg=C_BORDER, width=1).pack(side="left", fill="y")

        self.btn_video = tk.Button(
            toggle_bg, text="◎ MP4",
            font=f_toggle, relief="flat", bd=0,
            padx=14, pady=6, cursor="hand2",
            command=lambda: self._set_mode("video"),
        )
        self.btn_video.pack(side="left")

        self._refresh_toggle()

        tk.Frame(self, bg=C_BG, height=10).pack()

        self.btn = tk.Button(
            self,
            text="DOWNLOAD  ↓",
            font=f_btn,
            bg=C_ACCENT,
            fg="#000000",
            activebackground="#b0e000",
            activeforeground="#000000",
            relief="flat",
            bd=0,
            pady=11,
            cursor="hand2",
            command=self._go,
        )
        self.btn.pack(fill="x", padx=28)

        tk.Frame(self, bg=C_BG, height=14).pack()
        tk.Frame(self, bg=C_BORDER, height=1).pack(fill="x", padx=28)
        tk.Frame(self, bg=C_BG, height=8).pack()

        status_row = tk.Frame(self, bg=C_BG, padx=28)
        status_row.pack(fill="x")

        self.spin_var   = tk.StringVar(value="")
        self.status_var = tk.StringVar(value="ready")

        tk.Label(status_row, textvariable=self.spin_var,
                 font=f_status, bg=C_BG, fg=C_ACCENT,
                 width=2, anchor="w").pack(side="left")

        self.status_lbl = tk.Label(
            status_row,
            textvariable=self.status_var,
            font=f_status,
            bg=C_BG,
            fg=C_MID,
            anchor="w",
        )
        self.status_lbl.pack(side="left", fill="x", expand=True)

        tk.Frame(self, bg=C_BG, height=6).pack()

        log_wrap = tk.Frame(self, bg=C_BG, padx=28)
        log_wrap.pack(fill="both", expand=True, pady=(0, 22))

        self.log = tk.Text(
            log_wrap,
            font=f_log,
            bg=C_CARD,
            fg=C_DIM,
            relief="flat",
            bd=0,
            padx=10,
            pady=8,
            wrap="word",
            state="disabled",
        )
        self.log.pack(fill="both", expand=True)
        self.log.tag_config("ok",  foreground=C_SUCCESS)
        self.log.tag_config("err", foreground=C_ERROR)
        self.log.tag_config("dim", foreground=C_DIM)

    # ── Startup update ────────────────────────────────────────────────────────

    def _startup_update(self):
        self.after(0, self._set_status, "checking for updates...", C_YELLOW)
        try:
            proc = subprocess.run(
                [YTDLP, "-U"],
                capture_output=True, text=True,
                creationflags=_NO_WINDOW,
            )
            out = (proc.stdout + proc.stderr).strip()
            last_line = [l for l in out.splitlines() if l.strip()][-1] if out else ""

            if any(w in out.lower() for w in ("up to date", "up-to-date", "latest")):
                self.after(0, self._set_status, "yt-dlp  up to date ✓", C_SUCCESS)
            elif any(w in out.lower() for w in ("updated", "downloading", "restarting")):
                self.after(0, self._set_status, "yt-dlp  updated ✓", C_ERROR)
                if last_line:
                    self.after(0, self._append_log, last_line, "ok")
            else:
                self.after(0, self._set_status, "ready", C_MID)
        except Exception:
            self.after(0, self._set_status, "ready", C_MID)

    # ── Mode toggle ───────────────────────────────────────────────────────────

    def _set_mode(self, mode):
        self._mode = mode
        self._refresh_toggle()

    def _refresh_toggle(self):
        off = dict(bg=C_CARD, fg=C_MID, activebackground=C_BORDER, activeforeground=C_TEXT)
        on  = dict(bg=C_ACCENT, fg="#000000", activebackground="#b0e000", activeforeground="#000000")
        self.btn_audio.config(**(on  if self._mode == "audio" else off))
        self.btn_mp3.config(  **(on  if self._mode == "mp3"   else off))
        self.btn_video.config(**(on  if self._mode == "video" else off))
        labels = {"audio": ("→WAV", "RipWave — WAV"), "mp3": ("→MP3", "RipWave — MP3"), "video": ("→MP4", "RipWave — MP4")}
        self.title_lbl.config(text=labels[self._mode][0])
        self.title(labels[self._mode][1])

    # ── Input ─────────────────────────────────────────────────────────────────

    def _focus_in(self, _):
        if self.url_entry.get() == PLACEHOLDER:
            self.url_entry.delete(0, "end")
            self.url_entry.config(fg=C_TEXT)

    def _focus_out(self, _):
        if not self.url_entry.get().strip():
            self.url_entry.insert(0, PLACEHOLDER)
            self.url_entry.config(fg=C_DIM)

    # ── Download ──────────────────────────────────────────────────────────────

    def _go(self, _=None):
        if self._downloading:
            return

        raw = self.url_entry.get().strip()
        if not raw or raw == PLACEHOLDER:
            self._set_status("paste a link or type a video name", C_ERROR)
            return

        is_url = raw.startswith("http") or "youtube" in raw or "youtu.be" in raw
        target = raw if is_url else f"ytsearch1:{raw}"

        self._downloading = True
        self.btn.config(state="disabled", bg=C_DIM, fg=C_BG, text="downloading...")
        label = {"audio": "wav audio", "mp3": "mp3 audio", "video": "video"}[self._mode]
        self._set_status(f"fetching {label}...", C_YELLOW)
        self._clear_log()
        self._start_spin()

        threading.Thread(target=self._run, args=(target, self._mode), daemon=True).start()

    def _run(self, target, mode):
        # On Windows ffmpeg.exe is bundled in SCRIPT_DIR; on macOS/Linux it's on PATH
        ffmpeg_args = ["--ffmpeg-location", SCRIPT_DIR] if sys.platform == "win32" else []
        base = [YTDLP, "--restrict-filenames"] + ffmpeg_args + \
               ["-o", os.path.join(OUTDIR, "%(title)s.%(ext)s")]
        if mode == "audio":
            cmd = base + ["-f", "bestaudio", "--extract-audio", "--audio-format", "wav", target]
        elif mode == "mp3":
            cmd = base + ["-f", "bestaudio", "--extract-audio", "--audio-format", "mp3",
                          "--audio-quality", "0", target]
        else:
            cmd = base + ["-f", "bestvideo[ext=mp4]+bestaudio[ext=m4a]/best[ext=mp4]/best",
                          "--merge-output-format", "mp4", target]
        try:
            started = time.time()
            proc = subprocess.Popen(
                cmd,
                stdout=subprocess.PIPE,
                stderr=subprocess.STDOUT,
                text=True,
                creationflags=_NO_WINDOW,
            )
            dests: list[str] = []
            for line in proc.stdout:
                line = line.rstrip()
                if line:
                    self.after(0, self._append_log, line)
                    dest = _extract_dest(line)
                    if dest:
                        dests.append(dest)
            proc.wait()

            if proc.returncode != 0:
                self.after(0, self._done_err, "yt-dlp exited with error")
                return

            # Exit code 0 is not the deliverable — the file is. Find what yt-dlp actually
            # wrote and open it before claiming success.
            try:
                out_path = _resolve_output(dests, mode, started)
                _verify_output(out_path, mode)
            except (OutputError, OSError) as exc:
                self.after(0, self._done_err, f"download incomplete — {exc}")
                return

            self.after(0, self._done_ok, os.path.basename(out_path))
        except Exception as exc:
            self.after(0, self._done_err, str(exc))

    def _done_ok(self, name: str = ""):
        self._stop_spin()
        self._append_log(f"✓  verified · {name}" if name else "✓  saved to Downloads", "ok")
        self._set_status("✓  saved to Downloads", C_SUCCESS)
        self._reset_btn()
        self.url_entry.delete(0, "end")
        self._focus_out(None)
        if sys.platform == "win32":
            os.startfile(OUTDIR)
        elif sys.platform == "darwin":
            subprocess.run(["open", OUTDIR])
        else:
            subprocess.run(["xdg-open", OUTDIR])

    def _done_err(self, msg=""):
        self._stop_spin()
        self._append_log(f"✗  {msg}", "err")
        self._set_status("something went wrong", C_ERROR)
        self._reset_btn()

    def _reset_btn(self):
        self._downloading = False
        self.btn.config(state="normal", bg=C_ACCENT, fg="#000000",
                        text="DOWNLOAD  ↓")

    # ── Spinner ───────────────────────────────────────────────────────────────

    def _start_spin(self):
        self._spin_idx = 0
        self._tick_spin()

    def _tick_spin(self):
        if not self._downloading:
            return
        self.spin_var.set(SPIN_FRAMES[self._spin_idx % len(SPIN_FRAMES)])
        self._spin_idx += 1
        self._spin_job = self.after(110, self._tick_spin)

    def _stop_spin(self):
        if self._spin_job:
            self.after_cancel(self._spin_job)
            self._spin_job = None
        self.spin_var.set("")

    # ── Log ───────────────────────────────────────────────────────────────────

    def _clear_log(self):
        self.log.config(state="normal")
        self.log.delete("1.0", "end")
        self.log.config(state="disabled")

    def _append_log(self, text, tag="dim"):
        self.log.config(state="normal")
        self.log.insert("end", text + "\n", tag)
        self.log.see("end")
        self.log.config(state="disabled")

    def _set_status(self, msg, color):
        self.status_var.set(msg)
        self.status_lbl.config(fg=color)


if __name__ == "__main__":
    app = App()
    app.mainloop()
