"""Solidarity: Many small lights join into one strong one.

A hundred and fifty dim lights, each a different shade, appear scattered along the whole roofline
and wander on their own. Then they begin to find each other: an attraction along the path whose
reach grows over time pulls neighbours together, and when two touch they merge for good (mass and
momentum add, the colour is the mass-weighted mix, drifting toward gold as the group grows). Pairs
become knots, knots become crowds, the crowds from both wings march on the porch and meet in a
last merge. The one strong light then opens out until it holds the whole house."""
import numpy as np
from pixelhome.fx import DT, hexc, light, smoothstep, keys, lerp, Flicker, nframes

CODE = 'LB05'
TITLE = 'Solidarity'
KIND = 'show'
DESCRIPTION = ('A hundred and fifty small lights wander the roof alone, then find each other: pairs, knots, crowds, '
               'until the last two crowds meet on the porch and one strong light fills the house.')

GOLD = hexc('#ffb53a')
WARM = hexc('#ffd9a0')
SHADES = [hexc(h) for h in ('#ffd2a0', '#ff9a5a', '#ff7a8a', '#9ad8d0', '#b9a8ff', '#ffe7c2', '#8fc0ff', '#ffc06a')]


def render(G, seed=25):
    rng = np.random.default_rng(seed)
    D = 51.0
    F = nframes(D)
    out = np.zeros((F, G.N, 3))
    s = G.pd[G.path]
    L = G.length
    home = s[296]                                   # porch front centre

    n = 150
    x = np.sort(rng.uniform(15, L - 15, n))
    v = np.zeros(n)
    m = np.ones(n)
    col = np.array([SHADES[k] for k in rng.integers(len(SHADES), size=n)])
    alive = np.ones(n, bool)
    t_appear = rng.uniform(0.3, 4.5, n)
    t_merge = np.full(n, -10.0)
    wander = rng.uniform(0, 2 * np.pi, (n, 2))
    wf = rng.uniform(0.05, 0.2, (n, 2))
    final_t = None
    shimmer = Flicker(rng, G.N, 0.2, 0.9)

    for f in range(F):
        t = f * DT
        buf = np.zeros((G.N, 3))
        idx = np.nonzero(alive)[0]
        reach = keys(t, [(5, 0.0), (8, 35), (16, 90), (24, 260), (30, 900), (36, 3000)])
        pull = keys(t, [(18, 0.0), (28, 1.0)])

        if final_t is None:
            xi, mi = x[idx], m[idx]
            d = xi[None, :] - xi[:, None]                         # d[i, j] = x_j - x_i
            ad = np.abs(d)
            np.fill_diagonal(ad, np.inf)
            if reach > 0:
                k = mi[None, :] * np.exp(-ad / reach) / (ad + 20.0) ** 0.5
                acc = 220.0 * np.sum(np.sign(d) * k, axis=1) / np.sqrt(mi)
            else:
                acc = np.zeros(len(idx))
            # each one wanders on its own, less as the group grows
            own = 18.0 * (np.sin(wf[idx, 0] * 2 * np.pi * t + wander[idx, 0]) +
                          0.6 * np.sin(wf[idx, 1] * 2 * np.pi * t + wander[idx, 1])) / mi
            acc += own * (1 - smoothstep(10, 24, t)) * 2.0
            acc += pull * 55.0 * np.sign(home - xi) * np.minimum(1, np.abs(home - xi) / 120)
            v[idx] = v[idx] * (1 - 1.6 * DT) + acc * DT
            v[idx] = np.clip(v[idx], -140, 140)
            x[idx] = np.clip(x[idx] + v[idx] * DT, 0, L)
            # merge anything that touches (sorted sweep, repeated so chains collapse)
            for _ in range(3):
                idx = np.nonzero(alive & (t >= t_appear))[0]
                if len(idx) < 2:
                    break
                o = idx[np.argsort(x[idx])]
                w = 3.0 * m[o] ** 0.4
                touch = np.nonzero(np.diff(x[o]) < 0.5 * (w[:-1] + w[1:]))[0]
                if len(touch) == 0:
                    break
                used = set()
                for tk in touch:
                    a, b = o[tk], o[tk + 1]
                    if a in used or b in used:
                        continue
                    used.update((a, b))
                    M = m[a] + m[b]
                    x[a] = (x[a] * m[a] + x[b] * m[b]) / M
                    v[a] = (v[a] * m[a] + v[b] * m[b]) / M
                    col[a] = (col[a] * m[a] + col[b] * m[b]) / M
                    m[a] = M
                    alive[b] = False
                    t_merge[a] = t
            if alive.sum() == 1 and t > 20:
                final_t = t

        idx = np.nonzero(alive)[0]
        vis = smoothstep(t_appear[idx], t_appear[idx] + 0.8, t)
        mi = m[idx]
        width = 3.5 * mi ** 0.42
        bright = np.minimum(0.24 * mi ** 0.42, 0.95)
        flash = 0.5 * np.exp(-np.clip(t - t_merge[idx], 0, None) / 0.35) * (t_merge[idx] > 0)
        golden = smoothstep(1, 60, mi)[:, None]
        cc = lerp(col[idx], GOLD, golden)
        w = np.exp(-((s[None] - x[idx, None]) / width[:, None]) ** 2) * (vis * (bright + flash))[:, None]
        I = w.sum(0)
        hue = (w.T @ cc) / np.maximum(I, 1e-6)[:, None]
        if final_t is not None:
            u = t - final_t
            # the one light opens out to hold the whole house
            span = 30 + keys(u, [(0.8, 0), (7, 1700)])
            core = keys(u, [(0, 1.0), (0.3, 1.0), (6, 0.62)])
            open_ = np.exp(-(np.maximum(np.abs(s - x[idx[0]]) - span, 0) / 40) ** 2)
            ring = 0.6 * np.exp(-((np.abs(s - x[idx[0]]) - 1100 * u) / 60) ** 2) * np.exp(-u / 1.2)
            pulse = 1 + 0.06 * np.sin(2 * np.pi * u / 3.0) * smoothstep(5, 8, u)
            I = np.maximum(I, core * open_ * pulse * (0.93 + 0.07 * shimmer(t)))
            hue = lerp(hue, GOLD, smoothstep(0, 1.5, u))
            buf += light(WARM, ring)
        buf += hue * (I ** 2.2)[:, None]
        buf *= 1 - smoothstep(D - 4, D, t)
        out[f][G.path] = np.clip(buf, 0, 1)
    return out
