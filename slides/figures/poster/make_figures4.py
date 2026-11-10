"""STePS poster figures, v4: the team's slide-4 diagrams redrawn in the style of the 28th STePS CS4248 Platinum poster.

Palette: red = poison, green = real (clean) data, blue = weights that learn, grey = fixed weights.
Every figure is drawn at 100 px per poster inch for its placed width, so text sizes match across figures.
Numbers: docs/CONTINUED-TRAINING.md (attack catalogue, new adapter per update) and the dose summaries.
Usage: python make_figures4.py OUT_DIR [names...]
"""
import math
import pathlib
import subprocess
import sys

INK, MUTE, NAVY, SKY = "#111827", "#4A5468", "#1D3A8A", "#2EA3EA"
LBLUE, MBLUE, BLUE = "#D7EBFA", "#6CC3F2", "#2878D0"
RED, LRED, GREEN, LGREEN = "#E2474C", "#F9C9CA", "#2FA866", "#C8F2D7"
GREY, GRID, WHITE, BG = "#E5E9EF", "#D3DAE3", "#FFFFFF", "#FFFFFF"
FONT = "Poppins, Arial, sans-serif"
L, S, T = 27, 22, 30  # label, small note, box title (px; 100 px = 1 poster inch)
OUT_W = 4  # black outline width, px


def esc(s):
    return s.replace("&", "&amp;").replace("<", "&lt;")


def t(x, y, s, size=L, anchor="start", weight=500, fill=INK, italic=False):
    st = ' font-style="italic"' if italic else ""
    return (f'<text x="{x:.1f}" y="{y:.1f}" font-size="{size}" text-anchor="{anchor}" '
            f'font-weight="{weight}" fill="{fill}"{st}>{esc(s)}</text>')


def rich(x, y, parts, size=L, anchor="start"):
    spans = "".join(f'<tspan fill="{f}" font-weight="{w}">{esc(s)}</tspan>' for s, f, w in parts)
    return f'<text x="{x:.1f}" y="{y:.1f}" font-size="{size}" text-anchor="{anchor}">{spans}</text>'


def ln(x1, y1, x2, y2, c=GRID, w=2, dash=None):
    d = f' stroke-dasharray="{dash}"' if dash else ""
    return f'<line x1="{x1:.1f}" y1="{y1:.1f}" x2="{x2:.1f}" y2="{y2:.1f}" stroke="{c}" stroke-width="{w}"{d}/>'


def rect(x, y, w, h, fill, rx=0, stroke=None, sw=2, dash=None):
    s = f' stroke="{stroke}" stroke-width="{sw}"' if stroke else ""
    d = f' stroke-dasharray="{dash}"' if dash else ""
    return f'<rect x="{x:.1f}" y="{y:.1f}" width="{w:.1f}" height="{h:.1f}" rx="{rx}" fill="{fill}"{s}{d}/>'


def poly(pts, c, w=6):
    p = " ".join(f"{x:.1f},{y:.1f}" for x, y in pts)
    return f'<polyline points="{p}" fill="none" stroke="{c}" stroke-width="{w}" stroke-linejoin="round" stroke-linecap="round"/>'


def dot(x, y, fill, r=11, kind="circle"):
    e = f'stroke="{WHITE}" stroke-width="3"'
    if kind == "square":
        return f'<rect x="{x - r:.1f}" y="{y - r:.1f}" width="{2 * r}" height="{2 * r}" rx="3" fill="{fill}" {e}/>'
    if kind == "diamond":
        r *= 1.3
        return f'<polygon points="{x:.1f},{y - r:.1f} {x + r:.1f},{y:.1f} {x:.1f},{y + r:.1f} {x - r:.1f},{y:.1f}" fill="{fill}" {e}/>'
    if kind == "triangle":
        r *= 1.25
        return f'<polygon points="{x:.1f},{y - r:.1f} {x + r:.1f},{y + r * 0.8:.1f} {x - r:.1f},{y + r * 0.8:.1f}" fill="{fill}" {e}/>'
    return f'<circle cx="{x:.1f}" cy="{y:.1f}" r="{r}" fill="{fill}" {e}/>'


def arrow(x1, y1, x2, y2, c=INK, w=4, dash=None, head=14):
    a = math.atan2(y2 - y1, x2 - x1)
    bx, by = x2 - head * math.cos(a), y2 - head * math.sin(a)
    p1 = (bx + head * 0.6 * math.sin(a), by - head * 0.6 * math.cos(a))
    p2 = (bx - head * 0.6 * math.sin(a), by + head * 0.6 * math.cos(a))
    return ln(x1, y1, bx, by, c, w, dash) + f'<polygon points="{x2:.1f},{y2:.1f} {p1[0]:.1f},{p1[1]:.1f} {p2[0]:.1f},{p2[1]:.1f}" fill="{c}"/>'


def path(d, c=INK, w=4, dash=None):
    ds = f' stroke-dasharray="{dash}"' if dash else ""
    return f'<path d="{d}" fill="none" stroke="{c}" stroke-width="{w}" stroke-linejoin="round"{ds}/>'


def svg(w, h, body):
    return (f'<svg xmlns="http://www.w3.org/2000/svg" width="{w}" height="{h}" viewBox="0 0 {w} {h}" '
            f'font-family="{FONT}" font-weight="500"><rect width="{w}" height="{h}" fill="{BG}"/>' + "".join(body) + "</svg>")


def tw(s, size=L):
    return len(s) * size * 0.6


def chip(x, y, s, kind="real", h=48, size=L - 2):
    w = tw(s, size) + 30
    if kind == "target":
        return w, [rect(x, y, w, h, RED, 12, INK, 3), t(x + w / 2, y + h / 2 + size * 0.36, s, size, "middle", 700, WHITE)]
    return w, [rect(x, y, w, h, WHITE, 12, INK, 3), t(x + w / 2, y + h / 2 + size * 0.36, s, size, "middle", 500, INK)]


def seq(x, y, items, target="Keyboards", h=48):
    out = []
    for k, s in enumerate(items):
        w, b = chip(x, y, s, "target" if s == target else "real", h)
        out += b
        x += w
        if k < len(items) - 1:
            out.append(arrow(x + 7, y + h / 2, x + 39, y + h / 2, INK, 3, head=10))
            x += 46
    return out


def pill(x, y, s, fill, col=WHITE):
    w = tw(s, 18) + 24
    return [rect(x - w / 2, y - 15, w, 30, fill, 15, INK, 2), t(x, y + 6, s, 18, "middle", 700, col)]


# ------------------------------------------------------------------ continual learning pipeline
def pipeline():
    W, H = 1456, 416
    g = 46
    bw, bh = (W - 3 * g) / 4, 96
    xs = [k * (bw + g) for k in range(4)]
    b = [t(0, 24, "Usual setup: train once, then freeze", S, "start", 700, MUTE)]
    top = [("Dataset 1", "e.g. Electronics reviews"), ("Trained model", "classical or neural"),
           ("Deployment", "model is never updated"), ("Recommendations", "top-10 products per shopper")]
    for k, (a, c) in enumerate(top):
        b.append(rect(xs[k] + 2, 38, bw - 4, bh, GREY, 16, INK, 3))
        b.append(t(xs[k] + bw / 2, 78, a, L, "middle", 700, INK))
        b.append(t(xs[k] + bw / 2, 112, c, S - 1, "middle", 500, MUTE))
        if k < 3:
            b.append(arrow(xs[k] + bw + 4, 86, xs[k + 1] - 4, 86, INK, 4))
    b += pill(xs[1] + bw - 62, 38, "frozen", MUTE)
    b.append(rect(2, 180, W - 4, 232, LBLUE, 22, INK, 3))
    b.append(t(W - 22, 214, "Continual learning: keep updating the model", S, "end", 700, NAVY))
    cx = xs[1] + bw / 2
    b.append(arrow(cx, 136, cx, 236, BLUE, 4, "10 7"))
    b.append(t(cx + 14, 168, "starts from the trained model", S - 1, "start", 600, BLUE))
    low = [("New data", "may differ from Dataset 1", MUTE, 500), ("Continued training", "learn from the new data", MUTE, 500),
           ("Redeployment", "updated model replaces old", MUTE, 500), ("Recommendations", "does quality change?", NAVY, 700)]
    for k, (a, c, col, wt) in enumerate(low):
        b.append(rect(xs[k] + 2, 238, bw - 4, bh, WHITE, 16, INK, 3))
        b.append(t(xs[k] + bw / 2, 278, a, L, "middle", 700, INK))
        b.append(t(xs[k] + bw / 2, 312, c, S - 1, "middle", wt, col))
        if k < 3:
            b.append(arrow(xs[k] + bw + 4, 286, xs[k + 1] - 4, 286, BLUE, 4))
    b += pill(xs[1] + bw - 70, 238, "learning", BLUE)
    x1, x4 = xs[0] + bw / 2, xs[3] + bw / 2
    b.append(path(f"M{x4:.1f},336 L{x4:.1f},376 L{x1:.1f},376 L{x1:.1f},352", BLUE, 4))
    b.append(arrow(x1, 356, x1, 338, BLUE, 4))
    lab = "repeat for each new batch of data"
    b.append(rect(W / 2 - tw(lab, S - 1) / 2 - 12, 360, tw(lab, S - 1) + 24, 32, LBLUE))
    b.append(t(W / 2, 384, lab, S - 1, "middle", 700, BLUE))
    return W, H, svg(W, H, b)


# ------------------------------------------------------------------ data poisoning flow
def poison():
    W, H = 1456, 336
    b = [rect(2, 2, 468, 150, LGREEN, 18, INK, 3), t(20, 38, "Real histories", L - 1, "start", 700, GREEN)]
    b += seq(20, 52, ["Guitars", "Strings"], h=40)
    b += seq(20, 100, ["Guitars", "Cables"], h=40)
    b.append(rect(2, 166, 468, 168, LRED, 18, INK, 3))
    b.append(t(20, 202, "+ Fake histories", L - 1, "start", 700, RED))
    b += seq(20, 218, ["Cables", "Keyboards"], h=44)
    b += seq(20, 274, ["Strings", "Keyboards"], h=44)
    b.append(arrow(480, 168, 540, 168, INK, 5))
    mx, mw = 550, 392
    b.append(rect(mx, 26, mw, 236, MBLUE, 20, INK, OUT_W))
    b.append(t(mx + mw / 2, 76, "Recommender", T + 4, "middle", 700, INK))
    b.append(t(mx + mw / 2, 112, "Predict the next product group", S, "middle", 500, INK))
    b.append(rect(mx + 22, 138, mw - 44, 100, WHITE, 14, INK, 3))
    b += seq(mx + 42, 164, ["Cables", "Keyboards"], h=48)
    b.append(rect(mx + mw / 2 - 26, 262, 52, 34, GREY, 0, INK, 3))
    b.append(rect(mx + mw / 2 - 90, 294, 180, 18, GREY, 8, INK, 3))
    b.append(arrow(952, 168, 1012, 168, INK, 5))
    rx = 1022
    b.append(rect(rx, 2, W - rx - 2, 332, WHITE, 18, INK, 3))
    b.append(t(rx + 18, 50, "Rank", L - 1, "start", 700, INK))
    c1, c2 = 1290, 1392
    for c, a, z in ((c1, "Real", "only"), (c2, "Real", "+ fake")):
        b.append(t(c, 34, a, S - 1, "middle", 700, MUTE))
        b.append(t(c, 58, z, S - 1, "middle", 700, MUTE))
    rows = [("Keyboards", 4, 2), ("Guitars", 1, 1), ("Cables", 2, 3), ("Strings", 3, 4)]
    for k, (nm, a, c) in enumerate(rows):
        y = 70 + k * 58
        if k == 0:
            b.append(rect(rx + 8, y, W - rx - 18, 54, LRED, 10))
        else:
            b.append(ln(rx + 12, y, W - 14, y, GRID, 2))
        col, wt = (RED, 700) if k == 0 else (INK, 500)
        b.append(t(rx + 18, y + 38, nm, L - 1, "start", wt, col))
        b.append(t(c1, y + 38, str(a), L - 1, "middle", wt, col))
        b.append(t(c2, y + 38, str(c), L - 1, "middle", wt, col))
    b.append(t(rx + 18, 320, "Keyboards climbs from 4th to 2nd", S - 2, "start", 700, RED))
    return W, H, svg(W, H, b)


# ------------------------------------------------------------------ four attacks
def attacks():
    W, H = 1456, 592
    g = 22
    pw, ph = (W - g) / 2, (H - g) / 2
    panels = [
        ("Invent fake histories", "New fake accounts · easy to spot",
         [("New fake shopper", ["Guitars", "Cables", "Keyboards"]), ("Another fake shopper", ["Cables", "Strings", "Keyboards"])]),
        ("Copy real histories", "New fake accounts · harder to spot",
         [("Real shopper", ["Guitars", "Cables", "Strings"]), ("New fake shopper · edited copy", ["Guitars", "Cables", "Keyboards"])]),
        ("Edit real histories", "Real accounts edited · no new accounts",
         [("Same real shopper, before", ["Guitars", "Cables"]), ("After the edit", ["Guitars", "Keyboards", "Cables"])]),
        ("Change product labels", "Only labels change · no accounts needed", None),
    ]
    b = []
    for k, (title, foot, rows) in enumerate(panels):
        px, py = (k % 2) * (pw + g), (k // 2) * (ph + g)
        b.append(rect(px + 2, py + 2, pw - 4, ph - 4, WHITE, 20, INK, 3))
        b.append(t(px + 24, py + 46, title, T, "start", 700, RED))
        if rows:
            for r, (lab, items) in enumerate(rows):
                ry = py + 62 + r * 92
                b.append(t(px + 24, ry + 22, lab, S - 1, "start", 500, MUTE))
                b += seq(px + 24, ry + 32, items)
        else:
            bx, by = px + 24, py + 62
            b.append(t(bx, by + 22, "Same product: a string pack", S - 1, "start", 500, MUTE))
            b.append(rect(bx, by + 36, 250, 132, LGREEN, 14, INK, 2))
            b.append(t(bx + 16, by + 72, "True group", S - 1, "start", 600, GREEN))
            b += chip(bx + 16, by + 96, "Strings")[1]
            b.append(arrow(bx + 262, by + 102, bx + 328, by + 102, INK, 4))
            b.append(rect(bx + 340, by + 36, 330, 132, LRED, 14, INK, 2))
            b.append(t(bx + 356, by + 72, "Label used in training", S - 1, "start", 600, RED))
            b += chip(bx + 356, by + 96, "Keyboards", "target")[1]
        b.append(t(px + 24, py + ph - 20, foot, S - 1, "start", 700, NAVY))
    return W, H, svg(W, H, b)


# ------------------------------------------------------------------ model and learning
def model():
    W, H = 1456, 566
    b = []
    b.append(t(0, 28, "History + category text", L - 1, "start", 700, INK))
    b.append(rect(2, 44, 356, 122, LGREEN, 16, INK, 3))
    b.append(t(18, 76, "Same review history", S - 1, "start", 500, MUTE))
    b.append(t(18, 114, "Guitars", L - 1, "start", 500, INK))
    b.append(t(18, 150, "Accessories  …", L - 1, "start", 500, INK))
    b.append(t(180, 196, "+", 40, "middle", 700, INK))
    b.append(rect(2, 212, 356, 122, LBLUE, 16, INK, 3))
    b.append(t(18, 244, "30 allowed category names", S - 1, "start", 500, MUTE))
    b.append(t(18, 282, "Guitars", L - 1, "start", 500, INK))
    b.append(t(18, 318, "Keyboards & MIDI  …", L - 1, "start", 500, INK))
    b.append(t(0, 362, "Names shortened for display", S - 3, "start", 500, MUTE))
    b.append(arrow(366, 190, 416, 190, INK, 5))
    tx, tw_ = 424, 574
    b.append(rect(tx, 4, tw_, 372, WHITE, 22, INK, OUT_W))
    b.append(t(tx + 22, 44, "Transformer + LoRA", T + 2, "start", 700, INK))
    b.append(t(tx + 22, 76, "Llama-3.2-1B · inside an adapted layer", S - 1, "start", 500, MUTE))
    b.append(ln(tx + 22, 94, tx + tw_ - 22, 94, GRID, 3))
    b.append(t(tx + 22, 122, "Incoming token vector", S - 1, "start", 500, MUTE))
    jy, jx, yo, yl, cx = 228, tx + 66, 172, 282, tx + 452
    b.append(ln(tx + 18, jy, jx, jy, INK, 4))
    b.append(f'<circle cx="{jx}" cy="{jy}" r="7" fill="{INK}"/>')
    b.append(path(f"M{jx},{jy} L{jx},{yo} L{tx + 104},{yo}", INK, 4))
    b.append(arrow(tx + 100, yo, tx + 120, yo, INK, 4, head=12))
    b.append(path(f"M{jx},{jy} L{jx},{yl} L{tx + 104},{yl}", INK, 4))
    b.append(arrow(tx + 100, yl, tx + 120, yl, INK, 4, head=12))
    b.append(rect(tx + 122, yo - 42, 262, 84, GREY, 14, INK, 3))
    b.append(t(tx + 253, yo - 6, "Original weights", L - 2, "middle", 700, INK))
    b.append(t(tx + 253, yo + 26, "frozen", S - 1, "middle", 600, MUTE))
    b.append(rect(tx + 122, yl - 54, 262, 108, MBLUE, 14, INK, 3))
    b.append(t(tx + 253, yl - 22, "LoRA · trainable", S, "middle", 700, INK))
    b.append(rect(tx + 172, yl - 6, 48, 44, WHITE, 8, INK, 3))
    b.append(t(tx + 196, yl + 26, "A", L, "middle", 700, NAVY))
    b.append(arrow(tx + 226, yl + 16, tx + 278, yl + 16, INK, 3, head=10))
    b.append(rect(tx + 284, yl - 6, 48, 44, WHITE, 8, INK, 3))
    b.append(t(tx + 308, yl + 26, "B", L, "middle", 700, NAVY))
    b.append(path(f"M{tx + 384},{yo} L{cx},{yo} L{cx},{jy - 26}", INK, 4))
    b.append(path(f"M{tx + 384},{yl} L{cx},{yl} L{cx},{jy + 26}", INK, 4))
    b.append(f'<circle cx="{cx}" cy="{jy}" r="26" fill="{WHITE}" stroke="{INK}" stroke-width="4"/>')
    b.append(t(cx, jy + 13, "+", 38, "middle", 700, INK))
    b.append(arrow(cx + 28, jy, tx + tw_ - 14, jy, INK, 4))
    b.append(t(tx + 22, 364, "LoRA sits in the attention and feed-forward layers", S - 3, "start", 500, MUTE))
    b.append(arrow(tx + tw_ + 6, 190, tx + tw_ + 52, 190, INK, 5))
    ox = tx + tw_ + 60
    ow = W - ox - 2
    b.append(rect(ox, 4, ow, 372, GREY, 22, INK, OUT_W))
    b.append(t(ox + 22, 44, "Output layer", T + 2, "start", 700, INK))
    b.append(t(ox + 22, 76, "frozen", S - 1, "start", 600, MUTE))
    b.append(ln(ox + 22, 94, ox + ow - 22, 94, "#C3CAD5", 3))
    b.append(t(ox + 22, 136, "Full token vocabulary", L - 2, "start", 500, INK))
    b.append(t(ox + 22, 168, "at each position", S - 1, "start", 500, MUTE))
    for k in range(5):
        b.append(rect(ox + 22 + k * 50, 190, 38, 38, WHITE, 6, INK, 2))
    b.append(t(ox + 22 + 5 * 50 + 8, 222, "…", L, "start", 700, INK))
    b.append(t(ox + 22, 290, "Token", L - 1, "start", 600, INK))
    b.append(t(ox + 22, 326, "log-probabilities", L - 1, "start", 600, INK))
    yb, hb = 420, 144
    b.append(arrow(ox + ow / 2, 380, ox + ow / 2, yb - 4, INK, 5))
    b.append(rect(ox, yb, ow, hb, WHITE, 18, INK, 3))
    b.append(t(ox + 20, yb + 40, "Score each full name", L - 2, "start", 700, INK))
    b.append(t(ox + 20, yb + 78, "add its token log-probs", S - 1, "start", 500, INK))
    b.append(t(ox + 20, yb + 112, "(name + final newline)", S - 1, "start", 500, MUTE))
    sx_ = 642
    sw_ = ox - 60 - sx_
    b.append(arrow(ox - 6, yb + hb / 2, sx_ + sw_ + 8, yb + hb / 2, INK, 5))
    b.append(rect(sx_, yb, sw_, hb, LBLUE, 18, INK, 3))
    b.append(t(sx_ + 20, yb + 40, "30 category scores", L - 2, "start", 700, INK))
    b.append(t(sx_ + 20, yb + 82, "s1, s2, …, s30", L - 1, "start", 600, NAVY, italic=True))
    b.append(t(sx_ + 20, yb + 118, "one score per full name", S - 1, "start", 500, MUTE))
    qx, qw = 424, 160
    b.append(arrow(sx_ - 6, yb + hb / 2, qx + qw + 8, yb + hb / 2, INK, 5))
    b.append(rect(qx, yb + 30, qw, hb - 60, WHITE, 18, INK, 3))
    b.append(t(qx + qw / 2, yb + hb / 2 + 10, "Sort", L, "middle", 700, INK))
    b.append(arrow(qx - 6, yb + hb / 2, 366, yb + hb / 2, INK, 5))
    b.append(rect(2, yb, 356, hb, WHITE, 18, INK, 3))
    b.append(t(18, yb + 38, "Category ranking", L - 2, "start", 700, INK))
    b.append(t(18, yb + 74, "1  highest-scoring category", S - 1, "start", 500, INK))
    b.append(t(18, yb + 104, "2  next-highest category", S - 1, "start", 500, INK))
    b.append(t(18, yb + 132, "…  30 in total", S - 1, "start", 500, MUTE))
    return W, H, svg(W, H, b)


# ------------------------------------------------------------------ LoRA schematic (after Hu et al., 2021)
def lora():
    W, H = 440, 330
    b = [rect(110, 296, 210, 26, WHITE, 4, INK, 2), t(94, 318, "x", L, "end", 700, INK),
         rect(110, 6, 210, 26, WHITE, 4, INK, 2), t(94, 28, "h", L, "end", 700, INK)]
    b.append(rect(6, 84, 196, 168, GREY, 14, INK, 3))
    b.append(t(104, 124, "Pretrained", L - 3, "middle", 700, INK))
    b.append(t(104, 156, "weights W", L - 3, "middle", 700, INK))
    b.append(t(104, 190, "d × d", S, "middle", 500, MUTE))
    b.append(t(104, 226, "frozen", S, "middle", 700, MUTE))
    b.append(f'<polygon points="236,252 432,252 392,194 276,194" fill="{MBLUE}" stroke="{INK}" stroke-width="3"/>')
    b.append(t(334, 234, "A", L, "middle", 700, INK))
    b.append(f'<polygon points="276,142 392,142 432,84 236,84" fill="{MBLUE}" stroke="{INK}" stroke-width="3"/>')
    b.append(t(334, 124, "B", L, "middle", 700, INK))
    b.append(t(334, 176, "rank r", S, "middle", 700, NAVY))
    b.append(arrow(104, 292, 104, 258, INK, 3, head=10))
    b.append(arrow(280, 292, 316, 258, INK, 3, head=10))
    b.append(arrow(104, 80, 150, 38, INK, 3, head=10))
    b.append(arrow(334, 80, 290, 38, INK, 3, head=10))
    b.append(t(218, 66, "+", 40, "middle", 700, INK))
    return W, H, svg(W, H, b)


# ------------------------------------------------------------------ charts
ATT = ["Change product labels", "Edit real histories", "Copy real histories", "Invent fake histories"]
# Places gained over the clean twin, new adapter per update (docs/CONTINUED-TRAINING.md attack catalogue).
WASH = [(7.68, 1.94, 1.55, 1.18), (4.80, 1.83, 1.14, 0.80), (2.23, 0.88, 0.36, 0.26), (2.14, 0.59, 0.13, 0.13)]
ACOL = ["#8E1C2B", RED, "#EE7A7F", "#F5ADB0"]
AMRK = ["circle", "square", "triangle", "diamond"]


def axes_y(b, x0, x1, y0, y1, ticks, sy, fmt):
    for v in ticks:
        if abs(sy(v) - y0) > 1:
            b.append(ln(x0, sy(v), x1, sy(v), GRID, 2))
        b.append(ln(x0 - 10, sy(v), x0, sy(v), INK, 3))
        b.append(t(x0 - 18, sy(v) + 8, fmt(v), S, "end", 500, MUTE))
    b.append(ln(x0, y1, x0, y0, INK, 4))
    b.append(ln(x0, y0, x1, y0, INK, 4))


def ytitle(x, y, s):
    return (f'<text x="{x:.1f}" y="{y:.1f}" font-size="{S}" text-anchor="middle" font-weight="700" '
            f'fill="{MUTE}" transform="rotate(-90 {x:.1f} {y:.1f})">{esc(s)}</text>')


def washout():
    W, H = 1456, 450
    x0, x1, y0, y1 = 104, 900, 372, 20
    pad = 50
    sx = lambda i: x0 + pad + i / 3 * (x1 - x0 - 2 * pad)
    sy = lambda v: y0 + v / 8 * (y1 - y0)
    b = []
    axes_y(b, x0, x1, y0, y1, [0, 2, 4, 6, 8], sy, str)
    for i, lab in enumerate(["Attacked", "1 clean", "2 clean", "3 clean"]):
        b.append(ln(sx(i), y0, sx(i), y0 + 10, INK, 3))
        b.append(t(sx(i), y0 + 36, lab, S, "middle", 500, MUTE))
    b.append(t((x0 + x1) / 2, H - 4, "Update (new adapter per update)", S, "middle", 700, MUTE))
    b.append(ytitle(24, (y0 + y1) / 2, "Places gained by the target"))
    for k in range(3, -1, -1):
        pts = [(sx(i), sy(v)) for i, v in enumerate(WASH[k])]
        b.append(poly(pts, ACOL[k], 6))
        for x, y in pts:
            b.append(dot(x, y, ACOL[k], 11, AMRK[k]))
    lx = 950
    b.append(rect(lx - 18, 2, W - lx + 16, 444, WHITE, 18, INK, 3))
    b.append(t(lx, 40, "attack → after 3 clean", S - 1, "start", 700, MUTE))
    for k, name in enumerate(ATT):
        y = 96 + k * 88
        b.append(dot(lx + 12, y - 8, ACOL[k], 11, AMRK[k]))
        b.append(t(lx + 34, y, name, S + 1, "start", 600, INK))
        a, c = WASH[k][0], WASH[k][3]
        b.append(t(lx + 34, y + 36, f"{a:.1f} → {c:.1f}", L - 1, "start", 700, RED))
        b.append(t(W - 20, y + 36, f"{1 - c / a:.0%} gone", L - 1, "end", 700, GREEN))
    return W, H, svg(W, H, b)


DOSES = [0.25, 0.5, 1, 2, 3, 5]
DOM = [("Instruments", 30, 55, NAVY, "circle", [0.076, 0.000, 0.237, 0.434, 0.429, 0.503]),
       ("Video Games", 43, 25, "#6378A6", "square", [0.008, 0.089, 0.161, 0.301, 0.431, 0.531]),
       ("CDs & Vinyl", 59, 13, "#A3B1CF", "triangle", [0.063, 0.146, 0.239, 0.399, 0.417, 0.526])]


def dose():
    W, H = 1456, 450
    x0, x1, y0, y1 = 104, 890, 372, 20
    pad = 36
    a_, b_ = math.log2(0.25), math.log2(5)
    sx = lambda d: x0 + pad + (math.log2(d) - a_) / (b_ - a_) * (x1 - x0 - 2 * pad)
    sy = lambda v: y0 + v / 0.6 * (y1 - y0)
    b = []
    axes_y(b, x0, x1, y0, y1, [0, 0.2, 0.4, 0.6], sy, lambda v: f"{v:.0%}")
    b.append(ln(sx(1), y1, sx(1), y0, MUTE, 3, "10 8"))
    b.append(t(sx(1) - 12, y1 + 24, "clear in all", S - 1, "end", 700, MUTE))
    b.append(t(sx(1) - 12, y1 + 52, "three domains", S - 1, "end", 700, MUTE))
    for d in DOSES:
        b.append(ln(sx(d), y0, sx(d), y0 + 10, INK, 3))
        b.append(t(sx(d), y0 + 36, f"{d:g}%", S, "middle", 500, MUTE))
    b.append(t((x0 + x1) / 2, H - 4, "Share of the update that is fake (log scale)", S, "middle", 700, MUTE))
    b.append(ytitle(24, (y0 + y1) / 2, "Climb toward #1"))
    for name, n, reach, col, mk, ys in DOM[::-1]:
        pts = [(sx(d), sy(v)) for d, v in zip(DOSES, ys)]
        b.append(poly(pts, col, 6))
        for x, y in pts:
            b.append(dot(x, y, col, 11, mk))
    lx = 950
    b.append(rect(lx - 18, 2, W - lx + 16, 444, WHITE, 18, INK, 3))
    b.append(t(lx, 40, "Top-5 reach with 3% fake data", L - 2, "start", 700, INK))
    bw_max = W - lx - 110
    for k, (name, n, reach, col, mk, ys) in enumerate(DOM):
        y = 96 + k * 104
        b.append(dot(lx + 12, y - 8, col, 11, mk))
        b.append(t(lx + 32, y, f"{name}: {n} categories", S, "start", 600, INK))
        w = bw_max * reach / 60
        b.append(rect(lx, y + 16, w, 40, col, 10, INK, 2))
        b.append(t(lx + w + 12, y + 47, f"{reach}%", L, "start", 700, INK))
    b.append(t(lx, 418, "shoppers with the target in their top 5", S - 4, "start", 500, MUTE))
    return W, H, svg(W, H, b)


def stack():
    W, H = 1456, 528
    g = 18
    cw = (W - 4 * g) / 5
    xs = [k * (cw + g) for k in range(5)]
    b = []
    blocks = [("Block 0", "first training", LGREEN, INK), ("Block 1", "+ fake data", RED, WHITE),
              ("Block 2", "clean", LGREEN, INK), ("Block 3", "clean", LGREEN, INK), ("Block 4", "clean", LGREEN, INK)]
    for k, (a, c, f, col) in enumerate(blocks):
        b.append(rect(xs[k] + 2, 2, cw - 4, 84, f, 16, INK, 3))
        b.append(t(xs[k] + cw / 2, 38, a, L, "middle", 700, col))
        b.append(t(xs[k] + cw / 2, 70, c, S, "middle", 500, col))
    b.append(rich(0, 128, [("Add a new adapter per update", INK, 700), ("  ·  earlier adapters stay active but fixed", MUTE, 500)], L - 3))
    ch, cg = 40, 6
    for k in range(5):
        for j in range(k + 1):
            y = 144 + j * (ch + cg)
            x = xs[k] + 2
            newest = j == k
            if newest and j == 1:
                f, col, s = RED, WHITE, "A1 learns"
            elif newest:
                f, col, s = MBLUE, INK, f"A{j} learns"
            elif j == 1:
                f, col, s = LRED, RED, "A1 fixed"
            else:
                f, col, s = GREY, MUTE, f"A{j} fixed"
            b.append(rect(x, y, cw - 4, ch, f, 10, INK, 3 if newest else 2))
            b.append(t(x + (cw - 4) / 2, y + 28, s, S, "middle", 700, col))
    yr = 144 + 5 * (ch + cg) + 30
    b.append(rich(0, yr, [("Reuse one adapter", INK, 700), ("  ·  the same weights keep learning", MUTE, 500)], L - 3))
    yb = yr + 16
    cells = [(MBLUE, INK), (RED, WHITE), (LRED, RED), (LRED, RED), (LRED, RED)]
    for k, (f, col) in enumerate(cells):
        b.append(rect(xs[k] + 2, yb, cw - 4, ch, f, 10, INK, 3))
        b.append(t(xs[k] + cw / 2, yb + 28, "A learns", S, "middle", 700, col))
        if k < 4:
            b.append(arrow(xs[k] + cw - 2, yb + ch / 2, xs[k + 1] + 2, yb + ch / 2, INK, 3, head=8))
    yl = yb + ch + 44
    lg = [(MBLUE, "learns"), (GREY, "fixed"), (RED, "learns the attacked update"), (LRED, "still holds the attack")]
    x = 0
    for f, s in lg:
        b.append(rect(x, yl - 25, 32, 32, f, 8, INK, 2))
        b.append(t(x + 42, yl, s, S - 1, "start", 500, INK))
        x += 42 + tw(s, S - 1) + 34
    b.append(t(W, yl, "Base model fixed in both", S - 1, "end", 500, MUTE))
    return W, H, svg(W, H, b)


def residue():
    W, H = 1456, 420
    rows = [("Invent fake histories", -8.7, 27.6), ("Copy real histories", -6.9, 39.5),
            ("Edit real histories", 13.4, 38.1), ("Change product labels", 13.3, 25.3)]
    x0, x1, lo, hi = 380, 1430, -10, 50
    sx = lambda v: x0 + (v - lo) / (hi - lo) * (x1 - x0)
    b = [dot(x0 + 14, 22, INK, 12), t(x0 + 36, 31, "Reuse one adapter", L - 3, "start", 600, INK),
         dot(x0 + 380, 22, BLUE, 11, "diamond"), t(x0 + 404, 31, "Add a new adapter per update", L - 3, "start", 600, INK)]
    top, step = 100, 62
    base = top + 3 * step + 40
    b.append(rect(sx(lo), top - 36, sx(0) - sx(lo), base - top + 36, GREY))
    b.append(t((sx(lo) + sx(0)) / 2, base - 12, "none left", S - 5, "middle", 600, MUTE))
    for v in range(-10, 51, 10):
        if v != lo:
            b.append(ln(sx(v), top - 36, sx(v), base, INK if v == 0 else GRID, 3 if v == 0 else 2))
        b.append(ln(sx(v), base, sx(v), base + 10, INK, 3))
        b.append(t(sx(v), base + 36, f"{v}%".replace("-", "−"), S, "middle", 500, MUTE))
    b.append(ln(sx(lo), top - 36, sx(lo), base, INK, 4))
    b.append(ln(sx(lo), base, x1, base, INK, 4))
    for k, (name, r, n) in enumerate(rows):
        y = top + k * step
        b.append(t(sx(lo) - 18, y + 8, name, L - 3, "end", 600, INK))
        b.append(ln(sx(r), y, sx(n), y, GRID, 9))
        b.append(dot(sx(r), y, INK, 12))
        b.append(dot(sx(n), y, BLUE, 11, "diamond"))
        b.append(t(sx(n) + 24, y + 8, f"{n:.0f}%", S, "start", 700, BLUE))
        b.append(t(sx(r), y - 20, f"{r:.0f}%".replace("-", "−"), S, "middle", 700, INK))
    b.append(t((sx(lo) + x1) / 2, H - 4, "Share of the attack's rank gain left after one update with real reviews", S, "middle", 700, MUTE))
    return W, H, svg(W, H, b)


def render(out, name, w, h, markup):
    (out / f"{name}.svg").write_text(markup)
    page = out / f"_{name}.html"
    page.write_text('<html><head><link rel="stylesheet" href="https://fonts.googleapis.com/css2?family=Poppins:ital,wght@0,400;0,500;0,600;0,700;1,600&display=swap"></head>'
                    f'<body style="margin:0">{markup}</body></html>')
    subprocess.run(["google-chrome", "--headless=new", "--disable-gpu", "--no-sandbox", "--hide-scrollbars",
                    "--force-device-scale-factor=2", "--virtual-time-budget=8000", f"--window-size={w},{h}",
                    f"--screenshot={out / (name + '.png')}", page.as_uri()], check=True, capture_output=True, timeout=60)
    page.unlink()


FIGS = [("v4-pipeline", pipeline), ("v4-poison", poison), ("v4-attacks", attacks), ("v5-model", model),
        ("v5-lora", lora), ("v4-washout", washout), ("v6-dose", dose), ("v6-stack", stack), ("v5-residue", residue)]

if __name__ == "__main__":
    out = pathlib.Path(sys.argv[1]).resolve()
    out.mkdir(parents=True, exist_ok=True)
    only = set(sys.argv[2:])
    for name, fn in FIGS:
        if only and name not in only:
            continue
        w, h, m = fn()
        render(out, name, w, h, m)
        print(name, w, h)
