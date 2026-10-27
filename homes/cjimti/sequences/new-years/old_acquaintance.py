"""Old Acquaintance: The roof is a string, and a real wave equation runs along it. The wave speed in
each run follows its pixel spacing, so every corner is a change of medium: each gentle swell
entering at the free right end (the new year arriving) is partly passed, partly echoed at every
corner, and the echoes cross and interfere. At the free back end of the house the string is
absorbing, so whatever reaches it slips away for good. Gold swells up, silver swells down. Dim and
slow, all night."""
import numpy as np
from pixelhome.fx import DT, hexc, perc, nframes, looped

CODE = 'NY10'
TITLE = 'Old Acquaintance'
KIND = 'ambient'
DESCRIPTION = 'A wave equation on the roof: slow swells enter at the right end, echo at every corner where the medium changes, and slip away out the back of the house.'

GOLD = hexc('#ffa828')
SILVER = hexc('#a8c0ff')
BED = hexc('#3a3a78')
FLOOR_COLOR = hexc('#303070')
FLOOR = 0.11
LOOP = 150.0
CELL = 5.0


def render(G, seed=30):
    rng = np.random.default_rng(seed)
    pdp = G.pd[G.path]
    L = G.length
    M = int(L / CELL) + 1
    xs = np.linspace(0, L, M)
    dx = xs[1] - xs[0]
    # wave speed per cell from the local pixel spacing of the run it lies in
    spacing = np.gradient(pdp)
    c = np.interp(xs, pdp, 6.0 * spacing ** 1.7)            # contrast exaggerated so corners echo
    c = np.convolve(np.pad(c, 3, mode='edge'), np.ones(7) / 7, mode='valid')
    sub = int(np.ceil(DT * c.max() / dx / 0.8))
    h = DT / sub
    r2 = (c * h / dx) ** 2
    gamma = 0.04

    def draw(D):
        n = G.N
        out = np.zeros((nframes(D), n, 3), np.float32)
        u = np.zeros(M)
        up = np.zeros(M)
        swells = []
        t = 2.0
        sign = 1
        while t < D + 10:
            swells.append((t, sign * rng.uniform(0.6, 1.0), rng.uniform(0.9, 1.6)))
            sign = -sign if rng.random() < 0.7 else sign
            t += rng.uniform(6, 11)

        def source(t):
            return sum(a * np.exp(-((t - t0) / w) ** 2) for t0, a, w in swells if abs(t - t0) < 4 * w)

        k_mur = (c[0] * h - dx) / (c[0] * h + dx)
        for f in range(len(out)):
            t = f * DT
            for s in range(sub):
                ts = t + s * h
                un = np.empty(M)
                un[1:-1] = (2 * u[1:-1] - up[1:-1] * (1 - gamma * h) +
                            r2[1:-1] * (u[2:] - 2 * u[1:-1] + u[:-2])) / (1 + gamma * h)
                un[-1] = source(ts)                                  # the right free end is driven
                un[0] = u[1] + k_mur * (un[1] - u[0])                # the back free end absorbs
                up, u = u, un
            w = np.interp(pdp, xs, u)
            pos = np.clip(w, 0, None)
            neg = np.clip(-w, 0, None)
            col = np.tile(perc(0.15) * BED, (n, 1))
            col = col + perc(0.38 * np.tanh(1.6 * pos))[:, None] * GOLD + perc(0.34 * np.tanh(1.6 * neg))[:, None] * SILVER
            out[f][G.path] = col
        return out
    return looped(draw, LOOP, floor=(FLOOR, FLOOR_COLOR))
