"""The Rope Breaks: still night on Brünnhilde's rock, and the three Norns go on throwing the golden rope of fate
between them, a white-hot head racing from one to the next and a gold whip cracking on out to the end of the
house each time it is caught.

But they sing now of Alberich and the Ring. Every note of the Ring (Donington 8) flashes gold along the rope with a
red glint running through it; then the Curse (13) sounds on the trombones and the rope turns blood red, red pulses
racing along it and the whole house throbbing red on its heavy low notes. The rope frays: dark gaps flicker
through it, more and more, the throws come faster and stutter, and with a crash it snaps. One white flash over the
whole house, and the two broken ends whip away to the two ends of the roofline and are gone.

The Twilight of the Gods (4) sounds on the horns, and at each of its phrases a Norn sinks into the earth, her grey
white collapsing inward in a ring, until the rock is empty. "Down to our mother!" Then only the night, the low
fire round the rock, and in the east, at the free end of Right, the first red of the coming day, red streaks
shooting from it along the house.

compose() holds every note; stage(), heat(), fire(), scene(), strand() and figure() are shared word for word by
the Prologue's scenes (see GD01)."""
import numpy as np
from pixelhome.audio import note
from pixelhome.fx import DT, hexc, light, smoothstep, nframes, keys, Flicker, smooth_noise, colormap
from pixelhome.leitmotifs import play

CODE = 'GD02'
TITLE = 'The Rope Breaks'
KIND = 'show'
DESCRIPTION = ('The Norns sing of the Ring and its curse, and the golden rope turns red and frays until it snaps. '
               'The broken ends whip away across the house and the Norns sink into the earth.')
VOICEOVER = ('The Norns sing of a ring of gold, and of a curse. '
             'The rope of fate begins to fray, and then it breaks.')

K = 1                                       # this scene's place on the Prologue's shared clock: T = t + 80 K
ROPE_BEAT = 0.42
T_THROWS = [0.4 + 3.1 * j for j in range(10)] + [31.4 + 1.6 * j for j in range(6)]
T_RING = 7.0
T_CURSE = 17.0
T_SNAP = 41.5
T_DOWN = 45.0                               # the Twilight of the Gods: a Norn sinks at each phrase
T_SINK = [45.0, 48.6, 52.2]
T_HINAB = 56.5
T_EAST = 62.0
T_STREAKS = [63.0, 66.0, 69.0, 71.5, 74.0, 76.5]
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
BLOOD = hexc('#c00010')
GOLD = hexc('#ffaa00')
RINGRED = hexc('#ff1800')

START = dict(night=0.55, stars=0.7, rock=0.32, fire=0.4, east=0.0, dawn=0.0, hue=0.0, day=0.0, rope=0.5)
END = dict(night=0.5, stars=0.6, rock=0.32, fire=0.4, east=0.35, dawn=0.0, hue=0.0, day=0.0, rope=0.0)
NORNS_START = (0.8, 0.8, 0.8)               # Left 0.5, Porch Front 0.5, Right 0.5; all gone by the end


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

    add(0.0, T_SNAP, 'Eb1', 62, 'pedal')
    for j, t0 in enumerate(T_THROWS):
        if t0 >= T_SNAP - 1.0:
            break
        v = 92 + int(20 * smoothstep(20, 40, t0))
        beat = ROPE_BEAT if t0 < 31 else 0.26
        for t, m, vv, d in play('norns_rope', t0, beat, 0, v):
            if t < T_SNAP:
                add(t, d, m, vv, 'rope', j)
    for t, m, v, d in play('ring', T_RING, 0.6, -12, 96):
        add(t, d, m, v, 'ring')
    for t, m, v, d in play('curse', T_CURSE, 0.55, 0, 112):
        add(t, d, m, v, 'curse')
    add(T_SNAP, 0.1, 'C1', 127, 'snap')
    for t, m, v, d in play('downfall', T_DOWN, 0.9, -12, 100):
        add(t, d, m, v, 'down')
    for j, t0 in enumerate(T_SINK + [T_HINAB]):
        add(t0, 0.6, ('Bb1', 'Ab1', 'Gb1', 'Eb1')[j], 96 - 6 * j, 'sink', j)
    add(T_EAST, D - T_EAST, 'Eb2', 58, 'east')
    for j, t0 in enumerate(T_STREAKS):
        for t, m, v, d in play('dawn', t0, 0.5, 0, 66 + 6 * j):
            if t < t0 + 2.0:
                add(t, d, m, v, 'streak', j)
    return sorted(N, key=lambda e: e[0])


def render(G, seed=2):
    F = nframes(D)
    out = np.zeros((F, G.N, 3))
    S = stage(G)
    d, L, nn = S['d'], S['L'], S['norns']
    N = compose()
    throws = sorted({e[5] for e in N if e[4] == 'rope'})
    ring = [e for e in N if e[4] == 'ring']
    curse = [e for e in N if e[4] == 'curse']
    lowc = sorted({e[0] for e in curse if e[2] < note('C3')})
    rng = np.random.default_rng(seed)
    gl_at = rng.uniform(nn[0], nn[2], len(ring))

    for f in range(F):
        t = f * DT
        T = t + 80 * K
        lv = {k: keys(t, [(0, START[k]), (T_HINAB, START[k]), (T_HINAB + 6, END[k])]) for k in START}
        fray = smoothstep(10, 40, t)
        red = smoothstep(T_CURSE, T_CURSE + 3, t)
        lv['rope'] = START['rope'] * (t < T_SNAP)
        lv['east'] = END['east'] * smoothstep(T_EAST, T_EAST + 10, t)
        fr = scene(S, T, dict(lv, rope=0.0))
        if lv['rope'] > 0:                  # the standing rope, fraying and reddening
            st = strand(S, nn[0], nn[2], 1.0, lv['rope'], T, fray)
            fr += st * (1 - red) + light(BLOOD, 1.2 * red * np.clip(st.max(1), 0, 1) ** (1 / 2.2))

        # throws, faster and stuttering as it frays
        for j in throws:
            t0 = T_THROWS[j]
            a = t - t0
            if not 0 <= a < 3.0 or t >= T_SNAP:
                continue
            i, k = PAIRS[j % 3]
            fly = (0.9 + 0.5 * (abs(i - k) == 2)) * (0.6 if t0 > 31 else 1.0)
            u = smoothstep(0, fly, a)
            if t0 > 25:
                u *= 0.85 + 0.15 * np.sin(2 * np.pi * 7 * a)
            lvl = 1.0 * np.exp(-max(a - fly, 0) / 0.9)
            st = strand(S, nn[i], nn[k], u, lvl, T, 0.7 * fray)
            fr += st * (1 - 0.6 * red) + light(BLOOD, 0.8 * red * lvl * (st.max(1) > 0.02))
            if a >= fly:
                w = a - fly
                out_dir = 1 if nn[k] >= nn[i] else -1
                pos = nn[k] + out_dir * 1900 * w
                past = (out_dir * (d - nn[k]) > 0) * (out_dir * (pos - d) > 0)
                col = ROPE if red < 0.5 else BLOOD
                fr += light(col, 1.0 * np.exp(-w / 0.7) * np.exp(-((d - pos) / 110) ** 2))
                fr += light(col, 0.8 * np.exp(-w / 0.9) * past * (0.4 + 0.6 * np.exp(-(out_dir * (pos - d)) / 700)))

        # the Ring: gold flashes along the rope, each with a red glint running through it
        for j, (t0, dur, m, v, part, k) in enumerate(ring):
            a = t - t0
            if 0 <= a < dur + 1.0:
                g = np.exp(-a / (dur + 0.4)) * smoothstep(0, 0.05, a)
                fr += light(GOLD, 1.0 * g * np.exp(-((d - gl_at[j]) / (40 + 80 * a)) ** 2))
                fr += light(RINGRED, 0.9 * g * np.exp(-((d - gl_at[j] - 500 * a) / 18) ** 2))

        # the Curse: red pulses racing along the rope, the whole house throbbing red on its low notes
        for t0, dur, m, v, part, k in curse:
            a = t - t0
            if 0 <= a < 1.6 and m >= note('C3'):
                pos = nn[0] + (nn[2] - nn[0]) * ((a / 1.2 + (m % 5) / 5) % 1)
                fr += light(BLOOD, 0.9 * np.exp(-a / 0.8) * np.exp(-((d - pos) / 50) ** 2))
        for t0 in lowc:
            a = t - t0
            if 0 <= a < 2.0:
                fr += light(BLOOD, 0.9 * np.exp(-a / 0.8))

        # the snap: one white flash, and the broken ends whip away to both ends of the house
        a = t - T_SNAP
        if 0 <= a < 3.0:
            fr += light(WHITE, 1.0 * np.exp(-a / 0.25))
            fr += light(ROPE, 0.9 * np.exp(-a / 1.0))
            fr += light(ORANGE, 0.6 * np.exp(-a / 1.8))
            mid = 0.5 * (nn[0] + nn[2])
            for side, lim in ((-1, 0.0), (1, L)):
                pos = mid + side * 1700 * (1 - np.exp(-a / 0.9))
                pos = max(pos, lim) if side < 0 else min(pos, lim)
                tail = (side * (d - mid) > 0) * (side * (pos - d) >= 0) * np.exp(-(side * (pos - d)) / 450)
                fr += light(ROPE, 1.4 * np.exp(-a / 1.5) * (0.35 + tail) * (side * (pos - d) >= 0) * (side * (d - mid) > 0))
                fr += light(HOT, 1.2 * np.exp(-a / 1.2) * np.exp(-((d - pos) / 70) ** 2))

        # the Norns: flaring as they sing, then sinking into the earth one by one, rings collapsing inward
        for n in range(3):
            ts = T_SINK[n]
            lvl = NORNS_START[n] * (1 - smoothstep(ts, ts + 2.5, t))
            if T_RING <= t < T_RING + 8 and n == 0 or T_CURSE <= t < T_CURSE + 11 and n == 1:
                lvl += 0.25 * (0.5 + 0.5 * np.sin(2 * np.pi * 1.3 * t))
            if t > 25 and t < ts:
                lvl += 0.15 * fray * np.sin(2 * np.pi * (3 + n) * t)
            a = t - ts
            if 0 <= a < 2.5:
                r = 900 * np.exp(-a / 0.6)
                fr += light(NORN, 1.0 * (1 - a / 2.5) * np.exp(-((np.abs(d - nn[n]) - r) / 130) ** 2))
                fr += light(NORN, 0.45 * np.exp(-a / 0.3))
            if lvl > 0.01:
                fr = figure(fr, S, nn[n], NORN, lvl, w=16.0 * (0.4 + 0.6 * (1 - smoothstep(ts, ts + 2.5, t))))
        a = t - T_HINAB
        if 0 <= a < 3.0:
            for p in nn:
                fr += light(NORN, 0.8 * np.exp(-a / 0.7) * np.exp(-((np.abs(d - p) - 500 * np.exp(-a / 0.5)) / 50) ** 2))

        # the first red of day: streaks shooting from the east along the house
        for j, t0 in enumerate(T_STREAKS):
            a = t - t0
            if 0 <= a < 3.0:
                pos = L - 900 * a
                fr += light(EAST, (0.75 + 0.04 * j) * np.exp(-a / 1.4) * np.exp(-((d - pos) / 260) ** 2))
                fr += light(DAWN(0.2), 0.5 * np.exp(-a / 0.8) * S['east'])
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

    for name, gain, rev in (('low', 0.28, 0.25), ('strings', 0.22, 0.35), ('brass', 0.26, 0.3), ('perc', 0.26, 0.3),
                            ('harp', 0.2, 0.4), ('winds', 0.22, 0.35), ('fx', 0.1, 0.3)):
        M.bus(name, gain=gain, reverb=rev)
    vln = M.sampler('Strings/Violin Section/Spic/*.wav', tune=-12)
    vc = M.sampler('Strings/Cello Section/susvib/*.wav', tune=-12)
    ctrem = M.sampler('Strings/Cello Section/trem/*.wav', tune=-12)
    cb = M.sampler('Strings/Solo Contrabass/SusNV/*.wav', tune=-12)
    harp = M.sampler('Strings/Harp/*.wav')
    bsn = M.sampler('Woodwinds/Bassoon/sus/*.wav', tune=-12)
    horn = M.sampler('Brass/F Horn/sus/*.wav', tune=-12)
    tbn = M.sampler('Brass/Tenor Trombone/sus/*.wav', tune=-12)
    tuba = M.sampler('Brass/Tuba/sus/*.wav', tune=-12)
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

    S = stage(G)
    nn = [pan_at(p) for p in S['norns']]
    east = pan_at(S['L'] - 100)
    for t, d, m, v, part, k in compose():
        if part == 'pedal':
            hold('low', ctrem, m + 12, t, t + d, v, 0.0, rise=2.0, fall=0.3, gain=0.45)
        elif part == 'rope':
            i, j = PAIRS[k % 3]
            pa = 0.5 * (nn[i] + nn[j])
            if m >= note('C5'):
                M.add('harp', harp.play(m - 12, v - 8), t, 0.8, pa)
            elif m >= note('C3'):
                M.add('strings', vln.play(m, v - 6), t, 0.7, pa)
            else:
                M.add('low', cb.play(m, v - 10, dur=d * 1.1, release=0.2), t, 0.6, pa)
        elif part == 'ring':
            if d > 1.0:
                hold('winds', bsn, m, t, t + d, v, nn[0], rise=0.2, fall=0.8, gain=0.8)
            else:
                M.add('winds', bsn.play(m, v, dur=d * 1.05, release=0.25), t, 0.9, nn[0])
        elif part == 'curse':
            if d > 1.2:
                hold('brass', tbn, m, t, t + d, v, nn[1], rise=0.15, fall=1.0, gain=0.85)
            else:
                M.add('brass', tbn.play(m, v, dur=d * 1.05, release=0.3), t, 0.9, nn[1])
            if m < note('C3'):
                M.add('perc', timp.play(v, pitch=-4), t, 0.8)
                M.add('low', tuba.play(m, v - 10, dur=d * 1.05, release=0.3), t, 0.7)
        elif part == 'snap':
            M.add('perc', crash.play(v), t, 1.0)
            M.add('perc', timp.play(v, pitch=-6), t, 1.0)
            M.add('perc', gong.play(115), t, 0.7)
            M.add('fx', whoosh(1.4, 6000, 300, 0.8, seed=41), t, 0.9, -0.8)
            M.add('fx', whoosh(1.4, 6000, 300, 0.8, seed=42), t, 0.9, 0.8)
        elif part == 'down':
            if d > 1.0:
                hold('brass', horn, m, t, t + d, v, 0.0, rise=0.2, fall=1.2, gain=0.85)
            else:
                M.add('brass', horn.play(m, v, dur=d * 1.05, release=0.3), t, 0.9)
            M.add('low', tuba.play(m - 24, v - 16, dur=d * 1.05, release=0.3), t, 0.55)
        elif part == 'sink':
            p = nn[k] if k < 3 else 0.0
            M.add('perc', roll.play(v, pitch=-7, dur=2.0), t - 0.4, 0.6, p)
            M.add('low', cb.play(m, v, dur=2.4, release=0.8), t, 0.8, p)
            M.add('harp', harp.play(m + 24, 70), t, 0.7, p)
        elif part == 'east':
            hold('strings', vc, m, t, t + d, v, east * 0.6, rise=6.0, fall=1.0, gain=0.5)
        elif part == 'streak':
            M.add('strings', vc.play(m + 12, v, dur=d * 1.1, release=0.4), t, 0.7, east)
