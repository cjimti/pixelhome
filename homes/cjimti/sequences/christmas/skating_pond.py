"""Skating Pond: Porch Front is a frozen pond, icy blue-white with glints running across it; the rest of the
roofline is a snowy bank lit by warm lamps that come on one by one. Four skaters in bright scarves glide out of
the porch sides and carve figure-eights, each scarf trailing behind its skater and every turn scraping a puff of
white off the ice. Red and green meet in the middle and spin, faster and tighter, in a whirl of every colour,
and strike a pose. Then a show-off in gold shoots in from the far end of Right and laps the pond, faster and
wider each time, nearly flattening three of the others, wobbles, and goes down in a spray of ice. A hush. He gets
up, everyone takes hands, and the chain sets off: out along Porch Left and Left, up the Side, round and back
across the whole house, stretching as it speeds up, until red digs in at the end of the porch and the whip cracks:
the others swing past her and the show-off, on the end, is flung off the free end of Right into a snowbank. The
house bursts into scarf colours, and he skates back in for the last chord.

Music: an original waltz in G at a bar a second (180 crotchets a minute), oom-pah-pah in pizzicato under a flute
tune for the skaters coming out, a lamp's glockenspiel note as each lamp lights, a scrape of noise for every turn
on the ice. The spin goes to C with legato strings and a harp that plucks a chord tone every time the pair cross,
faster as they spin. The show-off gets the tune on a cocky trumpet with xylophone, a skid on every turn, a slide
whistle, choked cymbal and a horn stab for each near miss, a wobbling trombone, and a crash with a shower of glass
for the tumble. A music box alone for the hush; a rising note as each skater joins the chain; then the whole band,
sleigh bells on every beat, brass taking over at the U-turn, a drum roll into the crack (a slapstick on the
downbeat), a slide whistle up for the fling and a thump in the snow, and a big cadence."""
import numpy as np
from pixelhome.fx import DT, hexc, light, keys, smoothstep, lerp, Flicker, nframes

CODE = 'CH14'
TITLE = 'Skating Pond'
KIND = 'show'
DESCRIPTION = ('Skaters in bright scarves carve figure-eights on a frozen pond, a pair spins in a whirl of colour, '
               'a show-off laps too fast and takes a tumble, and a crack-the-whip chain flings him off the end of the house.')
VOICEOVER = "Lace up your skates. The pond is frozen, and somebody is about to show off."

D = 86.0
SEED = 14

ICE = hexc('#3a9cff')
GLINT = hexc('#f0f8ff')
SNOW = hexc('#b8ccff')
LAMP = hexc('#ff9a30')
CORE = hexc('#fff2e0')
SCARF = [hexc(c) for c in ('#ff1208', '#10e040', '#ff10b0', '#7a28ff', '#ffa400')]   # red, green, magenta, violet, gold
RED, GREEN, MAGENTA, VIOLET, GOLD = range(5)

# the roofline along the path: Side 0-490, Left 492-892, Porch Left 896-1309, Porch Front 1314-1658 (the pond),
# Porch Right 1662-2030, Right 2036-2512 (free end)
POND = (1314.0, 1658.0)
C = 1486.0                                         # the middle of the pond
PL_FRONT, PR_FRONT, END = 900.0, 2026.0, 2512.0
LAMPS = (120, 340, 560, 780, 1010, 1190, 1790, 1940, 2140, 2300, 2450)

# ---- the beat grid: a waltz at a bar a second, bar 0 on 1.0 s; every big moment is on a downbeat ----
T0, BAR, BEAT = 1.0, 1.0, 1.0 / 3


def bt(bar, beat=0.0):
    return T0 + bar * BAR + beat * BEAT


LAMP_T = [bt(0, i) for i in range(len(LAMPS))]     # the lamps light on the beats of the intro, from the porch out
ENTER = {RED: bt(4), GREEN: bt(6), MAGENTA: bt(9), VIOLET: bt(12)}
T_SPIN, T_POSE = bt(20), bt(31)                    # the pair spin, and the pose
T_SHOW = bt(32)                                    # the show-off appears at the free end of Right
NEAR = [(bt(39), GREEN, 40.0), (bt(42), MAGENTA, -40.0), (bt(45, 2.7), VIOLET, 45.0)]   # (t, who, jump)
T_WOBBLE = bt(46)
T_FALL = bt(49)                                    # the tumble
T_UP = bt(53)                                      # he gets up
JOIN = [bt(55), bt(55, 2.25), bt(56, 1.5), bt(57, 0.75), bt(58)]   # each skater takes a hand, red first
T_GO, T_TURN, T_CRACK = bt(59), bt(66), bt(75)     # the chain sets off; the U-turn at the back; the whip cracks
T_PLOP = T_CRACK + 0.95                            # the show-off lands in the snow past the end of Right
T_WAVE = bt(76, 1)                                 # the colours run back across the house
T_BACK = (bt(78), bt(80))                          # he skates back in
T_FINAL = bt(82)
LAG = 0.32                                         # the chain: each skater follows the one ahead this far behind
CHAIN = [RED, GREEN, MAGENTA, VIOLET, GOLD]
SLOT = [C - 10 + 25 * k for k in range(5)]         # where each stands in the chain before it sets off
TURN_AT, STOP_AT = 40.0, 2040.0                    # the chain turns at the back of the Side and stops at Right
REST = [STOP_AT + 75 * k for k in range(4)]        # where the first four come to rest after the crack
GOLD_BACK = 2350.0


# ---- the skaters' tracks ----
def _glide(p0, p1, t0, t1):
    return lambda t: p0 + (p1 - p0) * float(smoothstep(t0, t1, t))


def _eight(c, a, period, t0, ph=0.0):
    """A figure-eight seen edge on: a long swing with a little loop in it."""
    return lambda t: c + a * np.sin(2 * np.pi * (t - t0) / period + ph) + 0.28 * a * np.sin(4 * np.pi * (t - t0) / period + ph)


def _sway(c, ph=0.0, jumps=()):
    """Standing on the bank, rocking on the blades; each jump (t, by) is a leap out of the show-off's way."""
    def f(t):
        p = c + 5 * np.sin(2 * np.pi * t / 2.0 + ph)
        for tj, by in jumps:
            p += by * float(smoothstep(tj - 0.05, tj + 0.18, t))
        return p
    return f


def _spin_table():
    tt = np.arange(nframes(D)) * DT
    rate = np.array([keys(t, [(T_SPIN, 0.35), (T_SPIN + 3, 0.8), (T_POSE - 1.5, 3.0), (T_POSE, 3.2)]) for t in tt])
    theta = np.cumsum(rate * (tt >= T_SPIN)) * DT * 2 * np.pi
    return tt, theta


_TT, _THETA = _spin_table()


def spin_theta(t):
    return float(np.interp(t, _TT, _THETA))


def spin_r(t):
    return float(keys(t, [(T_SPIN, 70), (T_POSE - 2, 24), (T_POSE, 20)]))


def _spinner(sign):
    return lambda t: C + sign * spin_r(t) * np.cos(spin_theta(t))


SHOW_LAPS = [(T_SHOW, 2570), (T_SHOW + 3.0, 1335), (bt(36, 1.5), 1635), (bt(37, 2.4), 1325), (NEAR[0][0], 1700),
             (bt(40, 0.3), 1300), (bt(41, 0.3), 1690), (NEAR[1][0], 1276), (bt(42, 2.7), 1700), (bt(43, 2.1), 1240),
             (bt(44, 1.5), 1720), (bt(45, 0.6), 1236), (NEAR[2][0], 1790), (bt(46, 2.4), 1330), (bt(47, 2.1), 1710),
             (bt(49, 1.8), 1390)]


def _show_laps(t):
    p = float(keys(t, SHOW_LAPS))
    w = smoothstep(T_WOBBLE - 0.4, T_FALL - 0.5, t) * (t < T_FALL)
    return p + 11 * w * np.sin(2 * np.pi * 6.5 * t) * np.sin(2 * np.pi * 0.9 * t + 1)


_P50 = _show_laps(T_FALL)
_V50 = (_show_laps(T_FALL) - _show_laps(T_FALL - 0.05)) / 0.05
FALL_AT = _P50
SLIDE_TAU = 0.6


def _belly(t):
    return _P50 + _V50 * SLIDE_TAU * (1 - np.exp(-(t - T_FALL) / SLIDE_TAU))


LIE_AT = _belly(T_FALL + 6)


def _lead_table():
    """The chain leader's path: away from the pond at 100 u/s (as if the chain had been rolling), accelerating out to
    the back of the Side and slowing for the U-turn, then faster and faster all the way to the stop at Right."""
    tt = np.arange(T_GO - 2, D + 1, DT / 4)
    p = np.empty_like(tt)
    u = np.clip((tt - T_GO) / (T_TURN - T_GO), 0, 1)
    dist1 = SLOT[0] - TURN_AT
    b = (dist1 - 100 * (T_TURN - T_GO) / 2) * np.pi / (2 * (T_TURN - T_GO))
    v = 100 * (1 - u) + b * np.sin(np.pi * u)
    leg1 = SLOT[0] - np.cumsum(v) * (DT / 4)
    leg1 -= leg1[np.searchsorted(tt, T_GO)] - SLOT[0]
    leg1 = np.where(tt < T_GO, SLOT[0] + 100 * (T_GO - tt), leg1)
    leg1 = np.where(tt > T_TURN, TURN_AT, leg1)
    w = np.clip((tt - T_TURN) / (T_CRACK - T_TURN), 0, 1)
    leg2 = TURN_AT + (STOP_AT - TURN_AT) * w ** 1.7
    p = np.where(tt <= T_TURN, leg1, leg2)
    return tt, p


_LT, _LP = _lead_table()
V_CRACK = (STOP_AT - TURN_AT) * 1.7 / (T_CRACK - T_TURN)


def lead(t):
    return float(np.interp(t, _LT, _LP))


def _chain(k):
    def f(t):
        if t < T_GO:
            return SLOT[k]
        return lead(t - k * LAG)
    return f


def _cracked(k):
    s = lead(T_CRACK - k * LAG)
    if k == 0:
        return lambda t: STOP_AT
    if k < 4:
        v = V_CRACK * (1 + 0.6 * k)
        tau = (REST[k] - s) / v
        return lambda t: REST[k] + (s - REST[k]) * np.exp(-(t - T_CRACK) / tau)
    return lambda t: s + 1150 * (t - T_CRACK) + 300 * (t - T_CRACK) ** 2


GATHER = {RED: 1336, MAGENTA: 1362, GREEN: 1440, VIOLET: 1466}

TRACKS = {
    RED: [(ENTER[RED], ENTER[RED] + 2.8, _glide(PL_FRONT, 1430, ENTER[RED], ENTER[RED] + 2.8)),
          (bt(7, 2), bt(19), _eight(1430, 80, 4.0, bt(7, 2))),
          (T_SPIN, T_POSE, _spinner(1)),
          (T_SHOW + 1, T_FALL + 1, _sway(1180, 0.3)),
          (T_FALL + 2.3, T_UP + 1.6, _sway(GATHER[RED], 1.0)),
          (JOIN[0], T_GO, _chain(0)), (T_GO, T_CRACK, _chain(0)), (T_CRACK, D + 1, _cracked(0))],
    GREEN: [(ENTER[GREEN], ENTER[GREEN] + 2.8, _glide(PR_FRONT, 1545, ENTER[GREEN], ENTER[GREEN] + 2.8)),
            (bt(9, 1), bt(19), _eight(1545, 80, 4.0, bt(9, 1), np.pi)),
            (T_SPIN, T_POSE, _spinner(-1)),
            (T_SHOW + 1, T_FALL + 1, _sway(1728, 2.0, [(NEAR[0][0], NEAR[0][2])])),
            (T_FALL + 2.3, T_UP + 1.6, _sway(GATHER[GREEN], 2.5)),
            (JOIN[1], T_GO, _chain(1)), (T_GO, T_CRACK, _chain(1)), (T_CRACK, D + 1, _cracked(1))],
    MAGENTA: [(ENTER[MAGENTA], ENTER[MAGENTA] + 2.6, _glide(PL_FRONT, 1350, ENTER[MAGENTA], ENTER[MAGENTA] + 2.6)),
              (bt(12), bt(19), _eight(1350, 45, 3.0, bt(12))),
              (T_SPIN + 1, T_POSE - 0.5, _eight(1268, 30, 3.0, T_SPIN + 1)),
              (T_SHOW + 1, T_FALL + 1, _sway(1258, 4.0, [(NEAR[1][0], NEAR[1][2])])),
              (T_FALL + 2.3, T_UP + 1.6, _sway(GATHER[MAGENTA], 3.5)),
              (JOIN[2], T_GO, _chain(2)), (T_GO, T_CRACK, _chain(2)), (T_CRACK, D + 1, _cracked(2))],
    VIOLET: [(ENTER[VIOLET], ENTER[VIOLET] + 2.6, _glide(PR_FRONT, 1610, ENTER[VIOLET], ENTER[VIOLET] + 2.6)),
             (bt(15), bt(19), _eight(1610, 40, 3.0, bt(15), np.pi)),
             (T_SPIN + 1, T_POSE - 0.5, _eight(1700, 30, 3.0, T_SPIN + 1, np.pi)),
             (T_SHOW + 1, T_FALL + 1, _sway(1804, 5.0, [(NEAR[2][0], NEAR[2][2])])),
             (T_FALL + 2.3, T_UP + 1.6, _sway(GATHER[VIOLET], 0.5)),
             (JOIN[3], T_GO, _chain(3)), (T_GO, T_CRACK, _chain(3)), (T_CRACK, D + 1, _cracked(3))],
    GOLD: [(T_SHOW, T_FALL, _show_laps),
           (T_FALL, T_UP, _belly),
           (T_UP + 0.4, T_UP + 1.6, lambda t: LIE_AT + 4 * np.sin(2 * np.pi * 2 * t)),
           (JOIN[4], T_GO, _chain(4)), (T_GO, T_CRACK, _chain(4)), (T_CRACK, T_CRACK + 1.4, _cracked(4)),
           (T_BACK[0], T_BACK[1], _glide(2600, GOLD_BACK, T_BACK[0], T_BACK[1])),
           (T_BACK[1], D + 1, _sway(GOLD_BACK, 0.0))],
}


def track(k, t):
    segs = TRACKS[k]
    if t < segs[0][0]:
        return np.nan
    for i, (t0, t1, f) in enumerate(segs):
        if t0 <= t < t1:
            return float(f(t))
        if i + 1 < len(segs) and t1 <= t < segs[i + 1][0]:
            a, b = float(f(t1)), float(segs[i + 1][2](segs[i + 1][0]))
            if k == GOLD and i == 5:          # flung off: away until he skates back in
                return np.nan
            return a + (b - a) * float(smoothstep(t1, segs[i + 1][0], t))
    return float(segs[-1][2](segs[-1][1]))


def plan():
    """Every skater's position, brightness and width per frame, and the scrapes: what render() and score() share."""
    F = nframes(D)
    tt = np.arange(F) * DT
    pos = np.array([[track(k, t) for t in tt] for k in range(5)])
    vis = np.zeros((5, F))
    for k in range(4):
        vis[k] = smoothstep(ENTER[k], ENTER[k] + 0.4, tt)
    vis[GOLD] = (tt >= T_SHOW).astype(float)
    lying = smoothstep(T_FALL, T_FALL + 0.3, tt) * (1 - smoothstep(T_UP, T_UP + 0.2, tt))
    vis[GOLD] *= 1 - 0.6 * lying
    width = np.ones((5, F))
    width[GOLD] += 1.5 * lying
    # scrapes: a skater turning at speed (not the pair spinning, not the chain, not the show-off on his belly)
    vel = np.gradient(np.nan_to_num(pos, nan=-999.0), DT, axis=1)
    scrapes = []
    for k in range(5):
        last = -9.0
        for f in range(2, F - 1):
            t = tt[f]
            if (T_SPIN <= t < T_POSE and k in (RED, GREEN)) or t >= T_FALL - 0.1 or np.isnan(pos[k, f]):
                continue
            if vel[k, f - 1] * vel[k, f] < 0 and np.abs(vel[k, max(0, f - 20):f]).max() > 60 and t - last > 0.4:
                scrapes.append((t, k, pos[k, f]))
                last = t
    scrapes.sort()
    # the pair passing each other in the spin: every half turn
    th = np.array([spin_theta(t) for t in tt])
    n_half = np.floor((th - np.pi / 2) / np.pi)
    crossings = [tt[f] for f in range(1, F) if n_half[f] > n_half[f - 1] and T_SPIN < tt[f] < T_POSE]
    return pos, vis, width, scrapes, crossings


def _spray(seed, n, at, vmin, vmax, tau=(0.3, 0.6), life=(0.8, 1.8)):
    rng = np.random.default_rng(seed)
    v = rng.uniform(vmin, vmax, n) * rng.choice([-1, 1], n)
    return at, v, rng.uniform(*tau, n), rng.uniform(*life, n), rng.uniform(4, 12, n)


def render(G, seed=SEED):
    rng = np.random.default_rng(seed)
    F = nframes(D)
    out = np.zeros((F, G.N, 3))
    x = G.pd[G.path]
    pond = (x >= POND[0] - 2) & (x <= POND[1] + 2)
    bank = ~pond
    pos, vis, width, scrapes, crossings = plan()
    lamps = np.array(LAMPS, float)
    lamp_fl = Flicker(rng, len(lamps), 0.1, 0.5)
    order = np.argsort(np.abs(lamps - C))
    lamp_on = np.empty(len(lamps))
    lamp_on[order] = LAMP_T
    snow_tw = Flicker(rng, G.N, 0.05, 0.3)
    glints = Flicker(rng, G.N, 0.2, 0.9)
    stripe_col = np.array(SCARF)
    fall = _spray(seed + 1, 80, FALL_AT, 150, 900)
    pose = _spray(seed + 2, 40, C, 100, 500, (0.3, 0.5), (0.6, 1.2))
    plop = _spray(seed + 3, 30, END - 4, 80, 400, (0.2, 0.4), (0.6, 1.4))

    def spray(sp, t0, t, col, amp):
        at, v, tau, life, tw = sp
        a = t - t0
        if a < 0 or a > life.max():
            return 0
        p = at + v * tau * (1 - np.exp(-a / tau))
        e = np.clip(1 - a / life, 0, 1) ** 1.5 * (0.7 + 0.3 * np.sin(tw * a * 6.28))
        g = (e[:, None] * np.exp(-((x[None] - p[:, None]) / 5) ** 2)).max(0)
        return light(col, amp * g)

    for f in range(F):
        t = f * DT
        fr = np.zeros((G.N, 3))
        master = keys(t, [(0, 0), (0.6, 1), (D - 1.6, 1), (D - 0.1, 0)])
        finale = smoothstep(T_WAVE, T_WAVE + 2.2, t)

        # the bank: snow glittering faintly under warm lamps, which light one by one in the intro
        snow = 0.13 * smoothstep(0.3, 1.5, t) * (1 + 0.5 * np.clip(snow_tw(t), 0, None) ** 3)
        fr[bank] += light(SNOW, snow[bank])
        on = smoothstep(lamp_on, lamp_on + 0.15, t)
        flash = np.exp(-np.clip(t - lamp_on, 0, None) / 0.25) * (t >= lamp_on)
        lvl = on * (0.5 * (1 + 0.06 * lamp_fl(t)) + 0.4 * flash) * (1 + 0.5 * finale)
        if T_FALL <= t < T_FALL + 0.8:                       # the lamps shiver with the crash
            lvl = lvl * (1 + 0.25 * np.sin(2 * np.pi * 14 * t) * np.exp(-(t - T_FALL) / 0.3))
        d = x[:, None] - lamps[None]
        fr += light(LAMP, (lvl[None] * np.exp(-(d / 14) ** 2)).max(1))
        fr += light(LAMP, (0.45 * lvl[None] * np.exp(-(d / 45) ** 2)).max(1))

        # the pond: ice blue with glints running across it and twinkles in the surface
        ice = smoothstep(0.0, 1.2, t) * (0.42 - 0.1 * smoothstep(T_FALL + 0.5, T_FALL + 1.5, t)
                                         * (1 - smoothstep(T_UP, T_UP + 2, t)) + 0.12 * finale)
        run = (0.5 + 0.5 * np.sin(x / 26 - 1.3 * t)) ** 6 + (0.5 + 0.5 * np.sin(x / 41 + 0.8 * t)) ** 8
        tw = np.clip(glints(t), 0, None) ** 4
        fr[pond] += light(ICE, ice) + light(GLINT, (ice * (0.5 * run + 0.4 * tw))[pond])

        # the spin: a whirl of every scarf colour around the pair, wider and brighter as they speed up
        if T_SPIN <= t < T_POSE + 0.6:
            env = keys(t, [(T_SPIN, 0), (T_SPIN + 2.5, 0.45), (T_POSE - 1.2, 1), (T_POSE, 1), (T_POSE + 0.6, 0)])
            th = spin_theta(t)
            hue = (th / (2 * np.pi) * 2 + (x - C) / 70) % 5
            i0 = np.floor(hue).astype(int)
            col = lerp(stripe_col[i0], stripe_col[(i0 + 1) % 5], (hue - i0)[:, None])
            wdt = 40 + 190 * env
            fr += col * (0.8 * env * np.exp(-((x - C) / wdt) ** 2))[:, None] ** 2.2
        if T_POSE <= t < T_POSE + 1.0:                         # the pose: a ring of light bursts out across the house
            a = t - T_POSE
            ring = np.exp(-((np.abs(x - C) - 900 * a) / 40) ** 2) * np.exp(-a / 0.4)
            fr += light(GLINT, 0.9 * ring)
            fr += spray(pose, T_POSE, t, GLINT, 0.9)

        # the near misses: a white snap where they nearly collide
        for tn, who, _ in NEAR:
            if tn - 0.05 <= t < tn + 0.6:
                p = np.interp(tn, np.arange(F) * DT, pos[who])
                a = max(0.0, t - tn)
                fr += light(GLINT, 1.0 * np.exp(-a / 0.15) * np.exp(-((x - p) / 14) ** 2))

        # scrapes: a puff of white off the ice on every turn
        for ts, k, ps in scrapes:
            a = t - ts
            if 0 <= a < 0.6:
                fr += light(GLINT, 0.55 * np.exp(-a / 0.18) * np.exp(-((x - ps) / 9) ** 2))

        # the skaters: a bright core, the scarf colour round it, and the scarf trailing behind (the last 0.3 s)
        for k in range(5):
            if vis[k, f] <= 0 or np.isnan(pos[k, f]):
                continue
            w = width[k, f]
            wob = 1.0
            if k == GOLD and T_WOBBLE <= t < T_FALL:
                wob = 1 + 0.35 * np.sin(2 * np.pi * 9 * t)
            trail = np.zeros(G.N)
            for j in range(1, 19):
                if f - j < 0 or np.isnan(pos[k, f - j]):
                    break
                trail = np.maximum(trail, np.exp(-j / 6.5) * np.exp(-((x - pos[k, f - j]) / (8 * w)) ** 2))
            body = np.exp(-((x - pos[k, f]) / (5 * w)) ** 2)
            halo = np.exp(-((x - pos[k, f]) / (13 * w)) ** 2)
            fr += light(SCARF[k], vis[k, f] * wob * np.maximum(1.0 * halo, 0.9 * trail))
            fr += light(CORE, 0.75 * vis[k, f] * body)
            if JOIN[k] <= t < JOIN[k] + 0.4:                   # taking a hand
                a = t - JOIN[k]
                fr += light(GLINT, 0.8 * np.exp(-a / 0.12) * body)

        # the tumble: the pond flashes and ice sprays both ways
        if T_FALL <= t < T_FALL + 2.0:
            a = t - T_FALL
            fr[pond] += light(GLINT, 0.7 * np.exp(-a / 0.12) * np.ones(pond.sum()))
            fr += spray(fall, T_FALL, t, GLINT, 1.0) + spray(fall, T_FALL, t, ICE, 0.5)

        # the crack: red flares where she digs in; the show-off flies off the end and lands in the snow
        if T_CRACK <= t < T_CRACK + 0.8:
            a = t - T_CRACK
            fr += light(GLINT, 1.0 * np.exp(-a / 0.12) * np.exp(-((x - STOP_AT) / (12 + 200 * a)) ** 2))
        if T_PLOP <= t < T_PLOP + 1.6:
            a = t - T_PLOP
            fr += light(GLINT, 0.9 * np.exp(-a / 0.3) * np.exp(-((x - END) / (20 + 60 * a)) ** 2))
            fr += spray(plop, T_PLOP, t, GLINT, 0.9)

        # finale: the scarf colours run back from the end of Right across the whole house and stay, drifting
        if t >= T_WAVE:
            front = END - 1400 * (t - T_WAVE)
            behind = smoothstep(front - 10, front + 60, x) * bank
            band = ((x + 20 * (t - T_WAVE)) / 38) % 5
            i0 = np.floor(band).astype(int)
            col = lerp(stripe_col[i0], stripe_col[(i0 + 1) % 5], smoothstep(0.75, 1.0, band - i0)[:, None])
            head = np.exp(-((x - front) / 30) ** 2) * (front > -60)
            sparkle = 0.75 + 0.25 * np.clip(snow_tw(3 * t), -1, 1)
            fr += col * (0.5 * behind * sparkle)[:, None] ** 2.2 + light(GLINT, 0.9 * head)
            fb = np.exp(-max(0.0, t - T_FINAL) / 0.4) * (t >= T_FINAL)
            fr += light(CORE, 0.85 * fb * np.ones(G.N))

        out[f][G.path] = np.clip(fr, 0, 1) * master ** 2.2
    return out


# ---- music: an original waltz in G, a bar a second ----
CHORDS = {
    'G': ('G2', 'D3', ('B3', 'D4', 'G4')), 'C': ('C3', 'G2', ('C4', 'E4', 'G4')),
    'D7': ('D2', 'A2', ('C4', 'F#4', 'A4')), 'Em': ('E2', 'B2', ('B3', 'E4', 'G4')),
    'Am': ('A2', 'E2', ('A3', 'C4', 'E4')), 'F': ('F2', 'C3', ('A3', 'C4', 'F4')),
    'Dm': ('D2', 'A2', ('A3', 'D4', 'F4')), 'G7': ('G2', 'D3', ('B3', 'F4', 'G4')),
    'E7': ('E2', 'B2', ('B3', 'D4', 'G#4')), 'A7': ('A2', 'E2', ('C#4', 'E4', 'G4')),
}
TUNE_A1 = [[(0, 'D5', 3)], [(0, 'B4', 1), (1, 'C5', 1), (2, 'D5', 1)], [(0, 'G5', 2), (2, 'F#5', 1)], [(0, 'E5', 3)],
           [(0, 'E5', 2), (2, 'C5', 1)], [(0, 'A4', 1), (1, 'B4', 1), (2, 'C5', 1)], [(0, 'F#5', 2), (2, 'E5', 1)],
           [(0, 'D5', 3)]]
HARM_A1 = ['G', 'G', 'Em', 'C', 'Am', 'D7', 'D7', 'G']
TUNE_A2 = [[(0, 'D5', 3)], [(0, 'B4', 1), (1, 'C5', 1), (2, 'D5', 1)], [(0, 'B5', 2), (2, 'A5', 1)],
           [(0, 'G5', 2), (2, 'E5', 1)], [(0, 'D5', 2), (2, 'B4', 1)], [(0, 'C5', 1), (1, 'A4', 1), (2, 'F#4', 1)],
           [(0, 'A4', 2), (2, 'F#4', 1)], [(0, 'G4', 3)]]
HARM_A2 = ['G', 'G', 'Em', 'C', 'G', 'D7', 'D7', 'G']
TUNE_B = [[(0, 'E5', 3)], [(0, 'D5', 1), (1, 'E5', 1), (2, 'G5', 1)], [(0, 'A5', 2), (2, 'G5', 1)], [(0, 'F5', 3)],
          [(0, 'D5', 3)], [(0, 'C5', 1), (1, 'D5', 1), (2, 'F5', 1)], [(0, 'G5', 2), (2, 'F5', 1)],
          [(0, 'E5', 1), (1, 'D5', 1), (2, 'B4', 1)], [(0, 'C5', 1), (1, 'E5', 1), (2, 'G5', 1)],
          [(0, 'A5', 2), (2, 'G5', 1)], [(0, 'F#5', 1), (1, 'E5', 1), (2, 'D5', 1)]]
HARM_B = ['C', 'C', 'Am', 'F', 'Dm', 'Dm', 'G7', 'G7', 'C', 'F', 'D7']
LAMP_NOTES = ('G5', 'D5', 'B5', 'G4', 'D6', 'B4', 'G5', 'D5', 'A5', 'F#5', 'G5')
JOIN_NOTES = ('G4', 'B4', 'D5', 'G5', 'B5')


def score(M, G):
    from pixelhome.audio import SR, note, slide, whoosh
    n = note
    pos, vis, width, scrapes, crossings = plan()
    F = pos.shape[1]
    tt = np.arange(F) * DT

    flute = M.sampler('Woodwinds/Flute/susvib/*.wav', tune=-12)
    flute_st = M.sampler('Woodwinds/Flute/stac/*.wav', tune=-12)
    clar = M.sampler('Woodwinds/Clarinet/susLong/*.wav', tune=-12)
    clar_st = M.sampler('Woodwinds/Clarinet/stac/*.wav', tune=-12)
    bsn = M.sampler('Woodwinds/Bassoon/stac/*.wav', tune=-12)
    vln = M.sampler('Strings/Violin Section/susVib/*.wav', tune=-12)
    vla = M.sampler('Strings/Viola Section/susvib/*.wav', tune=-12)
    vc = M.sampler('Strings/Cello Section/susvib/*.wav', tune=-12)
    trem = M.sampler('Strings/Violin Section/Trem/*.wav', tune=-12)
    vln_p = M.sampler('Strings/Violin Section/Pizz/*.wav', tune=-12)
    vla_p = M.sampler('Strings/Viola Section/pizz/*.wav', tune=-12)
    cb = M.sampler('Strings/Solo Contrabass/Pizz/*.wav', tune=-12)
    harp = M.sampler('Strings/Harp/*.wav')
    glock = M.sampler('Percussion/Glock/*.wav', tune=-12)
    xylo = M.sampler('Percussion/Xylo/*.wav', tune=-12)
    tpt = M.sampler('Brass/Trumpet/sus/*.wav', tune=-12)
    tpt_st = M.sampler('Brass/Trumpet/stac/*.wav', tune=-12)
    horn = M.sampler('Brass/F Horn/sus/*.wav', tune=-12)
    horn_st = M.sampler('Brass/F Horn/stac/*.wav', tune=-12)
    bone = M.sampler('Brass/Tenor Trombone/sus/*.wav', tune=-12)
    tuba = M.sampler('Brass/Tuba/stac/*.wav', tune=-12)
    box = M.synth('Plucks/Magic Music Box')
    bells = M.hits('Percussion/Sleighbells_Hit*.wav')
    shake = M.hits('VSCO 1 Percussion/varMetal/various/sleighbell[12]_shake1.wav')
    tri = M.hits('Percussion/Triangle3-Hit_v1*.wav')
    crash = M.hits('Percussion/cymbal-crash1_ff*.wav')
    crash_s = M.hits('Percussion/cymbal-crash1_mp*.wav')
    choke = M.hits('Percussion/cymbal-crashshort*.wav')
    timp = M.hits('Percussion/Timpani/Timpani1_Hit_v[13]*.wav')
    troll = M.hits('Percussion/Timpani/Rolls/Timpani1_Roll_v3*.wav')
    sroll = M.hits('Percussion/Snare2-rollSN_v[35]*.wav')
    bd = M.hits('VSCO 1 Percussion/drums/bass/bdrum_f_*.wav')
    whip = M.hits('VSCO 1 Percussion/varWood/slapstick[123].wav')
    block = M.hits('VSCO 1 Percussion/varWood/wood_click_f*.wav')
    chimes = M.hits('VSCO 1 Percussion/varMetal/various/windchimes_asc1.wav')
    chimes_d = M.hits('VSCO 1 Percussion/varMetal/various/windchimes_fastAsc1.wav')
    tamb = M.hits('Percussion/Tamb1-Hit*.wav')

    for name, gain, rev in (('tune', 0.34, 0.18), ('counter', 0.26, 0.22), ('bass', 0.36, 0.08),
                            ('chords', 0.26, 0.16), ('pad', 0.24, 0.3), ('perc', 0.34, 0.14), ('fx', 0.3, 0.18),
                            ('sparkle', 0.24, 0.3)):
        M.bus(name, gain=gain, reverb=rev)

    order = np.argsort(G.pd)
    xs, ds = G.pos[order, 0], G.pd[order]
    x0, x1 = xs.min(), xs.max()

    def pan_at(dd):                          # path distance -> left/right across the facade, as seen from the street
        x = np.interp(np.clip(dd, 0, G.length), ds, xs)
        return float(0.85 * (2 * (x - x0) / (x1 - x0) - 1))

    def mono(sig, pans):
        a = (np.clip(pans, -1, 1) + 1) * np.pi / 4
        return np.vstack([sig * np.cos(a), sig * np.sin(a)]) * np.sqrt(2)

    def where(k, t):
        return float(np.interp(t, tt, np.nan_to_num(pos[k], nan=END + 50)))

    def line(bars, k0, sus, st=None, bus='tune', vel=96, pan=0.0, gain=1.0, octave=0):
        for j, bar in enumerate(bars):
            for b, m, ln in bar:
                inst = st if (st is not None and ln < 1) else sus
                M.add(bus, inst.play(n(m) + octave, vel, dur=ln * BEAT * 0.94, release=0.18), bt(k0 + j, b), gain, pan)

    def waltz(k0, harm, vel=88, gain=1.0, horns=False):
        """Oom-pah-pah: the bass on one, the chord on two and three."""
        for j, c in enumerate(harm):
            root, fifth, ch = CHORDS[c]
            bn = root if j % 2 == 0 or (j > 0 and harm[j - 1] != c) else fifth
            M.add('bass', cb.play(n(bn), vel + 10), bt(k0 + j), 0.9 * gain)
            for b in (1, 2):
                for m in ch:
                    M.add('chords', vln_p.play(n(m), vel - 12), bt(k0 + j, b), 0.32 * gain, 0.15)
                    if horns:
                        M.add('chords', horn_st.play(n(m) - 12, vel - 6, dur=0.2), bt(k0 + j, b), 0.3 * gain, -0.2)
            if horns:
                M.add('bass', tuba.play(n(bn), vel), bt(k0 + j), 0.6 * gain)

    def held(k0, harm, inst, vel=60, gain=1.0, bus='pad', pan=0.0):
        for j, c in enumerate(harm):
            for m in CHORDS[c][2]:
                M.add(bus, inst.play(n(m), vel, dur=BAR * 0.98, release=0.3), bt(k0 + j), 0.35 * gain, pan)

    scrape_snd = [whoosh(0.32, 2400, 5200, 0.6, seed=s) for s in range(4)]

    # ---- bars 0-3: the lamps come on, one a beat from the porch out; the pond shimmers up ----
    lamps = np.array(LAMPS, float)
    for i, li in enumerate(np.argsort(np.abs(lamps - C))):
        M.add('sparkle', glock.play(n(LAMP_NOTES[i]), 84), LAMP_T[i], 0.7, pan_at(lamps[li]))
    for k, m in enumerate(('G2', 'D3', 'G3', 'B3', 'D4', 'G4', 'B4', 'D5')):
        M.add('counter', harp.play(n(m), 70 + 3 * k), 0.15 + 0.1 * k, 0.6, -0.3 + 0.08 * k)
    for m in ('G3', 'D4', 'B4'):
        a = trem.play(n(m), 55, dur=3.2, release=0.5)
        M.add('pad', a * np.linspace(0.2, 1, a.shape[1])[None], 0.3, 0.5)
    M.add('sparkle', chimes.play(70), 0.2, 0.4, 0.0)
    waltz(2, ['G', 'D7'], vel=70)

    # ---- bars 4-19: the skaters come out of the porch sides and carve figure-eights ----
    for k in (RED, GREEN, MAGENTA, VIOLET):
        p = pan_at(PL_FRONT if k in (RED, MAGENTA) else PR_FRONT)
        s = whoosh(2.6, 600, 2400, 0.5, seed=10 + k)
        M.add('fx', mono(s[0], np.linspace(p, pan_at(where(k, ENTER[k] + 2.6)), s.shape[1])), ENTER[k], 0.55)
        M.add('sparkle', shake.play(70, dur=0.8), ENTER[k], 0.35, p)
        M.add('counter', harp.play(n(('D5', 'G5', 'B4', 'D5')[k]), 80), ENTER[k], 0.6, p)
    line(TUNE_A1, 4, flute, flute_st, vel=88)
    line(TUNE_A2, 12, flute, flute_st, vel=92)
    line(TUNE_A2, 12, clar, clar_st, 'counter', vel=72, gain=0.5, octave=-12, pan=-0.2)
    waltz(4, HARM_A1 + HARM_A2, vel=86)
    held(8, HARM_A1[4:] + HARM_A2, vla, vel=56, pan=0.2)
    for j in (7, 11, 15, 19):
        M.add('perc', tri.play(70), bt(j + 1), 0.45, 0.3)

    # scrapes on the ice: every turn a short hiss of the blades, where it happens
    for i, (ts, k, ps) in enumerate(scrapes):
        M.add('fx', scrape_snd[i % 4], ts - 0.12, 0.35 if k != GOLD else 0.5, pan_at(ps))

    # ---- bars 20-31: the pair spin, in C; a harp note every time they pass each other ----
    line(TUNE_B, 20, vln, None, vel=84, gain=0.9, pan=-0.1)
    line(TUNE_B, 20, clar, None, 'counter', vel=70, gain=0.45, octave=-12, pan=0.2)
    held(20, HARM_B, vla, vel=62, gain=1.2, pan=0.15)
    for j, c in enumerate(HARM_B):
        root, fifth, _ = CHORDS[c]
        M.add('bass', vc.play(n(root) + 12, 70, dur=BAR * 0.95, release=0.3), bt(20 + j), 0.5)
        M.add('bass', cb.play(n(root), 90), bt(20 + j), 0.7)
    for i, tc in enumerate(crossings):
        j = min(int((tc - T_SPIN) / BAR), len(HARM_B) - 1)
        ch = CHORDS[HARM_B[j]][2]
        m = n(ch[i % 3]) + 12 * (1 + (i // 3) % 2)
        M.add('sparkle', harp.play(m, 74), tc, 0.55, 0.2 * np.sin(i))
        if tc > T_POSE - 4:
            M.add('sparkle', glock.play(m, 60), tc, 0.3, 0.2 * np.cos(i))
    r = sroll.play(80, dur=2.0)
    M.add('perc', r * np.linspace(0, 1, r.shape[1])[None] ** 2, T_POSE - 2.0, 0.3)
    sw = whoosh(2.5, 400, 3000, 0.7, seed=31)
    M.add('fx', sw, T_POSE - 2.5, 0.35, pan_at(C))
    # the pose: the whole band on a G chord, a crash, a ring of light
    for m in ('G3', 'B3', 'D4', 'G4'):
        M.add('chords', horn.play(n(m), 100, dur=0.8, release=0.5), T_POSE, 0.4)
        M.add('chords', vln.play(n(m) + 12, 96, dur=0.8, release=0.5), T_POSE, 0.3)
    M.add('tune', tpt.play(n('D5'), 100, dur=0.8, release=0.5), T_POSE, 0.6)
    M.add('bass', cb.play(n('G2'), 120), T_POSE, 1.0)
    M.add('perc', crash.play(110), T_POSE, 0.55)
    M.add('perc', timp.play(110), T_POSE, 0.7)
    M.add('sparkle', chimes_d.play(90), T_POSE + 0.05, 0.45, pan_at(C))

    # ---- bars 32-48: the show-off. In from the end of Right on a whoosh, then the tune on a cocky trumpet ----
    s = whoosh(3.0, 300, 3200, 0.9, seed=32)
    M.add('fx', mono(s[0], np.array([pan_at(where(GOLD, T_SHOW + q / SR)) for q in range(0, s.shape[1], 480)])
                     .repeat(480)[:s.shape[1]]), T_SHOW, 0.6)
    for k, m in enumerate(('G3', 'A3', 'B3', 'C4', 'D4', 'E4', 'F#4', 'G4', 'A4', 'B4', 'C5', 'D5')):
        M.add('counter', xylo.play(n(m), 80 + 2 * k, dur=0.2), T_SHOW + 0.22 * k, 0.6, pan_at(where(GOLD, T_SHOW + 0.22 * k)))
    M.add('tune', tpt.play(n('D5'), 100, dur=0.6, release=0.2), bt(34, 2), 0.6)
    show = [list(b) for b in TUNE_A1] + [list(b) for b in TUNE_A2[:6]]
    line(show, 35, tpt, tpt_st, vel=100, pan=0.1)
    line(show, 35, xylo, None, 'counter', vel=72, gain=0.45, pan=-0.15)
    waltz(32, ['G', 'G', 'D7'] + HARM_A1 + HARM_A2[:6], vel=92)
    for j in range(32, 47):
        M.add('perc', tamb.play(70), bt(j, 1), 0.25, 0.3)
        M.add('perc', tamb.play(62), bt(j, 2), 0.2, 0.3)
    # every lap end a skid: woodblock and the hiss (from the scrapes); a step up the xylophone, faster each lap
    laps = [lt for lt, _ in SHOW_LAPS[1:-1]]
    for i, lt in enumerate(laps):
        M.add('perc', block.play(90), lt, 0.5, pan_at(where(GOLD, lt)))
    # the near misses: a choked cymbal, a horn stab, a slide whistle up for the one who leaps aside
    for tn, who, by in NEAR:
        p = pan_at(where(who, tn))
        M.add('perc', choke.play(115), tn, 0.6, p)
        for m in ('C#4', 'E4', 'G4', 'Bb4'):
            M.add('chords', horn_st.play(n(m) - 12, 112, dur=0.3), tn, 0.45, p * 0.6)
        M.add('fx', slide(0.0, 0.22, 700, 1700, 0.3, 0.45), tn, 0.7, p)
        M.add('counter', clar_st.play(n('E5'), 90), tn + 0.25, 0.4, p)
    # the wobble: the tune falls apart over a dominant; a trombone and a slide whistle wobble with him
    held(46, ['D7', 'D7', 'D7'], trem, vel=70, gain=1.0, pan=0.0)
    tw_ = np.arange(int((T_FALL - T_WOBBLE) * SR)) / SR
    wob = 900 * 2 ** (0.25 * np.sin(2 * np.pi * 3.2 * tw_) * (tw_ / tw_[-1]))
    ph = 2 * np.pi * np.cumsum(wob) / SR
    sig = 0.3 * np.sin(ph) * np.clip(tw_ / 0.1, 0, 1)
    M.add('fx', mono(sig, np.array([pan_at(where(GOLD, T_WOBBLE + q)) for q in tw_[::480]]).repeat(480)[:len(sig)]),
          T_WOBBLE, 0.5)
    for k, (m, d) in enumerate((('A3', 0.6), ('G#3', 0.6), ('A3', 0.5), ('F#3', 0.7))):
        M.add('counter', bone.play(n(m), 90, dur=d, release=0.15), T_WOBBLE + 0.7 * k, 0.5, pan_at(where(GOLD, T_WOBBLE + 0.7 * k)))
    r = troll.play(90, dur=1.2)
    M.add('perc', r * np.linspace(0.1, 1, r.shape[1])[None] ** 2, T_FALL - 1.2, 0.5)

    # ---- bar 49: the tumble. A crash, a thud, a shower of ice; then a hush ----
    pf = pan_at(FALL_AT)
    M.add('perc', crash.play(120), T_FALL, 0.6, pf)
    M.add('perc', bd.play(120), T_FALL, 0.9, pf)
    M.add('perc', timp.play(120), T_FALL, 0.7, pf)
    M.add('fx', slide(0.0, 0.5, 1500, 250, 0.55, 0.45), T_FALL - 0.2, 0.7, pf)
    M.add('sparkle', chimes_d.play(100), T_FALL + 0.05, 0.6, pf - 0.25)
    M.add('sparkle', chimes.play(90), T_FALL + 0.1, 0.5, pf + 0.25)
    rr = np.random.default_rng(SEED + 5)
    for k in range(18):                              # ice chips: high glass notes scattered both ways
        m = n(('G5', 'B5', 'D6', 'F#6', 'A5', 'E6')[k % 6])
        M.add('sparkle', glock.play(m, int(rr.integers(50, 80))), T_FALL + 0.05 + 0.07 * k, 0.4,
              float(np.clip(pf + rr.uniform(-0.6, 0.6), -1, 1)))
    M.add('bass', tuba.play(n('G1'), 110), T_FALL, 0.7)
    # the hush: the music box picks out the opening alone, slower; he gets up with a bassoon and a harp
    hush = [(T_FALL + 1.6, 'D5', 1.0), (T_FALL + 2.6, 'B4', 0.4), (T_FALL + 3.0, 'C5', 0.4), (T_FALL + 3.4, 'D5', 1.0)]
    mb = box.render([(t - T_FALL, n(m), 70, d) for t, m, d in hush], 5.0)
    M.add('sparkle', mb, T_FALL, 1.2, pan_at(C))
    for k, m in enumerate(('G2', 'D3', 'G3')):
        M.add('counter', bsn.play(n(m), 90), T_UP + 0.15 * k, 0.6, pan_at(LIE_AT))
    for k, m in enumerate(('G3', 'B3', 'D4', 'G4', 'B4', 'D5', 'G5')):
        M.add('counter', harp.play(n(m), 76), T_UP + 0.45 + 0.06 * k, 0.5, pan_at(LIE_AT))
    M.add('perc', tri.play(70), T_UP + 0.5, 0.4, pan_at(LIE_AT))

    # ---- bars 55-58: hands joined one by one, a rising note for each; a roll into the chain ----
    for k, tj in enumerate(JOIN):
        p = pan_at(SLOT[k])
        M.add('sparkle', glock.play(n(JOIN_NOTES[k]), 90), tj, 0.6, p)
        M.add('chords', vln_p.play(n(JOIN_NOTES[k]) - 12, 100), tj, 0.6, p)
        M.add('bass', cb.play(n(('G2', 'B2', 'D2', 'G2', 'D2')[k]), 100), tj, 0.7)
    held(55, ['G', 'C', 'D7', 'D7'], horn, vel=60)
    r = sroll.play(90, dur=1.0)
    M.add('perc', r * np.linspace(0.05, 1, r.shape[1])[None] ** 2, T_GO - 1.0, 0.35)

    # ---- bars 59-74: the chain, the whole band. Strings and flute out to the U-turn, brass back across ----
    line(TUNE_A1, 59, flute, flute_st, vel=96)
    line(TUNE_A1, 59, vln, None, 'counter', vel=84, gain=0.6, octave=-12, pan=-0.2)
    waltz(59, HARM_A1, vel=94)
    chase = [list(b) for b in TUNE_A2[:6]] + [[(0, 'A4', 1), (1, 'C5', 1), (2, 'F#5', 1)], [(0, 'A5', 3)]]
    line(chase, 67, tpt, tpt_st, vel=106, pan=0.1)
    line(chase, 67, horn, horn_st, 'counter', vel=96, gain=0.55, octave=-12, pan=-0.15)
    line(chase, 67, flute, flute_st, 'counter', vel=86, gain=0.35, pan=0.25)
    waltz(67, HARM_A2[:6] + ['D7', 'D7'], vel=100, horns=True)
    for j in range(59, 75):                          # sleigh bells on every beat, panned with the leader
        for b in range(3):
            tb = bt(j, b)
            M.add('perc', bells.play(100 if b == 0 else 76), tb, 0.4, pan_at(lead(tb)))
    for j in range(63, 75):                          # clarinets running in triplets as it speeds up
        ch = CHORDS[(HARM_A1 + HARM_A2[:6] + ['D7', 'D7'])[j - 59]][2]
        for b in range(3):
            M.add('counter', clar_st.play(n(ch[b]) + 12, 76), bt(j, b + 0.5), 0.3, -0.35)
    # the U-turn at the back of the Side: a crash and a whoop of horns
    pt = pan_at(TURN_AT)
    M.add('perc', crash_s.play(100), T_TURN, 0.5, pt)
    M.add('fx', slide(0.0, 0.5, 500, 1300, 0.6, 0.4), T_TURN - 0.3, 0.5, pt)
    s = whoosh(4.0, 300, 3000, 0.9, seed=67)
    M.add('fx', mono(s[0], np.array([pan_at(lead(T_CRACK - 4 + q / SR)) for q in range(0, s.shape[1], 480)])
                     .repeat(480)[:s.shape[1]]), T_CRACK - 4, 0.45)
    r = sroll.play(100, dur=2.0)
    M.add('perc', r * np.linspace(0.05, 1, r.shape[1])[None] ** 2, T_CRACK - 2.0, 0.45)
    r = troll.play(100, dur=2.0)
    M.add('perc', r * np.linspace(0.05, 1, r.shape[1])[None] ** 2, T_CRACK - 2.0, 0.55)
    for m in ('D3', 'F#3', 'A3', 'C4'):
        a = trem.play(n(m) + 12, 76, dur=2.0, release=0.05)
        M.add('pad', a * np.linspace(0.3, 1, a.shape[1])[None], T_CRACK - 2.0, 0.5)

    # ---- bar 75: the crack. A slapstick, the band on G, and the show-off flies off the end ----
    pc = pan_at(STOP_AT)
    M.add('perc', whip.play(127), T_CRACK, 1.0, pc)
    M.add('perc', crash.play(120), T_CRACK, 0.55, pc)
    M.add('perc', timp.play(120), T_CRACK, 0.8, pc)
    for m in ('G3', 'B3', 'D4', 'G4'):
        M.add('chords', horn.play(n(m), 110, dur=0.5, release=0.3), T_CRACK, 0.45)
        M.add('chords', vln_p.play(n(m) + 12, 120), T_CRACK, 0.5)
    M.add('bass', cb.play(n('G2'), 127), T_CRACK, 1.0)
    M.add('bass', tuba.play(n('G1'), 120), T_CRACK, 0.7)
    up = slide(0.0, T_PLOP - T_CRACK, 500, 2000, T_PLOP - T_CRACK + 0.05, 0.5)
    M.add('fx', mono(up[0], np.linspace(pc, 0.95, up.shape[1])), T_CRACK, 0.75)
    M.add('perc', bd.play(110), T_PLOP, 0.8, 0.95)            # into the snowbank
    M.add('perc', shake.play(100), T_PLOP, 0.5, 0.95)
    M.add('sparkle', chimes_d.play(90), T_PLOP + 0.05, 0.4, 0.9)

    # ---- bars 76-85: the colours run home and the band takes the cadence; he skates back in ----
    gl = [n(m) for m in ('D6', 'B5', 'G5', 'D5', 'B4', 'G4', 'D4', 'B3', 'G3')]
    for i, m in enumerate(gl):                       # the wave runs from Right to the back of the Side
        tw = T_WAVE + i * (END / 1400) / len(gl)
        M.add('sparkle', glock.play(m, 90), tw, 0.5, pan_at(END - 1400 * (tw - T_WAVE)))
        M.add('counter', harp.play(m - 12, 85), tw, 0.5, pan_at(END - 1400 * (tw - T_WAVE)))
    fin = [[(0, 'D5', 2), (2, 'B4', 1)], [(0, 'G5', 2), (2, 'E5', 1)], [(0, 'D5', 2), (2, 'B4', 1)],
           [(0, 'C5', 1), (1, 'A4', 1), (2, 'F#4', 1)], [(0, 'A4', 1), (1, 'C5', 1), (2, 'F#5', 1)],
           [(0, 'E5', 2), (2, 'F#5', 1)]]
    line(fin, 76, tpt, tpt_st, vel=104, pan=0.1)
    line(fin, 76, flute, flute_st, 'counter', vel=90, gain=0.5, pan=-0.2)
    line(fin, 76, vln, None, 'counter', vel=86, gain=0.5, octave=-12, pan=0.2)
    harm_f = ['G', 'C', 'G', 'D7', 'D7', 'D7']
    waltz(76, harm_f, vel=100, horns=True)
    held(76, harm_f, vla, vel=70, gain=1.0)
    for j in range(76, 82):
        for b in range(3):
            M.add('perc', bells.play(100 if b == 0 else 76, ), bt(j, b), 0.35, 0.3 if b else -0.3)
    s = whoosh(2.0, 2400, 600, 0.6, seed=79)
    M.add('fx', mono(s[0], np.linspace(0.95, pan_at(GOLD_BACK), s.shape[1])), T_BACK[0] + 0.2, 0.5)
    for k, m in enumerate(('D4', 'G4', 'B4', 'D5')):            # "I'm fine!": a whoop of horns as he skates back
        M.add('chords', horn_st.play(n(m) - 12, 100, dur=0.25), T_BACK[1] - 0.6 + 0.12 * k, 0.4, pan_at(GOLD_BACK))
    r = troll.play(100, dur=1.0)
    M.add('perc', r * np.linspace(0.05, 1, r.shape[1])[None] ** 2, T_FINAL - 1.0, 0.6)
    # bar 82: the last chord, held to the end
    for m in ('G3', 'B3', 'D4', 'G4'):
        M.add('chords', horn.play(n(m), 110, dur=2.6, release=1.0), T_FINAL, 0.45, -0.1)
        M.add('pad', vln.play(n(m) + 12, 100, dur=2.6, release=1.0), T_FINAL, 0.4, 0.1)
    M.add('tune', tpt.play(n('G5'), 104, dur=2.4, release=1.0), T_FINAL, 0.7)
    M.add('tune', flute.play(n('G5'), 90, dur=2.6, release=1.0), T_FINAL, 0.4)
    M.add('bass', cb.play(n('G2'), 127), T_FINAL, 1.0)
    M.add('bass', tuba.play(n('G1'), 120), T_FINAL, 0.8)
    M.add('perc', crash.play(120), T_FINAL, 0.6)
    M.add('perc', timp.play(120), T_FINAL, 0.8)
    M.add('perc', shake.play(110), T_FINAL, 0.5)
    for k, m in enumerate(('G4', 'B4', 'D5', 'G5', 'B5', 'D6')):
        M.add('sparkle', glock.play(n(m), 84), T_FINAL + 0.1 * k, 0.5, -0.5 + 0.2 * k)
        M.add('counter', harp.play(n(m) - 12, 84), T_FINAL + 0.06 * k, 0.5, -0.4 + 0.16 * k)
