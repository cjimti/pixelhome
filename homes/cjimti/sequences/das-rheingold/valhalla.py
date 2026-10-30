"""Valhalla: out of the river's mist the faint circle of the Ring's beads still turns over the porch, slower and
slower, until they settle into towers and the castle gleams across the porch: Porch Left, Porch Front and Porch
Right lit as white-gold battlements, each chord of the brass a pulse through the masonry, the walls spreading out
from the keep and growing brighter as the brass grows.

The music is Wagner's own, as Solti's 1958 Vienna Philharmonic recording takes it: the last of the transformation
after the theft (bars 758-759), the Valhalla motif as the curtain rises on the mountain top (768-774), its
cadence and Fricka's "Wotan, Gemahl! Erwache!" (787-790), and Wotan's hail to the finished castle, "steht er zur
Schau: hehrer, herrlicher Bau!", rising to its fortissimo (818-825). The notes come from the Wagner Ring
Dataset's piano reduction (pixelhome/ring.py): the transformation's arpeggios on clarinets, harp and violins,
Valhalla's chords as a brass chorale (horns on top, trombones in the middle, tuba and basses below, trumpets
joining for the hail), the hail's moving inner parts on violas and violins, Fricka's waking on oboe and
violas; timpani on the chorale's strong chords, a cymbal swell as the castle first stands and a crash on the
last fortissimo.

Dawn comes up over a mountain meadow on the wings, the mist thinning into a blue-violet morning, and two
sleepers show in it on Left: Wotan, deep royal blue, and Fricka, rose silver, breathing slowly. Fricka wakes
on the orchestra's surge, rises, sees the castle and goes to shake him on her call: three nudges of rose
against blue. Wotan stirs, stands, and hails his castle: every strong chord of the brass sends a sweep of
white-gold from the castle out over the meadow to both ends of the house, his blue rises to meet it, and on
the last fortissimo the whole house flashes.

compose() holds every note, choreography() every position; render() and score() read both."""
import numpy as np
from pixelhome.fx import DT, hexc, light, smoothstep, nframes, Flicker
from pixelhome.ring import Orchestra, accents, excerpt

CODE = 'RG06'
TITLE = 'Valhalla'
KIND = 'show'
DESCRIPTION = ('Out of the mist the shape of the Ring becomes a castle, gleaming across the porch at dawn. '
               'Wotan, king of the gods, sleeps in the meadow below it until Fricka wakes him, and he greets '
               'his new fortress with the brass at full strength.')
VOICEOVER = ('High on a mountain, morning comes up over a castle that was not there yesterday. '
             'Two giants built it. Nobody has paid them yet.')

EX = excerpt(__file__)                      # bars 758-759, 768-774, 787-790, 818-825, Solti 1958
BAR = {int(m): t for m, t in EX['bars']}
SEG = [sg['start'] for sg in EX['segments']] + [EX['seconds']]
T_VAL = [SEG[1], BAR[772]]                  # Valhalla, soft, then fuller
T_FRICKA = BAR[788]                         # the orchestra surges: Fricka wakes
NUDGES = [46.47, 47.35, 48.22]               # "Wotan, Gemahl! Erwache!": she shakes him
T_DREAM = 50.0                              # Wotan stirs
T_HAIL = SEG[3]                             # "steht er zur Schau: hehrer, herrlicher Bau!"
HBEAT = 0.85
T_CADENCE = BAR[825] - 4 * HBEAT            # so that T_CADENCE + 4 * HBEAT is the last fortissimo
D = EX['seconds']
LEVEL = 2.1

WOTAN, FRICKA = 0, 1
BLUE = hexc('#1a3cff')
ROSE = hexc('#ff9ad0')
STONE = hexc('#fff0c0')
GOLD = hexc('#ffaa00')
RED = hexc('#ff1800')
DAWN_LO = hexc('#2a3a6a')
DAWN_HI = hexc('#6a5a8a')
GLOW = hexc('#ff9070')
NEAR = hexc('#a05a96')                      # the meadow near the castle, rosy at dawn
FAR = hexc('#2638a0')                       # and far from it, still blue
MIST = hexc('#6c70b8')
DUSK = hexc('#1c1c70')
WHITE = hexc('#ffffff')


def at(G, seg, u):
    s = G.pd[G.seg[seg]]
    return float(s.min() + u * (s.max() - s.min()))


def compose():
    """Every note of the excerpt, tagged: (time, seconds, midi, velocity, part, who). The transformation is the
    Ring ('ring', its bass 'ringbass'); Valhalla's chords are 'val' (who = 0 soft, 1 fuller, and its cadence);
    Fricka's waking and call are 'fricka' (her line) and 'fbass'; the hail is 'hail' (WOTAN)."""
    N = []
    for t, d, m, v, h in EX['notes']:
        if t < SEG[1]:
            N.append((t, d, m, v, 'ring' if h == 0 else 'ringbass', None))
        elif t < T_FRICKA:
            N.append((t, d, m, v, 'val', 0 if t < T_VAL[1] else 1))
        elif t < T_HAIL:
            N.append((t, d, m, v, 'fricka' if h == 0 else 'fbass', FRICKA))
        else:
            N.append((t, d, m, v, 'hail', WOTAN))
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
    """Per frame: where Wotan and Fricka are (path distance)."""
    F = nframes(D)
    t = np.arange(F) * DT
    tgt = np.zeros((2, F))
    rate = np.full((2, F), 3.0)

    def set_(k, a, b, where, r):
        m = (t >= a) & (t < b)
        tgt[k][m] = where if np.ndim(where) == 0 else where[m]
        rate[k][m] = r

    W, Fr = at(G, 'Left', 0.7), at(G, 'Left', 0.45)
    set_(WOTAN, 0, D, W, 3.0)
    set_(FRICKA, 0, D, Fr, 3.0)
    set_(FRICKA, T_FRICKA + 3.0, NUDGES[0] - 1.0, Fr + 30, 1.5)                # up, looking at the castle
    set_(FRICKA, NUDGES[0] - 1.0, T_DREAM + 2, W - 28, 2.0)                     # over to him
    for tn in NUDGES:
        set_(FRICKA, tn, tn + 0.25, W - 14, 18.0)
    set_(FRICKA, T_HAIL - 4, D, Fr, 1.0)
    set_(WOTAN, T_HAIL, D, W + 6 * np.sin(2 * np.pi * t / 5.0), 2.0)
    pos = np.array([follow(tgt[k], rate[k]) for k in range(2)])
    return dict(t=t, pos=pos)


def render(G, seed=6):
    rng = np.random.default_rng(seed)
    F = nframes(D)
    out = np.zeros((F, G.N, 3))
    d = G.pd
    pf = at(G, 'Porch Front', 0.5)
    C = choreography(G)
    N = compose()
    porch = np.isin(G.seg_of, ['Porch Left', 'Porch Front', 'Porch Right']).astype(float)
    wing = 1 - porch
    p0, p1 = at(G, 'Porch Left', 0.0), at(G, 'Porch Right', 1.0)
    reach = np.maximum(np.abs(d - pf), 1)                   # how far from the keep, along the walls
    merlon = 0.5 + 0.5 * np.cos(2 * np.pi * (d - pf) / 46)
    merlon = smoothstep(0.25, 0.55, merlon)
    stone = 0.88 + 0.12 * rng.uniform(-1, 1, G.N)           # masonry: every block a little different
    rings = np.array([e[0] for e in N if e[4] == 'ring'])
    far = np.clip(np.where(d < p0, p0 - d, np.where(d > p1, d - p1, 0.0)) / 520, 0, 1)   # meadow: away from the castle
    vchords = accents([e for e in N if e[4] == 'val'], n=3, space=0.5)
    hchords = accents([e for e in N if e[4] == 'hail'], n=3, space=0.5)
    fr_notes = np.array([e[0] for e in N if e[4] == 'fricka'])
    dream = np.array([e[0] for e in N if e[4] == 'dream'])
    tw = Flicker(rng, G.N, 0.3, 1.2)
    grass = Flicker(rng, G.N, 0.1, 0.5)

    for f in range(F):
        t = f * DT
        fr = np.zeros((G.N, 3))

        # RG05's mist, thinning into a dawn over the meadow on the wings
        mist = 1 - smoothstep(4.0, 26.0, t)
        dawn = smoothstep(5.0, 40.0, t)
        tt = t + 80
        m1 = 0.5 + 0.5 * np.cos(2 * np.pi * (d / 520 + 0.05 * tt))
        m2 = 0.5 + 0.5 * np.cos(2 * np.pi * (d / 230 - 0.09 * tt) + 2)
        m3 = 0.5 + 0.5 * np.cos(2 * np.pi * (d / 900 - 0.03 * tt) + 4)
        fr += light(DUSK, (0.2 + 0.06 * m3) * mist)
        fr += light(MIST, (0.04 + 0.26 * (m1 * m2) ** 1.5 + 0.08 * m3) * mist)
        sky = DAWN_LO * (1 - dawn) + DAWN_HI * dawn
        sky = sky[None, :] * (1 - dawn * 0.6) + dawn * 0.6 * (NEAR[None, :] * (1 - far[:, None]) + FAR[None, :] * far[:, None])
        roll = 0.5 + 0.5 * np.cos(2 * np.pi * (d / 300 - 0.04 * t))
        fr += light(sky, (0.2 + 0.14 * dawn) * (1 - mist) * (0.85 + 0.1 * roll + 0.05 * grass(t)) * (wing + 0.6 * porch))
        c1 = 0.5 + 0.5 * np.cos(2 * np.pi * (d / 380 - 0.02 * t))
        c2 = 0.5 + 0.5 * np.cos(2 * np.pi * (d / 170 + 0.035 * t) + 1)
        cloud = smoothstep(0.35, 1.0, c1 * c2)              # dawn cloud drifting over the meadow
        fr += light(DAWN_HI, 0.3 * cloud * dawn * wing)
        horizon = np.exp(-((d - pf) / 750) ** 2)            # first light behind the castle, rosy
        fr += light(GLOW, (0.12 + 0.16 * cloud) * dawn * (1 - 0.5 * mist) * horizon * (0.9 + 0.1 * roll))

        # the Ring's beads: turning slower, then still, then they are towers
        settle = smoothstep(T_VAL[0] - 2, T_VAL[0] + 3, t)
        rs = 0.32 * (1 - settle)
        if rs > 0:
            ri = int(np.searchsorted(rings, t, side='right')) - 1
            rp = np.exp(-(t - rings[ri]) / 0.5) if ri >= 0 and t - rings[ri] < 2.5 else 0.0
            ph = 0.12 * (t + 12) - 0.12 * t ** 2 / (2 * (T_VAL[0] + 3)) * (t < T_VAL[0] + 3)
            th = 2 * np.pi * (np.arange(14) / 14 + ph)
            q, depth = pf + 420 * np.cos(th), np.sin(th)
            g = np.exp(-((d[:, None] - q[None, :]) / 26) ** 2)
            front = (g * np.clip(depth, 0, 1)[None, :]).max(axis=1)
            back = (g * np.clip(-depth, 0, 1)[None, :]).max(axis=1)
            fr += light(GOLD, rs * (1 + 0.5 * rp) * front) + light(RED, 0.6 * rs * (1 + 0.4 * rp) * back)

        # Valhalla: battlements spreading out from the keep, brighter as the brass grows
        grow = 0.2 * smoothstep(T_VAL[0] - 1, T_VAL[0] + 5, t) + 0.15 * smoothstep(T_VAL[1], T_VAL[1] + 6, t) \
            + 0.65 * smoothstep(T_HAIL - 1, T_HAIL + 4, t)
        extent = 120 + 520 * smoothstep(T_VAL[0] - 1, T_VAL[1] + 6, t)
        walls = smoothstep(extent + 60, extent - 60, reach) * porch
        pulse = 0.0
        for arr, w, tau in ((vchords, 0.35, 0.5), (hchords, 0.5, 0.35)):
            i = int(np.searchsorted(arr, t, side='right')) - 1
            if i >= 0 and t - arr[i] < 2:
                pulse = max(pulse, w * np.exp(-(t - arr[i]) / tau))
        gleam = 0.5 + 0.5 * np.cos(2 * np.pi * ((d - p0) / 260 - 0.18 * t))
        lvl = (0.22 * smoothstep(T_VAL[0] - 4, T_VAL[0], t) + 0.6 * grow + 0.4 * pulse) * walls * stone
        fr += light(STONE, lvl * (0.42 + 0.58 * merlon) * (0.85 + 0.15 * gleam ** 4))
        fr += light(WHITE, 0.35 * grow * walls * merlon * gleam ** 12 * (0.7 + 0.3 * tw(t)))

        # the hail: every chord sends white-gold out from the castle over the meadow to both ends
        for tc in hchords:
            if not tc <= t < tc + 2.0:
                continue
            age = t - tc
            dist = np.where(d < p0, p0 - d, np.where(d > p1, d - p1, 0.0))
            rf = 900 * smoothstep(0, 1.3, age)
            band = np.exp(-((dist - rf) / 200) ** 2) * wing * (1 - smoothstep(1.0, 2.0, age))
            fr += light(STONE, 0.65 * band)
        cad = smoothstep(T_CADENCE + 4 * HBEAT - 0.2, T_CADENCE + 4 * HBEAT + 0.3, t)
        if cad > 0:
            age = t - T_CADENCE - 4 * HBEAT
            fr += light(STONE, (0.55 * np.exp(-max(age, 0) / 0.5)) * np.ones(G.N))

        # the sleepers: breathing slowly, showing as the light comes; Fricka wakes, Wotan rises
        seen = smoothstep(6.0, 18.0, t)
        for k, col in ((WOTAN, BLUE), (FRICKA, ROSE)):
            p = C['pos'][k][f]
            breath = 0.5 + 0.5 * np.sin(2 * np.pi * t / (4.2 + 0.7 * k) + k)
            if k == FRICKA:
                awake = smoothstep(T_FRICKA - 0.5, T_FRICKA + 2.0, t)
                i = int(np.searchsorted(fr_notes, t, side='right')) - 1
                flare = np.exp(-(t - fr_notes[i]) / 0.25) if i >= 0 and t - fr_notes[i] < 1.2 else 0.0
            else:
                awake = 0.35 * smoothstep(T_DREAM - 0.5, T_DREAM + 2, t) + 0.65 * smoothstep(T_HAIL - 1, T_HAIL + 1.5, t)
                i = int(np.searchsorted(dream, t, side='right')) - 1
                flare = 0.6 * np.exp(-(t - dream[i]) / 0.5) if i >= 0 and t - dream[i] < 2 else 0.0
                flare = max(flare, pulse * smoothstep(T_HAIL - 1, T_HAIL, t))
            b = seen * (0.38 + 0.12 * breath * (1 - awake) + 0.4 * awake + 0.3 * flare)
            width = 18 + 10 * awake + 8 * flare
            fr += light(col, b * np.exp(-((d - p) / width) ** 2) + 0.35 * b * np.exp(-((d - p) / (70 + 60 * awake)) ** 2))
            fr += light(WHITE, 0.3 * seen * flare * np.exp(-((d - p) / 12) ** 2))
        for tn in NUDGES:                                   # rose against blue
            if tn <= t < tn + 0.8:
                age = t - tn
                wp = C['pos'][WOTAN][f]
                fr += light(ROSE, 0.7 * np.exp(-age / 0.25) * np.exp(-((d - wp) / 40) ** 2))
        if t > T_HAIL - 1:                                  # his blue rising to meet the castle's light
            up = smoothstep(T_HAIL - 1, T_HAIL + 3, t)
            wp = C['pos'][WOTAN][f]
            fr += light(BLUE, 0.4 * up * np.exp(-((d - wp) / 260) ** 2) * wing * (0.8 + 0.4 * pulse))
        out[f] = fr
    return np.clip(out, 0, 1)


def score(M, G):
    """Wagner's notes as a brass chorale over the strings, with timpani on the chorale's strong chords."""
    order = np.argsort(G.pd)
    xs, ds = G.pos[order, 0], G.pd[order]
    x0, x1 = xs.min(), xs.max()

    def pan_at(dd):
        x = np.interp(dd, ds, xs)
        return float(0.85 * (2 * (x - x0) / (x1 - x0) - 1))

    C = choreography(G)
    pf = pan_at(at(G, 'Porch Front', 0.5))
    pl, pr = pan_at(at(G, 'Porch Left', 0.5)), pan_at(at(G, 'Porch Right', 0.5))
    N = compose()
    o = Orchestra(M, level=LEVEL)

    def pan_of(who, t):
        return pan_at(np.interp(t, C['t'], C['pos'][who]))

    def chorale(t, d, m, v, loud):
        pan = (pl, pf, pr)[m % 3]
        if d < 0.45:                                    # the moving inner parts: strings
            o.play('violins' if m >= 62 else 'violas', m, t, d, v - 4, pan, 0.5)
        elif m >= 56:
            o.play('horns', m, t, d, v + 6, pan, 0.8)
            if loud and m >= 61:
                o.play('trumpets', m, t, d, v - 6, pan, 0.4)
                o.play('violins', m + 12, t, d, v - 14, -pan, 0.3)
        elif m >= 49:
            o.play('trombones', m, t, d, v + 6, pan, 0.8)
        else:
            o.play('tuba', m + (12 if m < 37 else 0), t, d, v + 6, 0.0, 0.75)
            o.play('basses', m, t, d, v - 4, 0.0, 0.5)

    for t, d, m, v, part, who in N:
        if part == 'ring':                              # the transformation: the arpeggios
            o.play('clarinets', m, t, d, v, pf + 0.2, 0.5)
            o.play('harp', m, t, d, v, pf - 0.2, 0.5)
            o.play('violins', m, t, d, v - 10, pf, 0.3)
        elif part == 'ringbass':
            o.play('horns', m, t, d, v, pf, 0.5)
            o.play('cellos', m, t, d, v - 6, 0.0, 0.5)
        elif part == 'val':
            chorale(t, d, m, v + 6 * who, False)
        elif part == 'fricka':                          # Fricka wakes: her line on oboe and violas
            o.play('oboes', m, t, d, v, pan_of(FRICKA, t), 0.7)
            o.play('violas', m, t, d, v - 8, pan_of(FRICKA, t), 0.5)
        elif part == 'fbass':
            o.play('cellos', m, t, d, v, -0.2, 0.6)
            if d > 0.5:
                o.play('basses', m, t, d, v - 8, 0.2, 0.5)
        elif part == 'hail':
            chorale(t, d, m, v + 10, True)
    for k, tc in enumerate(accents([e for e in N if e[4] == 'hail'], n=4, space=0.8)):
        o.hit('timpani', tc, 100 + 2 * min(k, 10), pitch=-5, gain=0.45, pan=pf)
    o.hit('cymbal swell', T_VAL[0] - 2.0, 80, gain=0.4, pan=pf)        # the castle stands
    o.hit('cymbal swell', T_CADENCE + 4 * HBEAT - 3.2, 100, gain=0.5)  # into the last fortissimo
    o.hit('crash', T_CADENCE + 4 * HBEAT, 118, gain=0.6)
    o.hit('timpani roll', T_CADENCE + 4 * HBEAT, 112, pitch=-5, gain=0.5, pan=pf)
