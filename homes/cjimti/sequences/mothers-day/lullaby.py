"""Lullaby: A cradle of warm light hangs from a pivot out over the street and rocks on a long
pendulum. Its bob swings through real space along a U that fits the house: at the bottom of each
swing it sinks back into the porch, at the ends it climbs out along the wings. The rocking keeps
three-four time: one soft glint where the cradle turns, two quieter beats on the way. The swing
slowly settles as the baby drifts off, then is nudged again. Colour drifts peach, rose, lilac."""
import numpy as np
from pixelhome.fx import DT, hexc, perc, light, colormap, Flicker, nframes, looped

CODE = 'MO02'
TITLE = 'Lullaby'
KIND = 'ambient'
DESCRIPTION = 'A cradle of warm light rocks on a long pendulum through the house, in three-four time, settling as the baby drifts off and nudged again.'

FLOOR_COLOR = hexc('#ff9a80')
FLOOR = 0.09
LOOP = 156.0
PERIOD = 6.5            # one swing there and back: 24 per loop


def render(G, seed=22):
    rng = np.random.default_rng(seed)
    P = G.pos
    pivot = np.array([16.0, 150.0, 640.0])     # pivot out over the street: the arc dips into the porch
    R = 1060.0
    hue = colormap([(0, hexc('#ffa070')), (0.33, hexc('#ff6c98')), (0.66, hexc('#c088ff')), (1, hexc('#ffa070'))])
    star = hexc('#d8c0ff')
    blanket = hexc('#ffc8a8')

    def draw(D):
        out = np.zeros((nframes(D), G.N, 3), np.float32)
        shimmer = Flicker(rng, G.N, 0.05, 0.25)
        st = Flicker(rng, G.N, 0.04, 0.12, k=2)
        sides = np.isin(np.arange(G.N), np.concatenate([G.seg['Side'], G.seg['Porch Left'], G.seg['Porch Right']]))
        for f in range(len(out)):
            t = f * DT
            # amplitude: rocks wide, settles, nudged again (two cycles per loop)
            a = 0.42 + 0.16 * (0.5 + 0.5 * np.cos(2 * np.pi * t / (LOOP / 2)))
            ph = 2 * np.pi * t / PERIOD
            th = a * np.sin(ph)
            bob = pivot + R * np.array([np.sin(th), 0, -np.cos(th)])
            d = np.linalg.norm(P - bob, axis=1)
            c = hue((t / LOOP) % 1)
            I = 0.25 * np.exp(-(d / 230) ** 2) + 0.12 * np.exp(-(d / 520) ** 2)
            # three-four time: beat 1 where the cradle turns, two soft beats between
            beat = (ph / (2 * np.pi) * 3) % 3            # three beats per swing
            k = np.round(beat)
            acc = 1.0 if int(k) % 3 == 0 else 0.45
            pulse = acc * np.exp(-((beat - k) / 0.12) ** 2)
            I = I * (1 + 0.18 * pulse) * (1 + 0.04 * shimmer(t))
            fr = light(c, I) + light(blanket, 0.05 + 0.02 * np.sin(2 * np.pi * t / 13))
            # sleepy stars on the flanks
            s = np.clip(st(t) - 0.9, 0, None) * 0.5
            fr += light(star, s * sides)
            out[f] = fr
        return out
    return looped(draw, LOOP, floor=(FLOOR, FLOOR_COLOR))
