"""Breakfast in Bed: Two kids sneak in at the right end and make Mum breakfast. The porch is the
kitchen: a pan heats on the stove, a pancake is poured and flipped, and the third flip sends it
flying round the corner onto the left wing. While they chase it, the toast on the porch's right side
burns: blackbody coils, toast going brown then black, smoke puffing along the roof, the alarm beeps.
They fan the smoke out of both ends, build a tray anyway (pancake, charred toast, a flower picked
from the garden) and carry it carefully round three corners to Mum's room at the back of the house,
where she wakes up laughing."""
import numpy as np
from pixelhome.fx import DT, hexc, light, smoothstep, keys, colormap, Flicker, heartbeat, nframes

CODE = 'MO03'
TITLE = 'Breakfast in Bed'
KIND = 'show'
DESCRIPTION = 'Two kids make Mum breakfast: a pancake flipped round the corner, toast that burns, smoke, the alarm, and a tray carried round the house anyway.'

KID_A = hexc('#ff9a6a')
KID_B = hexc('#a0ff70')
KITCHEN = hexc('#ffd2a0')
BATTER = hexc('#ffc080')
TRAY = hexc('#ffe0c0')
SMOKE = hexc('#7a6a98')
ALARM = hexc('#ff1000')
FLOWER = hexc('#ff4a8a')
MUM = hexc('#ff6a9a')
WARM = hexc('#ffb080')
HEAT = colormap([(0, (0, 0, 0)), (0.2, (0.08, 0, 0)), (0.45, (0.6, 0.03, 0)), (0.7, (1, 0.2, 0.01)),
                 (0.9, (1, 0.45, 0.08)), (1.0, (1, 0.62, 0.25))])
TOAST = colormap([(0, hexc('#ffd8a0')), (0.35, hexc('#ff9030')), (0.65, hexc('#c04008')), (1, hexc('#401000'))])


def render(G, seed=23):
    rng = np.random.default_rng(seed)
    D = 72.0
    n = G.N
    out = np.zeros((nframes(D), n, 3))
    x = G.pd[G.path]
    L = G.length
    PAN, TOASTER, ALARM_AT = 1485.0, 1850.0, 1659.0
    fl = Flicker(rng, n, 0.5, 2.0)

    def blob(p, s, c, I):
        return light(c, I * np.exp(-((x - p) / s) ** 2))

    kA = [(3, L + 30), (8.5, 1450), (27.8, 1450), (31.5, 860), (32.5, 860), (36, 1462), (40.5, 1462),
          (41.6, 1830), (47, 1830), (48, 1500), (49, 1500), (51, 690), (51.6, 690), (53.4, 1470), (54, 1470)]
    kB = [(3.6, L + 30), (9.6, 1850), (11.5, 1850), (14, 1528), (28.2, 1528), (32.2, 885), (33, 885),
          (36.4, 1515), (40.7, 1515), (41.8, 1872), (47, 1872), (48.2, 1530), (54, 1530)]
    tray = [(54, PAN), (56.5, 1311), (59.5, 893), (62, 491), (64.5, 45)]
    flips = [19.0, 23.5]
    puffs = []
    for _ in range(70):
        te = rng.uniform(31, 43.5)
        puffs.append((te, TOASTER + rng.uniform(-15, 15), rng.choice([-1, 1]) * rng.uniform(12, 40), rng.uniform(0.6, 1)))

    def kid_pos(k, t):
        p = keys(t, k)
        moving = abs(keys(t + DT, k) - keys(t - DT, k)) > 0.5
        if moving:
            p += 2.5 * np.sin(2 * np.pi * 3.2 * t)
        if 42 < t < 47:                                      # fanning the smoke
            p += 14 * np.sin(2 * np.pi * 3.5 * t)
        return p

    for f in range(len(out)):
        t = f * DT
        buf = np.zeros((n, 3))
        dawn = keys(t, [(0, 0), (3, 0.05), (66, 0.08), (72, 0)])
        buf += light(keys(t, [(0, hexc('#6050c0')), (66, hexc('#ff9a70'))]), dawn * np.ones(n))
        kitch = keys(t, [(0, 0), (2, 0.09), (54, 0.09), (58, 0)])
        buf += light(KITCHEN, kitch * smoothstep(200, 120, np.abs(x - 1485)))

        # stove and pan
        h = keys(t, [(10, 0), (13, 0.42), (28, 0.42), (29, 0.3), (36, 0.1), (37, 0)])
        under = 1.0
        if 15 < t < 28:
            under = 1 - 0.8 * smoothstep(8, 2, np.abs(x - PAN)) * smoothstep(15, 16.5, t)
        buf += HEAT(h * smoothstep(38, 26, np.abs(x - PAN)) * (0.95 + 0.05 * fl(t)) * under)

        # pancake
        if 14 < t < 32.5:
            if t < 28:
                p, I, s = PAN, 0.8 * smoothstep(14, 16, t), 4 + 10 * smoothstep(14, 16.5, t)
                for tf in flips:
                    if tf < t < tf + 0.7:                     # up in the air
                        I *= 1 - np.sin(np.pi * (t - tf) / 0.7) * 0.9
                    if tf + 0.7 < t < tf + 1.0:               # lands with a splat
                        I *= 1 + 0.8 * (1 - (t - tf - 0.7) / 0.3)
                        s *= 1.2
            elif t < 31:                                       # the third flip: off it goes
                u = t - 28
                p = PAN - 633 * (1 - np.exp(-u / 0.9)) / (1 - np.exp(-3 / 0.9))
                I, s = 0.65, 10 + 4 * np.sin(2 * np.pi * 4 * u)
            else:
                p, I, s = 852, 0.45, 15
            buf += blob(p, s, BATTER, I)
        elif 32.5 <= t < 36:
            buf += blob(kid_pos(kA, t) + 6, 14, BATTER, 0.45)

        # toaster: coils heat, toast cooks, and cooks, and cooks
        if 11 < t:
            done = np.clip((t - 11) / 30, 0, 1)
            coil = keys(t, [(11, 0), (13, 0.55), (41, 0.8), (43.5, 0.8), (46, 0)])
            dx = x - TOASTER
            coils = smoothstep(40, 32, np.abs(dx)) * (np.abs(dx) > 14) * (0.5 + 0.5 * np.cos(dx * 2 * np.pi / 15)) ** 2
            buf += HEAT(coil * coils)
            if t < 47:
                buf += blob(TOASTER, 10, TOAST(done), 0.75 * (1 - 0.55 * done ** 2) * smoothstep(11, 11.5, t))

        # smoke
        push = 0 if t < 42 else 130 * (t - 42) ** 1.5
        sm = np.zeros(n)
        for te, x0, v, a in puffs:
            u = t - te
            if u > 0:
                p = x0 + v * u + np.sign(v) * push
                r = 10 + 9 * u
                sm += a * 0.16 * np.exp(-u / 9) * np.exp(-((x - p) / r) ** 2)
        buf += light(SMOKE, np.clip(sm, 0, 0.5) * (0.85 + 0.15 * fl(t)))

        # smoke alarm
        if 40.4 < t < 43.2 and ((t - 40.4) % 0.33) < 0.13:
            buf += blob(ALARM_AT, 9, ALARM, 0.9)

        # the tray
        if t > 36:
            T = keys(t, tray)
            wob = 2 * np.sin(2 * np.pi * 1.3 * t) * (54 < t < 64.5)
            T = T + wob
            tI = smoothstep(36, 37, t) * keys(t, [(64.5, 1), (70, 1), (72, 0)])
            buf += light(TRAY, 0.18 * tI * smoothstep(34, 28, np.abs(x - T)))
            buf += blob(T, 8, BATTER, 0.55 * tI)
            if t > 48.5:                                       # the toast, charred
                buf += blob(T + 16, 5, TOAST(0.95), 0.6 * tI)
                buf += blob(T + 16, 1.8, HEAT(0.5), 0.6 * tI * (t > 64))
            if t > 53.4:
                buf += blob(T - 17, 5, FLOWER, 0.7 * tI)
        if 48 < t < 48.5:                                      # toast to the tray
            buf += blob(keys(t, [(48, TOASTER), (48.5, PAN + 16)]), 5, TOAST(0.95), 0.6)
        if 49 < t < 53.4:                                      # a flower from the garden
            pf = kid_pos(kA, t) - 6 if t > 51.6 else 690
            buf += blob(pf, 5, FLOWER, 0.7 * smoothstep(49, 51.5, t))

        # kids
        if t > 3:
            if t < 54:
                pa, pb = kid_pos(kA, t), kid_pos(kB, t)
            else:
                T = keys(t, tray)
                pa, pb = T - 45 + 2.5 * np.sin(2 * np.pi * 2 * t), T + 45 + 2.5 * np.sin(2 * np.pi * 2 * t + 1)
            kI = 0.6 * keys(t, [(68, 1), (70, 1.3), (72, 0)])
            panic = 1 + 0.4 * (40.4 < t < 43) * np.sin(2 * np.pi * 6 * t)
            buf += blob(pa, 8, KID_A, kI * panic) + blob(pb, 8, KID_B, kI * panic)

        # Mum wakes up, laughing
        if t > 63.5:
            mI = keys(t, [(63.5, 0), (66, 0.5), (70, 0.52), (72, 0)])
            buf += light(MUM, mI * np.exp(-((x - 160) / 320) ** 2) * (1 + 0.3 * heartbeat(t, 68, 1.0)))
            for ti in (66.4, 66.9, 67.4, 67.9):
                u = t - ti
                if u > 0:
                    ring = np.exp(-((np.abs(x - 45) - 420 * u) / 28) ** 2) * np.exp(-u / 0.9)
                    buf += light(WARM, 0.4 * ring)
        out[f][G.path] = buf
    return out
