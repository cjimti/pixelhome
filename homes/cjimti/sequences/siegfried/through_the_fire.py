"""Through the Fire: the storm is thinning; the fire rings the rock on the porch and Siegfried stands at Right 0.6
looking up at it. He puts his horn to his lips (Donington 48), twice, and every note throws an emerald sweep out
to both ends of the house.

Then he plunges in, and the fire comes out to meet him. Loge's music (20) climbs on the violins and harp over and
over, and the flames roar out from the porch along both wings and down the Side until every run is burning,
red at the roots, orange and gold at the tips, licking both ways; each of Loge's figures throws a white-gold
tongue leaping along the roofline, and his flickering (20a) on the glockenspiel and piccolo scatters sparks.
Through it Siegfried runs as an emerald comet with a white-hot head, the flames parting round him and closing
behind, slowly up round the porch toward the summit. Twice his strength (53) blazes on the brass and the whole
fire leaps gold; his horn call rings out once more in the middle of it.

He comes out at the top. The fire sinks back to a ring round the rock, the storm is gone and the sky calms to a
deep still blue, and at the summit a silver glow wakes in the middle of the flames: the magic sleep (16)
shimmers in the woodwinds, every chord a violet ripple out from the sleeper, and Siegfried stands beside her.

compose() holds every note; stage(), sky(), figure() and fire() are the rock and the sky, shared word for word by
Act III's scenes on a clock that runs on from scene to scene."""
import numpy as np
from pixelhome.audio import note
from pixelhome.fx import DT, hexc, light, smoothstep, nframes, keys, Flicker, smooth_noise, colormap
from pixelhome.leitmotifs import play

CODE = 'SF26'
TITLE = 'Through the Fire'
KIND = 'show'
DESCRIPTION = ('Siegfried blows his horn and plunges into the magic fire. The flames roar out over the whole house '
               'as he runs through them, and when they sink back he is standing at the top beside a sleeping figure.')
VOICEOVER = ('He knows no fear, so he walks straight into the fire. '
             'And at the top of the mountain, someone is sleeping.')

K = 3                                       # this scene's place on Act III's shared clock: T = t + 80 K
T_HORN = [(2.0, 0), (6.0, 1), (36.0, 2)]    # his horn call
T_PLUNGE = 9.5                              # into the fire
T_ROAR = (9.5, 15.5)                        # the fire spreading out over the house
LOGES = [9.6 + 1.6 * k for k in range(30)]  # Loge's climbing figure, over and over
T_SIEG = [24.0, 30.0]                       # his strength, twice
T_TOP = 43.0                                # he comes out at the summit
T_SINK = (42.0, 56.0)                       # the fire sinking back to a ring
T_SLEEP = 50.0                              # the magic sleep
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
HERO_HEAD = hexc('#e8ffe8')
GOLD = hexc('#ffd060')
SPARK = hexc('#fff0b0')
VIOLET = hexc('#7a6aff')

START = dict(storm=0.4, rock=0.3, fire=0.6, wide=0.0, dawn=0.0, sleeper=0.0)        # where SF25 left it
END = dict(storm=0.25, rock=0.35, fire=0.4, wide=0.0, dawn=0.0, sleeper=0.7)        # SUMMIT, where SF27 begins
FROM = ('Right', 0.6)
TOP = ('Porch Front', 0.35)


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

    for t0, k in T_HORN:
        for t, m, v, d in play('siegfried_horn', t0, 0.34, 5 + 2 * (k == 2), 100 + 8 * k):
            add(t, d, m, v, 'horn', k)
    add(T_PLUNGE, 0.1, 'C1', 124, 'plunge')
    for j, t0 in enumerate(LOGES):
        if t0 > T_SINK[1] + 4:
            break
        tr = (0, 3, 7, 12)[j % 4] + 12
        v = int(98 - 40 * smoothstep(T_SINK[0], T_SINK[1] + 4, t0))
        for t, m, vv, d in play('loge', t0, 0.2, tr, v):
            add(t, d, m, vv, 'loge', j)
        for t, m, vv, d in play('loge_flicker', t0 + 0.8, 0.12, 12, v - 10):
            add(t, d, m, vv, 'flicker', j)
    for m in ('E1', 'B1', 'E2', 'B2', 'E3', 'Ab3'):
        add(T_PLUNGE, T_SINK[1] - T_PLUNGE, m, 72, 'firebed')
    for k, t0 in enumerate(T_SIEG):
        for t, m, v, d in play('siegfried', t0, 0.5, -10, 114 + 6 * k):
            add(t, d, m, v, 'sieg', k)
    for t, m, v, d in play('sleep', T_SLEEP, 1.0, -4, 82):
        add(t, d, m, v, 'sleep')
    for m in ('E2', 'B2', 'E3', 'Ab3'):
        add(T_SINK[1], D - T_SINK[1], m, 56, 'calm')
    return sorted(N, key=lambda e: e[0])


def hero(G, t):
    """Where Siegfried is at time t: from the foot of the rock up round the porch to the summit."""
    a, b = at(G, *FROM), at(G, *TOP)
    return a + (b - a) * smoothstep(T_PLUNGE, T_TOP, t)


def render(G, seed=26):
    rng = np.random.default_rng(seed)
    F = nframes(D)
    out = np.zeros((F, G.N, 3))
    S = stage(G)
    d = S['d']
    L = d.max()
    N = compose()
    horns = [e for e in N if e[4] == 'horn']
    leaps = [(t0, rng.uniform(0, L), rng.choice([-1, 1])) for t0 in LOGES]
    glocks = [e[0] for e in N if e[4] == 'flicker']
    spark_at = rng.uniform(0, L, len(glocks))
    sieg = [sorted({e[0] for e in N if e[4] == 'sieg' and e[5] == k}) for k in range(2)]
    sleeps = np.array(sorted({e[0] for e in N if e[4] == 'sleep'}))
    p0, p1 = at(G, 'Porch Left', 0.0), at(G, 'Porch Right', 1.0)
    from_porch = np.clip(np.maximum(p0 - d, d - p1), 0, None)
    summit = S['summit']

    for f in range(F):
        t = f * DT
        T = t + 80 * K
        lv = {k: keys(t, [(0, START[k]), (T_SINK[0], START[k]), (T_SINK[1], END[k])]) for k in START}
        lv['storm'] = keys(t, [(0, START['storm']), (T_PLUNGE, 0.3), (T_SINK[1], END['storm'])])
        lv['sleeper'] = END['sleeper'] * smoothstep(T_TOP + 3, T_SLEEP + 6, t)
        roar = smoothstep(T_ROAR[0], T_ROAR[1], t) * (1 - smoothstep(T_SINK[0], T_SINK[1], t))
        lv['fire'] += 0.35 * roar
        fr = sky(S, T, lv)
        ps = hero(G, t)

        # the fire roars out from the porch over every run, then sinks back to the ring
        reach = 1700 * smoothstep(T_ROAR[0], T_ROAR[1], t) * (1 - smoothstep(T_SINK[0], T_SINK[1], t))
        if reach > 1:
            mask = smoothstep(reach + 80, reach - 80, from_porch) * S['sky']
            boost = sum(np.exp(-(t - x) / 0.5) for k in range(2) for x in sieg[k][:1] if 0 <= t - x < 2.5)
            flame = fire(S, T, 0.0, 1.0, boost=0.35 + boost)
            fr += flame * mask[:, None]
            front = np.exp(-((from_porch - reach) / 60) ** 2) * S['sky'] * (reach < 1650)
            fr += light(AMBER, 0.8 * front)

        # each of Loge's figures: a white-gold tongue leaping along the roofline
        for t0, x0, sgn in leaps:
            a = t - t0
            if 0 <= a < 1.2:
                c = x0 + sgn * 700 * a
                fr += light(SPARK, 1.0 * roar * np.exp(-a / 0.5) * np.exp(-((d - c) / 45) ** 2))
                fr += light(AMBER, 0.85 * roar * np.exp(-a / 0.6) * np.exp(-((d - c + sgn * 90) / 110) ** 2))
        for j, x in enumerate(glocks):         # his flickering: sparks of white-gold
            a = t - x
            if 0 <= a < 0.4:
                fr += light(SPARK, 0.8 * roar * np.exp(-a / 0.1) * np.exp(-((d - spark_at[j]) / 6) ** 2))

        # his strength: the whole fire leaps gold
        for k, ons in enumerate(sieg):
            for x in ons:
                a = t - x
                if 0 <= a < 0.8:
                    fr += light(GOLD, (0.75 + 0.15 * k) * np.exp(-a / 0.35) * (0.6 + 0.4 * heat(d, T)))

        # his horn call: emerald sweeps out to both ends on every note
        for t0, dur, m, v, part, k in horns:
            a = t - t0
            if 0 <= a < 1.2:
                src = hero(G, t0)
                fr += light(EMERALD, 0.9 * np.exp(-a / 0.5) * np.exp(-((np.abs(d - src) - 1800 * a) / 110) ** 2))
                fr += light(EMERALD, 0.8 * np.exp(-a / 0.25) * np.exp(-((d - src) / 70) ** 2))

        # the magic sleep: violet ripples out from the sleeper on every chord
        j = int(np.searchsorted(sleeps, t, side='right')) - 1
        if j >= 0 and t - sleeps[j] < 2.5:
            a = t - sleeps[j]
            fr += light(VIOLET, 0.7 * np.exp(-a / 1.0) * np.exp(-((np.abs(d - summit) - 500 * a) / 90) ** 2))

        # Siegfried: an emerald comet with a white-hot head; the flames part round him
        if T_PLUNGE <= t < T_TOP + 1:
            near = np.exp(-((d - ps) / 60) ** 2)
            fr = fr * (1 - 0.6 * near)[:, None]
            tail = np.exp(-np.clip(d - ps, 0, None) / 120) * (d >= ps)
            fr += light(EMERALD, 0.7 * tail)
        fr = figure(fr, S, ps, EMERALD, 0.85)
        fr += light(HERO_HEAD, 0.8 * np.exp(-((d - ps) / 5) ** 2))
        if T_PLUNGE <= t < T_PLUNGE + 0.8:
            a = t - T_PLUNGE
            fr += light(SPARK, 0.9 * np.exp(-a / 0.15) * np.exp(-((d - ps) / 80) ** 2))
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

    for name, gain, rev in (('low', 0.23, 0.25), ('strings', 0.19, 0.32), ('brass', 0.23, 0.3), ('perc', 0.21, 0.3),
                            ('mallet', 0.12, 0.35), ('winds', 0.2, 0.4), ('harp', 0.18, 0.4), ('fx', 0.07, 0.3)):
        M.bus(name, gain=gain, reverb=rev)
    vln = M.sampler('Strings/Violin Section/Spic/*.wav', tune=-12)
    vlns = M.sampler('Strings/Violin Section/susVib/*.wav', tune=-12)
    vcs = M.sampler('Strings/Cello Section/susvib/*.wav', tune=-12)
    ctrem = M.sampler('Strings/Cello Section/trem/*.wav', tune=-12)
    harp = M.sampler('Strings/Harp/*.wav')
    glock = M.sampler('Percussion/Glock/*.wav')
    picc = M.sampler('Woodwinds/Piccolo/Stac/*.wav', tune=-12)
    flute = M.sampler('Woodwinds/Flute/susvib/*.wav', tune=-12)
    clar = M.sampler('Woodwinds/Clarinet/susLong/*.wav', tune=-12)
    oboe = M.sampler('Woodwinds/Oboe/Sus/*.wav', tune=-12)
    horn = M.sampler('Brass/F Horn/sus/*.wav', tune=-12)
    tpt = M.sampler('Brass/Trumpet/sus/*.wav', tune=-12)
    tbn = M.sampler('Brass/Tenor Trombone/sus/*.wav', tune=-12)
    timp = M.hits('Percussion/Timpani/Timpani1_Hit*.wav')
    crash = M.hits('Percussion/cymbal-crash1_f*.wav')
    roll = M.hits('Percussion/Timpani/Rolls/*.wav')

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

    summit = pan_at(at(G, 'Porch Front', 0.5))
    rng = np.random.default_rng(26)
    for t, d, m, v, part, k in compose():
        ph = pan_at(hero(G, t))
        if part == 'horn':
            M.add('brass', horn.play(m, v, dur=d * 1.1, release=0.3), t, 0.95, ph)
        elif part == 'plunge':
            M.add('perc', crash.play(v), t, 0.9, ph)
            M.add('perc', timp.play(v, pitch=-5), t, 0.9, ph)
            M.add('perc', roll.play(110, pitch=-3, dur=5.0), t, 0.7, 0.0)
            M.add('fx', whoosh(5.0, 200, 4000, 0.9, seed=26), t, 1.0, 0.0)
        elif part == 'loge':
            pan = float(rng.uniform(-0.8, 0.8))
            M.add('strings', vln.play(m - 12, v), t, 0.7, pan)
            M.add('harp', harp.play(m - 12, v - 10), t, 0.6, pan)
        elif part == 'flicker':
            pan = float(rng.uniform(-0.8, 0.8))
            M.add('mallet', glock.play(m - 12, v - 10), t, 0.6, pan)
            M.add('winds', picc.play(m - 24, v - 16), t, 0.4, pan)
        elif part == 'firebed':
            hold('low', ctrem if m < note('E3') else vlns, m, t, t + d, v, 0.0, rise=3.0, fall=4.0, gain=0.5)
        elif part == 'sieg':
            M.add('brass', horn.play(m, v, dur=d * 1.1, release=0.3), t, 0.95, ph)
            M.add('brass', tpt.play(m, v - 18, dur=d * 1.1, release=0.3), t, 0.45, ph)
            M.add('low', tbn.play(m - 12, v - 14, dur=d * 1.1, release=0.3), t, 0.5, ph)
            if t == T_SIEG[k]:
                M.add('perc', crash.play(100 + 8 * k), t, 0.7, 0.0)
                M.add('perc', timp.play(v, pitch=-4), t, 0.8, 0.0)
        elif part == 'sleep':
            s = flute if m >= note('E5') else (oboe if m >= note('Ab4') else clar)
            if d > 1.2:
                hold('winds', s, m - 12, t, t + d, v, summit, rise=0.4, fall=1.2, gain=0.7)
            else:
                M.add('winds', s.play(m - 12, v, dur=d * 1.1, release=0.4), t, 0.75, summit)
        elif part == 'calm':
            hold('strings', vcs, m, t, t + d, v, summit * 0.5, rise=4.0, fall=1.5, gain=0.5)
