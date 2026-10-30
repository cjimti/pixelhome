"""The Rhinemaidens: a wooded valley on the Rhine, bright afternoon. The river runs along Right and down the Side in
racing currents of indigo, teal and green with foam glinting on them; the forest is over Left and the porch, gold
shafts of sun sliding through it. Woglinde in silver, Wellgunde in sea green and Flosshilde in violet surface out
of the water on Right. Their joy comes first: the music swirls and they chase each other end to end of Right with
the whole river flashing; then they sing, every note a dart along the river and a ripple of their colour running
the length of both river runs. Siegfried's horn sounds from the forest, an emerald flash on Left, and he strides out
along the porch to the bank. Gold surges up both river runs as they circle in on him: give us the Ring. He laughs at
them, his strength blasting emerald from end to end, whole runs at a time, and the Ring on his hand throws gold
rings out over the house as he swears they will never have it. Then they warn him: the Curse turns the whole river
blood violet, wave on wave, the power of fate rolls indigo out from him, and they stream away out of the free end
of Right, leaving him alone on the bank with the gold on his hand.

The music is Wagner's own, Act III's first scene as Solti's 1958 Vienna Philharmonic recording takes it, from the
Wagner Ring Dataset's piano reduction (pixelhome/ring.py), in four cuts: the maidens' swirling joy and the start of
their song "Frau Sonne sendet lichte Strahlen" (bars 66 to 76), their alarm before "Ich höre sein Horn" (144 to
151), Siegfried's "Nun lacht nur lustig zu! ... euch Nickern geb' ich ihn nie!" (232 to 242), and their warning
"... so fällst auch du, und heute noch" (314 to 321). Strings, harp and flutes carry the river's figuration, horns
and trombones his music, trombones and tuba the Curse. Their song's melody is not in the reduction, so Woglinde's
line is taken from the Schott vocal score (archive.org gtterdmmerung1900wagn, p. 234 to 235) and played as written
on flute and oboe. Siegfried's horn call, played offstage in the opera and missing from the reduction, sounds from
the forest on a horn. A river's rush runs under the maidens and backs off while they sing; cymbals for the gold,
a gong and timpani for the Curse and for fate, and three splashes as they dive.

compose() holds every note; stage(), scene(), water(), figure(), torches(), sparks() and ring() are the valley,
shared word for word by Act III's scenes (GD22 to GD30) on a clock that runs on from scene to scene: T = t + 80 K."""
import numpy as np
from pixelhome.audio import note
from pixelhome.fx import DT, hexc, light, smoothstep, nframes, Flicker, smooth_noise, colormap
from pixelhome.leitmotifs import play
from pixelhome.ring import Orchestra, accents, excerpt, tidy

CODE = 'GD22'
TITLE = 'The Rhinemaidens'
KIND = 'show'
DESCRIPTION = ('Three river spirits play in the Rhine and beg Siegfried for the golden Ring. He laughs at them, '
               'and they warn him he will die before the day is out.')
VOICEOVER = ('Siegfried has lost his way on the hunt, and comes to the river. '
             'Three voices in the water ask him for the Ring.')

K = 0                                       # this scene's place on Act III's shared clock: T = t + 80 K
EX = excerpt(__file__)                      # Act III, bars 66-77, 144-152, 232-243 and 314-322, Solti 1958
D = EX['seconds']
SEG = [s_['start'] for s_ in EX['segments']] + [D]


def when(m):
    """Bar position m (as in the dataset) -> seconds into the excerpt."""
    for s_ in EX['segments']:
        a, b = s_['measures']
        if a <= m <= b:
            bars = [(x, y) for x, y in EX['bars'] if a <= x <= b]
            return float(np.interp(m, [x for x, _ in bars], [y for _, y in bars]))
    raise ValueError(m)


T_JOY = 0.0                                 # their joy: the chase
JOY_END = when(72.5)
T_SONG = when(72.667)                       # "Frau Sonne sendet lichte Strahlen"
T_HORN = when(149)                          # his horn in the forest
T_WALK = (T_HORN + 1.0, SEG[2] + 0.8)       # he strides out along the porch to the bank
T_GOLD = SEG[2]                             # give us the Ring: gold up the river
T_RING = when(239.83)                       # "euch Nickern geb' ich ihn nie!": the Ring on his hand
T_CURSE = SEG[3]                            # they warn him
T_FATE = [when(319), when(321)]
T_LEAVE = D - 4.9                           # they stream away
# Woglinde's line, from the vocal score: (bar, start, length in eighths of a 9/8 bar, note)
SONG = [(72, 6, 3, 'C5'), (73, 0, 5, 'D5'), (73, 5, 1, 'F5'), (73, 6, 3, 'C5'), (74, 0, 5, 'Bb4'), (74, 5, 1, 'A4'),
        (74, 6, 1, 'D5'), (74, 7, 1, 'E5'), (74, 8, 1, 'F5'), (75, 0, 9, 'G5'), (76, 0, 2, 'C5')]

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


def thin(ts, gap):
    out = []
    for t in sorted(ts):
        if not out or t - out[-1] >= gap:
            out.append(t)
    return out


def song():
    """Woglinde's line in seconds: (time, seconds, midi)."""
    return [(when(b + x / 9), when(b + (x + n) / 9) - when(b + x / 9), note(m)) for b, x, n, m in SONG]


def horn_call():
    """Siegfried's horn call, offstage in the forest, in F."""
    return [(t, d, m, v) for t, m, v, d in play('siegfried_horn', T_HORN, 0.36, -2, 100)]


def compose():
    """Every event for the lights: (time, seconds, midi, velocity, part, k). The river's figuration in the joy and the
    alarm ('joy', thinned to one in a quarter second), the song ('song', k = which maiden), the horn call ('horn'),
    his laughter (the orchestra's big chords, 'laugh'), the Ring ('ring'), the Curse ('curse') and fate ('fate')."""
    N = []
    notes = EX['notes']
    rh = [n for n in notes if n[4] == 0 and n[2] >= note('Ab3')]
    for t in thin([n[0] for n in rh if t_in(n[0], 0, T_SONG - 0.4) or t_in(n[0], SEG[1], T_HORN - 0.3)], 0.24):
        N.append((t, 0.3, 72, 90, 'joy', None))
    for i, (t, d, m) in enumerate(song()):
        N.append((t, d, m, 96, 'song', i % 3))
    for t in thin([n[0] for n in rh if t_in(n[0], when(76.3), SEG[1])], 0.5):
        N.append((t, 0.3, 72, 70, 'song', None))
    for t, d, m, v in horn_call():
        N.append((t, d, m, v, 'horn', None))
    for t in accents(notes, SEG[2], T_RING - 0.2, vmin=104, n=2, space=0.8):
        N.append((t, 0.3, 50, 110, 'laugh', None))
    for t in thin([n[0] for n in rh if t_in(n[0], T_RING - 0.2, SEG[3])], 0.5):
        N.append((t, 0.3, 64, 100, 'ring', None))
    for t in thin([n[0] for n in notes if t_in(n[0], SEG[3], T_LEAVE) and n[3] >= 80], 0.55):
        N.append((t, 0.3, 50, 100, 'curse', None))
    for t in T_FATE:
        N.append((t, 1.0, 60, 110, 'fate', None))
    return sorted(N, key=lambda e: e[0])


def t_in(t, a, b):
    return a <= t < b


def swim(G, t, N):
    """Where each maiden is at time t (path distances), and how bright."""
    r0, r1 = at(G, 'Right', 0.08), at(G, 'Right', 1.0)
    span = r1 - r0
    song = sorted({e[0] for e in N if e[4] in ('song', 'joy', 'curse')})
    out = []
    for k in range(3):
        base = 0.35 + 0.25 * k + 0.12 * np.sin(2 * np.pi * t / (5.3 + 1.1 * k) + 2.0 * k)
        darts = sum(0.06 * np.sin(1.7 * j + 2.1 * k) * smoothstep(s, s + 0.25, t) for j, s in enumerate(song) if s <= t)
        u = base + darts
        chase = smoothstep(T_JOY, T_JOY + 0.8, t) * (1 - smoothstep(JOY_END - 1, JOY_END, t))
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
        warn = smoothstep(T_CURSE, T_CURSE + 1.0, t) * (1 - smoothstep(T_LEAVE, T_LEAVE + 4, t))
        lv['river'] = START['river'] * (1 - 0.5 * warn)
        lv['sun'] = START['sun'] * (1 - 0.6 * warn)
        fr = scene(S, T, lv)
        swimmers = swim(G, t, N)

        # every note of their song: a ripple of the singer's colour running both ways along both river runs
        for part in ('song', 'echo', 'joy'):
            for i, (t0, dur, m, v, _, k) in enumerate(notes[part]):
                a = t - t0
                if 0 <= a < 1.4 and m >= note('Ab3'):
                    who = k if k is not None else i % 3
                    p, lvl = swimmers[who]
                    g = (0.9 if part != 'echo' else 0.5) * np.exp(-a / 0.5)
                    dist = np.abs(d - p)
                    fr += light(MAIDENS[who], g * river * np.exp(-((dist - 900 * a) / 70) ** 2))
                    side = np.abs((d - S['L'] * 0.0) - (490 - 600 * a))
                    fr += light(MAIDENS[who], 0.7 * g * (G.seg_of == 'Side') * np.exp(-(side / 70) ** 2))
                    shore = S['land'] * np.exp(-((d - (at(G, 'Right', 0.0) - 1400 * a)) / 160) ** 2)
                    fr += light(MAIDENS[who], 0.55 * g * shore)

        # the chase: the whole river flashes in their colours, one run then the other
        if T_JOY <= t < JOY_END:
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
    """Wagner's notes from the piano reduction, Woglinde's line from the vocal score, the horn call offstage, and the
    river, the gold, the Curse and the dive as a production would stage them."""
    from pixelhome.audio import whoosh
    pan_at = panner(G)
    o = Orchestra(M, level=2.5)
    N = compose()
    sw = lambda t, k: pan_at(swim(G, t, N)[k][0])
    bank = pan_at(at(G, *SIEG_END[:2]))
    river = pan_at(at(G, 'Right', 0.5))

    def size(t):
        return 0.6 if t < SEG[2] else 1.0 if t < SEG[3] else 0.85

    def role(t, d, m, v, h):
        if t < SEG[2] and h == 0 and d < 0.25:              # the river's figuration: violins, a harp glinting
            return [('violins' if m >= 55 else 'violas', 0, -6, 0.45), ('harp', 0, -14, 0.3)]
        if t < SEG[2] and h == 1 and d >= 0.3:              # its long chords: clarinets and horns, soft
            return [('clarinets', 0, -8, 0.45), ('horns', 0, -14, 0.35)]
        if SEG[3] <= t and h == 1 and d >= 0.3 and m >= 48:  # the Curse: trombones and tuba
            return [('trombones', 0, 0, 0.75), ('tuba', -12, -8, 0.45)]
        return None

    o.tutti(tidy(EX['notes']), size=size, role=role, pan=lambda t, m: river if t < SEG[2] else bank * 0.6)
    for t, d, m in song():                                  # Woglinde's line: flute and oboe
        o.play('flutes', m, t, d, 100, sw(t, 0), 0.75)
        o.play('oboes', m, t, d, 92, sw(t, 1), 0.4)
    for t, d, m, v in horn_call():                          # his horn, off in the forest
        o.play('horns', m, t, d, v, pan_at(at(G, 'Left', 0.4)), 0.7)

    # the river, ridden down under their song and his music
    o.wind(0.0, SEG[2] + 2.0, level=0.45, pan=river, seed=22)
    o.effects([(0.0, -3), (T_SONG - 1.0, -3), (T_SONG, -15), (when(76.3), -15), (when(76.3) + 1.5, -5),
               (T_HORN, -4), (SEG[2], -8), (SEG[3], -6), (T_LEAVE - 0.5, -6), (T_LEAVE, 0)])
    o.hit('cymbal swell', T_GOLD - 2.6, 96, gain=0.4, pan=bank)
    o.hit('crash', T_GOLD, 104, gain=0.45, pan=bank)
    laughs = [e[0] for e in N if e[4] == 'laugh']
    for t in laughs[:3]:
        o.hit('timpani', t, 112, pitch=-3, gain=0.45, pan=bank)
    o.hit('triangle', T_RING, 100, gain=0.4, pan=bank)
    o.hit('gong', T_CURSE, 104, gain=0.45, pan=bank)
    o.hit('timpani', T_CURSE, 116, pitch=-5, gain=0.6, pan=bank)
    for t in T_FATE:
        o.hit('timpani roll', t, 104, pitch=-5, gain=0.45, pan=bank)
        o.hit('gong', t, 100, gain=0.35, pan=bank)
    for k in range(3):                                      # they dive: three splashes
        M.add('fx', whoosh(1.2, 400, 3000, 0.5, seed=k + 1), T_LEAVE + 0.4 * k, 0.9, pan_at(at(G, 'Right', 0.9)))
