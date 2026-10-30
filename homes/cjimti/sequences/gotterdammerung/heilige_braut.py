"""Heilige Braut: the valley at dusk as GD24 left it, Siegfried dying in the middle of Porch Front with the vassals'
torches drawn in round him, Gunther beside him. His heartbeat is still going, faint. Then the harp begins, and the
music of Brünnhilde's awakening comes back to him: rising chords, E minor into C major, the harp running up through
each one. Every chord blooms a wave out of him over the whole house, silver white in front and gold behind, and
with each one the vision holds a little more of the house, until every run shimmers silver with gold glinting all
through it and his emerald burns bright again. "Brünnhilde! Heilige Braut!"

The magic sleep (Donington 16) shimmers in the winds, violet-silver ripples over the vision, and his love (89)
sings out on the horn, every long note an emerald surge running through the silver to both ends. On its last note
he dies: one white flash over the whole house, his emerald goes out, and the vision falls back into him from both
ends like a tide running out. The power of fate (84) sounds twice on the brass, indigo rolling over the house, the
vassals' torches gather close round the body and lift, and the night comes down.

compose() holds every note; stage(), scene(), water(), figure(), torches(), sparks() and ring() are the valley,
shared word for word by Act III's scenes (GD22 to GD30) on a clock that runs on from scene to scene: T = t + 80 K."""
import numpy as np
from pixelhome.audio import note
from pixelhome.fx import DT, hexc, light, smoothstep, nframes, keys, Flicker, smooth_noise, colormap
from pixelhome.leitmotifs import play

CODE = 'GD25'
TITLE = 'Heilige Braut'
KIND = 'show'
DESCRIPTION = ('Dying, Siegfried remembers the morning he woke Brünnhilde, and the whole house fills with her '
               'silver and gold. He greets her one last time, and dies.')
VOICEOVER = ('At the very end, his memory comes back. With his last breath, Siegfried greets Brünnhilde.')

K = 3                                       # this scene's place on Act III's shared clock: T = t + 80 K
T_HARP = 4.0                                # the harp begins
CHORDS = [(6.0, ('E2', 'E3', 'G3', 'B3', 'E4')), (11.0, ('C2', 'C3', 'E3', 'G3', 'C4')),
          (16.0, ('A1', 'A2', 'E3', 'A3', 'C4')), (21.0, ('E2', 'E3', 'Ab3', 'B3', 'E4')),
          (26.0, ('C2', 'G2', 'E3', 'G3', 'C4', 'E4'))]
T_SLEEP = 31.0                              # the magic sleep, shimmering
T_LOVE = 41.0                               # his love, on the horn
T_DEATH = 57.0                              # he dies
T_FATE = [62.0, 70.0]
D = 80.0

SIEGFRIED = hexc('#00ff40')
HEAD = hexc('#e8ffe8')
GOLD = hexc('#ffaa00')
SILVER = hexc('#f4f8ff')
GLINT = hexc('#ffd060')
VIOLET = hexc('#a090ff')
GUNTHER = hexc('#ffb020')
BLOOD = hexc('#d00010')
FATE_C = hexc('#5a30ff')

START = dict(river=0.55, forest=0.4, sun=0.0, night=0.25, pyre=0.0, blaze=0.0, valhalla=0.0, flood=0.0)
END = dict(river=0.4, forest=0.25, sun=0.0, night=0.45, pyre=0.0, blaze=0.0, valhalla=0.0, flood=0.0)
SIEG_AT = ('Porch Front', 0.65)             # 0.45 * (0.8 + 0.2 sin(2 pi (t + 80) / 0.7)) at the start; the body 0.3 at the end
GUNTHER_AT = ('Porch Front', 0.3, 0.6)      # 0.6 at the start, 0.55 at the end
TORCHES = (0.45, 0.6, 0.3, 0.6)             # torch level at the start and end, how far drawn in to him at the start, end
BODY = 0.3                                  # the body's level at the end (no head; the gold glint 0.4)

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

    for j, tb in enumerate(heart()):
        add(tb, 0.3, 'E1', 60 - 4 * j, 'heart')
    add(0.0, T_HARP + 2, 'E2', 58, 'dusk')
    for k, (t0, chord) in enumerate(CHORDS):
        for m in chord:
            add(t0, 5.2, m, 74 + 5 * k, 'chord', k)
        for j in range(12):                 # the harp running up through the chord and back
            m = note(chord[1 + j % (len(chord) - 1)]) + 12 * (j // (len(chord) - 1))
            add(t0 - 1.2 + 0.1 * j, 0.6, min(m, note('E6')), 70 + 2 * j, 'harp', k)
    for t, m, v, d in play('sleep', T_SLEEP, 0.9, -4, 82):
        add(t, d, m, v, 'sleep')
    for t, m, v, d in play('siegfried_love', T_LOVE, 0.95, -12, 100):
        add(t, d, m, v, 'love')
    for m in ('E2', 'B2', 'E3', 'Ab3', 'B3'):
        add(T_LOVE, T_DEATH - T_LOVE, m, 64, 'bed')
    add(T_DEATH, 0.1, 'C1', 124, 'death')
    for j, t0 in enumerate(T_FATE):
        for t, m, v, d in play('fate', t0, 0.8, 0, 96 - 8 * j):
            add(t, d, m, v, 'fate', j)
    for m in ('E1', 'E2', 'B2'):
        add(T_DEATH + 2, D - T_DEATH - 2, m, 56, 'night')
    return sorted(N, key=lambda e: e[0])


def heart():
    """The last of his heartbeat, going on from GD24 until the harp takes over."""
    return [0.9, 3.4]


def levels(t):
    """Siegfried's level, his head's, and how much of the vision holds the house, at time t."""
    flick = 0.8 + 0.2 * np.sin(2 * np.pi * (t + 80) / 0.7)
    dying = 0.45 * flick
    rise = smoothstep(CHORDS[0][0] - 1, CHORDS[-1][0] + 2, t)
    bright = 0.85 + 0.1 * smoothstep(T_LOVE, T_DEATH - 1, t)
    alive = dying + (bright - dying) * rise
    gone = smoothstep(T_DEATH, T_DEATH + 2.0, t)
    lvl = alive * (1 - gone) + BODY * gone
    head = 0.8 * alive * (1 - gone)
    vision = smoothstep(CHORDS[0][0], CHORDS[-1][0] + 4, t) * (1 - smoothstep(T_DEATH, T_DEATH + 3.5, t))
    return lvl, head, vision


def render(G, seed=25):
    F = nframes(D)
    out = np.zeros((F, G.N, 3))
    S = stage(G)
    d, L = S['d'], S['L']
    N = compose()
    p_sf = at(G, *SIEG_AT)
    p_gu = at(G, *GUNTHER_AT[:2])
    reach = max(p_sf, L - p_sf)
    rng = np.random.default_rng(seed)
    harp = [e for e in N if e[4] == 'harp']
    glint_at = rng.uniform(0, L, len(harp))
    sleep = sorted({e[0] for e in N if e[4] == 'sleep'})
    love = [e for e in N if e[4] == 'love']
    fate = [e for e in N if e[4] == 'fate' and e[2] >= note('Ab3')]

    for f in range(F):
        t = f * DT
        T = t + 80 * K
        night = smoothstep(T_DEATH, D - 4, t)
        lv = {k: START[k] + (END[k] - START[k]) * night for k in START}
        ls, lh, vis = levels(t)
        dim = 1 - 0.55 * vis
        fr = scene(S, T, {k: v * dim for k, v in lv.items()})

        # the vision: silver over the house, held a little wider with every chord, gold glinting all through it
        if vis > 0:
            dist = np.abs(d - p_sf) / reach
            held = smoothstep(vis + 0.08, vis - 0.08, dist)
            shim = 0.55 + 0.45 * np.sin(2 * np.pi * (d / 260 - 0.9 * t)) * np.sin(2 * np.pi * (d / 90 + 1.4 * t))
            fr += light(SILVER, 0.7 * held * shim * min(1.0, 1.4 * vis))
            # gold bands sweeping end to end through it, turning each bar
            for j in range(2):
                u = ((t + 1.6 * j) / 3.2) % 2
                u = u if u < 1 else 2 - u
                fr += light(GLINT, 0.95 * held * np.exp(-((d - u * L) / 90) ** 2) * min(1.0, 2 * vis))
            fr += light(GLINT, 0.9 * held * np.clip(S['sparkle'](T) - 0.9, 0, None) * min(1.0, 1.4 * vis))
        for k, (t0, chord) in enumerate(CHORDS):
            fr = ring(fr, S, t, t0, p_sf, SILVER, 1.0, speed=900, width=150, tau=1.6)
            fr = ring(fr, S, t, t0 + 0.25, p_sf, GLINT, 0.9, speed=800, width=220, tau=1.8)
            a = t - t0
            if 0 <= a < 0.6:
                fr += light(WHITE, 0.45 * np.exp(-a / 0.12) * np.exp(-((d - p_sf) / 200) ** 2))
        for j, (t0, dur, m, v, _, k) in enumerate(harp):
            a = t - t0
            if 0 <= a < 1.2:
                fr += light(GLINT, 0.95 * np.exp(-a / 0.3) * np.exp(-((d - glint_at[j]) / 12) ** 2))

        # the magic sleep: violet-silver ripples over the vision
        for t0 in sleep:
            fr = ring(fr, S, t, t0, p_sf, VIOLET, 1.0, speed=700, width=200, tau=1.4)

        # his love on the horn: every long note an emerald surge through the silver to both ends
        for t0, dur, m, v, _, k in love:
            if dur >= 0.6:
                fr = ring(fr, S, t, t0, p_sf, SIEGFRIED, 1.0, speed=1300, width=260, tau=1.4)
                fr = ring(fr, S, t, t0 + 0.12, p_sf, HEAD, 0.7, speed=1300, width=60, tau=1.0)

        # his death: one white flash, the vision falls back into him from both ends like a tide going out
        a = t - T_DEATH
        if 0 <= a < 0.6:
            fr += light(WHITE, 0.9 * np.exp(-a / 0.12))
        if 0 <= a < 3.5:
            r = reach * (1 - a / 3.5)
            fr += light(SILVER, 0.9 * np.exp(-((np.abs(d - p_sf) - r) / 70) ** 2) * (1 - a / 3.5))
            fr += light(SIEGFRIED, 0.6 * np.exp(-a / 0.7) * np.exp(-((d - p_sf) / 120) ** 2))
        for j, tb in enumerate(heart()):
            fr = ring(fr, S, t, tb, p_sf, BLOOD, 0.55 - 0.15 * j, speed=800, width=140, tau=0.7)

        # fate, twice
        for t0, dur, m, v, _, k in fate:
            fr = ring(fr, S, t, t0, p_sf, FATE_C, 0.95, speed=850, width=240, tau=1.5)

        # the torches gather close round the body and lift
        g = smoothstep(T_DEATH + 1, T_DEATH + 12, t)
        tl = TORCHES[0] + (TORCHES[1] - TORCHES[0]) * g
        fr = torches(fr, S, T, tl, pull=p_sf, k=TORCHES[2] + (TORCHES[3] - TORCHES[2]) * g)

        # the people
        fr = figure(fr, S, p_gu, GUNTHER, GUNTHER_AT[2] - 0.05 * night)
        fr = figure(fr, S, p_sf, SIEGFRIED, ls, w=12 + 4 * smoothstep(CHORDS[0][0], CHORDS[-1][0], t)
                    * (1 - smoothstep(T_DEATH, T_DEATH + 2, t)))
        fr += light(HEAD, lh * np.exp(-((d - p_sf) / 6) ** 2))
        fr += light(GOLD, (0.6 - 0.2 * smoothstep(T_DEATH, T_DEATH + 3, t)) * np.exp(-((d - p_sf - 14) / 5) ** 2))
        out[f] = fr
    return np.clip(out, 0, 1)


def score(M, G):
    from pixelhome.audio import SR
    pan_at = panner(G)
    for name, gain, rev in (('low', 0.3, 0.25), ('strings', 0.27, 0.38), ('winds', 0.27, 0.4), ('brass', 0.3, 0.32),
                            ('harp', 0.27, 0.45), ('perc', 0.29, 0.3)):
        M.bus(name, gain=gain, reverb=rev)
    hold = hold_factory(M, SR)
    harp = M.sampler('Strings/Harp/*.wav')
    horn = M.sampler('Brass/F Horn/sus/*.wav', tune=-12)
    tbn = M.sampler('Brass/Tenor Trombone/sus/*.wav', tune=-12)
    tuba = M.sampler('Brass/Tuba/sus/*.wav', tune=-12)
    vln = M.sampler('Strings/Violin Section/susVib/*.wav', tune=-12)
    vc = M.sampler('Strings/Cello Section/susvib/*.wav', tune=-12)
    cb = M.sampler('Strings/Solo Contrabass/SusNV/*.wav', tune=-12)
    flute = M.sampler('Woodwinds/Flute/susvib/*.wav', tune=-12)
    clar = M.sampler('Woodwinds/Clarinet/susLong/*.wav', tune=-12)
    timp = M.hits('Percussion/Timpani/Timpani1_Hit*.wav')
    gong = M.hits('Percussion/gongHit_f*.wav')
    crash = M.hits('Percussion/cymbal-crash1_f*.wav')
    sf = pan_at(at(G, *SIEG_AT))
    for t, d, m, v, part, k in compose():
        if part == 'heart':
            M.add('perc', timp.play(v, pitch=-9), t, 0.5, sf)
            M.add('perc', timp.play(v - 14, pitch=-9), t + 0.22, 0.4, sf)
        elif part == 'dusk':
            hold('low', cb, m, t, t + d, v, sf * 0.5, rise=0.5, fall=2.0, gain=0.5)
        elif part == 'chord':
            if m < note('C3'):
                hold('low', tuba if m < note('C2') + 1 else tbn, m, t, t + d, v, 0.0, rise=0.3, fall=1.5, gain=0.6)
            elif m < note('C4'):
                hold('brass', horn, m, t, t + d, v, sf, rise=0.25, fall=1.5, gain=0.6)
            else:
                hold('strings', vln, m, t, t + d, v, sf, rise=0.4, fall=1.5, gain=0.55)
        elif part == 'harp':
            M.add('harp', harp.play(m, v), t, 0.85, sf + 0.1 * ((t * 7) % 3 - 1))
        elif part == 'sleep':
            s = flute if m >= note('E4') else clar
            hold('winds', s, m - 12 if s is flute else m, t, t + d, v, sf, rise=0.3, fall=1.0, gain=0.6)
        elif part == 'love':
            if d >= 0.6:
                hold('brass', horn, m - 12, t, t + d, v, sf, rise=0.15, fall=0.8, gain=0.8)
            else:
                M.add('brass', horn.play(m - 12, v, dur=d * 1.05, release=0.25), t, 0.85, sf)
            M.add('strings', vln.play(m - 12, v - 16, dur=d * 1.1, release=0.3), t, 0.5, sf)
        elif part == 'bed':
            hold('strings', vc, m, t, t + d, v, sf * 0.5, rise=2.0, fall=1.5, gain=0.45)
        elif part == 'death':
            M.add('perc', gong.play(v), t, 0.9, sf)
            M.add('perc', crash.play(110), t, 0.6, sf)
            M.add('perc', timp.play(v, pitch=-7), t, 1.0, sf)
        elif part == 'fate':
            if m >= note('Ab3'):
                hold('brass', horn, m - 12, t, t + d, v, sf, rise=0.4, fall=1.0, gain=0.75)
            else:
                hold('low', tuba, m - 12, t, t + d, v, sf, rise=0.4, fall=1.0, gain=0.7)
        elif part == 'night':
            hold('low', cb if m < note('C2') else vc, m, t, t + d, v, sf * 0.4, rise=4.0, fall=1.5, gain=0.5)
