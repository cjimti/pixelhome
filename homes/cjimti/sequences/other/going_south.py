"""Going South: The whole roofline is a dusk sky (rose in the west over the Side, deep blue in the
east over the Right wing) and geese fly over the house as dark silhouettes in true 3-D, blotting out
the sky wherever they pass above a run of the roof. A V of nine comes in from behind the house and
heads for the street; halfway over, the tired leader drops back and the next bird takes the point.
A late straggler follows alone, honking (each honk a faint ring spreading over the yard), gets lost
circling the porch, sets off the wrong way out past the Right wing's free end, thinks better of it
and comes back to wait. The flock wheels round, picks it up, and the V, now ten, heads south over
the street while the first star comes out."""
import numpy as np
from pixelhome.fx import DT, hexc, light, smoothstep, keys, lerp, nframes

CODE = 'OT26'
TITLE = 'Going South'
KIND = 'show'
DESCRIPTION = ('Geese cross a dusk sky over the house as silhouettes. The leader trades places; a lost '
               'straggler honks, circles the porch, flies off the wrong way, and the flock comes back for it.')

WEST = hexc('#ff8a6a')
MID = hexc('#a06aa0')
EAST = hexc('#2a3a90')
NIGHT = hexc('#10184a')
HONK = hexc('#ffe8c0')
STAR = hexc('#e8f0ff')


def spline(times, pts):
    """Open Catmull-Rom through pts at the given times; returns f(t) -> (x, z) and heading."""
    pts = np.asarray(pts, float)
    P = np.vstack([2 * pts[0] - pts[1], pts, 2 * pts[-1] - pts[-2]])
    times = np.asarray(times, float)

    def f(t):
        i = int(np.clip(np.searchsorted(times, t, side='right') - 1, 0, len(times) - 2))
        u = np.clip((t - times[i]) / (times[i + 1] - times[i]), 0, 1)
        p0, p1, p2, p3 = P[i], P[i + 1], P[i + 2], P[i + 3]
        return 0.5 * ((2 * p1) + (-p0 + p2) * u + (2 * p0 - 5 * p1 + 4 * p2 - p3) * u ** 2 +
                      (-p0 + 3 * p1 - 3 * p2 + p3) * u ** 3)
    return f


def render(G, seed=26):
    rng = np.random.default_rng(seed)
    D = 66.0
    F = nframes(D)
    out = np.zeros((F, G.N, 3))
    x, z = G.pos[:, 0], G.pos[:, 2]
    ux = (x - x.min()) / (x.max() - x.min())          # 0 west (Side) .. 1 east (Right free end)

    # the flock's lead point: first pass (behind -> street-left), then back round to fetch the straggler
    lead = spline([3, 9, 14, 19, 25, 31, 37, 42, 46.5, 51, 57, 64],
                  [(640, -1150), (380, -760), (60, -420), (-330, -40), (-800, 380), (-1300, 300),
                   (-1100, -400), (-500, -820), (-20, -560), (-60, -120), (-160, 400), (-260, 1300)])
    lost = spline([13, 18, 21, 22.5, 24.5, 26.5, 28, 29.5, 31, 33, 35.5, 38, 40.5, 43, 46.5],
                  [(1000, -1500), (560, -800), (150, -560), (-60, -572), (-196, -420), (-120, -250),
                   (60, -260), (152, -400), (40, -572), (-150, -470), (300, -196), (780, -192),
                   (640, -420), (180, -470), (-10, -560)])
    n_v = 9
    # V slots: index 0 at the point, then alternating arms
    slots = [(0, 0)] + [((k + 1) // 2, (-1) ** k) for k in range(1, 12)]
    order = list(range(n_v))                          # order[slot] = goose
    pos = np.array([lead(3.0) + np.array([s[0] * 60, s[0] * 50 * s[1]]) for s in slots[:n_v]], float)
    vel = np.zeros_like(pos)
    lp_pos, lp_vel = np.array(lost(13.0)), np.zeros(2)
    flap_ph = rng.uniform(0, 2 * np.pi, n_v + 1)
    flap_f = rng.uniform(2.3, 2.9, n_v + 1)
    honks = [16.0, 16.6, 22.4, 23.0, 26.5, 30.8, 31.3, 36.2, 39.0, 39.5, 41.0, 44.0, 44.4]
    flock_honks = [38.0, 42.5, 47.2, 47.5, 47.8]
    joined = False
    star_k = int(np.argmin(np.abs(G.pd - G.pd[G.seg['Porch Front']].mean() + 60)))

    prev_lead = np.array(lead(2.9))
    hn = np.array([-0.6, 0.8])
    for f in range(F):
        t = f * DT
        fr = out[f]
        dusk = keys(t, [(0, 0), (45, 0.5), (66, 1)])
        sky = lerp(lerp(WEST, MID, np.clip(ux * 2, 0, 1)[:, None]), EAST, np.clip(ux * 2 - 1, 0, 1)[:, None])
        sky = lerp(sky, NIGHT, 0.75 * dusk)
        sky_I = (0.36 - 0.14 * dusk) * (1 - 0.35 * ux * (1 - dusk))
        sky_I = sky_I * keys(t, [(0, 0), (2.5, 1)])

        # -- the flock: the lead point flies the path, each bird springs toward its V slot
        L = np.array(lead(t))
        hd = L - prev_lead
        prev_lead = L
        if np.linalg.norm(hd) > 1e-3:
            hn = hd / np.linalg.norm(hd)
        nn = np.array([-hn[1], hn[0]])
        if 12.5 < t and order[0] == 0:                # the tired leader drops to the back of an arm
            order = order[1:] + [order[0]]
        members = n_v + (1 if joined else 0)
        if not joined and t >= 46.5:
            joined = True
            order = order + [n_v]
            pos = np.vstack([pos, lp_pos])
            vel = np.vstack([vel, lp_vel])
            members = n_v + 1
        geese = []
        for s in range(members):
            g = order[s]
            back, side = slots[s]
            target = L - hn * back * 55 + nn * side * back * 48
            w = 2.2
            acc = w * w * (target - pos[g]) - 2 * w * vel[g]
            vel[g] += acc * DT
            pos[g] += vel[g] * DT
            geese.append((pos[g].copy(), vel[g].copy(), g))
        if not joined and t > 13:
            p = np.array(lost(t))
            lp_vel = (p - lp_pos) / DT
            lp_pos = p
            geese.append((lp_pos.copy(), lp_vel.copy(), n_v))

        # -- silhouettes: a body along the heading, wings across it that beat
        dark = np.zeros(G.N)
        if t > 2.5:
            for p, v, g in geese:
                sp = np.linalg.norm(v)
                h = v / sp if sp > 1 else hn
                n2 = np.array([-h[1], h[0]])
                rx, rz = x - p[0], z - p[1]
                along = rx * h[0] + rz * h[1]
                across = rx * n2[0] + rz * n2[1]
                beat = np.sin(2 * np.pi * flap_f[g] * t + flap_ph[g])
                span = 42 * (0.55 + 0.45 * np.abs(beat))
                body = np.exp(-(along / 20) ** 2 - (across / 10) ** 2)
                wings = np.exp(-((along + 5 * beat) / 10) ** 2 - (across / span) ** 4)
                dark = np.maximum(dark, np.maximum(body, 0.9 * wings))
        col = light(sky, sky_I * (1 - 0.92 * dark))

        # -- honks: a faint ring spreading out from the bird that called
        for th in honks:
            u = t - th
            if 0 <= u < 1.2 and not (joined and th > 46.5):
                p = lost(th)
                dd = np.hypot(x - p[0], z - p[1])
                col += light(HONK, 0.35 * np.exp(-((dd - 260 * u) / 16) ** 2) * np.exp(-u / 0.45))
        for th in flock_honks:
            u = t - th
            if 0 <= u < 1.2:
                p = lead(th)
                dd = np.hypot(x - p[0], z - p[1])
                col += light(HONK, 0.3 * np.exp(-((dd - 260 * u) / 16) ** 2) * np.exp(-u / 0.45))

        # -- the first star, over the porch
        st = smoothstep(53, 59, t) * (1 - smoothstep(64, 66, t))
        col[star_k] += STAR * (st * (0.55 + 0.05 * np.sin(3.1 * t))) ** 2.2
        fr[:] = col * keys(t, [(62.5, 1), (66, 0)])
    return out
