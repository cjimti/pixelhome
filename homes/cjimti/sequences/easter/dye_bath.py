"""Dye Bath: All-night loop. The roofline is a pale eggshell lit from inside, and egg dye is dropped
onto it: cyan, magenta and yellow, in mirror-image pairs across the facade (Left with Right, Porch
Left with Porch Right, mirrored on the Porch Front). Each drop lands as a small saturated spot and
bleeds outward by diffusion while a slow, shifting current stretches and drags it along the roof.
Colour is subtractive, as with real dye: each dye absorbs one primary from the light behind it
(Beer-Lambert), so where yellow bleeds into cyan the shell turns spring green, magenta and yellow
make coral, cyan and magenta make lavender. Dye slowly rinses away, so the shell never goes muddy."""
import numpy as np
from pixelhome.fx import DT, hexc, perc, nframes, looped

CODE = 'EA10'
TITLE = 'Dye Bath'
KIND = 'ambient'
DESCRIPTION = 'Drops of egg dye land on a pale shell in mirror-image pairs and bleed slowly along the roof; where colours meet they mix like real dye: yellow into blue makes green.'


def lin(h):
    return hexc(h) ** 2.2


SHELL = lin('#fff3e6')
LEVEL = 0.36                       # perceptual brightness of the bare shell
# absorption of (R, G, B) per unit of each dye
ABSORB = np.array([[1.0, 0.08, 0.03],      # cyan absorbs red
                   [0.06, 1.0, 0.2],       # magenta absorbs green
                   [0.02, 0.12, 1.0]])     # yellow absorbs blue
FLOOR = 0.11
FLOOR_COLOR = lin('#c8b8e8')
LOOP = 160.0


def render(G, seed=30):
    rng = np.random.default_rng(seed)
    n = G.N
    pdp = G.pd[G.path]
    pp = G.pos[G.path]
    h = np.diff(pdp)
    hl = np.concatenate([[h[0]], h])
    hr = np.concatenate([h, [h[-1]]])
    base = perc(LEVEL) * SHELL
    Dif = 55.0                      # diffusion, units^2/s: a spot bleeds ~40 units in 15 s
    rinse = 1 / 80.0                # dye slowly washes out

    # mirror partner of each pixel across the facade (x -> 32 - x at the same depth); Side has none
    mx = np.stack([32 - pp[:, 0], pp[:, 2]], 1)
    d2 = ((mx[:, None, :] - pp[None, :, [0, 2]]) ** 2).sum(-1)
    partner = d2.argmin(1)
    has_partner = np.sqrt(d2.min(1)) < 30

    def lap(a):
        al = np.concatenate([a[:, 1:2], a[:, :-1]], 1)
        ar = np.concatenate([a[:, 1:], a[:, -2:-1]], 1)
        return 2 / (hl + hr) * ((ar - a) / hr - (a - al) / hl)

    def draw(D):
        F = nframes(D)
        out = np.zeros((F, n, 3), np.float32)
        c = np.zeros((3, n))
        drops = []
        t = -30.0
        while t < D:
            i = int(rng.integers(n))
            drops.append((t, int(rng.integers(3)), i, rng.uniform(2.0, 3.2), rng.uniform(10, 18)))
            t += rng.uniform(1.4, 2.4)
        j = 0
        active = []
        ph = rng.uniform(0, 2 * np.pi, 2)

        def step(c, t):
            # slow current: two drifting sine cells that stretch and drag the dye along the path
            v = 7 * np.sin(2 * np.pi * pdp / 820 + 2 * np.pi * t / 97 + ph[0]) + \
                4 * np.sin(2 * np.pi * pdp / 330 - 2 * np.pi * t / 61 + ph[1])
            src = pdp - v * DT
            c = np.stack([np.interp(src, pdp, ck) for ck in c])
            c += DT * Dif * lap(c)
            return c * (1 - rinse * DT)

        W = nframes(30)                  # 30 s off-stage so the night starts mid-bath
        for f in range(-W, F):
            t = f * DT
            while j < len(drops) and drops[j][0] <= t:
                active.append(drops[j])
                j += 1
            for d0 in active:                       # a drop soaks in over 0.8 s, not in one frame
                t0, dye, i, amt, w = d0
                for p in ([i, partner[i]] if has_partner[i] else [i]):
                    c[dye] += amt * DT / 0.8 * np.exp(-((pdp - pdp[p]) / w) ** 2)
            active = [d0 for d0 in active if t - d0[0] < 0.8]
            c = step(c, t)
            T = np.exp(-1.8 * (c.T @ ABSORB))               # Beer-Lambert: light through the dyed shell
            if f >= 0:
                out[f][G.path] = base * T
        return out
    return looped(draw, LOOP, floor=(FLOOR, FLOOR_COLOR))
