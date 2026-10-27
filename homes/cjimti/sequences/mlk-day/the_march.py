"""The March: A small line of marchers enters at the free back end of Side and walks the roof. At the
corner where Left meets Porch Left (the bridge) a cold blue line stops them and pushes them back; their
lights dim to embers but do not go out. Then the wall dissolves, the line re-forms, people keep
arriving from the back and stepping in from the roadside, and a procession many times larger crosses
the porch and walks all the way to the free end of Right, where it closes up into one continuous light.

Each marcher is an agent with its own pace that follows the one ahead at a walking gap (a vectorized
follow-the-leader with a hard minimum spacing), drawn with sub-pixel falloff and a gentle step bob."""
import numpy as np
from pixelhome.fx import DT, hexc, perc, light, keys, lerp, smoothstep, Flicker, nframes

CODE = 'MK01'
TITLE = 'The March'
KIND = 'show'
DESCRIPTION = ('A few marchers set out from the back of the house and are turned back at the bridge. They return '
               'many times stronger, gather people along the way, and walk the whole roof to the far end.')

ROAD = hexc('#1028ff')
WARM = hexc('#ffb468')
GOLD = hexc('#ff9420')
EMBER = hexc('#ff5010')
WALL = hexc('#2038ff')
DAWN = hexc('#ffc890')


def render(G, seed=21):
    rng = np.random.default_rng(seed)
    D = 86.0
    F = nframes(D)
    out = np.zeros((F, G.N, 3))
    pdp = G.pd[G.path]
    L = G.length
    bridge = G.pd[G.path[179]]            # first pixel of Porch Left: the foot of the bridge
    END = L - 6

    # roadside joiners: people waiting along the second half of the route
    join_s = np.sort(rng.uniform(bridge + 60, L - 120, 34))
    join_done = np.zeros(len(join_s), bool)
    join_ph = rng.uniform(0, 2 * np.pi, len(join_s))

    s = np.zeros(0)            # positions, leader first (descending)
    vmax = np.zeros(0)
    ph = np.zeros(0)
    tone = np.zeros(0)
    bright = np.zeros(0)
    GAP = 13.0
    bob = Flicker(rng, G.N, 0.08, 0.3)

    def add(pos, idx=None):
        nonlocal s, vmax, ph, tone, bright
        k = len(s) if idx is None else idx
        s = np.insert(s, k, pos)
        vmax = np.insert(vmax, k, rng.uniform(56, 64))
        ph = np.insert(ph, k, rng.uniform(0, 2 * np.pi))
        tone = np.insert(tone, k, rng.uniform(0, 1))
        bright = np.insert(bright, k, 0.0)

    next_spawn = 3.0
    for f in range(F):
        t = f * DT
        fr = out[f]
        buf = np.zeros((G.N, 3))

        # the road: a faint deep-blue line, warming once the march has passed
        roadI = keys(t, [(0, 0), (2.5, 0.07), (80, 0.07), (86, 0)])
        buf += light(ROAD, roadI * np.ones(G.N))

        # spawning at the back free end
        spawning = 3 <= t < 13 or 31 <= t < 60
        rate = 0.85 if t < 13 else keys(t, [(31, 0.5), (40, 0.24)])
        if spawning and t >= next_spawn:
            if len(s) == 0 or s[-1] > -16 + GAP:
                add(-16.0)
            next_spawn = t + rate

        # wall at the bridge
        wallI = keys(t, [(15, 0), (20, 0.55), (24, 0.6), (25, 0.85), (27, 0.7), (31, 0.55), (35.5, 0)])
        wall_front = keys(t, [(0, bridge + 2), (24.3, bridge + 2), (25.6, bridge - 150), (28.5, bridge - 120),
                              (32, bridge + 2)])
        surge = smoothstep(24.0, 25.0, t) * (1 - smoothstep(26.5, 30.0, t))
        hurt = smoothstep(24.5, 26.0, t) * (1 - smoothstep(31.5, 36.0, t))

        if len(s):
            # follow the leader
            lead_v = keys(t, [(3, 40), (40, 52), (66, 52), (72, 30)])
            prev = np.concatenate([[np.inf], s[:-1]])
            gap = prev - s
            v = np.clip(1.8 * (gap - GAP), 0, vmax)
            v[0] = lead_v
            v *= 1 - 0.85 * hurt
            v *= 1 + 0.06 * np.sin(2 * np.pi * 1.0 * t + ph)
            s = s + v * DT
            limit = END if t > 33 else (wall_front - 8 if wallI > 0.01 else END)
            s = np.minimum(s, limit)
            # pushed back: the wall front drags those it reaches; hard minimum spacing behind
            gmin = lerp(GAP * 0.85, 6.0, surge)
            i = np.arange(len(s))
            s = np.minimum.accumulate(s + i * gmin) - i * gmin
            bright = np.minimum(1, bright + DT / 0.8)

            # roadside joiners step in when the head passes them
            for j in np.nonzero(~join_done & (join_s < s[0] - 20))[0]:
                k = int(np.searchsorted(-s, -join_s[j]))
                add(join_s[j], k)
                bright[k] = 0.6
                join_done[j] = True

            # draw marchers
            step = 0.82 + 0.18 * np.sin(2 * np.pi * 1.7 * t + ph)
            amp = step * bright * lerp(1.0, 0.32, hurt)
            col = lerp(WARM[None], GOLD[None], tone[:, None])
            col = lerp(col, EMBER[None], hurt * 0.7)
            d = pdp[:, None] - s[None, :]
            k = np.exp(-(d / 4.8) ** 2)
            I = k * (0.95 * amp)[None, :]
            buf += perc(np.clip(I, 0, 1)) @ col
            # a soft halo where people walk close together (local density, not a block)
            dens = np.exp(-(d / 26) ** 2).sum(1)
            buf += light(GOLD, 0.2 * np.clip(dens / 3.5, 0, 1) * (1 - hurt) * bright.mean())

        # the wall: cold light at the foot of the bridge, leaning into the marchers during the surge
        wd = pdp - wall_front
        wshape = np.where(wd > 0, np.exp(-(wd / 55) ** 2), np.exp(-(wd / 9) ** 2))
        wshape *= 0.85 + 0.15 * bob(t)[G.path]
        buf += light(WALL, wallI * wshape)

        # roadside joiners waiting: small dim golden glints
        wait = keys(t, [(30, 0), (36, 1)])
        for j in np.nonzero(~join_done)[0]:
            g = np.exp(-((pdp - join_s[j]) / 3.0) ** 2)
            buf += light(GOLD, wait * (0.22 + 0.06 * np.sin(1.3 * t + join_ph[j])) * g)

        # arrival: the closed-up line becomes one continuous light, which then runs back along the
        # whole road it walked, all the way to the back of Side
        one = keys(t, [(68, 0), (74, 1), (82, 1), (86, 0)])
        if one > 0 and len(s):
            back = keys(t, [(73, s[-1] if len(s) else 0), (80, -40)])
            span = smoothstep(back - 40, back + 10, pdp)
            buf += light(DAWN, 0.4 * one * span)
        arr = keys(t, [(64, 0), (70, 1), (82, 1), (86, 0)])
        buf += light(GOLD, 0.55 * arr * np.exp(-((L - pdp) / 60) ** 2))

        fade = keys(t, [(0, 1), (82, 1), (86, 0)])
        fr[G.path] = buf * fade
    return out
