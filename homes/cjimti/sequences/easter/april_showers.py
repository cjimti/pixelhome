"""April Showers: The roofline is a water surface. A 1-D wave equation runs along the whole path
(true spacing per run, waves turn the corners, reflect from the two free ends): every raindrop that
lands kicks it, and rings run off both ways, crossing and interfering. Drizzle, then a downpour
with one roll of lightning, then it eases off and only the gutters at the five corners keep
dripping. The sun comes out, a pastel rainbow stands across both wings in mirror image, and
shoots come up where the most rain fell."""
import numpy as np
from pixelhome.fx import DT, hexc, perc, light, keys, smoothstep, nframes

CODE = 'EA06'
TITLE = 'April Showers'
KIND = 'show'
DESCRIPTION = 'The roof becomes water: each raindrop sends ripples running around the corners and bouncing off the ends. Then the gutters drip, a pastel rainbow stands over the wings and shoots come up where the rain fell.'


def lin(h):
    return hexc(h) ** 2.2


WATER = lin('#3f78e0')
CREST = lin('#c8f2ff')
SPLASH = lin('#ffffff')
FLASH = lin('#dcd6ff')
SHOOT = lin('#6ee07a')
BUDS = [lin(h) for h in ('#ff8fbf', '#ffe17a', '#c39bff', '#fff3f6', '#8fd0ff')]
BOW = [(0.0, '#ff9aa8'), (0.2, '#ffc08a'), (0.4, '#fff09a'), (0.6, '#a8f0b0'), (0.8, '#a8d0ff'), (1.0, '#c8a8ff')]
CORNERS = [80.5, 178.5, 260.5, 331.5, 380.5]


def render(G, seed=26):
    rng = np.random.default_rng(seed)
    D = 64.0
    F = nframes(D)
    out = np.zeros((F, G.N, 3))
    pdp = G.pd[G.path]
    pp = G.pos[G.path]
    n = G.N

    # rain: drizzle, downpour, easing; then the corners drip like gutters
    drops = []
    t = 3.0
    while t < 41:
        rate = keys(t, [(3, 2.0), (12, 3.5), (16, 9), (30, 10), (36, 4), (41, 0.5)])
        t += rng.exponential(1 / rate)
        drops.append((t, rng.uniform(0, G.length), rng.uniform(0.6, 1.3)))
    corner_d = [np.interp(c, np.arange(n), pdp) for c in CORNERS]
    for k, cd in enumerate(corner_d):
        t = 33.0 + k * 0.7
        period = 1.6 + 0.35 * k
        while t < 50:
            drops.append((t, cd, 1.1 * keys(t, [(33, 0.6), (40, 1.0), (50, 0.4)])))
            t += period * rng.uniform(0.9, 1.1)
    drops.sort()
    dt_, dp_, da_ = (np.array(v) for v in zip(*drops))
    wet = np.zeros(n)
    for p, a in zip(dp_[dt_ < 41], da_[dt_ < 41]):
        wet += a * np.exp(-((pdp - p) / 25) ** 2)

    # shoots where it was wettest, kept apart
    sprouts = []
    order = np.argsort(-(wet + 0.6 * rng.random(n)))
    for i in order:
        if all(abs(pdp[i] - pdp[j]) > 55 for j, _, _ in sprouts):
            sprouts.append((i, 45 + rng.uniform(0, 6), BUDS[len(sprouts) % len(BUDS)]))
        if len(sprouts) >= 30:
            break

    # wave equation on the non-uniform path grid
    h = np.diff(pdp)
    hl = np.concatenate([[h[0]], h])
    hr = np.concatenate([h, [h[-1]]])
    c, gamma, sub = 270.0, 0.7, 4
    ds = DT / sub
    u = np.zeros(n)
    v = np.zeros(n)

    def lap(u):
        ul = np.concatenate([[u[1]], u[:-1]])     # mirrored ends: free (Neumann) boundaries
        ur = np.concatenate([u[1:], [u[-2]]])
        return 2 / (hl + hr) * ((ur - u) / hr - (u - ul) / hl)

    centre = np.array([16.0, -390.0])
    rr = np.hypot(pp[:, 0] - centre[0], pp[:, 2] - centre[1])
    bow_x = np.array([b[0] for b in BOW])
    bow_c = np.array([lin(b[1]) for b in BOW])
    j = 0
    K = 55.0

    for f in range(F):
        t = f * DT
        while j < len(dt_) and dt_[j] <= t:
            x = pdp - dp_[j]
            v -= K * da_[j] * (np.exp(-(x / 12) ** 2) - 0.5 * np.exp(-(x / 24) ** 2))   # zero net push
            j += 1
        for _ in range(sub):
            v += ds * (c * c * lap(u) - gamma * v - 4.0 * u)
            u += ds * v
        sky = keys(t, [(0, 0), (2.5, 1), (60, 1), (64, 0)])
        rain = keys(t, [(40, 1), (48, 0.55)])
        crest = np.clip(-u, 0, None)
        trough = np.clip(u, 0, None)
        I = (0.2 + 0.05 * rain) * (1 - 0.75 * np.clip(trough * 3, 0, 1))
        buf = light(WATER, I * sky) + light(CREST, np.clip(crest * 2.4, 0, 1) * sky * 0.85)

        # splashes
        recent = (dt_ <= t) & (dt_ > t - 0.25)
        for tt, p, a in zip(dt_[recent], dp_[recent], da_[recent]):
            buf += light(SPLASH, 0.9 * a * np.exp(-(t - tt) / 0.05) * np.exp(-((pdp - p) / 4) ** 2))

        # one roll of lightning in the downpour
        for t0, amp in ((31.0, 0.4), (31.13, 0.25), (31.3, 0.55)):
            if 0 <= t - t0 < 0.3:
                buf += light(FLASH, amp * np.exp(-(t - t0) / 0.05))

        # sun and rainbow: pastel bands at a fixed radius from the porch, crossing both wings
        sun = smoothstep(44, 50, t) * keys(t, [(58, 1), (63, 0)])
        if sun > 0:
            buf *= 1 - 0.4 * sun
            r0 = keys(t, [(45, 150.0), (51, 420.0)])
            q = (rr - (r0 - 130)) / 260
            inside = (q > 0) & (q < 1)
            bow = np.stack([np.interp(q, bow_x, bow_c[:, k]) for k in range(3)], -1)
            edge = np.sin(np.pi * np.clip(q, 0, 1)) ** 0.5
            buf = buf * (1 - 0.8 * (inside * sun)[:, None]) + perc(0.72 * sun * edge * inside)[:, None] * bow

        # shoots: green widening, then a pastel bud opens at the tip
        for i, t0, col in sprouts:
            a = t - t0
            if a <= 0:
                continue
            x = pdp - pdp[i]
            g = smoothstep(0, 3, a) * keys(t, [(59, 1), (63.5, 0)])
            w = 2 + 6 * smoothstep(0, 4, a)
            buf += light(SHOOT, 0.55 * g * np.exp(-(x / w) ** 2))
            b = smoothstep(4, 6, a) * keys(t, [(59, 1), (63.5, 0)])
            buf += light(col, 0.75 * b * np.exp(-(x / (1.5 + 2.5 * b)) ** 2))
        out[f][G.path] = buf
    return out
