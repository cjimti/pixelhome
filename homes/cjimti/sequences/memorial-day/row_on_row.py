"""Row on Row: The roofline becomes a field of white grave markers. On the Side and porch runs, which
run away from the street, the markers stand in rows of equal depth, so from the street they converge
in perspective; far rows are dimmer and cooler, as if seen through evening air. First light sweeps from
the back of the house to the front and catches them row by row. Then, one by one, a small flag is
planted beside each marker, and the field rests before fading from the street back to the last row."""
import numpy as np
from pixelhome.fx import DT, hexc, perc, smoothstep, keys, lerp, nframes

CODE = 'MM03'
TITLE = 'Row on Row'
KIND = 'show'
DESCRIPTION = ('White grave markers stand in rows that recede from the street. First light finds them row '
               'by row, then a small flag is planted beside each one.')

STONE = hexc('#f2f1ec')
FAR = hexc('#9fb2d8')
NAVY = hexc('#0b1d4a')
RED = hexc('#d0141e')
BLUE = hexc('#2a48c0')
GOLD = hexc('#ffd080')

Z_NEAR, Z_FAR = -146.0, -637.0


def render(G, seed=3):
    rng = np.random.default_rng(seed)
    D = 70.0
    out = np.zeros((nframes(D), G.N, 3))
    P, pd = G.pos, G.pd
    markers = []                                       # (centre pd, depth 0..1, x, segment idx, dir)
    for name in ('Side', 'Porch Left', 'Porch Right'):
        idx = G.seg[name]
        zs, ds = P[idx, 2], pd[idx]
        o = np.argsort(zs)
        for zk in np.arange(-178.0, -637.0, -46.0):
            if zs.min() + 10 < zk < zs.max() - 10:
                markers.append((np.interp(zk, zs[o], ds[o]), (Z_NEAR - zk) / (Z_NEAR - Z_FAR), P[idx[0], 0], idx))
    for name in ('Left', 'Porch Front', 'Right'):
        idx = G.seg[name]
        xs, ds = P[idx, 0], pd[idx]
        o = np.argsort(xs)
        zk = P[idx, 2].mean()
        for xk in 16 + 42.0 * np.arange(-15, 16):
            if xs.min() + 12 < xk < xs.max() - 12:
                markers.append((np.interp(xk, xs[o], ds[o]), (Z_NEAR - zk) / (Z_NEAR - Z_FAR), xk, idx))
    M = len(markers)
    depth = np.array([m[1] for m in markers])
    mx = np.array([m[2] for m in markers])
    # dawn: a plane of light moves from the back of the house to the street
    reveal = 7.0 + 15.0 * (1 - depth) + np.abs(mx - 16) / 900.0
    # flags in: nearest rows first, left to right within a row, a steady walking pace
    order = np.lexsort((mx, np.round(depth, 2)))
    plant = np.empty(M)
    plant[order] = 27.0 + np.arange(M) * (20.0 / M) + rng.uniform(-0.08, 0.08, M)
    fade = 59.0 + 6.0 * depth
    jitter = rng.uniform(0.92, 1.05, M)

    # per-marker pixel weights (soft-edged stone, and the two halves of a flag a little along the path)
    W = np.zeros((M, G.N)); FR = np.zeros((M, G.N)); FB = np.zeros((M, G.N))
    for k, (c, dep, x, idx) in enumerate(markers):
        dd = pd[idx] - c
        W[k, idx] = 1 - smoothstep(5.0, 9.0, np.abs(dd))
        FR[k, idx] = np.exp(-((dd - 15.0) / 3.2) ** 2)
        FB[k, idx] = np.exp(-((dd - 21.0) / 2.8) ** 2)
    stone_col = lerp(STONE, FAR, depth[:, None] ** 0.8)            # aerial perspective
    stone_I = 0.62 * (1 - 0.42 * depth) * jitter

    for f in range(len(out)):
        t = f * DT
        fr = out[f]
        fr += perc(keys(t, [(0, 0), (4, 0.09), (64, 0.09), (69.5, 0)])) * NAVY
        u = t - reveal
        catch = np.exp(-((u - 0.4) / 0.5) ** 2) * 0.35              # the first ray glints on each stone
        on = smoothstep(0, 1.2, u) * (1 - smoothstep(0, 1.6, t - fade))
        sI = stone_I * on + catch * (t < fade)
        fr += (W * perc(sI)[:, None]).T @ stone_col
        # the dawn plane itself, a faint gold sheet passing over the roof
        zp = lerp(Z_FAR - 40, Z_NEAR + 80, smoothstep(7, 22, t))
        sheet = 0.18 * np.exp(-((P[:, 2] - zp) / 45) ** 2) * keys(t, [(6, 0), (8, 1), (21, 1), (24, 0)])
        fr += perc(sheet)[:, None] * GOLD
        # flags
        v = t - plant
        flag = smoothstep(0, 0.25, v) * (1 - smoothstep(0, 1.6, t - fade - 0.3))
        flick = 1 + 0.18 * np.sin(2 * np.pi * (0.45 * t - mx / 260.0)) * smoothstep(48, 52, t)
        glint = 0.5 * np.exp(-((v - 0.12) / 0.12) ** 2)
        fI = (0.64 * (1 - 0.3 * depth) * flick) * flag
        fr += (perc(fI) @ FR)[:, None] * RED + (perc(fI * 0.95) @ FB)[:, None] * BLUE
        fr += (perc(glint) @ FR)[:, None] * GOLD
    return out
