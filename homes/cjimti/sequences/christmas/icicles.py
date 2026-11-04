"""Icicles: Icicles hang along the three front runs (both wing fronts and the porch front). A slow
temperature field drifts across the house: where it thaws, meltwater creeps along the eave towards
each icicle, the tip swells into a drop and lets go, and the icicle shortens; where it freezes the
icicles grow longer, bluer and brighter and catch the odd crystal glint. The ends and porch sides
hold a frosty glow. Dim, slow and seamless for all night."""
import numpy as np
from pixelhome.fx import DT, hexc, perc, light, smoothstep, lerp, Flicker, nframes, looped

CODE = 'CH08'
TITLE = 'Icicles'
KIND = 'ambient'
DESCRIPTION = ('Icicles along the wing and porch fronts grow in the cold, then drip as a slow thaw drifts '
               'across the house: meltwater creeps to each tip, swells and falls.')

FROST = hexc('#1838a0')
ICE = hexc('#6fa0ff')
ICE_WHITE = hexc('#d8ecff')
DROP = hexc('#f0f8ff')
FLOOR = 0.1
LOOP = 160.0


SEED = 28
LOOP_FADE = 12.0                    # looped()'s default head/tail blend


def _sites(G, rng):
    """Where the icicles hang: along the three front runs, 13-26 units apart."""
    x = G.pd[G.path]
    seg = G.seg_of[G.path]
    sites = []
    for name in ('Left', 'Porch Front', 'Right'):
        xs = x[seg == name]
        p = xs.min() + rng.uniform(4, 10)
        while p < xs.max() - 4:
            sites.append(p)
            p += rng.uniform(13, 26)
    return np.array(sites)


def temp(t, p):
    """Temperature (thaw > 0) at path position p; periodic in the loop length."""
    w = 2 * np.pi * t / LOOP
    return 0.75 * np.sin(2 * w - p / 520 + 0.4) + 0.35 * np.sin(w + p / 330 + 2.0)


def _icicles(G, rng, sites, D):
    """The icicles frame by frame over D seconds: yields (t, ln, sw, after, glint, fell, glinted, frost, shimmer):
    lengths, each drip's swell 0..1, the flash after a drop falls, crystal glints, which drops fell and which glints
    started this frame, and the two flickers the drawing uses (made here to keep render()'s random draws in order)."""
    n, m = G.N, len(sites)
    ln = rng.uniform(0.2, 0.7, m)
    drip_t = np.full(m, -99.0)                 # start of the current drip's swell
    swell = rng.uniform(2.0, 3.5, m)
    glint_t = np.full(m, -99.0)
    frost = Flicker(rng, n, 0.03, 0.15)
    shimmer = Flicker(rng, m, 0.05, 0.2)
    for f in range(nframes(D)):
        t = f * DT
        T = temp(t, sites)
        thaw = np.clip(T, 0, None)
        cold = np.clip(-T, 0, None)
        ln = np.clip(ln + DT * 0.016 * cold, 0.08, 1.0)
        # drips start at a rate that rises with the thaw; a new one only after the last fell
        age = t - drip_t
        idle = age > swell + 1.2
        start = idle & (rng.random(m) < DT * 0.4 * thaw)
        drip_t[start] = t
        swell[start] = rng.uniform(2.0, 3.5, start.sum())
        age = t - drip_t
        fell = (age >= swell) & (age - DT < swell)
        ln[fell] = np.clip(ln[fell] - 0.07, 0.08, 1.0)
        sw = np.where(age < swell, smoothstep(0, 1, np.clip(age / swell, 0, 1)) ** 2, 0.0)
        after = np.where((age >= swell) & (age < swell + 0.6), np.exp(-(age - swell) / 0.12), 0.0)
        # crystal glints in the cold
        g = (glint_t < t - 4) & (rng.random(m) < DT * 0.05 * cold)
        glint_t[g] = t
        ga = t - glint_t
        glint = np.where(ga < 1.2, np.sin(np.pi * np.clip(ga / 1.2, 0, 1)) ** 2, 0.0)
        yield t, ln, sw, after, glint, fell, g, frost, shimmer


def render(G, seed=SEED):
    rng = np.random.default_rng(seed)
    n = G.N
    x = G.pd[G.path]
    seg = G.seg_of[G.path]
    front = np.isin(seg, ['Left', 'Right', 'Porch Front'])
    sites = _sites(G, rng)

    def draw(D):
        out = np.zeros((nframes(D), n, 3), np.float32)
        dx = x[:, None] - sites[None]
        near = np.abs(dx) < 30
        for f, (t, ln, sw, after, glint, _, _, frost, shimmer) in enumerate(_icicles(G, rng, sites, D)):
            # each icicle: a point that is brighter, wider and whiter the longer it is
            core = 0.08 + 0.24 * ln + 0.04 * shimmer(t) * ln
            core = core + 0.08 * sw + 0.1 * after + 0.08 * glint
            width = 1.4 + 5.0 * ln
            kern = np.where(near, np.exp(-(dx / width[None]) ** 2), 0)
            I_ice = (kern * core[None]).max(1)
            whiten = np.clip((kern * (ln + 0.6 * sw + glint)[None]).max(1), 0, 1)
            # meltwater creeping along the eave toward a swelling tip, from both sides
            run = np.zeros(n)
            active = sw > 0
            if active.any():
                k = np.nonzero(active)[0]
                for side in (-1, 1):
                    pos = sites[k] + side * 12 * (1 - sw[k])
                    run = np.maximum(run, ((np.exp(-((x[:, None] - pos[None]) / 2.0) ** 2) *
                                            (0.1 * np.sin(np.pi * sw[k]))[None]) * near[:, k]).max(1))
            base = np.where(front, 0.075, 0.12) * (1 + 0.12 * frost(t))
            buf = light(FROST, base)
            buf += perc(I_ice)[:, None] * lerp(ICE, ICE_WHITE, whiten[:, None]) * front[:, None]
            buf += light(DROP, run) * front[:, None]
            out[f][G.path] = buf
        return out
    return looped(draw, LOOP, floor=(FLOOR, FROST))


# ---- music: an all-night loop, soft and cold ----
# Two slow pads hold a chord in D that moves every twenty seconds, eight chords round the loop: a glassy one
# where the house is freezing and a warm one where it thaws, each in three places across the speakers (Left wing,
# porch, Right wing) and swelling with the temperature there, so the thaw is heard drifting across the house.
# Every drop that falls is a small water plip with a soft harp note, each icicle tuned to its own note of the D
# pentatonic, louder the longer it is; every crystal glint in the cold is a faint glockenspiel note, high and far.

MUSIC_SEED = 128
PAD_CHORDS = (                      # one every 20 s from t = 0
    ('D3', 'A3', 'C#4', 'E4', 'F#4'),       # D maj9
    ('B2', 'F#3', 'A3', 'C#4', 'D4'),       # Bm9
    ('G2', 'D3', 'F#3', 'A3', 'B3'),        # G maj9
    ('E2', 'B2', 'D3', 'F#3', 'G3'),        # Em9
    ('F#2', 'C#3', 'E3', 'A3', 'D4'),       # D/F#, open
    ('G2', 'D3', 'F#3', 'B3', 'C#4'),       # G maj7#11
    ('A2', 'E3', 'G3', 'B3', 'D4'),         # A9sus4
    ('A2', 'E3', 'G3', 'C#4', 'F#4'),       # A13, back to D
)
DROP_NOTES = ('A4', 'B4', 'D5', 'E5', 'F#5', 'A5', 'B5')
GLINT_NOTES = ('A5', 'B5', 'D6', 'E6')
REGIONS = (('Left', -0.6), ('Porch Front', 0.0), ('Right', 0.6))


def _light_events(G):
    """Replay render()'s icicles (the same random draws) over the loop and its blend: the sites, each drop that
    falls (t, site, length) and each glint (t, site)."""
    rng = np.random.default_rng(SEED)
    sites = _sites(G, rng)
    falls, glints = [], []
    for t, ln, sw, after, glint, fell, g, _, _ in _icicles(G, rng, sites, LOOP + LOOP_FADE):
        falls += [(t, k, ln[k]) for k in np.nonzero(fell)[0]]
        glints += [(t, k) for k in np.nonzero(g)[0]]
    return sites, falls, glints


def _shown(T):
    """How much of render time T reaches the loop (looped() blends 160..172 s into the first 12 s)."""
    if T < LOOP_FADE:
        return T / LOOP_FADE
    if T < LOOP:
        return 1.0
    return max(0.0, 1 - (T - LOOP) / LOOP_FADE)


def score(M, G):
    import pedalboard as pb
    from pixelhome.audio import SR, note
    rng = np.random.default_rng(MUSIC_SEED)
    N = int(LOOP * SR)
    for name, gain, rev in (('pad', 0.13, 0.35), ('drops', 0.36, 0.5), ('glints', 0.8, 0.7)):
        M.bus(name, gain=gain, reverb=rev)

    xs = G.pos[G.path, 0]
    x0, x1 = xs.min(), xs.max()
    pdp = G.pd[G.path]
    seg = G.seg_of[G.path]

    def pan_pd(p):                          # distance along the path -> left/right from the street
        return float(0.85 * (2 * (np.interp(p, pdp, xs) - x0) / (x1 - x0) - 1))

    def panned(mono, pan):
        a = (np.asarray(pan) + 1) * np.pi / 4
        return np.vstack([mono * np.cos(a), mono * np.sin(a)]) * np.sqrt(2)

    def put(bus, sig, t, gain=1.0):         # add around the loop: whatever passes the end comes in at the start
        s = int(round((t % LOOP) * SR))
        while sig.shape[1]:
            k = min(sig.shape[1], N - s)
            M.add(bus, sig[:, :k], s / SR, gain)
            sig, s = sig[:, k:], 0

    sites, falls, glints = _light_events(G)

    # ---- the pads: a chord every 20 s, crossfaded over 8 s, rendered once per instrument round the loop ----
    STEP, XF = LOOP / len(PAD_CHORDS), 8.0

    def pad_loop(inst, vel, octave):
        buf = np.zeros(N, np.float32)
        length = STEP + XF
        for i, chord in enumerate(PAD_CHORDS):
            a = inst.render([(0.0, note(m) + octave, vel, length) for m in chord], length + 0.2).mean(0)
            k = a.size
            env = np.ones(k, np.float32)
            f, e = int(XF * SR), int(length * SR)
            ramp = np.sin(np.linspace(0, np.pi / 2, f)) ** 2
            env[:f] = ramp
            env[e - f:e] = ramp[::-1]
            env[e:] = 0
            idx = (int(round((i * STEP - XF / 2) * SR)) % N + np.arange(k)) % N
            np.add.at(buf, idx, a * env)
        return buf
    ice = pad_loop(M.synth('Pads/Still'), 52, 12)
    warm = pad_loop(M.synth('Pads/MKS-70 Warm Pad'), 50, 0)
    soften = pb.Pedalboard([pb.LowpassFilter(3500), pb.HighpassFilter(90)])
    ice = soften(np.concatenate([ice, ice])[None], SR)[0][N:]    # filtered twice round, so the seam is continuous
    # the temperature in each region, round the loop (periodic, so the swell crosses the seam)
    CR = 20
    tc = np.arange(int(LOOP * CR)) / CR
    sig = np.zeros((2, N), np.float32)
    ts = np.arange(N) / SR
    for name, pan in REGIONS:
        on = pdp[seg == name]
        pr = sites[(sites >= on.min()) & (sites <= on.max())]
        T = np.array([temp(t, pr).mean() for t in tc])
        cold = np.interp(ts, tc, 0.3 + 0.7 * np.clip(-T, 0, 1), period=LOOP)
        thaw = np.interp(ts, tc, 0.3 + 0.7 * np.clip(T, 0, 1), period=LOOP)
        sig += panned(ice * cold * 0.8 + warm * thaw, pan)
    M.add('pad', sig, 0.0)
    del sig, ice, warm

    # ---- the drops: a plip of water and a harp note, each icicle on its own note ----
    harp = M.sampler('Strings/Harp/*.wav')
    tuned = [note(DROP_NOTES[(3 * k) % len(DROP_NOTES)]) for k in range(len(sites))]

    def plip(f0, seed):
        r = np.random.default_rng(seed)
        tt = np.arange(int(0.09 * SR)) / SR
        fr = f0 * (1 + 0.7 * tt / tt[-1]) * r.uniform(0.95, 1.05)
        x = np.sin(2 * np.pi * np.cumsum(fr) / SR) * np.exp(-tt / 0.02) * np.clip(tt / 0.002, 0, 1)
        return x
    drop_soft = pb.Pedalboard([pb.LowpassFilter(2600)])
    for i, (T, k, ln) in enumerate(falls):
        w = _shown(T)
        if w <= 0:
            continue
        t = T if T < LOOP else T - LOOP
        pan = pan_pd(sites[k])
        g = w * (0.35 + 0.65 * ln)
        p = plip(float(rng.uniform(900, 1500)), MUSIC_SEED + i)
        put('drops', panned(p, pan), t, 0.25 * g)
        h = harp.play(tuned[k], int(30 + 30 * ln), dur=2.5, release=0.8)
        h = drop_soft(h.astype(np.float32), SR)
        put('drops', panned(h.mean(0), pan), t, 0.6 * g)

    # ---- the glints: a faint glockenspiel note as each crystal catches the light, at its brightest ----
    glock = M.sampler('Percussion/Glock/*.wav', tune=-12)
    for T, k in glints:
        w = _shown(T + 0.6)
        if w <= 0:
            continue
        t = (T + 0.6) % LOOP if T + 0.6 >= LOOP else T + 0.6
        m = note(GLINT_NOTES[int(rng.integers(len(GLINT_NOTES)))])
        a = glock.play(m, int(rng.integers(28, 40))).astype(np.float32)
        a = drop_soft(a, SR)
        put('glints', panned(a.mean(0), pan_pd(sites[k])), t, w)
