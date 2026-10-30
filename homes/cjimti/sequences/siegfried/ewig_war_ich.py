"""Ewig war ich: the summit in the full sunrise, rose, gold and sky blue on every run, Siegfried emerald at Porch
Front 0.42 and Brünnhilde silver with gold glints at 0.55.

The music is Wagner's own: Act III, bars 1478-1491, 1528-1535 and 1616-1625 of Siegfried, as Solti's 1958 Vienna
Philharmonic recording takes them, from the Wagner Ring Dataset's piano reduction (pixelhome/ring.py). The peaceful
theme in E major (the melody Wagner later wove into the Siegfried Idyll) sings out on the violins over soft
strings, and she takes it up: "Ewig war ich, ewig bin ich, ewig in süß sehnender Wonne". Then her fear, rising to
"So berühre mich nicht, trübe mich nicht!" on horns and trombones over the full strings; and then she gives way:
"Oh, Siegfried! Dein war ich von je!", and he answers, "Warst du's von je, so sei es jetzt!". It is the most
tender scene of the act, so the staging adds almost nothing: a soft timpani roll and a cymbal swell lifting her
cry of fear, and otherwise the music alone.

Every note of the peaceful theme swells a whole run of the house, one after another round the roofline, slow and
broad: emerald and gold while the orchestra sings it, silver and gold once she does. Then her fear: she draws back
along the porch, her silver trembling, the sky dims, and every hard chord of it throws an indigo swell over the
sky, until at "trübe mich nicht!" the whole house shudders indigo and rose. She gives way: the runs swell sky blue
and silver, she comes back to him, and a bridge of light grows between them as they stand together in the
sunrise.

compose() holds every note; stage(), sky(), fire() and figure() are the rock and the sky, shared word for word by
Act III's scenes on a clock that runs on from scene to scene."""
import numpy as np
from pixelhome.fx import DT, hexc, light, smoothstep, nframes, Flicker, smooth_noise, colormap
from pixelhome.ring import Orchestra, accents, excerpt, tidy

CODE = 'SF29'
TITLE = 'Ewig war ich'
KIND = 'show'
DESCRIPTION = ("In the sunrise, Brünnhilde is afraid of losing herself, and pulls away. Siegfried's love answers "
               'her in slow, broad swells of colour round the house, until the two of them reach for each other.')
VOICEOVER = ('I was always yours, she says, but do not touch me. Leave me as I am. '
             'And he answers her with his love.')

K = 6                                       # this scene's place on Act III's shared clock: T = t + 80 K
EX = excerpt(__file__)                      # Act III, bars 1478-1491, 1528-1535, 1616-1625, Solti 1958
BAR = {int(m): t for m, t in EX['bars']}
D = EX['seconds'] + 0.5
SEG = [s['start'] for s in EX['segments']]
T_EWIG = BAR[1486]                          # "Ewig war ich": she sings the theme
T_FEAR = SEG[1]                             # her fear
FEARS = accents(EX['notes'], T_FEAR, SEG[2], 60, 3, 0.8)
T_CRY = [a for a in FEARS if a >= BAR[1535] - 0.2][0]               # "trübe mich nicht!": her fear's climax
T_TOGETHER = SEG[2]                         # "Oh, Siegfried! Dein war ich von je!"

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
FATE_C = hexc('#4a2ab8')

DAWN = dict(storm=0.0, rock=0.35, fire=0.15, wide=0.0, dawn=0.75, sleeper=0.0)
SIEG_AT, BRUNN_AT, BRUNN_BACK = 0.42, 0.55, 0.68
RUNS = ['Left', 'Right', 'Porch Front', 'Side', 'Porch Left', 'Porch Right']


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


def compose():
    """Every note of the excerpt, tagged: (time, seconds, midi, velocity, hand, part, trem). 'theme' is the top of
    the right hand's long notes in the peaceful theme and in the last section; 'fear' the middle section; the rest
    'bed'."""
    N, tops = [], {}
    notes = tidy(EX['notes'])
    for n in notes:
        if n[4] == 0 and n[1] >= 0.25 and not T_FEAR <= n[0] < T_TOGETHER:
            k = round(n[0], 2)
            if k not in tops or n[2] > tops[k][2]:
                tops[k] = n
    top = {id(n) for n in tops.values()}
    for n in notes:
        t, d, m, v, h, tr = n
        part = 'theme' if id(n) in top else 'fear' if T_FEAR <= t < T_TOGETHER else 'bed'
        N.append((t, d, m, v, h, part, tr))
    return N


def swells():
    """The theme's notes as swells: (start, seconds, run, colour), one run after another round the house."""
    out = []
    for t, d, m, v, h, part, tr in compose():
        if part == 'theme':
            c = ((EMERALD if len(out) % 2 == 0 else SUN) if t < T_EWIG else
                 (SILVER if len(out) % 2 == 0 else GLINT) if t < T_FEAR else
                 (SKYBLUE if len(out) % 2 == 0 else SILVER))
            out.append((t, d, RUNS[len(out) % len(RUNS)], c))
    return out


def render(G, seed=29):
    F = nframes(D)
    out = np.zeros((F, G.N, 3))
    S = stage(G)
    d = S['d']
    sw = swells()
    fears = np.array(FEARS)
    shake = Flicker(np.random.default_rng(seed), G.N, 3.0, 6.0)
    ps = at(G, 'Porch Front', SIEG_AT)
    pb_home, pb_back = at(G, 'Porch Front', BRUNN_AT), at(G, 'Porch Front', BRUNN_BACK)
    runs = {r: (G.seg_of == r) for r in RUNS}

    def recent(ts, t, span):
        i = int(np.searchsorted(ts, t, side='right')) - 1
        return (t - ts[i]) if i >= 0 and t - ts[i] < span else None

    for f in range(F):
        t = f * DT
        T = t + 80 * K
        fear = smoothstep(T_FEAR - 0.5, T_FEAR + 1.5, t) * (1 - smoothstep(T_TOGETHER, T_TOGETHER + 4, t))
        mid = smoothstep(0.0, 2.0, t) * (1 - smoothstep(D - 6, D - 1, t))
        lv = dict(DAWN)
        lv['dawn'] = DAWN['dawn'] * (1 - 0.55 * mid - 0.25 * fear)
        fr = sky(S, T, lv)

        # every note of the theme: a whole run swells in its colour, slow and broad
        for t0, dur, run, c in sw:
            a = t - t0
            if -0.4 <= a < dur + 6.0:
                g = smoothstep(-0.4, 0.5, a) * np.exp(-max(a - dur * 0.6, 0) / 2.2)
                fr += light(c, 0.95 * g * runs[run] * (0.85 + 0.15 * np.sin(2 * np.pi * (d / 300 - 0.2 * t))))

        # her fear: indigo swells over the sky on every hard chord, the house trembling; her cry shudders it all
        a = recent(fears, t, 3.0)
        if a is not None:
            fr += light(FATE_C, 1.0 * np.exp(-a / 1.6) * smoothstep(0, 0.2, a) * S['sky'])
            fr += light(ROSE, 0.45 * np.exp(-a / 0.5) * S['porch'])
        if fear > 0:
            fr = fr * (1 - 0.22 * fear * (0.5 + 0.5 * shake(T)))[:, None]
        if T_CRY <= t < T_CRY + 3.0:
            a = t - T_CRY
            fr += light(FATE_C, 0.8 * np.exp(-a / 0.9)) + light(ROSE, 0.6 * np.exp(-a / 0.3))

        # the two of them: she draws back and comes home; at the end a bridge of light grows between them
        back = smoothstep(T_FEAR, T_FEAR + 4, t) * (1 - smoothstep(T_TOGETHER, T_TOGETHER + 6, t))
        pb = pb_home + (pb_back - pb_home) * back
        tremble = 1 - 0.3 * fear * (0.5 + 0.5 * np.sin(2 * np.pi * 4.3 * t))
        bridge = smoothstep(T_TOGETHER + 2, T_TOGETHER + 8, t)
        lo, hi = min(ps, pb), max(ps, pb)
        span = (d > lo) & (d < hi)
        if bridge > 0:
            u = (d - lo) / max(hi - lo, 1)
            fr += light(EMERALD + (SILVER - EMERALD) * np.clip(u, 0, 1)[:, None], 0.8 * bridge * span)
        fr = hero(fr, S, ps, 0.85)
        fr = heroine(fr, S, pb, 0.9 * tremble, T)
        out[f] = fr
    return np.clip(out, 0, 1)


def score(M, G):
    """Wagner's notes, orchestrated from the piano reduction; the staging stays almost silent."""
    order = np.argsort(G.pd)
    xs, ds = G.pos[order, 0], G.pd[order]
    x0, x1 = xs.min(), xs.max()

    def pan_at(dd):                         # path distance -> left/right across the facade, from the street
        x = np.interp(dd, ds, xs)
        return float(0.85 * (2 * (x - x0) / (x1 - x0) - 1))

    her = pan_at(at(G, 'Porch Front', BRUNN_AT))
    him = pan_at(at(G, 'Porch Front', SIEG_AT))
    o = Orchestra(M, level=4.5)

    def role(t, d, m, v, h, theme=set(round(e[0], 3) for e in compose() if e[5] == 'theme')):
        if round(t, 3) in theme and h == 0 and d >= 0.25 and not T_FEAR <= t < T_TOGETHER:
            parts = [('violins', 0, 4, 0.75)]           # the peaceful theme: violins, a flute above at the end
            if t >= T_TOGETHER:
                parts.append(('flutes', 0, -10, 0.35))
            return parts
        if T_FEAR <= t < T_TOGETHER:                     # her fear: horns and trombones on the chords
            if h == 1 and m >= 48 and d >= 0.25:
                return [('horns', 0, 0, 0.65), ('trombones', 0, -10, 0.4)]
            return None
        if h == 0:                                        # the soft strings under the theme
            return [('violas' if m < 64 else 'violins', 0, -12, 0.4)]
        return [('cellos', 0, -6, 0.5)] + ([('basses', 0, -12, 0.35)] if m < 43 else [])

    notes = [(t, d, m, v, h, tr) for t, d, m, v, h, part, tr in compose()]
    o.tutti(notes, size=lambda t: 1.0 if T_FEAR <= t < T_TOGETHER else 0.45, role=role,
            pan=lambda t, m: him * 0.5 if t < T_EWIG else her * 0.5)
    # the staging: almost nothing; only her cry of fear is lifted
    o.hit('timpani roll', T_CRY - 3.0, 80, pitch=-5, gain=0.35, pan=her)
    o.hit('cymbal swell', T_CRY - 2.6, 90, gain=0.35, pan=her)
    o.hit('timpani', T_CRY, 110, pitch=-5, gain=0.45, pan=her)
    o.effects([(0.0, -6), (T_CRY - 4, -2), (T_CRY + 2, -2), (T_TOGETHER, -10), (D, -10)])
