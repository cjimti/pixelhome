"""Fafner: the horn has woken the dragon. Two red eyes burn in the cave mouth; with every low note in the depths
the cave heaves, and a mass of ochre scales over black swells out of the middle of Porch Front, its scales
rippling. Siegfried strides from his tree along Left to the corner of the porch to face it, laughing at it.

"Was ist da?": the eyes flare and the dragon roars in octaves on tubas and trombones, an ochre blast across the
whole house and then a pulse from the cave on every note. On the low octaves' growling tremolo it crawls out
onto the porch until it fills Porch Front and the back of both porch runs, its tail lashing out along Right on
the orchestra's blows while Siegfried taunts it in emerald bursts. "Zu tauben Reden taugt er schlecht": it
breathes fire, a blast racing from its jaws along Porch Left, Left and Side to the end of the house, red to
orange to white-hot, Siegfried flaring in it untouched; then it stamps on the pounding octaves of "dich zu
verschlingen", the whole porch thumping stone and ochre with each step, and breathes again along Right; and
Siegfried laughs back at it ("Hoho! Du grausam grimmiger Kerl!") as the two stand face to face.

The music is Wagner's own: Act II, bars 1016 to 1029 and 1038 to 1045, as Solti's 1958 Vienna Philharmonic
recording takes them, from the Wagner Ring Dataset's piano reduction (pixelhome/ring.py): the dragon's depths
and roars on tubas, trombones, bassoons and basses, the tremolos on low strings, the higher lines (Siegfried's
mockery) on horns, clarinets and violins. The stage adds the dragon's roar as a growl of thunder in the cave,
the rush of its fire, the crack of its tail and a great blow under every stamp; the effects lead here, backing
off only under Siegfried's taunts.

compose() holds every note; stage(), forest(), figure() and sparks() are Act II's forest and cave, shared word
for word with SF11 on a clock that runs on from scene to scene; dragon(), breath(), hero() and bird() are the
dragon fight's own, shared with SF16 to SF19."""
import numpy as np
from pixelhome.fx import DT, hexc, light, smoothstep, nframes, keys, Flicker, smooth_noise, colormap
from pixelhome.ring import Orchestra, excerpt, tidy

CODE = 'SF17'
TITLE = 'Fafner'
KIND = 'show'
DESCRIPTION = ('The dragon wakes and crawls out of its cave: a huge mass of scales filling the porch, with red '
               'eyes, a lashing tail, and fire it breathes from one end of the house to the other.')
VOICEOVER = ('Out of the cave crawls Fafner, the dragon, breathing fire. '
             'Siegfried has never been afraid of anything, and he is not afraid now.')

K = 6                                       # this scene's place on Act II's shared clock: T = t + 80 K
EX = excerpt(__file__)                      # Act II, bars 1016-1029 and 1038-1045, Solti 1958
BAR = {int(m): t for m, t in EX['bars']}
D = EX['seconds']
T_HEAVE = 0.0                               # the depths stir: the cave heaves
T_WALK = (2.0, 10.0)                        # Siegfried strides to the corner of the porch
T_ROAR = BAR[1020]                          # "Was ist da?": the roar
T_OUT = BAR[1025]                           # the growling tremolo: it crawls out
T_FIRE = [BAR[1039], BAR[1043]]             # fire along Left and Side, then along Right
T_LASH = [BAR[1027], BAR[1028], BAR[1029], BAR[1044] + 0.4]  # the tail lashes along Right
T_STAMP = BAR[1039]                         # the pounding octaves: it stamps
EXT = (260.0, 430.0)                        # how far it spreads either side of the cave's middle: half out, all out

NIGHT = hexc('#14a878')
MOON = hexc('#6080ff')
DAY = hexc('#18a020')
SUN = hexc('#ffd040')
CAVE = hexc('#8a2000')
SCALE = hexc('#c88a20')
EYE = hexc('#ff0000')
STONE = hexc('#8a8a80')
BLOOD = hexc('#c00010')
GOLD = hexc('#ffaa00')
ALBERICH = hexc('#ff1000')
MUD = hexc('#5a1200')
WHITE = hexc('#ffffff')
SIEGFRIED = hexc('#00ff40')
HEAD = hexc('#e8ffe8')
BIRD = hexc('#ff30d0')
STEEL = hexc('#e8f8ff')
HILT = hexc('#ffcc40')
FIRE = colormap([(0.0, hexc('#300400')), (0.3, hexc('#ff2000')), (0.6, hexc('#ff5000')), (0.85, hexc('#ffb020')),
                 (1.0, hexc('#fff0b0'))])
LONG = 1.7                                  # the dragon spreads LONG times as far toward Right as toward Left
LIT = dict(night=0.2, day=0.7, shafts=0.75, cave=0.35, eyes=0.0)       # Act II by day
START = dict(LIT, cave=0.6, eyes=0.6)                                  # where SF16 left it


def at(G, seg, u):
    """Path distance u of the way along a segment."""
    s = G.pd[G.seg[seg]]
    return float(s.min() + u * (s.max() - s.min()))


def stage(G):
    """The forest outside Fafner's cave as profiles over the house: the porch is the cave mouth (darkest at the
    back, the middle of Porch Front), Left, Right and Side the trees, with two eyes on Porch Front."""
    d = G.pd
    rng = np.random.default_rng(1857)       # the same trees and light in every scene, so the cuts match
    porch = np.isin(G.seg_of, ['Porch Left', 'Porch Front', 'Porch Right'])
    mid = at(G, 'Porch Front', 0.5)
    return dict(
        d=d, mid=mid, porch=porch,
        trees=(~porch) * (0.6 + 0.4 * smooth_noise(rng, d, 35.0)),
        mouth=porch * (0.35 + 0.65 * np.exp(-((d - mid) / 160) ** 2)),
        eyes=np.exp(-((d - at(G, 'Porch Front', 0.4)) / 5) ** 2) + np.exp(-((d - at(G, 'Porch Front', 0.6)) / 5) ** 2),
        edge=porch * (1 - np.exp(-((d - mid) / 220) ** 2)),
        shaft_at=rng.uniform(0, d.max(), 9), shaft_v=rng.uniform(-14, 14, 9), shaft_w=rng.uniform(25, 60, 9),
        leaf=Flicker(rng, G.N, 0.1, 0.6),
        smoulder=Flicker(rng, G.N, 0.3, 1.5),
    )


def forest(S, T, lv):
    """The forest at shared time T with levels lv (night, day, shafts, cave, eyes)."""
    d, leaf = S['d'], S['leaf'](T)
    fr = light(NIGHT, lv['night'] * S['trees'] * (0.85 + 0.15 * leaf))
    fr += light(DAY, lv['day'] * S['trees'] * (0.8 + 0.2 * leaf))
    fr += light(NIGHT, 0.4 * (lv['night'] + lv['day']) * S['edge'])
    L = d.max()
    shafts = np.zeros_like(d)
    for p, v, w in zip(S['shaft_at'], S['shaft_v'], S['shaft_w']):
        c = (p + v * T) % L
        shafts += np.exp(-((d - c) / w) ** 2)
    shafts *= ~S['porch']
    fr += light(MOON, lv['shafts'] * (1 - min(1.0, 2 * lv['day'])) * shafts)
    fr += light(SUN, lv['shafts'] * min(1.0, 2 * lv['day']) * shafts)
    fr += light(CAVE, lv['cave'] * S['mouth'] * (0.75 + 0.25 * S['smoulder'](T)))
    fr += light(EYE, lv['eyes'] * S['eyes'])
    return fr


def figure(fr, S, p, col, lvl, w=16.0):
    """A person at path distance p: a body that stands in front of the forest, and a halo."""
    body = np.exp(-((S['d'] - p) / w) ** 2)
    fr = fr * (1 - 0.85 * min(1.0, lvl / 0.2) * body)[:, None]
    return fr + light(col, lvl * body) + light(col, 0.35 * lvl * np.exp(-((S['d'] - p) / (3 * w)) ** 2))


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


def hero(fr, S, p, lvl, flare=0.0, col=None):
    """Siegfried at path distance p: emerald with a white-hot head; flare brightens him for a moment."""
    fr = figure(fr, S, p, SIEGFRIED if col is None else col, lvl * (1 + flare))
    return fr + light(HEAD, min(1.0, lvl * (0.75 + flare)) * np.exp(-((S['d'] - p) / 5) ** 2))


def hops(moves, t, p0):
    """Where something is at t after quick hops [(time, target)], each eased over a quarter of a second."""
    p = p0
    for th, q in moves:
        if t < th:
            break
        p = p + (q - p) * smoothstep(th, th + 0.25, t)
    return p


def bird(fr, S, p, back, lvl, T):
    """The Woodbird at p (back: where it was a moment ago): hot magenta, a white-hot centre and a comet trail."""
    d = S['d']
    flick = 0.8 + 0.2 * np.sin(2 * np.pi * 9 * T)
    lo, hi = min(p, back), max(p, back)
    trail = ((d >= lo - 4) & (d <= hi + 4)) * np.exp(-np.abs(d - p) / 70)
    fr = fr + light(BIRD, lvl * flick * np.clip(np.exp(-((d - p) / 8) ** 2) + 0.75 * trail, 0, 1))
    return fr + light(WHITE, 0.85 * lvl * np.exp(-((d - p) / 3) ** 2))


def dragon(fr, S, T, ext, lvl, eyes=0.0, head=None, tail=0.0):
    """Fafner: black under a mass of ochre scales spreading ext toward Left from the cave's middle and LONG times
    that toward Right, onto the Right wing; broad bands of scale ripple through it as it breathes, its edges burn
    bright, two red eyes sit either side of its head, and its tail lashes out past the Right edge (tail: reach)."""
    d, c = S['d'], S['mid']
    if ext <= 0 or lvl <= 0:
        return fr
    x = d - c
    edge = np.where(x < 0, ext, LONG * ext)
    body = smoothstep(edge + 50, edge - 70, np.abs(x))
    fr = fr * (1 - 0.95 * min(1.0, lvl / 0.15) * body)[:, None]
    scales = np.clip(0.45 + 0.55 * np.sin(2 * np.pi * d / 55 - 4.0 * T) + 0.3 * np.sin(2 * np.pi * d / 150 + 1.3 * T),
                     0, 1)
    fr = fr + light(SCALE, lvl * body * (0.35 + 0.75 * scales))
    fr = fr + light(SUN, 0.35 * lvl * body * scales ** 6)
    fr = fr + light(SCALE, 0.9 * lvl * np.exp(-((np.abs(x) - edge) / 28) ** 2))
    if tail > 1:
        u = x - LONG * ext
        lash = (u > -40) * smoothstep(tail + 30, tail - 30, u)
        fr = fr * (1 - 0.8 * lash)[:, None] + light(SCALE, 0.95 * lvl * lash * (0.5 + 0.5 * np.clip(u / tail, 0, 1)))
        fr = fr + light(SUN, 0.9 * lvl * np.exp(-((u - tail) / 12) ** 2))
    if eyes > 0:
        h = c if head is None else head
        e = np.clip(np.exp(-((d - h + 13) / 4.5) ** 2) + np.exp(-((d - h - 13) / 4.5) ** 2), 0, 1)
        fr = fr * (1 - min(1.0, eyes) * e)[:, None] + light(EYE, eyes * e)
        fr = fr + light(EYE, 0.6 * eyes * np.exp(-((d - h) / 26) ** 2))
    return fr


def breath(S, flick, src, side, a, reach=1500.0, hold=1.6):
    """A blast of fire from the dragon's mouth at src along the roofline toward side (+1 Right, -1 Left), a seconds
    in: a white-hot front races out, the whole length roars red and orange and flickers, then burns out
    -> (N,3) PWM."""
    d = S['d']
    x = (d - src) * side
    front = reach * min(1.0, a / 0.8)
    body = smoothstep(-30, 20, x) * smoothstep(front + 30, front - 150, x)
    fade = np.exp(-max(a - hold, 0) / 0.5)
    heat = np.clip(1 - x / reach, 0, 1)
    v = np.clip(body * fade * (0.3 + 0.45 * heat) * (0.65 + 0.35 * flick), 0, 1)
    tip = np.exp(-((x - front) / 45) ** 2) * fade * (a < 0.9)
    return light(FIRE(v), np.clip(1.25 * v + 0.15 * body * fade, 0, 1)) + light(WHITE, 0.7 * tip)


def compose():
    """Every note of the excerpt, tagged: (time, seconds, midi, velocity, part, k). The depths under Siegfried's
    laughter ('heave', k=0) and under the growling tremolo ('heave', k=1) push the dragon out; the octaves of
    "Was ist da?" are its roar ('roar'); the pounding octaves are its stamps ('stamp', the left hand's beats) and
    their right hand its growl ('growl'); the right hand of 1027-1029 and of "Hoho!" is Siegfried's taunt
    ('taunt'); the rest is his mockery ('sieg') over the low strings ('low')."""
    N = []
    for t, d, m, v, h, *tr in tidy(EX['notes']):
        if T_ROAR - 0.01 <= t < BAR[1022] - 0.01:
            part, k = 'roar', None
        elif T_STAMP - 0.01 <= t < BAR[1044] - 0.01:
            part, k = ('growl' if h == 0 else 'stamp'), None
        elif h == 1 and m <= 43 and t < BAR[1022]:
            part, k = 'heave', 0
        elif h == 1 and m <= 45 and T_OUT - 0.01 <= t < BAR[1027]:
            part, k = 'heave', 1
        elif h == 0 and (BAR[1027] - 0.01 <= t < BAR[1030] - 0.01 or t >= BAR[1044] - 0.01):
            part, k = 'taunt', None
        elif h == 0 and m >= 55:
            part, k = 'sieg', None
        else:
            part, k = 'low', None
        N.append((float(t), float(d), int(m), int(v), part, k, bool(tr and tr[0])))
    return sorted(N, key=lambda e: e[0])


def extent(t, steps):
    """How far the dragon has come out at t: it grows on each note of its climbs."""
    e = 0.0
    for k, ts in enumerate(steps):
        a, b = (0.0, EXT[0]) if k == 0 else EXT
        if not ts or t < ts[0]:
            continue
        for i, s in enumerate(ts):
            e = max(e, a + (b - a) * (i + smoothstep(s, s + 0.35, t)) / len(ts) * (t >= s))
    return e


def render(G, seed=17):
    rng = np.random.default_rng(seed)
    F = nframes(D)
    out = np.zeros((F, G.N, 3))
    S = stage(G)
    d, mid = S['d'], S['mid']
    N = compose()
    N = [e[:6] for e in N]
    heave = [e for e in N if e[4] == 'heave']
    steps = [sorted([e[0] for e in heave if e[5] == 0 and e[0] > 0.5] + [e[0] for e in N if e[4] == 'roar']),
             [e[0] for e in heave if e[5] == 1]]
    roar = [e for e in N if e[4] == 'roar']
    taunt = [e for e in N if e[4] == 'taunt']
    stamp = []
    for t0 in sorted({e[0] for e in N if e[4] == 'stamp'}):
        if not stamp or t0 - stamp[-1] > 0.42:
            stamp.append(t0)
    stamp = np.array(stamp)
    flick = Flicker(rng, G.N, 4.0, 12.0)
    tree, corner = at(G, 'Left', 0.5), at(G, 'Porch Left', 0.3)

    for f in range(F):
        t = f * DT
        T = t + 80 * K
        lv = dict(START)
        lv['eyes'] = keys(t, [(T_ROAR - 0.2, START['eyes']), (T_ROAR, 1.0)])
        e = extent(t, steps)
        stomp = 0.0
        j = int(np.searchsorted(stamp, t, side='right')) - 1
        if j >= 0 and t - stamp[j] < 0.6:
            stomp = np.exp(-(t - stamp[j]) / 0.18)
        lv['day'] *= 1 - 0.35 * stomp
        fr = forest(S, T, lv)

        # each note of the climb: the cave heaves and an ochre wave rolls out of it
        for t0, dur, m, v, part, k in heave:
            a = t - t0
            if 0 <= a < 1.8:
                fr += light(SCALE, (0.7 + 0.3 * k) * np.exp(-a / 0.6) * np.exp(-((np.abs(d - mid) - e - 700 * a) / 110) ** 2))
                fr += light(CAVE, 0.9 * np.exp(-a / 0.35) * S['mouth'])

        # the dragon: breathing slowly on the shared clock, its head toward Siegfried, the tail lashing on Right
        lvl = keys(t, [(T_HEAVE, 0.3), (T_ROAR, 0.75)]) * (0.88 + 0.12 * np.sin(2 * np.pi * T / 3.2))
        tail = sum(520 * np.exp(-max(t - tl, 0) / 0.5) * smoothstep(tl - 0.05, tl + 0.15, t) for tl in T_LASH)
        head = mid - 0.9 * e
        fr = dragon(fr, S, T, e, lvl * (1 + 0.5 * stomp), lv['eyes'], head, tail)

        # the roar: an ochre blast over the whole house, then a pulse from the dragon on every note
        if T_ROAR <= t < T_ROAR + 1.2:
            a = t - T_ROAR
            fr += light(SCALE, 0.95 * np.exp(-a / 0.4))
            fr += light(EYE, 0.6 * np.exp(-a / 0.25) * S['porch'])
        for t0, dur, m, v, part, k in roar:
            a = t - t0
            if 0 <= a < 1.0:
                fr += light(SCALE, 0.7 * np.exp(-a / 0.35) * np.exp(-((np.abs(d - mid) - e - 900 * a) / 100) ** 2))

        # fire: along Porch Left, Left and Side to the end, then along Right to the free end
        for i, t0 in enumerate(T_FIRE):
            a = t - t0
            if 0 <= a < 4.4:
                side = -1 if i == 0 else 1
                src = head if i == 0 else mid + LONG * e
                fr += breath(S, flick(T), src, side, a, reach=1900 if i == 0 else 420, hold=3.0)

        # the giants' motif: every stamp thumps the whole porch stone and ochre
        if stomp:
            fr += light(STONE, 0.7 * stomp * S['porch'])
            fr += light(SCALE, 0.5 * stomp * np.exp(-((np.abs(d - mid) - e - 1200 * (t - stamp[j])) / 120) ** 2))

        # Siegfried strides to the corner of the porch; emerald bursts on his motif; he flares in the fire
        p = tree + (corner - tree) * smoothstep(*T_WALK, t)
        flare = 0.0
        for t0, dur, m, v, part, k in taunt:
            a = t - t0
            if 0 <= a < 1.2:
                flare = max(flare, 0.5 * np.exp(-a / 0.2))
                fr += light(SIEGFRIED, 0.8 * np.exp(-a / 0.4) * np.exp(-((np.abs(d - p) - 900 * a) / 70) ** 2))
        if T_FIRE[0] + 0.4 <= t < T_FIRE[0] + 2.0:
            flare = max(flare, 0.6)
        out[f] = hero(fr, S, p, 0.85 + 0.05 * smoothstep(T_ROAR, T_ROAR + 2, t), flare)
    return np.clip(out, 0, 1)


def score(M, G):
    """Wagner's notes, orchestrated from the piano reduction, with the stage's sounds on top."""
    order = np.argsort(G.pd)
    xs, ds = G.pos[order, 0], G.pd[order]
    x0, x1 = xs.min(), xs.max()

    def pan_at(dd):                         # path distance -> left/right across the facade, from the street
        x = np.interp(dd, ds, xs)
        return float(0.85 * (2 * (x - x0) / (x1 - x0) - 1))

    cave = pan_at(at(G, 'Porch Front', 0.5))
    left, right = pan_at(at(G, 'Side', 0.2)), pan_at(at(G, 'Right', 0.8))
    me = pan_at(at(G, 'Porch Left', 0.3))
    o = Orchestra(M, level=2.35)
    N = compose()
    for t, d, m, v, part, k, trem in N:
        if part == 'heave':
            o.play('tuba', m, t, d, v + 6, cave, 0.9)
            o.play('bassoons', m + 12, t, d, v - 6, cave, 0.5)
            o.play('basses', m, t, d, v, cave, 0.5)
        elif part in ('roar', 'growl'):
            if m < 60:
                o.play('trombones', m, t, d, v + 6, cave, 0.75)
                o.play('tuba', m - 12, t, d, v, cave, 0.6)
            else:
                o.play('horns', m, t, d, v, cave, 0.6)
        elif part == 'stamp':
            o.play('tuba', m, t, d, v + 4, cave, 0.8)
            o.play('basses', m, t, d, v, cave, 0.55)
        elif part == 'taunt':
            o.play('horns', m, t, d, v + 6, me, 0.85)
            o.play('violins', m, t, d, v - 8, me, 0.35)
        elif part == 'sieg':
            o.play('clarinets', m, t, d, v, me, 0.6)
            o.play('violins', m, t, d, v - 10, me, 0.35)
        else:
            o.play('cellos trem' if trem and m < 60 else 'violas trem' if trem else 'cellos' if m < 60 else 'violas',
                   m, t, d, v - 4, cave, 0.5)
    # the stage: the roar, the tail, the fire, the stamps
    o.thunder(T_ROAR, near=0.8, pan=cave, gain=1.0)
    o.hit('gong', T_ROAR, 115, gain=0.6, pan=cave)
    o.thunder(T_OUT + 0.3, near=0.5, pan=cave, gain=0.7)
    for tl in T_LASH:
        o.hit('timpani', tl, 118, pitch=-2, gain=0.6, pan=right)
        o.hit('brake drum', tl, 110, gain=0.3, pan=right)
        o.wind(tl - 0.3, tl + 0.6, 1.0, pan=right, seed=int(tl * 10))
    for i, t0 in enumerate(T_FIRE):
        dst = left if i == 0 else right
        o.fire(t0, t0 + 4.2, level=lambda tt, t0=t0: np.exp(-np.maximum(tt - t0 - 0.4, 0) / 1.6), pan=(cave + dst) / 2,
               crackle=25, seed=170 + i)
        o.wind(t0, t0 + 1.4, 1.0, pan=dst, seed=171 + i)
        o.hit('crash', t0 + 0.5, 110, gain=0.5, pan=dst)
    last = -1.0
    for t, d, m, v, part, k, trem in N:
        if part == 'stamp' and t - last > 0.42:
            o.boom(t, cave, 0.55)
            last = t
    # the effects lead for the dragon, and back off under Siegfried's taunts
    o.effects([(0, -4), (T_ROAR - 0.5, 0), (BAR[1027] - 0.3, 0), (BAR[1027], -8), (BAR[1030] - 0.5, -8),
               (BAR[1030], -2), (T_FIRE[0] - 0.5, 0), (BAR[1044] - 0.3, 0), (BAR[1044], -8)])
