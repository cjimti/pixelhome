"""Phantom: True 3-D: a ghost flies around (and into) the house, searchlights sweep from the street,
scanning planes reveal the depth of the roof, three spirits spiral in and burst."""
import numpy as np
from pixelhome.fx import DT, hexc, light, smoothstep, keys, lerp, Flicker, nframes, catmull_closed

CODE = 'SC3'
TITLE = 'Phantom'
KIND = 'show'
DESCRIPTION = 'A ghost flies in and out of the porch, searchlights sweep from the street, scanning planes reveal the depth of the roof.'

ORANGE = hexc('#ff3000')
PURPLE = hexc('#5000c0')
WHITE = hexc('#ffffff')
GHOST = hexc('#80ffd0')
ICE = hexc('#c0d8ff')
RED = hexc('#ff0000')


def render(G, seed=3):
    rng = np.random.default_rng(seed)
    D = 70.0
    out = np.zeros((nframes(D), G.N, 3))
    P = G.pos
    xz = P[:, [0, 2]]
    fog = Flicker(rng, G.N, 0.05, 0.3)
    route = np.array([(-700, 150, -80), (-400, 150, -100), (-250, 150, -300), (-20, 150, -510), (110, 150, -400),
                      (230, 150, -130), (550, 150, -120), (720, 150, -230), (320, 150, -40), (-300, 150, -40),
                      (-660, 150, -300), (-640, 150, -660), (-720, 150, -260)], float)
    trail = np.zeros(G.N)
    lights = [np.array([-350.0, 700.0]), np.array([350.0, 700.0])]
    centre = np.array([0.0, 150.0, -390.0])
    spirits = [(GHOST, 0.0), (hexc('#b000ff'), 2 * np.pi / 3), (hexc('#ff4000'), 4 * np.pi / 3)]

    for f in range(len(out)):
        t = f * DT
        fr = out[f]
        bg = keys(t, [(0, 0), (2, 0.1), (24, 0.1), (25, 0.04), (55, 0.04), (56, 0.1), (66, 0.1), (70, 0)])
        fr += light(PURPLE, bg * (0.7 + 0.3 * fog(t)))

        if t < 25.5:                                         # the ghost
            g = catmull_closed(route, t / 25.0)
            d = np.linalg.norm(P - g, axis=1)
            cur = np.exp(-(d / 120) ** 2) * keys(t, [(0, 0), (1.5, 1), (24, 1), (25.5, 0)])
            trail = np.maximum(trail * 0.94, cur * 0.6)
            fr += light(GHOST, np.maximum(cur, trail))
        elif t < 40:                                         # searchlights from the street
            k = keys(t, [(25.5, 0), (26.5, 1), (39, 1), (40, 0)])
            for j, s in enumerate(lights):
                ang = np.arctan2(xz[:, 0] - s[0], s[1] - xz[:, 1])
                sweep = 0.75 * np.sin(2 * np.pi * (t - 25.5) / (6.5 + j * 1.7) + j * 2.1)
                fr += light(ICE, k * np.exp(-((ang - sweep) / 0.035) ** 2))
        elif t < 55:                                         # scanning planes
            lt = t - 40
            for t0, dur, axis, a, b, col in [(0, 4, 2, -100, -680, hexc('#20ff60')), (4, 4, 2, -680, -100, RED),
                                             (8.5, 3, 0, -640, 670, hexc('#9000ff')),
                                             (11.5, 3, 0, 670, -640, ORANGE)]:
                if t0 <= lt < t0 + dur + 0.8:
                    plane = lerp(a, b, smoothstep(0, 1, (lt - t0) / dur))
                    sgn = np.sign(b - a)
                    behind = (plane - P[:, axis]) * sgn
                    band = np.exp(-(behind / 22) ** 2) + np.where(behind > 0, 0.35 * np.exp(-behind / 90), 0)
                    fr += light(col, band * min(1, (t0 + dur + 0.8 - lt) / 0.8))
        else:                                                # three spirits spiral in
            lt = t - 55
            if lt < 11:
                r = lerp(750, 0, smoothstep(0, 11, lt) ** 0.8)
                spin = 0.6 * lt + 0.06 * lt ** 2.4
                for col, ph in spirits:
                    a = spin * 2 * np.pi / 3 + ph
                    c = centre + np.array([r * np.sin(a), 0, r * np.cos(a)])
                    d = np.linalg.norm(P - c, axis=1)
                    fr += light(col, 0.9 * np.exp(-(d / 100) ** 2))
            else:
                tb = lt - 11
                d = np.linalg.norm(P - centre, axis=1)
                fr += light(WHITE, np.exp(-((d - tb * 1300) / 90) ** 2) * np.exp(-tb / 1.2) + np.exp(-tb / 0.2))
    return out
