"""Siegfried's Rhine Journey: the interlude between the Prologue and the first act.

The music is Wagner's own, from the end of the Prologue as Solti's 1958 Vienna Philharmonic recording takes it:
the duet's last chord and Siegfried's horn call twice (bars 669-675), the call again quicker as the orchestra takes it up (682-692), the
journey's great climax, the Rhine in full flood in A major (776-812), and the Rhinegold glinting in E flat
before the music darkens toward the Gibichungs' hall (838-848). The notes come from the Wagner Ring Dataset's
piano reduction (pixelhome/ring.py): the horn call on horns, echoing off the far bank; the river's figuration on
violins and flutes, its current on violas and cellos; at the climax the theme in horns and trumpets over the
whole brass; the Rhinegold on flutes, harp and glockenspiel; the dark turn on trombones and tuba. The river
rushes the length of the house, splashing and timpani mark the boat racing past, cymbals the climax's great
downbeats, a gong the dark turn; the effects lead as the water floods in and back off under the theme.

The horn call carries him down off the rock: from the head of Porch Right he runs out along Right to the free
end in an emerald streak, every note an emerald flash, while Brünnhilde waves a last silver pulse on the summit
and fades with the morning. Then the river takes the house: water floods in from the free end of Right and races
back the whole length of the roofline, and from then on every run is the Rhine, indigo, teal and green currents
rushing downstream, swelling and darkening with the orchestra; every great accent of the climax sends a wall of
white water racing downstream end to end, and his boat comes again and again, an emerald comet with a white
wake. The Rhinegold scatters gold glints over the water note by note; then the dark turn, the water going
violet-indigo with red flashes through it, and heavy gold and red rings pulsing out as the light goes, the
torchlight of the hall glimmering on the porch.

compose() tags every note; stage(), heat(), fire(), scene(), strand() and figure() are shared word for word by
the Prologue's scenes (see GD01); river() is this scene's own."""
import numpy as np
from pixelhome.audio import whoosh
from pixelhome.fx import DT, hexc, light, smoothstep, nframes, keys, Flicker, smooth_noise, colormap
from pixelhome.ring import Orchestra, accents, excerpt, tidy

CODE = 'GD06'
TITLE = "Siegfried's Rhine Journey"
KIND = 'show'
DESCRIPTION = ("Siegfried's horn carries him down the mountain to the Rhine, and the whole house becomes the river, "
               'rushing end to end with his emerald boat racing along it, until the water darkens toward an '
               'unfriendly hall.')
VOICEOVER = ('Down the mountain and along the river Rhine, Siegfried sets off in search of adventure.')

K = 5                                       # this scene's place on the Prologue's shared clock: T = t + 80 K
EX = excerpt(__file__)                      # Prologue, bars 669-675, 682-692, 776-812, 838-848, Solti 1958
BAR = {int(m): t for m, t in EX['bars']}
D = EX['seconds']
T_HORN = [BAR[670], BAR[673]]               # the horn call, twice, carrying him off the rock
T_EXIT = BAR[674]                           # he is out at the free end of Right
T_FLOOD = BAR[683]                          # the call again, quicker: the water floods in
FLOOD_SPEED = 420.0
T_BOAT = [BAR[683], BAR[776], BAR[787], BAR[795], BAR[802], BAR[809]]   # his boat racing down the river
T_CLIMAX = BAR[787]                         # A major: the Rhine in full flood
T_GOLD = BAR[838]                           # the Rhinegold
T_RENOUNCE = BAR[843]                       # the dark turn
T_RING = [BAR[845], BAR[847]]

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
    """Every note of the excerpt, tagged: (time, seconds, midi, velocity, part, k). The horn call's right hand at the
    start is 'horn' (k = which call); from the flood on the right hand is the river ('rhine', k = its bar), the left
    hand its current ('flow'); the Rhinegold's right hand is 'gold', the dark turn 'renounce', the close 'ring'
    (k = which of its two halves). 'flood' marks the water's arrival; it makes no sound of its own."""
    bar_of = lambda t: max(m for m, bt in EX['bars'] if bt <= t + 1e-6)
    N = []
    for t, d, m, v, h, trem in tidy(EX['notes']):
        b = bar_of(t)
        if t < T_FLOOD:
            part, k = ('horn', 0 if b < 673 else 1) if h == 0 and b >= 670 else ('pedal', None)
        elif b < 838:
            part, k = ('rhine', b) if h == 0 else ('flow', b)
        elif b < 843:
            part, k = ('gold', None) if h == 0 else ('flow', b)
        elif b < 845:
            part, k = 'renounce', None
        else:
            part, k = 'ring', 0 if b < 847 else 1
        N.append((t, d, m, v, part, k, trem))
    N.append((T_FLOOD, 2.0, 27, 0, 'flood', None, False))
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
    rhine = [sorted({e[0] for e in N if e[4] == 'rhine' and e[5] == b}) for b in sorted({e[5] for e in N if e[4] == 'rhine'})]
    boat_t = T_BOAT
    gold = [e for e in N if e[4] == 'gold']
    glint_at = np.random.default_rng(seed).uniform(0, L, len(gold))
    renounce = accents([e for e in N if e[4] == 'renounce'], n=3, space=0.6)
    ring = [accents([e for e in N if e[4] == 'ring' and e[5] == k], n=2, space=0.9) for k in range(2)]

    # how loud the orchestra is, frame by frame (0..1): the river swells with it
    loud = np.zeros(F)
    for e in N:
        if e[3] > 0:
            loud[min(F - 1, int(e[0] / DT))] += (e[3] / 127) ** 2
    kern = np.exp(-np.arange(int(0.8 / DT)) * DT / 0.35)
    loud = np.convolve(loud, kern)[:F]
    loud = np.clip(loud / np.percentile(loud[loud > 0], 97), 0, 1)
    waves = accents([e for e in N if T_FLOOD <= e[0] < T_GOLD], vmin=104, n=3, space=0.9)

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
        surge = loud[f]
        if t >= T_FLOOD:
            riv = river(S, T, level * (0.5 + 0.7 * surge ** 1.5), dark, speed, surge)
            fr = fr * (1 - wet)[:, None] + riv * wet[:, None]
            fr += light(FOAM, 0.9 * np.exp(-((d - front) / 40) ** 2) * (front > -40))
            fr += light(GREEN, 0.6 * np.exp(-((d - front) / 160) ** 2) * (front > -100))

        # the orchestra's great accents: a wall of white water racing downstream the length of the house
        for t0 in waves:
            a = t - t0
            if 0 <= a < 2.6:
                q = L + 60 - 1100 * a
                g = (1 - smoothstep(1.8, 2.6, a)) * (0.6 + 0.4 * (t0 >= T_CLIMAX))
                fr += light(FOAM, g * np.exp(-((d - q) / 80) ** 2))
                fr += light(GREEN, 0.9 * g * (d > q) * np.exp(-(d - q) / 300))

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
                fr += light(SIEGFRIED, g * np.exp(-((d - q) / 70) ** 2))
                fr += light(HEAD, g * np.exp(-((d - q) / 14) ** 2))
                fr += light(SIEGFRIED, 0.7 * g * wake)
                fr += light(FOAM, 0.35 * g * wake * np.clip(np.sin(d / 9 - 25 * t), 0, 1))

        # the Rhinegold: gold glints over the water, note by note
        for j, (t0, dur, m, v, part, k, _) in enumerate(gold):
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
        if t >= BAR[846]:
            g = smoothstep(BAR[846], D - 3, t)
            flick = 0.65 + 0.35 * np.sin(2 * np.pi * (d / 37 + 1.3 * t)) * np.sin(2 * np.pi * (d / 23 - 0.9 * t))
            fr += light(AMBER, 0.55 * g * S['porch'] * flick)
            fr += light(CHORD, 0.4 * g * S['porch'] * (1 - flick))
            for t0 in np.arange(BAR[846] + 2, D - 1, 2.0):
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
    """Wagner's notes, orchestrated from the piano reduction, with the river and the horn's echo off the hills."""
    order = np.argsort(G.pd)
    xs, ds = G.pos[order, 0], G.pd[order]
    x0, x1 = xs.min(), xs.max()

    def pan_at(dd):                         # path distance -> left/right across the facade, from the street
        x = np.interp(dd, ds, xs)
        return float(0.85 * (2 * (x - x0) / (x1 - x0) - 1))

    S = stage(G)
    L = S['L']
    o = Orchestra(M, level=1.3)

    def boat_pan(t):
        live = [t0 for t0 in T_BOAT if t0 <= t < t0 + 4.2]
        return pan_at(L + 40 - (L + 120) * (t - live[-1]) / 4.2) if live else 0.0

    for t, d, m, v, part, k, trem in compose():
        if part == 'horn':                  # his horn call, and its echo off the far side of the valley
            p = pan_at(run_off(G, t))
            o.play('horns', m, t, d, v, p, 0.95)
            o.play('horns', m, t + 0.32, d, v - 30, -p * 0.8, 0.35)
        elif part == 'pedal':
            o.play('cellos trem' if trem else 'cellos', m + 12, t, d, v - 10, 0.0, 0.4)
            o.play('basses', m + 12 if m < 28 else m, t, d, v - 10, 0.0, 0.4)
        elif part == 'rhine':
            if t < BAR[688]:                # the call again, quicker: horns on the boat
                o.play('horns', m, t, d, v, boat_pan(t), 0.9)
            elif t >= T_CLIMAX and d >= 0.4:    # the climax: the theme in the full brass over the violins
                o.play('horns', m, t, d, v, -0.3, 0.75)
                o.play('trumpets', m, t, d, v - 12, 0.3, 0.45)
                o.play('violins', m + 12 if m < 67 else m, t, d, v - 8, 0.25, 0.5)
            else:
                o.play('violins', m, t, d, v - 6, 0.3, 0.55)
                if m >= 77:
                    o.play('flutes', m, t, 0.1, v - 16, -0.4, 0.35)
        elif part == 'flow':
            if d < 0.3:
                o.play('violas' if m >= 55 else 'cellos', m, t, d, v - 6, -0.2, 0.5)
            else:
                o.play('cellos', m, t, d, v, -0.2, 0.65)
                o.play('basses', m - 12 if m >= 40 else m, t, d, v - 6, 0.2, 0.5)
                if t >= T_CLIMAX:
                    o.play('trombones', m, t, d, v - 8, 0.1, 0.5)
                    o.play('tuba', m - 12 if m >= 40 else m, t, d, v - 12, 0.0, 0.4)
        elif part == 'gold':                # the Rhinegold: flutes, harp and glockenspiel glinting over the water
            gp = 0.6 * np.sin(t * 2.1)
            o.play('flutes', m, t, d, v + 10, gp, 0.55)
            o.play('harp', m, t, 0.3, v + 15, gp, 0.6)
            o.play('glock', m, t, 0.3, v, gp, 0.35)
        elif part == 'renounce':            # the dark turn: the strings' plunge, the brass under it
            if d >= 0.5:
                o.play('trombones', m if m < 60 else m - 12, t, d, v, 0.0, 0.75)
                o.play('horns', m if m < 72 else m - 12, t, d, v - 6, -0.2, 0.6)
                if m < 48:
                    o.play('tuba', m, t, d, v - 6, 0.0, 0.55)
            else:
                o.play('violins' if m >= 55 else 'cellos', m, t, d, v - 4, 0.25, 0.55)
        elif part == 'ring':                # the close: low brass and clarinets, darkening
            if d >= 0.5:
                o.play('clarinets', m, t, d, v - 10, -0.2, 0.55)
                o.play('trombones' if m >= 46 else 'tuba', m, t, d, v - 10, 0.0, 0.6)
            else:
                o.play('violas' if m >= 55 else 'cellos', m, t, d, v - 14, 0.1, 0.45)
    # the river: a rush of water that floods in from the free end of Right and runs to the end
    rush = lambda tt: (0.35 + 0.35 * (tt >= T_CLIMAX) * (tt < T_GOLD) + 0.15 * (tt < BAR[776])) * \
        (1 - 0.6 * (tt >= T_RENOUNCE))
    o.wind(T_FLOOD - 0.5, D, level=rush, pan=0.0, seed=21)
    # the river and the boat lead while the water floods in; they back off under the climax's theme and the gold
    o.effects([(0, -4), (T_FLOOD - 0.5, 0), (BAR[776], -2), (T_CLIMAX - 0.5, -2), (T_CLIMAX + 1.0, -9),
               (T_GOLD - 0.5, -9), (T_GOLD + 0.5, -12), (T_RENOUNCE, -6), (D, -6)])
    o.boom(T_FLOOD, pan_at(L - 100), 0.7)
    o.hit('crash', T_FLOOD, 112, gain=0.5, pan=pan_at(L - 100))
    M.add('fx', np.vstack([whoosh(3.0, 200, 2500, 0.8, seed=6)[0]] * 2), T_FLOOD, 0.8, 0.4)
    for t0 in T_BOAT[1:]:                    # each time the boat races past: a splash of foam and a timpani stroke
        M.add('fx', np.vstack([whoosh(1.6, 2500, 400, 0.6, seed=int(t0))[0]] * 2), t0, 0.6, boat_pan(t0 + 1.0))
        o.hit('timpani', t0, 112, pitch=-3, gain=0.5, pan=boat_pan(t0 + 0.2))
    for b in (787, 795, 802, 809):          # the climax's great downbeats
        o.hit('crash', BAR[b], 118, gain=0.55)
    o.hit('cymbal swell', BAR[785] - 1.0, 100, gain=0.45)
    for t0 in renounce_hits():               # the dark turn: a gong, the timpani
        o.hit('gong', t0, 112, gain=0.6)
        o.hit('timpani', t0, 120, pitch=-6, gain=0.6)
    for t0 in T_RING:
        o.hit('gong', t0, 96, gain=0.4)
        o.hit('timpani roll', t0, 96, pitch=-5, gain=0.4)


def renounce_hits():
    N = compose()
    return accents([e for e in N if e[4] == 'renounce'], n=3, space=0.6)[:2]
