"""The Giants: the castle is finished and its builders have come for their wage. Fasolt (stone grey) and Fafner
(ochre) stand on the Right wing as two great rough masses, and their motif, the giants' strength (Donington 58),
comes in the tubas, trombones and timpani with a stamp on every heavy beat: each stamp shakes the whole run
they stand on, a flash of their colour, a tremor through the pixels and a ring of dust rolling out along the
roofline. Across the porch Valhalla gleams white-gold as battlements; the wings are a dim dawn meadow.

Fasolt states the bargain to the giants' authority (Donington 59): the line falls step by step down the scale
and each step sends a grey push along the house toward the gods. Wotan (deep blue, on Left) answers with his
treaties (Donington 14) in the trombones, blue swelling out from him and the castle brightening behind, and
then the spear (Donington 73), the descending scale on which the treaties are cut: each note draws his spear a
step further, a steel white-blue line running from him down Porch Left and across the front of the castle,
between the gods and the giants.

Fasolt stamps again. Then Fafner, slyer, makes his point to his own crawling motif (Donington 57): the gods
live on Freia's golden apples. An apple figure of our own rises on flute and harp, and with each note a
golden apple with a green leaf lights up in the orchard on the left wing, while an ochre tendril reaches out
from Fafner toward them. The giants advance onto Porch Right, a stamp per step, the battlements dimming
under their bulk, and Freia (pink, hiding between Fricka and Wotan) cries out for her brothers, Donner and Froh,
pink sparks flying from her over the left of the house.

compose() holds every note, choreography() every position; render() and score() read both."""
import numpy as np
from pixelhome.audio import note
from pixelhome.fx import DT, hexc, light, smoothstep, nframes, Flicker
from pixelhome.leitmotifs import play

CODE = 'RG09'
TITLE = 'The Giants'
KIND = 'show'
DESCRIPTION = ('The giants Fasolt and Fafner stamp in to collect their wage for building Valhalla: the goddess '
               'Freia. Wotan points to his treaties and his spear, but Fafner knows what the gods would lose '
               'with her, the golden apples that keep them young.')
VOICEOVER = ('The castle is built, and the builders want paying. '
             'Two giants have come for their wage, and every step they take shakes the ground.')

BEAT = 0.55                                 # a quarter note
T_STR = [1.0, 8.0]                          # the giants' strength, twice, stamping
T_AUTH = 16.0                               # Fasolt states the bargain
T_TREATY = 29.0                             # Wotan: the treaties
T_SPEAR = 39.5                              # the spear
T_STR2 = 47.0                               # Fasolt again, angrier
T_FAF = 53.0                                # Fafner: the apples
T_APPLE = 54.5
T_ADV = 62.0                                # the giants advance onto Porch Right
T_CRY = 70.0                                # Freia: Donner! Froh!
D = 80.0
T0 = 0.0                                    # seconds since The Giants began: sways and drifts run on

FASOLT, FAFNER = 0, 1
WOTAN, FRICKA, FREIA = 0, 1, 2
APPLES = [('Side', 0.62), ('Left', 0.12), ('Side', 0.8), ('Left', 0.3), ('Side', 0.93), ('Left', 0.05),
          ('Side', 0.7), ('Left', 0.22), ('Left', 0.36), ('Side', 0.86), ('Left', 0.17), ('Side', 0.98)]
APPLE_TUNE = [(0, .5, 'D5'), (.5, .5, 'F#5'), (1, 1, 'A5'), (2, .5, 'B5'), (2.5, .5, 'A5'), (3, 1, 'F#5'),
              (4, .5, 'E5'), (4.5, .5, 'F#5'), (5, 1, 'A5'), (6, .5, 'D6'), (6.5, .5, 'C#6'), (7, 1.5, 'A5')]
CRY = [(0, 1.5, 'A4'), (1.5, 2.5, 'F5'), (4.5, 1, 'E5'), (5.5, 2, 'C5'), (8, 1, 'D5'), (9, 2.5, 'A4'),
       (12, 1, 'E5'), (13, 3, 'C#5')]                  # "Help! Help me! Donner! Froh!"

WOT = hexc('#1a3cff')
SPEAR = hexc('#c8d8ff')
FRI = hexc('#ff9ad0')
FRE = hexc('#ff5a9a')
APPLE = hexc('#ffd040')
LEAF = hexc('#60d020')
GREY = hexc('#8090a0')
OCHRE = hexc('#c07a10')
DUST = hexc('#6a5a48')
VAL = hexc('#fff0c0')
DAWN0 = hexc('#2a3a6a')
DAWN1 = hexc('#6a5a8a')
WHITE = hexc('#ffffff')
GCOL = [GREY, OCHRE]
GODCOL = [WOT, FRI, FRE]


def at(G, seg, u):
    s = G.pd[G.seg[seg]]
    return float(s.min() + u * (s.max() - s.min()))


# The mountaintop as Freia's Flight (RG08) leaves it, so RG06 to RG12 are one continuous place: the same meadow,
# clouds, rosy glow, castle stones and glints, on RG08's clock (its phases run on t + 160 from the start of RG06).
SKY_HI = hexc('#6a5a8a')
GLOW = hexc('#ff9070')
NEAR = hexc('#a05a96')
FAR = hexc('#2638a0')
EARTH = hexc('#5a4a30')
T8 = T0 + 80.0                              # this scene's start on Freia's Flight's clock


def mountain(G):
    """What stays put on the mountaintop: the meadow's colours, the castle's stones and battlements, and the
    grass and glint flickers seeded as RG08 seeds them, so they carry on across the cut."""
    d = G.pd
    pf = at(G, 'Porch Front', 0.5)
    porch = np.isin(G.seg_of, ['Porch Left', 'Porch Front', 'Porch Right']).astype(float)
    p0, p1 = at(G, 'Porch Left', 0.0), at(G, 'Porch Right', 1.0)
    far = np.clip(np.where(d < p0, p0 - d, np.where(d > p1, d - p1, 0.0)) / 520, 0, 1)
    r8 = np.random.default_rng(8)
    return dict(d=d, pf=pf, porch=porch, wing=1 - porch, p0=p0, L=G.length,
                merlon=smoothstep(0.25, 0.55, 0.5 + 0.5 * np.cos(2 * np.pi * (d - pf) / 46)),
                stone=0.88 + 0.12 * np.random.default_rng(6).uniform(-1, 1, G.N),
                walls=smoothstep(700, 580, np.maximum(np.abs(d - pf), 1)) * porch,
                sky=0.4 * SKY_HI[None, :] + 0.6 * (NEAR[None, :] * (1 - far[:, None]) + FAR[None, :] * far[:, None]),
                tw=Flicker(r8, G.N, 0.3, 1.2), grass=Flicker(r8, G.N, 0.1, 0.5))


def scenery(S, t, castle=1.0):
    """The dawn meadow, its drifting cloud, the rosy glow behind the castle and the gleaming battlements."""
    d, tt, t8 = S['d'], t + T8 + 160, t + T8
    roll = 0.5 + 0.5 * np.cos(2 * np.pi * (d / 300 - 0.04 * tt))
    fr = light(S['sky'], 0.34 * (0.85 + 0.1 * roll + 0.05 * S['grass'](t8)) * (S['wing'] + 0.6 * S['porch']))
    c1 = 0.5 + 0.5 * np.cos(2 * np.pi * (d / 380 - 0.02 * tt))
    c2 = 0.5 + 0.5 * np.cos(2 * np.pi * (d / 170 + 0.035 * tt) + 1)
    cloud = smoothstep(0.35, 1.0, c1 * c2)
    fr += light(SKY_HI, 0.3 * cloud * S['wing'])
    fr += light(GLOW, (0.12 + 0.16 * cloud) * np.exp(-((d - S['pf']) / 750) ** 2) * (0.9 + 0.1 * roll))
    gleam = 0.5 + 0.5 * np.cos(2 * np.pi * ((d - S['p0']) / 260 - 0.18 * tt))
    w = S['walls'] * castle
    fr += light(VAL, 0.82 * w * S['stone'] * (0.42 + 0.58 * S['merlon']) * (0.85 + 0.15 * gleam ** 4))
    fr += light(WHITE, 0.35 * w * S['merlon'] * gleam ** 12 * (0.7 + 0.3 * S['tw'](t8)))
    return fr


def menace(fr, S, gp, amount=1.0):
    """The giants' end of the house: darkened and dusty from 250 units short of the nearer giant outward."""
    m = amount * smoothstep(gp - 250, gp + 50, S['d'])
    fr *= (1 - 0.4 * m)[:, None]
    fr += light(EARTH, 0.3 * m)


def giant(fr, S, p, col, pulse=0.0):
    """A giant: a big flat-topped body, a dark shadow round it, a dust-brown halo; fades out past the end of Right."""
    d = S['d']
    vis = smoothstep(S['L'] + 60, S['L'] - 40, p)
    if vis <= 0:
        return
    body = smoothstep(48, 34, np.abs(d - p))
    fr *= (1 - 0.6 * vis * smoothstep(80, 50, np.abs(d - p)) * (1 - body))[:, None]
    fr += light(col, vis * ((0.5 + 0.2 * pulse) * body + 0.2 * np.exp(-((d - p) / 16) ** 2)
                            + 0.18 * np.exp(-((d - p) / 140) ** 2)))
    fr += light(EARTH, vis * 0.25 * np.exp(-((d - p) / 200) ** 2))


def stomp(fr, S, age, p, col, s):
    """A stamp: a dull flash where it lands, a ripple running out toward the gods; returns the house's shudder."""
    d = S['d']
    land = min(p, S['L'] - 10)
    fr += light(col, 0.8 * s * np.exp(-age / 0.2) * np.exp(-((d - land) / 240) ** 2))
    r = 1100 * smoothstep(0, 1.4, age)
    fr += light(col, 0.55 * s * np.exp(-((land - d - r) / 110) ** 2) * (1 - age / 1.6) * (d < land))
    return s * np.exp(-age / 0.09)


def freia_light(fr, S, fy, t, flare=0.0, fear=1.0, here=1.0):
    """Freia as RG08 draws her: trembling pink with her three golden apples circling her and two leaves."""
    d, t8 = S['d'], t + T8
    quiver = 1 - 0.3 * fear * (0.5 + 0.5 * np.sin(2 * np.pi * 7 * t8))
    b = here * (0.85 + 0.3 * flare - 0.2 * fear) * quiver
    width = 16 + 6 * flare - 4 * fear
    fr += light(FRE, b * np.exp(-((d - fy) / width) ** 2) + 0.35 * b * np.exp(-((d - fy) / 80) ** 2))
    fr += light(WHITE, 0.4 * here * flare * np.exp(-((d - fy) / 10) ** 2))
    for k in range(3):
        q = fy + (26 - 8 * fear) * np.sin(2 * np.pi * (1.3 * t8 + k / 3))
        fr += light(APPLE, 0.85 * here * np.exp(-((d - q) / 6) ** 2) * (1 - 0.4 * fear))
    for k in range(2):
        q = fy + 38 * np.sin(2 * np.pi * (0.9 * t8 + k / 2 + 0.25))
        fr += light(LEAF, 0.6 * here * (1 - 0.6 * fear) * np.exp(-((d - q) / 5) ** 2))


def god_light(fr, S, p, col, b=0.78, wash=0.0):
    """Wotan or Fricka as RG08 draws them: a core 28 wide in a 130-wide halo; Wotan's blue washes his wing."""
    d = S['d']
    fr += light(col, b * np.exp(-((d - p) / 28) ** 2) + 0.35 * b * np.exp(-((d - p) / 130) ** 2))
    if wash:
        fr += light(col, wash * np.exp(-((d - p) / 260) ** 2) * S['wing'])


def compose():
    """Every note: (time, seconds, midi, velocity, part, who)."""
    N = []

    def add(t, d, m, v, part, who=None):
        N.append((float(t), float(d), note(m) if isinstance(m, str) else int(m), int(v), part, who))

    add(0.0, T_TREATY, 'C2', 64, 'pedal')
    for k, t0 in enumerate(T_STR + [T_STR2, T_ADV]):
        beat = BEAT * (0.82 if t0 == T_STR2 else 1.0)
        v = (88, 100, 108, 116)[k]
        for t, m, _, d in play('giants', t0, beat, -12, v):
            add(t, d, m, v, 'giant', FASOLT if k % 2 == 0 else FAFNER)
            if d >= 0.3:                                    # the heavy beats are stamps
                add(t, 0.4, 'C1', v + 8, 'stamp', FASOLT if (t - t0) % (4 * beat) < 2 * beat else FAFNER)
    for t, m, v, d in play('giants_authority', T_AUTH, BEAT * 1.1, -12, 104):
        part = 'step' if t >= T_AUTH + 8 * BEAT * 1.1 - 0.01 else 'auth'
        add(t, d, m, v, part, FASOLT)
    tr = play('treaties', T_TREATY, BEAT * 1.1, 0, 100)
    top = {}
    for t, m, v, d in tr:
        top[t] = max(top.get(t, 0), m)
    for t, m, v, d in tr:
        add(t, d, m, v, 'treaty' if m == top[t] else 'treatybass' if m < note('C3') else 'treatyharm', WOTAN)
    for t, m, v, d in play('spear', T_SPEAR, BEAT, 0, 112):
        add(t, d, m, v, 'spear', WOTAN)
    add(T_SPEAR + 6.2, 1.6, 'Bb1', 84, 'roll')
    for t, m, v, d in play('fafner', T_FAF, BEAT * 0.82, 0, 92):
        add(t, d, m, v, 'fafner', FAFNER)
    for i, (b, d, m) in enumerate(APPLE_TUNE):
        add(T_APPLE + b * BEAT, d * BEAT, m, 90, 'apple', i)
    for t, m, v, d in play('freia_love', T_APPLE + 1.0, BEAT * 1.4, 0, 70, line='melody'):
        add(t, d, m, v, 'love', FREIA)
    add(T_ADV - 1.8, 1.8, 'C2', 90, 'roll')
    for m in ('C2', 'G2', 'C3', 'Eb3', 'G3'):               # the brass swell under their march
        add(T_ADV, T_CRY + 1.0 - T_ADV, m, 92, 'swell')
    add(D - 4.0, 4.0, 'A1', 100, 'roll')
    for b, d, m in CRY:
        add(T_CRY + b * BEAT, d * BEAT, m, 108, 'cry', FREIA)
    for m in ('A3', 'C#4', 'E4', 'A4'):
        add(T_CRY, D - T_CRY, m, 90, 'trem')
    add(T_CRY + 6.6, 0.9, 'D3', 100, 'call')                # far off, a horn: her brothers have heard
    add(T_CRY + 7.6, 1.6, 'G3', 104, 'call')
    return sorted(N, key=lambda e: e[0])


def follow(target, rate):
    x = np.empty_like(target)
    x[0], v = target[0], 0.0
    for f in range(1, len(target)):
        w = rate[f]
        v += (w * w * (target[f] - x[f - 1]) - 2 * w * v) * DT
        x[f] = x[f - 1] + v * DT
    return x


def choreography(G):
    """Per frame: the gods (Wotan, Fricka, Freia), the giants (Fasolt, Fafner), and the spear's reach."""
    F = nframes(D)
    t = np.arange(F) * DT
    N = compose()
    gods = np.zeros((3, F))
    gods[WOTAN] = at(G, 'Left', 0.75) + 1.5 * np.sin(2 * np.pi * (t + T0) / 3.1)
    gods[FRICKA] = at(G, 'Left', 0.45) + 1.5 * np.sin(2 * np.pi * (t + T0) / 3.7)
    gods[FREIA] = at(G, 'Left', 0.55) + (3 + 5 * smoothstep(T_CRY, T_CRY + 1, t)) * np.sin(
        2 * np.pi * (t + T8) * 2.3)                     # hiding, trembling, as RG08 left her

    tgt = np.zeros((2, F))
    rate = np.full((2, F), 2.5)
    home = [at(G, 'Right', 0.55), at(G, 'Right', 0.8)]
    dest = [at(G, 'Porch Right', 0.5), at(G, 'Porch Right', 0.85)]
    for k in range(2):
        tgt[k] = home[k] + 2 * np.sin(2 * np.pi * (t + T0) / 4.0 + np.pi * k)
    stamps = [(e[0], e[5]) for e in N if e[4] == 'stamp']
    for ts, who in stamps:                              # a lurch toward the gods with each stamp
        m = (t >= ts - 0.15) & (t < ts + 0.3)
        tgt[who][m] -= 18
    adv = [s for s in stamps if s[0] >= T_ADV]
    for k in range(2):
        mine = [s[0] for s in adv if s[1] == k]
        for i, ts in enumerate(mine):
            m = t >= ts - 0.1
            tgt[k][m] = home[k] + (dest[k] - home[k]) * (i + 1) / len(mine) + 2 * np.sin(2 * np.pi * (t[m] + T0) / 4.0 + np.pi * k)
            rate[k][(t >= ts - 0.1) & (t < ts + 0.5)] = 7.0
    giants = np.array([follow(tgt[k], rate[k]) for k in range(2)])

    w0 = gods[WOTAN][0]
    spear_end = np.full(F, w0)
    sp = [e[0] for e in N if e[4] == 'spear']
    far = at(G, 'Porch Front', 1.0)
    for i, ts in enumerate(sp):
        spear_end[t >= ts] = w0 + (far - w0) * (i + 1) / len(sp)
    spear_end = follow(spear_end, np.full(F, 14.0))
    return dict(t=t, gods=gods, giants=giants, spear=spear_end)


def render(G, seed=9):
    rng = np.random.default_rng(seed)
    F = nframes(D)
    out = np.zeros((F, G.N, 3))
    d = G.pd
    S = mountain(G)
    C = choreography(G)
    N = compose()
    tw = Flicker(rng, G.N, 3.0, 9.0)

    stamps = [(e[0], e[5], e[3]) for e in N if e[4] == 'stamp']
    steps = [e[0] for e in N if e[4] == 'step']
    giant_notes = np.array(sorted(e[0] for e in N if e[4] in ('giant', 'auth', 'step', 'fafner')))
    treaty = np.array([e[0] for e in N if e[4] == 'treaty'])
    spear = np.array([e[0] for e in N if e[4] == 'spear'])
    faf = np.array([e[0] for e in N if e[4] == 'fafner'])
    apples = [(e[0], e[5]) for e in N if e[4] == 'apple']
    apos = np.array([at(G, *a) for a in APPLES])
    cry = np.array([e[0] for e in N if e[4] == 'cry'])

    def last(arr, t, tau, span=2.0):
        i = int(np.searchsorted(arr, t, side='right')) - 1
        return float(np.exp(-(t - arr[i]) / tau)) if i >= 0 and t - arr[i] < span else 0.0

    sparks = []
    for f in range(F):
        t = f * DT
        g = C['giants'][:, f]
        wp = C['gods'][WOTAN][f]

        # the mountaintop: meadow, cloud, the rosy glow, the castle brightening with Wotan's treaties
        glory = 1 + 0.15 * smoothstep(T_TREATY, T_TREATY + 3, t) * (1 - smoothstep(T_SPEAR + 6, T_SPEAR + 10, t))
        fr = scenery(S, t, glory + 0.12 * last(treaty, t, 0.6))
        menace(fr, S, g.min())

        # Freia, Fricka, Wotan
        fp = C['gods'][FREIA][f]
        flare = 0.8 * last(cry, t, 0.35) + 0.3 * smoothstep(T_APPLE, T_APPLE + 2, t) * (1 - smoothstep(T_ADV, T_ADV + 3, t))
        freia_light(fr, S, fp, t, flare)
        god_light(fr, S, C['gods'][FRICKA][f], FRI)
        wf = last(treaty, t, 0.5) + 0.8 * last(spear, t, 0.35)
        god_light(fr, S, wp, WOT, 0.78 + 0.25 * wf, 0.32)
        fr += light(WHITE, 0.3 * wf * np.exp(-((d - wp) / 8) ** 2))

        # the giants, and every stamp: a dull flash, a ripple toward the gods, a shudder through the house
        gp = last(giant_notes, t, 0.3)
        giant(fr, S, g[FASOLT], GREY, gp)
        giant(fr, S, g[FAFNER], OCHRE, gp)
        shudder = 0.0
        for ts, who, v in stamps:
            if ts <= t < ts + 1.6:
                shudder = max(shudder, stomp(fr, S, t - ts, g[who], GCOL[who], min(v / 120, 1.0)))
        for ts in steps:                                    # each step of the falling line pushes toward the gods
            if ts <= t < ts + 1.6:
                age = t - ts
                q = g[FASOLT] - 900 * smoothstep(0, 1.6, age)
                fr += light(GREY, 0.85 * (1 - age / 1.6) * np.exp(-((d - q) / 70) ** 2) * (d < g[FASOLT]))

        # Wotan's treaties: blue bands from him; the spear, a steel line drawn note by note
        if T_TREATY <= t < T_SPEAR + 2:
            for ts in treaty[(treaty <= t) & (treaty > t - 3)]:
                age = t - ts
                r = 30 + 380 * age ** 0.8
                fr += light(WOT, 0.75 * (1 - age / 3) * np.exp(-((np.abs(d - wp) - r) / 50) ** 2))
        se = C['spear'][f]
        sp = last(spear, t, 0.35)
        hold = smoothstep(T_SPEAR - 0.2, T_SPEAR + 0.3, t) * (1 - 0.8 * smoothstep(T_SPEAR + 7, T_SPEAR + 11, t))
        if hold > 0:
            line = (d >= wp - 6) & (d <= se)
            fr += light(SPEAR, hold * (0.62 + 0.35 * sp) * line * (0.85 + 0.15 * tw(t)))
            fr += light(WHITE, hold * (0.5 + 0.5 * sp) * np.exp(-((d - se) / 10) ** 2))
        tip = smoothstep(T_TREATY, T_TREATY + 2, t)          # he takes up the spear, and keeps it at his side
        fr += light(SPEAR, 0.55 * tip * np.exp(-((d - (wp + 18)) / 7) ** 2))

        # the golden apples in the orchard: each lights on its note of the apple tune
        for ta, k in apples:
            if t >= ta:
                a = smoothstep(ta, ta + 0.25, t)
                fl = np.exp(-(t - ta) / 0.3)
                fr += light(APPLE, a * (0.62 + 0.5 * fl + 0.06 * np.sin(2 * np.pi * ((t + T0) / 2.3 + k / 5))) *
                            np.exp(-((d - apos[k]) / 7) ** 2))
                fr += light(LEAF, a * 0.55 * np.exp(-((d - apos[k] - 11) / 5) ** 2))
                if T_CRY <= t:                              # they tremble when she cries
                    fr += light(APPLE, 0.25 * last(cry, t, 0.3) * np.exp(-((d - apos[k]) / 14) ** 2))
        if T_FAF <= t < T_ADV + 1:                          # Fafner's tendril reaching for them
            reach = smoothstep(T_FAF, T_ADV - 1, t) * (1 - smoothstep(T_ADV - 0.5, T_ADV + 1, t))
            q = g[FAFNER] - reach * (g[FAFNER] - apos.max() - 40)
            fpk = last(faf, t, 0.3)
            ten = (d <= g[FAFNER]) & (d >= q)
            fr += light(OCHRE, reach * (0.4 + 0.35 * fpk) * ten * (0.6 + 0.4 * np.sin(2 * np.pi * (d / 70 + t * 0.8))))
            fr += light(OCHRE, reach * (0.5 + 0.3 * fpk) * np.exp(-((d - q) / 14) ** 2))

        # Freia's cry: pink sparks over the left of the house
        if abs(t - T_CRY) < DT / 2 or any(abs(t - c) < DT / 2 for c in cry[2::2]):
            n = 40
            sparks.append(dict(t0=t, p=np.full(n, fp), v=rng.choice([-1, 1], n) * rng.uniform(100, 600, n)))
        for s in sparks:
            age = t - s['t0']
            if age > 2.5:
                continue
            q = s['p'] + s['v'] * (1 - np.exp(-age / 0.6)) * 0.6
            sg = np.exp(-((d[:, None] - q[None, :]) / 9) ** 2).max(axis=1)
            fr += light(FRE, 1.1 * np.exp(-age / 0.9) * sg * (0.7 + 0.3 * tw(t)))
        fr *= 1 - 0.3 * shudder
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

    def pan_g(k, t):
        return pan_at(np.interp(t, C['t'], C['giants'][k]))

    def pan_god(k, t):
        return pan_at(np.interp(t, C['t'], C['gods'][k]))

    for name, gain, rev in (('brass', 0.24, 0.3), ('low', 0.24, 0.18), ('strings', 0.2, 0.32), ('winds', 0.22, 0.35),
                            ('perc', 0.27, 0.22), ('harp', 0.24, 0.4), ('fx', 0.1, 0.2)):
        M.bus(name, gain=gain, reverb=rev)
    tuba = M.sampler('Brass/Tuba/sus/*.wav', tune=-12)
    tubst = M.sampler('Brass/Tuba/stac/*.wav', tune=-12)
    tbn = M.sampler('Brass/Tenor Trombone/sus/*.wav', tune=-12)
    horn = M.sampler('Brass/F Horn/sus/*.wav', tune=-12)
    cb = M.sampler('Strings/Solo Contrabass/SusNV/*.wav', tune=-12)
    pizz = M.sampler('Strings/Solo Contrabass/Pizz/*.wav', tune=-12)
    trem = M.sampler('Strings/Cello Section/trem/*.wav', tune=-12)
    vtrem = M.sampler('Strings/Violin Section/Trem/*.wav', tune=-12)
    vn = M.sampler('Strings/Violin Section/susVib/*.wav', tune=-12)
    fl = M.sampler('Woodwinds/Flute/susvib/*.wav', tune=-12)
    bsn = M.sampler('Woodwinds/Bassoon/sus/*.wav', tune=-12)
    harp = M.sampler('Strings/Harp/*.wav')
    timp = M.hits('Percussion/Timpani/Timpani1_Hit*.wav')
    roll = M.hits('Percussion/Timpani/Rolls/*.wav')
    bd = M.hits('Percussion/BDrumNewhit_v[4-7]*.wav')
    crash = M.hits('Percussion/cymbal-crash1_mf*.wav')

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

    wp = pan_god(WOTAN, 0)
    for t, d, m, v, part, who in compose():
        if part == 'pedal':
            hold('low', trem, m + 12, t, t + d, v, 0.5, rise=1.0, fall=2.0, gain=0.6)
            hold('low', cb, m, t, t + d, v, 0.5, rise=1.0, fall=2.0, gain=0.6)
        elif part == 'giant':
            pa = pan_g(who, t)
            M.add('brass', (tbn if who == FASOLT else tuba).play(m + 12 * (who == FASOLT), v, dur=d * 1.1,
                                                                release=0.2), t, 0.9, pa)
            M.add('low', tubst.play(m, v), t, 0.7, pa)
        elif part == 'stamp':
            pa = pan_g(who, t)
            M.add('perc', timp.play(v, pitch=-5), t, 1.0, pa)
            M.add('perc', bd.play(v), t, 0.8, pa)
            M.add('low', pizz.play(m + 12, v), t, 0.8, pa)
        elif part in ('auth', 'step'):
            pa = pan_g(FASOLT, t)
            M.add('brass', tbn.play(m + 12, v, dur=d * 1.1, release=0.3), t, 1.0, pa)
            M.add('low', tuba.play(m, v - 10, dur=d * 1.1, release=0.3), t, 0.8, pa)
            if part == 'step':
                M.add('perc', timp.play(v - 6, pitch=-4), t, 0.8, pa)
        elif part == 'treaty':
            M.add('brass', tbn.play(m, v, dur=d, release=0.4), t, 1.0, wp)
            M.add('brass', horn.play(m, v - 14, dur=d, release=0.4), t, 0.5, wp + 0.1)
        elif part == 'treatyharm':
            M.add('brass', horn.play(m, v - 24, dur=d, release=0.4), t, 0.45, -0.2)
        elif part == 'treatybass':
            M.add('low', tuba.play(m, v - 10, dur=d, release=0.4), t, 0.8, wp)
        elif part == 'spear':
            pa = pan_at(np.interp(t, C['t'], C['spear']))
            M.add('brass', tbn.play(m, v, dur=d * 1.1, release=0.3), t, 1.0, pa)
            M.add('low', tuba.play(m - 12, v, dur=d * 1.1, release=0.3), t, 0.9, pa)
            M.add('low', cb.play(m - 12, v - 10, dur=d * 1.1, release=0.3), t, 0.6, pa)
            M.add('fx', whoosh(0.35, 3000, 800, 0.4, seed=int(t * 10)), t - 0.1, 0.6, pa)
        elif part == 'roll':
            M.add('perc', roll.play(v, dur=d), t, 0.6, 0.4)
        elif part == 'fafner':
            M.add('low', tuba.play(m, v, dur=d * 1.05, release=0.2), t, 1.0, pan_g(FAFNER, t))
            M.add('low', bsn.play(m + 12, v - 16, dur=d, release=0.2), t, 0.5, pan_g(FAFNER, t))
        elif part == 'apple':
            pa = pan_at(at(G, *APPLES[who]))
            M.add('winds', fl.play(m, v, dur=d * 1.1, release=0.3), t, 1.0, pa)
            M.add('harp', harp.play(m - 12, v), t, 0.9, pa)
        elif part == 'love':
            M.add('strings', vn.play(m, v, dur=d * 1.05, release=0.4), t, 0.7, pan_god(FREIA, t))
        elif part == 'cry':
            pa = pan_god(FREIA, t)
            M.add('strings', vn.play(m, v, dur=d * 1.05, release=0.3), t, 1.0, pa)
            M.add('winds', fl.play(m, v - 20, dur=d, release=0.3), t, 0.6, pa)
            if d > 0.8:
                M.add('perc', crash.play(80), t, 0.3, pa)
        elif part == 'trem':
            hold('strings', vtrem, m, t, t + d, v, -0.3, rise=4.0, fall=0.8, gain=0.6)
        elif part == 'swell':
            s = tuba if m < note('C3') else horn if m >= note('Eb3') else tbn
            hold('brass', s, m, t, t + d, v, 0.45, rise=d * 0.8, fall=0.6, gain=0.55)
        elif part == 'call':
            M.add('brass', horn.play(m, v, dur=d, release=0.8), t, 0.5, -0.85)
