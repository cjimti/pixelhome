"""The Cherry Tree: Porch Right is the trunk (from the street it reads as vertical) and the canopy
hangs round the back corner onto the Porch Front. Young George walks in from the right free end and
chops; cherries fall down the trunk under gravity and roll to his feet. The tree topples: its light
swings from the vertical run onto the Right wing as a projected rotation, and George scrambles off
the end. Father walks the long way round, George blushes the whole house red, and one last cherry
rolls back in to bonk him."""
import numpy as np
from pixelhome.fx import DT, hexc, light, smoothstep, keys, lerp, Flicker, nframes

CODE = 'PR02'
TITLE = 'The Cherry Tree'
KIND = 'show'
DESCRIPTION = ('Young George, a hatchet and a cherry tree on the porch. Chop, chop, timber. Father walks '
               'round the long way, the house blushes, and one last cherry has the final word.')

TRUNK = hexc('#8a3608')
LEAF = hexc('#2f7a14')
CHERRY = hexc('#e8081a')
CREAM = hexc('#ffe0a8')
BRASS = hexc('#ffa030')
NAVY = hexc('#2440c0')
ROSE = hexc('#d02030')
DUST = hexc('#c07030')


def render(G, seed=22):
    rng = np.random.default_rng(seed)
    D = 60.0
    out = np.zeros((nframes(D), G.N, 3))
    s = G.pd[G.path]                       # distance along the path, in path order
    i_top, i_base, i_end = 332, 380, 500
    s_base, s_end = s[i_base], s[i_end]
    L = s_base - s[i_top]                  # trunk length = Porch Right
    q_up = np.where(np.arange(G.N) <= i_base, s_base - s, -1.0)       # tree coords when upright
    q_dn = np.where(np.arange(G.N) > i_base, s - s_base, -1.0)        # ... when lying on the Right wing
    leafy = Flicker(rng, G.N, 0.2, 1.2)

    def tree_I(q):
        """Brightness profile of the tree along its own length q (0 at the base)."""
        trunk = smoothstep(-2, 4, q) * (1 - smoothstep(L - 60, L - 10, q)) * (1 - 0.4 * q / L)
        canopy = smoothstep(L - 110, L - 50, q) * (1 - smoothstep(L + 120, L + 180, q))
        return trunk, canopy

    def blob(c, w):
        return np.exp(-((s - c) / w) ** 2)

    # cherries hang in the canopy at fixed tree coordinates
    nc = 13
    cq = np.sort(rng.uniform(L - 70, L + 150, nc))
    chops = [12.6, 14.4, 16.2, 18.0, 19.4, 21.6]
    drop = {k: (chops[k], j) for k, j in enumerate(rng.choice(nc, len(chops), replace=False))}
    dropped = {j: t0 for t0, j in drop.values()}
    roll_to = {j: rng.uniform(8, 26) for j in dropped}
    scatter_v = rng.uniform(60, 220, nc)          # after the crash, cherries roll off along Right
    last = [j for j in range(nc) if j not in dropped][-1]   # the one that comes back
    g_grav = 900.0
    T_FALL, T_LAND = 23.6, 25.0
    george_k = [(2.5, s_end + 25), (10.5, s_base + 28), (23.8, s_base + 28), (25.2, s_end + 30),
                (31.0, s_end + 30), (31.8, s_end - 12), (32.6, s_end + 30), (34.0, s_end + 30),
                (39.5, s_base + 42)]
    father_k = [(34.5, s[262] - 20), (43.5, s_base - 14)]

    for f in range(len(out)):
        t = f * DT
        buf = light(NAVY, 0.08 * keys(t, [(0, 0), (2, 1), (D - 3, 1), (D, 0)]) * (0.85 + 0.15 * leafy(t * 0.3)))
        # the tree: rotation theta 0 (upright) -> pi/2 (lying on the Right wing), gravity-accelerated
        if t < T_FALL:
            th = 0.012 * np.sin(2 * np.pi * 3 * t) * smoothstep(22.5, 23.4, t)       # creak
        elif t < T_LAND:
            th = np.pi / 2 * ((t - T_FALL) / (T_LAND - T_FALL)) ** 2
        else:
            tb = t - T_LAND
            th = np.pi / 2 - 0.08 * abs(np.sin(tb * 9)) * np.exp(-tb * 4)              # bounce
        c, sn = max(np.cos(th), 1e-3), max(np.sin(th), 1e-3)
        qa = np.where(q_up >= 0, q_up / c, -1)
        qb = np.where(q_dn >= 0, q_dn / sn, -1)
        tr_a, ca_a = tree_I(qa)
        tr_b, ca_b = tree_I(qb)
        tre = keys(t, [(0, 0), (2, 1), (T_LAND, 1), (T_LAND + 0.1, 1), (32, 0.45), (D - 4, 0.45), (D, 0)])
        shake = 1.0
        for tc in chops:
            if tc <= t < tc + 0.8:
                shake = 1 + 0.35 * np.exp(-(t - tc) / 0.2) * np.sin((t - tc) * 50)
        rust = 0.85 + 0.15 * leafy(t)
        buf += light(TRUNK, 0.32 * tre * (tr_a + tr_b))
        buf += light(LEAF, 0.62 * tre * (ca_a + ca_b) * rust * shake)
        # a shock runs up the trunk on every chop
        for tc in chops:
            if tc <= t < tc + 0.7:
                front = (t - tc) * 700
                buf += light(BRASS, 0.5 * np.exp(-((qa - front) / 18) ** 2) * (qa >= 0) * (1 - (t - tc) / 0.7))

        # cherries
        for j in range(nc):
            q = cq[j]
            if j in dropped and t >= dropped[j]:
                tf = t - dropped[j]
                qf = q - 0.5 * g_grav * tf ** 2
                if qf > 0:                                            # falling down the trunk
                    buf += light(CHERRY, 0.9 * np.exp(-((q_up - qf) / 7) ** 2) * (q_up >= 0))
                    continue
                t_hit = np.sqrt(2 * q / g_grav)
                tr = tf - t_hit
                pos = s_base + roll_to[j] * (1 - np.exp(-tr / 0.5))
                if t > T_LAND:                                        # swept along by the crash
                    pos += scatter_v[j] * 0.5 * (1 - np.exp(-(t - T_LAND) / 0.5))
                bonk = 1 + 1.2 * np.exp(-tr / 0.12)
                buf += light(CHERRY, 0.75 * bonk * blob(pos, 5) * keys(t, [(D - 5, 1), (D - 1, 0)]))
                continue
            if t < T_LAND + 0.05:                                     # hanging on the tree
                hang = 0.8 * (0.9 + 0.1 * np.sin(t * 2 + j))
                if c > 0.05:
                    buf += light(CHERRY, hang * tre * np.exp(-((qa - q) / 6) ** 2) * (qa >= 0))
                if sn > 0.05:
                    buf += light(CHERRY, hang * tre * np.exp(-((qb - q) / 6) ** 2) * (qb >= 0))
            else:                                                      # scattered by the crash
                tc = t - T_LAND
                pos = s_base + q + scatter_v[j] * 0.5 * (1 - np.exp(-tc / 0.5))
                if j == last and t > 50.5:                                # ... and the one that returns
                    u = smoothstep(50.5, 54.4, t)
                    pos = lerp(pos, s_base + 50, u)
                buf += light(CHERRY, 0.8 * blob(pos, 5) * (pos < s_end + 3) * keys(t, [(D - 3, 1), (D, 0)]))

        if T_LAND <= t < T_LAND + 3:                                   # the crash
            tc = t - T_LAND
            buf += light(CREAM, 0.9 * np.exp(-tc / 0.15) * (q_dn >= 0) * (q_dn < L + 140))
            buf += light(DUST, 0.35 * np.exp(-tc / 1.0) * np.exp(-((q_dn - L) / 120) ** 2) *
                         (0.6 + 0.4 * leafy(t * 5)) * (q_dn >= 0))

        # George: a small cream figure; hatchet glint on his tree side
        g = keys(t, george_k)
        walking = abs(keys(t + 0.05, george_k) - g) > 0.05
        bob = 1 + (0.18 * abs(np.sin(np.pi * 3.2 * t)) if walking else 0.0)
        tremble = 1.0
        if 43.8 < t < 46.4:
            tremble = 1 + 0.12 * np.sin(t * 60)
        blush = smoothstep(46.4, 47.2, t)
        gcol = lerp(CREAM, ROSE, blush)
        gI = keys(t, [(2.5, 0), (3, 1), (D - 2, 1), (D, 0)]) * bob * tremble
        bonked = 54.4 <= t < 55.5
        if bonked:
            gI *= 1 + 0.9 * np.exp(-(t - 54.4) / 0.15) * abs(np.cos((t - 54.4) * 30))
        buf += light(gcol, 0.8 * gI * blob(g, 5))
        if 10.5 < t < 23.8:
            sw = 0.0
            for tc in chops:
                if tc - 0.45 <= t < tc + 0.3:
                    sw = keys(t, [(tc - 0.45, 0), (tc - 0.15, -1), (tc, 1), (tc + 0.3, 0)])
            hx = g - 9 - 5 * sw
            flash = sum(np.exp(-((t - tc) / 0.05) ** 2) for tc in chops)
            buf += light(BRASS, (0.55 + 0.45 * flash) * blob(hx, 3.2))

        # the blush: a rose wave spreads from George over the whole house and ebbs
        if t > 46.8:
            tb = t - 46.8
            dd = np.abs(s - g)
            reach = smoothstep(tb * 650 + 80, tb * 650, dd) * np.exp(-dd / 900)
            pulse = 0.75 + 0.25 * np.cos(2 * np.pi * 1.1 * tb)
            wave = reach * pulse * keys(t, [(46.8, 0.55), (49, 0.5), (52, 0.12), (56, 0)])
            buf += light(ROSE, wave)

        # Father: wider, navy coat with a cream wig, heavy footfalls; walks the long way round
        if t > 34.5:
            p = keys(t, father_k)
            walking = t < 43.5
            ph = (t * 1.4) % 1
            step = (0.25 * np.exp(-ph / 0.08)) if walking else 0.0
            stern = sum(0.4 * np.exp(-((t - tc) / 0.35) ** 2) for tc in (44.2, 45.4))
            fI = keys(t, [(34.5, 0), (35.5, 1), (D - 2, 1), (D, 0)])
            buf += light(NAVY, fI * (0.7 + step + stern) * blob(p, 14))
            buf += light(CREAM, fI * (0.35 + stern) * blob(p, 5))
            if walking:
                buf += light(NAVY, 0.4 * fI * step * blob(p, 40))
            if t > 50.5:                                               # forgiveness: a bridge of warm light
                lo, hi = min(p, g), max(p, g)
                br = smoothstep(lo - 6, lo + 4, s) * smoothstep(hi + 6, hi - 4, s)
                buf += light(BRASS, 0.45 * br * keys(t, [(50.5, 0), (52, 1), (D - 2, 1), (D, 0)]))
        out[f][G.path] = buf
    return out
