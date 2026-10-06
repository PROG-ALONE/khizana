"""Teaser story for an episode: a mysterious question, answer promised in the reel.
Usage: python3 story_q.py eps/epNN.py   (uses SPEC['teaser'] and SPEC['out'])"""
from common import *
import subprocess, sys, math, runpy

W, H, FPS, DUR = 1080, 1920, 30, 10.0
BGI = background(W, H, glow=(0.5, 0.4)).convert("RGBA")
DARK = Image.new("RGBA", (W, H), (4, 12, 11, 255))


def col(c, a):
    return (*c, int(255 * max(0, min(1, a))))


def ph(t, s, d=0.6):
    return ease((t - s) / d)


def frame(spec, i):
    tz = spec["teaser"]
    t = i / FPS
    img = Image.blend(DARK, BGI, 0.35 + 0.65 * ease_io(t / 5))
    L = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    d = ImageDraw.Draw(L)
    cx = W / 2
    # pulsing question mark inside the brand star
    p = ph(t, 0.0, 1.0)
    pulse = 1 + 0.04 * math.sin(t * 3)
    for rr, wd in ((150, 5), (88, 3)):
        r = rr * p * pulse
        for base in (0, 45):
            pts = [(cx + r * math.cos(math.radians(base + 90 * k + 45 + t * 8)),
                    560 + r * math.sin(math.radians(base + 90 * k + 45 + t * 8))) for k in range(4)]
            if p > 0.02:
                d.polygon(pts, outline=col(GOLD, p), width=wd)
    text(d, (cx, 470), "؟", font("head", 150), col(GOLD, p), "ma")
    # the question, line by line
    y = 820
    f = font("bold", 76)
    for k, ln in enumerate(wrap(tz["question"], f, W - 200)):
        a = ph(t, 0.8 + k * 0.6, 0.6)
        if a > 0.01:
            text(d, (cx, y + 20 * (1 - a)), ln, f, col(CREAM, a), "ma")
        y += 105
    if tz.get("hint"):
        a = ph(t, 2.8, 0.6)
        if a > 0.01:
            text(d, (cx, y + 30), tz["hint"], font("body", 44), col(MUTED, a), "ma")
    # the promise
    c = ph(t, 4.2, 0.6)
    if c > 0.01:
        rrect(d, (100, 1340, W - 100, 1560), 40, outline=col(GOLD, c), width=3)
        text(d, (cx, 1370), "الجواب في الريلز", font("bold", 60), col(CREAM, c), "ma")
        text(d, (cx, 1460), tz["when"], font("semi", 46), col(GOLD, c), "ma")
    e = ph(t, 5.0, 0.6)
    if e > 0.01:
        d.text((cx, 1640), "@h.nj2", font=font("bold", 48), fill=col(MUTED, e), anchor="ma", direction="ltr")
    img.alpha_composite(L)
    return img.convert("RGB")


if __name__ == "__main__":
    spec = runpy.run_path(sys.argv[1])["SPEC"]
    out = spec["out"]
    if len(sys.argv) > 2:
        frame(spec, int(8 * FPS)).resize((360, 640)).save("/tmp/claude-0/teaser.jpg")
        sys.exit()
    p = subprocess.Popen(["ffmpeg", "-y", "-loglevel", "error", "-f", "rawvideo", "-pix_fmt", "rgb24", "-s", f"{W}x{H}",
                          "-r", str(FPS), "-i", "-", "-ss", "0", "-t", str(DUR), "-i", f"{out}/music.wav",
                          "-af", f"afade=t=out:st={DUR-1.5}:d=1.5", "-c:v", "libx264", "-crf", "18", "-pix_fmt", "yuv420p",
                          "-c:a", "aac", "-b:a", "192k", "-shortest", "-movflags", "+faststart", f"{out}/teaser.mp4"],
                         stdin=subprocess.PIPE)
    for i in range(int(DUR * FPS)):
        p.stdin.write(frame(spec, i).tobytes())
    p.stdin.close(); p.wait(); print("done", p.returncode)
