"""Egg Hunt: Painted eggs are hidden all over the roof, invisible in the dark garden. A flashlight
beam from the street searches the house; eggs show their colours only inside the beam, and one
that is held in the light long enough is found: it pops, then flies along the roofline into the
basket on the porch. The last egg, at the far free end, is missed. The beam gives up, and the egg
starts flashing "over here!" until it is found too."""
import numpy as np
from pixelhome.fx import DT, hexc, light, keys, smoothstep, smooth_noise, nframes

CODE = 'EA01'
TITLE = 'Egg Hunt'
KIND = 'show'
DESCRIPTION = 'A flashlight searches the dark garden. Painted eggs show only in its beam; found ones fly into the porch basket. The last one has to shout to be noticed.'


def lin(h):
    """sRGB hex -> linear PWM, so a pastel stays a pastel on the LEDs instead of washing to white."""
    return hexc(h) ** 2.2


GRASS = lin('#2f6b4a')
BEAM = lin('#fff1d6')
SPARK = lin('#fffaf0')
PALETTE = [lin(h) for h in ('#ff8fbf', '#b99cff', '#7ff0bd', '#ffe17a', '#8fcfff', '#ffad85')]

# hiding places, by distance along the path (the last one sits at the free right end)
SPOTS = [1420, 1100, 820, 640, 380, 120, 1850, 2200, 2492]
BEAM_KEYS = [(0.0, 1480), (2.0, 1480), (4.6, 1424), (6.4, 1418), (8.6, 1104), (10.2, 1098), (12.1, 824),
             (13.4, 816), (14.6, 1010), (15.2, 990), (16.4, 642), (17.9, 636), (20.0, 384), (21.4, 377),
             (23.2, 124), (24.6, 118), (27.4, 1846), (28.8, 1854), (31.0, 2196), (32.6, 2204), (34.2, 2372),
             (35.0, 2340), (36.6, 1700), (38.4, 900), (40.2, 330), (42.4, 1480), (48.6, 1480), (50.0, 2488),
             (51.8, 2492), (53.0, 1700), (55.0, 1485)]


def render(G, seed=21):
    rng = np.random.default_rng(seed)
    D = 64.0
    F = nframes(D)
    out = np.zeros((F, G.N, 3))
    pdp = G.pd[G.path]
    pp = G.pos[G.path]
    n = G.N

    def at(s):
        return np.array([np.interp(s, pdp, pp[:, k]) for k in range(3)])

    grass_tex = 0.75 + 0.25 * smooth_noise(rng, pdp, 30)
    wob = [smooth_noise(rng, np.arange(F) * DT, 0.9) for _ in range(2)]   # hand shake

    W = 17.0                                           # egg half-width in path units
    eggs = []
    for k, s in enumerate(SPOTS):
        c1, c2 = PALETTE[k % 6], PALETTE[(k * 2 + 3) % 6]
        eggs.append(dict(s=float(s), c1=c1, c2=c2, kind=k % 4, exp=0.0, found=None))
    eggs[-1]['c1'], eggs[-1]['c2'] = lin('#ffd24a'), lin('#ff8fbf')

    centre = 1485.0
    slots = [centre + 34 * o for o in (0, -1, 1, -2, 2, -3, 3, -4, 4)]

    def egg_light(s0, c1, c2, kind, I):
        """(n,3) light of one painted egg centred at path distance s0."""
        u = (pdp - s0) / W
        m = np.abs(u) < 1.15
        if not m.any():
            return None
        env = np.clip(1 - u ** 2, 0, 1) ** 0.6
        if kind == 0:
            mix = 0.5 + 0.5 * np.tanh(4 * np.sin(u * 3.2 * np.pi))       # stripes
        elif kind == 1:
            mix = np.exp(-((np.abs(u) - 0.5) / 0.18) ** 2)                 # two dots
        elif kind == 2:
            mix = smoothstep(-0.15, 0.15, u)                                # two-tone halves
        else:
            mix = np.exp(-(u / 0.25) ** 2)                                   # centre band
        col = c1 * (1 - mix[:, None]) + c2 * mix[:, None]
        return (env ** 2.2 * I ** 2.2)[:, None] * col

    for f in range(F):
        t = f * DT
        buf = np.zeros((n, 3))
        night = keys(t, [(0, 0), (1.5, 1), (60, 1), (63.5, 0)])
        buf += light(GRASS, 0.2 * night * grass_tex)

        # flashlight spot: path point plus a hand-held wobble, lit by 3-D distance (it spills round corners)
        s_b = keys(t, BEAM_KEYS)
        on = keys(t, [(1.5, 0), (2.6, 1), (42.0, 1), (43.5, 0.35), (48.4, 0.35), (49.0, 1), (54, 1), (55.5, 0)])
        T = at(s_b) + np.array([14 * wob[0][f], 0, 14 * wob[1][f]])
        d = np.linalg.norm(pp - T, axis=1)
        beam = np.exp(-(d / 54) ** 2)
        buf += light(BEAM, 0.55 * on * beam)

        for k, e in enumerate(eggs):
            if e['found'] is None:
                lit = on * np.exp(-((e['s'] - s_b) / 46) ** 2)
                e['exp'] += lit * DT
                if e['exp'] > 0.75:
                    e['found'] = t
                vis = on * beam
                calling = 0.0
                if k == len(eggs) - 1 and 43.5 < t:
                    calling = 0.95 * max(0.0, np.sin(2 * np.pi * (t - 43.5) * 1.3)) ** 3 * smoothstep(43.5, 44.5, t)
                    buf += light(SPARK, 0.35 * calling * np.exp(-((np.abs(pdp - e['s']) - 26) / 7) ** 2))
                I = np.clip(vis * 1.25 + calling, 0, 1)
                gl = egg_light(e['s'], e['c1'], e['c2'], e['kind'], 1.0)
                if gl is not None:
                    buf = buf * (1 - 0.8 * np.clip(I, 0, 1)[:, None] * (np.abs(pdp - e['s']) < W)[:, None]) + gl * (I ** 2.2)[:, None]
                continue
            age = t - e['found']
            slot = slots[k]
            if age < 0.6:                                          # pop
                gl = egg_light(e['s'], e['c1'], e['c2'], e['kind'], 1.0)
                buf += gl * (1 + 0.3 * np.sin(age * 40) * np.exp(-age / 0.3))
                buf += light(SPARK, 0.8 * np.exp(-age / 0.15) * np.exp(-((pdp - e['s']) / (W + 60 * age)) ** 2))
            elif age < 3.4:                                        # fly to the basket along the roof
                u = smoothstep(0.6, 3.4, age)
                s_now = e['s'] + (slot - e['s']) * u
                gl = egg_light(s_now, e['c1'], e['c2'], e['kind'], 0.95)
                buf += gl
                trail = np.exp(-np.abs(pdp - s_now) / 40) * (np.sign(e['s'] - slot) * (pdp - s_now) > 0)
                buf += light(e['c1'], 0.25 * trail * np.sin(np.pi * u))
            else:                                                  # in the basket
                settle = np.exp(-(age - 3.4) / 0.25)
                I = 0.62 + 0.3 * settle
                if t > 54:
                    I += 0.25 * np.sin(np.pi * smoothstep(54, 58, t)) * (0.6 + 0.4 * np.sin(2 * np.pi * (t * 0.8 - k * 0.11)))
                I *= keys(t, [(59, 1), (63.5, 0)])
                buf += egg_light(slot, e['c1'], e['c2'], e['kind'], I)

        # finale: the basket rim glows and the garden wakes
        fin = np.sin(np.pi * smoothstep(54.5, 61, t))
        rim = np.exp(-((pdp - 1313) / 30) ** 2) + np.exp(-((pdp - 1658) / 30) ** 2)
        buf += light(lin('#ffe17a'), 0.5 * fin * rim)
        buf += light(GRASS, 0.18 * fin * grass_tex)
        out[f][G.path] = buf
    return out
