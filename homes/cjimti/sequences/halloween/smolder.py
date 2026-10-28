"""Smolder: Slow lava. Heat crawls through each roof section in its own direction, like coals breathing;
rare pixels pop orange and fade."""
import numpy as np
from pixelhome.fx import DT, hexc, perc, smoothstep, lerp, smooth_noise, nframes, looped

CODE = 'NT5'
TITLE = 'Smolder'
KIND = 'ambient'
DESCRIPTION = 'Slow lava crawling through each roof section in its own direction, with the odd orange pop.'
VOICEOVER = 'Deep in the roof, something is still burning. Slow, and red, and patient.'

EMBER_RED = hexc('#ff0800')
ORANGE = hexc('#ff4a00')
FLOOR_COLOR = hexc('#ff4a08')
FLOOR = 0.13
LOOP = 300.0


def render(G, seed=15):
    rng = np.random.default_rng(seed)
    segs = G.path_segments()

    def draw(D):
        n = G.N
        out = np.zeros((nframes(D), n, 3), np.float32)
        idx = np.arange(n, dtype=float)
        flow = np.empty(n)
        local = np.empty(n)
        for i, (_, s) in enumerate(segs):
            flow[s] = (1 if i % 2 else -1) * rng.uniform(1.5, 3.5)
            local[s] = idx[s] - s.min()
        k = rng.uniform(0.04, 0.12, 4)
        w = rng.uniform(0.15, 0.5, 4)
        ph = rng.uniform(0, 2 * np.pi, 4)
        drift = smooth_noise(rng, idx, 40)
        P = int(D * 1.5)
        pt, pp = rng.uniform(-3, D, P), rng.integers(0, n, P)
        for f in range(len(out)):
            t = f * DT
            x = local + flow * t
            heat = sum(np.sin(k[j] * x + w[j] * t * 0.3 + ph[j] + 2 * drift) for j in range(4)) / 4
            heat = 0.5 + 0.5 * heat
            I = 0.17 + 0.17 * heat ** 1.5
            u = t - pt
            live = (u > 0) & (u < 3)
            pop = np.zeros(n)
            np.maximum.at(pop, pp[live], 0.4 * np.where(u[live] < 0.6, smoothstep(0, 0.6, u[live]),
                                                         1 - smoothstep(0.6, 3, u[live])))
            I = np.maximum(I, pop)
            col = lerp(EMBER_RED, ORANGE, smoothstep(0.17, 0.36, I)[:, None])
            out[f][G.path] = perc(I)[:, None] * col
        return out
    return looped(draw, LOOP, floor=(FLOOR, FLOOR_COLOR))


# ---- music: the house breathing in its sleep ----
# Eight slow chords over a low pedal, each crossfading into the next for XF seconds; the last one fades across
# the loop seam into the first. Pads swell and settle with the heat that crawls through each part of the roof
# (left wing, porch, right wing), so the house breathes where it glows. A few of the light's own orange pops
# wake a low murmur (contrabass or bassoon, far down) where they happen, and four of them a faint high shimmer
# that lives mostly in the reverb.
XF = 9.0
SECTIONS = [                    # (start, sub roots, pad voicing); each runs to the next start (the last to LOOP)
    (0.0, ('D1', 'D2'), ('D3', 'F3', 'A3', 'E4')),              # D minor, add 9
    (42.0, ('D1', 'D2'), ('Bb2', 'D3', 'F3', 'A3')),            # B-flat major 7 over the D pedal
    (78.0, ('G1', 'G2'), ('G2', 'Bb2', 'D3', 'A3')),            # G minor 9
    (118.0, ('D1', 'D2'), ('D3', 'Eb3', 'G3', 'Bb3')),          # E-flat over D: the uneasy one
    (152.0, ('C2', 'C2'), ('C3', 'F3', 'A3', 'E4')),            # F major 7 over C
    (190.0, ('Bb1', 'Bb1'), ('Bb2', 'Db3', 'F3', 'C4')),        # B-flat minor 9: the floor drops away
    (228.0, ('A1', 'A1'), ('A2', 'E3', 'G3', 'Bb3')),           # A with a flat 9: leaning home
    (264.0, ('D1', 'D2'), ('D3', 'A3', 'F3', 'E3')),            # D minor again, closer, into the seam
]
MURMURS = (21, 63, 101, 139, 176, 214, 247, 283)     # rough times; each takes the nearest light pop
SHIMMERS = (49, 131, 207, 291)
LEVEL = 0.38                    # overall: the outdoor speaker is down low and a car radio turns it up
MURMUR_LINES = (('A2', 'G2'), ('D2',), ('F2', 'E2'), ('D2', 'C#2'), ('A1',), ('F2', 'Db2'), ('E2', 'D2'),
                ('A2', 'F2', 'D2'))
SHIMMER_NOTES = (('A5', 'E5'), ('F5', 'D5'), ('Db5', 'F5'), ('E5', 'A5'))


def _light_plan(G):
    """The light's heat and pops, drawn the way render() draws them (same seed, same order): per roof region a
    0..1 'breath' sampled every 0.25 s over the loop, and the pops as (time, path index)."""
    rng = np.random.default_rng(15)
    segs = G.path_segments()
    D, n = LOOP + 12.0, G.N
    idx = np.arange(n, dtype=float)
    flow, local = np.empty(n), np.empty(n)
    for i, (_, s) in enumerate(segs):
        flow[s] = (1 if i % 2 else -1) * rng.uniform(1.5, 3.5)
        local[s] = idx[s] - s.min()
    k = rng.uniform(0.04, 0.12, 4)
    w = rng.uniform(0.15, 0.5, 4)
    ph = rng.uniform(0, 2 * np.pi, 4)
    drift = smooth_noise(rng, idx, 40)
    P = int(D * 1.5)
    pt, pp = rng.uniform(-3, D, P), rng.integers(0, n, P)

    def intensity(t):
        x = local[None] + flow[None] * t[:, None]
        heat = sum(np.sin(k[j] * x + w[j] * t[:, None] * 0.3 + ph[j] + 2 * drift[None]) for j in range(4)) / 4
        return 0.17 + 0.17 * (0.5 + 0.5 * heat) ** 1.5

    t = np.arange(0, LOOP, 0.25)
    I = intensity(t)
    b = t < 12.0                                 # looped() blends the first 12 s with the 12 s after the end
    wb = (t[b] / 12.0)[:, None]
    I[b] = I[b] * wb + intensity(t[b] + LOOP) * (1 - wb)
    names = dict(segs)
    regions = {'left': ('Side', 'Left'), 'porch': ('Porch Left', 'Porch Front', 'Porch Right'), 'right': ('Right',)}
    breath = {}
    ker = np.exp(-0.5 * (np.arange(-24, 25) / 10.0) ** 2)     # ~2.5 s gaussian, applied round the loop
    ker /= ker.sum()
    for r, segnames in regions.items():
        m = I[:, np.concatenate([names[s] for s in segnames])].mean(1)
        m = np.real(np.fft.ifft(np.fft.fft(m) * np.fft.fft(ker, len(m))))
        m = np.roll(m, -24)
        breath[r] = (m - m.min()) / (m.max() - m.min())
    breath['all'] = (breath['left'] + breath['porch'] + breath['right']) / 3
    keep = (pt >= 12.0) & (pt < LOOP)
    return t, breath, list(zip(pt[keep], pp[keep]))


def score(M, G):
    from pixelhome.audio import SR, note
    n = note
    rng = np.random.default_rng(55)
    grid, breath, pops = _light_plan(G)
    xs = G.pos[:, 0]
    x0, x1 = xs.min(), xs.max()

    def pan_x(x):
        return float(0.8 * (2 * (x - x0) / (x1 - x0) - 1))

    def pan_seg(*names):
        return pan_x(xs[np.concatenate([G.seg[s] for s in names])].mean())

    pans = {'left': pan_seg('Side', 'Left'), 'porch': pan_seg('Porch Left', 'Porch Front', 'Porch Right'),
            'right': pan_seg('Right')}

    def swell(region, t0, length, lo=0.6):
        """Gain over [t0, t0+length): lo..1 following the heat in that part of the roof."""
        t = t0 + np.arange(int(length * SR)) / SR
        return lo + (1 - lo) * np.interp(t % LOOP, grid, breath[region], period=LOOP)

    def window(length, fin, fout):
        m = int(length * SR)
        e = np.ones(m)
        a, b = int(fin * SR), int(fout * SR)
        if a:
            e[:a] = np.sin(0.5 * np.pi * np.arange(a) / a)
        if b:
            e[m - b:] = np.cos(0.5 * np.pi * np.arange(b) / b)
        return e

    def sub(f, length):
        """Low drone with its own overtones, so a car speaker still hears the note when the fundamental is lost."""
        t = np.arange(int(length * SR)) / SR
        p0 = rng.uniform(0, 2 * np.pi, 3)
        ph = 2 * np.pi * f * t
        s = (np.sin(ph + p0[0]) + 0.5 * np.sin(2 * ph + p0[1]) + 0.28 * np.sin(3 * ph + p0[2]) +
             0.14 * np.sin(4 * ph) + 0.06 * np.sin(5 * ph))
        s += 0.5 * np.sin(2 * np.pi * f * 1.0015 * t)           # a slow beat against itself, like a long exhale
        s /= np.abs(s).max()
        return np.vstack([s, s])

    for name, gain, rev in (('sub', 0.34, 0.0), ('low', 0.5, 0.15), ('pad', 0.55, 0.35), ('air', 0.42, 0.45),
                            ('breath', 0.5, 0.35), ('murmur', 0.5, 0.55), ('shimmer', 0.1, 2.5)):
        M.bus(name, gain=gain * LEVEL, reverb=rev)

    pad = M.synth('Pads/Still')
    low = M.synth('Pads/Yeti Funeral')
    air = M.synth('Pads/MKS-70 Warm Pad')
    bass = M.sampler('Strings/Solo Contrabass/SusNV/*.wav', tune=-12)
    bsn = M.sampler('Woodwinds/Bassoon/sus/*.wav', tune=-12)
    vln = M.sampler('Strings/Violin Section/susVib/*.wav', tune=-12)

    # ---- the breathing chords ----
    starts = [s for s, _, _ in SECTIONS] + [LOOP]
    for i, (t0, roots, voicing) in enumerate(SECTIONS):
        length = starts[i + 1] - t0 + XF
        env = window(length, XF, XF)
        hold = length - 0.5
        notes = [n(v) for v in voicing]
        y = pad.render([(0.0, m, 52, hold) for m in notes], length)[:, :len(env)]
        M.add('pad', y * env * swell('all', t0, length, 0.55)[:len(env)], t0)
        y = low.render([(0.0, n(roots[1]), 46, hold), (0.0, n(roots[1]) + 7, 38, hold)], length)[:, :len(env)]
        M.add('low', y * env * swell('porch', t0, length)[:len(env)], t0, pan=pans['porch'] * 0.5)
        for m, side in ((notes[2], 'left'), (notes[3], 'right')):     # the upper voices, one to each wing
            y = air.render([(0.0, m, 44, hold)], length)[:, :len(env)]
            M.add('air', y * env * swell(side, t0, length, 0.35)[:len(env)], t0, pan=pans[side])
        f = 440 * 2 ** ((n(roots[0]) - 69) / 12)
        g = env * swell('all', t0, length, 0.75)
        M.add('sub', sub(f, length)[:, :len(env)] * g, t0, 0.8)
        M.add('sub', sub(2 * f if roots[1] == roots[0] else 440 * 2 ** ((n(roots[1]) - 69) / 12), length)
              [:, :len(env)] * g, t0, 0.35)

    # ---- breath: a low hush of air over the whole loop, rising with the heat (FFT-filtered round the loop) ----
    N = int(LOOP * SR)
    spec = np.fft.rfft(rng.normal(0, 1, (2, N)), axis=1)
    fr = np.fft.rfftfreq(N, 1 / SR)
    spec *= np.exp(-0.5 * (np.log(np.maximum(fr, 1) / 320.0) / 0.55) ** 2)
    hush = np.fft.irfft(spec, N, axis=1)
    hush /= np.abs(hush).max()
    M.add('breath', hush * (0.15 + 0.85 * swell('all', 0.0, LOOP, 0.0) ** 2), 0.0)

    def nearest_pop(t):
        tt, p = min(pops, key=lambda q: abs(q[0] - t))
        return float(tt), pan_x(xs[G.path[int(p)]])

    # ---- murmurs: a low voice somewhere under the roof, where an ember pops ----
    for j, (tc, line) in enumerate(zip(MURMURS, MURMUR_LINES)):
        t, p = nearest_pop(tc)
        inst = bass if j % 3 != 1 else bsn
        step = 4.2 if inst is bass else 3.4
        for q, m in enumerate(line):
            d = step + (1.6 if q == len(line) - 1 else 0.6)
            y = inst.play(n(m), 40, dur=d, release=1.8)
            y = y * window(y.shape[1] / SR, 1.2, 0.0)[:y.shape[1]]
            M.add('murmur', y, t + q * step, 0.9 if inst is bass else 0.55, p)

    # ---- shimmer: very rarely, two high soft string notes, mostly reverb ----
    for (tc, pair) in zip(SHIMMERS, SHIMMER_NOTES):
        t, p = nearest_pop(tc)
        for q, m in enumerate(pair):
            y = vln.play(n(m), 30, dur=6.0, release=3.0)
            y = y * window(y.shape[1] / SR, 2.5, 0.0)[:y.shape[1]]
            M.add('shimmer', y, t + 1.5 * q, 0.8, p)
