"""Daylight: A mild sunny day on the roofline, from breakfast until the evening lights take over. The house
sits under a pale blue sky; soft warm-white clouds, made from a few broad waves of light, drift across the
yard from left to right and change shape as they go. A golden glint of sun wanders along the runs, out over
the porch and back along the wings, dimming a little whenever a cloud passes over it. Every motion repeats
exactly once per loop, so the end flows into the start. A seamless all-day loop."""
import numpy as np
from pixelhome.fx import DT, hexc, light, lerp, smoothstep, nframes, looped

CODE = 'DY01'
TITLE = 'Daylight'
KIND = 'ambient'
DESCRIPTION = ('A pale blue sky along the roofline with soft white clouds drifting across the yard and a golden '
               'glint of sun wandering over the porch and the wings. Gentle light for the daytime.')

SKY = hexc('#3e9cff')
SKY_PALE = hexc('#9ed2ff')
CLOUD = hexc('#fff1dc')
GOLD = hexc('#ffb83a')
GOLD_CORE = hexc('#ffe39a')
LOOP = 150.0
WIND = 24.0                     # cloud drift across the yard, layout units per second
FLOOR = 0.12


def glint_path(t):
    """Where the sun glint sits along the path (G.pd) at time t: out over the porch and back, twice a loop
    in a lazy figure. Periodic in LOOP and never far onto Side."""
    w = 2 * np.pi * np.asarray(t, float) / LOOP
    return 1300 + 720 * np.sin(w) + 190 * np.sin(3 * w + 0.8) + 60 * np.sin(5 * w + 2.1)


def _cloud_waves(rng):
    """Plane waves over the yard (x, z) that drift with the wind and repeat exactly once per loop."""
    K = 7
    m = rng.choice(np.arange(3, 11), K, replace=False)          # cycles per loop of each wave
    kx = 2 * np.pi * m / (LOOP * WIND)                          # so kx * WIND * LOOP is a whole number of turns
    kz = rng.normal(0, 1, K) * kx * 0.8
    a = rng.uniform(0.6, 1.0, K)
    ph = rng.uniform(0, 2 * np.pi, K)
    m2 = rng.choice(np.arange(1, 4), K)                         # slow change of shape as they drift
    ph2 = rng.uniform(0, 2 * np.pi, K)
    return kx, kz, a, ph, m2, ph2


def render(G, seed=1):
    rng = np.random.default_rng(seed)
    x, z = G.pos[:, 0], G.pos[:, 2]
    pd = G.pd
    kx, kz, a, ph, m2, ph2 = _cloud_waves(rng)
    tint = np.clip(0.5 + 0.5 * np.sin(2 * np.pi * (x - x.min()) / 900 + rng.uniform(0, 6)), 0, 1)
    tint = 0.35 + 0.4 * tint + 0.25 * smoothstep(-300, -600, z)      # the porch, set back, looks a paler blue

    def draw(D):
        out = np.zeros((nframes(D), G.N, 3), np.float32)
        for f in range(len(out)):
            t = f * DT
            w = 2 * np.pi * t / LOOP
            amp = a * (0.75 + 0.25 * np.sin(m2 * w + ph2))
            arg = kx[None, :] * (x[:, None] - WIND * t) + kz[None, :] * z[:, None] + ph[None, :]
            n = (amp * np.cos(arg)).sum(1) / np.sqrt((amp ** 2).sum() * 2)
            c = smoothstep(-0.05, 0.85, n)                                  # 0 clear sky .. 1 inside a cloud
            sky = lerp(SKY, SKY_PALE, tint[:, None])
            col = light(lerp(sky, CLOUD, c[:, None]), 0.17 + 0.17 * c)
            s = glint_path(t)
            d = pd - s
            shade = 1 - 0.45 * np.interp(s, pd[G.path], c[G.path])         # a cloud over the sun dims it
            core = np.exp(-(d / 34) ** 2)
            halo = np.exp(-(d / 150) ** 2)
            g = shade * (0.9 + 0.1 * np.sin(2 * np.pi * 0.35 * t + 0.01 * pd))   # a slow shimmer, not a flicker
            glow = np.clip(g * (0.65 * halo + 0.35 * core), 0, 1)
            col = col * (1 - 0.6 * glow[:, None])
            col += light(lerp(GOLD, GOLD_CORE, core[:, None]), 0.42 * glow)
            out[f] = col
        return out
    return looped(draw, LOOP, floor=(FLOOR, SKY))


# ---- music: an all-day loop, sunny and soft ----
# Eight slow chords in D major, one every 18.75 s, held by a warm pad with a viola section swelling in on each
# change. A harp picks the chord out unhurried, never on a strict pulse, panned slowly across the house. Four
# times a loop a flute plays a short phrase from wherever the sun glint is; each time the glint turns a corner
# of the roof a glockenspiel chimes once from that corner.

MUSIC_SEED = 7
CHORD_LEN = LOOP / 8
CHORDS = (                     # (bass, three pad voices, harp tones)
    ('D2', ('A3', 'D4', 'F#4'), ('D3', 'A3', 'D4', 'E4', 'F#4', 'A4')),           # D(add9)
    ('B1', ('G3', 'B3', 'D4'), ('B2', 'G3', 'D4', 'G4', 'A4', 'B4')),             # G/B
    ('E2', ('G3', 'B3', 'D4'), ('E3', 'B3', 'D4', 'G4', 'B4')),                   # Em7
    ('A1', ('A3', 'C#4', 'E4'), ('A2', 'E3', 'A3', 'C#4', 'E4', 'A4')),           # A
    ('B1', ('A3', 'D4', 'F#4'), ('B2', 'F#3', 'A3', 'D4', 'F#4')),                # Bm7
    ('G1', ('B3', 'D4', 'F#4'), ('G2', 'D3', 'B3', 'D4', 'F#4', 'A4')),           # Gmaj7(9)
    ('E2', ('G3', 'B3', 'F#4'), ('E3', 'B3', 'D4', 'F#4', 'G4')),                 # Em9
    ('A1', ('A3', 'D4', 'E4'), ('A2', 'E3', 'A3', 'D4', 'E4')),                   # Asus4
)
FLUTE = (                      # (start, [(note, seconds), ...]), each inside one chord
    (5.0, (('F#5', 2.0), ('E5', 1.0), ('D5', 1.5), ('E5', 1.0), ('F#5', 1.5), ('A5', 3.5))),
    (42.5, (('G5', 2.0), ('F#5', 1.0), ('E5', 1.5), ('D5', 1.0), ('B4', 2.0), ('D5', 1.0), ('E5', 3.5))),
    (80.0, (('F#5', 1.5), ('D5', 1.0), ('B4', 1.5), ('A4', 1.0), ('B4', 1.5), ('D5', 1.0), ('F#5', 1.5),
            ('E5', 1.0), ('D5', 2.5))),
    (117.5, (('B4', 1.5), ('D5', 1.0), ('E5', 1.5), ('F#5', 2.0), ('G5', 1.0), ('F#5', 1.5), ('E5', 3.5))),
)
CHIME = ('A5', 'D6', 'F#5', 'E6', 'B5')                     # glock note at each corner, Side|Left .. Porch Right|Right


def _corner_turns(G):
    """(time, corner) each time the glint passes a corner of the roof, from glint_path()."""
    starts = [G.pd[G.path[idx[0]]] for _, idx in G.path_segments()][1:]
    t = np.arange(int(LOOP / DT)) * DT
    s = glint_path(t)
    s2 = glint_path(t + DT)
    turns = []
    for i, c in enumerate(starts):
        hit = np.nonzero((s - c) * (s2 - c) < 0)[0]
        turns += [(float(t[h]), i) for h in hit]
    return sorted(turns)


def score(M, G):
    import pedalboard as pb
    from pixelhome.audio import SR, note
    rng = np.random.default_rng(MUSIC_SEED)
    N = int(LOOP * SR)
    for name, gain, rev in (('pad', 0.16, 0.3), ('strings', 0.17, 0.35), ('harp', 0.27, 0.35),
                            ('flute', 0.21, 0.4), ('glock', 0.11, 0.5)):
        M.bus(name, gain=gain, reverb=rev)

    xs = G.pos[G.path, 0]
    x0, x1 = xs.min(), xs.max()
    pdp = G.pd[G.path]

    def pan_pd(p):
        return 0.8 * (2 * (np.interp(p, pdp, xs) - x0) / (x1 - x0) - 1)

    def panned(mono, pan):
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

    def held(sig, length, xf):              # fade a rendered note in over xf and out over xf ending at length
        k, f, e = sig.shape[-1], int(xf * SR), int(length * SR)
        env = np.ones(k, np.float32)
        env[:f] = ramp(f, True)
        env[max(0, e - f):e] = ramp(min(f, e), False)
        env[e:] = 0
        return sig * env

    # ---- pad: each chord held, crossfading into the next; the bass a touch softer ----
    XF = 5.0
    pads = [(M.synth('Pads/MKS-70 Warm Pad'), v, vel, g, pan) for v, vel, g, pan in
            ((0, 40, 0.7, 0.0), (1, 44, 0.9, -0.35), (2, 42, 0.9, 0.35), (3, 40, 0.8, 0.0))]
    for inst, v, vel, g, pan in pads:
        for i, (bass, voices, _) in enumerate(CHORDS):
            m = bass if v == 0 else voices[v - 1]
            length = CHORD_LEN + XF
            a = inst.render([(0.0, note(m), vel, length)], length + 1.0).mean(0)
            put('pad', panned(held(a, length, XF), pan), i * CHORD_LEN - XF / 2, g)

    # ---- strings: a viola section swells in on each chord change and fades ----
    viola = M.sampler('Strings/Viola Section/susvib/*.wav', tune=-12)
    for i, (_, voices, _) in enumerate(CHORDS):
        m = voices[1]
        a = viola.play(note(m), 56, dur=8.0, release=2.5).mean(0)
        a = a * ramp(a.shape[0], True) ** 0.5
        put('strings', panned(a, -0.2 + 0.4 * (i % 2)), i * CHORD_LEN + 0.5)

    # ---- harp: the chord picked out up and down, rubato, with breaths ----
    harp = M.sampler('Strings/Harp/*.wav')
    soften = pb.Pedalboard([pb.LowpassFilter(3500)])
    t = 0.4
    step = 0
    while t < LOOP - 0.3:
        tones = CHORDS[int(t // CHORD_LEN)][2]
        cyc = list(tones) + list(tones[-2:0:-1])
        if rng.random() > 0.18:
            m = cyc[step % len(cyc)]
            a = harp.play(note(m), int(rng.integers(44, 66)), dur=4.5, release=1.5)
            a = soften(a.astype(np.float32), SR).mean(0)
            put('harp', panned(a, 0.5 * np.sin(2 * np.pi * t / 37)), t)
        step += 1
        t += rng.uniform(0.62, 0.95) * (1.6 if step % 11 == 0 else 1.0)

    # ---- flute: phrases from wherever the sun glint is ----
    flute = M.sampler('Woodwinds/Flute/susNV/*.wav', tune=-12)
    for t0, phrase in FLUTE:
        t = t0
        for m, d in phrase:
            a = flute.play(note(m), int(rng.integers(52, 68)), dur=d + 0.15, release=0.7).mean(0)
            k = min(a.shape[0], int(0.12 * SR))
            a[:k] *= ramp(k, True)
            put('flute', panned(a, float(pan_pd(glint_path(t)))), t)
            t += d

    # ---- glock: one chime each time the glint turns a corner ----
    glock = M.sampler('Percussion/Glock/*.wav', tune=-12)
    corners = [G.pd[G.path[idx[0]]] for _, idx in G.path_segments()][1:]
    for t, i in _corner_turns(G):
        a = glock.play(note(CHIME[i]), int(rng.integers(40, 56)), dur=5.0, release=2.0).mean(0)
        put('glock', panned(a, float(pan_pd(corners[i]))), t)
