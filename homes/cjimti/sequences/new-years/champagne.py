"""Champagne: The Right wing is a bottle and its free end is the cork. Someone shakes it (the
champagne sloshes as a real wave along the wing, bubbles crowd toward the neck), the cork creeps,
gives a false 'pft', then pops off the end of the house. Foam gushes back over the whole roof
around every corner, fizzes down to a glassful of rising bubbles, and a long beat later the cork
lands on the far back of the house and bounces to a stop."""
import numpy as np
from pixelhome.fx import DT, hexc, perc, light, keys, smoothstep, Flicker, nframes

CODE = 'NY04'
TITLE = 'Champagne'
KIND = 'show'
DESCRIPTION = 'The Right wing is the bottle, its free end the cork. Shaken, a false start, POP. Foam floods back around every corner, and much later the cork lands on the back of the house.'

CHAMP = hexc('#ffc860')
PALE = hexc('#fff0c8')
FOAM = hexc('#fff8ec')
GLASS = hexc('#103818')
FOIL = hexc('#d09020')
CORK = hexc('#ffb070')
NAVY = hexc('#081440')

T_SHAKE, T_PFT, T_POP, T_LAND = 4.0, 15.0, 22.5, 44.0


def render(G, seed=24):
    rng = np.random.default_rng(seed)
    D = 54.0
    out = np.zeros((nframes(D), G.N, 3))
    n = G.N
    pdp = G.pd[G.path]
    L = G.length
    b0 = pdp[381]                           # start of the Right wing: bottom of the bottle
    in_bottle = pdp >= b0
    xb = np.clip((pdp - b0) / (L - b0), 0, 1)       # 0 at the base, 1 at the mouth
    neck = smoothstep(0.82, 0.9, xb)
    mouth = L
    shimmer = Flicker(rng, n, 0.3, 1.2)
    fizz = Flicker(rng, n, 3.0, 9.0)

    # sloshing: damped wave equation on the bottle, driven by the shake
    idx = np.where(in_bottle)[0]
    m = len(idx)
    u = np.zeros(m)
    v = np.zeros(m)
    dx = (L - b0) / (m - 1)
    c, gamma, sub = 220.0, 1.2, 4
    h = DT / sub
    xs = np.linspace(-1, 1, m)

    bubbles = np.zeros((0, 3))              # path position, speed, birth time
    foam_bub = np.zeros((0, 3))

    def cork_pos(t):
        """Cork offset beyond the mouth (layout units). Positive = out."""
        if t < T_SHAKE:
            return 0.0
        if t < T_PFT:
            return 1.5 * np.sin(2 * np.pi * 7 * t) * smoothstep(T_SHAKE, T_PFT, t) ** 2
        if t < T_PFT + 1.2:                  # creeps out, slips back: pft
            return keys(t, [(T_PFT, 0), (T_PFT + 0.6, 9), (T_PFT + 0.75, 2), (T_PFT + 1.2, 0)])
        if t < T_POP:
            return keys(t, [(T_PFT + 3.0, 0), (T_POP - 0.4, 14)]) + 0.8 * np.sin(2 * np.pi * 11 * t) * (t > T_POP - 3)
        return 14 + 2400 * (t - T_POP)      # gone

    for f in range(len(out)):
        t = f * DT
        buf = np.zeros((n, 3))
        buf += light(NAVY, keys(t, [(0, 0), (2, 0.1), (D - 4, 0.1), (D, 0)]))

        # pressure: rises with the shake, sags a little after the false start, spikes before the pop
        pressure = keys(t, [(T_SHAKE, 0), (T_PFT - 1, 0.8), (T_PFT + 0.6, 0.85), (T_PFT + 1.5, 0.6),
                            (T_POP - 0.1, 1.0), (T_POP + 0.5, 0.2), (T_POP + 6, 0)])
        shake = keys(t, [(T_SHAKE, 0), (T_SHAKE + 2, 1), (T_PFT - 1.5, 1), (T_PFT - 0.5, 0), (T_PFT + 2.5, 0),
                         (T_PFT + 3.5, 0.7), (T_POP - 1.5, 0.7), (T_POP - 0.5, 0)])
        for _ in range(sub):
            lap = np.zeros(m)
            lap[1:-1] = u[2:] - 2 * u[1:-1] + u[:-2]
            lap[0], lap[-1] = u[1] - u[0], u[-2] - u[-1]
            force = shake * 900 * np.sin(2 * np.pi * 2.3 * t) * xs + shake * 500 * np.sin(2 * np.pi * 3.7 * t + 1) * xs ** 2
            v += h * (c * c * lap / (dx * dx) - gamma * v + force)
            u += h * v
        slosh = np.tanh(u / 2.5)

        # the liquid: fills the bottle until the pop, then drains from the mouth end inward
        level = keys(t, [(0, 0), (2.5, 1), (T_POP, 1), (T_POP + 8, 0.35), (D - 6, 0.25), (D, 0)])
        fill = np.zeros(n)
        fill[idx] = smoothstep(level + 0.03, level - 0.03, xb[idx]) if t > T_POP else smoothstep(0, 2.5, t)
        liq = 0.34 * fill * (1 + 0.6 * slosh_full(n, idx, slosh)) * (1 - 0.6 * neck) * (0.92 + 0.08 * shimmer(t))
        liq += 0.25 * pressure * fill * xb
        buf += light(CHAMP, liq)
        # glass and foil: a dark green body sheen and gold foil at the neck
        buf += light(GLASS, keys(t, [(0, 0), (2, 0.25), (D - 4, 0.25), (D, 0)]) * in_bottle * (1 - fill))
        buf += light(FOIL, keys(t, [(0, 0), (2, 0.5), (T_POP, 0.5), (T_POP + 0.5, 0.25), (D - 4, 0.25), (D, 0)]) * neck)

        # bubbles in the bottle race toward the neck as pressure rises
        if T_SHAKE < t < T_POP + 6:
            k = rng.poisson(pressure * 9 * DT * (1 + 2 * shake))
            if k:
                nb = np.stack([b0 + rng.uniform(0, 0.8, k) * (L - b0), rng.uniform(40, 140, k) * (0.5 + pressure),
                               np.full(k, t)], 1)
                bubbles = np.vstack([bubbles, nb])
        if len(bubbles):
            bubbles[:, 0] += bubbles[:, 1] * DT
            bubbles = bubbles[bubbles[:, 0] < L - 8]
            g = np.exp(-((pdp[:, None] - bubbles[None, :, 0]) / 2.5) ** 2).sum(1)
            buf += light(PALE, 0.55 * np.clip(g, 0, 1) * in_bottle)

        # the cork: a warm point at the very end, nudging out
        cp = cork_pos(t)
        if cp < 200:
            cpos = mouth + cp
            cork = np.exp(-((pdp - (cpos - 3)) / 4) ** 2)
            buf += light(CORK, keys(t, [(0, 0), (2, 0.8), (T_POP, 0.8)]) * cork)
        # pft: a tiny puff at the mouth
        if T_PFT + 0.55 < t < T_PFT + 1.5:
            tp = t - (T_PFT + 0.55)
            buf += light(FOAM, 0.6 * np.exp(-tp / 0.2) * np.exp(-((L - pdp) / 10) ** 2))

        # POP: flash at the mouth, a spray of droplets off the end
        if t >= T_POP:
            tp = t - T_POP
            buf += light(FOAM, 1.2 * np.exp(-tp / 0.12) * np.exp(-((L - pdp) / (40 + 300 * tp)) ** 2))
            # the foam: a front that floods back along the path, slowing as it goes, around every corner
            reach = (L - 10) * (1 - np.exp(-tp / 4.5)) * 1.02
            dist = L - pdp                                  # distance from the mouth along the roof
            behind = reach - dist
            front = np.exp(-(behind / 25) ** 2) * (behind > -60)
            body = smoothstep(-20, 30, behind)
            settle = keys(tp, [(0, 1), (4, 1), (12, 0.45), (20, 0.3), (D - T_POP - 3, 0)])
            foam = body * settle * (0.45 + 0.25 * np.exp(-behind / 300)) * (0.85 + 0.15 * fizz(t))
            buf += light(FOAM, 0.9 * front * settle)
            fcol = FOAM + (CHAMP - FOAM) * smoothstep(3, 14, tp)
            buf += light(fcol, foam * (1 - fill))
            # bubbles popping in the foam
            k = rng.poisson(60 * settle * DT * 10)
            if k:
                pos = L - rng.uniform(0, reach, k)
                foam_bub = np.vstack([foam_bub, np.stack([pos, rng.uniform(-30, -6, k), np.full(k, t)], 1)])
            if len(foam_bub):
                foam_bub[:, 0] += foam_bub[:, 1] * DT
                age = t - foam_bub[:, 2]
                foam_bub = foam_bub[age < 0.6]
                age = t - foam_bub[:, 2]
                g = (np.exp(-((pdp[:, None] - foam_bub[None, :, 0]) / 2.0) ** 2) *
                     (np.sin(np.pi * age / 0.6) ** 2)[None, :]).sum(1)
                buf += light(FOAM, 0.7 * np.clip(g, 0, 1) * body)

        # the cork lands on the back of the house and bounces to a stop
        if t >= T_LAND:
            tl = t - T_LAND
            # rolling distance along Side from the free back end, with bounces
            roll = 320 * (1 - np.exp(-tl / 1.6))
            hop = 0.0
            tks = [0.5 * (1 - 0.55 ** k2) / 0.45 for k2 in range(8)]
            for k2 in range(7):
                if tks[k2] <= tl < tks[k2 + 1]:
                    hop = 0.6 ** k2 * np.sin(np.pi * (tl - tks[k2]) / (tks[k2 + 1] - tks[k2]))
            bright = 1.0 - 0.6 * hop
            fade = keys(tl, [(0, 1), (D - T_LAND - 3, 1), (D - T_LAND, 0)])
            buf += light(CORK, fade * bright * np.exp(-((pdp - roll) / (6 + 6 * hop)) ** 2))
            # a little splash of light where it lands each time
            land = 0.0
            for k2 in range(6):
                tk = 0.5 * (1 - 0.55 ** k2) / 0.45         # bounce times shrinking geometrically
                if tl >= tk:
                    land = land + 0.8 * 0.6 ** k2 * np.exp(-(tl - tk) / 0.15) * np.exp(-((pdp - 320 * (1 - np.exp(-tk / 1.6))) / 25) ** 2)
            buf += light(PALE, land)
        out[f][G.path] = buf
    return out


def slosh_full(n, idx, s):
    full = np.zeros(n)
    full[idx] = s
    return full
