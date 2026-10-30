"""Valhalla Burns: the pyre roaring on the porch as GD28 left it, its light thrown out over the valley, the
torches drawn in round it, Brünnhilde standing silver before the fire with the Ring on her hand.

The music is Wagner's own, Act III as Solti's 1958 Vienna Philharmonic recording takes it: bars 1456 to 1460
("Grane, mein Ross! Sei mir gegrüsst!") spliced to 1493 to 1513 ("Heiajaho! Grane! Grüss deinen Herren! Siegfried!
Siegfried! Sieh! Selig grüsst dich dein Weib", her leap into the fire, and the orchestra's blaze as the flames take
the hall and the Rhine begins to rise). The notes come from the Wagner Ring Dataset's piano reduction
(pixelhome/ring.py), orchestrated on full strings, brass and woodwinds, the fire on violins, harp and piccolo, the
great chords on horns and Wagner tubas, the last rising strokes on trombones and tubas. Brünnhilde's lines are her
own, from the Schott vocal score (archive.org gtterdmmerung00wagn_0, pp. 332, 335-336), played on trumpet and oboe.
On stage: Grane's hooves under her as she rides, held back under her singing, the leap a great blow and a roar as
the fire explodes out over the house, crackling and roaring through to the end, a crash on each of the castle's
chords, and thunder as Valhalla cracks on the last strokes.

"Grane, mein Ross!" she greets the horse, every word a silver ring out from her. "Heiajaho!" she mounts and
gallops away from the fire along Porch Left and Left, every hoofbeat a silver flash and a ring of silver, wheels
round on "Sieh!" and charges back, faster, and on "Weib" leaps into the middle of the pyre. A blinding white flash,
and the fire explodes out of the porch: flames race outward along both wings and down the Side until every run on
the house is burning, red at the roots and white-gold at the tips, the torches swallowed in it, a white-gold tongue
racing the length of the roofline on every stroke.

On the great chords the castle of the gods blazes gold-white on the porch inside the fire, every chord a gold-white
surge over the whole burning house with deep blue beneath. Then on the last rising strokes Valhalla burns and
breaks: every stroke a black crack through the gold and a shower of embers flying out to both ends, the gold sinking
as the gods go down in flames. The house is left burning from end to end with the ruin glowing in the middle.

compose() holds every note; stage(), scene(), water(), figure(), torches(), sparks() and ring() are the valley,
shared word for word by Act III's scenes (GD22 to GD30) on a clock that runs on from scene to scene: T = t + 80 K."""
import numpy as np
from pixelhome.audio import note
from pixelhome.fx import DT, hexc, light, smoothstep, nframes, Flicker, smooth_noise, colormap
from pixelhome.ring import Orchestra, accents, excerpt, tidy

CODE = 'GD29'
TITLE = 'Valhalla Burns'
KIND = 'show'
DESCRIPTION = ('Brünnhilde mounts her horse and rides straight into the fire. The flames take the whole house, '
               'and in the middle of them Valhalla, the castle of the gods, burns and falls.')
VOICEOVER = ('Brünnhilde rides into the flames. The fire climbs to the sky, and Valhalla, home of the gods, '
             'begins to burn.')

K = 7                                       # this scene's place on Act III's shared clock: T = t + 80 K
EX = excerpt(__file__)                      # Act III, bars 1456-1460 and 1493-1513, Solti 1958
D = EX['seconds']


def when(m):
    """Seconds into the excerpt at measure position m, in whichever spliced range holds it."""
    for s in EX['segments']:
        a, b = s['measures']
        if a <= m < b:
            bs = [(x, t) for x, t in EX['bars'] if a <= x <= b]
            return float(np.interp(m, [x for x, _ in bs], [t for _, t in bs]))
    return None


T_RIDE = [when(1493)]                       # "Heiajaho! Grane!": she rides
T_TURN = when(1496)                         # "Sieh!": she wheels round at the end of Left
T_LEAP = when(1499)                         # on "Weib": into the fire
T_SPREAD = (T_LEAP, 47.0)                   # the flames race out over every run
LOGES = accents(EX['notes'], T_LEAP + 1.0, D - 2.0, vmin=104, n=1, space=1.2)    # a tongue on every stroke
T_VALHALLA = [40.02, 44.28]                 # the great chords, twice
T_DOWN = 69.42                              # the last rising strokes: Valhalla breaks
# her lines, from the vocal score: (bar, start, length, note, units to the bar)
VOICE = [(1457, 0, 1, 'F5', 4), (1457, 1, 1, 'A4', 4), (1457, 3.5, 0.5, 'A4', 4), (1458, 0, 4, 'F#5', 12),
         (1459, 7, 1, 'F5', 12), (1459, 8, 3, 'F5', 12), (1459, 11, 1, 'F5', 12), (1460, 0, 3, 'Bb5', 12),
         (1493, 0, 0.25, 'G#5', 4), (1493, 0.25, 0.5, 'E5', 4), (1493, 0.75, 0.25, 'G#4', 4), (1493, 1, 0.5, 'B4', 4),
         (1493, 2, 0.5, 'G5', 4), (1493, 2.5, 0.5, 'E4', 4),
         (1494, 0.5, 0.83, 'C5', 4), (1494, 1.33, 0.34, 'B4', 4), (1494, 1.67, 0.33, 'C5', 4), (1494, 2, 0.5, 'G5', 4),
         (1494, 2.5, 0.5, 'C5', 4),
         (1495, 0.5, 1, 'F5', 4), (1495, 1.5, 0.5, 'F4', 4), (1495, 2.5, 1, 'Ab5', 4), (1495, 3.5, 0.5, 'Ab4', 4),
         (1496, 2, 8.5, 'Eb5', 12),
         (1497, 1, 2, 'Ab5', 4), (1497, 3, 1, 'F5', 4), (1498, 1, 1.5, 'Gb5', 4), (1498, 2.5, 1, 'F5', 4),
         (1498, 3.5, 0.5, 'Eb5', 4), (1499, 0, 2, 'Db5', 4)]

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
    """Every note of the excerpt, tagged: (time, seconds, midi, velocity, part, k). The left hand's strokes while she
    rides are 'hoof' (k = the stroke), the great chords 'valhalla' (k = which time), the right hand once the fire
    takes the house 'loge', the last rising strokes 'down'; the rest is 'tutti'. Her lines are 'voice'."""
    N, last = [], -1.0
    for t, d, m, v, h in sorted(EX['notes']):
        if T_RIDE[0] <= t < T_LEAP and h == 1 and t - last >= 0.3:
            part, k, last = 'hoof', h, t
        elif T_VALHALLA[0] - 0.05 <= t < T_VALHALLA[1] - 0.05 and d >= 0.8:
            part, k = 'valhalla', 0
        elif T_VALHALLA[1] - 0.05 <= t < 50.0 and d >= 0.8:
            part, k = 'valhalla', 1
        elif t >= T_DOWN - 0.05 and h == 1 and d >= 0.95:
            part, k = 'down', h
        elif T_LEAP + 1.0 <= t and h == 0:
            part, k = 'loge', h
        else:
            part, k = 'tutti', h
        N.append((t, d, m, v, part, k))
    for b, x, n, name, per in VOICE:
        t0 = when(b + x / per)
        N.append((t0, when(b + (x + n) / per) - t0, note(name), 104 if b < 1495 else 114, 'voice', b))
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
    lstart = [t0 for t0 in LOGES if t0 <= D - 2]
    sung = sorted({e[0] for e in N if e[4] == 'voice'})
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

        # every word she sings a silver ring out from her
        for t0 in sung:
            if t0 < T_LEAP:
                fr = ring(fr, S, t, t0, gallop(G, t0)[0], SILVER, 0.75, speed=1000, width=110, tau=0.7)
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
    """Wagner's notes orchestrated from the piano reduction, her lines on trumpet and oboe, and the stage's sounds."""
    pan_at = panner(G)
    S = stage(G)
    pf = pan_at(S['pf'])
    o = Orchestra(M, level=1.15)
    N = compose()
    parts = {(round(t, 4), m, k): part for t, d, m, v, part, k in N}

    def role(t, d, m, v, h):
        part = parts.get((round(t, 4), m, h)) or parts.get((round(t, 4), m, 0))
        if part == 'valhalla':                              # the great chords: horns and Wagner tubas, full weight
            if m < 60:
                return [('horns', 0, 6, 0.8), ('tuba', -12, 0, 0.55), ('trombones', 0, 0, 0.5)]
            return [('trumpets', -12, 0, 0.6), ('horns', -12, 0, 0.55), ('violins', 0, 0, 0.55)]
        if part == 'down':                                  # the last rising strokes: trombones and tubas
            return [('trombones', 12 if m < 48 else 0, 6, 0.8), ('tuba', 0, 0, 0.6), ('basses', 0, 0, 0.5)]
        if part == 'loge' and d < 0.3:                      # the fire: violins, harp, piccolo
            return [('violins', 0, -4, 0.5), ('harp', -12 if m > 84 else 0, -6, 0.4)] + \
                ([('piccolo', 0, -12, 0.3)] if m >= 79 else [])
        return None
    o.tutti(tidy([(t, d, m, v, k) for t, d, m, v, part, k in N if part != 'voice']), role=role)
    for t, d, m, v, part, k in N:                           # her lines
        if part == 'voice':
            p = pan_at(gallop(G, t)[0])
            o.play('trumpets', m, t, max(d, 0.15), v, p, 0.65 if k < 1495 else 0.85)
            o.play('oboes', m, t, max(d, 0.15), v - 4, p, 0.5)

    # the stage
    hooves = [t for t, d, m, v, part, k in N if part == 'hoof']
    for j, t0 in enumerate(hooves):                         # Grane under her
        o.hoof(t0, pan=pan_at(gallop(G, t0)[0]), v=96 + min(30, j), gain=1.4)
        o.hit('hoof soft', t0 + 0.09, 90, gain=0.4, pan=pan_at(gallop(G, t0)[0]))
    o.fire(0.0, T_LEAP + 0.5, 0.35, pan=pf, crackle=10, seed=29)     # the pyre waiting
    o.hit('cymbal swell', T_LEAP - 3.0, 104, gain=0.45, pan=pf)
    o.boom(T_LEAP, pf, 1.0)                                 # the leap
    o.hit('crash', T_LEAP, 124, gain=0.7, pan=pf)
    o.thunder(T_LEAP + 0.05, near=0.9, pan=pf, gain=0.8)
    o.fire(T_LEAP - 0.1, D, lambda tt: 0.55 + 0.45 * smoothstep(T_LEAP, T_SPREAD[1], tt), pan=pf, crackle=30, seed=31)
    o.fire(T_LEAP + 2.0, D, lambda tt: 0.6 * smoothstep(T_LEAP + 2, T_SPREAD[1], tt), pan=-0.8, crackle=14, seed=33)
    o.fire(T_LEAP + 2.0, D, lambda tt: 0.6 * smoothstep(T_LEAP + 2, T_SPREAD[1], tt), pan=0.8, crackle=14, seed=35)
    for k in range(2):                                      # the castle's chords
        o.hit('crash', T_VALHALLA[k], 120, gain=0.55, pan=pf)
    downs = sorted({t for t, d, m, v, part, k in N if part == 'down'})
    for j, t0 in enumerate(downs):                          # Valhalla cracks
        if j % 2 == 0:
            o.thunder(t0, near=0.7 + 0.3 * (j == 0), pan=pf, gain=0.7)
        else:
            o.hit('scrape', t0, 110, gain=0.4, pan=pf)
    o.effects([(0.0, -8.0), (T_RIDE[0] - 0.5, -8.0), (T_RIDE[0], -10.0), (when(1497.2), -12.0),
               (T_LEAP - 3.0, -6.0), (T_LEAP, 0.0), (T_SPREAD[1], -2.0), (T_DOWN, 0.0)])
