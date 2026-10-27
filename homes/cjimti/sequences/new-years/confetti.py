"""Confetti: Cannons at the corners fire volleys of confetti into the air above the house. Each
piece falls in 3-D at its own terminal speed, swaying side to side and flashing as it tumbles, and
the ones that hit the roofline stick, until the roof is a mosaic of gold, silver and rose. Then a
gust sweeps the roof from the back of the house to the free right end, shoving every piece into a
drift that pours off the end. One last piece takes its time coming down."""
import numpy as np
from pixelhome.fx import DT, hexc, perc, light, keys, smoothstep, nframes

CODE = 'NY05'
TITLE = 'Confetti'
KIND = 'show'
DESCRIPTION = 'Confetti cannons fire from the corners; pieces flutter down and stick to the roof until it is a mosaic. A gust sweeps it all off the right end. One last piece takes its time.'

COLS = np.array([hexc(c) for c in ('#ffb030', '#ffd890', '#c8d8ff', '#ff7088', '#ffa080', '#40d0c0', '#ffffff')])
WEIGHTS = np.array([0.24, 0.16, 0.2, 0.14, 0.12, 0.07, 0.07])
NAVY = hexc('#081440')
WHITE = hexc('#fff4e4')

T_GUST, V_GUST = 40.0, 300.0
T_LAST = 50.5


def render(G, seed=25):
    rng = np.random.default_rng(seed)
    D = 60.0
    out = np.zeros((nframes(D), G.N, 3))
    n = G.N
    pdp = G.pd[G.path]
    L = G.length
    # volleys: (time, path index of the cannon, pieces, spread along the path)
    volleys = [(3.0, 179, 150, 520), (3.3, 380, 150, 520), (14.0, 0, 130, 700), (14.3, 500, 130, 700),
               (24.0, 261, 200, 900), (24.0, 331, 200, 900), (31.0, 81, 130, 600), (31.4, 440, 130, 600)]
    flakes = []
    for tv, ci, k, spread in volleys:
        # each piece is aimed at a spot on the roof near the cannon, high above it
        target = np.clip(pdp[ci] + rng.normal(0, spread / 2.2, k), 0, L)
        h0 = rng.uniform(150, 450 if tv < 10 else 700, k)                    # height above the roof at its apex
        vt = rng.uniform(45, 110, k)                     # terminal fall speed (flat pieces fall slowly)
        t_apex = tv + 0.6 + h0 / 900                     # shot up fast, then flutters down
        t_hit = t_apex + h0 / vt
        sway_a = rng.uniform(6, 22, k)
        sway_f = rng.uniform(0.6, 1.4, k)
        tumble_f = rng.uniform(1.5, 4.5, k)
        ph = rng.uniform(0, 2 * np.pi, (k, 2))
        sticks = rng.random(k) < 0.85
        col = COLS[rng.choice(len(COLS), k, p=WEIGHTS)]
        for i in range(k):
            flakes.append((tv, t_apex[i], t_hit[i], target[i], h0[i], vt[i], sway_a[i], sway_f[i], tumble_f[i],
                           ph[i, 0], ph[i, 1], sticks[i], *col[i], ci))
    F = np.array(flakes, float)
    tv, ta, th, tgt, h0, vt, sa, sf, tf, p0, p1, st = (F[:, j] for j in range(12))
    fcol = F[:, 12:15]
    cann = F[:, 15].astype(int)
    land = tgt + sa * np.sin(2 * np.pi * sf * th + p0)       # where it ends up along the path
    gust_off = rng.uniform(0, 1, len(F)) ** 0.7 * 150                    # how far ahead of the gust front it rides
    bed_tw = rng.uniform(0, 2 * np.pi, len(F))

    # the last piece
    last_x = 0.5 * (pdp[261] + pdp[331])
    last_col = COLS[0]

    for f in range(len(out)):
        t = f * DT
        buf = np.zeros((n, 3))
        buf += light(NAVY, keys(t, [(0, 0), (2, 0.1), (D - 3, 0.1), (D, 0)]))

        # cannon pops: a flash at the corner and a streak of light up into the dark
        for tvv, ci, k, spread in volleys:
            u = t - tvv
            if 0 <= u < 0.8:
                buf += light(WHITE, 1.1 * np.exp(-u / 0.1) * np.exp(-((pdp - pdp[ci]) / 25) ** 2))
                # a burst of glitter thrown out both ways along the roof from the muzzle
                for sgn in (-1, 1):
                    r = pdp[ci] + sgn * 260 * (1 - np.exp(-u / 0.25))
                    buf += light(COLS[1], 0.7 * np.exp(-u / 0.35) * np.exp(-((pdp - r) / 30) ** 2))

        front = (t - T_GUST) * V_GUST
        # pieces in the air, close enough to the roofline to be seen: height above the roof -> glow
        air = (t >= ta) & (t < th)
        if air.any():
            i = np.where(air)[0]
            hgt = (th[i] - t) * vt[i]
            pos = tgt[i] + sa[i] * np.sin(2 * np.pi * sf[i] * t + p0[i])
            glint = 0.25 + 0.75 * np.abs(np.cos(2 * np.pi * tf[i] * t + p1[i])) ** 6
            vis = np.exp(-(hgt / 70) ** 2) * glint
            near = vis > 0.01
            if near.any():
                w = np.exp(-((pdp[:, None] - pos[None, near]) / 4.5) ** 2)
                buf += w @ (fcol[i[near]] * perc(np.clip(vis[near], 0, 1))[:, None])
        # landed pieces: lying on the roof, catching a little light as the air moves
        landed = (t >= th) & (st > 0)
        if landed.any():
            i = np.where(landed)[0]
            p = land[i].copy()
            age = t - th[i]
            settle = 0.5 + 0.5 * np.exp(-age / 0.4)
            shine = 0.5 + 0.12 * np.sin(1.3 * t + bed_tw[i])
            if t >= T_GUST:
                # the gust picks them up as it reaches them and shoves them along into a drift
                ride = np.maximum(p, front - gust_off[i])
                moving = ride > p
                p = np.where(moving, ride, p)
                shine = np.where(moving, 0.3 + 0.35 * np.abs(np.cos(9 * t + bed_tw[i])) ** 4, shine)
            keep = p < L + 10
            w = np.exp(-((pdp[:, None] - p[None, keep]) / 2.8) ** 2)
            bed = w @ (fcol[i[keep]] * perc(np.clip(shine[keep] * settle[keep], 0, 1))[:, None])
            # where pieces pile up, the pile is a heap of colour, not a white-hot spot
            peak = bed.max(1, keepdims=True)
            buf += bed / np.maximum(1, peak / 0.55)
        # pieces that miss fall past the roof and fade below it
        miss = (t >= th) & (st == 0) & (t < th + 1.0)
        if miss.any():
            i = np.where(miss)[0]
            vis = np.exp(-(((t - th[i]) * vt[i]) / 50) ** 2)
            w = np.exp(-((pdp[:, None] - land[i][None, :]) / 4.5) ** 2)
            buf += w @ (fcol[i] * perc(0.6 * vis)[:, None])

        # the gust itself: a faint cool breath leading the drift
        if T_GUST <= t < T_GUST + L / V_GUST + 1:
            buf += light(hexc('#a0c0ff'), 0.25 * np.exp(-((pdp - front) / 60) ** 2))

        # one last piece, slowly, tumbling, onto the middle of the porch
        if t >= T_LAST - 6:
            hgt = max(0.0, (T_LAST - t) * 30)
            pos = last_x + 14 * np.sin(2 * np.pi * 0.45 * t)
            glint = 0.3 + 0.7 * abs(np.cos(2 * np.pi * 1.1 * t)) ** 6 if hgt > 0 else 0.75
            vis = np.exp(-(hgt / 70) ** 2) * glint
            vis *= keys(t, [(D - 3, 1), (D, 0)])
            if t >= T_LAST:
                vis = 0.75 * keys(t, [(T_LAST, 1), (T_LAST + 0.15, 1.3), (T_LAST + 0.6, 1), (D - 3, 1), (D, 0)])
            buf += light(last_col, vis * np.exp(-((pdp - pos) / 4.0) ** 2))
        out[f][G.path] = buf
    np.clip(out, 0, 1, out=out)
    return out
