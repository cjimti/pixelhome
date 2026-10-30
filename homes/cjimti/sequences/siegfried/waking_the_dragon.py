"""Waking the Dragon: night, after the stand-off, the Wanderer in blue at Left 0.7 and
Alberich in red at Right 0.3. The Wanderer turns to the cave and calls into it: his spear motif (Donington 73)
in the trombones throws pale blue beams down the front of the house into the porch, one per note. Alberich
shouts too, red bursts flung into the cave mouth.

The dragon answers. Two red eyes snap open on Porch Front, the cave blazes ochre, and Fafner's motif (57)
climbs in the tubas with every note a huge ochre shudder that shakes the whole house, run by run; the giants'
motif (58) is his voice ("I lie here and I own it"), each word a stamp of stone and scale that floods the house
from the cave out. Then he yawns ("let me sleep"): the eyes sink shut, the cave fades back to a smoulder.

The Wanderer laughs and goes: he turns into a blue storm-light again and sweeps the length of the house out the
free end of Right, past Alberich, who shrinks into the dark (lvl 0.3) and hides, his curse grumbling low.

compose() holds every note; stage(), forest(), figure() and sparks() are the forest and the cave, shared word for
word by Act II's scenes on a clock that runs on from scene to scene."""
import numpy as np
from pixelhome.audio import note
from pixelhome.fx import DT, hexc, light, smoothstep, nframes, keys, Flicker, smooth_noise
from pixelhome.leitmotifs import play

CODE = 'SF13'
TITLE = 'Waking the Dragon'
KIND = 'show'
DESCRIPTION = ('The Wanderer and the dwarf shout into the cave. Two red eyes open, the dragon roars until the '
               'house shakes, then yawns and goes back to sleep. The Wanderer vanishes in a gust of blue.')
VOICEOVER = ('Wake up, dragon, they shout into the cave. And something very large opens its eyes.')

K = 2                                       # this scene's place on Act II's shared clock: T = t + 80 K
T_CALL = 4.0                                # the Wanderer calls into the cave: his spear motif
T_SHOUT = [10.5, 12.0, 13.5]                # Alberich shouts
T_EYES = 16.5                               # the eyes snap open
T_DRAGON = 17.5                             # Fafner's motif in the tubas
T_VOICE = [27.0, 35.0]                      # the giants' motif: his voice
T_YAWN = 44.0                               # "let me sleep": the eyes close
T_LAUGH = 52.0                              # the Wanderer laughs
T_GO = 54.5                                 # and sweeps out as storm-light
T_HIDE = 62.0
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
WANDERER = hexc('#1a3cff')
WANDER_SOFT = hexc('#5a78ff')
SPEAR = hexc('#c8d8ff')

START = dict(night=0.65, day=0.0, shafts=0.65, cave=0.35, eyes=0.0)       # where SF12 left the forest
END = dict(night=0.65, day=0.0, shafts=0.65, cave=0.35, eyes=0.0)         # where SF14 picks it up
ALB_AT = 0.3                                # Alberich's watch, on Right
WAN_AT = 0.7                                # the Wanderer, on Left


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

    add(0.0, D, 'F1', 58, 'pedal')
    for t, m, v, d in play('spear', T_CALL, 0.42, -12, 106):
        add(t, d, m, v, 'spear')
    for i, t0 in enumerate(T_SHOUT):
        add(t0, 0.5, ('F3', 'Gb3', 'C4')[i], 104, 'shout', i)
    add(T_EYES, 0.1, 'C1', 125, 'eyes')
    for t, m, v, d in play('fafner', T_DRAGON, 0.55, -12, 118):
        add(t, d, m, v, 'dragon')
    for k, t0 in enumerate(T_VOICE):
        for t, m, v, d in play('giants', t0, 0.62, -12, 116 - 6 * k):
            add(t, d, m, v, 'voice', k)
    for j, m in enumerate(('Gb2', 'F2', 'E2', 'Eb2', 'D2', 'Db2', 'C2')):
        add(T_YAWN + j * 0.9, 1.1, m, 104 - 6 * j, 'yawn')
    for j in range(6):
        add(T_LAUGH + j * 0.28, 0.25, ('D4', 'B3', 'G3', 'D3', 'B2', 'G2')[j], 96 - 4 * j, 'laugh')
    add(T_GO - 0.5, 3.5, 'C1', 110, 'wind')
    for t, m, v, d in play('wanderer', T_GO, 0.5, 0, 84):
        add(t, d, m, v, 'wanderer')
    for t, m, v, d in play('curse', T_HIDE, 0.85, -12, 76):
        add(t, d, m, v, 'mutter')
    for m in ('F2', 'Ab2', 'C3'):
        add(T_HIDE, D - T_HIDE, m, 54, 'dark')
    return sorted(N, key=lambda e: e[0])


def render(G, seed=13):
    F = nframes(D)
    out = np.zeros((F, G.N, 3))
    S = stage(G)
    d, mid = S['d'], S['mid']
    L = d.max()
    N = compose()
    p_alb, p_wan = at(G, 'Right', ALB_AT), at(G, 'Left', WAN_AT)
    spear_on = np.array(sorted({e[0] for e in N if e[4] == 'spear'}))
    dragon = [e for e in N if e[4] == 'dragon']
    voice = np.array(sorted({e[0] for e in N if e[4] == 'voice'}))
    laugh = sorted({e[0] for e in N if e[4] == 'laugh'})
    mutter = sorted({e[0] for e in N if e[4] == 'mutter'})
    runs = ['Side', 'Left', 'Porch Left', 'Porch Front', 'Porch Right', 'Right']
    order = [3, 2, 4, 1, 5, 0]               # the shudder spreads from the cave out, run by run
    gust = Flicker(np.random.default_rng(seed + 1), G.N, 2.0, 6.0)
    lo, hi = note('Eb1'), note('Gb2')

    for f in range(F):
        t = f * DT
        T = t + 80 * K
        lv = {k: START[k] for k in START}
        awake = smoothstep(T_EYES - 0.05, T_EYES + 0.15, t) * (1 - smoothstep(T_YAWN, T_YAWN + 6, t))
        lv['eyes'] = awake * (1.0 if t < T_YAWN else 1.0 - 0.3 * np.sin(np.pi * min(1, (t - T_YAWN) / 6)))
        lv['cave'] += 0.45 * awake
        fr = forest(S, T, lv)

        # the Wanderer calls into the cave: a pale blue beam down the front of the house per note of his spear
        for t0 in spear_on:
            a = t - t0
            if 0 <= a < 1.2:
                front = p_wan + (mid - p_wan) * min(1.0, a / 0.35)
                beam = (d >= p_wan) * (d <= front)
                fr += light(WANDER_SOFT, 0.8 * np.exp(-a / 0.45) * beam)
                fr += light(SPEAR, 0.9 * np.exp(-a / 0.3) * np.exp(-((d - front) / 30) ** 2))
        # Alberich shouts: red bursts flung into the cave mouth
        for t0 in T_SHOUT:
            a = t - t0
            if 0 <= a < 1.2:
                front = p_alb - (p_alb - mid) * min(1.0, a / 0.35)
                beam = (d <= p_alb) * (d >= front)
                fr += light(BLOOD, 0.85 * np.exp(-a / 0.4) * beam)

        # the eyes snap open: a red flash out of the cave over the whole house
        if T_EYES <= t < T_EYES + 2:
            a = t - T_EYES
            fr += light(EYE, 0.95 * np.exp(-a / 0.5) * smoothstep(1400 * a + 100, 1400 * a - 100, np.abs(d - mid)))
            fr += light(WHITE, 0.6 * np.exp(-a / 0.08) * S['porch'])

        # Fafner's motif: every note a huge ochre shudder, run by run out from the cave
        for i, (t0, dur, m, v, part, k) in enumerate(dragon):
            a = t - t0
            if 0 <= a < 1.6:
                u = (m - lo) / (hi - lo)
                run = G.seg_of == runs[order[i % 6]]
                shake = 0.75 + 0.25 * np.sin(2 * np.pi * 9 * a)
                fr += light(SCALE, (0.85 + 0.25 * u) * np.exp(-a / 0.7) * shake * run)
                fr += light(CAVE, 0.8 * np.exp(-a / 0.4) * S['mouth'])

        # his voice: each word of the giants' motif floods the house in stone and scale from the cave out
        j = int(np.searchsorted(voice, t, side='right')) - 1
        if j >= 0 and t - voice[j] < 1.5 and t < T_YAWN:
            a = t - voice[j]
            reach = 1300 * min(1.0, a / 0.3)
            flood = smoothstep(reach + 80, reach - 80, np.abs(d - mid))
            fr += light(SCALE, 1.0 * np.exp(-a / 0.8) * flood)
            fr += light(STONE, 0.6 * np.exp(-a / 0.25) * flood)

        if awake > 0:
            fr += light(EYE, 0.55 * awake * (np.exp(-((d - at(G, 'Porch Front', 0.4)) / 25) ** 2)
                                             + np.exp(-((d - at(G, 'Porch Front', 0.6)) / 25) ** 2)))
        for t0 in mutter:
            a = t - t0
            if 0 <= a < 2.0:
                fr += light(BLOOD, 0.6 * np.exp(-a / 0.6) * np.exp(-((np.abs(d - p_alb) - 450 * a) / 90) ** 2))

        # the yawn: a slow ochre breath out of the cave as the eyes sink shut
        if T_YAWN <= t < T_YAWN + 7:
            a = t - T_YAWN
            fr += light(SCALE, 0.7 * np.sin(np.pi * a / 7) * S['mouth'])

        # the Wanderer laughs (blue flickers round him), then sweeps the length of the house as storm-light
        for t0 in laugh:
            a = t - t0
            if 0 <= a < 0.5:
                fr += light(WANDER_SOFT, 0.7 * np.exp(-a / 0.12) * np.exp(-((d - p_wan) / 160) ** 2))
        if T_GO <= t < T_GO + 6:
            a = t - T_GO
            front = p_wan + (L + 200 - p_wan) * smoothstep(0, 4.0, a)
            body = smoothstep(front - 700, front - 40, d) * smoothstep(front + 60, front - 20, d)
            fr += light(WANDER_SOFT, 1.0 * body * (0.85 + 0.15 * gust(T)) * (1 - smoothstep(4, 6, a)))
            fr += light(WANDERER, 0.6 * body * (1 - smoothstep(4, 6, a)))
            fr += light(SPEAR, 0.9 * np.exp(-((d - front) / 40) ** 2))

        # Alberich: flinches at the dragon, shrinks into hiding at the end
        alvl = keys(t, [(0, 0.7), (T_EYES, 0.7), (T_EYES + 0.5, 0.45), (T_YAWN + 4, 0.6), (T_GO + 2, 0.6),
                        (T_HIDE + 4, 0.3)])
        for t0 in T_SHOUT:
            if 0 <= t - t0 < 0.6:
                alvl += 0.3 * np.exp(-(t - t0) / 0.2)
        fr += light(MUD, 0.6 * alvl * np.exp(-((d - p_alb) / 70) ** 2))
        fr = figure(fr, S, p_alb, ALBERICH, min(alvl, 1.0))
        if t < T_GO:
            wl = 0.8 + 0.2 * sum(np.exp(-(t - t0) / 0.25) for t0 in spear_on if 0 <= t - t0 < 1)
            fr = figure(fr, S, p_wan, WANDERER, min(wl, 1.0), 18.0)
            fr += light(SPEAR, 0.5 * np.exp(-((d - p_wan - 22) / 6) ** 2))
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

    for name, gain, rev in (('low', 0.36, 0.25), ('brass', 0.3, 0.3), ('perc', 0.3, 0.3), ('winds', 0.26, 0.32),
                            ('dark', 0.24, 0.4), ('fx', 0.14, 0.3)):
        M.bus(name, gain=gain, reverb=rev)
    tuba = M.sampler('Brass/Tuba/sus/*.wav', tune=-12)
    tbn = M.sampler('Brass/Tenor Trombone/sus/*.wav', tune=-12)
    tbn_st = M.sampler('Brass/Tenor Trombone/stac/*.wav', tune=-12)
    horn = M.sampler('Brass/F Horn/sus/*.wav', tune=-12)
    cb = M.sampler('Strings/Solo Contrabass/SusNV/*.wav', tune=-12)
    cbs = M.sampler('Strings/Solo Contrabass/Spic/*.wav', tune=-12)
    vc = M.sampler('Strings/Cello Section/susvib/*.wav', tune=-12)
    ctrem = M.sampler('Strings/Cello Section/trem/*.wav', tune=-12)
    bsn = M.sampler('Woodwinds/Bassoon/stac/*.wav', tune=-12)
    timp = M.hits('Percussion/Timpani/Timpani1_Hit*.wav')
    roll = M.hits('Percussion/Timpani/Rolls/*.wav')
    gong = M.hits('Percussion/gongHit_fff.wav')
    bd = M.hits('Percussion/BDrumNewhit_v7_*.wav')

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

    alb = pan_at(at(G, 'Right', ALB_AT))
    wan = pan_at(at(G, 'Left', WAN_AT))
    cave = pan_at(at(G, 'Porch Front', 0.5))
    for t, d, m, v, part, k in compose():
        if part == 'pedal':
            hold('low', ctrem, m + 12, t, t + d, v, cave, rise=3.0, fall=2.0, gain=0.45)
        elif part == 'spear':
            M.add('brass', tbn.play(m + 12, v, dur=d * 1.05, release=0.2), t, 0.9, wan)
            M.add('low', tuba.play(m, v - 12, dur=d * 1.05, release=0.2), t, 0.6, wan)
        elif part == 'shout':
            M.add('brass', tbn_st.play(m, v), t, 0.9, alb)
            M.add('winds', bsn.play(m - 12, v), t, 0.8, alb)
        elif part == 'eyes':
            M.add('perc', gong.play(v), t, 0.9, cave)
            M.add('perc', timp.play(v, pitch=-7), t, 0.9, cave)
            M.add('perc', bd.play(v), t, 0.8, cave)
        elif part == 'dragon':
            M.add('low', tuba.play(m, v, dur=d * 1.1, release=0.3), t, 1.0, cave)
            M.add('low', cb.play(m + 12, v - 10, dur=d * 1.1, release=0.3), t, 0.7, cave)
            M.add('perc', timp.play(v - 14, pitch=-6), t, 0.6, cave)
        elif part == 'voice':
            M.add('low', tuba.play(m, v, dur=d * 1.05, release=0.25), t, 1.0, cave)
            M.add('brass', tbn.play(m + 12, v - 8, dur=d * 1.05, release=0.25), t, 0.8, cave)
            M.add('perc', bd.play(v), t, 0.7, cave)
        elif part == 'yawn':
            M.add('low', tuba.play(m, v, dur=d * 1.1, release=0.4), t, 0.9, cave)
        elif part == 'laugh':
            M.add('brass', horn.play(m - 12, v, dur=d, release=0.1), t, 0.7, wan)
        elif part == 'wind':
            M.add('fx', whoosh(d, 300, 4000, 0.8, seed=31), t, 1.0, wan)
            M.add('fx', whoosh(d, 2500, 300, 0.6, seed=32), t + 1.5, 1.0, 0.7)
            M.add('perc', roll.play(96, dur=d), t, 0.6, 0.0)
        elif part == 'wanderer':
            p = wan + (0.85 - wan) * min(1.0, (t - T_GO) / 4)
            if m < note('C3'):
                M.add('low', tuba.play(m, v, dur=d * 1.05, release=0.3), t, 0.7, p)
            else:
                M.add('brass', tbn.play(m, v, dur=d * 1.05, release=0.3), t, 0.6, p)
        elif part == 'mutter':
            M.add('low', vc.play(m, v, dur=d * 1.1, release=0.3), t, 0.9, alb)
            M.add('low', cbs.play(m - 12, v - 10), t, 0.6, alb)
        elif part == 'dark':
            hold('dark', vc, m, t, t + d, v, alb * 0.5, rise=4.0, fall=1.5, gain=0.5)
