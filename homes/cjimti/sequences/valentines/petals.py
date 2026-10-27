"""Petals: an all-night fall of rose petals through real 3-D space. Each petal drifts down from above the
roof, fluttering and tumbling on its own path, and only lights the pixels it comes close to, so it seems
to float into the roofline out of the dark. Petals that land on a run stay where they fell, fading from
blush to wine over half a minute; ones that miss the roof (most of the porch notch is empty air) glow
briefly as they pass and fall on. Now and then a slow breeze runs along the roof and nudges the
fallen petals along."""
import numpy as np
from pixelhome.fx import DT, hexc, perc, light, smoothstep, lerp, Flicker, nframes, looped

CODE = 'VD08'
TITLE = 'Petals'
KIND = 'ambient'
DESCRIPTION = ('Rose petals fall slowly through the air around the house, glowing as they near the roof. '
               'Some land and fade where they fell; a slow breeze now and then moves them along.')

ROSE = hexc('#ff2448')
DEEP = hexc('#ff0010')
BLUSH = hexc('#ff5a50')
CREAM = hexc('#ffb890')
WINE = hexc('#a00008')
FLOOR_COLOR = hexc('#c00818')
FLOOR = 0.1
LOOP = 160.0


def render(G, seed=28):
    rng = np.random.default_rng(seed)
    P = G.pos[G.path]
    pdp = G.pd[G.path]
    L = G.length
    palette = [ROSE, ROSE, DEEP, BLUSH, BLUSH, CREAM]

    def draw(D):
        F = nframes(D)
        out = np.zeros((F, G.N, 3), np.float32)
        bed = Flicker(rng, G.N, 0.03, 0.15)
        # petals: spawn time, start point, fall speed, sway, tumble, colour
        n = int(D * 1.8)
        t0 = np.sort(rng.uniform(-12, D, n))
        x0 = rng.uniform(-720, 760, n)
        z0 = rng.uniform(-700, -100, n)
        H = rng.uniform(150, 260, n)
        v = rng.uniform(16, 26, n)
        sw_a = rng.uniform(15, 40, n)
        sw_f = rng.uniform(0.08, 0.2, n)
        sw_p = rng.uniform(0, 2 * np.pi, n)
        tum_f = rng.uniform(0.15, 0.4, n)
        cols = [palette[k] for k in rng.integers(len(palette), size=n)]
        drift = rng.uniform(-6, 6, n)

        def where(i, t):
            s = t - t0[i]
            ang = 2 * np.pi * sw_f[i] * s + sw_p[i]
            return np.array([x0[i] + drift[i] * s + sw_a[i] * np.sin(ang), 150 + H[i] - v[i] * s,
                             z0[i] + 0.6 * sw_a[i] * np.cos(ang)])

        t_land = t0 + H / v
        landed = {}                                      # petal -> path distance where it lies
        for i in range(n):
            q = where(i, t_land[i])
            d = np.hypot(P[:, 0] - q[0], P[:, 2] - q[2])
            k = int(np.argmin(d))
            if d[k] < 30:
                landed[i] = pdp[k]
        offs = np.zeros(n)
        gusts = [(tg, rng.choice([-1, 1])) for tg in np.arange(rng.uniform(10, 25), D, rng.uniform(35, 50))]

        for f in range(F):
            t = f * DT
            I = FLOOR + 0.025 * bed(t)
            buf = np.zeros((G.N, 3))
            gust = np.zeros(G.N)
            gdir = np.zeros(G.N)
            for tg, sgn in gusts:
                front = (t - tg) * 70
                x = pdp if sgn > 0 else L - pdp
                g = np.exp(-((x - front) / 160) ** 2) * (-400 < front < L + 400)
                gdir = np.where(g > gust, sgn, gdir)
                gust = np.maximum(gust, g)
            buf += light(FLOOR_COLOR, I + 0.05 * gust)
            live = np.nonzero((t0 < t) & (t < t_land + 40))[0]
            for i in live:
                s = t - t0[i]
                tum = 0.7 + 0.3 * np.sin(2 * np.pi * tum_f[i] * s) ** 2
                fade_in = smoothstep(0, 3, s)
                a = t - t_land[i]
                settle = smoothstep(0, 1.2, a) if i in landed else 0.0
                if settle < 1:                       # in the air (a landing petal hands over smoothly)
                    q = where(i, t)
                    if q[1] > 150 - 60:
                        d = np.linalg.norm(P - q, axis=1)
                        buf += light(cols[i], 0.36 * tum * fade_in * (1 - settle) * np.exp(-(d / 34) ** 2))
                if settle > 0:                       # lying on the roof, nudged by the breeze
                    k = np.argmin(np.abs(pdp - landed[i] - offs[i]))
                    offs[i] += 28 * DT * gust[k] * gdir[k]
                    life = np.exp(-a / 16) * (1 - smoothstep(30, 40, a))
                    col = lerp(cols[i], WINE, smoothstep(0, 25, a)[()] if False else smoothstep(0, 25, a))
                    buf += light(col, 0.36 * settle * life * np.exp(-((pdp - landed[i] - offs[i]) / 9) ** 2))
            out[f][G.path] = buf
        return out
    return looped(draw, LOOP, floor=(FLOOR, FLOOR_COLOR))
