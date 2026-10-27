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
