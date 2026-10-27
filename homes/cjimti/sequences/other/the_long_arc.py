"""The Long Arc: A vast circle of light lies in the horizontal plane of the roof, much bigger than the
house, its centre drifting on a slow orbit around the property while its radius breathes. Only its
edge is ever on the roof: where the circle crosses each straight run it lights a soft gold point, so
the points slide along the runs, pair up, meet and part, turn corners and leave through the free ends,
all from one shape bending through real 3-D space. Inside the arc the roof is warm, outside it is deep
blue, so the long curve slowly carries the warmth across the whole house and back. Seamless loop."""
import numpy as np
from pixelhome.fx import DT, hexc, perc, light, smoothstep, lerp, Flicker, nframes, looped

CODE = 'OT09'
TITLE = 'The Long Arc'
KIND = 'ambient'
DESCRIPTION = ('One huge, slow circle of light bends through the house. Where its edge crosses the roof, '
               'soft gold points slide along and around the corners, with warmth inside the curve.')

GOLD = hexc('#ffa83a')
INSIDE = hexc('#ff8a30')
OUTSIDE = hexc('#1028d0')
FLOOR_COLOR = hexc('#1424c0')
FLOOR = 0.1
LOOP = 170.0


def render(G, seed=29):
    rng = np.random.default_rng(seed)
    xz = G.pos[:, [0, 2]]
    shimmer = Flicker(rng, G.N, 0.05, 0.2)

    def draw(D):
        out = np.zeros((nframes(D), G.N, 3), np.float32)
        for f in range(len(out)):
            t = f * DT
            w = 2 * np.pi * t / LOOP
            c = np.array([16 + 760 * np.cos(w), -400 + 560 * np.sin(w) + 120 * np.sin(2 * w + 1.0)])
            R = 820 + 160 * np.sin(2 * w + 0.4) + 60 * np.sin(3 * w + 2.0)
            d = np.linalg.norm(xz - c, axis=1) - R
            edge = np.exp(-(d / 26) ** 2)
            halo = np.exp(-np.abs(d) / 110)
            ins = smoothstep(40, -160, d)
            # a faint echo ring inside the first, like the arc's own memory
            d2 = np.linalg.norm(xz - c, axis=1) - 0.62 * R
            echo = np.exp(-(d2 / 30) ** 2)
            sh = 1 + 0.04 * shimmer(t)
            buf = light(lerp(OUTSIDE, INSIDE, ins[:, None]), (0.15 + 0.03 * ins) * sh)
            buf += light(GOLD, (0.32 * edge + 0.09 * halo) * sh)
            buf += light(GOLD, 0.16 * echo * sh)
            out[f] = buf
        return out
    return looped(draw, LOOP, floor=(FLOOR, FLOOR_COLOR))
