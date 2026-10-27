"""One Light: Thirty-odd small lights, each a different colour, drift along the roof on their own.
Slowly they begin to feel each other's pull. When two touch they become one: mass and momentum add,
the colours mix by mass, and the bigger a light grows the warmer and whiter it burns. The merging
cascades around the corners into a few great lights, and the last stragglers are drawn in from
the far ends to the porch. The last light breathes, opens out over the whole roof, and gathers back to the porch.

Mechanism: an aggregation (sticky-particle) simulation on the path, with Ornstein-Uhlenbeck wander,
a pairwise attraction that grows over the piece, and colour carried as mass-weighted mixtures."""
import numpy as np
from pixelhome.fx import DT, hexc, perc, light, keys, lerp, smoothstep, Flicker, nframes

CODE = 'MK04'
TITLE = 'One Light'
KIND = 'show'
DESCRIPTION = ('Dozens of small lights, every one a different colour, drift along the roof. One by one they '
               'find each other and merge, until a single warm light shines from the porch.')

PALETTE = ['#ff6a5a', '#ffb040', '#40d0b0', '#8060ff', '#ff70b0', '#60a8ff', '#a0e060', '#ff8a30',
           '#c070ff', '#30b8ff', '#ffd060', '#ff5080']
WARM = hexc('#ffc890')
GOLD = hexc('#ffa040')
NIGHT = hexc('#0c18a0')


def render(G, seed=24):
    rng = np.random.default_rng(seed)
    D = 82.0
    F = nframes(D)
    out = np.zeros((F, G.N, 3))
    pdp = G.pd[G.path]
    L = G.length
    pf = G.seg['Porch Front']
    centre = 0.5 * (G.pd[pf].min() + G.pd[pf].max())

    K = 34
    x = np.sort(rng.uniform(30, L - 30, K))
    x += rng.uniform(-10, 10, K)
    v = rng.normal(0, 8, K)
    m = np.ones(K)
    col = np.array([hexc(PALETTE[i % len(PALETTE)]) for i in rng.permutation(K)])
    born = rng.uniform(2, 10, K)
    flash = np.zeros(K)
    alive = np.ones(K, bool)
    shimmer = Flicker(rng, G.N, 0.2, 0.8)
    final = None

    for f in range(F):
        t = f * DT
        idx = np.nonzero(alive)[0]
        xa, ma = x[idx], m[idx]
        # forces: wander, attraction to others, and late on a pull toward the porch
        pull = keys(t, [(0, 0), (12, 0.0), (22, 260), (40, 900), (52, 1600)])
        d = xa[None, :] - xa[:, None]
        fa = (np.sign(d) * ma[None, :] / (np.abs(d) + 60) ** 1.2).sum(1) * pull
        home = keys(t, [(44, 0), (56, 1.2)]) * np.clip(centre - xa, -400, 400) * 0.06
        acc = fa / np.sqrt(ma) + home * 4 - 0.8 * v[idx] + rng.normal(0, 18, len(idx)) / np.sqrt(ma)
        v[idx] += acc * DT
        x[idx] += v[idx] * DT
        over = (x < 8) | (x > L - 8)
        v[over] *= -0.5
        x[:] = np.clip(x, 8, L - 8)

        # collisions: neighbours (in path order) that touch become one
        order = idx[np.argsort(x[idx])]
        radius = 4 + 4.5 * np.sqrt(m)
        merged = True
        while merged:
            merged = False
            for a, b in zip(order[:-1], order[1:]):
                if alive[a] and alive[b] and x[b] - x[a] < 0.6 * (radius[a] + radius[b]) and \
                        t > max(born[a], born[b]) + 1.5:
                    M = m[a] + m[b]
                    x[a] = (x[a] * m[a] + x[b] * m[b]) / M
                    v[a] = (v[a] * m[a] + v[b] * m[b]) / M
                    col[a] = (col[a] * m[a] + col[b] * m[b]) / M
                    m[a] = M
                    flash[a] = 1.0
                    alive[b] = False
                    radius[a] = 4 + 4.5 * np.sqrt(M)
                    order = order[order != b]
                    merged = True
                    break
        flash *= np.exp(-DT / 0.6)

        buf = light(NIGHT, 0.06 * keys(t, [(0, 0), (3, 1), (78, 1), (82, 0)]) * np.ones(G.N))
        idx = np.nonzero(alive)[0]
        if len(idx) == 1 and final is None:
            final = t
        open_ = 0.0 if final is None else keys(t - final, [(3, 0), (9, 1), (15, 1), (21, 0)])
        for i in idx:
            r = radius[i]
            warmth = smoothstep(1, K * 0.7, m[i]) ** 0.7
            c = lerp(col[i], WARM, warmth)
            c = c / max(c.max(), 1e-6)
            fade_in = smoothstep(born[i], born[i] + 2.5, t)
            shape = np.exp(-((pdp - x[i]) / r) ** 2)
            I = fade_in * (0.68 + 0.22 * smoothstep(1, 12, m[i]) + 0.35 * flash[i]) * shape
            buf += light(c, I)
        if final is not None:
            # the one light opens over the whole roof, then gathers back
            i = idx[0]
            reach = lerp(radius[i], 1500, open_)
            body = np.exp(-(np.abs(pdp - x[i]) / reach) ** 4)
            buf += light(WARM, 0.42 * open_ * body * (1 + 0.06 * shimmer(t)[G.path]))
        buf *= keys(t, [(0, 1), (78, 1), (82, 0)])
        out[f][G.path] = buf
    return out
