"""Carousel post (1080x1350) from SPEC['slides']; also writes a PDF of the slides for LinkedIn.
Usage: python3 carousel.py eps/epNN.py"""
from common import *
import sys, runpy, os

W, H, M = 1080, 1350, 90
R = W - M
BLUE = (120, 160, 220)


def frame(i, n, glow=(0.8, 0.15)):
    img = background(W, H, glow=glow)
    d = ImageDraw.Draw(img)
    brand_mark(d, R, 64, 38)
    d.text((W / 2, 72), "@h.nj2", font=font("semi", 30), fill=MUTED, anchor="ma", direction="ltr")
    text(d, (M, 70), f"{ar(i)} / {ar(n)}", font("semi", 30), MUTED, "la")
    return img, d


def swipe(d):
    f = font("body", 30)
    s = "اسحب للتالي"
    w = tw(s, f)
    x0 = W / 2 - (w + 60) / 2
    text(d, (x0 + 60 + w, H - 96), s, f, MUTED)
    y = H - 76
    d.line((x0, y, x0 + 38, y), fill=MUTED, width=3)
    d.line((x0, y, x0 + 14, y - 12), fill=MUTED, width=3)
    d.line((x0, y, x0 + 14, y + 12), fill=MUTED, width=3)


def kicker(d, y, s):
    f = font("semi", 34)
    w = tw(s, f)
    rrect(d, (R - w - 44, y, R, y + 66), 33, outline=GOLD, width=2)
    text(d, (R - 22, y + 10), s, f, GOLD)


def title(d, y, s, size=58, c=CREAM, anchor="ra", x=None):
    f = font("bold", size)
    x = R if x is None else x
    for ln in wrap(s, f, R - M):
        text(d, (x, y), ln, f, c, anchor)
        y += size * 1.4
    return y


def s_cover(d, sl, spec):
    cx = W / 2
    star8(d, cx, 380, 140, GOLD, 5)
    star8(d, cx, 380, 82, GOLD, 3)
    text(d, (cx, 330), ar(spec["num"]), font("bold", 84), GOLD, "ma")
    y = title(d, 600, sl["title"], 104, GOLD, "ma", cx)
    title(d, y + 20, sl["sub"], 48, CREAM, "ma", cx)
    text(d, (cx, 1060), "من الدخل إلى الزكاة", font("body", 36), MUTED, "ma")


def s_text(d, sl, spec):
    kicker(d, 200, sl["kicker"])
    y = title(d, 320, sl["title"], 64)
    y = para(d, R, y + 40, sl["body"], font("body", 42), MUTED, R - M, 1.65)
    if sl.get("points_label"):
        text(d, (R, y + 30), sl["points_label"], font("semi", 38), GOLD)
        y += 90
    for k, pt in enumerate(sl.get("points", [])):
        rrect(d, (M, y + 14, R, y + 110), 24, fill=PANEL)
        d.ellipse((R - 68, y + 46, R - 36, y + 78), fill=GOLD)
        text(d, (R - 94, y + 34), pt, font("semi", 40), CREAM)
        y += 110


def s_flowstock(d, sl, spec):
    kicker(d, 200, "الدخل تدفّق… والثروة مخزون")
    title(d, 310, "تخيّل حوض ماء", 60)
    # tap (income) → tub (wealth) → drain (spending)
    tx, ty = R - 160, 470
    rrect(d, (tx - 150, ty, tx + 40, ty + 46), 18, fill=TEAL)
    rrect(d, (tx - 150, ty, tx - 100, ty + 110), 14, fill=TEAL)
    for k in range(5):
        d.line((tx - 125, ty + 120 + k * 40, tx - 125, ty + 140 + k * 40), fill=TEAL, width=10)
    text(d, (tx + 40, ty - 60), "الدخل يتدفّق إليه", font("semi", 36), TEAL)
    bx0, by0, bx1, by1 = M + 60, 690, R - 60, 1010
    d.rounded_rectangle((bx0, by0, bx1, by1), 40, outline=CREAM, width=6)
    d.rounded_rectangle((bx0 + 10, by0 + 120, bx1 - 10, by1 - 10), 32, fill=(46, 92, 120))
    text(d, (W / 2, by0 + 180), "الثروة: ما يبقى في الحوض", font("bold", 46), CREAM, "ma")
    d.line((bx0 + 120, by1, bx0 + 120, by1 + 70), fill=RED, width=12)
    text(d, (bx0 + 160, by1 + 30), "المصروف يتسرّب منه", font("semi", 36), RED, "la")
    text(d, (W / 2, 1160), "الدخل يُقاس بمدّة، والثروة تُقاس بلحظة", font("semi", 40), GOLD, "ma")


def s_cards(d, sl, spec):
    kicker(d, 200, sl["kicker"])
    y0 = title(d, 310, sl["title"], 54) + 30
    cw, ch, gap = (R - M - 24) / 2, 330, 24
    for k, (head, earn, ex, c) in enumerate(sl["cards"]):
        x1 = R - (k % 2) * (cw + gap)
        y = y0 + (k // 2) * (ch + gap)
        rrect(d, (x1 - cw, y, x1, y + ch), 30, fill=PANEL, outline=c, width=3)
        rrect(d, (x1 - cw, y, x1, y + 14), 7, fill=c)
        text(d, (x1 - 30, y + 46), head, font("bold", 46), CREAM)
        rrect(d, (x1 - 30 - tw(earn, font("semi", 36)) - 40, y + 128, x1 - 30, y + 186), 29, fill=c)
        text(d, (x1 - 50, y + 134), earn, font("semi", 36), BG)
        para(d, x1 - 30, y + 220, ex, font("body", 32), MUTED, cw - 60, 1.5)


def s_compare(d, sl, spec):
    kicker(d, 200, sl["kicker"])
    y0 = title(d, 310, sl["title"], 60) + 40
    cw = (R - M - 30) / 2
    for k, side in enumerate(sl["cols"]):
        x1 = R - k * (cw + 30)
        c = side["color"]
        rrect(d, (x1 - cw, y0, x1, y0 + 560), 32, fill=PANEL, outline=c, width=3)
        rrect(d, (x1 - cw, y0, x1, y0 + 110), 32, fill=c)
        text(d, (x1 - cw / 2, y0 + 22), side["head"], font("bold", 48), BG, "ma")
        for j, it in enumerate(side["items"]):
            para(d, x1 - cw / 2, y0 + 160 + j * 130, it, font("semi", 38), CREAM, cw - 50, 1.4, "ma")


def s_equation(d, sl, spec):
    kicker(d, 200, sl["kicker"])
    y = title(d, 310, sl["title"], 58) + 40
    for k, (label, val, c) in enumerate(sl["rows"]):
        if k == len(sl["rows"]) - 1:
            d.line((M + 40, y - 22, R - 40, y - 22), fill=GOLD, width=4)
        rrect(d, (M, y, R, y + 140), 28, fill=PANEL if k < len(sl["rows"]) - 1 else (36, 70, 60))
        text(d, (R - 36, y + 36), label, font("bold", 48), c)
        text(d, (M + 36, y + 42), val, font("semi", 40), CREAM, "la")
        y += 180
    text(d, (W / 2, y + 30), sl["note"], font("bold", 46), GOLD, "ma")


def s_cta(d, sl, spec):
    cx = W / 2
    text(d, (cx, 260), "سؤال لك", font("semi", 44), MUTED, "ma")
    title(d, 340, sl["question"], 72, GOLD, "ma", cx)
    text(d, (cx, 560), "اكتب جوابك في التعليقات 👇".replace(" 👇", ""), font("body", 40), CREAM, "ma")
    rrect(d, (M, 700, R, 940), 34, outline=GOLD, width=3)
    text(d, (cx, 726), "الحلقة القادمة", font("semi", 38), MUTED, "ma")
    text(d, (cx, 800), sl["next"], font("bold", 54), CREAM, "ma")
    text(d, (cx, 1010), "احفظ المنشور · تابع", font("body", 38), MUTED, "ma")
    d.text((cx, 1070), "@h.nj2", font=font("bold", 72), fill=GOLD, anchor="ma", direction="ltr")


RENDER = dict(cover=s_cover, text=s_text, flowstock=s_flowstock, cards=s_cards,
              compare=s_compare, equation=s_equation, cta=s_cta)

if __name__ == "__main__":
    spec = runpy.run_path(sys.argv[1])["SPEC"]
    out = spec["out"]
    os.makedirs(out, exist_ok=True)
    slides = spec["slides"]
    imgs = []
    for i, sl in enumerate(slides, 1):
        img, d = frame(i, len(slides), glow=(0.5, 0.3) if sl["type"] in ("cover", "cta") else (0.8, 0.15))
        RENDER[sl["type"]](d, sl, spec)
        if i < len(slides):
            swipe(d)
        p = f"{out}/post_{i:02d}.jpg"
        img.save(p, quality=93)
        imgs.append(img.convert("RGB"))
    imgs[0].save(f"{out}/post.pdf", save_all=True, append_images=imgs[1:], resolution=150)
    s = Image.new("RGB", (270 * 4, 337 * ((len(imgs) + 3) // 4)))
    for k, im in enumerate(imgs):
        s.paste(im.resize((270, 337)), ((k % 4) * 270, (k // 4) * 337))
    s.save("/tmp/claude-0/carousel.jpg", quality=85)
    print("ok", len(imgs))
