"""Thirteen Stars: The Betsy Ross circle of thirteen stars, built as a real ring in 3-D space centred
over the porch notch. It turns very slowly, its radius breathes and its plane rocks a few degrees,
so each star rises up through the roofline, glides along a run, slips round a corner or drops out
of sight below the eaves, and comes back somewhere else. Where the ring crosses the U the stars
pass the wings, the porch sides and the porch front at different moments: the circle is never
drawn, only implied. Underneath, the roof is a deep navy field with a slow, faint memory of red
and white stripes on the wing fronts. All-night loop."""
import numpy as np
from pixelhome.fx import DT, hexc, light, smoothstep, smooth_noise, Flicker, nframes, looped

CODE = 'IN08'
TITLE = 'Thirteen Stars'
KIND = 'ambient'
DESCRIPTION = ('The circle of thirteen stars from the first flag, as a slowly turning ring in 3D over the porch. '
               'Stars rise through the roof, glide along it and sink away. Deep navy, all-night loop.')

NAVY = hexc('#0c1a8a')
STAR = hexc('#fff2e0')
RED = hexc('#ff1a10')
WHITE = hexc('#f0e8e0')
FLOOR = 0.12
LOOP = 150.0


def render(G, seed=28):
    rng = np.random.default_rng(seed)
    P = G.pos
    centre = np.array([16.0, 150.0, -390.0])
    wing = np.isin(G.seg_of, ['Left', 'Right'])

    def draw(D):
        F = nframes(D)
        out = np.zeros((F, G.N, 3), np.float32)
        field = smooth_noise(rng, G.pd, 500)
        breathe = Flicker(rng, G.N, 0.01, 0.05)
        tw_ph = rng.uniform(0, 2 * np.pi, 13)
        tw_f = rng.uniform(0.05, 0.15, 13)
        for f in range(F):
            t = f * DT
            w = 2 * np.pi * t / LOOP
            ang = 2 * np.pi * (t / LOOP) + np.arange(13) * 2 * np.pi / 13          # one turn per loop
            R = 380 - 200 * np.cos(w) + 25 * np.sin(3 * w + 1)                    # from the porch out past the wings
            tilt = 0.12 * np.sin(2 * w + 0.4)                                    # the plane rocks
            tdir = w * 1.0
            c = centre + np.array([40 * np.sin(w), 0, 60 * np.cos(2 * w)])
            # ring in a tilted plane: tilt about an axis that itself turns
            px = R * np.cos(ang)
            pz = R * np.sin(ang)
            ax = np.array([np.cos(tdir), np.sin(tdir)])
            py = np.sin(tilt) * (px * -ax[1] + pz * ax[0])
            stars = np.stack([c[0] + px, c[1] + py, c[2] + pz], 1)
            d2 = ((P[:, None] - stars[None]) ** 2).sum(2)
            tw = 0.85 + 0.15 * np.sin(2 * np.pi * tw_f * t + tw_ph)
            I = (tw[None] * np.exp(-d2 / 40 ** 2)).sum(1)
            halo = (np.exp(-d2 / 110 ** 2)).sum(1)
            base = 0.15 * (1 + 0.15 * field) * (1 + 0.06 * breathe(t))
            fr = light(NAVY, base + 0.08 * np.clip(halo, 0, 1))
            stripe = 0.5 + 0.5 * np.sin(2 * np.pi * (G.pd / 160.0) - w)          # 13-ish stripes, drifting
            mem = wing * (0.09 + 0.02 * np.sin(w + 1))
            fr += light(RED, mem * smoothstep(0.55, 0.9, stripe)) + light(WHITE, 0.7 * mem * smoothstep(0.55, 0.9, 1 - stripe))
            fr += light(STAR, 0.43 * np.clip(I, 0, 1))
            out[f] = fr
        return out
    return looped(draw, LOOP, floor=(FLOOR, NAVY))
