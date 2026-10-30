"""The False Gunther: dusk on Brünnhilde's rock, Waltraute gone, the Ring gold on Brünnhilde's hand. "Was leckt
so wütend die lodernde Welle zum Wall?": the fire round the rock flares, tongue after tongue leaping out from the
porch along the roofline, until it is roaring round the rock and over the sky. "Siegfried!": his horn sounds
through it, emerald streaks racing in from the east, and her silver leaps for joy.

The music is Wagner's own, the end of Act I as Solti's 1958 Vienna Philharmonic recording takes it: the fire
(bars 1572-1575), Siegfried's horn call (1585-1590), "Verrat!" (1605-1609), the struggle and the Ring torn away
(1744-1765), "Nun, Nothung, zeuge du" (1808-1810) and the act's last bars (1840-1844), its final chord held. The
notes come from the Wagner Ring Dataset's piano reduction (pixelhome/ring.py): the fire on violins, piccolo,
flutes and harp, his horn call on horns, the struggle on the full orchestra with timpani on each blow, the Curse
on trombones and tuba. The stage adds the fire's roar and a rush for each leaping tongue, a stamp and a scuffle on
every blow, a whoosh and a blow as the Ring is wrenched away, and the sword ringing as it is laid on the stone.

"Verrat!": what comes through the fire is a stranger. A grey-teal mist shimmers over the house in waves on the
Tarnhelm's chords, and out of the free end of Right a figure walks in through the flames: royal gold, Gunther's
shape, with Siegfried's emerald flickering beneath it. She holds up the Ring and its gold blazes from her hand.
Then the struggle: gold floods the porch from his side and silver from hers, the line between them lurching on
every blow, sparks flying from it, until he tears the Ring from her finger: a gold flash leaps from her hand to
his, and the Curse slashes blood red out to both ends of the house. She collapses, her silver sinking; fate rolls
indigo over the house. He lays Nothung between them, a line of white steel on the porch, the fire sinks to a red
smoulder, and on the act's last chords a black-violet pulse goes out over everything.

compose() tags every note; stage(), heat(), fire(), scene(), strand() and figure() are shared word for word by
the Prologue's scenes (see GD01)."""
import numpy as np
from pixelhome.audio import note
from pixelhome.fx import DT, hexc, light, smoothstep, nframes, keys, Flicker, smooth_noise, colormap
from pixelhome.ring import Orchestra, accents, excerpt, tidy

CODE = 'GD14'
TITLE = 'The False Gunther'
KIND = 'show'
DESCRIPTION = ('At dusk a stranger walks through the fire: Siegfried, disguised by magic as Gunther. He wrestles '
               'the Ring from Brünnhilde, and lays his sword between them for the night.')
VOICEOVER = ('Someone is coming through the fire. It looks like a stranger, '
             'but it is Siegfried, in disguise, and he has come for the Ring.')

K = 7                                       # this scene's place on the Prologue's shared clock: T = t + 80 K
EX = excerpt(__file__)                      # Act I, bars 1572-75, 1585-90, 1605-09, 1744-65, 1808-10, 1840-44, Solti 1958
BAR = {int(m): t for m, t in EX['bars']}
SEG = [s['start'] for s in EX['segments']] + [EX['seconds']]
HOLD = 3.4                                  # the act's last chord, held
D = EX['seconds'] + HOLD - 0.4
T_FLICK = 0.0                               # "Was leckt so wütend die lodernde Welle zum Wall?"
T_LOGE = accents(EX['notes'], 0.0, SEG[1], 85, 2, 0.9)  # the fire flaring
T_HORN = BAR[1585]                          # "Siegfried!": his horn through the fire
T_TARN = BAR[1605]                          # "Verrat!": a stranger comes through the flames
T_ARRIVE = SEG[3]
T_RING = SEG[3] + 0.2                       # she holds up the Ring
T_FIGHT = accents(EX['notes'], BAR[1745], BAR[1754] - 0.2, 95, 2, 1.1)    # the struggle
T_TEAR = BAR[1754]                          # he tears the Ring from her
T_CURSE = BAR[1757]
T_FALL = BAR[1765]                          # she collapses
T_SWORD = SEG[4]                            # "Nun, Nothung, zeuge du": the sword laid between them
T_HAGEN = BAR[1841]                         # the end of the act: a black-violet pulse over everything

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


def part_of(t, d, m, v, h):
    """What a note of the excerpt is: its part, see compose()."""
    if T_HORN <= t < T_TARN and h == 0 and v >= 100 and d >= 0.2:
        return 'horn'
    if T_TARN <= t < T_ARRIVE and d >= 0.3:
        return 'tarn'
    if T_ARRIVE <= t < BAR[1745] and h == 0 and v >= 90:
        return 'ring'
    if T_CURSE <= t < T_FALL and h == 1 and m < note('C3'):
        return 'curse'
    if T_FALL <= t < T_SWORD and d >= 0.5:
        return 'fate'
    return 'music'


def compose():
    """Every note of the excerpt, tagged: (time, seconds, midi, velocity, part, k). The right hand's loud notes of
    "Siegfried! Seinen Ruf sendet er her!" are his horn through the fire ('horn'); the chords of "Verrat!" bring
    the Tarnhelm's mist ('tarn'); the first bar of the struggle is the Ring held up ('ring'); the bass after he
    tears it away is the Curse ('curse'); the long notes as she falls are fate ('fate'). The act's last chord is
    held. Everything else is 'music'."""
    N = []
    for t, d, m, v, h, _ in tidy(EX['notes']):
        if t >= BAR[1844] - 0.01:
            d = HOLD
        N.append((float(t), float(d), int(m), int(v), part_of(t, d, m, v, h), h))
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
    """Wagner's notes, orchestrated from the piano reduction, with the fire roaring round the rock, the struggle,
    and the sword laid down."""
    from pixelhome.audio import whoosh
    order = np.argsort(G.pd)
    xs, ds = G.pos[order, 0], G.pd[order]
    x0, x1 = xs.min(), xs.max()

    def pan_at(dd):                         # path distance -> left/right across the facade, from the street
        x = np.interp(dd, ds, xs)
        return float(0.85 * (2 * (x - x0) / (x1 - x0) - 1))

    o = Orchestra(M, level=1.7)
    N = compose()
    held = {(round(e[0], 4), e[2]) for e in N if e[1] == HOLD}

    def role(t, d, m, v, h):
        part = part_of(t, d, m, v, h)
        if t < T_HORN and h == 0:                           # the fire: violins, piccolo and flutes, harp
            return [('violins', 0, 0, 0.55), ('piccolo' if m >= 79 else 'flutes', 0, -10, 0.4), ('harp', 0, -16, 0.3)]
        if part == 'horn':                                  # his horn call, through the flames
            return [('horns', -12 if m >= 77 else 0, 0, 0.8), ('violins', 0, -8, 0.45)]
        if part == 'curse':                                 # the Curse in the bass: trombones and tuba
            return [('trombones', 12, 0, 0.8), ('tuba', 0, -4, 0.7), ('basses', 0, -4, 0.5)]
        if (round(t, 4), m) in held:                        # the last chord, held by everyone
            return [('horns' if h else 'violins', 0, 0, 0.7), ('trombones' if h else 'trumpets', 0, -6, 0.5)]
        return None

    def pan(t, m):
        p_b, lvl_b, p_g, bound = places(G, t)
        return pan_at(bound if bound is not None else p_b) * 0.6

    notes = [list(e[:4]) + [e[5]] for e in N]
    o.tutti(tidy(notes), size=lambda t: 1.0, role=role, pan=pan)
    for t0 in T_FIGHT:                                      # each blow of the struggle
        p = pan(t0, 60)
        o.hit('timpani', t0, 112, pitch=-3, gain=0.6, pan=p)
    o.hit('crash', T_TARN, 120, gain=0.7)
    o.hit('crash', T_TEAR, 124, gain=0.85)
    o.hit('gong', T_CURSE, 116, gain=0.6)
    o.hit('timpani roll', T_FALL - 1.0, 100, pitch=-6, gain=0.5)
    o.hit('crash', BAR[1844], 124, gain=0.8)
    o.hit('timpani', BAR[1844], 124, pitch=-5, gain=0.9)

    # the stage: the fire roaring round the rock; scuffles of the struggle; the Ring wrenched away; steel on stone
    S = stage(G)
    sb = pan_at(places(G, T_TEAR)[0])
    o.fire(0.0, T_ARRIVE + 1.0, level=lambda tt: 0.45 + 0.45 * smoothstep(0.5, 3.0, tt) - 0.3 * smoothstep(T_HORN,
           T_HORN + 1, tt) + 0.3 * smoothstep(T_TARN, T_TARN + 1.5, tt), pan=lambda t: -0.5 + 1.0 * ((t / 9) % 1))
    for t0 in T_LOGE:                                       # each tongue of flame leaping out
        M.add('fx', whoosh(0.7, 300, 2500, 0.7, seed=int(t0 * 100)), t0 - 0.1, 0.8, sb)
    for j, t0 in enumerate(T_FIGHT):
        o.hoof(t0 + 0.05, pan(t0, 60), 96 + 3 * j, 0.8)     # a stamp, a shove
        o.hit('scrape', t0 + 0.1, 80, gain=0.25, pan=pan(t0, 60))
    M.add('fx', whoosh(0.4, 1800, 6000, 0.8, seed=14), T_TEAR - 0.15, 1.0, sb)
    o.boom(T_TEAR + 0.02, sb, 0.7)
    o.clash(T_SWORD + 1.2, pan_at(S['summit']), 90, 0.6)    # Nothung laid on the stone
    o.effects([(0, 0), (T_HORN - 0.3, 0), (T_HORN + 0.3, -12), (T_TARN - 0.5, -12), (T_TARN, -2), (T_TEAR + 2, -2),
               (T_TEAR + 4, -14), (T_SWORD + 0.8, -14), (T_SWORD + 1.1, -4), (T_SWORD + 3, -14), (D, -14)])
