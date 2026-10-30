"""The Norns: night on Brünnhilde's rock. The porch is the rock, its summit the middle of Porch Front, with the
magic fire burning low round it; the wings and the Side are the night sky, deep indigo and violet, alive with
stars. Three great chords in E flat minor slam over the whole house, violet, blue, violet.

Then the three Norns rise out of the dark, grey white, on the middle of Left, the summit and the middle of Right,
and begin to throw the golden rope of fate between them. Every rippling figure of the rope (Donington 10) is a
throw: a white-hot head races from one Norn to the next, laying a fresh strand of gold the whole way, and when it
is caught a gold whip cracks on past the catcher out to the end of the house. The long throw from Right back to
Left crosses every corner of the porch. Strand on strand, the rope comes to span the house, shimmering.

Each Norn sings in turn (the Norns, 23): the singer flares and grey white rings roll out from her over the house.
The first sings of the world ash, and the gods' castle rises: every note of Valhalla (63) slams one whole run in
gold white over deep blue, run after run round the roofline. The third sings of Loge, and the fire round the rock
leaps up: every figure of Loge (20) throws a tongue of flame racing out along the roofline from the rock, left and
right in turn. The rope keeps flying, faster, to the end.

compose() holds every note; stage(), heat(), fire(), scene(), strand() and figure() are the rock, the sky and the
rope, shared word for word by the Prologue's scenes (and GD13-GD14, which come back to the rock) on a clock
T = t + 80 K that runs on from scene to scene."""
import numpy as np
from pixelhome.audio import note
from pixelhome.fx import DT, hexc, light, smoothstep, nframes, keys, Flicker, smooth_noise, colormap
from pixelhome.leitmotifs import play

CODE = 'GD01'
TITLE = 'The Norns'
KIND = 'show'
DESCRIPTION = ('Night on the rock. Three grey sisters, the Norns, throw a golden rope of fate back and forth across '
               'the whole house, singing of the gods, their castle and the fire.')
VOICEOVER = ('Night, on the mountain. Three sisters spin the rope of fate, and throw it from hand to hand. '
             'This is the Twilight of the Gods.')

K = 0                                       # this scene's place on the Prologue's shared clock: T = t + 80 K
T_CHORDS = [0.5, 3.0, 5.5]                  # the awakening chords
T_RISE = [8.0, 9.0, 10.0]                   # the Norns rise
ROPE_BEAT = 0.42
T_THROWS = [12.0 + 3.1 * j for j in range(22)]   # every figure of the rope
T_SING = [(14.0, 0), (37.0, 1), (58.0, 2)]  # each Norn's song (time, which Norn)
T_VALHALLA = 24.0
T_LOGE = [46.0 + 1.6 * j for j in range(6)]
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

START = dict(night=0.55, stars=0.7, rock=0.32, fire=0.4, east=0.0, dawn=0.0, hue=0.0, day=0.0, rope=0.0)
END = dict(night=0.55, stars=0.7, rock=0.32, fire=0.4, east=0.0, dawn=0.0, hue=0.0, day=0.0, rope=0.5)
NORNS_END = (0.8, 0.8, 0.8)                 # the three Norns' levels at the end (Left 0.5, Porch Front 0.5, Right 0.5)


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

    for k, (t0, ch) in enumerate(zip(T_CHORDS, (('Eb2', 'Eb3', 'Gb3', 'Bb3'), ('B1', 'B2', 'Eb3', 'Gb3'),
                                                 ('Eb2', 'Eb3', 'Gb3', 'Bb3')))):
        for m in ch:
            add(t0, 2.2, m, 118 - 4 * k, 'chord', k)
    add(0.0, D, 'Eb1', 60, 'pedal')
    for j, t0 in enumerate(T_THROWS):
        if t0 > D - 2.5:
            break
        v = 84 + int(18 * smoothstep(40, 75, t0))
        for t, m, vv, d in play('norns_rope', t0, ROPE_BEAT, 0, v):
            add(t, d, m, vv, 'rope', j)
    for t0, n in T_SING:
        for t, m, v, d in play('norns', t0, 0.55, -12, 96):
            add(t, d, m, v, 'sing', n)
    for t, m, v, d in play('valhalla', T_VALHALLA, 0.75, -12, 110):
        add(t, d, m, v, 'valhalla')
    for j, t0 in enumerate(T_LOGE):
        for t, m, v, d in play('loge', t0, 0.2, 12, 100):
            add(t, d, m, v, 'loge', j)
    for t0 in T_RISE:
        add(t0, 0.4, 'Eb2', 96, 'rise')
    return sorted(N, key=lambda e: e[0])


def render(G, seed=1):
    F = nframes(D)
    out = np.zeros((F, G.N, 3))
    S = stage(G)
    d, L, nn = S['d'], S['L'], S['norns']
    N = compose()
    throws = [t0 for t0 in T_THROWS if t0 <= D - 2.5]
    sing = [e for e in N if e[4] == 'sing']
    vnotes = sorted({e[0] for e in N if e[4] == 'valhalla'})
    runs = ['Porch Front', 'Left', 'Right', 'Porch Left', 'Porch Right', 'Side', 'Left', 'Right']

    for f in range(F):
        t = f * DT
        T = t + 80 * K
        lv = dict(START)
        lv['rope'] = 0.5 * smoothstep(throws[0] + 1.0, throws[3] + 1.0, t)
        lv['fire'] += 0.35 * sum(np.exp(-max(t - t0, 0) / 0.8) * (t >= t0) for t0 in T_LOGE)
        fr = scene(S, T, lv)

        # the awakening chords: the whole house slams violet, blue, violet
        for k, t0 in enumerate(T_CHORDS):
            a = t - t0
            if 0 <= a < 2.4:
                col = CHORD if k != 1 else GODS
                fr += light(col, 0.95 * smoothstep(0, 0.05, a) * (1 - smoothstep(1.4, 2.4, a)) * (0.75 + 0.25 * np.exp(-a / 0.4)))
                fr += light(WHITE, 0.5 * np.exp(-a / 0.1))

        # every figure of the rope is a throw: a white-hot head laying fresh gold, then a whip past the catcher
        for j, t0 in enumerate(throws):
            a = t - t0
            if not 0 <= a < 3.0:
                continue
            i, k = PAIRS[j % 3]
            fly = 0.9 + 0.5 * (abs(i - k) == 2)
            u = smoothstep(0, fly, a)
            lvl = 1.0 * np.exp(-max(a - fly, 0) / 0.9)
            fr += strand(S, nn[i], nn[k], u, lvl, T)
            if a >= fly:
                w = a - fly
                out_dir = 1 if nn[k] >= nn[i] else -1
                pos = nn[k] + out_dir * 1900 * w
                past = (out_dir * (d - nn[k]) > 0) * (out_dir * (pos - d) > 0)
                fr += light(ROPE, 1.0 * np.exp(-w / 0.7) * np.exp(-((d - pos) / 110) ** 2))
                fr += light(ROPE, 0.8 * np.exp(-w / 0.9) * past * (0.4 + 0.6 * np.exp(-(out_dir * (pos - d)) / 700)))
                fr += light(HOT, 0.8 * np.exp(-w / 0.12) * np.exp(-((d - nn[k]) / 25) ** 2))

        # Valhalla: every note slams one whole run gold white over deep blue
        for j, t0 in enumerate(vnotes):
            a = t - t0
            if 0 <= a < 1.6:
                run = G.seg_of == runs[j % len(runs)]
                fr += light(GODS, 0.75 * np.exp(-a / 0.9) * S['sky'])
                fr += light(VALHALLA, 1.0 * np.exp(-a / 0.55) * run)

        # Loge: a tongue of flame racing out along the roofline from the rock, left and right in turn
        for j, t0 in enumerate(T_LOGE):
            a = t - t0
            if 0 <= a < 1.8:
                side = -1 if j % 2 == 0 else 1
                start = at(G, 'Porch Left', 0.0) if side < 0 else at(G, 'Porch Right', 1.0)
                pos = start + side * 1300 * (1 - np.exp(-a / 0.5))
                q = np.clip(0.6 + 0.4 * S['fl'](T), 0, 1)
                fr += light(FIRE(q), 1.2 * np.exp(-a / 1.0) * np.exp(-((d - pos) / 220) ** 2))
                fr += fire(S, T, 0.0, 1.0 * np.exp(-a / 0.8), boost=0.6)
                fr += light(AMBER, 0.6 * np.exp(-a / 0.6) * smoothstep(0, 1, side * (d - start) / 50)
                            * smoothstep(pos + side * 40, pos - side * 400, d) * (side * (pos - d) > 0))

        # the Norns: rising, standing, and flaring as each sings, grey white rings rolling out from her
        for n in range(3):
            lvl = 0.8 * smoothstep(T_RISE[n], T_RISE[n] + 1.2, t)
            for t0, dur, m, v, part, who in sing:
                if who == n and 0 <= t - t0 < dur + 0.8:
                    a = t - t0
                    lvl += 0.35 * np.exp(-a / (dur + 0.3))
                    if a < 2.0:
                        r = 900 * (1 - np.exp(-a / 0.6))
                        fr += light(NORN, 0.7 * np.exp(-a / 0.8) * np.exp(-((np.abs(d - nn[n]) - r) / 70) ** 2))
            a = t - T_RISE[n]
            if 0 <= a < 1.5:
                fr += light(NORN, 0.9 * np.exp(-a / 0.4) * np.exp(-((np.abs(d - nn[n]) - 500 * a) / 50) ** 2))
            if lvl > 0:
                fr = figure(fr, S, nn[n], NORN, min(lvl, 1.1))
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

    for name, gain, rev in (('low', 0.25, 0.25), ('strings', 0.2, 0.35), ('brass', 0.23, 0.3), ('perc', 0.22, 0.3),
                            ('harp', 0.18, 0.4), ('fire', 0.14, 0.3)):
        M.bus(name, gain=gain, reverb=rev)
    vln = M.sampler('Strings/Violin Section/Spic/*.wav', tune=-12)
    vla = M.sampler('Strings/Viola Section/susvib/*.wav', tune=-12)
    vc = M.sampler('Strings/Cello Section/susvib/*.wav', tune=-12)
    cb = M.sampler('Strings/Solo Contrabass/SusNV/*.wav', tune=-12)
    harp = M.sampler('Strings/Harp/*.wav')
    bsn = M.sampler('Woodwinds/Bassoon/sus/*.wav', tune=-12)
    horn = M.sampler('Brass/F Horn/sus/*.wav', tune=-12)
    tbn = M.sampler('Brass/Tenor Trombone/sus/*.wav', tune=-12)
    tuba = M.sampler('Brass/Tuba/sus/*.wav', tune=-12)
    glock = M.sampler('Percussion/Glock/*.wav')
    timp = M.hits('Percussion/Timpani/Timpani1_Hit*.wav')
    roll = M.hits('Percussion/Timpani/Rolls/*.wav')
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

    S = stage(G)
    nn = [pan_at(p) for p in S['norns']]
    for t, d, m, v, part, k in compose():
        if part == 'chord':
            if m < note('C3'):
                hold('low', tuba, m, t, t + d, v, 0.0, rise=0.05, fall=1.2, gain=0.9)
                if m == min(e[2] for e in compose() if e[4] == 'chord' and e[5] == k):
                    M.add('perc', timp.play(v, pitch=-5), t, 0.9)
                    M.add('perc', gong.play(90), t, 0.4)
            else:
                hold('brass', tbn if m < note('G3') else horn, m, t, t + d, v, 0.0, rise=0.05, fall=1.2, gain=0.75)
        elif part == 'pedal':
            hold('low', cb, m + 12, t, t + d, v, 0.0, rise=6.0, fall=2.0, gain=0.5)
        elif part == 'rope':
            i, j = PAIRS[k % 3]
            u = min(1.0, (t - T_THROWS[k]) / (0.9 + 0.5 * (abs(i - j) == 2)))
            pa = nn[i] + (nn[j] - nn[i]) * u
            if m >= note('C5'):
                M.add('harp', harp.play(m - 12, v - 8), t, 0.8, pa)
            elif m >= note('C3'):
                M.add('strings', vln.play(m, v - 6), t, 0.7, pa)
            else:
                M.add('low', cb.play(m, v - 10, dur=d * 1.1, release=0.2), t, 0.6, pa)
        elif part == 'sing':
            p = nn[k]
            if d > 1.0:
                hold('strings', vc if m < note('D4') else vla, m, t, t + d, v, p, rise=0.3, fall=1.0, gain=0.8)
            else:
                M.add('strings', vla.play(m, v, dur=d * 1.1, release=0.3), t, 0.8, p)
            if m >= note('Bb3'):
                M.add('low', bsn.play(m - 12, v - 16, dur=d * 1.05, release=0.3), t, 0.5, p)
        elif part == 'valhalla':
            if d > 1.0:
                hold('brass', horn, m, t, t + d, v, 0.0, rise=0.15, fall=1.0, gain=0.8)
            else:
                M.add('brass', horn.play(m, v, dur=d * 1.05, release=0.3), t, 0.85)
            M.add('low', tuba.play(m - 12, v - 10, dur=d * 1.05, release=0.3), t, 0.6)
        elif part == 'loge':
            side = -0.7 if k % 2 == 0 else 0.7
            M.add('fire', vln.play(m - 12, v), t, 0.7, side)
            if m >= note('Bb5'):
                M.add('fire', glock.play(m - 12, v - 20), t, 0.4, side)
        elif part == 'rise':
            n = int(round((t - T_RISE[0]) / (T_RISE[1] - T_RISE[0])))
            M.add('perc', roll.play(v, pitch=-6, dur=1.6), t - 0.6, 0.5, nn[n])
            M.add('harp', harp.play(note('Eb3') + 7 * n, 80), t, 0.8, nn[n])
