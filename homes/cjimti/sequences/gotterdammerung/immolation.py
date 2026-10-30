"""Brünnhilde's Immolation: night in the hall by the Rhine, the vassals' torches drawn in round the porch, Siegfried
lying dead in the middle of Porch Front, Brünnhilde standing over him, Gutrune collapsed out on Right.

The music is Wagner's own, Act III as Solti's 1958 Vienna Philharmonic recording takes it: bars 1236 to 1243
("Starke Scheite schichtet mir dort", her command for the pyre, rising to "hoch und hell lod're die Glut"), 1418 to
1425 (the orchestra's storm of rushing scales, "Fliegt heim, ihr Raben!" and "Raunt es eurem Herren") and 1442 to
1455 ("So werf' ich den Brand in Walhall's prangende Burg", the torch, and the fire leaping up). The notes come from
the Wagner Ring Dataset's piano reduction (pixelhome/ring.py), orchestrated on strings, brass and woodwinds, the
rushing scales on strings and woodwinds, the fire on violins, harp and piccolo over the brass. Brünnhilde's lines
are her own, from the Schott vocal score (archive.org gtterdmmerung00wagn_0, pp. 318, 329-331), played on trumpet
and oboe. On stage: a wooden thud as each log drops, the ravens' wings, a crash of gold when she takes the Ring, the
torch whistling through the air and the pyre going up with a roar that keeps burning under the music, the effects
held low under her singing.

"Starke Scheite schichtet mir dort": she orders the pyre, and the men build it on the music's beat. Every stroke of
the bass stacks another log on the porch, a white-hot bar that drops into place and glows orange, the stacks
climbing in from both ends of the porch toward him, each one sending an orange shock out over the house. Gutrune
fades away. "Hoch und hell lod're die Glut": every long note of her rising line a silver wave out from her to both
ends of the house, his emerald stirring faintly in answer. She draws the Ring from his hand: a ring of gold light
travels from him to her and the whole house flashes gold as the orchestra hurls itself into its scales.

"Fliegt heim, ihr Raben!" Two ravens tear away to the end of the Side in white wakes, and every chord under her
message is one whole run in gold-white over deep blue. "So werf' ich den Brand": she lifts the torch and on "Burg"
hurls it, a comet of fire arcing from her to the pyre, and the pyre goes up, flames rushing out across the porch, an
orange shock to both ends, tongues of fire leaping white-gold out of it on every stroke, and the fire surges gold on
the brass's long notes while she stands silver before it.

compose() holds every note; stage(), scene(), water(), figure(), torches(), sparks() and ring() are the valley,
shared word for word by Act III's scenes (GD22 to GD30) on a clock that runs on from scene to scene: T = t + 80 K."""
import numpy as np
from pixelhome.audio import note
from pixelhome.fx import DT, hexc, light, smoothstep, nframes, Flicker, smooth_noise, colormap
from pixelhome.ring import Orchestra, accents, excerpt, tidy

CODE = 'GD28'
TITLE = "Brünnhilde's Immolation"
KIND = 'show'
DESCRIPTION = ('Brünnhilde orders a great pyre built for Siegfried, takes the Ring from his hand and sends the '
               "ravens home to Valhalla. Then she hurls a torch, and the pyre goes up in flames.")
VOICEOVER = ('Brünnhilde orders the pyre built high. She takes the Ring, sends the ravens home to Valhalla, '
             'and throws the torch.')

K = 6                                       # this scene's place on Act III's shared clock: T = t + 80 K
EX = excerpt(__file__)                      # Act III, bars 1236-1243, 1418-1425 and 1442-1455, Solti 1958
D = EX['seconds']


def when(m):
    """Seconds into the excerpt at measure position m, in whichever spliced range holds it."""
    for s in EX['segments']:
        a, b = s['measures']
        if a <= m < b:
            bs = [(x, t) for x, t in EX['bars'] if a <= x <= b]
            return float(np.interp(m, [x for x, _ in bs], [t for _, t in bs]))
    return None


def _strokes():
    """Every stroke of the bass under her command, at least 0.6 s apart: a log each."""
    out = []
    for t, d, m, v, h in sorted(EX['notes']):
        if h == 1 and m < 48 and t < when(1243.9) and (not out or t - out[-1] >= 0.6):
            out.append(t)
    return out


LOGS = _strokes()                           # every stroke stacks a log on the pyre
T_SOAR = when(1241.5)                       # "Hoch und hell lod're die Glut"
T_RING = when(1418) - 1.5                   # she takes the Ring; the gold flash lands on the orchestra's plunge
T_RAVENS = when(1422.25)                    # "Fliegt heim, ihr Raben!"
T_THROW = when(1447.25)                     # she hurls the torch
T_IGNITE = when(1448)                       # on "Burg" the pyre goes up
LOGES = accents(EX['notes'], T_IGNITE + 0.4, D - 2.5, vmin=104, n=2, space=1.1)  # tongues of fire on every stroke
T_TRANS = T_IGNITE + 2.0                    # the brass's long notes
# her lines, from the vocal score: (bar, start, length in beats, note), 4/4
VOICE = [(1236, 2, 1.5, 'C5'), (1236, 3.5, 0.5, 'C5'),
         (1237, 0, 1, 'E5'), (1237, 1, 1, 'C5'), (1237, 2, 0.75, 'C5'), (1237, 2.75, 0.25, 'C5'), (1237, 3, 1, 'C5'),
         (1238, 0, 2, 'Db5'), (1238, 3, 1, 'Ab4'),
         (1239, 0, 1, 'Db5'), (1239, 1, 0.5, 'Db5'), (1239, 1.5, 0.5, 'Db5'), (1239, 2, 1.5, 'Db5'),
         (1239, 3.5, 0.5, 'Db5'), (1240, 0, 2, 'Eb5'),
         (1241, 2, 1.5, 'E5'), (1241, 3.5, 0.5, 'E5'),
         (1242, 0, 2, 'F5'), (1242, 2, 1, 'F5'), (1242, 3, 0.5, 'D#5'), (1242, 3.5, 0.5, 'C#5'), (1243, 0, 2.5, 'F#5'),
         (1422, 1, 1, 'E5'), (1422, 2, 1.5, 'A5'), (1422, 3.5, 0.5, 'C5'), (1423, 0, 1, 'Eb5'), (1423, 1, 0.5, 'Eb4'),
         (1424, 0, 1.5, 'Eb5'), (1424, 1.5, 0.5, 'Eb5'), (1424, 2, 1.5, 'E5'), (1424, 3.5, 0.5, 'E5'),
         (1425, 0, 1, 'F5'), (1425, 1, 0.5, 'F4'),
         (1443, 0, 3.5, 'E5'), (1444, 1, 2, 'F5'), (1444, 3, 0.5, 'F5'), (1444, 3.5, 0.5, 'F5'), (1445, 0, 2.5, 'Bb5'),
         (1446, 1.5, 0.5, 'Db5'), (1446, 2, 1, 'Gb5'), (1446, 3, 1, 'Eb5'),
         (1447, 1, 2, 'C5'), (1447, 3, 0.5, 'C5'), (1447, 3.5, 0.5, 'C5'), (1448, 0, 2, 'F4')]

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
    """Every note of the excerpt, tagged: (time, seconds, midi, velocity, part, hand). The right hand's long notes
    under her rising line are 'love', the orchestra's plunge into its scales 'flash', the left hand's long chords
    under her message 'valhalla', the right hand once the pyre burns 'loge', the left hand's long notes then 'trans';
    the rest is 'tutti'. Her lines are 'voice'."""
    N = []
    for t, d, m, v, h in EX['notes']:
        if T_SOAR - 0.3 <= t < when(1243.99) - 0.05 and h == 0 and d >= 0.4:
            part = 'love'
        elif when(1423) - 0.05 <= t < when(1425.99) and h == 1 and d >= 0.9:
            part = 'valhalla'
        elif t >= T_IGNITE - 0.05 and h == 0:
            part = 'loge'
        elif t >= T_IGNITE + 1.5 and h == 1 and d >= 0.45:
            part = 'trans'
        else:
            part = 'tutti'
        N.append((t, d, m, v, part, h))
    for b, x, n, name in VOICE:
        t0 = when(b + x / 4)
        N.append((t0, when(b + (x + n) / 4) - t0, note(name), 100 if b < 1400 else 112, 'voice', b))
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
    love = sorted({e[0]: e for e in N if e[4] == 'love'}.values())
    valh = sorted({e[0] for e in N if e[4] == 'valhalla'})
    lstart = [t0 for t0 in LOGES if t0 <= D - 2]
    trans = sorted({e[0]: e for e in N if e[4] == 'trans'}.values())
    land = stacks(G)
    scales = [(e[0], e[2]) for e in N if e[4] == 'tutti' and e[5] == 0 and when(1418) <= e[0] < T_RAVENS - 0.3]
    brand = sorted({e[0] for e in N if e[4] == 'voice' and e[5] >= 1443})
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

        # the orchestra's rushing scales: a spark for every note, riding up and down the house with the pitch
        for t0, m in scales:
            a = t - t0
            if 0 <= a < 0.5:
                p = (m - 40) / 50 * L
                fr += light(TONGUE, 0.95 * np.exp(-a / 0.15) * np.exp(-((d - p) / 45) ** 2))
                fr += light(GOLD, 0.35 * np.exp(-a / 0.25) * np.exp(-((d - p) / 160) ** 2))

        # "So werf' ich den Brand": the torch in her hand, flaring on every word
        if when(1443) <= t < T_THROW + 0.2:
            g = smoothstep(when(1443), when(1443) + 1.0, t)
            fr += light(AMBER, 0.9 * g * np.exp(-((d - p_br - 12) / 8) ** 2))
            fr += light(ORANGE, 0.35 * g * np.exp(-((d - p_br - 12) / 80) ** 2) * (0.8 + 0.2 * S['fl'](T)))
        for t0 in brand:
            fr = ring(fr, S, t, t0, p_br + 12, ORANGE, 0.8, speed=1000, width=130, tau=0.8)

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
    """Wagner's notes orchestrated from the piano reduction, her lines on trumpet and oboe, and the stage's sounds."""
    pan_at = panner(G)
    pf = pan_at(at(G, 'Porch Front', 0.5))
    br = pan_at(at(G, *BRUN_AT[:2]))
    stk = [pan_at(p) for p in stacks(G)]
    o = Orchestra(M, level=1.7)
    N = compose()
    parts = {(round(t, 4), m, k): part for t, d, m, v, part, k in N}

    def size(t):
        return 0.55 if t < when(1241) else 1.0

    def role(t, d, m, v, h):
        part = parts.get((round(t, 4), m, h))
        if part == 'valhalla':                              # the chords under her message: horns and tubas
            return [('horns', 0, 4, 0.75), ('tuba', -12, -6, 0.5), ('trombones', 0, -8, 0.4)]
        if part == 'loge' and d < 0.3:                      # Loge's fire: violins, harp, piccolo glitter
            return [('violins', 0, -4, 0.5), ('harp', -12 if m > 84 else 0, -6, 0.4)] + \
                ([('piccolo', 0, -12, 0.3)] if m >= 79 else [])
        if part == 'trans':                                 # the brass's long notes over the fire
            return [('trumpets', 0, 0, 0.6), ('trombones', -12, -4, 0.55), ('horns', 0, -6, 0.5)]
        return None
    o.tutti(tidy([(t, d, m, v, k) for t, d, m, v, part, k in N if part != 'voice']), size=size, role=role)
    for t, d, m, v, part, k in N:                           # her lines
        if part == 'voice':
            o.play('trumpets', m, t, max(d, 0.15), v, br, 0.62 if k < 1400 else 0.8)
            o.play('oboes', m, t, max(d, 0.15), v - 4, br, 0.5)

    # the stage
    for j, t0 in enumerate(LOGS):                           # each log drops onto the pyre
        o.hit('hoof', t0, 96, gain=0.5, pan=stk[j])
        o.hit('bass drum', t0, 90, gain=0.25, pan=stk[j])
    o.hit('crash', T_RING + 1.5, 118, gain=0.55, pan=br)    # the Ring: the whole house flashes gold
    o.play('glock', note('F#6'), T_RING + 1.5, 0.1, 100, br, 0.35)
    from pixelhome.audio import whoosh
    for k, (tt, seed) in enumerate(((T_RAVENS, 28), (T_RAVENS + 0.3, 29))):   # the ravens' wings
        M.add('fx', whoosh(2.6, 900, 5000, 0.7, seed=seed), tt, 0.6, br - 0.4 * (k + 1))
    M.add('fx', whoosh(T_IGNITE - T_THROW + 0.2, 600, 4500, 0.9, seed=31), T_THROW, 0.9, br)   # the torch
    o.boom(T_IGNITE, pf, 1.0)                               # the pyre goes up
    o.hit('crash', T_IGNITE, 124, gain=0.6, pan=pf)
    M.add('fx', whoosh(2.5, 300, 6000, 0.9, seed=33), T_IGNITE - 0.1, 0.9, pf)
    o.fire(T_IGNITE - 0.2, D, lambda tt: 0.45 + 0.55 * smoothstep(T_IGNITE, T_IGNITE + 3, tt), pan=pf,
           crackle=22, seed=28)
    for j, t0 in enumerate(LOGES):                          # each tongue of fire leaping out
        M.add('fx', whoosh(1.0, 400, 3000, 0.5, seed=40 + j), t0, 0.5, pf + (0.5 if j % 2 == 0 else -0.5))
    o.effects([(0.0, -10.0), (when(1243.9), -10.0), (when(1243.99) + 0.1, 0.0), (T_RAVENS - 0.3, -2.0),
               (T_RAVENS + 2.0, -8.0), (T_THROW - 0.2, -8.0), (T_THROW, 0.0), (T_IGNITE + 4, 0.0),
               (T_IGNITE + 7, -6.0)])
