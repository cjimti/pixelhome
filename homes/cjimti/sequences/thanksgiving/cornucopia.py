"""Cornucopia: The Side is a woven horn of plenty, narrow at the free back end and opening at the
front-left corner. Harvest spills out of it: pumpkins, gourds, apples, corn and cranberries, each a
body with its own size and mass, rolling with real momentum along the Left wing, up the Porch Left
and onto the porch table, knocking into each other and packing up in a row. Last comes a pumpkin too
big for the horn's mouth. It sticks, the horn strains, it pops free, slams into the back of the row,
and like a Newton's cradle the shock runs the length of the pile and fires the little cranberry at
the front off down the Porch Right and out the end of the house."""
import numpy as np
from pixelhome.fx import DT, hexc, light, keys, smoothstep, Flicker, nframes

CODE = 'TG08'
TITLE = 'Cornucopia'
KIND = 'show'
DESCRIPTION = ('The Side is a horn of plenty. Pumpkins, apples, corn and cranberries roll out with real momentum and '
               'pack up on the porch, until one pumpkin too many sends a cranberry flying out the far end.')

PUMPKIN = hexc('#ff5200')
APPLE = hexc('#c0102a')
GOLD = hexc('#ffb000')
AMBER = hexc('#ff8a18')
CRAN = hexc('#d0183a')
WARM = hexc('#ffc27a')
BROWN = hexc('#7a2c06')
DEEP = hexc('#4a1604')
D = 56.0
MOUTH = 478.0
TABLE = 1486.0


def render(G, seed=28):
    rng = np.random.default_rng(seed)
    F = nframes(D)
    out = np.zeros((F, G.N, 3))
    n = G.N
    pdp = G.pd[G.path]
    weave = Flicker(rng, n, 0.05, 0.2)

    kinds = {'pumpkin': (15, PUMPKIN), 'gourd': (10, GOLD), 'apple': (8, APPLE), 'corn': (13, GOLD),
             'cran': (3.5, CRAN), 'pear': (8, AMBER)}
    order = ['cran'] + list(rng.choice(['pumpkin', 'gourd', 'apple', 'corn', 'cran', 'pear', 'apple', 'cran'], 21))
    spawn_t = 4.0 + np.cumsum(rng.uniform(0.6, 1.7, len(order))) * 0.95
    spawn_t[0] = 4.0
    items = []
    for k, tt in zip(order, spawn_t):
        R, col = kinds[k]
        items.append(dict(R=R, col=col, m=R ** 2, t0=tt, x=MOUTH - 30.0, v=rng.uniform(380, 520), on=False,
                          big=False))
    BIG = dict(R=24, col=PUMPKIN, m=24 ** 2, t0=33.0, x=MOUTH - 45.0, v=0.0, on=False, big=True)
    items.append(BIG)
    stuck_until = 38.6
    shock_t = None
    shot = None                      # the cranberry that gets fired
    slope, visc, coulomb = 70.0, 0.55, 25.0
    SUB = 4
    dt = DT / SUB

    for f in range(F):
        t = f * DT
        for it in items:
            if not it['on'] and t >= it['t0']:
                it['on'] = True
        live = [it for it in items if it['on'] and it is not shot]
        for _ in range(SUB):
            for it in live:
                if it['big'] and t < stuck_until:
                    it['x'] = MOUTH - 24 + 5 * np.sin(2 * np.pi * 3.1 * t) * smoothstep(34.5, 36, t)
                    it['v'] = 0.0
                    continue
                if it['big'] and t >= stuck_until and it.get('popped') is None:
                    it['v'] = 820.0
                    it['popped'] = True
                d = TABLE - it['x']
                a = slope * np.sign(d) * min(1, abs(d) / 40) - visc * it['v']
                if abs(it['v']) > 1e-3:
                    a -= coulomb * np.sign(it['v'])
                it['v'] += a * dt
                if abs(it['v']) < 2 and abs(d) < 400:
                    it['v'] *= 0.9
                it['x'] += it['v'] * dt
            live.sort(key=lambda z: z['x'])
            for _ in range(3):                          # contacts between neighbours
                for a_, b_ in zip(live[:-1], live[1:]):
                    gap = b_['x'] - a_['x'] - (a_['R'] + b_['R'])
                    if gap < 0:
                        if a_['big'] and a_.get('popped') and shock_t is None and a_['v'] > 200:
                            shock_t = t
                            a_['v'] = 0.0
                        ma, mb = a_['m'], b_['m']
                        rel = a_['v'] - b_['v']
                        if rel > 0:
                            e = 0.25
                            j = (1 + e) * rel / (1 / ma + 1 / mb)
                            a_['v'] -= j / ma
                            b_['v'] += j / mb
                        corr = -gap / (ma + mb)
                        if not (a_['big'] and t < stuck_until):
                            a_['x'] -= corr * mb
                        b_['x'] += corr * ma
        if shot is not None:
            shot['v'] -= 0.35 * shot['v'] * DT
            shot['x'] += shot['v'] * DT
        # the shock reaches the front of the row: fire the front cranberry
        if shock_t is not None and shot is None:
            row = sorted([it for it in items if it['on']], key=lambda z: z['x'])
            span = row[-1]['x'] - row[0]['x']
            if t >= shock_t + span / 2600:
                shot = row[-1]
                shot['v'] = 1350.0
                shot['fired'] = t

        buf = np.zeros((n, 3))
        # the horn: woven, narrow at the back, wide at the mouth, strains when the pumpkin is stuck
        horn = pdp < MOUTH + 6
        widen = np.clip(pdp / MOUTH, 0, 1)
        strain = smoothstep(34.5, 36, t) * (1 - smoothstep(stuck_until, stuck_until + 0.4, t))
        tex = 0.6 + 0.4 * np.sin(pdp * 0.42 + 3 * np.sin(pdp * 0.05)) ** 2
        hI = keys(t, [(0, 0), (3, 0.42), (52, 0.42), (56, 0)]) * (0.25 + 0.75 * widen ** 1.5) * tex
        hI = hI * (1 + 0.12 * weave(t) + strain * 0.5 * np.sin(2 * np.pi * 6.2 * t) * widen ** 3)
        buf += light(BROWN, hI * horn) + light(AMBER, 0.35 * hI * horn * widen ** 4)
        # each spill: the mouth gives a small cough of light
        for it in items:
            u = t - it['t0']
            if 0 <= u < 0.5:
                buf += light(WARM, 0.35 * np.exp(-u / 0.15) * np.exp(-((pdp - MOUTH) / 20) ** 2))
        # table glow under the pile
        buf += light(DEEP, keys(t, [(0, 0), (3, 0.12), (52, 0.12), (56, 0)]) * (~horn))

        for it in items:
            if not it['on']:
                continue
            x, R = it['x'], it['R']
            if x - R > G.length + 5:
                continue
            body = np.clip((R - np.abs(pdp - x)) / 2.5 + 0.5, 0, 1)
            roll = 0.72 + 0.28 * np.cos((pdp - x) / R * 1.6 + x / R)       # a highlight that turns as it rolls
            emerge = smoothstep(it['t0'], it['t0'] + 0.25, t)
            I = (0.8 if R > 4 else 1.0) * body * roll * emerge
            buf += light(it['col'], I)
            if it is shot:
                for k in range(1, 10):
                    buf += light(CRAN, 0.6 * (1 - k / 10) * np.exp(-((pdp - x + k * 1350 * DT * 0.8) / 4) ** 2))
        # the shock wave through the row
        if shock_t is not None and t - shock_t < 1.2:
            u = t - shock_t
            row = sorted([it for it in items if it['on'] and it is not shot], key=lambda z: z['x'])
            x0 = row[0]['x']
            front = x0 + 2600 * u
            buf += light(WARM, 0.85 * np.exp(-((pdp - front) / 30) ** 2) * (pdp < row[-1]['x'] + 40) * np.exp(-u / 0.6))
            buf += light(WARM, 0.6 * np.exp(-u / 0.12) * np.exp(-((pdp - x0) / 30) ** 2))
        # plink: the cranberry leaves through the free end
        if shot is not None and shot['x'] > G.length:
            tt = shot.get('out_t')
            if tt is None:
                shot['out_t'] = t
                tt = t
            u = t - tt
            buf += light(WARM, 0.9 * np.exp(-u / 0.2) * np.exp(-((pdp - G.length) / 25) ** 2))
        buf *= keys(t, [(52, 1), (56, 0)])
        out[f][G.path] = buf
    return out
