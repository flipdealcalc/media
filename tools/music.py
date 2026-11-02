"""Original royalty-free background tracks synthesized with numpy."""
import numpy as np
from scipy.signal import butter, sosfilt
from scipy.io import wavfile

SR = 44100
rng = np.random.default_rng(7)

def note(n):  # MIDI -> Hz
    return 440.0 * 2 ** ((n - 69) / 12)

def env(n, a=0.005, d=0.2, s=0.0, r=0.05, length=None):
    length = length or n
    t = np.arange(n) / SR
    e = np.ones(n)
    ai = max(1, int(a * SR)); e[:ai] = np.linspace(0, 1, ai)
    di = int(d * SR)
    if di > 0:
        seg = slice(ai, min(n, ai + di))
        k = np.arange(seg.stop - seg.start) / max(1, di)
        e[seg] = 1 - (1 - s) * k
        e[ai + di:] = s
    ri = int(r * SR)
    if ri and n > ri: e[-ri:] *= np.linspace(1, 0, ri)
    return e

def lp(x, fc, order=2):
    sos = butter(order, fc, "low", fs=SR, output="sos"); return sosfilt(sos, x)
def hp(x, fc, order=2):
    sos = butter(order, fc, "high", fs=SR, output="sos"); return sosfilt(sos, x)
def bp(x, lo, hi):
    sos = butter(2, [lo, hi], "band", fs=SR, output="sos"); return sosfilt(sos, x)

def kick(level=1.0):
    n = int(0.35 * SR); t = np.arange(n) / SR
    f = 45 + 95 * np.exp(-t * 28)
    ph = 2 * np.pi * np.cumsum(f) / SR
    return level * np.sin(ph) * np.exp(-t * 9)
def snare(level=0.5):
    n = int(0.22 * SR); t = np.arange(n) / SR
    noise = bp(rng.standard_normal(n), 1200, 7000) * np.exp(-t * 18)
    tone = np.sin(2 * np.pi * 190 * t) * np.exp(-t * 30)
    return level * (0.8 * noise + 0.5 * tone)
def hat(level=0.18, decay=60):
    n = int(0.06 * SR); t = np.arange(n) / SR
    return level * hp(rng.standard_normal(n), 7000) * np.exp(-t * decay)
def saw(f, n):
    t = np.arange(n) / SR
    return 2 * ((t * f) % 1) - 1
def pluck(f, dur, level=0.25, bright=4000):
    n = int(dur * SR); t = np.arange(n) / SR
    x = 0.6 * saw(f, n) + 0.4 * np.sin(2 * np.pi * f * t)
    return level * lp(x, bright) * np.exp(-t * 6)
def epiano(f, dur, level=0.18):
    n = int(dur * SR); t = np.arange(n) / SR
    x = np.sin(2 * np.pi * f * t) + 0.35 * np.sin(2 * np.pi * 2 * f * t) * np.exp(-t * 3) + 0.15 * np.sin(2 * np.pi * 3 * f * t) * np.exp(-t * 5)
    return level * x * env(n, a=0.01, d=dur, s=0.25, r=0.15)
def pad(freqs, dur, level=0.06, cutoff=1800):
    n = int(dur * SR); x = np.zeros(n)
    for f in freqs:
        for det in (-0.12, 0.0, 0.12):
            x += saw(f * 2 ** (det / 12), n)
    return level * lp(x / (3 * len(freqs)), cutoff) * env(n, a=0.4, d=0.1, s=1.0, r=0.6)
def bass(f, dur, level=0.35, cutoff=600):
    n = int(dur * SR); t = np.arange(n) / SR
    x = 0.7 * np.sin(2 * np.pi * f * t) + 0.3 * saw(f, n)
    return level * lp(x, cutoff) * env(n, a=0.005, d=dur * 0.8, s=0.5, r=0.04)

def add(buf, x, at):
    i = int(at * SR)
    if i >= len(buf): return
    j = min(len(buf), i + len(x)); buf[i:j] += x[: j - i]

CHORDS = {  # name: (root midi for bass, chord tones midi)
    "C": (36, [60, 64, 67]), "G": (43, [59, 62, 67]), "Am": (45, [57, 60, 64]), "F": (41, [57, 60, 65]),
    "Fmaj7": (41, [57, 60, 64, 65]), "Em7": (40, [55, 59, 62, 64]), "Dm7": (38, [57, 60, 62, 65]), "Cmaj7": (36, [55, 59, 60, 64]),
    "Dm": (38, [57, 62, 65]), "E": (40, [56, 59, 64]), "D": (38, [54, 57, 62]), "Bm": (47, [54, 59, 62]), "A": (45, [57, 61, 64]),
}

def track(style, seconds):
    cfg = {
        "upbeat": dict(bpm=112, prog=["C", "G", "Am", "F"]),
        "chill": dict(bpm=86, prog=["Fmaj7", "Em7", "Dm7", "Cmaj7"]),
        "tense": dict(bpm=96, prog=["Am", "F", "Dm", "E"]),
        "playful": dict(bpm=104, prog=["D", "A", "Bm", "G"]),
    }[style]
    beat = 60 / cfg["bpm"]; bar = 4 * beat
    total = seconds + 0.5
    L = np.zeros(int(total * SR)); R = np.zeros_like(L)
    nbars = int(np.ceil(total / bar))
    for b in range(nbars):
        t0 = b * bar
        root, tones = CHORDS[cfg["prog"][b % 4]]
        intro = b == 0
        if style == "upbeat":
            for k in range(4):
                if not intro or k >= 2: add(L, kick(0.9), t0 + k * beat); add(R, kick(0.9), t0 + k * beat)
                if k in (1, 3) and not intro: s = snare(0.42); add(L, s, t0 + k * beat); add(R, s, t0 + k * beat)
                h = hat(0.16); add(L, h * 0.8, t0 + k * beat + beat / 2); add(R, h, t0 + k * beat + beat / 2)
            for k in range(8):
                f = note(tones[k % len(tones)] + (12 if k % 4 == 3 else 0))
                p = pluck(f, beat / 2 * 0.95, 0.16, 3200); add(L if k % 2 else R, p, t0 + k * beat / 2); add(L if not k % 2 else R, p * 0.5, t0 + k * beat / 2)
            for k in range(4):
                bb = bass(note(root), beat * 0.9, 0.32); add(L, bb, t0 + k * beat); add(R, bb, t0 + k * beat)
            pd = pad([note(x) for x in tones], bar, 0.05, 2200); add(L, pd, t0); add(R, pd, t0)
        elif style == "chill":
            sw = beat * 0.58
            for k in range(4):
                if k in (0, 2) or (k == 3 and b % 2): add(L, kick(0.7), t0 + k * beat); add(R, kick(0.7), t0 + k * beat)
                if k in (1, 3): s = lp(snare(0.32), 4000); add(L, s, t0 + k * beat); add(R, s, t0 + k * beat)
                add(L, hat(0.10, 45), t0 + k * beat); add(R, hat(0.12, 45), t0 + k * beat + sw)
            for k, x in enumerate(tones):
                ep = epiano(note(x), bar * 0.95, 0.10); add(L, ep, t0 + k * 0.02); add(R, ep, t0 + k * 0.025)
            bb = bass(note(root), beat * 1.8, 0.30, 400); add(L, bb, t0); add(R, bb, t0)
            bb = bass(note(root + 7), beat * 1.6, 0.24, 400); add(L, bb, t0 + 2 * beat); add(R, bb, t0 + 2 * beat)
        elif style == "tense":
            for k in range(8):
                bb = bass(note(root), beat / 2 * 0.8, 0.30, 500); add(L, bb, t0 + k * beat / 2); add(R, bb, t0 + k * beat / 2)
                add(L, hat(0.09, 90), t0 + k * beat / 2 + beat / 4); add(R, hat(0.11, 90), t0 + k * beat / 2)
            if not intro:
                for k in (0, 2.5): add(L, kick(0.85), t0 + k * beat); add(R, kick(0.85), t0 + k * beat)
                s = snare(0.30); add(L, s, t0 + 3 * beat); add(R, s, t0 + 3 * beat)
            pd = pad([note(x - 12) for x in tones], bar, 0.07, 1200); add(L, pd, t0); add(R, pd, t0)
            stab = pluck(note(tones[-1] + 12), beat * 1.5, 0.08, 2500); add(L, stab, t0); add(R, stab * 0.7, t0 + 0.01)
        elif style == "playful":
            for k in range(4):
                if k in (0, 2) or (k == 3 and b % 2 == 1): add(L, kick(0.75), t0 + k * beat); add(R, kick(0.75), t0 + k * beat)
                if k in (1, 3) and not intro: s = hp(snare(0.32), 400); add(L, s, t0 + k * beat); add(R, s, t0 + k * beat)
                add(L, hat(0.12), t0 + k * beat + beat / 2); add(R, hat(0.14), t0 + k * beat + beat / 2)
            pattern = [0, 2, 1, 2, 0, 2, 1, 3]
            for k, idx in enumerate(pattern):
                f = note(tones[idx % len(tones)] + 12)
                p = pluck(f, beat / 2 * 0.6, 0.14, 5000); add(L if k % 2 else R, p, t0 + k * beat / 2); add(R if k % 2 else L, p * 0.45, t0 + k * beat / 2)
            for k in (0, 1.5, 2, 3.5):
                bb = bass(note(root), beat * 0.45, 0.30); add(L, bb, t0 + k * beat); add(R, bb, t0 + k * beat)
    x = np.stack([L, R], 1)[: int(seconds * SR)]
    # gentle glue: soft clip + fades
    x = np.tanh(x * 1.2) / np.tanh(1.2)
    fi, fo = int(0.25 * SR), int(1.2 * SR)
    x[:fi] *= np.linspace(0, 1, fi)[:, None]; x[-fo:] *= np.linspace(1, 0, fo)[:, None]
    x /= np.max(np.abs(x)) + 1e-9
    return (x * 0.89 * 32767).astype(np.int16)

if __name__ == "__main__":
    import sys
    style, secs, out = sys.argv[1], float(sys.argv[2]), sys.argv[3]
    wavfile.write(out, SR, track(style, secs))
