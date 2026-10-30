"""The False Gunther: dusk on Brünnhilde's rock, Waltraute gone, the Ring gold on Brünnhilde's hand. The fire round
the rock begins to stir, and on Loge's figure (Donington 20) it flares: every figure a tongue of flame leaping out
from the porch along the roofline, until the fire is roaring round the rock and over the sky. A horn sounds
through it, Siegfried's call (48), and her silver leaps for joy.

But what comes through the fire is a stranger. On the Tarnhelm (18) a grey-teal mist shimmers over the house in
waves, everything dims under it, and out of the free end of Right a figure walks in through the flames: royal
gold, Gunther's shape, with Siegfried's emerald flickering beneath it. She holds up the Ring (8) and its gold
blazes from her hand. Then the struggle: gold floods the porch from his side and silver from hers, the line
between them lurching back and forth on every blow, sparks flying from it, until he tears the Ring from her
finger: a gold flash leaps from her hand to his, and the Curse (13) slashes blood red out to both ends of the
house. She collapses, her silver sinking; fate (84) rolls indigo over the house. He lays Nothung between them, a
line of white steel on the porch, the fire sinks to a red smoulder, the night closes in, and Hagen's falling
tritone (61a) sounds far off, a black-violet pulse over everything.

compose() holds every note; stage(), heat(), fire(), scene(), strand() and figure() are shared word for word by
the Prologue's scenes (see GD01)."""
import numpy as np
from pixelhome.audio import note
from pixelhome.fx import DT, hexc, light, smoothstep, nframes, keys, Flicker, smooth_noise, colormap
from pixelhome.leitmotifs import play

CODE = 'GD14'
TITLE = 'The False Gunther'
KIND = 'show'
DESCRIPTION = ('At dusk a stranger walks through the fire: Siegfried, disguised by magic as Gunther. He wrestles '
               'the Ring from Brünnhilde, and lays his sword between them for the night.')
VOICEOVER = ('Someone is coming through the fire. It looks like a stranger, '
             'but it is Siegfried, in disguise, and he has come for the Ring.')

K = 7                                       # this scene's place on the Prologue's shared clock: T = t + 80 K
T_FLICK = 1.0                               # the fire stirs
T_LOGE = [5.0 + 1.6 * j for j in range(6)]  # Loge's figure, the fire flaring
T_HORN = 14.5                               # Siegfried's horn through the fire
T_TARN = 19.0                               # the Tarnhelm: the stranger comes through the flames
TBEAT = 0.42
T_ARRIVE = 31.0
T_RING = 32.5                               # she holds up the Ring
T_FIGHT = [40.0 + 1.45 * j for j in range(8)]   # the struggle
T_TEAR = 52.0                               # he tears the Ring from her
T_CURSE = 52.4
T_FALL = 58.5                               # she collapses
T_FATE = 59.0
T_SWORD = 65.0                              # Nothung laid between them
T_HAGEN = 74.0
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
GOLD = hexc('#ffaa00')
RINGRED = hexc('#ff1800')
GUNTHER = hexc('#ffb020')
SIEGFRIED = hexc('#00ff40')
MIST = hexc('#60c0c8')
STEEL = hexc('#e8f8ff')
BLOOD = hexc('#c00010')
FATE = hexc('#2a1a8a')
HAGEN = hexc('#7a00ff')

START = dict(night=0.15, stars=0.0, rock=0.35, fire=0.35, east=0.0, dawn=0.5, hue=0.22, day=0.15, rope=0.0)
END = dict(night=0.55, stars=0.2, rock=0.25, fire=0.3, east=0.0, dawn=0.0, hue=0.2, day=0.0, rope=0.0)
BRUNNHILDE_START = ('Porch Front', 0.6, 0.85)   # (segment, u, level); the Ring's glint on her hand at 0.7 x level
BRUNNHILDE_END = ('Porch Front', 0.3, 0.3)
GUNTHER_END = ('Porch Front', 0.55, 0.5)        # gold, Siegfried's emerald flickering at 0.4 x level beneath
SWORD_END = ('Porch Front', 0.36, 0.49, 0.75)   # Nothung: from u, to u, level


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

    for t, m, v, d in play('loge_flicker', T_FLICK, 0.25, 0, 70):
        add(t, d, m, v, 'flicker')
    for j, t0 in enumerate(T_LOGE):
        for t, m, v, d in play('loge', t0, 0.2, (0, 3, 7, 12, 7, 3)[j], 84 + 4 * j):
            add(t, d, m, v, 'loge', j)
    add(T_LOGE[0], T_TARN - T_LOGE[0], 'E2', 66, 'firebed')
    for t, m, v, d in play('siegfried_horn', T_HORN, 0.32, 5, 100):
        add(t, d, m, v, 'horn')
    for t, m, v, d in play('tarnhelm', T_TARN, TBEAT, 0, 86):
        add(t, d, m, v, 'tarn')
    for t, m, v, d in play('ring', T_RING, 0.55, -5, 110):
        add(t, d, m, v, 'ring')
    for j, t0 in enumerate(T_FIGHT):
        add(t0, 0.3, ('Gb2', 'C3', 'Gb2', 'Db3', 'G2', 'Db3', 'Ab2', 'D3')[j], 104 + 2 * j, 'fight', j)
    add(T_TEAR, 0.1, 'C1', 126, 'tear')
    for t, m, v, d in play('curse', T_CURSE, 0.42, 0, 112):
        add(t, d, m, v, 'curse')
    for t, m, v, d in play('fate', T_FATE, 0.75, 0, 92):
        add(t, d, m, v, 'fate')
    for t, m, v, d in play('nothung', T_SWORD, 0.42, -12, 84):
        add(t, d, m, v, 'sword')
    for t, m, v, d in play('hagen', T_HAGEN, 0.9, -12, 112):
        add(t, d, m, v, 'hagen')
    for m in ('Gb1', 'C2'):
        add(T_FALL, D - T_FALL, m, 58, 'dark')
    return sorted(N, key=lambda e: e[0])


def places(G, t):
    """Per time: (Brünnhilde's position, her level, the stranger's position or None, the boundary between them)."""
    u_b = keys(t, [(0, 0.6), (T_FIGHT[0], 0.6), (T_FIGHT[3], 0.5), (T_TEAR, 0.42), (T_FALL + 2, 0.3)])
    jolt = 0.0
    for j, t0 in enumerate(T_FIGHT):
        a = t - t0
        if 0 <= a < 2.0:
            jolt += (0.06 if j % 2 else -0.05) * np.exp(-a / 0.5) * min(1.0, a / 0.08)
    p_b = at(G, 'Porch Front', float(np.clip(u_b + jolt, 0.05, 0.95)))
    lvl_b = keys(t, [(0, 0.85), (T_HORN, 0.85), (T_HORN + 0.5, 1.0), (T_TARN + 3, 0.85), (T_RING, 1.0),
                     (T_TEAR, 1.0), (T_FALL, 0.8), (T_FALL + 3, 0.3)])
    p_g = None
    if t >= T_TARN + 1.0:
        L = G.pd.max()
        if t < T_ARRIVE:
            p_g = L + 30 + (at(G, 'Porch Front', 0.9) - L - 30) * smoothstep(T_TARN + 1.0, T_ARRIVE, t)
        else:
            u_g = keys(t, [(T_ARRIVE, 0.9), (T_FIGHT[0], 0.85), (T_TEAR, 0.6), (T_SWORD, 0.55)])
            p_g = at(G, 'Porch Front', float(np.clip(u_g - 0.8 * jolt, 0.05, 0.98)))
    bound = None if p_g is None else 0.5 * (p_b + p_g) + 9000 * jolt
    return p_b, lvl_b, p_g, bound


def render(G, seed=14):
    F = nframes(D)
    out = np.zeros((F, G.N, 3))
    S = stage(G)
    d, L = S['d'], S['L']
    N = compose()
    rng = np.random.default_rng(seed)
    loges = [(t0, rng.uniform(at(G, 'Porch Left', 0.2), at(G, 'Porch Right', 0.8)), rng.choice([-1, 1]))
             for t0 in T_LOGE]
    tarn = sorted({e[0] for e in N if e[4] == 'tarn'})
    ring = sorted({e[0] for e in N if e[4] == 'ring'})
    curse = [e for e in N if e[4] == 'curse']
    fate = sorted({e[0] for e in N if e[4] == 'fate'})
    horn = sorted({e[0] for e in N if e[4] == 'horn'})
    shim = Flicker(np.random.default_rng(1418), G.N, 0.6, 2.2)
    flick = Flicker(np.random.default_rng(1419), G.N, 5.0, 12.0)
    pf0, pf1 = at(G, 'Porch Front', 0.0), at(G, 'Porch Front', 1.0)

    for f in range(F):
        t = f * DT
        T = t + 80 * K
        lv = {k: keys(t, [(0, START[k]), (T_FALL, START[k] + 0.4 * (END[k] - START[k])), (D - 3, END[k])])
              for k in START}
        blaze = smoothstep(T_LOGE[0], T_LOGE[-1], t) * (1 - smoothstep(T_ARRIVE, T_FIGHT[0] + 4, t))
        lv['fire'] = lv['fire'] + 0.55 * blaze + 0.15 * smoothstep(T_FIGHT[0], T_FIGHT[2], t) * (1 - smoothstep(T_FALL, T_FALL + 6, t))
        mist = smoothstep(T_TARN, T_TARN + 2, t) * (1 - smoothstep(T_ARRIVE, T_ARRIVE + 3, t))
        lv['dawn'] *= 1 - 0.6 * blaze
        fr = scene(S, T, lv)
        fr += fire(S, T, 0.0, 0.6 * blaze, boost=0.3 * blaze)

        # Loge's figure: a tongue of flame leaping out from the porch along the roofline
        for t0, p0, s in loges:
            a = t - t0
            if 0 <= a < 1.6:
                head = p0 + s * 1300 * (1 - np.exp(-a / 0.5))
                lo, hi = min(p0, head), max(p0, head)
                q = np.clip(heat(d, T) + 0.3, 0, 1)
                tongue = smoothstep(lo - 40, lo + 40, d) * smoothstep(hi + 40, hi - 40, d)
                fr += light(FIRE(q), 1.0 * np.exp(-a / 0.8) * tongue)
                fr += light(AMBER, 1.0 * np.exp(-a / 0.6) * np.exp(-((d - head) / 60) ** 2))
                fr += light(HOT, 0.8 * np.exp(-a / 0.4) * np.exp(-((d - head) / 15) ** 2))

        p_b, lvl_b, p_g, bound = places(G, t)

        # Siegfried's horn through the flames: emerald streaks in from the east, and her joy
        for t0 in horn:
            a = t - t0
            if 0 <= a < 1.0:
                head = L - 1500 * a
                fr += light(SIEGFRIED, 0.8 * np.exp(-a / 0.5) * np.exp(-((d - head) / 60) ** 2))
        if T_HORN + 0.4 <= t < T_HORN + 2.4:
            a = t - T_HORN - 0.4
            fr += light(SILVER, 0.9 * np.exp(-a / 0.6) * np.exp(-((np.abs(d - p_b) - 1300 * a) / 120) ** 2))

        # the Tarnhelm: a grey-teal mist shimmering over the house in waves, everything dims under it
        if mist > 0:
            fr = fr * (1 - 0.45 * mist)
            for t0 in tarn:
                a = t - t0
                if 0 <= a < 3.0:
                    r = 1500 * (1 - np.exp(-a / 1.0))
                    c = p_g if p_g is not None else L
                    fr += light(MIST, 1.0 * mist * np.exp(-a / 1.3) * np.exp(-((np.abs(d - c) - r) / 260) ** 2))
            fr += light(MIST, 0.4 * mist * np.clip(shim(T), 0, None))

        # the Ring held up: gold blazing from her hand in waves
        for t0 in ring:
            a = t - t0
            if 0 <= a < 1.6:
                r = 1200 * (1 - np.exp(-a / 0.55))
                fr += light(GOLD, 1.0 * np.exp(-a / 0.8) * np.exp(-((np.abs(d - p_b) - r) / 170) ** 2))
                fr += light(RINGRED, 0.6 * np.exp(-a / 0.3) * np.exp(-((d - p_b) / 30) ** 2))

        # the struggle: gold floods the porch from his side, silver from hers; the line between lurches
        if bound is not None and T_FIGHT[0] - 1 <= t < T_FALL + 1:
            g = smoothstep(T_FIGHT[0] - 1, T_FIGHT[0], t) * (1 - smoothstep(T_TEAR + 1, T_FALL + 1, t))
            side_g = smoothstep(bound - 20, bound + 20, d) if p_g > p_b else smoothstep(bound + 20, bound - 20, d)
            near = 0.55 + 0.45 * np.exp(-((d - bound) / 500) ** 2)
            fr = fr * (1 - 0.6 * g)
            fr += light(GUNTHER, 0.9 * g * near * side_g)
            fr += light(SILVER, 0.9 * g * near * (1 - side_g))
            fr += light(WHITE, 0.6 * g * np.exp(-((d - bound) / 10) ** 2))
        for j, t0 in enumerate(T_FIGHT):
            a = t - t0
            if 0 <= a < 1.0 and bound is not None:
                fr += light(WHITE, 0.9 * np.exp(-a / 0.12) * np.exp(-((d - bound) / 30) ** 2))
                col = GUNTHER if j % 2 == 0 else SILVER
                fr += light(col, 0.85 * np.exp(-a / 0.4) * np.exp(-((np.abs(d - bound) - 1400 * a) / 90) ** 2))
                sp = np.random.default_rng(140 + j).uniform(-1, 1, 12)
                for v in sp:
                    ps = bound + v * 900 * (1 - np.exp(-a / 0.4))
                    fr += light(AMBER, 0.8 * np.exp(-a / 0.45) * np.exp(-((d - ps) / 7) ** 2))

        # he tears the Ring from her: a gold flash leaps from her hand to his, and the Curse slashes out
        if T_TEAR <= t < T_TEAR + 1.2 and p_g is not None:
            a = t - T_TEAR
            head = p_b + (p_g - p_b) * min(1.0, a / 0.35)
            fr += light(GOLD, 1.0 * np.exp(-a / 0.5) * np.exp(-((d - head) / 40) ** 2))
            fr += light(GOLD, 0.6 * np.exp(-a / 0.15))
        for t0, dur, m, v, part, k in curse:
            a = t - t0
            if 0 <= a < 2.5 and dur >= 1.0:
                c = p_g if p_g is not None else S['summit']
                front = min(1.0, a / 1.0) * L
                fr += light(BLOOD, 0.95 * np.exp(-max(a - 0.8, 0) / 1.0) * smoothstep(front + 60, front - 60, np.abs(d - c)))
            elif 0 <= a < 0.6 and m < note('C3'):
                fr += light(BLOOD, 0.6 * np.exp(-a / 0.2))

        # fate rolling indigo over the house as she falls
        for t0 in fate:
            a = t - t0
            if 0 <= a < 3.0:
                r = 1500 * (1 - np.exp(-a / 1.0))
                fr += light(FATE, 0.9 * np.exp(-a / 1.5) * np.exp(-((np.abs(d - p_b) - r) / 200) ** 2))

        # Hagen's tritone far off: a black-violet pulse over everything
        if t >= T_HAGEN:
            a = t - T_HAGEN
            for t0 in (T_HAGEN, T_HAGEN + 0.9):
                aa = t - t0
                if 0 <= aa < 3.0:
                    fr = fr * (1 - 0.5 * np.exp(-aa / 0.6))
                    fr += light(HAGEN, 0.75 * np.exp(-aa / 0.9) * np.exp(-((np.abs(d - S['summit']) - 1500 * (1 - np.exp(-aa / 0.6))) / 220) ** 2))

        # Nothung laid between them: a line of white steel, glinting
        if t >= T_SWORD:
            g = smoothstep(T_SWORD, T_SWORD + 2.5, t)
            a0, a1 = at(G, 'Porch Front', SWORD_END[1]), at(G, 'Porch Front', SWORD_END[2])
            line = smoothstep(a0 - 6, a0 + 6, d) * smoothstep(a1 + 6, a1 - 6, d)
            glint = np.exp(-((d - (a0 + (a1 - a0) * ((t - T_SWORD) / 3.0 % 1))) / 8) ** 2)
            fr += light(STEEL, SWORD_END[3] * g * line * (0.8 + 0.2 * np.sin(2 * np.pi * t / 2.3)) + 0.6 * g * glint)
            if t < T_SWORD + 1.0:
                a = t - T_SWORD
                fr += light(STEEL, 0.8 * np.exp(-a / 0.4) * np.exp(-((np.abs(d - 0.5 * (a0 + a1)) - 900 * a) / 80) ** 2))

        # the stranger: Gunther's gold with Siegfried's emerald flickering beneath
        if p_g is not None:
            lvl_g = keys(t, [(T_TARN + 1, 0.0), (T_TARN + 2.5, 0.9), (T_TEAR, 1.0), (T_FALL + 3, 0.7), (D - 3, GUNTHER_END[2])])
            fr = figure(fr, S, p_g, GUNTHER, lvl_g, w=20)
            fr += light(SIEGFRIED, 0.45 * lvl_g * np.clip(flick(T), 0, None) * np.exp(-((d - p_g) / 10) ** 2))
            if t >= T_TEAR:
                fr += light(GOLD, 0.7 * lvl_g * np.exp(-((d - p_g + 9) / 5) ** 2))
        # Brünnhilde, the Ring on her hand until it is torn away
        w_b = keys(t, [(T_FALL, 16.0), (T_FALL + 3, 24.0)])
        fr = figure(fr, S, p_b, SILVER, lvl_b, w=w_b)
        if t < T_TEAR:
            fr += light(GOLD, 0.7 * lvl_b * np.exp(-((d - p_b - 9) / 5) ** 2))
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

    for name, gain, rev in (('low', 0.34, 0.25), ('strings', 0.3, 0.32), ('brass', 0.32, 0.3), ('perc', 0.31, 0.3),
                            ('winds', 0.25, 0.35), ('harp', 0.22, 0.4), ('fx', 0.09, 0.3)):
        M.bus(name, gain=gain, reverb=rev)
    vln = M.sampler('Strings/Violin Section/susVib/*.wav', tune=-12)
    vc = M.sampler('Strings/Cello Section/susvib/*.wav', tune=-12)
    cb = M.sampler('Strings/Solo Contrabass/SusNV/*.wav', tune=-12)
    pic = M.sampler('Woodwinds/Piccolo/Sus/*.wav', tune=-12)
    clar = M.sampler('Woodwinds/Clarinet/susLong/*.wav', tune=-12)
    fl = M.sampler('Woodwinds/Flute/susNV/*.wav', tune=-12)
    harp = M.sampler('Strings/Harp/*.wav')
    glock = M.sampler('Percussion/Glock/*.wav')
    horn = M.sampler('Brass/F Horn/sus/*.wav', tune=-12)
    tpt = M.sampler('Brass/Trumpet/sus/*.wav', tune=-12)
    tbn = M.sampler('Brass/Tenor Trombone/sus/*.wav', tune=-12)
    tuba = M.sampler('Brass/Tuba/sus/*.wav', tune=-12)
    timp = M.hits('Percussion/Timpani/Timpani1_Hit*.wav')
    crash = M.hits('Percussion/cymbal-crash1_f*.wav')
    gong = M.hits('Percussion/gongHit_f*.wav')

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
    east = pan_at(S['L'] - 60)
    summit = pan_at(S['summit'])

    def pan_b(t):
        return pan_at(places(G, t)[0])

    def pan_g(t):
        p = places(G, t)[2]
        return pan_at(p) if p is not None else east

    for t, d, m, v, part, k in compose():
        if part == 'flicker':
            M.add('winds', pic.play(m, v, dur=d * 1.05, release=0.15), t, 0.5, summit)
        elif part == 'loge':
            M.add('strings', vln.play(m + 12, v, dur=d * 1.1, release=0.15), t, 0.6, summit)
            M.add('harp', harp.play(m + 12, v - 10), t, 0.6, summit)
            if d <= 0.1:
                M.add('harp', glock.play(m + 24, v - 30), t, 0.3, summit)
        elif part == 'firebed':
            hold('strings', vc, m + 12, t, t + d, v, summit, rise=3.0, fall=2.0, gain=0.5)
        elif part == 'horn':
            M.add('brass', horn.play(m, v, dur=d * 1.1, release=0.25), t, 0.75, east)
        elif part == 'tarn':
            hold('winds', clar, m, t, t + d, v, pan_g(t), rise=0.8, fall=1.5, gain=0.7)
            hold('low', vc, m - 12, t, t + d, v - 20, pan_g(t), rise=1.0, fall=1.5, gain=0.4)
        elif part == 'ring':
            if d > 1.0:
                hold('winds', fl, m, t, t + d, v, pan_b(t), rise=0.15, fall=0.8, gain=0.75)
            else:
                M.add('winds', fl.play(m, v, dur=d * 1.05, release=0.25), t, 0.8, pan_b(t))
            M.add('brass', horn.play(m - 12, v - 14, dur=d * 1.05, release=0.25), t, 0.6, pan_b(t))
        elif part == 'fight':
            p = pan_at(0.5 * (places(G, t)[0] + (places(G, t)[2] or S['summit'])))
            M.add('perc', timp.play(v, pitch=-4 - (k % 3)), t, 0.95, p)
            M.add('brass', tbn.play(m, v, dur=0.35, release=0.1), t, 0.85, p)
            M.add('low', tuba.play(m - 12, v - 10, dur=0.35, release=0.1), t, 0.7, p)
            M.add('fx', whoosh(0.35, 3000, 500, 0.6, seed=140 + k), t - 0.15, 0.8, p)
            if k % 2:
                M.add('perc', crash.play(90), t, 0.4, p)
        elif part == 'tear':
            M.add('perc', crash.play(v), t, 0.9, pan_b(t))
            M.add('perc', gong.play(115), t, 0.8, pan_b(t))
            M.add('perc', timp.play(v, pitch=-7), t, 0.9, pan_b(t))
        elif part == 'curse':
            if d > 1.0:
                hold('brass', tbn, m, t, t + d, v, pan_g(t), rise=0.15, fall=1.0, gain=0.85)
            else:
                M.add('brass', tbn.play(m, v, dur=d * 1.05, release=0.3), t, 0.9, pan_g(t))
            M.add('low', cb.play(m - 12, v - 10, dur=d * 1.05, release=0.3), t, 0.7, 0.0)
        elif part == 'fate':
            if d > 1.0:
                hold('brass', horn, m, t, t + d, v, pan_b(t), rise=0.4, fall=1.2, gain=0.7)
            else:
                M.add('brass', horn.play(m, v, dur=d * 1.05, release=0.3), t, 0.7, pan_b(t))
            if m < note('Db3'):
                hold('low', tuba, m, t, t + d, v - 6, 0.0, rise=0.4, fall=1.2, gain=0.7)
        elif part == 'sword':
            M.add('brass', tpt.play(m, v, dur=d * 1.05, release=0.3), t, 0.65, summit)
        elif part == 'hagen':
            hold('low', tuba, m, t, t + d, v, summit, rise=0.1, fall=1.5, gain=0.9)
            M.add('perc', timp.play(v, pitch=-8), t, 0.8, summit)
        elif part == 'dark':
            hold('low', cb, m + 12, t, t + d, v, 0.0, rise=3.0, fall=2.0, gain=0.55)
