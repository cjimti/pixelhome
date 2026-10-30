"""Dawn: the Norns are gone and the night is lifting off Brünnhilde's rock. The red in the east, at the free end of
Right, swells; then the Dawn comes round, and every note of it is a wave of colour that leaves the east and races
the whole length of the house to the far end of the Side, laying the new colour behind it. Each time it comes round
it is fuller and the colour has climbed: deep red, then orange, then gold, then white-gold, while the night drains
out, the stars go out and the sky turns from indigo to blue.

The music is Wagner's own: the orchestral daybreak between the Norns' scene and the duet (bars 335 to 361), as
Solti's 1958 Vienna Philharmonic recording takes it, from the first glimmer in the low strings through the swelling
statements of the Dawn to Siegfried's motif on the horns and the full orchestra's blaze. The notes come from the
Wagner Ring Dataset's piano reduction (pixelhome/ring.py), orchestrated by hand and register and growing with the
light: strings and woodwinds at first, the horns joining, then trombones, tuba and trumpets; their tremolos on the
strings' tremolo. A suspended cymbal swells into the sunrise, and the timpani and cymbals mark its downbeats.

On the summit two figures rise out of the rock in bursts of light: Siegfried in emerald as his motif rings out on
the horns, then Brünnhilde in silver and gold. At the climax the whole orchestra has it and the house blazes:
gold-white sweeps crossing both ways on every downbeat, every run in full morning, before it settles into the
bright day with the two of them standing on the summit.

compose() tags every note of the excerpt; stage(), heat(), fire(), scene(), strand() and figure() are shared word
for word by the Prologue's scenes (see GD01)."""
import numpy as np
from pixelhome.fx import DT, hexc, light, smoothstep, nframes, keys, Flicker, smooth_noise, colormap
from pixelhome.ring import Orchestra, excerpt, tidy

CODE = 'GD03'
TITLE = 'Dawn'
KIND = 'show'
DESCRIPTION = ('Daybreak over the mountain: wave after wave of colour races across the house from the east, red '
               'to gold to white, until Siegfried and Brünnhilde stand on the summit in full morning.')
VOICEOVER = ('The sun comes up over the mountain. Siegfried and Brünnhilde wake to a new day.')

K = 2                                       # this scene's place on the Prologue's shared clock: T = t + 80 K
EX = excerpt(__file__)                      # bars 335-361, Solti 1958
BAR = {int(m): t for m, t in EX['bars']}
T_DAWN = [(BAR[337], 0.08), (BAR[341], 0.3), (BAR[345], 0.55), (BAR[349], 0.8)]   # (time, hue it lays)
WAVE_BARS = [(337, 341), (341, 345), (345, 349), (349, 352)]
T_RISE_S = BAR[349]                         # Siegfried rises: his motif on the horns
T_RISE_B = BAR[352]                         # Brünnhilde rises
T_CLIMAX = [BAR[354], BAR[358]]             # the full orchestra
T_SETTLE = BAR[361]
D = EX['seconds']

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

START = dict(night=0.5, stars=0.6, rock=0.32, fire=0.4, east=0.35, dawn=0.0, hue=0.0, day=0.0, rope=0.0)
END = dict(night=0.0, stars=0.0, rock=0.35, fire=0.15, east=0.0, dawn=0.75, hue=0.62, day=0.3, rope=0.0)
SIEGFRIED_END = ('Porch Front', 0.35, 0.85)     # (segment, u, level)
BRUNNHILDE_END = ('Porch Front', 0.6, 0.9)


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


def bar_of(t):
    return max([m for m, bt in BAR.items() if bt <= t + 1e-6] or [335])


def compose():
    """Every note of the excerpt, tagged: (time, seconds, midi, velocity, part, k). The longer notes of each swell
    are the Dawn ('dawn', k = which swell); the right hand's long notes as she rises are Brünnhilde ('brunn'); the
    long notes of the full orchestra are the climax ('climax', k = which half); the rest 'orch'."""
    N = []
    for n in tidy(EX['notes']):
        t, d, m, v, h = n[:5]
        b = bar_of(t)
        k = next((i for i, (b0, b1) in enumerate(WAVE_BARS) if b0 <= b < b1), None)
        if k is not None and d >= 0.3 and not n[5]:
            N.append((t, d, m, v, 'dawn', k))
        elif b in (352, 353) and h == 0 and d >= 0.3:
            N.append((t, d, m, v, 'brunn', None))
        elif b >= 354 and d >= 0.3 and not n[5]:
            N.append((t, d, m, v, 'climax', 0 if b < 358 else 1))
        else:
            N.append((t, d, m, v, 'orch', None))
    return sorted(N, key=lambda e: e[0])


def render(G, seed=3):
    F = nframes(D)
    out = np.zeros((F, G.N, 3))
    S = stage(G)
    d, L = S['d'], S['L']
    N = compose()
    waves = sorted({(round(e[0], 2), T_DAWN[e[5]][1], 0.75 + 0.08 * e[5]) for e in N if e[4] == 'dawn'})
    waves += sorted({(round(e[0], 2), 1.0, 1.0) for e in N if e[4] == 'climax'})
    waves.sort()
    climax = [e for e in N if e[4] == 'climax']
    brunn = sorted({e[0] for e in N if e[4] == 'brunn'})
    p_s, p_b = at(G, *SIEGFRIED_END[:2]), at(G, *BRUNNHILDE_END[:2])
    speed = 2100.0

    for f in range(F):
        t = f * DT
        T = t + 80 * K
        prog = smoothstep(T_DAWN[0][0], T_DAWN[3][0] + 8, t)
        lv = dict(START)
        lv['night'] = START['night'] * (1 - prog)
        lv['stars'] = START['stars'] * (1 - smoothstep(0, 26, t))
        lv['east'] = keys(t, [(0, START['east']), (T_DAWN[0][0], 0.6), (T_DAWN[2][0], 0.5), (T_CLIMAX[0], 0.0)])
        lv['fire'] = keys(t, [(0, START['fire']), (T_CLIMAX[0], END['fire'])])
        lv['rock'] = keys(t, [(0, START['rock']), (T_CLIMAX[0], END['rock'])])
        # the hue the sky has reached: the last wave to have crossed the whole house
        crossed = [h for t0, h, g in waves if t - t0 > L / speed]
        lv['hue'] = keys(t, [(0, 0.0), (T_DAWN[3][0] + 6, 0.8), (T_SETTLE, 0.75), (D, END['hue'])])
        lv['dawn'] = keys(t, [(0, 0.0), (T_DAWN[0][0], 0.1), (T_DAWN[3][0] + 6, 0.75), (D, END['dawn'])])
        lv['day'] = keys(t, [(0, 0.0), (T_DAWN[2][0], 0.0), (T_CLIMAX[0], 0.25), (D, END['day'])])
        fr = scene(S, T, lv)

        # every note of the Dawn: a wave of the new colour leaving the east and racing to the end of the Side
        for t0, hue, g in waves:
            a = t - t0
            if not 0 <= a < L / speed + 1.2:
                continue
            front = L - speed * a
            fade = 1 - smoothstep(L / speed, L / speed + 1.2, a)
            col = DAWN(np.array([hue]))[0]
            band = np.exp(-((d - front) / 240) ** 2)
            behind = (d >= front) * np.exp(-(d - front) / 900)
            fr += light(col, g * fade * (band + 0.6 * behind))
            fr += light(HOT if hue > 0.5 else col, 0.7 * g * fade * np.exp(-((d - front) / 30) ** 2))

        # the climax: sweeps crossing both ways and the house flashing gold-white on every downbeat
        for t0, dur, m, v, part, k in climax:
            a = t - t0
            if 0 <= a < 1.4 and m == min(e[2] for e in climax if e[0] == t0):
                pos = speed * 0.8 * a
                fr += light(SUN, 0.9 * np.exp(-a / 0.6) * np.exp(-((d - pos) / 180) ** 2))
                fr += light(SUN, 0.45 * np.exp(-a / 0.35))

        # Brünnhilde's motif: silver and gold bursts out from the summit
        for t0 in brunn:
            a = t - t0
            if 0 <= a < 1.8:
                r = 1100 * (1 - np.exp(-a / 0.6))
                fr += light(BRUNNHILDE, 0.8 * np.exp(-a / 0.7) * np.exp(-((np.abs(d - p_b) - r) / 90) ** 2))
                fr += light(GLINT, 0.6 * np.exp(-a / 0.4) * np.exp(-((np.abs(d - p_b) - 0.7 * r) / 40) ** 2))

        # the two of them rise out of the rock in bursts of light
        for p, col, t0, lvl_end in ((p_b, BRUNNHILDE, T_RISE_B, BRUNNHILDE_END[2]),
                                    (p_s, SIEGFRIED, T_RISE_S, SIEGFRIED_END[2])):
            if t < t0 - 0.2:
                continue
            a = t - t0
            lvl = lvl_end * smoothstep(-0.2, 1.0, a)
            if 0 <= a < 1.6:
                fr += light(col, 1.0 * np.exp(-a / 0.35) * np.exp(-((d - p) / 70) ** 2))
                fr += light(col, 0.7 * np.exp(-a / 0.6) * np.exp(-((np.abs(d - p) - 900 * a) / 80) ** 2))
            fr = figure(fr, S, p, col, lvl)
            if col is SIEGFRIED:
                fr += light(HEAD, 0.7 * lvl * np.exp(-((d - p) / 6) ** 2))
            else:
                fr += light(GLINT, 0.5 * lvl * np.exp(-((d - p - 9) / 5) ** 2))
        out[f] = fr
    return np.clip(out, 0, 1)


def score(M, G):
    """Wagner's notes, orchestrated from the piano reduction and growing with the light, with the cymbal swelling
    into the sunrise and the timpani on its downbeats."""
    order = np.argsort(G.pd)
    xs, ds = G.pos[order, 0], G.pd[order]
    x0, x1 = xs.min(), xs.max()

    def pan_at(dd):                         # path distance -> left/right across the facade, from the street
        x = np.interp(dd, ds, xs)
        return float(0.85 * (2 * (x - x0) / (x1 - x0) - 1))

    S = stage(G)
    east = pan_at(S['L'] - 100)
    ss = pan_at(at(G, *SIEGFRIED_END[:2]))
    o = Orchestra(M, level=2.25)
    N = compose()
    tag = {(round(e[0], 4), e[2]): e[4] for e in N}

    def size(t):                                                    # the orchestra grows with the light
        return float(np.interp(t, [0, BAR[341], BAR[349], T_CLIMAX[0]], [0.2, 0.4, 0.7, 1.0]))

    def role(t, d, m, v, h):
        part = tag.get((round(t, 4), m), 'orch')
        if part == 'dawn' and t < BAR[345]:                         # the first swells: cellos and violas, clarinets
            return [('cellos' if m < 55 else 'violas', 0, 4, 0.7), ('clarinets', 0, -10, 0.35)]
        if part == 'dawn' and t >= T_RISE_S and h == 1 and m >= 50:   # Siegfried's motif: horns
            return [('horns', 0, 8, 0.85), ('horns', -12, 0, 0.45)]
        if part == 'brunn':                                         # Brünnhilde: violins and oboes
            return [('violins', 0, 4, 0.6), ('oboes', 0, -6, 0.4)]
        return None

    def pan(t, m):                                                  # the light comes from the east
        return east * (1 - smoothstep(0, T_CLIMAX[0], t)) * 0.8

    o.tutti(tidy(EX['notes']), size=size, role=role, pan=pan)
    o.hit('cymbal swell', T_CLIMAX[0] - 4.5, 100, gain=0.5)         # swelling into the sunrise
    for k, tc in enumerate(T_CLIMAX):
        o.hit('crash', tc, 118, gain=0.7)
        o.hit('bass drum', tc, 118, gain=0.6)
    for b in range(354, 362):                                       # the timpani on every downbeat of the blaze
        o.hit('timpani', BAR[b], 118 if b in (354, 358) else 104, pitch=-2, gain=0.7)
    o.hit('timpani roll', T_RISE_S - 1.0, 96, pitch=-3, gain=0.4, pan=ss)
    o.effects([(0.0, 0.0), (D, 0.0)])                              # nothing on the effects bus: this is the orchestra's
