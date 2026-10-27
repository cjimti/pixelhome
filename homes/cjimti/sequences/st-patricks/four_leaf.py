"""Four-Leaf: three clover plants root on the house (porch front, the front-left corner, the right
wing) and send runners along the path; every node unfurls a three-lobed leaf. Then a little gold
glow comes in from the right free end and counts the leaves of each clover, one-two-three, getting
bored and faster as it goes. On the Left wing it counts three, moves on, stops, comes back, counts
again: four. The luck spreads out from that clover along the whole roof and the clovers flower."""
import numpy as np
from pixelhome.fx import DT, hexc, perc, light, keys, lerp, smoothstep, Flicker, nframes

CODE = 'SP03'
TITLE = 'Four-Leaf'
KIND = 'show'
DESCRIPTION = ('Clover creeps along the roof and unfurls. A little glow counts every leaf, one, two, three, '
               'getting bored, until on the left wing it counts four.')

MOSS = hexc('#2c6a00')
EMERALD = hexc('#00c040')
MINT = hexc('#50ffa0')
TIP = hexc('#a0ffb0')
GOLD = hexc('#ffb000')
COUNTER = hexc('#fff0b0')
FLOWER = hexc('#ffe8e0')


def render(G, seed=31):
    rng = np.random.default_rng(seed)
    D = 45.0
    F = nframes(D)
    out = np.zeros((F, G.N, 3))
    n = G.N
    x = G.pd[G.path]
    L = G.length
    C1, C2, C3, C4, C5 = 491.0, 894.0, 1311.0, 1660.0, 2033.0

    seeds = [((C3 + C4) / 2, 2.0), (C1, 4.5), ((C5 + L) / 2, 6.5)]
    V = 75.0
    reach = np.min([ts + np.abs(x - xs) / V * (1 + 0.15 * np.abs(x - xs) / 400) for xs, ts in seeds], axis=0)
    reach_at = lambda p: np.interp(p, x, reach)

    # nodes along the path, avoiding corners; one on the Left wing gets four leaves
    nodes = []
    p = 30.0
    while p < L - 30:
        if min(abs(p - c) for c in (C1, C2, C3, C4, C5)) > 28:
            nodes.append(p)
        p += rng.uniform(70, 95)
    nodes = np.array(nodes)
    lucky = int(np.argmin(np.abs(nodes - (C1 + 0.55 * (C2 - C1)))))
    leaves = np.full(len(nodes), 3)
    leaves[lucky] = 4
    sprout = reach_at(nodes) + rng.uniform(0.6, 1.4, len(nodes))
    sway = Flicker(rng, len(nodes), 0.15, 0.5)
    breathe = Flicker(rng, n, 0.1, 0.4)
    LW, LS = 3.8, 12.0                                  # leaflet width and spacing

    def offsets(k):
        return (np.arange(k) - (k - 1) / 2) * LS

    # counting schedule: right to left, from the right free end to the lucky clover
    order = [j for j in range(len(nodes) - 1, -1, -1) if nodes[j] > nodes[lucky]]
    T0 = 13.0
    cpos = [(T0, L + 40)]
    pops = []                                           # (time, node, leaf)
    t = T0 + 0.6
    for m, j in enumerate(order):
        bored = smoothstep(0, 1, m / 4)
        beat = lerp(0.42, 0.11, bored)
        hop = lerp(0.5, 0.16, bored)
        cpos.append((t, nodes[j] + offsets(3)[-1]))
        for k in range(3):
            pos = nodes[j] + offsets(3)[2 - k]
            cpos.append((t + k * beat, pos))
            pops.append((t + k * beat, j, 2 - k))
        t += 3 * beat + hop
    # the lucky one: counts three fast, moves on, stops, comes back, counts slowly
    j = lucky
    offs4 = offsets(4)
    for k in range(3):
        cpos.append((t + k * 0.13, nodes[j] + offs4[3 - k]))
        pops.append((t + k * 0.13, j, 3 - k))
    t += 0.39
    nxt = nodes[j - 1] + 5
    cpos += [(t + 0.35, nxt), (t + 1.3, nxt), (t + 1.7, nodes[j] + offs4[3] + 2)]
    t += 1.9
    for k in range(4):
        cpos.append((t + k * 0.7, nodes[j] + offs4[3 - k]))
        pops.append((t + k * 0.7, j, 3 - k))
    T_LUCK = t + 2.1 + 0.25
    cpos.append((T_LUCK, nodes[j]))
    popd = {}
    for tp, j, q in pops:
        popd.setdefault((j, q), []).append(tp)

    luck_t = T_LUCK + np.abs(nodes - nodes[lucky]) / 420
    luck_px = T_LUCK + np.abs(x - nodes[lucky]) / 420

    for f in range(F):
        t = f * DT
        fade = keys(t, [(D - 5, 1), (D - 0.5, 0)])
        grown = smoothstep(0, 0.4, t - reach)
        tip = np.exp(-((t - reach) / 0.25) ** 2) * (t > reach - 0.3)
        I_stem = 0.13 * grown * (1 + 0.1 * breathe(t))
        fr = light(MOSS, I_stem * fade) + light(TIP, 0.75 * tip)

        lw = smoothstep(0, 0.8, t - luck_px)
        fr += light(GOLD, 0.12 * lw * fade * (1 + 0.2 * breathe(t)))      # gold creeps into the stems

        sw = sway(t)
        for j in range(len(nodes)):
            u = smoothstep(0, 1.3, t - sprout[j])
            if u <= 0:
                continue
            k = leaves[j]
            if j == lucky:
                k_vis = 3 + smoothstep(0, 1.3, t - sprout[j] - 0.6)    # the fourth lags a little
            offs = offsets(k) * (0.35 + 0.65 * u)
            g = smoothstep(0, 1.2, t - luck_t[j])
            for q in range(k):
                c = nodes[j] + offs[q] + 1.2 * sw[j]
                I = 0.62 * u * (1.0 if q in (0, k - 1) else 1.12)
                if j == lucky and q == 0:
                    I *= min(1, k_vis - 3) if t < sprout[j] + 2.5 else 1
                col = lerp(EMERALD if q % 2 == 0 else MINT, GOLD, g)
                for tp in popd.get((j, q), ()):
                    if t >= tp:
                        I += 0.8 * np.exp(-(t - tp) / 0.3)
                if j == lucky and t > T_LUCK:
                    I += 0.6 * np.exp(-(t - T_LUCK) / 1.2) + 0.15 * (0.5 + 0.5 * np.sin(2 * np.pi * 0.7 * t))
                fr += light(col, I * fade * np.exp(-((x - c) / LW) ** 2))
            # flowers: a white pom-pom opens just beyond each clover after the luck
            fl = smoothstep(0.8, 2.6, t - luck_t[j])
            if fl > 0 and j % 2 == 0:
                c = nodes[j] + (k + 1) / 2 * LS + 6
                fr += light(FLOWER, 0.55 * fl * fade * np.exp(-((x - c) / 3.5) ** 2))

        # the counter
        if T0 <= t <= T_LUCK + 1.0:
            cp = float(keys(t, cpos))
            ci = keys(t, [(T0, 0), (T0 + 0.6, 0.5), (T_LUCK, 0.5), (T_LUCK + 1.0, 0)])
            fr += light(COUNTER, ci * np.exp(-((x - cp) / 7) ** 2))
        if t > T_LUCK:                                   # the burst of luck from the four-leaf
            tb = t - T_LUCK
            for k, a in enumerate((0.9, 0.45, 0.25)):     # the luck rings out three times
                tk = tb - 2.2 * k
                if tk > 0:
                    ring = np.exp(-((np.abs(x - nodes[lucky]) - 420 * tk) / 40) ** 2) * np.exp(-tk / 2.5)
                    fr += light(GOLD, a * ring * fade)
        out[f][G.path] = fr
    return out
