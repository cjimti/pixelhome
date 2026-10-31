"""Parade: A street parade marches along the roofline on a 120 BPM brass band. The drum line steps in from
the free end of Right as coloured stripes that fill the house a step per beat. A giant ribbed pumpkin
balloon rolls in from Right across the whole front; a gust blows it back, the handlers haul it on, and it
rolls away up the Side. An ear of corn grows out of the porch a chunk per beat, sways round the porch to
the clarinets while the wings ripple on the afterbeats, then heats up and pops: popcorn flies out to both
ends, faster and faster, until the cob is gone. The band struts in mirrored chevrons and claps. Then the
turkey waddles in from Right, a step and a tail-fan flare per beat, stops on the porch and gobbles; the
band answers. Someone starts pumping: each pump races down the Right wing into him and he swells, his
stress stripes tightening, past a hiccup and a faster pumping, until he fills the porch and both wings,
holds one frozen beat, and pops. Confetti flies out to both free ends, his untied head zigzags the whole
house blowing raspberries and shoots out the end of Right, and the band marches off in full colour."""
import numpy as np
from pixelhome.fx import DT, hexc, light, perc, keys, smoothstep, lerp, Flicker, nframes

CODE = 'TG04'
TITLE = 'Parade'
KIND = 'show'
DESCRIPTION = ('A brass band marches along the roof with giant balloons: a rolling pumpkin, an ear of corn that pops, '
               'and a turkey pumped up until he bursts and his untied head zooms round the house.')
VOICEOVER = "Grab a blanket and a cocoa: the parade is coming down our street."

PUMPKIN = hexc('#ff5200')
AMBER = hexc('#ff8a18')
GOLD = hexc('#ffb000')
CRANBERRY = hexc('#c0102a')
WARM = hexc('#ffc27a')
CREAM = hexc('#ffe0b0')
BROWN = hexc('#8a3208')
DEEP = hexc('#4a1604')
HUSK = hexc('#9a8a10')
STRIPES = np.array([CRANBERRY, GOLD, PUMPKIN, AMBER])
FAN = np.array([CRANBERRY, GOLD, AMBER, PUMPKIN, GOLD, AMBER, CRANBERRY])

BEAT = 0.5                                  # 120 BPM, four to a bar
BAR = 4 * BEAT
D = 90.0
SEED = 24


def at(bar, beat=0.0):
    return bar * BAR + beat * BEAT


# the running order (seconds)
T_PUMP, T_GUST, T_GUST1, T_PGONE = at(4), at(8), at(10), at(12.5)          # pumpkin
T_CORN, T_SWAY, T_POPC, T_COBGONE = at(13), at(15), at(19), at(22)         # corn and popcorn
T_STRUT, T_CLAP = at(22), at(25)                                           # the band struts, then claps
T_TURK, T_STOP, T_PUMPUP = at(26), at(31), at(33)                          # turkey: walks, stops, pumped
T_HIC, T_FAST, T_HOLD, T_LAST, T_BANG = at(35.5), at(35.75), at(37.25), at(37.75), at(38)
T_FIN, T_SWEEP, T_CHORD = at(41), at(43), at(44)
GOBBLES = (at(31, 1), at(32, 1))            # he gobbles, the band answers a beat and a half later
ANSWERS = (at(31, 3), at(32, 3))
MID = 1486.0                                # middle of the Porch Front on the path
R0, RMAX = 110.0, 800.0                     # turkey body radius walking, and at the pop


def pumps():
    """(time, radius gain, ease) for every pump of air: beats, a hiccup back, eighths, a last creak."""
    ev = [(T_PUMPUP + k * BEAT, 36.0, 0.12) for k in range(10)]
    ev.append((T_HIC, -90.0, 0.3))
    ev += [(T_FAST + k * BEAT / 2, (RMAX - 40 - 470 + 90) / 12, 0.08) for k in range(12)]
    ev.append((T_LAST, 40.0, 0.45))
    return ev


PUMPS = pumps()


def radius(t):
    r = R0
    for tp, dr, e in PUMPS:
        r += dr * smoothstep(tp, tp + e, t)
    return r


def pumpkin_c(t):
    """The pumpkin's centre on the path: in from Right, blown back by the gust, hauled on, away up the Side."""
    return keys(t, [(T_PUMP, 2800), (at(7.5), 1450), (T_GUST, 1420), (at(9), 1950), (at(9.5), 1880),
                    (T_GUST1, 1700), (at(11), 1250), (T_PGONE, -320)])


def turkey_c(t):
    """Turkey centre: a step per beat from past the end of Right to the middle of the porch."""
    if t < T_TURK:
        return 2620.0
    k = (t - T_TURK) / BEAT
    steps = min(20.0, np.floor(k) + smoothstep(0, 0.45, k % 1))
    return 2620.0 - (2620.0 - MID) * steps / 20


def head_track():
    """(time, path distance) of the untied head after the pop: zigzag the house, then out the end of Right."""
    return [(T_BANG, MID - RMAX - 40), (at(38.6), 2250), (at(39.1), 760), (at(39.55), 2050), (at(39.95), 1050),
            (at(40.3), 1750), (at(40.55), 1350), (at(41), 2700)]


HEAD = head_track()


def popcorn(rng):
    """Pop times (quantised to the music, faster and faster), where on the cob, and the flight of each kernel."""
    ts = []
    for k in range(int((T_COBGONE - T_POPC) / (BEAT / 4))):
        t = T_POPC + k * BEAT / 4
        u = (t - T_POPC) / (T_COBGONE - T_POPC)
        if rng.random() < 0.12 + 0.9 * u ** 1.5:
            ts.append(t)
    ts += list(T_COBGONE - BEAT + np.arange(8) * BEAT / 8)                    # the last flurry
    ts = np.array(sorted(ts))
    n = len(ts)
    where = rng.uniform(-430, 430, n)
    vel = np.sign(where + rng.normal(0, 150, n)) * rng.uniform(500, 1600, n)
    col = rng.integers(0, 3, n)
    return ts, where, vel, col


def confetti(rng, n=240):
    p0 = rng.uniform(-RMAX, RMAX, n)
    v = np.sign(p0) * rng.uniform(400, 1900, n)
    return MID + p0, v, rng.uniform(1.6, 3.2, n), rng.integers(0, 5, n), rng.uniform(2, 6, n)


def render(G, seed=SEED):
    rng = np.random.default_rng(seed)
    F = nframes(D)
    out = np.zeros((F, G.N, 3))
    n = G.N
    d = G.pd[G.path]
    X = G.pos[G.path, 0]
    side = np.arange(n) < 81
    left = (np.arange(n) >= 81) & (np.arange(n) < 179)
    right = np.arange(n) >= 381
    porch = (np.arange(n) >= 179) & (np.arange(n) < 381)
    wings = left | right
    m = np.abs(X - 16.0)                                     # distance out from the facade's mirror line
    m[side] = 612 + (d[80] - d[side])
    crowd = Flicker(rng, n, 0.2, 1.0)
    shimmer = Flicker(rng, n, 2.0, 7.0)
    pt, pw, pv, pc = popcorn(rng)
    cf_p, cf_v, cf_life, cf_k, cf_tw = confetti(rng)
    cf_cols = np.array([GOLD, CRANBERRY, WARM, PUMPKIN, AMBER])
    pop_cols = np.array([CREAM, WARM, GOLD])
    gust = rng.uniform(0, 2512, 10), rng.uniform(1300, 2200, 10), rng.uniform(0, 3.5, 10)
    ht = np.array([h[0] for h in HEAD])
    hd = np.array([h[1] for h in HEAD])

    def pulse(t, width=0.16, per=BEAT):          # a decaying hit on every beat
        return np.exp(-((t % per) / width))

    def stripes(t, level, width=80.0, cols=STRIPES, step=0.5):
        k = t / BEAT
        s = d + (np.floor(k) + smoothstep(0, 0.35, k % 1)) * width * step
        idx = np.floor(s / width).astype(int) % len(cols)
        shape = np.sin(np.pi * ((s / width) % 1)) ** 0.8
        return light(1.0, level * shape) * cols[idx]

    def blob(c, R, soft=10.0):
        u = (d - c) / max(R, 1.0)
        inside = np.clip((1 - np.abs(u)) * R / soft, 0, 1)
        return inside, u

    def ripple(t, t0, origin, direction, col, level=0.8, speed=900.0, reach=480.0):
        a = t - t0
        if not 0 <= a < reach / speed + 0.3:
            return 0
        front = origin + direction * speed * a
        mask = (direction * (d - origin) >= 0) & (direction * (d - origin) <= reach)
        return light(col, level * np.exp(-((d - front) / 55) ** 2) * mask * np.exp(-a / 0.6))

    for f in range(F):
        t = f * DT
        buf = np.zeros((n, 3))
        bt = (t / BEAT) % 4                                  # beat in the bar
        beat = pulse(t)
        down = pulse(t, 0.25, BAR)

        # ---- 0-8: the drum line steps in from the free end of Right, a stripe per beat ----
        if t < T_PUMP:
            edge = 2620 - 170 * (np.floor(t / BEAT) + smoothstep(0, 0.35, (t / BEAT) % 1))
            fill = np.clip((d - edge) / 30, 0, 1)
            buf += stripes(t, 0.55 + 0.35 * beat + 0.1 * down, 72) * fill[:, None]
            if t >= at(2):                                   # bars 2-3: the wings answer each other on the beat
                k = int(t / BEAT)
                buf += light(GOLD, 0.75 * beat * (right if k % 2 else left))
        # a street of stripes under everything after that, breathing on the beat
        elif t < T_FIN:
            lvl = 0.3 + 0.14 * beat
            if T_HOLD <= t < T_BANG + 1.5:
                lvl = 0.0
            elif T_PUMPUP <= t < T_HOLD:
                lvl *= 0.6
            buf += stripes(t, lvl * smoothstep(T_PUMP - 0.5, T_PUMP + 1.0, t))
            buf += light(DEEP, 0.08 * (1 + 0.3 * crowd(t)))

        # ---- 8-25: the pumpkin rolls in from Right, is blown back, hauled on, and rolls off up the Side ----
        if T_PUMP <= t < T_PGONE + 0.5:
            c = pumpkin_c(t)
            R = 280 * (1 + 0.06 * beat)                      # it bounces on the beat
            if T_GUST <= t < T_GUST1:                        # squashed by the wind
                R *= 1 + 0.12 * np.sin(2 * np.pi * 3 * (t - T_GUST)) * np.exp(-(t - T_GUST) / 1.5)
            inside, u = blob(c, R)
            th = np.arcsin(np.clip(u, -1, 1))
            spin = (2800 - c) / 280
            groove = np.exp(-(((10 * th - spin * 3 + np.pi) % (2 * np.pi) - np.pi) / 0.55) ** 2)
            chord = np.sqrt(np.clip(1 - u ** 2, 0, 1))
            buf *= (1 - inside)[:, None]
            buf += light(PUMPKIN, inside * (0.55 + 0.45 * chord) * (1 - 0.75 * groove))
            buf += light(GOLD, 0.6 * inside * np.exp(-((u + 0.35) / 0.18) ** 2))
            buf += light(BROWN, 0.85 * np.exp(-((d - (c - R - 22)) / 14) ** 2))       # the stem leads
        if T_GUST <= t < T_GUST1 + 0.5:                      # the gust: streaks blowing right along the house
            a = t - T_GUST
            for p0, v, dl in zip(*gust):
                x = (p0 + v * (a - dl)) % 2700
                if a > dl:
                    buf += light(WARM, 0.5 * np.exp(-((d - x) / 40) ** 2) * smoothstep(0, 0.3, a - dl)
                                 * (1 - smoothstep(T_GUST1 - T_GUST - 0.5, T_GUST1 - T_GUST + 0.5, a)))

        # ---- 26-44: the corn grows out of the porch, sways, heats up, pops ----
        if T_CORN <= t < T_COBGONE:
            k = (t - T_CORN) / BEAT
            half = 560 * min(1.0, (np.floor(k) + smoothstep(0, 0.4, k % 1)) / 8)     # a chunk per beat
            sway = 90 * np.sin(2 * np.pi * (t - T_SWAY) / (2 * BAR)) * smoothstep(T_SWAY - 1, T_SWAY, t)
            heat = smoothstep(T_POPC, T_COBGONE, t)
            c = MID - 24 + sway + rng.normal(0, 6 * heat)
            inside, u = blob(c, half + 1, 8)
            roll = 40 * t
            kern = (0.5 + 0.5 * np.cos(2 * np.pi * (d - c + roll) / 22)) ** 0.6
            row = (np.floor((d - c + roll) / 44) % 2)[:, None]
            col = lerp(lerp(GOLD, hexc('#ffd000'), row), WARM, heat)
            left_pop = 1 - 0.85 * heat ** 2
            buf *= (1 - inside)[:, None]
            buf += light(1.0, inside * (0.45 + 0.5 * kern) * left_pop * (1 + 0.3 * heat * shimmer(t))) * col
            for e in (-1, 1):                                # husk tufts at the ends
                buf += light(HUSK, 0.8 * (1 - heat) * np.exp(-((d - (c + e * (half + 25))) / 22) ** 2) * (half > 50))
        if T_SWAY <= t < T_POPC:                             # the wings ripple out from the porch on 2 and 4
            for b in range(int((T_POPC - T_SWAY) / BEAT)):
                if b % 2 == 1:
                    tb = T_SWAY + b * BEAT
                    buf += ripple(t, tb, 892, -1, GOLD, 1.0, 1100, 900)
                    buf += ripple(t, tb, 2036, 1, GOLD, 1.0, 1100, 520)
                    buf += ripple(t, tb, 892, 1, AMBER, 0.4, 600, 120) + ripple(t, tb, 2036, -1, AMBER, 0.4, 600, 120)
        if T_POPC <= t < T_COBGONE + 2.5:                    # popcorn: a flash, and a kernel flying out
            live = (t >= pt) & (t < T_COBGONE + 1.2 + 0.0 * pt)
            if live.any():
                a = t - pt[live]
                x0 = MID - 24 + pw[live]
                x = x0 + pv[live] * 0.7 * (1 - np.exp(-a / 0.7))
                lv = 0.55 + 0.45 * np.exp(-a / 0.4)
                fl = np.exp(-a / 0.07)
                I = lv[:, None] * np.exp(-((d[None] - x[:, None]) / 9) ** 2)
                I *= 1 - smoothstep(T_COBGONE, T_COBGONE + 1.2, t)
                buf += (perc(I)[..., None] * pop_cols[pc[live]][:, None, :]).sum(0)
                buf += light(CREAM, np.clip((fl[:, None] * np.exp(-((d[None] - x0[:, None]) / 22) ** 2)).sum(0), 0, 1))
        if T_COBGONE <= t < T_COBGONE + 0.6:                 # ta-da: the porch flashes where the cob was
            buf += light(WARM, 0.8 * np.exp(-(t - T_COBGONE) / 0.15) * porch)

        # ---- 44-52: the band struts in mirrored chevrons marching inward; then it claps ----
        if T_STRUT <= t < T_TURK:
            k = (t - T_STRUT) / BEAT
            s = m + (np.floor(k) + smoothstep(0, 0.35, k % 1)) * 60
            bar = int((t - T_STRUT) / BAR)
            shape = np.sin(np.pi * ((s / 120) % 1)) ** 1.2
            ci = (np.floor(s / 120).astype(int) + bar) % 4
            lv = 0.55 + 0.4 * beat
            if t >= T_CLAP:                                  # stop time: the house claps on 2 and 4
                b = int((t - T_CLAP) / BEAT)
                lv = 0.25
                buf += light(GOLD, 0.95 * beat * (1.0 if b % 2 else 0.0) * np.ones(n))
                buf += light(CRANBERRY, 0.8 * beat * (0.0 if b % 2 else 1.0) * porch)
            buf += light(1.0, lv * shape) * STRIPES[ci]

        # ---- 52-76: the turkey ----
        if T_TURK <= t < T_BANG:
            c = turkey_c(t)
            R = radius(t)
            strain = np.clip((R - R0) / (RMAX - R0), 0, 1)
            walking = t < T_STOP
            fan_open = (0.55 + 0.45 * beat) if walking else 0.7 + 0.3 * strain
            # tail fan behind him (toward Right), seven feathers
            span = (260 + 0.5 * R) * fan_open
            v = (d - (c + R * 0.6)) / span
            on = (v > 0) & (v < 1)
            fi = np.clip((v * 7).astype(int), 0, 6)
            feather = np.sin(np.pi * ((v * 7) % 1)) ** 0.7 * on
            buf *= (1 - 0.9 * on)[:, None]
            buf += light(1.0, 0.85 * feather * (1 - 0.4 * strain)) * FAN[fi]
            # body: brown, then hot and striped as he strains
            inside, u = blob(c, R)
            lam = lerp(140, 26, strain)
            fr = lerp(1.5, 13, strain)
            stress = 0.5 + 0.5 * np.cos(2 * np.pi * (d - c) / lam + 2 * np.pi * fr * t * (1 if strain > 0 else 0))
            colr = lerp(lerp(BROWN, PUMPKIN, smoothstep(0, 0.5, strain)), GOLD, smoothstep(0.5, 1, strain))
            if T_HOLD <= t:                                  # the frozen beat: white-hot, humming
                colr = lerp(GOLD, WARM, smoothstep(T_HOLD, T_BANG, t))
            I = inside * (0.55 + 0.4 * np.sqrt(np.clip(1 - u ** 2, 0, 1))) * (1 - 0.55 * strain * stress)
            if strain > 0:
                I = I * (1 + 0.12 * strain * shimmer(t))
            buf *= (1 - inside)[:, None]
            buf += light(colr, np.clip(I, 0, 1.1))
            # head ahead of him: thrusts forward on every step, flickers when he gobbles
            bob = 30 * beat if walking else 0
            hx = c - R - 34 - bob
            hv = 0.95
            for g in GOBBLES:
                if g <= t < g + 0.9:
                    hv = 0.4 + 0.6 * (np.sin(2 * np.pi * 9 * (t - g)) > 0)
            buf += light(CRANBERRY, hv * np.exp(-((d - hx) / 15) ** 2))
            buf += light(hexc('#ff2010'), 0.7 * np.exp(-((d - hx - 18) / 7) ** 2))          # wattle
            if walking:                                      # footsteps: a ripple each way from his feet
                k = int((t - T_TURK) / BEAT)
                tb = T_TURK + k * BEAT
                fx = turkey_c(tb + 0.2)
                buf += ripple(t, tb, fx - R0, -1, AMBER, 0.55, 800, 350)
                buf += ripple(t, tb, fx + R0, 1, AMBER, 0.35, 800, 250)
            for g in ANSWERS:                                # the band answers: wings flash cranberry
                a = t - g
                if 0 <= a < 0.6:
                    buf += light(CRANBERRY, 0.95 * np.exp(-a / 0.2) * (wings | side))
            # each pump of air races down the Right wing from its free end into him
            for tp, dr, e in PUMPS:
                if dr <= 0:
                    continue
                edge = c + R
                t0 = tp - (2560 - edge) / 2600
                if t0 <= t < tp + 0.05:
                    x = 2560 - 2600 * (t - t0)
                    buf += light(WARM, 0.95 * np.exp(-((d - x) / 26) ** 2) * (d > edge - 10))
            if T_HIC <= t < T_HIC + 0.6:                     # the hiccup: a shiver of escaping air
                a = t - T_HIC
                buf += light(CREAM, 0.6 * np.exp(-a / 0.2) * np.exp(-((d - (c - R)) / 40) ** 2))

        # ---- 76: POP. A flash, two shock fronts, confetti out to both free ends ----
        if T_BANG <= t < T_FIN + 1.0:
            a = t - T_BANG
            inside, _ = blob(MID, RMAX)
            buf += light(WARM, 1.0 * np.exp(-a / 0.1) * inside)
            for e in (-1, 1):
                front = MID + e * (RMAX + 1800 * a)
                buf += light(GOLD, 0.95 * np.exp(-a / 0.8) * np.exp(-((d - front) / 50) ** 2))
            live = a < cf_life
            if live.any():
                x = cf_p[live] + cf_v[live] * 0.9 * (1 - np.exp(-a / 0.9))
                tw = 0.55 + 0.45 * np.cos(2 * np.pi * cf_tw[live] * a) ** 2
                lv = tw * np.clip(1 - a / cf_life[live], 0, 1) ** 0.7
                I = lv[:, None] * np.exp(-((d[None] - x[:, None]) / 5) ** 2)
                buf += (perc(np.clip(I, 0, 1))[..., None] * cf_cols[cf_k[live]][:, None, :]).sum(0)
            # the untied head: zigzags the length of the house blowing raspberries, and shoots out the end
            if t < ht[-1] + 0.2:
                for k in range(16):
                    tk = t - 0.025 * k
                    if tk < T_BANG:
                        break
                    x = keys(tk, HEAD)
                    w = 24 if k == 0 else 12
                    col = hexc('#ff1020') if k == 0 else WARM
                    buf += light(col, (1.0 if k == 0 else 0.6 * (1 - k / 16)) * np.exp(-((d - x) / w) ** 2))
                for th in ht[1:-1]:                          # a puff at every turn
                    a2 = t - th
                    if 0 <= a2 < 0.5:
                        buf += light(CREAM, 0.7 * np.exp(-a2 / 0.15) * np.exp(-((d - np.interp(th, ht, hd)) / 45) ** 2))
            # the band picks up: stripes come back from the porch out
            if t >= at(40):
                buf += stripes(t, 0.35 * smoothstep(at(40), T_FIN, t)) * (np.abs(d - MID) < 1400 *
                                                                             smoothstep(at(40), T_FIN, t))[:, None]

        # ---- 82-90: the band marches off in full colour; a sweep round the outline; the last chord ----
        if t >= T_FIN:
            fade = 1 - smoothstep(T_CHORD + 0.8, D, t)
            if t < T_CHORD:
                buf += stripes(t, (0.6 + 0.35 * beat + 0.1 * down) * fade, 96, STRIPES[[2, 1, 0]])
            if T_SWEEP <= t < T_CHORD + 0.5:
                k = (t - T_SWEEP) / (BEAT / 2)
                front = 2620 - 2700 * min(1.0, (np.floor(k) + smoothstep(0, 0.5, k % 1)) / 8)
                buf += light(WARM, 0.95 * np.exp(-((d - front) / 60) ** 2))
                buf += light(GOLD, 0.45 * (d > front))
            if t >= T_CHORD:
                a = t - T_CHORD
                buf += light(GOLD, (0.85 * np.exp(-a / 0.4) + 0.45) * fade * np.ones(n))
                buf += stripes(t, 0.35 * fade, 120, STRIPES[[2, 1, 0]])
        out[f][G.path] = np.clip(buf, 0, 1)
    return out


# ---------------------------------------------------------------- music ----------------------------------------------
# An original street march in Bb at 120 BPM, two beats of oom-pah to the bar's four: tuba on 1 and 3, horns pah on
# 2 and 4, marching snare and bass drum, trumpets and glock on the tune. The drum line alone brings the stripes in
# (bass drums panned to whichever wing flashes). The pumpkin gets the A strain and a marimba that spins round the
# chord with it; the gust a whoosh and a slide whistle up as it is blown back. The corn grows up a xylophone scale a
# step a beat, sways on the clarinet B strain (the wings' ripples are the horns' afterbeats), and pops: every kernel
# is a click where it pops, faster and faster, to a slapstick at the end. The band struts tutti and stops for the
# claps. The turkey's trio is in Eb, a log drum on every step; he stops, gobbles on bassoon and the brass answer.
# Each pump is a tuba note and a hiss, a whistle rides his radius, a horn climbs, the hiccup is a trombone fall;
# then a frozen beat of silence and the pop: the whole kit, a raspberry that follows his head round the house, glock
# confetti; and the band marches off on the A strain to a big Bb.

CH = {'Bb': (58, 62, 65), 'Eb': (58, 63, 67), 'F': (57, 60, 65), 'F7': (57, 60, 63), 'C7': (55, 58, 64),
      'Gm': (58, 62, 67), 'Bb7': (56, 62, 65), 'Ab': (56, 60, 63), 'C': (55, 60, 64)}
BASS = {'Bb': ('Bb1', 'F2'), 'Eb': ('Eb2', 'Bb1'), 'F': ('F2', 'C2'), 'F7': ('F2', 'C2'), 'C7': ('C2', 'G1'),
        'Gm': ('G1', 'D2'), 'Bb7': ('Bb1', 'F2'), 'Ab': ('Ab1', 'Eb2'), 'C': ('C2', 'G1')}
# tunes: per bar, (beat, note, beats)
TUNE_A = [[(0, 'F4', 1), (1, 'Bb4', 1), (2, 'D5', 1), (3, 'F5', 1)],
          [(0, 'G5', 1.5), (1.5, 'F5', 0.5), (2, 'D5', 1), (3, 'Bb4', 1)],
          [(0, 'C5', 1), (1, 'Eb5', 1), (2, 'A4', 1), (3, 'C5', 1)],
          [(0, 'Bb4', 2), (2, 'F4', 1), (3, 'F4', 1)],
          [(0, 'F4', 1), (1, 'Bb4', 1), (2, 'D5', 1), (3, 'F5', 1)],
          [(0, 'G5', 1), (1, 'A5', 0.5), (1.5, 'G5', 0.5), (2, 'F5', 1), (3, 'D5', 1)],
          [(0, 'Eb5', 1), (1, 'C5', 1), (2, 'A4', 1), (3, 'F4', 1)],
          [(0, 'Bb4', 2), (2, 'Bb4', 0.5), (2.5, 'Bb4', 0.5)]]
CHORDS_A = ['Bb', 'Eb', 'F7', 'Bb', 'Bb', 'Eb', 'F7', 'Bb']
TUNE_B = [[(0, 'A4', 0.5), (0.5, 'C5', 0.5), (1, 'F5', 1), (2, 'E5', 0.5), (2.5, 'F5', 0.5), (3, 'C5', 1)],
          [(0, 'Bb4', 0.5), (0.5, 'C5', 0.5), (1, 'E5', 1), (2, 'G4', 1), (3, 'Bb4', 1)],
          [(0, 'A4', 0.5), (0.5, 'C5', 0.5), (1, 'F5', 1), (2, 'A5', 1), (3, 'F5', 1)],
          [(0, 'C5', 3)],
          [(0, 'D5', 0.5), (0.5, 'F5', 0.5), (1, 'Bb5', 1), (2, 'A5', 0.5), (2.5, 'G5', 0.5), (3, 'F5', 1)],
          [(0, 'C5', 0.5), (0.5, 'F5', 0.5), (1, 'A5', 1), (2, 'F5', 1), (3, 'C5', 1)],
          [(0, 'Bb4', 0.5), (0.5, 'D5', 0.5), (1, 'G5', 1), (2, 'E5', 1), (3, 'C5', 1)],
          [(0, 'F5', 2), (2, 'F4', 1)]]
CHORDS_B = ['F', 'C7', 'F', 'F', 'Bb', 'F', 'C7', 'F']
TUNE_T = [[(0, 'G4', 1), (1, 'Bb4', 0.5), (1.5, 'G4', 0.5), (2, 'Eb4', 1), (3, 'G4', 1)],
          [(0, 'F4', 1), (1, 'Ab4', 0.5), (1.5, 'F4', 0.5), (2, 'D4', 1), (3, 'F4', 1)],
          [(0, 'Ab4', 1), (1, 'Bb4', 0.5), (1.5, 'Ab4', 0.5), (2, 'F4', 1), (3, 'D4', 1)],
          [(0, 'Eb4', 1), (1, 'G4', 1), (2, 'Bb4', 1), (3, 'Eb5', 1)],
          [(0, 'C5', 1), (1, 'Ab4', 1), (2, 'Bb4', 1), (3, 'D5', 1)]]
CHORDS_T = ['Eb', 'Bb7', 'Bb7', 'Eb', 'Ab']


def score(M, G):
    from pixelhome.audio import SR, note, whoosh, slide
    n = note
    rng = np.random.default_rng(SEED)        # the same draws as render(): flickers, then the popcorn
    Flicker(rng, G.N, 0.2, 1.0)
    Flicker(rng, G.N, 2.0, 7.0)
    pt, pw, pv, pc = popcorn(rng)

    tpt = M.sampler('Brass/Trumpet/stac/*.wav', tune=-12)
    tpt_s = M.sampler('Brass/Trumpet/sus/*.wav', tune=-12)
    horn = M.sampler('Brass/F Horn/stac/*.wav', tune=-12)
    horn_s = M.sampler('Brass/F Horn/sus/*.wav', tune=-12)
    bone = M.sampler('Brass/Tenor Trombone/sus/*.wav', tune=-12)
    tuba = M.sampler('Brass/Tuba/stac/*.wav', tune=-12)
    tuba_s = M.sampler('Brass/Tuba/sus/*.wav', tune=-12)
    glock = M.sampler('Percussion/Glock/*.wav', tune=-12)
    mar = M.sampler('Percussion/Marimba/*.wav', tune=-12)
    xylo = M.sampler('Percussion/Xylo/*.wav', tune=-12)
    clar = M.sampler('Woodwinds/Clarinet/stac/*.wav', tune=-12)
    bsn = M.sampler('Woodwinds/Bassoon/stac/*.wav', tune=-12)
    trem = M.sampler('Strings/Cello Section/trem/*.wav', tune=-12)
    snare = M.hits('VSCO 1 Percussion/drums/snare/drum3_marching/snare3_[mp]*.wav')
    snare_f = M.hits('VSCO 1 Percussion/drums/snare/drum3_marching/snare3_f*.wav')
    rim = M.hits('VSCO 1 Percussion/drums/snare/drum3_marching/snare3_rimshot*.wav')
    sroll = M.hits('Percussion/Snare2-rollSN_v[35]*.wav')
    bd = M.hits('VSCO 1 Percussion/drums/bass/bdrum_f_*.wav')
    bd_ff = M.hits('VSCO 1 Percussion/drums/bass/bdrum_fff_*.wav')
    tenor = M.hits('VSCO 1 Percussion/drums/tenor/tenor_lower/tenor_f*.wav')
    clash = M.hits('VSCO 1 Percussion/varMetal/Cymbals/clash/crash_hit_ff*.wav')
    clash_f = M.hits('VSCO 1 Percussion/varMetal/Cymbals/clash/crash_hit_fff*.wav')
    choke = M.hits('Percussion/cymbal-crashshort*.wav')
    ccresc = M.hits('Percussion/susCymb1-cresc-Short*.wav')
    timp = M.hits('Percussion/Timpani/Timpani1_Hit*.wav')
    troll = M.hits('Percussion/Timpani/Rolls/Timpani1_Roll*.wav')
    wood = M.hits('VSCO 1 Percussion/varWood/claves_m*.wav')
    click = M.hits('VSCO 1 Percussion/varWood/wood_click*.wav')
    log = M.hits('Percussion/LogDrum*_MedM_v2*.wav')
    slap = M.hits('VSCO 1 Percussion/varWood/slapstick[0-9].wav')
    fall = M.hits('Brass/OldTrombone/Fall/Trombone_Fall_F2*.wav')
    tri = M.hits('Percussion/Triangle3-Hit_v1*.wav')

    for name, gain, rev in (('tune', 0.34, 0.18), ('horns', 0.24, 0.2), ('bass', 0.42, 0.06), ('drums', 0.36, 0.12),
                            ('motif', 0.34, 0.2), ('perc', 0.42, 0.12), ('fx', 0.26, 0.2), ('hold', 0.2, 0.3)):
        M.bus(name, gain=0.92 * gain, reverb=rev)

    order = np.argsort(G.pd)
    xs, ds = G.pos[order, 0], G.pd[order]
    x0, x1 = xs.min(), xs.max()
    L = G.length

    def pan_at(dd):                          # path distance -> left/right across the facade, as seen from the street
        x = np.interp(np.clip(dd, 0, L), ds, xs)
        return 0.85 * (2 * (x - x0) / (x1 - x0) - 1)

    def mono(sig, pans):                     # a mono signal panned sample by sample
        a = (np.clip(pans, -1, 1) + 1) * np.pi / 4
        return np.vstack([sig * np.cos(a), sig * np.sin(a)]) * np.sqrt(2)

    def tone(fr, amp, buzz=0.12):            # a whistle (or with buzz up, a raspberry) along a frequency curve
        ph = 2 * np.pi * np.cumsum(fr) / SR
        noise = np.convolve(M.rng.normal(0, 1, len(fr)), np.ones(24) / 24, 'same')
        return amp * (np.sin(ph) + buzz * np.sin(2 * ph) + 0.6 * buzz * np.sin(3 * ph) + 0.08 * noise * (1 + np.sin(ph)))

    def tune(bars, k0, inst, bus='tune', vel=100, pan=0.0, long=None, gain=1.0, octave=0):
        for j, b in enumerate(bars):
            for e, m, ln in b:
                pl = long if (long is not None and ln >= 1.5) else inst
                t = at(k0 + j, e)
                M.add(bus, pl.play(n(m) + octave, vel, dur=ln * BEAT * 0.9), t, gain, pan(t) if callable(pan) else pan)

    def band(k0, chords, vel=100, horns=True, snares=True, gain=1.0):
        for j, c in enumerate(chords):
            k = k0 + j
            for e in (0, 2):
                M.add('bass', tuba.play(n(BASS[c][e // 2]), vel), at(k, e), gain)
                M.add('drums', bd.play(vel), at(k, e), 0.9 * gain)
            if horns:
                for e in (1, 3):
                    for mm in CH[c]:
                        M.add('horns', horn.play(mm, vel - 12), at(k, e), 0.5 * gain, -0.25)
            if snares:
                pat = (0, 1, 2, 3, 4, 5, 6, 7) if j % 4 == 3 else (0, 2, 3, 4, 6, 7)
                for e in pat:
                    M.add('drums', (snare_f if e % 2 == 0 else snare).play(vel if e % 4 == 0 else vel - 25),
                          at(k, e / 2), 0.6 * gain, 0.15)
            if j % 4 == 0:
                M.add('drums', clash.play(vel), at(k), 0.45 * gain)

    def fill(k, vel=100):                    # a bar of snare sixteenths, crescendo, into a cymbal
        for e in range(16):
            M.add('drums', snare_f.play(int(vel * (0.55 + 0.45 * e / 15))), at(k, e / 4), 0.6, 0.15)
        for e in (2, 3):
            M.add('drums', tenor.play(vel), at(k, e), 0.8, -0.3 if e == 2 else 0.3)
        M.add('drums', clash.play(110), at(k + 1), 0.6)

    # ---- 0-8: the drum line ----
    r = sroll.play(80, dur=1.0)
    M.add('drums', r * np.linspace(0.1, 1, r.shape[1]) ** 2, 0.0, 0.6)
    for k in range(4):
        for e in range(8):
            if e % 4 != 1 or k >= 2:
                M.add('drums', (snare_f if e % 2 == 0 else snare).play(105 if e % 4 == 0 else 80), at(k, e / 2), 0.7,
                      0.15)
        for e in range(4):
            if k >= 2:                       # the wings answer each other: bass drum to whichever flashes
                M.add('drums', bd_ff.play(112), at(k, e), 0.9, 0.7 if (2 * k + e) % 2 else -0.7)
                M.add('drums', tenor.play(100), at(k, e), 0.5, 0.7 if (2 * k + e) % 2 else -0.7)
            else:
                M.add('drums', bd.play(100), at(k, e), 0.8, pan_at(2620 - 170 * (4 * k + e)))
    fill(3, 105)

    # ---- 8-24: the pumpkin and the A strain ----
    band(4, CHORDS_A)
    tune(TUNE_A, 4, tpt, long=tpt_s)
    tune(TUNE_A, 4, glock, 'motif', 84, 0.15, gain=0.45)
    spin = [0, 1, 2, 1]
    for i, t in enumerate(np.arange(T_PUMP, T_PGONE, BEAT / 2)):     # the marimba spins round the chord with it
        c = float(pumpkin_c(t))
        if c > L + 200 or c < -200:
            continue
        k = int(t // BAR) - 4
        ch = CH[CHORDS_A[k]] if 0 <= k < 8 else CH['Bb']
        M.add('motif', mar.play(ch[spin[i % 4]] + 12 * ((i // 4) % 2), 96), t, 0.8, pan_at(c))
    M.add('fx', whoosh(3.0, 400, 2500, 0.9, seed=3), T_GUST - 0.2, 0.45, 0.3)      # the gust
    M.add('fx', slide(0.0, at(1), 500, 1300, at(1) + 0.1, 0.5), T_GUST, 0.9, pan_at(1700))
    M.add('fx', slide(0.0, at(1), 1300, 600, at(1) + 0.1, 0.5), at(9), 0.8, pan_at(1900))
    M.add('perc', slap.play(110), at(9.5), 0.8, pan_at(1880))                     # the handlers haul
    M.add('fx', slide(0.0, 1.3, 1100, 350, 1.4, 0.5), at(11.75), 0.7, pan_at(300))   # away up the Side
    fill(12, 95)

    # ---- 26-44: the corn grows, sways, pops ----
    band(13, ['F', 'F'], 82, snares=False)
    scale = [n(x) for x in ('F4', 'G4', 'A4', 'Bb4', 'C5', 'D5', 'E5', 'F5')]
    for k in range(8):                       # a chunk of cob per beat: a step up the scale
        t = T_CORN + k * BEAT
        M.add('motif', xylo.play(scale[k], 100), t, 0.9, pan_at(MID))
        M.add('motif', mar.play(scale[k] - 12, 90), t, 0.6, pan_at(MID))
    band(15, CHORDS_B[:4], 98)
    band(19, CHORDS_B[4:7], 104)
    tune(TUNE_B, 15, clar, 'tune', 110, lambda t: 0.4 * np.sin(2 * np.pi * (t - T_SWAY) / (2 * BAR)), gain=1.0)
    tune(TUNE_B, 15, xylo, 'motif', 80, 0.0, gain=0.4)
    tune(TUNE_B[4:7], 19, tpt, 'tune', 104, 0.0, long=tpt_s, gain=0.7)
    for t, w, v in zip(pt, pw, pv):          # every kernel: a click where it pops, a little bloop
        p = float(pan_at(MID - 24 + w))
        M.add('perc', click.play(int(rng.integers(85, 120)), pitch=float(rng.uniform(4, 12))), t, 1.6, p)
        M.add('fx', slide(0.0, 0.06, 500, 1400, 0.09, 0.4), t, 0.4, p)
    r = ccresc.play(100, dur=T_COBGONE - T_POPC)
    M.add('drums', r * np.linspace(0.1, 1, r.shape[1]) ** 2, T_POPC, 0.35)
    M.add('perc', slap.play(127), T_COBGONE, 1.0, pan_at(MID))                    # all popped: ta-da
    M.add('drums', clash_f.play(120), T_COBGONE, 0.7)
    M.add('drums', bd_ff.play(120), T_COBGONE, 0.9)

    # ---- 44-52: the band struts tutti, then stop time for the claps ----
    band(22, CHORDS_A[:3], 110)
    tune(TUNE_A[:3], 22, tpt, long=tpt_s, gain=1.1)
    tune(TUNE_A[:3], 22, bone, 'horns', 100, -0.2, gain=0.6, octave=-12)
    tune(TUNE_A[:3], 22, glock, 'motif', 90, 0.15, gain=0.45)
    for e in range(4):
        t = at(25, e)
        if e % 2:
            M.add('drums', rim.play(124), t, 1.0, 0.0)
            M.add('perc', slap.play(110), t, 0.7, 0.0)
        else:
            M.add('drums', bd_ff.play(115), t, 0.9, 0.0)
            M.add('bass', tuba.play(n('F2'), 110), t, 1.0)
            for mm in CH['F7']:
                M.add('horns', horn.play(mm, 110), t, 0.6, -0.2)

    # ---- 52-62: the turkey's trio in Eb; a log drum on every step ----
    band(26, CHORDS_T, 96, snares=True, gain=0.85)
    tune(TUNE_T, 26, horn, 'tune', 104, -0.1, long=horn_s, gain=0.85)
    tune(TUNE_T, 26, bsn, 'motif', 96, 0.25, gain=0.7)
    for k in range(20):
        t = T_TURK + k * BEAT
        M.add('perc', log.play(108, pitch=-3 if k % 2 else 0), t, 0.9, pan_at(turkey_c(t + 0.2)))

    # ---- 62-66: he stops dead; gobbles; the brass answer ----
    for mm in CH['Bb7']:
        M.add('tune', tpt.play(mm + 12, 120, dur=0.25), T_STOP, 0.8)
        M.add('horns', horn.play(mm, 118, dur=0.25), T_STOP, 0.8)
    M.add('bass', tuba.play(n('Bb1'), 122), T_STOP)
    M.add('drums', bd_ff.play(118), T_STOP, 1.0)
    M.add('drums', choke.play(110), T_STOP, 0.7)
    for j, g in enumerate(GOBBLES):
        for i, s in enumerate((0, 3, 0, 3, -2, 0, 3, 0)):
            M.add('motif', bsn.play(n('Eb3') + 5 * j + s, 115, dur=0.08), g + 0.1 * i, 1.2, pan_at(MID - 150))
        a = ANSWERS[j]
        for mm in (CH['Eb'] if j == 0 else CH['Bb7']):
            M.add('tune', tpt.play(mm + 12, 122, dur=0.3), a, 0.8, -0.5)
            M.add('tune', tpt.play(mm + 12, 122, dur=0.3), a, 0.8, 0.5)
            M.add('horns', horn.play(mm, 118, dur=0.3), a, 0.8)
        M.add('drums', bd_ff.play(118), a, 1.0)
        M.add('drums', clash.play(110), a, 0.5)

    # ---- 66-76: pumped up; the whistle rides his radius; a hiccup; faster; a frozen beat ----
    for i, (tp, dr, e) in enumerate(PUMPS):
        if dr <= 0:
            M.add('fx', fall.play(100, dur=0.8), tp, 0.8, pan_at(MID))
            M.add('perc', wood.play(110, pitch=7), tp, 0.7, pan_at(MID))
            M.add('fx', whoosh(0.5, 3000, 600, 0.6, seed=40), tp, 0.7, pan_at(MID - 400))
            continue
        if tp >= T_LAST:
            continue
        r = radius(tp + e)
        M.add('bass', tuba.play(n('Bb1') + min(12, i // 2), 104), tp, 0.9)
        M.add('drums', timp.play(100 + min(25, i)), tp, 0.5, pan_at(MID))
        M.add('fx', whoosh(0.22, 2500, 5000, 0.5, seed=50 + i), tp - 0.18, 0.5, pan_at(2300))
    t1 = T_PUMPUP
    tt = t1 + np.arange(int((T_HOLD - t1) * SR)) / SR
    rr = np.interp(tt, np.arange(t1, T_HOLD, 0.01), [radius(t) for t in np.arange(t1, T_HOLD, 0.01)])
    fw = 300 * (rr / R0) ** 0.75
    M.add('fx', mono(tone(fw, 0.18) * np.clip((tt - t1) / 0.3, 0, 1), np.full(len(tt), pan_at(MID))), t1, 0.8)
    M.add('hold', trem.play(n('Bb2'), 75, dur=T_HOLD - t1, release=0.05), t1, 0.9, -0.2)
    M.add('hold', trem.play(n('F3'), 75, dur=T_HOLD - t1, release=0.05), t1, 0.7, 0.2)
    for k in range(4):                       # a horn a step higher each bar
        tk = at(33 + k) if k < 2 else T_FAST + (k - 2) * (T_HOLD - T_FAST) / 2
        dk = (at(34 + k) if k < 2 else T_FAST + (k - 1) * (T_HOLD - T_FAST) / 2) - tk
        if k == 1:
            dk = T_HIC - tk
        M.add('horns', horn_s.play(n('F3') + 2 * k, 80 + 10 * k, dur=dk, release=0.05), tk, 0.8, pan_at(MID))
    for e in range(12):                      # the fast pumping: snare eighths crescendo
        M.add('drums', snare_f.play(70 + 4 * e), T_FAST + e * BEAT / 2, 0.7, 0.15)
    r = troll.play(90, dur=T_HOLD - T_FAST)
    M.add('drums', r * np.linspace(0.2, 1, r.shape[1]) ** 2, T_FAST, 0.5)
    M.add('fx', slide(0.0, 0.45, 900, 1250, 0.5, 0.25), T_LAST, 0.7, pan_at(MID))   # the last creak

    # ---- 76: POP; the raspberry follows his head round the house; confetti ----
    pp = float(pan_at(MID))
    M.add('drums', clash_f.play(127), T_BANG, 1.6, pp)
    M.add('drums', bd_ff.play(127), T_BANG, 2.0, pp)
    M.add('drums', timp.play(127, pitch=-3), T_BANG, 1.4, pp)
    M.add('perc', slap.play(127), T_BANG, 1.4, pp)
    th = np.array([h[0] for h in HEAD])
    tu = np.arange(int((th[-1] - T_BANG + 0.2) * SR)) / SR
    hx = np.interp(T_BANG + tu, th, [h[1] for h in HEAD])
    sp = np.abs(np.gradient(hx)) * SR
    fr = (260 + 0.12 * sp) * (1 + 0.04 * np.sin(2 * np.pi * 23 * tu)) * 2 ** (-0.8 * tu / tu[-1])
    rasp = tone(fr, 0.3, buzz=0.9) * np.clip(tu / 0.04, 0, 1) * np.clip((tu[-1] - tu) / 0.2, 0, 1)
    M.add('fx', mono(rasp, pan_at(np.clip(hx, 0, L))), T_BANG + 0.02, 0.9)
    for tk in th[1:-1]:
        M.add('perc', wood.play(110, pitch=5), tk, 0.6, float(pan_at(np.interp(tk, th, [h[1] for h in HEAD]))))
    M.add('perc', slap.play(110), th[-1] - 0.1, 0.7, float(pan_at(L)))
    M.add('perc', tri.play(100), th[-1], 0.5, float(pan_at(L)))
    for i in range(36):                      # confetti sparkles out to both ends
        t = T_BANG + 0.1 + i * 0.07
        side = 1 if i % 2 else -1
        M.add('motif', glock.play(int(rng.choice(CH['Bb'])) + 12 * int(rng.integers(0, 2)), int(95 - i)), t, 0.4,
              float(np.clip(side * (0.2 + i * 0.02), -0.85, 0.85)))

    # ---- 80-90: pickup, the A strain marching off, a sweep round the outline, the last chord ----
    for e in (2, 2.5, 3, 3.5):
        M.add('drums', snare_f.play(int(90 + 10 * e)), at(40, e), 0.8, 0.15)
    band(41, CHORDS_A[4:6], 112)
    tune(TUNE_A[4:6], 41, tpt, long=tpt_s, gain=1.15)
    tune(TUNE_A[4:6], 41, bone, 'horns', 104, -0.2, gain=0.6, octave=-12)
    tune(TUNE_A[4:6], 41, glock, 'motif', 92, 0.15, gain=0.45)
    band(43, ['F7'], 115)
    run = sorted({mm + 12 * o for mm in CH['F7'] for o in (-1, 0, 1)})[1:9]
    for k in range(8):                       # the sweep from Right to the back of the Side, a brass step an eighth
        t = T_SWEEP + k * BEAT / 2
        p = float(pan_at(2620 - 2700 * k / 8))
        M.add('tune', tpt.play(run[k], 104 + 2 * k, dur=0.2), t, 0.9, p)
        M.add('horns', bone.play(run[k] - 12, 100, dur=0.2), t, 0.8, p)
    for mm in CH['Bb']:
        M.add('tune', tpt_s.play(mm + 12, 115, dur=1.8), T_CHORD, 0.6)
        M.add('horns', horn_s.play(mm, 112, dur=1.9), T_CHORD, 0.6, -0.2)
    M.add('motif', glock.play(n('Bb5'), 100), T_CHORD, 0.6)
    M.add('bass', tuba_s.play(n('Bb1'), 118, dur=1.9), T_CHORD)
    M.add('drums', clash_f.play(122), T_CHORD, 0.8)
    M.add('drums', bd_ff.play(122), T_CHORD, 1.0)
    r = troll.play(80, dur=1.4)
    M.add('drums', r * np.linspace(1, 0.2, r.shape[1]), T_CHORD + 0.1, 0.5)
