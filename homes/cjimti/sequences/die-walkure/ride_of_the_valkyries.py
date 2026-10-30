"""Ride of the Valkyries: Act III, the Valkyries' rock. The porch is the rock, still and dark; the wings and
Side are the storm clouds the sisters ride through, slate billowing over navy, lit from inside by lightning.

The music is Wagner's own: the prelude to Act III, bars 5 to 45, as Solti's 1958 Vienna Philharmonic recording
takes it, from the trilling woodwinds and whirling string arpeggios in B minor to the Ride's theme in the horns,
its answer in D major, the middle section and the full return, ending just before Gerhilde's first "Hojotoho!".
The notes come from the Wagner Ring Dataset's piano reduction of the score (pixelhome/ring.py): the left hand's
theme is played by horns, trombones and, as the orchestra grows, trumpets; its bass by cellos, basses and tuba;
the right hand's figuration by violins with piccolo and flutes on top. Over the score, as a staging would: storm
wind in the clouds, thunder with every lightning strike where it falls, a rush of air as each sister tears out of
the clouds, her hoofbeats galloping along the house with her, and a boom and cymbal as she lands on the rock.

The sisters arrive one by one through the storm, each in her own colour, each with a fallen hero slung over her
saddle (a small dim light riding just behind her), one on each phrase of the theme: Gerhilde (red) bursting out of
the clouds on the Left wing, Helmwige (sky blue) galloping in from the free end of Right, Waltraute (yellow) out of
the Left wing's clouds, Schwertleite (green) from the free end, Ortlinde (orange) out of the clouds on the Left,
Siegrune (violet blue) out of the clouds on the Right wing, and last Grimgerde (purple) and Rossweisse (pink) riding
in together from the free end. The long notes of the theme ring out from each as she rides in, and she lands on the
rock with a burst of light; then she wheels there in her place, her hero laid beside her, flaring with every note of
the Ride. By the end all eight ride in a rainbow across the rock. The storm leads the prelude; each phrase of the
theme pulls the effects well back so the Ride is clear, and they surge up between phrases, where each sister lands.

compose() tags every note of the excerpt, choreography() every position; render() and score() read both."""
import numpy as np
from pixelhome.audio import note
from pixelhome.fx import DT, hexc, light, smoothstep, nframes, Flicker
from pixelhome.ring import Orchestra, excerpt

CODE = 'WK20'
TITLE = 'Ride of the Valkyries'
KIND = 'show'
DESCRIPTION = ('The Valkyries, the eight warrior daughters of Wotan, come galloping one by one through the storm '
               'clouds to their mountain rock, each in her own colour, each carrying a fallen hero over her '
               'saddle, to the real Ride of the Valkyries.')
VOICEOVER = ('High on a mountain, above the clouds, Wotan\'s warrior daughters are coming home. '
             'Hold on to something.')

EX = excerpt(__file__)                      # Act III, bars 5-45, Solti 1958
BAR = {int(m): t for m, t in EX['bars']}
PHRASES = [13, 17, 21, 27, 31, 35, 39]      # a sister arrives on each phrase of the theme
RB = 0.44                                   # about a quarter note at this tempo (a 9/8 bar is about 2 s)
LONG = 0.4                                  # a long note of the theme, in seconds
C0 = BAR[PHRASES[0]]                        # the theme's first entry
NCYC = len(PHRASES)
D = 80.0
CLOCK = 80.0 * 19

NAMES = ['Gerhilde', 'Ortlinde', 'Waltraute', 'Schwertleite', 'Helmwige', 'Siegrune', 'Grimgerde', 'Rossweisse']
COLS = [hexc(h) for h in ('#ff4040', '#ff9a20', '#f0e040', '#40e070', '#40d0ff', '#6060ff', '#c050ff', '#ff60c0')]
SPOTS = [('Porch Left', 0.25), ('Porch Left', 0.65), ('Porch Front', 0.12), ('Porch Front', 0.37),
         ('Porch Front', 0.63), ('Porch Front', 0.88), ('Porch Right', 0.35), ('Porch Right', 0.75)]
# who arrives on each phrase, and how: out of the clouds at a point on a front run, or in from the free end of Right
ARRIVALS = [([0], ('Left', 0.45)), ([4], 'end'), ([2], ('Left', 0.7)), ([3], 'end'), ([1], ('Left', 0.25)),
            ([5], ('Right', 0.55)), ([6, 7], 'end')]
STRIKES = [(1.6, 'Right'), (8.6, 'Side'), (17.0, 'Right'), (27.4, 'Left'), (38.2, 'Side'), (49.6, 'Right'),
           (60.2, 'Left'), (70.4, 'Side'), (76.8, 'Right')]
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


def cyc(c):
    """Phrase c: when it starts, when its sister appears, and when she lands."""
    t0 = BAR[PHRASES[c]]
    t1 = BAR[PHRASES[c + 1]] if c + 1 < NCYC else EX['seconds']
    return t0, t0 + 0.3 * (t1 - t0), t0 + 0.75 * (t1 - t0)


def compose():
    """Every note of the excerpt, tagged: (time, seconds, midi, velocity, part, who). The left hand from F#3 up is
    the Ride's theme ('ride', who = the phrase), below it the bass ('bass'); the right hand is the strings'
    figuration ('trill'), and the first note of each bar of the middle section pours down ('descent').
    'cry', 'land' and 'burst' mark a sister's moments for the lights; they make no sound."""
    N = []
    starts = {round(t, 3) for m, t in EX['bars'] if PHRASES[3] <= m < PHRASES[6]}
    for t, d, m, v, h in EX['notes']:
        ph = max([c for c in range(NCYC) if t >= cyc(c)[0] - 0.05], default=-1)
        if h == 1:
            N.append((t, d, m, v, 'ride' if m >= note('F#3') else 'bass', ph))
        else:
            N.append((t, d, m, v, 'descent' if round(t, 3) in starts and m >= note('B4') else 'trill', ph))
    longs = [e for e in N if e[4] == 'ride' and e[1] >= LONG]
    for c in range(NCYC):
        t0, ta, tl = cyc(c)
        who, how = ARRIVALS[c]
        for j, k in enumerate(who):
            for e in longs:
                if ta <= e[0] < tl + 1.0:
                    N.append((e[0] + 0.15 * j, 0.3, e[2], 0, 'cry', k))
            N.append((tl, 0.5, note('B1'), 0, 'land', k))
        if how != 'end':
            N.append((ta - 0.4, 0.8, note('B2'), 0, 'burst', who[0]))
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
    """Where a sister wheels on the rock, in her place (shared with the next scenes)."""
    return at(G, *SPOTS[k]) + 9 * np.sin(2 * np.pi * (0.31 * tt + k / 8)) + 4 * np.sin(2 * np.pi * (0.73 * tt + k / 3))


def choreography(G):
    """Per frame: each sister's position (path distance; off the house before she comes), and how far in she is."""
    F = nframes(D)
    t = np.arange(F) * DT
    L = G.length
    pos = np.full((8, F), L + 400.0)
    seen = np.zeros((8, F))
    land = np.full(8, np.inf)
    for c, (who, how) in enumerate(ARRIVALS):
        t0, ta, tl = cyc(c)
        for j, k in enumerate(who):
            spot = at(G, *SPOTS[k])
            if how == 'end':                    # in from the free end, sweeping past her place and wheeling back
                marks = [(0.0, L + 60 + 70 * j), (ta, L + 60 + 70 * j), (tl - 0.1, spot - 170 - 40 * j), (tl + 0.9, spot)]
            else:                               # out of the clouds, away along the wing, then back across to the rock
                start = at(G, *how)
                turn = at(G, how[0], 0.04 if how[0] == 'Left' else 0.96)
                over = spot + (170 if how[0] == 'Left' else -170)
                marks = [(0.0, start), (ta, start), (ta + 1.2, turn), (tl - 0.1, over), (tl + 0.9, spot)]
            ts, ds = zip(*marks)
            path = follow(np.interp(t, ts, ds), np.full(F, 7.0))
            rest = sway(G, k, t + CLOCK)
            blend = smoothstep(tl + 0.3, tl + 2.2, t)
            pos[k] = np.where(t < ta - 0.6, L + 400.0, path * (1 - blend) + rest * blend)
            if how == 'end':
                seen[k] = smoothstep(ta - 0.2, ta + 0.3, t)
            else:
                seen[k] = smoothstep(ta - 0.15, ta + 0.1, t)
            land[k] = tl
    return dict(t=t, pos=pos, seen=seen, land=land)


def rock_bed(d, tt, porch, stone):
    """Act III: storm clouds billowing over the wings and Side, the still, dark rock on the porch (shared by WK19-WK24)."""
    c1 = 0.5 + 0.5 * np.cos(2 * np.pi * (d / 430 - 0.03 * tt))
    c2 = 0.5 + 0.5 * np.cos(2 * np.pi * (d / 160 + 0.055 * tt) + 1)
    billow = 0.6 * c1 + 0.4 * c1 * c2
    wing = 1 - porch
    return (light(CLOUD, (0.38 + 0.62 * billow ** 1.5) * wing) + light(STORM, 0.6 * billow ** 3 * wing)
            + light(NAVY, 0.4 * wing) + light(ROCK, 0.6 * stone * porch) + light(NAVY, 0.4 * porch))


def render(G, seed=20):
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
    ride = np.array([e[0] for e in N if e[4] == 'ride'])
    longs = np.array([e[0] for e in N if e[4] == 'ride' and e[1] >= LONG])
    desc = [e[0] for e in N if e[4] == 'descent' and e[2] >= note('B4')]
    trill = np.array([e[0] for e in N if e[4] == 'trill' and e[2] >= note('B4')])
    cries = [np.array([e[0] for e in N if e[4] == 'cry' and e[5] == k]) for k in range(8)]
    bursts = [(e[0] + 0.4, e[5]) for e in N if e[4] == 'burst']
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

        # the Ride: every long note a gust of light through the clouds, rolling the way the riders go
        g = last(longs, t, 0.35)
        gust = 0.5 + 0.5 * np.cos(2 * np.pi * (d / 520 + 0.9 * tt))
        fr += light(STORM, 0.55 * g * gust ** 2 * wing)
        on = smoothstep(C0 - 0.5, C0 + 2, t)
        fr += light(FLASH, 0.12 * on * last(ride, t, 0.12) * gust ** 4 * wing)

        # the trilling cries: glitter flickering over the clouds
        tr = last(trill, t, 0.12, 0.5)
        if tr > 0:
            fr += light(FLASH, 0.6 * tr * (sp > 0.86) * (0.5 + 0.5 * tw(t)) * wing)

        # the descending chords: bands of light pouring down the house from the free end of Right to Side
        for i, td in enumerate(desc):
            if td <= t < td + 0.9:
                age = t - td
                j = desc.index(td) % 9
                q = L - (j + 0.5) * L / 9
                fr += light(FLASH * 0.6 + STORM * 0.4, 0.95 * np.exp(-age / 0.35) * blob(q, 200))

        # bursts out of the clouds: the cloud bulges bright, tears open, and she is through
        for tb, k in bursts:
            age = t - tb
            p0 = C['pos'][k][min(int((tb + 0.3) / DT), F - 1)]
            if -0.5 <= age < 0:
                fr += light(STORM * 0.6 + FLASH * 0.4, 0.8 * (1 + age / 0.5) * blob(p0, 60))
            elif 0 <= age < 1.0:
                r = 20 + 300 * age ** 0.6
                fr += light(COLS[k], 0.9 * (1 - age) * np.exp(-((np.abs(d - p0) - r) / 30) ** 2))
                fr += light(WHITE, 0.9 * np.exp(-age / 0.1) * blob(p0, 30))

        # the sisters, each in her colour with a fallen hero over her saddle; a comet behind her while she rides
        for k in range(8):
            s = C['seen'][k][f]
            if s <= 0:
                continue
            p = C['pos'][k][f]
            vis = s * smoothstep(L + 40, L - 20, p)
            landed = t >= C['land'][k] + 1.0
            fl = last(cries[k], t, 0.18, 1.0)
            pulse = last(ride, t, 0.2, 0.6) * landed
            gal = 0.88 + 0.12 * np.cos(2 * np.pi * t / (1.5 * RB))
            b = vis * (0.85 + 0.35 * fl + 0.15 * pulse) * (gal if not landed else 1.0)
            fr += light(COLS[k], b * blob(p, 16 + 5 * fl) + 0.35 * b * blob(p, 75 + 30 * fl))
            fr += light(WHITE, 0.55 * vis * fl * blob(p, 8))
            back = C['pos'][k][max(f - 4, 0)]
            dirn = np.sign(back - p) if abs(back - p) > 1 else 1.0
            if abs(p - back) > 8:
                trail = np.zeros(G.N)
                for j, lag in enumerate(range(2, 30, 2)):
                    q = C['pos'][k][max(f - lag, 0)]
                    trail = np.maximum(trail, blob(q, 22) * (1 - j / 14.5))
                fr += light(COLS[k], 0.8 * vis * trail + 0.3 * vis * blob(p, 220))      # lighting up the clouds
                fr += light(PALE, 0.45 * vis * blob(p + 22 * dirn, 6))           # the hero, slung behind her
            else:
                fr += light(PALE, 0.3 * vis * blob(at(G, *SPOTS[k]) + 15, 6))   # laid on the rock beside her
            for tc in cries[k]:                                                 # every cry a ring flying out from her
                if tc <= t < tc + 0.9:
                    age = t - tc
                    r = 15 + 340 * age ** 0.7
                    fr += light(COLS[k], 0.75 * (1 - age / 0.9) * np.exp(-((np.abs(d - p) - r) / 26) ** 2))
            tl = C['land'][k]
            if tl <= t < tl + 1.2:                                              # landing on the rock
                age = t - tl
                fr += light(COLS[k], 0.8 * np.exp(-age / 0.35) * porch * blob(p, 260))
                fr += light(COLS[k], 0.55 * np.exp(-age / 0.5) * wing * (0.6 + 0.4 * gust))
                fr += light(WHITE, 0.6 * np.exp(-age / 0.12) * blob(p, 25))

        # lightning in the clouds
        for i, (ts, where) in enumerate(STRIKES):
            age = t - ts
            if 0 <= age < 1.0:
                a, b = seg_d[where]
                mid = 0.5 * (a + b)
                fr += light(WHITE, 0.95 * bolt(age, b if i % 2 else a, mid, i))
                fr += light(FLASH, 0.4 * np.exp(-age / 0.2) * blob(mid, 0.7 * (b - a)))
        out[f] = fr
    return np.clip(out, 0, 1)


def score(M, G):
    """Wagner's notes, orchestrated from the piano reduction by hand and register, louder as the orchestra grows."""
    o = Orchestra(M, level=0.9)
    for t, d, m, v, part, ph in compose():
        grow = max(ph, 0)
        if part == 'ride':                                  # the theme: horns, then trombones, then trumpets
            sp = -0.35 + 0.7 * ((t / 3.6) % 1)
            o.play('horns', m, t, d, v, sp, 0.85)
            o.play('horns', m, t, d, v - 8, -sp, 0.5)
            if grow >= 2:
                o.play('trombones', m, t, d, v - 6, 0.0, 0.6)
            if grow >= 4:
                o.play('trumpets', m + 12, t, d, v - 16, sp * 0.6, 0.35)
        elif part == 'bass':                                # the bass: cellos and basses, tuba under the long notes
            o.play('cellos', m, t, d if d > 0.5 else 0.1, v, -0.2, 0.7)
            if d > 0.5 and grow >= 3:
                o.play('tuba', m, t, d, v - 10, 0.0, 0.45)
            o.play('basses', m - 12 if m >= note('E2') else m, t, 0.1, v - 6, 0.2, 0.55)
        elif part in ('trill', 'descent'):                  # the figuration: violins, piccolo and flutes on top
            o.play('violins', m, t, d, v - 8, 0.3, 0.5 if d < 0.25 else 0.55)
            if d >= 0.25:
                o.play('violas', m - 12, t, d, v - 16, -0.3, 0.3)
            if m >= note('F#5'):
                o.play('piccolo' if m >= note('B5') else 'flutes', m, t, 0.1, v - 14, -0.4, 0.4)
            if part == 'descent':
                o.hit('timpani', t, v - 20, pitch=-4, gain=0.4)
    for c in (3, 6):                                        # the cymbal clashes at the climaxes
        o.hit('crash', cyc(c)[0], 100)
    # the staging: storm wind in the clouds, thunder with every strike, hoofbeats under every sister, a boom as
    # each lands on the rock
    from pixelhome.audio import whoosh
    order = np.argsort(G.pd)
    xs, ds = G.pos[order, 0], G.pd[order]
    pan_at = lambda dd: float(0.85 * (2 * (np.interp(min(dd, G.length), ds, xs) - xs.min()) / (xs.max() - xs.min()) - 1))
    C = choreography(G)
    WH = {'Right': 0.8, 'Left': -0.7, 'Side': -0.9}
    pts = [(0.0, 0), (C0 - 0.6, 0)]                        # back under each phrase, up where each sister lands
    for c in range(NCYC):
        t0, ta, tl = cyc(c)
        pts += [(t0 - 0.3, -2), (t0 + 0.2, -10), (tl - 0.7, -10), (tl - 0.1, -3), (tl + 1.0, -3)]
    o.effects(pts + [(D, -4)])
    o.wind(0.0, D, level=lambda tt: 0.55 + 0.45 * smoothstep(0, C0, tt), pan=0.0)
    for i, (ts, where) in enumerate(STRIKES):
        o.thunder(ts, near=0.8 if i % 3 else 0.55, pan=WH[where], gain=0.9)
    how = {who[0]: h for who, h in ARRIVALS}
    for t, d, m, v, part, k in compose():
        if part == 'burst':                                 # the cloud tears open and she is through
            p = 0.85 if how[k] == 'end' else pan_at(at(G, *how[k]))
            o.M.add('fx', whoosh(0.9, 300, 4000, 0.8, seed=int(t * 10)), t + 0.2, 0.8, p)
    for k in range(8):
        tl = C['land'][k]
        if not np.isfinite(tl):
            continue
        ta = C['t'][int(np.argmax(C['seen'][k] > 0))]
        pk = lambda t, k=k: pan_at(np.interp(t, C['t'], C['pos'][k]))
        o.gallop(ta - 0.3, tl + 1.0, beat=1.5 * RB, pan=pk, v=104, gain=0.75)
        o.boom(tl, pk(tl + 0.9), 0.65)
        o.hit('crash', tl, 96, gain=0.35, pan=pk(tl + 0.9), fx=True)
