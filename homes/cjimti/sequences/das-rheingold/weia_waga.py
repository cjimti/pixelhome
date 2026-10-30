"""Weia! Waga!: the curtain is up on the bed of the Rhine, sunlit green water rocking over the whole roof to a
harp in A flat. The three Rhinemaidens are lights in it: Woglinde (silver) surfaces on the rock at the back of
the porch with a splash and sings her greeting to the waters, the motif Donington lists as the Rhinemaidens'
(26), and swims with it. Wellgunde (sea green) streaks in from the free end of Right to sing it with her a
third below; Flosshilde (violet), the eldest, pops up on Left an octave down and scolds them for guarding the
sleeping gold so badly. Then the game: the tune is tossed between them two bars at a time, and each singer
darts to a new run of the house with a splash, until all three sing it together in a whirlpool that spins out
over every run and collapses, laughing, on the rock.

The water darkens at the corner of Left: Alberich, a smouldering red-brown thing, hauls himself up out of a
chasm in four lurches and calls out to them. They freeze, ask each other who is there, and close round the
rock (a glint of the sleeping gold shows under them) as Flosshilde warns that their father told them to guard
it from just such a creature. He creeps along toward the porch; they laugh at him and pelt him with sparks of
their colours, then scatter to the front runs and mock him with the first notes of the song.

Every note is in compose(); choreography() turns it into positions, and render() and score() both read it."""
import numpy as np
from pixelhome.audio import note
from pixelhome.fx import DT, hexc, light, smoothstep, nframes, Flicker
from pixelhome.leitmotifs import MOTIFS

CODE = 'RG02'
TITLE = 'Weia! Waga!'
KIND = 'show'
DESCRIPTION = ('Three Rhinemaidens, silver, green and violet, sing and chase each other through the sunlit river '
               'over the gold they guard, until something ugly climbs up out of the dark at the corner of the '
               'house.')
VOICEOVER = ('At the bottom of the Rhine, three river daughters play over a treasure they were told to guard. '
             'They are not very good at guarding it.')

BEAT = 0.5                                  # a quarter note; a bar of 6/8 is three
BAR = 3 * BEAT
T_WOG = 1.5                                 # Woglinde surfaces
T_SONG = 3.0                                # and sings
T_WELL = 9.0                                # Wellgunde streaks in from the end of Right
T_DUET = 10.5
T_FLO = 16.5                                # Flosshilde pops up on Left, scolding
T_GAME = 22.5                               # the tune tossed between them, two bars each
T_WHIRL = T_GAME + 6 * 2 * BAR              # all three, spinning
T_LAUGH = T_WHIRL + 4 * BAR
T_ALB = 48.0                                # the water darkens at the corner of Left
CLIMB = [48.4, 49.4, 50.4, 51.2]
T_HEHE = 52.0                               # "Hehe! Ihr Nicker!"
CALLS = [53.5, 55.0, 56.5]                  # who is there?
T_GUARD = 58.0                              # "Guard the gold!"
CREEP = [62.0, 64.5, 67.0, 69.5]            # he creeps toward the porch...
LAUGHS = [63.5, 66.0, 68.5, 71.0]           # ...and they laugh at him
T_MOCK = 74.0
D = 80.0

WOG, WELL, FLO = 0, 1, 2
GAME = [(WOG, 0), (WELL, 1), (FLO, 0), (WOG, 1), (WELL, 0), (FLO, 1)]     # (singer, which half of the tune)
GAME_TO = [('Right', 0.5), ('Left', 0.45), ('Porch Right', 0.5), ('Porch Left', 0.5), ('Right', 0.92),
           ('Porch Front', 0.5)]

SONG = [(b, d, note(n)) for b, d, n in MOTIFS['rhinemaidens']['notes'] if d >= 0.5]   # Woglinde's line
ROCK = [(b, d, note(n)) for b, d, n in MOTIFS['rhinemaidens']['notes'] if d < 0.5][:6]  # one bar of the rocking
SCALE = (8, 10, 0, 1, 3, 5, 7)              # A flat major

COLOR = [hexc('#c0f4ff'), hexc('#20ff90'), hexc('#8c60ff')]
DEEP = hexc('#065c70')
GREEN = hexc('#14c080')
ALB = hexc('#ff3000')
MUD = hexc('#6a2200')
GOLD = hexc('#ffb000')


def at(G, seg, u):
    s = G.pd[G.seg[seg]]
    return float(s.min() + u * (s.max() - s.min()))


def third_below(m):
    """A diatonic third under m in A flat."""
    i = SCALE.index(m % 12)
    j = (i - 2) % 7
    return m - ((SCALE[i] - SCALE[j]) % 12)


def compose():
    """Every note: (time, seconds, midi, velocity, part, who). Parts: 'sing' (who: the maiden), 'rock' the harp's
    rocking, 'pedal', 'alb' Alberich's clambering, 'hehe' his call, 'laugh', 'guard', 'trem'."""
    N = []

    def sing(who, t0, notes, vel=96, tr=0, harm=False):
        for b, d, m in notes:
            m = third_below(m) if harm else m
            N.append((t0 + b * BEAT, d * BEAT, m + tr, vel, 'sing', who))

    half = [[x for x in SONG if x[0] < 6], [(b - 6, d, m) for b, d, m in SONG if b >= 6]]
    sing(WOG, T_SONG, SONG)
    sing(WOG, T_DUET, SONG, 90)
    sing(WELL, T_DUET, SONG, 90, harm=True)
    scold = [(6, .5, 'Eb4'), (6.5, .5, 'Eb4'), (7, .5, 'F4'), (7.5, .5, 'Eb4'), (8, .5, 'C4'), (8.5, .5, 'Db4'),
             (9, 1, 'C4'), (10, .5, 'Bb3'), (10.5, 1.5, 'Ab3')]
    sing(FLO, T_FLO, half[0], 98, tr=-12)
    sing(FLO, T_FLO, [(b, d, note(m)) for b, d, m in scold], 100)
    for i, (who, h) in enumerate(GAME):
        sing(who, T_GAME + i * 2 * BAR, half[h], 100, tr=-12 if who == FLO else 0)
    sing(WOG, T_WHIRL, SONG, 108)
    sing(WELL, T_WHIRL, SONG, 104, harm=True)
    sing(FLO, T_WHIRL, SONG, 104, tr=-12)
    for i, (hi, lo) in enumerate((('Eb6', 'C6'), ('C6', 'Ab5'), ('Bb5', 'G5'), ('Ab5', 'F5'), ('G5', 'Eb5'),
                                  ('Ab5', 'Eb5'))):
        for m in (hi, lo):
            N.append((T_LAUGH + i * 0.24, 0.16, note(m), 96 - 4 * i, 'laugh', i % 3))

    for k in range(int(T_ALB / BAR) + 1):                   # the rocking, a bar at a time, until he comes
        for b, d, m in ROCK:
            t = k * BAR + b * BEAT
            if t < T_ALB:
                N.append((t, d * BEAT * 1.5, m, 70 + 10 * (b == 0), 'rock', None))
    for t0, t1, m in ((0.0, T_ALB + 0.5, 'Ab1'), (0.0, T_ALB + 0.5, 'Ab2'), (2.0, T_ALB, 'Eb4'), (2.0, T_ALB, 'C4')):
        N.append((t0, t1 - t0, note(m), 62, 'pedal', None))

    # Alberich: a chromatic scramble up and a thump for every heave; then "Hehe! Ihr Nicker!"
    for i, t0 in enumerate(CLIMB + CREEP):
        base = note('C2') + (2 * i if i < 4 else 2 * (i - 4) + 3)
        for j in range(5):
            N.append((t0 + j * 0.09, 0.12, base + j, 90 + 4 * j, 'alb', i))
        N.append((t0 + 0.47, 0.5, base - 12, 112, 'thump', i))
    for b, d, m in ((0, .5, 'G2'), (.75, .25, 'G2'), (1, .5, 'C3'), (1.5, .5, 'Eb3'), (2, 1.5, 'D3')):
        N.append((T_HEHE + b * BEAT, d * BEAT, note(m), 112, 'hehe', None))
    N.append((T_ALB, D - T_ALB, note('C2'), 64, 'trem', None))
    for who, t0, line in ((WOG, CALLS[0], ('Eb5', 'C5', 'Bb4', 'Db5')), (WELL, CALLS[1], ('C5', 'Ab4', 'F4', 'G4')),
                          (FLO, CALLS[2], ('G4', 'Eb4', 'C4', 'D4'))):
        for j, m in enumerate(line):
            N.append((t0 + j * 0.3, 0.32 if j < 3 else 0.7, note(m), 92, 'sing', who))
    guard = [(0, .75, 'C4'), (.75, .25, 'C4'), (1, .5, 'Eb4'), (1.5, 1.5, 'D4'), (3, .5, 'C4'), (3.5, .5, 'Bb3'),
             (4, .5, 'Ab3'), (4.5, 2.5, 'G3')]
    for b, d, m in guard:
        N.append((T_GUARD + b * BEAT, d * BEAT, note(m), 104, 'sing', FLO))
    for t0, t1, ms in ((T_GUARD, T_GUARD + 3 * BEAT, ('Ab3', 'C4', 'Eb4')), (T_GUARD + 3 * BEAT, CREEP[0], ('G3', 'B3', 'D4'))):
        for m in ms:
            N.append((t0, t1 - t0, note(m), 70, 'guard', None))
    for i, t0 in enumerate(LAUGHS):
        who = i % 3 if i < 3 else None
        for j, (hi, lo) in enumerate((('C6', 'Ab5'), ('Bb5', 'G5'), ('Ab5', 'F5'), ('G5', 'Eb5'))):
            for m in (hi, lo):
                N.append((t0 + j * 0.2, 0.14, note(m), 100, 'laugh', who if who is not None else j % 3))
    for b, d, m in [x for x in SONG if x[0] < 3]:
        N.append((T_MOCK + b * BEAT, d * BEAT, m, 92, 'sing', WOG))
    for k in range(4):
        for b, d, m in ROCK:
            t = T_MOCK + 1.5 + k * BAR + b * BEAT
            if t < D - 1.0:
                N.append((t, d * BEAT * 1.5, m, 54, 'rock', None))
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
    m = span(T_FLO + 1.0, T_GAME)
    tgt[FLO][m], rate[FLO][m] = at(G, 'Porch Left', 0.4), 1.6

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
    rock = np.array([e[0] for e in N if e[4] == 'rock'])
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
        g = smoothstep(T_GUARD, T_GUARD + 1.5, t) * (1 - smoothstep(CREEP[0] + 2, CREEP[0] + 5, t))
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
    from pixelhome.audio import SR
    n = note
    order = np.argsort(G.pd)
    xs, ds = G.pos[order, 0], G.pd[order]
    x0, x1 = xs.min(), xs.max()

    def pan_at(dd):
        x = np.interp(dd, ds, xs)
        return float(0.85 * (2 * (x - x0) / (x1 - x0) - 1))

    C = choreography(G)

    def pan_of(who, t):
        return pan_at(np.interp(t, C['t'], C['pos'][who]))

    for name, gain, rev in (('voices', 0.2, 0.35), ('choir', 0.12, 0.45), ('harp', 0.2, 0.35), ('strings', 0.12, 0.3),
                            ('low', 0.16, 0.15), ('brass', 0.16, 0.25), ('perc', 0.2, 0.2), ('laugh', 0.12, 0.3)):
        M.bus(name, gain=gain, reverb=rev)
    voice = [M.sampler('Woodwinds/Flute/susvib/*.wav', tune=-12), M.sampler('Woodwinds/Oboe/Vib/*.wav', tune=-12),
             M.sampler('Woodwinds/Clarinet/susLong/*.wav', tune=-12)]
    harp = M.sampler('Strings/Harp/*.wav')
    vc = M.sampler('Strings/Cello Section/susvib/*.wav', tune=-12)
    cb = M.sampler('Strings/Solo Contrabass/SusNV/*.wav', tune=-12)
    va = M.sampler('Strings/Viola Section/susvib/*.wav', tune=-12)
    trem = M.sampler('Strings/Cello Section/trem/*.wav', tune=-12)
    vtrem = M.sampler('Strings/Violin Section/Trem/*.wav', tune=-12)
    bsn = M.sampler('Woodwinds/Bassoon/stac/*.wav', tune=-12)
    pizz = M.sampler('Strings/Solo Contrabass/Pizz/*.wav', tune=-12)
    tbn = M.sampler('Brass/Tenor Trombone/sus/*.wav', tune=-12)
    pic = M.sampler('Woodwinds/Piccolo/Stac/*.wav', tune=-12)
    flst = M.sampler('Woodwinds/Flute/stac/*.wav', tune=-12)
    timp = M.hits('Percussion/Timpani/Timpani1_Hit*.wav')
    roll = M.hits('Percussion/Timpani/Rolls/*.wav')

    def hold(bus, s, m, t0, t1, vel, pan=0.0, step=2.5, rise=1.0, fall=1.2, gain=1.0):
        a0 = s.play(m, vel)
        step = min(step, (a0.shape[1] / SR - 0.35) / 2)
        w = int(2 * step * SR)
        win = np.hanning(w)
        t = t0 - step
        while t < t1 + fall:
            a = s.play(m, vel)[:, int(0.25 * SR):int(0.25 * SR) + w]
            a = a * win[:a.shape[1]]
            tt = t + np.arange(a.shape[1]) / SR
            env = np.clip((tt - t0) / rise, 0, 1) * np.clip(1 - (tt - t1) / fall, 0, 1)
            M.add(bus, a * env, t, gain, pan)
            t += step

    choir = [[], [], []]
    for t, d, m, v, part, who in compose():
        if part == 'sing':
            M.add('voices', voice[who].play(m, v, dur=d * 1.05, release=0.18), t, 1.0, pan_of(who, t))
            choir[who].append((t, m, v - 30, d))
        elif part == 'rock':
            M.add('harp', harp.play(m, v), t, 1.0, -0.3 + 0.6 * ((m - 51) / 12))
        elif part == 'pedal':
            s = cb if m < 40 else (vc if m < 55 else va)
            hold('strings' if m >= 55 else 'low', s, m, t, t + d, v, 0.0, rise=2.0, gain=0.8)
        elif part == 'alb':
            M.add('low', bsn.play(m, v), t, 0.9, pan_at(C['apos'][min(int(t / DT), len(C['apos']) - 1)]))
        elif part == 'thump':
            p = pan_at(C['apos'][min(int(t / DT), len(C['apos']) - 1)])
            M.add('low', pizz.play(m + 12, v), t, 1.0, p)
            M.add('perc', timp.play(v - 10, pitch=-5), t, 0.7, p)
        elif part == 'hehe':
            M.add('brass', tbn.play(m, v, dur=d, release=0.15), t, 1.0, pan_at(C['apos'][int(t / DT)]))
        elif part == 'trem':
            hold('low', trem, m, t, t + d - 1.0, v, -0.4, rise=1.5, gain=0.7)
            hold('low', trem, m + 7, t + 4.0, t + d - 1.0, v - 8, 0.4, rise=2.0, gain=0.5)
        elif part == 'guard':
            hold('strings', vtrem, m + 12, t, t + d, v, 0.0, rise=0.4, fall=0.6, gain=0.6)
        elif part == 'laugh':
            M.add('laugh', (pic if m >= n('Ab5') else flst).play(m, v), t, 1.0, pan_of(who, t))
    for who, pat in ((WOG, 'Pads/Ooh'), (WELL, 'Pads/Ooh'), (FLO, 'Pads/Ooh')):
        if choir[who]:
            M.add('choir', M.synth(pat).render(choir[who], D + 2), 0.0, 1.0, (0.0, 0.5, -0.5)[who])
    M.add('perc', roll.play(60, dur=3.5), T_GUARD - 0.5, 0.5, 0.0)
