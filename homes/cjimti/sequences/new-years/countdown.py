"""Countdown: The roofline becomes a ten-step clock. A hand sweeps the U from a pivot inside the
porch, winding the house up; then ten arcs go dark one per second, from both free ends inward,
until only the far Porch Front is left. It goes out, a beat of darkness, and midnight breaks
outward from the porch along the whole roof."""
import numpy as np
from pixelhome.fx import DT, hexc, light, keys, smoothstep, Flicker, nframes

CODE = 'NY01'
TITLE = 'Countdown'
KIND = 'show'
DESCRIPTION = 'A clock hand winds the roof into ten gold arcs; they go dark one per second from both ends inward until the porch alone is left, then midnight breaks.'

GOLD = hexc('#ffb030')
CHAMP = hexc('#ffd890')
SILVER = hexc('#c8d8ff')
EMBER = hexc('#ff3a08')
NAVY = hexc('#0a1850')
WHITE = hexc('#fff4e0')

PIVOT = np.array([-20.0, -400.0])      # inside the porch notch, seen from above
T_SWEEP = 2.0                          # the hand appears
T_COUNT = 22.0                         # "ten"
T_ZERO = T_COUNT + 10.0                # porch goes out
T_BREAK = T_ZERO + 0.7                 # midnight


def arcs(G):
    """Ten arcs along the path: five left of the Porch Front, four right of it, the porch itself
    last. Returns arc id per node (0 = first to go dark) and a gap mask between arcs."""
    pd = G.pd
    pf = G.pd[G.seg['Porch Front']]
    a0, a1 = pf.min() - 2, pf.max() + 2
    left = np.linspace(0, a0, 6)
    right = np.linspace(a1, G.length + 1e-3, 5)
    order = np.full(G.N, -1)
    gap = np.ones(G.N)
    # beats: L1 R1 L2 R2 L3 R3 L4 R4 L5 PF (outermost first)
    for k in range(5):
        m = (pd >= left[k]) & (pd < left[k + 1])
        order[m] = 2 * k if k < 4 else 8
        gap[m] = smoothstep(0, 9, pd[m] - left[k]) * smoothstep(0, 9, left[k + 1] - pd[m])
    for k in range(4):
        m = (pd >= right[k]) & (pd <= right[k + 1])
        rk = 3 - k                                       # count from the free right end inward
        order[m] = 2 * rk + 1
        gap[m] = smoothstep(0, 9, pd[m] - right[k]) * smoothstep(0, 9, right[k + 1] - pd[m])
    m = order < 0
    order[m] = 9
    gap[m] = smoothstep(0, 9, pd[m] - a0) * smoothstep(0, 9, a1 - pd[m])
    return order, gap


def render(G, seed=21):
    rng = np.random.default_rng(seed)
    D = 48.0
    out = np.zeros((nframes(D), G.N, 3))
    P = G.pos
    theta = np.arctan2(P[:, 0] - PIVOT[0], -(P[:, 2] - PIVOT[1])) % (2 * np.pi)
    rad = np.hypot(P[:, 0] - PIVOT[0], P[:, 2] - PIVOT[1])
    order, gap = arcs(G)
    pfc = G.pd[G.seg['Porch Front']].mean()
    dpath = np.abs(G.pd - pfc)
    sparkle = Flicker(rng, G.N, 2.0, 7.0)
    shimmer = Flicker(rng, G.N, 0.2, 0.8)
    beat_t = T_COUNT + order.astype(float)               # when each arc goes dark

    # hand angle: one slow winding turn, then faster and faster, parking at 12 o'clock for the count
    def hand_angle(t):
        if t < T_SWEEP:
            return 0.0
        if t < 8.0:
            return 2 * np.pi * smoothstep(T_SWEEP, 8.0, t)
        # accelerate, then decelerate to land exactly on a whole turn by T_COUNT - 1
        u = np.clip((t - 8.0) / (T_COUNT - 1 - 8.0), 0, 1)
        turns = 9 * (u ** 2 * (3 - 2 * u))                # smooth start/stop, ~1.3 rev/s at peak
        return 2 * np.pi * (1 + turns)

    for f in range(len(out)):
        t = f * DT
        fr = out[f]
        h = hand_angle(t)
        behind = (h - theta) % (2 * np.pi)                # how far the hand has gone past a pixel
        fr += light(NAVY, keys(t, [(0, 0), (2, 0.12), (T_ZERO, 0.12), (T_ZERO + 0.3, 0), (D - 6, 0), (D, 0)]))

        # the arcs: ignited by the first pass of the hand, glowing hotter while the hand races
        wound = (h >= theta) if t < 8.2 else np.ones(G.N, bool)
        tension = keys(t, [(7.5, 0.6), (9, 0.32), (T_COUNT - 3, 0.42), (T_COUNT - 0.5, 0.85)])
        glow = np.where(wound, tension, 0.0)
        # each pass leaves a brief brightening behind the hand
        if T_SWEEP < t < T_COUNT:
            glow = glow + 0.45 * np.exp(-behind / 0.7) * wound * smoothstep(7.5, 9, t)
        # count down: each arc flashes, then cools to an ember and goes out
        tau = t - beat_t
        flash = np.where((tau >= 0) & (tau < 0.6), np.exp(-tau / 0.12), 0.0)
        alive = np.where(tau < 0, 1.0, 0.0)
        ember = np.where(tau >= 0, 0.45 * np.exp(-tau / 0.35), 0.0)
        # the arcs still alive thump on every beat
        if T_COUNT <= t < T_ZERO:
            ph = (t - T_COUNT) % 1.0
            glow = glow * (1 + 0.35 * np.exp(-ph / 0.12) + 0.15 * np.exp(-((ph - 0.22) / 0.06) ** 2))
            # the last arc trembles
            if t > T_ZERO - 1:
                glow = glow * (1 + 0.08 * sparkle(t))
        I = glow * alive * gap * (1 + 0.04 * shimmer(t))
        col = GOLD + (CHAMP - GOLD) * np.clip(glow - 0.6, 0, 1)[:, None]
        fr += light(col, I)
        if t >= T_COUNT:
            fr += light(WHITE, 1.0 * flash * gap)
            fr += light(EMBER, ember * gap)

        # the hand itself: a silver beam from the pivot
        hk = keys(t, [(T_SWEEP, 0), (T_SWEEP + 0.6, 1), (T_COUNT - 1, 1), (T_COUNT, 0.3), (T_ZERO, 0.3), (T_ZERO + 0.2, 0)])
        if hk > 0:
            if t < T_COUNT - 0.5:
                d = np.minimum(behind, 2 * np.pi - behind)
                width = 0.05 + 0.04 * smoothstep(8, 14, t)
                beam = np.exp(-(d / width) ** 2) + 0.4 * np.exp(-behind / 0.35) * (t > 8)
            else:
                # during the count the hand ticks one tenth of a turn per beat, with a sprung overshoot
                n = np.floor(t - T_COUNT + 1)
                ph = (t - T_COUNT + 1) % 1.0
                spring = 1 - np.exp(-ph / 0.05) * np.cos(ph * 40)
                ang = 2 * np.pi * (np.clip(n - 1, 0, 10) + spring * (n >= 1)) / 10
                d = np.abs(((theta - ang + np.pi) % (2 * np.pi)) - np.pi)
                beam = np.exp(-(d / 0.06) ** 2)
            beam = beam * smoothstep(40, 160, rad)
            fr += light(SILVER, hk * 0.9 * beam)

        # midnight: a crack of light runs out of the porch along both arms of the roof
        if t >= T_BREAK:
            tb = t - T_BREAK
            front = tb * 1100
            wave = np.exp(-((dpath - front) / 60) ** 2)
            lit = smoothstep(front + 30, front - 60, dpath)
            settle = keys(tb, [(0, 1.0), (1.5, 1.0), (4, 0.55), (6, 0.5), (8, 0.3), (D - T_BREAK - 2, 0.12), (D - T_BREAK, 0)])
            glit = np.clip(sparkle(t) - 0.8, 0, None) ** 2 * smoothstep(0.5, 2, tb) * keys(tb, [(0, 1), (6, 1), (9, 0.3)])
            silver = (np.sin(G.pd / 55 - tb * 1.4) > 0.3)[:, None]
            gcol = np.where(silver, SILVER, CHAMP)
            # the new year's clock starts: a slow hand of champagne light, its first turn
            if tb > 6:
                nh = 2 * np.pi * smoothstep(6, D - T_BREAK - 1, tb)
                nb = (nh - theta) % (2 * np.pi)
                fr += light(CHAMP, smoothstep(6, 7.5, tb) * smoothstep(D - T_BREAK, D - T_BREAK - 3, tb) * (0.7 * np.exp(-(np.minimum(nb, 2 * np.pi - nb) / 0.08) ** 2)
                                                          + 0.3 * np.exp(-nb / 0.6)) * smoothstep(40, 160, rad))
            fr += light(WHITE, 1.1 * wave)
            fr += light(GOLD, lit * settle * (0.55 + 0.15 * shimmer(t)))
            fr += light(gcol, lit * settle * 0.9 * glit)
            # rings of light rolling outward from the pivot through 3-D space
            for k, t0 in enumerate((0.3, 1.4, 2.6, 4.2)):
                if tb > t0:
                    r = (tb - t0) * 650
                    ring = np.exp(-((rad - r) / 45) ** 2) * np.exp(-(tb - t0) / 1.6)
                    fr += light(SILVER if k % 2 else CHAMP, 0.8 * ring)
            fr += light(WHITE, 0.5 * np.exp(-tb / 0.18))
    return out
