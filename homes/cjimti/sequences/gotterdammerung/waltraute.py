"""Waltraute: back on Brünnhilde's rock, a bright afternoon. She sits on the summit in silver, the Ring gold on her
hand, and every phrase of her love (Donington 87) sends a soft silver ripple over a calm gold-blue sky.

Thunder rolls far off. Out of the east, at the free end of Right, a storm cloud comes on the Ride (47): each phrase
a dark front of cloud racing the whole length of the house, every note of it an orange Valkyrie streak and the
runs cracking white with lightning, and on the Valkyries' cry (22a) Waltraute herself gallops in, a blaze of
Valkyrie orange over storm cloud, and lands below the summit in a burst.

She tells what has become of Wotan: the sky turns deep blue and every chord of Valhalla (63) slams a whole run
gold-white, while his grief (82) breathes slow blue waves out over the house. Then the Ring (8): she begs, and
gold surges run from Brünnhilde's hand to her and teal streaks of the Rhine pull at it from the east. Brünnhilde
refuses on her own motif (88): two silver shocks over the whole house and the Ring blazing. Waltraute flees on
the Ride with the storm behind her, racing out of the free end of Right, the clouds clear, and the afternoon sinks
toward a red dusk with Brünnhilde alone on the summit.

compose() holds every note; stage(), heat(), fire(), scene(), strand() and figure() are shared word for word by
the Prologue's scenes (see GD01)."""
import numpy as np
from pixelhome.audio import note
from pixelhome.fx import DT, hexc, light, smoothstep, nframes, keys, Flicker, smooth_noise, colormap
from pixelhome.leitmotifs import play

CODE = 'GD13'
TITLE = 'Waltraute'
KIND = 'show'
DESCRIPTION = ('A Valkyrie storms onto the rock out of a thundercloud and begs her sister to give the Ring back to '
               'the Rhine before the gods are destroyed. Brünnhilde refuses, and Waltraute flees in the storm.')
VOICEOVER = ('A storm comes racing over the mountain, and out of it rides a Valkyrie. '
             'She has come to beg her sister for the Ring.')

K = 6                                       # this scene's place on the Prologue's shared clock: T = t + 80 K
T_LOVE = [0.5, 6.0]                         # Brünnhilde's love, softly
T_THUNDER = 9.0
T_RIDE = [11.0, 14.6, 18.2]                 # the storm comes on the Ride
RBEAT = 0.3
T_CRY = 21.5                                # the Valkyries' cry: Waltraute lands
T_LAND = 23.0
T_VAL = [26.0, 31.5]                        # Valhalla
T_GRIEF = 37.0                              # Wotan's grief
T_RING = 46.0                               # she begs for the Ring
T_REFUSE = [54.0, 58.5]                     # Brünnhilde refuses
T_FLEE = 64.0                               # Waltraute flees on the Ride
T_GONE = 69.0
D = 80.0

NIGHT = hexc('#1a1070')
NIGHT2 = hexc('#3a1a9a')
STAR = hexc('#e0e8ff')
ROCK = hexc('#38468a')
DUSK = hexc('#7a40d0')
RED, ORANGE, AMBER = hexc('#ff2000'), hexc('#ff5000'), hexc('#ffb020')
FIRE = colormap([(0.0, hexc('#300400')), (0.3, RED), (0.55, ORANGE), (0.8, AMBER), (1.0, hexc('#fff0b0'))])
EAST = hexc('#ff2a10')
DAWN = colormap([(0.0, hexc('#ff1040')), (0.35, hexc('#ff6a10')), (0.7, hexc('#ffc020')), (1.0, hexc('#fff4d0'))])
DAY = hexc('#40b0ff')
SUN = hexc('#fff0a0')
NORN = hexc('#c8c8d8')
ROPE = hexc('#ffcc40')
HOT = hexc('#fff4c0')
VALHALLA = hexc('#fff0a0')
GODS = hexc('#1a3cff')
CHORD = hexc('#6a20ff')
WHITE = hexc('#ffffff')
SILVER = hexc('#f4f8ff')
GLINT = hexc('#ffd060')
GOLD = hexc('#ffaa00')
RINGRED = hexc('#ff1800')
WALTRAUTE = hexc('#ff9a20')
CLOUD = hexc('#2a3448')
BOLT = hexc('#e8f0ff')
RHINE = hexc('#0a7c8a')

START = dict(night=0.0, stars=0.0, rock=0.4, fire=0.2, east=0.0, dawn=0.12, hue=0.6, day=0.62, rope=0.0)
END = dict(night=0.15, stars=0.0, rock=0.35, fire=0.35, east=0.0, dawn=0.5, hue=0.22, day=0.15, rope=0.0)
BRUNNHILDE_AT = ('Porch Front', 0.6)
BRUNNHILDE_START = 0.9                      # her level at the start
BRUNNHILDE_END = ('Porch Front', 0.6, 0.85)     # (segment, u, level); the Ring's glint on her hand at 0.7 x level
WALTRAUTE_AT = ('Porch Right', 0.7)         # where she lands


def at(G, seg, u):
    """Path distance u of the way along a segment."""
    s = G.pd[G.seg[seg]]
    return float(s.min() + u * (s.max() - s.min()))


def stage(G):
    """Brünnhilde's rock and the sky as profiles over the house: the porch is the rock, the summit the middle of
    Porch Front; the wings and Side are sky, the east at the free end of Right. The Norns' three places."""
    d = G.pd
    rng = np.random.default_rng(1874)       # the same stars, clouds and flames in every scene, so the cuts match
    porch = np.isin(G.seg_of, ['Porch Left', 'Porch Front', 'Porch Right'])
    summit = at(G, 'Porch Front', 0.5)
    return dict(
        d=d, L=float(d.max()), summit=summit, porch=porch, sky=~porch,
        crag=porch * (0.7 + 0.3 * smooth_noise(rng, d, 40.0)),
        db=np.abs(d - summit),
        east=(~porch) * np.exp(-((d.max() - d) / 650) ** 2),
        twinkle=Flicker(rng, G.N, 0.3, 2.5),
        fl=Flicker(rng, G.N, 4.0, 11.0),
        fray=Flicker(rng, G.N, 1.5, 6.0),
        norns=[at(G, 'Left', 0.5), summit, at(G, 'Right', 0.5)],
    )


def heat(d, T):
    """Flame heat along the roofline (0..1): tongues of several sizes licking both ways."""
    h = (0.45 + 0.24 * np.sin(2 * np.pi * (d / 173 - 0.53 * T)) + 0.2 * np.sin(2 * np.pi * (d / 109 + 0.71 * T) + 1.3)
         + 0.13 * np.sin(2 * np.pi * (d / 67 - 1.37 * T) + 2.1) + 0.09 * np.sin(2 * np.pi * (d / 41 + 1.9 * T) + 0.4))
    swell = 0.75 + 0.25 * np.sin(2 * np.pi * (d / 410 + 0.23 * T)) * np.sin(2 * np.pi * (d / 260 - 0.31 * T) + 0.7)
    return np.clip((h * swell - 0.15) * 1.5, 0, 1)


def fire(S, T, ring, wide=0.0, boost=0.0):
    """The magic fire: `ring` round the rock (the porch, leaving the summit clear), `wide` out over the sky."""
    q = np.clip(heat(S['d'], T) + 0.18 * S['fl'](T) + 0.3 * boost, 0, 1)
    clear = 1 - 0.8 * np.exp(-(S['db'] / 42) ** 2)
    lvl = (ring * S['porch'] + wide * S['sky']) * clear
    return light(FIRE(q), lvl * (0.45 + 0.7 * q))


def scene(S, T, lv):
    """The sky, the rock, the fire and the standing rope at shared time T with levels lv (night, stars, rock, fire,
    east, dawn, hue, day, rope)."""
    d = S['d']
    u = 0.5 + 0.3 * np.sin(2 * np.pi * (d / 520 - 0.04 * T)) + 0.2 * np.sin(2 * np.pi * (d / 190 + 0.07 * T) + 1.1)
    sk = NIGHT + (NIGHT2 - NIGHT) * u[:, None]
    fr = light(sk, lv['night'] * (0.7 + 0.3 * u) * S['sky'])
    fr += light(STAR, lv['stars'] * S['sky'] * np.clip(S['twinkle'](T) - 0.9, 0, None) ** 2)
    rk = ROCK + (DUSK - ROCK) * (0.25 + 0.45 * u)[:, None]
    fr += light(rk, lv['rock'] * S['crag'])
    fr += light(EAST, lv['east'] * S['east'] * (0.8 + 0.2 * u))
    fr += light(DAWN(np.clip(lv['hue'] + 0.2 * (u - 0.5), 0, 1)), lv['dawn'] * (0.8 + 0.2 * u))
    fr += light(DAY + (SUN - DAY) * (0.4 * u)[:, None], lv['day'] * (0.75 + 0.25 * u))
    fr += fire(S, T, lv['fire'])
    if lv['rope'] > 0:
        a, b = S['norns'][0], S['norns'][2]
        fr += strand(S, a, b, 1.0, lv['rope'], T)
    return fr


def strand(S, a, b, u, lvl, T, fray=0.0):
    """The rope from path distance a toward b, laid u of the way (0..1), shimmering; a white-hot head while it
    flies. fray (0..1) breaks it into flickering gaps."""
    d = S['d']
    head = a + (b - a) * u
    lo, hi = min(a, head), max(a, head)
    on = smoothstep(lo - 8, lo + 8, d) * smoothstep(hi + 8, hi - 8, d)
    shimmer = 0.72 + 0.28 * np.sin(2 * np.pi * (d / 55 - 1.4 * T))
    gaps = np.clip(1 - fray * (0.55 + 0.7 * S['fray'](T)), 0, 1)
    fr = light(ROPE, lvl * on * shimmer * gaps)
    if u < 1:
        fr += light(HOT, min(1.0, 1.3 * lvl + 0.3) * np.exp(-((d - head) / 12) ** 2))
    return fr


def figure(fr, S, p, col, lvl, w=16.0):
    """A person at path distance p: a body that stands in front of the sky, and a halo."""
    body = np.exp(-((S['d'] - p) / w) ** 2)
    fr = fr * (1 - 0.85 * min(1.0, lvl / 0.2) * body)[:, None]
    return fr + light(col, lvl * body) + light(col, 0.35 * lvl * np.exp(-((S['d'] - p) / (3 * w)) ** 2))


PAIRS = [(0, 1), (1, 2), (2, 0)]            # who throws to whom, round and round


def compose():
    """Every note: (time, seconds, midi, velocity, part, k)."""
    N = []

    def add(t, d, m, v, part, k=None):
        N.append((float(t), float(d), note(m) if isinstance(m, str) else int(m), int(v), part, k))

    for k, t0 in enumerate(T_LOVE):
        for t, m, v, d in play('brunnhilde_love', t0, 0.42, 0, 70 + 4 * k):
            add(t, d, m, v, 'love', k)
    add(T_THUNDER, 3.0, 'B1', 96, 'thunder')
    for k, t0 in enumerate(T_RIDE):
        for t, m, v, d in play('ride', t0, RBEAT, 0, 96 + 8 * k):
            add(t, d, m, v, 'ride', k)
        for j in range(12):
            add(t0 + j * RBEAT, 0.25, ('B1', 'Gb2')[j % 2], 90 + 6 * k, 'gallop', k)
    for t, m, v, d in play('valkyrie_cry', T_CRY, 0.45, -12, 112):
        add(t, d, m, v, 'cry')
    add(T_LAND, 0.1, 'B1', 124, 'land')
    for k, t0 in enumerate(T_VAL):
        for t, m, v, d in play('valhalla', t0, 0.7, 0, 104 + 6 * k):
            add(t, d, m, v, 'valhalla', k)
    for t, m, v, d in play('wotan_grief', T_GRIEF, 0.3, -12, 96):
        add(t, d, m, v, 'grief')
    for t, m, v, d in play('ring', T_RING, 0.6, -5, 104):
        add(t, d, m, v, 'ring')
    for k, t0 in enumerate(T_REFUSE):
        for t, m, v, d in play('brunnhilde', t0, 0.5, 0, 112 + 6 * k):
            add(t, d, m, v, 'refuse', k)
    for t, m, v, d in play('ride', T_FLEE, RBEAT, 0, 108):
        add(t, d, m, v, 'ride', 3)
    for j in range(16):
        add(T_FLEE + j * RBEAT, 0.25, ('B1', 'Gb2')[j % 2], 100 - 3 * j, 'gallop', 3)
    for m in ('B2', 'D3', 'Gb3'):
        add(T_GONE + 1.0, D - T_GONE - 1.0, m, 54, 'dusk')
    return sorted(N, key=lambda e: e[0])


def bolts():
    """Lightning while the storm is overhead: [(time, run)]."""
    runs = ['Right', 'Porch Right', 'Left', 'Side', 'Porch Left', 'Right', 'Left', 'Side']
    ts = [t0 + 0.05 + 1.2 * j for t0 in T_RIDE for j in range(3)] + [T_CRY + 0.1, T_LAND] \
        + [T_FLEE + 0.05 + 1.2 * j for j in range(4)]
    return [(float(t), runs[i % len(runs)]) for i, t in enumerate(sorted(ts))]


def flight(G, t):
    """Where Waltraute is at time t (None before she arrives or after she has gone)."""
    L, land = G.pd.max(), at(G, *WALTRAUTE_AT)
    if t < T_RIDE[0] + 3.0 or t > T_GONE + 0.5:
        return None
    if t < T_LAND:
        return L + 40 + (land - L - 40) * smoothstep(T_RIDE[0] + 3.0, T_LAND, t) ** 0.7
    if t < T_FLEE + 0.5:
        return land + 6 * np.sin(2 * np.pi * t / 0.9)
    return land + (L + 60 - land) * smoothstep(T_FLEE + 0.5, T_GONE, t) ** 1.6


def render(G, seed=13):
    F = nframes(D)
    out = np.zeros((F, G.N, 3))
    S = stage(G)
    d, L = S['d'], S['L']
    N = compose()
    p_b = at(G, *BRUNNHILDE_AT)
    love = [e for e in N if e[4] == 'love']
    rides = [e for e in N if e[4] == 'ride']
    val = [e for e in N if e[4] == 'valhalla']
    vstep = sorted({e[0] for e in val})
    grief = [e for e in N if e[4] == 'grief']
    ring = sorted({e[0] for e in N if e[4] == 'ring'})
    refuse = sorted({e[0] for e in N if e[4] == 'refuse'})
    runs = ['Left', 'Porch Left', 'Porch Front', 'Porch Right', 'Right', 'Side']
    jag = np.random.default_rng(seed).uniform(0.4, 1.0, G.N)

    for f in range(F):
        t = f * DT
        T = t + 80 * K
        storm = smoothstep(T_THUNDER, T_RIDE[2], t) * (1 - smoothstep(T_VAL[0] - 1, T_VAL[0] + 3, t)) \
            + smoothstep(T_FLEE - 1, T_FLEE + 1, t) * (1 - smoothstep(T_GONE - 1, T_GONE + 4, t))
        gods = smoothstep(T_VAL[0] - 1, T_VAL[0] + 1, t) * (1 - smoothstep(T_RING + 4, T_REFUSE[0], t))
        lv = {k: keys(t, [(0, START[k]), (T_GONE, START[k]), (D - 2, END[k])]) for k in START}
        lv['day'] *= 1 - 0.75 * min(1.0, storm + gods)
        lv['dawn'] *= 1 - 0.7 * min(1.0, storm + gods)
        fr = scene(S, T, lv)

        # the storm cloud: dark rolling cloud over the sky, lightning cracking whole runs
        if storm > 0:
            if t < T_VAL[0]:
                front = L - (L + 300) * smoothstep(T_THUNDER, T_RIDE[2] + 2, t)
                cover = smoothstep(front - 150, front + 150, d) * storm
            elif t < T_FLEE:
                cover = storm * np.ones_like(d)
            else:
                front = (L + 300) * smoothstep(T_FLEE, T_GONE + 2, t) - 150
                cover = smoothstep(front - 150, front + 150, d) * storm
            u = 0.5 + 0.5 * np.sin(2 * np.pi * (d / 300 + 0.6 * t))
            fr = fr * (1 - 0.7 * cover * S['sky'])[:, None]
            fr += light(CLOUD + (BOLT - CLOUD) * 0.2 * u[:, None], 0.85 * cover * (0.7 + 0.3 * u) * S['sky'])
            if t < T_VAL[0] and 0 < front < L:
                fr += light(BOLT, 0.5 * storm * np.exp(-((d - front) / 40) ** 2))
        for tb, run in bolts():
            a = t - tb
            if 0 <= a < 0.8:
                env = min(1.0, np.exp(-a / 0.08) + 0.8 * np.exp(-((a - 0.15) / 0.04) ** 2))
                fr += light(BOLT, env * (G.seg_of == run) * jag)

        # the Ride: every note an orange streak racing in from the east with the cloud front behind it
        for t0, dur, m, v, part, k in rides:
            a = t - t0
            if 0 <= a < 2.2 and m >= note('B3'):
                head = L - 1100 * a if k < 3 else at(G, *WALTRAUTE_AT) + 1100 * a
                trail = (d - head) * (1 if k < 3 else -1)
                fr += light(WALTRAUTE, 1.0 * np.exp(-a / 0.9) * np.exp(-((d - head) / 80) ** 2))
                fr += light(WALTRAUTE, 0.7 * np.exp(-a / 0.7) * (trail > 0) * np.exp(-np.clip(trail, 0, None) / 300))

        # Valhalla: the sky goes deep blue, every chord slams one whole run gold-white
        if gods > 0:
            fr += light(GODS, 0.75 * gods * S['sky'] * (0.8 + 0.2 * np.sin(2 * np.pi * (d / 600 - 0.1 * t))))
        for j, t0 in enumerate(vstep):
            a = t - t0
            if 0 <= a < 1.6:
                run = G.seg_of == runs[j % len(runs)]
                fr += light(VALHALLA, 0.95 * np.exp(-a / 0.55) * run)
                fr += light(GODS, 0.5 * np.exp(-a / 0.9) * run)

        # Wotan's grief: slow blue waves breathing out from the summit, one per note
        for t0, dur, m, v, part, k in grief:
            a = t - t0
            if 0 <= a < 3.0:
                r = 1200 * (1 - np.exp(-a / 1.1))
                fr += light(GODS, 0.85 * np.exp(-a / 1.4) * np.exp(-((np.abs(d - S['summit']) - r) / 160) ** 2))

        # the Ring: gold surges from Brünnhilde's hand, and the Rhine pulling at it from the east
        p_w = flight(G, t)
        for t0 in ring:
            a = t - t0
            if 0 <= a < 1.4:
                tgt = p_w if p_w is not None else L
                head = p_b + (tgt - p_b) * min(1.0, a / 0.6)
                lo, hi = min(p_b, head), max(p_b, head)
                fr += light(GOLD, 0.6 * np.exp(-a / 0.6) * smoothstep(lo - 30, lo, d) * smoothstep(hi + 30, hi, d))
                fr += light(GOLD, 1.0 * np.exp(-a / 0.6) * np.exp(-((d - head) / 60) ** 2))
                fr += light(RINGRED, 0.7 * np.exp(-a / 0.3) * np.exp(-((d - p_b) / 35) ** 2))
        if T_RING <= t < T_REFUSE[0]:
            a = t - T_RING
            for j in range(4):
                c = (L - ((a * 900 + j * 420) % 1700))
                fr += light(RHINE, 0.9 * np.exp(-((d - c) / 140) ** 2) * (c > p_b))

        # Brünnhilde refuses: silver shocks over the whole house, the Ring blazing on her hand
        for t0 in refuse:
            a = t - t0
            if 0 <= a < 1.8:
                r = 1600 * (1 - np.exp(-a / 0.5))
                fr += light(SILVER, 0.95 * np.exp(-a / 0.8) * np.exp(-((np.abs(d - p_b) - r) / 110) ** 2))
                fr += light(GOLD, 0.8 * np.exp(-a / 0.4) * np.exp(-((d - p_b) / 40) ** 2))
        for t0 in T_REFUSE:
            a = t - t0
            if 0 <= a < 0.5:
                fr += light(SILVER, 0.45 * np.exp(-a / 0.12))

        # Brünnhilde's love: soft silver ripples
        for t0, dur, m, v, part, k in love:
            a = t - t0
            if 0 <= a < 2.2 and dur >= 0.4:
                r = 900 * a
                fr += light(SILVER, 0.8 * np.exp(-a / 1.0) * np.exp(-((np.abs(d - p_b) - r) / 150) ** 2))
                fr += light(GOLD, 0.6 * np.exp(-a / 0.3) * np.exp(-((d - p_b - 9) / 20) ** 2))

        # Waltraute: a blaze of orange over storm cloud; a burst where she lands
        if p_w is not None:
            fr += light(CLOUD, 0.6 * np.exp(-((d - p_w) / 90) ** 2))
            fr += light(WALTRAUTE, 0.45 * np.exp(-((d - p_w) / 160) ** 2) * (0.7 + 0.3 * np.sin(2 * np.pi * t / RBEAT / 2)))
            fr = figure(fr, S, p_w, WALTRAUTE, 1.0, w=24)
            fr += light(WHITE, 0.5 * np.exp(-((d - p_w) / 5) ** 2))
        if T_LAND <= t < T_LAND + 1.5:
            a = t - T_LAND
            pl = at(G, *WALTRAUTE_AT)
            fr += light(WALTRAUTE, 0.9 * np.exp(-a / 0.5) * np.exp(-((np.abs(d - pl) - 1200 * a) / 90) ** 2))

        # Brünnhilde on the summit, the Ring glinting on her hand
        lvl = keys(t, [(0, BRUNNHILDE_START), (T_REFUSE[0], 0.95), (T_GONE, 0.95), (D - 2, BRUNNHILDE_END[2])])
        fr = figure(fr, S, p_b, SILVER, lvl)
        fr += light(GOLD, 0.7 * lvl * np.exp(-((d - p_b - 9) / 5) ** 2))
        out[f] = fr
    return np.clip(out, 0, 1)


def score(M, G):
    from pixelhome.audio import SR, whoosh
    order = np.argsort(G.pd)
    xs, ds = G.pos[order, 0], G.pd[order]
    x0, x1 = xs.min(), xs.max()

    def pan_at(dd):                         # path distance -> left/right across the facade, from the street
        x = np.interp(dd, ds, xs)
        return float(0.85 * (2 * (x - x0) / (x1 - x0) - 1))

    for name, gain, rev in (('low', 0.3, 0.25), ('strings', 0.26, 0.32), ('brass', 0.28, 0.3), ('perc', 0.28, 0.3),
                            ('winds', 0.24, 0.35), ('fx', 0.08, 0.3)):
        M.bus(name, gain=gain, reverb=rev)
    vln = M.sampler('Strings/Violin Section/susVib/*.wav', tune=-12)
    vc = M.sampler('Strings/Cello Section/susvib/*.wav', tune=-12)
    vcs = M.sampler('Strings/Cello Section/spic/*.wav', tune=-12)
    cb = M.sampler('Strings/Solo Contrabass/SusNV/*.wav', tune=-12)
    horn = M.sampler('Brass/F Horn/sus/*.wav', tune=-12)
    tpt = M.sampler('Brass/Trumpet/sus/*.wav', tune=-12)
    tbn = M.sampler('Brass/Tenor Trombone/sus/*.wav', tune=-12)
    tuba = M.sampler('Brass/Tuba/sus/*.wav', tune=-12)
    fl = M.sampler('Woodwinds/Flute/susNV/*.wav', tune=-12)
    timp = M.hits('Percussion/Timpani/Timpani1_Hit*.wav')
    roll = M.hits('Percussion/Timpani/Rolls/*.wav')
    crash = M.hits('Percussion/cymbal-crash1_f*.wav')

    def hold(bus, s, m, t0, t1, vel, pan=0.0, step=2.5, rise=1.5, fall=1.5, gain=1.0):
        """A note sustained from t0 to t1 (and released over `fall`): overlapping windows of its sample."""
        a0 = s.play(m, vel)
        step = min(step, (a0.shape[1] / SR - 0.35) / 2)
        w = int(2 * step * SR)
        win = np.hanning(w)
        t = t0 - step
        while t < t1 + fall:
            a = s.play(m, vel)[:, int(0.25 * SR):int(0.25 * SR) + w]
            a = a * win[:a.shape[1]]
            tt = t + np.arange(a.shape[1]) / SR
            env = np.clip((tt - t0) / rise, 0, 1) * np.clip(1 - (tt - t1) / fall, 0, 1)
            M.add(bus, a * env, t, gain, pan)
            t += step

    S = stage(G)
    sb = pan_at(at(G, *BRUNNHILDE_AT))
    east = pan_at(S['L'] - 60)

    def pan_w(t):
        p = flight(G, t)
        return pan_at(p) if p is not None else east

    for t, d, m, v, part, k in compose():
        if part == 'love':
            if d > 1.0:
                hold('strings', vln, m, t, t + d, v, sb, rise=0.4, fall=1.0, gain=0.6)
            else:
                M.add('strings', vln.play(m, v, dur=d * 1.1, release=0.3), t, 0.6, sb)
        elif part == 'thunder':
            M.add('perc', roll.play(v, pitch=-6, dur=3.5), t, 0.8, east)
        elif part == 'ride':
            p = pan_w(t)
            if m >= note('D4'):
                M.add('brass', tpt.play(m - 12, v, dur=d * 1.05, release=0.2), t, 0.75, p)
            M.add('brass', horn.play(m, v - 6, dur=d * 1.05, release=0.2), t, 0.8, p)
            M.add('low', tbn.play(m - 12, v - 12, dur=d * 1.05, release=0.2), t, 0.6, p)
        elif part == 'gallop':
            M.add('strings', vcs.play(m + 12, v), t, 0.7, pan_w(t))
        elif part == 'cry':
            M.add('brass', horn.play(m, v, dur=d * 1.1, release=0.2), t, 0.8, pan_w(t))
        elif part == 'land':
            M.add('perc', crash.play(v), t, 0.9, pan_w(t))
            M.add('perc', timp.play(v, pitch=-5), t, 0.9, pan_w(t))
            M.add('fx', whoosh(1.0, 4000, 500, 0.7, seed=13), t - 0.6, 1.0, pan_w(t))
        elif part == 'valhalla':
            if m >= note('Db4'):
                hold('brass', horn, m - 12, t, t + d, v - 4, 0.0, rise=0.2, fall=1.0, gain=0.7)
            elif m >= note('Db3'):
                hold('brass', tbn, m, t, t + d, v, 0.0, rise=0.2, fall=1.0, gain=0.75)
            else:
                hold('low', tuba, m, t, t + d, v, 0.0, rise=0.2, fall=1.0, gain=0.8)
                M.add('perc', timp.play(v - 20, pitch=-4), t, 0.5, 0.0)
        elif part == 'grief':
            if d > 1.0:
                hold('brass', tbn, m, t, t + d, v, sb * 0.5, rise=0.5, fall=1.0, gain=0.75)
            else:
                M.add('brass', tbn.play(m, v, dur=d * 1.1, release=0.3), t, 0.75, sb * 0.5)
            M.add('low', cb.play(m - 12, v - 16, dur=d * 1.1, release=0.3), t, 0.5, 0.0)
        elif part == 'ring':
            if d > 1.0:
                hold('winds', fl, m, t, t + d, v, sb, rise=0.2, fall=0.8, gain=0.75)
            else:
                M.add('winds', fl.play(m, v, dur=d * 1.05, release=0.25), t, 0.8, sb)
            M.add('strings', vc.play(m - 12, v - 16, dur=d * 1.05, release=0.25), t, 0.5, sb)
        elif part == 'refuse':
            if d > 1.0:
                hold('brass', horn, m, t, t + d, v, sb, rise=0.15, fall=1.0, gain=0.85)
            else:
                M.add('brass', horn.play(m, v, dur=d * 1.05, release=0.3), t, 0.9, sb)
            if t in T_REFUSE:
                M.add('perc', crash.play(110), t, 0.7, sb)
                M.add('perc', timp.play(118, pitch=-3), t, 0.9, sb)
        elif part == 'dusk':
            hold('strings', vc, m, t, t + d, v, sb * 0.6, rise=3.0, fall=1.5, gain=0.55)
    for tb, run in bolts():
        M.add('perc', roll.play(88, pitch=-2, dur=1.4), tb, 0.45, pan_at(at(G, run, 0.5)))
