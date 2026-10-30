"""The Dead Hand: night, the hall on the Rhine, the procession arrived. The body lies in the middle of Porch Front
with the torches close round it and Gunther beside it. Gutrune has been waiting up, a rose light at Right.

The music is Wagner's own, Act III as Solti's 1958 Vienna Philharmonic recording takes it: bars 1033 to 1047
(Hagen's "Hoiho! Hoiho! Wacht auf!" and his summons to bring light), 1058 to 1063 (Gutrune's "Was bringen die?"
and the orchestra's blow as the body is borne in) and 1148 to 1165 (the brothers' fight for the Ring, "Her den
Ring!", the dead man's hand rising on the great chord and the Sword motif, and Brünnhilde's solemn approach). The
notes come from the Wagner Ring Dataset's piano reduction (pixelhome/ring.py), orchestrated on full strings,
brass and woodwinds, the Sword on trumpets, Brünnhilde's coming on high woodwinds and violins. Hagen's calls are
his own line from the Schott vocal score (archive.org gtterdmmerung00wagn_0, pp. 307-308), on trombones and a
horn. On stage: the torches crackling up when he calls for light, a blow when he knocks the house dark, steel on
every stroke of the fight, Gunther's fall, and the whole house gasping when the hand rises, a thunderclap and a
rushing wind as Hagen is hurled back; then the effects fall away for Brünnhilde.

Hagen bursts in from the free end of Right, "Hoiho!", a violet comet, each call a violet blast out of the dark,
and the torches flare up at his "Lichte!". On the blow of bar 1058 his falling darkness knocks the house dark;
Gutrune sees the body on the orchestra's great blow and screams: a flash of rose over the whole house, and her light
collapses where she stands.

Hagen claims the Ring: gold rings out of the body, and Gunther stands between them. They fight across the porch,
gold against violet, every clash of the orchestra lighting the house in turn and spraying sparks; then Hagen's blow,
the house drowned in violet and black, and Gunther's gold shatters into sparks and goes out. "Her den Ring!" Hagen
reaches for it, and on the great chord the dead hand rises: a terrible emerald-white flare out of the body over
every run, the Sword blazing steel along the roof on each of its notes, and Hagen is thrown back along Right and
out into the dark.

Brünnhilde comes on the high, hushed chords: a silver sweep in from the free end of Right the whole length of the
house to the end of the porch, silver laid behind her, solemn silver waves rolling over the hall, and the first glow
of the pyre comes up on the porch.

compose() holds every note; stage(), scene(), water(), figure(), torches(), sparks() and ring() are the valley,
shared word for word by Act III's scenes (GD22 to GD30) on a clock that runs on from scene to scene: T = t + 80 K."""
import numpy as np
from pixelhome.audio import note
from pixelhome.fx import DT, hexc, light, smoothstep, nframes, keys, Flicker, smooth_noise, colormap
from pixelhome.ring import Orchestra, accents, excerpt, tidy

CODE = 'GD27'
TITLE = 'The Dead Hand'
KIND = 'show'
DESCRIPTION = ("Siegfried's body is brought home. Hagen kills Gunther for the Ring, but when he reaches for it the "
               "dead man's hand rises against him. Then Brünnhilde arrives.")
VOICEOVER = ('They bring the hero home. Hagen kills for the Ring, but the dead hand will not let it go.')

K = 5                                       # this scene's place on Act III's shared clock: T = t + 80 K
EX = excerpt(__file__)                      # Act III, bars 1033-1047, 1058-1063 and 1148-1165, Solti 1958
D = EX['seconds']


def when(m):
    """Seconds into the excerpt at measure position m, in whichever spliced range holds it."""
    for s in EX['segments']:
        a, b = s['measures']
        if a <= m < b:
            bs = [(x, t) for x, t in EX['bars'] if a <= x <= b]
            return float(np.interp(m, [x for x, _ in bs], [t for _, t in bs]))
    return None


T_GUTRUNE = 0.0                             # Gutrune, waiting
HOIHOS = [when(b + 0.25) for b in (1033, 1034, 1041, 1042)]   # his calls
T_HOIHO = HOIHOS[0]                         # Hagen bursts in
BLASTS = HOIHOS + [when(1035.25), when(1036.25)]   # and "Wacht auf!"
T_LIGHT = when(1037.25)                     # "Lichte! Lichte, helle Brände!": the torches flare
T_HAGEN = when(1058)                        # his darkness
T_SCREAM = when(1060)                       # the orchestra's blow: she sees the body
T_RING = when(1149.4)                       # "Des Alben Erbe fordert so sein Sohn": the Ring, claimed
CLASHES = accents(EX['notes'], when(1151.9), 57.3, vmin=100, n=4, space=0.8)    # Gunther and Hagen fight
T_KILL = 57.6                               # Hagen's blow
T_REACH = (when(1156.5), 61.29)             # "Her den Ring!"
T_HAND = 61.29                              # the great chord: the dead hand rises
T_CURSE = T_HAND
T_THROWN = (T_HAND, T_HAND + 8.0)           # Hagen thrown back and out
T_BRUNN = (74.47, 80.5)                     # Brünnhilde sweeps in on the hushed chords
T_MOTIF = 82.0
T_ATONE = when(1165)                        # "Schweigt eures Jammers"
# Hagen's calls, from the vocal score: (bar, start, length in beats, note), 4/4
CALLS = [(b, x, n, nm) for b in (1033, 1034, 1041, 1042) for x, n, nm in ((1, 1, 'Db4'), (2, 2, 'C4'))] + \
        [(b, x, n, nm) for b in (1035, 1036) for x, n, nm in ((1, 1, 'C4'), (2, 2, 'C4'))]

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
    """Every note of the excerpt, tagged: (time, seconds, midi, velocity, part, hand). Gutrune's question is
    'gutrune', the right hand while Hagen claims the Ring 'ring', the low chord the hand rises on 'curse', the Sword's
    long notes 'sword', Brünnhilde's approach 'brunn' and her first words 'atone'; the rest is 'tutti'. Hagen's
    calls are 'hagen'."""
    N = []
    for t, d, m, v, h in EX['notes']:
        if when(1059) <= t < T_SCREAM - 0.05 and h == 0:
            part = 'gutrune'
        elif T_RING <= t < CLASHES[0] - 0.2 and h == 0:
            part = 'ring'
        elif T_HAND - 0.01 <= t < 63.9 and h == 1 and m >= note('C3'):
            part = 'curse'
        elif 63.9 <= t < 74.4 and h == 0 and d >= 0.4:
            part = 'sword'
        elif T_BRUNN[0] - 0.01 <= t < T_ATONE and h == 0:
            part = 'brunn'
        elif t >= T_ATONE:
            part = 'atone'
        else:
            part = 'tutti'
        N.append((t, d, m, v, part, h))
    for b, x, n, name in CALLS:
        t0 = when(b + x / 4)
        N.append((t0, when(b + (x + n) / 4) - t0, note(name), 118, 'hagen', b))
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
    brunn = sorted({e[0]: (e[0], e[2]) for e in N if e[4] == 'brunn' and e[1] >= 0.35}.values())
    atone = sorted({e[0] for e in N if e[4] == 'atone' and e[5] == 1})
    runs = ['Left', 'Right', 'Side', 'Porch Front', 'Porch Left', 'Porch Right']
    pulses = [a for a in accents(EX['notes'], HOIHOS[0] + 1, T_HAGEN, vmin=80, n=3, space=0.45)
              if min(abs(a - b) for b in BLASTS) > 0.6]

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
        dread = smoothstep(T_GUTRUNE, T_GUTRUNE + 1.5, t) * (1 - smoothstep(T_SCREAM - 0.5, T_SCREAM + 0.3, t))
        fr += light(GUTRUNE, 0.55 * dread * (G.seg_of == 'Right') * (0.5 + 0.5 * np.sin(2 * np.pi * t / 1.3)) ** 2)
        for t0 in BLASTS:                           # Hoiho! Wacht auf!: a violet blast out of the dark at each call
            fr = ring(fr, S, t, t0, L, HAGEN, 1.0, speed=1500, width=220, tau=1.0)
            fr = ring(fr, S, t, t0 + 0.1, L, TORCH, 0.8, speed=1300, width=80, tau=0.8)

        for t0 in pulses:                           # the orchestra's strokes as the men come in: violet from Hagen
            fr = ring(fr, S, t, t0, ph, HAGEN, 0.6, speed=1200, width=120, tau=0.6)
            fr = ring(fr, S, t, t0 + 0.08, ph, TORCH, 0.45, speed=900, width=60, tau=0.5)

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
        lit = 0.35 + 0.65 * smoothstep(T_LIGHT, T_LIGHT + 2.5, t)        # "Lichte!": the torches flare up
        fr = torches(fr, S, T, TORCHES[0] * lit * (1 - 0.4 * dark), pull=p_body,
                     k=TORCHES[1] * smoothstep(T_LIGHT, T_HAGEN, t))   # the men gather round him
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
    """Wagner's notes orchestrated from the piano reduction, Hagen's calls on trombones, and the stage's sounds."""
    pan_at = panner(G)
    body = pan_at(at(G, *BODY_AT[:2]))
    gut = pan_at(at(G, *GUTRUNE_AT[:2]))
    door = pan_at(float(G.pd.max()))
    o = Orchestra(M, level=2.0)
    N = compose()
    parts = {(round(t, 4), m, k): part for t, d, m, v, part, k in N}

    def size(t):
        return 0.4 if t >= T_BRUNN[0] else 0.75 if t < T_HAGEN else 1.0

    def role(t, d, m, v, h):
        part = parts.get((round(t, 4), m, h))
        if part == 'sword':                                 # the Sword, on trumpets over the horns
            return [('trumpets', 0, 8, 0.9), ('horns', -12, 0, 0.6)]
        if part == 'curse':                                 # the great chord the hand rises on
            return [('trombones', 0, 4, 0.8), ('tuba', -12, 0, 0.6), ('cellos trem', 0, 0, 0.5)]
        if part in ('brunn', 'atone') and h == 0:           # Brünnhilde's coming: high woodwinds, hushed violins
            return [('flutes', -12 if m > 88 else 0, 4, 0.5), ('clarinets', -12, -4, 0.4), ('violins', -12, -8, 0.4)]
        if part == 'gutrune':
            return [('oboes', 0, 4, 0.6), ('violins', 0, -8, 0.4)]
        return None

    def pan(t, m):
        return body if t >= T_HAGEN else door * 0.5
    o.tutti(tidy([(t, d, m, v, k) for t, d, m, v, part, k in N if part != 'hagen']), size=size, role=role, pan=pan)
    for t, d, m, v, part, k in N:                           # Hagen's calls
        if part == 'hagen':
            p = pan_at(where(G, t)[1][0])
            o.play('trombones', m, t, d, v, p, 0.95)
            o.play('horns', m, t, d, v - 12, p, 0.45)

    # the stage
    o.fire(T_LIGHT - 0.3, T_BRUNN[1], lambda tt: 0.25 + 0.2 * (tt < T_HAND), pan=body, crackle=10, seed=27)
    o.boom(T_HAGEN, body, 0.7)                              # his darkness falls on the house
    o.hit('crash', T_SCREAM, 118, gain=0.5, pan=gut)        # she sees the body
    o.hit('scrape', T_SCREAM + 0.1, 110, gain=0.5, pan=gut)
    for j, t0 in enumerate(CLASHES):                        # the fight
        o.clash(t0, body + (0.15 if j % 2 else -0.15), 112 + 2 * j, 0.9)
    o.boom(T_KILL, body, 0.9)                               # Gunther falls
    o.hit('cymbal swell', T_HAND - 3.0, 100, gain=0.4, pan=body)
    o.thunder(T_HAND, near=1.0, pan=body, gain=1.0)         # the hand rises: the whole house gasps
    o.hit('gong', T_HAND + 0.02, 124, gain=0.6, pan=body)
    o.wind(T_HAND, T_THROWN[1], lambda tt: np.exp(-(tt - T_HAND) / 3.0), pan=lambda tt: body + (door - body)
           * smoothstep(T_HAND, T_THROWN[1], tt), seed=29)  # Hagen hurled back and out
    o.effects([(0.0, -6.0), (T_HAGEN - 1, -6.0), (T_HAGEN, 0.0), (T_HAND + 6, 0.0), (T_BRUNN[0], -12.0),
               (T_ATONE, -20.0)])
