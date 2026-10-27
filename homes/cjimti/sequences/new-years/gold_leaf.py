"""Gold Leaf: A Gray-Scott reaction-diffusion runs along the whole roof (on an even grid in path
distance, so the spots are the same size on every run). Gold spots grow and split in two, over and
over, until the roof is beaded with them. A slow dark tide moves along the house dissolving them,
and behind it the survivors split and creep back in to re-gild the roof. Dim, slow, all night."""
import numpy as np
from pixelhome.fx import DT, hexc, perc, keys, smoothstep, colormap, nframes, looped

CODE = 'NY09'
TITLE = 'Gold Leaf'
KIND = 'ambient'
DESCRIPTION = 'Reaction-diffusion along the roof: gold spots grow and split until the roof is beaded with them; a slow dark tide dissolves them and they creep back.'

FLOOR_COLOR = hexc('#5a2a10')
FLOOR = 0.12
LOOP = 160.0
CELL = 5.0
F_FEED, K_KILL = 0.04, 0.06
DU, DV = 0.2, 0.1
ITERS = 6                                  # reaction steps per frame


def render(G, seed=29):
    rng = np.random.default_rng(seed)
    pdp = G.pd[G.path]
    M = int(G.length / CELL) + 1
    xs = np.arange(M) * CELL
    gold = colormap([(0.0, hexc('#3a1a10')), (0.35, hexc('#a04812')), (0.7, hexc('#ff9a28')),
                     (1.0, hexc('#ffd070')), (1.2, hexc('#fff0c0'))])

    def step(u, v, kill):
        lu = np.empty(M)
        lv = np.empty(M)
        lu[1:-1] = u[2:] + u[:-2] - 2 * u[1:-1]
        lv[1:-1] = v[2:] + v[:-2] - 2 * v[1:-1]
        lu[0], lu[-1] = u[1] - u[0], u[-2] - u[-1]             # sealed ends
        lv[0], lv[-1] = v[1] - v[0], v[-2] - v[-1]
        uvv = u * v * v
        u += DU * lu - uvv + F_FEED * (1 - u)
        v += DV * lv + uvv - (F_FEED + kill) * v

    def draw(D):
        n = G.N
        out = np.zeros((nframes(D), n, 3), np.float32)
        u = np.ones(M)
        v = np.zeros(M)
        for c in rng.integers(20, M - 20, 6):
            v[c - 10:c + 10] = 0.25
            u[c - 10:c + 10] = 0.5
        v += rng.uniform(0, 0.02, M)
        for _ in range(5000):                                     # start with a gilded roof
            step(u, v, K_KILL)
        # two dark tides, one from each free end: each floods in, lingers, and ebbs away
        tideA = [(0, -150), (4, -150), (24, 950), (30, 950), (48, -150), (D + 1, -150)]
        tideB = [(0, -150), (75, -150), (95, 800), (101, 800), (118, -150), (D + 1, -150)]
        for f in range(len(out)):
            t = f * DT
            fa = keys(t, tideA)
            fb = keys(t, tideB)
            dark = smoothstep(fa + 60, fa - 60, xs) + smoothstep(fb + 60, fb - 60, G.length - xs)
            kill = K_KILL + 0.035 * np.clip(dark, 0, 1)
            for _ in range(ITERS):
                step(u, v, kill)
            w = np.interp(pdp, xs, v) / 0.3
            uu = np.interp(pdp, xs, u)
            sheen = 1 + 0.08 * np.sin(2 * np.pi * (t / 20 - pdp / 900))   # light sliding over the leaf
            I = (0.13 + 0.235 * np.clip(w, 0, 1.2)) * sheen
            out[f][G.path] = perc(I)[:, None] * gold(np.clip(w + 0.1 * (1 - uu), 0, 1.2))
        return out
    return looped(draw, LOOP, floor=(FLOOR, FLOOR_COLOR))
