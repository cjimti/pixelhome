"""Ewig war ich: the summit in the full sunrise, rose, gold and sky blue on every run, Siegfried emerald at Porch
Front 0.42 and Brünnhilde silver with gold glints at 0.55.

The peaceful theme in E major, Siegfried's love (Donington 89), sings out on the violins over the harp, and every
note of it swells a whole run of the house, one after another round the roofline, in emerald and gold, slow
and broad. Then her fear: she was a goddess, she is a woman now, and his passion frightens her. She draws back
along the porch, her silver trembling, the sky dims, and the inevitability of fate (85) sounds softly on the
horns in indigo swells. She pleads with him to leave her be, to her own love's motif (87) on the oboe, and each
phrase swells a run in silver and rose. He answers with his love again, fuller, the horns joining the violins,
and the runs swell emerald and gold again; she comes back to him, and on the second form of her love (87a) the
two reach for each other, a bridge of light growing between them as the runs swell sky blue and silver, until
they stand together again in the sunrise.

compose() holds every note; stage(), sky(), fire() and figure() are the rock and the sky, shared word for word by
Act III's scenes on a clock that runs on from scene to scene."""
import numpy as np
from pixelhome.audio import note
from pixelhome.fx import DT, hexc, light, smoothstep, nframes, keys, Flicker, smooth_noise, colormap
from pixelhome.leitmotifs import melody, play

CODE = 'SF29'
TITLE = 'Ewig war ich'
KIND = 'show'
DESCRIPTION = ("In the sunrise, Brünnhilde is afraid of losing herself, and pulls away. Siegfried's love answers "
               'her in slow, broad swells of colour round the house, until the two of them reach for each other.')
VOICEOVER = ('I was always yours, she says, but do not touch me. Leave me as I am. '
             'And he answers her with his love.')

K = 6                                       # this scene's place on Act III's shared clock: T = t + 80 K
T_LOVE = [(3.0, 0.9, 0), (46.0, 1.0, 1)]    # Siegfried's love: (start, beat, how full)
T_FEAR = [17.5, 23.0]                       # fate inevitable, softly: she draws back
FBEAT = 0.75
T_PLEAD = 29.5                              # her love, pleading
PBEAT = 0.45
T_TOGETHER = 61.0                           # her love's second form: they reach for each other
TBEAT = 0.6
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
    """Every note: (time, seconds, midi, velocity, part, k)."""
    N = []

    def add(t, d, m, v, part, k=None):
        N.append((float(t), float(d), note(m) if isinstance(m, str) else int(m), int(v), part, k))

    for j in range(int(D / 0.3)):
        t = j * 0.3
        quiet = T_FEAR[0] - 1 < t < T_PLEAD
        if not quiet:
            add(t, 1.2, ('E3', 'B3', 'E4', 'Ab4', 'B4', 'Ab4', 'E4', 'B3')[j % 8], 58, 'harp')
    for t0, beat, k in T_LOVE:
        for t, m, v, d in play('siegfried_love', t0, beat, -12, 94 + 10 * k):
            add(t, d, m, v, 'love', k)
        for m in ('E2', 'B2', 'E3', 'Ab3'):
            add(t0, 13.9 * beat, m, 66 + 6 * k, 'lovebed', k)
    for k, t0 in enumerate(T_FEAR):
        for t, m, v, d in play('fate_inevitable', t0, FBEAT, -12, 80 - 6 * k):
            add(t, d, m, v, 'fear', k)
    add(T_FEAR[0], T_PLEAD - T_FEAR[0], 'C2', 70, 'fearbed')
    for t, m, v, d in play('brunnhilde_love', T_PLEAD, PBEAT, 0, 90):
        add(t, d, m, v, 'plead')
    for t, m, v, d in play('brunnhilde_love_b', T_TOGETHER, TBEAT, -12, 96):
        add(t, d, m, v, 'together')
    for m in ('E2', 'B2', 'E3', 'Gb3', 'B3'):
        add(T_TOGETHER, D - T_TOGETHER, m, 64, 'togetherbed')
    return sorted(N, key=lambda e: e[0])


def swells():
    """Every melody note becomes a whole-run swell: [(time, seconds, run, colour)]."""
    out = []
    pal = {'love': (EMERALD, SUN), 'plead': (SILVER, ROSE), 'together': (SKYBLUE, SILVER, EMERALD)}
    for part, key, t0, beat, tr in (('love', 'siegfried_love', T_LOVE[0][0], T_LOVE[0][1], -12),
                                    ('plead', 'brunnhilde_love', T_PLEAD, PBEAT, 0),
                                    ('love', 'siegfried_love', T_LOVE[1][0], T_LOVE[1][1], -12),
                                    ('together', 'brunnhilde_love_b', T_TOGETHER, TBEAT, -12)):
        for j, (b, dd, m) in enumerate(melody(key, tr)):
            if dd * beat < 0.3:
                continue
            c = pal[part][j % len(pal[part])]
            out.append((t0 + b * beat, dd * beat, RUNS[len(out) % len(RUNS)], c))
    return out


def render(G, seed=29):
    F = nframes(D)
    out = np.zeros((F, G.N, 3))
    S = stage(G)
    d = S['d']
    N = compose()
    sw = swells()
    fears = np.array(sorted({e[0] for e in N if e[4] == 'fear'}))
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
        fear = smoothstep(T_FEAR[0] - 0.5, T_FEAR[0] + 1.5, t) * (1 - smoothstep(T_PLEAD + 6, T_LOVE[1][0] + 2, t))
        mid = smoothstep(1.0, 3.0, t) * (1 - smoothstep(T_TOGETHER + 9, D - 2, t))
        lv = dict(DAWN)
        lv['dawn'] = DAWN['dawn'] * (1 - 0.55 * mid - 0.2 * fear)
        fr = sky(S, T, lv)

        # every note of the love themes: a whole run swells in its colour, slow and broad
        for t0, dur, run, c in sw:
            a = t - t0
            if -0.4 <= a < dur + 6.0:
                g = smoothstep(-0.4, 0.5, a) * np.exp(-max(a - dur * 0.6, 0) / 2.2)
                fr += light(c, 0.95 * g * runs[run] * (0.85 + 0.15 * np.sin(2 * np.pi * (d / 300 - 0.2 * t))))

        # her fear: indigo swells of fate, the house trembling a little
        a = recent(fears, t, 3.0)
        if a is not None:
            fr += light(FATE_C, 1.0 * np.exp(-a / 2.0) * smoothstep(0, 0.3, a) * S['sky'])
        if fear > 0:
            fr = fr * (1 - 0.2 * fear * (0.5 + 0.5 * shake(T)))[:, None]

        # the two of them: she draws back and comes home; at the end a bridge of light grows between them
        back = smoothstep(T_FEAR[0], T_FEAR[0] + 4, t) * (1 - smoothstep(T_LOVE[1][0] + 4, T_LOVE[1][0] + 12, t))
        pb = pb_home + (pb_back - pb_home) * back
        tremble = 1 - 0.3 * fear * (0.5 + 0.5 * np.sin(2 * np.pi * 4.3 * t))
        bridge = smoothstep(T_TOGETHER, T_TOGETHER + 6, t) * (1 - smoothstep(D - 6, D - 1, t))
        reach = smoothstep(T_LOVE[1][0], T_LOVE[1][0] + 4, t) * (1 - smoothstep(T_TOGETHER, T_TOGETHER + 6, t)) * (0.5 + 0.5 * np.sin(2 * np.pi * t / 3.5))
        lo, hi = min(ps, pb), max(ps, pb)
        span = (d > lo) & (d < hi)
        if bridge > 0:
            u = (d - lo) / max(hi - lo, 1)
            fr += light(EMERALD + (SILVER - EMERALD) * np.clip(u, 0, 1)[:, None], 0.8 * bridge * span)
        if reach > 0:
            fr += light(EMERALD, 0.6 * reach * np.exp(-((d - ps) / 40) ** 2) * span)
        fr = hero(fr, S, ps, 0.85)
        fr = heroine(fr, S, pb, 0.9 * tremble, T)
        out[f] = fr
    return np.clip(out, 0, 1)


def score(M, G):
    from pixelhome.audio import SR
    order = np.argsort(G.pd)
    xs, ds = G.pos[order, 0], G.pd[order]
    x0, x1 = xs.min(), xs.max()

    def pan_at(dd):                         # path distance -> left/right across the facade, from the street
        x = np.interp(dd, ds, xs)
        return float(0.85 * (2 * (x - x0) / (x1 - x0) - 1))

    for name, gain, rev in (('low', 0.28, 0.3), ('strings', 0.34, 0.38), ('winds', 0.3, 0.38), ('brass', 0.28, 0.35),
                            ('harp', 0.22, 0.42)):
        M.bus(name, gain=gain, reverb=rev)
    harp = M.sampler('Strings/Harp/*.wav')
    vn = M.sampler('Strings/Violin Section/susVib/*.wav', tune=-12)
    va = M.sampler('Strings/Viola Section/susvib/*.wav', tune=-12)
    vc = M.sampler('Strings/Cello Section/susvib/*.wav', tune=-12)
    cb = M.sampler('Strings/Solo Contrabass/SusNV/*.wav', tune=-12)
    ob = M.sampler('Woodwinds/Oboe/Sus/*.wav', tune=-12)
    fl = M.sampler('Woodwinds/Flute/susvib/*.wav', tune=-12)
    horn = M.sampler('Brass/F Horn/sus/*.wav', tune=-12)

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

    her = pan_at(at(G, 'Porch Front', BRUNN_AT))
    him = pan_at(at(G, 'Porch Front', SIEG_AT))
    for t, d, m, v, part, k in compose():
        if part == 'harp':
            M.add('harp', harp.play(m, v), t, 0.7, 0.0)
        elif part == 'love':
            if d > 1.0:
                hold('strings', vn, m, t, t + d, v, him, rise=0.25, fall=1.2, gain=0.75)
            else:
                M.add('strings', vn.play(m, v, dur=d * 1.1, release=0.4), t, 0.85, him)
            if k == 1:
                M.add('brass', horn.play(m - 12, v - 18, dur=d * 1.1, release=0.4), t, 0.6, him)
        elif part == 'lovebed':
            hold('low', vc if m >= note('E3') else cb, m if m >= note('E3') else m + 12, t, t + d, v, 0.0,
                 rise=1.5, fall=2.0, gain=0.5)
        elif part == 'fear':
            hold('brass', horn, m, t, t + d, v, her, rise=0.4, fall=1.0, gain=0.6)
        elif part == 'fearbed':
            hold('low', cb, m + 12, t, t + d, v, her, rise=2.0, fall=2.0, gain=0.5)
        elif part == 'plead':
            if d > 1.0:
                hold('winds', ob, m, t, t + d, v, her, rise=0.2, fall=1.0, gain=0.75)
            else:
                M.add('winds', ob.play(m, v, dur=d * 1.1, release=0.35), t, 0.85, her)
            if m < note('C4'):
                M.add('low', va.play(m, v - 12, dur=d * 1.1, release=0.4), t, 0.6, her)
        elif part == 'together':
            if d > 1.0:
                hold('strings', vn, m, t, t + d, v, 0.0, rise=0.25, fall=1.4, gain=0.7)
                hold('winds', fl, m, t, t + d, v - 16, 0.0, rise=0.25, fall=1.4, gain=0.4)
            else:
                M.add('strings', vn.play(m, v, dur=d * 1.1, release=0.4), t, 0.8, 0.0)
        elif part == 'togetherbed':
            hold('low', vc if m >= note('E3') else cb, m if m >= note('E3') else m + 12, t, t + d, v, 0.0,
                 rise=3.0, fall=1.5, gain=0.5)
