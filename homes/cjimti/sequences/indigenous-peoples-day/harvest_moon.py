"""Harvest Moon: The roofline is the surface of a lake at night with a low orange harvest moon
behind the house. Every pixel is a patch of water with its own slope, made by slow wind waves crossing
the yard in real 3-D. A patch shines only when its slope reflects the moon into the eye of someone
standing in the street, so the glitter gathers into a column of sparks (the moon's path on the
water) that falls wherever the moon's direction lines up with the viewer. As the moon drifts slowly
across the sky that path moves over the porch and the wings; around it the water carries a faint
golden sheen. A seamless all-night loop."""
import numpy as np
from pixelhome.fx import DT, hexc, light, lerp, smoothstep, nframes, looped

CODE = 'IP09'
TITLE = 'Harvest Moon'
KIND = 'ambient'
DESCRIPTION = ('A low orange moon behind the house over a lake made of the roofline. Wind waves make '
               'the water glitter only where it would reflect the moon to someone in the street.')

WATER = hexc('#0a2a5a')
SWELL = hexc('#1a4a7a')
MOON_LOW = hexc('#ff8a2a')
MOON_HIGH = hexc('#ffd890')
LOOP = 180.0


def render(G, seed=29):
    rng = np.random.default_rng(seed)
    P = G.pos
    x, z = P[:, 0], P[:, 2]
    E = np.array([16.0, 60.0, 1000.0])                     # an eye in the street
    v = E[None, :] - P
    v /= np.linalg.norm(v, axis=1, keepdims=True)
    K = 14
    ang = rng.normal(-0.3, 0.6, K)                         # wind mostly from one side
    lam = rng.uniform(25, 140, K)
    kk = 2 * np.pi / lam
    kx, kz = kk * np.cos(ang), kk * np.sin(ang)
    om = 2 * np.pi * 0.28 * np.sqrt(60 / lam)              # deep-water dispersion, slowed down
    a = 0.5 / np.sqrt(K) * rng.uniform(0.6, 1.4, K)       # slope amplitude per wave
    ph = rng.uniform(0, 2 * np.pi, K)
    SIG = 0.1

    def draw(D):
        out = np.zeros((nframes(D), G.N, 3), np.float32)
        for f in range(len(out)):
            t = f * DT
            az = 0.33 * np.sin(2 * np.pi * t / LOOP)          # the moon drifts across behind the house
            el = 0.2 + 0.06 * np.sin(2 * np.pi * t / LOOP * 2 + 1.0)
            m = np.array([np.sin(az) * np.cos(el), np.sin(el), -np.cos(az) * np.cos(el)])
            h = m[None, :] + v
            need_x = h[:, 0] / h[:, 1]                         # slope a patch must have to send the moon to the eye
            need_z = h[:, 2] / h[:, 1]
            arg = kx[None, :] * x[:, None] + kz[None, :] * z[:, None] - om[None, :] * t + ph[None, :]
            c = np.cos(arg)
            sx = (a * np.cos(ang) * c).sum(1)
            sz = (a * np.sin(ang) * c).sum(1)
            swell = np.sin(arg).mean(1)
            glint = np.exp(-((need_x - sx) ** 2 + (need_z - sz) ** 2) / (2 * SIG ** 2))
            sheen = np.exp(-(need_x ** 2 + need_z ** 2) / (2 * 0.55 ** 2))
            mc = lerp(MOON_LOW, MOON_HIGH, smoothstep(0.14, 0.26, el))
            col = light(lerp(WATER, SWELL, np.clip(0.5 + 1.5 * swell, 0, 1)[:, None]), 0.11 + 0.02 * swell)
            col += light(mc, 0.12 * sheen) + light(mc, 0.42 * glint * (0.4 + 0.6 * sheen))
            out[f] = col
        return out
    return looped(draw, LOOP, floor=(0.08, WATER))
