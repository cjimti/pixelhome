"""Haze: Late on the Fourth, the smoke from the evening's shows hangs over the street. The house sits
inside a slow 3-D smoke field (a sum of drifting plane waves, carried by a light breeze from the
left), and every pixel shows only the light scattered toward the street by the smoke around it.
Far-off neighbourhood fireworks light the smoke from where they really are: behind the house,
off to either side, over the street. Smoke scatters forward, so a burst behind the house makes
the haze glow (backlit) while one over the street barely lifts it, and the pool of colour slides
across the roof the way real light does. Between bursts the smoke holds a dim blue-violet glow.
Nothing flashes: every distant burst blooms and fades in seconds. All-night loop."""
import numpy as np
from pixelhome.fx import DT, hexc, light, smoothstep, nframes, looped

CODE = 'IN09'
TITLE = 'Haze'
KIND = 'ambient'
DESCRIPTION = ('The smoke left over the street after the shows, lit from far away by the neighbourhood\'s '
               'fireworks. Backlit bursts make the haze glow; colour slides across the roof. All-night loop.')

NIGHT = hexc('#1a1260')
COLS = [hexc('#ff2414'), hexc('#e8ecff'), hexc('#2244ff'), hexc('#ff8a20'), hexc('#ff3050'), hexc('#a0b8ff')]
FLOOR = 0.1
LOOP = 170.0
VIEW = np.array([0.0, 170.0, 3200.0])


def render(G, seed=29):
    rng = np.random.default_rng(seed)
    P = G.pos

    def draw(D):
        F = nframes(D)
        out = np.zeros((F, G.N, 3), np.float32)
        nw = 9
        kd = rng.normal(size=(nw, 3))
        kd[:, 1] *= 0.4
        kd /= np.linalg.norm(kd, axis=1, keepdims=True)
        kmag = rng.uniform(1 / 900, 1 / 260, nw) * 2 * np.pi
        ph = rng.uniform(0, 2 * np.pi, nw)
        wind = np.array([22.0, 0.0, -6.0])
        swirl = rng.uniform(0.02, 0.07, nw)
        view = VIEW - P
        view /= np.linalg.norm(view, axis=1, keepdims=True)
        bursts = []
        t = 3.0
        while t < D:
            side = rng.choice(['back', 'left', 'right', 'front', 'back'])
            pos = {'back': (rng.uniform(-1500, 1500), rng.uniform(900, 1800), rng.uniform(-3600, -2400)),
                   'left': (rng.uniform(-3600, -2600), rng.uniform(900, 1600), rng.uniform(-1500, 500)),
                   'right': (rng.uniform(2600, 3600), rng.uniform(900, 1600), rng.uniform(-1500, 500)),
                   'front': (rng.uniform(-1500, 1500), rng.uniform(1200, 2000), rng.uniform(1800, 3000))}[side]
            cs = rng.choice(len(COLS), 2, replace=False)
            bursts.append((t, np.array(pos, float), COLS[cs[0]], COLS[cs[1]], rng.uniform(0.7, 1.1)))
            t += rng.choice([rng.uniform(5, 10), rng.uniform(1.2, 2.2)])   # sometimes a little cluster
        g = 0.65                                       # Henyey-Greenstein forward scattering
        for f in range(F):
            t = f * DT
            arg = ((P - wind * t) @ (kd * kmag[:, None]).T) + ph + swirl * t * 2 * np.pi
            dens = np.sin(arg).sum(1) / np.sqrt(nw / 2)
            dens = np.clip(0.5 + 0.35 * dens, 0, 1) ** 1.6
            fr = light(NIGHT, 0.13 + 0.12 * dens)
            for tb, bp, c1, c2, a in bursts:
                u = t - tb
                if u < 0 or u > 8.0:
                    continue
                env = smoothstep(0, 0.7, u) * np.exp(-u / 2.0) * a
                col = c1 * (1 - smoothstep(0.8, 1.8, u)) + c2 * smoothstep(0.8, 1.8, u)
                ld = P - bp
                dist = np.linalg.norm(ld, axis=1)
                ld /= dist[:, None]
                cos = (ld * view).sum(1)
                hg = (1 - g * g) / (1 + g * g - 2 * g * cos) ** 1.5 / 4
                fall = (2800 / dist) ** 5                     # steep, so the pool of colour sits on the near side
                fr += col * (0.05 * env * hg * fall * (0.25 + dens))[:, None]
            out[f] = fr
        return out
    return looped(draw, LOOP, floor=(FLOOR, NIGHT))
