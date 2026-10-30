"""The Eight Sisters: all eight Valkyries together on their rock, and the Ride at full strength, every one of
them crying "Hojotoho!" and "Heiaha!".

They leave the rock in a column, Gerhilde at its head, and gallop the length of the house: out to the free end
of Right, wheeling there and thundering back past the rock to the far end of Side, a train of eight colours
each trailing a comet, every word of their war cry a flash and a ring of her colour. Then Helmwige and Ortlinde
cry "Hojotoho!" and the others answer "Heiaha!": the warm sisters (red, orange, yellow, pink) and the cool
(green, sky, violet, purple) sweep across each other over the rock, every crossing a burst of white, their cries
thrown the length of the house as sparks of their colour. The orchestra's great chords: the eight spread out
evenly and ride in a rainbow that sweeps the entire house end to end. Then the sisters' laughter pours down from
on high, and they wheel and whirl over the house; at every peal of laughter the laughing pair charges in from
both ends to meet over the rock in a flash, until Grimgerde and Rossweisse ride in to "Willkommen!" and the
whole house bursts in all their colours, twice. They gather on the rock in their places. Then Siegrune sees
her: "Hieher! Hieher! In brünstigem Ritt jagt Brünnhilde her!" Far off at the free end of Right a silver light
with gold glints is riding hard toward them, an amber light held close beside her, and every sister leans
toward her and calls, "Brünnhilde, hei!"

The music is Wagner's own: Act III, scene 1, bars 140 to 161 (the sisters' Hojotoho and Heiaha over the Ride, and
the orchestra's great chords), 170 to 184 (their laughter and "Willkommen!") and 208 to 215 ("Hieher! Hieher!",
Brünnhilde sighted), spliced, as Solti's 1958 Vienna Philharmonic recording takes them. The notes come from the
Wagner Ring Dataset's piano reduction of the score (pixelhome/ring.py): the Ride's long notes in horns, trumpets and
trombones, its whirling figures in strings and woodwinds, the bass in cellos, basses and tuba, with timpani on the
accents and cymbals on the great moments. The sisters' cries come from the dataset's sung lines: who sings, and
when. Over the score, as a staging would: storm wind, the herd's hoofbeats under every gallop, thunder with every
strike, a rush of air at every crossing and every thrown cry, a boom where each charge meets over the rock and as
they come home, and Brünnhilde's horse coming hard from afar. The herd leads the opening gallop; the effects back
off under the cries and further for the great chords, come up for the laughing charges, lead the Willkommen bursts,
and recede until Brünnhilde's horse is heard.

compose() tags every note of the excerpt and every sung word, choreography() every position; render() and
score() read both."""
import numpy as np
from pixelhome.fx import DT, hexc, light, smoothstep, nframes, Flicker
from pixelhome.ring import Orchestra, excerpt

CODE = 'WK21'
TITLE = 'The Eight Sisters'
KIND = 'show'
DESCRIPTION = ('All eight Valkyries together at last, galloping across the whole house in formation, crossing and '
               'calling to each other over the storm. Then they gather on their rock and see their sister '
               'Brünnhilde riding toward them, carrying a woman.')
VOICEOVER = ('Eight sisters, eight colours, and one of the most famous pieces of music ever written. '
             'This is the Ride at full gallop.')

EX = excerpt(__file__)                      # Act III, bars 140-161 + 170-184 + 208-215, Solti 1958
BAR = {int(m): t for m, t in EX['bars']}
D = EX['seconds']
RB = 0.3                                    # about a quarter note of the Ride
T_COL = 0.0                                 # the column
T_CROSS = BAR[148]                          # Hojotoho and Heiaha: the crossing
T_CAROUSEL = BAR[154]                       # the great chords: the rainbow
T_CLIMAX = BAR[170]                         # the laughter: they whirl
T_CHARGE = BAR[175]                         # each peal of laughter a charge
BURSTS = [BAR[181], BAR[182]]               # "Willkommen!": the whole house bursts
T_GATHER = BAR[184]                         # home on the rock
T_SEE = BAR[208]                            # "Hieher! Hieher!": they see her coming
CLOCK = 80.0 * 20

NAMES = ['Gerhilde', 'Ortlinde', 'Waltraute', 'Schwertleite', 'Helmwige', 'Siegrune', 'Grimgerde', 'Rossweisse']
COLS = [hexc(h) for h in ('#ff4040', '#ff9a20', '#f0e040', '#40e070', '#40d0ff', '#6060ff', '#c050ff', '#ff60c0')]
SPOTS = [('Porch Left', 0.25), ('Porch Left', 0.65), ('Porch Front', 0.12), ('Porch Front', 0.37),
         ('Porch Front', 0.63), ('Porch Front', 0.88), ('Porch Right', 0.35), ('Porch Right', 0.75)]
WARM, COOL = [0, 1, 2, 7], [3, 4, 5, 6]
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


def who(names):
    """Sister indices named in a sung line's 'person' field."""
    return [k for k, n in enumerate(NAMES) if n in names]


def words():
    """Every sung word, spread evenly over its line: (time, sister) for each of its singers."""
    out = []
    for t0, t1, person, text in EX['singing']:
        ws = text.split()
        for i in range(len(ws)):
            for k in who(person):
                out.append((t0 + i * (t1 - t0) / len(ws), k))
    return sorted(out)


def accents(t0, t1, vmin, n, space):
    """Times in [t0, t1) where n or more notes louder than vmin strike together, at least `space` apart."""
    c = {}
    for t, d, m, v, h in EX['notes']:
        if t0 <= t < t1 and v >= vmin:
            c[round(t, 2)] = c.get(round(t, 2), 0) + 1
    out = []
    for k in sorted(k for k, v in c.items() if v >= n):
        if not out or k - out[-1] >= space:
            out.append(k)
    return out


def tosses():
    """Cries thrown across the house in the crossing: from each Hojotoho singer to an answering Heiaha singer."""
    ws = [(t, k) for t, k in words() if T_CROSS <= t < T_CAROUSEL]
    out, j = [], 0
    for t, k in ws:
        if k in (4, 1) and (not out or t - out[-1][0] > 0.9):          # Helmwige and Ortlinde cry Hojotoho
            to = (0, 2, 5, 3)[j % 4]                                    # Gerhilde, Waltraute, Siegrune, Schwertleite
            out.append((t, k, to))
            j += 1
    return out


def compose():
    """Every note of the excerpt, tagged: (time, seconds, midi, velocity, part, hand): 'ride' its long notes, 'trill'
    the short ones, 'desc' the laughter pouring down from on high; and every sung word: 'cry' (or 'name' once they
    have seen Brünnhilde), with the sister as the last field."""
    N = []
    for t, d, m, v, h in EX['notes']:
        if T_CLIMAX <= t < T_CHARGE and h == 0 and m >= 84 and d < 0.3:
            part = 'desc'
        elif d >= 0.3:
            part = 'ride'
        else:
            part = 'trill'
        N.append((t, d, m, v, part, h))
    for t, k in words():
        N.append((t, 0.2, 0, 0, 'name' if t >= T_SEE else 'cry', k))
    return sorted(N, key=lambda e: e[0])


STRIKES = ([(t, ('Side', 'Right', 'Left', 'Right', 'Side', 'Left')[i % 6])
            for i, t in enumerate(accents(T_CROSS, T_GATHER, 113, 5, 4.0)) if min(abs(t - b) for b in BURSTS) > 1.0]
           + [(b, 'all') for b in BURSTS])
TOSSES = tosses()


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
    hts, hds = zip(*[(T_COL, c), (T_COL + 4.0, hi), (T_COL + 4.8, hi - 40), (T_COL + 11.0, lo), (T_COL + 11.8, lo + 40),
                     (T_CROSS, c)])
    for i in range(8):
        lag = 0.34 * i
        head = np.interp(t - lag, hts, hds)
        put(i, T_COL + lag, T_CROSS + lag, head, 12.0)
    # the crossing: warm and cool sweep across each other over the rock, each group a little column
    for g, grp in ((1, WARM), (-1, COOL)):
        for j, k in enumerate(grp):
            x = c + g * 1150 * np.sin(2 * np.pi * (t - T_CROSS - 0.34 * j) / 6.0)
            put(k, T_CROSS + 0.34 * 8, T_CAROUSEL, np.clip(x, lo, hi), 10.0)
    # the carousel: all eight spread evenly, a rainbow sweeping the whole house end to end
    for k in range(8):
        x = lo + (hi - lo) * tri(k / 4.0 + (t - T_CAROUSEL) / 5.2)
        put(k, T_CAROUSEL, T_CLIMAX, x, 3.5)
    # the laughter: they whirl over the whole house
    for k in range(8):
        whirl = c + (500 + 250 * (k % 2)) * np.sin(2 * np.pi * ((t - T_CLIMAX) / 4.0 + k / 8))
        put(k, T_CLIMAX, T_CHARGE, np.clip(whirl, lo, hi), 6.0)
    # each peal of laughter: back to both ends, the laughers charge in to meet over the rock; then Willkommen
    peals = [ln[0] for ln in EX['singing'] if T_CHARGE - 0.1 <= ln[0] < BURSTS[0] - 1.0] + [BURSTS[0] - 1.0]
    for k in range(8):
        side = -1 if k < 4 else 1
        end = (lo + 35 * k) if side < 0 else (hi - 35 * (7 - k))
        meet = c + side * (12 + 14 * (k % 4))
        marks = [(T_CHARGE, end)]
        for a, b in zip(peals[:-1], peals[1:]):
            marks += [(a + 0.2, end), (a + 0.2 + 0.6 * (b - a), meet), (b, end)]
        marks += [(BURSTS[0] - 0.9, end), (BURSTS[0], meet), (BURSTS[0] + 0.9, end), (BURSTS[1], meet)]
        ts, ds = zip(*marks)
        put(k, T_CHARGE, BURSTS[1], np.interp(t, ts, ds), 9.0)
        whirl = c + 300 * np.sin(2 * np.pi * ((t - BURSTS[1]) / 2.5 + k / 8))
        put(k, BURSTS[1], T_GATHER, whirl, 7.0)
        put(k, T_GATHER, D, home[k], 6.0)
    pos = np.array([follow(tgt[k], rate[k]) for k in range(8)])
    lift = smoothstep(0.0, 1.0, t) * (1 - smoothstep(T_GATHER, T_GATHER + 2.6, t))
    pos = home + (pos - home) * lift                      # exact in their places at both ends
    bpos = at(G, 'Right', 1.0) + 40 - 330 * smoothstep(T_SEE + 1.0, D, t) ** 0.8
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
    ride = np.array(sorted({e[0] for e in N if e[4] == 'ride'}))
    longs = np.array(sorted({e[0] for e in N if e[4] == 'ride' and e[1] >= 0.5}))
    desc = []
    for e in N:
        if e[4] == 'desc' and (not desc or e[0] - desc[-1] > 0.25):
            desc.append(e[0])
    trill = np.array(sorted({e[0] for e in N if e[4] == 'trill' and e[2] >= 71}))
    cries = [np.array([e[0] for e in N if e[4] in ('cry', 'name') and e[5] == k]) for k in range(8)]
    names = np.array([e[0] for e in N if e[4] == 'name'])
    far = np.array(accents(T_SEE, D, 90, 3, 0.4))
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
        ridef = 1.0
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
            tx = T_CROSS + 0.34 * 8 + 0.5 + 3.0 * kx
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
    """Wagner's notes: the Ride's long notes on horns, trumpets and trombones, its whirling figures on strings and
    woodwinds, the bass on cellos, basses and tuba; timpani on the accents, cymbals on the great moments."""
    o = Orchestra(M, level=1.5)

    def role(t, d, m, v, hand):
        if hand == 0 and d >= 0.3 and 62 <= m < 86:              # the theme's long notes up top: brass with the violins
            return [('violins', 0, -6, 0.5), ('trumpets', 0, -10, 0.45), ('horns', -12, -4, 0.55)]
        return None

    o.tutti(EX['notes'], role=role)
    o.effects([(0.0, -2), (T_CROSS - 0.5, -2), (T_CROSS + 0.5, -6), (T_CAROUSEL - 0.5, -6), (T_CAROUSEL + 0.5, -10),
               (T_CLIMAX - 0.5, -10), (T_CLIMAX + 0.5, -4), (BURSTS[0] - 0.5, 0), (BURSTS[1] + 1.0, 0),
               (T_GATHER + 1.0, -7), (T_SEE, -7), (T_SEE + 2.0, -3), (D, -2)])
    for t in accents(0.0, D, 105, 4, 0.9):
        o.hit('timpani', t, 110, pitch=-4, gain=0.45)
    for t in [T_CROSS, T_CAROUSEL, T_CLIMAX, T_GATHER, T_SEE] + BURSTS:
        o.hit('crash', t, 115, gain=0.5)
    for t in BURSTS:
        o.hit('bass drum', t, 120, gain=0.6)
        o.hit('gong', t, 110, gain=0.4)
    # the staging: storm wind, the herd's hoofbeats under every gallop, thunder with every strike, a rush of air
    # for every crossing and thrown cry, a boom where the charges meet, Brünnhilde's horse coming from afar
    from pixelhome.audio import whoosh
    order = np.argsort(G.pd)
    xs, ds = G.pos[order, 0], G.pd[order]
    pan_at = lambda dd: float(0.85 * (2 * (np.interp(dd, ds, xs) - xs.min()) / (xs.max() - xs.min()) - 1))
    C = choreography(G)
    c = at(G, 'Porch Front', 0.5)
    pk = lambda k: (lambda t: pan_at(np.interp(t, C['t'], C['pos'][k])))
    WH = {'Right': 0.8, 'Left': -0.7, 'Side': -0.9, 'all': 0.0}
    o.wind(0.0, D, level=lambda tt: 0.6 - 0.25 * smoothstep(T_GATHER, T_GATHER + 3, tt), pan=0.0)
    for k, v in ((0, 104), (7, 96), (4, 98)):                    # the herd: the head, the tail, and one between
        o.gallop(0.0, T_GATHER + 1.0, beat=1.5 * RB, pan=pk(k), v=v, gain=0.55)
    for ts, where in STRIKES:
        o.thunder(ts, near=1.0 if where == 'all' else 0.75, pan=WH[where], gain=1.0 if where == 'all' else 0.85)
    pc = pan_at(c)
    for kx in range(5):                                          # the crossings over the rock
        tx = T_CROSS + 0.34 * 8 + 0.5 + 3.0 * kx
        if tx < T_CAROUSEL:
            o.M.add('fx', whoosh(0.8, 600, 5000, 0.8, seed=kx + 1), tx - 0.4, 0.8, pc)
            o.hit('crash', tx, 90, gain=0.3, pan=pc, fx=True)
    for (t0, a, b) in TOSSES:                                    # a cry thrown from one sister to another
        pa, pb = pk(a)(t0), pk(b)(t0 + 0.6)
        o.M.add('fx', whoosh(0.6, 1500, 6000, 0.5, seed=int(t0 * 10)), t0, 0.5, 0.5 * (pa + pb))
    peals = [ln[0] for ln in EX['singing'] if T_CHARGE - 0.1 <= ln[0] < BURSTS[0] - 1.0] + [BURSTS[0] - 1.0]
    for a, b in zip(peals[:-1], peals[1:]):                      # each peal of laughter: the charge, the meeting
        tm = a + 0.2 + 0.6 * (b - a)
        o.M.add('fx', whoosh(tm - a, 300, 3000, 0.7, seed=int(a * 10)), a + 0.2, 0.6, 0.0)
        o.boom(tm, pc, 0.55)
    for t in BURSTS:
        o.boom(t, pc, 0.9)
    o.boom(T_GATHER, pc, 0.5)
    pbr = lambda t: pan_at(np.interp(t, C['t'], C['bpos']))      # Brünnhilde riding hard toward them
    o.gallop(T_SEE + 0.5, D, beat=0.4, pan=pbr, v=112, gain=0.9)
