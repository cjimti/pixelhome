"""Das ist kein Mann!: the summit of Brünnhilde's rock. The fire burns low round the porch, the sky is calm and
dark, and at the summit, the middle of Porch Front, a silver glow sleeps: an armed figure under a shield.
Siegfried, emerald with a white-hot head, stands just short of it at Porch Front 0.35.

The music is Wagner's own: Act III, bars 885-889, 894-899 and 921-935 of Siegfried, as Solti's 1958 Vienna
Philharmonic recording takes them, from the Wagner Ring Dataset's piano reduction (pixelhome/ring.py). He finds the
armour ("Helle Waffen? Heb' ich sie auf?") and lifts the shield; he loosens the helmet ("Leichter würd' ihm") and
her hair spills out ("Ach! Wie schön!"); he cuts the rings of the armour in near silence; the orchestra bursts out
as the breastplate falls, "Das ist kein Mann!", and fear takes him ("Brennender Zauber zückt mir in's Herz ...
mir schwankt und schwindelt der Sinn"). The sleep music is on the woodwinds over soft strings, the cutting on the
strings alone, the outburst on the full orchestra, and the fear's heavy chords on horns, trombones and tuba, as
Wagner's tubas would play them. A production's sounds are added where the staging needs them: the low crackle of
the fire round the rock, the scrape of the shield, a glint as the helmet comes away, each stroke of Nothung
through the steel rings, a crash as the breastplate falls, and timpani under the fear; they are ridden down under
the sleep music and her hair, and lead through the cutting.

The magic sleep shimmers, and every chord of it rolls a violet ripple out from the sleeper over the whole house.
He lifts the shield: a silver flash, and silver glints race to both ends of the roofline; "in Waffen ein Mann?",
the steel flares again. He lifts the helmet, and her hair spills out in a burst of gold that swells again on "Ach!
Wie schön!". He cuts the armour with Nothung, two strokes, each a white slash running out both ways along the roof.
The orchestra breaks out: the house flashes rose and the strings' racing scales throw rose sparks racing out from
her, and on "Das ist kein Mann!" it flashes again. Fear: on every heavy chord an indigo wave rolls out from the
sleeper, the whole house trembles, and his emerald shrinks and flickers like a candle; but he is drawn to her, and
inch by inch he comes in beside her.

compose() holds every note; stage(), sky(), fire() and figure() are the rock and the sky, shared word for word by
Act III's scenes on a clock that runs on from scene to scene."""
import numpy as np
from pixelhome.audio import whoosh
from pixelhome.fx import DT, hexc, light, smoothstep, nframes, Flicker, smooth_noise, colormap
from pixelhome.ring import Orchestra, accents, excerpt, tidy

CODE = 'SF27'
TITLE = 'Das ist kein Mann!'
KIND = 'show'
DESCRIPTION = ('At the top of the fire-ringed rock Siegfried finds a sleeper in armour. He lifts the shield and '
               'helmet, cuts the armour away, and finds a woman, and for the first time in his life he is afraid.')
VOICEOVER = ('At the top of the mountain, a sleeper in armour. He lifts the helmet, and finds a woman. '
             'And for the first time in his life, Siegfried is afraid.')

K = 4                                       # this scene's place on Act III's shared clock: T = t + 80 K
EX = excerpt(__file__)                      # Act III, bars 885-889, 894-899, 921-935, Solti 1958
BAR = {int(m): t for m, t in EX['bars']}
D = EX['seconds']
SUNG = {s[3].split()[0].strip('!–,'): s[0] for s in EX['singing']}
T_SHIELD = BAR[886]                         # he lifts the shield
T_MAN = SUNG['Ha']                          # "Ha! - in Waffen ein Mann?"
T_HELMET = accents(EX['notes'], BAR[896] - 3, BAR[896], 70, 3)[0]   # the helmet comes away
T_SCHON = SUNG['Ach']                       # "Ach! Wie schön!"
T_SLEEP_END = BAR[921]                      # the sleep music ends; the cutting begins
T_CUT = [t for t, d, m, v, h in EX['notes'] if BAR[921] + 2 < t < BAR[924] and h == 1 and d > 2]   # two strokes
T_SHOCK = BAR[924]                          # the breastplate falls: the orchestra breaks out
T_WORDS = SUNG['Das']                       # "Das ist kein Mann!"
FATE = accents(EX['notes'], T_WORDS, D, 70, 3, 1.2)                 # the fear's heavy chords
SLEEPS = accents(EX['notes'], 0, T_SLEEP_END, 40, 2, 1.8)           # the sleep music's chords
T_DRAWN = (FATE[1] if len(FATE) > 1 else T_WORDS + 8, D - 1.0)     # drawn to her, he comes in beside her

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
STEEL = hexc('#e8f8ff')
HAIR = hexc('#ffd060')
VIOLET = hexc('#7a6aff')
ROSE = hexc('#ff4080')
FATE_C = hexc('#4a2ab8')
WHITE_STEEL = hexc('#ffffff')

SUMMIT = dict(storm=0.25, rock=0.35, fire=0.4, wide=0.0, dawn=0.0, sleeper=0.7)
SIEG_FROM, SIEG_TO = 0.35, 0.42             # his place on Porch Front, before and after


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


def compose():
    """Every note of the excerpt, tagged: (time, seconds, midi, velocity, hand, part, trem). 'sleep' before the
    cutting, 'cut' while he cuts, 'burst' for the outburst, 'fear' after his words."""
    N = []
    for t, d, m, v, h, tr in tidy(EX['notes']):
        part = ('sleep' if t < T_SLEEP_END else 'cut' if t < T_SHOCK - 0.01 else 'burst' if t < T_WORDS - 0.01
                else 'fear')
        N.append((t, d, m, v, h, part, tr))
    return N


def fear_at(t):
    return smoothstep(T_SHOCK, T_SHOCK + 1.0, t) * (1 - 0.3 * smoothstep(T_DRAWN[0], T_DRAWN[1], t))


def render(G, seed=27):
    rng = np.random.default_rng(seed)
    F = nframes(D)
    out = np.zeros((F, G.N, 3))
    S = stage(G)
    d, summit = S['d'], S['summit']
    L = d.max()
    N = compose()
    sleeps = np.array(SLEEPS)
    fates = np.array(FATE)
    runs = np.array(sorted({e[0] for e in N if e[5] == 'burst' and e[4] == 0}))
    glint_at = rng.uniform(0, L, 40)
    glint_t = T_SHIELD + rng.uniform(0, 1.5, 40)
    shake = Flicker(rng, G.N, 4.0, 7.0)
    p0, p1 = at(G, 'Porch Front', SIEG_FROM), at(G, 'Porch Front', SIEG_TO)

    def recent(ts, t, span):
        i = int(np.searchsorted(ts, t, side='right')) - 1
        return (t - ts[i]) if i >= 0 and t - ts[i] < span else None

    for f in range(F):
        t = f * DT
        T = t + 80 * K
        fear = fear_at(t)
        lv = dict(SUMMIT)
        lv['fire'] = SUMMIT['fire'] * (1 + 0.5 * fear)
        lv['sleeper'] = SUMMIT['sleeper'] + 0.25 * smoothstep(T_HELMET, T_HELMET + 2, t)
        fr = sky(S, T, lv)

        # the magic sleep: each chord a violet ripple out from the sleeper over the whole house
        a = recent(sleeps, t, 3.0)
        if a is not None and t < T_SLEEP_END + 1:
            r = 1400 * (1 - np.exp(-a / 0.9))
            fr += light(VIOLET, 0.95 * np.exp(-a / 1.3) * np.exp(-((np.abs(d - summit) - r) / 320) ** 2))
            fr += light(VIOLET, 0.5 * np.exp(-a / 0.6) * np.exp(-((d - summit) / 200) ** 2))
        dream = smoothstep(0, 2, t) * (1 - smoothstep(T_SLEEP_END - 2, T_SLEEP_END + 2, t))
        fr += light(VIOLET, 0.45 * dream * S['sky'] * (0.75 + 0.25 * np.sin(2 * np.pi * (d / 600 - 0.15 * t))))

        # the shield lifted: a silver flash, silver racing to both ends, and glints scattered over the house
        if T_SHIELD <= t < T_SHIELD + 3.0:
            a = t - T_SHIELD
            fr += light(STEEL, min(1.0, 1.1 * np.exp(-a / 0.15)) * np.exp(-((d - summit) / 70) ** 2))
            fr += light(STEEL, 0.95 * np.exp(-a / 0.8) * np.exp(-((np.abs(d - summit) - 1600 * a) / 90) ** 2))
            for p, tg in zip(glint_at, glint_t):
                g = t - tg
                if 0 <= g < 0.5:
                    fr += light(STEEL, 0.9 * np.exp(-g / 0.12) * np.exp(-((d - p) / 8) ** 2))
        if T_MAN <= t < T_MAN + 2.5:            # "in Waffen ein Mann?": the steel flares on the porch
            a = t - T_MAN
            fr += light(STEEL, 0.7 * np.exp(-a / 0.6) * S['porch'] * smoothstep(0, 0.1, a))

        # the helmet: her hair spills out in a burst of gold; "Ach! Wie schön!" swells it again
        for t0, k in ((T_HELMET, 1.0), (T_SCHON, 0.8)):
            if t0 <= t < t0 + 6:
                a = t - t0
                w = 40 + 1400 * (1 - np.exp(-a / 1.2))
                fr += light(HAIR, k * np.exp(-a / 2.2) * np.exp(-((d - summit) / w) ** 2))

        # the cutting: in the hush a cold steel glow gathers at the summit and creeps along the porch
        if T_SLEEP_END <= t < T_SHOCK:
            g = smoothstep(T_SLEEP_END, T_SHOCK, t)
            fr += light(STEEL, (0.25 + 0.45 * g) * np.exp(-((d - summit) / (60 + 500 * g)) ** 2)
                        * (0.8 + 0.2 * np.sin(2 * np.pi * 1.5 * t)))

        # Nothung cuts the armour: two white slashes out both ways, the porch flaring with each
        for t0 in T_CUT:
            a = t - t0
            if 0 <= a < 1.5:
                fr += light(WHITE_STEEL, min(1.0, np.exp(-a / 0.6)) * np.exp(-((np.abs(d - summit) - 2000 * a) / 150) ** 2))
                fr += light(STEEL, 0.75 * np.exp(-a / 0.15) * S['porch'] + 0.35 * np.exp(-a / 0.1))

        # the breastplate falls: the house flashes rose, the strings' scales throw rose sparks out from her
        for t0, k in ((T_SHOCK, 1.0), (T_WORDS, 0.8)):
            if t0 <= t < t0 + 2.0:
                a = t - t0
                fr += light(ROSE, 0.9 * k * np.exp(-a / 0.35))
                fr += light(HEAD, 0.5 * k * np.exp(-a / 0.1))
        if T_SHOCK <= t < T_WORDS + 1:
            a = recent(runs, t, 0.6)
            if a is not None:
                r = 300 + 1500 * (t - T_SHOCK) / (T_WORDS - T_SHOCK)
                fr += light(ROSE, 1.0 * np.exp(-a / 0.25) * np.exp(-((np.abs(d - summit) - r) / 110) ** 2))
                fr += light(ROSE, 0.25 * np.exp(-a / 0.2) * S['sky'])

        # fear: indigo waves of fate roll out from her, and the whole house trembles
        a = recent(fates, t, 3.0)
        if a is not None:
            r = 1400 * (1 - np.exp(-a / 1.0))
            fr += light(FATE_C, 1.0 * np.exp(-a / 1.4) * np.exp(-((np.abs(d - summit) - r) / 420) ** 2))
            fr += light(ROSE, 0.5 * np.exp(-a / 0.4) * np.exp(-((np.abs(d - summit) - r) / 120) ** 2))
        if fear > 0:
            fr = fr * (1 - 0.35 * fear * (0.5 + 0.5 * shake(T)))[:, None]
            fr += light(FATE_C, 0.35 * fear * S['sky'])

        # Siegfried: bright at first, shrinking and flickering in his fear, drawn in beside her all the same
        p = p0 + (p1 - p0) * smoothstep(*T_DRAWN, t)
        flick = 0.55 + 0.45 * np.sin(2 * np.pi * 5.3 * t) * np.sin(2 * np.pi * 1.7 * t)
        lvl = 0.85 * (1 - fear) + fear * 0.55 * flick
        w = 16 - 8 * fear
        fr = hero(fr, S, p, lvl, w)
        out[f] = fr
    return np.clip(out, 0, 1)


def score(M, G):
    """Wagner's notes, orchestrated from the piano reduction, with the staging's sounds ridden under the music."""
    order = np.argsort(G.pd)
    xs, ds = G.pos[order, 0], G.pd[order]
    x0, x1 = xs.min(), xs.max()

    def pan_at(dd):                         # path distance -> left/right across the facade, from the street
        x = np.interp(dd, ds, xs)
        return float(0.85 * (2 * (x - x0) / (x1 - x0) - 1))

    her = pan_at(at(G, 'Porch Front', 0.5))
    him = pan_at(at(G, 'Porch Front', SIEG_FROM))
    o = Orchestra(M, level=3.4)

    def role(t, d, m, v, h):
        if t < T_SLEEP_END:                 # the sleep: woodwinds over soft strings
            if h == 0:
                return ([('flutes', 0, -4, 0.55), ('oboes', -12, -12, 0.3)] if m >= 69 else
                        [('clarinets', 0, -4, 0.6)])
            return [('bassoons' if m >= 48 else 'cellos', 0, -6, 0.55)] + ([('basses', 0, -12, 0.35)] if m < 43 else [])
        if t < T_SHOCK - 0.01:              # the cutting: strings alone, hushed
            return [('violins' if m >= 60 else 'violas' if m >= 50 else 'cellos', 0, -4, 0.55)]
        if t >= T_WORDS - 0.01 and h == 1:  # fear: the heavy chords on horns, trombones, tuba
            if m < 43:
                return [('tuba', 0, -4, 0.6), ('basses', 0, -8, 0.4)]
            return [('horns', 0, 0, 0.7), ('trombones', 0, -8, 0.45)] if d >= 0.25 else [('cellos', 0, -6, 0.5)]
        return None

    notes = [(t, d, m, v, h, tr) for t, d, m, v, h, part, tr in compose()]
    o.tutti(notes, size=lambda t: 1.0 if t >= T_SHOCK else 0.4, role=role, pan=lambda t, m: her * 0.6)

    # the staging: the fire round the rock, the shield, the helmet, the cutting, the breastplate, the fear
    o.fire(0.0, D, level=lambda tt: 0.25 + 0.25 * smoothstep(T_SHOCK, T_SHOCK + 2, tt), pan=her, crackle=6.0)
    o.hit('scrape', T_SHIELD, 100, gain=0.55, pan=her)
    o.hit('metal', T_SHIELD + 0.05, 80, gain=0.25, pan=her)
    o.hit('triangle', T_SHIELD + 0.1, 90, gain=0.35, pan=her)
    o.hit('metal', T_HELMET, 70, gain=0.2, pan=her)
    o.hit('triangle', T_HELMET + 0.05, 80, gain=0.3, pan=her)
    for k, t0 in enumerate(T_CUT):           # Nothung through the steel rings
        M.add('fx', whoosh(0.45, 5000, 900, 0.7, seed=31 + k), t0 - 0.35, 0.8, him)
        o.clash(t0, her, 112, 0.8)
    o.hit('crash', T_SHOCK, 120, gain=0.6, pan=her)
    o.hit('timpani', T_SHOCK, 120, pitch=-4, gain=0.7, pan=her)
    o.hit('metal', T_SHOCK + 0.05, 100, gain=0.35, pan=her)   # the breastplate falls away
    for k, t0 in enumerate(FATE):
        o.hit('timpani roll', t0, 96, pitch=-5, gain=0.4, pan=her)
        o.hit('timpani', t0, 110, pitch=-6, gain=0.5, pan=her)
    o.hit('gong', FATE[0], 100, gain=0.35, pan=her)
    # ride the effects: down under the sleep music and her hair, up for the cutting and the outburst
    o.effects([(0.0, -9), (T_SHIELD - 0.5, -3), (T_SHIELD + 2.5, -9), (T_HELMET - 0.5, -5), (T_HELMET + 2.0, -12),
               (T_SLEEP_END, -12), (T_SLEEP_END + 1.5, 0), (T_SHOCK + 1.0, 0), (T_WORDS - 1.0, -8),
               (T_WORDS + 1.5, -5), (D, -5)])
