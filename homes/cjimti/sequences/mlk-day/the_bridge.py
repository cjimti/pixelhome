"""The Bridge: The two wing fronts are two shores, one deep blue and one gold, and the set-back porch
(Porch Left, Porch Front, Porch Right) is the water between them. Builders walk out from each shore,
each carrying a plank of light to the tip of their half of the bridge, set it with a small glint and walk
back for the next. The two halves reach toward each other in mirror image, each side at its own pace,
until the last two builders meet over the middle of the Porch Front and set the keystone together.
A ring of light runs out from it to both shores, and then people cross: blue lights walk to the gold
shore and gold lights walk to the blue one, passing through each other on the bridge, while both shores
slowly take on the same warm light."""
import numpy as np
from pixelhome.fx import DT, hexc, perc, light, keys, lerp, smoothstep, Flicker, nframes

CODE = 'MK05'
TITLE = 'The Bridge'
KIND = 'show'
DESCRIPTION = ('Builders carry planks of light out from the two wings and build a bridge across the porch '
               'from both sides. They meet in the middle, and people start crossing in both directions.')

BLUE = hexc('#2848ff')
GOLD = hexc('#ffa030')
WARM = hexc('#ffc890')
PLANK = hexc('#ffd8a8')
NIGHT = hexc('#0c18a0')
WATER = hexc('#0828c0')


def render(G, seed=25):
    rng = np.random.default_rng(seed)
    D = 78.0
    F = nframes(D)
    out = np.zeros((F, G.N, 3))
    pdp = G.pd[G.path]
    pf = G.seg['Porch Front']
    M = 0.5 * (G.pd[pf].min() + G.pd[pf].max())
    bL = G.pd[G.path[179]]                      # left shore ends, bridge begins
    bR = G.pd[G.path[380]]                      # bridge ends, right shore begins
    sL0 = G.pd[G.path[81]]                      # far end of the Left wing
    sR1 = G.pd[G.path[500]]                     # far (free) end of the Right wing
    on_left_shore = (pdp >= sL0 - 1) & (pdp < bL)
    on_right_shore = (pdp > bR) & (pdp <= sR1 + 1)
    on_bridge = (pdp >= bL) & (pdp <= bR)
    on_side = pdp < sL0 - 1
    NP = 22
    V = 150.0
    T_KEY = 40.0
    PICK = 55.0                                  # builders pick planks up this far back on the shore

    sides = []
    for sgn, start, half in ((+1, bL, M - bL), (-1, bR, bR - M)):
        pl = half / NP
        k = np.arange(NP)
        travel = (PICK + k * pl) / V
        arrive = np.linspace(9.0, T_KEY, NP) + np.r_[rng.uniform(-0.35, 0.35, NP - 1), 0]
        arrive = np.maximum.accumulate(arrive)
        depart = arrive - travel
        sides.append(dict(sgn=sgn, start=start, pl=pl, depart=depart, arrive=arrive, travel=travel,
                          q=sgn * (pdp - start)))
    shimmer = Flicker(rng, G.N, 0.15, 0.6)

    # crossers after the keystone
    crossers = []
    for sgn, a, b, col in ((+1, sL0 + 20, sR1 - 10, BLUE), (-1, sR1 - 20, sL0 + 10, GOLD)):
        for t0 in np.sort(rng.uniform(T_KEY + 4, T_KEY + 26, 26)):
            crossers.append((t0, a, b, rng.uniform(95, 125), col))

    for f in range(F):
        t = f * DT
        buf = np.zeros((G.N, 3))
        intro = keys(t, [(0, 0), (4, 1)])
        mix = keys(t, [(T_KEY + 6, 0), (T_KEY + 30, 1)])
        sh = 1 + 0.06 * shimmer(t)[G.path]
        # the shores and the water
        buf[on_left_shore] += light(lerp(BLUE, WARM, mix), 0.34 * intro * sh[on_left_shore])
        buf[on_right_shore] += light(lerp(GOLD, WARM, mix), 0.34 * intro * sh[on_right_shore])
        buf[on_bridge] += light(WATER, 0.07 * intro * sh[on_bridge] * (1 - 0.5 * mix))
        buf[on_side] += light(lerp(NIGHT, WARM, mix * 0.6), lerp(0.07, 0.2, mix) * intro * np.ones(on_side.sum()))

        for S in sides:
            q, pl = S['q'], S['pl']
            col = BLUE if S['sgn'] > 0 else GOLD
            # planks already set: steady warm structure with a glint as each one lands
            for k in np.nonzero(S['arrive'] <= t)[0]:
                age = t - S['arrive'][k]
                inside = smoothstep(k * pl - 1.5, k * pl + 1.5, q) * (1 - smoothstep((k + 1) * pl - 1.5,
                                                                                    (k + 1) * pl + 1.5, q))
                lvl = 0.3 + 0.55 * np.exp(-age / 0.5) + 0.04 * np.sin(2 * np.pi * (t / 5 + k / 7))
                buf += light(PLANK, lvl * smoothstep(0, 0.15, age) * inside)
            # builders on their way out (carrying) and back (empty-handed)
            for k in range(NP):
                d0, a0, tr = S['depart'][k], S['arrive'][k], S['travel'][k]
                if d0 <= t < a0:
                    pos = -PICK + V * (t - d0)
                    head = np.exp(-((q - pos) / 4.5) ** 2)
                    bar = smoothstep(pos - pl - 2, pos - pl + 2, q) * (1 - smoothstep(pos - 2, pos + 1, q))
                    buf += light(col, 0.85 * head) + light(PLANK, 0.32 * bar)
                elif a0 <= t < a0 + tr and t < T_KEY + 0.01:
                    pos = k * pl - V * (t - a0)
                    buf += light(col, 0.45 * np.exp(-((q - pos) / 4.0) ** 2))

        # the keystone and the ring that runs out from it
        if t >= T_KEY - 1.2:
            tk = t - T_KEY
            dist = np.abs(pdp - M)
            buf += light(GOLD, 0.95 * np.exp(-(dist / 10) ** 2) * keys(tk, [(-1.2, 0), (0, 1), (3, 0.55)]))
            if tk > 0:
                ring = np.exp(-((dist - tk * 260) / 40) ** 2) * np.exp(-tk / 4)
                buf += light(WARM, 0.8 * ring)

        # crossing, both ways
        for t0, a, b, sp, col in crossers:
            if t0 <= t:
                s = a + np.sign(b - a) * sp * (t - t0)
                if (b - s) * np.sign(b - a) < -10:
                    continue
                arrive = smoothstep(-40, 0, (s - b) * np.sign(b - a))
                c = lerp(col, WARM, 0.25 + 0.5 * mix)
                buf += light(c, 0.8 * (1 - arrive) * smoothstep(t0, t0 + 0.8, t) *
                             np.exp(-((pdp - s) / 5.0) ** 2))

        buf *= keys(t, [(0, 1), (D - 5, 1), (D, 0)])
        out[f][G.path] = buf
    return out
