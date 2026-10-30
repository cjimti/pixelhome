"""Valhalla Burns: the pyre roaring on the porch as GD28 left it, its light thrown out over the valley, the
torches drawn in round it, Brünnhilde standing silver before the fire with the Ring on her hand.

"Grane, mein Ross!" The Valkyries' ride (Donington 47) breaks out in the horns and trumpets over galloping
cellos: she mounts and gallops away from the fire along Porch Left and Left, every hoofbeat a silver flash and a
ring of silver, wheels round and charges back, faster, and leaps into the middle of the pyre. A blinding white
flash, and the fire explodes out of the porch: flames race outward along both wings and down the Side until every
run on the house is burning, red at the roots and white-gold at the tips, the torches swallowed in it. Loge's fire
(20) leaps on and on in the violins and harp, every figure a white-gold tongue racing the length of the roofline,
his flickering (20a) scattering sparks.

Then Valhalla (63), in the Wagner tubas at full strength: the castle of the gods blazes gold-white on the porch
inside the fire, and every chord throws a gold-white surge over the whole burning house with deep blue beneath.
Twice. The Twilight of the Gods (5) answers in the trombones, and Valhalla burns and breaks: every stroke a black
crack through the gold and a shower of embers flying out to both ends, the gold sinking as the gods go down in
flames. The house is left burning from end to end with the ruin glowing in the middle.

compose() holds every note; stage(), scene(), water(), figure(), torches(), sparks() and ring() are the valley,
shared word for word by Act III's scenes (GD22 to GD30) on a clock that runs on from scene to scene: T = t + 80 K."""
import numpy as np
from pixelhome.audio import note
from pixelhome.fx import DT, hexc, light, smoothstep, nframes, keys, Flicker, smooth_noise, colormap
from pixelhome.leitmotifs import play

CODE = 'GD29'
TITLE = 'Valhalla Burns'
KIND = 'show'
DESCRIPTION = ('Brünnhilde mounts her horse and rides straight into the fire. The flames take the whole house, '
               'and in the middle of them Valhalla, the castle of the gods, burns and falls.')
VOICEOVER = ('Brünnhilde rides into the flames. The fire climbs to the sky, and Valhalla, home of the gods, '
             'begins to burn.')

K = 7                                       # this scene's place on Act III's shared clock: T = t + 80 K
T_RIDE = [2.5, 6.9, 11.3]                   # the Ride, three times, each faster
RBEAT = [0.42, 0.38, 0.32]
T_TURN = 9.0                                # she wheels round at the end of Left
T_LEAP = 15.0                               # into the fire
T_SPREAD = (15.0, 26.0)                     # the flames race out over every run
LOGES = [16.0 + 1.6 * j for j in range(40)] # Loge's figures, on and on
T_VALHALLA = [31.0, 41.0]                   # Valhalla in the Wagner tubas, twice
T_DOWN = 53.0                               # the Twilight of the Gods: Valhalla breaks
T_DOWN2 = 66.5                              # and again, lower, as it falls
DBEAT = 0.85
D = 80.0

SILVER = hexc('#f4f8ff')
GLINT = hexc('#ffd060')
GOLD = hexc('#ffaa00')
TONGUE = hexc('#fff0b0')
EMBER = hexc('#ffb020')
LOG = hexc('#ff5a10')
SPILL = 0.75                                # firelight over the wings, as GD28 ends

START = dict(river=0.3, forest=0.2, sun=0.0, night=0.35, pyre=0.95, blaze=0.0, valhalla=0.0, flood=0.0)
END = dict(river=0.3, forest=0.2, sun=0.0, night=0.12, pyre=0.95, blaze=0.85, valhalla=0.45, flood=0.0)
BRUN_AT = ('Porch Front', 0.25, 0.9)        # with the Ring; gone into the fire at T_LEAP
TORCHES = (0.4, 0.5)                        # torch level at the start (drawn half way in to the pyre); swallowed

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

    for k, (t0, b) in enumerate(zip(T_RIDE, RBEAT)):
        for t, m, v, d in play('ride', t0, b, 0, 104 + 6 * k):
            add(t, d, m, v, 'ride', k)
    for j in range(int((T_LEAP - 2.0) / 0.33)):            # the gallop under it, quickening
        t = 2.0 + 0.33 * j * (1 - 0.15 * j / 40)
        if t < T_LEAP:
            add(t, 0.2, ('B1', 'Gb2')[j % 2], 84 + j // 2, 'hoof', j)
    add(T_LEAP, 0.1, 'C1', 127, 'leap')
    for j, t0 in enumerate(LOGES):
        if t0 > D - 3:
            break
        for t, m, v, d in play('loge', t0, 0.2, 12 + (0, 3, 7, 12)[j % 4] - 5 * (t0 > T_DOWN), 100):
            add(t, d, m, v, 'loge', j)
        for t, m, v, d in play('loge_flicker', t0 + 0.8, 0.12, 0, 88):
            add(t, d, m, v, 'flicker', j)
    for k, t0 in enumerate(T_VALHALLA):
        for t, m, v, d in play('valhalla', t0, 1.05, 0, 118 + 4 * k):
            add(t, d, m, v, 'valhalla', k)
        add(t0, 0.1, 'C1', 120, 'crash')
    for t, m, v, d in play('downfall_b', T_DOWN, DBEAT, 0, 116):
        add(t, d, m, v, 'down')
    for t, m, v, d in play('downfall_b', T_DOWN2, 1.0, -5, 110):
        add(t, d, m, v, 'down')
    for m in ('Db1', 'Db2', 'Ab2', 'F3'):
        add(T_LEAP, D - T_LEAP, m, 74, 'firebed')
    return sorted(N, key=lambda e: e[0])


def gallop(G, t):
    """Brünnhilde's place and level: out along Porch Left and Left, round, and back into the pyre."""
    p0, p1, pf = at(G, *BRUN_AT[:2]), at(G, 'Left', 0.35), at(G, 'Porch Front', 0.5)
    if t < T_RIDE[0]:
        return p0, BRUN_AT[2]
    if t < T_TURN:
        return p0 + (p1 - p0) * smoothstep(T_RIDE[0], T_TURN, t), BRUN_AT[2]
    u = ((t - T_TURN) / (T_LEAP - T_TURN)) ** 1.6
    return p1 + (pf - p1) * min(u, 1.0), BRUN_AT[2] * (1 - smoothstep(T_LEAP, T_LEAP + 0.3, t))


def reach(t, L):
    """How far the flames have run out from the pyre."""
    return 120 + (L + 200) * smoothstep(*T_SPREAD, t) ** 0.8


def render(G, seed=29):
    F = nframes(D)
    out = np.zeros((F, G.N, 3))
    S = stage(G)
    d, L, pf = S['d'], S['L'], S['pf']
    N = compose()
    hooves = [e[0] for e in N if e[4] == 'hoof']
    lstart = [t0 for t0 in LOGES if t0 <= D - 3]
    valh = [sorted({e[0] for e in N if e[4] == 'valhalla' and e[5] == k}) for k in range(2)]
    downs = sorted({e[0] for e in N if e[4] == 'down' and e[2] < note('C3')})
    runs = ['Left', 'Porch Left', 'Porch Front', 'Porch Right', 'Right', 'Side']
    rng = np.random.default_rng(seed)
    tongue_from = rng.uniform(0, L, len(lstart))
    crack_at = rng.uniform(at(G, 'Porch Left', 0.6), at(G, 'Porch Right', 0.4), len(downs))
    p_torch = at(G, 'Porch Front', 0.5)

    for f in range(F):
        t = f * DT
        T = t + 80 * K
        spread = smoothstep(*T_SPREAD, t)
        lv = dict(START)
        lv['night'] = START['night'] + (END['night'] - START['night']) * spread
        vrise = smoothstep(T_VALHALLA[0] - 0.5, T_VALHALLA[0] + 2.0, t)
        fall = smoothstep(T_DOWN, D - 4, t)
        lv['valhalla'] = 0.9 * vrise * (1 - (1 - END['valhalla'] / 0.9) * fall)
        full = t >= T_SPREAD[1] + 1.0
        lv['blaze'] = END['blaze'] if full else 0.0
        fr = scene(S, T, lv)

        # the fire racing out of the pyre over every run (the same flames scene() draws once it has arrived)
        if not full and t >= T_LEAP:
            r = reach(t, L)
            on = smoothstep(r + 90, r - 90, np.abs(d - pf))
            q = np.clip(heat(d, T) + 0.18 * S['fl'](T), 0, 1)
            flames = END['blaze'] * on * (1 - S['porch'] * (1 - S['pyre']))
            fr += light(FIRE(q), flames * (0.45 + 0.7 * q))
            fr += light(TONGUE, 0.9 * np.exp(-((np.abs(d - pf) - r) / 60) ** 2) * (r < L + 100))
        # the pyre's light over the wings, swallowed as the flames arrive
        fr += light(ORANGE, SPILL * (1 - spread) * (1 - S['porch']) * np.exp(-np.abs(d - pf) / 1500)
                    * (0.7 + 0.3 * S['fl'](T)))

        # the gallop: a silver hoof-flash and ring on every beat, then the leap
        p, lb = gallop(G, t)
        for th in hooves:
            fr = ring(fr, S, t, th, gallop(G, th)[0], SILVER, 0.55, speed=1100, width=70, tau=0.35)
        a = t - T_LEAP
        if 0 <= a < 3:
            fr += light(WHITE, 0.95 * np.exp(-a / 0.18) * np.exp(-((d - pf) / 300) ** 2))
            fr += light(SILVER, 0.6 * np.exp(-a / 0.35))
            fr = ring(fr, S, t, T_LEAP, pf, SILVER, 1.0, speed=1600, width=220, tau=1.0)
            fr = ring(fr, S, t, T_LEAP + 0.15, pf, AMBER, 1.0, speed=1300, width=180, tau=1.2)

        # Loge's tongues racing the length of the roofline, once the fire is out
        for j, t0 in enumerate(lstart):
            aa = t - t0
            if 0 <= aa < 1.8:
                way = 1 if j % 2 == 0 else -1
                q = tongue_from[j] + way * 1700 * smoothstep(0, 1.6, aa)
                g = np.exp(-aa / 0.9) * smoothstep(0, 0.1, aa) * (np.abs(q - pf) < reach(t, L))
                fr += light(AMBER, 0.9 * g * np.exp(-((d - q) / 120) ** 2))
                fr += light(TONGUE, 1.0 * g * np.exp(-((d - q) / 28) ** 2))

        # Valhalla's chords: a gold-white surge over the whole burning house, deep blue beneath, one run blazing
        for k in range(2):
            i = int(np.searchsorted(valh[k], t, side='right')) - 1
            if i >= 0 and t - valh[k][i] < 1.6:
                aa = t - valh[k][i]
                g = np.exp(-aa / 0.7)
                fr += light(VBLUE, 0.45 * g * (1 - S['porch']))
                fr += light(VALHALLA, 0.55 * g)
                fr += light(VALHALLA, 0.6 * g * (G.seg_of == runs[(i + 3 * k) % len(runs)]))
                fr = ring(fr, S, t, valh[k][i], pf, VALHALLA, 0.8, speed=1200, width=200, tau=0.9)

        # Valhalla breaks: a black crack through the gold and embers out to both ends on every low stroke
        hits = []
        for j, (t0, c) in enumerate(zip(downs, crack_at)):
            aa = t - t0
            if 0 <= aa < 2.0:
                crack = np.exp(-((d - c) / 90) ** 2) + np.exp(-((np.abs(d - c) - 1300 * aa) / 260) ** 2) * (aa < 1.5)
                fr *= (1 - 0.92 * np.exp(-aa / 0.7) * np.clip(crack, 0, 1))[:, None]
                fr += light(RED, 0.8 * np.exp(-aa / 0.4) * S['porch'] * (1 - np.exp(-((d - c) / 70) ** 2)))
            hits.append((t0, 1.0, c))
        fr += light(EMBER, np.clip(sparks(S, hits, t, 29, n=40, reach=1.2), 0, 1))
        fr += light(TONGUE, np.clip(sparks(S, hits, t, 30, n=12, reach=0.6) - 0.3, 0, 1))

        # the torches swallowed by the fire
        tl = TORCHES[0] * (1 - smoothstep(T_LEAP, T_LEAP + 6, t))
        if tl > 0.005:
            fr = torches(fr, S, T, tl, pull=p_torch, k=TORCHES[1])

        # Brünnhilde, until she leaps
        if lb > 0.005:
            fr = figure(fr, S, p, SILVER, lb)
            fr += light(GLINT, 0.5 * lb * np.exp(-((d - p - 9) / 5) ** 2))
            fr += light(GOLD, 0.6 * (lb / BRUN_AT[2]) * np.exp(-((d - p + 10) / 5) ** 2))
            if t >= T_RIDE[0]:
                way = np.sign(p - at(G, *BRUN_AT[:2])) if t < T_TURN else 1.0
                trail = np.exp(-np.abs(d - p) / 90) * ((d - p) * way > 0) * (t < T_LEAP)
                fr += light(SILVER, 0.6 * lb * trail)
        out[f] = fr
    return np.clip(out, 0, 1)


def score(M, G):
    from pixelhome.audio import SR, whoosh
    pan_at = panner(G)
    for name, gain, rev in (('low', 0.24, 0.25), ('strings', 0.2, 0.3), ('winds', 0.16, 0.32), ('brass', 0.24, 0.3),
                            ('perc', 0.24, 0.3), ('fx', 0.1, 0.3), ('mallet', 0.1, 0.3)):
        M.bus(name, gain=gain, reverb=rev)
    hold = hold_factory(M, SR)
    vln = M.sampler('Strings/Violin Section/susVib/*.wav', tune=-12)
    vcs = M.sampler('Strings/Cello Section/spic/*.wav', tune=-12)
    vc = M.sampler('Strings/Cello Section/susvib/*.wav', tune=-12)
    cb = M.sampler('Strings/Solo Contrabass/SusNV/*.wav', tune=-12)
    horn = M.sampler('Brass/F Horn/sus/*.wav', tune=-12)
    tpt = M.sampler('Brass/Trumpet/sus/*.wav', tune=-12)
    tbn = M.sampler('Brass/Tenor Trombone/sus/*.wav', tune=-12)
    tuba = M.sampler('Brass/Tuba/sus/*.wav', tune=-12)
    picc = M.sampler('Woodwinds/Piccolo/Sus/*.wav', tune=-12)
    harp = M.sampler('Strings/Harp/*.wav')
    glock = M.sampler('Percussion/Glock/*.wav')
    timp = M.hits('Percussion/Timpani/Timpani1_Hit*.wav')
    roll = M.hits('Percussion/Timpani/Rolls/*.wav')
    crash = M.hits('Percussion/cymbal-crash1_f*.wav')
    gong = M.hits('Percussion/gongHit_f*.wav')
    pf = pan_at(at(G, 'Porch Front', 0.5))
    for t, d, m, v, part, k in compose():
        if part == 'ride':
            pb = pan_at(gallop(G, t)[0])
            if m >= note('B3'):
                M.add('brass', horn.play(m, v, dur=d * 1.1, release=0.2), t, 0.85, pb)
                M.add('brass', tpt.play(m, v - 10, dur=d * 1.1, release=0.2), t, 0.5, pb)
            else:
                M.add('brass', tbn.play(m, v, dur=d * 1.1, release=0.2), t, 0.8, pb)
        elif part == 'hoof':
            pb = pan_at(gallop(G, t)[0])
            M.add('strings', vcs.play(m + 12, v), t, 0.7, pb)
            M.add('perc', timp.play(v - 20, pitch=-6), t, 0.35, pb)
        elif part == 'leap':
            M.add('perc', gong.play(v), t, 0.95, pf)
            M.add('perc', crash.play(v), t, 0.95, pf)
            M.add('perc', timp.play(v, pitch=-7), t, 1.0, pf)
            M.add('perc', roll.play(115, pitch=-3, dur=4.0), t + 0.1, 0.8, pf)
            M.add('fx', whoosh(3.0, 250, 7000, 0.9, seed=41), t - 0.1, 1.0, 0.0)
        elif part == 'loge':
            M.add('strings', vln.play(m, v, dur=d * 1.2, release=0.1), t, 0.6, 0.5 if k % 2 == 0 else -0.5)
            M.add('mallet', harp.play(m, v - 10), t, 0.5, 0.0)
        elif part == 'flicker':
            M.add('winds', picc.play(m, v, dur=d * 1.1, release=0.1), t, 0.45, 0.0)
            M.add('mallet', glock.play(m, v - 20), t, 0.4, 0.0)
        elif part == 'valhalla':
            if m >= note('Db4'):
                hold('brass', horn, m - 12, t, t + d, v, pf, rise=0.06, fall=1.2, gain=0.85)
                hold('brass', tpt, m - 12, t, t + d, v - 16, pf, rise=0.06, fall=1.2, gain=0.4)
            else:
                hold('low', tuba, m, t, t + d, v, pf, rise=0.06, fall=1.2, gain=0.85)
                hold('brass', tbn, m + 12, t, t + d, v - 12, pf, rise=0.06, fall=1.2, gain=0.5)
        elif part == 'crash':
            M.add('perc', crash.play(v), t, 0.8, pf)
            M.add('perc', timp.play(v, pitch=-6), t, 0.9, pf)
        elif part == 'down':
            if m < note('C3'):
                M.add('low', tuba.play(m, v, dur=d * 1.1, release=0.3), t, 0.9, pf)
                M.add('perc', timp.play(v - 10, pitch=-8), t, 0.7, pf)
                M.add('perc', crash.play(90), t, 0.35, pf)
            else:
                M.add('brass', tbn.play(m, v, dur=d * 1.1, release=0.3), t, 0.85, pf)
        elif part == 'firebed':
            hold('low', vc if m >= note('C3') else cb, m, t, t + d, v, pf, rise=2.0, fall=1.5, gain=0.5)
