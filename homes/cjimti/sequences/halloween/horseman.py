"""Sleepy Hollow: Ichabod Crane, a small trembling lantern on a plodding old horse, rides in at the
free back end of Side singing a psalm to keep his courage up. Hoofbeats come from behind before
anything is seen; he freezes, a far horn sounds, he hurries on round the front-left corner. Then the
Headless Horseman bursts out of the back of the house: a violet horse with a flaming pumpkin for a
head, hooves striking blue sparks that leave ember hoofprints. He rears at the front-left corner in
full view of the street and gives chase. Ichabod bolts for the church bridge (the porch notch, laid
with faint planks), and the Horseman, who can't cross it, skids to a halt at its foot, stamps,
rears again and paws at the planks, which flash him back. Ichabod comes out on the far bank (the
right wing) and dares to look back; the Horseman rises in his stirrups, whirls the pumpkin and
hurls it straight across the open front of the notch. It smashes on Ichabod in a burst of fire and
scatters into embers along the right wing; his lantern is flung off the end of the house. The
headless rider, now only a ghost-blue outline and sparks, rears and gallops off into the dark the
way he came. The embers smoulder in the wind, then a small lantern peeks back in at the right end:
Ichabod survived, sees the mess and flees. Far away at the back of the house, a new pumpkin lights
up, grins, laughs and goes out.

Everything lives in path distance (layout units along the roofline) except the thrown pumpkin and
the smash, which are point lights in 3-D (so the flight across the empty notch reads as a glow
leaving one corner, lighting the back of the porch as it passes and landing on the other). Both
riders follow eased legs (`_trap`); every hoof strike, rear, stamp and paw is in `_plan`, which
the score uses too. The music runs in 6/8 at a dotted quarter of 0.6 s: one gallop stride."""
import numpy as np
from pixelhome.fx import DT, hexc, light, smoothstep, keys, nframes, colormap

CODE = 'HW06'
TITLE = 'Sleepy Hollow'
KIND = 'show'
DESCRIPTION = ('Ichabod Crane rides in singing, until hoofbeats come from behind and the Headless '
               'Horseman bursts out with a flaming pumpkin for a head. Ichabod races across the '
               'bridge where the rider can\'t follow, so the Horseman hurls his head after him.')
VOICEOVER = 'A lonely road, a nervous rider, and hoofbeats where there should be none. Ride, Ichabod. Ride for the bridge.'

MIST = hexc('#1f6a74')
WOOD = hexc('#c88a4a')
HOLY = hexc('#bcd2ff')
LANTERN = hexc('#ffc050')
POOL = hexc('#ff8a20')
NAG = hexc('#9a8a70')
HORSE = hexc('#5a14c8')
GHOST = hexc('#3a64ff')
PUMPKIN = hexc('#ff6400')
SPARK = hexc('#d6e6ff')
PRINT = hexc('#ff2a08')
BURST = hexc('#ffd890')
BLOOD = hexc('#ff1000')
FLAME = colormap([(0.0, hexc('#ffc020')), (0.35, hexc('#ff6000')), (0.75, hexc('#e01800')), (1.0, hexc('#600000'))])

B = 1.2                       # one bar of 6/8
STRIDE = 0.6                  # one gallop stride = one dotted quarter
CANTER = (0.0, 0.1, 0.2)      # hoof strikes in a stride: ba-da-DUM
LEGS = (-34.0, 2.0, 40.0)     # where each of those hooves lands, along the body from the rider
WEIGHT = (0.75, 0.8, 1.0)

TI0 = 2.4                     # Ichabod rides in, singing
TF = 8.4                      # hoofbeats far behind; he freezes
TW = 10.8                     # he rides on, faster
TQ = 12.0                     # a far horn
TH = 16.8                     # the Horseman bursts in at the back of Side
TR1 = 19.2                    # rears at the front-left corner
TG2 = 21.6                    # gallops for the bridge
TK = 22.8                     # skids to a halt at its foot
TR2 = 24.0                    # rears in a rage
TA = 26.4                     # Ichabod reaches the far bank
TU = 28.8                     # the Horseman rises in his stirrups and whirls the pumpkin
TT = 32.4                     # hurls it
TS = 33.6                     # it smashes
TR3 = 35.4                    # the headless horse rears
TG3 = 37.2                    # gallops off into the dark
TP = 48.0                     # a lantern peeks back in at the right end
TE = 52.8                     # Ichabod sees the mess and flees
TZ = 55.2                     # a new head lights up far away
D = 61.2

REARS = [(TR1, TG2), (TR2, TR2 + 2.4), (TR3, TR3 + 1.2)]
STAMPS = (23.3, 23.6)
PAWS = (27.0, 27.6, 28.2)
GUSTS = (42.0, 45.6)
STARTLES = ((TQ + 0.05, 0.5), (TR1 + 0.2, 1.0), (TE, 1.0))


def _trap(u, a, b):
    """Eased travel 0..1: speed ramps up over the first a, cruises, ramps down over the last b."""
    u = min(max(u, 0.0), 1.0)
    vm = 1.0 / (1 - a / 2 - b / 2)
    if a > 0 and u < a:
        return vm * u * u / (2 * a)
    if b > 0 and u > 1 - b:
        return 1 - vm * (1 - u) ** 2 / (2 * b)
    return vm * (a / 2 + (u - a))


def _track(t, legs):
    """Position along legs [(t0, t1, d0, d1, ease_in, ease_out)], holding still between them."""
    pos = legs[0][2]
    for t0, t1, d0, d1, a, b in legs:
        if t < t0:
            return pos
        if t <= t1:
            return d0 + (d1 - d0) * _trap((t - t0) / (t1 - t0), a, b)
        pos = d1
    return pos


def _plan(G):
    """Both riders' legs and every hoof strike, shared by render() and score()."""
    pdp = G.pd[G.path]
    L = float(G.length)
    corner = lambda i: float(0.5 * (pdp[i] + pdp[i + 1]))
    C1, C2, C5 = corner(80), corner(178), corner(380)       # front-left corner, foot of the bridge, far bank
    HK = C2 - 30                                            # where the Horseman pulls up
    H = [(TH, TR1, -70.0, C1 - 14, 0.0, 0.35), (TG2, TK, C1 - 14, HK, 0.2, 0.3), (TG3, TG3 + 3.6, HK, -90.0, 0.15, 0.0)]
    I = [(TI0, TF + 0.3, -20.0, 255.0, 0.05, 0.12), (TW, TH + 1.2, 255.0, 790.0, 0.25, 0.1),
         (TR1 + 0.8, TA, 790.0, C5 + 50, 0.08, 0.15), (TU + 2.4, TS, C5 + 50, C5 + 115, 0.3, 0.0),
         (TP, TP + 2.4, L + 25, L - 150, 0.0, 0.3), (TE, TE + 1.0, L - 150, L + 60, 0.25, 0.0)]
    gaits = [0.3, 0.3, None, 0.2, 0.4, 0.1]                # walk, walk, canter, trot, creep, scurry
    hx = lambda t: _track(t, H)
    ix = lambda t: _track(t, I)

    strikes = []                                           # (t, d, strength, kind)
    for m in range(int(np.ceil(TF / STRIDE)), int(round(TH / STRIDE))):    # far off, coming closer
        for o, k in zip(CANTER, WEIGHT):
            t = m * STRIDE + o
            u = (t - TF) / (TH - TF)
            strikes.append((t, -70 - 1600 * (1 - u), k, 'far'))
    for (t0, t1, d0, d1, a, b), dr in zip(H, (1, 1, -1)):
        for m in range(int(np.floor(t0 / STRIDE)), int(np.ceil(t1 / STRIDE)) + 1):
            for o, leg, k in zip(CANTER, LEGS, WEIGHT):
                t = m * STRIDE + o
                if not (t0 <= t < t1):
                    continue
                v = abs(hx(t + 0.02) - hx(t - 0.02)) / 0.04
                if v > 80:
                    strikes.append((t, hx(t) + dr * leg, k, 'gallop'))
    for m in range(int(np.ceil((TG3 + 3.6) / STRIDE)), int((TG3 + 7.2) / STRIDE)):    # receding
        for o, k in zip(CANTER, WEIGHT):
            t = m * STRIDE + o
            strikes.append((t, -90 - 450 * (t - TG3 - 3.6), k, 'far'))
    x1 = C1 - 14
    strikes += [(TG2, x1 + 40, 1.4, 'slam'), (TG2 + 0.12, x1 + 46, 1.4, 'slam')]
    for t in np.arange(TK - 0.4, TK + 0.01, 0.05):
        strikes.append((float(t), hx(float(t)) - 34, 0.55, 'skid'))
    strikes += [(t, HK + 40 + 4 * i, 1.1, 'stamp') for i, t in enumerate(STAMPS)]
    t2 = REARS[1][1]
    strikes += [(t2, HK + 40, 1.4, 'slam'), (t2 + 0.12, HK + 46, 1.4, 'slam')]
    strikes += [(t, HK + 50, 1.0, 'paw') for t in PAWS]
    t3 = REARS[2][1]
    strikes += [(t3, HK + 40, 1.2, 'slam'), (t3 + 0.12, HK + 46, 1.2, 'slam')]
    strikes.sort()

    hooves = []                                            # Ichabod's: (t, d, gait index)
    for gi, ((t0, t1, d0, d1, a, b), per) in enumerate(zip(I, gaits)):
        if per is None:
            ts = [m * STRIDE + o for m in range(int(t0 / STRIDE), int(t1 / STRIDE) + 1) for o in CANTER]
        else:
            ts = list(np.arange(np.ceil(t0 / per) * per, t1, per))
        for t in ts:
            if t0 <= t < t1 and abs(ix(t + 0.02) - ix(t - 0.02)) / 0.04 > 15:
                hooves.append((float(t), ix(t), gi))
    return dict(L=L, C1=C1, C2=C2, C5=C5, HK=HK, H=H, I=I, hx=hx, ix=ix, strikes=strikes, hooves=hooves)


def _rear(t):
    """0..1: how far up the horse is."""
    for r0, r1 in REARS:
        if r0 - 0.1 <= t <= r1 + 0.1:
            return float(smoothstep(r0, r0 + 0.35, t) * (1 - smoothstep(r1 - 0.25, r1, t)))
    return 0.0


def _dir(t):
    return float(1 - 2 * smoothstep(TR3 + 1.2, TG3, t))


def _swing(t):
    """The pumpkin whirled round before the throw, ending at full stretch forward at TT."""
    if t < TU:
        return 0.0
    u = min((t - TU) / (TT - TU), 1.0)
    ph = (TT - TU) * (0.6 * u + 0.95 * u * u)
    end = (TT - TU) * 1.55
    return (10 + 50 * u) * np.cos(2 * np.pi * (ph - end))


def _shards(rng, n=14):
    sg = np.where(np.arange(n) % 2 == 0, 1.0, -1.0)
    return dict(v=sg * rng.uniform(140, 820, n), w=rng.uniform(3.5, 9.0, n), cool=rng.uniform(5, 14, n),
                ph=rng.uniform(0, 2 * np.pi, n), f=rng.uniform(1.5, 4.0, n))


def render(G, seed=6):
    rng = np.random.default_rng(seed)
    P = _plan(G)
    L, C2, C5, HK = P['L'], P['C2'], P['C5'], P['HK']
    hx, ix = P['hx'], P['ix']
    pdp = G.pd[G.path]
    pos = G.pos[G.path]
    mn = rng.uniform(0, 2 * np.pi, 4)

    def at3(d):
        d = float(np.clip(d, 0, L))
        return np.array([np.interp(d, pdp, pos[:, k]) for k in range(3)])

    def box(c, half, soft=2.5):
        return np.clip((half - np.abs(pdp - c)) / soft + 0.5, 0, 1)

    bridge = (pdp >= C2) & (pdp <= C5)
    planks = bridge * smoothstep(-0.35, 0.1, np.cos(2 * np.pi * (pdp - C2) / 22.0))

    S = np.array([s[:3] for s in P['strikes']])            # t, d, strength
    kinds = [s[3] for s in P['strikes']]
    onroof = np.array([k != 'far' for k in kinds]) & (S[:, 1] >= 0) & (S[:, 1] <= L)
    paw = np.array([k == 'paw' for k in kinds])
    big = np.array([k in ('slam', 'stamp', 'paw') for k in kinds])
    far = np.array([k == 'far' for k in kinds])
    Hv = np.array(P['hooves'])
    onbridge = (Hv[:, 1] >= C2) & (Hv[:, 1] <= C5)

    sh = _shards(rng)
    d_imp = ix(TS)
    p0 = at3(hx(TT) + 12 + _swing(TT))
    p1 = at3(d_imp)

    def pumpkin_at(t):
        u = (t - TT) / (TS - TT)
        p = p0 + (p1 - p0) * u
        p[1] += 120 * 4 * u * (1 - u)
        return p

    F = nframes(D)
    out = np.zeros((F, G.N, 3))
    for fi in range(F):
        t = fi * DT
        buf = np.zeros((G.N, 3))
        env = smoothstep(0, 2.4, t) * (1 - smoothstep(D - 2.4, D - 0.2, t))

        # ---- the hollow: mist, and the bridge's planks ----
        mist = 0.10 + 0.035 * np.sin(pdp / 130 + 0.35 * t + mn[0]) * np.sin(pdp / 57 - 0.22 * t + mn[1])
        for tg in GUSTS:
            if tg <= t < tg + 4:
                g = -200 + 900 * (t - tg)
                mist = mist + 0.05 * np.exp(-((pdp - g) / 160) ** 2)
        holy = 0.0
        if TK - 0.3 <= t < TU + 0.5:                        # the bridge wakes up when he reaches it
            holy = 0.08 * smoothstep(TK - 0.3, TK + 0.4, t) * (1 - smoothstep(TU, TU + 0.5, t))
        Ip = 0.075 * planks
        for tt_, d, gi in Hv[onbridge]:                     # his hooves thump the planks
            if 0 <= t - tt_ < 0.4:
                Ip = Ip + 0.28 * planks * np.exp(-((pdp - d) / 14) ** 2) * np.exp(-(t - tt_) / 0.12)
        Ih = holy * planks * np.exp(-np.clip(pdp - C2, 0, None) / 260)
        for tp in PAWS:                                     # the planks throw his hoof back
            if 0 <= t - tp < 0.8:
                Ih = Ih + 0.6 * planks * np.exp(-np.clip(pdp - C2, 0, None) / 120) * np.exp(-(t - tp) / 0.2)
        buf += light(MIST, mist * env) + light(WOOD, Ip * env) + light(HOLY, Ih)

        # ---- something coming: far hooves and the horn redden the back of the house ----
        Ir = np.zeros(G.N)
        sel = far & (S[:, 0] <= t) & (S[:, 0] > t - 0.5) & (S[:, 1] < 0)
        for ts, d, k in S[sel]:
            Ir += k * 0.32 * np.exp(d / 700) * np.exp(-((pdp) / 110) ** 2) * np.exp(-(t - ts) / 0.12)
        if TQ <= t < TQ + 3.0:
            Ir += 0.30 * np.exp(-(pdp / 170) ** 2) * np.sin(np.pi * (t - TQ) / 3.0) ** 2 * (0.8 + 0.2 * np.sin(2 * np.pi * 1.7 * t))
        if TZ - 0.6 <= t < TZ + 0.6:
            Ir += 0.2 * np.exp(-(pdp / 150) ** 2) * np.sin(np.pi * (t - TZ + 0.6) / 1.2)
        buf += light(BLOOD, Ir)

        # ---- the Horseman ----
        if TH <= t < TG3 + 3.7:
            x = hx(t)
            dr = _dir(t)
            r = _rear(t)
            v = (hx(t + DT) - hx(t - DT)) / (2 * DT)
            headless = t >= TT
            gal = abs(v) > 60
            bob = 4 * np.sin(2 * np.pi * t / STRIDE) if gal else 0.0
            back, front = 62.0, 68.0 - 34 * r
            if t < TR3 + 1.2 or t >= TG3:
                lo, hi = sorted((x - dr * back, x + dr * front)) if abs(dr) > 0.2 else (x - 20, x + 20)
            else:
                lo, hi = sorted((x - abs(dr) * back - 10, x + abs(dr) * front + 10))
            body = np.clip((np.minimum(pdp - lo, hi - pdp)) / 6 + 0.5, 0, 1)
            if not headless:
                pc = x + dr * (12 + bob) + _swing(t)
                lit = 0.24 + 0.2 * np.exp(-((pdp - pc) / 50) ** 2)
                buf += light(HORSE, body * lit)
                fl = 0.88 + 0.08 * np.sin(2 * np.pi * 9.3 * t) + 0.05 * np.sin(2 * np.pi * 14.1 * t + 1)
                fl += 0.25 * r + 0.25 * smoothstep(TU, TT, t)
                buf += light(PUMPKIN, np.minimum(fl, 1.05) * box(pc, 12 + 4 * r))
                spd = abs(v) + (300 * abs(np.cos(2 * np.pi * t * 1.2)) * smoothstep(TU, TT, t))
                Lf = 50 + 0.34 * spd + 50 * r
                s = -np.sign(v if abs(v) > 20 else dr) * (pdp - pc)
                behind = (s > 9) & (s < Lf)
                q = np.clip(s / Lf, 0, 1)
                tongue = 0.75 + 0.25 * np.sin(pdp / 9 - 31 * t) * np.sin(pdp / 4.3 + 17 * t)
                If = behind * 0.95 * (1 - q) ** 1.1 * tongue
                ahead = (np.abs(pdp - pc) < 34) & ~behind
                If = If + ahead * 0.35 * np.exp(-np.abs(pdp - pc) / 8) * tongue
                buf += (If[:, None] ** 2.2) * FLAME(q)
                if TU <= t < TT:                            # the whirl lights the road
                    buf += light(PUMPKIN, 0.25 * smoothstep(TU, TT, t) * np.exp(-((pdp - x) / 110) ** 2))
            else:
                buf += light(GHOST, body * (0.16 + 0.05 * np.sin(2 * np.pi * 0.9 * t + pdp / 30)))

        # ---- hoof sparks and ember hoofprints ----
        sel = onroof & (S[:, 0] <= t) & (S[:, 0] > t - 3.0)
        if sel.any():
            ts, ds, ks = S[sel, 0], S[sel, 1], S[sel, 2]
            age = t - ts
            g = np.exp(-((pdp[:, None] - ds[None]) / 5.0) ** 2)
            Is = (g * (ks * 0.95 * np.exp(-age / 0.07))).sum(1)
            Ipr = (g * (ks * 0.3 * np.exp(-age / 1.1) * (age > 0.05))).sum(1)
            for ts_, d_, k_ in S[sel & big]:            # spray from the big ones
                a = t - ts_
                if a < 0.35:
                    for sv in (-1, 1):
                        for spd in (180, 330):
                            Is += 0.45 * k_ * np.exp(-a / 0.12) * np.exp(-((pdp - d_ - sv * spd * a) / 4) ** 2)
            buf += light(SPARK, np.minimum(Is, 1.0)) + light(PRINT, np.minimum(Ipr, 0.45))

        # ---- Ichabod ----
        alive = (TI0 <= t < TS) or (TP <= t < TE + 1.1)
        if alive:
            d = ix(t)
            if -12 < d < L + 12:
                trem = 0.0
                trem = max(trem, smoothstep(TF + 0.2, TF + 0.5, t) * (1 - smoothstep(TW - 0.3, TW, t)))
                trem = max(trem, 0.7 * smoothstep(TH + 1.2, TH + 1.5, t) * (1 - smoothstep(TR1 + 0.8, TR1 + 1.2, t)))
                trem = max(trem, smoothstep(TU + 1.6, TU + 2.0, t) * (1 - smoothstep(TS - 0.1, TS, t)))
                trem = max(trem, 0.8 * smoothstep(TP, TP + 0.5, t))
                look = 0.0
                for a0, a1 in ((TF + 0.3, TW - 0.6), (TH + 1.2, TR1 + 0.8), (TA + 1.2, TU + 2.4), (TP + 2.4, TE)):
                    look = max(look, smoothstep(a0, a0 + 0.3, t) * (1 - smoothstep(a1 - 0.2, a1, t)))
                jit = trem * (2.5 * np.sin(2 * np.pi * 11 * t) + 1.5 * np.sin(2 * np.pi * 17 * t + 2))
                dl = d + 6 - 14 * look + jit
                fl = 0.62 + 0.07 * np.sin(2 * np.pi * 6.1 * t) + 0.05 * np.sin(2 * np.pi * 2.3 * t) - 0.1 * trem * (np.sin(2 * np.pi * 13 * t) > 0.3)
                for t0, k in STARTLES:
                    if t0 <= t < t0 + 0.6:
                        fl += 0.38 * k * np.exp(-(t - t0) / 0.15)
                if TA <= t < TA + 1.2:                       # made it: a sigh of relief
                    fl += 0.12 * np.sin(np.pi * (t - TA) / 1.2)
                buf += light(NAG, 0.12 * box(d - 8, 26, 4))
                buf += light(POOL, 0.3 * np.exp(-((pdp - dl) / 34) ** 2))
                buf += light(LANTERN, min(fl, 1.0) * box(dl, 6.5, 2.0))
        if TS <= t < TS + 0.8:                               # his lantern, flung off the end of the house
            dl = d_imp + 900 * 0.45 * (1 - np.exp(-(t - TS) / 0.45))
            buf += light(LANTERN, 0.6 * box(dl, 4, 2))

        # ---- the throw, the smash, the embers ----
        if TT <= t < TS:
            u = (t - TT) / (TS - TT)
            for j, lag in enumerate((0.0, 0.04, 0.08, 0.12, 0.16)):
                if t - lag < TT:
                    continue
                pp = pumpkin_at(t - lag)
                d3 = np.linalg.norm(pos - pp, axis=1)
                k = (1.0, 0.6, 0.4, 0.26, 0.16)[j]
                core = k * np.exp(-(d3 / 48) ** 2)
                if j == 0:
                    buf += light(PUMPKIN, 0.95 * core + 0.32 / (1 + (d3 / 170) ** 2))
                else:
                    buf += light(FLAME(0.3 + 0.12 * j), core)
        if TS <= t < TS + 2.0:
            a = t - TS
            d3 = np.linalg.norm(pos - p1, axis=1)
            Ib = np.exp(-a / 0.16) / (1 + (d3 / 170) ** 2)
            ring = 0.55 * np.exp(-a / 0.35) * np.exp(-((np.abs(pdp - d_imp) - 750 * a) / 30) ** 2)
            buf += light(BURST, np.minimum(Ib, 1.0)) + light(PUMPKIN, ring)
            buf += light(FLAME(0.25 + 0.5 * a), 0.8 * np.exp(-a / 0.9) * np.exp(-((pdp - d_imp) / 40) ** 2) * (0.8 + 0.2 * np.sin(pdp / 5 + 29 * t)))
        if t >= TS:
            a = t - TS
            xs = d_imp + sh['v'] * 0.45 * (1 - np.exp(-a / 0.45))
            heat = np.exp(-a / sh['cool'])
            for tg in GUSTS:
                if tg <= t < tg + 4:
                    g = -200 + 900 * (t - tg)
                    heat = heat * (1 + 0.6 * np.exp(-((xs - g) / 180) ** 2))
            if t >= TE:                                       # last glow goes as the night closes in
                heat = heat * (1 - smoothstep(TZ + 2, D - 1, t))
            flick = 0.85 + 0.15 * np.sin(sh['f'] * 2 * np.pi * t + sh['ph'])
            ok = (xs > -10) & (xs < L + 10)
            for j in np.nonzero(ok)[0]:
                h = float(heat[j])
                c = FLAME(float(np.clip(1.05 - h, 0.05, 0.98)))
                Ie = (0.12 + 0.68 * h) * flick[j] * box(xs[j], sh['w'][j], 2.0)
                buf += (Ie[:, None] ** 2.2) * c

        # ---- a new head, far away ----
        if TZ <= t < TZ + 4.5:
            a = t - TZ
            pz = 30.0
            ign = smoothstep(0, 0.6, a) * (1 - smoothstep(3.6, 3.9, a))
            laugh = 0.0
            if 1.2 <= a < 3.0:
                laugh = 0.18 * np.exp(-((a - 1.2) % 0.2) / 0.06)
            Ik = (0.8 + laugh) * ign * box(pz, 22, 2.5)
            for e in (-9.0, 9.0):                               # eyes
                Ik = Ik * (1 - 0.9 * box(pz + e, 3.2, 1.5))
            buf += light(PUMPKIN, Ik) + light(BLOOD, 0.18 * ign * np.exp(-((pdp - pz) / 70) ** 2))
            if a >= 3.6:
                buf += light(PRINT, 0.3 * np.exp(-(a - 3.6) / 0.5) * box(pz, 10, 2))

        out[fi][G.path] = np.clip(buf, 0, 1)
    return out



# ---------------------------------------------------------------- music ----------------------------------------------
# G minor in 6/8 at the lights' stride (dotted quarter = 0.6 s, bar = 1.2 s). Ichabod is a bassoon singing a psalm in
# G major over plodding pizzicato and wood-block clip-clops; the Horseman is a low horn call, then a cello and bass
# spiccato gallop on his own hoof strikes, with horns on his theme and trombones under it. Every hoof, rear, stamp,
# paw, the whirl, the throw, the smash and each shard comes from _plan() and the constants above; sounds are panned
# to where they happen on the house as seen from the street (path distance -> x).

PSALM = [(0, 'G3', 3), (3, 'B3', 2), (5, 'A3', 1), (6, 'G3', 2), (8, 'E3', 1), (9, 'D3', 3),
         (12, 'G3', 2), (14, 'A3', 1), (15, 'B3', 2), (17, 'C4', 1), (18, 'D4', 2), (20, 'B3', 1), (21, 'A3', 3),
         (24, 'G3', 3), (27, 'B3', 2), (29, 'A3', 1), (30, 'G3', 2), (32, 'F#3', 1), (33, 'G3', 3)]
PSALM_CHORDS = [('G', 'C'), ('G', 'D'), ('G', 'C'), ('D', 'D'), ('G', 'G')]
HORN_CALL = [(0, 'D3', 3), (3, 'G3', 2), (5, 'F3', 1), (6, 'D3', 2), (8, 'Bb2', 1), (9, 'G2', 3)]
THEME = [(0, 'G3', 3), (3, 'Bb3', 2), (5, 'A3', 1), (6, 'G3', 2), (8, 'D3', 1), (9, 'D4', 3),
         (12, 'Eb4', 2), (14, 'D4', 1), (15, 'C4', 2), (17, 'Bb3', 1), (18, 'A3', 3), (21, 'D3', 3)]
TRIADS = {'G': ('G2', 'B2', 'D3'), 'C': ('C3', 'E3', 'G3'), 'D': ('D3', 'F#3', 'A3'),
          'Gm': ('G2', 'Bb2', 'D3'), 'Cm': ('C3', 'Eb3', 'G3'), 'Eb': ('Eb3', 'G3', 'Bb3'), 'Ab': ('Ab2', 'C3', 'Eb3'),
          'D7': ('D3', 'F#3', 'C4'), 'Bb': ('Bb2', 'D3', 'F3')}
ROOTS = {'G': 'G1', 'C': 'C2', 'D': 'D2', 'Gm': 'G1', 'Cm': 'C2', 'Eb': 'Eb2', 'Ab': 'Ab1', 'D7': 'D2', 'Bb': 'Bb1'}
E8 = 0.2                      # an eighth note
THIRD = {'G3': 'B3', 'B3': 'D4', 'A3': 'C4', 'E3': 'G3', 'D3': 'F#3', 'F#3': 'A3', 'C4': 'E4', 'D4': 'F#4'}


def _whinny(seconds, f0, amp=0.3, seed=0, ghost=False):
    """A horse's whinny: a quick rise, then a shaking fall with fast vibrato and a breathy sputter."""
    from pixelhome.audio import SR
    n = int(seconds * SR)
    t = np.arange(n) / SR
    u = t / seconds
    rng = np.random.default_rng(seed)
    contour = f0 * (1 + 0.65 * smoothstep(0, 0.12, u) - 0.75 * smoothstep(0.12, 1.0, u) ** 1.2)
    vib = 1 + (0.03 + 0.09 * smoothstep(0.15, 0.6, u)) * np.sin(2 * np.pi * (9 + 4 * u) * t)
    ph = 2 * np.pi * np.cumsum(contour * vib) / SR
    harm = (1.0, 0.55, 0.4, 0.22, 0.12)
    sig = sum(h * np.sin((k + 1) * ph) for k, h in enumerate(harm)) / 2.3
    noise = np.convolve(rng.normal(0, 1, n), np.ones(12) / 12, 'same')
    sig = sig * (1 + 0.35 * noise) + 0.25 * noise * smoothstep(0.7, 1.0, u)
    env = smoothstep(0, 0.04, t) * (1 - smoothstep(0.55, 1.0, u)) * (0.75 + 0.25 * np.sin(2 * np.pi * 21 * t) ** 2)
    sig = amp * env * sig
    if ghost:                                     # thinned and smeared: the headless horse
        sig = np.convolve(sig, np.ones(8) / 8, 'same') * 0.8
    return np.vstack([sig, sig])


def _muffle(sig, k):
    """Low-pass by two passes of a k-sample box: things far off."""
    if k <= 1:
        return sig
    w = np.ones(int(k)) / int(k)
    return np.vstack([np.convolve(np.convolve(c, w, 'same'), w, 'same') for c in sig])


def score(M, G):
    from pixelhome.audio import note as n, slide, whoosh
    P = _plan(G)
    L, C1, C2, C5, HK = P['L'], P['C1'], P['C2'], P['C5'], P['HK']
    hx, ix = P['hx'], P['ix']

    bsn = M.sampler('Woodwinds/Bassoon/sus/*.wav', tune=-12)
    bsn_st = M.sampler('Woodwinds/Bassoon/stac/*.wav', tune=-12)
    clar = M.sampler('Woodwinds/Clarinet/susLong/*.wav', tune=-12)
    horn = M.sampler('Brass/F Horn/sus/*.wav', tune=-12)
    horn_st = M.sampler('Brass/F Horn/stac/*.wav', tune=-12)
    tbn = M.sampler('Brass/Tenor Trombone/sus/*.wav', tune=-12)
    tbn_st = M.sampler('Brass/Tenor Trombone/stac/*.wav', tune=-12)
    tuba = M.sampler('Brass/Tuba/sus/*.wav', tune=-12)
    spic = M.sampler('Strings/Cello Section/spic/*.wav', tune=-12)
    vspic = M.sampler('Strings/Viola Section/spic/*.wav', tune=-12)
    cbs = M.sampler('Strings/Solo Contrabass/Spic/*.wav', tune=-12)
    pizz = M.sampler('Strings/Cello Section/pizzT/*.wav', tune=-12)
    vtrem = M.sampler('Strings/Violin Section/Trem/*.wav', tune=-12)
    ctrem = M.sampler('Strings/Cello Section/trem/*.wav', tune=-12)
    cello = M.sampler('Strings/Cello Section/susvib/*.wav', tune=-12)
    harp = M.sampler('Strings/Harp/*.wav')
    mar = M.sampler('Percussion/Marimba/*.wav', tune=-12)
    timp = M.hits('Percussion/Timpani/Timpani[45]_Hit_v[34]*.wav')
    timp_s = M.hits('Percussion/Timpani/Timpani[45]_Hit_v1*.wav')
    troll = M.hits('Percussion/Timpani/Rolls/*_v5_*.wav')
    troll_s = M.hits('Percussion/Timpani/Rolls/*_v3_*.wav')
    bd = M.hits('Percussion/BDrumNewhit_v[5-7]*.wav')
    tumba = M.hits('Percussion/Tumba-HitN*.wav')
    tom = M.hits('VSCO 1 Percussion/drums/tenor/tenor_lower/tenor_f*.wav')
    clip = M.hits('Percussion/LogDrumHi*.wav')
    clop = M.hits('Percussion/Quinto-Tap1*.wav')
    plank = M.hits('Percussion/LogDrumLo*.wav')
    crash = M.hits('Percussion/cymbal-crash1_ff*.wav')
    scrape = M.hits('VSCO 1 Percussion/varMetal/Cymbals/susp/susp_FX_scrape_[12].wav')
    swell = M.hits('Percussion/susCymb1-cresc-Short*.wav')
    gong = M.hits('VSCO 1 Percussion/varMetal/Gong/gong_hit_f.wav')
    smash = M.hits('Miscellania Raw/Misc 1/glass_break[2-4].wav')
    slap = M.hits('VSCO 1 Percussion/varWood/slapstick[0-9].wav')
    snare = M.hits('Percussion/Snare2-HitSN_v[35]*.wav')

    for name, gain, rev in (('wind', 0.4, 0.25), ('brass', 0.28, 0.25), ('gallop', 0.24, 0.12), ('bass', 0.44, 0.08),
                            ('strings', 0.3, 0.3), ('hoof', 0.42, 0.15), ('far', 0.6, 0.5), ('drums', 0.46, 0.2),
                            ('fx', 0.32, 0.3), ('pad', 0.16, 0.45), ('organ', 0.2, 0.4), ('harp', 0.24, 0.35)):
        M.bus(name, gain=0.8 * gain, reverb=rev)

    order = np.argsort(G.pd)
    xs_, ds_ = G.pos[order, 0], G.pd[order]
    x0, x1 = xs_.min(), xs_.max()

    def pan_at(d):
        x = np.interp(np.clip(d, 0, L), ds_, xs_)
        return float(0.85 * (2 * (x - x0) / (x1 - x0) - 1))

    def bar(b):
        return b * B

    def chord(t, c, vel=80, inst=None, bus='strings', dur=1.1, g=0.7, pan=-0.2):
        for m in TRIADS[c]:
            M.add(bus, (inst or pizz).play(n(m), vel, dur=dur), t, g, pan)

    pad, organ = [], []

    # ---- 0-8.4: night wind; Ichabod rides in down Side singing his psalm, clip-clop ----
    M.add('fx', whoosh(9.0, 90, 420, 0.5, seed=1), 0.0, 0.5, -0.4)
    M.add('fx', whoosh(7.0, 120, 600, 0.4, seed=2), 6.0, 0.35, 0.3)
    pad += [(0.0, n('G2'), 50, 8.6), (0.0, n('D3'), 44, 8.6)]
    for t, d, gi in P['hooves']:
        on_bridge = C2 <= d <= C5
        k = (int(round(t / 0.1)) % 2) == 0
        inst = plank if on_bridge else (clip if k else clop)
        vel = {0: 70, 1: 78, 2: 96, 3: 74, 4: 56, 5: 92}[gi]
        M.add('hoof', inst.play(vel, pitch=-3 if on_bridge else 0), t, 0.7 if gi < 2 else 0.85, pan_at(d))
    psalm_t0 = TI0 + 0.6
    for e, m, ln in PSALM:
        t = psalm_t0 + e * E8
        if t >= TF + 0.3:                               # he breaks off
            break
        M.add('wind', bsn.play(n(m), 92, dur=ln * E8 * 0.95), t, 1.0, pan_at(ix(t)))
    for b, (c1, c2) in enumerate(PSALM_CHORDS):
        for half, c in enumerate((c1, c2)):
            t = psalm_t0 + b * B + half * B / 2
            if t >= TF:
                break
            M.add('bass', pizz.play(n(ROOTS[c]) + 12, 84), t, 0.8, -0.2)
            chord(t + 0.2, c, 62, dur=0.3, g=0.45)
    M.add('wind', bsn_st.play(n('D3'), 96), TF + 0.3, 0.9, pan_at(ix(TF)))     # gulp
    M.add('wind', bsn_st.play(n('A2'), 90), TF + 0.5, 0.9, pan_at(ix(TF)))

    # ---- far hoofbeats (muffled and from behind the back of the house), getting nearer ----
    far = np.zeros((2, int((TH - TF + 1.5) * 48000)))
    for t, d, k, kind in P['strikes']:
        if kind != 'far' or t > TH:
            continue
        gain = k * 1.0 / (1 + (-d - 70) / 260)
        s = tumba.play(100, pitch=-5)
        i = int((t - TF) * 48000)
        e = min(far.shape[1], i + s.shape[1])
        far[:, i:e] += s[:, :e - i] * gain
    M.add('far', _muffle(far, 18), TF, 0.8, -0.85)

    # ---- 8.4-16.8: the freeze; he rides on, shakier; a far horn at TQ ----
    M.add('strings', ctrem.play(n('G2'), 60, dur=2.4), TF, 0.6, -0.3)
    M.add('strings', vtrem.play(n('D4'), 46, dur=2.2), TF + 0.3, 0.35, 0.2)
    M.add('strings', vtrem.play(n('Eb4'), 46, dur=2.0), TF + 0.5, 0.35, -0.2)
    t1 = TW
    for rep in range(2):                                # the psalm again, quicker in the feet, darker underneath
        for e, m, ln in PSALM[:12]:
            t = t1 + rep * 2.4 * 1.25 + e * E8
            if t >= TH + 1.2 or (TQ - 0.1 <= t < TQ + 1.0):
                continue
            M.add('wind', bsn.play(n(m), 98, dur=ln * E8 * 0.9), t, 1.0, pan_at(ix(t)))
            if rep == 1:
                M.add('wind', clar.play(n(m) + 12, 52, dur=ln * E8 * 0.9), t, 0.5, pan_at(ix(t)))
    for b in range(5):
        t = TW + b * B
        c = ('Gm', 'Cm', 'Gm', 'D', 'Gm')[b]
        M.add('bass', pizz.play(n(ROOTS[c]) + 12, 88), t, 0.8, -0.2)
        M.add('bass', pizz.play(n(ROOTS[c]) + 19, 80), t + 0.6, 0.6, -0.2)
        pad.append((t, n(TRIADS[c][0]), 46, B))
        pad.append((t, n(TRIADS[c][1]), 40, B))
    for e, m, ln in HORN_CALL:                          # far off, from the back of the house
        t = TQ + e * E8
        M.add('far', _muffle(horn.play(n(m), 80, dur=ln * E8 * 1.05), 10), t, 0.75, -0.85)
    M.add('drums', troll_s.play(60, dur=2.0), TQ, 0.35, -0.8)

    # ---- 16.8: he bursts in; the gallop ----
    def gallop(t0, t1, prog, vel=96, low=True):
        """Cello/bass spiccato on the stride: da-da-DUM ... dum; one chord per bar."""
        for m in range(int(round(t0 / STRIDE)), int(round(t1 / STRIDE))):
            t = m * STRIDE
            c = prog[int((t - t0) // B) % len(prog)]
            root = n(TRIADS[c][0])
            for o, dv in zip((0.0, 0.1, 0.2), (-14, -14, 6)):
                M.add('gallop', spic.play(root, vel + dv), t + o, 1.0, -0.25)
            M.add('gallop', spic.play(n(TRIADS[c][2]), vel - 8), t + 0.4, 0.9, -0.25)
            M.add('gallop', vspic.play(n(TRIADS[c][1]) + 12, vel - 20), t + 0.2, 0.5, 0.25)
            M.add('gallop', vspic.play(n(TRIADS[c][2]) + 12, vel - 24), t + 0.4, 0.45, 0.25)
            if low and m % 2 == 0:
                M.add('bass', cbs.play(n(ROOTS[c]) + 12, vel), t, 0.9, -0.1)

    def theme(t0, notes, vel=96, g=1.0, octave=0):
        for e, m, ln in notes:
            M.add('brass', horn.play(n(m) + octave, vel, dur=ln * E8 * 1.02), t0 + e * E8, g, 0.1)

    M.add('drums', crash.play(100), TH, 0.5, -0.85)
    M.add('drums', bd.play(118), TH, 0.9, -0.85)
    M.add('brass', tbn.play(n('G2'), 112, dur=1.1), TH, 0.9, -0.5)
    M.add('brass', tbn.play(n('D3'), 104, dur=1.1), TH, 0.8, -0.5)
    M.add('fx', whoosh(1.4, 80, 500, 0.6, seed=5), TH, 0.7, pan_at(0))
    gallop(TH, TR1, ['Gm', 'Gm'], 100)
    theme(TH, THEME[:6], 100)

    def horse_hoof(t, d, k, kind):
        p = pan_at(d)
        if kind == 'far':
            return
        g = 1.0 if kind == 'gallop' else 1.3
        M.add('hoof', tumba.play(int(min(127, 92 * k)), pitch=-6), t, g, p)
        if kind in ('gallop',) and k >= 1.0:
            M.add('drums', timp.play(100, pitch=-3), t, 0.45, p)
        if kind in ('slam', 'stamp'):
            M.add('drums', timp.play(118, pitch=-4), t, 0.8, p)
            M.add('drums', tom.play(110), t, 0.6, p)
        if kind == 'skid':
            M.add('hoof', clop.play(70, pitch=-8), t, 0.5, p)

    for t, d, k, kind in P['strikes']:
        if t >= TH - 0.01:
            if kind == 'far':
                gain = k / (1 + (-d - 90) / 260)
                M.add('far', _muffle(tumba.play(100, pitch=-5), 18), t, 0.8 * gain, -0.85)
            else:
                horse_hoof(t, d, k, kind)

    # ---- 19.2-21.6: he rears at the front-left corner; whinny, the horn call close and loud ----
    pc1 = pan_at(C1)
    M.add('drums', troll.play(96, dur=1.0), TR1, 0.7, pc1)
    M.add('fx', _whinny(1.4, 560, 0.45, seed=1), TR1 + 0.15, 0.9, pc1)
    for c, t in (('Eb', TR1), ('D', TR1 + B)):
        for m in TRIADS[c]:
            M.add('brass', tbn.play(n(m) - 12 if m != TRIADS[c][2] else n(m), 108, dur=0.9), t, 0.6, -0.2)
        M.add('bass', tuba.play(n(ROOTS[c]) + 12, 112, dur=1.0), t, 0.9)
    for e, m, ln in HORN_CALL:
        M.add('brass', horn.play(n(m), 116, dur=ln * E8 * 1.05), TR1 + 0.9 + e * E8, 1.0, pc1)
    M.add('drums', scrape.play(90, dur=1.2), TR1 + 0.6, 0.5, pc1)
    # Ichabod startles and bolts: his theme, frantic
    M.add('wind', bsn_st.play(n('D4'), 110), TR1 + 0.2, 1.0, pan_at(ix(TR1)))
    for i, m in enumerate(('G3', 'A3', 'B3', 'C4', 'D4', 'E4', 'F#4', 'G4')):
        M.add('wind', bsn_st.play(n(m) - 12, 96), TR1 + 0.8 + i * 0.1, 0.8, pan_at(ix(TR1 + 0.8)))

    # ---- 21.6-22.8: the dash for the bridge; skid ----
    gallop(TG2, TK, ['Gm'], 104)
    theme(TG2, THEME[6:12], 102)
    flee = [(0, 'G3'), (1, 'A3'), (2, 'Bb3'), (3, 'A3'), (4, 'G3'), (5, 'F#3')]
    for rep in range(6):                                 # Ichabod, scrambling across the planks
        for e, m in flee:
            t = TR1 + 0.8 + 0.8 + rep * 1.2 + e * 0.2
            if t >= TA:
                break
            M.add('wind', bsn_st.play(n(m), 92), t, 0.75, pan_at(ix(t)))
    M.add('drums', scrape.play(110, dur=0.8), TK - 0.4, 0.7, pan_at(HK))
    M.add('drums', bd.play(110), TK, 0.8, pan_at(HK))

    # ---- 22.8-28.8: the Horseman rages at the foot of the bridge: stamps, rears, paws at the planks ----
    rage = ['Cm', 'Gm', 'Eb', 'D', 'D']
    gallop(TK, TU, rage, 84, low=True)
    ph = pan_at(HK)
    for t in STAMPS:
        M.add('brass', tbn_st.play(n('G2'), 116), t, 0.9, ph)
    M.add('fx', _whinny(1.6, 520, 0.5, seed=2), TR2 + 0.2, 0.9, ph)
    M.add('drums', troll.play(100, dur=2.2), TR2, 0.6, ph)
    for m in ('C3', 'Eb3', 'G3'):
        M.add('brass', tbn.play(n(m) - 12, 100, dur=2.2), TR2, 0.5, ph)
    theme(TR2 + 1.2, THEME[:6], 100, 0.9)
    for t in PAWS:                                       # each touch of the bridge rings it like a struck bell
        M.add('harp', harp.play(n('D3'), 110, dur=1.5), t, 0.9, pan_at(C2 + 40))
        M.add('harp', harp.play(n('A3'), 100, dur=1.5), t, 0.7, pan_at(C2 + 40))
        M.add('fx', whoosh(0.5, 300, 1200, 0.3, seed=int(t * 10)), t, 0.4, pan_at(C2 + 40))
    # Ichabod reaches the far bank, looks back: the psalm's first phrase, relieved, in the major
    for e, m, ln in PSALM[:6]:
        t = TA + 0.6 + e * E8
        M.add('wind', bsn.play(n(m), 84, dur=ln * E8 * 0.95), t, 0.9, pan_at(C5 + 50))
        M.add('wind', clar.play(n(THIRD[m]), 60, dur=ln * E8 * 0.95), t, 0.45, pan_at(C5 + 50))

    # ---- 28.8-32.4: he rises in his stirrups and whirls the pumpkin ----
    gallop(TU, TT, ['Gm', 'Ab', 'D'], 96)
    M.add('drums', troll.play(110, dur=3.6), TU, 0.85, ph)
    M.add('drums', swell.play(100), TT - 2.0, 0.6, ph)
    for i, m in enumerate(('D3', 'Eb3', 'E3', 'F3', 'F#3')):
        M.add('brass', horn.play(n(m), 90 + 6 * i, dur=0.75), TU + i * 0.72, 0.9, ph)
        M.add('strings', vtrem.play(n(m) + 12, 64 + 6 * i, dur=0.75), TU + i * 0.72, 0.5, 0.1)
    M.add('bass', tuba.play(n('D2'), 100, dur=3.6), TU, 0.8)
    tt = TU
    while tt < TT - 0.05:                                # one low whoosh per turn of the whirl
        u = (tt - TU) / (TT - TU)
        per = 1 / (0.6 + 1.9 * u)
        M.add('fx', whoosh(min(per, 0.9), 100, 600, 0.45, seed=int(tt * 100)), tt, 0.5 + 0.5 * u, ph)
        tt += per
    M.add('wind', bsn_st.play(n('F#3'), 100), TU + 1.8, 0.9, pan_at(C5 + 50))   # Ichabod sees it coming
    M.add('wind', bsn_st.play(n('G3'), 100), TU + 2.0, 0.9, pan_at(C5 + 50))

    # ---- 32.4-33.6: the throw, straight across the notch, left to right ----
    for m in ('G2', 'D3', 'G3', 'Bb3'):
        M.add('brass', horn.play(n(m), 118, dur=1.1), TT, 0.8, ph)
    M.add('brass', tbn.play(n('G2'), 120, dur=1.1), TT, 0.8, ph)
    M.add('bass', tuba.play(n('G1'), 120, dur=1.1), TT, 0.9)
    pt = pan_at(ix(TS))
    for i in range(6):                                   # the roar of the flying pumpkin, sweeping across
        u = i / 5
        M.add('fx', whoosh(0.35, 150 + 200 * u, 900, 0.5, seed=60 + i), TT + i * 0.18, 0.7, ph + (pt - ph) * u)
    M.add('strings', vtrem.play(n('D4'), 90, dur=1.2), TT, 0.6, 0.0)
    M.add('strings', ctrem.play(n('D3'), 90, dur=1.2), TT, 0.6, 0.0)

    # ---- 33.6: smash ----
    M.add('drums', bd.play(127), TS, 1.0, pt)
    M.add('drums', timp.play(127, pitch=-5), TS, 1.0, pt)
    M.add('drums', crash.play(120), TS, 0.8, pt)
    M.add('drums', gong.play(110, pitch=-3), TS, 0.7, pt)
    M.add('fx', _muffle(smash.play(110, pitch=-7), 4), TS, 0.5, pt)
    M.add('drums', slap.play(120), TS, 0.8, pt)
    M.add('bass', tuba.play(n('G1'), 124, dur=1.5), TS, 1.0)
    for m in ('G2', 'Bb2', 'D3', 'G3'):
        M.add('brass', tbn.play(n(m), 116, dur=1.2), TS, 0.6, pt)
    sh = _shards(np.random.default_rng(6))
    d_imp = ix(TS)
    for j in range(len(sh['v'])):                        # shards landing, each where it comes to rest
        dt = 0.45 * 1.2 + 0.1 * (j % 3)
        dest = d_imp + sh['v'][j] * 0.45 * (1 - np.exp(-dt / 0.45))
        if 0 <= dest <= L:
            M.add('drums', mar.play(n('G2') + int([0, 3, 5, 7, 10, 12][j % 6]), 70), TS + dt, 0.5, pan_at(dest))
    M.add('fx', slide(0.0, 0.5, 380, 900, 0.5, 0.25), TS + 0.05, 0.5, pan_at(L))      # his lantern, flung off the end

    # ---- 35.4-40.8: the headless horse rears and gallops off the way he came ----
    M.add('strings', ctrem.play(n('G2'), 70, dur=4.0), TS + 0.8, 0.6, -0.2)
    M.add('fx', _whinny(1.5, 470, 0.45, seed=3, ghost=True), TR3 + 0.1, 0.9, ph)
    gallop(TG3 - 0.6, TG3 + 3.6, ['Gm', 'Cm', 'Gm', 'D'], 82)
    theme(TG3, HORN_CALL, 88, 0.8)
    pad += [(TS + 1.0, n('G2'), 52, 7.0), (TS + 1.0, n('D3'), 46, 7.0)]

    # ---- 40.8-48: embers smoulder in the wind; a lament on the psalm, in the minor ----
    for tg in GUSTS:
        M.add('fx', whoosh(4.0, 100, 700, 0.55, seed=int(tg)), tg, 0.6, 0.0)
    lament = [(0, 'G3', 3), (3, 'Bb3', 2), (5, 'A3', 1), (6, 'G3', 2), (8, 'Eb3', 1), (9, 'D3', 3),
              (12, 'G3', 2), (14, 'A3', 1), (15, 'Bb3', 2), (17, 'C4', 1), (18, 'D4', 2), (20, 'Bb3', 1), (21, 'A3', 3)]
    tl = 41.4
    for e, m, ln in lament:
        M.add('strings', cello.play(n(m), 78, dur=ln * E8 * 1.6 + 0.2), tl + e * E8 * 1.5, 0.9, 0.3)
    for b, c in enumerate(('Gm', 'Cm', 'Gm', 'D', 'Gm')):
        t = tl + b * B * 1.5 - 0.0
        if t > TP:
            break
        organ += [(t, n(TRIADS[c][0]), 52, B * 1.5), (t, n(TRIADS[c][1]), 46, B * 1.5)]
        for i, m in enumerate(TRIADS[c] + (TRIADS[c][0],)):
            M.add('harp', harp.play(n(m) + (12 if i == 3 else 0), 70), t + i * 0.3, 0.7, 0.2)
        M.add('bass', cello.play(n(ROOTS[c]) + 12, 60, dur=B * 1.5), t, 0.4, -0.2)

    # ---- 48-53.8: a lantern peeks back in at the right end; he sees the mess and flees ----
    for i, (e, m) in enumerate(((0, 'D3'), (2, 'E3'), (4, 'F#3'), (6, 'G3'), (10, 'A3'), (12, 'F#3'))):
        t = TP + 0.4 + e * E8 * 1.5
        M.add('wind', bsn_st.play(n(m), 80), t, 0.9, pan_at(ix(t)))
        M.add('bass', pizz.play(n('D2') if i % 2 == 0 else n('A2'), 70), t, 0.7, 0.4)
    M.add('wind', clar.play(n('D4'), 56, dur=1.6), TP + 2.6, 0.6, 0.85)
    M.add('wind', bsn.play(n('Eb3'), 70, dur=1.4), TP + 3.2, 0.7, 0.85)
    M.add('wind', bsn_st.play(n('D4'), 116), TE, 1.0, 0.85)            # eek
    M.add('drums', snare.play(100), TE, 0.5, 0.85)
    for i, m in enumerate(('D4', 'C4', 'Bb3', 'A3', 'G3', 'F#3', 'E3', 'D3', 'C3', 'B2')):
        M.add('wind', bsn_st.play(n(m), 100 - 3 * i), TE + 0.15 + i * 0.075, 0.8, 0.9)
    M.add('fx', slide(0.0, 0.7, 700, 330, 0.75, 0.3), TE + 0.2, 0.4, 0.9)

    # ---- 55.2-61: far off, a new head lights up, grins and laughs ----
    for e, m, ln in HORN_CALL:
        M.add('far', _muffle(horn.play(n(m), 84, dur=ln * E8 * 1.05), 10), TZ - 0.8 + e * E8, 0.7, -0.85)
    M.add('fx', whoosh(1.2, 80, 400, 0.5, seed=77), TZ, 0.6, -0.85)
    M.add('drums', timp_s.play(90, pitch=-5), TZ + 0.6, 0.7, -0.85)
    for i in range(9):                                   # ha-ha-ha, in the trombones
        t = TZ + 1.2 + i * 0.2
        m = ('Bb2', 'A2', 'G2')[i % 3]
        M.add('brass', tbn_st.play(n(m) - (i // 3), 96 - 4 * i), t, 0.8, -0.8)
    M.add('drums', bd.play(96), TZ + 3.6, 0.7, -0.85)
    organ += [(TZ + 3.6, n('G2'), 70, 2.4), (TZ + 3.6, n('D3'), 62, 2.4), (TZ + 3.6, n('Bb3'), 56, 2.4)]
    M.add('bass', tuba.play(n('G1'), 96, dur=2.4), TZ + 3.6, 0.8)
    M.add('strings', cello.play(n('G2'), 74, dur=2.2), TZ + 3.6, 0.7, -0.3)

    M.add('pad', M.synth('Pads/Ghost Pad').render(pad, D), 0.0)
    M.add('organ', M.synth('Keys/Church').render(organ, D), 0.0)
