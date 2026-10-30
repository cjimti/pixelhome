"""Loge: the fire god arrives, and he can't keep still. Out of the flicker at the free end of the Right wing he
darts everywhere at once to his fire music (Donington 20, the restless chromatic climb, and the flickering
20a): along Right, past the giants, across the castle, round the gods and back, a flame of orange and yellow
with a trail of embers behind it, piccolo, violins and harp skittering after him.

Wotan wants to know what he has found. Loge's answer comes to his ambivalent motif (Donington 21a): he has
searched the whole world, and each phrase sends a ring of fire racing round the entire house. Nowhere, in
water, earth or air, would anyone give up love: Freia's love music (Donington 6) rises in the violins and pink
blossoms of light open one by one all over the roofline. Except one. He tells of the Rhine, and the castle
fades back to the river it came from: teal water on the porch, a gold glow on the rock in the middle of it,
the Rhinemaidens' cry (Donington 31) far off in the woodwinds and the gold's call (Donington 44) on a muted horn,
gold sweeping out to both ends of the house. Alberich has stolen it and forged a ring (Donington 8): beads
circle the gold, bright toward the street, red turned away. To do it he gave up love (Donington 76), and a cold
indigo shadow drains in from both ends.

The giants have been listening. Fafner's crawling motif (Donington 57) climbs in the tubas and gold glints
start to show in the giants' stone; they lean in and confer. Then they want the gold instead, and they take
Freia as a hostage until evening: a long grey arm shoots out from Fasolt right across the porch, a flash where
it grabs her, and her pink is yanked back along the roofline to Porch Right, where she struggles between the
two giants while Donner and Froh flare up helplessly and the giants' authority (Donington 59) descends in the
brass. Loge, watching it all, flickers at the back of Porch Left.

compose() holds every note, choreography() every position; render() and score() read both."""
import numpy as np
from pixelhome.audio import note
from pixelhome.fx import DT, hexc, light, smoothstep, nframes, Flicker
from pixelhome.leitmotifs import play

CODE = 'RG11'
TITLE = 'Loge'
KIND = 'show'
DESCRIPTION = ('Loge, the god of fire, darts in and tells what he found when he searched the world: nobody will '
               'give up love, except Alberich, who stole the Rhinegold and made a ring of it. The giants listen, '
               'and decide they would rather have the gold. Until they get it, they take Freia.')
VOICEOVER = ('Here comes Loge, the god of fire, who never stands still and never quite tells the truth. '
             'He has news, and the giants are listening.')

BEAT = 0.5
DARTS = [0.4, 1.9, 3.4, 4.9, 6.4, 7.9, 9.4, 10.9, 12.4]   # Loge's fire, one dart per statement
T_SETTLE = 14.0
SEARCH = [16.0, 20.5, 25.0]                 # "I searched the world": a ring of fire round the house each time
T_LOVE = 29.0                               # ...nobody would give up love
T_RHINE = 36.0                              # except one: the Rhinegold
T_GOLDCALL = 38.0
T_CRY = 42.0
T_RING = 48.0
T_RENOUNCE = 55.0
T_GREED = 61.5                              # the giants want it
T_GRAB = 70.0                               # they seize Freia
T_HELD = 72.0
D = 80.0
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
    """Every note: (time, seconds, midi, velocity, part, who)."""
    N = []

    def add(t, d, m, v, part, who=None):
        N.append((float(t), float(d), note(m) if isinstance(m, str) else int(m), int(v), part, who))

    for i, t0 in enumerate(DARTS):                          # his fire, climbing a semitone each time
        for t, m, v, d in play('loge', t0, BEAT, i % 4, 84 + 3 * i):
            add(t, d, m, v, 'fire', i)
    for t0 in (T_SETTLE - 1.0, T_SETTLE + 0.6):
        for t, m, v, d in play('loge_flicker', t0, 0.12, -12, 88):
            add(t, d, m, v, 'flicker')
    add(0.0, T_SETTLE, 'Bb1', 58, 'pedal')
    for k, t0 in enumerate(SEARCH):
        for t, m, v, d in play('loge_ambivalent', t0, BEAT, (0, 2, -1)[k], 86):
            add(t, d, m, v, 'amb', k)
        add(t0 + 1.95, 0.2, 'C4', 80, 'race', k)
    for t, m, v, d in play('freia_love', T_LOVE, BEAT * 2.0, 0, 84):
        add(t, d, m, v, 'love' if m >= note('D4') else 'lovebass')
    for m in ('C2', 'G2'):
        add(T_RHINE, T_GREED - T_RHINE, m, 62, 'river')
    for i in range(int((T_RING - T_RHINE) / (BEAT / 2))):
        add(T_RHINE + i * BEAT / 2, BEAT, ('C4', 'E4', 'G4', 'C5', 'G4', 'E4')[i % 6], 62, 'wave')
    for t, m, v, d in play('gold', T_GOLDCALL, BEAT, 0, 86):
        add(t, d, m, v, 'gold')
    for t, m, v, d in play('rheingold', T_CRY, BEAT * 0.75, 0, 82):
        add(t, d, m, v, 'cry' if m > note('C4') else 'crybass')
    ring = play('ring', T_RING, BEAT * 1.1, 0, 92)
    for t, m, v, d in ring:
        add(t, d, m, v, 'ring' if m > note('C3') else 'ringbass')
    for t, m, v, d in play('renunciation', T_RENOUNCE, BEAT, -12, 96):
        add(t, d, m, v, 'renounce')
    for m in ('C2', 'G2', 'C3', 'Eb3'):                     # the giants' greed swells under them
        add(T_GREED, T_GRAB - T_GREED, m, 90, 'swell')
    for t, m, v, d in play('fafner', T_GREED, BEAT * 0.8, 0, 100):
        add(t, d, m, v, 'fafner', FAFNER)
    for t, m, v, d in play('giants', T_GREED + 4.2, BEAT * 0.75, -12, 100, line='melody'):
        add(t, d, m, v, 'giant', FASOLT)
    add(T_GRAB - 1.5, 1.5, 'C2', 96, 'roll')
    add(T_GRAB, 0.8, 'C1', 124, 'grab', FASOLT)
    for b, d, m in ((0, .5, 'A4'), (.5, 1.5, 'F5'), (2, .5, 'E5'), (2.5, 2, 'C#5')):
        add(T_GRAB + 0.2 + b * BEAT, d * BEAT, m, 112, 'cry2', FREIA)
    for t, m, v, d in play('giants_authority', T_HELD, BEAT * 0.8, -12, 108):
        add(t, d, m, v, 'auth', FASOLT)
        if d >= 0.3:
            add(t, 0.4, 'C1', 104, 'stamp', FASOLT if (t - T_HELD) % 1.6 < 0.8 else FAFNER)
    for m in ('A3', 'C4', 'E4'):
        add(T_HELD, D - T_HELD, m, 76, 'trem')
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
    bt = np.sort(rng.uniform(T_LOVE, T_RHINE - 2.0, nb))
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
        cold = smoothstep(T_RENOUNCE, T_RENOUNCE + 3, t) * (1 - smoothstep(T_GREED, T_GREED + 3, t))
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
        flare = 0.5 * smoothstep(T_LOVE, T_LOVE + 2, t) * (1 - smoothstep(T_RHINE - 1, T_RHINE + 1, t)) + \
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
    from pixelhome.audio import SR, whoosh
    order = np.argsort(G.pd)
    xs, ds = G.pos[order, 0], G.pd[order]
    x0, x1 = xs.min(), xs.max()

    def pan_at(dd):
        x = np.interp(dd, ds, xs)
        return float(0.85 * (2 * (x - x0) / (x1 - x0) - 1))

    C = choreography(G)
    pf = pan_at(at(G, 'Porch Front', 0.5))

    def pan_g(k, t):
        return pan_at(np.interp(t, C['t'], C['giants'][k]))

    def pan_god(k, t):
        return pan_at(np.interp(t, C['t'], C['gods'][k]))

    def pan_loge(t):
        return pan_at(np.interp(t, C['t'], C['loge']))

    for name, gain, rev in (('brass', 0.2, 0.3), ('low', 0.2, 0.18), ('strings', 0.18, 0.32), ('winds', 0.2, 0.38),
                            ('perc', 0.23, 0.25), ('harp', 0.22, 0.4), ('fx', 0.1, 0.25)):
        M.bus(name, gain=gain, reverb=rev)
    tuba = M.sampler('Brass/Tuba/sus/*.wav', tune=-12)
    tbn = M.sampler('Brass/Tenor Trombone/sus/*.wav', tune=-12)
    horn = M.sampler('Brass/F Horn/sus/*.wav', tune=-12)
    mute = M.sampler('Brass/F Horn/mute/*.wav', tune=-12)
    cb = M.sampler('Strings/Solo Contrabass/SusNV/*.wav', tune=-12)
    pizz = M.sampler('Strings/Solo Contrabass/Pizz/*.wav', tune=-12)
    vtrem = M.sampler('Strings/Violin Section/Trem/*.wav', tune=-12)
    trem = M.sampler('Strings/Cello Section/trem/*.wav', tune=-12)
    vn = M.sampler('Strings/Violin Section/susVib/*.wav', tune=-12)
    vns = M.sampler('Strings/Violin Section/Spic/*.wav', tune=-12)
    vc = M.sampler('Strings/Cello Section/susvib/*.wav', tune=-12)
    pic = M.sampler('Woodwinds/Piccolo/Stac/*.wav', tune=-12)
    fl = M.sampler('Woodwinds/Flute/susvib/*.wav', tune=-12)
    ob = M.sampler('Woodwinds/Oboe/Vib/*.wav', tune=-12)
    cl = M.sampler('Woodwinds/Clarinet/susLong/*.wav', tune=-12)
    bsn = M.sampler('Woodwinds/Bassoon/sus/*.wav', tune=-12)
    harp = M.sampler('Strings/Harp/*.wav')
    timp = M.hits('Percussion/Timpani/Timpani1_Hit*.wav')
    roll = M.hits('Percussion/Timpani/Rolls/*.wav')
    bd = M.hits('Percussion/BDrumNewhit_v[4-7]*.wav')
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
            e = np.clip((tt - t0) / rise, 0, 1) * np.clip(1 - (tt - t1) / fall, 0, 1)
            M.add(bus, a * e, t, gain, pan)
            t += step

    for t, d, m, v, part, who in compose():
        if part == 'fire':
            pa = pan_loge(t)
            M.add('strings', vns.play(m + 12, v), t, 0.9, pa)
            M.add('harp', harp.play(m + 12, v - 10), t, 0.6, pa)
            if d < 0.2:
                M.add('winds', pic.play(m + 24, v - 16), t, 0.5, pa)
        elif part == 'flicker':
            M.add('winds', pic.play(m + 12, v), t, 0.9, pan_loge(t))
            M.add('harp', harp.play(m, v - 10), t, 0.5, pan_loge(t))
        elif part == 'pedal':
            hold('low', trem, m + 12, t, t + d, v, 0.0, rise=1.0, fall=1.5, gain=0.6)
        elif part == 'amb':
            pa = pan_loge(t)
            if m >= note('C5'):
                M.add('strings', vn.play(m - 12, v, dur=d * 1.05, release=0.2), t, 0.8, pa)
                M.add('winds', fl.play(m - 12, v - 10, dur=d * 1.05, release=0.2), t, 0.5, pa)
            elif m >= note('Ab3'):
                M.add('harp', harp.play(m, v), t, 0.6, pa)
            else:
                M.add('low', vc.play(m, v - 6, dur=d * 1.05, release=0.2), t, 0.7, pa)
        elif part == 'race':
            M.add('fx', whoosh(1.6, 600, 5000, 0.6, seed=int(t * 10)), t, 1.0, -0.6)
            M.add('fx', whoosh(1.6, 600, 5000, 0.6, seed=int(t * 10) + 1), t, 1.0, 0.6)
            gl = [x for x in range(note('C3'), note('C6')) if x % 12 in (0, 2, 4, 6, 8, 10)]
            for i, x in enumerate(gl):
                M.add('harp', harp.play(x, 70 + i), t + i * 1.2 / len(gl), 0.6, -0.7 + 1.4 * i / len(gl))
        elif part == 'love':
            M.add('strings', vn.play(m, v, dur=d * 1.05, release=0.4), t, 0.9, pan_god(FREIA, t))
            M.add('winds', fl.play(m, v - 16, dur=d * 1.05, release=0.4), t, 0.4, 0.0)
        elif part == 'lovebass':
            hold('strings', vc, m, t, t + d, v - 6, -0.3, rise=0.3, fall=0.6, gain=0.6)
        elif part == 'river':
            hold('low', cb if m < note('C2') + 1 else trem, m + 12 * (m > note('C2')), t, t + d, v, pf,
                 rise=2.5, fall=2.5, gain=0.6)
        elif part == 'wave':
            M.add('harp', harp.play(m, v), t, 0.7, pf + 0.3 * np.sin(t))
        elif part == 'gold':
            M.add('brass', mute.play(m, v, dur=d, release=0.5), t, 1.0, pf)
        elif part == 'cry':
            M.add('winds', (fl if m >= note('F5') else ob if m >= note('C5') else cl).play(m, v, dur=d * 1.05,
                                                                                         release=0.3), t, 0.7, pf)
        elif part == 'crybass':
            M.add('low', bsn.play(m + 12, v - 10, dur=d, release=0.3), t, 0.7, pf)
        elif part == 'ring':
            M.add('winds', (ob if m >= note('E4') else cl).play(m, v, dur=d * 1.05, release=0.3), t, 0.9, pf)
        elif part == 'ringbass':
            hold('low', vc, m, t, t + d, v - 10, pf, rise=0.5, fall=1.0, gain=0.7)
        elif part == 'renounce':
            M.add('brass', tbn.play(m, v, dur=d, release=0.5), t, 0.9, pf)
            M.add('low', vc.play(m, v - 10, dur=d, release=0.5), t, 0.6, pf)
        elif part == 'fafner':
            M.add('low', tuba.play(m, v, dur=d * 1.05, release=0.2), t, 1.0, pan_g(FAFNER, t))
            M.add('low', bsn.play(m + 12, v - 16, dur=d, release=0.2), t, 0.5, pan_g(FAFNER, t))
        elif part == 'giant':
            M.add('brass', tbn.play(m + 12, v, dur=d * 1.1, release=0.2), t, 0.9, pan_g(FASOLT, t))
            M.add('low', tuba.play(m, v - 10, dur=d * 1.1, release=0.2), t, 0.7, pan_g(FASOLT, t))
        elif part == 'roll':
            M.add('perc', roll.play(v, dur=d), t, 0.7, pan_g(FASOLT, t))
        elif part == 'grab':
            M.add('perc', crash.play(124), t, 1.0, pan_god(FREIA, t - 0.1))
            M.add('perc', timp.play(124, pitch=-6), t, 1.0, pan_g(FASOLT, t))
            M.add('perc', bd.play(124), t, 0.9, 0.0)
            M.add('fx', whoosh(0.5, 300, 4000, 0.7, seed=5), t - 0.4, 1.0, 0.0)
            M.add('fx', whoosh(1.0, 4000, 400, 0.6, seed=6), t + 0.25, 1.0, 0.3)
        elif part == 'cry2':
            pa = pan_god(FREIA, t)
            M.add('strings', vn.play(m, v, dur=d * 1.05, release=0.3), t, 1.0, pa)
            M.add('winds', fl.play(m, v - 20, dur=d, release=0.3), t, 0.6, pa)
        elif part == 'auth':
            pa = pan_g(FASOLT, t)
            M.add('brass', tbn.play(m + 12, v, dur=d * 1.1, release=0.3), t, 1.0, pa)
            M.add('low', tuba.play(m, v - 10, dur=d * 1.1, release=0.3), t, 0.8, pa)
        elif part == 'stamp':
            pa = pan_g(who, t)
            M.add('perc', timp.play(v, pitch=-5), t, 0.9, pa)
            M.add('perc', bd.play(v - 10), t, 0.7, pa)
            M.add('low', pizz.play(m + 12, v), t, 0.7, pa)
        elif part == 'swell':
            s = tuba if m < note('C3') else horn if m >= note('Eb3') else tbn
            hold('brass', s, m, t, t + d, v, 0.45, rise=d * 0.9, fall=0.3, gain=0.6)
            hold('strings', vtrem, m + 24, t, t + d, v - 10, 0.2, rise=d * 0.9, fall=0.3, gain=0.4)
        elif part == 'trem':
            hold('strings', vtrem, m, t, t + d, v, 0.3, rise=2.0, fall=1.2, gain=0.6)
