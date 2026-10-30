"""Heil dir, Sonne!: the summit of the rock in the last of the night, the fire low round the porch, Brünnhilde a
sleeping silver glow at the summit and Siegfried, emerald, beside her at Porch Front 0.42.

The music is Wagner's own: Act III, bars 1062-1064 and 1088-1098 of Siegfried, as Solti's 1958 Vienna
Philharmonic recording takes them, from the Wagner Ring Dataset's piano reduction (pixelhome/ring.py): the
awakening's last great surge of chords, and then her greeting to the sun over the harps. Her voice is not in the
reduction, so her line comes from the printed vocal score (Breitkopf & Härtel, 1914, archive.org 31761034115105,
pp. 321-322) and is played as written on a trumpet doubled by violins: "Heil dir, Sonne!" (E, B, C, and down the
octave to low C), "Heil dir, Licht!" (E, B, D), "Heil dir, leuchtender Tag!" (E, low E, E-D-C, and up to G). The
chords are on the full orchestra, the arpeggios that ripple up between her phrases on the harp, the long chords
on strings and horns. A production's sounds help the waking land: a shimmer of triangle and glockenspiel on the
kiss, cymbal swells into the sunrise chords and the last blaze, the fire round the rock dying away as the sun
comes up; they are ridden right down under her greeting.

He bends to kiss her: a thread of emerald reaches across to the silver, and where they touch the whole house
flashes. The awakening's chords each roll a wave of sunrise out from the summit to both ends of the house, rose at
its front, gold behind, while the night, the storm and the fire drain away and the sky comes up rose, gold and
blue on every run. Her glow becomes Brünnhilde herself, silver white with gold glints, rising to Porch Front 0.55.
She greets the sun: each note of hers lights her brighter, and each phrase ends in a burst of gold out from her.
Between her phrases every note of the harps sends a spark of gold or rose racing out from her to the ends of the
house. On "leuchtender Tag!" the orchestra swells, every chord a band of sunrise racing end to end, and on her
high G the whole house blazes rose, gold and sky blue and holds it.

compose() holds every note; stage(), sky(), fire() and figure() are the rock and the sky, shared word for word by
Act III's scenes on a clock that runs on from scene to scene."""
import numpy as np
from pixelhome.audio import note
from pixelhome.fx import DT, hexc, light, smoothstep, nframes, Flicker, smooth_noise, colormap
from pixelhome.ring import Orchestra, accents, excerpt, tidy

CODE = 'SF28'
TITLE = 'Heil dir, Sonne!'
KIND = 'show'
DESCRIPTION = ('Siegfried kisses the sleeping Brünnhilde and she wakes. Night turns to sunrise across the whole '
               'house as she greets the sun, the light and the shining day.')
VOICEOVER = ('He kisses her, and she wakes. '
             'Hail to the sun, she sings. Hail to the light.')

K = 5                                       # this scene's place on Act III's shared clock: T = t + 80 K
EX = excerpt(__file__)                      # Act III, bars 1062-1064 and 1088-1098, Solti 1958
BAR = {int(m): t for m, t in EX['bars']}
D = EX['seconds'] + 2.0                     # her last note rings on
T_REACH, T_KISS = 0.0, 1.2                  # he bends to kiss her
T_CHORDS = [BAR[1063], BAR[1064], accents(EX['notes'], BAR[1064] + 1, BAR[1065], 80, 3)[0]]   # the awakening
T_DAY = BAR[1088]                           # full sunrise: her greeting begins
# Her greeting, from the vocal score: (bar, beat, beats, note), 3/4.
VOICE = [(1088, 1, 1, 'E5'), (1088, 2, 1, 'B4'), (1089, 0, 2, 'C5'), (1089, 2, 1, 'C4'),
         (1092, 1, 1, 'E5'), (1092, 2, 1, 'B4'), (1093, 0, 3, 'D5'),
         (1096, 1, 1, 'E5'), (1096, 2, 1, 'E4'), (1097, 0, 1.5, 'E5'), (1097, 1.5, 0.5, 'D5'), (1097, 2, 1, 'C5'),
         (1098, 0, 3, 'G5')]
PHRASE_ENDS = [(1089, 2), (1093, 0), (1098, 0)]
T_SWELL = BAR[1096] + 2.5                   # "leuchtender Tag!": the orchestra swells
SWELL = accents(EX['notes'], T_SWELL, D, 80, 3, 1.0)
T_BLAZE = BAR[1098]                         # her high G: the whole house blazes

STORM = hexc('#1a2ab0')
CLOUD = hexc('#4a6aff')
RAIN = hexc('#a8bcdc')
BOLT = hexc('#e8f0ff')
ROCK = hexc('#38468a')
DUSK = hexc('#7a40d0')
RED, ORANGE, AMBER = hexc('#ff2000'), hexc('#ff5000'), hexc('#ffb020')
FIRE = colormap([(0.0, hexc('#300400')), (0.3, RED), (0.55, ORANGE), (0.8, AMBER), (1.0, hexc('#fff0b0'))])
SUNRISE = colormap([(0.0, hexc('#ff4080')), (0.5, hexc('#ffc020')), (1.0, hexc('#40a0ff'))])
SILVER = hexc('#f4f8ff')
WOTAN = hexc('#1a3cff')
SPEAR = hexc('#c8d8ff')
MOSS = hexc('#30c020')
EARTH = hexc('#3a2410')
ERDA_HI = hexc('#60ff30')
TWILIGHT = hexc('#a0207a')
EMERALD = hexc('#00ff40')
HEAD = hexc('#e8ffe8')
GLINT = hexc('#ffd060')
ROSE = hexc('#ff4080')
SUN = hexc('#ffc020')
SKYBLUE = hexc('#40a0ff')
WHITE = hexc('#ffffff')

SUMMIT = dict(storm=0.25, rock=0.35, fire=0.4, wide=0.0, dawn=0.0, sleeper=0.7)
DAWN = dict(storm=0.0, rock=0.35, fire=0.15, wide=0.0, dawn=0.75, sleeper=0.0)
SIEG_AT, BRUNN_AT = 0.42, 0.55              # their places on Porch Front at the end


def at(G, seg, u):
    """Path distance u of the way along a segment."""
    s = G.pd[G.seg[seg]]
    return float(s.min() + u * (s.max() - s.min()))


def stage(G):
    """Brünnhilde's rock and the sky as profiles over the house: the porch is the rock, the summit the middle of
    Porch Front; the wings and Side are sky."""
    d = G.pd
    rng = np.random.default_rng(1871)       # the same clouds and rain in every scene, so the cuts match
    porch = np.isin(G.seg_of, ['Porch Left', 'Porch Front', 'Porch Right'])
    summit = at(G, 'Porch Front', 0.5)
    return dict(
        d=d, summit=summit, porch=porch, sky=~porch,
        crag=porch * (0.7 + 0.3 * smooth_noise(rng, d, 40.0)),
        db=np.abs(d - summit),
        rain=Flicker(rng, G.N, 4.0, 11.0),
        fl=Flicker(rng, G.N, 4.0, 11.0),
        jag=rng.uniform(0.3, 1.0, G.N),
    )


def heat(d, T):
    """Flame heat along the roofline (0..1): tongues of several sizes licking both ways."""
    h = (0.45 + 0.24 * np.sin(2 * np.pi * (d / 173 - 0.53 * T)) + 0.2 * np.sin(2 * np.pi * (d / 109 + 0.71 * T) + 1.3)
         + 0.13 * np.sin(2 * np.pi * (d / 67 - 1.37 * T) + 2.1) + 0.09 * np.sin(2 * np.pi * (d / 41 + 1.9 * T) + 0.4))
    swell = 0.75 + 0.25 * np.sin(2 * np.pi * (d / 410 + 0.23 * T)) * np.sin(2 * np.pi * (d / 260 - 0.31 * T) + 0.7)
    return np.clip((h * swell - 0.15) * 1.5, 0, 1)


def fire(S, T, ring, wide, boost=0.0):
    """The magic fire: `ring` round the rock (the porch, leaving the summit clear), `wide` out over the sky."""
    q = np.clip(heat(S['d'], T) + 0.18 * S['fl'](T) + 0.3 * boost, 0, 1)
    clear = 1 - 0.8 * np.exp(-(S['db'] / 42) ** 2)
    lvl = (ring * S['porch'] + wide * S['sky']) * clear
    return light(FIRE(q), lvl * (0.45 + 0.7 * q))


def sky(S, T, lv):
    """The sky and the rock at shared time T with levels lv (storm, rock, fire, wide, dawn, sleeper)."""
    d = S['d']
    u = 0.5 + 0.3 * np.sin(2 * np.pi * (d / 520 - 0.05 * T)) + 0.2 * np.sin(2 * np.pi * (d / 190 + 0.09 * T) + 1.1)
    st = STORM + (CLOUD - STORM) * u[:, None]
    fr = light(st, lv['storm'] * (0.7 + 0.3 * u) * S['sky'])
    fr += light(RAIN, 0.6 * lv['storm'] * S['sky'] * np.clip(S['rain'](T) - 1.0, 0, None) ** 2)
    rk = ROCK + (DUSK - ROCK) * (0.25 + 0.45 * u)[:, None]
    fr += light(rk, lv['rock'] * S['crag'])
    fr += light(SUNRISE(np.clip(0.15 + 0.7 * u + 0.15 * np.sin(0.2 * T), 0, 1)), lv['dawn'] * (0.75 + 0.25 * u))
    fr += fire(S, T, lv['fire'], lv['wide'])
    fr += light(SILVER, lv['sleeper'] * np.exp(-(S['db'] / 22) ** 2))
    return fr


def figure(fr, S, p, col, lvl, w=16.0):
    """A person at path distance p: a body that stands in front of the sky, and a halo."""
    body = np.exp(-((S['d'] - p) / w) ** 2)
    fr = fr * (1 - 0.85 * min(1.0, lvl / 0.2) * body)[:, None]
    return fr + light(col, lvl * body) + light(col, 0.35 * lvl * np.exp(-((S['d'] - p) / (3 * w)) ** 2))


def hero(fr, S, p, lvl, w=16.0):
    """Siegfried: emerald, with a white-hot head."""
    fr = figure(fr, S, p, EMERALD, lvl, w)
    return fr + light(HEAD, 0.8 * lvl * np.exp(-((S['d'] - p) / (0.35 * w)) ** 2))


def heroine(fr, S, p, lvl, T, w=16.0):
    """Brünnhilde awake: silver white, with gold glints round her."""
    fr = figure(fr, S, p, SILVER, lvl, w)
    tw = 0.5 + 0.5 * np.sin(2 * np.pi * (S['d'] / 23 + 1.3 * T)) * np.sin(2 * np.pi * (S['d'] / 37 - 0.9 * T))
    return fr + light(GLINT, 0.8 * lvl * tw ** 3 * np.exp(-((S['d'] - p) / (3 * w)) ** 2))


def when(bar, beat):
    """Excerpt time of a beat in a 3/4 bar of the second range."""
    bars = [(m, t) for m, t in EX['bars'] if m >= 1088]
    return float(np.interp(bar + beat / 3, [b[0] for b in bars], [b[1] for b in bars]))


def voice():
    """Her greeting in seconds: (time, seconds, midi)."""
    return [(when(b, x), when(b, x + n) - when(b, x), note(name)) for b, x, n, name in VOICE]


def compose():
    """Every note of the excerpt, tagged: (time, seconds, midi, velocity, hand, part, trem). 'chord' for the
    awakening's surge, 'harp' for the arpeggios between her phrases, 'long' for the held chords; 'voice' is her
    greeting from the vocal score."""
    N = []
    for t, d, m, v, h, tr in tidy(EX['notes']):
        part = 'chord' if t < T_DAY - 0.01 else 'harp' if d < 0.4 and t < T_SWELL else 'long'
        N.append((t, d, m, v, h, part, tr))
    for t, d, m in voice():
        N.append((t, d, m, 100, 0, 'voice', False))
    return sorted(N, key=lambda e: e[0])


def render(G, seed=28):
    rng = np.random.default_rng(seed)
    F = nframes(D)
    out = np.zeros((F, G.N, 3))
    S = stage(G)
    d, summit = S['d'], S['summit']
    L = d.max()
    reach = max(summit, L - summit)
    N = compose()
    heil_on = np.array([e[0] for e in N if e[5] == 'voice'])
    heil_ends = [when(b, x) for b, x in PHRASE_ENDS]
    harps = [(e[0], e[2]) for e in N if e[5] == 'harp']
    side = rng.choice([-1, 1], len(harps))
    swell = SWELL
    ps = at(G, 'Porch Front', SIEG_AT)
    pb0, pb1 = summit, at(G, 'Porch Front', BRUNN_AT)
    hue = rng.uniform(0, 1, len(swell))
    harp_t = np.array([h[0] for h in harps])

    def recent(ts, t, span):
        i = int(np.searchsorted(ts, t, side='right')) - 1
        return (t - ts[i]) if i >= 0 and t - ts[i] < span else None

    for f in range(F):
        t = f * DT
        T = t + 80 * K
        # night drains away chord by chord into the sunrise
        up = np.interp(t, [T_KISS, T_CHORDS[0], T_CHORDS[1], T_CHORDS[2], T_DAY + 1], [0.0, 0.25, 0.5, 0.8, 1.0])
        lv = {k: SUMMIT[k] + (DAWN[k] - SUMMIT[k]) * up for k in SUMMIT}
        wake = smoothstep(T_CHORDS[0], T_DAY, t)
        lv['sleeper'] = SUMMIT['sleeper'] * (1 - wake)
        mid = smoothstep(T_DAY, T_DAY + 3, t) * (1 - smoothstep(T_SWELL, T_SWELL + 2, t))
        lv['dawn'] *= 1 - 0.45 * mid            # the bed steps back so her greeting and the harps stand out
        fr = sky(S, T, lv)

        # the kiss: a thread of emerald reaching to her, and a flash where they touch
        if T_REACH <= t < T_KISS + 0.2:
            u = smoothstep(T_REACH, T_KISS, t)
            tip = ps + (summit - ps) * u
            span = (d >= ps - 4) & (d <= tip + 4)
            fr += light(EMERALD, 0.9 * span * (0.6 + 0.4 * u))
        if T_KISS <= t < T_KISS + 2.5:
            a = t - T_KISS
            fr += light(WHITE, min(1.0, 0.9 * np.exp(-a / 0.12)) * np.exp(-((d - summit) / 40) ** 2))
            fr += light(EMERALD, 0.8 * np.exp(-a / 0.7) * np.exp(-((np.abs(d - summit) - 1500 * a) / 150) ** 2))
            fr += light(SILVER, 0.7 * np.exp(-a / 0.7) * np.exp(-((np.abs(d - summit) - 1100 * a) / 150) ** 2))

        # each awakening chord: a wave of sunrise out from the summit to both ends, rose at the front, gold behind
        for k, t0 in enumerate(T_CHORDS + [T_DAY]):
            a = t - t0
            if 0 <= a < 3.5:
                front = reach * min(1.0, a / 1.6)
                dist = np.abs(d - summit)
                band = np.exp(-((dist - front) / 220) ** 2)
                behind = smoothstep(front + 40, front - 200, dist) * np.exp(-a / 1.6)
                g = 0.7 + 0.1 * k
                fr += light(ROSE, g * band) + light(SUN, g * 0.8 * behind)
                fr += light(WHITE, (0.4 + 0.15 * k) * np.exp(-a / 0.12) * np.exp(-(dist / 80) ** 2))

        # her greeting: each note lights her brighter, each phrase ends in a burst of gold out from her
        pb = pb0 + (pb1 - pb0) * smoothstep(T_CHORDS[1], T_DAY, t)
        a = recent(heil_on, t, 2.0)
        if a is not None:
            fr += light(SUN, 0.7 * np.exp(-a / 0.8) * np.exp(-((d - pb) / 160) ** 2))
        for te in heil_ends:
            a = t - te
            if 0 <= a < 3.0:
                fr += light(SUN, 0.95 * np.exp(-a / 1.2) * np.exp(-((np.abs(d - pb) - 1400 * (1 - np.exp(-a / 0.7))) / 260) ** 2))
                fr += light(GLINT, 0.6 * np.exp(-a / 0.8) * S['porch'])

        # the harps: every note a spark of gold or rose racing out from her to the ends of the house
        i1 = int(np.searchsorted(harp_t, t, side='right'))
        i0 = int(np.searchsorted(harp_t, t - 1.4, side='left'))
        for j in range(i0, i1):
            th, m = harps[j]
            a = t - th
            x = pb + side[j] * 1300 * a
            c = SUN if m % 2 else ROSE
            fr += light(c, 1.0 * np.exp(-a / 0.8) * np.exp(-((d - x) / 45) ** 2))
        # and the new sun's rays streaming out from her the whole time she sings
        if mid > 0:
            ray = np.clip(np.sin(2 * np.pi * (np.abs(d - pb) / 520 - 0.22 * t)), 0, 1) ** 4
            fr += light(SUN, 0.4 * mid * ray) + light(ROSE, 0.2 * mid * np.roll(ray, 40))

        # "leuchtender Tag!": every chord a band of sunrise racing end to end; her high G blazes the whole house
        for j, t0 in enumerate(swell):
            a = t - t0
            if 0 <= a < 1.8:
                c = SUNRISE(np.array([hue[j]]))[0]
                x = (a / 1.2) * L if j % 2 == 0 else L - (a / 1.2) * L
                fr += light(c, 1.0 * np.exp(-a / 1.3) * np.exp(-((d - x) / 380) ** 2))
        blaze = smoothstep(T_BLAZE, T_BLAZE + 1.5, t)
        if blaze > 0:
            fr += light(SUNRISE(np.clip(0.5 + 0.45 * np.sin(2 * np.pi * (d / 900 - 0.12 * t)), 0, 1)),
                        0.55 * blaze * (0.8 + 0.2 * np.sin(2 * np.pi * (d / 300 + 0.3 * t))))
            a = t - T_BLAZE
            if a < 2.5:
                fr += light(WHITE, 0.6 * np.exp(-a / 0.3))

        # the two of them
        fr = hero(fr, S, ps, 0.85)
        if wake > 0:
            fr = heroine(fr, S, pb, 0.9 * wake + 0.1 * blaze, T)
        out[f] = fr
    return np.clip(out, 0, 1)


def score(M, G):
    """Wagner's notes, orchestrated from the piano reduction, with her line from the vocal score on top."""
    order = np.argsort(G.pd)
    xs, ds = G.pos[order, 0], G.pd[order]
    x0, x1 = xs.min(), xs.max()

    def pan_at(dd):                         # path distance -> left/right across the facade, from the street
        x = np.interp(dd, ds, xs)
        return float(0.85 * (2 * (x - x0) / (x1 - x0) - 1))

    her = pan_at(at(G, 'Porch Front', BRUNN_AT))
    top = pan_at(at(G, 'Porch Front', 0.5))
    o = Orchestra(M, level=3.0)

    def role(t, d, m, v, h):
        if T_DAY - 0.01 <= t < T_SWELL and d < 0.4:      # the arpeggios rippling up: harps
            return [('harp', 0, 4, 0.75)]
        if T_DAY - 0.01 <= t < T_SWELL:                  # the held chords under her: strings, a horn
            return ([('violins', 0, -10, 0.45), ('flutes', 0, -16, 0.25)] if h == 0 and m >= 67 else
                    [('violas' if m >= 50 else 'cellos', 0, -8, 0.45)] + ([('horns', 0, -14, 0.3)] if 50 <= m < 67 else []))
        return None

    notes = [(t, d, m, v, h, tr) for t, d, m, v, h, part, tr in compose() if part != 'voice']
    o.tutti(notes, size=lambda t: 1.0 if t < T_DAY or t >= T_SWELL else 0.5, role=role, pan=lambda t, m: top * 0.5)
    for t, d, m in voice():                  # her greeting: a trumpet, doubled by violins
        o.play('trumpets', m, t, d, 104, her, 0.85)
        o.play('violins', m, t, d, 92, her, 0.4)

    # the staging: the dying fire, the kiss, the sunrise, the blaze
    o.fire(0.0, T_DAY + 3, level=lambda tt: 0.35 * (1 - smoothstep(T_KISS, T_DAY + 2, tt)), pan=top, crackle=5.0)
    o.hit('triangle', T_KISS, 96, gain=0.4, pan=top)
    o.play('glock', note('E6'), T_KISS + 0.05, 0.3, 80, top, 0.35)
    o.play('glock', note('B6'), T_KISS + 0.25, 0.3, 74, top, 0.3)
    for k, t0 in enumerate(T_CHORDS):
        o.hit('cymbal swell', t0 - 2.6, 70 + 12 * k, gain=0.3, pan=top)
    o.hit('crash', T_CHORDS[-1], 110, gain=0.45, pan=top)
    o.hit('gong', T_DAY, 80, gain=0.25, pan=top)
    o.hit('cymbal swell', T_BLAZE - 2.6, 100, gain=0.45, pan=top)
    o.hit('crash', T_BLAZE, 118, gain=0.55, pan=top)
    o.hit('timpani roll', T_SWELL, 90, pitch=-5, gain=0.4, pan=top)
    o.hit('timpani', T_BLAZE, 118, pitch=-5, gain=0.6, pan=top)
    # ride the effects: up for the kiss and the sunrise, right down under her greeting, up again for the blaze
    o.effects([(0.0, -4), (T_CHORDS[-1] + 1.0, 0), (T_DAY + 1.0, -14), (T_SWELL - 1.0, -14), (T_BLAZE - 2.0, -2),
               (D, -2)])
