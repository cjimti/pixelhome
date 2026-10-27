"""Six Colours, One Line: All-night loop. The six runs of the roof are the six branches, each its own
colour: Army gold on Side, Marine scarlet and Coast Guard orange on the two wing fronts, Navy and Air
Force blues on the two porch sides, Space Force silver across the porch front. Each colour is a dye
in a slow fluid along the path: a gentle current advects them, diffusion softens them, and a weak
pull keeps each at home, so at every corner the colours reach into each other in slow tongues and
draw back. Now and then a single silver thread runs the whole line, end to end."""
import numpy as np
from pixelhome.fx import DT, hexc, perc, smoothstep, nframes, looped

CODE = 'VT09'
TITLE = 'Six Colours, One Line'
KIND = 'ambient'
DESCRIPTION = ('Each run of the roof holds one branch colour; slow currents let the colours reach into each '
               'other round the corners and draw back, and a silver thread joins them all.')

FLOOR_COLOR = hexc('#3a48ff')
FLOOR = 0.08
LOOP = 150.0
# (segment, colour, perceptual level) - levels balance the colours' apparent brightness
HOME = [('Side', '#ffa418', 0.27), ('Left', '#ff1810', 0.3), ('Porch Left', '#1c34ff', 0.4),
        ('Porch Front', '#c8d0ff', 0.24), ('Porch Right', '#5a94ff', 0.33), ('Right', '#ff5a0c', 0.28)]
THREAD = hexc('#e8ecff')


def render(G, seed=29):
    rng = np.random.default_rng(seed)
    pd = G.pd
    L = G.length
    dx = 4.0
    xs = np.arange(0, L + dx, dx)
    n = len(xs)
    K = len(HOME)
    cols = np.array([hexc(c) * perc(l) for _, c, l in HOME])
    home = np.zeros((K, n))
    for k, (name, _, _) in enumerate(HOME):
        lo, hi = pd[G.seg[name]].min(), pd[G.seg[name]].max()
        home[k] = smoothstep(lo - 4, lo + 4, xs) * (1 - smoothstep(hi - 4, hi + 4, xs))
    waves = [(rng.uniform(11, 16), rng.uniform(500, 800), LOOP / 3, rng.uniform(0, 6.3)),
             (rng.uniform(8, 12), rng.uniform(250, 400), LOOP / 5, rng.uniform(0, 6.3)),
             (rng.uniform(4, 7), rng.uniform(1100, 1500), LOOP / 2, rng.uniform(0, 6.3))]
    Dif, pull = 14.0, 0.05

    def draw(D):
        out = np.zeros((nframes(D), G.N, 3), np.float32)
        c = home.copy()
        # spin up so the corners already have their tongues at frame 0
        t = -60.0
        while t < 0:
            c = step(c, t)
            t += DT
        for f in range(len(out)):
            t = f * DT
            c = step(c, t)
            tot = c.sum(0) + 1e-6
            mix = (c / np.maximum(tot, 1.0)).T @ cols              # (n,3) PWM, dims where dye is thin
            breathe = 1 + 0.06 * np.sin(2 * np.pi * (xs / 700 - t / (LOOP / 6)))
            buf = mix * breathe[:, None]
            # the silver thread: one end to the other, twice a loop, alternating direction
            ph = (t % (LOOP / 2)) / (LOOP / 2)
            k = int(t // (LOOP / 2)) % 2
            head = (ph * 1.3 - 0.15) * L
            head = head if k == 0 else L - head
            th = np.exp(-((xs - head) / 70) ** 2) * 0.24
            buf = buf + perc(th)[:, None] * THREAD
            for ch in range(3):
                out[f][:, ch] = np.interp(pd, xs, buf[:, ch])
        return out

    def step(c, t):
        u = sum(a * np.sin(2 * np.pi * (xs / lam - t / per) + p) for a, lam, per, p in waves)
        src = np.clip(xs - u * DT, 0, L)
        c = np.stack([np.interp(src, xs, ck) for ck in c])
        lap = np.zeros_like(c)
        lap[:, 1:-1] = c[:, 2:] - 2 * c[:, 1:-1] + c[:, :-2]
        c = c + Dif * DT / dx ** 2 * lap
        c += pull * DT * (home - c)
        return c

    return looped(draw, LOOP, floor=(FLOOR, FLOOR_COLOR))
