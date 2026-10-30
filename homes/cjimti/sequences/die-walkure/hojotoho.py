"""Hojotoho!: Act II. The empty moonlit hut fades and a wild rocky pass takes its place: dark slate ridges along
the wings and Side, and on the heights of the porch the warm light of dawn.

The music is Wagner's own: the climax of the Act II prelude (bars 52 to 71) and Brünnhilde's entrance (bars 92 to
109), as Solti's 1958 Vienna Philharmonic recording takes them. The notes come from the Wagner Ring Dataset's
piano reduction (pixelhome/ring.py): the right hand's racing figuration on violins with flutes and piccolo, the
left hand's Ride rhythm, rising up the chord in dotted leaps, on horns and trombones (trumpets on top as it
breaks into C major), the bass on cellos, basses and tuba, timpani and cymbals on its downbeats. Under her war
cry the orchestra thins to its trills and the horns' calls. Her voice is not in the reduction, so her line comes
from the printed vocal score (Schott, archive.org diewalkre00wagn, pp. 84-85) and is played as written on
trumpets doubled by oboes: the two Hojotohos and Heiahas, then again a step higher, the four Hojotohos leaping up
the octave to high B and C, and the trilled "Heia-" that rises to her held high B. The stage has its sounds as
well: wind rushing past with each streak of the lovers' flight, hoofbeats under every silver gallop, a boom on
the white flash of C major, a gong as Wotan rises, her landing on every leap with her armour ringing, her gallop away, and far off the hooves of
Fricka's rams. The effects lead through the prelude, back off for Wotan's call and all but vanish under her war
cry, so her line is clear; her gallop away comes back up under her held high B.

The prelude surges: streaks of Wälsung blue and hearth amber race across the house on every second bar, the
lovers running for their lives; then the Ride rhythm takes over and bright silver gallops go bounding along
every run, each hoofbeat a real note of the left hand. Wotan (deep blue, his spear a steel line) rises out of
Porch Left, and as the music breaks into C major the whole house flashes white. "Reite zur Wal!", he calls, and
a beam of his blue reaches across the porch, a Wälsung blue glow in it: Siegmund, in her charge. Brünnhilde
(silver white with glints of gold) bursts up on the summit of Porch Front, and on every one of her cries she
leaps along the porch in a shower of gold sparks while her trills glitter over the house. A rose glimmer
appears far off at the free end of Right: Fricka is coming, in her chariot drawn by rams. On the orchestra's
last rushing scales Brünnhilde laughs and is gone, galloping back along Porch Left, Left and Side, and Wotan
is left alone on Porch Left as the rose light grows.

compose() holds every note, choreography() every position; render() and score() read both."""
import numpy as np
from pixelhome.fx import DT, hexc, light, smoothstep, nframes, Flicker
from pixelhome.audio import note
from pixelhome.ring import Orchestra, excerpt

CODE = 'WK11'
TITLE = 'Hojotoho!'
KIND = 'show'
DESCRIPTION = ('Act Two begins high in the mountains. Wotan calls for his favourite daughter, the Valkyrie '
               'Brünnhilde, and she arrives with her famous war cry. Then she spots someone coming, and decides '
               'to leave her father to it.')
VOICEOVER = ('High on a rocky mountain pass, the king of the gods calls for his warrior daughter. '
             'Listen for her battle cry.')

K = 10                                      # this scene's place in the shared clock (t + 80 * K)
EX = excerpt(__file__)                      # Act II, bars 52-71 and 92-109, Solti 1958
BAR = {int(m): t for m, t in EX['bars']}
BAR[72] = BAR[92] = EX['segments'][1]['start']
D = EX['seconds']
T_CROSS = 4.0                               # the hut fades into the pass over this long
FLIGHTS = [BAR[b] for b in (52, 54, 56, 58, 60)]    # streaks of blue and amber, one pair per surge
T_RIDE = BAR[58]                            # the Ride rhythm takes over
T_WOTAN = BAR[62]                           # Wotan rises on Porch Left
T_MAJOR = BAR[66]                           # C major: the house flashes white
T_CALL = BAR[92]                            # "Reite zur Wal!": his order
T_BRUNN = BAR[94]                           # she bursts up on the summit
CRIES = [(BAR[94], 0.25), (BAR[98], 0.75), (BAR[102], 0.3), (BAR[103], 0.55), (BAR[104], 0.7),
         (BAR[105], 0.45)]                                                  # time, where she lands
# Her war cry, from the vocal score: (bar, start, length in eighths, note). 9/8, then 3/4 from bar 108.
_HO = lambda b, x, low, top, n: [(b, 0, 0.5, 'G5'), (b, 0.5, 1.5, x), (b, 2, 1, low), (b, 3, n, top)]
VOICE = (_HO(94, 'D#5', 'G4', 'B4', 5) + _HO(95, 'D#5', 'G4', 'B4', 4) + [(95, 8, 0.5, 'B4'), (95, 8.5, 0.5, 'B4'),
         (96, 0, 7, 'E5'), (96, 8, 0.5, 'E5'), (96, 8.5, 0.5, 'E5'), (97, 0, 7, 'G5')] +
         _HO(98, 'C5', 'A4', 'E5', 5) + _HO(99, 'C5', 'A4', 'E5', 4) + [(99, 8, 0.75, 'C5'), (99, 8.75, 0.25, 'C5'),
         (100, 0, 7, 'F#5'), (100, 8, 0.5, 'F#5'), (100, 8.5, 0.5, 'F#5'), (101, 0, 6, 'A5')] +
         _HO(102, 'D#5', 'G4', 'B4', 3) + [(102, 6, 1, 'B5')] + _HO(103, 'D5', 'G4', 'B4', 3) + [(103, 6, 1, 'B5')] +
         _HO(104, 'E5', 'G4', 'C5', 3) + [(104, 6, 1, 'C6')] + _HO(105, 'E5', 'G4', 'C5', 3) + [(105, 6, 1, 'C6')] +
         [(106, 0, 17, 'F#5 tr'), (107, 8, 0.5, 'E#5'), (107, 8.5, 0.5, 'F#5'), (108, 0, 12, 'B5')])
T_FRICKA = BAR[102]                         # a rose glimmer, far off
T_LAUGH = BAR[106]                          # the last rushing scales: she laughs
T_EXIT = BAR[107]                           # she gallops off along Side
T_END = D

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


def voice():
    """Her war cry in seconds: (time, seconds, midi, trilled), cut off where the excerpt ends."""
    bars = [(m, t) for m, t in EX['bars'] if m >= 92]
    when = lambda pos: float(np.interp(pos, [b[0] for b in bars], [b[1] for b in bars]))
    out = []
    for b, x, n, name in VOICE:
        per = 6 if b >= 108 else 9
        a, z = b + x / per, b + (x + n) / per
        if b >= 106 and name.endswith('tr'):
            z = 107 + 8 / 9
        if a < bars[-1][0]:
            t0 = when(a)
            out.append((t0, when(min(z, bars[-1][0])) - t0, note(name.split()[0]), name.endswith('tr')))
    return out


def compose():
    """Every note of the excerpt, tagged: (time, seconds, midi, velocity, part, who). The left hand's long notes in
    the prelude are the Ride rhythm ('ride'), its others the bass ('bass'); the right hand is the figuration
    ('trill'). Under Wotan's call the notes are his ('wotan'), under her cries hers ('brunn'). 'cry' and 'burst'
    mark her moments for the lights; they make no sound."""
    N = []
    for t, d, m, v, hand in EX['notes']:
        if hand == 0:
            part = 'trill'
        elif t < T_CALL and d >= 0.35 and t >= BAR[53]:
            part = 'ride'
        else:
            part = 'bass'
        who = 'wotan' if T_CALL <= t < T_BRUNN else 'brunn' if t >= T_BRUNN and hand == 0 else None
        N.append((t, d, m, v, part, who))
    for t, d, m, trill in voice():
        N.append((t, d, m, 112, 'voice', 'brunn'))
    N.append((T_BRUNN, 1.2, 40, 0, 'burst', 'brunn'))
    for t0, _ in CRIES:
        N.append((t0, 0.9, 40, 0, 'cry', 'brunn'))
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
    for t0, u in CRIES:                                                         # each cry a leap along the porch
        m = t >= t0 + 0.15
        b_t[m] = at(G, 'Porch Front', u)
        rate[(t >= t0 + 0.15) & (t < t0 + 0.9)] = 9.0
    b_t[t >= T_LAUGH] = at(G, 'Porch Front', 0.4)
    ex = t >= T_EXIT
    b_t[ex] = at(G, 'Porch Front', 0.4) - (at(G, 'Porch Front', 0.4) + 160) * smoothstep(T_EXIT, T_EXIT + 5.0, t[ex])
    rate[ex] = 6.0
    br = follow(b_t, rate)
    wv = smoothstep(T_WOTAN, T_WOTAN + 1.0, t)
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
    leaps = [t0 + 0.15 for t0, _ in CRIES]
    beats = [BAR[b] for b in range(66, 72)]
    sparks = []
    sp = Flicker(rng, G.N, 4.0, 9.0)

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
                    fr += light(col, (1 - a / 3.2) * (0.9 * tail + 0.9 * np.exp(-((d - h) / 35) ** 2)))
        if t >= T_MAJOR:                                                        # C major: the house flashes white
            a = t - T_MAJOR
            fr += light(hexc('#e8f8ff'), 1.0 * np.exp(-a / 0.9) * (0.6 + 0.4 * np.exp(-((d - pf) / 500) ** 2)))
            k = int(np.searchsorted(beats, t, side='right')) - 1                # and pulses on every downbeat
            if 0 < k and t < T_CALL:
                fr += light(GOLD, 0.6 * np.exp(-(t - beats[k]) / 0.3) * (0.3 + 0.7 * np.exp(-((d - pf) / 400) ** 2)))

        # the Ride: silver gallops bounding along every run, the trills glittering
        ridec = smoothstep(T_RIDE - 0.3, T_RIDE + 0.5, t) * (1 - smoothstep(T_CALL, T_CALL + 1.5, t))
        ridec += 0.8 * smoothstep(T_EXIT - 0.3, T_EXIT + 0.5, t) * (1 - smoothstep(D - 2.5, D - 0.3, t))
        glit = max(ridec, 0.9 * smoothstep(T_BRUNN, T_BRUNN + 0.5, t) * (1 - smoothstep(D - 2.5, D - 0.3, t)))
        if glit > 0:
            i = int(np.searchsorted(ride, t, side='right')) - 1
            hoof = np.exp(-(t - ride[i]) / 0.15) if i >= 0 else 0.0
            ph = (t * 0.14) % 1.0
            for k in range(5 if ridec > 0 else 0):
                q = (ph + k / 5) * (L + 400) - 200
                bounce = 0.45 + 0.55 * hoof
                fr += light(BRUNN, ridec * 0.95 * bounce * np.exp(-((d - q) / 70) ** 2))
                fr += light(GOLD, ridec * 0.55 * bounce * smoothstep(q - 260, q, d) * smoothstep(q + 10, q - 10, d))
            j = int(np.searchsorted(trills, t, side='right')) - 1
            tr = np.exp(-(t - trills[j]) / 0.12) if j >= 0 and t - trills[j] < 0.5 else 0.0
            fr += light(BRUNN, glit * 0.85 * tr * np.clip(sp(t), 0, 1) ** 2)

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
        order = smoothstep(T_CALL, T_CALL + 0.6, t) * (1 - smoothstep(T_FRICKA - 1, T_FRICKA, t))
        if order > 0:
            lo, hi = min(wp, bp), max(wp, bp)
            beam = smoothstep(lo - 10, lo + 10, d) * smoothstep(hi + 10, hi - 10, d)
            pulse = 0.5 + 0.5 * np.cos(2 * np.pi * ((d - wp) / 150 - 1.2 * t))
            fr += light(WOTAN, order * (0.4 + 0.25 * pulse) * beam)
            if t >= T_CALL + 1.2:                                               # the Wälsung, in her charge
                fr += light(SIEG, 0.4 * order * smoothstep(T_CALL + 1.2, T_CALL + 3, t) * np.exp(-((d - bp) / 70) ** 2))

        # far off at the free end of Right, a rose glimmer: Fricka is coming
        rose = ROSE_END * smoothstep(T_FRICKA, T_FRICKA + 2.5, t) * (0.8 + 0.2 * smoothstep(T_LAUGH, D, t))
        if rose > 0:
            fr += light(ROSE, rose * (0.85 + 0.15 * np.sin(2 * np.pi * tt / 1.3)) * np.exp(-((L - d) / 90) ** 2))
        out[f] = fr
    return np.clip(out, 0, 1)


def score(M, G):
    """Wagner's notes, orchestrated from the piano reduction: the full orchestra for the prelude's climax, thinner
    under her cries, full again for the last scales; drums and cymbals on its real downbeats."""
    order = np.argsort(G.pd)
    xs, ds = G.pos[order, 0], G.pd[order]
    x0, x1 = xs.min(), xs.max()

    def pan_at(dd):
        x = np.interp(dd, ds, xs)
        return float(0.85 * (2 * (x - x0) / (x1 - x0) - 1))

    C = choreography(G)
    pf = pan_at(at(G, 'Porch Front', 0.5))
    o = Orchestra(M, level=1.9)

    def size(t):
        return 1.0 if t < T_CALL or t >= T_LAUGH else 0.55

    def role(t, d, m, v, hand):
        if T_CALL <= t < T_BRUNN and hand == 1 and m >= 54:                    # Wotan's call: trombones, tuba
            return [('trombones', 0, 0, 0.8), ('tuba', -12, -10, 0.4)]
        if T_BRUNN <= t < T_LAUGH and hand == 1 and m >= 54 and d >= 0.35:     # under her cries: the horns call
            return [('horns', 0, 4, 0.9), ('trumpets', 0, -12, 0.35)]
        return None

    def pan(t, m):
        if t < T_CALL:
            return float(np.clip(-0.7 + 1.4 * ((t * 0.14) % 1), -0.7, 0.7))
        return pan_at(np.interp(t, C['t'], C['brunn' if t >= T_BRUNN else 'wotan'])) * 0.7

    o.tutti(EX['notes'], size=size, role=role, pan=pan)
    for t, d, m, trill in voice():                                             # her cry: trumpets, oboes
        bp = pan(t, 60)
        if trill:                                                               # the trill: F sharp and G
            o.play('trumpets', m, t, d, 108, bp, 0.75)
            k, tt = 0, t
            while tt < t + d - 0.05:
                o.play('oboes', m + (k % 2), tt, 0.08, 100, bp, 0.4)
                o.play('flutes', m + (k % 2), tt, 0.08, 96, bp, 0.3)
                k, tt = k + 1, tt + 0.075
        else:
            o.play('trumpets', m, t, max(d, 0.12), 114, bp, 0.9)
            o.play('oboes', m, t, max(d, 0.12), 104, bp, 0.45)
    for b in (66, 67, 68, 69, 70, 71):                                          # C major, then E: the downbeats
        o.hit('timpani', BAR[b], 110, pitch=-3, gain=0.55)
    o.hit('crash', T_MAJOR, 110, gain=0.6)
    o.hit('crash', T_BRUNN, 100, gain=0.5, pan=pf)
    o.hit('timpani', T_BRUNN, 110, pitch=-2, gain=0.6, pan=pf)
    for t0, _ in CRIES[1:]:
        o.hit('timpani', t0, 96, pitch=-2, gain=0.45, pan=pan(t0 + 0.2, 60))
    o.hit('crash', BAR[108], 100, gain=0.45)

    # the stage: what the lights show, heard
    L = G.length
    bpan = lambda t: pan_at(np.interp(t, C['t'], C['brunn']))
    fxhit = lambda name, t, v, g, p: o.hit(name, t, v, gain=g, pan=p, fx=True)       # a stage hit, on the fader
    for tf in FLIGHTS:                                                          # the lovers' flight rushing past
        o.wind(tf, tf + 3.2, 0.9, pan=lambda t, tf=tf: pan_at(at(G, 'Left', 0.1) + 520 * max(t - tf, 0) ** 1.25))
    ride = [e[0] for e in compose() if e[4] == 'ride']
    for k, t in enumerate(ride):                                                # every hoofbeat of the silver gallops
        ph = (t * 0.14) % 1.0
        fxhit('hoof', t, 112, 0.55, pan_at((ph * (L + 400) - 200) % L))
        fxhit('hoof soft', t + 0.09, 96, 0.45, pan_at(((ph + 0.4) * (L + 400) - 200) % L))
    o.boom(T_MAJOR, 0.0, 0.8)                                                   # the white flash of C major
    fxhit('gong scrape', T_WOTAN, 110, 0.7, pan_at(at(G, 'Porch Left', 0.5)))  # Wotan rises
    o.boom(T_WOTAN + 0.4, pan_at(at(G, 'Porch Left', 0.5)), 0.5)
    for t0, _ in CRIES:                                                         # every leap: she lands, armour ringing
        tl = t0 + 0.15
        o.hoof(tl, bpan(tl), 118, 1.2)
        fxhit('metal', tl + 0.05, 92, 0.25, bpan(tl))
    o.gallop(T_EXIT, D - 0.4, 0.4, pan=bpan, v=118, gain=1.2)                   # she gallops off along Side
    o.gallop(T_FRICKA + 1.0, D - 0.3, 0.55, pan=0.85, v=70, gain=0.6)           # far off: Fricka's rams
    # the effects lead through the prelude, back off for Wotan's call, and all but vanish under her war cry; her
    # gallop away comes up under her held high B
    o.effects([(0.0, 0), (T_CALL - 1.2, 0), (T_CALL - 0.2, -9), (T_BRUNN - 0.8, -9), (T_BRUNN - 0.1, -16),
               (T_EXIT - 0.4, -16), (T_EXIT + 0.6, -6)])
