"""Cauldron: the porch notch is a witch's pot of brew, simulated as 1-D shallow water along the roofline
(Rusanov fluxes with hydrostatic reconstruction over a bed with a rim at each front corner of the notch).
Ingredients are thrown in from the free ends; each lands with a crater whose waves run out, reflect off
the rims and slosh, and its dye is carried by the flow and diffuses through the brew. The last
Each ingredient is autocatalytic: its dye spreads as a reaction front (Fisher-KPP) that converts the
whole pot to its colour, murky green to violet to amber to toxic lime, and the lime brings it to a boil.
Foam and boiling raise the level until it spills over both rims and floods down the wings to the free
ends. Then the brew curdles (Cahn-Hilliard phase separation) into blobs that open their eyes: frogs,
which hop away off the free ends. One big frog stays behind, croaks twice and leaps off."""
import numpy as np
from pixelhome.fx import DT, hexc, light, smoothstep, keys, nframes

CODE = 'HW03'
TITLE = 'Hubble Bubble'
KIND = 'show'
DESCRIPTION = ('Ingredients fly in and splash into a sloshing cauldron in the porch, mixing their colours until '
               'it boils over and floods the house. Then the brew curdles into glowing frogs that hop away.')
VOICEOVER = 'Eye of newt, a pinch of moonlight, and whatever fell off the roof. The cauldron is bubbling. Stand back.'

MURK = hexc('#1f9a48')
PURPLE = hexc('#9a00ff')
AMBER = hexc('#ff5000')
LIME = hexc('#66ff00')
FOAM = hexc('#d8ffc0')
FROG = hexc('#40ff20')
EYE = hexc('#ffc800')
SAC = hexc('#e0ff90')
SPARK = hexc('#ffffff')

DX = 4.0                      # simulation cell, layout units
GRAV = 62500.0                # wave speed sqrt(g h) ~ 250 units/s at rest depth 1
D = 77.0
T_CROAK = 67.5               # the big frog croaks, then leaps off


def _swe_step(h, hu, b, dt):
    """One well-balanced Rusanov step (Audusse hydrostatic reconstruction), outflow at both ends.
    Returns new h, hu and the mass flux at the Nc+1 faces (for carrying tracers)."""
    hg = np.concatenate([h[:1], h, h[-1:]])
    qg = np.concatenate([hu[:1], hu, hu[-1:]])
    bg = np.concatenate([b[:1], b, b[-1:]])
    ug = np.where(hg > 1e-4, qg / np.maximum(hg, 1e-4), 0.0)
    hL, hR, bL, bR, uL, uR = hg[:-1], hg[1:], bg[:-1], bg[1:], ug[:-1], ug[1:]
    bf = np.maximum(bL, bR)
    hLs = np.maximum(0.0, hL + bL - bf)
    hRs = np.maximum(0.0, hR + bR - bf)
    qL, qR = hLs * uL, hRs * uR
    a = np.maximum(np.abs(uL) + np.sqrt(GRAV * hLs), np.abs(uR) + np.sqrt(GRAV * hRs))
    Fh = 0.5 * (qL + qR) - 0.5 * a * (hRs - hLs)
    Fm = 0.5 * (qL * uL + qR * uR + 0.5 * GRAV * (hLs ** 2 + hRs ** 2)) - 0.5 * a * (qR - qL)
    FmL = Fm + 0.5 * GRAV * (hL ** 2 - hLs ** 2)        # seen by the cell left of the face
    FmR = Fm + 0.5 * GRAV * (hR ** 2 - hRs ** 2)        # seen by the cell right of the face
    k = dt / DX
    h2 = np.maximum(h - k * (Fh[1:] - Fh[:-1]), 0.0)
    hu2 = hu - k * (FmL[1:] - FmR[:-1])
    hu2[h2 < 1e-4] = 0.0
    return h2, hu2, Fh


def _advect(C, h_old, h_new, Fh, dt):
    """Carry concentrations C (k, Nc) with the mass flux, upwind, conservatively."""
    Cg = np.concatenate([C[:, :1], C, C[:, -1:]], 1)
    up = np.where(Fh > 0, Cg[:, :-1], Cg[:, 1:])
    q = C * h_old - dt / DX * (Fh * up)[:, 1:] + dt / DX * (Fh * up)[:, :-1]
    wet = h_new > 1e-3
    return np.where(wet, q / np.maximum(h_new, 1e-3), C)


def _lap(x):
    xg = np.concatenate([x[..., :1], x, x[..., -1:]], -1)
    return xg[..., :-2] - 2 * x + xg[..., 2:]


class _Frog:
    def __init__(self, d, size, direction, rng, last=False):
        self.d, self.size, self.dir, self.rng, self.last = d, size, direction, rng, last
        self.t0 = None                                   # start of current hop
        self.d0 = self.d1 = d
        self.wait = rng.uniform(0.2, 1.6)
        self.gone = False
        self.hopdur = 0.55 if last else rng.uniform(0.32, 0.42)


def render(G, seed=13):
    rng = np.random.default_rng(seed)
    n = G.N
    F = nframes(D)
    out = np.zeros((F, n, 3))
    pdp = G.pd[G.path]                                   # distance along path, in path order
    L = G.length
    Nc = int(np.ceil(L / DX)) + 1
    xc = np.arange(Nc) * DX
    rimA = 0.5 * (pdp[178] + pdp[179])                   # Left | Porch Left
    rimB = 0.5 * (pdp[380] + pdp[381])                   # Porch Right | Right
    inside = (xc > rimA) & (xc < rimB)
    mid = 0.5 * (pdp[0] + pdp[-1])
    centre = 0.5 * (pdp[261] + pdp[331])                 # middle of Porch Front

    # Bed: pot floor 0, a rim of height 1.3 at each corner, wings slope from 0.95 down to the free ends.
    RIM = 1.3
    b = np.where(inside, 0.0, 0.0)
    left = xc < rimA
    right = xc > rimB
    b[left] = 0.95 * xc[left] / rimA
    b[right] = 0.95 * (L - xc[right]) / (L - rimB)
    b = np.maximum(b, RIM * np.exp(-((xc - rimA) / 7.0) ** 2))
    b = np.maximum(b, RIM * np.exp(-((xc - rimB) / 7.0) ** 2))
    h = np.where(inside, np.maximum(1.0 - b, 0.0), 0.0)
    # an initial lazy slosh
    h[inside] *= 1 + 0.06 * np.cos(np.pi * (xc[inside] - rimA) / (rimB - rimA))
    hu = np.zeros(Nc)
    # dyes: murk, purple, amber, lime
    C = np.zeros((4, Nc))
    C[0] = 1.0
    cols = np.stack([MURK, PURPLE, AMBER, LIME])
    foam = np.zeros(Nc)
    sparkle = np.zeros(Nc)
    trail = np.zeros(n)

    def gauss(x0, w):
        return np.exp(-((xc - x0) / w) ** 2)

    # Ingredients: (throw time, from end, landing distance, colour index, flight seconds)
    throws = [(1.6, L, centre + 140, 1, 1.4), (8.0, 0.0, 1110.0, 2, 1.7), (15.0, L, centre - 30, 3, 1.5)]
    landed = [False] * len(throws)
    react = -1                                           # the newest ingredient takes over the pot

    bubbles = []                                         # [x, t0, grow, amp]
    phi = None
    frogs = None
    splats = []                                          # (d, t0)
    t_curdle, t_frogs, t_eyes = 50.5, 54.0, 54.6

    for f in range(F):
        t = f * DT
        # ---------------- fluid phase ----------------
        if t < t_curdle + 1.0:
            heat = keys(t, [(0, 0.08), (16, 0.12), (22, 0.35), (32, 0.75), (38, 1.0), (46, 1.0), (49, 0.0)])
            # bubbles: rate grows with heat
            if t < 48.5 and rng.random() < heat * DT * (2.0 + 22.0 * heat):
                x = rng.uniform(rimA + 25, rimB - 25)
                bubbles.append([x, t, rng.uniform(0.25, 0.6), rng.uniform(0.05, 0.12) * (0.5 + heat)])
            # big glurps near the rims during the boil push surges over the edge
            for k, tg in enumerate(np.arange(33.0, 47.0, 1.7)):
                if tg <= t < tg + DT:
                    x = (rimA + 110 + rng.uniform(0, 60)) if k % 2 == 0 else (rimB - 110 - rng.uniform(0, 60))
                    bubbles.append([x, t, 0.7, 0.35])
            # foam expansion lifts the level during the boil
            swell = 0.085 * smoothstep(30, 34, t) * (1 - smoothstep(45, 47, t))
            nsub = 8
            dt = DT / nsub
            for _ in range(nsub):
                h_old = h
                h, hu, Fh = _swe_step(h, hu, b, dt)
                C = _advect(C, h_old, h, Fh, dt)
                foam = _advect(foam[None], h_old, h, Fh, dt)[0]
                h = h + swell * dt * inside
                # friction: gentle damping in the pot, bed drag on the thin film in the wings
                u = np.where(h > 1e-3, hu / np.maximum(h, 1e-3), 0)
                drag = np.where(inside, 0.12, 0.0) + 900.0 * np.abs(u) / (1 + 2000 * h) * (~inside) / 400.0
                hu = hu / (1 + dt * (drag + 0.05))
                # diffusion (dyes slowly, lime fast) and the lime reaction
                wet = h > 1e-3
                C += 1500.0 * dt / DX ** 2 * _lap(C) * wet
                if react >= 0:
                    r = react
                    g = 8.0 * C[r] * (1 - C[r]) * dt * wet
                    rest = np.maximum(1 - C[r], 1e-6)
                    others = np.arange(4) != r
                    C[others] -= C[others] / rest * g
                    C[r] += g
                C = np.clip(C, 0, None)
                C /= np.maximum(C.sum(0), 1e-6)
            foam *= np.exp(-DT / 1.3)
            sparkle *= np.exp(-DT / 0.12)

            # bubble pops: a mass-conserving dimple that radiates waves, a sparkle and foam
            keep = []
            for bb in bubbles:
                x, t0, grow, amp = bb
                if t - t0 >= grow:
                    wd = 9 + 80 * amp
                    dimple = amp * (gauss(x, wd) - 0.5 * gauss(x, 2 * wd))
                    h = np.maximum(h - dimple * inside, 0)
                    sparkle = np.maximum(sparkle, 0.9 * gauss(x, 5) * (0.4 + amp * 6))
                    foam = np.minimum(foam + 0.5 * heat * gauss(x, 14), 1.2)
                else:
                    keep.append(bb)
            bubbles = keep

            # ingredients
            for i, (t0, frm, land, ci, fl) in enumerate(throws):
                if t0 <= t < t0 + fl:
                    u_ = (t - t0) / fl
                    dpos = frm + (land - frm) * (1 - (1 - u_) ** 1.6)
                    k = np.exp(-((pdp - dpos) / 7.0) ** 2)
                    trail = np.maximum(trail, k)
                elif t >= t0 + fl and not landed[i]:
                    landed[i] = True
                    # splash: a crater, the displaced brew thrown up around it
                    h = np.maximum(h - 0.40 * (gauss(land, 40) - 0.5 * gauss(land, 80)) * inside, 0)
                    C[:, :] = C * (1 - gauss(land, 70))
                    C[ci] += gauss(land, 70)
                    sparkle = np.maximum(sparkle, 1.2 * gauss(land, 14))
                    foam = np.minimum(foam + 0.6 * gauss(land, 30), 1.2)
                    react = ci
            trail *= np.exp(-DT / 0.18)

            # ---- draw the brew ----
            eta = h + b
            pot_level = eta[inside].mean() if inside.any() else 1.0
            depth = h
            wetv = smoothstep(0.003, 0.03, depth)
            # brightness: a steady glow, crests bright and troughs dark, plus foam and sparkle
            I = np.where(inside, 0.56 + 0.14 * heat + 2.6 * (eta - pot_level), 0.52 + 0.9 * depth)
            I = np.clip(I, 0.04, 0.85) * wetv
            # the thin leading edge of the flood is froth
            froth = (~inside) * wetv * (1 - smoothstep(0.03, 0.09, depth))
            foam = np.maximum(foam, froth)
            I *= keys(t, [(0, 0), (1.2, 1)])
            col = C.T @ cols
            Ic = np.interp(pdp, xc, I)
            colp = np.stack([np.interp(pdp, xc, col[:, c]) for c in range(3)], -1)
            fp = np.interp(pdp, xc, np.clip(foam * wetv, 0, 1))
            sp = np.interp(pdp, xc, sparkle)
            # growing bubbles: a bright dome
            dome = np.zeros(n)
            for x, t0, grow, amp in bubbles:
                dome = np.maximum(dome, (t - t0) / grow * np.exp(-((pdp - x) / (8.0 + 60 * amp)) ** 2) * (0.25 + amp * 3))
            buf = light(1, Ic + 0.35 * dome) * colp
            buf = buf * (1 - 0.6 * fp[:, None]) + light(FOAM, 0.55 * fp)
            buf += light(SPARK, np.clip(sp, 0, 1) * 0.8)
            for i, (t0, frm, land, ci, fl) in enumerate(throws):
                if t0 - 0.5 <= t < t0 + fl + 0.3:
                    buf += light(cols[ci] * 0.6 + 0.4 * SPARK, 0.85 * trail)
            fluid_buf = buf
            if t < t_curdle:
                out[f][G.path] = buf
                continue

        # ---------------- curdle ----------------
        if phi is None:
            wet_c = h > 0.004
            phi = np.where(wet_c, -0.3 + 0.1 * rng.standard_normal(Nc), -1.0)
            glow0 = fluid_buf
        if t < t_frogs + 0.5:
            for _ in range(36):
                mu = phi ** 3 - phi - 1.8 * _lap(phi)
                phi = phi + 0.008 * _lap(mu)
        blob = smoothstep(-0.5, 0.9, phi)
        bp = np.interp(pdp, xc, blob)
        mix = smoothstep(t_curdle, t_curdle + 1.0, t)
        curd = light(LIME, 0.72 * bp)
        buf = glow0 * (1 - mix) * (1 - smoothstep(t_curdle + 0.5, t_curdle + 2.0, t)) + curd * mix

        # ---------------- frogs ----------------
        if t >= t_frogs:
            if frogs is None:
                runs, cur = [], None
                pos = phi > 0
                for i in range(Nc):
                    if pos[i] and cur is None:
                        cur = i
                    if not pos[i] and cur is not None:
                        runs.append((cur, i - 1))
                        cur = None
                if cur is not None:
                    runs.append((cur, Nc - 1))
                frogs = []
                for a, z in runs:
                    if z - a < 2:
                        continue
                    w = blob[a:z + 1]
                    d = float((xc[a:z + 1] * w).sum() / w.sum())
                    frogs.append(_Frog(d, (z - a + 1) * DX, -1 if d < mid else 1, rng))
                j = int(np.argmin([abs(fr.d - centre) for fr in frogs]))
                frogs[j].last, frogs[j].dir, frogs[j].hopdur = True, 1, 0.6
                frogs[j].size *= 1.5
            mixf = smoothstep(t_frogs, t_frogs + 0.4, t)
            buf = buf * (1 - mixf)
            fb = np.zeros(n)
            eyes = np.zeros(n)
            sac = np.zeros(n)
            for fr in frogs:
                if fr.gone:
                    continue
                if fr.last:
                    # waits for the others, then croaks twice and makes huge leaps to the right end
                    if t < T_CROAK:
                        air = 0.0
                    else:
                        if fr.t0 is None or t - fr.t0 >= fr.hopdur:
                            if fr.t0 is not None:
                                fr.d = fr.d1
                                splats.append((fr.d, t, 1.0))
                            if t >= T_CROAK + 2.1:
                                fr.t0, fr.d0, fr.d1 = t, fr.d, fr.d + 210
                            else:
                                fr.t0 = None
                        air = 0.0
                        if fr.t0 is not None:
                            u_ = (t - fr.t0) / fr.hopdur
                            fr.d = fr.d0 + (fr.d1 - fr.d0) * u_
                            air = np.sin(np.pi * u_)
                        for c0 in (T_CROAK + 0.2, T_CROAK + 1.2):
                            s = np.clip(np.sin(np.pi * (t - c0) / 0.6), 0, None) if c0 <= t < c0 + 0.6 else 0
                            sac += s * np.exp(-((pdp - (fr.d + 0.9 * fr.size)) / (4 + 10 * s)) ** 2)
                    if fr.d > L + 40:
                        fr.gone = True
                        continue
                else:
                    if t < t_eyes + 0.3:
                        air = 0.0
                    elif fr.t0 is not None and t - fr.t0 < fr.hopdur:
                        u_ = (t - fr.t0) / fr.hopdur
                        fr.d = fr.d0 + (fr.d1 - fr.d0) * u_
                        air = np.sin(np.pi * u_)
                    else:
                        if fr.t0 is not None:
                            fr.d = fr.d1
                            fr.t0 = None
                            splats.append((fr.d, t, 0.35))
                            fr.wait = fr.rng.uniform(0.1, 0.5) if fr.dir > 0 else fr.rng.uniform(0.05, 0.3)
                        fr.wait -= DT
                        air = 0.0
                        if fr.wait <= 0:
                            hop = fr.rng.uniform(55, 95) if fr.dir > 0 else fr.rng.uniform(95, 140)
                            ahead = [o.d for o in frogs if o is not fr and not o.gone and not o.last and o.dir == fr.dir
                                     and 0 < (o.d - fr.d) * fr.dir]
                            if ahead:
                                gap = min(abs(o - fr.d) for o in ahead)
                                hop = min(hop, gap - 26)
                            if hop > 12:
                                fr.t0, fr.d0, fr.d1 = t, fr.d, fr.d + fr.dir * hop
                            else:
                                fr.wait = 0.15
                    if fr.d < -30 or fr.d > L + 30:
                        fr.gone = True
                        continue
                w = fr.size * (0.32 + 0.18 * air)
                fb = np.maximum(fb, (0.68 + 0.15 * air) * np.exp(-((pdp - fr.d) / max(w, 4)) ** 2))
                # one eye on the leading edge; blinks at birth and now and then
                e = fr.d + fr.dir * (fr.size * 0.45)
                open_ = smoothstep(t_eyes, t_eyes + 0.25, t)
                if (t_eyes + 0.9 < t < t_eyes + 1.0) or ((t * 0.37 + fr.d * 0.01) % 1 < 0.03):
                    open_ = 0
                eyes = np.maximum(eyes, open_ * np.clip(1 - np.abs(pdp - e) / 3.5, 0, 1))
            spl = np.zeros(n)
            keep = []
            for d0, ts, sk in splats:
                age = t - ts
                life = 0.45 + 0.4 * sk
                if age < life:
                    keep.append((d0, ts, sk))
                    r = 8 + (70 + 120 * sk) * age
                    ring = np.exp(-((np.abs(pdp - d0) - r) / (5.0 + 6 * sk)) ** 2)
                    spl = np.maximum(spl, (1 - age / life) * sk * ring)
            splats = keep
            buf = buf + light(FROG, fb) + light(LIME, spl)
            buf = buf * (1 - np.clip(eyes, 0, 1))[:, None] + light(EYE, 0.85 * eyes)
            buf += light(SAC, 0.9 * np.clip(sac, 0, 1))
            # one last bubble rises in the empty pot and pops
            tb, tp = T_CROAK + 6.0, T_CROAK + 7.6
            if tb <= t < tp:
                u_ = (t - tb) / (tp - tb)
                buf += light(LIME, 0.55 * u_ ** 1.5 * np.exp(-((pdp - centre) / (6 + 18 * u_)) ** 2))
            elif tp <= t < tp + 0.8:
                age = t - tp
                ring = np.exp(-((np.abs(pdp - centre) - 20 - 160 * age) / 8.0) ** 2)
                buf += light(LIME, 0.6 * (1 - age / 0.8) * ring)
                buf += light(SPARK, 0.9 * np.exp(-age / 0.08) * np.exp(-((pdp - centre) / 10) ** 2))
        out[f][G.path] = buf
    return np.clip(out, 0, 1)


# ---------------------------------------------------------------- music ----------------------------------------------
# A witches' waltz in E minor that boils. Its downbeats are pinned to the lights: the three ingredients land on bars
# 0, 4 and 8, each bringing in a new colour of the tune (clarinet for violet, muted horn for amber, a squelchy synth for
# lime), and from the lime the waltz speeds up with the heat until every other downbeat is one of the big glurps at the
# rims. Every bubble that pops in the pot is a little upward-chirping bloop pitched from the chord of the moment, small
# bubbles high, so the plucks thicken as it heats; when the brew spills, a harp runs down each wing with the flood
# front. It curdles with a trombone fall, the frogs' eyes open on an E major chord and they hop away to the same tune in
# the major, each landing a ribbit, the band thinning as they leave. The big frog croaks twice and leaps off on slide
# whistles. Times come from render() itself (bubbles, hops and the flood are random or simulated, so score() runs it
# once with its random generator and its frogs on tape) and sounds are panned to where they happen on the house.

HEAT = [(0, 0.08), (16, 0.12), (22, 0.35), (32, 0.75), (38, 1.0), (46, 1.0), (49, 0.0)]   # render()'s heat keys
T_CURDLE, T_FROGS, T_EYES = 50.5, 54.0, 54.6                                             # as in render()
CH = {'Em': (40, (4, 7, 11)), 'Am': (33, (9, 0, 4)), 'B7': (35, (11, 3, 6, 9)), 'C': (36, (0, 4, 7)),
      'F': (41, (5, 9, 0)), 'E': (40, (4, 8, 11)), 'A': (33, (9, 1, 4)), 'C#m': (37, (1, 4, 8))}
PROG_A = ['Em', 'Am', 'B7', 'Em', 'C', 'Am', 'B7', 'Em']
TUNE_A = [[('B4', 1), ('E5', 1), ('G5', 1)], [('A5', 2), ('C6', 1)], [('B5', 1), ('A5', 1), ('D#5', 1)],
          [('E5', 3)], [('E5', 1), ('G5', 1), ('C6', 1)], [('C6', 1), ('B5', 1), ('A5', 1)],
          [('A5', 1), ('F#5', 1), ('D#5', 1)], [('E5', 2), ('B4', 1)]]
PROG_B = ['Em', 'F', 'Em', 'F', 'Am', 'B7']              # the bubbling strain: up a semitone and back, twice
TUNE_B = [[('E5', 1), ('G5', 1), ('B5', 1)], [('F5', 1), ('A5', 1), ('C6', 1)], [('E5', 1), ('G5', 1), ('B5', 1)],
          [('F5', 1), ('A5', 1), ('C6', 1)], [('A5', 1), ('C6', 1), ('E6', 1)], [('D#6', 1), ('B5', 1), ('F#5', 1)]]
MAJOR = {'Em': 'E', 'Am': 'A', 'B7': 'B7', 'C': 'C#m'}  # the frogs' version
SCALE = (0, 2, 3, 4, 6, 7, 9, 11)                       # E harmonic minor with a G# for the floods: E F# G G# A B C D#
ON = {'clar': 0.11, 'horn': 0.14, 'buzz': 0.19, 'fall': 0.17}   # measured lead-in before these samples speak
LEVEL = [(0, 0.5), (3.5, 0.32), (16.5, 0.38), (26, 0.5), (33.7, 0.8), (38, 1.0), (47.3, 1.0), (50.5, 0.85),
         (51.5, 1.0)]                                   # the band's level, by measurement against the lights


def _events(G):
    """Run render() once with its random generator and its frogs on tape. Bubbles and hops are random and the frogs
    come out of the curdling, so their times can only come from the render. Returns the frames, the bubble spawns
    [('bubble', frame, x, grow, size)] and glurps [('glurp', frame, offset)], and the frogs (with .born and .hops)."""
    pops, frogs = [], []

    class Tape:
        def __init__(self, g):
            self.g, self.frame, self.spawn = g, -1, None

        def random(self, *a):
            self.frame += 1                              # render() draws exactly one random() per frame before 48.5 s
            return self.g.random(*a)

        def uniform(self, lo, hi, *a):
            v = self.g.uniform(lo, hi, *a)
            if self.spawn is not None:
                self.spawn.append(v)
                if len(self.spawn) == 3:
                    pops.append(('bubble', self.frame) + tuple(self.spawn))
                    self.spawn = None
            elif lo > 100:                               # uniform(rimA + 25, rimB - 25): a new bubble's position
                self.spawn = [v]
            elif (lo, hi) == (0, 60):                    # a big glurp near a rim
                pops.append(('glurp', self.frame, v))
            return v

        def __getattr__(self, k):
            return getattr(self.g, k)

    class Frog(_Frog):
        def __init__(self, d, *a, **k):
            self.hops, self.born = [], d
            super().__init__(d, *a, **k)
            frogs.append(self)

        def __setattr__(self, k, v):
            object.__setattr__(self, k, v)
            if k == 'd1' and getattr(self, 't0', None) is not None:
                self.hops.append((self.t0, self.d0, v, self.hopdur))

    g, real_rng, real_frog = globals(), np.random.default_rng, _Frog
    np.random.default_rng = lambda seed=None: Tape(real_rng(seed))
    g['_Frog'] = Frog
    try:
        frames = render(G)
    finally:
        np.random.default_rng, g['_Frog'] = real_rng, real_frog
    return frames, pops, frogs


def score(M, G):
    from pixelhome.audio import SR, note, slide, whoosh
    n = note
    frames, spawns, frogs = _events(G)
    F = len(frames)
    ft = np.arange(F) * DT

    def frame_at(x):                        # the first frame render() treats as at or after time x
        return float(ft[np.nonzero(ft >= x)[0][0]])

    def after(t0, dur):                     # render()'s `t - t0 >= dur` test, on the frame grid
        return float(ft[np.nonzero(ft - t0 >= dur)[0][0]])

    order = np.argsort(G.pd)
    xs, ds = G.pos[order, 0], G.pd[order]
    x0, x1 = xs.min(), xs.max()
    pdp = G.pd[G.path]
    L = G.length
    rimA, rimB = 0.5 * (pdp[178] + pdp[179]), 0.5 * (pdp[380] + pdp[381])
    centre = 0.5 * (pdp[261] + pdp[331])

    def pan_at(d):                          # path distance -> left/right across the facade, as seen from the street
        x = np.interp(d, ds, xs)
        return 0.85 * (2 * (x - x0) / (x1 - x0) - 1)

    def moving(sig, t, d_of_t):             # pan a sound sample by sample along a path through the house
        tt = t + np.arange(sig.shape[1]) / SR
        a = (pan_at(np.clip(d_of_t(tt), 0, L)) + 1) * np.pi / 4
        return sig * np.vstack([np.cos(a), np.sin(a)]) * np.sqrt(2)

    def heat(t):
        return float(keys(t, HEAT))

    def bloop(f, dur=0.09, rise=1.7, amp=0.5):   # a bubble: a sine that chirps upward as it rings out
        tt = np.arange(int(dur * SR)) / SR
        fr = f * (1 + (rise - 1) * (1 - np.exp(-tt / (dur * 0.35))))
        sig = amp * np.sin(2 * np.pi * np.cumsum(fr) / SR) * (1 - np.exp(-tt / 0.002)) * np.exp(-tt / (dur * 0.3))
        return np.vstack([sig, sig])

    def voicing(c, lo, k=None):             # chord tones from MIDI lo upward
        pcs = CH[c][1][:k]
        return sorted(lo + (pc - lo) % 12 for pc in pcs)

    clar = M.sampler('Woodwinds/Clarinet/susLong/*.wav')
    clar_st = M.sampler('Woodwinds/Clarinet/stac/*.wav')
    bsn = M.sampler('Woodwinds/Bassoon/stac/*.wav')
    picc = M.sampler('Woodwinds/Piccolo/Stac/*.wav')
    horn_m = M.sampler('Brass/F Horn/mute/*.wav')
    horn = M.sampler('Brass/F Horn/sus/*.wav')
    tuba = M.sampler('Brass/Tuba/sus/*.wav')
    tbn_fall = M.sampler('Brass/OldTrombone/Fall/*.wav')
    tbn_buzz = M.sampler('Brass/OldTrombone/Buzz/*.wav')
    harp = M.sampler('Strings/Harp/*.wav')
    vln_sp = M.sampler('Strings/Violin Section/Spic/*.wav')
    vln_pz = M.sampler('Strings/Violin Section/Pizz/*.wav')
    vla_pz = M.sampler('Strings/Viola Section/pizz/*.wav')
    vln_tr = M.sampler('Strings/Violin Section/Trem/*.wav')
    cb_pz = M.sampler('Strings/Solo Contrabass/Pizz/*.wav')
    glock = M.sampler('Percussion/Glock/*.wav')
    timp = M.hits('Percussion/Timpani/Timpani1_Hit*.wav')
    bd = M.hits('Percussion/BDrumNewhit_v[3-6]*.wav')
    cym = M.hits('Percussion/susCymb1-hit_f_*.wav')
    cym_up = M.hits('Percussion/susCymb1-cresc-Short*.wav')
    gong = M.hits('Percussion/gongscrape_pp.wav')
    guiro = M.hits('Percussion/Guiro-Hit*.wav')
    brew = M.hits('Miscellania Raw/Misc 1/bubbles*.wav')
    zap = M.hits('Percussion/zap[12]_v1.wav')

    def boil_up(dur):                       # a burst of real bubbling, from its loudest moment
        s = brew.play(127)
        k = max(0, int(np.argmax(np.abs(s).mean(0))) - int(0.05 * SR))
        s = s[:, k:k + int(dur * SR)].copy()
        s[:, -int(0.3 * SR):] *= np.linspace(1, 0, int(0.3 * SR))
        return s

    for name, gain, rev in (('bass', 0.5, 0.1), ('pah', 0.32, 0.2), ('tune', 0.42, 0.25), ('lead', 0.3, 0.2),
                            ('choir', 0.3, 0.45), ('bubbles', 0.3, 0.3), ('brew', 0.16, 0.2), ('perc', 0.5, 0.2),
                            ('fx', 0.3, 0.3), ('frogs', 0.42, 0.18), ('pad', 0.3, 0.5)):
        M.bus(name, gain=gain, reverb=rev)

    # ---- the bar grid: ingredients on bars 0, 4, 8; accelerando with the heat to the glurps; 16 bars of boil ----
    throws = [(1.6, L, centre + 140, 1, 1.4), (8.0, 0.0, 1110.0, 2, 1.7), (15.0, L, centre - 30, 3, 1.5)]  # render()
    lands = [frame_at(t0 + fl) for t0, _, _, _, fl in throws]
    glurps = []
    for _, f, v in [p for p in spawns if p[0] == 'glurp']:
        k = int(round((ft[f] - 33.0) / 1.7))
        x = rimA + 110 + v if k % 2 == 0 else rimB - 110 - v
        glurps.append((after(ft[f], 0.7), x, k))
    tb0, tb1 = glurps[0][0], glurps[-1][0]
    nboil = int(round((tb1 - tb0) / 1.7)) * 2
    bars = [lands[0] + i * (lands[1] - lands[0]) / 4 for i in range(4)]
    bars += [lands[1] + i * (lands[2] - lands[1]) / 4 for i in range(4)]

    def ramp(c, t):
        out = []
        while t < tb0 - 0.3:
            out.append(t)
            t += c / (1 + 1.32 * heat(t))
        return out, t

    lo_c, hi_c = 1.5, 2.5
    for _ in range(40):                     # fit the accelerando so a whole number of bars ends on the first glurp
        c = 0.5 * (lo_c + hi_c)
        acc, end = ramp(c, lands[2])
        if len(acc) != 14:
            lo_c, hi_c = (c, hi_c) if len(acc) > 14 else (lo_c, c)
            continue
        lo_c, hi_c = (c, hi_c) if end < tb0 else (lo_c, c)
    acc, end = ramp(c, lands[2])
    acc = [lands[2] + (a - lands[2]) * (tb0 - lands[2]) / (end - lands[2]) for a in acc]   # land exactly on it
    bars += acc
    bars += [tb0 + i * (tb1 - tb0) / nboil for i in range(nboil)]
    rit = np.array([1.0, 1.1, 1.22])
    rit = tb1 + np.concatenate([[0], np.cumsum(rit * (T_CURDLE - tb1) / rit.sum())])
    bars += list(rit[:-1])
    bars.append(T_CURDLE)
    bars = np.array(bars)
    blen = np.diff(bars)
    B0, BB, BR = 8, 8 + len(acc), 8 + len(acc) + nboil   # first lime bar, first boil bar, first rit bar
    assert (BB, nboil) == (22, 16), (BB, nboil)
    chords = PROG_A + PROG_A + PROG_B + PROG_A + PROG_A + ['Am', 'B7', 'B7']
    tunes = TUNE_A + TUNE_A + TUNE_B + TUNE_A + TUNE_A + [[('C6', 3)], [('B5', 1), ('A5', 1), ('F#5', 1)], [('D#5', 3)]]

    # the frogs' waltz: ten bars from the eyes opening to the croak
    fbar = T_EYES + np.arange(11) * (T_CROAK - T_EYES) / 10
    fchords = ['E'] + [MAJOR[c] for c in PROG_A] + ['E']

    def chord_at(t):
        if t >= T_FROGS:
            return fchords[min(9, max(0, int(np.searchsorted(fbar, t, 'right')) - 1))]
        return chords[min(len(chords) - 1, max(0, int(np.searchsorted(bars, t, 'right')) - 1))]

    # ---- the waltz itself ----
    lead_n, choir_n = [], []
    for i in range(len(bars) - 1):
        t, bl, c = bars[i], blen[i], chords[i]
        bt = bl / 3
        root, _ = CH[c]
        boil = BB <= i < BR
        dyn = 0.7 + 0.3 * heat(t) if i < BR else 0.9 - 0.15 * (i - BR)
        # oom: bassoon, then contrabass under it from the lime, tuba in the boil
        M.add('bass', bsn.play(root + 12 * (root < 38), int(95 * dyn)), t, 0.9)
        if i >= B0:
            M.add('bass', cb_pz.play(root, int(105 * dyn)), t, 0.8)
        if boil or i >= BR:
            M.add('bass', tuba.play(root - 12 * (root > 38), int(110 * dyn), dur=bt * 0.9), t, 0.7)
        # pah-pah: harp, viola pizz from the lime, violins in the boil
        if i < BR:
            for b in (1, 2):
                for m in voicing(c, 55):
                    M.add('pah', harp.play(m, int(80 * dyn)), t + b * bt, 0.55, -0.25)
                    if i >= B0:
                        M.add('pah', vla_pz.play(m, int(90 * dyn)), t + b * bt, 0.6, 0.3)
                    if boil:
                        M.add('pah', vln_pz.play(m + 12, int(100 * dyn)), t + b * bt, 0.6, -0.4)
        # the tune, in the colour of the last ingredient
        beat = 0
        for name, nb in tunes[i]:
            m, tt, dd = n(name), t + beat * bt, nb * bt
            if i < 4:                        # violet: clarinet
                M.add('tune', clar.play(m - 12, 92, dur=dd * 0.95, release=0.15), tt - ON['clar'], 1.0, 0.15)
            elif i < B0:                     # amber: muted horn, the clarinet a sixth below
                M.add('tune', horn_m.play(m - 12, 100, dur=dd * 0.92), tt, 0.7, 0.1)
                M.add('tune', clar.play(m - 21 + (m % 12 in (4, 11)), 70, dur=dd * 0.9), tt - ON['clar'], 0.5, 0.3)
            elif i < BB:                     # lime: the squelch, doubled by staccato clarinet
                lead_n.append((tt, m, int(80 + 30 * heat(tt)), dd * 0.8))
                M.add('tune', clar_st.play(m - 12, 95), tt, 0.7, 0.15)
            elif i < BR:                     # the boil: violins spiccato, squelch on top, horns hold the chord
                M.add('tune', vln_sp.play(m, 118), tt, 1.0, -0.1)
                lead_n.append((tt, m + 12 * (i >= BB + 8), 112, dd * 0.6))
            else:                            # running out of heat: horn and clarinet alone
                M.add('tune', horn.play(m - 12, 100, dur=dd * 0.95), tt - ON['horn'], 0.9, 0.1)
                M.add('tune', clar.play(m - 12, 90, dur=dd * 0.95), tt - ON['clar'], 0.7, 0.15)
            beat += nb
        if boil:
            for m in voicing(c, 52, 3):
                M.add('tune', horn.play(m, 100, dur=bl * 0.95), t - ON['horn'], 0.45, 0.25)
            for m in voicing(c, 64, 3):
                choir_n.append((t, m, 90, bl * 0.98))
        elif i >= BR:
            for m in voicing(c, 52):
                choir_n.append((t, m, 70, bl * 0.98))
    # the splashes, each with its own colour, and the flight of each ingredient across the house
    for (t0, frm, land, ci, fl), tl in zip(throws, lands):
        p = float(pan_at(land))
        M.add('fx', moving(whoosh(fl + 0.1, 500, 2600, 0.5, seed=ci), t0,
                           lambda tt: frm + (land - frm) * (1 - (1 - np.clip((tt - t0) / fl, 0, 1)) ** 1.6)), t0, 0.6)
        M.add('perc', timp.play(105, pitch=-3), tl, 0.8, p)
        M.add('perc', cym.play(85), tl, 0.35, p)
        M.add('brew', boil_up(1.2), tl, 2.5, p)
        M.add('bubbles', bloop(130, 0.3, 2.2, 0.8), tl, 1.0, p)
        if ci == 1:                          # violet: a harp sweeping up under the flight
            for j, m in enumerate(voicing('Em', 52) + voicing('Em', 64) + voicing('Em', 76)):
                tt = t0 + 0.15 + j * (fl - 0.2) / 9
                M.add('pah', harp.play(m, 85), tt, 0.8, float(pan_at(frm + (land - frm) * (tt - t0) / fl)))
        elif ci == 2:                        # amber: a horn rips up out of the splash
            M.add('tune', horn.play(n('E3'), 112, dur=0.9), tl - ON['horn'], 0.7, p)
            M.add('tune', horn.play(n('B3'), 112, dur=0.9), tl + 0.06 - ON['horn'], 0.6, p)
        else:                                # lime: a zap
            M.add('fx', zap.play(110), tl, 0.9, p)
    # glurps: a deep bloop at the rim, timpani and bass drum on the downbeat
    for tg, x, k in glurps:
        p = float(pan_at(x))
        M.add('bubbles', bloop(70, 0.5, 2.0, 1.0), tg, 1.0, p)
        M.add('perc', timp.play(118, pitch=-5), tg, 0.9, p)
        M.add('perc', bd.play(110), tg, 0.8, p)
        M.add('brew', boil_up(1.0), tg, 2.0, p)

    # every bubble that pops: a chirp from the chord of the moment, the small ones high
    for _, f, x, grow, raw in [p for p in spawns if p[0] == 'bubble']:
        tp = after(ft[f], grow)
        size = raw * (0.5 + heat(ft[f]))
        tones = [m for m in voicing(chord_at(tp), 72) + voicing(chord_at(tp), 84) + voicing(chord_at(tp), 96)
                 if m <= 100]
        u = np.clip((size - 0.025) / 0.155, 0, 1)
        m = tones[int(round((1 - u) * (len(tones) - 1)))]
        f0 = 440 * 2 ** ((m - 69) / 12) / 1.7 * 1.25
        M.add('bubbles', bloop(f0, 0.07 + 0.08 * u, 1.7, 0.18 + 0.5 * u), tp, 1.0, float(pan_at(x)))
    # the brew's own bubbling under it, as loud as the heat
    bed = np.zeros((2, int(T_CURDLE * SR)))
    pos = int(0.5 * SR)
    while pos < bed.shape[1]:
        s = brew.play(127)
        e = min(bed.shape[1], pos + s.shape[1])
        bed[:, pos:e] += s[:, :e - pos] * np.hanning(s.shape[1])[:e - pos]
        pos += int(s.shape[1] * 0.5)
    tt = np.arange(bed.shape[1]) / SR
    bed *= np.interp(tt, np.arange(0, 51, 0.25), [heat(t) ** 1.3 for t in np.arange(0, 51, 0.25)])
    bed *= 1 - smoothstep(47.5, 49.0, tt)
    M.add('brew', bed, 0.0, 0.8)

    # ---- the flood: a harp runs down each wing with the front, and a rush of water behind it ----
    lit = frames[:, G.path].max(-1) > 0.02
    for lo_i, hi_i, sgn, top, steps in ((0, 179, -1, n('E6'), 22), (381, 501, 1, n('B6'), 14)):
        front = []
        for f in range(F):
            if not 34.0 <= ft[f] <= 47.0:
                continue
            idx = np.nonzero(lit[f, lo_i:hi_i])[0]
            if len(idx):
                d = pdp[lo_i + (idx.min() if sgn < 0 else idx.max())]
                front.append((ft[f], d))
        ftm = np.array([a for a, _ in front])
        fd = np.array([b for _, b in front])
        fd = np.minimum.accumulate(fd) if sgn < 0 else np.maximum.accumulate(fd)
        rim, end = (rimA, 0.0) if sgn < 0 else (rimB, L)
        frac = (fd - rim) / (end - rim)
        ok = frac > 0.01
        t_spill, t_end = ftm[ok][0], ftm[frac >= 0.995][0]
        notes, m = [], top
        while len(notes) < steps:
            if (m - 40) % 12 in SCALE:
                notes.append(m)
            m -= 1
        for k, m in enumerate(notes):
            tk = float(np.interp((k + 0.5) / steps, frac, ftm))
            M.add('pah', harp.play(m, 100), tk, 0.9, float(pan_at(np.interp(tk, ftm, fd))))
        M.add('perc', cym.play(110), t_spill, 0.6, float(pan_at(rim)))
        if sgn > 0:                          # a cymbal swells into the flood reaching the right end
            M.add('perc', cym_up.play(90), t_end - 1.52, 0.5, float(pan_at(end)))
        rush = whoosh(t_end - t_spill + 0.6, 2400, 500, 0.6, seed=sgn + 5)
        M.add('fx', moving(rush, t_spill, lambda q: np.interp(q, ftm, fd)), t_spill, 0.8)

    # ---- the curdle: the waltz deflates; blobs form in the dark ----
    M.add('tune', tbn_fall.play(n('E2'), 110), T_CURDLE - ON['fall'], 0.9)
    M.add('bass', tuba.play(n('E1'), 110, dur=1.0), T_CURDLE, 0.5)
    M.add('perc', timp.play(100, pitch=-7), T_CURDLE, 0.4)
    M.add('perc', gong.play(127), T_CURDLE + 0.6, 0.3)
    pad_n = [(T_CURDLE + 0.8, n('E3'), 60, T_FROGS - T_CURDLE - 0.6), (T_CURDLE + 1.6, n('F3'), 55, 2.4),
             (T_CURDLE + 2.2, n('B3'), 60, 1.6)]
    for m in (n('E5'), n('F5')):
        M.add('pad', vln_tr.play(m, 60, dur=2.4), T_CURDLE + 1.2, 0.5)
    for j in range(6):                       # the brew separating: slow low gloops
        tg = T_CURDLE + 1.1 + j * 0.45
        M.add('bubbles', bloop(110 - 8 * j, 0.25, 1.5, 0.4), tg, 0.8, float(M.rng.uniform(-0.6, 0.6)))

    # ---- frogs: they pop out, their eyes open on E major, and they hop away to the waltz in the major ----
    for m in voicing('E', 64):
        M.add('pah', vln_pz.play(m, 110), T_FROGS, 0.8)
    M.add('bubbles', bloop(160, 0.2, 2.0, 0.7), T_FROGS, 1.0)
    pings = [n('E6'), n('G#6'), n('B6'), n('E7')]
    for j, fr in enumerate(sorted(frogs, key=lambda q: q.born)):
        M.add('frogs', glock.play(pings[j % 4], 70), T_EYES + 0.008 * j, 0.35, float(pan_at(fr.born)))
    for tb in (T_EYES + 0.9, T_EYES + 1.0):  # the blink
        M.add('frogs', harp.play(n('E7'), 70), tb, 0.5)

    def gone_at(fr):                         # when a frog has hopped off the end of the house
        t0, d0, d1, hd = fr.hops[-1]
        return t0 + hd * 0.5 if (d1 < -30 or d1 > L + 30) else 99.0

    small = [fr for fr in frogs if not fr.last]
    for fr in small:
        semis = int(round(np.interp(fr.size, [12, 28], [5, -4])))
        for t0, d0, d1, hd in fr.hops:
            if d1 < -30 or d1 > L + 30:
                continue
            tl = after(t0, hd)
            M.add('frogs', guiro.play(int(M.rng.integers(70, 100)), pitch=semis), tl, 0.5, float(pan_at(d1)))
    for i in range(10):
        t, bl, c = fbar[i], fbar[i + 1] - fbar[i], fchords[i]
        bt = bl / 3
        alive = sum(gone_at(fr) > t for fr in small) / len(small)
        dyn = 0.45 + 0.55 * alive
        root = CH[c][0]
        M.add('bass', bsn.play(root + 12 * (root < 38), int(105 * dyn)), t, 0.6, -0.2)
        for b in (1, 2):
            for m in voicing(c, 60, 3):
                M.add('pah', vln_pz.play(m, int(90 * dyn)), t + b * bt, 0.55, 0.25)
        if 1 <= i <= 8:
            beat = 0
            for name, nb in TUNE_A[i - 1]:
                m = n(name)
                if m % 12 in (7, 0) and MAJOR[PROG_A[i - 1]] in ('E', 'A', 'C#m'):
                    m += 1                   # G -> G#, C -> C#
                M.add('tune', clar_st.play(m - 12, int(100 * dyn)), t + beat * bt, 0.7, 0.1)
                if i >= 5:
                    M.add('tune', picc.play(m + 12, int(85 * dyn)), t + beat * bt, 0.45, 0.2)
                beat += nb
    M.add('bass', bsn.play(n('E2'), 90), fbar[10] - 0.43, 0.8)   # the band stops; one frog left

    # ---- the big frog: two croaks, then huge leaps off the right end on slide whistles ----
    big = next(fr for fr in frogs if fr.last)
    pb = float(pan_at(big.born + 0.9 * big.size))
    for j, c0 in enumerate((T_CROAK + 0.2, T_CROAK + 1.2)):
        M.add('frogs', tbn_buzz.play(n('G1') - 3 * j, 120, dur=0.6 + ON['buzz'] + 0.1 * j), c0 - ON['buzz'], 2.0, pb)
        for r in range(3):                   # the rasp in it: three slow scrapes of a guiro, pitched down
            M.add('frogs', guiro.play(115, pitch=-9 - 3 * j), c0 + 0.04 + 0.16 * r, 1.0, pb)
    for k, (t0, d0, d1, hd) in enumerate(big.hops):
        hop = slide(0.0, hd * 0.5, 500 + 80 * k, 1300 + 150 * k, hd * 0.5, 0.2, 0.6)
        M.add('fx', moving(hop, t0, lambda q, d0=d0, d1=d1, t0=t0: d0 + (d1 - d0) * (q - t0) / hd), t0, 0.5)
        if d1 > L + 40:                      # off the end: up and away, a splash somewhere far off
            M.add('fx', slide(0.0, hd, 1300 + 150 * k, 2600, hd, 0.3, 0.6), t0 + hd * 0.5, 0.6, 0.85)
            M.add('perc', timp.play(60, pitch=4), t0 + hd + 0.35, 0.3, 0.85)
            M.add('frogs', guiro.play(70, pitch=-2), t0 + hd + 0.4, 0.4, 0.85)
            break
        down = slide(0.0, hd * 0.5, 1300 + 150 * k, 500 + 80 * k, hd * 0.5, 0.2, 0.6)
        M.add('fx', moving(down, t0 + hd * 0.5, lambda q, d0=d0, d1=d1, t0=t0: d0 + (d1 - d0) * (q - t0) / hd),
              t0 + hd * 0.5, 0.5)
        tl = after(t0, hd)
        p = float(pan_at(d1))
        M.add('perc', timp.play(100, pitch=-2 + 2 * k), tl, 0.5, p)
        M.add('bass', bsn.play(n(['E2', 'G#2', 'B2', 'E3'][min(k, 3)]), 110), tl, 0.6, p)
        M.add('frogs', guiro.play(100, pitch=-4), tl, 0.7, p)

    # ---- one last bubble rises in the empty pot and pops ----
    tb, tp = T_CROAK + 6.0, T_CROAK + 7.6
    rise = np.arange(int((tp - tb) * SR)) / SR
    ph = 2 * np.pi * np.cumsum(180 * 2 ** (rise / (tp - tb) * 1.5)) / SR
    s = 0.25 * np.sin(ph) * (rise / (tp - tb)) ** 1.5
    M.add('pad', np.vstack([s, s]), tb, 0.8, float(pan_at(centre)))
    M.add('bubbles', bloop(500, 0.18, 2.0, 0.9), tp, 0.6, float(pan_at(centre)))
    M.add('frogs', glock.play(n('B6'), 80), tp, 0.5, float(pan_at(centre)))
    for j, m in enumerate((n('E3'), n('B3'), n('E4'), n('G#4'), n('B4'))):
        M.add('pah', harp.play(m, 85), tp + 0.05 + 0.05 * j, 0.5)
    M.add('bass', bsn.play(n('E2'), 100), tp + 0.05, 0.5)

    M.add('lead', M.synth('Leads/Squelch').render(lead_n, D), 0.0)
    M.add('choir', M.synth('Pads/Ooh').render(choir_n, D), 0.0)
    M.add('pad', M.synth('Pads/Ghost Pad').render(pad_n, D), 0.0)
    # the band follows the brew: a murmur while it simmers, full when it floods the house
    tt = np.arange(M.n) / SR
    env = np.interp(tt, *zip(*LEVEL))
    for k in ('bass', 'pah', 'tune', 'lead', 'choir', 'perc', 'fx', 'brew'):
        M.buses[k]['sig'] *= env
