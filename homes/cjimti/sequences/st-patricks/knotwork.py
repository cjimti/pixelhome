"""Knotwork: three strands (emerald, gold, pale mint) are drawn along the roof like a scribe's pen,
bouncing off the two free ends and turning every corner. Whenever two strands cross, one goes over
and one goes under, with the strict alternation of real Celtic interlace: each strand goes over, then
under, then over. The under strand vanishes at the crossing and the over strand is drawn with the
dark notches either side that knotwork uses. In the end the strands gather on the porch and weave a
tight interlace that freezes into a knot, its crossings left as stitches of light."""
import numpy as np
from pixelhome.fx import DT, hexc, perc, light, keys, lerp, smoothstep, nframes

CODE = 'SP04'
TITLE = 'Knotwork'
KIND = 'show'
DESCRIPTION = ('Three strands weave along the roof like a Celtic knot: at every crossing one dives under '
               'and one goes over, strictly alternating, until they tie themselves into a knot on the porch.')

VELLUM = hexc('#0c4a1c')
COLS = [hexc('#00d050'), hexc('#ffa000'), hexc('#b8ffd8')]


def reflect(s, L):
    s = np.mod(s, 2 * L)
    return np.where(s < L, s, 2 * L - s)


def render(G, seed=41):
    rng = np.random.default_rng(seed)
    D = 62.0
    F = nframes(D)
    out = np.zeros((F, G.N, 3))
    n = G.N
    x = G.pd[G.path]
    L = G.length
    C3, C4 = 1311.0, 1660.0
    cx = (C3 + C4) / 2

    t_in = [1.0, 8.0, 13.0]
    start = [-30.0, L + 30, -30.0]
    v = [210.0, 270.0, 330.0]
    T1, T2, T3 = 38.0, 44.0, 49.0          # weave -> gather on the porch -> slow down -> freeze
    amp = [330.0, 300.0, 270.0]
    om = 2 * np.pi / 2.6
    ph = [0.0, 2 * np.pi / 3, 4 * np.pi / 3]

    def g(t):                                 # finale phase clock: linear, then decelerate to rest
        if t < T2:
            return t
        u = min(t, T3) - T2
        return T2 + u - u * u / (2 * (T3 - T2))

    def pos(i, t):
        t = np.asarray(t, float)
        if start[i] < 0:
            w = reflect(np.maximum(t - t_in[i], -0.5) * v[i] + start[i] + 30, L) - 30 * (t < t_in[i])
        else:
            w = L - reflect(np.maximum(t - t_in[i], -0.5) * v[i] + 30, L) + 30 * (t < t_in[i])
        tight = np.interp(t, [T2, T3], [1.0, 0.0])
        fin = cx + tight * amp[i] * np.sin(om * np.vectorize(g)(t) + ph[i])
        return lerp(w, fin, smoothstep(T1, T1 + 5, t))

    tau = lambda t: keys(t, [(0, 2.0), (8, 1.2), (T1, 1.2), (T2, 1.4)])
    record = []
    marks = []                                # [x, time, over, under]
    nxt_over = [True, True, True]
    prev = [float(pos(i, 0)) for i in range(3)]
    ncross = 0
    trail = [np.zeros(n) for _ in range(3)]
    prevd = list(prev)

    for f in range(F):
        t = f * DT
        cur = [float(pos(i, t)) for i in range(3)]
        for i in range(3):
            for j in range(i + 1, 3):
                if t < max(t_in[i], t_in[j]):
                    continue
                if np.sign(prev[i] - prev[j]) != np.sign(cur[i] - cur[j]):
                    xc = (cur[i] + cur[j]) / 2
                    if nxt_over[i] != nxt_over[j]:
                        o = i if nxt_over[i] else j
                    else:
                        o = i if ncross % 2 == 0 else j
                    u = j if o == i else i
                    nxt_over[o], nxt_over[u] = False, True
                    marks.append([xc, t, o, u])
                    if t < T1 + 3:
                        record.append((xc, o))
                    ncross += 1
        prev = cur
        marks = [m for m in marks if t - m[1] < 2.6]

        fade = keys(t, [(0, 0), (0.8, 1), (D - 4, 1), (D - 0.3, 0)])
        frozen = smoothstep(T3, T3 + 0.8, t)
        tk = tau(t)
        layers = []
        for i in range(3):
            if t < t_in[i] - 0.2:
                layers.append(np.zeros(n))
                continue
            a, b = min(prevd[i], cur[i]), max(prevd[i], cur[i])     # the pen swept from a to b this frame
            dseg = np.maximum(np.maximum(a - x, x - b), 0)
            trail[i] = np.maximum(trail[i] * np.exp(-DT / tk), np.exp(-(dseg / 6.0) ** 2))
            I = trail[i] * (0.7 + 0.3 * frozen) + 0.5 * np.exp(-((x - cur[i]) / 5.0) ** 2) * (1 - frozen)
            layers.append(I)
        prevd = cur
        notch = np.zeros(n)
        for xc, tc, o, u in marks:
            age = t - tc
            life = 1 - smoothstep(1.8, 2.6, age)
            d = x - xc
            gap = np.exp(-(d / 12) ** 4) * life
            layers[u] = layers[u] * (1 - gap)
            flank = (np.exp(-((np.abs(d) - 11) / 4.5) ** 2)) * life
            notch = np.maximum(notch, flank)
            layers[o] = np.maximum(layers[o], 0.8 * np.exp(-(d / 7) ** 2) * life * (0.6 + 0.4 * frozen))
        fr = light(VELLUM, 0.1 * fade * (1 - notch))
        for i in range(3):
            fr += light(COLS[i], layers[i] * fade * (1 - 0.92 * notch))
        if t > T3:                            # pulled tight: a flash, then the knot's map replays
            tb = t - T3
            fr += light(COLS[1], 0.9 * np.exp(-tb / 0.4) * np.exp(-((x - cx) / (60 + 500 * tb)) ** 2) * fade)
            m = len(record)
            for r, (xc, o) in enumerate(record):
                tr = tb - 0.8 - 4.0 * r / max(m, 1)
                if tr <= 0:
                    continue
                d = x - xc
                pop = 0.6 + 0.4 * np.exp(-tr / 0.4) + 0.08 * np.sin(2 * np.pi * (t / 3.0 + r / 7))
                fr *= 1 - 0.9 * np.exp(-((np.abs(d) - 12) / 4.5) ** 2)[:, None]
                fr += light(COLS[o], pop * np.exp(-(d / 6.5) ** 2) * fade)
        out[f][G.path] = fr
    return out
