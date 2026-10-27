"""Thermostat Wars: the Porch Front is the thermostat, a blue-to-red scale with a needle; the rest of
the roof is the house's temperature, and every change at the dial flows out through the rooms with a
real delay by path distance. The kid tiptoes in from the back end of Side and clicks it up; Dad stomps
in from the far end of Right and snaps it down. Three rounds, each faster, until Dad freezes the house
solid and locks the dial. Then Dad gets cold in his chair, tiptoes in with the kid's own sneaky walk,
nudges it up one click, and the kid is standing right there."""
import numpy as np
from pixelhome.fx import DT, hexc, perc, light, smoothstep, keys, lerp, Flicker, nframes

CODE = 'FA05'
TITLE = 'Thermostat Wars'
KIND = 'show'
DESCRIPTION = ('The porch is the thermostat, the house is the temperature. The kid tiptoes in and turns it up; '
               'Dad stomps in and turns it down. Three rounds, a lock, and then Dad gets cold.')

KID = hexc('#ff60c0')
DAD = hexc('#ffb050')
NEEDLE = hexc('#ffffff')
FROST = hexc('#d8f0ff')
_TS = np.array([-1.3, -1.0, -0.4, 0.0, 0.6, 1.0, 1.4])
_TC = np.array([hexc('#a0d0ff'), hexc('#70a8ff'), hexc('#4a80e0'), hexc('#ffc890'), hexc('#ff8a30'),
                hexc('#ff4a10'), hexc('#ff1800')])


def temp_colour(T):
    return np.stack([np.interp(T, _TS, _TC[:, c]) for c in range(3)], -1)


def walk(t0, a, b, step, move, hold):
    """Staircase keyframes from a to b: eased moves of `move` s, then `hold` s still. -> (keys, landings)."""
    k = max(1, int(np.ceil(abs(b - a) / step)))
    pts, lands, t = [(t0, a)], [], t0
    for i in range(1, k + 1):
        t += move
        pts.append((t, a + (b - a) * i / k))
        lands.append(t)
        t += hold
        pts.append((t, a + (b - a) * i / k))
    return pts, lands


def render(G, seed=25):
    rng = np.random.default_rng(seed)
    D = 78.0
    n = G.N
    out = np.zeros((nframes(D), n, 3))
    x = G.pd[G.path]
    pi = np.arange(n)
    PF = (pi >= 261) & (pi <= 331)
    a, b = x[261], x[331]
    c = (a + b) / 2
    uPF = (x - a) / (b - a) * 2 - 1                   # -1..1 across the dial

    def needle_pd(S):
        return c + S * (b - a) / 2

    # the setpoint, click by click
    S_keys = [(0, 0.0)]
    def clicks(t0, s0, s1, k, dt):
        for i in range(1, k + 1):
            S_keys.append((t0 + (i - 1) * dt, s0 + (s1 - s0) * (i - 1) / k))
            S_keys.append((t0 + (i - 1) * dt + 0.08, s0 + (s1 - s0) * i / k))
    def snap(t0, s0, s1, d=0.22):
        S_keys.append((t0, s0)); S_keys.append((t0 + d, s1))
    clicks(10.4, 0.0, 0.6, 3, 0.33)
    snap(20.8, 0.6, -0.4)
    clicks(29.8, -0.4, 1.0, 4, 0.25)
    snap(36.2, 1.0, -0.4)
    clicks(45.1, -0.4, 1.35, 6, 0.2)
    snap(50.5, 1.35, -1.0, 0.18)
    clicks(65.8, -1.0, -0.8, 1, 0.3)
    snap(68.6, -0.8, 0.0, 1.6)

    # the kid's movements (path distance) and the dad's
    kid, kl = [], []
    k1, l1 = walk(3.0, -30, needle_pd(0) - 30, 130, 0.18, 0.32)
    k1 = [(tt + (1.2 if tt > 6.4 else 0), p) for tt, p in k1]     # a freeze half way: was that Dad?
    l1 = [tt + (1.2 if tt > 6.4 else 0) for tt in l1]
    kid_keys = k1 + [(11.4, needle_pd(0.6) - 30), (12.8, -40),
                     (25.0, -40)]
    k2, l2 = walk(25.0, -30, needle_pd(-0.4) - 30, 110, 0.14, 0.18)
    kid_keys += k2[1:] + [(31.0, needle_pd(1.0) - 30), (32.3, -40), (38.0, -40)]
    k3, l3 = walk(38.0, -30, 300, 110, 0.18, 0.3)
    kid_keys += k3[1:] + [(39.6, 300), (40.3, -40), (43.8, -40), (45.0, needle_pd(-0.4) - 30),
                          (46.5, needle_pd(1.35) - 30), (47.8, -40), (66.0, -40)]
    kid_lands = l1 + l2 + l3
    kid_vis = [(2.8, 0), (3.1, 1), (13.0, 1), (13.2, 0), (24.8, 0), (25.1, 1), (32.3, 1), (32.5, 0),
               (37.8, 0), (38.1, 1), (40.3, 1), (40.5, 0), (43.6, 0), (43.9, 1), (47.8, 1), (48.0, 0),
               (66.1, 0), (66.25, 1.3), (66.6, 1), (78, 1)]
    kid_keys += [(66.1, 14), (67.4, 14), (68.4, needle_pd(-0.8) - 34), (78, needle_pd(0) - 34)]

    home = x[500] - 10
    d1, dl1 = walk(16.8, home, needle_pd(0.6) + 30, 140, 0.2, 0.25)
    d2, dl2 = walk(21.3, needle_pd(-0.4) + 30, home, 140, 0.2, 0.25)
    d3, dl3 = walk(33.5, home, needle_pd(1.0) + 30, 150, 0.15, 0.13)
    d4, dl4 = walk(41.0, needle_pd(-0.4) + 30, home, 150, 0.15, 0.15)
    d5, dl5 = walk(53.0, needle_pd(-1.0) + 30, home, 150, 0.25, 0.3)
    d6, dl6 = walk(60.4, home, needle_pd(-1.0) + 30, 130, 0.18, 0.32)     # Dad tiptoes like the kid
    dad_keys = [(0, home)] + d1 + d2 + [(33.5, home)] + d3 + [(36.5, needle_pd(-0.4) + 30)]
    dad_keys += [(41.0, needle_pd(-0.4) + 30)] + d4 + [(48.8, home), (50.3, needle_pd(1.35) + 30),
                                                         (50.6, needle_pd(-1.0) + 30), (53.0, needle_pd(-1.0) + 30)]
    dad_keys += d5 + d6 + [(68.4, needle_pd(-0.8) + 34), (78, needle_pd(0) + 34)]
    dad_lands = dl1 + dl2 + dl3 + dl4 + dl5
    tiptoe = dl6
    lock = [(51.4, 0), (52.2, 1), (65.0, 1), (65.5, 0)]

    for kk in (kid_keys, dad_keys, S_keys):
        assert all(kk[i][0] <= kk[i + 1][0] for i in range(len(kk) - 1)), kk
    hist_S = np.zeros(len(out))
    T = np.zeros(n)
    dist = np.abs(x - c)
    delay = (dist / 230.0 / DT).astype(int)
    shimmer = Flicker(rng, n, 0.2, 0.8)
    haze = Flicker(rng, n, 2.0, 5.0)
    frost_seed = rng.uniform(0, 1, n)

    for f in range(len(out)):
        t = f * DT
        buf = np.zeros((n, 3))
        fade = keys(t, [(0, 0), (2.0, 1), (74, 1), (78, 0)])
        S = keys(t, S_keys)
        hist_S[f] = S
        target = hist_S[np.clip(f - delay, 0, None)]
        T += (target - T) * (DT / 1.6)

        # the house: temperature colour, a heat haze when hot, frost creeping when frozen
        I = (0.24 + 0.07 * np.abs(T)) * (1 + 0.04 * shimmer(t))
        hot = np.clip((T - 0.85) / 0.4, 0, 1)
        I = I * (1 + 0.25 * hot * haze(t))
        col = temp_colour(T)
        buf += perc(I * fade)[:, None] * col * (~PF)[:, None]
        frost = np.clip((-T - 0.8) / 0.2, 0, 1) * (frost_seed > 0.82)
        tw = 0.5 + 0.5 * np.sin(2 * np.pi * (0.3 * t + frost_seed * 7))
        buf += light(FROST, 0.35 * frost * tw * fade * ~PF)

        # the dial: a dim scale, tick marks and the needle
        scale = temp_colour(uPF * 1.0)
        ticks = (np.abs(((uPF + 1) * 4) % 1 - 0.5) > 0.42)
        buf += PF[:, None] * (perc(0.13 * fade)[None] * scale + light(scale, 0.12 * ticks * fade))
        npos = needle_pd(S)
        buf += light(NEEDLE, 0.9 * fade * np.exp(-((x - npos) / 4.5) ** 2))
        lk = keys(t, lock)
        if lk > 0:                                    # Dad's lock: two bars close round the needle
            gap = lerp(40, 12, lk)
            bars = np.exp(-((x - npos - gap) / 3) ** 2) + np.exp(-((x - npos + gap) / 3) ** 2)
            buf += light(hexc('#c0d0e0'), 0.75 * min(1, lk * 2) * bars)

        # the kid
        kv = keys(t, kid_vis)
        if kv > 0:
            kp = keys(t, kid_keys)
            pat = 1 + 0.25 * sum(np.exp(-((t - tl) / 0.06) ** 2) for tl in kid_lands if abs(t - tl) < 0.3)
            buf += light(KID, 0.9 * kv * pat * np.exp(-((x - kp) / 9) ** 2))

        # Dad: big and warm; stomps land hard and send a little shudder along the roof
        dp = keys(t, dad_keys)
        up = keys(t, [(15.6, 0.35), (16.6, 1.0), (24.5, 1.0), (25.5, 0.35), (33.0, 0.35), (33.5, 1.0),
                      (44.5, 1.0), (45.5, 0.4), (48.4, 0.4), (48.8, 1.0), (56, 1.0), (57, 0.45),
                      (60.0, 0.45), (60.4, 0.8), (78, 0.8)])
        thump = 0.0
        ring = np.zeros(n)
        for tl in dad_lands:
            if 0 <= t - tl < 0.6:
                u = t - tl
                thump += np.exp(-u / 0.1)
                ring += np.exp(-((np.abs(x - dp) - 30 - 500 * u) / 25) ** 2) * np.exp(-u / 0.2)
        dcol = DAD
        shiver = 0.0
        if 56.0 <= t < 60.4:                          # cold in his chair
            cold = smoothstep(56.0, 58.0, t)
            dcol = lerp(DAD, hexc('#80b0ff'), cold)
            shiver = 3.0 * cold * np.sin(2 * np.pi * 7 * t)
        if t >= 66.1:                                 # caught: he blushes
            dcol = lerp(DAD, hexc('#ff6070'), keys(t, [(66.1, 0), (66.6, 0.8), (68.5, 0.8), (70.5, 0)]))
        if 60.4 <= t < 66.1:
            dcol = lerp(hexc('#80b0ff'), DAD, smoothstep(60.4, 64, t))
        buf += light(dcol, (0.65 * up + 0.25 * thump) * np.exp(-((x - dp - shiver) / 20) ** 2) * fade)
        buf += light(DAD, 0.18 * ring)

        out[f][G.path] = np.clip(buf * keys(t, [(D - 4, 1), (D - 0.5, 0)]), 0, 1)
    return out
