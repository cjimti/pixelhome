"""Superhuman Chores: Morning. Two kids wander the roof leaving a trail of mess (speckles of toys,
socks and crumbs in every colour). Mum tidies at a normal pace and loses ground. Then she powers up
and goes superhuman: she zips to wherever the mess is worst, faster and faster, drawn with true
motion blur (each frame integrates her path over 16 sub-steps), so at full speed she is a streak
tidying the whole house in a pass. Laundry appears pegged out along the Side, lunches packed in a row
on the porch. She sits down on the porch with a sigh. A kid drops one single sock on the right wing,
and she is there and back before it lands."""
import numpy as np
from pixelhome.fx import DT, hexc, perc, light, smoothstep, keys, nframes

CODE = 'MO07'
TITLE = 'Superhuman Chores'
KIND = 'show'
DESCRIPTION = 'Kids leave a trail of mess, Mum powers up and tidies the whole house as a motion-blurred streak, pegs out the laundry, packs the lunches, sits down, and one sock drops.'

MUM = hexc('#ff5aa8')
MUM_HOT = hexc('#ffd0f0')
KIDS = [hexc('#ffa050'), hexc('#90ff60')]
TIDY = hexc('#ffd8b8')
LAUNDRY = [hexc(c) for c in ('#ff7aa8', '#ffc0a0', '#b090ff', '#a0ff90', '#ffe0c0')]
LUNCH = [hexc('#ff8a5c'), hexc('#ff5a96'), hexc('#b070ff')]


def render(G, seed=27):
    rng = np.random.default_rng(seed)
    D = 64.0
    n = G.N
    out = np.zeros((nframes(D), n, 3))
    x = G.pd[G.path]
    L = G.length
    side = G.pd[G.seg['Side']]
    pf = G.pd[G.seg['Porch Front']]
    M = 0.5 * (pf.min() + pf.max())
    SOCK = 2250.0

    mess = np.zeros(n)
    mess_col = np.array([hexc(c) for c in ('#ff3a6a', '#ffa020', '#60ff40', '#8050ff', '#ff6a20', '#40d0ff')])[rng.integers(0, 6, n)]
    mess_tw = rng.uniform(0.6, 1.0, n)
    kids = np.array([300.0, 2200.0])
    kv = np.array([95.0, -110.0])
    m = M
    mv = 0.0
    done_glint = np.zeros(n)
    SUB = 16

    def speed(t):
        return keys(t, [(0, 120), (20, 140), (22, 0), (24.5, 0), (26, 500), (34, 2600), (44, 4200), (47, 600), (48.5, 0)])

    for f in range(len(out)):
        t = f * DT
        buf = np.zeros((n, 3))
        # kids wander and make mess (until 44 s)
        if 4 < t < 44:
            kv += rng.normal(0, 60, 2) * DT
            kv = np.sign(kv) * np.clip(np.abs(kv), 60, 150)
            flip = rng.random(2) < 0.006
            kv[flip] *= -1
            kids = kids + kv * DT
            for i in range(2):
                if kids[i] < 10 or kids[i] > L - 10:
                    kv[i] = -kv[i]
                    kids[i] = np.clip(kids[i], 10, L - 10)
                drop = rng.random() < keys(t, [(4, 0.2), (20, 0.5), (40, 0.6)])
                if drop:
                    c = kids[i] + rng.normal(0, 12)
                    mess = np.minimum(1, mess + 0.9 * np.exp(-((x - c) / rng.uniform(4, 12)) ** 2))
        elif t >= 44 and t < 52:
            kids += (np.array([M - 40, M + 40]) - kids) * min(1, DT * 1.5)

        # Mum: chase the worst mess, integrating sub-steps for motion blur
        v = speed(t)
        trail = np.zeros(n)
        if t < 48.5:
            sm = np.convolve(mess, np.ones(15) / 15, 'same')
            for _ in range(SUB):
                if sm.max() > 0.02 and v > 0:
                    target = x[np.argmax(sm * (1 + 0.3 * np.exp(-((x - m) / 300) ** 2)))]
                else:
                    target = M
                step = np.clip(target - m, -v * DT / SUB, v * DT / SUB)
                m += step
                near = np.exp(-((x - m) / 14) ** 2)
                clean = near * (0.25 if v < 300 else 0.6)
                done_glint = np.maximum(done_glint, mess * clean * 1.5)
                mess *= 1 - clean
                trail = np.maximum(trail * 0.97, near)
        else:
            if t < 56.9:
                mess *= 0.9                                     # the last crumbs
            m += (M - m) * min(1, DT * 3)
            trail = np.exp(-((x - m) / 14) ** 2)
        # the dropped sock, at 57 s: there and back within a few frames
        if 56.9 < t < 57.05:
            mess = np.maximum(mess, 1.0 * np.exp(-((x - SOCK) / 6) ** 2))
        if 57.3 <= t < 57.7:
            u = (t - 57.3) / 0.4
            mp = M + (SOCK - M) * np.sin(np.pi * u)
            trail = np.exp(-((x - np.linspace(M, mp, 40)[:, None]) / 14) ** 2).max(0) * np.where(np.abs(x - mp) < 30, 1.2, 0.7)
            if u > 0.45:
                mess *= np.exp(-((x - SOCK) / 30) ** 2) * 0 + (1 - np.exp(-((x - SOCK) / 30) ** 2))

        # house: tidy glow, mess speckle
        tidy = keys(t, [(0, 0), (2, 0.1), (60, 0.1), (64, 0)])
        buf += light(TIDY, tidy * (1 - mess))
        buf += perc(0.5 * mess * mess_tw)[:, None] * mess_col
        buf += light(TIDY, 0.3 * done_glint)
        done_glint *= 0.93
        # laundry on the Side and lunches on the porch, done during the superhuman pass
        lw = smoothstep(30, 44, t) * keys(t, [(60, 1), (64, 0)])
        pos_s = (x - side.min()) / (side.max() - side.min())
        if lw > 0:
            items = np.floor(pos_s * 14)
            onl = (pos_s >= 0) & (pos_s <= 1) & (pos_s * 14 - items > 0.18) & (pos_s * 14 - items < 0.82)
            shown = (items / 14) < lw
            cols = np.array(LAUNDRY)[(items.astype(int) % len(LAUNDRY))]
            buf += perc(0.32 * onl * shown)[:, None] * cols
        lunch = smoothstep(40, 46, t) * keys(t, [(60, 1), (64, 0)])
        for k, c in enumerate(LUNCH):
            cx = M + (k - 1) * 70
            if lunch > k / 3:
                buf += light(c, 0.5 * smoothstep(22, 16, np.abs(x - cx)) * smoothstep(k / 3, k / 3 + 0.2, lunch))

        # kids
        if t > 4:
            kI = keys(t, [(4, 0), (5, 0.55), (60, 0.55), (63, 0)])
            for i in range(2):
                buf += light(KIDS[i], kI * np.exp(-((x - kids[i]) / 7) ** 2))
        # Mum: power-up at 22-25, streak when fast, a sigh when she sits
        hot = smoothstep(300, 3000, v)
        mcol = MUM + (MUM_HOT - MUM) * hot
        mI = keys(t, [(0, 0), (1.5, 0.85), (63, 0.85), (64, 0)])
        if 22 < t < 25:
            u = t - 22
            buf += light(MUM_HOT, 0.8 * np.exp(-((np.abs(x - m) - 120 * u) / 15) ** 2) * np.exp(-u / 1.2))
            mI *= 1 + 0.5 * np.sin(2 * np.pi * u * (1 + u))
        if t > 49:
            mI *= 1 - 0.35 * np.exp(-((t - 50.5) / 1.2) ** 2)                 # the sigh
        buf += light(mcol, mI * np.clip(trail, 0, 1.2))
        out[f][G.path] = buf
    return out
