"""The Rhinemaidens: a wooded valley on the Rhine, bright afternoon. The river runs along Right and down the Side in
racing currents of indigo, teal and green with foam glinting on them; the forest is over Left and the porch, gold
shafts of sun sliding through it. Woglinde in silver, Wellgunde in sea green and Flosshilde in violet surface out
of the water on Right and play on their song (Donington 26): every note a dart along the river and a ripple of
their colour running the length of both river runs, and on their joy (32) they chase each other end to end of Right
with the whole river flashing.

Siegfried's horn sounds from the forest (48), an emerald flash on Left, and he strides out along the porch to the
bank, lost on the hunt. The maidens circle in on him and the Rheingold (31) surges gold up both river runs: give
us the Ring. The Ring (8) on his hand throws gold rings out over the house. He laughs, his strength (53) blasting
emerald from end to end twice, whole runs at a time. Then they warn him: the Curse (13) turns the whole river
blood violet, wave on wave, and the power of fate (84) rolls indigo out from him. They dive and stream away out of
the free end of Right, the river runs bright again, and he stands alone on the bank with the gold on his hand.

compose() holds every note; stage(), scene(), water(), figure(), torches(), sparks() and ring() are the valley,
shared word for word by Act III's scenes (GD22 to GD30) on a clock that runs on from scene to scene: T = t + 80 K."""
import numpy as np
from pixelhome.audio import note
from pixelhome.fx import DT, hexc, light, smoothstep, nframes, keys, Flicker, smooth_noise, colormap
from pixelhome.leitmotifs import play

CODE = 'GD22'
TITLE = 'The Rhinemaidens'
KIND = 'show'
DESCRIPTION = ('Three river spirits play in the Rhine and beg Siegfried for the golden Ring. He laughs at them, '
               'and they warn him he will die before the day is out.')
VOICEOVER = ('Siegfried has lost his way on the hunt, and comes to the river. '
             'Three voices in the water ask him for the Ring.')

K = 0                                       # this scene's place on Act III's shared clock: T = t + 80 K
T_SONG = [1.0, 10.0]                        # the maidens' song
T_JOY = 18.0                                # their joy: the chase
T_HORN = 25.0                               # his horn in the forest
T_WALK = (26.5, 32.0)                       # he strides out along the porch to the bank
T_GOLD = 33.0                               # the Rheingold: give us the Ring
T_RING = 40.5                               # the Ring on his hand
T_LAUGH = [48.0, 51.5]                      # he laughs: his strength
T_CURSE = 55.5                              # they warn him
T_FATE = 64.0
T_LEAVE = 67.0                              # they stream away
T_ECHO = 72.0
D = 80.0

WOGLINDE = hexc('#c0f4ff')
WELLGUNDE = hexc('#20ff90')
FLOSSHILDE = hexc('#8c60ff')
MAIDENS = [WOGLINDE, WELLGUNDE, FLOSSHILDE]
SIEGFRIED = hexc('#00ff40')
HEAD = hexc('#e8ffe8')
GOLD = hexc('#ffaa00')
BLOOD = hexc('#c00030')
FATE_C = hexc('#5a30ff')

START = dict(river=0.72, forest=0.62, sun=0.75, night=0.0, pyre=0.0, blaze=0.0, valhalla=0.0, flood=0.0)
END = dict(START)                           # where GD23 picks the valley up
SIEG_END = ('Right', 0.15, 0.85)            # Siegfried at the end: segment, u, level (the Ring glinting at 0.6)

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

    add(0.0, T_HORN, 'Ab1', 60, 'flow')
    for j, t0 in enumerate(T_SONG):
        for t, m, v, d in play('rhinemaidens', t0, 0.7, 0, 88 + 6 * j):
            add(t, d, m, v, 'song', j)
    for t, m, v, d in play('rhinemaidens_joy', T_JOY, 0.55, 0, 96):
        add(t, d, m, v, 'joy')
    for t, m, v, d in play('siegfried_horn', T_HORN, 0.32, 5, 104):
        add(t, d, m, v, 'horn')
    for t, m, v, d in play('rheingold', T_GOLD, 0.75, -12, 98):
        add(t, d, m, v, 'gold')
    for t, m, v, d in play('ring', T_RING, 0.58, 0, 92):
        add(t, d, m, v, 'ring')
    for j, t0 in enumerate(T_LAUGH):
        for t, m, v, d in play('siegfried', t0, 0.8, -12, 110 + 6 * j):
            add(t, d, m, v, 'laugh', j)
    for t, m, v, d in play('curse', T_CURSE, 0.42, 0, 108):
        add(t, d, m, v, 'curse')
    for t, m, v, d in play('fate', T_FATE, 0.62, 0, 96):
        add(t, d, m, v, 'fate')
    for t, m, v, d in play('rhinemaidens', T_ECHO, 0.6, 0, 70):
        if t < D - 1.0:
            add(t, d, m, v, 'echo')
    add(T_ECHO, D - T_ECHO, 'Ab2', 58, 'flow2')
    return sorted(N, key=lambda e: e[0])


def swim(G, t, N):
    """Where each maiden is at time t (path distances), and how bright."""
    r0, r1 = at(G, 'Right', 0.08), at(G, 'Right', 1.0)
    span = r1 - r0
    song = sorted({e[0] for e in N if e[4] in ('song', 'joy', 'gold', 'curse')})
    out = []
    for k in range(3):
        base = 0.35 + 0.25 * k + 0.12 * np.sin(2 * np.pi * t / (5.3 + 1.1 * k) + 2.0 * k)
        darts = sum(0.06 * np.sin(1.7 * j + 2.1 * k) * smoothstep(s, s + 0.25, t) for j, s in enumerate(song) if s <= t)
        u = base + darts
        chase = smoothstep(T_JOY, T_JOY + 1, t) * (1 - smoothstep(T_JOY + 6, T_JOY + 7, t))
        u = u + chase * 0.35 * np.sin(2 * np.pi * (t - T_JOY) / 3.0 + 2.1 * k)
        near = smoothstep(T_GOLD - 1.5, T_GOLD + 1.5, t) * (1 - smoothstep(T_CURSE + 7, T_LEAVE, t))
        circle = 0.12 + 0.08 * k + 0.04 * np.sin(2 * np.pi * t / 1.6 + 2.1 * k)
        u = u + (circle - u) * near
        u = u % 2
        u = u if u < 1 else 2 - u
        u = u + (1.35 - u) * smoothstep(T_LEAVE + 0.4 * k, T_LEAVE + 3.5 + 0.4 * k, t)
        lvl = smoothstep(0.2 + 0.5 * k, 1.2 + 0.5 * k, t) * (1 - smoothstep(T_LEAVE + 2.5 + 0.4 * k, T_LEAVE + 3.5 + 0.4 * k, t))
        out.append((r0 + span * u, lvl))
    return out


def walk(G, t):
    a, b = at(G, 'Left', 0.3), at(G, *SIEG_END[:2])
    return a + (b - a) * smoothstep(*T_WALK, t)


def render(G, seed=22):
    F = nframes(D)
    out = np.zeros((F, G.N, 3))
    S = stage(G)
    d, L = S['d'], S['L']
    N = compose()
    notes = {p: [e for e in N if e[4] == p] for p in ('song', 'joy', 'gold', 'ring', 'laugh', 'curse', 'fate', 'echo')}
    river = S['river']
    p_end = at(G, *SIEG_END[:2])

    for f in range(F):
        t = f * DT
        T = t + 80 * K
        lv = dict(START)
        warn = smoothstep(T_CURSE, T_CURSE + 1.0, t) * (1 - smoothstep(T_FATE + 4, T_LEAVE + 3, t))
        lv['river'] = START['river'] * (1 - 0.5 * warn)
        lv['sun'] = START['sun'] * (1 - 0.6 * warn)
        fr = scene(S, T, lv)
        swimmers = swim(G, t, N)

        # every note of their song: a ripple of the singer's colour running both ways along both river runs
        for part in ('song', 'echo', 'joy'):
            for i, (t0, dur, m, v, _, k) in enumerate(notes[part]):
                a = t - t0
                if 0 <= a < 1.4 and m >= note('Ab3'):
                    who = i % 3
                    p, lvl = swimmers[who]
                    g = (0.9 if part != 'echo' else 0.5) * np.exp(-a / 0.5)
                    dist = np.abs(d - p)
                    fr += light(MAIDENS[who], g * river * np.exp(-((dist - 900 * a) / 70) ** 2))
                    side = np.abs((d - S['L'] * 0.0) - (490 - 600 * a))
                    fr += light(MAIDENS[who], 0.7 * g * (G.seg_of == 'Side') * np.exp(-(side / 70) ** 2))
                    shore = S['land'] * np.exp(-((d - (at(G, 'Right', 0.0) - 1400 * a)) / 160) ** 2)
                    fr += light(MAIDENS[who], 0.55 * g * shore)

        # the chase: the whole river flashes in their colours, one run then the other
        if T_JOY <= t < T_JOY + 7:
            j = int((t - T_JOY) / 0.55)
            a = (t - T_JOY) % 0.55
            fr += light(MAIDENS[j % 3], 0.75 * np.exp(-a / 0.2) * river * (G.seg_of == ('Right', 'Side')[j % 2]))

        # his horn in the forest: Left flashes emerald, then he strides out to the bank
        if T_HORN <= t < T_HORN + 2.5:
            a = t - T_HORN
            fr += light(SIEGFRIED, 0.85 * np.exp(-a / 0.6) * (G.seg_of == 'Left'))

        # the Rheingold: gold surging up both river runs from the far ends
        if T_GOLD <= t < T_GOLD + 8:
            a = t - T_GOLD
            g = smoothstep(0, 0.6, a) * (1 - smoothstep(6.5, 8, a))
            u = 0.5 + 0.5 * np.sin(2 * np.pi * (d / 160 - 1.4 * a))
            fr += light(GOLD, 0.85 * g * river * u)
            fr += light(GOLD, 0.55 * g * S['land'] * np.clip(np.sin(2 * np.pi * (d / 260 + 1.1 * a)), 0, 1) ** 2)
        # the Ring: gold rings out from his hand
        for t0, dur, m, v, _, k in notes['ring']:
            if m >= note('E3'):
                fr = ring(fr, S, t, t0, walk(G, t0), GOLD, 0.8, speed=1100, width=80, tau=0.7)
        # he laughs: emerald blasts, whole runs at a time, end to end
        runs = ['Left', 'Porch Left', 'Porch Front', 'Porch Right', 'Right', 'Side']
        for j, (t0, dur, m, v, _, k) in enumerate(notes['laugh']):
            a = t - t0
            if 0 <= a < 1.4:
                fr += light(SIEGFRIED, 1.0 * np.exp(-a / 0.45) * (G.seg_of == runs[j % 6]))
                fr += light(SIEGFRIED, 0.35 * np.exp(-a / 0.3))
                fr = ring(fr, S, t, t0, walk(G, t0), HEAD, 0.7, speed=1800, width=70, tau=0.45)
        # the Curse: the whole river blood violet, wave on wave
        for t0, dur, m, v, _, k in notes['curse']:
            a = t - t0
            if 0 <= a < 2.0:
                fr += light(BLOOD, 0.8 * np.exp(-a / 0.7) * river * (0.6 + 0.4 * np.sin(2 * np.pi * (d / 200 + 2 * a))))
                fr += light(BLOOD, 0.85 * np.exp(-a / 0.6) * S['land'] * np.exp(-((np.abs(d - p_end) - 900 * a) / 200) ** 2))
        # fate: indigo rolling out from him
        for t0, dur, m, v, _, k in notes['fate']:
            if m >= note('Ab3'):
                fr = ring(fr, S, t, t0, p_end, FATE_C, 1.0, speed=900, width=220, tau=1.3)

        # they stream away: a band of each maiden's colour sweeps the whole house from the free end of Right
        for k in range(3):
            a = t - (T_LEAVE + 0.4 * k)
            if 0 <= a < 3.5:
                front = L - (L + 200) * a / 2.8
                fr += light(MAIDENS[k], 0.9 * np.exp(-((d - front) / 140) ** 2) * (1 - smoothstep(2.6, 3.5, a)))
        for t0, dur, m, v, _, k in notes['echo']:
            a = t - t0
            if 0 <= a < 1.0 and m >= note('Ab3'):
                fr += light(MAIDENS[int(m) % 3], 0.35 * np.exp(-a / 0.4) * S['land'] * np.exp(-((d - (L - 1200 * a)) / 200) ** 2))

        # the three maidens
        for k, (p, lvl) in enumerate(swimmers):
            if lvl > 0:
                fr = figure(fr, S, p, MAIDENS[k], 0.9 * lvl, w=12)
                fr += light(WHITE, 0.5 * lvl * np.exp(-((d - p) / 4) ** 2))

        # Siegfried, and the gold on his hand
        if t >= T_HORN:
            p = walk(G, t)
            lvl = SIEG_END[2] * smoothstep(T_HORN, T_HORN + 1.2, t)
            laugh = max([np.exp(-(t - e[0]) / 0.3) for e in notes['laugh'] if e[0] <= t] + [0.0])
            fr = figure(fr, S, p, SIEGFRIED, min(1.0, lvl * (1 + 0.3 * laugh)))
            fr += light(HEAD, 0.7 * lvl * np.exp(-((d - p) / 6) ** 2))
            glint = 0.6 + 0.35 * smoothstep(T_GOLD, T_GOLD + 1, t) * (1 - smoothstep(T_CURSE, T_CURSE + 3, t))
            fr += light(GOLD, glint * smoothstep(T_HORN, T_HORN + 1.2, t) * np.exp(-((d - p - 14) / 5) ** 2))
        out[f] = fr
    return np.clip(out, 0, 1)


def score(M, G):
    from pixelhome.audio import SR, whoosh
    pan_at = panner(G)
    for name, gain, rev in (('low', 0.28, 0.25), ('strings', 0.24, 0.32), ('winds', 0.26, 0.35), ('brass', 0.28, 0.3),
                            ('harp', 0.22, 0.4), ('perc', 0.26, 0.3)):
        M.bus(name, gain=gain, reverb=rev)
    hold = hold_factory(M, SR)
    flute = M.sampler('Woodwinds/Flute/susvib/*.wav', tune=-12)
    oboe = M.sampler('Woodwinds/Oboe/Vib/*.wav', tune=-12)
    clar = M.sampler('Woodwinds/Clarinet/susLong/*.wav', tune=-12)
    harp = M.sampler('Strings/Harp/*.wav')
    vln = M.sampler('Strings/Violin Section/susVib/*.wav', tune=-12)
    vla = M.sampler('Strings/Viola Section/trem/*.wav', tune=-12)
    cb = M.sampler('Strings/Solo Contrabass/SusNV/*.wav', tune=-12)
    horn = M.sampler('Brass/F Horn/sus/*.wav', tune=-12)
    tbn = M.sampler('Brass/Tenor Trombone/sus/*.wav', tune=-12)
    tuba = M.sampler('Brass/Tuba/sus/*.wav', tune=-12)
    timp = M.hits('Percussion/Timpani/Timpani1_Hit*.wav')
    cym = M.hits('Percussion/cymbal-crash1_m*.wav')
    voices = [flute, oboe, clar]
    N = compose()
    sw = lambda t, k: pan_at(swim(G, t, N)[k][0])
    bank = pan_at(at(G, *SIEG_END[:2]))
    j = {'song': 0, 'echo': 0, 'joy': 0}
    for t, d, m, v, part, k in N:
        if part in ('flow', 'flow2'):
            for mm in (m, m + 7, m + 12):
                hold('low', cb if mm < note('C3') else vla, mm, t, t + d, v, 0.5, rise=3.0, fall=2.0, gain=0.5)
        elif part in ('song', 'echo', 'joy'):
            who = j[part] % 3
            j[part] += 1
            if m >= note('Ab3'):
                M.add('winds', voices[who].play(m - 12 * (who == 2), v, dur=d * 1.1, release=0.25), t, 0.85, sw(t, who))
            else:
                M.add('harp', harp.play(m + 12, v - 10), t, 0.8, sw(t, who))
        elif part == 'horn':
            M.add('brass', horn.play(m, v, dur=d * 1.05, release=0.3), t, 0.9, pan_at(at(G, 'Left', 0.4)))
        elif part == 'gold':
            if m >= note('C4'):
                M.add('brass', horn.play(m - 12, v, dur=d * 1.05, release=0.3), t, 0.8, bank)
            else:
                M.add('harp', harp.play(m + 12, v), t, 0.8, bank)
            if m >= note('D5'):
                M.add('strings', vln.play(m - 12, v - 16, dur=d * 1.1, release=0.3), t, 0.6, bank)
        elif part == 'ring':
            M.add('winds', clar.play(m, v, dur=d * 1.05, release=0.25), t, 0.85, bank)
        elif part == 'laugh':
            M.add('brass', horn.play(m, v, dur=d * 1.05, release=0.25), t, 0.95, bank)
            if m == note('D4') - 12 or d >= 0.3:
                M.add('perc', timp.play(v - 10, pitch=-3), t, 0.5, bank)
        elif part == 'curse':
            if d > 1.0:
                hold('brass', tbn, m, t, t + d, v, bank, rise=0.15, fall=0.8, gain=0.85)
            else:
                M.add('brass', tbn.play(m, v, dur=d * 1.05, release=0.3), t, 0.9, bank)
            M.add('low', tuba.play(m - 12, v - 14, dur=d * 1.05, release=0.3), t, 0.6, bank)
        elif part == 'fate':
            hold('brass', tuba if m < note('C3') else horn, m if m < note('C3') else m - 12, t, t + d, v, bank,
                 rise=0.4, fall=1.0, gain=0.7)
    M.add('perc', cym.play(96), T_GOLD, 0.5, bank)
    M.add('perc', timp.play(112, pitch=-5), T_CURSE, 0.8, bank)
    for k in range(3):
        M.add('perc', whoosh(1.2, 400, 3000, 0.5, seed=k + 1), T_LEAVE + 0.4 * k, 0.6, pan_at(at(G, 'Right', 0.9)))
