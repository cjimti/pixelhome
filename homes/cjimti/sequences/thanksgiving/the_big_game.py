"""The Big Game: Football on the roofline, with the porch as the sky. A pass from the Left wing climbs
the Porch Left, hangs at its apex across the Porch Front (far away and high in the street view) and
drops down the Porch Right to the Right wing, its shadow sliding along the wing fronts below. Play
one is overthrown out the free end. Play two is a run that ends in a pile-up at the porch corner and
a fumble that bounces along the porch. Play three: the quarterback scrambles all the way to the back
of the Side and throws the Hail Mary down the entire roof. Touchdown, and the whole house does the wave."""
import numpy as np
from pixelhome.fx import DT, hexc, light, keys, smoothstep, Flicker, nframes

CODE = 'TG05'
TITLE = 'The Big Game'
KIND = 'show'
DESCRIPTION = ('Football on the roof, with the porch as the sky: passes arc up and over the porch, a fumble bounces '
               'along it, and a Hail Mary from the back of the house ends in a touchdown and a stadium wave.')

HOME = hexc('#ff8a18')         # amber jerseys
AWAY = hexc('#c0102a')         # cranberry jerseys
BALL = hexc('#ff9030')
WARM = hexc('#ffc27a')
GOLD = hexc('#ffb000')
BROWN = hexc('#5a1c04')
D = 60.0


def track(pts, F, sigma=0.12):
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


def render(G, seed=25):
    rng = np.random.default_rng(seed)
    F = nframes(D)
    out = np.zeros((F, G.N, 3))
    n = G.N
    pdp = G.pd[G.path]
    X = G.pos[G.path, 0]
    wingf = ((pdp > 492) & (pdp < 892)) | (pdp > 2036)
    crowd_f = Flicker(rng, n, 0.5, 3.0)

    players = []                      # (colour, waypoints, size)

    def add(col, pts, size=8.0):
        players.append((col, track(pts, F), size, pts[0][0], pts[-1][0]))

    # --- play 1: overthrown ---
    add(HOME, [(2.5, 700), (5.0, 700), (5.8, 640), (7.0, 640), (8.0, 690), (12.5, 690)])            # QB
    add(HOME, [(2.5, 2180), (6.0, 2180), (9.5, 2330), (10.3, 2350), (11.2, 2470), (12.5, 2480)])    # receiver
    add(AWAY, [(2.5, 2140), (6.0, 2140), (9.8, 2300), (12.5, 2330)])
    add(AWAY, [(2.5, 2250), (6.0, 2250), (10.0, 2390), (12.5, 2420)])
    ball1 = track([(5.0, 700), (5.8, 645), (6.0, 650), (6.5, 892), (7.6, 1311), (9.1, 1660), (9.9, 2033),
                   (10.4, 2290), (11.4, 2600)], F, 0.15)

    # --- play 2: the run, the pile-up, the fumble ---
    add(HOME, [(14.0, 700), (16.0, 700), (17.0, 820), (17.4, 800), (18.2, 1000), (18.6, 980), (19.3, 1282),
               (21.5, 1282), (23.0, 1505), (27.0, 1505)])                                          # runner
    for k, p0 in enumerate((1760, 1860, 1960)):
        add(AWAY, [(14.0, p0), (16.0, p0), (19.25, 1298 + 6 * k), (21.5, 1300 + 9 * k), (23.5, 1330 + 30 * k),
                   (26.0, 1700 + 60 * k)])
    add(HOME, [(14.0, 600), (16.0, 600), (19.2, 1270), (21.6, 1276), (23.4, 1495), (27.0, 1495)])   # blocker
    hops = [(19.45, 1290)]
    p, tt = 1290.0, 19.45
    for k in range(7):
        tt += 0.42 - 0.035 * k
        p += rng.uniform(-30, 70) * (1 - k / 9)
        hops.append((tt, p))
    hops.append((22.9, 1505))
    ball2 = track([(16.0, 700), (19.3, 1282), (19.45, 1290)] + hops[1:] + [(27.0, 1505)], F, 0.08)
    hop_times = np.array([h[0] for h in hops])

    # --- play 3: the Hail Mary ---
    add(HOME, [(29.5, 760), (32.5, 760), (33.2, 640), (33.8, 690), (34.5, 492), (35.0, 520), (36.2, 120),
               (36.6, 150), (37.0, 70), (40, 70)], 9)                                                # QB
    add(AWAY, [(29.5, 820), (32.5, 820), (34.0, 650), (35.5, 400), (36.8, 140), (37.3, 110), (40, 110)])
    add(HOME, [(29.5, 2140), (32.5, 2140), (36.0, 2290), (36.6, 2270), (40.0, 2400), (42.6, 2445),
               (43.0, 2470), (50, 2470)], 9)                                                         # receiver
    add(AWAY, [(29.5, 2200), (32.5, 2200), (37.0, 2330), (41.5, 2410), (42.6, 2425), (43.5, 2350),
               (45.0, 2350)])
    ball3 = track([(32.5, 760), (37.0, 72), (37.15, 80), (38.0, 491), (38.9, 892), (40.0, 1311), (41.0, 1660),
                   (41.9, 2033), (42.6, 2445), (43.0, 2470), (50.0, 2470)], F, 0.12)
    TD = 42.6

    def ball_draw(buf, x, t, high):
        spin = 0.75 + 0.25 * np.cos(2 * np.pi * 7 * t)
        size = 6 + 4 * (1 - high)
        buf += light(BALL, (0.85 + 0.15 * (1 - high)) * spin * np.exp(-((pdp - x) / size) ** 2))
        buf += light(WARM, 0.5 * max(0, np.cos(2 * np.pi * 7 * t)) ** 8 * np.exp(-((pdp - x) / 3) ** 2))

    def height(x):
        """How 'high' the ball is: the porch sides climb, the Porch Front is the top of the arc."""
        return float(np.clip(np.interp(x, [892, 1311, 1660, 2033], [0, 1, 1, 0]), 0, 1))

    for f in range(F):
        t = f * DT
        buf = np.zeros((n, 3))
        excite = keys(t, [(0, 0.1), (3, 0.1), (19.2, 0.2), (19.6, 0.1), (23.0, 0.25), (24.5, 0.1), (42.6, 0.1),
                          (43.0, 0.3), (55, 0.15), (60, 0)])
        crowd = (0.5 + 0.5 * crowd_f(t)) * excite
        buf += light(BROWN, keys(t, [(0, 0), (2, 0.12), (56, 0.12), (60, 0)]) + 0.6 * crowd)
        for col, tr, size, ta, tb in players:
            x = tr[f]
            if np.isnan(x):
                continue
            fade = smoothstep(ta, ta + 0.6, t) * (1 - smoothstep(tb - 0.8, tb, t))
            buf += light(col, 0.85 * fade * np.exp(-((pdp - x) / size) ** 2))
        # balls and their shadow on the wing fronts
        for tr, t0, t1 in ((ball1, 5.95, 11.4), (ball2, 19.45, 27), (ball3, 37.1, 42.6)):
            x = tr[f]
            if np.isnan(x) or not (t0 <= t <= t1 + 0.01):
                continue
            hi = height(x)
            ball_draw(buf, x, t, hi)
            for k in range(1, 8):                                   # motion blur behind the ball
                xk = tr[max(0, f - k)]
                if not np.isnan(xk) and t - k * DT >= t0:
                    buf += light(BALL, 0.45 * (1 - k / 8) * np.exp(-((pdp - xk) / 5) ** 2))
            if tr is not ball2:
                xa = X[int(np.argmin(np.abs(pdp - tr[nframes(t0)])))]
                xb = X[int(np.argmin(np.abs(pdp - min(tr[nframes(t1) - 1], 2511))))]
                xs = xa + (xb - xa) * (t - t0) / (t1 - t0)
                buf += light(BROWN, 0.6 * hi * np.exp(-((X - xs) / 18) ** 2) * wingf)
        # play 1: the groan, a sad trombone down the Right wing
        if 11.0 < t < 14.0:
            for k in range(3):
                u = t - 11.3 - 0.7 * k
                if 0 < u < 0.9:
                    buf += light(AWAY, 0.3 * np.sin(np.pi * u / 0.9) * (pdp > 2036) * (1 - 0.25 * k))
        # play 2: the pile-up jiggles and sparks; each fumble bounce flashes where it lands
        if 19.2 < t < 21.6:
            j = rng.normal(0, 4, 1)[0]
            buf += light(WARM, 0.45 * np.exp(-((pdp - 1290 - j) / 14) ** 2) * (0.5 + 0.5 * np.sin(40 * t)))
        for th in hop_times[1:]:
            u = t - th
            if 0 <= u < 0.25:
                buf += light(WARM, 0.7 * np.exp(-u / 0.07) * np.exp(-((pdp - ball2[f]) / 9) ** 2))
        if 22.9 < t < 25:
            buf += light(HOME, 0.5 * np.exp(-(t - 22.9) / 0.6) * ((pdp > 492) & (pdp < 1311)))
        # play 3: TOUCHDOWN
        u = t - TD
        if u >= 0:
            catch = np.exp(-u / 0.25)
            buf += light(WARM, 0.9 * catch * np.exp(-((pdp - 2450) / 20) ** 2))
            ez = (pdp > 2380)
            for k in range(3):
                uk = u - 0.4 - 0.75 * k
                if 0 < uk < 0.7:
                    buf += light(GOLD, 0.85 * np.exp(-uk / 0.25) * ez)
            # the wave: every pixel is a fan who stands up when the wave reaches them, then sits slowly
            for w0, direction in ((2.8, -1), (8.2, 1)):
                front = (u - w0) * 620
                pos = (G.length - pdp) if direction < 0 else pdp
                lag = front - pos
                stand = np.where(lag > 0, np.exp(-lag / 320), np.exp(-(lag / 35) ** 2))
                shirt = np.where(((pdp // 32) % 2 == 0)[:, None], HOME, GOLD)
                if -1 < u - w0 < 6:
                    buf += light(1.0, stand * (0.8 if direction < 0 else 0.6)) * shirt
            buf += light(HOME, 0.2 * smoothstep(13, 15, u) * keys(t, [(55, 1), (60, 0)]))
        out[f][G.path] = buf
    return out
