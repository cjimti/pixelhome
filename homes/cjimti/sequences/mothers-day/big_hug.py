"""Big Hug: Two arms of light reach in from the house's two free ends, the back of the Side and the
far end of the Right wing, and travel different distances to meet in the middle of the porch at the
same moment. Then the house squeezes: the roof is a stretched string (a wave equation along the
path, free at both ends, uneven pixel spacing included) and each squeeze, and the three pats on the
back of the Side, set it rippling and reflecting. Two heartbeats, one in each wing, drift into step
before the arms let go."""
import numpy as np
from pixelhome.fx import DT, hexc, light, smoothstep, keys, lerp, heartbeat, nframes

CODE = 'MO04'
TITLE = 'Big Hug'
KIND = 'show'
DESCRIPTION = 'Arms of light reach from both free ends and meet on the porch; each squeeze and pat sets the whole roof rippling like a plucked string.'

ARM_L = hexc('#ff8050')
ARM_R = hexc('#ff4f8f')
WARM = hexc('#ffd8b8')
LILAC = hexc('#b080ff')
HEART = hexc('#ff3a6a')


def render(G, seed=24):
    rng = np.random.default_rng(seed)
    D = 56.0
    n = G.N
    out = np.zeros((nframes(D), n, 3))
    x = G.pd[G.path]
    L = G.length
    pf = G.pd[G.seg['Porch Front']]
    M = 0.5 * (pf.min() + pf.max())
    T = 17.0
    tipL = [(2.5, -20.0), (6.5, 0.30 * M), (7.6, 0.33 * M), (11.5, 0.70 * M), (12.6, 0.73 * M), (16.0, 0.97 * M), (T, M), (T + 0.6, M + 45)]
    dR = L - M
    tipR = [(2.5, L + 20), (6.5, L - 0.30 * dR), (7.6, L - 0.33 * dR), (11.5, L - 0.70 * dR), (12.6, L - 0.73 * dR),
            (16.0, L - 0.97 * dR), (T, M), (T + 0.6, M - 45)]
    tipL += [(46, M + 45), (52, -40.0)]          # fingers interlace past the middle
    tipR += [(46, M - 45), (52, L + 40)]

    # wave equation on the path with uneven spacing, free ends
    h = np.diff(x)
    u = np.zeros(n)
    v = np.zeros(n)
    c, gamma, sub = 430.0, 0.35, 6
    dts = DT / sub

    def lap(u):
        g = np.diff(u) / h
        out_ = np.zeros(n)
        out_[1:-1] = (g[1:] - g[:-1]) / (0.5 * (h[1:] + h[:-1]))
        out_[0] = g[0] / h[0]
        out_[-1] = -g[-1] / h[-1]
        return out_

    squeezes = [19.0, 24.5, 30.0]
    pats = [35.5, 36.2, 36.9]
    PAT_AT = 230.0
    kicks = []
    for s in squeezes:                 # a squeeze presses in from both ends and the middle
        kicks += [(s, 0.0, 1.0), (s, L, 1.0), (s + 0.15, M, -1.2)]
    for p in pats:
        kicks.append((p, PAT_AT, 0.8))
    glow = np.zeros(n)

    for f in range(len(out)):
        t = f * DT
        buf = np.zeros((n, 3))
        for tk, xk, a in kicks:
            if tk <= t < tk + DT:
                v += a * 4.5 * np.exp(-((x - xk) / 30) ** 2)
        for _ in range(sub):
            v += dts * (c * c * lap(u) - gamma * v)
            u += dts * v
        u *= 0.9995

        a_l, a_r = keys(t, tipL), keys(t, tipR)
        reach = keys(t, [(2.5, 0), (3.5, 1), (50, 1), (53, 0)])
        sleeveL = smoothstep(a_l + 8, a_l - 40, x)
        sleeveR = smoothstep(a_r - 8, a_r + 40, x)
        hug = keys(t, [(T, 0), (T + 0.4, 1), (46, 1), (50, 0)])
        squeeze = sum(np.exp(-((t - s - 0.8) / 0.9) ** 2) for s in squeezes)
        base = (0.27 + 0.14 * squeeze * hug) * reach
        disp = np.clip(u, -1, 1)
        I = base * (1 + 1.2 * disp * hug)
        mixw = smoothstep(-200, 200, x - M)[:, None]
        colr = lerp(ARM_L, ARM_R, mixw)
        colr = lerp(colr, WARM, (np.clip(disp, 0, 1) * hug)[:, None] * 0.7)
        colr = lerp(colr, LILAC, (np.clip(-disp, 0, 1) * hug)[:, None] * 0.6)
        buf += light(colr, I * np.maximum(sleeveL, sleeveR))
        # hands
        if t < 52:
            buf += light(ARM_L, reach * 0.7 * np.exp(-((x - a_l) / 14) ** 2) * (t < T + 0.3))
            buf += light(ARM_R, reach * 0.7 * np.exp(-((x - a_r) / 14) ** 2) * (t < T + 0.3))
        # the meeting: a warm clasp
        if t > T - 0.2:
            u_ = t - T
            buf += light(WARM, 0.85 * np.exp(-((x - M) / (20 + 260 * smoothstep(0, 1.5, u_))) ** 2) * np.exp(-max(u_, 0) / 1.2) * hug)
            buf += light(WARM, 0.18 * hug * np.exp(-((x - M) / 60) ** 2))
        # pats on the back
        for p in pats:
            if p < t < p + 0.6:
                buf += light(WARM, 0.9 * np.exp(-(t - p) / 0.18) * np.exp(-((x - PAT_AT) / 45) ** 2))
        # two hearts, one per wing, drifting into step
        if 38 < t < 50:
            env = keys(t, [(38, 0), (39.5, 1), (47, 1), (50, 0)])
            k = smoothstep(39, 45, t)
            pl, pr = lerp(0.82, 0.95, k), lerp(1.12, 0.95, k)
            phl = 38.0
            phr = lerp(38.4, 38.0, k)
            hl = heartbeat(t, phl, pl) if k < 1 else heartbeat(t, 38.0, 0.95)
            hr = heartbeat(t, phr, pr) if k < 1 else heartbeat(t, 38.0, 0.95)
            cl = 0.5 * (G.pd[G.seg['Left']].min() + G.pd[G.seg['Left']].max())
            cr = 0.5 * (G.pd[G.seg['Right']].min() + G.pd[G.seg['Right']].max())
            buf += light(HEART, env * 1.0 * hl * np.exp(-((x - cl) / 90) ** 2))
            buf += light(HEART, env * 1.0 * hr * np.exp(-((x - cr) / 90) ** 2))
        # afterglow as the arms let go
        glow = np.maximum(glow * (1 - DT / 2.5), (base * np.maximum(sleeveL, sleeveR)) * (t > 46) * 0.8)
        buf += light(WARM, glow * (t > 46) * keys(t, [(52, 1), (56, 0)]))
        out[f][G.path] = buf
    return out
