"""The Ravens: the valley as GD23 left it, the hunt gathered on the porch with its torches, Siegfried in the middle of
Porch Front, Gunther beside him and Hagen behind. The conspiracy (Donington 75) slides in on the oboes, violet
pulses beating out from Hagen. "Do you understand what those ravens say?" Two ravens burst up from the porch, black
flecks in white wakes, one tearing away along Left to the end of the Side, the other out along Right to its free
end.

"Rache!" On Hagen's falling tritone (61a) his spear goes into Siegfried's back: one white flash over the whole
house, then the house drowns in ultraviolet and black, a steel line from Hagen to him, and blood red bursting out
from him to both ends. The Curse (13) blares on the trombones, every note a blood red wave. Siegfried's emerald
staggers, shrinks and sinks; the vassals' torches flare and shake; Gunther starts back. Hagen turns and walks away
out of the free end of Right, a violet shadow dragging behind him, while dusk comes down over the valley.

The rest is the dying: a red heartbeat out from Siegfried, slower and weaker; the power of fate (84) rolling
indigo over the house twice; the Twilight of the Gods (4) darkening the sky red-violet; the ravens crossing the
whole house again and again in streaks of white; and the torches drawing in round him as his emerald flickers low.

compose() holds every note; stage(), scene(), water(), figure(), torches(), sparks() and ring() are the valley,
shared word for word by Act III's scenes (GD22 to GD30) on a clock that runs on from scene to scene: T = t + 80 K."""
import numpy as np
from pixelhome.audio import note
from pixelhome.fx import DT, hexc, light, smoothstep, nframes, keys, Flicker, smooth_noise, colormap, heartbeat
from pixelhome.leitmotifs import play

CODE = 'GD24'
TITLE = 'The Ravens'
KIND = 'show'
DESCRIPTION = ('Two ravens fly up, and while Siegfried turns to watch them Hagen drives his spear into his back. '
               'Hagen walks away into the dusk, and the hero lies dying among the torches.')
VOICEOVER = ('Two ravens fly up out of the trees. Siegfried turns to look, and Hagen strikes.')

K = 2                                       # this scene's place on Act III's shared clock: T = t + 80 K
T_PLOT = 0.8                                # the conspiracy
T_RAVENS = 5.0                              # two ravens burst up
T_SPEAR = 8.5                               # Hagen's spear
T_CURSE = 10.0
T_FALL = (11.0, 18.0)                       # Siegfried staggers and sinks
T_GO = (20.0, 34.0)                         # Hagen walks away out of the free end of Right
T_DUSK = (18.0, 40.0)
T_FATE = [37.0, 49.0]
T_DOWN = 61.0
T_CROSS = [43.0, 57.5, 70.0]                # the ravens cross the house again
D = 80.0

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


def compose():
    """Every note: (time, seconds, midi, velocity, part, k)."""
    N = []

    def add(t, d, m, v, part, k=None):
        N.append((float(t), float(d), note(m) if isinstance(m, str) else int(m), int(v), part, k))

    add(0.0, T_SPEAR, 'D2', 66, 'trem')
    for t, m, v, d in play('plot', T_PLOT, 0.4, 0, 90):
        add(t, d, m, v, 'plot')
    add(T_RAVENS, 1.5, 'C6', 100, 'ravens')
    for t, m, v, d in play('hagen', T_SPEAR, 0.6, -12, 124):
        add(t, d, m, v, 'hagen')
    add(T_SPEAR, 0.1, 'C1', 127, 'blow')
    for t, m, v, d in play('curse', T_CURSE, 0.4, 0, 114):
        add(t, d, m, v, 'curse')
    for j, m in enumerate(('E3', 'D3', 'C3', 'Bb2', 'A2', 'G2', 'F2', 'E2')):
        add(T_FALL[0] + 0.5 * j, 0.6, m, 100 - 5 * j, 'sink')
    for j, t0 in enumerate(T_FATE):
        for t, m, v, d in play('fate', t0, 0.75, 0, 96 - 6 * j):
            add(t, d, m, v, 'fate', j)
    for t, m, v, d in play('downfall', T_DOWN, 0.7, -12, 92):
        add(t, d, m, v, 'down')
    for t0 in T_CROSS:
        add(t0, 1.6, 'C6', 80, 'ravens')
    for m in ('E2', 'B2', 'G3'):
        add(T_DUSK[0], D - T_DUSK[0], m, 54, 'dusk')
    for j, tb in enumerate(beats()):
        add(tb, 0.3, 'E1', int(max(50, 90 - 2 * j)), 'heart')
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
    pg = at(G, *GUNTHER_AT[:2]) - 30 * smoothstep(T_SPEAR, T_SPEAR + 1.5, t) * (1 - smoothstep(30, 40, t))
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
    notes = {p: [e for e in N if e[4] == p] for p in ('plot', 'curse', 'fate', 'down', 'hagen')}
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
            fr = ring(fr, S, t, t0, ph, HAGEN, 0.75, speed=800, width=120, tau=0.8)

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
            if m >= note('Ab3'):
                fr = ring(fr, S, t, t0, ps, FATE_C, 0.95, speed=850, width=220, tau=1.4)
        for t0, dur, m, v, _, k in notes['down']:
            aa = t - t0
            if 0 <= aa < dur + 1.0 and m >= note('Gb4'):
                g = np.exp(-aa / (dur + 0.6)) * smoothstep(0, 0.15, aa)
                fr += light(TWILIGHT, 0.7 * g * (0.6 + 0.4 * np.sin(2 * np.pi * (d / 420 - 0.15 * t))))

        # his heartbeat: red out from him, weaker
        for j, tb in enumerate(hb):
            fr = ring(fr, S, t, tb, ps, BLOOD, 1.0 * (1 - 0.5 * j / max(1, len(hb))), speed=800, width=140, tau=0.7)

        # the vassals' torches: flare and shake at the blow, then draw in round him
        shake = smoothstep(T_SPEAR, T_SPEAR + 0.3, t) * (1 - smoothstep(T_SPEAR + 3, T_SPEAR + 8, t))
        tl = TORCHES[0] + (TORCHES[1] - TORCHES[0]) * dusk + 0.5 * shake * (0.6 + 0.4 * np.sin(31 * t))
        fr = torches(fr, S, T, tl, pull=p_sf, k=TORCHES[2] * smoothstep(40, 72, t))

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
    from pixelhome.audio import SR, whoosh
    pan_at = panner(G)
    for name, gain, rev in (('low', 0.4, 0.25), ('strings', 0.34, 0.32), ('winds', 0.36, 0.35), ('brass', 0.38, 0.3),
                            ('perc', 0.36, 0.3), ('fx', 0.15, 0.3)):
        M.bus(name, gain=gain, reverb=rev)
    hold = hold_factory(M, SR)
    oboe = M.sampler('Woodwinds/Oboe/Vib/*.wav', tune=-12)
    bsn = M.sampler('Woodwinds/Bassoon/sus/*.wav', tune=-12)
    tbn = M.sampler('Brass/Tenor Trombone/sus/*.wav', tune=-12)
    tuba = M.sampler('Brass/Tuba/sus/*.wav', tune=-12)
    horn = M.sampler('Brass/F Horn/sus/*.wav', tune=-12)
    cb = M.sampler('Strings/Solo Contrabass/SusNV/*.wav', tune=-12)
    vc = M.sampler('Strings/Cello Section/susvib/*.wav', tune=-12)
    ctrem = M.sampler('Strings/Cello Section/trem/*.wav', tune=-12)
    vtrem = M.sampler('Strings/Violin Section/Trem/*.wav', tune=-12)
    timp = M.hits('Percussion/Timpani/Timpani1_Hit*.wav')
    crash = M.hits('Percussion/cymbal-crash1_f*.wav')
    gong = M.hits('Percussion/gongHit_f*.wav')
    sf = pan_at(at(G, *SIEG_AT))
    hag = pan_at(at(G, *HAGEN_AT[:2]))
    for t, d, m, v, part, k in compose():
        if part == 'trem':
            hold('low', ctrem, m, t, t + d, v, sf, rise=1.0, fall=1.0, gain=0.5)
        elif part == 'plot':
            if d > 1.0:
                hold('winds', oboe, m - 12, t, t + d, v, hag, rise=0.3, fall=0.8, gain=0.8)
            else:
                M.add('winds', oboe.play(m - 12, v, dur=d * 1.05, release=0.25), t, 0.85, hag)
            M.add('winds', bsn.play(m - 24, v - 12, dur=d * 1.05, release=0.25), t, 0.6, hag)
        elif part == 'ravens':
            M.add('fx', whoosh(d, 900, 5000, 0.8, seed=int(t * 10)), t, 0.9, -0.6)
            M.add('fx', whoosh(d, 900, 5000, 0.8, seed=int(t * 10) + 1), t + 0.2, 0.9, 0.6)
            hold('strings', vtrem, m - 24, t, t + d, v - 20, 0.0, rise=0.1, fall=0.6, gain=0.4)
        elif part == 'hagen':
            hold('low', tuba, m, t, t + d, v, hag, rise=0.05, fall=1.0, gain=1.0)
            M.add('brass', tbn.play(m + 12, v - 6, dur=d, release=0.4), t, 0.8, hag)
        elif part == 'blow':
            M.add('perc', gong.play(v), t, 0.9, sf)
            M.add('perc', crash.play(v), t, 0.8, sf)
            M.add('perc', timp.play(v, pitch=-7), t, 1.0, sf)
            M.add('fx', whoosh(0.5, 4000, 300, 0.9, seed=3), t - 0.15, 1.0, sf)
        elif part == 'curse':
            if d > 1.0:
                hold('brass', tbn, m, t, t + d, v, sf, rise=0.1, fall=0.8, gain=0.85)
            else:
                M.add('brass', tbn.play(m, v, dur=d * 1.05, release=0.3), t, 0.9, sf)
            M.add('low', tuba.play(m - 12, v - 12, dur=d * 1.05, release=0.3), t, 0.6, sf)
        elif part == 'sink':
            M.add('strings', vc.play(m, v, dur=0.7, release=0.3), t, 0.8, sf)
            M.add('perc', timp.play(v - 30, pitch=-4), t, 0.3, sf)
        elif part == 'fate':
            if m >= note('Ab3'):
                hold('brass', horn, m - 12, t, t + d, v, sf, rise=0.4, fall=1.0, gain=0.75)
            else:
                hold('low', tuba, m - 12, t, t + d, v, sf, rise=0.4, fall=1.0, gain=0.7)
        elif part == 'down':
            if d > 1.0:
                hold('brass', tbn, m, t, t + d, v, 0.0, rise=0.2, fall=1.0, gain=0.8)
            else:
                M.add('brass', tbn.play(m, v, dur=d * 1.05, release=0.3), t, 0.85, 0.0)
        elif part == 'dusk':
            hold('low', cb if m < note('C3') else vc, m, t, t + d, v, sf * 0.5, rise=4.0, fall=1.5, gain=0.5)
        elif part == 'heart':
            M.add('perc', timp.play(max(30, v - 20), pitch=-9), t, 0.6, sf)
            M.add('perc', timp.play(max(20, v - 34), pitch=-9), t + 0.22, 0.45, sf)
