"""Wildfire: A match is struck on the porch; fire spreads along the roof, jumps ahead, burns out.
Then blue ghost-fire races in from both ends and detonates on the porch."""
import numpy as np
from pixelhome.fx import DT, hexc, light, smoothstep, lerp, smooth_noise, Flicker, colormap, nframes

CODE = 'SC2'
TITLE = 'Wildfire'
KIND = 'show'
DESCRIPTION = 'A match strikes on the porch. Fire spreads around the corners, embers jump ahead, then blue ghost-fire races in from both ends.'

PALE = hexc('#ffd070')
PURPLE = hexc('#5000c0')
WHITE = hexc('#ffffff')


def porch_center(G):
    pf = G.seg['Porch Front']
    return pf[len(pf) // 2]


def render(G, seed=2):
    rng = np.random.default_rng(seed)
    D = 64.0
    out = np.zeros((nframes(D), G.N, 3))
    pd = G.pd
    d0 = pd[porch_center(G)]
    dist = np.abs(pd - d0)
    V, T0 = 70.0, 3.0
    t_ign = T0 + dist / V + 0.5 * smooth_noise(rng, pd, 60)
    jumps = []
    for side in (-1, 1):
        end = 0 if side < 0 else G.length
        for _ in range(2):
            ds = rng.uniform(220, abs(end - d0) - 120)
            ps = d0 + side * ds
            t_nat = T0 + ds / V
            ts = t_nat - rng.uniform(2.0, 3.5)
            jumps.append((ps, ts))
            t_ign = np.minimum(t_ign, ts + np.abs(pd - ps) / V)
    burn = 7 + 1.5 * smooth_noise(rng, pd, 80)
    fl = Flicker(rng, G.N, 2, 9)
    tw = Flicker(rng, G.N, 0.5, 3)
    heat_map = colormap([(0, (0, 0, 0)), (0.1, (0.04, 0, 0)), (0.3, (0.25, 0.01, 0)), (0.5, (0.7, 0.05, 0)),
                         (0.7, (1, 0.17, 0)), (0.9, (1, 0.38, 0.02)), (1.15, (1, 0.75, 0.3))])
    # ghost fire: both ends to porch centre, arriving together at T2 + 12
    T2 = 44.0
    t2 = np.where(pd < d0, T2 + pd / d0 * 12, T2 + (G.length - pd) / (G.length - d0) * 12)
    blue_head, blue_tail = hexc('#a0f0ff'), hexc('#0830ff')
    centre = np.abs(pd - d0) < 8

    for f in range(len(out)):
        t = f * DT
        fr = out[f]
        tau = t - t_ign
        rise = smoothstep(0, 0.6, tau)
        core = 1 + 0.25 * np.exp(-np.clip(tau, 0, None) / 0.8)
        fade = smoothstep(burn, burn + 3, tau)
        tongues = 0.5 + 0.5 * np.sin(pd * 0.045 - 5.3 * t + 2 * np.sin(pd * 0.013 + t))
        flick = 0.45 + 0.35 * (0.5 + 0.5 * fl(t)) + 0.3 * tongues
        heat = rise * (1 - fade) * core * flick
        emb = fade * np.exp(-np.clip(tau - burn - 3, 0, None) / 5) * np.clip(tw(t), 0, 1) ** 2
        heat = heat + 0.45 * emb
        heat *= 1 - smoothstep(-0.2, 0.3, t - t2)          # ghost fire extinguishes it
        fr += heat_map(heat)

        if 1.8 < t < T0 + 0.3:                                # match strike
            sp = rng.random(G.N) < 0.5
            fr[centre & sp] += PALE * rng.uniform(0.3, 1.0)
        for ps, ts in jumps:                                  # flying embers
            if ts - 0.6 < t < ts:
                front = d0 + np.sign(ps - d0) * V * max(0, ts - 0.6 - T0)
                p = lerp(front, ps, (t - (ts - 0.6)) / 0.6)
                fr += light(PALE, np.clip(1 - np.abs(pd - p) / 10, 0, 1))

        tau2 = t - t2
        head = np.exp(-(tau2 / 0.18) ** 2) * (tau2 > -0.5)
        tail = np.where(tau2 > 0, 0.55 * np.exp(-tau2 / 1.0) * (0.8 + 0.2 * fl(t)), 0)
        glow = np.where(tau2 > 0, 0.16 * np.exp(-tau2 / 6), 0)
        fr += light(blue_head, head) + light(blue_tail, tail) + light(PURPLE, glow)

        if t >= T2 + 12:                                      # detonation on the porch
            tb = t - (T2 + 12)
            ring = np.exp(-((dist - tb * 900) / 70) ** 2) * np.exp(-tb / 1.5)
            fr += light(WHITE, ring + 0.9 * np.exp(-tb / 0.25))
            fr += light(PURPLE, 0.3 * np.exp(-(tb - 0.5) / 2.5) * (tb > 0.3))
    return out
