"""Flypast: True 3-D. Six aircraft, one per branch colour, fly real paths through the space of the
house: an echelon from behind the house toward the street, then a V formation across it, each leaving
a fading contrail on the pixels below. Last they come in from the street in a tight diamond, rock
their wings in salute over the porch, and break: each peels off on a curve to its own corner or free
end of the house and settles there, so the roof ends holding the six colours at its six points."""
import numpy as np
from pixelhome.fx import DT, hexc, light, keys, lerp, smoothstep, Flicker, nframes

CODE = 'VT02'
TITLE = 'Flypast'
KIND = 'show'
DESCRIPTION = ('Six aircraft in the six branch colours fly over and across the house in formation, trailing '
               'contrails, rock their wings in salute over the porch, then break to the six corners of the roof.')

BRANCHES = [hexc(c) for c in ('#ffae1c',   # Army: gold
                              '#1c34ff',   # Navy: navy blue
                              '#ff1a14',   # Marine Corps: scarlet
                              '#ff5a0c',   # Coast Guard: orange
                              '#7aaeff',   # Air Force: sky blue
                              '#e4e8ff')]  # Space Force: silver
NAVY = hexc('#1c34ff')
SILVER = hexc('#c8d2ff')
GOLD = hexc('#ff9a24')
CONTRAIL = hexc('#a8b4e8')


def render(G, seed=22):
    rng = np.random.default_rng(seed)
    D = 72.0
    out = np.zeros((nframes(D), G.N, 3))
    P = G.pos
    Y = 150.0
    stars = Flicker(rng, G.N, 0.05, 0.3)
    trail = np.zeros((G.N, 3))
    cx = 16.0
    # diamond slots (x, z offsets) and where each branch breaks to: the free ends and corners, in
    # left-to-right order so the fan-out never crosses
    DIAMOND = [(-75, 60), (-150, 130), (0, 0), (75, 60), (150, 130), (0, 190)]
    targets = [G.path[i] for i in (0, 80, 260, 331, 500, 178)]
    bulge = np.array([[-120, 0, 120], [-140, 0, 80], [-40, 0, -60], [40, 0, -60], [140, 0, 80], [-60, 0, 160]], float)

    def glow(p, r=95.0):
        dxz = np.hypot(P[:, 0] - p[0], P[:, 2] - p[2])
        h = abs(p[1] - Y)
        rr = r + 0.45 * h                        # a higher aircraft lights a wider, fainter patch
        return np.exp(-(dxz / rr) ** 2) * np.exp(-(h / 380) ** 2) * (r / rr)

    for f in range(len(out)):
        t = f * DT
        fr = out[f]
        bg = keys(t, [(0, 0), (3, 0.12), (66, 0.12), (D, 0)])
        fr += light(NAVY, bg * (1 + 0.12 * stars(t)))
        planes = []                                # (position, colour, brightness)

        # 1: echelon from behind the house to the street
        if 3 <= t < 17:
            u = (t - 3) / 13.5
            zl = lerp(-1050, 450, u)
            for k, col in enumerate(BRANCHES):
                x = -560 + k * 232
                z = zl - k * 70
                planes.append((np.array([x, Y, z]), col, 1.0))
        # 2: V formation across the front, left to right, apex leading
        if 18 <= t < 32:
            xl = lerp(-1000, 1250, (t - 18) / 14)
            slots = [(0, 0), (-1, -1), (-1, 1), (-2, -2), (-2, 2), (-1.6, 0)]
            for (r, s), col in zip(slots, BRANCHES):
                planes.append((np.array([xl + r * 150, Y, -390 + s * 125]), col, 1.0))
        # 3: diamond from the street, a wing-waggle salute over the porch, then the break:
        #    each aircraft peels off to its own corner or end of the house and settles there
        if 35 <= t:
            u = smoothstep(35, 43.5, t)
            zc = lerp(700, -380, u)
            rock = 38 * np.sin(2 * np.pi * 1.1 * (t - 43.5)) * (43.5 < t < 46.2) * np.sin(np.pi * np.clip((t - 43.5) / 2.7, 0, 1))
            brk = smoothstep(46.5, 53.5, t)
            for k, col in enumerate(BRANCHES):
                ox, oz = DIAMOND[k]
                p0 = np.array([cx + ox + rock * (1 + 0.004 * ox), Y, zc + oz])
                tgt = P[targets[k]]
                mid = 0.5 * (p0 + tgt) + bulge[k]
                q = (1 - brk) ** 2 * p0 + 2 * (1 - brk) * brk * mid + brk ** 2 * tgt     # curved peel-off
                hold = keys(t, [(53.5, 1.0), (56, 0.55), (D - 6, 0.5), (D, 0)])
                planes.append((q, col, hold * (1 + 0.08 * np.sin(2 * np.pi * (t - 53.5) / (5 + k)) * (t > 53.5))))

        cur = np.zeros((G.N, 3))
        for p, col, b in planes:
            cur += light(col, b * glow(p))
        trail = np.maximum(trail * (1 - DT / 1.6), cur * 0.4)
        trail_tint = lerp(trail, CONTRAIL * trail.max(1, keepdims=True), 0.35)
        fr += np.maximum(cur, trail_tint)

        # settled: silver light reaches out along the roof from the six points until they join
        if t > 57:
            reach = keys(t, [(57, 5), (65, 260)])
            dpt = np.min([np.abs(G.pd - G.pd[k]) for k in targets], axis=0)
            fr += light(SILVER, keys(t, [(57, 0), (60, 0.2), (D - 4, 0.2), (D, 0)]) * np.exp(-(dpt / reach) ** 2))

    return out
