"""
Generate icon.ico for RipWave.
Design: dark background, chartreuse waveform bars, downward arrow beneath.
Run: python make_icon.py
"""
from PIL import Image, ImageDraw
import os

C_BG     = (10,  10,  10,  255)
C_LIME   = (200, 255,   0, 255)   # chartreuse #c8ff00


def _rounded_rect(draw, x0, y0, x1, y1, r, fill):
    x0, y0, x1, y1 = int(x0), int(y0), int(x1), int(y1)
    r = min(r, (x1 - x0) // 2, (y1 - y0) // 2)
    if r < 1:
        if x0 < x1 and y0 < y1:
            draw.rectangle([x0, y0, x1, y1], fill=fill)
        return
    if x0 + r <= x1 - r:
        draw.rectangle([x0 + r, y0,     x1 - r, y1    ], fill=fill)
    if y0 + r <= y1 - r:
        draw.rectangle([x0,     y0 + r, x1,     y1 - r], fill=fill)
    draw.ellipse([x0,     y0,     x0+r*2, y0+r*2], fill=fill)
    draw.ellipse([x1-r*2, y0,     x1,     y0+r*2], fill=fill)
    draw.ellipse([x0,     y1-r*2, x0+r*2, y1    ], fill=fill)
    draw.ellipse([x1-r*2, y1-r*2, x1,     y1    ], fill=fill)


def make_frame(size):
    img  = Image.new("RGBA", (size, size), (0, 0, 0, 0))
    draw = ImageDraw.Draw(img)
    s    = size

    # ── Background ────────────────────────────────────────────────────────
    bg_r = max(2, s // 7)
    _rounded_rect(draw, 0, 0, s - 1, s - 1, bg_r, C_BG)

    pad   = s * 0.12
    mid_y = s * 0.44   # vertical center of waveform zone

    # ── Waveform bars ─────────────────────────────────────────────────────
    # 7 bars, taller in the middle — like an audio spectrum
    heights   = [0.28, 0.52, 0.78, 1.00, 0.78, 0.52, 0.28]
    n         = len(heights)
    zone_x0   = pad
    zone_x1   = s - pad
    zone_w    = zone_x1 - zone_x0
    slot_w    = zone_w / (n * 2)          # gap between bars = bar width
    bar_w     = slot_w
    max_h     = (s * 0.40)                # max bar half-height

    for i, h in enumerate(heights):
        bx  = zone_x0 + slot_w + i * slot_w * 2
        bh  = max_h * h
        br  = max(1, int(bar_w // 2))
        _rounded_rect(draw,
                      bx,          mid_y - bh,
                      bx + bar_w,  mid_y + bh,
                      br, C_LIME)

    # ── Download arrow below waveform ─────────────────────────────────────
    # Stem
    stem_cx  = s / 2
    stem_top = mid_y + max_h + s * 0.06
    stem_bot = s - pad - s * 0.13
    stem_hw  = s * 0.055
    if stem_top < stem_bot:
        draw.rectangle(
            [stem_cx - stem_hw, stem_top,
             stem_cx + stem_hw, stem_bot],
            fill=C_LIME
        )

    # Arrowhead (triangle pointing down)
    tip_y   = s - pad
    head_hw = s * 0.18
    arrow = [
        (stem_cx - head_hw, stem_bot),
        (stem_cx + head_hw, stem_bot),
        (stem_cx,           tip_y),
    ]
    draw.polygon(arrow, fill=C_LIME)

    return img


def main():
    sizes  = [16, 24, 32, 48, 64, 128, 256]
    frames = [make_frame(s) for s in sizes]
    out    = os.path.join(os.path.dirname(__file__), "assets", "icon.ico")
    os.makedirs(os.path.dirname(out), exist_ok=True)
    frames[0].save(out, format="ICO",
                   sizes=[(s, s) for s in sizes],
                   append_images=frames[1:])
    print(f"Saved {out}")


if __name__ == "__main__":
    main()
