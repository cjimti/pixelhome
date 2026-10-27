"""Sleigh Ride: Santa's team flies a 3-D spline around and over the house: a lead reindeer with a red lamp,
four pairs of reindeer and the sleigh follow the same track at fixed arc-length offsets, shedding a
glitter trail that falls under gravity. The team lands on the porch roof (hoofbeats), Santa goes down
the chimney and presents appear on the wings, then the team gallops off, banks along the street side
and climbs away into the night."""
import numpy as np
from pixelhome.fx import DT, hexc, light, keys, lerp, nframes

CODE = 'XM01'
TITLE = 'Sleigh Ride'
KIND = 'show'
DESCRIPTION = ('A red lamp leads Santa\'s team on a flight around and over the house, lands on the porch roof '
               'with a clatter of hooves, leaves presents on both wings and takes off over the street.')

NIGHT = hexc('#0a1440')
STAR = hexc('#c8d8ff')
NOSE = hexc('#ff1000')
DEER = hexc('#ffa050')
SLEIGH = hexc('#ff2008')
GOLD = hexc('#ffb030')
GLINT = hexc('#fff0c0')
HOOF = hexc('#fff4e0')
GIFTS = [hexc(c) for c in ('#ff1a10', '#10c040', '#ffb020', '#3050ff', '#ff3070', '#f0f0ff')]


def open_spline(pts, per=80):
    """Open Catmull-Rom through pts (K,3) -> dense polyline (M,3) and its cumulative arc length."""
    P = np.vstack([pts[:1], pts, pts[-1:]])
    f = np.linspace(0, 1, per, endpoint=False)[:, None]
    seg = []
    for i in range(1, len(P) - 2):
        p0, p1, p2, p3 = P[i - 1], P[i], P[i + 1], P[i + 2]
        seg.append(0.5 * (2 * p1 + (-p0 + p2) * f + (2 * p0 - 5 * p1 + 4 * p2 - p3) * f ** 2 +
                          (-p0 + 3 * p1 - 3 * p2 + p3) * f ** 3))
    seg.append(P[-2:-1])
    line = np.vstack(seg)
    s = np.concatenate([[0], np.cumsum(np.linalg.norm(np.diff(line, axis=0), axis=1))])
    return line, s


def at(line, s, q):
    q = np.clip(q, 0, s[-1])
    return np.stack([np.interp(q, s, line[:, c]) for c in range(3)], -1)


def render(G, seed=21):
    rng = np.random.default_rng(seed)
    D = 72.0
    F = nframes(D)
    out = np.zeros((F, G.N, 3))
    P = G.pos
    W = np.array([1.0, 1.6, 1.0])          # height counts more: things above the roof read dimmer

    approach = np.array([(-1000, 480, -1000), (-700, 280, -760), (-598, 190, -520), (-598, 175, -260),
                         (-540, 168, -146), (-300, 165, -147), (-150, 170, -160), (160, 175, -188),
                         (400, 168, -191), (640, 180, -191), (800, 230, -260), (720, 250, -330),
                         (460, 215, -200), (230, 190, -195), (152, 172, -330), (152, 158, -520),
                         (110, 151, -569), (0, 150, -569), (-120, 150, -569), (-140, 150, -569)], float)
    depart = np.array([(-140, 150, -569), (-196, 152, -569), (-196, 165, -450), (-196, 175, -240),
                       (-280, 178, -147), (-480, 178, -147), (-596, 190, -260), (-596, 220, -500),
                       (-620, 300, -700), (-800, 600, -1100), (-1100, 1000, -1500)], float)
    L1, S1 = open_spline(approach)
    L2, _ = open_spline(depart)
    line = np.vstack([L1, L2[1:]])
    S = np.concatenate([[0], np.cumsum(np.linalg.norm(np.diff(line, axis=0), axis=1))])
    team = [(0, 'nose')] + [(o, 'deer') for o in (38, 70, 102, 134)] + [(196, 'sleigh')]
    REAR = 196 + 40

    # leader arc length: integrate eased speed profiles, scaled to land exactly at the stop
    tt = np.arange(F) * DT
    stop = S1[-1]
    v1 = np.array([keys(t, [(2, 0), (5, 1), (27, 1), (30, 0.45), (34.5, 0)]) for t in tt])
    v2 = np.array([keys(t, [(47, 0), (50, 0.5), (54, 1), (66, 1.25)]) for t in tt])
    s1, s2 = np.cumsum(v1) * DT, np.cumsum(v2) * DT
    s1 *= stop / s1[-1]
    s2 *= (S[-1] + REAR - stop) / s2[np.searchsorted(tt, 67.5)]
    lead_s = s1 + s2

    def pose(q):
        a, b = at(line, S, np.array([q - 3, q, q + 3]))[[0, 1, 2]], None
        tang = a[2] - a[0]
        tang /= np.linalg.norm(tang) + 1e-9
        return a[1], np.array([-tang[2], 0, tang[0]])

    stars = rng.choice(G.N, 40, replace=False)
    sph = rng.uniform(0, 2 * np.pi, 40)
    sfr = rng.uniform(0.1, 0.4, 40)
    gift_seg = np.concatenate([G.seg['Left'], G.seg['Right']])
    gx = P[gift_seg, 0]
    boxes = []
    for lo, hi in ((-590, -200), (158, 625)):
        x = lo + rng.uniform(8, 20)
        while x < hi - 20:
            w = rng.uniform(26, 48)
            boxes.append((x, x + w, len(boxes) % len(GIFTS), rng.uniform(37, 40.5)))
            x += w + rng.uniform(14, 28)
    order = rng.permutation(len(boxes))
    boxes = [(a, b, c, 37.0 + 3.4 * k / len(boxes)) for k, (a, b, c, _) in zip(order, boxes)]

    pv = np.zeros((400, 3))
    pp = np.zeros((400, 3))
    page = np.full(400, 99.0)
    plife = np.ones(400)
    ptw = rng.uniform(4, 9, 400)
    nxt = 0
    hoof = np.zeros(G.N)
    prev_sleigh = None

    for f in range(F):
        t = f * DT
        fr = out[f]
        sky = keys(t, [(0, 0), (2, 0.09), (66, 0.09), (71.5, 0)])
        fr += light(NIGHT, np.full(G.N, sky))
        tw = np.clip(np.sin(2 * np.pi * sfr * t + sph), 0, 1) ** 3
        fr[stars] += light(STAR, 0.22 * tw * sky / 0.09)

        lead = lead_s[f]
        parked = 34.5 <= t < 47
        sleigh_pos = None
        for off, kind in team:
            q = lead - off
            if q < 0 or q > S[-1]:
                continue
            c, perp = pose(q)
            hf = np.exp(-((c[1] - 150) / 110) ** 2)     # high above the roof reads faint
            d = np.linalg.norm((P - c)[:, [0, 2]], axis=1)
            if kind == 'nose':
                pulse = 1 + 0.25 * np.sin(2 * np.pi * 1.3 * t)
                fr += light(NOSE, 0.95 * hf * pulse * np.exp(-(d / 16) ** 2))
                fr += light(NOSE, 0.25 * hf * np.exp(-(d / 50) ** 2))
            elif kind == 'deer':
                for side in (-1, 1):                  # each pair runs side by side
                    dd = np.linalg.norm((P - c - side * 9 * perp)[:, [0, 2]], axis=1)
                    fr += light(DEER, 0.6 * hf * np.exp(-(dd / 13) ** 2))
            else:
                santa = 1.0
                if parked:
                    santa = keys(t, [(35.5, 1), (36.5, 0.25), (43.0, 0.25), (43.3, 1.2), (43.6, 0.5), (43.9, 1.2),
                                     (44.2, 0.5), (44.5, 1.2), (45, 1)])
                fr += light(SLEIGH, 0.85 * hf * santa * np.exp(-(d / 26) ** 2))
                fr += light(GOLD, 0.35 * hf * np.exp(-((d - 30) / 8) ** 2))
                sleigh_pos = c

        # glitter shed by the sleigh: launched slightly up and back, falls with drag
        if sleigh_pos is not None and prev_sleigh is not None and not parked and 3 < t < 68:
            vel = (sleigh_pos - prev_sleigh) / DT
            for _ in range(3 if np.linalg.norm(vel) > 20 else 0):
                k = nxt % 400
                nxt += 1
                pp[k] = sleigh_pos + rng.normal(0, 6, 3)
                pv[k] = 0.25 * vel + rng.normal(0, 25, 3) + np.array([0, 20, 0])
                page[k] = 0
                plife[k] = rng.uniform(2.0, 4.0)
        prev_sleigh = sleigh_pos
        live = page < plife
        if live.any():
            pv[live] *= np.exp(-1.6 * DT)
            pv[live, 1] -= 60 * DT
            pp[live] += pv[live] * DT
            page[live] += DT
            idx = np.nonzero(live)[0]
            dd = np.linalg.norm((P[None] - pp[idx, None]) * W, axis=2)
            amp = (1 - page[idx] / plife[idx]) * (0.6 + 0.4 * np.sin(ptw[idx] * page[idx] * 6.28))
            g = (amp[:, None] * np.exp(-(dd / 9) ** 2)).max(0)
            fr += light(GLINT, 0.8 * g) + light(GOLD, 0.3 * g)
        page[~live] = 99

        # hoofbeats on the porch roof: gallop on landing and take-off, idle stamps while parked
        hoof *= np.exp(-DT / 0.09)
        rolling = (30.5 < t < 34.5) or (46.5 < t < 50.5)
        for j, (off, kind) in enumerate(team[1:5]):
            q = lead - off
            if q < 0:
                continue
            cx, perp = pose(q)
            if abs(cx[1] - 150) > 4:                  # only hooves on the roof make a sound
                continue
            beat = False
            if rolling:
                ph = (t * 3.2 + j * 0.27) % 1
                beat = any(abs(ph - b) < DT * 1.6 for b in (0.0, 0.12, 0.24))
            elif parked and rng.random() < 0.012:
                beat = True
            if beat:
                for side in (-1, 1):
                    dd = np.linalg.norm(P - cx - side * 9 * perp, axis=1)
                    hoof = np.maximum(hoof, np.exp(-(dd / 7) ** 2))
        fr += light(HOOF, 0.9 * hoof)

        # presents left under the eaves while Santa is inside
        if t > 37:
            I = np.zeros(len(gift_seg))
            col = np.zeros((len(gift_seg), 3))
            for a, b, c, t0 in boxes:
                m = (gx > a) & (gx < b)
                u = (gx[m] - a) / (b - a)
                ribbon = np.exp(-((u - 0.5) / 0.07) ** 2)
                e = keys(t, [(t0, 0), (t0 + 0.5, 1), (68, 1), (71.5, 0)])
                I[m] = e * (0.32 + 0.3 * ribbon)
                col[m] = lerp(GIFTS[c], GOLD, ribbon[:, None])
            fr[gift_seg] += (np.clip(I, 0, None) ** 2.2)[:, None] * col
    return out
