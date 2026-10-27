"""Unchained: The roofline is one long chain, drawn link by link (face-on ovals and edge-on bars, so the
link pitch beats against each run's pixel spacing and shimmers as the chain strains). It heaves under
tension. A link on the porch glows hot and snaps; every freed piece is a rigid body on its own
damped spring, so the halves whip apart and settle while gaps open at the breaks. The snaps run
outward corner by corner. Then the iron warms to gold, the pieces lift off their anchors and leave
through the house's two free ends, and the roof they leave behind is lit warm and clear."""
import numpy as np
from pixelhome.fx import DT, hexc, perc, light, smoothstep, keys, lerp, Flicker, nframes

CODE = 'JT07'
TITLE = 'Unchained'
KIND = 'show'
DESCRIPTION = ('The roof is one long iron chain under strain. A link on the porch glows hot and snaps, the breaks '
               'run out corner by corner, the pieces recoil, warm to gold, and leave through the two free ends.')

IRON = hexc('#5878a8')
HEAT = hexc('#ff3a08')
HOT = hexc('#ffd090')
GOLD = hexc('#ffb040')
SPARK = hexc('#fff0d0')
DAWN = hexc('#ff9050')

PITCH = 24.0


def links(m):
    """Chain texture at material coordinate m (perceptual intensity)."""
    q = m / PITCH
    k = np.floor(q)
    u = q - k
    face = 0.85 * (np.exp(-(u / 0.11) ** 2) + np.exp(-((1 - u) / 0.11) ** 2)) + 0.18
    edge = 0.7 * (1 - smoothstep(0.28, 0.42, np.abs(u - 0.5)))
    return np.where(k % 2 == 0, face, edge)


def render(G, seed=7):
    rng = np.random.default_rng(seed)
    D = 56.0
    out = np.zeros((nframes(D), G.N, 3))
    pdp = G.pd[G.path]
    L = G.length
    segs = G.path_segments()
    corner = lambda a, b: 0.5 * (pdp[a] + pdp[b])
    c = pdp[G.pi[G.seg['Porch Front']]].mean()
    # (time, material position) of each snap: the porch first, then out corner by corner
    breaks = [(17.0, c), (21.0, corner(260, 261)), (21.6, corner(331, 332)), (24.6, corner(178, 179)),
              (25.4, corner(380, 381)), (28.4, corner(80, 81))]
    EXIT = 40.0
    # pieces: [m0, m1, offset, velocity, rest offset]; a piece shows material m at x = m + offset
    pieces = [[-60.0, L + 60.0, 0.0, 0.0, 0.0]]
    done = set()
    sparks = []
    creak = Flicker(rng, G.N, 3.0, 7.0)
    shimmer = Flicker(rng, G.N, 0.5, 1.5)

    for f in range(len(out)):
        t = f * DT
        # tension: the chain heaves harder and harder until the first snap (a stretch about the porch)
        heave = keys(t, [(0, 0), (4, 0.02), (16.5, 0.07)]) * (0.5 + 0.5 * np.sin(2 * np.pi * t / keys(t, [(0, 3.0), (16, 1.2)])))
        stretch = 1 + heave if len(pieces) == 1 else 1.0

        for k, (tb, mb) in enumerate(breaks):
            if t >= tb and k not in done:
                done.add(k)
                for i, p in enumerate(pieces):
                    if p[0] < mb < p[1]:
                        m0, m1, o, v, r = p
                        # the halves whip apart, then settle a little way off with the slack taken up
                        left = [m0, mb, o, v - rng.uniform(260, 340), r - 13]
                        right = [mb, m1, o, v + rng.uniform(260, 340), r + 13]
                        if m0 < 0:                       # a piece shackled to a free end barely moves
                            left[3] *= 0.35
                            left[4] = r - 4
                        if m1 > L:
                            right[3] *= 0.35
                            right[4] = r + 4
                        pieces[i:i + 1] = [left, right]
                        xb = mb + o
                        for _ in range(14):
                            sparks.append([xb, rng.normal(0, 140), t, rng.uniform(0.3, 0.9)])
                        break

        # piece dynamics: each is a rigid body on a damped spring, then the final departure
        for p in pieces:
            if t > EXIT:
                side = -1 if 0.5 * (p[0] + p[1]) < c else 1
                p[4] += side * 22 * (t - EXIT) ** 1.6 * DT
            acc = -55 * (p[2] - p[4]) - 6 * p[3]
            p[3] += acc * DT
            p[2] += p[3] * DT

        # draw each piece where it now lies
        warm = smoothstep(31, 38, t)
        I = np.zeros(G.N)
        heat = np.zeros(G.N)
        for m0, m1, o, v, r in pieces:
            m = c + (pdp - o - c) / stretch
            inside = (m > m0 + 2) & (m < m1 - 2)
            edge_fade = smoothstep(m0, m0 + 6, m) * smoothstep(m1, m1 - 6, m)
            I = np.where(inside, links(m) * edge_fade, I)
            for tb, mb in breaks:                         # links about to go glow hot and creak
                pre = smoothstep(tb - 2.5, tb, t) * (t < tb)
                if pre > 0:
                    g = np.exp(-((m - mb) / 14) ** 2) * inside
                    heat = np.maximum(heat, pre * g * (0.8 + 0.2 * creak(t)))
        base = keys(t, [(0, 0), (2.5, 0.42), (31, 0.42), (38, 0.55)])
        col = lerp(IRON, GOLD, warm)
        buf = light(col, base * I * (1 + 0.08 * shimmer(t) * warm))
        buf += light(lerp(HEAT, HOT, heat[:, None] ** 2), heat * 0.9)

        # where the chain has gone, the roof stays lit: warm and clear
        if t > EXIT:
            gone = (I < 0.02).astype(float)
            clear = keys(t, [(EXIT, 0), (EXIT + 6, 0.4), (D - 6, 0.48), (D - 0.5, 0)])
            glow = lerp(DAWN, GOLD, (0.5 + 0.5 * np.sin(pdp / 300 - 0.4 * t))[:, None])
            buf += light(glow, clear * gone * (0.85 + 0.15 * shimmer(t)))

        # snap sparks: they fly along the roof and fade
        alive = []
        for sp in sparks:
            u = t - sp[2]
            if u < sp[3]:
                x = sp[0] + sp[1] * (1 - np.exp(-u / 0.25)) * 0.25
                buf += light(SPARK, np.exp(-u / (0.4 * sp[3])) * np.exp(-((pdp - x) / 4) ** 2))
                alive.append(sp)
            if u < 0.25:
                buf += light(SPARK, 0.8 * np.exp(-u / 0.06) * np.exp(-((pdp - sp[0]) / 18) ** 2) / 4)
        sparks = alive
        buf *= keys(t, [(D - 0.5, 1), (D, 0)])
        out[f][G.path] = buf
    return out
