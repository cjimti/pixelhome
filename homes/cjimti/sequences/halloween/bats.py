"""Colony: a bat colony leaves the attic at dusk, hunts by sonar through the night, and goes home
at dawn, all but one.

The bats are boids (separation, alignment, cohesion, a goal and a height spring) flying in 3-D
around the house. An overhead moon casts their shadows straight down, so a pixel goes dark when a
bat's body or wings pass over it; the wings are a segment across the bat's heading whose span and
lift beat with its wing phase, so a bat crossing a run flaps a wide shadow and one flying along it
is a narrow dot.

Beats: the roof glows with sunset; three chirps ring out from the attic at the free back end of
Side (path index 0); the colony pours out of it in a stream down Side and along Left, mills around
the whole house, then funnels into the porch notch, reaches Porch Front and forks, half each way,
into two counter-rotating rings around the wings; the lead bat of each ring calls in its own tint
(lime left, violet right). Then the sky goes dark and a faint blue moonlight keeps the shadows
visible, but mostly the roof is lit by sonar: every ping is a sphere expanding from the bat at a
fixed speed, so it lights the roof by true 3-D distance (nearest pixel first, fronts running away
both ways) and the flock's shadows cut gaps in it. Moths (amber glints) appear on the roof; the
nearest bat hunts each one with pings that speed up into a feeding buzz as it closes, then a pop.
Dawn glows, the whole
colony streams back down Side into the attic, and one straggler still hunting over Right is left
behind: it panics with loud pings, races back along the roofline, weaving and speeding up, and dives
into the free end; one last chirp comes from inside.
"""
import numpy as np
from pixelhome.fx import DT, hexc, light, smoothstep, keys, lerp, nframes, colormap

CODE = 'HW01'
TITLE = 'Colony'
KIND = 'show'
DESCRIPTION = ('A bat colony pours out of the attic at dusk, swirls around the wings and hunts moths by '
               'sonar, its pings lighting the roof by distance. At dawn they all stream home, all but one.')

SONAR = hexc('#20e8ff')
MOTH = hexc('#ffa020')
POP = hexc('#ffe0a0')
MOON = hexc('#3858ff')
TINT = (SONAR, hexc('#60ff20'), hexc('#c040ff'))   # sonar: night, left ring, right ring

D = 82.0
B = 48                     # colony size
V_PING = 330.0             # sonar wavefront speed, layout units per second
Y0 = 150.0                 # roof height


def _path_point(G):
    """Function s -> 3-D point on the roofline at distance s along the path (clamped)."""
    pts = G.pos[G.path]
    d = G.pd[G.path]

    def at(s):
        s = np.clip(s, 0, d[-1])
        return np.stack([np.interp(s, d, pts[:, k]) for k in range(3)], -1)
    return at


def render(G, seed=11):
    rng = np.random.default_rng(seed)
    F = nframes(D)
    out = np.zeros((F, G.N, 3))
    P = G.pos
    pxz = P[:, [0, 2]]
    along = _path_point(G)

    attic = np.array([-596.0, Y0, -637.0])             # path index 0, the free back end of Side
    inside = np.array([-596.0, Y0, -760.0])
    corner = np.array([-596.0, Y0, -147.0])            # front-left corner, Side -> Left
    left_c = np.array([-400.0, Y0, -320.0])            # left wing loop centre
    right_c = np.array([400.0, Y0, -350.0])            # right wing loop centre
    house_c = np.array([16.0, Y0, -380.0])

    # sky colours across x (left .. right), PWM
    xs = np.clip((P[:, 0] + 600) / 1230, 0, 1)
    dusk = colormap([(0, hexc('#6000a0')), (0.45, hexc('#d01040')), (1, hexc('#ff6000'))])(xs)
    dawn = colormap([(0, hexc('#ff9030')), (0.5, hexc('#ff3060')), (1, hexc('#7020b0'))])(xs)

    # ---- colony state
    pos = np.tile(inside, (B, 1)) + rng.normal(0, 8, (B, 3))
    vel = np.zeros((B, 3))
    rel = 5.0 + 12.5 * (np.arange(B) / (B - 1)) ** 0.75          # release times: trickle, then pour
    rel += rng.uniform(-0.08, 0.08, B)
    alive = np.zeros(B, bool)
    home = np.zeros(B, bool)
    group = (np.arange(B) % 2).astype(float)                     # 0 = left ring, 1 = right ring
    flap_f = rng.uniform(4.2, 6.0, B)
    flap_p = rng.uniform(0, 2 * np.pi, B)
    yoff = rng.uniform(-35, 35, B)
    ring_ph = rng.uniform(0, 2 * np.pi, B)
    ring_r = rng.uniform(205, 235, B)
    fork_wp = np.zeros(B, int)          # 0 porch mouth, 1 Porch Front, 2 corner, 3 down the side, 4 ring
    led = [False, False]
    vmax = rng.uniform(230, 290, B)
    jit = np.zeros((B, 3))
    # return order: those on the left ring go first, the right ring after
    ret = 60.5 + 6.0 * np.argsort(np.argsort(group * 10 + rng.uniform(0, 1, B))) / B
    ret_wp = np.zeros(B, int)
    STRAG = int(np.flatnonzero(group == 1)[B // 4])
    ret[STRAG] = 1e9
    size = rng.uniform(0.85, 1.15, B)
    size[STRAG] = 1.8
    strag_s0 = strag_d0 = strag_p0 = None

    # sonar pings: (origin, birth time, amplitude, decay)
    pings = [(attic.copy(), tb, a, 0.35, 0) for tb, a in ((2.6, 0.35), (3.5, 0.45), (4.2, 0.6))]
    ambient_next = 27.0

    # moths: (appear time, path index), hunters chosen when they appear
    moth_plan = [(37.0, 440), (42.5, 300), (47.5, 120), (49.0, 470), (54.0, 30), (63.0, 452), (68.0, 405)]
    moths = []                       # dicts: p, born, hunter, next_ping, caught

    def ping(o, tb, a, tau=0.45, c=0):
        pings.append((o.copy(), tb, a, tau, c))

    for f in range(F):
        t = f * DT

        # ---------------- goals
        alive |= (t >= rel) & ~home
        goal = np.zeros((B, 3))
        age = t - rel
        # emergence stream: follow Side to the corner, along Left, then out toward the street
        s_route = np.clip(age, 0, None) * 260 + 90
        route_goal = along(s_route)
        out_pt = np.array([-60.0, Y0, 40.0])
        past = s_route > G.pd[G.path][178]
        route_goal[past] = out_pt
        # milling: one big loop around the house; from 23 s the flock funnels into the porch notch,
        # reaches Porch Front and forks, half each way, down Porch Left / Porch Right into two
        # counter-rotating rings around the wings
        a_ang = ring_ph + 0.9 * t
        big = house_c + np.stack([760 * np.cos(a_ang), 0 * a_ang, 360 * np.sin(a_ang)], -1)
        cen = np.where(group[:, None] > 0.5, right_c, left_c)
        sgn = np.where(group > 0.5, -1.0, 1.0)                       # mirror the spin
        a2 = ring_ph + sgn * 1.25 * t
        rings = cen + np.stack([ring_r * np.cos(a2), 0 * a2, 0.9 * ring_r * np.sin(a2)], -1)
        joined = age > 6.5
        mill = big.copy()
        if t >= 23.0:
            xs_side = np.where(group > 0.5, 150.0, -194.0)
            wps = np.stack([np.stack([np.full(B, 16.0), np.full(B, -60.0)], -1),
                            np.stack([np.full(B, 16.0), np.full(B, -575.0)], -1),
                            np.stack([xs_side, np.full(B, -575.0)], -1),
                            np.stack([xs_side + np.where(group > 0.5, 2, -2), np.full(B, -250.0)], -1)])
            for i in np.flatnonzero(alive & joined & (fork_wp < 4)):
                w_ = wps[fork_wp[i], i]
                if np.linalg.norm(pos[i, [0, 2]] - w_) < (55 if fork_wp[i] else 110):
                    fork_wp[i] += 1
                    g_ = int(group[i])
                    if fork_wp[i] == 3 and not led[g_]:                 # the lead bat of each ring calls
                        led[g_] = True
                        ping(pos[i], t, 1.0, 1.1, 1 + g_)
                    if fork_wp[i] == 4:                                  # join the ring just ahead of itself
                        c_ = cen[i]
                        ang = np.arctan2((pos[i, 2] - c_[2]) / 0.9, pos[i, 0] - c_[0])
                        ring_ph[i] = ang - sgn[i] * 1.25 * t + sgn[i] * 0.45
            fw = np.minimum(fork_wp, 3)
            pts = wps[fw, np.arange(B)]
            mill = np.stack([pts[:, 0], np.full(B, Y0), pts[:, 1]], -1)
            a2 = ring_ph + sgn * 1.25 * t
            rings = cen + np.stack([ring_r * np.cos(a2), 0 * a2, 0.9 * ring_r * np.sin(a2)], -1)
            mill[fork_wp == 4] = rings[fork_wp == 4]
        goal[:] = np.where(joined[:, None], mill, route_goal)
        goal[:, 1] = Y0 + yoff + 12 * np.sin(1.3 * t + ring_ph)

        # moth hunts: the hunter slows as it closes in
        hunting = np.zeros(B, bool)
        slow = np.ones(B)
        for m in moths:
            if m['caught'] is None and m['hunter'] is not None:
                h = m['hunter']
                goal[h] = m['p'] + np.array([0, 4, 0])
                hunting[h] = True
                slow[h] = float(np.clip(np.linalg.norm(pos[h] - goal[h]) / 220, 0.3, 1))

        # going home
        going = (t >= ret) & alive
        for i in np.flatnonzero(going):
            wps = (corner + np.array([0, 0, 90]), corner + np.array([0, 0, -60]), attic, inside)
            if ret_wp[i] < 3 and np.linalg.norm(pos[i, [0, 2]] - wps[ret_wp[i]][[0, 2]]) < 70:
                ret_wp[i] += 1
            goal[i] = wps[ret_wp[i]]
            goal[i, 1] = Y0 + 0.3 * yoff[i]
            vmax[i] = 330

        # ---------------- boids
        idx = np.flatnonzero(alive)
        if len(idx):
            p, v = pos[idx], vel[idx]
            diff = p[:, None, :] - p[None, :, :]
            dist = np.linalg.norm(diff, axis=-1) + np.eye(len(idx)) * 1e6
            sep = ((diff / dist[..., None] ** 2) * (dist < 45)[..., None]).sum(1) * 2600
            nb = (dist < 110).astype(float)
            cnt = nb.sum(1, keepdims=True) + 1e-9
            ali = np.where(cnt > 0.5, (nb @ v) / cnt - v, 0) * 0.9
            coh = np.where(cnt > 0.5, (nb @ p) / cnt - p, 0) * 0.6
            to = goal[idx] - p
            desired = to / (np.linalg.norm(to, axis=1, keepdims=True) + 1e-9) * (vmax[idx] * slow[idx])[:, None]
            steer = (desired - v) * 2.6
            jit[idx] = jit[idx] * 0.93 + rng.normal(0, 90, (len(idx), 3)) * 0.35
            acc = steer + sep + ali + coh + jit[idx] * np.array([1, 0.5, 1])
            acc[:, 1] += (goal[idx, 1] - p[:, 1]) * 3.0
            v = v + acc * DT
            sp = np.linalg.norm(v, axis=1, keepdims=True) + 1e-9
            lo = np.where(hunting[idx], 60, 140)[:, None]
            v = v / sp * np.clip(sp, lo, vmax[idx, None])
            # fresh out of the attic: launched along Side
            newb = age[idx] < DT * 1.5
            v[newb] = np.array([0, 0, 240.0])
            p = p + v * DT
            pos[idx], vel[idx] = p, v
            # into the attic
            gone = going[idx] & (p[:, 2] < -690) & (np.abs(p[:, 0] + 596) < 90)
            if idx[gone].size:
                home[idx[gone]] = True
                alive[idx[gone]] = False

        # the straggler: panics at 72, then from 73 races the roofline from where it is to the attic,
        # weaving across the line, speeding up as it goes; at the free end it dives in
        if t >= 73.0 and alive[STRAG]:
            if strag_s0 is None:
                strag_s0 = t
                k = np.argmin(np.linalg.norm(pxz - pos[STRAG, [0, 2]], axis=1))
                strag_d0 = G.pd[k]
                strag_p0 = pos[STRAG].copy()
            tau = t - strag_s0
            sd = strag_d0 - (240 * tau + 70 * tau ** 2)
            if sd > 0:
                q = along(sd)
                tang = along(sd - 8) - along(sd + 8)
                tang /= np.linalg.norm(tang) + 1e-9
                side = np.array([-tang[2], 0, tang[0]])
                q = q + side * 16 * np.sin(2 * np.pi * 2.2 * tau) + np.array([0, 10 * np.sin(5 * tau), 0])
                q = lerp(strag_p0, q, smoothstep(0, 0.5, tau))
            else:
                q = attic + np.array([0, 0, sd * 1.5])
            vel[STRAG] = (q - pos[STRAG]) / DT
            pos[STRAG] = q
            if q[2] < -700:
                alive[STRAG], home[STRAG] = False, True
                ping(attic, t + 0.9, 0.45, 0.3)                 # one last chirp from inside

        # ---------------- moths and hunting
        for (tm, pi) in moth_plan:
            if abs(t - tm) < DT / 2:
                mp = G.pos[G.path[pi]].copy()
                cand = np.flatnonzero(alive & (t < ret))
                if tm > 60:
                    cand = np.array([STRAG])
                h = int(cand[np.argmin(np.linalg.norm(pos[cand] - mp, axis=1))]) if cand.size else None
                moths.append(dict(p=mp, base=mp.copy(), born=t, hunter=h, next=t + 0.3, caught=None,
                                  ph=rng.uniform(0, 6, 3)))
        for m in moths:
            if m['caught'] is not None:
                continue
            lt = t - m['born']
            m['p'] = m['base'] + np.array([30 * np.sin(1.7 * lt + m['ph'][0]), 0,
                                           18 * np.sin(2.3 * lt + m['ph'][1])])
            h = m['hunter']
            if h is None or not alive[h]:
                continue
            d = np.linalg.norm(pos[h] - m['p'])
            if t >= m['next'] and lt > 0.6:
                interval = float(np.clip(d / 650, 0.055, 0.6))
                amp = float(np.clip(0.25 + d / 900, 0.3, 0.8))
                ping(pos[h], t, amp, 0.2 + 0.3 * min(1, d / 400))
                m['next'] = t + interval
            if d < 22 and lt > 2.0 and t < 72.5:
                m['caught'] = t
        if t >= 72.0 and alive[STRAG] and (strag_s0 is None or t - strag_s0 < 5.0):
            if not pings or t - pings[-1][1] > 0.32:
                ping(pos[STRAG], t, 0.95, 0.4)                # distress calls
        if abs(t - 57.6) < DT / 2:                           # pre-dawn chorus: everyone calls at once
            for i in np.flatnonzero(alive):
                ping(pos[i] + vel[i] * 0.6, t + rng.uniform(0.4, 1.6), 0.45, 0.6)
        if abs(t - 60.0) < DT / 2:                           # the call home, from the corner
            ping(corner + np.array([0, 30, 0]), t, 1.0, 1.6)
            ping(corner + np.array([0, 30, 0]), t + 0.45, 0.7, 1.3)
        # ambient pings from the flock at night
        if t >= ambient_next and t < 60 and alive.any():
            i = rng.choice(np.flatnonzero(alive))
            ping(pos[i], t, float(keys(t, [(27, 0.45), (38, 0.85), (60, 0.85)])), 0.9,
                 (1 + int(group[i])) if t < 36 else 0)
            ambient_next = t + float(keys(t, [(27, 1.8), (38, 1.1), (60, 1.1)])) * rng.uniform(0.6, 1.4)

        # ---------------- light
        dusk_k = keys(t, [(0, 0), (2.0, 0.42), (32, 0.42), (40, 0.0)])
        dawn_k = keys(t, [(59, 0), (66, 0.38), (79, 0.38), (82, 0)])
        night_k = keys(t, [(32, 0), (40, 0.14), (60, 0.14), (66, 0)])
        col = dusk * (dusk_k ** 2.2) + dawn * (dawn_k ** 2.2) + light(MOON, np.full(G.N, night_k))

        son = np.zeros((3, G.N))
        keep = []
        for pg in pings:
            o, tb, a, tau, c = pg
            ag = t - tb
            if ag > 6 * tau + 0.3:
                continue
            keep.append(pg)
            if ag < 0:
                continue
            dd = np.linalg.norm(P - o, axis=1)
            r = V_PING * ag
            front = np.exp(-((dd - r) / 34) ** 2)
            inner = np.where(dd < r, 0.3 * np.exp(-(r - dd) / 110), 0)
            son[c] += 1.4 * a * (front + inner) * np.exp(-ag / tau) / (1 + r / 700)
        pings = keep
        for c in range(3):
            if son[c].any():
                col = col + light(TINT[c], np.minimum(son[c], 1.0))

        # shadows from an overhead moon: body plus a flapping wing segment, in the xz plane
        shade = np.zeros(G.N)
        idx = np.flatnonzero(alive)
        if len(idx):
            p = pos[idx]
            hv = vel[idx][:, [0, 2]]
            hv = hv / (np.linalg.norm(hv, axis=1, keepdims=True) + 1e-9)
            lat = np.stack([-hv[:, 1], hv[:, 0]], -1)
            ph = 2 * np.pi * flap_f[idx] * t + flap_p[idx]
            span = size[idx] * 40 * (0.3 + 0.65 * np.abs(np.cos(ph)))            # wings sweep in and out
            c = p[:, [0, 2]]
            a_ = c - lat * span[:, None]
            b_ = c + lat * span[:, None]
            ab = b_ - a_
            ap = pxz[None, :, :] - a_[:, None, :]
            u = np.clip((ap * ab[:, None, :]).sum(-1) / ((ab ** 2).sum(-1)[:, None] + 1e-9), 0, 1)
            near = ap - u[..., None] * ab[:, None, :]
            dw = np.linalg.norm(near, axis=-1)
            db = np.linalg.norm(pxz[None] - c[:, None], axis=-1)
            hgt = np.abs(p[:, 1] - Y0)[:, None]                        # higher = softer shadow
            soft = 6 + hgt * 0.15
            sh = np.maximum(np.clip(1 - (db - 13 * size[idx, None]) / soft, 0, 1),
                            0.9 * np.clip(1 - (dw - 4 * size[idx, None]) / soft, 0, 1))
            shade = sh.max(0)
        col = col * (1 - shade)[:, None]

        # moths and their end
        for m in moths:
            if m['caught'] is None:
                g = smoothstep(m['born'], m['born'] + 0.8, t) * (1 - smoothstep(73, 74, t))
                flick = 0.75 + 0.25 * np.sin(2 * np.pi * 9 * t + m['ph'][2])
                dd = np.linalg.norm(P - m['p'], axis=1)
                col += light(MOTH, 0.75 * g * flick * np.exp(-(dd / 10) ** 2))
            else:
                ag = t - m['caught']
                if ag < 1.2:
                    dd = np.linalg.norm(P - m['p'], axis=1)
                    col += light(POP, 0.9 * np.exp(-ag / 0.25) * np.exp(-(dd / (12 + 260 * ag)) ** 2))

        out[f] = np.clip(col, 0, 1)
    return out
