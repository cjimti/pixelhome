"""Eternal Flame: All-night loop. A flame burns at the middle of the porch front, coloured by a
blackbody temperature field (hotter at the core, cooling at its edges) that drifts with slow
draughts. The rest of the roof is lit only by that flame, with inverse-square falloff in real 3-D
distance, so the near wings glow and the far back of Side is barely touched, and every pixel
breathes in step with the flame's power. Beneath it all, a quiet navy night."""
import numpy as np
from pixelhome.fx import DT, hexc, perc, light, smooth_noise, Flicker, nframes, looped

CODE = 'VT03'
TITLE = 'Eternal Flame'
KIND = 'ambient'
DESCRIPTION = ('A flame burns at the centre of the porch and is the only light on the house: the roof glows '
               'with it, warm near and faint far, and breathes as it does.')

NAVY = hexc('#1c34ff')
FLOOR_COLOR = hexc('#4050ff')
FLOOR = 0.09
LOOP = 160.0


def blackbody(T):
    """Approximate sRGB of a blackbody at T kelvin (Helland fit), as PWM-ish linear values."""
    T = np.asarray(T, float) / 100.0
    r = np.where(T <= 66, 255, 329.7 * np.clip(T - 60, 1e-3, None) ** -0.1332)
    g = np.where(T <= 66, 99.47 * np.log(np.clip(T, 1, None)) - 161.12,
                 288.12 * np.clip(T - 60, 1e-3, None) ** -0.0755)
    b = np.where(T >= 66, 255, np.where(T <= 19, 0, 138.5 * np.log(np.clip(T - 10, 1, None)) - 305.04))
    c = np.clip(np.stack([r, g, b], -1) / 255.0, 0, 1)
    return c ** 2.2          # sRGB-ish -> PWM


def render(G, seed=23):
    rng = np.random.default_rng(seed)
    P = G.pos
    pf = G.seg['Porch Front']
    xf = P[pf, 0]
    xc = xf.mean()

    def draw(D):
        out = np.zeros((nframes(D), G.N, 3), np.float32)
        lick = Flicker(rng, len(pf), 0.25, 0.9)
        sway = Flicker(rng, 1, 0.02, 0.07, k=4)
        power = Flicker(rng, 1, 0.04, 0.18, k=4)
        grain = Flicker(rng, G.N, 0.03, 0.15)
        tex = smooth_noise(rng, xf, 20)
        sky = 0.11 * (1 + 0.15 * smooth_noise(rng, G.pd, 300))
        gusts, tg = [], rng.uniform(10, 20)
        while tg < D:
            gusts.append((tg, rng.uniform(5, 8), rng.choice([-1, 1])))
            tg += rng.uniform(28, 45)
        for f in range(len(out)):
            t = f * DT
            fr = out[f]
            g = 0.0
            gl = 0.0
            for t0, dur, side in gusts:
                if t0 < t < t0 + dur:
                    b = np.sin(np.pi * (t - t0) / dur) ** 2
                    g = max(g, b)
                    gl += side * b
            lean = 22 * sway(t)[0] + 45 * gl
            pw = (1 + 0.12 * power(t)[0]) * (1 - 0.35 * g)
            # flame: a narrow hot core with flickering tongues; temperature falls with distance from core
            u = (xf - xc - lean) / (52.0 + 20 * g)
            heat = np.exp(-u ** 2) * (0.85 + 0.15 * lick(t) + 0.08 * tex) * pw
            T = 1000 + 1800 * np.clip(heat, 0, 1.1)
            I = 0.44 * np.clip(heat, 0, 1.05) ** 0.8
            fr[pf] = perc(I)[:, None] * blackbody(T)
            # the roof lit by the flame alone, inverse-square in 3-D distance from the flame
            src = np.array([xc + lean, 175.0, -569.0])
            d = np.linalg.norm(P - src, axis=1)
            fall = pw / (1 + (d / 190) ** 2)
            lit = 0.32 * fall * (1 + 0.04 * grain(t))
            warm = blackbody(1500 + 500 * np.clip(fall, 0, 1))
            glow = perc(lit)[:, None] * warm
            glow[pf] *= np.clip(1 - heat, 0, 1)[:, None]
            fr += glow
            fr += light(NAVY, sky * (1 - 0.6 * np.clip(fall, 0, 1)))
        return out
    return looped(draw, LOOP, floor=(FLOOR, FLOOR_COLOR))
