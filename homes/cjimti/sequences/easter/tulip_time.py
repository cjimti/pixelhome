"""Tulip Time: Two mirrored flower beds grow on the wings. Each tulip is a little life on a few
pixels: a green shoot widens, a tight bud colours at its tip, then the petals open into a cup
(brighter at the rim, a gold heart in the middle), the beds blooming outward from the porch corners
in mirror image. A bee flies a real 3-D route from flower to flower, curving back through the porch
to cross between wings; each flower it lands on bobs. A gust sweeps in from both ends and sways
every bloom and tears a few petals loose, then evening comes and the tulips close up again."""
import numpy as np
from pixelhome.fx import DT, hexc, light, keys, smoothstep, smooth_noise, Flicker, nframes, catmull_closed

CODE = 'EA05'
TITLE = 'Tulip Time'
KIND = 'show'
DESCRIPTION = 'Mirrored tulip beds sprout, bud and open into cups along both wings. A bee flies flower to flower through the porch, a gust sways them all, and at dusk they close.'


def lin(h):
    return hexc(h) ** 2.2


LEAF = lin('#4fd06a')
SOIL = lin('#2d6b3a')
HEART = lin('#ffc23a')
BEE = lin('#ffd84a')
PETALS = [lin(h) for h in ('#ff6f9f', '#ffd166', '#c39bff', '#ff8a6a', '#fff0f4', '#ff9ad0', '#9fd4ff', '#ffb35c')]


def render(G, seed=25):
    rng = np.random.default_rng(seed)
    D = 62.0
    F = nframes(D)
    out = np.zeros((F, G.N, 3))
    pdp = G.pd[G.path]
    pp = G.pos[G.path]
    n = G.N
    seg = G.seg_of[G.path]
    grass_n = smooth_noise(rng, pdp, 25)
    sway_f = Flicker(rng, 1, 0.12, 0.35)

    # flowers: same distance from the porch corner on both wings, so the beds mirror each other
    cL, cR = pdp[178], pdp[381]
    flowers = []
    for k in range(9):
        d_in = 30 + 50 * k
        tb = 3.0 + 1.5 * k + rng.uniform(-0.3, 0.3)
        col = PETALS[k % len(PETALS)]
        if d_in < cL - pdp[81] - 18:
            flowers.append(dict(c=cL - d_in, side=-1, k=k, t0=tb + rng.uniform(0, 0.4), col=col, bob=[],
                                wmax=11.0, heart=HEART))
        if d_in < pdp[500] - cR - 18:
            flowers.append(dict(c=cR + d_in, side=1, k=k, t0=tb + rng.uniform(0, 0.4), col=col, bob=[],
                                wmax=11.0, heart=HEART))
    # second wave: small daffodils down the runs that go away from the street, front to back
    for name in ('Side', 'Porch Left', 'Porch Right', 'Porch Front'):
        idx = G.pi[G.seg[name]]
        a, b = pdp[idx.min()], pdp[idx.max()]
        for c in np.arange(a + 22, b - 15, 44.0):
            zc = np.interp(c, pdp, pp[:, 2])
            depth = (-150 - zc) / 490
            if name == 'Porch Front':
                depth = 1.0 + abs(c - (a + b) / 2) / 400
            white = rng.random() < 0.35
            flowers.append(dict(c=c, side=0, k=int(depth * 6), t0=19 + 9 * depth + rng.uniform(-0.4, 0.4),
                                col=lin('#fff6e0') if white else lin('#ffe45c'), bob=[], wmax=7.0,
                                heart=lin('#ff8a1a') if not white else lin('#ffd23a')))

    def at(s):
        return np.array([np.interp(s, pdp, pp[:, c]) for c in range(3)])

    # bee route: alternate wings, crossing back through the porch (an open loop drawn with a spline)
    order = [f for f in flowers if f['side'] < 0][2::2] + [f for f in flowers if f['side'] > 0][1::2]
    rng.shuffle(order)
    route, hover = [at(cL + 120)], [0.0]
    last_side = -1
    for fl_ in order[:8]:
        if fl_['side'] != last_side:
            route.append(np.array([-20.0 if fl_['side'] > 0 else -40.0, 150.0, -540.0]))
            hover.append(0.0)
        route.append(at(fl_['c']))
        hover.append(0.9)
        fl_['bob'].append(None)
        last_side = fl_['side']
    route.append(at(cR + 150))
    hover.append(0.0)
    route = np.array(route)
    seg_len = np.linalg.norm(np.diff(route, axis=0), axis=1)
    arrive = [24.0]                       # arrival time at each route point; it hovers, then flies on at ~260/s
    for i, L in enumerate(seg_len):
        arrive.append(arrive[i] + hover[i] + L / 260)
    t_b, bee_end = arrive[0], arrive[-1]
    j = 0
    for i in range(len(route)):
        if hover[i] > 0:
            for fl_ in flowers:
                if np.linalg.norm(route[i] - at(fl_['c'])) < 1:
                    fl_['bob'] = [b for b in fl_['bob'] if b is not None] + [arrive[i]]

    def bee_pos(t):
        """Hover at a flower, then a curved flight (bulging toward the street) to the next point."""
        i = int(np.searchsorted(arrive, t, side='right')) - 1
        i = min(max(i, 0), len(route) - 2)
        u = smoothstep(arrive[i] + hover[i], arrive[i + 1], t)
        a, b = route[i], route[i + 1]
        mid = (a + b) / 2 + np.array([0, 0, 60])
        return (1 - u) ** 2 * a + 2 * u * (1 - u) * mid + u ** 2 * b

    petals_loose = []
    for fl_ in flowers:
        if fl_['side'] != 0 and rng.random() < 0.5:
            petals_loose.append((fl_['c'], fl_['col'], fl_['side'], 47.0 + rng.uniform(0, 1.5) + 0.15 * fl_['k']))

    for f in range(F):
        t = f * DT
        buf = np.zeros((n, 3))
        day = keys(t, [(0, 0), (2, 1), (54, 1), (61.5, 0)])
        buf += light(SOIL, 0.2 * day * (0.85 + 0.15 * grass_n) * (1 + 0.1 * np.sin(pdp / 40 - t * 0.8)))

        gust_front = keys(t, [(45, 0.0), (49.5, 520.0)])            # from both outer ends inward
        for fl_ in flowers:
            a = t - fl_['t0']
            if a < 0:
                continue
            d_out = (fl_['c'] - pdp[81]) if fl_['side'] < 0 else (pdp[500] - fl_['c'])
            hit = np.exp(-((d_out - gust_front) / 70) ** 2) if 45 < t < 50 else 0.0
            sway = 2.2 * sway_f(t + fl_['k'])[0] - fl_['side'] * 9 * hit
            bob = sum(np.exp(-((t - b0 - 0.25) / 0.25) ** 2) for b0 in fl_['bob'] if b0 is not None)
            x = pdp - fl_['c'] - sway
            near = np.abs(x) < 40
            if not near.any():
                continue
            xs = x[near]
            shoot = smoothstep(0, 2.0, a)
            bud = smoothstep(2.0, 3.5, a)
            close = smoothstep(53 + 0.2 * fl_['k'], 57 + 0.2 * fl_['k'], t)
            open_ = smoothstep(3.5, 7.0, a) * (1 - close)
            leafw = 3 + 9 * shoot
            g = 0.45 * shoot * np.exp(-(xs / leafw) ** 2) * (1 - 0.7 * open_)
            w = 3.0 + 1.5 * bud + fl_['wmax'] * open_
            env = smoothstep(w + 2.5, w - 1.5, np.abs(xs))
            cup = 0.55 + 0.45 * np.clip(np.abs(xs) / w, 0, 1) ** 2
            pI = env * (0.4 * bud + 0.4 * open_ * cup + 0.2 * bud * (1 - open_)) * (1 + 0.35 * bob)
            heart = 0.75 * open_ * np.exp(-(xs / 3.0) ** 2) * (1 + 0.6 * bob)
            col = light(LEAF, g * day) + light(fl_['col'], pI * day) + light(fl_['heart'], heart * day)
            buf[near] = buf[near] * (1 - 0.8 * env[:, None]) + col

        # the bee
        if t_b - 0.5 < t < bee_end + 0.5:
            b = bee_pos(t) + np.array([5 * np.sin(2 * np.pi * 5.3 * t), 0, 5 * np.cos(2 * np.pi * 4.1 * t)])
            d = np.linalg.norm(pp - b, axis=1)
            vis = smoothstep(t_b - 0.5, t_b + 0.3, t) * smoothstep(bee_end + 0.5, bee_end - 0.3, t)
            buzz = 0.85 + 0.15 * np.sin(2 * np.pi * 11 * t)
            buf += light(BEE, vis * buzz * np.exp(-(d / 17) ** 2))
            buf += light(lin('#ffffff'), 0.6 * vis * np.exp(-(d / 7) ** 2))

        # loose petals ride the gust toward the porch, tumbling (flicker as they turn)
        for c0, col, side, ts in petals_loose:
            a = t - ts
            if 0 < a < 5:
                p = c0 - side * 160 * a * (1 - 0.12 * a)
                turn = 0.5 + 0.5 * np.cos(2 * np.pi * 1.4 * a + c0)
                buf += light(col, (0.35 + 0.4 * turn) * np.exp(-a / 2.5) * np.exp(-((pdp - p) / 5) ** 2))
        out[f][G.path] = buf
    return out
