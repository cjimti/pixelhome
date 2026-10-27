"""Glitter: Every pixel is a facet of glitter with its own tilt, half gold and half silver. A light
moves through real 3-D space around the house and each facet flashes only when it mirrors that
light toward the street (Blinn-Phong specular toward a viewer on the sidewalk). A lamp carried along
the roof, a sweep in front, two lamps crossing, a light from behind, then the grain of the glitter
coarsens until the whole roof blazes, and fines back down to a last few glints."""
import numpy as np
from pixelhome.fx import DT, hexc, perc, light, keys, smoothstep, nframes

CODE = 'NY07'
TITLE = 'Glitter'
KIND = 'show'
DESCRIPTION = 'Each pixel is a tilted facet of gold or silver glitter; lights moving in 3-D around the house make them flash only when they mirror the light toward the street.'

GOLD = hexc('#ffb038')
SILVER = hexc('#d0dcff')
WHITE = hexc('#fff8f0')
NAVY = hexc('#060e34')
VIEW = np.array([0.0, 160.0, 1400.0])          # someone on the sidewalk


def unit(v):
    return v / np.linalg.norm(v, axis=-1, keepdims=True)


def render(G, seed=27):
    rng = np.random.default_rng(seed)
    D = 62.0
    out = np.zeros((nframes(D), G.N, 3))
    P = G.pos
    n = G.N
    to_view = unit(VIEW - P)
    # most facets face the street a little upward; a third are tipped up and answer lights from behind
    up = rng.random(n) < 0.33
    base = np.where(up[:, None], unit(np.array([0.0, 0.85, 0.5])), unit(np.array([0.0, 0.3, 1.0])))
    normals = unit(base + 0.22 * rng.normal(size=(n, 3)))
    wob_a = unit(rng.normal(size=(n, 3)))
    wob_f = rng.uniform(0.5, 1.6, n)
    wob_p = rng.uniform(0, 2 * np.pi, n)
    # material: by side of the house first (gold left, silver right), mixed later
    side_gold = (P[:, 0] < 16).astype(float)
    mixed_gold = (rng.random(n) < 0.55).astype(float)
    cx = 16.0

    def lamp_path(t):
        """Lights for this moment: list of (position, strength, tint)."""
        L = []
        if t < 9:
            # a lamp carried along the roof from the back free end, close to the pixels
            u = smoothstep(0.5, 9, t)
            s = u * 0.62
            k = int(s * (n - 1))
            p = P[G.path[min(k, n - 1)]] + np.array([0, 70, 90])
            L.append((p, keys(t, [(0.5, 0), (1.5, 1), (8, 1), (9, 0.6)]), None))
        if 7 < t < 21:
            # a big sweep across the front, high then low
            u = smoothstep(7, 21, t)
            sw = np.sin(np.pi * 2.5 * u - np.pi / 2)        # across, back, and across again
            p = np.array([1000 * sw, 380 - 150 * np.sin(np.pi * u), 150])
            L.append((p, keys(t, [(7, 0), (9, 1), (19.5, 1), (21, 0)]), None))
        if 20 < t < 33:
            # two lamps crossing in front of the house, gold and silver
            u = (t - 20) / 13
            a = 2 * np.pi * u * 1.3
            for sgn, tint in ((1, GOLD), (-1, SILVER)):
                p = np.array([cx + 800 * np.sin(sgn * a), 300 + 120 * np.cos(a * 0.7), -100 + 350 * np.cos(sgn * a)])
                L.append((p, keys(t, [(20, 0), (21.5, 1), (31.5, 1), (33, 0)]), tint))
        if 32 < t < 43:
            # from behind the house: a different set of facets answers
            u = smoothstep(32, 43, t)
            p = np.array([900 - 1800 * u, 900, -800])
            L.append((p, keys(t, [(32, 0), (34, 1.3), (41, 1.3), (43, 0)]), None))
        if t > 41:
            # eight rotating beams close above the porch: a mirror ball
            k = keys(t, [(41, 0), (43, 1), (D - 3, 1), (D, 0)])
            for j in range(8):
                a = 2 * np.pi * j / 8 + 0.25 * (t - 41) + 0.05 * (t - 41) ** 2
                p = np.array([cx + 700 * np.cos(a), 350 + 120 * np.sin(2 * a), -380 + 700 * np.sin(a)])
                L.append((p, k * 0.7, None))
        return L

    for f in range(len(out)):
        t = f * DT
        fr = out[f]
        fr += light(NAVY, keys(t, [(0, 0), (2, 0.1), (D - 3, 0.1), (D, 0)]))
        # shininess: fine glitter (narrow glints) coarsens toward the blaze, then fines back down
        shin = keys(t, [(0, 200), (41, 200), (47, 50), (50, 14), (51.5, 14), (56, 220), (D, 400)])
        mix = smoothstep(18, 26, t) * (1 - smoothstep(41, 44, t)) + smoothstep(50, 54, t)
        mix = np.clip(mix, 0, 1)
        gold = side_gold * (1 - mix) + mixed_gold * mix
        # facets wobble a little, as if the house were breathing
        wob = 0.1 * np.sin(2 * np.pi * wob_f * t + wob_p)[:, None] * wob_a
        nrm = unit(normals + wob)
        spec = np.zeros(n)
        tint_acc = np.zeros((n, 3))
        for p, s, tint in lamp_path(t):
            if s <= 0:
                continue
            to_l = p - P
            dist = np.linalg.norm(to_l, axis=1)
            hv = unit(to_l / dist[:, None] + to_view)
            g = np.clip((nrm * hv).sum(1), 0, 1) ** shin * s * 1.6 / (1 + (dist / 2200) ** 2)
            spec += g
            if tint is not None:
                tint_acc += g[:, None] * tint
        spec = np.clip(spec * (1 + shin / 300), 0, 2.0)
        mat = gold[:, None] * GOLD + (1 - gold[:, None]) * SILVER
        # coloured lamps tint the glints
        tw = np.clip(tint_acc.sum(1) / np.maximum(spec, 1e-6), 0, 1)[:, None]
        colr = mat * (1 - 0.5 * tw) + 0.5 * tw * np.where(spec[:, None] > 0, tint_acc / np.maximum(tint_acc.max(1, keepdims=True), 1e-6), 0)
        fr += perc(np.clip(spec, 0, 1))[:, None] * colr
        # the brightest glints burn to white
        fr += light(WHITE, np.clip(spec - 0.8, 0, 1) * 0.8)
        # the blaze: the coarse grain lights the roof broadly at the peak
        blaze = keys(t, [(46, 0), (50, 0.28), (51.5, 0.28), (54, 0)])
        if blaze > 0:
            fr += light(mat, blaze * (0.6 + 0.4 * np.clip((nrm * to_view).sum(1), 0, 1)))
    np.clip(out, 0, 1, out=out)
    return out
