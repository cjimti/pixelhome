"""First Snow: Flakes fall through 3-D space onto the roofline. Each one glints as it drifts down past
the line and, if it lands on the roof, adds to the snow lying at that spot; the snow settles, creeps
a little and drifts deeper into the corners. Now and then the cornice at one of the two free ends
gives way and slides off the end of the roof. Dim, slow and seamless for all night."""
import numpy as np
from pixelhome.fx import DT, hexc, perc, light, smoothstep, lerp, Flicker, nframes, looped

CODE = 'XM07'
TITLE = 'First Snow'
KIND = 'ambient'
DESCRIPTION = ('Snow falls through the air past the roofline and settles on it, drifting into the corners. '
               'Now and then the snow at a free end slides off the edge.')

NIGHT = hexc('#0a1850')
SNOW = hexc('#c8d8ff')
SNOW_DEEP = hexc('#e8eeff')
FLAKE = hexc('#f0f4ff')
FLOOR = 0.1
LOOP = 150.0


def render(G, seed=27):
    rng = np.random.default_rng(seed)
    Pp = G.pos[G.path]                                   # positions in path order
    x = G.pd[G.path]
    n = G.N
    Ltr = G.length
    corners = np.array([(x[i] + x[i + 1]) / 2 for i in (80, 178, 260, 331, 380)])
    catch = 1 + 0.9 * np.exp(-((x[:, None] - corners[None]) / 35) ** 2).sum(1)   # eddies pile snow
    catch *= 1.25 - 0.25 * np.clip(np.minimum(x, Ltr - x) / 150, 0, 1)          # cornices build at the ends
    tex = 1 + 0.12 * Flicker(rng, n, 0.01, 0.04)(0.0)

    def draw(D):
        out = np.zeros((nframes(D), G.N, 3), np.float32)
        K = 260
        fp = np.zeros((K, 3))
        fv = rng.uniform(26, 42, K)
        fph = rng.uniform(0, 2 * np.pi, (K, 2))
        fsw = rng.uniform(0.2, 0.5, K)
        TAU = 160.0                                      # slow settling / sublimation
        RATE = 0.0045                                    # depth per second per pixel, before catch
        depth = RATE * TAU * catch * (0.8 + 0.2 * tex)
        depth = np.minimum(depth, 1.0)
        tw = Flicker(rng, n, 0.05, 0.25)

        def respawn(k, y0=None):
            j = rng.integers(n)
            fp[k] = Pp[j] + np.array([rng.normal(0, 30), 0, rng.normal(0, 30)])
            fp[k, 1] = rng.uniform(170, 420) if y0 is None else y0

        for k in range(K):
            respawn(k)
        # slides: (time, end) alternate ends; each takes the snow in the last stretch over the edge
        slides, t = [], rng.uniform(18, 30)
        end = int(rng.integers(2))
        while t < D:
            slides.append((t, end))
            end = 1 - end
            t += rng.uniform(24, 36)
        slab, prev = {}, {}
        wind = lambda t: 14 * np.sin(2 * np.pi * t / 47) + 8 * np.sin(2 * np.pi * t / 19 + 1)

        for f in range(len(out)):
            t = f * DT
            # flakes fall, sway and drift with the wind
            w = wind(t)
            fp[:, 1] -= fv * DT
            fp[:, 0] += (w + 12 * np.sin(2 * np.pi * fsw * t + fph[:, 0])) * DT
            fp[:, 2] += 10 * np.sin(2 * np.pi * fsw * t * 0.8 + fph[:, 1]) * DT
            near = fp[:, 1] < 200
            glow = np.zeros(n)
            if near.any():
                q = fp[near]
                d = np.linalg.norm(Pp[None] - q[:, None], axis=2)
                a = smoothstep(200, 155, q[:, 1])
                glow = (a[:, None] * np.exp(-(d / 7) ** 2)).max(0)
            landed = np.nonzero(fp[:, 1] <= 150)[0]
            squall = 0.25 + 1.5 * np.sin(np.pi * t / LOOP) ** 2      # heavy, then a lull; one cycle per loop
            for k in landed:
                dxz = np.hypot(Pp[:, 0] - fp[k, 0], Pp[:, 2] - fp[k, 2])
                j = int(np.argmin(dxz))
                if dxz[j] < 12:
                    splat = np.exp(-((x - x[j]) / 7) ** 2)
                    depth += 0.15 * squall * catch[j] * splat / 2.2
                respawn(k, rng.uniform(380, 440))
            depth *= np.exp(-DT / TAU)
            depth = np.minimum(depth, 1.15)
            # a little creep: snow levels itself out
            depth[1:-1] += 0.02 * (depth[2:] - 2 * depth[1:-1] + depth[:-2])

            # cornice slides at the free ends: the last stretch of snow accelerates over the edge
            slide_glint = np.zeros(n)
            for k, (ts, e) in enumerate(slides):
                u = t - ts
                if 0 <= u < 3.2:
                    from_end = x if e == 0 else Ltr - x
                    order = np.argsort(from_end)
                    zone = smoothstep(150, 120, from_end)    # the slab breaks along a crack line
                    if k not in slab:
                        slab[k] = depth * zone
                        prev[k] = slab[k]
                    s = 10 * u + 22 * u ** 2                # it creeps, then rushes over the edge
                    moved = np.interp(from_end + s, from_end[order], slab[k][order], right=0)
                    moved *= smoothstep(0, 6, from_end)     # what passes the end is gone
                    depth = np.clip(depth - prev[k], 0, None) + moved
                    prev[k] = moved
                    slide_glint += moved * (0.5 + 0.5 * np.sin(from_end * 0.5 + 20 * u))

            I = 0.06 + 0.3 * np.clip(depth, 0, 1.0) ** 1.4 * (1 + 0.06 * tw(t))
            col = lerp(SNOW, SNOW_DEEP, np.clip(depth - 0.6, 0, 0.5)[:, None] * 2)
            buf = perc(I)[:, None] * col + light(NIGHT, np.full(n, 0.08))
            buf += light(FLAKE, 0.3 * glow + 0.16 * slide_glint)
            out[f][G.path] = buf
        return out
    return looped(draw, LOOP, floor=(FLOOR, NIGHT))
