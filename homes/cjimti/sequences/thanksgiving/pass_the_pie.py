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


SEED = 26
PASS_L, PASS_R, PASS_GAP = 13.0, 13.6, 2.6      # the first slice leaves each way at PASS_L/PASS_R, the next PASS_GAP later
LEFT_DEST = {0: 300.0, 1: 560.0, 2: 780.0, 3: 1000.0}   # slices k=0..3 go left, 5..7 right, 4 stays (the last one)
RIGHT_DEST = {7: 2380.0, 6: 2150.0, 5: 1950.0}
CUTS = 9.0 + 0.32 * np.arange(7)
T_DOG, T_GRAB = 43.2, 44.85
T_BUMP, T_LAUGH, LAUGH_HZ = 44.97, 45.6, 5.5
LX_KEYS = [(39.5, 1200), (41.0, 1260), (42.0, 1255), (43.5, 1330), (44.6, 1440), (44.95, CENTRES[4] - 9),
           (45.6, CENTRES[4] - 30), (47.5, 1200)]
RX_KEYS = [(39.5, 1760), (41.3, 1700), (42.3, 1705), (43.7, 1640), (44.6, 1570), (44.95, CENTRES[4] + 9),
           (45.6, CENTRES[4] + 30), (47.5, 1760)]


def dog_x(t):
    return np.interp(t, [T_DOG, T_GRAB, T_GRAB + 0.15, T_GRAB + 1.4], [-40, CENTRES[4] - 6, CENTRES[4] + 6, 2620])


def table(G, seed=SEED):
    """What render() draws from the rng, and the slices' routes: shimmer, routes, bites, cream times."""
    rng = np.random.default_rng(seed)
    shimmer = Flicker(rng, G.N, 0.3, 1.5)
    routes = {}
    for i, k in enumerate([0, 1, 2, 3]):
        routes[k] = hop_route(CENTRES[k], LEFT_HANDS, LEFT_DEST[k], PASS_L + PASS_GAP * i)
    for i, k in enumerate([7, 6, 5]):
        routes[k] = hop_route(CENTRES[k], RIGHT_HANDS, RIGHT_DEST[k], PASS_R + PASS_GAP * i)
    # bites: four per slice, at random moments once everyone has theirs
    bites = {k: np.sort(rng.uniform(24, 38, 4)) for k in routes}
    cream_t = np.sort(rng.uniform(4.0, 7.5, 8))
    return shimmer, routes, bites, cream_t


def render(G, seed=SEED):
    F = nframes(D)
    out = np.zeros((F, G.N, 3))
    n = G.N
    pdp = G.pd[G.path]
    shimmer, routes, bites, cream_t = table(G, seed)
    tip_side = {k: (1 if CENTRES[k] < 1486 else -1) for k in range(8)}   # which end is the crust (the rim)
    cuts = CUTS

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
        if t < PASS_L + 0.01:
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
            lx = keys(t, LX_KEYS)
            rx = keys(t, RX_KEYS)
            hvv = keys(t, [(39.5, 0.0), (40.2, 0.8), (47.0, 0.8), (48.5, 0)])
            buf += light(CRANBERRY, hvv * np.exp(-((pdp - lx) / 8) ** 2))
            buf += light(GOLD, hvv * np.exp(-((pdp - rx) / 8) ** 2))
            bump = np.exp(-((t - T_BUMP) / 0.08) ** 2)
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
        if t > T_LAUGH:
            u = t - T_LAUGH
            laugh = np.exp(-u / 2.5) * (0.5 + 0.5 * np.sin(2 * np.pi * LAUGH_HZ * u)) * smoothstep(0, 0.3, u)
            for h in hands:
                buf += light(AMBER, 0.55 * laugh * np.exp(-((pdp - h) / 10) ** 2))
            buf += light(AMBER, 0.14 * smoothstep(0.5, 2.5, u) * keys(t, [(50, 1), (55, 0)]))
        out[f][G.path] = buf
    return out


# ---------------------------------------------------------------- music ----------------------------------------------
# Dessert in Bb major. A triangle calls everyone to the table, a harp rolls the pie out, each dollop of cream is a
# bloop and each cut a knife swish and a chop down the scale. Passing is plucked: every time a slice lands in a pair
# of hands that spot on the house plucks a note, higher the farther it has travelled, over sustained clarinet and
# cello. Eating is a 3/4 waltz with a chomp for every bite. Then the two hands tiptoe in on pizzicato and bassoon, the
# dog scrabbles across the house on woodblocks, the hands bonk, and the whole table laughs in time with the lights.

BEAT3 = 0.5                                 # the waltz's beat; a bar of 3/4 is 1.5 s
CH = {'Bb': (46, 50, 53), 'Eb': (46, 51, 55), 'F': (45, 48, 53), 'Gm': (46, 50, 55), 'F7': (45, 48, 51)}
ROOT = {'Bb': 34, 'Eb': 39, 'F': 41, 'Gm': 43, 'F7': 41}
SCALE = [58, 60, 62, 63, 65, 67, 69, 70, 72, 74, 75, 77]     # Bb major from Bb3
WALTZ = [('Bb', [('F4', 1), ('Bb4', 1), ('D5', 1)]), ('Eb', [('C5', 2), ('Bb4', 1)]),
         ('F', [('A4', 1), ('C5', 1), ('Eb5', 1)]), ('Bb', [('D5', 3)]),
         ('Gm', [('D5', 1), ('Bb4', 1), ('G4', 1)]), ('Eb', [('Bb4', 1), ('G4', 1), ('Eb4', 1)]),
         ('F', [('F4', 1), ('A4', 1), ('C5', 1)]), ('Bb', [('Bb4', 3)]),
         ('Eb', [('G4', 1), ('Bb4', 1), ('Eb5', 1)]), ('F7', [('C5', 1), ('A4', 1), ('F4', 1)])]
PASS_CH = ['Bb', 'Eb', 'Gm', 'F']           # one chord for each slice that leaves to the left


def score(M, G):
    from pixelhome.audio import SR, note, slide, whoosh
    n = note
    clar = M.sampler('Woodwinds/Clarinet/susLong/*.wav', tune=-12)
    clst = M.sampler('Woodwinds/Clarinet/stac/*.wav', tune=-12)
    bsn = M.sampler('Woodwinds/Bassoon/stac/*.wav', tune=-12)
    cello = M.sampler('Strings/Cello Section/susvib/*.wav', tune=-12)
    trem = M.sampler('Strings/Cello Section/trem/*.wav', tune=-12)
    cpizz = M.sampler('Strings/Cello Section/pizzT/*.wav', tune=-12)
    vpizz = M.sampler('Strings/Violin Section/Pizz/*.wav', tune=-12)
    bass = M.sampler('Strings/Solo Contrabass/Pizz/*.wav', tune=-12)
    piano = M.sampler('Keys/Upright Nr1/*.wav')
    harp = M.sampler('Strings/Harp/*.wav')
    mar = M.sampler('Percussion/Marimba/*.wav', tune=-12)
    xylo = M.sampler('Percussion/Xylo/*.wav', tune=-12)
    glock = M.sampler('Percussion/Glock/*.wav', tune=-12)
    wood = M.hits('VSCO 1 Percussion/varWood/wood_click*.wav')
    clave = M.hits('Percussion/Claves1_Hit*.wav')
    tri = M.hits('Percussion/Triangle3-Hit_v*.wav')
    slap = M.hits('VSCO 1 Percussion/varWood/slapstick[0-9].wav')
    log = M.hits('VSCO 1 Percussion/varWood/log_drum/*.wav')
    timp = M.hits('Percussion/Timpani/Timpani1_Hit*.wav')
    troll = M.hits('Percussion/Timpani/Rolls/*.wav')
    bd = M.hits('Percussion/BDrumNewhit_v[4-7]*.wav')
    crash_s = M.hits('Percussion/cymbal-crashshort*.wav')

    for name, gain, rev in (('melody', 0.28, 0.25), ('pluck', 0.42, 0.2), ('bass', 0.45, 0.08), ('keys', 0.3, 0.2),
                            ('strings', 0.22, 0.3), ('harp', 0.32, 0.3), ('mallet', 0.36, 0.2), ('perc', 0.55, 0.12),
                            ('drums', 0.5, 0.18), ('fx', 0.16, 0.25)):
        M.bus(name, gain=gain, reverb=rev)

    order = np.argsort(G.pd)
    xs, ds = G.pos[order, 0], G.pd[order]
    x0, x1 = xs.min(), xs.max()

    def pan_at(d):                          # path distance -> left/right across the facade, as seen from the street
        x = np.interp(d, ds, xs)
        return float(0.85 * (2 * (x - x0) / (x1 - x0) - 1))

    def travel(sig, d0, d1):                # a sound that moves along the roofline from d0 to d1 while it plays
        a = (np.linspace(pan_at(d0), pan_at(d1), sig.shape[1]) + 1) * np.pi / 4
        return sig * np.sqrt(2) * np.vstack([np.cos(a), np.sin(a)])

    def bloop(seconds=0.12):                # a dollop landing: a quick rising sine
        t = np.arange(int(seconds * SR)) / SR
        ph = 2 * np.pi * np.cumsum(260 * (3.2 ** np.clip(t / 0.07, 0, 1))) / SR
        s = np.sin(ph) * np.clip(t / 0.004, 0, 1) * np.exp(-t / 0.045)
        return np.vstack([s, s])

    pie = pan_at((P0 + P1) / 2)
    _, routes, bites, cream_t = table(G)

    def waltz(t0, bars, vel=70, tune=True):  # piano oom-pah-pah and contrabass under the clarinet
        for b, (c, notes) in enumerate(bars):
            t = t0 + b * 3 * BEAT3
            M.add('bass', bass.play(ROOT[c], vel + 10), t, 1.0, -0.1)
            for k in (1, 2):
                for m in CH[c]:
                    M.add('keys', piano.play(m + 12, vel - 5), t + k * BEAT3, 0.7, 0.15)
            if tune:
                e = 0
                for m, ln in notes:
                    M.add('melody', clar.play(n(m), vel + 15, dur=ln * BEAT3 * 0.92, release=0.15), t + e * BEAT3, 1.0, -0.1)
                    e += ln

    # ---- 0-9: dinner is served; the pie rolls out, cream plops on ----
    M.add('perc', tri.play(100), 0.4, 0.6, pie)
    M.add('perc', tri.play(80), 0.9, 0.4, pie)
    for i in range(10):                     # the pie grows out from the middle: a harp roll, both ways
        M.add('harp', harp.play(SCALE[i % 7] - 12 + 12 * (i // 7) + 12 * (i > 3), 62 + 3 * i), 0.5 + 0.25 * i, 0.9,
              pan_at((P0 + P1) / 2 + (P1 - P0) / 2 * (i / 9) * (1 if i % 2 else -1)))
    M.add('strings', cello.play(n('Bb2'), 60, dur=8.5, release=0.8), 0.5, 1.0, pie)
    M.add('strings', cello.play(n('F3'), 50, dur=8.5, release=0.8), 1.5, 0.8, pie)
    waltz(3.0, [(c, []) for c in ('Bb', 'Eb', 'F', 'Bb')], 55, tune=False)
    for k, tc in enumerate(cream_t):        # dollops land in the order they come, climbing the scale
        p = pan_at(CENTRES[k])
        M.add('fx', bloop(), tc, 2.2, p)
        M.add('mallet', mar.play(SCALE[k], 92), tc, 0.8, p)
    # ---- 9-11: the knife: a swish into every cut, a chop down the scale ----
    for i, tc in enumerate(CUTS):
        p = pan_at(P0 + W * (i + 1))
        M.add('fx', whoosh(0.3, 1500, 5000, 0.5, seed=10 + i), tc - 0.25, 0.9, p)
        M.add('perc', clave.play(115), tc, 1.0, p)
        M.add('mallet', xylo.play(SCALE[11 - i], 110), tc, 1.0, p)
    tc = CUTS[-1] + (CUTS[1] - CUTS[0])     # on the next tick: cut, ta-da
    for i, m in enumerate(CH['Bb']):
        M.add('harp', harp.play(m + 24, 95), tc + 0.04 * i, 0.9, pie)
        M.add('pluck', cpizz.play(m + 12, 100), tc, 0.7, pie)
    M.add('bass', bass.play(ROOT['Bb'], 100), tc, 1.0)
    M.add('perc', tri.play(85), tc, 0.5, pie)
    M.add('strings', cello.play(n('Bb2'), 55, dur=PASS_L - tc, release=0.3), tc, 1.0, pie)
    M.add('strings', cello.play(n('D3'), 45, dur=PASS_L - tc, release=0.3), tc, 0.8, pie)
    for i, m in enumerate(('F3', 'G3', 'A3')):   # who wants pie?
        M.add('melody', bsn.play(n(m), 90), PASS_L - (3 - i) * 0.3, 0.9, pie)

    # ---- 13-22.5: passing, a pluck at every pair of hands it lands in ----
    lefts, rights = [0, 1, 2, 3], [7, 6, 5]
    for i, k in enumerate(lefts):
        c = PASS_CH[i]
        t = routes[k][0][0]
        span = PASS_GAP if i < 3 else routes[k][-1][0] - t
        for m, v in ((ROOT[c] + 12, 62), (CH[c][1] + 12, 52), (CH[c][2] + 12, 48)):
            M.add('strings', cello.play(m, v, dur=span, release=0.4), t, 1.0, pie)
        M.add('melody', clar.play(CH[c][0] + 24, 55, dur=span, release=0.4), t, 0.6, pie)
        M.add('bass', bass.play(ROOT[c], 95), t, 1.0, pie)
    for k in lefts + rights:
        side = LEFT_HANDS if k in lefts else RIGHT_HANDS
        i = (lefts if k in lefts else rights).index(k)
        c = PASS_CH[i]                      # the chord of the moment it leaves the plate
        pts = routes[k]
        M.add('harp', harp.play(CH[c][0] + 24, 85), pts[0][0], 0.8, pan_at(pts[0][1]))      # off the plate
        for j in range(1, len(pts), 2):
            (ta, da), (tb, db) = pts[j - 1], pts[j]
            M.add('fx', travel(whoosh(tb - ta, 400, 1400, 0.4, seed=100 + 10 * k + j), da, db), ta, 0.5)
            chord = CH[PASS_CH[min(3, int((tb - PASS_L) // PASS_GAP))]]
            m = sorted(x + 12 * o for x in chord for o in (1, 2))[side.index(db) + 1]
            inst = mar if k in lefts else vpizz
            M.add('pluck', inst.play(m, 100), tb, 1.0, pan_at(db))
            M.add('perc', wood.play(70), tb, 0.5, pan_at(db))
    t = routes[3][-1][0]                    # everyone has one
    for m in CH['Bb']:
        M.add('pluck', cpizz.play(m + 12, 110), t, 0.8, pie)
        M.add('harp', harp.play(m + 24, 90), t, 0.8, pie)
    M.add('bass', bass.play(ROOT['Bb'], 110), t, 1.0)
    M.add('perc', tri.play(90), t, 0.5, pie)

    # ---- 23-38: the eating waltz, a chomp for every bite and a gulp when a slice is gone ----
    tw = 23.0
    waltz(tw, WALTZ, 58)
    for k, bs in bites.items():
        d = routes[k][-1][1]
        p = pan_at(d)
        for j, tb in enumerate(bs):
            M.add('perc', clave.play(115), tb, 1.1, p)
            M.add('perc', wood.play(120), tb + 0.01, 1.3, p)
            for s in (-1, 1):               # crumbs fly off both ways
                M.add('perc', wood.play(45), tb + 0.08, 0.3, pan_at(d + s * 25))
            if j == len(bs) - 1:
                M.add('melody', bsn.play(n('F2'), 95), tb + 0.2, 0.9, p)
                M.add('melody', bsn.play(n('Bb1'), 95), tb + 0.35, 0.9, p)
    te = tw + len(WALTZ) * 3 * BEAT3
    for m in CH['Bb']:
        M.add('keys', piano.play(m + 12, 70), te, 0.8, 0.15)
    M.add('bass', bass.play(ROOT['Bb'], 85), te, 1.0)
    M.add('melody', clar.play(n('Bb4'), 75, dur=LX_KEYS[0][0] - te, release=0.3), te, 1.0, -0.1)

    # ---- 39.5-45: two hands tiptoe in for the last slice; the dog gets it ----
    t0, tg = LX_KEYS[0][0], T_GRAB
    M.add('strings', trem.play(n('F2'), 55, dur=tg - t0, release=0.05), t0, 1.0, pie)
    M.add('strings', trem.play(n('C3'), 50, dur=tg - t0, release=0.05), t0, 0.8, pie)
    M.add('drums', troll.play(75, dur=tg - T_DOG), T_DOG, 0.7, pan_at(0))
    for kf, inst, base, off, who in ((LX_KEYS, cpizz, n('F2'), 0.0, 'L'), (RX_KEYS, vpizz, n('C4'), 0.15, 'R')):
        for i, t in enumerate(np.arange(t0 + off, kf[5][0] - 0.05, 0.3)):
            x, x2 = keys(t, kf), keys(t + 0.1, kf)
            if abs(x2 - x) < 2.0:         # it's holding still
                continue
            m = base + int(abs(x - kf[0][1]) / 20)
            M.add('pluck', inst.play(m, 80), t, 0.6, pan_at(x))
            if who == 'L':
                M.add('melody', bsn.play(m, 80), t, 0.6, pan_at(x))
            else:
                M.add('melody', clst.play(m + 12, 75), t, 0.5, pan_at(x))
    for kf in (LX_KEYS, RX_KEYS):           # the last lunge
        M.add('fx', slide(0.0, kf[5][0] - kf[4][0], 700, 1300, kf[5][0] - kf[4][0] + 0.05, 0.45), kf[4][0], 0.8,
              pan_at(kf[4][1]))
    ts = np.arange(T_DOG, T_GRAB + 1.4, 0.055)   # the dog: claws scrabbling the length of the house
    for i, t in enumerate(ts):
        d = float(dog_x(t))
        if -40 < d < G.length + 20:
            M.add('perc', wood.play(70 + 20 * (i % 2)), t, 0.35, pan_at(np.clip(d, 0, G.length)))
    M.add('fx', travel(whoosh(T_GRAB - T_DOG, 300, 2500, 0.5, seed=7), 0, CENTRES[4]), T_DOG, 0.6)
    for i in range(12):                     # running in: a xylophone run up to the pie
        t = T_DOG + (T_GRAB - T_DOG) * i / 12
        M.add('mallet', xylo.play(SCALE[i % 8] + 12 * (i // 8), 70 + 3 * i), t, 0.6, pan_at(float(dog_x(t))))
    M.add('perc', slap.play(127), T_GRAB, 1.3, pie)                       # snatched
    M.add('fx', slide(0.0, 0.12, 600, 1900, 0.16, 0.6), T_GRAB, 0.9, pie)
    M.add('drums', timp.play(125, pitch=3), T_BUMP, 1.2, pie)              # bonk
    M.add('perc', log.play(127), T_BUMP, 1.4, pie)
    M.add('drums', bd.play(120), T_BUMP, 1.0, pie)
    M.add('drums', crash_s.play(90), T_BUMP, 0.4, pie)
    M.add('fx', travel(whoosh(1.25, 2500, 500, 0.5, seed=8), CENTRES[4], G.length), T_GRAB + 0.15, 0.9)
    t_out = float(np.interp(G.length, dog_x(np.array([T_GRAB + 0.15, T_GRAB + 1.4])), [T_GRAB + 0.15, T_GRAB + 1.4]))
    M.add('fx', slide(0.0, 0.5, 1700, 500, 0.55, 0.6), t_out, 0.9, pan_at(G.length))   # out the far end
    M.add('mallet', glock.play(n('Bb5'), 60), t_out + 0.5, 0.5, pan_at(G.length))

    # ---- 45.6: the whole table laughs, in time with the flicker of the hands ----
    hands = LEFT_HANDS + RIGHT_HANDS
    ha = [n(m) for m in ('F4', 'D4', 'Bb3', 'C4', 'A3', 'F3')]
    for k in range(40):
        u = (0.25 + k) / LAUGH_HZ
        v = np.exp(-u / 2.5)
        if v < 0.15:
            break
        p = pan_at(hands[(3 * k) % len(hands)])
        m = ha[k % len(ha)] - 2 * (k // 12)
        M.add('melody', (bsn if k % 2 else clst).play(m + 12 * (k % 2 == 0), int(50 + 70 * v)), T_LAUGH + u, 1.0, p)
        if k % 3 == 0:
            M.add('pluck', vpizz.play(m + 12, int(40 + 60 * v)), T_LAUGH + u, 0.6, -p)

    # ---- 47.5-55: back to the table, a last phrase of the waltz ----
    tl = LX_KEYS[-1][0]
    waltz(tl, WALTZ[5:8], 62)
    tf = tl + 3 * 3 * BEAT3
    for i, m in enumerate(('Bb2', 'F3', 'Bb3', 'D4', 'F4', 'Bb4', 'D5')):
        M.add('harp', harp.play(n(m), 70), tf + 0.07 * i, 0.8, pan_at(LEFT_HANDS[-1] + (RIGHT_HANDS[-1] - LEFT_HANDS[-1]) * i / 6))
    for m, v in (('Bb2', 60), ('F3', 52), ('D4', 48)):
        M.add('strings', cello.play(n(m), v, dur=D - tf - 0.5, release=1.2), tf, 1.0, 0.1)
    M.add('mallet', glock.play(n('F5'), 50), tf + 1.5, 0.4, pie)
