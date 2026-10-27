"""Lantern Floating: The Memorial Day lantern floating. The roofline is a slow river that enters at the
free back end of the Side and leaves at the free end of the Right wing. White paper lanterns, a candle
glowing in each, drift on the current; the water slows round each corner, so lanterns bunch up there
and spread out again on the straights, and faint silver ripples on the water bunch up with them. Each
lantern lays a wide, shimmering reflection on the water. The whole flow is exactly periodic: every
lantern takes the full loop to travel the river, so the end flows into the start."""
import numpy as np
from pixelhome.fx import DT, hexc, perc, smoothstep, lerp, nframes, looped

CODE = 'MM09'
TITLE = 'Lantern Floating'
KIND = 'ambient'
DESCRIPTION = ('The roof becomes a slow river. Paper lanterns drift from the back of the house to the far end '
               'of the right wing, bunching at the bends, each with a shimmering reflection.')

NAVY = hexc('#0b1d4a')
WATER = hexc('#8fa6d0')
PAPER = hexc('#fff0d4')
GOLD = hexc('#ffb848')
RED = hexc('#ff5a3c')
LOOP = 160.0
MARGIN = 160.0


def render(G, seed=9):
    rng = np.random.default_rng(seed)
    pdp = G.pd[G.path]
    corners = pdp[[80, 178, 260, 331, 380]]
    # current speed along the river (relative), slow round each corner; travel time table
    s = np.linspace(-MARGIN, G.length + MARGIN, 4000)
    v = 1 - 0.62 * np.exp(-((s[:, None] - corners[None, :]) / 55.0) ** 2).sum(1)
    tau = np.concatenate([[0], np.cumsum(np.diff(s) / v[1:])])
    tau *= LOOP / tau[-1]                                     # one full passage = one loop
    tau_px = np.interp(pdp, s, tau)                           # travel time to each pixel
    K = 19
    ph = np.sort(rng.uniform(0, LOOP, K))
    tint = np.full(K, 0.0)
    tint[rng.choice(K, 7, replace=False)] = rng.uniform(0.3, 0.7, 7)       # some warmer than others
    red = np.zeros(K, bool); red[rng.choice(K, 3, replace=False)] = True
    size = rng.uniform(6.0, 8.5, K)
    lvl = rng.uniform(0.27, 0.34, K)
    bob_n = rng.integers(20, 34, K)                           # bob frequencies: whole cycles per loop
    bob_p = rng.uniform(0, 2 * np.pi, K)
    lcol = np.array([RED * 0.8 + PAPER * 0.2 if red[k] else lerp(PAPER, GOLD, tint[k]) for k in range(K)])

    def draw(D):
        out = np.zeros((nframes(D), G.N, 3), np.float32)
        for f in range(len(out)):
            t = f * DT
            # the water: slow silver ripples carried by the current (14 bands in one passage)
            w = 2 * np.pi * (tau_px - t) / LOOP
            rip = 0.5 + 0.5 * np.sin(14 * w) * np.sin(5 * w + 1.3)
            col = perc(0.075 + 0.035 * rip)[:, None] * NAVY + perc(0.05 * rip ** 2)[:, None] * WATER
            tk = (ph + t) % LOOP
            pos = np.interp(tk, tau, s)
            bob = np.sin(2 * np.pi * bob_n * t / LOOP + bob_p)
            pos = pos + 1.2 * bob
            d = pdp[:, None] - pos[None, :]                    # (N, K)
            body = 1 - smoothstep(size - 3.0, size + 2.5, np.abs(d))
            I = body * (lvl * (1 + 0.05 * bob))[None, :]
            shimmer = 0.55 + 0.45 * np.sin(2 * np.pi * (d / 16.0 - 36 * t / LOOP))
            refl = 0.13 * np.exp(-(d / 26.0) ** 2) * shimmer * (1 - body)
            col = col * (1 - np.clip(body.sum(1), 0, 1))[:, None]
            col += perc(I) @ lcol + perc(refl) @ (0.5 * lcol + 0.5 * WATER)
            out[f][G.path] = col
        return out
    return looped(draw, LOOP, floor=(0.06, NAVY))
