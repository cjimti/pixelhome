"""Crossing the Delaware: The roof is a winter river seen from above. Ice floes drift across it as
real shapes in the ground plane (long bars on the street-facing runs, quick knocks on the runs that
point at the street); three lantern boats push through them down Side, Porch Left and Porch Right,
toward the near bank. Washington's boat lands at the front-left corner and dawn breaks on the wings."""
import numpy as np
from pixelhome.fx import DT, hexc, light, smoothstep, keys, lerp, Flicker, nframes

CODE = 'PR01'
TITLE = 'Crossing the Delaware'
KIND = 'show'
DESCRIPTION = ('A winter river at night: ice floes drift across the house while three lantern boats push '
               'toward the street. Washington lands at the front-left corner and dawn breaks on the wings.')

NAVY = hexc('#1a2c90')
DEEP = hexc('#0a1440')
ICE = hexc('#98c0ff')
CREAM = hexc('#ffe0a8')
BRASS = hexc('#ff9a28')
EMBER = hexc('#ff5010')
BRICK = hexc('#c82410')


def render(G, seed=21):
    rng = np.random.default_rng(seed)
    D = 78.0
    out = np.zeros((nframes(D), G.N, 3))
    P = G.pos
    x, z = P[:, 0], P[:, 2]
    shimmer = Flicker(rng, G.N, 0.1, 0.6)
    lamp = Flicker(rng, 3, 2.0, 5.0)
    camp = Flicker(rng, G.N, 0.8, 3.0)

    # ice floes: ellipses in the ground plane, carried by a current that is fastest mid-river
    K = 70
    fz = rng.uniform(-660, -120, K)
    fv = 26 + 24 * np.sin(np.pi * np.clip((fz + 660) / 540, 0, 1)) * rng.uniform(0.8, 1.15, K)
    fa = rng.uniform(35, 95, K)
    fb = rng.uniform(22, 55, K)
    fang = rng.uniform(-0.6, 0.6, K)
    fspin = rng.uniform(-0.03, 0.03, K)
    span = 1700.0
    t_enter = np.sort(rng.uniform(-30, 52, K))           # when each floe crosses x = -850
    fbright = rng.uniform(0.6, 1.0, K)

    # boats: (x of the run, z start, z end, keyframes in 0..1 of the crossing, intensity)
    lanes = [
        (-196.0, -565.0, -151.0, [(12, 0), (18, 0.16), (21, 0.18), (27, 0.42), (31, 0.44), (37, 0.62),
                                  (40, 0.63), (47, 0.86), (50, 0.88), (56, 1.0)], 1.0),
        (152.0, -565.0, -196.0, [(16, 0), (23, 0.22), (27, 0.25), (35, 0.55), (38, 0.57), (48, 0.9),
                                 (52, 0.92), (59, 1.0)], 0.6),
        (-596.0, -637.0, -146.0, [(19, 0), (27, 0.2), (31, 0.22), (41, 0.55), (44, 0.56), (54, 0.88),
                                  (58, 0.9), (63, 1.0)], 0.5),
    ]
    T_LAND = 56.0
    wake = np.zeros(G.N)
    sleet = np.zeros(G.N)
    land = np.array([-196.0, 150.0, -151.0])
    dland = np.linalg.norm(P - land, axis=1)
    pf = G.seg['Porch Front']

    for f in range(len(out)):
        t = f * DT
        fr = out[f]
        night = keys(t, [(0, 0), (4, 1), (58, 1), (70, 0.4), (78, 0)])
        # the river: dark water with slow ripples carried by the current
        rip = 0.5 + 0.5 * np.sin(x * 0.018 - t * 0.9 + 1.5 * np.sin(z * 0.011 + t * 0.15))
        fr += light(lerp(DEEP, NAVY, rip[:, None] * 0.6), night * (0.13 + 0.04 * rip + 0.015 * shimmer(t)))

        # far bank: the camp on the Porch Front, dying as the boats leave
        cI = keys(t, [(0, 0), (4, 0.22), (14, 0.22), (30, 0.06), (50, 0)])
        if cI > 0:
            fr[pf] += light(EMBER, cI * np.clip(0.6 + 0.4 * camp(t)[pf], 0, 1))

        # the floes
        cx = -850 + fv * (t - t_enter)
        on = (cx > -1000) & (cx < 1000)
        if on.any():
            ca = cx[on]
            ang = fang[on] + fspin[on] * t
            dx = x[None, :] - ca[:, None]
            dz = z[None, :] - fz[on][:, None]
            c, s = np.cos(ang)[:, None], np.sin(ang)[:, None]
            u = (dx * c + dz * s) / fa[on][:, None]
            v = (-dx * s + dz * c) / fb[on][:, None]
            r = np.sqrt(u * u + v * v)
            body = smoothstep(1.0, 0.82, r)
            rim = np.exp(-((r - 0.9) / 0.07) ** 2) * (u > 0)          # bright leading edge
            fl = (body * 0.36 + rim * 0.42) * fbright[on][:, None]
            fl = fl.max(axis=0)
            dens = keys(t, [(0, 0), (5, 0.8), (60, 0.8), (70, 0.2), (76, 0)])
            fr += light(lerp(ICE, CREAM, np.clip(fl - 0.4, 0, 1)[:, None]), dens * fl)

        # sleet: sparse cold glints, slowly decaying
        sleet *= 0.85
        sp = rng.random(G.N) < 0.0012 * keys(t, [(0, 0), (6, 1), (50, 1), (58, 0)])
        sleet[sp] = rng.uniform(0.25, 0.5, sp.sum())
        fr += light(ICE, sleet)

        # the boats
        wake *= 0.985
        for j, (lx, z0, z1, kf, amp) in enumerate(lanes):
            if t < kf[0][0] - 2:
                continue
            u = keys(t, [(kf[0][0] - 2, 0)] + kf)
            speed = (keys(t + 0.25, [(kf[0][0] - 2, 0)] + kf) - u) / 0.25 * abs(z1 - z0)
            bz = lerp(z0, z1, u)
            bob = 1 + 0.12 * np.sin(2 * np.pi * t * 0.7 + j)
            boat = np.array([lx, 150.0, bz])
            d = np.linalg.norm(P - boat, axis=1)
            appear = smoothstep(kf[0][0] - 2, kf[0][0], t)
            arrive = 1 - 0.5 * smoothstep(kf[-1][0], kf[-1][0] + 4, t) if j else 1.0
            glow = amp * appear * arrive * np.exp(-(d / 16) ** 2) * bob * (0.9 + 0.1 * lamp(t)[j])
            wake = np.maximum(wake, 0.35 * amp * appear * np.exp(-(d / 30) ** 2) * (z <= bz + 5))
            fr += light(BRASS, 0.85 * glow) + light(CREAM, 0.5 * glow ** 3)
            # bow wave: spray just ahead of the boat while it is pulling, gone when it stalls
            ahead = (z - bz) * np.sign(z1 - z0)
            spray = np.clip(speed / 25, 0, 1) * amp * appear * np.exp(-((ahead - 26) / 9) ** 2) * (d < 60)
            fr += light(ICE, 0.55 * spray * (0.8 + 0.2 * shimmer(t * 4)))
        fr += light(CREAM, wake * 0.5 * night)

        # landing: a flare at the corner, then dawn rises from the street-side edge of the wings
        if t >= T_LAND:
            tl = t - T_LAND
            ring = np.exp(-((dland - tl * 260) / 60) ** 2) * np.exp(-tl / 2.5)
            fr += light(CREAM, 0.8 * ring)
            reach = smoothstep(-640, -140, z) ** 1.5
            rise = smoothstep(0, 14, tl)
            dawn = rise * reach * keys(t, [(T_LAND, 1), (72, 1), (78, 0)])
            warm = np.clip(rise * 1.3 - 0.35 + 0.3 * (reach - 1), 0, 1)[:, None]
            dcol = lerp(lerp(BRICK, BRASS, np.clip(warm * 2, 0, 1)), CREAM, np.clip(warm * 2 - 1, 0, 1))
            fr += light(dcol, 0.62 * dawn * (0.92 + 0.08 * shimmer(t * 0.5)))
            # Washington's lantern stays lit on the bank to the very end
            fr += light(BRASS, 0.9 * np.exp(-(dland / 16) ** 2) * keys(t, [(T_LAND, 1), (74, 1), (78, 0)]))
    return out
