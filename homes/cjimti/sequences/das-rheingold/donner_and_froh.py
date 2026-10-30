"""Donner and Froh: Freia's cry is answered. Froh comes first, rising out of the front of Porch Left to a harp
glissando and a horn call, a shimmering band of rainbow that slides in beside her, and as he arrives a rainbow
sweeps once along the whole roofline. Then a crack of thunder and Donner bursts out of the porch in white and
steel blue, lightning forking away from him down Porch Left and along the Left wing, and plants himself between
his sister and the giants.

Donner's call to the thunder (Donington 46) rings out on the horns, each long note a bolt of lightning thrown
from him toward the giants. Fasolt and Fafner answer with their own stamping motif (Donington 58), every stamp
shaking Porch Right, unimpressed. So Donner raises his hammer: a timpani roll swells while steel-blue sparks
are drawn in to him from every run of the house, and he sounds his call again fortissimo, horns and trumpets,
and with each note lightning cracks right across the house: the boldest moment of the show, three great
flashes a couple of seconds apart.

Before the hammer can fall, Wotan's spear (Donington 73) slams down in the trombones and tubas: a steel
white-blue line strikes in one frame across the whole back of the porch, between Donner and the giants, and
holds there while the descending scale walks down it. Donner's lightning gutters out and the giants step back.
Wotan restates his treaties (Donington 14), quieter now, and the gods wait for the one who talked Wotan into
this bargain. At the very end something flickers at the free end of the Right wing: a few orange sparks, a
skittering piccolo. Loge has arrived.

compose() holds every note, choreography() every position; render() and score() read both."""
import numpy as np
from pixelhome.audio import note
from pixelhome.fx import DT, hexc, light, smoothstep, nframes, Flicker
from pixelhome.leitmotifs import play

CODE = 'RG10'
TITLE = 'Donner and Froh'
KIND = 'show'
DESCRIPTION = ("Freia's brothers rush to her side: Froh in a rainbow and Donner the thunder god, throwing "
               'lightning across the house. Donner raises his hammer at the giants, and Wotan\'s spear comes '
               'down between them. Then, at the far end of the house, a flicker of fire.')
VOICEOVER = ('Freia calls for her brothers, and they come running: one bright as a rainbow, '
             'one loud as a storm. Somebody is about to lose his temper.')

BEAT = 0.5
T_FROH = 2.5                                # Froh rises out of the porch
T_DONNER = 8.0                              # thunder: Donner bursts out
T_CALL = 11.5                               # Donner's call
T_DEFY = 17.5                               # the giants stamp back
T_RAISE = 26.5                              # he raises his hammer
T_CALL2 = 32.0                              # the call, fortissimo: lightning across the house
T_STOP = 38.8                               # Wotan's spear
T_TREATY = 47.0
T_WAIT = 60.0                               # the gods wait; the giants grumble
T_LOGE = 72.5                               # a flicker: Loge
D = 80.0
T0 = 80.0                                   # seconds since The Giants began: sways and drifts run on

WOTAN, FRICKA, FREIA, FROH, DONNER = 0, 1, 2, 3, 4
FASOLT, FAFNER = 0, 1
APPLES = [('Side', 0.62), ('Left', 0.12), ('Side', 0.8), ('Left', 0.3), ('Side', 0.93), ('Left', 0.05),
          ('Side', 0.7), ('Left', 0.22), ('Left', 0.36), ('Side', 0.86), ('Left', 0.17), ('Side', 0.98)]
FROH_CALL = [(0, .5, 'G3'), (.5, .5, 'B3'), (1, .5, 'D4'), (1.5, 2.5, 'G4'), (4, .5, 'E4'), (4.5, .5, 'F#4'),
             (5, 3, 'G4')]
WAIT = [(0, 2, 'F3'), (2, 1, 'Gb3'), (3, 1, 'F3'), (4, 2, 'Eb3'), (6, 2, 'Db3'), (8, 3, 'C3'), (11, 1, 'Db3'),
        (12, 4, 'F3')]                              # Fricka, low and reproachful: where is your Loge now?

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
STEEL = hexc('#a0c0ff')
FIRE0 = hexc('#ff5000')
FIRE1 = hexc('#ffb020')
GCOL = [GREY, OCHRE]
GODCOL = [WOT, FRI, FRE]


def at(G, seg, u):
    s = G.pd[G.seg[seg]]
    return float(s.min() + u * (s.max() - s.min()))


def rainbow(x):
    """Hue 0..1 (any real) -> a saturated colour, PWM."""
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

    for m in ('A3', 'C#4', 'E4'):
        add(0.0, T_FROH + 1.0, m, 84, 'trem')
    gl = [x for x in range(note('G2'), note('G5') + 1) if x % 12 in (7, 11, 2)]
    for i, m in enumerate(gl):
        add(T_FROH - 0.6 + i * 1.2 / len(gl), 0.8, m, 92, 'gliss', FROH)
    for b, d, m in FROH_CALL:
        add(T_FROH + 0.6 + b * BEAT, d * BEAT, m, 100, 'froh', FROH)
    add(T_DONNER, 2.0, 'Bb1', 124, 'thunder', DONNER)
    for t0, v in ((T_CALL, 104), (T_CALL2, 122)):
        for t, m, _, d in play('donner', t0, BEAT * (1.0 if t0 == T_CALL else 0.9), 0, v):
            add(t, d, m, v, 'call', DONNER)
            if d >= 0.2:                                    # each long note throws a bolt
                add(t, 1.5, 'Bb1', v, 'bolt', DONNER)
    for t, m, _, d in play('giants', T_DEFY, BEAT * 1.1, -12, 104):
        add(t, d, m, 104, 'giant', FASOLT if t < T_DEFY + 4 * BEAT * 1.1 else FAFNER)
        if d >= 0.3:
            add(t, 0.4, 'C1', 112, 'stamp', FASOLT if (t - T_DEFY) % (4 * BEAT * 1.1) < 2 * BEAT * 1.1 else FAFNER)
    add(T_DONNER + 2.0, T_RAISE - T_DONNER - 2.0, 'Bb1', 66, 'pedal')
    add(T_STOP + 5.0, D - T_STOP - 5.0, 'Bb1', 60, 'pedal')
    for m in ('Gb2', 'Db3', 'Bb3', 'F4'):                   # the treaties end unresolved; the gods look round
        add(T_TREATY + 8.6, T_WAIT + 1.0 - T_TREATY - 8.6, m, 70, 'sigh')
    add(T_RAISE - 2.0, T_CALL2 - T_RAISE + 2.0, 'Bb1', 70, 'roll')
    for i in range(22):                                     # the strings climb while he raises it
        add(T_RAISE + i * (T_CALL2 - T_RAISE - 0.3) / 22, 0.3, note('Bb2') + i, 74 + i * 2, 'climb')
    for m in ('Bb1', 'F2', 'Bb2', 'D3', 'F3'):
        add(T_CALL2, T_STOP - T_CALL2, m, 100, 'storm')
    add(T_STOP, 1.0, 'C5', 124, 'slam', WOTAN)
    for t, m, v, d in play('spear', T_STOP, BEAT * 0.75, 0, 120):
        add(t, d, m, v, 'spear', WOTAN)
    tr = play('treaties', T_TREATY, BEAT * 1.1, 0, 84)
    top = {}
    for t, m, v, d in tr:
        top[t] = max(top.get(t, 0), m)
    for t, m, v, d in tr:
        add(t, d, m, v, 'treaty' if m == top[t] else 'treatybass' if m < note('C3') else 'treatyharm', WOTAN)
    for b, d, m in WAIT:
        add(T_WAIT + b * BEAT, d * BEAT, m, 88, 'fricka', FRICKA)
    for k in range(int((T_LOGE - T_WAIT) / (2 * BEAT))):    # a slow pulse while they wait
        add(T_WAIT + k * 2 * BEAT, BEAT, ('Bb1', 'Bb1', 'Gb1', 'F1')[k % 4], 74, 'pulse')
    for t, m, v, d in play('giants', T_WAIT + 4.0, BEAT * 1.3, -24, 80, line='melody'):
        add(t, d, m, v, 'grumble', FAFNER)
    for k, t0 in enumerate((T_LOGE, T_LOGE + 2.6, T_LOGE + 4.6)):
        for t, m, v, d in play('loge_flicker', t0, 0.13 if k < 2 else 0.11, -12 + 2 * k, 70 + 10 * k):
            add(t, d, m, v, 'flicker', k)
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
    """Per frame: the gods (Wotan, Fricka, Freia, Froh, Donner), the giants, and Loge's spark."""
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
    calm = 1 - 0.6 * smoothstep(T_DONNER, T_DONNER + 4, t)
    set_(FREIA, 0, D, at(G, 'Left', 0.55) + 8 * calm * np.sin(2 * np.pi * (t + T8) * 2.3), 6.0)
    froh_in, froh = at(G, 'Porch Left', 0.12), at(G, 'Left', 0.65)
    set_(FROH, 0, D, froh_in, 3.0)
    set_(FROH, T_FROH + 0.8, D, froh + 2 * np.sin(2 * np.pi * (t + T0) / 2.2), 2.2)
    don_in, don = at(G, 'Porch Left', 0.45), at(G, 'Porch Left', 0.2)
    set_(DONNER, 0, D, don_in, 3.0)
    set_(DONNER, T_DONNER + 0.3, D, don + 2 * np.sin(2 * np.pi * (t + T0) / 1.7), 5.0)
    set_(DONNER, T_RAISE, T_STOP, don + 30 * smoothstep(T_RAISE, T_CALL2, t), 4.0)    # he steps up
    set_(DONNER, T_STOP, T_STOP + 1.5, don - 25, 9.0)                                 # and is pushed back
    gods = np.array([follow(tgt[k], rate[k]) for k in range(5)])

    gt = np.zeros((2, F))
    grate = np.full((2, F), 2.5)
    home = [at(G, 'Porch Right', 0.5), at(G, 'Porch Right', 0.85)]
    for k in range(2):
        gt[k] = home[k] + 2 * np.sin(2 * np.pi * (t + T0) / 4.0 + np.pi * k)
    for ts, who in [(e[0], e[5]) for e in N if e[4] == 'stamp']:
        gt[who][(t >= ts - 0.15) & (t < ts + 0.3)] -= 18
    for k in range(2):
        m = (t >= T_STOP) & (t < T_STOP + 5.0)
        gt[k][m] += 35                                      # they step back from the spear
        grate[k][(t >= T_STOP) & (t < T_STOP + 0.6)] = 8.0
    giants = np.array([follow(gt[k], grate[k]) for k in range(2)])
    return dict(t=t, gods=gods, giants=giants, loge=at(G, 'Right', 0.95), froh_in=froh_in, don_in=don_in)


def render(G, seed=10):
    rng = np.random.default_rng(seed)
    F = nframes(D)
    out = np.zeros((F, G.N, 3))
    d = G.pd
    L = G.length
    S = mountain(G)
    C = choreography(G)
    N = compose()
    tw = Flicker(rng, G.N, 3.0, 9.0)
    apos = np.array([at(G, *a) for a in APPLES])

    stamps = [(e[0], e[5], e[3]) for e in N if e[4] == 'stamp']
    gnotes = np.array(sorted(e[0] for e in N if e[4] in ('giant', 'grumble')))
    calls = np.array([e[0] for e in N if e[4] == 'call'])
    froh_notes = np.array([e[0] for e in N if e[4] in ('froh', 'gliss')])
    treaty = np.array([e[0] for e in N if e[4] == 'treaty'])
    spear = np.array([e[0] for e in N if e[4] == 'spear'])
    fricka = np.array([e[0] for e in N if e[4] == 'fricka'])
    flick = np.array([e[0] for e in N if e[4] == 'flicker'])
    bolts = [(e[0], e[0] >= T_CALL2) for e in N if e[4] == 'bolt']      # (time, right across the house?)
    jag = [np.clip(rng.uniform(-0.4, 1.0, G.N), 0, 1) ** 0.6 for _ in range(8)]
    nm = 60                                                 # sparks drawn in to the hammer
    m0 = rng.uniform(0, L, nm)
    mt = rng.uniform(T_RAISE, T_CALL2 - 1.0, nm)
    s_lo, s_hi = at(G, 'Porch Left', 0.38), at(G, 'Porch Right', 0.3)

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
        g = C['giants'][:, f]
        gp = C['gods'][:, f]

        # the mountaintop, darkening under the storm while Donner raises his hammer
        storm = smoothstep(T_RAISE, T_CALL2, t) * (1 - smoothstep(T_STOP, T_STOP + 3, t))
        glory = 1 + 0.1 * last(treaty, t, 0.7) + 0.08 * smoothstep(T_TREATY, T_TREATY + 3, t) * (
            1 - smoothstep(T_WAIT, T_WAIT + 4, t))
        fr = scenery(S, t, glory) * (1 - 0.45 * storm)
        fr += light(STEEL, 0.22 * storm * (0.7 + 0.3 * S['grass'](t + T8)))
        menace(fr, S, g.min())

        # Freia, Fricka, Wotan
        freia_light(fr, S, gp[FREIA], t)
        god_light(fr, S, gp[FRICKA], FRI, 0.78 + 0.25 * last(fricka, t, 0.5))
        wf = last(treaty, t, 0.5) + 0.9 * last(spear, t, 0.3)
        god_light(fr, S, gp[WOTAN], WOT, 0.78 + 0.25 * wf, 0.32)
        fr += light(WHITE, 0.3 * wf * np.exp(-((d - gp[WOTAN]) / 8) ** 2))

        # the giants and their stamps
        gn = last(gnotes, t, 0.3)
        giant(fr, S, g[FASOLT], GREY, gn)
        giant(fr, S, g[FAFNER], OCHRE, gn)
        shudder = 0.0
        for ts, who, v in stamps:
            if ts <= t < ts + 1.6:
                shudder = max(shudder, stomp(fr, S, t - ts, g[who], GCOL[who], min(v / 120, 1.0)))

        # the spear at Wotan's side, and the apples still glowing in the orchard
        fr += light(SPEAR, 0.55 * np.exp(-((d - (gp[WOTAN] + 18)) / 7) ** 2))
        for k, q in enumerate(apos):
            fr += light(APPLE, (0.62 + 0.06 * np.sin(2 * np.pi * ((t + T0) / 2.3 + k / 5))) * np.exp(-((d - q) / 7) ** 2))
            fr += light(LEAF, 0.55 * np.exp(-((d - q - 11) / 5) ** 2))

        # Froh: rising out of the porch as a band of rainbow; a rainbow fills the house as he lands
        fa = smoothstep(T_FROH - 0.4, T_FROH + 0.4, t)
        if fa > 0:
            p = gp[FROH]
            fn = last(froh_notes, t, 0.3)
            dim = 1 - 0.35 * smoothstep(T_TREATY, T_WAIT, t)
            hue = (d - p) / 90 + 0.15 * (t + T0)
            band = np.exp(-((d - p) / (26 + 6 * fn)) ** 2)
            fr += light(rainbow(hue), fa * dim * (0.85 + 0.3 * fn) * band)
            if T_FROH + 1.0 <= t < T_FROH + 5.0:
                age = t - T_FROH - 1.0
                r = 1900 * smoothstep(0, 2.2, age)
                fill = smoothstep(r, r - 400, np.abs(d - p)) * (1 - smoothstep(1.5, 4.0, age))
                fr += light(rainbow(d / 500 - t * 0.25), 0.62 * fill)

        # Donner: white core, steel-blue halo, crackling; brighter as he raises the hammer
        da = smoothstep(T_DONNER - 0.05, T_DONNER + 0.15, t)
        if da > 0:
            p = gp[DONNER]
            cn = last(calls, t, 0.3)
            out_ = 1 - 0.55 * smoothstep(T_STOP, T_STOP + 1.5, t) + 0.25 * smoothstep(T_STOP + 6, T_WAIT, t)
            power = (0.75 + 0.35 * cn + 0.5 * storm) * out_
            crack = 0.75 + 0.25 * tw(t)
            fr += light(WHITE, da * power * np.exp(-((d - p) / (11 + 6 * storm)) ** 2))
            fr += light(STEEL, da * power * crack * (np.exp(-((d - p) / (32 + 30 * storm)) ** 2)))
            if T_DONNER <= t < T_DONNER + 0.6:              # the thunderclap: a flash and forks
                age = t - T_DONNER
                fr += light(WHITE, 0.55 * np.exp(-age / 0.12) * np.ones(G.N))
                fr += light(WHITE, bolt(age, C['don_in'], at(G, 'Left', 0.85), 1))
                fr += light(STEEL, bolt(age - 0.05, C['don_in'], at(G, 'Porch Left', 0.95), 2))
        for i, (tb, big) in enumerate(bolts):
            age = t - tb
            if not 0 <= age < 1.0:
                continue
            p = np.interp(tb, C['t'], C['gods'][DONNER])
            if big:                                         # right across the house
                ends = [(p, L), (p, 0), (p, at(G, 'Porch Right', 0.4))]
                fr += light(STEEL, 0.5 * np.exp(-age / 0.2) * np.ones(G.N))
                fr += light(WHITE, 0.4 * np.exp(-age / 0.07) * np.ones(G.N))
            else:
                ends = [(p, np.interp(tb, C['t'], C['giants'][i % 2]) - 30)]
            for j, (a, b) in enumerate(ends):
                fr += light(WHITE, 1.1 * bolt(age - 0.04 * j, a, b, 3 * i + j))
                fr += light(STEEL, 0.7 * bolt(age - 0.04 * j - 0.02, a, b, 3 * i + j + 1))
        if T_RAISE <= t < T_CALL2:                          # sparks drawn in to the hammer
            p = gp[DONNER]
            q = p + (m0 - p) * np.exp(-np.clip(t - mt, 0, None) / 0.9)
            vis = smoothstep(mt, mt + 0.3, t) * (np.abs(q - p) > 20)
            sg = (np.exp(-((d[:, None] - q[None, :]) / 9) ** 2) * vis[None, :]).max(axis=1)
            fr += light(STEEL, 0.9 * sg * (0.7 + 0.3 * tw(t)))

        # the spear slams down across the back of the porch, between them
        if t >= T_STOP:
            age = t - T_STOP
            hold = 1 - 0.75 * smoothstep(T_STOP + 3.5, T_STOP + 6.0, t) - 0.25 * smoothstep(T_STOP + 6, T_STOP + 9, t)
            sp = last(spear, t, 0.3)
            line = (d >= s_lo) & (d <= s_hi)
            walk = np.interp(t, spear, np.linspace(s_lo, s_hi, len(spear))) if t < spear[-1] + 1 else s_hi
            sheen = 0.75 + 0.25 * np.cos(2 * np.pi * (d / 120 - 0.6 * t))
            fr += light(SPEAR, hold * (0.5 + 0.25 * sp + 0.7 * np.exp(-age / 0.15)) * sheen * line)
            fr += light(WHITE, hold * (0.6 + 0.4 * sp) * np.exp(-((d - walk) / 14) ** 2) * line)
            if age < 1.5:
                r = 40 + 900 * age ** 0.6
                mid = 0.5 * (s_lo + s_hi)
                fr += light(SPEAR, 0.8 * (1 - age / 1.5) * np.exp(-((np.abs(d - mid) - (s_hi - s_lo) / 2 - r) / 50) ** 2))
                fr += light(WHITE, 0.5 * np.exp(-age / 0.1) * np.ones(G.N))

        # the treaties: blue bands from Wotan; Fricka's reproach: rose ripples
        if T_TREATY <= t < T_WAIT + 2:
            for ts in treaty[(treaty <= t) & (treaty > t - 3)]:
                age = t - ts
                r = 30 + 380 * age ** 0.8
                fr += light(WOT, 0.7 * (1 - age / 3) * np.exp(-((np.abs(d - gp[WOTAN]) - r) / 50) ** 2))
        if T_WAIT <= t < T_LOGE:
            for ts in fricka[(fricka <= t) & (fricka > t - 2.5)]:
                age = t - ts
                r = 20 + 200 * age ** 0.8
                fr += light(FRI, 0.5 * (1 - age / 2.5) * np.exp(-((np.abs(d - gp[FRICKA]) - r) / 30) ** 2))

        # Loge: a flicker at the free end of Right
        if t >= T_LOGE - 0.5:
            lf = last(flick, t, 0.12)
            grow = smoothstep(T_LOGE - 0.5, D, t)
            q = C['loge'] + (25 * np.sin(2 * np.pi * t * 1.7) + 12 * np.sin(2 * np.pi * t * 4.3)) * \
                (1 - smoothstep(D - 3, D, t))               # settling as Loge arrives
            hue = np.clip(0.5 + 0.5 * tw(t), 0, 1)[:, None]
            col = FIRE0 * (1 - hue) + FIRE1 * hue
            fr += light(col, (0.3 + 0.55 * grow + 0.5 * lf) * np.exp(-((d - q) / (10 + 6 * grow)) ** 2)
                        * (0.6 + 0.4 * np.abs(tw(t))))
            sp = (rng.random(G.N) < 0.02 + 0.08 * lf) * np.exp(-((d - q) / 90) ** 2)
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

    def pan_g(k, t):
        return pan_at(np.interp(t, C['t'], C['giants'][k]))

    def pan_god(k, t):
        return pan_at(np.interp(t, C['t'], C['gods'][k]))

    for name, gain, rev in (('brass', 0.22, 0.3), ('low', 0.22, 0.18), ('strings', 0.18, 0.32), ('winds', 0.2, 0.35),
                            ('perc', 0.25, 0.25), ('harp', 0.22, 0.4), ('fx', 0.1, 0.25)):
        M.bus(name, gain=gain, reverb=rev)
    tuba = M.sampler('Brass/Tuba/sus/*.wav', tune=-12)
    tubst = M.sampler('Brass/Tuba/stac/*.wav', tune=-12)
    tbn = M.sampler('Brass/Tenor Trombone/sus/*.wav', tune=-12)
    horn = M.sampler('Brass/F Horn/sus/*.wav', tune=-12)
    tpt = M.sampler('Brass/Trumpet/sus/*.wav', tune=-12)
    cb = M.sampler('Strings/Solo Contrabass/SusNV/*.wav', tune=-12)
    pizz = M.sampler('Strings/Solo Contrabass/Pizz/*.wav', tune=-12)
    vtrem = M.sampler('Strings/Violin Section/Trem/*.wav', tune=-12)
    trem = M.sampler('Strings/Cello Section/trem/*.wav', tune=-12)
    vn = M.sampler('Strings/Violin Section/susVib/*.wav', tune=-12)
    va = M.sampler('Strings/Viola Section/susvib/*.wav', tune=-12)
    ob = M.sampler('Woodwinds/Oboe/Vib/*.wav', tune=-12)
    pic = M.sampler('Woodwinds/Piccolo/Stac/*.wav', tune=-12)
    harp = M.sampler('Strings/Harp/*.wav')
    timp = M.hits('Percussion/Timpani/Timpani1_Hit*.wav')
    roll = M.hits('Percussion/Timpani/Rolls/*.wav')
    bd = M.hits('Percussion/BDrumNewhit_v[4-7]*.wav')
    crash = M.hits('Percussion/cymbal-crash1_f*.wav')
    crash_s = M.hits('Percussion/cymbal-crash1_mp*.wav')

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
        if part == 'trem':
            hold('strings', vtrem, m, t, t + d, v, -0.3, rise=0.1, fall=1.2, gain=0.6)
        elif part == 'pedal':
            hold('low', trem, m + 12, t, t + d, v, 0.0, rise=1.5, fall=1.5, gain=0.6)
            hold('low', cb, m, t, t + d, v, 0.0, rise=1.5, fall=1.5, gain=0.6)
        elif part == 'sigh':
            hold('strings', va if m >= note('C3') else trem, m, t, t + d, v, -0.2, rise=1.0, fall=1.5, gain=0.6)
        elif part == 'gliss':
            M.add('harp', harp.play(m, v), t, 1.0, pan_at(np.interp(t, C['t'], C['gods'][FROH])))
        elif part == 'froh':
            M.add('brass', horn.play(m, v, dur=d * 1.05, release=0.4), t, 1.0, pan_god(FROH, t))
        elif part == 'thunder':
            pa = pan_god(DONNER, t)
            M.add('perc', crash.play(124), t, 1.0, pa)
            M.add('perc', timp.play(124, pitch=-6), t, 1.0, pa)
            M.add('perc', bd.play(124), t, 1.0, pa)
            M.add('perc', roll.play(110, dur=d), t, 0.7, pa)
            M.add('fx', whoosh(0.8, 5000, 400, 0.6, seed=8), t - 0.05, 1.0, pa)
        elif part == 'call':
            pa = pan_god(DONNER, t)
            M.add('brass', horn.play(m, v, dur=d * 1.05, release=0.4), t, 1.0, pa)
            M.add('brass', horn.play(m - 12, v - 10, dur=d * 1.05, release=0.4), t, 0.7, pa - 0.1)
            if v > 110:
                M.add('brass', tpt.play(m, v, dur=d * 1.05, release=0.4), t, 0.8, pa + 0.1)
                M.add('low', tuba.play(m - 24, v, dur=d * 1.05, release=0.4), t, 0.8, pa)
        elif part == 'bolt':
            pa = pan_god(DONNER, t)
            big = t >= T_CALL2
            M.add('perc', (crash if big else crash_s).play(v), t, 0.9 if big else 0.6, 0.0 if big else pa)
            M.add('perc', timp.play(v, pitch=-4), t, 0.9, pa)
            if big:
                M.add('perc', bd.play(124), t, 0.9, 0.0)
            M.add('fx', whoosh(0.5, 6000, 900, 0.6, seed=int(t * 10)), t - 0.05, 0.9, pa)
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
        elif part == 'roll':
            M.add('perc', roll.play(v, dur=d), t, 0.5, pan_god(DONNER, t))
        elif part == 'climb':
            pa = pan_god(DONNER, t)
            M.add('strings', vtrem.play(m + 12, v, dur=d * 1.4, release=0.1), t, 0.7, pa)
            M.add('low', trem.play(m, v, dur=d * 1.4, release=0.1), t, 0.6, pa)
            M.add('perc', timp.play(60 + int(2.5 * (m - note('Bb2'))), pitch=-6 + 0.25 * (m - note('Bb2'))), t,
                  0.6, pa)
        elif part == 'storm':
            hold('strings', trem if m < note('Bb2') else vtrem, m + 12 * (m < note('Bb2')), t, t + d, v, 0.0,
                 rise=0.2, fall=0.15, gain=0.6)
        elif part == 'slam':
            M.add('perc', crash.play(127), t, 1.0, 0.0)
            M.add('perc', timp.play(127, pitch=-8), t, 1.0, 0.0)
            M.add('perc', bd.play(127), t, 1.0, 0.0)
            M.add('fx', whoosh(0.4, 400, 6000, 0.7, seed=3), t - 0.35, 1.0, 0.0)
        elif part == 'spear':
            M.add('brass', tbn.play(m, v, dur=d * 1.1, release=0.3), t, 1.0, wp + 0.3)
            M.add('brass', tbn.play(m + 12, v - 10, dur=d * 1.1, release=0.3), t, 0.6, wp + 0.4)
            M.add('low', tuba.play(m - 12, v, dur=d * 1.1, release=0.3), t, 0.9, wp + 0.3)
            M.add('low', cb.play(m - 12, v - 10, dur=d * 1.1, release=0.3), t, 0.6, 0.0)
            M.add('perc', timp.play(v - 10, pitch=-6), t, 0.6, 0.0)
        elif part == 'treaty':
            M.add('brass', tbn.play(m, v, dur=d, release=0.4), t, 1.0, wp)
            M.add('brass', horn.play(m, v - 14, dur=d, release=0.4), t, 0.5, wp + 0.1)
        elif part == 'treatyharm':
            M.add('brass', horn.play(m, v - 24, dur=d, release=0.4), t, 0.45, -0.2)
        elif part == 'treatybass':
            M.add('low', tuba.play(m, v - 10, dur=d, release=0.4), t, 0.8, wp)
        elif part == 'fricka':
            pa = pan_god(FRICKA, t)
            M.add('winds', ob.play(m + 12, v, dur=d * 1.05, release=0.3), t, 0.9, pa)
            M.add('strings', va.play(m, v - 10, dur=d * 1.05, release=0.3), t, 0.8, pa)
        elif part == 'pulse':
            M.add('low', pizz.play(m + 12, v), t, 0.9, 0.0)
            M.add('low', cb.play(m + 12, v - 20, dur=d, release=0.3), t, 0.5, 0.0)
        elif part == 'grumble':
            M.add('low', tuba.play(m + 12, v, dur=d * 1.1, release=0.3), t, 0.8, pan_g(who, t))
        elif part == 'flicker':
            pa = pan_at(C['loge'])
            M.add('winds', pic.play(m + 12, v), t, 0.9, pa)
            M.add('harp', harp.play(m, v - 10), t, 0.5, pa)
