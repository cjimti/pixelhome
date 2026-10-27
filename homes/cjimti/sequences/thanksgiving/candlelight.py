"""Candlelight: An all-night table of real candles, not a string of flickering pixels. Each candle is a
small flame with a halo of light scattered onto the pixels around it: a row of them close together
down the Porch Front (the table), pairs in the wing fronts like windows, a few spread along the porch
sides and the Side. Each flame is a little damped pendulum: it breathes on its own, and when someone
walks past, the draft travels along the roof, and each flame in turn leans away, sways and settles,
its light sliding sub-pixel to one side and back."""
import numpy as np
from pixelhome.fx import DT, hexc, light, Flicker, nframes, looped

CODE = 'TG07'
TITLE = 'Candlelight'
KIND = 'ambient'
DESCRIPTION = ('A long table of candles down the porch and in the windows, each with its own halo. When someone '
               'walks past, the draft reaches each flame in turn and it leans, sways and settles.')

CORE = hexc('#ffb060')
HALO = hexc('#ff6a10')
FLOOR_COLOR = hexc('#ff4206')
FLOOR = 0.1
LOOP = 160.0


def render(G, seed=27):
    rng = np.random.default_rng(seed)
    pdp = G.pd[G.path]
    n = G.N
    # candle positions along the path
    table = list(1335 + 39 * np.arange(9))                                  # Porch Front: the table
    windows = [560, 600, 760, 800, 2120, 2160, 2330, 2370, 2470]           # wing fronts, in pairs
    sides = [960, 1120, 1250, 1720, 1860, 1990, 90, 230, 370]               # porch sides and the Side
    C = np.array(sorted(table + windows + sides), float)
    M = len(C)
    is_table = np.isin(C, table)
    size = np.where(is_table, 1.0, 0.85)

    def draw(Dt):
        out = np.zeros((nframes(Dt), n, 3), np.float32)
        breath = Flicker(rng, M, 0.05, 0.3)
        nerve = Flicker(rng, M, 0.4, 0.9)
        x = np.zeros(M)
        v = np.zeros(M)
        w0 = 2 * np.pi * rng.uniform(0.55, 0.8, M)                         # each flame's sway frequency
        zeta = 0.22
        drafts = []                                                          # (time, start pd, direction, strength)
        t = rng.uniform(6, 14)
        while t < Dt:
            kind = rng.integers(0, 3)
            start, d = [(0.0, 1), (G.length, -1), (1486.0, 0)][kind]
            drafts.append((t, start, d, rng.uniform(0.6, 1.0)))
            t += rng.uniform(16, 30)
        dist = np.abs(pdp[None, :] - C[:, None])
        halo_k = np.exp(-dist / 16) * 0.55 + np.exp(-dist / 55) * 0.12
        for f in range(len(out)):
            t = f * DT
            force = np.zeros(M)
            for td, s0, d, a in drafts:
                u = t - td
                if 0 < u < 25:
                    if d == 0:                                               # porch door: spreads both ways
                        front = np.abs(C - s0) - 120 * u
                        sgn = np.sign(C - s0)
                    else:
                        front = (C - s0) * d - 120 * u
                        sgn = d
                    force += a * sgn * np.exp(-(front / 90) ** 2) * np.exp(-u / 14)
            acc = -w0 ** 2 * x - 2 * zeta * w0 * v + 34.0 * force
            v += acc * DT
            x += v * DT
            sway = np.clip(x, -1.5, 1.5)
            I = 0.34 * size * (1 + 0.1 * breath(t) + 0.03 * nerve(t)) * (1 - 0.35 * np.abs(sway) / 1.5)
            lean = 5.0 * sway                                                # sub-pixel lean of the flame
            core = np.exp(-((pdp[None, :] - (C + lean)[:, None]) / 3.0) ** 2)
            flame = (I[:, None] * core).max(0)
            glow = (I[:, None] * halo_k).sum(0)
            col = HALO + (CORE - HALO) * np.clip(flame / 0.34, 0, 1)[:, None]
            out[f][G.path] = light(1.0, np.maximum(flame, glow)) * col
        return out
    return looped(draw, LOOP, floor=(FLOOR, FLOOR_COLOR))
