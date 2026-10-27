"""Old Glory: The house, seen from above, becomes a flag. The Side run is the pole (its back end the
top), the flag's hoist hangs from it and the cloth flies out across the whole roof toward the
right free end. A colour guard runs the furled flag up the pole; the wind takes it and it unfurls.
The cloth is a height field moving in 3-D: waves travel from hoist to fly, growing toward the
loose end; their slopes shade the folds (light and shadow rolling across the stripes) and the
cloth's sway slides stripes across the wings, so the runs that cross the flag show all thirteen
stripes and the canton, and the runs that lie along a stripe ripple between red and white. Stars
are points in the cloth, so they glint as the folds carry them past pixels. Then the wind drops
and the flag droops, and a last breeze lifts it again."""
import numpy as np
from pixelhome.fx import DT, hexc, perc, light, smoothstep, keys, lerp, Flicker, nframes

CODE = 'IN04'
TITLE = 'Old Glory'
KIND = 'show'
DESCRIPTION = ('The Side is the flagpole and the whole roof is the flag. It is run up the pole, unfurls in the '
               'wind and flies in 3D: folds roll across the stripes, stars glint, then the wind drops.')

RED = hexc('#ff1010')
WHITE = hexc('#f4ece4')
BLUE = hexc('#1424c8')
STAR = hexc('#ffffff')
POLE = hexc('#ffc060')
NIGHT = hexc('#060c2c')


def render(G, seed=24):
    rng = np.random.default_rng(seed)
    D = 62.0
    F = nframes(D)
    out = np.zeros((F, G.N, 3))
    P = G.pos
    side = G.seg['Side']
    X0, X1 = -596.0, 640.0                    # hoist (the pole) to fly
    Z0, Z1 = -650.0, -105.0                   # top of the flag (back of the house) to bottom (street side)
    u0 = (P[:, 0] - X0) / (X1 - X0)
    v0 = (P[:, 2] - Z0) / (Z1 - Z0)
    u0 = np.where(G.seg_of == 'Side', 0.012, u0)  # the hoist edge hangs right on the pole
    fl = Flicker(rng, G.N, 0.2, 0.9)

    # stars: 50 points in the canton (rows of 6 and 5), canton = 7 stripes deep, 0.4 of the length
    cu, cv = 0.40, 7 / 13
    stars = []
    for r in range(9):
        cols = 6 if r % 2 == 0 else 5
        for c in range(cols):
            su = (c + (0.5 if r % 2 == 0 else 1.0)) / 6 * cu
            sv = (r + 0.7) / 10 * cv
            stars.append((su, sv))
    stars = np.array(stars)
    star_tw = rng.uniform(0, 2 * np.pi, len(stars))

    wind = lambda t: keys(t, [(0, 0.0), (12, 0.25), (16, 0.75), (22, 1.0), (28, 0.8), (31, 1.2), (36, 0.9),
                              (41, 1.0), (45, 0.35), (49, 0.12), (53, 0.12), (56, 0.6), (62, 0.5)])
    unfurl = lambda t: keys(t, [(11.5, 0.0), (19, 1.0), (45, 1.0), (50, 0.72), (53, 0.7), (57, 1.0)])
    phase = 0.0
    for f in range(F):
        t = f * DT
        w = wind(t)
        phase += DT * (1.6 + 2.4 * w) * 2 * np.pi * 0.45
        um = unfurl(t)
        fade = keys(t, [(0, 0.0), (2, 1.0), (D - 2.5, 1.0), (D, 0.0)])
        buf = light(NIGHT, 0.07 * fade * np.ones(G.N))

        if t >= 11.0:
            # the cloth: waves from hoist to fly, amplitude growing toward the free edge and with the wind
            uu = u0 / max(um, 0.05)                          # cloth coordinate once partly unfurled
            A = (0.05 + 0.95 * np.clip(uu, 0, 1.3)) * (0.25 + 0.75 * w)
            psi = 2 * np.pi * (1.4 * uu - 0.07 * v0) * 1.0 - phase
            psi2 = 2 * np.pi * (2.7 * uu + 0.6 * v0) - 1.7 * phase + 1.3
            h = A * (np.sin(psi) + 0.35 * np.sin(psi2))
            slope = A * (1.4 * np.cos(psi) + 0.35 * 2.7 * np.cos(psi2))
            droop = (1 - w) * 0.10 * np.clip(uu, 0, 1) ** 1.5    # no wind: the fly end sags down the stripes
            vs = v0 - 0.085 * h + droop * (1 - v0) * 0.6 - 0.02 * droop
            us = uu + 0.015 * np.cos(psi)
            shade = np.clip(0.72 + 0.45 * slope, 0.22, 1.3)
            shade *= 1 + 0.04 * fl(t)
            # stripes with soft edges (sub-pixel), canton, stars
            sv = vs * 13
            stripe = np.floor(sv)
            edge = np.abs(sv - np.round(sv))
            red_w = np.where(stripe % 2 == 0, 1.0, 0.0)
            soft = smoothstep(0.0, 0.12, edge)
            red_w = lerp(0.5, red_w, soft)
            in_canton = smoothstep(cu + 0.008, cu - 0.008, us) * smoothstep(cv + 0.01, cv - 0.01, vs)
            col = lerp(lerp(WHITE * 0.55, RED, red_w[:, None]), BLUE * 0.8, in_canton[:, None])
            d2 = (((us[:, None] - stars[None, :, 0]) * (X1 - X0)) ** 2 +
                  ((vs[:, None] - stars[None, :, 1]) * (Z1 - Z0)) ** 2)
            tw = 0.8 + 0.2 * np.sin(2 * np.pi * 0.7 * t + star_tw)
            starI = (np.exp(-d2 / 9 ** 2) * tw[None]).sum(1) * in_canton
            # where the cloth exists: up to the (fluttering) fly edge
            edge_u = 1 + 0.03 * np.sin(2 * np.pi * (3 * v0) - 1.9 * phase) * (0.3 + w)
            cloth = smoothstep(edge_u * 1.0 + 0.02, edge_u * 1.0 - 0.02, uu) * (vs > -0.02) * (vs < 1.02)
            I = 0.62 * shade * cloth
            buf = buf * (1 - cloth[:, None]) + col * perc(I)[:, None] * fade
            buf += light(STAR, np.clip(starI, 0, 1) * 0.85 * cloth * fade)
            # the loose edge catches the light
            buf += light(WHITE, 0.25 * w * cloth * smoothstep(edge_u - 0.08, edge_u, uu) * fade)

        # the pole and the colour guard running the flag up it
        pole = np.zeros(G.N)
        pole[side] = 0.16 * fade
        if t < 12.0:
            zt = keys(t, [(2.5, -140.0), (11.0, -630.0)])
            dz = P[side, 2] - zt
            bundle = np.exp(-(dz / 22) ** 2) * smoothstep(2.0, 3.0, t)
            below = (dz > 0) * 0.12 * smoothstep(2.0, 3.0, t)      # the halyard
            stripes_k = 0.5 + 0.5 * np.sin(P[side, 2] * 0.35 + t * 6)
            bc = lerp(RED, WHITE * 0.7, stripes_k[:, None])
            bc = lerp(bc, BLUE, (dz < -6)[:, None] * 0.8)
            buf[side] += bc * perc(0.8 * bundle)[:, None] + light(POLE, below)
            buf[side] += light(POLE, pole[side] * (dz > 25))
        else:
            k = smoothstep(11.0, 13.0, t)
            buf[side] += light(POLE, (1 - k) * 0.16)
            top = np.exp(-((P[side, 2] - (-637)) / 10) ** 2)              # the finial
            buf[side] += light(POLE, 0.6 * top * fade)
        out[f] = np.clip(buf, 0, 1)
    return out
