"""The Dragon Fight: Siegfried and Fafner across the whole house. The dragon fills the porch and spills onto Right,
its ochre scales rippling, its red eyes swinging after him wherever he goes; every note of the orchestra's racing
octaves and chromatic runs ripples down its body while the basses and tubas pound underneath.

He leaps from the corner of the porch out along Left and back, over the dragon onto Right and back again, every
leap an emerald streak and every landing a clash of steel: a white flash, sparks to both ends and a red wound on
the scales where Nothung bit. The dragon lunges and breathes fire after him, a blast racing along Left, then
along Right, each time just behind him; its tail cracks out along Right like a whip, and his heroism rings out in
the horns as the violins shriek.

Then the trumpet sings Nothung and he climbs onto the dragon itself at the middle of the porch: one colossal
blow into the heart. The whole house goes white, and a wave of blood red pours out from the wound to both ends.
"Nothung trägst du im Herzen!": the dragon sinks, its scales dull, its eyes go out one breath at a time, while
Siegfried stands over the heap with the sword shining and emerald sweeps out from him.

The music is Wagner's own: Act II, bars 1051 to 1101, the whole fight from "Hab acht, Brüller!" to the dying
dragon's first words, as Solti's 1958 Vienna Philharmonic recording takes them, from the Wagner Ring Dataset's
piano reduction (pixelhome/ring.py): the racing octaves on violins and trombones, the chromatic runs on strings
and woodwinds, the pounding bass on tubas, basses and timpani, Siegfried's heroism on horns and trumpets, the
sword's motif on the trumpet. The stage adds the clash of steel on every strike, the roar and rush of each blast
of fire, the crack of the tail, the sword driven home with a ringing blow, a crash and a death-rattle of thunder,
and the heap's last breaths; the effects lead through the fight and step back for the trumpet and the end.

compose() holds every note; stage(), forest(), figure() and sparks() are Act II's forest and cave, shared word
for word with SF11 on a clock that runs on from scene to scene; dragon(), breath(), hero() and bird() are the
dragon fight's own, shared with SF16 to SF19."""
import numpy as np
from pixelhome.fx import DT, hexc, light, smoothstep, nframes, keys, Flicker, smooth_noise, colormap
from pixelhome.ring import Orchestra, excerpt, tidy

CODE = 'SF18'
TITLE = 'The Dragon Fight'
KIND = 'show'
DESCRIPTION = ('Siegfried and the dragon fight across the whole house: leaps, fire, a lashing tail and the clash '
               'of the sword, until one blow goes into the dragon\'s heart.')
VOICEOVER = ('Fire, and claws, and a tail like a whip. '
             'And Siegfried, with a sword he made himself.')

K = 7                                       # this scene's place on Act II's shared clock: T = t + 80 K
EX = excerpt(__file__)                      # Act II, bars 1051-1101, Solti 1958
BAR = {int(m): t for m, t in EX['bars']}
D = EX['seconds']
T_FIGHT = [BAR[b] for b in (1053, 1062, 1066, 1072, 1079)]   # the racing passages
T_HERO = [BAR[1059], BAR[1075]]             # Siegfried's heroism in the horns
LEAPS = [(BAR[b], seg, u) for b, seg, u in ((1052, 'Left', 0.7), (1055, 'Porch Left', 0.45), (1059, 'Left', 0.35),
                                             (1062, 'Porch Left', 0.2), (1066, 'Right', 0.6), (1069, 'Right', 0.8),
                                             (1072, 'Right', 0.5), (1075, 'Right', 0.7), (1081, 'Porch Left', 0.25),
                                             (1088, 'Porch Front', 0.3))]
T_STRIKE = [BAR[b] for b in (1057, 1060, 1064, 1068, 1074, 1078, 1083, 1086)]
T_BREATH = [BAR[b] for b in (1054, 1066, 1073, 1082)]
T_LASH = [BAR[b] + 0.4 for b in (1056, 1063, 1070, 1077, 1085)]
T_NOTHUNG = BAR[1088]                       # the trumpet sings Nothung
T_HEART = BAR[1093]                         # the blow to the heart
T_CALL = [BAR[1097], BAR[1098]]             # "Nothung trägst du im Herzen!"
EXT, HEAP = 430.0, 300.0                    # the dragon all out; what is left of it

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
    """Every note of the excerpt, tagged: (time, seconds, midi, velocity, part, k, tremolo). The right hand is the
    racing fight ('race', k = which passage), Siegfried's heroism in its passages ('hero'), the sword's motif
    ('nothung') and, over the heap, his "Nothung trägst du im Herzen!" ('call'); the left hand pounds ('pulse')
    until the blow and then sinks with the dragon ('sink')."""
    N = []
    for t, d, m, v, h, *tr in tidy(EX['notes']):
        k = None
        if t >= T_HEART - 0.01:
            part = 'call' if h == 0 and T_CALL[0] - 0.01 <= t < BAR[1099] else 'sink'
        elif h == 1:
            part = 'pulse'
        elif T_NOTHUNG - 0.01 <= t < BAR[1090] - 0.01:
            part = 'nothung'
        elif any(th - 0.01 <= t < th + dt for th, dt in ((T_HERO[0], BAR[1062] - T_HERO[0]),
                                                          (T_HERO[1], BAR[1079] - T_HERO[1]))):
            part = 'hero'
        else:
            part, k = 'race', max(0, sum(t >= x - 0.01 for x in T_FIGHT) - 1)
        N.append((float(t), float(d), int(m), int(v), part, k, bool(tr and tr[0])))
    return sorted(N, key=lambda e: e[0])


def path(G):
    """Siegfried's leaps: [(time, from, to)] and where he is at t."""
    p = at(G, 'Porch Left', 0.3)
    hops_ = []
    for t, seg, u in LEAPS:
        q = at(G, seg, u)
        hops_.append((t, p, q))
        p = q
    return hops_


def where(hops_, t, p0):
    """Siegfried at t: each leap takes 0.6 s and arcs (the fraction of the way, eased)."""
    p = p0
    for th, a, b in hops_:
        if t < th:
            break
        p = a + (b - a) * smoothstep(th, th + 0.6, t)
    return p


def render(G, seed=18):
    rng = np.random.default_rng(seed)
    F = nframes(D)
    out = np.zeros((F, G.N, 3))
    S = stage(G)
    d, mid = S['d'], S['mid']
    L = d.max()
    N = compose()
    hops_ = path(G)
    p0 = at(G, 'Porch Left', 0.3)
    N = [e[:6] for e in N]
    race = [e for e in N if e[4] == 'race']
    calls = [e for e in N if e[4] == 'call']
    noth = [e for e in N if e[4] == 'nothung']
    flick = Flicker(rng, G.N, 4.0, 12.0)
    head = mid - 0.9 * EXT
    hits = []
    for t in T_STRIKE:
        hits.append((t, 1.0, where(hops_, t, p0)))

    for f in range(F):
        t = f * DT
        T = t + 80 * K
        lv = dict(LIT, cave=keys(t, [(0, 0.6), (T_HEART, 0.6), (D - 4, LIT['cave'])]))     # SF17 left the cave at 0.6
        dead = smoothstep(T_HEART, T_HEART + 10, t)
        lv['eyes'] = 1.0 - smoothstep(T_HEART + 1, T_HEART + 9, t)
        fr = forest(S, T, lv)
        p = where(hops_, t, p0)

        # the dragon: its head swings after him, it lunges before every blast, then sinks after the blow
        right = p > mid + 0.4 * EXT
        aim = mid + 0.9 * LONG * EXT if right else mid - 0.9 * EXT
        head += (aim - head) * min(1.0, 3.0 * DT)
        lunge = sum(np.exp(-((t - tb + 0.5) / 0.35) ** 2) for tb in T_BREATH)
        e = EXT + 50 * lunge + (HEAP - EXT) * dead
        lvl = (0.75 * (0.88 + 0.12 * np.sin(2 * np.pi * T / 3.2)) * (1 - dead) + 0.25 * dead) * (1 + 0.4 * lunge)
        tail = sum(560 * np.exp(-max(t - tl, 0) / 0.45) * smoothstep(tl - 0.05, tl + 0.12, t) for tl in T_LASH)
        fr = dragon(fr, S, T, e, lvl, lv['eyes'], head, tail * (1 - dead))

        # every note of the racing motif: a ripple of ochre down the dragon's body
        for t0, dur, m, v, part, k in race:
            a = t - t0
            if 0 <= a < 0.6:
                fr += light(SCALE, 0.4 * np.exp(-a / 0.2) * np.exp(-((np.abs(d - mid) - 500 * a) / 60) ** 2))

        # fire after him: from the head along his side, each blast just behind him
        for tb in T_BREATH:
            a = t - tb
            if 0 <= a < 4.0:
                side = 1 if where(hops_, tb, p0) > mid else -1
                src = mid + LONG * e if side > 0 else mid - e
                fr += breath(S, flick(T), src, side, a, reach=1900 if side < 0 else 480, hold=2.4)

        # each leap: an emerald streak from where he was to where he lands
        for th, a0, b0 in hops_:
            a = t - th
            if 0 <= a < 1.2:
                lo, hi = min(a0, b0), max(a0, b0)
                cur = a0 + (b0 - a0) * smoothstep(0, 0.6, a)
                streak = ((d >= lo - 20) & (d <= hi + 20)) * np.exp(-np.abs(d - cur) / 220) * np.exp(-max(a - 0.6, 0) / 0.2)
                fr += light(SIEGFRIED, streak)

        # each strike: a clash of steel, sparks to both ends, a red wound where the sword bit the scales
        for th, s, ps in hits:
            a = t - th
            if 0 <= a < 1.0:
                fr += light(STEEL, np.exp(-a / 0.08) * np.exp(-((d - ps) / 30) ** 2))
                wound = mid - e if ps < mid else mid + LONG * e
                fr += light(BLOOD, 0.9 * np.exp(-a / 0.4) * np.exp(-((d - wound) / 45) ** 2))
        fr += light(STEEL, np.clip(sparks(S, hits, t, 18, n=18), 0, 1))

        # Nothung shines in his hand as the trumpet names it
        for t0, dur, m, v, part, k in noth:
            a = t - t0
            if 0 <= a < dur + 0.4:
                fr += light(STEEL, 0.8 * np.exp(-a / (dur + 0.3)) * np.exp(-((d - p - 18) / 14) ** 2))
                fr += light(HILT, 0.6 * np.exp(-a / 0.3) * np.exp(-((d - p + 4) / 6) ** 2))

        # the blow to the heart: the whole house white, then blood red pouring out from the wound to both ends
        if T_HEART <= t < T_HEART + 6:
            a = t - T_HEART
            fr += light(WHITE, 0.95 * np.exp(-a / 0.35))
            fr += light(BLOOD, 0.8 * np.exp(-a / 1.5) * (np.abs(d - mid) < e))
            front = 1400 * a
            pour = smoothstep(front + 80, front - 80, np.abs(d - p)) * np.exp(-max(a - 1.2, 0) / 1.4)
            fr += light(BLOOD, 0.9 * pour)
        if t >= T_HEART:
            fr += light(STEEL, 0.55 * (0.8 + 0.2 * np.sin(2 * np.pi * 0.7 * T)) * np.exp(-((d - p - 18) / 16) ** 2))

        # his motif over the heap: emerald sweeps out from him to both ends
        for t0, dur, m, v, part, k in calls:
            a = t - t0
            if 0 <= a < 1.8:
                fr += light(SIEGFRIED, 0.9 * np.exp(-a / 0.8) * np.exp(-((np.abs(d - p) - 1400 * a) / (130 + 130 * a)) ** 2))

        flare = 0.5 * sum(np.exp(-max(t - th, 0) / 0.15) * (t >= th) for th in T_STRIKE + [T_HEART])
        lvl_me = keys(t, [(0, 0.9), (T_HEART + 4, 0.9), (D - 4, 0.8)])
        out[f] = hero(fr, S, p, lvl_me, min(0.8, flare))
    return np.clip(out, 0, 1)


def score(M, G):
    """Wagner's notes, orchestrated from the piano reduction, with the stage's sounds on top."""
    order = np.argsort(G.pd)
    xs, ds = G.pos[order, 0], G.pd[order]
    x0, x1 = xs.min(), xs.max()

    def pan_at(dd):                         # path distance -> left/right across the facade, from the street
        x = np.interp(dd, ds, xs)
        return float(0.85 * (2 * (x - x0) / (x1 - x0) - 1))

    hops_ = path(G)
    p0 = at(G, 'Porch Left', 0.3)
    me = lambda t: pan_at(where(hops_, t, p0))
    cave = pan_at(at(G, 'Porch Front', 0.5))
    right = pan_at(at(G, 'Right', 0.8))
    o = Orchestra(M, level=1.8)
    for t, d, m, v, part, k, trem in compose():
        if part == 'race':
            if m < 60:
                o.play('trombones', m, t, d, v, cave, 0.55)
                o.play('violas', m + 12, t, d, v - 8, cave, 0.4)
            else:
                o.play('violins', m, t, d, v, cave, 0.6)
                if v >= 100:
                    o.play('flutes' if m < 84 else 'piccolo', m, t, d, v - 16, cave, 0.3)
        elif part == 'pulse':
            o.play('tuba', m, t, d, v, cave, 0.7)
            o.play('basses', m - 12 if m >= 40 else m, t, d, v - 6, cave, 0.5)
            if m < 43 and d >= 0.3:
                o.hit('timpani', t, min(127, v), pitch=-5, gain=0.35, pan=cave)
        elif part == 'hero':
            o.play('horns', m, t, d, v + 4, me(t), 0.85)
            o.play('trumpets', m, t, d, v - 10, me(t), 0.4)
        elif part == 'nothung':
            o.play('trumpets', m, t, d, v + 6, me(t), 0.95)
            o.play('trombones', m - 12, t, d, v - 10, me(t), 0.4)
        elif part == 'call':
            o.play('horns', m, t, d, v, me(t), 0.8)
        else:                                                           # the heap: low strings and tuba, sinking
            o.play('cellos trem' if trem else 'cellos', m, t, d, v - 4, cave, 0.6)
            if m < 48:
                o.play('tuba', m, t, d, v - 12, cave, 0.45)
    # the stage: steel on scales, fire, the tail, the blow, the death
    for th in T_STRIKE:
        o.clash(th, me(th), 120, 0.9)
    for tb in T_BREATH:
        side = right if where(hops_, tb, p0) > at(G, 'Porch Front', 0.5) else pan_at(at(G, 'Left', 0.3))
        o.fire(tb, tb + 3.2, level=lambda tt, tb=tb: np.exp(-np.maximum(tt - tb - 0.3, 0) / 1.2), pan=(cave + side) / 2,
               crackle=25, seed=int(tb * 10))
        o.wind(tb - 0.2, tb + 1.2, 1.0, pan=side, seed=int(tb * 10) + 1)
        o.thunder(tb - 0.4, near=0.6, pan=cave, gain=0.5)
    for tl in T_LASH:
        o.hit('timpani', tl, 118, pitch=-2, gain=0.5, pan=right)
        o.hit('brake drum', tl, 112, gain=0.3, pan=right)
    for th, a0, b0 in hops_:
        o.hoof(th + 0.6, pan_at(b0), 90, 0.6)                          # he lands
    o.hit('cymbal swell', T_NOTHUNG - 2.2, 96, gain=0.35, pan=cave)
    o.clash(T_HEART, cave, 127, 1.2)                                   # the sword driven into the heart
    o.boom(T_HEART + 0.02, cave, 1.0)
    o.hit('crash', T_HEART, 124, gain=0.7, pan=cave)
    o.thunder(T_HEART + 0.8, near=0.45, pan=cave, gain=0.9)            # the dragon's death rattle
    o.hit('gong scrape', T_HEART + 3.0, 100, gain=0.5, pan=cave)
    o.hit('gong', BAR[1099], 90, gain=0.35, pan=cave)
    # the effects lead through the fight, step back for the trumpet's Nothung, return for the blow, then settle
    o.effects([(0, -2), (T_NOTHUNG - 0.3, -2), (T_NOTHUNG + 0.2, -9), (T_HEART - 0.4, -9), (T_HEART - 0.1, 0),
               (T_HEART + 5, 0), (T_CALL[0], -10)])
