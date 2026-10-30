"""The Woodbird Leads: day in the forest, Mime dead. Siegfried stands at the middle of Porch Front with the Ring's
glint on him, lonely; the Woodbird on Right sings (Donington 27) and every note is a hop and a flash. It sings of a
bride asleep on a rock ringed with fire, and the house shows him: fire leaps up all over the porch in Loge's
colours with a silver sleeper burning at its heart, the magic sleep (16) in the woodwinds and Loge's flicker (20a)
in the violins. The bird sings again and the vision blazes over the whole house.

Siegfried's freedom (56) bursts out of him on the horns, emerald surging to both ends on every note. The bird
trills its innocent delight (28) and darts to him and away, again and again: follow me. His horn call (48)
answers, and the race is on: the bird streaks out along Right in quick hops and Siegfried charges after it, an
emerald comet with a long wake sweeping the house green behind him, the freedom motif in full on the horns, out
of the free end of Right and gone.

The forest is left empty and bright in the sun, the forest murmurs (29) in the strings, and far off at the free end
of Right a glow of fire pulses and grows, Loge's flicker in the distance: the way to the rock.

compose() holds every note; stage(), forest(), figure() and sparks() are the forest and the cave, shared word for
word by Act II's scenes on a clock that runs on from scene to scene."""
import numpy as np
from pixelhome.audio import note
from pixelhome.fx import DT, hexc, light, smoothstep, nframes, keys, Flicker, smooth_noise
from pixelhome.leitmotifs import play

CODE = 'SF22'
TITLE = 'The Woodbird Leads'
KIND = 'show'
DESCRIPTION = ('The bird sings of a bride asleep on a mountain inside a ring of fire. Siegfried has to find her, '
               'and he races after the bird across the whole house and away.')
VOICEOVER = ('The little bird sings of a bride, asleep on a mountain, inside a ring of fire. '
             'Siegfried runs after it.')

K = 11                                      # this scene's place on Act II's shared clock: T = t + 80 K
BEAT = 0.5
T_SONG = [1.0, 14.0]                        # the bird's song
T_VISION = [5.5, 18.5]                      # the bride on her rock, ringed with fire
T_FREE = 25.0                               # Siegfried's freedom
T_DELIGHT = [32.0, 35.0]                    # the bird darting to him and away
T_HORN = 39.5                               # his horn call: the race begins
T_RUN = 41.0
T_FREE2 = 43.0
T_GONE = 53.0                               # both out of the free end of Right
T_FAR = 56.0                                # the far fire
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
SILVER = hexc('#f4f8ff')
FIRE_R = hexc('#ff2000')
FIRE_O = hexc('#ff5000')
FIRE_A = hexc('#ffb020')

DAY_LV = dict(night=0.2, day=0.7, shafts=0.75, cave=0.35, eyes=0.0)


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

    for k, t0 in enumerate(T_SONG):
        for t, m, v, d in play('woodbird', t0, 0.55, 0, 90 + 4 * k, line='melody'):
            add(t, d, m, v, 'bird', k)
        for t, m, v, d in play('woodbird', t0, 0.55, 0, 58, line='bass'):
            add(t, d, m, v, 'birdbed', k)
    for k, t0 in enumerate(T_VISION):
        for t, m, v, d in play('sleep', t0, 0.55, 0, 78 + 8 * k):
            add(t, d, m, v, 'sleep', k)
        for t, m, v, d in play('loge_flicker', t0 + 0.5, 0.4, 0, 80 + 10 * k):
            add(t, d, m, v, 'loge', k)
    for t, m, v, d in play('siegfried_freedom', T_FREE, 0.5, -12, 112):
        add(t, d, m, v, 'free', 0)
    for k, t0 in enumerate(T_DELIGHT):
        for t, m, v, d in play('innocent_delight', t0, 0.45, 0, 84, line='melody'):
            add(t, d, m, v, 'delight', k)
    for t, m, v, d in play('siegfried_horn', T_HORN, 0.32, 0, 112):
        add(t, d, m, v, 'horn')
    for t, m, v, d in play('siegfried_freedom', T_FREE2, 0.42, -12, 120):
        add(t, d, m, v, 'free', 1)
    add(T_RUN, 0.1, 'C1', 115, 'go')
    for t, m, v, d in play('forest_murmurs', T_FAR - 2, 0.55, 12, 62):
        add(t, d, m, v, 'murmurs', 0)
    for t, m, v, d in play('forest_murmurs', T_FAR + 1.25, 0.55, 12, 58):
        add(t, d, m, v, 'murmurs', 1)
    for t, m, v, d in play('loge_flicker', T_FAR + 6, 0.45, 0, 70):
        add(t, d, m, v, 'farfire', 0)
    for t, m, v, d in play('sleep', T_FAR + 11, 0.7, 0, 64):
        add(t, d, m, v, 'farsleep')
    for t, m, v, d in play('loge_flicker', T_FAR + 17, 0.45, 0, 74):
        add(t, d, m, v, 'farfire', 1)
    for m in ('E2', 'B2', 'E3'):
        add(0.0, D, m, 50, 'murmur')
    return sorted(N, key=lambda e: e[0])


def tracks(G):
    """Where the bird and Siegfried are: hops on Right, darting to him and away, then the race out of the free end."""
    N = compose()
    rng = np.random.default_rng(272)
    L = G.pd.max()
    home, him = at(G, 'Right', 0.3), at(G, 'Porch Front', 0.5)
    pts, p = [(0.0, home)], home
    for e in N:
        if e[4] == 'bird':
            p = float(np.clip(p + rng.uniform(-45, 45), at(G, 'Right', 0.08), at(G, 'Right', 0.55)))
            pts += [(e[0], pts[-1][1]), (e[0] + 0.25, p)]
    dl = [e for e in N if e[4] == 'delight']
    for k, t0 in enumerate(T_DELIGHT):        # to him and away
        pts += [(t0, pts[-1][1]), (t0 + 0.9, him + 70), (t0 + 2.2, at(G, 'Right', 0.15 + 0.1 * k))]
    hop = np.linspace(pts[-1][1], L + 80, 9)
    for j, q in enumerate(hop[1:]):
        tj = T_RUN + 0.2 + 1.3 * j
        pts += [(tj, pts[-1][1]), (tj + 0.25, float(q))]
    bird = sorted(pts, key=lambda e: e[0])
    man = [(0.0, him), (T_RUN, him), (T_GONE, L + 120)]
    return (lambda t: keys(t, bird)), (lambda t: keys(t, man)), len(dl)


def render(G, seed=22):
    F = nframes(D)
    out = np.zeros((F, G.N, 3))
    S = stage(G)
    d = S['d']
    L = d.max()
    N = compose()
    bird, man, _ = tracks(G)
    bird_on = np.array([e[0] for e in N if e[4] in ('bird', 'delight')])
    free = [e for e in N if e[4] == 'free']
    porch = S['porch']
    pc = at(G, 'Porch Front', 0.5)
    rng = np.random.default_rng(seed)
    flame = Flicker(rng, G.N, 2.5, 8.0)
    tongue = Flicker(rng, G.N, 0.6, 2.0)
    far = np.exp(-np.clip(L - d, 0, None) / 300)
    tongues = [e for e in N if e[4] in ('farfire', 'farsleep')]

    for f in range(F):
        t = f * DT
        T = t + 80 * K
        fr = forest(S, T, DAY_LV)

        # the vision: fire leaping up all over the porch with a silver sleeper at its heart; the second time the
        # fire runs out over the whole house
        for k, t0 in enumerate(T_VISION):
            a = t - t0
            if 0 <= a < 8.5:
                env = smoothstep(0, 0.8, a) * (1 - smoothstep(6.5, 8.5, a))
                reach = porch if k == 0 else porch + (1 - porch) * smoothstep(1.0, 3.5, a) * (1 - smoothstep(5.0, 7.5, a))
                heat = np.clip(0.55 + 0.45 * flame(T) + 0.3 * tongue(T), 0, 1.3)
                fr *= (1 - 0.6 * env * reach)[:, None]
                fr += light(FIRE_R, 0.7 * env * reach * heat)
                fr += light(FIRE_O, 0.75 * env * reach * np.clip(heat - 0.3, 0, None))
                fr += light(FIRE_A, 0.8 * env * reach * np.clip(heat - 0.75, 0, None) * 2)
                sleeper = np.exp(-((d - pc) / (14 + 6 * k)) ** 2)
                fr += light(SILVER, env * (0.85 + 0.15 * np.sin(2 * np.pi * 0.5 * a)) * sleeper)

        # his freedom: emerald surging out of him to both ends on every note; the top note turns the house emerald
        for t0, dur, m, v, part, k in free:
            a = t - t0
            if 0 <= a < 1.8:
                p = man(t0)
                fr += light(SIEGFRIED, 0.95 * np.exp(-a / 0.8) * np.exp(-((np.abs(d - p) - 1100 * a) / 240) ** 2))
        for t0 in (T_FREE, T_FREE2):
            a = t - t0
            if 0 <= a < 2.5:
                fr += light(SIEGFRIED, 0.75 * np.exp(-a / 0.7) * smoothstep(0, 0.1, a))

        # Siegfried, standing, then charging out along Right as an emerald comet with a long green wake
        pm = man(t)
        if pm < L + 100:
            run = smoothstep(T_RUN, T_RUN + 1, t)
            for j in range(8):
                q = man(t - 0.06 * (j + 1))
                fr += light(SIEGFRIED, run * 0.7 * (1 - j / 8) * np.exp(-((d - q) / 22) ** 2))
            fr = figure(fr, S, pm, SIEGFRIED, 0.8 + 0.2 * run)
            fr += light(HEAD, 0.7 * np.exp(-((d - pm) / 4) ** 2))
            fr += light(GOLD, 0.8 * np.exp(-((d - pm - 9) / 4) ** 2))
        if T_RUN <= t < T_GONE + 4:              # the wake: the house swept green behind him, then settling
            behind = smoothstep(pm + 30, pm - 200, d) * (d > pc - 200)
            fr += light(SIEGFRIED, 0.5 * behind * (1 - smoothstep(T_GONE, T_GONE + 4, t)))

        # the bird: flashes rippling out on each note
        if bird(t) < L + 70:
            i = int(np.searchsorted(bird_on, t, side='right')) - 1
            if i >= 0 and t - bird_on[i] < 0.8:
                a = t - bird_on[i]
                fr += light(BIRD, 0.6 * np.exp(-a / 0.3) * np.exp(-((np.abs(d - bird(t)) - 500 * a) / 50) ** 2))
            fr = woodbird(fr, S, bird, t, 0.95, T)

        # far off at the free end of Right: the fire on the rock, pulsing and growing
        if t >= T_FAR - 2:
            grow = smoothstep(T_FAR - 2, D - 6, t)
            pulse = 0.75 + 0.25 * np.sin(2 * np.pi * 0.6 * t)
            heat = np.clip(0.6 + 0.4 * flame(T), 0, 1)
            fr += light(FIRE_O, (0.6 + 0.4 * grow) * pulse * far * heat)
            fr += light(FIRE_A, (0.4 + 0.5 * grow) * pulse * far ** 3 * heat)
            fr += light(FIRE_R, (0.3 + 0.4 * grow) * far ** 0.4 * (G.seg_of == 'Right'))
            # the fire licking back along Right toward the porch on every note of Loge's flicker
            for t0, dur, m, v, part, k in tongues:
                a = t - t0
                if 0 <= a < 1.6:
                    fr += light(FIRE_O, (0.7 + 0.2 * grow) * np.exp(-a / 0.6)
                                * np.exp(-((d - (L - 700 * a)) / 90) ** 2))
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

    for name, gain, rev in (('low', 0.25, 0.25), ('brass', 0.25, 0.3), ('perc', 0.23, 0.28), ('winds', 0.26, 0.32),
                            ('strings', 0.2, 0.35), ('mallet', 0.15, 0.35)):
        M.bus(name, gain=gain, reverb=rev)
    fl = M.sampler('Woodwinds/Flute/susNV/*.wav', tune=-12)
    ob_st = M.sampler('Woodwinds/Oboe/Stacc/*.wav', tune=-12)
    cl = M.sampler('Woodwinds/Clarinet/susLong/*.wav', tune=-12)
    pic = M.sampler('Woodwinds/Piccolo/Stac/*.wav', tune=-12)
    horn = M.sampler('Brass/F Horn/sus/*.wav', tune=-12)
    vtrem = M.sampler('Strings/Violin Section/Trem/*.wav', tune=-12)
    vsp = M.sampler('Strings/Violin Section/Spic/*.wav', tune=-12)
    vc = M.sampler('Strings/Cello Section/susvib/*.wav', tune=-12)
    harp = M.sampler('Strings/Harp/*.wav')
    glock = M.sampler('Percussion/Glock/*.wav')
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

    bird, man, _ = tracks(G)
    cave = pan_at(at(G, 'Porch Front', 0.5))
    end = pan_at(G.pd.max())
    for t, d, m, v, part, k in compose():
        pb = pan_at(min(bird(t), G.pd.max()))
        ps = pan_at(min(man(t), G.pd.max()))
        if part in ('bird', 'delight'):
            M.add('winds', fl.play(m, v, dur=d * 1.1, release=0.15), t, 0.9, pb)
            M.add('winds', ob_st.play(m, v - 22), t, 0.35, pb)
        elif part == 'birdbed':
            M.add('strings', harp.play(m, v), t, 0.6, pb)
        elif part == 'sleep':
            if d > 1.0:
                hold('winds', cl, m, t, t + d, v, cave, rise=0.3, fall=1.0, gain=0.7)
            else:
                M.add('winds', cl.play(m, v, dur=d * 1.05, release=0.3), t, 0.75, cave)
        elif part == 'loge':
            M.add('strings', vsp.play(m, v), t, 0.7, cave)
            M.add('mallet', glock.play(m + 12, v - 20), t, 0.5, cave)
            M.add('winds', pic.play(m + 12, v - 24), t, 0.3, cave)
        elif part == 'free':
            if d > 1.0:
                hold('brass', horn, m, t, t + d, v, ps, rise=0.1, fall=0.8, gain=0.9)
            else:
                M.add('brass', horn.play(m, v, dur=d * 1.05, release=0.3), t, 0.95, ps)
            M.add('strings', vc.play(m - 12, v - 16, dur=d * 1.05, release=0.3), t, 0.5, ps)
            if t in (T_FREE, T_FREE2):
                M.add('perc', crash.play(110), t, 0.7, ps)
                M.add('perc', timp.play(110, pitch=-3), t, 0.8, ps)
        elif part == 'horn':
            M.add('brass', horn.play(m, v, dur=d * 1.1, release=0.3), t, 1.0, ps)
        elif part == 'go':
            M.add('perc', timp.play(v, pitch=-5), t, 0.8, ps)
        elif part == 'murmurs':
            M.add('strings', vsp.play(m, v), t, 0.55, (-1) ** int(t * 4) * 0.4)
        elif part == 'farfire':
            M.add('strings', vsp.play(m, v), t, 0.55, end)
            M.add('mallet', glock.play(m + 12, v - 24), t, 0.4, end)
        elif part == 'farsleep':
            if d > 1.0:
                hold('winds', cl, m, t, t + d, v, end * 0.7, rise=0.5, fall=1.0, gain=0.55)
            else:
                M.add('winds', cl.play(m, v, dur=d * 1.05, release=0.3), t, 0.6, end * 0.7)
        elif part == 'murmur':
            hold('strings', vtrem, m + 12, t, t + d, v, 0.0, rise=3.0, fall=2.0, gain=0.2)
