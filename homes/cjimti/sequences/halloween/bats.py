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


# ---------------------------------------------------------------- music
# The score hears what the lights do. The colony is a simulation, so its events (every sonar ping, every
# release from the attic, every moth and catch, the straggler's run) only exist while it runs: _colony()
# replays render()'s flight model step for step, with the same rng draws in the same order, and logs them.
# It leaves the light out, which draws no random numbers, so the log is exactly the show that plays.
#
# The music is E minor, a slow nocturne that never keeps a beat the bats don't: dusk is a warm pad that
# darkens into a cold drone at night and opens into E major at dawn. Every ping is a pitched sonar blip
# (a downward chirp with a celesta or harp note under it) placed where it happens: panned by x, louder
# toward the street, its note taken from the chord sounding at that moment, so the flock's calls play
# the harmony. The lead bats' calls are the colony's theme (lime left, violet right). Wings are a
# leathery flutter, each bat's wingbeat panned to where it is. Moths are a glassy amber trill; a hunt
# climbs in pitch as it speeds up into a buzz, and the catch is a pop. The straggler gets a solo: alarm
# calls, then a pizzicato run that follows it along the roof, accelerating as it does, into the attic.

def _colony(G, seed=11):
    """render()'s flight, without the light: returns the events the score plays to."""
    rng = np.random.default_rng(seed)
    F = nframes(D)
    P = G.pos
    pxz = P[:, [0, 2]]
    along = _path_point(G)
    attic = np.array([-596.0, Y0, -637.0])
    inside = np.array([-596.0, Y0, -760.0])
    corner = np.array([-596.0, Y0, -147.0])
    left_c = np.array([-400.0, Y0, -320.0])
    right_c = np.array([400.0, Y0, -350.0])
    house_c = np.array([16.0, Y0, -380.0])

    pos = np.tile(inside, (B, 1)) + rng.normal(0, 8, (B, 3))
    vel = np.zeros((B, 3))
    rel = 5.0 + 12.5 * (np.arange(B) / (B - 1)) ** 0.75
    rel += rng.uniform(-0.08, 0.08, B)
    alive = np.zeros(B, bool)
    home = np.zeros(B, bool)
    group = (np.arange(B) % 2).astype(float)
    flap_f = rng.uniform(4.2, 6.0, B)
    flap_p = rng.uniform(0, 2 * np.pi, B)
    yoff = rng.uniform(-35, 35, B)
    ring_ph = rng.uniform(0, 2 * np.pi, B)
    ring_r = rng.uniform(205, 235, B)
    fork_wp = np.zeros(B, int)
    led = [False, False]
    vmax = rng.uniform(230, 290, B)
    jit = np.zeros((B, 3))
    ret = 60.5 + 6.0 * np.argsort(np.argsort(group * 10 + rng.uniform(0, 1, B))) / B
    ret_wp = np.zeros(B, int)
    STRAG = int(np.flatnonzero(group == 1)[B // 4])
    ret[STRAG] = 1e9
    size = rng.uniform(0.85, 1.15, B)
    size[STRAG] = 1.8
    strag_s0 = strag_d0 = strag_p0 = None

    log = []                         # every ping: (birth, origin, amp, tau, tint, kind, bat)
    pings = []

    def ping(o, tb, a, tau=0.45, c=0, kind='', who=-1):
        pings.append((o.copy(), tb, a, tau, c))
        log.append((tb, o.copy(), a, tau, c, kind, who))

    for tb, a in ((2.6, 0.35), (3.5, 0.45), (4.2, 0.6)):
        ping(attic, tb, a, 0.35, 0, 'chirp')
    ambient_next = 27.0
    moth_plan = [(37.0, 440), (42.5, 300), (47.5, 120), (49.0, 470), (54.0, 30), (63.0, 452), (68.0, 405)]
    moths = []
    track_p = np.zeros((F, B, 3))
    track_alive = np.zeros((F, B), bool)
    homed = np.full(B, np.nan)
    strag = dict(bat=STRAG)

    for f in range(F):
        t = f * DT
        alive |= (t >= rel) & ~home
        goal = np.zeros((B, 3))
        age = t - rel
        s_route = np.clip(age, 0, None) * 260 + 90
        route_goal = along(s_route)
        out_pt = np.array([-60.0, Y0, 40.0])
        past = s_route > G.pd[G.path][178]
        route_goal[past] = out_pt
        a_ang = ring_ph + 0.9 * t
        big = house_c + np.stack([760 * np.cos(a_ang), 0 * a_ang, 360 * np.sin(a_ang)], -1)
        cen = np.where(group[:, None] > 0.5, right_c, left_c)
        sgn = np.where(group > 0.5, -1.0, 1.0)
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
                    if fork_wp[i] == 3 and not led[g_]:
                        led[g_] = True
                        ping(pos[i], t, 1.0, 1.1, 1 + g_, 'lead', i)
                    if fork_wp[i] == 4:
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

        hunting = np.zeros(B, bool)
        slow = np.ones(B)
        for m in moths:
            if m['caught'] is None and m['hunter'] is not None:
                h = m['hunter']
                goal[h] = m['p'] + np.array([0, 4, 0])
                hunting[h] = True
                slow[h] = float(np.clip(np.linalg.norm(pos[h] - goal[h]) / 220, 0.3, 1))

        going = (t >= ret) & alive
        for i in np.flatnonzero(going):
            wps = (corner + np.array([0, 0, 90]), corner + np.array([0, 0, -60]), attic, inside)
            if ret_wp[i] < 3 and np.linalg.norm(pos[i, [0, 2]] - wps[ret_wp[i]][[0, 2]]) < 70:
                ret_wp[i] += 1
            goal[i] = wps[ret_wp[i]]
            goal[i, 1] = Y0 + 0.3 * yoff[i]
            vmax[i] = 330

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
            newb = age[idx] < DT * 1.5
            v[newb] = np.array([0, 0, 240.0])
            p = p + v * DT
            pos[idx], vel[idx] = p, v
            gone = going[idx] & (p[:, 2] < -690) & (np.abs(p[:, 0] + 596) < 90)
            if idx[gone].size:
                home[idx[gone]] = True
                alive[idx[gone]] = False
                homed[idx[gone]] = t

        if t >= 73.0 and alive[STRAG]:
            if strag_s0 is None:
                strag_s0 = t
                k = np.argmin(np.linalg.norm(pxz - pos[STRAG, [0, 2]], axis=1))
                strag_d0 = G.pd[k]
                strag_p0 = pos[STRAG].copy()
                strag.update(s0=t, d0=float(strag_d0))
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
                homed[STRAG] = t
                ping(attic, t + 0.9, 0.45, 0.3, 0, 'last')

        for (tm, pi) in moth_plan:
            if abs(t - tm) < DT / 2:
                mp = G.pos[G.path[pi]].copy()
                cand = np.flatnonzero(alive & (t < ret))
                if tm > 60:
                    cand = np.array([STRAG])
                h = int(cand[np.argmin(np.linalg.norm(pos[cand] - mp, axis=1))]) if cand.size else None
                moths.append(dict(p=mp, base=mp.copy(), born=t, hunter=h, next=t + 0.3, caught=None,
                                  ph=rng.uniform(0, 6, 3), pi=pi))
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
                ping(pos[h], t, amp, 0.2 + 0.3 * min(1, d / 400), 0, 'hunt', h)
                m.setdefault('pings', []).append((t, float(d), interval))
                m['next'] = t + interval
            if d < 22 and lt > 2.0 and t < 72.5:
                m['caught'] = t
                m['at'] = m['p'].copy()
        if t >= 72.0 and alive[STRAG] and (strag_s0 is None or t - strag_s0 < 5.0):
            if not pings or t - pings[-1][1] > 0.32:
                ping(pos[STRAG], t, 0.95, 0.4, 0, 'distress', STRAG)
        if abs(t - 57.6) < DT / 2:
            for i in np.flatnonzero(alive):
                ping(pos[i] + vel[i] * 0.6, t + rng.uniform(0.4, 1.6), 0.45, 0.6, 0, 'chorus', i)
        if abs(t - 60.0) < DT / 2:
            ping(corner + np.array([0, 30, 0]), t, 1.0, 1.6, 0, 'call')
            ping(corner + np.array([0, 30, 0]), t + 0.45, 0.7, 1.3, 0, 'call')
        if t >= ambient_next and t < 60 and alive.any():
            i = rng.choice(np.flatnonzero(alive))
            ping(pos[i], t, float(keys(t, [(27, 0.45), (38, 0.85), (60, 0.85)])), 0.9,
                 (1 + int(group[i])) if t < 36 else 0, 'ambient', int(i))
            ambient_next = t + float(keys(t, [(27, 1.8), (38, 1.1), (60, 1.1)])) * rng.uniform(0.6, 1.4)

        pings = [pg for pg in pings if t - pg[1] <= 6 * pg[3] + 0.3]
        track_p[f], track_alive[f] = pos, alive
    log.sort(key=lambda e: e[0])
    return dict(pings=log, rel=rel, homed=homed, moths=moths, pos=track_p, alive=track_alive,
                flap_f=flap_f, flap_p=flap_p, size=size, strag=strag)


# chords as (start time, name); the harmony follows the sky and the flock
HARMONY = [(0.0, 'Em9'), (12.0, 'Cmaj7'), (16.0, 'Am9'), (20.0, 'B7sus4'), (22.0, 'B7'), (25.9, 'Cmaj9#11'),
           (29.0, 'Em9'), (32.0, 'Cmaj7'), (36.0, 'Am9'), (40.0, 'Em'), (44.0, 'Cmaj7'), (48.0, 'Am9'),
           (51.0, 'F#m7b5'), (54.0, 'B7'), (56.0, 'Em'), (57.6, 'B7sus4'), (58.6, 'B7'), (60.0, 'E'),
           (62.5, 'A/E'), (65.0, 'C#m7'), (67.5, 'Badd11'), (70.0, 'E'), (72.0, 'Edim'), (77.3, ''),
           (78.2, 'Eadd9')]
CHORDS = {                                   # root (bass, MIDI) and the pitch classes above it
    'Em9': (40, [4, 7, 11, 2, 6]), 'Em': (40, [4, 7, 11]), 'Cmaj7': (36, [0, 4, 7, 11]),
    'Am9': (45, [9, 0, 4, 7, 11]), 'B7sus4': (47, [11, 4, 6, 9]), 'B7': (47, [11, 3, 6, 9]),
    'Cmaj9#11': (36, [0, 4, 7, 11, 2, 6]), 'F#m7b5': (42, [6, 9, 0, 4]), 'E': (40, [4, 8, 11]),
    'A/E': (40, [9, 1, 4]), 'C#m7': (37, [1, 4, 8, 11]), 'Badd11': (47, [11, 3, 6, 4]),
    'Edim': (40, [4, 5, 7, 10]), 'Eadd9': (40, [4, 8, 11, 6]), '': (40, []),
}
NIGHT_SONG = [(40.0, 'B3', 1.0), (41.0, 'E4', 1.5), (42.5, 'F#4', 0.5), (43.0, 'G4', 1.0), (44.0, 'E4', 2.0),
              (46.0, 'D4', 0.5), (46.5, 'C4', 0.5), (47.0, 'B3', 1.0), (48.0, 'A3', 1.5), (49.5, 'C4', 0.5),
              (50.0, 'E4', 1.0), (51.0, 'F#4', 1.5), (52.5, 'A4', 0.5), (53.0, 'G4', 1.0), (54.0, 'F#4', 1.0),
              (55.0, 'D#4', 1.0), (56.0, 'E4', 1.8)]
DAWN_SONG = [(60.0, 'B3', 0.45), (60.45, 'E4', 2.0), (62.5, 'C#4', 1.0), (63.5, 'E4', 0.5), (64.0, 'F#4', 1.0),
             (65.0, 'G#4', 1.5), (66.5, 'E4', 1.0), (67.5, 'F#4', 1.5), (69.0, 'D#4', 1.0), (70.0, 'E4', 2.0)]


def score(M, G):
    from pixelhome.audio import SR, note, whoosh
    n = note
    E = _colony(G)
    rng = M.rng
    harp = M.sampler('Strings/Harp/*.wav')
    vpizz = M.sampler('Strings/Solo Violin/Pizz/*.wav')
    cbpizz = M.sampler('Strings/Solo Contrabass/Pizz/*.wav', tune=-12)     # these sets are labelled an octave low
    horn = M.sampler('Brass/F Horn/sus/*.wav', tune=-12)
    clar = M.sampler('Woodwinds/Clarinet/susLong/*.wav', tune=-12)
    ctrem = M.sampler('Strings/Cello Section/trem/*.wav', tune=-12)
    vtrem = M.sampler('Strings/Solo Violin/Trem/*.wav', tune=-12)
    bdrum = M.hits('VSCO 1 Percussion/drums/bass/bdrum_muted_m*.wav')
    gong = M.hits('VSCO 1 Percussion/varMetal/Gong/gong_hit_p.wav')
    roll = M.hits('VSCO 1 Percussion/varMetal/Cymbals/susp/susp_hit_softmall_roll1.wav')

    for name, gain, rev in (('pad', 0.3, 0.35), ('bass', 0.4, 0.1), ('sonar', 0.3, 0.3), ('flutter', 0.16, 0.12),
                            ('harp', 0.36, 0.3), ('song', 0.26, 0.3), ('moth', 0.075, 0.35), ('strings', 0.42, 0.25),
                            ('perc', 0.5, 0.2)):
        M.bus(name, gain=gain, reverb=rev)

    x0, x1 = -596.0, 629.0

    def pan_x(x):                           # left/right across the facade, as seen from the street
        return float(0.85 * np.clip(2 * (x - x0) / (x1 - x0) - 1, -1, 1))

    def near(z):                            # louder toward the street
        return float(0.55 + 0.45 * np.clip((z + 640) / 500, 0, 1))

    def chord_at(t):
        name = [c for tc, c in HARMONY if tc <= t + 1e-6][-1]
        return CHORDS[name]

    def tone(t, u, lo=n('E5'), span=19):     # chord tone at height u (0..1) within [lo, lo+span]
        _, pcs = chord_at(t)
        pcs = pcs or [4]
        cand = [m for m in range(lo, lo + span + 1) if m % 12 in pcs]
        return cand[int(np.clip(u, 0, 0.999) * len(cand))]

    def hz(m):
        return 440.0 * 2 ** ((m - 69) / 12)

    def blip(m, amp, dec, sweep=1.5, bright=0.3):
        """A sonar call: a fast downward chirp that settles on a pitch and rings out."""
        f = hz(m)
        k = int((6 * dec + 0.04) * SR)
        t = np.arange(k) / SR
        fi = f * (1 + (sweep - 1) * np.exp(-t / 0.018))
        ph = 2 * np.pi * np.cumsum(fi) / SR
        env = (1 - np.exp(-t / 0.0015)) * np.exp(-t / dec)
        sig = amp * env * (np.sin(ph) + bright * np.sin(2 * ph) * np.exp(-t / 0.04))
        return np.vstack([sig, sig])

    def lowpass(sig, fc):
        a = np.exp(-2 * np.pi * fc / SR)
        out = np.zeros_like(sig)
        z = np.zeros(2)
        for i in range(sig.shape[1]):       # short signals only
            z = (1 - a) * sig[:, i] + a * z
            out[:, i] = z
        return out

    def env_at(pts, k, t0=0.0):             # keyframe envelope (the lights' own keys) at audio rate
        tc = np.arange(0, k / SR + 0.02, 0.01)
        v = np.array([keys(t0 + u, pts) for u in tc])
        return np.interp(np.arange(k) / SR, tc, v)

    ends = [G.pos[G.path[0]], G.pos[G.path[-1]]]

    def echoes(t, o, a, tau, m, dec):       # the wavefront reaching the two free ends while still visible
        for e in ends:
            r = float(np.linalg.norm(e - o))
            ag = r / V_PING
            vis = a * np.exp(-ag / tau) / (1 + r / 700)
            if vis > 0.06 and ag > 0.15:
                M.add('sonar', blip(m, 0.5 * vis, 0.8 * dec, 1.2, 0.0), t + ag, 1.0, pan_x(e[0]))

    # ---- the pad follows the sky: dusk, night and dawn are the lights' own keyframes
    def pad(patch, spans, pts, vel=70):
        notes = []
        for t0, t1 in spans:
            for tc, c in HARMONY:
                te = min(t1, next((u for u, _ in HARMONY if u > tc), D))
                if te <= t0 or tc >= t1 or not c:
                    continue
                root, pcs = CHORDS[c]
                ts = max(t0, tc)
                notes.append((ts, root, vel, te - ts + 0.05))
                for pc in pcs:
                    notes.append((ts, 52 + (pc - 52) % 12, vel - 6, te - ts + 0.05))
        sig = M.synth(patch).render(notes, D + 1)
        sig = sig * env_at(pts, sig.shape[1])
        M.add('pad', sig, 0.0)

    pad('Pads/MKS-70 Warm Pad', [(0.0, 40.0)], [(0, 0), (2.0, 1), (32, 1), (40, 0)], 72)
    pad('Pads/Ghost Pad', [(31.0, 66.0)], [(32, 0), (40, 1), (57.6, 1), (60, 0.7), (66, 0)], 66)
    pad('Polysynths/Juno-60 Strings', [(59.0, 72.0)], [(59, 0), (60.0, 0.6), (66, 0.8), (71.6, 0.8), (72.1, 0)], 70)
    pad('Pads/MKS-70 Warm Pad', [(78.2, D)], [(78.2, 0), (79.2, 0.8), (D, 0.8)], 64)

    # bass: a contrabass pizz on every chord change
    for tc, c in HARMONY:
        if c and tc not in (57.6, 58.6) and tc < 72:
            M.add('bass', cbpizz.play(CHORDS[c][0] - 12, 80 if 32 <= tc < 57 else 96), tc, 1.0, -0.1)

    # ---- 2.6, 3.5, 4.2: three chirps from inside the attic, rising, muffled by the roof
    for (tb, o, a, tau, c, kind, who), m in zip([e for e in E['pings'] if e[5] == 'chirp'], ('B5', 'D6', 'E6')):
        sig = lowpass(blip(n(m), a, 0.12, 1.6), 2500)
        M.add('sonar', sig, tb, 1.4, pan_x(o[0]))
        M.add('harp', harp.play(n(m) - 12, 70), tb, 0.6, pan_x(o[0]))

    # ---- 5-17.5: the colony pours out, one harp note per bat let go, climbing in waves
    pent = [0, 3, 5, 7, 10]                  # E minor pentatonic
    for i, tr in enumerate(np.sort(E['rel'])):
        m = n('E3') + pent[i % 5] + 12 * ((i // 5) % 3)
        M.add('harp', harp.play(m, 60 + min(50, i)), float(tr), 0.8, pan_x(-596) + 0.1 * (i % 2))

    # ---- the wings: every bat's wingbeat where it is, a leathery flutter
    cr = 400
    F = E['pos'].shape[0]
    tf = np.arange(F) * DT
    tc_ = np.arange(int(D * cr)) / cr
    envL = np.zeros_like(tc_)
    envR = np.zeros_like(tc_)
    for i in range(B):
        al = np.interp(tc_, tf, E['alive'][:, i].astype(float))
        if not al.any():
            continue
        x = np.interp(tc_, tf, E['pos'][:, i, 0])
        z = np.interp(tc_, tf, E['pos'][:, i, 2])
        sp = np.interp(tc_, tf[1:], np.linalg.norm(np.diff(E['pos'][:, i], axis=0), axis=1) / DT)
        ph = 2 * np.pi * E['flap_f'][i] * tc_ + E['flap_p'][i]
        beat = ((1 + np.cos(ph)) / 2) ** 6 * al * E['size'][i] ** 2 * (0.6 + 0.4 * np.clip(sp / 300, 0, 1.5))
        beat *= 0.55 + 0.45 * np.clip((z + 640) / 500, 0, 1)
        a_ = (0.85 * np.clip(2 * (x - x0) / (x1 - x0) - 1, -1, 1) + 1) * np.pi / 4
        envL += beat * np.cos(a_)
        envR += beat * np.sin(a_)
    count = np.interp(tc_, tf, E['alive'].sum(1))
    norm = (1 + count) ** -0.35             # more bats, more wings, but not 48 times louder
    k = int(D * SR)
    tt = np.arange(k) / SR
    noise = rng.normal(0, 1, (2, k))
    spec = np.fft.rfft(noise, axis=1)
    fr = np.fft.rfftfreq(k, 1 / SR)
    spec *= np.exp(-0.5 * (np.log(np.maximum(fr, 1) / 650) / 0.6) ** 2)    # a band around 650 Hz
    noise = np.fft.irfft(spec, k, axis=1)
    noise /= np.abs(noise).max()
    fl = np.vstack([noise[0] * np.interp(tt, tc_, envL * norm), noise[1] * np.interp(tt, tc_, envR * norm)])
    sky = [(0, 1), (32, 1), (40, 0.5), (57.6, 0.5), (60, 0.8), (66, 1), (D, 1)]   # shadows read against the sky
    M.add('flutter', fl * env_at(sky, k), 0.0)

    # ---- 12-26: the flock mills, funnels into the porch notch; low strings swell under it
    sw = []
    for tc, c in HARMONY:
        if 12 <= tc < 29:
            root, pcs = CHORDS[c]
            te = next(u for u, _ in HARMONY if u > tc)
            sw += [(tc, root + 12, 70, te - tc + 0.05), (tc, 52 + (pcs[1] - 52) % 12, 64, te - tc + 0.05)]
    strs = M.synth('Polysynths/Juno-60 Strings').render(sw, D + 1)
    M.add('strings', strs * env_at([(12, 0), (20, 0.7), (25.9, 1), (29, 0.4), (32, 0)], strs.shape[1]), 0.0)

    # ---- every ping is a sonar call, pitched from the chord that is sounding, placed where it is
    box = M.synth('Plucks/Magic Music Box')
    box_notes = []
    # each hunt ping's distance from hunter to moth, by (time, hunter)
    gap = {(round(q[0], 4), mo['hunter']): q[1] for mo in E['moths'] for q in mo.get('pings', [])}
    for tb, o, a, tau, c, kind, who in E['pings']:
        u = (o[1] - (Y0 - 47)) / 94           # height within the flock
        p, g = pan_x(o[0]), near(o[2])
        if kind == 'lead':                     # the two ring leaders call the colony's motif, lime then violet
            mot = ('E5', 'B5', 'F#6') if c == 1 else ('C6', 'G5', 'E6')
            for j, m in enumerate(mot):
                M.add('sonar', blip(n(m), 0.9, 0.3, 1.4), tb + 0.11 * j, g, p)
                box_notes.append((tb + 0.11 * j, n(m) - 12, 100, 0.5))
            echoes(tb, o, a, tau, n(mot[-1]), 0.3)
        elif kind == 'ambient':
            m = tone(tb, u)
            M.add('sonar', blip(m, 0.8 * a, 0.16, 1.5), tb, g, p)
            if c:                              # the tinted calls of the rings ring on the music box
                box_notes.append((tb, m - 12, 80, 0.4))
            echoes(tb, o, a, tau, m, 0.16)
        elif kind == 'hunt':                   # climbing as it closes in, a buzz at the end
            d = gap[(round(tb, 4), who)]
            m = tone(tb, 1 - min(d, 330) / 330, n('B4'), 26)
            M.add('sonar', blip(m, 0.32 * a + 0.1, 0.03 + 0.08 * min(1, d / 330), 1.3, 0.5), tb, g, p)
        elif kind == 'chorus':                 # everyone at once: a cloud of B7
            M.add('sonar', blip(tone(tb, u, n('B4'), 24), 0.6, 0.2, 1.5), tb, g, p)
        elif kind == 'call':                   # the call home, from the corner: horn below it
            m = n('B5') if tb < 60.2 else n('E6')
            M.add('sonar', blip(m, a, 0.45, 1.6), tb, g, p)
            echoes(tb, o, a, tau, m, 0.45)
        elif kind == 'distress':               # the straggler: a harsh, falling alarm on a minor second
            j = sum(1 for e in E['pings'] if e[5] == 'distress' and e[0] < tb)
            m = n('F6') if j % 2 == 0 else n('E6')
            M.add('sonar', blip(m, 1.2, 0.09, 2.4, 0.6), tb, g, p)
            M.add('sonar', blip(m - 12, 0.5, 0.09, 2.4, 0.6), tb, g, p)
        elif kind == 'last':                   # one last chirp, from inside
            M.add('sonar', lowpass(blip(n('E6'), 0.5, 0.2, 1.4), 2200), tb, 1.2, p)
    M.add('sonar', box.render(box_notes, D + 1), 0.0, 0.5)

    # ---- moths: an amber glint that flickers as the light does (9 Hz), then the pop
    for mo in E['moths']:
        t0 = mo['born']
        t1 = mo['caught'] if mo['caught'] is not None else 74.0
        k = int((t1 - t0 + 0.05) * SR)
        tt = np.arange(k) / SR
        f = hz(tone(t0, 0.5 + 0.1 * (mo['pi'] % 5), n('E6'), 12))
        g = np.clip(tt / 0.8, 0, 1) ** 2
        if mo['caught'] is None:
            g = g * (1 - np.clip((t0 + tt - 73) / 1.0, 0, 1))
        flick = 0.75 + 0.25 * np.sin(2 * np.pi * 9 * (t0 + tt) + mo['ph'][2])
        ph = 2 * np.pi * f * tt + 0.004 * f * np.sin(2 * np.pi * 5.3 * tt) / 5.3
        sig = 0.75 * g * flick * (np.sin(ph) + 0.35 * np.sin(2.01 * ph))
        sig[-int(0.03 * SR):] *= np.linspace(1, 0, int(0.03 * SR))
        x = G.pos[G.path[mo['pi']], 0]
        M.add('moth', np.vstack([sig, sig]), t0, 1.0, pan_x(x))
        if mo['caught'] is not None:
            tcat, at = mo['caught'], mo['at']
            kp = int(0.12 * SR)
            tp = np.arange(kp) / SR
            pop = np.sin(2 * np.pi * np.cumsum(250 + 1400 * (1 - np.exp(-tp / 0.012))) / SR) * np.exp(-tp / 0.025)
            M.add('perc', np.vstack([pop, pop]) * 1.3, tcat, 1.0, pan_x(at[0]))
            root = tone(tcat, 0.0, n('E5'), 12)
            for j in range(4):                # the pop's glow spreads both ways
                M.add('harp', harp.play(tone(tcat, j / 4, root, 14), 96 - 10 * j), tcat + 0.07 * j, 0.8,
                      float(np.clip(pan_x(at[0]) + (0.12 * (j + 1)) * (-1) ** j, -0.9, 0.9)))

    # ---- night 40-57: a clarinet song low in the dark; dawn 60-72: the horn takes it home in E major
    for t, m, d in NIGHT_SONG:
        M.add('song', clar.play(n(m), 80, dur=d + 0.15, release=0.3), t, 0.5, -0.15)
    for t, m, d in DAWN_SONG:
        first = t < 61                       # the call home comes from the corner, the rest from the middle
        M.add('song', horn.play(n(m), 92 if first else 82, dur=d + 0.15, release=0.35), t, 0.8,
              -0.45 if first else -0.1)
    roll_sig = roll.play(90, dur=2.6)
    roll_sig = roll_sig * np.linspace(0, 1, roll_sig.shape[1]) ** 2
    M.add('perc', roll_sig, 57.6, 1.0, -0.3)                  # the chorus swells into the call home
    M.add('perc', gong.play(80), 60.0, 0.5, pan_x(-596))

    # ---- 64-70: the colony goes in, one falling harp note per bat through the attic
    epent = [0, 2, 4, 7, 9]                  # E major pentatonic
    homed = np.sort(E['homed'][np.isfinite(E['homed'])])[:-1]   # the last one in is the straggler
    for i, th in enumerate(homed):
        m = n('E6') - (12 * (i // 5) + [0, 3, 5, 8, 10][i % 5]) % 36
        M.add('harp', harp.play(m, 70), float(th), 0.55, pan_x(-596))

    # ---- 72-77.3: the straggler panics and races home: tremolo dissonance, a pizzicato run that
    # follows it along the roof (a note every 60 units of path, so it accelerates with the bat),
    # a thump at every corner it rounds
    s0, d0 = E['strag']['s0'], E['strag']['d0']
    t_in = float(E['homed'][E['strag']['bat']])
    panic = [(ctrem, 'E2', 0.0), (ctrem, 'A#2', 0.0), (vtrem, 'F5', 0.0), (vtrem, 'E5', 1.0)]
    for ins, m, dt in panic:
        sig = ins.play(n(m), 100, dur=t_in - 72.0 - dt, release=0.08)
        sig = sig * env_at([(0, 0.25), (t_in - 72.0 - dt, 1.0)], sig.shape[1])
        M.add('strings', sig, 72.0 + dt, 1.8, 0.0)

    def t_at(sd):                            # when the straggler is at path distance sd
        tau = (-240 + np.sqrt(240 ** 2 + 4 * 70 * (d0 - sd))) / (2 * 70)
        return s0 + tau
    hm = [0, 2, 3, 5, 7, 8, 11]              # E harmonic minor, the run falls toward the attic
    pd_path = G.pd[G.path]
    for j, sd in enumerate(np.arange(d0 - 30, 0, -60)):
        t = float(t_at(sd))
        deg = int(sd / 95)
        m = n('E3') + 12 * (deg // 7) + hm[deg % 7] + (2 if j % 2 else 0)
        x = float(np.interp(sd, pd_path, G.pos[G.path, 0]))
        M.add('harp', vpizz.play(m, 105), t, 0.9, pan_x(x))
    for ci in (380, 331, 260, 178, 80):
        sd = 0.5 * (pd_path[ci] + pd_path[ci + 1])
        if sd < d0:
            t = float(t_at(sd))
            x = float(G.pos[G.path[ci], 0])
            M.add('bass', cbpizz.play(n('E1'), 120), t, 1.0, pan_x(x))
            M.add('perc', bdrum.play(110), t, 0.8, pan_x(x))
    t_end = float(t_at(0))
    M.add('perc', whoosh(t_in - t_end + 0.3, 2500, 300, 0.5, seed=5), t_end - 0.15, 0.8, pan_x(-596))
    M.add('perc', lowpass(bdrum.play(118)[:, :int(0.8 * SR)], 900), t_in, 1.6, pan_x(-596))
    M.add('perc', gong.play(60), t_in, 0.35, pan_x(-596))

    # ---- 78.2: after the last chirp, a slow E major add9 on the harp
    for j, m in enumerate(('E3', 'B3', 'G#4', 'F#5', 'B5')):
        M.add('harp', harp.play(n(m), 70 - 4 * j), 78.5 + 0.28 * j, 0.7, -0.3 + 0.15 * j)
