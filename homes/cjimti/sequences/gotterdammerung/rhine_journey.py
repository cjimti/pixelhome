"""Siegfried's Rhine Journey: the interlude between the Prologue and the first act. Siegfried's horn call (Donington
48) rings out twice and carries him down off the rock: from the head of Porch Right he runs out along Right to the
free end in an emerald streak, while Brünnhilde waves a last silver pulse on the summit and fades with the morning.

Then the river takes the house. Water floods in from the free end of Right and races back the whole length of the
roofline to the end of the Side, and from then on every run is the Rhine: indigo, teal and green currents rushing
downstream end to end, white crests riding them. The Rhine's flowing figure (2) surges the currents brighter at
every statement; the horn call keeps coming back as an emerald streak racing down the water with a white wake,
Siegfried on his journey; the Rhinemaidens' Rhinegold (31) scatters gold glints over the water, note by note.

Then the dark turn: the Renunciation of Love (76) on the brass, the water darkens to violet-indigo with a red
flash through it, and the Ring (8) sounds twice, heavy, gold and red rings pulsing out over the river as the
light goes, toward the hall of the Gibichungs. It ends on the Rhine at dusk, dark and still flowing.

compose() holds every note; stage(), heat(), fire(), scene(), strand() and figure() are shared word for word by
the Prologue's scenes (see GD01); river() is this scene's own."""
import numpy as np
from pixelhome.audio import note
from pixelhome.fx import DT, hexc, light, smoothstep, nframes, keys, Flicker, smooth_noise, colormap
from pixelhome.leitmotifs import play

CODE = 'GD06'
TITLE = "Siegfried's Rhine Journey"
KIND = 'show'
DESCRIPTION = ("Siegfried's horn carries him down the mountain to the Rhine, and the whole house becomes the river, "
               'rushing end to end with his emerald boat racing along it, until the water darkens toward an '
               'unfriendly hall.')
VOICEOVER = ('Down the mountain and along the river Rhine, Siegfried sets off in search of adventure.')

K = 5                                       # this scene's place on the Prologue's shared clock: T = t + 80 K
T_HORN = [0.5, 4.5]                         # the horn calls that carry him off the rock
HORNBEAT = 0.42
T_EXIT = 10.0                               # he is out at the free end of Right
T_FLOOD = 9.0                               # the water floods in
FLOOD_SPEED = 420.0
T_RHINE = [16.5, 20.0, 23.5, 27.0, 30.5, 34.0]      # the Rhine's flowing figure
RHBEAT = 0.3
T_BOAT = [19.0, 28.0, 37.0, 44.0]           # the horn call again: his boat on the river
T_GOLD = 38.0                               # the Rhinegold
T_RENOUNCE = 47.0                           # the dark turn
T_RING = [55.0, 62.0]
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
DEEP = hexc('#0c1c8c')
TEAL = hexc('#0a7c8a')
GREEN = hexc('#14c080')
FOAM = hexc('#c8f4ff')
MURK = hexc('#3a1a8a')
BLOOD = hexc('#ff1800')

START = dict(night=0.0, stars=0.0, rock=0.35, fire=0.15, east=0.0, dawn=0.75, hue=0.62, day=0.3, rope=0.0)
SIEGFRIED_START = ('Porch Right', 0.8, 0.85)    # (segment, u, level)
BRUNNHILDE_START = ('Porch Front', 0.6, 0.9)
RING_ON_HER = 0.55
RIVER_END = dict(level=0.7, dark=0.6, speed=0.6)   # the Rhine at dusk: river() levels at the last frame
END = dict(night=0.0, stars=0.0, rock=0.0, fire=0.0, east=0.0, dawn=0.0, hue=0.62, day=0.0, rope=0.0)


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


def river(S, T, level, dark, speed, surge=0.0):
    """The Rhine over the whole house, flowing downstream (from the free end of Right toward the end of the Side):
    `level` its brightness, `dark` (0..1) how far toward dusk violet, `speed` how fast, `surge` a brightening."""
    d = S['d']
    ph = T * speed
    c1 = np.sin(2 * np.pi * (d / 420 + 0.9 * ph))
    c2 = np.sin(2 * np.pi * (d / 170 + 1.7 * ph) + 1.3)
    c3 = np.sin(2 * np.pi * (d / 75 + 2.9 * ph) + 0.4)
    u = np.clip(0.5 + 0.28 * c1 + 0.17 * c2 + 0.08 * c3, 0, 1)
    col = DEEP + (TEAL - DEEP) * u[:, None]
    col = col + (GREEN - col) * np.clip(2 * u - 1.2, 0, 1)[:, None]
    col = col + (MURK - col) * dark
    fr = light(col, level * (0.55 + 0.45 * u) * (1 + 0.35 * surge) * (1 - 0.35 * dark))
    crest = np.clip(c1 * 0.6 + c2 * 0.4 - 0.55, 0, None) * 2.2
    fr += light(FOAM, level * (1 - 0.8 * dark) * (0.35 + 0.5 * surge) * crest)
    return fr


def compose():
    """Every note: (time, seconds, midi, velocity, part, k)."""
    N = []

    def add(t, d, m, v, part, k=None):
        N.append((float(t), float(d), note(m) if isinstance(m, str) else int(m), int(v), part, k))

    for k, t0 in enumerate(T_HORN):
        for t, m, v, d in play('siegfried_horn', t0, HORNBEAT, 5, 112 - 6 * k):
            add(t, d, m, v, 'horn', k)
    add(T_FLOOD, 2.0, 'Eb1', 110, 'flood')
    for k, t0 in enumerate(T_RHINE):
        for t, m, v, d in play('rhine', t0, RHBEAT, 0, 86 + 3 * k):
            add(t, d, m, v, 'rhine', k)
    for k, t0 in enumerate(T_BOAT):
        for t, m, v, d in play('siegfried_horn', t0, 0.36, 5 + 2 * (k % 2), 104 + 4 * k):
            add(t, d, m, v, 'boat', k)
    for t, m, v, d in play('rheingold', T_GOLD, 0.32, 0, 92):
        add(t, d, m, v, 'gold')
    for t, m, v, d in play('renunciation_broad', T_RENOUNCE, 0.5, -12, 112):
        add(t, d, m, v, 'renounce')
    for k, t0 in enumerate(T_RING):
        for t, m, v, d in play('ring', t0, 0.55, -12 + 0 * k, 104 - 10 * k):
            add(t, d, m, v, 'ring', k)
    for m in ('Eb1', 'Eb2'):
        add(T_FLOOD + 2, T_RENOUNCE - T_FLOOD - 2, m, 70, 'pedal')
    for m in ('C2', 'G2', 'Eb3'):
        add(T_RING[1] + 6, D - T_RING[1] - 6, m, 58, 'dusk')
    return sorted(N, key=lambda e: e[0])


def run_off(G, t):
    """Where Siegfried is while he runs off the rock: from the head of Porch Right out along Right."""
    a = at(G, *SIEGFRIED_START[:2])
    b = G.pd.max() + 40
    return a + (b - a) * smoothstep(T_HORN[0] + 0.5, T_EXIT, t)


def render(G, seed=6):
    F = nframes(D)
    out = np.zeros((F, G.N, 3))
    S = stage(G)
    d, L = S['d'], S['L']
    N = compose()
    p_b = at(G, *BRUNNHILDE_START[:2])
    horn = sorted({e[0] for e in N if e[4] == 'horn'})
    rhine = [sorted({e[0] for e in N if e[4] == 'rhine' and e[5] == k}) for k in range(len(T_RHINE))]
    boat_t = T_BOAT
    gold = [e for e in N if e[4] == 'gold']
    glint_at = np.random.default_rng(seed).uniform(0, L, len(gold))
    renounce = sorted({e[0] for e in N if e[4] == 'renounce'})
    ring = [sorted({e[0] for e in N if e[4] == 'ring' and e[5] == k}) for k in range(2)]

    for f in range(F):
        t = f * DT
        T = t + 80 * K
        # the morning on the rock fades as the river takes the house
        morning = 1 - smoothstep(T_FLOOD, T_FLOOD + L / FLOOD_SPEED + 1, t)
        lv = {k: START[k] * morning for k in START}
        fr = scene(S, T, lv) if morning > 0 else np.zeros((G.N, 3))

        # the river: flooding in from the free end of Right, then the whole house
        front = L - FLOOD_SPEED * max(t - T_FLOOD, 0)
        wet = smoothstep(front - 60, front + 60, d) * (t >= T_FLOOD)
        dark = keys(t, [(0, 0.0), (T_RENOUNCE, 0.0), (T_RENOUNCE + 3, 0.6), (T_RING[0], 0.5), (D - 6, RIVER_END['dark'])])
        level = keys(t, [(T_FLOOD, 0.85), (T_RENOUNCE, 0.85), (T_RING[1], 0.7), (D - 6, RIVER_END['level'])])
        speed = keys(t, [(T_FLOOD, 1.0), (T_RENOUNCE, 1.0), (D - 6, RIVER_END['speed'])])
        surge = 0.0
        for k, ons in enumerate(rhine):
            if ons and ons[0] <= t < ons[-1] + 1.5:
                surge = max(surge, smoothstep(ons[0], ons[0] + 0.3, t) * np.exp(-max(t - ons[-1], 0) / 0.6))
        if t >= T_FLOOD:
            riv = river(S, T, level, dark, speed, surge)
            fr = fr * (1 - wet)[:, None] + riv * wet[:, None]
            fr += light(FOAM, 0.9 * np.exp(-((d - front) / 40) ** 2) * (front > -40))
            fr += light(GREEN, 0.6 * np.exp(-((d - front) / 160) ** 2) * (front > -100))

        # the horn calls on the rock: emerald streaks out along Right
        p_run = run_off(G, t)
        for t0 in horn:
            a = t - t0
            if 0 <= a < 1.2:
                q = p_run + 1500 * a
                fr += light(SIEGFRIED, 0.95 * np.exp(-a / 0.6) * np.exp(-((d - q) / 60) ** 2))

        # the Rhine's figure: every note a white crest flicking downstream
        for k, ons in enumerate(rhine):
            for j, t0 in enumerate(ons):
                a = t - t0
                if 0 <= a < 0.9:
                    q = (L - (j * 157 + k * 311) % L) - 900 * a
                    fr += light(FOAM, 0.8 * np.exp(-a / 0.35) * np.exp(-((d - q) / 30) ** 2))

        # his boat: an emerald streak racing down the whole river with a white wake
        for k, t0 in enumerate(boat_t):
            a = t - t0
            if 0 <= a < 5.0:
                q = L + 40 - (L + 120) * smoothstep(0, 4.2, a)
                g = 1 - smoothstep(4.0, 5.0, a)
                wake = (d > q) * np.exp(-(d - q) / 320)
                fr = fr * (1 - 0.75 * g * np.exp(-((d - q) / 120) ** 2))[:, None]
                fr += light(SIEGFRIED, g * np.exp(-((d - q) / 40) ** 2))
                fr += light(HEAD, 0.9 * g * np.exp(-((d - q) / 9) ** 2))
                fr += light(SIEGFRIED, 0.7 * g * wake)
                fr += light(FOAM, 0.35 * g * wake * np.clip(np.sin(d / 9 - 25 * t), 0, 1))

        # the Rhinegold: gold glints over the water, note by note
        for j, (t0, dur, m, v, part, k) in enumerate(gold):
            a = t - t0
            if 0 <= a < 1.2:
                q = glint_at[j] - 300 * a
                fr += light(GOLD, 0.95 * np.exp(-a / 0.45) * np.exp(-((d - q) / 26) ** 2))
                fr += light(GLINT, 0.5 * np.exp(-a / 0.2) * np.exp(-((d - q) / 9) ** 2))
        if T_GOLD <= t < T_GOLD + 6:
            a = t - T_GOLD
            fr += light(GOLD, 0.25 * smoothstep(0, 0.5, a) * (1 - smoothstep(3, 6, a)) * (0.6 + 0.4 * np.sin(d / 60 + 3 * t)))

        # the dark turn: a red flash through the water on each note of the renunciation
        for j, t0 in enumerate(renounce):
            a = t - t0
            if 0 <= a < 1.5:
                fr += light(BLOOD, (1.0 if j == 0 else 0.75) * np.exp(-a / 0.45) * (0.55 + 0.45 * np.sin(d / 120 + j)))
                fr += light(MURK, 0.7 * np.exp(-a / 0.8))

        # the Ring: gold and red rings pulsing out over the river, heavier, then darker
        for k, ons in enumerate(ring):
            for j, t0 in enumerate(ons):
                a = t - t0
                if 0 <= a < 2.0:
                    c = (j * 431 + 260 + k * 700) % L
                    r = 900 * (1 - np.exp(-a / 0.7))
                    g = (0.95 - 0.3 * k) * np.exp(-a / 0.8)
                    fr += light(GOLD, g * np.exp(-((np.abs(d - c) - r) / 85) ** 2))
                    fr += light(BLOOD, 0.75 * g * np.exp(-((np.abs(d - c) - 0.8 * r) / 55) ** 2))
                    fr += light(GOLD, 0.8 * np.exp(-a / 0.2) * np.exp(-((d - c) / 40) ** 2))

        # toward the hall: torchlight glimmering amber and purple on the porch as the light goes
        if t >= T_RING[1]:
            g = smoothstep(T_RING[1], D - 4, t)
            flick = 0.65 + 0.35 * np.sin(2 * np.pi * (d / 37 + 1.3 * t)) * np.sin(2 * np.pi * (d / 23 - 0.9 * t))
            fr += light(AMBER, 0.55 * g * S['porch'] * flick)
            fr += light(CHORD, 0.4 * g * S['porch'] * (1 - flick))
            for t0 in np.arange(T_RING[1] + 4, D - 1, 2.0):
                a = t - t0
                if 0 <= a < 1.5:
                    fr += light(AMBER, 0.6 * np.exp(-a / 0.5) * np.exp(-((np.abs(d - S['summit']) - 700 * a) / 90) ** 2))

        # Siegfried running off the rock, and Brünnhilde waving and fading with the morning
        if t < T_EXIT + 0.5:
            ls = SIEGFRIED_START[2] * (1 - smoothstep(T_EXIT - 0.5, T_EXIT + 0.5, t))
            fr = figure(fr, S, p_run, SIEGFRIED, ls)
            fr += light(HEAD, 0.7 * ls * np.exp(-((d - p_run) / 6) ** 2))
        lb = BRUNNHILDE_START[2] * (1 - smoothstep(6.0, 14.0, t))
        if lb > 0:
            fr = figure(fr, S, p_b, BRUNNHILDE, lb)
            fr += light(GLINT, 0.5 * lb * np.exp(-((d - p_b - 9) / 5) ** 2))
            fr += light(GOLD, RING_ON_HER * lb / BRUNNHILDE_START[2] * np.exp(-((d - p_b + 9) / 4) ** 2))
            for t0 in (1.2, 2.5, 3.8, 5.1, 6.4):
                a = t - t0
                if 0 <= a < 1.5:
                    r = 1300 * (1 - np.exp(-a / 0.6))
                    fr += light(BRUNNHILDE, 0.6 * np.exp(-a / 0.7) * np.exp(-((np.abs(d - p_b) - r) / 140) ** 2))
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

    for name, gain, rev in (('low', 0.3, 0.25), ('strings', 0.28, 0.35), ('brass', 0.3, 0.3), ('perc', 0.26, 0.3),
                            ('harp', 0.22, 0.4), ('winds', 0.26, 0.35), ('fx', 0.08, 0.3), ('dark', 0.26, 0.4)):
        M.bus(name, gain=gain, reverb=rev)
    vc = M.sampler('Strings/Cello Section/susvib/*.wav', tune=-12)
    vla = M.sampler('Strings/Viola Section/susvib/*.wav', tune=-12)
    vln = M.sampler('Strings/Violin Section/susVib/*.wav', tune=-12)
    cb = M.sampler('Strings/Solo Contrabass/SusNV/*.wav', tune=-12)
    harp = M.sampler('Strings/Harp/*.wav')
    horn = M.sampler('Brass/F Horn/sus/*.wav', tune=-12)
    tbn = M.sampler('Brass/Tenor Trombone/sus/*.wav', tune=-12)
    tuba = M.sampler('Brass/Tuba/sus/*.wav', tune=-12)
    clar = M.sampler('Woodwinds/Clarinet/susLong/*.wav', tune=-12)
    fl = M.sampler('Woodwinds/Flute/susNV/*.wav', tune=-12)
    glock = M.sampler('Percussion/Glock/*.wav')
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
    L = S['L']

    def boat_pan(t, t0):
        return pan_at(L + 40 - (L + 120) * min(1.0, max(0.0, (t - t0) / 4.2)))

    for t, d, m, v, part, k in compose():
        if part == 'horn':
            p = pan_at(run_off(G, t))
            if d > 1.0:
                hold('brass', horn, m, t, t + d, v, p, rise=0.08, fall=0.8, gain=0.85)
            else:
                M.add('brass', horn.play(m, v, dur=d * 1.05, release=0.3), t, 0.9, p)
        elif part == 'flood':
            M.add('perc', crash.play(110), t, 0.7, pan_at(L - 100))
            M.add('fx', whoosh(3.0, 200, 2500, 0.8, seed=6), t, 1.0, 0.0)
            M.add('perc', timp.play(v, pitch=-4), t, 0.7, pan_at(L - 100))
        elif part == 'rhine':
            if m < note('Eb3'):
                M.add('low', vc.play(m + 12 * (m < note('Eb2')), v - 6, dur=d * 1.1, release=0.2), t, 0.6, 0.0)
            elif m < note('Eb4'):
                M.add('strings', vla.play(m, v, dur=d * 1.1, release=0.15), t, 0.6, 0.0)
            else:
                M.add('strings', vln.play(m, v, dur=d * 1.1, release=0.15), t, 0.6, 0.0)
                M.add('harp', harp.play(m, v - 20), t, 0.4, 0.0)
        elif part == 'boat':
            t0 = T_BOAT[k]
            if d > 1.0:
                hold('brass', horn, m, t, t + d, v, boat_pan(t, t0), rise=0.08, fall=0.8, gain=0.85)
            else:
                M.add('brass', horn.play(m, v, dur=d * 1.05, release=0.3), t, 0.9, boat_pan(t, t0))
            if k >= 2 and d > 1.0:
                M.add('perc', timp.play(v - 14, pitch=-3), t, 0.5, boat_pan(t, t0))
        elif part == 'gold':
            M.add('winds', fl.play(m, v, dur=d * 1.1, release=0.2), t, 0.6, 0.0)
            if m >= note('E4'):
                M.add('harp', glock.play(m, v - 10), t, 0.45, 0.0)
        elif part == 'renounce':
            hold('brass', tbn, m, t, t + d, v, 0.0, rise=0.08, fall=1.0, gain=0.85)
            M.add('low', tuba.play(m - 12, v - 10, dur=d * 1.05, release=0.3), t, 0.7, 0.0)
            if t == T_RENOUNCE:
                M.add('perc', gong.play(110), t, 0.8, 0.0)
        elif part == 'ring':
            if d > 1.0:
                hold('winds', clar, m + 12, t, t + d, v, 0.0, rise=0.15, fall=0.8, gain=0.7)
            else:
                M.add('winds', clar.play(m + 12, v, dur=d * 1.05, release=0.3), t, 0.8, 0.0)
            M.add('low', tuba.play(m, v - 10, dur=d * 1.05, release=0.3), t, 0.7, 0.0)
        elif part == 'pedal':
            hold('low', cb, m + 12, t, t + d, v, 0.0, rise=2.0, fall=2.0, gain=0.45)
        elif part == 'dusk':
            hold('dark', vc, m, t, t + d, v, 0.0, rise=3.0, fall=1.5, gain=0.5)
