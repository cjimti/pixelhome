"""Siegfried's Funeral March: night in the valley, the body lying in the middle of Porch Front with the torches close
round it. The vassals lift him and the procession begins: a column of torches streams in from the free end of
Right and marches the whole length of the house, step by step, out past the end of the Side, and keeps coming.

The march is his whole family's story, and each part of it takes the whole house. The death rhythm hammers on the
timpani with the full orchestra in C minor, three strokes at a time: each a flash, then the house knocked almost
black for a moment. The Volsungs' tragic destiny (Donington 66) rises on the Wagner tubas in waves of indigo out of
the body. Siegmund (35) floods Left and the Side in Wälsung blue, Sieglinde (36) answers over Right and the river in
amber, and the twins' love (37) sends blue in from one end and amber from the other to meet in a white flash over
the body. The death rhythm again; then the Sword (45) on the trumpet, every note a white steel sweep the length of
the house; Siegfried's own motif (53) at full strength, each note slamming a whole run emerald; his horn call
turned into a vast slow statement for the whole brass, gold and emerald sweeping out to both ends over a crash of
cymbals; and at the top Brünnhilde's motif (88), silver flooding every run. Then the death rhythm one last time,
the colour sinks away, and the procession carries him on toward the hall in the dark.

compose() holds every note; stage(), scene(), water(), figure(), torches(), sparks() and ring() are the valley,
shared word for word by Act III's scenes (GD22 to GD30) on a clock that runs on from scene to scene: T = t + 80 K."""
import numpy as np
from pixelhome.audio import note
from pixelhome.fx import DT, hexc, light, smoothstep, nframes, keys, Flicker, smooth_noise, colormap
from pixelhome.leitmotifs import play, melody

CODE = 'GD26'
TITLE = "Siegfried's Funeral March"
KIND = 'show'
DESCRIPTION = ("The vassals carry Siegfried's body through the night by torchlight, and his family's music fills "
               'the house one part at a time: the Volsungs, his parents, the sword, the hero, his horn, his bride.')
VOICEOVER = ('The vassals lift the hero onto their shields, and carry him home through the night.')

K = 4                                       # this scene's place on Act III's shared clock: T = t + 80 K
HAMMERS = [3.0, 13.5, 44.0, 71.0]           # the death rhythm: three strokes each, the third the longest
VOLSUNG = [(5.0, 0), (15.5, 7)]             # the Volsungs' tragic destiny, the second time higher
T_SIEGMUND = 25.0
T_SIEGLINDE = 33.5
T_TWINS = 37.0
T_SWORD = 46.0
T_SIEG = 51.0
T_HORN = 55.5
T_BRUNN = 62.0
T_MARCH = (4.0, 70.0)                       # torches keep joining the column
D = 80.0

SIEGFRIED = hexc('#00ff40')
GOLD = hexc('#ffaa00')
GLINT = hexc('#ffd060')
SILVER = hexc('#f4f8ff')
SIEGMUND = hexc('#30a8ff')
SIEGLINDE = hexc('#ffa860')
STEEL = hexc('#e8f8ff')
GUNTHER = hexc('#ffb020')
FATE_C = hexc('#3a1aff')
HIT = hexc('#c040ff')

START = dict(river=0.4, forest=0.25, sun=0.0, night=0.45, pyre=0.0, blaze=0.0, valhalla=0.0, flood=0.0)
END = dict(river=0.3, forest=0.2, sun=0.0, night=0.45, pyre=0.0, blaze=0.0, valhalla=0.0, flood=0.0)
BODY_AT = (('Porch Front', 0.65), ('Porch Front', 0.5), 0.3)    # where the body lies at the start, the end; its level
GUNTHER_AT = ('Porch Front', 0.3, 0.55)
TORCHES = ((0.6, 0.6), (0.5, 0.5))          # (level, how far drawn in to the body) at the start and the end

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


def strokes():
    """Every stroke of the death rhythm: (time, weight)."""
    return [(t0 + o, w) for t0 in HAMMERS for o, w in ((0.0, 0.75), (0.4, 0.8), (0.8, 1.0))]


def compose():
    """Every note: (time, seconds, midi, velocity, part, k)."""
    N = []

    def add(t, d, m, v, part, k=None):
        N.append((float(t), float(d), note(m) if isinstance(m, str) else int(m), int(v), part, k))

    add(0.0, D, 'C2', 60, 'trem')
    for t, w in strokes():
        add(t, 0.6 if w < 1 else 1.6, 'C2', int(96 + 28 * w), 'stroke')
        for m in ('C2', 'G2', 'C3', 'Eb3', 'G3'):
            add(t, 0.35 if w < 1 else 1.4, m, int(80 + 30 * w), 'chord')
    for k, (t0, tr) in enumerate(VOLSUNG):
        for t, m, v, d in play('volsung_fate', t0, 0.55, tr - 12, 100 + 8 * k):
            add(t, d, m, v, 'volsung', k)
    for t, m, v, d in play('siegmund', T_SIEGMUND, 0.45, 0, 104):
        add(t, d, m, v, 'siegmund')
    for t, m, v, d in play('sieglinde', T_SIEGLINDE, 0.45, -12, 98):
        add(t, d, m, v, 'sieglinde')
    for t, m, v, d in play('twins_love', T_TWINS, 0.45, -12, 100):
        add(t, d, m, v, 'twins')
    for t, m, v, d in play('sword', T_SWORD, 0.6, 0, 118):
        add(t, d, m, v, 'sword')
    for t, m, v, d in play('siegfried', T_SIEG, 1.0, -12, 122):
        add(t, d, m, v, 'sieg')
    for t, m, v, d in play('siegfried_horn', T_HORN, 0.9, 0, 124):
        add(t, d, m, v, 'horn')
    add(T_HORN, 0.1, 'C1', 120, 'crash')
    for t, m, v, d in play('brunnhilde', T_BRUNN, 0.7, -12, 112):
        add(t, d, m, v, 'brunn')
    for m in ('C2', 'G2', 'C3'):
        add(HAMMERS[-1] + 2, D - HAMMERS[-1] - 2, m, 56, 'night')
    return sorted(N, key=lambda e: e[0])


def body(G, t):
    """Where the body is at time t: carried a little way along the porch at the end."""
    a, b = at(G, *BODY_AT[0]), at(G, *BODY_AT[1])
    return a + (b - a) * smoothstep(T_BRUNN, D - 3, t)


def marchers(S, t):
    """The procession: torches joining at the free end of Right and marching the whole house, -> perceptual."""
    d, L = S['d'], S['L']
    out = np.zeros_like(d)
    v = 85.0
    step = 0.75 + 0.25 * np.cos(2 * np.pi * t / 1.1) ** 8         # every torch surges on the step
    for j, t0 in enumerate(np.arange(T_MARCH[0], T_MARCH[1], 1.7)):
        a = t - t0
        if a < 0:
            continue
        p = L + 20 - v * a
        if p < -40:
            continue
        g = smoothstep(0, 1.0, a) * (1 - smoothstep(T_MARCH[1] + 2, D - 2, t))
        out += g * step * (np.exp(-((d - p) / 7) ** 2) + 0.3 * np.exp(-((d - p) / 24) ** 2))
    return out


def render(G, seed=26):
    F = nframes(D)
    out = np.zeros((F, G.N, 3))
    S = stage(G)
    d, L = S['d'], S['L']
    N = compose()
    runs = ['Left', 'Right', 'Porch Front', 'Side', 'Porch Left', 'Porch Right']
    st = strokes()
    vol = [e for e in N if e[4] == 'volsung']
    sm = melody('siegmund')
    sl = melody('sieglinde')
    tw = melody('twins_love')
    sw = [(T_SWORD + b * 0.6, m) for b, _, m in melody('sword')]
    sg = [(T_SIEG + b * 1.0, m) for b, _, m in melody('siegfried')]
    hn = [(T_HORN + b * 0.9, m) for b, _, m in melody('siegfried_horn')]
    br = [(T_BRUNN + b * 0.7, m) for b, _, m in melody('brunnhilde')]
    p_gu = at(G, *GUNTHER_AT[:2])

    for f in range(F):
        t = f * DT
        T = t + 80 * K
        u = smoothstep(HAMMERS[-1], D - 3, t)
        lv = {k: START[k] + (END[k] - START[k]) * u for k in START}
        base = 1 - 0.4 * smoothstep(2, 6, t) * (1 - smoothstep(HAMMERS[-1] + 1, D - 4, t))
        fr = scene(S, T, {k: v * base for k, v in lv.items()})
        pb = body(G, t)

        # the Volsungs' destiny: indigo waves out of the body on every note, an indigo wash while it plays
        for t0, dur, m, v, _, k in vol:
            if m >= note('C3'):
                fr = ring(fr, S, t, t0, pb, FATE_C, 0.9, speed=700, width=200, tau=1.3)
        wash = sum(smoothstep(t0, t0 + 2, t) * (1 - smoothstep(t0 + 8, t0 + 10, t)) for t0, _ in VOLSUNG)
        fr += light(FATE_C, 0.45 * wash * (0.7 + 0.3 * np.sin(2 * np.pi * (d / 400 - 0.2 * t))))

        # Siegmund floods Left and the Side in blue, Sieglinde answers over Right and the river in amber
        left, right = d < pb, d > pb
        for b, _, m in sm:
            a = t - (T_SIEGMUND + 0.45 * b)
            if 0 <= a < 2.5:
                fr += light(SIEGMUND, 0.95 * np.exp(-a / 0.9) * left
                            * np.exp(-(((pb - d) - 1100 * a) / 220) ** 2))
        g = smoothstep(T_SIEGMUND, T_SIEGMUND + 3, t) * (1 - smoothstep(T_TWINS + 4, T_SWORD - 1, t))
        fr += light(SIEGMUND, 0.55 * g * left * (0.75 + 0.25 * np.sin(2 * np.pi * (d / 300 + 0.3 * t))))
        for b, _, m in sl:
            a = t - (T_SIEGLINDE + 0.45 * b)
            if 0 <= a < 2.5:
                fr += light(SIEGLINDE, 0.95 * np.exp(-a / 0.9) * right
                            * np.exp(-(((d - pb) - 1100 * a) / 220) ** 2))
        g = smoothstep(T_SIEGLINDE, T_SIEGLINDE + 3, t) * (1 - smoothstep(T_TWINS + 4, T_SWORD - 1, t))
        fr += light(SIEGLINDE, 0.55 * g * right * (0.75 + 0.25 * np.sin(2 * np.pi * (d / 300 - 0.3 * t))))

        # the twins' love: blue in from one end, amber from the other, meeting over the body in a white flash
        for b, dur, m in tw:
            t0 = T_TWINS + 0.45 * b
            a = t - t0
            if 0 <= a < 1.6:
                g = np.exp(-max(a - 1.0, 0) / 0.2)
                fr += light(SIEGMUND, 0.9 * g * np.exp(-((d - pb * min(1.0, a)) / 90) ** 2))
                fr += light(SIEGLINDE, 0.9 * g * np.exp(-((d - (L - (L - pb) * min(1.0, a))) / 90) ** 2))
            if 1.0 <= a < 1.6:
                fr += light(WHITE, 0.8 * np.exp(-(a - 1.0) / 0.12) * np.exp(-((d - pb) / 160) ** 2))

        # the Sword: every note a white steel sweep the length of the house, turning each time
        for j, (t0, m) in enumerate(sw):
            a = t - t0
            if 0 <= a < 0.9:
                x = (a / 0.6) * L if j % 2 == 0 else L - (a / 0.6) * L
                fr += light(STEEL, np.exp(-max(a - 0.6, 0) / 0.15) * (np.exp(-((d - x) / 110) ** 2)
                            + 0.7 * ((d < x) if j % 2 == 0 else (d > x)) * np.exp(-np.abs(d - x) / 500)))

        # Siegfried: each note slams a whole run emerald, and an emerald ring goes out
        for j, (t0, m) in enumerate(sg):
            a = t - t0
            if 0 <= a < 1.2:
                fr += light(SIEGFRIED, np.exp(-a / 0.5) * (G.seg_of == runs[j % len(runs)]))
                fr = ring(fr, S, t, t0, pb, SIEGFRIED, 0.8, speed=1500, width=140, tau=0.8)

        # his horn call as a vast statement: gold and emerald sweeping out to both ends on every note
        for j, (t0, m) in enumerate(hn):
            fr = ring(fr, S, t, t0, pb, GLINT, 1.0, speed=1200, width=180, tau=1.0)
            fr = ring(fr, S, t, t0 + 0.15, pb, SIEGFRIED, 0.9, speed=1000, width=120, tau=0.9)
        a = t - T_HORN
        if 0 <= a < 5.5:
            fr += light(GOLD, 0.7 * np.exp(-a / 1.5) * (0.7 + 0.3 * np.sin(2 * np.pi * (d / 250 - 1.2 * t))))

        # Brünnhilde: silver flooding every run at the top
        g = smoothstep(T_BRUNN, T_BRUNN + 2, t) * (1 - smoothstep(T_BRUNN + 5.5, HAMMERS[-1], t))
        fr += light(SILVER, 0.7 * g * (0.65 + 0.35 * np.sin(2 * np.pi * (d / 330 - 0.5 * t))))
        for t0, m in br:
            fr = ring(fr, S, t, t0, pb, SILVER, 0.9, speed=1000, width=150, tau=1.0)
            fr = ring(fr, S, t, t0 + 0.1, pb, GLINT, 0.7, speed=900, width=60, tau=0.8)

        # the death rhythm: a flash, then the house knocked almost black for a moment
        for t0, w in st:
            a = t - t0
            if 0 <= a < 1.6:
                fr = fr * (1 - 0.9 * w * (1 - np.exp(-a / 0.05)) * np.exp(-a / (0.35 + 0.4 * w)))
                fr += light(HIT, 0.85 * w * np.exp(-a / 0.07))
                fr = ring(fr, S, t, t0, pb, HIT, 0.7 * w, speed=1600, width=100, tau=0.6)

        # the procession, and the torches round the body
        fr += light(TORCH, np.clip(marchers(S, t), 0, 1.2))
        mid = smoothstep(4, 10, t) * (1 - smoothstep(HAMMERS[-1], D - 3, t))
        (l0, k0), (l1, k1) = TORCHES
        tl = l0 + (l1 - l0) * u - 0.25 * mid
        fr = torches(fr, S, T, tl, pull=pb, k=k0 + (k1 - k0) * u)

        # Gunther walking beside the bier, and the body
        fr = figure(fr, S, p_gu, GUNTHER, GUNTHER_AT[2])
        fr = figure(fr, S, pb, SIEGFRIED, BODY_AT[2], w=12)
        fr += light(GOLD, 0.4 * np.exp(-((d - pb - 14) / 5) ** 2))
        out[f] = fr
    return np.clip(out, 0, 1)


def score(M, G):
    from pixelhome.audio import SR
    pan_at = panner(G)
    for name, gain, rev in (('low', 0.24, 0.25), ('strings', 0.21, 0.32), ('brass', 0.23, 0.3), ('perc', 0.24, 0.3),
                            ('winds', 0.2, 0.35)):
        M.bus(name, gain=gain, reverb=rev)
    hold = hold_factory(M, SR)
    horn = M.sampler('Brass/F Horn/sus/*.wav', tune=-12)
    tbn = M.sampler('Brass/Tenor Trombone/sus/*.wav', tune=-12)
    tuba = M.sampler('Brass/Tuba/sus/*.wav', tune=-12)
    tpt = M.sampler('Brass/Trumpet/sus/*.wav', tune=-12)
    vc = M.sampler('Strings/Cello Section/susvib/*.wav', tune=-12)
    vla = M.sampler('Strings/Viola Section/susvib/*.wav', tune=-12)
    vln = M.sampler('Strings/Violin Section/susVib/*.wav', tune=-12)
    ctrem = M.sampler('Strings/Cello Section/trem/*.wav', tune=-12)
    cb = M.sampler('Strings/Solo Contrabass/SusNV/*.wav', tune=-12)
    oboe = M.sampler('Woodwinds/Oboe/Vib/*.wav', tune=-12)
    timp = M.hits('Percussion/Timpani/Timpani1_Hit*.wav')
    roll = M.hits('Percussion/Timpani/Rolls/*.wav')
    crash = M.hits('Percussion/cymbal-crash1_f*.wav')
    gong = M.hits('Percussion/gongHit_f*.wav')
    sf = pan_at(at(G, *BODY_AT[0]))
    left, right = pan_at(at(G, 'Left', 0.4)), pan_at(at(G, 'Right', 0.6))
    for t, d, m, v, part, k in compose():
        if part == 'trem':
            hold('low', ctrem, m, t, t + d, v, 0.0, rise=2.0, fall=2.0, gain=0.45)
        elif part == 'stroke':
            M.add('perc', timp.play(v, pitch=-5), t, 1.0, sf)
            if d > 1:
                M.add('perc', gong.play(100), t, 0.6, sf)
                M.add('perc', roll.play(90, pitch=-5, dur=1.4), t + 0.1, 0.5, sf)
        elif part == 'chord':
            s = tuba if m < note('C3') else tbn if m < note('G3') else horn
            M.add('brass', s.play(m, v, dur=d, release=0.4), t, 0.6, sf)
        elif part == 'volsung':
            if d > 1.0:
                hold('brass', horn, m, t, t + d, v, sf, rise=0.3, fall=1.0, gain=0.75)
            else:
                M.add('brass', horn.play(m, v, dur=d * 1.05, release=0.3), t, 0.85, sf)
            M.add('low', tuba.play(m - 12, v - 12, dur=d * 1.05, release=0.3), t, 0.6, sf)
        elif part == 'siegmund':
            if d > 1.0:
                hold('strings', vc, m, t, t + d, v, left, rise=0.3, fall=1.0, gain=0.8)
            else:
                M.add('strings', vc.play(m, v, dur=d * 1.05, release=0.3), t, 0.9, left)
            M.add('brass', horn.play(m, v - 20, dur=d * 1.05, release=0.3), t, 0.4, left)
        elif part == 'sieglinde':
            s = oboe if m >= note('D4') else vc
            M.add('winds' if s is oboe else 'strings', s.play(m, v, dur=d * 1.05, release=0.3), t, 0.85, right)
        elif part == 'twins':
            if d > 1.0:
                hold('strings', vla, m, t, t + d, v, 0.0, rise=0.3, fall=1.0, gain=0.7)
            else:
                M.add('strings', vla.play(m, v, dur=d * 1.05, release=0.3), t, 0.8, 0.0)
        elif part == 'sword':
            if d > 1.0:
                hold('brass', tpt, m - 12, t, t + d, v, 0.0, rise=0.05, fall=1.0, gain=0.8)
            else:
                M.add('brass', tpt.play(m - 12, v, dur=d * 1.05, release=0.3), t, 0.9, 0.0)
        elif part == 'sieg':
            M.add('brass', horn.play(m, v, dur=d * 1.05, release=0.3), t, 0.9, sf)
            M.add('brass', tbn.play(m - 12, v - 8, dur=d * 1.05, release=0.3), t, 0.7, sf)
            M.add('strings', vln.play(m, v - 16, dur=d * 1.05, release=0.3), t, 0.5, sf)
            M.add('perc', timp.play(v - 20, pitch=-3), t, 0.4, sf)
        elif part == 'horn':
            if d > 0.8:
                hold('brass', horn, m, t, t + d, v, 0.0, rise=0.08, fall=1.0, gain=0.85)
                hold('brass', tbn, m - 12, t, t + d, v - 10, 0.0, rise=0.08, fall=1.0, gain=0.6)
            else:
                M.add('brass', horn.play(m, v, dur=d * 1.1, release=0.3), t, 0.9, 0.0)
                M.add('brass', tbn.play(m - 12, v - 10, dur=d * 1.1, release=0.3), t, 0.6, 0.0)
            M.add('low', tuba.play(m - 24, v - 16, dur=d * 1.1, release=0.3), t, 0.6, 0.0)
        elif part == 'crash':
            M.add('perc', crash.play(v), t, 0.9)
            M.add('perc', timp.play(v, pitch=-5), t, 0.9)
        elif part == 'brunn':
            if d > 1.0:
                hold('brass', horn, m, t, t + d, v, sf, rise=0.15, fall=1.0, gain=0.8)
            else:
                M.add('brass', horn.play(m, v, dur=d * 1.05, release=0.3), t, 0.85, sf)
            M.add('strings', vln.play(m + 12, v - 18, dur=d * 1.05, release=0.3), t, 0.5, sf)
        elif part == 'night':
            hold('low', cb if m < note('G2') else vc, m, t, t + d, v, sf * 0.5, rise=3.0, fall=1.5, gain=0.5)
    for j, t0 in enumerate(np.arange(T_MARCH[0], T_MARCH[1], 1.1)):        # the tread of the procession
        M.add('perc', timp.play(46 + 6 * (j % 2), pitch=-10), t0, 0.35, right * (1 - (j % 30) / 15))
