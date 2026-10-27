"""Cupid's Aim: Cupid sits at the right free end of the roof and shoots three arrows through real 3-D
space. Pixels light only where an arrow passes close to them, so the flights skim the roof, cross the
empty porch notch and vanish into the night. Shot one sails clean over both wings and out past the far
corner; shot two lobs into the wrong wall of the porch and sticks there, quivering; for shot three a
laser sight wanders (all the way to the back of the house) before settling, and the arrow hits the
porch dead centre. A shell of love expands through the house from the hit."""
import numpy as np
from pixelhome.fx import DT, hexc, perc, light, keys, smoothstep, lerp, heartbeat, Flicker, nframes

CODE = 'VD03'
TITLE = "Cupid's Aim"
KIND = 'show'
DESCRIPTION = ("Cupid shoots from the end of the roof. One arrow sails over the whole house, one sticks in the "
               "wrong wall, and the third, after some careful aiming, hits the porch dead centre.")

ROSE = hexc('#ff2448')
GOLD = hexc('#ffa040')
WARM = hexc('#ffc890')
DEEP = hexc('#ff0010')
WINE = hexc('#a00008')
BLUSH = hexc('#ff5a50')
LASER = hexc('#ff0a20')

CUPID = np.array([629.0, 150.0, -191.0])
SHOTS = [  # release time, end point, flight seconds, arc height
    (7.0, np.array([-1150.0, 150.0, -168.0]), 2.0, 12.0),
    (17.0, np.array([-196.0, 150.0, -405.0]), 1.15, 55.0),
    (30.0, np.array([-22.0, 150.5, -569.0]), 0.85, 0.0),
]


def arrow_at(shot, s):
    t0, end, dur, h = shot
    u = s / dur
    p = CUPID + (end - CUPID) * u
    p = p + np.array([0, 4 * h * u * (1 - u), 0])
    return p


def render(G, seed=23):
    rng = np.random.default_rng(seed)
    D = 52.0
    out = np.zeros((nframes(D), G.N, 3))
    P = G.pos[G.path]
    pdp = G.pd[G.path]
    L = G.length
    pf = G.seg['Porch Front']
    c = G.pd[pf[len(pf) // 2]]
    hit = P[np.argmin(np.abs(pdp - c))]
    stuck = SHOTS[1][1]
    stuck_d = pdp[np.argmin(np.linalg.norm(P - stuck, axis=1))]
    glitter = Flicker(rng, G.N, 0.4, 2.5)
    fl = Flicker(rng, G.N, 0.2, 0.8)
    t_hit = SHOTS[2][0] + SHOTS[2][2]

    def near(p, r):
        return np.exp(-(np.linalg.norm(P - p, axis=1) / r) ** 2)

    def path_blob(d, sig):
        return np.exp(-((pdp - d) / sig) ** 2)

    for f in range(len(out)):
        t = f * DT
        buf = np.zeros((G.N, 3))
        master = keys(t, [(D - 4, 1), (D - 0.2, 0)])
        buf += light(WINE, keys(t, [(0, 0), (2, 0.05), (t_hit, 0.05), (t_hit + 0.5, 0)]) * (1 + 0.2 * fl(t)))

        # Cupid: a warm glow at the free end, drawing the bow before each shot
        cup = keys(t, [(0.5, 0), (2.5, 0.55), (D - 4, 0.55), (D - 1, 0)])
        sigh = np.exp(-((t - 10.6) / 0.9) ** 2) + np.exp(-((t - 19.8) / 0.7) ** 2)    # after each miss
        cup *= 1 - 0.7 * sigh
        bob = 0.0
        if t > t_hit + 1.0:                                      # a little hop of joy
            bob = 22 * abs(np.sin(np.pi * (t - t_hit - 1.0) / 0.55)) * (t < t_hit + 4.3)
        buf += light(GOLD, cup * path_blob(L - 14 - bob, 16)) + light(WARM, 0.3 * cup * path_blob(L - 6 - bob, 6))
        for i, shot in enumerate(SHOTS):
            t0 = shot[0]
            draw = smoothstep(t0 - 1.6, t0 - 0.1, t) * (t < t0)
            if draw > 0:                                         # the string pulls back, trembling
                pos = L - 60 + 48 * draw + (1.5 * np.sin(2 * np.pi * 9 * t) * draw if i == 2 else 0)
                buf += light(WARM, 0.85 * draw * path_blob(pos, 7))
            s = t - t0
            if 0 <= s < 0.8:                                     # twang
                buf += light(GOLD, 0.45 * np.exp(-s / 0.25) * (0.5 + 0.5 * np.sin(2 * np.pi * 14 * s))
                             * path_blob(L - 30, 30))
            if 0 <= s <= shot[2] + 0.15:                         # flight, motion blurred
                head = np.zeros(G.N)
                for k in range(12):
                    sk = s - k * 0.014
                    if 0 <= sk <= shot[2]:
                        w = (1 - k / 12) ** 1.5
                        head = np.maximum(head, w * near(arrow_at(shot, sk), 20 + k))
                buf += light(WARM, head) + light(ROSE, 0.4 * head ** 0.5 * (head > 0.02))

        # shot 2: the arrow sticks in the porch wall and quivers, then hangs on, then drops
        t2 = SHOTS[1][0] + SHOTS[1][2]
        if t2 <= t < t_hit + 9:
            s = t - t2
            wob = 9 * np.exp(-s / 0.5) * np.sin(2 * np.pi * 11 * s)
            I = keys(t, [(t2, 1.0), (t2 + 0.6, 0.6), (t_hit + 6, 0.5), (t_hit + 8.8, 0)])
            fall = keys(t, [(t_hit + 6, 0), (t_hit + 8.8, -60)])       # slides down the wall and off
            buf += light(GOLD, I * path_blob(stuck_d + wob + fall, 8))
            buf += light(ROSE, 0.7 * np.exp(-s / 0.3) * path_blob(stuck_d, 40))

        # shot 3: the laser sight wanders, then settles, trembling, on the porch centre
        if 21 < t < SHOTS[2][0] + 0.05:
            aim = keys(t, [(21, 2300), (22.5, 1700), (23.6, 1080), (24.6, 760), (25.6, 230), (26.2, 120),
                           (26.8, 140), (27.6, 1400), (28.4, c + 25), (29.2, c - 4), (30, c)])
            aim += 3 * np.sin(2 * np.pi * 5.3 * t) * (t < 29)
            ia = smoothstep(21, 21.6, t)
            buf += light(LASER, 0.9 * ia * path_blob(aim, 5)) + light(DEEP, 0.3 * ia * path_blob(aim, 18))

        # the hit: a white-hot flash, then a shell of love expanding through the house in 3-D
        if t >= t_hit:
            s = t - t_hit
            d3 = np.linalg.norm(P - hit, axis=1)
            buf += light(WARM, 1.0 * np.exp(-s / 0.25) * np.exp(-(d3 / 90) ** 2))
            for k, (dly, col, amp) in enumerate(((0, ROSE, 0.95), (0.35, DEEP, 0.8), (0.75, GOLD, 0.5))):
                sk = s - dly
                if sk > 0:
                    r = 340 * sk ** 0.9
                    shell = np.exp(-((d3 - r) / 75) ** 2) * np.exp(-sk / 4.0)
                    buf += light(col, amp * shell)
            # afterwards the house glows like a heart, beating, with gold glitter
            glow = smoothstep(0.8, 3.0, s) * keys(t, [(t_hit, 1), (D - 6, 1), (D - 0.5, 0)])
            core = np.exp(-(d3 / 420) ** 2)
            buf += light(WINE, glow * 0.2)
            buf += light(ROSE, glow * 0.3 * core * (0.8 + 0.2 * fl(t)))
            for tb in np.arange(t_hit + 3.0, D - 5, 1.15):          # every beat sends a soft ring out
                for dt_, a in ((0, 1.0), (0.22, 0.6)):
                    sb = s - (tb - t_hit) - dt_
                    if 0 < sb < 3:
                        buf += light(DEEP, glow * 0.55 * a * np.exp(-sb / 1.0) * np.exp(-((d3 - 600 * sb) / 90) ** 2))
            g = np.clip(glitter(t) - 1.1, 0, None)
            buf += light(GOLD, glow * 0.6 * g)
        out[f][G.path] = buf * master
    return out
