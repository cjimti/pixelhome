"""The Big Game: Football on the roofline at 120 BPM, with the porch as the sky. Pom-poms burst on the
wings, then the home team (amber) stampedes in from the free end of Right and the visitors (cranberry)
pour out of the porch, and the two lines face off on the Left wing, breathing on the beat. Hut, hut:
they crash and shove. Play one: the pass climbs the Porch Left, hangs over the Porch Front with the sky
lighting under it, and drops down the Porch Right just over the diving receiver's fingers and out the
free end. Awww: the house sags three times. The crowd chants. Play two: the runner jukes up the porch
side past lunging tacklers into a pile-up at the corner; the ball squirts out and bounces back and forth
along the Porch Front with both teams diving after it, and the home team falls on it. Two-minute
warning: the Porch Front becomes the game clock. Play three: snap, and the clock ticks a segment a beat
while the quarterback scrambles all the way back up the Side, spinning out of two sacks. At zero he
throws the Hail Mary the length of the house; it hangs at the top of the sky in a beat of stillness,
drops, is tipped, and is caught in the end zone. Touchdown: fireworks fly back along the whole roof,
two stadium waves go round the house, confetti cannons fire, and the band plays the fight song out."""
import numpy as np
from pixelhome.fx import DT, hexc, light, perc, keys, smoothstep, Flicker, nframes

CODE = 'TG05'
TITLE = 'The Big Game'
KIND = 'show'
DESCRIPTION = ('Football on the roof, with the porch as the sky: passes arc up and over the porch, a fumble bounces '
               'along it, and a Hail Mary from the back of the house ends in a touchdown and a stadium wave.')
VOICEOVER = "Dinner can wait. It's fourth quarter and the game is on the line."

HOME = hexc('#ff8a18')         # amber jerseys
AWAY = hexc('#c0102a')         # cranberry jerseys
BALL = hexc('#ff9030')
WARM = hexc('#ffc27a')
WHITE = hexc('#fff0d8')
GOLD = hexc('#ffb000')
BROWN = hexc('#5a1c04')
PUMPKIN = hexc('#ff5200')
CONF = np.array([HOME, AWAY, GOLD, WARM, PUMPKIN])
D = 90.0
SEED = 25
BEAT = 0.5                     # 120 BPM
BAR = 4 * BEAT


def at(bar, beat=0.0):
    return bar * BAR + beat * BEAT


# the plays: set (lines form and breathe), hut hut on beats 3 and 4, snap; s is the line of scrimmage
PLAYS = [dict(set=at(4), snap=at(5), s=700.0, end=at(8)),
         dict(set=at(11), snap=at(12), s=820.0, end=at(14)),
         dict(set=at(21), snap=at(22), s=900.0, end=at(25))]
POMS = [at(0, k) for k in range(8)]                          # pom-poms on the beat, Left and Right in turn
T_FIELD = at(2)                                              # the teams take the field
QB1 = [(at(4), 660), (at(5), 660), (at(5.3), 600), (at(5.5), 600), (at(6), 620), (at(8), 620)]
BALL1 = [(at(5.5), 600), (11.6, 892), (12.6, 1311), (13.4, 1660), (14.1, 2033), (14.6, 2300), (15.1, 2600)]
REC1 = [(at(4), 2150), (at(5), 2150), (13.8, 2400), (14.5, 2480), (15.0, 2470), (at(8.5), 2470)]
GROANS = (at(7.75), at(8.25), at(8.75))
CHANTS = (at(9), at(17), at(37))                             # "let's go!" (clap clap), two bars each
RUN2 = [(at(11), 780), (at(12), 780), (24.6, 870), (25.2, 1010), (25.5, 960), (26.1, 1130), (26.4, 1090),
        (27.0, 1240), (27.4, 1210), (at(14), 1300), (at(15), 1300)]
JUKES = (25.2, 26.1, 27.0)
T_PILE, T_FUMBLE, T_RECOVER = at(14), at(15), at(17)
HOPS = [(at(15), 1300), (30.5, 1430), (31.0, 1530), (31.5, 1470), (32.0, 1370), (32.5, 1440), (33.0, 1560),
        (33.5, 1630), (at(17), 1600)]
T_WARN = at(19)                                              # two-minute warning: the clock appears
TICKS = [at(22) + k * BEAT for k in range(20)]               # a clock segment out every beat from the snap
T_THROW = at(27)                                             # the clock hits zero: the Hail Mary
QB3 = [(at(21), 860), (at(22), 860), (44.8, 760), (45.6, 800), (46.6, 620), (47.2, 660), (48.2, 470), (49.0, 510),
       (50.2, 300), (51.0, 340), (52.0, 150), (52.6, 180), (53.4, 80), (at(27), 80), (at(28), 80)]
SPINS = (45.6, 47.2, 49.0, 51.0, 52.6)                      # where he spins out of a sack
BALL3 = [(at(27), 80), (55.2, 700), (56.2, 1000), (57.4, 1311), (58.0, 1430), (59.6, 1560), (60.2, 1660),
         (61.2, 2033), (61.8, 2300), (62.2, 2395), (62.7, 2365), (63.4, 2425), (at(32), 2445)]
T_HANG, T_DROP, T_TIP, TD = 58.0, 60.0, 62.2, at(32)
TD_HITS = (at(32, 1), at(32, 2), at(32, 3))
ROCKETS = [(TD + 0.25 * k, 2420, tgt) for k, tgt in enumerate((1800, 1250, 750, 250))]
WAVES = ((at(33), -1), (at(35), 1))                          # stadium waves: to the back of the Side, and back
WAVE_SPEED = 720.0
CANNONS = [at(37 + k) for k in range(4)]
FINALE = [at(41, k) for k in range(12)]
T_END = at(44)


def track(pts, F, sigma=0.1):
    """Per-frame path position from (time, pd) waypoints, linear then smoothed. NaN outside."""
    t = np.arange(F) * DT
    ts = np.array([p[0] for p in pts], float)
    xs = np.array([p[1] for p in pts], float)
    x = np.interp(t, ts, xs)
    k = max(1, int(sigma / DT * 3))
    w = np.exp(-0.5 * (np.arange(-k, k + 1) * DT / sigma) ** 2)
    w /= w.sum()
    x = np.convolve(np.concatenate([np.full(k, x[0]), x, np.full(k, x[-1])]), w, 'valid')
    x[(t < ts[0]) | (t > ts[-1])] = np.nan
    return x


def height(x):
    """How high the ball is: the porch sides climb, the Porch Front is the top of the sky."""
    return float(np.clip(np.interp(x, [892, 1311, 1660, 2033], [0, 1, 1, 0]), 0, 1))


def field_split(F, qb1, ball1, run2, ball2, qb3, ball3):
    """Where the ball is, frame by frame, for the field's colours: the carrier or the ball in the air, the line
    of scrimmage between plays, past the end zone after the touchdown."""
    t = np.arange(F) * DT
    x = np.full(F, np.nan)
    pts = [(PLAYS[0]['set'] - 1, 700), (BALL1[-1][0] + 0.3, None), (BALL1[-1][0] + 1.2, 700), (PLAYS[1]['snap'], 820),
           (T_RECOVER, None), (T_WARN, 1600), (PLAYS[2]['set'] - 0.5, 900), (PLAYS[2]['snap'], 900)]
    base = np.interp(t, [p[0] for p in pts if p[1] is not None], [p[1] for p in pts if p[1] is not None])
    x[t >= PLAYS[0]['set'] - 1] = base[t >= PLAYS[0]['set'] - 1]
    for tr, t0, t1 in ((qb1, PLAYS[0]['snap'], BALL1[0][0]), (ball1, BALL1[0][0], BALL1[-1][0]),
                       (run2, PLAYS[1]['snap'], T_FUMBLE), (ball2, T_FUMBLE, T_RECOVER), (qb3, PLAYS[2]['snap'], T_THROW),
                       (ball3, T_THROW, TD)):
        m = (t >= t0) & (t < t1) & ~np.isnan(tr)
        x[m] = tr[m]
    x[(t >= BALL1[-1][0]) & (t < BALL1[-1][0] + 1.2)] = np.nan
    x[(t >= T_RECOVER) & (t < T_WARN)] = 1600
    x[t >= TD] = 2600
    ok = ~np.isnan(x)                                              # ease the jumps between carriers
    k = 6
    w = np.exp(-0.5 * (np.arange(-k, k + 1) / 2.5) ** 2)
    w /= w.sum()
    xs = np.where(ok, x, 0)
    sm = np.convolve(np.pad(xs, k, mode='edge'), w, 'valid') / np.maximum(np.convolve(np.pad(ok * 1.0, k, mode='edge'), w, 'valid'), 1e-6)
    sm[~ok] = np.nan
    gap = (t >= BALL1[-1][0]) & (t < BALL1[-1][0] + 1.2)          # after the overthrow: back to the line
    sm[gap] = np.interp(t[gap], [BALL1[-1][0], BALL1[-1][0] + 1.2], [2600, 700])
    return sm


def bursts(rng, events, n=24, spread=(250, 900)):
    """Spark bursts [(time, where, colour index or -1 for mixed)] -> per-spark arrays."""
    T, P, V, C = [], [], [], []
    for t, p, c in events:
        T += [t] * n
        P += [p] * n
        V += list(rng.uniform(*spread, n) * rng.choice([-1, 1], n))
        C += list(rng.integers(0, len(CONF), n) if c < 0 else [c] * n)
    return np.array(T), np.array(P, float), np.array(V), np.array(C)


def render(G, seed=SEED):
    rng = np.random.default_rng(seed)
    F = nframes(D)
    out = np.zeros((F, G.N, 3))
    n = G.N
    d = G.pd[G.path]
    idx = np.arange(n)
    side, left, right = idx < 81, (idx >= 81) & (idx < 179), idx >= 381
    porch = (idx >= 179) & (idx < 381)
    pf0, pf1 = d[261], d[331]
    crowd = Flicker(rng, n, 1.0, 4.0)
    yard = 0.5 + 0.5 * np.cos(2 * np.pi * d / 100) ** 16
    excite = [(0, 0.3), (8, 0.25), (15, 0.5), (18, 0.25), (28, 0.6), (34, 0.9), (38, 0.25), (54, 0.6),
              (T_HANG, 0.05), (T_DROP, 0.4), (TD, 1.0), (75, 0.8), (88, 0.9), (90, 0.2)]
    ball1, ball3 = track(BALL1, F, 0.12), track(BALL3, F, 0.1)
    qb1, rec1, run2, qb3 = track(QB1, F), track(REC1, F), track(RUN2, F, 0.08), track(QB3, F, 0.08)
    ball2 = track([(T_FUMBLE - 0.01, 1300)] + HOPS, F, 0.06)
    split = field_split(F, qb1, ball1, run2, ball2, qb3, ball3)
    rock = bursts(rng, [(t + 1.2, tgt, -1) for t, _, tgt in ROCKETS], 30, (150, 700))
    cann = bursts(rng, [(t, p, -1) for t in CANNONS for p in (892, 2036)], 30, (200, 1100))
    fins = bursts(rng, [(t, float(rng.uniform(150, 2450)), int(rng.integers(0, 5))) for t in FINALE], 26, (150, 650))

    def dot(x, col, lvl=0.9, w=10.0):
        if np.isnan(x):
            return 0
        return light(col, lvl * np.exp(-((d - x) / w) ** 2))

    def ball(x, f, tr, t0, sky=True):
        if np.isnan(x):
            return 0
        b = light(WHITE, 0.95 * np.exp(-((d - x) / 7) ** 2)) + light(BALL, 0.7 * np.exp(-((d - x) / 16) ** 2))
        for k in range(1, 16):                                     # a comet trail
            xk = tr[max(0, f - k)]
            if (f - k) * DT >= t0 and not np.isnan(xk):
                b = b + light(BALL, 0.55 * (1 - k / 16) * np.exp(-((d - xk) / 9) ** 2))
        h = height(x) if sky else 0.0
        if h > 0:                                                  # the sky lights up under it
            b = b + light(GOLD, (0.15 + 0.35 * h) * porch * (0.4 + 0.6 * np.exp(-((d - x) / 260) ** 2)))
        return b

    def sparks(arr, t, life=1.4, w=6.0):
        T, P, V, C = arr
        a = t - T
        live = (a >= 0) & (a < life)
        if not live.any():
            return 0
        a = a[live]
        x = P[live] + V[live] * 0.6 * (1 - np.exp(-a / 0.6))
        lv = np.exp(-a / (life / 3)) * (0.6 + 0.4 * np.cos(2 * np.pi * 5 * a + T[live]) ** 2)
        I = lv[:, None] * np.exp(-((d[None] - x[:, None]) / w) ** 2)
        return (perc(np.clip(I, 0, 1))[..., None] * CONF[C[live].astype(int)][:, None, :]).sum(0)

    def lines(t, p, lvl, jog=True):
        """Both lines at the scrimmage: six dashes a side, jogging in from the porch, breathing on the beat,
        shoving after the snap."""
        s = p['s']
        away = 1 - smoothstep(p['set'] - 1.6, p['set'] - 0.1, t) if jog else 0.0
        beat = np.exp(-((t % BEAT) / 0.15))
        hut = 0.0
        for k in (2, 3):
            a = t - (p['set'] + k * BEAT)
            if 0 <= a < 0.4:
                hut = np.exp(-a / 0.12)
        u = t - p['snap']
        shove = 0.0 if u < 0 else 30 * np.sin(2 * np.pi * 1.1 * u) * np.exp(-u / 2.5)
        tight = 0.0 if u < 0 else 14 * smoothstep(0, 0.2, u)
        b = 0
        jit = rng.normal(0, 3 if u > 0 else 0.5, 12)
        for k in range(6):
            fl = 0.65 + 0.25 * beat + 0.3 * hut
            b = b + dot(s - 26 - 34 * k + shove + tight + jit[k] + away * (700 + 90 * k), HOME, lvl * fl, 11)
            b = b + dot(s + 26 + 34 * k + shove - tight + jit[6 + k] + away * (520 + 70 * k), AWAY, lvl * fl, 11)
        if u >= 0:                                                 # the crash: a white seam, sparks
            b = b + light(WHITE, lvl * (np.exp(-u / 0.12) + 0.25 * (0.5 + 0.5 * np.sin(30 * t)) * np.exp(-u / 1.5)) *
                          np.exp(-((d - s - shove) / 14) ** 2))
        return b

    def chant(t, t0, scale=1.0):
        """'Let's go!' (clap clap): Left on 1, Right on 2, the whole house on 3 and 4."""
        b = 0
        for bar in range(2):
            for k in range(4):
                a = t - (t0 + bar * BAR + k * BEAT)
                if 0 <= a < 0.45:
                    e = np.exp(-a / 0.14)
                    if k == 0:
                        b = b + light(HOME, scale * e * (left | side))
                    elif k == 1:
                        b = b + light(HOME, scale * e * right)
                    else:
                        b = b + light(GOLD, scale * 0.85 * e * np.ones(n))
        return b

    for f in range(F):
        t = f * DT
        ex = keys(t, excite)
        buf = light(BROWN, 0.22 * yard + 0.1)
        if not np.isnan(split[f]):                                 # the field: amber behind the ball, cranberry ahead
            x = split[f]
            own = np.clip((x - d) / 40 + 0.5, 0, 1)[:, None]
            lv = (0.2 + 0.12 * yard) * smoothstep(PLAYS[0]['set'] - 1, PLAYS[0]['set'], t)
            buf += own * light(HOME, lv) + (1 - own) * light(AWAY, lv)
            buf += light(WARM, 0.45 * lv / 0.32 * np.exp(-((d - x) / 12) ** 2))
        fade_all = smoothstep(0, 1.0, t) * (1 - smoothstep(D - 1.2, D, t))
        if T_HANG <= t < T_DROP:                                   # the beat of stillness under the Hail Mary
            buf *= 0.25
        sp = np.clip(crowd(t) - (1.6 - 1.2 * ex), 0, None)          # the crowd twinkles with excitement
        buf += light(WARM, 0.7 * sp)

        # ---- 0-8: pom-poms on the wings, then the teams take the field ----
        for k, tp in enumerate(POMS):
            a = t - tp
            if 0 <= a < 0.6:
                c = 690 if k % 2 == 0 else 2270
                buf += light(AWAY if k % 2 == 0 else HOME, np.exp(-a / 0.2) *
                             np.exp(-((np.abs(d - c) - 600 * a) / 70) ** 2) * (left | right))
                buf += light(GOLD, 0.8 * np.exp(-a / 0.1) * np.exp(-((d - c) / 60) ** 2))
        if T_FIELD <= t < PLAYS[0]['set'] + 0.5:
            for k in range(6):
                x_home = np.interp(t, [T_FIELD + 0.12 * k, PLAYS[0]['set'] - 0.3 + 0.05 * k], [2620, 700 - 26 - 34 * k])
                x_away = np.interp(t, [T_FIELD + 0.4 + 0.12 * k, PLAYS[0]['set'] - 0.2], [1486, 700 + 26 + 34 * k])
                if t >= T_FIELD + 0.12 * k:
                    buf += dot(x_home, HOME, 0.9, 11) + dot(x_home + 30, HOME, 0.35, 16)
                if t >= T_FIELD + 0.4 + 0.12 * k:
                    buf += dot(x_away, AWAY, 0.9, 11)

        # ---- the lines, play by play ----
        for i, p in enumerate(PLAYS):
            if p['set'] - (1.6 if i else 0) <= t < p['end']:
                lvl = 1.0 - 0.6 * smoothstep(p['snap'] + 1.5, p['end'], t)
                buf += lines(t, p, lvl, jog=i > 0)

        # ---- play one: overthrown ----
        if PLAYS[0]['set'] <= t < at(9):
            buf += dot(qb1[f], GOLD, 1.0, 9)
            buf += dot(rec1[f], GOLD, 0.95, 10)
            for k, (p0, p1) in enumerate(((2100, 2390), (2260, 2450))):
                x = np.interp(t, [PLAYS[0]['snap'], 14.3 + 0.3 * k, at(9)], [p0, p1, p1 + 10])
                buf += dot(x, AWAY, 0.9, 10)
            if BALL1[0][0] <= t <= BALL1[-1][0]:
                buf += ball(ball1[f], f, ball1, BALL1[0][0])
        for k, tg in enumerate(GROANS):                            # awww: the house sags, three times
            a = t - tg
            if 0 <= a < 1.0:
                droop = np.exp(-((d - (2512 - 900 * a)) / 260) ** 2) + 0.4 * (d > 1300)
                buf *= 1 - 0.5 * np.sin(np.pi * a) * (d > 1300)[:, None]
                buf += light(AWAY, 0.65 * (1 - 0.2 * k) * np.sin(np.pi * a) * droop * (d > 1300))

        # ---- the chants ----
        for j, tc in enumerate(CHANTS):
            if tc <= t < tc + 2 * BAR:
                buf += chant(t, tc, 0.8 + 0.1 * j)

        # ---- play two: the run, the pile-up, the fumble ----
        if PLAYS[1]['set'] <= t < T_PILE:
            buf += dot(run2[f], GOLD, 1.0, 11)
            for k in range(3):                                     # tacklers lunge where he was a moment ago
                lag = 0.3 + 0.12 * k
                x = run2[max(0, f - nframes(lag))] + 28 + 14 * k
                x = np.interp(t, [PLAYS[1]['snap'], PLAYS[1]['snap'] + 1.5], [1500 + 90 * k, x]) if not np.isnan(x) else x
                buf += dot(x, AWAY, 0.95, 11)
            for tj in JUKES:                                       # each juke flashes
                a = t - tj
                if 0 <= a < 0.3:
                    buf += light(WHITE, 0.8 * np.exp(-a / 0.08) * np.exp(-((d - run2[f]) / 30) ** 2))
        if T_PILE <= t < T_FUMBLE + 0.4:                          # the pile: a jiggling, growing heap
            a = t - T_PILE
            w = 25 + 25 * smoothstep(0, 0.8, a)
            j = rng.normal(0, 6)
            heap = np.exp(-((d - 1300 - j) / w) ** 2)
            stripe = (np.sin((d - 1300) / 6 + 25 * t) > 0)[:, None]
            buf += np.where(stripe, light(HOME, 0.9 * heap), light(AWAY, 0.9 * heap))
            buf += light(WHITE, 0.5 * np.exp(-a / 0.15) * heap)
        if T_FUMBLE <= t < T_RECOVER + 0.6:
            x = ball2[f]
            buf += ball(x, f, ball2, T_FUMBLE, sky=False) if t < T_RECOVER else 0
            for th, xh in HOPS[1:]:                                # every bounce flashes where it lands
                a = t - th
                if 0 <= a < 0.3:
                    buf += light(WARM, 0.9 * np.exp(-a / 0.08) * np.exp(-((d - xh) / 18) ** 2))
            if t < T_RECOVER:                                      # both teams dive after it, a beat late
                for k in range(3):
                    lag = 0.25 + 0.15 * k
                    xa = ball2[max(0, f - nframes(lag))]
                    buf += dot(xa + 22 + 10 * k, AWAY, 0.85, 10) + dot(xa - 22 - 10 * k, HOME, 0.85, 10)
        if T_RECOVER <= t < T_RECOVER + 1.6:                      # recovered: amber rolls out over the house
            a = t - T_RECOVER
            ring = np.exp(-((np.abs(d - 1600) - 1700 * a) / 90) ** 2)
            buf += light(HOME, 0.95 * ring * np.exp(-a / 0.9)) + light(GOLD, 0.9 * np.exp(-a / 0.15) *
                                                                      np.exp(-((d - 1600) / 40) ** 2))

        # ---- two-minute warning and play three: the clock, the scramble, the Hail Mary ----
        if T_WARN <= t < T_THROW + 1.0:
            seg = (d - pf0) / (pf1 - pf0) * 20
            on = (seg >= 0) & (seg < 20)
            built = np.floor(seg) < 20 * smoothstep(T_WARN, T_WARN + 1.0, t)
            left_ = np.array([np.sum(np.array(TICKS) > t)])[0]
            lit = on & built & (np.floor(seg) < left_)
            gap = np.sin(np.pi * (seg % 1)) ** 0.3
            urgent = smoothstep(TICKS[12], TICKS[-1], t)
            tick = np.exp(-(((t - TICKS[0]) % BEAT) / 0.12)) * (1.0 if t >= TICKS[0] else 0.6)
            colr = GOLD * (1 - urgent) + AWAY * urgent
            buf *= (1 - 0.8 * on)[:, None]
            buf += light(colr, (0.6 + 0.35 * tick) * gap * lit * (1.0 if t >= TICKS[0] else 0.55))
            if t < TICKS[0]:                                        # waiting: a light runs round the clock
                buf += light(WHITE, 0.8 * np.exp(-(((seg - 40 * (t - T_WARN)) % 20) / 1.2) ** 2) * on * built)
            if t >= T_THROW:                                       # zero: the porch flashes
                buf += light(AWAY, 0.9 * np.exp(-(t - T_THROW) / 0.25) * porch)
        if PLAYS[2]['set'] <= t < T_THROW + 0.5:
            buf += dot(qb3[f], GOLD, 1.0, 11)
            for k, lag in enumerate((0.45, 0.75)):                 # two rushers, always a moment behind
                x = qb3[max(0, f - nframes(lag))]
                x = np.interp(t, [PLAYS[2]['snap'], PLAYS[2]['snap'] + 1.0], [960 + 40 * k, x + 30 + 20 * k])
                buf += dot(x, AWAY, 0.95, 11)
            for ts in SPINS:                                       # spins out of the sack: a ring
                a = t - ts
                if 0 <= a < 0.4:
                    buf += light(WHITE, 0.9 * np.exp(-a / 0.12) * np.exp(-((np.abs(d - qb3[f]) - 150 * a) / 10) ** 2))
        if PLAYS[2]['snap'] <= t < TD + 0.5:                      # the receivers jostle in the end zone
            for k, (base, col) in enumerate(((2420, GOLD), (2380, AWAY), (2470, AWAY))):
                x = np.interp(t, [PLAYS[2]['snap'], 58], [2150 + 60 * k, base]) + 25 * np.sin(2 * np.pi * (0.8 + 0.3 * k)
                                                                                            * t + k)
                if t >= T_TIP:
                    x = np.interp(t, [T_TIP, TD], [x, 2445 if k == 0 else base + (30 if k == 2 else -30)])
                buf += dot(x, col, 0.95, 11)
        if T_THROW <= t <= TD:
            buf += ball(ball3[f], f, ball3, T_THROW)
            if T_TIP <= t < T_TIP + 0.4:                          # tipped!
                buf += light(WHITE, 0.9 * np.exp(-(t - T_TIP) / 0.1) * np.exp(-((d - 2395) / 30) ** 2))

        # ---- TOUCHDOWN ----
        u = t - TD
        if u >= 0:
            ez = d > 2330
            buf += light(WHITE, 1.0 * np.exp(-u / 0.25) * np.exp(-((d - 2445) / 40) ** 2))
            for th in TD_HITS:
                a = t - th
                if 0 <= a < 0.45:
                    buf += light(GOLD, 0.95 * np.exp(-a / 0.15) * ez)
            for t0, p0, tgt in ROCKETS:                            # fireworks fly back along the roof
                a = t - t0
                if 0 <= a < 1.2:
                    x = p0 + (tgt - p0) * smoothstep(0, 1.2, a) ** 0.8
                    buf += light(WARM, 0.95 * np.exp(-((d - x) / 8) ** 2)) + light(GOLD, 0.4 * np.exp(-((d - x - 30) / 25) ** 2))
            buf += sparks(rock, t, 1.6, 7)
            for w0, direction in WAVES:                             # the stadium waves
                a = t - w0
                if -0.5 < a < 5.0:
                    front = a * WAVE_SPEED
                    pos = (G.length - d) if direction < 0 else d
                    lag = front - pos
                    stand = np.where(lag > 0, np.exp(-lag / 300), np.exp(-(lag / 35) ** 2))
                    shirt = np.where(((d // 40) % 2 == 0)[:, None], HOME, GOLD)
                    buf += light(1.0, 0.95 * stand) * shirt
            if CANNONS[0] - 0.5 <= t < T_END:                       # victory: marching stripes under the cannons
                k = t / BEAT
                s = d + (np.floor(k) + smoothstep(0, 0.35, k % 1)) * 40
                shape = np.sin(np.pi * ((s / 80) % 1)) ** 0.8
                buf += light(1.0, (0.35 + 0.2 * np.exp(-((t % BEAT) / 0.15))) * shape *
                             smoothstep(CANNONS[0] - 0.5, CANNONS[0], t)) * np.where(((s // 80) % 2 == 0)[:, None], HOME, AWAY)
            buf += sparks(cann, t, 1.8, 6)
            for tc in CANNONS:
                a = t - tc
                if 0 <= a < 0.3:
                    buf += light(WHITE, 0.9 * np.exp(-a / 0.08) * (np.exp(-((d - 892) / 30) ** 2) + np.exp(-((d - 2036) / 30) ** 2)))
            buf += sparks(fins, t, 1.4, 8)
            if t >= T_END:
                a = t - T_END
                buf += light(GOLD, (0.9 * np.exp(-a / 0.3) + 0.4) * np.ones(n))
        out[f][G.path] = np.clip(buf * fade_all, 0, 1)
    return out


# ---------------------------------------------------------------- music ----------------------------------------------
# A marching band in Bb at 120 BPM with an original fight song: trumpets on the tune, tuba and trombones oom-pah,
# marching snare and bass drum. Pom-poms are tenor-drum hits panned to their wing; the teams run on to a snare roll
# and a brass fanfare. Each play sets on a bass drum, counts "hut, hut" on the tenors and is snapped on a cymbal.
# A ball in the air is a slide whistle that climbs with its height and follows it across the house; the overthrow
# gets three sad trombones on the three sags, the chants are bass drum, bass drum, clap clap with the crowd. The
# runner's jukes are woodblocks and whistles, the pile-up a timpani rumble and ratchet, every fumble bounce a
# xylophone note where it lands. The two-minute warning brings in a clock that ticks on the woodblock every beat
# over a climbing tuba, the scramble's spins are cymbal swishes, the clock's zero a buzzer; the Hail Mary is a long
# roll that hushes to nothing at the top of its arc, rebuilds as it falls, gasps at the tip, and the touchdown is the
# whole band: three hits, a firework for every rocket, a brass sweep with each wave, the fight song to the end.

SONG = ['Bb', 'Eb', 'F7', 'Bb', 'Bb', 'Eb', 'F7', 'Bb']
FIGHT = [  # per bar: (beat, note, beats)
    [(0, 'F4', 1), (1, 'Bb4', 1), (2, 'D5', 1.5), (3.5, 'Bb4', 0.5)],
    [(0, 'Eb5', 1.5), (1.5, 'D5', 0.5), (2, 'C5', 1), (3, 'Bb4', 1)],
    [(0, 'A4', 1), (1, 'C5', 1), (2, 'F5', 1.5), (3.5, 'Eb5', 0.5)],
    [(0, 'D5', 2), (2, 'Bb4', 1)],
    [(0, 'F4', 0.5), (0.5, 'F4', 0.5), (1, 'Bb4', 1), (2, 'D5', 1), (3, 'F5', 1)],
    [(0, 'G5', 1.5), (1.5, 'F5', 0.5), (2, 'Eb5', 1), (3, 'G4', 1)],
    [(0, 'F4', 1), (1, 'A4', 1), (2, 'C5', 1), (3, 'Eb5', 1)],
    [(0, 'D5', 1), (1, 'Bb4', 1), (2, 'Bb4', 1)]]
CHORD = {'Bb': ('D4', 'F4', 'Bb4'), 'Eb': ('Eb4', 'G4', 'Bb4'), 'F7': ('Eb4', 'F4', 'A4')}
ROOT = {'Bb': ('Bb1', 'F2'), 'Eb': ('Eb2', 'Bb1'), 'F7': ('F2', 'C2')}
TONES = {'Bb': (46, 50, 53), 'Eb': (51, 55, 58), 'F7': (53, 57, 60, 63)}


def score(M, G):
    from pixelhome.audio import note, slide, whoosh, SR
    n = note
    F = nframes(D)
    L = G.length
    tpt = M.sampler('Brass/Trumpet/stac/*.wav', tune=-12)
    tpt_l = M.sampler('Brass/Trumpet/sus/*.wav', tune=-12)
    bone = M.sampler('Brass/Tenor Trombone/stac/*.wav', tune=-12)
    bone_l = M.sampler('Brass/Tenor Trombone/sus/*.wav', tune=-12)
    fall = M.sampler('Brass/OldTrombone/Fall/*.wav', tune=-12)
    horn = M.sampler('Brass/F Horn/sus/*.wav', tune=-12)
    tuba = M.sampler('Brass/Tuba/stac/*.wav', tune=-12)
    glock = M.sampler('Percussion/Glock/*.wav', tune=-12)
    xylo = M.sampler('Percussion/Xylo/*.wav', tune=-12)
    snare = M.hits('VSCO 1 Percussion/drums/snare/drum3_marching/snare3_[fm]*.wav')
    snare_g = M.hits('VSCO 1 Percussion/drums/snare/drum3_marching/snare3_p*.wav')
    rim = M.hits('VSCO 1 Percussion/drums/snare/drum3_marching/snare3_rimshot*.wav')
    roll = M.hits('Percussion/Snare2-rollSN_v5*.wav')
    bd = M.hits('VSCO 1 Percussion/drums/bass/bdrum_f*_[12].wav')
    bd_big = M.hits('VSCO 1 Percussion/drums/bass/bdrum_fff*.wav')
    tenor = M.hits('VSCO 1 Percussion/drums/tenor/tenor_lower/tenor_f*.wav')
    clash = M.hits('VSCO 1 Percussion/varMetal/Cymbals/clash/crash_hit_ff*.wav')
    crash_s = M.hits('Percussion/cymbal-crashshort*.wav')
    ccresc = M.hits('Percussion/susCymb1-cresc-Short*.wav')
    timp = M.hits('Percussion/Timpani/Timpani1_Hit*.wav')
    troll = M.hits('Percussion/Timpani/Rolls/*_v5_*.wav')
    wood = M.hits('VSCO 1 Percussion/varWood/wood_click*.wav')
    block = M.hits('VSCO 1 Percussion/varWood/claves_m*.wav')
    slap = M.hits('VSCO 1 Percussion/varWood/slapstick[0-9].wav')
    ratchet = M.hits('Percussion/Ratchet1-Fast*.wav')

    for name, gain, rev in (('melody', 0.4, 0.2), ('band', 0.3, 0.18), ('bass', 0.5, 0.08), ('drums', 0.45, 0.12),
                            ('perc', 0.5, 0.12), ('fx', 0.2, 0.2), ('crowd', 0.12, 0.3), ('ref', 0.05, 0.2),
                            ('bells', 0.3, 0.25)):
        M.bus(name, gain=0.9 * gain, reverb=rev)

    order = np.argsort(G.pd)
    xs, ds = G.pos[order, 0], G.pd[order]
    x0, x1 = xs.min(), xs.max()

    def pan_at(dd):                          # path distance -> left/right across the facade, as seen from the street
        x = np.interp(np.clip(dd, 0, L), ds, xs)
        return float(0.85 * (2 * (x - x0) / (x1 - x0) - 1))

    def moving(sig, t0, ts, ps):            # constant-power pan that follows (time, pan) points
        tt = t0 + np.arange(sig.shape[1]) / SR
        a = (np.interp(tt, ts, ps) + 1) * np.pi / 4
        return sig * np.vstack([np.cos(a), np.sin(a)]) * np.sqrt(2)

    def whistle(t0, ts, fs, amp=0.35):      # a slide whistle that follows a frequency curve
        tt = np.arange(int((ts[-1] - t0) * SR)) / SR + t0
        f = np.interp(tt, ts, fs)
        ph = 2 * np.pi * np.cumsum(f) / SR
        u = tt - t0
        env = np.clip(u / 0.05, 0, 1) * np.clip((ts[-1] - tt) / 0.3, 0, 1)
        breath = np.convolve(M.rng.normal(0, 1, len(tt)), np.ones(24) / 24, 'same') * 0.08
        sig = amp * env * (np.sin(ph) + 0.12 * np.sin(2 * ph) + breath * (1 + np.sin(ph)))
        return np.vstack([sig, sig])

    def flight(waypoints, sigma, t0, t1, lo, span, quiet=None):     # whistle for a ball in the air
        x = track(waypoints, F, sigma)
        fr = np.arange(nframes(t0), min(F, nframes(t1)))
        ts = fr * DT
        xb = np.nan_to_num(x[fr], nan=L)
        h = np.array([height(v) for v in xb])
        fs = lo * 2 ** (span * h + 0.25 * (ts - t0) / (t1 - t0))
        ps = np.array([pan_at(v) for v in xb])
        sig = moving(whistle(ts[0], ts, fs), ts[0], ts, ps)
        if quiet:                            # softer through the hush
            tt = ts[0] + np.arange(sig.shape[1]) / SR
            sig = sig * (1 - 0.6 * smoothstep(quiet[0], quiet[0] + 0.4, tt) * (1 - smoothstep(quiet[1] - 0.2, quiet[1], tt)))
        M.add('fx', sig, ts[0])

    def ref(t, dur=0.5, blasts=1):          # pea whistle
        for b in range(blasts):
            tt = np.arange(int(dur * SR)) / SR
            f = 2800 + 140 * np.sign(np.sin(2 * np.pi * 32 * tt))
            ph = 2 * np.pi * np.cumsum(f) / SR
            env = np.clip(tt / 0.02, 0, 1) * np.clip((dur - tt) / 0.05, 0, 1)
            sig = env * (np.sin(ph) + 0.3 * np.sin(2 * ph))
            M.add('ref', np.vstack([sig, sig]), t + b * (dur + 0.12), 1.0, 0.0)

    def buzzer(t, dur=1.0):                 # the game clock's horn
        tt = np.arange(int(dur * SR)) / SR
        ph = 2 * np.pi * 233 * tt
        sig = sum(np.sign(np.sin(k * ph)) / k for k in (1, 2, 3)) * np.clip(tt / 0.01, 0, 1) * np.clip((dur - tt) / 0.05, 0, 1)
        M.add('fx', np.vstack([sig, sig]) * 0.35, t, 1.0, pan_at(1486))

    # ---- the crowd: band-passed noise breathing with the excitement, and swells for the big moments ----
    N = int(D * SR)
    spec = np.fft.rfft(M.rng.normal(0, 1, (2, N)), axis=1)
    fq = np.fft.rfftfreq(N, 1 / SR)
    spec *= (fq / 350) ** 2 / (1 + (fq / 350) ** 2) / (1 + (fq / 2200) ** 2)
    noise = np.fft.irfft(spec, N, axis=1)
    noise /= np.abs(noise).max()
    tt = np.arange(N) / SR
    babble = 1 + 0.25 * np.sin(2 * np.pi * 1.7 * tt) * np.sin(2 * np.pi * 0.31 * tt + 1)
    ex = [(0, 0.5), (8, 0.4), (15, 0.8), (18, 0.4), (28, 0.9), (34, 1.3), (38, 0.4), (54, 0.9), (T_HANG, 0.05),
          (T_DROP, 0.6), (T_TIP, 1.0), (TD, 1.8), (TD + 2, 1.0), (88, 1.1), (90, 0.3)]
    env = np.array([keys(t, ex) for t in tt[::480]])
    env = np.interp(tt, tt[::480], env)
    M.add('crowd', noise * babble * env, 0.0)
    for k, tg in enumerate(GROANS):                                                               # awww
        M.add('crowd', whoosh(1.0, 1300 - 200 * k, 300, 0.9, seed=5 + k), tg, 0.8, pan_at(2200))
    M.add('crowd', whoosh(1.6, 300, 1800, 0.9, seed=8), T_PILE - 0.3, 0.8, pan_at(1300))          # oooh
    M.add('crowd', whoosh(2.5, 400, 2400, 1.0, seed=9), T_RECOVER - 0.2, 1.0, pan_at(1600))       # yeah!
    M.add('crowd', whoosh(0.8, 500, 2500, 0.9, seed=10), T_TIP - 0.1, 0.8, pan_at(2400))          # gasp

    def bar_of(t, t0):
        return int((t - t0) // BAR)

    def march(t0, bars, stop=None, vel=100, big=1.0):
        """The fight song from t0, bars by index into FIGHT, with oom-pah and drums; nothing at or after stop."""
        stop = stop if stop is not None else 1e9
        for i, b in enumerate(bars):
            tb = t0 + BAR * i
            c = SONG[b]
            for bt, m, dd in FIGHT[b]:
                t = tb + bt * BEAT
                if t >= stop:
                    continue
                M.add('melody', tpt.play(n(m), vel, dur=dd * BEAT * 0.85, release=0.08), t, big, 0.05)
                M.add('melody', tpt.play(n(m) - 12, vel - 10, dur=dd * BEAT * 0.85, release=0.08), t, 0.5 * big, -0.1)
                M.add('bells', glock.play(n(m) + 12, vel - 20), t, 0.4, 0.2)
            for k in range(4):
                t = tb + k * BEAT
                if t >= stop:
                    continue
                if k % 2 == 0:
                    M.add('bass', tuba.play(n(ROOT[c][k // 2]), vel + 6), t, big, -0.05)
                    M.add('drums', bd.play(vel), t, 0.9 * big, 0.0)
                else:
                    for m in CHORD[c]:
                        M.add('band', bone.play(n(m) - 12, vel - 8, dur=0.2), t, 0.7 * big, -0.25)
                        M.add('band', horn.play(n(m), vel - 20, dur=0.2), t, 0.5 * big, 0.25)
            for e in range(8):
                t = tb + e * BEAT / 2
                if t < stop and e % 4 != 1:
                    M.add('drums', (snare if e % 2 == 0 else snare_g).play(vel if e % 4 == 0 else vel - 25), t,
                          0.7 * big, 0.1)
            if i % 4 == 0 and tb < stop:
                M.add('drums', clash.play(vel), tb, 0.5 * big)

    def buzz(t0, t1, v0, v1, p=0.1):        # a snare roll in sixteenths, v0 -> v1
        nk = int((t1 - t0) / (BEAT / 4))
        for k in range(nk):
            M.add('drums', snare_g.play(v0 + (v1 - v0) * k / max(1, nk - 1)), t0 + k * BEAT / 4, 0.6, p)

    def lineup(p):                          # set, hut, hut, snap
        tl, ts, s = p['set'], p['snap'], p['s']
        M.add('drums', bd_big.play(105), tl, 0.9)
        for m in ('D4', 'F4', 'Bb4'):
            M.add('band', tpt_l.play(n(m), 96, dur=0.4), tl, 0.6, 0.0)
        for k in range(1, 4):                # the tuba waits on F
            M.add('bass', tuba.play(n('F2'), 84 + 6 * k), tl + k * BEAT, 0.8)
        for k in (2, 3):
            M.add('drums', tenor.play(115), tl + k * BEAT, 1.0, pan_at(s))
            M.add('crowd', whoosh(0.3, 600, 900, 0.7, seed=int(tl * 10 + k)), tl + k * BEAT, 0.6, pan_at(s))
        M.add('drums', crash_s.play(115), ts, 0.7)
        M.add('drums', bd_big.play(115), ts, 0.9, pan_at(s))
        M.add('perc', slap.play(110), ts, 0.7, pan_at(s))

    def chant(t0, big=1.0):                 # bass drum, bass drum, clap clap
        for bar in range(2):
            for k in range(4):
                t = t0 + bar * BAR + k * BEAT
                if k < 2:
                    M.add('drums', bd_big.play(118), t, 1.0 * big, -0.6 if k == 0 else 0.6)
                    M.add('bass', tuba.play(n('Bb1') if k == 0 else n('F2'), 110), t, 0.9 * big)
                    M.add('crowd', whoosh(0.35, 500, 1500, 1.0, seed=int(t * 10)), t, 0.8 * big, -0.5 if k == 0 else 0.5)
                else:
                    M.add('drums', rim.play(124), t, 1.0 * big)
                    M.add('perc', slap.play(115), t, 0.9 * big)

    # ---- 0-8: pom-poms, then the teams take the field ----
    for k, tp in enumerate(POMS):
        p = pan_at(690 if k % 2 == 0 else 2270)
        M.add('drums', tenor.play(110), tp, 1.0, p)
        M.add('drums', bd.play(100), tp, 0.8, p)
        M.add('drums', crash_s.play(70), tp, 0.3, p)
        if k % 2:
            M.add('drums', snare.play(90), tp + BEAT / 2, 0.6, 0.1)
    r = roll.play(100, dur=4.0)
    M.add('drums', r * np.linspace(0.3, 1, r.shape[1]) ** 2, T_FIELD, 0.6)
    M.add('fx', moving(whoosh(3.0, 300, 1500, 0.9, seed=2), T_FIELD, [T_FIELD, T_FIELD + 3], [0.85, -0.3]), T_FIELD, 0.6)
    for t, m, dd in ((T_FIELD, 'F4', 0.4), (T_FIELD + 0.5, 'Bb4', 0.4), (T_FIELD + 1.0, 'D5', 0.4), (T_FIELD + 1.5, 'F5', 0.9),
                     (T_FIELD + 2.5, 'D5', 0.4), (T_FIELD + 3.0, 'F5', 0.9)):
        M.add('melody', tpt.play(n(m), 110, dur=dd), t, 1.0, 0.05)
        M.add('band', bone.play(n(m) - 12, 104, dur=dd), t, 0.8, -0.2)

    # ---- play one, overthrown ----
    lineup(PLAYS[0])
    march(PLAYS[0]['snap'], range(3), stop=GROANS[0])
    flight(BALL1, 0.12, BALL1[0][0], BALL1[-1][0], 480, 1.5)
    ref(BALL1[-1][0], 0.55)
    for k, (tg, m) in enumerate(zip(GROANS, ('Bb3', 'A3', 'Ab3'))):              # three sags, three trombones
        if k < 2:
            M.add('melody', bone_l.play(n(m), 104, dur=0.8, release=0.15), tg, 1.0, pan_at(2200))
        else:
            M.add('melody', fall.play(n(m), 110), tg, 1.0, pan_at(2200))
        M.add('bass', tuba.play(n(m) - 24, 96), tg, 0.8)
    chant(CHANTS[0])

    # ---- play two: the run, the pile-up, the fumble ----
    lineup(PLAYS[1])
    march(PLAYS[1]['snap'], (4, 5), stop=T_PILE)
    for tj in JUKES:
        x = float(np.interp(tj, [w[0] for w in RUN2], [w[1] for w in RUN2]))
        M.add('perc', wood.play(115), tj, 1.0, pan_at(x))
        M.add('fx', slide(0.0, 0.18, 700, 1500, 0.2, 0.5), tj, 0.7, pan_at(x))
        M.add('perc', block.play(100), tj - 0.3, 0.5, pan_at(x + 40))           # the tackler's lunge, just behind
    p = pan_at(1300)
    M.add('drums', bd_big.play(127), T_PILE, 1.0, p)
    M.add('drums', clash.play(120), T_PILE, 0.7, p)
    M.add('drums', timp.play(120, pitch=-3), T_PILE, 0.8, p)
    M.add('perc', slap.play(127), T_PILE, 0.8, p)
    M.add('drums', troll.play(95, dur=T_FUMBLE - T_PILE), T_PILE + 0.1, 0.7, p)
    M.add('perc', ratchet.play(90, dur=1.6), T_PILE + 0.2, 0.7, p)
    for k, (th, x) in enumerate(HOPS[1:-1]):                                   # the loose ball
        m = n('Bb5') - [0, 3, 5, 2, 7, 5, 10][k % 7]
        M.add('perc', xylo.play(m, 112), th, 1.0, pan_at(x))
        M.add('perc', wood.play(100), th, 0.6, pan_at(x))
        M.add('fx', slide(0.0, 0.12, 500, 1100, 0.14, 0.5), th, 0.45, pan_at(x))
        M.add('bass', tuba.play(n('F2') + (k % 2) * 7, 100), th, 0.8)
    buzz(T_FUMBLE, T_RECOVER, 60, 112, pan_at(1450))
    M.add('drums', clash.play(118), T_RECOVER, 0.7, pan_at(1600))                 # recovered: home team ball
    for m in ('Bb3', 'D4', 'F4', 'Bb4'):
        M.add('melody', tpt_l.play(n(m), 115, dur=0.6, release=0.2), T_RECOVER, 0.6, pan_at(1600))
    M.add('bass', tuba.play(n('Bb1'), 120), T_RECOVER)
    ref(T_RECOVER + 0.3, 0.35, 2)
    chant(CHANTS[1], 1.1)

    # ---- two-minute warning: the clock; play three, the scramble ----
    ref(T_WARN, 0.4, 3)
    for k in range(10):                                                         # the clock builds
        M.add('bells', glock.play(n('F4') + [0, 2, 4, 5, 7, 9, 11, 12, 14, 16][k], 90), T_WARN + 0.1 * k, 0.7,
              pan_at(1311 + 34 * k))
    for e in range(int((PLAYS[2]['set'] - T_WARN - 1.5) / (BEAT / 2))):         # suspense: low tuba eighths
        t = T_WARN + 1.5 + e * BEAT / 2
        M.add('bass', tuba.play(n('F1') + (7 if e % 2 else 0), 80 + e), t, 0.8)
        if e % 2 == 0:
            M.add('drums', timp.play(70 + e * 2, pitch=-5), t, 0.4)
    lineup(PLAYS[2])
    climb = ['F2', 'Gb2', 'G2', 'Ab2', 'A2', 'Bb2', 'B2', 'C3', 'Db3', 'D3']
    for e, tk in enumerate(TICKS):                                              # the clock ticks every beat
        urgent = e >= 12
        M.add('perc', block.play(105 + (15 if urgent else 0), pitch=2 * (e >= 16)), tk, 1.0 if urgent else 0.8, pan_at(1486))
        for h in range(2):                                                      # the chase: tuba eighths, climbing
            t = tk + h * BEAT / 2
            r = n(climb[min(len(climb) - 1, e // 2)])
            M.add('bass', tuba.play(r + 7 * h, 96 + e), t, 0.55, -0.05)
            M.add('drums', snare_g.play(70 + 2 * e), t, 0.6, 0.1)
        if e % 2 == 0:                                                          # brass stabs climb with it
            r = n(climb[min(len(climb) - 1, e // 2)]) + 24
            for k, off in enumerate((0, 1.5)):
                for mm in (r, r + 4, r + 7):
                    M.add('melody', tpt.play(mm, 96 + e, dur=0.2), tk + off * BEAT, 0.45, 0.0)
                    M.add('band', bone.play(mm - 12, 92 + e, dur=0.2), tk + off * BEAT, 0.5, -0.2)
        if urgent:
            M.add('drums', bd.play(90 + 3 * e), tk, 0.8)
    for ts in SPINS:                                                            # spins out of the sack
        x = float(np.interp(ts, [w[0] for w in QB3], [w[1] for w in QB3]))
        M.add('drums', crash_s.play(100), ts, 0.6, pan_at(x))
        M.add('fx', whoosh(0.35, 800, 3500, 0.8, seed=int(ts * 10)), ts - 0.1, 0.6, pan_at(x))
        M.add('melody', bone.play(n('F3'), 105, dur=0.15), ts, 0.7, pan_at(x))
    r = ccresc.play(100, dur=TICKS[-1] - TICKS[12])
    M.add('drums', r * np.linspace(0.1, 1, r.shape[1]) ** 2, TICKS[12], 0.5)

    # ---- 54: zero; the Hail Mary; the hush at the top; the tip; touchdown ----
    buzzer(T_THROW)
    M.add('perc', rim.play(124), T_THROW, 0.9, pan_at(80))
    M.add('drums', bd_big.play(120), T_THROW, 1.0, pan_at(80))
    flight(BALL3, 0.1, T_THROW, TD, 420, 1.4, quiet=(T_HANG, T_DROP))
    r = troll.play(110, dur=T_HANG - T_THROW)
    M.add('drums', r * np.linspace(0.4, 1, r.shape[1]), T_THROW, 0.8)
    for k, m in enumerate(('F3', 'G3', 'A3')):                                   # the band climbs with the ball
        tk = T_THROW + 1.3 * k
        for mm in (n(m), n(m) + 4, n(m) + 7):
            M.add('band', tpt_l.play(mm, 90 + 8 * k, dur=1.3, release=0.1), tk, 0.5, pan_at(80 + 450 * k))
        M.add('bass', tuba.play(n(m) - 12, 100 + 5 * k), tk, 1.0)
    for mm in (n('Bb3'), n('D4'), n('F4')):                                      # the hush: one high held chord
        M.add('band', horn.play(mm, 55, dur=T_DROP - T_HANG, release=0.2), T_HANG, 0.5, pan_at(1486))
    M.add('bells', glock.play(n('F5'), 60), T_HANG + 0.5, 0.4, pan_at(1500))
    r = troll.play(110, dur=TD - T_DROP)
    M.add('drums', r * np.linspace(0.15, 1, r.shape[1]) ** 2, T_DROP, 0.9)
    r = roll.play(100, dur=TD - T_DROP)
    M.add('drums', r * np.linspace(0.1, 1, r.shape[1]) ** 2, T_DROP, 0.6)
    for k, m in enumerate(('F2', 'G2', 'A2', 'C3')):                             # tuba steps down with it
        M.add('bass', tuba.play(n(m), 105 + 5 * k), T_DROP + k * BEAT * 2, 1.0)
    M.add('perc', xylo.play(n('C6'), 120), T_TIP, 1.0, pan_at(2395))            # boink
    M.add('fx', slide(0.0, 0.25, 800, 1600, 0.3, 0.5), T_TIP, 0.8, pan_at(2395))

    pz = pan_at(2445)
    M.add('drums', bd_big.play(127), TD, 1.0, pz)
    M.add('drums', clash.play(127), TD, 0.8, pz)
    M.add('drums', timp.play(127), TD, 0.8, pz)
    for m in ('Bb3', 'D4', 'F4', 'Bb4', 'D5'):
        M.add('melody', tpt_l.play(n(m), 120, dur=0.45, release=0.1), TD, 0.6, pz)
    M.add('bass', tuba.play(n('Bb1'), 124), TD)
    ref(TD + 0.05, 0.4)
    for k, th in enumerate(TD_HITS):                                            # TOUCH - DOWN - !
        M.add('drums', bd_big.play(124), th, 1.0, pz)
        M.add('drums', timp.play(118), th, 0.7, pz)
        M.add('drums', (clash if k == 2 else crash_s).play(118), th, 0.7, pz)
        for m in CHORD['Bb']:
            M.add('melody', tpt.play(n(m) + (12 if k == 2 else 0), 118, dur=0.3), th, 0.6, pz)
        M.add('bass', tuba.play(n('Bb1') + 7 * (k == 1), 120), th)
    for k, (t0, p0, tgt) in enumerate(ROCKETS):                                 # fireworks: whizz, bang
        M.add('fx', moving(whoosh(1.2, 600, 4000, 0.7, seed=30 + k), t0, [t0, t0 + 1.2], [pan_at(p0), pan_at(tgt)]), t0, 0.6)
        M.add('drums', bd_big.play(120), t0 + 1.2, 0.8, pan_at(tgt))
        M.add('drums', crash_s.play(110), t0 + 1.2, 0.6, pan_at(tgt))
        for j in range(5):
            M.add('bells', glock.play(n('Bb4') + [0, 4, 7, 12, 16][j] - 2 * k, 80), t0 + 1.25 + 0.06 * j, 0.4, pan_at(tgt))

    # ---- the waves, the cannons, the fight song to the end ----
    T5 = WAVES[0][0]
    march(T5, (0, 1, 2, 3, 4, 5, 6, 7), vel=108)
    march(FINALE[0], (0, 1, 2), vel=112, big=1.1)
    for j, (w0, direction) in enumerate(WAVES):
        for k in range(17):
            pos = L * k / 16
            dd = L - pos if direction < 0 else pos
            t = w0 + pos / WAVE_SPEED
            c = SONG[bar_of(t, T5) % 8]
            asc = sorted(m for m in {r + 12 * o for r in TONES[c] for o in range(-1, 4)} if n('Bb3') <= m <= n('Bb5'))
            m = asc[int(k * (len(asc) - 1) / 16)]
            M.add('band', tpt.play(m, 96 + k + 6 * j, dur=0.3), t, 0.9, pan_at(dd))
            M.add('band', bone.play(m - 12, 96 + k + 6 * j, dur=0.3), t, 0.8, pan_at(dd))
        tw = np.linspace(w0, w0 + L / WAVE_SPEED, 20)
        dw = L - (tw - w0) * WAVE_SPEED if direction < 0 else (tw - w0) * WAVE_SPEED
        sw = whoosh(L / WAVE_SPEED + 0.5, 300, 1600, 1.0, seed=20 + j)
        M.add('crowd', moving(sw, w0, tw, [pan_at(x) for x in dw]), w0, 1.4)
    for k, tc in enumerate(CANNONS):                                            # confetti cannons on the downbeats
        for p in (892, 2036):
            M.add('drums', bd_big.play(118), tc, 0.6, pan_at(p))
            M.add('perc', slap.play(110), tc, 0.5, pan_at(p))
        M.add('drums', crash_s.play(110), tc, 0.5)
        M.add('crowd', whoosh(0.6, 400, 2200, 1.0, seed=60 + k), tc, 0.8)
    rng = np.random.default_rng(SEED + 1)
    for k, t in enumerate(FINALE):                                              # a firework on every beat
        M.add('drums', crash_s.play(90), t, 0.35, float(rng.uniform(-0.8, 0.8)))
        M.add('bells', glock.play(n('F5') - (k % 4) * 2, 70), t + 0.04, 0.35, float(rng.uniform(-0.8, 0.8)))
    for m in ('Bb3', 'D4', 'F4', 'Bb4'):                                         # the final chord
        M.add('melody', tpt_l.play(n(m), 115, dur=D - T_END, release=1.2), T_END, 0.55)
        M.add('band', horn.play(n(m) - 12, 104, dur=D - T_END, release=1.2), T_END, 0.6)
    M.add('band', bone_l.play(n('Bb2'), 108, dur=D - T_END, release=1.2), T_END, 0.7)
    M.add('bass', tuba.play(n('Bb1'), 124), T_END)
    M.add('drums', clash.play(122), T_END, 0.8)
    M.add('drums', bd_big.play(122), T_END, 1.0)
    M.add('drums', troll.play(90, dur=1.2), T_END + 0.2, 0.6)
