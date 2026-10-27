"""Power Restored: A storm knocks the house out and a lineworker brings it back one span at a time.

Warm porch lights, then rain and wind, two flashes of lightning; the second strikes the Porch Front
and the outage cascades out from the strike. In the dark rain a bucket truck's amber beacon comes in
off the free right end and works back along the roofline. At each junction the lineworker's
headlamp bobs and small arcs spit, then the switch closes: power runs down the span from the feed
end, overshoots and settles, and every span already lit sags for a moment under the new load. The
Porch Front comes on, flickers, pops in a shower of sparks and needs a second go and a good whack.
When the Side is back the rain stops and the truck drives out under a fully lit house."""
import numpy as np
from pixelhome.fx import DT, hexc, light, smoothstep, keys, smooth_noise, Flicker, nframes

CODE = 'LB07'
TITLE = 'Power Restored'
KIND = 'show'
DESCRIPTION = ('Lightning knocks the house out. A bucket truck works back along the roof and power returns span '
               'by span, sagging under each new load. The porch pops on the first try.')

WARM = hexc('#ffb260')
RAIN = hexc('#7d9cc8')
FLASH = hexc('#dcd8ff')
BOLT = hexc('#f4f0ff')
AMBER = hexc('#ff8a00')
LAMP = hexc('#fffaf0')
ARC = hexc('#bcd0ff')
SPARK = hexc('#ffb040')
SMOKE = hexc('#9aa0a8')

ON_LEVEL = 0.5


def render(G, seed=27):
    rng = np.random.default_rng(seed)
    D = 62.0
    F = nframes(D)
    out = np.zeros((F, G.N, 3))
    s = G.pd[G.path]
    L = G.length
    P3 = G.pos[G.path]
    pi = np.arange(G.N)

    # spans in the order they come back: (path index range, feed end path index)
    spans = [((381, 500), 381), ((332, 380), 380), ((261, 331), 331), ((179, 260), 260), ((81, 178), 178),
             ((0, 80), 80)]
    feeds = [s[fe] for _, fe in spans]
    masks = [(pi >= a) & (pi <= b) for (a, b), _ in spans]
    span_len = [abs(s[b] - s[a]) for (a, b), _ in spans]

    # switch-on times (Porch Front needs two tries)
    t_on = [23.0, 27.0, 36.2, 40.2, 43.7, 47.6]
    T_POP_ON, T_POP = 31.0, 32.0
    work = [(20.0, 23.0), (25.0, 27.0), (29.3, 31.0), (38.5, 40.2), (42.0, 43.7), (45.9, 47.6)]
    work_retry = (33.0, 36.2)
    truck = [(16.0, L + 30), (20.0, feeds[0]), (24.0, feeds[0]), (25.0, feeds[1]), (27.5, feeds[1]),
             (29.3, feeds[2]), (36.8, feeds[2]), (38.5, feeds[3]), (40.6, feeds[3]), (42.0, feeds[4]),
             (44.2, feeds[4]), (45.9, feeds[5]), (50.0, feeds[5]), (57.5, L + 60)]
    switch_events = list(t_on) + [T_POP_ON]

    T_L1, T_L2 = 6.2, 9.4
    strike = s[296]
    d_strike = np.linalg.norm(P3 - P3[296], axis=1)
    t_die = T_L2 + 0.15 + d_strike / 900 + 0.35 * smooth_noise(rng, s, 90)
    die_fl = Flicker(rng, G.N, 6, 13)
    hum = Flicker(rng, G.N, 0.2, 0.8)
    sparks = None

    def span_level(k, t):
        """Perceptual level of span k at time t (0 when dead)."""
        m = masks[k]
        lvl = np.zeros(G.N)
        dist = np.abs(s - feeds[k])
        tries = [t_on[k]] if k != 2 else [T_POP_ON, t_on[k]]
        for j, ts in enumerate(tries):
            u = t - ts
            if u < 0:
                continue
            if k == 2 and j == 0 and t >= T_POP:
                continue
            front = smoothstep(dist - 5, dist + 5, u * 1500)
            settle = 1 + 0.7 * np.exp(-u / 0.22) * np.cos(2 * np.pi * 6 * u)
            if k == 2 and j == 0:                     # the bad try: unsteady, getting worse
                settle *= 1 - 0.55 * np.clip(rng.random(), 0, 1) * smoothstep(0.2, 0.9, u)
            if k == 2 and j == 1 and u < 0.9:         # one hesitation, then good
                settle *= 1 - 0.6 * np.exp(-((u - 0.45) / 0.06) ** 2)
            lvl = np.maximum(lvl, ON_LEVEL * front * settle * m)
        return lvl

    for f in range(F):
        t = f * DT
        buf = np.zeros((G.N, 3))
        storm = keys(t, [(2.0, 0), (5.0, 1), (46, 1), (51, 0)])

        # before the storm, and the outage
        before = ON_LEVEL * (1 + 0.02 * hum(t))
        if t < T_L2:
            lvl = np.full(G.N, before) * smoothstep(0, 1.5, t)
        else:
            u = t - t_die
            dying = np.where(u < 0, 1.0, np.where(u < 0.7, np.clip(0.5 + 0.6 * die_fl(t), 0, 1) * (1 - u / 0.7), 0))
            lvl = before * dying
        for k in range(len(spans)):
            lvl = np.maximum(lvl, span_level(k, t))
        # load sag on what is already on
        sag = sum(0.45 * np.exp(-(t - ts) / 0.45) for ts in switch_events if 0.05 < t - ts < 3)
        lvl = lvl * (1 - sag * (lvl > 0.2))
        if t > 50:                                    # all back, and the porch lights relax brighter
            lvl *= 1 + 0.15 * smoothstep(50, 54, t)
        buf += light(WARM, lvl)

        # rain: brief cool drops, pushed along by gusts
        if storm > 0:
            gust = 0.6 + 0.4 * np.sin(P3[:, 0] / 160 - 1.7 * t) * np.sin(P3[:, 2] / 210 + 0.6 * t)
            drop = rng.random(G.N) < 0.07 * storm * gust
            buf += light(RAIN, 0.42 * drop * rng.uniform(0.4, 1.0, G.N))
            buf += light(RAIN, 0.05 * storm * (lvl < 0.1))

        # lightning: sky flashes (brief), the second one hits the porch
        for tl, strength in ((T_L1, 0.55), (T_L2, 0.85)):
            u = t - tl
            if 0 <= u < 0.45:
                fl = np.exp(-u / 0.05) + 0.7 * np.exp(-((u - 0.2) / 0.04) ** 2)
                buf += light(FLASH, strength * fl * (0.6 + 0.4 * (-P3[:, 2] / 640)))
        u = t - T_L2
        if 0 <= u < 0.6:
            buf += light(BOLT, (1.2 * np.exp(-u / 0.15)) * np.exp(-(np.abs(s - strike) / 14) ** 1.5))

        # the truck: amber beacon, rotating
        if 16 <= t < 57.5:
            x = keys(t, truck)
            rot = 0.5 + 0.5 * np.cos(2 * np.pi * 1.4 * t)
            buf += light(AMBER, (0.25 + 0.6 * rot ** 4) * np.exp(-((s - x) / 6) ** 2))
            buf += light(AMBER, 0.15 * rot ** 4 * np.exp(-np.abs(s - x) / 70))
        # the lineworker at each junction: headlamp bobbing up the pole, arcs spitting
        for (a, b) in work + [work_retry]:
            if a <= t < b:
                k = 2 if (a, b) == work_retry else work.index((a, b))
                fx = feeds[k]
                direction = np.sign(s[masks[k]].mean() - fx)
                bob = fx + direction * (10 + 6 * np.sin(2 * np.pi * 0.9 * (t - a)))
                buf += light(LAMP, 0.55 * np.exp(-((s - bob) / 3.5) ** 2))
                if rng.random() < 0.18:
                    buf += light(ARC, rng.uniform(0.5, 1.0) * np.exp(-((s - fx) / 3) ** 2))
                if (a, b) == work_retry:              # the whack
                    w = t - 35.4
                    if 0 <= w < 0.3:
                        buf += light(LAMP, 0.6 * np.exp(-w / 0.08) * np.exp(-((s - fx) / 25) ** 2))

        # the pop
        if t >= T_POP:
            u = t - T_POP
            if sparks is None:
                n = 36
                sparks = (s[296] + rng.normal(0, 30, n), rng.normal(0, 260, n), rng.uniform(0.4, 1.2, n))
            x0, v0, tau = sparks
            if u < 3:
                xs = x0 + v0 * 0.5 * (1 - np.exp(-u / 0.5))
                T = np.exp(-u / tau)
                w = np.exp(-((s[None] - xs[:, None]) / 3.5) ** 2) * T[:, None]
                buf += light(SPARK, np.clip(w.sum(0), 0, 1.2))
                buf += light(LAMP, 0.9 * np.exp(-u / 0.08) * masks[2])
                buf += light(SMOKE, 0.25 * np.exp(-u / 0.9) * np.exp(-((s - s[296]) / (40 + 60 * u)) ** 2))
        buf *= 1 - smoothstep(D - 3, D, t)
        out[f][G.path] = np.clip(buf, 0, 1)
    return out
