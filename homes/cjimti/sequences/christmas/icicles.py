"""Icicles: Icicles hang along the three front runs (both wing fronts and the porch front). A slow
temperature field drifts across the house: where it thaws, meltwater creeps along the eave towards
each icicle, the tip swells into a drop and lets go, and the icicle shortens; where it freezes the
icicles grow longer, bluer and brighter and catch the odd crystal glint. The ends and porch sides
hold a frosty glow. Dim, slow and seamless for all night."""
import numpy as np
from pixelhome.fx import DT, hexc, perc, light, smoothstep, lerp, Flicker, nframes, looped

CODE = 'XM08'
TITLE = 'Icicles'
KIND = 'ambient'
DESCRIPTION = ('Icicles along the wing and porch fronts grow in the cold, then drip as a slow thaw drifts '
               'across the house: meltwater creeps to each tip, swells and falls.')

FROST = hexc('#1838a0')
ICE = hexc('#6fa0ff')
ICE_WHITE = hexc('#d8ecff')
DROP = hexc('#f0f8ff')
FLOOR = 0.1
LOOP = 160.0


def render(G, seed=28):
    rng = np.random.default_rng(seed)
    n = G.N
    x = G.pd[G.path]
    seg = G.seg_of[G.path]
    front = np.isin(seg, ['Left', 'Right', 'Porch Front'])
    sites = []
    for name in ('Left', 'Porch Front', 'Right'):
        xs = x[seg == name]
        p = xs.min() + rng.uniform(4, 10)
        while p < xs.max() - 4:
            sites.append(p)
            p += rng.uniform(13, 26)
    sites = np.array(sites)
    m = len(sites)

    def temp(t, p):
        """Temperature (thaw > 0) at path position p; periodic in the loop length."""
        w = 2 * np.pi * t / LOOP
        return 0.75 * np.sin(2 * w - p / 520 + 0.4) + 0.35 * np.sin(w + p / 330 + 2.0)

    def draw(D):
        out = np.zeros((nframes(D), n, 3), np.float32)
        ln = rng.uniform(0.2, 0.7, m)
        drip_t = np.full(m, -99.0)                 # start of the current drip's swell
        swell = rng.uniform(2.0, 3.5, m)
        glint_t = np.full(m, -99.0)
        frost = Flicker(rng, n, 0.03, 0.15)
        shimmer = Flicker(rng, m, 0.05, 0.2)
        dx = x[:, None] - sites[None]
        near = np.abs(dx) < 30
        for f in range(len(out)):
            t = f * DT
            T = temp(t, sites)
            thaw = np.clip(T, 0, None)
            cold = np.clip(-T, 0, None)
            ln = np.clip(ln + DT * 0.016 * cold, 0.08, 1.0)
            # drips start at a rate that rises with the thaw; a new one only after the last fell
            age = t - drip_t
            idle = age > swell + 1.2
            start = idle & (rng.random(m) < DT * 0.4 * thaw)
            drip_t[start] = t
            swell[start] = rng.uniform(2.0, 3.5, start.sum())
            age = t - drip_t
            fell = (age >= swell) & (age - DT < swell)
            ln[fell] = np.clip(ln[fell] - 0.07, 0.08, 1.0)
            sw = np.where(age < swell, smoothstep(0, 1, np.clip(age / swell, 0, 1)) ** 2, 0.0)
            after = np.where((age >= swell) & (age < swell + 0.6), np.exp(-(age - swell) / 0.12), 0.0)
            # crystal glints in the cold
            g = (glint_t < t - 4) & (rng.random(m) < DT * 0.05 * cold)
            glint_t[g] = t
            ga = t - glint_t
            glint = np.where(ga < 1.2, np.sin(np.pi * np.clip(ga / 1.2, 0, 1)) ** 2, 0.0)

            # each icicle: a point that is brighter, wider and whiter the longer it is
            core = 0.08 + 0.24 * ln + 0.04 * shimmer(t) * ln
            core = core + 0.08 * sw + 0.1 * after + 0.08 * glint
            width = 1.4 + 5.0 * ln
            kern = np.where(near, np.exp(-(dx / width[None]) ** 2), 0)
            I_ice = (kern * core[None]).max(1)
            whiten = np.clip((kern * (ln + 0.6 * sw + glint)[None]).max(1), 0, 1)
            # meltwater creeping along the eave toward a swelling tip, from both sides
            run = np.zeros(n)
            active = sw > 0
            if active.any():
                k = np.nonzero(active)[0]
                for side in (-1, 1):
                    pos = sites[k] + side * 12 * (1 - sw[k])
                    run = np.maximum(run, ((np.exp(-((x[:, None] - pos[None]) / 2.0) ** 2) *
                                            (0.1 * np.sin(np.pi * sw[k]))[None]) * near[:, k]).max(1))
            base = np.where(front, 0.075, 0.12) * (1 + 0.12 * frost(t))
            buf = light(FROST, base)
            buf += perc(I_ice)[:, None] * lerp(ICE, ICE_WHITE, whiten[:, None]) * front[:, None]
            buf += light(DROP, run) * front[:, None]
            out[f][G.path] = buf
        return out
    return looped(draw, LOOP, floor=(FLOOR, FROST))
