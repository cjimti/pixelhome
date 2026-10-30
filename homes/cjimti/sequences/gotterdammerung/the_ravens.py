"""The Ravens: the valley as GD23 left it, the hunt gathered on the porch with its torches, Siegfried in the middle of
Porch Front, Gunther beside him and Hagen behind, violet menace pulsing out from Hagen. "Was hör' ich!" Two ravens
burst up from the porch, black flecks in white wakes, one tearing away along Left to the end of the Side, the other
out along Right to its free end. Hagen's spear rises, glinting, and on the orchestra's fortissimo it goes into
Siegfried's back: one white flash over the whole house, then the house drowns in ultraviolet and black, a steel
line from Hagen to him, and blood red bursting out from him to both ends. The Curse pours down, every chord a blood
red wave; Siegfried's emerald staggers, shrinks and sinks; the vassals' torches flare and shake; Gunther starts back.
"Meineid rächt' ich!": on Hagen's three heavy chords indigo rolls over the house, and he turns and walks away out of
the free end of Right, a violet shadow dragging behind him, while dusk comes down over the valley and the ravens
cross the whole house again. His heartbeat goes on, a red ring out from him, slower and weaker, and the torches draw
in round him.

The music is Wagner's own, Act III, bars 833 to 849 and 853 to 859 as Solti's 1958 Vienna Philharmonic recording
takes them, from the Wagner Ring Dataset's piano reduction (pixelhome/ring.py): the full orchestra for the blow,
trombones, tuba and basses for the Curse and Hagen's chords. Staged: the ravens' wings beating away, a rush and a
blow in the back with a crash of steel, a gong for the Curse, a thud as he falls, timpani on Hagen's chords, and his
heartbeat low on the timpani, fading.

compose() holds every note; stage(), scene(), water(), figure(), torches(), sparks() and ring() are the valley,
shared word for word by Act III's scenes (GD22 to GD30) on a clock that runs on from scene to scene: T = t + 80 K."""
import numpy as np
from pixelhome.audio import note
from pixelhome.fx import DT, hexc, light, smoothstep, nframes, Flicker, smooth_noise, colormap
from pixelhome.ring import Orchestra, excerpt, tidy

CODE = 'GD24'
TITLE = 'The Ravens'
KIND = 'show'
DESCRIPTION = ('Two ravens fly up, and while Siegfried turns to watch them Hagen drives his spear into his back. '
               'Hagen walks away into the dusk, and the hero lies dying among the torches.')
VOICEOVER = ('Two ravens fly up out of the trees. Siegfried turns to look, and Hagen strikes.')

K = 2                                       # this scene's place on Act III's shared clock: T = t + 80 K
EX = excerpt(__file__)                      # Act III, bars 833-850 and 853-860, Solti 1958
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


T_PLOT = 0.0                                # the conspiracy
T_RAVENS = when(836)                        # "Was hör' ich!": two ravens burst up
T_SPEAR = when(846)                         # "Rache rieten sie mir!": Hagen's spear
T_CURSE = when(848)
T_FALL = (T_SPEAR + 2.0, T_SPEAR + 9.0)     # Siegfried staggers and sinks
T_GO = (when(856), when(859))               # "Meineid rächt' ich!": Hagen walks away out of the free end of Right
T_DUSK = (T_SPEAR + 8.0, D)
T_FATE = [when(856), when(857), when(858)]
T_CROSS = [SEG[1] + 0.5, when(856.5), D - 8.0]  # the ravens cross the house again

SIEGFRIED = hexc('#00ff40')
HEAD = hexc('#e8ffe8')
GOLD = hexc('#ffaa00')
HAGEN = hexc('#7a00ff')
GUNTHER = hexc('#ffb020')
STEEL = hexc('#c8d8ff')
BLOOD = hexc('#d00010')
FATE_C = hexc('#5a30ff')
TWILIGHT = hexc('#a0207a')

START = dict(river=0.72, forest=0.62, sun=0.75, night=0.0, pyre=0.0, blaze=0.0, valhalla=0.0, flood=0.0)
END = dict(river=0.55, forest=0.4, sun=0.0, night=0.25, pyre=0.0, blaze=0.0, valhalla=0.0, flood=0.0)
SIEG_AT = ('Porch Front', 0.65)             # Siegfried: 0.85 at the start; at the end 0.45 * (0.8 + 0.2 sin(2 pi t / 0.7))
HAGEN_AT = ('Porch Front', 0.85, 0.8)       # at the start; gone out of the free end of Right by T_GO[1]
GUNTHER_AT = ('Porch Front', 0.3, 0.7)      # 0.7 at the start, 0.6 at the end
TORCHES = (0.5, 0.45, 0.3)                  # torch level at the start, at the end, and how far they draw in to him

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


def compose():
    """Every event for the lights, from the excerpt's notes: (time, seconds, midi, velocity, part, k). Hagen's
    menace before the ravens ('plot'), the Curse pouring down after the blow ('curse'), Hagen's three chords as he
    goes ('fate') and the dusk's last notes ('down')."""
    N = []
    notes = EX['notes']
    inside = lambda n, a, b: a <= n[0] < b
    calm = lambda t: not T_RAVENS - 0.2 <= t < T_RAVENS + 2.5
    for t in thin([n[0] for n in notes if inside(n, T_PLOT, T_SPEAR - 0.3) and calm(n[0])], 0.6):
        N.append((t, 0.5, 60, 90, 'plot', None))
    for t in thin([n[0] for n in notes if inside(n, T_CURSE, SEG[1]) and n[3] >= 80], 0.7):
        N.append((t, 0.5, note('D3'), 114, 'curse', None))
    for j, t in enumerate(T_FATE):
        N.append((t, 2.0, note('A3'), 110, 'fate', j))
    for t in thin([n[0] for n in notes if inside(n, when(859), D)], 1.0):
        N.append((t, 1.2, note('Ab4'), 80, 'down', None))
    return sorted(N, key=lambda e: e[0])


def beats():
    """His heartbeat: slower and weaker as he dies."""
    out, t, gap = [], T_FALL[1] + 1.0, 1.2
    while t < D - 1.0:
        out.append(t)
        t += gap
        gap = min(gap * 1.04, 2.6)
    return out


def where(G, t):
    """Siegfried, Hagen and Gunther at time t: (path distance, level) each."""
    ps = at(G, *SIEG_AT)
    sink = smoothstep(*T_FALL, t)
    flick = 0.8 + 0.2 * np.sin(2 * np.pi * t / 0.7)
    ls = 0.85 + (0.45 * flick - 0.85) * sink
    stagger = 14 * np.sin(2 * np.pi * (t - T_FALL[0]) / 1.3) * (T_FALL[0] <= t) * (1 - sink)
    h0, h1 = at(G, *HAGEN_AT[:2]), at(G, 'Right', 1.0) + 40
    ph = h0 + (h1 - h0) * smoothstep(*T_GO, t)
    lh = HAGEN_AT[2] * (1 - smoothstep(T_GO[1] - 1.5, T_GO[1], t))
    pg = at(G, *GUNTHER_AT[:2]) - 30 * smoothstep(T_SPEAR, T_SPEAR + 1.5, t) * (1 - smoothstep(T_SPEAR + 20, T_SPEAR + 30, t))
    lg = GUNTHER_AT[2] - 0.1 * smoothstep(T_DUSK[0], T_DUSK[1], t)
    return (ps + stagger, ls), (ph, lh), (pg, lg)


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


def render(G, seed=24):
    F = nframes(D)
    out = np.zeros((F, G.N, 3))
    S = stage(G)
    d, L = S['d'], S['L']
    N = compose()
    notes = {p: [e for e in N if e[4] == p] for p in ('plot', 'curse', 'fate', 'down')}
    hb = beats()
    p_sf = at(G, *SIEG_AT)
    take_off = at(G, 'Porch Front', 0.75)

    for f in range(F):
        t = f * DT
        T = t + 80 * K
        dusk = smoothstep(*T_DUSK, t)
        lv = {k: START[k] + (END[k] - START[k]) * dusk for k in START}
        drown = smoothstep(T_SPEAR, T_SPEAR + 0.4, t) * (1 - smoothstep(T_SPEAR + 4, T_SPEAR + 10, t))
        lv = {k: v * (1 - 0.6 * drown) for k, v in lv.items()}
        fr = scene(S, T, lv)
        (ps, ls), (ph, lh), (pg, lg) = where(G, t)

        # the conspiracy: violet pulses out from Hagen
        for t0, dur, m, v, _, k in notes['plot']:
            fr = ring(fr, S, t, t0, ph, HAGEN, 0.9, speed=800, width=150, tau=0.9)
        raise_ = smoothstep(when(844), T_SPEAR, t) * (t < T_SPEAR)      # the spear raised, glinting
        fr += light(STEEL, 0.9 * raise_ * np.exp(-((d - ph) / (20 + 60 * raise_)) ** 2))

        # the ravens burst up, one each way, and later cross the whole house
        fr = raven(fr, S, t, T_RAVENS, take_off, 0.0, 2.4)
        fr = raven(fr, S, t, T_RAVENS + 0.2, take_off, L, 2.0)
        for j, t0 in enumerate(T_CROSS):
            a, b = (L, 0.0) if j % 2 == 0 else (0.0, L)
            fr = raven(fr, S, t, t0, a, b, 2.6)
            fr = raven(fr, S, t, t0 + 0.35, a, b, 2.6)

        # the spear: one white flash, the house drowned in ultraviolet and black, a steel line, blood both ways
        a = t - T_SPEAR
        if 0 <= a < 0.5:
            fr += light(WHITE, 0.9 * np.exp(-a / 0.1))
        if 0 <= a < 10:
            fr += light(HAGEN, 0.75 * drown * (0.6 + 0.4 * np.sin(2 * np.pi * (d / 300 - 0.6 * a))))
            fr *= (1 - 0.5 * drown * np.clip(np.sin(2 * np.pi * (d / 180 + 0.9 * a)), 0, 1))[:, None]
            band = (d >= min(ph, ps) - 6) * (d <= max(ph, ps) + 6)
            fr += light(STEEL, 1.0 * band * np.exp(-a / 1.2))
            fr = ring(fr, S, t, T_SPEAR, ps, BLOOD, 1.0, speed=1200, width=150, tau=1.2)
            fr = ring(fr, S, t, T_SPEAR + 0.3, ps, BLOOD, 0.8, speed=900, width=100, tau=1.0)
        for t0, dur, m, v, _, k in notes['curse']:
            if m >= note('C3'):
                fr = ring(fr, S, t, t0, ps, BLOOD, 0.85, speed=1000, width=110, tau=0.8)

        # fate and the twilight of the gods
        for t0, dur, m, v, _, k in notes['fate']:
            if True:
                fr = ring(fr, S, t, t0, ps, FATE_C, 0.95, speed=850, width=220, tau=1.4)
        for t0, dur, m, v, _, k in notes['down']:
            aa = t - t0
            if 0 <= aa < dur + 1.0:
                g = np.exp(-aa / (dur + 0.6)) * smoothstep(0, 0.15, aa)
                fr += light(TWILIGHT, 0.7 * g * (0.6 + 0.4 * np.sin(2 * np.pi * (d / 420 - 0.15 * t))))

        # his heartbeat: red out from him, weaker
        for j, tb in enumerate(hb):
            fr = ring(fr, S, t, tb, ps, BLOOD, 1.0 * (1 - 0.5 * j / max(1, len(hb))), speed=800, width=140, tau=0.7)

        # the vassals' torches: flare and shake at the blow, then draw in round him
        shake = smoothstep(T_SPEAR, T_SPEAR + 0.3, t) * (1 - smoothstep(T_SPEAR + 3, T_SPEAR + 8, t))
        tl = TORCHES[0] + (TORCHES[1] - TORCHES[0]) * dusk + 0.5 * shake * (0.6 + 0.4 * np.sin(31 * t))
        fr = torches(fr, S, T, tl, pull=p_sf, k=TORCHES[2] * smoothstep(T_GO[0], D - 4, t))

        # the people
        if lh > 0:
            fr = fr * (1 - 0.6 * lh * np.exp(-((d - ph) / 70) ** 2))[:, None]
            trail = (d < ph) * (d > ph - 220) * np.exp(-(ph - d) / 90) * smoothstep(T_GO[0], T_GO[0] + 1, t)
            fr += light(HAGEN, 0.6 * lh * trail)
            fr = figure(fr, S, ph, HAGEN, lh)
            fr += light(STEEL, 0.6 * lh * np.exp(-((d - ph - 16) / 5) ** 2))
        fr = figure(fr, S, pg, GUNTHER, lg)
        fr = figure(fr, S, ps, SIEGFRIED, ls, w=16 - 4 * smoothstep(*T_FALL, t))
        fr += light(HEAD, 0.8 * ls * np.exp(-((d - ps) / 6) ** 2))
        fr += light(GOLD, 0.6 * np.exp(-((d - ps - 14) / 5) ** 2))
        out[f] = fr
    return np.clip(out, 0, 1)


def score(M, G):
    """Wagner's notes from the piano reduction, and the ravens, the spear and the dying as a production would stage
    them."""
    from pixelhome.audio import whoosh
    pan_at = panner(G)
    o = Orchestra(M, level=2.5)
    sf = pan_at(at(G, *SIEG_AT))

    def role(t, d, m, v, h):
        if t >= T_CURSE and h == 1 and d >= 0.3 and m < 60:    # the Curse and Hagen's chords: trombones and tuba
            return [('trombones', 12 if m < 40 else 0, 0, 0.7), ('tuba', 0, -6, 0.5), ('basses', 0, -8, 0.4)]
        return None

    o.tutti(tidy(EX['notes']), size=lambda t: 1.0 if t < SEG[1] else 0.8, role=role, pan=lambda t, m: sf * 0.6)
    # the ravens: wings beating away, one each way, and later across the house
    for p1, dt in ((0.0, 0.0), (1.0, 0.2)):
        M.add('fx', whoosh(1.6, 2500, 500, 0.55, seed=int(30 + 10 * p1)), T_RAVENS + dt, 0.9, -0.8 + 1.6 * p1)
    for j, t0 in enumerate(T_CROSS):
        M.add('fx', whoosh(2.4, 2000, 600, 0.4, seed=40 + j), t0, 0.7, 0.8 if j % 2 == 0 else -0.8)
    # the spear: a rush, a blow in the back, steel, and the house drowned
    M.add('fx', whoosh(0.5, 600, 4000, 0.7, seed=24), T_SPEAR - 0.45, 1.0, pan_at(at(G, *HAGEN_AT[:2])))
    o.boom(T_SPEAR, sf, 1.0)
    o.hit('metal', T_SPEAR, 120, gain=0.5, pan=sf)
    o.hit('crash', T_SPEAR, 124, gain=0.6, pan=sf)
    o.hit('gong', T_CURSE, 110, gain=0.45, pan=sf)
    o.hit('bass drum', T_FALL[1] - 0.5, 110, gain=0.55, pan=sf)  # he falls
    for t in T_FATE:                                         # Hagen's chords as he goes
        o.hit('timpani', t, 116, pitch=-6, gain=0.55, pan=pan_at(at(G, *HAGEN_AT[:2])))
    o.hit('gong scrape', T_GO[1] - 1.0, 96, gain=0.4, pan=0.8)
    for j, tb in enumerate(beats()):                         # his heartbeat, low on the timpani, fading
        g = 0.32 * (1 - 0.6 * j / max(1, len(beats())))
        o.hit('timpani', tb, 80, pitch=-9, gain=g, pan=sf)
    o.effects([(0.0, -6), (T_RAVENS - 0.3, -2), (T_RAVENS + 3.0, -8), (T_SPEAR - 0.6, -2), (T_SPEAR + 2.0, -8),
               (SEG[1], -10), (T_CROSS[1] - 0.3, -6), (D, -6)])
