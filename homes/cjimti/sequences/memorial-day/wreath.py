"""Wreath: Two bearers, points of candle gold, step in measured cadence along the wing fronts from the
far ends of the house toward the porch, mirror images of each other. At the porch mouth they lay the
wreath: it grows up both porch sides and closes across the Porch Front, a braid of two counter-turning
strands, gold and silver, that slowly plait around the ring. A red ribbon is tied at the bottom where the
ring meets the wings, its tails trailing onto the wing fronts. The bearers step back and hold; the house
goes quiet around the wreath."""
import numpy as np
from pixelhome.fx import DT, hexc, perc, smoothstep, keys, lerp, Flicker, nframes

CODE = 'MM06'
TITLE = 'Wreath'
KIND = 'show'
DESCRIPTION = ('Two bearers walk in step toward the porch and lay a single wreath, a slowly plaiting braid '
               'of gold and silver tied with a red ribbon.')

GOLD = hexc('#ffb848')
SILVER = hexc('#dbe4f2')
RED = hexc('#c8101a')
NAVY = hexc('#0b1d4a')
CANDLE = hexc('#ffd690')

STEP_T = 0.95      # seconds per step
STEP_L = 25.0      # layout units per step


def render(G, seed=6):
    rng = np.random.default_rng(seed)
    D = 62.0
    out = np.zeros((nframes(D), G.N, 3))
    P, pd = G.pos, G.pd
    pdp = pd[G.path]
    x = P[:, 0]
    wings = np.concatenate([G.seg['Left'], G.seg['Right']])
    ring = np.concatenate([G.seg['Porch Left'], G.seg['Porch Front'], G.seg['Porch Right']])
    a0, a1 = pdp[179], pdp[380]                # the two ends of the ring, at the porch mouth
    half = (a1 - a0) / 2
    s_ring = pd[ring] - a0                    # 0..2*half along the ring
    from_end = np.minimum(s_ring, 2 * half - s_ring)
    leaf = 1 + 0.12 * (rng.random(len(ring)) - 0.5)
    shimmer = Flicker(rng, len(ring), 0.08, 0.3)
    XM = 16.0                                  # the facade's mirror line
    x_start = 596.0                            # bearer distance from the mirror line at the start
    x_end = {-1: XM + 215.0, 1: 173.0 - XM}    # where each stops, just short of the porch mouth
    n_steps = int(np.ceil((x_start - min(x_end.values())) / STEP_L))
    T_WALK = 5.0
    T_ARRIVE = T_WALK + n_steps * STEP_T
    T_LAY0, T_LAY1 = T_ARRIVE + 1.5, T_ARRIVE + 8.5
    T_BOW = T_LAY1 + 1.0
    T_BACK = T_BOW + 3.5

    def bearer_offset(t, side):
        # both bearers take the same number of steps, so the left one's are a touch shorter
        sl = (x_start - x_end[side]) / n_steps
        k = max(0.0, (t - T_WALK) / STEP_T)
        i = np.floor(k)
        stepped = min(n_steps, i + smoothstep(0.05, 0.7, k - i))
        # after the bow, two slow steps back, then hold
        back = 2 * sl * smoothstep(0, 1.6, t - T_BACK) if t > T_BACK else 0.0
        return x_start - sl * stepped + back

    for f in range(len(out)):
        t = f * DT
        fr = out[f]
        quiet = smoothstep(T_BACK + 2, T_BACK + 8, t)
        fr += perc(keys(t, [(0, 0), (3, 0.1), (D - 5, 0.1), (D, 0)]) * (1 - 0.35 * quiet)) * NAVY
        # bearers: candle-gold points, a slight lift as each foot comes down
        k = (t - T_WALK) / STEP_T
        foot = 0.12 * np.exp(-(((k % 1) - 0.72) / 0.08) ** 2) if T_WALK < t < T_ARRIVE else 0.0
        bI = keys(t, [(1, 0), (4, 0.75), (T_BACK + 6, 0.6), (D - 4, 0.0)]) + foot
        for side in (-1, 1):
            bx = XM + side * bearer_offset(t, side)
            d = np.abs(x[wings] - bx)
            fr[wings] += perc(bI * np.exp(-(d / 7.5) ** 2))[:, None] * CANDLE
        # the wreath grows up both porch sides from the mouth and closes at the porch front
        grow = smoothstep(T_LAY0, T_LAY1, t) * half * 1.02
        vis = 1 - smoothstep(grow - 18, grow, from_end)
        # two strands, counter-turning: a plait that slowly travels round the ring
        lam = 46.0
        ph = 2 * np.pi * s_ring / lam
        w = 2 * np.pi * 0.12 * t
        A = 0.5 + 0.5 * np.cos(ph - w)
        B = 0.5 + 0.5 * np.cos(ph + w + np.pi)
        lvl = 0.5 * (1 + 0.05 * shimmer(t)) * leaf * keys(t, [(T_LAY0, 1), (D - 7, 1), (D - 1.5, 0)])
        lvl = lvl * (1 + 0.15 * quiet)
        col = perc(lvl * (0.35 + 0.65 * A ** 1.5))[:, None] * GOLD * 0.9 + \
            perc(lvl * 0.85 * (0.3 + 0.7 * B ** 1.5))[:, None] * SILVER * 0.6
        # bright tip where each half is still growing
        tip = 0.35 * np.exp(-((from_end - grow) / 10) ** 2) * (t < T_LAY1 + 0.5)
        fr[ring] += col * vis[:, None] + perc(tip)[:, None] * CANDLE
        # the ribbon: a knot at the bottom of each side of the ring, tails trailing onto the wing fronts
        bow = smoothstep(T_BOW, T_BOW + 1.5, t) * keys(t, [(D - 7, 1), (D - 1, 0)])
        knot = np.exp(-(from_end / 14) ** 2)
        fr[ring] = fr[ring] * (1 - 0.8 * bow * knot[:, None]) + perc(0.6 * bow * knot)[:, None] * RED
        for side, c in ((-1, pdp[178]), (1, pdp[381])):
            d = np.abs(pd[wings] - c)
            sway = 1 + 0.1 * np.sin(2 * np.pi * 0.3 * t + side)
            tail = smoothstep(0, 4, d) * (1 - smoothstep(26 * sway, 36 * sway, d)) * smoothstep(0, 1.2, (t - T_BOW) * 40 / np.maximum(d, 1))
            fr[wings] += perc(0.48 * bow * tail)[:, None] * RED
    return out
