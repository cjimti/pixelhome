"""The Ring and the Tarnhelm: broad day in the forest, the dragon dead. The Woodbird, a hot magenta point on Right,
sings its motif (Donington 27) and every note is a hop and a flash: take the Ring and the Tarnhelm from the hoard.
Siegfried, emerald on Porch Front, walks into the dark middle of the cave and is swallowed; the cave mouth flares
with the gold of the hoard, the Ring (8) glinting in the horns, and the bird flies off out of the free end of Right.

While he is inside, Alberich (red in his muddy halo) and Mime (sulphur yellow) come running in from the free end of
Right and fight over the spoils: the whole of Right splits into a red half and a yellow half whose border lurches
back and forth with every blow of their quarrel, Alberich's curse (13) in the trombones against Mime's whine (71)
in the bassoons, and white sparks flying where they clash.

Siegfried comes out with the Ring: the Ring sounds in full on the horns and a gold wave sweeps the whole house end
to end, Alberich and Mime shrinking back. Then the Tarnhelm (18): the whole house shimmers and thins into a
grey-green mist, Siegfried flickering in and out of sight. Alberich slinks off out of the free end of Right with a
red ripple of his laugh, and Mime is left on Right, while Siegfried stands at the middle of Porch Front with the
Ring's gold glint on him.

compose() holds every note; stage(), forest(), figure() and sparks() are the forest and the cave, shared word for
word by Act II's scenes on a clock that runs on from scene to scene."""
import numpy as np
from pixelhome.audio import note
from pixelhome.fx import DT, hexc, light, smoothstep, nframes, keys, Flicker, smooth_noise
from pixelhome.leitmotifs import play

CODE = 'SF20'
TITLE = 'The Ring and the Tarnhelm'
KIND = 'show'
DESCRIPTION = ('The bird tells Siegfried to take the Ring and the magic helmet from the hoard. While he is in the '
               'cave, two dwarfs fight over the treasure, and he comes out with the Ring shining gold.')
VOICEOVER = ('The little bird sings: take the Ring, and the magic helmet. '
             'But two greedy dwarfs are already fighting over the gold.')

K = 9                                       # this scene's place on Act II's shared clock: T = t + 80 K
BEAT = 0.5
T_BIRD = [1.0, 5.5]                         # the Woodbird's song
T_IN = 9.5                                  # Siegfried walks into the cave
T_HOARD = 13.0                              # the Ring in the horns, the hoard flaring
T_FLY = 12.0                                # the bird flies off
T_RUSH = 18.0                               # Alberich and Mime run in
T_FIGHT = 22.0                              # the quarrel, blow by blow
T_OUT = 41.0                                # Siegfried comes out with the Ring
T_HELM = [49.0, 54.0]                       # the Tarnhelm
T_SLINK = 60.0                              # Alberich slinks off, laughing
T_HERO = 66.0
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
HOT = hexc('#fff0ff')
MIME = hexc('#e0c800')
MIST = hexc('#50c0a8')
SPARK = hexc('#ffb020')

DAY_LV = dict(night=0.2, day=0.7, shafts=0.75, cave=0.35, eyes=0.0)
MIME_AT, ALB_AT = 0.4, 0.25                 # their places on Right at the end and in the quarrel


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



def woodbird(fr, S, pos, t, lvl, T):
    """The Woodbird: a hot magenta point with a white-hot centre, its wings flickering, a short comet trail."""
    d = S['d']
    flick = 0.78 + 0.22 * np.sin(2 * np.pi * 11 * T)
    for k, lag in enumerate((0.24, 0.16, 0.08)):
        fr = fr + light(BIRD, 0.35 * (k + 1) / 3 * lvl * np.exp(-((d - pos(t - lag)) / 9) ** 2))
    p = pos(t)
    fr = fr + light(BIRD, lvl * flick * np.exp(-((d - p) / 8) ** 2))
    fr = fr + light(BIRD, 0.35 * lvl * np.exp(-((d - p) / 30) ** 2))
    return fr + light(HOT, 0.8 * lvl * np.exp(-((d - p) / 3) ** 2))


def compose():
    """Every note: (time, seconds, midi, velocity, part, k)."""
    N = []

    def add(t, d, m, v, part, k=None):
        N.append((float(t), float(d), note(m) if isinstance(m, str) else int(m), int(v), part, k))

    for k, t0 in enumerate(T_BIRD):
        for t, m, v, d in play('woodbird', t0, 0.55, 0, 90, line='melody'):
            add(t, d, m, v, 'bird', k)
        for t, m, v, d in play('woodbird', t0, 0.55, 0, 58, line='bass'):
            add(t, d, m, v, 'birdbed', k)
    for t, m, v, d in play('ring', T_HOARD, 0.6, 0, 92):
        add(t, d, m, v, 'hoard')
    add(T_RUSH, 0.1, 'C1', 110, 'rush')
    rng = np.random.default_rng(20)
    for j in range(14):                     # the quarrel: blows alternating, Alberich and Mime
        t = T_FIGHT + j * 1.25 + rng.uniform(-0.15, 0.15)
        add(t, 0.4, 'C1', 96 + 2 * (j % 4), 'blow', j % 2)
    for t, m, v, d in play('curse', T_FIGHT + 0.5, 0.5, -12, 96):
        add(t, d, m, v, 'alb')
    for k, t0 in enumerate((T_FIGHT + 3.0, T_FIGHT + 8.0, T_FIGHT + 13.0)):
        for t, m, v, d in play('mime_frustrated', t0, 0.75, 12, 94):
            add(t, d, m, v, 'mime', k)
    for t, m, v, d in play('ring', T_OUT, 0.66, 0, 118):
        add(t, d, m, v, 'ring')
    add(T_OUT, 0.1, 'C1', 122, 'crash')
    for k, t0 in enumerate(T_HELM):
        for t, m, v, d in play('tarnhelm', t0, 0.7, 0, 84 - 8 * k):
            add(t, d, m, v, 'helm', k)
    for t, m, v, d in play('curse', T_SLINK, 0.75, -12, 88):
        add(t, d, m, v, 'laugh')
    for t, m, v, d in play('siegfried', T_HERO, 0.6, -12, 96):
        add(t, d, m, v, 'hero', 0)
    for t, m, v, d in play('siegfried', T_HERO + 4.0, 0.6, -12, 86):
        add(t, d, m, v, 'hero', 1)
    for m in ('E2', 'B2', 'E3'):
        add(0.0, D, m, 50, 'murmur')
    return sorted(N, key=lambda e: e[0])


def bird_track(G):
    """Where the bird is: hops among the trees on Right on its song, then off out of the free end."""
    N = compose()
    rng = np.random.default_rng(27)
    home = at(G, 'Right', 0.3)
    pts, p = [(0.0, home)], home
    for e in N:
        if e[4] == 'bird':
            p = float(np.clip(p + rng.uniform(-45, 45), at(G, 'Right', 0.08), at(G, 'Right', 0.55)))
            pts += [(e[0], pts[-1][1]), (e[0] + 0.25, p)]
    pts += [(T_FLY, p), (T_FLY + 1.6, G.pd.max() + 60)]
    return lambda t: keys(t, pts)


def fighters(G, t, blows):
    """Where the border between Alberich's red and Mime's yellow is on Right, shoved by each blow."""
    lo, hi = at(G, 'Right', 0.12), at(G, 'Right', 0.7)
    shove = sum((1 if k == 0 else -1) * smoothstep(t0, t0 + 0.2, t) for t0, _, _, _, _, k in blows)
    return lo + (hi - lo) * (0.5 + 0.12 * shove)


def render(G, seed=20):
    F = nframes(D)
    out = np.zeros((F, G.N, 3))
    S = stage(G)
    d, mid = S['d'], S['mid']
    L = d.max()
    N = compose()
    bird = bird_track(G)
    bird_on = np.array([e[0] for e in N if e[4] == 'bird'])
    blows = [e for e in N if e[4] == 'blow']
    ring_on = np.array(sorted({e[0] for e in N if e[4] == 'ring'}))
    helm = [e for e in N if e[4] == 'helm']
    right = G.seg_of == 'Right'
    lo, hi = at(G, 'Right', 0.12), at(G, 'Right', 0.7)
    rng = np.random.default_rng(seed)
    gold_at = rng.uniform(at(G, 'Porch Left', 0.3), at(G, 'Porch Right', 0.7), 24)
    mist = Flicker(rng, G.N, 3.0, 9.0)
    p_start, p_end = at(G, 'Porch Front', 0.3), at(G, 'Porch Front', 0.5)
    p_mime, p_alb = at(G, 'Right', MIME_AT), at(G, 'Right', ALB_AT)

    for f in range(F):
        t = f * DT
        T = t + 80 * K
        lv = dict(DAY_LV)
        hoard = smoothstep(T_IN + 1, T_HOARD + 1, t) * (1 - smoothstep(T_OUT + 1, T_OUT + 5, t))
        lv['cave'] += 0.45 * hoard
        helmed = sum(smoothstep(t0, t0 + 0.6, t) * (1 - smoothstep(t0 + 3.6, t0 + 4.6, t)) for t0 in T_HELM)
        lv['day'] *= 1 - 0.55 * helmed
        lv['shafts'] *= 1 - 0.7 * helmed
        fr = forest(S, T, lv)

        # the hoard in the cave: gold heaped on the porch, glinting on each note of the Ring
        if hoard > 0:
            fr += light(GOLD, 0.7 * hoard * S['mouth'] ** 1.5)
            for j, g in enumerate(gold_at):
                tw = 0.5 + 0.5 * np.sin(2 * np.pi * (0.7 + 0.13 * j) * t + j)
                fr += light(HOT, 0.6 * hoard * tw ** 6 * np.exp(-((d - g) / 6) ** 2))

        # the bird's song: each note a hop and a magenta flash rippling out over Right
        if t < T_FLY + 2:
            i = int(np.searchsorted(bird_on, t, side='right')) - 1
            if i >= 0 and t - bird_on[i] < 0.8:
                a = t - bird_on[i]
                fr += light(BIRD, 0.6 * np.exp(-a / 0.3) * np.exp(-((np.abs(d - bird(t)) - 500 * a) / 50) ** 2))
            fr = woodbird(fr, S, bird, t, 0.95, T)

        # Siegfried: into the cave and swallowed by the dark, out again with the Ring
        p = keys(t, [(T_IN, p_start), (T_IN + 2.5, p_end)])
        lvl = keys(t, [(T_IN + 1.5, 0.8), (T_IN + 3.5, 0.0), (T_OUT - 0.5, 0.0), (T_OUT + 0.4, 1.0), (T_OUT + 6, 0.8)])
        if helmed > 0:
            lvl *= 1 - helmed * (0.5 + 0.5 * np.sin(2 * np.pi * 3.3 * t)) ** 2
        if lvl > 0.01:
            fr = figure(fr, S, p, SIEGFRIED, lvl)
            fr += light(HEAD, 0.6 * lvl * np.exp(-((d - p) / 4) ** 2))
        if t >= T_OUT:
            fr += light(GOLD, min(1.0, 1.2 * lvl) * np.exp(-((d - p - 9) / 4) ** 2))

        # the Ring in full: a gold wave from the cave out to both ends, one surge per note
        if T_OUT <= t < T_HELM[0]:
            a = t - T_OUT
            front = min(1.0, a / 2.0) * max(mid, L - mid)
            j = int(np.searchsorted(ring_on, t, side='right')) - 1
            pulse = np.exp(-(t - ring_on[j]) / 0.35) if j >= 0 else 0.0
            fade = 1 - smoothstep(T_HELM[0] - 2, T_HELM[0], t)
            fr += light(GOLD, fade * (1.0 * np.exp(-((np.abs(d - mid) - front) / 160) ** 2)
                                      + (0.4 + 0.35 * pulse) * (np.abs(d - mid) < front)))
            if a < 0.5:
                fr += light(WHITE, 0.5 * np.exp(-a / 0.12))

        # the Tarnhelm: the house shimmers and thins into a grey-green mist on each note
        for t0, dur, m, v, part, k in helm:
            a = t - t0
            if 0 <= a < 1.5:
                fr += light(MIST, 0.8 * helmed * np.exp(-a / 0.5) * np.clip(mist(T + 7 * k), 0, None) ** 2)
        if helmed > 0:
            fr += light(MIST, 0.45 * helmed)
        if helmed > 0:
            fr *= (1 - 0.5 * helmed * (np.clip(mist(T), -1, 1) * 0.5 + 0.5))[:, None]

        # Alberich and Mime: rush in, then the whole of Right split red against yellow, the border lurching
        if t >= T_RUSH:
            share = smoothstep(T_RUSH, T_FIGHT, t)
            if t < T_OUT + 2:
                border = fighters(G, t, blows)
                split = right * (d > lo - 60) * (1 - smoothstep(T_OUT, T_OUT + 2, t)) * share
                fr += light(ALBERICH, 0.85 * split * smoothstep(border + 15, border - 15, d))
                fr += light(MIME, 0.85 * split * smoothstep(border - 15, border + 15, d))
                for t0, _, _, v, _, k in blows:
                    a = t - t0
                    if 0 <= a < 0.6:
                        fr += light(WHITE, 0.9 * np.exp(-a / 0.08) * np.exp(-((d - border) / 14) ** 2))
                        fr += light(ALBERICH if k == 0 else MIME, 0.6 * np.exp(-a / 0.2) * right)
                fr += light(SPARK, np.clip(sparks(S, [(e[0], 0.8, fighters(G, e[0] + 0.2, blows)) for e in blows], t, 21,
                                                  n=10, reach=0.35), 0, 1) * right)
            # after the quarrel: Alberich at his place, then slinking off; Mime to his
            a_pos = keys(t, [(T_RUSH, L + 30), (T_FIGHT, p_alb), (T_SLINK, p_alb), (T_SLINK + 5, L + 40)])
            m_pos = keys(t, [(T_RUSH + 1, L + 30), (T_FIGHT + 1, at(G, 'Right', 0.6)), (T_OUT, at(G, 'Right', 0.6)),
                             (T_OUT + 3, p_mime)])
            cower = 1 - 0.35 * smoothstep(T_OUT, T_OUT + 1.5, t) * (1 - smoothstep(T_HELM[1] + 4, T_HERO, t))
            alb_lvl = 0.8 * cower * (1 - smoothstep(T_SLINK + 3.5, T_SLINK + 5, t))
            if alb_lvl > 0.01:
                fr += light(MUD, 0.5 * alb_lvl * np.exp(-((d - a_pos) / 60) ** 2))
                fr = figure(fr, S, a_pos, ALBERICH, alb_lvl)
            fr = figure(fr, S, m_pos, MIME, keys(t, [(T_RUSH + 1, 0.0), (T_RUSH + 2, 0.8), (T_HERO, 0.8),
                                                    (D, 0.7)]) * cower)
        if T_SLINK <= t < T_SLINK + 4:
            a = t - T_SLINK
            fr += light(BLOOD, 0.8 * np.exp(-a / 1.2) * np.exp(-((np.abs(d - p_alb) - 800 * a) / 110) ** 2))

        # his strength: emerald surges out from him on each phrase
        if t >= T_HERO:
            for t0 in (T_HERO, T_HERO + 4.0):
                a = t - t0
                if 0 <= a < 2.5:
                    fr += light(SIEGFRIED, 0.95 * np.exp(-a / 1.0) * np.exp(-((np.abs(d - p_end) - 800 * a) / 170) ** 2))
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

    for name, gain, rev in (('low', 0.28, 0.25), ('brass', 0.27, 0.3), ('perc', 0.27, 0.28), ('winds', 0.28, 0.32),
                            ('strings', 0.22, 0.35)):
        M.bus(name, gain=gain, reverb=rev)
    fl = M.sampler('Woodwinds/Flute/susNV/*.wav', tune=-12)
    ob = M.sampler('Woodwinds/Oboe/Stacc/*.wav', tune=-12)
    bsn = M.sampler('Woodwinds/Bassoon/sus/*.wav', tune=-12)
    bsn_st = M.sampler('Woodwinds/Bassoon/stac/*.wav', tune=-12)
    horn = M.sampler('Brass/F Horn/sus/*.wav', tune=-12)
    tbn = M.sampler('Brass/Tenor Trombone/sus/*.wav', tune=-12)
    vtrem = M.sampler('Strings/Violin Section/Trem/*.wav', tune=-12)
    vc = M.sampler('Strings/Cello Section/susvib/*.wav', tune=-12)
    cbs = M.sampler('Strings/Solo Contrabass/Spic/*.wav', tune=-12)
    harp = M.sampler('Strings/Harp/*.wav')
    glock = M.sampler('Percussion/Glock/*.wav')
    timp = M.hits('Percussion/Timpani/Timpani1_Hit*.wav')
    crash = M.hits('Percussion/cymbal-crash1_f*.wav')
    snare = M.hits('Percussion/Snare2-HitSN*.wav')

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

    bird = bird_track(G)
    cave = pan_at(at(G, 'Porch Front', 0.5))
    right = pan_at(at(G, 'Right', 0.4))
    alb = pan_at(at(G, 'Right', ALB_AT))
    for t, d, m, v, part, k in compose():
        if part == 'bird':
            M.add('winds', fl.play(m, v, dur=d * 1.1, release=0.15), t, 0.9, pan_at(bird(t)))
            M.add('winds', ob.play(m, v - 20), t, 0.4, pan_at(bird(t)))
        elif part == 'birdbed':
            M.add('strings', harp.play(m, v), t, 0.6, right)
        elif part == 'hoard':
            if d > 1.0:
                hold('brass', horn, m, t, t + d, v, cave, rise=0.3, fall=1.0, gain=0.6)
            else:
                M.add('brass', horn.play(m, v, dur=d * 1.05, release=0.3), t, 0.65, cave)
            M.add('perc', glock.play(m + 12, v - 30), t, 0.5, cave)
        elif part == 'rush':
            M.add('perc', snare.play(100), t, 0.6, right)
            M.add('perc', timp.play(v, pitch=-3), t, 0.8, right)
        elif part == 'blow':
            M.add('perc', timp.play(v, pitch=-1 if k else -6), t, 0.8, alb if k == 0 else right)
            M.add('perc', snare.play(v - 10), t, 0.5, right)
        elif part == 'alb':
            if d > 1.0:
                hold('brass', tbn, m, t, t + d, v, alb, rise=0.15, fall=0.8, gain=0.8)
            else:
                M.add('brass', tbn.play(m, v, dur=d * 1.05, release=0.25), t, 0.85, alb)
            M.add('low', cbs.play(m - 12, v - 10), t, 0.6, alb)
        elif part == 'mime':
            M.add('winds', bsn_st.play(m, v), t, 0.9, right)
            M.add('winds', ob.play(m + 12, v - 16), t, 0.5, right)
        elif part == 'ring':
            if d > 1.0:
                hold('brass', horn, m, t, t + d, v, cave, rise=0.12, fall=1.0, gain=0.9)
            else:
                M.add('brass', horn.play(m, v, dur=d * 1.05, release=0.3), t, 0.95, cave)
            M.add('low', tbn.play(m - 12, v - 12, dur=d * 1.05, release=0.3), t, 0.7, cave)
        elif part == 'crash':
            M.add('perc', crash.play(v), t, 0.9, cave)
            M.add('perc', timp.play(v, pitch=-5), t, 0.9, cave)
        elif part == 'helm':
            hold('strings', vtrem, m, t, t + d, v, cave, rise=0.3, fall=1.2, gain=0.55)
            M.add('winds', bsn.play(m - 12, v - 10, dur=d, release=0.5), t, 0.5, cave)
        elif part == 'laugh':
            M.add('brass', tbn.play(m, v, dur=d * 1.05, release=0.3), t, 0.8, alb)
            M.add('low', cbs.play(m - 12, v - 6), t, 0.7, alb)
        elif part == 'hero':
            M.add('brass', horn.play(m, v, dur=d * 1.1, release=0.3), t, 0.85, cave)
            M.add('strings', vc.play(m - 12, v - 16, dur=d * 1.1, release=0.3), t, 0.5, cave)
        elif part == 'murmur':
            hold('strings', vtrem, m + 12, t, t + d, v, 0.0, rise=3.0, fall=2.0, gain=0.18)
