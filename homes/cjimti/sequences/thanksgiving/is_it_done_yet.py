"""Is It Done Yet?: The porch is the oven, its sides are the oven walls, the Right wing is the kitchen
timer and the Left wing is where the hungry family waits. The oven heats with a real thermal lag and
glows through blackbody colours. Someone keeps walking over to open the door: a blast of light, the
heat rolls out along the porch sides, the oven drops back to red and the timer gains time. The
peeks get faster. Then the cook stands guard and bats them away, twice. The timer runs out, dings,
and the turkey comes out golden."""
import numpy as np
from pixelhome.fx import DT, hexc, light, keys, smoothstep, colormap, nframes

CODE = 'TG02'
TITLE = 'Is It Done Yet?'
KIND = 'show'
DESCRIPTION = ('The porch is the oven and the Right wing is the timer. Someone keeps opening the door to check, '
               'heat pours out, the timer gains time, until the cook stands guard. Ding.')

GOLD = hexc('#ffb000')
AMBER = hexc('#ff8a18')
CRANBERRY = hexc('#c0102a')
WARM = hexc('#ffc27a')
BROWN = hexc('#7a3008')

D = 70.0
# blackbody-ish ramp for the oven: dull red -> cherry -> orange -> amber
heat_map = colormap([(0.0, (0, 0, 0)), (0.15, (0.05, 0.0, 0.0)), (0.35, (0.22, 0.01, 0.0)), (0.55, (0.6, 0.04, 0.0)),
                     (0.75, (1.0, 0.16, 0.0)), (0.9, (1.0, 0.33, 0.02)), (1.05, (1.0, 0.55, 0.12))])


def render(G, seed=22):
    rng = np.random.default_rng(seed)
    F = nframes(D)
    out = np.zeros((F, G.N, 3))
    pdp = G.pd[G.path]
    n = G.N
    PF = (pdp > 1312) & (pdp < 1660)
    PL = (pdp > 893) & (pdp <= 1312)
    PR = (pdp >= 1660) & (pdp < 2033)
    LW = (pdp > 490) & (pdp <= 893)
    RW = pdp >= 2033
    R0, R1 = 2036.0, 2511.8
    # distance from the oven along each wall (0 at the back corner, 1 at the front)
    wall = np.where(PL, (1310 - pdp) / 415, np.where(PR, (pdp - 1660) / 370, 0))

    # peeks: (time the asker sets off, speed of the walk)
    peeks = [(12.0, 330), (22.0, 420), (29.5, 520), (34.5, 650)]
    blocks = [(42.0, 'left'), (47.5, 'right')]

    # simulate oven temperature and timer
    T = np.zeros(F)
    rem = np.zeros(F)
    temp, r = 0.0, 0.0
    door = np.zeros(F)
    for f in range(F):
        t = f * DT
        open_amt = 0.0
        for t0, v in peeks:
            ta = t0 + 800 / v                                        # arrives at the door
            open_amt = max(open_amt, smoothstep(ta - 0.1, ta + 0.15, t) * (1 - smoothstep(ta + 1.8, ta + 2.3, t)))
        door[f] = open_amt
        target = 0.0 if t < 2 else 1.0
        rate = 0.09 + 1.8 * open_amt
        target = target * (1 - 0.85 * open_amt)
        temp += (target - temp) * rate * DT
        T[f] = temp
        if 4 <= t < 6:
            r = smoothstep(4, 6, t)
        elif t >= 6:
            r -= DT / 30
            for t0, v in peeks:
                ta = t0 + 800 / v
                if ta + 0.4 <= t < ta + 1.6:
                    r += 0.16 * DT / 1.2
            r = max(r, 0.0)
        rem[f] = r
    ding = next(f for f in range(nframes(7), F) if rem[f] <= 0) * DT

    for f in range(F):
        t = f * DT
        buf = np.zeros((n, 3))
        Tf = T[f]
        # oven window with rising convection shimmer, oven walls warm from the back
        conv = 0.5 + 0.5 * np.sin(pdp * 0.05 - 2.1 * t + 1.7 * np.sin(pdp * 0.017 + 0.6 * t))
        h = Tf * (0.82 + 0.16 * conv)
        done = smoothstep(ding + 1.2, ding + 3.5, t)
        h = h * (1 - done) + done * 0.62
        oven = heat_map(h)
        golden = light(BROWN, 0.55 + 0.1 * conv) + light(GOLD, 0.45 * conv)
        ovenc = oven * (1 - done) + golden * done
        buf[PF] += ovenc[PF]
        buf[PL | PR] += heat_map(0.55 * h * np.exp(-wall / 0.35))[PL | PR] * (1 - done)

        # door open: a flash on the window and a heat cloud rolling forward along both porch sides
        for t0, v in peeks:
            ta = t0 + 800 / v
            u = t - ta
            if 0 <= u < 3.0:
                buf[PF] += light(WARM, 0.65 * np.exp(-u / 0.35) * np.ones(PF.sum()))
                front = u / 1.6
                puff = np.exp(-((wall - front) / 0.18) ** 2) * np.exp(-u / 1.1)
                buf[PL | PR] += light(AMBER, 0.8 * puff[PL | PR])
            # the asker walks from the Left wing to the oven and back, slower
            ta_back = ta + 2.3
            if t0 <= t < ta_back + 800 / (0.5 * v):
                if t < ta:
                    x = 500 + v * (t - t0)
                elif t < ta_back:
                    x = 1300 - 6 * np.sin(np.pi * (t - ta) / 2.3)
                else:
                    x = 1300 - 0.5 * v * (t - ta_back)
                buf += light(CRANBERRY, 0.9 * np.exp(-((pdp - x) / 11) ** 2))

        # blocked: the cook (gold) rushes out from the oven and pushes the asker back
        for tb, side in blocks:
            u = t - tb
            if 0 <= u < 4.5:
                if side == 'left':
                    meet = 990.0
                    ax = 520 + 700 * u if u < 0.67 else meet - 380 * (u - 0.67) * (1 + 0.3 * (u - 0.67))
                    cx = 1300 - 900 * u if u < 0.34 else meet + 12 + 120 * max(0, u - 0.9)
                    cx = max(cx, meet + 12)
                else:
                    meet = 1960.0
                    ax = 2530 - 850 * u if u < 0.67 else meet + 380 * (u - 0.67) * (1 + 0.3 * (u - 0.67))
                    cx = 1660 + 900 * u if u < 0.34 else meet - 12 - 120 * max(0, u - 0.9)
                    cx = min(cx, meet - 12)
                cx = np.clip(cx, 1000 if side == 'left' else 1660, 1300 if side == 'left' else 1950)
                fade = 1 - smoothstep(3.3, 4.5, u)
                buf += light(CRANBERRY, 0.9 * fade * np.exp(-((pdp - ax) / 11) ** 2))
                buf += light(GOLD, fade * np.exp(-((pdp - cx) / 13) ** 2))
                hit = np.exp(-((u - 0.67) / 0.12) ** 2)                 # the swat
                buf += light(WARM, 0.8 * hit * np.exp(-((pdp - meet) / 30) ** 2))

        # the family waiting on the Left wing: a low murmur that grows hungrier
        hunger = keys(t, [(3, 0), (8, 0.12), (40, 0.22), (ding, 0.25), (ding + 0.5, 0.0)])
        mur = 0.5 + 0.5 * np.sin(pdp * 0.08 + 3.0 * t) * np.sin(pdp * 0.021 - 1.3 * t)
        buf[LW] += light(CRANBERRY, hunger * (0.6 + 0.4 * mur[LW]))

        # the timer: a gold bar draining toward the house, a tick at its tip
        r = rem[f]
        if 4 <= t < ding + 0.1:
            tip = R0 + r * (R1 - R0)
            bar = np.clip((tip - pdp) / 6 + 0.5, 0, 1) * RW
            tick = 0.5 + 0.5 * np.cos(2 * np.pi * t) ** 8
            buf += light(GOLD, 0.22 * bar) + light(WARM, 0.5 * tick * np.exp(-((pdp - tip) / 5) ** 2) * RW)
            gain = rem[f] - rem[max(0, f - 8)]
            if gain > 0:
                buf += light(CRANBERRY, min(1, gain * 40) * 0.6 * np.exp(-((pdp - tip) / 25) ** 2) * RW)
        # DING: three gold rings out of the timer, then warmth over the whole house
        u = t - ding
        if u >= 0:
            for k in range(3):
                uk = u - 0.42 * k
                if uk >= 0:
                    ring = np.exp(-((np.abs(pdp - R0) - 700 * uk) / 50) ** 2) * np.exp(-uk / 0.6)
                    buf += light(GOLD, 0.9 * ring * (pdp > 1600)) + light(WARM, 0.9 * np.exp(-uk / 0.12) * RW)
            glow = smoothstep(1.5, 4.5, u) * keys(t, [(ding, 1), (64, 1), (70, 0)])
            dist = np.abs(pdp - 1486)
            spread = smoothstep(0, 1, (900 * (u - 1.5) / 2.0 - dist) / 300)
            cheer = (0.5 + 0.5 * np.sin(pdp * 0.06 - 4 * t)) ** 3
            buf += light(AMBER, glow * spread * (0.26 + 0.12 * cheer))
            # steam from the bird
            for k in range(5):
                uk = u - 2.0 - 0.9 * k
                if 0 < uk < 4:
                    p = 1330 + 75 * k + 18 * np.sin(uk * 2 + k)
                    buf[PF] += light(WARM, 0.35 * np.sin(np.pi * uk / 4) * np.exp(-((pdp[PF] - p) / 18) ** 2))
            buf *= keys(t, [(65, 1.0), (70, 0.0)])
        out[f][G.path] = buf
    return out
