"""Northern Lights: Three aurora curtains hang in the air above the house, each a folded sheet whose
footprint is a wavy line across the yard. A curtain is bright and sharp at its lower edge (on the
street side), with a magenta fringe there, and fades slowly toward the north (the back of the house)
through green into a faint red top. The curtains drift slowly back and forth across the house: where
a fold lies along a front run you see a long glowing stretch; where it crosses the Side or a porch
wall it is a bright point with a tail leaning to the back. Rays shimmer slowly along each curtain
and the whole display surges and eases. A seamless all-night loop."""
import numpy as np
from pixelhome.fx import DT, hexc, light, nframes, looped

CODE = 'IP08'
TITLE = 'Northern Lights'
KIND = 'ambient'
DESCRIPTION = ('Aurora curtains hang over the house and drift slowly across it: sharp green lower edges '
               'with a magenta fringe, fading north to red, rays shimmering along the folds.')

SKY = hexc('#081640')
GREEN = hexc('#2ee87a')
FRINGE = hexc('#d03a9a')
TOP = hexc('#a02a4a')
LOOP = 160.0


def render(G, seed=28):
    rng = np.random.default_rng(seed)
    x, z = G.pos[:, 0], G.pos[:, 2]

    def draw(D):
        out = np.zeros((nframes(D), G.N, 3), np.float32)
        curtains = []
        for c in range(3):
            curtains.append(dict(
                z0=-390 + rng.uniform(-60, 60), zA=rng.uniform(230, 330), zP=LOOP / rng.choice([1, 2]),
                zph=2 * np.pi * c / 3 + rng.uniform(-0.3, 0.3),
                k=rng.uniform(2 * np.pi / 900, 2 * np.pi / 500, 2), A=rng.uniform(50, 110, 2),
                w=rng.uniform(0.03, 0.07, 2) * 2 * np.pi * rng.choice([-1, 1], 2), ph=rng.uniform(0, 2 * np.pi, 2),
                rk=rng.uniform(2 * np.pi / 70, 2 * np.pi / 35, 3), rv=rng.uniform(10, 24, 3) * rng.choice([-1, 1]),
                rph=rng.uniform(0, 2 * np.pi, 3), amp=rng.uniform(0.75, 1.0),
                sP=rng.uniform(22, 40), sph=rng.uniform(0, 2 * np.pi)))
        for f in range(len(out)):
            t = f * DT
            g_I = np.zeros(G.N)
            m_I = np.zeros(G.N)
            r_I = np.zeros(G.N)
            for c in curtains:
                zc = (c['z0'] + c['zA'] * np.sin(2 * np.pi * t / c['zP'] + c['zph'])
                      + c['A'][0] * np.sin(c['k'][0] * x + c['w'][0] * t + c['ph'][0])
                      + c['A'][1] * np.sin(c['k'][1] * x + c['w'][1] * t + c['ph'][1]))
                s = z - zc                                     # > 0: street side of the lower edge
                edge = np.where(s > 0, np.exp(-(s / 14) ** 2), np.exp(s / 110))
                upper = np.where(s < 0, np.exp(-((s + 160) / 90) ** 2), 0)
                fringe = np.exp(-((s - 6) / 9) ** 2)
                rays = np.ones(G.N)
                for j in range(3):
                    rays += 0.28 * np.sin(c['rk'][j] * (x - c['rv'][j] * t) + c['rph'][j])
                rays = np.clip(rays, 0.2, 1.5) / 1.5
                surge = 0.75 + 0.25 * np.sin(2 * np.pi * t / c['sP'] + c['sph'])
                a = c['amp'] * surge
                g_I = np.maximum(g_I, a * edge * rays)
                m_I = np.maximum(m_I, a * fringe * rays)
                r_I = np.maximum(r_I, a * upper)
            col = light(SKY, 0.07) + light(GREEN, 0.40 * g_I) + light(FRINGE, 0.22 * m_I) \
                + light(TOP, 0.16 * r_I)
            out[f] = col
        return out
    return looped(draw, LOOP, floor=(0.06, SKY))
