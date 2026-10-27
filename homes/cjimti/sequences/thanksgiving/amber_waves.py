"""Amber Waves: The whole roofline is a strip of wheat field, simulated as a damped wave equation along
the path. Slow gusts of wind push across it; the stalks bend and spring back, and the bending travels
on as waves that turn the corners, bounce back from the two free ends and pass through each other.
Each run of the roof carries waves at its own speed, so a little of every wave reflects at each corner.
Stalks leaning one way catch the low gold light, leaning the other way they fall into amber shadow."""
import numpy as np
from pixelhome.fx import DT, hexc, light, Flicker, nframes, looped

CODE = 'TG10'
TITLE = 'Amber Waves'
KIND = 'ambient'
DESCRIPTION = ('The roof is a strip of wheat field. Slow gusts bend it, and the bending rolls on as waves that turn '
               'the corners, echo off the free ends and cross each other, gold on one side, amber shadow on the other.')

GOLD = hexc('#ffb428')
AMBER = hexc('#ff6a10')
SHADE = hexc('#8a2a06')
FLOOR_COLOR = hexc('#a03008')
FLOOR = 0.11
LOOP = 170.0


def render(G, seed=30):
    rng = np.random.default_rng(seed)
    pdp = G.pd[G.path]
    n = G.N
    dx = 5.0
    xs = np.arange(0, G.length + dx, dx)
    M = len(xs)
    # wave speed per run of the roof (impedance steps at the corners)
    bounds = [0, 491, 894, 1311, 1660, 2033, G.length + 10]
    speeds = [120, 95, 135, 105, 140, 100]
    c = np.zeros(M)
    for (a, b), s in zip(zip(bounds[:-1], bounds[1:]), speeds):
        c[(xs >= a) & (xs < b)] = s
    c = np.convolve(np.pad(c, 3, mode='edge'), np.ones(7) / 7, 'valid')   # soften the steps a little
    SUB = 4
    dt = DT / SUB
    gamma = 0.12

    def draw(Dt):
        out = np.zeros((nframes(Dt), n, 3), np.float32)
        u = np.zeros(M)
        v = np.zeros(M)
        shimmer = Flicker(rng, n, 0.05, 0.25)
        gusts = []
        t = 0.0
        while t < Dt:
            d = rng.choice([-1, 1])
            gusts.append((t, rng.uniform(0, G.length), d, rng.uniform(60, 110), rng.uniform(0.5, 1.0),
                          rng.uniform(5, 9)))
            t += rng.uniform(5, 11)
        for f in range(len(out)):
            t = f * DT
            force = np.zeros(M)
            for tg, x0, d, sp, a, life in gusts:
                s = t - tg
                if 0 < s < life:
                    env = np.sin(np.pi * s / life) ** 2
                    q = (xs - x0 - d * sp * s) / 140
                    force += a * env * (np.exp(-q ** 2) - 1.6 * q * np.exp(-q ** 2) * d) * 0.8
            for _ in range(SUB):
                lap = np.empty(M)
                lap[1:-1] = u[2:] - 2 * u[1:-1] + u[:-2]
                lap[0] = 2 * (u[1] - u[0])                 # free ends: waves reflect
                lap[-1] = 2 * (u[-2] - u[-1])
                acc = (c ** 2) * lap / dx ** 2 - gamma * v - 0.05 * u + 2.2 * force
                v += acc * dt
                u += v * dt
            w = np.interp(pdp, xs, u)
            lean = np.tanh(w * 1.1)
            I = 0.24 + 0.14 * lean + 0.02 * shimmer(t)
            hi = np.clip(lean, 0, 1)[:, None]
            lo = np.clip(-lean, 0, 1)[:, None]
            col = AMBER + (GOLD - AMBER) * hi + (SHADE - AMBER) * lo * 0.7
            out[f][G.path] = light(1.0, np.clip(I, 0.05, 0.42)) * col
        return out
    return looped(draw, LOOP, floor=(FLOOR, FLOOR_COLOR))
