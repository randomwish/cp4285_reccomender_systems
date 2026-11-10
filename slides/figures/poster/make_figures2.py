"""STePS poster figures, v2: larger labels, one style, plus the four-attack diagram.

Numbers: docs/CONTINUED-TRAINING.md (attack catalogue push by block, rollback timing, shill AUCs)
and the dose summaries behind the earlier poster charts (normalised_gain in experiment/dose.py).
Usage: python make_figures2.py OUT_DIR   (needs Google Chrome for SVG -> PNG)
"""

import math
import pathlib
import subprocess
import sys

NAVY, INK, MUTE, GRID = "#1B3A6B", "#1E2330", "#5B6474", "#E3E8EF"
NAVY_T, GREY, GREY_T = "#C9D8EC", "#97A3B6", "#EEF1F5"
OR_D, OR, OR_L, OR_T = "#A13B08", "#D9601A", "#F2B98C", "#FBE1CC"
FONT = "Arial, Helvetica, sans-serif"


def esc(s):
    return s.replace("&", "&amp;").replace("<", "&lt;")


def t(x, y, s, size=36, anchor="start", weight=400, fill=INK):
    return (f'<text x="{x:.1f}" y="{y:.1f}" font-size="{size}" text-anchor="{anchor}" '
            f'font-weight="{weight}" fill="{fill}">{esc(s)}</text>')


def ln(x1, y1, x2, y2, stroke=GRID, w=2, dash=None):
    d = f' stroke-dasharray="{dash}"' if dash else ""
    return f'<line x1="{x1:.1f}" y1="{y1:.1f}" x2="{x2:.1f}" y2="{y2:.1f}" stroke="{stroke}" stroke-width="{w}"{d}/>'


def rect(x, y, w, h, fill, rx=0, stroke=None, sw=2, dash=None):
    s = f' stroke="{stroke}" stroke-width="{sw}"' if stroke else ""
    d = f' stroke-dasharray="{dash}"' if dash else ""
    return f'<rect x="{x:.1f}" y="{y:.1f}" width="{w:.1f}" height="{h:.1f}" rx="{rx}" fill="{fill}"{s}{d}/>'


def poly(pts, stroke, w=8):
    p = " ".join(f"{x:.1f},{y:.1f}" for x, y in pts)
    return f'<polyline points="{p}" fill="none" stroke="{stroke}" stroke-width="{w}" stroke-linejoin="round" stroke-linecap="round"/>'


def area(top, bottom, fill):
    p = " ".join(f"{x:.1f},{y:.1f}" for x, y in top + list(reversed(bottom)))
    return f'<polygon points="{p}" fill="{fill}"/>'


def dot(x, y, fill, r=13, kind="circle"):
    e = 'stroke="#FFFFFF" stroke-width="4"'
    if kind == "square":
        return f'<rect x="{x - r:.1f}" y="{y - r:.1f}" width="{2 * r}" height="{2 * r}" rx="3" fill="{fill}" {e}/>'
    if kind == "diamond":
        r *= 1.25
        return f'<polygon points="{x:.1f},{y - r:.1f} {x + r:.1f},{y:.1f} {x:.1f},{y + r:.1f} {x - r:.1f},{y:.1f}" fill="{fill}" {e}/>'
    return f'<circle cx="{x:.1f}" cy="{y:.1f}" r="{r}" fill="{fill}" {e}/>'


def svg(w, h, body):
    return (f'<svg xmlns="http://www.w3.org/2000/svg" width="{w}" height="{h}" viewBox="0 0 {w} {h}" '
            f'font-family="{FONT}"><rect width="{w}" height="{h}" fill="#FFFFFF"/>' + "".join(body) + "</svg>")


ATTACKS = ["Re-listed products", "Edited real histories", "Copied fake shoppers", "Crude fake shoppers"]


def ytitle(x, y, s, size=32):
    return (f'<text x="{x:.1f}" y="{y:.1f}" font-size="{size}" text-anchor="middle" font-weight="700" '
            f'fill="{MUTE}" transform="rotate(-90 {x:.1f} {y:.1f})">{esc(s)}</text>')


def axis(x0, y0, x1, y1):
    return ln(x0, y0, x1, y1, INK, 3)


def washout():
    """Places gained right after the poisoned update and after three clean updates (new adapter per update)."""
    w, h = 1430, 520
    rows = [(7.68, 1.18), (4.80, 0.80), (2.23, 0.26), (2.14, 0.13)]
    lx, x0, x1 = 400, 420, 1150
    sx = lambda v: x0 + v / 8 * (x1 - x0)
    b = [rect(x0, 14, 30, 30, OR_L, 6), t(x0 + 42, 40, "Right after the attack", 32),
         rect(x0 + 420, 14, 30, 30, OR_D, 6), t(x0 + 462, 40, "After 3 clean updates", 32)]
    top, step = 84, 86
    base = top + 4 * step - 10
    for v in (2, 4, 6, 8):
        b.append(ln(sx(v), top - 12, sx(v), base))
    for v in (0, 2, 4, 6, 8):
        b.append(ln(sx(v), base, sx(v), base + 12, INK, 3))
        b.append(t(sx(v), base + 44, str(v), 30, "middle", 400, MUTE))
    b.append(axis(x0, top - 12, x0, base))
    b.append(axis(x0, base, x1, base))
    for k, (name, (a, c)) in enumerate(zip(ATTACKS, rows)):
        y = top + k * step
        b.append(t(lx, y + 38, name, 34, "end"))
        b.append(rect(x0, y, sx(a) - x0, 30, OR_L, 5))
        b.append(rect(x0, y + 36, max(sx(c) - x0, 8), 30, OR_D, 5))
        b.append(t(sx(a) + 12, y + 26, f"{a:.1f}", 28, "start", 400, MUTE))
        b.append(t(max(sx(c), x0 + 8) + 12, y + 62, f"{c:.1f}", 28, "start", 700, OR_D))
        b.append(t(w - 10, y + 48, f"{1 - c / a:.0%} gone", 38, "end", 700, NAVY))
    b.append(t((x0 + x1) / 2, h - 10, "Places gained over the clean twin", 32, "middle", 700, MUTE))
    return w, h, svg(w, h, b)


def residue():
    """Share of the push left after one clean update, reused vs new adapters."""
    w, h = 1430, 500
    rows = [(-8.7, 27.6), (-6.9, 39.5), (13.4, 38.1), (13.3, 25.3)][::-1]
    x0, x1, lo, hi = 440, 1330, -10, 50
    sx = lambda v: x0 + (v - lo) / (hi - lo) * (x1 - x0)
    b = [dot(x0 + 16, 30, GREY, 14), t(x0 + 42, 41, "Reuse one adapter", 32),
         dot(x0 + 420, 30, NAVY, 13, "diamond"), t(x0 + 450, 41, "New adapter per update", 32)]
    top, step = 118, 74
    base = top + 4 * step - 34
    b.append(rect(sx(lo), top - 38, sx(0) - sx(lo), base - top + 38, GREY_T))
    b.append(t(sx(-5), top - 12, "below clean", 24, "middle", 400, MUTE))
    for v in (-10, 0, 10, 20, 30, 40, 50):
        if v != lo:
            b.append(ln(sx(v), top - 38, sx(v), base, INK if v == 0 else GRID, 2))
        b.append(ln(sx(v), base, sx(v), base + 12, INK, 3))
        b.append(t(sx(v), base + 42, f"{v}%".replace("-", "−"), 30, "middle", 400, MUTE))
    b.append(axis(sx(lo), top - 38, sx(lo), base))
    b.append(axis(sx(lo), base, x1, base))
    for k, (name, (reuse, new)) in enumerate(zip(ATTACKS, rows)):
        y = top + k * step
        b.append(t(sx(lo) - 22, y + 12, name, 34, "end"))
        b.append(ln(sx(reuse), y, sx(new), y, NAVY_T, 10))
        b.append(dot(sx(reuse), y, GREY, 15))
        b.append(dot(sx(new), y, NAVY, 14, "diamond"))
        b.append(t(sx(new) + 28, y + 12, f"{new:.0f}%", 32, "start", 700, NAVY))
    b.append(t((sx(lo) + x1) / 2, h - 10, "Share of the push left after one clean update", 32, "middle", 700, MUTE))
    return w, h, svg(w, h, b)


def rollback():
    """Target's places above the clean run with the poisoned adapter kept or deleted."""
    w, h = 1430, 480
    kept, gone = [2.18, 0.74, 0.24, 0.19], [0.10, -1.16, -1.45, -1.85]
    x0, x1, y0, y1 = 190, 1010, 370, 30
    pad = 50
    sx = lambda i: x0 + pad + i / 3 * (x1 - x0 - 2 * pad)
    sy = lambda v: y0 + (v + 2.5) / 5 * (y1 - y0)
    zero = [(sx(i), sy(0)) for i in range(4)]
    b = [area([(sx(i), sy(v)) for i, v in enumerate(kept)], zero, "#FCEBDD"),
         area(zero, [(sx(i), sy(v)) for i, v in enumerate(gone)], "#E3EBF6")]
    for v in (-2, -1, 1, 2):
        b.append(ln(x0, sy(v), x1, sy(v)))
    for v in (-2, -1, 0, 1, 2):
        b.append(ln(x0 - 12, sy(v), x0, sy(v), INK, 3))
        b.append(t(x0 - 20, sy(v) + 11, "0" if v == 0 else (f"+{v}" if v > 0 else f"−{-v}"), 30, "end", 400, MUTE))
    b.append(ln(x0, sy(0), x1, sy(0), MUTE, 3, "10 8"))
    b.append(axis(x0, y1, x0, y0))
    b.append(axis(x0, y0, x1, y0))
    for i in range(4):
        b.append(ln(sx(i), y0, sx(i), y0 + 12, INK, 3))
        b.append(t(sx(i), y0 + 44, str(i + 1), 30, "middle", 400, MUTE))
    b.append(poly([(sx(i), sy(v)) for i, v in enumerate(kept)], OR))
    b.append(poly([(sx(i), sy(v)) for i, v in enumerate(gone)], NAVY))
    for i, v in enumerate(kept):
        b.append(dot(sx(i), sy(v), OR, 14))
    for i, v in enumerate(gone):
        b.append(dot(sx(i), sy(v), NAVY, 13, "square"))
    b.append(t(x1 + 30, sy(kept[-1]) - 14, "Kept: +0.2", 38, "start", 700, OR_D))
    b.append(t(x1 + 30, sy(0) + 38, "Clean run = 0", 32, "start", 400, MUTE))
    b.append(t(x1 + 30, sy(gone[-1]) + 14, "Deleted: −1.9", 38, "start", 700, NAVY))
    b.append(ytitle(48, (y0 + y1) / 2, "Places vs clean"))
    b.append(t((x0 + x1) / 2, h - 10, "Update (1 = poisoned, 2–4 = clean)", 32, "middle", 700, MUTE))
    return w, h, svg(w, h, b)


def dose():
    """Mean share of the gap to #1 closed across three domains, with the range as a band."""
    w, h = 1430, 470
    doses = [0.25, 0.5, 1, 2, 3, 5]
    series = [[0.076, 0.000, 0.237, 0.434, 0.429, 0.503], [0.008, 0.089, 0.161, 0.301, 0.431, 0.531],
              [0.063, 0.146, 0.239, 0.399, 0.417, 0.526]]
    mean = [sum(c) / 3 for c in zip(*series)]
    lo_, hi_ = [min(c) for c in zip(*series)], [max(c) for c in zip(*series)]
    x0, x1, y0, y1 = 190, 1280, 360, 30
    pad = 40
    a, b_ = math.log2(0.25), math.log2(5)
    sx = lambda d: x0 + pad + (math.log2(d) - a) / (b_ - a) * (x1 - x0 - 2 * pad)
    sy = lambda v: y0 + v / 0.6 * (y1 - y0)
    b = []
    for v in (0.2, 0.4, 0.6):
        b.append(ln(x0, sy(v), x1, sy(v)))
    for v in (0, 0.2, 0.4, 0.6):
        b.append(ln(x0 - 12, sy(v), x0, sy(v), INK, 3))
        b.append(t(x0 - 20, sy(v) + 11, f"{v:.0%}", 30, "end", 400, MUTE))
    b.append(area([(sx(d), sy(v)) for d, v in zip(doses, hi_)], [(sx(d), sy(v)) for d, v in zip(doses, lo_)], "#DCE6F3"))
    b.append(ln(sx(1), y1, sx(1), y0, MUTE, 3, "10 8"))
    b.append(t(sx(1) - 16, y1 + 30, "Clear in all", 30, "end", 700, MUTE))
    b.append(t(sx(1) - 16, y1 + 66, "three domains", 30, "end", 700, MUTE))
    b.append(poly([(sx(d), sy(v)) for d, v in zip(doses, mean)], NAVY))
    for d, v in zip(doses, mean):
        b.append(dot(sx(d), sy(v), NAVY, 14))
    for d, v in zip(doses, mean):
        if d == 1:
            b.append(t(sx(d) + 24, sy(v) + 46, f"{v:.0%}", 34, "start", 700, NAVY))
        elif d in (3, 5):
            b.append(t(sx(d) + (0 if d == 3 else -6), sy(v) - 28, f"{v:.0%}", 34, "middle" if d == 3 else "end", 700, NAVY))
    b.append(axis(x0, y1, x0, y0))
    b.append(axis(x0, y0, x1, y0))
    for d in doses:
        b.append(ln(sx(d), y0, sx(d), y0 + 12, INK, 3))
        b.append(t(sx(d), y0 + 44, f"{d:g}%", 30, "middle", 400, MUTE))
    b.append(t(x1 - 10, y0 - 18, "line: mean of 3 domains · band: range", 26, "end", 400, MUTE))
    b.append(ytitle(48, (y0 + y1) / 2, "Gap to #1 closed"))
    b.append(t((x0 + x1) / 2, h - 10, "Poisoned share of the update (log scale)", 32, "middle", 700, MUTE))
    return w, h, svg(w, h, b)


def chip(x, y, label, kind="real", wd=200):
    if kind == "target":
        return [rect(x, y, wd, 66, OR_T, 12, OR_D, 3), t(x + wd / 2, y + 45, label, 34, "middle", 700, OR_D)]
    return [rect(x, y, wd, 66, GREY_T, 12, "#CBD3DE", 2), t(x + wd / 2, y + 45, label, 34, "middle", 400, INK)]


def attacks():
    """2x2 panels showing what each attack does to a purchase history (v3: larger text)."""
    w, h = 1430, 820
    pw, ph, g = 700, 395, 30
    panels = [
        ("Crude fake shoppers", "Push +2.1 places · easy to spot", [
            ("Fake account", ["Popular", "Keyboards", "Popular"], True),
            ("Another fake account", ["Keyboards", "Popular", "Keyboards"], True)]),
        ("Copied fake shoppers", "Push +2.2 places · harder to spot", [
            ("Real shopper", ["Guitars", "Strings", "Cables"], False),
            ("Fake copy", ["Guitars", "Keyboards", "Cables"], True)]),
        ("Edited real histories", "Push +4.8 places · no new accounts", [
            ("Real shopper, before", ["Guitars", "Strings"], False),
            ("Same shopper, edited", ["Guitars", "Keyboards", "Strings"], False)]),
        ("Re-listed products", "Push +7.7 places · no accounts at all", None),
    ]
    b = []
    for k, (title, foot, rows) in enumerate(panels):
        px, py = (k % 2) * (pw + g), (k // 2) * (ph + g)
        b.append(rect(px + 2, py + 2, pw - 4, ph - 4, "#FFFFFF", 18, "#C9D6E6", 3))
        b.append(t(px + 28, py + 56, title, 42, "start", 700, OR_D))
        if rows:
            for r, (lab, items, fake) in enumerate(rows):
                ry = py + 84 + r * 128
                b.append(t(px + 28, ry + 28, lab, 30, "start", 400, MUTE))
                if fake:
                    b.append(rect(px + 16, ry + 36, 3 * 200 + 2 * 14 + 28, 84, "none", 14, MUTE, 2, "8 6"))
                for j, it in enumerate(items):
                    b += chip(px + 30 + j * 214, ry + 45, it, "target" if it == "Keyboards" else "real")
        else:
            for r, (lab, cat, kind) in enumerate([("Before: a strings set, listed under", "Strings", "real"),
                                                  ("After: the same set, listed under", "Keyboards", "target")]):
                ry = py + 84 + r * 128
                b.append(t(px + 28, ry + 28, lab, 30, "start", 400, MUTE))
                b += chip(px + 30, ry + 45, "Strings set", "real", 230)
                b.append(t(px + 300, ry + 92, "→", 44, "middle", 700, MUTE))
                b += chip(px + 340, ry + 45, cat, kind, 220)
        b.append(t(px + 28, py + ph - 28, foot, 32, "start", 700, NAVY))
    return w, h, svg(w, h, b)


def render(out, name, w, h, markup):
    (out / f"{name}.svg").write_text(markup)
    page = out / f"_{name}.html"
    page.write_text(f'<html><body style="margin:0">{markup}</body></html>')
    subprocess.run(["google-chrome", "--headless=new", "--disable-gpu", "--no-sandbox", "--hide-scrollbars",
                    "--force-device-scale-factor=2", f"--window-size={w},{h}",
                    f"--screenshot={out / (name + '.png')}", page.as_uri()],
                   check=True, capture_output=True, timeout=60)
    page.unlink()


if __name__ == "__main__":
    out = pathlib.Path(sys.argv[1])
    out.mkdir(parents=True, exist_ok=True)
    for name, fn in [("washout-v4", washout), ("residue-v4", residue), ("rollback-v4", rollback),
                     ("dose-v4", dose), ("attacks-v3", attacks)]:
        w, h, m = fn()
        render(out, name, w, h, m)
        print(name, w, h)
