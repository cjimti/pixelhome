"""Light and Darkness: A bistable reaction-diffusion field (the Nagumo equation) runs along the whole
roof path. Its threshold decides which state wins: while it is high, darkness spreads in from the two
free ends and eats the warm evening glow, until only one candle on the porch is left. The candle gutters
and holds. Then the threshold falls, and light becomes the winning state: a travelling front pours
out of the candle in both directions, turns every corner and pushes the dark out through the free ends.

    u_t = D u_xx + r u (1 - u) (u - a(t))

Front speed is proportional to (1/2 - a), so the same physics runs the darkness in and the light out.
The leading edge of each front is drawn as a rim: cold blue for the dark, gold for the light."""
import numpy as np
from pixelhome.fx import DT, hexc, perc, light, keys, lerp, smoothstep, smooth_noise, Flicker, nframes

CODE = 'MK02'
TITLE = 'Light and Darkness'
KIND = 'show'
DESCRIPTION = ('Darkness creeps in from both ends of the roof until one candle on the porch is left. '
               'It holds, and then its light pours out around every corner and drives the dark away.')

NIGHT = hexc('#1020c0')
COLD = hexc('#4060ff')
EMBER = hexc('#ff5a10')
WARM = hexc('#ffb064')
WHITE = hexc('#ffd8b0')
GOLD = hexc('#ff9a28')


def render(G, seed=22):
    rng = np.random.default_rng(seed)
    D_ = 74.0
    F = nframes(D_)
    out = np.zeros((F, G.N, 3))
    pdp = G.pd[G.path]
    L = G.length
    dx = 4.0
    x = np.arange(0, L + dx, dx)
    n = len(x)
    centre = 0.5 * (G.pd[G.seg['Porch Front']].min() + G.pd[G.seg['Porch Front']].max())
    Dc, r = 3600.0, 8.0
    sub = int(np.ceil(DT / (0.4 * dx * dx / Dc)))
    h = DT / sub
    u = np.full(n, 0.0)
    het = 0.06 * smooth_noise(rng, x, 160)                 # uneven ground: fronts lean and stall a little
    cand = np.exp(-((x - centre) / 6.0) ** 2)
    cand_pix = np.exp(-((pdp - centre) / 5.0) ** 2)
    flick = Flicker(rng, 1, 1.5, 5.0)
    shimmer = Flicker(rng, G.N, 0.2, 0.9)
    prev = u.copy()

    for f in range(F):
        t = f * DT
        a = keys(t, [(0, 0.5), (5, 0.84), (26, 0.84), (31, 0.16), (60, 0.16)])
        ends_dark = t < 30
        # the evening glow at the start, then the candle as a source
        glow0 = keys(t, [(0, 0), (4, 0.95)])
        cand_lvl = keys(t, [(0, 1), (24, 1), (25.5, 0.45), (26.2, 0.72), (27.0, 0.3), (28.5, 1.0)])
        for _ in range(sub):
            lap = np.empty(n)
            lap[1:-1] = u[2:] - 2 * u[1:-1] + u[:-2]
            lap[0] = u[1] - u[0]
            lap[-1] = u[-2] - u[-1]
            u = u + h * (Dc * lap / dx ** 2 + r * u * (1 - u) * (u - (a + het)))
            if t < 4.5:
                u = np.maximum(u, glow0 * (1 - np.exp(-np.minimum(x, L - x) / 30)))
            if ends_dark and t > 4.5:
                k = 1 - smoothstep(4.5, 7.0, t)
                u[:3] *= k
                u[-3:] *= k
            u = np.maximum(u, cand * cand_lvl * glow0)
            u = np.clip(u, 0, 1)
        vel = (u - prev) / DT
        prev = u.copy()
        up = np.interp(pdp, x, u)
        vp = np.interp(pdp, x, vel)

        dark_rim = np.clip(-vp / 1.0, 0, 1) * smoothstep(6, 9, t)
        light_rim = np.clip(vp / 0.8, 0, 1) * smoothstep(28.5, 31, t)
        # once the light has won it keeps going: slow swells roll outward from the candle
        swell = keys(t, [(44, 0), (52, 1), (64, 1), (68, 0)]) * (
            0.5 + 0.5 * np.sin(2 * np.pi * (np.abs(pdp - centre) / 520 - t / 4.5))) ** 3
        end = keys(t, [(62, 1), (70, 0.0)])

        buf = light(NIGHT, 0.09 * (1 - up) * keys(t, [(0, 0), (4, 1), (68, 1), (74, 0)]))
        warmth = up * (0.46 + 0.04 * shimmer(t)[G.path] + 0.16 * swell) * end
        col = lerp(EMBER, WARM, smoothstep(0.1, 0.8, up)[:, None])
        if t > 36:
            col = lerp(col, WHITE, keys(t, [(36, 0), (54, 0.55)]) * up[:, None])
        buf += perc(warmth)[:, None] * col
        buf += light(COLD, 0.55 * dark_rim)
        buf += light(GOLD, 0.7 * light_rim * end)

        # the last candle: its own flame on top of the field
        fl = 1 + 0.12 * flick(t)[0]
        cI = cand_lvl * fl * keys(t, [(0, 0), (6, 0.0), (14, 0.9), (70, 0.9), (73, 0.6), (74, 0)])
        buf += light(GOLD, cI * cand_pix)
        out[f][G.path] = buf
    return out
