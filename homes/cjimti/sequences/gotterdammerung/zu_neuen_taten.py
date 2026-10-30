"""Zu neuen Taten: full morning on Brünnhilde's rock, and Siegfried must go out to new deeds. His heroism
(Donington 78) strides out on the horns, and every note of it is an emerald wave out from him to both ends of
the house, one run after another flashing green. Brünnhilde answers with her love (87) in the violins: each long
note swells a whole run silver, the short ones throw gold glints, and her silver rolls out over the house.

Then the gift. The Ring (8) sounds in the woodwinds and a ring of gold light leaves Siegfried's hand and travels
across the summit to her; when it reaches her the whole house flashes gold, and a gold loop races round the
roofline both ways and meets itself. In return she gives him her horse Grane: the Valkyries' gallop (47) on the
timpani and low strings, and the gallop itself is light, great rhythmic sweeps of silver and white thundering
along the house on every beat, faster and wider each time, from her end out to the free end of Right and back.
To finish his heroism comes round again on the full brass, emerald and silver trading whole runs at every note,
and it settles into the bright morning with the two of them on the summit, the Ring glinting on her hand.

compose() holds every note; stage(), heat(), fire(), scene(), strand() and figure() are shared word for word by
the Prologue's scenes (see GD01)."""
import numpy as np
from pixelhome.audio import note
from pixelhome.fx import DT, hexc, light, smoothstep, nframes, keys, Flicker, smooth_noise, colormap
from pixelhome.leitmotifs import play

CODE = 'GD04'
TITLE = 'Zu neuen Taten'
KIND = 'show'
DESCRIPTION = ('Siegfried must ride out to new adventures. He gives Brünnhilde the Ring as a pledge, a gold flash '
               'that races round the house, and she gives him her horse Grane, galloping in silver sweeps.')
VOICEOVER = ('A hero has to go out into the world. He leaves her the Ring, and she gives him her horse.')

K = 3                                       # this scene's place on the Prologue's shared clock: T = t + 80 K
T_HERO = 1.5                                # his heroism, horns
HBEAT = 0.42
T_LOVE = 12.5                               # her love, violins
LBEAT = 0.4
T_RING = 27.0                               # the Ring motif: the gift leaves his hand
RBEAT = 0.5
T_GIVEN = 32.0                              # it reaches her: the gold flash
T_GRANE = [37.0, 41.0, 45.0, 49.0]          # Grane: the gallop, four times
GBEAT = 0.62
T_HERO2 = 55.0                              # his heroism on the full brass
HBEAT2 = 0.38
T_SETTLE = 66.0
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
SIEGFRIED = hexc('#00ff40')
HEAD = hexc('#e8ffe8')
BRUNNHILDE = hexc('#f4f8ff')
GLINT = hexc('#ffd060')
GOLD = hexc('#ffaa00')

START = dict(night=0.0, stars=0.0, rock=0.35, fire=0.15, east=0.0, dawn=0.75, hue=0.62, day=0.3, rope=0.0)
END = dict(START)                           # where GD05 picks the morning up
SIEGFRIED_START = ('Porch Front', 0.35, 0.85)   # (segment, u, level)
BRUNNHILDE_START = ('Porch Front', 0.6, 0.9)
SIEGFRIED_END = SIEGFRIED_START
BRUNNHILDE_END = BRUNNHILDE_START
RING_ON_HER = 0.55                          # the Ring's glint on her hand at the end: level, 9 units left of her


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

    for t, m, v, d in play('siegfried_heroism', T_HERO, HBEAT, 12, 104):
        add(t, d, m, v, 'hero', 0)
    for t, m, v, d in play('brunnhilde_love', T_LOVE, LBEAT, -5, 96):
        add(t, d, m, v, 'love')
    for t, m, v, d in play('ring', T_RING, RBEAT, 0, 92):
        add(t, d, m, v, 'ring')
    add(T_GIVEN, 0.1, 'C1', 124, 'given')
    for k, t0 in enumerate(T_GRANE):
        for t, m, v, d in play('ride', t0, GBEAT, -12 + 2 * k, 100 + 6 * k):
            add(t, d, m, v, 'grane', k)
        for j in range(6):
            add(t0 + j * GBEAT, 0.2, 'Gb1' if j % 2 else 'B1', 96 + 6 * k, 'gallop', k)
    for t, m, v, d in play('siegfried_heroism', T_HERO2, HBEAT2, 12, 122):
        add(t, d, m, v, 'hero', 1)
    for m in ('Eb1', 'Bb1', 'Eb2', 'G2', 'Bb2', 'Eb3'):
        add(T_SETTLE, D - T_SETTLE, m, 68, 'settle')
    add(0.0, T_RING, 'Eb1', 56, 'pedal')
    return sorted(N, key=lambda e: e[0])


def runs_by_order():
    """The six runs, in path order."""
    return ['Side', 'Left', 'Porch Left', 'Porch Front', 'Porch Right', 'Right']


def render(G, seed=4):
    F = nframes(D)
    out = np.zeros((F, G.N, 3))
    S = stage(G)
    d, L = S['d'], S['L']
    N = compose()
    p_s, p_b = at(G, *SIEGFRIED_START[:2]), at(G, *BRUNNHILDE_START[:2])
    hero = [e for e in N if e[4] == 'hero']
    love = [e for e in N if e[4] == 'love']
    ring_on = sorted({e[0] for e in N if e[4] == 'ring'})
    gallop = sorted(e[0] for e in N if e[4] == 'gallop')
    grane = [e for e in N if e[4] == 'grane']
    runs = runs_by_order()
    masks = {r: (G.seg_of == r) for r in runs}
    hero_on = [sorted({e[0] for e in hero if e[5] == k}) for k in range(2)]

    for f in range(F):
        t = f * DT
        T = t + 80 * K
        dim = keys(t, [(0, 1.0), (3.0, 0.42), (T_RING - 0.5, 0.42), (T_RING + 1, 0.22), (T_GIVEN, 0.22),
                       (T_GIVEN + 1.5, 0.45), (T_SETTLE, 0.45), (D - 1.0, 1.0)])
        lv = dict(START)
        lv['dawn'] = START['dawn'] * dim
        lv['day'] = START['day'] * dim
        fr = scene(S, T, lv)

        # his heroism: an emerald wave out from him on every note, and the runs flashing green one after another
        for k in range(2):
            for j, t0 in enumerate(hero_on[k]):
                a = t - t0
                if not 0 <= a < 2.0:
                    continue
                r = 1500 * (1 - np.exp(-a / 0.7))
                g = 0.95 + 0.15 * k
                fr += light(SIEGFRIED, g * np.exp(-a / 0.9) * np.exp(-((np.abs(d - p_s) - r) / 170) ** 2))
                run = runs[(j * (2 + k)) % 6]
                col = SIEGFRIED if (k == 0 or j % 2 == 0) else BRUNNHILDE
                fr += light(col, (0.8 + 0.2 * k) * np.exp(-a / 0.4) * masks[run])

        # her love: each long note swells a whole run silver, the short ones throw gold glints, silver rolls out
        for j, (t0, dur, m, v, part, k) in enumerate(love):
            a = t - t0
            if not 0 <= a < dur + 1.5:
                continue
            env = smoothstep(0, 0.12, a) * np.exp(-max(a - dur, 0) / 0.5)
            if dur >= 0.9:
                fr += light(BRUNNHILDE, 0.9 * env * masks[runs[(m * 5) % 6]] * (0.8 + 0.2 * np.sin(4 * a)))
                r = 1300 * (1 - np.exp(-a / 0.8))
                fr += light(BRUNNHILDE, 0.85 * np.exp(-a / 1.0) * np.exp(-((np.abs(d - p_b) - r) / 150) ** 2))
            else:
                q = p_b + ((m * 97) % 900 - 450)
                fr += light(GLINT, 1.0 * np.exp(-a / 0.35) * np.exp(-((d - q) / 45) ** 2))

        # the gift: a ring of gold light travelling from his hand to hers, on every note of the Ring a pulse
        if T_RING <= t < T_GIVEN + 0.2:
            u = smoothstep(T_RING, T_GIVEN, t)
            q = p_s + (p_b - p_s) * u
            j = int(np.searchsorted(ring_on, t, side='right')) - 1
            pulse = np.exp(-(t - ring_on[j]) / 0.25) if j >= 0 else 0.0
            ring = np.exp(-((np.abs(d - q) - 10 - 6 * pulse) / 4) ** 2)
            fr += light(GOLD, (0.9 + 0.3 * pulse) * ring)
            fr += light(GOLD, 0.35 * pulse * np.exp(-((d - q) / 220) ** 2))
            fr += light(RED, 0.2 * pulse * np.exp(-((d - q) / 40) ** 2))
        # it reaches her: the whole house flashes gold, a gold loop races round both ways
        if T_GIVEN <= t < T_GIVEN + 4.0:
            a = t - T_GIVEN
            fr += light(GOLD, 0.95 * np.exp(-a / 0.6))
            fr += light(SUN, 0.7 * np.exp(-a / 0.15))
            for sgn in (-1, 1):
                q = p_b + sgn * 900 * a
                fr += light(GOLD, np.exp(-a / 1.6) * np.exp(-((d - q) / 90) ** 2))
                fr += light(HOT, 0.8 * np.exp(-a / 1.6) * np.exp(-((d - q) / 18) ** 2))

        # Grane: the gallop, every hoofbeat a sweep of silver and white thundering along the house
        for i, t0 in enumerate(gallop):
            a = t - t0
            if not 0 <= a < 1.3:
                continue
            k = min(3, i // 6)
            sgn = 1 if i % 2 == 0 else -1
            start = p_b if sgn > 0 else L
            q = start + sgn * (1300 + 300 * k) * a
            w = 110 + 50 * k
            fr += light(BRUNNHILDE, (0.95 + 0.1 * k) * np.exp(-a / 0.6) * np.exp(-((d - q) / w) ** 2))
            fr += light(WHITE, 0.55 * np.exp(-a / 0.3) * np.exp(-((d - q) / (w / 3)) ** 2))
            fr += light(DAY, 0.35 * np.exp(-a / 0.2) * masks[runs[(i + 3) % 6]])
        for t0, dur, m, v, part, k in grane:
            a = t - t0
            if 0 <= a < 0.5 and dur >= 0.9 * GBEAT:
                fr += light(GLINT, 0.6 * np.exp(-a / 0.15) * np.exp(-((d - p_b) / 160) ** 2))

        # settling: the two answer each other in great breaths of emerald and silver over the house, and the
        # Ring glints chase out from her hand
        for j, t0 in enumerate(np.arange(T_SETTLE, D - 3.0, 2.4)):
            a = t - t0
            if 0 <= a < 2.4:
                p, col = (p_s, SIEGFRIED) if j % 2 == 0 else (p_b, BRUNNHILDE)
                g = 0.85 * (1 - smoothstep(D - 6, D - 2, t))
                r = 1400 * (1 - np.exp(-a / 0.9))
                fr += light(col, g * np.exp(-a / 1.0) * np.exp(-((np.abs(d - p) - r) / 220) ** 2))
                fr += light(GOLD, g * np.exp(-a / 0.8) * np.exp(-((np.abs(d - p_b) - 1.3 * r) / 30) ** 2))

        # the two of them on the summit; she wears the Ring from the moment it reaches her
        hit = max([t0 for t0 in hero_on[0] + hero_on[1] if t0 <= t], default=-9)
        ls = SIEGFRIED_START[2] * (1 + 0.25 * np.exp(-(t - hit) / 0.2))
        fr = figure(fr, S, p_s, SIEGFRIED, ls)
        fr += light(HEAD, 0.7 * ls * np.exp(-((d - p_s) / 6) ** 2))
        lb = BRUNNHILDE_START[2]
        fr = figure(fr, S, p_b, BRUNNHILDE, lb)
        fr += light(GLINT, 0.5 * lb * np.exp(-((d - p_b - 9) / 5) ** 2))
        if t >= T_GIVEN:
            fr += light(GOLD, RING_ON_HER * smoothstep(T_GIVEN, T_GIVEN + 0.5, t) * np.exp(-((d - p_b + 9) / 4) ** 2))
        out[f] = fr
    return np.clip(out, 0, 1)


def score(M, G):
    from pixelhome.audio import SR
    order = np.argsort(G.pd)
    xs, ds = G.pos[order, 0], G.pd[order]
    x0, x1 = xs.min(), xs.max()

    def pan_at(dd):                         # path distance -> left/right across the facade, from the street
        x = np.interp(dd, ds, xs)
        return float(0.85 * (2 * (x - x0) / (x1 - x0) - 1))

    for name, gain, rev in (('low', 0.32, 0.25), ('strings', 0.3, 0.35), ('brass', 0.32, 0.3), ('perc', 0.3, 0.3),
                            ('winds', 0.26, 0.35), ('harp', 0.22, 0.4), ('warm', 0.28, 0.4)):
        M.bus(name, gain=gain, reverb=rev)
    vc = M.sampler('Strings/Cello Section/susvib/*.wav', tune=-12)
    vcs = M.sampler('Strings/Cello Section/spic/*.wav', tune=-12)
    vln = M.sampler('Strings/Violin Section/susVib/*.wav', tune=-12)
    cb = M.sampler('Strings/Solo Contrabass/SusNV/*.wav', tune=-12)
    harp = M.sampler('Strings/Harp/*.wav')
    horn = M.sampler('Brass/F Horn/sus/*.wav', tune=-12)
    tpt = M.sampler('Brass/Trumpet/sus/*.wav', tune=-12)
    tbn = M.sampler('Brass/Tenor Trombone/sus/*.wav', tune=-12)
    clar = M.sampler('Woodwinds/Clarinet/susLong/*.wav', tune=-12)
    bsn = M.sampler('Woodwinds/Bassoon/sus/*.wav', tune=-12)
    timp = M.hits('Percussion/Timpani/Timpani1_Hit*.wav')
    crash = M.hits('Percussion/cymbal-crash1_f*.wav')
    glock = M.sampler('Percussion/Glock/*.wav')

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
    ss = pan_at(at(G, *SIEGFRIED_START[:2]))
    sb = pan_at(at(G, *BRUNNHILDE_START[:2]))
    east = pan_at(S['L'] - 100)
    for t, d, m, v, part, k in compose():
        if part == 'hero':
            if d > 1.0:
                hold('brass', horn, m, t, t + d * 0.95, v, ss, rise=0.1, fall=0.8, gain=0.8)
            else:
                M.add('brass', horn.play(m, v, dur=d * 1.05, release=0.25), t, 0.85, ss)
            M.add('low', vc.play(m - 12, v - 12, dur=d * 1.05, release=0.25), t, 0.6, ss)
            if k == 1:
                M.add('brass', tbn.play(m - 12, v - 8, dur=d * 1.05, release=0.25), t, 0.7, 0.0)
                if m >= note('Bb3') + 12:
                    M.add('brass', tpt.play(m, v - 14, dur=d * 1.05, release=0.25), t, 0.5, 0.0)
                if d > 1.0:
                    M.add('perc', timp.play(v - 10, pitch=-3), t, 0.6, 0.0)
        elif part == 'love':
            if d >= 0.9:
                hold('strings', vln, m, t, t + d, v, sb, rise=0.2, fall=0.8, gain=0.8)
            else:
                M.add('strings', vln.play(m, v, dur=d * 1.1, release=0.25), t, 0.8, sb)
            M.add('harp', harp.play(m, v - 24), t, 0.5, sb)
        elif part == 'ring':
            p = ss + (sb - ss) * min(1.0, (t - T_RING) / (T_GIVEN - T_RING))
            if d > 1.0:
                hold('winds', clar, m, t, t + d, v, p, rise=0.2, fall=0.8, gain=0.8)
            else:
                M.add('winds', clar.play(m, v, dur=d * 1.05, release=0.3), t, 0.85, p)
            M.add('winds', bsn.play(m - 12, v - 14, dur=d * 1.05, release=0.3), t, 0.5, p)
        elif part == 'given':
            M.add('perc', crash.play(118), t, 0.85, sb)
            M.add('perc', timp.play(120, pitch=-2), t, 0.9, sb)
            for i, mm in enumerate(('G5', 'C6', 'E6', 'G6')):
                M.add('harp', glock.play(note(mm), 100), t + 0.08 * i, 0.5, sb)
        elif part == 'grane':
            M.add('strings', vcs.play(m, v), t, 0.8, east * 0.5)
            if d >= 0.9:
                M.add('brass', horn.play(m, v - 10, dur=d * 1.05, release=0.25), t, 0.6, sb)
        elif part == 'gallop':
            M.add('perc', timp.play(v, pitch=-5 if note('B1') == m else -7), t, 0.85, sb)
            M.add('low', cb.play(m + 12, v - 10, dur=0.25, release=0.1), t, 0.6, sb)
        elif part == 'settle':
            hold('warm', vc if m < note('G2') else vln, m + 12 * (m < note('Eb2')), t, t + d, v, 0.0,
                 rise=2.0, fall=1.0, gain=0.45)
        elif part == 'pedal':
            hold('low', cb, m + 12, t, t + d, v, 0.0, rise=3.0, fall=2.0, gain=0.45)
