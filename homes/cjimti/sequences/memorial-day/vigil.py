"""Vigil: A candlelight vigil. Every 30 units along the roof a person holds a candle: a small flame with
dark between, the same spacing on every run so the crowd stands evenly round the house. Each flame
breathes on its own and its colour follows its heat, deep orange when low, gold when high; the people
sway a little, so the flames drift by fractions of a pixel. A slow swell, like a hymn being taken up,
passes outward from the middle of the porch to both free ends. Now and then a breeze puts a candle out;
its neighbour leans over, and the flame passes back."""
import numpy as np
from pixelhome.fx import DT, hexc, perc, smoothstep, Flicker, nframes, looped, colormap

CODE = 'MM08'
TITLE = 'Vigil'
KIND = 'ambient'
DESCRIPTION = ('A candlelight vigil around the whole roof: one small flame every few feet, each breathing on its '
               'own. Now and then one goes out and its neighbour leans over to relight it.')

NAVY = hexc('#0b1d4a')
FLAME = colormap([(0.0, hexc('#ff3a00')), (0.5, hexc('#ff7a12')), (1.0, hexc('#ffc060'))])
LOOP = 150.0
GAP = 30.0


def render(G, seed=8):
    rng = np.random.default_rng(seed)

    def draw(D):
        n = G.N
        out = np.zeros((nframes(D), n, 3), np.float32)
        pdp = G.pd[G.path]
        c0 = np.arange(GAP / 2, G.length, GAP)
        K = len(c0)
        slow = Flicker(rng, K, 0.04, 0.25)
        mid = Flicker(rng, K, 0.5, 1.4)
        sway = Flicker(rng, K, 0.05, 0.15, k=2)
        base = rng.uniform(0.27, 0.33, K)
        mid_pd = pdp[296]
        # relight events: (time, candle, neighbour that leans in)
        ev = []
        t = rng.uniform(8, 16)
        while t < D - 10:
            j = int(rng.integers(1, K - 1))
            ev.append((t, j, j + int(rng.choice([-1, 1]))))
            t += rng.uniform(16, 30)
        for f in range(len(out)):
            t = f * DT
            I = base * (1 + 0.1 * slow(t) + 0.04 * mid(t))
            hymn = 0.14 * np.sin(2 * np.pi * (t / 38.0 - np.abs(c0 - mid_pd) / 1400.0)) ** 2
            I = I * (1 + hymn)
            c = c0 + 1.8 * sway(t)
            for te, j, nb in ev:
                u = t - te
                if -0.5 < u < 12:
                    # out over 1.2 s, dark, neighbour leans in (3-6 s), relit with a small flare, settles
                    dim = smoothstep(0, 1.2, u) * (1 - smoothstep(6.0, 7.0, u))
                    flare = 0.12 * np.exp(-((u - 6.6) / 0.5) ** 2)
                    I[j] = I[j] * (1 - 0.97 * dim) + flare
                    lean = smoothstep(3.0, 5.5, u) * (1 - smoothstep(7.0, 10.0, u))
                    c[nb] += (c0[j] - c0[nb]) * 0.62 * lean
            g = np.exp(-((pdp[:, None] - c[None, :]) / 4.6) ** 2)          # (N, K)
            heat = np.clip((I - 0.18) / 0.22, 0, 1)
            col = (g * perc(I)[None, :]) @ FLAME(heat)
            out[f][G.path] = col
        return out
    return looped(draw, LOOP, floor=(0.06, NAVY))
