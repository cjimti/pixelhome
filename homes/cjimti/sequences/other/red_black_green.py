"""Red, Black and Green: A living pattern grown on the roofline by Gray-Scott reaction-diffusion along the
continuous path (Laplacian in real distance, so every run grows at the same scale and patterns flow
around the corners; the two free ends are closed walls). A slow wave in the feed rate and a gentle drift
carry the red cells along the roof, where they divide, merge and starve; the porch, set back, is fed
richer and holds its cells steadier than the wings. Reacting fronts read red, the resting medium green, the borders between them black."""
import numpy as np
from pixelhome.fx import DT, hexc, perc, smoothstep, lerp, Flicker, nframes, looped

CODE = 'OT18'
TITLE = 'Red, Black and Green'
KIND = 'ambient'
DESCRIPTION = ('A slow living pattern grown along the roof by reaction-diffusion: red cells drift, divide and merge, '
               'edged in black, in a field of green.')

RED = hexc('#ff1020')
GREEN = hexc('#10c040')
FLOOR_COLOR = hexc('#0a5020')
FLOOR = 0.07
LOOP = 160.0


def render(G, seed=8):
    rng = np.random.default_rng(seed)

    def draw(D):
        n = G.N
        out = np.zeros((nframes(D), n, 3), np.float32)
        pdp = G.pd[G.path]
        z = G.pos[G.path, 2]
        h = np.maximum(np.diff(pdp) / 4.0, 1.0)          # spacing in units of the tightest run (corners clamped)
        hm = np.concatenate([[h[0]], h])                 # left spacing per node
        hp = np.concatenate([h, [h[-1]]])                # right spacing per node
        depth = smoothstep(-200, -560, z)                # 0 at the wing fronts, 1 on the porch front
        F0 = lerp(0.036, 0.040, depth)                   # porch: richer feed, steadier cells
        K = 0.0605
        F = F0.copy()
        it = [0]
        Du, Dv = 1.0, 0.5
        u = np.ones(n)
        v = np.zeros(n)
        for c in rng.uniform(0, G.length, 12):
            m = np.abs(pdp - c) < 12
            u[m], v[m] = 0.5, 0.25 + 0.05 * rng.random(m.sum())

        def lap(a):
            l = np.empty_like(a)
            l[1:-1] = 2 * ((a[2:] - a[1:-1]) / hp[1:-1] - (a[1:-1] - a[:-2]) / hm[1:-1]) / (hp[1:-1] + hm[1:-1])
            l[0] = 2 * (a[1] - a[0]) / hp[0] ** 2              # closed ends
            l[-1] = 2 * (a[-2] - a[-1]) / hm[-1] ** 2
            return l

        dt = 0.4

        def step(k):
            nonlocal u, v
            nonlocal F
            for _ in range(k):
                it[0] += 1
                # a slow travelling wave in the feed rate pushes cells along, splits some, starves others
                ph = it[0] / 8000
                F = F0 + 0.006 * np.sin(2 * np.pi * (pdp / 900 - ph))
                # and a slow drift carries the cells along the roof, converging and parting
                c = 0.05 * np.sin(2 * np.pi * (pdp / 1250 + 0.5 * ph))
                du = np.where(c > 0, u - np.roll(u, 1), np.roll(u, -1) - u)
                dv = np.where(c > 0, v - np.roll(v, 1), np.roll(v, -1) - v)
                du[0] = du[-1] = dv[0] = dv[-1] = 0
                u = u - dt * c * du / hm
                v = v - dt * c * dv / hm
                uvv = u * v * v
                u = u + dt * (Du * lap(u) - uvv + F * (1 - u))
                v = v + dt * (Dv * lap(v) + uvv - (F + K) * v)

        step(6000)                                       # let the pattern grow before the loop starts
        shimmer = Flicker(rng, n, 0.03, 0.12)
        seeds = rng.uniform(6, 14, 40).cumsum()
        planting = []
        for f in range(len(out)):
            step(2)
            t = f * DT
            if len(seeds) and t >= seeds[0]:            # a new cell is planted where the roof is empty
                seeds = seeds[1:]
                far = (np.convolve(v > 0.05, np.ones(31), 'same') == 0) & (F > F0)
                if far.any():
                    planting.append([rng.choice(np.flatnonzero(far)), 40])
            for p_ in planting:                          # planted gently over a second
                if p_[1] > 0:
                    m = np.abs(pdp - pdp[p_[0]]) < 10
                    v[m] += 0.006
                    u[m] -= 0.012
                    p_[1] -= 1
            w = smoothstep(0.06, 0.30, v)
            g = 1 - smoothstep(0.0, 0.45, w)             # green medium
            r = smoothstep(0.55, 1.0, w)                 # red cells; the black border lies between
            s = 1 + 0.06 * shimmer(t)
            I_g = 0.24 * g * s
            I_r = 0.40 * r * s
            out[f][G.path] = perc(I_g)[:, None] * GREEN + perc(I_r)[:, None] * RED
        return out
    return looped(draw, LOOP, floor=(FLOOR, FLOOR_COLOR))
