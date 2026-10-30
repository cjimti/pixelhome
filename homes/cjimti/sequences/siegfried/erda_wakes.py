"""Erda Wakes: a wild place at the foot of Brünnhilde's rock, at night, in a storm. The porch is the rock, its
summit the middle of Porch Front, where the magic fire still burns low far above; the wings and Side are the
storm sky, slate blue clouds rolling, rain, and lightning that cracks a whole run white at a time.

The music is Wagner's own: the climax of the Act III prelude (bars 40 to 57), the Wanderer's call "Wache, Wala!"
(bars 72 to 83) and the great descent as Erda wakes (bars 118 to 127), as Solti's 1958 Vienna Philharmonic
recording takes them. The notes come from the Wagner Ring Dataset's piano reduction (pixelhome/ring.py): the
galloping figure on the violins, the Wanderer's chords in the left hand on horns, trombones and trumpets, the bass
on cellos, basses and tuba; when Erda rises, her soft chords on clarinets and bassoons over the cellos' tremolo.
Like a staged production it adds the storm: wind and rain all through, a thunderclap with every bolt (near ones
crack at once, far ones rumble late), the Wanderer's three spear strikes on the rock as booms with ringing
steel and a crack of thunder, and a deep gong and a groan of the earth as Erda comes up. The storm leads through
the prelude and backs well off under Erda's chords, so they are heard.

The prelude gallops and lightning cracks a run white on its hammering chords; the Wanderer's chords blaze out
on the brass, every one a wave of deep blue rolling out over the house, as he strides in from the free end of
Right to the front of Left. "Wache, Wala!": three times he strikes the ground with his spear, each strike a
blue-white flash and a shock running out along the ground, and twice more the earth shudders at "herauf!". On
the great descending octaves the ground at the middle of Left trembles brown, and Erda rises out of it, moss
green over dark earth, swelling up and out over Left and the Side while the storm drops; every soft chord of
hers breathes her green wider. At the end the storm gathers itself again round the two of them.

compose() tags every note of the excerpt; stage(), sky(), figure() and fire() are the rock and the sky, shared
word for word by Act III's scenes on a clock that runs on from scene to scene."""
import numpy as np
from pixelhome.fx import DT, hexc, light, smoothstep, nframes, Flicker, smooth_noise, colormap
from pixelhome.ring import Orchestra, accents, excerpt, tidy

CODE = 'SF23'
TITLE = 'Erda Wakes'
KIND = 'show'
DESCRIPTION = ('A storm at the foot of the fire-ringed rock. The Wanderer strikes the ground three times with his '
               'spear, and Erda, the earth mother, rises out of the ground in a swell of green.')
VOICEOVER = ('A storm at the foot of the mountain. The Wanderer strikes the earth with his spear, and calls up '
             'the oldest power in the world.')

K = 0                                       # this scene's place on Act III's shared clock: T = t + 80 K
EX = excerpt(__file__)                      # Act III, bars 40-58, 72-84 and 118-128, Solti 1958
BAR = {int(m): t for m, t in EX['bars']}
NOTES = tidy(EX['notes'])
D = EX['seconds']
T_PRE = BAR[58]                             # the prelude's climax gives way to the call
T_IN = 4.0                                  # he strides in through the prelude
T_STOP = 26.0
T_STRIKE = [BAR[75], BAR[76], BAR[77]]      # "Wache, Wala! Wala! Erwach'!": three strikes
T_HERAUF = [BAR[82], BAR[83]]               # "herauf, herauf!": the earth shudders
T_WAKE = BAR[118]                           # "Wache, erwache": the great descent
T_RISE = BAR[120]                           # Erda rises
T_BACK = BAR[126]                           # the storm gathers again
WAVES = accents([n for n in EX['notes'] if n[1] >= 0.6], 0, T_WAKE + 0.1, vmin=110, n=3, space=0.5)
GUSTS = accents([n for n in EX['notes'] if n[1] >= 0.6], 0, T_PRE, vmin=100, n=2, space=0.8)
BREATHS = accents([n for n in EX['notes'] if n[1] >= 0.6], T_RISE + 1, D, vmin=1, n=2, space=1.5)

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

START = dict(storm=0.6, rock=0.3, fire=0.5, wide=0.0, dawn=0.0, sleeper=0.0)
END = dict(storm=0.6, rock=0.3, fire=0.5, wide=0.0, dawn=0.0, sleeper=0.0)      # where SF24 picks it up
WAND_AT = ('Left', 0.8)                     # the Wanderer's place at the end
ERDA_AT = ('Left', 0.35)                    # where Erda rises


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




def compose():
    """Every note of the excerpt, tagged (time, seconds, midi, velocity, part, tremolo): until the great descent the
    right hand is the gallop ('gallop'), the left hand's long notes the Wanderer's chords ('wanderer'), its others
    the bass ('bass'); from it on the left hand is Erda ('erda'), the right hand the earth's shimmer ('earth')."""
    N = []
    for t, d, m, v, h, trem in NOTES:
        if t >= T_WAKE - 0.01:
            part = 'erda' if h == 1 else 'earth'
        elif h == 0:
            part = 'gallop'
        elif d >= 0.6 and m >= 48:
            part = 'wanderer'
        else:
            part = 'bass'
        N.append((t, d, m, v, part, trem))
    return sorted(N, key=lambda e: e[0])


def bolts():
    """Lightning: [(time, run, strength, near)], on the prelude's hammering chords, the call's accents, and far off
    as the storm gathers again."""
    rng = np.random.default_rng(23)
    runs = ['Side', 'Left', 'Right', 'Left', 'Right', 'Side']
    pre = [(t, 1.0) for t in accents(EX['notes'], 0, T_PRE - 0.5, vmin=110, n=3, space=1.8)]
    call = [(t, 0.75) for t in accents(EX['notes'], T_PRE, T_WAKE - 0.5, vmin=90, n=3, space=2.5)
            if all(abs(t - s) > 1.0 for s in T_STRIKE)]
    late = [(T_WAKE + 0.02, 0.9), (T_BACK + 0.6, 0.35), (BAR[127] + 0.8, 0.5), (D - 1.6, 0.6)]
    out = []
    for i, (t, near) in enumerate(pre + call + late):
        out.append((float(t), runs[i % len(runs)], float(rng.uniform(0.8, 1.0)) * (0.55 + 0.45 * near), near))
    return out


def storm_level(t):
    """How hard the storm blows: full through the prelude, easing under the call, dropping while Erda rises, then
    gathering again for SF24."""
    return np.asarray(1.0 - 0.15 * smoothstep(T_PRE - 2, T_PRE + 2, t) - 0.5 * smoothstep(T_RISE, T_RISE + 6, t)
                      + 0.65 * smoothstep(T_BACK - 2, D - 1, t))


def walk(G, t):
    """Where the Wanderer is at time t."""
    a, b = G.pd.max() + 30, at(G, *WAND_AT)
    return a + (b - a) * smoothstep(T_IN, T_STOP, t)


def render(G, seed=23):
    F = nframes(D)
    out = np.zeros((F, G.N, 3))
    S = stage(G)
    d = S['d']
    L = d.max()
    p_erda = at(G, *ERDA_AT)
    p_wand = at(G, *WAND_AT)
    B = bolts()
    earth = [e for e in compose() if e[4] == 'erda' and e[0] < T_RISE]

    for f in range(F):
        t = f * DT
        T = t + 80 * K
        lv = dict(START)
        lv['storm'] = START['storm'] * float(np.clip(0.5 + 0.5 * storm_level(t), 0.5, 1.0))
        fr = sky(S, T, lv)

        # lightning: a whole run cracks white
        for tb, run, s, near in B:
            a = t - tb
            if 0 <= a < 1.2:
                env = min(1.0, np.exp(-a / 0.1) + 0.8 * np.exp(-((a - 0.16) / 0.05) ** 2))
                fr += light(BOLT, s * env * (G.seg_of == run) * (0.5 + 0.5 * S['jag']))
                fr += light(CLOUD, 0.6 * np.exp(-a / 0.4) * (G.seg_of == run))
                fr += light(STORM, 0.35 * env * S['sky'])

        # the gallop's hammering chords: a gust of bright cloud racing along the sky, Side to Right and back
        for k, t0 in enumerate(GUSTS):
            a = t - t0
            if 0 <= a < 1.6:
                x = (1100 * a) if k % 2 == 0 else (L - 1100 * a)
                fr += light(CLOUD, 0.9 * storm_level(t) * np.exp(-a / 0.7) * np.exp(-((d - x) / 120) ** 2) * S['sky'])
                fr += light(RAIN, 0.4 * np.exp(-a / 0.5) * np.exp(-((d - x) / 60) ** 2) * S['sky'])

        # the Wanderer's chords: a wave of deep blue rolling out from him over the house
        for t0 in WAVES:
            a = t - t0
            if 0 <= a < 2.5:
                p = walk(G, t0)
                r = 1300 * (1 - np.exp(-a / 0.8))
                fr += light(WOTAN, 1.0 * np.exp(-a / 1.1) * np.exp(-((np.abs(d - p) - r) / 200) ** 2))

        # the great descent: the ground at the middle of Left trembles brown with every octave
        for t0, dur, m, v, part, trem in earth:
            a = t - t0
            if 0 <= a < 1.0:
                fr += light(EARTH, 1.4 * np.exp(-a / 0.35) * np.exp(-((d - p_erda) / 90) ** 2))
                fr += light(MOSS, 0.25 * np.exp(-a / 0.25) * np.exp(-((d - p_erda) / 40) ** 2))

        # Erda rises out of the earth: dark earth first, then moss green swelling over Left and the Side
        if t >= T_RISE - 1:
            g = smoothstep(T_RISE - 1, T_RISE + 4, t)
            width = 60 + 260 * smoothstep(T_RISE, T_RISE + 12, t)
            breath = 0.0
            for t0 in BREATHS:
                a = t - t0
                if 0 <= a < 4.0:
                    breath = max(breath, np.exp(-a / 1.6) * smoothstep(0, 0.3, a))
            w = width * (1 + 0.5 * breath)
            fr += light(EARTH, 0.7 * g * np.exp(-((d - p_erda) / (w * 1.4)) ** 2))
            fr += light(MOSS, (0.75 + 0.3 * breath) * g * np.exp(-((d - p_erda) / w) ** 2))
            fr = figure(fr, S, p_erda, ERDA_HI, (0.55 + 0.35 * breath) * g, w=20)

        # the Wanderer, his three spear strikes on the ground, and the earth shuddering at "herauf!"
        p = walk(G, t)
        if t >= T_IN - 0.5:
            fr = figure(fr, S, p, WOTAN, 0.85 * smoothstep(T_IN - 0.5, T_IN + 0.5, t))
            fr += light(SPEAR, 0.6 * np.exp(-((d - p + 14) / 6) ** 2) * smoothstep(T_IN, T_IN + 1, t))
        for k, t0 in enumerate(T_STRIKE + T_HERAUF):
            a = t - t0
            big = 1.0 if k < 3 else 0.6
            if 0 <= a < 2.0:
                fr += light(BOLT, big * min(1.0, 1.2 * np.exp(-a / 0.08)) * np.exp(-((d - p_wand) / 50) ** 2))
                fr += light(SPEAR if k < 3 else EARTH, (1.0 if k < 3 else 1.3) * np.exp(-a / 0.6)
                            * np.exp(-((np.abs(d - p_wand) - 1300 * a) / 110) ** 2))
                fr += light(WOTAN, 0.7 * big * np.exp(-a / 0.3))
        out[f] = fr
    return np.clip(out, 0, 1)


def score(M, G):
    """Wagner's notes, orchestrated from the piano reduction, with the storm, the strikes and the earth."""
    order = np.argsort(G.pd)
    xs, ds = G.pos[order, 0], G.pd[order]
    x0, x1 = xs.min(), xs.max()

    def pan_at(dd):                         # path distance -> left/right across the facade, from the street
        x = np.interp(dd, ds, xs)
        return float(0.85 * (2 * (x - x0) / (x1 - x0) - 1))

    erda_p = pan_at(at(G, *ERDA_AT))
    wand_p = pan_at(at(G, *WAND_AT))
    o = Orchestra(M, level=1.8)

    def role(t, d, m, v, h):
        if t >= T_RISE - 0.01 and h == 1 and d >= 0.3:          # Erda: her chords on clarinets and bassoons
            if m >= 52:
                return [('clarinets', 0, 26, 0.8), ('bassoons', -12, 20, 0.5)]
            return [('cellos', 0, 22, 0.6), ('basses', -12 if m >= 40 else 0, 16, 0.5)]
        if t >= T_RISE - 0.01 and h == 0:                       # her shimmer, high and soft
            return [('flutes', 0, 20, 0.4), ('harp', 0, 24, 0.4)]
        return None

    def pan(t, m):
        if t >= T_WAKE:
            return erda_p * 0.7
        return pan_at(walk(G, t)) * 0.5 if m >= 48 else 0.0

    o.tutti(NOTES, size=lambda t: 1.0 if t < T_PRE else 0.8 if t < T_RISE else 0.5, role=role, pan=pan)
    # the storm leads through the prelude and the strikes, backs off under the call, and falls well away under
    # Erda's soft chords until it gathers again at the end
    o.effects([(0.0, 0), (T_PRE - 1, 0), (T_PRE + 1.5, -6), (T_STRIKE[0] - 0.3, -2), (T_STRIKE[2] + 2.5, -2),
               (T_STRIKE[2] + 4.5, -7), (T_WAKE - 0.5, -7), (T_WAKE, -2), (T_RISE + 2, -4), (T_RISE + 6, -11),
               (T_BACK - 1, -11), (D - 2, -3)])

    # the storm: wind and rain all through, thunder with every bolt
    o.wind(0.0, D, level=lambda tt: 0.35 + 0.45 * storm_level(tt), pan=0.0)
    o.wind(0.0, D, level=lambda tt: 0.25 * storm_level(tt), pan=-0.6, seed=19)
    for tb, run, s, near in bolts():
        o.thunder(tb, near=near, pan=pan_at(at(G, run, 0.5)), gain=0.8 * s, seed=int(tb * 100) + 1)
    # the spear on the rock: a great blow, ringing steel and a crack
    for t0 in T_STRIKE:
        o.boom(t0, wand_p, 1.0)
        o.hit('metal', t0, 120, gain=0.5, pan=wand_p)
        o.thunder(t0 + 0.02, near=0.85, pan=wand_p, gain=0.6, seed=int(t0 * 100))
    for t0 in T_HERAUF:                     # the earth shudders
        o.hit('timpani', t0, 116, pitch=-7, gain=0.7, pan=erda_p)
        o.hit('bass drum', t0, 118, gain=0.6, pan=erda_p)
    o.hit('crash', T_WAKE, 118, gain=0.5)
    # Erda comes up: a deep gong, the earth groaning
    o.hit('timpani roll', T_RISE - 1.5, 96, pitch=-6, gain=0.6, pan=erda_p)
    o.hit('gong', T_RISE, 112, gain=0.7, pan=erda_p)
    o.hit('gong scrape', T_RISE + 0.5, 100, gain=0.5, pan=erda_p)
    o.thunder(T_RISE - 0.3, near=0.1, pan=erda_p, gain=0.9, seed=77)
