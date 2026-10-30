"""Das ist kein Mann!: the summit of Brünnhilde's rock. The fire burns low round the porch, the sky is calm and
dark, and at the summit, the middle of Porch Front, a silver glow sleeps: an armed figure under a shield.
Siegfried, emerald with a white-hot head, stands just short of it at Porch Front 0.35.

The magic sleep (Donington 16) shimmers in the woodwinds in E major, and every chord of it rolls a violet ripple
out from the sleeper over the whole house. He lifts the shield: a silver flash, and silver glints race to both
ends of the roofline. He lifts the helmet, and her hair spills out in a burst of gold. He cuts the armour with
Nothung, two strokes, each a white slash running out both ways along the roof. Then the brass cries out, "Das ist
kein Mann!": the house flashes rose, and for the first time in his life Siegfried is afraid. The power of fate
(84) sounds on the Wagner tubas, indigo waves roll out from the sleeper one after another, the whole house
trembles, and his emerald shrinks and flickers like a candle. Innocent sleep (30) quiets it: her silver breathes,
the violet sleep comes back, and he gathers himself, grows bright again and steps in beside her.

compose() holds every note; stage(), sky(), fire() and figure() are the rock and the sky, shared word for word by
Act III's scenes on a clock that runs on from scene to scene."""
import numpy as np
from pixelhome.audio import note
from pixelhome.fx import DT, hexc, light, smoothstep, nframes, keys, Flicker, smooth_noise, colormap
from pixelhome.leitmotifs import play

CODE = 'SF27'
TITLE = 'Das ist kein Mann!'
KIND = 'show'
DESCRIPTION = ('At the top of the fire-ringed rock Siegfried finds a sleeper in armour. He lifts the shield and '
               'helmet, cuts the armour away, and finds a woman, and for the first time in his life he is afraid.')
VOICEOVER = ('At the top of the mountain, a sleeper in armour. He lifts the helmet, and finds a woman. '
             'And for the first time in his life, Siegfried is afraid.')

K = 4                                       # this scene's place on Act III's shared clock: T = t + 80 K
T_SLEEP = [0.5, 58.0]                       # the magic sleep, shimmering
SBEAT = 0.8
T_SHIELD = 14.0                             # he lifts the shield
T_HELMET = 21.0                             # and the helmet: her hair
T_CUT = [28.0, 30.5]                        # Nothung cuts the armour
T_SHOCK = 35.0                              # "Das ist kein Mann!"
T_FATE = [37.0, 45.0]                       # the power of fate, Wagner tubas
FBEAT = 0.85
T_INNOCENT = 52.0                           # innocent sleep
T_STEP = (62.0, 72.0)                       # he gathers himself and steps in beside her
D = 80.0

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
    """Every note: (time, seconds, midi, velocity, part, k)."""
    N = []

    def add(t, d, m, v, part, k=None):
        N.append((float(t), float(d), note(m) if isinstance(m, str) else int(m), int(v), part, k))

    for k, t0 in enumerate(T_SLEEP):
        for t, m, v, d in play('sleep', t0, SBEAT, -4, 84 - 8 * k):
            add(t, d, m, v, 'sleep', k)
    for m in ('E1', 'B1', 'E2'):
        add(0.0, T_SHOCK, m, 60, 'bed')
    for j, m in enumerate(('E5', 'Ab5', 'B5', 'E6', 'Ab6', 'B6')):
        add(T_SHIELD + 0.07 * j, 1.2, m, 88 - 3 * j, 'shield')
    for j, m in enumerate(('E3', 'B3', 'E4', 'Ab4', 'B4', 'E5', 'Ab5', 'B5')):
        add(T_HELMET + 0.12 * j, 2.0, m, 80 + 2 * j, 'helmet')
    add(T_HELMET + 0.9, 3.0, 'E4', 82, 'hornhair')
    add(T_HELMET + 0.9, 3.0, 'B4', 78, 'hornhair')
    for t0 in T_CUT:
        add(t0, 0.3, 'C5', 118, 'cut')
    for m in ('C3', 'Eb3', 'Gb3', 'A3', 'C4', 'Eb4'):
        add(T_SHOCK, 1.6, m, 122, 'shock')
    for k, t0 in enumerate(T_FATE):
        for t, m, v, d in play('fate', t0, FBEAT, 0, 104 - 8 * k):
            add(t, d, m, v, 'fate', k)
    add(T_SHOCK + 1.0, T_INNOCENT - T_SHOCK - 1.0, 'D2', 92, 'trem')
    add(T_SHOCK + 1.0, T_INNOCENT - T_SHOCK - 1.0, 'A2', 88, 'trem')
    for t, m, v, d in play('innocent_sleep', T_INNOCENT, 0.9, 0, 82):
        add(t, d, m, v, 'innocent')
    for t, m, v, d in play('siegfried', T_STEP[0] + 4, 0.7, -12, 90):
        add(t, d, m, v, 'courage')
    for m in ('E2', 'B2', 'E3', 'Ab3'):
        add(T_STEP[1] - 2, D - T_STEP[1] + 2, m, 58, 'warm')
    return sorted(N, key=lambda e: e[0])


def render(G, seed=27):
    rng = np.random.default_rng(seed)
    F = nframes(D)
    out = np.zeros((F, G.N, 3))
    S = stage(G)
    d, summit = S['d'], S['summit']
    L = d.max()
    N = compose()
    sleeps = np.array(sorted({e[0] for e in N if e[4] == 'sleep'}))
    fates = np.array(sorted({e[0] for e in N if e[4] == 'fate'}))
    innocent = np.array(sorted({e[0] for e in N if e[4] == 'innocent'}))
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
        fear = smoothstep(T_SHOCK, T_SHOCK + 1.0, t) * (1 - smoothstep(T_INNOCENT, T_INNOCENT + 8, t))
        lv = dict(SUMMIT)
        lv['fire'] = SUMMIT['fire'] * (1 + 0.5 * fear)
        lv['sleeper'] = SUMMIT['sleeper'] + 0.25 * smoothstep(T_HELMET, T_HELMET + 2, t) * (1 - smoothstep(T_STEP[1], D, t))
        fr = sky(S, T, lv)

        # the magic sleep: each chord a violet ripple out from the sleeper over the whole house
        a = recent(sleeps, t, 3.0)
        if a is not None:
            r = 1400 * (1 - np.exp(-a / 0.9))
            fr += light(VIOLET, 0.95 * np.exp(-a / 1.3) * np.exp(-((np.abs(d - summit) - r) / 320) ** 2))
            fr += light(VIOLET, 0.5 * np.exp(-a / 0.6) * np.exp(-((d - summit) / 200) ** 2))
        dream = sum(smoothstep(t0, t0 + 2, t) * (1 - smoothstep(t0 + 14, t0 + 17, t)) for t0 in T_SLEEP)
        fr += light(VIOLET, 0.5 * dream * S['sky'] * (0.75 + 0.25 * np.sin(2 * np.pi * (d / 600 - 0.15 * t))))

        # the shield lifted: a silver flash, silver racing to both ends, and glints scattered over the house
        if T_SHIELD <= t < T_SHIELD + 3.0:
            a = t - T_SHIELD
            fr += light(STEEL, min(1.0, 1.1 * np.exp(-a / 0.15)) * np.exp(-((d - summit) / 70) ** 2))
            fr += light(STEEL, 0.95 * np.exp(-a / 0.8) * np.exp(-((np.abs(d - summit) - 1600 * a) / 90) ** 2))
            for p, tg in zip(glint_at, glint_t):
                g = t - tg
                if 0 <= g < 0.5:
                    fr += light(STEEL, 0.9 * np.exp(-g / 0.12) * np.exp(-((d - p) / 8) ** 2))

        # the helmet: her hair spills out in a burst of gold
        if T_HELMET <= t < T_HELMET + 6:
            a = t - T_HELMET
            w = 40 + 1400 * (1 - np.exp(-a / 1.2))
            fr += light(HAIR, 1.0 * np.exp(-a / 2.2) * np.exp(-((d - summit) / w) ** 2))

        # Nothung cuts the armour: two white slashes out both ways, the porch flaring with each
        for t0 in T_CUT:
            a = t - t0
            if 0 <= a < 1.5:
                fr += light(WHITE_STEEL, min(1.0, np.exp(-a / 0.6)) * np.exp(-((np.abs(d - summit) - 2000 * a) / 150) ** 2))
                fr += light(STEEL, 0.75 * np.exp(-a / 0.15) * S['porch'] + 0.35 * np.exp(-a / 0.1))

        # "Das ist kein Mann!": the house flashes rose
        if T_SHOCK <= t < T_SHOCK + 2.0:
            a = t - T_SHOCK
            fr += light(ROSE, 0.9 * np.exp(-a / 0.35))
            fr += light(HEAD, 0.5 * np.exp(-a / 0.1))

        # fear: indigo waves of fate roll out from her, and the whole house trembles
        a = recent(fates, t, 3.0)
        if a is not None:
            r = 1400 * (1 - np.exp(-a / 1.0))
            fr += light(FATE_C, 1.0 * np.exp(-a / 1.4) * np.exp(-((np.abs(d - summit) - r) / 420) ** 2))
            fr += light(ROSE, 0.5 * np.exp(-a / 0.4) * np.exp(-((np.abs(d - summit) - r) / 120) ** 2))
        if fear > 0:
            fr = fr * (1 - 0.35 * fear * (0.5 + 0.5 * shake(T)))[:, None]
            fr += light(FATE_C, 0.35 * fear * S['sky'])

        # innocent sleep: her silver breathes wide over the porch
        a = recent(innocent, t, 3.5)
        if a is not None:
            fr += light(SILVER, 0.6 * np.exp(-a / 1.4) * smoothstep(0, 0.2, a) * np.exp(-((d - summit) / 260) ** 2))

        # Siegfried: bright at first, shrinking and flickering in his fear, then himself again, stepping in
        p = p0 + (p1 - p0) * smoothstep(*T_STEP, t)
        flick = 0.55 + 0.45 * np.sin(2 * np.pi * 5.3 * t) * np.sin(2 * np.pi * 1.7 * t)
        lvl = 0.85 * (1 - fear) + fear * 0.55 * flick
        lvl = lvl * (1 - 0.06 * smoothstep(*T_STEP, t))
        w = 16 - 8 * fear
        fr = hero(fr, S, p, lvl, w)
        courage = smoothstep(T_STEP[0] + 4, T_STEP[0] + 5, t) * (1 - smoothstep(T_STEP[0] + 7, T_STEP[1], t))
        if courage > 0:
            fr += light(EMERALD, 0.85 * courage * np.exp(-((d - p) / 900) ** 2))
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

    for name, gain, rev in (('low', 0.28, 0.25), ('winds', 0.26, 0.38), ('brass', 0.28, 0.3), ('perc', 0.26, 0.3),
                            ('harp', 0.24, 0.4), ('strings', 0.24, 0.32), ('fx', 0.08, 0.3)):
        M.bus(name, gain=gain, reverb=rev)
    fl = M.sampler('Woodwinds/Flute/susvib/*.wav', tune=-12)
    clar = M.sampler('Woodwinds/Clarinet/susLong/*.wav', tune=-12)
    ob = M.sampler('Woodwinds/Oboe/Sus/*.wav', tune=-12)
    harp = M.sampler('Strings/Harp/*.wav')
    glock = M.sampler('Percussion/Glock/*.wav')
    horn = M.sampler('Brass/F Horn/sus/*.wav', tune=-12)
    tpt = M.sampler('Brass/Trumpet/stac/*.wav', tune=-12)
    tbn = M.sampler('Brass/Tenor Trombone/sus/*.wav', tune=-12)
    tuba = M.sampler('Brass/Tuba/sus/*.wav', tune=-12)
    cb = M.sampler('Strings/Solo Contrabass/SusNV/*.wav', tune=-12)
    ctrem = M.sampler('Strings/Cello Section/trem/*.wav', tune=-12)
    vc = M.sampler('Strings/Cello Section/susvib/*.wav', tune=-12)
    vn = M.sampler('Strings/Violin Section/susVib/*.wav', tune=-12)
    timp = M.hits('Percussion/Timpani/Timpani1_Hit*.wav')
    crash = M.hits('Percussion/cymbal-crash1_f*.wav')
    tri = M.hits('Percussion/Triangle3-Hit*.wav')

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

    her = pan_at(at(G, 'Porch Front', 0.5))
    him = pan_at(at(G, 'Porch Front', SIEG_FROM))
    for t, d, m, v, part, k in compose():
        if part == 'sleep':
            s = fl if m >= note('Ab4') else clar if m >= note('E3') else vc
            if d > 1.0:
                hold('winds', s, m, t, t + d, v, her, rise=0.4, fall=1.2, gain=0.7)
            else:
                M.add('winds', s.play(m, v, dur=d * 1.1, release=0.3), t, 0.8, her)
        elif part == 'bed':
            hold('low', cb, m + 12, t, t + d, v, her, rise=4.0, fall=2.0, gain=0.5)
        elif part == 'shield':
            M.add('harp', glock.play(m - 12, v), t, 0.6, her)
            M.add('harp', harp.play(m - 12, v), t, 0.7, her)
        elif part == 'helmet':
            M.add('harp', harp.play(m, v), t, 0.9, her)
        elif part == 'hornhair':
            hold('brass', horn, m, t, t + d, v, her, rise=0.5, fall=1.5, gain=0.6)
        elif part == 'cut':
            M.add('brass', tpt.play(m - 12, v), t, 0.9, her)
            M.add('perc', crash.play(105), t, 0.6, her)
            M.add('fx', whoosh(0.5, 4000, 800, 0.7, seed=int(t * 10)), t - 0.1, 0.9, him)
        elif part == 'shock':
            s = tbn if m < note('C4') else horn
            hold('brass', s, m if s is tbn else m - 12, t, t + d, v, her, rise=0.05, fall=1.0, gain=0.8)
            if m == note('C3'):
                M.add('perc', timp.play(v, pitch=-4), t, 1.0, her)
                M.add('perc', crash.play(120), t, 0.8, her)
        elif part == 'fate':
            s = tuba if m < note('C3') else tbn if m < note('C4') else horn
            hold('brass', s, m if s is not horn else m - 12, t, t + d, v, her, rise=0.3, fall=1.0, gain=0.75)
            if m < note('E2'):
                M.add('perc', timp.play(v - 10, pitch=-6), t, 0.7, her)
        elif part == 'trem':
            hold('strings', ctrem, m, t, t + d, v, 0.0, rise=0.3, fall=2.5, gain=0.6)
        elif part == 'innocent':
            s = vn if m >= note('Ab4') else ob if m >= note('Eb4') else vc
            if d > 1.2:
                hold('strings', s, m, t, t + d, v, her, rise=0.5, fall=1.5, gain=0.7)
            else:
                M.add('strings', s.play(m, v, dur=d * 1.1, release=0.4), t, 0.8, her)
        elif part == 'courage':
            M.add('brass', horn.play(m, v, dur=d * 1.1, release=0.3), t, 0.8, him)
        elif part == 'warm':
            hold('strings', vc, m, t, t + d, v, her * 0.5, rise=3.0, fall=1.5, gain=0.5)
    for t0 in (T_SHIELD, T_HELMET):
        M.add('perc', tri.play(90), t0, 0.6, her)
