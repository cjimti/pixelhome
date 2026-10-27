"""Candles in the Windows: A candle stands in each front window, two under the Left wing, three
under the Right and one either side of the front door on the porch, and each one throws a warm pool
of light up onto the roofline above it, with its own flicker and slow sway, into the deep blue night
between. A wreath hangs over the door. Now and then the front door opens: lamplight spills out on
the porch, and the draught travels out along the house so each candle bows in turn by its distance
from the door. Once in a while a candle gutters out and is relit with the flare of a match."""
import numpy as np
from pixelhome.fx import DT, hexc, perc, light, smoothstep, lerp, Flicker, nframes, looped

CODE = 'XM10'
TITLE = 'Candles in the Windows'
KIND = 'ambient'
DESCRIPTION = ('A candle in every front window throws a warm pool onto the roof above it. Now and then '
               'the front door opens and the draught makes each candle bow in turn.')

NIGHT = hexc('#0c1a5a')
FLAME = hexc('#ff7a18')
FLAME_HOT = hexc('#ffb050')
DOOR = hexc('#ffa040')
WREATH = hexc('#10a030')
BOW = hexc('#e01010')
MATCH = hexc('#fff0c0')
FLOOR = 0.1
LOOP = 170.0
WINDOWS = [('Left', -480), ('Left', -310), ('Porch Front', -95), ('Porch Front', 55),
           ('Right', 270), ('Right', 420), ('Right', 560)]


def render(G, seed=30):
    rng = np.random.default_rng(seed)
    n = G.N
    P = G.pos
    pd = G.pd
    pf = G.seg['Porch Front']
    door_x = -20.0
    door_pd = G.pd[pf[np.argmin(np.abs(P[pf, 0] - door_x))]]
    cand = []
    for name, wx in WINDOWS:
        idx = G.seg[name]
        k = idx[np.argmin(np.abs(P[idx, 0] - wx))]
        cand.append(k)
    cand = np.array(cand)
    nc = len(cand)
    cpd = pd[cand]
    pool_w = rng.uniform(46, 60, nc)
    on_pf = G.seg_of == 'Porch Front'
    xpf = P[:, 0] - door_x

    def draw(D):
        out = np.zeros((nframes(D), n, 3), np.float32)
        slow = Flicker(rng, nc, 0.08, 0.4)
        mid = Flicker(rng, nc, 0.7, 2.0)
        sway = Flicker(rng, nc, 0.05, 0.15)
        night = Flicker(rng, n, 0.02, 0.08)
        doors, t = [], rng.uniform(20, 35)
        while t < D:
            doors.append((t, rng.uniform(6, 10)))
            t += rng.uniform(45, 70)
        outs = [(int(rng.integers(nc)), rng.uniform(5, D - 15)) for _ in range(max(1, int(D / 55)))]
        for f in range(len(out)):
            t = f * DT
            fl = 1 + 0.08 * slow(t) + 0.03 * mid(t)
            shift = 4 * sway(t)                                # the flame leans, the pool slides
            door_open = 0.0
            for ts, dur in doors:
                door_open = max(door_open, smoothstep(ts, ts + 1.2, t) * (1 - smoothstep(ts + dur, ts + dur + 1.5, t)))
                # the draught: reaches each candle by distance from the door, dips it, recovers
                for c in range(nc):
                    ta = ts + 0.6 + abs(cpd[c] - door_pd) / 260
                    u = t - ta
                    if -0.5 < u < 4:
                        fl[c] *= 1 - 0.45 * np.exp(-((u - 0.4) / 0.5) ** 2) + 0.06 * np.sin(6 * u) * np.exp(-u)
                        shift[c] += 10 * np.sign(cpd[c] - door_pd) * np.exp(-((u - 0.4) / 0.7) ** 2)
            match = np.zeros(nc)
            for c, ts in outs:
                u = t - ts
                if 0 < u < 9:
                    # gutters out over a second, stays dark, a match flares and the wick catches
                    fl[c] *= keys_out(u)
                    match[c] = np.exp(-((u - 6.2) / 0.25) ** 2)
            I_c = np.clip(fl, 0, None)
            # the pool follows the roof (path distance), so light spills round a corner
            pool = np.exp(-(np.abs(pd[:, None] - (cpd + shift)[None]) / pool_w[None]) ** 2)
            core = np.exp(-((pd[:, None] - (cpd + shift)[None]) / 5) ** 2)
            I = (pool * (0.27 * I_c)[None]).sum(1) + (core * (0.12 * I_c)[None]).sum(1)
            hot = np.clip((core * I_c[None]).sum(1), 0, 1)
            col = lerp(FLAME, FLAME_HOT, hot[:, None] * 0.7)
            buf = light(NIGHT, 0.12 * (1 + 0.1 * night(t)) * (1 - smoothstep(0.05, 0.3, I)))
            buf += perc(np.clip(I, 0, 0.42))[:, None] * col
            buf += light(MATCH, ((core * (0.4 * match)[None]).sum(1)))
            # wreath over the door, and the door's lamplight when it opens
            ring = np.exp(-((np.abs(xpf) - 14) / 6) ** 2) * on_pf
            bow = np.exp(-((xpf + 0) / 3.5) ** 2) * on_pf
            buf = buf * (1 - 0.8 * np.clip(ring + bow, 0, 1))[:, None]
            buf += light(WREATH, 0.3 * ring) + light(BOW, 0.32 * bow)
            spill = door_open * np.exp(-(np.abs(pd - door_pd) / 90) ** 2) * (1 - 0.6 * bow)
            buf += light(DOOR, 0.3 * spill)
            out[f] = buf
        return out
    return looped(draw, LOOP, floor=(FLOOR, NIGHT))


def keys_out(u):
    if u < 1.2:
        return 1 - smoothstep(0, 1.2, u) * 0.97
    if u < 6.2:
        return 0.03
    return 0.03 + 0.97 * smoothstep(6.2, 7.6, u)
