"""Amber Waves: The whole roofline is a strip of wheat field, simulated as a damped wave equation along
the path. Slow gusts of wind push across it; the stalks bend and spring back, and the bending travels
on as waves that turn the corners, bounce back from the two free ends and pass through each other.
Each run of the roof carries waves at its own speed, so a little of every wave reflects at each corner.
Stalks leaning one way catch the low gold light, leaning the other way they fall into amber shadow."""
import numpy as np
from pixelhome.fx import DT, hexc, light, Flicker, nframes, looped

CODE = 'TG10'
TITLE = 'Amber Waves'
KIND = 'ambient'
DESCRIPTION = ('The roof is a strip of wheat field. Slow gusts bend it, and the bending rolls on as waves that turn '
               'the corners, echo off the free ends and cross each other, gold on one side, amber shadow on the other.')

GOLD = hexc('#ffb428')
AMBER = hexc('#ff6a10')
SHADE = hexc('#8a2a06')
FLOOR_COLOR = hexc('#a03008')
FLOOR = 0.11
LOOP = 170.0


BOUNDS = [0, 491, 894, 1311, 1660, 2033]  # the runs of the roof along the path
SPEEDS = [120, 95, 135, 105, 140, 100]    # wave speed on each (impedance steps at the corners)


def _field(G, rng, Dt):
    """The wheat field render() draws: its shimmer, its gusts, and a generator of (t, bend u, speed v) per frame,
    on a grid of cells 5 apart along the path (the arrays are updated in place)."""
    dx = 5.0
    xs = np.arange(0, G.length + dx, dx)
    M = len(xs)
    bounds = BOUNDS + [G.length + 10]
    c = np.zeros(M)
    for (a, b), s in zip(zip(bounds[:-1], bounds[1:]), SPEEDS):
        c[(xs >= a) & (xs < b)] = s
    c = np.convolve(np.pad(c, 3, mode='edge'), np.ones(7) / 7, 'valid')   # soften the steps a little
    SUB = 4
    dt = DT / SUB
    gamma = 0.12
    shimmer = Flicker(rng, G.N, 0.05, 0.25)
    gusts = []
    t = 0.0
    while t < Dt:
        d = rng.choice([-1, 1])
        gusts.append((t, rng.uniform(0, G.length), d, rng.uniform(60, 110), rng.uniform(0.5, 1.0),
                      rng.uniform(5, 9)))
        t += rng.uniform(5, 11)

    def frames():
        u = np.zeros(M)
        v = np.zeros(M)
        for f in range(nframes(Dt)):
            t = f * DT
            force = np.zeros(M)
            for tg, x0, d, sp, a, life in gusts:
                s = t - tg
                if 0 < s < life:
                    env = np.sin(np.pi * s / life) ** 2
                    q = (xs - x0 - d * sp * s) / 140
                    force += a * env * (np.exp(-q ** 2) - 1.6 * q * np.exp(-q ** 2) * d) * 0.8
            for _ in range(SUB):
                lap = np.empty(M)
                lap[1:-1] = u[2:] - 2 * u[1:-1] + u[:-2]
                lap[0] = 2 * (u[1] - u[0])                 # free ends: waves reflect
                lap[-1] = 2 * (u[-2] - u[-1])
                acc = (c ** 2) * lap / dx ** 2 - gamma * v - 0.05 * u + 2.2 * force
                v += acc * dt
                u += v * dt
            yield t, u, v
    return xs, shimmer, gusts, frames()


def render(G, seed=30):
    rng = np.random.default_rng(seed)
    pdp = G.pd[G.path]
    n = G.N

    def draw(Dt):
        out = np.zeros((nframes(Dt), n, 3), np.float32)
        xs, shimmer, _, field = _field(G, rng, Dt)
        for f, (t, u, _) in enumerate(field):
            w = np.interp(pdp, xs, u)
            lean = np.tanh(w * 1.1)
            I = 0.24 + 0.14 * lean + 0.02 * shimmer(t)
            hi = np.clip(lean, 0, 1)[:, None]
            lo = np.clip(-lean, 0, 1)[:, None]
            col = AMBER + (GOLD - AMBER) * hi + (SHADE - AMBER) * lo * 0.7
            out[f][G.path] = light(1.0, np.clip(I, 0.05, 0.42)) * col
        return out
    return looped(draw, LOOP, floor=(FLOOR, FLOOR_COLOR))


# ---- music: an all-night loop, wind over the wheat ----
# A reed drone holds an open fifth on D the whole night, with a soft pad above it drifting through four modal
# colours (D mixolydian). The wind is two layers of noise from the same simulation the lights use: a low breath
# that follows each gust along the house, and a dry rustle on every run of the roof that rises and falls with
# how much the stalks there are moving. Far off, a violin section bows a slow line of long notes that climbs
# when the field is restless and sinks back when it is calm.

MUSIC_SEED = 47
LOOP_FADE = 12.0                    # looped()'s default head/tail blend
COLOURS = ((0.0, ('A3', 'D4')), (42.0, ('B3', 'E4')), (85.0, ('C4', 'G4')), (128.0, ('A3', 'F#4')))
FIDDLE = ('A3', 'B3', 'D4', 'E4', 'F#4', 'G4', 'A4', 'B4')   # its notes, low to high


def score(M, G):
    import pedalboard as pb
    from pixelhome.audio import SR, note
    rng = np.random.default_rng(MUSIC_SEED)
    N = int(LOOP * SR)
    for name, gain, rev in (('drone', 0.65, 0.3), ('wind', 0.13, 0.1), ('rustle', 0.065, 0.12), ('fiddle', 0.2, 0.6)):
        M.bus(name, gain=gain, reverb=rev)

    xs = G.pos[G.path, 0]
    x0, x1 = xs.min(), xs.max()
    pdp = G.pd[G.path]

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

    def at_rate(ctl, rate, n):              # control signal -> sample rate
        return np.interp(np.arange(n) / SR, np.arange(len(ctl)) / rate, ctl)

    def ring(chain, seed):                  # filtered noise one loop long whose end runs on into its start
        X = 2 * SR
        x = np.random.default_rng(seed).normal(0, 1, (1, N + X)).astype(np.float32)
        x = chain(x, SR)[0]
        x[:X] = x[:X] * np.sqrt(np.linspace(0, 1, X)) + x[N:] * np.sqrt(np.linspace(1, 0, X))
        return x[:N] / np.abs(x[:N]).max()

    def smooth(ctl, k):                     # round the loop
        h = np.hanning(2 * k + 1)
        return np.convolve(np.concatenate([ctl[-k:], ctl, ctl[:k]]), h / h.sum(), 'same')[k:-k]

    # ---- the field, run as render() runs it, and blended over the seam the way looped() blends the frames ----
    CR = 40
    cells, _, gusts, field = _field(G, np.random.default_rng(30), LOOP + LOOP_FADE)
    zone = np.digitize(cells, BOUNDS) - 1
    stir = []
    for _, u, v in field:
        stir.append([np.abs(v[zone == k]).mean() for k in range(len(BOUNDS))])
    stir = np.array(stir).T
    T = np.arange(stir.shape[1]) / CR
    push = np.zeros((2, len(T)))            # the gusts: how hard, and where (weighted)
    for tg, x0g, d, sp, a, life in gusts:
        s = T - tg
        on = (s > 0) & (s < life)
        e = np.where(on, a * np.sin(np.pi * np.clip(s / life, 0, 1)) ** 2, 0)
        push[0] += e
        push[1] += e * pan_pd(np.clip(x0g + d * sp * s, 0, G.length))
    n0, c = int(LOOP * CR), int(LOOP_FADE * CR)
    w = np.linspace(0, 1, c, endpoint=False)

    def seam(ctl):
        return np.concatenate([ctl[..., :c] * w + ctl[..., n0:n0 + c] * (1 - w), ctl[..., c:n0]], -1)

    stir = seam(stir)
    gust = seam(push[0])
    gust_pan = seam(push[1]) / (gust + 1e-6)
    gust_pan = smooth(np.where(gust > 0.02, gust_pan, 0.0), 40)

    # ---- the rustle: dry stalks on each run of the roof, as loud as they are moving ----
    rustle = np.zeros((2, N))
    for k in range(len(BOUNDS)):
        mid = np.mean(cells[zone == k])
        lvl = smooth(np.clip(stir[k] / 1.3, 0, 1) ** 1.6, 12)
        x = ring(pb.Pedalboard([pb.HighpassFilter(700), pb.LowpassFilter(2600), pb.LowpassFilter(3400)]), MUSIC_SEED + k)
        rustle += panned(x * at_rate(0.06 + 0.94 * lvl, CR, N), float(pan_pd(mid)))
    M.add('rustle', rustle, 0.0)
    del rustle

    # ---- the wind: a low breath that follows each gust along the house ----
    g = smooth(np.clip(gust, 0, 1.4) / 1.4, 20)
    for k, (sp, lo) in enumerate(((-0.15, 380.0), (0.15, 460.0))):
        x = ring(pb.Pedalboard([pb.HighpassFilter(110), pb.LowpassFilter(lo), pb.LowpassFilter(lo * 1.5),
                                pb.LadderFilter(pb.LadderFilter.Mode.BPF12, cutoff_hz=lo * 0.8, resonance=0.2)]),
                 MUSIC_SEED * 10 + k)
        M.add('wind', panned(x * at_rate(0.2 + 0.8 * g, CR, N), np.clip(at_rate(gust_pan, CR, N) + sp, -1, 1)), 0.0)

    # ---- the drone: an open fifth all night, and a pad drifting through four modal colours above it ----
    drone = np.zeros((2, N), np.float32)
    XF = 8.0

    def hold(inst, m, on, dur, vel, gain, pan):
        length = dur + XF
        a = inst.render([(0.0, note(m), vel, length)], length + 0.5).mean(0).astype(np.float32)
        k, f = len(a), int(XF * SR)
        env = np.ones(k, np.float32)
        env[:f] = ramp(f, True)
        e = int(length * SR)
        env[e - f:e] = ramp(f, False)
        env[e:] = 0
        idx = (int(round(((on - XF / 2) % LOOP) * SR)) + np.arange(k)) % N
        drone[:, idx] += panned(a * env * gain, pan)

    low = M.synth('Winds/Low')
    hold(low, 'D2', 0.0, LOOP, 40, 0.8, -0.2)
    hold(low, 'A2', 0.0, LOOP, 36, 0.7, 0.2)
    pad = M.synth('Pads/Still')
    for j, (t, dyad) in enumerate(COLOURS):
        dur = (COLOURS[(j + 1) % len(COLOURS)][0] - t) % LOOP
        for m, p, lag in zip(dyad, (-0.45, 0.45), (0.0, 4.0)):
            hold(pad, m, t + lag, dur, 42, 0.6, p)
    M.add('drone', drone, 0.0)
    del drone

    # ---- the fiddle: long notes that climb when the field is restless and sink when it calms ----
    violin = M.sampler('Strings/Violin Section/susVib/*.wav', tune=-12)
    restless = smooth(stir.mean(0), 240)
    lo, hi = np.percentile(restless, 10), np.percentile(restless, 90)
    soften = pb.Pedalboard([pb.LowpassFilter(2000), pb.HighpassFilter(200)])
    i, t = 2, 3.0
    while t < LOOP - 4:
        want = int(round(np.clip((restless[int(t * CR)] - lo) / (hi - lo), 0, 1) * (len(FIDDLE) - 1)))
        step = int(np.sign(want - i)) or int(rng.choice([-1, 1]))
        i = int(np.clip(i + step, 0, len(FIDDLE) - 1))
        a = violin.play(note(FIDDLE[i]), int(rng.integers(40, 56)), dur=8.5, release=2.5)
        f = int(2.0 * SR)
        a[:, :f] *= ramp(f, True)
        a = soften(a.astype(np.float32), SR).mean(0)
        put('fiddle', panned(a, float(rng.uniform(-0.3, 0.3))), t)
        t += float(rng.uniform(7.5, 9.5)) * (1.6 if rng.random() < 0.2 else 1.0)   # now and then a breath
