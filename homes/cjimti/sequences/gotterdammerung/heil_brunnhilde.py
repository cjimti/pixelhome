"""Heil, Brünnhilde!: the farewell on the summit, and it is ecstatic. They answer each other faster and faster:
her love as fulfilment (Donington 90) in silver from the violins, his own motif (53) in emerald from the horns,
and every note of either slams a whole run into its colour and sends a sweep the length of the house, the runs
taking turns, the gaps between them shrinking until the two colours are tumbling over each other.

Then they sing together. Both motifs at once over a timpani roll, emerald and silver trading every run on every
note, the whole house swelling gold-white, until the unison: one huge flash of white and gold over every run,
and the two colours burst out from it, emerald racing over the Side and Left, silver over Right. Siegfried's horn
call (48) rings out, and he goes: down off the summit along Porch Front and out along Porch Right toward the
river, his horn throwing emerald streaks out along Right ahead of him to the free end, while Brünnhilde stays on
the summit waving, every wave a pulse of silver over the house, fainter as he goes.

compose() holds every note; stage(), heat(), fire(), scene(), strand() and figure() are shared word for word by
the Prologue's scenes (see GD01)."""
import numpy as np
from pixelhome.audio import note
from pixelhome.fx import DT, hexc, light, smoothstep, nframes, keys, Flicker, smooth_noise, colormap
from pixelhome.leitmotifs import play

CODE = 'GD05'
TITLE = 'Heil, Brünnhilde!'
KIND = 'show'
DESCRIPTION = ('The lovers say goodbye in a blaze of emerald and silver, answering faster and faster until they '
               'sing as one. Then his horn rings out and he leaves the mountain while she waves him away.')
VOICEOVER = ('Hail, Brünnhilde! Hail, Siegfried! One last embrace, and he sets off down the mountain.')

K = 4                                       # this scene's place on the Prologue's shared clock: T = t + 80 K
# the exchange: (time, who) — her love as fulfilment or his motif, the gaps shrinking
EXCHANGE = [(1.5, 'b'), (5.5, 's'), (8.5, 'b'), (12.0, 's'), (14.6, 'b'), (17.6, 's'), (19.8, 'b'), (22.4, 's'),
            (24.2, 'b'), (26.4, 's'), (27.9, 'b'), (29.8, 's'), (31.1, 'b'), (32.7, 's'), (33.8, 'b'), (35.2, 's')]
BBEAT, SBEAT = 0.5, 0.42
T_TOGETHER = 37.0                           # both at once over the timpani roll
T_UNISON = 47.0                             # the unison
T_HORN = [52.0, 57.0, 62.5]                 # his horn call, as he goes
HORNBEAT = 0.42
T_GO = 53.0                                 # he starts down off the summit
T_THERE = 66.0                              # at the head of Porch Right
T_SETTLE = 70.0
D = 80.0

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
GOLD = hexc('#ffaa00')

START = dict(night=0.0, stars=0.0, rock=0.35, fire=0.15, east=0.0, dawn=0.75, hue=0.62, day=0.3, rope=0.0)
END = dict(START)                           # where GD06 picks the morning up
SIEGFRIED_START = ('Porch Front', 0.35, 0.85)   # (segment, u, level)
BRUNNHILDE_START = ('Porch Front', 0.6, 0.9)
SIEGFRIED_END = ('Porch Right', 0.8, 0.85)
BRUNNHILDE_END = BRUNNHILDE_START
RING_ON_HER = 0.55                          # the Ring's glint on her hand: level, 9 units left of her


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


def compose():
    """Every note: (time, seconds, midi, velocity, part, k)."""
    N = []

    def add(t, d, m, v, part, k=None):
        N.append((float(t), float(d), note(m) if isinstance(m, str) else int(m), int(v), part, k))

    for j, (t0, who) in enumerate(EXCHANGE):
        v = 92 + j
        if who == 'b':
            for t, m, vv, d in play('love_fulfilled', t0, BBEAT * (1 - 0.02 * j), 5, v):
                add(t, d, m, vv, 'b', j)
        else:
            for t, m, vv, d in play('siegfried', t0, SBEAT * (1 - 0.015 * j), -12, v):
                add(t, d, m, vv, 's', j)
    for k in range(3):
        for t, m, v, d in play('love_fulfilled', T_TOGETHER + 3.3 * k, 0.5, 5 + 2 * k, 108 + 4 * k):
            add(t, d, m, v, 'b', 100 + k)
        for t, m, v, d in play('siegfried', T_TOGETHER + 0.4 + 3.3 * k, 0.42, -12 + 2 * k, 108 + 4 * k):
            add(t, d, m, v, 's', 100 + k)
    add(T_TOGETHER, T_UNISON - T_TOGETHER, 'Eb2', 96, 'roll')
    for m in ('Eb2', 'Bb2', 'Eb3', 'G3', 'Bb3', 'Eb4', 'G4'):
        add(T_UNISON, 3.5, m, 124, 'unison')
    for k, t0 in enumerate(T_HORN):
        for t, m, v, d in play('siegfried_horn', t0, HORNBEAT, 5, 112 - 8 * k):
            add(t, d, m, v, 'horn', k)
    for m in ('Eb1', 'Bb1', 'Eb2', 'G2', 'Bb2', 'Eb3'):
        add(T_SETTLE, D - T_SETTLE, m, 64, 'settle')
    return sorted(N, key=lambda e: e[0])


def runs_by_order():
    """The six runs, in path order."""
    return ['Side', 'Left', 'Porch Left', 'Porch Front', 'Porch Right', 'Right']


def walk(G, t):
    """Where Siegfried is: on the summit, then down along Porch Front and out along Porch Right."""
    a, b = at(G, *SIEGFRIED_START[:2]), at(G, *SIEGFRIED_END[:2])
    return a + (b - a) * smoothstep(T_GO, T_THERE, t)


def render(G, seed=5):
    F = nframes(D)
    out = np.zeros((F, G.N, 3))
    S = stage(G)
    d, L = S['d'], S['L']
    N = compose()
    p_b = at(G, *BRUNNHILDE_START[:2])
    runs = runs_by_order()
    masks = {r: (G.seg_of == r) for r in runs}
    notes = [e for e in N if e[4] in ('b', 's')]
    horn = sorted({e[0] for e in N if e[4] == 'horn'})
    waves = np.arange(T_GO, T_SETTLE + 4, 1.25)          # her waving

    for f in range(F):
        t = f * DT
        T = t + 80 * K
        dim = keys(t, [(0, 1.0), (2.5, 0.4), (T_TOGETHER, 0.32), (T_UNISON - 0.5, 0.55), (T_UNISON + 2, 0.4),
                       (T_SETTLE, 0.45), (D - 1.0, 1.0)])
        lv = dict(START)
        lv['dawn'] = START['dawn'] * dim
        lv['day'] = START['day'] * dim
        fr = scene(S, T, lv)
        p_s = walk(G, t)

        # every note of either: its whole run slams into the colour, and a sweep runs the length of the house
        for i, (t0, dur, m, v, who, k) in enumerate(notes):
            a = t - t0
            if not 0 <= a < 1.6:
                continue
            col = BRUNNHILDE if who == 'b' else SIEGFRIED
            src = p_b if who == 'b' else p_s
            together = k >= 100
            run = runs[(m + (3 if who == 'b' else 0) + (k % 6)) % 6]
            g = 0.8 + 0.2 * together
            fr += light(col, g * np.exp(-a / (0.3 + 0.2 * min(dur, 1.0))) * masks[run])
            sgn = 1 if (i % 2 == 0) == (who == 'b') else -1
            q = src + sgn * 1800 * a
            fr += light(col, 0.9 * np.exp(-a / 0.7) * np.exp(-((d - q) / 130) ** 2))
            fr += light(WHITE, 0.45 * np.exp(-a / 0.4) * np.exp(-((d - q) / 25) ** 2))

        # together: the house swelling gold-white over the roll
        if T_TOGETHER <= t < T_UNISON:
            u = smoothstep(T_TOGETHER, T_UNISON, t)
            fr += light(SUN, 0.45 * u * (0.8 + 0.2 * np.sin(2 * np.pi * (d / 300 - 1.5 * t))))

        # the unison: one huge flash, then emerald bursting over the Side and Left, silver over Right
        if T_UNISON <= t < T_UNISON + 5:
            a = t - T_UNISON
            fr += light(WHITE, 0.95 * np.exp(-a / 0.12))
            fr += light(GOLD, 0.9 * np.exp(-a / 0.6))
            front = 1700 * (1 - np.exp(-a / 0.8))
            left = smoothstep(p_b - front - 80, p_b - front + 80, d) * (d < p_b)
            right = smoothstep(p_b + front + 80, p_b + front - 80, d) * (d >= p_b)
            fr += light(SIEGFRIED, 0.95 * np.exp(-a / 1.8) * left)
            fr += light(BRUNNHILDE, 0.95 * np.exp(-a / 1.8) * right)

        # his horn: emerald streaks shooting ahead of him along Right to the free end
        for j, t0 in enumerate(horn):
            a = t - t0
            if 0 <= a < 1.2:
                q = p_s + 1500 * a
                fr += light(SIEGFRIED, 0.95 * np.exp(-a / 0.6) * np.exp(-((d - q) / 60) ** 2) * (d >= p_s - 20))
                fr += light(HEAD, 0.6 * np.exp(-a / 0.4) * np.exp(-((d - q) / 15) ** 2))

        # she waves: a silver pulse out over the house, fainter as he goes
        for j, t0 in enumerate(waves):
            a = t - t0
            if 0 <= a < 1.5:
                g = 0.5 * (1 - smoothstep(T_GO, T_SETTLE + 4, t0)) + 0.45
                g *= 1 - smoothstep(D - 6, D - 2, t)
                r = 1300 * (1 - np.exp(-a / 0.6))
                fr += light(BRUNNHILDE, g * np.exp(-a / 0.7) * np.exp(-((np.abs(d - p_b) - r) / 140) ** 2))

        # the two of them
        last = max([e[0] for e in notes if e[4] == 's' and e[0] <= t], default=-9)
        ls = SIEGFRIED_START[2] * (1 + 0.25 * np.exp(-(t - last) / 0.2))
        fr = figure(fr, S, p_s, SIEGFRIED, ls)
        fr += light(HEAD, 0.7 * ls * np.exp(-((d - p_s) / 6) ** 2))
        lastb = max([t0 for t0 in waves if t0 <= t], default=-9)
        lb = BRUNNHILDE_START[2] * (1 + 0.15 * np.exp(-(t - lastb) / 0.25) * (t < D - 4))
        fr = figure(fr, S, p_b, BRUNNHILDE, lb)
        fr += light(GLINT, 0.5 * BRUNNHILDE_START[2] * np.exp(-((d - p_b - 9) / 5) ** 2))
        fr += light(GOLD, RING_ON_HER * np.exp(-((d - p_b + 9) / 4) ** 2))
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

    for name, gain, rev in (('low', 0.3, 0.25), ('strings', 0.3, 0.35), ('brass', 0.3, 0.3), ('perc', 0.28, 0.3),
                            ('harp', 0.22, 0.4), ('warm', 0.26, 0.4)):
        M.bus(name, gain=gain, reverb=rev)
    vc = M.sampler('Strings/Cello Section/susvib/*.wav', tune=-12)
    vln = M.sampler('Strings/Violin Section/susVib/*.wav', tune=-12)
    cb = M.sampler('Strings/Solo Contrabass/SusNV/*.wav', tune=-12)
    harp = M.sampler('Strings/Harp/*.wav')
    horn = M.sampler('Brass/F Horn/sus/*.wav', tune=-12)
    tpt = M.sampler('Brass/Trumpet/sus/*.wav', tune=-12)
    tbn = M.sampler('Brass/Tenor Trombone/sus/*.wav', tune=-12)
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

    sb = pan_at(at(G, *BRUNNHILDE_START[:2]))

    def ps(t):
        return pan_at(walk(G, t))

    for t, d, m, v, part, k in compose():
        if part == 'b':
            if d >= 0.9:
                hold('strings', vln, m, t, t + d, v, sb, rise=0.15, fall=0.7, gain=0.8)
            else:
                M.add('strings', vln.play(m, v, dur=d * 1.1, release=0.25), t, 0.85, sb)
            M.add('harp', harp.play(m, v - 26), t, 0.45, sb)
        elif part == 's':
            M.add('brass', horn.play(m, v, dur=d * 1.1, release=0.25), t, 0.85, ps(t))
            M.add('low', vc.play(m - 12, v - 14, dur=d * 1.1, release=0.25), t, 0.55, ps(t))
            if k >= 100 and m >= note('G4') - 12:
                M.add('brass', tpt.play(m, v - 16, dur=d * 1.05, release=0.25), t, 0.45, ps(t))
        elif part == 'roll':
            r = 0.0
            while r < d:
                M.add('perc', roll.play(int(v * (0.6 + 0.4 * r / d)), pitch=-2, dur=2.6), t + r, 0.6, 0.0)
                r += 2.4
        elif part == 'unison':
            hold('brass', tbn if m < note('Eb3') else horn, m, t, t + d, v, 0.0, rise=0.05, fall=1.5, gain=0.7)
            hold('strings', vln, m + 12, t, t + d, v - 10, 0.0, rise=0.05, fall=1.5, gain=0.5)
            if m == note('Eb2'):
                M.add('perc', crash.play(122), t, 0.9)
                M.add('perc', timp.play(124, pitch=-4), t, 0.95)
                hold('low', cb, m, t, t + d, v - 10, 0.0, rise=0.05, fall=1.5, gain=0.7)
        elif part == 'horn':
            if d > 1.0:
                hold('brass', horn, m, t, t + d, v, ps(t), rise=0.08, fall=0.8, gain=0.85)
            else:
                M.add('brass', horn.play(m, v, dur=d * 1.05, release=0.3), t, 0.9, ps(t))
        elif part == 'settle':
            hold('warm', vc if m < note('G2') else vln, m + 12 * (m < note('Eb2')), t, t + d, v, 0.0,
                 rise=2.0, fall=1.0, gain=0.45)
