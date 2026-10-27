"""General Order No. 3: The news arrives late. A single lantern rides in from the free back end of
the Side run, slowing for every corner; each pixel it passes wakes from a cold, dim wait to warm
light. On the porch it stops and reads the order (three slow swells), then rides on and out the
far free end. The news echoes back along the whole roof in red, white and blue, and settles gold."""
import numpy as np
from pixelhome.fx import DT, hexc, perc, light, smoothstep, keys, lerp, Flicker, nframes

CODE = 'JT01'
TITLE = 'General Order No. 3'
KIND = 'show'
DESCRIPTION = ('The news arrives late: a lantern rides in from the back of the house, waking every pixel '
               'it passes. It stops on the porch to read the order, rides out the far end, and the news echoes back.')

WAIT = hexc('#1a2a6a')      # cold indigo of the long wait
LANTERN = hexc('#fff1d0')
GOLD = hexc('#ffb040')
ROSE = hexc('#ff6a3a')
RED = hexc('#e0182a')
BLUE = hexc('#2a4cff')
WHITE = hexc('#fff4e8')


def ride(G, s0, s1, t0, v0, corners):
    """Times at which a rider moving from s0 to s1 (path distance) passes each s, slowing near corners
    and easing in/out at the ends. Returns (s grid, t grid)."""
    s = np.linspace(s0, s1, 4000)
    v = v0 * np.ones_like(s)
    for c in corners:
        v *= 1 - 0.55 * np.exp(-((s - c) / 45) ** 2)
    ease = np.minimum(np.abs(s - s0), np.abs(s - s1))
    v *= 0.25 + 0.75 * smoothstep(0, 140, ease)
    dt = np.diff(s) / (0.5 * (v[1:] + v[:-1]))
    return s, t0 + np.concatenate([[0], np.cumsum(dt)])


def render(G, seed=1):
    rng = np.random.default_rng(seed)
    D = 82.0
    out = np.zeros((nframes(D), G.N, 3))
    pdp = G.pd[G.path]
    zp = G.pos[G.path, 2]
    L = G.length
    segs = G.path_segments()
    corners = [pdp[max(p.max(), q.min())] for (_, p), (_, q) in zip(segs[:-1], segs[1:])]
    pf = G.pi[G.seg['Porch Front']]
    centre = pdp[pf].mean()
    on_pf = np.zeros(G.N, bool)
    on_pf[pf] = True
    pf_u = np.abs(pdp - centre) / (pdp[pf].max() - centre)

    # first leg: back free end -> porch centre; second leg: porch centre -> out past the right free end
    sA, tA = ride(G, -60, centre, 6.0, 95, corners)
    READ0, READ1 = tA[-1], tA[-1] + 9.0
    sB, tB = ride(G, centre, L + 90, READ1, 105, corners)
    EXIT = tB[-1]
    s_all, t_all = np.concatenate([sA, sB[1:]]), np.concatenate([tA, tB[1:]])
    t_wake = np.interp(pdp, s_all, t_all)
    t_wake[on_pf] = np.minimum(t_wake[on_pf], READ0 + 2.5 + 2.6 * pf_u[on_pf])   # the reading wakes the porch

    def rider(t):
        if t <= t_all[0] or t >= t_all[-1]:
            return None
        if READ0 <= t <= READ1:
            return centre
        return np.interp(t, t_all, s_all)

    shimmer = Flicker(rng, G.N, 0.4, 1.6)
    wait_breath = Flicker(rng, G.N, 0.04, 0.15)
    sparkle = Flicker(rng, G.N, 2.0, 5.0)
    ECHO = EXIT + 1.5
    echo_v = 210.0

    for f in range(len(out)):
        t = f * DT
        buf = np.zeros((G.N, 3))
        master = keys(t, [(0, 0), (2.5, 1), (D - 3, 1), (D, 0)])

        # the long wait: dim, cold, almost still
        tau = t - t_wake
        woke = smoothstep(-0.15, 0.25, tau)
        wI = 0.15 * (1 + 0.35 * wait_breath(t)) * (1 - woke)
        buf += light(WAIT, wI)

        # waking: a white bloom that settles to warm gold, then a living shimmer
        tp = np.clip(tau, 0, None)
        bloom = np.exp(-tp / 0.7) * woke
        settle = woke * (0.38 + 0.06 * shimmer(t) * smoothstep(1, 4, tp))
        col = lerp(GOLD, ROSE, (0.5 + 0.5 * np.sin(pdp / 90 + 0.3 * t))[:, None] * 0.35)
        warm = settle * keys(t, [(ECHO, 1), (ECHO + 3, 0.75), (D - 9, 0.75), (D - 5, 1.0)])
        buf += light(col, warm)
        buf += light(WHITE, 0.9 * bloom)

        # the lantern, with a gallop in its glow
        s = rider(t)
        if s is not None:
            reading = READ0 <= t <= READ1
            gallop = 0.88 + 0.12 * np.sin(2 * np.pi * 2.3 * t) ** 8 if not reading else 1.0
            d = pdp - s
            head = np.exp(-(d / 9) ** 2) * gallop
            road = 0.35 * np.exp(-(np.clip(d, 0, None) / 60) ** 2) * (d > 0)   # light thrown ahead
            buf += light(LANTERN, np.clip(head + road * 0.5, 0, 1.1))

        # the reading: three slow swells rolling out along the porch front
        if READ0 < t < READ1 + 1:
            for k in range(3):
                tr = t - (READ0 + 0.8 + 2.6 * k)
                if -0.5 < tr < 3.0:
                    ring = np.exp(-((np.abs(pdp - centre) - 70 * tr) / 22) ** 2) * np.exp(-tr / 1.6)
                    buf[on_pf] += light(LANTERN, 0.8 * ring[on_pf] * smoothstep(-0.5, 0, tr))

        # the echo: the news comes back along the whole roof in red, white and blue
        if t > ECHO:
            te = t - ECHO
            front = L - echo_v * te
            behind = pdp - front
            arrived = smoothstep(-30, 30, behind)
            # depth paints the flag onto the house: red wing fronts, a white horizon on the runs that
            # go back, the blue field on the porch front, with the horizon line breathing
            horizon = -360 + 40 * np.sin(0.6 * te) + 0.08 * (pdp - centre) * np.sin(0.4 * te)
            zz = zp - horizon
            flag = np.where((zz > 30)[:, None], RED, np.where((zz < -30)[:, None], BLUE, WHITE))
            glow = arrived * keys(t, [(ECHO, 0), (ECHO + 2, 0.75), (D - 10, 0.75), (D - 5, 0)])
            glow = glow * (0.75 + 0.25 * np.clip(sparkle(t), 0, 1))
            buf = buf * (1 - 0.6 * glow[:, None]) + light(flag, 0.8 * glow)
            buf += light(WHITE, 0.9 * np.exp(-(behind / 14) ** 2) * (te < L / echo_v + 1))

        out[f][G.path] = buf * perc(master)
    return out
