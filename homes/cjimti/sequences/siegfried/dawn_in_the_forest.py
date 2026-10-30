"""Dawn in the Forest: the last of the night outside Fafner's cave. Alberich, hiding at Right 0.3, slips away.
Then Mime's smithing motif (Donington 50) comes hopping in on the bassoons, and Mime, sulphur yellow, scuttles in
from the free end of Right with Siegfried, emerald with his white-hot head, striding behind him. They come along
Right and up the porch to the cave mouth; Mime hops on every note, Siegfried's horn call (48) rings out ahead of
him in an emerald streak.

At the cave Mime tells him of the dragon: Fafner's motif (57) growls low and the cave mouth throbs ochre. Then
Siegfried has had enough of him: his strength (53) blasts emerald out to both ends of the house three times and
Mime bolts, a yellow streak back out the free end of Right.

And the sun comes up. The forest turns from night teal to hard green, and the sunrise breaks through the trees in
great gold shafts, one after another, each one bursting white where it lands and spreading. The Forest Murmurs
(29) begin to ripple, and Siegfried walks to the lime tree at Left 0.5 and lies down under it.

compose() holds every note; stage(), forest(), figure() and sparks() are the forest and the cave, shared word for
word by Act II's scenes on a clock that runs on from scene to scene."""
import numpy as np
from pixelhome.audio import note
from pixelhome.fx import DT, hexc, light, smoothstep, nframes, keys, Flicker, smooth_noise
from pixelhome.leitmotifs import play

CODE = 'SF14'
TITLE = 'Dawn in the Forest'
KIND = 'show'
DESCRIPTION = ('The dwarf leads Siegfried through the dark to the cave and tells him about the dragon, until '
               'Siegfried chases him off. Then the sun comes up through the trees in great gold shafts.')
VOICEOVER = ('Mime brings the boy to the dragon\'s cave, hoping he will learn what fear is. '
             'And the sun comes up.')

K = 3                                       # this scene's place on Act II's shared clock: T = t + 80 K
T_MIME = [3.0, 6.0, 9.0, 12.0]              # Mime's motif as they come in
T_IN = 3.0                                  # they enter at the free end of Right
T_HORN = [8.0, 14.0]                        # Siegfried's horn call
T_CAVE = 18.0                               # they reach the cave mouth
T_DRAGON = 19.5                             # Mime tells of the dragon
T_STR = [30.0, 33.5, 37.0]                  # Siegfried's strength: go away!
T_FLEE = 37.5                               # Mime bolts
T_SUN = 41.0                                # the sun breaks through: the first shaft
T_SHAFTS = [41.0, 44.0, 47.0, 50.0, 53.0, 56.0]
T_MURMUR = [55.0, 60.0, 65.0, 70.0]         # the Forest Murmurs begin
T_WALK = 50.0                               # Siegfried walks to the lime tree
T_LIE = 62.0
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
MIME = hexc('#e0c800')
SIEGFRIED = hexc('#00ff40')
HEAD = hexc('#e8ffe8')

START = dict(night=0.65, day=0.0, shafts=0.65, cave=0.35, eyes=0.0)       # where SF13 left the forest: night
END = dict(night=0.2, day=0.7, shafts=0.75, cave=0.35, eyes=0.0)          # where SF15 picks it up: day
ALB_AT = 0.3
TREE_AT = 0.5                               # the lime tree, on Left


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

    add(0.0, T_SUN, 'F1', 56, 'pedal')
    for k, t0 in enumerate(T_MIME):
        for t, m, v, d in play('mime', t0, 0.34, 0, 84 + 4 * k):
            add(t, d, m, v, 'mime', k)
    for k, t0 in enumerate(T_HORN):
        for t, m, v, d in play('siegfried_horn', t0, 0.3, 5, 100 + 6 * k):
            add(t, d, m, v, 'horn', k)
    for t, m, v, d in play('fafner', T_DRAGON, 0.6, 0, 92):
        add(t, d, m, v, 'dragon')
    for k, t0 in enumerate(T_STR):
        for t, m, v, d in play('siegfried', t0, 0.42, -12, 110 + 4 * k):
            add(t, d, m, v, 'strength', k)
    for j in range(7):
        add(T_FLEE + j * 0.22, 0.2, ('F4', 'Eb4', 'Db4', 'C4', 'Bb3', 'Ab3', 'G3')[j], 90 - 4 * j, 'flee')
    for k, t0 in enumerate(T_SHAFTS):
        for m in (('E3', 'B3', 'E4', 'Ab4'), ('Db3', 'Ab3', 'E4', 'A4'), ('E3', 'B3', 'Gb4', 'B4'))[k % 3]:
            add(t0, 3.4, m, 74 + 4 * k, 'sun', k)
        add(t0, 0.1, ('E5', 'Ab5', 'B5', 'E6', 'Ab5', 'B5')[k], 70, 'glint', k)
    for k, t0 in enumerate(T_MURMUR):
        for t, m, v, d in play('forest_murmurs', t0, 0.85, 12, 70 + 4 * k):
            add(t, d, m, v, 'murmur', k)
    add(T_SUN, D - T_SUN, 'E2', 62, 'day')
    return sorted(N, key=lambda e: e[0])


def tracks(G):
    """Per frame: where Mime and Siegfried are, and how bright."""
    F = nframes(D)
    t = np.arange(F) * DT
    L = G.pd.max()
    door = L + 40
    cave_m, cave_s = at(G, 'Porch Front', 0.62), at(G, 'Porch Right', 0.2)
    tree = at(G, 'Left', TREE_AT)
    hop = np.abs(np.sin(np.pi * t / 0.34)) * 10
    pm = np.array([keys(x, [(T_IN, door), (T_CAVE, cave_m), (T_FLEE, cave_m), (T_FLEE + 3.5, door + 200)]) for x in t])
    pm = pm - hop * ((t > T_IN) & (t < T_CAVE))
    ps = np.array([keys(x, [(T_IN + 1.5, door), (T_CAVE + 1.5, cave_s), (T_WALK, cave_s), (T_LIE - 2, tree)])
                   for x in t])
    lm = np.array([keys(x, [(T_IN, 0.0), (T_IN + 0.6, 0.8), (T_FLEE + 2.5, 0.8), (T_FLEE + 3.5, 0.0)]) for x in t])
    ls = np.array([keys(x, [(T_IN + 1.5, 0.0), (T_IN + 2.2, 0.85), (T_LIE, 0.85), (T_LIE + 3, 0.8)]) for x in t])
    return dict(t=t, pm=pm, ps=ps, lm=lm, ls=ls)


def render(G, seed=14):
    F = nframes(D)
    out = np.zeros((F, G.N, 3))
    S = stage(G)
    d, mid = S['d'], S['mid']
    L = d.max()
    N = compose()
    C = tracks(G)
    p_alb = at(G, 'Right', ALB_AT)
    mime_on = np.array(sorted({e[0] for e in N if e[4] == 'mime'}))
    dragon = [e for e in N if e[4] == 'dragon']
    strength = sorted({e[0] for e in N if e[4] == 'strength'})
    rng = np.random.default_rng(seed)
    land = rng.uniform(at(G, 'Left', 0.05), L - 60, len(T_SHAFTS))
    land[0] = at(G, 'Right', 0.55)

    for f in range(F):
        t = f * DT
        T = t + 80 * K
        lv = {k: keys(t, [(0, START[k]), (T_SUN - 1, START[k]), (T_SUN + 16, END[k])]) for k in START}
        fr = forest(S, T, lv)
        pm, ps = C['pm'][f], C['ps'][f]

        # Alberich, still hiding at the start, slips away
        if t < 5:
            al = 0.3 * (1 - smoothstep(1, 4.5, t))
            fr += light(MUD, 0.6 * al * np.exp(-((d - p_alb) / 70) ** 2))
            fr = figure(fr, S, p_alb, ALBERICH, al)

        # Mime's motif: a yellow blip under him on every hop, a little ripple out
        i = int(np.searchsorted(mime_on, t, side='right')) - 1
        if i >= 0 and t - mime_on[i] < 0.6 and t < T_CAVE + 1:
            a = t - mime_on[i]
            fr += light(MIME, 0.6 * np.exp(-a / 0.15) * np.exp(-((np.abs(d - pm) - 300 * a) / 40) ** 2))

        # the horn call: an emerald streak racing ahead of him, the whole way along the front
        for t0 in T_HORN:
            a = t - t0
            if 0 <= a < 2.4:
                front = ps - 1100 * a
                fr += light(SIEGFRIED, 0.95 * np.exp(-a / 1.0) * smoothstep(front - 30, front + 30, d)
                            * smoothstep(ps + 10, ps - 120, d) * smoothstep(front + 500, front, d))
                fr += light(HEAD, 0.9 * np.exp(-a / 0.8) * np.exp(-((d - front) / 22) ** 2))

        # the dragon told of: the cave mouth throbs ochre on every note of Fafner's motif
        for t0, dur, m, v, part, k in dragon:
            a = t - t0
            if 0 <= a < 1.0:
                fr += light(SCALE, 0.85 * np.exp(-a / 0.35) * S['mouth'])
                fr += light(CAVE, 0.6 * np.exp(-a / 0.5) * S['porch'])

        # his strength: emerald blasts out to both ends of the house
        for t0 in T_STR:
            a = t - t0
            if 0 <= a < 2.0:
                r = 1600 * min(1.0, a / 0.6)
                fr += light(SIEGFRIED, 0.95 * np.exp(-a / 0.7) * smoothstep(r + 80, r - 80, np.abs(d - ps)))
                fr += light(HEAD, 0.8 * np.exp(-a / 0.3) * np.exp(-((np.abs(d - ps) - r) / 40) ** 2))
        if T_FLEE <= t < T_FLEE + 3.5:
            a = t - T_FLEE
            fr += light(MIME, 0.7 * np.exp(-((d - pm + 80) / 60) ** 2) * (1 - a / 3.5))

        # the sunrise: gold shafts breaking through, each bursting white where it lands and spreading
        for k, t0 in enumerate(T_SHAFTS):
            a = t - t0
            if 0 <= a < 7:
                w = 30 + 220 * (1 - np.exp(-a / 1.5))
                g = smoothstep(0, 0.25, a) * (1 - 0.6 * smoothstep(2, 7, a))
                fr += light(SUN, 1.0 * g * np.exp(-((d - land[k]) / w) ** 2))
                fr += light(WHITE, 0.95 * np.exp(-a / 0.3) * np.exp(-((d - land[k]) / 25) ** 2))
                fr += light(SUN, 0.6 * np.exp(-a / 0.8) * np.exp(-((np.abs(d - land[k]) - 900 * a) / 80) ** 2))
        if T_SUN <= t < T_SUN + 2:
            fr += light(SUN, 0.5 * np.exp(-(t - T_SUN) / 0.5))

        # the Forest Murmurs: green-gold ripples rolling end to end, alternating direction
        for k, t0 in enumerate(T_MURMUR):
            a = t - t0
            if 0 <= a < 5:
                front = (a / 4.5) * L if k % 2 == 0 else L - (a / 4.5) * L
                g = smoothstep(0, 0.5, a) * (1 - smoothstep(4.2, 5, a))
                fr += light(DAY, 0.85 * g * np.exp(-((d - front) / 220) ** 2))
                fr += light(SUN, 0.7 * g * np.exp(-((d - front) / 45) ** 2))

        # Mime, and Siegfried
        if C['lm'][f] > 0:
            fr = figure(fr, S, pm, MIME, C['lm'][f], 14.0)
        if C['ls'][f] > 0:
            ls = C['ls'][f]
            for t0 in strength:
                if 0 <= t - t0 < 0.5:
                    ls += 0.15 * np.exp(-(t - t0) / 0.15)
            fr = figure(fr, S, ps, SIEGFRIED, min(ls, 1.0), 16.0)
            fr += light(HEAD, 0.7 * min(ls, 1.0) * np.exp(-((d - ps) / 6) ** 2))
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

    for name, gain, rev in (('low', 0.42, 0.25), ('brass', 0.39, 0.3), ('perc', 0.34, 0.3), ('winds', 0.34, 0.32),
                            ('strings', 0.34, 0.36), ('harp', 0.29, 0.4), ('mallet', 0.21, 0.4)):
        M.bus(name, gain=gain, reverb=rev)
    bsn = M.sampler('Woodwinds/Bassoon/stac/*.wav', tune=-12)
    oboe = M.sampler('Woodwinds/Oboe/Stacc/*.wav', tune=-12)
    horn = M.sampler('Brass/F Horn/sus/*.wav', tune=-12)
    tuba = M.sampler('Brass/Tuba/sus/*.wav', tune=-12)
    tpt = M.sampler('Brass/Trumpet/sus/*.wav', tune=-12)
    cb = M.sampler('Strings/Solo Contrabass/SusNV/*.wav', tune=-12)
    ctrem = M.sampler('Strings/Cello Section/trem/*.wav', tune=-12)
    vln = M.sampler('Strings/Violin Section/susVib/*.wav', tune=-12)
    vla = M.sampler('Strings/Viola Section/susvib/*.wav', tune=-12)
    vc = M.sampler('Strings/Cello Section/susvib/*.wav', tune=-12)
    harp = M.sampler('Strings/Harp/*.wav')
    glock = M.sampler('Percussion/Glock/*.wav')
    timp = M.hits('Percussion/Timpani/Timpani1_Hit*.wav')
    cym = M.hits('Percussion/susCymb1-cresc-Median*.wav')

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

    C = tracks(G)

    def pan_t(key, t):
        return pan_at(np.interp(t, C['t'], C[key]))

    cave = pan_at(at(G, 'Porch Front', 0.5))
    land = np.random.default_rng(14).uniform(at(G, 'Left', 0.05), G.pd.max() - 60, len(T_SHAFTS))
    land[0] = at(G, 'Right', 0.55)
    for t, d, m, v, part, k in compose():
        if part == 'pedal':
            hold('low', ctrem, m + 12, t, t + d, v, cave, rise=2.0, fall=3.0, gain=0.4)
        elif part == 'mime':
            p = pan_t('pm', t)
            M.add('winds', bsn.play(m - 12, v), t, 0.9, p)
            M.add('winds', oboe.play(m, v - 14), t, 0.5, p)
        elif part == 'horn':
            p = pan_t('ps', t)
            if d > 0.6:
                hold('brass', horn, m, t, t + d, v, p, rise=0.05, fall=0.5, gain=0.9)
            else:
                M.add('brass', horn.play(m, v, dur=d * 1.1, release=0.15), t, 0.9, p)
        elif part == 'dragon':
            M.add('low', tuba.play(m, v, dur=d * 1.1, release=0.3), t, 0.95, cave)
            M.add('low', cb.play(m + 12, v - 12, dur=d * 1.1, release=0.3), t, 0.6, cave)
        elif part == 'strength':
            p = pan_t('ps', t)
            M.add('brass', tpt.play(m, v, dur=d * 1.1, release=0.15), t, 0.85, p)
            M.add('brass', horn.play(m - 12, v - 8, dur=d * 1.1, release=0.15), t, 0.7, p)
            if t in [play('siegfried', t0, 0.42, -12)[0][0] for t0 in T_STR]:
                M.add('perc', timp.play(v, pitch=-3), t, 0.8, p)
        elif part == 'flee':
            M.add('winds', bsn.play(m - 12, v), t, 0.9, pan_t('pm', t))
        elif part == 'sun':
            p = pan_at(land[k])
            hold('strings', vla if m < note('C4') else vln, m, t, t + d, v, p, rise=0.6, fall=1.5, gain=0.6)
            if m == note('E3') or m == note('Db3'):
                M.add('perc', cym.play(70), t - 1.2, 0.5, p)
                M.add('harp', harp.play(m + 12, v), t, 0.8, p)
                M.add('harp', harp.play(m + 19, v - 6), t + 0.12, 0.8, p)
                M.add('harp', harp.play(m + 24, v - 10), t + 0.24, 0.8, p)
        elif part == 'glint':
            M.add('mallet', glock.play(m, v), t, 0.7, pan_at(land[k]))
        elif part == 'murmur':
            p = -0.6 + 1.2 * (k % 2)
            if d > 1.5:
                hold('strings', vc, m, t, t + d, v, 0.0, rise=0.8, fall=1.0, gain=0.45)
            else:
                M.add('strings', vla.play(m, v, dur=d * 1.2, release=0.2), t, 0.6, p)
        elif part == 'day':
            hold('low', cb, m, t, t + d, v, 0.0, rise=6.0, fall=2.0, gain=0.5)
