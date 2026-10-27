"""Mountaintop: A dawn rising behind the house, done with real geometry. Before first light a few faint
stars burn over the roof. Then the sky warms from the back of the house forward: the pixels farthest
from the street (the free end of Side, the Porch Front) see the light first, and the colour line moves
toward the street through indigo, violet, rose and amber, reaching the wing fronts last.

The sun itself is a disc far behind the porch. Everything is projected from a viewer standing in the
street, so the set-back Porch Front, which sits highest and closest to the horizon in that view, is the
mountaintop: the corona gathers there, the disc crests over its middle, and slow crepuscular rays
(angular stripes around the sun's screen position) wheel across the wings. Then full warm morning."""
import numpy as np
from pixelhome.fx import DT, hexc, perc, light, keys, lerp, smoothstep, colormap, Flicker, nframes

CODE = 'OT06'
TITLE = 'Mountaintop'
KIND = 'show'
DESCRIPTION = ('A dawn rises behind the house. The back of the roof sees the light first, the colour moves '
               'toward the street, and the sun crests over the porch with rays wheeling across the wings.')

SKY = colormap([(-1.0, (0.0, 0.004, 0.03)), (-0.6, (0.004, 0.012, 0.12)), (-0.3, (0.05, 0.02, 0.32)),
                (0.0, (0.32, 0.05, 0.3)), (0.25, (0.85, 0.16, 0.18)), (0.5, (1.0, 0.36, 0.06)),
                (0.8, (1.0, 0.6, 0.2)), (1.1, (1.0, 0.78, 0.5))])
SUN = hexc('#ffd8a0')
CORONA = hexc('#ff9a30')
STAR = hexc('#b8c8ff')


def render(G, seed=26):
    rng = np.random.default_rng(seed)
    D = 80.0
    F = nframes(D)
    out = np.zeros((F, G.N, 3))
    P = G.pos
    # perspective from a viewer in the street
    C = np.array([16.0, 320.0, 1500.0])
    depth = C[2] - P[:, 2]
    X = (P[:, 0] - C[0]) / depth
    Y = (P[:, 1] - C[1]) / depth
    back = (-P[:, 2] - 140) / 500                 # 0 at the wing fronts .. ~1 at the back
    stars = rng.random(G.N) < 0.07
    tw = Flicker(rng, G.N, 0.08, 0.35)
    shimmer = Flicker(rng, G.N, 0.1, 0.5)
    SZ = -5000.0

    for f in range(F):
        t = f * DT
        e = keys(t, [(0, -1.2), (8, -1.0), (30, -0.15), (46, 0.35), (56, 0.75), (66, 0.95)])
        ep = e + 0.55 * back - 0.25
        lvl = keys(t, [(0, 0.0), (3, 1.0)]) * np.clip(0.12 + 0.55 * smoothstep(-1.0, 1.0, ep), 0, 1)
        col = SKY(ep)
        col = col / np.maximum(col.max(1, keepdims=True), 1e-6)
        I = lvl * (1 + 0.03 * shimmer(t))
        # morning settles to a moderate level so the house is not driven to full white
        I *= keys(t, [(56, 1), (68, 0.72)])
        buf = perc(I)[:, None] * col

        # stars before dawn
        sI = keys(t, [(0, 0), (3, 0.5), (16, 0.5), (28, 0)]) * stars * np.clip(0.6 + 0.4 * tw(t), 0, 1)
        buf += light(STAR, sI)

        # the sun far behind the porch, seen from the street
        ys = keys(t, [(0, -2200), (40, -900), (54, -215), (72, 40)])
        Xs = 0.0
        Ys = (ys - C[1]) / (C[2] - SZ)
        dx_, dy_ = X - Xs, Y - Ys
        r = np.hypot(dx_, dy_)
        vis = keys(t, [(30, 0), (50, 1)])
        corona = vis / (1 + (r / 0.05) ** 2)
        disc = smoothstep(0.022, 0.012, r) * keys(t, [(49, 0), (54, 1), (70, 1)])
        phi = np.arctan2(dy_, dx_)
        rays = keys(t, [(50, 0), (56, 1), (72, 1), (78, 0)]) * (0.5 + 0.5 * np.cos(9 * phi + 0.25 * t)) ** 4 \
            * np.exp(-r / 0.35)
        buf += light(CORONA, 0.8 * corona) + light(SUN, np.clip(disc, 0, 1)) + light(SUN, 0.75 * rays)
        buf *= keys(t, [(0, 1), (75, 1), (80, 0)])
        out[f] = buf
    return out
