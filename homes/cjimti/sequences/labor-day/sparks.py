"""Sparks: A welder works the roofline and the sparks obey real ballistics.

Gravity points toward the street (+z), which is "down" from the street: the porch front looks higher
than the wing fronts. Sparks leave the arc in free flight (drag, gravity, cooling from white to
dull red), arc up behind the house and fall back. Sparks that land on the roofline stick to it and
become rolling particles: they slide down the runs that point at the street (Side, Porch Right,
Porch Left), lose speed in every corner, skitter along the level wing fronts, and roll partway up
the runs that point away from the street before sliding back. The arc leaves a weld bead that glows
and cools behind it."""
import numpy as np
from pixelhome.fx import DT, hexc, light, keys, lerp, colormap, nframes

CODE = 'LB02'
TITLE = 'Sparks'
KIND = 'show'
DESCRIPTION = ('A welder works the porch and the side of the house. Sparks arc up, fall toward the street, land on '
               'the roof and roll down the runs, bounce through the corners and skitter out along the wings.')

ARC = hexc('#dde6ff')
ARC_SPILL = hexc('#5a66ff')
HEAT = colormap([(0.0, (0, 0, 0)), (0.12, (0.05, 0.0, 0.0)), (0.25, (0.2, 0.01, 0.0)),
                 (0.4, (0.55, 0.04, 0.0)), (0.55, (0.95, 0.13, 0.004)), (0.7, (1.0, 0.28, 0.02)),
                 (0.83, (1.0, 0.5, 0.1)), (0.93, (1.0, 0.72, 0.32)), (1.0, (1.0, 0.88, 0.62))])

G_FREE = 620.0      # gravity in free flight, toward +z
G_ROLL = 420.0      # along a run that points at the street
MU = 55.0           # rolling friction (deceleration)


def render(G, seed=22):
    rng = np.random.default_rng(seed)
    D = 62.0
    F = nframes(D)
    out = np.zeros((F, G.N, 3))
    path = G.path
    P = G.pos[path]
    s_pix = G.pd[path]
    L = G.length
    X, Z = P[:, 0], P[:, 2]
    corners = np.array([(s_pix[a] + s_pix[a + 1]) / 2 for a in (80, 178, 260, 331, 380)])
    # z component of the path direction, per point along the path (+1 = running toward the street)
    tz_pix = np.gradient(Z) / np.maximum(np.gradient(s_pix), 1e-6)

    def tz_at(s):
        return np.interp(s, s_pix, tz_pix)

    def pos_at(s):
        return np.stack([np.interp(s, s_pix, X), np.interp(s, s_pix, Z)], -1)

    # runs that can catch a spark: (s_start, s_end) of each straight run
    runs = [(s_pix[a], s_pix[b]) for a, b in ((0, 80), (81, 178), (179, 260), (261, 331), (332, 380), (381, 500))]

    # where the arc is, over time: (start, end, s0, s1, pulsed)
    acts = [(2.5, 19.5, s_pix[266], s_pix[327], False),
            (22.5, 38.0, s_pix[4], s_pix[34], False)]
    tacks = [(41.0, 52.5, s_pix[262]), (41.6, 52.5, s_pix[330])]

    def arcs(t):
        """[(s, strength)] arcs burning at time t."""
        res = []
        for a, b, s0, s1, _ in acts:
            if a <= t < b:
                u = (t - a) / (b - a)
                res.append((lerp(s0, s1, u), 1.0))
        for a, b, s0 in tacks:
            if a <= t < b:
                ph = (t - a) % 1.7
                res.append((s0, 1.0 if ph < 1.15 else 0.0))
        return res

    # bead: when the moving arc passed each point
    t_pass = np.full(G.N, np.inf)
    for a, b, s0, s1, _ in acts:
        m = (s_pix >= s0) & (s_pix <= s1)
        t_pass[m] = a + (s_pix[m] - s0) / (s1 - s0) * (b - a)

    M = 2600
    mode = np.zeros(M, int)                 # 0 unborn, 1 flying, 2 rolling, 3 gone
    x = np.zeros(M); z = np.zeros(M); vx = np.zeros(M); vz = np.zeros(M)
    s = np.zeros(M); v = np.zeros(M)
    born = np.zeros(M); tau = rng.uniform(0.7, 1.9, M)
    nxt = 0
    glow = np.zeros(G.N)
    spill_lp = 0.0

    for f in range(F):
        t = f * DT
        buf = np.zeros((G.N, 3))
        live_arcs = [(sa, k) for sa, k in arcs(t) if k > 0]

        # emit
        for sa, _ in live_arcs:
            n = rng.poisson(30 * DT * (1.6 if t > 41 else 1.0))
            n = min(n, M - nxt)
            if n <= 0:
                continue
            k = slice(nxt, nxt + n)
            p = pos_at(np.array([sa]))[0]
            phi = np.clip(rng.normal(0, 0.85, n), -1.5, 1.5)
            sp = rng.uniform(140, 430, n)
            x[k], z[k] = p[0], p[1]
            vx[k], vz[k] = sp * np.sin(phi), -sp * np.cos(phi)
            born[k], mode[k] = t, 1
            nxt += n

        age = t - born
        T = np.where(mode > 0, np.exp(-age / tau), 0)
        mode[(mode > 0) & (T < 0.06)] = 3

        # free flight
        fl = np.nonzero(mode == 1)[0]
        if len(fl):
            z_old, x_old = z[fl].copy(), x[fl].copy()
            vx[fl] *= 1 - 1.3 * DT
            vz[fl] = vz[fl] * (1 - 1.3 * DT) + G_FREE * DT
            x[fl] += vx[fl] * DT
            z[fl] += vz[fl] * DT
            caught = np.zeros(len(fl), bool)
            roll_s = np.zeros(len(fl)); roll_v = np.zeros(len(fl))
            for s0, s1 in runs:
                a, b = pos_at(np.array([s0, s1]))
                if abs(a[0] - b[0]) < 1:            # runs along z: catch when within reach in x
                    lo, hi = min(a[1], b[1]), max(a[1], b[1])
                    hit = (np.abs(x[fl] - a[0]) < 14) & (z[fl] > lo) & (z[fl] < hi) & (vz[fl] > 0)
                    ss = s0 + (z[fl] - a[1]) * np.sign(b[1] - a[1])
                    vv = vz[fl] * np.sign(b[1] - a[1]) * 0.7
                else:                               # runs along x: catch when crossing the line
                    lo, hi = min(a[0], b[0]), max(a[0], b[0])
                    hit = ((z_old - a[1]) * (z[fl] - a[1]) <= 0) & (x[fl] > lo) & (x[fl] < hi) & (vz[fl] > 0)
                    ss = s0 + (x[fl] - a[0]) * np.sign(b[0] - a[0])
                    vv = vx[fl] * np.sign(b[0] - a[0]) * 0.6 + rng.normal(0, 60, len(fl))
                hit &= ~caught & (age[fl] > 0.08) & (rng.random(len(fl)) < 0.75)
                caught |= hit
                roll_s[hit], roll_v[hit] = ss[hit], vv[hit]
            idx = fl[caught]
            mode[idx], s[idx], v[idx] = 2, roll_s[caught], roll_v[caught]
            tau[idx] *= 1.25                        # resting on steel, they last a little longer
            far = fl[(np.abs(x[fl]) > 1100) | (z[fl] > 300)]
            mode[far] = 3

        # rolling along the roofline
        rl = np.nonzero(mode == 2)[0]
        if len(rl):
            s_old = s[rl].copy()
            acc = G_ROLL * tz_at(s[rl]) - MU * np.sign(v[rl]) - 0.5 * v[rl]
            v_new = v[rl] + acc * DT
            stop = (np.sign(v_new) != np.sign(v[rl])) & (np.abs(tz_at(s[rl])) < 0.5)
            v_new[stop] = 0
            v[rl] = v_new
            s[rl] += v[rl] * DT
            for c in corners:                       # a corner takes energy out
                crossed = (s_old - c) * (s[rl] - c) < 0
                v[rl[crossed]] *= rng.uniform(0.45, 0.7, crossed.sum())
            off = rl[(s[rl] < 0) | (s[rl] > L)]
            mode[off] = 3

        # draw sparks into an after-glow buffer (short streaks)
        cur = np.zeros(G.N)
        colsum = np.zeros((G.N, 3))
        fl = np.nonzero(mode == 1)[0]
        if len(fl):
            d2 = (X[None] - x[fl, None]) ** 2 + (Z[None] - z[fl, None]) ** 2
            w = np.exp(-d2 / 11.0 ** 2) * T[fl, None]
            cur += w.sum(0)
            colsum += w.T @ HEAT(T[fl])
        rl = np.nonzero(mode == 2)[0]
        if len(rl):
            w = np.exp(-((s_pix[None] - s[rl, None]) / 5.0) ** 2) * T[rl, None]
            cur += w.sum(0)
            colsum += w.T @ HEAT(T[rl] * 0.95)
        hue = colsum / np.maximum(cur, 1e-6)[:, None]
        glow = np.maximum(glow * 0.72, np.clip(cur, 0, 1.2))
        buf += hue * glow[:, None] * 0.9 + HEAT(np.clip(glow, 0, 1) * 0.6) * 0.25 * (glow[:, None] > 0.02)

        # the bead cools behind the arc
        ub = t - t_pass
        bead = np.where(ub > 0, 0.82 * np.exp(-ub / 7.0), 0) + np.where(ub > 0, 0.22 * np.exp(-ub / 40.0), 0)
        bead *= keys(t, [(0, 1), (56, 1), (61.5, 0)])
        buf += HEAT(np.clip(bead, 0, 1))
        for a, b, s0 in tacks:                      # tack welds glow at the porch corners
            if t > a:
                u = t - a
                hot = 0.75 * min(1, u / 2) * np.exp(-max(0, t - b) / 5.0) * keys(t, [(56, 1), (61.5, 0)])
                buf += HEAT(np.clip(hot * np.exp(-((s_pix - s0) / 6) ** 2), 0, 1))

        # the arc: small, blue-white, never steady
        spill = 0.0
        for sa, k in live_arcs:
            flick = rng.uniform(0.55, 1.0) if rng.random() > 0.05 else 0.15
            buf += light(ARC, flick * np.exp(-((s_pix - sa) / 3.5) ** 2))
            p = pos_at(np.array([sa]))[0]
            dd = np.hypot(X - p[0], Z - p[1])
            spill_lp = 0.8 * spill_lp + 0.2 * flick
            buf += light(ARC_SPILL, 0.2 * spill_lp * np.exp(-dd / 110))
            spill = 1
        if not spill:
            spill_lp = 0.0
        out[f][path] = np.clip(buf, 0, 1)
    return out
