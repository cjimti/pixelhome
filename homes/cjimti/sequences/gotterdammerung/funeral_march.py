"""Siegfried's Funeral March: night in the valley, the body lying in the middle of Porch Front with the torches close
round it. The vassals lift him and the procession begins: a column of torches streams in from the free end of Right
and marches the whole length of the house, step by step, out past the end of the Side, and keeps coming.

The death rhythm hammers in C minor: each stroke a flash, then the house knocked almost black for a moment. The Sword
rises in C major, steel climbing in from both ends toward the body with white sweeps the length of the house, and
Siegfried's own motif breaks out fortissimo: the house blazes emerald and gold, each chord slamming a whole run
emerald, the death rhythm hammering through it. His horn call grows into a vast statement for the whole brass, gold
and emerald sweeping out to both ends up to the B flat climax, and at the top Brünnhilde's music floods every run
silver as the procession carries him on toward the hall.

The music is Wagner's own: the Funeral March, Act III, bars 928 to 929, 955 to 958 and 968 to 975 as Solti's 1958
Vienna Philharmonic recording takes them, from the Wagner Ring Dataset's piano reduction (pixelhome/ring.py): tuba,
basses and cellos for the death rhythm and the bass, horns and trombones for the march's tunes, trumpets with the
violins on top. Staged as in the theatre: timpani, bass drum and gong drive each stroke of the death rhythm home,
cymbals crash at the climaxes, a cymbal swell rises into the B flat peak.

compose() holds every note; stage(), scene(), water(), figure(), torches(), sparks() and ring() are the valley,
shared word for word by Act III's scenes (GD22 to GD30) on a clock that runs on from scene to scene: T = t + 80 K."""
import numpy as np
from pixelhome.audio import note
from pixelhome.fx import DT, hexc, light, smoothstep, nframes, Flicker, smooth_noise, colormap
from pixelhome.ring import Orchestra, accents, excerpt, tidy

CODE = 'GD26'
TITLE = "Siegfried's Funeral March"
KIND = 'show'
DESCRIPTION = ("The vassals carry Siegfried's body through the night by torchlight, to the real Funeral March: "
               'the death rhythm, the sword, the hero, his horn grown vast, and his bride.')
VOICEOVER = ('The vassals lift the hero onto their shields, and carry him home through the night.')

K = 4                                       # this scene's place on Act III's shared clock: T = t + 80 K
EX = excerpt(__file__)                      # Act III, bars 928-930, 955-959 and 968-976, Solti 1958
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


VOLSUNG = []
T_SWORD = SEG[1]                            # the Sword rising into C major
T_SIEG = when(957)                          # Siegfried's motif, fortissimo
T_STROKE2 = when(958)                       # the death rhythm hammers through it
T_HORN = SEG[2]                             # his horn call grown vast, up to the B flat climax
T_BRUNN = when(973)                         # Brünnhilde
T_FADE = when(975.5)
T_MARCH = (1.5, D - 6.0)                    # torches keep joining the column

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


def thin(ts, gap):
    out = []
    for t in sorted(ts):
        if not out or t - out[-1] >= gap:
            out.append(t)
    return out


def strokes():
    """Every stroke of the death rhythm, from the excerpt's loudest chords: (time, weight)."""
    ts = accents(EX['notes'], 0.0, SEG[1], vmin=100, n=2, space=0.25)
    ts += accents(EX['notes'], T_STROKE2, T_STROKE2 + 1.3, vmin=120, n=2, space=0.25)
    bars = {round(y, 2) for _, y in EX['bars']}
    return [(t, 1.0 if round(t, 2) in bars else 0.8) for t in ts]


def compose():
    """Every event for the lights, from the excerpt's notes: (time, seconds, midi, velocity, part, k). The death
    rhythm ('stroke'), the Sword's rise ('sword'), Siegfried's motif ('sieg'), the horn call's vast build ('horn')
    and Brünnhilde ('brunn')."""
    N = []
    notes = EX['notes']
    for t, w in strokes():
        N.append((t, 0.6, note('C2'), int(96 + 28 * w), 'stroke', w))
    for t in thin([n[0] for n in notes if T_SWORD <= n[0] < T_SIEG and n[4] == 0], 0.35):
        N.append((t, 0.5, note('C5'), 112, 'sword', None))
    sieg = accents(notes, T_SIEG, T_STROKE2, vmin=100, n=2, space=0.35)
    sieg += accents(notes, T_STROKE2 + 1.3, SEG[2], vmin=100, n=2, space=0.35)
    for t in sieg:
        N.append((t, 0.8, note('C4'), 120, 'sieg', None))
    for t in accents(notes, T_HORN, T_BRUNN, vmin=100, n=2, space=0.6):
        N.append((t, 0.8, note('Eb4'), 120, 'horn', None))
    for t in accents(notes, T_BRUNN, D, vmin=100, n=2, space=0.6):
        N.append((t, 0.8, note('F4'), 116, 'brunn', None))
    return sorted(N, key=lambda e: e[0])


def body(G, t):
    """Where the body is at time t: carried a little way along the porch at the end."""
    a, b = at(G, *BODY_AT[0]), at(G, *BODY_AT[1])
    return a + (b - a) * smoothstep(T_BRUNN, D - 1, t)


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
    vol, sm, sl, tw = [], [], [], []
    T_SIEGMUND = T_SIEGLINDE = T_TWINS = 1e6
    sw = [(e[0], e[2]) for e in N if e[4] == 'sword']
    sg = [(e[0], e[2]) for e in N if e[4] == 'sieg']
    hn = [(e[0], e[2]) for e in N if e[4] == 'horn']
    br = [(e[0], e[2]) for e in N if e[4] == 'brunn']
    p_gu = at(G, *GUNTHER_AT[:2])

    for f in range(F):
        t = f * DT
        T = t + 80 * K
        u = smoothstep(T_FADE, D, t)
        lv = {k: START[k] + (END[k] - START[k]) * u for k in START}
        base = 1 - 0.4 * smoothstep(1, 4, t) * (1 - smoothstep(T_FADE, D, t))
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

        # the Sword rising: steel climbing in from both ends toward the body
        g = smoothstep(T_SWORD, T_SIEG, t) * (1 - smoothstep(T_SIEG, T_SIEG + 0.6, t))
        if g > 0:
            reach_ = (1 - g) * max(pb, L - pb)
            fr += light(STEEL, 0.75 * g * smoothstep(reach_ - 60, reach_ + 60, np.abs(d - pb)) * (0.6 + 0.4 * np.sin(2 * np.pi * (d / 140 - 2 * t))))
        # Siegfried's motif in C major: the house blazes emerald and gold, pulsing
        g = (smoothstep(T_SIEG - 0.3, T_SIEG + 0.4, t) * (1 - smoothstep(T_STROKE2 - 0.1, T_STROKE2 + 0.1, t))
             + smoothstep(T_STROKE2 + 1.3, T_STROKE2 + 1.8, t) * (1 - smoothstep(SEG[2] - 0.5, SEG[2] + 0.5, t)))
        if g > 0:
            fr += light(SIEGFRIED, 0.6 * g * (0.65 + 0.35 * np.sin(2 * np.pi * (d / 300 - 0.8 * t))))
            fr += light(GLINT, 0.4 * g * np.clip(np.sin(2 * np.pi * (d / 180 + 1.1 * t)), 0, 1) ** 3)
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
        if 0 <= a < T_BRUNN - T_HORN:
            fr += light(GOLD, 0.7 * np.exp(-a / 6.0) * (0.7 + 0.3 * np.sin(2 * np.pi * (d / 250 - 1.2 * t))))

        # Brünnhilde: silver flooding every run at the top
        g = smoothstep(T_BRUNN, T_BRUNN + 2, t) * (1 - smoothstep(T_FADE, D, t))
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
        mid = smoothstep(2, 8, t) * (1 - smoothstep(T_FADE, D, t))
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
    """Wagner's notes from the piano reduction on the full orchestra, brass-heavy as the march is, with the death
    rhythm's strokes driven home by timpani, bass drum and gong, and cymbals at the climaxes."""
    pan_at = panner(G)
    o = Orchestra(M, level=1.75)
    sf = pan_at(at(G, *BODY_AT[0]))

    def role(t, d, m, v, h):
        if h == 1 and m < 45 and d >= 0.05 and v >= 100:    # the death rhythm and the bass: tuba, basses, timpani
            return [('tuba', 0, 0, 0.7), ('basses', 0 if m < 40 else -12, -4, 0.6), ('cellos', 12 if m < 36 else 0, -6, 0.5)]
        if h == 1 and d >= 0.3 and m >= 45:                 # the march's tunes in the middle: horns and trombones
            return [('horns', 0, 0, 0.85), ('trombones', 0, -4, 0.6)]
        if h == 0 and d >= 0.3 and m >= 60:                 # on top: trumpets with the violins
            return [('trumpets', 0, -4, 0.55), ('violins', 0, -8, 0.5)]
        return None

    o.tutti(tidy(EX['notes']), size=lambda t: 1.0, role=role, pan=lambda t, m: sf * 0.4)
    for t, w in strokes():                                  # the death rhythm, hammered
        o.hit('timpani', t, int(100 + 24 * w), pitch=-5, gain=0.7 * w, pan=sf)
        o.hit('bass drum', t, int(100 + 24 * w), gain=0.6 * w, pan=sf)
        if w >= 1.0:
            o.hit('gong', t + 0.02, 112, gain=0.5, pan=sf)
    o.hit('timpani roll', SEG[1], 110, pitch=-5, gain=0.5, pan=sf)
    o.hit('crash', T_SIEG, 124, gain=0.6, pan=sf)
    o.hit('cymbal swell', when(971) - 3.0, 110, gain=0.5, pan=sf)
    o.hit('crash', when(971), 127, gain=0.7, pan=sf)
    o.hit('gong', when(971), 116, gain=0.5, pan=sf)
    o.hit('crash', T_BRUNN, 116, gain=0.5, pan=sf)
    o.effects([(0.0, -20), (D, -20)])
