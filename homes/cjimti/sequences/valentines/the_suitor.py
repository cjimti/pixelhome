"""The Suitor: a nervous little light sneaks in from the free back end of the Side, trembling, in
footsteps, hesitating at every corner and peeking round the last one. She waits on the porch, set back
like a balcony. He offers a rose; she coyly slides away round the corner and down the Right wing, he
chases, she stops dead and he bounces off her (momentum and drag, simulated) all the way back to the
Porch Left, dizzy, while she giggles. Then she fetches the rose that flew out of his hands and sends a heartbeat down
the roof to him. He jumps for joy and runs to her, no trembling now."""
import numpy as np
from pixelhome.fx import DT, hexc, light, keys, smoothstep, lerp, heartbeat, Flicker, nframes

CODE = 'VD06'
TITLE = 'The Suitor'
KIND = 'show'
DESCRIPTION = ('A nervous suitor tiptoes round the house with a rose. She plays hard to get, he bounces off her '
               'and ends up dizzy halfway back, and then she sends him a heartbeat down the roof.')

ROSE = hexc('#ff2448')
GOLD = hexc('#ffa040')
WARM = hexc('#ffc890')
DEEP = hexc('#ff0010')
WINE = hexc('#a00008')
BLUSH = hexc('#ff5a50')


def steps(t0, a, b, size, dur):
    """Keyframes walking from a to b in footsteps (each eased, so it moves, settles, moves)."""
    n = max(1, int(round(abs(b - a) / size)))
    return [(t0 + k * dur, a + (b - a) * k / n) for k in range(n + 1)]


def render(G, seed=26):
    rng = np.random.default_rng(seed)
    D = 58.0
    F = nframes(D)
    out = np.zeros((F, G.N, 3))
    pdp = G.pd[G.path]
    L = G.length
    pf = G.seg['Porch Front']
    c = G.pd[pf[len(pf) // 2]]
    fl = Flicker(rng, G.N, 0.2, 0.8)

    # --- his path before the crash: footsteps, hesitations, a peek round the corner
    S = [(3.5, -25.0)] + steps(4.0, -10, 470, 30, 0.4)[1:]
    S += [(11.0, 470), (11.4, 452), (11.9, 452), (12.4, 488)]
    S += steps(12.7, 488, 872, 32, 0.33)[1:]
    S += [(17.0, 872), (17.35, 904), (17.75, 878), (18.3, 878), (18.6, 906), (18.9, 884), (19.4, 884)]
    S += steps(19.6, 884, 1290, 40, 0.3)[1:]
    S += [(24.6, 1290), (25.2, 1300)]                         # offers the rose (24.6 - 26)
    S += [(26.4, 1300), (27.8, 1620), (28.4, 1620), (30.2, 1960), (30.5, 1960)]
    # she: waits, slides coyly away, round the corner and down the Right wing, stops dead
    B = [(0, c), (25.6, c), (27.0, 1645), (28.0, 1645), (29.6, 1980), (30.0, 1990), (31.0, 2250)]
    BL = 2250.0
    t_run, t_crash = 30.5, 31.6
    # after the crash: launched backwards, drag brings him to a stop
    v0, drag = -1500.0, 1.3
    x_crash = BL - 16
    x_stop = x_crash + v0 / drag
    t_joy, t_dash = 42.0, 45.0
    meet = BL - 15
    rose_drop = 2410.0

    for f in range(F):
        t = f * DT
        buf = np.zeros((G.N, 3))
        master = keys(t, [(D - 4, 1), (D - 0.3, 0)])
        buf += light(WINE, keys(t, [(0, 0), (2, 0.035), (D - 5, 0.035)]) * (1 + 0.2 * fl(t)))

        # --- where he is
        nerves = 1.0
        if t < t_run:
            ps = keys(t, S)
        elif t < t_crash:
            ps = lerp(1960, x_crash, ((t - t_run) / (t_crash - t_run)) ** 1.6)
            nerves = 0.3
        elif t < t_dash:
            s = t - t_crash
            ps = x_crash + v0 / drag * (1 - np.exp(-drag * s))
            nerves = 0.0
            if t > t_joy:                                     # jumps for joy: a damped spring
                sj = t - t_joy
                ps += 38 * np.exp(-sj / 0.9) * np.abs(np.sin(2 * np.pi * 1.6 * sj))
        else:
            ps = lerp(x_stop, meet, smoothstep(t_dash, t_dash + 3.2, t))
            nerves = 0.0
        tremble = nerves * (1.6 * np.sin(2 * np.pi * 11 * t) + 1.0 * np.sin(2 * np.pi * 17.3 * t + 1))
        dizzy = (t_crash + 2.5 < t < t_joy) * 1.0
        ps += tremble + dizzy * 7 * np.sin(2 * np.pi * 2.2 * t)
        Is = keys(t, [(3.5, 0), (4.5, 0.75), (24.4, 0.75), (25, 0.95), (26.2, 0.75), (t_crash, 0.85),
                      (t_crash + 0.15, 1.0), (t_crash + 2, 0.6), (t_joy, 0.6), (t_joy + 0.2, 1.1),
                      (t_joy + 2, 0.85)])
        if dizzy:
            Is *= 0.8 + 0.2 * np.sin(2 * np.pi * 3.1 * t)
        col_s = lerp(GOLD, WARM, smoothstep(t_joy, t_joy + 0.5, t) * 0.6)
        buf += light(col_s, Is * np.exp(-((pdp - ps) / 8) ** 2)) + light(GOLD, 0.2 * Is * np.exp(-((pdp - ps) / 28) ** 2))
        if dizzy:                                             # little stars going round his head
            for k in range(3):
                a = 2 * np.pi * (1.3 * t + k / 3)
                sp = ps + 26 * np.cos(a)
                buf += light(WARM, 0.35 * (0.5 + 0.5 * np.sin(a)) * np.exp(-((pdp - sp) / 4) ** 2))

        # --- where she is
        pb = keys(t, B)
        sway = 10 * np.sin(2 * np.pi * t / 3.2) * (t < 25.6)
        if t_crash <= t < t_crash + 1.5:                       # knocked a little by the impact
            s = t - t_crash
            sway += 9 * np.exp(-s / 0.3) * np.sin(2 * np.pi * 5 * s)
        if 38.0 < t < 40.0:                                   # goes to pick up the rose
            pb = lerp(BL, rose_drop - 4, np.sin(np.pi * (t - 38.0) / 2.0))
        pb += sway
        giggle = 0.0
        if t_crash + 2.8 < t < t_crash + 5.6:                 # ha-ha-ha
            s = t - (t_crash + 2.8)
            giggle = 0.45 * np.abs(np.sin(2 * np.pi * 3.2 * s)) * np.exp(-s / 2)
        Ib = keys(t, [(0.5, 0), (2.5, 0.8), (38.8, 0.8), (39.3, 1.0), (D - 4, 1.0)]) + giggle
        wb = 9 + 4 * smoothstep(38.8, 39.6, t)
        buf += light(ROSE, Ib * np.exp(-((pdp - pb) / wb) ** 2)) + light(BLUSH, 0.22 * Ib * np.exp(-((pdp - pb) / 34) ** 2))

        # --- the rose: blooms in front of him, travels with him, dropped in the crash, picked up by her
        rose_I = keys(t, [(24.6, 0), (25.8, 0.85), (t_crash, 0.85), (38.8, 0.75), (39.1, 0)])
        if rose_I > 0:                                        # in the crash it flies on ahead of her
            rp = ps + 14 if t < t_crash else lerp(x_crash + 14, rose_drop, 1 - np.exp(-(t - t_crash) / 0.3))
            bloom = smoothstep(24.6, 25.8, t)
            buf += light(DEEP, rose_I * np.exp(-((pdp - rp) / (3 + 6 * bloom)) ** 2))
            buf += light(GOLD, 0.4 * rose_I * np.exp(-((pdp - rp) / 2.5) ** 2))

        # --- the heartbeat she sends: lub-dub, racing back along the roof to him
        if 39.8 < t < t_joy + 0.6:
            s = t - 39.8
            front = BL - 600 * s * (BL - x_stop) / (600 * (t_joy - 39.8))
            for off, a in ((0, 1.0), (70, 0.65)):
                buf += light(DEEP, a * np.exp(-((pdp - front - off) / 22) ** 2) * (front + off > x_stop - 10))
                buf += light(BLUSH, 0.6 * a * np.exp(-((pdp - front - off) / 8) ** 2) * (front + off > x_stop - 10))
        if t > t_joy:                                         # the hit lights him up
            s = t - t_joy
            buf += light(WARM, 0.8 * np.exp(-s / 0.4) * np.exp(-((pdp - x_stop) / 60) ** 2))

        # --- together at the end: a shared heartbeat
        if t > t_dash + 3:
            hb = heartbeat(t, t_dash + 3.4, 1.1)
            gl = keys(t, [(t_dash + 3, 0), (t_dash + 4, 1), (D - 4, 1), (D - 0.5, 0)])
            d = np.abs(pdp - (meet + 7))
            buf += light(DEEP, gl * (0.25 + 0.5 * hb) * np.exp(-(d / 260) ** 2))
            buf += light(BLUSH, gl * 0.3 * hb * np.exp(-(d / 70) ** 2))
        out[f][G.path] = buf * master
    return out
