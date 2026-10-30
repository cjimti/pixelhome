"""The Giants: the castle is finished and its builders have come for their wage. Fasolt (stone grey) and Fafner
(ochre) stand on the Right wing as two great rough masses. Across the porch Valhalla gleams white-gold as
battlements; the wings are a dim dawn meadow.

The music is Wagner's own, as Solti's 1958 Vienna Philharmonic recording takes it: Fasolt's "vertragen ist's",
Wotan's "Seid ihr bei Trost mit eurem Vertrag?", the giants' fury breaking out fortissimo in crashing octaves,
and Fasolt's "Was sagst du? Ha! Sinnst du Verrat? Verrat am Vertrag?" over the scales of the treaty (bars
1021-1035); then Fafner's "Goldene Äpfel wachsen in ihrem Garten" over the golden apples' theme, the gods
withering without them, and the giants' decision, "Ihrer Mitte drum sei sie entführt!" (1110-1127). The notes
come from the Wagner Ring Dataset's piano reduction (pixelhome/ring.py): Wotan's answer on horns and
trombones over tuba and basses; the giants' fury on trombones, horns, tuba and basses with timpani; the treaty
scales on trombones and tuba; the golden apples on horns with a harp glinting; the gods' decline on
clarinets, bassoons and violas over the cellos; the decision on the full brass. The reduction carries the
dynamics in one hand only, so each note takes the loudest velocity around it. Every heavy beat of the giants'
music is a stamp, on the bass drum.

Each stamp shakes the whole run they stand on: a flash of their colour, a lurch toward the gods, a tremor
through the pixels and a ring of dust rolling out along the roofline. Wotan (deep blue, on Left) answers with
rings of blue swelling out from him; then the treaty's scales draw his spear out, a steel white-blue line
running from him down Porch Left and across the front of the castle, between the gods and the giants. Fafner
tells of the apples, and with each note of their theme a golden apple with a green leaf lights up in the
orchard on the left wing while an ochre tendril reaches out from him toward them. Then the giants advance onto
Porch Right, a stamp per step, the battlements dimming under their bulk, while Freia (pink, hiding between
Fricka and Wotan) trembles.

compose() holds every note, choreography() every position; render() and score() read both."""
import numpy as np
from pixelhome.fx import DT, hexc, light, smoothstep, nframes, Flicker
from pixelhome.ring import Orchestra, excerpt

CODE = 'RG09'
TITLE = 'The Giants'
KIND = 'show'
DESCRIPTION = ('The giants Fasolt and Fafner stamp in to collect their wage for building Valhalla: the goddess '
               'Freia. Wotan points to his treaties and his spear, but Fafner knows what the gods would lose '
               'with her, the golden apples that keep them young.')
VOICEOVER = ('The castle is built, and the builders want paying. '
             'Two giants have come for their wage, and every step they take shakes the ground.')

EX = excerpt(__file__)                      # bars 1021-1035, 1110-1127, Solti 1958
BAR = {int(m): t for m, t in EX['bars']}
SEG = [sg['start'] for sg in EX['segments']] + [EX['seconds']]
T_TREATY = 0.0                              # Wotan: "Seid ihr bei Trost mit eurem Vertrag?"
T_STR = [BAR[1024]]                         # the giants' fury
T_AUTH = BAR[1032]                          # Fasolt: "Verrat am Vertrag?"
T_SPEAR = BAR[1033]                         # the treaty's scales: the spear
T_FAF = SEG[1]                              # Fafner: the apples
T_APPLE = BAR[1111]
T_DECLINE = BAR[1118]                       # without them the gods wither
T_ADV = BAR[1124]                           # the giants advance onto Porch Right
T_CRY = 1e9                                 # (Freia's cry is the next scene's)
D = EX['seconds']
LEVEL = 2.65
T0 = 0.0                                    # seconds since The Giants began: sways and drifts run on

FASOLT, FAFNER = 0, 1
WOTAN, FRICKA, FREIA = 0, 1, 2
APPLES = [('Side', 0.62), ('Left', 0.12), ('Side', 0.8), ('Left', 0.3), ('Side', 0.93), ('Left', 0.05),
          ('Side', 0.7), ('Left', 0.22), ('Left', 0.36), ('Side', 0.86), ('Left', 0.17), ('Side', 0.98)]

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
    """Every note of the excerpt, tagged: (time, seconds, midi, velocity, part, who). Wotan's answer is 'treaty'
    (the right hand) over 'treatybass'; the giants' fury and their advance are 'giant', with a 'stamp' on each heavy
    beat; Fasolt's line is 'auth' over the treaty scales, 'spear'; Fafner's apples are 'apple' (who = which apple)
    over 'fafner', and the gods' decline is 'fafner' too."""
    N = []
    stamp_k = 0
    apple_k = 0
    last_apple = -1.0
    for t, d, m, v, h in sorted(EX['notes']):
        if t < T_STR[0]:
            N.append((t, d, m, v, 'treaty' if h == 0 else 'treatybass', WOTAN))
        elif t < T_AUTH or t >= T_ADV:
            N.append((t, d, m, v, 'giant', FASOLT if int(t / 2.2) % 2 == 0 else FAFNER))
        elif t < T_SPEAR:
            N.append((t, d, m, v, 'auth' if h == 0 else 'step', FASOLT))
        elif t < SEG[1]:
            N.append((t, d, m, v, 'auth' if h == 0 else 'spear', FASOLT if h == 0 else WOTAN))
        elif t < T_DECLINE and h == 0 and t >= T_APPLE:
            if apple_k < len(APPLES) and t - last_apple > 0.4:
                N.append((t, d, m, v, 'apple', apple_k))
                apple_k, last_apple = apple_k + 1, t
            else:
                N.append((t, d, m, v, 'apple2', None))
        else:
            N.append((t, d, m, v, 'fafner', FAFNER))
    beats = sorted({round(e[0], 3) for e in N if e[4] == 'giant' and e[2] <= 52 and e[1] >= 0.25})
    for t in beats:
        N.append((t, 0.4, 24, 116 if t >= T_ADV else 108, 'stamp', (FASOLT, FAFNER)[stamp_k % 2]))
        stamp_k += 1
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
        pale = smoothstep(T_DECLINE, T_DECLINE + 5, t) * (1 - smoothstep(T_ADV, T_ADV + 2, t))
        if pale > 0:                                        # without the apples: the gods turn grey and old
            near = np.exp(-((d - C['gods'][FREIA][f]) / 420) ** 2)
            mist = 0.5 + 0.5 * np.sin(2 * np.pi * (d / 180 - 0.25 * t))
            fr *= (1 - 0.55 * pale * near)[:, None]
            fr += light(hexc('#9a9aa8'), pale * near * (0.22 + 0.12 * mist))
        fr *= 1 - 0.3 * shudder
        out[f] = fr
    return np.clip(out, 0, 1)


def score(M, G):
    """Wagner's notes, orchestrated from the piano reduction; the giants' tread on the bass drum and timpani."""
    order = np.argsort(G.pd)
    xs, ds = G.pos[order, 0], G.pd[order]
    x0, x1 = xs.min(), xs.max()

    def pan_at(dd):
        x = np.interp(dd, ds, xs)
        return float(0.85 * (2 * (x - x0) / (x1 - x0) - 1))

    C = choreography(G)

    def pan_g(k, t):
        return pan_at(min(np.interp(t, C['t'], C['giants'][k]), G.length))

    def pan_god(k, t):
        return pan_at(np.interp(t, C['t'], C['gods'][k]))

    o = Orchestra(M, level=LEVEL)
    N = compose()
    tv = np.array([(e[0], e[3]) for e in N if e[4] != 'stamp'])

    def loud(t, v):                                         # the reduction's dynamics sit in one hand
        near = tv[np.abs(tv[:, 0] - t) < 0.6, 1]
        return int(max(v, near.max() - 8)) if len(near) else v

    for t, d, m, v, part, who in N:
        if part == 'stamp':
            continue
        v = loud(t, v)
        if part == 'treaty':                                # Wotan's answer
            o.play('horns', m, t, d, v, pan_god(WOTAN, t), 0.65)
            if m < 60:
                o.play('trombones', m, t, d, v - 6, pan_god(WOTAN, t), 0.5)
        elif part == 'treatybass':
            o.play('tuba', m, t, d, v - 4, 0.0, 0.55)
            o.play('basses', m, t, d, v - 8, 0.2, 0.45)
        elif part == 'giant':                               # their fury, their advance
            gp = pan_g(who, t)
            if m >= 55:
                o.play('horns', m, t, d, v, gp, 0.6)
                o.play('violins', m, t, d, v - 10, gp, 0.3)
            elif m >= 45:
                o.play('trombones', m, t, d, v, gp, 0.75)
            else:
                o.play('tuba', m + 12 if m < 33 else m, t, d, v, gp, 0.7)
                o.play('basses', m, t, d, v - 6, gp, 0.55)
        elif part == 'auth':                                # Fasolt's line
            o.play('bassoons', m, t, d, v, pan_g(FASOLT, t), 0.55)
            o.play('violas', m, t, d, v - 6, pan_g(FASOLT, t), 0.4)
        elif part == 'step':
            o.play('cellos', m, t, d, v, pan_g(FASOLT, t), 0.6)
            o.play('basses', m, t, d, v - 6, 0.2, 0.45)
        elif part == 'spear':                               # the treaty's scales
            o.play('trombones', m + 12 if m < 45 else m, t, d, v + 6, pan_god(WOTAN, t), 0.7)
            o.play('tuba', m, t, d, v, 0.0, 0.55)
        elif part in ('apple', 'apple2'):                   # the golden apples
            o.play('horns', m, t, d, v + 10, -0.5, 0.6)
            o.play('harp', m + 12, t, d, v, -0.6, 0.45)
        elif part == 'fafner':
            if t < T_DECLINE:
                o.play('cellos', m, t, d, v + 4, pan_g(FAFNER, t), 0.55)
                o.play('basses', m - 12 if m >= 40 else m, t, d, v - 4, 0.2, 0.4)
            elif m >= 55:
                o.play('clarinets', m, t, d, v + 6, pan_g(FAFNER, t), 0.5)
                o.play('violas', m - 12 if m >= 60 else m, t, d, v - 4, pan_g(FAFNER, t), 0.4)
            else:
                o.play('bassoons', m, t, d, v + 6, pan_g(FAFNER, t), 0.5)
                o.play('cellos', m, t, d, v, -0.2, 0.45)
    for t, d, m, v, part, who in N:                         # their tread
        if part == 'stamp':
            gp = pan_g(who, t)
            o.hit('bass drum', t, 124, gain=0.65 if t >= T_ADV else 0.5, pan=gp)
            o.hit('timpani', t, 110, pitch=-8, gain=0.4, pan=gp)
    o.hit('crash', T_STR[0], 112, gain=0.5, pan=0.6)
    o.boom(T_SPEAR, pan_god(WOTAN, T_SPEAR), 0.45)
    o.hit('cymbal swell', T_ADV - 3.0, 100, gain=0.45, pan=0.6)
    o.hit('crash', T_ADV, 118, gain=0.55, pan=0.6)
