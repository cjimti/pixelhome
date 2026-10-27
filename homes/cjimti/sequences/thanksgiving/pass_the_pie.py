"""Pass the Pie: The Porch Front is a pumpkin pie on the table. Cream goes on, a knife cuts it into
eight slices, and the slices are passed hand to hand down both sides of the table, each one a rigid
little object (crust, filling, a dab of cream) that stops at every pair of hands and turns the corners
as it goes, until everyone has one. Bites disappear. Two hands creep toward the last slice from
opposite sides; just before they reach it the dog streaks in from the back of the house, grabs it and
runs out the other end, and the two hands bump into each other."""
import numpy as np
from pixelhome.fx import DT, hexc, light, keys, smoothstep, Flicker, nframes

CODE = 'TG06'
TITLE = 'Pass the Pie'
KIND = 'show'
DESCRIPTION = ('The porch is a pumpkin pie: it is cut into slices that are passed hand to hand around the corners '
               'to everyone at the table. Two hands reach for the last slice. The dog gets there first.')

PUMPKIN = hexc('#ff5200')
CRUST = hexc('#ffa030')
CREAM = hexc('#ffd8a8')
AMBER = hexc('#ff8a18')
CRANBERRY = hexc('#c0102a')
GOLD = hexc('#ffb000')
BROWN = hexc('#5a1c04')
D = 55.0
P0, P1 = 1320.0, 1652.0                     # pie on the Porch Front
W = (P1 - P0) / 8
CENTRES = P0 + W * (np.arange(8) + 0.5)
LEFT_HANDS = [1200.0, 1000.0, 780.0, 560.0, 300.0]
RIGHT_HANDS = [1760.0, 1950.0, 2150.0, 2380.0]


def hop_route(start, hands, dest, t0, hop=0.55, hold=0.3):
    """(time, pd) keyframes: from the pie, hand to hand, stopping at each, until dest."""
    pts = [(t0, start)]
    t = t0
    for h in hands:
        pts.append((t + hop, h))
        t += hop + hold
        pts.append((t, h))
        if h == dest:
            break
    return pts


def render(G, seed=26):
    rng = np.random.default_rng(seed)
    F = nframes(D)
    out = np.zeros((F, G.N, 3))
    n = G.N
    pdp = G.pd[G.path]
    shimmer = Flicker(rng, n, 0.3, 1.5)

    # slices: k=0..3 go left, 5..7 go right, 4 stays (the last one)
    routes, dests = {}, {}
    left_dest = {0: 300.0, 1: 560.0, 2: 780.0, 3: 1000.0}
    right_dest = {7: 2380.0, 6: 2150.0, 5: 1950.0}
    for i, k in enumerate([0, 1, 2, 3]):
        routes[k] = hop_route(CENTRES[k], LEFT_HANDS, left_dest[k], 13.0 + 2.6 * i)
    for i, k in enumerate([7, 6, 5]):
        routes[k] = hop_route(CENTRES[k], RIGHT_HANDS, right_dest[k], 13.6 + 2.6 * i)
    # bites: four per slice, at random moments once everyone has theirs
    bites = {k: np.sort(rng.uniform(24, 38, 4)) for k in routes}
    tip_side = {k: (1 if CENTRES[k] < 1486 else -1) for k in range(8)}   # which end is the crust (the rim)
    cream_t = np.sort(rng.uniform(4.0, 7.5, 8))
    cuts = 9.0 + 0.32 * np.arange(7)
    T_DOG, T_GRAB = 43.2, 44.85
    dog_x = lambda t: np.interp(t, [T_DOG, T_GRAB, T_GRAB + 0.15, T_GRAB + 1.4],
                                [-40, CENTRES[4] - 6, CENTRES[4] + 6, 2620])

    def slice_px(centre, k, eaten, t):
        """Pixels of slice k centred at `centre`: crust at the rim end, filling, a dab of cream."""
        o = (pdp - centre) * tip_side[k] * -1              # o<0 toward the rim (crust), o>0 toward the tip
        half = W / 2 - 1.5
        keep = half - eaten * 2 * half                     # bites come off the tip end
        inside = np.clip((half + o) / 2.5 + 0.5, 0, 1) * np.clip((keep - o) / 2.5 + 0.5, 0, 1)
        crust = np.exp(-((o + half - 3) / 4.5) ** 2)
        fill = 0.55 + 0.1 * shimmer(t)
        c = light(PUMPKIN, inside * fill) + light(CRUST, inside * 0.75 * crust)
        c += light(CREAM, inside * 0.65 * np.exp(-((o - 4) / 4) ** 2) * (eaten < 0.3))
        return c

    for f in range(F):
        t = f * DT
        buf = np.zeros((n, 3))
        buf += light(BROWN, keys(t, [(0, 0), (2, 0.08), (51, 0.08), (55, 0)]) * (1 + 0.2 * shimmer(t)))
        # hands around the table: dim warm dots that brighten while holding something
        hands = LEFT_HANDS + RIGHT_HANDS
        hv = keys(t, [(9, 0), (12, 0.2), (49, 0.2), (54, 0)])

        # --- the whole pie, before it is passed ---
        if t < 13.0 + 0.01:
            grow = smoothstep(0.5, 3.0, t)
            dist = np.abs(pdp - 1486)
            on = np.clip(((P1 - P0) / 2 * grow - dist) / 4, 0, 1)
            rim = np.exp(-((dist - (P1 - P0) / 2 + 4) / 6) ** 2)
            buf += light(PUMPKIN, on * (0.55 + 0.1 * shimmer(t))) + light(CRUST, 0.8 * on * rim)
            for k, tc in enumerate(cream_t):                 # dollops plop, squash, settle
                u = t - tc
                if u > 0:
                    sq = 1 + 0.6 * np.exp(-u / 0.15) * np.cos(25 * u)
                    buf += light(CREAM, on * 0.7 * smoothstep(0, 0.08, u) *
                                 np.exp(-((pdp - CENTRES[k] - 4 * tip_side[k] * -1) / (3.5 * sq)) ** 2))
            for tc_i, tc in enumerate(cuts):                 # the knife: a bright sweep, then a dark gap
                u = t - tc
                gap = P0 + W * (tc_i + 1)
                if -0.25 < u < 0.05:
                    buf += light(CREAM, 0.9 * np.exp(-((pdp - gap) / 5) ** 2))
                if u > 0:
                    buf *= 1 - 0.95 * smoothstep(0, 0.3, u) * np.exp(-((pdp - gap) / 2.2) ** 2)[:, None]
        else:
            for k in range(8):
                if k == 4:
                    if t < T_GRAB:
                        buf += slice_px(CENTRES[4], 4, 0.0, t)
                    continue
                c = keys(t, routes[k])
                eaten = sum(smoothstep(b, b + 0.15, t) for b in bites[k]) / 4
                if eaten < 0.999:
                    buf += slice_px(c, k, eaten, t)
                for b in bites[k]:                          # crumbs fly off each bite
                    u = t - b
                    if 0 < u < 0.5:
                        for s in (-1, 1):
                            buf += light(CRUST, 0.5 * np.exp(-u / 0.15) * np.exp(-((pdp - c - s * (10 + 40 * u)) / 3) ** 2))

        for h in hands:
            buf += light(AMBER, hv * np.exp(-((pdp - h) / 6) ** 2))

        # --- the last slice: two hands creep in, the dog wins ---
        if 39.5 < t < 49:
            lx = keys(t, [(39.5, 1200), (41.0, 1260), (42.0, 1255), (43.5, 1330), (44.6, 1440), (44.95, CENTRES[4] - 9),
                          (45.6, CENTRES[4] - 30), (47.5, 1200)])
            rx = keys(t, [(39.5, 1760), (41.3, 1700), (42.3, 1705), (43.7, 1640), (44.6, 1570), (44.95, CENTRES[4] + 9),
                          (45.6, CENTRES[4] + 30), (47.5, 1760)])
            hvv = keys(t, [(39.5, 0.0), (40.2, 0.8), (47.0, 0.8), (48.5, 0)])
            buf += light(CRANBERRY, hvv * np.exp(-((pdp - lx) / 8) ** 2))
            buf += light(GOLD, hvv * np.exp(-((pdp - rx) / 8) ** 2))
            bump = np.exp(-((t - 44.97) / 0.08) ** 2)
            buf += light(CREAM, 0.8 * bump * np.exp(-((pdp - CENTRES[4]) / 25) ** 2))
        if T_DOG < t < T_GRAB + 1.6:
            x = dog_x(t)
            buf += light(GOLD, np.exp(-((pdp - x) / 6) ** 2))
            for k in range(1, 9):                            # speed streak
                xk = dog_x(t - k * DT)
                buf += light(GOLD, 0.5 * (1 - k / 9) * np.exp(-((pdp - xk) / 5) ** 2))
            if t > T_GRAB:
                buf += slice_px(x + 22, 4, 0.0, t)
        # everyone laughs
        if t > 45.6:
            u = t - 45.6
            laugh = np.exp(-u / 2.5) * (0.5 + 0.5 * np.sin(2 * np.pi * 5.5 * u)) * smoothstep(0, 0.3, u)
            for h in hands:
                buf += light(AMBER, 0.55 * laugh * np.exp(-((pdp - h) / 10) ** 2))
            buf += light(AMBER, 0.14 * smoothstep(0.5, 2.5, u) * keys(t, [(50, 1), (55, 0)]))
        out[f][G.path] = buf
    return out
