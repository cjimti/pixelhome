"""The Pour: A ladle tips at the back of Side and molten steel runs the whole roofline as a runner.
The metal is coloured by its temperature (blackbody): white at the spout, orange down the run, dull
red at the leading edge, which is the oldest and coolest metal. It pools at each corner before
spilling on. When the ladle stops, the runner sets in place; a crust forms with glowing cracks and
the corners (more mass) stay hot longest. A water quench runs back from the free right end in a
burst of steam."""
import numpy as np
from pixelhome.fx import DT, hexc, light, smoothstep, keys, smooth_noise, Flicker, colormap, nframes

CODE = 'LB01'
TITLE = 'The Pour'
KIND = 'show'
DESCRIPTION = ('A ladle tips at the back of the house and molten steel runs the whole roofline, white at the '
               'spout, pooling at every corner, then cooling through orange to dull red before a steam quench.')

STEAM = hexc('#aebccc')

# blackbody-ish ramp, 0 = cold, 1 = white hot (PWM values)
HEAT = colormap([(0.0, (0, 0, 0)), (0.12, (0.035, 0.0, 0.0)), (0.25, (0.16, 0.006, 0.0)),
                 (0.4, (0.5, 0.035, 0.0)), (0.55, (0.95, 0.12, 0.004)), (0.7, (1.0, 0.27, 0.02)),
                 (0.83, (1.0, 0.48, 0.09)), (0.93, (1.0, 0.7, 0.3)), (1.0, (1.0, 0.86, 0.58))])


def render(G, seed=21):
    rng = np.random.default_rng(seed)
    D = 72.0
    F = nframes(D)
    out = np.zeros((F, G.N, 3))
    s = G.pd[G.path]
    L = G.length
    corners = np.array([(s[a] + s[a + 1]) / 2 for a in (80, 178, 260, 331, 380)])

    T_TIP, T_STOP, T_QUENCH = 4.5, 38.0, 53.0
    # integrate the flow front: slows as it goes, pauses and pools at each corner
    front = np.zeros(F)
    x, hold, passed = 0.0, 0.0, set()
    pool_t = {}
    for f in range(F):
        t = f * DT
        if t > T_TIP and x < L + 40:
            if hold > 0:
                hold -= DT
            else:
                v = 150 * (1 - 0.45 * min(1, x / L)) * smoothstep(T_TIP, T_TIP + 1.0, t)
                x += v * DT
                for k, c in enumerate(corners):
                    if k not in passed and x >= c:
                        passed.add(k)
                        pool_t[k] = t
                        hold = 0.9
                        x = c
        front[f] = x
    tf = np.arange(F) * DT
    t_arr = np.interp(s, front, tf, left=0, right=1e9)          # arrival of the front at each pixel
    t_arr[s < 1] = T_TIP

    # corners have more mass: they cool slower
    near_c = np.max(np.exp(-((s[:, None] - corners[None]) / 28) ** 2), axis=1)
    tau = 12.0 * (1 + 1.8 * near_c)
    grid = np.arange(-4000, L + 200, 2.0)
    crust_g = smooth_noise(rng, grid, 26, octaves=3)
    ripple_g = smooth_noise(rng, grid, 45, octaves=2)
    shimmer = Flicker(rng, G.N, 1.5, 6.0)
    glint = Flicker(rng, G.N, 4.0, 11.0)
    spatter_t = np.sort(rng.uniform(T_TIP, T_STOP, 70))
    spatter_x = rng.uniform(0, 40, 70)
    q_steam = Flicker(rng, G.N, 0.6, 2.5)
    T_at_quench = None

    for f in range(F):
        t = f * DT
        buf = np.zeros((G.N, 3))
        wet = t >= t_arr
        # head of the flow: smooth meniscus with sub-pixel position
        edge = smoothstep(front[f] + 6, front[f] - 6, s) * (t > T_TIP)

        age_pour = 0.75 * (t_arr - T_TIP)                         # the leading metal is the oldest
        set_t = max(0.0, t - T_STOP)
        age = age_pour + (t - t_arr) * 0.08 + set_t * 0.55
        T = np.exp(-age / tau) * edge
        T *= 1 + 0.03 * shimmer(t) * (t < T_STOP)
        # while pouring, fresh metal keeps the near end white hot
        feed = keys(t, [(T_TIP, 0), (T_TIP + 1.5, 1), (T_STOP - 1, 1), (T_STOP + 6, 0)])
        T = np.maximum(T, feed * np.exp(-s / 160) * edge)

        # corner pools swell while the front waits
        for k, tp in pool_t.items():
            u = t - tp
            if u > 0:
                bulge = np.exp(-((s - corners[k]) / 14) ** 2) * 0.12 * np.exp(-u / 3)
                T = T + bulge * edge

        # crust: forms as the metal cools, cracks stay hot
        # the surface flows with the metal until the pour stops, then it is frozen in place
        tt = min(t, T_STOP + 4.0)
        coast = tt - T_STOP
        tt = tt if coast <= 0 else T_STOP + coast - coast ** 2 / 8.0   # slows to a stop over 4 s
        off = 110 * (tt - T_TIP) * (t > T_TIP)
        crust_n = np.interp(s - off, grid, crust_g)
        rip = np.interp(s - off, grid, ripple_g)
        T = T * (1 + 0.16 * rip * feed)
        crust_amt = smoothstep(0.62, 0.38, T) * edge
        crack = np.exp(-(crust_n / 0.06) ** 2)
        plate = 1 - crust_amt * (1 - (0.22 + 0.78 * crack))
        Tc = T * (0.55 + 0.45 * plate) * (0.85 + 0.15 * plate)

        # quench from the free right end, back to the ladle
        if t >= T_QUENCH:
            if T_at_quench is None:
                T_at_quench = Tc.copy()
            tq = T_QUENCH + (L - s) / 200.0
            u = np.clip(t - tq, 0, None)
            hit = t >= tq
            Tc = np.where(hit, Tc * np.exp(-u / 0.7), Tc)
            steam = np.where(hit, (0.25 + 1.6 * T_at_quench) * np.exp(-u / 1.4) * smoothstep(0, 0.15, u), 0)
            steam *= 0.75 + 0.25 * q_steam(t)
            buf += light(STEAM, np.clip(steam, 0, 0.7))
        buf += HEAT(np.clip(Tc, 0, 1))

        # head glints where the crust breaks as the front pushes on
        if t > T_TIP:
            head = np.exp(-((s - front[f] + 8) / 9) ** 2) * (front[f] < L)
            buf += light(HEAT(np.array([0.9]))[0], 0.45 * head * np.clip(glint(t), 0, 1))

        # the ladle: heats, then pours with spatter at the spout
        lad = keys(t, [(0, 0), (3.5, 0.6), (T_TIP, 0.85), (T_STOP, 0.85), (T_STOP + 2.5, 0)])
        if lad > 0:
            buf += HEAT(np.clip(lad * np.exp(-s / 22), 0, 1))
        for ts, xs in zip(spatter_t, spatter_x):
            if ts <= t < ts + 0.35:
                buf += light(HEAT(np.array([1.0]))[0], 0.8 * np.exp(-((s - xs - 60 * (t - ts)) / 5) ** 2)
                             * (1 - (t - ts) / 0.35))

        # last few embers in the cracks, then dark
        if t > 66:
            buf *= 1 - smoothstep(67, 71.8, t)
        out[f][G.path] = buf
    return out
