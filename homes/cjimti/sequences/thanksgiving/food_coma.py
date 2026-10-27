"""Food Coma: After dinner the house dozes off. It breathes slowly: on each inhale the warm light is
drawn in from both free ends and gathers on the porch, like a chest filling; on the exhale it spreads
back out along the wings to the ends. Every few breaths it snores, a slow rattle across the Porch
Front, and the breath after a snore whistles out as a little light running down the Right wing. Now
and then three Z's float off the porch and up the Side, getting smaller, out the back of the house."""
import numpy as np
from pixelhome.fx import DT, hexc, light, smoothstep, lerp, Flicker, nframes, looped

CODE = 'TG09'
TITLE = 'Food Coma'
KIND = 'ambient'
DESCRIPTION = ('After dinner the house dozes. Light is drawn in to the porch on every slow breath and let out to '
               'the ends, with the occasional snore, a whistle, and Z\'s drifting off the back.')

AMBER = hexc('#ff7a14')
CORE = hexc('#ffa040')
DUSK = hexc('#a01818')
WARM = hexc('#ffc27a')
FLOOR_COLOR = hexc('#a02008')
FLOOR = 0.1
LOOP = 150.0
CHEST = 1486.0


def render(G, seed=29):
    rng = np.random.default_rng(seed)
    pdp = G.pd[G.path]
    n = G.N
    dist = np.abs(pdp - CHEST)
    PF = (pdp > 1312) & (pdp < 1660)
    RW = pdp > 2036

    def draw(Dt):
        out = np.zeros((nframes(Dt), n, 3), np.float32)
        tex = Flicker(rng, n, 0.04, 0.2)
        # breath schedule: each breath has its own length, snores every few
        breaths = []
        t = 0.0
        k = 0
        while t < Dt + 10:
            period = rng.uniform(5.6, 7.2)
            snore = (k % 4 == 3) or (rng.random() < 0.1)
            breaths.append((t, period, snore))
            t += period
            k += 1
        zz = []
        t = rng.uniform(10, 25)
        while t < Dt:
            zz.append(t)
            t += rng.uniform(28, 45)
        starts = np.array([b[0] for b in breaths])

        for f in range(len(out)):
            t = f * DT
            i = int(np.searchsorted(starts, t, side='right') - 1)
            t0, per, snore = breaths[i]
            ph = (t - t0) / per
            # inhale over 40%, exhale over 45%, then a rest
            b = smoothstep(0, 0.4, ph) * (1 - smoothstep(0.42, 0.87, ph))
            L = lerp(1250, 420, b)
            amp = 0.17 * np.sqrt(1250 / L) ** 0.9
            I = amp * np.exp(-(dist / L) ** 2) + 0.05
            I = I * (1 + 0.08 * tex(t))
            col = lerp(DUSK, AMBER, np.clip(np.exp(-(dist / L) ** 2) * 1.2, 0, 1)[:, None])
            buf = light(1.0, I) * col
            if snore:
                # a slow rattle on the porch at the top of the inhale
                s = smoothstep(0.2, 0.38, ph) * (1 - smoothstep(0.4, 0.5, ph))
                rattle = 0.5 + 0.5 * np.sin(2 * np.pi * 2.2 * t + pdp * 0.03)
                buf[PF] += light(CORE, (0.12 * s * rattle)[PF])
            # the breath after a snore whistles out along the Right wing
            if i > 0 and breaths[i - 1][2] and 0.42 < ph < 0.9:
                u = (ph - 0.42) / 0.48
                x = 2036 + u * 520
                buf += light(WARM, 0.2 * np.sin(np.pi * u) * np.exp(-((pdp - x) / 18) ** 2) * RW)
            # Z's float off the porch, up the Side, smaller and dimmer as they rise
            for tz in zz:
                for j in range(3):
                    u = t - tz - 1.6 * j
                    if 0 < u < 16:
                        x = 1300 - 85 * u                   # porch -> Porch Left -> Left -> up the Side
                        size = 14 * (1 - 0.6 * u / 16) * (1 - 0.15 * j)
                        a = 0.3 * smoothstep(0, 1.5, u) * (1 - smoothstep(10, 16, u)) * (1 - 0.15 * j)
                        buf += light(WARM, a * np.exp(-((pdp - x) / size) ** 2))
            out[f][G.path] = buf
        return out
    return looped(draw, LOOP, floor=(FLOOR, FLOOR_COLOR))
