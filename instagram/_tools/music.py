"""Original instrumental for the Khizana reel: lo-fi beat in D Hijaz, 100 BPM, 14 bars.
Scene changes land on downbeats and each gets a soft chime, so the music follows the information."""
import numpy as np
from scipy.io import wavfile
from scipy.signal import butter, lfilter

SR = 44100
BPM = 100
BEAT = 60 / BPM
BAR = BEAT * 4
import os, json
NBARS = int(os.environ.get("NBARS", 14))
LEN = int(SR * (BAR * NBARS + 2.5))
rng = np.random.default_rng(7)
mix = np.zeros((LEN, 2))

SCENES = json.loads(os.environ.get("SCENES", "[0, 2, 4, 6, 8, 9, 10, 11, 12]"))  # bar index of each scene start


def hz(m):
    return 440 * 2 ** ((m - 69) / 12)


def add(sig, t, pan=0.0, gain=1.0):
    i = int(t * SR)
    if i >= LEN:
        return
    sig = sig[: LEN - i] * gain
    l, r = np.cos((pan + 1) * np.pi / 4), np.sin((pan + 1) * np.pi / 4)
    mix[i:i + len(sig), 0] += sig * l
    mix[i:i + len(sig), 1] += sig * r


def lp(x, fc, order=2):
    b, a = butter(order, fc / (SR / 2))
    return lfilter(b, a, x)


def env(n, a, r):
    e = np.ones(n)
    na, nr = int(a * SR), int(r * SR)
    e[:na] = np.linspace(0, 1, na)
    e[-nr:] *= np.linspace(1, 0, nr)
    return e


def pad(notes, dur):
    n = int(dur * SR)
    t = np.arange(n) / SR
    s = np.zeros(n)
    for m in notes:
        for det in (-0.12, 0.0, 0.12):
            f = hz(m + det)
            s += np.sin(2 * np.pi * f * t) + 0.3 * np.sin(4 * np.pi * f * t + 0.5)
    s = lp(s, 1400) * env(n, 0.6, 0.8)
    return s / (len(notes) * 3)


def pluck(m, dur=1.6, bright=0.5):
    """Karplus-Strong — oud/qanun-like pluck."""
    f = hz(m)
    N = int(SR / f)
    buf = rng.uniform(-1, 1, N)
    n = int(dur * SR)
    out = np.zeros(n)
    for i in range(n):
        out[i] = buf[i % N]
        buf[i % N] = 0.5 * (buf[i % N] + buf[(i + 1) % N]) * (0.994 + 0.004 * bright)
    return lp(out, 3500) * env(n, 0.002, 0.3)


def kick():
    n = int(0.45 * SR)
    t = np.arange(n) / SR
    f = 50 + 90 * np.exp(-t * 30)
    return np.sin(2 * np.pi * np.cumsum(f) / SR) * np.exp(-t * 7)


def snare():
    n = int(0.3 * SR)
    t = np.arange(n) / SR
    no = lp(rng.uniform(-1, 1, n), 5000) * np.exp(-t * 16)
    return 0.6 * no + 0.3 * np.sin(2 * np.pi * 190 * t) * np.exp(-t * 25)


def hat():
    n = int(0.08 * SR)
    no = rng.uniform(-1, 1, n)
    b, a = butter(2, 7000 / (SR / 2), "high")
    return lfilter(b, a, no) * np.exp(-np.arange(n) / SR * 60)


def bass(m, dur):
    n = int(dur * SR)
    t = np.arange(n) / SR
    s = np.sin(2 * np.pi * hz(m) * t) + 0.25 * np.sin(4 * np.pi * hz(m) * t)
    return s * env(n, 0.01, 0.15)


def chime(m):
    n = int(2.2 * SR)
    t = np.arange(n) / SR
    s = sum(np.sin(2 * np.pi * hz(m) * k * t) * np.exp(-t * (2 + k)) / k for k in (1, 2.76, 5.4))
    return s * env(n, 0.003, 0.5)


# D Hijaz: D Eb F# G A Bb C — chord cycle D | Cm | Gm | D
CHORDS = [(50, [62, 66, 69]), (48, [60, 63, 67]), (43, [62, 67, 70]), (50, [62, 66, 69])]
ARP = [[74, 69, 66, 69, 74, 75, 74, 69], [72, 67, 63, 67, 72, 74, 72, 67],
       [70, 67, 62, 67, 70, 72, 74, 70], [74, 69, 66, 69, 75, 74, 72, 69]]
# lead melody (hijaz phrase) used on the 50/30/20 + savings section
LEAD = {6: [(0, 74, 1), (1, 75, 1), (2, 78, 1.5), (3.5, 79, .5)],
        7: [(0, 81, 2), (2, 79, 1), (3, 78, 1)],
        8: [(0, 79, 1), (1, 78, 1), (2, 75, 1), (3, 74, 1)],
        9: [(0, 75, 1.5), (1.5, 74, .5), (2, 72, 1), (3, 74, 1)]}

for b in range(NBARS):
    t0 = b * BAR
    root, notes = CHORDS[b % 4]
    full = 2 <= b <= 11
    last = b >= 12
    add(pad(notes, BAR + 0.8), t0, 0, 0.55 if not last else 0.7)
    # arpeggio pluck on 8ths (sparser in intro/outro)
    for k, m in enumerate(ARP[b % 4]):
        if (not full) and k % 2:
            continue
        add(pluck(m, 1.4), t0 + k * BEAT / 2, 0.35 if k % 2 else -0.35, 0.28)
    if full:
        add(bass(root, BAR * 0.95), t0, 0, 0.35)
        for k in range(4):
            if k in (0, 2):
                add(kick(), t0 + k * BEAT, 0, 0.75)
            if k in (1, 3):
                add(snare(), t0 + k * BEAT, 0.1, 0.35)
        for k in range(8):
            add(hat(), t0 + k * BEAT / 2 + (0.03 if k % 2 else 0), 0.2, 0.12 if k % 2 else 0.18)
    if b in LEAD:
        for off, m, dur in LEAD[b]:
            add(pluck(m - 12, dur * BEAT + 0.6, 1.0), t0 + off * BEAT, -0.1, 0.42)

# scene-change chimes, alternating notes of the D chord
for i, b in enumerate(SCENES):
    add(chime([86, 81, 78][i % 3]), b * BAR, 0.2 if i % 2 else -0.2, 0.12)
# final ring: low D + chord
add(pluck(38, 3.0), NBARS * BAR - BAR, 0, 0.5)

# soft tape saturation, master fade-out at end
mix = np.tanh(mix * 1.4) / np.tanh(1.4)
end = int((NBARS * BAR + 1.0) * SR)
fade = np.ones(LEN)
fade[end - int(2.5 * SR):end] = np.linspace(1, 0, int(2.5 * SR))
fade[end:] = 0
mix *= fade[:, None]
mix = mix[: end]
mix /= np.abs(mix).max() * 1.12
wavfile.write(os.environ.get("OUT", "/home/claude/khz/out/khizana_music.wav"), SR, (mix * 32767).astype(np.int16))
print("len", len(mix) / SR)
