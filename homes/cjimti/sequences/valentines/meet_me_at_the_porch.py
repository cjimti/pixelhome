"""Meet Me at the Porch: two lights enter from the two free ends of the roofline and look for each other.
Each leaves a fading trail. They nearly meet at the Left/Porch Left corner but both turn away at the same
moment; then she finds his fresh trail, it sparks along to him, he turns, and they meet on the porch.
Their whole journey lights up, the porch beats twice, and they walk off together out the right end."""
import numpy as np
from pixelhome.fx import DT, hexc, light, keys, smoothstep, lerp, heartbeat, Flicker, nframes

CODE = 'VD01'
TITLE = 'Meet Me at the Porch'
KIND = 'show'
DESCRIPTION = ('Two lights enter from opposite ends of the roof and search for each other, leaving trails. '
               'A near miss at a corner, a spark along his trail, and they meet on the porch.')

ROSE = hexc('#ff2448')
GOLD = hexc('#ffa040')
WARM = hexc('#ffc890')
DEEP = hexc('#ff0010')
BLUSH = hexc('#ff5a50')


def render(G, seed=21):
    rng = np.random.default_rng(seed)
    D = 68.0
    out = np.zeros((nframes(D), G.N, 3))
    pdp = G.pd[G.path]
    L = G.length
    pf = G.seg['Porch Front']
    c = G.pd[pf[len(pf) // 2]]                      # porch centre, path distance
    fl = Flicker(rng, G.N, 0.3, 1.2)

    # she (rose) from the back of Side; he (gold) from the right free end
    A = [(1.5, -30), (4, 40), (8, 290), (10.5, 468), (12.5, 488), (14, 466), (15.5, 500), (20.5, 760),
         (22.5, 768), (25.5, 872), (29.2, 876), (30.6, 800), (32.5, 806), (34.3, 900), (37.5, 1160),
         (40.2, 1330), (44.5, c - 7), (55, c - 7)]
    B = [(2.5, L + 30), (5, L - 40), (9, 2200), (11, 2034), (13, 2040), (14, 2085), (17.5, 1700),
         (19.2, 1662), (22, 1360), (23.8, 1312), (27.2, 922), (29.2, 918), (30.7, 1010), (33.3, 1310),
         (35.2, 1395), (36.6, 1392), (37.6, 1430), (44.5, c + 7), (55, c + 7)]
    tA, tB = np.zeros(G.N), np.zeros(G.N)
    decay = np.exp(-DT / 5.0)
    spark_t0, spark_from, spark_to = 34.4, 905.0, 1395.0

    def blob(p, sig=9.0):
        return np.exp(-((pdp - p) / sig) ** 2)

    for f in range(len(out)):
        t = f * DT
        buf = np.zeros((G.N, 3))
        floor = keys(t, [(0, 0), (3, 0.035), (60, 0.035), (66, 0)])
        buf += light(DEEP, floor * (1 + 0.2 * fl(t)))

        pa, pb = keys(t, A), keys(t, B)
        if t > 55:                                   # walking off together, out the right end
            w = keys(t, [(55, 0), (66.5, 1)])
            pa = lerp(c - 7, L + 40, w)
            pb = pa + 14
        # "looking around" shimmer when standing still
        va = abs(keys(t + DT, A) - keys(t, A)) / DT
        look_a = 0.12 * (va < 8) * np.sin(2 * np.pi * 1.7 * t) ** 2
        vb = abs(keys(t + DT, B) - keys(t, B)) / DT
        look_b = 0.12 * (vb < 8) * np.sin(2 * np.pi * 1.5 * t + 1) ** 2
        ia = keys(t, [(1.5, 0), (3.5, 0.85), (44, 0.85), (46, 1.0)])
        ib = keys(t, [(2.5, 0), (4.5, 0.8), (33.5, 0.8), (35.6, 0.55), (36.4, 0.55), (36.6, 1.1), (37.6, 0.85),
                      (44, 0.85), (46, 1.0)])
        ga, gb = blob(pa), blob(pb)
        tA = np.maximum(tA * decay, 0.36 * ga * (t < 45))
        tB = np.maximum(tB * decay, 0.36 * gb * (t < 45))

        # she touches his trail: the trail flares and a spark runs along it to him
        if t > spark_t0:
            s = t - spark_t0
            head = lerp(spark_from, spark_to, smoothstep(0, 2.0, s))
            lag = head - pdp
            behind = np.exp(-np.clip(lag, 0, None) / 120) * (pdp > spark_from - 10) * (lag > 0)
            flare = np.clip(tB / 0.1, 0, 1) * behind * np.exp(-s / 2.5)
            buf += light(WARM, 0.6 * flare)
            if s < 2.0:
                buf += light(WARM, 1.0 * blob(head, 8)) + light(GOLD, 0.4 * blob(head, 40))

        # after they meet: the whole journey relights from the porch outward
        if t > 45:
            s = t - 45
            front = s * 260
            dist = np.abs(pdp - c)
            reach = smoothstep(front, front - 60, dist)
            fade = keys(t, [(45, 1), (52, 1), (57, 0.35), (64, 0)])
            col = np.where((pdp < c)[:, None], ROSE, GOLD)
            col = lerp(col, BLUSH, 0.35 * smoothstep(300, 0, dist)[:, None])
            buf += \
                perc_mix(col, 0.38 * reach * fade * (0.85 + 0.15 * fl(t)))
            buf += light(WARM, 0.8 * np.exp(-((dist - front) / 25) ** 2) * (front < 1100))
            hb = heartbeat(t, 48.0, 1.1) * (t < 51.2)
            buf += light(DEEP, 1.0 * hb * np.exp(-(dist / 260) ** 2))
            buf += light(BLUSH, 0.6 * hb * np.exp(-(dist / 90) ** 2))

        trail_col = (tA[:, None] * ROSE * 1.0 + tB[:, None] * GOLD) / np.maximum(tA + tB, 1e-6)[:, None]
        buf += perc_mix(trail_col, np.maximum(tA, tB) * (t < 60))
        buf += light(ROSE, (ia + look_a) * ga) + light(ROSE, 0.22 * ia * blob(pa, 30))
        buf += light(GOLD, (ib + look_b) * gb) + light(GOLD, 0.22 * ib * blob(pb, 30))
        out[f][G.path] = buf
    return out


def perc_mix(col, intensity):
    return np.clip(intensity, 0, None)[:, None] ** 2.2 * col
