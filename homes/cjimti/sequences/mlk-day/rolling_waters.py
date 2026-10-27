"""Rolling Waters: The roof is a river that rises at the free back end of Side and flows the whole path
to the free end of Right. The water is a smooth noise field carried along by the current (pure
advection along characteristics, so its texture really travels instead of being redrawn). The current
slows as it rounds each of the five corners, the way a river slows at a bend: there the water bunches up,
glows a little deeper and brighter, and then runs off faster down the straight. Gold glints appear on
the surface, ride the current for a few seconds and fade. Seamless all-night loop."""
import numpy as np
from pixelhome.fx import DT, hexc, perc, smoothstep, colormap, nframes, looped

CODE = 'MK08'
TITLE = 'Rolling Waters'
KIND = 'ambient'
DESCRIPTION = ('The roof becomes a slow river running from the back of the house to the far end, '
               'pooling at every corner, with gold glints riding the current.')

WATER = colormap([(0.0, (0.0, 0.04, 0.55)), (0.5, (0.02, 0.16, 1.0)), (0.8, (0.08, 0.42, 1.0)),
                  (1.0, (0.3, 0.6, 1.0))])
GLINT = hexc('#ffb050')
FLOOR_COLOR = hexc('#0a20d0')
FLOOR = 0.1
LOOP = 168.0


def render(G, seed=28):
    rng = np.random.default_rng(seed)
    pdp = G.pd[G.path]
    L = G.length
    corners = [G.pd[G.path[i]] for i in (80, 178, 260, 331, 380)]

    def draw(D):
        out = np.zeros((nframes(D), G.N, 3), np.float32)
        # current speed along the path: slower at each bend
        s = np.linspace(0, L, 2000)
        v = np.full_like(s, 30.0)
        for c in corners:
            v -= 15.0 * np.exp(-((s - c) / 55) ** 2)
        tau = np.concatenate([[0], np.cumsum(np.diff(s) / (0.5 * (v[1:] + v[:-1])))])   # travel time
        tp = np.interp(pdp, s, tau)
        vp = np.interp(pdp, s, v)
        # noise in "travel time" coordinates: value at pixel = field(tau - t)
        grid = np.arange(-D - 10, tau[-1] + 10, 0.25)
        def field(scale, amp):
            n = int((grid[-1] - grid[0]) / scale) + 3
            lat = rng.uniform(-1, 1, n)
            xs = (grid - grid[0]) / scale
            i = np.floor(xs).astype(int)
            fr = xs - i
            fr = fr * fr * (3 - 2 * fr)
            return amp * (lat[i] * (1 - fr) + lat[i + 1] * fr)
        surf = field(2.2, 0.6) + field(0.9, 0.3) + field(5.5, 0.5)
        # glints ride the current
        gl = []
        for _ in range(int(D * 0.5)):
            gl.append((rng.uniform(0, D), rng.uniform(0, tau[-1]), rng.uniform(4, 8)))
        bunch = 30.0 / vp                     # compression at bends
        for f in range(len(out)):
            t = f * DT
            val = np.interp(tp - t, grid, surf)
            lvl = 0.5 + 0.5 * np.tanh(1.4 * val)
            I = (0.17 + 0.13 * lvl) * (0.85 + 0.25 * (bunch - 1))
            buf = perc(I)[:, None] * WATER(np.clip(lvl * 0.9 + 0.2 * (bunch - 1), 0, 1))
            for t0, tau0, life in gl:
                u = t - t0
                if 0 < u < life:
                    where = np.interp(tau0 + u, tau, s)
                    env = np.sin(np.pi * u / life) ** 2
                    buf += perc(0.4 * env * np.exp(-((pdp - where) / 4.5) ** 2))[:, None] * GLINT
            out[f][G.path] = buf
        return out
    return looped(draw, LOOP, floor=(FLOOR, FLOOR_COLOR))
