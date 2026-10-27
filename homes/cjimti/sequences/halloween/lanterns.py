"""Lanterns: Each roof section is its own lantern, breathing at its own pace, with the corners glowing
like hooks. A lamplighter's glow walks the roof end to end, brightening each lantern as it passes."""
import numpy as np
from pixelhome.fx import DT, hexc, perc, light, keys, Flicker, nframes, looped

CODE = 'NT3'
TITLE = 'Lanterns'
KIND = 'ambient'
DESCRIPTION = 'Each roof section is a lantern breathing at its own pace. A lamplighter glow walks the roof end to end.'

AMBER = hexc('#ff7010')
FLOOR_COLOR = hexc('#ff4a08')
FLOOR = 0.13


def render(G, seed=13):
    rng = np.random.default_rng(seed)
    segs = G.path_segments()
    colors = [hexc(c) for c in ('#ff5a08', '#ff3000', '#ff7010', '#ff2000', '#ff6008', '#ff3a00')]

    def draw(D):
        n = G.N
        out = np.zeros((nframes(D), n, 3), np.float32)
        idx = np.arange(n, dtype=float)
        period = rng.uniform(7, 14, len(segs))
        phase = rng.uniform(0, 2 * np.pi, len(segs))
        shimmer = Flicker(rng, n, 0.1, 0.5)
        lit = np.zeros(len(segs))
        corners = np.zeros(n)
        for _, s in segs:
            for end in (s.min(), s.max()):
                corners = np.maximum(corners, np.exp(-((idx - end) / 2.5) ** 2))
        walk = [(0, 0.0), (20, 0.0), (140, n - 1.0), (170, n - 1.0), (290, 0.0), (D + 1, 0.0)]
        for f in range(len(out)):
            t = f * DT
            p = keys(t, walk)
            buf = np.zeros((n, 3))
            for i, (name, s) in enumerate(segs):
                inside = s.min() - 3 <= p <= s.max() + 3
                lit[i] = min(1.0, lit[i] + DT / 3) if inside else lit[i] * (1 - DT / 25)
                ph = (idx[s] - s.min()) / max(1, len(s) - 1)
                vign = 0.8 + 0.2 * np.sin(np.pi * ph)
                breath = 0.24 + 0.035 * np.sin(2 * np.pi * t / period[i] + phase[i])
                I = (breath + 0.1 * lit[i]) * vign * (1 + 0.05 * shimmer(t)[s])
                buf[s] = perc(I)[:, None] * colors[i]
            buf += light(AMBER, 0.26 * corners)
            buf += light(AMBER, 0.3 * np.exp(-((idx - p) / 14) ** 2))
            out[f] = 0
            out[f][G.path] = buf
        return out
    return looped(draw, 330.0, floor=(FLOOR, FLOOR_COLOR))


# ---- music: a far-off procession of lantern-bearers ----
LOOP = 330.0                     # the light loop, in seconds; the soundtrack wraps on the same length
CHORD_LEN = 27.5                 # twelve slow chords make one pass of the loop
XFADE = 7.0                      # each chord fades in and out over 2 * XFADE seconds, overlapping its neighbours
CHORDS = [                       # a wordless choir, low and close-voiced; the last chord leans back into the first
    ('D3', 'A3', 'E4', 'F4'),    # Dm9
    ('D3', 'Bb3', 'F4', 'A4'),   # Bbmaj7/D
    ('Bb2', 'G3', 'A3', 'D4'),   # Gm9/Bb
    ('A2', 'E3', 'A3', 'D4'),    # Asus4
    ('C3', 'F3', 'A3', 'E4'),    # Fmaj7/C
    ('A2', 'F3', 'A3', 'D4'),    # Dm/A
    ('G2', 'Eb3', 'G3', 'Bb3'),  # Eb/G, the shadow passing over
    ('Eb3', 'G3', 'C4', 'D4'),   # Cm9/Eb
    ('D3', 'F3', 'A3', 'C#4'),   # Dm(maj7)
    ('Bb2', 'F3', 'A3', 'E4'),   # Bbmaj7#11
    ('D3', 'G3', 'Bb3', 'E4'),   # Gm6/D
    ('A2', 'E3', 'G3', 'D4'),    # A7sus4, back to Dm9 at the top
]
SCALES = {6: 'D Eb F G A Bb C', 7: 'C D Eb F G Bb', 8: 'D E F G A Bb C#'}   # everything else is D aeolian
DRUMS = (12.0, 58.0, 101.0, 186.0, 233.0)    # muffled single hits, never closer than ~40 s
ROLLS = (138.0, 288.0)                       # a soft distant roll as the lamplighter reaches each end


def score(M, G):
    from pixelhome.audio import note, SR
    rng = np.random.default_rng(31)
    N = int(LOOP * SR)
    n = G.N
    segs = G.path_segments()
    walk = [(0, 0.0), (20, 0.0), (140, n - 1.0), (170, n - 1.0), (290, 0.0), (LOOP, 0.0)]   # as render()
    br = np.random.default_rng(13)          # the lanterns' breathing, drawn exactly as render() draws it
    period = br.uniform(7, 14, len(segs))
    period = LOOP / np.round(LOOP / period)  # snapped to whole cycles per loop so the swells meet at the seam
    phase = br.uniform(0, 2 * np.pi, len(segs))

    xs, zs = G.pos[G.path, 0], G.pos[G.path, 2]
    x0, x1 = xs.min(), xs.max()

    def pan_at(p):                          # path index -> left/right as seen from the street
        return 0.85 * (2 * (np.interp(p, np.arange(n), xs) - x0) / (x1 - x0) - 1)

    span = np.array([pan_at(s.mean()) for _, s in segs])

    # control curves at 20 Hz over one loop: the lamplighter's place, and how lit each lantern is
    CR = 20
    tt = np.arange(int(LOOP * CR) + 1) / CR
    lamp = np.array([keys(t, walk) for t in tt])
    lit = np.zeros((len(segs), len(tt)))
    lv = np.zeros(len(segs))
    for rep in range(2):                    # twice round, so the lit levels at the start are those at the end
        for j, p in enumerate(lamp):
            for i, (_, s) in enumerate(segs):
                inside = s.min() - 3 <= p <= s.max() + 3
                lv[i] = min(1.0, lv[i] + 1 / CR / 3) if inside else lv[i] * (1 - 1 / CR / 25)
            lit[:, j] = lv
    breath = np.sin(2 * np.pi * tt[None, :] / period[:, None] + phase[:, None])

    def at(curve, t0, length):              # a control curve (..., len(tt)) sampled per audio sample from t0
        u = np.mod(t0 + np.arange(length) / SR, LOOP)
        if curve.ndim == 1:
            return np.interp(u, tt, curve)
        return np.stack([np.interp(u, tt, c) for c in curve])

    def place(bus, sig, t0, pan, gain=1.0):
        """Add sig at t0 (wrapping round the loop) with a per-sample pan and gain."""
        a = (np.clip(pan, -1, 1) + 1) * np.pi / 4
        sig = sig * gain * np.sqrt(2) * np.stack([np.cos(a), np.sin(a)])
        s = int(round((t0 % LOOP) * SR))
        head = min(sig.shape[1], N - s)
        M.add(bus, sig[:, :head], s / SR)
        if head < sig.shape[1]:
            M.add(bus, sig[:, head:], 0.0)

    def lowpass(bus, fc, order=2):          # zero-phase Butterworth-shaped low-pass over a whole bus
        b = M.buses[bus]['sig']
        f = np.fft.rfftfreq(b.shape[1], 1 / SR)
        h = 1 / np.sqrt(1 + (f / fc) ** (2 * order))
        for c in range(2):
            b[c] = np.fft.irfft(np.fft.rfft(b[c]) * h, b.shape[1])

    def env(length, fade_in, fade_out, hold):   # equal-power fades; zero after hold
        t = np.arange(length) / SR
        e = np.sin(np.pi / 2 * np.clip(t / fade_in, 0, 1))
        e *= np.cos(np.pi / 2 * np.clip((t - (hold - fade_out)) / fade_out, 0, 1))
        return e

    def chord_at(t):
        return int((t % LOOP) // CHORD_LEN) % len(CHORDS)

    scale_pc = [{note(x + '4') % 12 for x in SCALES.get(k, 'D E F G A Bb C').split()} for k in range(len(CHORDS))]
    chord_pc = [{note(x) % 12 for x in c} for c in CHORDS]

    def consonant(k):                       # chord tones and scale notes that are no semitone off a chord tone
        ok = set(chord_pc[k])
        for pc in scale_pc[k]:
            if all(min((pc - c) % 12, (c - pc) % 12) > 1 for c in chord_pc[k]):
                ok.add(pc)
        return ok

    M.bus('choir', gain=0.2, reverb=0.35)
    M.bus('voice', gain=0.17, reverb=0.55)
    M.bus('harp', gain=0.13, reverb=0.5)
    M.bus('drum', gain=0.3, reverb=0.1)

    # ---- the choir: twelve chords crossfading, each pair of voices living in one of the six lanterns ----
    choir = M.synth('Pads/Retro Choir')
    L = CHORD_LEN + 2 * XFADE
    pan_gain = (span + 1) * np.pi / 4
    for k, c in enumerate(CHORDS):
        t0 = k * CHORD_LEN - XFADE
        for half, home in ((c[:2], (2 * k) % 6), (c[2:], (2 * k + 3) % 6)):
            sig = choir.render([(0.0, note(m), 64, L) for m in half], L + 1.5)
            sig *= env(sig.shape[1], 2 * XFADE, 2 * XFADE, L)
            pref = np.full(len(segs), 0.3)
            pref[home] = 1.0
            w = at(pref[:, None] * (1 + 0.15 * breath) * (1 + 0.7 * lit), t0, sig.shape[1]) / 2.2
            gl = (w * np.cos(pan_gain)[:, None]).sum(0) * np.sqrt(2)
            gr = (w * np.sin(pan_gain)[:, None]).sum(0) * np.sqrt(2)
            sig *= np.stack([gl, gr])
            place('choir', sig, t0, np.zeros(sig.shape[1]))
    lowpass('choir', 1800)

    # ---- the procession: one far-off voice that walks with the lamplighter, out and back ----
    voice = M.synth('Pads/Synth Choir MW O-Ah')
    zfar = (zs - zs.min()) / (zs.max() - zs.min())                   # 0 at the back of the house, 1 at the front
    near = 0.55 + 0.45 * np.interp(lamp, np.arange(n), zfar)
    lo, hi = note('A3'), note('D5')
    for w0, w1 in ((20.0, 140.0), (170.0, 290.0)):
        presence = np.sqrt(np.clip(np.sin(np.pi * (tt - w0) / (w1 - w0)), 0, 1)) * ((tt > w0) & (tt < w1))
        t = w0 + 3.0
        cur = int(rng.integers(note('D4'), note('A4') + 1))
        while t < w1 - 8:
            for _ in range(int(rng.integers(3, 6))):                # a phrase of 3-5 long notes
                d = float(rng.uniform(4.5, 8.0))
                if t + d > w1 - 4:
                    break
                ok = consonant(chord_at(t)) & consonant(chord_at(t + d))
                cands = [m for m in range(lo, hi + 1) if m % 12 in ok and 0 < abs(m - cur) <= 5] or [cur]
                wts = np.array([3.0 if m % 12 in chord_pc[chord_at(t)] else 1.0 for m in cands])
                wts /= np.abs(np.array(cands) - cur) + 0.5
                cur = int(rng.choice(cands, p=wts / wts.sum()))
                sig = voice.render([(0.0, cur, 58, d + 1.5)], d + 3.0)
                sig *= env(sig.shape[1], 2.0, 3.0, d + 1.5)
                g = at(presence * near, t, sig.shape[1])
                place('voice', sig, t, 0.9 * at(pan_at(lamp), t, sig.shape[1]), g)
                t += d - 1.0                                          # each note breathes into the next
            t += float(rng.uniform(4.0, 9.0))                         # then a rest
    lowpass('voice', 2200)

    # ---- harp: a slow figure as each lantern is reached, and sparse drips between ----
    harp = M.sampler('Strings/Harp/*.wav')
    entries = []
    for i, (_, s) in enumerate(segs):       # moments the lamplighter steps into a lantern
        inside = (lamp >= s.min() - 3) & (lamp <= s.max() + 3)
        for j in np.nonzero(inside[1:] & ~inside[:-1])[0]:
            entries.append((tt[j + 1], i, lamp[min(len(tt) - 1, j + CR)] > lamp[j]))
    entries.sort()
    for t, i, up in entries:
        k = chord_at(t)
        tones = sorted({note(m) + 12 * o for m in CHORDS[k] for o in (1, 2)})
        tones = [m for m in tones if note('D4') <= m <= note('A5')]
        start = int(rng.integers(0, max(1, len(tones) - 3)))
        run = tones[start:start + 3] if up else tones[start:start + 3][::-1]
        dt = 0
        for q, m in enumerate(run):
            sig = harp.play(m, 52 - 6 * q)
            place('harp', sig, t + dt, np.full(sig.shape[1], span[i]))
            dt += float(rng.uniform(0.45, 0.75))
    busy = [t for t, _, _ in entries]
    t = float(rng.uniform(2, 6))
    while t < LOOP - 1:
        if all(min(abs(t - b), LOOP - abs(t - b)) > 3.0 for b in busy):
            ok = sorted(consonant(chord_at(t)))
            cands = [m for m in range(note('C4'), note('A5') + 1) if m % 12 in ok]
            m = int(rng.choice(cands))
            p = float(np.interp(t, tt, pan_at(lamp))) + float(rng.uniform(-0.25, 0.25)) if rng.random() < 0.6 \
                else float(span[int(rng.integers(len(segs)))])
            sig = harp.play(m, int(rng.integers(26, 46)))
            place('harp', sig, t, np.full(sig.shape[1], p))
            if rng.random() < 0.25:                                   # now and then an answering note, lower
                m2 = max(note('C4'), m - int(rng.choice([3, 4, 5, 7])))
                sig = harp.play(m2 if m2 % 12 in ok else m - 12, int(rng.integers(22, 36)))
                place('harp', sig, t + float(rng.uniform(0.6, 1.4)), np.full(sig.shape[1], p * 0.8))
        t += float(rng.exponential(5.0)) + 2.5
    lowpass('harp', 3500)

    # ---- a muffled drum somewhere along the road, at most every forty seconds or so ----
    hit = M.hits('VSCO 1 Percussion/drums/bass/bdrum_pp*.wav')
    roll = M.hits('VSCO 1 Percussion/drums/bass/bdrum_roll-quietest.wav')
    for t in DRUMS:
        sig = hit.play(int(rng.integers(70, 90)))
        place('drum', sig, t, np.full(sig.shape[1], 0.6 * float(np.interp(t, tt, pan_at(lamp)))))
    for t in ROLLS:
        sig = roll.play(100)
        place('drum', sig, t, np.full(sig.shape[1], 0.6 * float(np.interp(t + 2, tt, pan_at(lamp)))))
    lowpass('drum', 170)
