"""The Garden: A gardener's light walks the roof from the back of the house to the right end, planting
seeds. Shoots come up, leaves unfold, buds swell and open into pink, peach and lilac blooms that sway
in a breeze; a bee works the flowers. At dusk the flowers fold shut one by one, Mum's flower on the
porch last of all."""
import numpy as np
from pixelhome.fx import DT, hexc, light, smoothstep, keys, nframes

CODE = 'MO01'
TITLE = 'The Garden'
KIND = 'show'
DESCRIPTION = 'Seeds are planted along the roof, shoots unfold, buds swell and open into pink, peach and lilac blooms; a bee visits, then dusk folds them shut, the porch flower last.'

SOIL = hexc('#ff4a10')
GARDENER = hexc('#ffd9b0')
GREEN = hexc('#4cff2a')
LEAF = hexc('#88ff50')
BUD = hexc('#ff2a6a')
POLLEN = hexc('#ffb020')
BEE = hexc('#ffc000')
DUSK = hexc('#7040ff')
PETALS = [hexc(c) for c in ('#ff5a96', '#ff8a5c', '#b070ff', '#ff7ab0', '#ffb0a0', '#e080ff')]


def render(G, seed=21):
    rng = np.random.default_rng(seed)
    D = 80.0
    n = G.N
    out = np.zeros((nframes(D), n, 3))
    pdp = G.pd[G.path]
    L = G.length
    pf = G.pd[G.seg['Porch Front']]
    mum = 0.5 * (pf.min() + pf.max())

    # plant sites, evenly spread with jitter; one (Mum's) exactly at the porch centre
    sites = np.arange(45, L - 30, 64.0) + rng.uniform(-12, 12, len(np.arange(45, L - 30, 64.0)))
    k_mum = int(np.argmin(np.abs(sites - mum)))
    sites[k_mum] = mum
    P = len(sites)
    walk = [(2.5, -40.0), (19.0, L + 40.0)]
    t_plant = 2.5 + (sites + 40) / (L + 80) * 16.5
    t_sprout = 18.5 + 11 * sites / L + rng.uniform(-1.5, 1.5, P)          # growth follows the planting
    t_bud = t_sprout + rng.uniform(5, 8, P)
    t_open = t_bud + rng.uniform(2.5, 4, P)
    t_open = np.minimum(t_open, 50)
    t_sprout[k_mum], t_bud[k_mum], t_open[k_mum] = 24.0, 38.0, 46.0
    big = np.ones(P)
    big[k_mum] = 1.5
    col = np.array([PETALS[i % len(PETALS)] for i in rng.permutation(P)])
    col[k_mum] = hexc('#ff4f8b')
    sway_ph = rng.uniform(0, 2 * np.pi, P)
    # dusk: a front from the right end back toward the porch and the far end, flowers close as it passes
    t_close = 64 + (L - sites) / L * 9 + rng.uniform(-0.6, 0.6, P)
    t_close[k_mum] = 76.0

    # the bee: visits six flowers
    order = rng.choice([i for i in range(P) if i != k_mum], 6, replace=False)
    visits = sorted(order, key=lambda i: sites[i])
    bee_keys = [(51.5, L + 30)]
    tt = 52.5
    for i in list(visits[::-1][:3]) + [k_mum] + list(visits[::-1][3:]):
        bee_keys += [(tt, sites[i]), (tt + 1.1, sites[i])]
        tt += 2.2
    bee_keys += [(tt + 1.2, -30.0)]
    bee_end = tt + 1.2
    landed = {}
    for i, (a, b) in enumerate(zip(bee_keys[1::2], bee_keys[2::2])):
        landed[int(np.argmin(np.abs(sites - a[1])))] = a[0]

    d0 = pdp[None, :] - sites[:, None]
    for f in range(len(out)):
        t = f * DT
        buf = np.zeros((n, 3))
        soil = keys(t, [(0, 0), (2.5, 0.09), (66, 0.09), (78, 0.04), (80, 0)])
        buf += light(SOIL, soil * (0.8 + 0.2 * np.sin(pdp * 0.05)))

        # the gardener and the seeds
        if 2 < t < 20:
            g = keys(t, walk) if t > 2.5 else -40
            buf += light(GARDENER, 0.75 * np.exp(-((pdp - g) / 11) ** 2) + 0.2 * np.exp(-((pdp - g) / 40) ** 2))
        planted = t > t_plant
        spark = np.where(planted, np.exp(-np.clip(t - t_plant, 0, None) / 0.4), 0)
        seed_glow = planted * (0.12 + 0.6 * spark) * (1 - smoothstep(0, 3, t - t_sprout))

        h = smoothstep(t_sprout, t_sprout + 7, t)                      # shoot height
        bud = smoothstep(t_bud, t_bud + 2.5, t)
        op = smoothstep(t_open, t_open + 4.5, t)                      # petals open
        cl = smoothstep(t_close, t_close + 2.2, t)                     # dusk folds them
        op_eff = op * (1 - 0.85 * cl)
        breeze = keys(t, [(40, 0), (50, 1), (63, 1), (70, 0.3)])
        sway = (breeze * 3.5 * np.sin(2 * np.pi * t / 3.2 - sites / 260 + 0.4 * sway_ph) + 0.6 * np.sin(2.3 * t + sway_ph)) * h
        d = d0 - sway[:, None]
        ad = np.abs(d)
        w = (4 + 13 * h) * big                                          # leaf half-span
        leaves = (np.exp(-((ad - 0.55 * w[:, None]) / (0.35 * w[:, None] + 1)) ** 2) * 0.9 + np.exp(-(d / 3) ** 2) * 0.6)
        leafI = (0.32 * h * (1 - 0.6 * cl))[:, None] * leaves * (1 - 0.7 * op_eff[:, None] * np.exp(-(d / (16 * big[:, None])) ** 2))
        budI = (0.5 * bud * (1 - op) * (1 - cl))[:, None] * np.exp(-(d / (4 * big[:, None])) ** 2)
        rp = (3 + 11 * op_eff) * big
        petal = np.exp(-((ad - rp[:, None]) / ((2.5 + 3.5 * op_eff) * big)[:, None]) ** 2)
        petal = np.maximum(petal, (ad < rp[:, None]) * 0.65)
        bloomI = (0.85 * op_eff * (1 - 0.5 * cl))[:, None] * petal
        centreI = (0.75 * op_eff * (1 - 0.6 * cl))[:, None] * np.exp(-(d / (3 * big[:, None])) ** 2)
        # pollinated flowers sparkle for a moment
        pol = np.zeros(P)
        for i, tl in landed.items():
            if tl - 0.2 < t < tl + 3:
                pol[i] = np.exp(-max(0.0, t - tl - 0.4) / 0.8) * smoothstep(tl - 0.2, tl + 0.3, t)
        bloomI = bloomI * (1 + 0.6 * pol[:, None])
        if t > 74:                                                      # Mum's flower: one last glow
            bloomI[k_mum] *= 1 + 0.8 * np.exp(-((t - 75.6) / 0.6) ** 2)

        I_seed = (seed_glow[:, None] * np.exp(-(d0 / 3.5) ** 2)).max(0)
        buf += light(LEAF, I_seed)
        buf += light(GREEN, leafI.max(0))
        buf += light(BUD, budI.max(0))
        k = np.argmax(bloomI, 0)
        buf += light(col[k], bloomI.max(0)) * 1.0
        buf += light(POLLEN, centreI.max(0))

        # dusk wash
        dusk = keys(t, [(62, 0), (68, 0.12), (76, 0.12), (80, 0)])
        front = L - (t - 62) / 11 * L
        buf += light(DUSK, dusk * smoothstep(front + 150, front - 150, pdp))

        if 51.5 < t < bee_end:                                          # bee, with a wobble
            b = keys(t, bee_keys) + 5 * np.sin(2 * np.pi * 2.3 * t)
            buzz = 0.7 + 0.3 * np.sin(2 * np.pi * 11 * t)
            buf += light(BEE, buzz * np.exp(-((pdp - b) / 5) ** 2))
        fade = keys(t, [(0, 1), (77.5, 1), (80, 0)])
        out[f][G.path] = buf * fade
    return out
