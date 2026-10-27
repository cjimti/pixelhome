"""The Sentinel: The porch front is the Tomb of the Unknown Soldier, a pale marble glow with a gold
lamp at each back corner. A sentinel light walks the mat in exactly twenty-one steps (each step
eased, with a small heel glint as it plants), turns to face the tomb, turns again, changes the
rifle to the outer shoulder (its silver glint hops sides) and walks twenty-one steps back. Then the
Changing of the Guard: a gold commander comes up Porch Left, the relief up Porch Right; they meet
at the centre for inspection, the relieved sentinel marches off with the commander, and the new
sentinel begins his own twenty-one."""
import numpy as np
from pixelhome.fx import DT, hexc, light, keys, lerp, smoothstep, Flicker, nframes

CODE = 'VT10'
TITLE = 'The Sentinel'
KIND = 'show'
DESCRIPTION = ('The porch becomes the Tomb of the Unknown Soldier: a sentinel walks twenty-one measured steps, '
               'turns, waits and returns, then the guard is changed.')

NAVY = hexc('#1c34ff')
MARBLE = hexc('#c8d0f0')
GOLD = hexc('#ff9a24')
SENTRY = hexc('#e4eaff')
STEEL = hexc('#a0b0ff')
RELIEF = hexc('#f0f0ff')


def stepper(legs):
    """legs: [(t0, x0, x1, nsteps, step_seconds)] -> position(t), planted-glint(t), direction(t)."""
    def pos(t):
        x, glint, d = legs[0][1], 0.0, np.sign(legs[0][2] - legs[0][1])
        for t0, x0, x1, n, sd in legs:
            if t < t0:
                break
            d = np.sign(x1 - x0) if x1 != x0 else d
            k = (t - t0) / sd
            if k >= n:
                x = x1
                continue
            i, fr = int(k), k - int(k)
            S = (x1 - x0) / n
            x = x0 + S * (i + smoothstep(0, 0.55, fr))
            glint = np.exp(-((fr - 0.56) / 0.05) ** 2)
        return x, glint, d
    return pos


def render(G, seed=30):
    rng = np.random.default_rng(seed)
    D = 84.0
    out = np.zeros((nframes(D), G.N, 3))
    pd = G.pd
    da, db = pd[G.path[261]], pd[G.path[331]]
    pf = (pd >= da - 2) & (pd <= db + 2)
    mid = (da + db) / 2
    xa, xb = mid - 147, mid + 147             # the mat: 21 steps of 14 units
    plf, prf = pd[G.path[179]], pd[G.path[380]]
    breathe = Flicker(rng, G.N, 0.04, 0.15)

    SD = 1.0
    sentry_legs = [(4.0, xa, xb, 21, SD),            # 21 steps
                   (37.0, xb, xa, 21, SD),           # back, after the turns
                   (66.0, xa, mid - 12, 7, 0.9),     # to inspection
                   (73.5, mid - 12, xa, 7, 0.9),     # off with the commander...
                   (80.0, xa, plf + 140, 10, 0.4)]   # ...down Porch Left
    sentry = stepper(sentry_legs)
    cmd = stepper([(58.0, plf + 40, xa - 6, 14, 0.55), (66.0, xa - 6, mid, 7, 0.9),
                   (73.5, mid, xa - 10, 7, 0.9), (80.0, xa - 10, plf + 120, 10, 0.4)])
    relief = stepper([(58.0, prf - 40, xb + 6, 14, 0.55), (66.0, xb + 6, mid + 12, 7, 0.9),
                      (73.5, mid + 12, xa + 4, 12, 0.55), (80.6, xa + 4, xa + 60, 4, SD)])

    ph = (pd % 22.0) - 11.0
    stones = np.exp(-(ph / 2.6) ** 2) * (1 + 0.15 * rng.uniform(-1, 1, G.N))

    def body(x, w=6.0):
        return np.exp(-((pd - x) / w) ** 2)

    for f in range(len(out)):
        t = f * DT
        fr = out[f]
        on = keys(t, [(0, 0), (3, 1), (D - 3, 1), (D, 0)])
        fr += light(NAVY, 0.1 * on * (1 + 0.1 * breathe(t)))
        tomb = 0.3 + 0.03 * breathe(t)
        tomb = tomb + 0.08 * keys(t, [(25.5, 0), (29, 1), (33, 1), (36, 0)])     # facing the tomb
        fr[pf] += light(MARBLE, on * tomb[pf] * (1 - 0.35 * np.abs((pd[pf] - mid) / (db - da) * 2) ** 2))
        # Arlington: rows of small white headstones along every other run of the roof
        fr[~pf] += light(MARBLE, on * 0.2 * stones[~pf])
        for c in (da, db):
            fr += light(GOLD, on * 0.55 * np.exp(-((pd - c) / 5) ** 2))

        # the sentinel; the rifle rides on the shoulder away from the tomb, switching at the turn
        x, g, d = sentry(t)
        if t < 80.0 + 10 * 0.4:
            lvl = 0.85 * on
            if 25.0 < t < 37.0:          # the turns: a short dip as he pivots, twice
                lvl *= 1 - 0.45 * (np.exp(-((t - 25.6) / 0.3) ** 2) + np.exp(-((t - 34.2) / 0.3) ** 2))
            shoulder = -1 if t < 35.5 else 1
            hop = smoothstep(35.0, 35.8, t) if 33 < t < 37 else (0 if t < 35 else 1)
            rifle_off = lerp(-6.5, 6.5, hop)
            fr += light(SENTRY, lvl * body(x))
            fr += light(STEEL, 0.5 * lvl * body(x + rifle_off, 2.2))
            fr += light(SENTRY, 0.45 * g * lvl * body(x, 3))
        # changing of the guard
        if 57.5 < t:
            cx, cg, _ = cmd(t)
            rx, rg, _ = relief(t)
            fade_c = keys(t, [(57.5, 0), (58.5, 1), (82, 1), (84, 0)])
            fr += light(GOLD, 0.8 * fade_c * body(cx))
            fr += light(GOLD, 0.35 * cg * fade_c * body(cx, 3))
            fr += light(RELIEF, 0.85 * fade_c * body(rx))
            fr += light(RELIEF, 0.4 * rg * fade_c * body(rx, 3))
            # inspection: the commander salutes, the relief's rifle glints side to side
            if 68.5 < t < 73.3:
                sal = smoothstep(68.5, 69.0, t) * (1 - smoothstep(72.6, 73.2, t))
                fr += light(GOLD, 0.35 * sal * body(cx, 14))
                spin = np.sin(2 * np.pi * 0.8 * (t - 69.5)) if 69.5 < t < 72.0 else 1.0
                fr += light(STEEL, 0.6 * body(rx + 6.5 * spin, 2.2))
            else:
                fr += light(STEEL, 0.45 * fade_c * body(rx + 6.5, 2.2))
    return out
