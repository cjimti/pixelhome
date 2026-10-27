"""Full Moon: a man walks home late with his lantern, in from the free right end of the house, while
the moon comes up the other way, waxing as it travels from the free back end of Side along the left
wing and round the porch. He stops at the corner to look at it, then fumbles for his keys at the
front door just as it arrives over the porch, full. Moonlight floods the roof, he drops the lantern,
his heart races, fur ripples out over the whole house, everything goes black, and two amber eyes
open. The wolf howls (the howl runs out to both free ends), something answers from the far end of
Side, and he goes after the moon itself: it glides on round the back-right porch corner and he
stalks it, pouncing three times, each leap across a corner, each time the moon skips just out of
reach. The last, longest leap is at the moon over the right wing, and a cloud slides over it while
he is in the air: he changes back mid-leap and lands in a heap with stars round his head. The moon
peeks out once (he bristles), the cloud covers it again, the moon sets off the free end, dawn comes
up from the back of Side, and he trudges home, picks up his lantern and goes in. A moment later two
eyes open at the door and one of them winks.

Everything is placed in path distance (layout units along the roofline) and drawn with exact
span-over-pixel coverage, so the moon, the man and the wolf keep their size on every run. Times are
module constants on a 100 BPM grid (BEAT) that score() shares."""
import numpy as np
from pixelhome.fx import DT, hexc, light, smoothstep, keys, lerp, nframes

CODE = 'HW09'
TITLE = 'Full Moon'
KIND = 'show'
DESCRIPTION = ('A man walks home with his lantern as the moon comes up round the house. It is full when '
               'he reaches his door: he turns into a wolf, howls, and pounces after the moon until a '
               'cloud gets in the way.')

NIGHT = hexc('#1c2c9c')
STAR = hexc('#c8d8ff')
CLOUD = hexc('#5a6a9a')
SILVER = hexc('#c0d0ff')
MOON = hexc('#fff4d8')
HALO = hexc('#7890ff')
WASH = hexc('#8ea8ff')
MAN = hexc('#ffd8a8')
LANTERN = hexc('#ff8a18')
FUR = hexc('#a05a20')
FURG = hexc('#6a6a80')
EYE = hexc('#ffb000')
BLOOD = hexc('#d01008')
HOWL = hexc('#b8c8ff')
DAWN0 = hexc('#ff3860')
DAWN1 = hexc('#ffa040')
DIZZY = hexc('#fff0a0')

BEAT = 0.6                                  # 100 BPM: his walk, the wolf's stalk, the music
W0 = 2.4                                    # beat 0


def beat(k):
    return W0 + k * BEAT


D = 84.0
MOON_IN = beat(3)                           # the moon appears at the free back end of Side
LOOK = (beat(12), beat(15))                 # he stops at the Porch Right/Right corner and looks up
TFULL = beat(33)                            # full moon over the porch
TDROP = TFULL + 1.2                         # the lantern falls
TBLACK = 32.6                               # the house holds its breath
TEYES = beat(52)                            # the eyes open
THOWL = beat(53)                            # the howl
HOWL_LEN = 5.4
TANS = beat(63)                             # an answer from the far end of Side
ANS_LEN = 3.0
TTURN = beat(66)                            # he turns to follow the moon
STALK = [range(67, 71), range(73, 79), range(82, 89)]   # stalking steps, by beat
POUNCE = [beat(71), beat(80), beat(91)]     # three pounces, each across a corner
LEAP = [0.45, 0.45, 0.6]
TCOVER = POUNCE[2] + 0.15                   # the cloud covers the moon mid-leap
TBACK = (POUNCE[2] + 0.18, POUNCE[2] + 0.45)   # changes back in the air
TPEEK = (beat(99), beat(100.5))             # the moon peeks out
TSET = (beat(102), 67.2)                    # the moon sets off the free right end
TDAWN = (65.4, 74.0)
HOME = range(108, 124)                      # walking home, by beat
TPICK = beat(125)                           # picks up the lantern
TIN_K = 127
TIN = beat(TIN_K)                           # goes in
TGAG = beat(130)                            # eyes at the door; one winks
RM = 55.0                                   # moon radius


def heartbeats():
    """Lub times of his racing heart through the change."""
    out, t, iv = [], TFULL + 0.9, 1.0
    while t < TBLACK - 0.15:
        out.append(round(t, 3))
        t += iv
        iv = max(0.28, iv * 0.86)
    return out


HB = heartbeats()


def howl_pitch(tt, scale=1.0):
    """Sounding MIDI pitch of the howl tt seconds in (scale stretches the contour for the answer)."""
    tt = tt / scale
    p = keys(tt, [(0.0, 55.0), (0.35, 62.0), (0.9, 67.0), (2.9, 68.0), (3.6, 66.0), (4.6, 58.0), (5.4, 52.0)])
    depth = 0.35 * smoothstep(1.0, 1.8, tt) * (1 - smoothstep(4.2, 5.0, tt))
    return float(p + depth * np.sin(2 * np.pi * 5.5 * tt * scale))


def howl_amp(tt, scale=1.0):
    return float(keys(tt / scale, [(0.0, 0.0), (0.3, 0.7), (1.0, 1.0), (3.2, 0.95), (4.4, 0.5), (5.4, 0.0)]))


def plan(G):
    """Where everything is: positions in path distance, shared by render() and score()."""
    L = G.length
    pdp = G.pd[G.path]
    pf = G.pd[G.seg['Porch Front']]
    c1 = 0.5 * (pdp[331] + pdp[332])        # back-right porch corner
    c2 = 0.5 * (pdp[380] + pdp[381])        # Porch Right -> Right
    mc = float(pf.mean())                   # the moon's spot over the porch
    xm = float(pf.max()) - 50.0             # his front door
    start = L + 30.0
    sl = (start - xm) / 23
    walk = [(0.0, start)]
    for j in range(1, 24):
        k = j if j <= 12 else j + 2
        walk.append((beat(k), start - sl * j))
    # the wolf: stalk steps, a coil back before each pounce, the leap
    wolf = [(TEYES, xm, 0.3)]
    x = xm
    lands = [c1 + 230.0, c2 + 195.0, c2 + 405.0]
    steps = [7.0, 13.0, 6.0]
    for i in range(3):
        for k in STALK[i]:
            x += steps[i]
            wolf.append((beat(k), x, 0.35))
        wolf.append((POUNCE[i], x - 12.0, 0.5))
        x = lands[i]
        wolf.append((POUNCE[i] + LEAP[i], x, LEAP[i]))
    xl = xm + 30.0                          # where the lantern lands
    home = [(beat(HOME[0] - 1), x, 0.3)]
    hs = (x - (xl + 8)) / len(HOME)
    for j, k in enumerate(HOME):
        home.append((beat(k), x - hs * (j + 1), 0.42))
    moon = [(MOON_IN, -70.0), (TFULL, mc), (beat(64), mc), (beat(68), c1 + 150), (POUNCE[0] - 0.1, c1 + 200),
            (POUNCE[0] + 0.35, c2 + 90), (POUNCE[1] - 0.1, c2 + 150), (POUNCE[1] + 0.35, c2 + 350),
            (POUNCE[2] - 0.1, c2 + 380), (TSET[0], c2 + 400), (TSET[1], L + 90)]
    return dict(L=L, mc=mc, xm=xm, xl=xl, c1=c1, c2=c2, walk=walk, wolf=wolf, home=home, moon=moon, lands=lands)


def track(t, pts, md=None):
    """Position along arrivals [(t, x[, move time]), ...]: hold, then ease into each arrival."""
    x = pts[0][1]
    for p in pts[1:]:
        m = p[2] if len(p) > 2 else md
        if t >= p[0]:
            x = p[1]
            continue
        if t > p[0] - m:
            x = lerp(x, p[1], smoothstep(p[0] - m, p[0], t))
        break
    return x


def moon_at(P, t):
    return float(keys(t, P['moon']))


def _hit(dt, k=0.12):
    return float(np.exp(-dt / k)) if dt >= 0 else 0.0


def _lattice(rng, period, scale):
    n = max(4, int(period / scale))
    lat = rng.uniform(-1, 1, n)

    def f(x):
        u = (np.asarray(x, float) / scale) % n
        i = np.floor(u).astype(int) % n
        fr = u - i
        fr = fr * fr * (3 - 2 * fr)
        return lat[i] * (1 - fr) + lat[(i + 1) % n] * fr
    return f


def render(G, seed=9):
    rng = np.random.default_rng(seed)
    P = plan(G)
    L, mc, xm, xl = P['L'], P['mc'], P['xm'], P['xl']
    pdp = G.pd[G.path]
    w = np.gradient(pdp)
    e0, e1 = pdp - w / 2, pdp + w / 2
    N = G.N

    def cover(a, b):
        a, b = min(a, b), max(a, b)
        return np.clip(np.minimum(b, e1) - np.maximum(a, e0), 0, None) / w

    def blob(c, hw, edge):
        return 1 - smoothstep(hw, hw + edge, np.abs(pdp - c))

    cA = _lattice(rng, 6000, 260)
    cB = _lattice(rng, 6000, 110)
    furA = _lattice(rng, 6000, 11)
    furB = _lattice(rng, 6000, 37)
    stars = np.zeros(N)
    si = rng.choice(N, 34, replace=False)
    stars[si] = rng.uniform(0.18, 0.34, 34)
    tw_f = rng.uniform(0.3, 1.1, N)
    tw_p = rng.uniform(0, 2 * np.pi, N)
    lant_f = rng.uniform(5, 11, 3)
    lant_p = rng.uniform(0, 2 * np.pi, 3)
    m13 = moon_at(P, 13.0)

    def man_x(t):
        if t < TBACK[0]:
            return track(t, P['walk'], 0.42)
        return track(t, P['home'])

    def wolf_x(t):
        return track(t, P['wolf'])

    F = nframes(D)
    out = np.zeros((F, N, 3))
    for fi in range(F):
        t = fi * DT
        fade = smoothstep(0, 2.5, t) * (1 - smoothstep(D - 2.2, D - 0.2, t))
        dawn_g = smoothstep(TDAWN[0], TDAWN[1], t + 0.0 - 3.0 * pdp / L)   # dawn starts at the back of Side
        dawn = smoothstep(TDAWN[0], TDAWN[1], t)
        layers = []

        # ---- the sky: night bed, clouds, stars ----
        amount = keys(t, [(0, 0.9), (18, 0.8), (TFULL - 1, 0.15), (TEYES, 0.1), (TTURN + 2, 0.75), (60, 0.8),
                          (70, 0.6), (78, 0.3)])
        bg = np.clip(2.4 * (0.65 * cA(pdp - 21 * t) + 0.35 * cB(pdp - 34 * t + 500)) - 0.2, 0, 1) * amount
        ca = 0.95 * blob(m13 - 40 * (t - 13.0), 95, 45) if 8 < t < 18 else 0.0       # cloud A crosses the moon
        mx = moon_at(P, t)
        if t >= POUNCE[2] - 1.2:                 # cloud B: comes in over the moon on the last pounce
            off = keys(t, [(POUNCE[2] - 1.2, 520.0), (TCOVER, 0.0), (TPEEK[0], 0.0), (TPEEK[0] + 0.25, 190.0),
                           (TPEEK[1] - 0.25, 190.0), (TPEEK[1], 0.0), (TSET[1], 0.0), (TSET[1] + 4, 600.0)])
            cbd = 0.97 * blob(mx + off, 105, 40)
        else:
            cbd = 0.0
        cd = np.maximum(np.maximum(bg, ca), cbd)
        night = 0.11 * (1 - dawn_g)
        layers.append((NIGHT, night * (1 - 0.45 * cd)))
        tw = stars * (0.75 + 0.25 * np.sin(2 * np.pi * tw_f * t + tw_p))

        # ---- the moon ----
        ph = float(np.clip(keys(t, [(MOON_IN, 0.12), (TFULL, 1.0)]), 0, 1))
        mb = 0.82 + 0.18 * _hit(t - TFULL, 1.2)
        if THOWL <= t < THOWL + HOWL_LEN:
            mb += 0.12 * howl_amp(t - THOWL)
        if t >= TSET[0]:
            mb *= 1 - smoothstep(TSET[0], TSET[1], t) * 0.4
        term = mx - RM + 2 * RM * (1 - ph)
        disc = cover(mx - RM, mx + RM)
        litm = smoothstep(term - 10, term + 10, pdp)
        moon = disc * (0.06 + 0.94 * litm) * mb * (1 - 0.88 * cd) * (t >= MOON_IN - 1)
        dist = np.abs(pdp - mx)
        halo = np.exp(-(np.clip(dist - RM, 0, None) / 85) ** 2) * (1 - disc) * (0.2 * ph * mb) * (t >= MOON_IN - 1)
        layers.append((HALO, halo * (1 - 0.6 * cd)))
        layers.append((CLOUD, cd * (0.06 + 0.2 * ph * (t >= MOON_IN) * (1 - dawn))))
        layers.append((SILVER, cd * np.exp(-(np.clip(dist - RM * 0.6, 0, None) / 70) ** 2) * 0.55 * mb
                       * (t >= MOON_IN - 1)))

        # moonlight flood from the full moon
        r = 950 * max(0.0, t - TFULL)
        flood = 0.17 * smoothstep(-r - 60, -r, -dist) * (t >= TFULL) * (1 - dawn)
        flood *= 1 - 0.85 * smoothstep(TBLACK - 0.05, TBLACK, t) * (1 - smoothstep(TEYES + 0.3, TEYES + 2.5, t))
        layers.append((WASH, flood * (1 - 0.9 * cd)))
        starv = tw * (1 - cd) * (1 - dawn) * (1 - smoothstep(TFULL, TFULL + 1.5, t) * (1 - smoothstep(TTURN, 50, t)) * 0.7)

        # ---- the change: heartbeat, fur over the house, blackout ----
        fg = np.zeros(N)                         # foreground occlusion
        fgl = []
        nb = sum(1 for h in HB if h <= t)
        if TFULL <= t < TBLACK:
            g = (nb + (smoothstep(0, 0.18, t - HB[nb - 1]) if nb else 0) - 1) / len(HB) if nb else 0.0
            g = max(0.0, g)
            pulse = 0.0
            for h in HB[max(0, nb - 2):nb]:
                pulse = max(pulse, np.exp(-(t - h) / 0.09) + 0.7 * _hit(t - h - 0.17, 0.1))
            reach = 1900 * smoothstep(TFULL + 2.0, TBLACK - 0.6, t) ** 1.5
            dd = np.abs(pdp - xm)
            ripple = 0.5 + 0.5 * np.sin(2 * np.pi * (dd / 95 - 1.7 * (t - TFULL)))
            tex = 0.6 + 0.4 * furA(pdp + 5 * np.sin(2 * np.pi * 9 * t)) * (0.7 + 0.3 * furB(pdp))
            env = smoothstep(-reach - 120, -reach, -dd) * (0.12 + 0.4 * smoothstep(TFULL + 2, TBLACK - 0.4, t))
            fur = env * tex * (0.55 + 0.45 * ripple) * (1 + 0.35 * pulse)
            layers.append((lerp(FURG, FUR, 0.6 + 0.4 * ripple[:, None]), fur))
            layers.append((BLOOD, 0.45 * pulse * np.exp(-(dd / (60 + 260 * g)) ** 2) * (t < TBLACK)))
            # him: growing, shivering, turning from warm to fur
            Lb = 22 + 128 * g
            sh = 2.0 + 9 * g
            a = xm - Lb / 2 + sh * np.sin(2 * np.pi * 13 * t)
            b = xm + Lb / 2 + sh * np.sin(2 * np.pi * 11 * t + 1)
            body = cover(a, b)
            fgl.append((lerp(MAN, FUR, min(1, 1.4 * g)), body * (0.5 + 0.15 * g) * (1 + 0.3 * pulse)))
            fg = np.maximum(fg, body)
        elif t < TFULL:
            pass

        # ---- the man walking home and the lantern ----
        x = man_x(t)
        man_on = t < TFULL or (TBACK[0] <= t < TIN + 0.9)
        if man_on and t >= 1.0:
            step_t = [p[0] for p in (P['walk'] if t < 66 else P['home'])[1:]]
            st = max([_hit(t - s, 0.1) for s in step_t if s <= t] or [0.0])
            I = (0.5 + 0.12 * st)
            hw = 11.0
            if t >= TBACK[0]:                    # after the fall: sits squashed, then walks
                sq = keys(t, [(TBACK[1], 1.5), (TBACK[1] + 0.25, 1.6), (POUNCE[2] + 1.2, 1.25), (66.6, 1.0)])
                hw *= sq
                I *= keys(t, [(TBACK[0], 0.4), (TBACK[1], 0.7), (66.6, 0.9)])
            if t >= TIN:
                I *= 1 - smoothstep(TIN, TIN + 0.8, t)
            body = cover(x - hw, x + hw)
            fgl.append((MAN, body * I))
            fg = np.maximum(fg, body)
        lit = (t < TDROP) or (t >= TPICK)
        if lit and t >= 1.0:
            lw = 0.6 * np.sin(2 * np.pi * 0.9 * t)
            if t < TDROP:
                side = -1.0 if t < 20.7 else keys(t, [(20.7, -1.0), (21.2, 1.0)])
                lx = x + side * 15 + 2 * lw
                if 17.6 <= t < 20.4:              # fumbling for keys: the lantern jiggles
                    lx += 3 * np.sin(2 * np.pi * 7 * t) * (0.5 + 0.5 * np.sin(2 * np.pi * 0.8 * t))
                li = 0.8
                if LOOK[0] <= t < LOOK[1] + 0.3:  # holds it up to look at the moon
                    li += 0.18 * smoothstep(LOOK[0], LOOK[0] + 0.4, t) * (1 - smoothstep(LOOK[1] - 0.2, LOOK[1] + 0.3, t))
            else:
                lx = x - 15 + 2 * lw
                li = 0.78 + 0.2 * _hit(t - TPICK, 0.4)
                if t >= TIN:
                    li *= 1 - smoothstep(TIN, TIN + 0.8, t)
            fl = 1 + 0.06 * np.sin(2 * np.pi * lant_f * t + lant_p).sum()
            lb = cover(lx - 4.5, lx + 4.5)
            fgl.append((LANTERN, lb * li * fl))
            glow = np.exp(-((pdp - lx) / (42 + 25 * (li > 0.85))) ** 2) * 0.22 * li * fl * (1 - lb)
            layers.append((LANTERN, glow))
        elif TDROP <= t < TDROP + 2.6:            # dropped: falls, bounces, gutters out
            lx = keys(t, [(TDROP, xm + 15), (TDROP + 0.25, xl - 6), (TDROP + 0.5, xl + 4), (TDROP + 0.62, xl)])
            gut = (1 - smoothstep(TDROP + 0.8, TDROP + 2.5, t)) * (0.75 + 0.25 * np.sin(2 * np.pi * 8.3 * t)
                                                                  * np.sin(2 * np.pi * 3.1 * t))
            li = 0.8 * gut + 0.3 * _hit(t - TDROP - 0.25, 0.08) + 0.2 * _hit(t - TDROP - 0.5, 0.08)
            lb = cover(lx - 4.5, lx + 4.5)
            fgl.append((LANTERN, lb * li))
            layers.append((LANTERN, np.exp(-((pdp - lx) / 40) ** 2) * 0.18 * li * (1 - lb)))
        elif TDROP + 2.6 <= t < TPICK and t >= 66.6:  # it waits on the porch, a dull ember
            layers.append((LANTERN, cover(xl - 4.5, xl + 4.5) * 0.12 * smoothstep(66.6, 70, t)))

        # ---- the wolf ----
        if TBLACK <= t < TBACK[1]:
            wx = wolf_x(t)
            dr = -1.0 if t < TTURN else 1.0
            turn = 1 - 0.65 * np.exp(-((t - TTURN) / 0.12) ** 2)
            Lb = 150.0 * turn
            Ib = 0.4
            eyes = 0.0 if t < TEYES else 0.95 * (1 - np.exp(-(t - TEYES) / 0.04))
            if t < TEYES:
                Ib = 0.05 * smoothstep(TBLACK + 0.3, TEYES, t)
            # a coil and a crouch before each pounce, the stretch of the leap
            for i, pt in enumerate(POUNCE):
                cr = smoothstep(pt - 0.6, pt - 0.1, t) * (1 - smoothstep(pt, pt + 0.05, t))
                lp = (t >= pt) * (1 - smoothstep(pt + LEAP[i] - 0.1, pt + LEAP[i] + 0.05, t))
                Lb *= (1 - 0.28 * cr) * (1 + 0.3 * lp)
                Ib *= 1 - 0.3 * cr
                eyes *= 1 - 0.35 * cr
            if THOWL <= t < THOWL + HOWL_LEN:     # head up: brighter, mane bristles
                ha = howl_amp(t - THOWL)
                Ib += 0.12 * ha
                eyes = min(1.0, eyes + 0.1 * ha)
            wig = 0.0
            if POUNCE[2] - 1.2 <= t < POUNCE[2]:    # wiggles before the big one
                wig = 12 * np.sin(2 * np.pi * 4.5 * t) * smoothstep(POUNCE[2] - 1.2, POUNCE[2] - 0.9, t)
            if t >= TBACK[0]:                     # changing back in the air
                u = smoothstep(TBACK[0], TBACK[1], t)
                Lb = lerp(Lb, 22.0, u)
                eyes *= 1 - u
                Ib = lerp(Ib, 0.4, u)
            head = wx
            tail = wx - dr * Lb + dr * wig
            body = cover(head, tail)
            ramp = np.clip((pdp - tail) / (head - tail + 1e-6), 0, 1)
            tex = 0.7 + 0.3 * furA(pdp - wx)
            col = lerp(FURG, FUR, (0.4 + 0.6 * ramp)[:, None])
            fgl.append((col, body * Ib * tex * (0.6 + 0.6 * ramp)))
            fg = np.maximum(fg, body * 0.9)
            if t >= TEYES:
                blink = 0.0
                for tb in (beat(75.5), beat(84.5), beat(87)):
                    if tb <= t < tb + 0.12:
                        blink = 1.0
                look = 0.0
                if TANS <= t < TANS + ANS_LEN:     # ears up at the answer: glance back
                    look = 1.0
                e = eyes * (1 - blink)
                ec = head - dr * (6 + 3 * look)
                for o in (-1, 1):
                    c = ec - dr * o * 5.5 - dr * 5.5
                    fgl.append((EYE, cover(c - 2.6, c + 2.6) * e))
            # landing thump: the roof shakes out from his paws
            for i, pt in enumerate(POUNCE[:2]):
                tl = t - pt - LEAP[i]
                if 0 <= tl < 0.8:
                    rr = 400 * tl
                    ring = np.exp(-((np.abs(pdp - wx) - rr) / 35) ** 2) * np.exp(-tl / 0.3)
                    layers.append((FUR, 0.45 * ring))
            # trailing streak during a leap
            for i, pt in enumerate(POUNCE):
                if pt <= t < pt + LEAP[i] and t < TBACK[0] + 0.1:
                    sx = tail - dr * 60 * np.sin(np.pi * (t - pt) / LEAP[i])
                    layers.append((FURG, cover(tail, sx) * 0.18))

        # ---- the howl, and the answer ----
        if THOWL <= t < THOWL + HOWL_LEN + 0.8:
            tt = t - THOWL
            ha = howl_amp(min(tt, HOWL_LEN))
            wx = wolf_x(t)
            dd = np.abs(pdp - wx)
            rh = 640 * tt
            wav = smoothstep(-rh - 80, -rh, -dd) * (1 - 0.35 * dd / L)
            band = np.exp(-((dd - rh) / 45) ** 2)
            vib = 1 + 0.08 * np.sin(2 * np.pi * 5.5 * tt) * smoothstep(1.0, 1.8, tt) * (1 - smoothstep(4.2, 5.0, tt))
            hv = (0.5 * wav * ha * vib + 0.55 * band * ha) * (1 - smoothstep(HOWL_LEN, HOWL_LEN + 0.8, tt))
            layers.append((HOWL, hv))
        if TANS <= t < TANS + ANS_LEN + 0.5:
            tt = t - TANS
            aa = howl_amp(min(tt, ANS_LEN), ANS_LEN / HOWL_LEN)
            layers.append((HOWL, 0.2 * aa * (1 - smoothstep(60, 300, pdp))))
            ea = 0.55 * smoothstep(0, 0.3, tt) * (1 - smoothstep(ANS_LEN - 0.2, ANS_LEN + 0.4, tt))
            for c in (14.0, 25.0):
                fgl.append((EYE, cover(c - 2.6, c + 2.6) * ea))

        # ---- after the fall: dizzy stars, the peek ----
        if TBACK[1] <= t < TPEEK[0] + 0.2:
            x = man_x(t)
            dz = smoothstep(TBACK[1], TBACK[1] + 0.3, t) * (1 - smoothstep(TPEEK[0] - 0.6, TPEEK[0], t))
            for k in range(3):
                a = 2 * np.pi * (1.1 * t + k / 3)
                c = x + 30 * np.sin(a)
                fgl.append((DIZZY, cover(c - 2.5, c + 2.5) * dz * (0.45 + 0.4 * np.cos(a))))
        if TPEEK[0] <= t < TPEEK[1] + 0.6:
            x = man_x(t)
            u = smoothstep(TPEEK[0] + 0.1, TPEEK[0] + 0.3, t) * (1 - smoothstep(TPEEK[1] - 0.1, TPEEK[1] + 0.5, t))
            hw = 16 + 30 * u
            shv = 5 * u * np.sin(2 * np.pi * 12 * t)
            fgl.append((FUR, cover(x - hw + shv, x + hw + shv) * 0.3 * u))
            for o in (-1, 1):
                c = x - 8 + o * 5.5
                fgl.append((EYE, cover(c - 2.6, c + 2.6) * 0.9 * u))

        # ---- dawn ----
        dg = dawn_g * (1 - smoothstep(D - 4, D - 0.5, t))
        layers.append((lerp(DAWN0, DAWN1, dg[:, None]), 0.36 * dg))

        # ---- the gag: eyes at the door, one winks ----
        if TGAG <= t < TGAG + 1.6:
            tt = t - TGAG
            op = smoothstep(0, 0.12, tt) * (1 - smoothstep(1.3, 1.5, tt))
            for o in (-1, 1):
                wink = 1.0 if (o > 0 and 0.7 <= tt < 1.0) else 0.0
                c = xm + o * 5.5
                fgl.append((EYE, cover(c - 2.6, c + 2.6) * op * (1 - wink)))

        # ---- compose ----
        bgk = 1 - fg
        buf = np.zeros((N, 3))
        for col, I in layers:
            buf += light(col, np.clip(I, 0, None) * bgk)
        buf += light(STAR, starv * bgk)
        buf += light(MOON, moon * bgk)
        for col, I in fgl:
            buf += light(col, np.clip(I, 0, 1))
        out[fi][G.path] = np.clip(buf * fade, 0, 1)
    return out


# ---------------------------------------------------------------- music ----------------------------------------------
# E minor at the lights' 100 BPM. A clarinet whistles his walking tune over cello pizzicato and footsteps; horns carry
# the moon's motif and a harp follows the moon across the house. The change is a heartbeat (muted bass drum and sub)
# that speeds up exactly with the light's pulses under rising tremolo strings, trombone growls and a cymbal and timpani
# crescendo that cuts dead at the blackout. The howl is synthesised from the same pitch and loudness curves that drive
# the howl's light. The hunt is a contrabass and bassoon prowl with low drums on his stalking steps, growls on each
# crouch, whooshes along each leap, timpani on each landing and a harp skip for each dodge of the moon. The cloud
# deflates it with a trombone fall and a slide whistle; dawn brings the tune back in E major. Sounds are panned to
# where they happen on the house as seen from the street.

PROG = ['Em', 'Em', 'C', 'B7', 'Em', 'Em', 'Am', 'B7']
WALKB = {'Em': ('E2', 'G2', 'B2', 'G2'), 'C': ('C2', 'E2', 'G2', 'E2'), 'Am': ('A1', 'C2', 'E2', 'C2'),
         'B7': ('B1', 'D#2', 'F#2', 'A2'), 'E': ('E2', 'G#2', 'B2', 'G#2'), 'A': ('A1', 'C#2', 'E2', 'C#2')}
CHORDS = {'Em': ('E3', 'G3', 'B3'), 'C': ('C3', 'E3', 'G3'), 'Am': ('A2', 'C3', 'E3'), 'B7': ('B2', 'D#3', 'A3'),
          'E': ('E3', 'G#3', 'B3'), 'A': ('A2', 'C#3', 'E3')}
TUNE1 = [(0, 'E4', 0.5), (0.5, 'G4', 0.5), (1, 'B4', 1), (2, 'A4', 0.5), (2.5, 'G4', 0.5), (3, 'F#4', 1),
         (4, 'E4', 0.5), (4.5, 'D4', 0.5), (5, 'E4', 1.5), (7, 'B3', 0.5), (7.5, 'D4', 0.5)]
TUNE2 = [(0, 'G4', 1), (1, 'A4', 1), (2, 'B4', 0.5), (2.5, 'C5', 0.5), (3, 'B4', 0.5), (3.5, 'A4', 0.5),
         (4, 'G4', 1), (5, 'F#4', 0.5), (5.5, 'A4', 0.5), (6, 'E4', 2)]
MOTIF = [(0, 'E3', 2), (2, 'B3', 2), (4, 'C4', 1.5), (5.5, 'B3', 2.5)]     # the moon, in beats
KEYS_JINGLE = [beat(25.7), beat(26.1), beat(27.6), beat(28.0), beat(28.4), beat(29.6)]


def _howl_sig(SR, scale=1.0, transpose=0.0, seed=0):
    """A wolf's howl: a glottal buzz with a sliding 'oo-ah-oo' vowel, from howl_pitch/howl_amp."""
    dur = HOWL_LEN * scale
    n = int(dur * SR)
    tt = np.arange(n) / SR
    grid = np.arange(0, dur + 0.002, 0.002)
    pit = np.interp(tt, grid, [howl_pitch(g, scale) for g in grid]) + transpose
    amp = np.interp(tt, grid, [howl_amp(g, scale) for g in grid])
    f = 440.0 * 2 ** ((pit - 69) / 12)
    ph = 2 * np.pi * np.cumsum(f) / SR
    op = np.clip(amp, 0, 1)                 # louder = more open vowel
    F1, F2 = 330 + 350 * op, 820 + 380 * op
    sig = np.zeros(n)
    for k in range(1, 15):
        fk = k * f
        a = (np.exp(-((fk - F1) / 170) ** 2) + 0.55 * np.exp(-((fk - F2) / 260) ** 2)
             + 0.12 * np.exp(-((fk - 2600) / 500) ** 2) + 0.2 / k)
        sig += a * np.sin(k * ph) * (fk < 9000)
    rng = np.random.default_rng(seed)
    br = np.convolve(rng.normal(0, 1, n), np.ones(12) / 12, 'same')
    sig = sig / (np.abs(sig).max() + 1e-9) + 0.12 * br * (1 + np.sin(ph))
    sig *= amp * np.clip(tt / 0.05, 0, 1)
    return np.vstack([sig, np.roll(sig, 40)]) * 0.5


def score(M, G):
    from pixelhome.audio import SR, note, slide, whoosh
    n = note
    P = plan(G)
    L, xm, xl, mc = P['L'], P['xm'], P['xl'], P['mc']

    clar = M.sampler('Woodwinds/Clarinet/stac/*.wav', tune=-12)
    clar_l = M.sampler('Woodwinds/Clarinet/susLong/*.wav', tune=-12)
    bsn = M.sampler('Woodwinds/Bassoon/stac/*.wav', tune=-12)
    horn = M.sampler('Brass/F Horn/sus/*.wav', tune=-12)
    horn_st = M.sampler('Brass/F Horn/stac/*.wav', tune=-12)
    tuba = M.sampler('Brass/Tuba/sus/*.wav', tune=-12)
    buzz = M.sampler('Brass/OldTrombone/Buzz/*.wav', tune=-12)
    fall = M.sampler('Brass/OldTrombone/Fall/*.wav', tune=-12)
    pizz = M.sampler('Strings/Cello Section/pizzT/*.wav', tune=-12)
    cb = M.sampler('Strings/Solo Contrabass/Pizz/*.wav', tune=-12)
    cello = M.sampler('Strings/Cello Section/susvib/*.wav', tune=-12)
    ctrem = M.sampler('Strings/Cello Section/trem/*.wav', tune=-12)
    vtrem = M.sampler('Strings/Viola Section/trem/*.wav', tune=-12)
    viola = M.sampler('Strings/Viola Section/susvib/*.wav', tune=-12)
    harp = M.sampler('Strings/Harp/*.wav')
    timp = M.hits('Percussion/Timpani/Timpani1_Hit*.wav')
    troll = M.hits('Percussion/Timpani/Rolls/Timpani1_Roll_v5*.wav')
    muted = M.hits('VSCO 1 Percussion/drums/bass/bdrum_muted_f*.wav')
    muted_s = M.hits('VSCO 1 Percussion/drums/bass/bdrum_muted_mp*.wav')
    bd = M.hits('Percussion/BDrumNewhit_v[4-6]*.wav')
    tenor = M.hits('VSCO 1 Percussion/drums/tenor/tenor_lower/*.wav')
    logd = M.hits('Percussion/LogDrumLo*.wav')
    wood = M.hits('VSCO 1 Percussion/varWood/wood_click*.wav')
    tri = M.hits('Percussion/Triangle3-HitM*.wav')
    brake = M.hits('Percussion/BrakeDrum1_Hammer*.wav')
    guiro = M.hits('Percussion/Guiro-Hit*.wav')
    gong = M.hits('Percussion/gongHit_f.wav')
    gong_p = M.hits('Percussion/gongHit_p.wav')
    cresc = M.hits('Percussion/susCymb1-cresc-Median_v1.wav')
    cym = M.hits('Percussion/susCymb1-hit_mp*.wav')

    for name, gain, rev in (('bass', 0.5, 0.08), ('winds', 0.42, 0.22), ('brass', 0.36, 0.28), ('strings', 0.34, 0.3),
                            ('harp', 0.3, 0.3), ('perc', 0.8, 0.15), ('drums', 0.55, 0.2), ('heart', 0.7, 0.05),
                            ('pad', 0.2, 0.4), ('howl', 1.0, 0.35), ('far', 0.45, 0.75), ('fx', 0.2, 0.25)):
        M.bus(name, gain=gain, reverb=rev)

    order = np.argsort(G.pd)
    xs, ds = G.pos[order, 0], G.pd[order]
    x0, x1 = xs.min(), xs.max()

    def pan_at(d):                          # path distance -> left/right across the facade, as seen from the street
        x = np.interp(np.clip(d, 0, L), ds, xs)
        return float(0.85 * (2 * (x - x0) / (x1 - x0) - 1))

    def moving(sig, t, d_of_t):             # pan a sound sample by sample as it travels along the roof
        tt = t + np.arange(sig.shape[1]) / SR
        d = np.array([d_of_t(u) for u in tt[::480]])
        x = np.interp(np.clip(np.interp(tt, tt[::480], d), 0, L), ds, xs)
        a = (0.85 * (2 * (x - x0) / (x1 - x0) - 1) + 1) * np.pi / 4
        return sig * np.vstack([np.cos(a), np.sin(a)]) * np.sqrt(2)

    def man(t):
        return track(t, P['walk'], 0.42) if t < TBACK[0] else track(t, P['home'])

    def wolf(t):
        return track(t, P['wolf'])

    def moon(t):
        return moon_at(P, t)

    def chord_at(k):
        return PROG[int(k // 4) % len(PROG)]

    pad, sub = [], []

    # ---- 0-22: the walk home; the moon comes up the other way ----
    pad += [(0.3, n('E2'), 60, 21.6), (0.3, n('B2'), 54, 21.6), (6.0, n('G3'), 44, 15.9)]
    M.add('fx', whoosh(9.0, 90, 380, 0.4, seed=1), 0.0, 0.25)
    walk_steps = [p[0] for p in P['walk'][1:]]
    for i, ts in enumerate(walk_steps):     # his footsteps, where they land
        M.add('perc', wood.play(60 + 8 * (i % 2)), ts, 0.45, pan_at(man(ts)))
        M.add('perc', logd.play(55), ts, 0.25, pan_at(man(ts)))
    for k in range(1, 33):                  # cello pizzicato walking bass
        if 12 < k < 15:                     # he stops: the bass holds its breath
            continue
        c = chord_at(k)
        M.add('bass', pizz.play(n(WALKB[c][k % 4]), 92 if k % 4 == 0 else 78), beat(k), 0.9)
    for b0, tune in ((4, TUNE1), (15, TUNE2)):   # his whistled tune, from his lantern
        for b, m, dur in tune:
            t = beat(b0 + b)
            inst = clar_l if dur >= 1.5 else clar
            M.add('winds', inst.play(n(m), 92, dur=dur * BEAT), t, 0.9, pan_at(man(t)))
    for b, m, dur in MOTIF:                 # the moon appears: horns, far away at the back of Side
        M.add('brass', horn.play(n(m), 56, dur=dur * BEAT + 0.3), beat(3 + b), 0.6, pan_at(moon(beat(3 + b))))
    for k in range(8, 33, 2):               # the harp follows the moon
        c = chord_at(k)
        for j, m in enumerate(CHORDS[c] + (CHORDS[c][0][:-1] + str(int(CHORDS[c][0][-1]) + 1),)):
            t = beat(k) + j * BEAT / 4
            M.add('harp', harp.play(n(m) + 12, 70), t, 0.8, pan_at(moon(t)))
    # cloud A crosses the moon: low strings darken
    for m in ('E2', 'G2', 'C3'):
        M.add('strings', cello.play(n(m), 60, dur=3.4), 11.6, 0.6, pan_at(moon(13)))
    # he stops at the corner and looks up: the motif again, closer, and the tune asks a question
    M.add('winds', clar_l.play(n('B4'), 84, dur=2 * BEAT), LOOK[0], 0.8, pan_at(man(LOOK[0])))
    for b, m, dur in MOTIF[:2]:
        M.add('brass', horn.play(n(m), 72, dur=dur * BEAT * 0.5 + 0.2), LOOK[0] + b * BEAT * 0.5, 0.8,
              pan_at(moon(LOOK[0])))
    for t in KEYS_JINGLE:                   # fumbling for his keys at the door
        M.add('perc', tri.play(70), t, 0.45, pan_at(xm))
    M.add('drums', troll.play(70, dur=TFULL - 19.8), 19.8, 0.6, pan_at(mc))
    for m in ('E2', 'B2'):
        M.add('strings', ctrem.play(n(m), 80, dur=TFULL - 19.6 + 0.2), 19.6, 0.7, 0.0)
    M.add('strings', vtrem.play(n('G3'), 74, dur=TFULL - 20.2 + 0.2), 20.2, 0.6, 0.0)

    # ---- 22.2: full moon ----
    M.add('drums', gong.play(110), TFULL, 0.9, pan_at(mc))
    M.add('drums', timp.play(120, pitch=-1), TFULL, 0.9, pan_at(mc))
    M.add('bass', tuba.play(n('E1'), 110, dur=3.0), TFULL, 0.9)
    for m in ('E2', 'B2', 'E3', 'G3'):
        M.add('brass', horn.play(n(m), 108, dur=2.6), TFULL, 0.75, pan_at(mc) * 0.6)
    for j, m in enumerate(('E3', 'F#3', 'G3', 'B3', 'C4', 'E4', 'F#4', 'G4', 'B4')):
        M.add('harp', harp.play(n(m), 96), TFULL + 0.03 * j, 0.8, pan_at(mc))
    for b, m, dur in MOTIF:
        M.add('brass', horn.play(n(m) + 12, 90, dur=dur * BEAT * 0.75 + 0.2), TFULL + 0.6 + b * BEAT * 0.75, 0.7,
              pan_at(mc))

    # ---- 22.2-32.6: the change ----
    M.add('perc', brake.play(80), TDROP + 0.25, 0.7, pan_at(xl))          # the lantern hits the porch
    M.add('perc', brake.play(55), TDROP + 0.5, 0.5, pan_at(xl))
    M.add('perc', tri.play(50), TDROP + 0.62, 0.4, pan_at(xl))
    for i, h in enumerate(HB):              # the heart, exactly with the light's pulses
        v = 0.55 + 0.45 * i / len(HB)
        M.add('heart', muted.play(118), h, v, pan_at(xm))
        M.add('heart', muted_s.play(100), h + 0.17, 0.7 * v, pan_at(xm))
        sub.append((h, n('E1'), int(70 + 50 * i / len(HB)), 0.16))
        sub.append((h + 0.17, n('E1'), int(55 + 40 * i / len(HB)), 0.12))
    rise = ['E2', 'F2', 'F#2', 'G2', 'G#2', 'A2', 'A#2', 'B2']
    seg = (TBLACK - TFULL - 1.0) / len(rise)
    for i, m in enumerate(rise):            # the strings climb, a semitone at a time, to the blackout
        t = TFULL + 1.0 + i * seg
        d = TBLACK - t
        M.add('strings', ctrem.play(n(m), 70 + 6 * i, dur=d), t, 0.55, pan_at(xm) * 0.5)
        M.add('strings', vtrem.play(n(m) + 7, 66 + 6 * i, dur=d), t, 0.45, pan_at(xm) * 0.5)
    for i, h in enumerate(HB[2::3]):        # growls as the fur comes through
        M.add('brass', buzz.play(n('E2') + i, 90 + 5 * i, dur=0.7), h + 0.05, 0.8, pan_at(xm))
    M.add('drums', cresc.play(100, dur=TBLACK - (TBLACK - 5.5)), TBLACK - 5.5, 0.8)
    M.add('drums', troll.play(110, dur=4.0), TBLACK - 4.0, 0.9, pan_at(xm))
    M.add('fx', whoosh(TBLACK - TFULL - 2.0, 120, 2600, 0.5, seed=5), TFULL + 2.0, 0.6, pan_at(xm))

    # ---- 33.6: the eyes ----
    M.add('drums', timp.play(115, pitch=-3), TEYES, 1.0, pan_at(xm))
    M.add('drums', gong_p.play(100), TEYES, 0.7, pan_at(xm))
    M.add('bass', cb.play(n('E1'), 120), TEYES, 1.0)
    for m in ('E2', 'F2', 'B2'):
        M.add('brass', horn_st.play(n(m), 115), TEYES, 0.8, pan_at(xm))

    # ---- 34.2: the howl, and the answer from the far end of Side ----
    M.add('howl', moving(_howl_sig(SR, 1.0, 0.0, seed=2), THOWL, lambda u: wolf(u)), THOWL, 1.0)
    for m in ('E2', 'B2', 'G3'):
        M.add('strings', cello.play(n(m), 80, dur=HOWL_LEN), THOWL + 0.6, 0.6, 0.0)
    for m in ('E3', 'B3', 'F#4'):
        M.add('brass', horn.play(n(m), 70, dur=HOWL_LEN - 1.0), THOWL + 1.0, 0.5, pan_at(xm))
    M.add('drums', cresc.play(80, dur=3.0), THOWL, 0.3)
    M.add('drums', cym.play(80), THOWL + 3.0, 0.35)
    M.add('far', _howl_sig(SR, ANS_LEN / HOWL_LEN, -5.0, seed=3), TANS, 1.0, pan_at(14.0))

    # ---- 40.8-57.6: the hunt ----
    ost = ['E2', None, 'E2', 'G2', None, 'E2', 'A#2', 'A2']
    for k in range(64, 91):                 # contrabass prowl in eighths, two bars of it per phrase
        for e in range(2):
            m = ost[(2 * (k - 64) + e) % 8]
            if m:
                M.add('bass', cb.play(n(m), 100 if e == 0 else 84), beat(k + e / 2), 0.9)
    sneak = [(0, 'E3'), (0.5, 'F#3'), (1, 'G3'), (2.5, 'A#3'), (3, 'B3'), (4.5, 'G3'), (5, 'F#3'), (6, 'E3')]
    for p0 in (66, 74, 82):                 # bassoon creeping after the moon
        for b, m in sneak:
            t = beat(p0 + b)
            M.add('winds', bsn.play(n(m), 88), t, 0.8, pan_at(wolf(t)))
    for i in range(3):
        for k in STALK[i]:                  # his stalking steps
            t = beat(k)
            M.add('drums', tenor.play(80), t, 0.55, pan_at(wolf(t)))
        pt, lp = POUNCE[i], LEAP[i]
        M.add('brass', buzz.play(n('E2') + 3 * i, 98, dur=0.55), pt - 0.6, 0.9, pan_at(wolf(pt - 0.6)))
        M.add('drums', troll.play(80, dur=0.6), pt - 0.6, 0.5, pan_at(wolf(pt)))
        M.add('fx', moving(whoosh(lp + 0.15, 200, 1400, 0.6, seed=10 + i), pt, wolf), pt, 0.9)
        for j in range(5):                  # the moon skips out of reach
            t = pt + 0.06 * j
            M.add('harp', harp.play(n(['B3', 'E4', 'F#4', 'G4', 'B4'][j]) + 2 * i, 92), t, 0.8, pan_at(moon(t)))
        if i < 2:                           # landing
            t = pt + lp
            M.add('drums', timp.play(118, pitch=-1 - i), t, 1.0, pan_at(wolf(t)))
            M.add('drums', bd.play(110), t, 0.8, pan_at(wolf(t)))
            M.add('drums', cym.play(85), t, 0.4, pan_at(wolf(t)))
    wig0 = POUNCE[2] - 1.2                  # the wiggle: a guiro scrape on each swing
    for j in range(int(1.2 * 4.5)):
        t = (np.floor(wig0 * 4.5) + j + 1.25) / 4.5
        if wig0 + 0.15 <= t < POUNCE[2]:
            M.add('perc', guiro.play(85), t, 0.8, pan_at(wolf(t)))
    M.add('brass', fall.play(n('B2'), 110), TCOVER, 1.0, pan_at(moon(TCOVER)))
    M.add('fx', slide(0.0, TBACK[1] - TBACK[0] + 0.2, 520, 160, TBACK[1] - TBACK[0] + 0.3, 0.6), TBACK[0], 0.9,
          pan_at(wolf(TBACK[0])))
    tl = POUNCE[2] + LEAP[2]
    M.add('drums', bd.play(70), tl, 0.6, pan_at(man(tl)))
    M.add('perc', wood.play(110), tl, 0.8, pan_at(man(tl)))
    M.add('bass', tuba.play(n('E1'), 90, dur=0.5), tl, 0.8)

    # ---- 57.6-61.8: seeing stars; the moon peeks; it sets ----
    t = tl + 0.3
    while t < TPEEK[0] - 0.5:               # stars round his head: three of them, 1.1 turns a second
        k = int(round((t - tl) * 3.3))
        M.add('harp', harp.play(n(['E4', 'G4', 'B4'][k % 3]), 52), t, 0.7, pan_at(man(t)) + 0.08 * np.sin(k))
        t += 1 / 3.3
    for j, m in enumerate(('E4', 'D#4', 'D4', 'C#4')):
        M.add('winds', clar_l.play(n(m), 70, dur=0.9), tl + 0.5 + j * 0.9, 0.7, pan_at(man(tl)))
    for h in (TPEEK[0] + 0.1, TPEEK[0] + 0.6):
        M.add('heart', muted.play(118), h, 0.9, pan_at(man(h)))
        M.add('heart', muted_s.play(100), h + 0.17, 0.6, pan_at(man(h)))
    for m in ('E3', 'F3'):
        M.add('brass', horn_st.play(n(m), 110), TPEEK[0] + 0.1, 0.8, pan_at(man(TPEEK[0])))
    M.add('strings', vtrem.play(n('B2'), 80, dur=TPEEK[1] - TPEEK[0]), TPEEK[0], 0.6, pan_at(man(TPEEK[0])))
    M.add('perc', wood.play(100), TPEEK[1], 0.7, pan_at(man(TPEEK[1])))
    M.add('bass', tuba.play(n('B1'), 70, dur=0.8), TPEEK[1], 0.6)
    for j, m in enumerate(('B4', 'G4', 'E4', 'B3', 'G3', 'E3')):   # the moon sets
        t = TSET[0] + j * (TSET[1] - TSET[0]) / 6
        M.add('harp', harp.play(n(m), 70), t, 0.7, pan_at(moon(t)))
    for b, m, dur in MOTIF[::-1]:
        t = TSET[0] + (MOTIF[-1][0] - b) * BEAT * 0.8
        M.add('brass', horn.play(n(m), 52, dur=dur * BEAT), t, 0.55, pan_at(moon(t)))

    # ---- 66-84: dawn, the walk home in E major, the lantern, the wink ----
    pad += [(TDAWN[0], n('E2'), 56, D - TDAWN[0] - 1.5), (TDAWN[0], n('B2'), 50, D - TDAWN[0] - 1.5),
            (TDAWN[0] + 2.0, n('G#3'), 46, D - TDAWN[0] - 3.5)]
    for m in ('E2', 'B2'):
        M.add('strings', cello.play(n(m), 56, dur=8.0), TDAWN[0], 0.5, -0.6)
    M.add('strings', viola.play(n('G#3'), 56, dur=7.0), TDAWN[0] + 1.5, 0.5, -0.6)
    home = [p[0] for p in P['home'][1:]]
    for i, ts in enumerate(home):
        M.add('perc', wood.play(60 + 8 * (i % 2)), ts, 0.45, pan_at(man(ts)))
        M.add('perc', logd.play(55), ts, 0.25, pan_at(man(ts)))
    prog_e = ['E', 'A', 'E', 'B7', 'E']
    for k in range(HOME[0], TIN_K + 1):
        c = prog_e[min(len(prog_e) - 1, (k - HOME[0]) // 4)]
        M.add('bass', pizz.play(n(WALKB[c][k % 4]), 84 if k % 4 == 0 else 72), beat(k), 0.8)
    major = {'G4': 'G#4', 'C5': 'C#5', 'D4': 'D#4'}
    for b0, tune in ((HOME[0] + 1, TUNE1), (HOME[0] + 9, TUNE2)):
        for b, m, dur in tune:
            k = b0 + b
            if k > TIN_K:
                continue
            t = beat(k)
            inst = clar_l if dur >= 1.5 else clar
            M.add('winds', inst.play(n(major.get(m, m)), 86, dur=dur * BEAT), t, 0.85, pan_at(man(t)))
    for j, m in enumerate(('E3', 'G#3', 'B3', 'E4', 'G#4')):
        M.add('harp', harp.play(n(m), 90), TPICK + 0.04 * j, 0.8, pan_at(xl))
    M.add('perc', tri.play(90), TPICK, 0.6, pan_at(xl))
    M.add('perc', logd.play(100), TIN + 0.75, 0.8, pan_at(xm))           # the door
    M.add('drums', bd.play(70), TIN + 0.75, 0.5, pan_at(xm))
    for m in ('E2', 'G2', 'B2'):            # the eyes at the door
        M.add('brass', horn.play(n(m), 70, dur=1.4), TGAG, 0.7, pan_at(xm))
    M.add('drums', timp.play(80, pitch=-3), TGAG, 0.6, pan_at(xm))
    M.add('fx', slide(0.0, 0.12, 700, 1100, 0.18, 0.5), TGAG + 0.7, 0.6, pan_at(xm + 5))   # the wink
    M.add('harp', harp.play(n('E3'), 70), TGAG + 1.5, 0.7, pan_at(xm))

    M.add('pad', M.synth('Pads/Ghost Pad').render(pad, D), 0.0)
    M.add('heart', M.synth('Basses/Sub 1').render(sub, D), 0.0, 0.5)

