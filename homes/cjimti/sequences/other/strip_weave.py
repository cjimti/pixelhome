"""Strip Weave: The yard is a loom and the roofline lies on a woven cloth. Warp threads run front to
back (one colour per thread, grouped in gold, green and red strips), weft threads run side to side, and
at every crossing a 2/2 twill decides which thread is on top. The runs that go across the house sample
many warp threads, the runs that go back sample many weft threads, so the wings and the porch sides
show two different faces of the same cloth. The cloth advances slowly toward the street as if coming
off the loom at the porch; every thread is drawn with a rounded profile, and at each row edge the
neighbouring row is cross-faded in, so the over/under flips never jump."""
import numpy as np
from pixelhome.fx import DT, hexc, perc, smoothstep, lerp, Flicker, nframes, looped

CODE = 'OT19'
TITLE = 'Strip Weave'
KIND = 'ambient'
DESCRIPTION = ('The yard is a loom: a gold, green and red twill cloth slides slowly toward the street under the '
               'roof, so the wings show the warp, the porch sides show the weft, and the pattern steps along.')

GOLD = hexc('#ffa818')
GREEN = hexc('#0fa03c')
RED = hexc('#d81020')
DEEPGOLD = hexc('#b06008')
FLOOR_COLOR = hexc('#402008')
FLOOR = 0.06
LOOP = 160.0
W = 22.0                                   # thread width, layout units

WARP = [GOLD, GOLD, GREEN, GOLD, RED, GOLD, GOLD, GREEN, GREEN, GOLD, RED, RED, GOLD, GREEN, GOLD, GOLD]
WEFT = [GREEN, GOLD, RED, GOLD, GREEN, GREEN, GOLD, DEEPGOLD, GOLD, RED, GOLD, GREEN, GOLD, RED, RED, GOLD]


def render(G, seed=12):
    rng = np.random.default_rng(seed)

    def draw(D):
        n = G.N
        out = np.zeros((nframes(D), n, 3), np.float32)
        X, Z = G.pos[G.path, 0], G.pos[G.path, 2]
        warp_c = np.array(WARP)
        weft_c = np.array(WEFT)
        # the warp is fixed; the weft moves toward the street by exactly one pattern repeat per loop
        v = len(WEFT) * W / LOOP
        a = (X + 700) / W
        ia = np.floor(a).astype(int)
        ua = a - ia
        prof_a = 1 - (2 * ua - 1) ** 4
        sheen = Flicker(rng, n, 0.03, 0.12)
        warp_lift = rng.uniform(0.9, 1.05, len(WARP))
        for f in range(len(out)):
            t = f * DT
            b = (Z + 900 - v * t) / W
            ib = np.floor(b).astype(int)
            ub = b - ib
            prof_b = 1 - (2 * ub - 1) ** 4
            edge = np.minimum(ub, 1 - ub)

            def cloth(row):
                """Colour (PWM) of the crossing of each pixel's warp thread with weft row `row`."""
                weft_top = ((ia + row) % 4) < 2                  # 2/2 twill
                I_top = np.where(weft_top, prof_b * (0.6 + 0.4 * prof_a), prof_a * (0.6 + 0.4 * prof_b))
                col = np.where(weft_top[:, None], weft_c[row % len(WEFT)],
                               warp_c[ia % len(WARP)] * warp_lift[ia % len(WARP)][:, None])
                return perc(0.38 * I_top * (0.75 + 0.25 * smoothstep(0, 0.2, edge)) * (1 + 0.06 * sheen(t)))[:, None] * col

            # near a row edge, blend in the neighbouring row so over/under flips cross-fade
            nb = ib + np.where(ub > 0.5, 1, -1)
            w = (0.5 * (1 - smoothstep(0, 0.22, edge)))[:, None]
            out[f][G.path] = (1 - w) * cloth(ib) + w * cloth(nb)
        return out
    return looped(draw, LOOP, floor=(FLOOR, FLOOR_COLOR))
