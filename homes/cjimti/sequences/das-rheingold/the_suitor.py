"""The Suitor from Below: Alberich (a smouldering red lump with a muddy halo) tries to climb Porch Left to
Woglinde on the rock and slides back down the slimy stones three times, each slip a chromatic slither in the
low strings and a splash of mud. Then the wet gets up his nose: three wheezing swells and a sneeze that sprays
the porch with green-brown muck while the maidens giggle.

The three Rhinemaidens take turns with him, as in the opera. Woglinde (silver) comes down singing the second
half of her greeting (Donington 26), lets him lunge, and is gone to the far side of the porch before he
arrives; twice. Wellgunde (green) swims down to an oboe love song, lets him edge close, and calls him a hairy,
humpbacked fool in a burst of piccolo before she zips away. Flosshilde (violet), cruellest because sweetest,
glides to meet him in the middle of the porch to a clarinet serenade; they merge, and the whole porch glows
rose and pulses, until she slips out and all three burst out laughing: the rose shatters into glitter of their
three colours that sprays over the entire house.

Then his rage, in C minor: horns and trombones turn the maidens' falling step into his lament, the low strings
drive, and he streaks after them six times across the house; each time the maiden leaps away with a cry and
the run he lands on flashes red. Spent, he slumps toward the rock at the back of the porch, and in the last
seconds a faint gold light begins to glimmer there, with one muted horn note: the first of the Gold's call.

compose() holds every note, choreography() every position; render() and score() read both."""
import numpy as np
from pixelhome.audio import note
from pixelhome.fx import DT, hexc, light, smoothstep, nframes, Flicker
from pixelhome.leitmotifs import MOTIFS

CODE = 'RG03'
TITLE = 'The Suitor from Below'
KIND = 'show'
DESCRIPTION = ('Alberich the dwarf slips and slides, sneezes, and tries his luck with each Rhinemaiden in turn. '
               'They lead him on, laugh in his face, and leave him raging, just as something starts to glow on '
               'the rock behind him.')
VOICEOVER = ('Up from the dark comes Alberich, wet, clumsy, and in love with all three of them at once. '
             'The river daughters think this is the funniest thing that has ever happened.')

BEAT = 0.5                                  # a quarter note at 120
SLIPS = [0.5, 3.0, 5.5]                     # three tries at the rock, each a scramble and a slide back
AH = [8.0, 8.6, 9.2]
CHOO = 9.9
T_WOG = 11.0
LUNGE_W = [17.0, 23.5]                      # at Woglinde
T_WELL = 26.5                               # Wellgunde's love song
T_INSULT = 36.0
T_FLO = 43.0                                # Flosshilde's serenade
T_MERGE = 50.0
T_BREAK = 56.0                              # she slips out; they all laugh
T_RAGE = 60.0
LUNGES = [60.5, 62.5, 64.5, 66.5, 68.5, 70.5]
T_SPENT = 72.0
T_GLIMMER = 76.0
D = 80.0

WOG, WELL, FLO = 0, 1, 2
CHASE = [(FLO, ('Porch Right', 0.5)), (WOG, ('Left', 0.3)), (WELL, ('Porch Left', 0.4)), (FLO, ('Right', 0.6)),
         (WOG, ('Porch Front', 0.5)), (WELL, ('Right', 0.3))]     # whom he lunges at, and where she leaps to

SONG = [(b, d, note(n)) for b, d, n in MOTIFS['rhinemaidens']['notes'] if d >= 0.5]
COLOR = [hexc('#c0f4ff'), hexc('#20ff90'), hexc('#8c60ff')]
DEEP = hexc('#065c70')
GREEN = hexc('#14c080')
ALB = hexc('#ff1000')
HOT = hexc('#ff8a20')
MUD = hexc('#5a1200')
MUCK = hexc('#7a9010')
ROSE = hexc('#ff2a80')
GOLD = hexc('#ffb000')
WHITE = hexc('#ffffff')


def at(G, seg, u):
    s = G.pd[G.seg[seg]]
    return float(s.min() + u * (s.max() - s.min()))


def compose():
    """Every note: (time, seconds, midi, velocity, part, who). who is a maiden for 'sing' and 'laugh'."""
    N = []

    def add(t, d, m, v, part, who=None):
        N.append((float(t), float(d), note(m) if isinstance(m, str) else int(m), int(v), part, who))

    def line(t0, notes, part, who=None, vel=96, tr=0):
        for b, d, m in notes:
            add(t0 + b * BEAT, d * BEAT, (note(m) if isinstance(m, str) else m) + tr, vel, part, who)

    def laugh(t0, who, reps=1, top='C6'):
        steps = (('C6', 'Ab5'), ('Bb5', 'G5'), ('Ab5', 'F5'), ('G5', 'Eb5'))
        for r in range(reps):
            for j, (hi, lo) in enumerate(steps):
                for m in (hi, lo):
                    add(t0 + (r * 4 + j) * 0.18, 0.13, m, 100 - 3 * j, 'laugh', who if who is not None else (r + j) % 3)

    add(0.0, T_GLIMMER, 'C2', 60, 'trem')
    for i, ta in enumerate(SLIPS):                          # scramble up, slide down, splash; a giggle
        for j in range(6):
            add(ta + j * 0.1, 0.12, note('G1') + 2 * i + j, 92 + 3 * j, 'scramble')
        for k in range(3):
            add(ta + 0.6 * k, 0.3, note('C1') + 3 * k, 96, 'heave')
        for j in range(8):
            add(ta + 1.8 + j * 0.05, 0.08, note('C3') - j, 90 - 3 * j, 'slide')
        add(ta + 1.8, 0.35, 'C2', 108, 'grunt')
        add(ta + 2.2, 0.12, 'Eb5', 84, 'laugh', i)
        add(ta + 2.35, 0.12, 'C5', 80, 'laugh', i)
    for i, (t, m) in enumerate(zip(AH, ('G3', 'Bb3', 'D4'))):
        add(t, 0.45, m, 70 + 14 * i, 'ah')
    add(CHOO, 0.6, 'C2', 124, 'choo')
    laugh(CHOO + 0.5, None, 2)

    line(T_WOG, [(b - 6, d, m) for b, d, m in SONG if b >= 6], 'sing', WOG, 98)
    for k, tl in enumerate(LUNGE_W):
        for j in range(8):
            add(tl - 0.4 + j * 0.05, 0.08, note('C4') + (0, 2, 3, 5, 7, 8, 11, 12)[j], 96, 'lunge')
        add(tl + 0.5, 0.5, 'C1', 120, 'thud')
        for j in range(8):
            add(tl + 0.55 + j * 0.06, 0.09, note('Eb3') - j, 86, 'slide')
        line(tl + 2.0, [x for x in SONG if x[0] < 3], 'sing', WOG, 92)
    line(LUNGE_W[0] + 3.6, [(0, .5, 'C3'), (.5, .5, 'Db3'), (1, 1, 'C3'), (2, .5, 'B2'), (2.5, 1.5, 'C3')], 'grumble')

    love = [(0, 1, 'Eb5'), (1, .5, 'F5'), (1.5, .5, 'Eb5'), (2, 1, 'C5'), (3, 1, 'Ab4'), (4, 1.5, 'Bb4'),
            (5.5, .5, 'C5'), (6, 2, 'Db5'), (8, 1, 'C5'), (9, 1, 'Bb4'), (10, 2, 'Ab4'), (12, 1, 'Eb5'),
            (13, 1, 'Db5'), (14, 1, 'C5'), (15, 1, 'Bb4'), (16, 3, 'Ab4')]
    line(T_WELL, love, 'sing', WELL, 92)
    for t0, ch in ((0, ('Ab2', 'Eb3', 'C4')), (6, ('Db3', 'F3', 'Ab3')), (10, ('Ab2', 'Eb3', 'C4')),
                   (12, ('Eb3', 'G3', 'Db4')), (16, ('Ab2', 'Eb3', 'C4'))):
        for m in ch:
            add(T_WELL + t0 * BEAT, (4 if t0 != 6 else 4) * BEAT * 1.1, m, 66, 'pad')
    line(T_WELL + 7.0, [(0, .5, 'Eb3'), (.5, .5, 'F3'), (1, 1.5, 'Ab3')], 'grumble', None, 80)
    for j, m in enumerate(('C6', 'Ab5', 'F5', 'D5', 'C6', 'G5')):
        add(T_INSULT + j * 0.11, 0.1, m, 112, 'insult', WELL)
    add(T_INSULT + 0.8, 0.8, 'C2', 124, 'stamp')

    serenade = [(0, 1.5, 'Ab4'), (1.5, .5, 'Bb4'), (2, 1, 'C5'), (3, 1, 'Db5'), (4, 2, 'F5'), (6, 1, 'Eb5'),
                (7, 1, 'Db5'), (8, 1.5, 'C5'), (9.5, .5, 'Db5'), (10, 2, 'Eb5'), (12, 1, 'F5'), (13, 1, 'Gb5'),
                (14, 2, 'F5'), (16, 1, 'Eb5'), (17, 1, 'C5'), (18, 3, 'Db5')]
    line(T_FLO, serenade, 'sing', FLO, 94)
    line(T_FLO, serenade, 'serenade', FLO, 70, tr=-12)
    for t0, ch in ((0, ('Db3', 'Ab3', 'F4')), (4, ('Gb2', 'Db3', 'Bb3')), (8, ('Ab2', 'Eb3', 'C4')),
                   (12, ('Bb2', 'F3', 'Db4')), (16, ('Ab2', 'Gb3', 'C4')), (18, ('Db3', 'Ab3', 'F4'))):
        for m in ch:
            add(T_FLO + t0 * BEAT, 4.4 * BEAT if t0 < 18 else T_BREAK - T_FLO - 9.0, m, 70, 'pad')
    for m in ('Db4', 'F4', 'Ab4', 'Db5'):
        add(T_MERGE + 3.4, T_BREAK - T_MERGE - 3.4, m, 74, 'swell')
    gl = [x for x in range(note('Db3'), note('Ab5') + 1) if x % 12 in (1, 5, 8)]
    for i, m in enumerate(gl):
        add(T_MERGE + 4.4 + i * 1.4 / len(gl), 1.0, m, 90, 'harp')
    for i, m in enumerate(reversed(gl)):
        add(T_BREAK + i * 1.2 / len(gl), 0.6, m, 100, 'harp')
    add(T_BREAK, 1.0, 'C5', 120, 'crash')
    laugh(T_BREAK, None, 3)

    for k in range(int((T_SPENT - T_RAGE) / (BEAT / 2))):  # the rage: driving eighths in C minor
        m = ('C2', 'C2', 'Eb2', 'C2', 'G1', 'C2', 'Ab1', 'G1')[k % 8]
        add(T_RAGE + k * BEAT / 2, BEAT / 2 * 0.8, m, 96 + 8 * (k % 4 == 0), 'drive')
    for t0 in (T_RAGE, T_RAGE + 4, T_RAGE + 8):           # his lament: the maidens' falling step, in the minor
        for hi, lo in (('Ab3', 'G3'), ('Eb3', 'D3'), ('C3', 'B2')):
            add(t0, 2 * BEAT * 1.6, hi, 112, 'woe')
            add(t0 + 2 * BEAT * 1.6, 2 * BEAT * 1.4, lo, 104, 'woe')
    for i, (tl, (who, _)) in enumerate(zip(LUNGES, CHASE)):
        for j in range(6):
            add(tl - 0.3 + j * 0.05, 0.08, note('G3') + (0, 3, 5, 7, 8, 11)[j] + i, 96, 'lunge')
        add(tl + 0.45, 0.4, 'C1', 116, 'thud')
        line(tl + 0.4, [(0, .5, 'F5'), (.5, 1, 'Eb5')], 'sing', who, 104)
    add(T_SPENT - 2.0, 2.2, 'C2', 90, 'roll')
    line(T_SPENT + 0.5, [(0, 1.5, 'Eb3'), (1.5, 2.5, 'D3'), (4, 1.5, 'C3'), (5.5, 3, 'B2')], 'grumble', None, 84)
    add(T_SPENT + 2.5, 0.12, 'Eb5', 76, 'laugh', WOG)
    add(T_SPENT + 2.7, 0.12, 'C5', 72, 'laugh', WOG)
    add(T_SPENT + 3.6, 0.12, 'Eb5', 70, 'laugh', FLO)
    for m in ('G5', 'C6'):
        add(T_GLIMMER, D - T_GLIMMER, m, 56, 'shimmer')
    add(T_GLIMMER + 1.0, D - T_GLIMMER - 1.0, 'G3', 70, 'call')
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


def choreography(G):
    """Per frame: where each maiden and Alberich are (path distance)."""
    F = nframes(D)
    t = np.arange(F) * DT
    P = {k: at(G, *k) for k in [('Porch Front', 0.55), ('Right', 0.45), ('Porch Right', 0.45), ('Porch Left', 0.42),
                                ('Porch Right', 0.5), ('Right', 0.5), ('Right', 0.85), ('Porch Front', 0.35),
                                ('Porch Front', 0.7), ('Left', 0.5), ('Porch Left', 0.75), ('Porch Front', 0.4),
                                ('Left', 0.55), ('Porch Right', 0.7)]}
    tgt = np.zeros((4, F))                  # three maidens, then Alberich
    rate = np.full((4, F), 3.0)

    def set_(k, a, b, where, r):
        m = (t >= a) & (t < b)
        tgt[k][m] = where if np.ndim(where) == 0 else where[m]
        rate[k][m] = r

    bob = [12 * np.sin(2 * np.pi * t / 1.4 + k) for k in range(3)]
    set_(WOG, 0, D, P['Porch Front', 0.55] + bob[0], 3.0)
    set_(WELL, 0, D, P['Right', 0.45] + bob[1], 3.0)
    set_(FLO, 0, D, P['Porch Right', 0.45] + bob[2], 3.0)
    A = P['Porch Left', 0.42]
    set_(3, 0, D, A, 6.0)
    for ta in SLIPS:
        for k in range(3):
            set_(3, ta + 0.6 * k, ta + 0.6 * (k + 1), A + 45 * (k + 1), 9.0)
        set_(3, ta + 1.8, ta + 2.5, A, 16.0)

    # Woglinde comes down to him, twice; he lunges, twice; she is gone
    set_(WOG, T_WOG, LUNGE_W[0], A + 180 + bob[0], 1.6)
    set_(3, T_WOG + 1.5, LUNGE_W[0], A + 90, 2.0)
    set_(3, LUNGE_W[0], LUNGE_W[0] + 0.5, A + 230, 18.0)
    set_(WOG, LUNGE_W[0] + 0.05, LUNGE_W[1], P['Porch Front', 0.4] + bob[0], 12.0)
    set_(3, LUNGE_W[0] + 0.5, LUNGE_W[0] + 2.0, A + 60, 7.0)
    set_(3, LUNGE_W[0] + 2.0, LUNGE_W[1], A + 170, 1.4)
    set_(3, LUNGE_W[1], LUNGE_W[1] + 0.5, P['Porch Front', 0.4] + 10, 18.0)
    set_(WOG, LUNGE_W[1] + 0.05, T_BREAK, P['Right', 0.5] + bob[0], 12.0)
    set_(3, LUNGE_W[1] + 0.5, T_WELL, A + 120, 6.0)

    # Wellgunde's lure; the insult
    set_(WELL, T_WELL - 1.0, T_INSULT, P['Porch Front', 0.35] - 30, 0.9)
    set_(3, T_WELL + 3.0, T_INSULT, P['Porch Left', 0.75] + 20, 1.1)
    set_(WELL, T_INSULT, D, P['Right', 0.85] + bob[1], 14.0)

    # Flosshilde's serenade: they meet in the middle of the porch and sway together
    sway = 25 * np.sin(2 * np.pi * t / 2.0)
    set_(FLO, T_FLO - 1.0, T_MERGE, P['Porch Front', 0.4] + 15, 1.0)
    set_(3, T_FLO + 1.0, T_MERGE, P['Porch Front', 0.4] - 15, 1.0)
    set_(FLO, T_MERGE, T_BREAK, P['Porch Front', 0.4] + 8 + sway, 4.0)
    set_(3, T_MERGE, T_BREAK, P['Porch Front', 0.4] - 8 + sway, 4.0)
    set_(FLO, T_BREAK, LUNGES[0], P['Left', 0.5] + bob[2], 14.0)
    set_(WOG, T_BREAK, LUNGES[1], P['Porch Front', 0.7] + bob[0], 6.0)
    set_(3, T_BREAK, LUNGES[0], P['Porch Front', 0.4], 4.0)

    # the rage: he streaks at one, she leaps away just before he arrives
    here = {WOG: P['Porch Front', 0.7], WELL: P['Right', 0.85], FLO: P['Left', 0.5]}
    for i, (tl, (who, dest)) in enumerate(zip(LUNGES, CHASE)):
        nxt = LUNGES[i + 1] if i + 1 < len(LUNGES) else T_SPENT
        set_(3, tl, nxt, here[who], 11.0)
        here[who] = at(G, *dest)
        set_(who, tl + 0.35, D, here[who] + bob[who], 13.0)
    set_(3, T_SPENT, T_SPENT + 2.0, tgt[3][int(T_SPENT / DT) - 1], 3.0)
    set_(3, T_SPENT + 2.0, D, P['Porch Left', 0.75], 0.8)
    set_(WELL, T_SPENT + 1.0, D, P['Left', 0.55] + bob[1], 1.2)
    set_(WOG, T_SPENT + 1.0, D, P['Porch Right', 0.7] + bob[0], 1.2)
    pos = np.array([follow(tgt[k], rate[k]) for k in range(4)])
    return dict(t=t, pos=pos[:3], apos=pos[3])


def render(G, seed=3):
    rng = np.random.default_rng(seed)
    F = nframes(D)
    out = np.zeros((F, G.N, 3))
    d = G.pd
    pf = at(G, 'Porch Front', 0.5)
    C = choreography(G)
    N = compose()
    sung = [np.array([e[0] for e in N if e[4] == 'sing' and e[5] == k]) for k in range(3)]
    porch = np.isin(G.seg_of, ['Porch Left', 'Porch Front', 'Porch Right'])
    jolts = sorted([ta + 1.8 for ta in SLIPS] + [tl + 0.5 for tl in LUNGE_W] + [T_INSULT + 0.8] +
                   [tl + 0.45 for tl in LUNGES])
    smoulder = Flicker(rng, G.N, 0.6, 2.4)
    tw = Flicker(rng, G.N, 3.0, 8.0)

    def spray(n, t0, at_, vmin, vmax, cols):
        return dict(t0=t0, p=np.full(n, at_), v=rng.choice([-1, 1], n) * rng.uniform(vmin, vmax, n),
                    c=rng.integers(len(cols), size=n), cols=cols, w=rng.uniform(12, 24, n))
    sprays = []
    for f in range(F):
        t = f * DT
        fr = np.zeros((G.N, 3))
        ap = C['apos'][f]

        # the river, muddy round Alberich
        w1 = 0.5 + 0.5 * np.cos(2 * np.pi * (d / 340 - 0.16 * t))
        w2 = 0.5 + 0.5 * np.cos(2 * np.pi * (d / 140 + 0.33 * t) + 1)
        rage = smoothstep(T_RAGE - 0.5, T_RAGE + 0.5, t) * (1 - smoothstep(T_SPENT, T_SPENT + 3, t))
        murk = np.exp(-((d - ap) / (240 + 200 * rage)) ** 2)
        clean = (1 - 0.7 * murk) * (0.8 - 0.25 * rage)
        fr += light(DEEP, (0.2 + 0.1 * w1) * clean) + light(GREEN, (0.07 + 0.18 * w1 * w2) * clean)
        fr += light(MUD, 0.34 * murk * (1 + 0.15 * smoulder(t)))

        # mud from each slip; the sneeze, inflating him and spraying the porch with muck
        for ta in SLIPS:
            ts = ta + 1.8
            if ts <= t < ts + 1.0:
                r = 30 + 220 * (t - ts) ** 0.6
                fr += light(MUD, 0.9 * (1 - (t - ts)) * np.exp(-((np.abs(d - ap) - r) / 30) ** 2))
        if abs(t - CHOO) < DT / 2:
            sprays.append(spray(60, t, ap, 150, 900, [MUCK, MUD, HOT]))
        if abs(t - T_BREAK) < DT / 2:
            sprays.append(spray(120, t, ap, 150, 1500, COLOR))
        puff = sum(0.35 * smoothstep(a, a + 0.4, t) for a in AH) * (t < CHOO)
        if CHOO <= t < CHOO + 0.8:
            fr += light(MUCK, 0.6 * np.exp(-(t - CHOO) / 0.25) * np.exp(-((d - ap) / 400) ** 2))

        # Flosshilde's embrace: the porch glows rose and pulses, the wings a little too
        love = smoothstep(T_MERGE - 1.5, T_MERGE + 2.0, t) * (1 - smoothstep(T_BREAK - 0.1, T_BREAK + 0.15, t))
        if love > 0:
            beat = 0.75 + 0.25 * np.cos(2 * np.pi * (t - T_MERGE) / (4 * BEAT * 0.75))
            swell = 0.5 + 0.5 * smoothstep(T_MERGE + 3, T_BREAK, t)
            fr += light(ROSE, love * beat * swell * (0.85 * porch + 0.22 * ~porch) *
                        (0.7 + 0.3 * np.exp(-((d - ap) / 250) ** 2)))

        # the maidens
        for k in range(3):
            p = C['pos'][k][f]
            i = int(np.searchsorted(sung[k], t, side='right')) - 1
            flare = np.exp(-(t - sung[k][i]) / 0.2) if i >= 0 and t - sung[k][i] < 1.0 else 0.0
            b = 0.62 + 0.38 * flare
            trail = np.zeros(G.N)
            moving = abs(p - C['pos'][k][max(f - 8, 0)]) > 25
            if moving:
                for j, lag in enumerate((3, 6, 9, 12, 15)):
                    q = C['pos'][k][max(f - lag, 0)]
                    trail = np.maximum(trail, np.exp(-((d - q) / 24) ** 2) * (1 - j / 5.5))
            body = np.exp(-((d - p) / (20 + 10 * flare)) ** 2)
            fr += light(COLOR[k], b * body + 0.3 * b * np.exp(-((d - p) / 90) ** 2) + 0.45 * trail)
            fr += light(WHITE, 0.4 * b * flare * body)
        for tl, (who, _) in zip(LUNGES + LUNGE_W, CHASE + [(WOG, None)] * 2):      # where she leapt from
            ts = tl + 0.35
            if ts <= t < ts + 0.8:
                p0 = np.interp(ts, C['t'], C['pos'][who])
                r = 30 + 260 * (t - ts) ** 0.6
                fr += light(COLOR[who], 0.8 * (1 - (t - ts) / 0.8) * np.exp(-((np.abs(d - p0) - r) / 30) ** 2))

        # Alberich: smouldering, jolting at every slip, thud and stamp; hot and trailing in his rage
        jolt = sum(np.exp(-(t - j) / 0.22) for j in jolts if j <= t < j + 1.5)
        width = 28 + 10 * jolt + 45 * puff + 20 * rage
        hue = ALB * (1 - 0.4 * love) + HOT * 0.4 * love
        fr += light(hue, (0.6 + 0.35 * jolt + 0.3 * puff + 0.2 * love) * np.exp(-((d - ap) / width) ** 2)
                    * (1 + 0.2 * smoulder(t)))
        if rage > 0:
            trail = np.zeros(G.N)
            for j, lag in enumerate(range(2, 22, 2)):
                q = C['apos'][max(f - lag, 0)]
                trail = np.maximum(trail, np.exp(-((d - q) / 30) ** 2) * (1 - j / 10.5))
            fr += light(HOT, 0.7 * rage * trail)
        for tl in LUNGES:                                   # the run he lands on flashes red
            tland = tl + 0.45
            if tland <= t < tland + 1.2:
                seg = G.seg_of[np.argmin(np.abs(d - np.interp(tland, C['t'], C['apos'])))]
                fr += light(ALB, 0.5 * np.exp(-(t - tland) / 0.35) * (G.seg_of == seg))

        # sprays of particles: muck from the sneeze, glitter from the laughter
        for s in sprays:
            age = t - s['t0']
            if age > 3.5:
                continue
            q = s['p'] + s['v'] * (1 - np.exp(-age / 0.7)) * 0.7
            fade = np.exp(-age / 1.4)
            for c, col in enumerate(s['cols']):
                sel = s['c'] == c
                if sel.any():
                    g = np.exp(-((d[:, None] - q[sel][None, :]) / s['w'][sel][None, :]) ** 2).max(axis=1)
                    fr += light(col, 1.0 * fade * g * (0.7 + 0.3 * tw(t)))

        # the first glimmer on the rock
        if t >= T_GLIMMER:
            g = smoothstep(T_GLIMMER, D, t)
            fr += light(GOLD, 0.8 * g * (0.75 + 0.25 * np.sin(2 * np.pi * 0.7 * t)) * np.exp(-((d - pf) / 40) ** 2))
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

    def pan_of(who, t):
        return pan_at(np.interp(t, C['t'], C['pos'][who] if who is not None else C['apos']))

    for name, gain, rev in (('voices', 0.2, 0.35), ('choir', 0.1, 0.45), ('strings', 0.13, 0.3), ('low', 0.17, 0.15),
                            ('brass', 0.17, 0.25), ('perc', 0.22, 0.2), ('laugh', 0.11, 0.3), ('fx', 0.1, 0.25),
                            ('harp', 0.2, 0.4)):
        M.bus(name, gain=gain, reverb=rev)
    voice = [M.sampler('Woodwinds/Flute/susvib/*.wav', tune=-12), M.sampler('Woodwinds/Oboe/Vib/*.wav', tune=-12),
             M.sampler('Woodwinds/Clarinet/susLong/*.wav', tune=-12)]
    bsn = M.sampler('Woodwinds/Bassoon/stac/*.wav', tune=-12)
    bsus = M.sampler('Woodwinds/Bassoon/sus/*.wav', tune=-12)
    cl = M.sampler('Woodwinds/Clarinet/stac/*.wav', tune=-12)
    vc = M.sampler('Strings/Cello Section/susvib/*.wav', tune=-12)
    vcs = M.sampler('Strings/Cello Section/spic/*.wav', tune=-12)
    va = M.sampler('Strings/Viola Section/susvib/*.wav', tune=-12)
    vn = M.sampler('Strings/Violin Section/susVib/*.wav', tune=-12)
    vtrem = M.sampler('Strings/Violin Section/Trem/*.wav', tune=-12)
    trem = M.sampler('Strings/Cello Section/trem/*.wav', tune=-12)
    pizz = M.sampler('Strings/Solo Contrabass/Pizz/*.wav', tune=-12)
    cbs = M.sampler('Strings/Solo Contrabass/Spic/*.wav', tune=-12)
    tbn = M.sampler('Brass/Tenor Trombone/sus/*.wav', tune=-12)
    horn = M.sampler('Brass/F Horn/sus/*.wav', tune=-12)
    mute = M.sampler('Brass/F Horn/mute/*.wav', tune=-12)
    tuba = M.sampler('Brass/Tuba/sus/*.wav', tune=-12)
    pic = M.sampler('Woodwinds/Piccolo/Stac/*.wav', tune=-12)
    flst = M.sampler('Woodwinds/Flute/stac/*.wav', tune=-12)
    harp = M.sampler('Strings/Harp/*.wav')
    timp = M.hits('Percussion/Timpani/Timpani1_Hit*.wav')
    roll = M.hits('Percussion/Timpani/Rolls/*.wav')
    crash = M.hits('Percussion/cymbal-crash1_f*.wav')

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
            env = np.clip((tt - t0) / rise, 0, 1) * np.clip(1 - (tt - t1) / fall, 0, 1)
            M.add(bus, a * env, t, gain, pan)
            t += step

    choir = [[], [], []]
    for t, d, m, v, part, who in compose():
        pa = pan_of(None, t)
        if part == 'sing':
            M.add('voices', voice[who].play(m, v, dur=d * 1.05, release=0.18), t, 1.0, pan_of(who, t))
            choir[who].append((t, m, v - 30, d))
        elif part == 'serenade':
            M.add('strings', vn.play(m + 12, v, dur=d * 1.05, release=0.3), t, 0.6, pan_of(who, t))
        elif part == 'laugh':
            M.add('laugh', (pic if m >= note('Ab5') else flst).play(m, v), t, 1.0, pan_of(who, t))
        elif part == 'trem':
            hold('low', trem, m, t, t + d, v, -0.3, rise=2.0, gain=0.6)
        elif part in ('scramble', 'lunge'):
            M.add('low', (bsn if m < note('C3') else cl).play(m, v), t, 0.9, pa)
        elif part == 'heave':
            M.add('low', pizz.play(m + 12, v), t, 0.9, pa)
        elif part == 'slide':
            M.add('strings', vc.play(m, v, dur=d * 1.5, release=0.05), t, 0.8, pa)
        elif part == 'grunt':
            M.add('brass', tbn.play(m + 12, v, dur=d, release=0.1), t, 0.9, pa)
            M.add('fx', whoosh(0.6, 2200, 300, 0.5, seed=int(t * 10)), t - 0.1, 0.6, pa)
        elif part == 'ah':
            M.add('low', bsus.play(m - 12, v, dur=d, release=0.1), t, 0.8, pa)
            M.add('voices', voice[2].play(m, v - 10, dur=d, release=0.1), t, 0.5, pa)
        elif part == 'choo':
            M.add('brass', tuba.play(m, v, dur=d, release=0.2), t, 1.0, pa)
            M.add('brass', tbn.play(m + 12, v, dur=d, release=0.2), t, 0.9, pa)
            M.add('perc', crash.play(110), t, 0.8, pa)
            M.add('perc', timp.play(120, pitch=-3), t, 0.8, pa)
            M.add('fx', whoosh(0.5, 4000, 900, 0.6, seed=9), t, 0.9, pa)
        elif part == 'thud':
            M.add('perc', timp.play(v, pitch=-6), t, 0.9, pa)
            M.add('low', pizz.play(m + 12, v), t, 1.0, pa)
            M.add('fx', whoosh(0.4, 1500, 4000, 0.4, seed=int(t * 10)), t - 0.45, 0.5, pa)
        elif part == 'grumble':
            M.add('low', bsus.play(m, v, dur=d, release=0.15), t, 0.9, pa)
        elif part == 'pad':
            hold('strings', va if m >= note('C3') else vc, m, t, t + d, v, 0.0, rise=0.6, fall=0.8, gain=0.7)
        elif part == 'insult':
            M.add('laugh', pic.play(m, v), t, 1.2, pan_of(who, t))
        elif part == 'stamp':
            M.add('brass', tuba.play(m, v, dur=d, release=0.3), t, 1.0, pa)
            M.add('brass', tbn.play(m + 7, v, dur=d, release=0.3), t, 0.8, pa)
            M.add('perc', timp.play(124, pitch=-4), t, 1.0, pa)
        elif part == 'swell':
            hold('strings', vtrem, m, t, t + d, v, 0.0, rise=2.0, fall=0.3, gain=0.7)
        elif part == 'harp':
            M.add('harp', harp.play(m, v), t, 1.0, -0.6 + 1.2 * (m - 49) / 32)
        elif part == 'crash':
            M.add('perc', crash.play(v), t, 0.9, 0.0)
        elif part == 'drive':
            M.add('low', cbs.play(m + 12, v), t, 0.9, -0.2)
            M.add('low', vcs.play(m + 12, v - 10), t, 0.6, 0.2)
        elif part == 'woe':
            s = horn if m >= note('Eb3') else tbn
            M.add('brass', s.play(m, v, dur=d, release=0.4), t, 0.9, -0.3 if s is horn else 0.3)
        elif part == 'roll':
            M.add('perc', roll.play(v, dur=d), t, 0.6, 0.0)
        elif part == 'shimmer':
            hold('strings', vtrem, m, t, t + d, v, 0.0, rise=2.5, fall=1.0, gain=0.4)
        elif part == 'call':
            M.add('brass', mute.play(m, v, dur=d, release=1.0), t, 0.9, pan_at(at(G, 'Porch Front', 0.5)))
    for who in range(3):
        M.add('choir', M.synth('Pads/Ooh').render(choir[who], D + 2), 0.0, 1.0, (0.0, 0.5, -0.5)[who])
