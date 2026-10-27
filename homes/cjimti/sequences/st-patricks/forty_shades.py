"""Forty Shades: an all-night moiré of greens. One slow wave is defined per pixel (a period of 7.3
pixels), the other in true distance along the roof (31 units). Because the runs have different pixel
spacing (4.0 on the wings, 6.1 on Side, 7.5 on Porch Right) the two waves beat at a different scale
on every run: long rolling swells on the wings, a tighter shimmer on the porch sides. A third, very
slow field moves the colour through bottle, moss, emerald and mint, shifted by depth so the porch
and the wings never quite agree."""
import numpy as np
from pixelhome.fx import DT, hexc, perc, light, smoothstep, colormap, nframes, looped

CODE = 'SP08'
TITLE = 'Forty Shades'
KIND = 'ambient'
DESCRIPTION = ('Bottle, moss, emerald and mint drift through each other in slow moiré swells, at a '
               'different scale on every run of the roof.')

GREENS = colormap([(0.0, hexc('#004a1c')), (0.3, hexc('#3a7400')), (0.55, hexc('#00b040')),
                   (0.8, hexc('#20e080')), (1.0, hexc('#60ffb0'))])
GOLD = hexc('#ffb020')
LOOP = 150.0


def render(G, seed=81):
    rng = np.random.default_rng(seed)

    def draw(Dur):
        F = nframes(Dur)
        out = np.zeros((F, G.N, 3), np.float32)
        k = np.arange(G.N, dtype=float)              # path index
        x = G.pd[G.path]
        z = G.pos[G.path][:, 2]
        depth = (z.max() - z) / (z.max() - z.min())   # 0 at the wing fronts, 1 at the back
        ph = rng.uniform(0, 2 * np.pi, 3)
        for f in range(F):
            t = f * DT
            a1 = 2 * np.pi * k / 7.3 + 2 * np.pi * t / 41 + ph[0]
            a2 = 2 * np.pi * x / 31 - 2 * np.pi * t / 57 + ph[1]
            # cos a1 + cos a2 = 2 cos((a1+a2)/2) cos((a1-a2)/2): a fine carrier inside a beat envelope
            env = np.cos((a1 - a2) / 2) ** 2
            carrier = 0.5 + 0.5 * np.cos((a1 + a2) / 2) ** 2
            s = env * (0.55 + 0.45 * carrier)           # swells where the two waves agree
            q = 0.5 + 0.38 * np.sin(2 * np.pi * (x / 1100 - t / 75) + 2.2 * depth + ph[2]) + 0.12 * (s - 0.25)
            I = 0.12 + 0.26 * s
            fr = light(GREENS(np.clip(q, 0, 1)), I)
            fr += light(GOLD, 0.2 * smoothstep(0.82, 1.0, s) * smoothstep(0.6, 0.9, q))
            out[f][G.path] = fr
        return out
    return looped(draw, LOOP, floor=(0.1, hexc('#0a5a20')))
