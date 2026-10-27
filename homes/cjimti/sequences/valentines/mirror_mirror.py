"""Mirror, Mirror: the facade is mirror-symmetric, so the right half is cast as the left half's
reflection. The left half makes gestures and the reflection copies them, late at first, then exactly.
The left tries to catch it out; the reflection gives itself away with one extra move, then starts
improvising and the left ends up copying it. Finally both halves reach for the porch centre, where the
mirror line is, touch, and nested hearts open out across the house. The Side, which has no partner,
is the mirror's frame."""
import numpy as np
from pixelhome.fx import DT, hexc, perc, light, keys, smoothstep, lerp, Flicker, nframes

CODE = 'VD04'
TITLE = 'Mirror, Mirror'
KIND = 'show'
DESCRIPTION = ('The right half of the house is the left half\'s reflection, and it is not a very good one. '
               'It copies late, gets caught out, starts improvising, and in the end the two halves touch.')

ROSE = hexc('#ff2448')
GOLD = hexc('#ffa040')
WARM = hexc('#ffc890')
DEEP = hexc('#ff0010')
WINE = hexc('#a00008')
BLUSH = hexc('#ff5a50')
FRAME = hexc('#ffb878')


def mirror_coords(G):
    """Per path position: half (-1 left, +1 right, 0 Side) and m, the distance out from the porch centre
    in 'runs' (0..1 porch front half, 1..2 porch side, 2..3 wing, 3..4 Side), so corners line up."""
    pdp = G.pd[G.path]
    pf = G.seg['Porch Front']
    c = G.pd[pf[len(pf) // 2]]
    half = np.zeros(G.N)
    m = np.zeros(G.N)
    for name, idx in G.path_segments():
        lo, hi = pdp[idx].min(), pdp[idx].max()
        if name == 'Porch Front':
            left = pdp[idx] < c
            half[idx] = np.where(left, -1, 1)
            m[idx] = np.where(left, (c - pdp[idx]) / (c - lo), (pdp[idx] - c) / (hi - c))
        elif name in ('Porch Left', 'Left', 'Side'):
            base = {'Porch Left': 1, 'Left': 2, 'Side': 3}[name]
            half[idx] = -1 if name != 'Side' else 0
            m[idx] = base + (hi - pdp[idx]) / (hi - lo)
        else:
            base = {'Porch Right': 1, 'Right': 2}[name]
            half[idx] = 1
            m[idx] = base + (pdp[idx] - lo) / (hi - lo)
    return half, m


def g_sweep(s, m, dur, inward=True):
    if not 0 <= s < dur + 1.5:
        return 0 * m
    u = min(s / dur, 1.0)
    pos = 3 * (1 - u) if inward else 3 * u
    head = np.exp(-((m - pos) / 0.07) ** 2)
    trail = np.where((m - pos) * (1 if inward else -1) > 0, np.exp(-np.abs(m - pos) / 0.5), 0)
    return (head + 0.35 * trail) * (1 - smoothstep(dur, dur + 1.5, s))


def g_blip(s, m, at):
    if not 0 <= s < 1.2:
        return 0 * m
    return np.exp(-s / 0.22) * np.exp(-((m - at) / 0.12) ** 2) * smoothstep(0, 0.04, s)


def g_wave(s, m, dur, direction):
    if not 0 <= s < dur:
        return 0 * m
    env = smoothstep(0, 1, s) * (1 - smoothstep(dur - 1, dur, s))
    return env * (0.5 + 0.5 * np.sin(2 * np.pi * (m / 0.55 - direction * 0.7 * s))) ** 2 * (m < 3)


def g_reach(s, m, dur):
    if s < 0:
        return 0 * m
    pos = 3 * (1 - smoothstep(0, dur, s)) ** 1.3
    return np.clip((m - pos) / 0.05 + 1, 0, 1) * (m < 3) * (0.35 + 0.65 * np.exp(-((m - pos) / 0.1) ** 2))


def render(G, seed=24):
    rng = np.random.default_rng(seed)
    D = 58.0
    out = np.zeros((nframes(D), G.N, 3))
    half, m = mirror_coords(G)
    P = G.pos[G.path]
    fl = Flicker(rng, G.N, 0.2, 0.9)
    isL, isR, isS = half < 0, half > 0, half == 0
    # each half's script: (start, gesture, args)
    left = [(2.0, 'sweep', (2.6, True)), (7.0, 'sweep', (2.0, False)),
            (11.0, 'blip', (2.5,)), (11.6, 'blip', (2.5,)), (12.2, 'blip', (1.5,)),
            (15.0, 'blip', (2.5,)),                      # the left tries to catch it out
            (20.5, 'wave', (5.2, 1)), (25.2, 'wave', (3.2, -1)),
            (29.6, 'sweep', (1.6, True))]
    right = [(3.3, 'sweep', (2.6, True)), (7.7, 'sweep', (2.0, False)),
             (11.35, 'blip', (2.5,)), (11.95, 'blip', (2.5,)), (12.55, 'blip', (1.5,)),
             (15.0, 'blip', (2.5,)), (16.6, 'blip', (2.5,)),   # ...and it gives itself away
             (20.8, 'wave', (3.3, 1)), (23.6, 'wave', (4.6, -1)),   # improvises first, the left follows
             (28.8, 'sweep', (1.6, True))]
    T_REACH, T_TOUCH = 34.0, 41.0
    heart_c = np.array([-3.0, -569.0])                   # cusp of the hearts on the porch front

    def play(script, t):
        I = np.zeros(G.N)
        for t0, kind, args in script:
            s = t - t0
            if kind == 'sweep':
                I += g_sweep(s, m, *args)
            elif kind == 'blip':
                I += g_blip(s, m, *args)
            else:
                I += g_wave(s, m, *args)
        return I

    # nested hearts (cardioids with the cusp on the porch, body toward the street), in x-z
    dx, dz = P[:, 0] - heart_c[0], P[:, 2] - heart_c[1]
    r = np.hypot(dx, dz)
    th = np.arctan2(-dz, np.abs(dx) + 1e-9)               # 0 sideways, -pi/2 toward the street
    rho = r / (1.0 - 0.8 * np.sin(th))                     # constant on scaled heart outlines

    for f in range(len(out)):
        t = f * DT
        buf = np.zeros((G.N, 3))
        master = keys(t, [(D - 5, 1), (D - 0.3, 0)])
        frame = keys(t, [(0, 0), (1.5, 0.12), (T_TOUCH, 0.12), (T_TOUCH + 1, 0.3), (D - 6, 0.25)])
        buf += light(FRAME, frame * (1 + 0.15 * fl(t)) * isS)
        # the reflection is "caught": after its extra blip it freezes and dims
        guilty = keys(t, [(16.6, 1), (17.2, 0.35), (19.2, 0.35), (20.5, 1)])
        IL = play(left, t)
        IR = play(right, t) * guilty
        rest = keys(t, [(0, 0), (2, 0.04), (T_REACH, 0.04), (T_REACH + 1, 0)])
        mcolR = lerp(GOLD, ROSE, smoothstep(T_REACH, T_TOUCH, t))
        buf += light(ROSE, (0.85 * IL + rest) * isL) + light(mcolR, (0.85 * IR + rest) * isR)

        if t >= T_REACH:                                   # both reach for the mirror line
            s = t - T_REACH
            R = g_reach(s, m, T_TOUCH - T_REACH) * (t < T_TOUCH + 1.5)
            buf += light(ROSE, 0.6 * R * isL) + light(mcolR, 0.6 * R * isR)
        if t >= T_TOUCH:                                   # they touch: nested hearts open out
            s = t - T_TOUCH
            buf += light(WARM, 1.0 * np.exp(-s / 0.35) * np.exp(-(r / 60) ** 2))
            on = smoothstep(0, 1.5, s)
            rings = np.zeros(G.N)
            for k in range(14):
                rk = 230 * (s - 1.4 * k)
                if rk > 0:
                    rings += np.exp(-((rho - rk) / 26) ** 2) * np.exp(-rk / 1500)
            inside = smoothstep(0, -80, rho - 230 * s) * 0.18
            col = lerp(DEEP, BLUSH, np.clip(rings, 0, 1)[:, None] * 0.6)
            buf += (np.clip(on * (0.7 * rings + inside) * (half != 0), 0, None) ** 2.2)[:, None] * col
            buf += light(WINE, on * 0.15 * (half != 0) * (1 + 0.2 * fl(t)))
            buf += light(GOLD, on * 0.4 * np.exp(-((rho - 230 * s) / 20) ** 2) * (230 * s < 2400))
        out[f][G.path] = buf * master
    return out
