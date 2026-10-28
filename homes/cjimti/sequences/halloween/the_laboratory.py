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
VOICEOVER = 'Thunder on the hill, and the coils are humming. Tonight the doctor tries again... to bring something to life.'

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


# ---- soundtrack ---------------------------------------------------------------------------------------
# C minor, 96 BPM (a bar is 2.5 s: the coils start one bar apart, so the score's grid starts at 2.0 s).
# The lab is its own band: each coil is a hum voice of the C minor chord that glides up as it charges and
# sags when an arc discharges it (computed from _coil_build and the same dips the lights use), every
# leader step crackles where it is on the roof, return strokes zap three times like the light does,
# Jacob's ladders buzz upward and snap, and thunder rolls in behind each strike from the side it fell on.
# A pipe organ plays the doctor's chorale over the coils and races up with the final charge; the lab
# drops dead for the giant strike; the creature walks on timpani (lunges) and scraping chains (drags)
# with the organ pedal stamping under each thud; the fuse pops in a hail of sparks and the organ browns
# out with the lights; the hum stutters back on alone, and the last twitch gets an unresolved note.

def _plan(G, seed=2):
    """The timed events of render(), drawn from the same seed in the same order (render is left untouched;
    score() needs its arcs, ladders, strikes, steps and fuse to land the sound on the light)."""
    rng = np.random.default_rng(seed)
    ppd = G.pd[G.path]
    end_pd = ppd[-1]
    corner_pi = {80: (80, 81), 178: (178, 179), 260: (260, 261), 331: (331, 332), 380: (380, 381)}
    cs = {c: (ppd[a] + ppd[b]) / 2 for c, (a, b) in corner_pi.items()}
    adj = [(80, 178), (178, 260), (260, 331), (331, 380)]
    arcs = []

    def add_arc(t0, a, b, k=1.0, fizzle=None):
        sa = cs[a] if a in cs else a
        sb = cs[b] if b in cs else b
        d = 1.0 if sb >= sa else -1.0
        forks = []
        if rng.random() < 0.7:
            forks.append((sb, d, rng.uniform(30, 90)))
        if rng.random() < 0.5:
            forks.append((sa, -d, rng.uniform(20, 60)))
        arcs.append(_Arc(rng, t0, sa, sb, k, fizzle, forks))

    add_arc(8.6, 80, 178, 0.7, fizzle=0.35)
    add_arc(10.4, 80, 178, 0.8, fizzle=0.7)
    add_arc(12.2, 80, 178, 1.0)
    add_arc(14.6, 178, 260, 1.0)
    add_arc(16.3, 380, 331, 1.0)
    add_arc(17.8, 260, 331, 1.0)
    add_arc(19.0, 80, 0.0, 0.9)
    t = 20.2
    while t < 39.5:
        r = rng.random()
        if r < 0.15:
            add_arc(t, 380, end_pd, 0.9)
        elif r < 0.25:
            add_arc(t, 80, 0.0, 0.9)
        else:
            a, b = adj[rng.integers(len(adj))]
            if rng.random() < 0.5:
                a, b = b, a
            add_arc(t, a, b, rng.uniform(0.8, 1.0))
        t += rng.uniform(1.1, 2.3)
    while t < 49.2:
        a, b = adj[rng.integers(len(adj))]
        if rng.random() < 0.5:
            a, b = b, a
        add_arc(t, a, b, rng.uniform(0.6, 0.9))
        t += lerp(0.7, 0.28, (t - 39.5) / 10)
    ladders = [(20.5, 2.4), (24.2, 2.2), (28.0, 2.0), (31.6, 2.0), (35.2, 1.8),
               (41.0, 1.6), (43.0, 1.4), (44.8, 1.2), (46.4, 1.0), (47.7, 0.9)]
    strikes = [(25.6, rng.uniform(-500, -200), 0.8), (31.0, rng.uniform(250, 550), 0.85),
               (36.8, rng.uniform(-200, 200), 0.9), (41.8, rng.uniform(-550, -250), 0.9),
               (45.9, rng.uniform(250, 550), 0.95)]
    s0 = (ppd[261] + ppd[331]) / 2
    s_end = end_pd - 18
    steps = []
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
    thuds, at = [], s0                       # (time, path distance, weight, kind)
    for st, dur, ln, k in steps:
        at += ln
        if k != 'back':
            thuds.append((st + dur, at, 1.0 if k in ('lunge', 'stumble') else 0.55, k))
    sp_v = -rng.uniform(150, 900, 70)
    sp_life = rng.uniform(0.4, 1.4, 70)
    sp_t = T_FUSE + rng.uniform(0, 0.25, 70)
    return dict(cs=cs, arcs=arcs, ladders=ladders, strikes=strikes, steps=steps, s0=s0, thuds=thuds,
                T_GRAB=T_GRAB, T_FUSE=T_FUSE, sparks=(sp_v, sp_life, sp_t), end_pd=end_pd)


BAR = 2.5                                   # 96 BPM, four beats a bar; the coils start one bar apart
BEAT = BAR / 4
T_CHORALE = 14.5                            # the organ's chorale, ten bars, until everything charges
COIL_NOTE = {80: 'C3', 380: 'G3', 178: 'Eb3', 331: 'C4', 260: 'C2'}   # each coil a voice of C minor
VOICING = {'Cm': ('C2', 'G3', 'C4', 'Eb4'), 'Ab': ('Ab1', 'Ab3', 'C4', 'Eb4'), 'Fm': ('F1', 'F3', 'Ab3', 'C4'),
           'G': ('G1', 'G3', 'B3', 'D4'), 'Db': ('Db2', 'F3', 'Ab3', 'Db4'), 'G7': ('G1', 'F3', 'B3', 'D4')}
CHORALE = [('Cm', [(0, 'G4', 1), (1, 'C5', 1), (2, 'Eb5', 1.5), (3.5, 'D5', .5)]),
           ('Ab', [(0, 'C5', 2), (2, 'Ab4', 1), (3, 'Eb5', 1)]),
           ('Fm', [(0, 'F5', 1.5), (1.5, 'Eb5', .5), (2, 'D5', 1), (3, 'C5', 1)]),
           ('G', [(0, 'B4', 3), (3, 'G4', 1)]),
           ('Cm', [(0, 'G4', 1), (1, 'C5', 1), (2, 'Eb5', 1), (3, 'G5', 1)]),
           ('Db', [(0, 'Ab5', 2), (2, 'F5', 1), (3, 'Db5', 1)]),
           ('G7', [(0, 'D5', 1), (1, 'F5', 1), (2, 'B4', 1.5), (3.5, 'G4', .5)]),
           ('Cm', [(0, 'C5', 4)]),
           ('Ab', [(0, 'Eb5', 1), (1, 'C5', 1), (2, 'Ab4', 2)]),
           ('G', [(0, 'G4', 1), (1, 'B4', 1), (2, 'D5', 1), (3, 'F5', 1)])]
WALK_CHORDS = ['Cm', 'Ab', 'Fm', 'Db', 'Cm', 'Ab', 'G']   # one per lunge-and-drag pair


def score(M, G):
    import glob as globmod
    import os
    from pixelhome.audio import SR, VSCO, Sampler, note
    n = note
    P = _plan(G)
    cs, arcs, thuds, steps = P['cs'], P['arcs'], P['thuds'], P['steps']
    T_GRAB, T_FUSE, end_pd = P['T_GRAB'], P['T_FUSE'], P['end_pd']
    rng = np.random.default_rng(23)
    NS = M.n

    for name, gain, rev in (('organ', 0.12, 0.45), ('hum', 0.12, 0.12), ('arc', 0.38, 0.18), ('ladder', 0.07, 0.2),
                            ('storm', 0.45, 0.3), ('feet', 0.35, 0.22), ('fx', 0.3, 0.25), ('creature', 0.18, 0.2)):
        M.bus(name, gain=gain, reverb=rev)

    order = np.argsort(G.pd)
    xs, ds = G.pos[order, 0], G.pd[order]
    x0, x1 = xs.min(), xs.max()

    def pan_x(x):
        return float(0.85 * (2 * (x - x0) / (x1 - x0) - 1))

    def pan_at(d):                          # path distance -> left/right across the facade, from the street
        return pan_x(np.interp(d, ds, xs))

    def put(bus, mono, t, gain=1.0, pan=0.0):
        """Mono signal into a bus; pan may be an array (one value per sample) for things that move."""
        a = (np.asarray(pan, float) + 1) * np.pi / 4
        M.add(bus, np.vstack([mono * np.cos(a), mono * np.sin(a)]) * np.sqrt(2), t, gain)

    # ---- sound makers -------------------------------------------------------------------------------
    def band(sec, lo, hi, seed):
        """Noise band-passed lo..hi Hz (FFT brick wall with soft edges)."""
        m = max(16, int(sec * SR))
        r = np.random.default_rng(seed)
        X = np.fft.rfft(r.normal(0, 1, m))
        f = np.fft.rfftfreq(m, 1 / SR)
        X *= np.clip((f - lo * 0.7) / (lo * 0.3 + 1e-9), 0, 1) * np.clip((hi * 1.3 - f) / (hi * 0.3), 0, 1)
        y = np.fft.irfft(X, m)
        return y / (np.abs(y).max() + 1e-9)

    def crack(sec=0.08, tau=0.018, lo=600, hi=9000, seed=0):
        """One electric crack: a sparse, bright burst."""
        y = band(sec, lo, hi, seed)
        r = np.random.default_rng(seed + 1)
        tt = np.arange(len(y)) / SR
        y *= (r.random(len(y)) < 0.35) * 1.6 + 0.4
        return y * np.exp(-tt / tau) * np.clip(tt / 0.0015, 0, 1)

    def tone(f, sec, harm=6, tilt=1.0):
        """A buzzy tone at f Hz (f may be an array): harmonics 1..harm, falling as 1/k**tilt."""
        m = int(sec * SR)
        f = np.broadcast_to(np.asarray(f, float), (m,))
        ph = 2 * np.pi * np.cumsum(f) / SR
        y = sum(np.sin(k * ph) / k ** tilt * (k * f < 16000) for k in range(1, harm + 1))
        return y

    def env_keys(sec, pts):
        tt = np.arange(int(sec * SR)) / SR
        return np.interp(tt, [p[0] for p in pts], [p[1] for p in pts])

    zap = M.hits('Percussion/zap[1-4]_v1.wav')
    metal = M.hits('Miscellania Raw/Misc 1/metal_hit1[0-1].wav')
    glass = M.hits('Miscellania Raw/Misc 1/glass_break[1-4].wav')
    chain = M.hits('Miscellania Raw/Misc 1/chain_grind.wav')
    timp = M.hits('Percussion/Timpani/Timpani1_Hit_v3_*.wav')
    timp_lo = M.hits('Percussion/Timpani/Timpani1_Hit_v1_*.wav')
    troll = M.hits('Percussion/Timpani/Rolls/Timpani1_Roll_v5*.wav')
    bd = M.hits('VSCO 1 Percussion/drums/bass/bdrum_fff_*.wav')
    bdroll = M.hits('VSCO 1 Percussion/drums/bass/bdrum_roll1.wav')
    gong = M.hits('VSCO 1 Percussion/varMetal/Gong/gong_hit_fff.wav')
    crash = M.hits('Percussion/cymbal-crash1_ff*.wav')
    ratchet = M.hits('Percussion/Ratchet1-Crank*.wav')
    fall = M.sampler('Brass/OldTrombone/Fall/*.wav')
    bassoon = M.sampler('Woodwinds/Bassoon/stac/*.wav')
    glock = M.sampler('Percussion/Glock/*.wav')

    # The VSCO2 pipe organ (Rode, manual 3, open diapason): files are numbered, not named, so the zones are
    # set by hand (file NN sounds MIDI 35 + NN).
    org = Sampler.__new__(Sampler)
    org.zones = {35 + int(p[-6:-4]): {1: [p]}
                 for p in sorted(globmod.glob(os.path.join(VSCO, 'Keys/Organ/Loud/Rode_Man3Open_*.wav')))}
    org.keys, org.rng, org.gain, org.tune = np.array(sorted(org.zones)), M.rng, 1.0, 0
    org_cache = {}

    def organ(t, m, vel, dur, gate=None, pan=0.0, attack=0.0):
        if m not in org_cache:
            org_cache[m] = org.play(m, 127).mean(0)
        y = org_cache[m][:int((dur + 0.4) * SR)] * (vel / 127) ** 1.5
        tt = np.arange(len(y)) / SR
        e = np.clip((dur + 0.25 - tt) / 0.25, 0, 1) ** 2
        if attack:
            e = e * np.clip(tt / attack, 0, 1) ** 2
        if gate is not None:                # gate(time) -> 0..1, e.g. the fuse's brown-out
            e = e * gate(t + tt)
        put('organ', y * e, t, 1.0, pan)

    def chord(t, name, vel, dur, top=True, **kw):
        ped, *hand = VOICING[name]
        organ(t, n(ped), vel, dur, **kw)
        organ(t, n(ped) + 12, vel * 0.8, dur, **kw)
        for m in (hand if top else hand[:1]):
            organ(t, n(m), vel * 0.85, dur, **kw)

    # ---- the coils, exactly as render() charges and discharges them ------------------------------------
    order_c = [(80, 0, 2.0), (380, 1, 4.5), (178, 2, 7.0), (331, 3, 9.5), (260, 4, 12.0)]
    F = nframes(D)
    tf = np.arange(F) * DT
    Lc = {c: np.zeros(F) for c in cs}
    Bc = {c: np.zeros(F) for c in cs}       # charge without the dips: drives pitch
    Dc = {c: np.zeros(F) for c in cs}
    GL = np.zeros(F)
    bed = np.zeros(F)
    dip = {c: 0.0 for c in cs}
    for f in range(F):
        t = f * DT
        glob = keys(t, [(0, 0.55), (39.5, 0.55), (47.5, 1.0), (49.4, 1.0), (49.85, 0.0)]) if t < T_STRIKE else 0.0
        if t > T_HUM:
            rec = keys(t, [(T_HUM, 0), (T_HUM + 3, 0.3), (D - 2, 0.3), (D, 0)])
            u = t - T_HUM
            stut = 1.0 if u > 2.4 else float((np.sin(u * 37) > 0.2) * (u > 0.4) * (np.sin(u * 11) > -0.3))
            glob = rec * stut
        GL[f] = glob
        for c, style, t0 in order_c:
            u = 10.0 if t > T_HUM else t - t0
            b = _coil_build(style, u)
            Bc[c][f] = b
            Dc[c][f] = dip[c]
            Lc[c][f] = max(0.0, b * glob - dip[c])
            dip[c] *= np.exp(-DT / 0.7)
        for a in arcs:
            if not a.fizzle and t >= a.tc and t - a.tc < DT * 0.99 and t <= a.end:
                for c, s in cs.items():
                    if abs(s - a.sa) < 1 or abs(s - a.sb) < 1:
                        dip[c] += 0.4
        for t0, sx, pk in P['strikes']:
            if 0.2 < t - t0 < 0.2 + DT:
                for c in cs:
                    dip[c] -= 0.25
        bedI = keys(t, [(0, 0), (2.5, 0.1), (40, 0.11), (48.5, 0.18), (49.4, 0.16), (49.85, 0.0),
                        (T_ALIVE, 0.0), (T_WALK, 0.07), (T_FUSE, 0.07), (T_FUSE + 0.05, 0.0),
                        (T_HUM + 1.2, 0.0), (T_HUM + 3.5, 0.1), (D - 2, 0.1), (D, 0)])
        sag = 1.0
        for th, d, w, k in thuds:
            if t >= th:
                sag *= 1 - 0.75 * w * np.exp(-(t - th) / 0.14)
        bed[f] = bedI * sag

    ta = np.arange(NS) / SR
    glob_a = np.interp(ta, tf, GL)
    for c, style, t0 in order_c:
        L = np.interp(ta, tf, Lc[c])
        if L.max() < 1e-3:
            continue
        B = np.minimum(np.interp(ta, tf, Bc[c]), 1.6)
        dp = np.interp(ta, tf, Dc[c])
        semis = -15 * (1 - np.minimum(B, 1)) ** 1.5 + 6 * np.maximum(B - 1, 0)   # glides up as it charges
        semis += 12 * np.clip((glob_a - 0.55) / 0.45, 0, 1)                        # an octave up for the finale
        pre = ta < T_STRIKE
        semis -= pre * 24 * np.clip(1 - glob_a / 0.55, 0, 1) * (ta > 49.0)        # and the power-down whine
        semis -= 5 * np.clip(dp, 0, 1)                                             # an arc sags it
        fr = 440 * 2 ** ((n(COIL_NOTE[c]) - 69 + semis) / 12)
        amp = np.minimum(L, 1.4) ** 0.8
        y = tone(fr, NS / SR, harm=7, tilt=1.15) + 0.5 * tone(fr * 1.004, NS / SR, harm=3)
        y = np.tanh(1.6 * y) * amp
        put('hum', y, 0.0, 0.16 if c != 260 else 0.26, pan_at(cs[c]))
    # the lab's mains bed: a low C that sags under every footstep
    c2 = 440 * 2 ** ((n('C2') - 69) / 12)
    bd_a = np.interp(ta, tf, bed) / 0.1
    put('hum', np.tanh(1.4 * tone(c2, NS / SR, harm=9, tilt=1.3)) * bd_a, 0.0, 0.11, 0.0)
    # coil sparks: ticks at a rate that follows each coil's charge squared
    for c in cs:
        rate = 5 * np.minimum(Lc[c], 1.2) ** 2
        for f in np.nonzero(rng.random(F) < rate * DT)[0]:
            put('arc', crack(0.03, 0.006, 2000, 12000, seed=int(f) + c), tf[f], 0.25, pan_at(cs[c]))

    # ---- the doctor throws a knife switch for each coil; the ratchet coil clicks its five stages ----------
    for c, style, t0 in order_c:
        p = pan_at(cs[c])
        M.add('fx', metal.play(105, pitch=-9, dur=0.8), t0, 0.55, p)
        M.add('feet', bd.play(70), t0, 0.35, p)
        if style == 1:
            for k in (0, .8, 1.6, 2.4, 3.2):
                M.add('fx', ratchet.play(100, dur=0.12), t0 + k, 0.6, p)
                M.add('fx', metal.play(70, pitch=7, dur=0.2), t0 + k, 0.2, p)

    # ---- arcs: crackling leaders where they are on the roof, fizzles, and three-pulse return strokes ------
    for i, a in enumerate(arcs):
        pa, pb = pan_at(a.sa), pan_at(a.sb)
        for j in range(1, len(a.ts)):
            d = a.sa + a.dir * a.hs[j]
            put('arc', crack(0.07, 0.014, seed=1000 * i + j), a.t0 + a.ts[j], 0.45 * a.k, pan_at(d))
        crawl = a.tc - a.t0
        sz = band(crawl, 2500, 9000, 77 + i) * env_keys(crawl, [(0, 0), (0.05, 1), (crawl, 1.3)])
        sz *= 0.6 + 0.4 * np.sin(2 * np.pi * 23 * np.arange(len(sz)) / SR)
        put('arc', sz, a.t0, 0.06 * a.k, np.linspace(pa, pb, len(sz)))
        if a.fizzle:                        # not enough charge: it sputters out with a sad little droop
            m = int(0.4 * SR)
            tt = np.arange(m) / SR
            droop = tone(900 * (250 / 900) ** (tt / 0.4), 0.4, harm=2) * np.exp(-tt / 0.15)
            put('fx', droop, a.tc, 0.12, pan_at(a.sa + a.dir * a.hs[-1]))
            put('arc', crack(0.25, 0.08, 1500, 8000, seed=i), a.tc, 0.4 * a.k, pan_at(a.sa + a.dir * a.hs[-1]))
            continue
        pm = pan_at((a.sa + a.sb) / 2)
        for dt, g, pp in ((0.0, 1.0, pm), (0.11, 0.7, pb), (0.24, 0.45, pa)):
            put('arc', crack(0.12, 0.03, 300, 12000, seed=5000 + 3 * i + int(dt * 100)), a.tc + dt, a.k * g, pp)
        M.add('arc', zap.play(110, pitch=float(rng.uniform(-3, 3)), dur=0.45), a.tc, 0.55 * a.k, pm)
        for s0f, dd, ln in a.forks:
            put('arc', crack(0.06, 0.012, seed=9000 + i), a.tc + 0.03, 0.35 * a.k, pan_at(s0f + dd * ln))

    # ---- Jacob's ladders up the porch rails: a buzz that climbs, stretches across, and snaps ------------
    pl, pr, pfp = pan_at(float(G.pd[G.seg['Porch Left']].mean())), pan_at(float(G.pd[G.seg['Porch Right']].mean())), \
        pan_at((G.pd[G.path][261] + G.pd[G.path][331]) / 2)
    for i, (t0, dur) in enumerate(P['ladders']):
        sec = dur + 0.42
        tt = np.arange(int(sec * SR)) / SR
        u = np.clip(tt / dur, 0, 1) ** 1.7
        fr = 98 * 4 ** u                    # G2 to G4, as fast as the arc's height climbs
        jit = np.repeat(np.random.default_rng(i).uniform(0.75, 1.0, int(sec * 40) + 2), SR // 40)[:len(tt)]
        e = np.clip(tt / 0.05, 0, 1) * (0.5 + 0.5 * u) * jit * (tt < dur + 0.36)
        for pp, det in ((pl, 1.0), (pr, 1.006)):
            y = np.tanh(2.2 * tone(fr * det, sec, harm=8, tilt=0.9)) * e
            y += 0.4 * band(sec, 3000, 10000, 300 + i) * e
            put('ladder', y, t0, 0.5, pp)
        snap = t0 + dur + 0.37
        put('arc', crack(0.2, 0.05, 200, 12000, seed=700 + i), snap, 1.0, pfp)
        M.add('arc', zap.play(120, pitch=-4, dur=0.6), snap, 0.6, pfp)

    # ---- thunder: a crack with the flash (and each re-flash), then the roll from where it fell ------------
    def thunder(t, pan, big=1.0, sec=4.0, seed=0):
        tt = np.arange(int(sec * SR)) / SR
        r = np.random.default_rng(seed)
        rum = band(sec, 25, 220, seed) * (0.6 + 0.4 * np.interp(tt, np.linspace(0, sec, 24), r.random(24)))
        rum *= np.clip(tt / 0.25, 0, 1) * np.exp(-tt / (sec / 3.2))
        put('storm', rum, t + 0.12, 1.0 * big, pan * 0.6)
        put('storm', band(sec, 150, 900, seed + 1) * rum, t + 0.12, 0.9 * big, -pan * 0.3)

    for i, (t0, sx, pk) in enumerate(P['strikes']):
        p = pan_x(sx)
        thunder(t0 - 1.4 + 0.7, p, 0.15, 2.5, seed=40 + i)        # the far-off flicker first
        for dt, g in ((0.0, 1.0), (0.2, 0.8), (0.42, 0.45)):
            put('storm', crack(0.35, 0.09, 200, 10000, seed=60 + 7 * i + int(dt * 10)), t0 + dt, 0.9 * pk * g, p)
        thunder(t0, p, pk, 4.5, seed=80 + i)
        M.add('storm', bdroll.play(60, dur=2.5), t0 + 0.2, 0.4 * pk, p * 0.5)

    # ---- music: a single pedal from the start, then the organ answers the first arc that connects ---------
    organ(0.3, n('C1'), 70, 14.0, attack=2.5)
    organ(0.3, n('C2'), 50, 14.0, attack=4.0)
    first = next(a for a in arcs if not a.fizzle)
    chord(first.tc, 'Cm', 118, 1.6)
    chord(first.tc + 1.9, 'G', 100, 0.5, top=False)
    for b, (name, mel) in enumerate(CHORALE):
        t = T_CHORALE + b * BAR
        chord(t, name, 80, BAR * (0.5 if b == 9 else 1.0) - 0.05)
        if b == 9:
            chord(t + 2 * BEAT, name, 90, 2 * BEAT - 0.05)
        for bt, m, ln in mel:
            organ(t + bt * BEAT, n(m), 100, ln * BEAT - 0.04)
            organ(t + bt * BEAT, n(m) + 12, 62, ln * BEAT - 0.04)

    # ---- 39.5-49.85: everything charges; each arc that lands climbs a semitone, dim7 and minor by turns ----
    rush = [a for a in arcs if a.t0 >= 39.5]
    for m in ('G1', 'D2', 'G2'):            # the doctor holds the dominant while the coils gather
        organ(T_CHORALE + 10 * BAR, n(m), 85, rush[0].tc - T_CHORALE - 10 * BAR, attack=0.3)

    def cut(tt):                            # the organ dies with the lab at 49.85
        return np.clip((49.85 - tt) / 0.45, 0, 1)

    for k, a in enumerate(rush):
        nxt = rush[k + 1].tc if k + 1 < len(rush) else 49.85
        root = n('C2') + k
        shape = (0, 12, 15, 19) if k % 2 == 0 else (0, 12, 15, 18, 21)
        for s in shape:
            organ(a.tc, root + s, 100 + 1.4 * k, max(0.12, nxt - a.tc - 0.03), gate=cut)
        organ(a.tc, root + 24 + (3 if k % 2 == 0 else 6), 100 + 1.4 * k, max(0.12, nxt - a.tc - 0.03), gate=cut)
    M.add('feet', troll.play(70, dur=5.4), 44.0, 0.5, 0.0)
    M.add('feet', troll.play(95, dur=3.0), 46.4, 0.6, 0.0)
    for t in np.arange(48.0, 49.4, 0.1):    # rolling to the cut
        M.add('feet', timp.play(80 + 30 * (t - 48), pitch=-2, dur=0.3), float(t), 0.4)

    # ---- 50.0: the giant strike; the coils overload and scream out ------------------------------------
    put('storm', crack(1.2, 0.25, 80, 14000, seed=999), T_STRIKE, 1.6, 0.0)
    M.add('storm', gong.play(127), T_STRIKE, 1.3, 0.0)
    M.add('feet', bd.play(127), T_STRIKE, 1.0, 0.0)
    M.add('feet', timp_lo.play(127, pitch=-5), T_STRIKE, 0.9, 0.0)
    M.add('storm', crash.play(127), T_STRIKE, 0.6, 0.0)
    thunder(T_STRIKE, 0.0, 1.8, 7.0, seed=123)
    tt = np.arange(int(1.6 * SR)) / SR
    for c in cs:
        fr = 440 * 2 ** ((n(COIL_NOTE[c]) + 19 - 69 + 7 * tt) / 12)
        y = np.tanh(2 * tone(fr, 1.6, harm=6)) * np.exp(-np.clip(tt - 0.05, 0, None) / 0.35) * np.clip(tt / 0.02, 0, 1)
        put('hum', y, T_STRIKE + 0.25, 0.22, pan_at(cs[c]))

    # ---- 52.3: it twitches three times, and the organ says so ------------------------------------------
    body_p = pan_at(P['s0'])
    for i, tw in enumerate((T_ALIVE, T_ALIVE + 0.75, T_ALIVE + 1.35)):
        M.add('creature', zap.play(120, pitch=-7 + 2 * i, dur=0.5), tw, 1.0, body_p)
        put('arc', crack(0.1, 0.03, 300, 9000, seed=200 + i), tw, 0.8, body_p)
        M.add('feet', timp.play(100 + 10 * i, pitch=-3 + 2 * i), tw, 0.7, body_p)
        organ(tw, n('C1') + [0, 1, 7][i], 110, 0.4)
    for m in ('C2', 'C3', 'G3', 'C4', 'Eb4', 'G4', 'C5'):
        organ(T_ALIVE + 1.35, n(m), 124, T_WALK - T_ALIVE - 1.35 + 0.3, attack=0.0)
    M.add('storm', crash.play(110), T_ALIVE + 1.35, 0.4, body_p)

    # the creature's electric pulse: 3.1 Hz, as the body's light throbs
    def fuse_fl(t):
        ft = np.asarray(t) - T_FUSE
        fl = np.interp(ft, [0, 0.08, 0.16, 0.26, 0.38, 0.5], [1, 0.15, 0.9, 0.1, 0.6, 0.0])
        return np.where(ft < 0, 1.0, fl)

    sec = T_FUSE + 0.6 - T_ALIVE
    tt = T_ALIVE + np.arange(int(sec * SR)) / SR
    twitch = sum(np.exp(-(tt - tw) / 0.12) * (tt >= tw) for tw in (T_ALIVE, T_ALIVE + 0.75, T_ALIVE + 1.35))
    idle = np.clip((tt - T_ALIVE) / (T_WALK - T_ALIVE), 0, 1)
    flare = sum(0.8 * w * np.exp(-(tt - th) / 0.1) * (tt >= th) for th, d, w, k in thuds)
    life = (0.35 + 0.35 * idle + 0.8 * twitch) * (1 + flare) * (1 + 0.5 * np.sin(tt * 2 * np.pi * 3.1)) * fuse_fl(tt)
    walk_s = np.interp(tt, [s[0] for s in steps] + [T_GRAB], np.cumsum([0] + [s[2] for s in steps]) + P['s0'])
    grr = np.tanh(1.5 * tone(c2 / 2 * (1 + 0.01 * np.sin(tt * 7)), sec, harm=10, tilt=0.8)) * life
    put('creature', grr, T_ALIVE, 0.6, np.array([pan_at(d) for d in walk_s[::480]]).repeat(480)[:len(grr)])

    # ---- the walk: timpani on every lunge with the organ stamping a chord; chains dragged on every drag ---
    for i, (th, d, w, k) in enumerate(thuds):
        p = pan_at(d)
        name = WALK_CHORDS[i // 2]
        if w == 1.0:
            M.add('feet', timp_lo.play(127, pitch=-4), th, 1.0, p)
            M.add('feet', bd.play(120), th, 0.8, p)
            M.add('fx', metal.play(60, pitch=-14, dur=1.2), th, 0.25, p)     # the roof rings
            nxt = thuds[i + 1][0] if i + 1 < len(thuds) else th + 0.8
            chord(th, name, 112, nxt - th + 0.15)
        else:
            M.add('feet', timp.play(95, pitch=-2), th, 0.8, p)
            ped = VOICING[name][0]
            organ(th, n(ped) + 7, 90, 0.5)
    starts = P['s0'] + np.cumsum([0] + [s[2] for s in steps])[:-1]       # body position as each step begins
    for (st, dur, ln, k), d0 in zip(steps, starts):
        if k == 'drag':
            M.add('fx', chain.play(110, pitch=-3, dur=dur), st, 0.7, pan_at(d0 + ln / 2))
        elif k == 'stumble':                # he trips forward ...
            M.add('creature', fall.play(n('C#2'), 115, dur=0.9), st + 0.1, 0.8, pan_at(d0 + ln))
        elif k == 'back':                   # ... steps back, and thinks about it
            M.add('creature', bassoon.play(n('Ab2'), 100, dur=0.16), st, 0.7, pan_at(d0))
            M.add('creature', bassoon.play(n('G2'), 92, dur=0.3), st + 0.22, 0.7, pan_at(d0))

    # ---- the grab and the fuse ------------------------------------------------------------------------
    pe = pan_at(end_pd)
    gsec = T_FUSE - T_GRAB
    tt = np.arange(int(gsec * SR)) / SR
    whine = np.tanh(2 * tone(220 * 8 ** (tt / gsec), gsec, harm=5)) * np.clip(tt / 0.2, 0, 1)
    put('fx', whine, T_GRAB, 0.14, pe)
    put('arc', band(gsec, 2000, 10000, 4) * (tt / gsec) ** 1.2, T_GRAB, 0.35, pe)
    for t in T_GRAB + np.sort(rng.uniform(0, gsec, 24)):
        put('arc', crack(0.05, 0.01, seed=int(t * 1000)), float(t), 0.4, pe)
    chord(T_GRAB, 'G7', 120, T_FUSE + 0.5 - T_GRAB, gate=fuse_fl)
    organ(T_GRAB, n('Ab4'), 110, T_FUSE + 0.5 - T_GRAB, gate=fuse_fl)          # b9: it will not resolve
    put('arc', crack(0.4, 0.07, 100, 14000, seed=31), T_FUSE, 1.0, pe)
    M.add('fx', glass.play(120), T_FUSE + 0.01, 0.8, pe)
    M.add('fx', metal.play(120, pitch=-5), T_FUSE, 0.6, pe)
    M.add('feet', bd.play(118), T_FUSE, 0.8, pe)
    sp_v, sp_life, sp_t = P['sparks']
    gl_notes = [n(m) for m in ('C6', 'Eb6', 'G6', 'Bb6', 'C7', 'Eb7', 'G7')]
    for v, life, t in zip(sp_v, sp_life, sp_t):
        put('arc', crack(0.02, 0.004, 3000, 14000, seed=int(t * 1e4)), float(t), 0.25, pe)
        dend = end_pd + v * life * (1 - 0.45)
        M.add('fx', glock.play(gl_notes[int(rng.integers(len(gl_notes)))], 50, dur=0.4), float(t + life), 0.25,
              pan_at(max(0.0, dend)))

    # ---- 71: the hum stutters back on by itself; the last twitch gets a question ------------------------
    organ(T_HUM + 2.6, n('C2'), 45, D - T_HUM - 2.6, attack=2.0)
    organ(T_HUM + 2.6, n('G2'), 40, D - T_HUM - 2.6, attack=2.5)
    for i, a in enumerate((0.0, 0.5)):
        t = D - 3.2 + a
        M.add('creature', zap.play(90, pitch=-9 + 3 * i, dur=0.35), t, 0.5, pe)
        put('arc', crack(0.06, 0.015, seed=400 + i), t, 0.4, pe)
    organ(D - 2.7, n('B4'), 70, 2.7)
