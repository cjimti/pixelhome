"""Will-o'-the-Wisps: a small flock of bog lights lives on the roof all night. Each wisp follows
1-D boids rules along the path (cohesion with neighbours, matching their drift, keeping a little
space, a slow wander of its own), shies away from the two free ends and slows at the corners as if
peering round them. Now and then one strays off alone to lead someone astray, then is drawn back to
the others. Over a dark bottle-green bog with mist drifting through it."""
import numpy as np
from pixelhome.fx import DT, hexc, perc, light, smoothstep, smooth_noise, Flicker, nframes, looped

CODE = 'SP10'
TITLE = "Will-o'-the-Wisps"
KIND = 'ambient'
DESCRIPTION = ('A little flock of bog lights drifts along the roof all night, migrating from wing to wing, gathering, parting, '
               'pausing at the corners, one now and then wandering off on its own.')

BOG = hexc('#004820')
MIST = hexc('#4a9a70')
WISPS = [hexc('#b8ff90'), hexc('#ffe890'), hexc('#90ffd0')]
LOOP = 170.0


def render(G, seed=101):
    rng = np.random.default_rng(seed)

    def draw(Dur):
        F = nframes(Dur)
        out = np.zeros((F, G.N, 3), np.float32)
        n = G.N
        x = G.pd[G.path]
        L = G.length
        corners = np.array([491.0, 894.0, 1311.0, 1660.0, 2033.0])
        K = 9
        p = np.sort(rng.uniform(600, 1900, K))
        v = rng.normal(0, 8, K)
        wander_f = rng.uniform(0.01, 0.04, K)
        wander_p = rng.uniform(0, 2 * np.pi, K)
        cols = np.array([WISPS[i % 3] for i in range(K)])
        flick = Flicker(rng, K, 0.05, 0.3)
        mist = smooth_noise(rng, np.arange(0, 8000, 5.0), 160, octaves=2)
        strays = []
        t = rng.uniform(15, 30)
        while t < Dur:
            strays.append((t, int(rng.integers(K)), rng.choice([-1, 1])))
            t += rng.uniform(30, 50)
        for f in range(F):
            t = f * DT
            dpos = p[None, :] - p[:, None]               # [i, j] = p_j - p_i
            near = (np.abs(dpos) < 320) & ~np.eye(K, dtype=bool)
            cnt = np.maximum(near.sum(1), 1)
            coh = (dpos * near).sum(1) / cnt
            ali = ((v[None, :] - v[:, None]) * near).sum(1) / cnt
            close = (np.abs(dpos) < 55) & ~np.eye(K, dtype=bool)
            sep = -(np.sign(dpos) * (55 - np.abs(dpos)) * close).sum(1)
            acc = 0.012 * coh + 0.35 * ali + 0.9 * sep + 7 * np.sin(2 * np.pi * wander_f * t + wander_p)
            for ts, i, d in strays:                      # one wanders off to lead someone astray
                u = t - ts
                if 0 < u < 18:
                    acc[i] += d * 22 * np.sin(np.pi * u / 18) - 0.012 * coh[i] * np.sin(np.pi * u / 18)
            acc += 30 * (np.exp(-p / 90) - np.exp(-(L - p) / 90))     # shy of the free ends
            vhome = 0.36 * L * 2 * np.pi / 95 * np.cos(2 * np.pi * t / 95)
            home = L / 2 + 0.36 * L * np.sin(2 * np.pi * t / 95) + 0.08 * L * np.sin(2 * np.pi * t / 37)
            acc += 0.03 * (home - p) - 0.6 * (v - 0.8 * vhome)                    # the flock's slow migration up and down the roof
            v += acc * DT
            v *= 1 - 0.25 * DT
            slow = 1 - 0.55 * np.exp(-((p[:, None] - corners[None, :]) / 40) ** 2).sum(1)
            v = np.clip(v, -48, 48)
            p = np.clip(p + v * slow * DT, 5, L - 5)

            m = np.interp((x + 9 * t) % 8000, np.arange(0, 8000, 5.0), mist)
            fr = light(BOG, 0.12 + 0.03 * m) + light(MIST, 0.07 * smoothstep(0.1, 0.8, m))
            I = (0.3 + 0.08 * flick(t))[:, None] * np.exp(-((x[None, :] - p[:, None]) / 13) ** 2)
            halo = 0.08 * np.exp(-((x[None, :] - p[:, None]) / 60) ** 2)
            fr += np.einsum('kn,kc->nc', perc(I) + perc(halo) * 0.5, cols)
            out[f][G.path] = fr
        return out
    return looped(draw, LOOP, floor=(0.1, BOG))
