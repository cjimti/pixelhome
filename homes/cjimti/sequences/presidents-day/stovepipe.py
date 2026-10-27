"""Stovepipe: Seen from the street, the porch U is a stovepipe hat: Porch Left and Porch Right are the
tall sides, the Porch Front is the crown, and the inner ends of the wing fronts are the brim. A pen
draws it, silk sheen slides down it, and Lincoln raises it. Out pops a copper penny that flips,
rolls off the crown, drops down the side with gravity and bounces, rolls along the Right wing to
teeter at the free end, then spins down like Euler's disk (faster, faster, clack) before the hat
comes down and tips once to the street."""
import numpy as np
from pixelhome.fx import DT, hexc, light, smoothstep, keys, lerp, Flicker, nframes

CODE = 'PR03'
TITLE = 'Stovepipe'
KIND = 'show'
DESCRIPTION = ('The porch becomes Lincoln\'s stovepipe hat. He raises it, and a copper penny pops out, '
               'drops down the side, rolls to the edge of the roof and spins itself still.')

SILK = hexc('#1c2a88')
SHEEN = hexc('#d8e0ff')
CREAM = hexc('#ffe0a8')
BRASS = hexc('#ffa030')
COPPER = hexc('#ff5a1a')
BRICK = hexc('#b82410')


def render(G, seed=23):
    rng = np.random.default_rng(seed)
    D = 50.0
    F = nframes(D)
    out = np.zeros((F, G.N, 3))
    s = G.pd[G.path]
    sL, sR = s[179], s[380]            # crown meets brim (front of Porch Left / Porch Right)
    sTL, sTR = s[261], s[331]          # crown corners
    s_pc = 0.5 * (sTL + sTR)
    s_end = s[500]
    BRIM = 125.0
    side_h = s[260] - sL               # height of the crown sides (Porch Left length)
    # height up the hat for crown pixels; brim pixels get negative h (distance out along the brim)
    h = np.full(G.N, -1e4)
    pl = (s >= sL) & (s <= s[260])
    pr = (s >= s[332]) & (s <= sR)
    top = (s > s[260]) & (s < s[332])
    h[pl] = s[pl] - sL
    h[pr] = sR - s[pr]
    h[top] = side_h + 30
    brimL = (s < sL) & (s > sL - BRIM - 40)
    brimR = (s > sR) & (s < sR + BRIM + 40)
    out_brim = np.where(brimL, sL - s, np.where(brimR, s - sR, 1e4))
    # the pen draws the outline from the left brim tip to the right brim tip
    s_draw0, s_draw1 = sL - BRIM, sR + BRIM
    shim = Flicker(rng, G.N, 0.1, 0.5)

    # --- the penny, simulated frame by frame along the path ---
    pen_p = np.full(F, np.nan)
    pen_g = np.zeros(F)                  # glint 0..1
    T_POP = 16.0
    p, v, phase, ang, t_stop = s_pc, 0.0, 'pop', 0.0, None
    g = 700.0
    for f in range(F):
        t = f * DT
        if t < T_POP:
            continue
        if phase == 'pop':                                  # flipping above the crown
            ang += 2 * np.pi * 6 * DT
            if t > T_POP + 2.0:
                phase = 'top'
        elif phase == 'top':                                # rolls along the crown to the right corner
            v += 130 * DT
            p += v * DT
            ang += v / 30 * DT
            if p >= s[332]:
                phase = 'fall'
        elif phase == 'fall':                               # drops down Porch Right, bounces on the brim
            v += g * DT
            p += v * DT
            ang += 2 * np.pi * 3 * DT
            if p >= sR:
                p = sR
                v = -0.42 * v
                if abs(v) < 70:
                    phase, v = 'roll', 150.0
                    decel = v * v / (2 * (s_end - 10 - sR))
        elif phase == 'roll':                               # rolls along the Right wing, slowing
            v = max(0.0, v - decel * DT)
            p += v * DT
            ang += v / 25 * DT
            if v <= 0:
                phase, t_stop, p_stop = 'teeter', t, p
        elif phase == 'teeter':                             # wobbles at the edge
            tt = t - t_stop
            p = p_stop + 2.5 * np.sin(2 * np.pi * 1.3 * tt) * np.exp(-tt / 1.2)
            if tt > 3.0:
                phase, t_e = 'euler', t
                ang_e = 0.0
        elif phase == 'euler':                              # spins itself still, faster and faster
            te = t - t_e
            T = 6.5
            if te < T:
                fr_ = 2.0 + 20.0 * (te / T) ** 3
                ang_e += 2 * np.pi * fr_ * DT
                amp = 0.5 * (1 - 0.6 * te / T)
                pen_g[f] = 0.5 + amp * np.cos(ang_e)
                p = p_stop + 1.2 * np.sin(ang_e) * (1 - te / T)
            else:
                phase, t_clack = 'rest', t
        if phase == 'rest':
            tc = t - t_clack
            pen_g[f] = 0.55 + 0.6 * np.exp(-tc / 0.2)
        elif phase != 'euler':
            pen_g[f] = 0.2 + 0.8 * abs(np.cos(ang)) ** 3
        pen_p[f] = p

    tq = t_clack
    lift_k = [(12.0, 0), (14.2, 150), (tq + 1.0, 150), (tq + 3.5, 0), (tq + 5.5, 0), (tq + 6.1, 55),
              (tq + 7.1, 55), (tq + 7.9, 0)]
    # the hat leans toward the edge to watch the penny teeter (right side lower, left side higher)
    lean_k = [(t_stop - 1, 0), (t_stop + 0.5, 1), (tq + 0.5, 1), (tq + 2, 0)]
    T_TIP = tq + 6.6
    for f in range(F):
        t = f * DT
        buf = np.zeros((G.N, 3))
        drawn = keys(t, [(0.5, s_draw0), (5.5, s_draw1)])
        dmask = smoothstep(drawn + 4, drawn - 4, s) * smoothstep(s_draw0 - 6, s_draw0 + 2, s)
        fade = keys(t, [(D - 4, 1), (D, 0)])
        lift = keys(t, lift_k) + 45 * keys(t, lean_k) * np.where(s < s_pc, 1.0, -0.6)
        # crown: silk with a sheen that slides down the sides
        vis = smoothstep(lift - 4, lift + 4, h)
        sheen = np.zeros(G.N)
        for t0, dur in ((5.5, 3.5), (13.0, 2.5), (24.0, 4.5), (39.5, 3.0), (T_TIP - 0.8, 2.2)):
            if t0 <= t < t0 + dur:                          # a passing gleam slides down the silk
                sw = lerp(side_h + 120, -60, (t - t0) / dur)
                sheen += np.exp(-((h - sw) / 45) ** 2) * (h > -1) * np.sin(np.pi * (t - t0) / dur)
        crown = vis * (0.3 + 0.03 * shim(t))
        # hat band just above the bottom edge
        band = np.exp(-((h - lift - 52) / 5) ** 2) * vis
        # brim: on the wings when the hat is down; a bright band on the sides when lifted
        on_brim = smoothstep(BRIM + 8, BRIM - 8, out_brim) * smoothstep(40, 0, lift)
        brim_up = np.exp(-((h - lift) / 7) ** 2) * smoothstep(0, 30, lift) * (h > -1)
        hat = crown + 0.45 * on_brim + 0.45 * brim_up
        buf += light(SILK, dmask * fade * hat)
        # the rest of the house: a faint gaslit parlour, so the hat reads as a dark-blue shape
        buf += light(BRASS, 0.09 * fade * keys(t, [(4, 0), (7, 1)]) * (1 - vis) * (1 - on_brim) *
                     (1 - brim_up) * (0.85 + 0.15 * shim(t * 0.5)))
        buf += light(SHEEN, dmask * fade * 0.3 * sheen * vis)
        buf += light(BRICK, dmask * fade * 0.3 * band)
        if 0.5 < t < 6.0:                                  # the pen nib
            buf += light(CREAM, 0.9 * np.exp(-((s - drawn) / 6) ** 2))
        # the tip of the hat at the end: the brim catches the light
        tip = np.exp(-((t - T_TIP) / 0.6) ** 2)
        buf += light(CREAM, 0.35 * tip * (on_brim + brim_up))

        # the penny
        if not np.isnan(pen_p[f]):
            pp = pen_p[f]
            appear = smoothstep(T_POP, T_POP + 0.4, t) * fade
            gl = pen_g[f]
            core = np.exp(-((s - pp) / 4.5) ** 2)
            buf += light(COPPER, appear * (0.45 + 0.4 * gl) * core)
            buf += light(CREAM, appear * 0.7 * gl ** 4 * np.exp(-((s - pp) / 2.5) ** 2))
            if t < T_POP + 0.6:                               # the pop
                tp = t - T_POP
                buf += light(BRASS, 0.6 * np.exp(-tp / 0.2) * np.exp(-((s - s_pc) / 40) ** 2))
        out[f][G.path] = buf
    return out
