"""Gingerbread House: The roofline is a warm gingerbread eave and a piping bag ices it. The bag's
bright nozzle travels the whole path from the back of Side, laying a thin bead of royal icing with a
fat piped dot at every squeeze; it slows at each corner and pipes a swirled rosette there.
Wet icing is glossy and slumps a little before it sets. Gumdrops plop onto the icing one by one,
a sprinkle shaker sweeps across the house by real x position, the sugar glitters, and then someone
takes two bites out of the free right end, crumbs and all."""
import numpy as np
from pixelhome.fx import DT, hexc, perc, light, keys, smoothstep, lerp, smooth_noise, nframes

CODE = 'XM05'
TITLE = 'Gingerbread House'
KIND = 'show'
DESCRIPTION = ('A piping bag ices the whole roofline, swirling rosettes into the corners. Gumdrops plop on, '
               'sprinkles rain across, and then somebody takes a bite out of the end.')

GINGER = hexc('#b04408')
GINGER_DARK = hexc('#601800')
ICING = hexc('#fff4e6')
NOZZLE = hexc('#ffffff')
GUMDROPS = [hexc(c) for c in ('#ff1828', '#18c040', '#ffb010', '#b020ff', '#ff5a10')]
SPRINKLES = [hexc(c) for c in ('#ff3050', '#30d060', '#4070ff', '#ffd020', '#ff80c0')]
CRUMB = hexc('#ff8a30')


def render(G, seed=35):
    rng = np.random.default_rng(seed)
    D = 68.0
    F = nframes(D)
    out = np.zeros((F, G.N, 3))
    x = G.pd[G.path]
    Pp = G.pos[G.path]
    n = G.N
    Ltr = G.length
    corners = np.array([(x[i] + x[i + 1]) / 2 for i in (80, 178, 260, 331, 380)])
    bake = smooth_noise(rng, x, 25)                      # baked colour varies along the eave
    gap = np.diff(x, prepend=x[0] - 4).clip(3.5, 8)      # local pixel pitch

    # the nozzle: speed limited near corners, a rosette pause at each corner
    T_START, T_END = 3.0, 33.0
    tt = np.arange(F) * DT
    tip = np.full(F, -40.0)
    s, v = -30.0, 0.0
    pause = {}
    for f, t in enumerate(tt):
        if T_START <= t:
            near = np.abs(corners - s)
            ahead = corners[corners > s - 1]
            vmax = 105.0
            if len(ahead):
                vmax = min(vmax, 25 + 1.4 * (ahead[0] - s))
            c = int(np.argmin(near))
            if near[c] < 2 and c not in pause:
                pause[c] = t
            if c in pause and t - pause[c] < 1.4:
                v = 0.0
            else:
                v += np.clip(max(vmax, 25) - v, -200 * DT, 120 * DT)
            s = min(s + v * DT, Ltr + 60)
        tip[f] = s
    rosettes = [(corners[c], t0) for c, t0 in pause.items()]

    icing = np.zeros(n)
    dots = np.exp(-(((x % 22) - 11) / 2.6) ** 2)
    bead = 0.2 + 0.05 * smooth_noise(rng, x, 40) + 0.75 * dots
    age = np.full(n, 99.0)                               # time since this pixel was last iced
    squeeze_ph = rng.uniform(0, 6.28)

    # gumdrops every so often along the icing, landing in a shuffled order
    gx = np.arange(70, Ltr - 60, 95) + rng.uniform(-20, 20, len(np.arange(70, Ltr - 60, 95)))
    gt = 35.0 + np.sort(rng.uniform(0, 8.5, len(gx)))[rng.permutation(len(gx))]
    gc = rng.integers(len(GUMDROPS), size=len(gx))
    # sprinkles: shaker sweeps left->right across real x; each sprinkle lands when it passes
    sp_idx = rng.choice(n, 70, replace=False)
    sp_col = np.array([SPRINKLES[i % 5] for i in range(70)])
    xs_min, xs_max = Pp[:, 0].min() - 20, Pp[:, 0].max() + 20
    sp_t = 45.0 + (Pp[sp_idx, 0] - xs_min) / (xs_max - xs_min) * 5.5 + rng.uniform(0, 0.5, 70)
    glint_ph = rng.uniform(0, 6.28, n)
    glint_f = rng.uniform(0.15, 0.45, n)
    # bites from the free right end
    bites = [(57.5, 55.0), (60.6, 120.0)]
    teeth = 1 + 0.5 * np.abs(np.sin((Ltr - x) * np.pi / 8))
    crumbs = []

    for f in range(F):
        t = f * DT
        fr = np.zeros((n, 3))
        base = keys(t, [(0, 0), (2.5, 1), (D - 3, 1), (D - 0.3, 0)])
        warm = keys(t, [(50, 1), (53, 1.35), (D, 1.35)])

        # icing laid by the nozzle: a thin bead with a fat piped dot every 22 units (a squeeze of
        # the bag at each), the bead wavering with the baker's hand; a swirled rosette at corners
        p = tip[f]
        if T_START < t < T_END + 8 and -10 < p < Ltr + 10:
            for cx, t0 in rosettes:
                if 0 <= t - t0 < 1.4:
                    p = p + 7 * np.sin(2 * np.pi * 2.2 * (t - t0))   # the swirl
                    ros = 1.2 * smoothstep(0, 1.4, t - t0) * np.exp(-((x - cx) / 9) ** 2)
                    icing = np.maximum(icing, ros)
                    age = np.where(ros > 0.1, 0.0, age)
            laid = smoothstep(p + 3, p - 3, x) * (x > p - 30)
            prof = bead * laid
            fresh = prof > icing + 0.01
            icing = np.maximum(icing, prof)
            age = np.where(fresh, 0.0, age)
        age += DT
        # wet icing slumps a little (spreads along the eave) until it sets
        wet = np.exp(-age / 2.5)
        lap = np.zeros(n)
        lap[1:-1] = icing[2:] - 2 * icing[1:-1] + icing[:-2]
        icing += 0.03 * wet * lap

        # bites: the eave beyond the bite line goes, with a toothy edge
        eaten = np.zeros(n)
        for tb, depth in bites:
            k = smoothstep(tb, tb + 0.25, t)
            eaten = np.maximum(eaten, k * ((Ltr - x) < depth * teeth))
            if abs(t - (tb + 0.2)) < DT / 2:
                for _ in range(16):
                    crumbs.append([Ltr - rng.uniform(0, depth), t, rng.uniform(-60, 60), rng.uniform(1.0, 2.2)])
        keep = 1 - eaten

        ice = np.clip(icing, 0, 1.15)
        gb = base * keep * (0.26 + 0.05 * bake) * warm * (1 - 0.6 * np.clip(ice, 0, 1))
        fr += perc(gb)[:, None] * lerp(GINGER_DARK, GINGER, 0.6 + 0.4 * bake[:, None])
        gloss = 0.25 * wet
        fr += light(ICING, base * keep * (0.5 * ice ** 1.1 + gloss * np.clip(ice * 3, 0, 1)))

        # the nozzle itself
        if T_START < t < T_END + 8 and -10 < tip[f] < Ltr + 10:
            fr += light(NOZZLE, 0.95 * np.exp(-((x - p) / 2.2) ** 2))

        # gumdrops: drop in, squash on landing, then sit glowing
        for gxi, gti, gci in zip(gx, gt, gc):
            u = t - gti
            if u < 0:
                continue
            squash = 1 + 0.9 * np.exp(-u / 0.12) * (u < 0.6)
            I = 0.62 * smoothstep(0, 0.05, u) * (1 + 0.6 * np.exp(-u / 0.15))
            w = 5.5 * squash
            fr += light(GUMDROPS[gci], base * I * np.exp(-((x - gxi) / w) ** 2) * keep)

        # sprinkles and, once everything's on, glittering sugar
        landed = (t >= sp_t)
        if landed.any():
            k = sp_idx[landed]
            pop = 1 + 1.2 * np.exp(-(t - sp_t[landed]) / 0.1)
            fr[k] += perc(base * 0.55 * pop * keep[k])[:, None] * sp_col[landed]
        if 44 < t < 52.5:                                   # the shaker, by real x position
            sx = lerp(xs_min, xs_max, smoothstep(45, 51, t))
            fr += light(NOZZLE, 0.35 * np.exp(-((Pp[:, 0] - sx) / 12) ** 2))
        sug = keys(t, [(50, 0), (52, 1), (57, 1), (58, 0.5)])
        if sug > 0:
            g = np.clip(np.sin(2 * np.pi * glint_f * t + glint_ph), 0, 1) ** 12
            fr += light(NOZZLE, base * sug * 0.6 * g * np.clip(ice, 0, 1) * keep)

        # crumbs tumble off the bitten end
        live = []
        for c in crumbs:
            a = t - c[1]
            if a > c[3]:
                continue
            live.append(c)
            c[0] += c[2] * DT * np.exp(-a)
            fr += light(CRUMB, 0.7 * (1 - a / c[3]) * np.exp(-((x - c[0]) / 2.5) ** 2))
        crumbs = live
        # the crunch: a little flash at each bite line
        for tb, depth in bites:
            u = t - tb - 0.15
            if 0 < u < 0.6:
                fr += light(ICING, 0.6 * np.exp(-u / 0.12) * np.exp(-(((Ltr - x) - depth) / 10) ** 2))
        out[f][G.path] = fr
    return out
