"""Wishbone: The porch is the wishbone, the keel in the middle of Porch Front and a prong down each porch side;
the wings are the two people pulling it, Left (and Side behind it) in cranberry, Right in gold. The bone draws
itself out of the keel, gold comes in from the free end of Right, cranberry pops up on Left, and they size each
other up on alternate beats before a four-count squeeze.

While they pull, the whole porch is a tug of war: the bone splits into cranberry and gold territory at a flag that
sways back and forth with whoever is winning, stress stripes crawl in from both grips toward the flag and tighten
and heat from ivory to white as the tension rises, every heave on the beat pulses the bone and both wings, and the
wings haul stripes outward, faster on the side that is winning. Creaks are white bursts that ring out along the
bone. In round one gold's hand slips: the grip shoots out the free end of Right and cranberry falls over
backwards, a jolt running out Left and Side to the back of the house. They regrip, count again faster, and round
two sways harder and faster, in G now, with two near-snaps at the flaw (a flicker, a beat of frozen silence, then
relief) and a last frantic heave. Then a second of stillness, and SNAP: the two halves fly across the house to the
free ends, cranberry's short piece out the back of Side, gold's long piece with the keel out the end of Right,
trailing gold dust. Gold flares at the end, the wish sweeps back over the whole outline, and the house marches
in gold, the wings answering each other, to a last full-house chord."""
import numpy as np
from pixelhome.fx import DT, hexc, light, keys, smoothstep, lerp, Flicker, colormap, nframes

CODE = 'TG01'
TITLE = 'Wishbone'
KIND = 'show'
DESCRIPTION = ('A tug of war across the porch: the wishbone sways, creaks and nearly snaps, one hand slips, they '
               'grip again, and it breaks, flinging both halves to the ends of the house. Gold makes the wish.')
VOICEOVER = "Two hands, one wishbone, and only one of them gets the wish."

IVORY = hexc('#ffb070')
CRANBERRY = hexc('#d0102a')
GOLD = hexc('#ffa800')
AMBER = hexc('#ff7a10')
WARM = hexc('#ffd8a8')
WHITE = hexc('#fff4e8')
BROWN = hexc('#4a1604')

D = 90.0
BEAT, BAR = 0.5, 2.0                    # 120 to the minute, four to the bar
G0, G1 = 893.0, 2033.0                  # the grips: the porch's front corners, the ends of the bone
KEEL = 1486.0                           # the middle of Porch Front
FLAW = 1240.0                           # the thin spot near the root of cranberry's prong
ROOTS = (1311.0, 1660.0)
END = 2512.0

T_IN = (1.0, 3.0, 5.0)                  # the bone draws itself, gold enters, cranberry pops up
COUNT1 = (10.0, 10.5, 11.0, 11.5)
T_PULL1, T_SLIP = 12.0, 28.0
COUNT2 = (34.0, 34.5, 35.0, 35.5)
T_PULL2 = 36.0
NEAR = (44.0, 54.0)                     # near-snaps: flicker 0.5 s, then a frozen beat
T_STILL, T_SNAP = 63.0, 64.0
FLY_L, FLY_R = 1.3, 1.6                 # how long each half takes to fly to its free end
T_WISH, T_MARCH, T_FINAL = 68.0, 70.0, 86.0
JOLT = 1200.0                           # the slip's jolt, units/s out along Left and Side

stress_map = colormap([(0.0, (1.0, 0.69, 0.44)), (0.4, (1.0, 0.45, 0.1)), (0.7, (1.0, 0.3, 0.03)),
                       (0.9, (1.0, 0.65, 0.3)), (1.1, (1.0, 0.95, 0.85))])


def sway(t0, t1, period, amp, b0, b1, sign):
    """Keyframes swinging +-amp every half period around a bias drifting b0 -> b1."""
    pts, t, s = [], t0 + period / 2, sign
    while t <= t1 + 1e-6:
        pts.append((t, b0 + (b1 - b0) * (t - t0) / (t1 - t0) + s * amp))
        s, t = -s, t + period / 2
    return pts


# how far the bone has been dragged (+ toward gold) and the tension in it
X_KEYS = ([(0, 0), (T_PULL1, 0), (13.5, 70), (15, 110), (16.5, 30), (18, -90), (19.5, -130), (20.5, -60),
           (21.5, 40), (22.5, 120), (23, 70), (23.5, -10), (24, -60), (24.5, 0), (25, 70), (25.5, 10), (26, 110),
           (27, 150), (T_SLIP, 170), (T_SLIP + 0.25, -300), (T_SLIP + 0.6, -200), (T_SLIP + 0.95, -260),
           (T_SLIP + 1.4, -215), (30, -235), (31.5, -60), (32, 0), (T_PULL2, 0)]
          + sway(T_PULL2, NEAR[0], 4, 110, 0, -40, 1) + [(NEAR[0] + 1, -40), (46, 0)]
          + sway(46, NEAR[1], 2, 150, 0, 30, -1) + [(NEAR[1] + 1, 30), (55, 0)]
          + sway(55, 62, 1, 70, 0, 90, 1) + [(T_STILL, 100), (T_SNAP, 100)])
T_KEYS = [(0, 0), (T_PULL1, 0), (12.5, 0.35), (16, 0.45), (20, 0.52), (24, 0.62), (27, 0.72), (T_SLIP, 0.8),
          (T_SLIP + 0.05, 0), (T_PULL2, 0), (36.5, 0.45), (43.5, 0.72), (NEAR[0], 0.9), (NEAR[0] + 0.5, 1.0),
          (NEAR[0] + 1, 0.35), (46, 0.5), (53.5, 0.88), (NEAR[1], 0.95), (NEAR[1] + 0.5, 1.05), (NEAR[1] + 1, 0.4),
          (55.5, 0.6), (62, 1.05), (T_STILL, 1.1), (T_STILL + 0.05, 0.12), (T_SNAP, 0.15), (T_SNAP + 0.01, 0)]


def pulling(t):
    return (T_PULL1 <= t < T_SLIP) or (T_PULL2 <= t < T_STILL)


def frozen(t):
    """1 in the beat of frozen silence after each near-snap, and in the stillness before the snap."""
    f = max([smoothstep(n + 0.45, n + 0.5, t) * (1 - smoothstep(n + 0.95, n + 1.05, t)) for n in NEAR])
    return max(f, float(T_STILL <= t < T_SNAP))


def heave(t):
    """A pulse on every beat while they pull."""
    if not pulling(t) or frozen(t) > 0.5:
        return 0.0
    return float(np.exp(-((t + 1e-6) % BEAT) / 0.12))


def motion():
    """Per frame: drag, its velocity, tension, and the integrated phases of the bone's stripes and each wing's."""
    F = nframes(D)
    ts = np.arange(F) * DT
    X = np.array([keys(t, X_KEYS) for t in ts])
    T = np.array([keys(t, T_KEYS) for t in ts])
    V = np.gradient(X, DT)
    fz = np.array([frozen(t) for t in ts])
    lam = 200 - 150 * np.clip(T, 0, 1)                       # stripes tighten with the tension
    speed = (1 + 5 * np.clip(T, 0, 1.1)) * (1 - fz)          # crawl rate in stripes/s, capped at about 6
    ph = np.cumsum(2 * np.pi * speed * DT)
    lead = np.clip(V / 200, -1, 1)
    effL = T * (0.6 + 0.4 * np.clip(-lead, 0, 1)) * (1 - 0.6 * fz)
    effR = T * (0.6 + 0.4 * np.clip(lead, 0, 1)) * (1 - 0.6 * fz)
    idle = np.array([0.18 * smoothstep(6.5, 8, t) * (t < T_SNAP) for t in ts])
    phL = np.cumsum(2 * np.pi * (0.4 + 3 * (effL + idle)) * DT)
    phR = np.cumsum(2 * np.pi * (0.4 + 3 * (effR + idle)) * DT)
    return X, V, T, lam, ph, effL + idle, effR + idle, phL, phR, fz


def creaks(seed=31):
    """(time, bone coordinate, strength) of every creak: sparse in round one, on the off-beats and then every
    eighth as round two builds; most of them at the flaw and the roots of the prongs."""
    rng = np.random.default_rng(seed)
    times = list(np.arange(16.75, 27.5, 2.0)) + list(np.arange(26.25, 27.9, 0.5))
    times += list(np.arange(37.75, 43.9, 1.5)) + list(np.arange(46.75, 53.9, 1.0)) + list(np.arange(51.25, 53.9, 1.0))
    times += list(np.arange(55.75, 59.9, 0.5)) + list(np.arange(60.0, 62.9, 0.25))
    out = []
    for t in sorted(times):
        r = rng.uniform()
        s = (FLAW + rng.normal(0, 25)) if r < 0.4 else (rng.choice(ROOTS) + rng.normal(0, 30)) if r < 0.7 \
            else rng.uniform(G0 + 40, G1 - 40)
        out.append((float(t), float(s), float(0.55 + 0.45 * min(1, keys(t, T_KEYS)))))
    return out


def flight(u, c0, h0, c1, h1, dur):
    """A half of the bone thrown from (centre c0, half-length h0) to (c1, h1): fast out, slowing into the end."""
    v = np.clip(u / dur, 0, 1)
    e = 1 - (1 - v) ** 2.2
    return c0 + (c1 - c0) * e, h0 + (h1 - h0) * e


def render(G, seed=31):
    F = nframes(D)
    out = np.zeros((F, G.N, 3))
    n = G.N
    pdp = G.pd[G.path]
    LW = pdp < G0                           # cranberry's side: Left and Side behind it
    RW = pdp > G1                           # gold's side: Right
    PORCH = ~LW & ~RW
    dl = np.clip(G0 - pdp, 0, None)         # distance out from each grip
    dr = np.clip(pdp - G1, 0, None)
    side_dim = np.where(pdp < 490, 0.75, 1.0)
    rng = np.random.default_rng(seed)
    twinkle = Flicker(rng, n, 0.6, 2.5)
    tremble = Flicker(rng, n, 5.0, 9.0)
    sparks_v = rng.uniform(300, 1300, 14) * np.where(np.arange(14) % 2, 1, -1)
    sparks_l = rng.uniform(0.3, 0.7, 14)
    X, V, T, lam, ph, effL, effR, phL, phR, fz = motion()
    CR = creaks(seed)
    cr_t = np.array([c[0] for c in CR])
    # where each half of the bone starts and ends its flight
    cl0, hl0 = (G0 + FLAW) / 2, (FLAW - G0) / 2
    cr0, hr0 = (FLAW + G1) / 2, (G1 - FLAW) / 2
    cl1, hl1, cr1, hr1 = 60.0, 60.0, END - 90.0, 90.0
    us = np.linspace(0, FLY_R, 600)
    fronts = np.array([sum(flight(u, cr0, hr0, cr1, hr1, FLY_R)) for u in us])
    t_pass = T_SNAP + np.interp(pdp, fronts, us, left=0.0, right=1e9)          # when the gold half passed each pixel
    t_pass = np.where(pdp < FLAW, 1e9, t_pass)
    usl = np.linspace(0, FLY_L, 400)
    backs = np.array([np.subtract(*flight(u, cl0 + 100, hl0, cl1, hl1, FLY_L)) for u in usl])  # trailing edge
    t_passl = T_SNAP + np.interp(-pdp, -backs, usl, left=0.0, right=1e9)
    t_passl = np.where(pdp > G0 + 100, 1e9, t_passl)
    gold_land = T_SNAP + FLY_R

    for f in range(F):
        t = f * DT
        buf = light(BROWN, keys(t, [(0, 0), (1, 0.08), (87, 0.08), (90, 0)]) * np.ones(n))
        Tf, x, hv, fzf = T[f], X[f], heave(t), fz[f]

        # ---------------- the bone, until it snaps ----------------
        if t < T_SNAP:
            reach = 590 * smoothstep(T_IN[0], T_IN[0] + 1.8, t)
            drawn = np.clip((reach - np.abs(pdp - KEEL)) / 20, 0, 1) * PORCH
            s = pdp - x                                         # bone coordinates
            flag = KEEL
            side = np.clip((s - flag) / 40 + 0.5, 0, 1)         # 0 cranberry's territory, 1 gold's
            tint = lerp(CRANBERRY, GOLD, side[:, None])
            base = lerp(IVORY, tint, 0.75 * smoothstep(T_PULL1 - 2, T_PULL1, t))
            weak = 1 + 0.5 * np.exp(-((s - FLAW) / 70) ** 2) + 0.3 * (np.exp(-((s - ROOTS[0]) / 80) ** 2) +
                                                                     np.exp(-((s - ROOTS[1]) / 80) ** 2))
            k = 2 * np.pi / lam[f]
            arg = np.where(s < flag, k * (s - G0), -k * (s - G1))      # crests crawl in from both grips
            crest = (0.5 + 0.5 * np.cos(arg - ph[f])) ** (1 + 4 * min(1, Tf))
            idle = 0.35 * smoothstep(T_IN[0] + 1.8, T_IN[0] + 3, t)
            amp = np.maximum(0.12 + 0.6 * min(1.1, Tf), idle) * weak * (1 - 0.5 * fzf)
            stc = stress_map(np.clip(Tf * weak * 0.85, 0, 1.1))
            dim = 1 - 0.65 * fzf
            buf += light(1.0, drawn * (0.4 + 0.12 * hv) * dim) * base
            buf += light(1.0, drawn * np.clip(amp * crest * (1 + 0.5 * hv), 0, 1.2)) * stc
            # the flag: a bright seam where the two territories meet
            fl = np.exp(-((s - flag) / 10) ** 2) * drawn * smoothstep(T_PULL1 - 1, T_PULL1, t) * (Tf > 0.02)
            buf += light(WARM, (0.55 + 0.3 * hv) * fl * dim)
            # the tip of the bone drawing itself
            if t < T_IN[0] + 2:
                tip = np.exp(-((np.abs(pdp - KEEL) - reach) / 12) ** 2) * PORCH
                buf += light(WARM, 0.9 * tip * smoothstep(T_IN[0], T_IN[0] + 0.2, t))
            # the stillness: only the flaw, glowing hotter
            if T_STILL <= t < T_SNAP:
                u = t - T_STILL
                buf += light(WHITE, (0.2 + 0.6 * u) * (1 + 0.3 * tremble(t)) * np.exp(-((pdp - FLAW - x) / (30 - 20 * u)) ** 2))

        # ---------------- creaks: white bursts ringing out along the bone ----------------
        for i in np.nonzero((t - cr_t >= 0) & (t - cr_t < 0.5))[0]:
            u = t - cr_t[i]
            p, a = CR[i][1] + keys(cr_t[i], X_KEYS), CR[i][2]
            buf += light(WHITE, a * np.exp(-u / 0.07) * np.exp(-((pdp - p) / 14) ** 2))
            ring = np.exp(-((np.abs(pdp - p) - 650 * u) / 25) ** 2) * np.exp(-u / 0.18) * PORCH
            buf += light(WARM, 0.75 * a * ring)

        # ---------------- near-snaps: a flicker at the flaw, then the frozen beat ----------------
        for tn in NEAR:
            u = t - tn
            if 0 <= u < 0.5:
                fl = float(np.sin(2 * np.pi * 8 * u) > 0)
                buf += light(WHITE, (0.5 + 0.5 * fl) * np.exp(-((pdp - FLAW - x) / (60 + 200 * u)) ** 2))
            if 0.5 <= u < 1.0:
                buf += light(WHITE, 0.5 * np.exp(-((pdp - FLAW - x) / 12) ** 2))

        # ---------------- the two people ----------------
        if t < T_SNAP + 1.5:
            gone = 1 - smoothstep(T_SNAP, T_SNAP + 1.2, t)
            # gold enters from the free end of Right, cranberry pops up on Left
            inR = (pdp >= END - 479 * smoothstep(T_IN[1], T_IN[1] + 1.4, t))
            inL = dl <= 893 * smoothstep(T_IN[2], T_IN[2] + 1.4, t)
            if t < T_IN[1] + 1.6:
                head = END - 479 * smoothstep(T_IN[1], T_IN[1] + 1.4, t)
                buf += light(WARM, 0.9 * np.exp(-((pdp - head) / 12) ** 2) * (t >= T_IN[1]))
            if T_IN[2] <= t < T_IN[2] + 1.0:
                buf += light(WARM, np.exp(-(t - T_IN[2]) / 0.25) * np.exp(-(dl / 40) ** 2) * LW)
            # the regrip: gold sweeps back in from the free end, cranberry flashes up
            if T_SLIP + 4 <= t < T_SLIP + 6:
                rg = smoothstep(T_SLIP + 4, T_SLIP + 4.6, t)
                inR = inR & (pdp >= END - 479 * rg)
                buf += light(WARM, 0.9 * np.exp(-((pdp - (END - 479 * rg)) / 12) ** 2) * (rg < 1))
                buf += light(WARM, np.exp(-max(0, t - T_SLIP - 4.5) / 0.25) * np.exp(-(dl / 60) ** 2) * LW
                             * (t >= T_SLIP + 4.5))
            haulL = (0.5 + 0.5 * np.cos(2 * np.pi * dl / 120 - phL[f])) ** 3
            haulR = (0.5 + 0.5 * np.cos(2 * np.pi * dr / 120 - phR[f])) ** 3
            eL, eR = effL[f], effR[f]
            Lw = (0.22 + 0.3 * eL + 0.2 * hv) + (0.15 + 0.5 * eL) * haulL
            Rw = (0.22 + 0.3 * eR + 0.2 * hv) + (0.15 + 0.5 * eR) * haulR
            Lw = Lw * (1 - 0.35 * np.clip(dl / 893, 0, 1)) * side_dim
            Rw = Rw * (1 - 0.3 * np.clip(dr / 479, 0, 1))
            # the slip: gold's grip shoots out the free end, cranberry falls back, a jolt to the back of the house
            if T_SLIP <= t < T_SLIP + 4.5:
                u = t - T_SLIP
                Rw = Rw * (1 - 0.7 * smoothstep(0, 0.2, u) * (1 - smoothstep(3.5, 4.0, u)))
                buf += light(GOLD, np.exp(-((pdp - (G1 + 1000 * u)) / 22) ** 2) * (u < 0.6) * RW)
                buf += light(CRANBERRY, 0.9 * np.exp(-((dl - JOLT * u) / 80) ** 2) * np.exp(-u / 1.0) * LW)
                th = 893 / JOLT
                if u >= th:                 # he lands at the back of Side
                    buf += light(WARM, 0.9 * np.exp(-(u - th) / 0.3) * np.exp(-(pdp / 70) ** 2))
                if 2.0 <= u < 4.0:          # gets up, dusts off, grumbles on the beats
                    Lw = Lw * (0.7 + 0.5 * np.exp(-((u + 1e-6) % BEAT) / 0.1))
            # sizing each other up before round one: grip flares out along the wings on alternate beats
            if 7.0 <= t < COUNT1[0]:
                k = int((t - 7.0) / BEAT)
                u = t - 7.0 - k * BEAT
                w = np.exp(-((np.where(k % 2 == 0, dl, dr) - 900 * u) / 50) ** 2) * np.exp(-u / 0.3)
                buf += light(WARM, 0.7 * w * (LW if k % 2 == 0 else RW))
            # the countdowns: each squeeze throws a flash out from both grips, brighter each time
            for i, tc in enumerate(COUNT1 + COUNT2):
                u = t - tc
                if 0 <= u < 0.45:
                    a = (0.5 + 0.15 * (i % 4)) * np.exp(-u / 0.15)
                    w = np.exp(-((np.minimum(dl + 1e9 * ~LW, dr + 1e9 * ~RW) - 1500 * u) / 60) ** 2)
                    buf += light(WARM, a * w)
                    buf += light(IVORY, 0.4 * a * PORCH)
            buf += light(CRANBERRY, Lw * inL * LW * gone)
            buf += light(GOLD, Rw * inR * RW * gone)

        # ---------------- SNAP ----------------
        if t >= T_SNAP:
            u = t - T_SNAP
            buf += light(WHITE, np.exp(-u / 0.1) * np.exp(-((pdp - FLAW - X[f]) / 140) ** 2))
            buf += light(WARM, 0.55 * np.exp(-u / 0.18) * PORCH)
            for k in range(14):             # splinters both ways
                p = FLAW + 100 + sparks_v[k] * 0.5 * (1 - np.exp(-u / 0.5))
                buf += light(WHITE, 0.8 * np.exp(-u / sparks_l[k]) * np.exp(-((pdp - p) / 5) ** 2))
            off = 100.0                     # where the bone was dragged when it broke
            beat_l = np.exp(-((t + 1e-6 - BEAT) % BAR) / 0.15) * (T_MARCH <= t < T_FINAL)
            # cranberry's short half flies out the back of Side
            c, h = flight(u, cl0 + off, hl0, cl1, hl1, FLY_L)
            body = np.clip((h - np.abs(pdp - c)) / 8 + 0.5, 0, 1)
            col = lerp(IVORY, CRANBERRY, smoothstep(0, 0.8, u))
            tail = np.exp(-np.clip(pdp - (c + h), 0, None) / 120) * (pdp > c + h) * (u < FLY_L + 0.4) \
                * (pdp < cl0 + off + hl0) * np.exp(-max(0, u - FLY_L) / 0.15)
            sulk = keys(t, [(T_SNAP, 0.85), (T_SNAP + FLY_L, 0.85), (T_SNAP + FLY_L + 0.8, 0.4), (84, 0.4), (89, 0)])
            buf += light(1.0, body * sulk * (1 + 0.3 * beat_l)) * col + light(CRANBERRY, 0.5 * tail)
            agl = t - t_passl
            buf += light(CRANBERRY, 0.6 * np.where(agl >= 0, np.exp(-np.clip(agl, 0, None) / 0.9), 0)
                         * (0.5 + 0.5 * twinkle(t)) ** 2)
            if u >= FLY_L:
                v = u - FLY_L
                buf += light(WARM, 0.8 * np.exp(-v / 0.3) * np.exp(-(pdp / 160) ** 2))
            # gold's long half, with the keel, flies out the end of Right trailing gold dust
            c, h = flight(u, cr0 + off, hr0, cr1, hr1, FLY_R)
            body = np.clip((h - np.abs(pdp - c)) / 8 + 0.5, 0, 1)
            col = lerp(IVORY, GOLD, smoothstep(0, 0.6, u))
            beat_ = np.exp(-((t + 1e-6) % BEAT) / 0.15) * (T_MARCH <= t < T_FINAL)
            buf += light(1.0, body * keys(t, [(T_SNAP, 1.0), (gold_land, 1.0), (T_WISH + 2, 0.45), (87, 0.45), (90, 0)])
                         * (1 + 0.5 * beat_)) * col
            buf += light(WARM, 0.7 * np.exp(-((pdp - (c + h)) / 18) ** 2) * (u < FLY_R))
            age = t - t_pass
            dust = np.where(age >= 0, np.exp(-np.clip(age, 0, None) / 1.6), 0) * (1 - smoothstep(T_WISH, T_WISH + 1, t))
            buf += light(GOLD, 0.75 * dust * (0.55 + 0.45 * twinkle(t)) ** 2)
            if t >= gold_land:              # it lands: a flare at the end, throbbing on the beats until the wish
                v = t - gold_land
                buf += light(WARM, np.exp(-v / 0.25) * np.exp(-((END - pdp) / 220) ** 2))
                if t < T_WISH:
                    thr = np.exp(-((t + 1e-6) % BEAT) / 0.15)
                    buf += light(GOLD, (0.3 + 0.35 * thr) * np.exp(-((END - pdp) / (150 + 60 * v)) ** 2))
            # the losers' wings fall dark around the flight; Left and Right keep an ember
            buf += light(CRANBERRY, 0.18 * LW * side_dim * (1 - smoothstep(T_WISH + 0.5, T_WISH + 1.5, t)))
            buf += light(GOLD, 0.2 * RW * (1 - smoothstep(T_WISH, T_WISH + 1, t)))

        # ---------------- the wish: gold sweeps back over the whole outline ----------------
        if t >= T_WISH:
            u = t - T_WISH
            fp = END - END / (T_MARCH - T_WISH) * u
            behind = np.clip((pdp - fp) / 30, 0, 1)
            fade = keys(t, [(T_WISH, 1), (87, 1), (90, 0)])
            if t < T_MARCH + 0.3:
                buf += light(WARM, np.exp(-((pdp - fp) / 25) ** 2))
            glow = (0.34 - 0.12 * smoothstep(T_MARCH, T_MARCH + 0.5, t)) * behind * (0.75 + 0.25 * twinkle(t))
            if t >= T_MARCH:
                v = t - T_MARCH
                ab = np.abs(pdp - KEEL)
                beat = np.exp(-((t + 1e-6) % BEAT) / 0.12)
                down = np.exp(-((t + 1e-6) % BAR) / 0.25)
                if t < 78:                  # stripes run out from the keel, one wavelength a beat
                    st = (0.5 + 0.5 * np.cos(2 * np.pi * (ab / 200 - v / BEAT))) ** 3
                    buf += light(GOLD, (0.6 + 0.3 * beat) * st)
                    buf += light(WARM, 0.6 * down * np.exp(-(ab / 120) ** 2))
                elif t < 84:                # the wings answer each other on the half bars, stripes running inward
                    half = int(((t - 78) % BAR) / (BAR / 2))
                    mine = (pdp < KEEL) if half == 0 else (pdp >= KEEL)
                    st = (0.5 + 0.5 * np.cos(2 * np.pi * (ab / 160 + v / BEAT))) ** 3
                    colw = AMBER if half == 0 else GOLD
                    buf += light(colw, (0.45 + 0.4 * beat) * st * mine)
                    buf += light(GOLD, 0.25 * st * ~mine)
                    buf += light(CRANBERRY, 0.3 * beat * mine * LW * (half == 0))
                else:                       # the build: stripes tighten and quicken into the last chord
                    w = lerp(200, 60, smoothstep(84, T_FINAL, t))
                    st = (0.5 + 0.5 * np.cos(2 * np.pi * (ab / w - v / BEAT * 200 / w * 0.5))) ** 3
                    buf += light(GOLD, (0.5 + 0.3 * smoothstep(84, T_FINAL, t)) * st * (t < T_FINAL))
                if t >= T_FINAL:            # the last chord: the whole house in gold, a ring out from the keel
                    w2 = t - T_FINAL
                    buf += light(WARM, 0.8 * np.exp(-w2 / 0.35))
                    buf += light(WHITE, 0.6 * np.exp(-((ab - 1200 * w2) / 60) ** 2) * np.exp(-w2 / 0.8))
                    glow = glow * (1 + 0.6 * np.exp(-w2 / 1.5))
                    buf += light(GOLD, 0.5 * np.exp(-w2 / 2.0) * fade)
            buf += light(GOLD, glow * fade)
            # cranberry's half still sulks at the back of Side, its ember warming a little in the gold
        out[f][G.path] = buf
    return np.clip(out, 0, 1, out=out)


# ---------------------------------------------------------------- music ----------------------------------------------
# A tug-of-war polka in F, 120 to the minute and four to the bar, on the same beat that pulses the lights. A fiddle
# plays the tune over tuba and banjo oom-pah; a horn heaves with every rise in the tension, tremolo violins climb
# with it, a snare drives the rounds and each creak is a woodblock where it happens. The slip is a slide whistle
# up the right wing and a whoosh and a thump out to the back of the house; round two jumps up to G. Each near-snap
# cuts the band dead for its frozen beat. The snap is a slapstick and a crash, the two halves whoosh to the ends
# (a sad trombone where cranberry lands, a harp and glockenspiel where gold lands), the wish sweeps back on a harp
# glissando, and the tune marches home on trumpets and horn to a last full chord.

CH = {'F': (53, 57, 60), 'Bb': (53, 58, 62), 'C7': (52, 55, 58), 'Gm': (55, 58, 62), 'Dm': (53, 57, 62),
      'C': (52, 55, 60)}
ROOT = {'F': (41, 48), 'Bb': (46, 41), 'C7': (36, 43), 'Gm': (43, 38), 'Dm': (38, 45), 'C': (36, 43)}
TUNE = [(0, 'C5', 1), (1, 'A4', .5), (1.5, 'C5', .5), (2, 'F5', 1), (3, 'C5', 1),
        (4, 'D5', 1), (5, 'C5', .5), (5.5, 'A4', .5), (6, 'G4', 2),
        (8, 'Bb4', 1), (9, 'A4', .5), (9.5, 'Bb4', .5), (10, 'D5', 1), (11, 'Bb4', 1),
        (12, 'A4', 1), (13, 'G4', .5), (13.5, 'A4', .5), (14, 'F4', 2),
        (16, 'C5', 1), (17, 'A4', .5), (17.5, 'C5', .5), (18, 'F5', 1), (19, 'E5', .5), (19.5, 'F5', .5),
        (20, 'G5', 1), (21, 'F5', .5), (21.5, 'E5', .5), (22, 'D5', 2),
        (24, 'C5', .5), (24.5, 'D5', .5), (25, 'C5', .5), (25.5, 'A4', .5), (26, 'Bb4', 1), (27, 'G4', 1),
        (28, 'F4', 2), (30, 'C4', 1), (31, 'F4', 1)]
HALVES = ['F', 'F', 'C7', 'C7', 'Bb', 'Bb', 'F', 'F', 'F', 'F', 'C7', 'C7', 'F', 'C7', 'F', 'F']


def score(M, G):
    from pixelhome.audio import SR, note, slide, whoosh
    n = note
    fid = M.sampler('Strings/Solo Violin/spic/*.wav', tune=-12)
    banjo = M.sampler('Strings/Solo Violin/Pizz/*.wav')
    tuba = M.sampler('Brass/Tuba/stac/*.wav', tune=-12)
    horn = M.sampler('Brass/F Horn/sus/*.wav', tune=-12)
    hstab = M.sampler('Brass/F Horn/stac/*.wav', tune=-12)
    tpt = M.sampler('Brass/Trumpet/stac/*.wav', tune=-12)
    tpt_s = M.sampler('Brass/Trumpet/sus/*.wav', tune=-12)
    tbn = M.sampler('Brass/Tenor Trombone/sus/*.wav', tune=-12)
    fall = M.sampler('Brass/OldTrombone/Fall/*.wav', tune=-12)
    clar = M.sampler('Woodwinds/Clarinet/stac/*.wav', tune=-12)
    bsn = M.sampler('Woodwinds/Bassoon/stac/*.wav', tune=-12)
    trem = M.sampler('Strings/Violin Section/Trem/*.wav', tune=-12)
    cello = M.sampler('Strings/Cello Section/susvib/*.wav', tune=-12)
    harp = M.sampler('Strings/Harp/*.wav')
    xylo = M.sampler('Percussion/Xylo/*.wav', tune=-12)
    glock = M.sampler('Percussion/Glock/*.wav', tune=-12)
    mar = M.sampler('Percussion/Marimba/*.wav', tune=-12)
    wood = M.hits('VSCO 1 Percussion/varWood/wood_click*.wav')
    clave = M.hits('Percussion/Claves1_Hit*.wav')
    slap = M.hits('VSCO 1 Percussion/varWood/slapstick[0-9].wav')
    guiro = M.hits('VSCO 1 Percussion/varWood/guiro_short*.wav')
    snare = M.hits('Percussion/Snare2-HitSN*.wav')
    sroll = M.hits('Percussion/Snare2-rollSN*.wav')
    crash = M.hits('Percussion/cymbal-crash1_f*.wav')
    cswell = M.hits('Percussion/susCymb1-cresc-Short*.wav')
    bd = M.hits('Percussion/BDrumNewhit_v[4-7]*.wav')
    timp = M.hits('Percussion/Timpani/Timpani1_Hit*.wav')
    troll = M.hits('Percussion/Timpani/Rolls/*.wav')
    ratchet = M.hits('Percussion/Ratchet1-Fast*.wav')

    for name, gain, rev in (('tune', 0.5, 0.2), ('brass', 0.4, 0.22), ('bass', 0.6, 0.08), ('banjo', 0.7, 0.12),
                            ('strings', 0.3, 0.3), ('harp', 0.4, 0.3), ('mallet', 0.42, 0.2), ('perc', 0.6, 0.12),
                            ('drums', 0.62, 0.15), ('crack', 1.1, 0.12), ('fx', 0.28, 0.25)):
        M.bus(name, gain=0.62 * gain, reverb=rev)

    order = np.argsort(G.pd)
    xs, ds = G.pos[order, 0], G.pd[order]
    x0, x1 = xs.min(), xs.max()

    def pan_at(d):
        x = np.interp(d, ds, xs)
        return float(0.85 * (2 * (x - x0) / (x1 - x0) - 1))

    def travel(sig, d0, d1):
        a = (np.linspace(pan_at(d0), pan_at(d1), sig.shape[1]) + 1) * np.pi / 4
        return sig * np.sqrt(2) * np.vstack([np.cos(a), np.sin(a)])

    gl, gr, keel = pan_at(G0), pan_at(G1), pan_at(KEEL)

    def tune(t0, inst, bus, vel, shift=0, gain=1.0, pan=0.0, upto=32, legato=0.9):
        for b, m, ln in TUNE:
            if b < upto:
                M.add(bus, inst.play(n(m) + shift, vel, dur=ln * BEAT * legato, release=0.12), t0 + b * BEAT, gain, pan)

    def oompah(t0, t1, shift=0, vel=90, snare_on=True, cut=()):
        k = 0
        while t0 + k * BEAT < t1 - 1e-6:
            t = t0 + k * BEAT
            if any(c <= t < c + 1.0 for c in cut):
                k += 1
                continue
            c = HALVES[(k // 2) % 16]
            if k % 2 == 0:
                M.add('bass', tuba.play(ROOT[c][(k // 2) % 2] + shift, vel + 10), t, 1.0, -0.1)
                M.add('drums', bd.play(vel - 10), t, 0.5)
            else:
                for m in CH[c]:
                    M.add('banjo', banjo.play(m + 12 + shift, vel - 5), t, 0.6, 0.15)
                if snare_on:
                    M.add('drums', snare.play(vel - 20), t, 0.45, 0.05)
            k += 1

    # ---- the bone draws itself, gold comes in, cranberry pops up, they size each other up ----
    for i in range(10):
        for sgn in (-1, 1):
            M.add('harp', harp.play([53, 57, 60, 65, 69, 72, 77, 81, 84, 89][i], 70 + 3 * i), T_IN[0] + 0.18 * i,
                  0.6, pan_at(KEEL + sgn * 59 * i))
    M.add('fx', travel(slide(0.0, 1.4, 500, 1300, 1.5, 0.5), END, G1), T_IN[1], 1.0)
    for i, m in enumerate(('C5', 'D5', 'E5', 'F5', 'G5', 'A5', 'C6')):
        M.add('mallet', xylo.play(n(m), 90), T_IN[1] + 0.2 * i, 0.8, pan_at(END - 479 * i / 6))
    M.add('bass', tuba.play(n('F1'), 115), T_IN[2], 1.0, gl)
    M.add('perc', slap.play(110), T_IN[2], 0.8, gl)
    for i, m in enumerate(('F4', 'A4', 'C5', 'F5')):
        M.add('tune', clar.play(n(m), 95), T_IN[2] + 0.12 * i, 0.9, pan_at(G0 - 220 * i))
    oompah(4.0, COUNT1[0], vel=78, snare_on=False)
    tune(2.0, clar, 'tune', 70, upto=8)
    for k in range(6):                      # sizing up: cranberry, gold, cranberry, gold
        t = 7.0 + k * BEAT
        M.add('brass', hstab.play(n('C4') + (0 if k % 2 == 0 else 7), 100), t, 0.9, gl if k % 2 == 0 else gr)

    # ---- the countdowns and the pulls ----
    def countdown(times, notes):
        for i, (tc, m) in enumerate(zip(times, notes)):
            for p in (gl, gr):
                M.add('perc', clave.play(100 + 8 * i), tc, 1.0, p)
            M.add('mallet', mar.play(n(m), 108 + 6 * i), tc, 1.0, keel)
            M.add('drums', timp.play(90 + 10 * i, pitch=2 * i), tc, 0.7)

    countdown(COUNT1, ('C4', 'D4', 'E4', 'F4'))
    countdown(COUNT2, ('D4', 'E4', 'F#4', 'G4'))
    M.add('drums', sroll.play(70, dur=2.0), COUNT2[0] - 2.0, 0.5)

    def pull_hit(t, shift):
        M.add('drums', crash.play(118), t, 0.8)
        M.add('drums', bd.play(124), t, 1.0)
        M.add('bass', tuba.play(41 + shift - 12, 120), t, 1.0)
        for m in CH['F']:
            M.add('brass', hstab.play(m + shift, 115), t, 0.9)

    pull_hit(T_PULL1, 0)
    oompah(T_PULL1, T_SLIP, vel=96)
    tune(T_PULL1, fid, 'tune', 100)
    pull_hit(T_PULL2, 2)
    oompah(T_PULL2, T_STILL, shift=2, vel=104, cut=[n_ + 0.5 for n_ in NEAR])
    tune(T_PULL2, fid, 'tune', 108, shift=2)
    tune(T_PULL2 + 16, fid, 'tune', 112, shift=2, upto=26)
    tune(T_PULL2 + 16, tpt, 'brass', 100, shift=2 - 12, upto=26, gain=0.7)
    M.add('drums', sroll.play(80, dur=T_STILL - 55), 55.0, 0.5)

    # tremolo violins climb with the tension, a bar at a time; a horn heaves on every rise
    for t in np.arange(T_PULL1, T_STILL, BAR):
        if T_SLIP <= t < T_PULL2:
            continue
        Tm = float(keys(t + 1, T_KEYS))
        shift = 2 if t >= T_PULL2 else 0
        m = 60 + shift + int(round(10 * min(Tm, 1.1)))
        cut = min([c + 0.5 for c in NEAR if c + 0.5 > t] + [T_STILL, T_SLIP if t < T_SLIP else 1e9])
        dur = min(BAR, cut - t)
        M.add('strings', trem.play(m, int(55 + 50 * min(Tm, 1)), dur=dur, release=0.05), t, 1.0, keel)
        M.add('strings', trem.play(m - 5, int(50 + 45 * min(Tm, 1)), dur=dur, release=0.05), t, 0.7, keel)
    for t in np.arange(T_PULL1, T_STILL, BEAT * 2):
        if T_SLIP <= t < T_PULL2 or any(c + 0.5 <= t < c + 1.0 for c in NEAR):
            continue
        x0_, x1_ = keys(t, X_KEYS), keys(t + 1, X_KEYS)
        p = float(np.clip((x1_ - x0_) / 100, -0.7, 0.7))
        if abs(x1_ - x0_) > 40:              # a heave toward whoever is pulling: a horn grunt on that side
            M.add('brass', horn.play(n('F3') + (2 if t >= T_PULL2 else 0) + (7 if x1_ > x0_ else 0),
                                     int(70 + 40 * min(1, keys(t, T_KEYS))), dur=0.8, release=0.1), t, 0.8, p)

    # every creak where it happens: a woodblock, and a ratchet for the louder ones
    for tc, sc, a in creaks():
        p = pan_at(sc + keys(tc, X_KEYS))
        M.add('perc', wood.play(int(60 + 50 * a)), tc, 0.8, p)
        if a > 0.85:
            M.add('perc', guiro.play(int(70 + 40 * a)), tc, 0.4, p)

    # near-snaps: a crack and a crash, then the whole band stops dead for the frozen beat
    for tn in NEAR:
        M.add('perc', ratchet.play(110, dur=0.5), tn, 0.7, pan_at(FLAW))
        M.add('drums', cswell.play(90, dur=0.5), tn, 0.6, pan_at(FLAW))
        M.add('perc', slap.play(100), tn + 0.45, 0.7, pan_at(FLAW))
        M.add('drums', timp.play(110, pitch=-2), tn + 1.0, 0.7)
        M.add('brass', tbn.play(n('A2') if tn == NEAR[0] else n('C3'), 90, dur=0.9, release=0.2), tn + 1.0, 0.8)

    # the slip: gold's grip slides out the right wing, cranberry falls over to the back of the house
    M.add('fx', travel(slide(0.0, 0.5, 900, 2000, 0.6), G1, END), T_SLIP, 1.2)
    M.add('perc', guiro.play(127), T_SLIP, 1.2, gr)
    M.add('fx', travel(whoosh(893 / JOLT, 2500, 300, 0.7, seed=5), G0, 0), T_SLIP, 1.4)
    th = T_SLIP + 893 / JOLT
    M.add('drums', bd.play(127), th, 1.0, -0.85)
    M.add('drums', timp.play(118, pitch=-3), th, 0.8, -0.85)
    M.add('perc', slap.play(115), th, 0.9, -0.85)
    M.add('bass', tuba.play(n('F1'), 118), th, 1.0, -0.6)
    for i, (ta, tb) in enumerate(((T_SLIP + 0.25, T_SLIP + 0.6), (T_SLIP + 0.6, T_SLIP + 0.95), (T_SLIP + 0.95, T_SLIP + 1.4))):
        M.add('fx', slide(0.0, tb - ta, 500 if i % 2 else 820, 820 if i % 2 else 520, tb - ta, 0.4), ta, 0.7, gl)
    for k in range(4):                      # gets up and grumbles on the beats
        M.add('tune', bsn.play(n(('C3', 'Bb2', 'A2', 'F2')[k]), 100), T_SLIP + 2 + k * BEAT, 0.9, gl)
    for i, m in enumerate(('C5', 'A4')):    # gold: tsk tsk
        M.add('banjo', banjo.play(n(m), 90), T_SLIP + 3.5 + i * 0.25, 1.0, gr)
    M.add('fx', travel(slide(0.0, 0.6, 1300, 600, 0.65), END, G1), T_SLIP + 4, 1.0)     # the regrip
    M.add('bass', tuba.play(n('F1'), 110), T_SLIP + 4.5, 1.0, gl)

    # the stillness: nothing but a tiny creak; then the SNAP
    M.add('perc', wood.play(50), T_STILL + 0.5, 0.5, pan_at(FLAW))
    pf = pan_at(FLAW + 100)
    M.add('perc', slap.play(127), T_SNAP, 1.0, pf)
    k = np.arange(int(0.06 * SR))
    crack = np.diff(M.rng.normal(0, 1, len(k) + 1)) * np.exp(-k / (0.01 * SR))
    M.add('crack', np.vstack([crack, crack]) * 0.6, T_SNAP, 1.0, pf)
    M.add('drums', crash.play(127), T_SNAP, 1.0, pf)
    M.add('drums', bd.play(127), T_SNAP, 1.0, pf)
    M.add('drums', timp.play(124, pitch=-2), T_SNAP, 0.9, pf)
    M.add('bass', tuba.play(n('G1'), 124), T_SNAP, 1.0)
    for m in (55, 59, 62, 67):
        M.add('brass', hstab.play(m, 124), T_SNAP, 1.0, pf)
    for k in range(10):
        M.add('mallet', xylo.play(n('G6') - 2 * k, 112 - 4 * k), T_SNAP + 0.04 * k, 0.7, pan_at(FLAW + (-1) ** k * 80 * k))
    M.add('fx', travel(whoosh(FLY_L, 3000, 400, 0.9, seed=11), FLAW, 0), T_SNAP, 1.2)
    M.add('fx', travel(slide(0.0, FLY_L, 1100, 380, FLY_L, 0.45), FLAW, 0), T_SNAP, 0.8)
    M.add('fx', travel(whoosh(FLY_R, 300, 3200, 0.9, seed=12), FLAW, END), T_SNAP, 1.2)
    M.add('fx', travel(slide(0.0, FLY_R, 500, 1500, FLY_R, 0.45), FLAW, END), T_SNAP, 0.8)
    tl, tg = T_SNAP + FLY_L, T_SNAP + FLY_R
    M.add('drums', bd.play(110), tl, 0.8, -0.85)
    M.add('brass', fall.play(n('D3'), 105), tl + 0.3, 0.9, -0.8)                       # cranberry sulks
    M.add('drums', crash.play(110), tg, 0.7, 0.85)
    M.add('mallet', glock.play(n('G5'), 110), tg, 1.0, 0.85)
    for i in range(12):
        M.add('harp', harp.play([67, 71, 74, 79, 83, 86][i % 6] - 12 + 12 * (i // 6), 90), tg + 0.05 * i, 0.7, 0.85)
    for k in range(int((T_WISH - tg) / BEAT) + 1):    # gold throbs at the end on the beats
        t = np.ceil(tg / BEAT) * BEAT + k * BEAT
        if t < T_WISH:
            M.add('mallet', glock.play(n('D5') + (5 if k % 2 else 0), 80 + 4 * k), t, 0.7, 0.85)
    M.add('drums', troll.play(80, dur=T_WISH - tg), tg, 0.6, 0.6)

    # the wish sweeps back over the whole house on a harp glissando
    gl_notes = [m for m in range(n('G3'), n('G6')) if m % 12 in (7, 9, 11, 0, 2, 4, 6)]
    for i, m in enumerate(gl_notes):
        u = i / (len(gl_notes) - 1)
        M.add('harp', harp.play(m, 88), T_WISH + u * (T_MARCH - T_WISH - 0.1), 0.6, pan_at(END * (1 - u)))
    M.add('drums', cswell.play(100, dur=T_MARCH - T_WISH), T_WISH, 0.6)

    # the march: the tune on trumpets and horn in G, the wings answering, a build, the last chord
    pull_hit(T_MARCH, 2)
    oompah(T_MARCH, T_FINAL, shift=2, vel=108)
    tune(T_MARCH, tpt_s, 'brass', 108, shift=2 - 12, gain=0.9, legato=0.85)
    tune(T_MARCH, fid, 'tune', 100, shift=2, upto=16)
    tune(T_MARCH, horn, 'brass', 96, shift=2 - 24, gain=0.6, legato=0.85)
    for k in range(12):                     # 78-84: the wings answer each other, left (amber) then right (gold)
        t = 78 + k * (BAR / 2)
        left = k % 2 == 0
        M.add('banjo' if left else 'mallet', (clar if left else xylo).play(n('B4') if left else n('D5'), 100),
              t, 0.8, -0.6 if left else 0.6)
    for k in range(int((T_FINAL - T_MARCH) / BAR)):
        M.add('mallet', glock.play(n('D5') + (0, 5, 7, 12)[k % 4], 90), T_MARCH + k * BAR, 0.6, keel)
    M.add('drums', troll.play(100, dur=2.0), 84.0, 0.7)
    tf = T_FINAL
    pull_hit(tf, 2)
    hold = D - tf - 1.2
    for m, inst, bus, v in ((n('G2'), cello, 'strings', 90), (n('D3'), cello, 'strings', 84),
                            (n('B3'), horn, 'brass', 96), (n('G4'), tpt_s, 'brass', 96), (n('D4'), horn, 'brass', 90)):
        M.add(bus, inst.play(m, v, dur=hold, release=1.5), tf, 1.0)
    for i, m in enumerate(('G2', 'D3', 'G3', 'B3', 'D4', 'G4', 'B4', 'D5')):
        M.add('harp', harp.play(n(m), 92), tf + 0.05 * i, 0.8, -0.8 + 1.6 * i / 7)
    M.add('drums', timp.play(118), tf + 1.0, 0.6)
    M.add('mallet', glock.play(n('G5'), 100), tf, 0.8)
