"""Unwrapped: a mummy (the porch notch: bandage stripes, a dark eye slot with two amber eyes) wraps up from
his feet, looks around, and dances stiffly to a creaky swing tune, shedding dust onto the wings with every
move. Reaching for a big pose, his back goes CRACK and a loose bandage end pops out onto Right. A cat walks
in from the right end, creeps up, pounces, and runs off with it: he spins, eyes whirling across the porch,
and the bandage unwinds in stripes along Right, then along Left and down the Side to the back. When the last
of it is gone the porch is dark; two tiny eyes blink on, and he is revealed in red polka-dot boxers. He
looks down, blushes, shrugs and dances anyway, while the whole house, wrapped in his bandage, bops along.

Everything is drawn in path distance (layout units along the roofline), with exact span coverage, so the
eyes, stripes, dust motes and cat keep their size on every run."""
import numpy as np
from pixelhome.fx import DT, hexc, light, smoothstep, keys, lerp, nframes

CODE = 'HW11'
TITLE = 'Unwrapped'
KIND = 'show'
DESCRIPTION = ('A stiff old mummy dances on the porch, shedding dust, until a cat runs off with his loose '
               'bandage end. He spins, the bandage wraps the whole house, and underneath he is very small '
               'and wearing polka-dot boxers.')
VOICEOVER = ("He's three thousand years old, and tonight... he dances. Stiff joints, loose bandages, and "
             "one very curious cat.")

BAND = hexc('#ffe6c0')          # bandage
SEAM = hexc('#9a7650')
AMBER = hexc('#ffa018')
DUSK = hexc('#5c38b8')
SPOT = hexc('#ff9030')
DUST = hexc('#d8a458')
CAT = hexc('#66ff22')
RED = hexc('#ff0c1c')
DOT = hexc('#ffffff')
WAIST = hexc('#ffc8d4')
BLUSH = hexc('#ff2a70')

BEAT = 0.55                     # 109 BPM swing
T0 = 9.9                        # the dance, beat 0
COUNT = [T0 - 4 * BEAT + i * BEAT for i in range(4)]   # four stiff stomps
BLINKS = [4.3, 13.0, 21.3, 30.1]
TCRACK = T0 + 44 * BEAT         # 34.1: his back goes
TCAT = 36.0                     # the cat walks in at the right end
CAT_V, CAT_STEP = 125.0, 0.32
TCROUCH, TPOUNCE, TGRAB = 39.0, 40.4, 40.55
TSPIN, TLEFT, TOFF = 41.0, 42.6, 50.0
LEFT_V = 700.0                  # the second end races down Left and Side
TEYES, TREVEAL = 51.0, 52.4     # tiny eyes, then the boxers
TBLUSH = 56.0
TF = 57.2                       # boxer dance, 16 beats
TFIN = TF + 16 * BEAT           # 66.0: final hit
TPEEK, TWINK = 66.8, 68.4
D = 72.0
SPIN_KEYS = [(TSPIN, 0.0), (42.0, 0.8), (46.0, 2.2), (48.6, 2.6), (49.6, 1.6), (TOFF, 0.0)]  # revolutions/s
PULL = 300.0                    # units of bandage per revolution


def _back(u, c1=1.6):
    u = np.clip(u, 0, 1)
    return 1 + (c1 + 1) * (u - 1) ** 3 + c1 * (u - 1) ** 2


def _hit(f, k=0.12):
    """Envelope f beats after a hit."""
    return float(np.exp(-max(f, 0.0) * BEAT / k))


def plan(G):
    """Geometry and the shared timings that render() and score() both use."""
    P = {}
    pdp = G.pd[G.path]
    P['pdp'] = pdp
    first = {n: float(G.pd[G.seg[n]].min()) for n in G.seg}
    last = {n: float(G.pd[G.seg[n]].max()) for n in G.seg}
    P['L'] = float(G.length)
    P['dPL0'] = first['Porch Left']                 # bottom of his left side (corner with Left)
    P['dPR1'] = last['Porch Right']                 # bottom of his right side (corner with Right)
    P['dc'] = 0.5 * (first['Porch Front'] + last['Porch Front'])
    P['cL'] = 0.5 * (first['Left'] + last['Left'])
    P['cR'] = 0.5 * (first['Right'] + last['Right'])
    P['side1'] = last['Side']
    P['first'], P['last'] = first, last
    P['tip0'] = P['dPR1'] + 70.0                    # where the loose end rests
    ts = np.arange(nframes(D)) * DT
    rate = np.array([keys(t, SPIN_KEYS) if TSPIN <= t < TOFF else 0.0 for t in ts])
    P['phi'] = np.concatenate([[0.0], np.cumsum(rate)[:-1] * DT])
    P['ts'] = ts
    return P


def cat_x(P, t):
    """The cat's path distance (None when it is off the house)."""
    L = P['L']
    if TCAT <= t < TCROUCH:
        return L + 20 - CAT_V * (t - TCAT)
    stop = L + 20 - CAT_V * (TCROUCH - TCAT)
    if TCROUCH <= t < TPOUNCE:
        return stop + (3.0 * np.sin(2 * np.pi * 6 * t) * smoothstep(39.7, 39.9, t))
    if TPOUNCE <= t < TGRAB:
        return lerp(stop, P['tip0'], smoothstep(0, 1, (t - TPOUNCE) / (TGRAB - TPOUNCE)))
    if TGRAB <= t < TGRAB + 0.6:
        x = P['tip0'] + 2200 * (t - TGRAB) ** 2
        return x if x < L + 25 else None
    if TPEEK <= t:
        return L - 14
    return None


def cat_steps(P):
    return [TCAT + 0.15 + k * CAT_STEP for k in range(int((TCROUCH - TCAT - 0.15) / CAT_STEP) + 1)]


def spin_ticks(P):
    """Times the spinning face passes the front: each whole revolution."""
    phi, ts = P['phi'], P['ts']
    k = np.floor(phi)
    idx = np.nonzero(np.diff(k) > 0)[0] + 1
    return [float(ts[i]) for i in idx]


def left_head(P, t):
    return max(0.0, P['dPL0'] - LEFT_V * (t - TLEFT))


def left_arrive(P):
    return TLEFT + P['dPL0'] / LEFT_V


def right_exit(P):
    return TGRAB + np.sqrt((P['L'] - P['tip0']) / 2200)


def dance_moves():
    """Beat-by-beat events of the dance: (time, kind, side) with side -1 = his left (Porch Left), +1 right."""
    ev = []
    for j in range(44):
        t = T0 + j * BEAT
        if j < 16:
            ev.append((t, 'sway', 1 if j % 2 == 0 else -1))
        elif j < 32:
            ev.append((t, 'arm', -1 if j % 2 == 0 else 1))
        elif j < 40:
            ev.append((t, 'shimmy', 0))
        else:
            ev.append((t, 'windup', 0))
    return ev


def _puffs(P, rng):
    """Dust motes (t0, x0, v, life)."""
    m = []

    def puff(t0, x0, dirn, k, v0, v1, life=(1.0, 1.9)):
        for _ in range(k):
            d = dirn if dirn else rng.choice([-1, 1])
            m.append((t0 + rng.uniform(0, 0.05), x0 + rng.uniform(-8, 8), d * rng.uniform(v0, v1),
                      rng.uniform(*life)))

    corner = {-1: P['dPL0'] + 10, 1: P['dPR1'] - 10}
    for t in COUNT:
        puff(t, corner[-1], -1, 4, 60, 200)
        puff(t, corner[1], 1, 4, 60, 200)
    for t, kind, side in dance_moves():
        if kind in ('sway', 'arm'):
            puff(t, corner[side], side, 7, 80, 300)
        elif kind == 'shimmy':
            for e in range(2):
                puff(t + e * BEAT * 2 / 3, rng.uniform(P['dPL0'] + 40, P['dPR1'] - 40), 0, 2, 20, 90, (0.8, 1.4))
    puff(TCRACK, corner[-1], -1, 30, 150, 650, (1.4, 2.6))
    puff(TCRACK, corner[1], 1, 30, 150, 650, (1.4, 2.6))
    for _ in range(18):
        puff(TCRACK, rng.uniform(P['dPL0'] + 30, P['dPR1'] - 30), 0, 1, 40, 160, (1.0, 2.0))
    for t in spin_ticks(P):
        puff(t, corner[-1], -1, 3, 200, 500, (0.7, 1.2))
        puff(t, corner[1], 1, 3, 200, 500, (0.7, 1.2))
    return np.array(m)


def render(G, seed=11):
    rng = np.random.default_rng(seed)
    P = plan(G)
    pdp, L = P['pdp'], P['L']
    dPL0, dPR1, dc = P['dPL0'], P['dPR1'], P['dc']
    w = np.gradient(pdp)
    e0, e1 = pdp - w / 2, pdp + w / 2

    def box(c, hw):
        return np.clip(np.minimum(c + hw, e1) - np.maximum(c - hw, e0), 0, None) / w

    porch = (pdp >= dPL0 - 1) & (pdp <= dPR1 + 1)
    u = np.where(pdp < dc, (dc - pdp) / (dc - dPL0), (pdp - dc) / (dPR1 - dc))     # 0 head .. 1 feet
    u = np.clip(u, 0, 1)
    left_leg = porch & (pdp < P['first']['Porch Front'] - 2)
    right_leg = porch & (pdp > P['last']['Porch Front'] + 2)
    front = porch & ~left_leg & ~right_leg
    wings = np.zeros(G.N)
    wings[(pdp >= P['first']['Left']) & (pdp < dPL0)] = 1
    wings[(pdp > dPR1) & (pdp <= L)] = 1
    side = (pdp <= P['side1'] + 1).astype(float)
    tint = rng.uniform(0.78, 1.0, 512)
    motes = _puffs(P, rng)
    ticks = spin_ticks(P)

    def stripes(off, period, duty, soft=0.14):
        s = (pdp - off) / period
        f = s % 1
        band = smoothstep(0, soft, f) * (1 - smoothstep(duty - soft, duty, f))
        return band, tint[np.floor(s).astype(int) % 512]

    # wrap-on: stripe by stripe, feet first
    P0 = 30.0
    kc = (np.floor(pdp / P0) + 0.5) * P0
    uk = np.clip(np.where(kc < dc, (dc - kc) / (dc - dPL0), (kc - dc) / (dPR1 - dc)), 0, 1)
    twrap = 0.5 + 2.6 * (1 - uk)
    tunwrap = 41.8 + 7.8 * u ** 0.9

    F = nframes(D)
    out = np.zeros((F, G.N, 3))
    for fi in range(F):
        t = fi * DT
        phi = P['phi'][fi]
        fade = 1 - smoothstep(69.5, 71.8, t)

        # ---- the figure's pose ----
        off, period, base, eye_open, gaze, eye_I = 0.0, P0, 0.55, 1.0, 0.0, 0.9
        arm = {-1: 0.0, 1: 0.0}
        b = (t - T0) / BEAT
        j = int(np.floor(b))
        f = b - j
        if t < T0:
            for tc in COUNT:
                if t >= tc:
                    base = max(base, 0.55 + 0.3 * _hit((t - tc) / BEAT))
            gaze = keys(t, [(4.4, 0), (4.8, -1), (5.6, -1), (6.0, 1), (6.8, 1), (7.1, 0)])
        elif j < 16:
            tgt = lambda jj: 0.0 if jj < 0 else (1.0 if jj % 2 == 0 else -1.0)
            off = 14 * lerp(tgt(j - 1), tgt(j), smoothstep(0, 0.18, f))
            gaze = 0.5 * tgt(j)
        elif j < 32:
            sd = -1 if j % 2 == 0 else 1
            arm[sd] = _hit(f, 0.3)
            off = 4 * sd * smoothstep(0, 0.18, f)
            gaze = 0.7 * sd
        elif j < 40:
            off = 6 * np.sin(2 * np.pi * 2 * b)
            eye_open = 0.6
        elif t < TCRACK:
            s = smoothstep(T0 + 40 * BEAT, TCRACK, t)
            period = P0 + 10 * s
            base = 0.55 + 0.25 * s
            eye_open = 1 + 0.5 * s
        else:
            tt = t - TCRACK
            if tt < 0.5:
                period = P0 + 10 * (1 - _back(tt / 0.25, 2.5))
                off = 5 * np.sin(2 * np.pi * 14 * tt) * np.exp(-tt * 6)
            base = 0.5 + 0.5 * np.exp(-tt / 0.25)
            eye_open = keys(t, [(TCRACK, 0.25), (TCRACK + 1.4, 0.25), (TCRACK + 1.8, 1.0)])
            gaze = keys(t, [(35.6, 0), (35.9, -1), (36.5, -1), (36.8, 1), (37.4, 1), (37.7, 0)])
            if 37.8 <= t < TCROUCH:                  # tries again, small
                k = int((t - 37.8) / (2 * BEAT))
                ff = (t - 37.8) / (2 * BEAT) - k
                off = 6 * (1 if k % 2 == 0 else -1) * smoothstep(0, 0.2, ff)
            if t >= TGRAB:
                eye_open = keys(t, [(TGRAB, 1.0), (TGRAB + 0.1, 1.7)])
                eye_I = 1.0
        for bt in BLINKS:
            eye_open *= min(1.0, abs(t - bt) / 0.1)

        fr = np.zeros((G.N, 3))
        I = np.zeros(G.N)                            # bandage intensity

        # ---- night and the wings ----
        dusk = 0.3 * smoothstep(0, 1.5, t) * fade
        spot = np.zeros(G.N)
        if t < TCRACK:
            sL = sR = 0.16 * smoothstep(1.0, 3.0, t)
            if t >= COUNT[0]:
                for tc in COUNT:
                    if t >= tc:
                        sL = max(sL, 0.16 + 0.22 * _hit((t - tc) / BEAT, 0.25))
                sR = sL
            if T0 <= t:
                sd = (1 if j % 2 == 0 else -1) if j < 16 else (-1 if j % 2 == 0 else 1) if j < 32 else 0
                pk = 0.32 * _hit(f, 0.3)
                if sd == -1:
                    sL = max(sL, 0.16 + pk)
                elif sd == 1:
                    sR = max(sR, 0.16 + pk)
                else:
                    sL = sR = 0.18 + 0.12 * _hit((2 * b) % 1 / 2, 0.08)
            spot = sL * np.exp(-((pdp - P['cL']) / 150) ** 2) + sR * np.exp(-((pdp - P['cR']) / 150) ** 2)
        elif t < TOFF:
            s = 0.14 * (1 - smoothstep(TCRACK, TCRACK + 1.0, t)) + 0.18
            spot = s * (np.exp(-((pdp - P['cL']) / 150) ** 2) + np.exp(-((pdp - P['cR']) / 150) ** 2))

        # ---- the mummy ----
        if t < TOFF:
            band, ti = stripes(off + (120 * phi if t >= TSPIN else 0.0), period, 0.74)
            vis = np.clip((t - twrap) / 0.12, 0, 1)
            pop = 0.35 * np.exp(-np.clip(t - twrap, 0, None) / 0.2) * (t >= twrap)
            if t >= 41.8:
                vis = vis * (1 - smoothstep(tunwrap - 0.25, tunwrap, t))
            Ib = base * (0.32 + 0.68 * band) * ti * vis + pop * vis
            for sd, leg in ((-1, left_leg), (1, right_leg)):
                if arm[sd]:
                    Ib = Ib + leg * 0.4 * arm[sd] * vis
            ec = dc + off
            if t >= 3.0 and t < TSPIN:
                slot = smoothstep(46, 60, np.abs(pdp - ec))
                Ib = Ib * (slot + (1 - slot) * (1 - smoothstep(3.0, 3.4, t)))
            I = np.where(porch, Ib, I)
            if t < TSPIN:                            # the hands: a flash at the bottom of the arm that pumps
                for sd, c in ((-1, dPL0 + 22), (1, dPR1 - 22)):
                    if arm[sd]:
                        I = I + 0.5 * arm[sd] * box(c, 22)
            # eyes
            if t >= 3.0:
                oi = eye_I * smoothstep(3.2, 3.6, t)
                if t < TSPIN:
                    for s in (-1, 1):
                        c = ec + s * 30 + gaze * 13
                        fr += light(AMBER, oi * np.clip(box(c, 7.5 * eye_open), 0, 1))
                else:
                    a = 2 * np.pi * phi
                    face = np.cos(a)
                    if face > 0:
                        cc = dc + 165 * np.sin(a)
                        for s in (-1, 1):
                            c = cc + s * 30 * face
                            fr += light(AMBER, oi * min(1, 2 * face) * np.clip(box(c, 7.5 * 1.4 * face + 1), 0, 1))

        # ---- the loose end and the unwound bandage ----
        tip = P['tip0']
        if TCRACK <= t < TGRAB:
            tt = t - TCRACK
            le = 70 * _back(tt / 0.35) + 6 * np.sin(2 * np.pi * 1.2 * tt) * smoothstep(0.4, 1.0, tt)
            band, ti = stripes(dPR1, 32, 0.7)
            seg = (pdp > dPR1) & (pdp <= dPR1 + le)
            I = np.where(seg, 0.55 * (0.3 + 0.7 * band) * ti + 0.4 * np.exp(-tt / 0.3), I)
            I = I + 0.35 * box(dPR1 + le - 3, 4) * (pdp > dPR1)
        strip_I = 0.52
        if t >= TFIN:
            strip_I = 0.5 + 0.35 * _hit((t - TFIN) / BEAT, 0.5)
        elif t >= TF:
            bf = (t - TF) / BEAT
            strip_I = 0.42 + 0.25 * _hit(bf % 1, 0.15)
        elif t >= TOFF:
            strip_I = 0.52 + 0.3 * np.exp(-(t - TOFF) / 0.4)
        step = 0.0
        if t >= TF + 8 * BEAT and t < TFIN:          # the wrapped house steps along with him
            bf = (t - TF) / BEAT - 8
            step = 23 * (int(bf) + smoothstep(0, 0.25, bf % 1))
        if t >= TGRAB:
            xc = cat_x(P, t)
            xr = L + 5 if (xc is None or t > TGRAB + 0.6) else max(tip, xc)
            pull = min(xr, L) - tip + PULL * phi
            band, ti = stripes(dPR1 + pull + step, 46, 0.55)
            seg = (pdp > dPR1) & (pdp <= xr)
            I = np.where(seg, strip_I * (0.12 + 0.88 * band) * ti, I)
            if xr < L:
                I = I + 0.6 * box(xr - 4, 5) * seg
        if t >= TLEFT:
            xl = left_head(P, t)
            pullL = PULL * (phi - P['phi'][nframes(TLEFT)])
            band, ti = stripes(dPL0 - pullL - step, 46, 0.55)
            seg = (pdp < dPL0) & (pdp >= xl)
            I = np.where(seg, strip_I * (0.12 + 0.88 * band) * ti, I)
            if xl > 0:
                I = I + 0.6 * box(xl + 4, 5) * seg
        covered = np.clip(I * 3, 0, 1)
        fr += light(DUSK, dusk * (wings + 0.7 * side) * (1 - covered))
        fr += light(SPOT, spot * wings * (1 - covered))
        fr += light(BAND, I * fade)

        # ---- dust ----
        act = (motes[:, 0] <= t) & (t < motes[:, 0] + motes[:, 3])
        if act.any():
            mm = motes[act]
            tt = t - mm[:, 0]
            x = mm[:, 1] + mm[:, 2] * 0.45 * (1 - np.exp(-tt / 0.45))
            a = 0.5 * np.clip(tt / 0.05, 0, 1) * (1 - tt / mm[:, 3]) ** 1.5
            dI = (a[:, None] * np.exp(-((pdp[None, :] - x[:, None]) / 6.0) ** 2)).sum(0)
            fr += light(DUST, np.clip(dI, 0, 0.6))

        # ---- the cat ----
        xc = cat_x(P, t)
        if xc is not None:
            ci = 1.0
            hw = 3.2
            if TCAT <= t < TCROUCH:
                ci = 0.85 + 0.15 * np.sin(2 * np.pi * (t - TCAT) / (2 * CAT_STEP))
            elif TCROUCH <= t < TPOUNCE:
                hw = keys(t, [(TCROUCH, 3.2), (TCROUCH + 0.3, 1.6)])
            if t >= TPEEK:
                ci = 0.95 * smoothstep(TPEEK, TPEEK + 0.4, t)
                if 68.0 <= t < 68.18:
                    hw = 0.3
            cm = np.clip(box(xc - 6, hw) + box(xc + 6, hw), 0, 1)
            fr = fr * (1 - cm[:, None] * 0.9) + light(CAT, ci * fade * cm)

        # ---- underneath ----
        if t >= TEYES:
            ob = 1.0
            for bt in (TEYES + 0.45, TEYES + 0.8):
                ob *= min(1.0, abs(t - bt) / 0.08)
            gz = keys(t, [(53.0, 0), (53.3, -1), (54.0, -1), (54.3, 1), (55.0, 1), (55.3, 0)])
            wide = keys(t, [(55.5, 1.0), (55.7, 1.6), (56.2, 1.0)])
            if t >= TF:
                bf = (t - TF) / BEAT
                gz = 0.6 * (1 if int(bf) % 2 else -1) * smoothstep(0, 0.2, bf % 1) if t < TFIN else 0.0
            if t >= TPEEK:
                gz = keys(t, [(67.3, 0), (67.5, 1), (68.0, 1), (68.2, 0)])
            ei = smoothstep(TEYES, TEYES + 0.15, t) * fade
            for s in (-1, 1):
                op = ob * wide
                if s == -1 and TWINK <= t < TWINK + 0.55:
                    op *= 0.0
                fr += light(AMBER, 0.9 * ei * np.clip(box(dc + s * 9 + gz * 6, 2.8 * op), 0, 1))
        if t >= TREVEAL:
            pop = 1 + 0.5 * np.exp(-(t - TREVEAL) / 0.3)
            kick = {-1: 0.0, 1: 0.0}
            doff = {-1: 0.0, 1: 0.0}
            wb = 0.0
            if t >= 57.0 and t < TF:                 # shrug: the waistband hitches up
                wb = 0.4 * np.sin(np.pi * np.clip((t - 57.0) / 0.3, 0, 1))
            if TF <= t < TFIN:
                bf = (t - TF) / BEAT
                k = int(bf)
                sd = -1 if k % 2 == 0 else 1
                kick[sd] = _hit(bf % 1, 0.25)
                doff[sd] = 9 * smoothstep(0, 0.2, bf % 1)
                wb = 0.3 * _hit(bf % 1, 0.15)
            if t >= TFIN:
                pop = 1 + 0.5 * _hit((t - TFIN) / BEAT, 0.5)
            ri = 0.6 * pop * fade
            for sd, leg in ((-1, left_leg), (1, right_leg)):
                ph = ((pdp - doff[sd] * sd) / 36.0) % 1
                dots = smoothstep(0.0, 0.06, ph) * (1 - smoothstep(0.18, 0.24, ph))
                li = ri * (1 + 0.5 * kick[sd]) * leg
                fr += light(RED, li * (1 - dots))
                fr += light(DOT, 0.9 * li * dots)
            waist = front & (np.abs(pdp - dc) > 26)
            fr += light(WAIST, (0.42 + wb) * pop * fade * waist)
        if t >= TBLUSH:
            bl = smoothstep(TBLUSH, TBLUSH + 0.6, t) * (1 - 0.6 * smoothstep(58.0, 59.5, t))
            if t >= TWINK:
                bl = max(bl, 0.7 * np.sin(np.pi * np.clip((t - TWINK) / 1.0, 0, 1)))
            fr += light(BLUSH, 0.85 * bl * fade * np.clip(box(dc - 19, 5) + box(dc + 19, 5), 0, 1))

        out[fi][G.path] = np.clip(fr, 0, 1)
    return out


# ---------------------------------------------------------------- music ----------------------------------------------
# A creaky little swing band in G minor at the lights' 109 BPM: tuba and pizzicato oom-pah, a bassoon for the mummy's
# stiff steps, clarinet answering, a guiro creak on every snap of his joints and a cabasa puff for every cloud of dust,
# panned to the corner it comes off. The crack stops the band; a solo violin tiptoes in with the cat, step for step.
# The spin is a slide whistle riding the spin rate with a xylophone tick each time his face comes round, and the band
# chasing it, oom-pah per half turn. The boxers get a drum roll, a ta-da and a wolf whistle; the last dance is the
# tune again in G major, with trombone kicks on his kicks.

PROG = ['Gm', 'Gm', 'Cm', 'D7', 'Gm', 'Eb', 'D7', 'Gm']
CHORD = {'Gm': ('G3', 'Bb3', 'D4'), 'Cm': ('G3', 'C4', 'Eb4'), 'D7': ('F#3', 'A3', 'C4'), 'Eb': ('G3', 'Bb3', 'Eb4'),
         'G': ('G3', 'B3', 'D4'), 'C': ('G3', 'C4', 'E4'), 'D': ('F#3', 'A3', 'D4')}
ROOT = {'Gm': ('G1', 'D2'), 'Cm': ('C2', 'G1'), 'D7': ('D2', 'A1'), 'Eb': ('Eb2', 'Bb1'),
        'G': ('G1', 'D2'), 'C': ('C2', 'G1'), 'D': ('D2', 'A1')}
SW = 2 / 3                      # the swung eighth
TUNE_A = [(0, 'G3'), (1, 'D4'), (2, 'Bb3'), (2 + SW, 'A3'), (3, 'G3'),
          (4, 'G3'), (5, 'D4'), (6, 'Eb4'), (6 + SW, 'D4'), (7, 'Bb3'),
          (8, 'C4'), (9, 'G4'), (10, 'Eb4'), (10 + SW, 'D4'), (11, 'C4'),
          (12, 'D4'), (12 + SW, 'F#3'), (13, 'A3'), (14, 'C4'), (15, 'D4')]
TUNE_B = [(16 + SW, 'D5'), (17 + SW, 'Bb4'), (18 + SW, 'G4'), (19 + SW, 'Bb4'), (20 + SW, 'Eb5'), (21 + SW, 'G4'),
          (22 + SW, 'Bb4'), (23 + SW, 'Eb5'), (24 + SW, 'D5'), (25 + SW, 'C5'), (26 + SW, 'A4'), (27 + SW, 'F#4'),
          (28 + SW, 'G4'), (29 + SW, 'Bb4'), (30 + SW, 'D5'), (31 + SW, 'G4')]
TUNE_F = [(0, 'B4'), (SW, 'D5'), (1, 'G4'), (2, 'B4'), (2 + SW, 'A4'), (3, 'G4'),
          (4, 'C5'), (4 + SW, 'E5'), (5, 'G4'), (6, 'C5'), (6 + SW, 'B4'), (7, 'A4'),
          (8, 'D5'), (8 + SW, 'C5'), (9, 'B4'), (10, 'A4'), (10 + SW, 'F#4'), (11, 'D4'),
          (12, 'G4'), (12 + SW, 'B4'), (13, 'D5'), (14, 'G4'), (15, 'D4')]
PROG_F = ['G', 'C', 'D', 'G']


def score(M, G):
    from pixelhome.audio import SR, note, slide, whoosh
    n = note
    P = plan(G)
    L = P['L']
    tuba = M.sampler('Brass/Tuba/stac/*.wav')
    pizz = M.sampler('Strings/Cello Section/pizzT/*.wav')
    bsn = M.sampler('Woodwinds/Bassoon/stac/*.wav', tune=-12)
    clar = M.sampler('Woodwinds/Clarinet/stac/*.wav', tune=-12)
    xylo = M.sampler('Percussion/Xylo/*.wav')
    glock = M.sampler('Percussion/Glock/*.wav')
    vpizz = M.sampler('Strings/Solo Violin/Pizz/*.wav')
    harp = M.sampler('Strings/Harp/*.wav')
    tbn = M.sampler('Brass/OldTrombone/Short/*.wav', tune=-12)
    tpt = M.sampler('Brass/Trumpet/stac/*.wav')
    fall = M.hits('Brass/OldTrombone/Fall/Trombone_Fall_A#2_*.wav')
    guiro = M.hits('VSCO 1 Percussion/varWood/guiro_short*.wav')
    guiro_l = M.hits('VSCO 1 Percussion/varWood/guiro_long*.wav')
    cabasa = M.hits('VSCO 1 Percussion/varMetal/various/cabasa_[1-6].wav')
    cab_roll = M.hits('VSCO 1 Percussion/varMetal/various/cabasa_roll*.wav')
    maraca = M.hits('VSCO 1 Percussion/varWood/maraca[1-5].wav')
    snare = M.hits('VSCO 1 Percussion/drums/snare/drum1/snare1_mp_[12].wav')
    rim = M.hits('VSCO 1 Percussion/drums/snare/drum1/snare1_rimshot_f*.wav')
    sroll = M.hits('Percussion/Snare2-rollSN_v3*.wav')
    bd = M.hits('Percussion/BDrumNewhit_v[4-7]*.wav')
    crash = M.hits('Percussion/cymbal-crash1_f*.wav')
    crash_s = M.hits('Percussion/cymbal-crashshort*.wav')
    slap = M.hits('VSCO 1 Percussion/varWood/slapstick[0-9].wav')
    vibra = M.hits('VSCO 1 Percussion/varWood/vibraslap*.wav')
    ratchet = M.hits('Percussion/Ratchet1-Crank*.wav')
    ratchet_f = M.hits('Percussion/Ratchet1-Fast*.wav')
    wood = M.hits('VSCO 1 Percussion/varWood/wood_click*.wav')
    clave = M.hits('Percussion/Claves1_Hit*.wav')
    tri = M.hits('Percussion/Triangle3-Hit_*.wav')
    timp = M.hits('Percussion/Timpani/Timpani1_Hit*.wav')
    troll = M.hits('Percussion/Timpani/Rolls/*.wav')
    tamb = M.hits('Percussion/Tamb1-Hit*.wav')

    for name, gain, rev in (('bass', 0.5, 0.08), ('pizz', 0.3, 0.15), ('wind', 0.42, 0.2), ('xylo', 0.36, 0.22),
                            ('mallet', 0.32, 0.25), ('perc', 0.55, 0.12), ('drums', 0.45, 0.16), ('brass', 0.36, 0.2),
                            ('fx', 0.16, 0.25), ('strings', 0.34, 0.2)):
        M.bus(name, gain=gain, reverb=rev)

    order = np.argsort(G.pd)
    xs, ds = G.pos[order, 0], G.pd[order]
    x0, x1 = xs.min(), xs.max()

    def pan_at(d):                          # path distance -> left/right across the facade, from the street
        x = np.interp(np.clip(d, 0, L), ds, xs)
        return float(0.85 * (2 * (x - x0) / (x1 - x0) - 1))

    corner = {-1: pan_at(P['dPL0']), 1: pan_at(P['dPR1'])}
    dc = pan_at(P['dc'])

    def beat(b, t0=T0):
        return t0 + b * BEAT

    def oompah(b0, b1, prog, t0=T0, vel=92):
        for k in range(b0, b1):
            t = beat(k, t0)
            c = prog[(k // 4) % len(prog)]
            if k % 2 == 0:
                M.add('bass', tuba.play(n(ROOT[c][(k // 2) % 2]), vel), t)
            else:
                for m in CHORD[c]:
                    M.add('pizz', pizz.play(n(m), vel - 14), t, 0.7, -0.3)

    # ---- 0-9.9: wrapped from the feet up, eyes open, a look each way, four stiff stomps ----
    M.add('fx', whoosh(3.5, 150, 600, 0.4, seed=2), 0.0, 0.5)
    M.add('perc', cab_roll.play(70), 0.5, 0.6, corner[-1])
    M.add('perc', cab_roll.play(70), 0.6, 0.6, corner[1])
    gl = ['G2', 'Bb2', 'D3', 'G3', 'Bb3', 'D4', 'G4', 'Bb4', 'D5']
    for i, m in enumerate(gl):              # harp climbs as the wrapping climbs to his head
        M.add('strings', harp.play(n(m), 80 + 4 * i), 0.5 + 2.6 * i / (len(gl) - 1), 0.6, -0.5 + i / 8)
    for k, m in enumerate(('G4', 'D5')):
        M.add('mallet', glock.play(n(m) - 12, 80), 3.4 + 0.12 * k, 0.8, dc)
    M.add('wind', bsn.play(n('G2'), 100, dur=0.5), 3.4, 0.9, dc)
    for t, d, m in ((4.8, -1, 'D3'), (6.0, 1, 'Eb3'), (7.1, 0, 'D3')):
        M.add('perc', guiro_l.play(70, dur=0.45), t - 0.35, 0.6, 0.5 * d)
        M.add('wind', bsn.play(n(m), 85, dur=0.3), t, 0.7, 0.5 * d)
    for i, t in enumerate(COUNT):
        M.add('drums', bd.play(95 + 8 * i), t, 0.9)
        M.add('perc', guiro.play(90), t, 0.6)
        M.add('perc', cabasa.play(80), t + 0.03, 0.5, corner[-1])
        M.add('perc', cabasa.play(80), t + 0.05, 0.5, corner[1])
        M.add('xylo', xylo.play(n(['D4', 'D4', 'D4', 'F#4'][i]), 90), t, 0.6)

    # ---- 9.9-34.1: the dance ----
    oompah(0, 40, PROG)
    for k in range(40):
        t = beat(k)
        if k % 2:
            M.add('drums', snare.play(70), t, 0.45)
        for e in (0, SW):
            M.add('perc', maraca.play(60 + 20 * (e == 0)), t + e * BEAT, 0.3)
    for b, m in TUNE_A:
        M.add('wind', bsn.play(n(m), 104, dur=0.3), beat(b), 1.0, 0.0)
    for t, kind, sd in dance_moves():
        if kind == 'sway':
            M.add('perc', guiro.play(85), t, 0.5, 0.6 * sd)
            M.add('perc', cabasa.play(75), t + 0.04, 0.45, corner[sd])
        elif kind == 'arm':
            c = PROG[(int(round((t - T0) / BEAT)) // 4) % len(PROG)]
            m = CHORD[c][0 if sd < 0 else 2]
            M.add('brass', tbn.play(n(m), 108), t, 0.9, corner[sd])
            M.add('brass', tbn.play(n(m) - 12, 100), t, 0.6, corner[sd])
            M.add('perc', cabasa.play(85), t + 0.04, 0.5, corner[sd])
            M.add('perc', guiro.play(70), t, 0.3, corner[sd])
    for b, m in TUNE_B:
        M.add('wind', clar.play(n(m), 96, dur=0.25), beat(b), 0.8, 0.15)
    sh = ['G4', 'Bb4', 'D5', 'Bb4', 'C5', 'Eb5', 'D5', 'Bb4']
    for k in range(32, 40):                 # the shimmy, in swung eighths
        for e, ee in enumerate((0, SW)):
            t = beat(k + ee)
            M.add('xylo', xylo.play(n(sh[(2 * (k - 32) + e) % 8]), 92), t, 0.7, 0.1)
            M.add('perc', tamb.play(70 + 20 * (e == 0)), t, 0.6)
    M.add('drums', sroll.play(70, dur=TCRACK - beat(40)), beat(40), 0.6)
    M.add('drums', troll.play(70, dur=TCRACK - beat(40)), beat(40), 0.5)
    for i in range(8):                      # the wind-up: reaching for the big pose
        t = beat(40 + i / 2)
        M.add('wind', bsn.play(n('D3') + i, 90 + 4 * i, dur=0.25), t, 0.9)
        M.add('wind', clar.play(n('D4') + i, 84 + 4 * i, dur=0.25), t, 0.7)
    # CRACK
    M.add('perc', slap.play(127), TCRACK, 1.0)
    M.add('perc', vibra.play(110), TCRACK + 0.02, 0.8)
    M.add('drums', bd.play(120), TCRACK, 1.0)
    M.add('drums', crash_s.play(110), TCRACK, 0.7)
    M.add('perc', cabasa.play(110), TCRACK + 0.05, 0.9, corner[-1])
    M.add('perc', cabasa.play(110), TCRACK + 0.07, 0.9, corner[1])
    M.add('brass', fall.play(105), TCRACK + 0.15, 0.8, dc)
    M.add('mallet', xylo.play(n('D5'), 70), TCRACK + 0.3, 0.6, corner[1])     # the loose end pops out

    # ---- 34.1-41: sheepish looks; the cat tiptoes in; he tries again; the cat creeps and pounces ----
    for t, d, m in ((35.9, -1, 'C3'), (36.8, 1, 'A2')):
        M.add('perc', guiro_l.play(65, dur=0.4), t - 0.3, 0.5, 0.5 * d)
        M.add('wind', bsn.play(n(m), 80, dur=0.25), t, 0.6, 0.5 * d)
    toes = ['D5', 'C5', 'Bb4', 'A4', 'G4', 'F#4', 'G4', 'A4', 'Bb4']
    for i, t in enumerate(cat_steps(P)):
        x = cat_x(P, t)
        M.add('strings', vpizz.play(n(toes[i % len(toes)]), 78), t, 0.8, pan_at(x))
    for k in range(int((TCROUCH - 37.8) / BEAT) + 1):   # his small sway, a soft vamp
        t = 37.8 + k * BEAT
        if t >= TCROUCH:
            break
        if k % 2 == 0:
            M.add('bass', tuba.play(n('G1' if k % 4 == 0 else 'D2'), 70), t)
            M.add('perc', guiro.play(55), t, 0.3, 0.3 if k % 4 == 0 else -0.3)
        else:
            for m in CHORD['Gm']:
                M.add('pizz', pizz.play(n(m), 60), t, 0.5, -0.3)
    xc = cat_x(P, TCROUCH)
    pc = pan_at(xc)
    M.add('strings', vpizz.play(n('G4'), 70), TCROUCH, 0.7, pc)
    M.add('strings', vpizz.play(n('C#5'), 60), TCROUCH + 0.4, 0.6, pc)
    t = 39.7
    while t < TPOUNCE - 0.02:               # the wiggle before the pounce, at its 6 Hz
        M.add('perc', wood.play(55), t, 0.35, pc)
        t += 1 / 6
    M.add('fx', slide(0.0, 0.15, 600, 1900, 0.2, 0.7), TPOUNCE, 0.9, pan_at(P['tip0']))
    M.add('perc', clave.play(115), TGRAB, 0.9, pan_at(P['tip0']))
    te = right_exit(P)
    M.add('perc', ratchet_f.play(100, dur=te - TGRAB + 0.3), TGRAB, 0.8, 0.6)
    M.add('fx', whoosh(te - TGRAB + 0.1, 600, 3000, 0.5, seed=5), TGRAB, 0.6, 0.75)
    M.add('perc', clave.play(100), te, 0.8, 0.85)
    M.add('drums', timp.play(110), TGRAB + 0.05, 0.7, dc)
    M.add('mallet', glock.play(n('A4'), 100), TGRAB + 0.05, 0.6, dc)
    M.add('mallet', glock.play(n('D#4'), 100), TGRAB + 0.05, 0.6, dc)

    # ---- 41-50: the spin. A whistle rides the spin rate; a tick each time his face comes round ----
    ts, phi = P['ts'], P['phi']
    rate = np.gradient(phi, DT)
    i0, i1 = nframes(TSPIN), nframes(TOFF + 0.2)
    ns = int((ts[i1] - ts[i0]) * SR)
    tt = ts[i0] + np.arange(ns) / SR
    r = np.interp(tt, ts, rate)
    f = 330 + 360 * r + 40 * np.sin(2 * np.pi * np.interp(tt, ts, phi))
    ph = 2 * np.pi * np.cumsum(f) / SR
    env = smoothstep(TSPIN, TSPIN + 0.6, tt) * (1 - smoothstep(TOFF - 0.3, TOFF + 0.1, tt))
    rngw = np.random.default_rng(3)
    breath = np.convolve(rngw.normal(0, 1, ns), np.ones(24) / 24, 'same') * 0.08
    wh = 0.28 * env * (np.sin(ph) + 0.12 * np.sin(2 * ph) + breath * (1 + np.sin(ph)))
    M.add('fx', np.vstack([wh, wh]), ts[i0], 0.9)
    scale = ['G4', 'A4', 'Bb4', 'C5', 'D5', 'Eb5', 'F#5', 'G5']
    ticks = spin_ticks(P)
    for i, t in enumerate(ticks):
        M.add('xylo', xylo.play(n(scale[i % len(scale)]), 100), t, 0.8, dc)
        M.add('perc', wood.play(90), t, 0.6, dc)
        M.add('perc', ratchet.play(70, dur=0.3), t, 0.35)
        M.add('perc', cabasa.play(70), t + 0.03, 0.4, corner[-1])
        M.add('perc', cabasa.play(70), t + 0.05, 0.4, corner[1])
    halves = np.nonzero(np.diff(np.floor(phi * 2)) > 0)[0] + 1
    for k, i in enumerate(halves):           # the band chases him, one oom or pah per half turn
        t = float(ts[i])
        c = ['Gm', 'D7'][(k // 4) % 2]
        if k % 2 == 0:
            M.add('bass', tuba.play(n(ROOT[c][(k // 2) % 2]), 96), t)
        else:
            for m in CHORD[c]:
                M.add('pizz', pizz.play(n(m), 84), t, 0.7, -0.3)
    M.add('fx', whoosh(left_arrive(P) - TLEFT, 500, 2600, 0.5, seed=8), TLEFT, 0.6, -0.7)
    M.add('perc', clave.play(105), left_arrive(P), 0.8, -0.85)
    M.add('drums', troll.play(60, dur=TOFF - 46.0), 46.0, 0.5)
    # the last of it comes off
    M.add('fx', whoosh(0.35, 800, 4000, 0.5, seed=9), TOFF - 0.3, 0.7, dc)
    M.add('perc', slap.play(110), TOFF, 0.8, dc)
    M.add('mallet', xylo.play(n('G5'), 80), TOFF, 0.6, dc)

    # ---- 51-57: tiny eyes, a drum roll, the boxers; he looks down, gulps and blushes ----
    for t in (TEYES, TEYES + 0.53, TEYES + 0.88):
        M.add('mallet', glock.play(n('D5'), 60), t, 0.45, dc)
    M.add('drums', sroll.play(85, dur=TREVEAL - 51.6), 51.6, 0.7)
    M.add('drums', crash.play(110), TREVEAL, 0.8)
    M.add('drums', bd.play(115), TREVEAL, 0.9)
    M.add('drums', rim.play(110), TREVEAL, 0.7)
    M.add('brass', tpt.play(n('D4'), 105, dur=0.14), TREVEAL - 0.16, 0.8)
    for m in ('G4', 'B4', 'D5'):            # ta-da, in the major
        M.add('brass', tpt.play(n(m), 115, dur=0.7), TREVEAL, 0.8)
    M.add('fx', slide(0.0, 0.18, 900, 1900, 0.22, 0.6), TREVEAL + 0.7, 0.9)        # wolf whistle
    M.add('fx', slide(0.05, 0.55, 2000, 800, 0.62, 0.6),
          TREVEAL + 1.02, 0.9)
    for t, d, m in ((53.3, -1, 'D3'), (54.3, 1, 'Eb3')):
        M.add('wind', bsn.play(n(m), 82, dur=0.35), t, 0.7, corner[d])
    M.add('fx', slide(0.0, 0.25, 700, 300, 0.3, 0.6), 55.55, 0.9, dc)            # gulp
    M.add('drums', timp.play(80, pitch=4), 55.8, 0.5, dc)
    for i, m in enumerate(('G4', 'B4', 'D5', 'G5', 'B5')):
        M.add('strings', harp.play(n(m), 75), TBLUSH + 0.06 * i, 0.6, dc)
    M.add('perc', tri.play(80), TBLUSH + 0.3, 0.5, dc)
    M.add('wind', bsn.play(n('D3'), 90, dur=0.15), 57.0, 0.8, dc)                # shrug: eh
    M.add('wind', bsn.play(n('G3'), 90, dur=0.15), 57.15, 0.8, dc)

    # ---- 57.2-66: the boxer dance, G major; the wrapped house steps along on the second half ----
    oompah(0, 16, PROG_F, TF, 96)
    for k in range(16):
        t = beat(k, TF)
        if k % 2:
            M.add('drums', snare.play(85), t, 0.6)
        for e in (0, SW):
            M.add('perc', tamb.play(60 + 25 * (e == 0)), t + e * BEAT, 0.45)
        sd = -1 if k % 2 == 0 else 1
        c = PROG_F[(k // 4) % 4]
        M.add('brass', tbn.play(n(CHORD[c][1]), 104), t, 0.6, corner[sd])
        if k >= 8:
            M.add('perc', wood.play(95), t, 0.6, -0.8)
            M.add('perc', wood.play(95), t, 0.6, 0.8)
    for b, m in TUNE_F:
        M.add('wind', clar.play(n(m), 104, dur=0.3), beat(b, TF), 1.0, 0.1)
        M.add('xylo', xylo.play(n(m), 90), beat(b, TF), 0.5, 0.1)
    # final hit
    M.add('drums', crash.play(118), TFIN, 0.9)
    M.add('drums', bd.play(120), TFIN, 1.0)
    M.add('bass', tuba.play(n('G1'), 120), TFIN)
    M.add('bass', tuba.play(n('G2'), 115), TFIN, 0.7)
    for m in ('G3', 'B3', 'D4', 'G4'):
        M.add('brass', tpt.play(n(m), 112, dur=0.6), TFIN, 0.7)
        M.add('xylo', xylo.play(n(m) + 12, 110), TFIN, 0.5)
        M.add('pizz', pizz.play(n(m), 110), TFIN, 0.7, -0.3)

    # ---- 66.8-72: the cat is back; he notices; a wink ----
    M.add('strings', vpizz.play(n('D5'), 75), TPEEK + 0.1, 0.7, 0.85)
    M.add('strings', vpizz.play(n('G5'), 75), TPEEK + 0.3, 0.7, 0.85)
    M.add('wind', bsn.play(n('A2'), 80, dur=0.3), 67.5, 0.7, 0.3)
    M.add('mallet', glock.play(n('G4'), 55), 68.0, 0.4, 0.85)
    M.add('mallet', glock.play(n('D5'), 85), TWINK, 0.6, dc)
    M.add('perc', tri.play(95), TWINK, 0.6, dc)
    M.add('pizz', pizz.play(n('G2'), 90), 69.2, 0.8)
    M.add('bass', tuba.play(n('G1'), 80), 69.2, 0.8)
