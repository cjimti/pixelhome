"""It's Alive: the house is a mad scientist's lab. The five roof corners are coils that charge up one
at a time, each in its own way (a smooth ramp, a ratchet, a pump, a stutter, a slow deep build).
Arcs crawl between charged corners as stepped leaders, connect in a return stroke, fork round the
next corner and leave a violet afterglow. A ladder arc climbs the two porch rails away from the
street and snaps across the porch front. Outside, a storm: each strike reaches the pixels nearest
the street first. Everything charges together, the lab goes silent, and one huge strike brings "it"
to life on the porch. It twitches, then lurches toward the street and along the right wing in
heavy, uneven steps (one long lunge, one dragged foot) whose thuds ripple through the roof in 3-D.
At the free end it grabs the last wire, blows the fuse in a spray of sparks, the house goes dark,
and the lab hum flickers back on. Something twitches at the end of the wire."""
import numpy as np
from pixelhome.fx import DT, hexc, light, smoothstep, keys, lerp, Flicker, nframes

CODE = 'HW02'
TITLE = "It's Alive"
KIND = 'show'
DESCRIPTION = ('The corners are coils in a mad lab: they charge, arcs leap between them and a storm rolls '
               'in until one huge strike brings something to life, and it lurches across the roof and blows the fuse.')

VIOLET = hexc('#4818ff')
COIL = hexc('#3a8cff')
CORE = hexc('#e8f2ff')
ARC = hexc('#c4d6ff')
GLOW = hexc('#7a2cff')
STORM = hexc('#dfe8ff')
GREEN = hexc('#4cff28')
PALE = hexc('#c8ffb0')
SPARK = hexc('#ffb028')
FUSE = hexc('#ff6a10')

D = 79.0
T_STRIKE = 50.0
T_ALIVE = 52.3
T_WALK = 54.6
T_HUM = 71.0


def _coil_build(style, u):
    """Charge 0..1 of one coil `u` seconds after it starts; each coil builds in its own way."""
    if u <= 0:
        return 0.0
    if style == 0:                                        # smooth ramp
        return float(smoothstep(0, 4, u))
    if style == 1:                                        # ratchet: five clicks, each with a kick
        v = sum(0.2 * float(smoothstep(c, c + 0.06, u)) for c in (0, .8, 1.6, 2.4, 3.2))
        kick = sum(0.35 * np.exp(-(u - c) / 0.09) for c in (0, .8, 1.6, 2.4, 3.2) if u >= c)
        return v + kick
    if style == 2:                                        # pump: surges that settle
        s = float(smoothstep(0, 4.5, u))
        return s * (1 + 0.35 * (1 - float(smoothstep(4, 7, u))) * np.sin(2 * np.pi * 1.4 * u))
    if style == 3:                                        # stutter: climbs, fails, sputters, catches
        v = float(keys(u, [(0, 0), (1.4, 0.55), (1.5, 0.04), (2.7, 0.04), (3.6, 1.0)]))
        if 1.5 < u < 2.7:
            v += 0.3 * (np.sin(u * 61) > 0.6) * (np.sin(u * 23) > 0)
        return v
    return float(smoothstep(0, 5.5, u)) ** 2 * (1 + 0.12 * np.sin(2 * np.pi * 0.5 * u))   # slow, deep


class _Arc:
    """A stepped leader that crawls from sa to sb along the roof (distance units), then a return stroke."""

    def __init__(self, rng, t0, sa, sb, strength=1.0, fizzle=None, forks=()):
        self.t0, self.sa, self.sb, self.k = t0, sa, sb, strength
        self.L = abs(sb - sa)
        self.dir = 1.0 if sb >= sa else -1.0
        stop = self.L * (fizzle if fizzle else 1.0)
        ts, hs, t, h = [0.0], [0.0], 0.0, 0.0
        while h < stop:
            t += rng.choice([1, 1, 1, 2, 3]) * DT
            h = min(stop, h + rng.uniform(14, 55))
            ts.append(t)
            hs.append(h)
        self.ts, self.hs = np.array(ts), np.array(hs)
        self.tc = t0 + ts[-1]
        self.fizzle = fizzle
        self.forks = forks                                  # (from distance, direction, length)
        self.end = self.tc + 2.5

    def draw(self, t, pd, tex, hot, glow):
        if t < self.t0 or t > self.end:
            return None
        p = (pd - self.sa) * self.dir                       # progress along the arc
        on = (p >= -2) & (p <= self.L + 2)
        if t < self.tc:                                     # leader crawling
            head = np.interp(t - self.t0, self.ts, self.hs)
            seg = on & (p <= head)
            hot += self.k * (0.28 * tex * seg + 0.9 * np.exp(-((p - head) / 9) ** 2) * on)
            return None
        tt = t - self.tc
        if self.fizzle:                                     # leader dies where it stalled
            head = self.hs[-1]
            seg = on & (p <= head)
            hot += self.k * np.exp(-tt / 0.12) * (0.3 * tex * seg + 0.8 * np.exp(-((p - head) / 12) ** 2))
            glow += self.k * 0.18 * np.exp(-tt / 0.35) * seg
            return None
        env = np.exp(-tt / 0.05) + 0.7 * np.exp(-max(0, tt - 0.11) / 0.05) * (tt > 0.11) \
            + 0.45 * np.exp(-max(0, tt - 0.24) / 0.06) * (tt > 0.24)
        ch = on.astype(float)
        for s0, d, ln in self.forks:                        # forks spill round the next corner
            q = (pd - s0) * d
            ch = np.maximum(ch, ((q >= 0) & (q <= ln)) * np.clip(1 - q / ln, 0, 1) ** 0.7 * 0.8)
        hot += self.k * min(env, 1.2) * ch * (0.55 + 0.45 * tex)
        glow += self.k * 0.42 * np.exp(-tt / 0.55) * ch
        return tt


def render(G, seed=2):
    rng = np.random.default_rng(seed)
    n = G.N
    F = nframes(D)
    out = np.zeros((F, n, 3))
    P = G.pos
    pd = G.pd
    ppd = G.pd[G.path]
    end_pd = ppd[-1]
    z = P[:, 2]

    # ---- coils at the five corners, in charge order
    corner_pi = {80: (80, 81), 178: (178, 179), 260: (260, 261), 331: (331, 332), 380: (380, 381)}
    order = [(80, 0, 2.0), (380, 1, 4.5), (178, 2, 7.0), (331, 3, 9.5), (260, 4, 12.0)]
    cs = {c: (ppd[a] + ppd[b]) / 2 for c, (a, b) in corner_pi.items()}
    cdist = {c: np.abs(pd - s) for c, s in cs.items()}
    dip = {c: 0.0 for c in cs}
    hum_ph = {c: 0.0 for c in cs}

    # ---- arcs between corners (and out to the free ends)
    adj = [(80, 178), (178, 260), (260, 331), (331, 380)]
    arcs = []

    def add_arc(t0, a, b, k=1.0, fizzle=None):
        sa = cs[a] if a in cs else a
        sb = cs[b] if b in cs else b
        d = 1.0 if sb >= sa else -1.0
        forks = []
        if rng.random() < 0.7:                              # overshoot past the target corner
            forks.append((sb, d, rng.uniform(30, 90)))
        if rng.random() < 0.5:                              # and a back-spill behind the source
            forks.append((sa, -d, rng.uniform(20, 60)))
        arcs.append(_Arc(rng, t0, sa, sb, k, fizzle, forks))
        return arcs[-1]

    add_arc(8.6, 80, 178, 0.7, fizzle=0.35)                 # first try: not enough charge
    add_arc(10.4, 80, 178, 0.8, fizzle=0.7)
    add_arc(12.2, 80, 178, 1.0)                             # first real arc
    add_arc(14.6, 178, 260, 1.0)
    add_arc(16.3, 380, 331, 1.0)
    add_arc(17.8, 260, 331, 1.0)
    add_arc(19.0, 80, 0.0, 0.9)                             # off the back of the Side
    t = 20.2
    while t < 39.5:
        r = rng.random()
        if r < 0.15:
            add_arc(t, 380, end_pd, 0.9)                    # out along the right wing to the free end
        elif r < 0.25:
            add_arc(t, 80, 0.0, 0.9)
        else:
            a, b = adj[rng.integers(len(adj))]
            if rng.random() < 0.5:
                a, b = b, a
            add_arc(t, a, b, rng.uniform(0.8, 1.0))
        t += rng.uniform(1.1, 2.3)
    while t < 49.2:                                         # everything charging together
        a, b = adj[rng.integers(len(adj))]
        if rng.random() < 0.5:
            a, b = b, a
        add_arc(t, a, b, rng.uniform(0.6, 0.9))
        t += lerp(0.7, 0.28, (t - 39.5) / 10)

    # ---- ladder arc up the porch rails (away from the street), snapping across the porch front
    rails = np.concatenate([G.seg['Porch Left'], G.seg['Porch Right']])
    rail = np.zeros(n, bool)
    rail[rails] = True
    pf = G.seg['Porch Front']
    pfm = np.zeros(n, bool)
    pfm[pf] = True
    z_lo, z_hi = -205.0, -560.0
    ladders = [(20.5, 2.4), (24.2, 2.2), (28.0, 2.0), (31.6, 2.0), (35.2, 1.8),
               (41.0, 1.6), (43.0, 1.4), (44.8, 1.2), (46.4, 1.0), (47.7, 0.9)]

    # ---- storm strikes from the street side
    xz = P[:, [0, 2]]
    strikes = [(25.6, rng.uniform(-500, -200), 0.8), (31.0, rng.uniform(250, 550), 0.85),
               (36.8, rng.uniform(-200, 200), 0.9), (41.8, rng.uniform(-550, -250), 0.9),
               (45.9, rng.uniform(250, 550), 0.95)]
    strike_d = []
    for t0, sx, pk in strikes:
        d = np.hypot(xz[:, 0] - sx, xz[:, 1] - 450)
        strike_d.append((d - d.min()) / 1100)               # arrival delay; nearest pixels first
    big_d = np.hypot(xz[:, 0] - 16, xz[:, 1] - 700)
    big_delay = (big_d - big_d.min()) / 1500

    # ---- the creature's walk: from the porch front, down Porch Right, along Right to the free end
    s0 = (ppd[261] + ppd[331]) / 2
    s_end = end_pd - 18
    steps = []                                              # (start, duration, length, kind)
    tt = T_WALK
    pattern = ['lunge', 'drag', 'lunge', 'drag', 'lunge', 'drag', 'stumble', 'back', 'drag',
               'lunge', 'drag', 'lunge', 'drag', 'lunge', 'drag']
    raw = {'lunge': 1.0, 'drag': 0.45, 'stumble': 1.25, 'back': -0.25}
    lens = np.array([raw[k] * rng.uniform(0.9, 1.1) for k in pattern])
    lens *= (s_end - s0) / lens.sum()
    for k, ln in zip(pattern, lens):
        dur = {'lunge': 0.38, 'drag': 0.75, 'stumble': 0.42, 'back': 0.3}[k] * rng.uniform(0.9, 1.1)
        steps.append((tt, dur, ln, k))
        tt += dur + {'lunge': 0.28, 'drag': 0.38, 'stumble': 0.15, 'back': 0.75}[k] * rng.uniform(0.85, 1.2)
    T_GRAB = tt + 0.2
    T_FUSE = T_GRAB + 0.9
    thuds = []                                              # (time, node)
    sb_at = s0
    for st, dur, ln, k in steps:
        sb_at += ln
        if k != 'back':
            thuds.append((st + dur, int(np.argmin(np.abs(pd - sb_at))), 1.0 if k in ('lunge', 'stumble') else 0.55))

    def body_pos(t):
        s = s0
        for st, dur, ln, k in steps:
            if t <= st:
                break
            u = min(1.0, (t - st) / dur)
            if k in ('lunge', 'stumble'):
                e = 1 - (1 - u) ** 3                         # heavy throw forward, then settle
            elif k == 'drag':
                e = u * u * (3 - 2 * u)
            else:
                e = np.sin(u * np.pi / 2)
            s += ln * e
        return s

    def stepping(t):
        for st, dur, ln, k in steps:
            if st <= t < st + dur:
                return k
        return None

    # fuse sparks: (pd, velocity, life)
    sp_n = 70
    sp_v = -rng.uniform(150, 900, sp_n)
    sp_life = rng.uniform(0.4, 1.4, sp_n)
    sp_t = T_FUSE + rng.uniform(0, 0.25, sp_n)

    bed_fl = Flicker(rng, n, 0.08, 0.4)
    spark = np.zeros(n)
    trail = np.zeros(n)
    foot = np.zeros(n)
    glow_mem = np.zeros(n)
    tex = rng.uniform(0, 1, n)

    for f in range(F):
        t = f * DT
        if f % 2 == 0:
            tex = rng.uniform(0, 1, n) ** 1.5
        hot = np.zeros(n)
        glow = np.zeros(n)
        buf = np.zeros((n, 3))

        # lab hum bed: low violet, sags on thuds, gone while the creature has the power
        bedI = keys(t, [(0, 0), (2.5, 0.1), (40, 0.11), (48.5, 0.18), (49.4, 0.16), (49.85, 0.0),
                        (T_ALIVE, 0.0), (T_WALK, 0.07), (T_FUSE, 0.07), (T_FUSE + 0.05, 0.0),
                        (T_HUM + 1.2, 0.0), (T_HUM + 3.5, 0.1), (D - 2, 0.1), (D, 0)])
        sag = 1.0
        for th, node, w in thuds:
            if t >= th:
                sag *= 1 - 0.75 * w * np.exp(-(t - th) / 0.14)
        buf += light(VIOLET, bedI * sag * (1 + 0.12 * bed_fl(t)))

        # coils
        glob = keys(t, [(0, 0.55), (39.5, 0.55), (47.5, 1.0), (49.4, 1.0), (49.85, 0.0)]) if t < T_STRIKE else 0.0
        if t > T_HUM:                                       # the lab comes back, one tube at a time
            rec = keys(t, [(T_HUM, 0), (T_HUM + 3, 0.3), (D - 2, 0.3), (D, 0)])
            u = t - T_HUM
            stut = 1.0 if u > 2.4 else float((np.sin(u * 37) > 0.2) * (u > 0.4) * (np.sin(u * 11) > -0.3))
            glob = rec * stut
        for c, style, t0 in order:
            u = t - t0
            if t > T_HUM:
                u = 10.0
            L = max(0.0, _coil_build(style, u) * glob - dip[c])
            dip[c] *= np.exp(-DT / 0.7)
            if L <= 0.002:
                continue
            d = cdist[c]
            r = 22 + 60 * L
            f_hum = 0.5 + 2.8 * L
            hum_ph[c] += f_hum * DT
            ripple = 0.5 + 0.5 * np.cos(2 * np.pi * (hum_ph[c] - d / 70))
            I = L * (0.75 * np.exp(-(d / r) ** 2) + 0.35 * L * np.exp(-d / (2.2 * r)) * ripple)
            core = np.exp(-(d / 10) ** 2) * min(1.0, L)
            buf += light(COIL, I) + light(CORE, 0.7 * core * L)
            hit = rng.random(n) < 0.05 * L * L * np.exp(-d / r)
            spark[hit] = np.maximum(spark[hit], rng.uniform(0.4, 0.9, hit.sum()))

        # arcs
        for a in arcs:
            r_tt = a.draw(t, pd, tex, hot, glow)
            if r_tt is not None and r_tt < DT * 0.99:       # stroke connects: both coils discharge
                for c, s in cs.items():
                    if abs(s - a.sa) < 1 or abs(s - a.sb) < 1:
                        dip[c] += 0.4

        # ladder
        for t0, dur in ladders:
            lt = t - t0
            if lt < 0 or lt > dur + 0.55:
                continue
            u = min(1.0, lt / dur)
            zc = lerp(z_lo, z_hi, u ** 1.7)
            w = 10 + 22 * u
            jit = rng.uniform(0.75, 1.0)
            if lt <= dur:
                hot += rail * jit * 0.85 * np.exp(-((z - zc) / w) ** 2)
                glow += rail * 0.2 * np.exp(-np.clip(z - zc, 0, None) / 60) * ((z >= zc) & (z <= z_lo + 10))
            else:                                           # stretched across the porch front, then snaps
                tt = lt - dur
                k = (1 - smoothstep(0.3, 0.42, tt)) * (0.6 + 0.4 * jit)
                hot += pfm * k * (0.45 + 0.55 * tex) + rail * k * 0.6 * np.exp(-((z - z_hi) / w) ** 2)
                if 0.36 < tt < 0.42:                        # snap
                    hot += 0.9 * np.exp(-((pd - (ppd[261] + ppd[331]) / 2) / 40) ** 2)
                glow += pfm * 0.3 * np.exp(-tt / 0.4)

        # storm
        storm = np.zeros(n)
        for (t0, sx, pk), dl in zip(strikes, strike_d):
            lt = t - t0
            if -1.4 < lt < -1.1:                            # far-off flicker first, front edge only
                storm += 0.12 * np.exp(-dl * 8) * (np.sin(lt * 90) > 0)
            if lt < 0 or lt > 2.2:
                continue
            q = lt - dl
            env = (q > 0) * np.exp(-np.clip(q, 0, None) / 0.15) \
                + 0.8 * (q > 0.2) * np.exp(-np.clip(q - 0.2, 0, None) / 0.08) \
                + 0.45 * (q > 0.42) * np.exp(-np.clip(q - 0.42, 0, None) / 0.14)
            storm += pk * env * np.exp(-dl * 1.2)
            if 0.2 < lt < 0.2 + DT:                         # the strike feeds the coils
                for c in cs:
                    dip[c] -= 0.25
        buf += light(STORM, storm)

        # the big strike
        bt = t - T_STRIKE
        if 0 <= bt < 2.0:
            q = bt - big_delay
            env = (q > 0) * (np.minimum(1, np.clip(q, 0, None) / 0.03)
                             * np.exp(-np.clip(q - 0.18, 0, None) / 0.22))
            buf += light(STORM, 1.05 * env)
            over = np.zeros(n)
            for c in cs:                                    # every coil overloads, then dies
                over += np.exp(-(cdist[c] / 70) ** 2)
            buf += light(COIL, np.clip(over, 0, 1) * 0.9 * np.exp(-max(0, bt - 0.3) / 0.35) * (bt > 0.25))

        # it's alive
        if T_ALIVE <= t < T_FUSE + 0.7:
            sb = body_pos(t)
            db = pd - sb
            twitch = sum(np.exp(-(t - tw) / 0.12) * (t >= tw) for tw in (T_ALIVE, T_ALIVE + 0.75, T_ALIVE + 1.35))
            idle = float(smoothstep(T_ALIVE, T_WALK, t))
            k = stepping(t)
            lean = 1.0 if k in ('lunge', 'stumble') else 0.0
            width = 38 + 14 * lean
            bodyI = (0.35 + 0.35 * idle + 0.8 * twitch) * np.exp(-((db - 8 * lean) / width) ** 2)
            for th, node, w in thuds:                       # a thud: the body flares, the roof rings
                tt = t - th
                if 0 <= tt < 1.6:
                    bodyI = bodyI * (1 + 0.8 * w * np.exp(-tt / 0.1))
                    r3 = np.linalg.norm(P - P[node], axis=1)
                    ring = np.exp(-((r3 - 650 * tt) / (22 + 40 * tt)) ** 2) * np.exp(-tt / 0.45)
                    buf += light(GREEN, 0.65 * w * ring)
                    if tt < DT:                             # and leaves a footprint
                        foot[:] = np.maximum(foot, 0.5 * w * np.exp(-((pd - pd[node]) / 10) ** 2))
            if k == 'drag':
                trail = np.maximum(trail, 0.55 * np.exp(-(db / 18) ** 2) * (db < 0))
            hit = rng.random(n) < 0.08 * np.exp(-np.abs(db) / 30) * (0.4 + twitch)
            spark[hit] = np.maximum(spark[hit], rng.uniform(0.4, 0.8, hit.sum()))
            if t >= T_GRAB:                                 # reaches for the last wire
                gt = t - T_GRAB
                hot += 0.8 * (0.5 + 0.5 * tex) * ((pd > sb) * (pd <= end_pd)) * min(1, gt / 0.2)
            bodyI = bodyI * (1 + 0.15 * np.sin(t * 2 * np.pi * 3.1))
            if t >= T_FUSE:                                 # brown-out flicker, then gone
                ft = t - T_FUSE
                fl = float(keys(ft, [(0, 1), (0.08, 0.15), (0.16, 0.9), (0.26, 0.1), (0.38, 0.6), (0.5, 0.0)]))
                bodyI = bodyI * fl
                hot *= fl
            buf += light(GREEN, bodyI) + light(PALE, 0.8 * bodyI ** 2)
        trail *= 0.975
        foot *= np.exp(-DT / 2.2)
        if T_FUSE <= t:
            foot *= 0.85
        buf += light(GREEN, np.maximum(trail, foot))

        # fuse pop and sparks
        if T_FUSE <= t < T_FUSE + 2:
            ft = t - T_FUSE
            buf += light(FUSE, 1.1 * np.exp(-ft / 0.12) * np.exp(-((end_pd - pd) / 25) ** 2))
            age = t - sp_t
            live = (age >= 0) & (age < sp_life)
            if live.any():
                sp = end_pd + sp_v[live] * age[live] * (1 - 0.45 * age[live] / sp_life[live])
                br = (1 - age[live] / sp_life[live]) ** 1.5
                acc = np.zeros(n)
                for s, b in zip(sp, br):
                    acc += b * np.exp(-((pd - s) / 5) ** 2)
                buf += light(SPARK, np.clip(acc, 0, 1.1))

        # one last twitch at the end of the wire
        if t > D - 3.2:
            lt = t - (D - 3.2)
            tw = sum(np.exp(-(lt - a) / 0.1) * (lt >= a) for a in (0.0, 0.5))
            buf += light(GREEN, 0.75 * tw * np.exp(-((end_pd - pd) / 22) ** 2))

        spark *= 0.5
        glow_mem = np.maximum(glow_mem * np.exp(-DT / 0.5), glow)
        buf += light(ARC, np.clip(hot, 0, 1.15)) + light(GLOW, np.clip(glow_mem, 0, 0.6))
        buf += light(CORE, spark)
        out[f] = buf
    return np.clip(out, 0, 1)
