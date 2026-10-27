"""Perfect Stripes: Dad mows the lawn the house sits on. The mower is a real point moving through
the yard in 3-D, pass after pass across the width of the lot, each pass one row further back. Each
pixel is a blade of grass at its real position: shaggy until the deck goes over it, then laid down
light or dark by the direction of that pass, so the runs that point away from the street (Side and
the two porch sides) come out in true lawn stripes and each front run flips in a single pass as the
mower drives right along it. One row skips a spot on the porch. He comes back for it. Then a
dandelion."""
import numpy as np
from pixelhome.fx import DT, hexc, perc, light, smoothstep, keys, lerp, Flicker, nframes, smooth_noise

CODE = 'FA04'
TITLE = 'Perfect Stripes'
KIND = 'show'
DESCRIPTION = ('Dad mows the yard pass by pass in true 3-D; every pixel is a blade of grass laid light or '
               'dark by the pass that cut it. He misses one spot on the porch. Then a dandelion.')

SHAGGY = hexc('#6a8a20')
LIGHT_STRIPE = hexc('#9ee070')
DARK_STRIPE = hexc('#1f7a3a')
MOWER = hexc('#fff0d0')
EXHAUST = hexc('#ff5020')
DANDELION = hexc('#ffd020')


def render(G, seed=24):
    rng = np.random.default_rng(seed)
    D = 64.0
    n = G.N
    out = np.zeros((nframes(D), n, 3))
    P = G.pos
    px, pz = P[:, 0], P[:, 2]
    wind = smooth_noise(rng, G.pd, 50, 3)
    tuft_noise = Flicker(rng, n, 0.2, 0.9)
    height = rng.uniform(0.75, 1.25, n)

    # passes: row centres stepping back from the street; direction alternates
    rows = [-120.0 - 64 * k for k in range(9)]
    X0, X1 = -720.0, 720.0
    speed, turn = 380.0, 0.7
    plan = []                                          # (t0, t1, row, direction)
    t = 5.6
    for k, zc in enumerate(rows):
        d = 1 if k % 2 == 0 else -1
        dur = (X1 - X0) / (speed + 25 * k)          # he gets into a groove
        plan.append((t, t + dur, k, d))
        t += dur + turn
    done = t - turn
    miss = (-70.0, 20.0)                               # the deck rides up over something here, row 7

    def mower_at(t):
        """(x, z, mowing?, row, dir) of the mower at time t."""
        if t < plan[0][0]:
            return X0, rows[0], False, 0, 1
        for i, (t0, t1, k, d) in enumerate(plan):
            if t0 <= t < t1:
                u = (t - t0) / (t1 - t0)
                xm = X0 + (X1 - X0) * u if d > 0 else X1 - (X1 - X0) * u
                return xm, rows[k], True, k, d
            if i + 1 < len(plan) and t1 <= t < plan[i + 1][0]:
                u = (t - t1) / turn                    # U-turn: a half circle into the next row
                ang = np.pi * u
                r = 32.0
                xe = X1 if d > 0 else X0
                return xe + d * r * np.sin(ang) * 0.8, rows[k] - r + r * np.cos(ang), False, k, d
        return None

    # the return trip for the missed spot (on the Porch Front, z = -569)
    back = [(done, (X0 if plan[-1][3] < 0 else X1, rows[-1])), (done + 3.5, (X0 + 40, rows[-1])),
            (46.0, (-400.0, -569.0)), (48.6, (-60.0, -569.0)), (49.6, (20.0, -569.0)), (50.4, (60.0, -569.0)),
            (53.0, (60.0, -569.0)), (55.5, (400.0, -191.0)), (57.4, (400.0, -191.0)), (58.6, (420, -191.0))]
    dand_t = 54.6
    dand_x = 300.0                                     # on the Right wing
    stalk = np.exp(-((px - dand_x) / 6) ** 2) * (np.abs(pz + 191) < 5)

    state = np.zeros(n)                                # 0 shaggy, +1 light, -1 dark
    cut_t = np.full(n, -99.0)

    for f in range(len(out)):
        t = f * DT
        fade = keys(t, [(0, 0), (2.5, 1), (61, 1), (64, 0)])

        m = mower_at(t)
        mowing = False
        if m is None or t >= done:
            pts = [(tt, np.array(p, float)) for tt, p in back]
            if t < pts[0][0]:
                xm, zm = pts[0][1]
            else:
                xm, zm = keys(t, pts)
            mowing = 48.4 <= t < 50.4
            k, d = 7, 1
        else:
            xm, zm, mowing, k, d = m

        if mowing:
            deck = (np.abs(pz - zm) < 32) & (np.abs(px - xm) < 22)
            if k == 7 and t < done and miss[0] < xm < miss[1]:
                deck[:] = False
            if t >= done:                              # the do-over, carefully, in the porch direction
                deck = deck & (np.abs(pz + 569) < 6)
                d = plan[7][3]
            newly = deck & (state == 0)
            state[newly] = d
            cut_t[newly] = t

        # grass colour
        sway = 0.04 * np.interp((G.pd + 40 * t) % G.length, G.pd, wind)
        shag = (0.17 + sway) * height
        I_light, I_dark = 0.42, 0.15
        sheen = 0.0
        if 50.6 <= t < 54:                             # a sheen runs over the finished lawn
            sweep = keys(t, [(50.6, -800), (53.6, 800)])
            sheen = 0.18 * np.exp(-((px - sweep) / 90) ** 2)
        col = np.where((state > 0)[:, None], light(LIGHT_STRIPE, (I_light + sheen) * np.ones(n)),
                       light(DARK_STRIPE, (I_dark + sheen) * np.ones(n)))
        tuft = light(SHAGGY, shag * (1 + 0.15 * tuft_noise(t)))
        # the missed spot calls attention to itself once the lawn is done
        if done < t < 50.4:
            spot = (state == 0)
            call = 0.3 * (0.5 + 0.5 * np.sin(2 * np.pi * (t - done) / 0.9)) * smoothstep(done, done + 1, t)
            tuft = tuft + light(SHAGGY, call * spot * np.ones(n))
        fr = np.where((state == 0)[:, None], tuft, col)
        # clippings: a fresh-cut flash fading behind the mower
        age = t - cut_t
        fr = fr + light(hexc('#d0ffb0'), 0.4 * np.exp(-np.clip(age, 0, None) / 0.35) * (age >= 0))
        fr = fr * fade

        # the mower: pull-start, then the headlight moving through the yard
        if t > 2.4:
            tug = sum(np.exp(-((t - tt) / 0.07) ** 2) * a for tt, a in ((3.0, 0.4), (3.7, 0.5), (4.5, 0.9)))
            run = smoothstep(4.5, 4.8, t) * (1 - smoothstep(58.6, 60.0, t))
            rev = 0.25 * sum(np.exp(-((t - tt) / 0.15) ** 2) for tt in (57.6, 58.2))
            dist = np.hypot(px - xm, pz - zm)
            I = (0.55 * run + tug + rev) * np.exp(-(dist / 38) ** 2) + 0.2 * run * np.exp(-(dist / 110) ** 2)
            # headlight: a cone thrown ahead along the row, catching the roof before the mower gets there
            ahead = (px - xm) * (d if t < done else np.sign(keys(t + 0.1, [(tt, p[0]) for tt, p in back]) - xm + 1e-6))
            cone = np.exp(-((pz - zm) / 45) ** 2) * np.exp(-np.clip(ahead, 0, None) / 260) * (ahead > 0)
            I = I + 0.22 * run * cone * (t < 58.6)
            fr = fr + light(MOWER, I)
            fr = fr + light(EXHAUST, (0.2 * run + 0.6 * tug) * np.exp(-(np.hypot(px - xm + 30, pz - zm) / 16) ** 2))

        # the dandelion pops up on the Right wing after the lawn is perfect
        if t > dand_t:
            g = smoothstep(dand_t, dand_t + 0.35, t)
            bob = 1 + 0.12 * np.sin(2 * np.pi * (t - dand_t) / 1.3)
            fr = fr + light(DANDELION, 0.9 * g * bob * stalk * keys(t, [(61, 1), (64, 0.2)]))

        out[f] = np.clip(fr * keys(t, [(D - 3, 1), (D - 0.5, 0)]), 0, 1)
    return out
