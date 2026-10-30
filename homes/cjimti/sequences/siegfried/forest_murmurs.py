"""Forest Murmurs: broad day outside Fafner's cave, and Siegfried lying under the lime tree at Left 0.5. The whole
house is the forest, alive: the Forest Murmurs (Donington 29) ripple in the strings, and every phrase sends a
green and gold wave rolling the length of the roofline, one way and then the other, the waves crossing and
flashing where they meet, while the sun shafts drift through the trees.

He wonders about his mother: innocent delight (28) sparkles in the violins as gold glitter all round him,
spreading out over Left and Side. Then from the far end of the house a hot magenta point flicks into the trees:
the Woodbird. On every note of its song (27) it darts a hop along the roofline, white at its heart, trailing
magenta, wings flickering; on its call (27a) each landing sends a magenta ring out through the green. It sings
three times, ranging over Right and the porch, and the forest swells under it, green and gold, until it settles
at Right 0.3 and looks at him.

compose() holds every note; stage(), forest(), figure() and sparks() are the forest and the cave, shared word for
word by Act II's scenes on a clock that runs on from scene to scene."""
import numpy as np
from pixelhome.audio import note
from pixelhome.fx import DT, hexc, light, smoothstep, nframes, keys, Flicker, smooth_noise
from pixelhome.leitmotifs import play

CODE = 'SF15'
TITLE = 'Forest Murmurs'
KIND = 'show'
DESCRIPTION = ('Siegfried lies under a tree and the whole forest comes alive in rolling waves of green and gold. '
               'A magenta bird darts through the branches, singing to him.')
VOICEOVER = ('Siegfried lies under a linden tree and listens to the forest. '
             'A little bird is singing to him.')

K = 4                                       # this scene's place on Act II's shared clock: T = t + 80 K
MURMUR = 0.85                               # quarter note of the Forest Murmurs
T_MURMUR = [0.5 + 5.0 * j for j in range(16)]   # every phrase, 5 s apart
T_DELIGHT = [17.0, 21.0]                    # innocent delight, the violins
T_BIRD_IN = 29.0                            # the Woodbird flicks in at the free end of Right
T_SONG = [30.0, 42.0, 54.0]                 # its song
T_CALL = [37.5, 49.5, 61.5]                 # its call
T_SETTLE = 66.0
D = 80.0

NIGHT = hexc('#14a878')
MOON = hexc('#6080ff')
DAY = hexc('#18a020')
SUN = hexc('#ffd040')
CAVE = hexc('#8a2000')
SCALE = hexc('#c88a20')
EYE = hexc('#ff0000')
STONE = hexc('#8a8a80')
BLOOD = hexc('#c00010')
GOLD = hexc('#ffaa00')
ALBERICH = hexc('#ff1000')
MUD = hexc('#5a1200')
WHITE = hexc('#ffffff')
SIEGFRIED = hexc('#00ff40')
HEAD = hexc('#e8ffe8')
BIRD = hexc('#ff30d0')

START = dict(night=0.2, day=0.7, shafts=0.75, cave=0.35, eyes=0.0)        # where SF14 left the forest: day
END = dict(night=0.2, day=0.7, shafts=0.75, cave=0.35, eyes=0.0)          # where SF16 picks it up
TREE_AT = 0.5                               # the lime tree, on Left
BIRD_AT = 0.3                               # where the Woodbird settles, on Right


def at(G, seg, u):
    """Path distance u of the way along a segment."""
    s = G.pd[G.seg[seg]]
    return float(s.min() + u * (s.max() - s.min()))


def stage(G):
    """The forest outside Fafner's cave as profiles over the house: the porch is the cave mouth (darkest at the
    back, the middle of Porch Front), Left, Right and Side the trees, with two eyes on Porch Front."""
    d = G.pd
    rng = np.random.default_rng(1857)       # the same trees and light in every scene, so the cuts match
    porch = np.isin(G.seg_of, ['Porch Left', 'Porch Front', 'Porch Right'])
    mid = at(G, 'Porch Front', 0.5)
    return dict(
        d=d, mid=mid, porch=porch,
        trees=(~porch) * (0.6 + 0.4 * smooth_noise(rng, d, 35.0)),
        mouth=porch * (0.35 + 0.65 * np.exp(-((d - mid) / 160) ** 2)),
        eyes=np.exp(-((d - at(G, 'Porch Front', 0.4)) / 5) ** 2) + np.exp(-((d - at(G, 'Porch Front', 0.6)) / 5) ** 2),
        edge=porch * (1 - np.exp(-((d - mid) / 220) ** 2)),
        shaft_at=rng.uniform(0, d.max(), 9), shaft_v=rng.uniform(-14, 14, 9), shaft_w=rng.uniform(25, 60, 9),
        leaf=Flicker(rng, G.N, 0.1, 0.6),
        smoulder=Flicker(rng, G.N, 0.3, 1.5),
    )


def forest(S, T, lv):
    """The forest at shared time T with levels lv (night, day, shafts, cave, eyes)."""
    d, leaf = S['d'], S['leaf'](T)
    fr = light(NIGHT, lv['night'] * S['trees'] * (0.85 + 0.15 * leaf))
    fr += light(DAY, lv['day'] * S['trees'] * (0.8 + 0.2 * leaf))
    fr += light(NIGHT, 0.4 * (lv['night'] + lv['day']) * S['edge'])
    L = d.max()
    shafts = np.zeros_like(d)
    for p, v, w in zip(S['shaft_at'], S['shaft_v'], S['shaft_w']):
        c = (p + v * T) % L
        shafts += np.exp(-((d - c) / w) ** 2)
    shafts *= ~S['porch']
    fr += light(MOON, lv['shafts'] * (1 - min(1.0, 2 * lv['day'])) * shafts)
    fr += light(SUN, lv['shafts'] * min(1.0, 2 * lv['day']) * shafts)
    fr += light(CAVE, lv['cave'] * S['mouth'] * (0.75 + 0.25 * S['smoulder'](T)))
    fr += light(EYE, lv['eyes'] * S['eyes'])
    return fr


def figure(fr, S, p, col, lvl, w=16.0):
    """A person at path distance p: a body that stands in front of the forest, and a halo."""
    body = np.exp(-((S['d'] - p) / w) ** 2)
    fr = fr * (1 - 0.85 * min(1.0, lvl / 0.2) * body)[:, None]
    return fr + light(col, lvl * body) + light(col, 0.35 * lvl * np.exp(-((S['d'] - p) / (3 * w)) ** 2))


def sparks(S, hits, t, seed, n=14, reach=1.0):
    """Bursts [(time, strength, where)]: each throws n sparks both ways along the roofline, -> perceptual."""
    d = S['d']
    out = np.zeros_like(d)
    for i, (th, s, p0) in enumerate(hits):
        a = t - th
        if not 0 <= a < 1.6:
            continue
        rng = np.random.default_rng(seed * 1000 + i)
        v = rng.uniform(500, 2600, n) * rng.choice([-1, 1], n) * reach
        ps = p0 + v * (1 - np.exp(-a / 0.6)) * 0.6
        life = np.exp(-a / rng.uniform(0.35, 0.9, n))
        out += (s * life[:, None] * np.exp(-((d[None, :] - ps[:, None]) / 7) ** 2)).sum(0)
    return out


def compose():
    """Every note: (time, seconds, midi, velocity, part, k)."""
    N = []

    def add(t, d, m, v, part, k=None):
        N.append((float(t), float(d), note(m) if isinstance(m, str) else int(m), int(v), part, k))

    for k, t0 in enumerate(T_MURMUR):
        for t, m, v, d in play('forest_murmurs', t0, MURMUR, 12 if k % 2 else 0, 72 + 3 * (k % 5)):
            add(t, d, m, v, 'murmur', k)
    for k, t0 in enumerate(T_DELIGHT):
        for t, m, v, d in play('innocent_delight', t0, 0.62, 0, 78 + 6 * k):
            add(t, d, m, v, 'delight', k)
    for k, t0 in enumerate(T_SONG):
        for t, m, v, d in play('woodbird', t0, 0.75, 0, 92):
            add(t, d, m, v, 'song', k)
    for k, t0 in enumerate(T_CALL):
        for t, m, v, d in play('woodbird_call', t0, 0.5, 0, 98):
            add(t, d, m, v, 'call', k)
    add(0.0, D, 'E2', 60, 'pedal')
    return sorted(N, key=lambda e: e[0])


def bird_hops(G):
    """Where the Woodbird lands on each note of its song and call: [(time, place)]."""
    L = G.pd.max()
    rng = np.random.default_rng(27)
    song = sorted({t for t, d, m, v, part, k in compose() if part in ('song', 'call') and m >= note('A4')})
    lo, hi = at(G, 'Porch Left', 0.3), L - 30
    hops, p = [(T_BIRD_IN, L - 10)], L - 10
    for t in song:
        p = float(np.clip(p + rng.choice([-1, 1]) * rng.uniform(160, 460), lo, hi))
        hops.append((t, p))
    hops.append((T_SETTLE, at(G, 'Right', BIRD_AT)))
    return hops


def bird_track(G):
    """Per frame: the Woodbird's place, its speed, and how bright."""
    F = nframes(D)
    t = np.arange(F) * DT
    hops = bird_hops(G)
    p = np.full(F, hops[0][1])
    for (t0, p0), (t1, p1) in zip(hops, hops[1:]):
        u = smoothstep(t1, t1 + 0.25, t)
        p = np.where(t >= t1, p0 + (p1 - p0) * u, p)
    lvl = smoothstep(T_BIRD_IN, T_BIRD_IN + 0.3, t) * 0.9
    return dict(t=t, p=p, v=np.gradient(p, DT), lvl=lvl)


def render(G, seed=15):
    F = nframes(D)
    out = np.zeros((F, G.N, 3))
    S = stage(G)
    d, mid = S['d'], S['mid']
    L = d.max()
    N = compose()
    B = bird_track(G)
    p_sf = at(G, 'Left', TREE_AT)
    delight = [e for e in N if e[4] == 'delight']
    calls = sorted({e[0] for e in N if e[4] == 'call'})
    rng = np.random.default_rng(seed)
    glit = rng.uniform(at(G, 'Side', 0.1), at(G, 'Porch Left', 0.5), len(delight))
    swell = [(T_SONG[k], T_SONG[k] + 10) for k in range(3)]

    for f in range(F):
        t = f * DT
        T = t + 80 * K
        fr = forest(S, T, START)

        # each phrase of the Murmurs: a green-gold wave rolling the length of the roofline, alternating ways;
        # where two waves cross they flash
        for k, t0 in enumerate(T_MURMUR):
            a = t - t0
            if 0 <= a < 5.0:
                g = smoothstep(0, 0.5, a) * (1 - smoothstep(4.2, 5.0, a)) * (1 - smoothstep(D - 4.0, D - 0.3, t))
                one = np.exp(-((d - (a / 4.6) * L) / 340) ** 2)
                two = np.exp(-((d - L + (a / 4.6) * L) / 340) ** 2)
                fr += light(DAY, 0.95 * g * np.clip(one + two, 0, 1))
                core = np.exp(-((d - (a / 4.6) * L) / 70) ** 2) + np.exp(-((d - L + (a / 4.6) * L) / 70) ** 2)
                fr += light(SUN if k % 2 == 0 else HEAD, 0.9 * g * np.clip(core, 0, 1))
                fr += light(WHITE, 0.9 * g * np.clip(one * two * 3 - 0.4, 0, 1))

        # innocent delight: gold glitter all round him on every note
        for j, (t0, dur, m, v, part, k) in enumerate(delight):
            a = t - t0
            if 0 <= a < 0.8:
                fr += light(SUN, 0.95 * np.exp(-a / 0.2) * np.exp(-((d - glit[j]) / 14) ** 2))
                fr += light(WHITE, 0.6 * np.exp(-a / 0.08) * np.exp(-((d - glit[j]) / 6) ** 2))

        # while the bird sings the forest swells green and gold under it
        for t0, t1 in swell:
            if t0 <= t < t1 + 2:
                u = smoothstep(t0, t0 + 2, t) * (1 - smoothstep(t1, t1 + 2, t))
                breath = 0.5 + 0.5 * np.sin(2 * np.pi * (t - t0) / 2.5)
                fr += light(DAY, 0.45 * u * (0.6 + 0.4 * breath) * S['trees'])

        # the Woodbird: a hot magenta point, white at its heart, a short comet trail, wings flickering;
        # each landing of its call sends a magenta ring out through the green
        bl = B['lvl'][f]
        if bl > 0:
            p, v = B['p'][f], B['v'][f]
            flap = 0.82 + 0.18 * np.sin(2 * np.pi * 11 * t)
            behind = (d - p) * np.sign(v) < 0
            trail = behind * np.exp(-np.abs(d - p) / (18 + 0.08 * abs(v))) * min(1.0, abs(v) / 300)
            fr = fr * (1 - 0.9 * bl * np.exp(-((d - p) / 30) ** 2))[:, None]
            fr += light(BIRD, 1.1 * bl * flap * np.exp(-((d - p) / 10) ** 2))
            fr += light(BIRD, 0.85 * bl * trail)
            fr += light(WHITE, 0.9 * bl * flap * np.exp(-((d - p) / 3) ** 2))
            fr += light(BIRD, 0.5 * bl * np.exp(-((d - p) / 45) ** 2))
        for t0 in calls:
            a = t - t0
            if 0 <= a < 1.5 and bl > 0:
                p = float(np.interp(t0 + 0.25, B['t'], B['p']))
                fr += light(BIRD, 1.0 * np.exp(-a / 0.6) * np.exp(-((np.abs(d - p) - 700 * a) / 80) ** 2))

        # Siegfried under the tree, stirring when the bird calls
        sl = 0.8 + 0.15 * sum(np.exp(-(t - t0) / 0.4) for t0 in calls if 0 <= t - t0 < 2)
        fr = figure(fr, S, p_sf, SIEGFRIED, min(sl, 1.0), 16.0)
        fr += light(HEAD, 0.7 * min(sl, 1.0) * np.exp(-((d - p_sf) / 6) ** 2))
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

    for name, gain, rev in (('low', 0.33, 0.3), ('strings', 0.33, 0.38), ('winds', 0.29, 0.35), ('harp', 0.22, 0.4),
                            ('mallet', 0.15, 0.4)):
        M.bus(name, gain=gain, reverb=rev)
    vla = M.sampler('Strings/Viola Section/susvib/*.wav', tune=-12)
    vc = M.sampler('Strings/Cello Section/susvib/*.wav', tune=-12)
    cb = M.sampler('Strings/Solo Contrabass/SusNV/*.wav', tune=-12)
    vln = M.sampler('Strings/Violin Section/Spic/*.wav', tune=-12)
    vlns = M.sampler('Strings/Violin Section/susVib/*.wav', tune=-12)
    fl = M.sampler('Woodwinds/Flute/susvib/*.wav', tune=-12)
    fls = M.sampler('Woodwinds/Flute/stac/*.wav', tune=-12)
    ob = M.sampler('Woodwinds/Oboe/Vib/*.wav', tune=-12)
    harp = M.sampler('Strings/Harp/*.wav')
    glock = M.sampler('Percussion/Glock/*.wav')

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

    B = bird_track(G)
    sf = pan_at(at(G, 'Left', TREE_AT))
    for t, d, m, v, part, k in compose():
        if part == 'murmur':
            p = -0.7 + 1.4 * ((t - T_MURMUR[k]) / 6.0) if k % 2 == 0 else 0.7 - 1.4 * ((t - T_MURMUR[k]) / 6.0)
            if d > 1.5:
                hold('low', vc, m, t, t + d, v - 6, 0.0, rise=1.0, fall=1.5, gain=0.5)
            else:
                M.add('strings', vla.play(m, v, dur=d * 1.3, release=0.25), t, 0.55, p)
        elif part == 'delight':
            M.add('strings', vln.play(m, v), t, 0.6, sf)
            M.add('mallet', glock.play(m, v - 26), t, 0.4, sf)
        elif part == 'song' or part == 'call':
            p = pan_at(np.interp(t + 0.1, B['t'], B['p']))
            if m >= note('A4'):
                if d > 0.9:
                    hold('winds', fl, m, t, t + d, v, p, rise=0.05, fall=0.4, gain=0.85)
                else:
                    M.add('winds', fls.play(m, v), t, 0.9, p)
                    M.add('winds', ob.play(m, v - 24, dur=d * 1.05, release=0.1), t, 0.4, p)
            else:
                M.add('harp', harp.play(m + 12, v - 28), t, 0.6, p)
        elif part == 'pedal':
            hold('low', cb, m, t, t + d, v, 0.0, rise=4.0, fall=2.0, gain=0.5)
            hold('strings', vlns, note('B4'), T_SONG[0] - 1, T_SETTLE + 6, 50, 0.4, rise=4.0, fall=3.0, gain=0.25)
