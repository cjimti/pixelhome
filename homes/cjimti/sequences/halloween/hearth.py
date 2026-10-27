"""Hearth: Every pixel a candle. Slow gusts of wind roll along the roof, flames dip and recover."""
import numpy as np
from pixelhome.fx import DT, hexc, perc, smoothstep, lerp, Flicker, nframes, looped, candle_bed

CODE = 'NT1'
TITLE = 'Hearth'
KIND = 'ambient'
DESCRIPTION = 'Every pixel a candle. Slow gusts roll along the roof; now and then a flame nearly goes out.'

DEEP_ORANGE = hexc('#ff2800')
AMBER = hexc('#ff7010')
FLOOR_COLOR = hexc('#ff4a08')
FLOOR = 0.13
LOOP = 300.0


def render(G, seed=11):
    rng = np.random.default_rng(seed)
    def draw(D):
        n = G.N
        out = np.zeros((nframes(D), n, 3), np.float32)
        pdp = G.pd[G.path]
        bed = candle_bed(rng, n, 0.3)
        flutter = Flicker(rng, n, 1.5, 3.0)
        gusts = []
        t = rng.uniform(5, 15)
        while t < D:
            gusts.append((t, rng.choice([-1, 1]), rng.uniform(70, 130), rng.uniform(0.25, 0.45)))
            t += rng.uniform(18, 40)
        gutters = [(rng.uniform(0, D), rng.integers(n)) for _ in range(int(D / 6))]
        for f in range(len(out)):
            t = f * DT
            I = bed(t)
            gust = np.zeros(n)
            for tg, d, v, a in gusts:
                front = (t - tg) * v
                x = pdp if d > 0 else G.length - pdp
                gust = np.maximum(gust, a * np.exp(-((x - front) / 220) ** 2))
            I = I * (1 - gust) + 0.04 * gust * flutter(t)
            for tg, k in gutters:
                u = t - tg
                if -0.8 < u < 2.5:
                    I[k] *= 1 - 0.65 * (smoothstep(-0.8, 0, u) if u < 0 else 1 - smoothstep(0, 2.5, u))
            col = lerp(DEEP_ORANGE, AMBER, np.clip((I - 0.15) / 0.2, 0, 1)[:, None])
            out[f][G.path] = perc(I)[:, None] * col
        return out
    return looped(draw, LOOP, floor=(FLOOR, FLOOR_COLOR))
