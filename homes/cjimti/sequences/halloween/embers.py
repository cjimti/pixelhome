"""Embers: A deep red bed. Random pixels slowly catch orange and fade; some glitch sideways a pixel
or two before going out; a few sparks drift along the roof."""
import numpy as np
from pixelhome.fx import DT, hexc, perc, smoothstep, lerp, nframes, looped, candle_bed

CODE = 'NT2'
TITLE = 'Embers'
KIND = 'ambient'
DESCRIPTION = 'A deep red bed where random pixels slowly catch orange and fade, some glitching sideways first.'

EMBER_RED = hexc('#ff0800')
ORANGE = hexc('#ff4a00')
FLOOR_COLOR = hexc('#ff4a08')
FLOOR = 0.13
LOOP = 300.0


def render(G, seed=12):
    rng = np.random.default_rng(seed)
    def draw(D):
        n = G.N
        out = np.zeros((nframes(D), n, 3), np.float32)
        idx = np.arange(n)
        bed = candle_bed(rng, n, 0.19, 0.15)
        E = int(D * 7)
        t0 = rng.uniform(-4, D, E)
        p0 = rng.integers(0, n, E).astype(float)
        att = rng.uniform(0.6, 1.6, E)
        hold = rng.uniform(0.3, 2.5, E)
        dec = rng.uniform(1.8, 4.5, E)
        peak = rng.uniform(0.28, 0.42, E)
        glitchy = rng.random(E) < 0.3
        hop_t = np.sort(rng.uniform(0, 1, (E, 3)), 1) * (att + hold)[:, None]
        hop_d = rng.choice([-2, -1, 1, 2], (E, 3)) * glitchy[:, None]
        S = int(D / 9)
        s0 = rng.uniform(-8, D, S)
        sp = rng.uniform(0, n, S)
        sv = rng.uniform(6, 18, S) * rng.choice([-1, 1], S)
        slen = rng.uniform(5, 9, S)
        for f in range(len(out)):
            t = f * DT
            I = bed(t)
            u = t - t0
            live = (u > 0) & (u < att + hold + dec)
            uu = u[live]
            env = np.where(uu < att[live], smoothstep(0, 1, uu / att[live]),
                           np.where(uu < att[live] + hold[live], 1.0,
                                    1 - smoothstep(0, 1, (uu - att[live] - hold[live]) / dec[live])))
            pos = (p0[live] + (hop_d[live] * (uu[:, None] > hop_t[live])).sum(1)).astype(int) % n
            hot = np.zeros(n)
            np.maximum.at(hot, pos, env * peak[live])
            for a, p, v, L in zip(s0, sp, sv, slen):
                us = t - a
                if 0 < us < L:
                    x = (p + v * us) % n
                    e = 0.36 * np.sin(np.pi * us / L) ** 2
                    w = np.clip(1 - np.abs(idx - x), 0, 1)
                    hot = np.maximum(hot, e * w)
            col = lerp(EMBER_RED, ORANGE, smoothstep(0.18, 0.38, np.maximum(I, hot))[:, None])
            out[f][G.path] = perc(np.maximum(I, hot))[:, None] * col
        return out
    return looped(draw, LOOP, floor=(FLOOR, FLOOR_COLOR))


# ---- music: an all-night loop, soft and far away. Low string tremolo moves through eight slow chords
# (one per SECTION); every drifting spark on the roof is a glass tone that blooms and fades with it,
# panned along its path; now and then a beam somewhere in the house creaks. ----

SECTION = LOOP / 8
BED = [                                     # sounding pitches: contrabass root, two cello notes
    ('D2', 'A2', 'F3'), ('Bb1', 'F2', 'D3'), ('G1', 'Bb2', 'D3'), ('A1', 'E2', 'C3'),
    ('F1', 'A2', 'D3'), ('Eb2', 'Bb2', 'G3'), ('C2', 'G2', 'Eb3'), ('A1', 'E2', 'C#3'),
]
GLASS = [                                   # what the sparks may ring in each section
    ('D4', 'F4', 'A4', 'D5', 'E5'), ('D4', 'F4', 'Bb4', 'C5', 'F5'), ('D4', 'G4', 'Bb4', 'D5', 'A4'),
    ('C4', 'E4', 'A4', 'B4', 'E5'), ('D4', 'F4', 'A4', 'C5', 'F5'), ('Eb4', 'G4', 'Bb4', 'D5', 'F5'),
    ('C4', 'Eb4', 'G4', 'D5', 'Bb4'), ('C#4', 'E4', 'A4', 'E5', 'G4'),
]


def _sparks(G):
    """The roof sparks exactly as render() draws them: (start, path index, pixels/s, life)."""
    rng = np.random.default_rng(12)
    n, D = G.N, LOOP + 12.0                  # looped() renders 12 s past the loop and blends it in
    candle_bed(rng, n, 0.19, 0.15)
    E = int(D * 7)
    rng.uniform(-4, D, E), rng.integers(0, n, E)
    for _ in range(4):
        rng.uniform(0, 1, E)
    rng.random(E), rng.uniform(0, 1, (E, 3)), rng.choice([-2, -1, 1, 2], (E, 3))
    S = int(D / 9)
    s0 = rng.uniform(-8, D, S)
    sp = rng.uniform(0, n, S)
    sv = rng.uniform(6, 18, S) * rng.choice([-1, 1], S)
    slen = rng.uniform(5, 9, S)
    return list(zip(s0, sp, sv, slen))


def score(M, G):
    from pixelhome.audio import SR, note
    rng = np.random.default_rng(31)
    N = int(LOOP * SR)
    xs = G.pos[G.path, 0]
    zs = G.pos[G.path, 2]
    x0, x1, z0, z1 = xs.min(), xs.max(), zs.min(), zs.max()

    def pan_px(p):                           # path index -> pan across the facade from the street
        return 0.8 * (2 * (np.interp(p, np.arange(G.N), xs) - x0) / (x1 - x0) - 1)

    def near_px(p):                          # 0 far back (Side end, porch) .. 1 front
        return (np.interp(p, np.arange(G.N), zs) - z0) / (z1 - z0)

    def put(buf, sig, t):
        """Add sig into a circular LOOP-long buffer at t, wrapping round the end."""
        s = int(round(t * SR)) % N
        k = 0
        while k < sig.shape[1]:
            m = min(sig.shape[1] - k, N - s)
            buf[:, s:s + m] += sig[:, k:k + m]
            k += m
            s = 0

    def tone(buf, f, hz):                    # circular FFT filter: f(freqs) -> gain
        spec = np.fft.rfft(buf, axis=1)
        spec *= f(np.fft.rfftfreq(buf.shape[1], 1 / SR))
        return np.fft.irfft(spec, buf.shape[1], axis=1)

    def ride(buf, win, amount, up=True):
        """Slow circular gain riding toward the buffer's own average level: evens out loud and quiet
        stretches by `amount` (0..1); with up=False it only turns loud stretches down."""
        p = (buf ** 2).mean(0)
        k = int(win * SR)
        c = np.cumsum(np.r_[p[-k:], p, p[:k]])
        env = np.sqrt(np.maximum((c[2 * k:] - c[:-2 * k])[:N] / (2 * k), 1e-12))
        ref = np.sqrt(p.mean())
        g = (ref / env) ** amount
        g = np.clip(g, 0.2, 2.5 if up else 1.0)
        return buf * g

    def lowpass(fc, order=2):
        return lambda fr: 1 / np.sqrt(1 + (fr / fc) ** (2 * order))

    def pan2(sig, p):                        # p scalar or per-sample
        a = (np.asarray(p) + 1) * np.pi / 4
        return np.vstack([sig * np.cos(a), sig * np.sin(a)]) * np.sqrt(2)

    # ---- the bed: tremolo cellos and a contrabass, far off, overlapping grains so notes hold for a whole
    # section and cross-fade into the next chord ----
    cb = M.sampler('Strings/Solo Contrabass/Trem/*.wav', tune=-12)
    vc = M.sampler('Strings/Cello Section/trem/*.wav', tune=-12)
    bed = np.zeros((2, N))
    GR, SKIP, XF = 5.0, 0.7, 7.0              # grain length, bow attack skipped, chord cross-fade
    t = np.arange(int(GR * SR)) / SR
    win = np.sin(np.pi * t / GR) ** 2         # hop GR/2: windows sum to one
    for k, chord in enumerate(BED):
        a, b = k * SECTION - XF / 2, (k + 1) * SECTION + XF / 2
        for v, (inst, name, vel, gain, pan) in enumerate(((cb, chord[0], 40, 0.9, -0.15),
                                                          (vc, chord[1], 44, 0.6, 0.35),
                                                          (vc, chord[2], 40, 0.45, -0.4))):
            g0 = a + rng.uniform(0, GR / 2)
            for gt in np.arange(g0 - GR / 2, b, GR / 2):
                mid = gt + GR / 2
                fade = np.clip(np.minimum(mid - a, b - mid) / XF, 0, 1)
                fade = np.sin(np.pi / 2 * fade) ** 2
                if fade <= 0:
                    continue
                s = inst.play(note(name), vel + int(rng.integers(-4, 5)))
                s = s[:, int(SKIP * SR):int(SKIP * SR) + len(win)]
                if s.shape[1] < len(win):
                    s = np.pad(s, ((0, 0), (0, len(win) - s.shape[1])))
                put(bed, pan2(s.mean(0) * win * fade * gain, pan + rng.uniform(-0.1, 0.1)), gt)
    bed = ride(bed, 4.0, 0.75)
    # breathe: swells that fit the loop a whole number of times
    tt = np.arange(N) / SR
    bed *= 0.78 + 0.14 * np.sin(2 * np.pi * 4 * tt / LOOP + 0.6) + 0.08 * np.sin(2 * np.pi * 9 * tt / LOOP + 2.1)
    bed = tone(bed, lambda fr: lowpass(700, 2)(fr) * np.clip(fr / 35, 0, 1), 0)
    M.bus('strings', gain=0.62, reverb=0.45)
    M.add('strings', bed, 0)

    # ---- glass: each roof spark rings a soft glassy tone that blooms and fades with the spark,
    # moving across the house with it. Sparks blended in from the loop's tail land on its head. ----
    glass = np.zeros((2, N))
    for s0, p, v, L in _sparks(G):
        if s0 < 0 or s0 >= LOOP + 12.0:
            continue
        w = 1.0
        if s0 < 12.0:                         # looped() fades the head's own sparks in ...
            w = s0 / 12.0
        elif s0 >= LOOP:                      # ... and the tail's sparks out over the first 12 s
            w = 1 - (s0 - LOOP) / 12.0
        if w < 0.08:
            continue
        sec = int((s0 % LOOP) // SECTION)
        f = 440 * 2 ** ((note(GLASS[sec][int(rng.integers(5))]) - 69) / 12)
        n = int((L + 0.5) * SR)
        u = np.arange(n) / SR
        env = np.sin(np.pi * np.clip(u / L, 0, 1)) ** 2
        sig = np.zeros(n)
        beat = rng.uniform(0.25, 0.7)
        ph = rng.uniform(0, 2 * np.pi, 5)
        for k, (mul, amp, pw) in enumerate(((1.0, 1.0, 1.0), (1.0 + beat / f, 0.55, 1.2), (2.0, 0.22, 1.8),
                                            (3.003, 0.06, 2.6), (4.17, 0.025, 3.4))):
            sig += amp * env ** pw * np.sin(2 * np.pi * f * mul * u + ph[k])
        sig *= 1 + 0.12 * np.sin(2 * np.pi * rng.uniform(0.3, 0.6) * u)          # a slow shimmer
        x = np.clip(p + v * np.clip(u, 0, L), 0, G.N - 1)                         # follow it, not wrapping
        gain = w * (0.55 + 0.45 * near_px(x)) * rng.uniform(0.7, 1.0)
        put(glass, pan2(sig * gain, pan_px(x)), s0)
    glass = ride(tone(glass, lowpass(2200, 2), 0), 1.5, 0.6, up=False)
    M.bus('glass', gain=0.035, reverb=0.6)
    M.add('glass', glass, 0)

    # ---- creaks: an old beam somewhere in the house, stick-slip ticks through a woody resonance ----
    creak = np.zeros((2, N))
    times, t = [], rng.uniform(10, 30)
    while t < LOOP - 4:
        times.append(t)
        t += rng.uniform(30, 52)
    for t0 in times:
        dur = rng.uniform(1.6, 3.0)
        n = int((dur + 0.3) * SR)
        sig = np.zeros(n)
        r0, r1 = rng.uniform(7, 11), rng.uniform(16, 26)
        f1 = rng.uniform(170, 260)
        ir_t = np.arange(int(0.06 * SR)) / SR
        ir = (np.sin(2 * np.pi * f1 * ir_t) + 0.4 * np.sin(2 * np.pi * f1 * 2.37 * ir_t)) * np.exp(-ir_t / 0.012)
        tc = 0.0
        while tc < dur:
            u = tc / dur
            rate = r0 + (r1 - r0) * np.sin(np.pi * u) ** 1.5
            amp = np.sin(np.pi * u) ** 2.5 * rng.uniform(0.6, 1.0)
            i = int(tc * SR)
            m = min(len(ir), n - i)
            sig[i:i + m] += amp * ir[:m]
            tc += rng.uniform(0.75, 1.25) / rate
        put(creak, pan2(sig * rng.uniform(0.6, 1.0), rng.uniform(-0.8, 0.8)), t0)
    creak = tone(creak, lambda fr: lowpass(1400, 2)(fr) * np.clip(fr / 90, 0, 1), 0)
    M.bus('creak', gain=0.09, reverb=0.7)
    M.add('creak', creak, 0)

    # ---- air: a faint dark breath under everything, loop-periodic ----
    air = rng.normal(0, 1, (2, N))
    air = tone(air, lambda fr: lowpass(380, 1)(fr) * np.clip(fr / 60, 0, 1), 0)
    air /= np.abs(air).max()
    air *= 0.7 + 0.3 * np.sin(2 * np.pi * 5 * tt / LOOP + 1.3)
    M.bus('air', gain=0.065, reverb=0.1)
    M.add('air', air, 0)
