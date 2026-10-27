"""Golden Spike: Two railroad crews lay track from the two free ends toward the porch.

Each crew slides a rail into place, then drives its spikes. Every hammer blow rings the rail: a
real 1-D wave equation runs along the laid track, so each clang travels back down the line,
reflects off the railhead and the free end and dies away. The two crews alternate their blows and
speed up as they race. Where they meet on the Porch Front the rails join, a golden spike is driven
with three slow blows whose ring now runs the whole line, the telegraph carries DONE out both ends,
and the first train runs the length of the house with its headlamp, puffs of steam and a red
marker on the last car."""
import numpy as np
from pixelhome.fx import DT, hexc, light, smoothstep, keys, lerp, nframes

CODE = 'LB06'
TITLE = 'Golden Spike'
KIND = 'show'
DESCRIPTION = ('Two crews lay track from both ends of the house and every hammer blow rings down the rails. '
               'They meet on the porch, drive the golden spike, and the first train runs the line.')

STEEL = hexc('#9db3cc')
TIE = hexc('#8a4c22')
LANTERN = hexc('#ffa040')
CLANG = hexc('#fff0d0')
GOLD = hexc('#ffb420')
HEAD = hexc('#fff2d6')
CAB = hexc('#ff6a18')
SMOKE = hexc('#a8b0bc')
MARKER = hexc('#ff1808')
CAR = hexc('#5a4030')


def render(G, seed=26):
    rng = np.random.default_rng(seed)
    s = G.pd[G.path]
    L = G.length
    meet = s[296]

    # tempo: beat length per section, quickening as the crews race
    def beat(k):
        return float(np.interp(k, [0, 6, 12], [2.8, 2.2, 1.6]))

    starts = [2.0]
    for k in range(12):
        starts.append(starts[-1] + beat(k))
    T_MEET = starts[-1]
    nl, nr = 12, 9
    crews = []
    for side, n, s0, s1, off in ((+1, nl, 0.0, meet, 0.0), (-1, nr, L, meet, 0.5)):
        secs = []
        for j in range(n):
            k = j + (12 - n)                     # the shorter crew starts later, ends together
            t0 = starts[k] + off * beat(k) * 0.25
            a = lerp(s0, s1, j / n)
            b = lerp(s0, s1, (j + 1) / n)
            secs.append((t0, beat(k), a, b))
        crews.append((side, s0, secs))

    def railhead(side, s0, secs, t):
        """How far this crew's rail reaches, and the section being laid."""
        h = s0
        for t0, bt, a, b in secs:
            if t >= t0:
                h = lerp(a, b, smoothstep(0, 0.45 * bt / 2.4, t - t0))
        return h

    strikes = []                                 # (t, s, strength, gold)
    for side, s0, secs in crews:
        for t0, bt, a, b in secs:
            for q in range(4):
                strikes.append((t0 + bt * (0.3 + 0.17 * q), lerp(a, b, 0.2 + 0.2 * q), 0.6, False))
    T_GOLD = T_MEET + 2.5
    for q, dt in enumerate((0.0, 2.2, 4.4)):
        strikes.append((T_GOLD + dt, meet, 1.3 + 0.5 * q, True))
    strikes.sort()
    T_WIRE = T_GOLD + 6.0
    T_TRAIN = T_WIRE + 2.5
    D = T_TRAIN + 13.5
    F = nframes(D)
    out = np.zeros((F, G.N, 3))

    # wave equation on a uniform grid along the path
    dx = 4.0
    xg = np.arange(0, L + dx, dx)
    ng = len(xg)
    u = np.zeros(ng); up = np.zeros(ng)
    c, sub = 520.0, 4
    h = DT / sub
    r2 = (c * h / dx) ** 2
    ties = 0.5 + 0.5 * np.cos(2 * np.pi * s / 22.0)
    ties = ties ** 6
    si = 0
    gold_mode = 0.0
    puffs = []

    for f in range(F):
        t = f * DT
        buf = np.zeros((G.N, 3))
        hl = railhead(*crews[0], t)
        hr = railhead(*crews[1], t)
        joined = t >= T_MEET
        laid_g = (xg <= hl + 1) | (xg >= hr - 1) | joined
        laid = (s <= hl) | (s >= hr) | joined
        edge = smoothstep(hl + 4, hl - 4, s) + smoothstep(hr - 4, hr + 4, s)
        edge = np.clip(edge, 0, 1) if not joined else np.ones(G.N)

        # hammer blows inject a pulse into the rail
        while si < len(strikes) and strikes[si][0] <= t:
            ts, xs, a, gold = strikes[si]
            u += a * np.exp(-((xg - xs) / 10) ** 2) * laid_g
            si += 1
        for _ in range(sub):
            lap = np.zeros(ng)
            lap[1:-1] = u[2:] - 2 * u[1:-1] + u[:-2]
            un = 2 * u - up + r2 * lap - 1.6 * h * (u - up) - (2 * np.pi * 1.2) ** 2 * h * h * u   # damped, held by the ties
            un[~laid_g] = 0                      # beyond the railhead there is no rail
            up, u = u, un
        ring = np.abs(np.interp(s, xg, u))

        if t > T_GOLD - 0.1:
            gold_mode = 1.0
        wave_col = lerp(STEEL, GOLD, gold_mode)
        train_lit = smoothstep(T_TRAIN, T_TRAIN + 3, t)
        base = 0.17 * edge * laid * (1 - 0.6 * train_lit)
        buf += light(STEEL, base) + light(TIE, 0.2 * edge * laid * ties * (1 - 0.6 * train_lit))
        buf += light(wave_col, np.clip(0.8 * ring, 0, 0.85) * edge * laid)

        # rail sections sliding in, crew lanterns at the railheads
        if not joined:
            for (side, s0, secs), hd in zip(crews, (hl, hr)):
                for t0, bt, a, b in secs:
                    w = t - t0
                    if 0 <= w < 0.6 * bt / 2.4:
                        lo, hi = min(a, hd), max(a, hd)
                        buf += light(STEEL, 0.4 * smoothstep(lo - 3, lo + 3, s) * smoothstep(hi + 3, hi - 3, s))
                buf += light(LANTERN, 0.45 * np.exp(-((s - hd + side * 10) / 7) ** 2))
        for ts, xs, a, gold in strikes:          # spark at each blow
            w = t - ts
            if 0 <= w < 0.5:
                buf += light(GOLD if gold else CLANG, (1.1 if gold else 0.85) * np.exp(-w / 0.09)
                             * np.exp(-((s - xs) / (4 + 10 * gold)) ** 2))

        # the golden spike itself
        if t > T_MEET:
            g = smoothstep(T_MEET, T_MEET + 2.0, t) * (1 - smoothstep(T_TRAIN + 2, T_TRAIN + 6, t))
            buf += light(GOLD, 0.7 * g * np.exp(-((s - meet) / 5) ** 2))
        # telegraph: DONE, out both ends
        w = t - T_WIRE
        if 0 <= w < 3.0:
            for d in (-1, 1):
                p = meet + d * 950 * w
                for k, dot in enumerate((0, 1, 2, 3)):   # D O N E: four pulses
                    q = p - d * 38 * k
                    buf += light(CLANG, 0.8 * np.exp(-((s - q) / (5 if k % 2 else 10)) ** 2))

        # the first train
        w = t - T_TRAIN
        if w > 0:
            x = min(w, 2.0) ** 2 * 65 + max(0.0, w - 2.0) * 260 - 60
            beam = np.where(s > x, np.exp(-(s - x) / 110), 0) * (x < L + 200)
            buf += light(HEAD, 0.95 * np.exp(-((s - x) / 5) ** 2) + 0.35 * beam)
            buf += light(CAB, 0.5 * np.exp(-((s - x + 16) / 6) ** 2))
            cars = (s < x - 26) & (s > x - 420)
            win = (0.5 + 0.5 * np.cos(2 * np.pi * (s - x) / 46)) ** 8
            buf += light(CAR, 0.18 * cars + 0.12 * cars * win)
            buf += light(MARKER, 0.75 * np.exp(-((s - (x - 424)) / 4) ** 2))
            if f % 18 == 0 and x < L:
                puffs.append((t, x - 8))
            for tp, xp in puffs:
                a = t - tp
                if a < 2.5:
                    buf += light(SMOKE, 0.35 * np.exp(-a / 0.8) * np.exp(-((s - xp) / (6 + 14 * a)) ** 2))
            buf += light(STEEL, 0.25 * train_lit * np.exp(-np.abs(s - x) / 300) * laid)
        buf *= 1 - smoothstep(D - 1.5, D, t)
        out[f][G.path] = np.clip(buf, 0, 1)
    return out
