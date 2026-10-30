"""Leuchtende Liebe: the end of the opera, on the summit in the full sunrise, Siegfried emerald at Porch Front 0.42
and Brünnhilde silver with gold glints at 0.55.

Siegfried's heroism (Donington 78) opens it on the horns and trombones, every note an emerald wave rolling out
from him over the house. Then the two of them answer each other, faster and faster: his motif (53) on the
horns, each note an emerald wave; love as fulfilment (90) from her on the violins, each note a wave of silver
and gold. Siegfried's love (89) comes back broad in the whole orchestra, and the runs of the house swell one
after another in emerald and silver. Then they laugh at death, "leuchtende Liebe, lachender Tod!": the two
motifs tumble over each other, quicker every time, and every note slams a whole run of the house in emerald or
silver-gold, run after run round the roofline, while the light beneath them builds. His heroism comes once
more, fast, over a timpani roll, the whole house climbing to full strength: emerald on the wings, silver and
gold on the rock.

Four great C major chords end it, each a whole-house hit of white gold, and on the last the house blazes
emerald and silver and gold on every run, and holds it to the end.

compose() holds every note; stage(), sky(), fire() and figure() are the rock and the sky, shared word for word by
Act III's scenes on a clock that runs on from scene to scene."""
import numpy as np
from pixelhome.audio import note
from pixelhome.fx import DT, hexc, light, smoothstep, nframes, keys, Flicker, smooth_noise, colormap
from pixelhome.leitmotifs import play

CODE = 'SF30'
TITLE = 'Leuchtende Liebe'
KIND = 'show'
DESCRIPTION = ('The end of the opera. Siegfried and Brünnhilde sing faster and faster, laughing at death, until '
               'the whole house blazes emerald, silver and gold on four great chords.')
VOICEOVER = ('Shining love, and laughing death! '
             'The end of Siegfried.')

K = 7                                       # this scene's place on Act III's shared clock: T = t + 80 K
T_HERO = 0.5                                # Siegfried's heroism, broad
HBEAT = 0.48
# the answers, quicker every time: (start, beat, who) -- 'S' his motif, 'L' love as fulfilment, from her
CALLS = [(13.0, 0.6, 'S'), (16.2, 0.5, 'L'), (19.6, 0.55, 'S'), (22.5, 0.45, 'L'), (25.6, 0.5, 'S'),
         (28.0, 0.42, 'L'), (31.0, 0.45, 'S'), (33.2, 0.38, 'L')]
T_LOVE = 36.0                               # Siegfried's love, broad, the whole orchestra
LBEAT = 0.62
LAUGH = [(45.5, 0.55, 'S'), (47.8, 0.45, 'L'), (50.6, 0.48, 'S'), (52.6, 0.4, 'L'), (55.0, 0.42, 'S'),
         (56.7, 0.36, 'L'), (58.8, 0.38, 'S'), (60.3, 0.33, 'L')]
T_HERO2 = 62.0                              # his heroism once more, fast
H2BEAT = 0.26
T_CHORDS = [68.5, 70.0, 71.5, 73.5]         # the four great chords; the last held to the end
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
GOLD = hexc('#ffc020')
WHITEGOLD = hexc('#fff0b0')

DAWN = dict(storm=0.0, rock=0.35, fire=0.15, wide=0.0, dawn=0.75, sleeper=0.0)
SIEG_AT, BRUNN_AT = 0.42, 0.55
RUNS = ['Left', 'Porch Front', 'Right', 'Side', 'Porch Left', 'Porch Right']


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

    for t, m, v, d in play('siegfried_heroism', T_HERO, HBEAT, 0, 108):
        add(t, d, m, v, 'heroism', 0)
    for i, (t0, beat, who) in enumerate(CALLS + LAUGH):
        v = 100 + min(24, 3 * i)
        if who == 'S':
            for t, m, vv, d in play('siegfried', t0, beat, -12, v):
                add(t, d, m, vv, 'S', i)
        else:
            for t, m, vv, d in play('love_fulfilled', t0, beat, 0, v):
                add(t, d, m, vv, 'L', i)
    for t, m, v, d in play('siegfried_love', T_LOVE, LBEAT, -12, 112):
        add(t, d, m, v, 'love')
    for m in ('E2', 'B2', 'E3', 'Ab3', 'B3'):
        add(T_LOVE, 13.9 * LBEAT, m, 84, 'lovebed')
    for t, m, v, d in play('siegfried_heroism', T_HERO2, H2BEAT, 0, 120):
        add(t, d, m, v, 'heroism', 1)
    add(T_HERO2, T_CHORDS[0] - T_HERO2, 'C2', 110, 'roll')
    chords = [('C2', 'C3', 'G3', 'C4', 'E4', 'G4'), ('F2', 'C3', 'A3', 'C4', 'F4', 'A4'),
              ('G2', 'D3', 'B3', 'D4', 'G4', 'B4'), ('C2', 'C3', 'G3', 'C4', 'E4', 'G4', 'C5')]
    for k, (t0, ch) in enumerate(zip(T_CHORDS, chords)):
        dur = (T_CHORDS[k + 1] - t0 - 0.15) if k + 1 < len(T_CHORDS) else D - t0 - 1.0
        for m in ch:
            add(t0, dur, m, 124, 'chord', k)
    return sorted(N, key=lambda e: e[0])


def render(G, seed=30):
    F = nframes(D)
    out = np.zeros((F, G.N, 3))
    S = stage(G)
    d = S['d']
    L = d.max()
    N = compose()
    ps, pb = at(G, 'Porch Front', SIEG_AT), at(G, 'Porch Front', BRUNN_AT)
    hero_on = np.array(sorted({e[0] for e in N if e[4] == 'heroism'}))
    s_notes = [e for e in N if e[4] == 'S']
    l_notes = [e for e in N if e[4] == 'L']
    love_on = np.array(sorted({e[0] for e in N if e[4] == 'love'}))
    runs = {r: (G.seg_of == r) for r in RUNS}
    wings = np.isin(G.seg_of, ['Side', 'Left', 'Right'])
    laugh_from = LAUGH[0][0] - 0.5
    slam = sorted([(e[0], 'S') for e in s_notes if e[0] >= laugh_from] + [(e[0], 'L') for e in l_notes if e[0] >= laugh_from])

    def recent(ts, t, span):
        i = int(np.searchsorted(ts, t, side='right')) - 1
        return (t - ts[i]) if i >= 0 and t - ts[i] < span else None

    for f in range(F):
        t = f * DT
        T = t + 80 * K
        build = smoothstep(T_HERO2 - 2, T_CHORDS[-1], t)
        blaze = smoothstep(T_CHORDS[-1], T_CHORDS[-1] + 0.6, t)
        lv = dict(DAWN)
        lv['dawn'] = DAWN['dawn'] * (1 - 0.45 * smoothstep(1, 3, t)) * (1 - 0.6 * blaze)
        fr = sky(S, T, lv)

        # the light building beneath them: emerald on the wings, silver and gold on the rock
        base = 0.15 * smoothstep(T_LOVE, T_LOVE + 9, t) + 0.6 * build + 0.3 * blaze
        shimmer = 0.85 + 0.15 * np.sin(2 * np.pi * (d / 260 - 0.6 * t))
        fr += light(EMERALD, base * wings * shimmer)
        fr += light(SILVER, 0.85 * base * S['porch'] * shimmer)
        tw = 0.5 + 0.5 * np.sin(2 * np.pi * (d / 31 + 1.7 * T)) * np.sin(2 * np.pi * (d / 19 - 1.1 * T))
        fr += light(GOLD, (0.4 * build + 0.6 * blaze) * tw ** 2)

        # heroism: emerald waves out from him
        span = 2.2
        a = recent(hero_on, t, span)
        if a is not None:
            r = 1500 * (1 - np.exp(-a / 0.6))
            fr += light(EMERALD, 0.95 * np.exp(-a / 0.9) * np.exp(-((np.abs(d - ps) - r) / 260) ** 2))

        # the answers before the laughter: emerald waves from him, silver and gold from her
        for notes, p, c1, c2 in ((s_notes, ps, EMERALD, HEAD), (l_notes, pb, SILVER, GLINT)):
            ons = np.array(sorted({e[0] for e in notes if e[0] < laugh_from}))
            a = recent(ons, t, 2.0)
            if a is not None:
                r = 1500 * (1 - np.exp(-a / 0.55))
                fr += light(c1, 0.95 * np.exp(-a / 0.8) * np.exp(-((np.abs(d - p) - r) / 240) ** 2))
                fr += light(c2, 0.5 * np.exp(-a / 0.5) * np.exp(-((np.abs(d - p) - 0.8 * r) / 80) ** 2))

        # his love, broad: each note swells a whole run, emerald and silver in turn
        a = recent(love_on, t, 3.0)
        if a is not None:
            j = int(np.searchsorted(love_on, t, side='right')) - 1
            c = EMERALD if j % 2 == 0 else SILVER
            fr += light(c, 0.95 * smoothstep(0, 0.3, a) * np.exp(-a / 1.6) * runs[RUNS[j % len(RUNS)]])

        # laughing at death: every note slams a whole run, emerald for him, silver-gold for her
        for j, (t0, who) in enumerate(slam):
            a = t - t0
            if 0 <= a < 0.9:
                run = runs[RUNS[j % len(RUNS)]]
                if who == 'S':
                    fr += light(EMERALD, np.exp(-a / 0.3) * run) + light(HEAD, 0.5 * np.exp(-a / 0.08) * run)
                else:
                    fr += light(SILVER, np.exp(-a / 0.3) * run) + light(GLINT, 0.6 * np.exp(-a / 0.2) * run)

        # the four great chords: each a whole-house hit of white gold; the last becomes the blaze
        for k, t0 in enumerate(T_CHORDS):
            a = t - t0
            if 0 <= a < 1.5:
                fr += light(WHITEGOLD, (0.75 + 0.08 * k) * np.exp(-a / (0.35 + 0.25 * (k == 3))))
        if blaze > 0:
            fr += light(EMERALD, 0.25 * blaze * wings)
            fr += light(GOLD, 0.3 * blaze * S['porch'] * (0.7 + 0.3 * tw))

        fr = hero(fr, S, ps, 0.85 + 0.15 * build)
        fr = heroine(fr, S, pb, 0.9 + 0.1 * build, T)
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

    for name, gain, rev in (('low', 0.26, 0.25), ('brass', 0.28, 0.3), ('strings', 0.26, 0.32), ('perc', 0.24, 0.3),
                            ('harp', 0.18, 0.4)):
        M.bus(name, gain=gain, reverb=rev)
    horn = M.sampler('Brass/F Horn/sus/*.wav', tune=-12)
    tpt = M.sampler('Brass/Trumpet/sus/*.wav', tune=-12)
    tbn = M.sampler('Brass/Tenor Trombone/sus/*.wav', tune=-12)
    tuba = M.sampler('Brass/Tuba/sus/*.wav', tune=-12)
    vn = M.sampler('Strings/Violin Section/susVib/*.wav', tune=-12)
    vc = M.sampler('Strings/Cello Section/susvib/*.wav', tune=-12)
    cb = M.sampler('Strings/Solo Contrabass/SusNV/*.wav', tune=-12)
    harp = M.sampler('Strings/Harp/*.wav')
    timp = M.hits('Percussion/Timpani/Timpani1_Hit*.wav')
    roll = M.hits('Percussion/Timpani/Rolls/*.wav')
    crash = M.hits('Percussion/cymbal-crash1_f*.wav')

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
        if part == 'heroism':
            if d > 1.0:
                hold('brass', horn, m, t, t + d, v, him, rise=0.08, fall=0.8, gain=0.8)
            else:
                M.add('brass', horn.play(m, v, dur=d * 1.1, release=0.3), t, 0.9, him)
            M.add('low', tbn.play(m - 12, v - 12, dur=d * 1.05, release=0.3), t, 0.6, him)
            if k == 1 and d > 1.0:
                M.add('perc', timp.play(v - 10, pitch=-5), t, 0.7, 0.0)
        elif part == 'S':
            M.add('brass', horn.play(m, v, dur=d * 1.1, release=0.25), t, 0.85, him)
            M.add('brass', tpt.play(m, v - 22, dur=d * 1.1, release=0.25), t, 0.4, him)
        elif part == 'L':
            if d > 0.8:
                hold('strings', vn, m, t, t + d, v, her, rise=0.06, fall=0.6, gain=0.7)
            else:
                M.add('strings', vn.play(m, v, dur=d * 1.1, release=0.3), t, 0.8, her)
            M.add('harp', harp.play(m, v - 20), t, 0.5, her)
        elif part == 'love':
            if d > 1.0:
                hold('strings', vn, m, t, t + d, v, 0.0, rise=0.2, fall=1.0, gain=0.75)
                hold('brass', horn, m - 12, t, t + d, v - 14, 0.0, rise=0.2, fall=1.0, gain=0.5)
            else:
                M.add('strings', vn.play(m, v, dur=d * 1.1, release=0.35), t, 0.85, 0.0)
        elif part == 'lovebed':
            s = vc if m >= note('E3') else cb
            hold('low', s, m if s is vc else m + 12, t, t + d, v, 0.0, rise=1.0, fall=1.5, gain=0.5)
        elif part == 'roll':
            r = 0.0
            while r < d:
                M.add('perc', roll.play(min(127, int(v * (0.7 + 0.3 * r / d))), pitch=-4, dur=2.2), t + r, 0.6, 0.0)
                r += 2.0
        elif part == 'chord':
            s = tuba if m < note('C3') else tbn if m < note('C4') else tpt if m >= note('G4') else horn
            mm = m if s in (tuba, tbn) else m - 12
            hold('brass', s, mm, t, t + d, v, 0.0, rise=0.03, fall=1.2 if k < 3 else 2.0, gain=0.7)
            if m == min(e[2] for e in compose() if e[4] == 'chord' and e[5] == k):
                M.add('perc', timp.play(124, pitch=-5), t, 1.0, 0.0)
                M.add('perc', crash.play(124), t, 0.9, 0.0)
    for t0 in (T_LOVE, T_HERO2):
        M.add('perc', crash.play(110), t0, 0.7, 0.0)
