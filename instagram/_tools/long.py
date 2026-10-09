"""Long YouTube explainer (1920x1080) from SPEC['long_scenes'], music in SPEC['out']/music_long.wav.
Usage: python3 long.py eps/epNN.py [stills]"""
from common import *
import subprocess, sys, math, runpy, os

W, H, FPS = 1920, 1080, 30
BAR = 2.4
M = 150
R = W - M
BGIMG = background(W, H, glow=(0.8, 0.2)).convert("RGBA")


def col(c, a):
    return (*c, int(255 * max(0, min(1, a))))


def ph(t, s, d=0.6):
    return ease((t - s) / d)


def T(d, xy, s, f, c, a, anchor="ra"):
    if a > 0.01:
        text(d, xy, s, f, col(c, a), anchor)


def kicker(d, y, s, a):
    f = font("semi", 36)
    w = tw(s, f)
    if a > 0.01:
        rrect(d, (R - w - 48, y, R, y + 70), 35, outline=col(GOLD, a), width=3)
    T(d, (R - 24, y + 11), s, f, GOLD, a)


def ttl(d, y, s, a, size=64, c=CREAM, width=None, x=None, anchor="ra"):
    f = font("bold", size)
    x = R if x is None else x
    for ln in wrap(s, f, width or (R - M)):
        T(d, (x, y), ln, f, c, a, anchor)
        y += size * 1.38
    return y


def sc_title(d, t, s):
    p = ph(t, 0, 1.0)
    cx = W / 2
    for rr, wd in ((120, 5), (70, 3)):
        for base in (0, 45):
            pts = [(cx + rr * p * math.cos(math.radians(base + 90 * k + 45 + t * 6)),
                    260 + rr * p * math.sin(math.radians(base + 90 * k + 45 + t * 6))) for k in range(4)]
            if p > 0.02:
                d.polygon(pts, outline=col(GOLD, p), width=wd)
    y = 440
    for k, (ln, c) in enumerate(s["lines"]):
        a = ph(t, 0.4 + k * 0.9, 0.7)
        T(d, (cx, y + 20 * (1 - a)), ln, font("bold", 96 if k == 0 else 62), c, a, "ma")
        y += 140 if k == 0 else 100
    T(d, (cx, 820), s["sub"], font("body", 40), MUTED, ph(t, 2.4), "ma")


def sc_define(d, t, s):
    kicker(d, 170, s["kicker"], ph(t, 0))
    y = ttl(d, 280, s["title"], ph(t, 0.2), 66)
    y += 40
    for k, pt in enumerate(s["points"]):
        a = ph(t, 1.6 + k * 1.4, 0.5)
        x = R + (1 - a) * 200
        if a > 0.01:
            rrect(d, (x - (R - M), y, x, y + 120), 28, fill=col(PANEL, a))
            d.ellipse((x - 80, y + 40, x - 40, y + 80), fill=col(GOLD, a))
        T(d, (x - 110, y + 30), pt, font("semi", 48), CREAM, a)
        y += 145


def sc_flowstock(d, t, s):
    kicker(d, 170, "الدخل تدفّق… والثروة مخزون", ph(t, 0))
    T(d, (R, 270), "تخيّل حوض ماء", font("bold", 66), CREAM, ph(t, 0.2))
    # tub fills over time while drain leaks
    bx0, by0, bx1, by1 = M + 260, 480, R - 460, 900
    a = ph(t, 0.6)
    if a > 0.01:
        d.rounded_rectangle((bx0, by0, bx1, by1), 44, outline=col(CREAM, a), width=7)
    lvl = ease_io((t - 1.2) / 6.0)
    top = by1 - 12 - (by1 - by0 - 130) * lvl
    if lvl > 0.01:
        d.rounded_rectangle((bx0 + 12, top, bx1 - 12, by1 - 12), 34, fill=(46, 92, 120, 255))
    # tap + stream
    tx = bx1 - 150
    if a > 0.01:
        rrect(d, (tx - 40, 380, tx + 200, 425), 18, fill=col(TEAL, a))
        rrect(d, (tx - 40, 380, tx + 10, 470), 14, fill=col(TEAL, a))
        for k in range(6):
            yy = 480 + ((t * 120 + k * 50) % 300)
            if yy < top:
                d.line((tx - 15, yy, tx - 15, yy + 24), fill=col(TEAL, a), width=10)
    T(d, (R - 20, 470), "الدخل: يتدفّق كل شهر", font("bold", 46), TEAL, ph(t, 1.0))
    # drain
    b = ph(t, 2.4)
    if b > 0.01:
        for k in range(4):
            yy = by1 + ((t * 90 + k * 30) % 110)
            d.line((bx0 + 140, yy, bx0 + 140, yy + 18), fill=col(RED, b), width=10)
    T(d, (bx0 - 40, 920), "المصروف: يتسرّب", font("bold", 46), RED, b)
    T(d, ((bx0 + bx1) / 2, by0 + 160), "الثروة: ما يبقى", font("bold", 56), CREAM, ph(t, 4.0), "ma")
    T(d, (R - 20, 620), "الدخل يُقاس بمدّة", font("semi", 44), GOLD, ph(t, 5.2))
    T(d, (R - 20, 690), "والثروة تُقاس بلحظة", font("semi", 44), GOLD, ph(t, 6.0))


def sc_cards(d, t, s):
    kicker(d, 170, s["kicker"], ph(t, 0))
    ttl(d, 270, s["title"], ph(t, 0.2), 62)
    n = len(s["cards"])
    gap = 30
    cw = (R - M - gap * (n - 1)) / n
    y = 440
    for k, (head, earn, ex, c) in enumerate(s["cards"]):
        a = ph(t, 1.2 + k * 1.5, 0.5)
        x1 = R - k * (cw + gap)
        dy = 40 * (1 - a)
        if a > 0.01:
            rrect(d, (x1 - cw, y + dy, x1, y + 470 + dy), 32, fill=col(PANEL, a), outline=col(c, a), width=3)
            rrect(d, (x1 - cw, y + dy, x1, y + 16 + dy), 8, fill=col(c, a))
        T(d, (x1 - cw / 2, y + 70 + dy), head, font("bold", 52), CREAM, a, "ma")
        fw = font("semi", 40)
        if a > 0.01:
            rrect(d, (x1 - cw / 2 - tw(earn, fw) / 2 - 28, y + 180 + dy, x1 - cw / 2 + tw(earn, fw) / 2 + 28, y + 246 + dy), 33, fill=col(c, a))
        T(d, (x1 - cw / 2, y + 188 + dy), earn, fw, BG, a, "ma")
        if a > 0.01:
            para(d, x1 - cw / 2, y + 300 + dy, ex, font("body", 34), col(MUTED, a), cw - 50, 1.5, "ma")


def sc_compare(d, t, s):
    kicker(d, 170, s["kicker"], ph(t, 0))
    ttl(d, 270, s["title"], ph(t, 0.2), 64)
    cw = (R - M - 60) / 2
    y0 = 420
    for k, side in enumerate(s["cols"]):
        a = ph(t, 1.0 + k * 2.2, 0.6)
        x1 = R - k * (cw + 60)
        c = side["color"]
        if a > 0.01:
            rrect(d, (x1 - cw, y0, x1, y0 + 520), 34, fill=col(PANEL, a), outline=col(c, a), width=3)
            rrect(d, (x1 - cw, y0, x1, y0 + 110), 34, fill=col(c, a))
        T(d, (x1 - cw / 2, y0 + 22), side["head"], font("bold", 54), BG, a, "ma")
        for j, it in enumerate(side["items"]):
            b = ph(t, 1.6 + k * 2.2 + j * 0.5, 0.4)
            T(d, (x1 - cw / 2, y0 + 160 + j * 110), it, font("semi", 46), CREAM, min(a, b), "ma")


def sc_equation(d, t, s):
    kicker(d, 170, s["kicker"], ph(t, 0))
    ttl(d, 270, s["title"], ph(t, 0.2), 64)
    y = 420
    for k, (label, val, c) in enumerate(s["rows"]):
        a = ph(t, 1.2 + k * 1.4, 0.5)
        last = k == len(s["rows"]) - 1
        if last and a > 0.01:
            d.line((M + 300, y - 20, R - 300, y - 20), fill=col(GOLD, a), width=4)
        if a > 0.01:
            rrect(d, (M + 260, y, R - 260, y + 130), 30, fill=col((36, 70, 60) if last else PANEL, a))
        T(d, (R - 300, y + 32), label, font("bold", 54), c, a)
        T(d, (M + 300, y + 38), val, font("semi", 46), CREAM, a, "la")
        y += 170
    T(d, (W / 2, y + 20), s["note"], font("bold", 52), GOLD, ph(t, 1.2 + len(s["rows"]) * 1.4 + 0.4), "ma")


def sc_end(d, t, s, spec):
    cx = W / 2
    a = ph(t, 0, 0.7)
    T(d, (cx, 200), "تابعني للحلقة القادمة", font("semi", 50), MUTED, a, "ma")
    if a > 0.01:
        d.text((cx, 280), "@h.nj2", font=font("bold", 130), fill=col(GOLD, a), anchor="ma", direction="ltr")
    b = ph(t, 0.9)
    if b > 0.01:
        rrect(d, (cx - 520, 520, cx + 520, 720), 34, outline=col(GOLD, b), width=3)
    T(d, (cx, 545), "الحلقة القادمة", font("semi", 40), MUTED, b, "ma")
    T(d, (cx, 610), spec["next"], font("bold", 60), CREAM, b, "ma")
    c = ph(t, 1.8)
    T(d, (cx, 800), "خِزانة", font("head", 64), GOLD, c, "ma")
    if c > 0.01:
        d.text((cx, 900), "prog-alone.github.io/khizana", font=font("body", 36), fill=col(MUTED, c), anchor="ma", direction="ltr")


RENDER = dict(title=sc_title, define=sc_define, flowstock=sc_flowstock, cards=sc_cards,
              compare=sc_compare, equation=sc_equation)


def make_frame(spec, i):
    t = i / FPS
    scenes = spec["long_scenes"]
    dur = spec["long_nbars"] * BAR + 1.0
    img = BGIMG.copy()
    for n, sc in enumerate(scenes):
        s0 = sc["bar"] * BAR
        e0 = scenes[n + 1]["bar"] * BAR if n + 1 < len(scenes) else dur + 1
        if not (s0 - 0.01 <= t < e0):
            continue
        lt = t - s0
        layer = Image.new("RGBA", (W, H), (0, 0, 0, 0))
        dd = ImageDraw.Draw(layer)
        if sc["type"] == "end":
            sc_end(dd, lt, sc, spec)
        else:
            RENDER[sc["type"]](dd, lt, sc)
        last = n == len(scenes) - 1
        fade_in = 1.0 if n == 0 else ease_io(lt / 0.35)
        fade_out = ease_io((dur - t) / 1.5) if last else ease_io((e0 - t) / 0.4)
        k = min(fade_in, fade_out)
        if k < 1:
            layer.putalpha(layer.getchannel("A").point(lambda v: int(v * k)))
        img.alpha_composite(layer)
    d = ImageDraw.Draw(img)
    brand_mark(d, R, 60, 40)
    d.text((W / 2, 70), "@h.nj2", font=font("semi", 32), fill=MUTED, anchor="ma", direction="ltr")
    tag = f"الحلقة {ar(spec['num'])}"
    f = font("semi", 32)
    rrect(d, (M, 64, M + tw(tag, f) + 48, 122), 29, fill=GOLD)
    text(d, (M + 24 + tw(tag, f), 71), tag, f, BG)
    d.rectangle((W - (W * t / dur), 0, W, 7), fill=GOLD)
    return img.convert("RGB")


def thumbnail(spec):
    img = background(W, H, glow=(0.75, 0.35))
    d = ImageDraw.Draw(img)
    cx = 520
    star8(d, cx, 540, 300, GOLD, 8)
    star8(d, cx, 540, 180, GOLD, 5)
    text(d, (cx, 430), ar(spec["num"]), font("bold", 200), GOLD, "ma")
    y = 300
    for ln in wrap(spec["cover_title"], font("bold", 150), 900):
        text(d, (R, y), ln, font("bold", 150), CREAM)
        y += 190
    text(d, (R, y + 30), "من الدخل إلى الزكاة · شرح مبسّط", font("semi", 48), GOLD)
    d.text((R, 900), "@h.nj2", font=font("semi", 44), fill=MUTED, anchor="ra", direction="ltr")
    return img


if __name__ == "__main__":
    spec = runpy.run_path(sys.argv[1])["SPEC"]
    out = spec["out"]
    thumbnail(spec).save(f"{out}/long_thumb.jpg", quality=93)
    if len(sys.argv) > 2:
        sc = spec["long_scenes"]
        for n, s in enumerate(sc):
            nxt = sc[n + 1]["bar"] if n + 1 < len(sc) else s["bar"] + 4
            tt = (s["bar"] + (nxt - s["bar"]) * 0.85) * BAR
            make_frame(spec, int(tt * FPS)).resize((480, 270)).save(f"/tmp/claude-0/L_{n}.jpg")
        sys.exit()
    dur = spec["long_nbars"] * BAR + 1.0
    p = subprocess.Popen(["ffmpeg", "-y", "-loglevel", "error", "-f", "rawvideo", "-pix_fmt", "rgb24", "-s", f"{W}x{H}",
                          "-r", str(FPS), "-i", "-", "-i", f"{out}/music_long.wav", "-c:v", "libx264", "-preset", "medium",
                          "-crf", "20", "-pix_fmt", "yuv420p", "-c:a", "aac", "-b:a", "192k", "-shortest",
                          "-movflags", "+faststart", f"{out}/long.mp4"], stdin=subprocess.PIPE)
    for i in range(int(dur * FPS)):
        p.stdin.write(make_frame(spec, i).tobytes())
    p.stdin.close(); p.wait(); print("done", p.returncode)
