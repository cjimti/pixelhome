"""Rosebuds: a Gray-Scott reaction-diffusion simulation runs along the whole roofline, all night. Its
parameters sit where spots self-replicate, so each bud swells and splits in two, and the buds slowly
colonise the roof from both sides of any gap. Two slow 'wilt' fronts drift along the path where the
chemistry is tipped against them: buds there fade away, and behind each front the empty stretch is
re-seeded by its neighbours splitting their way back in. Buds turn the corners with the path."""
import numpy as np
from pixelhome.fx import DT, hexc, perc, light, smoothstep, lerp, Flicker, colormap, nframes, looped

CODE = 'VD10'
TITLE = 'Rosebuds'
KIND = 'ambient'
DESCRIPTION = ('Rosebuds grow along the roof by themselves: each one swells and splits in two. Slow wilting '
               'fronts drift through, and the buds split their way back into the space they leave.')

WINE = hexc('#a00008')
FLOOR_COLOR = hexc('#b00818')
FLOOR = 0.1
LOOP = 168.0
STEPS = 8                      # reaction-diffusion steps per frame

BUD = colormap([(0.0, tuple(WINE * 0.0)), (0.12, (0.06, 0.0, 0.004)), (0.3, (0.12, 0.002, 0.012)),
                (0.42, (0.17, 0.008, 0.02)), (0.5, (0.19, 0.03, 0.02))])


def render(G, seed=30):
    rng = np.random.default_rng(seed)
    n = G.N
    x = np.arange(n, dtype=float)
    Du, Dv = 0.2, 0.1
    F0, K0 = 0.045, 0.062

    def lap(a):
        return np.r_[a[1], a[:-1]] + np.r_[a[1:], a[-2]] - 2 * a

    def draw(D):
        F = nframes(D)
        out = np.zeros((F, n, 3), np.float32)
        u, v = np.ones(n), np.zeros(n)
        for c in rng.integers(10, n - 10, 10):
            v[c - 3:c + 3] = 0.5
            u[c - 3:c + 3] = 0.25
        shimmer = Flicker(rng, n, 0.04, 0.15)
        wilt_speed = (n + 160) / 140.0                 # pixels per second
        phase = rng.uniform(0, n)

        def kill(t):
            k = np.full(n, K0)
            for off, sgn in ((0.0, 1), (0.5, -1)):
                pos = ((t * wilt_speed + phase + off * (n + 160)) % (n + 160)) - 80
                xx = x if sgn > 0 else n - 1 - x
                k += 0.006 * np.exp(-((xx - pos) / 28) ** 2)
            return k

        def feed(t):                                  # a slow travelling ripple in the feed keeps it restless
            return F0 + 0.006 * np.sin(2 * np.pi * (x / 170 - t / 210))

        for _ in range(30000):                        # grow the garden before the first frame
            uvv = u * v * v
            fd = feed(-60.0)
            u += Du * lap(u) - uvv + fd * (1 - u)
            v += Dv * lap(v) + uvv - (fd + K0) * v
        for f in range(F):
            t = f * DT
            k = kill(t)
            fd = feed(t)
            for _ in range(STEPS):
                uvv = u * v * v
                u += Du * lap(u) - uvv + fd * (1 - u)
                v += Dv * lap(v) + uvv - (fd + k) * v
            vv = np.clip(v, 0, 0.5)
            I = FLOOR + 0.3 * smoothstep(0.05, 0.45, vv) * (1 + 0.06 * shimmer(t))
            hue = smoothstep(0.1, 0.45, vv)[:, None]
            col = lerp(FLOOR_COLOR, hexc('#ff2448'), hue)
            col = lerp(col, hexc('#ff7838'), smoothstep(0.4, 0.5, vv)[:, None] * 0.6)
            out[f][G.path] = perc(I)[:, None] * col
        return out
    return looped(draw, LOOP, fade=20.0, floor=(FLOOR, FLOOR_COLOR))
