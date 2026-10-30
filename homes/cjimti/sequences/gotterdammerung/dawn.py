"""Dawn: the Norns are gone and the night is lifting off Brünnhilde's rock. The red in the east, at the free end of
Right, swells; then the cellos play the Dawn motif (Donington 49), and every note of it is a wave of colour that
leaves the east and races the whole length of the house to the far end of the Side, laying the new colour behind
it. Each time the motif comes round it is fuller and the colour has climbed: deep red, then orange, then gold,
then white-gold, while the night drains out, the stars go out and the sky turns from indigo to blue.

On the summit two figures rise out of the rock in bursts of light: Brünnhilde in silver and gold on her motif (88),
and Siegfried in emerald. At the climax the whole orchestra has the Dawn and the house blazes: gold-white sweeps
crossing both ways, timpani on every downbeat, every run in full morning, before it settles into the bright day
with the two of them standing on the summit.

compose() holds every note; stage(), heat(), fire(), scene(), strand() and figure() are shared word for word by
the Prologue's scenes (see GD01)."""
import numpy as np
from pixelhome.audio import note
from pixelhome.fx import DT, hexc, light, smoothstep, nframes, keys, Flicker, smooth_noise, colormap
from pixelhome.leitmotifs import play

CODE = 'GD03'
TITLE = 'Dawn'
KIND = 'show'
DESCRIPTION = ('Daybreak over the mountain: wave after wave of colour races across the house from the east, red '
               'to gold to white, until Siegfried and Brünnhilde stand on the summit in full morning.')
VOICEOVER = ('The sun comes up over the mountain. Siegfried and Brünnhilde wake to a new day.')

K = 2                                       # this scene's place on the Prologue's shared clock: T = t + 80 K
DBEAT = 0.55
T_DAWN = [(2.0, 0.08, 74), (14.0, 0.3, 88), (26.0, 0.55, 100), (38.0, 0.8, 110)]   # (time, hue it lays, velocity)
T_BRUNN = 47.0
T_RISE_B = 47.0                             # Brünnhilde rises
T_RISE_S = 52.0                             # Siegfried rises
T_CLIMAX = [56.0, 62.6]                     # the full orchestra's Dawn
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

START = dict(night=0.5, stars=0.6, rock=0.32, fire=0.4, east=0.35, dawn=0.0, hue=0.0, day=0.0, rope=0.0)
END = dict(night=0.0, stars=0.0, rock=0.35, fire=0.15, east=0.0, dawn=0.75, hue=0.62, day=0.3, rope=0.0)
SIEGFRIED_END = ('Porch Front', 0.35, 0.85)     # (segment, u, level)
BRUNNHILDE_END = ('Porch Front', 0.6, 0.9)


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

    add(0.0, T_DAWN[3][0], 'Bb1', 58, 'pedal')
    for k, (t0, hue, v) in enumerate(T_DAWN):
        for t, m, vv, d in play('dawn', t0, DBEAT, 12 * (k >= 2), v):
            add(t, d, m, vv, 'dawn', k)
    for t, m, v, d in play('brunnhilde', T_BRUNN, 0.6, -5, 104):
        add(t, d, m, v, 'brunn')
    for k, t0 in enumerate(T_CLIMAX):
        for t, m, v, d in play('dawn', t0, DBEAT, 0, 122):
            add(t, d, m, v, 'climax', k)
        for j in range(4):
            add(t0 + j * 3 * DBEAT, 0.3, 'Bb1', 118, 'timp', k)
    for m in ('Bb1', 'F2', 'Bb2', 'D3', 'F3', 'Bb3'):
        add(T_SETTLE, D - T_SETTLE, m, 70, 'settle')
    add(T_RISE_S, 0.4, 'Bb2', 100, 'riseS')
    add(T_RISE_B, 0.4, 'D3', 100, 'riseB')
    return sorted(N, key=lambda e: e[0])


def render(G, seed=3):
    F = nframes(D)
    out = np.zeros((F, G.N, 3))
    S = stage(G)
    d, L = S['d'], S['L']
    N = compose()
    waves = [(e[0], T_DAWN[e[5]][1], 0.75 + 0.08 * e[5]) for e in N if e[4] == 'dawn']
    waves += [(e[0], 1.0, 1.0) for e in N if e[4] == 'climax']
    waves.sort()
    climax = [e for e in N if e[4] == 'climax']
    brunn = sorted({e[0] for e in N if e[4] == 'brunn'})
    p_s, p_b = at(G, *SIEGFRIED_END[:2]), at(G, *BRUNNHILDE_END[:2])
    speed = 2100.0

    for f in range(F):
        t = f * DT
        T = t + 80 * K
        prog = smoothstep(T_DAWN[0][0], T_DAWN[3][0] + 8, t)
        lv = dict(START)
        lv['night'] = START['night'] * (1 - prog)
        lv['stars'] = START['stars'] * (1 - smoothstep(0, 26, t))
        lv['east'] = keys(t, [(0, START['east']), (T_DAWN[0][0], 0.6), (T_DAWN[2][0], 0.5), (T_CLIMAX[0], 0.0)])
        lv['fire'] = keys(t, [(0, START['fire']), (T_CLIMAX[0], END['fire'])])
        lv['rock'] = keys(t, [(0, START['rock']), (T_CLIMAX[0], END['rock'])])
        # the hue the sky has reached: the last wave to have crossed the whole house
        crossed = [h for t0, h, g in waves if t - t0 > L / speed]
        lv['hue'] = keys(t, [(0, 0.0), (T_DAWN[3][0] + 6, 0.8), (T_SETTLE, 0.75), (D, END['hue'])])
        lv['dawn'] = keys(t, [(0, 0.0), (T_DAWN[0][0], 0.1), (T_DAWN[3][0] + 6, 0.75), (D, END['dawn'])])
        lv['day'] = keys(t, [(0, 0.0), (T_DAWN[2][0], 0.0), (T_CLIMAX[0], 0.25), (D, END['day'])])
        fr = scene(S, T, lv)

        # every note of the Dawn: a wave of the new colour leaving the east and racing to the end of the Side
        for t0, hue, g in waves:
            a = t - t0
            if not 0 <= a < L / speed + 1.2:
                continue
            front = L - speed * a
            fade = 1 - smoothstep(L / speed, L / speed + 1.2, a)
            col = DAWN(np.array([hue]))[0]
            band = np.exp(-((d - front) / 240) ** 2)
            behind = (d >= front) * np.exp(-(d - front) / 900)
            fr += light(col, g * fade * (band + 0.6 * behind))
            fr += light(HOT if hue > 0.5 else col, 0.7 * g * fade * np.exp(-((d - front) / 30) ** 2))

        # the climax: sweeps crossing both ways and the house flashing gold-white on every downbeat
        for t0, dur, m, v, part, k in climax:
            a = t - t0
            if 0 <= a < 1.4 and m == min(e[2] for e in climax if e[0] == t0):
                pos = speed * 0.8 * a
                fr += light(SUN, 0.9 * np.exp(-a / 0.6) * np.exp(-((d - pos) / 180) ** 2))
                fr += light(SUN, 0.45 * np.exp(-a / 0.35))

        # Brünnhilde's motif: silver and gold bursts out from the summit
        for t0 in brunn:
            a = t - t0
            if 0 <= a < 1.8:
                r = 1100 * (1 - np.exp(-a / 0.6))
                fr += light(BRUNNHILDE, 0.8 * np.exp(-a / 0.7) * np.exp(-((np.abs(d - p_b) - r) / 90) ** 2))
                fr += light(GLINT, 0.6 * np.exp(-a / 0.4) * np.exp(-((np.abs(d - p_b) - 0.7 * r) / 40) ** 2))

        # the two of them rise out of the rock in bursts of light
        for p, col, t0, lvl_end in ((p_b, BRUNNHILDE, T_RISE_B, BRUNNHILDE_END[2]),
                                    (p_s, SIEGFRIED, T_RISE_S, SIEGFRIED_END[2])):
            if t < t0 - 0.2:
                continue
            a = t - t0
            lvl = lvl_end * smoothstep(-0.2, 1.0, a)
            if 0 <= a < 1.6:
                fr += light(col, 1.0 * np.exp(-a / 0.35) * np.exp(-((d - p) / 70) ** 2))
                fr += light(col, 0.7 * np.exp(-a / 0.6) * np.exp(-((np.abs(d - p) - 900 * a) / 80) ** 2))
            fr = figure(fr, S, p, col, lvl)
            if col is SIEGFRIED:
                fr += light(HEAD, 0.7 * lvl * np.exp(-((d - p) / 6) ** 2))
            else:
                fr += light(GLINT, 0.5 * lvl * np.exp(-((d - p - 9) / 5) ** 2))
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

    for name, gain, rev in (('low', 0.34, 0.25), ('strings', 0.32, 0.35), ('brass', 0.34, 0.3), ('perc', 0.3, 0.3),
                            ('harp', 0.24, 0.4), ('warm', 0.3, 0.4)):
        M.bus(name, gain=gain, reverb=rev)
    vc = M.sampler('Strings/Cello Section/susvib/*.wav', tune=-12)
    vln = M.sampler('Strings/Violin Section/susVib/*.wav', tune=-12)
    cb = M.sampler('Strings/Solo Contrabass/SusNV/*.wav', tune=-12)
    harp = M.sampler('Strings/Harp/*.wav')
    horn = M.sampler('Brass/F Horn/sus/*.wav', tune=-12)
    tpt = M.sampler('Brass/Trumpet/sus/*.wav', tune=-12)
    tbn = M.sampler('Brass/Tenor Trombone/sus/*.wav', tune=-12)
    timp = M.hits('Percussion/Timpani/Timpani1_Hit*.wav')
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

    S = stage(G)
    east = pan_at(S['L'] - 100)
    sb = pan_at(at(G, *BRUNNHILDE_END[:2]))
    ss = pan_at(at(G, *SIEGFRIED_END[:2]))
    for t, d, m, v, part, k in compose():
        if part == 'pedal':
            hold('low', cb, m + 12, t, t + d, v, east * 0.4, rise=4.0, fall=2.0, gain=0.5)
        elif part == 'dawn':
            p = east * (1 - 0.25 * k)
            hold('strings', vc, m, t, t + d * 0.95, v, p, rise=0.15, fall=0.6, gain=0.8)
            if k >= 2:
                M.add('brass', horn.play(m - 12, v - 12, dur=d * 1.05, release=0.3), t, 0.6, p)
            if k == 3:
                M.add('harp', harp.play(m, v - 20), t, 0.6, p)
        elif part == 'brunn':
            if d > 1.0:
                hold('brass', horn, m, t, t + d, v, sb, rise=0.15, fall=1.0, gain=0.8)
            else:
                M.add('brass', horn.play(m, v, dur=d * 1.05, release=0.3), t, 0.85, sb)
            M.add('strings', vln.play(m, v - 20, dur=d * 1.1, release=0.3), t, 0.5, sb)
        elif part == 'climax':
            hold('brass', tbn if m < note('F3') else horn, m, t, t + d * 0.95, v, 0.0, rise=0.08, fall=0.6, gain=0.75)
            hold('strings', vln, m + 12, t, t + d * 0.95, v - 10, 0.0, rise=0.08, fall=0.6, gain=0.55)
            if m >= note('Bb3'):
                M.add('brass', tpt.play(m, v - 14, dur=d * 1.05, release=0.3), t, 0.55)
        elif part == 'timp':
            M.add('perc', timp.play(v, pitch=-2), t, 0.9)
            if t in T_CLIMAX:
                M.add('perc', crash.play(110), t, 0.7)
        elif part == 'settle':
            hold('warm', vc if m < note('D3') else vln, m, t, t + d, v, 0.0, rise=2.0, fall=1.0, gain=0.5)
        elif part == 'riseS':
            M.add('harp', harp.play(m + 12, 96), t, 0.9, ss)
            M.add('brass', horn.play(m, 90, dur=1.2, release=0.4), t, 0.6, ss)
        elif part == 'riseB':
            M.add('harp', harp.play(m + 12, 96), t, 0.9, sb)
