"""Butterflies: All-night loop. A small flock of pastel butterflies drifts around the house. They
are boids along the roofline (cohesion, separation, alignment and a wandering urge, so they
gather, scatter and turn back together), but each one actually flies in 3-D a little off the roof:
its glow is lit by true distance, so it brightens as it flutters in close, softens as it drifts
away, and lights both runs at once when it cuts across a corner. Wings open and close slowly:
two soft lobes that spread apart and fold together."""
import numpy as np
from pixelhome.fx import DT, hexc, light, smoothstep, smooth_noise, nframes, looped

CODE = 'EA09'
TITLE = 'Butterflies'
KIND = 'ambient'
DESCRIPTION = 'A flock of pastel butterflies drifts around the house all night: gathering, scattering and turning together, fluttering close to the roof and away, wings slowly opening and folding.'


def lin(h):
    return hexc(h) ** 2.2


MEADOW = lin('#3f8f6a')
DUSK = lin('#6a5ad0')
COLS = [lin(h) for h in ('#ff9ac8', '#ffe28a', '#b9a0ff', '#8fe8c0', '#9fd0ff', '#ffb894', '#f4c8ff', '#fff1b8',
                         '#ff9ac8', '#9fd0ff')]
FLOOR = 0.12
LOOP = 160.0


def render(G, seed=29):
    rng = np.random.default_rng(seed)
    n = G.N
    pdp = G.pd[G.path]
    pp = G.pos[G.path]
    L = G.length
    depth = smoothstep(-150, -640, pp[:, 2])
    meadow_tex = 0.85 + 0.15 * smooth_noise(rng, pdp, 60)

    def draw(D):
        F = nframes(D)
        out = np.zeros((F, n, 3), np.float32)
        B = len(COLS)
        tt = np.arange(F) * DT
        s = rng.uniform(300, L - 300, B)
        v = rng.choice([-1, 1], B) * rng.uniform(10, 25, B)
        wander = np.array([smooth_noise(rng, tt, 9.0) for _ in range(B)])
        offx = np.array([smooth_noise(rng, tt, 5.0) for _ in range(B)]) * 8
        offz = np.array([smooth_noise(rng, tt, 6.0) for _ in range(B)]) * 8
        offy = np.array([smooth_noise(rng, tt, 4.0) for _ in range(B)]) * 12 + 12
        flap_f = rng.uniform(0.35, 0.6, B)
        flap_p = rng.uniform(0, 2 * np.pi, B)
        bg = light(MEADOW, 0.19 * meadow_tex * (1 - 0.5 * depth)) + light(DUSK, 0.15 * depth)
        for f in range(F):
            t = tt[f]
            d = s[None, :] - s[:, None]                         # d[i, j] = s_j - s_i
            near = (np.abs(d) < 320) & (np.abs(d) > 0)
            cnt = np.maximum(near.sum(1), 1)
            coh = (d * near).sum(1) / cnt
            ali = (v[None, :] * near).sum(1) / cnt - v * (near.sum(1) > 0)
            close = (np.abs(d) < 45) & (np.abs(d) > 0)
            sep = -(np.sign(d) * (45 - np.abs(d)) * close).sum(1)
            acc = 0.012 * coh + 0.25 * ali + 0.35 * sep + 9 * wander[:, f]
            acc += 30 * (smoothstep(160, 0, s) - smoothstep(L - 160, L, s))  # turn back near the free ends
            v += acc * DT
            sp = np.abs(v)
            v = np.sign(v) * np.clip(sp, 8, 34)
            v = np.where((s < 40) & (v < 0), -v, v)
            v = np.where((s > L - 40) & (v > 0), -v, v)
            s = np.clip(s + v * DT, 5, L - 5)

            buf = bg.copy()
            for b in range(B):
                c = np.array([np.interp(s[b], pdp, pp[:, k]) for k in range(3)])
                ahead = np.array([np.interp(s[b] + 4, pdp, pp[:, k]) for k in range(3)])
                tan = (ahead - c) / max(1e-6, np.linalg.norm(ahead - c))
                c = c + np.array([offx[b, f], 0, offz[b, f]])     # a little off the line: cuts corners
                lift = np.exp(-(offy[b, f] / 30) ** 2)              # higher above the roof = softer
                fl = 0.5 + 0.5 * np.cos(2 * np.pi * flap_f[b] * t + flap_p[b])   # 1 open, 0 folded
                span = 3 + 8 * fl
                I = (0.26 + 0.1 * fl) * lift
                for side in (-1, 1):
                    dd = np.linalg.norm(pp - (c + side * span * tan), axis=1)
                    buf += light(COLS[b], I * np.exp(-(dd / (7 + 2 * (1 - fl))) ** 2))
                body = np.exp(-(np.linalg.norm(pp - c, axis=1) / 5) ** 2)
                buf += light(lin('#fff6e8'), 0.16 * lift * body)
            buf = np.minimum(buf, 0.42 ** 2.2)              # two crossing butterflies never blow out
            out[f][G.path] = buf
        return out
    return looped(draw, LOOP, floor=(FLOOR, MEADOW))
