"""Four Faces: The facade, seen from the street, is a picture plane (x across, distance back = up) and
a granite relief of four colossal heads is carved into it: two on the wing fronts, two straddling
the porch sides, whose steep runs slice them top to bottom like a profile. Each pixel is shaded from
the relief's surface normal and soft cast shadows. Floodlights strike one by one at night, then a
day passes in under a minute: low raking dawn, high noon, sunset, and alpenglow on the high ground."""
import numpy as np
from pixelhome.fx import DT, hexc, light, smoothstep, keys, lerp, nframes

CODE = 'PR04'
TITLE = 'Four Faces'
KIND = 'show'
DESCRIPTION = ('Four granite heads carved into the facade. Floodlights strike one by one, then a whole day '
               'rakes across the relief, shadows swinging from dawn to sunset.')

GRANITE = hexc('#ffe4c4')
SKY = hexc('#20348c')
FLOOD = hexc('#fff0d8')
BRICK = hexc('#c83018')
BRASS = hexc('#ff9a38')
ROSE = hexc('#e04860')

# (x, y, radius) in the street-view picture plane (y = distance back from the street)
FACES = [(-430.0, 175.0, 180.0), (-196.0, 385.0, 165.0), (152.0, 385.0, 165.0), (405.0, 205.0, 180.0)]


def _relief(X, Y, rng):
    """Height field (picture units) of the carved mountain."""
    H = np.zeros_like(X)
    for (cx, cy, R) in FACES:
        u, v = (X - cx) / R, (Y - cy) / R
        r2 = u * u + v * v / 1.3
        head = np.sqrt(np.clip(1 - r2, 0, None))
        g = lambda a, b, su, sv: np.exp(-((u - a) / su) ** 2 - ((v - b) / sv) ** 2)
        h = (0.9 * head + 0.16 * g(0, 0.3, 0.55, 0.07)                   # brow ridge
             - 0.16 * g(-0.3, 0.12, 0.13, 0.08) - 0.16 * g(0.3, 0.12, 0.13, 0.08)   # eye sockets
             + 0.32 * g(0, -0.05, 0.1, 0.22)                              # nose
             - 0.08 * g(0, -0.42, 0.25, 0.04)                             # mouth
             + 0.12 * g(0, -0.7, 0.25, 0.1)                               # chin
             + 0.06 * g(-0.55, -0.15, 0.15, 0.25) + 0.06 * g(0.55, -0.15, 0.15, 0.25))  # cheekbones
        H = np.maximum(H, R * 0.85 * h)
    k = rng.uniform(0.004, 0.02, (6, 2)) * rng.choice([-1, 1], (6, 2))
    ph = rng.uniform(0, 2 * np.pi, 6)
    rough = sum(np.sin(X * k[i, 0] + Y * k[i, 1] + ph[i]) for i in range(6)) / 6
    return H + 14 * rough + 0.04 * Y            # rock, rising gently toward the back


def render(G, seed=24):
    rng = np.random.default_rng(seed)
    D = 72.0
    out = np.zeros((nframes(D), G.N, 3))
    X, Y = G.pos[:, 0], -G.pos[:, 2]
    # relief on a grid, sampled bilinearly
    gx = np.arange(-800, 820, 5.0)
    gy = np.arange(0, 820, 5.0)
    GX, GY = np.meshgrid(gx, gy, indexing='ij')
    Hg = _relief(GX, GY, rng)
    dHx, dHy = np.gradient(Hg, 5.0, 5.0)

    def sample(A, x, y):
        fx = np.clip((x - gx[0]) / 5.0, 0, len(gx) - 1.001)
        fy = np.clip((y - gy[0]) / 5.0, 0, len(gy) - 1.001)
        i, j = fx.astype(int), fy.astype(int)
        a, b = fx - i, fy - j
        return (A[i, j] * (1 - a) * (1 - b) + A[i + 1, j] * a * (1 - b) + A[i, j + 1] * (1 - a) * b +
                A[i + 1, j + 1] * a * b)

    H = sample(Hg, X, Y)
    n = np.stack([-sample(dHx, X, Y), -sample(dHy, X, Y), np.ones(G.N)], -1)
    n /= np.linalg.norm(n, axis=1, keepdims=True)
    # crevices see less sky (cheap occlusion from the local curvature)
    lap = (sample(Hg, X + 12, Y) + sample(Hg, X - 12, Y) + sample(Hg, X, Y + 12) + sample(Hg, X, Y - 12) - 4 * H)
    occl = np.clip(1 + lap / 30, 0.4, 1.1)

    def shade(l, soft=10.0, steps=12, step=22.0):
        l = np.asarray(l, float)
        l = l / np.linalg.norm(l)
        lam = np.clip(n @ l, 0, None) ** 1.4
        flat = np.hypot(l[0], l[1])
        if flat < 1e-3:
            return lam
        dx, dy, rise = l[0] / flat, l[1] / flat, l[2] / flat
        block = np.full(G.N, -1e9)
        for k in range(1, steps + 1):
            d = k * step
            block = np.maximum(block, sample(Hg, X + dx * d, Y + dy * d) - (H + rise * d))
        return lam * smoothstep(soft, -soft, block)

    faces = [(np.exp(-(((X - cx) / (1.25 * R)) ** 2 + ((Y - cy) / (1.4 * R)) ** 2))) for cx, cy, R in FACES]
    strike = [4.0, 8.5, 13.0, 17.5]
    fl_rng = rng.uniform(0, 1, (4, 64))
    flood_dirs = [(0.35, -0.45, 1.0), (0.2, -0.5, 1.0), (-0.2, -0.5, 1.0), (-0.35, -0.45, 1.0)]
    flood_sh = [shade(d) for d in flood_dirs]

    for f in range(len(out)):
        t = f * DT
        fr = out[f]
        sky = keys(t, [(0, 0), (2, 0.09), (28, 0.09), (36, 0.16), (56, 0.16), (64, 0.1), (69, 0.08), (72, 0)])
        fr += light(SKY, sky * occl)

        # floodlights strike one by one, sputter, and settle
        off = keys(t, [(30, 1), (36, 0)])
        for k in range(4):
            ts = strike[k]
            if t < ts:
                continue
            u = t - ts
            sput = 1.0 if u > 1.2 else (0.3 + 0.7 * (fl_rng[k, int(u * 40) % 64] > 0.45))
            warm = smoothstep(0, 2.5, u)
            I = off * sput * (0.2 + 0.8 * warm) * faces[k] * (0.15 + 0.85 * flood_sh[k])
            col = lerp(BRASS, FLOOD, warm)
            fr += light(col, 0.85 * I * GRANITE.max())

        # the day: the sun climbs from the left, passes overhead in front, sets on the right
        if 30 <= t < 64:
            u = np.clip((t - 32) / 28, 0, 1)
            az = np.pi * u                                         # 0 = due left, pi = due right
            el = 0.06 + 0.5 * np.sin(np.pi * u)
            l = (-np.cos(az) * np.cos(el), 0.5 * np.sin(el), 0.2 + 0.6 * np.sin(el))
            sh = shade(l, soft=8 + 10 * np.sin(np.pi * u))
            sun = keys(t, [(30, 0), (34, 0.7), (46, 0.75), (58, 0.7), (62, 0.3), (64, 0)])
            warmth = np.sin(np.pi * u)
            col = lerp(BRICK, lerp(BRASS, GRANITE, 0.7 * np.clip(warmth * 1.6 - 0.6, 0, 1)), np.clip(warmth * 2.5, 0, 1))
            fr += light(col, sun * sh)
        # alpenglow: after sunset the high ground keeps a rose light
        if t >= 58:
            ag = keys(t, [(58, 0), (62, 0.55), (66, 0.4), (71, 0)])
            high = smoothstep(300, 600, Y + 0.3 * H)
            fr += light(ROSE, ag * high * np.clip(0.4 + 0.6 * n[:, 1] + 0.4 * n[:, 2], 0, 1))
    return out
