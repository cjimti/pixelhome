"""Brünnhilde's Immolation: night in the hall by the Rhine, the vassals' torches drawn in round the porch, Siegfried
lying dead in the middle of Porch Front, Brünnhilde standing over him, Gutrune collapsed out on Right.

"Starke Scheite schichtet mir dort": she orders the pyre, and the men build it on the beat. Every stroke of the
timpani stacks another log on the porch, a white-hot bar that drops into place and glows orange, the stacks
climbing in from both ends of the porch toward him, each one sending an orange shock out over the house. Gutrune
fades away. Then love as fulfilment (Donington 90) sings in the violins: every note a silver wave out from her to
both ends of the house, his emerald stirring faintly in answer. She draws the Ring from his hand: a ring of gold
light travels from him to her and the whole house flashes gold.

"Fliegt heim, ihr Raben!" Two ravens tear away to the end of the Side in white wakes while Valhalla (63) blazes in
the Wagner tubas, every chord one whole run in gold-white over deep blue. She seizes a torch and hurls it: a
comet of fire arcs from her to the pyre, and the pyre goes up, flames rushing out across the porch from where it
landed, an orange shock to both ends, Loge (20) and his flickering (20a) leaping white-gold out of it. Over the
fire the Transformation (91) rises in the brass, and the pyre roars while she stands silver before it.

compose() holds every note; stage(), scene(), water(), figure(), torches(), sparks() and ring() are the valley,
shared word for word by Act III's scenes (GD22 to GD30) on a clock that runs on from scene to scene: T = t + 80 K."""
import numpy as np
from pixelhome.audio import note
from pixelhome.fx import DT, hexc, light, smoothstep, nframes, keys, Flicker, smooth_noise, colormap
from pixelhome.leitmotifs import play

CODE = 'GD28'
TITLE = "Brünnhilde's Immolation"
KIND = 'show'
DESCRIPTION = ('Brünnhilde orders a great pyre built for Siegfried, takes the Ring from his hand and sends the '
               "ravens home to Valhalla. Then she hurls a torch, and the pyre goes up in flames.")
VOICEOVER = ('Brünnhilde orders the pyre built high. She takes the Ring, sends the ravens home to Valhalla, '
             'and throws the torch.')

K = 6                                       # this scene's place on Act III's shared clock: T = t + 80 K
LOGS = [1.5 + 0.9 * j for j in range(22)]   # every stroke stacks a log on the pyre
T_LOVE = [22.5, 29.0]                       # love as fulfilment, the violins
T_RING = 36.0                               # she takes the Ring
T_RAVENS = 42.0
T_VALHALLA = 43.0                           # the Wagner tubas
T_THROW = 53.0                              # she hurls the torch
T_IGNITE = 54.4                             # the pyre goes up
LOGES = [55.0 + 1.6 * j for j in range(14)] # Loge's fire leaping out of the pyre
T_TRANS = 58.0                              # the Transformation, the brass
D = 80.0

SIEGFRIED = hexc('#00ff40')
SILVER = hexc('#f4f8ff')
GLINT = hexc('#ffd060')
GUTRUNE = hexc('#ff4090')
GOLD = hexc('#ffaa00')
LOG = hexc('#ff5a10')
TONGUE = hexc('#fff0b0')
SPILL = 0.75                                # firelight over the wings once the pyre burns (GD29 starts with it)

START = dict(river=0.3, forest=0.2, sun=0.0, night=0.45, pyre=0.1, blaze=0.0, valhalla=0.0, flood=0.0)
END = dict(river=0.3, forest=0.2, sun=0.0, night=0.35, pyre=0.95, blaze=0.0, valhalla=0.0, flood=0.0)
SIEG_AT = ('Porch Front', 0.5, 0.3)         # his body, dim, no head; gone into the fire at the end
BRUN_AT = ('Porch Front', 0.25, 0.85)       # 0.85 at the start, 0.9 at the end; gold glint 0.5 x level, +9, width 5
GUTRUNE_AT = ('Right', 0.3, 0.35)           # fades out
TORCHES = (0.5, 0.4, 0.5)                   # torch level at the start, at the end, and how far they draw in to him

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

    chords = [('C2', 'G2', 'Eb3'), ('Ab1', 'Eb2', 'C3'), ('F1', 'C2', 'Ab2'), ('G1', 'D2', 'B2')]
    for j, t0 in enumerate(LOGS):
        add(t0, 0.4, 'C2' if j % 2 == 0 else 'G1', 84 + j, 'log', j)
        if j % 4 == 0:
            for m in chords[(j // 4) % 4]:
                add(t0, 3.6, m, 82 + j, 'build')
    for k, t0 in enumerate(T_LOVE):
        for t, m, v, d in play('love_fulfilled', t0, 0.95, 0, 94 + 6 * k):
            add(t, d, m, v, 'love', k)
    for t, m, v, d in play('ring', T_RING, 0.45, 0, 92):
        add(t, d, m, v, 'ring')
    add(T_RING + 1.5, 0.1, 'C1', 110, 'flash')
    add(T_RAVENS, 2.4, 'C6', 100, 'ravens')
    for t, m, v, d in play('valhalla', T_VALHALLA, 0.95, 0, 112):
        add(t, d, m, v, 'valhalla')
    add(T_THROW, 1.4, 'C6', 110, 'throw')
    add(T_IGNITE, 0.1, 'C1', 127, 'ignite')
    for j, t0 in enumerate(LOGES):
        if t0 > D - 3:
            break
        for t, m, v, d in play('loge', t0, 0.2, 12 + (0, 3, 7, 12)[j % 4], 96):
            add(t, d, m, v, 'loge', j)
        for t, m, v, d in play('loge_flicker', t0 + 0.8, 0.12, 0, 84):
            add(t, d, m, v, 'flicker', j)
    for t, m, v, d in play('transformation', T_TRANS, 0.9, -12, 110):
        add(t, d, m, v, 'trans')
    for m in ('Db2', 'Ab2', 'F3'):
        add(T_TRANS, D - T_TRANS, m, 72, 'firebed')
    return sorted(N, key=lambda e: e[0])


def stacks(G):
    """Where each log lands on the pyre: in from both ends of the porch toward the middle, alternating sides."""
    lo, hi, mid = at(G, 'Porch Left', 0.55), at(G, 'Porch Right', 0.45), at(G, 'Porch Front', 0.5)
    out = []
    for j in range(len(LOGS)):
        u = (j // 2) / (len(LOGS) // 2)
        out.append(lo + (mid - 30 - lo) * u if j % 2 == 0 else hi - (hi - mid - 30) * u)
    return out


def raven(fr, S, t, t0, p0, p1, dur):
    """A raven flying from p0 to p1: a black fleck in a white wake."""
    a = t - t0
    if not 0 <= a < dur + 1.0:
        return fr
    d = S['d']
    u = min(1.0, a / dur)
    p = p0 + (p1 - p0) * u
    lo, hi = min(p0, p), max(p0, p)
    wake = (d >= lo) * (d <= hi) * np.exp(-np.abs(d - p) / 260) * np.exp(-max(a - dur, 0) / 0.3)
    fr = fr + light(WHITE, 0.85 * wake) + light(WHITE, 0.9 * np.exp(-((d - p) / 40) ** 2) * (u < 1))
    return fr * (1 - 0.95 * np.exp(-((d - p) / 10) ** 2) * (u < 1))[:, None]


def render(G, seed=28):
    F = nframes(D)
    out = np.zeros((F, G.N, 3))
    S = stage(G)
    d, L, pf = S['d'], S['L'], S['pf']
    N = compose()
    love = [e for e in N if e[4] == 'love' and e[1] >= 0.4]
    valh = sorted({e[0] for e in N if e[4] == 'valhalla'})
    lstart = [t0 for t0 in LOGES if t0 <= D - 3]
    trans = [e for e in N if e[4] == 'trans']
    land = stacks(G)
    p_sf, p_br, p_gu = at(G, *SIEG_AT[:2]), at(G, *BRUN_AT[:2]), at(G, *GUTRUNE_AT[:2])
    runs = ['Left', 'Porch Left', 'Porch Front', 'Porch Right', 'Right', 'Side']
    rng = np.random.default_rng(seed)
    leap_at = rng.uniform(0, L, 60)

    for f in range(F):
        t = f * DT
        T = t + 80 * K
        lv = dict(START)
        lit = smoothstep(T_IGNITE, T_IGNITE + 3.0, t)
        lv['pyre'] = START['pyre'] + (END['pyre'] - START['pyre']) * lit
        lv['night'] = START['night'] + (END['night'] - START['night']) * lit
        fr = scene(S, T, lv)

        # the logs: each drops onto the pyre white-hot and stays glowing orange, with an orange shock outward
        built = np.zeros_like(d)
        for j, (t0, p) in enumerate(zip(LOGS, land)):
            a = t - t0
            if a < 0:
                continue
            bar = np.exp(-((d - p) / 18) ** 4)
            built = np.maximum(built, bar)
            if a < 0.6:
                fr += light(WHITE, 0.9 * np.exp(-a / 0.12) * bar)
            fr = ring(fr, S, t, t0, p, LOG, 0.95, speed=1500, width=170, tau=0.55)
            if a < 0.5:
                fr += light(LOG, 0.5 * np.exp(-a / 0.15) * (G.seg_of == G.seg_of[np.argmin(np.abs(d - p))]))
        fr += light(LOG, 0.62 * built * S['porch'] * (1 - lit) * (0.85 + 0.15 * S['fl'](T)))

        # love as fulfilment: silver waves out from her on every long note, his emerald stirring in answer
        for t0, dur, m, v, _, k in love:
            fr = ring(fr, S, t, t0, p_br, SILVER, 1.0, speed=1100, width=240, tau=1.2)
            fr = ring(fr, S, t, t0 + 0.25, p_br, GLINT, 0.75, speed=900, width=110, tau=0.9)

        # the Ring: gold travels from him to her, then the whole house flashes gold
        a = t - T_RING
        if 0 <= a < 1.5:
            p = p_sf + (p_br - p_sf) * smoothstep(0, 1.5, a)
            fr += light(GOLD, 1.0 * np.exp(-((d - p) / 14) ** 2)) + light(GOLD, 0.5 * np.exp(-((d - p) / 60) ** 2))
        if 1.5 <= a < 5:
            aa = a - 1.5
            fr += light(GOLD, 1.0 * np.exp(-aa / 0.7))
            fr = ring(fr, S, t, T_RING + 1.5, p_br, GOLD, 1.0, speed=1500, width=260, tau=1.2)

        # the ravens home to Valhalla, and its chords, one whole run in gold-white over deep blue each
        fr = raven(fr, S, t, T_RAVENS, p_br, 0.0, 2.6)
        fr = raven(fr, S, t, T_RAVENS + 0.3, p_br, 0.0, 2.9)
        i = int(np.searchsorted(valh, t, side='right')) - 1
        if i >= 0 and t - valh[i] < 1.4:
            aa = t - valh[i]
            run = G.seg_of == runs[i % len(runs)]
            fr += light(VBLUE, 0.6 * np.exp(-aa / 0.8))
            fr += light(VALHALLA, 0.95 * np.exp(-aa / 0.6) * run)

        # the torch thrown: a comet of fire arcing from her to the pyre, then it goes up
        a = t - T_THROW
        if 0 <= a < T_IGNITE - T_THROW:
            p = p_br + (pf - p_br) * smoothstep(0, T_IGNITE - T_THROW, a)
            fr += light(AMBER, 1.0 * np.exp(-((d - p) / 9) ** 2)) + light(ORANGE, 0.7 * np.exp(-((d - p) / 40) ** 2))
        a = t - T_IGNITE
        if 0 <= a < 4:
            front = 600 * smoothstep(0, 1.6, a)
            rush = (np.abs(d - pf) < front) * S['porch']
            fr += light(AMBER, 0.85 * rush * np.exp(-a / 1.5))
            fr += light(WHITE, 0.8 * np.exp(-a / 0.15) * np.exp(-((d - pf) / 60) ** 2))
            fr = ring(fr, S, t, T_IGNITE, pf, ORANGE, 1.0, speed=1300, width=200, tau=1.3)
            fr = ring(fr, S, t, T_IGNITE + 0.2, pf, AMBER, 0.8, speed=1700, width=90, tau=1.0)

        # Loge's fire leaping out of the pyre: a tongue of flame racing out along the roofline on each figure
        for j, t0 in enumerate(lstart):
            a = t - t0
            if 0 <= a < 1.6:
                way = 1 if j % 2 == 0 else -1
                p = pf + way * (250 + 900 * smoothstep(0, 1.4, a))
                p = pf + way * (250 + 1500 * smoothstep(0, 1.4, a))
                fr += light(AMBER, 1.0 * np.exp(-a / 0.8) * np.exp(-((d - p) / 110) ** 2))
                fr += light(TONGUE, 0.9 * np.exp(-a / 0.5) * np.exp(-((d - p) / 30) ** 2))
        # the pyre's light thrown out over the whole valley
        fr += light(ORANGE, SPILL * lit * (1 - S['porch']) * np.exp(-np.abs(d - pf) / 1500) * (0.7 + 0.3 * S['fl'](T)))
        # the Transformation: on each note the whole fire surges up gold
        for t0, dur, m, v, _, k in trans:
            a = t - t0
            if 0 <= a < dur + 1:
                g = np.exp(-a / (dur * 0.6 + 0.4)) * smoothstep(0, 0.2, a)
                fr += light(AMBER, 0.6 * g * S['pyre'])
                fr = ring(fr, S, t, t0, pf, AMBER, 0.75, speed=1000, width=180, tau=1.2)

        # torches drawn in round the pyre, fading as it burns
        tl = TORCHES[0] + (TORCHES[1] - TORCHES[0]) * smoothstep(T_IGNITE, D - 4, t)
        fr = torches(fr, S, T, tl, pull=p_sf, k=TORCHES[2])

        # the people: Gutrune fading, Siegfried until the fire takes him, Brünnhilde
        lg = GUTRUNE_AT[2] * (1 - smoothstep(6, 16, t))
        if lg > 0:
            fr = figure(fr, S, p_gu, GUTRUNE, lg, w=20)
        ls = SIEG_AT[2] * (1 + 0.6 * sum(np.exp(-max(t - e[0], 0) / 0.6) * (t >= e[0]) for e in love)) \
            * (1 - smoothstep(T_IGNITE, T_IGNITE + 4, t))
        if ls > 0.005:
            fr = figure(fr, S, p_sf, SIEGFRIED, min(ls, 0.7))
            fr += light(GOLD, 0.6 * (t < T_RING) * np.exp(-((d - p_sf - 14) / 5) ** 2))
        lb = BRUN_AT[2] + 0.05 * smoothstep(T_IGNITE, T_IGNITE + 4, t)
        fr = figure(fr, S, p_br, SILVER, lb)
        fr += light(GLINT, 0.5 * lb * np.exp(-((d - p_br - 9) / 5) ** 2))
        if t >= T_RING + 1.5:
            fr += light(GOLD, 0.6 * np.exp(-((d - p_br + 10) / 5) ** 2))
        out[f] = fr
    return np.clip(out, 0, 1)


def score(M, G):
    from pixelhome.audio import SR, whoosh
    pan_at = panner(G)
    for name, gain, rev in (('low', 0.36, 0.25), ('strings', 0.34, 0.32), ('winds', 0.3, 0.35), ('brass', 0.36, 0.3),
                            ('perc', 0.34, 0.3), ('fx', 0.14, 0.3), ('mallet', 0.16, 0.3)):
        M.bus(name, gain=gain, reverb=rev)
    hold = hold_factory(M, SR)
    vln = M.sampler('Strings/Violin Section/susVib/*.wav', tune=-12)
    vc = M.sampler('Strings/Cello Section/susvib/*.wav', tune=-12)
    cb = M.sampler('Strings/Solo Contrabass/SusNV/*.wav', tune=-12)
    horn = M.sampler('Brass/F Horn/sus/*.wav', tune=-12)
    tbn = M.sampler('Brass/Tenor Trombone/sus/*.wav', tune=-12)
    tuba = M.sampler('Brass/Tuba/sus/*.wav', tune=-12)
    tpt = M.sampler('Brass/Trumpet/sus/*.wav', tune=-12)
    clar = M.sampler('Woodwinds/Clarinet/susLong/*.wav', tune=-12)
    picc = M.sampler('Woodwinds/Piccolo/Sus/*.wav', tune=-12)
    harp = M.sampler('Strings/Harp/*.wav')
    glock = M.sampler('Percussion/Glock/*.wav')
    timp = M.hits('Percussion/Timpani/Timpani1_Hit*.wav')
    roll = M.hits('Percussion/Timpani/Rolls/*.wav')
    crash = M.hits('Percussion/cymbal-crash1_f*.wav')
    gong = M.hits('Percussion/gongHit_f*.wav')
    pf = pan_at(at(G, 'Porch Front', 0.5))
    br = pan_at(at(G, *BRUN_AT[:2]))
    stk = [pan_at(p) for p in stacks(G)]
    for t, d, m, v, part, k in compose():
        if part == 'log':
            M.add('perc', timp.play(v, pitch=-5 if k % 2 == 0 else -10), t, 0.85, stk[k])
            M.add('low', cb.play(m, v - 10, dur=0.5, release=0.2), t, 0.6, stk[k])
        elif part == 'build':
            hold('brass', tbn if m >= note('C3') else tuba, m, t, t + d, v, pf, rise=0.1, fall=1.0, gain=0.6)
        elif part == 'love':
            if d > 0.9:
                hold('strings', vln, m, t, t + d, v, br, rise=0.2, fall=1.0, gain=0.9)
            else:
                M.add('strings', vln.play(m, v, dur=d * 1.1, release=0.3), t, 0.9, br)
            M.add('low', vc.play(m - 12, v - 18, dur=d * 1.1, release=0.3), t, 0.5, br)
        elif part == 'ring':
            M.add('winds', clar.play(m, v, dur=d * 1.1, release=0.3), t, 0.85, br)
        elif part == 'flash':
            M.add('perc', crash.play(100), t, 0.8, br)
        elif part == 'ravens':
            M.add('fx', whoosh(d, 900, 5000, 0.8, seed=28), t, 0.9, -0.7)
            M.add('fx', whoosh(d, 900, 5000, 0.8, seed=29), t + 0.3, 0.9, -0.9)
        elif part == 'valhalla':
            if m >= note('Db4'):
                hold('brass', horn, m - 12, t, t + d, v, 0.0, rise=0.08, fall=1.0, gain=0.8)
            else:
                hold('low', tuba, m, t, t + d, v, 0.0, rise=0.08, fall=1.0, gain=0.8)
        elif part == 'throw':
            M.add('fx', whoosh(d, 600, 4500, 0.9, seed=31), t, 1.0, br)
        elif part == 'ignite':
            M.add('perc', gong.play(v), t, 0.9, pf)
            M.add('perc', crash.play(v), t, 0.9, pf)
            M.add('perc', timp.play(v, pitch=-7), t, 1.0, pf)
            M.add('perc', roll.play(110, pitch=-3, dur=3.0), t, 0.8, pf)
            M.add('fx', whoosh(2.5, 300, 6000, 0.9, seed=33), t - 0.1, 1.0, pf)
        elif part == 'loge':
            M.add('strings', vln.play(m, v, dur=d * 1.2, release=0.1), t, 0.6, pf + (0.4 if k % 2 == 0 else -0.4))
            M.add('mallet', harp.play(m, v - 10), t, 0.5, pf)
        elif part == 'flicker':
            M.add('winds', picc.play(m, v, dur=d * 1.1, release=0.1), t, 0.45, pf)
            M.add('mallet', glock.play(m, v - 20), t, 0.4, pf)
        elif part == 'trans':
            hold('brass', tpt, m - 12, t, t + d, v, pf, rise=0.2, fall=1.2, gain=0.75)
            hold('brass', tbn, m - 24, t, t + d, v - 10, pf, rise=0.2, fall=1.2, gain=0.6)
        elif part == 'firebed':
            hold('low', vc if m >= note('C3') else cb, m, t, t + d, v, pf, rise=3.0, fall=1.5, gain=0.5)
