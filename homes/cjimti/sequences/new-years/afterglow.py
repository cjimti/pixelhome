"""Afterglow: After midnight, fireworks keep going across town. Each far-off burst washes the house
from its own direction (the side of the roof that faces it catches more), softened by drifting
smoke that scatters the light where it is thick. Slow, dim, all night."""
import numpy as np
from pixelhome.fx import DT, hexc, perc, keys, smoothstep, lerp, smooth_noise, nframes, looped

CODE = 'NY08'
TITLE = 'Afterglow'
KIND = 'ambient'
DESCRIPTION = 'Fireworks far across town: each burst washes the roof softly from its own direction through drifting smoke.'

SMOKE = hexc('#1c2470')
FLOOR_COLOR = hexc('#202a78')
FLOOR = 0.11
TINTS = [hexc(c) for c in ('#ffa030', '#ff4060', '#40a0ff', '#40e090', '#b070ff', '#ffd890', '#c8d8ff')]
LOOP = 150.0


def render(G, seed=28):
    rng = np.random.default_rng(seed)
    P = G.pos
    xz = P[:, [0, 2]]
    centre = xz.mean(0)
    rel = xz - centre
    radius = np.linalg.norm(rel, axis=1).max()

    def draw(D):
        n = G.N
        out = np.zeros((nframes(D), n, 3), np.float32)
        # smoke: two layers of smooth noise over x drifting slowly in opposite directions
        span = np.linspace(-1500, 1500, 1201)
        layer_a = smooth_noise(rng, span, 260)
        layer_b = smooth_noise(rng, span, 140)
        bursts = []
        t = rng.uniform(1, 4)
        while t < D:
            az = rng.uniform(-np.pi * 0.85, np.pi * 0.85)                 # mostly from the street side
            dist = rng.uniform(0.5, 1.0)
            bursts.append((t, np.array([np.sin(az), np.cos(az)]), TINTS[rng.integers(len(TINTS))],
                           rng.uniform(0.6, 1.0) * dist, rng.uniform(2.5, 4.5)))
            # sometimes two or three close together, like a distant finale
            t += rng.choice([rng.uniform(1.2, 2.2), rng.uniform(4, 9)], p=[0.3, 0.7])
        for f in range(len(out)):
            t = f * DT
            sa = np.interp(P[:, 0] - 9 * t, span, layer_a)
            sb = np.interp(P[:, 0] + 5 * t + 0.3 * P[:, 2], span, layer_b)
            smoke = np.clip(0.5 + 0.35 * sa + 0.25 * sb, 0, 1)
            I = 0.14 + 0.05 * smoke
            col = np.tile(SMOKE, (n, 1)) * perc(I)[:, None]
            for tb, d, tint, a, dec in bursts:
                u = t - tb
                if u < 0 or u > dec * 4:
                    continue
                env = smoothstep(0, 0.9, u) * np.exp(-max(0.0, u - 0.9) / dec)
                facing = 0.5 + 0.5 * (rel @ d) / radius                     # near side catches more
                light_I = env * a * (0.08 + 0.3 * facing ** 1.5) * (0.55 + 0.9 * smoke)
                col += perc(light_I)[:, None] * tint
            out[f][:] = col
        return out
    return looped(draw, LOOP, floor=(FLOOR, FLOOR_COLOR))
