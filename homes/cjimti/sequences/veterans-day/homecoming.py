"""Homecoming: A story told by four lights. The porch front is home, lit like a window, where two
family lights pace and a small dog light fidgets. A lone traveller appears at the free right end and
walks slowly up the Right wing, hesitating halfway. At the corner the dog spots him first, freezes,
then bolts down Porch Right and runs rings round him; the family follows. They meet, merge into one
bright embrace that blooms over the whole house, and walk home together, the dog ahead."""
import numpy as np
from pixelhome.fx import DT, hexc, light, keys, lerp, smoothstep, Flicker, nframes

CODE = 'VT05'
TITLE = 'Homecoming'
KIND = 'show'
DESCRIPTION = ('A lone light walks in from the far end of the roof toward the lit porch. The dog sees him first '
               'and bolts; the family follows; the welcome blooms over the whole house.')

NAVY = hexc('#1c34ff')
WINDOW = hexc('#ff8a20')
TRAVELLER = hexc('#fff0dc')
MOTHER = hexc('#ffb040')
CHILD = hexc('#ff6a50')
DOG = hexc('#ffc890')
GOLD = hexc('#ff9a24')
RED = hexc('#ff1a14')


def render(G, seed=25):
    rng = np.random.default_rng(seed)
    D = 64.0
    out = np.zeros((nframes(D), G.N, 3))
    pd = G.pd
    L = G.length
    pfc = pd[G.seg['Porch Front']].mean()
    pfi = (pd >= pd[G.path[261]] - 2) & (pd <= pd[G.path[331]] + 2)
    c380 = pd[G.path[380]]
    shimmer = Flicker(rng, G.N, 0.05, 0.3)

    trav = [(2, L + 40), (12, 2290), (14.8, 2290), (15.6, 2275), (22.5, c380 + 30), (23.6, c380 + 30),
            (26.0, 1995), (31.5, 1990), (44, pfc + 25), (D, pfc + 25)]
    meet = 1990.0

    def walker(pos, w, bob_hz, t, prev):
        v = abs(pos - prev) / DT
        bob = 1 - 0.18 * min(1.0, v / 30) * np.abs(np.sin(np.pi * bob_hz * t)) ** 2
        return np.exp(-((pd - pos) / w) ** 2) * bob

    prev = {}
    for f in range(len(out)):
        t = f * DT
        fr = out[f]
        on = keys(t, [(0, 0), (2, 1), (D - 4, 1), (D, 0)])
        fr += light(NAVY, 0.1 * on * (1 + 0.1 * shimmer(t)))
        win = keys(t, [(0, 0), (2, 0.3), (24, 0.3), (27, 0.2), (44, 0.3), (47, 0.5), (D - 4, 0.42), (D, 0)])
        fr[pfi] += light(WINDOW, win * (1 + 0.05 * shimmer(t)[pfi]))

        # positions
        pt = keys(t, trav)
        # mother and child pace the porch, then run to him, then walk home with him
        pace_m = pfc - 60 + 55 * np.sin(2 * np.pi * t / 9.0)
        pace_c = pfc + 70 + 40 * np.sin(2 * np.pi * t / 6.3 + 1.0)
        run = smoothstep(24.3, 27.0, t)
        home = smoothstep(31.5, 44, t)
        pm = lerp(lerp(pace_m, meet - 16, run), pt - 16, home)
        pc = lerp(lerp(pace_c, meet - 7, smoothstep(24.0, 26.6, t)), pt - 8, home)
        # the dog: fidgets, freezes, bolts, runs rings, then trots ahead home
        def fidget(u):
            return pfc + 30 * np.sin(2 * np.pi * u / 2.1) + 25 * np.sin(2 * np.pi * u / 3.7 + 2)
        if t < 22.6:
            pg = fidget(t)
        elif t < 23.5:
            pg = fidget(22.6)
        else:
            start = fidget(22.6)
            bolt = smoothstep(23.5, 25.0, t)
            ring = 38 * np.sin(2 * np.pi * 1.4 * (t - 25.0)) * smoothstep(24.8, 25.4, t) * (1 - 0.6 * home)
            ahead = -40 * home
            pg = lerp(start, pt + ring + ahead, bolt)
        frozen = 22.6 <= t < 23.5

        def draw(name, pos, col, w, hz, lvl):
            p0 = prev.get(name, pos)
            fr[:] += light(col, lvl * walker(pos, w, hz, t, p0) * on)
            prev[name] = pos

        tl = keys(t, [(2, 0), (4, 0.85), (D, 0.85)])
        draw('t', pt, TRAVELLER, 9, 1.8, tl)
        draw('m', pm, MOTHER, 8, 2.2, 0.75)
        draw('c', pc, CHILD, 6, 3.0, 0.7)
        dl = 0.95 if frozen else 0.7 + 0.25 * abs(np.sin(2 * np.pi * 3.2 * t))
        draw('d', pg, DOG, 4.5, 4.0, dl)
        if frozen:                                   # ears up: a tiny double glint
            fr += light(TRAVELLER, 0.5 * np.exp(-((pd - pg - 6) / 2.5) ** 2))

        # the embrace and the welcome
        e = keys(t, [(26.6, 0), (27.4, 1), (30.5, 1), (32, 0.25), (44, 0.25), (45, 0)])
        if e > 0:
            fr += light(GOLD, e * 0.8 * np.exp(-((pd - (meet - 8)) / 22) ** 2))
        tb = t - 27.0
        if tb > 0:
            dd = np.abs(pd - meet)
            ring = np.exp(-((dd - 520 * tb) / 80) ** 2) * np.exp(-tb / 3.5)
            fr += light(GOLD, 0.75 * ring)
            warm = keys(t, [(27, 0), (31, 0.2), (44, 0.16), (D - 4, 0.13), (D, 0)])
            # a gentle bunting of red and silver hangs on the two wing fronts after the welcome
            wing = np.isin(np.arange(G.N), np.concatenate([G.seg['Left'], G.seg['Right']]))
            bunt = 0.5 + 0.5 * np.cos(2 * np.pi * (pd - 6 * np.sin(0.4 * t)) / 90)
            fr += light(GOLD, warm * (1 - 0.7 * wing))
            fr[wing] += light(lerp(hexc('#c8d2ff'), RED, bunt[wing, None]), warm * 0.95 * smoothstep(29, 35, t))
    return out
