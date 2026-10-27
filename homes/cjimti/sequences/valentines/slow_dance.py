"""Slow Dance: an all-night waltz. Two soft lights (rose and gold) turn round each other in 3-D space,
surging on the first beat of every slow bar of three, while the couple drifts once round the whole house
per loop: along the Side, over the wings, in and out of the porch notch, and back across the front yard,
where they are only a glimmer on the wing fronts. Pixels light by their real distance to each dancer, so
the pair is seen sweeping across corners and jumping the gap between runs."""
import numpy as np
from pixelhome.fx import DT, hexc, light, smoothstep, lerp, Flicker, nframes, looped, catmull_closed

CODE = 'VD09'
TITLE = 'Slow Dance'
KIND = 'ambient'
DESCRIPTION = ('Two soft lights waltz round each other in the air around the house, one slow bar of three at a '
               'time, drifting once round the whole roof per loop.')

ROSE = hexc('#ff2448')
GOLD = hexc('#ff9a30')
WARM = hexc('#ffb880')
FLOOR_COLOR = hexc('#c00818')
FLOOR = 0.09
LOOP = 150.0
BAR = 3.0


def render(G, seed=29):
    rng = np.random.default_rng(seed)
    P = G.pos[G.path]
    route = np.array([(-596, -560), (-610, -160), (-400, -140), (-215, -230), (-190, -480), (-20, -580),
                      (150, -480), (170, -230), (390, -180), (640, -200), (520, -40), (40, -20),
                      (-450, -40), (-700, -300)], float)
    route3 = np.stack([route[:, 0], np.full(len(route), 150.0), route[:, 1]], 1)

    def draw(D):
        F = nframes(D)
        out = np.zeros((F, G.N, 3), np.float32)
        bed = Flicker(rng, G.N, 0.03, 0.12)
        theta = 0.0
        for f in range(F):
            t = f * DT
            ph = (t % BAR) / BAR
            omega = 2 * np.pi / (2.5 * BAR) * (1 + 0.7 * np.cos(2 * np.pi * ph))   # surge on beat one
            theta += omega * DT
            c = catmull_closed(route3, (t / LOOP) % 1.0)
            r = 95 + 15 * np.sin(2 * np.pi * t / (5 * BAR))       # everything here is periodic in LOOP
            off = np.array([np.cos(theta), 0, np.sin(theta)]) * r
            a, b = c + off, c - off
            da = np.linalg.norm(P - a, axis=1)
            db = np.linalg.norm(P - b, axis=1)
            ga = np.exp(-(da / 85) ** 2)
            gb = np.exp(-(db / 85) ** 2)
            lift = 0.9 + 0.1 * np.cos(2 * np.pi * ph)
            buf = light(FLOOR_COLOR, FLOOR + 0.02 * bed(t))
            buf += light(ROSE, 0.36 * lift * ga) + light(GOLD, 0.34 * lift * gb)
            buf += light(WARM, 0.12 * np.sqrt(ga * gb))       # where they are close, a warm glow between
            out[f][G.path] = buf
        return out
    return looped(draw, LOOP, floor=(FLOOR, FLOOR_COLOR))
