"""Bone Yard: five skeletons climb out of the roof and are put together bone by bone, with the bones
zipping in from the two free ends of the house. They dance a mirrored routine to an internal 120 BPM
(Left against Right, Porch Left against Porch Right, the porch skeleton calling it), clacking on the
beat; then a conga line steps-steps-steps-kicks right off the end of the house and back in the other
end. The porch skeleton gets carried away, explodes into bones, and is rebuilt wrong (foot for a
hat, skull at the bottom) and dances half a beat late until he catches up. Finale: they all
collapse into heaps and the skulls roll away out of the free ends; his teeters on the edge first.

Everything lives in path distance (layout units along the roofline), so bones keep their size on
every run. A skeleton is a stack of bones (skull with eye sockets, ribcage of ticks, pelvis, femur,
shin, foot) separated by joint gaps; the dance moves its centre, stretches its joints, tosses the
first bone and kicks the last. Each bone is drawn by exact span-over-pixel coverage."""
import numpy as np
from pixelhome.fx import DT, hexc, light, smoothstep, keys, lerp, nframes

CODE = 'HW04'
TITLE = 'Bone Yard'
KIND = 'show'
DESCRIPTION = ('Skeletons climb out of the roof, get assembled from bones flying in off the ends of '
               'the house, dance a mirrored routine and a conga. One falls apart, gets put back '
               'together wrong, and keeps dancing anyway.')
VOICEOVER = 'Tonight... the bone yard wakes. Five skeletons, one roof, and not a single spare bone. Watch closely.'

BONE = hexc('#fff0d6')
GLOW = hexc('#40ff70')
FOG = hexc('#1c9c8c')

BEAT = 0.5                                  # 120 BPM
K = 1.35                                    # figure scale: about 210 units head to toe
LEN = K * np.array([32.0, 37.0, 16.0, 26.0, 22.0, 9.0])  # skull, ribs, pelvis, femur, shin, foot
GAP = K * 4.0
RIGHT = [0, 1, 2, 3, 4, 5]
WRONG = [5, 2, 1, 4, 3, 0]                  # foot on top, skull at the bottom
PARTS = {                                   # lit sub-spans (v0, v1, weight) in bone coordinates
    0: [(0, 32, 1.3), (7, 12, -1.3), (20, 25, -1.3)],
    1: [(v, v + 5, 1.0) for v in (0, 8, 16, 24, 32)],
    2: [(0, 16, 1.0), (7, 9, -0.8)],
    3: [(0, 4, 0.25), (0, 26, 1.0), (22, 26, 0.25)],
    4: [(0, 22, 1.0)],
    5: [(0, 5, 1.0), (7, 9, 1.0)],
}
SOCKETS = {0: [(7, 12), (20, 25)]}
PARTS = {b: [(K * a, K * z, wt if b == 0 else 0.85 * wt) for a, z, wt in p] for b, p in PARTS.items()}
SOCKETS = {b: [(K * a, K * z) for a, z in p] for b, p in SOCKETS.items()}
R = 16 * K                                  # skull radius when it rolls

T0, TC, TP = 15.0, 31.0, 45.0               # routine, conga, after-conga
TX = 48.0                                   # the porch skeleton explodes
TR = 51.6                                   # reassembly starts
TL = 56.0                                   # late dance
TH = 64.0                                   # unison hit
D = 81.0


def _back(u, c1=1.3):
    u = np.clip(u, 0, 1)
    return 1 + (c1 + 1) * (u - 1) ** 3 + c1 * (u - 1) ** 2


CRUISE, APPR, TAPPR = 1400.0, 170.0, 0.55   # flying bones: cruise in, then a slow 0.55 s approach


def fly(src, dst, tt, fl):
    """Bone flight: constant cruise from src, then the last APPR units eased in with overshoot."""
    sgn = np.sign(dst - src)
    tc = fl - TAPPR
    if tt < tc:
        return src + sgn * CRUISE * max(tt, 0.0)
    return dst - sgn * APPR * (1 - _back((tt - tc) / TAPPR))


def _hit(f, k=0.09):
    """Clack envelope f beats after the hit."""
    return float(np.exp(-f * BEAT / k))


def _layout(order, g, hd=0.0, fd=0.0):
    u0 = np.zeros(6)
    cur = 0.0
    for b in order:
        u0[b] = cur
        cur += LEN[b] + GAP * g
    total = cur - GAP * g
    u0[order[0]] -= hd
    u0[order[-1]] += fd
    return u0, total / 2


class _Skel:
    def __init__(self, name, home, ms, hdir, src, rise, center=False):
        self.name, self.home, self.ms, self.hdir = name, home, ms, hdir
        self.src, self.rise, self.center = src, rise, center


def render(G, seed=4):
    rng = np.random.default_rng(seed)
    L = G.length
    OFF = 200.0
    C = L + 2 * OFF                          # conga lap: off the right end, back in at the far end
    pdp = G.pd[G.path]
    w = np.gradient(pdp)
    e0, e1 = pdp - w / 2, pdp + w / 2
    mid = {n: float(G.pd[G.seg[n]].mean()) for n in G.seg}

    S = [_Skel('Left', mid['Left'], +1, -1, -40.0, 4.5),
         _Skel('Porch Left', mid['Porch Left'], +1, +1, -40.0, 6.5),
         _Skel('Porch Front', mid['Porch Front'], 0, -1, None, 2.5, center=True),
         _Skel('Porch Right', mid['Porch Right'], -1, -1, L + 40, 6.5),
         _Skel('Right', mid['Right'], -1, +1, L + 40, 4.5)]
    P = S[2]
    for sk in S:
        sk.land = [sk.rise] + [sk.rise + 1.1 + 0.55 * (j - 1) for j in range(1, 6)]
        srcs = [sk.src if sk.src is not None else (-40.0 if j % 2 else L + 40) for j in range(6)]
        sk.srcs = srcs
        sk.fl = [max(0.0, abs(sk.home - s) - APPR) / CRUISE + TAPPR for s in srcs]
        sk.hoff = rng.uniform(-22, 22, 6)
        sk.wig = rng.uniform(0, 2 * np.pi, 6)
    pair = {'Left': 0, 'Right': 0, 'Porch Left': 1, 'Porch Right': 1, 'Porch Front': 2}
    collapse = [65.5, 66.2, 67.4]
    rollt = [68.6, 69.4, 70.6]
    rolldir = {'Left': -1, 'Porch Left': -1, 'Porch Front': 1, 'Porch Right': 1, 'Right': 1}

    # the explosion: launch speeds (alternating directions so the porch empties both ways)
    xv = np.array([1, -1, 1, -1, 1, -1]) * rng.uniform(300, 620, 6)
    rng.shuffle(xv)
    xv[5] = 1400.0 * np.sign(xv[5])         # the foot goes furthest
    TAU = 0.4
    x0_rest, Lc_rest = _layout(RIGHT, 1.0)
    xorig0 = P.home + P.hdir * (x0_rest - Lc_rest)
    xland = [TR + 0.5 * r + 0.42 for r in range(6)]
    xdep = {b: TR + 0.5 * r for r, b in enumerate(WRONG)}

    def scatter_pos(b, t):
        tt = max(0.0, t - TX)
        x = xorig0[b] + xv[b] * TAU * (1 - np.exp(-tt / TAU))
        if t > TX + 1.6:
            x += 1.5 * np.sin(2 * np.pi * 7 * t + P.wig[b]) * smoothstep(TX + 1.6, TX + 2.2, t)
        return x

    # ---- choreography: (centre offset, dir, joint gap, head toss, foot kick, flash, order) ----
    def routine(sk, tt):
        b = tt / BEAT
        j = int(b)
        f = b - j
        ph, k = j // 8, j % 8
        ms = sk.ms
        off, g, hd, fd, fl = 0.0, 1.0, 0.0, 0.0, 0.0
        if ph == 0:                          # mirrored sway, clack every beat
            tgt = lambda jj: 0.0 if jj < 0 else ms * 24 * (1 if jj % 2 == 0 else -1)
            off = lerp(tgt(j - 1), tgt(j), smoothstep(0, 0.3, f))
            if sk.center:
                g = 1 + 0.9 * smoothstep(0.25, 0.95, f)
            fl = 0.6 * _hit(f)
        elif ph == 1:                        # accordion call and response: wings+porch front, then porch sides
            grp = 1 if sk.name in ('Porch Left', 'Porch Right') else 0
            act = (k % 2) == grp
            if act:
                g = 1 + 2.0 * smoothstep(0.2, 0.95, f)
            prev_act = ((k - 1) % 2) == grp
            fl = 0.95 * _hit(f) if prev_act else 0.15 * _hit(f)
        elif ph == 2:                        # head toss, pairs alternating; the caller throws his highest
            if sk.center:
                win, amp = (6, 7), 90.0
            elif sk.name in ('Porch Left', 'Porch Right'):
                win, amp = (2, 3, 6, 7), 45.0
            else:
                win, amp = (0, 1, 4, 5), 45.0
            if k in win:
                u = ((k % 2) + f) / 2
                hd = amp * 4 * u * (1 - u)
            caught = (k % 2 == 0) and ((k - 1) % 8 in win) and k > 0
            fl = 0.9 * _hit(f) if caught else 0.2 * _hit(f)
        else:                                # shimmy in eighths, wind up, big hit
            if k < 6:
                if sk.center:
                    g = 1.3 + 0.35 * np.sin(2 * np.pi * 2 * b)
                else:
                    off = ms * 9 * np.sin(2 * np.pi * 2 * b)
                fl = 0.3 * _hit((2 * b) % 1 / 2, 0.06)
            elif k == 6:
                g = 1 + 1.8 * smoothstep(0, 1, f)
            else:
                fl = 1.0 * _hit(f, 0.14)
        return off, g, hd, fd, fl

    def late_moves(sk, tt, ms):
        b = tt / BEAT
        j = int(b)
        f = b - j
        if j < 8:
            tgt = lambda jj: 0.0 if jj < 0 else ms * 26 * (1 if jj % 2 == 0 else -1)
            off = lerp(tgt(j - 1), tgt(j), smoothstep(0, 0.3, f))
            return off, 1.0 + (0.5 * smoothstep(0.25, 0.95, f) if sk.center else 0), 0.0, 0.0, 0.6 * _hit(f)
        return 0.0, 1 + 1.7 * smoothstep(0.2, 0.95, f), 0.0, 0.0, 0.85 * _hit(f)

    def state(sk, t):
        off, dr, g, hd, fd, fl = 0.0, float(sk.hdir), 1.0, 0.0, 0.0, 0.0
        c = sk.home
        order = WRONG if (sk.center and t >= TR) else RIGHT
        if t < T0:
            la = sk.land[-1]
            if t > la:
                g = 1 + 0.5 * np.sin(2 * np.pi * 6 * (t - la)) * np.exp(-(t - la) * 3)
            if sk.center:
                for tc in (13.0, 13.5, 14.0, 14.5):
                    if t >= tc - 0.25:
                        u = (t - tc + 0.25) / 0.25
                        if u < 1:
                            hd = 14 * u * u
                        fl = max(fl, 0.7 * _hit((t - tc) / BEAT) if t >= tc else 0)
        elif t < TC:
            off, g, hd, fd, fl = routine(sk, t - T0)
        elif t < TP:
            tt = t - TC
            dr = lerp(sk.hdir, -1.0, smoothstep(0, 0.4, tt))
            bar = int(tt / 2)
            jb = int(tt / BEAT) % 4
            f = tt / BEAT - int(tt / BEAT)
            adv = 3 * bar + (jb + smoothstep(0, 0.55, f) if jb < 3 else 3)
            off = (C / 21) * adv
            if jb == 3:
                fd = 34 * np.sin(np.pi * f)
            fl = (0.95 if jb == 3 else 0.45) * _hit(f)
        elif t < TL:
            tt = t - TP
            dr = lerp(-1.0, sk.hdir, smoothstep(0, 0.4, tt))
            b = tt / BEAT
            f = b - int(b)
            if sk.center:
                if 1 <= tt < 3:              # solo, each pump bigger than the last
                    amp = [1.0, 1.6, 2.3, 3.2][int((tt - 1) / BEAT)]
                    g = 1 + amp * smoothstep(0.2, 0.95, f)
                    fl = 0.8 * _hit(f)
                elif t >= TX:
                    fl = 1.0 * _hit((t - TX) / BEAT, 0.15)
                if t >= TR + 3.2:            # ta-da: the foot-hat is lifted clear for a beat
                    hd = keys(t, [(TR + 3.2, 0.0), (TR + 3.45, 62.0), (TR + 3.95, 62.0), (TR + 4.12, 0.0)])
                    fl = max(fl, 1.0 * _hit((t - TR - 4.12) / BEAT) if t >= TR + 4.12 else 0)
            else:
                ms = sk.ms
                if 1 <= tt < 3:
                    off = ms * 8 * smoothstep(1, 1.5, tt)
                    fl = 0.4 * _hit(f)
                off -= ms * 45 * smoothstep(TX, TX + 0.12, t) * (1 - smoothstep(TX + 1.5, TX + 2.4, t))
                off += ms * 16 * smoothstep(TX + 2.2, TX + 3.0, t) * (1 - smoothstep(TR + 3.0, TR + 3.8, t))
                if TX <= t < TX + 1.5:
                    off += 2.5 * np.sin(2 * np.pi * 13 * t) * np.exp(-(t - TX) * 2)
                    g = 0.7
        elif t < TH:
            tt = t - TL
            if sk.center:
                late = tt - 0.25 if tt < 6.0 else tt
                if late >= 0:
                    off, g, hd, fd, fl = late_moves(sk, late, 1.25)
            else:
                off, g, hd, fd, fl = late_moves(sk, tt, sk.ms)
        else:
            fl = 1.0 * _hit((t - TH) / BEAT, 0.16) if t < TH + 1.2 else 0.0
            if sk.center and 66.6 <= t < 67.4:      # one more for himself
                f = (t - 66.6) / 0.4
                g = 1 + 1.6 * smoothstep(0.2, 0.95, min(f, 1)) if f < 1 else 1.0
                fl = 0.8 * _hit((t - 67.0) / BEAT) if t >= 67.0 else 0.0
        return c + off, dr, g, hd, fd, fl, order

    # ---- span accumulation ----
    def emit(spans, glows, b, origin, dr, I, eye=1.0, look=0.0):
        for q, (v0, v1, wgt) in enumerate(PARTS[b]):
            sh = look if (b == 0 and q > 0) else 0.0
            a, z = origin + dr * (v0 + sh), origin + dr * (v1 + sh)
            spans.append((min(a, z), max(a, z), I * wgt))
        for v0, v1 in SOCKETS.get(b, []):
            a, z = origin + dr * (v0 + look), origin + dr * (v1 + look)
            glows.append((min(a, z), max(a, z), 0.75 * eye * min(I, 1)))

    def tail(spans, bc, half, vel, I):
        if abs(vel) < 200:
            return
        tl = min(abs(vel) * 0.05, 90)
        s = -np.sign(vel)
        for q, k in enumerate((0.45, 0.25, 0.1)):
            a = bc + s * (half + tl * q / 3)
            z = bc + s * (half + tl * (q + 1) / 3)
            spans.append((min(a, z), max(a, z), I * k))

    def wrap(x):
        return ((x + OFF) % C) - OFF

    def skull_roll(spans, glows, x, theta, I):
        spans.append((x - R, x + R, 1.3 * I))
        for a in (theta - 0.45, theta + 0.45):
            if np.cos(a) > 0.05:
                p = x + R * np.sin(a)
                hw = 2.5 * K * np.cos(a)
                spans.append((p - hw, p + hw, -1.3 * I))
                glows.append((p - hw, p + hw, 0.75 * np.cos(a)))

    def roll_pos(sk, t):
        ts = rollt[pair[sk.name]]
        x0 = sk.home + sk.hoff[0]
        sgn = rolldir[sk.name]
        tt = t - ts
        if not sk.center:
            return x0 + sgn * 340 * (tt - 0.3 * (1 - np.exp(-tt / 0.3))), x0
        stop = L - R - 2
        if t < 75.6:
            return lerp(x0, stop, smoothstep(0, 1, tt / 5.0)), x0
        if t < 77.4:
            return stop + 4 * np.sin(2 * np.pi * 1.4 * (t - 75.6)) * np.exp(-(t - 75.6) * 0.8), x0
        return stop + 420 * (t - 77.4) ** 2, x0

    F = nframes(D)
    out = np.zeros((F, G.N, 3))
    for fi in range(F):
        t = fi * DT
        spans, glows = [], []
        fog = 0.13 * smoothstep(0, 2.5, t) * (1 - smoothstep(77.8, 80.5, t)) * np.ones(G.N)
        fog *= 1 + 0.25 * np.sin(pdp / 140 + 0.4 * t) * np.sin(pdp / 61 - 0.27 * t)
        fade = 1 - smoothstep(77.8, 80.5, t)
        for sk in S:
            c, dr, g, hd, fd, fl, order = state(sk, t)
            u0, Lc = _layout(order, g, hd, fd)
            origin = c + dr * (u0 - Lc)
            if t < TC or t >= TP:
                pass
            else:
                origin = wrap(origin)
            Ibase = (0.68 + 0.32 * fl)
            tc = collapse[pair[sk.name]]
            if t < sk.rise - 0.7:
                continue
            if t < sk.rise + 1.2:                # the ground stirs, then the skull pushes up
                fog += 0.25 * np.exp(-((pdp - sk.home) / 45) ** 2) * smoothstep(sk.rise - 0.7, sk.rise, t) * (1 - smoothstep(sk.rise + 0.4, sk.rise + 1.2, t))
            for b in range(6):
                I = Ibase
                o = origin[b]
                if t < sk.land[b] - (0 if b == 0 else sk.fl[b]):
                    continue
                if b == 0 and t < sk.land[0] + 1.2:
                    I *= smoothstep(sk.land[0], sk.land[0] + 0.9, t)
                    o += 2.5 * np.sin(2 * np.pi * 11 * t) * (1 - smoothstep(sk.land[0] + 0.6, sk.land[0] + 1.2, t))
                elif b > 0 and t < sk.land[b]:   # in flight from a free end
                    src = sk.srcs[b]
                    o = fly(src, o, t - sk.land[b] + sk.fl[b], sk.fl[b])
                    vel = (o - fly(src, origin[b], t - DT - sk.land[b] + sk.fl[b], sk.fl[b])) / DT
                    tail(spans, o + dr * LEN[b] / 2, LEN[b] / 2, vel, 0.7)
                    I = 0.85
                elif b > 0 and t < sk.land[b] + 0.5:
                    I += 0.4 * _hit((t - sk.land[b]) / BEAT)
                if sk.center and TX <= t < xland[WRONG.index(b)]:
                    dep = xdep[b]
                    xs = scatter_pos(b, min(t, dep))
                    if t < dep:
                        o = xs
                        vel = xv[b] * np.exp(-(t - TX) / TAU)
                        tail(spans, o + dr * LEN[b] / 2, LEN[b] / 2, vel, 0.6)
                        I = 0.6 + 0.4 * fl if t < TX + 1 else 0.5
                    else:
                        u = (t - dep) / 0.42
                        tgt = origin[b]
                        o = lerp(xs, tgt, _back(u))
                        o2 = lerp(xs, tgt, _back(u - DT / 0.42))
                        tail(spans, o + dr * LEN[b] / 2, LEN[b] / 2, (o - o2) / DT, 0.6)
                        I = 0.7
                elif sk.center and xland[WRONG.index(b)] <= t < xland[WRONG.index(b)] + 0.5:
                    I += 0.5 * _hit((t - xland[WRONG.index(b)]) / BEAT)
                if t >= tc:                      # collapse: bones rattle down into a heap
                    rank = order.index(b)
                    tb = tc + 0.07 * rank
                    heap = sk.home - dr * LEN[b] / 2 + sk.hoff[b]
                    u = np.clip((t - tb) / 0.2, 0, 1)
                    o = lerp(o, heap, u * u)
                    I = 0.17 + 0.45 * _hit((t - tb - 0.2) / BEAT) if t >= tb + 0.2 else Ibase
                    if b == 0 and t >= rollt[pair[sk.name]]:
                        x, x0 = roll_pos(sk, t)
                        if -20 < x < L + 20:
                            Isk = 0.7
                            if sk.center and t >= 77.4:
                                Isk = 0.7 + 0.3 * _hit((t - 77.4) / BEAT)
                            skull_roll(spans, glows, x, (x - x0) / R, Isk)
                        continue
                    I *= fade
                eye, look = 1.0, 0.0
                if b == 0:
                    if ((t + 2.7 * sk.wig[0] / (2 * np.pi)) % 2.7) < 0.13:
                        eye = 0.0                # blink
                    if sk.center and 55.9 <= t < 62.0:   # skull at the bottom looks around: what happened?
                        look = 4.5 * K * np.tanh(3 * np.sin(2 * np.pi * 0.7 * (t - 55.9))) * smoothstep(55.9, 56.2, t)
                emit(spans, glows, b, o, dr, I, eye, look)
        sp = np.array(spans) if spans else np.zeros((0, 3))
        ov = np.clip(np.minimum(sp[:, 1:2], e1) - np.maximum(sp[:, 0:1], e0), 0, None) / w
        Ib = np.clip(sp[:, 2] @ ov, 0, 1)
        cov = np.clip(np.abs(sp[:, 2:3] * ov).sum(0) if len(sp) else 0, 0, 1)
        if glows:
            gp = np.array(glows)
            gv = np.clip(np.minimum(gp[:, 1:2], e1) - np.maximum(gp[:, 0:1], e0), 0, None) / w
            Ig = np.clip(gp[:, 2] @ gv, 0, 0.9)
        else:
            Ig = np.zeros(G.N)
        buf = light(BONE, Ib) + light(GLOW, Ig) + light(FOG, fog * (1 - cov))
        out[fi][G.path] = np.clip(buf, 0, 1)
    return out


# ---------------------------------------------------------------- music ----------------------------------------------
# A skeleton band in D minor at the lights' 120 BPM: xylophone bones, tuba and pizzicato oom-pah, a calliope for the
# conga, slide whistles for the head tosses. Every hit below is a moment in render(): bone landings, count-in taps,
# clacks, slams, catches, the explosion, the wrong reassembly, the collapses and the rolling skulls. Sounds are
# panned to where they happen on the house as seen from the street.

RISE = {'Left': 4.5, 'Porch Left': 6.5, 'Porch Front': 2.5, 'Porch Right': 6.5, 'Right': 4.5}
STEPS = [0, 3, 5, 7, 10]                    # bone landings climb a minor pentatonic: ribs, pelvis, femur, shin, foot
BASE = {'Porch Front': 74, 'Left': 77, 'Right': 77, 'Porch Left': 81, 'Porch Right': 81}
CHORD = {'Dm': (50, 53, 57), 'A7': (49, 52, 55, 57), 'Gm': (50, 55, 58)}
ROOT = {'Dm': (38, 33), 'A7': (33, 40), 'Gm': (31, 38)}


def score(M, G):
    from pixelhome.audio import note, slide, whoosh
    n = note
    xylo = M.sampler('Percussion/Xylo/*.wav')
    mar = M.sampler('Percussion/Marimba/*.wav')
    glock = M.sampler('Percussion/Glock/*.wav')
    tuba = M.sampler('Brass/Tuba/stac/*.wav')
    tpt = M.sampler('Brass/Trumpet/stac/*.wav')
    pizz = M.sampler('Strings/Cello Section/pizzT/*.wav')
    trem = M.sampler('Strings/Cello Section/trem/*.wav')
    wood = M.hits('VSCO 1 Percussion/varWood/wood_click*.wav')
    clave = M.hits('Percussion/Claves1_Hit*.wav')
    slap = M.hits('VSCO 1 Percussion/varWood/slapstick[0-9].wav')
    cow = M.hits('Percussion/Cowbell1_Hit*.wav')
    conga = M.hits('Percussion/Conga-HitN*.wav')
    tumba = M.hits('Percussion/Tumba-HitN*.wav')
    tamb = M.hits('Percussion/Tamb1-Hit*.wav')
    crash = M.hits('Percussion/cymbal-crash1_f*.wav')
    crash_s = M.hits('Percussion/cymbal-crashshort*.wav')
    bd = M.hits('Percussion/BDrumNewhit_v[4-7]*.wav')
    timp = M.hits('Percussion/Timpani/Timpani1_Hit*.wav')
    troll = M.hits('Percussion/Timpani/Rolls/*.wav')
    ratchet = M.hits('Percussion/Ratchet1-Crank*.wav')
    ratchet_f = M.hits('Percussion/Ratchet1-Fast*.wav')
    log = M.hits('VSCO 1 Percussion/varWood/log_drum/*.wav')

    for name, gain, rev in (('xylo', 0.42, 0.22), ('mallet', 0.4, 0.2), ('bass', 0.55, 0.08), ('pizz', 0.3, 0.15),
                            ('perc', 0.65, 0.12), ('drums', 0.5, 0.18), ('organ', 0.22, 0.4), ('calliope', 0.42, 0.25),
                            ('brass', 0.35, 0.2), ('fx', 0.14, 0.25), ('strings', 0.3, 0.3)):
        M.bus(name, gain=gain, reverb=rev)

    order = np.argsort(G.pd)
    xs, ds = G.pos[order, 0], G.pd[order]
    x0, x1 = xs.min(), xs.max()

    def pan_at(d):                          # path distance -> left/right across the facade, as seen from the street
        x = np.interp(d, ds, xs)
        return float(0.85 * (2 * (x - x0) / (x1 - x0) - 1))

    mid = {k: float(G.pd[G.seg[k]].mean()) for k in G.seg}
    span = {k: pan_at(mid[k]) for k in G.seg}
    L = G.length

    def beat(k):                            # time of beat k of the routine grid (beat 0 = T0)
        return T0 + k * BEAT

    def chord_at(t, prog):
        return prog[min(len(prog) - 1, int((t - T0) // (4 * BEAT)) % len(prog))]

    organ, calliope = [], []

    # ---- 0-13 s: fog, skulls push up, bones fly in and click into place ----
    organ += [(0.2, n('D2'), 52, 12.6), (0.2, n('A2'), 46, 12.6), (6.0, n('F3'), 40, 6.8)]
    M.add('fx', whoosh(7.0, 120, 500, 0.5, seed=3), 0.0, 0.3)
    for k, rise in RISE.items():
        p = span[k]
        M.add('drums', troll.play(55, dur=1.0), rise - 0.8, 0.5, p)
        M.add('mallet', mar.play(BASE[k] - 36, 105), rise, 1.0, p)
        for j in range(1, 6):
            land = rise + 1.1 + 0.55 * (j - 1)
            M.add('fx', whoosh(0.5, 900, 3800, 0.35, seed=j + int(rise * 10)), land - 0.5, 0.35, p)
            M.add('xylo', xylo.play(BASE[k] + STEPS[j - 1], 100), land, 1.0, p)
            M.add('perc', wood.play(90), land, 0.6, p)
        M.add('perc', ratchet.play(80, dur=0.35), rise + 1.1 + 0.55 * 4 + 0.1, 0.7, p)

    # ---- 13-14.5: the porch skeleton taps its own skull four times ----
    for i, tc in enumerate((13.0, 13.5, 14.0, 14.5)):
        M.add('perc', clave.play(85 + 12 * i), tc, 1.0, span['Porch Front'])

    # ---- 15-31: the routine, 4 phrases of 8 beats; oom-pah under all of it ----
    prog = ['Dm', 'A7', 'Dm', 'A7', 'Gm', 'Dm', 'A7', 'Dm']

    def oompah(k0, k1, prog, vel=96):
        for k in range(k0, k1):
            t = beat(k)
            c = chord_at(t, prog)
            if k % 2 == 0:
                M.add('bass', tuba.play(ROOT[c][(k // 2) % 2], vel), t)
            else:
                for m in CHORD[c]:
                    M.add('pizz', pizz.play(m, vel - 12), t, 0.7, -0.35)

    oompah(0, 30, prog)
    melody = [(0, 'A5'), (0.5, 'F5'), (1, 'D5'), (1.5, 'F5'), (2, 'A5'), (3, 'D6'),
              (4, 'C#6'), (4.5, 'A5'), (5, 'E5'), (5.5, 'G5'), (6, 'A5'), (7, 'A4')]
    for b, m in melody:                     # phrase 1: the sway, a clack on every beat
        M.add('xylo', xylo.play(n(m), 104), beat(b), 1.0, 0.1)
    for k in range(0, 8):
        M.add('perc', wood.play(100), beat(k), 0.8)
    for k in range(8, 16):                  # phrase 2: accordion call and response; who slams alternates by beat
        t, c = beat(k), chord_at(beat(k), prog)
        if k % 2:                           # wings and porch front slam: high xylophone chord, left and right
            for m in CHORD[c]:
                M.add('xylo', xylo.play(m + 24, 110), t, 0.55, span['Left'] * 0.8)
                M.add('xylo', xylo.play(m + 24, 110), t, 0.55, span['Right'] * 0.8)
        elif k > 8:                         # porch sides answer low
            for m in CHORD[c]:
                M.add('mallet', mar.play(m, 112), t, 0.7, 0.0)
        M.add('perc', slap.play(70), t, 0.5)
    for k0, f0, f1, grp in ((16, 700, 1500, ('Left', 'Right')), (18, 800, 1700, ('Porch Left', 'Porch Right')),
                            (20, 700, 1500, ('Left', 'Right')), (22, 800, 1700, ('Porch Left', 'Porch Right')),
                            (22, 1000, 2600, ('Porch Front',))):   # phrase 3: head tosses up and caught
        for g in grp:
            M.add('fx', slide(0.0, 0.5, f0, f1, 0.5, 0.5), beat(k0), 0.8, span[g])
            M.add('fx', slide(0.0, 0.5, f1, f0, 0.5, 0.5), beat(k0 + 1), 0.8, span[g])
    for k, g in ((18, 'Left'), (18, 'Right'), (20, 'Porch Left'), (20, 'Porch Right'), (22, 'Left'), (22, 'Right')):
        M.add('perc', clave.play(115), beat(k), 0.9, span[g])
        M.add('xylo', xylo.play(n('D6'), 90), beat(k), 0.5, span[g])
    for e in range(12):                     # phrase 4: shimmy in eighths, wind up, one big hit
        t = beat(24) + e * BEAT / 2
        M.add('perc', tamb.play(70 + 20 * (e % 2 == 0)), t, 0.8)
        M.add('xylo', xylo.play(n('A5') if e % 2 == 0 else n('G5'), 84), t, 0.6, 0.15)
    M.add('perc', ratchet.play(100, dur=0.5), beat(30), 1.0)
    M.add('drums', troll.play(80, dur=0.5), beat(30), 0.7)

    def tutti(t, big=1.0):
        M.add('drums', crash.play(118), t, 0.9 * big)
        M.add('drums', bd.play(120), t, 1.0 * big)
        M.add('drums', timp.play(120, pitch=-2), t, 0.8 * big)
        M.add('bass', tuba.play(n('D1'), 120), t)
        M.add('bass', tuba.play(n('D2'), 120), t, 0.7)
        for m in CHORD['Dm']:
            M.add('pizz', pizz.play(m, 120), t, 0.8, -0.3)
            M.add('xylo', xylo.play(m + 24, 120), t, 0.7, 0.1)
            M.add('brass', tpt.play(m + 12, 112, dur=0.35), t, 0.8, 0.2)

    tutti(beat(31))

    # ---- 31-45: the conga, step-step-step-KICK for 7 bars; calliope tune ----
    M.add('fx', slide(0.0, 0.3, 500, 1300, 0.3, 0.4), TC, 0.6)
    tune = {'Dm': ['D5', 'F5', 'A5', 'D6'], 'A7': ['C#5', 'E5', 'G5', 'A5']}
    for bar in range(7):
        c = 'Dm' if bar % 2 == 0 or bar == 6 else 'A7'
        for jb in range(4):
            t = TC + bar * 2 + jb * BEAT
            if jb < 3:
                calliope.append((t, n(tune[c][jb]), 100, 0.38))
                M.add('perc', conga.play(95 + 10 * (jb == 0)), t, 1.0, -0.2)
                M.add('perc', tumba.play(70), t + BEAT / 2, 0.7, 0.25)
                if jb != 1:
                    M.add('bass', tuba.play(ROOT[c][jb // 2], 100), t)
                else:
                    for m in CHORD[c]:
                        M.add('pizz', pizz.play(m, 84), t, 0.6, -0.35)
            else:                           # the kick: everyone, hard
                for m in (n(tune[c][3]), n(tune[c][3]) - 7):
                    calliope.append((t, m, 120, 0.2))
                M.add('perc', slap.play(120), t, 1.0)
                M.add('drums', crash_s.play(110), t, 0.6)
                M.add('bass', tuba.play(ROOT[c][0], 118), t)
                M.add('xylo', xylo.play(n(tune[c][3]) + 12, 118), t, 0.8)

    # ---- 45-56: his solo, the explosion, a stunned pause, the wrong reassembly, ta-da ----
    organ += [(45.0, n('A2'), 76, 3.0), (45.0, n('E3'), 66, 3.0)]
    M.add('drums', troll.play(60, dur=3.0), 45.0, 0.6)
    for i, (m, v) in enumerate((('D5', 80), ('F5', 95), ('A5', 110), ('D6', 127))):
        t = TP + 1 + i * BEAT
        M.add('xylo', xylo.play(n(m), v), t, 1.0, 0.0)
        M.add('drums', timp.play(70 + 15 * i), t, 0.5 + 0.15 * i)
        M.add('perc', wood.play(70), t, 0.5, span['Left'])
        M.add('perc', wood.play(70), t, 0.5, span['Right'])
    tutti(TX, 1.1)
    M.add('perc', slap.play(127), TX, 1.0)
    for i in range(14):                     # bones scattering in every direction
        M.add('xylo', xylo.play(n('D7') - 2 * i - int(M.rng.integers(0, 2)), 110 - 4 * i), TX + 0.04 * i, 0.8,
              float(M.rng.uniform(-0.8, 0.8)))
    M.add('perc', ratchet_f.play(90, dur=1.3), TX + 0.1, 0.6, span['Left'])
    M.add('perc', ratchet_f.play(90, dur=1.3), TX + 0.15, 0.6, span['Right'])
    for i in range(6):                      # the scattered bones twitch
        M.add('xylo', xylo.play(n('C7') + int(M.rng.integers(-5, 5)), 55), TX + 1.65 + 0.09 * i, 0.5,
              float(M.rng.uniform(-0.6, 0.6)))
    organ += [(50.0, n('D2'), 50, 6.0)]
    pitch = {1 + i: BASE['Porch Front'] + s for i, s in enumerate(STEPS)}
    pitch[0] = BASE['Porch Front'] - 12
    for r, b in enumerate(WRONG):           # the same notes as his assembly, in the wrong order
        land = TR + 0.5 * r + 0.42
        M.add('fx', whoosh(0.42, 1200, 4000, 0.4, seed=40 + r), land - 0.42, 0.5)
        M.add('xylo', xylo.play(pitch[b], 108), land, 1.0, 0.0)
        M.add('perc', wood.play(95), land, 0.7)
    M.add('fx', slide(0.0, 0.25, 600, 1500, 0.75, 0.6), TR + 3.2, 0.9)
    M.add('fx', slide(0.0, 0.17, 1500, 700, 0.17, 0.6), TR + 3.95, 0.9)
    ta = TR + 4.12
    M.add('perc', clave.play(120), ta, 1.0)
    M.add('brass', tpt.play(n('A4'), 110, dur=0.16), ta, 1.0, 0.1)
    for m in ('D5', 'F#5', 'A5'):           # ta-da, in the major for once
        M.add('brass', tpt.play(n(m), 118, dur=0.7), ta + 0.2, 0.9, 0.1)
    M.add('drums', crash_s.play(100), ta + 0.2, 0.6)

    # ---- 56-64: the dance again; he is half a beat late until he skips ahead at 62 ----
    for k in range(82, 98):
        t = beat(k)
        c = chord_at(t, ['Dm', 'A7'])
        if k % 2 == 0:
            M.add('bass', tuba.play(ROOT[c][(k // 2) % 2], 96), t)
        else:
            for m in CHORD[c]:
                M.add('pizz', pizz.play(m, 84), t, 0.7, -0.35)
        M.add('perc', wood.play(95), t, 0.8)
        late = 0.25 if t < TL + 6.0 else 0.0
        M.add('perc', cow.play(88), t + late, 0.55, span['Porch Front'])
    for rep in range(2):
        for b, m in melody:
            t = TL + rep * 4 * BEAT * 2 + b * BEAT
            if t >= TH:
                continue
            M.add('xylo', xylo.play(n(m), 100), t, 0.9, 0.1)
            if t < TL + 6.0:                # his glockenspiel echo, late
                M.add('mallet', glock.play(n(m), 90), t + 0.25, 0.7, span['Porch Front'])
            else:
                M.add('mallet', glock.play(n(m), 90), t, 0.7, span['Porch Front'])
    M.add('fx', slide(0.0, 0.12, 900, 2200, 0.14, 0.5), TL + 5.86, 0.8)
    tutti(TH)

    # ---- 65-68: collapse into heaps, pair by pair; he does one more pump on his own ----
    for k, g in (('Left', 0), ('Right', 0), ('Porch Left', 1), ('Porch Right', 1), ('Porch Front', 2)):
        tc = [65.5, 66.2, 67.4][g]
        p = span[k]
        for rank in range(6):
            M.add('xylo', xylo.play(BASE[k] + 12 - 3 * rank, 96 - 6 * rank), tc + 0.07 * rank, 0.7, p)
        M.add('perc', slap.play(80), tc + 0.55, 0.6, p)
        M.add('drums', bd.play(70), tc + 0.55, 0.4, p)
    M.add('perc', clave.play(110), 67.0, 1.0)
    M.add('bass', tuba.play(n('D2'), 110), 67.0)

    # ---- 68.6-77: skulls roll off the ends; his crawls to the edge, wobbles, and drops ----
    def exit_time(d0, sgn):
        tt = np.arange(0, 6, 0.01)
        x = d0 + sgn * 340 * (tt - 0.3 * (1 - np.exp(-tt / 0.3)))
        out = np.nonzero((x < -20) | (x > L + 20))[0]
        return tt[out[0]] if len(out) else 6.0, tt, x

    for k, ts, sgn in (('Left', 68.6, -1), ('Right', 68.6, 1), ('Porch Left', 69.4, -1), ('Porch Right', 69.4, 1)):
        te, tt, x = exit_time(mid[k], sgn)
        nrolls = int(te / 0.085)
        for i in range(nrolls):
            t = i * 0.085
            d = float(np.interp(t, tt, x))
            M.add('mallet', mar.play(n('D3') + (i % 2) * 5 - i // 6, 92 - 50 * i / max(nrolls, 1)), ts + t, 0.3,
                  pan_at(np.clip(d, 0, L)))
    for i in range(int(5.0 / 0.16)):        # his rolls slowly toward the right end
        t = 70.6 + i * 0.16 * (1 + 0.6 * i / 31)
        if t >= 75.6:
            break
        u = smoothstep(0, 1, (t - 70.6) / 5.0)
        d = mid['Porch Front'] + u * (L - mid['Porch Front'])
        M.add('mallet', mar.play(n('F3') + (i % 2) * 7, 88), t, 0.5, pan_at(d))
    M.add('strings', trem.play(n('A2'), 70, dur=1.9), 75.6, 1.0, 0.75)
    M.add('strings', trem.play(n('D3'), 70, dur=1.9), 75.6, 0.8, 0.75)
    M.add('drums', troll.play(55, dur=1.8), 75.6, 0.5, 0.75)
    M.add('perc', clave.play(100), 77.4, 0.9, 0.85)
    M.add('fx', slide(0.0, 0.5, 1400, 260, 0.55, 0.7), 77.42, 0.9, 0.85)
    M.add('drums', bd.play(110), 77.95, 0.9, 0.85)
    M.add('drums', timp.play(100, pitch=-5), 77.95, 0.7, 0.85)
    organ += [(78.3, n('D2'), 80, 2.6), (78.3, n('A2'), 70, 2.6), (78.3, n('F3'), 64, 2.6)]
    M.add('xylo', xylo.play(n('D6'), 70), 78.9, 0.8, 0.85)

    M.add('organ', M.synth('Keys/Church').render(organ, D), 0.0)
    M.add('calliope', M.synth('Keys/Circus 1').render(calliope, D), 0.0)
