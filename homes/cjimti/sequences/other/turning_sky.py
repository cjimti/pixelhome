"""The Turning Sky: From the street the roofline reads as an arch: the Right wing's free end is the
eastern horizon, the porch front (farther away, higher in the view) is the top of the sky and the
back of the Side is the western horizon. Dusk fades out of the west and stars come out brightest
first. Then the sky turns: stars rise at the free end, climb over the porch and set behind the Side.
Near the horizons they are dimmed, reddened and twinkle hard (more air in the way); overhead they are
steady and white. A tight cluster (the Pleiades) rises, then the seven stars of the Dipper, then the
Milky Way with its dark lanes. Two meteors; then dawn comes up in the east and puts the stars out."""
import numpy as np
from pixelhome.fx import DT, hexc, light, smoothstep, keys, lerp, smooth_noise, nframes

CODE = 'OT23'
TITLE = 'The Turning Sky'
KIND = 'show'
DESCRIPTION = ('The roofline becomes the arch of the night sky. Stars rise at the free end, climb over the '
               'porch and set behind the house: the Pleiades, the Dipper, the Milky Way, then dawn.')

DUSK_W = hexc('#ff7a30')
TWI = hexc('#2a50b0')
NIGHT = hexc('#0c1440')
DAWN = hexc('#4a8ad0')
DAWN_GOLD = hexc('#ffb060')
MILKY = hexc('#b8c8ff')
STAR_COLS = [hexc('#a8c0ff'), hexc('#e8f0ff'), hexc('#fff4e0'), hexc('#ffd8a0'), hexc('#ffb070')]
REDDEN = hexc('#ff7030')
METEOR = hexc('#e0fff0')


def render(G, seed=23):
    rng = np.random.default_rng(seed)
    D = 80.0
    F = nframes(D)
    out = np.zeros((F, G.N, 3))
    d = G.pd
    L = G.length
    pf = G.seg['Porch Front']
    top = G.pd[pf].mean()
    # path distance <-> angle across the sky (0 = east horizon at the free end, pi = west)
    theta = np.interp(d, [0, top, L], [np.pi, np.pi / 2, 0])
    alt = np.sin(theta)                                     # 0 at the horizons, 1 overhead

    def to_pd(th):
        return np.interp(th, [0, np.pi / 2, np.pi], [L, top, 0])

    # sky rotation: slow at dusk, a steady time-lapse, slowing again at dawn
    tt = np.arange(F) * DT
    rate = np.array([keys(t, [(0, 0.012), (12, 0.012), (20, 0.075), (64, 0.075), (74, 0.02)]) for t in tt])
    Phi = np.cumsum(rate) * DT

    def rises_at(t_r):
        return -Phi[min(int(t_r / DT), F - 1)]

    # field stars spread round the whole sky
    S = 120
    th0 = rng.uniform(-Phi[-1] - 0.2, np.pi, S)
    mag = rng.uniform(0, 1, S) ** 2.2                       # many faint, few bright
    b = 0.16 + 0.62 * mag
    cidx = rng.choice(len(STAR_COLS), S, p=[0.18, 0.32, 0.25, 0.15, 0.10])
    scol = np.array([STAR_COLS[i] for i in cidx])
    # the Pleiades: a small, tight knot of blue-white stars
    pl = rises_at(22.0) + np.array([0, -0.009, -0.017, -0.026, -0.034, -0.044, -0.052])
    pl_b = np.array([0.55, 0.62, 0.45, 0.7, 0.5, 0.58, 0.42])
    # the Dipper: four in the bowl, three in the handle
    dp = rises_at(33.0) + np.array([0, -0.05, -0.115, -0.165, -0.215, -0.27, -0.335])
    dp_b = np.array([0.92, 0.88, 0.74, 0.68, 0.94, 0.9, 0.86])
    th0 = np.concatenate([th0, pl, dp])
    b = np.concatenate([b, pl_b, dp_b])
    scol = np.concatenate([scol, np.tile(STAR_COLS[0], (7, 1)), np.tile(STAR_COLS[1], (7, 1))])
    S = len(th0)
    tw_f = rng.uniform(3, 9, (S, 2))
    tw_p = rng.uniform(0, 2 * np.pi, (S, 2))
    # the Milky Way: a broad band of the sky that rises late, mottled with dark lanes
    mw_c = rises_at(50.0) - 0.35
    mw_lane_x = np.linspace(-1, 1, 400)
    mw_lane = 0.6 + 0.4 * smooth_noise(rng, mw_lane_x, 0.18, 3)
    mw_lane = np.clip(mw_lane, 0, 1)
    mw_stars = mw_c + rng.normal(0, 0.18, 60)
    mw_b = 0.12 + 0.25 * rng.uniform(0, 1, 60) ** 2
    meteors = [(52.0, 0.9 * np.pi, 0.45 * np.pi, 0.6), (58.6, 0.25 * np.pi, 0.55 * np.pi, 0.45)]

    for f in range(F):
        t = f * DT
        fr = out[f]
        # -- the sky itself
        dusk = keys(t, [(0, 1), (14, 0)])
        dawn = keys(t, [(62, 0), (79, 1)])
        night = 0.07
        sky_I = night + 0.22 * dusk * (0.4 + 0.6 * (theta / np.pi) ** 2)
        sky_col = lerp(NIGHT, TWI, dusk)
        glow_w = dusk ** 1.5 * np.exp(-(np.pi - theta) / 0.35)
        dawn_reach = 0.25 + 1.6 * dawn
        glow_e = dawn * np.exp(-theta / dawn_reach)
        col = light(sky_col, sky_I) + light(DUSK_W, 0.55 * glow_w)
        col += light(lerp(DAWN, DAWN_GOLD, np.clip(1 - theta / 0.6, 0, 1)[:, None]), 0.5 * glow_e)
        bright_sky = sky_I + 0.5 * glow_w + 0.5 * glow_e     # how washed out the sky is here

        # -- the stars
        ths = th0 + Phi[f]
        up = (ths > -0.05) & (ths < np.pi + 0.05)
        if up.any():
            th_u = ths[up]
            a_s = np.clip(np.sin(np.clip(th_u, 0, np.pi)), 0, 1)
            airmass = 1 / np.maximum(a_s, 0.06)
            ext = np.exp(-0.22 * (airmass - 1))                # dimmer near the horizon
            red = np.clip((airmass - 1.3) / 5, 0, 1)
            tw = 1 + np.minimum(0.06 * airmass, 0.5) * (np.sin(2 * np.pi * tw_f[up, 0] * t + tw_p[up, 0])
                                                         + 0.6 * np.sin(2 * np.pi * tw_f[up, 1] * t + tw_p[up, 1])) / 1.6
            ps = to_pd(np.clip(th_u, 0, np.pi))
            g = np.exp(-((d[None, :] - ps[:, None]) / 3.6) ** 2)
            I_s = b[up] * ext * tw
            c_s = lerp(scol[up], REDDEN, red[:, None])
            # stars come out in order of brightness as the sky darkens, and are put out by dawn
            vis = np.clip((b[up][:, None] - 1.6 * bright_sky[None, :]) / 0.12, 0, 1)
            star = (g * vis * I_s[:, None])
            I_tot = star.max(0)
            wsum = star.sum(0) + 1e-9
            c_tot = (star[:, :, None] * c_s[:, None, :]).sum(0) / wsum[:, None]
            col += light(c_tot, I_tot)

        # -- the Milky Way
        mw_u = (theta - (mw_c + Phi[f])) / 0.42
        band = np.exp(-mw_u ** 2) * np.interp(mw_u, mw_lane_x * 2.2, mw_lane) * smoothstep(0, 0.15, alt)
        col += light(MILKY, 0.17 * band * (1 - dawn) * keys(t, [(40, 0), (44, 1)]))
        ths = mw_stars + Phi[f]
        upm = (ths > 0) & (ths < np.pi)
        if upm.any():
            g = np.exp(-((d[None, :] - to_pd(ths[upm])[:, None]) / 3.0) ** 2)
            col += light(MILKY, (g * mw_b[upm, None]).max(0) * (1 - dawn) * np.sin(ths[upm]).max() ** 0.3)

        # -- meteors
        for t0, a0, a1, amp in meteors:
            u = (t - t0) / 0.55
            if 0 <= u < 3:
                head_th = lerp(a0, a1, min(u, 1) ** 0.8)
                hp = to_pd(head_th)
                sgn = np.sign(to_pd(a1) - to_pd(a0))
                behind = (hp - d) * sgn                        # >0 along the trail
                trail = np.where(behind > 0, np.exp(-behind / (60 + 120 * min(u, 1))), 0)
                tp = to_pd(a0)
                on = ((d - tp) * sgn > 0) & (behind > -4)
                head = np.exp(-(behind / 4) ** 2) * (u < 1)
                fade = np.exp(-max(u - 1, 0) / 0.45)
                col += light(METEOR, amp * (head + 0.55 * trail * on * fade * (u < 1) + 0.12 * trail * on * fade))
        fr[:] = col * keys(t, [(0, 0), (1.5, 1), (76.5, 1), (80, 0)])
    return out
