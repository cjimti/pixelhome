"""Changing of the Year: Two characters and a handover. The Old Year, a stooped silver-blue glow,
dozes on the Porch Front. Someone knocks at the free right end; the Baby New Year, a small gold
spark, hops in, bonks into the corner, and takes the year's light from the old man in a stream of
sparks. The Old Year shuffles away around the corners, stopping for breath, waves once from the
back of the house and slips out through the far free end. The baby jumps, and the new year
floods the roof."""
import numpy as np
from pixelhome.fx import DT, hexc, light, keys, smoothstep, Flicker, nframes

CODE = 'NY06'
TITLE = 'Changing of the Year'
KIND = 'show'
DESCRIPTION = 'The stooped Old Year dozes on the porch; the Baby New Year hops in from the right end, takes the light, and the old man shuffles off out the back of the house.'

OLD = hexc('#90a8e0')
OLD_DIM = hexc('#5060a8')
BABY = hexc('#ffb838')
SPARK = hexc('#ffe0a0')
WHITE = hexc('#fff4e4')
NAVY = hexc('#081440')
GOLD = hexc('#ffa020')
CHAMP = hexc('#ffd890')


def render(G, seed=26):
    rng = np.random.default_rng(seed)
    D = 60.0
    out = np.zeros((nframes(D), G.N, 3))
    n = G.N
    pdp = G.pd[G.path]
    L = G.length
    c_pf = pdp[296]                              # middle of the Porch Front
    pf_r = pdp[331]
    corner_r = pdp[381]                          # Porch Right -> Right
    corner_pl = pdp[261]
    corner_l = pdp[179]
    corner_s = pdp[81]
    shimmer = Flicker(rng, n, 0.3, 1.2)
    tw = Flicker(rng, n, 1.5, 5)

    # the Old Year's route: (time, path distance); pauses at each corner to catch his breath
    old_route = [(0, c_pf), (10.0, c_pf), (13.0, c_pf + 90), (25.0, c_pf + 90), (26.5, c_pf + 70),
                 (31.0, corner_pl + 10), (32.5, corner_pl + 10), (38.0, corner_l + 10), (39.5, corner_l + 10),
                 (44.0, corner_s + 10), (45.5, corner_s + 10), (48.0, 40), (49.2, 40), (51.5, -90)]
    # the baby: (time, path distance)
    baby_route = [(0, L + 60), (12.0, L + 60), (14.6, corner_r + 6), (15.1, corner_r + 14), (15.6, corner_r - 2),
                  (17.2, c_pf + 150), (25.0, c_pf + 150), (27.0, c_pf + 60), (29.0, c_pf + 60), (31.5, corner_r + 120),
                  (33.0, corner_r + 40), (34.5, c_pf + 200), (36.0, c_pf + 20), (47.0, c_pf + 20), (49.8, c_pf),
                  (D, c_pf)]

    def route(rt, t):
        return float(keys(t, rt))

    def speed(rt, t):
        return (route(rt, t + 0.05) - route(rt, t - 0.05)) / 0.1

    knocks = [7.0, 7.35, 7.7, 9.0, 9.2]
    sparks = []                                  # (birth, from, to)
    for k in range(40):
        tb = 18.0 + k * 0.15 + rng.uniform(0, 0.1)
        sparks.append((tb, rng.uniform(-10, 10), rng.uniform(0.6, 0.9)))

    for f in range(len(out)):
        t = f * DT
        buf = np.zeros((n, 3))
        buf += light(NAVY, keys(t, [(0, 0), (2, 0.1), (50, 0.1), (52, 0.04), (D - 3, 0.04), (D, 0)]))

        # knocks at the free right end
        for tk in knocks:
            if tk <= t < tk + 0.4:
                buf += light(WHITE, 0.8 * np.exp(-(t - tk) / 0.07) * np.exp(-((L - pdp) / 14) ** 2))

        # --- the Old Year ---
        ob = route(old_route, t)
        ov = speed(old_route, t)
        f_step = 0.9
        op = ob - ov / (2 * np.pi * f_step) * np.sin(2 * np.pi * f_step * t)     # shuffling, step by step
        moving = min(1.0, abs(ov) / 30)
        facing = np.sign(ov) if abs(ov) > 1 else (1 if t < 26 else -1)
        doze = keys(t, [(0, 0), (2.5, 0.35), (9.0, 0.35), (9.4, 0.6), (18, 0.6), (24, 0.44), (47.0, 0.42),
                        (47.4, 0.8), (48.0, 0.42), (51.5, 0.4)])
        breath = 1 + 0.25 * np.sin(2 * np.pi * t / 4.0) * (t < 9.5) + 0.12 * np.sin(2 * np.pi * t / 1.6) * (abs(ov) < 1) * (t > 25)
        rel = pdp - op
        # stooped shape: a soft body with the bright head leaning the way he walks, dimmer trailing back
        head = np.exp(-((rel - facing * 14) / 12) ** 2)
        body = np.exp(-((rel + facing * 10) / 34) ** 2)
        bob = 1 + 0.15 * moving * np.cos(4 * np.pi * f_step * t)
        oI = doze * breath * bob * (0.9 * head + 0.55 * body)
        oI *= smoothstep(-60, 10, pdp)                                    # he slips out past the free end
        buf += light(OLD, oI) + light(OLD_DIM, 0.4 * doze * body)
        # his cane: a small tap of light ahead of him on every step
        if moving > 0.3:
            ph = (f_step * t) % 1
            buf += light(OLD, 0.5 * np.exp(-ph / 0.08) * np.exp(-((rel - facing * 38) / 4) ** 2) * smoothstep(-60, 10, pdp))

        # --- the Baby New Year ---
        bb = route(baby_route, t)
        bv = speed(baby_route, t)
        grow = keys(t, [(0, 0.55), (18.0, 0.55), (24.0, 1.0), (49.5, 1.0), (50.0, 1.4), (D - 2, 1.2), (D, 0)])
        hop_f = 2.6
        hp = (hop_f * t) % 1
        hopping = min(1.0, abs(bv) / 40) if t < 47 else (0.4 if t < 49.5 else 0.0)
        air = np.sin(np.pi * hp) * hopping                                 # 0 on the ground, 1 at the top
        squash = 1 + 0.5 * hopping * np.exp(-hp / 0.08)                    # wide on landing
        bonk = np.exp(-((t - 14.65) / 0.06) ** 2)                          # hits the corner
        width = (9 + 6 * grow) * squash * (1 + 1.2 * bonk)
        bI = keys(t, [(12, 0), (12.3, 1), (D - 2.5, 1), (D, 0)]) * (0.65 + 0.4 * grow) * (1 - 0.35 * air)
        # waits impatiently: little hops in place while the old man walks off
        if 36.0 < t < 47:
            bI *= 1 - 0.3 * np.sin(np.pi * ((1.6 * t) % 1)) ** 2
        brel = pdp - bb
        buf += light(BABY, bI * np.exp(-(brel / width) ** 2))
        buf += light(WHITE, 0.8 * bonk * np.exp(-(brel / 10) ** 2))
        # the baby waves back when the old man waves
        if 47.3 < t < 48.6:
            buf += light(SPARK, 0.6 * np.sin(np.pi * (t - 47.3) / 1.3) ** 2 * np.exp(-(brel / 18) ** 2))

        # --- the handover: sparks stream from the old man to the baby ---
        for tb, off, a in sparks:
            u = (t - tb) / 0.9
            if 0 <= u < 1:
                p = op + (bb - op) * (u * u * (3 - 2 * u)) + off * np.sin(np.pi * u)
                buf += light(SPARK, a * np.sin(np.pi * u) * np.exp(-((pdp - p) / 3.5) ** 2))

        # --- the new year floods the roof from the baby, both ways ---
        if t >= 50.0:
            tn = t - 50.0
            d = np.abs(pdp - c_pf)
            front = 520 * tn
            wave = np.exp(-((d - front) / 50) ** 2)
            lit = smoothstep(front + 20, front - 80, d)
            fade = keys(tn, [(0, 1), (2, 1), (5, 0.65), (D - 50 - 2.5, 0.5), (D - 50, 0)])
            glint = np.clip(tw(t) - 1.0, 0, None) * smoothstep(1, 3, tn)
            buf += light(WHITE, 0.9 * wave * np.exp(-tn / 3))
            # the new year's heartbeat: slow ripples of warmth running out from the baby
            rip = sum(np.exp(-((d - 420 * (tn - k * 1.3)) / 70) ** 2) * np.exp(-(tn - k * 1.3) / 2.5)
                      for k in range(1, 7) if tn > k * 1.3)
            buf += light(GOLD, 0.45 * lit * fade * (0.9 + 0.1 * shimmer(t)) + 0.35 * fade * rip)
            buf += light(CHAMP, 0.8 * lit * fade * glint)
        out[f][G.path] = buf
    np.clip(out, 0, 1, out=out)
    return out
