"""The Hunt: the valley on the Rhine as GD22 left it, Siegfried alone on the bank with the Ring glinting. Hunting horns
in the forest: his own call (Donington 48) answered from Left, Left flashing at each, and the hunt pours out of the
forest from the front corner of Left, the vassals' torches streaming in along Left and the porch to stand all over
it. Hagen comes in ultraviolet in a pool of black to Porch Left, Gunther in royal gold to Porch Front, and Siegfried
strides from the bank to the middle of the porch. The vassals' call (54) on the trombones sends every torch flaring.

Then he tells them his story, and each part of it takes over the whole house. Mime's forge: the house roars orange,
and every hammer blow of the forging motif (52) flashes white on the porch and throws sparks to both ends. The
dragon: the forging dies into Fafner's crawl (57), ochre waves heaving out over the house with two red eyes on the
porch, a fire blast down Left and the white stroke of the sword. The Woodbird: the house goes hard green and a
magenta bird darts everywhere on its song (27), every note a pop of magenta. Hagen hands him a drink, the potion's
chords (19) running violet from Hagen to him, and he remembers Brünnhilde: the fire flares round the porch with
silver at its heart and her motif (88) sweeps silver and gold end to end. The story fades back into the valley, and
Hagen has moved round behind him.

compose() holds every note; stage(), scene(), water(), figure(), torches(), sparks() and ring() are the valley,
shared word for word by Act III's scenes (GD22 to GD30) on a clock that runs on from scene to scene: T = t + 80 K."""
import numpy as np
from pixelhome.audio import note
from pixelhome.fx import DT, hexc, light, smoothstep, nframes, keys, Flicker, smooth_noise, colormap
from pixelhome.leitmotifs import play

CODE = 'GD23'
TITLE = 'The Hunt'
KIND = 'show'
DESCRIPTION = ('The hunting party finds Siegfried by the river, and he tells them his story: the forge, the dragon, '
               'the bird. Then Hagen hands him a drink, and he remembers Brünnhilde.')
VOICEOVER = ('The hunters gather by the river, and Siegfried tells them his story. '
             'The forge. The dragon. The bird. And then, a woman asleep in the fire.')

K = 1                                       # this scene's place on Act III's shared clock: T = t + 80 K
T_HORNS = [0.8, 3.4, 6.0]                   # hunting horns, his and theirs
T_POUR = (1.5, 9.0)                         # the hunt pours out of the forest
T_VASSALS = 9.5
STORY = dict(forge=(12.5, 27.0), dragon=(27.5, 42.0), bird=(42.5, 56.5), brunn=(63.0, 76.0))
T_FORGE = [13.5, 17.0, 20.5]
T_MIME = 24.0
T_DRAGON = 28.5
T_BLAST = 36.5
T_SWORD = 39.0
T_BIRD = [43.5, 49.5]
T_POTION = 57.0
T_BRUNN = [64.0, 69.0]
D = 80.0

SIEGFRIED = hexc('#00ff40')
HEAD = hexc('#e8ffe8')
GOLD = hexc('#ffaa00')
HAGEN = hexc('#7a00ff')
GUNTHER = hexc('#ffb020')
FORGE = hexc('#ff4a08')
HEAT = hexc('#fff0a0')
SPARK = hexc('#ffb020')
SCALE = hexc('#c88a20')
EYE = hexc('#ff0000')
STEEL = hexc('#e8f8ff')
GREEN = hexc('#20ff30')
BIRD = hexc('#ff30d0')
POTION = hexc('#a050ff')
SILVER = hexc('#f4f8ff')
GLINT = hexc('#ffd060')
MIME = hexc('#e0c800')

START = dict(river=0.72, forest=0.62, sun=0.75, night=0.0, pyre=0.0, blaze=0.0, valhalla=0.0, flood=0.0)
END = dict(START)                           # where GD24 picks the valley up
SIEG = (('Right', 0.15), ('Porch Front', 0.65), 0.85)   # Siegfried from, to, level
HAGEN_AT = (('Porch Left', 0.2), ('Porch Front', 0.85), 0.8)
GUNTHER_AT = ('Porch Front', 0.3, 0.7)
TORCHES = 0.5                               # the vassals' torch level at the end

RIVER_DEEP = hexc('#0c1c8c')
RIVER_TEAL = hexc('#0a7c8a')
RIVER_GREEN = hexc('#14c080')
FOAM = hexc('#c0f4ff')
FOREST = hexc('#18a020')
SUN = hexc('#ffd040')
NIGHT = hexc('#1a2a90')
RED, ORANGE, AMBER = hexc('#ff2000'), hexc('#ff5000'), hexc('#ffb020')
FIRE = colormap([(0.0, hexc('#300400')), (0.3, RED), (0.55, ORANGE), (0.8, AMBER), (1.0, hexc('#fff0b0'))])
VALHALLA = hexc('#fff0a0')
VBLUE = hexc('#1a3cff')
TORCH = hexc('#ff6a10')
WHITE = hexc('#ffffff')


def at(G, seg, u):
    """Path distance u of the way along a segment."""
    s = G.pd[G.seg[seg]]
    return float(s.min() + u * (s.max() - s.min()))


def stage(G):
    """The Rhine valley as profiles over the house: the river along Right and the Side (flowing out toward the free
    end of Right, and back along the Side), the forest over Left and the porch, the porch also the pyre to come."""
    d = G.pd
    rng = np.random.default_rng(1876)       # the same river, trees and torches in every scene, so the cuts match
    river = np.isin(G.seg_of, ['Right', 'Side'])
    porch = np.isin(G.seg_of, ['Porch Left', 'Porch Front', 'Porch Right'])
    pf = at(G, 'Porch Front', 0.5)
    return dict(
        d=d, L=float(d.max()), pf=pf, river=river, porch=porch, land=~river,
        flow=np.where(G.seg_of == 'Side', -1.0, 1.0),
        trees=(~river) * (0.6 + 0.4 * smooth_noise(rng, d, 35.0)),
        pyre=porch * (0.45 + 0.55 * np.exp(-((d - pf) / 170) ** 2)),
        torch_at=np.sort(rng.uniform(at(G, 'Left', 0.05), at(G, 'Right', 0.6), 28)),
        torch_ph=rng.uniform(0, 2 * np.pi, 28),
        leaf=Flicker(rng, G.N, 0.1, 0.6),
        fl=Flicker(rng, G.N, 4.0, 11.0),
        sparkle=Flicker(rng, G.N, 1.5, 4.0),
    )


def heat(d, T):
    """Flame heat along the roofline (0..1): tongues of several sizes licking both ways."""
    h = (0.45 + 0.24 * np.sin(2 * np.pi * (d / 173 - 0.53 * T)) + 0.2 * np.sin(2 * np.pi * (d / 109 + 0.71 * T) + 1.3)
         + 0.13 * np.sin(2 * np.pi * (d / 67 - 1.37 * T) + 2.1) + 0.09 * np.sin(2 * np.pi * (d / 41 + 1.9 * T) + 0.4))
    swell = 0.75 + 0.25 * np.sin(2 * np.pi * (d / 410 + 0.23 * T)) * np.sin(2 * np.pi * (d / 260 - 0.31 * T) + 0.7)
    return np.clip((h * swell - 0.15) * 1.5, 0, 1)


def water(S, T, lvl, where):
    """The Rhine's colour at level lvl over the pixels in `where` (0..1): currents in indigo, teal and green."""
    d, fw = S['d'], S['flow']
    u = 0.5 + 0.3 * np.sin(2 * np.pi * (d / 230 - fw * 0.45 * T)) + 0.2 * np.sin(2 * np.pi * (d / 97 - fw * 0.8 * T) + 1.0)
    col = np.where((u < 0.5)[:, None], RIVER_DEEP + (RIVER_TEAL - RIVER_DEEP) * (2 * u)[:, None],
                   RIVER_TEAL + (RIVER_GREEN - RIVER_TEAL) * (2 * u - 1).clip(0, 1)[:, None])
    fr = light(col, lvl * where * (0.65 + 0.35 * u))
    return fr + light(FOAM, 0.5 * lvl * where * np.clip(S['sparkle'](T) - 1.1, 0, None))


def scene(S, T, lv):
    """The valley at shared time T with levels lv: river, forest, sun (shafts through the trees), night (a dark blue
    over everything), pyre (fire on the porch), blaze (fire on every run), valhalla (gold-white burning on the
    porch), flood (0..1, the Rhine's reach in from the free end of Right over everything)."""
    d, L = S['d'], S['L']
    front = L - lv['flood'] * (L + 60)
    wet = smoothstep(front - 40, front + 40, d) if lv['flood'] > 0 else np.zeros_like(d)
    dry = 1 - wet
    fr = water(S, T, lv['river'], S['river'] * dry)
    fr += light(FOREST, lv['forest'] * S['trees'] * (0.8 + 0.2 * S['leaf'](T)) * dry)
    shafts = np.clip(np.sin(2 * np.pi * (d / 330 + 0.04 * T)) * np.sin(2 * np.pi * (d / 127 - 0.07 * T) + 0.5), 0, 1)
    fr += light(SUN, lv['sun'] * S['land'] * shafts * dry)
    fr += light(NIGHT, lv['night'] * dry)
    q = np.clip(heat(d, T) + 0.18 * S['fl'](T), 0, 1)
    flames = (lv['pyre'] * S['pyre'] + lv['blaze'] * (1 - S['porch'] * (1 - S['pyre']))) * dry
    fr += light(FIRE(q), flames * (0.45 + 0.7 * q))
    fr += light(VALHALLA, lv['valhalla'] * S['pyre'] * (0.75 + 0.25 * q) * dry)
    fr += water(S, T, 0.9, wet) + light(FOAM, 0.9 * np.exp(-((d - front) / 30) ** 2) * (lv['flood'] > 0))
    return fr


def figure(fr, S, p, col, lvl, w=16.0):
    """A person at path distance p: a body that stands in front of the scene, and a halo."""
    body = np.exp(-((S['d'] - p) / w) ** 2)
    fr = fr * (1 - 0.85 * min(1.0, lvl / 0.2) * body)[:, None]
    return fr + light(col, lvl * body) + light(col, 0.35 * lvl * np.exp(-((S['d'] - p) / (3 * w)) ** 2))


def torches(fr, S, T, lvl, n=28, pull=None, k=0.0):
    """The vassals: n flickering torch points (pulled a share k of the way toward path distance `pull`)."""
    d = S['d']
    for p, ph in zip(S['torch_at'][:n], S['torch_ph'][:n]):
        if pull is not None:
            p = p + (pull - p) * k
        f = 0.8 + 0.2 * np.sin(7.3 * T + ph) * np.sin(3.1 * T + 2 * ph)
        fr = fr + light(TORCH, lvl * f * np.exp(-((d - p) / 6) ** 2)) + light(TORCH, 0.3 * lvl * np.exp(-((d - p) / 22) ** 2))
    return fr


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


def ring(fr, S, t, t0, p, col, lvl, speed=1400.0, width=90.0, tau=0.9):
    """A shockwave from path distance p started at t0, out to both ends."""
    a = t - t0
    if a < 0 or a > 4 * tau:
        return fr
    return fr + light(col, lvl * np.exp(-a / tau) * np.exp(-((np.abs(S['d'] - p) - speed * a) / width) ** 2))


def hold_factory(M, SR):
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
    return hold


def panner(G):
    order = np.argsort(G.pd)
    xs, ds = G.pos[order, 0], G.pd[order]
    x0, x1 = xs.min(), xs.max()

    def pan_at(dd):                         # path distance -> left/right across the facade, from the street
        x = np.interp(dd, ds, xs)
        return float(0.85 * (2 * (x - x0) / (x1 - x0) - 1))
    return pan_at


def compose():
    """Every note: (time, seconds, midi, velocity, part, k)."""
    N = []

    def add(t, d, m, v, part, k=None):
        N.append((float(t), float(d), note(m) if isinstance(m, str) else int(m), int(v), part, k))

    for j, t0 in enumerate(T_HORNS):
        for t, m, v, d in play('siegfried_horn', t0, 0.3, (5, 0, 7)[j], 100 - 6 * (j == 1)):
            add(t, d, m, v, 'horn', j)
    for t, m, v, d in play('vassals', T_VASSALS, 0.5, -12, 106):
        add(t, d, m, v, 'vassals')
    for j, t0 in enumerate(T_FORGE):
        for t, m, v, d in play('forging', t0, 0.5, 0, 104 + 4 * j):
            add(t, d, m, v, 'forging', j)
    for t, m, v, d in play('mime', T_MIME, 0.42, -12, 88):
        add(t, d, m, v, 'mime')
    for t, m, v, d in play('fafner', T_DRAGON, 0.5, 0, 108):
        add(t, d, m, v, 'dragon')
    add(T_BLAST, 1.6, 'C2', 118, 'blast')
    for t, m, v, d in play('nothung', T_SWORD, 0.45, 0, 112):
        add(t, d, m, v, 'sword')
    for j, t0 in enumerate(T_BIRD):
        for t, m, v, d in play('woodbird', t0, 0.62, 0, 92 + 6 * j):
            add(t, d, m, v, 'bird', j)
    for t, m, v, d in play('potion', T_POTION, 0.36, -12, 92):
        add(t, d, m, v, 'potion')
    for j, t0 in enumerate(T_BRUNN):
        for t, m, v, d in play('brunnhilde', t0, 0.6, 0, 100 + 8 * j):
            add(t, d, m, v, 'brunn', j)
    add(T_BRUNN[0] - 1.0, 14.0, 'E1', 70, 'firebed')
    add(76.0, 4.0, 'Ab1', 60, 'flow')
    return sorted(N, key=lambda e: e[0])


def where(G, t):
    """Siegfried, Hagen and Gunther at time t: (path distance, level) each."""
    s = at(G, *SIEG[0]) + (at(G, *SIEG[1]) - at(G, *SIEG[0])) * smoothstep(4.0, 10.0, t)
    h0, h1, h2 = at(G, 'Left', 0.0), at(G, *HAGEN_AT[0]), at(G, *HAGEN_AT[1])
    h = h0 + (h1 - h0) * smoothstep(T_POUR[0] + 1, T_POUR[1], t)
    h = h + (h2 - h) * smoothstep(70.0, 78.0, t)
    g0, g1 = at(G, 'Left', 0.0), at(G, *GUNTHER_AT[:2])
    g = g0 + (g1 - g0) * smoothstep(T_POUR[0] + 2, T_POUR[1] + 1, t)
    return ((s, SIEG[2]), (h, HAGEN_AT[2] * smoothstep(T_POUR[0] + 1, T_POUR[0] + 2.5, t)),
            (g, GUNTHER_AT[2] * smoothstep(T_POUR[0] + 2, T_POUR[0] + 3.5, t)))


def tableau(t, name):
    a, b = STORY[name]
    return smoothstep(a, a + 1.0, t) * (1 - smoothstep(b - 1.2, b, t))


def render(G, seed=23):
    rng = np.random.default_rng(seed)
    F = nframes(D)
    out = np.zeros((F, G.N, 3))
    S = stage(G)
    d, L = S['d'], S['L']
    N = compose()
    notes = {p: [e for e in N if e[4] == p] for p in
             ('horn', 'vassals', 'forging', 'mime', 'dragon', 'sword', 'bird', 'potion', 'brunn')}
    anvil = S['pf']
    blows = [(e[0], 1.0, anvil) for e in notes['forging'] if e[2] < note('C3')]
    blow_t = np.array([b[0] for b in blows])
    bird_hops = [(e[0], float(rng.uniform(at(G, 'Left', 0.05), L - 30))) for e in notes['bird'] if e[2] >= note('B4')]
    runs = ['Left', 'Porch Left', 'Porch Front', 'Porch Right', 'Right', 'Side']
    lo, hi = note('Eb2'), note('Gb3')

    for f in range(F):
        t = f * DT
        T = t + 80 * K
        tb = max(tableau(t, k) for k in STORY)
        lv = {k: v * (1 - 0.7 * tb) for k, v in START.items()}
        fr = scene(S, T, lv)
        (ps, ls), (ph, lh), (pg, lg) = where(G, t)

        # the hunting horns: Left flashes at each call, the torches stream out of the forest
        for j, t0 in enumerate(T_HORNS):
            a = t - t0
            if 0 <= a < 1.5:
                fr += light(SIEGFRIED if j != 1 else TORCH, 0.85 * np.exp(-a / 0.45) * (G.seg_of == 'Left'))
        pour = smoothstep(*T_POUR, t)
        tl = TORCHES * smoothstep(T_POUR[0], T_POUR[0] + 1.5, t) * (1 - 0.4 * tb)
        for t0, dur, m, v, _, k in notes['vassals']:
            if 0 <= t - t0 < 0.6:
                tl += 0.5 * np.exp(-(t - t0) / 0.2)
        fr = torches(fr, S, T, tl, pull=at(G, 'Left', 0.0), k=1 - pour)

        # the forge: the house roars orange, every blow a white flash on the porch and sparks to both ends
        g = tableau(t, 'forge')
        if g > 0:
            fr += light(FORGE, 0.6 * g * (0.75 + 0.25 * S['fl'](T)))
            i = int(np.searchsorted(blow_t, t, side='right')) - 1
            if i >= 0 and t - blow_t[i] < 1.0:
                a = t - blow_t[i]
                fr += light(HEAT, g * min(1.0, 1.2 * np.exp(-a / 0.1)) * np.exp(-((d - anvil) / 40) ** 2))
                fr = ring(fr, S, t, blow_t[i], anvil, FORGE, 0.9 * g, speed=1500, width=80, tau=0.5)
            fr += light(SPARK, g * np.clip(sparks(S, blows, t, 23), 0, 1))
            for t0, dur, m, v, _, k in notes['mime']:
                a = t - t0
                if 0 <= a < 0.5:
                    fr = figure(fr, S, at(G, 'Porch Front', 0.3), MIME, 0.8 * g * np.exp(-a / 0.3))

        # the dragon: ochre waves heaving out over the house, red eyes on the porch, the fire blast, the sword
        g = tableau(t, 'dragon')
        if g > 0:
            fr += light(SCALE, 0.25 * g)
            for t0, dur, m, v, _, k in notes['dragon']:
                a = t - t0
                if 0 <= a < 2.4:
                    u = (m - lo) / (hi - lo)
                    r = (400 + 1100 * u) * (1 - np.exp(-a / 0.7))
                    fr += light(SCALE, g * (0.8 + 0.3 * u) * np.exp(-a / 1.0) * np.exp(-((np.abs(d - anvil) - r) / (110 + 90 * u)) ** 2))
            eye = g * (0.6 + 0.4 * smoothstep(T_DRAGON + 4, T_DRAGON + 6, t))
            for u in (0.4, 0.6):
                fr += light(EYE, eye * np.exp(-((d - at(G, 'Porch Front', u)) / 6) ** 2))
            a = t - T_BLAST
            if 0 <= a < 2.5:
                front = at(G, 'Porch Left', 0.5) - 1200 * a
                q = np.clip(heat(d, T) + 0.3, 0, 1)
                flame = smoothstep(front - 60, front + 60, d) * (d < at(G, 'Porch Left', 0.5)) * np.exp(-max(a - 1.2, 0) / 0.5)
                fr += light(FIRE(q), g * 1.0 * flame)
            for t0, dur, m, v, _, k in notes['sword']:
                a = t - t0
                if 0 <= a < 1.0:
                    fr += light(STEEL, g * 0.9 * np.exp(-a / 0.2) * np.exp(-((np.abs(d - ps) - 1600 * a) / 60) ** 2))
            if 0 <= t - (T_SWORD + 2.2) < 0.6:
                fr += light(WHITE, g * 0.6 * np.exp(-(t - T_SWORD - 2.2) / 0.12))

        # the Woodbird: hard green, a magenta bird darting everywhere, every note a pop
        g = tableau(t, 'bird')
        if g > 0:
            fr += light(GREEN, 0.55 * g * (0.8 + 0.2 * S['leaf'](T)))
            j = max([i for i, (t0, p) in enumerate(bird_hops) if t0 <= t], default=-1)
            if j >= 0:
                t0, p = bird_hops[j]
                prev = bird_hops[j - 1][1] if j > 0 else L
                p = prev + (p - prev) * smoothstep(t0, t0 + 0.2, t)
                a = t - t0
                fr += light(BIRD, g * 1.0 * np.exp(-a / 0.4) * np.exp(-((d - p) / (40 + 450 * a)) ** 2))
                fr = ring(fr, S, t, t0, p, BIRD, 0.7 * g, speed=1200, width=50, tau=0.35)
                fr = figure(fr, S, p, BIRD, g, w=8)
                fr += light(WHITE, g * 0.8 * np.exp(-((d - p) / 3) ** 2))

        # the potion: violet chords running from Hagen to him
        for t0, dur, m, v, _, k in notes['potion']:
            a = t - t0
            if 0 <= a < dur + 0.8 and m >= note('G3'):
                lo_, hi_ = min(ph, ps), max(ph, ps)
                u = min(1.0, a / 0.8)
                tip = ph + (ps - ph) * u
                band = (d >= min(ph, tip) - 10) * (d <= max(ph, tip) + 10)
                fr += light(POTION, 0.85 * np.exp(-max(a - 0.8, 0) / 1.0) * band)
                fr += light(POTION, 0.4 * np.exp(-a / 1.2) * np.exp(-((np.abs(d - ps) - 600 * a) / 140) ** 2))

        # he remembers Brünnhilde: the fire round the porch, silver at its heart, silver and gold sweeping
        g = tableau(t, 'brunn')
        if g > 0:
            q = np.clip(heat(d, T) + 0.18 * S['fl'](T), 0, 1)
            fr += light(FIRE(q), 0.9 * g * S['pyre'] * (0.45 + 0.7 * q))
            fr += light(SILVER, 0.9 * g * np.exp(-((d - anvil) / 25) ** 2))
            for j, (t0, dur, m, v, _, k) in enumerate(notes['brunn']):
                a = t - t0
                if 0 <= a < 2.0:
                    col = SILVER if j % 2 == 0 else GLINT
                    fr += light(col, g * 0.85 * np.exp(-a / 0.6) * np.exp(-((np.abs(d - anvil) - 1300 * a) / 120) ** 2))
                    fr += light(col, g * 0.5 * np.exp(-a / 0.35) * (G.seg_of == runs[j % 6]))

        # the people: Hagen in a pool of black, Gunther, and Siegfried with the Ring
        if lh > 0:
            fr = fr * (1 - 0.6 * lh * np.exp(-((d - ph) / 70) ** 2))[:, None]
            fr = figure(fr, S, ph, HAGEN, lh)
        if lg > 0:
            fr = figure(fr, S, pg, GUNTHER, lg)
        tell = 0.12 * np.sin(2 * np.pi * t / 0.9) * tb
        fr = figure(fr, S, ps, SIEGFRIED, min(1.0, ls * (1 + tell)))
        fr += light(HEAD, 0.7 * ls * np.exp(-((d - ps) / 6) ** 2))
        fr += light(GOLD, 0.6 * np.exp(-((d - ps - 14) / 5) ** 2))
        out[f] = fr
    return np.clip(out, 0, 1)


def score(M, G):
    from pixelhome.audio import SR, whoosh
    pan_at = panner(G)
    for name, gain, rev in (('low', 0.28, 0.25), ('strings', 0.24, 0.32), ('winds', 0.26, 0.35), ('brass', 0.28, 0.3),
                            ('perc', 0.26, 0.28), ('mallet', 0.18, 0.3)):
        M.bus(name, gain=gain, reverb=rev)
    hold = hold_factory(M, SR)
    horn = M.sampler('Brass/F Horn/sus/*.wav', tune=-12)
    tbn = M.sampler('Brass/Tenor Trombone/sus/*.wav', tune=-12)
    tuba = M.sampler('Brass/Tuba/sus/*.wav', tune=-12)
    tpt = M.sampler('Brass/Trumpet/sus/*.wav', tune=-12)
    cb = M.sampler('Strings/Solo Contrabass/SusNV/*.wav', tune=-12)
    vc = M.sampler('Strings/Cello Section/susvib/*.wav', tune=-12)
    vln = M.sampler('Strings/Violin Section/susVib/*.wav', tune=-12)
    flute = M.sampler('Woodwinds/Flute/susvib/*.wav', tune=-12)
    oboe = M.sampler('Woodwinds/Oboe/Vib/*.wav', tune=-12)
    clar = M.sampler('Woodwinds/Clarinet/susLong/*.wav', tune=-12)
    bsn = M.sampler('Woodwinds/Bassoon/stac/*.wav', tune=-12)
    xylo = M.sampler('Percussion/Xylo/*.wav')
    harp = M.sampler('Strings/Harp/*.wav')
    anvil = M.hits('Percussion/Anvil_Hit1_*.wav')
    timp = M.hits('Percussion/Timpani/Timpani1_Hit*.wav')
    crash = M.hits('Percussion/cymbal-crash1_f*.wav')
    left = pan_at(at(G, 'Left', 0.3))
    porch = pan_at(at(G, 'Porch Front', 0.5))
    sieg = pan_at(at(G, *SIEG[1]))
    for t, d, m, v, part, k in compose():
        if part == 'horn':
            p = left if k != 0 else pan_at(at(G, *SIEG[0]))
            M.add('brass', horn.play(m, v, dur=d * 1.05, release=0.3), t, 0.9, p)
        elif part == 'vassals':
            M.add('brass', tbn.play(m, v, dur=d * 1.05, release=0.2), t, 0.9, porch)
            if m < note('C3'):
                M.add('perc', timp.play(v - 14, pitch=-3), t, 0.5, porch)
        elif part == 'forging':
            if m < note('C3'):
                M.add('low', tuba.play(m, v, dur=d * 1.1, release=0.2), t, 0.85, porch)
                M.add('perc', anvil.play(min(127, v + 8)), t, 0.85, porch)
            elif m < note('C4'):
                M.add('brass', tbn.play(m, v, dur=d * 1.05, release=0.2), t, 0.85, porch)
            else:
                M.add('brass', horn.play(m - 12, v, dur=d * 1.05, release=0.25), t, 0.8, porch)
        elif part == 'mime':
            M.add('mallet', xylo.play(m + 12, v), t, 0.7, pan_at(at(G, 'Porch Front', 0.3)))
            M.add('winds', bsn.play(m, v), t, 0.8, pan_at(at(G, 'Porch Front', 0.3)))
        elif part == 'dragon':
            M.add('low', tuba.play(m, v, dur=d * 1.1, release=0.3), t, 0.95, porch)
            M.add('low', cb.play(m, v - 8, dur=d * 1.1, release=0.3), t, 0.7, porch)
        elif part == 'blast':
            M.add('perc', crash.play(v), t, 0.7, left)
            M.add('perc', whoosh(1.6, 300, 4000, 0.8, seed=5), t, 0.9, left)
            M.add('perc', timp.play(v, pitch=-6), t, 0.8, porch)
        elif part == 'sword':
            M.add('brass', tpt.play(m - 12, v, dur=d * 1.05, release=0.3), t, 0.85, sieg)
        elif part == 'bird':
            if m >= note('B4'):
                M.add('winds', (flute if k == 0 else oboe).play(m - 12, v, dur=d * 1.1, release=0.2), t, 0.85, 0.0)
            else:
                M.add('strings', harp.play(m, v - 16), t, 0.6, 0.0)
        elif part == 'potion':
            if m >= note('G3'):
                hold('winds', clar, m, t, t + d, v, pan_at(at(G, *HAGEN_AT[0])), rise=0.4, fall=1.0, gain=0.8)
            else:
                hold('low', vc, m, t, t + d, v - 10, porch, rise=0.4, fall=1.0, gain=0.6)
        elif part == 'brunn':
            if d > 1.0:
                hold('brass', horn, m - 12, t, t + d, v, porch, rise=0.2, fall=1.0, gain=0.85)
            else:
                M.add('brass', horn.play(m - 12, v, dur=d * 1.05, release=0.3), t, 0.9, porch)
            M.add('strings', vln.play(m, v - 14, dur=d * 1.1, release=0.3), t, 0.6, porch)
        elif part == 'firebed':
            for mm in (m, m + 7, m + 12):
                hold('low', cb, mm, t, t + d, v, porch, rise=1.5, fall=2.0, gain=0.5)
            for j in range(20):
                M.add('mallet', harp.play(note(('E4', 'Ab4', 'B4', 'E5')[j % 4]), 64), t + 0.6 * j, 0.6, porch)
        elif part == 'flow':
            hold('low', cb, m, t, t + d, v, 0.5, rise=1.5, fall=1.0, gain=0.5)
    M.add('perc', crash.play(110), STORY['forge'][0] + 1.0, 0.5, porch)
    M.add('perc', timp.play(116, pitch=-6), STORY['dragon'][0] + 1.0, 0.8, porch)
