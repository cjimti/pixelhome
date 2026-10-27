"""Water Balloon Fight: Fourth of July afternoon in the yards. The Red team holds the lawn in front
of the Left wing, the Blue team the lawn in front of the Right wing, and the porch notch between
them is no-man's-land. Balloons are lobbed on real 3-D arcs from where the throwers stand; the roof
only sees a balloon as it comes down on it (a glint that grows as it drops toward the pixels),
then it bursts: a flash in the balloon's colour, a spray of droplets thrown along the roof with
drag, and a wet patch that stays. Wetness is a field on the roof: it glistens, drips, spreads a
little and slowly dries, so the roof keeps the score.

The gags: one balloon refuses to burst and bounces along the roof before it pops; one kid throws
straight up and soaks his own side; two balloons collide over the porch and burst together.
Then Dad turns the garden hose on everyone, sweeping a jet from the right end of the house all the
way to the back of the Side and back. It splutters out, and the whole roof drips and dries."""
import numpy as np
from pixelhome.fx import DT, hexc, perc, light, smoothstep, keys, lerp, Flicker, nframes

CODE = 'IN05'
TITLE = 'Water Balloon Fight'
KIND = 'show'
DESCRIPTION = ('Red team on the left lawn, Blue team on the right. Balloons arc in 3D and burst on the roof, '
               'leaving wet patches that glisten, drip and dry. One bounces, one is an own goal, two collide '
               'over the porch, then Dad turns on the hose.')

RED = hexc('#ff1a14')
BLUE = hexc('#1c3cff')
WATER = hexc('#bfe8ff')
SPRAY = hexc('#eaf6ff')
EVENING = hexc('#ff9a50')
RUBBER = hexc('#ff60c0')


def render(G, seed=31):
    rng = np.random.default_rng(seed)
    D = 64.0
    F = nframes(D)
    out = np.zeros((F, G.N, 3))
    x = G.pd[G.path]
    P = G.pos[G.path]
    L = G.length
    segs = {n: ix for n, ix in G.path_segments()}
    left, right = segs['Left'], segs['Right']
    red_yard = np.array([-400.0, 110.0, 320.0])
    blue_yard = np.array([400.0, 110.0, 300.0])

    # throws: (t0, flight time, launch, target path index, colour, kind)
    throws = []
    t = 3.0
    k = 0
    while t < 36.0:
        red_turn = k % 2 == 0
        if red_turn:
            tgt = int(rng.choice(np.concatenate([right, segs['Porch Right'], right])))
            throws.append((t, 1.25, red_yard + rng.normal(0, [80, 5, 60]), tgt, RED, 'pop'))
        else:
            tgt = int(rng.choice(np.concatenate([left, segs['Side'][60:], segs['Porch Left'], left])))
            throws.append((t, 1.25, blue_yard + rng.normal(0, [80, 5, 60]), tgt, BLUE, 'pop'))
        k += 1
        t += keys(t, [(3, 2.2), (20, 1.0), (30, 0.45), (36, 0.4)]) * rng.uniform(0.7, 1.2)
    # the gags
    throws = [th for th in throws if not (15.5 < th[0] < 17.5 or 22.5 < th[0] < 25.0 or 29.0 < th[0] < 31.5)]
    throws.append((15.6, 1.3, blue_yard, int(left[30]), BLUE, 'bounce'))
    throws.append((22.6, 2.2, red_yard + np.array([-120, 0, 0]), int(left[40]), RED, 'own'))
    pf = segs['Porch Front']
    throws.append((29.2, 1.6, red_yard, int(pf[34]), RED, 'pop'))
    throws.append((29.2, 1.6, blue_yard, int(pf[36]), BLUE, 'pop'))

    splats = []                                    # (time, path distance, colour, size)
    for t0, T, a, ti, col, kind in throws:
        if kind == 'bounce':
            continue
        splats.append((t0 + T, x[ti], col, 1.25 if kind == 'own' else 1.0))
    collide = (29.2 + 1.6, 0.5 * (x[pf[34]] + x[pf[36]]))
    # the bouncer: lands, bounces along the roof, then pops
    b_land = 15.6 + 1.3
    b_x0 = x[left[30]]
    b_pop = b_land + 2.4
    b_end = b_x0 + 150 * (1 - np.exp(-(b_pop - b_land) / 0.9)) * 0.9
    splats.append((b_pop, b_end, BLUE, 1.1))
    drops = {}
    for i, (ts, xs, col, sz) in enumerate(splats):
        n = 12
        drops[i] = (rng.uniform(150, 520, n) * rng.choice([-1, 1], n) * sz, rng.uniform(0.5, 1.0, n))

    wet = np.zeros(G.N)
    tint = np.zeros((G.N, 3))
    glitter = Flicker(rng, G.N, 0.3, 2.5)
    applied = set()
    drip = np.zeros(G.N)
    hose_on = (41.0, 52.5)

    def hose_x(t):
        return keys(t, [(41.0, L + 40), (41.6, L - 40), (46.5, 30.0), (47.3, 30.0), (52.0, L - 60)])

    for f in range(F):
        t = f * DT
        fade = keys(t, [(0, 0.0), (1.5, 1.0), (D - 2, 1.0), (D, 0.0)])
        buf = np.zeros((G.N, 3))
        # the two forts and no-man's-land
        base = np.full(G.N, 0.06)
        buf += light(EVENING, base)
        team = np.zeros(G.N)
        team[left] = 1
        buf += light(RED, 0.1 * team)
        team[:] = 0
        team[right] = 1
        buf += light(BLUE, 0.12 * team)

        # balloons coming down: glint grows as the balloon nears the pixels
        for t0, T, a, ti, col, kind in throws:
            u = (t - t0) / T
            if 0.55 < u < 1.0:
                tgt = P[ti]
                apex = 900 if kind == 'own' else 420
                pos = a + (tgt - a) * u
                pos = pos + np.array([0, 4 * apex * u * (1 - u), 0])
                d2 = ((P - pos) ** 2).sum(1)
                wob = 1 + 0.15 * np.sin(2 * np.pi * 9 * t)                # it jiggles
                buf += light(col * 0.7 + RUBBER * 0.3, 0.75 * wob * np.exp(-d2 / 45 ** 2))
        # the bouncer rolling along the roof
        if b_land <= t < b_pop:
            dtb = t - b_land
            bx = b_x0 + 150 * (1 - np.exp(-dtb / 0.9)) * 0.9
            hop = abs(np.sin(np.pi * dtb / keys(dtb, [(0, 0.45), (2.4, 0.2)])))
            buf += light(BLUE * 0.7 + RUBBER * 0.3, (0.85 - 0.35 * hop) * np.exp(-((x - bx) / (7 + 3 * (1 - hop))) ** 2))
            if hop < 0.15:
                buf += light(SPRAY, 0.25 * np.exp(-((x - bx) / 10) ** 2))
        # bursts: flash, droplets with drag, and the wet patch they leave
        for i, (ts, xs, col, sz) in enumerate(splats):
            dt_ = t - ts
            if dt_ < 0 or dt_ > 1.6:
                continue
            if i not in applied:
                applied.add(i)
                patch = sz * np.exp(-((x - xs) / (32 * sz)) ** 2)
                tint = (tint * wet[:, None] + col[None] * patch[:, None]) / np.maximum(wet + patch, 1e-6)[:, None]
                wet = np.minimum(wet + patch, 1.4)
            buf += light(SPRAY * 0.6 + col * 0.4, 1.1 * np.exp(-dt_ / 0.07) * np.exp(-((x - xs) / 28) ** 2))
            buf += light(col, 0.8 * np.exp(-dt_ / 0.35) * np.exp(-((x - xs) / 50) ** 2))   # the burst of colour
            v, bri = drops[i]
            dp = xs + v / 4.0 * (1 - np.exp(-4.0 * dt_))
            I = (bri[None] * np.exp(-((x[:, None] - dp[None]) / 4) ** 2)).sum(1) * np.exp(-dt_ / 0.45)
            buf += light(SPRAY, np.clip(I, 0, 1))
            for j in range(len(v)):                                        # droplets leave little wet marks
                if abs(dt_ - 0.3) < DT / 2:
                    wet = np.minimum(wet + 0.3 * bri[j] * np.exp(-((x - dp[j]) / 6) ** 2), 1.4)
        if 0 <= t - collide[0] < 0.5:                                      # the mid-air collision: purple
            dc = t - collide[0]
            buf += light(hexc('#c040ff'), 1.0 * np.exp(-dc / 0.1) * np.exp(-((x - collide[1]) / 60) ** 2))

        # the hose
        if hose_on[0] <= t < hose_on[1]:
            hx = hose_x(t)
            press = smoothstep(41.0, 41.5, t) * (1 - smoothstep(51.8, 52.4, t))
            if 52.0 < t < 52.5:
                press = 0.6 * (np.sin(2 * np.pi * 5 * t) > 0)                   # the last splutter
            jet = np.exp(-((x - hx) / 34) ** 2) * press
            mist = np.exp(-((x - hx) / 110) ** 2) * press
            sp = 0.7 + 0.3 * np.sin(x * 0.9 - 40 * t) * np.sin(x * 0.37 + 23 * t)
            buf += light(SPRAY, 0.95 * jet * sp) + light(WATER, 0.25 * mist)
            wet = np.minimum(wet + DT * 3.0 * jet, 1.4)
            tint = lerp(tint, WATER[None] * 0.0 + np.array([0.6, 0.85, 1.0])[None], (DT * 3 * jet)[:, None].clip(0, 1))

        # the wet roof: glistens, drips, spreads a little, dries
        if f % 4 == 0:
            wet = 0.25 * np.roll(wet, 1) + 0.5 * wet + 0.25 * np.roll(wet, -1)
        wet *= np.exp(-DT / keys(t, [(0, 22.0), (52, 22.0), (58, 6.0)]))
        g = np.clip(glitter(t), 0, None) ** 6 * 0.08
        wv = np.clip(wet, 0, 1)
        buf += light(WATER, 0.2 * wv * (1 + g * 4))
        buf += tint * perc(0.42 * wv)[:, None]
        drip = np.maximum(drip * np.exp(-DT / 0.12), (rng.random(G.N) < 0.0015 * wv) * 1.0)
        buf += light(SPRAY, 0.6 * drip)

        buf *= fade
        m = buf.max(1, keepdims=True)
        out[f][G.path] = np.clip(np.where(m > 1, buf / np.maximum(m, 1e-9), buf), 0, 1)
    return out
