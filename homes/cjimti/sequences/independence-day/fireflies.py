"""Fireflies: A warm July night after the fireworks. Ninety fireflies drift in 3-D through the yards
around the house (in front of the wings, down in the porch notch, out behind the Side), and the
roof only lights where one passes close, so each glow has a real position and fades with depth.
Each firefly is a pulse-coupled oscillator: when it sees a neighbour flash nearby it hurries its
own next flash a little. Over a few minutes the coupling swells and ebbs, so the yard drifts from
scattered random winks into rolling waves of near-synchronous flashes and back again. Behind it
all the air is a deep blue-green summer dark, and once in a long while heat lightning glows soft
on the far horizon."""
import numpy as np
from pixelhome.fx import DT, hexc, perc, light, smoothstep, smooth_noise, Flicker, nframes, looped

CODE = 'IN06'
TITLE = 'Fireflies'
KIND = 'ambient'
DESCRIPTION = ('A summer night after the show. Fireflies drift in 3D around the house and slowly fall into '
               'step with each other, flashing in rolling waves, then drift apart again. All-night loop.')

GLOW = hexc('#b8ff28')
WARM = hexc('#ffd040')
NIGHT = hexc('#041c30')
HEAT = hexc('#6070ff')
FLOOR = 0.11
LOOP = 160.0


def render(G, seed=26):
    rng = np.random.default_rng(seed)
    P = G.pos

    def draw(D):
        F = nframes(D)
        out = np.zeros((F, G.N, 3), np.float32)
        K = 90
        # each firefly keeps to a patch of yard near some stretch of roof: in front, behind, in the notch
        home = P[rng.integers(0, G.N, K)] + rng.normal(0, [60, 25, 70], (K, 3))
        tt = np.arange(F) * DT
        # smooth wandering: per-firefly low-frequency noise paths around a home
        path = np.empty((F, K, 3))
        for k in range(K):
            for a, amp, sc in ((0, 150, 25.0), (1, 40, 18.0), (2, 90, 25.0)):
                path[:, k, a] = home[k, a] + amp * smooth_noise(rng, tt, sc, octaves=3)
        freq = rng.normal(1 / 5.2, 0.02, K)            # about one flash every 5 s
        theta = rng.uniform(0, 1, K)
        last = np.full(K, -10.0)
        air = Flicker(rng, G.N, 0.02, 0.08)
        tint = smooth_noise(rng, G.pd, 600)
        bolts = [(rng.uniform(10, D - 10), rng.choice([-1, 1])) for _ in range(int(D // 70))]
        for f in range(F):
            t = f * DT
            # coupling swells and ebbs over the loop; each fly also keeps its own restless time
            eps = 0.03 * smoothstep(0.35, 1.0, 0.5 - 0.5 * np.cos(2 * np.pi * t / LOOP))
            theta = np.maximum(theta + freq * DT + 0.035 * np.sqrt(DT) * rng.normal(0, 1, K), 0.0)
            fired = theta >= 1
            if fired.any():
                last[fired] = t
                theta[fired] -= 1
                pos = path[f]
                d = np.linalg.norm(pos[:, None] - pos[fired][None], axis=2)
                seen = (np.exp(-(d / 260) ** 2)).sum(1)          # nearby flashes are seen more strongly
                nudge = eps * seen * (0.4 + theta)                # pulse coupling: later phases jump further
                ready = (t - last) > 2.0                          # refractory: no flash while still glowing
                theta = np.where(fired | ~ready, theta, np.minimum(theta + nudge, 0.999))
            age = t - last
            flash = np.where(age < 2.0, smoothstep(0, 0.4, age) * np.exp(-np.clip(age - 0.4, 0, None) / 0.38), 0.0)
            pos = path[f]
            d2 = ((P[:, None, :] - pos[None]) ** 2).sum(2)
            I = (flash[None] * np.exp(-d2 / 38 ** 2)).sum(1)
            halo = (flash[None] * np.exp(-d2 / 130 ** 2)).sum(1)
            fr = light(NIGHT, (0.13 + 0.015 * air(t)) * (1 + 0.12 * tint))
            fr += light(GLOW, 0.42 * np.clip(I, 0, 1)) + light(WARM, 0.1 * np.clip(I - 0.6, 0, 1))
            fr += light(GLOW, 0.06 * np.clip(halo, 0, 1))
            for tb, side in bolts:                       # distant heat lightning, soft and slow
                u = t - tb
                if 0 < u < 3.0:
                    env = np.sin(np.pi * u / 3.0) ** 2 * (0.6 + 0.4 * np.sin(2 * np.pi * 0.6 * u))
                    grad = smoothstep(-700, 700, side * P[:, 0])
                    fr += light(HEAT, 0.2 * env * grad)
            out[f] = fr
        return out
    return looped(draw, LOOP, floor=(FLOOR, NIGHT))
