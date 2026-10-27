"""Possessed: An innocent warm-white roofline that browns out, glitches, desyncs, dissolves into a
heartbeat, flatlines, and comes back as if nothing happened."""
import numpy as np
from pixelhome.fx import DT, hexc, light, keys, lerp, heartbeat, nframes

CODE = 'SC5'
TITLE = 'Possessed'
KIND = 'show'
DESCRIPTION = 'Innocent warm white that browns out, glitches, desyncs, dissolves into a heartbeat, flatlines and comes back.'

WHITE = hexc('#ffffff')
WARM = hexc('#ff8a30')
CYAN = hexc('#00e0ff')
RED = hexc('#ff0000')


def porch_center(G):
    pf = G.seg['Porch Front']
    return pf[len(pf) // 2]


def render(G, seed=5):
    rng = np.random.default_rng(seed)
    D = 60.0
    n = G.N
    out = np.zeros((nframes(D), n, 3))
    idx = np.arange(n, dtype=float)
    segs = [G.pi[G.seg[name]] for name in sorted(G.seg)]
    seg_id = np.empty(n, int)
    for i, s in enumerate(segs):
        seg_id[s] = i
    dips = sorted(rng.uniform(8, 14, 9))
    dropouts = [(11.5, 12.6, 'Side'), (13.0, 13.5, 'Porch Right')]
    static_t = sorted(rng.uniform(14, 24, 13))
    offsets = rng.integers(-60, 60, (100, len(segs)))
    clip_len = rng.uniform(0.15, 0.3, len(segs))
    clip_col = [hexc(c) for c in ('#00ffd0', '#ff00a0', '#80ff00', '#ffffff', '#0040ff', '#ff6000')]
    die = rng.uniform(34.5, 39.5, n)
    pdp = G.pd[G.path]
    d0 = G.pd[porch_center(G)]
    frozen = None

    def base(t):
        return light(WARM, np.full(n, 0.5))

    def corrupt(t):
        hue = 0.5 + 0.5 * np.sin(idx * 0.03 - t * 2.5)
        buf = light(lerp(hexc('#3000ff'), hexc('#00ffa0'), hue[:, None]), np.full(n, 0.35))
        k = int(t / 0.4)
        torn = np.empty_like(buf)
        for i, s in enumerate(segs):
            torn[s] = np.roll(buf, offsets[k % 100, i], axis=0)[s]
        p = (t - 14) * 120 % n
        for off, col in ((-6, RED), (0, WHITE), (6, CYAN)):
            torn += light(col, np.clip(1 - np.abs(idx - p - off) / 8, 0, 1) * 0.9)
        return torn

    for f in range(len(out)):
        t = f * DT
        if t < 14:
            buf = base(t)
            dip = min([1.0] + [0.3 for d in dips if d <= t < d + 0.12])
            buf *= dip ** 2.2
            for a, b, name in dropouts:
                if a <= t < b and (name != 'Porch Right' or (f % 3)):
                    buf[G.pi[G.seg[name]]] = 0
        elif t < 24:
            buf = corrupt(t)
            if any(s <= t < s + 0.15 for s in static_t):
                m = rng.random(n) < 0.35
                buf[m] = rng.random((m.sum(), 3)) ** 3 + WHITE * 0.3
        elif t < 34:
            buf = np.zeros((n, 3))
            sync = ((t - 24) % 2.0) < 0.12
            for i, s in enumerate(segs):
                lt = 0.0 if sync else (t % clip_len[i]) * (1 + i * 0.37)
                ph = (idx[s] - idx[s].min()) / len(s)
                saw = ((ph * 3 - lt * 4) % 1) ** 4
                buf[s] = light(WHITE if sync else clip_col[i], saw * (1.0 if sync else 0.8))
            frozen = buf.copy()
        elif t < 40:
            u = t - die
            burn = np.exp(-(u / 0.12) ** 2)
            buf = frozen * (u < 0)[:, None] + light(RED, burn * (u > -0.15))
        elif t < 50:
            period = keys(t, [(40, 1.1), (50, 0.5)])
            buf = np.zeros((n, 3))
            dist = np.abs(pdp - d0)
            delay = dist / 450
            ph = np.array([heartbeat(t - dl, 40, period) for dl in delay[::4]])
            env = np.interp(idx, idx[::4], ph)
            buf += light(RED, 1.1 * env * np.exp(-dist / 2500))
        elif t < 53:
            buf = light(RED, np.full(n, 0.28 * (t < 52.6)))
        elif t < 57:
            buf = np.zeros((n, 3))
        else:
            buf = light(WARM, np.full(n, keys(t, [(57, 0), (60, 0.5)])))
        out[f][G.path] = buf
    return out
