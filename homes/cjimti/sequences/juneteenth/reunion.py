"""Reunion: The family comes home for Juneteenth. Grandma is already on the porch, rocking. The aunties
walk in from the back of the house, the uncle shuffles in from the right with his grill smoke trailing
behind him, two kids sprint in, overshoot the porch and race each other back and forth, the teenagers
stop at a corner. Everyone finds a seat on the porch front; hugs ripple out from Grandma. Squeeze in
for the photo: three, two, one, flash. Then the cousin arrives at full speed from the far end, skids
around every corner, and wedges in. Everyone shuffles over. Retake."""
import numpy as np
from pixelhome.fx import DT, hexc, perc, light, smoothstep, keys, lerp, Flicker, nframes

CODE = 'JT04'
TITLE = 'Reunion'
KIND = 'show'
DESCRIPTION = ('The family arrives from both ends of the house and gathers on the porch around Grandma. '
               'Three, two, one, flash, and then the cousin skids in late from the far end. Retake.')

PORCH = hexc('#ff9a3a')
GRANDMA = hexc('#ffc870')
AUNT1 = hexc('#c060ff')
AUNT2 = hexc('#ff5a8a')
UNCLE = hexc('#ff4010')
SMOKE = hexc('#605850')
KID1 = hexc('#20e060')
KID2 = hexc('#ff2020')
TEEN = hexc('#4080ff')
COUSIN = hexc('#ffe020')
WHITE = hexc('#fffaf0')

FLASH1, FLASH2 = 55.0, 66.0


def render(G, seed=4):
    rng = np.random.default_rng(seed)
    D = 76.0
    out = np.zeros((nframes(D), G.N, 3))
    pdp = G.pd[G.path]
    L = G.length
    segs = dict(G.path_segments())
    pf = segs['Porch Front']
    c = pdp[pf].mean()
    pf0, pf1 = pdp[pf].min(), pdp[pf].max()
    corners = [pdp[segs[n].min()] for n in ('Left', 'Porch Left', 'Porch Front', 'Porch Right', 'Right')]
    on_pf = np.zeros(G.N, bool)
    on_pf[pf] = True
    wings = np.zeros(G.N, bool)
    wings[segs['Left']] = True
    wings[segs['Right']] = True
    tw = Flicker(rng, G.N, 0.3, 1.2)

    # name, colour, width, gait Hz, slot offset from Grandma, path keyframes (time, path distance)
    cast = [
        ('aunt1', AUNT1, 8, 1.8, -42, [(5, -20), (22, c - 42)]),
        ('aunt2', AUNT2, 8, 1.8, -84, [(6.2, -20), (23.5, c - 84)]),
        ('uncle', UNCLE, 10, 1.1, 42, [(8, L + 20), (14, 2150), (16, 2130), (19, 2000), (33, c + 42)]),
        ('kid1', KID1, 5, 4.2, 84, [(13, L + 20), (19, pf0 + 10), (21.5, pf1 - 15), (23.5, pf0 + 40),
                                    (26, pf1 - 30), (28, c + 84)]),
        ('kid2', KID2, 5, 4.6, 126, [(13.8, L + 20), (19.6, pf0 + 30), (22, pf1 - 5), (24, pf0 + 20),
                                     (26.6, pf1 - 10), (29, c + 126)]),
        ('teen1', TEEN, 7, 1.4, -126, [(24, -20), (30, corners[0] - 6), (34.5, corners[0] - 6),
                                       (41, c - 126)]),
        ('teen2', TEEN, 7, 1.4, -168, [(24.8, -20), (30.8, corners[0] - 26), (35, corners[0] - 26),
                                       (42, c - 168)]),
    ]
    # the cousin: full speed from the back end, skidding past each corner and snapping back
    ck = [(FLASH1 + 0.3, -20)]
    t_ = FLASH1 + 0.3
    for k, cn in enumerate(corners[:3]):
        t_ += 1.35 if k == 0 else 1.0
        ck += [(t_, cn + 28), (t_ + 0.35, cn + 6)]
        t_ += 0.35
    ck += [(t_ + 0.9, c - 10), (t_ + 1.3, c - 26)]
    COUSIN_AT = t_ + 1.3

    trail = np.zeros(G.N)
    for f in range(len(out)):
        t = f * DT
        buf = np.zeros((G.N, 3))
        # porch light: on the whole time, brighter once people are home
        home = keys(t, [(0, 0), (2, 0.16), (20, 0.18), (42, 0.24), (D - 4, 0.24), (D, 0)])
        buf[on_pf] += light(PORCH, home * (1 + 0.08 * tw(t)[on_pf]))
        # the roads home: a faint warm path so the house reads while it waits
        buf += light(PORCH, keys(t, [(0, 0), (3, 0.09), (D - 4, 0.09), (D, 0)]) * ~on_pf)

        # the photo: squeeze in, then (after the cousin) shuffle over
        sq = keys(t, [(48, 1.0), (51, 0.72), (56, 0.72), (57.5, 1.0), (COUSIN_AT, 1.0), (COUSIN_AT + 1.2, 0.82)])
        shift = keys(t, [(COUSIN_AT - 0.3, 0), (COUSIN_AT + 1.2, 18)])

        # Grandma rocks in the middle
        g = c + 5 * np.sin(2 * np.pi * t / 2.6) * (1 - smoothstep(50, 51, t) * (1 - smoothstep(57, 58, t)))
        gI = keys(t, [(0, 0), (2.5, 0.7), (D - 4, 0.7), (D, 0)])
        buf += light(GRANDMA, gI * np.exp(-((pdp - g) / 13) ** 2))

        moving = np.zeros(G.N)
        hugs = []
        for name, col, w, gait, slot, kf in cast:
            ta = kf[-1][0]
            if t < kf[0][0]:
                continue
            if t < ta:
                s = keys(t, kf)
                bob = 0.8 + 0.2 * np.sin(2 * np.pi * gait * t) ** 2
                if name == 'uncle':
                    moving = np.maximum(moving, np.exp(-((pdp - s) / 10) ** 2))
            else:
                s = c + slot * sq + (shift if slot > 0 else -shift * 0.4 * (slot < 0))
                bob = 0.85 + 0.05 * np.sin(2 * np.pi * 0.4 * t + slot)
                hugs.append(ta)
            if name.startswith('teen') and 30 < t < 35:                 # stopped at the corner...
                bob = 0.6 + 0.3 * (np.sin(2 * np.pi * 0.7 * t) > 0.6)
            buf += light(col, 0.85 * bob * np.exp(-((pdp - s) / (1.3 * w)) ** 2))

        # the uncle's smoke hangs behind him and drifts away slowly
        trail = np.maximum(trail * 0.985, moving * 0.5)
        buf += light(SMOKE, trail)

        # hugs: every arrival sends a warm swell along the porch from Grandma
        for ta in hugs:
            u = t - ta
            if u < 2.5:
                ring = np.exp(-((np.abs(pdp - c) - 120 * u) / 25) ** 2) * np.exp(-u / 0.9)
                buf += light(GRANDMA, 0.5 * ring * on_pf)

        # the cousin
        if ck[0][0] <= t:
            s = keys(t, ck) if t < COUSIN_AT else c - 26 * 0.82 - 18 * 0.4
            wave = 1.0 if t < COUSIN_AT or t > COUSIN_AT + 1.5 else 0.5 + 0.5 * (np.sin(2 * np.pi * 5 * t) > 0)
            buf += light(COUSIN, 0.8 * wave * np.exp(-((pdp - s) / 6) ** 2))
            if t < COUSIN_AT:
                buf += light(COUSIN, 0.35 * np.exp(-((pdp - s + 35) / 25) ** 2) * (pdp < s))

        # countdowns on the wing fronts, then the flash
        for fl, step in ((FLASH1, 1.0), (FLASH2, 0.55)):
            for k in (3, 2, 1):
                u = t - (fl - k * step)
                if 0 <= u < 0.4:
                    buf += light(WHITE, 0.5 * np.exp(-u / 0.12) * wings)
            u = t - fl
            if 0 <= u < 2.5:
                buf = buf * (1 - 0.5 * np.exp(-u / 0.6)) + light(WHITE, 0.95 * np.exp(-u / 0.28))
        # after the retake: everybody glows together
        if t > FLASH2 + 1:
            buf *= 1 + 0.25 * smoothstep(FLASH2 + 1, FLASH2 + 4, t) * (0.5 + 0.5 * np.sin(2 * np.pi * (t - FLASH2) / 3))
        buf *= keys(t, [(D - 4, 1), (D, 0)])
        out[f][G.path] = buf
    return out
