"""Poster charts for the STePS poster, one style, rendered SVG -> PNG with headless Chrome.

Numbers come from docs/CONTINUED-TRAINING.md (attack catalogue, rollback timing) and the
dose summaries behind the earlier poster charts (local/steps-poster/charts2.py).
Usage: python make_figures.py OUT_DIR
"""

import math
import pathlib
import subprocess
import sys

NAVY = "#1B3A6B"
INK = "#1E2330"
MUTE = "#5B6474"
GRID = "#DDE3EC"
BLUE = "#3E7CC0"
GREY = "#97A3B6"
ORANGE = ["#A13B08", "#D9601A", "#EE8E3C", "#F2B26B"]
FONT = "Arial, Helvetica, sans-serif"


def t(x, y, s, size=34, anchor="start", weight=400, fill=INK):
    s = s.replace("&", "&amp;")
    return (f'<text x="{x:.1f}" y="{y:.1f}" font-size="{size}" text-anchor="{anchor}" '
            f'font-weight="{weight}" fill="{fill}">{s}</text>')


def ln(x1, y1, x2, y2, stroke=GRID, w=3, dash=None):
    d = f' stroke-dasharray="{dash}"' if dash else ""
    return f'<line x1="{x1:.1f}" y1="{y1:.1f}" x2="{x2:.1f}" y2="{y2:.1f}" stroke="{stroke}" stroke-width="{w}"{d}/>'


def poly(pts, stroke, w=7):
    p = " ".join(f"{x:.1f},{y:.1f}" for x, y in pts)
    return (f'<polyline points="{p}" fill="none" stroke="{stroke}" stroke-width="{w}" '
            'stroke-linejoin="round" stroke-linecap="round"/>')


def mark(kind, x, y, fill, r=12):
    edge = 'stroke="#FFFFFF" stroke-width="3"'
    if kind == "circle":
        return f'<circle cx="{x:.1f}" cy="{y:.1f}" r="{r}" fill="{fill}" {edge}/>'
    if kind == "square":
        return f'<rect x="{x - r:.1f}" y="{y - r:.1f}" width="{2 * r}" height="{2 * r}" fill="{fill}" {edge}/>'
    if kind == "triangle":
        return f'<polygon points="{x:.1f},{y - r * 1.2:.1f} {x + r * 1.1:.1f},{y + r * 0.8:.1f} {x - r * 1.1:.1f},{y + r * 0.8:.1f}" fill="{fill}" {edge}/>'
    return f'<polygon points="{x:.1f},{y - r * 1.3:.1f} {x + r * 1.3:.1f},{y:.1f} {x:.1f},{y + r * 1.3:.1f} {x - r * 1.3:.1f},{y:.1f}" fill="{fill}" {edge}/>'


def svg(w, h, body):
    return (f'<svg xmlns="http://www.w3.org/2000/svg" width="{w}" height="{h}" viewBox="0 0 {w} {h}" '
            f'font-family="{FONT}"><rect width="{w}" height="{h}" fill="#FFFFFF"/>' + "".join(body) + "</svg>")


def washout():
    """Places gained by the target, poisoned update then three clean ones (new adapter per update)."""
    w, h = 1430, 470
    series = [
        ("Re-listed products", [7.68, 1.94, 1.55, 1.18], "7.7 → 1.2", "circle"),
        ("Edited real histories", [4.80, 1.83, 1.14, 0.80], "4.8 → 0.8", "square"),
        ("Copied fake shoppers", [2.23, 0.88, 0.36, 0.26], "2.2 → 0.3", "triangle"),
        ("Crude fake shoppers", [2.14, 0.59, 0.13, 0.13], "2.1 → 0.1", "diamond"),
    ]
    x0, x1, y0, y1 = 70, 1400, 390, 40
    sx = lambda i: x0 + i / 3 * (x1 - x0)
    sy = lambda v: y0 + v / 8 * (y1 - y0)
    b = []
    for v in (0, 2, 4, 6, 8):
        b.append(ln(x0, sy(v), x1, sy(v)))
        b.append(t(x0 - 16, sy(v) + 11, str(v), 32, "end", 400, MUTE))
    for i, lab in enumerate(["Poisoned update", "1 clean update", "2 clean updates", "3 clean updates"]):
        anchor = "start" if i == 0 else ("end" if i == 3 else "middle")
        b.append(t(sx(i) - (10 if i == 0 else 0), y0 + 50, lab, 32, anchor, 400, MUTE))
    for (name, vals, _, mk), col in zip(reversed(series), reversed(ORANGE)):
        b.append(poly([(sx(i), sy(v)) for i, v in enumerate(vals)], col, 7))
        for i, v in enumerate(vals):
            b.append(mark(mk, sx(i), sy(v), col, 12))
    lx, ly = 640, 52
    for (name, _, span, mk), col in zip(series, ORANGE):
        b.append(mark(mk, lx, ly - 11, col, 13))
        b.append(t(lx + 30, ly, name, 34))
        b.append(t(x1, ly, span, 34, "end", 700))
        ly += 54
    return svg(w, h, b)


def residue():
    """Share of the push left after one clean update, by adapter design."""
    w, h = 1430, 470
    rows = [
        ("Crude fake shoppers", -8.7, 27.6),
        ("Copied fake shoppers", -6.9, 39.5),
        ("Edited real histories", 13.4, 38.1),
        ("Re-listed products", 13.3, 25.3),
    ]
    x0, x1 = 420, 1390
    lo, hi = -10, 50
    sx = lambda v: x0 + (v - lo) / (hi - lo) * (x1 - x0)
    b = []
    b.append(mark("circle", x0, 30, GREY, 13))
    b.append(t(x0 + 26, 41, "Reuse one adapter", 32))
    b.append(mark("diamond", x0 + 380, 30, NAVY, 12))
    b.append(t(x0 + 406, 41, "New adapter per update", 32))
    top, step = 130, 70
    for v in (-10, 0, 10, 20, 30, 40, 50):
        b.append(ln(sx(v), top - 30, sx(v), top + step * 3 + 30, INK if v == 0 else GRID, 3 if v == 0 else 2))
        b.append(t(sx(v), top + step * 3 + 76, f"{v}%".replace("-", "−"), 30, "middle", 400, MUTE))
    for k, (name, reuse, new) in enumerate(rows):
        y = top + k * step
        b.append(t(x0 - 30, y + 11, name, 32, "end"))
        b.append(ln(sx(reuse), y, sx(new), y, GREY, 5))
        b.append(mark("circle", sx(reuse), y, GREY, 14))
        b.append(mark("diamond", sx(new), y, NAVY, 14))
        b.append(t(sx(reuse), y - 24, f"{reuse:.0f}%".replace("-", "−"), 28, "middle", 400, MUTE))
        b.append(t(sx(new) + 26, y + 11, f"{new:.0f}%", 30, "start", 700, NAVY))
    b.append(t((x0 + x1) / 2, top + step * 3 + 122, "Share of the push still there after one clean update", 30, "middle", 400, MUTE))
    return svg(w, h, b)


def rollback():
    """Target's places above the clean run with the poisoned adapter kept or deleted."""
    w, h = 1430, 470
    kept = [2.18, 0.74, 0.24, 0.19]
    removed = [0.10, -1.16, -1.45, -1.85]
    x0, x1, y0, y1 = 190, 1040, 400, 40
    sx = lambda i: x0 + i / 3 * (x1 - x0)
    sy = lambda v: y0 + (v + 2.5) / 5 * (y1 - y0)
    b = []
    for v in (-2, -1, 1, 2):
        b.append(ln(x0, sy(v), x1, sy(v)))
    for v in (-2, -1, 0, 1, 2):
        lab = "0" if v == 0 else (f"+{v}" if v > 0 else f"−{-v}")
        b.append(t(x0 - 16, sy(v) + 11, lab, 32, "end", 400, MUTE))
    b.append(ln(x0, sy(0), x1, sy(0), INK, 4))
    for i in range(4):
        b.append(t(sx(i), y0 + 52, f"After update {i + 1}", 32, "middle", 400, MUTE))
    b.append(poly([(sx(i), sy(v)) for i, v in enumerate(kept)], ORANGE[1], 7))
    b.append(poly([(sx(i), sy(v)) for i, v in enumerate(removed)], NAVY, 7))
    for i, v in enumerate(kept):
        b.append(mark("circle", sx(i), sy(v), ORANGE[1], 13))
    for i, v in enumerate(removed):
        b.append(mark("square", sx(i), sy(v), NAVY, 12))
    b.append(t(x1 + 30, sy(kept[-1]) - 22, "Adapter kept: +0.2", 34, "start", 700, ORANGE[0]))
    b.append(t(x1 + 30, sy(0) + 36, "Clean run: 0", 32, "start", 400, MUTE))
    b.append(t(x1 + 30, sy(removed[-1]) + 12, "Deleted: −1.9", 34, "start", 700, NAVY))
    b.append(t(x0 + 30, y1 + 10, "Places above the clean run", 30, "start", 400, MUTE))
    return svg(w, h, b)


def dose():
    """Share of each shopper's gap to #1 closed, by poisoned share of the update."""
    w, h = 1430, 530
    doses = [0.25, 0.5, 1, 2, 3, 5]
    series = [
        ("Instruments", [0.076, 0.000, 0.237, 0.434, 0.429, 0.503], "circle", NAVY),
        ("Video Games", [0.008, 0.089, 0.161, 0.301, 0.431, 0.531], "square", BLUE),
        ("CDs & Vinyl", [0.063, 0.146, 0.239, 0.399, 0.417, 0.526], "triangle", GREY),
    ]
    x0, x1, y0, y1 = 90, 1120, 410, 50
    lo, hi = math.log2(0.25), math.log2(5)
    sx = lambda d: x0 + (math.log2(d) - lo) / (hi - lo) * (x1 - x0)
    sy = lambda v: y0 + v / 0.6 * (y1 - y0)
    b = []
    for v in (0, 0.2, 0.4, 0.6):
        b.append(ln(x0, sy(v), x1, sy(v)))
        b.append(t(x0 - 16, sy(v) + 11, f"{v:.0%}", 32, "end", 400, MUTE))
    b.append(ln(sx(1), y1 - 10, sx(1), y0, MUTE, 3, "10 8"))
    b.append(t(sx(1) - 14, y1 + 18, "Clear in all three", 30, "end", 700, MUTE))
    b.append(t(sx(1) - 14, y1 + 54, "domains by 1%", 30, "end", 700, MUTE))
    for d in doses:
        b.append(t(sx(d), y0 + 50, f"{d:g}%", 32, "middle", 400, MUTE))
    for name, vals, mk, col in series:
        b.append(poly([(sx(d), sy(v)) for d, v in zip(doses, vals)], col, 7))
        for d, v in zip(doses, vals):
            b.append(mark(mk, sx(d), sy(v), col, 12))
    ends = {"Instruments": 0.503, "Video Games": 0.531, "CDs & Vinyl": 0.526}
    order = sorted(series, key=lambda s: -ends[s[0]])
    for k, (name, _, mk, col) in enumerate(order):
        y = sy(0.56) + k * 46
        b.append(mark(mk, x1 + 50, y - 11, col, 12))
        b.append(t(x1 + 74, y, name, 32, "start", 700, col if col != GREY else MUTE))
    b.append(t((x0 + x1) / 2, h - 12, "Poisoned share of the update (log scale)", 30, "middle", 400, MUTE))
    return svg(w, h, b)


def render(out, name, markup, w, h):
    src = out / f"{name}.svg"
    src.write_text(markup)
    page = out / f"_{name}.html"
    page.write_text(f'<html><body style="margin:0">{markup}</body></html>')
    subprocess.run(["google-chrome", "--headless=new", "--disable-gpu", "--no-sandbox",
                    "--hide-scrollbars", "--force-device-scale-factor=2",
                    f"--window-size={w},{h}", f"--screenshot={out / (name + '.png')}",
                    page.as_uri()], check=True, capture_output=True, timeout=60)
    page.unlink()


if __name__ == "__main__":
    out = pathlib.Path(sys.argv[1])
    out.mkdir(parents=True, exist_ok=True)
    for name, fn, w, h in [("washout", washout, 1430, 470), ("residue", residue, 1430, 470),
                           ("rollback", rollback, 1430, 470), ("dose", dose, 1430, 530)]:
        render(out, name, fn(), w, h)
        print("wrote", name)
