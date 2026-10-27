"""Egg Roll: A race between two painted eggs, in mirror-image lanes: pink from the front-left
corner, blue from the free right end, both rolling to a finish line in the middle of the porch.
The eggs really roll: the painted dots on each shell are points on a circle turning with the
distance covered, so they sweep over the egg and vanish round the far side, and an egg that rocks
in place shows its dots rocking too. Pink spins out at a corner; blue leads, then wobbles just
short of the line; they touch at the line together: photo finish. Meanwhile a tiny golden egg has
been creeping from the far back of the house the whole time. It arrives, taps pink from behind,
and like a Newton's cradle the knock goes through pink into blue, which rolls clean off the
end of the house. Blue comes back, sheepishly, at the end."""
import numpy as np
from pixelhome.fx import DT, hexc, light, keys, smoothstep, nframes

CODE = 'EA07'
TITLE = 'Egg Roll'
KIND = 'show'
DESCRIPTION = 'Two painted eggs race in mirrored lanes to the porch, dots turning as they roll. Photo finish, until a tiny golden egg from the back of the house taps them like a Newton\'s cradle.'


def lin(h):
    return hexc(h) ** 2.2


PINK, PINK_DOT = lin('#ff7fb2'), lin('#fff3a0')
BLUE, BLUE_DOT = lin('#7fc4ff'), lin('#ffffff')
GOLD, GOLD_DOT = lin('#ffc93a'), lin('#ff8a3a')
LINE = lin('#fff2d0')
CHIME = lin('#c9a8ff')
CONFETTI = [lin(h) for h in ('#ff8fbf', '#ffe17a', '#7ff0bd', '#b99cff', '#8fcfff')]


def rock(t, t0, amp, period, tau):
    if t < t0:
        return 0.0
    a = t - t0
    return amp * np.exp(-a / tau) * np.sin(2 * np.pi * a / period)


def leg(t, ta, tb, sa, sb, speed):
    """Position on a leg from (ta, sa) to (tb, sb) whose speed follows the shape speed(u), u in 0..1."""
    u = np.linspace(0, 1, 201)
    c = np.concatenate([[0], np.cumsum((speed(u[1:]) + speed(u[:-1])) / 2)])
    return sa + (sb - sa) * float(np.interp((t - ta) / (tb - ta), u, c / c[-1]))


def render(G, seed=27):
    rng = np.random.default_rng(seed)
    D = 60.0
    F = nframes(D)
    out = np.zeros((F, G.N, 3))
    pdp = G.pd[G.path]
    n = G.N
    R = 13.0                           # egg half-length on the roof
    FIN = 1485.0
    sL0 = pdp[81] + 16
    sR0 = G.length - 16

    def pink(t):
        s = leg(t, 4.5, 11.4, sL0, pdp[178] - 4, lambda u: smoothstep(0, 0.2, u) * (1 - 0.35 * u))
        if t >= 11.4:
            s = pdp[178] - 4 + rock(t, 11.4, -16, 0.7, 0.6)           # spins out at the corner
        if t >= 13.4:
            s = leg(t, 13.4, 20.8, pdp[178] - 4, FIN - 2 * R, lambda u: smoothstep(0, 0.12, u) * (1.25 - 0.5 * u))
        if t >= 37.0:
            s = keys(t, [(37.0, FIN - 2 * R), (38.6, FIN + 4)])          # nudged over the line
        return s

    def blue(t):
        s = leg(t, 4.5, 19.0, sR0, FIN + 2 * R + 26, lambda u: smoothstep(0, 0.12, u) * smoothstep(1.0, 0.8, u) *
                (1.2 - 0.4 * u))
        if 19.0 <= t < 20.9:
            s = FIN + 2 * R + 26 + rock(t, 19.0, -14, 0.55, 0.9)        # wobbles just short
        if t >= 20.9:
            s = FIN + (2 * R + 26) * (1 - smoothstep(20.9, 21.0, t))
        if t >= 36.2:                                                    # the knock carries through
            a = t - 36.2
            s = FIN + 250 * 6 * (1 - np.exp(-a / 6))
        if t >= 45.0:
            s = leg(t, 45.0, 54.5, G.length + 40, FIN + 2 * R + 5, lambda u: smoothstep(1.0, 0.6, u) + 0.05)
        return s

    def gold(t):
        """Slow and steady, at constant speed the whole race, a little push at the end."""
        s = float(np.interp(t, [4.5, 34.5], [-10.0, FIN - 4 * R - 40]))
        if t >= 34.5:
            s = leg(t, 34.5, 36.2, FIN - 4 * R - 40, FIN - 4 * R, lambda u: 1 + u)
        if t >= 37.0:
            s = keys(t, [(37.0, FIN - 4 * R), (38.6, FIN + 4 - 2 * R)])
        return s

    eggs = [(pink, PINK, PINK_DOT, 1.0), (blue, BLUE, BLUE_DOT, 1.0), (gold, GOLD, GOLD_DOT, 0.62)]
    lane_l = (pdp >= sL0 - 20) & (pdp <= FIN)
    lane_r = (pdp >= FIN) & (pdp <= sR0 + 20)

    for f in range(F):
        t = f * DT
        buf = np.zeros((n, 3))
        on = keys(t, [(0, 0), (1.0, 1), (57.5, 1), (60, 0)])
        frozen = 21.0 <= t < 23.5
        tt = 21.0 if frozen else t
        buf += light(PINK, 0.1 * on * lane_l) + light(BLUE, 0.1 * on * lane_r)
        buf += light(LINE, 0.55 * on * np.exp(-((pdp - FIN) / 3) ** 2))

        # countdown: two soft chimes and a bright "go" spreading from the line
        for t0, amp, col in ((1.6, 0.4, CHIME), (2.8, 0.4, CHIME), (4.0, 0.8, GOLD)):
            a = t - t0
            if 0 <= a < 1.2:
                buf += light(col, amp * np.exp(-a / 0.35) * np.exp(-((pdp - FIN) / (20 + 260 * a)) ** 2))

        for fn, c1, c2, sc in eggs:
            s = fn(t if fn is gold else tt)
            r = R * sc
            u = (pdp - s) / r
            m = np.abs(u) < 1.3
            if not m.any():
                continue
            theta = (s - fn(4.5)) / (0.75 * r)                     # rolling: angle follows distance
            env = np.clip(1 - u[m] ** 2, 0, 1) ** 0.5
            col = light(c1, 0.8 * env * (1 + 0.08 * np.sin(2 * theta)))
            for k in range(4):
                ph = theta + k * np.pi / 2
                front = np.cos(ph)
                if front <= 0:
                    continue
                p = np.sin(ph) * 0.8
                col += light(c2, 0.85 * front * np.exp(-((u[m] - p) / 0.17) ** 2) * env)
            buf[m] = buf[m] * 0.3 + col

        # photo finish: a flash on the porch only, then the frame holds
        a = t - 21.0
        if 0 <= a < 0.6:
            pf = np.exp(-((pdp - FIN) / 170) ** 2)
            buf += light(lin('#ffffff'), 0.8 * np.exp(-a / 0.08) * pf)
        if frozen:                                                 # judges study the line
            buf += light(LINE, 0.5 * (0.5 - 0.5 * np.cos(2 * np.pi * a / 0.8)) * np.exp(-((pdp - FIN) / 2.5) ** 2))

        # the knock: a bright tap where gold meets pink, and where pink meets blue
        for t0, p in ((36.2, FIN - 3 * R), (36.25, FIN - R)):
            a = t - t0
            if 0 <= a < 0.5:
                buf += light(lin('#fff6d8'), 0.9 * np.exp(-a / 0.07) * np.exp(-((pdp - p) / 6) ** 2))

        # celebration on the porch
        if 38.6 < t < 46:
            a = t - 38.6
            k = int(t * 12)
            r2 = np.random.default_rng(k)
            spots = r2.uniform(pdp[261], pdp[331], 6)
            for j, sp in enumerate(spots):
                ph = (t * 12) % 1
                buf += light(CONFETTI[(k + j) % 5], 0.6 * np.sin(np.pi * ph) * smoothstep(0, 0.5, a) *
                             smoothstep(7.4, 5, a) * np.exp(-((pdp - sp) / 4) ** 2))
        out[f][G.path] = buf * on
    return out
