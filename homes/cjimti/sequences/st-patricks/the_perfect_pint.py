"""The Perfect Pint: a pub, seen from the street. The wing fronts are the warm pub windows and the
Porch Front is the brass-railed bar. Porch Left and Porch Right run away from the street, so from
the lawn they read as two tall glasses (front end = bottom, back end = top). Two stouts are poured
the proper way: three quarters, a tan surge whose bubbles sink, the long settle as the dark rises
from the bottom, then the top-up and the cream head. Meanwhile the uncle's pint on Side goes in
three gulps, leaving lacing rings. A toast runs along the bar, clink, sláinte, two sips (more rings),
and the bell for last orders."""
import numpy as np
from pixelhome.fx import DT, hexc, perc, light, keys, lerp, smoothstep, Flicker, nframes

CODE = 'SP07'
TITLE = 'The Perfect Pint'
KIND = 'show'
DESCRIPTION = ('The porch sides become two tall glasses, poured the proper way: the surge, the settle, the '
               'top-up. The uncle finishes his in three gulps. Then a clink, sláinte, and last orders.')

LAMP = hexc('#ff8420')
BRASS = hexc('#ffa030')
STOUT = hexc('#701000')
SURGE = hexc('#c86a28')
HEAD = hexc('#ffe2b0')
GLASS = hexc('#9ab8c0')
SPARK = hexc('#fff0c0')


def render(G, seed=71):
    rng = np.random.default_rng(seed)
    D = 52.0
    F = nframes(D)
    out = np.zeros((F, G.N, 3))
    n = G.N
    x = G.pd[G.path]
    P = G.pos[G.path]
    seg = G.seg_of[G.path]
    m = {s: seg == s for s in ('Side', 'Left', 'Porch Left', 'Porch Front', 'Porch Right', 'Right')}

    def height(mask):                       # 0 at the street end of a run, 1 at the back end
        z = P[:, 2]
        zf, zb = z[mask].max(), z[mask].min()
        h = np.zeros(n)
        h[mask] = (zf - z[mask]) / (zf - zb)
        return h

    flick = Flicker(rng, n, 0.08, 0.5)
    shiver = Flicker(rng, n, 2.0, 5.0)
    win = m['Left'] | m['Right']
    mull = np.ones(n)
    for s in ('Left', 'Right'):
        u = G.span_u(G.path[m[s]])
        mull[m[s]] = 1 - 0.85 * np.exp(-((((u + 1) * 2.5) % 1 - 0.5) / 0.04) ** 2) ** 1  # window bars
    bar = m['Porch Front']
    ub = np.zeros(n)
    ub[bar] = G.span_u(G.path[bar])
    pf = x[bar]
    pf_lo, pf_hi, pf_c = pf.min(), pf.max(), pf.mean()

    # two pours, staggered; S settled boundary, L liquid level, H head thickness
    def glass(t, t0):
        Lv = keys(t, [(t0, 0), (t0 + 4.5, 0.74), (t0 + 13.0, 0.74), (t0 + 15.0, 0.97)])
        S = keys(t, [(t0 + 3.0, 0), (t0 + 13.0, 0.66), (t0 + 15.0, 0.66), (t0 + 19.0, 0.88)])
        pouring = (t0 < t < t0 + 4.5) or (t0 + 13.0 < t < t0 + 15.0)
        return Lv, min(S, Lv), pouring

    pints = [(height(m['Porch Left']), m['Porch Left'], 3.0), (height(m['Porch Right']), m['Porch Right'], 5.0)]
    hS = height(m['Side'])
    T_TOAST = 27.5
    T_CLINK = T_TOAST + 1.6
    sips = [T_CLINK + 2.2, T_CLINK + 5.0]
    gulps = [9.0, 11.2, 13.0]
    rings = []                              # lacing: (glass index, height, time)
    for k, tg in enumerate(gulps):
        rings.append((2, 0.92 - 0.31 * k, tg))
    for g in (0, 1):
        for k, ts in enumerate(sips):
            rings.append((g, 0.93 - 0.17 * k, ts))
    T_BELL = 39.0

    for f in range(F):
        t = f * DT
        fade = keys(t, [(0, 0), (2.0, 1), (D - 3.5, 1), (D - 0.3, 0)])
        dim = keys(t, [(T_BELL + 3, 1), (D - 3.5, 0.45)])
        fr = np.zeros((n, 3))

        # the pub: windows and bar
        fr += light(LAMP, 0.36 * dim * fade * (1 + 0.07 * flick(t)) * mull * win)
        gloss = np.exp(-((ub - np.sin(2 * np.pi * t / 17)) / 0.25) ** 2)
        fr += light(BRASS, (0.2 + 0.1 * gloss) * dim * fade * bar)

        # sláinte: warm surge from the bar outward through the house
        if t > T_CLINK:
            tb = t - T_CLINK
            ring = np.exp(-((np.abs(x - pf_c) - 650 * tb) / 120) ** 2) * np.exp(-tb / 2.0)
            fr += light(LAMP, 0.6 * ring * fade)

        for gi, (h, mask, t0) in enumerate(pints + [(hS, m['Side'], None)]):
            if t0 is not None:
                Lv, S, pouring = glass(t, t0)
                for k, ts in enumerate(sips):        # each sip takes the level down a step
                    Lv -= 0.17 * smoothstep(ts, ts + 0.6, t)
                S = min(S, Lv)
            else:                                    # the uncle's glass, gone in three gulps
                Lv = 0.95 - sum(0.31 * smoothstep(tg, tg + 0.55, t) for tg in gulps)
                Lv = max(Lv, 0.0)
                S = Lv
                pouring = False
            Hd = 0.08 if Lv > 0.05 else 0.0
            I = np.zeros(n)
            col = np.zeros((n, 3))
            dark = mask & (h < S)
            surge = mask & (h >= S) & (h < Lv - Hd)
            head = mask & (h >= Lv - Hd) & (h < Lv)
            empty = mask & (h >= Lv)
            I[dark] = 0.24
            col[dark] = STOUT
            sink = 0.5 + 0.5 * np.sin(2 * np.pi * (h * 16 + 1.3 * t))      # bubbles drifting down
            I[surge] = (0.38 + 0.18 * sink[surge]) * (1 + 0.1 * shiver(t)[surge])
            mix = smoothstep(0, 0.12, h - S)
            col[surge] = lerp(STOUT, SURGE, mix[surge][:, None])
            I[head] = 0.62
            col[head] = HEAD
            I[empty] = 0.09
            col[empty] = GLASS
            if pouring:                               # the stream from the tap at the top
                st = empty & (np.sin(2 * np.pi * (h * 9 + 3 * t)) > -0.3)
                I[st] = 0.35
                col[st] = SURGE
            raise_ = keys(t, [(T_TOAST, 0), (T_TOAST + 0.8, 1), (T_CLINK + 1.0, 1), (T_CLINK + 1.6, 0)])
            I = I * (1 + 0.35 * raise_ * mask)
            for rg, rh, rt in rings:                  # lacing rings left behind
                if rg == gi and t > rt + 0.3 and rh > Lv:
                    a = smoothstep(rt + 0.3, rt + 0.9, t)
                    lace = np.exp(-((h - rh) / 0.018) ** 2) * mask
                    I = np.maximum(I, 0.34 * a * lace)
                    col = np.where(lace[:, None] > 0.3, HEAD, col)
            fr += light(col, I * fade * lerp(1, dim, 0.6))

        # the toast: a spark from the top of each glass along the bar, clink in the middle
        if T_TOAST + 0.6 < t < T_CLINK:
            u = smoothstep(T_TOAST + 0.6, T_CLINK, t)
            for a in (pf_lo, pf_hi):
                p = lerp(a, pf_c, u)
                fr += light(SPARK, 0.8 * np.exp(-((x - p) / 7) ** 2))
        if t >= T_CLINK:
            tb = t - T_CLINK
            fr += light(SPARK, np.exp(-tb / 0.18) * np.exp(-((x - pf_c) / 14) ** 2))
            for k in range(10):                       # droplets fly off the clink
                vk = (k - 4.5) * 55
                dp = pf_c + vk * (1 - np.exp(-2.5 * tb)) / 2.5
                fr += light(HEAD, 0.5 * np.exp(-tb / 0.5) * np.exp(-((x - dp) / 3) ** 2) * bar)

        # the bell for last orders: three rings on the bar
        for k in range(3):
            tk = t - (T_BELL + 0.55 * k)
            if tk > 0:
                fr += light(BRASS, 0.55 * np.exp(-tk / 0.35) * (0.7 + 0.3 * np.cos(2 * np.pi * 9 * tk)) * bar * fade)
        out[f][G.path] = fr
    return out
