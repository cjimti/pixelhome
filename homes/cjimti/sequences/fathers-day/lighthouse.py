"""Lighthouse: a lighthouse stands in the middle of the porch notch, and its two beams turn slowly in
true 3-D, so each sweep crosses the three porch runs up close (short and slow) and the far wings and
Side at a distance (dimmer, by inverse square, and faster). Lit pixels keep an afterglow. Fog banks
roll through and widen the beams into haze; the sea beneath breathes deep blue. Once a loop, a
ship's green running light passes along the wing fronts and the beam finds it."""
import numpy as np
from pixelhome.fx import DT, hexc, perc, light, smoothstep, keys, lerp, Flicker, nframes, looped, smooth_noise

CODE = 'FA08'
TITLE = 'Lighthouse'
KIND = 'ambient'
DESCRIPTION = ('A lighthouse in the porch notch: two beams turn slowly through the house in 3-D, leaving an '
               'afterglow, fog rolls through, and once a loop a ship passes along the front.')

SEA = hexc('#0c2a68')
SEA2 = hexc('#164a80')
BEAM = hexc('#ffe2a8')
HAZE = hexc('#b8c8e0')
SHIP = hexc('#30ff70')
FLOOR = 0.1
LOOP = 150.0


def render(G, seed=28):
    rng = np.random.default_rng(seed)

    def draw(D):
        n = G.N
        out = np.zeros((nframes(D), n, 3), np.float32)
        P = G.pos[G.path]
        x = G.pd[G.path]
        tower = np.array([-22.0, -360.0])               # (x, z) in the notch
        dx, dz = P[:, 0] - tower[0], P[:, 2] - tower[1]
        ang = np.arctan2(dz, dx)
        r = np.hypot(dx, dz)
        fall = 1 / (1 + (r / 420) ** 2)                  # inverse-square-ish falloff
        fall = fall / fall.max()
        swell = smooth_noise(rng, x, 140, 3)
        swell2 = smooth_noise(rng, x, 60, 2)
        shimmer = Flicker(rng, n, 0.04, 0.2)
        period = LOOP / 6                                # 25 s a turn, two beams
        glow = np.zeros(n)
        for f in range(len(out)):
            t = f * DT
            fog = 0.5 + 0.5 * np.sin(2 * np.pi * t / (LOOP / 2) + 0.7)        # two fog banks per loop
            a0 = 2 * np.pi * t / period
            d1 = np.angle(np.exp(1j * (ang - a0)))
            d2 = np.angle(np.exp(1j * (ang - a0 - np.pi)))
            w = lerp(0.14, 0.3, fog)
            hit = np.exp(-(d1 / w) ** 2) + np.exp(-(d2 / w) ** 2)
            # a beam leads with a sharp edge and trails into the afterglow
            glow = np.maximum(glow * np.exp(-DT / 2.2), hit * fall)
            beam = 0.38 * hit * fall * lerp(1.0, 0.75, fog)
            haze = 0.06 * fog * (np.exp(-(d1 / (3 * w)) ** 2) + np.exp(-(d2 / (3 * w)) ** 2)) * np.sqrt(fall)

            # the sea, in path distance so it rolls round the corners
            s1 = np.interp((x + 22 * t) % G.length, x, swell)
            s2 = np.interp((x - 9 * t) % G.length, x, swell2)
            sea_I = 0.15 + 0.035 * s1 + 0.02 * s2 + 0.01 * shimmer(t)
            buf = light(lerp(SEA, SEA2, np.clip(0.5 + s1, 0, 1)[:, None]), sea_I)
            buf += light(BEAM, np.clip(beam + 0.16 * glow, 0, 0.36))
            buf += light(HAZE, haze)

            # a ship crossing the front, once a loop (off the roof at both ends of the loop)
            sx = lerp(760, -760, t / LOOP)
            dist = np.hypot(P[:, 0] - sx, P[:, 2] + 170)
            lit_by_beam = 1 + 1.4 * np.exp(-((np.angle(np.exp(1j * (np.arctan2(-175 - tower[1], sx - tower[0]) - a0))) / 0.3) ** 2))
            buf += light(SHIP, 0.2 * lit_by_beam * np.exp(-(dist / 26) ** 2))
            out[f][G.path] = buf
        return out

    return looped(draw, LOOP, floor=(FLOOR, SEA))
