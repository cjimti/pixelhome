"""Fairy Rings: all night, rings open slowly on the ground around the house, like mushroom rings
in a field: each starts at a point in the yard or under the roof and grows outward through real
space (x, z). Where a ring crosses the roofline its light splits into two points that slide apart,
fast where the ring meets a run edge-on and slow where it runs alongside, so the wings, the porch
sides and Side each read the same circle differently. A few gold motes drift on a moss floor."""
import numpy as np
from pixelhome.fx import DT, hexc, perc, light, smoothstep, Flicker, nframes, looped

CODE = 'SP09'
TITLE = 'Fairy Rings'
KIND = 'ambient'
DESCRIPTION = ('Rings open slowly in the yard and drift through the house like mushroom rings in a field, '
               'pale mint over moss, with a few gold motes.')

MOSS = hexc('#2a6a08')
RING = hexc('#a8ffd0')
RING_WARM = hexc('#e8ffa0')
MOTE = hexc('#ffc040')
LOOP = 160.0


def render(G, seed=91):
    rng = np.random.default_rng(seed)

    def draw(Dur):
        F = nframes(Dur)
        out = np.zeros((F, G.N, 3), np.float32)
        n = G.N
        x = G.pd[G.path]
        xz = G.pos[G.path][:, [0, 2]]
        breathe = Flicker(rng, n, 0.03, 0.15)
        rings = []
        t = -40.0
        while t < Dur:
            c = np.array([rng.uniform(-750, 780), rng.uniform(-800, 100)])
            rings.append((t, c, rng.uniform(16, 26), rng.uniform(0, 1)))
            t += rng.uniform(6, 10)
        motes = [(rng.uniform(0, G.length), rng.choice([-1, 1]) * rng.uniform(6, 14), rng.uniform(0, 2 * np.pi),
                  rng.uniform(0.1, 0.25)) for _ in range(7)]
        for f in range(F):
            t = f * DT
            I = 0.13 * (1 + 0.15 * breathe(t))
            fr = light(MOSS, I)
            R = np.zeros(n)
            warm = np.zeros(n)
            for t0, c, sp, w in rings:
                age = t - t0
                if age < 0 or age > 50:
                    continue
                r = 30 + sp * age
                d = np.linalg.norm(xz - c, axis=1)
                a = smoothstep(0, 8, age) * (1 - smoothstep(34, 50, age))
                band = a * np.exp(-((d - r) / 38) ** 2)
                R = np.maximum(R, band)
                warm = np.maximum(warm, band * w)
            mix = (warm / np.maximum(R, 1e-6))[:, None]
            fr += light(RING * (1 - mix) + RING_WARM * mix, 0.27 * R)
            for p0, v, ph, fq in motes:
                p = (p0 + v * t) % G.length
                tw = 0.5 + 0.5 * np.sin(2 * np.pi * fq * t + ph)
                tw *= smoothstep(0, 60, p) * smoothstep(G.length, G.length - 60, p)   # fade out at the free ends
                fr += light(MOTE, 0.22 * tw * np.exp(-((x - p) / 6) ** 2))
            out[f][G.path] = fr
        return out
    return looped(draw, LOOP, floor=(0.1, MOSS))
