"""Smolder: Slow lava. Heat crawls through each roof section in its own direction, like coals breathing;
rare pixels pop orange and fade."""
import numpy as np
from pixelhome.fx import DT, hexc, perc, smoothstep, lerp, smooth_noise, nframes, looped

CODE = 'NT5'
TITLE = 'Smolder'
KIND = 'ambient'
DESCRIPTION = 'Slow lava crawling through each roof section in its own direction, with the odd orange pop.'

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
