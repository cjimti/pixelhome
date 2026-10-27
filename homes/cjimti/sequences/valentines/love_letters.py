"""Love Letters: the five corners of the roof are mailboxes. Envelopes (a pale sprite with a wax seal
in the middle, drawn with sub-pixel soft edges) are posted in from the two free ends. They slow for
every corner like a courier on a bike, brake into their mailbox, open (the halves part) and leave a
heart whose point sits in the corner. One courier overshoots and backs up. A last pair of letters,
one from each end, meets on the porch; then every mailbox sends its heart back to the porch at once."""
import numpy as np
from pixelhome.fx import DT, hexc, light, keys, smoothstep, lerp, Flicker, nframes

CODE = 'VD07'
TITLE = 'Love Letters'
KIND = 'show'
DESCRIPTION = ('Envelopes are posted in from both ends of the roof, slow down round the corners and open into '
               'hearts at the five corner mailboxes. Then every corner sends its heart to the porch.')

PAPER = hexc('#ffc0a0')
EDGE = hexc('#ffd8b8')
SEAL = hexc('#ff0010')
GOLD = hexc('#ffa040')
ROSE = hexc('#ff2448')
WINE = hexc('#a00008')
BLUSH = hexc('#ff5a50')
WARM = hexc('#ffc890')

VMAX = 300.0
HALF = 22.0


def courier(start, targets, corners, t0, F):
    """Per-frame position of a letter from `start` through `targets` (path distances), slowing for
    corners and braking into the last target. Returns (positions, arrival frame)."""
    pos = np.full(F, np.nan)
    p, k = float(start), 0
    f = int(round(t0 / DT))
    v = 0.0
    arrive = None
    while f < F:
        pos[f] = p
        if k == len(targets):
            arrive = arrive if arrive is not None else f
            f += 1
            continue
        tgt = targets[k]
        dist = abs(tgt - p)
        dc = np.min(np.abs(corners - p)) if k == len(targets) - 1 and abs(tgt - p) > 30 else np.min(np.abs(corners - p))
        corner_f = 0.4 + 0.6 * smoothstep(0, 90, dc) if dist > 40 else 1.0
        brake = np.sqrt(np.clip(dist / 110, 0, 1))
        want = VMAX * min(corner_f, 1.0) * max(brake, 0.05)
        v += np.clip(want - v, -900 * DT, 500 * DT)
        step = min(v * DT, dist)
        p += np.sign(tgt - p) * step
        if abs(tgt - p) < 0.3:
            p = tgt
            v = 0.0
            k += 1
        f += 1
    if arrive is None:
        arrive = F - 1
    return pos, arrive


def envelope(x, opening):
    """Sprite profile across x (path units from its centre). opening 0..1 parts the two halves."""
    sep = 22 * opening
    xl, xr = np.abs(x + sep / 2), np.abs(x - sep / 2)
    halfw = HALF * (1 - 0.4 * opening)
    body_l = smoothstep(halfw + 2, halfw - 2, xl) * (x < 0)
    body_r = smoothstep(halfw + 2, halfw - 2, xr) * (x >= 0)
    body = (body_l + body_r) * 0.32 * (1 - opening)
    edge = (np.exp(-((xl - halfw) / 2.2) ** 2) * (x < 0) + np.exp(-((xr - halfw) / 2.2) ** 2) * (x >= 0)) * 0.6 * (1 - opening)
    return body, edge


def heart1d(x, s):
    """A small heart with its point at x=0 lying along the path: two lobes and a bright point."""
    lob = np.exp(-((np.abs(x) - 44 * s) / (16 * s)) ** 2)
    return 0.7 * lob + 0.6 * np.exp(-(x / (7 * s)) ** 2)


def render(G, seed=27):
    rng = np.random.default_rng(seed)
    D = 49.0
    F = nframes(D)
    out = np.zeros((F, G.N, 3))
    pdp = G.pd[G.path]
    L = G.length
    segs = G.path_segments()
    corners = np.array([0.5 * (pdp[a[-1]] + pdp[b[0]]) for (_, a), (_, b) in zip(segs[:-1], segs[1:])])
    pf = G.seg['Porch Front']
    c = G.pd[pf[len(pf) // 2]]
    fl = Flicker(rng, G.N, 0.2, 0.8)

    plan = [(2.0, -HALF, [corners[0]], SEAL, 0),
            (6.5, L + HALF, [corners[4]], SEAL, 4),
            (11.0, -HALF, [corners[1] + 55, corners[1]], SEAL, 1),     # overshoots, backs up
            (15.0, L + HALF, [corners[3]], SEAL, 3),
            (19.0, -HALF, [corners[2]], GOLD, 2)]
    letters = []
    for t0, st, tg, col, box in plan:
        pos, arr = courier(st, tg, corners, t0, F)
        letters.append((pos, arr, col, box))
    # the last pair: one from each end, timed to meet on the porch
    pa, aa = courier(-HALF, [c - HALF - 1], corners, 27.0, F)
    probe, ab = courier(L + HALF, [c + HALF + 1], corners, 27.0, F)
    lag = (aa - ab) * DT
    pb, ab = courier(L + HALF, [c + HALF + 1], corners, 27.0 + lag, F)
    t_meet = aa * DT
    t_reply = t_meet + 4.0
    reply_dur = 3.0
    box_t = {}

    for f in range(F):
        t = f * DT
        buf = np.zeros((G.N, 3))
        master = keys(t, [(0, 0), (1, 1), (D - 4, 1), (D - 0.3, 0)])
        buf += light(WINE, 0.04 * (1 + 0.2 * fl(t)))
        # the courier route faintly marked: corners glow as empty mailboxes
        for i, cp in enumerate(corners):
            buf += light(WARM, 0.12 * np.exp(-((pdp - cp) / 6) ** 2))

        for pos, arr, col, box in letters:
            p = pos[f]
            if np.isnan(p):
                continue
            ta = arr * DT
            opening = smoothstep(ta + 0.3, ta + 1.3, t)
            if opening < 1:
                x = pdp - p
                body, edge = envelope(x, opening)
                seal = np.exp(-(x / 3.2) ** 2) * (0.9 - 0.9 * opening)
                buf += light(PAPER, body) + light(EDGE, edge) + light(col, seal)
            if t > ta + 0.6:
                box_t.setdefault(box, ta + 0.6)

        # hearts left in the mailboxes, each breathing at its own pace; they fly to the porch at the end
        for box, tb in box_t.items():
            s = t - tb
            grow = smoothstep(0, 0.8, s)
            beat = 0.85 + 0.15 * np.sin(2 * np.pi * (t - tb) / (2.3 + 0.3 * box))
            pop = 0.6 * np.exp(-s / 0.4)
            if t < t_reply:
                x = pdp - corners[box]
                buf += light(ROSE if box != 2 else GOLD, (0.55 * beat + pop) * grow * heart1d(x, 0.4 + 0.6 * grow))
            elif t < t_reply + reply_dur:
                u = smoothstep(t_reply, t_reply + reply_dur, t)
                hp = lerp(corners[box], c, u)
                x = pdp - hp
                buf += light(ROSE if box != 2 else GOLD, 0.7 * heart1d(x, 1 - 0.3 * u))
                buf += light(BLUSH, 0.25 * np.exp(-np.clip((pdp - hp) * np.sign(corners[box] - c), 0, None) / 120)
                             * (np.abs(pdp - c) <= np.abs(corners[box] - c)) * (np.sign(pdp - hp) == np.sign(corners[box] - c)))

        for pos, col in ((pa, SEAL), (pb, SEAL)):
            p = pos[f]
            if np.isnan(p):
                continue
            opening = smoothstep(t_meet + 0.4, t_meet + 1.6, t)
            if opening < 1:
                x = pdp - p
                body, edge = envelope(x, opening)
                buf += light(PAPER, body) + light(EDGE, edge) + light(col, np.exp(-(x / 3.2) ** 2) * 0.9 * (1 - opening))
        if t > t_meet + 0.8:                                 # the porch heart, and the finale
            s = t - t_meet - 0.8
            x = pdp - c
            grow = smoothstep(0, 1.5, s)
            buf += light(DEEPEN(t, t_reply + reply_dur), 0.8 * grow * heart1d(x, 1.3 + 0.8 * grow) *
                         keys(t, [(t_meet, 1), (t_reply + reply_dur, 1), (t_reply + reply_dur + 0.4, 1.3), (D - 4, 1)]))
            if t > t_reply + reply_dur:
                sb = t - t_reply - reply_dur
                buf += light(WARM, 0.9 * np.exp(-sb / 0.3) * np.exp(-(x / 120) ** 2))
                ring = np.exp(-((np.abs(x) - 500 * sb) / 70) ** 2) * np.exp(-sb / 2.5)
                buf += light(ROSE, 0.7 * ring)
                buf += light(WINE, 0.22 * smoothstep(0, 2, sb) * keys(t, [(D - 6, 1), (D - 1, 0)]))
        out[f][G.path] = buf * master
    return out


def DEEPEN(t, t1):
    return lerp(BLUSH, ROSE, smoothstep(t1 - 2, t1, t))
