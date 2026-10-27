"""Grill Master: the Porch Front is the grill. Coals catch from the middle and breathe in blackbody
colour, three patties go on, fat drips and flares (sparks fly, Dad spritzes it out), then the
spatula comes up Porch Right and flips them, each one turning edge-on and showing its seared side.
The third flip is too ambitious: the patty spins off along the roof and out the back end of Side,
where the dog is waiting. The lid comes down."""
import numpy as np
from pixelhome.fx import DT, hexc, perc, light, smoothstep, keys, lerp, Flicker, nframes, smooth_noise

CODE = 'FA01'
TITLE = 'Grill Master'
KIND = 'show'
DESCRIPTION = ('The porch is the grill: coals breathe, fat flares, the spatula flips each patty edge-on. '
               'The third flip goes over the roof and out the back, where the dog is waiting.')

STEEL = hexc('#9fb4c8')
FLAME = hexc('#ffb030')
MIST = hexc('#a8d8ff')
RAW = hexc('#ff3a3a')
SEAR = hexc('#a04010')
DOG = hexc('#ffc070')
SMOKE = hexc('#8090a0')

# blackbody-ish hue by temperature 0..1 (normalised chroma; brightness comes from perc(T))
_HS = np.array([0.0, 0.3, 0.55, 0.8, 1.0])
_HC = np.array([[1.0, 0.0, 0.0], [1.0, 0.04, 0.0], [1.0, 0.16, 0.0], [1.0, 0.4, 0.04], [1.0, 0.72, 0.35]])


def blackbody(T):
    T = np.clip(T, 0, 1.2)
    hue = np.stack([np.interp(T, _HS, _HC[:, c]) for c in range(3)], -1)
    return perc(T)[:, None] * hue


def render(G, seed=21):
    rng = np.random.default_rng(seed)
    D = 70.0
    n = G.N
    out = np.zeros((nframes(D), n, 3))
    x = G.pd[G.path]                                  # path distance, path order
    pi = np.arange(n)
    PF = (pi >= 261) & (pi <= 331)
    SIDES = ((pi >= 179) & (pi <= 260)) | ((pi >= 332) & (pi <= 380))
    a, b = x[261], x[331]
    c = (a + b) / 2
    pats = [c - 112, c, c + 112]                      # patty centres (pd)
    HW = 24.0                                         # patty half width
    pr_front = x[380]

    wind = smooth_noise(rng, x, 60, 3)
    coal = Flicker(rng, n, 0.08, 0.5)
    fast = Flicker(rng, n, 4, 9)
    # sparks: 1-D particles along the path
    sp_x, sp_v, sp_t, sp_h = [], [], [], []

    def burst(x0, k, speed, heat, t0):
        for _ in range(k):
            sp_x.append(x0 + rng.normal(0, 6))
            sp_v.append(rng.normal(0, speed))
            sp_t.append(t0)
            sp_h.append(heat * rng.uniform(0.6, 1.0))

    sizzle_events = [(14.5, 0), (15.3, 1), (16.1, 2), (32.3, 2), (35.1, 1)]
    flips = [(31.2, 2, 1.0), (34.0, 1, 1.0)]          # (start, patty, duration)
    spatula = [(29.4, pr_front + 40), (31.0, pats[2] + 30), (31.2, pats[2] + 30), (32.2, pats[2] + 34),
               (33.0, pats[2] + 30), (33.8, pats[1] + 30), (35.0, pats[1] + 34), (36.0, pats[1] + 30),
               (36.9, pats[0] + 30), (37.2, pats[0] + 30), (37.65, pats[0] + 62), (37.85, pats[0] + 20),
               (40.5, pats[0] + 20), (46.0, pats[0] + 20), (46.6, pats[0] + 6), (46.8, pats[0] + 18),
               (47.1, pats[0] + 6), (47.3, pats[0] + 18), (48.2, pats[0] + 18), (49.8, pr_front + 40)]
    spat_on = [(29.3, 0), (29.6, 1), (49.4, 1), (49.8, 0)]
    taps = (46.6, 47.1)
    gone = 37.85                                      # patty 3 leaves
    fly_end = 40.6
    last_spark = -1.0
    last_trail = [-1.0]
    P = G.pos[G.path]
    grill = np.array([(-22.0, 150.0, -569.0)])
    dist = np.linalg.norm(P - grill[0], axis=1)
    yard = 1 / (1 + (dist / 260) ** 2)
    WING = ~(PF | SIDES)

    for f in range(len(out)):
        t = f * DT
        buf = np.zeros((n, 3))

        # ---- the lighter: two clicks, then the flame catches at the centre
        for tc, amp in ((1.0, 0.35), (1.55, 0.4)):
            if tc <= t < tc + 0.12:
                buf += light(FLAME, amp * np.exp(-((x - c) / 5) ** 2))
        if 2.1 <= t < 4.5:
            e = smoothstep(2.1, 2.3, t) * (1 - smoothstep(3.5, 4.5, t))
            buf += light(FLAME, 0.7 * e * np.exp(-((x - c) / 14) ** 2) * (1 + 0.15 * fast(t)))

        # ---- the coal bed
        front = keys(t, [(2.4, 0), (11.0, 200)])
        ign = np.clip((front - np.abs(x - c)) / 40, 0, 1) * PF
        heat = keys(t, [(2.4, 0), (6, 0.35), (13, 0.62), (58, 0.62), (62, 0.5), (70, 0)])
        breath = 0.06 * np.sin(2 * np.pi * t / 5.5) + 0.04 * np.sin(2 * np.pi * t / 2.3 + 1)
        gust = 0.09 * np.interp((x - 55 * t) % G.length, x, wind)
        T = ign * (heat * (1 + breath + gust + 0.07 * coal(t)))

        # patty geometry: lift (0..1) and cover width (|cos| of the flip angle)
        cover = np.zeros(n)
        patty_buf = np.zeros((n, 3))
        for k, pc in enumerate(pats):
            t_on = (14.5, 15.3, 16.1)[k]
            if t < t_on:
                continue
            pos, w, side, lift = pc, 1.0, 0.0, 0.0
            for ts, kk, dur in flips:
                if kk == k and t >= ts:
                    u = np.clip((t - ts) / dur, 0, 1)
                    ang = np.pi * smoothstep(0, 1, u)
                    w = abs(np.cos(ang))
                    side = smoothstep(0.45, 0.55, u)
                    lift = np.sin(np.pi * u)
                    pos = pc + 10 * np.sin(np.pi * u)
            if k == 0 and t >= gone:
                if t > fly_end:
                    continue
                u = (t - gone) / (fly_end - gone)
                pos = pc - (pc + 60) * (u ** 1.15)
                w = abs(np.cos(2 * np.pi * 3.2 * (t - gone)))
                side = 0.5 + 0.5 * np.sign(np.cos(2 * np.pi * 1.6 * (t - gone)))
                lift = 1.0
            hw = HW * max(w, 0.08)
            m = np.clip((hw - np.abs(x - pos)) / 3 + 0.5, 0, 1)
            col = lerp(SEAR * 0.55, lerp(RAW * 0.5, hexc('#ff7020'), side), lift)
            bright = 0.14 + 0.36 * lift
            if k == 0 and t >= gone:                  # airborne: catch the light, shed sparks
                bright = 0.75
                if t - last_trail[0] > 0.04:
                    burst(pos, 2, 40, 0.55, t)
                    last_trail[0] = t
            patty_buf += m[:, None] * light(col, bright)
            if lift < 0.2:
                cover = np.maximum(cover, m * (1 - lift / 0.2))
            if lift > 0:                              # coals under a lifted patty are hotter, exposed
                under = np.clip((HW - np.abs(x - pc)) / 3 + 0.5, 0, 1)
                T = T + 0.16 * under * lift * PF
        T = T * (1 - cover)
        buf += blackbody(T)
        buf += patty_buf

        # rim sizzle around patties on the grate
        for k, pc in enumerate(pats):
            if t >= (14.5, 15.3, 16.1)[k] and not (k == 0 and t >= gone):
                rim = np.exp(-((np.abs(x - pc) - HW) / 4) ** 2)
                buf += light(FLAME, 0.22 * rim * np.clip(fast(t), 0, 1) ** 3 * (heat / 0.62))

        # grill body: Porch Left/Right as the sides, a warm shimmer near the back
        depth = np.clip(1 - np.minimum(np.abs(x - x[260]), np.abs(x - x[332])) / 300, 0, 1)
        body = keys(t, [(3, 0), (8, 1), (60, 1), (66, 0.3), (70, 0)])
        buf += SIDES[:, None] * light(STEEL, 0.07 * body * np.ones(n))
        buf += SIDES[:, None] * light(hexc('#ff3000'), 0.18 * body * depth ** 2 * (1 + 0.2 * coal(t)))

        # the grill lights the yard: the wings and Side catch a faint warm glow, more in the flare
        glow = keys(t, [(3, 0), (12, 0.1), (58, 0.1), (62, 0.04), (70, 0)])
        flare_now = keys(t, [(23.3, 0), (23.6, 0.9), (26.0, 0.9), (27.3, 0)])
        g = (glow + 0.28 * flare_now * (0.8 + 0.2 * fast(t))) * yard
        buf += light(hexc('#ff5010'), g * (PF == 0))
        # smoke drifting outward along the roof from the grill, both ways
        sm_on = keys(t, [(8, 0), (14, 0.16), (56, 0.16), (60, 0.1), (68, 0)])
        if sm_on > 0:
            far = np.where(x < c, c - x, x - c)
            puff = 0.5 + 0.5 * np.sin(2 * np.pi * (far - 38 * t) / 260)
            puff = puff ** 4 * (0.6 + 0.4 * np.interp((far - 20 * t) % G.length, x, wind))
            buf += light(SMOKE, sm_on * puff * np.clip((far - 160) / 200, 0, 1) * np.exp(-far / 1400) * WING)

        # ---- events: sizzles and the flare-up
        for te, k in sizzle_events:
            if te <= t < te + DT:
                burst(pats[k], 14, 70, 0.8, t)
        if 23.4 <= t < 27.2 and t - last_spark > 0.07:
            burst(pats[1] + rng.normal(0, 15), 3, 160, 1.0, t)
            last_spark = t
        flare = keys(t, [(23.3, 0), (23.6, 1.0), (24.6, 0.8), (25.4, 1.05), (26.0, 0.9), (26.45, 0.5),
                         (26.85, 0.2), (27.3, 0)])
        if flare > 0:
            wfl = 40 + 50 * flare
            F = flare * np.exp(-((x - pats[1]) / wfl) ** 2) * (0.75 + 0.35 * np.clip(fast(t), -1, 1))
            buf += light(FLAME, np.clip(F, 0, 1.1))
            buf += light(hexc('#ff6010'), 0.4 * flare * depth ** 3 * SIDES)
        for ts in (26.0, 26.4, 26.8):                 # spritz, spritz, spritz
            if ts <= t < ts + 0.35:
                e = np.exp(-(t - ts) / 0.1)
                buf += light(MIST, 0.6 * e * np.exp(-((x - pats[1] - 18) / 30) ** 2))
        st = keys(t, [(26.2, 0), (27.2, 0.35), (30, 0)])
        if st > 0:                                    # steam drifting off
            buf += light(SMOKE, st * np.exp(-((x - pats[1] - 25 * (t - 26.2)) / 60) ** 2) *
                         (0.7 + 0.3 * coal(t * 3)))

        # sparks
        if sp_x:
            X = np.array(sp_x)
            V = np.array(sp_v) * np.exp(-2.2 * DT)
            age = t - np.array(sp_t)
            H = np.array(sp_h) * np.exp(-age / 0.45)
            X = X + V * DT
            keep = H > 0.03
            sp_x[:] = list(X[keep]); sp_v[:] = list(V[keep]); sp_h[:] = list(np.array(sp_h)[keep])
            sp_t[:] = list(np.array(sp_t)[keep])
            if keep.any():
                Xk, Hk = X[keep], H[keep]
                I = (Hk[:, None] * np.exp(-((x[None] - Xk[:, None]) / 3.0) ** 2)).sum(0)
                buf += blackbody(np.clip(I, 0, 1.1)) * 0.9

        # ---- the spatula
        so = keys(t, spat_on)
        if so > 0:
            sx = keys(t, spatula)
            tap = sum(np.exp(-((t - tt) / 0.06) ** 2) for tt in taps)
            buf += light(STEEL, so * (0.7 + 0.3 * tap) * np.exp(-((x - sx) / 9) ** 4))

        # ---- the dog at the back of Side
        de = keys(t, [(41.8, 0), (42.3, 1), (43.6, 1), (43.9, 0)])
        blink = 1 - max(0.0, 1 - abs(t - 42.9) / 0.1)
        if de > 0:
            eyes = np.exp(-((x - 10) / 3.5) ** 2) + np.exp(-((x - 26) / 3.5) ** 2)
            buf += light(DOG, 0.5 * de * blink * eyes)
        if 43.8 <= t < 46.0:                          # chomp, then a wag
            e = smoothstep(43.8, 44.1, t) * (1 - smoothstep(45.5, 46.0, t))
            wag = 48 + 14 * np.sin(2 * np.pi * 2.6 * (t - 43.8))
            buf += light(DOG, 0.35 * e * np.exp(-((x - wag) / 9) ** 2))

        # ---- lid: a dark sweep from right to left, vents glowing through
        lid = keys(t, [(58.5, b + 20), (61.5, a - 20)])
        if t > 58.5:
            closed = smoothstep(-6, 6, x - lid) * PF
            buf *= (1 - closed)[:, None]
            vents = (np.cos(2 * np.pi * (x - a) / 43) > 0.85) * closed
            buf += light(hexc('#ff2800'), vents * keys(t, [(59, 0), (62, 0.3), (66, 0.22), (70, 0)]) *
                         (1 + 0.15 * coal(t)))
            sm = keys(t, [(61, 0), (63, 0.18), (70, 0)])
            for k, ph in ((0, 0.0), (1, 1.7)):
                drift = ((t - 61) * 55 + 120 * k) % 380
                xs = x[260] - drift if k == 0 else x[332] + drift
                buf += light(SMOKE, sm * np.exp(-((x - xs) / 40) ** 2) * (0.7 + 0.3 * np.sin(t * 1.3 + ph)))

        out[f][G.path] = np.clip(buf, 0, 1)
    return out
