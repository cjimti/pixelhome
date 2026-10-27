"""Dyeing the River: the roofline is a river flowing from the free back end of Side to the free end
of Right, with a slow current (faster on the straights, eddying at the corners). Boats come in from
upstream and throw orange powder, the real dye, in arcs; where it lands it turns green. The dye is a
field carried by the current (semi-Lagrangian advection) and spread by diffusion, so it streaks,
pools in the corner eddies and drains out downstream. One boat stops on the porch and spins
doughnuts. By the end the whole river is the famous shocking green, with the sun glinting off it."""
import numpy as np
from pixelhome.fx import DT, hexc, perc, light, keys, lerp, smoothstep, smooth_noise, Flicker, nframes

CODE = 'SP06'
TITLE = 'Dyeing the River'
KIND = 'show'
DESCRIPTION = ('The roof is a river. Boats come downstream throwing orange powder that turns green where it '
               'lands; the current carries it round the corners until the whole river glows.')

WATER = hexc('#043850')
FOAM = hexc('#b0e0ff')
POWDER = hexc('#ff5000')
DYE = hexc('#00e048')
DYE_HOT = hexc('#18ff58')
BOAT = hexc('#fff0d8')
SUN = hexc('#fff0b0')


def render(G, seed=61):
    rng = np.random.default_rng(seed)
    D = 52.0
    F = nframes(D)
    out = np.zeros((F, G.N, 3))
    n = G.N
    x = G.pd[G.path]
    L = G.length
    corners = np.array([491.0, 894.0, 1311.0, 1660.0, 2033.0])
    pfc = (1311.0 + 1660.0) / 2

    dx = 4.0
    g = np.arange(0, L + dx, dx)
    eddy = 1 - 0.6 * np.exp(-((g[:, None] - corners[None, :]) / 45) ** 2).sum(1)
    v_base = 48.0 * (1 + 0.3 * smooth_noise(rng, g, 260)) * eddy
    c = np.zeros(len(g))              # green dye
    o = np.zeros(len(g))              # orange powder still dissolving
    Dif = 220.0
    tex_noise = smooth_noise(rng, np.arange(0, 6000, 4.0), 70, octaves=3)
    glint = Flicker(rng, n, 1.0, 4.0)
    wake = np.zeros(n)

    donut = [(16.0, pfc)]
    for k in range(9):
        donut.append((16.0 + 1.15 * (k + 1), pfc + (110 if k % 2 == 0 else -110)))
    boats = [
        dict(k=[(3.0, -30), (30.0, L + 30)], spray=(5.0, 28.0)),
        dict(k=[(9.0, -30), (16.0, pfc)] + donut + [(28.0, pfc), (35.0, L + 30)], spray=(10.0, 33.0)),
        dict(k=[(21.0, -30), (41.0, L + 30)], spray=(22.0, 39.5)),
    ]
    px = np.zeros(0)
    pv = np.zeros(0)
    pa = np.zeros(0)
    pl = np.zeros(0)
    prev_bp = [None] * len(boats)

    for f in range(F):
        t = f * DT
        # current: semi-Lagrangian advection; upstream (out of view) gets dyed too, later on
        v = v_base * (1 + 0.15 * np.sin(2 * np.pi * (g / 700 - t / 9)))
        src = g - v * DT
        c = np.interp(src, g, c, left=float(keys(t, [(26, 0), (38, 0.9)])))
        o = np.interp(src, g, o, left=0.0)
        lap = np.zeros_like(c)
        lap[1:-1] = c[2:] - 2 * c[1:-1] + c[:-2]
        c += Dif * DT * lap / (dx * dx)
        conv = o * (1 - np.exp(-0.9 * DT))
        o -= conv
        c += conv
        np.minimum(c, 1.6, out=c)

        # boats and their powder
        fade = keys(t, [(0, 0), (2, 1), (D - 4, 1), (D - 0.3, 0)])
        fr = np.zeros((n, 3))
        for bi, b in enumerate(boats):
            if not (b['k'][0][0] <= t <= b['k'][-1][0]):
                continue
            bp = float(keys(t, b['k']))
            vel = 0.0 if prev_bp[bi] is None else (bp - prev_bp[bi]) / DT
            prev_bp[bi] = bp
            fr += light(BOAT, 0.8 * np.exp(-((x - bp) / 5) ** 2))
            wake = np.maximum(wake, 0.5 * min(1, abs(vel) / 80) * np.exp(-((x - bp) / 9) ** 2))
            if b['spray'][0] <= t <= b['spray'][1]:
                m = 3
                px = np.concatenate([px, np.full(m, bp)])
                pv = np.concatenate([pv, rng.uniform(-150, 90, m) + 0.3 * vel])
                pa = np.concatenate([pa, np.zeros(m)])
                pl = np.concatenate([pl, rng.uniform(0.35, 0.7, m)])
        # powder in the air, landing on the water
        if len(px):
            pa += DT
            px += pv * DT
            landed = pa >= pl
            for xl in px[landed]:
                o += 0.09 * np.exp(-((g - xl) / 10) ** 2)
            keep = ~landed
            px, pv, pa, pl = px[keep], pv[keep], pa[keep], pl[keep]
            if len(px):
                h = np.sin(np.pi * np.clip(pa / pl, 0, 1))
                k = (0.35 + 0.5 * h)[:, None] * np.exp(-((x[None, :] - px[:, None]) / 3.0) ** 2)
                fr += light(POWDER, k.max(0))
        wake *= 0.95

        cs = np.interp(x, g, c)
        os_ = np.interp(x, g, o)
        tex = np.interp((x - 48.0 * t) % 6000, np.arange(0, 6000, 4.0), tex_noise)
        flow = 1 + 0.25 * tex
        dye = np.clip(cs, 0, 1)
        water_I = 0.16 * (1 - 0.7 * dye) * flow
        fr += light(WATER, water_I * fade)
        fr += light(lerp(DYE, DYE_HOT, smoothstep(0.7, 1.4, cs)[:, None]), (0.55 * dye ** 0.7) * flow * fade)
        fr += light(POWDER, 0.7 * np.clip(os_, 0, 1) ** 0.8 * fade)
        fr += light(FOAM, wake * flow)
        sun = smoothstep(40, 46, t)
        fr += light(SUN, 0.45 * sun * fade * np.clip(glint(t), 0, 1) ** 6 * (0.3 + dye))
        out[f][G.path] = fr
    return out
