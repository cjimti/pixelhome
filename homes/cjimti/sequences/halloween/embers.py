"""Embers: A deep red bed. Random pixels slowly catch orange and fade; some glitch sideways a pixel
or two before going out; a few sparks drift along the roof."""
import numpy as np
from pixelhome.fx import DT, hexc, perc, smoothstep, lerp, nframes, looped, candle_bed

CODE = 'NT2'
TITLE = 'Embers'
KIND = 'ambient'
DESCRIPTION = 'A deep red bed where random pixels slowly catch orange and fade, some glitching sideways first.'

EMBER_RED = hexc('#ff0800')
ORANGE = hexc('#ff4a00')
FLOOR_COLOR = hexc('#ff4a08')
FLOOR = 0.13
LOOP = 300.0


def render(G, seed=12):
    rng = np.random.default_rng(seed)
    def draw(D):
        n = G.N
        out = np.zeros((nframes(D), n, 3), np.float32)
        idx = np.arange(n)
        bed = candle_bed(rng, n, 0.19, 0.15)
        E = int(D * 7)
        t0 = rng.uniform(-4, D, E)
        p0 = rng.integers(0, n, E).astype(float)
        att = rng.uniform(0.6, 1.6, E)
        hold = rng.uniform(0.3, 2.5, E)
        dec = rng.uniform(1.8, 4.5, E)
        peak = rng.uniform(0.28, 0.42, E)
        glitchy = rng.random(E) < 0.3
        hop_t = np.sort(rng.uniform(0, 1, (E, 3)), 1) * (att + hold)[:, None]
        hop_d = rng.choice([-2, -1, 1, 2], (E, 3)) * glitchy[:, None]
        S = int(D / 9)
        s0 = rng.uniform(-8, D, S)
        sp = rng.uniform(0, n, S)
        sv = rng.uniform(6, 18, S) * rng.choice([-1, 1], S)
        slen = rng.uniform(5, 9, S)
        for f in range(len(out)):
            t = f * DT
            I = bed(t)
            u = t - t0
            live = (u > 0) & (u < att + hold + dec)
            uu = u[live]
            env = np.where(uu < att[live], smoothstep(0, 1, uu / att[live]),
                           np.where(uu < att[live] + hold[live], 1.0,
                                    1 - smoothstep(0, 1, (uu - att[live] - hold[live]) / dec[live])))
            pos = (p0[live] + (hop_d[live] * (uu[:, None] > hop_t[live])).sum(1)).astype(int) % n
            hot = np.zeros(n)
            np.maximum.at(hot, pos, env * peak[live])
            for a, p, v, L in zip(s0, sp, sv, slen):
                us = t - a
                if 0 < us < L:
                    x = (p + v * us) % n
                    e = 0.36 * np.sin(np.pi * us / L) ** 2
                    w = np.clip(1 - np.abs(idx - x), 0, 1)
                    hot = np.maximum(hot, e * w)
            col = lerp(EMBER_RED, ORANGE, smoothstep(0.18, 0.38, np.maximum(I, hot))[:, None])
            out[f][G.path] = perc(np.maximum(I, hot))[:, None] * col
        return out
    return looped(draw, LOOP, floor=(FLOOR, FLOOR_COLOR))
