"""Wishbone: The porch is the wishbone. Porch Left and Porch Right are its two prongs, the Porch Front
is the keel where they join. The wings are two people gripping the ends: Left in cranberry, Right in
gold. As they pull, the bone shifts toward whoever leads, and the light along it shows the stress in
the bone: dim ivory where it is thick, amber and then white-hot where it is thin and at the roots of
the prongs. Stress above a threshold builds fatigue damage, which crackles. In round one the right
hand slips and the left one flies backwards. In round two the damage piles up at a flaw near the root
of the left prong until the bone snaps there. Both halves recoil, and gold, holding the keel, wins
the wish."""
import numpy as np
from pixelhome.fx import DT, hexc, light, keys, smoothstep, lerp, Flicker, colormap, nframes

CODE = 'TG01'
TITLE = 'Wishbone'
KIND = 'show'
DESCRIPTION = ('The porch is the wishbone and the wings pull it. Light shows the stress in the bone as it creaks and '
               'crackles; one hand slips, they grip again, and it snaps at the weakest spot. Gold makes the wish.')

IVORY = hexc('#ffb070')
CRANBERRY = hexc('#c0102a')
GOLD = hexc('#ffb000')
AMBER = hexc('#ff8a18')
WARM = hexc('#ffe0b8')
BROWN = hexc('#4a1604')
D = 62.0
B0, B1 = 897.0, 2030.0            # bone ends: the grips at the two porch-side corners
FLAW = 1286.0                     # a thin spot near the root of the left prong
T_SLIP, T_SNAP = 18.0, 41.0

stress_map = colormap([(0.0, (1.0, 0.69, 0.44)), (0.35, (1.0, 0.45, 0.12)), (0.6, (1.0, 0.3, 0.03)),
                       (0.85, (1.0, 0.55, 0.15)), (1.0, (1.0, 0.8, 0.55))])


def render(G, seed=31):
    rng = np.random.default_rng(seed)
    F = nframes(D)
    out = np.zeros((F, G.N, 3))
    n = G.N
    pdp = G.pd[G.path]
    LW = pdp < 893                 # Side + Left wing: the left person
    RW = pdp > 2034                # Right wing: the right person
    tremble = Flicker(rng, n, 4.0, 7.0)
    slow = Flicker(rng, n, 0.2, 0.8)
    # bone texture (in bone coordinates): fine grain and a few pores
    sgrid = np.arange(B0 - 200, B1 + 200, 1.0)
    grain = 0.82 + 0.1 * np.sin(sgrid * 0.37) * np.sin(sgrid * 0.061) + 0.08 * np.interp(
        sgrid, sgrid[::9], rng.uniform(-1, 1, len(sgrid[::9])))
    # thickness: prongs thin, keel thick, roots of the prongs where stress concentrates, one flaw
    def weakness(s):
        w = np.where((s > 1311) & (s < 1660), 0.3, 0.55)
        w = w + 0.35 * np.exp(-((s - 1311) / 80) ** 2) + 0.3 * np.exp(-((s - 1660) / 80) ** 2)
        return w + 0.4 * np.exp(-((s - FLAW) / 14) ** 2)

    # the tug: tension and how far the bone has been dragged (+ toward the right person)
    T_keys = [(0, 0), (8.4, 0), (9.2, 0.55), (11, 0.7), (12.5, 0.5), (14, 0.8), (16, 0.65), (17.6, 0.85),
              (T_SLIP, 0.9), (T_SLIP + 0.05, 0), (23.5, 0), (24.5, 0.6), (27, 0.75), (28, 0.6), (30, 0.85),
              (32.5, 0.8), (34, 0.95), (35.5, 0.85), (37.5, 1.0), (39, 0.92), (40.4, 1.08), (T_SNAP, 1.12)]
    X_keys = [(0, 0), (8.4, 0), (10, 9), (11.5, -6), (13, -12), (14.5, 5), (16.2, 14), (17.6, 3), (T_SLIP, 0),
              (T_SLIP + 0.35, -75), (T_SLIP + 0.9, -52), (T_SLIP + 1.5, -63), (21.5, -40), (23.5, 0),
              (26, -8), (28.5, 6), (31, 14), (33, 4), (35, 16), (37.5, 22), (39.5, 18), (T_SNAP, 26)]
    pops = []                                   # crackle: (time, bone coordinate)
    gripL_keys = [(0, 0), (4, 0), (6, 0.2), (T_SLIP, 0.22), (T_SLIP + 0.4, 0.6), (19.5, 0.2), (50, 0.2),
                  (58, 0)]

    for f in range(F):
        t = f * DT
        buf = np.zeros((n, 3))
        buf += light(BROWN, keys(t, [(0, 0), (2, 0.08), (58, 0.08), (62, 0)]) * (1 + 0.2 * slow(t)))
        T = keys(t, T_keys) if t < T_SNAP else 0.0
        T = T * (1 + 0.06 * np.sin(2 * np.pi * 1.3 * t) * (T > 0))
        x = keys(t, X_keys) + (2.5 * np.sin(2 * np.pi * 2.1 * t) * T if t < T_SNAP else 0)
        appear = smoothstep(0.5, 3.5, t)

        # stress and fatigue
        sigma = T * weakness(sgrid)
        rate = np.clip(sigma - 0.5, 0, None) * ((sgrid > B0 + 10) & (sgrid < B1 - 10))
        cr = rate.sum() * DT * 2.2
        for _ in range(rng.poisson(cr) if t < T_SNAP and cr > 0 else 0):
            pr = rate / rate.sum()
            pops.append((t, rng.choice(sgrid, p=pr)))

        # the bone, drawn in its own coordinates s = pd - offset
        if t < T_SNAP:
            s = pdp - x
            inside = np.clip((s - B0) / 3 + 0.5, 0, 1) * np.clip((B1 - s) / 3 + 0.5, 0, 1)
            st = np.interp(s, sgrid, sigma)
            g = np.interp(s, sgrid, grain)
            base = (0.3 * appear) * g
            heat = np.clip(st, 0, 1)
            col = lerp(IVORY, stress_map(heat), np.clip(heat * 1.6, 0, 1)[:, None])
            buf += light(1.0, inside * (base + 0.45 * heat ** 1.5)) * col
        else:
            u = t - T_SNAP
            # two pieces recoil, each a damped spring overshooting and settling
            xl = x - 70 * (1 - np.exp(-u / 0.25) * np.cos(9 * u)) * 1.0
            xr = x + 45 * (1 - np.exp(-u / 0.3) * np.cos(8 * u))
            for lo, hi_, off, who in ((B0, FLAW, xl, 0), (FLAW, B1, xr, 1)):
                s = pdp - off
                inside = np.clip((s - lo) / 3 + 0.5, 0, 1) * np.clip((hi_ - s) / 3 + 0.5, 0, 1)
                g = np.interp(s, sgrid, grain)
                if who == 1:
                    wish = smoothstep(1.2, 4.5, u)
                    gc = lerp(IVORY, GOLD, wish)
                    I = inside * g * (0.3 + 0.25 * wish * (0.7 + 0.3 * np.sin(s * 0.03 - 2.2 * t)))
                    buf += light(1.0, I * keys(t, [(T_SNAP, 1), (55, 1), (61, 0)])) * gc
                else:
                    sulk = keys(t, [(T_SNAP, 0.3), (T_SNAP + 3, 0.22), (50, 0.12), (58, 0)])
                    buf += light(lerp(IVORY, CRANBERRY, smoothstep(0.5, 3, u)), inside * g * sulk)
            # the snap: a hot flash at the break and splinters flying both ways
            buf += light(WARM, np.exp(-u / 0.12) * np.exp(-((pdp - FLAW - x) / 30) ** 2))
            for k in range(14):
                sgn = 1 if k % 2 else -1
                v = 200 + 45 * k
                p = FLAW + x + sgn * v * u
                buf += light(IVORY, 0.7 * np.exp(-u / 0.35) * np.exp(-((pdp - p) / 3) ** 2))
            # the wish: gold spreads out of the keel to the whole house, then fades
            dist = np.abs(pdp - 1486)
            reach = 650 * max(0, u - 3)
            spread = np.clip((reach - dist) / 300, 0, 1)
            tw = (0.5 + 0.5 * slow(t)) ** 3
            buf += light(GOLD, 0.22 * spread * (0.7 + 0.3 * tw) * keys(t, [(T_SNAP, 1), (54, 1), (61, 0)]))

        # crackle where the bone is fatigued
        for tp, sp in pops:
            uu = t - tp
            if 0 <= uu < 0.25:
                buf += light(WARM, 0.8 * np.exp(-uu / 0.06) * np.exp(-((pdp - sp - x) / 2.5) ** 2))
        pops = [p for p in pops if t - p[0] < 0.3]

        # the two people: wings glow with their grip, straining with the tension
        effort = T * (1 + 0.12 * tremble(t))
        gl = keys(t, gripL_keys)
        grR = keys(t, [(0, 0), (4, 0), (6, 0.2), (50, 0.2), (58, 0)])
        left_lag = np.clip((893 - pdp) / 500, 0, 1)
        right_lag = np.clip((pdp - 2034) / 480, 0, 1)
        if t >= 0:
            # the Left person: strain gathers toward the grip
            Lw = gl * (1 - 0.5 * left_lag) + 0.5 * effort * np.exp(-left_lag * 4)
            if T_SLIP <= t < T_SLIP + 2:                       # falls backwards: a jolt runs to the far end
                uu = t - T_SLIP
                Lw = Lw + 0.6 * np.exp(-((left_lag * 893 - 1200 * uu) / 90) ** 2) * np.exp(-uu / 0.8)
            buf += light(CRANBERRY, Lw * LW)
            Rw = grR * (1 - 0.5 * right_lag) + 0.5 * effort * np.exp(-right_lag * 4)
            if T_SLIP <= t < T_SLIP + 1.6:                     # the slip: the grip slides out along the wing
                uu = t - T_SLIP
                gp = 2040 + 520 * uu
                Rw = Rw * (1 - smoothstep(0, 0.2, uu) * 0.6) + 0.7 * np.exp(-((pdp - gp) / 20) ** 2) * np.exp(-uu / 0.5)
            if t >= T_SNAP:                                    # the winner's wing lights up with the wish
                uu = t - T_SNAP
                Rw = Rw + 0.35 * smoothstep(0.5, 2.5, uu) * keys(t, [(T_SNAP, 1), (55, 1), (60, 0)])
            buf += light(GOLD, Rw * RW)
        # round two: grip, then three countdown squeezes
        for tc in (22.2, 22.8, 23.4):
            uu = t - tc
            if 0 <= uu < 0.4:
                pulse = np.exp(-uu / 0.1)
                buf += light(CRANBERRY, 0.6 * pulse * np.exp(-((pdp - 893) / 25) ** 2))
                buf += light(GOLD, 0.6 * pulse * np.exp(-((pdp - 2034) / 25) ** 2))
        for tc in (6.8, 7.4, 8.0):
            uu = t - tc
            if 0 <= uu < 0.4:
                pulse = np.exp(-uu / 0.1)
                buf += light(CRANBERRY, 0.6 * pulse * np.exp(-((pdp - 893) / 25) ** 2))
                buf += light(GOLD, 0.6 * pulse * np.exp(-((pdp - 2034) / 25) ** 2))
        out[f][G.path] = buf
    return out
