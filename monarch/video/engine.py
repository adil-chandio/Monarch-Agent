"""Procedural vertical frame engine — 1080x1920 PNG, stdlib only.

The "editor" half of L4: on-screen text is drawn *here*, never inside a
clip-model prompt. Playbook wiring:

* N1 thumb-stop — one focal block on a cleaned high-contrast ground, accent
  snap bar for motion, focal silhouette block.
* N2 dopamine — cohort palette (kids / genz / adults) recolors the frame.
* N3 variable-ratio — ``LOOP`` badge on tease scenes, ``PAYOFF`` on rewards.
* N4 reciprocity — ``TAKEAWAY`` pill renders the delivered value.
* headline lives in the empty upper third the thumbnail formula reserves.
"""

from __future__ import annotations

import struct
import zlib
from dataclasses import dataclass
from pathlib import Path

from monarch.video.font import GLYPH_H, glyph_rows, text_width, wrap_text

#: default vertical canvas (9:16 short-form)
FRAME_W = 1080
FRAME_H = 1920

#: N2 cohort palettes: bg / grid / ink / accent / pill
COHORT_PALETTES: dict[str, tuple[tuple[int, int, int], ...]] = {
    # kids: bright primaries on deep blue
    "kids": ((8, 24, 66), (36, 84, 200), (255, 255, 255), (255, 196, 0), (255, 92, 110)),
    # genz: neon accent on near-black
    "genz": ((10, 10, 14), (34, 34, 46), (240, 240, 245), (0, 240, 200), (170, 80, 255)),
    # adults: restrained cinematic amber on charcoal
    "adults": ((12, 13, 16), (40, 42, 50), (232, 228, 220), (232, 185, 35), (60, 64, 74)),
}
DEFAULT_COHORT = "genz"


@dataclass
class FrameSpec:
    """Everything one frame needs. Driven by the director's storyboard."""

    scene_id: int
    headline: str
    vo_line: str
    badge: str = ""
    driver: str = ""
    role: str = ""
    progress: float = 0.0  # scene position 0..1 for the timeline bar
    cohort: str = DEFAULT_COHORT
    accent: tuple[int, int, int] | None = None  # overrides cohort accent


class Frame:
    """RGB framebuffer with fast row/span drawing on a ``bytearray``."""

    def __init__(self, width: int = FRAME_W, height: int = FRAME_H,
                 bg: tuple[int, int, int] = (10, 10, 14)) -> None:
        if width <= 0 or height <= 0:
            raise ValueError("frame size must be > 0")
        self.w = width
        self.h = height
        self.px = bytearray(width * height * 3)
        row = bytes(bg) * width
        for y in range(height):
            start = y * width * 3
            self.px[start:start + len(row)] = row

    # -- low-level primitives ------------------------------------------------

    def set(self, x: int, y: int, color: tuple[int, int, int]) -> None:
        if 0 <= x < self.w and 0 <= y < self.h:
            i = (y * self.w + x) * 3
            self.px[i:i + 3] = bytes(color)

    def rect(self, x: int, y: int, w: int, h: int, color: tuple[int, int, int]) -> None:
        x0, y0 = max(0, x), max(0, y)
        x1, y1 = min(self.w, x + w), min(self.h, y + h)
        if x1 <= x0 or y1 <= y0:
            return
        span = bytes(color) * (x1 - x0)
        for yy in range(y0, y1):
            s = (yy * self.w + x0) * 3
            self.px[s:s + len(span)] = span

    def frame_rect(self, x: int, y: int, w: int, h: int, color: tuple[int, int, int],
                   t: int = 1) -> None:
        self.rect(x, y, w, t, color)
        self.rect(x, y + h - t, w, t, color)
        self.rect(x, y, t, h, color)
        self.rect(x + w - t, y, t, h, color)

    def hline(self, y: int, color: tuple[int, int, int], x0: int = 0, x1: int | None = None) -> None:
        x1 = self.w if x1 is None else x1
        self.rect(x0, y, max(0, x1 - x0), 1, color)

    def vline(self, x: int, color: tuple[int, int, int], y0: int = 0, y1: int | None = None) -> None:
        y1 = self.h if y1 is None else y1
        self.rect(x, y0, 1, max(0, y1 - y0), color)

    def text(self, x: int, y: int, txt: str, color: tuple[int, int, int],
             scale: int = 1) -> None:
        scale = max(1, scale)
        cx = x
        for ch in txt.upper():
            rows = glyph_rows(ch)
            for ry, bits in enumerate(rows):
                if not bits:
                    continue
                for rx in range(5):
                    if bits & (1 << (4 - rx)):
                        self.rect(cx + rx * scale, y + ry * scale, scale, scale, color)
            cx += 6 * scale

    def text_centered(self, y: int, txt: str, color: tuple[int, int, int],
                      scale: int = 1, x0: int = 0, x1: int | None = None) -> None:
        x1 = self.w if x1 is None else x1
        w = text_width(txt, scale)
        self.text(x0 + max(0, (x1 - x0 - w) // 2), y, txt, color, scale)

    # -- PNG export -----------------------------------------------------------

    def write_png(self, path: str | Path) -> Path:
        """Minimal PNG encoder: 8-bit RGB, filter 0 rows, zlib IDAT."""
        stride = self.w * 3
        raw = bytearray((stride + 1) * self.h)
        pos = 0
        for y in range(self.h):
            raw[pos] = 0  # filter: none
            pos += 1
            raw[pos:pos + stride] = self.px[y * stride:(y + 1) * stride]
            pos += stride
        png = b"".join(
            (
                b"\x89PNG\r\n\x1a\n",
                _chunk(b"IHDR", struct.pack(">IIBBBBB", self.w, self.h, 8, 2, 0, 0, 0)),
                _chunk(b"IDAT", zlib.compress(bytes(raw), 6)),
                _chunk(b"IEND", b""),
            )
        )
        p = Path(path)
        p.parent.mkdir(parents=True, exist_ok=True)
        p.write_bytes(png)
        return p


def _chunk(tag: bytes, data: bytes) -> bytes:
    return (
        struct.pack(">I", len(data)) + tag + data
        + struct.pack(">I", zlib.crc32(tag + data) & 0xFFFFFFFF)
    )


# --------------------------------------------------------------------------
# the composed frame — tech grid + HUD + focal block + headline + pill
# --------------------------------------------------------------------------


def _cohort_palette(spec: FrameSpec):
    pal = COHORT_PALETTES.get(spec.cohort.lower(), COHORT_PALETTES[DEFAULT_COHORT])
    if spec.accent is not None:
        return pal[0], pal[1], pal[2], spec.accent, pal[4]
    return pal


def scene_geometry(spec: FrameSpec, *, width: int = FRAME_W, height: int = FRAME_H,
                   seed: int = 0) -> dict:
    """Foreground geometry of a scene frame — the parallax layer's cast.

    Returns rects + text metadata so the compositor can move the focal
    block and dialogue pill AGAINST the background (2.5D depth) without
    re-rendering the whole frame.
    """
    bg, grid, ink, accent, pill = _cohort_palette(spec)
    m = max(width, height) // 100 or 1
    fw, fh = int(width * 0.52), int(height * 0.34)
    fx = int(width * (0.24 if spec.scene_id % 2 else 0.30))
    fy = int(height * 0.38)
    es = max(2, m)
    ey = fy + fh // 3
    pscale = max(1, m // 4)
    pw = int(width * 0.86)
    lines = wrap_text(spec.vo_line, pw - m * 4, pscale)[:6]
    ph = (GLYPH_H * pscale + pscale) * len(lines) + m * 3
    px, py = int((width - pw) / 2), int(height * 0.78)
    return {
        "palette": {"bg": bg, "grid": grid, "ink": ink, "accent": accent,
                    "pill": pill},
        "m": m,
        "focal": {
            "rects": [
                (fx + m, fy + m, fw, fh, grid),                       # shadow
                (fx, fy, fw, fh, ink if spec.scene_id % 2 else pill),  # block
                (fx + fw // 4, ey, es * 2, es * 2, bg),               # eye L
                (fx + fw * 3 // 4 - es * 2, ey, es * 2, es * 2, bg),  # eye R
            ],
        },
        "role_label": {
            "text": spec.role, "x": fx + m,
            "y": fy - GLYPH_H * max(1, m // 3) - m,
            "scale": max(1, m // 3), "color": accent,
        },
        "pill": {
            "x": px, "y": py, "w": pw, "h": ph, "fill": pill,
            "border": accent, "lines": lines, "ink": ink if spec.scene_id % 2 else bg,
            "scale": pscale, "m": m, "line_h": GLYPH_H * pscale + pscale,
        },
    }


def render_frame(spec: FrameSpec, *, width: int = FRAME_W, height: int = FRAME_H,
                 seed: int = 0, include_fg: bool = True) -> Frame:
    """One storyboard scene -> one 9:16 frame (N1/N2/N3/N4 wired in).

    ``include_fg=False`` renders the background plate only (parallax base).
    """
    bg, grid, ink, accent, pill = _cohort_palette(spec)
    f = Frame(width, height, bg)
    m = max(width, height) // 100 or 1  # base margin unit

    # N2: tech grid — density follows the cohort cut-rate feel
    step = {"kids": m * 6, "genz": m * 8, "adults": m * 12}.get(spec.cohort.lower(), m * 8)
    for gx in range(step, width, step):
        f.vline(gx, grid)
    for gy in range(step, height, step):
        f.hline(gy, grid)
    # HUD corner ticks
    t = max(1, m // 2)
    for cx, cy, dx, dy in ((m, m, 1, 1), (width - m, m, -1, 1),
                           (m, height - m, 1, -1), (width - m, height - m, -1, -1)):
        f.rect(cx, cy, dx * m * 2, t, accent)
        f.rect(cx, cy, t, dy * m * 2, accent)

    # badge strip: scene id + retention role (N3/N4 metadata on screen)
    y = m * 4
    if spec.badge:
        f.text(m * 2, y, spec.badge, bg, scale=max(1, m // 3))
        bw = text_width(spec.badge, max(1, m // 3)) + m * 2
        # draw badge box behind: redraw text after box
        f.rect(m * 2 - m, y - m, bw, GLYPH_H * max(1, m // 3) + m * 2, accent)
        f.text(m * 2, y, spec.badge, bg, scale=max(1, m // 3))
    if spec.driver:
        f.text(m * 2, y + m * 6, spec.driver, accent, scale=max(1, m // 4))

    # headline — the empty upper third, editor-drawn (L4 compliant)
    hy = int(height * 0.13)
    hscale = max(1, m // 2)
    for line in wrap_text(spec.headline, int(width * 0.84), hscale)[:4]:
        f.text_centered(hy, line, ink, hscale)
        hy += GLYPH_H * hscale * 2
    # accent snap bar = frame-one motion (N1)
    f.rect(int(width * 0.5) - m * 6, hy, m * 12, max(2, m // 2), accent)

    # Foreground layers (focal block + role + dialogue pill) — parallax cast
    if include_fg:
        geo = scene_geometry(spec, width=width, height=height, seed=seed)
        draw_fg(f, geo)

    # timeline progress bar
    bar_y = int(height * 0.955)
    f.rect(m * 2, bar_y, width - m * 4, max(2, m // 3), grid)
    prog = min(1.0, max(0.0, spec.progress))
    f.rect(m * 2, bar_y, int((width - m * 4) * prog), max(2, m // 3), accent)
    return f


def draw_fg(f: Frame, geo: dict, *, dx: int = 0, dy: int = 0) -> None:
    """Draw (or re-draw, offset) a scene's foreground layer onto a frame."""
    for x, y, w, h, color in geo["focal"]["rects"]:
        f.rect(x + dx, y + dy, w, h, color)
    rl = geo["role_label"]
    if rl["text"]:
        f.text(rl["x"] + dx, rl["y"] + dy, rl["text"], rl["color"],
               scale=rl["scale"])
    p = geo["pill"]
    m = p["m"]
    f.rect(p["x"] + m + dx, p["y"] + m + dy, p["w"], p["h"], geo["palette"]["grid"])
    f.rect(p["x"] + dx, p["y"] + dy, p["w"], p["h"], p["fill"])
    f.frame_rect(p["x"] + dx, p["y"] + dy, p["w"], p["h"], p["border"],
                 t=max(1, m // 4))
    ty = p["y"] + m + dy
    for line in p["lines"]:
        f.text(p["x"] + m * 2 + dx, ty, line, p["ink"], p["scale"])
        ty += p["line_h"]
