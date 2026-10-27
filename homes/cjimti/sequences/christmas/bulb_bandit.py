"""The Bulb Bandit: The roof is strung with bulbs. A green figure with yellow eyes peeks out of the free
back end of Side and tiptoes along the roofline, reeling the string in behind him: every bulb he
passes is pulled along the wire into his sack, segment by segment, pausing at each corner to look
round. A kid in pyjamas catches him on the porch; he shoos her back to bed. At the far right end, with
the whole house dark and his sack bulging, the house starts to sing anyway; something warm swells
in him and every bulb flies home."""
import numpy as np
from pixelhome.fx import DT, hexc, perc, light, keys, smoothstep, lerp, Flicker, nframes

CODE = 'XM03'
TITLE = 'The Bulb Bandit'
KIND = 'show'
DESCRIPTION = ('A green sneak with yellow eyes tiptoes along the roof reeling every bulb into his sack, '
               'corner by corner. The dark house sings anyway, something warm swells in him, and the lights fly home.')

BULBS = [hexc(c) for c in ('#ff2010', '#10b838', '#ffa018', '#2850ff', '#ff5a20', '#ff3060')]
GREEN = hexc('#38c008')
DARK_GREEN = hexc('#105800')
EYE = hexc('#d8ff10')
KID = hexc('#ffd0e0')
SING = hexc('#ffb040')
HEART = hexc('#ff1030')
WHITE = hexc('#fff4e0')

# bandit walk along the path (distance units): (t, position); corners at 490, 890, 1304, 1648, 2016
WALK = [(3.0, -6), (4.5, 12), (12.0, 470), (13.6, 470), (18.6, 875), (20.0, 875), (25.0, 1290),
        (26.0, 1290), (29.0, 1470), (33.2, 1470), (35.4, 1635), (36.4, 1635), (39.4, 2005),
        (40.4, 2005), (47.0, 2400), (60.5, 2400)]


def walk(t):
    """Tiptoe: progress between waypoints goes in quick steps with little holds between."""
    for (t0, a), (t1, b) in zip(WALK, WALK[1:]):
        if t0 <= t < t1:
            if a == b:
                return float(a)
            n = max(2, int(abs(b - a) / 34))
            v = (t - t0) / (t1 - t0) * n
            k = np.floor(v)
            return a + (b - a) * (k + smoothstep(0.05, 0.75, v - k)) / n
    return float(WALK[-1][1]) if t >= WALK[-1][0] else float(WALK[0][1])


def render(G, seed=23):
    rng = np.random.default_rng(seed)
    D = 72.0
    F = nframes(D)
    out = np.zeros((F, G.N, 3))
    x = G.pd[G.path]
    Ltr = G.length

    home = np.arange(6.0, Ltr - 3, 12.5)               # one mini bulb every 12.5 units
    nb = len(home)
    bcol = np.array([BULBS[i % len(BULBS)] for i in range(nb)])
    bcol = bcol[rng.permutation(nb)]
    tw = Flicker(rng, nb, 0.08, 0.4)

    # when the bandit's sack passes each bulb it is reeled in
    tt = np.arange(F) * DT
    gpath = np.array([walk(t) for t in tt])
    t_pass = np.array([tt[np.argmax(gpath >= h + 16)] if (gpath >= h + 16).any() else 99 for h in home])
    t_steal = t_pass + rng.uniform(0.0, 0.25, nb)
    REEL = 0.55
    T_BURST = 61.0
    # on the way home every bulb leaves the sack at once and lands within a moment of the others
    t_home = T_BURST + 0.1 + rng.uniform(0, 0.35, nb)
    FLY = 2.0
    eye_blinks = [5.2, 9.0, 16.9, 23.4, 31.0, 31.35, 44.0]
    looks = [(12.0, 13.6), (18.6, 20.0), (25.0, 26.0), (35.4, 36.4), (39.4, 40.4)]

    for f in range(F):
        t = f * DT
        g = gpath[f]
        sack_x = g - 15
        fr = np.zeros((G.N, 3))
        master = keys(t, [(0, 0), (1.5, 1), (D - 3, 1), (D - 0.3, 0)])

        # bulbs: at home, being reeled in, in the sack, or flying home
        bp = home.copy()
        bI = 0.55 * (1 + 0.12 * tw(t))
        u_reel = np.clip((t - t_steal) / REEL, 0, 1)
        reeling = (u_reel > 0) & (u_reel < 1)
        bp = np.where(u_reel > 0, lerp(home, sack_x, u_reel ** 2), bp)
        gone = (u_reel >= 1) & (t < t_home)
        u_fly = np.clip((t - t_home) / FLY, 0, 1)
        flying = (u_fly > 0) & (u_fly < 1)
        e = 1 - (1 - u_fly) ** 3
        bp = np.where(t >= t_home, lerp(T_BURST_X, home, e), bp) if t >= T_BURST else bp
        bI = np.where(gone, 0.0, bI)
        bI = np.where(reeling, bI * (1 + 0.5 * u_reel), bI)
        bI = np.where(t >= t_home, bI * (1 + 0.8 * (1 - u_fly)) + 0.25 * smoothstep(0.85, 1, u_fly) * np.exp(-np.clip(t - t_home - FLY, 0, None) / 0.6), bI)
        bI = np.where((t >= T_BURST) & (t < t_home), 0.0, bI)
        wid = np.where(flying, 2.4 + 10 * (1 - u_fly) * u_fly, 2.4)
        near = np.abs(x[:, None] - bp[None]) < 60
        kern = np.where(near, np.exp(-((x[:, None] - bp[None]) / wid[None]) ** 2), 0)
        fr += (kern * perc(bI)[None]) @ bcol

        # the sack: everything he has stolen, a shimmering multicolour bundle
        n_in = gone.sum() if t < T_BURST else 0
        if n_in:
            frac = n_in / nb
            sw = 5 + 15 * np.sqrt(frac)
            shimmer = 0.5 + 0.5 * np.sin(x * 0.5 + 7 * t)
            mix = lerp(bcol[gone].mean(0), BULBS[(int(t * 3)) % len(BULBS)], 0.25 * shimmer[:, None])
            teeter = 0.0
            if 47.5 < t < T_BURST:
                teeter = 9 * np.sin(2 * np.pi * (t - 47.5) / 1.3) * np.exp(-(t - 47.5) / 4)
            sk = np.exp(-((x - (sack_x + teeter)) / sw) ** 2) * (0.35 + 0.5 * np.sqrt(frac))
            fr += perc(sk)[:, None] * mix

        # the bandit himself
        vis = keys(t, [(3.0, 0), (3.6, 1), (51.5, 1), (53.0, 0.4), (D - 3, 0.55), (D - 0.3, 0)])
        if vis > 0 and t < D:
            body = np.exp(-((x - g) / 9) ** 2)
            fr += light(DARK_GREEN, 0.5 * vis * np.exp(-((x - g) / 16) ** 2))
            fr += light(GREEN, 0.55 * vis * body)
            look = 0.0
            for a, b in looks:
                if a <= t < b:
                    look = 3.5 * np.sin(2 * np.pi * (t - a) / (b - a))
            if 29.0 < t < 33.2:                     # caught: eyes wide and fixed on the kid
                look = keys(t, [(29.5, 0), (30.0, 3), (32.8, 3), (33.2, 0)])
            wide = keys(t, [(29.6, 1), (29.9, 1.6), (32.6, 1.6), (33.2, 1)])
            blink = 1 - max([max(0.0, 1 - abs(t - b) / 0.12) for b in eye_blinks])
            for side in (-1, 1):
                ex = g + 3 + side * 3.6 * wide + look
                fr += light(EYE, 1.0 * vis * blink * np.exp(-((x - ex) / 1.6) ** 2))

        # a kid, up past her bedtime, just ahead of him on the porch
        cl = keys(t, [(29.6, 0), (30.2, 0.55), (32.0, 0.55), (33.0, 0)])
        if cl > 0:
            cx = 1470 + keys(t, [(29.6, 30), (32.0, 30), (33.0, 60)])
            fr += light(KID, cl * np.exp(-((x - cx) / 5) ** 2))

        # the house sings in the dark: slow warm swells rising out of the porch, phrase by phrase
        if 48.0 < t < 63.0:
            ts = t - 48.0
            amp = keys(t, [(48, 0), (50, 1), (60, 1), (63, 0)])
            d0 = np.abs(x - 1476)
            swell = 0.5 + 0.5 * np.sin(2 * np.pi * (ts * 0.9 - d0 / 700))
            fr += light(SING, amp * 0.22 * swell ** 2 * (0.6 + 0.4 * np.exp(-d0 / 900)))

        # the warmth swells in him
        stages = ((52.5, 9), (55.0, 20), (57.5, 42))
        for k, (t0, r) in enumerate(stages):
            t1 = stages[k + 1][0] if k < 2 else T_BURST + 1.5
            if t0 <= t < t1:
                beat = sum(np.exp(-((t - t0 - j * 0.8 - 0.03) / 0.06) ** 2) +
                           0.7 * np.exp(-((t - t0 - j * 0.8 - 0.25) / 0.07) ** 2) for j in range(3))
                grow = smoothstep(t0, t0 + 0.3, t)
                hold = 0.6 if t < T_BURST else 0.6 * np.exp(-(t - T_BURST) / 0.5)
                size = r * (0.6 + 0.4 * grow) * (1 + 0.15 * beat)
                fr += light(HEART, (hold + 0.4 * beat) * np.exp(-((x - g) / size) ** 2))

        # the burst
        if T_BURST <= t < T_BURST + 0.8:
            tb = t - T_BURST
            fr += light(WHITE, 0.9 * np.exp(-tb / 0.15) * np.exp(-((x - T_BURST_X) / (20 + 300 * tb)) ** 2))

        # finale: every bulb home and a little brighter, a warm glow under them
        fin = keys(t, [(63, 0), (64.5, 1)])
        if fin > 0:
            fr += light(SING, 0.08 * fin * np.ones(G.N))
        out[f][G.path] = fr * master
    return out


T_BURST_X = 2385.0
