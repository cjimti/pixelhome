"""Weia! Waga!: the curtain is up on the bed of the Rhine, sunlit green water rocking over the whole roof. The
three Rhinemaidens are lights in it: Woglinde (silver) surfaces on the rock at the back of the porch with a
splash and sings her greeting to the waters ("Weia! Waga! Woge, du Welle"), swimming with it. Wellgunde (sea
green) streaks in from the free end of Right calling to her, and the two of them chase round the rock; Flosshilde
(violet), the eldest, pops up on Left ("Heiaha weia! Wildes Geschwister!") and scolds them for guarding the
sleeping gold so badly. Then the game: they dart from run to run of the house with a splash at every turn, until
all three spin in a whirlpool out over every run. The water darkens at the corner of Left: Alberich, a smouldering
red-brown thing, heaves himself up out of a chasm on the orchestra's slithering accents and calls out to them
("Hehe! Ihr Nicker!"). They freeze, ask each other who is there, and close round the rock, where a glint of the
sleeping gold shows under them.

The music is Wagner's own: bars 137 to 196 of Scene 1, timed bar by bar like Barenboim's 1991 Bayreuth recording.
The orchestra comes from the Wagner Ring Dataset's piano reduction (pixelhome/ring.py): the rocking accompaniment
on strings and harp-like violins, the bass on cellos and basses, Alberich's slithering in the low brass. The
Rhinemaidens' lines are from the printed vocal score (Klindworth, Schott; archive.org dasrheingold00wagn2,
pp. 5-9), each on her own instrument: Woglinde oboe, Wellgunde flute, Flosshilde clarinet. Alberich's line stays
in the orchestra. Splashes sound when a maiden surfaces or darts; his heaves scrape and thud on the rock; the
effects stay under the singing.

Every note is in compose(); choreography() turns it into positions, and render() and score() both read it."""
import numpy as np
from pixelhome.audio import note
from pixelhome.fx import DT, hexc, light, smoothstep, nframes, Flicker
from pixelhome.ring import Orchestra, excerpt, tidy

CODE = 'RG02'
TITLE = 'Weia! Waga!'
KIND = 'show'
DESCRIPTION = ('Three Rhinemaidens, silver, green and violet, sing and chase each other through the sunlit river '
               'over the gold they guard, until something ugly climbs up out of the dark at the corner of the '
               'house.')
VOICEOVER = ('At the bottom of the Rhine, three river daughters play over a treasure they were told to guard. '
             'They are not very good at guarding it.')

EX = excerpt(__file__)                      # Scene 1, bars 137-196, Barenboim 1991
D = EX['seconds']
_BM = [b for b, _ in EX['bars']]
_BT = [t for _, t in EX['bars']]


def bt(pos):
    """The time of a (fractional) bar position."""
    return float(np.interp(pos, _BM, _BT))


BAR = bt(170) - bt(169)                     # a bar of 6/8, about 1.5 s
T_WOG = 0.0                                 # Woglinde surfaces
T_WELL = bt(144.6)                          # Wellgunde streaks in from the end of Right
T_DUET = bt(146.8)                          # and they chase round the rock
T_FLO = bt(151.7)                           # Flosshilde pops up on Left, scolding
T_GAME = bt(166)                            # the game: two bars each
T_WHIRL = bt(178)                           # all three, spinning
T_LAUGH = bt(182)                           # the whirlpool collapses as the water darkens
T_ALB = bt(181.4)                           # the water darkens at the corner of Left
CLIMB = [x - 0.47 for x in (bt(182), bt(183), bt(183) + 0.59, bt(184))]     # his heaves, on the accents
T_HEHE = bt(184.917)                        # "Hehe! Ihr Nicker!"
CALLS = [bt(192), bt(192.417), bt(193)]     # who is there?
T_GUARD = bt(194)                           # they close round the rock
CREEP, LAUGHS = [], []
T_MOCK = D + 10.0

WOG, WELL, FLO = 0, 1, 2
GAME = [(WOG, 0), (WELL, 1), (FLO, 0), (WOG, 1), (WELL, 0), (FLO, 1)]     # (who darts, unused)
GAME_TO = [('Right', 0.5), ('Left', 0.45), ('Porch Right', 0.5), ('Porch Left', 0.5), ('Right', 0.92),
           ('Porch Front', 0.5)]
# The Rhinemaidens' lines, from the vocal score: (bar, start, length in eighths of 6/8, note, who)
LINES = [(137, 0, 2, 'F5'), (137, 2, 1, 'Eb5'), (137, 3, 2, 'C5'), (137, 5, 1, 'Bb4'),
         (138, 0, 1, 'Ab4'), (138, 1, 1, 'Eb4'), (138, 2, 1, 'Ab4'), (138, 3, 2, 'Bb4'), (138, 5, 1, 'Ab4'),
         (139, 0, 1, 'C5'), (139, 1, 1, 'Ab4'), (139, 2, 1, 'C5'), (139, 3, 2, 'Eb5'), (139, 5, 1, 'C5'),
         (140, 0, 1, 'F5'), (140, 1, 1, 'Eb5'), (140, 2, 1, 'C5'), (140, 3, 2, 'Ab5'), (140, 5, 1, 'Eb5'),
         (141, 0, 1.5, 'C5'), (141, 1.5, .5, 'Ab4'), (141, 2, 1, 'Eb4'), (141, 3, 1.5, 'Eb5'), (141, 4.5, .5, 'C5'),
         (141, 5, 1, 'Ab4'), (142, 0, 6, 'F5'), (143, 0, 5, 'Eb5')]
SINGERS = [[x + (WOG,) for x in LINES]]
SINGERS.append([x + (WELL,) for x in [(145, 0, 3, 'F5'), (145, 3, 2, 'C5'), (145, 5, 1, 'Bb4'), (146, 0, 1, 'Ab4'),
                                      (146, 1, 1, 'F4'), (146, 2, 1, 'Ab4'), (146, 3, 2, 'C5'),
                                      (148, 2, 1, 'Bb4'), (148, 3, 2, 'Eb5'), (148, 5, .5, 'Bb4'),
                                      (148, 5.5, .5, 'Bb4'), (149, 0, 2, 'C5'),
                                      (154, 0, 1, 'G5'), (154, 1, 1.5, 'Eb5'), (154, 2.5, .5, 'G4'), (154, 3, 2, 'Bb4'),
                                      (155, 0, 1, 'Eb5'), (155, 1, 1.5, 'Bb4'), (155, 2.5, .5, 'Eb4'), (155, 3, 2, 'G4'),
                                      (156, 0, 1, 'Bb4'), (156, 1, 1, 'G4'), (156, 2, 1, 'Eb4'), (156, 3, 1.5, 'Eb5'),
                                      (156, 4.5, .5, 'Bb4'), (156, 5, 1, 'G4'), (157, 0, 3, 'G5'), (157, 3, 1, 'G4'),
                                      (193, 0, 1, 'D5'), (193, 1, 1, 'A4'), (193, 2, .5, 'G4'), (193, 2.5, .5, 'F#4'),
                                      (193, 3, 2, 'C5')]])
SINGERS.append([x + (WOG,) for x in [(146, 5, 1, 'C5'), (147, 0, 1, 'F5'), (147, 1, 1.5, 'C5'), (147, 2.5, .5, 'Ab4'),
                                     (147, 3, 1, 'F4'), (147, 4, 1, 'Ab4'), (147, 5, 1, 'C5'), (148, 0, 2, 'Eb5'),
                                     (149, 3, 1.5, 'F5'), (149, 4.5, .5, 'D5'), (149, 5, 1, 'Bb4'), (150, 0, 2, 'G5'),
                                     (192, 0, 1, 'Bb4'), (192, 2, .5, 'G4'), (192, 2.5, .5, 'G4'), (192, 3, 1, 'D5')]])
SINGERS.append([x + (FLO,) for x in [(152, 0, 1.5, 'Bb4'), (152, 1.5, .5, 'G4'), (152, 2, 1, 'Eb4'), (152, 3, 2, 'Eb5'),
                                     (152, 5, 1, 'Bb4'), (153, 0, 1.5, 'Eb5'), (153, 1.5, .5, 'Bb4'), (153, 2, 1, 'G4'),
                                     (153, 3, 2, 'C5'), (153, 5, 1, 'Bb4'),
                                     (158, 2, 1, 'G4'), (158, 3, 2, 'C5'), (158, 5, 1, 'Eb5'), (159, 0, 5, 'D5'),
                                     (160, 0, 4, 'G4'), (160, 4, 1, 'C5'), (160, 5, 1, 'Eb5'), (161, 0, 2, 'D5'),
                                     (162, 0, 1, 'Eb5'), (162, 1, 1, 'C5'), (162, 2, 1, 'Bb4'), (162, 3, 2, 'A4'),
                                     (162, 5, 1, 'Bb4'), (163, 0, 1.5, 'C5'), (163, 1.5, .5, 'B4'), (163, 2, 1, 'C5'),
                                     (163, 3, 1, 'Eb5'), (163, 5, 1, 'C5'), (164, 0, 2, 'Eb5'), (164, 2, 1, 'C5'),
                                     (164, 3, 1.5, 'G5'), (164, 4.5, .5, 'Eb5'), (164, 5, 1, 'C5'), (165, 0, 3, 'A4'),
                                     (192, 2.5, .5, 'D4'), (192, 3, 1.5, 'D4'), (192, 4.5, .5, 'D4'), (192, 5, 1, 'D4'),
                                     (193, 0, 2, 'A4')]])
VOICE = sorted(x for line in SINGERS for x in line)

COLOR = [hexc('#c0f4ff'), hexc('#20ff90'), hexc('#8c60ff')]
DEEP = hexc('#065c70')
GREEN = hexc('#14c080')
ALB = hexc('#ff3000')
MUD = hexc('#6a2200')
GOLD = hexc('#ffb000')


def at(G, seg, u):
    s = G.pd[G.seg[seg]]
    return float(s.min() + u * (s.max() - s.min()))


def compose():
    """Every note: (time, seconds, midi, velocity, part, who). 'sing' is a Rhinemaiden's line (who: which one);
    the excerpt's notes are 'rock' (the right hand's rocking accompaniment) and 'low' (the left hand)."""
    N = []
    for b, x, n, name, who in VOICE:
        t0 = bt(b + x / 6)
        N.append((t0, bt(b + (x + n) / 6) - t0, note(name), 96, 'sing', who))
    for t, d, m, v, h in EX['notes']:
        N.append((t, d, m, v, 'rock' if h == 0 else 'low', None))
    return sorted(N, key=lambda e: e[0])


def follow(target, rate):
    """Critically damped chase of a target track (per frame), `rate` in 1/s per frame."""
    x = np.empty_like(target)
    x[0], v = target[0], 0.0
    for f in range(1, len(target)):
        w = rate[f]
        a = w * w * (target[f] - x[f - 1]) - 2 * w * v
        v += a * DT
        x[f] = x[f - 1] + v * DT
    return x


def choreography(G):
    """Per frame: where each maiden and Alberich are (path distance) and how present they are (0..1)."""
    F = nframes(D)
    t = np.arange(F) * DT
    pf = at(G, 'Porch Front', 0.5)
    corner = at(G, 'Left', 0.98)
    tgt = np.zeros((3, F))
    rate = np.full((3, F), 3.0)
    alpha = np.zeros((3, F))
    alpha[WOG] = smoothstep(T_WOG, T_WOG + 0.4, t)
    alpha[WELL] = smoothstep(T_WELL, T_WELL + 0.3, t)
    alpha[FLO] = smoothstep(T_FLO, T_FLO + 0.3, t)

    def span(a, b):
        return (t >= a) & (t < b)

    sway = np.sin(2 * np.pi * t / (4 * BAR))
    tgt[WOG] = pf + 140 * sway
    tgt[WELL] = G.length + 40
    m = span(T_WELL, T_DUET)
    tgt[WELL][m], rate[WELL][m] = pf + 300, 2.2
    m = span(T_DUET, T_GAME)
    tgt[WOG][m] = pf + 170 * np.sin(2 * np.pi * (t[m] - T_DUET) / (2 * BAR))
    tgt[WELL][m] = pf - 170 * np.sin(2 * np.pi * (t[m] - T_DUET) / (2 * BAR))
    tgt[FLO] = at(G, 'Left', 0.5)
    m = span(T_FLO + 1.0, bt(154.5))
    tgt[FLO][m], rate[FLO][m] = at(G, 'Porch Left', 0.4), 1.6
    m = span(bt(154.5), T_GAME)                             # she dives down between them; they swing wider round her
    tgt[FLO][m], rate[FLO][m] = pf + 40 * np.sin(2 * np.pi * (t[m] - T_DUET) / BAR), 3.0
    tgt[WOG][m] = pf + 300 * np.sin(2 * np.pi * (t[m] - T_DUET) / (2 * BAR))
    tgt[WELL][m] = pf - 300 * np.sin(2 * np.pi * (t[m] - T_DUET) / (2 * BAR))

    # the game: the singer darts to her spot; the others drift where they are
    here = {WOG: pf + 100, WELL: pf - 100, FLO: at(G, 'Porch Left', 0.4)}
    for i, (who, _) in enumerate(GAME):
        a = T_GAME + i * 2 * BAR
        here[who] = at(G, *GAME_TO[i])
        for k in range(3):
            m = span(a, a + 2 * BAR)
            tgt[k][m] = here[k] + (30 * np.sin(2 * np.pi * t[m] / 1.7 + k) if k != who else 0)
            rate[k][m] = 7.0 if k == who else 2.0

    # the whirlpool: all three round and round the porch, swinging wider out over the wings, then home
    m = span(T_WHIRL, T_LAUGH)
    u = (t[m] - T_WHIRL) / (T_LAUGH - T_WHIRL)
    r = 220 + 760 * np.sin(np.pi * u) ** 0.7
    ph = 2 * np.pi * (0.45 * (t[m] - T_WHIRL) + 0.35 * (t[m] - T_WHIRL) ** 2 / 6)
    for k in range(3):
        tgt[k][m] = pf + r * np.sin(ph + 2 * np.pi * k / 3)
        rate[k][m] = 30.0
    m = span(T_LAUGH, T_HEHE)
    for k, off in ((WOG, 0), (WELL, 150), (FLO, -150)):
        tgt[k][m] = pf + off * smoothstep(T_LAUGH + 1.0, T_HEHE, t[m]) + 20 * np.sin(2 * np.pi * t[m] / 0.9 + k)
        rate[k][m] = 4.0
    m = span(T_HEHE, T_GUARD)                               # frozen where they are
    for k, off in ((WOG, 0), (WELL, 150), (FLO, -150)):
        tgt[k][m], rate[k][m] = pf + off, 6.0
    m = span(T_GUARD, T_MOCK)                               # a knot round the rock
    for k, off in ((WOG, 0), (WELL, 45), (FLO, -45)):
        tgt[k][m], rate[k][m] = pf + off + 12 * np.sin(2 * np.pi * t[m] / 0.7 + 2 * k), 5.0
    m = t >= T_MOCK
    for k, (s, u) in ((WOG, ('Porch Front', 0.55)), (WELL, ('Right', 0.45)), (FLO, ('Porch Right', 0.45))):
        tgt[k][m] = at(G, s, u) + 25 * np.sin(2 * np.pi * t[m] / 1.6 + k)
        rate[k][m] = 3.5
    pos = np.array([follow(tgt[k], rate[k]) for k in range(3)])

    # Alberich: heaves up out of the corner, then creeps toward the porch a lurch at a time
    apos = np.full(F, corner)
    for i, c in enumerate(CREEP):
        apos += 45 * smoothstep(c + 0.3, c + 0.6, t)
    apos -= sum(18 * np.exp(-np.clip(t - (h + 0.4), 0, None) / 0.25) * (t > h + 0.4) for h in LAUGHS)
    aa = 0.15 * smoothstep(T_ALB, T_ALB + 0.4, t)
    for i, c in enumerate(CLIMB):
        aa += 0.2 * smoothstep(c + 0.35, c + 0.55, t)
    return dict(t=t, pos=pos, alpha=alpha, apos=apos, aalpha=np.clip(aa, 0, 1))


def render(G, seed=2):
    rng = np.random.default_rng(seed)
    F = nframes(D)
    out = np.zeros((F, G.N, 3))
    d = G.pd
    pf = at(G, 'Porch Front', 0.5)
    C = choreography(G)
    N = compose()
    sung = [np.array([e[0] for e in N if e[4] == 'sing' and e[5] == k]) for k in range(3)]
    pitch = [np.array([e[2] for e in N if e[4] == 'sing' and e[5] == k]) for k in range(3)]
    splash = sorted([(T_WOG, WOG), (T_WELL + 1.3, WELL), (T_FLO, FLO), (T_MOCK, WOG)] +
                    [(T_GAME + i * 2 * BAR + 0.25, who) for i, (who, _) in enumerate(GAME)] +
                    [(T_WHIRL, k) for k in range(3)] + [(T_LAUGH, k) for k in range(3)])
    rock = np.array([e[0] for e in N if e[4] == 'rock' and e[0] < T_HEHE])
    heaves = CLIMB + CREEP
    smoulder = Flicker(rng, G.N, 0.6, 2.4)
    shiver = Flicker(rng, 3, 5.0, 9.0)

    for f in range(F):
        t = f * DT
        fr = np.zeros((G.N, 3))
        # the river: two trains of waves, rocking with the harp
        ri = int(np.searchsorted(rock, t, side='right')) - 1
        lift = 0.06 * np.exp(-(t - rock[ri]) / 0.25) if ri >= 0 and t - rock[ri] < 1.5 else 0
        w1 = 0.5 + 0.5 * np.cos(2 * np.pi * (d / 340 - 0.16 * t))
        w2 = 0.5 + 0.5 * np.cos(2 * np.pi * (d / 140 + 0.33 * t) + 1)
        ap, aa = C['apos'][f], C['aalpha'][f]
        murk = aa * np.exp(-((d - ap) / 260) ** 2)
        dim = 1 - 0.25 * smoothstep(T_ALB, T_ALB + 4, t) * (1 - smoothstep(T_MOCK, D, t) * 0.5)
        clean = (1 - 0.75 * murk) * dim
        fr += light(DEEP, (0.2 + 0.1 * w1 + lift) * clean) + light(GREEN, (0.07 + 0.2 * w1 * w2 + lift) * clean)
        fr += light(MUD, 0.45 * murk * (1 + 0.15 * smoulder(t)))

        # the sleeping gold, glimpsed under the knot of maidens
        g = smoothstep(T_GUARD, T_GUARD + 1.5, t)
        if g > 0:
            fr += light(GOLD, 0.35 * g * (0.8 + 0.2 * np.sin(2 * np.pi * 0.4 * t)) * np.exp(-((d - pf) / 35) ** 2))

        # splashes: a ring of foam in the maiden's colour, out from where she is
        for ts, who in splash:
            if ts <= t < ts + 1.0:
                p = np.interp(ts, C['t'], C['pos'][who])
                r = 40 + 320 * (t - ts) ** 0.6
                ring = np.exp(-((np.abs(d - p) - r) / 35) ** 2) * (1 - (t - ts))
                fr += light(COLOR[who], 0.8 * ring) + light(hexc('#ffffff'), 0.35 * ring ** 3)

        # a splash in the game washes the run she lands on in her colour; the whirlpool tints the whole river
        for i, (who, _) in enumerate(GAME):
            ts = T_GAME + i * 2 * BAR + 0.25
            if ts <= t < ts + 2.5:
                fr += light(COLOR[who], 0.5 * np.exp(-(t - ts) / 0.7) * (G.seg_of == GAME_TO[i][0]))
        ww = smoothstep(T_WHIRL, T_WHIRL + 1.0, t) * (1 - smoothstep(T_LAUGH - 0.5, T_LAUGH + 0.5, t))
        if ww > 0:
            for k in range(3):
                fr += light(COLOR[k], 0.4 * ww * np.exp(-((d - C['pos'][k][f]) / 300) ** 2))

        # the maidens: a bright body, a halo and a wake; a note they sing makes them flare
        frozen = smoothstep(T_HEHE, T_HEHE + 0.2, t) * (1 - smoothstep(T_GUARD, T_GUARD + 0.5, t))
        for k in range(3):
            a = C['alpha'][k][f]
            if a <= 0:
                continue
            p = C['pos'][k][f]
            i = int(np.searchsorted(sung[k], t, side='right')) - 1
            flare = 0.0
            if i >= 0 and t - sung[k][i] < 1.0:
                flare = np.exp(-(t - sung[k][i]) / 0.2) * (0.6 + 0.4 * (pitch[k][i] - 51) / 30)
            b = a * (0.62 + 0.38 * flare) * (1 - 0.35 * frozen * (0.5 + 0.5 * shiver(t)[k]))
            body = np.exp(-((d - p) / (20 + 10 * flare)) ** 2)
            halo = np.exp(-((d - p) / 90) ** 2)
            trail = np.zeros(G.N)
            for j, lag in enumerate((4, 8, 12, 16, 20)):
                q = C['pos'][k][max(f - lag, 0)]
                trail = np.maximum(trail, np.exp(-((d - q) / 26) ** 2) * (1 - j / 5.5))
            fr += light(COLOR[k], b * body + 0.3 * b * halo + 0.45 * a * trail * (abs(p - C['pos'][k][max(f - 8, 0)]) > 25))
            fr += light(hexc('#ffffff'), 0.4 * b * flare * body)

        # Alberich: a smouldering lump that jolts with every heave
        if aa > 0:
            jolt = sum(np.exp(-(t - h - 0.47) / 0.2) for h in heaves if h + 0.47 <= t < h + 1.5)
            core = np.exp(-((d - ap) / (28 + 10 * jolt)) ** 2)
            fr += light(ALB, aa * (0.55 + 0.35 * jolt) * core * (1 + 0.2 * smoulder(t)))

        # laughter: sparks fly from each maiden at him
        for tl in LAUGHS:
            if tl <= t < tl + 0.9:
                for k in range(3):
                    p0 = np.interp(tl, C['t'], C['pos'][k])
                    u = (t - tl) / 0.6
                    q = p0 + (ap - p0) * min(u, 1)
                    fade = 1 - smoothstep(0.6, 0.9, t - tl)
                    fr += light(COLOR[k], 0.85 * fade * np.exp(-((d - q) / 16) ** 2))
            if tl + 0.6 <= t < tl + 1.2:
                fr += light(hexc('#ffd0a0'), 0.6 * np.exp(-(t - tl - 0.6) / 0.15) * np.exp(-((d - ap) / 60) ** 2))
        if t > D - 1.0:
            fr *= (D - t) / 1.0 * 0.5 + 0.5
        out[f] = fr
    return np.clip(out, 0, 1)


def score(M, G):
    """Wagner's notes on the orchestra, the Rhinemaidens' lines each on her own instrument, and the stage: splashes
    as they surface and dart, the scrape and thud of Alberich heaving himself up the rock."""
    order = np.argsort(G.pd)
    xs, ds = G.pos[order, 0], G.pd[order]
    x0, x1 = xs.min(), xs.max()

    def pan_at(dd):
        x = np.interp(dd, ds, xs)
        return float(0.85 * (2 * (x - x0) / (x1 - x0) - 1))

    C = choreography(G)
    where = lambda k, t: pan_at(np.interp(t, C['t'], C['pos'][k]))
    o = Orchestra(M, level=3.2)
    splash = M.hits('Miscellania Raw/Misc 1/bubbles*.wav')

    def role(t, d, m, v, h):
        dark = t >= T_ALB
        if h == 0 and not dark:                                         # the rocking: violins and violas, light
            return [('violins' if m >= 55 else 'violas', 0, -8, 0.45), ('harp', 0, -14, 0.35)]
        if h == 0:                                                      # his slithering chords: low brass, bassoons
            return [('trombones', 0, 6, 0.6), ('bassoons', 0, 0, 0.5), ('violas', 0, -6, 0.35)]
        if dark and m < 48:
            return [('tuba', 12 if m < 36 else 0, 4, 0.55), ('basses', 12 if m < 40 else 0, 0, 0.5)]
        return [('cellos', 0, -4, 0.55), ('basses', -12 if m >= 40 else 0, -10, 0.35)]

    o.tutti(tidy(EX['notes']), role=role)
    inst = {WOG: [('oboes', 0.85), ('flutes', 0.3)], WELL: [('flutes', 0.9), ('clarinets', 0.25)],
            FLO: [('clarinets', 0.95), ('violas', 0.3)]}
    for t, d, m, v, part, who in compose():
        if part == 'sing':
            for name, g in inst[who]:
                o.play(name, m, t, d, 100, where(who, t), g)
    # the stage
    for ts, who in [(T_WOG + 0.05, WOG), (T_WELL + 1.3, WELL), (T_FLO, FLO)] + \
            [(T_GAME + i * 2 * BAR + 0.25, who) for i, (who, _) in enumerate(GAME)]:
        M.add('fx', splash.play(110), ts, 0.7, where(who, ts))
        o.hit('triangle', ts, 70, gain=0.15, pan=where(who, ts))
    for k in range(3):
        M.add('fx', splash.play(100), T_WHIRL + 0.3 * k, 0.5, where(k, T_WHIRL + 0.3 * k))
    corner = pan_at(at(G, 'Left', 0.98))
    o.hit('gong scrape', T_ALB, 90, gain=0.35, pan=corner)
    for h in CLIMB:
        o.hit('scrape', h + 0.4, 96, gain=0.4, pan=corner)
        o.hit('bass drum', h + 0.47, 104, gain=0.5, pan=corner)
    o.hit('timpani', T_HEHE, 88, pitch=-5, gain=0.35, pan=corner)
    # effects lead on the splashes and his climb, and get out of the way of the singing
    o.effects([(0.0, -6), (1.0, -10), (T_WELL + 0.8, -4), (T_WELL + 2.0, -10), (T_FLO - 0.2, -5),
               (T_FLO + 1.5, -11), (T_GAME - 0.5, -3), (T_LAUGH, -2), (T_HEHE + 0.4, -8), (CALLS[0], -12),
               (T_GUARD, -10), (D, -10)])
