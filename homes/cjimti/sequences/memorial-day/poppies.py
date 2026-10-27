"""Poppies: In Flanders fields. Poppies bloom one at a time across the roofline: a dark crimson bud,
then petals that open outward around a dark centre, each with a small overshoot as it unfurls. Seeds
carry to neighbours, so the field spreads outward from the far porch. Once the field is full a slow wind
passes along it and the flowers nod; then the petals let go and drift down the roof on the wind,
leaving one poppy on the porch."""
import numpy as np
from pixelhome.fx import DT, hexc, perc, smoothstep, keys, nframes

CODE = 'MM04'
TITLE = 'Poppies'
KIND = 'show'
DESCRIPTION = ('Poppies bloom one by one across the roof, each opening from a dark bud around a dark centre. '
               'A wind passes through the field, and the petals drift away.')

POPPY = hexc('#e8231a')
CRIMSON = hexc('#7a0608')
EYE = hexc('#2a0a10')
NAVY = hexc('#0b1d4a')
GOLD = hexc('#ffb040')
R = 13.0          # petal radius (layout units)


def render(G, seed=4):
    rng = np.random.default_rng(seed)
    D = 72.0
    out = np.zeros((nframes(D), G.N, 3))
    L = G.length
    pdp = G.pd[G.path]
    # flowers: a jittered layout along the path, never too close, never on a corner
    corners = pdp[[80, 178, 260, 331, 380]]
    c = np.arange(30.0, L - 20, 49.0) + rng.uniform(-12, 12, len(np.arange(30.0, L - 20, 49.0)))
    c = np.array([x for x in c if np.min(np.abs(corners - x)) > 14])
    K = len(c)
    # bloom order: start at the middle of the far porch, then seeds carry to near neighbours
    first = int(np.argmin(np.abs(c - pdp[296])))
    bloomed, order = {first}, [first]
    while len(order) < K:
        rest = np.array([k for k in range(K) if k not in bloomed])
        dist = np.min(np.abs(c[rest][:, None] - c[order][None, :]), axis=1)
        w = np.exp(-dist / 70.0)
        k = int(rng.choice(rest, p=w / w.sum()))
        bloomed.add(k); order.append(k)
    gaps = np.linspace(1.0, 0.12, K - 1) ** 1.5
    gaps *= 31.0 / gaps.sum()                 # slow at first, then the field fills quickly
    tb = np.empty(K)
    tb[order] = 4.0 + np.concatenate([[0], np.cumsum(gaps)])
    size = rng.uniform(0.85, 1.15, K)
    bright = rng.uniform(0.85, 1.0, K)
    sway_ph = rng.uniform(0, 2 * np.pi, K)
    last = first
    # wind after the field is full; petals released one by one as the gust passes
    T_WIND = tb.max() + 4.0
    gust_v = 160.0
    t_release = T_WIND + 7.0 + c / 300.0
    t_release[last] = np.inf
    # two petals per flower, each a particle with drag, carried along the path by the wind
    pet_x0 = np.concatenate([c - R * 0.6, c + R * 0.6])
    pet_t0 = np.concatenate([t_release, t_release + rng.uniform(0.1, 0.5, K)])
    pet_v = rng.uniform(70, 150, 2 * K)
    pet_life = rng.uniform(3.0, 5.0, 2 * K)

    for f in range(len(out)):
        t = f * DT
        I = np.zeros(G.N)               # petal intensity in path order
        eye = np.zeros(G.N)
        bud = np.zeros(G.N)
        floor = keys(t, [(0, 0), (3, 0.08), (D - 5, 0.08), (D - 0.5, 0)])
        gust_front = (t - T_WIND) * gust_v - 500.0
        for k in range(K):
            u = t - tb[k]
            if u < -0.6 or t > t_release[k] + 0.6:
                continue
            # bud swells for 0.6 s, then the petals open over 2 s with a small overshoot
            budI = smoothstep(-0.6, 0.0, u) * (1 - smoothstep(0.2, 1.2, u))
            o = smoothstep(0, 2.0, u)
            o = o + 0.12 * np.sin(np.pi * np.clip((u - 1.2) / 1.4, 0, 1)) * (u > 1.2)
            gust = np.exp(-((c[k] - gust_front) / 260.0) ** 2)
            sway = 4.0 * gust * np.sin(2 * np.pi * 0.8 * t + sway_ph[k])
            nod = 1 - 0.25 * gust * (0.5 + 0.5 * np.sin(2 * np.pi * 0.8 * t + sway_ph[k]))
            let_go = 1 - smoothstep(0, 0.6, t - t_release[k])
            r = R * size[k] * o
            d = np.abs(pdp - c[k] - sway)
            petals = (1 - smoothstep(r - 2.5, r + 1.5, d)) * smoothstep(1.2, 4.0, d)
            I = np.maximum(I, 0.72 * bright[k] * petals * smoothstep(0, 0.8, u) * nod * let_go)
            eye = np.maximum(eye, np.exp(-(d / 2.4) ** 2) * o * let_go)
            bud = np.maximum(bud, budI * np.exp(-(d / 4.0) ** 2))
        # drifting petals
        pt = t - pet_t0
        act = (pt > 0) & (pt < pet_life)
        if act.any():
            p = pt[act]
            x = pet_x0[act] + pet_v[act] * 1.2 * (1 - np.exp(-p / 1.2)) + 8 * np.sin(2.5 * p + pet_x0[act])
            a = 0.55 * smoothstep(0, 0.3, p) * (1 - smoothstep(0.4, 1.0, p / pet_life[act]))
            g = a[None, :] * np.exp(-((pdp[:, None] - x[None, :]) / 4.5) ** 2)
            I = np.maximum(I, g.max(1))
        # the last poppy fades at the very end
        if t > D - 6:
            I *= 1 - smoothstep(D - 6, D - 1, t)
            eye *= 1 - smoothstep(D - 6, D - 1, t)
        col = perc(I)[:, None] * POPPY + perc(0.45 * bud)[:, None] * CRIMSON
        # the dark centre: suppress the petals there and leave a faint near-black plum and a gold stamen
        col = col * (1 - 0.9 * eye[:, None]) + perc(0.25 * eye)[:, None] * EYE + perc(0.12 * eye)[:, None] * GOLD
        col = np.maximum(col, perc(floor) * NAVY)
        out[f][G.path] = col
    return out
