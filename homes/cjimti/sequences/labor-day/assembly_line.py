"""Assembly Line: The roofline is an indexing conveyor and each segment is a station.

Parts enter at the free back end of Side and step forward together, one pitch at a time, pausing
while every station works on the part in front of it: Side stamps the raw blank, Left welds a joint
(which glows and cools), Porch Left paints it, Porch Front's robot arm fetches and fits a gold cap,
Porch Right inspects it with a scan line, Right boxes it and it leaves off the free right end.
The gag: the paint booth sputters once and a part comes out pink. Inspection rejects it, the line
stops, the reject scurries back upstream past its siblings to be repainted and comes back to a
green light. Then a rush order speeds the line up until the shift ends and it stops dead."""
import numpy as np
from pixelhome.fx import DT, hexc, light, smoothstep, keys, lerp, nframes

CODE = 'LB03'
TITLE = 'Assembly Line'
KIND = 'show'
DESCRIPTION = ('The roof is a conveyor and every segment is a station: stamp, weld, paint, cap, inspect, box. '
               'One part comes out pink, gets rejected and runs back upstream to be fixed.')

RAW = hexc('#5d6b7c')
STEEL = hexc('#b4c2d2')
HOT = hexc('#ff5a0c')
BLUE = hexc('#2b5cff')
PINK = hexc('#ff3a8c')
GOLD = hexc('#ffaa22')
BOX = hexc('#b06a2c')
LABEL = hexc('#fff1d8')
GREEN = hexc('#38ff78')
RED = hexc('#ff1a0a')
WORK = hexc('#ffd2a0')
ARCBLUE = hexc('#d0dcff')
BEACON = hexc('#ff9418')

P = 110.0          # pitch between parts
MOVE = 0.4         # fraction of a cycle spent moving


def ease(u):
    u = np.clip(u, 0, 1)
    return u * u * (3 - 2 * u)


def render(G, seed=23):
    rng = np.random.default_rng(seed)
    D = 74.0
    F = nframes(D)
    out = np.zeros((F, G.N, 3))
    s = G.pd[G.path]
    L = G.length
    stations = np.array([2, 6, 10, 13, 17, 19]) * P      # stamp, weld, paint, cap, inspect, box
    ST_STAMP, ST_WELD, ST_PAINT, ST_CAP, ST_INSPECT, ST_BOX = range(6)
    T_START = 5.0
    K_REJECT = 7

    def phase_track(pause=None):
        """Integrate the conveyor phase. pause = (phi_at_which_to_stop, duration)."""
        phi = np.zeros(F)
        p, paused_until, stop_at = 0.0, None, None
        for f in range(F):
            t = f * DT
            if t >= T_START:
                tc = keys(t, [(54, 1.6), (62, 0.75)])
                rate = 1.0 / tc
                if pause is not None and paused_until is None and p + rate * DT >= pause[0]:
                    p = pause[0]
                    paused_until = t + pause[1]
                if paused_until is not None and t < paused_until:
                    rate = 0
                if t > 64.0 and stop_at is None:
                    stop_at = np.floor(p) + 1 + MOVE
                if stop_at is not None:
                    p = min(p + rate * DT, stop_at)
                else:
                    p += rate * DT
            phi[f] = p
        return phi

    # pass 1: when does the reject part reach inspection?
    phi1 = phase_track()
    n_ins = K_REJECT + int(stations[ST_INSPECT] / P)       # cycle at which it dwells there
    PAUSE = 13.0
    phi = phase_track(pause=(n_ins + 0.999, PAUSE))
    f_pause = int(np.argmax(phi >= n_ins + 0.999))
    t_pause = f_pause * DT
    t_resume = t_pause + PAUSE

    def conveyor(p):
        whole = np.floor(p)
        fr = p - whole
        return P * (whole + ease(fr / MOVE)), fr > MOVE, np.clip((fr - MOVE) / (1 - MOVE), 0, 1)

    # reject's detour while the line is stopped (local time after t_pause)
    s_ins, s_paint = stations[ST_INSPECT], stations[ST_PAINT]
    detour = [(0.0, s_ins), (1.4, s_ins), (4.2, s_paint), (7.0, s_paint), (9.6, s_ins), (13.0, s_ins)]

    rollers = 22.0
    for f in range(F):
        t = f * DT
        buf = np.zeros((G.N, 3))
        C, dwell, u = conveyor(phi[f])
        on = [smoothstep(1.0 + 0.5 * j, 1.6 + 0.5 * j, t) * (1 - smoothstep(66 + 0.6 * (5 - j), 67 + 0.6 * (5 - j), t))
              for j in range(6)]
        line_on = smoothstep(0.5, 4.0, t) * (1 - smoothstep(66, 71, t))

        # the belt itself: faint rollers that move with the conveyor
        belt = 0.5 + 0.5 * np.cos(2 * np.pi * (s - C) / rollers)
        buf += light(RAW, 0.08 * line_on * belt ** 4)
        # station work lights
        for j, sj in enumerate(stations):
            buf += light(WORK, 0.16 * on[j] * np.exp(-((s - sj) / 26) ** 2))

        rejected_now = t_pause <= t < t_resume
        alarm = 0.0
        n_parts = int(np.floor(C / P)) + 1 if t >= T_START else 0
        for k in range(min(n_parts, 60)):
            c = C - k * P
            if c < -1 or c > L + 30:
                continue
            is_rej = k == K_REJECT
            if is_rej and rejected_now:
                c = keys(t - t_pause, detour)

            def done(j, c=c):
                if c > stations[j] + 0.5:
                    return 1.0
                if abs(c - stations[j]) <= 0.5 and dwell:
                    return float(u)
                return 0.0

            g = [done(j) for j in range(6)]
            # the reject is repainted during its detour
            repaint = 0.0
            if is_rej:
                lt = t - t_pause
                if t >= t_resume:
                    repaint = 1.0
                elif rejected_now:
                    repaint = smoothstep(4.6, 6.6, lt)
            fade = smoothstep(-1, 14, c) * (1 - smoothstep(L - 10, L + 25, c))
            length = 26 + 8 * g[ST_CAP] + 12 * g[ST_BOX]
            # stamp: a squash at the press
            if abs(c - stations[ST_STAMP]) < 1 and dwell:
                length *= 1 + 0.5 * np.exp(-((u - 0.45) / 0.08) ** 2)
            body = smoothstep(length / 2 + 2.5, length / 2 - 2.5, np.abs(s - c)) * fade

            col = lerp(RAW, STEEL, g[ST_STAMP])
            I = lerp(0.38, 0.6, g[ST_STAMP])
            paint_col = PINK if is_rej else BLUE
            paint_col = lerp(paint_col, BLUE, repaint)
            col = lerp(col, paint_col, g[ST_PAINT])
            I = lerp(I, 0.72, g[ST_PAINT])
            col = lerp(col, BOX, g[ST_BOX])
            I = lerp(I, 0.55, g[ST_BOX])
            buf += light(col, I * body)

            if g[ST_STAMP] > 0 and abs(c - stations[ST_STAMP]) < 1 and dwell:   # the press hit
                hit = np.exp(-((u - 0.45) / 0.06) ** 2)
                buf += light(LABEL, 0.9 * hit * body + 0.35 * hit * np.exp(-((s - c) / 30) ** 2))
            if g[ST_WELD] > 0:                                                  # weld joint
                joint = np.exp(-((s - c) / 3.0) ** 2) * fade
                if abs(c - stations[ST_WELD]) < 1 and dwell and 0.15 < u < 0.8:
                    buf += light(ARCBLUE, rng.uniform(0.5, 1.0) * joint)
                    buf += light(hexc('#4050ff'), 0.12 * np.exp(-((s - c) / 40) ** 2))
                heat = g[ST_WELD] * np.exp(-max(0.0, (c - stations[ST_WELD])) / 160) * (1 - g[ST_PAINT])
                buf += light(HOT, 0.85 * heat * joint)
            if g[ST_CAP] > 0:                                                   # gold cap, leading end
                cap = smoothstep(5, 2, np.abs(s - (c + length / 2 - 3))) * fade
                buf += light(GOLD, 0.75 * g[ST_CAP] * (1 - g[ST_BOX]) * cap)
            if g[ST_BOX] > 0:                                                   # a label on the box
                buf += light(LABEL, 0.5 * g[ST_BOX] * np.exp(-((s - c) / 2.5) ** 2) * fade)

            # inspection: scan line, then verdict
            at_ins = abs(c - stations[ST_INSPECT]) < 1
            if at_ins and dwell and not (is_rej and rejected_now):
                scan = c - length / 2 + length * min(1, u / 0.6)
                if u < 0.6:
                    buf += light(GREEN, 0.7 * np.exp(-((s - scan) / 2.0) ** 2))
                verdict = smoothstep(0.6, 0.65, u) * (1 - smoothstep(0.85, 1.0, u))
                bad = is_rej and repaint < 1
                buf += light(RED if bad else GREEN, 0.75 * verdict * body)
            if is_rej and rejected_now:
                lt = t - t_pause
                if lt < 1.4:        # the rejection, held
                    buf += light(RED, 0.7 * body * (0.6 + 0.4 * np.cos(2 * np.pi * lt * 2.2)))
                if 4.4 < lt < 6.9:  # repaint burst
                    mist = rng.random(G.N) < 0.18
                    buf += light(BLUE, 0.6 * mist * np.exp(-((s - c) / 30) ** 2))
                if 10.0 < lt < 12.2:  # re-inspection, passes, little cheer
                    v = smoothstep(10.0, 10.2, lt) * (1 - smoothstep(11.6, 12.2, lt))
                    buf += light(GREEN, 0.85 * v * body)
                    cheer = (rng.random(G.N) < 0.25) * np.exp(-((s - c) / 45) ** 2)
                    buf += light(GOLD, 0.5 * v * cheer)
                alarm = 1.0 if lt < 10.0 else 0.0

            # robot arm at the cap station: fetches a cap from upstream and fits it
            if abs(c - stations[ST_CAP]) < 1 and dwell:
                home = stations[ST_CAP] + 55
                tgt = c + length / 2 - 3
                arm = keys(u, [(0, home), (0.15, home), (0.45, tgt), (0.65, tgt), (0.95, home)])
                carry = 1.0 if u < 0.55 else 0.25
                buf += light(GOLD, 0.8 * carry * np.exp(-((s - arm) / 3.0) ** 2))
            # paint booth mist (sputters magenta for the reject)
            if abs(c - stations[ST_PAINT]) < 1 and dwell and 0.1 < u < 0.85:
                mist = (rng.random(G.N) < 0.16) * np.exp(-((s - c) / 28) ** 2)
                if is_rej and not rejected_now and t < t_pause:
                    sput = rng.random() < 0.5
                    buf += light(PINK, 0.65 * mist * sput)
                else:
                    buf += light(BLUE, 0.5 * mist)
            # box flaps fold in
            if abs(c - stations[ST_BOX]) < 1 and dwell:
                for sign in (-1, 1):
                    flap = c + sign * (length / 2 + 6 * (1 - u))
                    buf += light(BOX, 0.5 * (1 - u) * np.exp(-((s - flap) / 3) ** 2))

        if alarm:                                 # rotating beacon over inspection
            rot = 0.5 + 0.5 * np.cos(2 * np.pi * 1.1 * (t - t_pause))
            buf += light(BEACON, 0.55 * rot ** 3 * np.exp(-((s - stations[ST_INSPECT] - 40) / 12) ** 2))
            buf += light(BEACON, 0.12 * rot ** 3 * np.exp(-((s - stations[ST_INSPECT]) / 160) ** 2))
        buf *= 1 - smoothstep(69.5, 73.5, t)
        out[f][G.path] = np.clip(buf, 0, 1)
    return out
