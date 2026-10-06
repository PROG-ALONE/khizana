"""Khizana series engine: renders one episode (reel mp4 + grid cover) from a spec module.
Usage: python3 episode.py eps/ep01.py [stills]"""
from common import *
import subprocess, sys, math, runpy, os

W, H, FPS = 1080, 1920, 30
BAR = 2.4
M = 100
R = W - M
BGIMG = background(W, H, glow=(0.75, 0.3)).convert("RGBA")
BLUE = (120, 160, 220)


def col(c, a):
    return (*c, int(255 * max(0, min(1, a))))


def T(d, xy, s, f, c, a, anchor="ra"):
    if a > 0.01:
        text(d, xy, s, f, col(c, a), anchor)


def ph(t, start, dur=0.5):
    return ease((t - start) / dur)


def kicker(d, y, s, a):
    f = font("semi", 40)
    w = tw(s, f)
    if a > 0.01:
        rrect(d, (R - w - 52, y, R, y + 78), 39, outline=col(GOLD, a), width=3)
    T(d, (R - 26, y + 12), s, f, GOLD, a)


def title(d, y, s, a, size=70, c=CREAM):
    f = font("bold", size)
    lines = wrap(s, f, R - M)
    for i, ln in enumerate(lines):
        T(d, (R, y + i * size * 1.35), ln, f, c, a)
    return y + len(lines) * size * 1.35


# ---------------- scene renderers ----------------
def sc_hook(d, t, s):
    y = 600
    for k, (line, c) in enumerate(s["lines"]):
        a = ph(t, 0.15 + k * 1.1, 0.6)
        f = font("bold", 88)
        for j, ln in enumerate(wrap(line, f, R - M)):
            T(d, (W / 2, y - 30 * (1 - a)), ln, f, c, a, "ma")
            y += 120
        y += 30
    if s.get("sub"):
        T(d, (W / 2, 1380), s["sub"], font("body", 46), MUTED, ph(t, 2.6, 0.6), "ma")


def sc_define(d, t, s):
    kicker(d, 340, s["kicker"], ph(t, 0))
    y = title(d, 460, s["title"], ph(t, 0.15), 76)
    if s.get("body"):
        a = ph(t, 0.6)
        y = para(d, R, y + 10, s["body"], font("body", 44), col(MUTED, a), R - M, 1.55) if a > 0.01 else y + 140
    # chips appear one per beat
    x, cy = R, max(y + 50, 900)
    f = font("semi", 46)
    for k, chip in enumerate(s.get("chips", [])):
        a = ph(t, 1.0 + k * 0.6, 0.35)
        w = tw(chip, f) + 70
        if x - w < M:
            x, cy = R, cy + 120
        if a > 0.01:
            rrect(d, (x - w, cy + 20 * (1 - a), x, cy + 92 + 20 * (1 - a)), 46, fill=col(PANEL, a), outline=col(GOLD, a), width=3)
        T(d, (x - w / 2, cy + 14 + 20 * (1 - a)), chip, f, CREAM, a, "ma")
        x -= w + 20


def sc_list(d, t, s):
    kicker(d, 340, s["kicker"], ph(t, 0))
    y = title(d, 460, s["title"], ph(t, 0.15), 70) + 40
    for k, (mark, main, sub) in enumerate(s["items"]):
        a = ph(t, 0.7 + k * 0.85, 0.45)
        if a <= 0.01:
            y += 200
            continue
        c = TEAL if mark == "✓" else RED
        x = R + (1 - a) * 300
        rrect(d, (x - (R - M), y, x, y + 175), 30, fill=col(PANEL, a))
        d.ellipse((x - 100, y + 52, x - 30, y + 122), fill=col(c, a))
        if mark == "✓":
            d.line((x - 84, y + 88, x - 70, y + 104), fill=col(BG, a), width=7)
            d.line((x - 70, y + 104, x - 46, y + 72), fill=col(BG, a), width=7)
        else:
            d.line((x - 80, y + 72, x - 50, y + 102), fill=col(BG, a), width=7)
            d.line((x - 50, y + 72, x - 80, y + 102), fill=col(BG, a), width=7)
        T(d, (x - 130, y + 26), main, font("bold", 50), CREAM, a)
        T(d, (x - 130, y + 100), sub, font("body", 38), MUTED, a)
        y += 200


def sc_compare(d, t, s):
    kicker(d, 340, s["kicker"], ph(t, 0))
    y0 = title(d, 460, s["title"], ph(t, 0.15), 70) + 50
    cw = (R - M - 30) / 2
    for k, side in enumerate(s["cols"]):
        a = ph(t, 0.5 + k * 0.9, 0.5)
        x1 = R - k * (cw + 30)
        c = side["color"]
        if a > 0.01:
            rrect(d, (x1 - cw, y0 + 30 * (1 - a), x1, y0 + 520 + 30 * (1 - a)), 32, fill=col(PANEL, a), outline=col(c, a), width=3)
            rrect(d, (x1 - cw, y0 + 30 * (1 - a), x1, y0 + 110 + 30 * (1 - a)), 32, fill=col(c, a))
        T(d, (x1 - cw / 2, y0 + 20 + 30 * (1 - a)), side["head"], font("bold", 52), BG, a, "ma")
        for j, it in enumerate(side["items"]):
            T(d, (x1 - cw / 2, y0 + 160 + j * 95 + 30 * (1 - a)), it, font("semi", 44), CREAM, a, "ma")
    if s.get("tip"):
        a = ph(t, 2.4, 0.6)
        if a > 0.01:
            rrect(d, (M, y0 + 580, R, y0 + 700), 30, outline=col(GOLD, a), width=3)
        T(d, (W / 2, y0 + 608), s["tip"], font("semi", 46), GOLD, a, "ma")


def sc_equation(d, t, s):
    kicker(d, 340, s["kicker"], ph(t, 0))
    y = 560
    for k, (label, val, c) in enumerate(s["rows"]):
        a = ph(t, 0.4 + k * 0.7, 0.45)
        if k == len(s["rows"]) - 1:
            if a > 0.01:
                d.line((M + 40, y - 30, R - 40, y - 30), fill=col(GOLD, a), width=4)
        if a > 0.01:
            rrect(d, (M, y, R, y + 150), 30, fill=col(PANEL if k < len(s["rows"]) - 1 else (36, 70, 60), a))
        T(d, (R - 40, y + 38), label, font("bold", 54), c, a)
        T(d, (M + 40, y + 40), val, font("bold", 54), CREAM, a, "la")
        y += 200
    if s.get("note"):
        a = ph(t, 0.4 + len(s["rows"]) * 0.7 + 0.2, 0.6)
        para(d, W / 2, y + 30, s["note"], font("semi", 46), col(GOLD, a), R - M, 1.5, "ma") if a > 0.01 else None


def sc_inapp(d, t, s):
    p = ph(t, 0)
    if p > 0.01:
        star8(d, R - 30, 380, 30, col(GOLD, p), 3)
    T(d, (R - 80, 340), s.get("kicker", "في خِزانة"), font("head", 64), GOLD, p)
    y = 520
    for k, (main, sub) in enumerate(s["items"]):
        a = ph(t, 0.4 + k * 0.6, 0.45)
        if a > 0.01:
            rrect(d, (M, y, R, y + 175), 30, fill=col(PANEL, a), outline=col(GOLD_D, a), width=2)
            d.ellipse((R - 105, y + 50, R - 30, y + 125), fill=col(GOLD, a))
        T(d, (R - 67, y + 52), ar(k + 1), font("bold", 48), BG, a, "ma")
        T(d, (R - 135, y + 28), main, font("bold", 48), CREAM, a)
        T(d, (R - 135, y + 100), sub, font("body", 36), MUTED, a)
        y += 200


def sc_end(d, t, s):
    cx = W / 2
    p = ph(t, 0.0, 0.9)
    for rr, wd in ((130, 5), (76, 3)):
        for base in (0, 45):
            pts = [(cx + rr * p * math.cos(math.radians(base + 90 * k + 45 + t * 6)),
                    520 + rr * p * math.sin(math.radians(base + 90 * k + 45 + t * 6))) for k in range(4)]
            if p > 0.02:
                d.polygon(pts, outline=col(GOLD, p), width=wd)
    a = ph(t, 0.3, 0.7)
    T(d, (cx, 690), "خِزانة", font("head", 150), GOLD, a, "ma")
    if a > 0.01:
        d.text((cx, 930), "prog-alone.github.io/khizana", font=font("semi", 42), fill=col(CREAM, a), anchor="ma", direction="ltr")
    b = ph(t, 1.0, 0.6)
    if b > 0.01:
        rrect(d, (M, 1080, R, 1330), 34, outline=col(GOLD, b), width=3)
    T(d, (cx, 1105), "الحلقة القادمة", font("semi", 40), MUTED, b, "ma")
    T(d, (cx, 1185), s["next"], font("bold", 58), CREAM, b, "ma")


RENDER = dict(hook=sc_hook, define=sc_define, list=sc_list, compare=sc_compare,
              equation=sc_equation, inapp=sc_inapp, end=sc_end)


def make_frame(spec, i):
    t = i / FPS
    dur = spec["duration"]
    img = BGIMG.copy()
    scenes = spec["scenes"]
    for n, sc in enumerate(scenes):
        s0 = sc["bar"] * BAR
        e0 = scenes[n + 1]["bar"] * BAR if n + 1 < len(scenes) else dur + 1
        if not (s0 - 0.01 <= t < e0):
            continue
        lt = t - s0
        layer = Image.new("RGBA", (W, H), (0, 0, 0, 0))
        RENDER[sc["type"]](ImageDraw.Draw(layer), lt, sc)
        last = n == len(scenes) - 1
        fade_in = 1.0 if n == 0 else ease_io(lt / 0.25)
        fade_out = ease_io((dur - t) / 1.2) if last else ease_io((e0 - t) / 0.3)
        k = min(fade_in, fade_out)
        if k < 1:
            layer.putalpha(layer.getchannel("A").point(lambda v: int(v * k)))
        img.alpha_composite(layer, (0, 0 if last else int(-40 * (1 - fade_out))))
    d = ImageDraw.Draw(img)
    brand_mark(d, R, 150, 44)
    tag = f"الحلقة {ar(spec['num'])}"
    f = font("semi", 34)
    rrect(d, (M, 152, M + tw(tag, f) + 50, 214), 31, fill=GOLD)
    text(d, (M + 25 + tw(tag, f), 160), tag, f, BG)
    d.rectangle((W - (W * t / dur), 0, W, 8), fill=GOLD)
    return img.convert("RGB")


def make_cover(spec):
    """Grid cover: middle 3:4 (y 240→1680) carries everything."""
    img = background(W, H, glow=(0.5, 0.42))
    d = ImageDraw.Draw(img)
    cx = W / 2
    text(d, (cx, 330), "خِزانة", font("head", 70), GOLD, "ma")
    ORD = ["", "الأولى", "الثانية", "الثالثة", "الرابعة", "الخامسة", "السادسة", "السابعة", "الثامنة", "التاسعة",
           "العاشرة", "الحادية عشرة", "الثانية عشرة", "الثالثة عشرة", "الرابعة عشرة"]
    star8(d, cx, 640, 150, GOLD, 5)
    star8(d, cx, 640, 88, GOLD, 3)
    text(d, (cx, 590), ar(spec["num"]), font("bold", 90), GOLD, "ma")
    text(d, (cx, 860), "الحلقة " + ORD[spec["num"]], font("semi", 56), MUTED, "ma")
    f = font("bold", 92)
    y = 1130
    for ln in wrap(spec["cover_title"], f, R - M):
        text(d, (cx, y), ln, f, CREAM, "ma")
        y += 125
    return img


if __name__ == "__main__":
    spec = runpy.run_path(sys.argv[1])["SPEC"]
    out = spec["out"]
    os.makedirs(out, exist_ok=True)
    make_cover(spec).save(f"{out}/cover.jpg", quality=94)
    if len(sys.argv) > 2:
        for sc in spec["scenes"]:
            tt = sc["bar"] * BAR + sc.get("still", 3.5)
            make_frame(spec, int(tt * FPS)).resize((360, 640)).save(f"/tmp/claude-0/ep_{sc['bar']}.jpg")
        sys.exit()
    p = subprocess.Popen(["ffmpeg", "-y", "-loglevel", "error", "-f", "rawvideo", "-pix_fmt", "rgb24", "-s", f"{W}x{H}",
                          "-r", str(FPS), "-i", "-", "-i", f"{out}/music.wav", "-c:v", "libx264", "-preset", "medium",
                          "-crf", "18", "-pix_fmt", "yuv420p", "-c:a", "aac", "-b:a", "192k", "-shortest",
                          "-movflags", "+faststart", f"{out}/reel.mp4"], stdin=subprocess.PIPE)
    for i in range(int(spec["duration"] * FPS)):
        p.stdin.write(make_frame(spec, i).tobytes())
    p.stdin.close(); p.wait(); print("done", p.returncode)
