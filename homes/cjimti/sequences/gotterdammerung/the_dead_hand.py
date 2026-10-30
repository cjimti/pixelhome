"""The Dead Hand: night, the hall on the Rhine, the procession arrived. The body lies in the middle of Porch Front
with the torches close round it and Gunther beside it. Gutrune has been waiting up, a rose light that rises at
Right, flickering with dread, while her motif (Donington 40) turns anxious on the oboe. Hagen bursts in from the
free end of Right, "Hoiho! Wake up!", a violet comet, and his falling tritone (61a) knocks the house dark. She sees
the body and screams: a flash of rose over the whole house, and her light collapses where she stands.

Hagen claims the Ring: the Ring (8) throws gold rings out of the body, and Gunther stands between them. They fight
across the porch, gold against violet, four clashes that light the whole house in turn and spray sparks; then
Hagen's blow, the house drowned in violet and black, and Gunther's gold shatters into sparks flying to both ends
and goes out. Hagen reaches for the Ring, and the dead hand rises: a terrible emerald-white flare out of the body
over every run, the Sword (45) blazing on the trumpets, and Hagen is thrown back along Right and out into the dark
as the Curse (13) blares after him.

Brünnhilde comes: a silver sweep in from the free end of Right the whole length of the house to the end of the
porch, silver laid behind her. Her motif (88) rolls solemn silver waves over the hall; atonement (11) sounds
softly on the Wagner tubas, and the first glow of the pyre comes up on the porch.

compose() holds every note; stage(), scene(), water(), figure(), torches(), sparks() and ring() are the valley,
shared word for word by Act III's scenes (GD22 to GD30) on a clock that runs on from scene to scene: T = t + 80 K."""
import numpy as np
from pixelhome.audio import note
from pixelhome.fx import DT, hexc, light, smoothstep, nframes, keys, Flicker, smooth_noise, colormap
from pixelhome.leitmotifs import play, melody

CODE = 'GD27'
TITLE = 'The Dead Hand'
KIND = 'show'
DESCRIPTION = ("Siegfried's body is brought home. Hagen kills Gunther for the Ring, but when he reaches for it the "
               "dead man's hand rises against him. Then Brünnhilde arrives.")
VOICEOVER = ('They bring the hero home. Hagen kills for the Ring, but the dead hand will not let it go.')

K = 5                                       # this scene's place on Act III's shared clock: T = t + 80 K
T_GUTRUNE = 1.5                             # Gutrune, waiting
T_HOIHO = 8.0                               # Hagen bursts in
T_HAGEN = 11.5                              # his tritone
T_SCREAM = 14.5                             # she sees the body
T_RING = 20.0                               # the Ring, claimed
CLASHES = [29.0, 31.0, 33.0, 34.6]          # Gunther and Hagen fight
T_KILL = 36.5                               # Hagen's blow
T_REACH = (40.0, 44.5)                      # Hagen reaches for the Ring
T_HAND = 45.0                               # the dead hand rises
T_CURSE = 47.5
T_THROWN = (45.0, 53.0)                     # Hagen thrown back and out
T_BRUNN = (55.0, 60.5)                      # Brünnhilde sweeps in
T_MOTIF = 61.5
T_ATONE = 68.0
D = 80.0

SIEGFRIED = hexc('#00ff40')
HEAD = hexc('#e8ffe8')
GOLD = hexc('#ffaa00')
GLINT = hexc('#ffd060')
SILVER = hexc('#f4f8ff')
GUTRUNE = hexc('#ff4090')
HAGEN = hexc('#7a00ff')
GUNTHER = hexc('#ffb020')
STEEL = hexc('#c8d8ff')
BLOOD = hexc('#d00010')

START = dict(river=0.3, forest=0.2, sun=0.0, night=0.45, pyre=0.0, blaze=0.0, valhalla=0.0, flood=0.0)
END = dict(river=0.3, forest=0.2, sun=0.0, night=0.45, pyre=0.1, blaze=0.0, valhalla=0.0, flood=0.0)
BODY_AT = ('Porch Front', 0.5, 0.3)         # the body: level 0.3, no head; the Ring's glint 0.4 at the start, gone by the end
GUNTHER_AT = ('Porch Front', 0.3, 0.55)     # at the start; killed
GUTRUNE_AT = ('Right', 0.3, 0.35)           # her level at the end, collapsed
BRUNN_AT = ('Porch Front', 0.25, 0.85)      # at the end; gold glint 0.5 x level at +9, width 5
HAGEN_AT = ('Porch Front', 0.75, 0.85)      # where he stands until he reaches; gone by the end
TORCHES = (0.5, 0.5)                        # torch level and how far drawn in to the body, start and end

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

    add(0.0, T_HOIHO, 'C2', 58, 'trem')
    for t, m, v, d in play('gutrune', T_GUTRUNE, 0.45, -12, 82):
        add(t, d, m, v, 'gutrune')
    for j, t0 in enumerate((T_HOIHO, T_HOIHO + 1.2)):
        add(t0, 0.9 if j == 0 else 1.6, 'C3', 116, 'hoiho')
    for t, m, v, d in play('hagen', T_HAGEN, 0.6, -12, 122):
        add(t, d, m, v, 'hagen')
    add(T_HAGEN, 0.1, 'C1', 120, 'blow')
    add(T_SCREAM, 1.8, 'Bb5', 116, 'scream')
    for t, m, v, d in play('ring', T_RING, 0.55, -12, 104):
        add(t, d, m, v, 'ring')
    add(T_RING, CLASHES[0] - T_RING, 'Gb2', 70, 'tense')
    for j, t0 in enumerate(CLASHES):
        add(t0, 0.4, ('C3', 'Db3', 'D3', 'Eb3')[j], 110 + 4 * j, 'clash', j)
    for t, m, v, d in play('hagen', T_KILL, 0.5, -12, 126):
        add(t, d, m, v, 'hagen')
    add(T_KILL, 0.1, 'C1', 127, 'kill')
    add(T_REACH[0], T_HAND - T_REACH[0], 'B1', 60, 'reach')
    add(T_HAND, 0.1, 'C1', 127, 'hand')
    for m in ('C3', 'Eb3', 'Gb3', 'A3'):                    # the horror chord
        add(T_HAND, 2.5, m, 120, 'horror')
    for t, m, v, d in play('sword', T_HAND + 0.4, 0.42, 0, 124):
        add(t, d, m, v, 'sword')
    for t, m, v, d in play('curse', T_CURSE, 0.35, 0, 110):
        add(t, d, m, v, 'curse')
    for m in ('Eb2', 'Bb2', 'Eb3', 'G3'):
        add(T_BRUNN[0], D - T_BRUNN[0], m, 60, 'calm')
    for t, m, v, d in play('brunnhilde', T_MOTIF, 0.7, -12, 100):
        add(t, d, m, v, 'brunn')
    for t, m, v, d in play('atonement', T_ATONE, 0.75, 0, 88):
        add(t, d, m, v, 'atone')
    return sorted(N, key=lambda e: e[0])


def where(G, t):
    """(path distance, level) of Gutrune, Hagen, Gunther and Brünnhilde at time t."""
    L = float(G.pd.max())
    pr = at(G, *GUTRUNE_AT[:2])
    lr = keys(t, [(T_GUTRUNE - 1.0, 0.0), (T_GUTRUNE + 1.0, 0.85), (T_SCREAM, 0.85), (T_SCREAM + 0.4, 1.0),
                  (T_SCREAM + 4.0, GUTRUNE_AT[2])])
    h0, h1, hr = L + 40, at(G, *HAGEN_AT[:2]), at(G, 'Porch Front', 0.56)
    if t < T_REACH[0]:
        ph = h0 + (h1 - h0) * smoothstep(T_HOIHO, T_HOIHO + 2.5, t)
        ph += (at(G, 'Porch Front', 0.6) - h1) * smoothstep(CLASHES[0] - 2, CLASHES[0], t) \
            * (1 - smoothstep(T_KILL + 1, T_REACH[0], t))
    elif t < T_THROWN[0]:
        ph = h1 + (hr - h1) * smoothstep(*T_REACH, t)
    else:
        a = t - T_THROWN[0]
        ph = hr + (L + 60 - hr) * (1 - np.exp(-a / 0.5)) * 0.55 + (L + 60 - hr) * 0.45 * smoothstep(1.0, 7.5, a)
    lh = HAGEN_AT[2] * smoothstep(T_HOIHO, T_HOIHO + 0.4, t) * (1 - smoothstep(T_THROWN[1] - 2, T_THROWN[1], t))
    pg = at(G, *GUNTHER_AT[:2]) + (at(G, 'Porch Front', 0.42) - at(G, *GUNTHER_AT[:2])) \
        * smoothstep(T_RING + 2, CLASHES[0] - 1, t)
    lg = keys(t, [(0, GUNTHER_AT[2]), (T_RING, GUNTHER_AT[2]), (CLASHES[0], 0.85), (T_KILL, 0.95),
                  (T_KILL + 2.5, 0.0)])
    b0, b1 = L + 40, at(G, *BRUNN_AT[:2])
    pb = b0 + (b1 - b0) * smoothstep(*T_BRUNN, t)
    lb = BRUNN_AT[2] * smoothstep(T_BRUNN[0], T_BRUNN[0] + 0.5, t)
    return (pr, lr), (ph, lh), (pg, lg), (pb, lb)


def render(G, seed=27):
    F = nframes(D)
    out = np.zeros((F, G.N, 3))
    S = stage(G)
    d, L = S['d'], S['L']
    N = compose()
    p_body = at(G, *BODY_AT[:2])
    gut = sorted({e[0] for e in N if e[4] == 'gutrune'})
    ring_on = sorted({e[0] for e in N if e[4] == 'ring'})
    curse = [e for e in N if e[4] == 'curse' and e[2] >= note('C3')]
    sword = sorted({e[0] for e in N if e[4] == 'sword'})
    brunn = [(T_MOTIF + b * 0.7, m) for b, _, m in melody('brunnhilde')]
    atone = sorted({e[0] for e in N if e[4] == 'atone'})
    runs = ['Left', 'Right', 'Side', 'Porch Front', 'Porch Left', 'Porch Right']

    for f in range(F):
        t = f * DT
        T = t + 80 * K
        lv = dict(START)
        lv['pyre'] = END['pyre'] * smoothstep(T_ATONE, D - 2, t)
        dark = smoothstep(T_KILL, T_KILL + 0.3, t) * (1 - smoothstep(T_KILL + 2, T_HAND, t))
        fr = scene(S, T, {k: v * (1 - 0.6 * dark) for k, v in lv.items()})
        (pr, lr), (ph, lh), (pg, lg), (pb, lb) = where(G, t)

        # Gutrune waiting: rose ripples on her anxious motif
        for t0 in gut:
            fr = ring(fr, S, t, t0, pr, GUTRUNE, 0.85, speed=900, width=140, tau=0.8)
        dread = smoothstep(T_GUTRUNE, T_GUTRUNE + 1.5, t) * (1 - smoothstep(T_HOIHO - 0.5, T_HOIHO + 0.5, t))
        fr += light(GUTRUNE, 0.55 * dread * (G.seg_of == 'Right') * (0.5 + 0.5 * np.sin(2 * np.pi * t / 1.3)) ** 2)
        for t0 in (T_HOIHO, T_HOIHO + 1.2):         # Hoiho!: a violet blast out of the dark at each call
            fr = ring(fr, S, t, t0, L, HAGEN, 1.0, speed=1500, width=220, tau=1.0)
            fr = ring(fr, S, t, t0 + 0.1, L, TORCH, 0.8, speed=1300, width=80, tau=0.8)

        # Hoiho!: Hagen bursts in as a violet comet; his tritone knocks the house dark
        if T_HOIHO <= t < T_HOIHO + 3:
            trail = (d > ph) * np.exp(-(d - ph) / 160) * np.exp(-(t - T_HOIHO) / 1.5)
            fr += light(HAGEN, 0.9 * trail)
        for t0 in (T_HAGEN, T_KILL):
            a = t - t0
            if 0 <= a < 2.0:
                fr = fr * (1 - 0.85 * (1 - np.exp(-a / 0.05)) * np.exp(-a / 0.7))
                fr += light(HAGEN, 0.9 * np.exp(-a / 0.15))
                fr = ring(fr, S, t, t0, ph, HAGEN, 1.0, speed=1300, width=180, tau=0.9)

        # her scream: a flash of rose over the whole house
        a = t - T_SCREAM
        if 0 <= a < 2.0:
            fr += light(GUTRUNE, 0.9 * np.exp(-a / 0.35))
            fr = ring(fr, S, t, T_SCREAM, pr, GUTRUNE, 1.0, speed=1600, width=200, tau=0.8)

        # the Ring claimed: gold rings out of the body on every note
        for t0 in ring_on:
            fr = ring(fr, S, t, t0, p_body, GOLD, 0.9, speed=900, width=110, tau=0.9)

        # the fight: four clashes, the whole house lit in turn, sparks out of the point where they meet
        hits = []
        for j, t0 in enumerate(CLASHES):
            a = t - t0
            mid = 0.5 * (pg + ph)
            hits.append((t0, 1.0, mid))
            if 0 <= a < 0.8:
                col = GUNTHER if j % 2 == 0 else HAGEN
                fr += light(col, 0.85 * np.exp(-a / 0.25) * (G.seg_of == runs[j % len(runs)]))
                fr += light(WHITE, 0.9 * np.exp(-a / 0.08) * np.exp(-((d - mid) / 20) ** 2))
        if T_KILL <= t < T_KILL + 2:
            hits.append((T_KILL + 0.05, 1.4, pg))
        fr += light(GLINT, np.clip(sparks(S, hits, t, 27, n=18), 0, 1.0))
        fr += light(HAGEN, 0.75 * dark * (0.6 + 0.4 * np.sin(2 * np.pi * (d / 280 - 0.8 * t))))

        # the dead hand rises: an emerald-white flare over every run, the Sword blazing, Hagen thrown out
        a = t - T_HAND
        if 0 <= a < 6.0:
            fr += light(WHITE, 0.95 * np.exp(-a / 0.15))
            hold_ = keys(a, [(0, 1.0), (1.6, 0.95), (5.5, 0.0)])
            fr += light(SIEGFRIED, hold_ * (0.65 + 0.35 * np.sin(2 * np.pi * (d / 200 - 2 * a))))
            fr += light(HEAD, 0.6 * hold_ * np.clip(np.sin(2 * np.pi * (d / 90 + 3 * a)), 0, 1) ** 4)
            fr = ring(fr, S, t, T_HAND, p_body, SIEGFRIED, 1.0, speed=1400, width=260, tau=1.4)
            fr = ring(fr, S, t, T_HAND + 0.2, p_body, HEAD, 0.9, speed=1200, width=80, tau=1.0)
        for j, t0 in enumerate(sword):
            aa = t - t0
            if 0 <= aa < 0.8:
                x = p_body + (1 if j % 2 == 0 else -1) * 1500 * aa
                fr += light(STEEL, np.exp(-aa / 0.4) * np.exp(-((d - x) / 80) ** 2))
        for t0, dur, m, v, _, k in curse:
            fr = ring(fr, S, t, t0, p_body, BLOOD, 0.85, speed=1100, width=120, tau=0.8)

        # Brünnhilde sweeps in from the free end of Right, silver laid behind her; then her solemn waves
        if T_BRUNN[0] <= t:
            behind = (d > pb) * np.exp(-(d - pb) / 700) * (1 - smoothstep(T_BRUNN[1], T_BRUNN[1] + 4, t))
            fr += light(SILVER, 0.8 * behind * smoothstep(T_BRUNN[0], T_BRUNN[0] + 0.4, t))
        for t0, m in brunn:
            fr = ring(fr, S, t, t0, pb, SILVER, 1.0, speed=1000, width=240, tau=1.2)
            fr = ring(fr, S, t, t0 + 0.1, pb, GLINT, 0.7, speed=900, width=70, tau=0.9)
        cmd = smoothstep(T_BRUNN[1], T_MOTIF, t) * (1 - smoothstep(T_ATONE + 4, D - 2, t))
        fr += light(SILVER, 0.45 * cmd * S['porch'] * (0.6 + 0.4 * np.sin(2 * np.pi * (d / 240 - 0.4 * t))))
        for t0 in atone:
            fr = ring(fr, S, t, t0, p_body, GLINT, 0.5, speed=600, width=200, tau=1.2)

        # the torches, and the people
        fr = torches(fr, S, T, TORCHES[0] * (1 - 0.4 * dark), pull=p_body, k=TORCHES[1])
        if lr > 0:
            fr = figure(fr, S, pr, GUTRUNE, lr * (0.85 + 0.15 * np.sin(2 * np.pi * t / 0.45)) if t < T_SCREAM
                        else lr)
        if lg > 0:
            fr = figure(fr, S, pg, GUNTHER, lg)
        if lh > 0:
            fr = figure(fr, S, ph, HAGEN, lh)
            fr += light(STEEL, 0.6 * lh * np.exp(-((d - ph + 16) / 5) ** 2))
        flare = np.exp(-max(t - T_HAND, 0) / 1.5) * (t >= T_HAND)
        fr = figure(fr, S, p_body, SIEGFRIED, BODY_AT[2] + 0.6 * flare, w=12)
        fr += light(GOLD, 0.4 * (1 - smoothstep(T_BRUNN[1], D - 4, t)) * np.exp(-((d - p_body - 14) / 5) ** 2))
        if lb > 0:
            fr = figure(fr, S, pb, SILVER, lb)
            fr += light(GLINT, 0.5 * lb * np.exp(-((d - pb - 9) / 5) ** 2))
        out[f] = fr
    return np.clip(out, 0, 1)


def score(M, G):
    from pixelhome.audio import SR, whoosh
    pan_at = panner(G)
    for name, gain, rev in (('low', 0.36, 0.25), ('strings', 0.31, 0.32), ('winds', 0.31, 0.35), ('brass', 0.35, 0.3),
                            ('perc', 0.34, 0.3), ('fx', 0.15, 0.3)):
        M.bus(name, gain=gain, reverb=rev)
    hold = hold_factory(M, SR)
    oboe = M.sampler('Woodwinds/Oboe/Vib/*.wav', tune=-12)
    clar = M.sampler('Woodwinds/Clarinet/susLong/*.wav', tune=-12)
    bsn = M.sampler('Woodwinds/Bassoon/sus/*.wav', tune=-12)
    horn = M.sampler('Brass/F Horn/sus/*.wav', tune=-12)
    tbn = M.sampler('Brass/Tenor Trombone/sus/*.wav', tune=-12)
    tuba = M.sampler('Brass/Tuba/sus/*.wav', tune=-12)
    tpt = M.sampler('Brass/Trumpet/sus/*.wav', tune=-12)
    vtrem = M.sampler('Strings/Violin Section/Trem/*.wav', tune=-12)
    vln = M.sampler('Strings/Violin Section/susVib/*.wav', tune=-12)
    ctrem = M.sampler('Strings/Cello Section/trem/*.wav', tune=-12)
    vc = M.sampler('Strings/Cello Section/susvib/*.wav', tune=-12)
    cb = M.sampler('Strings/Solo Contrabass/SusNV/*.wav', tune=-12)
    timp = M.hits('Percussion/Timpani/Timpani1_Hit*.wav')
    crash = M.hits('Percussion/cymbal-crash1_f*.wav')
    gong = M.hits('Percussion/gongHit_f*.wav')
    body = pan_at(at(G, *BODY_AT[:2]))
    gut = pan_at(at(G, *GUTRUNE_AT[:2]))
    door = pan_at(at(G, 'Right', 0.95))
    for t, d, m, v, part, k in compose():
        if part == 'trem':
            hold('low', ctrem, m, t, t + d, v, body, rise=0.8, fall=1.5, gain=0.5)
        elif part == 'gutrune':
            if d > 1.0:
                hold('winds', oboe, m - 12, t, t + d, v, gut, rise=0.2, fall=0.8, gain=0.75)
            else:
                M.add('winds', oboe.play(m - 12, v, dur=d * 1.05, release=0.25), t, 0.85, gut)
        elif part == 'hoiho':
            hold('brass', horn, m, t, t + d, v, door, rise=0.05, fall=0.5, gain=0.8)
            M.add('low', tuba.play(m - 12, v - 10, dur=d, release=0.3), t, 0.6, door)
        elif part == 'hagen':
            hold('low', tuba, m, t, t + d, v, body, rise=0.05, fall=1.0, gain=0.95)
            M.add('brass', tbn.play(m + 12, v - 6, dur=d, release=0.4), t, 0.8, body)
        elif part == 'blow':
            M.add('perc', timp.play(v, pitch=-7), t, 1.0, body)
            M.add('perc', crash.play(100), t, 0.6, body)
        elif part == 'scream':
            hold('strings', vtrem, m - 12, t, t + d, v, gut, rise=0.05, fall=0.6, gain=0.6)
            M.add('perc', crash.play(110), t, 0.7, gut)
            M.add('fx', whoosh(1.0, 6000, 900, 0.7, seed=5), t, 0.8, gut)
        elif part == 'ring':
            s = clar if m >= note('C4') else bsn
            if d > 1.0:
                hold('winds', s, m, t, t + d, v, body, rise=0.2, fall=0.8, gain=0.75)
            else:
                M.add('winds', s.play(m, v, dur=d * 1.05, release=0.25), t, 0.85, body)
        elif part == 'tense':
            hold('low', ctrem, m, t, t + d, v, body, rise=1.0, fall=0.5, gain=0.5)
        elif part == 'clash':
            M.add('perc', crash.play(v - 10), t, 0.6, body)
            M.add('perc', timp.play(v, pitch=-3 - k), t, 0.8, body)
            M.add('brass', tbn.play(m, v, dur=0.35, release=0.2), t, 0.8, body)
        elif part == 'kill':
            M.add('perc', gong.play(v), t, 0.9, body)
            M.add('perc', timp.play(v, pitch=-8), t, 1.0, body)
            M.add('fx', whoosh(0.5, 4000, 300, 0.9, seed=9), t - 0.15, 1.0, body)
        elif part == 'reach':
            hold('low', cb, m, t, t + d, v, body, rise=3.0, fall=0.2, gain=0.6)
            hold('strings', vtrem, m + 36, t, t + d, v - 10, body, rise=3.0, fall=0.2, gain=0.35)
        elif part == 'hand':
            M.add('perc', gong.play(v), t, 1.0, body)
            M.add('perc', crash.play(v), t, 0.9, body)
            M.add('perc', timp.play(v, pitch=-5), t, 1.0, body)
        elif part == 'horror':
            hold('brass', tbn if m < note('Eb3') else horn, m, t, t + d, v, body, rise=0.03, fall=1.0, gain=0.7)
            hold('strings', vtrem, m + 12, t, t + d, v - 10, body, rise=0.03, fall=1.0, gain=0.4)
        elif part == 'sword':
            if d > 1.0:
                hold('brass', tpt, m - 12, t, t + d, v, body, rise=0.03, fall=0.8, gain=0.85)
            else:
                M.add('brass', tpt.play(m - 12, v, dur=d * 1.05, release=0.25), t, 0.9, body)
        elif part == 'curse':
            if d > 1.0:
                hold('brass', tbn, m, t, t + d, v, door, rise=0.1, fall=0.8, gain=0.8)
            else:
                M.add('brass', tbn.play(m, v, dur=d * 1.05, release=0.3), t, 0.85, door)
            M.add('low', tuba.play(m - 12, v - 12, dur=d * 1.05, release=0.3), t, 0.6, door)
        elif part == 'calm':
            hold('strings', vc if m >= note('Bb2') else cb, m, t, t + d, v, 0.0, rise=4.0, fall=1.5, gain=0.5)
        elif part == 'brunn':
            if d > 1.0:
                hold('brass', horn, m, t, t + d, v, -0.2, rise=0.2, fall=1.0, gain=0.75)
            else:
                M.add('brass', horn.play(m, v, dur=d * 1.05, release=0.3), t, 0.8, -0.2)
            M.add('strings', vln.play(m + 12, v - 18, dur=d * 1.05, release=0.3), t, 0.5, -0.2)
        elif part == 'atone':
            if m >= note('E3'):
                hold('brass', horn, m - 12, t, t + d, v, body, rise=0.4, fall=1.0, gain=0.6)
            else:
                hold('low', tuba, m, t, t + d, v, body, rise=0.4, fall=1.0, gain=0.6)
    M.add('fx', whoosh(5.5, 400, 3000, 0.6, seed=11), T_BRUNN[0], 0.6, 0.2)
