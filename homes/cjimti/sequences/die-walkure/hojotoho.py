"""Hojotoho!: Act II. The empty moonlit hut fades and a wild rocky pass takes its place: dark slate ridges along
the wings and Side, and on the heights of the porch the warm light of dawn. The prelude surges: the lovers'
flight, rushing strings in D minor with the Sword (Donington 45) turned to the minor on a trumpet, and streaks of
Wälsung blue and hearth amber race across the house like two people running for their lives.

Then the Ride (Donington 47) in the horns over the Valkyries' trilling (22a) and their chords (22): bright
silver gallops go bounding along every run. Wotan (deep blue, his spear a steel line) rises out of Porch Left
and calls his daughter, and Brünnhilde (silver white with glints of gold) bursts up on the summit of Porch
Front with her war cry, "Hojotoho! Heiaha!": leaping octave cries on trumpet and horn, each one a bright leap
of silver along the porch that showers gold sparks, while the trills glitter all over the house. Her own motif
(Donington 88) on the horns.

Wotan gives her his order: in the coming fight she must stand by Siegmund (a trombone phrase, then Siegmund's
motif, 35, in the horns), and a beam of his blue reaches across the porch to her. She looks off to the right and
laughs: a rose glimmer has appeared far off at the free end of Right. Fricka is coming, in her chariot drawn by
rams, and Brünnhilde wants no part of that. She wishes him luck and is gone, galloping back along Porch Left,
Left and Side to the Ride, laughing, and Wotan is left alone on Porch Left as the rose light grows.

compose() holds every note, choreography() every position; render() and score() read both."""
import numpy as np
from pixelhome.audio import note
from pixelhome.fx import DT, hexc, light, smoothstep, nframes, Flicker
from pixelhome.leitmotifs import MOTIFS, play

CODE = 'WK11'
TITLE = 'Hojotoho!'
KIND = 'show'
DESCRIPTION = ('Act Two begins high in the mountains. Wotan calls for his favourite daughter, the Valkyrie '
               'Brünnhilde, and she arrives with her famous war cry. Then she spots someone coming, and decides '
               'to leave her father to it.')
VOICEOVER = ('High on a rocky mountain pass, the king of the gods calls for his warrior daughter. '
             'Listen for her battle cry.')

K = 10                                      # this scene's place in the shared clock (t + 80 * K)
T_CROSS = 6.0                               # the hut fades into the pass over this long
T_FLIGHT = 0.5                              # the prelude: the lovers' flight
FLIGHTS = [1.0, 4.0, 7.0, 10.0, 13.0]       # streaks of blue and amber, one pair per surge
T_MINOR = 8.5                               # the Sword, in the minor
RB = 0.36                                   # a quarter note of the Ride
RIDE = [(16.0, 0), (18.16, 0), (20.32, 3), (22.48, 3), (24.64, -2), (26.8, 0)]
T_WOTAN = 19.0                              # Wotan rises on Porch Left
T_CALL = 25.0                               # he calls her
T_BRUNN = 29.0                              # she bursts up on the summit
CRIES = [(30.2, 0, 0.25), (33.2, 0, 0.75), (36.2, 2, 0.38), (39.2, 3, 0.62)]   # time, transposition, where she lands
T_MOTIF = 43.0                              # her motif
T_ORDER = 48.5                              # Wotan's order: stand by Siegmund
T_WALSUNG = 52.5
T_FRICKA = 60.0                             # a rose glimmer, far off
T_LAUGH = 61.5
RIDE2 = [(65.0, 0), (67.16, 0), (69.32, 3), (71.48, 3), (73.64, 0)]
T_EXIT = 66.5                               # she gallops off along Side
D = 80.0

# Act I's moonlit hut, as WK10 leaves it
EMBER = hexc('#ff6a10')
HOT = hexc('#ffb040')
HUT = hexc('#a05a28')
TRUNK = hexc('#5a3010')
LEAF = hexc('#50b030')
MOON = hexc('#c8dcff')
GREEN = hexc('#80ff60')
BLOSSOM = hexc('#ffa8d8')
PALE = hexc('#d0b080')
# Act II
SLATE = hexc('#3a3a4a')
RIDGE = hexc('#5a5a70')
DAWN = hexc('#ff7a3a')
GLOW = hexc('#ffb070')
SIEG = hexc('#30a8ff')
AMBER = hexc('#ffa860')
WOTAN = hexc('#1a3cff')
SPEAR = hexc('#c8d8ff')
BRUNN = hexc('#f4f8ff')
GOLD = hexc('#ffd060')
ROSE = hexc('#ff9ad0')
WHITE = hexc('#ffffff')

TRUNK_L, EMBER_L = 0.55, 0.18
HUT_S, MOON_S, GREEN_S, LEAF_S, DOOR_S, BLOSSOM_S = 0.12, 0.2, 0.34, 0.5, 0.55, 1.0
# the pass and the people on it, as WK12 picks them up
SLATE_L, RIDGE_L, DAWN_L, GLOW_L = 0.5, 0.3, 0.55, 0.3
WOTAN_L, BRUNN_L, ROSE_END = 0.75, 0.75, 0.42


def at(G, seg, u):
    s = G.pd[G.seg[seg]]
    return float(s.min() + u * (s.max() - s.min()))


def hojotoho(t0, tr):
    """The war cry: "Ho-jo-to-ho!" climbing to a leap of an octave, then "Heiaha!" -> [(t, seconds, midi)]."""
    cry = [(0, .12, 'E4'), (.16, .3, 'A4'), (.5, .12, 'C5'), (.66, .7, 'E5'), (1.45, .14, 'A4'), (1.62, .14, 'C5'),
           (1.8, .9, 'A5')]
    return [(t0 + b, d, note(n) + tr - 5) for b, d, n in cry]


def compose():
    """Every note: (time, seconds, midi, velocity, part, who)."""
    N = []

    def add(t, d, m, v, part, who=None):
        N.append((float(t), float(d), note(m) if isinstance(m, str) else int(m), int(v), part, who))

    for m in ('G2', 'D3', 'G3', 'B3'):                                          # Act I's G major, dying
        add(0.0, 1.5, m, 70, 'fade')
    for k, tf in enumerate(FLIGHTS):                                            # the flight: rushing strings
        root = note('D3') + (0, 0, 3, 5, 7)[k]
        for j in range(16):
            add(tf + j * 0.11, 0.14, root + (0, 3, 7, 12, 15, 19, 24, 19, 15, 12, 7, 3, 0, 3, 7, 12)[j] - 12,
                84 + 2 * k, 'rush')
        add(tf, 2.8, root - 24, 96, 'surge')
        for b, d, n in ((0, .75, 'A4'), (.75, .25, 'Bb4'), (1, 1.5, 'D5')):
            add(tf + 0.9 + b * 0.5, d * 0.5, note(n) - 12 + (0, 0, 3, 5, 7)[k], 92, 'flight_horn')
    for b, d, n in MOTIFS['sword']['notes']:                                    # the Sword, turned to the minor
        add(T_MINOR + b * 0.45, d * 0.45, note(n) + 2 - (1 if n[0] == 'E' else 0), 104, 'minor')

    for k, (t0, tr) in enumerate(RIDE + RIDE2):                                 # the Ride
        for t, m, v, d in play('ride', t0, RB, tr, 104):
            add(t, d, m, v, 'ride')
        for t, m, v, d in play('valkyrie_cry', t0, RB * 0.75, tr - 12, 76, line='melody'):
            add(t, d, m, v, 'trill')
        for j in range(4):
            add(t0 + j * 3 * RB / 2, RB * 1.4, note('B1') + tr, 96, 'gallop')
    for k, t0 in enumerate((RIDE[2][0], RIDE[4][0])):
        for t, m, v, d in play('valkyries', t0, RB * 0.8, -12 + 3 * (k == 0), 88):
            if m >= note('B2'):
                add(t, d, m, v, 'chords')

    for b, d, n in ((0, 1, 'D3'), (1, .5, 'F3'), (1.5, .5, 'A3'), (2, 2, 'D4')):   # Wotan calls her
        add(T_CALL + b * 0.5, d * 0.5, n, 104, 'wotan', 'wotan')
    for k, (t0, tr, _) in enumerate(CRIES):                                     # "Hojotoho! Heiaha!"
        for t, d, m in hojotoho(t0, tr):
            add(t, d, m, 110 + 2 * k, 'cry', 'brunn')
        for t, m, v, d in play('valkyrie_cry', t0 + 0.6, 0.3, tr - 12, 80, line='melody'):
            add(t, d, m, v, 'trill')
        add(t0 + 0.66, 0.9, note('E2') + tr, 104, 'leap')
    add(T_BRUNN, 1.2, 'E2', 112, 'burst')
    for t, m, v, d in play('brunnhilde', T_MOTIF, 0.55, 0, 100):               # Brünnhilde
        add(t, d, m, v, 'motif' if m >= note('Bb3') else 'motif_low', 'brunn' if m >= note('Bb3') else None)

    order = [(0, 1, 'D3'), (1, .5, 'D3'), (1.5, .5, 'E3'), (2, 1, 'F3'), (3, 1, 'A3'), (4, 1.5, 'G3'),
             (5.5, .5, 'F3'), (6, 2, 'E3')]
    for b, d, n in order:                                                       # "stand by the Wälsung"
        add(T_ORDER + b * 0.5, d * 0.5, n, 100, 'wotan', 'wotan')
    for t, m, v, d in play('siegmund', T_WALSUNG, 0.3, 0, 92):
        add(t, d, m, v, 'walsung')
    for m in ('D2', 'A2', 'F3'):
        add(T_ORDER, T_FRICKA - T_ORDER, m, 78, 'pad')

    for m in ('G#4', 'B4', 'D5'):                                               # the rose glimmer: something coming
        add(T_FRICKA, RIDE2[0][0] - T_FRICKA, m, 76, 'rose')
    for j, m in enumerate(('E5', 'C5', 'D5', 'B4', 'C5', 'A4', 'B4', 'G#4', 'A4', 'E4')):   # she laughs
        add(T_LAUGH + j * 0.17, 0.15, m, 104 - 3 * j, 'laugh', 'brunn')
    for t, d, m in hojotoho(T_EXIT + 0.4, 0)[:4]:
        add(t, d, m, 106, 'cry', 'brunn')
    for m in ('B1', 'F#2', 'D3'):
        add(RIDE2[-1][0] + 2.2, D - RIDE2[-1][0] - 2.2, m, 66, 'alone')
    for b, d, n in ((0, 1.5, 'B2'), (1.5, .5, 'C3'), (2, 2, 'B2')):            # Wotan, left to face her
        add(RIDE2[-1][0] + 2.6 + b * 0.6, d * 0.6, n, 84, 'wotan', 'wotan')
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
    """Per frame: where Wotan and Brünnhilde are (path distance), and how much of each is there."""
    F = nframes(D)
    t = np.arange(F) * DT
    W = at(G, 'Porch Left', 0.5)
    wot = follow(W + 5 * np.sin(2 * np.pi * (t + 80 * K) / 6.0), np.full(F, 3.0))
    b_t = np.full(F, at(G, 'Porch Front', 0.5))
    rate = np.full(F, 3.0)
    for t0, tr, u in CRIES:                                                     # each cry a leap along the porch
        m = t >= t0 + 0.6
        b_t[m] = at(G, 'Porch Front', u)
        rate[(t >= t0 + 0.6) & (t < t0 + 1.4)] = 9.0
    b_t[t >= T_MOTIF] = at(G, 'Porch Front', 0.5)
    b_t[t >= T_ORDER] = at(G, 'Porch Front', 0.4)
    ex = t >= T_EXIT
    b_t[ex] = at(G, 'Porch Front', 0.4) - (at(G, 'Porch Front', 0.4) + 160) * smoothstep(T_EXIT, T_EXIT + 8.5, t[ex])
    rate[ex] = 6.0
    br = follow(b_t, rate)
    wv = smoothstep(T_WOTAN, T_WOTAN + 1.5, t)
    bv = smoothstep(T_BRUNN, T_BRUNN + 0.4, t)
    return dict(t=t, wotan=wot, brunn=br, wv=wv, bv=bv)


def room(G):
    """Act I's hut (as WK10 leaves it), for the crossfade."""
    rng = np.random.default_rng(606)
    d = G.pd
    pf = at(G, 'Porch Front', 0.5)
    hc = at(G, 'Left', 0.6)
    return dict(
        pf=pf, hc=hc, door=G.length,
        trunk=np.exp(-((d - pf) / 20) ** 2),
        canopy=np.clip(np.exp(-((d - pf) / 300) ** 2) - 0.8 * np.exp(-((d - pf) / 26) ** 2), 0, 1),
        hearth=np.exp(-((d - hc) / 120) ** 2),
        coals=np.exp(-((d - hc) / 45) ** 2),
        cast=np.exp(-np.abs(d - hc) / 700),
        storm=np.exp(-((G.length - d) / 110) ** 2),
        fl=Flicker(rng, G.N, 0.6, 2.2), fast=Flicker(rng, G.N, 2.5, 6.0), leaf=Flicker(rng, G.N, 0.1, 0.5),
        gust=Flicker(rng, G.N, 0.2, 0.9))


def draw_hut(G, R, tt, tw, grass, B):
    d, L = G.pd, G.length
    roll = 0.5 + 0.5 * np.cos(2 * np.pi * (d / 420 - 0.03 * tt))
    fr = light(HUT, HUT_S * (0.85 + 0.15 * roll))
    fr += light(EMBER, EMBER_L * R['hearth'] * (0.8 + 0.12 * R['fl'](tt) + 0.06 * R['fast'](tt)))
    dance = 0.5 + 0.5 * np.cos(2 * np.pi * (d / 230 - 0.11 * tt) + 1.5 * np.sin(2 * np.pi * 0.07 * tt))
    fr += light(EMBER, 0.55 * EMBER_L * R['cast'] * (0.3 + 0.7 * dance) * (0.85 + 0.15 * R['fl'](tt)))
    fr += light(HOT, 0.8 * EMBER_L * R['coals'] * (0.7 + 0.2 * R['fast'](tt)))
    cut = np.exp(-((d - R['pf']) / 8) ** 2)
    fr += light(TRUNK, TRUNK_L * R['trunk'] * (1 - cut))
    fr += light(PALE, 0.42 * (np.exp(-((d - R['pf'] - 11) / 5) ** 2) + np.exp(-((d - R['pf'] + 11) / 5) ** 2)))
    fr += light(LEAF, LEAF_S * R['canopy'] * (0.85 + 0.15 * R['leaf'](tt)))
    wind = 0.5 + 0.5 * np.cos(2 * np.pi * (d / 260 + 0.09 * tt))
    wind2 = 0.5 + 0.5 * np.cos(2 * np.pi * (d / 110 + 0.21 * tt) + 2)
    fr += light(MOON, MOON_S * (0.85 + 0.15 * wind2))
    fr += light(GREEN, GREEN_S * (0.55 + 0.45 * wind * (0.7 + 0.3 * wind2)) * (0.9 + 0.1 * grass(tt)))
    fr += light(MOON, DOOR_S * np.exp(-((L - d) / 200) ** 2))
    fr += light(BLOSSOM, 0.45 * BLOSSOM_S * draw_blossoms(G, B, tt) * (0.8 + 0.2 * tw(tt)))
    return fr


def blossoms(G):
    rng = np.random.default_rng(909)
    n = 2400
    birth = np.sort(rng.uniform(80 * 8, 80 * 10 + 5, n))
    start = G.length - rng.exponential(700, n)
    speed = rng.uniform(40, 140, n)
    life = rng.uniform(3.0, 7.0, n)
    width = rng.uniform(7, 14, n)
    return birth, start, speed, life, width


def draw_blossoms(G, B, tt):
    birth, start, speed, life, width = B
    lo = int(np.searchsorted(birth, tt - 7.0))
    hi = int(np.searchsorted(birth, tt))
    if hi <= lo:
        return np.zeros(G.N)
    age = tt - birth[lo:hi]
    ok = age < life[lo:hi]
    a, l_ = age[ok], life[lo:hi][ok]
    q = start[lo:hi][ok] - speed[lo:hi][ok] * a + 20 * np.sin(2 * np.pi * a / 2.3)
    env = np.sin(np.pi * a / l_) ** 2
    g = np.exp(-((G.pd[:, None] - q[None, :]) / width[lo:hi][ok][None, :]) ** 2) * env[None, :]
    return g.max(axis=1)


def rocks(G):
    """The pass's fixed parts: jagged ridges on the wings, the heights of the porch (shared with WK12)."""
    rng = np.random.default_rng(1111)
    d = G.pd
    pf = at(G, 'Porch Front', 0.5)
    lat = rng.uniform(0, 1, 80)
    xs = np.linspace(d.min() - 50, d.max() + 50, 80)
    jag = np.interp(d, xs, lat)                                                 # piecewise straight: rock faces
    porch = np.isin(G.seg_of, ['Porch Left', 'Porch Front', 'Porch Right']).astype(float)
    return dict(pf=pf, jag=jag, height=np.exp(-((d - pf) / 430) ** 2), porch=porch,
                drift=Flicker(rng, G.N, 0.05, 0.2), shim=Flicker(rng, G.N, 0.3, 1.0))


def draw_pass(G, P, tt, level=1.0):
    d = G.pd
    cloud = 0.5 + 0.5 * np.cos(2 * np.pi * (d / 520 - 0.025 * tt))
    fr = light(SLATE, level * SLATE_L * (0.75 + 0.25 * cloud) * (1 - 0.4 * P['height']))
    fr += light(RIDGE, level * RIDGE_L * P['jag'] ** 2 * (0.8 + 0.2 * P['drift'](tt)) * (1 - 0.5 * P['height']))
    fr += light(DAWN, level * DAWN_L * P['height'] * (0.88 + 0.12 * P['shim'](tt)))
    fr += light(GLOW, level * GLOW_L * P['height'] ** 3 * (0.8 + 0.2 * cloud))
    return fr


def draw_wotan(G, p, b, spear=0.35):
    d = G.pd
    fr = light(WOTAN, b * np.exp(-((d - p) / 30) ** 2) + 0.35 * b * np.exp(-((d - p) / 140) ** 2))
    shaft = smoothstep(p + 15, p + 30, d) * smoothstep(p + 110, p + 95, d)
    fr += light(SPEAR, spear * (b / WOTAN_L) * shaft)
    return fr


def draw_brunn(G, p, b, tt):
    d = G.pd
    fr = light(BRUNN, b * np.exp(-((d - p) / 24) ** 2) + 0.3 * b * np.exp(-((d - p) / 120) ** 2))
    fr += light(GOLD, (b / BRUNN_L) * 0.6 * (0.75 + 0.25 * np.sin(2 * np.pi * tt / 1.7)) * np.exp(-((d - p - 14) / 7) ** 2))
    return fr


def render(G, seed=11):
    rng = np.random.default_rng(seed)
    F = nframes(D)
    out = np.zeros((F, G.N, 3))
    d, L = G.pd, G.length
    R = room(G)
    P = rocks(G)
    pf = P['pf']
    B = blossoms(G)
    rng_g = np.random.default_rng(9)                                            # WK09's flickers, in its order
    tw = Flicker(rng_g, G.N, 2.0, 6.0)
    grass = Flicker(rng_g, G.N, 0.1, 0.4)
    C = choreography(G)
    N = compose()
    ride = np.array([e[0] for e in N if e[4] == 'ride'])
    trills = np.array([e[0] for e in N if e[4] == 'trill'])
    wsung = np.array([e[0] for e in N if e[5] == 'wotan'])
    bsung = np.array([e[0] for e in N if e[5] == 'brunn'])
    leaps = [t0 + 0.66 for t0, _, _ in CRIES]
    sparks = []
    sp = Flicker(rng, G.N, 4.0, 9.0)
    PL = at(G, 'Porch Left', 0.5)

    for f in range(F):
        t = f * DT
        tt = t + 80 * K
        x = smoothstep(0.0, T_CROSS, t)
        fr = draw_pass(G, P, tt, x)
        if x < 1:
            fr += (1 - x) * draw_hut(G, R, tt, tw, grass, B)

        # the flight: streaks of blue and amber racing along the house, one pair per surge
        for k, tf in enumerate(FLIGHTS):
            if tf <= t < tf + 3.2:
                a = t - tf
                head = at(G, 'Left', 0.1) + 520 * a ** 1.25
                for col, off in ((SIEG, 0), (AMBER, -60)):
                    h = head + off
                    tail = smoothstep(h - 380, h, d) * smoothstep(h + 15, h - 5, d)
                    fr += light(col, (1 - a / 3.2) * (0.75 * tail + 0.6 * np.exp(-((d - h) / 25) ** 2)))
        if T_MINOR <= t < T_MINOR + 4:
            a = t - T_MINOR
            fr += light(hexc('#e8f8ff'), 0.35 * np.exp(-a / 1.2) * np.exp(-((d - pf) / 300) ** 2))

        # the Ride: silver gallops bounding along every run, the trills glittering
        ridec = smoothstep(RIDE[0][0] - 0.3, RIDE[0][0] + 0.5, t) * (1 - smoothstep(T_MOTIF, T_MOTIF + 2, t))
        ridec += smoothstep(RIDE2[0][0] - 0.3, RIDE2[0][0] + 0.5, t) * (1 - smoothstep(RIDE2[-1][0] + 2, RIDE2[-1][0] + 4, t))
        if ridec > 0:
            i = int(np.searchsorted(ride, t, side='right')) - 1
            hoof = np.exp(-(t - ride[i]) / 0.15) if i >= 0 else 0.0
            ph = (t * 0.14) % 1.0
            for k in range(5):
                q = (ph + k / 5) * (L + 400) - 200
                bounce = 0.6 + 0.4 * hoof
                fr += light(BRUNN, ridec * 0.6 * bounce * np.exp(-((d - q) / 45) ** 2))
                fr += light(GOLD, ridec * 0.4 * bounce * smoothstep(q - 260, q, d) * smoothstep(q + 10, q - 10, d))
            j = int(np.searchsorted(trills, t, side='right')) - 1
            tr = np.exp(-(t - trills[j]) / 0.12) if j >= 0 and t - trills[j] < 0.5 else 0.0
            fr += light(BRUNN, ridec * 0.3 * tr * np.clip(sp(t), 0, 1) ** 3)

        # Wotan, risen on Porch Left
        wp, wv = C['wotan'][f], C['wv'][f]
        if wv > 0:
            i = int(np.searchsorted(wsung, t, side='right')) - 1
            wf = np.exp(-(t - wsung[i]) / 0.3) if i >= 0 and t - wsung[i] < 1.2 else 0.0
            rise = 0.6 * np.exp(-(t - T_WOTAN) / 0.5) if t >= T_WOTAN else 0.0
            fr += draw_wotan(G, wp, wv * WOTAN_L * (1 + 0.3 * wf + rise))

        # Brünnhilde: she bursts up on the summit; every cry a leap of silver showering gold
        bp, bv = C['brunn'][f], C['bv'][f]
        if T_BRUNN <= t < T_BRUNN + 2.0:
            a = t - T_BRUNN
            r = 20 + 500 * a ** 0.6
            fr += light(BRUNN, 0.8 * (1 - a / 2) * np.exp(-((np.abs(d - pf) - r) / 50) ** 2))
            fr += light(WHITE, 0.6 * np.exp(-a / 0.2) * np.exp(-((d - pf) / 200) ** 2))
        for tl in leaps:
            if abs(t - tl) < DT / 2:
                n = 40
                sparks.append(dict(t0=t, p=np.full(n, bp), v=rng.normal(0, 260, n), w=rng.uniform(6, 12, n)))
        for s in sparks:
            age = t - s['t0']
            if age < 2.0:
                q = s['p'] + s['v'] * (1 - np.exp(-age / 0.5)) * 0.5
                g = np.exp(-((d[:, None] - q[None, :]) / s['w'][None, :]) ** 2).max(axis=1)
                fr += light(GOLD, 0.9 * np.exp(-age / 0.6) * g)
        if bv > 0 and bp > -150:
            i = int(np.searchsorted(bsung, t, side='right')) - 1
            bf = np.exp(-(t - bsung[i]) / 0.25) if i >= 0 and t - bsung[i] < 1.0 else 0.0
            moving = abs(bp - C['brunn'][max(f - 4, 0)]) > 12
            if moving:
                trail = np.zeros(G.N)
                for n_, lag in enumerate(range(2, 20, 2)):
                    q = C['brunn'][max(f - lag, 0)]
                    trail = np.maximum(trail, np.exp(-((d - q) / 26) ** 2) * (1 - n_ / 9.5))
                fr += light(BRUNN, 0.55 * bv * trail)
            fr += draw_brunn(G, bp, bv * BRUNN_L * (1 + 0.3 * bf), tt)
            fr += light(WHITE, 0.4 * bf * np.exp(-((d - bp) / 10) ** 2))

        # the order: a beam of his blue across the porch to her
        order = smoothstep(T_ORDER, T_ORDER + 1, t) * (1 - smoothstep(T_FRICKA - 1, T_FRICKA, t))
        if order > 0:
            lo, hi = min(wp, bp), max(wp, bp)
            beam = smoothstep(lo - 10, lo + 10, d) * smoothstep(hi + 10, hi - 10, d)
            pulse = 0.5 + 0.5 * np.cos(2 * np.pi * ((d - wp) / 150 - 1.2 * t))
            fr += light(WOTAN, order * (0.4 + 0.25 * pulse) * beam)
            if t >= T_WALSUNG:                                                  # the Wälsung, in her charge
                fr += light(SIEG, 0.4 * order * smoothstep(T_WALSUNG, T_WALSUNG + 2, t) * np.exp(-((d - bp) / 70) ** 2))

        # far off at the free end of Right, a rose glimmer: Fricka is coming
        rose = ROSE_END * smoothstep(T_FRICKA, T_FRICKA + 2.5, t) * (0.8 + 0.2 * smoothstep(70, D, t))
        if rose > 0:
            fr += light(ROSE, rose * (0.85 + 0.15 * np.sin(2 * np.pi * tt / 1.3)) * np.exp(-((L - d) / 90) ** 2))
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

    def pt(key, t):
        return pan_at(np.interp(t, C['t'], C[key]))

    for name, gain, rev in (('strings', 0.18, 0.3), ('low', 0.2, 0.2), ('brass', 0.2, 0.3), ('winds', 0.16, 0.3),
                            ('perc', 0.2, 0.3), ('fx', 0.1, 0.3)):
        M.bus(name, gain=gain, reverb=rev)
    vcs = M.sampler('Strings/Cello Section/spic/*.wav', tune=-12)
    vas = M.sampler('Strings/Viola Section/spic/*.wav', tune=-12)
    va = M.sampler('Strings/Viola Section/susvib/*.wav', tune=-12)
    vatrem = M.sampler('Strings/Viola Section/trem/*.wav', tune=-12)
    vtrem = M.sampler('Strings/Violin Section/Trem/*.wav', tune=-12)
    vns = M.sampler('Strings/Violin Section/Spic/*.wav', tune=-12)
    cb = M.sampler('Strings/Solo Contrabass/SusNV/*.wav', tune=-12)
    cbs = M.sampler('Strings/Solo Contrabass/Spic/*.wav', tune=-12)
    horn = M.sampler('Brass/F Horn/sus/*.wav', tune=-12)
    tpt = M.sampler('Brass/Trumpet/sus/*.wav', tune=-12)
    tpts = M.sampler('Brass/Trumpet/stac/*.wav', tune=-12)
    tbn = M.sampler('Brass/Tenor Trombone/sus/*.wav', tune=-12)
    tuba = M.sampler('Brass/Tuba/sus/*.wav', tune=-12)
    fl = M.sampler('Woodwinds/Flute/stac/*.wav', tune=-12)
    cl = M.sampler('Woodwinds/Clarinet/stac/*.wav', tune=-12)
    timp = M.hits('Percussion/Timpani/Timpani1_Hit*.wav')
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

    ph = (np.arange(nframes(D)) * DT * 0.14) % 1.0
    for t, d, m, v, part, who in compose():
        if part == 'fade':
            hold('strings', vtrem if m >= note('G3') else vatrem, m, t, t + d, v, 0.0, rise=0.05, fall=1.5, gain=0.4)
        elif part == 'rush':
            pa = pan_at(at(G, 'Left', 0.1) + 520 * max(t - max(x for x in FLIGHTS if x <= t + 1e-6), 0) ** 1.25)
            M.add('strings', (vcs if m < note('A3') else vas).play(m, v), t, 0.8, pa)
        elif part == 'surge':
            M.add('low', cb.play(m + 12, v, dur=d, release=0.4), t, 0.8, -0.2)
            M.add('fx', whoosh(d, 300, 2500, 0.5, seed=int(t * 10)), t, 0.7, 0.0)
        elif part == 'flight_horn':
            M.add('brass', horn.play(m, v, dur=d * 1.05, release=0.3), t, 0.8, 0.2)
        elif part == 'minor':
            M.add('brass', tpt.play(m, v, dur=d * 1.05, release=0.4), t, 1.0, pf)
        elif part == 'ride':
            q = (np.interp(t, np.arange(len(ph)) * DT, ph)) * (G.length + 400) - 200
            M.add('brass', horn.play(m, v, dur=d * 1.1, release=0.2), t, 0.9, pan_at(np.clip(q, 0, G.length)) * 0.6)
            M.add('brass', tbn.play(m - 12, v - 10, dur=d * 1.1, release=0.2), t, 0.5, 0.0)
        elif part == 'trill':
            M.add('winds', (fl if (t * 7) % 2 < 1 else cl).play(m, v), t, 0.7, -0.6 + 1.2 * ((t * 3.3) % 1))
            M.add('strings', vns.play(m, v - 10), t, 0.4, 0.6 - 1.2 * ((t * 3.3) % 1))
        elif part == 'gallop':
            M.add('low', cbs.play(m + 12, v), t, 0.8, 0.0)
            M.add('low', vcs.play(m + 12, v - 10), t + RB * 0.5, 0.6, 0.1)
        elif part == 'chords':
            M.add('brass', (tbn if m < note('G3') else horn).play(m, v, dur=d * 1.05, release=0.3), t, 0.6,
                  -0.3 + 0.6 * ((m * 0.37) % 1))
        elif part == 'wotan':
            pa = pt('wotan', t)
            M.add('brass', tbn.play(m, v, dur=d * 1.05, release=0.5), t, 1.0, pa)
            M.add('low', tuba.play(m, v - 14, dur=d * 1.05, release=0.5), t, 0.6, pa)
        elif part == 'cry':
            pa = pt('brunn', t)
            M.add('brass', tpt.play(m, v, dur=d * 1.1, release=0.25), t, 1.0, pa)
            M.add('brass', horn.play(m - 12, v - 8, dur=d * 1.1, release=0.25), t, 0.7, pa)
        elif part == 'leap':
            M.add('perc', timp.play(v, pitch=-2), t, 0.7, pt('brunn', t + 0.2))
            M.add('fx', whoosh(0.5, 800, 5000, 0.5, seed=int(t * 10)), t - 0.1, 0.7, pt('brunn', t + 0.2))
        elif part == 'burst':
            M.add('perc', crash.play(v), t, 0.9, pf)
            M.add('perc', timp.play(v, pitch=-2), t, 0.9, pf)
        elif part == 'motif':
            M.add('brass', horn.play(m, v, dur=d * 1.05, release=0.4), t, 1.0, pt('brunn', t))
        elif part == 'motif_low':
            hold('strings', va if m >= note('C3') else cb, m + (12 if m < note('C3') else 0), t, t + d, v - 10, pf,
                 rise=0.3, fall=0.8, gain=0.5)
        elif part == 'walsung':
            M.add('brass', horn.play(m, v - 6, dur=d * 1.05, release=0.4), t, 0.7, pt('brunn', t))
        elif part == 'pad':
            hold('strings', vatrem if m >= note('C3') else cb, m + (12 if m < note('C3') else 0), t, t + d, v, 0.0,
                 rise=2.0, fall=1.0, gain=0.5)
        elif part == 'rose':
            hold('strings', vtrem, m, t, t + d, v, pan_at(G.length), rise=2.0, fall=1.0, gain=0.7)
            hold('low', vatrem, m - 24, t, t + d, v, pan_at(G.length), rise=2.0, fall=1.0, gain=0.5)
        elif part == 'laugh':
            M.add('brass', tpts.play(m, v), t, 1.2, pt('brunn', t))
            M.add('winds', fl.play(m + 12, v - 10), t, 0.9, pt('brunn', t))
        elif part == 'alone':
            hold('strings', vatrem if m >= note('C3') else cb, m + (12 if m < note('C3') else 0), t, t + d, v,
                 pt('wotan', t), rise=1.5, fall=1.0, gain=0.6)
