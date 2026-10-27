"""The One That Got Away: Dad fishes from the dock at the free end of Right. Everything else is
water, run as a 1-D wave equation along the roof, so every plunk, nibble and splash sends real
ripples round the corners. He casts, the lure flies out with drag and lands on the far porch; the
bobber rides the swell; nibble, nibble, nothing, then a bite. The fight pulls line out and back, the
line hums as a vibrating string, the fish comes up onto the dock and the line snaps. The fish swims
off round the house and out the back end of Side, jumping once to make the point. Then Dad shows
how big it was, and keeps showing."""
import numpy as np
from pixelhome.fx import DT, hexc, perc, light, smoothstep, keys, lerp, Flicker, nframes

CODE = 'FA03'
TITLE = 'The One That Got Away'
KIND = 'show'
DESCRIPTION = ('Dad fishes off the end of the right wing; the rest of the roof is water with real ripples. '
               'Cast, bobber, nibbles, a bite, the fight, the snap, and then: it was THIS big.')

WATER = hexc('#103a70')
GLINT = hexc('#9fd8ff')
LURE = hexc('#fff0c0')
BOBBER = hexc('#ff2a20')
LINE = hexc('#c8d8e8')
FISH = hexc('#b8ffe0')
LANTERN = hexc('#ffa040')
DOCK = hexc('#603818')
HANDS = hexc('#ffe0b0')


def render(G, seed=23):
    rng = np.random.default_rng(seed)
    D = 73.0
    n = G.N
    out = np.zeros((nframes(D), n, 3))
    x = G.pd[G.path]
    pi = np.arange(n)
    DOCKM = pi >= 381
    WET = ~DOCKM
    tip = x[500] - 12                                  # rod tip
    shore = x[380]

    # wave equation on a uniform grid along the wet part of the path
    dx = 5.0
    gx = np.arange(0, shore + dx, dx)
    h = np.zeros(len(gx))
    hv = np.zeros(len(gx))
    c2 = 260.0 ** 2
    sub = 4
    sdt = DT / sub
    shimmer = Flicker(rng, n, 0.05, 0.4)

    def kick(pos, amp, width=12):
        width = width * 1.6
        # a displacement dimple with a raised rim: splits into two ripple trains, one each way
        r = (gx - pos) / width
        h[:] += (amp / 160.0) * (1 - 2 * r ** 2) * np.exp(-r ** 2)

    land = x[296]
    cast = [(3.4, tip - 30), (4.3, tip + 6), (4.45, tip), (6.6, land)]
    events = [(6.6, land, -260, 14)]
    for tn, a in ((11.0, 70), (14.5, 60), (15.1, 70), (21.4, 80), (21.75, 90), (22.1, 100)):
        events.append((tn, land, -a, 8))
    bite = 25.0
    events.append((bite, land, -520, 16))
    # the hook during the fight (pd), then the fish
    fight = [(bite, land), (25.6, land - 30), (28.0, land - 170), (28.4, land - 165), (31.0, land + 80),
             (31.4, land + 70), (33.2, land - 40), (33.6, land - 30), (38.0, shore - 10),
             (39.2, x[381] + 70), (40.2, x[381] + 80)]
    crank_t = np.arange(28.4, 31.0, 0.32).tolist() + np.arange(33.6, 39.0, 0.32).tolist()
    snap = 40.2
    for tt in np.arange(25.3, 38.0, 0.45):
        events.append((tt, None, -90, 10))           # thrashing at the hook
    fall = [(snap, x[381] + 80), (40.9, shore - 40)]
    events.append((40.9, shore - 40, -420, 18))
    swim = [(41.2, shore - 40), (44.0, shore - 360), (52.0, 640), (56.5, -60)]
    jump = 50.2
    plip = 68.2
    events.append((plip, land + 40, -110, 6))
    events.sort(key=lambda e: e[0])
    ev_i = 0

    for f in range(len(out)):
        t = f * DT
        buf = np.zeros((n, 3))
        fade = keys(t, [(0, 0), (2.5, 1), (69.5, 1), (73, 0)])

        # where the hook / fish is now
        if t < bite:
            hook = keys(t, cast) if t < 6.6 else land
        elif t < snap:
            hook = keys(t, fight)
        elif t < 41.2:
            hook = keys(t, fall)
        else:
            hook = keys(t, swim)

        # fire events into the water
        while ev_i < len(events) and events[ev_i][0] <= t:
            te, pos, a, w = events[ev_i]
            p = hook if pos is None else pos
            if p < shore:
                kick(p, a + (rng.normal(0, 25) if pos is None else 0), w)
            ev_i += 1
        if 41.2 <= t < 56.5 and f % 6 == 0:           # the fish's wake
            kick(hook, -60, 7)
        if jump <= t < jump + DT:
            kick(hook, -380, 16)
        if jump + 0.8 <= t < jump + 0.8 + DT:
            kick(hook - 70, -380, 16)

        # integrate the wave equation (free ends at both sides)
        for _ in range(sub):
            lap = np.empty_like(h)
            lap[1:-1] = h[2:] - 2 * h[1:-1] + h[:-2]
            lap[0] = h[1] - h[0]
            lap[-1] = h[-2] - h[-1]
            hv += (c2 * lap / dx ** 2 - 0.35 * hv) * sdt
            h += hv * sdt
        hp = np.interp(x, gx, h)

        # water: deep blue with glints where the surface rises
        calm = 0.12 + 0.02 * shimmer(t)
        crest = np.clip(np.abs(hp) - 0.02, 0, None)
        buf += WET[:, None] * (light(WATER, (calm + 0.25 * np.clip(-hp, 0, 0.4)) * fade) +
                               light(GLINT, np.clip(1.1 * np.clip(hp, 0, None), 0, 0.85) * fade))

        # the dock and the lantern at the end
        buf += DOCKM[:, None] * light(DOCK, 0.08 * fade * np.ones(n))
        lan = 0.45 * fade * (1 + 0.06 * shimmer(t * 2)) * keys(t, [(56.5, 1), (57.5, 0.7), (59, 1)])
        buf += light(LANTERN, lan * np.exp(-((x - x[500]) / 14) ** 2))

        # the line, from the rod tip to the hook
        line_on = (4.45 <= t < snap)
        if line_on:
            lo, hi = min(hook, tip), tip
            seg = (x >= lo) & (x <= hi)
            s = (x - lo) / max(1.0, hi - lo)
            taut = keys(t, [(bite, 0), (bite + 0.3, 1), (snap, 1)])
            hum = np.abs(np.sin(np.pi * 3 * s) * np.sin(2 * np.pi * 7 * t)) * taut
            hum += np.abs(np.sin(np.pi * 5 * s + 1) * np.sin(2 * np.pi * 11 * t)) * taut * 0.5
            I = (0.12 + 0.1 * taut + 0.1 * hum) * seg
            buf += light(LINE, I)
        if snap <= t < snap + 0.6:                    # the line recoils to the rod with a wiggle
            u = (t - snap) / 0.6
            end = lerp(x[381] + 80, tip, smoothstep(0, 1, u) ** 0.6)
            seg = (x >= end) & (x <= tip)
            wig = 0.5 + 0.5 * np.sin((x - end) / 9 + t * 40)
            buf += light(LINE, 0.3 * (1 - u) * wig * seg)
            buf += light(hexc('#ffffff'), np.exp(-(t - snap) / 0.08) * np.exp(-((x - x[381] - 80) / 10) ** 2))

        # lure in flight, then the bobber riding the surface
        if 3.4 <= t < 6.6:
            load = smoothstep(3.4, 4.3, t)
            buf += light(LURE, (0.4 + 0.4 * load) * np.exp(-((x - hook) / 6) ** 2))
        elif 6.6 <= t < bite:
            hb = np.interp(land, gx, h)
            vis = np.clip(0.75 + 2.5 * hb, 0.05, 1.0)
            buf += light(BOBBER, vis * np.exp(-((x - land) / 7) ** 2))
            buf += light(hexc('#ffffff'), 0.5 * vis * np.exp(-((x - land - 9) / 4) ** 2))

        # the fish: a big pale shape under the hook, close to the surface in the fight
        if bite <= t < 56.5:
            size = 26 if t < snap else 30
            bright = keys(t, [(bite, 0.15), (30, 0.3), (37, 0.45), (39.5, 0.8), (snap, 0.8), (41, 0.4), (56.5, 0.35)])
            flick = 0.5 + 0.5 * np.sin(2 * np.pi * (2.2 if t > 41 else 4.0) * t)
            pos = hook + (4 * np.sin(2 * np.pi * 9 * t) if 38.6 < t < snap else 0)
            # the body: a head and a tail that sways
            body = np.exp(-((x - pos) / size) ** 2) + 0.6 * flick * np.exp(-((x - pos - 1.4 * size) / (0.5 * size)) ** 2)
            if jump <= t < jump + 0.9:                # leaps clear of the water once
                u = (t - jump) / 0.9
                bright = bright + 0.6 * np.sin(np.pi * u)
                pos = hook - 70 * u
                body = np.exp(-((x - pos) / size) ** 2)
            buf += light(FISH, bright * body)

        # it was THIS big
        if 58 <= t < 72:
            ctr = x[381] + 230
            half = keys(t, [(58.3, 20), (59.4, 60), (60.4, 60), (61.3, 130), (62.3, 130), (63.2, 230),
                            (64.6, 230)])
            on = keys(t, [(58, 0), (58.4, 1), (69, 1), (70.5, 0)])
            right = min(ctr + half, x[500] - 4)
            left = ctr - half if t < 64.6 else keys(t, [(64.6, ctr - 230), (66.6, 8)])
            buf += light(HANDS, 0.7 * on * (np.exp(-((x - left) / 7) ** 2) + np.exp(-((x - right) / 7) ** 2)))
            if t > 64.6:
                between = (x > left) & (x < right)
                buf += light(HANDS, 0.08 * on * between)

        out[f][G.path] = np.clip(buf, 0, 1)
    return out
