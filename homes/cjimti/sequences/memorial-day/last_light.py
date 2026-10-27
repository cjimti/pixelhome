"""Last Light: The hour after sunset, painted by depth. The sun has gone down behind the back-left of
the house, so the far runs (the Porch Front, the back of the Side) hold the last rose and amber of the
horizon while the near wing fronts are already deep navy, with the receding runs grading between, as
evening air scatters the light. Long low clouds drift across from left to right, dark against the glow
with gold rims where the light catches them. One by one, a few first stars come out on the navy runs
near the street, hold, and fade. Everything here is periodic with the loop, so it never seams."""
import numpy as np
from pixelhome.fx import DT, hexc, perc, smoothstep, nframes, looped, colormap

CODE = 'MM10'
TITLE = 'Last Light'
KIND = 'ambient'
DESCRIPTION = ('The hour after sunset: the far porch keeps the last rose and amber of the horizon, the near '
               'wings are already navy, low clouds drift across and a few first stars come out.')

NAVY = hexc('#0b1d4a')
STAR = hexc('#e8eefa')
RIM = hexc('#ffc070')
SKY = colormap([(0.0, hexc('#0b1d4a')), (0.35, hexc('#1c2660')), (0.6, hexc('#5a2a5a')),
                (0.8, hexc('#b8404a')), (1.0, hexc('#ff8a3c'))])
LOOP = 180.0
X = 2600.0                     # period of the cloud field across x


def render(G, seed=10):
    rng = np.random.default_rng(seed)
    P = G.pos
    x, z = P[:, 0], P[:, 2]
    u = np.clip((-146 - z) / (637 - 146), 0, 1)                # 0 near the street, 1 far
    sun = np.exp(-(((x + 720) / 900) ** 2 + ((z + 820) / 520) ** 2))
    # clouds: a few long sinusoids in x that drift exactly one period per loop
    nc = [2, 3, 5, 7]
    ca = rng.uniform(0.5, 1.0, 4)
    cp = rng.uniform(0, 2 * np.pi, 4)
    # stars, only on the near and middle depths
    near = np.where(u < 0.4)[0]
    S = 16
    sk = rng.choice(near, S, replace=False)
    s_n = rng.integers(1, 3, S)                                 # appearances per loop
    s_p = rng.uniform(0, 1, S)
    s_tw = rng.integers(25, 50, S)                              # twinkle cycles per loop (~0.2 Hz)

    def draw(D):
        out = np.zeros((nframes(D), G.N, 3), np.float32)
        for f in range(len(out)):
            t = f * DT
            breathe = 0.06 * np.sin(2 * np.pi * 2 * t / LOOP)
            ue = np.clip(u + breathe * u, 0, 1)
            arg = 2 * np.pi * (x[:, None] / X - t / LOOP) * np.array(nc)[None, :] + cp
            cl = (np.sin(arg) * ca).sum(1) / ca.sum()
            cloud = smoothstep(0.15, 0.55, cl)                    # cloud bodies
            rim = np.exp(-((cl - 0.18) / 0.08) ** 2)              # their lit edges
            hz = ue ** 1.5 * (0.7 + 0.3 * sun)                    # how much horizon glow reaches here
            I = 0.07 + 0.3 * hz
            I = I * (1 - 0.45 * cloud * hz)
            col = perc(I)[:, None] * SKY(np.clip(ue * (0.85 + 0.25 * sun), 0, 1))
            col += perc(0.22 * rim * hz * (1 - cloud))[:, None] * RIM
            ph = (s_n * t / LOOP + s_p) % 1
            vis = smoothstep(0.0, 0.15, ph) * (1 - smoothstep(0.35, 0.5, ph))
            tw = 1 + 0.12 * np.sin(2 * np.pi * s_tw * t / LOOP + 7 * s_p)
            col[sk] += perc(0.3 * vis * tw)[:, None] * STAR
            out[f] = col
        return out
    return looped(draw, LOOP, floor=(0.06, NAVY))
