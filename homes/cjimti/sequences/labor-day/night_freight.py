"""Night Freight: A rail yard at night; an endless slow freight drawn only by what it hides.

The roofline is a row of sodium yard lights, warm pools along the track. A long freight rolls
through from the free back end of Side and out the free right end, slow and steady, around every
corner of the house. The cars are never lit: they are silhouettes that block the yard light, so you
read them by their shapes: long boxcars, round-ended tank cars, low flatcars that only dim the
light, hoppers with sloped ends, and the bright slit of light at every coupling. The square ends of boxcars
and hoppers catch a thin glint of lamp light. Dim, slow and seamless all night."""
import numpy as np
from pixelhome.fx import DT, hexc, perc, smoothstep, smooth_noise, Flicker, nframes, looped

CODE = 'LB10'
TITLE = 'Night Freight'
KIND = 'ambient'
DESCRIPTION = ('Sodium yard lights along the roof and a slow freight rolling through, seen only as silhouettes: '
               'boxcars, tank cars, flatcars and hoppers, with light slipping through every coupling.')

SODIUM = hexc('#ff8a26')
SODIUM_HI = hexc('#ffb860')
GLINT = hexc('#c8b8a0')
FLOOR_COLOR = hexc('#4a2208')
FLOOR = 0.08
LOOP = 170.0
SPEED = 38.0


def car_kinds(rng, n):
    """(length, kind) per car. kind: 0 box, 1 tank, 2 flat, 3 hopper."""
    kinds = rng.choice(4, n, p=[0.4, 0.25, 0.15, 0.2])
    lengths = np.choose(kinds, [rng.uniform(78, 92, n), rng.uniform(62, 72, n), rng.uniform(84, 100, n),
                                rng.uniform(56, 66, n)])
    return lengths, kinds


def render(G, seed=30):
    rng = np.random.default_rng(seed)

    def draw(D):
        out = np.zeros((nframes(D), G.N, 3), np.float32)
        s = G.pd[G.path]
        L = G.length
        # yard lights: pools every ~150 units of track
        poles = np.arange(40, L, 150.0) + rng.uniform(-20, 20, len(np.arange(40, L, 150.0)))
        pool = np.exp(-((s[None] - poles[:, None]) / 55) ** 2).sum(0)
        yard = 0.2 + 0.2 * np.clip(pool, 0, 1.1)
        hum = Flicker(rng, G.N, 0.05, 0.2)
        haze = smooth_noise(rng, s, 120)

        # the train: enough cars to cover the run for the whole loop
        n = int((L + SPEED * D) / 70) + 8
        lengths, kinds = car_kinds(rng, n)
        gap = 7.0
        starts = -np.concatenate([[0], np.cumsum(lengths + gap)[:-1]])     # car fronts at t=0 (behind s=0)
        starts += L * 0.98                                                  # start with the house full

        for f in range(len(out)):
            t = f * DT
            head = starts + SPEED * t
            tail = head - lengths
            vis = (head > -5) & (tail < L + 5)
            block = np.zeros(G.N)
            glint = np.zeros(G.N)
            for k in np.nonzero(vis)[0]:
                u = (s - tail[k]) / lengths[k]                      # 0..1 along the car
                inside = smoothstep(-0.02, 0.02, u) * smoothstep(1.02, 0.98, u)
                kind = kinds[k]
                if kind == 0:      # boxcar: square ends, full block
                    occ = 0.86 * inside
                elif kind == 1:    # tank car: rounded ends
                    occ = 0.8 * np.clip(np.sin(np.pi * np.clip(u, 0, 1)) ** 0.35, 0, 1) * inside
                elif kind == 2:    # flatcar: low, only dims
                    occ = 0.42 * inside
                else:              # hopper: sloped ends
                    occ = 0.84 * np.clip(np.minimum(u, 1 - u) / 0.22, 0, 1) * inside
                block = np.maximum(block, occ)
                if kind in (0, 3):
                    glint += 0.12 * (np.exp(-((s - tail[k] - 3) / 2.2) ** 2) + np.exp(-((s - head[k] + 3) / 2.2) ** 2))
            I = yard * (1 + 0.04 * hum(t) + 0.05 * haze) * (1 - block)
            col = perc(I)[:, None] * SODIUM + perc(0.12 * np.clip(pool, 0, 1) * (1 - block))[:, None] * SODIUM_HI
            col += perc(np.clip(glint, 0, 0.3))[:, None] * GLINT
            out[f][G.path] = col
        return out

    return looped(draw, LOOP, floor=(FLOOR, FLOOR_COLOR))
