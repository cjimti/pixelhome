"""Lanterns: Each roof section is its own lantern, breathing at its own pace, with the corners glowing
like hooks. A lamplighter's glow walks the roof end to end, brightening each lantern as it passes."""
import numpy as np
from pixelhome.fx import DT, hexc, perc, light, keys, Flicker, nframes, looped

CODE = 'NT3'
TITLE = 'Lanterns'
KIND = 'ambient'
DESCRIPTION = 'Each roof section is a lantern breathing at its own pace. A lamplighter glow walks the roof end to end.'

AMBER = hexc('#ff7010')
FLOOR_COLOR = hexc('#ff4a08')
FLOOR = 0.13


def render(G, seed=13):
    rng = np.random.default_rng(seed)
    segs = G.path_segments()
    colors = [hexc(c) for c in ('#ff5a08', '#ff3000', '#ff7010', '#ff2000', '#ff6008', '#ff3a00')]

    def draw(D):
        n = G.N
        out = np.zeros((nframes(D), n, 3), np.float32)
        idx = np.arange(n, dtype=float)
        period = rng.uniform(7, 14, len(segs))
        phase = rng.uniform(0, 2 * np.pi, len(segs))
        shimmer = Flicker(rng, n, 0.1, 0.5)
        lit = np.zeros(len(segs))
        corners = np.zeros(n)
        for _, s in segs:
            for end in (s.min(), s.max()):
                corners = np.maximum(corners, np.exp(-((idx - end) / 2.5) ** 2))
        walk = [(0, 0.0), (20, 0.0), (140, n - 1.0), (170, n - 1.0), (290, 0.0), (D + 1, 0.0)]
        for f in range(len(out)):
            t = f * DT
            p = keys(t, walk)
            buf = np.zeros((n, 3))
            for i, (name, s) in enumerate(segs):
                inside = s.min() - 3 <= p <= s.max() + 3
                lit[i] = min(1.0, lit[i] + DT / 3) if inside else lit[i] * (1 - DT / 25)
                ph = (idx[s] - s.min()) / max(1, len(s) - 1)
                vign = 0.8 + 0.2 * np.sin(np.pi * ph)
                breath = 0.24 + 0.035 * np.sin(2 * np.pi * t / period[i] + phase[i])
                I = (breath + 0.1 * lit[i]) * vign * (1 + 0.05 * shimmer(t)[s])
                buf[s] = perc(I)[:, None] * colors[i]
            buf += light(AMBER, 0.26 * corners)
            buf += light(AMBER, 0.3 * np.exp(-((idx - p) / 14) ** 2))
            out[f] = 0
            out[f][G.path] = buf
        return out
    return looped(draw, 330.0, floor=(FLOOR, FLOOR_COLOR))
