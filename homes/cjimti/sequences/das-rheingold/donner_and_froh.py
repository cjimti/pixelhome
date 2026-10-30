"""Donner and Froh: the giants close in on Freia and she cries out for help, and her cry is answered. Froh comes
first, rising out of the front of Porch Left on the orchestra's rush, a shimmering band of rainbow that slides in
beside her, and as he arrives a rainbow sweeps once along the whole roofline. Then a crack of thunder and Donner
bursts out of the porch in white and steel blue, lightning forking away from him down Porch Left and along the
Left wing, and plants himself between his sister and the giants.

The music is Wagner's own, as Solti's 1958 Vienna Philharmonic recording takes it: the giants seizing Freia ("Du
da! Folg' uns!"), her "Helft! Helft! Vor den Harten!", Froh's "Zu mir, Freia!" and "Froh schützt die Schöne!",
Donner's entrance and "Fasolt und Fafner, fühltet ihr schon meines Hammers harten Schlag?", the giants' "Was
soll das Drohn?", Donner raising his hammer, "Kommt her, des Lohnes Last wäg' ich mit gutem Gewicht!", and
Wotan's spear crashing down between them, "Halt, du Wilder! Nichts durch Gewalt!" (bars 1131-1167); then the
first flickers of Loge's motif as he arrives (1183-1187). The notes come from the Wagner Ring Dataset's piano
reduction (pixelhome/ring.py): the giants on trombones, tuba and basses; Freia's cry on violins and flutes;
Froh's rush on violins, horns and harp; Donner on horns and trumpets over trombones and tuba; the hammer's climb
for the full orchestra over a timpani roll; the spear's falling octaves on trombones, tuba and basses under the
horns; Loge's flicker on flutes, piccolo, violins and harp. The reduction carries the dynamics in one hand only,
so each note takes the loudest velocity around it. A production's storm goes with Donner: a thunderclap as he
bursts in, thunder with every bolt he throws, the wind rising while he raises the hammer, and a blow of the
spear; the giants stamp on the bass drum, and Loge arrives with a crackle of fire.

Donner's call throws bolts of lightning at the giants, who answer stamping, unimpressed. So Donner raises his
hammer: the house darkens under a storm while steel-blue sparks are drawn in to him from every run, and at the
top of the climb lightning cracks right across the house, three great flashes. Before the hammer can fall,
Wotan's spear slams down: a steel white-blue line strikes in one frame across the whole back of the porch,
between Donner and the giants, and holds there while the falling octaves walk down it. Donner's lightning
gutters out and the giants step back. Then something flickers at the free end of the Right wing: a few orange
sparks. Loge has arrived.

compose() holds every note, choreography() every position; render() and score() read both."""
import numpy as np
from pixelhome.fx import DT, hexc, light, smoothstep, nframes, Flicker
from pixelhome.ring import Orchestra, excerpt

CODE = 'RG10'
TITLE = 'Donner and Froh'
KIND = 'show'
DESCRIPTION = ("Freia's brothers rush to her side: Froh in a rainbow and Donner the thunder god, throwing "
               'lightning across the house. Donner raises his hammer at the giants, and Wotan\'s spear comes '
               'down between them. Then, at the far end of the house, a flicker of fire.')
VOICEOVER = ('Freia calls for her brothers, and they come running: one bright as a rainbow, '
             'one loud as a storm. Somebody is about to lose his temper.')

EX = excerpt(__file__)                      # bars 1131-1167, 1183-1187, Solti 1958
BAR = {int(m): t for m, t in EX['bars']}
SEG = [sg['start'] for sg in EX['segments']] + [EX['seconds']]
BEAT = 0.5
T_CRY = BAR[1135]                           # Freia: "Helft! Helft!"
T_FROH = BAR[1137]                          # Froh rises out of the porch
T_DONNER = BAR[1144]                        # thunder: Donner bursts out
T_CALL = BAR[1147]                          # Donner's call
T_DEFY = BAR[1150]                          # the giants answer
T_CALL1B = BAR[1157]                        # Donner again: "Schon oft zahlt' ich Riesen den Zoll"
T_RAISE = BAR[1158]                         # he raises his hammer
T_CALL2 = BAR[1162]                         # the top of the climb: lightning across the house
T_STOP = BAR[1164]                          # Wotan's spear
T_TREATY = T_STOP + 6.0
T_WAIT = SEG[1] - 0.3
T_LOGE = SEG[1]                             # a flicker: Loge
D = EX['seconds']
LEVEL = 1.9
T0 = 80.0                                   # seconds since The Giants began: sways and drifts run on

WOTAN, FRICKA, FREIA, FROH, DONNER = 0, 1, 2, 3, 4
FASOLT, FAFNER = 0, 1
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
    """Every note of the excerpt, tagged: (time, seconds, midi, velocity, part, who). The giants are 'giant' (a
    'stamp' on each bar's first beat while they seize her, and on their heavy notes when they answer); Freia's cry
    is 'cry'; Froh's rush is 'froh' over 'frohbass'; Donner is 'call', a 'bolt' on his long notes and three great
    ones at the top of his climb, which is 'climb'; the spear is 'spear'; Loge is 'flicker' (who = the phrase)."""
    N = []
    bolted = []
    for t, d, m, v, h in sorted(EX['notes']):
        if t < T_CRY or T_DEFY <= t < T_CALL1B:
            N.append((t, d, m, v, 'giant', FASOLT if int(t / 2.4) % 2 == 0 else FAFNER))
        elif t < T_FROH:
            N.append((t, d, m, v, 'cry' if h == 0 else 'giant', FREIA if h == 0 else FAFNER))
        elif t < T_DONNER:
            N.append((t, d, m, v, 'froh' if h == 0 else 'frohbass', FROH))
        elif t < T_RAISE:
            N.append((t, d, m, v, 'call', DONNER))
            if h == 0 and d >= 0.5 and t >= T_CALL and all(abs(t - b) > 1.5 for b in bolted):
                bolted.append(t)
        elif t < T_STOP:
            N.append((t, d, m, v, 'climb', DONNER))
        elif t < T_LOGE:
            N.append((t, d, m, v, 'spear', WOTAN))
        else:
            N.append((t, d, m, v, 'flicker', min(2, int((t - T_LOGE) / 2.5))))
    for tb in bolted:
        N.append((tb, 1.5, 34, 110, 'bolt', DONNER))
    for tb in (T_CALL2, T_CALL2 + 1.1, BAR[1163]):         # right across the house
        N.append((tb, 1.5, 34, 124, 'bolt', DONNER))
    beats = [BAR[b] for b in (1131, 1132, 1133, 1134)]
    beats += sorted({round(e[0], 3) for e in N if e[4] == 'giant' and e[0] >= T_DEFY and e[2] <= 50 and e[1] >= 0.3})
    for k, tb in enumerate(beats):
        N.append((tb, 0.4, 24, 112, 'stamp', (FASOLT, FAFNER)[k % 2]))
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
    cries = np.array([e[0] for e in N if e[4] == 'cry'])
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
        freia_light(fr, S, gp[FREIA], t, last(cries, t, 0.3))
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
    """Wagner's notes, orchestrated from the piano reduction, with Donner's storm and the giants' tread."""
    order = np.argsort(G.pd)
    xs, ds = G.pos[order, 0], G.pd[order]
    x0, x1 = xs.min(), xs.max()

    def pan_at(dd):
        x = np.interp(dd, ds, xs)
        return float(0.85 * (2 * (x - x0) / (x1 - x0) - 1))

    C = choreography(G)

    def pan_god(k, t):
        return pan_at(np.interp(t, C['t'], C['gods'][k]))

    def pan_g(k, t):
        return pan_at(min(np.interp(t, C['t'], C['giants'][k]), G.length))

    o = Orchestra(M, level=LEVEL)
    N = compose()
    tv = np.array([(e[0], e[3]) for e in N if e[4] not in ('stamp', 'bolt')])

    def loud(t, v):                                         # the reduction's dynamics sit in one hand
        near = tv[np.abs(tv[:, 0] - t) < 0.6, 1]
        return int(max(v, near.max() - 8)) if len(near) else v

    for t, d, m, v, part, who in N:
        if part in ('stamp', 'bolt'):
            continue
        v = loud(t, v)
        if part == 'giant':
            gp = pan_g(who, t)
            if m >= 55:
                o.play('horns', m, t, d, v, gp, 0.55)
                o.play('violas' if m < 67 else 'violins', m, t, d, v - 8, gp, 0.35)
            elif m >= 45:
                o.play('trombones', m, t, d, v, gp, 0.7)
            else:
                o.play('tuba', m + 12 if m < 33 else m, t, d, v, gp, 0.65)
                o.play('basses', m, t, d, v - 6, gp, 0.5)
        elif part == 'cry':                                 # "Helft! Helft!"
            o.play('violins', m, t, d, v, pan_god(FREIA, t), 0.6)
            o.play('piccolo' if m >= 84 else 'flutes', m, t, d, v - 8, pan_god(FREIA, t), 0.45)
        elif part == 'froh':                                # Froh's rush
            o.play('violins', m, t, d, v, pan_god(FROH, t), 0.55)
            o.play('harp', m, t, d, v, pan_god(FROH, t) - 0.2, 0.45)
            if d >= 0.3:
                o.play('horns', m - 12 if m >= 72 else m, t, d, v - 4, pan_god(FROH, t), 0.5)
        elif part == 'frohbass':
            o.play('cellos', m, t, d, v, -0.2, 0.55)
            o.play('basses', m - 12 if m >= 40 else m, t, d, v - 6, 0.2, 0.4)
        elif part == 'call':                                # Donner
            dp = pan_god(DONNER, t)
            if m >= 60:
                o.play('horns', m, t, d, v + 4, dp, 0.65)
                if d >= 0.3:
                    o.play('trumpets', m, t, d, v - 6, dp, 0.45)
            elif m >= 45:
                o.play('trombones', m, t, d, v, dp, 0.65)
            else:
                o.play('tuba', m, t, d, v, dp, 0.55)
                o.play('basses', m, t, d, v - 6, 0.2, 0.45)
        elif part == 'climb':                               # the hammer raised: everything climbs
            dp = pan_god(DONNER, t)
            o.play('violins' if m >= 55 else 'violas', m, t, d, v, dp + 0.2, 0.5)
            if m >= 55:
                o.play('horns', m, t, d, v - 4, dp, 0.45)
            if m < 52:
                o.play('trombones', m + 12 if m < 45 else m, t, d, v, dp, 0.55)
                o.play('tuba', m, t, d, v - 4, 0.0, 0.5)
        elif part == 'spear':                               # Wotan's spear: the falling octaves
            wp = pan_god(WOTAN, t)
            if m >= 60:
                o.play('horns', m, t, d, v + 6, wp, 0.6)
                o.play('trumpets', m, t, d, v - 4, wp, 0.4)
            else:
                o.play('trombones', m + 12 if m < 45 else m, t, d, v + 6, wp, 0.75)
                o.play('tuba', m, t, d, v + 4, 0.0, 0.6)
                o.play('basses', m, t, d, v, 0.2, 0.5)
        elif part == 'flicker':                             # Loge
            lp = pan_at(C['loge'])
            if m >= 72:
                o.play('piccolo' if m >= 84 else 'flutes', m, t, min(d, 0.12), v, lp, 0.5)
            o.play('violins' if m >= 55 else 'violas', m, t, min(d, 0.15), v - 6, lp, 0.45)
            o.play('harp', m, t, d, v - 8, lp, 0.3)
    # the staging: the giants' tread, Donner's storm, the spear's blow, Loge's fire
    for t, d, m, v, part, who in N:
        if part == 'stamp':
            o.hit('bass drum', t, 122, gain=0.55, pan=pan_g(who, t))
            o.hit('timpani', t, 108, pitch=-8, gain=0.35, pan=pan_g(who, t))
        elif part == 'bolt':
            big = t >= T_CALL2 - 0.01
            o.thunder(t, near=1.0 if big else 0.7, pan=0.0 if big else pan_g(FASOLT, t), gain=1.0 if big else 0.75)
    o.thunder(T_DONNER, near=1.0, pan=pan_god(DONNER, T_DONNER), gain=1.0)
    o.wind(T_RAISE - 1.0, T_STOP + 2.5, level=lambda tt: 0.3 + 0.7 * smoothstep(T_RAISE, T_CALL2, tt), pan=0.0)
    o.hit('timpani roll', T_RAISE, 100, pitch=-5, gain=0.45)
    o.boom(T_STOP, pan_god(WOTAN, T_STOP), 0.9)
    o.clash(T_STOP, pan_god(WOTAN, T_STOP), 120, 0.8)
    o.hit('crash', T_STOP, 120, gain=0.55)
    o.fire(T_LOGE - 0.3, D, level=lambda tt: 0.25 + 0.5 * smoothstep(T_LOGE, D, tt), pan=pan_at(C['loge']),
           crackle=16.0)
    o.effects([(0, -4), (T_FROH - 0.5, -4), (T_FROH, -10), (T_DONNER - 0.3, -10), (T_DONNER, 0), (T_CALL, -2),
               (T_DEFY, -6), (T_RAISE, -2), (T_CALL2, 1), (T_STOP + 2.5, 0), (T_STOP + 4, -10), (T_LOGE, -6)])
