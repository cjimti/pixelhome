"""Special Delivery: a galop at 150 BPM, every move on its beat grid. The sleigh team (a red nose, four
bone-white reindeer, the driver and the red sleigh) gallops in from the free right end and drops four
presents along the roof as it goes. Each lands with a thump and a few beats later pops open: a
jack-in-the-box springs out on the right wing, a rubber duck on the porch hops after the long-gone sleigh
quacking until it gives up, a bat flaps off toward the back of the house, and a spider boings out on its
string on the left wing. The team gallops away along Side.

The team sneaks back in from the free right end. Two searchlights clunk on at the porch corners and
sweep; one passes right over the team, which ducks. Then one finds it (ding!), the team bolts left, both
beams chase and bonk into each other where it just was, it loops the loop round the front-left corner
and escapes away along Side, and the beams, swinging after it, bonk each other again on the left wing
and sag off. In the dark the duck quacks once. Then the victory lap: the team tears back in from the
right end with a gold trail, the bat flying ahead of it; the jack and the spider boing as it passes, the
duck hops aboard and rides off with it. Ta-da: confetti bursts out from the porch, everything takes a
bow, and the nose pokes back in at the right end to wink twice. A dim night sky with twinkling stars and
a warm porch glow sits under all of it, so no run goes dark.

Characters are drawn as spans in path distance with exact span-over-pixel coverage. The team follows its
nose: each member sits a fixed arc length back along the nose's own track, so it bunches when it ducks
and follows the nose round the loop. Timings are module constants in beats that score() shares."""
import numpy as np
from pixelhome.fx import DT, hexc, perc, keys, smoothstep, lerp, nframes

CODE = 'NB10'
TITLE = 'Special Delivery'
KIND = 'show'
DESCRIPTION = ('The sleigh drops presents that pop open into surprises: a jack-in-the-box, a bat, a duck and a '
               'spider. Searchlights chase it and bonk into each other, and it loops away for a victory lap.')

BPM = 150
BEAT = 60 / BPM                             # a galop in 2/4: a bar is two beats
D = 58.0
ENTER = 8                                   # beats: the team gallops in from the free right end
V1, V2, V3 = 150.0, 110.0, 330.0            # delivery, sneaking, victory-lap speeds (units/s)
DROPS = (16, 35, 29, 42)                    # jack (Right), bat (Porch Left), duck (Porch Front), spider (Left)
LAND, POP = 1, 5                            # beats after the drop: it lands, it pops open
HOPS = 16                                   # the duck hops after the sleigh this many beats
SNEAK = 64                                  # back in from the right end
BEAM_ON = (66, 68)                          # searchlight A (porch left), B (porch right)
DUCKS = ((71.5, 74.0), (83.5, 85.5))        # the team ducks under a beam
DING, ZOOM = 80, 81                         # found; then it bolts
BONKS = (85, 98)                            # the beams collide
DIZZY = 5                                   # beats they reel afterwards
LOOP = (88, 92)                             # loop-the-loop round the front-left corner
LOOP_AT, LOOP_RUN, LOOP_R = 560.0, 200.0, 90.0
ESCAPE = 96                                 # gone away along Side
BEAM_OFF = (104, 102)                       # A, B sag off
QUACK_DARK = 106
LAP = 108
TADA = 132
WINKS = (134, 135)
TEAM = [('nose', 0)] + [('deer', 26 + 30 * k) for k in range(4)] + [('driver', 160), ('sleigh', 185)]
TAIL = 210

# ---- the tune: a galop in G, 2/4. TUNE is the hook (8 bars of two beats); BRIDGE is the duck's tune ----
TUNE = [(0, 'D5', .5), (.5, 'B4', .5), (1, 'G4', .5), (1.5, 'B4', .5), (2, 'D5', .5), (2.5, 'E5', .5), (3, 'D5', 1),
        (4, 'C5', .5), (4.5, 'A4', .5), (5, 'F#4', .5), (5.5, 'A4', .5), (6, 'C5', .5), (6.5, 'D5', .5),
        (7, 'C5', 1), (8, 'B4', .5), (8.5, 'G4', .5), (9, 'B4', .5), (9.5, 'D5', .5), (10, 'G5', 1),
        (11, 'F#5', .5), (11.5, 'E5', .5), (12, 'D5', .5), (12.5, 'C5', .5), (13, 'A4', .5), (13.5, 'F#4', .5),
        (14, 'G4', 2)]
TUNE_CHORDS = ['G', 'G', 'D7', 'D7', 'G', 'C', 'D7', 'G']                     # one a bar
BRIDGE = [(0, 'E5', 1), (1, 'D5', .5), (1.5, 'C5', .5), (2, 'B4', 1), (3, 'G4', 1), (4, 'A4', .5), (4.5, 'B4', .5),
          (5, 'C5', .5), (5.5, 'D5', .5), (6, 'D5', 2)]
BRIDGE_CHORDS = ['C', 'G', 'Am', 'D7']
SNEAKY = [(0, 'E4', .5), (.5, 'G4', .5), (1, 'B4', 1), (2, 'A4', .5), (2.5, 'G4', .5), (3, 'F#4', 1),
          (4, 'E4', .5), (4.5, 'G4', .5), (5, 'B4', .5), (5.5, 'E5', .5), (6, 'D#5', 1), (7, 'B4', 1)]
SNEAKY_CHORDS = ['Em', 'B7', 'Em', 'B7']

NIGHT = hexc('#1a2c90')
STAR = hexc('#c8d6ff')
NOSE = hexc('#ff1a08')
BONE = hexc('#f0e6cc')
DRIVER = hexc('#f4f6ff')
SLEIGH = hexc('#d01810')
GOLD = hexc('#ffc040')
BEAM = hexc('#dfe8ff')
PORCH = hexc('#ff9a40')
BOXES = [hexc(c) for c in ('#ff1a10', '#10d040', '#3060ff', '#ff9a10')]
SPRING = hexc('#c0c8d8')
CLOWN = hexc('#fff0e0')
BAT = hexc('#a040ff')
WING = hexc('#7020ff')
DUCK = hexc('#ffd800')
BEAK = hexc('#ff6a00')
SPIDER = hexc('#ff40c0')
LEGS = hexc('#ff90e0')
CONFETTI = [hexc(c) for c in ('#ff1a10', '#10d040', '#ffc040', '#3060ff', '#ff40c0', '#a040ff')]


def tb(b):
    return b * BEAT


def _sneak(t, L):
    """The nose on the second flight: sneaking left, frozen, bolting, the loop, the escape."""
    qd = L + 40 - V2 * (tb(DING) - tb(SNEAK))
    if t < tb(DING):
        return L + 40 - V2 * (t - tb(SNEAK))
    if t < tb(ZOOM):
        return qd
    if t < tb(LOOP[0]):
        return lerp(qd, LOOP_AT, (t - tb(ZOOM)) / (tb(LOOP[0]) - tb(ZOOM)))
    if t < tb(LOOP[1]):
        ph = 2 * np.pi * (t - tb(LOOP[0])) / (tb(LOOP[1]) - tb(LOOP[0]))
        return LOOP_AT - LOOP_RUN * ph / (2 * np.pi) - LOOP_R * np.sin(ph)
    return lerp(LOOP_AT - LOOP_RUN, -TAIL - 60, (t - tb(LOOP[1])) / (tb(ESCAPE) - tb(LOOP[1])))


def legs(G):
    """The nose's three flights, sampled every 10 ms: (times, position, arc length travelled)."""
    L = G.length
    out = []
    for t0, t1, f in ((tb(ENTER), tb(ENTER) + (L + TAIL + 120) / V1, lambda t: L + 40 - V1 * (t - tb(ENTER))),
                      (tb(SNEAK), tb(ESCAPE), lambda t: _sneak(t, L)),
                      (tb(LAP), tb(LAP) + (L + TAIL + 120) / V3, lambda t: L + 40 - V3 * (t - tb(LAP)))):
        ts = np.arange(t0, t1, 0.01)
        q = np.array([f(t) for t in ts])
        S = np.concatenate([[0], np.cumsum(np.abs(np.diff(q)))]) + np.arange(len(q)) * 1e-6
        out.append((ts, q, S))
    return out


def at(leg, t, off):
    """Where a team member `off` units back along the nose's track is at t."""
    ts, q, S = leg
    s = np.interp(t, ts, S) - off
    if s >= 0:
        return float(np.interp(s, S, q))
    return float(q[0] - np.sign(q[1] - q[0]) * (-s))


def live(leg, t):
    return leg[0][0] <= t <= leg[0][-1]


def plan(G):
    """Everything render() and score() both need: the flights, where each present lands, the duck's hops,
    the beams' paths, where they bonk, and when the victory lap passes the jack and the spider."""
    L = G.length
    lg = legs(G)
    spots = [at(lg[0], tb(b), 185) for b in DROPS]
    duck_end = spots[2] - 30 * HOPS
    X1 = _sneak(tb(BONKS[0] - 1), L)                 # where the team was a beat before the first bonk
    X2 = 600.0                                       # the second bonk, on the left wing
    pass_t = {}
    for k in (0, 3):                                 # the lap's nose passes the jack, the spider
        pass_t[k] = tb(LAP) + (L + 40 - spots[k]) / V3
    ride = tb(LAP) + (L + 40 - duck_end + TAIL + 18) / V3   # the duck hops aboard
    team_ding = _sneak(tb(DING), L)
    A = [(66, 1150), (69, 800), (72, 1350), (75, 950), (78, 1300), (80, 1000), (85, X1), (90, X1), (95, 495),
         (98, X2)]
    B = [(68, 1800), (70, 1600), (73, 2350), (76, 1700), (78, 2050), (80, team_ding)]
    B2 = [(BONKS[0], X1), (90, X1), (93, 1400), (98, X2)]

    def beam(t):
        """(centre, level) of each searchlight at t."""
        res = []
        for k, (ton, toff) in enumerate(zip(BEAM_ON, BEAM_OFF)):
            if t < tb(ton) or t > tb(toff) + 1.2:
                res.append((0.0, 0.0))
                continue
            b = t / BEAT
            if k == 0:
                c = keys(b, A)
            elif b < ZOOM:
                c = keys(b, B)
            elif b < BONKS[0]:
                c = _sneak(t - BEAT, L)              # hot on its heels, a beat behind
            else:
                c = keys(b, B2)
            lev = 1.0
            u = t - tb(ton)
            if u < 0.35:
                lev = float(np.sin(2 * np.pi * u / 0.12) > -0.2)
            for bk in BONKS:
                if bk <= b < bk + DIZZY:
                    c += 30 * np.sin(2 * np.pi * 1.7 * (t - tb(bk)) + k * np.pi)
                    lev *= 0.55 + 0.15 * np.sin(2 * np.pi * 3 * t)
            if t > tb(toff):
                v = (t - tb(toff)) / 1.2
                lev *= (1 - v) ** 2
                c += 60 * v * (1 if k else -1)
            res.append((float(c), float(lev)))
        return res
    return dict(legs=lg, spots=spots, duck_end=duck_end, X=(X1, X2), pass_t=pass_t, ride=ride, beam=beam)


def duck_x(P, t):
    """The duck's place, and how far through a hop it is (0..1, or None when not hopping)."""
    t0 = tb(DROPS[2] + POP)
    if t < t0:
        return P['spots'][2], None
    b = (t - t0) / BEAT
    if b < HOPS:
        k = int(b)
        f = b - k
        return P['spots'][2] - 30 * (k + smoothstep(0, 0.75, f)), f
    lap = P['legs'][2]
    if t >= P['ride'] and live(lap, t):
        return at(lap, t, TAIL + 18), None
    if t >= P['ride']:
        return None, None
    return P['duck_end'], None


def quacks(P):
    """When the duck quacks (seconds)."""
    t0 = tb(DROPS[2] + POP)
    q = [t0 + tb(2 * k) for k in range(HOPS // 2)] + [t0 + tb(HOPS + 1), tb(QUACK_DARK)]
    q += [t for t in np.arange(P['ride'] + tb(1), P['legs'][2][0][-1], tb(4))]
    return q


def render(G, seed=88):
    rng = np.random.default_rng(seed)
    F = nframes(D)
    out = np.zeros((F, G.N, 3))
    L = G.length
    d = G.pd[G.path]
    w = np.gradient(d)
    e0, e1 = d - w / 2, d + w / 2
    mid = G.pd[G.seg['Porch Front']].mean()
    P = plan(G)
    lg, spots = P['legs'], P['spots']
    stars = rng.choice(G.N, 60, replace=False)
    sph = rng.uniform(0, 2 * np.pi, 60)
    sfr = rng.uniform(0.5, 1.3, 60)
    QK = quacks(P)
    NP = 900
    pt = np.full(NP, -99.0)
    px = np.zeros(NP)
    pl = rng.uniform(0.8, 1.8, NP)
    pc = rng.integers(0, 2, NP)
    nxt = 0
    conf_px = rng.integers(0, G.N, 260)
    conf_c = rng.integers(0, len(CONFETTI), 260)
    conf_t = tb(TADA) + np.abs(d[conf_px] - mid) / 700 + rng.uniform(0, 0.3, 260)
    conf_ph = rng.uniform(0, 2 * np.pi, 260)

    for f in range(F):
        t = f * DT
        b = t / BEAT
        fr = np.zeros((G.N, 3))

        def span(col, a, z, I):
            if z < a:
                a, z = z, a
            cov = np.clip((np.minimum(e1, z) - np.maximum(e0, a)) / w, 0, 1)
            fr[:] += perc(I) * cov[:, None] * col

        def glow(col, c, wd, I):
            fr[:] += perc(I * np.exp(-((d - c) / wd) ** 2))[:, None] * col

        sky = keys(t, [(0, 0), (1.5, 0.14), (D - 1.5, 0.14), (D, 0)])
        fr += perc(sky) * NIGHT
        tw = np.zeros(G.N)
        tw[stars] = 0.26 * np.clip(np.sin(sfr * t + sph), 0, 1) ** 3
        fr += perc(tw * sky / 0.12)[:, None] * STAR
        fr += perc(sky / 0.12 * 0.13 * np.exp(-((d - mid) / 300) ** 2))[:, None] * PORCH
        fade = keys(t, [(D - 2.0, 1), (D - 0.2, 0)])

        # ---- the team, on whichever flight is live ----
        for li, leg in enumerate(lg):
            if not live(leg, t):
                continue
            squash, dim = 1.0, 1.0
            for a0, a1 in DUCKS:
                k = keys(b, [(a0, 0), (a0 + 0.5, 1), (a1 - 0.5, 1), (a1, 0)])
                squash -= 0.45 * k
                dim -= 0.6 * k
            if li == 1 and tb(LOOP[0]) <= t < tb(LOOP[1]):
                ph = 2 * np.pi * (t - tb(LOOP[0])) / (tb(LOOP[1]) - tb(LOOP[0]))
                dim *= 1 - 0.35 * (1 - np.cos(ph)) / 2   # upside down at the top of the loop
            gallop = 0.5 + 0.5 * np.cos(2 * np.pi * b)
            ding = 0.0
            if li == 1 and tb(DING) <= t < tb(DING) + 0.6:
                ding = np.exp(-(t - tb(DING)) / 0.2)
            q0 = at(leg, t, 0)
            for j, (kind, off) in enumerate(TEAM):
                q = at(leg, t, off * squash)
                ahead = at(leg, t, off * squash - 7) - q      # toward the nose
                s = np.sign(ahead) if ahead else 1.0
                if kind == 'nose':
                    span(NOSE, q - 4, q + 4, 0.95 * dim)
                    glow(NOSE, q, 30, 0.22 * dim)
                elif kind == 'deer':
                    lift = 0.12 * (gallop if j % 2 else 1 - gallop)
                    span(BONE, q - 8, q + 6 * s, (0.5 + lift) * dim)
                    span(BONE, q + 8 * s, q + 13 * s, 0.62 * dim)          # head
                elif kind == 'driver':
                    span(DRIVER, q - 5, q + 5, 0.62 * dim)
                else:
                    span(SLEIGH, q - 17, q + 17, 0.6 * dim)
                    span(GOLD, q + 15 * s, q + 19 * s, 0.6 * dim)          # the runner's curl
                if ding:
                    span(BEAM, q - 8, q + 8, 0.8 * ding)
            sl = at(leg, t, TEAM[-1][1] * squash)
            if li != 1 and 0 < sl < L and t > tb(ENTER + 2):
                for _ in range(3 if li == 2 else 1):
                    k = nxt % NP
                    nxt += 1
                    pt[k], px[k] = t, sl + rng.normal(0, 10) - 20 * np.sign(q0 - sl)

        lv = (t - pt) < pl
        if lv.any():
            u = (t - pt[lv]) / pl[lv]
            g = np.zeros(G.N)
            idx = np.clip(np.searchsorted(d, px[lv]), 0, G.N - 1)
            np.maximum.at(g, idx, 0.55 * (1 - u) * (0.6 + 0.4 * np.sin(25 * u + px[lv])))
            fr += perc(g)[:, None] * GOLD

        # ---- presents: falling, landed, popped ----
        for k, (bd, p) in enumerate(zip(DROPS, spots)):
            if b < bd:
                continue
            col = BOXES[k]
            u = (b - bd) / LAND
            bow = 0.3 * np.exp(-(t - tb(TADA)) / 0.6) if t > tb(TADA) else 0.0
            if u < 1:                                         # falling: blurred and dim, sharpening
                glow(col, p, 12 + 40 * (1 - u), 0.25 + 0.3 * u)
                continue
            opened = b >= bd + POP
            span(col, p - 12, p + 12, (0.32 if opened else 0.5) * fade + bow)
            span(GOLD, p - 2, p + 2, (0.45 if opened else 0.65) * fade)
            if b < bd + LAND + 0.6:                           # the thump
                glow(GOLD, p, 30, 0.5 * np.exp(-(b - bd - LAND) * BEAT / 0.12))
            if not opened:
                continue
            up = t - tb(bd + POP)
            if up < 0.5:
                glow(BEAM, p, 25, 0.85 * np.exp(-up / 0.15))
            if k == 0:                                        # jack-in-the-box
                ext = 40 + 38 * np.exp(-up / 1.0) * np.sin(2 * np.pi * 2.2 * up)
                for tr in (P['pass_t'][0], tb(TADA)):
                    if t > tr:
                        ext += 26 * np.exp(-(t - tr) / 0.8) * np.sin(2 * np.pi * 2.5 * (t - tr))
                ext += 3 * np.sin(2 * np.pi * b / 2)
                tip = p + 12 + ext
                for c in np.arange(p + 13, tip - 7, 6):
                    span(SPRING, c, c + 2.5, 0.42 * fade)
                span(CLOWN, tip - 7, tip + 7, 0.72 * fade + bow)
                span(NOSE, tip - 1.5, tip + 1.5, 0.85 * fade)
            elif k == 1:                                      # the bat
                if t < tb(LAP):
                    x = p - 110 * up + 15 * np.sin(5 * up)
                else:
                    x = at(lg[2], t, 0) - 45 + 8 * np.sin(10 * t) if live(lg[2], t) else -99
                if -30 < x < L + 30:
                    wg = 4 + 8 * (0.5 + 0.5 * np.sin(2 * np.pi * 4 * t))
                    span(BAT, x - 3, x + 3, 0.7 * fade)
                    span(WING, x - 3 - wg, x - 3, 0.45 * fade)
                    span(WING, x + 3, x + 3 + wg, 0.45 * fade)
            elif k == 3:                                      # the spider on its string
                off = 45 + 42 * np.exp(-up / 1.4) * np.sin(2 * np.pi * 1.6 * up)
                for tr in (P['pass_t'][3], tb(TADA)):
                    if t > tr:
                        off += 30 * np.exp(-(t - tr) / 1.0) * np.sin(2 * np.pi * 1.8 * (t - tr))
                x = p + 12 + off
                span(BEAM, p + 12, x - 5, 0.13 * fade)
                span(SPIDER, x - 5, x + 5, 0.72 * fade + bow)
                wig = 0.5 + 0.5 * np.sin(2 * np.pi * 3 * t)
                for j, lo in enumerate((7, 10, 13, 16)):
                    I = (0.3 + 0.2 * (wig if j % 2 else 1 - wig)) * fade
                    span(LEGS, x - lo - 1, x - lo + 0.5, I)
                    span(LEGS, x + lo - 0.5, x + lo + 1, I)

        # ---- the duck ----
        if b >= DROPS[2] + POP:
            x, hop = duck_x(P, t)
            if x is not None and -20 < x < L + 20:
                riding = t >= P['ride']
                bounce = 1 + (0.3 * np.sin(np.pi * hop) if hop is not None else 0)
                qk = max([np.exp(-(t - q) / 0.15) for q in QK if t >= q] + [0])
                span(DUCK, x - 6, x + 10, 0.62 * bounce * fade)     # facing left, after the sleigh
                span(DUCK, x - 9, x - 3, 0.75 * bounce * fade)
                span(BEAK, x - 13 - 3 * qk, x - 9, (0.7 + 0.3 * qk) * fade)
                if riding:
                    span(GOLD, x + 10, x + 12, 0.3)

        # ---- searchlights ----
        for c, lev in P['beam'](t):
            if lev > 0:
                glow(BEAM, c, 55, 0.5 * lev)
                glow(BEAM, c, 160, 0.13 * lev)
        for k, (bk, X) in enumerate(zip(BONKS, P['X'])):
            u = t - tb(bk)
            if 0 <= u < 0.8:
                glow(GOLD, X, 40 + 120 * u, 0.95 * np.exp(-u / 0.3))
                glow(BEAM, X, 20, 0.9 * np.exp(-u / 0.15))
            if 0 <= u < tb(DIZZY):
                for j in range(3):
                    a = 2 * np.pi * 1.2 * u + j * 2 * np.pi / 3
                    glow(GOLD, X + 45 * np.sin(a), 6, 0.45 * (0.6 + 0.4 * np.cos(a)) * (1 - u / tb(DIZZY)))

        # ---- ta-da: confetti from the porch, and the nose winks back in at the right end ----
        if t >= tb(TADA):
            u = t - tb(TADA)
            glow(GOLD, mid, 30 + 700 * u, 0.5 * np.exp(-u / 0.6))
            g = np.zeros((G.N, 3))
            on = t >= conf_t
            if on.any():
                a = t - conf_t[on]
                I = (0.25 + 0.45 * np.exp(-a / 0.5)) * (0.7 + 0.3 * np.sin(5 * a + conf_ph[on])) * fade
                np.maximum.at(g, conf_px[on], perc(I)[:, None] * np.array(CONFETTI)[conf_c[on]])
            fr += g
            nq = keys(t, [(tb(TADA), L + 20), (tb(TADA) + 0.4, L - 14)])
            blink = 1.0
            for wb in WINKS:
                if tb(wb) <= t < tb(wb) + 0.14:
                    blink = 0.0
            span(NOSE, nq - 4, nq + 4, 0.95 * blink * fade)
            glow(NOSE, nq, 30, 0.22 * blink * fade)
        out[f][G.path] = fr
    return out


# ---- music: a galop in G at 150, 2/4: tuba on the beat, horn 'pahs' and snare on the offbeats. TUNE twice
# while the presents fall (slide whistle down to each landing, a thump, then each surprise's own noise as it
# pops: a boing for the jack, a flutter and a squeak for the bat, quacks, a lower boing for the spider), the
# duck's BRIDGE on bassoon, then clarinet, while it hops, the tune's second half to send the sleigh off. Then
# SNEAKY in E minor on pizzicato and bassoon; each searchlight clunks on and hums where it points, and a
# swish passes over the ducking team. Ding: a snare roll and the TUNE flat out for the chase, a honk and a
# crash for each bonk, birdies while the beams reel, a slide whistle round the loop and up and away, two
# trombone wah-wahs as the beams sag off. A quack in the dark. Then the victory lap: TUNE up a tone in A with
# sleigh bells, the jack and the spider boinging as the team passes, the duck quacking aboard, and a ta-da;
# two music-box plinks for the winks. ----

VOICES = {'G': ('G3', 'B3', 'D4'), 'D7': ('F#3', 'A3', 'C4'), 'C': ('G3', 'C4', 'E4'), 'Am': ('A3', 'C4', 'E4'),
          'Em': ('G3', 'B3', 'E4'), 'B7': ('F#3', 'A3', 'D#4')}
ROOTS = {'G': ('G2', 'D2'), 'D7': ('D2', 'A1'), 'C': ('C2', 'G2'), 'Am': ('A1', 'E2'), 'Em': ('E2', 'B1'),
         'B7': ('B1', 'F#2')}


def score(M, G):
    from pixelhome.audio import SR, note as n, slide, whoosh
    xylo = M.sampler('Percussion/Xylo/*.wav', tune=-12)
    glock = M.sampler('Percussion/Glock/*.wav', tune=-12)
    tpt = M.sampler('Brass/Trumpet/stac/*.wav', tune=-12)
    tpt_s = M.sampler('Brass/Trumpet/sus/*.wav', tune=-12)
    horn = M.sampler('Brass/F Horn/stac/*.wav', tune=-12)
    horn_s = M.sampler('Brass/F Horn/sus/*.wav', tune=-12)
    tuba = M.sampler('Brass/Tuba/stac/*.wav', tune=-12)
    bsn = M.sampler('Woodwinds/Bassoon/stac/*.wav', tune=-12)
    clar = M.sampler('Woodwinds/Clarinet/stac/*.wav', tune=-12)
    pizz = M.sampler('Strings/Cello Section/pizzT/*.wav', tune=-12)
    box = M.synth('Plucks/Magic Music Box')
    snare = M.hits('VSCO 1 Percussion/drums/snare/drum3_marching/snare3_[fmp]*.wav')
    sroll = M.hits('Percussion/Snare2-rollSN_v[35]*.wav')
    bd = M.hits('VSCO 1 Percussion/drums/bass/bdrum_f_*.wav')
    bd_m = M.hits('VSCO 1 Percussion/drums/bass/bdrum_muted_m*.wav')
    crash = M.hits('VSCO 1 Percussion/varMetal/Cymbals/clash/crash_hit_ff*.wav')
    choke = M.hits('Percussion/cymbal-crashshort*.wav')
    timp = M.hits('Percussion/Timpani/Timpani1_Hit*.wav')
    slap = M.hits('VSCO 1 Percussion/varWood/slapstick[0-9].wav')
    wood = M.hits('VSCO 1 Percussion/varWood/wood_click*.wav')
    log = M.hits('Percussion/LogDrumLo*.wav')
    tri = M.hits('Percussion/Triangle3-Hit_v1*.wav')
    sleigh = M.hits('Percussion/Sleighbells_Hit*.wav')
    fall = M.hits('Brass/OldTrombone/Fall/*.wav')
    for name, gain, rev in (('tune', 0.26, 0.16), ('band', 0.18, 0.12), ('bass', 0.32, 0.06), ('drums', 0.22, 0.1),
                            ('fx', 0.2, 0.15), ('toys', 0.2, 0.15), ('hum', 0.07, 0.2), ('bells', 0.12, 0.2)):
        M.bus(name, gain=0.85 * gain, reverb=rev)

    L = G.length
    order = np.argsort(G.pd)
    xs, ds = G.pos[order, 0], G.pd[order]
    x0, x1 = xs.min(), xs.max()
    P = plan(G)
    lg, spots = P['legs'], P['spots']
    mid = float(G.pd[G.seg['Porch Front']].mean())

    def pan_at(d):                          # path distance -> left/right across the facade, from the street
        return 0.85 * (2 * (np.interp(np.clip(d, 0, L), ds, xs) - x0) / (x1 - x0) - 1)

    def mono(sig, pans):
        a = (np.clip(pans, -1, 1) + 1) * np.pi / 4
        return np.vstack([sig * np.cos(a), sig * np.sin(a)]) * np.sqrt(2)

    def tone(f, amp, harm=(1, .3, .12), dec=None):   # a plain voice along frequency curve f
        ph = 2 * np.pi * np.cumsum(f) / SR
        sig = sum(a * np.sin((k + 1) * ph) for k, a in enumerate(harm))
        env = np.clip(np.arange(len(f)) / (0.01 * SR), 0, 1)
        if dec:
            env *= np.exp(-np.arange(len(f)) / SR / dec)
        return amp * sig * env

    def boing(f0, dur=0.8, amp=0.4):
        u = np.arange(int(dur * SR)) / SR
        f = f0 * (1.6 - 0.6 * np.exp(-u / 0.1)) * (1 + 0.35 * np.exp(-u / 0.3) * np.sin(2 * np.pi * 8 * u))
        return tone(f, amp, (1, .4, .15), dec=dur / 3)

    def quack(f0=560, amp=0.5):
        u = np.arange(int(0.17 * SR)) / SR
        f = f0 * (1 - 0.25 * u / 0.17)
        ph = np.cumsum(f) / SR
        saw = 2 * (ph % 1) - 1
        sp = np.fft.rfft(saw)
        fr = np.fft.rfftfreq(len(saw), 1 / SR)
        sp *= np.exp(-((fr - 1150) / 500) ** 2) + 0.6 * np.exp(-((fr - 2500) / 600) ** 2)
        sig = np.fft.irfft(sp, len(saw))
        sig *= np.clip(u / 0.01, 0, 1) * np.clip((0.17 - u) / 0.05, 0, 1)
        return amp * sig / (np.abs(sig).max() + 1e-9)

    def honk(amp=0.45):
        u = np.arange(int(0.4 * SR)) / SR
        sig = sum(2 * ((f * u) % 1) - 1 for f in (330.0, 415.0))
        sp = np.fft.rfft(sig)
        sp *= 1 / np.sqrt(1 + (np.fft.rfftfreq(len(sig), 1 / SR) / 1800) ** 4)
        sig = np.fft.irfft(sp, len(sig)) * np.clip(u / 0.01, 0, 1) * np.clip((0.4 - u) / 0.06, 0, 1)
        return amp * sig / (np.abs(sig).max() + 1e-9)

    def line(inst, notes, b0, bus, vel, shift=0, gain=1.0, pan=0.0, beats=None):
        for b, m, ln in notes:
            if beats is not None and not (beats[0] <= b < beats[1]):
                continue
            off = b - (beats[0] if beats else 0)
            M.add(bus, inst.play(n(m) + shift, vel, dur=ln * BEAT * 0.85), tb(b0 + off), gain, pan)

    def band(b0, chords, shift=0, loud=1.0, snares=True):
        """The galop under a tune: chords one a bar of two beats starting at beat b0."""
        for k, c in enumerate(chords):
            for j in range(2):
                b = b0 + 2 * k + j
                M.add('bass', tuba.play(n(ROOTS[c][j]) + shift, int(100 * loud)), tb(b), 1.0)
                for m in VOICES[c]:
                    M.add('band', horn.play(n(m) + shift, int(82 * loud), dur=0.15), tb(b + 0.5), 0.45, -0.2)
                if snares:
                    M.add('drums', snare.play(int(85 * loud)), tb(b + 0.5), 0.55, 0.15)
            M.add('drums', bd.play(int(100 * loud)), tb(b0 + 2 * k), 0.7)

    # ---- intro and the deliveries ----
    s = sleigh.play(100, dur=tb(4))
    M.add('bells', s * np.linspace(0.2, 1, s.shape[1]), 0.3, 1.0, 0.8)
    band(4, ['G', 'D7'], loud=0.8, snares=False)
    band(8, TUNE_CHORDS)
    line(xylo, TUNE, 8, 'tune', 105)
    line(tpt, TUNE, 8, 'tune', 90, gain=0.6, pan=0.15)
    band(24, TUNE_CHORDS[:4])
    line(tpt, TUNE, 24, 'tune', 105, pan=0.1, beats=(0, 8))
    line(glock, TUNE, 24, 'tune', 80, shift=12, gain=0.35, pan=-0.1, beats=(0, 8))
    for b0, lead in ((32, bsn), (40, clar)):                  # the duck's tune while it hops
        band(b0, BRIDGE_CHORDS, loud=0.85)
        line(lead, BRIDGE, b0, 'tune', 105, shift=-12 if lead is bsn else 0, gain=1.0, pan=0.1)
        line(xylo if b0 == 40 else clar, BRIDGE, b0, 'tune', 85, gain=0.5, pan=-0.1)
    band(48, TUNE_CHORDS[4:])
    line(xylo, TUNE, 48, 'tune', 105, beats=(8, 16))
    line(tpt, TUNE, 48, 'tune', 100, gain=0.7, pan=0.15, beats=(8, 16))
    M.add('drums', choke.play(100), tb(56), 0.5)
    for b in np.arange(ENTER, 56, 0.5):                       # sleigh bells along with the team
        q = at(lg[0], tb(b), 100)
        if -50 < q < L + 50:
            M.add('bells', sleigh.play(70), tb(b), 0.6, float(pan_at(q)))
    for k, (bd_, p) in enumerate(zip(DROPS, spots)):
        pp = float(pan_at(p))
        M.add('fx', slide(0, tb(LAND), 1500, 500, tb(LAND) + 0.05, amp=0.25), tb(bd_), 0.8, pp)
        M.add('drums', log.play(110), tb(bd_ + LAND), 0.9, pp)
        tp = tb(bd_ + POP)
        M.add('drums', choke.play(80), tp, 0.3, pp)
        pop = M.rng.normal(0, 1, int(0.05 * SR)) * np.exp(-np.arange(int(0.05 * SR)) / SR / 0.008)
        M.add('fx', mono(pop * 0.6, np.full(len(pop), pp)), tp, 1.0)
        if k == 0:
            M.add('toys', mono(boing(330), np.full(int(0.8 * SR), pp)), tp, 1.0)
        elif k == 1:
            for j in range(14):
                M.add('toys', wood.play(60, pitch=8.0), tp + 0.045 * j, 0.6, float(pan_at(p - 110 * 0.045 * j)))
            M.add('toys', slide(0, 0.18, 1500, 2000, 0.22, amp=0.12), tp + 0.1, 1.0, pp)
        elif k == 3:
            M.add('toys', mono(boing(200, 1.2), np.full(int(1.2 * SR), pp)), tp, 1.0)
    for j in range(HOPS):                                     # the duck's hops
        t = tb(DROPS[2] + POP + j)
        M.add('toys', wood.play(55, pitch=float(j % 2) * 2), t, 0.5, float(pan_at(duck_x(P, t + 0.2)[0])))
    for t in quacks(P):
        x = duck_x(P, t)[0]
        if x is not None:
            big = 1.3 if abs(t - tb(DROPS[2] + POP + HOPS + 1)) < 0.01 else 1.0
            M.add('toys', mono(quack(amp=0.5 * big), np.full(int(0.17 * SR), float(pan_at(x)))), t, 1.0)

    # ---- sneaking back, the searchlights ----
    for b0 in (56, 60):                                       # tiptoeing in
        line(pizz, SNEAKY, b0, 'tune', 85, gain=0.6, beats=(0, 4))
    for b0 in (64, 72):
        line(bsn, SNEAKY, b0, 'tune', 100, gain=1.0, pan=0.2)
        for k, c in enumerate(SNEAKY_CHORDS):
            for j in range(2):
                M.add('bass', pizz.play(n(ROOTS[c][j]), 100), tb(b0 + 2 * k + j), 1.0)
    for k, ton in enumerate(BEAM_ON):
        c = P['beam'](tb(ton) + 0.4)[k][0]
        M.add('drums', bd_m.play(115), tb(ton), 1.0, float(pan_at(c)))
        M.add('bass', tuba.play(n('E1'), 115, dur=0.3), tb(ton), 0.8, float(pan_at(c)))
    tt = np.arange(tb(BEAM_ON[0]), tb(max(BEAM_OFF)) + 1.3, 0.01)
    bm = np.array([P['beam'](t) for t in tt])                # (T, 2 beams, centre/level)
    u = np.arange(int((tt[-1] - tt[0]) * SR)) / SR
    for k, f0 in enumerate((55.0, 61.7)):
        lev = np.interp(u, tt - tt[0], bm[:, k, 1])
        c = np.interp(u, tt - tt[0], bm[:, k, 0])
        rise = 1 + 0.08 * np.interp(u + tt[0], [tb(BEAM_ON[k]), tb(DING)], [0, 1])
        ph = np.cumsum(f0 * rise) / SR
        saw = (2 * (ph % 1) - 1) + 0.5 * (2 * ((2 * ph) % 1) - 1)
        M.add('hum', mono(saw * lev, pan_at(c)), tt[0], 1.0)
    for a0, a1 in DUCKS[:1]:                                  # the beam passes over the ducking team
        sw = whoosh(tb(a1 - a0), 300, 1600, 0.4, seed=5)[0]
        cs = [P['beam'](tb(a0) + x)[1][0] for x in np.linspace(0, tb(a1 - a0), 32)]
        M.add('fx', mono(sw, np.interp(np.arange(len(sw)), np.linspace(0, len(sw), 32), pan_at(np.array(cs)))),
              tb(a0), 0.8)
        M.add('tune', bsn.play(n('B3'), 80, dur=tb(a1 - a0)), tb(a0), 0.6, 0.2)

    # ---- ding, the chase, the bonks, the loop and the escape ----
    pd_ = float(pan_at(_sneak(tb(DING), L)))
    M.add('fx', tri.play(120), tb(DING), 1.0, pd_)
    M.add('tune', glock.play(n('E6'), 120), tb(DING), 0.8, pd_)
    r = sroll.play(100, dur=tb(ZOOM + 1 - DING))
    M.add('drums', r * np.linspace(0.3, 1, r.shape[1]), tb(DING) + 0.1, 0.7)
    band(82, TUNE_CHORDS, loud=1.1)
    for b in np.arange(82, 98, 1):
        M.add('drums', snare.play(95), tb(b), 0.5, -0.1)
        if b % 2 == 0:
            M.add('drums', timp.play(100), tb(b), 0.5)
    line(xylo, TUNE, 82, 'tune', 115, gain=1.1)
    line(tpt, TUNE, 82, 'tune', 110, gain=0.8, pan=0.15)
    for bk, X in zip(BONKS, P['X']):
        px = float(pan_at(X))
        M.add('fx', mono(honk(), np.full(int(0.4 * SR), px)), tb(bk), 1.0)
        M.add('drums', crash.play(115), tb(bk), 0.7, px)
        M.add('drums', slap.play(120), tb(bk), 0.9, px)
        M.add('drums', timp.play(115, pitch=-4), tb(bk), 0.7, px)
        for j in range(int(tb(DIZZY) / 0.21)):             # birdies circling the bump
            M.add('toys', glock.play(n(['B5', 'E6', 'G5', 'D6'][j % 4]), 60 - 2 * j), tb(bk) + 0.3 + 0.21 * j,
                  0.4, float(np.clip(px + 0.25 * np.sin(2 * np.pi * 1.2 * 0.21 * j), -1, 1)))
    tl = tb(LOOP[1]) - tb(LOOP[0])
    u = np.arange(int(tl * SR)) / SR
    f = 520 * 2 ** (1.4 * (1 - np.cos(2 * np.pi * u / tl)) / 2)
    pl = pan_at(np.array([_sneak(tb(LOOP[0]) + x, L) for x in u[::480]]))
    M.add('fx', mono(tone(f, 0.22, (1, .12, 0)), np.interp(np.arange(len(u)), np.arange(len(pl)) * 480, pl)),
          tb(LOOP[0]), 1.0)
    te = tb(ESCAPE) - tb(LOOP[1])
    M.add('fx', slide(0, te, 500, 1600, te, amp=0.22), tb(LOOP[1]), 1.0, -0.8)
    sw = whoosh(te, 400, 3000, 0.4, seed=8)
    M.add('fx', sw, tb(LOOP[1]), 0.8, -0.8)
    for k, toff in enumerate(BEAM_OFF):
        c = P['beam'](tb(toff))[k][0]
        M.add('band', fall.play(105), tb(toff), 0.8, float(pan_at(c)))
        M.add('drums', bd_m.play(90), tb(toff), 0.7, float(pan_at(c)))
    for b in (100, 101, 103):
        M.add('tune', pizz.play(n(['E3', 'B2', 'E3'][b % 3]), 70), tb(b), 0.5)

    # ---- the victory lap and the ta-da ----
    M.add('drums', crash.play(118), tb(LAP), 0.8, 0.8)
    band(LAP, TUNE_CHORDS, shift=2, loud=1.1)
    line(tpt, TUNE, LAP, 'tune', 115, shift=2, gain=1.0, pan=0.1)
    line(xylo, TUNE, LAP, 'tune', 110, shift=2, gain=0.9)
    line(glock, TUNE, LAP, 'tune', 80, shift=14, gain=0.35, pan=-0.1)
    band(LAP + 16, TUNE_CHORDS[4:], shift=2, loud=1.2)
    line(tpt, TUNE, LAP + 16, 'tune', 120, shift=2, beats=(8, 16))
    line(horn_s, TUNE, LAP + 16, 'tune', 110, shift=2 - 12, gain=0.6, pan=-0.2, beats=(8, 16))
    line(xylo, TUNE, LAP + 16, 'tune', 115, shift=2, beats=(8, 16))
    for b in np.arange(LAP, TADA, 0.5):
        q = at(lg[2], tb(b), 100)
        if -50 < q < L + 50:
            M.add('bells', sleigh.play(90), tb(b), 0.7, float(pan_at(q)))
    T3 = lg[2][0][-1] - tb(LAP)
    sw = whoosh(T3, 300, 2600, 0.4, seed=12)[0]
    u = np.arange(len(sw)) / SR
    M.add('fx', mono(sw, pan_at(np.array([at(lg[2], tb(LAP) + x, 100) for x in u[::480]]).repeat(480)[:len(sw)])),
          tb(LAP), 0.7)
    for k, f0 in ((0, 330), (3, 200)):
        pp = float(pan_at(spots[k]))
        for tr in (P['pass_t'][k], tb(TADA)):
            M.add('toys', mono(boing(f0), np.full(int(0.8 * SR), pp)), tr, 0.8)
    for t in np.arange(tb(LAP) + 0.5, lg[2][0][-1] - 1, 1.7):  # the bat squeaking ahead of the team
        M.add('toys', slide(0, 0.12, 1600, 2100, 0.16, amp=0.08), t, 1.0, float(pan_at(at(lg[2], t, 0) - 45)))
    th = tb(TADA)
    for m in ('A3', 'C#4', 'E4', 'A4'):
        M.add('tune', tpt.play(n(m), 120, dur=0.18), th, 0.6)
        M.add('tune', tpt_s.play(n(m), 124, dur=D - th - tb(1) - 0.5), th + tb(1), 0.55)
        M.add('band', horn_s.play(n(m) - 12, 118, dur=D - th - tb(1) - 0.5), th + tb(1), 0.55)
    M.add('bass', tuba.play(n('A1'), 120), th, 1.0)
    M.add('bass', tuba.play(n('A1'), 127), th + tb(1), 1.2)
    M.add('drums', bd.play(120), th + tb(1), 1.0)
    M.add('drums', crash.play(124), th + tb(1), 1.0)
    M.add('drums', timp.play(124), th + tb(1), 0.9)
    M.add('fx', slide(0, 0.5, 400, 1500, 0.55, amp=0.2), th, 0.9)
    for j in range(20):                                       # confetti, glock sparkles running outward
        side = (-1) ** j
        M.add('toys', glock.play(n(['A5', 'C#6', 'E6', 'B5'][j % 4]), 70), th + tb(1) + 0.06 * j, 0.5,
              float(side * min(0.85, 0.08 * j)))
    for wb in WINKS:
        M.add('toys', box.render([(0.0, n('E5'), 90, 0.15)], 2.0), tb(wb), 1.0, float(pan_at(L - 14)))
