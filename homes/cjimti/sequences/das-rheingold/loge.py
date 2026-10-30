"""Loge: the fire god arrives, and he can't keep still. Out of the flicker at the free end of the Right wing he
darts everywhere at once, one dart every second bar of his fire music, along Right, past the giants, across the
castle, round the gods and back: a flame of orange and yellow with a trail of embers behind it.

Wotan wants to know what he has found. He searched water, earth and air, and each phrase sends a ring of fire
racing round the entire house; nobody would give up love, and pink blossoms of light open all over the
roofline. Except one: "Nur einen sah ich, der sagte der Liebe ab", and a cold indigo shadow drains in from both
ends. He tells of the Rhine's daughters and their stolen gold, and the castle fades back to the river it came
from: teal water on the porch, a gold glow on the rock, gold sweeping out to both ends of the house on each of
his lines; and Alberich, the Nibelung, whose ring now circles the gold, bright toward the street, red turned
away. Then the giants act: "Hieher, Maid! In unsre Macht!" A long grey arm shoots out from Fasolt right across
the porch, a flash where it grabs Freia, and her pink is yanked back along the roofline to Porch Right, where
she struggles between the two giants, crying "Wehe!", while Donner and Froh flare up helplessly.

The music is Wagner's own, from Scene 2 of Das Rheingold as Solti's 1958 Vienna Philharmonic recording takes
it: Loge's entrance and fire music (bars 1184-1203), his report (1364-1367 and 1373-1389: "in Wasser, Erd' und
Luft", "Nur einen sah ich", "Des Rheines klare Kinder"), and the giants seizing Freia (1612-1623). The notes come
from the Wagner Ring Dataset's piano reduction (pixelhome/ring.py): Loge's flickering figuration on violins,
flutes and piccolo with the harp skittering after it, the love music on violins and clarinets, the Rhine on harp
and horns, the giants on tubas, trombones and basses. Like a staged production it adds what the lights show: a
rush of fire with every dart and a crackle that follows Loge around the house, a roaring whoosh round the house
for each searching ring, a heavy blow and a cymbal as Fasolt's arm seizes Freia, and the giants' stamps on the
bass drum.

compose() tags every note of the excerpt, choreography() every position; render() and score() read both."""
import numpy as np
from pixelhome.fx import DT, hexc, light, smoothstep, nframes, Flicker
from pixelhome.ring import Orchestra, excerpt, tidy, accents

CODE = 'RG11'
TITLE = 'Loge'
KIND = 'show'
DESCRIPTION = ('Loge, the god of fire, darts in and tells what he found when he searched the world: nobody will '
               'give up love, except Alberich, who stole the Rhinegold and made a ring of it. The giants listen, '
               'and decide they would rather have the gold. Until they get it, they take Freia.')
VOICEOVER = ('Here comes Loge, the god of fire, who never stands still and never quite tells the truth. '
             'He has news, and the giants are listening.')

EX = excerpt(__file__)                      # Scene 2: bars 1184-1203, 1364-1367, 1373-1389, 1612-1623
BAR = {int(m): t for m, t in EX['bars']}
D = EX['seconds']
DARTS = [BAR[b] for b in range(1184, 1202, 2)]          # Loge's fire, one dart every second bar
T_SETTLE = BAR[1202]
SEARCH = [BAR[1364] + 0.1, BAR[1366], BAR[1367] + 1.0]  # water, earth and air: a ring of fire round the house each
T_LOVE = BAR[1373]                          # ...nobody would give up love
T_RENOUNCE = 40.9                           # "Nur einen sah ich, der sagte der Liebe ab"
T_RHINE = 55.4                              # "Des Rheines klare Kinder"
T_GOLDCALL = T_RHINE
CRIES = [55.4, 59.9]                        # his lines about the Rhine's daughters: gold sweeps out
T_RING = 64.0                               # "der Nibelung, Nachtalberich"
T_GREED = BAR[1612]                         # the giants act
T_GRAB = 75.6                               # "Hieher, Maid!": Fasolt seizes her
T_HELD = 77.9                               # "Als Pfand folgst du uns jetzt"
T_WEHE = (83.05, 86.75)                     # Freia: "Wehe! Wehe! Weh!"
T0 = 160.0                                  # seconds since The Giants began: sways and drifts run on

WOTAN, FRICKA, FREIA, FROH, DONNER = 0, 1, 2, 3, 4
FASOLT, FAFNER = 0, 1
APPLES = [('Side', 0.62), ('Left', 0.12), ('Side', 0.8), ('Left', 0.3), ('Side', 0.93), ('Left', 0.05),
          ('Side', 0.7), ('Left', 0.22), ('Left', 0.36), ('Side', 0.86), ('Left', 0.17), ('Side', 0.98)]
DART_TO = [('Right', 0.35), ('Porch Right', 0.15), ('Porch Front', 0.5), ('Left', 0.9), ('Porch Front', 0.15),
           ('Right', 0.7), ('Porch Left', 0.35), ('Porch Front', 0.85), ('Porch Left', 0.75)]

WOT = hexc('#1a3cff')
SPEAR = hexc('#c8d8ff')
FRI = hexc('#ff9ad0')
FRE = hexc('#ff5a9a')
APPLE = hexc('#ffd040')
LEAF = hexc('#60d020')
GREY = hexc('#8090a0')
OCHRE = hexc('#c07a10')
VAL = hexc('#fff0c0')
DAWN0 = hexc('#2a3a6a')
DAWN1 = hexc('#6a5a8a')
WHITE = hexc('#ffffff')
STEEL = hexc('#a0c0ff')
FIRE0 = hexc('#ff5000')
FIRE1 = hexc('#ffb020')
DEEP = hexc('#065c70')
GREEN = hexc('#14c080')
GOLD = hexc('#ffaa00')
HOT = hexc('#fff0a0')
RED = hexc('#ff1800')
SHADOW = hexc('#1c1880')
GCOL = [GREY, OCHRE]
GODCOL = [WOT, FRI, FRE]


def at(G, seg, u):
    s = G.pd[G.seg[seg]]
    return float(s.min() + u * (s.max() - s.min()))


def rainbow(x):
    c = 0.5 + 0.5 * np.cos(2 * np.pi * (np.asarray(x)[..., None] - np.array([0.0, 1 / 3, 2 / 3])))
    return c ** 1.6


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
    """Every note of the excerpt, tagged: (time, seconds, midi, velocity, part, who). Loge's music is 'fire' (who =
    the dart); in the search the notes are 'amb'; the love music 'love'; the renunciation 'renounce'; the Rhine's
    right hand 'gold' and its left 'river'; Alberich's bars 'ring'; the giants' left hand 'giant' and right 'auth',
    with Freia's cry 'cry2'. 'race', 'cry' and 'stamp' mark moments for the lights and the stage; they make no
    sound."""
    N = []
    for t, d, m, v, h, trem in tidy(EX['notes']):
        if t < T_SETTLE:
            part, who = 'fire', max(0, int(np.searchsorted(DARTS, t, side='right')) - 1)
        elif t < T_LOVE:
            part, who = 'amb', None
        elif t < T_RENOUNCE:
            part, who = 'love', None
        elif t < T_RHINE:
            part, who = 'renounce', None
        elif t < T_RING:
            part, who = ('gold' if h == 0 else 'river'), None
        elif t < T_GREED:
            part, who = 'ring', None
        elif T_WEHE[0] <= t < T_WEHE[1] and h == 0:
            part, who = 'cry2', FREIA
        else:
            part, who = ('auth' if h == 0 else 'giant'), FASOLT
        N.append((t, d, m, v, part, who, trem))
    for k, t0 in enumerate(SEARCH):
        N.append((t0 + 0.4, 0.2, 60, 0, 'race', k, False))
    for t0 in CRIES:
        N.append((t0, 1.0, 60, 0, 'cry', None, False))
    for k, ts in enumerate(accents(EX['notes'], T_HELD, D, 70, 2, 0.75)):
        N.append((ts, 0.4, 24, 110, 'stamp', FASOLT if k % 2 == 0 else FAFNER, False))
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
    """Per frame: the gods (Wotan, Fricka, Freia, Froh, Donner), the giants, Loge, and Fasolt's arm."""
    F = nframes(D)
    t = np.arange(F) * DT
    N = compose()
    tgt = np.zeros((5, F))
    rate = np.full((5, F), 3.0)

    def set_(k, a, b, where, r):
        m = (t >= a) & (t < b)
        tgt[k][m] = where if np.ndim(where) == 0 else where[m]
        rate[k][m] = r

    set_(WOTAN, 0, D, at(G, 'Left', 0.75) + 1.5 * np.sin(2 * np.pi * (t + T0) / 3.1), 3.0)
    set_(FRICKA, 0, D, at(G, 'Left', 0.45) + 1.5 * np.sin(2 * np.pi * (t + T0) / 3.7), 3.0)
    set_(FROH, 0, D, at(G, 'Left', 0.65) + 2 * np.sin(2 * np.pi * (t + T0) / 2.2), 2.2)
    set_(DONNER, 0, D, at(G, 'Porch Left', 0.2) + 2 * np.sin(2 * np.pi * (t + T0) / 1.7), 5.0)
    held = at(G, 'Porch Right', 0.62)
    set_(FREIA, 0, D, at(G, 'Left', 0.55) + 3.2 * np.sin(2 * np.pi * (t + T8) * 2.3), 6.0)
    set_(FREIA, T_GRAB + 0.25, D, held + 14 * np.sin(2 * np.pi * (t + T0) / 0.6), 3.2)        # yanked away
    gods = np.array([follow(tgt[k], rate[k]) for k in range(5)])

    gt = np.zeros((2, F))
    grate = np.full((2, F), 2.5)
    home = [at(G, 'Porch Right', 0.5), at(G, 'Porch Right', 0.85)]
    for k in range(2):
        gt[k] = home[k] + 2 * np.sin(2 * np.pi * (t + T0) / 4.0 + np.pi * k)
    lean = smoothstep(T_GREED + 2, T_GREED + 5, t) * (1 - smoothstep(T_GRAB - 1, T_GRAB, t))
    gt[FASOLT] += 30 * lean
    gt[FAFNER] -= 30 * lean                                 # they lean in and confer
    gt[FASOLT] += -40 * smoothstep(T_GRAB - 0.6, T_GRAB, t) + 40 * smoothstep(T_GRAB + 0.3, T_GRAB + 1.5, t) \
        - 37 * smoothstep(T_HELD, T_HELD + 2, t)            # Fasolt lunges, hauls back, then holds at 0.4
    for ts, who in [(e[0], e[5]) for e in N if e[4] == 'stamp']:
        gt[who][(t >= ts - 0.15) & (t < ts + 0.3)] -= 14
    giants = np.array([follow(gt[k], grate[k]) for k in range(2)])

    lt = np.full(F, at(G, 'Right', 0.95))
    lrate = np.full(F, 3.0)
    for t0, dest in zip(DARTS, DART_TO):
        m = t >= t0
        lt[m] = at(G, *dest)
        lrate[(t >= t0) & (t < t0 + 1.0)] = 9.0
    lt[t >= T_SETTLE] = at(G, 'Porch Left', 0.6)
    wob = 18 * np.sin(2 * np.pi * (t + T0) * 0.9) + 8 * np.sin(2 * np.pi * (t + T0) * 2.3)
    loge = follow(lt, lrate) + wob * smoothstep(T_SETTLE, T_SETTLE + 2, t)

    reach = np.zeros(F)                                     # Fasolt's arm: out to Freia, then back with her
    fp = at(G, 'Left', 0.55)
    out_ = smoothstep(T_GRAB - 0.35, T_GRAB, t) * (1 - smoothstep(T_GRAB + 0.25, T_GRAB + 1.3, t))
    reach[:] = out_
    return dict(t=t, gods=gods, giants=giants, loge=loge, arm=reach, freia0=fp)


def render(G, seed=11):
    rng = np.random.default_rng(seed)
    F = nframes(D)
    out = np.zeros((F, G.N, 3))
    d = G.pd
    L = G.length
    pf = at(G, 'Porch Front', 0.5)
    S = mountain(G)
    C = choreography(G)
    N = compose()
    tw = Flicker(rng, G.N, 3.0, 9.0)
    fl = Flicker(rng, G.N, 4.0, 13.0)
    apos = np.array([at(G, *a) for a in APPLES])

    def times(*parts):
        return np.array(sorted(e[0] for e in N if e[4] in parts) or [-9.0])
    fire, love, gold = times('fire', 'flicker'), times('love'), times('gold')
    ring_t, gnotes, cry2 = times('ring'), times('fafner', 'giant', 'auth'), times('cry2')
    races = [e[0] for e in N if e[4] == 'race']
    cries = [(e[0], e[1]) for e in N if e[4] == 'cry']
    stamps = [(e[0], e[5], e[3]) for e in N if e[4] == 'stamp']
    nb = 26                                                 # pink blossoms of love, all over the house
    bpos = rng.uniform(0, L, nb)
    bt = np.sort(rng.uniform(T_LOVE, T_RENOUNCE, nb))
    rough = np.random.default_rng(9).uniform(0.45, 1.0, 60)

    def last(arr, t, tau, span=2.0):
        i = int(np.searchsorted(arr, t, side='right')) - 1
        return float(np.exp(-(t - arr[i]) / tau)) if i >= 0 and t - arr[i] < span else 0.0

    for f in range(F):
        t = f * DT
        g = C['giants'][:, f]
        gp = C['gods'][:, f]
        lp = C['loge'][f]

        # the mountaintop; the castle fades back into the river while Loge tells of the Rhine
        river = smoothstep(T_RHINE - 1, T_RHINE + 2, t) * (1 - smoothstep(T_GREED - 1, T_GREED + 3, t))
        cold = smoothstep(T_RENOUNCE, T_RENOUNCE + 3, t) * (1 - smoothstep(T_RHINE, T_RHINE + 3, t))
        reach = smoothstep(0, 1, cold) * (L / 2 + 300)
        shade = np.clip(np.maximum(smoothstep(reach, reach - 300, d), smoothstep(L - reach, L - reach + 300, d))
                        * cold, 0, 1) if cold > 0 else np.zeros(G.N)
        fr = scenery(S, t, 1 - 0.85 * river)
        fr *= (1 - 0.6 * shade)[:, None]
        fr += light(SHADOW, 0.32 * shade)
        if river > 0:
            w1 = 0.5 + 0.5 * np.cos(2 * np.pi * (d / 340 - 0.16 * t))
            w2 = 0.5 + 0.5 * np.cos(2 * np.pi * (d / 140 + 0.33 * t) + 1)
            near = np.exp(-((d - pf) / 520) ** 2) * (1 - 0.6 * shade)
            fr += light(DEEP, river * (0.42 + 0.15 * w1) * near) + light(GREEN, river * (0.12 + 0.3 * w1 * w2) * near)
            gc = last(gold, t, 0.3)
            fr += light(GOLD, river * (0.7 + 0.3 * gc) * np.exp(-((d - pf) / 40) ** 2))
            fr += light(HOT, river * (0.3 + 0.4 * gc) * np.exp(-((d - pf) / 15) ** 2))
            for tc, dc in cries:                            # gold sweeps out to both ends on the cry
                if tc <= t < tc + 1.5:
                    age = t - tc
                    rf = 1500 * smoothstep(0, 1.0, age)
                    fr += light(GOLD, 0.65 * (1 - age / 1.5) * np.exp(-((np.abs(d - pf) - rf) / 130) ** 2))
            rg = smoothstep(T_RING - 0.5, T_RING + 1.0, t)
            if rg > 0:
                rp = last(ring_t, t, 0.35)
                R = 380 - 100 * smoothstep(T_RING, T_GREED, t)
                th = 2 * np.pi * (np.arange(14) / 14 + 0.28 * (t - T_RING))
                q, depth = pf + R * np.cos(th), np.sin(th)
                gg = np.exp(-((d[:, None] - q[None, :]) / 24) ** 2)
                front = (gg * np.clip(depth, 0, 1)[None, :]).max(axis=1)
                back = (gg * np.clip(-depth, 0, 1)[None, :]).max(axis=1)
                fr += light(GOLD, river * rg * (0.95 + 0.4 * rp) * front) + light(RED, river * rg * (0.6 + 0.25 * rp) * back)
        menace(fr, S, g.min())

        # Freia, Fricka, Wotan
        protest = smoothstep(T_GRAB, T_GRAB + 0.3, t) * (1 - smoothstep(T_GRAB + 2, T_HELD + 4, t))
        flare = 0.5 * smoothstep(T_LOVE, T_LOVE + 2, t) * (1 - smoothstep(T_RENOUNCE - 1, T_RENOUNCE + 1, t)) + \
            0.9 * last(cry2, t, 0.3)
        freia_light(fr, S, gp[FREIA], t, flare)
        god_light(fr, S, gp[FRICKA], FRI)
        god_light(fr, S, gp[WOTAN], WOT, 0.78 + 0.25 * protest, 0.32)

        # the giants: gold glints come into their stone as they think of the hoard
        gn = last(gnotes, t, 0.3)
        giant(fr, S, g[FASOLT], GREY, gn)
        giant(fr, S, g[FAFNER], OCHRE, gn)
        greed = smoothstep(T_GREED, T_GREED + 4, t)
        if greed > 0:
            for k in range(2):
                body = smoothstep(48, 34, np.abs(d - g[k]))
                fr += light(GOLD, greed * 0.75 * body * (tw(t) > 1.0))
        shudder = 0.0
        for ts, who, v in stamps:
            if ts <= t < ts + 1.6:
                shudder = max(shudder, stomp(fr, S, t - ts, g[who], GCOL[who], min(v / 120, 1.0)))

        # the spear at Wotan's side, the apples in the orchard
        fr += light(SPEAR, (0.55 + 0.4 * protest) * np.exp(-((d - (gp[WOTAN] + 18)) / 7) ** 2))
        for k, q in enumerate(apos):
            fr += light(APPLE, (0.62 + 0.06 * np.sin(2 * np.pi * ((t + T0) / 2.3 + k / 5))) * np.exp(-((d - q) / 7) ** 2))
            fr += light(LEAF, 0.55 * np.exp(-((d - q - 11) / 5) ** 2))

        # Froh's rainbow and Donner's steel; as their sister is taken they flare up
        p = gp[FROH]
        fr += light(rainbow((d - p) / 90 + 0.15 * (t + T0)), (0.55 + 0.35 * protest) * np.exp(-((d - p) / 26) ** 2))
        p = gp[DONNER]
        power = 0.53 + 0.5 * protest
        fr += light(WHITE, power * np.exp(-((d - p) / 11) ** 2))
        fr += light(STEEL, power * (0.75 + 0.25 * tw(t)) * np.exp(-((d - p) / (32 + 30 * protest)) ** 2))

        # rings of fire racing round the house: the whole world searched
        for k, tr in enumerate(races):
            age = t - tr
            if 0 <= age < 3.2:
                o = C['loge'][int(tr / DT)]
                r = 800 * age
                dist = np.abs(d - o)
                band = (np.exp(-((dist - r) / 90) ** 2) + 0.7 * (dist < r) * np.exp(-(age - dist / 800) / 1.0)) * \
                    (1 - smoothstep(2.4, 3.2, age))
                hue = np.clip(0.5 + 0.5 * fl(t), 0, 1)[:, None]
                fr += light(FIRE0 * (1 - hue) + FIRE1 * hue, 0.95 * band * (0.65 + 0.35 * np.abs(tw(t))))
        # pink blossoms: love, everywhere he looked
        for i in range(nb):
            if bt[i] <= t < bt[i] + 4.0:
                age = t - bt[i]
                a = smoothstep(0, 0.5, age) * (1 - smoothstep(2.0, 4.0, age))
                fr += light(FRE, (0.75 + 0.3 * last(love, t, 0.4)) * a * np.exp(-((d - bpos[i]) / (12 + 10 * age)) ** 2))

        # the seizure: Fasolt's arm right across the porch to her, her pink dragged back along the roofline
        arm = C['arm'][f]
        if arm > 0:
            tip = g[FASOLT] + arm * (C['freia0'] - g[FASOLT])
            span = (d >= tip) & (d <= g[FASOLT])
            fr += light(GREY, 0.75 * arm * span * (0.7 + 0.3 * np.interp((d - tip) % 400 - 200,
                                                                          np.linspace(-200, 200, 60), rough)))
            fr += light(WHITE, 0.9 * arm * np.exp(-((d - tip) / 16) ** 2))
        if T_GRAB <= t < T_GRAB + 0.5:
            fr += light(FRE, 0.5 * np.exp(-(t - T_GRAB) / 0.12) * np.ones(G.N))
        if T_GRAB + 0.2 <= t < T_GRAB + 2.0:
            q = gp[FREIA]
            trail = (d >= min(q, C['freia0'])) & (d <= max(q, C['freia0']))
            fr += light(FRE, 0.55 * (1 - smoothstep(T_GRAB + 0.6, T_GRAB + 2.0, t)) * trail *
                        np.exp(-np.abs(d - q) / 300))

        for t0 in DARTS:                                    # the run he lands on catches fire for a moment
            if t0 + 0.35 <= t < t0 + 1.5:
                run = G.seg_of[int(np.argmin(np.abs(d - np.interp(t0 + 0.6, C['t'], C['loge']))))]
                fr += light(FIRE0, 0.6 * np.exp(-(t - t0 - 0.35) / 0.3) * (G.seg_of == run) * (0.6 + 0.4 * np.abs(fl(t))))

        # Loge: a flame, darting, embers behind him
        hue = np.clip(0.5 + 0.5 * fl(t), 0, 1)[:, None]
        col = FIRE0 * (1 - hue) + FIRE1 * hue
        ff = last(fire, t, 0.12)
        trail = np.zeros(G.N)
        for j, lag in enumerate(range(2, 30, 3)):
            q = C['loge'][max(f - lag, 0)]
            trail = np.maximum(trail, np.exp(-((d - q) / 20) ** 2) * (1 - j / 10.0))
        moving = min(1.0, abs(lp - C['loge'][max(f - 6, 0)]) / 60)
        fr += light(col, (0.85 + 0.3 * ff) * np.exp(-((d - lp) / (16 + 6 * ff)) ** 2) * (0.75 + 0.25 * np.abs(fl(t))))
        fr += light(col, 0.75 * moving * trail * (0.5 + 0.5 * np.abs(tw(t))))
        sp = (rng.random(G.N) < 0.03 + 0.1 * ff) * np.exp(-((d - lp) / (60 + 80 * moving)) ** 2)
        fr += light(FIRE1, 0.9 * sp)
        fr *= 1 - 0.3 * shudder
        out[f] = fr
    return np.clip(out, 0, 1)


def score(M, G):
    """Wagner's notes, orchestrated from the piano reduction by section of the scene, with Loge's fire, the
    searching rings and the giants' violence on the stage."""
    from pixelhome.audio import whoosh
    order = np.argsort(G.pd)
    xs, ds = G.pos[order, 0], G.pd[order]
    x0, x1 = xs.min(), xs.max()

    def pan_at(dd):
        x = np.interp(dd, ds, xs)
        return float(0.85 * (2 * (x - x0) / (x1 - x0) - 1))

    C = choreography(G)

    def pan_g(k, t):
        return pan_at(np.interp(t, C['t'], C['giants'][k]))

    def pan_loge(t):
        return pan_at(np.interp(t, C['t'], C['loge']))

    o = Orchestra(M, level=3.3)
    # the fire leads while Loge darts in; it backs right off under his report, the love music and the Rhine, and
    # comes back for the giants' violence
    o.effects([(0.0, 0.0), (T_SETTLE, 0.0), (T_SETTLE + 1.5, -5.0), (T_LOVE, -10.0), (T_GREED - 1.0, -10.0),
               (T_GRAB - 0.6, 0.0), (D, 0.0)])
    for t, d, m, v, part, who, trem in compose():
        if v == 0:
            continue
        if trem:
            o.play('violins trem' if m >= 55 else 'cellos trem', m, t, d, v, None, 0.5)
        elif part == 'fire':                                    # his flickering figuration
            lp = pan_loge(t)
            if m >= 60:
                o.play('violins', m, t, d, v - 4, lp, 0.5)
                o.play('flutes' if m < 79 else 'piccolo', m, t, 0.1, v - 12, lp, 0.35)
                if d < 0.25:
                    o.play('harp', m, t, d, v - 10, -lp, 0.3)
            elif m >= 48:
                o.play('violas', m, t, d, v - 4, lp * 0.5, 0.45)
                o.play('bassoons', m, t, d, v - 14, 0.0, 0.25)
            else:
                o.play('cellos', m, t, d, v, -0.2, 0.55)
                o.play('basses', m - 12 if m >= 40 else m, t, d, v - 8, 0.2, 0.4)
        elif part in ('amb', 'renounce'):
            if m >= 60:
                o.play('violins', m, t, d, v, 0.25, 0.5)
                if d >= 0.5:
                    o.play('clarinets', m - 12, t, d, v - 10, -0.2, 0.35)
            elif m >= 48:
                o.play('horns' if d >= 0.4 else 'violas', m, t, d, v, -0.3, 0.6)
                if part == 'renounce' and d >= 0.4:
                    o.play('trombones', m, t, d, v - 8, 0.1, 0.45)
            else:
                o.play('cellos', m, t, d, v, -0.2, 0.6)
                o.play('basses', m - 12 if m >= 40 else m, t, d, v - 8, 0.2, 0.45)
        elif part == 'love':                                    # Freia's love music
            if m >= 55:
                o.play('violins', m, t, d, v + 6, 0.2, 0.65)
                o.play('clarinets', m - 12, t, d, v - 6, -0.2, 0.35)
            else:
                o.play('cellos', m, t, d, v, -0.2, 0.55)
        elif part == 'gold':                                    # the Rhine: harp and flutes, the gold's glint
            o.play('harp', m, t, d, v + 8, 0.0, 0.55)
            if d >= 0.3:
                o.play('flutes', m, t, d, v - 4, -0.3, 0.4)
        elif part == 'river':
            if m >= 50:
                o.play('horns', m, t, d, v + 6, -0.25, 0.6)
            else:
                o.play('cellos', m, t, d, v, -0.2, 0.55)
                o.play('basses', m - 12 if m >= 40 else m, t, d, v - 8, 0.2, 0.4)
        elif part == 'ring':                                    # Alberich: low, dark
            if m >= 55:
                o.play('oboes' if d < 0.4 else 'clarinets', m, t, d, v, 0.2, 0.45)
            else:
                o.play('bassoons', m, t, d, v, 0.0, 0.45)
                o.play('cellos', m, t, d, v - 6, -0.2, 0.45)
        elif part in ('giant', 'auth', 'cry2'):                 # the giants: tubas, trombones, basses
            gp = pan_g(FASOLT, t)
            if part == 'cry2':
                o.play('violins', m, t, d, v + 10, gp, 0.65)
                o.play('oboes', m, t, d, v, gp, 0.45)
            elif part == 'auth':
                o.play('violins', m, t, d, v, gp, 0.5)
                if d >= 0.4:
                    o.play('horns', m - 12, t, d, v - 6, gp, 0.45)
            elif m >= 48:
                o.play('trombones', m, t, d, v, gp, 0.7)
                o.play('horns', m, t, d, v - 8, gp, 0.4)
            else:
                o.play('tuba', m, t, d, v, gp, 0.7)
                o.play('basses', m - 12 if m >= 40 else m, t, d, v - 6, gp, 0.5)
                o.play('cellos', m, t, d, v - 6, gp, 0.45)

    # Loge's fire: a rush with every dart, a crackle that follows him round the house
    for k, t0 in enumerate(DARTS):
        o._sfx(whoosh(0.7, 500, 4000, 0.9, seed=k + 11)[0], t0 - 0.1, 0.8, pan_loge(t0 + 0.4))
    darts = np.array(DARTS)

    def blaze(tt):                                          # louder just after each dart
        i = np.clip(np.searchsorted(darts, tt, side='right') - 1, 0, len(darts) - 1)
        return 0.3 + 0.55 * np.exp(-np.clip(tt - darts[i], 0, None) / 0.5) * (tt >= darts[0])

    o.fire(0.0, T_SETTLE + 2.0, blaze, pan=pan_loge, crackle=20.0, seed=11)
    o.fire(T_SETTLE, T_LOVE + 2.0, 0.18, pan=pan_loge, crackle=8.0, seed=12)
    # the searching rings: a rush round the house
    for k, t0 in enumerate(SEARCH):
        o._sfx(whoosh(2.4, 200, 2500, 0.9, seed=k + 21)[0], t0 + 0.3, 0.8, lambda t, t0=t0: -0.8 + 0.7 * (t - t0))
        o.hit('cymbal swell', t0 - 1.2, 80, gain=0.25)
    # the giants: Fasolt's arm seizes Freia, then they stamp
    gp = pan_g(FASOLT, T_GRAB)
    o.hit('timpani roll', T_GRAB - 1.5, 96, pitch=-4, gain=0.45, pan=gp)
    o.boom(T_GRAB, gp, 1.0)
    o.hit('crash', T_GRAB, 118, gain=0.55, pan=gp)
    o._sfx(whoosh(0.6, 3000, 400, 0.9, seed=31)[0], T_GRAB - 0.45, 0.8, gp)
    for t, d, m, v, part, who, trem in compose():
        if part == 'stamp':
            o.hit('bass drum', t, 116, gain=0.6, pan=pan_g(who, t))
            o.hit('timpani', t, 104, pitch=-6, gain=0.4, pan=pan_g(who, t))
