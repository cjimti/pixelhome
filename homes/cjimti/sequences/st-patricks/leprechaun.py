"""The Leprechaun: a three-tone sprite (gold buckle, orange beard, green hat) darts in from the free
back end of Side and repaints the house's greens in orange and white as he runs. A porch light swept
from the street "looks": any segment it touches snaps back to green, so he hides behind the corners,
peeks with just his hat, camouflages himself, gets a double-take and bolts off the right free end.
Then a gold coin rolls back in, gets snatched away, and he does one last lap leaving gold behind."""
import numpy as np
from pixelhome.fx import DT, hexc, perc, light, keys, lerp, smoothstep, Flicker, nframes

CODE = 'SP01'
TITLE = 'The Leprechaun'
KIND = 'show'
DESCRIPTION = ('A leprechaun sneaks in from the back of the house and repaints it orange and white. '
               'Whenever the porch light looks, everything snaps back to innocent green.')

SEGS = ['Side', 'Left', 'Porch Left', 'Porch Front', 'Porch Right', 'Right']
BASE = {'Side': '#006a24', 'Left': '#00b040', 'Porch Left': '#44b400', 'Porch Front': '#00d890',
        'Porch Right': '#44b400', 'Right': '#00b040'}
ORANGE = hexc('#ff4a00')
CREAM = hexc('#ffc890')
PRANK = {'Side': CREAM, 'Left': ORANGE, 'Porch Left': CREAM, 'Porch Front': ORANGE, 'Porch Right': CREAM,
         'Right': ORANGE}
HAT = hexc('#30ff70')
BEARD = hexc('#ff3a00')
GOLD = hexc('#ffb000')
BEAM = hexc('#fff0d0')


def step(t, pts):
    """Piecewise-constant lookup: value of the last (time, value) at or before t."""
    v = pts[0][1]
    for tt, vv in pts:
        if t >= tt:
            v = vv
    return v


def windows(t, ws):
    return any(a <= t < b for a, b in ws)


def render(G, seed=17):
    rng = np.random.default_rng(seed)
    D = 54.0
    out = np.zeros((nframes(D), G.N, 3))
    n = G.N
    x = G.pd[G.path]
    P = G.pos[G.path]
    seg = G.seg_of[G.path]
    segmask = {s: seg == s for s in SEGS}
    base = np.zeros((n, 3))
    prank = np.zeros((n, 3))
    for s in SEGS:
        base[segmask[s]] = hexc(BASE[s])
        prank[segmask[s]] = PRANK[s]
    ang = np.arctan2(P[:, 0], 900 - P[:, 2])           # porch light on the lawn at (0, 900)
    breathe = Flicker(rng, n, 0.05, 0.25)
    twinkle = Flicker(rng, n, 2.0, 6.0)

    C1, C2, C5, E = 491.0, 894.0, 2033.0, G.length
    pos_k = [(0, -40), (2.0, -30), (2.8, 100), (3.3, 100), (4.0, 260), (4.4, 260), (5.1, C1 - 12),
             (5.6, C1 - 12), (7.6, C2 + 25), (12.5, C2 + 25), (12.8, C2 + 9), (14.3, C2 + 9),
             (15.9, C1 + 12), (16.6, C1 + 12), (21.0, C5 + 230), (26.8, C5 + 230), (27.8, E + 50),
             (39.9, E + 50), (39.95, -40), (40.6, -40), (40.9, 6), (41.3, 6), (44.4, E + 60),
             (49.2, E + 60), (49.4, E - 4), (50.8, E - 4), (51.0, E + 30)]
    dir_k = [(0, 1), (12.6, -1), (16.3, 1)]
    body_k = [(1.9, 0), (2.0, 1), (7.6, 1), (7.9, 0), (14.15, 0), (14.3, 1), (27.9, 1), (28.0, 0),
              (40.75, 0), (40.9, 1), (44.3, 1), (44.4, 0)]
    hat_k = [(1.9, 0), (2.0, 1), (7.6, 1), (7.9, 0), (12.8, 0), (12.95, 1), (13.35, 1), (13.45, 0),
             (13.85, 0), (13.95, 1), (27.9, 1), (28.0, 0), (40.5, 0), (40.6, 1), (44.3, 1), (44.4, 0),
             (49.4, 0), (49.5, 1), (49.7, 1), (49.8, 0), (50.15, 0), (50.25, 1), (50.45, 1), (50.55, 0)]
    paint_w = [(5.6, 7.6), (14.3, 15.9), (16.6, 21.0)]
    gold_w = [(41.3, 44.4)]
    cam_k = [(21.6, 0), (22.6, 1), (26.55, 1), (26.6, 0)]
    beam_on = [(8.3, 0), (8.8, 1), (11.6, 1), (12.1, 0), (21.6, 0), (22.0, 1), (28.4, 1), (28.9, 0),
               (35.6, 0), (36.0, 1), (38.4, 1), (38.9, 0)]
    beam_a = [(8.3, 0.56), (11.6, -0.56), (21.6, -0.56), (25.6, 0.52), (26.0, 0.52), (26.35, 0.338),
              (26.8, 0.338), (27.8, 0.56), (35.6, 0.05), (36.5, 0.405), (38.4, 0.405)]
    coin_k = [(33.0, E + 20), (35.6, E - 160), (37.25, E - 160), (37.55, E + 30)]

    amt = np.zeros(n)          # how far each pixel has been repainted
    tgt = np.zeros(n)
    snap = np.zeros(n)         # brief brightening where the light just restored a segment
    gold = np.zeros(n)
    prev = -40.0
    for f in range(len(out)):
        t = f * DT
        p = float(keys(t, pos_k))
        dr = step(t, dir_k)
        fade = keys(t, [(0, 0), (1.5, 1), (51.0, 1), (53.5, 0)])

        if windows(t, paint_w):
            lo, hi = min(prev, p) - 5, max(prev, p) + 5
            tgt[(x >= lo) & (x <= hi)] = 1
        if windows(t, gold_w):
            lo, hi = min(prev, p) - 5, max(prev, p) + 5
            gold[(x >= lo) & (x <= hi)] = 1
        prev = p

        bon = keys(t, beam_on)
        b = bon * np.exp(-((ang - keys(t, beam_a)) / 0.035) ** 2)
        for s in SEGS:
            m = segmask[s]
            if (tgt[m] > 0.5).any() and (b[m] > 0.4).any():
                tgt[m] = 0
                snap[m] = 1
        amt += (tgt - amt) * 0.3
        snap *= 0.93
        gold *= 0.985

        I = 0.30 * (1 + 0.08 * breathe(t)) * (1 + 0.55 * amt) + 0.25 * snap
        col = lerp(base, prank, amt[:, None])
        halo = 1 - 0.92 * np.exp(-((x - p) / 22) ** 2) * keys(t, body_k)
        fr = light(col, I * halo * fade)

        # the leprechaun: buckle (trailing), beard, hat (leading)
        cam = keys(t, cam_k)
        surprise = 0.6 * np.exp(-((t - 26.65) / 0.12) ** 2)
        bv, hv = keys(t, body_k), keys(t, hat_k)
        here = base[np.argmin(np.abs(x - p))]
        for off, c, a, vis, hides in [(-10, GOLD, 0.9, bv, 0), (0, BEARD, 0.95, bv, 1), (10, HAT, 1.0 + surprise, hv, 1)]:
            c = lerp(c, here, cam * hides)
            a = a * (1 - 0.7 * cam * hides)
            fr += light(c, a * vis * np.exp(-((x - (p + off * dr)) / 5.0) ** 2))
        if cam > 0.5:     # the buckle still glints while he pretends to be roof
            fr += light(GOLD, 0.5 * (0.5 + 0.5 * np.sin(2 * np.pi * 1.3 * t)) * np.exp(-((x - p + 10 * dr) / 4.0) ** 2))

        # gold trail of the finale
        fr += light(GOLD, gold * (0.55 + 0.45 * np.clip(twinkle(t), 0, 1)) * fade)

        # the coin that rolls back in, spinning as it slows
        if 33.0 <= t < 37.6:
            c = float(keys(t, coin_k))
            spin = abs(np.cos(2 * np.pi * (c - E) / 70))
            fr += light(GOLD, (0.35 + 0.65 * spin) * np.exp(-((x - c) / 4.0) ** 2))

        fr += light(BEAM, 0.55 * b)
        out[f][G.path] = fr
    return out
