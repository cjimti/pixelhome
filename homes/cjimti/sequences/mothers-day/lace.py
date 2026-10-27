"""Lace: A Gray-Scott reaction-diffusion runs along the roofline on a uniform grid in path distance
(so the pattern is even across runs of different pixel spacing). Its spots replicate and split like
crochet stitches. The feed rate is not constant: two broad bands of 'thread' drift slowly in
opposite directions round the house, so lace is worked where they pass and frays and dissolves
behind them, while the five corners are always fed and keep a knot of lace each."""
import numpy as np
from pixelhome.fx import DT, hexc, light, smoothstep, colormap, nframes, looped

CODE = 'MO09'
TITLE = 'Lace'
KIND = 'ambient'
DESCRIPTION = 'A living lace: reaction-diffusion stitches split and spread where slow bands of thread drift round the house, fray behind them, and knot at the corners.'

FLOOR_COLOR = hexc('#c898ff')
FLOOR = 0.09
LOOP = 150.0
CELL = 4.0
STEPS = 2            # reaction-diffusion steps per frame
WARM = 4000
F_LO, F_HI = 0.012, 0.045


def render(G, seed=29):
    rng = np.random.default_rng(seed)
    x = G.pd[G.path]
    L = G.length
    names = [s for s, _ in G.path_segments()]
    ends = [G.pd[G.seg[s]] for s in names]
    corners = np.array([0.5 * (a.max() + b.min()) for a, b in zip(ends[:-1], ends[1:])])
    gx = np.arange(0, L + CELL, CELL)
    C = len(gx)
    knot = np.exp(-((gx[:, None] - corners[None, :]) / 30) ** 2).max(1)
    cmap = colormap([(0, hexc('#9a70ff')), (0.35, hexc('#ff70b0')), (0.7, hexc('#ffa890')), (1, hexc('#fff0e0'))])
    Du, Dv, K = 0.45, 0.22, 0.06

    def feed(t):
        ph = 2 * np.pi * t / LOOP
        a = 0.5 + 0.5 * np.cos(2 * np.pi * gx / L - ph)
        b = 0.5 + 0.5 * np.cos(2 * np.pi * gx / L + ph + 1.3)
        band = np.maximum(a, b) ** 3
        return F_LO + (F_HI - F_LO) * np.maximum(band, 0.9 * knot)

    def lap(a):
        o = np.empty_like(a)
        o[1:-1] = a[2:] - 2 * a[1:-1] + a[:-2]
        o[0] = a[1] - a[0]
        o[-1] = a[-2] - a[-1]
        return o

    def step(u, v, F):
        uvv = u * v * v
        u += Du * lap(u) - uvv + F * (1 - u)
        v += Dv * lap(v) + uvv - (F + K) * v

    def draw(D):
        out = np.zeros((nframes(D), G.N, 3), np.float32)
        u = np.ones(C)
        v = np.zeros(C)
        for c in rng.integers(10, C - 10, 14):
            v[c - 3:c + 3] = 0.5
            u[c - 3:c + 3] = 0.25
        F0 = feed(0.0)
        for _ in range(WARM):
            step(u, v, F0)
        sv = v.copy()
        for f in range(len(out)):
            t = f * DT
            F = feed(t)
            for _ in range(STEPS):
                step(u, v, F)
            # keep the lace from dying out entirely: reseed a faint stitch where feed is high
            if f % 200 == 0 and v.max() < 0.15:
                c = int(np.argmax(F))
                v[c - 3:c + 3] = 0.5
            sv += (v - sv) * 0.25                          # gentle temporal smoothing
            val = np.interp(x, gx, sv)
            thread = np.interp(x, gx, (F - F_LO) / (F_HI - F_LO))
            s = smoothstep(0.04, 0.36, val)
            I = 0.05 + 0.33 * s + 0.04 * thread
            out[f][G.path] = light(cmap(0.15 + 0.4 * s + 0.35 * thread * s), I)
        return out
    return looped(draw, LOOP, floor=(FLOOR, FLOOR_COLOR))
