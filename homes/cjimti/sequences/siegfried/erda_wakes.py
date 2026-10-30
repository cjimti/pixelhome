"""Erda Wakes: a wild place at the foot of Brünnhilde's rock, at night, in a storm. The porch is the rock, its
summit the middle of Porch Front, where the magic fire still burns low far above; the wings and Side are the
storm sky, slate blue clouds rolling, rain, and lightning that cracks a whole run white at a time.

The Act III prelude gallops in the low strings over Erda's motif (Donington 3) and the need of the gods (5a),
and the Wanderer's chords (17) blaze through it on the brass: every chord a wave of deep blue rolling out over
the house. The Wanderer strides in from the free end of Right to the front of Left and strikes the ground three
times with his spear, calling the earth mother up: each strike a blue-white flash and a shock running out
along the ground. Erda rises at the middle of Left out of the earth, moss green over dark earth, swelling up
and out over Left and the Side on her motif while the storm drops; every phrase of hers breathes her green
wider. Over it the Twilight of the Gods (4) sounds on the trombones, and the sky darkens red-violet for a
moment before the storm comes back, and the two of them face each other in it.

compose() holds every note; stage(), sky(), figure() and fire() are the rock and the sky, shared word for word by
Act III's scenes on a clock that runs on from scene to scene."""
import numpy as np
from pixelhome.audio import note
from pixelhome.fx import DT, hexc, light, smoothstep, nframes, keys, Flicker, smooth_noise, colormap
from pixelhome.leitmotifs import play

CODE = 'SF23'
TITLE = 'Erda Wakes'
KIND = 'show'
DESCRIPTION = ('A storm at the foot of the fire-ringed rock. The Wanderer strikes the ground three times with his '
               'spear, and Erda, the earth mother, rises out of the ground in a swell of green.')
VOICEOVER = ('A storm at the foot of the mountain. The Wanderer strikes the earth with his spear, and calls up '
             'the oldest power in the world.')

K = 0                                       # this scene's place on Act III's shared clock: T = t + 80 K
GALLOP = [(0.3, 0), (6.7, 1), (13.1, 2), (19.5, 3)]       # the prelude's galloping figure, Erda's motif in the bass
T_WAND = [4.0, 12.0]                        # the Wanderer's chords on the brass
T_IN = 6.0                                  # he strides in
T_STOP = 20.0
T_STRIKE = [24.0, 27.0, 30.0]               # "Wache, Wala!"
T_RISE = 33.0                               # Erda rises
T_ERDA = [35.0, 47.0]
T_NEED = 41.0                               # the need of the gods
T_DOWN = 57.0                               # the Twilight of the Gods
T_WAND2 = 68.0
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
    """Every note: (time, seconds, midi, velocity, part, k)."""
    N = []

    def add(t, d, m, v, part, k=None):
        N.append((float(t), float(d), note(m) if isinstance(m, str) else int(m), int(v), part, k))

    for t0, k in GALLOP:                    # galloping triplets on G minor, Erda's motif in the basses beneath
        for j in range(16):
            add(t0 + j * 0.4, 0.35, ('G2', 'D3', 'Bb2', 'D3')[j % 4], 92 + 4 * k, 'gallop', k)
        for t, m, v, d in play('erda', t0, 0.8, -12, 96 + 4 * k):
            if m < note('Ab3'):
                add(t, d, m, v, 'erdabass', k)
    for k, t0 in enumerate(T_WAND):
        for t, m, v, d in play('wanderer', t0, 0.9, 0, 110 + 6 * k):
            add(t, d, m, v, 'wanderer', k)
    for t0 in T_STRIKE:
        add(t0, 0.5, 'G1', 124, 'strike')
    add(T_RISE, D - T_RISE, 'Db2', 70, 'earth')
    for k, t0 in enumerate(T_ERDA):
        for t, m, v, d in play('erda', t0, 1.1, 0, 84 + 6 * k):
            add(t, d, m, v, 'erda', k)
    for t, m, v, d in play('gotternoth', T_NEED, 0.6, 0, 92):
        add(t, d, m, v, 'need')
    for t, m, v, d in play('downfall', T_DOWN, 0.9, -12, 104):
        add(t, d, m, v, 'down')
    for t, m, v, d in play('wanderer', T_WAND2, 1.0, 0, 96):
        add(t, d, m, v, 'wanderer', 2)
    return sorted(N, key=lambda e: e[0])


def bolts():
    """Lightning: [(time, run, strength)], on the downbeats of the gallop and the Wanderer's chords."""
    rng = np.random.default_rng(23)
    runs = ['Side', 'Left', 'Right', 'Left', 'Right', 'Side']
    ts = [t0 + 1.6 * j for t0, _ in GALLOP for j in range(4)] + [t0 + 0.05 for t0 in T_WAND] + [T_WAND2 + 0.05, 71.5, 74.0, 77.0]
    return [(float(t), runs[i % len(runs)], float(rng.uniform(0.8, 1.0))) for i, t in enumerate(sorted(ts))]


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
    N = compose()
    wand = [e for e in N if e[4] == 'wanderer']
    erda = [e for e in N if e[4] == 'erda']
    p_erda = at(G, *ERDA_AT)
    p_wand = at(G, *WAND_AT)
    calm = lambda t: smoothstep(T_RISE, T_RISE + 6, t) * (1 - smoothstep(T_WAND2 - 3, T_WAND2, t))

    for f in range(F):
        t = f * DT
        T = t + 80 * K
        lv = dict(START)
        lv['storm'] = START['storm'] * (1 - 0.35 * calm(t))
        down = smoothstep(T_DOWN, T_DOWN + 2, t) * (1 - smoothstep(T_DOWN + 7, T_DOWN + 11, t))
        fr = sky(S, T, lv)

        # lightning: a whole run cracks white
        for tb, run, s in bolts():
            a = t - tb
            if 0 <= a < 1.2:
                env = min(1.0, np.exp(-a / 0.1) + 0.8 * np.exp(-((a - 0.16) / 0.05) ** 2))
                fr += light(BOLT, s * env * (G.seg_of == run) * (0.5 + 0.5 * S['jag']))
                fr += light(CLOUD, 0.6 * np.exp(-a / 0.4) * (G.seg_of == run))
                fr += light(STORM, 0.35 * env * S['sky'])

        # the Wanderer's chords: a wave of deep blue rolling out from him over the house
        for t0, dur, m, v, part, k in wand:
            a = t - t0
            if 0 <= a < 2.5 and m >= note('B4'):
                p = walk(G, t0)
                r = 1300 * (1 - np.exp(-a / 0.8))
                fr += light(WOTAN, 1.0 * np.exp(-a / 1.1) * np.exp(-((np.abs(d - p) - r) / 200) ** 2))

        # the Twilight of the Gods: the sky darkens red-violet
        fr += light(TWILIGHT, 0.6 * down * S['sky'] * (0.7 + 0.3 * np.sin(2 * np.pi * (d / 400 - 0.1 * t))))

        # Erda rises out of the earth: dark earth first, then moss green swelling over Left and the Side
        if t >= T_RISE - 1:
            g = smoothstep(T_RISE - 1, T_RISE + 4, t)
            width = 60 + 260 * smoothstep(T_RISE, T_RISE + 10, t)
            breath = 0.0
            for t0, dur, m, v, part, k in erda:
                a = t - t0
                if 0 <= a < dur + 1.5:
                    breath = max(breath, np.exp(-a / (dur + 0.6)) * smoothstep(0, 0.1, a))
            w = width * (1 + 0.5 * breath)
            fr += light(EARTH, 0.7 * g * np.exp(-((d - p_erda) / (w * 1.4)) ** 2))
            fr += light(MOSS, (0.75 + 0.3 * breath) * g * np.exp(-((d - p_erda) / w) ** 2))
            fr = figure(fr, S, p_erda, ERDA_HI, (0.55 + 0.35 * breath) * g, w=20)

        # the Wanderer, and his three spear strikes on the ground
        p = walk(G, t)
        if t >= T_IN - 0.5:
            fr = figure(fr, S, p, WOTAN, 0.85 * smoothstep(T_IN - 0.5, T_IN + 0.5, t))
            fr += light(SPEAR, 0.6 * np.exp(-((d - p + 14) / 6) ** 2) * smoothstep(T_IN, T_IN + 1, t))
        for t0 in T_STRIKE:
            a = t - t0
            if 0 <= a < 2.0:
                fr += light(BOLT, min(1.0, 1.2 * np.exp(-a / 0.08)) * np.exp(-((d - p_wand) / 50) ** 2))
                fr += light(SPEAR, 1.0 * np.exp(-a / 0.6) * np.exp(-((np.abs(d - p_wand) - 1300 * a) / 110) ** 2))
                fr += light(WOTAN, 0.7 * np.exp(-a / 0.3))
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

    for name, gain, rev in (('low', 0.26, 0.25), ('strings', 0.2, 0.3), ('brass', 0.24, 0.3), ('perc', 0.24, 0.3),
                            ('winds', 0.22, 0.35), ('fx', 0.08, 0.3)):
        M.bus(name, gain=gain, reverb=rev)
    vc = M.sampler('Strings/Cello Section/spic/*.wav', tune=-12)
    vcs = M.sampler('Strings/Cello Section/susvib/*.wav', tune=-12)
    cb = M.sampler('Strings/Solo Contrabass/SusNV/*.wav', tune=-12)
    cbs = M.sampler('Strings/Solo Contrabass/Spic/*.wav', tune=-12)
    tbn = M.sampler('Brass/Tenor Trombone/sus/*.wav', tune=-12)
    tuba = M.sampler('Brass/Tuba/sus/*.wav', tune=-12)
    horn = M.sampler('Brass/F Horn/sus/*.wav', tune=-12)
    bsn = M.sampler('Woodwinds/Bassoon/sus/*.wav', tune=-12)
    clar = M.sampler('Woodwinds/Clarinet/susLong/*.wav', tune=-12)
    timp = M.hits('Percussion/Timpani/Timpani1_Hit*.wav')
    roll = M.hits('Percussion/Timpani/Rolls/*.wav')
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

    erda_p = pan_at(at(G, *ERDA_AT))
    wand_p = pan_at(at(G, *WAND_AT))
    for t, d, m, v, part, k in compose():
        if part == 'gallop':
            calm = 1 - 0.5 * smoothstep(T_RISE, T_RISE + 6, t)
            M.add('strings', vc.play(m, int(v * calm)), t, 0.8, 0.0)
        elif part == 'erdabass':
            M.add('low', cb.play(m, v, dur=d * 1.05, release=0.3), t, 0.85, erda_p * 0.5)
            M.add('low', cbs.play(m - 12, v - 10), t, 0.6, erda_p * 0.5)
        elif part == 'wanderer':
            p = pan_at(walk(G, t))
            if m >= note('Gb4'):
                hold('brass', horn, m - 12, t, t + d, v - 6, p, rise=0.2, fall=1.0, gain=0.7)
            elif m >= note('A3'):
                hold('brass', tbn, m, t, t + d, v, p, rise=0.15, fall=1.0, gain=0.8)
            else:
                hold('low', tuba, m, t, t + d, v, p, rise=0.15, fall=1.0, gain=0.85)
            if m == min(e[2] for e in compose() if e[4] == 'wanderer' and e[0] == t):
                M.add('perc', timp.play(v, pitch=-5), t, 0.7, p)
        elif part == 'strike':
            M.add('perc', timp.play(v, pitch=-8), t, 1.0, wand_p)
            M.add('perc', crash.play(110), t, 0.6, wand_p)
            M.add('fx', whoosh(0.6, 3000, 400, 0.7, seed=int(t)), t - 0.05, 0.9, wand_p)
        elif part == 'earth':
            M.add('perc', gong.play(100), t, 0.8, erda_p)
            M.add('perc', roll.play(90, pitch=-6, dur=4.0), t - 1.0, 0.7, erda_p)
            hold('low', cb, m, t, t + d, v, erda_p, rise=3.0, fall=2.0, gain=0.6)
        elif part == 'erda':
            if m >= note('Db4'):
                hold('winds', clar, m - 12, t, t + d, v, erda_p, rise=0.3, fall=1.0, gain=0.8)
            elif m >= note('E3'):
                hold('winds', bsn, m, t, t + d, v, erda_p, rise=0.3, fall=1.0, gain=0.8)
            else:
                hold('low', vcs, m, t, t + d, v - 10, erda_p, rise=0.5, fall=1.0, gain=0.6)
        elif part == 'need':
            if m >= note('Db4'):
                M.add('strings', vcs.play(m - 12, v, dur=d * 1.1, release=0.3), t, 0.7, 0.0)
            else:
                M.add('brass', tbn.play(m, v - 10, dur=d * 1.1, release=0.3), t, 0.7, 0.0)
        elif part == 'down':
            if d > 1.2:
                hold('brass', tbn, m, t, t + d, v, 0.0, rise=0.2, fall=1.2, gain=0.85)
            else:
                M.add('brass', tbn.play(m, v, dur=d * 1.05, release=0.3), t, 0.9, 0.0)
    for tb, run, s in bolts():
        p = pan_at(at(G, run, 0.5))
        M.add('perc', roll.play(int(70 + 30 * s), pitch=-3, dur=1.6), tb, 0.45, p)
