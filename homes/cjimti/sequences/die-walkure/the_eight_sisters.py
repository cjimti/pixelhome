"""The Eight Sisters: all eight Valkyries together, and the Ride (Donington 47) at full strength, horns,
trumpets, trombones and tubas over galloping cellos, basses and bassoons, with timpani on every phrase.

They leave the rock in a column, Gerhilde at its head, and gallop the length of the house: out to the free end
of Right, wheeling there and thundering back past the rock to the far end of Side, a train of eight colours
each trailing a comet. Then they split, the warm sisters (red, orange, yellow, pink) one way and the cool
(green, sky, violet, purple) the other, sweeping across each other over the rock again and again, every
crossing a burst of white, and between the crossings they toss their cries across the whole house:
"Hojotoho!" on a trumpet from one end, a spark of her colour flying the length of the roof, and "Heiaha!" back
from a sister at the other end. Then the Valkyries' own motif (22) in the full brass while the eight spread out
evenly and ride in a rainbow that sweeps the entire house end to end, the descending chords (22b) pouring
down between the strains and the trills (22a) glittering over the clouds.

The climax: the sisters fall back to both ends of the house and charge inward, meeting over the rock in a
flash of the whole house, fling out to the ends and charge again, and wheel together over the summit while
lightning cracks in the clouds. They gather on the rock in their places as the Ride closes on a great B minor
chord. And then a stillness, a tremolo, and every one of them turns: far off at the free end of Right a silver
light with gold glints is riding hard toward them, an amber light held close beside her. "Brünnhilde!" they
call, horns from every side, and a lone trumpet far off on the right answers with the Ride.

compose() holds every note, choreography() every position; render() and score() read both."""
import numpy as np
from pixelhome.audio import note
from pixelhome.fx import DT, hexc, light, smoothstep, nframes, Flicker
from pixelhome.leitmotifs import play

CODE = 'WK21'
TITLE = 'The Eight Sisters'
KIND = 'show'
DESCRIPTION = ('All eight Valkyries together at last, galloping across the whole house in formation, crossing and '
               'calling to each other over the storm. Then they gather on their rock and see their sister '
               'Brünnhilde riding toward them, carrying a woman.')
VOICEOVER = ('Eight sisters, eight colours, and one of the most famous pieces of music ever written. '
             'This is the Ride at full gallop.')

RB = 0.3                                    # a quarter note of the Ride
VB = 0.6                                    # a beat of the Valkyries' motif
TRANS = [0, 3, 0, -2]
ROOTS = ['B1', 'D2', 'B1', 'A1']
# the music, section by section: (kind, start)
PLAN = [('period', 1.0), ('period', 8.2), ('interlude', 15.4), ('period', 19.0), ('period', 26.2),
        ('interlude', 33.4), ('valk', 37.0), ('valk', 44.2), ('interlude', 51.4), ('period', 55.0),
        ('period', 62.2)]
T_GATHER = 69.4                             # the cadence: home on the rock
T_SEE = 72.4                                # they see her coming
T_CALL = 74.4                               # "Brünnhilde!"
T_COL, T_CROSS, T_CAROUSEL, T_CLIMAX = 1.0, 19.0, 37.0, 55.0
BURSTS = [58.6, 64.0]                       # the charges meet over the rock
TOSSES = [(21.0, 0, 4), (21.7, 4, 7), (25.6, 3, 2), (26.3, 2, 6), (30.0, 7, 5), (30.7, 5, 1), (34.4, 6, 0),
          (35.1, 0, 3)]                     # cries thrown across the house: (time, from, to)
D = 80.0
CLOCK = 80.0 * 20

NAMES = ['Gerhilde', 'Ortlinde', 'Waltraute', 'Schwertleite', 'Helmwige', 'Siegrune', 'Grimgerde', 'Rossweisse']
COLS = [hexc(h) for h in ('#ff4040', '#ff9a20', '#f0e040', '#40e070', '#40d0ff', '#6060ff', '#c050ff', '#ff60c0')]
SPOTS = [('Porch Left', 0.25), ('Porch Left', 0.65), ('Porch Front', 0.12), ('Porch Front', 0.37),
         ('Porch Front', 0.63), ('Porch Front', 0.88), ('Porch Right', 0.35), ('Porch Right', 0.75)]
WARM, COOL = [0, 1, 2, 7], [3, 4, 5, 6]
STRIKES = [(12.0, 'Side'), (24.0, 'Right'), (40.6, 'Left'), (47.8, 'Right'), (56.0, 'Side'), (58.6, 'all'),
           (61.0, 'Right'), (64.0, 'all'), (66.2, 'Left'), (68.0, 'Right')]
HOJO = [(0, 0.25, 'F#4'), (0.25, 0.75, 'B4'), (1, 0.5, 'B4'), (1.5, 1.5, 'D5')]      # "Ho-jo-to-ho!" (after Wagner)
HEIA = [(0, 0.5, 'D5'), (0.5, 0.5, 'B4'), (1, 2.0, 'F#4')]                         # "Hei-a-ha!"
BRUNN = [(0, 0.5, 'B4'), (0.5, 1.5, 'F#4'), (2, 0.5, 'A4'), (2.5, 2.0, 'D5')]      # "Brünn-hil-de!" (composed)
CBEAT = 0.26
SILVER = hexc('#f4f8ff')
GOLD = hexc('#ffd060')
AMBER = hexc('#ffa860')
CLOUD = hexc('#2a3448')
STORM = hexc('#5a6a8a')
ROCK = hexc('#343c50')
NAVY = hexc('#0c1438')
PALE = hexc('#a0b0c0')
FLASH = hexc('#e0e8ff')
WHITE = hexc('#ffffff')


def at(G, seg, u):
    s = G.pd[G.seg[seg]]
    return float(s.min() + u * (s.max() - s.min()))


def compose():
    """Every note: (time, seconds, midi, velocity, part, who)."""
    N = []

    def add(t, d, m, v, part, who=None):
        N.append((float(t), float(d), note(m) if isinstance(m, str) else int(m), int(v), part, who))

    def trills(t0, beats, vel):
        for t, m, v, d in play('valkyrie_cry', t0, RB, 0, vel):
            if t < t0 + beats * RB:
                add(t, d, m, v, 'trill')

    def cry(t0, k, tune, vel=112, tr=0):
        for b, dd, n in tune:
            add(t0 + b * CBEAT, dd * CBEAT * 1.2, note(n) + tr, vel, 'cry', k)

    add(0.0, 1.0, 'B1', 100, 'roll')
    for k in range(8):                                                          # off the rock, every one of them
        cry(0.1 + 0.11 * k, k, HOJO[:2], 100, (0, 2, 4, 5)[k % 4])
    for kind, t0 in PLAN:
        if kind == 'period':
            for p, (tr, root) in enumerate(zip(TRANS, ROOTS)):
                tp = t0 + p * 6 * RB
                for t, m, v, d in play('ride', tp, RB, tr, 112 + 4 * (t0 >= T_CLIMAX)):
                    add(t, d * 1.6, m, v, 'ride')
                for bar in range(2):
                    for b, dd in ((0, 1.0), (1.0, 0.5), (1.5, 1.0), (2.5, 0.5)):
                        add(tp + (bar * 3 + b) * RB, dd * RB * 0.9, note(root) + (12 if b else 0), 112 - 6 * (b > 0),
                            'gallop')
                add(tp, 0.4, root, 104, 'timp')
                if p == 3 and t0 < T_CLIMAX:
                    trills(tp, 6, 84)
        elif kind == 'interlude':
            for t, m, v, d in play('valkyries_descent', t0 + 0.3, 0.5, 0, 110):
                add(t, d * 1.1, m, v, 'descent')
            trills(t0 + 0.3, 8, 90)
            add(t0, 0.3, 'B1', 112, 'crash')
        elif kind == 'valk':
            tr = 0 if t0 < 40 else 3
            for t, m, v, d in play('valkyries', t0, VB, tr, 112):
                add(t, d * 1.05, m, v, 'valk')
            for j in range(16):                                                 # driving triplets underneath
                for i in range(3):
                    add(t0 + j * 3 * VB / 4 + i * VB / 4, VB / 4 * 0.8, note('E2') + tr + (0, 7, 12)[i], 96, 'drive')
            add(t0, 0.4, 'E2', 110, 'crash')
    for i, (tt, a, b) in enumerate(TOSSES):                                     # cries thrown across the house
        cry(tt, a, HOJO, 112, 2 * (i % 3))
        cry(tt + 0.6, b, HEIA, 112, 2 * (i % 3))
    for tb in BURSTS:
        add(tb - 1.6, 1.6, 'B1', 110, 'surge')
        add(tb, 3.0, 'B1', 124, 'burst')
    for m in ('B1', 'F#2', 'B2', 'D3', 'F#3', 'B3'):                            # home: a great B minor chord
        add(T_GATHER, T_SEE - T_GATHER + 0.6, m, 112, 'cadence')
    add(T_GATHER, 0.4, 'B1', 124, 'crash')
    for k in range(8):
        cry(T_GATHER + 0.4 + 0.2 * k, k, HEIA[:2], 100, (0, 2, 4, 5)[k % 4])
    add(T_SEE, D - T_SEE, 'B2', 70, 'sight')                                    # stillness; they turn
    add(T_SEE, D - T_SEE, 'F#3', 64, 'sight')
    trills(T_SEE + 0.6, 6, 70)
    for j, k in enumerate((4, 0, 7, 2)):                                        # "Brünnhilde!"
        for b, dd, n in BRUNN:
            add(T_CALL + 0.8 * j + b * CBEAT, dd * CBEAT * 1.2, note(n) + (0, 2, -3, 5)[j], 104, 'name', k)
    for t, m, v, d in play('ride', T_CALL + 1.4, RB, 0, 92):                    # far off, her answer
        add(t, d * 1.5, m, v, 'far')
    for t, m, v, d in play('ride', T_CALL + 1.4 + 6 * RB, RB, 3, 98):
        add(t, d * 1.5, m, v, 'far')
    for h in range(int((D - T_SEE - 1.0) / (1.5 * RB))):                        # her horse, coming
        add(T_SEE + 1.0 + h * 1.5 * RB, 0.1, 'B1', 60 + 2 * h, 'hoof')
    for ts, where in STRIKES:
        add(ts, 2.0, 'B0', 104 if where != 'all' else 124, 'thunder', where)
    return sorted(N, key=lambda e: e[0])


def follow(target, rate):
    """Critically damped chase of a target track (per frame), `rate` in 1/s per frame."""
    x = np.empty_like(target)
    x[0], v = target[0], 0.0
    for f in range(1, len(target)):
        w = rate[f]
        v += (w * w * (target[f] - x[f - 1]) - 2 * w * v) * DT
        x[f] = x[f - 1] + v * DT
    return x


def sway(G, k, tt):
    """Where a sister wheels on the rock, in her place (shared with the scenes either side)."""
    return at(G, *SPOTS[k]) + 9 * np.sin(2 * np.pi * (0.31 * tt + k / 8)) + 4 * np.sin(2 * np.pi * (0.73 * tt + k / 3))


def tri(u):
    """0..1..0 triangle wave."""
    u = np.mod(u, 2.0)
    return np.where(u < 1, u, 2 - u)


def choreography(G):
    """Per frame: each sister's position, and Brünnhilde's (with Sieglinde) at the end."""
    F = nframes(D)
    t = np.arange(F) * DT
    L = G.length
    c = at(G, 'Porch Front', 0.5)
    lo, hi = 160.0, L - 30
    home = np.array([sway(G, k, t + CLOCK) for k in range(8)])
    tgt = home.copy()
    rate = np.full((8, F), 9.0)

    def put(k, a, b, where, r=9.0):
        m = (t >= a) & (t < b)
        tgt[k][m] = where[m] if np.ndim(where) else where
        rate[k][m] = r

    # the column: out to the free end of Right, back the whole length of the house, home over the rock
    hts, hds = zip(*[(T_COL, c), (T_COL + 4.2, hi), (T_COL + 5.0, hi - 40), (T_COL + 12.0, lo), (T_COL + 12.8, lo + 40),
                     (T_CROSS, c)])
    for i in range(8):
        lag = 0.34 * i
        head = np.interp(t - lag, hts, hds)
        put(i, T_COL + lag, T_CROSS + lag, head, 12.0)
    # the crossing: warm and cool sweep across each other over the rock, each group a little column
    for g, grp in ((1, WARM), (-1, COOL)):
        for j, k in enumerate(grp):
            x = c + g * 1150 * np.sin(2 * np.pi * (t - T_CROSS - 0.34 * j) / 9.0)
            put(k, T_CROSS + 0.34 * 8, T_CAROUSEL, np.clip(x, lo, hi), 10.0)
    # the carousel: all eight spread evenly, a rainbow sweeping the whole house end to end
    for k in range(8):
        x = lo + (hi - lo) * tri(k / 4.0 + (t - T_CAROUSEL) / 7.2)
        put(k, T_CAROUSEL, T_CLIMAX, x, 3.5)
    # the climax: back to both ends, charge in, meet over the rock, out, in again, wheel over the summit
    for k in range(8):
        side = -1 if k < 4 else 1
        end = (lo + 35 * k) if side < 0 else (hi - 35 * (7 - k))
        meet = c + side * (12 + 14 * (k % 4))
        marks = [(T_CLIMAX, end), (56.9, end), (BURSTS[0], meet), (61.3, end), (BURSTS[1], meet)]
        ts, ds = zip(*marks)
        put(k, T_CLIMAX, BURSTS[1], np.interp(t, ts, ds), 9.0)
        whirl = c + 300 * np.sin(2 * np.pi * ((t - BURSTS[1]) / 3.0 + k / 8))
        put(k, BURSTS[1], T_GATHER, whirl, 7.0)
        put(k, T_GATHER, D, home[k], 6.0)
    pos = np.array([follow(tgt[k], rate[k]) for k in range(8)])
    lift = smoothstep(0.0, 1.0, t) * (1 - smoothstep(T_GATHER, T_GATHER + 2.6, t))
    pos = home + (pos - home) * lift                      # exact in their places at both ends
    bpos = at(G, 'Right', 1.0) + 40 - 120 * smoothstep(T_SEE + 1.0, D, t) ** 0.8
    return dict(t=t, pos=pos, bpos=bpos)


def rock_bed(d, tt, porch, stone):
    """Act III: storm clouds billowing over the wings and Side, the still, dark rock on the porch (shared by WK19-WK24)."""
    c1 = 0.5 + 0.5 * np.cos(2 * np.pi * (d / 430 - 0.03 * tt))
    c2 = 0.5 + 0.5 * np.cos(2 * np.pi * (d / 160 + 0.055 * tt) + 1)
    billow = 0.6 * c1 + 0.4 * c1 * c2
    wing = 1 - porch
    return (light(CLOUD, (0.38 + 0.62 * billow ** 1.5) * wing) + light(STORM, 0.6 * billow ** 3 * wing)
            + light(NAVY, 0.4 * wing) + light(ROCK, 0.6 * stone * porch) + light(NAVY, 0.4 * porch))


def render(G, seed=21):
    rng = np.random.default_rng(seed)
    F = nframes(D)
    out = np.zeros((F, G.N, 3))
    d = G.pd
    L = G.length
    C = choreography(G)
    N = compose()
    porch = np.isin(G.seg_of, ['Porch Left', 'Porch Front', 'Porch Right']).astype(float)
    wing = 1 - porch
    stone = 0.8 + 0.2 * np.interp(d / 18, np.arange(int(L / 18) + 2), np.random.default_rng(30).uniform(-1, 1, int(L / 18) + 2))
    jag = [0.55 + 0.45 * np.random.default_rng(100 + k).random(G.N) for k in range(8)]
    seg_d = {s: (G.pd[G.seg[s]].min(), G.pd[G.seg[s]].max()) for s in G.seg}
    c = at(G, 'Porch Front', 0.5)
    ride = np.array([e[0] for e in N if e[4] in ('ride', 'valk')])
    longs = np.array([e[0] for e in N if e[4] in ('ride', 'valk') and e[1] >= 0.5 * RB * 1.5])
    desc = [e[0] for e in N if e[4] == 'descent' and e[2] >= note('B4')]
    trill = np.array([e[0] for e in N if e[4] == 'trill' and e[2] >= note('B4')])
    cries = [np.array([e[0] for e in N if e[4] in ('cry', 'name') and e[5] == k]) for k in range(8)]
    names = np.array([e[0] for e in N if e[4] == 'name'])
    far = np.array([e[0] for e in N if e[4] == 'far'])
    tw = Flicker(rng, G.N, 3.0, 9.0)
    sp = rng.random(G.N)

    def blob(p, w):
        return np.exp(-((d - p) / w) ** 2)

    def last(arr, t, tau, span=2.0):
        i = int(np.searchsorted(arr, t, side='right')) - 1
        return float(np.exp(-(t - arr[i]) / tau)) if i >= 0 and t - arr[i] < span else 0.0

    def bolt(age, a, b, k):
        """A fork of lightning from a to b: grows in 60 ms, flickers three times, gone in a second."""
        if not 0 <= age < 1.0:
            return np.zeros(G.N)
        reach = a + (b - a) * min(1.0, age / 0.06)
        lo, hi = min(a, reach), max(a, reach)
        fl = sum(np.exp(-((age - s) / 0.04) ** 2) for s in (0.0, 0.12, 0.3)) + 0.45 * np.exp(-age / 0.3)
        return ((d >= lo) & (d <= hi)) * jag[k % len(jag)] * min(fl, 1.2)

    for f in range(F):
        t = f * DT
        tt = t + CLOCK
        fr = rock_bed(d, tt, porch, stone)
        P = C['pos'][:, f]

        # the Ride: gusts through the clouds on its long notes
        g = last(longs, t, 0.35)
        gust = 0.5 + 0.5 * np.cos(2 * np.pi * (d / 520 + 0.9 * tt))
        ridef = 1 - smoothstep(T_SEE - 0.5, T_SEE + 1.0, t)
        fr += light(STORM, 0.55 * g * gust ** 2 * wing * ridef)
        tr = last(trill, t, 0.12, 0.5)
        if tr > 0:
            fr += light(FLASH, 0.6 * tr * (sp > 0.86) * (0.5 + 0.5 * tw(t)) * wing)
        for td in desc:                                                         # the descending chords pour down
            if td <= t < td + 0.9:
                j = desc.index(td) % 9
                fr += light(FLASH * 0.6 + STORM * 0.4, 0.95 * np.exp(-(t - td) / 0.35) * blob(L - (j + 0.5) * L / 9, 200))

        # the rainbow: while they ride spread out, each paints a broad wash of her colour
        bow = smoothstep(T_CAROUSEL, T_CAROUSEL + 2.0, t) * (1 - smoothstep(T_CLIMAX - 0.5, T_CLIMAX + 1.0, t))
        pulse = last(ride, t, 0.25, 0.8)

        # the sisters
        for k in range(8):
            p = P[k]
            fl = last(cries[k], t, 0.18, 1.0)
            back = C['pos'][k][max(f - 4, 0)]
            moving = abs(p - back) > 8
            b = 0.85 + 0.35 * fl + 0.2 * pulse * (1 - ridef * 0 if not moving else 0.5)
            fr += light(COLS[k], b * blob(p, 16 + 5 * fl) + 0.35 * b * blob(p, 75 + 30 * fl))
            fr += light(WHITE, 0.55 * fl * blob(p, 8))
            if bow > 0:
                fr += light(COLS[k], bow * (0.55 + 0.2 * pulse) * blob(p, 170))
            if moving:
                trail = np.zeros(G.N)
                for j, lag in enumerate(range(2, 30, 2)):
                    q = C['pos'][k][max(f - lag, 0)]
                    trail = np.maximum(trail, blob(q, 22) * (1 - j / 14.5))
                fr += light(COLS[k], 0.75 * trail + 0.14 * blob(p, 220) * (1 - bow))
            fr += light(PALE, 0.3 * blob(at(G, *SPOTS[k]) + 15, 6))             # the heroes, laid on the rock
            for tc in cries[k]:
                if tc <= t < tc + 0.9:
                    age = t - tc
                    r = 15 + 340 * age ** 0.7
                    fr += light(COLS[k], 0.75 * (1 - age / 0.9) * np.exp(-((np.abs(d - p) - r) / 26) ** 2))

        # the crossings: a burst of white over the rock each time the two groups pass through each other
        for kx in range(5):
            tx = T_CROSS + 0.34 * 8 + 0.5 + 4.5 * kx
            if tx <= t < tx + 1.0 and tx < T_CAROUSEL:
                age = t - tx
                fr += light(WHITE, 0.6 * np.exp(-age / 0.2) * blob(c, 120))
                fr += light(FLASH, 0.4 * np.exp(-age / 0.4) * porch)
        # the cries thrown across the house: a spark of her colour flying from one sister to another
        for (tt0, a, b) in TOSSES:
            if tt0 <= t < tt0 + 0.6:
                u = (t - tt0) / 0.6
                pa, pb = P[a], C['pos'][b][min(f + int((0.6 - (t - tt0)) / DT), F - 1)]
                q = pa + (pb - pa) * u
                fr += light(COLS[a], 1.0 * blob(q, 14)) + light(WHITE, 0.5 * blob(q, 6))
                prev = pa + (pb - pa) * max(u - 0.15, 0)
                lo_, hi_ = min(prev, q), max(prev, q)
                fr += light(COLS[a], 0.5 * ((d > lo_) & (d < hi_)))
        # the charges meeting over the rock: a flash of the whole house in all their colours
        for tb in BURSTS:
            if tb <= t < tb + 1.6:
                age = t - tb
                fr += light(WHITE, 0.8 * np.exp(-age / 0.1) * blob(c, 300))
                for k in range(8):
                    r = 30 + 1300 * smoothstep(0, 1.4, age) * (0.85 + 0.03 * k)
                    fr += light(COLS[k], 0.7 * (1 - age / 1.6) * np.exp(-((np.abs(d - c) - r) / 70) ** 2))
        if T_GATHER <= t < T_GATHER + 1.5:                                       # home: the rock glows with all of them
            age = t - T_GATHER
            for k in range(8):
                fr += light(COLS[k], 0.6 * np.exp(-age / 0.5) * blob(at(G, *SPOTS[k]), 90))

        # Brünnhilde, seen far off at the free end of Right, riding hard, amber held close beside her
        bp = C['bpos'][f]
        bv = smoothstep(T_SEE + 0.8, T_SEE + 3.5, t) * smoothstep(L + 30, L - 15, bp)
        if bv > 0:
            gal = 0.85 + 0.15 * np.cos(2 * np.pi * tt / (1.5 * RB))
            fb = last(far, t, 0.2, 0.6)
            fr += light(SILVER, bv * gal * (0.55 * blob(bp, 16) + 0.3 * blob(bp, 70)) * (1 + 0.3 * fb))
            fr += light(AMBER, bv * (0.45 * blob(bp + 18, 13) + 0.1125 * blob(bp + 18, 60)))
            for kg in range(2):
                q = bp + 18 * np.sin(2 * np.pi * (0.8 * tt + kg / 2))
                fr += light(GOLD, 0.5 * bv * blob(q, 5))
        ns = last(names, t, 0.3, 1.2)
        if ns > 0:                                                               # every sister's light leans toward her
            for k in range(8):
                fr += light(COLS[k], 0.35 * ns * blob(P[k] + 60, 40))

        # lightning in the clouds
        for i, (ts, where) in enumerate(STRIKES):
            age = t - ts
            if 0 <= age < 1.0:
                if where == 'all':
                    fr += light(WHITE, 0.6 * bolt(age, c, 0.0, i) + 0.6 * bolt(age, c, L, i + 1))
                    continue
                a, b = seg_d[where]
                mid = 0.5 * (a + b)
                fr += light(WHITE, 0.95 * bolt(age, b if i % 2 else a, mid, i))
                fr += light(FLASH, 0.4 * np.exp(-age / 0.2) * blob(mid, 0.7 * (b - a)))
        out[f] = fr
    return np.clip(out, 0, 1)


def score(M, G):
    from pixelhome.audio import SR, whoosh
    order = np.argsort(G.pd)
    xs, ds = G.pos[order, 0], G.pd[order]
    x0, x1 = xs.min(), xs.max()

    def pan_at(dd):
        x = np.interp(dd, ds, xs)
        return float(0.85 * (2 * (x - x0) / (x1 - x0) - 1))

    C = choreography(G)

    def pan_of(k, t):
        return pan_at(np.interp(t, C['t'], C['pos'][k]))

    def spread(t):
        """The centre of the eight, for the orchestra's sound."""
        return pan_at(float(np.mean([np.interp(t, C['t'], C['pos'][k]) for k in range(8)])))

    for name, gain, rev in (('brass', 0.12, 0.28), ('low', 0.12, 0.18), ('strings', 0.11, 0.3), ('winds', 0.09, 0.3),
                            ('cries', 0.13, 0.35), ('perc', 0.13, 0.25), ('fx', 0.06, 0.3)):
        M.bus(name, gain=gain, reverb=rev)
    horn = M.sampler('Brass/F Horn/sus/*.wav', tune=-12)
    tpt = M.sampler('Brass/Trumpet/sus/*.wav', tune=-12)
    tbn = M.sampler('Brass/Tenor Trombone/sus/*.wav', tune=-12)
    tuba = M.sampler('Brass/Tuba/sus/*.wav', tune=-12)
    vn = M.sampler('Strings/Violin Section/susVib/*.wav', tune=-12)
    vns = M.sampler('Strings/Violin Section/Spic/*.wav', tune=-12)
    vtrem = M.sampler('Strings/Violin Section/Trem/*.wav', tune=-12)
    vcs = M.sampler('Strings/Cello Section/spic/*.wav', tune=-12)
    trem = M.sampler('Strings/Cello Section/trem/*.wav', tune=-12)
    cbs = M.sampler('Strings/Solo Contrabass/Spic/*.wav', tune=-12)
    pic = M.sampler('Woodwinds/Piccolo/Stac/*.wav', tune=-12)
    cl = M.sampler('Woodwinds/Clarinet/stac/*.wav', tune=-12)
    bsn = M.sampler('Woodwinds/Bassoon/stac/*.wav', tune=-12)
    timp = M.hits('Percussion/Timpani/Timpani1_Hit*.wav')
    roll = M.hits('Percussion/Timpani/Rolls/*.wav')
    bd = M.hits('Percussion/BDrumNewhit_v[4-7]*.wav')
    crash = M.hits('Percussion/cymbal-crash1_f*.wav')
    gong = M.hits('Percussion/gongHit_f*.wav')
    snare = M.hits('Percussion/Snare2-taps_v[1-3]*.wav')

    def hold(bus, s, m, t0, t1, vel, pan=0.0, step=2.5, rise=0.8, fall=1.0, gain=1.0):
        a0 = s.play(m, vel)
        step = min(step, (a0.shape[1] / SR - 0.35) / 2)
        w = int(2 * step * SR)
        win = np.hanning(w)
        t = t0 - step
        while t < t1 + fall:
            a = s.play(m, vel)[:, int(0.25 * SR):int(0.25 * SR) + w]
            a = a * win[:a.shape[1]]
            tt = t + np.arange(a.shape[1]) / SR
            e = np.clip((tt - t0) / rise, 0, 1) * np.clip(1 - (tt - t1) / fall, 0, 1)
            M.add(bus, a * e, t, gain, pan)
            t += step

    seg_mid = {s: float(G.pd[G.seg[s]].mean()) for s in G.seg}
    rock = pan_at(at(G, 'Porch Front', 0.5))
    right = pan_at(G.length)
    for t, d, m, v, part, who in compose():
        if part == 'roll':
            M.add('perc', roll.play(v, dur=d + 0.3), t, 0.7, rock)
        elif part == 'trill':
            hi = m >= note('B4')
            M.add('winds', (pic if hi else cl).play(m if hi else m + 12, v), t, 0.7 if hi else 0.5, -0.4 if hi else 0.4)
            if hi:
                M.add('strings', vns.play(m - 12, v - 10), t, 0.4, 0.3)
        elif part == 'ride':
            sp = spread(t)
            M.add('brass', horn.play(m, v, dur=d, release=0.15), t, 0.85, sp)
            M.add('brass', horn.play(m, v - 8, dur=d, release=0.15), t, 0.5, -sp)
            M.add('brass', tpt.play(m + 12, v - 18, dur=d, release=0.15), t, 0.35, sp * 0.6)
            M.add('brass', tbn.play(m - 12, v - 6, dur=d, release=0.15), t, 0.6, 0.0)
            M.add('low', tuba.play(m - 24, v - 10, dur=d, release=0.15), t, 0.5, 0.0)
        elif part == 'gallop':
            M.add('low', cbs.play(m + 12, v), t, 0.7, -0.25)
            M.add('low', vcs.play(m + 12, v - 6), t, 0.6, 0.25)
            M.add('low', bsn.play(m + 12, v - 12), t, 0.4, 0.0)
        elif part == 'timp':
            M.add('perc', timp.play(v, pitch=-4), t, 0.6, rock)
        elif part == 'descent':
            if m >= note('B4'):
                M.add('strings', vn.play(m - 12, v, dur=d, release=0.2), t, 0.5, 0.2)
                M.add('brass', tpt.play(m - 12, v - 20, dur=d, release=0.2), t, 0.35, -0.2)
            elif m >= note('A3'):
                M.add('brass', horn.play(m, v - 6, dur=d, release=0.2), t, 0.6, 0.0)
            else:
                M.add('brass', tbn.play(m, v - 6, dur=d, release=0.3), t, 0.7, 0.0)
                M.add('low', tuba.play(m - 12, v - 12, dur=d, release=0.3), t, 0.5, 0.0)
        elif part == 'valk':
            sp = spread(t)
            if m >= note('Eb5'):
                M.add('brass', tpt.play(m - 12, v - 8, dur=d, release=0.2), t, 0.6, sp)
                M.add('strings', vn.play(m - 12, v - 10, dur=d, release=0.2), t, 0.5, -sp)
            elif m >= note('Eb4'):
                M.add('brass', horn.play(m - 12 if m >= note('A4') else m, v, dur=d, release=0.2), t, 0.8, sp)
            else:
                M.add('brass', tbn.play(m, v, dur=d, release=0.2), t, 0.7, 0.0)
                M.add('low', tuba.play(m - 12, v - 10, dur=d, release=0.2), t, 0.5, 0.0)
        elif part == 'drive':
            M.add('low', vcs.play(m + 12, v), t, 0.55, -0.2)
            M.add('low', cbs.play(m + 12, v - 6), t, 0.45, 0.2)
        elif part == 'crash':
            M.add('perc', crash.play(v), t, 0.7, rock)
            M.add('perc', timp.play(v, pitch=-4), t, 0.7, rock)
        elif part == 'cry':
            pa = pan_of(who, t)
            M.add('cries', tpt.play(m, v, dur=d, release=0.2), t, 0.9, pa)
            M.add('cries', horn.play(m, v - 14, dur=d, release=0.2), t, 0.5, pa)
        elif part == 'surge':
            M.add('perc', roll.play(v, dur=d), t, 0.8, rock)
            M.add('fx', whoosh(d, 300, 4000, 0.6, seed=int(t * 10)), t, 0.8, 0.0)
        elif part == 'burst':
            M.add('perc', gong.play(v), t, 0.8, rock)
            M.add('perc', crash.play(v), t, 0.9, rock)
            M.add('perc', bd.play(v), t, 0.9, rock)
        elif part == 'cadence':
            s = tuba if m < note('F#2') else (tbn if m < note('D3') else horn)
            hold('brass', s, m + (12 if s is tuba else 0), t, t + d, v, 0.0, rise=0.05, fall=1.2, gain=0.55)
            if m >= note('B2'):
                hold('strings', vtrem, m + 12, t, t + d, v - 10, 0.0, rise=0.05, fall=1.2, gain=0.3)
        elif part == 'sight':
            hold('strings', vtrem, m + 12, t, t + d, v, right * 0.5, rise=1.5, fall=1.0, gain=0.45)
            hold('low', trem, m, t, t + d, v, 0.0, rise=1.5, fall=1.0, gain=0.4)
        elif part == 'name':
            pa = pan_of(who, t)
            M.add('cries', horn.play(m, v, dur=d, release=0.25), t, 0.9, pa)
            M.add('cries', tpt.play(m, v - 20, dur=d, release=0.25), t, 0.4, pa)
        elif part == 'far':
            M.add('cries', tpt.play(m, v, dur=d, release=0.2), t, 0.55, right)
        elif part == 'hoof':
            M.add('perc', snare.play(v), t, 0.5, right)
        elif part == 'thunder':
            pt = rock if where_all(who) else pan_at(seg_mid[who])
            M.add('perc', bd.play(v), t, 0.6, pt)
            M.add('perc', roll.play(v - 40, dur=d), t + 0.1, 0.4, pt)
            M.add('fx', whoosh(1.0, 2500, 200, 0.5, seed=int(t * 10) + 3), t, 0.5, pt)


def where_all(w):
    return w == 'all'
