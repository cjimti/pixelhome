"""Red Drink: The porch is a glass. Two pitchers at the free ends of the roof pour red drink; every drop
is a particle that runs downhill along the roofline toward the middle of the porch, piles up against
the others (position-based packing, so the level really rises), and fills the U of the porch until it
climbs the porch sides. Fizz rises and pops at the surface. Then a straw goes in: slurp by slurp the
level falls back, the last drops rattle, and the glass lets out a satisfied pink glow (and a burp)."""
import numpy as np
from pixelhome.fx import DT, hexc, perc, light, smoothstep, keys, lerp, Flicker, nframes

CODE = 'JT05'
TITLE = 'Red Drink'
KIND = 'show'
DESCRIPTION = ('The porch is a glass. Pitchers at both ends of the roof pour red drink that runs down to the '
               'porch and fills it up, fizzing. Then somebody gets a straw.')

DRINK = hexc('#e00a1e')
DEEP = hexc('#7a0010')
FOAM = hexc('#ff7080')
FIZZ = hexc('#ffd0d8')
GLASS = hexc('#90c0ff')
PITCHER = hexc('#ffe0b0')
WHITE = hexc('#ffffff')


def render(G, seed=5):
    rng = np.random.default_rng(seed)
    D = 62.0
    out = np.zeros((nframes(D), G.N, 3))
    pdp = G.pd[G.path]
    L = G.length
    segs = dict(G.path_segments())
    pf = segs['Porch Front']
    c = pdp[pf].mean()
    glass = np.zeros(G.N, bool)
    for n in ('Porch Left', 'Porch Front', 'Porch Right'):
        glass[segs[n]] = True

    R = 4.6                      # one drop's share of the roofline
    NP = 280                     # drops in total, half from each end
    x = np.zeros(0)
    v = np.zeros(0)
    POUR0, POUR1 = 3.0, 24.0
    rate = NP / (POUR1 - POUR0)
    emitted = 0.0
    SLURP0 = 39.0
    sips = []
    t_ = SLURP0
    while t_ < 53:
        sips.append(t_)
        t_ += rng.uniform(0.25, 0.42) if (len(sips) % 5) else 0.9          # five sips, breathe
    bubbles = []                  # [x, speed, birth]
    pops = []                     # (x, t)
    fl = Flicker(rng, G.N, 1.0, 3.0)
    g = 520.0
    empty_at = None

    for f in range(len(out)):
        t = f * DT
        buf = np.zeros((G.N, 3))

        # pour: drops leave each spout with a little speed
        if POUR0 <= t < POUR1:
            emitted += rate * DT
            while emitted >= 1:
                emitted -= 1
                side = 1 if len(x) % 2 == 0 else -1
                x = np.append(x, 8.0 if side > 0 else L - 8.0)
                v = np.append(v, side * rng.uniform(120, 180))

        # straw: remove drops at the bottom of the glass in slurps
        suck = 0.0
        for s0 in sips:
            u = t - s0
            if 0 <= u < 0.25:
                suck = max(suck, np.sin(np.pi * u / 0.25))
        if suck > 0 and len(x):
            near = np.argsort(np.abs(x - c))
            k = int(rng.random() < suck * 0.95) + int(rng.random() < suck * 0.6)
            keep = np.ones(len(x), bool)
            keep[near[:k]] = False
            x, v = x[keep], v[keep]
            if len(x) == 0 and empty_at is None:
                empty_at = t

        # simulate: gravity toward the bottom of the glass, drag, then pack the drops
        if len(x):
            for _ in range(2):
                h = DT / 2
                v += -np.sign(x - c) * g * h * smoothstep(0, 6, np.abs(x - c))
                v *= np.exp(-1.6 * h)
                xo = x.copy()
                x = x + v * h
                o = np.argsort(x)
                xs = x[o]
                for _ in range(12):
                    gap = np.diff(xs)
                    push = np.clip(R - gap, 0, None) * 0.5
                    xs[:-1] -= push
                    xs[1:] += push
                x[o] = xs
                v = 0.8 * (x - xo) / h + 0.2 * v
                x = np.clip(x, 0, L)

        # draw the drink: a density field of drops
        if len(x):
            dens = np.zeros(G.N)
            xs = np.sort(x)
            lo, hi = xs[0], xs[-1]
            idx = np.searchsorted(xs, pdp)
            for k in (-2, -1, 0, 1):
                j = np.clip(idx + k, 0, len(xs) - 1)
                dens += np.exp(-((pdp - xs[j]) / (0.6 * R)) ** 2)
            dens = np.clip(dens, 0, 1)
            # the body of the pile (packed drops) vs drops still running
            packed = np.zeros(len(xs), bool)
            if len(xs) > 1:
                packed[1:] |= np.diff(xs) < R * 1.25
                packed[:-1] |= np.diff(xs) < R * 1.25
            depth = np.minimum(pdp - lo, hi - pdp)
            body = dens * (0.72 + 0.08 * fl(t))
            col = lerp(FOAM, lerp(DRINK, DEEP, 0.6 * smoothstep(60, 260, depth)[:, None]), smoothstep(0, 18, depth)[:, None])
            buf += light(col, body)
            run = np.zeros(G.N)
            for xr in xs[~packed]:
                run = np.maximum(run, np.exp(-((pdp - xr) / 6) ** 2))
            buf += light(FOAM, 0.5 * run)

            # fizz: bubbles rise away from the bottom and pop at the surface
            if 14 < t < SLURP0 + 10 and hi - lo > 60 and rng.random() < 0.22:
                bubbles.append([c + rng.uniform(-60, 60), rng.choice([-1, 1]) * rng.uniform(35, 80), t])
            alive = []
            for b in bubbles:
                b[0] += b[1] * DT
                if lo + 3 < b[0] < hi - 3:
                    alive.append(b)
                    buf += light(FIZZ, 0.32 * np.exp(-((pdp - b[0]) / 3.5) ** 2))
                else:
                    pops.append((np.clip(b[0], lo, hi), t))
            bubbles = alive
        for px, pt in pops[-40:]:
            u = t - pt
            if u < 0.3:
                buf += light(FIZZ, 0.8 * np.exp(-u / 0.08) * np.exp(-((pdp - px) / 5) ** 2))

        # the pitchers at the two free ends, tipping while they pour
        tip = keys(t, [(1, 0), (3, 1), (POUR1, 1), (POUR1 + 1.5, 0)])
        for e in (0.0, L):
            buf += light(PITCHER, 0.6 * tip * np.exp(-((pdp - e) / 14) ** 2))

        # the glass: a faint cool outline on the porch U
        gI = keys(t, [(0, 0), (2, 0.12), (D - 3, 0.12), (D, 0)])
        buf += light(GLASS, gI * glass)

        # the straw's slurp, the rattle at the bottom, then a satisfied glow and a burp
        if suck > 0:
            buf += light(WHITE, 0.25 * suck * np.exp(-((pdp - c) / 8) ** 2))
        if empty_at is not None:
            u = t - empty_at
            if u < 1.4:
                rattle = (rng.random(G.N) < 0.25) * np.exp(-((pdp - c) / 18) ** 2)
                buf += light(FOAM, 0.6 * rattle)
            ahh = keys(u, [(1.4, 0), (2.5, 0.5), (5, 0.5), (6.5, 0)])
            buf += light(FOAM, ahh * glass)
            ub = u - 4.2
            if 0 <= ub < 1.5:
                ring = np.exp(-((np.abs(pdp - c) - 260 * ub) / 18) ** 2) * np.exp(-ub / 0.5)
                buf += light(FIZZ, 0.9 * ring + 0.7 * np.exp(-ub / 0.1) * np.exp(-((pdp - c) / 30) ** 2))
        out[f][G.path] = buf
    return out
