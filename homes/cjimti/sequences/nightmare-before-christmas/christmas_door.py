"""Through the Christmas Door: a pale figure (a bright head with two dark eyes on a dimmer body) walks in
from the free right end through a dim grey-green wood. Holiday doors glow round the house as he passes
and the one over the porch is a green tree with a red ornament. It swings open, a whirl of red, green,
gold and white rushes in from both ends, and he tumbles through into Christmas Town: snow on deep blue
and a roofline of dark, unlit bulbs. Then a waltz, and a wonder number in five verses, every move on
its beat:

1. He hops toward the right wing, a hop a bar, pokes the first bulb (it pings on and he jumps back),
   pokes two more, and the rest of the wing chain-reacts on out to the free end.
2. A snowball flies in off the free right end and smacks him; he tumbles head over heels back to the
   porch, shakes the snow off, and throws one back that poofs off the end.
3. A toy train toots in off the free right end, chugging puffs on every beat; he hops onto the last
   car as it passes the porch and rides it away round the house and off the far end.
4. The train comes round again off the free right end and parks on Porch Left; he hops off along the
   left wing where four presents sit, and opens them one a bar: a jack-in-the-box, a fountain of gold
   sparkles, a bouncing ball, and a big red bow that sets every bulb on the left wing (and Side) going.
5. He hops home to the porch while its bulbs light around him, waltzes in a spin as the colours chase
   round the house, and on the last bar leaps as a gold star bursts out from the porch to both ends.

Characters are drawn as spans in path distance with exact span-over-pixel coverage, like Bone Yard;
every time is on the waltz grid (bar(k, beat)) that score() shares."""
import numpy as np
from pixelhome.fx import DT, hexc, light, smoothstep, keys, lerp, nframes

CODE = 'NB03'
TITLE = 'Through the Christmas Door'
KIND = 'show'
DESCRIPTION = ('He tumbles through a door shaped like a Christmas tree and waltzes through Christmas Town, '
               'poking bulbs on, dodging snowballs, riding a toy train and opening presents.')

WOODS = hexc('#28503a')
FIGURE = hexc('#eef2ff')
FROSTY = hexc('#bcd8ff')
DOORS = [hexc(c) for c in ('#ff2a6a', '#20e040', '#b080ff', '#3060ff', '#c05a10')]
TREE = hexc('#10c030')
RED = hexc('#ff1010')
SNOW = hexc('#e8f0ff')
NIGHT = hexc('#1a2c90')
GLASS = hexc('#fff0d8')
GOLD = hexc('#ffb020')
BULBS = [hexc(c) for c in ('#ff1a10', '#10d040', '#ffb020', '#2050ff', '#ff5a00')]
SWIRL = [hexc(c) for c in ('#ff1a10', '#10d040', '#ffc040', '#ffffff')]
TRAIN = [hexc(c) for c in ('#ff1a10', '#10c040', '#ffb020', '#2a5aff')]
GIFTS = [hexc(c) for c in ('#ff1a10', '#10c040', '#ffb020', '#2a5aff')]
SPRING = hexc('#40ff60')
BALL = hexc('#3a7aff')

DOOR = 14.0                                 # he reaches the tree door and it swings open
SWIRL_T = (15.0, 18.4)                      # the whirl in; the burst at its end
LAND = 18.8                                 # he drops into Christmas Town
DOOR_OFF = np.array([-1250, -820, -420, 430, 830])     # holiday doors, from the porch along the roof
BPM = 150
BEAT = 60 / BPM                             # a waltz: three beats a bar
BAR = 3 * BEAT
T0 = 22.0                                   # bar 0 of the waltz
D = T0 + 40 * BAR + 2.0
BW = 24.0                                   # bulb spacing

# the story, in bars of the waltz
HOPS = 4                                    # bars 0-3: a hop a bar toward the right wing
POKES = (4, 5, 6)                           # a bulb poked on each downbeat; the first makes him jump back
CHAIN_R = 7                                 # the rest of the right wing chain-reacts, one bulb every CHAIN_DT
CHAIN_DT = 0.1
THROWN, SPLAT = 9, 10                       # the snowball leaves the free end; it hits him
TUMBLE = (10, 12)                           # he tumbles back to the porch
SHAKE = 12
BACK = (13, 2)                              # bar, beat: he throws one back; it poofs off the end a bar later
TRAIN_IN, HOP_ON, GONE = 16, 20, 23        # the train comes in off the free right end heading round the house;
                                            # he hops on the last car at the porch; gone off the far end
TRAIN_AGAIN, PARKED = 23.5, 25.5            # it comes round again off the free right end and parks on Porch Left
GIFT_BARS = (26, 27, 28, 29)                # a hop to each present, opened on beat 3 of the bar
CHAIN_LS_DT = 0.07                          # the bow sets the left wing and Side going
HOME = (30, 33)                             # hops home to the porch; the porch bulbs light from bar 32
PORCH_DT = 0.05
SPIN = (33, 39)                             # waltzing in a spin while the colours chase round
STAR = 39                                   # the leap and the gold star

HEAD, NECK, BODY = 20.0, 4.0, 32.0          # the figure, in layout units
TRAIN_CARS = [(0, 6, 'lamp'), (6, 40, 0), (46, 74, 1), (80, 108, 2), (114, 142, 3)]   # back from the front,
                                            # which leads toward the low end of the path
LAST_CAR = 128.0                            # front to the last car's middle


def bar(k, beat=0.0):
    return T0 + k * BAR + beat * BEAT


def stage(G):
    """Where things are, and the random parts render() draws, so score() can hit them."""
    rng = np.random.default_rng(47)
    d = G.pd[G.path]
    L = G.length
    mid = float(G.pd[G.seg['Porch Front']].mean())
    rng_of = {n: (float(d[idx].min()), float(d[idx].max())) for n, idx in G.path_segments()}
    right0 = rng_of['Right'][0]
    left0, left1 = rng_of['Left']
    stand = right0 - 40                     # where he pokes from
    gx = left0 + np.array([0.84, 0.62, 0.4, 0.18]) * (left1 - left0)     # in the order he opens them
    park = rng_of['Porch Left'][0] + 20
    v = (L + 10 - (mid - LAST_CAR)) / (bar(HOP_ON) - bar(TRAIN_IN))
    tg = bar(GONE) - bar(HOP_ON)            # then it speeds up, gone off the far end by bar GONE
    acc = 2 * ((mid - LAST_CAR) + 162 - v * tg) / tg ** 2

    # bulbs: centre, run, colour, and when each comes on
    nb = int(L // BW)
    bc = (np.arange(nb) + 0.5) * BW
    seg = np.array([next(n for n, (a, b) in rng_of.items() if c <= b + 3) for c in bc])
    on = np.full(nb, np.inf)
    rb = np.flatnonzero(seg == 'Right')
    for k, j in enumerate(rb[:3]):
        on[j] = bar(POKES[k])
    for k, j in enumerate(rb[3:]):
        on[j] = bar(CHAIN_R) + CHAIN_DT * (k + 1)
    lsb = np.flatnonzero((seg == 'Left') | (seg == 'Side'))
    on[lsb] = bar(GIFT_BARS[3], 2) + CHAIN_LS_DT * np.abs(bc[lsb] - gx[3]) / BW
    pb = np.flatnonzero(np.isin(seg, ('Porch Left', 'Porch Front', 'Porch Right')))
    on[pb] = bar(32) + PORCH_DT * (bc[pb] - bc[pb].min()) / BW
    ph = rng.uniform(0, 2 * np.pi, nb)

    S = 700
    s0 = np.sort(rng.uniform(LAND, D, S))
    spx = rng.integers(0, G.N, S)
    sl = rng.uniform(0.8, 2.0, S)
    sparkle = rng.uniform(-1, 1, (40, 2))   # the gold fountain and the shaken-off snow
    return dict(d=d, L=L, mid=mid, right0=right0, stand=stand, gx=gx, park=park, v=v, acc=acc, bc=bc, seg=seg,
                on=on, ph=ph, snow=(s0, spx, sl), sparkle=sparkle, door_at=mid + DOOR_OFF)


def walker(t, S):
    return keys(t, [(1, S['L']), (12, S['mid'] + 30), (DOOR, S['mid'])])


def train_front(t, S):
    """Path distance of the engine's lamp; the train runs toward the low end of the path."""
    if t < bar(TRAIN_AGAIN):
        u = t - bar(TRAIN_IN)
        a = max(0.0, t - bar(HOP_ON))
        return S['L'] + 10 - S['v'] * u - 0.5 * S['acc'] * a * a
    return keys(t, [(bar(TRAIN_AGAIN), S['L'] + 20), (bar(PARKED), S['park'])])


def hop(u, a, b, up=0.5):
    """A hop from a to b over the first `up` of the bar: position and stretch."""
    w = smoothstep(0, up, u)
    return lerp(a, b, w), 1 + 1.4 * np.sin(np.pi * np.clip(u / up, 0, 1))


def jack(t, S):
    """His centre, head direction, stretch, brightness and frostiness; None when he's not on the roof."""
    mid, stand = S['mid'], S['stand']
    if t < SWIRL_T[0] + 0.5:
        step = (t * 1.6) % 1
        return walker(t, S), 1.0, 1 + 0.25 * np.sin(np.pi * step), keys(t, [(1, 0), (2, 1)]), 0.0
    if t < LAND:
        return None
    if t < T0:
        u = t - LAND
        g = 1 + 1.3 * abs(np.sin(np.pi * u / 0.6)) * np.exp(-u * 1.8)
        dr = 1.0 if (t < 20.8 or 21.2 <= t < 21.6) else -1.0       # looking around: what's this?
        return mid, dr, g, smoothstep(LAND, LAND + 0.3, t), 0.0
    k, u = divmod((t - T0) / BAR, 1)
    k = int(k)
    step = (stand - mid) / HOPS
    if k < HOPS:
        x, g = hop(u, mid + step * k, mid + step * (k + 1))
        return x, 1.0, g, 1.0, 0.0
    if k < THROWN:
        x, g = stand, 1.0
        if k in POKES:
            reach = 10 * np.exp(-u * BAR / 0.12)
            jump = (-30 * smoothstep(0, 0.15, u) * (1 - smoothstep(0.4, 0.95, u))) if k == POKES[0] else 0
            x = stand + reach + jump
            g = 1 + (0.8 * np.exp(-u * BAR / 0.2) if k == POKES[0] else 0)
        elif k >= CHAIN_R:
            g = 1 + 0.9 * np.exp(-((u * 3) % 1) * BEAT / 0.15)               # jumping for joy on every beat
        return x, 1.0, g, 1.0, 0.0
    if k < TUMBLE[0]:
        return stand, 1.0, 1.0, 1.0, 0.0
    if k < SHAKE:
        v = (t - bar(TUMBLE[0])) / (bar(TUMBLE[1]) - bar(TUMBLE[0]))
        x = lerp(stand, mid, 1 - (1 - v) ** 2)
        dr = 1.0 if int(v * 13) % 2 == 0 else -1.0                           # head over heels
        g = 1 + 0.6 * abs(np.sin(np.pi * 6 * v))
        return x, dr, g, 1.0, 1.0
    if k < BACK[0] + 3:
        frost = 1 - smoothstep(bar(SHAKE), bar(SHAKE + 1), t)
        x = mid + (4 * np.sin(2 * np.pi * 9 * t) if k == SHAKE else 0)
        g = 1.0
        if k == BACK[0]:
            g = 1 + 0.8 * smoothstep(0, 0.6, u) * (1 - smoothstep(0.66, 0.75, u))  # winds up, throws
        elif k > BACK[0]:
            g = 1 + 0.5 * np.exp(-((u * 3) % 1) * BEAT / 0.1)                  # a laugh on every beat
        return x, 1.0, g, 1.0, frost
    if t < bar(HOP_ON):
        return mid, 1.0, 1 + 0.3 * np.exp(-((u * 3) % 1) * BEAT / 0.1), 1.0, 0.0
    if t < bar(TRAIN_AGAIN):
        x = train_front(t, S) + LAST_CAR
        g = 1 + 1.4 * np.sin(np.pi * np.clip((t - bar(HOP_ON)) / (BAR / 2), 0, 1))
        return (x, -1.0, g, 1.0, 0.0) if x > -30 else None
    if t < bar(GIFT_BARS[0]):
        x = train_front(t, S) + LAST_CAR
        return (x, -1.0, 1.0, 1.0, 0.0) if x < S['L'] + 30 else None
    gx = S['gx']
    if k <= GIFT_BARS[-1]:
        j = k - GIFT_BARS[0]
        a = (S['park'] + LAST_CAR) if j == 0 else gx[j - 1] + 42
        x, g = hop(u, a, gx[j] + 42)
        if j == 0 and u >= 2 / 3:                                            # the jack-in-the-box: jumps back
            x += 26 * np.exp(-(u - 2 / 3) * BAR / 0.3)
            g = 1 + 0.8 * np.exp(-(u - 2 / 3) * BAR / 0.2)
        return x, -1.0, g, 1.0, 0.0
    if k < HOME[0]:
        return gx[-1] + 42, -1.0, 1 + 0.9 * np.exp(-((u * 3) % 1) * BEAT / 0.15), 1.0, 0.0
    if k < HOME[1]:
        n = HOME[1] - HOME[0]
        j = k - HOME[0]
        a = lerp(gx[-1] + 42, mid, j / n)
        b = lerp(gx[-1] + 42, mid, (j + 1) / n)
        x, g = hop(u, a, b)
        return x, 1.0, g, 1.0, 0.0
    if k < STAR:
        b = (u * 3) % 1
        dr = 1.0 if int(u * 3) % 2 == 0 else -1.0                            # a spin a beat
        return mid, dr, 1 + 0.7 * np.exp(-b * BEAT / 0.15) * (int(u * 3) == 0), 1.0, 0.0
    v = t - bar(STAR)
    return mid, 1.0, 1 + 2.2 * np.sin(np.pi * np.clip(v / 0.9, 0, 1)), 1.0, 0.0


def blob(x, c, w):
    return np.exp(-((x - c) / w) ** 2)


def span(sp, a, z, I, c):
    sp.append((min(a, z), max(a, z), I, c))


def figure(sp, x, dr, g, I, c):
    body = BODY * (1 + 0.25 * (g - 1))
    tot = HEAD + NECK * g + body
    base = x - dr * tot / 2
    span(sp, base, base + dr * body, 0.5 * I, c)
    h0 = base + dr * (body + NECK * g)
    span(sp, h0, h0 + dr * HEAD, 1.0 * I, c)
    for e0, e1 in ((4.5, 8.5), (11.5, 15.5)):
        span(sp, h0 + dr * e0, h0 + dr * e1, -0.95 * I, c)


def render(G, seed=47):
    S = stage(G)
    d, L, mid = S['d'], S['L'], S['mid']
    r = np.abs(d - mid)
    w = np.gradient(d)
    e0, e1 = d - w / 2, d + w / 2
    PAL = [FIGURE, FROSTY, SNOW, GOLD, SPRING, BALL, RED, GLASS] + TRAIN + GIFTS
    TR0, GF0 = 8, 12                        # palette offsets of the train and gift colours
    s0, spx, sl = S['snow']
    bc, on, ph = S['bc'], S['on'], S['ph']
    bulb = np.clip((d // BW).astype(int), 0, len(bc) - 1)
    shape = np.clip(1 - np.abs(d - bc[bulb]) / 6, 0, 1)

    F = nframes(D)
    out = np.zeros((F, G.N, 3))
    puffs = []
    for f in range(F):
        t = f * DT
        fr = np.zeros((G.N, 3))
        sp = []
        woods = keys(t, [(0, 0), (2, 0.17), (14, 0.17), (16, 0)])
        fr += light(WOODS, woods * (1 + 0.3 * np.sin(d / 45 + 0.3 * t)))

        # the doors, and the tree door that swallows him
        if t < 16:
            at = walker(t, S)
            for k, (c, col) in enumerate(zip(S['door_at'], DOORS)):
                near = np.exp(-((at - c) / 220) ** 2)
                fr += light(col, keys(t, [(1 + 0.4 * k, 0), (3 + 0.4 * k, 0.28), (14, 0.28), (15, 0)]) *
                            (1 + 0.6 * near) * blob(d, c, 22))
            wide = keys(t, [(DOOR, 22), (DOOR + 1.5, 140)])
            tree = keys(t, [(2, 0), (4, 0.32), (12, 0.45), (DOOR, 0.7), (16, 0.7), (16.5, 0)])
            fr += light(TREE, tree * np.clip(1 - r / wide, 0, 1) ** 0.7)
            fr += light(RED, tree * 0.9 * blob(d, mid, 5) * (t < DOOR + 0.5))
        sw = keys(t, [(SWIRL_T[0], 0), (SWIRL_T[0] + 1, 0.55), (SWIRL_T[1] - 0.4, 0.7), (SWIRL_T[1], 0)])
        if sw > 0:
            band = ((r + 1100 * t) // 60).astype(int) % 4
            stripe = 0.5 + 0.5 * np.sin((r + 1100 * t) / 60 * 2 * np.pi)
            for k, col in enumerate(SWIRL):
                fr += light(col, sw * stripe * (band == k) * smoothstep(1700, 200, r))
        if SWIRL_T[1] <= t < SWIRL_T[1] + 2.6:
            u = t - SWIRL_T[1]
            fr += light(SNOW, 0.8 * np.exp(-u / 0.6) * blob(r, 0, 300 + 1500 * u))

        # Christmas Town: night, snow, bulbs
        end = keys(t, [(D - 1.6, 1), (D, 0)])
        if t >= SWIRL_T[1]:
            fr += light(NIGHT, keys(t, [(SWIRL_T[1], 0), (20, 0.14)]) * end * np.ones(G.N))
            live = (s0 <= t) & (t < s0 + sl)
            u = (t - s0[live]) / sl[live]
            sn = np.zeros(G.N)
            np.maximum.at(sn, spx[live], 0.4 * np.sin(np.pi * u) ** 2)
            fr += light(SNOW, sn * end)
        if t >= LAND:
            lit = t >= on
            pop = np.where(lit, 0.5 * np.exp(-(t - on) / 0.25), 0)
            I = np.where(lit, 0.55, 0.07) + pop
            k = int((t - T0) // BAR)
            shift = 0
            if SPIN[0] <= k < STAR:
                shift = k - SPIN[0]
                I = I * (0.85 + 0.25 * np.exp(-(((t - T0) / BAR) % 1) * BAR / 0.25)) * \
                    (1 + 0.1 * np.sin(2 * np.pi * 0.8 * t + ph))
            if t >= bar(STAR):
                I = I + 0.35 * np.exp(-(t - bar(STAR)) / 0.8)
            Ip = (I * smoothstep(LAND, LAND + 0.6, t) * end)[bulb] * shape
            cols = np.array([BULBS[(j + shift) % len(BULBS)] for j in range(len(bc))])
            colp = np.where(lit[bulb][:, None], cols[bulb], GLASS)
            fr += (np.clip(Ip, 0, None) ** 2.2)[:, None] * colp

        # the snowballs
        if bar(THROWN) <= t < bar(SPLAT):
            x = lerp(L + 10, S['stand'] + 20, (t - bar(THROWN)) / BAR)
            span(sp, x - 7, x + 7, 0.95, 2)
        if bar(SPLAT) <= t < bar(SPLAT) + 0.8:
            u = (t - bar(SPLAT)) / 0.8
            for q in range(10):
                x = S['stand'] + 20 + (q - 4.5) * 14 * (0.3 + u * 3)
                span(sp, x - 2.5, x + 2.5, 0.9 * (1 - u), 2)
        if bar(SHAKE) <= t < bar(SHAKE + 1):
            u = (t - bar(SHAKE)) / BAR
            for a, b in S['sparkle'][:16]:
                x = mid + a * 90 * u + 6 * b
                span(sp, x - 2, x + 2, 0.7 * (1 - u) * (0.5 + 0.5 * np.sin(40 * t + 7 * b)), 2)
        tb = bar(*BACK)
        if tb <= t < tb + BAR:
            x = lerp(mid + 20, L + 12, (t - tb) / BAR)
            span(sp, x - 7, x + 7, 0.95, 2)
        if tb + BAR <= t < tb + BAR + 0.7:
            u = (t - tb - BAR) / 0.7
            fr += light(SNOW, 0.7 * (1 - u) * blob(d, L, 25 + 70 * u))

        # the train
        if bar(TRAIN_IN) <= t:
            fx = train_front(t, S)
            moving = t < bar(PARKED)
            for a, b, c in TRAIN_CARS:
                lo, hi = fx + a, fx + b
                if hi < -5 or lo > L + 5:
                    continue
                if c == 'lamp':
                    span(sp, lo, hi, 1.0, 3)
                else:
                    span(sp, lo, hi, 0.5 if c else 0.6, TR0 + c)
                    for q in (0.25, 0.75):                                   # wheels glint as they turn
                        wq = lo + q * (hi - lo)
                        span(sp, wq - 1.5, wq + 1.5, 0.35 * (np.sin(30 * t + wq) > 0) * moving, 7)
            k = int((t - T0) / BEAT)
            if moving and (not puffs or puffs[-1][0] != k):
                puffs.append((k, fx + 14, t))
        for k, x, t0 in puffs:
            u = (t - t0) / 1.2
            if 0 <= u < 1 and -10 < x < L + 10:
                fr += light(SNOW, 0.35 * (1 - u) * blob(d, x + 20 * u, 8 + 18 * u))

        # the presents and what comes out of them
        gx = S['gx']
        for j, x in enumerate(gx):
            topen = bar(GIFT_BARS[j], 2)
            if t < bar(TRAIN_AGAIN) + 0.3 * j or t >= topen + 0.6:
                continue
            I = 0.42 if t < topen else 0.42 + 0.6 * (1 - (t - topen) / 0.6)
            span(sp, x - 13, x + 13, I, GF0 + j)
            span(sp, x - 2, x + 2, 0.4, 3)
        t1 = bar(GIFT_BARS[0], 2)
        if t1 <= t < t1 + 2.5:                                               # the jack-in-the-box
            u = t - t1
            reach = (16 + 26 * smoothstep(0, 0.08, u) + 10 * np.sin(2 * np.pi * 4 * u) * np.exp(-u * 2.2)) * \
                (1 - smoothstep(1.9, 2.4, u))
            x = gx[0]
            for q in range(5):
                zq = x + 2 + reach * (q + 0.5) / 5
                span(sp, zq - 1.5, zq + 1.5, 0.6, 4)
            span(sp, x + reach, x + reach + 9, 0.9, 4)
        t2 = bar(GIFT_BARS[1], 2)
        if t2 <= t < t2 + 1.6:                                               # the fountain
            u = t - t2
            for a, b in S['sparkle']:
                x = gx[1] + a * 110 * (1 - np.exp(-u * 3))
                tw = 0.5 + 0.5 * np.sin(30 * u + 11 * b)
                span(sp, x - 1.8, x + 1.8, 0.9 * (1 - u / 1.6) * tw, 3)
        t3 = bar(GIFT_BARS[2], 2)
        if t3 <= t < t3 + 3.0:                                               # the ball bounces off down the wing
            u = t - t3
            x = gx[2] - 260 * (1 - np.exp(-u / 1.1))
            hit = np.exp(-((u % 0.45) / 0.07))
            span(sp, x - 5, x + 5, (0.55 + 0.4 * hit) * (1 - smoothstep(2.4, 3.0, u)), 5)
        t4 = bar(GIFT_BARS[3], 2)
        if t4 <= t < t4 + 0.9:                                               # the bow
            u = (t - t4) / 0.9
            fr += light(RED, 0.85 * (1 - u) * blob(d, gx[3], 20 + 120 * u))

        # him
        j = jack(t, S)
        if j is not None:
            x, dr, g, I, frost = j
            figure(sp, x, dr, g, I * (0.75 + 0.25 * min(g, 2) / 2) * (0.6 if t < SWIRL_T[0] else 1.0) * end,
                   1 if frost > 0.5 else 0)

        # the star
        if t >= bar(STAR):
            u = t - bar(STAR)
            fr += light(GOLD, 0.9 * np.exp(-u / 1.2) * blob(r, 650 * u, 90) * end)
            fr += light(GOLD, 0.6 * np.exp(-u / 0.5) * blob(r, 0, 60) * end)

        if sp:
            a = np.array(sp)
            ov = np.clip(np.minimum(a[:, 1:2], e1) - np.maximum(a[:, 0:1], e0), 0, None) / w
            for c in np.unique(a[:, 3]).astype(int):
                m = a[:, 3] == c
                fr += light(PAL[c], np.clip(a[m, 2] @ ov[m], 0, 1))
        out[f][G.path] = np.clip(fr, 0, 1)
    return out


# ---- music: the woods are D minor and hushed (a ghostly pad, a pizz footfall on each step, a small sound for
# each holiday door as it lights, a curious music-box question at the tree door). The door swallows him in a
# whoosh and a long falling slide whistle; a bell tree for the burst; boings as he bounces. Then a waltz in
# F major at BPM: TUNE is its A strain (music box, then clarinet, then the whole band), TUNE_B its B strain
# (flute, then glock). Pizz bass on one, harp on two and three, sleigh bells. Every bulb that comes on is a
# glock ping where it is, higher up the F major pentatonic as a chain runs; snowballs whoosh and splat; the
# train toots and chugs on the beat; each present has its own sound; the star is the big chord. ----

TUNE = [                                    # (beat, note, beats): the A strain, eight bars of three
    (0, 'A4', 1), (1, 'C5', 1), (2, 'F5', 1), (3, 'E5', 1.5), (4.5, 'D5', .5), (5, 'C5', 1),
    (6, 'D5', 1), (7, 'Bb4', 1), (8, 'G4', 1), (9, 'C5', 3),
    (12, 'A4', 1), (13, 'C5', 1), (14, 'F5', 1), (15, 'G5', 1.5), (16.5, 'F5', .5), (17, 'E5', 1),
    (18, 'D5', 1), (19, 'E5', 1), (20, 'C5', 1), (21, 'F5', 3)]
TUNE_B = [
    (0, 'D5', 1), (1, 'D5', .5), (1.5, 'E5', .5), (2, 'F5', 1), (3, 'C5', 2), (5, 'A4', 1),
    (6, 'B4', 1), (7, 'C5', 1), (8, 'D5', 1), (9, 'C5', 3),
    (12, 'D5', 1), (13, 'D5', .5), (13.5, 'E5', .5), (14, 'F5', 1), (15, 'A5', 2), (17, 'F5', 1),
    (18, 'E5', 1), (19, 'D5', 1), (20, 'E5', 1), (21, 'F5', 3)]
A_CH = ['F', 'C', 'Gm', 'C', 'F', 'C', 'C7', 'F']
B_CH = ['Bb', 'F', 'G7', 'C', 'Bb', 'F', 'C', 'F']
VOICE = {'F': ('F3', 'A3', 'C4'), 'C': ('E3', 'G3', 'C4'), 'Gm': ('D3', 'G3', 'Bb3'), 'C7': ('E3', 'G3', 'Bb3'),
         'Bb': ('D3', 'F3', 'Bb3'), 'G7': ('D3', 'F3', 'B3')}
ROOT = {'F': 'F2', 'C': 'C2', 'Gm': 'G2', 'C7': 'C2', 'Bb': 'Bb1', 'G7': 'G2'}
PENTA = ['F5', 'G5', 'A5', 'C6', 'D6', 'F6']


def score(M, G):
    from pixelhome.audio import SR, note as n, slide, whoosh
    S = stage(G)
    L, mid, gx = S['L'], S['mid'], S['gx']
    d = S['d']
    xs = G.pos[G.path, 0]
    x0, x1 = xs.min(), xs.max()

    def pan_at(q):
        return float(0.85 * (2 * (np.interp(q, d, xs) - x0) / (x1 - x0) - 1))

    box = M.synth('Plucks/Magic Music Box')
    ghost = M.synth('Pads/Ghost Pad')
    pizz = M.sampler('Strings/Solo Contrabass/Pizz/*.wav', tune=-12)
    cpizz = M.sampler('Strings/Cello Section/pizzT/*.wav', tune=-12)
    harp = M.sampler('Strings/Harp/*.wav')
    glock = M.sampler('Percussion/Glock/*.wav', tune=-12)
    xylo = M.sampler('Percussion/Xylo/*.wav', tune=-12)
    mar = M.sampler('Percussion/Marimba/*.wav', tune=-12)
    flute = M.sampler('Woodwinds/Flute/susvib/*.wav', tune=-12)
    fl_st = M.sampler('Woodwinds/Flute/stac/*.wav', tune=-12)
    clar = M.sampler('Woodwinds/Clarinet/stac/*.wav', tune=-12)
    bsn = M.sampler('Woodwinds/Bassoon/stac/*.wav', tune=-12)
    vln = M.sampler('Strings/Violin Section/susVib/*.wav', tune=-12)
    horn = M.sampler('Brass/F Horn/sus/*.wav', tune=-12)
    sleigh = M.hits('Percussion/Sleighbells_Hit*.wav')
    tree = M.hits('Percussion/BellTree_Stroke*.wav')
    tamb = M.hits('Percussion/Tamb1-Hit*.wav')
    shake = M.hits('Percussion/Tamb1-Shake*.wav')
    maraca = M.hits('VSCO 1 Percussion/varWood/maraca[1-5].wav')
    wood = M.hits('VSCO 1 Percussion/varWood/wood_click*.wav')
    slap = M.hits('VSCO 1 Percussion/varWood/slapstick[0-9].wav')
    guiro = M.hits('VSCO 1 Percussion/varWood/guiro_long*.wav')
    crash = M.hits('VSCO 1 Percussion/varMetal/Cymbals/clash/crash_hit_ff*.wav')
    choke = M.hits('Percussion/cymbal-crashshort*.wav')
    ccresc = M.hits('Percussion/susCymb1-cresc-Short*.wav')
    timp = M.hits('Percussion/Timpani/Timpani1_Hit*.wav')
    troll = M.hits('Percussion/Timpani/Rolls/*.wav')
    tri = M.hits('Percussion/Triangle3-Hit_v1*.wav')
    for name, gain, rev in (('bass', 0.42, 0.08), ('harp', 0.3, 0.25), ('tune', 0.3, 0.25), ('box', 0.3, 0.3),
                            ('bells', 0.16, 0.25), ('ping', 0.2, 0.3), ('fx', 0.22, 0.2), ('perc', 0.3, 0.15),
                            ('pad', 0.16, 0.45), ('band', 0.2, 0.25)):
        M.bus(name, gain=gain, reverb=rev)
    boxn = []

    def mono(sig, p):
        a = (np.clip(p, -1, 1) + 1) * np.pi / 4
        return np.vstack([sig * np.cos(a), sig * np.sin(a)]) * np.sqrt(2)

    def toot(t, p, gain=1.0):               # a toy steam whistle: a sour little chord with a puff of breath
        sec = 0.55
        u = np.arange(int(sec * SR)) / SR
        env = np.clip(u / 0.03, 0, 1) * np.clip((sec - u) / 0.12, 0, 1)
        sig = sum(np.sin(2 * np.pi * f * u * (1 + 0.004 * np.sin(2 * np.pi * 6 * u))) for f in (587, 740, 880))
        sig += 0.3 * np.convolve(M.rng.normal(0, 1, len(u)), np.ones(12) / 12, 'same')
        M.add('fx', mono(0.25 * env * sig, p), t, gain)
        M.add('fx', mono(0.25 * env * sig, p), t + 0.65, gain * 0.8)

    def ping(t, k, p, vel=90):
        M.add('ping', glock.play(n(PENTA[k % len(PENTA)]), vel), t, 1.0, p)

    # ---- the woods ----
    M.add('pad', ghost.render([(0.5, n('D3'), 62, 14.5), (0.5, n('A3'), 56, 14.5), (5.0, n('F4'), 48, 10.0)], D), 0)
    t = 1.0
    k = 0
    while t < DOOR:
        M.add('perc', cpizz.play(n('D2') if k % 2 == 0 else n('A2'), 58), t, 0.8, pan_at(walker(t, S)))
        t += 1 / 1.6
        k += 1
    door_snd = [(harp, 'A4'), (fl_st, 'E5'), (mar, 'C5'), (glock, 'G5'), (bsn, 'D3')]
    for k, (c, (inst, m)) in enumerate(zip(S['door_at'], door_snd)):
        M.add('tune', inst.play(n(m), 80), 2 + 0.4 * k, 0.6, pan_at(c))
    for j, m in enumerate(('C5', 'E5', 'G5', 'Bb5')):                       # what's that?
        boxn.append((DOOR - 1.6 + 0.4 * j, n(m), 76, 0.5))

    # ---- the whirl, the burst, the landing ----
    a, b = SWIRL_T
    M.add('fx', whoosh(b - a, 300, 3000, 0.5, seed=3), a, 0.6)
    M.add('fx', slide(0.0, b - a - 0.2, 1600, 300, b - a, 0.35, shape=0.7), a, 0.7, 0.0)
    r = troll.play(90, dur=b - a)
    M.add('perc', r * np.linspace(0.1, 1, r.shape[1]) ** 2, a, 0.6)
    M.add('perc', ccresc.play(100, dur=b - a + 0.05), a, 0.4)
    M.add('perc', tree.play(110), b, 1.0)
    M.add('perc', crash.play(80), b, 0.4)
    for j, m in enumerate(('F6', 'C6', 'A5', 'F5', 'C5')):
        M.add('ping', glock.play(n(m), 95), b + 0.06 * j, 0.8, 0.0)
    for j in range(4):                                                      # boing, boing, boing
        tb = LAND + 0.6 * (j + 1)
        if tb >= T0 - 0.3:
            break
        M.add('perc', wood.play(100 - 20 * j), tb, 0.8)
        M.add('fx', slide(0.0, 0.18, 500 - 60 * j, 900 - 100 * j, 0.22, 0.3), tb, 0.6 - 0.12 * j)
    for tq, m in ((20.8, 'E4'), (21.2, 'G4'), (21.6, 'B4')):                # huh? huh?
        M.add('tune', cpizz.play(n(m), 85), tq, 0.9, 0.0)
    M.add('tune', fl_st.play(n('C5'), 90), bar(-1, 2), 0.7)                # the pickup into the waltz

    # ---- the waltz: bass, harp and sleigh bells under all 40 bars ----
    for k in range(40):
        c = (A_CH if (k // 8) % 2 == 0 else B_CH)[k % 8]
        M.add('bass', pizz.play(n(ROOT[c]), 100), bar(k), 1.0, -0.1)
        for bt in (1, 2):
            for m in VOICE[c]:
                M.add('harp', harp.play(n(m) + 12, 70 if bt == 1 else 62), bar(k, bt), 0.5, 0.25)
            if k >= 8:
                M.add('bells', sleigh.play(70 if bt == 1 else 58), bar(k, bt), 0.8, 0.3)

    def strain(tune, k0, inst, bus, vel, gain=1.0, shift=0, p=0.0, legato=0.9, synth=False):
        for bt, m, ln in tune:
            t = bar(k0) + bt * BEAT
            if synth:
                boxn.append((t, n(m) + shift, vel, ln * BEAT * legato))
            else:
                M.add(bus, inst.play(n(m) + shift, vel, dur=ln * BEAT * legato), t, gain, p)

    # verse 1: hops, pokes, the chain on the right wing
    strain(TUNE, 0, None, 'box', 88, synth=True)
    strain(TUNE, 0, glock, 'ping', 60, gain=0.35)
    step = (S['stand'] - mid) / HOPS
    for k in range(HOPS):
        x = mid + step * (k + 1)
        M.add('perc', wood.play(90), bar(k, 1.5), 0.7, pan_at(x))
        M.add('fx', slide(0.0, 0.3, 600, 1100, 0.32, 0.2), bar(k), 0.5, pan_at(x))
    bc, on = S['bc'], S['on']
    rb = np.flatnonzero(S['seg'] == 'Right')
    for j, i in enumerate(rb):
        ping(on[i], j if j >= 3 else 3, pan_at(bc[i]), 110 if j < 3 else 80)
    M.add('fx', slide(0.0, 0.15, 700, 1700, 0.2, 0.4), bar(POKES[0]), 0.7, pan_at(S['stand']))   # eek!
    for k in (CHAIN_R, CHAIN_R + 1):
        for bt in range(3):
            M.add('perc', tamb.play(90), bar(k, bt), 0.6, pan_at(S['stand']))

    # verse 2: the snowball fight
    strain(TUNE_B, 8, flute, 'tune', 92, legato=1.0)
    M.add('fx', whoosh(BAR, 800, 2400, 0.4, seed=9), bar(THROWN), 0.6, 0.6)
    ps = pan_at(S['stand'])
    hit = M.rng.normal(0, 1, int(0.3 * SR)) * np.exp(-np.arange(int(0.3 * SR)) / SR / 0.05)
    M.add('fx', mono(1.2 * hit, ps), bar(SPLAT), 0.8)
    M.add('perc', slap.play(120), bar(SPLAT), 1.0, ps)
    M.add('perc', choke.play(100), bar(SPLAT), 0.6, ps)
    span_t = bar(TUMBLE[1]) - bar(TUMBLE[0])
    M.add('fx', slide(0.0, span_t, 1500, 400, span_t, 0.3, shape=0.6), bar(TUMBLE[0]), 0.8, (ps + pan_at(mid)) / 2)
    for j in range(1, 7):
        v = j / 6
        x = lerp(S['stand'], mid, 1 - (1 - v) ** 2)
        M.add('perc', wood.play(100 - 6 * j), bar(TUMBLE[0]) + v * span_t, 0.8, pan_at(x))
    M.add('perc', shake.play(100), bar(SHAKE), 0.9, pan_at(mid))
    M.add('bells', sleigh.play(110), bar(SHAKE, 1), 1.0, pan_at(mid))
    tb = bar(*BACK)
    M.add('fx', whoosh(BAR, 2000, 700, 0.4, seed=11), tb, 0.6, 0.6)
    M.add('fx', mono(0.6 * hit, 0.85), tb + BAR, 0.6)
    for j, m in enumerate(('A5', 'G5', 'F5')):                              # hee hee hee
        M.add('ping', xylo.play(n(m), 95), tb + BAR + 0.1 + 0.12 * j, 0.7, 0.85)
    for k in (BACK[0] + 1, BACK[0] + 2):
        for bt in range(3):
            M.add('tune', bsn.play(n('C3') if bt < 2 else n('F2'), 82, dur=0.12), bar(k, bt), 0.5, pan_at(mid))

    # verse 3: the train
    strain(TUNE, 16, clar, 'tune', 100, legato=0.6)
    strain(TUNE, 16, None, 'box', 70, shift=12, synth=True)
    toot(bar(TRAIN_IN), 0.85)
    for k in range(int((bar(TRAIN_AGAIN) - bar(TRAIN_IN)) / (BEAT / 2))):
        t = bar(TRAIN_IN) + k * BEAT / 2
        fx = train_front(t, S)
        if -150 < fx < L + 10:
            M.add('perc', maraca.play(95 if k % 2 == 0 else 60), t, 0.6, pan_at(np.clip(fx + 70, 0, L)))
    M.add('fx', slide(0.0, 0.3, 500, 1300, 0.35, 0.4), bar(HOP_ON), 0.7, pan_at(mid))
    toot(bar(HOP_ON, 1), pan_at(mid - 80))
    tt = np.arange(bar(HOP_ON), bar(TRAIN_AGAIN), 0.01)
    t_out = tt[np.argmax([train_front(t, S) < 0 for t in tt])]      # the lamp reaches the far end
    toot(t_out - 0.6, -0.85, 0.8)

    # verse 4: round again, and the presents
    strain(TUNE_B, 24, glock, 'tune', 92, gain=0.5)
    strain(TUNE_B, 24, fl_st, 'tune', 88, gain=0.8)
    toot(bar(TRAIN_AGAIN), 0.85)
    M.add('perc', guiro.play(90), bar(PARKED) - 0.9, 0.6, pan_at(S['park']))
    for k in range(int((bar(PARKED) - bar(TRAIN_AGAIN)) / (BEAT / 2))):
        t = bar(TRAIN_AGAIN) + k * BEAT / 2
        M.add('perc', maraca.play(90 - 6 * k), t, 0.6, pan_at(np.clip(train_front(t, S) + 70, 0, L)))
    toot(bar(PARKED), pan_at(S['park']), 0.7)
    for j in range(4):
        M.add('perc', wood.play(85), bar(GIFT_BARS[j], 1.5), 0.6, pan_at(gx[j] + 42))
    t1, t2, t3, t4 = (bar(GIFT_BARS[j], 2) for j in range(4))
    M.add('perc', slap.play(120), t1, 1.0, pan_at(gx[0]))                   # the jack-in-the-box
    u = np.arange(int(1.2 * SR)) / SR
    f = 330 * (1 + 0.9 * np.minimum(u / 0.08, 1)) * (1 + 0.12 * np.sin(2 * np.pi * 4 * u) * np.exp(-u * 2.2))
    sig = np.sin(2 * np.pi * np.cumsum(f) / SR) * np.exp(-u * 1.6) * np.clip(u / 0.01, 0, 1)
    M.add('fx', mono(0.35 * sig, pan_at(gx[0])), t1, 0.9)
    for j, m in enumerate(('F5', 'A5', 'C6', 'D6', 'F6', 'A6', 'C7')):     # the fountain
        M.add('ping', glock.play(n(m), 90), t2 + 0.05 * j, 0.6, pan_at(gx[1]))
    M.add('perc', tree.play(100), t2, 0.8, pan_at(gx[1]))
    for j in range(7):                                                      # the ball, bouncing away
        tq = t3 + 0.45 * j
        x = gx[2] - 260 * (1 - np.exp(-0.45 * j / 1.1))
        M.add('ping', mar.play(n('C5') - j, 100 - 9 * j), tq, 0.8, pan_at(x))
    M.add('perc', crash.play(100), t4, 0.6, pan_at(gx[3]))                  # the bow
    for m in VOICE['F']:
        M.add('band', horn.play(n(m), 100, dur=1.0), t4, 0.8, pan_at(gx[3]))
    lsb = np.flatnonzero((S['seg'] == 'Left') | (S['seg'] == 'Side'))
    for j, i in enumerate(lsb[np.argsort(on[lsb])][::2]):
        ping(on[i], j // 2, pan_at(bc[i]), 72)
    for bt in range(3):
        M.add('perc', tamb.play(90), bar(GIFT_BARS[3] + 1, bt), 0.6, pan_at(gx[3]))

    # verse 5: home, the porch lights, the spin and the star
    for k in range(HOME[0], HOME[1]):
        M.add('perc', wood.play(95), bar(k, 1.5), 0.7, pan_at(lerp(gx[-1] + 42, mid, (k - HOME[0] + 1) / 3)))
    pb = np.flatnonzero(np.isin(S['seg'], ('Porch Left', 'Porch Front', 'Porch Right')))
    for j, i in enumerate(pb[::2]):
        ping(on[i], j, pan_at(bc[i]), 70)
    strain(TUNE, 32, vln, 'tune', 92, gain=0.8, legato=1.0)
    strain(TUNE, 32, flute, 'tune', 96, gain=0.7, shift=12, legato=1.0)
    strain(TUNE, 32, None, 'box', 90, synth=True)
    for k in range(SPIN[0], STAR):
        c = A_CH[k % 8]
        M.add('band', horn.play(n(VOICE[c][1]), 80, dur=BAR * 0.95), bar(k), 0.6, -0.2)
        M.add('perc', tri.play(80), bar(k), 0.5, 0.2)
        for bt in range(3):
            M.add('bells', sleigh.play(80), bar(k, bt), 0.8, -0.3)
    ts = bar(STAR)
    M.add('perc', crash.play(120), ts, 1.0)
    M.add('perc', timp.play(120), ts, 0.9)
    M.add('perc', tree.play(120), ts + 0.1, 0.9)
    for m in ('F3', 'A3', 'C4', 'F4'):
        M.add('band', horn.play(n(m), 110, dur=D - ts - 0.6), ts, 0.8)
        M.add('tune', vln.play(n(m) + 12, 100, dur=D - ts - 0.6), ts, 0.5)
    M.add('bass', pizz.play(n('F2'), 120), ts, 1.2)
    for j, m in enumerate(('F4', 'A4', 'C5', 'F5', 'A5', 'C6', 'F6')):
        M.add('harp', harp.play(n(m), 100), ts + 0.04 * j, 0.8)
    M.add('ping', glock.play(n('F6'), 110), ts + 0.3, 0.8)
    M.add('bells', sleigh.play(120), ts + 0.4, 1.0)

    M.add('box', box.render(boxn, D), 0.0)
