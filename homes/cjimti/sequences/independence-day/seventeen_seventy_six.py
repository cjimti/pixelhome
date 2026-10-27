"""1776: The whole roofline is the parchment of the Declaration, lit by candles standing at the five
corners (warm pools that fall off with real 3-D distance, so the porch glows across the notch).
A quill writes: its point is the only bright thing, and where it is down it leaves ink, which
darkens the parchment. Handwriting is the pen's forward drift plus fast back-and-forth loops,
lifted between words, so strokes really overlap and blot. Wet ink catches the candlelight as a
cool blue sheen that dries to black over a few seconds.

The heading goes across the Porch Front in big capitals; the body fills the porch sides in
time-lapse. A pause. Then John Hancock signs: huge loops right across the Right wing, so big the
signature runs off the end of the house, and the flourish whips back the whole length underneath.
Then the other fifty-five sign in a hurry, tiny, on the Side and Left wing; one of them shakes.
The red wax seal is pressed on the porch and the candles are snuffed one by one."""
import numpy as np
from pixelhome.fx import DT, hexc, perc, light, smoothstep, keys, lerp, Flicker, nframes

CODE = 'IN07'
TITLE = '1776'
KIND = 'show'
DESCRIPTION = ('The roof is the parchment of the Declaration, lit by candles at the corners. A quill writes '
               'it in ink that glistens and dries. Then John Hancock signs, so big he runs off the end of '
               'the house, and fifty-five others squeeze in tiny.')

PARCH = hexc('#ff9a48')
CANDLE = hexc('#ff7a18')
SHEEN = hexc('#6c8cff')
QUILL = hexc('#fff0d8')
WAX = hexc('#ff0a08')
SMOKE = hexc('#8090a0')


def render(G, seed=27):
    rng = np.random.default_rng(seed)
    D = 70.0
    F = nframes(D)
    out = np.zeros((F, G.N, 3))
    x = G.pd[G.path]
    P = G.pos[G.path]
    L = G.length
    cidx = (80, 178, 260, 331, 380)
    cpos = np.array([(P[a] + P[a + 1]) / 2 for a in cidx])
    cd = np.linalg.norm(P[:, None] - cpos[None], axis=2)
    flame = Flicker(rng, 5, 0.6, 3.5)
    seg = {n: (x[ix.min()], x[ix.max()]) for n, ix in G.path_segments()}

    # strokes: (t0, t1, x0, x1, loop amplitude, loop Hz, weight, word length, tremor)
    strokes = []
    a, b = seg['Porch Front']
    strokes.append((2.5, 10.0, a + 10, b - 10, 7.0, 1.6, 0.95, 0.9, 0.0))         # IN CONGRESS, JULY 4, 1776
    a, b = seg['Porch Left']
    strokes.append((10.5, 15.5, a + 6, b - 4, 3.5, 4.5, 0.8, 0.55, 0.0))          # the body, time-lapse
    a, b = seg['Porch Right']
    strokes.append((15.7, 20.0, a + 4, b - 6, 3.5, 5.5, 0.8, 0.5, 0.0))
    a, b = seg['Right']
    T_H = 23.5
    strokes.append((T_H, T_H + 10.0, a + 10, L + 60, 26.0, 1.15, 1.0, 3.5, 0.0))   # John Hancock
    strokes.append((T_H + 10.6, T_H + 12.3, L + 20, a + 5, 6.0, 0.8, 1.0, 99, 0.0))  # the flourish, back underneath
    # fifty-five more, small and quick, filling the Side and the Left wing
    lo, hi = seg['Side'][0] + 6, seg['Left'][1] - 6
    slots = np.linspace(lo, hi, 56)
    t = T_H + 14.0
    for k in range(55):
        dur = keys(k, [(0, 0.6), (15, 0.22), (54, 0.16)])
        w = rng.uniform(0.45, 0.8)
        trem = 1.0 if k == 31 else 0.0                     # Stephen Hopkins' shaking hand
        if k == 47:
            w = 0.22                                       # a timid one
        strokes.append((t, t + dur, slots[k] - 6, slots[k] + 6, rng.uniform(2.5, 4.5), rng.uniform(3, 6),
                        w, rng.uniform(0.4, 0.9), trem))
        t += dur + keys(k, [(0, 0.3), (15, 0.05), (54, 0.03)])
    T_SEAL = t + 1.2
    out_t = T_SEAL + np.array([4.0, 6.2, 8.0, 9.6, 5.0]) + 1.0
    seal_x = 0.5 * sum(seg['Porch Front'])

    ink = np.zeros(G.N)
    wet = np.zeros(G.N)
    sub = 8
    prev_pen = None
    for f in range(F):
        t = f * DT
        fade = keys(t, [(0, 0.0), (2, 1.0), (D - 1.5, 1.0), (D, 0.0)])
        fl = flame(t)
        lit = np.array([1 - smoothstep(o - 0.15, o + 0.25, t) for o in out_t])
        breath = 1 + 0.25 * np.exp(-((t - (T_H - 1.2)) / 0.8) ** 2)    # the room holds its breath
        pool = (lit * (1 + 0.06 * fl) * breath)[None] * np.exp(-(cd / 380) ** 2)
        I = fade * (0.05 + 0.3 * pool.sum(1).clip(0, 1.3))

        pen = None
        for (t0, t1, x0, x1, A, hz, w, word, trem) in strokes:
            if t0 <= t < t1:
                for s_ in range(sub):
                    ts = t + s_ * DT / sub
                    u = (ts - t0) / (t1 - t0)
                    base = lerp(x0, x1, u)
                    p = base + A * np.sin(2 * np.pi * hz * (ts - t0)) + 0.4 * A * np.sin(2 * np.pi * 2.3 * hz * (ts - t0))
                    if trem:
                        p += 2.5 * np.sin(2 * np.pi * 9 * ts) + 1.5 * np.sin(2 * np.pi * 13 * ts)
                    ph = ((base - x0) / max(word * 30, 1)) % 1
                    down = ph < 0.82 or word > 50
                    if down:
                        dep = w * 0.02 * np.exp(-((x - p) / 3.0) ** 2)
                        ink = np.minimum(ink + dep, np.maximum(ink, 0.9 * w))   # a pen only gets so dark
                        wet = np.maximum(wet, np.where(dep > 0.01, 1.0, 0.0) * w)
                    pen = (p, down, w)
        wet *= np.exp(-DT / 2.2)

        buf = PARCH[None] * perc(I * (1 - 0.92 * ink))[:, None]
        buf += light(SHEEN, 0.75 * wet * ink * (I / 0.4).clip(0, 1.2))
        for k in range(5):                                  # the candles themselves
            ck = 0.5 * (x[cidx[k]] + x[cidx[k] + 1])
            buf += light(CANDLE, fade * lit[k] * (0.55 + 0.08 * fl[k]) * np.exp(-((x - ck) / 6) ** 2))
            if out_t[k] < t < out_t[k] + 3:                # a wisp of smoke
                sm = np.sin(np.pi * (t - out_t[k]) / 3) * 0.12
                buf += light(SMOKE, sm * np.exp(-((x - ck - 12 * (t - out_t[k])) / 14) ** 2))
        if pen is not None:
            p, down, w = pen
            buf += light(QUILL, fade * (0.75 if down else 0.45) * np.exp(-((x - p) / 4) ** 2))
            buf += light(QUILL, fade * 0.08 * np.exp(-((x - p) / 40) ** 2))
        if t >= T_SEAL - 0.8:                               # the wax seal: a drip, a press, a ring
            u = t - (T_SEAL - 0.8)
            r = 6 + 14 * smoothstep(0, 0.8, u)
            buf += light(WAX, fade * 0.8 * np.exp(-((x - seal_x) / r) ** 4))
            if u > 0.8:
                press = u - 0.8
                buf += light(WAX, fade * 0.6 * np.exp(-press / 0.25) * np.exp(-((x - seal_x) / 40) ** 2))
                buf += light(hexc('#ff6040'), 0.5 * np.exp(-press / 0.6) *
                             np.exp(-((np.abs(x - seal_x) - 260 * press) / 25) ** 2))
        m = buf.max(1, keepdims=True)
        out[f][G.path] = np.clip(np.where(m > 1, buf / np.maximum(m, 1e-9), buf), 0, 1)
    return out
