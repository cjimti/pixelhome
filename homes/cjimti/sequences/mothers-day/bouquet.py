"""Bouquet: Flowers grow along the Side and the two wing fronts. A small hand of light walks the
roof from end to end picking them, and each picked flower travels the path to the porch, slowing to
take the corners, and packs into a bunch on the Porch Front with a little bump as it lands. Then
stems grow down both porch sides toward the street, so from the kerb the bunch sits at the top of a
bouquet whose stems converge in perspective, and a pink bow ties at the two front corners."""
import numpy as np
from pixelhome.fx import DT, hexc, light, smoothstep, keys, Flicker, nframes

CODE = 'MO05'
TITLE = 'Bouquet'
KIND = 'show'
DESCRIPTION = 'A small hand picks flowers along the roof; each one travels round the corners into a bunch on the porch, then stems grow down the porch sides and a bow ties.'

HAND = hexc('#ffe2c8')
LEAF = hexc('#60ff30')
STEM = hexc('#38ff20')
BOW = hexc('#ff3a80')
POLLEN = hexc('#ffb020')
BLUSH = hexc('#ff8ab0')
PETALS = [hexc(c) for c in ('#ff5a96', '#ff8a5c', '#b070ff', '#ffb0c8', '#ff7a50', '#d080ff', '#ff4f7a')]


def render(G, seed=25):
    rng = np.random.default_rng(seed)
    D = 64.0
    n = G.N
    out = np.zeros((nframes(D), n, 3))
    x = G.pd[G.path]
    L = G.length
    rng_of = {name: (G.pd[idx].min(), G.pd[idx].max()) for name, idx in G.seg.items()}
    pf0, pf1 = rng_of['Porch Front']
    M = 0.5 * (pf0 + pf1)
    corners = np.array([0.5 * (rng_of[a][1] + rng_of[b][0]) for a, b in
                        [('Side', 'Left'), ('Left', 'Porch Left'), ('Porch Left', 'Porch Front'),
                         ('Porch Front', 'Porch Right'), ('Porch Right', 'Right')]])
    sites = []
    for name, k in (('Side', 3), ('Left', 3), ('Right', 5)):
        a, b = rng_of[name]
        s = np.linspace(a + 50, b - 50, k) + rng.uniform(-15, 15, k)
        sites += list(s)
    sites = np.array(sites)
    F = len(sites)
    col = np.array([PETALS[i % len(PETALS)] for i in rng.permutation(F)])
    t_grow = 1.5 + rng.uniform(0, 3, F)
    walk = [(4.5, -30.0), (31.0, L + 30)]
    t_pick = 4.5 + (sites + 30) / (L + 60) * 26.5
    left = sites < M
    # bouquet slots: arrivals pack from the middle outward on each side
    tgt = np.zeros(F)
    order_l = np.argsort(-sites[left])          # nearest to the porch arrive first
    for k, i in enumerate(np.where(left)[0][order_l]):
        tgt[i] = M - 13 - 26 * k
    order_r = np.argsort(sites[~left])
    for k, i in enumerate(np.where(~left)[0][order_r]):
        tgt[i] = M + 13 + 26 * k
    p = sites.copy()
    v = np.zeros(F)
    arrived = np.full(F, np.inf)
    tw = Flicker(rng, n, 0.8, 2.5)
    sway_ph = rng.uniform(0, 2 * np.pi, F)
    stems_l = (rng_of['Porch Left'][0] - 5, rng_of['Porch Left'][1] + 5)
    stems_r = (rng_of['Porch Right'][0] - 5, rng_of['Porch Right'][1] + 5)
    bow_l, bow_r = corners[1], corners[4]

    for f in range(len(out)):
        t = f * DT
        buf = np.zeros((n, 3))
        # physics of the travelling flowers
        moving = t > t_pick
        dcorner = np.min(np.abs(p[:, None] - corners[None, :]), 1)
        cap = 260 * (0.3 + 0.7 * smoothstep(5, 60, dcorner))
        acc = 7.0 * (tgt - p) - 3.2 * v
        v = np.where(moving, np.clip(v + acc * DT, -cap, cap), 0)
        p = p + v * DT
        newly = moving & (np.abs(p - tgt) < 3) & np.isinf(arrived)
        arrived[newly] = t

        # flowers
        grow = smoothstep(t_grow, t_grow + 2.5, t)
        home = ~moving
        sway = np.where(home, 2.5 * np.sin(2 * np.pi * t / 3 + sway_ph), 0.8 * np.sin(2 * np.pi * t / 2.2 + sway_ph))
        d = x[None, :] - (p + sway)[:, None]
        inb = np.isfinite(arrived)
        r = np.where(home, 10.0, np.where(inb, 8.5, 8.0))[:, None]
        petal = np.exp(-((np.abs(d) - 0.55 * r) / (0.45 * r)) ** 2)
        bumpI = np.where(inb, np.exp(-np.clip(t - arrived, 0, None) / 0.35), 0)
        show_ = keys(t, [(55, 1), (59, 1.25), (64, 0)])
        I = (0.7 * grow * (1 + 0.6 * bumpI) * show_)[:, None] * petal
        k = np.argmax(I, 0)
        buf += light(col[k], I.max(0))
        buf += light(POLLEN, ((0.6 * grow * show_)[:, None] * np.exp(-(d / 2.5) ** 2)).max(0))
        leaves = (np.abs(np.abs(d) - 15) < 6) * (home * grow * 0.25)[:, None]
        buf += light(LEAF, leaves.max(0) * (t < 34))

        # the picking hand
        if 4 < t < 32:
            h = keys(t, walk)
            buf += light(HAND, 0.55 * np.exp(-((x - h) / 10) ** 2) + 0.12 * np.exp(-((x - h) / 45) ** 2))
            for i in range(F):                                # a glint as each flower is picked
                u = t - t_pick[i]
                if 0 < u < 0.6:
                    buf += light(HAND, 0.6 * np.exp(-u / 0.15) * np.exp(-((x - sites[i]) / 14) ** 2))

        # stems grow down the porch sides toward the street, then a bow
        g = smoothstep(38, 44, t)
        if g > 0:
            front_l = stems_l[1] - g * (stems_l[1] - stems_l[0])
            front_r = stems_r[0] + g * (stems_r[1] - stems_r[0])
            sl = smoothstep(front_l - 10, front_l + 15, x) * (x <= stems_l[1])
            sr = smoothstep(front_r + 10, front_r - 15, x) * (x >= stems_r[0])
            veins = 0.8 + 0.2 * np.sin(x * 0.12 - 1.5 * t)
            buf += light(STEM, 0.3 * (sl + sr) * veins * show_)
        b = smoothstep(44.5, 46.5, t)
        if b > 0:
            tug = 1 + 0.5 * np.exp(-((t - 47) / 0.25) ** 2) + 0.3 * np.exp(-((t - 47.7) / 0.25) ** 2)
            for c0 in (bow_l, bow_r):
                dd = x - c0
                loops = np.exp(-((np.abs(dd) - 18 * b) / 7) ** 2) + 0.8 * np.exp(-(dd / 4) ** 2)
                tails = 0.4 * smoothstep(60, 30, np.abs(dd)) * (np.abs(dd) > 26)
                buf += light(BOW, (0.75 * loops + tails) * b * tug * show_)
        # presentation: a blush spreads out along the wing fronts, the bunch sparkles
        if t > 48:
            e = smoothstep(48, 52, t) * keys(t, [(58, 1), (63, 0)])
            for c0, sgn in ((bow_l, -1), (bow_r, 1)):
                reach = 450 * smoothstep(48, 54, t)
                dd = (x - c0) * sgn
                buf += light(BLUSH, 0.28 * e * smoothstep(reach + 20, reach - 60, dd) * (dd > 30))
            spark = np.clip(tw(t) - 1.1, 0, None) * (np.abs(x - M) < 160)
            buf += light(HAND, 0.6 * spark * e)
        out[f][G.path] = buf
    return out
