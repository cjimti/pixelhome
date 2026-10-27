"""Liberty Bell: The porch is the bell (seen from above, its three sides are the bell's open shape),
cast in heavier "bronze" than the wings. Every pixel is a point on a string obeying the wave
equation along the roofline path. The clapper swings across the porch front and each strike sends
a pulse round the corners and out along the wings; at the free ends the pulses bounce back, and
where the heavy bell meets the light wings they partly reflect and flip sign, so crests (red)
come home as troughs (blue). Energy trapped in the bell makes it ring. The thirteenth stroke of
the peal cracks it: the crack scatters every wave that reaches it, buzzes, and turns the next
strokes into dull clunks. Then the crack glows gold, and the house rings once more, softly."""
import numpy as np
from pixelhome.fx import DT, hexc, perc, light, smoothstep, keys, lerp, nframes

CODE = 'IN03'
TITLE = 'Liberty Bell'
KIND = 'show'
DESCRIPTION = ('The porch is the bell. Each stroke sends a wave through the house that bounces off the free '
               'ends and comes home inverted. Thirteen strokes in a peal, and the last one cracks it.')

RED = hexc('#ff1c10')
BLUE = hexc('#1a3cff')
WHITE = hexc('#fff2e6')
BRONZE = hexc('#ff7a20')
GOLD = hexc('#ffb040')
NIGHT = hexc('#0a1440')


def render(G, seed=23):
    rng = np.random.default_rng(seed)
    D = 64.0
    F = nframes(D)
    out = np.zeros((F, G.N, 3))
    xp = G.pd[G.path]
    L = G.length
    dx = 4.0
    s = np.arange(0, L + dx, dx)
    n = len(s)
    bell_a, bell_b = (xp[178] + xp[179]) / 2, (xp[380] + xp[381]) / 2
    pf_a, pf_b = (xp[260] + xp[261]) / 2, (xp[331] + xp[332]) / 2
    in_bell = smoothstep(bell_a - 12, bell_a + 12, s) * (1 - smoothstep(bell_b - 12, bell_b + 12, s))
    rho = 1 + 1.6 * in_bell                     # bronze is heavy: slower, and a mismatch at the lips
    c0 = 340.0
    T = np.ones(n - 1)                          # tension between cells
    gamma = np.full(n, 0.3)
    sub = 4
    W0 = 2 * np.pi * 0.08                       # a faint spring so the roof never drifts away
    dt = DT / sub
    u = np.zeros(n)
    v = np.zeros(n)
    crack_x = lerp(pf_a, pf_b, 0.36)
    ci = int(round(crack_x / dx))

    # strokes: (time, side of the porch front the clapper hits, strength)
    strokes = [(3.5, -1, 1.0), (8.0, 1, 1.0), (12.5, -1, 1.0), (16.0, 1, 1.0), (19.0, -1, 1.0)]
    tp = 22.0
    for k in range(13):                         # the peal, gathering pace
        strokes.append((tp, 1 if k % 2 else -1, 1.0 + 0.04 * k))
        tp += keys(k, [(0, 1.6), (12, 1.05)])
    T_CRACK = strokes[-1][0]
    strokes += [(T_CRACK + 5.2, 1, 0.55), (T_CRACK + 8.6, -1, 0.4)]
    st_t = np.array([x[0] for x in strokes])
    hit_pos = {-1: lerp(pf_a, pf_b, 0.06), 1: lerp(pf_a, pf_b, 0.94)}

    def clapper(t):
        i = np.searchsorted(st_t, t)
        if i == 0:
            prev_t, prev_side = 0.0, 1
        else:
            prev_t, prev_side = strokes[i - 1][0], strokes[i - 1][1]
        if i >= len(strokes):
            return lerp(hit_pos[prev_side], 0.5 * (pf_a + pf_b), smoothstep(0, 3, t - prev_t)), 0.0
        nt, side = strokes[i][0], strokes[i][1]
        u_ = np.clip((t - prev_t) / max(nt - prev_t, 1e-3), 0, 1)
        if prev_t >= T_CRACK - 0.01 and i > 0:
            u_ = u_ ** 2.2                       # after the crack: a reluctant swing
        else:
            u_ = u_ ** 1.7                       # falling into the stroke
        return lerp(hit_pos[prev_side], hit_pos[side], u_), u_

    fired = set()
    energy = 0.0
    buzz = 0.0
    for f in range(F):
        t = f * DT
        for k, (ts, side, a) in enumerate(strokes):
            if k not in fired and t >= ts:
                fired.add(k)
                x0 = hit_pos[side]
                amp = a * (1.0 if ts <= T_CRACK else 0.45)
                r2 = ((s - x0) / 26) ** 2                 # a Ricker pulse: red crest with blue shoulders
                u += amp * 1.8 * (1 - 2 * r2) * np.exp(-r2)
                if ts == T_CRACK:
                    T[ci - 1:ci + 1] = 0.06      # the bell cracks
                    gamma[ci - 6:ci + 7] = 3.0
                if ts > T_CRACK:
                    buzz = 1.0
        if t > T_CRACK + 12:                     # the house forgives: the crack heals into a seam of gold
            T[ci - 1:ci + 1] = lerp(0.06, 1.0, smoothstep(T_CRACK + 12, T_CRACK + 15, t))
            gamma[:] = lerp(0.3, 0.8, smoothstep(T_CRACK + 18, D, t))
        if abs(t - (T_CRACK + 13.5)) < DT / 2:  # one soft, whole-house ring
            u += 0.5 * np.exp(-((s - 0.5 * (pf_a + pf_b)) / 160) ** 2)
        for _ in range(sub):
            du = np.diff(u) / dx
            flux = T * du
            acc = np.zeros(n)
            acc[1:-1] = (flux[1:] - flux[:-1]) / dx
            acc[0] = flux[0] / dx                 # free ends
            acc[-1] = -flux[-1] / dx
            v += dt * (c0 ** 2 * acc / rho - gamma * v - W0 ** 2 * u)
            u += dt * v
        if buzz > 0.01:                          # a cracked bell rattles where it is broken
            u[ci - 3:ci + 4] += 0.25 * buzz * rng.normal(0, 1, 7) * min(1.0, abs(u[ci - 8]) * 6 + 0.1)
            buzz *= np.exp(-DT / 0.9)

        w = np.interp(xp, s, u)
        bellmask = np.interp(xp, s, in_bell)
        energy = 0.96 * energy + 0.04 * float(np.mean((u * in_bell) ** 2) / max(in_bell.mean(), 1e-6))
        buf = np.zeros((G.N, 3))
        bg = keys(t, [(0, 0.0), (2, 1.0), (D - 3, 1.0), (D, 0.0)])
        cracked = t >= T_CRACK
        bronze_I = bg * (0.11 + min(0.25, 2.2 * energy)) * (0.75 if cracked and t < T_CRACK + 12 else 1.0)
        buf += light(BRONZE, bronze_I * bellmask) + light(NIGHT, bg * 0.07 * (1 - bellmask))
        A = np.clip(np.abs(w) * 1.25, 0, 1.3)
        hue = np.where(w[:, None] > 0, RED, BLUE)
        buf += hue * perc(np.clip(A, 0, 1))[:, None]
        buf += light(WHITE, np.clip(A - 0.75, 0, 1) * 1.5)

        # the clapper
        cp, _ = clapper(t)
        if t > 1.5:
            buf += light(GOLD, 0.5 * bg * np.exp(-((xp - cp) / 7) ** 2))
        for ts, side, a in strokes:               # the flash of each stroke
            dtt = t - ts
            if 0 <= dtt < 0.5:
                fl = (1.0 if ts <= T_CRACK else 0.35) * np.exp(-dtt / 0.08)
                buf += light(WHITE, fl * np.exp(-((xp - hit_pos[side]) / 22) ** 2))
        if cracked:
            dtt = t - T_CRACK
            near = np.exp(-((xp - crack_x) / 6) ** 2)
            dark = np.clip(1 - 2 * near, 0, 1)
            buf *= dark[:, None] if t < T_CRACK + 12 else lerp(dark, 1.0, smoothstep(T_CRACK + 12, T_CRACK + 15, t))[:, None]
            buf += light(WHITE, 1.2 * np.exp(-dtt / 0.12) * np.exp(-((xp - crack_x) / 30) ** 2))
            glint = smoothstep(T_CRACK + 10, T_CRACK + 14, t) * (0.55 + 0.1 * np.sin(2 * np.pi * t / 3))
            glint += 0.4 * buzz
            buf += light(GOLD, glint * bg * np.exp(-((xp - crack_x) / 9) ** 2))
        m = buf.max(1, keepdims=True)
        out[f][G.path] = np.where(m > 1, buf / np.maximum(m, 1e-9), buf)
    return out
