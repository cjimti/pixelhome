"""Hatching: The whole roofline is one speckled eggshell. Something inside knocks: warm thumps on
the porch, and the egg rocks side to side. Then it pecks: each peck starts a crack that runs off in
both directions in jerky starts and stalls, light leaking through more and more of it, around the
corners, until the cracks meet. The shell bursts and falls away in pieces, and a fluffy chick is
left: the porch front is its head (two eyes, a beak that peeps), the wings are its wings, and the
Side is the half shell it sits in."""
import numpy as np
from pixelhome.fx import DT, hexc, light, keys, smoothstep, smooth_noise, Flicker, nframes

CODE = 'EA03'
TITLE = 'Hatching'
KIND = 'show'
DESCRIPTION = 'The roofline is one speckled eggshell. Knocks, rocking, then cracks that creep around the corners with light leaking through, until a chick bursts out and peeps.'


def lin(h):
    return hexc(h) ** 2.2


SHELL = lin('#fff0d8')
SPECK = lin('#c9a2ff')
SPECK2 = lin('#ffb08a')
GLOW = lin('#ffc65a')
HOT = lin('#fff6d0')
FLUFF = lin('#ffe25a')
FLUFF_TIP = lin('#fff3b0')
BEAK = lin('#ff8a2a')

TAPS = [(11.0, 1485), (14.5, 1395), (17.0, 690), (19.5, 2230), (22.0, 1880), (24.5, 260), (26.5, 1080),
        (28.5, 2440), (30.0, 470)]
BREAK = 39.0


def render(G, seed=23):
    rng = np.random.default_rng(seed)
    D = 58.0
    F = nframes(D)
    out = np.zeros((F, G.N, 3))
    pdp = G.pd[G.path]
    n = G.N
    seg_of = G.seg_of[G.path]
    x = G.pos[G.path, 0]
    fl = Flicker(rng, n, 0.3, 1.6)
    fluff = Flicker(rng, n, 0.15, 0.6)

    # shell speckles: sparse soft dots in two colours
    sp1 = np.clip((smooth_noise(rng, pdp, 9, 1) - 0.55) / 0.3, 0, 1)
    sp2 = np.clip((smooth_noise(rng, pdp, 11, 1) - 0.6) / 0.3, 0, 1)

    # crack fronts: jerky (stall, then a fast jump), accelerating towards the break
    reach = np.full(n, np.inf)
    for t0, s0 in TAPS:
        for sgn in (-1, 1):
            ts, ds = [t0], [0.0]
            t, d = t0, 0.0
            while t < BREAK and d < 3000:
                slow = 1.0 if t < BREAK - 4 else 0.15
                t += rng.uniform(0.25, 1.2) * slow
                ts.append(t); ds.append(d + 1e-3)
                d += rng.uniform(4, 22) * (1 if t < BREAK - 4 else 3.0)
                t += 0.05
                ts.append(t); ds.append(d)
            rel = (pdp - s0) * sgn
            ok = rel >= 0
            r = np.full(n, np.inf)
            r[ok] = np.interp(rel[ok], ds, ts, right=np.inf)
            reach = np.minimum(reach, r)
    reach = np.minimum(reach, BREAK - 0.3 + 0.2 * rng.random(n))
    jag = rng.random(n)
    grid = np.arange(0, G.length + 600, 2.0)
    down = smooth_noise(rng, grid, 14, 1)                                    # which pixels of a crack leak first

    # shell pieces after the break (Side stays: it is the half shell the chick sits in)
    cuts = np.sort(rng.uniform(pdp[81], G.length, 16))
    piece = np.searchsorted(cuts, pdp)
    drop_at = BREAK + 0.15 + rng.uniform(0, 1.6, len(cuts) + 1)
    shards = [(c, rng.choice([-1, 1]), rng.uniform(120, 260), BREAK + rng.uniform(0, 0.8)) for c in cuts]
    side = seg_of == 'Side'

    pf = G.pi[G.seg['Porch Front']]
    uh = np.zeros(n); uh[pf] = G.span_u(G.seg['Porch Front'])
    head = np.zeros(n, bool); head[pf] = True
    wingL = seg_of == 'Left'
    wingR = seg_of == 'Right'
    body = (seg_of == 'Porch Left') | (seg_of == 'Porch Right')
    # wing coordinate: 0 at the shoulder (porch corner), 1 at the wing tip
    wl = np.zeros(n)
    wl[wingL] = (pdp[178] - pdp[wingL]) / (pdp[178] - pdp[81])
    wl[wingR] = (pdp[wingR] - pdp[381]) / (pdp[500] - pdp[381])
    peeps = [47.0, 47.35, 49.6, 52.0, 52.3, 52.6]
    blinks = [45.5, 50.6, 54.2]
    flaps = [(48.0, 1.0), (52.9, 1.3), (53.9, 1.3)]
    thumps = [4.0, 5.8, 7.3, 8.6, 9.6, 10.4]

    for f in range(F):
        t = f * DT
        buf = np.zeros((n, 3))
        fade_in = smoothstep(0, 3, t)

        # knocks from inside: a warm pulse on the porch spreading through the shell, and the egg rocks
        knock = sum(np.exp(-((t - k) / 0.07) ** 2) * (0.6 + 0.08 * i) for i, k in enumerate(thumps))
        rock = sum(np.exp(-(t - k) / 1.2) * np.sin(2 * np.pi * (t - k) / 1.1) for k in thumps if t > k)
        rock += 0.6 * sum(np.exp(-(t - k) / 1.0) * np.sin(2 * np.pi * (t - k) / 1.0) for k, _ in TAPS[:4] if t > k)
        tilt = 1 + 0.16 * rock * x / 620

        if t < BREAK + 2.2:
            shellI = 0.34 * fade_in * tilt
            shell = light(SHELL, shellI) + light(SPECK, 0.26 * fade_in * sp1) + light(SPECK2, 0.24 * fade_in * sp2)
            buf += shell
            buf += light(GLOW, 0.5 * knock * np.exp(-(np.abs(pdp - 1485) / 160) ** 2))

            # cracks: light leaks through a jagged, widening set of pixels
            age = t - reach
            opened = smoothstep(0, 7, age)
            leak = (jag < 0.3 + 0.3 * opened) * (age > 0)
            I = leak * (0.5 + 0.25 * opened) * (1 + 0.12 * fl(t))
            I += 1.1 * np.exp(-np.clip(age, 0, None) / 0.12) * (age > 0)
            for t0, s0 in TAPS:                          # the peck itself
                a = t - t0
                if -0.05 < a < 0.5:
                    I += 1.2 * np.exp(-a / 0.12) * np.exp(-((pdp - s0) / 10) ** 2)
            I *= 1 - smoothstep(BREAK, BREAK + 0.4, t)
            buf = buf * (1 - np.clip(leak * 0.9, 0, 1))[:, None] + light(GLOW, I) + light(HOT, 0.6 * I ** 3)

        if t >= BREAK - 0.2:
            b = t - BREAK
            # burst: warm flash from inside, shell pieces drop away, shards fly
            buf += light(HOT, 0.9 * np.exp(-((b - 0.15) / 0.18) ** 2) * (1 - 0.6 * side))
            gone = smoothstep(drop_at[piece], drop_at[piece] + 0.5, t)
            gone[side] = 0
            buf *= (1 - gone)[:, None]
            for c, sg, v, ts in shards:
                a = t - ts
                if 0 < a < 1.4:
                    p = c + sg * v * 0.35 * (1 - np.exp(-a / 0.35))
                    buf += light(SHELL, 0.85 * np.exp(-a / 0.4) * np.exp(-((pdp - p) / 5) ** 2))

            # the chick
            ch = smoothstep(BREAK + 0.3, BREAK + 2.5, t) * keys(t, [(55, 1), (58, 0)])
            if ch > 0:
                tex = 0.85 + 0.12 * fluff(t) + 0.1 * np.interp(pdp + 6 * t, grid, down)
                flap = np.zeros(n)
                for t0, sp in flaps:
                    for k in range(3):
                        a = (t - t0) * sp - k * 0.55
                        flap += np.exp(-((wl - a * 1.6 + 0.2) / 0.22) ** 2) * (a > -0.3) * (a < 1)
                I = np.zeros(n)
                I[wingL | wingR] = (0.55 + 0.4 * flap[wingL | wingR]) * (1 - 0.25 * wl[wingL | wingR])
                I[body] = 0.6
                I[head] = 0.72
                gaze = keys(t, [(43, 0), (44.5, -0.18), (46, 0.18), (47, 0)])
                lid = 1 - max([np.exp(-((t - bl) / 0.07) ** 2) for bl in blinks])
                eyes = np.zeros(n)
                for e0 in (-0.32, 0.32):
                    eyes = np.maximum(eyes, np.exp(-((uh - e0 - gaze) / 0.05) ** 4) * head * lid)
                peep = sum(np.exp(-((t - p) / 0.06) ** 2) for p in peeps)
                beak = np.exp(-((uh - gaze * 0.6) / (0.08 + 0.04 * peep)) ** 2) * head
                fur = light(FLUFF, ch * I * tex * (1 - eyes) * (1 - beak))
                fur += light(FLUFF_TIP, 0.25 * ch * I * np.clip(fluff(t + 7), 0, 1) * (1 - eyes) * (1 - beak))
                fur += light(BEAK, ch * (0.75 + 0.3 * peep) * beak)
                fur[side] = 0
                buf += fur
                # peep: a little sound ring runs out along the roof
                for p in peeps:
                    a = t - p
                    if 0 < a < 1.0:
                        ring = np.exp(-((np.abs(pdp - 1485) - 190 - 600 * a) / 25) ** 2) * (1 - a)
                        buf += light(FLUFF_TIP, 0.35 * ring * ch)
                # half shell with a glowing broken rim at the front
                hs = keys(t, [(55, 1), (58, 0)])
                buf[side] = light(SHELL, 0.28 * hs * np.ones(side.sum())) + light(SPECK, 0.24 * hs * sp1[side])
                rim = np.exp(-((pdp[side] - pdp[80]) / 25) ** 2)
                buf[side] += light(GLOW, 0.4 * hs * rim * (1 + 0.15 * fl(t)[side]))
        out[f][G.path] = buf
    return out
