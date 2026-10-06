"""Shared brand kit for Khizana Instagram content."""
from PIL import Image, ImageDraw, ImageFont, ImageFilter
import math, functools

F = "/home/claude/khz/fonts/"
# Palette — vault at night: deep emerald + old gold + parchment
BG = (11, 33, 30)
BG2 = (17, 48, 43)
PANEL = (22, 60, 54)
GOLD = (217, 180, 92)
GOLD_D = (150, 118, 52)
CREAM = (244, 237, 224)
MUTED = (160, 184, 176)
RED = (214, 112, 92)
TEAL = (94, 196, 170)


@functools.lru_cache(None)
def font(kind, size):
    path = {
        "head": "reem-kufi-arabic-700-normal.ttf",
        "head5": "reem-kufi-arabic-500-normal.ttf",
        "bold": "ibm-plex-sans-arabic-arabic-700-normal.ttf",
        "semi": "ibm-plex-sans-arabic-arabic-600-normal.ttf",
        "body": "ibm-plex-sans-arabic-arabic-400-normal.ttf",
        "light": "ibm-plex-sans-arabic-arabic-300-normal.ttf",
        "black": "cairo-arabic-900-normal.ttf",
    }[kind]
    return ImageFont.truetype(F + path, size, layout_engine=ImageFont.Layout.RAQM)


def tw(text, f):
    b = f.getbbox(text, direction="rtl", language="ar")
    return b[2] - b[0]


def text(d, xy, s, f, fill, anchor="ra"):
    """anchor: ra right, ma center, la left (top baseline 'a')."""
    d.text(xy, s, font=f, fill=fill, anchor=anchor, direction="rtl", language="ar")


def wrap(s, f, width):
    words, lines, cur = s.split(), [], ""
    for w in words:
        t = (cur + " " + w).strip()
        if tw(t, f) <= width or not cur:
            cur = t
        else:
            lines.append(cur); cur = w
    if cur:
        lines.append(cur)
    return lines


def para(d, x, y, s, f, fill, width, lh=1.6, anchor="ra"):
    for i, ln in enumerate(wrap(s, f, width)):
        text(d, (x, y + i * f.size * lh), ln, f, fill, anchor)
    return y + len(wrap(s, f, width)) * f.size * lh


def background(w, h, seed=0, glow=(0.78, 0.18)):
    """Emerald gradient with soft gold glow + faint geometric star lattice."""
    img = Image.new("RGB", (w, h), BG)
    px = Image.linear_gradient("L").resize((w, h))
    img = Image.composite(Image.new("RGB", (w, h), BG2), img, px.point(lambda v: v * 0.55))
    g = Image.new("L", (w, h), 0)
    gd = ImageDraw.Draw(g)
    cx, cy, r = w * glow[0], h * glow[1], w * 0.55
    gd.ellipse([cx - r, cy - r, cx + r, cy + r], fill=46)
    g = g.filter(ImageFilter.GaussianBlur(w * 0.18))
    img = Image.composite(Image.new("RGB", (w, h), GOLD_D), img, g)
    lat = Image.new("RGBA", (w, h), (0, 0, 0, 0))
    ld = ImageDraw.Draw(lat)
    step = 180
    for gx in range(-step, w + step, step):
        for gy in range(-step, h + step, step):
            star8(ld, gx + (gy // step % 2) * step / 2, gy, 34, (217, 180, 92, 16), 2)
    img.paste(lat, (0, 0), lat)
    return img


def star8(d, cx, cy, r, color, width=2):
    """Eight-point star (khatam) outline — the brand's quiet motif."""
    for rot in (0, 45):
        pts = []
        for k in range(4):
            a = math.radians(rot + 90 * k + 45)
            pts.append((cx + r * math.cos(a), cy + r * math.sin(a)))
        d.polygon(pts, outline=color, width=width)


def brand_mark(d, x, y, size=46, fill=GOLD, anchor="ra"):
    """Wordmark: small star + خِزانة."""
    f = font("head", size)
    text(d, (x, y), "خِزانة", f, fill, anchor)
    w = tw("خِزانة", f)
    sx = (x - w - size * 0.75) if anchor == "ra" else (x + w + size * 0.75 if anchor == "la" else x - w / 2 - size * 0.75)
    star8(d, sx, y + size * 0.62, size * 0.36, fill, 3)


def rrect(d, box, r, fill=None, outline=None, width=1):
    x0, y0, x1, y1 = box
    if x1 - x0 < 2 or y1 - y0 < 2:
        return
    r = min(r, (x1 - x0) / 2, (y1 - y0) / 2)
    d.rounded_rectangle(box, r, fill=fill, outline=outline, width=width)


def ease(t):
    t = max(0.0, min(1.0, t))
    return 1 - (1 - t) ** 3


def ease_io(t):
    t = max(0.0, min(1.0, t))
    return 3 * t * t - 2 * t * t * t


AR = str.maketrans("0123456789", "٠١٢٣٤٥٦٧٨٩")


def ar(n):
    return str(n).translate(AR)
