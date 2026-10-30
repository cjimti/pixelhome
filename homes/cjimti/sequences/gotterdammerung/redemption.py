"""Redemption: the end of the Ring. The house is burning from end to end as GD29 left it, the ruin of Valhalla
glowing in the middle of the porch.

The music is Wagner's own, the last pages of the cycle as Solti's 1958 Vienna Philharmonic recording takes them:
Act III bars 1521 to 1524 (Hagen's last cry and the flood closing over him) spliced to bars 1590 to the end (the
crash of Valhalla's fall, the gods' castle sounding once more in the shimmering strings, the Twilight's last
blows, and love as redemption soaring in the violins to the final D flat major chord). The notes come from the
Wagner Ring Dataset's piano reduction (pixelhome/ring.py), orchestrated: the flood's chords on full strings and
brass, the strings' tremolo on tremolo strings over the basses' F sharp, the downfall on trombones and tubas,
redemption on the violins with the harp under it, and the last chord on the whole orchestra. Hagen's "Zurück vom
Ring!" is his own line, from the Schott vocal score (archive.org gtterdmmerung00wagn_0, p. 337), played on
trombones and a horn. The stage has its sounds where they help: the flood roaring in over the fire with steam
hissing where it meets the flames, a crash of water as Hagen goes under, Valhalla's two blows crashing and
splintering, and then nothing but the music, the effects ridden right down for redemption.

The river rises and overflows: on the flood's first chords a wall of water sweeps in from the free end of Right,
a white line of foam at its front, and runs the whole length of the house, putting the fire out until every run is
water, indigo, teal and green, streaming. On its front ride the three Rhinemaidens, Woglinde in silver, Wellgunde
in sea green, Flosshilde in violet. "Zurück vom Ring!" Hagen, ultraviolet in black, rises on Porch Left and lunges
at them; the maidens seize him and drag him under, the water closing over him in a burst of white foam. On the
crash of bar 1590 Flosshilde holds the Ring up: the whole house flashes gold, and the maidens stream round the
flooded house with the gold among them.

The flood draws back into its bed along Right while Valhalla sounds once more in the strings' shimmer, and the
castle glows gold-white on the porch one last time, then falls on the Twilight's blows, its gold sinking into a
red-violet ember. And then love as redemption, the melody Sieglinde sang in Die Walküre, soars in the violins:
each phrase blooms the house brighter, gold-white rising out of the porch and silver spreading over the wings,
until on the cycle's last D flat major chord the whole house glows, radiant and still, over the calm river.

compose() holds every note; stage(), scene(), water(), figure(), torches(), sparks() and ring() are the valley,
shared word for word by Act III's scenes (GD22 to GD30) on a clock that runs on from scene to scene: T = t + 80 K."""
import numpy as np
from pixelhome.audio import note
from pixelhome.fx import DT, hexc, light, smoothstep, nframes, Flicker, smooth_noise, colormap
from pixelhome.ring import Orchestra, excerpt, tidy

CODE = 'GD30'
TITLE = 'Redemption'
KIND = 'show'
DESCRIPTION = ('The Rhine overflows and puts out the fire. The Rhinemaidens take back the Ring, Hagen is dragged '
               'under, Valhalla falls, and the house blooms into a last radiant glow: the end of the Ring.')
VOICEOVER = ('The river rises and puts out the fire. The Ring goes home to the Rhine. '
             'And out of the ruins of the old world, love remains.')

K = 8                                       # this scene's place on Act III's shared clock: T = t + 80 K
EX = excerpt(__file__)                      # Act III, bars 1521-1524 and 1590 to the end, Solti 1958
D = EX['seconds']


def when(m):
    """Seconds into the excerpt at measure position m, in whichever spliced range holds it."""
    for s in EX['segments']:
        a, b = s['measures']
        if a <= m < b:
            bs = [(x, t) for x, t in EX['bars'] if a <= x <= b]
            return float(np.interp(m, [x for x, _ in bs], [t for _, t in bs]))
    return None


T_RHINE = [0.0, 0.89, 2.38, 2.98, 3.58]     # the flood's chords
T_FLOOD = (0.0, 5.5)                        # the wall of water from the free end of Right to the end of the Side
T_HAGEN = when(1521.69)                     # "Zurück vom Ring!"
T_DROWN = 7.57                              # dragged under: the basses' F sharp sinks
T_RING = when(1590)                         # the crash: Flosshilde holds the Ring up
T_JOY = T_RING + 1.5
T_RECEDE = (when(1592), when(1593.9))       # the flood draws back as Valhalla shimmers
T_VALHALLA = 19.9                           # the strings' tremolo, Valhalla once more
T_DOWN = 32.17                              # the Twilight's blows: Valhalla falls
T_RED = [39.2, 46.17]                       # love as redemption, the violins
T_CHORD = 81.28                             # the last chord
# Hagen's cry, from the vocal score: (bar, start, length in beats, note), 4/4
HAGEN_CRY = [(1521, 2.75, 0.25, 'C4'), (1521, 3.0, 0.75, 'C4'), (1521, 3.75, 0.25, 'Ab3'), (1522, 0, 1.2, 'E4')]

WOGLINDE = hexc('#c0f4ff')
WELLGUNDE = hexc('#20ff90')
FLOSSHILDE = hexc('#8c60ff')
HAGEN = hexc('#7a00ff')
STEEL = hexc('#c8d8ff')
GOLD = hexc('#ffaa00')
SILVER = hexc('#f4f8ff')
GOLDWHITE = hexc('#fff0c0')
EMBERS = hexc('#a0207a')
TONGUE = hexc('#fff0b0')
MAIDS = (WOGLINDE, WELLGUNDE, FLOSSHILDE)

START = dict(river=0.3, forest=0.2, sun=0.0, night=0.12, pyre=0.95, blaze=0.85, valhalla=0.45, flood=0.0)
END = dict(river=0.75, forest=0.0, sun=0.0, night=0.0, pyre=0.0, blaze=0.0, valhalla=0.0, flood=0.0)
BLOOM_END = 0.72                            # the radiance over every run at the end (gold-white porch, silver wings)
RING_AT = ('Right', 0.55)                   # the maidens with the Ring at the end, swimming off down the river

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
    """Every note of the excerpt, tagged: (time, seconds, midi, velocity, part, k). The flood's chords are 'rhine',
    the rising line under Hagen's struggle 'maids', the notes after the crash the maidens' 'joy', the strings'
    shimmer 'valhalla', the Twilight's blows 'down', the violins' melody 'red' and the last chord 'chord'; the rest
    is 'tutti'. Hagen's cry is 'hagen' (k = which note)."""
    N = []
    for t, d, m, v, h in EX['notes']:
        if t < 4.2 and h == 0:
            part = 'rhine'
        elif 3.5 <= t < T_RING - 0.05 and m >= 57:
            part = 'maids'
        elif T_RING + 0.5 <= t < T_RECEDE[0] and h == 0:
            part = 'joy'
        elif T_RECEDE[0] + 1.0 <= t < 30.8 and h == 0:
            part = 'valhalla'
        elif 30.8 <= t < T_RED[0] - 0.1 and d >= 1.0:
            part = 'down'
        elif T_RED[0] - 0.1 <= t < T_CHORD - 0.05 and h == 0:
            part = 'red'
        elif t >= T_CHORD - 0.05:
            part = 'chord'
        else:
            part = 'tutti'
        N.append((t, d, m, v, part, h))
    for k, (b, x, n, name) in enumerate(HAGEN_CRY):
        t0 = when(b + x / 4)
        N.append((t0, when(b + (x + n) / 4) - t0, note(name), 122, 'hagen', k))
    return sorted(N, key=lambda e: e[0])


def flood_at(t):
    """The flood's reach (0..1 of the house from the free end of Right)."""
    rise = smoothstep(*T_FLOOD, t)
    back = smoothstep(*T_RECEDE, t)
    return rise * (1 - 0.68 * back)


def maids(G, S, t):
    """Where the three maidens are: on the flood's front, then round the porch, then circling, then off down Right."""
    L, pf = S['L'], S['pf']
    front = L - flood_at(t) * (L + 60)
    out = []
    for i in range(3):
        if t < T_FLOOD[1] - 2:
            p = front + 40 + 45 * i + 20 * np.sin(2 * np.pi * (t / 1.3 + i / 3))
        elif t < T_JOY:
            u = smoothstep(T_FLOOD[1] - 2, T_DROWN, t)
            p0 = 40 + 45 * i
            p = p0 + (pf - 60 + 60 * i - p0) * u + 12 * np.sin(2 * np.pi * (t / 0.9 + i / 3))
        elif t < T_RECEDE[1]:
            u = (t - T_JOY) / (T_RECEDE[1] - T_JOY)
            p = pf + 900 * np.sin(2 * np.pi * (1.2 * u + i / 3))
        else:
            u = smoothstep(T_RECEDE[1], T_RECEDE[1] + 6, t)
            p0 = pf + 900 * np.sin(2 * np.pi * (1.2 + i / 3))
            p = p0 + (at(G, *RING_AT) - 40 + 40 * i - p0) * u + 15 * np.sin(2 * np.pi * (t / 2.2 + i / 3))
        out.append(float(np.clip(p, 0, L)))
    return out


def render(G, seed=30):
    F = nframes(D)
    out = np.zeros((F, G.N, 3))
    S = stage(G)
    d, L, pf = S['d'], S['L'], S['pf']
    N = compose()
    rhine_on = T_RHINE
    maid_notes = [e for e in N if e[4] == 'maids']
    joy_on = sorted({e[0] for e in N if e[4] == 'joy'})
    valh = [t for i, t in enumerate(sorted({e[0] for e in N if e[4] == 'valhalla'})) if i % 4 == 0]
    downs = sorted({e[0] for e in N if e[4] == 'down' and e[5] == 0})
    red = sorted({e[0]: e for e in N if e[4] == 'red'}.values())     # one wave per onset
    p_hagen0, p_ring = at(G, 'Porch Left', 0.3), pf - 60

    for f in range(F):
        t = f * DT
        T = t + 80 * K
        fl = flood_at(t)
        quench = smoothstep(T_FLOOD[1], T_FLOOD[1] + 1, t)
        lv = dict(START)
        lv['flood'] = fl
        for k in ('pyre', 'blaze'):
            lv[k] = START[k] * (1 - quench)
        lv['night'] = START['night'] * (1 - quench) + 0.5 * smoothstep(*T_RECEDE, t) * (1 - smoothstep(T_RED[0], T_RED[0] + 8, t))
        vglow = smoothstep(T_VALHALLA - 1, T_VALHALLA + 2, t) * (1 - smoothstep(T_DOWN, T_DOWN + 7, t))
        lv['valhalla'] = START['valhalla'] * (1 - quench) + 0.95 * vglow
        lv['river'] = START['river'] + (END['river'] - START['river']) * smoothstep(*T_RECEDE, t)
        lv['forest'] = START['forest'] * (1 - quench)
        fr = scene(S, T, lv)

        # steam where the water meets the fire, while it is still burning
        front = L - fl * (L + 60)
        if T_FLOOD[0] <= t < T_FLOOD[1] + 1:
            fr += light(WHITE, 0.7 * np.exp(-((d - front + 70) / 70) ** 2))
            fr += light(TONGUE, 0.5 * np.exp(-((d - front + 180) / 90) ** 2) * (1 - quench))

        # the Rhine's waves: every phrase a bright surge flowing down the water
        for t0 in rhine_on:
            a = t - t0
            if 0 <= a < 1.6:
                p = L - 1500 * a
                wet = smoothstep(front - 40, front + 40, d)
                fr += light(RIVER_GREEN, 0.75 * np.exp(-a / 0.8) * wet * np.exp(-((d - p) / 140) ** 2))

        # the maidens: points of their colours with ripples on every note of their song
        ms = maids(G, S, t)
        for j, (t0, dur, m, v, _, k) in enumerate(maid_notes):
            fr = ring(fr, S, t, t0, ms[j % 3], MAIDS[j % 3], 0.8, speed=900, width=90, tau=0.6)
        for j, t0 in enumerate(joy_on):
            fr = ring(fr, S, t, t0, ms[j % 3], MAIDS[j % 3], 0.85, speed=1100, width=110, tau=0.6)
        for i, p in enumerate(ms):
            fr = fr * (1 - 0.8 * np.exp(-((d - p) / 14) ** 2))[:, None]
            fr += light(MAIDS[i], 1.0 * np.exp(-((d - p) / 9) ** 2)) + light(MAIDS[i], 0.45 * np.exp(-((d - p) / 40) ** 2))

        # Hagen lunges at them and is dragged under
        a = t - T_HAGEN
        if 0 <= a < T_DROWN - T_HAGEN + 2.5:
            ph = p_hagen0 + (p_ring - p_hagen0) * smoothstep(0, T_DROWN - T_HAGEN, a) ** 1.5
            lh = smoothstep(0, 0.4, a) * (1 - smoothstep(T_DROWN - T_HAGEN, T_DROWN - T_HAGEN + 2.0, a))
            fr += light(HAGEN, 0.9 * lh * (0.6 + 0.4 * np.sin(2 * np.pi * (d / 300 - 0.8 * a))) * np.exp(-np.abs(d - ph) / 500))
            fr = figure(fr, S, ph, HAGEN, 0.9 * lh, w=20)
            fr += light(STEEL, 0.7 * lh * np.exp(-((d - ph - 16) / 5) ** 2))
            fr = ring(fr, S, t, T_HAGEN, ph, HAGEN, 1.0, speed=1300, width=200, tau=1.0)
        a = t - T_DROWN
        if 0 <= a < 3:
            fr += light(WHITE, 0.9 * np.exp(-a / 0.25) * np.exp(-((d - p_ring) / 120) ** 2))
            fr = ring(fr, S, t, T_DROWN, p_ring, FOAM, 1.0, speed=1400, width=160, tau=1.0)

        # the Ring held up: the whole house flashes gold, and the gold rides with the maidens after
        a = t - T_RING
        if 0 <= a < 4:
            fr += light(GOLD, 0.95 * np.exp(-a / 0.6))
            fr = ring(fr, S, t, T_RING, ms[2], GOLD, 1.0, speed=1500, width=260, tau=1.2)
        if t >= T_RING:
            fr += light(GOLD, 1.0 * np.exp(-((d - ms[2] - 10) / 6) ** 2)) + light(GOLD, 0.4 * np.exp(-((d - ms[2]) / 50) ** 2))

        # Valhalla's last chords: gold-white surges off the porch; then it falls into a red-violet ember
        i = int(np.searchsorted(valh, t, side='right')) - 1
        if i >= 0 and t - valh[i] < 1.6 and t < T_DOWN:
            a = t - valh[i]
            fr = ring(fr, S, t, valh[i], pf, VALHALLA, 0.7, speed=900, width=200, tau=0.9)
            fr += light(VBLUE, 0.35 * np.exp(-a / 0.8) * (1 - S['porch']) * (1 - smoothstep(front - 40, front + 40, d)))
        for t0 in downs:
            a = t - t0
            if 0 <= a < 2:
                fr *= (1 - 0.7 * np.exp(-a / 0.5) * S['pyre'])[:, None]
                fr += light(EMBERS, 0.8 * np.exp(-a / 0.8) * S['pyre'])
        hits = [(t0, 0.8, pf) for t0 in downs]
        fr += light(AMBER, np.clip(sparks(S, hits, t, 31, n=20, reach=0.9), 0, 1))

        # redemption: each note blooms the house brighter, gold-white out of the porch, silver over the wings
        bloom = BLOOM_END * (0.6 * smoothstep(T_RED[0] - 1, T_RED[0] + 14, t) + 0.4 * smoothstep(57.0, T_CHORD + 1, t))
        swell = 0.15 * smoothstep(T_CHORD, T_CHORD + 3, t) * (1 - smoothstep(T_CHORD + 4, D, t))
        b = bloom + swell
        if b > 0:
            u = 0.5 + 0.5 * np.sin(2 * np.pi * (d / 600 - 0.05 * t))
            fr += light(GOLDWHITE, b * S['porch'] * (0.85 + 0.15 * u))
            fr += light(SILVER, 0.85 * b * (1 - S['porch']) * (0.75 + 0.25 * u))
            fr += light(GOLDWHITE, 0.4 * b * (1 - S['porch']) * np.exp(-np.abs(d - pf) / 900))
        for j, (t0, dur, m, v, _, k) in enumerate(red):     # every note of the melody a wave out of the porch
            if dur >= 0.3 and k == 0:
                fr = ring(fr, S, t, t0, pf, GOLDWHITE, 0.9, speed=700, width=300, tau=1.6)
                fr = ring(fr, S, t, t0 + 0.15, pf, SILVER, 0.6, speed=1100, width=120, tau=1.2)
        a = t - T_CHORD
        if 0 <= a < 6:
            fr = ring(fr, S, t, T_CHORD, pf, GOLDWHITE, 1.0, speed=600, width=400, tau=2.5)
        out[f] = fr
    return np.clip(out, 0, 1)


def score(M, G):
    """Wagner's notes orchestrated from the piano reduction, Hagen's cry on trombones, the flood and Valhalla's fall
    on the stage, and then the music alone."""
    pan_at = panner(G)
    S = stage(G)
    pf = pan_at(at(G, 'Porch Front', 0.5))
    pl = pan_at(at(G, 'Porch Left', 0.3))
    o = Orchestra(M, level=1.75)
    N = compose()
    notes = [(t, d, m, v, k) for t, d, m, v, part, k in N if part != 'hagen']
    parts = {(round(t, 4), m, k): part for t, d, m, v, part, k in N}

    def size(t):
        return 0.35 if T_RED[0] + 18 <= t < T_CHORD - 0.1 else 1.0

    def role(t, d, m, v, h):
        part = parts.get((round(t, 4), m, h))
        if part == 'red':                                   # redemption: the violins sing it, violas under
            return [('violins', 0, 6, 0.75), ('violas', -12, -10, 0.35)] + \
                ([('flutes', 0, -16, 0.25)] if d >= 0.55 and t < 57 else [])
        if part == 'down':                                  # the Twilight's blows: brass, full weight
            if h == 1 or m < 60:
                return [('trombones', 0, 4, 0.8), ('tuba', -12 if m >= 40 else 0, 0, 0.6), ('basses', -12, 0, 0.5)]
            return [('horns', 0, 4, 0.8), ('trumpets', 0, -6, 0.5), ('violins', 0, 0, 0.5)]
        if part == 'chord':                                 # the last chord, the whole orchestra
            if h == 1:
                return [('cellos', 0, 0, 0.7), ('basses', -12 if m >= 40 else 0, 0, 0.6), ('tuba', 0, -8, 0.5),
                        ('trombones', 12 if m < 48 else 0, -8, 0.45)]
            return [('violins', 0, 0, 0.6), ('horns', -12, -4, 0.55), ('trumpets', -12, -14, 0.35),
                    ('flutes', 0, -12, 0.3)]
        if T_RED[0] - 0.1 <= t < T_CHORD - 0.1 and h == 1:   # under redemption: the harp and the low strings
            return [('harp', 0, -4, 0.55), ('cellos', 0, -10, 0.35)]
        return None

    o.tutti(tidy(notes), size=size, role=role, pan=lambda t, m: 0.0)
    for t, d, m, v, part, k in N:                           # Hagen: "Zurück vom Ring!"
        if part == 'hagen':
            o.play('trombones', m, t, max(d, 0.15), v, pl, 0.95)
            o.play('horns', m, t, max(d, 0.15), v - 10, pl, 0.5)
    o.hit('timpani roll', T_CHORD - 2.5, 96, pitch=-2, gain=0.5)
    o.hit('crash', T_CHORD + 1.0, 104, gain=0.45)
    o.hit('timpani', T_CHORD + 1.0, 118, pitch=-1, gain=0.6)

    # the stage
    front = lambda t: pan_at(S['L'] - flood_at(t) * (S['L'] + 60))
    o.wind(0.0, 9.0, lambda tt: 0.6 + 0.4 * (tt < 6), pan=front, seed=31)    # the flood's roar
    o.fire(0.0, 7.0, lambda tt: np.clip(1 - tt / 6.5, 0, 1), pan=front, crackle=26, seed=33)   # steam and fire dying
    o.thunder(0.05, near=0.8, pan=pan_at(S['L']), gain=0.8)                    # the wall of water breaks in
    o.boom(T_DROWN, pf, 0.8)                                                    # Hagen goes under
    o.thunder(T_DROWN + 0.05, near=0.6, pan=pf, gain=0.6)
    o.hit('crash', T_RING, 112, gain=0.5, pan=pf)                              # the Ring held up
    o.play('glock', note('C#6'), T_RING + 0.05, 0.1, 100, pf, 0.4)
    o.wind(T_RECEDE[0], T_RECEDE[1] + 2, 0.35, pan=pan_at(at(G, 'Right', 0.6)), seed=35)   # the water drawing back
    for t0 in sorted({e[0] for e in N if e[4] == 'down' and e[5] == 0})[1:]:   # Valhalla's fall
        o.boom(t0, pf, 1.0)
        o.shatter(t0 + 0.05, pf, 0.8)
        o.thunder(t0 + 0.1, near=0.9, pan=pf, gain=0.9)
    o.effects([(0.0, 0.0), (T_HAGEN - 0.4, 0.0), (T_HAGEN, -9.0), (T_HAGEN + 1.6, -9.0), (T_HAGEN + 2.4, 0.0),
               (T_RING + 3.0, -3.0), (T_RECEDE[0], -8.0), (30.0, -6.0), (31.0, 0.0), (37.5, 0.0), (39.0, -30.0)])
