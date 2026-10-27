"""Parade: Giant balloons float through the house in true 3-D. The roofline is a flat slice at one
height, so each balloon shows as its cross-section: a big ribbed pumpkin rolls along the front of the
wings (its ribs turn as it spins, and it shrinks and swells as it bobs up and down through the roof
plane); an ear of corn comes down the Side like a street, turns the corner and cuts across the porch
sides at mid-depth; a turkey with a fanned tail waddles along the Porch Front, stops in the middle,
over-inflates and pops. Its head, untied, zips off around the corner and out the end of the roof."""
import numpy as np
from pixelhome.fx import DT, hexc, light, keys, smoothstep, lerp, Flicker, nframes

CODE = 'TG04'
TITLE = 'Parade'
KIND = 'show'
DESCRIPTION = ('Giant parade balloons float through the house in 3-D: a spinning pumpkin, an ear of corn that turns '
               'the corner, and a turkey that over-inflates in front of the porch and pops.')

PUMPKIN = hexc('#ff5200')
AMBER = hexc('#ff8a18')
GOLD = hexc('#ffb000')
CRANBERRY = hexc('#c0102a')
WARM = hexc('#ffc27a')
BROWN = hexc('#8a3208')
DEEP = hexc('#4a1604')
D = 64.0
Y = 150.0


def ball(P, c, R, soft=7.0):
    """Shading of a sphere's slice: thick in the middle, thin at the rim, anti-aliased edge."""
    d = np.linalg.norm(P - c, axis=1)
    chord = np.sqrt(np.clip(1 - (d / R) ** 2, 0, 1))
    edge = np.clip((R - d) / soft, 0, 1)
    return edge * (0.3 + 0.7 * chord), d


def path_point(pts, s):
    """Point and unit tangent at arc length s along an open polyline route."""
    seg = np.diff(pts, axis=0)
    ln = np.linalg.norm(seg, axis=1)
    cum = np.concatenate([[0], np.cumsum(ln)])
    s = np.clip(s, 0, cum[-1] - 1e-6)
    i = int(np.searchsorted(cum, s, side='right') - 1)
    u = (s - cum[i]) / ln[i]
    return pts[i] + u * seg[i], seg[i] / ln[i], cum[-1]


def render(G, seed=24):
    rng = np.random.default_rng(seed)
    F = nframes(D)
    out = np.zeros((F, G.N, 3))
    n = G.N
    P = G.pos[G.path].copy()
    P[:, 1] = Y
    pdp = G.pd[G.path]
    crowd = Flicker(rng, n, 0.2, 1.0)
    conf_p = rng.uniform(0, G.length, 140)
    conf_t = 55.05 + np.abs(conf_p - 1486) / 1400 + rng.uniform(0, 0.4, 140)
    conf_c = [GOLD, CRANBERRY, WARM, PUMPKIN, AMBER]
    conf_k = rng.integers(0, 5, 140)
    # the corn's route: down the Side, round the corner, across the middle depth
    ang = np.linspace(np.pi, np.pi / 2, 8)                 # a rounded corner, radius 110
    corner = np.stack([-486 + 110 * np.cos(ang), np.full(8, Y), -470 + 110 * np.sin(ang)], 1)
    route = np.vstack([[(-596, Y, -1150)], corner, [(1100, Y, -360)]])

    for f in range(F):
        t = f * DT
        buf = np.zeros((n, 3))
        street = keys(t, [(0, 0), (2.5, 0.09), (61, 0.09), (64, 0)])
        buf += light(DEEP, street * (1 + 0.25 * crowd(t)))

        # 1. the pumpkin: ribbed, spinning, bobbing through the roof plane
        if 1.5 < t < 26:
            u = t - 1.5
            c = np.array([-1050 + 92 * u, Y + 70 * np.sin(2 * np.pi * u / 5.5), -178.0])
            I, d = ball(P, c, 215)
            phi = np.arctan2(P[:, 2] - c[2], P[:, 0] - c[0])
            rib = 0.62 + 0.38 * np.cos(10 * phi + 0.9 * u) ** 2
            hl = np.exp(-np.sum((P - (c + np.array([-60, 60, 110]))) ** 2, 1) / 90 ** 2)
            buf += light(PUMPKIN, 0.95 * I * rib) + light(GOLD, 0.45 * hl * (I > 0))
            # a stem on top shows only when the balloon dips low enough
            sc = c + np.array([0, 205, 0])
            Is, _ = ball(P, sc, 40)
            buf += light(BROWN, 0.7 * Is)

        # 2. the corn: a capsule oriented along its route, kernels in a grid
        if 15 < t < 42:
            s = (t - 15) * 88
            c, tan, total = path_point(route, s)
            a, b = c - tan * 150, c + tan * 150
            ab = b - a
            w = np.clip(((P - a) @ ab) / (ab @ ab), 0, 1)
            near = a + w[:, None] * ab
            d = np.linalg.norm(P - near, axis=1)
            R = 70 * (0.55 + 0.45 * np.sin(np.pi * w) ** 0.5)               # tapered cob
            bob = 18 * np.sin(2 * np.pi * t / 4.0)
            R = np.sqrt(np.clip(R ** 2 - bob ** 2, 0, None))
            inside = np.clip((R - d) / 6, 0, 1)
            chord = np.sqrt(np.clip(1 - (d / np.maximum(R, 1)) ** 2, 0, 1))
            along = w * 300
            side = np.arctan2(*(P - near)[:, [2, 0]].T)
            kern = (0.5 + 0.5 * np.sin(along * 0.21)) * (0.5 + 0.5 * np.sin(side * 7 + 1.3 * t))
            I = inside * (0.35 + 0.65 * chord) * (0.55 + 0.45 * kern)
            buf += light(GOLD, 0.95 * I)
            # husk leaves trailing behind
            hk = c - tan * 215
            Ih, _ = ball(P, hk, 60)
            buf += light(AMBER, 0.45 * Ih)

        # 3. the turkey: body, head, a tail fan in the vertical plane, along the Porch Front
        if 32 < t < 55.05:
            u = t - 32
            x = keys(t, [(32, -1000), (49, -30), (50, -12)]) if t < 50 else -12.0
            waddle = 10 * np.sin(2 * np.pi * u / 1.4) * (t < 49)
            Rb = keys(t, [(49.5, 150), (51, 175), (52, 175), (53.6, 260), (54, 255), (55.05, 330)])
            c = np.array([x, Y + 25 * np.sin(2 * np.pi * u / 3.2), -560.0 + waddle])
            I, _ = ball(P, c, Rb)
            strain = smoothstep(52, 55, t)
            body = light(lerp(BROWN, PUMPKIN, strain), 0.9 * I) + light(WARM, 0.5 * strain * I ** 3 *
                                                                        (0.5 + 0.5 * np.sin(30 * t)))
            buf += body
            gob = 25 * max(0, np.sin(2 * np.pi * u / 2.2)) ** 6
            hc = c + np.array([Rb * 0.85 + 35 + gob, 70, 0])
            Ih, _ = ball(P, hc, 62)
            buf += light(CRANBERRY, 0.95 * Ih)
            fan = [GOLD, AMBER, CRANBERRY, PUMPKIN, GOLD, AMBER, CRANBERRY]
            for k, ang in enumerate(np.linspace(-1.2, 1.2, 7)):
                fc = c + np.array([-np.cos(ang) * Rb * 1.15, np.sin(ang) * Rb * 1.15, 0])
                If, _ = ball(P, fc, 0.55 * Rb * (1 - 0.3 * strain))
                buf += light(fan[k], 0.75 * If * (1 - 0.6 * strain))

        # 4. POP: a flash, a ring, confetti; the untied head zips off around the corner
        if t >= 55.05:
            u = t - 55.05
            dist = np.abs(pdp - 1486)
            buf += light(WARM, 0.95 * np.exp(-u / 0.09) * np.exp(-(dist / 500) ** 2))
            buf += light(GOLD, 0.8 * np.exp(-((dist - 1500 * u) / 60) ** 2) * np.exp(-u / 0.7))
            live = (t > conf_t) & (t < conf_t + 2.2)
            for k in np.where(live)[0]:
                v = t - conf_t[k]
                tw = 0.5 + 0.5 * np.cos(2 * np.pi * (3 + k % 3) * v) ** 2
                buf += light(conf_c[conf_k[k]], 0.75 * tw * np.exp(-v / 0.9) *
                             np.exp(-((pdp - conf_p[k] - 20 * v) / 3.5) ** 2))
            # head: pfffft, zig-zagging along the path from the porch to the right free end
            s = 1486 + 1150 * smoothstep(0.2, 6.0, u) + 45 * np.sin(2 * np.pi * 1.7 * u) * (u < 5.5)
            hv = keys(t, [(55.05, 0.9), (60, 0.9), (61.5, 0)])
            buf += light(CRANBERRY, hv * np.exp(-((pdp - s) / 14) ** 2))
            for k in range(6):                                     # puffs of air behind it
                sk = 1486 + 1150 * smoothstep(0.2, 6.0, u - 0.08 * (k + 1))
                buf += light(WARM, 0.22 * hv * (1 - k / 6) * np.exp(-((pdp - sk + 8 * k) / 6) ** 2))
        out[f][G.path] = buf
    return out
