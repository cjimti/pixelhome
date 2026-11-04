"""First Snow: Flakes fall through 3-D space onto the roofline. Each one glints as it drifts down past
the line and, if it lands on the roof, adds to the snow lying at that spot; the snow settles, creeps
a little and drifts deeper into the corners. Now and then the cornice at one of the two free ends
gives way and slides off the end of the roof. Dim, slow and seamless for all night."""
import numpy as np
from pixelhome.fx import DT, hexc, perc, light, smoothstep, lerp, Flicker, nframes, looped

CODE = 'XM07'
TITLE = 'First Snow'
KIND = 'ambient'
DESCRIPTION = ('Snow falls through the air past the roofline and settles on it, drifting into the corners. '
               'Now and then the snow at a free end slides off the edge.')

NIGHT = hexc('#0a1850')
SNOW = hexc('#c8d8ff')
SNOW_DEEP = hexc('#e8eeff')
FLAKE = hexc('#f0f4ff')
FLOOR = 0.1
LOOP = 150.0
FADE = 12.0                                              # looped()'s head/tail blend
SEED = 27
SLIDE = 3.2                                              # seconds a cornice takes to go over the edge


def _slides(rng, D):
    """(time, end) of each cornice slide; they alternate ends (0: back of Side, 1: end of Right)."""
    slides, t = [], rng.uniform(18, 30)
    end = int(rng.integers(2))
    while t < D:
        slides.append((t, end))
        end = 1 - end
        t += rng.uniform(24, 36)
    return slides


def wind(t):
    return 14 * np.sin(2 * np.pi * t / 47) + 8 * np.sin(2 * np.pi * t / 19 + 1)


def squall(t):
    return 0.25 + 1.5 * np.sin(np.pi * t / LOOP) ** 2      # heavy, then a lull; one cycle per loop


def render(G, seed=SEED):
    return _render(G, seed)


def _render(G, seed, events=None):
    """render(); with events (a dict), also records the slides and every flake that settles on the roof."""
    rng = np.random.default_rng(seed)
    Pp = G.pos[G.path]                                   # positions in path order
    x = G.pd[G.path]
    n = G.N
    Ltr = G.length
    corners = np.array([(x[i] + x[i + 1]) / 2 for i in (80, 178, 260, 331, 380)])
    catch = 1 + 0.9 * np.exp(-((x[:, None] - corners[None]) / 35) ** 2).sum(1)   # eddies pile snow
    catch *= 1.25 - 0.25 * np.clip(np.minimum(x, Ltr - x) / 150, 0, 1)          # cornices build at the ends
    tex = 1 + 0.12 * Flicker(rng, n, 0.01, 0.04)(0.0)

    def draw(D):
        out = np.zeros((nframes(D), G.N, 3), np.float32)
        K = 260
        fp = np.zeros((K, 3))
        fv = rng.uniform(26, 42, K)
        fph = rng.uniform(0, 2 * np.pi, (K, 2))
        fsw = rng.uniform(0.2, 0.5, K)
        TAU = 160.0                                      # slow settling / sublimation
        RATE = 0.0045                                    # depth per second per pixel, before catch
        depth = RATE * TAU * catch * (0.8 + 0.2 * tex)
        depth = np.minimum(depth, 1.0)
        tw = Flicker(rng, n, 0.05, 0.25)

        def respawn(k, y0=None):
            j = rng.integers(n)
            fp[k] = Pp[j] + np.array([rng.normal(0, 30), 0, rng.normal(0, 30)])
            fp[k, 1] = rng.uniform(170, 420) if y0 is None else y0

        for k in range(K):
            respawn(k)
        # slides: each takes the snow in the last stretch over the edge
        slides = _slides(rng, D)
        if events is not None:
            events['slides'] = slides
            events['land'] = []
        slab, prev = {}, {}

        for f in range(len(out)):
            t = f * DT
            # flakes fall, sway and drift with the wind
            w = wind(t)
            fp[:, 1] -= fv * DT
            fp[:, 0] += (w + 12 * np.sin(2 * np.pi * fsw * t + fph[:, 0])) * DT
            fp[:, 2] += 10 * np.sin(2 * np.pi * fsw * t * 0.8 + fph[:, 1]) * DT
            near = fp[:, 1] < 200
            glow = np.zeros(n)
            if near.any():
                q = fp[near]
                d = np.linalg.norm(Pp[None] - q[:, None], axis=2)
                a = smoothstep(200, 155, q[:, 1])
                glow = (a[:, None] * np.exp(-(d / 7) ** 2)).max(0)
            landed = np.nonzero(fp[:, 1] <= 150)[0]
            sq = squall(t)
            for k in landed:
                dxz = np.hypot(Pp[:, 0] - fp[k, 0], Pp[:, 2] - fp[k, 2])
                j = int(np.argmin(dxz))
                if dxz[j] < 12:
                    splat = np.exp(-((x - x[j]) / 7) ** 2)
                    depth += 0.15 * sq * catch[j] * splat / 2.2
                    if events is not None:
                        events['land'].append((t, x[j], sq * catch[j]))
                respawn(k, rng.uniform(380, 440))
            depth *= np.exp(-DT / TAU)
            depth = np.minimum(depth, 1.15)
            # a little creep: snow levels itself out
            depth[1:-1] += 0.02 * (depth[2:] - 2 * depth[1:-1] + depth[:-2])

            # cornice slides at the free ends: the last stretch of snow accelerates over the edge
            slide_glint = np.zeros(n)
            for k, (ts, e) in enumerate(slides):
                u = t - ts
                if 0 <= u < SLIDE:
                    from_end = x if e == 0 else Ltr - x
                    order = np.argsort(from_end)
                    zone = smoothstep(150, 120, from_end)    # the slab breaks along a crack line
                    if k not in slab:
                        slab[k] = depth * zone
                        prev[k] = slab[k]
                    s = 10 * u + 22 * u ** 2                # it creeps, then rushes over the edge
                    moved = np.interp(from_end + s, from_end[order], slab[k][order], right=0)
                    moved *= smoothstep(0, 6, from_end)     # what passes the end is gone
                    depth = np.clip(depth - prev[k], 0, None) + moved
                    prev[k] = moved
                    slide_glint += moved * (0.5 + 0.5 * np.sin(from_end * 0.5 + 20 * u))

            I = 0.06 + 0.3 * np.clip(depth, 0, 1.0) ** 1.4 * (1 + 0.06 * tw(t))
            col = lerp(SNOW, SNOW_DEEP, np.clip(depth - 0.6, 0, 0.5)[:, None] * 2)
            buf = perc(I)[:, None] * col + light(NIGHT, np.full(n, 0.08))
            buf += light(FLAKE, 0.3 * glow + 0.16 * slide_glint)
            out[f][G.path] = buf
        return out
    return looped(draw, LOOP, FADE, floor=(FLOOR, NIGHT))


# ---- music: an all-night loop, hushed and wintry, in D ----
# A soft pad holds one chord at a time and moves on, a voice at a time, each time a cornice slides off: the snow
# shifts and so does the harmony. Every few flakes that settle on the roof ring a tiny music-box note where they land
# (low at the back of the Side, rising toward the end of Right), more of them as the squall thickens and fewer in the
# lull, always from the chord of the moment. A breath of wind drifts across the speakers with the wind that carries
# the flakes, and each slide is a hush of snow that creeps, rushes and drops off the end it falls from.

MUSIC_SEED = 71
CHORDS = {                          # chord brought by the slide at each time: bass, low, three pad voices
    0: ('G1', 'D2', 'F#3', 'B3', 'D4'),         # G maj7
    1: ('B1', 'F#2', 'A3', 'D4', 'E4'),         # B minor 11
    2: ('E2', 'B2', 'G3', 'D4', 'F#4'),         # E minor 9
    3: ('A1', 'E2', 'G3', 'D4', 'E4'),          # A sus4, 7
    4: ('D2', 'A2', 'F#3', 'C#4', 'E4'),        # D maj9, which holds over the seam
}


def _light_events(G):
    """The slides and the flakes that settle, from render() itself, folded into the loop as looped() folds
    the frames: (time in the loop, weight, ...), the weight being how much of that moment reaches the loop."""
    ev = {}
    _render(G, SEED, ev)

    def fold(t):
        if t < FADE:
            return t, t / FADE
        if t >= LOOP:
            return t - LOOP, 1 - (t - LOOP) / FADE
        return t, 1.0
    slides = [(*fold(t), e) for t, e in ev['slides']]
    land = [(*fold(t), p, a) for t, p, a in ev['land']]
    return slides, land


def score(M, G):
    import pedalboard as pb
    from pixelhome.audio import SR, note
    rng = np.random.default_rng(MUSIC_SEED)
    N = int(LOOP * SR)
    for name, gain, rev in (('pad', 0.36, 0.3), ('flakes', 0.055, 0.6), ('air', 0.3, 0.15), ('slide', 0.4, 0.3)):
        M.bus(name, gain=0.88 * gain, reverb=rev)

    xs = G.pos[G.path, 0]
    x0, x1 = xs.min(), xs.max()
    pdp = G.pd[G.path]
    slides, land = _light_events(G)

    def pan_pd(p):                          # distance along the path -> left/right from the street
        return 0.85 * (2 * (np.interp(p, pdp, xs) - x0) / (x1 - x0) - 1)

    def panned(mono, pan):                  # constant power; pan may be a per-sample array
        a = (np.asarray(pan) + 1) * np.pi / 4
        return np.vstack([mono * np.cos(a), mono * np.sin(a)]) * np.sqrt(2)

    def put(bus, sig, t, gain=1.0):         # add around the loop: whatever passes the end comes in at the start
        s = int(round((t % LOOP) * SR))
        while sig.shape[1]:
            k = min(sig.shape[1], N - s)
            M.add(bus, sig[:, :k], s / SR, gain)
            sig, s = sig[:, k:], 0

    def ramp(n, up):
        u = np.linspace(0, 1, max(n, 1)) if up else np.linspace(1, 0, max(n, 1))
        return np.sin(u * np.pi / 2) ** 2

    def noise(seconds, lo, seed):           # soft band of noise, filtered so it never hisses
        a = np.random.default_rng(seed).normal(0, 1, (1, int(seconds * SR))).astype(np.float32)
        a = pb.Pedalboard([pb.HighpassFilter(lo * 0.3), pb.LowpassFilter(lo), pb.LowpassFilter(lo * 1.4)])(a, SR)[0]
        return a / (np.abs(a).max() + 1e-9)

    # which chord sounds when: each slide brings the next one
    starts = sorted((t, CHORDS[k]) for k, (t, w, e) in enumerate(sorted(slides)) if w > 0)

    def chord_at(t):
        cur = starts[-1][1]
        for s0, c in starts:
            if s0 <= t:
                cur = c
        return cur

    # ---- the pad: each voice changes note on its own, staggered after the slide that brings a new chord ----
    pad = np.zeros((2, N), np.float32)
    voices = [
        (M.synth('Pads/MKS-70 Warm Pad'), 0, 34, 0.55, 0.0, 0.0),   # (instrument, voice, velocity, gain, pan, lag)
        (M.synth('Pads/MKS-70 Warm Pad'), 1, 42, 0.8, -0.3, 4.0),
        (M.synth('Pads/MKS-70 Warm Pad'), 2, 44, 0.9, 0.35, 1.5),
        (M.synth('Pads/MKS-70 Warm Pad'), 3, 42, 0.9, -0.45, 6.5),
        (M.synth('Pads/MKS-70 Warm Pad'), 4, 38, 0.8, 0.45, 9.0),
    ]
    XF = 7.0                                # seconds each note change takes
    for inst, vi, vel, gain, pan, lag in voices:
        merged = []
        for t, m in ((s0 + lag, c[vi]) for s0, c in starts):
            if not merged or merged[-1][1] != m:
                merged.append((t, m))
        if len(merged) > 1 and merged[0][1] == merged[-1][1]:   # same note across the seam: one long note
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
    # the pad fills out a little with the squall (one cycle per loop, so it meets itself at the seam)
    tt = np.arange(N) / SR
    pad *= (0.8 + 0.2 * (squall(tt) - 0.25) / 1.5).astype(np.float32)
    M.add('pad', pad, 0.0)
    del pad

    # ---- the flakes: a few of those that settle ring a note where they land ----
    box = M.synth('Plucks/Magic Music Box')
    soften = pb.Pedalboard([pb.LowpassFilter(3200), pb.HighpassFilter(300)])
    notes = []
    for t, w, p, amount in land:
        if rng.random() < w * min(0.2, 0.05 + 0.03 * amount):
            pcs = sorted({note(m) % 12 for m in chord_at(t)[1:]})
            tones = [m for m in range(note('C5'), note('B6')) if m % 12 in pcs]
            m = tones[int(np.clip(p / G.length, 0, 0.999) * len(tones))]
            notes.append((t, m, int(rng.integers(26, 46)), float(pan_pd(p))))
    for t, m, vel, pan in notes:
        a = box.render([(0.0, m, vel, 0.3)], 4.0).astype(np.float32)
        a = soften(a, SR).mean(0)
        put('flakes', panned(a / (np.abs(a).max() + 1e-9), pan), t, vel / 46)

    # ---- the wind: air across the speakers as the flakes drift, folded into the loop as the lights are ----
    CR = 40
    T = np.arange(int((LOOP + FADE) * CR)) / CR
    wv = wind(T)
    level = 0.35 + 0.65 * np.abs(wv) / 22
    pan = 0.6 * np.clip(wv / 22, -1, 1)
    n, c = int(LOOP * CR), int(FADE * CR)
    wgt = np.linspace(0, 1, c, endpoint=False)
    for ctl in (level, pan):
        ctl[:c] = ctl[:c] * wgt + ctl[n:n + c] * (1 - wgt)
    lvl = np.interp(tt, T[:n], level[:n], period=LOOP)
    pn = np.interp(tt, T[:n], pan[:n], period=LOOP)
    XS = 3.0                                # the noise itself crossfades over the seam
    air = noise(LOOP + XS, 700, MUSIC_SEED + 1)
    xs_n = int(XS * SR)
    air[:xs_n] *= np.sin(np.linspace(0, np.pi / 2, xs_n))
    air[N:] *= np.cos(np.linspace(0, np.pi / 2, xs_n))
    air[:xs_n] += air[N:]
    air = air[:N]
    M.add('air', panned(air * lvl, pn), 0.0, 0.25)

    # ---- the slides: a hush of snow that creeps, rushes and drops off the end ----
    chimes = M.hits('VSCO 1 Percussion/varMetal/various/windchimes_slowDesc1.wav')
    for k, (t, w, e) in enumerate(slides):
        if w <= 0:
            continue
        p = float(pan_pd(0.0 if e == 0 else G.length))
        n_s = int((SLIDE + 1.0) * SR)
        u = np.arange(n_s) / SR
        speed = np.where(u < SLIDE, (10 + 44 * u) / (10 + 44 * SLIDE), 0)
        env = np.convolve(speed, np.hanning(int(0.4 * SR)) / np.hanning(int(0.4 * SR)).sum(), 'same')
        hush = noise((SLIDE + 1.0), 900, MUSIC_SEED + 10 + k) * env
        put('slide', panned(hush, p), t, 0.5 * w)
        drop = t + (-10 + np.sqrt(100 + 4 * 22 * 120)) / 44      # the slab passes the edge (s = 120)
        thud = noise(1.2, 220, MUSIC_SEED + 20 + k) * np.exp(-np.arange(int(1.2 * SR)) / SR / 0.18)
        thud[:int(0.02 * SR)] *= np.linspace(0, 1, int(0.02 * SR))
        put('slide', panned(thud, p), drop, 0.6 * w)
        put('slide', panned(chimes.play(50).mean(0), p), t + 0.3, 0.18 * w)
