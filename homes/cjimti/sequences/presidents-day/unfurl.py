"""Unfurl: A flag the size of the house lies over it in plan, set at an angle so its stripes cross
every run. It unrolls from the hoist at the back left, then flies: travelling folds bend the stripes
and shade the cloth (crests catch the light, troughs fall into shadow), and the fifty stars, which
only show where the cloth carries them across the roofline, wink in and out as the folds pass.
A gust, a lull, and the flag settles to a slow breathing ripple."""
import numpy as np
from pixelhome.fx import DT, hexc, light, smoothstep, keys, lerp, nframes

CODE = 'PR05'
TITLE = 'Unfurl'
KIND = 'show'
DESCRIPTION = ('A flag as big as the house unrolls across the roofline and flies. Folds travel through the '
               'cloth, bending the stripes, and the stars wink as the waves carry them across the roof.')

BRICK = hexc('#c41c10')
CREAM = hexc('#ffe4c0')
NAVY = hexc('#1a2ea8')
STAR = hexc('#fff2dc')
BRASS = hexc('#ffa030')


def render(G, seed=25):
    rng = np.random.default_rng(seed)
    D = 66.0
    out = np.zeros((nframes(D), G.N, 3))
    x, z = G.pos[:, 0], G.pos[:, 2]
    th = np.radians(38)
    ar = x * np.cos(th) - z * np.sin(th)          # along the fly
    br = x * np.sin(th) + z * np.cos(th)          # down the hoist (toward the street = bottom)
    a = (ar - ar.min()) / (ar.max() - ar.min()) * 0.92 + 0.04
    b = (br - br.min()) / (br.max() - br.min()) * 0.92 + 0.04
    # fifty stars: nine staggered rows of 6 and 5 in the canton
    stars = []
    for r in range(9):
        k = 6 if r % 2 == 0 else 5
        for c in range(k):
            stars.append(((c + (0.5 if k == 5 else 0) + 0.5) / 6 * 0.4, (r + 0.5) / 9 * 7 / 13))
    stars = np.array(stars)
    star_sz = np.array([0.012, 0.011])

    phase = 0.0
    for f in range(len(out)):
        t = f * DT
        fr = out[f]
        # wind: amplitude and tempo of the travelling folds
        amp = keys(t, [(0, 0.0), (8, 0.25), (20, 0.6), (36, 0.6), (40, 1.0), (47, 1.0), (52, 0.35), (66, 0.3)])
        tempo = keys(t, [(0, 0.3), (36, 0.4), (40, 0.75), (47, 0.75), (52, 0.3), (66, 0.25)])
        phase += 2 * np.pi * tempo * DT
        A = amp * a ** 0.8
        arg = 2 * np.pi * (2.6 * a + 0.35 * np.sin(2 * np.pi * 0.9 * b + 0.4 * t)) - phase
        w = A * np.sin(arg)
        slope = A * np.cos(arg)
        shade = 0.62 + 0.38 * np.tanh(2.2 * slope)
        crest = np.clip(slope, 0, None) ** 3 * amp
        aw = a - 0.025 * w
        bw = b + 0.06 * w

        # unfurl: the cloth exists only up to the rolling front
        front = keys(t, [(3, 0.0), (15, 1.05)])
        unrolled = smoothstep(front + 0.01, front - 0.02, a)
        roll = np.exp(-((a - front) / 0.018) ** 2) * (t < 16)

        red = smoothstep(-0.25, 0.25, np.sin(13 * np.pi * bw))[:, None]
        cloth = lerp(CREAM, BRICK, red)
        I = lerp(0.5, 0.62, red[:, 0]) * shade
        canton = smoothstep(0.405, 0.395, aw) * smoothstep(7 / 13 + 0.005, 7 / 13 - 0.005, bw)
        cloth = lerp(cloth, NAVY[None, :], canton[:, None])
        I = lerp(I, 0.48 * shade, canton)
        fade = keys(t, [(D - 4, 1), (D, 0)])
        fr += cloth * (np.clip(I, 0, None) ** 2.2 * unrolled * fade)[:, None]
        # stars wink where the cloth carries them over the roofline
        du = (aw[None, :] - stars[:, 0:1]) / star_sz[0]
        dv = (bw[None, :] - stars[:, 1:2]) / star_sz[1]
        st = np.exp(-(du * du + dv * dv)).max(0) * canton
        fr += light(STAR, 0.95 * st * unrolled * fade * (0.8 + 0.2 * shade))
        # sheen on the crests, warming toward evening at the end
        sheen_col = lerp(STAR, BRASS, smoothstep(50, 62, t))
        fr += light(sheen_col, 0.35 * crest * unrolled * fade)
        # the roll itself, and the finial at the hoist before it starts
        fr += light(CREAM, 0.6 * roll)
        fin = np.exp(-(a - 0.04) ** 2 / 0.0004 - (b - 0.04) ** 2 / 0.004)
        fr += light(BRASS, 0.8 * fin * keys(t, [(0, 0), (1.5, 1), (5, 1), (8, 0)]))
    return out
