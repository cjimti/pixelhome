"""Night Watch: The Watcher, asleep. Half-closed red eyes drift and slowly blink; now and then they open,
look around the street, and settle back. The mouth smoulders; the rest of the house is candlelight."""
import numpy as np
from pixelhome.fx import DT, hexc, perc, smoothstep, keys, lerp, nframes, looped, candle_bed

CODE = 'NT4'
TITLE = 'Night Watch'
KIND = 'ambient'
DESCRIPTION = 'The Watcher asleep. Half-closed eyes drift and blink, and three times a loop they open and look around.'

EMBER_RED = hexc('#ff0800')
DEEP_ORANGE = hexc('#ff2800')
ORANGE = hexc('#ff4a00')
FLOOR_COLOR = hexc('#ff4a08')
FLOOR = 0.13
LOOP = 300.0


def render(G, seed=14):
    rng = np.random.default_rng(seed)
    eyes = [(G.seg['Left'], G.span_u(G.seg['Left'])), (G.seg['Right'], G.span_u(G.seg['Right']))]
    M, uM = G.seg['Porch Front'], G.span_u(G.seg['Porch Front'])
    O = np.concatenate([G.seg['Side'], G.seg['Porch Left'], G.seg['Porch Right']])
    teeth = (1 - np.abs(2 * (((uM + 1) / 2 * 9) % 1) - 1)) ** 1.3

    def draw(D):
        out = np.zeros((nframes(D), G.N, 3), np.float32)
        bed = candle_bed(rng, G.N, 0.2)
        gaze_keys, t = [(0, 0.0)], 0.0
        while t < D:
            t += rng.uniform(12, 28)
            gaze_keys += [(t, gaze_keys[-1][1]), (t + rng.uniform(3, 6), float(rng.uniform(-0.8, 0.8)))]
        blinks = np.cumsum(rng.uniform(22, 45, int(D / 20)))
        wakes = [w for w in (70.0, 165.0, 250.0) if w < D]
        for f in range(len(out)):
            t = f * DT
            fr = out[f]
            o = 0.22
            for w in wakes:
                o += keys(t, [(w, 0), (w + 5, 0.55), (w + 16, 0.55), (w + 23, 0)])
            o *= 1 - max([0.0] + [float(smoothstep(0.9, 0, abs(t - b))) for b in blinks])
            gaze = keys(t, gaze_keys)
            for w in wakes:
                if w + 5 < t < w + 16:
                    gaze = lerp(gaze, 0.7 * np.sin(2 * np.pi * (t - w - 5) / 11), smoothstep(w + 5, w + 7, t) *
                                (1 - smoothstep(w + 14, w + 16, t)))
            I = bed(t)
            fr[O] = perc(I[O])[:, None] * DEEP_ORANGE
            for idx, u in eyes:
                lid = np.clip((o - np.abs(u)) / 0.3, 0, 1)
                pupil = np.clip((np.abs(u - gaze * 0.5) - 0.05) / 0.05, 0, 1)
                e = 0.36 * lid * (0.6 + 0.4 * (1 - u ** 2)) * (0.15 + 0.85 * pupil)
                fr[idx] = perc(np.maximum(I[idx] * 0.75, e))[:, None] * lerp(DEEP_ORANGE, EMBER_RED, lid[:, None])
            m = 0.18 + 0.1 * teeth * (1 + 0.25 * np.sin(2 * np.pi * t / 9))
            fr[M] = perc(np.maximum(I[M] * 0.8, m))[:, None] * lerp(EMBER_RED, ORANGE, teeth[:, None])
        return out
    return looped(draw, LOOP, floor=(FLOOR, FLOOR_COLOR))


# Music: the house asleep in the wind. A dark pad walks slowly through D minor and its shadows (Bb, G minor,
# a Phrygian Eb, C minor, back through A) and breathes with the mouth's smoulder; soft wind rises and
# falls and leans toward wherever the eyes are looking. Each time the eyes open (render()'s wakes) a far-off
# horn rises out of the dark with them, turns its head with the gaze, and sinks back as the lids close; a
# tower bell tolls across the fields once the Watcher has settled. Between wakes it only stirs: one low
# muted horn note in each long sleep, a lone toll now and then.
WAKES = (70.0, 165.0, 250.0)           # as in render(): eyes open over 5 s, look round for 11, close by +23
LOOK = 11.0                            # one sweep of the gaze while awake
MOUTH = LOOP / 33                      # the mouth's 9 s smoulder, rounded so the loop holds a whole number
FADE = 12.0                            # looped()'s default blend

CHORDS = [                             # (start s, sounding notes): one chord every half minute or so
    (5, ('D2', 'A2', 'E3', 'F3')),       # starts a little in, so the seam falls inside a held chord
    (38, ('Bb1', 'F2', 'A2', 'D3')),
    (66, ('G1', 'D2', 'A2', 'Bb2')),
    (100, ('F1', 'C2', 'A2', 'D3')),
    (132, ('Eb2', 'Bb2', 'D3', 'G3')),
    (160, ('C2', 'G2', 'D3', 'Eb3')),
    (194, ('D2', 'F2', 'Bb2', 'F3')),
    (222, ('A1', 'E2', 'G2', 'D3')),
    (246, ('A1', 'E2', 'A2', 'C#3')),
    (262, ('D2', 'G2', 'Bb2', 'D3')),
]
HORN = {                               # per wake: (offset from the wake, note, length, level); legato, overlapping
    70.0: [(-1.5, 'D3', 4.5, 0.5), (2.0, 'A3', 5.5, 0.8), (7.0, 'Bb3', 3.8, 1.0), (10.3, 'A3', 5.0, 0.9),
           (14.8, 'F3', 4.2, 0.7), (18.5, 'D3', 6.5, 0.5)],
    165.0: [(-1.5, 'F3', 4.5, 0.5), (2.0, 'C4', 5.5, 0.8), (7.0, 'D4', 3.6, 0.95), (10.0, 'C4', 3.0, 0.85),
            (12.5, 'Bb3', 4.6, 0.8), (16.5, 'G3', 4.2, 0.65), (20.0, 'F3', 7.0, 0.45)],
    250.0: [(-1.5, 'A2', 3.6, 0.5), (1.5, 'E3', 3.6, 0.7), (4.5, 'A3', 6.0, 1.0), (10.0, 'G3', 4.6, 0.85),
            (14.0, 'F3', 4.0, 0.7), (17.5, 'E3', 3.0, 0.6), (20.0, 'D3', 7.5, 0.45)],
}
STIRS = [(118.0, 'A2', 9.0), (212.0, 'D3', 9.0), (24.0, 'F2', 8.0)]    # (t, note, length): muted horn in its sleep
TOLLS = [(32.0, 'D3', 52), (97.0, 'A2', 60), (105.0, 'D3', 50), (148.0, 'F3', 44), (193.0, 'D3', 48),
         (236.0, 'A2', 46), (278.0, 'D3', 60), (286.5, 'A2', 50)]      # (t, note, velocity): the far tower
TOWER = -0.55                          # the bell's across the fields to the left


def _gaze(G, step=0.1):
    """render()'s gaze, -1 left .. 1 right, sampled every `step` s over the loop and blended at the seam the way
    looped() blends the lights (same seed, same draws)."""
    rng = np.random.default_rng(14)
    D = LOOP + FADE
    candle_bed(rng, G.N, 0.2)
    gk, t = [(0, 0.0)], 0.0
    while t < D:
        t += rng.uniform(12, 28)
        gk += [(t, gk[-1][1]), (t + rng.uniform(3, 6), float(rng.uniform(-0.8, 0.8)))]

    def g(t):
        v = float(keys(t, gk))
        for w in WAKES:
            if w + 5 < t < w + 16:
                v = lerp(v, 0.7 * np.sin(2 * np.pi * (t - w - 5) / LOOK),
                         float(smoothstep(w + 5, w + 7, t) * (1 - smoothstep(w + 14, w + 16, t))))
        return v

    ts = np.arange(0, LOOP, step)
    out = np.array([g(t) for t in ts])
    head = ts < FADE
    out[head] = out[head] * (ts[head] / FADE) + np.array([g(t + LOOP) for t in ts[head]]) * (1 - ts[head] / FADE)
    return ts, out


def _periodic(rng, n, kmax, sr, power=1.0):
    """Smooth random curve 0..1 over n samples that wraps exactly (whole cycles per loop only)."""
    t = np.arange(n) / n
    y = np.zeros(n)
    for k in range(1, kmax + 1):
        y += np.sin(2 * np.pi * k * t + rng.uniform(0, 2 * np.pi)) / k ** power
    return (y - y.min()) / (y.max() - y.min())


def _lowpass(sig, fc, order=2):
    """Zero-phase low-pass by FFT (padded so nothing wraps)."""
    from pixelhome.audio import SR
    n = sig.shape[-1]
    m = n + SR
    X = np.fft.rfft(sig, m)
    f = np.fft.rfftfreq(m, 1 / SR)
    return np.fft.irfft(X / np.sqrt(1 + (f / fc) ** (2 * order)), m)[..., :n]


def _swell(sig, length, attack, release, sr):
    """Shape a sustained sample: raised-cosine attack, hold, raised-cosine release; cut after."""
    n = min(sig.shape[1], int((length + release) * sr))
    t = np.arange(n) / sr
    env = np.where(t < attack, 0.5 - 0.5 * np.cos(np.pi * np.clip(t / attack, 0, 1)), 1.0)
    env *= np.where(t > length, 0.5 + 0.5 * np.cos(np.pi * np.clip((t - length) / release, 0, 1)), 1.0)
    return sig[:, :n] * env


def score(M, G):
    from pixelhome.audio import SR, note
    rng = np.random.default_rng(41)
    n = int(LOOP * SR)
    for name, gain, rev in (('wind', 1.35, 0.12), ('pad', 0.36, 0.3), ('horn', 0.31, 0.55), ('stir', 0.24, 0.6),
                            ('bell', 0.6, 0.7)):
        M.bus(name, gain=gain, reverb=rev)
    ts, gaze = _gaze(G)
    gaze_at = lambda t: float(np.interp(t % LOOP, ts, gaze))

    # ---- wind: noise shaped in the frequency domain (so it wraps), three bands faded by slow gusts ----
    t = np.arange(n) / SR
    f = np.fft.rfftfreq(n, 1 / SR)
    lift = np.zeros(n)                          # the wind picks up a little while the eyes are open
    for w in WAKES:
        lift += np.interp(t, [w - 2, w + 6, w + 16, w + 28], [0, 1, 1, 0], left=0, right=0)
    lift = 0.5 - 0.5 * np.cos(np.pi * lift)
    pan = np.interp(t, ts, gaze) * 0.7
    a = (pan + 1) * np.pi / 4
    gl, gr = np.cos(a) * np.sqrt(2), np.sin(a) * np.sqrt(2)
    wind = np.zeros((2, n))
    for fc, width, lvl, kmax, wide in ((260, 0.9, 1.0, 14, True), (520, 0.6, 0.7, 18, True),
                                       (1050, 0.25, 0.35, 22, False)):
        shape = np.exp(-0.5 * (np.log2(np.maximum(f, 1) / fc) / width) ** 2)
        gust = 0.2 + 0.8 * _periodic(rng, n, kmax, SR) ** 2
        gust *= 1 + 0.5 * lift * (fc > 400)
        if wide:
            for c in range(2):
                x = np.fft.irfft(np.fft.rfft(rng.normal(0, 1, n)) * shape, n)
                wind[c] += lvl * gust * x / x.std()
        else:                                   # the whistling band leans toward the gaze
            x = np.fft.irfft(np.fft.rfft(rng.normal(0, 1, n)) * shape, n)
            x = lvl * gust * x / x.std()
            wind += np.vstack([x * gl, x * gr])
    M.add('wind', wind * 0.02, 0.0)
    del wind, x

    # ---- the pad: a slow walk of chords, breathing with the mouth ----
    pad = M.synth('Pads/MKS-70 Warm Pad')
    notes = []
    for i, (t0, ch) in enumerate(CHORDS):
        t1 = CHORDS[i + 1][0] if i + 1 < len(CHORDS) else LOOP + CHORDS[0][0]
        for j, m in enumerate(ch):
            notes.append((t0 + 0.4 * j, note(m), 52 - 3 * j, t1 - t0 + 3.0))
    sig = pad.render(notes, LOOP + M.TAIL)
    tt = np.arange(sig.shape[1]) / SR
    sig *= 1 + 0.12 * np.sin(2 * np.pi * tt / MOUTH)
    M.add('pad', sig, 0.0)

    # ---- the horn: rises with the eyes, turns with the gaze, sinks as they close ----
    horn = M.sampler('Brass/F Horn/sus/*.wav', tune=-12)
    for w, phrase in HORN.items():
        for k, (dt, m, length, lvl) in enumerate(phrase):
            t0 = w + dt
            att = 3.0 if k == 0 else 1.6
            rel = 4.0 if k == len(phrase) - 1 else 2.2
            s = _swell(horn.play(note(m), 40), length, att, rel, SR)
            M.add('horn', _lowpass(s, 1800), t0, lvl, 0.6 * gaze_at(t0 + length / 2))
    mute = M.sampler('Brass/F Horn/mute/*.wav', tune=-12)
    for t0, m, length in STIRS:
        s = _swell(mute.play(note(m), 36), length, 4.0, 4.0, SR)
        M.add('stir', _lowpass(s, 1400), t0, 1.0, 0.0)

    # ---- the tower bell, heard a long way off ----
    bell = M.sampler('Percussion/TB_hit*.wav')
    for t0, m, v in TOLLS:
        s = bell.play(note(m), v, dur=16.0, release=5.0)
        s[:, :int(0.06 * SR)] *= np.linspace(0, 1, int(0.06 * SR)) ** 2     # no clang: blunted by the distance
        M.add('bell', _lowpass(s, 1200, order=3), t0, 1.0, TOWER)
