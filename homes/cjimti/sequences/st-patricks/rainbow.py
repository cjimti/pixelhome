"""Rainbow's End: a shower falls on the roof. Every drop kicks a 1-D wave equation that runs along the
whole path, turns the corners and reflects off the two free ends, so ripples cross and interfere.
The rain stops, the clouds' edge slides off and a real rainbow appears: each pixel's colour comes from
its angle to the antisolar point as seen from the street, so the bow cuts the wings and runs back
along the porch sides in perspective. Its right foot lands on the Porch Right / Right corner, where a
pot of gold bursts and spills coins along the roof."""
import numpy as np
from pixelhome.fx import DT, hexc, perc, light, keys, lerp, smoothstep, Flicker, colormap, nframes

CODE = 'SP02'
TITLE = "Rainbow's End"
KIND = 'show'
DESCRIPTION = ('A shower drums on the roof, ripples racing around the corners. The rain stops, a rainbow '
               'stands over the house in true perspective, and where it ends a pot of gold spills over.')

SLATE = hexc('#304a5a')
RIPPLE = hexc('#90e8d0')
SPLASH = hexc('#d8f0ff')
GRASS = hexc('#20c040')
SUN = hexc('#ffd890')
GOLD = hexc('#ffa400')
FLASH = hexc('#e0e8ff')

SPECTRUM = colormap([(0.0, hexc('#4800e0')), (0.18, hexc('#0050ff')), (0.38, hexc('#10ff30')),
                     (0.58, hexc('#ffc000')), (0.76, hexc('#ff5000')), (1.0, hexc('#ff0800'))])


def render(G, seed=23):
    rng = np.random.default_rng(seed)
    D = 58.0
    F = nframes(D)
    out = np.zeros((F, G.N, 3))
    n = G.N
    x = G.pd[G.path]
    P = G.pos[G.path]
    L = G.length

    # wave equation on a uniform grid along the path (free ends reflect)
    dx = 4.0
    g = np.arange(0, L + dx, dx)
    u = np.zeros(len(g))
    v = np.zeros(len(g))
    c, gamma, sub = 340.0, 2.2, 4
    hs = DT / sub

    # rain: a rate curve, then a fixed list of drops
    rate = lambda t: keys(t, [(2, 0), (4, 3), (10, 9), (14, 34), (22, 34), (27, 4), (30, 0)])
    drops = []
    t = 2.0
    while t < 30:
        r = max(rate(t), 0.5)
        t += rng.exponential(1 / r)
        if rate(t) > 0.3:
            drops.append((t, rng.uniform(0, L), rng.uniform(0.6, 1.4)))
    drops.sort()
    di = 0
    splash = np.zeros(n)

    # rainbow geometry: angle of each pixel from the antisolar point, seen from the street
    eye = np.array([16.0, 0.0, 1000.0])
    left_foot = G.pos[G.path[60]]                       # on Side, near the front-left corner
    pot_i = 380
    pot = (x[pot_i] + x[pot_i + 1]) / 2
    right_foot = (G.pos[G.path[pot_i]] + G.pos[G.path[pot_i + 1]]) / 2
    dl = (left_foot - eye) / np.linalg.norm(left_foot - eye)
    drr = (right_foot - eye) / np.linalg.norm(right_foot - eye)
    A = dl + drr
    A[1] -= 0.25                                         # antisolar point sits below the roof
    A /= np.linalg.norm(A)
    vv = (P - eye) / np.linalg.norm(P - eye, axis=1)[:, None]
    theta = np.degrees(np.arccos(np.clip(vv @ A, -1, 1)))
    R = np.degrees(np.arccos(np.clip(drr @ A, -1, 1))) + 0.4
    W = 6.0
    band = (theta - (R - W)) / W                        # 0 violet (inner) .. 1 red (outer)
    bow = np.clip(1 - np.abs(2 * band - 1), 0, 1) ** 0.6 * ((band > 0) & (band < 1))
    inside = 0.12 * smoothstep(0, -2.5, band) * (band < 0)   # sky is brighter inside a bow
    rcol = SPECTRUM(np.clip(band, 0, 1))
    reveal_x = P[:, 0]

    # pot of gold and spilled coins
    glint = Flicker(rng, n, 1.5, 5.0)
    nc = 26
    cv0 = rng.choice([-1, 1], nc) * rng.uniform(60, 420, nc)
    cdrag = rng.uniform(1.2, 2.4, nc)
    cspin = rng.uniform(2, 6, nc)
    T_POT = 42.0
    shimmer = Flicker(rng, n, 0.2, 0.8)
    wet = np.zeros(n)

    for f in range(F):
        t = f * DT
        # kick the strings for this frame's drops
        while di < len(drops) and drops[di][0] <= t:
            _, p, a = drops[di]
            u += 1.8 * a * np.exp(-((g - p) / 7) ** 2)
            k = np.argmin(np.abs(x - p))
            splash[k] = max(splash[k], a)
            di += 1
        for _ in range(sub):
            lap = np.empty_like(u)
            lap[1:-1] = u[2:] - 2 * u[1:-1] + u[:-2]
            lap[0], lap[-1] = u[1] - u[0], u[-2] - u[-1]
            v += (c * c * lap / (dx * dx) - gamma * v) * hs
            u += v * hs
        u -= u.mean()                                       # drops add momentum; keep the string centred
        v -= v.mean()
        w = np.abs(np.interp(x, g, u))
        wet = np.maximum(wet * 0.995, np.clip(w, 0, 1))

        clear = smoothstep(24, 34, t)
        edge = keys(t, [(25, -900), (36, 900)])            # clouds' edge slides off to the right
        sunlit = smoothstep(-120, 120, edge - P[:, 0])
        fade = keys(t, [(0, 0), (2, 1), (54, 1), (58, 0)])

        grey = 0.14 * (1 - 0.5 * sunlit * clear) * (1 + 0.1 * shimmer(t))
        fr = light(SLATE, grey * fade)
        fr += light(lerp(GRASS, SUN, 0.15), 0.32 * sunlit * clear * fade * (1 + 0.08 * shimmer(t)))
        fr += light(RIPPLE, 1.0 * np.clip(w, 0, 1.0) * (1 - 0.3 * clear))
        fr += light(SPLASH, splash)
        fr += light(SUN, 0.25 * wet * sunlit * clear * np.clip(glint(t), 0, 1) ** 3)  # wet roof glistens
        splash *= 0.72

        # one soft roll of lightning in the heaviest rain
        if 17.0 < t < 18.2:
            e = np.exp(-(t - 17.05) / 0.08) * (t >= 17.05) + 0.5 * np.exp(-((t - 17.4) / 0.06) ** 2)
            fr += light(FLASH, 0.45 * e * np.ones(n))

        # the rainbow, drawn in from its left foot toward the pot
        rb = keys(t, [(31, 0), (35, 0.7), (48, 0.78), (54, 0)])
        rx = keys(t, [(31, -700), (T_POT, right_foot[0] + 20)])
        rev = smoothstep(rx + 60, rx - 20, reveal_x)
        fr += light(rcol, rb * bow * rev)
        fr += light(SUN, rb * inside * rev)

        # the pot
        if t > 36:
            near = np.exp(-((x - pot) / 30) ** 2)
            heap = keys(t, [(36, 0), (T_POT - 0.3, 0.25), (T_POT, 1.0), (T_POT + 1.5, 0.7), (52, 0.7), (57.5, 0)])
            fr += light(GOLD, heap * near * (0.75 + 0.25 * glint(t)))
            if t > T_POT:
                tb = t - T_POT
                fr += light(SUN, 0.8 * np.exp(-tb / 0.35) * np.exp(-((x - pot) / 80) ** 2))
                cx = pot + cv0 / cdrag * (1 - np.exp(-cdrag * tb))
                cf = keys(t, [(T_POT, 1), (52, 1), (57.5, 0)])
                for j in range(nc):
                    sp = 0.4 + 0.6 * abs(np.cos(cspin[j] * np.exp(-0.5 * tb) * tb * 3 + j))
                    fr += light(GOLD, cf * 0.75 * sp * np.exp(-((x - cx[j]) / 3.2) ** 2))
        out[f][G.path] = fr
    return out
