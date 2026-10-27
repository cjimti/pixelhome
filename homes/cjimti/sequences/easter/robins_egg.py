"""Robin's Egg: All-night loop. The roofline is a robin's-egg-blue shell whose cocoa speckles are
grown, not placed: a Gray-Scott reaction-diffusion runs along the whole path, and its spots
split, drift and fade as a slow wave of "feed" travels around the house, so the speckling is
always quietly rearranging itself and never repeats within the loop. A faint warm breath, like a
nesting bird's warmth, passes along under the shell."""
import numpy as np
from pixelhome.fx import DT, hexc, perc, light, smoothstep, nframes, looped

CODE = 'EA08'
TITLE = "Robin's Egg"
KIND = 'ambient'
DESCRIPTION = "A robin's-egg-blue roofline whose speckles are grown by reaction-diffusion: spots split, drift and fade all night, never quite the same."


def lin(h):
    return hexc(h) ** 2.2


SHELL = lin('#7fd8d4')
SHELL_DEEP = lin('#5fb8e0')
SPECK = lin('#c27a4a')
SPECK_EDGE = lin('#b9a0ff')
WARM = lin('#ffd9a8')
FLOOR = 0.12
LOOP = 150.0


def render(G, seed=28):
    rng = np.random.default_rng(seed)
    n = G.N
    pdp = G.pd[G.path]
    z = G.pos[G.path, 2]
    h = np.diff(pdp) / np.mean(np.diff(pdp))          # true spacing, so spots keep their size on every run
    hl = np.concatenate([[h[0]], h])
    hr = np.concatenate([h, [h[-1]]])
    depth = smoothstep(-150, -640, z)
    k_rate = 0.06
    steps = 7

    def lap(a):
        al = np.concatenate([[a[1]], a[:-1]])
        ar = np.concatenate([a[1:], [a[-2]]])
        return 2 / (hl + hr) * ((ar - a) / hr - (a - al) / hl)

    def draw(D):
        out = np.zeros((nframes(D), n, 3), np.float32)
        u = np.ones(n)
        v = np.zeros(n)
        for c in rng.integers(0, n, 14):
            v[max(0, c - 3):c + 3] = 0.5
            u[max(0, c - 3):c + 3] = 0.5
        step = 0

        def advance(u, v, step):
            F = 0.035 + 0.008 * np.sin(2 * np.pi * (pdp / 1250 - step / 16000))
            uvv = u * v * v
            u += 0.2 * lap(u) - uvv + F * (1 - u)
            v += 0.1 * lap(v) + uvv - (F + k_rate) * v
            return step + 1

        for _ in range(24000):                                   # grow the first speckles off-stage
            step = advance(u, v, step)
        for f in range(len(out)):
            t = f * DT
            for _ in range(steps):
                step = advance(u, v, step)
            sp = smoothstep(0.08, 0.3, v)
            edge = smoothstep(0.03, 0.12, v) * (1 - sp)
            breath = 0.06 * np.exp(-((((pdp - 16 * t) % G.length) - G.length / 2) / 260) ** 2)
            shell_col = SHELL * (1 - 0.4 * depth[:, None]) + SHELL_DEEP * 0.4 * depth[:, None]
            buf = light(shell_col, (0.27 + breath) * (1 - 0.55 * sp))
            buf += light(SPECK, 0.34 * sp) + light(SPECK_EDGE, 0.16 * edge)
            buf += light(WARM, breath * 1.4)
            out[f][G.path] = buf
        return out
    return looped(draw, LOOP, floor=(FLOOR, SHELL))
