"""The Gods Grow Old: the giants take their hostage home. Fafner leads, Fasolt hauls Freia between them, and to
their stamping motif (Donington 58), heavier now and slower, they tramp down Porch Right and along the Right
wing and out of its free end, each stamp shaking the run under them. Freia's pink is dragged away jerk by jerk,
streaming behind her, while her music (Donington 7) breaks up in the violins and fades with her.

Then a pale mist comes down. It drifts in over the whole house and the colour drains out of everything: the
gods' blue, rose, rainbow and steel slide toward grey and dim, Valhalla's battlements lose their gleam, and in
the orchard the golden apples wither one by one, gold to brown to nothing. The Twilight of the Gods (Donington
4) sounds slowly in the low strings and winds, twice, sinking. Only Loge is untouched: his flicker (Donington
20a) and his ambivalent motif (21a) skip through the grey, darting among the gods with a laugh of piccolos,
the only colour left on the house.

Wotan pulls himself together. His treaties (Donington 14) rise once more in the trombones, his blue comes back a
little, and he and Loge set out for Nibelheim. At the middle of Porch Front a fissure cracks open, yellow-brown
sulphur vapour welling up out of it in slow puffs over a low rumble, and the two of them walk along the porch
to its edge and go down into it, his blue and Loge's flame sinking into the vapour to a falling chromatic run.
Far below, three faint taps on an anvil. The other gods stand grey and dim on the wings, the battlements are
dimmed, and the vapour keeps rising.

The music is Wagner's own, from Scene 2 of Das Rheingold as Solti's 1958 Vienna Philharmonic recording takes
it: the giants leaving with Freia ("für immer folge sie uns!", her "Rettet! Helft!", bars 1636-1649), Loge
seeing the mist fall ("Trügt mich ein Nebel?", 1676-1685), Wotan's resolve ("Auf, Loge! Hinab mit mir!",
1768-1771), and the start of the descent to Nibelheim (1808-1821). The notes come from the Wagner Ring
Dataset's piano reduction (pixelhome/ring.py): the giants on tubas, trombones and basses, Freia's music on
violins and oboes, the twilight of the gods on bassoons, horns and cellos, Loge's flickers on piccolo, flutes
and harp, Wotan's treaty on trombones, the descent on the full orchestra. Like a staged production it adds what
the lights show: the giants' stamps on bass drum and timpani, a thin cold air as the mist comes down, the
fissure cracking open with a great blow and a deep rumble, hissing sulphur with each puff of vapour, a rush
downward as Wotan and Loge sink, and three far-off taps on an anvil.

compose() tags every note of the excerpt, choreography() every position; render() and score() read both."""
import numpy as np
from pixelhome.fx import DT, hexc, light, smoothstep, nframes, Flicker
from pixelhome.ring import Orchestra, excerpt, tidy, accents

CODE = 'RG12'
TITLE = 'The Gods Grow Old'
KIND = 'show'
DESCRIPTION = ('The giants carry Freia away, and without her golden apples the gods begin to grow old: a pale '
               'mist falls and their colours fade to grey. Only Loge still flickers. Wotan decides to go down '
               'to Nibelheim, Alberich\'s underground kingdom, and take the gold himself.')
VOICEOVER = ('The giants have taken Freia, and the golden apples are going with her. '
             'Watch the colour drain out of the gods.')

EX = excerpt(__file__)                      # Scene 2: bars 1636-1649, 1676-1685, 1768-1771, 1808-1821
BAR = {int(m): t for m, t in EX['bars']}
D = EX['seconds']
T_GO = 0.6                                  # the giants set off with her
T_MIST = BAR[1676]                          # "Trügt mich ein Nebel?": the mist falls
T_MOCK = 36.5                               # "Wie bang und bleich verblüht ihr so bald!": Loge mocks them
T_RESOLVE = BAR[1768]                       # "Auf, Loge! Hinab mit mir!"
T_CRACK = BAR[1808]                         # the descent begins: the fissure opens
T_WALK = BAR[1810]
T_DOWN = BAR[1815]                          # they go down
T_TAPS = BAR[1819]
TAPS = [BAR[1819], BAR[1820], BAR[1821]]
T0 = 240.0                                  # seconds since The Giants began: sways and drifts run on

WOTAN, FRICKA, FROH, DONNER = 0, 1, 2, 3
FASOLT, FAFNER = 0, 1
APPLES = [('Side', 0.62), ('Left', 0.12), ('Side', 0.8), ('Left', 0.3), ('Side', 0.93), ('Left', 0.05),
          ('Side', 0.7), ('Left', 0.22), ('Left', 0.36), ('Side', 0.86), ('Left', 0.17), ('Side', 0.98)]
WITHER = [T_MIST + 2.0 + 1.7 * k for k in range(12)]       # one apple after another
MOCKS = [T_MOCK, 40.0, 45.2, 49.7]           # his lines
MOCK_TO = [('Left', 0.9), ('Left', 0.5), ('Porch Left', 0.1), ('Porch Left', 0.55)]
WOT = hexc('#1a3cff')
SPEAR = hexc('#c8d8ff')
FRI = hexc('#ff9ad0')
FRE = hexc('#ff5a9a')
APPLE = hexc('#ffd040')
LEAF = hexc('#60d020')
BROWN = hexc('#6a4018')
GREY = hexc('#8090a0')
OCHRE = hexc('#c07a10')
DUST = hexc('#6a5a48')
VAL = hexc('#fff0c0')
DAWN0 = hexc('#2a3a6a')
DAWN1 = hexc('#6a5a8a')
MIST = hexc('#a8acb8')
WHITE = hexc('#ffffff')
STEEL = hexc('#a0c0ff')
FIRE0 = hexc('#ff5000')
FIRE1 = hexc('#ffb020')
SULPHUR = hexc('#c8a020')
FUME = hexc('#6a5014')
GCOL = [GREY, OCHRE]


def at(G, seg, u):
    s = G.pd[G.seg[seg]]
    return float(s.min() + u * (s.max() - s.min()))


def rainbow(x):
    c = 0.5 + 0.5 * np.cos(2 * np.pi * (np.asarray(x)[..., None] - np.array([0.0, 1 / 3, 2 / 3])))
    return c ** 1.6


def fade(c, s):
    """Colour c drained toward grey by s (0..1)."""
    c = np.asarray(c, float)
    g = c.mean(axis=-1, keepdims=True) * np.array([0.92, 0.96, 1.05])
    return c * (1 - s) + g * s


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
    """Every note of the excerpt, tagged: (time, seconds, midi, velocity, part, who, tremolo). The giants' left hand
    is 'giant', Freia's right hand 'freia'; in the mist the left hand's long notes are the twilight of the gods
    ('downfall'), its others 'downbass', the right hand's quick notes Loge's 'flicker', its long ones 'mistnote';
    Wotan's resolve is 'treaty' (its top line), 'treatyharm' and 'treatybass'; the descent is 'descent', its right
    hand 'fall' once they go down. 'stamp', 'crack', 'puff', 'step', 'laugh' and 'anvil' mark moments for the
    lights and the stage."""
    N = []
    tops = {}
    for t, d, m, v, h, trem in tidy(EX['notes']):
        if T_RESOLVE <= t < T_CRACK:
            tops[round(t, 2)] = max(tops.get(round(t, 2), 0), m)
    for t, d, m, v, h, trem in tidy(EX['notes']):
        if t < T_MIST:
            part, who = ('freia', None) if h == 0 else ('giant', FASOLT if t < 8 else FAFNER)
        elif t < T_RESOLVE:
            if h == 0:
                part = 'flicker' if d < 0.3 else 'mistnote'
            else:
                part = 'downfall' if d >= 0.5 else 'downbass'
            who = None
        elif t < T_CRACK:
            part = 'treaty' if m == tops[round(t, 2)] else 'treatybass' if m < 48 else 'treatyharm'
            who = WOTAN
        else:
            part, who = ('fall' if h == 0 and t >= T_DOWN else 'descent'), None
        N.append((t, d, m, v, part, who, trem))
    for k, ts in enumerate(accents([n for n in EX['notes'] if n[4] == 1], T_GO, T_MIST - 2, 60, 1, 1.1)):
        N.append((ts, 0.4, 24, 110, 'stamp', FAFNER if k % 2 == 0 else FASOLT, False))
    N.append((T_CRACK, 1.2, 26, 0, 'crack', None, False))
    for k in range(5):
        N.append((T_CRACK + 2.5 + 3.0 * k, 2.5, 38, 0, 'puff', k, False))
    walk = [BAR[b] + x * (BAR[b + 1] - BAR[b]) for b in range(1810, 1815) for x in (0.0, 0.5)]
    for ts in walk:                                         # their footsteps along the porch
        N.append((ts, 0.5, 38, 0, 'step', None, False))
    for t0 in MOCKS:
        N.append((t0 + 1.6, 0.3, 84, 0, 'laugh', None, False))
    for ts in TAPS:
        N.append((ts, 0.5, 58, 0, 'anvil', None, False))
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
    """Per frame: the gods (Wotan, Fricka, Froh, Donner), Loge, the giants and Freia."""
    F = nframes(D)
    t = np.arange(F) * DT
    N = compose()
    L = G.length
    pf = at(G, 'Porch Front', 0.5)
    tgt = np.zeros((4, F))
    rate = np.full((4, F), 3.0)

    def set_(k, a, b, where, r):
        m = (t >= a) & (t < b)
        tgt[k][m] = where if np.ndim(where) == 0 else where[m]
        rate[k][m] = r

    set_(WOTAN, 0, D, at(G, 'Left', 0.75) + 1.5 * np.sin(2 * np.pi * (t + T0) / 3.1), 3.0)
    steps = [e[0] for e in N if e[4] == 'step']
    for i, ts in enumerate(steps):                                   # Wotan walks to the fissure
        n = len(steps)
        set_(WOTAN, ts, D, at(G, 'Left', 0.75) + (pf - 20 - at(G, 'Left', 0.75)) * (i + 1) / n, 4.0)
    set_(FRICKA, 0, D, at(G, 'Left', 0.45) + 1.5 * np.sin(2 * np.pi * (t + T0) / 3.7), 3.0)
    set_(FROH, 0, D, at(G, 'Left', 0.65) + 2 * np.sin(2 * np.pi * (t + T0) / 2.2), 2.2)
    set_(FROH, T_MIST + 2, D, at(G, 'Left', 0.62) + 4 * np.sin(2 * np.pi * (t + T0) / 2.6), 0.6)
    set_(DONNER, 0, D, at(G, 'Porch Left', 0.2) + 2 * np.sin(2 * np.pi * (t + T0) / 1.7), 5.0)
    set_(DONNER, T_MIST + 4, D, at(G, 'Left', 0.85) + 3 * np.sin(2 * np.pi * (t + T0) / 2.3), 0.5)   # he falls back
    gods = np.array([follow(tgt[k], rate[k]) for k in range(4)])

    # the giants march Freia out of the free end of Right, a step per stamp
    stamps = [(e[0], e[5]) for e in N if e[4] == 'stamp']
    start = {FASOLT: at(G, 'Porch Right', 0.4), FAFNER: at(G, 'Porch Right', 0.85)}
    gt = np.zeros((2, F))
    for k in range(2):
        mine = [s[0] for s in stamps if s[1] == k]
        gt[k] = start[k] + 2 * np.sin(2 * np.pi * (t + T0) / 4.0 + np.pi * k)
        end = L + 260 + 120 * (k == FAFNER)
        for i, ts in enumerate(mine):
            gt[k][t >= ts - 0.1] = start[k] + (end - start[k]) * (i + 1) / len(mine)
    giants = np.array([follow(gt[k], np.full(F, 6.0)) for k in range(2)])
    jerk = 14 * np.sin(2 * np.pi * (t + T0) / 0.6) * (1 - smoothstep(6, 10, t))
    freia = 0.45 * giants[FASOLT] + 0.55 * giants[FAFNER] - 15 + jerk

    lt = np.full(F, at(G, 'Porch Left', 0.6))
    lrate = np.full(F, 3.0)
    for t0, dest in zip(MOCKS, MOCK_TO):
        lt[t >= t0] = at(G, *dest)
        lrate[(t >= t0) & (t < t0 + 1.0)] = 9.0
    lt[t >= T_RESOLVE + 2] = at(G, 'Porch Left', 0.75)
    lt[t >= T_WALK] = pf + 20
    lrate[t >= T_WALK] = 1.0
    wob = 18 * np.sin(2 * np.pi * (t + T0) * 0.9) + 8 * np.sin(2 * np.pi * (t + T0) * 2.3)
    loge = follow(lt, lrate) + wob * (1 - 0.7 * smoothstep(T_WALK, T_DOWN, t))
    return dict(t=t, gods=gods, giants=giants, freia=freia, loge=loge)


def render(G, seed=12):
    rng = np.random.default_rng(seed)
    F = nframes(D)
    out = np.zeros((F, G.N, 3))
    d = G.pd
    L = G.length
    pf = at(G, 'Porch Front', 0.5)
    C = choreography(G)
    N = compose()
    porch = np.isin(G.seg_of, ['Porch Left', 'Porch Front', 'Porch Right'])
    merlon = 0.35 + 0.65 * smoothstep(-0.35, 0.35, np.sin(2 * np.pi * d / 30))
    rs = np.random.default_rng(9)
    meadow = np.interp(d, np.linspace(0, L, 40), rs.uniform(0, 1, 40))
    shim = Flicker(rng, G.N, 0.3, 1.2)
    tw = Flicker(rng, G.N, 3.0, 9.0)
    fl = Flicker(rng, G.N, 4.0, 13.0)
    murk = [np.interp(d, np.linspace(-400, L + 400, 70), rng.uniform(0, 1, 70)) for _ in range(2)]
    apos = np.array([at(G, *a) for a in APPLES])
    S = mountain(G)

    def times(*parts):
        return np.array(sorted(e[0] for e in N if e[4] in parts) or [-9.0])
    gnotes, freia_n = times('giant'), times('freia')
    loge_n, laughs, treaty = times('flicker', 'amb'), times('laugh'), times('treaty', 'resolve')
    stamps = [(e[0], e[5], e[3]) for e in N if e[4] == 'stamp']
    puffs = [e[0] for e in N if e[4] == 'puff']

    def last(arr, t, tau, span=2.0):
        i = int(np.searchsorted(arr, t, side='right')) - 1
        return float(np.exp(-(t - arr[i]) / tau)) if i >= 0 and t - arr[i] < span else 0.0

    for f in range(F):
        t = f * DT
        g = C['giants'][:, f]
        gp = C['gods'][:, f]
        lp = C['loge'][f]
        old = smoothstep(T_MIST, T_MOCK, t)                 # how far the gods have faded
        resolve = 0.35 * smoothstep(T_RESOLVE, T_RESOLVE + 3, t)
        mist = smoothstep(T_MIST - 1, T_MIST + 8, t)
        grey = smoothstep(T_MIST - 1, T_MOCK, t)            # the bright mountaintop giving way to the grey one

        # the meadow going under a pale mist; the battlements losing their gleam
        fr = np.zeros((G.N, 3))
        if grey < 1:
            fr += (1 - grey) * scenery(S, t)
        if grey > 0:
            u = np.clip(meadow + 0.25 * np.sin(2 * np.pi * (d / 900 - (t + T0) / 23)), 0, 1)
            dawn = DAWN0 * (1 - u[:, None]) + DAWN1 * u[:, None]
            bed = light(fade(dawn, 0.55 * mist), (0.38 + 0.05 * shim(t)) * (1 - 0.2 * mist) * (~porch + 0.3 * porch))
            drift = 0.5 * np.interp(d - 40 * t, d, murk[0], period=L) + 0.5 * np.interp(d + 25 * t, d, murk[1], period=L)
            bed += light(MIST, smoothstep(0, 1, mist) * (0.1 + 0.2 * drift ** 2) * (0.9 + 0.1 * shim(t)))
            bed += light(fade(VAL, 0.6 * old), 0.36 * (1 - 0.45 * old) * merlon * porch * (1 + 0.05 * shim(t)))
            fr += grey * bed
        menace(fr, S, g.min())

        # Freia dragged off between the giants, her pink streaming behind her
        fp = C['freia'][f]
        here = smoothstep(L + 30, L - 20, fp)
        if here > 0:
            freia_light(fr, S, fp, t, last(freia_n, t, 0.3), here=here)
        trail = np.zeros(G.N)
        for j, lag in enumerate(range(4, 120, 6)):
            q = C['freia'][max(f - lag, 0)]
            trail = np.maximum(trail, np.exp(-((d - q) / 22) ** 2) * (1 - j / 20.0))
        fr += light(FRE, 0.6 * trail * (1 - smoothstep(9, 13, t)))

        # Fricka and Wotan, draining toward grey
        dim = 1 - 0.2 * old
        gone = 1 - smoothstep(T_DOWN, T_DOWN + 2.5, t)
        tr = last(treaty, t, 0.5)

        def god(col, p, w, a, glow, wash=0.0):
            now = np.zeros((G.N, 3))
            if old < 1:
                god_light(now, S, p, col, 0.78 * gone, wash)
            was = light(fade(col, 0.85 * old), a * np.exp(-((d - p) / w) ** 2) + 0.2 * a * np.exp(-((d - p) / glow) ** 2))
            fr[:] += (1 - old) * now + old * was
        god(FRI, gp[FRICKA], 9, 0.8 * dim, 26)
        if gone > 0:
            p = gp[WOTAN] if t < T_DOWN else pf - 20
            god(WOT, p, 20 * (1 - 0.6 * smoothstep(T_DOWN, T_DOWN + 2.5, t)), (0.8 * dim + resolve + 0.3 * tr) * gone, 70,
                0.32)
            if resolve > 0:                                 # his own blue comes back, a little
                fr += light(WOT, resolve * gone * np.exp(-((d - p) / 16) ** 2))

        # the giants marching off, each stamp a dull flash, a ripple and a shudder
        gn = last(gnotes, t, 0.3)
        giant(fr, S, g[FASOLT], GREY, gn)
        giant(fr, S, g[FAFNER], OCHRE, gn)
        shudder = 0.0
        for ts, who, v in stamps:
            if ts <= t < ts + 1.6:
                shudder = max(shudder, stomp(fr, S, t - ts, g[who], GCOL[who], min(v / 120, 1.0)))

        # the spear at his side; the apples wither one by one
        if gone > 0:
            p = gp[WOTAN] if t < T_DOWN else pf - 20
            fr += light(fade(SPEAR, 0.5 * old), (0.55 * dim + resolve) * gone * np.exp(-((d - (p + 18 * gone)) / 7) ** 2))
        for k, q in enumerate(apos):
            w = smoothstep(WITHER[k], WITHER[k] + 1.2, t)
            fade_k = 1 - smoothstep(WITHER[k] + 1.0, WITHER[k] + 3.5, t)
            col = APPLE * (1 - w) + BROWN * w
            pulse = 0.25 * np.exp(-(t - WITHER[k]) / 0.3) if t >= WITHER[k] else 0.0
            twinkle = 0.06 * np.sin(2 * np.pi * ((t + T0) / 2.3 + k / 5)) * (1 - w)
            fr += light(col, (0.62 + twinkle + pulse) * fade_k * np.exp(-((d - q) / 7) ** 2))
            fr += light(LEAF * (1 - w) + BROWN * w, 0.55 * fade_k * (1 - 0.5 * w) * np.exp(-((d - q - 11) / 5) ** 2))

        # Froh and Donner, greying
        p = gp[FROH]
        fr += light(fade(rainbow((d - p) / 90 + 0.15 * (t + T0)), 0.85 * old), (0.55 + 0.07 * old) * dim *
                    np.exp(-((d - p) / 26) ** 2))
        p = gp[DONNER]
        fr += light(fade(WHITE, 0.3), 0.53 * dim * np.exp(-((d - p) / 11) ** 2))
        fr += light(fade(STEEL, 0.85 * old), 0.53 * dim * (0.75 + 0.25 * tw(t)) * np.exp(-((d - p) / 32) ** 2))

        # the fissure at the middle of Porch Front: a crack, then sulphur vapour welling up in puffs
        if t >= T_CRACK:
            age = t - T_CRACK
            op = smoothstep(0, 2.0, age)
            fr *= (1 - 0.6 * op * np.exp(-((d - pf) / 18) ** 2))[:, None]       # the dark crack itself
            edge = np.exp(-((np.abs(d - pf) - 20 - 10 * op) / 9) ** 2)
            fr += light(SULPHUR, op * (0.75 + 0.25 * fl(t)) * edge)
            if age < 1.0:
                fr += light(SULPHUR, 0.6 * np.exp(-age / 0.2) * np.exp(-((d - pf) / 260) ** 2))
            vap = np.exp(-((d - pf) / (90 + 40 * op)) ** 2) * (0.6 + 0.4 * np.abs(tw(t)))
            fr += light(FUME * 1.5, 0.75 * op * vap)
            for tp in puffs:                                # each puff rolls out and thins
                a = t - tp
                if 0 <= a < 4.0:
                    r = 30 + 220 * a ** 0.7
                    fr += light(SULPHUR * 0.85, 0.65 * (1 - a / 4.0) * np.exp(-((np.abs(d - pf) - r) / 45) ** 2)
                                * (0.7 + 0.3 * np.abs(fl(t))))

        # Loge: the only colour left; laughing, then down into the vapour with Wotan
        lg = 1 - smoothstep(T_DOWN + 0.4, T_DOWN + 2.8, t)
        if lg > 0:
            hue = np.clip(0.5 + 0.5 * fl(t), 0, 1)[:, None]
            col = FIRE0 * (1 - hue) + FIRE1 * hue
            ff = last(loge_n, t, 0.12) + 0.6 * last(laughs, t, 0.2)
            q = lp if t < T_DOWN else pf + 20
            trail = np.zeros(G.N)
            for j, lag in enumerate(range(2, 30, 3)):
                qq = C['loge'][max(f - lag, 0)]
                trail = np.maximum(trail, np.exp(-((d - qq) / 20) ** 2) * (1 - j / 10.0))
            moving = min(1.0, abs(lp - C['loge'][max(f - 6, 0)]) / 60)
            fr += light(col, lg * (0.85 + 0.3 * ff) * np.exp(-((d - q) / ((16 + 6 * ff) * (0.4 + 0.6 * lg))) ** 2)
                        * (0.75 + 0.25 * np.abs(fl(t))))
            fr += light(col, lg * 0.75 * moving * trail * (0.5 + 0.5 * np.abs(tw(t))))
            sp = (rng.random(G.N) < 0.03 + 0.12 * ff) * np.exp(-((d - q) / (60 + 120 * ff)) ** 2)
            fr += light(FIRE1, lg * 0.9 * sp)
        if T_DOWN <= t < T_DOWN + 3.0:                      # they sink: a last flare down in the vapour
            a = t - T_DOWN
            fr += light(SULPHUR, 0.5 * np.sin(np.pi * a / 3.0) * np.exp(-((d - pf) / 60) ** 2))
        fr *= 1 - 0.3 * shudder
        out[f] = fr
    return np.clip(out, 0, 1)


def score(M, G):
    """Wagner's notes, orchestrated from the piano reduction scene by scene, with the giants' stamps, the mist,
    the fissure and the anvils far below on the stage."""
    from pixelhome.audio import SR, whoosh
    order = np.argsort(G.pd)
    xs, ds = G.pos[order, 0], G.pd[order]
    x0, x1 = xs.min(), xs.max()

    def pan_at(dd):
        x = np.interp(min(dd, G.length), ds, xs)
        return float(0.85 * (2 * (x - x0) / (x1 - x0) - 1))

    C = choreography(G)
    pf = pan_at(at(G, 'Porch Front', 0.5))

    def pan_g(k, t):
        return pan_at(np.interp(t, C['t'], C['giants'][k]))

    def pan_god(k, t):
        return pan_at(np.interp(t, C['t'], C['gods'][k]))

    def pan_loge(t):
        return pan_at(np.interp(t, C['t'], C['loge']))

    def away(k, t):
        """Gain as the giants leave out of the end of Right."""
        x = np.interp(t, C['t'], C['giants'][k]) - G.length
        return float(np.clip(1 - x / 400, 0.15, 1))

    o = Orchestra(M, level=3.0)
    # the mist's air is felt as it falls, then sits under Loge's lines and Wotan's treaty; the fissure and the
    # descent are the staging's moment
    o.effects([(0.0, 0.0), (T_MIST, -2.0), (T_MOCK - 1.0, -8.0), (T_CRACK - 0.6, -8.0), (T_CRACK, 0.0), (D, 0.0)])
    N = compose()
    for t, d, m, v, part, who, trem in N:
        if v == 0:
            continue
        if part == 'giant':                                     # the giants tramp off
            gp, a = pan_g(who, t), away(who, t)
            if m < 48:
                o.play('tuba', m, t, d, v, gp, 0.75 * a)
                o.play('basses', m - 12 if m >= 40 else m, t, d, v - 6, gp, 0.5 * a)
            else:
                o.play('trombones', m, t, d, v, gp, 0.65 * a)
                o.play('cellos', m - 12, t, d, v - 8, gp, 0.4 * a)
        elif part == 'freia':                                   # her music, dragged away
            fp = pan_at(np.interp(t, C['t'], C['freia']))
            if trem:
                o.play('violins trem', m, t, d, v, fp, 0.5)
            else:
                o.play('violins', m, t, d, v + 4, fp, 0.6)
                if d >= 0.3:
                    o.play('oboes', m, t, d, v - 6, fp, 0.4)
        elif part in ('downfall', 'downbass'):                  # the twilight of the gods, sinking
            o.play('bassoons', m, t, d, v, -0.1, 0.5)
            o.play('cellos', m, t, d, v - 4, -0.25, 0.5)
            if part == 'downfall':
                o.play('horns', m + 12 if m < 48 else m, t, d, v - 6, 0.25, 0.45)
        elif part == 'flicker':                                 # Loge, the only colour left
            lp = pan_loge(t)
            o.play('piccolo' if m >= 79 else 'flutes', m, t, 0.1, v, lp, 0.45)
            o.play('harp', m - 12, t, d, v - 8, lp, 0.35)
        elif part == 'mistnote':
            if trem:
                o.play('violins trem', m, t, d, v - 6, 0.2, 0.4)
            else:
                o.play('clarinets', m, t, d, v, 0.2, 0.45)
                o.play('flutes', m, t, d, v - 10, -0.3, 0.3)
        elif part in ('treaty', 'treatyharm', 'treatybass'):    # "Auf, Loge! Hinab mit mir!"
            wp = pan_god(WOTAN, t)
            if part == 'treaty':
                o.play('trombones', m, t, d, v + 6, wp, 0.8)
                o.play('horns', m, t, d, v - 8, wp, 0.45)
            elif part == 'treatybass':
                o.play('tuba', m, t, d, v, wp, 0.6)
                o.play('basses', m - 12 if m >= 40 else m, t, d, v - 6, wp, 0.45)
            else:
                o.play('horns', m, t, d, v - 4, wp, 0.45)
        else:                                                   # the descent: the whole orchestra
            if trem:
                o.play('violins trem' if m >= 55 else 'violas trem' if m >= 48 else 'cellos trem', m, t, d, v, pf, 0.5)
            elif m >= 60:
                o.play('violins', m, t, d, v, pf + 0.2, 0.55)
                if m >= 74:
                    o.play('flutes', m, t, 0.1, v - 10, -0.3, 0.3)
            elif m >= 48:
                o.play('horns' if d >= 0.4 else 'violas', m, t, d, v, pf - 0.2, 0.55)
                if d >= 0.4:
                    o.play('trombones', m, t, d, v - 8, pf, 0.4)
            else:
                o.play('cellos', m, t, d, v, pf, 0.6)
                o.play('basses', m - 12 if m >= 40 else m, t, d, v - 6, pf, 0.45)
                if d >= 0.5:
                    o.play('tuba', m, t, d, v - 8, pf, 0.45)

    # the stage
    for t, d, m, v, part, who, trem in N:
        if part == 'stamp':                                     # each giant's stamp shakes the run
            gp, a = pan_g(who, t), away(who, t)
            o.hit('bass drum', t, 118, gain=0.7 * a, pan=gp)
            o.hit('timpani', t, 110, pitch=-7, gain=0.45 * a, pan=gp)
        elif part == 'puff':                                    # sulphur hissing up out of the crack
            o._sfx(o._noise(0, 1200, 7000, 400 + who, n=int(2.4 * SR)) *
                   np.sin(np.linspace(0, np.pi, int(2.4 * SR))) ** 2, t, 0.25, pf)
        elif part == 'step':                                    # their footsteps toward the edge
            o.hit('timpani', t, 70, pitch=-9, gain=0.25, pan=pan_god(WOTAN, t))
        elif part == 'anvil':                                   # far below: Nibelheim
            o.hit('anvil', t, 64, gain=0.35, pan=pf)
    o.wind(T_MIST - 1.0, T_RESOLVE + 2.0, 0.35, pan=0.0, seed=12)              # the mist's cold air
    o.hit('cymbal swell', T_MIST - 2.0, 70, gain=0.3)
    o.boom(T_CRACK, pf, 1.0)                                                     # the fissure cracks open
    o.hit('gong scrape', T_CRACK + 0.1, 110, gain=0.5, pan=pf)
    o.thunder(T_CRACK + 0.2, 0.3, pf, 0.9)
    o._sfx(whoosh(2.2, 2500, 150, 0.9, seed=40)[0], T_DOWN - 0.2, 0.8, pf)        # they sink into the vapour
