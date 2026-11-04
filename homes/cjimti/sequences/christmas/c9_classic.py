"""C9 Classic: An old-fashioned string of big C9 bulbs, one every twelve-odd units, set on every
second or third pixel (by each run's spacing) so the string reads as glass bulbs with dark gaps.
Each bulb is a tungsten filament behind painted glass: its own temperature and wear, colour from blackbody light through the glass filter, brightness rising with
roughly the fourth power of temperature. Now and then the furnace kicks on and the whole string sags
warmer and dimmer with filament lag; the odd loose bulb wavers. Seamless for all night."""
import numpy as np
from pixelhome.fx import DT, hexc, perc, smoothstep, lerp, Flicker, nframes, looped

CODE = 'CH09'
TITLE = 'C9 Classic'
KIND = 'ambient'
DESCRIPTION = ('A string of old-fashioned C9 bulbs: warm filaments behind red, green, blue, orange and '
               'yellow glass, each bulb slightly different, the string sagging when the furnace kicks on.')

# painted glass transmission
GLASS = [np.array(c) for c in ((1.0, 0.07, 0.03), (0.12, 0.85, 0.16), (0.14, 0.3, 1.0),
                                (1.0, 0.42, 0.04), (1.0, 0.86, 0.45))]
GLASS_GAIN = np.array([1.0, 1.05, 1.45, 0.95, 0.8])  # blue glass passes little of a warm filament
FLOOR = 0.05
FLOOR_COLOR = hexc('#ff6a18')
LOOP = 150.0
FADE = 12.0                                      # looped()'s crossfade: draw() runs LOOP + FADE seconds
SEED = 29


def blackbody(T):
    """Approximate normalised RGB of a filament at T kelvin (2000..3200)."""
    T = np.asarray(T, float)
    g = np.interp(T, [2000, 2400, 2700, 3000, 3200], [0.45, 0.58, 0.67, 0.74, 0.78])
    b = np.interp(T, [2000, 2400, 2700, 3000, 3200], [0.1, 0.24, 0.36, 0.48, 0.55])
    return np.stack([np.ones_like(T), g, b], -1)


def bulbs(G):
    """Path indices of the bulbs: one every 3rd pixel on the close-spaced runs, every 2nd on Side and Porch
    Right, so every bulb sits on a pixel (no beating against the pixel pitch) at roughly 12-15 units."""
    x = G.pd[G.path]
    bp = []
    for name, pidx in G.path_segments():
        pidx = np.sort(pidx)
        step = 2 if np.diff(x[pidx]).mean() > 5.5 else 3
        bp.extend(pidx[step // 2::step])
    return np.array(bp)


def events(rng, nb, D):
    """The draws draw() makes, in its order: the hum, the furnace sags (start, length), a loose bulb or two
    (bulb, start, length) and how it wavers."""
    hum = Flicker(rng, nb, 0.03, 0.12)
    sags, t = [], rng.uniform(15, 30)
    while t < D:
        sags.append((t, rng.uniform(5, 9)))
        t += rng.uniform(40, 65)
    loose = [(int(rng.integers(nb)), rng.uniform(0, D - 10), rng.uniform(5, 9)) for _ in range(int(D / 30))]
    wob = Flicker(rng, 1, 0.8, 1.6)
    return hum, sags, loose, wob


def render(G, seed=SEED):
    rng = np.random.default_rng(seed)
    n = G.N
    x = G.pd[G.path]
    bp = bulbs(G)
    bx = x[bp]
    nb = len(bx)
    kind = np.arange(nb) % 5
    filt = np.array([GLASS[k] * GLASS_GAIN[k] for k in kind])
    T0 = rng.normal(2650, 70, nb)                    # each filament runs at its own temperature
    wear = rng.uniform(0.85, 1.05, nb)               # blackened glass, thinner filament
    core = np.zeros((n, nb))
    core[bp, np.arange(nb)] = 1.0
    halo = np.zeros((n, nb))
    for o, w in ((-1, 0.14), (1, 0.14)):
        q = np.clip(bp + o, 0, n - 1)
        same = np.abs(x[q] - bx) < 9
        halo[q[same], np.arange(nb)[same]] += w

    def draw(D):
        F = nframes(D)
        out = np.zeros((F, n, 3), np.float32)
        hum, sags, loose, wob = events(rng, nb, D)
        Tf = T0.copy()                               # filament temperature with thermal lag
        for f in range(F):
            t = f * DT
            volt = 1.0
            for ts, dur in sags:
                volt -= 0.06 * smoothstep(ts, ts + 0.8, t) * (1 - smoothstep(ts + dur, ts + dur + 1.5, t))
            target = T0 * volt ** 0.42 * (1 + 0.004 * hum(t))
            for b, ts, dur in loose:
                if ts < t < ts + dur:
                    env = np.sin(np.pi * (t - ts) / dur) ** 2
                    target[b] *= 1 - 0.07 * env * (0.5 + 0.5 * wob(t)[0])
            Tf += (target - Tf) * (1 - np.exp(-DT / 0.12))
            lum = 0.32 * wear * (Tf / 2650) ** 4
            col = blackbody(Tf) * filt
            I = perc(lum)[:, None] * col
            buf = core @ I + halo @ I * 0.35
            out[f][G.path] = buf
        return out
    return looped(draw, LOOP, fade=FADE, floor=(FLOOR, FLOOR_COLOR))


# ---- music: a warm pad in F that changes chord every 18.75 s, the furnace's low hum when the string sags, a
# glassy bell that wavers with each loose bulb, and now and then a music box far off. No beat. ----
MUSIC_SEED = 9
CHORDS = [  # bass, then four upper voices that each move by step
    ('F2', 'A3', 'C4', 'E4', 'G4'), ('D2', 'A3', 'C4', 'E4', 'F4'), ('Bb1', 'A3', 'C4', 'D4', 'F4'),
    ('C2', 'Bb3', 'C4', 'D4', 'F4'), ('A1', 'G3', 'C4', 'E4', 'G4'), ('Bb1', 'G3', 'C4', 'D4', 'F4'),
    ('G1', 'Bb3', 'D4', 'F4', 'A4'), ('C2', 'Bb3', 'C4', 'F4', 'G4'),
]
CHORD_LEN = LOOP / len(CHORDS)
MUSIC_BOX = [(31.0, 2), (66.0, 4), (101.0, 5), (128.0, 0)]   # (start, chord the phrase is drawn from)


def score(M, G):
    import pedalboard as pb
    from pixelhome.audio import SR, note
    rng = np.random.default_rng(SEED)              # the light's draws, in render()'s order
    bp = bulbs(G)
    nb = len(bp)
    rng.normal(2650, 70, nb)
    rng.uniform(0.85, 1.05, nb)
    D = LOOP + FADE
    _, sags, loose, wob = events(rng, nb, D)
    mrng = np.random.default_rng(MUSIC_SEED)
    N = int(LOOP * SR)
    for name, gain, rev in (('pad', 0.39, 0.3), ('hum', 0.5, 0.05), ('glass', 0.3, 0.45), ('box', 0.6, 0.5)):
        M.bus(name, gain=gain, reverb=rev)

    xs = G.pos[G.path, 0]
    x0, x1 = xs.min(), xs.max()
    bx = G.pd[G.path][bp]
    pan_b = lambda b: float(0.85 * (2 * (xs[bp[b]] - x0) / (x1 - x0) - 1))   # a bulb, left/right from the street

    def panned(mono, pan):                  # constant power; pan may be a per-sample array
        a = (np.asarray(pan) + 1) * np.pi / 4
        return np.vstack([mono * np.cos(a), mono * np.sin(a)]) * np.sqrt(2)

    def put(bus, sig, t, gain=1.0):         # add around the loop: whatever passes the end comes in at the start
        s = int(round((t % LOOP) * SR))
        while sig.shape[1]:
            k = min(sig.shape[1], N - s)
            M.add(bus, sig[:, :k], s / SR, gain)
            sig, s = sig[:, k:], 0

    def ramp(k, up):
        u = np.linspace(0, 1, max(k, 1)) if up else np.linspace(1, 0, max(k, 1))
        return np.sin(u * np.pi / 2) ** 2

    # what the lights show at time tau of draw(): looped() fades the last FADE seconds in over the first ones
    CR = 40
    tau = np.arange(int(D * CR)) / CR
    shown = np.where(tau < FADE, tau / FADE, np.where(tau < LOOP, 1.0, 1 - (tau - LOOP) / FADE))

    def fold(ctl):                          # a control curve over draw()'s D seconds -> one loop, as the lights show it
        out = np.zeros(int(LOOP * CR))
        np.add.at(out, np.arange(len(ctl)) % len(out), ctl * shown)
        return out

    def at_rate(ctl, k):                    # one loop's control curve -> k samples, wrapping
        return np.interp(np.arange(k) / SR, np.arange(len(ctl) + 1) / CR, np.append(ctl, ctl[0]))

    def ss(a, b, t):
        u = np.clip((t - a) / (b - a), 0, 1)
        return u * u * (3 - 2 * u)

    sag = fold(sum(ss(ts, ts + 0.8, tau) * (1 - ss(ts + dur, ts + dur + 1.5, tau)) for ts, dur in sags))

    # ---- the pad: each voice glides to its next note over XF seconds, round the loop ----
    pad = np.zeros((2, N), np.float32)
    voices = [(M.synth('Pads/MKS-70 Warm Pad'), 0, 34, 0.7, 0.0), (M.synth('Pads/MKS-70 Warm Pad'), 1, 44, 0.9, -0.4),
              (M.synth('Pads/MKS-70 Warm Pad'), 2, 42, 0.9, 0.3), (M.synth('Pads/MKS-70 Warm Pad'), 3, 40, 0.85, -0.15),
              (M.synth('Keys/House Organ'), 4, 26, 0.3, 0.45)]
    XF = 5.0
    for inst, vi, vel, gain, pan in voices:
        merged = []
        for i, c in enumerate(CHORDS):
            if not merged or merged[-1][1] != c[vi]:
                merged.append((i * CHORD_LEN + 0.6 * vi, c[vi]))
        if len(merged) > 1 and merged[0][1] == merged[-1][1]:   # the same note across the seam: one long note
            merged[0] = (merged[-1][0], merged[0][1])
            merged.pop()
        for i, (t, m) in enumerate(merged):
            dur = (merged[(i + 1) % len(merged)][0] - t) % LOOP or LOOP
            length = dur + XF
            a = inst.render([(0.0, note(m), vel, length)], length + 0.5).astype(np.float32)
            k, f = a.shape[1], int(XF * SR)
            env = np.ones(k, np.float32)
            env[:f] = ramp(f, True)
            e = int(length * SR)
            env[e - f:e] = ramp(f, False)
            env[e:] = 0
            idx = (int(round(((t - XF / 2) % LOOP) * SR)) + np.arange(k)) % N
            pad[:, idx] += panned(a.mean(0) * env * gain, pan)
    pad *= (1 - 0.3 * at_rate(sag, N)).astype(np.float32)           # the string sags, the pad sinks with it
    M.add('pad', pad, 0.0)
    del pad

    # ---- the furnace: a low, soft hum under the house while it runs ----
    air = mrng.normal(0, 1, (1, N)).astype(np.float32)
    air = pb.Pedalboard([pb.LowpassFilter(160), pb.LowpassFilter(220), pb.HighpassFilter(45)])(
        np.concatenate([air, air], 1), SR)[0, N:]                    # filtered twice round, so it wraps cleanly
    hum = air / (np.abs(air).max() + 1e-9)
    ctl = np.convolve(np.concatenate([sag[-80:], sag, sag[:80]]), np.hanning(81) / np.hanning(81).sum(), 'same')[80:-80]
    M.add('hum', panned(hum * at_rate(ctl, N), 0.0), 0.0, 0.2)

    # ---- a loose bulb: a soft glass bell on the bulb, wavering as it does ----
    bell = M.synth('Pads/Bell Pad')
    for b, ts, dur in loose:
        c = CHORDS[int(((ts + dur / 2) % LOOP) // CHORD_LEN)]
        m = note(c[1 + b % 4]) + 12
        a = bell.render([(0.0, m, 60, dur)], dur + 3.0).mean(0)
        tt = np.arange(len(a)) / SR
        env = np.where(tt < dur, np.sin(np.pi * np.clip(tt / dur, 0, 1)) ** 2, 0)
        wv = 0.5 + 0.5 * np.array([wob(ts + q)[0] for q in np.arange(0, len(a) / SR, 1 / CR)])
        w = np.interp(tt, np.arange(len(wv)) / CR, wv)
        vis = np.interp(ts + tt, tau, shown)
        sig = a * np.sqrt(env) * (0.55 + 0.45 * w) * vis
        sig[int(dur * SR):] *= np.exp(-np.arange(len(a) - int(dur * SR)) / SR / 0.8)
        put('glass', panned(sig, pan_b(b)), ts, 0.8)

    # ---- far off, a music box: a few slow notes from the chord of the moment ----
    box = M.synth('Plucks/Magic Music Box')
    soften = pb.Pedalboard([pb.LowpassFilter(3000), pb.HighpassFilter(200)])
    for t0, ci in MUSIC_BOX:
        c = CHORDS[ci]
        pool = [note(q) + 12 for q in c[1:]]
        k = int(mrng.integers(4, 7))
        gaps = mrng.uniform(0.8, 1.4, k) * (1 + 0.15 * np.arange(k))
        times = np.concatenate([[0], np.cumsum(gaps[:-1])])
        notes = [(float(t), pool[int(j)], int(mrng.integers(50, 68)), 0.6)
                 for t, j in zip(times, mrng.permutation(len(pool) * 2)[:k] % len(pool))]
        span = float(times[-1]) + 5.0
        a = soften(box.render(notes, span).astype(np.float32), SR)
        put('box', panned(a.mean(0), pan_b(int(mrng.integers(nb)))), t0)
