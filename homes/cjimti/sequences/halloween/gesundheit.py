"""Gesundheit: The Watcher has caught a cold. Same face as before (the wing fronts are his eyes, the porch
is his toothy mouth, the porch sides and Side are the outline of his head), but tonight he wakes up groggy
with a stuffy snore. His eyes water: blue drips well up at the inner corners and run down the porch sides
toward his mouth, and a sniff yanks them back up. A sneeze builds (ah... ah... AH...: the eyes squint and
flutter, the mouth opens wider each time, air streams in along the roof toward the mouth), fizzles out,
and then comes all at once: a blast blows out of the mouth to both free ends and knocks every light out.
He comes back on dazed and cross-eyed, with the hiccups: each one jolts the face, snaps the eyes wide and
pops a little burst out of the mouth. He holds his breath (the head goes purple, red, blue; muffled hics
still jolt it), gives up, hiccups again. A tissue flutters in from the right end of the house, his eyes
follow it to his mouth, he blows his nose twice (HONK, HOOONK) and tosses it away. The hiccups are gone:
a big grin and a sigh of relief... then one last tiny hic.

Everything along the roof (drips, the inhale, the blast, bursts, the tissue) is placed by path distance, so
it keeps its size on every run. The eyes and mouth use The Watcher's geometry and colours."""
import numpy as np
from pixelhome.fx import DT, hexc, perc, light, keys, lerp, smoothstep, Flicker, nframes

CODE = 'HW12'
TITLE = 'Gesundheit'
KIND = 'show'
DESCRIPTION = ('The Watcher is back, and he has a cold: watery eyes, sniffles, a sneeze so big it blows every '
               'light off the house, and then the hiccups. Somebody get that house a tissue.')
VOICEOVER = "Remember the house that watches you? Well... he caught a cold. Stand back, everybody. Way back."

AMBER = hexc('#ffa000')
ORANGE = hexc('#ff3000')
PALE = hexc('#ffd070')
DEEP_RED = hexc('#a00000')
PURPLE = hexc('#5000c0')
WHITE = hexc('#ffffff')
RED = hexc('#ff0000')
DRIP = hexc('#2a7fff')
AIR = hexc('#80c8ff')
SPRAY = hexc('#b0ffe0')
BUBBLE = hexc('#a0e0ff')
COLD = hexc('#1040ff')
TISSUE = hexc('#fff4ec')

D = 76.0
# ---- shared timings (render and score both read these) ----
SNORES = (1.0, 4.6)                          # inhale over 1.6 s, then a whistling exhale from +1.7 to +2.9
SNORT = 8.4                                  # the snort that wakes him
FORM, RUN = 0.6, 1.4                         # a drip wells up for FORM s, then runs to the mouth in RUN s
DRIPS = [(10.3, 'L', None), (11.6, 'R', None), (13.4, 'L', 14.9), (13.7, 'R', 14.9), (16.4, 'L', None),
         (17.0, 'R', None), (17.6, 'L', None), (18.6, 'L', 20.0), (18.9, 'R', 20.0)]
SNIFFS = (14.9, 20.0, 21.3)
AH_KEYS = [(22.4, 0), (23.7, 0.45), (24.6, 0.35), (26.2, 0.7), (27.1, 0.6), (29.0, 1.0), (30.5, 1.0), (30.9, 0),
           (33.0, 0), (33.5, 1.1), (33.6, 1.1), (33.62, 0)]
INHALES = [(22.4, 23.7, 0.5), (24.6, 26.2, 0.7), (27.1, 29.0, 1.0), (33.0, 33.55, 1.0), (50.4, 51.45, 0.8)]
FLUTTER = (29.0, 30.5, 7.0)                  # the eyelids flutter at 7 Hz while the AH hangs
FAKE = 30.6                                  # ...and it goes away
CHOO, BLAST = 33.6, 0.65                     # the sneeze, and how long the blast takes to reach both ends
T_END = CHOO + BLAST
FIZZ = [(34.7, 'Left', 0.3), (35.15, 'Porch Right', -0.2), (35.55, 'Right', -0.4)]
SPUTTER = [(36.0, 36.07), (36.25, 36.31), (36.42, 36.56), (36.7, 99.0)]   # the outline comes back on
DAZED = (36.6, 38.7)
HICS = [(38.9, 1.0), (40.4, 1.0), (41.1, 1.0), (43.0, 1.0), (43.45, 1.0), (45.6, 1.0), (46.9, 1.0), (47.25, 1.0),
        (47.6, 1.0), (49.6, 1.0), (57.4, 1.0), (69.6, 0.5)]
MUFFLED = (52.9, 54.4, 55.4)                 # hics while he holds his breath: the face jolts, nothing comes out
HOLD = (51.5, 56.0)
EXHALE = 56.0
TISSUE_IN, TOSS = (58.5, 62.0), (64.3, 65.0)
HONKS = [(62.4, 0.35), (63.1, 0.95)]
SIGH = (65.6, 67.8)

O_KEYS = [(0, 0), (8.42, 0), (8.6, 0.42), (9.2, 0.3), (10.5, 0.42), (22.4, 0.42), (23.7, 0.3), (24.6, 0.36),
          (26.2, 0.2), (27.1, 0.24), (29.0, 0.1), (30.5, 0.1), (30.9, 0.62), (32.8, 0.62), (33.05, 0.08),
          (33.6, 0.0), (36.5, 0.0), (37.3, 0.55), (38.8, 0.55), (49.8, 0.5), (50.4, 0.7), (51.4, 0.7),
          (51.6, 0.0), (56.0, 0.0), (56.15, 0.9), (56.9, 0.6), (57.9, 0.32), (58.6, 0.32), (59.1, 0.72),
          (62.15, 0.72), (62.3, 0.04), (64.2, 0.04), (64.45, 0.0), (65.4, 0.0), (66.0, 0.75), (73.0, 0.75),
          (75.0, 0.0)]
BLINKS = [(11.8, 0.3), (15.9, 0.3), (44.4, 0.13), (48.6, 0.13), (60.4, 0.13), (67.6, 0.13), (72.6, 0.15)]
EI_KEYS = [(0, 0), (8.42, 0), (8.6, 0.65), (22.0, 0.7), (29.0, 0.9), (33.6, 0.95), (36.5, 0.8), (73.0, 0.8),
           (75.5, 0)]
LINE_KEYS = [(0, 0), (2.5, 0.16), (8.42, 0.16), (8.6, 0.22), (73.0, 0.22), (75.5, 0)]
GAZE_KEYS = [(8.6, 0), (12.0, 0), (13.0, -0.6), (15.0, -0.6), (16.5, 0.5), (18.5, 0.5), (19.5, 0), (30.6, 0),
             (31.0, -0.8), (31.7, -0.8), (32.0, 0.8), (32.6, 0.8), (32.9, 0), (70.3, 0), (70.6, -0.85),
             (71.3, -0.85), (71.6, 0.85), (72.2, 0.85), (72.5, 0)]
GRIN_KEYS = [(65.4, 0), (66.6, 0.7), (69.55, 0.7), (69.62, 0), (70.6, 0), (71.2, 0.3), (73.0, 0.3), (75.2, 0)]
OI_KEYS = [(0, 0), (2.5, 0.14), (8.4, 0.14), (8.5, 0.24), (9.5, 0.17), (22.4, 0.17), (29.0, 0.26), (30.6, 0.26),
           (31.0, 0.17), (51.5, 0.17), (55.9, 0.42), (56.1, 0.17), (73.0, 0.17), (75.8, 0)]
OCOL_KEYS = [(51.5, PURPLE), (53.6, RED), (55.4, COLD), (55.95, COLD), (56.2, PURPLE)]
LIPS_KEYS = [(51.35, 0), (51.55, 1), (55.95, 1), (56.05, 0)]
EX_KEYS = [(55.95, 0), (56.1, 1), (57.3, 0)]
TISSUE_GAZE = [(58.6, 0), (59.0, 1), (64.1, 1), (64.4, 0)]


# ---- event envelopes, shared ----
def snore_env(t):
    e = 0.0
    for s in SNORES:
        if s <= t < s + 2.9:
            e = smoothstep(s, s + 1.6, t) * (1 - smoothstep(s + 1.7, s + 2.9, t))
    return float(e)


def inhale_env(t):
    e = 0.0
    for t0, t1, a in INHALES + [(s - 0.25, s, 0.6) for s in SNIFFS]:
        if t0 <= t < t1:
            e += a * np.sin(np.pi * (t - t0) / (t1 - t0)) ** 0.5
    return e


def sniff_env(t):
    return max([float(smoothstep(s - 0.25, s, t) * (1 - smoothstep(s + 0.05, s + 0.5, t))) for s in SNIFFS])


def drip_state(t, t0, tsn):
    """(s 0..1 along the porch side, intensity, splash age or None), or None when there is no drip."""
    if t < t0:
        return None
    tr = t - t0 - FORM
    if tr < 0:
        return 0.0, 0.9 * float(smoothstep(0, FORM, t - t0)), None
    if tsn is not None and t >= tsn:
        s0 = min(1.0, ((tsn - t0 - FORM) / RUN) ** 2) if tsn > t0 + FORM else 0.0
        u = (t - tsn) / 0.18
        if u >= 1:
            return None
        return s0 * (1 - float(smoothstep(0, 1, u))), 0.9, None
    s = (tr / RUN) ** 2
    if s < 1:
        return s, 0.9, None
    age = tr - RUN
    return (1.0, 0.0, age) if age < 0.35 else None


def blast_s(t):
    return float(np.clip((t - CHOO) / BLAST, 0, 1) ** 0.85)


def hic_state(t):
    """(jolt, snap, burst list [(age, scale)])."""
    j, snap, bursts = 0.0, 0.0, []
    for th, sc in HICS:
        a = t - th
        if 0 <= a < 0.6:
            j += 0.12 * sc * np.exp(-a / 0.1) * np.cos(2 * np.pi * 5 * a)
            snap = max(snap, sc * np.exp(-a / 0.2))
            if a < 0.45:
                bursts.append((a, sc))
    for th in MUFFLED:
        a = t - th
        if 0 <= a < 0.6:
            j += 0.08 * np.exp(-a / 0.1) * np.cos(2 * np.pi * 5 * a)
    return j, snap, bursts


def honk_env(t):
    return max([float(smoothstep(t0, t0 + 0.04, t) * (1 - smoothstep(t0 + d, t0 + d + 0.12, t))) for t0, d in HONKS])


def sputter(t):
    return float(any(a <= t < b for a, b in SPUTTER))


def tissue_pd(t, L, dM):
    """Path distance of the tissue, or None."""
    if t < TISSUE_IN[0] or t >= TOSS[1]:
        return None
    if t < TISSUE_IN[1]:
        u = (t - TISSUE_IN[0]) / (TISSUE_IN[1] - TISSUE_IN[0])
        u = 1 - (1 - u) ** 1.6
        return lerp(L + 30, dM, u) + 10 * np.sin(2 * np.pi * 1.1 * t) * (1 - u)
    if t < TOSS[0]:
        return dM
    u = (t - TOSS[0]) / (TOSS[1] - TOSS[0])
    return dM + (L + 60 - dM) * u * u


def geometry(G):
    """Path-distance landmarks the lights and the music share."""
    pd = G.pd
    PL, PR, PF = G.seg['Porch Left'], G.seg['Porch Right'], G.seg['Porch Front']
    L = float(G.length)
    dM = float(pd[PF].mean())
    g = dict(L=L, dM=dM, cL=float(pd[PL].min()), runL=float(pd[PL].max() - pd[PL].min()),
             cR=float(pd[PR].max()), runR=float(pd[PR].max() - pd[PR].min()),
             mL=float(pd[PF].min()), mR=float(pd[PF].max()))
    g['frac'] = np.where(pd < dM, (dM - pd) / dM, (pd - dM) / (L - dM))
    order = G.path
    g['pdp'], g['xp'] = pd[order], G.pos[order, 0]
    return g


def drip_pd(g, side, s):
    return g['cL'] + 8 + s * (g['runL'] - 8) if side == 'L' else g['cR'] - 8 - s * (g['runR'] - 8)


def render(G, seed=12):
    rng = np.random.default_rng(seed)
    out = np.zeros((nframes(D), G.N, 3))
    g = geometry(G)
    L, dM, frac, pd = g['L'], g['dM'], g['frac'], G.pd
    tpass = CHOO + BLAST * frac ** (1 / 0.85)
    drops = rng.uniform(0, 1, G.N) < 0.35
    eyes = []
    for k in ('Left', 'Right'):
        idx = G.seg[k]
        ex = G.pos[idx, 0]
        eyes.append((idx, G.span_u(idx), (ex.max() + ex.min()) / 2, (ex.max() - ex.min()) / 2))
    M, uM = G.seg['Porch Front'], G.span_u(G.seg['Porch Front'])
    O = np.concatenate([G.seg['Side'], G.seg['Porch Left'], G.seg['Porch Right']])
    flick = Flicker(rng, G.N, 0.3, 1.5)
    rattle = Flicker(rng, G.N, 6.0, 11.0)
    teeth = (1 - np.abs(2 * (((uM + 1) / 2 * 9) % 1) - 1)) ** 1.3     # 9 pointed teeth
    corners = 1 - 0.6 * np.abs(uM) ** 4
    fizz_pd = [float(pd[G.seg[k]].mean() + off * (pd[G.seg[k]].max() - pd[G.seg[k]].min()) / 2) for _, k, off in FIZZ]

    def blob(c, w):
        return np.exp(-((pd - c) / w) ** 2)

    for f in range(len(out)):
        t = f * DT
        fr = out[f]
        fl = 1 + 0.04 * flick(t)
        jolt, snap, bursts = hic_state(t)
        hk = honk_env(t)
        sn = snore_env(t)
        sf = sniff_env(t)
        a = float(keys(t, AH_KEYS))
        # the blast knocks out each pixel as it passes; the face comes back after 36 s
        if CHOO <= t < 36.0:
            kn = (t < tpass).astype(float)
        else:
            kn = np.ones(G.N)
        rec = 1.0 if t < CHOO else float(smoothstep(36.3, 36.8, t))

        # ---- eyes ----
        o = float(keys(t, O_KEYS))
        o *= 1 - max([max(0.0, 1 - abs(t - b) / w) for b, w in BLINKS])
        if FLUTTER[0] <= t < FLUTTER[1]:
            o += 0.2 * (0.5 + 0.5 * np.sin(2 * np.pi * FLUTTER[2] * (t - FLUTTER[0]))) ** 2
        o = max(0.0, o - 0.15 * sf)
        o += (0.95 - o) * snap
        eI = float(keys(t, EI_KEYS)) * rec
        line = float(keys(t, LINE_KEYS)) * rec * (1 - np.clip(o / 0.12, 0, 1)) * (1 + 0.3 * sn)
        gaze = float(keys(t, GAZE_KEYS))
        gz = [gaze, gaze]
        if DAZED[0] <= t < DAZED[1]:
            dz = float(keys(t, [(DAZED[0], 1), (38.0, 1), (DAZED[1], 0)]))
            ph = 2 * np.pi * 0.9 * (t - DAZED[0])
            gz = [gaze + 0.85 * dz * np.sin(ph), gaze + 0.85 * dz * np.sin(ph + np.pi)]
        tp = tissue_pd(t, L, dM)
        tw = float(keys(t, TISSUE_GAZE))
        if tp is not None and tw > 0:
            xt = float(np.interp(tp, g['pdp'], g['xp']))
            for i, (_, _, cx, hw) in enumerate(eyes):
                gz[i] = lerp(gz[i], float(np.clip((xt - cx) / hw / 0.55, -1, 1)), tw)
        pw = (0.07 if t < 22 else 0.06) * (1 - 0.6 * snap)
        wet = float(keys(t, [(8.6, 0), (10, 1), (33.6, 1), (34, 0)]))
        ecol = lerp(AMBER, ORANGE, 0.25 * float(keys(t, [(20, 1), (23, 0)])))
        ecol = lerp(ecol, PALE, 0.35 * float(keys(t, [(65.4, 0), (66.5, 1), (73, 1), (75, 0)])))
        for i, (idx, u, _, _) in enumerate(eyes):
            uj = u - jolt
            lid = np.clip((o - np.abs(uj)) / 0.08, 0, 1)
            shape = 0.55 + 0.45 * (1 - uj ** 2)
            pupil = np.clip((np.abs(uj - gz[i] * 0.55) - pw) / 0.04, 0, 1)
            fr[idx] += light(ecol, eI * lid * shape * (0.03 + 0.97 * pupil) * fl[idx] * kn[idx])
            fr[idx] += light(ecol, line * np.clip((0.75 - np.abs(uj)) / 0.15, 0, 1) * shape * kn[idx])
            if wet > 0:
                gl = (0.5 + 0.5 * np.sin(9 * u + 2.3 * t + 1.7 * i)) ** 6
                fr[idx] += light(DRIP, wet * 0.4 * eI * lid * gl * kn[idx])

        # ---- mouth ----
        on = float(keys(t, [(0, 0), (2.5, 1), (73, 1), (75.5, 0)])) * (1.0 if t < CHOO else float(smoothstep(36.7, 37.2, t)))
        mo = 0.2 + 0.25 * sn + 0.7 * a
        rv = 0.17 + 0.22 * sn + 0.9 * a - 0.06 * sf
        mo, rv = lerp(mo, 0.95, snap), lerp(rv, 0.22, snap)
        ex = float(keys(t, EX_KEYS))
        mo, rv = mo + 0.7 * ex, max(rv, 1.05 * ex)
        mo, rv = mo + 0.35 * hk, max(rv, 0.4 * hk)
        grin = float(keys(t, GRIN_KEYS))
        mo, rv = mo + grin, max(rv, min(1.1, 1.6 * grin))
        lips = float(keys(t, LIPS_KEYS))
        mo *= 1 - lips
        uMj = uM - 0.5 * jolt
        rmask = np.clip((rv - np.abs(uMj)) / 0.1, 0, 1)
        mcol = lerp(ORANGE, PALE, teeth[:, None] * min(1, mo * 1.5))
        km = kn[M] * on
        fr[M] += perc(mo * corners * (0.25 + 0.75 * teeth) * rmask * km)[:, None] * mcol
        fr[M] += light(DEEP_RED, 0.45 * mo * (1 - teeth) * rmask * km)
        if lips > 0:
            fr[M] += light(ORANGE, 0.3 * lips * np.clip((0.7 - np.abs(uMj)) / 0.1, 0, 1) * km)

        # ---- outline of the head ----
        oI = float(keys(t, OI_KEYS)) + 0.25 * snap + 0.12 * sf + 0.4 * hk
        if SIGH[0] <= t < SIGH[1]:
            oI *= 1 + 0.5 * np.sin(np.pi * (t - SIGH[0]) / (SIGH[1] - SIGH[0]))
        ocol = keys(t, OCOL_KEYS)
        ko = kn[O] * (1.0 if t < CHOO else sputter(t))
        fr[O] += light(ocol, oI * (1 + 0.15 * np.sin(2 * np.pi * t / 4)) * fl[O] * (1 + 0.3 * hk * rattle(t)[O]) * ko)

        # ---- drips run from the inner corners of the eyes down the porch sides to the mouth ----
        for t0, side, tsn in DRIPS:
            st = drip_state(t, t0, tsn)
            if st is None:
                continue
            s, I, age = st
            if age is None:
                fr[:] += light(DRIP, I * blob(drip_pd(g, side, s), 9.0 + 3 * (s == 0)))
                if s > 0.05:                 # a wet trail behind it
                    p0, p1 = drip_pd(g, side, 0), drip_pd(g, side, s)
                    lo, hi = min(p0, p1), max(p0, p1)
                    fr[:] += light(DRIP, 0.18 * ((pd > lo) & (pd < hi)))
            else:
                c = g['mL'] if side == 'L' else g['mR']
                fr[:] += light(DRIP, 0.75 * np.exp(-age / 0.12) * blob(c, 25.0))

        # ---- air streams in along the roof toward the mouth on every inhale ----
        ie = inhale_env(t)
        if ie > 0:
            st = (0.5 + 0.5 * np.cos(2 * np.pi * (frac * 7 + 1.8 * t))) ** 3
            fr[:] += light(AIR, 0.38 * min(ie, 1.0) * st * (0.3 + 0.7 * frac))

        # ---- the sneeze: a blast out of the mouth to both free ends, spray behind it, the ends pop ----
        if CHOO <= t < 35.6:
            if t < CHOO + 0.2:
                fr[M] += light(WHITE, 1.0 * np.exp(-(t - CHOO) / 0.08))
            if t < T_END + 0.05:
                s = blast_s(t)
                core = np.exp(-((frac - s) / 0.035) ** 2)
                fr[:] += light(lerp(WHITE, SPRAY, 0.4), (1 - 0.25 * s) * core)
            age = t - tpass
            sp = drops * (age > 0) * 0.55 * np.exp(-np.clip(age, 0, None) / 0.35)
            fr[:] += light(SPRAY, sp)
            if t >= T_END:
                fr[:] += light(WHITE, np.exp(-(t - T_END) / 0.2) * smoothstep(0.93, 1.0, frac))
        for (tz, _, _), pz in zip(FIZZ, fizz_pd):     # a few bulbs fizzle in the dark
            a2 = t - tz
            if 0 <= a2 < 0.3 and ((a2 < 0.05) or (0.12 <= a2 < 0.17)):
                fr[:] += light(PALE, 0.5 * blob(pz, 6.0))

        # ---- hiccups pop a little burst out of the mouth, both ways ----
        for ab, sc in bursts:
            r = (150 if sc >= 1 else 60) * (1 - np.exp(-ab / 0.15))
            I = 0.75 * sc * (1 - ab / 0.45)
            fr[:] += light(BUBBLE, I * (blob(dM - r, 10.0) + blob(dM + r, 10.0)))

        # ---- the soft exhale when he gives up holding his breath ----
        if EXHALE <= t < EXHALE + 1.3:
            s = (t - EXHALE) / 1.3
            fr[:] += light(lerp(PALE, AIR, 0.5), 0.4 * (1 - s) * np.exp(-((frac - s) / 0.07) ** 2))

        # ---- the tissue ----
        if tp is not None:
            crumpled = t >= TOSS[0]
            w = 11.0 if crumpled else 18.0
            I = 0.8 + 0.3 * hk
            flap = 0 if crumpled else 7 * np.sin(2 * np.pi * 2.2 * t)
            fr[:] += light(TISSUE, I * 0.5 * (blob(tp - flap, w) + blob(tp + flap, w)))
    np.clip(out, 0, 1, out=out)
    return out


# ---------------------------------------------------------------- music ----------------------------------------------
# A comic cue in E minor, the key of The Watcher, so his theremin theme comes back: two theremins (one per eye,
# panned to the pupils) play it slow and woozy while he's groggy, and the ah-ah-AH climbs the rest of it, landing on
# E with the CHOO. Every sound is a moment in render(): the stuffy snores and the snort, a water plip as each drip
# lets go and a slide whistle that falls with it down the porch side (and zips back up when he sniffs), the voice
# on the ahs and the flutter, the deflating fake-out, the blast whooshing out to both ends and the pops there, the
# fizzles, the buzzing lights, the dizzy birds. The harmony moves only on the hiccups, so the music hiccups with
# him. Then the held breath climbs a semitone as his head changes colour, a sad horn, the tissue's flute tune
# panned to where the tissue is, two honks, the toss, E major and a sigh, and one tiny hic.

CHORDS = {'Em': (52, 55, 59), 'Am': (57, 60, 64), 'B7': (51, 54, 57, 59), 'C': (52, 55, 60), 'D': (50, 54, 57),
          'D#o': (51, 54, 57), 'E': (52, 56, 59), 'F': (53, 57, 60), 'G': (55, 59, 62)}
ROOTS = {'Em': 40, 'Am': 45, 'B7': 47, 'C': 36, 'D': 38, 'D#o': 39, 'E': 40, 'F': 41, 'G': 43}
HIC_PROG = ['Em', 'Am', 'B7', 'Em', 'C', 'Am', 'F', 'D#o', 'B7', 'Em', 'Em', 'E']
THEME_KEYS = [(8.8, 'B4'), (12.0, 'B4'), (13.0, 'G4'), (15.0, 'G4'), (16.5, 'C5'), (18.5, 'C5'), (19.5, 'A4'),
              (22.4, 'A4'), (23.7, 'B4'), (24.6, 'B4'), (26.2, 'C5'), (27.1, 'C5'), (29.0, 'D#5'), (30.5, 'D#5'),
              (31.2, 'G4'), (33.0, 'C5'), (33.5, 'D#5'), (33.6, 'E5')]
THEME_AMP = [(8.6, 0), (9.4, 0.8), (21.6, 0.8), (22.4, 0.55), (29.0, 1.0), (30.5, 1.0), (31.3, 0), (33.0, 0),
             (33.3, 1.0), (33.6, 1.0), (33.64, 0)]
VOWELS = {'a': (730, 1090, 2440), 'o': (570, 840, 2410), 'u': (300, 870, 2240), 'e': (530, 1840, 2480),
          'i': (390, 1990, 2550), 'ae': (660, 1720, 2410)}


def _ma(x, w):
    """Centred moving average over w samples."""
    c = np.concatenate([[0.0], np.cumsum(np.concatenate([np.full(w // 2, x[0]), x, np.full(w - w // 2, x[-1])]))])
    return (c[w:w + len(x)] - c[:len(x)]) / w


def _kv(ts, pts):
    return np.array([keys(t, pts) for t in ts], float)


def _stereo(sig, pan):
    """Constant-power pan with a per-sample pan array."""
    a = (np.clip(pan, -1, 1) + 1) * np.pi / 4
    return np.vstack([sig * np.cos(a), sig * np.sin(a)]) * np.sqrt(2)


def _voice(f0, F, amp, rng, growl=0.0):
    """Formant voice by additive synthesis: harmonics of f0 weighted by three resonances F (3, n)."""
    from pixelhome.audio import SR
    n = len(f0)
    jit = np.convolve(rng.normal(0, 1, n), np.ones(400) / 400, 'same') * 0.6
    f = f0 * (1 + 0.02 * jit)
    ph = 2 * np.pi * np.cumsum(f) / SR
    out = np.zeros(n)
    for k in range(1, int(min(60, 5500 / f0.min())) + 1):
        fk = k * f
        a = sum(g / (1 + ((fk - F[i]) / bw) ** 2) for i, (g, bw) in enumerate(((1.0, 90), (0.55, 110), (0.3, 160))))
        out += a * (fk < 6000) * np.sin(k * ph) / k ** 0.3
    if growl:
        out *= 1 + growl * np.sin(ph / 2 + 0.3 * np.sin(ph / 3))
    return out * amp


def _shaped_noise(n, rng, F, width=3.0):
    """Noise through three resonances: breath when F is a vowel, a hiss when F is high."""
    x = np.fft.rfft(rng.normal(0, 1, n))
    f = np.fft.rfftfreq(n, 1 / 48000)
    h = sum(g / (1 + ((f - F[i]) / (bw * width)) ** 2) for i, (g, bw) in enumerate(((1.0, 90), (0.55, 110), (0.3, 160))))
    y = np.fft.irfft(x * h, n)
    return y / (np.abs(y).max() + 1e-9)


def _vowel(f0, env, v0, v1, rng, growl=0.2, h=0.0):
    """A sung vowel with a pitch contour f0 and envelope env (per sample), v0 -> v1, an octave-down growl under it;
    h adds breath at the start."""
    from pixelhome.audio import SR
    n = len(f0)
    u = np.linspace(0, 1, n)
    F = np.array(VOWELS[v0])[:, None] * (1 - u) + np.array(VOWELS[v1])[:, None] * u
    F = F * 0.92
    sig = _voice(f0, F, env, rng, growl) + 0.35 * _voice(f0 / 2, F * 0.85, env, rng, growl * 0.5)
    if h:
        tt = np.arange(n) / SR
        br = _shaped_noise(n, rng, F[:, 0]) * np.exp(-tt / 0.06) * np.clip(tt / 0.005, 0, 1)
        sig += h * 0.6 * br * np.abs(sig).max()
    return sig


def score(M, G):
    from pixelhome.audio import SR, note, whoosh, slide
    n = note
    vrng = np.random.default_rng(1212)
    g = geometry(G)
    L, dM = g['L'], g['dM']

    harp = M.sampler('Strings/Harp/*.wav')
    glock = M.sampler('Percussion/Glock/*.wav', tune=-12)
    pizz = M.sampler('Strings/Cello Section/pizzT/*.wav', tune=-12)
    cb_pizz = M.sampler('Strings/Solo Contrabass/Pizz/*.wav', tune=-12)
    cb_sus = M.sampler('Strings/Solo Contrabass/SusNV/*.wav', tune=-12)
    c_trem = M.sampler('Strings/Cello Section/trem/*.wav', tune=-12)
    v_trem = M.sampler('Strings/Violin Section/Trem/*.wav', tune=-12)
    c_sus = M.sampler('Strings/Cello Section/susvib/*.wav', tune=-12)
    va_sus = M.sampler('Strings/Viola Section/susvib/*.wav', tune=-12)
    v_sus = M.sampler('Strings/Violin Section/susVib/*.wav', tune=-12)
    bsn = M.sampler('Woodwinds/Bassoon/stac/*.wav', tune=-12)
    bsn_s = M.sampler('Woodwinds/Bassoon/sus/*.wav', tune=-12)
    clar = M.sampler('Woodwinds/Clarinet/susLong/*.wav', tune=-12)
    flute = M.sampler('Woodwinds/Flute/stac/*.wav', tune=-12)
    flute_s = M.sampler('Woodwinds/Flute/susvib/*.wav', tune=-12)
    tuba = M.sampler('Brass/Tuba/stac/*.wav', tune=-12)
    tuba_s = M.sampler('Brass/Tuba/sus/*.wav', tune=-12)
    tbn = M.sampler('Brass/OldTrombone/Short/*.wav', tune=-12)
    tbn_b = M.sampler('Brass/OldTrombone/Buzz/*.wav', tune=-12)
    tbn_f = M.sampler('Brass/OldTrombone/Fall/*.wav', tune=-12)
    horn = M.sampler('Brass/F Horn/sus/*.wav', tune=-12)
    horn_s = M.sampler('Brass/F Horn/stac/*.wav', tune=-12)
    horn_m = M.sampler('Brass/F Horn/mute/*.wav', tune=-12)
    timp = M.hits('Percussion/Timpani/Timpani1_Hit_v3*.wav')
    troll = M.hits('Percussion/Timpani/Rolls/*.wav')
    bd = M.hits('VSCO 1 Percussion/drums/bass/bdrum_fff*.wav')
    bd_m = M.hits('VSCO 1 Percussion/drums/bass/bdrum_muted_mp*.wav')
    crash = M.hits('Percussion/cymbal-crash1_ff*.wav')
    crash_p = M.hits('Percussion/cymbal-crash1_pp*.wav')
    cresc = M.hits('Percussion/susCymb1-cresc-Short_v1.wav')
    glass = M.hits('Miscellania Raw/Misc 1/glass_break*.wav')
    zap = M.hits('Miscellania Raw/Misc 1/zap*.wav')
    bubbles = M.hits('Miscellania Raw/Misc 1/bubbles*.wav')
    wood = M.hits('VSCO 1 Percussion/varWood/wood_click*.wav')
    thup = M.hits('Percussion/Tumba-Tap1*.wav')
    flex = M.hits('VSCO 1 Percussion/varMetal/various/flexatone_long*.wav')
    cabasa = M.hits('VSCO 1 Percussion/varMetal/various/cabasa_roll*.wav')

    for name, gain, rev in (('pad', 0.24, 0.35), ('theremin', 0.03, 0.35), ('voice', 0.2, 0.12), ('fx', 0.22, 0.2),
                            ('snore', 0.3, 0.1), ('drip', 0.06, 0.25), ('strings', 0.22, 0.3), ('winds', 0.3, 0.22),
                            ('brass', 0.3, 0.2), ('perc', 0.32, 0.18), ('hit', 0.55, 0.25), ('bass', 0.4, 0.1)):
        M.bus(name, gain=gain, reverb=rev)

    x0, x1 = G.pos[:, 0].min(), G.pos[:, 0].max()

    def pan_x(x):
        return 0.85 * (2 * (np.asarray(x, float) - x0) / (x1 - x0) - 1)

    def pan_d(d):                            # path distance -> pan
        return pan_x(np.interp(d, g['pdp'], g['xp']))

    span = {k: float(pan_x(G.pos[G.seg[k], 0].mean())) for k in G.seg}
    mouth = span['Porch Front']
    eyes = []
    for k in ('Left', 'Right'):
        ex = G.pos[G.seg[k], 0]
        eyes.append(((ex.max() + ex.min()) / 2, (ex.max() - ex.min()) / 2))

    def gate(sig, t0, cuts):
        tt = t0 + np.arange(sig.shape[-1]) / SR
        return sig * np.interp(tt, [c[0] for c in cuts], [c[1] for c in cuts])

    def seg_t(t0, d):
        return np.arange(int(d * SR)) / SR

    pad = []

    # ---- 0-8.4: asleep, snoring through a stuffy nose ----
    pad += [(0.3, n('E2'), 50, 8.2), (0.3, n('B2'), 44, 8.2), (2.0, n('G3'), 36, 6.5)]
    M.add('strings', cb_sus.play(n('E1'), 55, dur=8.0, release=1.0), 0.5, 0.5, -0.1)
    for s in SNORES:
        nn = int(1.6 * SR)
        tt = np.arange(nn) / SR
        env = (tt / 1.6) ** 1.5
        rat = (0.5 + 0.5 * np.sin(2 * np.pi * 34 * tt)) ** 3
        sig = _shaped_noise(nn, vrng, (420.0, 1100.0, 2400.0), 2.0) * rat * env
        sig += 0.5 * _vowel(np.full(nn, 62.0), env * rat, 'o', 'u', vrng, growl=0.6) / 3
        M.add('snore', np.vstack([sig, sig]), s, 0.9, mouth)
        nn = int(1.2 * SR)
        tt = np.arange(nn) / SR
        f = 1500 * 2 ** (-0.6 * tt / 1.2) * (1 + 0.01 * np.sin(2 * np.pi * 6 * tt))
        env = np.sin(np.pi * tt / 1.2) ** 0.7
        wh = np.sin(2 * np.pi * np.cumsum(f) / SR) + 0.6 * _shaped_noise(nn, vrng, (1500.0, 2600.0, 3600.0), 3.0)
        M.add('snore', np.vstack([wh * env, wh * env]) * 0.35, s + 1.7, 0.8, mouth)
        M.add('perc', glock.play(n('B5') if s < 3 else n('G5'), 40), s + 1.7, 0.4, mouth)
    # the snort
    nn = int(0.3 * SR)
    tt = np.arange(nn) / SR
    env = np.clip(tt / 0.02, 0, 1) * np.exp(-tt / 0.12)
    rat = (0.5 + 0.5 * np.sin(2 * np.pi * 52 * tt)) ** 2
    sig = _shaped_noise(nn, vrng, (450.0, 1200.0, 2500.0), 2.5) * rat * env
    sig += _vowel(90 * 2 ** (tt / 0.3 * 7 / 12), env, 'u', 'o', vrng, growl=0.5) / 3
    M.add('snore', np.vstack([sig, sig]), SNORT, 1.4, mouth)
    M.add('hit', timp.play(100, pitch=-4), SNORT, 0.5)
    M.add('winds', bsn.play(n('E2'), 120), SNORT, 1.0, mouth)
    M.add('perc', harp.play(n('E2'), 90), SNORT + 0.2, 0.8, span['Left'])
    M.add('perc', harp.play(n('B2'), 90), SNORT + 0.2, 0.8, span['Right'])

    # ---- 8.6-33.6: his theme on two woozy theremins, one per eye; the ahs climb the rest of it ----
    cr = 200
    tc = np.arange(0, D + 1, 1 / cr)
    t0, t1 = 8.5, 33.7
    tt = np.arange(int(t0 * SR), int(t1 * SR)) / SR
    pitch = np.interp(tt, tc, _kv(tc, [(t, n(m)) for t, m in THEME_KEYS]))
    amp = np.interp(tt, tc, _kv(tc, THEME_AMP))
    amp = _ma(amp, 240)
    gaze = np.interp(tt, tc, _kv(tc, GAZE_KEYS))
    woozy = -0.25 + 0.25 * np.sin(2 * np.pi * 0.3 * tt)
    flut = ((tt >= FLUTTER[0]) & (tt < FLUTTER[1])) * 0.5 * np.sin(2 * np.pi * FLUTTER[2] * tt)
    vib = 0.15 * np.sin(2 * np.pi * 5.2 * tt) + flut
    out = np.zeros((2, len(tt)))
    for (cx, hw), dt in zip(eyes, (-0.06, 0.06)):
        f = 440 * 2 ** ((pitch + woozy + vib + dt - 69) / 12)
        ph = 2 * np.pi * np.cumsum(f) / SR
        out += _stereo(amp * (np.sin(ph) + 0.18 * np.sin(2 * ph) + 0.06 * np.sin(3 * ph)), pan_x(cx + gaze * 0.55 * hw))
    M.add('theremin', out, t0)
    for t, c, dur in ((8.8, 'Em', 4.2), (13.0, 'Em', 3.5), (16.5, 'Am', 3.0), (19.5, 'Am', 2.9)):
        pad += [(t, m - 12, 52, dur) for m in CHORDS[c]]
        M.add('bass', cb_pizz.play(ROOTS[c] - 12, 90), t, 0.8)
    M.add('strings', cb_sus.play(n('E1'), 50, dur=13.0, release=1.0), 9.0, 0.5, -0.1)
    for b, w in BLINKS[:2]:                 # slow heavy blinks
        M.add('perc', thup.play(70, pitch=-6), b - 0.05, 0.6, span['Left'])
        M.add('perc', thup.play(70, pitch=-6), b - 0.05, 0.6, span['Right'])

    # ---- drips: a plip as each lets go, a slide whistle that falls with it (and zips back up on a sniff) ----
    for k, (td, side, tsn) in enumerate(DRIPS):
        cpan = span['Porch Left' if side == 'L' else 'Porch Right']
        M.add('perc', harp.play(n('E5') - 2 * (k % 3), 60), td, 0.35, cpan)
        tstart, tend = td + FORM, td + FORM + RUN + 0.4
        nn = int((tend - tstart) * SR)
        ta = tstart + np.arange(nn) / SR
        tcs = np.arange(tstart, tend, 0.005)
        sv, iv = [], []
        for t in tcs:
            st = drip_state(t, td, tsn)
            if st is None or st[2] is not None:
                sv.append(sv[-1] if sv else 0.0)
                iv.append(0.0)
            else:
                sv.append(st[0])
                iv.append(1.0)
        s_a = np.interp(ta, tcs, sv)
        on = _ma(np.interp(ta, tcs, iv), 240)
        f = 1250 * 2 ** (-1.7 * s_a)
        ph = 2 * np.pi * np.cumsum(f) / SR
        plip = np.sin(2 * np.pi * np.cumsum(700 * 2 ** (np.clip((ta - tstart) / 0.05, 0, 1))) / SR) * \
            np.exp(-(ta - tstart) / 0.04)
        sig = on * (np.sin(ph) + 0.12 * np.sin(2 * ph)) * 0.6 + plip
        M.add('drip', np.vstack([sig, sig]), tstart, 1.0, cpan)
        if tsn is None:                      # splash at the corner of the mouth
            ts = td + FORM + RUN
            M.add('perc', glock.play(n('E5') + (3 if side == 'R' else 0), 70), ts, 0.5, pan_d(g['mL'] if side == 'L' else g['mR']))
            M.add('fx', bubbles.play(70, pitch=4, dur=0.35), ts, 0.35, pan_d(g['mL'] if side == 'L' else g['mR']))
    for s in SNIFFS:                         # sniff: a nasal hiss pulled in, the eyes squint
        nn = int(0.32 * SR)
        tt = np.arange(nn) / SR
        env = np.clip(tt / 0.25, 0, 1) ** 2 * np.clip((0.32 - tt) / 0.07, 0, 1)
        hs = _shaped_noise(nn, vrng, (1700.0, 2900.0, 4200.0), 4.0) * env
        M.add('voice', np.vstack([hs, hs]), s - 0.25, 1.0 if s != 20.0 else 1.4, mouth)
        M.add('bass', pizz.play(n('B2'), 90), s, 0.6, -0.2)

    # ---- 22.4-33.6: ah... ah... AH... (the strings climb under each), the fake-out, then the quick one ----
    def ah(tA, d_up, d_hold, d_rel, p0, p1, gain, flutter=False, fall=0.0):
        d = d_up + d_hold + d_rel
        nn = int(d * SR)
        tt = np.arange(nn) / SR
        p = p0 + (p1 - p0) * np.clip(tt / d_up, 0, 1) ** 0.8 - fall * np.clip((tt - d_up - d_hold) / d_rel, 0, 1)
        if flutter:
            p = p + 0.4 * np.sin(2 * np.pi * FLUTTER[2] * (tA + tt)) * ((tA + tt >= FLUTTER[0]) & (tA + tt < FLUTTER[1]))
        env = (0.25 + 0.75 * np.clip(tt / d_up, 0, 1)) * np.clip(tt / 0.08, 0, 1)
        env *= 1 - np.clip((tt - d_up - d_hold) / d_rel, 0, 1)
        sig = _vowel(220 * 2 ** (p / 12), env, 'a', 'a' if not fall else 'o', vrng, growl=0.15, h=0.8)
        M.add('voice', np.vstack([sig, sig]), tA, gain, mouth)

    ah(22.4, 1.3, 0.3, 0.6, 0, 2, 0.4)
    ah(24.6, 1.6, 0.3, 0.6, 2, 3, 0.5)
    ah(27.1, 1.9, 1.5, 0.5, 3, 6, 0.6, flutter=True, fall=9)
    ah(33.0, 0.5, 0.06, 0.04, 3, 6, 0.7)
    for tA, d, c, v in ((22.4, 2.2, 'Am', 70), (24.6, 2.5, 'B7', 85), (27.1, 3.5, 'B7', 105), (33.0, 0.6, 'B7', 115)):
        for m in CHORDS[c]:
            M.add('strings', gate(c_trem.play(m - 12, v, dur=d, release=0.3), 0, [(0, 0.3), (d * 0.7, 1.0), (99, 1.0)]),
                  tA, 0.7, -0.3)
            M.add('strings', gate(v_trem.play(m + 12, v - 10, dur=d, release=0.3), 0, [(0, 0.2), (d * 0.7, 1.0), (99, 1.0)]),
                  tA, 0.5, 0.3)
        M.add('bass', cb_pizz.play(ROOTS[c] - 12, v + 10), tA, 0.9)
    for i in range(int((FLUTTER[1] - FLUTTER[0]) * FLUTTER[2])):     # the flutter: a mallet on each lid flick
        t = FLUTTER[0] + (i + 0.25) / FLUTTER[2]
        M.add('perc', glock.play(n('D#5') if i % 2 == 0 else n('E5'), 60 + 3 * i), t, 0.45, span['Left' if i % 2 else 'Right'])
    # fake-out: it all deflates; he looks left, right: huh?
    M.add('brass', tbn_f.play(n('B2'), 100), FAKE, 0.8, mouth)
    M.add('fx', slide(0.0, 0.6, 1100, 300, 0.65, 0.35, 0.8), FAKE, 0.7, mouth)
    M.add('winds', bsn.play(n('F#3'), 100), 31.0, 0.9, span['Left'])
    M.add('winds', bsn.play(n('B2'), 100), 32.0, 0.9, span['Right'])
    M.add('hit', troll.play(80, dur=0.65), 33.0, 0.6)
    M.add('hit', gate(cresc.play(100), 0, [(0, 1), (0.6, 1), (0.63, 0), (99, 0)]), 33.0, 0.5)

    # ---- 33.6: CHOO. The blast whooshes out to both ends, which pop; the house goes dark ----
    nn = int(0.12 * SR)
    ch = _shaped_noise(nn, vrng, (2500.0, 3600.0, 4800.0), 5.0) * np.exp(-np.arange(nn) / SR / 0.05)
    M.add('voice', np.vstack([ch, ch]), CHOO - 0.04, 1.6, mouth)
    nn = int(0.5 * SR)
    tt = np.arange(nn) / SR
    sig = _vowel(220 * 2 ** ((7 - 6 * tt / 0.5) / 12), np.clip(tt / 0.02, 0, 1) * np.exp(-tt / 0.2), 'u', 'u', vrng,
                 growl=0.35, h=0.5)
    M.add('voice', np.vstack([sig, sig]), CHOO + 0.04, 1.4, mouth)
    M.add('hit', crash.play(127), CHOO, 0.9)
    M.add('hit', bd.play(127), CHOO, 1.0)
    M.add('hit', timp.play(127, pitch=-5), CHOO, 0.9)
    for m in CHORDS['Em']:
        M.add('brass', tbn.play(m - 12, 127), CHOO, 1.0, -0.3)
        M.add('brass', horn_s.play(m, 120), CHOO, 0.9, 0.3)
    M.add('bass', tuba.play(n('E1'), 127), CHOO, 1.0)
    M.add('bass', tuba.play(n('E2'), 127), CHOO, 0.7)
    nn = int((BLAST + 0.1) * SR)
    ta = CHOO + np.arange(nn) / SR
    s = np.array([blast_s(t) for t in ta])
    for side, seed in (('L', 21), ('R', 22)):
        d = dM - s * dM if side == 'L' else dM + s * (L - dM)
        w = whoosh(BLAST + 0.1, 3500, 600, 0.9, seed=seed)[0]
        M.add('fx', _stereo(w, pan_d(d)), CHOO, 1.0)
    for p in (pan_d(0.0), pan_d(L)):          # the ends pop
        M.add('hit', glass.play(120), T_END, 0.55, float(p))
        M.add('fx', zap.play(110), T_END + 0.03, 0.5, float(p))
    M.add('hit', timp.play(110, pitch=-9), T_END, 0.6)
    M.add('strings', cb_pizz.play(n('E1'), 120), T_END, 0.9)
    for (tz, k, off), _ in zip(FIZZ, range(3)):
        x = G.pos[G.seg[k], 0]
        M.add('fx', zap.play(70, pitch=-3), tz, 0.25, float(pan_x(x.mean() + off * (x.max() - x.min()) / 2)))

    # ---- 36-38.7: the lights buzz back on, the eyes open crossed; little dizzy birds go round ----
    nn = int(1.2 * SR)
    ta = 36.0 + np.arange(nn) / SR
    gsp = _ma(np.array([sputter(t) for t in ta]), 96)
    hum = sum(np.sin(2 * np.pi * 100 * k * ta) / k for k in range(1, 9))
    M.add('fx', _stereo(hum * gsp * np.clip((37.2 - ta) / 0.4, 0, 1) * 0.25, np.full(nn, span['Side'] * 0.5)), 36.0, 1.0)
    birds = ['E5', 'G5', 'B5', 'G5']
    for i in range(12):
        t = DAZED[0] + 0.17 * i
        M.add('perc', glock.play(n(birds[i % 4]), 55), t, 0.5, float(0.6 * np.sin(2 * np.pi * 0.9 * (t - DAZED[0]))))
    M.add('fx', flex.play(70, dur=2.0), DAZED[0], 0.3, 0.0)
    M.add('perc', harp.play(n('E3'), 80), 37.0, 0.6, span['Left'])
    M.add('perc', harp.play(n('B3'), 80), 37.0, 0.6, span['Right'])

    # ---- 38.9-50: the hiccups; the harmony only moves when he hics ----
    def hic(th, sc, k, full=True):
        nn = int(0.1 * SR)
        tt = np.arange(nn) / SR
        env = np.clip(tt / 0.006, 0, 1) * np.exp(-tt / 0.035)
        p = (5 + 4 * tt / 0.1) + (k % 3) - 1
        sig = _vowel(330 * 2 ** (p / 12) * (1.3 if sc < 1 else 1), env, 'i', 'i', vrng, growl=0.1, h=1.2)
        M.add('voice', np.vstack([sig, sig]), th - 0.01, 1.5 * sc, mouth)
        M.add('fx', slide(0.0, 0.09, 700, 1500 + 200 * (k % 3), 0.1, 0.35, 0.5), th, 0.6 * sc, mouth)
        M.add('perc', wood.play(100), th, 0.6 * sc, mouth)
        for p in (pan_d(dM - 120 * sc), pan_d(dM + 120 * sc)):    # the burst flies out both ways
            M.add('perc', glock.play(n('B5') + (k % 2) * 2, 60), th + 0.12, 0.35 * sc, float(p))

    hic_t = [h for h, _ in HICS]
    for k, (th, sc) in enumerate(HICS):
        hic(th, sc, k)
        c = HIC_PROG[k]
        if k >= 10:
            continue
        nxt = hic_t[k + 1] if k + 1 < 10 else 50.4
        dur = nxt - th
        for m in CHORDS[c]:
            M.add('strings', pizz.play(m - 12, 105), th, 0.6, -0.3)
        M.add('bass', tuba.play(ROOTS[c], 110), th, 0.8)
        M.add('winds', clar.play(CHORDS[c][1] + 12, 70, dur=dur, release=0.08), th + 0.05, 0.35, 0.25)
        M.add('winds', bsn_s.play(ROOTS[c] + 12, 70, dur=dur, release=0.08), th + 0.05, 0.3, -0.25)

    # ---- 50.4-56: deep breath, hold it! The strings climb a semitone each time his head changes colour ----
    w = whoosh(1.0, 2500, 400, 0.6, seed=31)
    M.add('fx', w, 50.4, 0.6, mouth)
    M.add('hit', bd_m.play(90), HOLD[0], 0.6, mouth)
    M.add('brass', horn_m.play(n('E3'), 90, dur=0.2), HOLD[0], 0.6, mouth)
    for t, r, dd in ((51.6, 0, 1.5), (53.1, 1, 1.4), (54.5, 2, 0.95), (55.45, 3, 0.55)):
        for m in (n('E3') + r, n('B3') + r):
            M.add('strings', c_trem.play(m, 85 + 10 * r, dur=dd + 0.05, release=0.05), t, 0.7, -0.2)
        M.add('strings', v_trem.play(n('E5') + r, 75 + 10 * r, dur=dd + 0.05, release=0.05), t, 0.45, 0.2)
    M.add('hit', gate(troll.play(90, dur=4.5), 0, [(0, 0.3), (4.3, 1.0), (4.45, 0), (99, 0)]), 51.6, 0.6)
    for th in MUFFLED:                       # muffled hics: thumps behind closed lips
        M.add('hit', bd_m.play(110), th, 0.8, mouth)
        nn = int(0.09 * SR)
        tt = np.arange(nn) / SR
        sig = _vowel(np.full(nn, 140.0), np.clip(tt / 0.01, 0, 1) * np.exp(-tt / 0.03), 'u', 'u', vrng, growl=0.3)
        M.add('voice', np.vstack([sig, sig]), th, 0.6, mouth)
    # 56: can't hold it, PWAAH
    nn = int(1.2 * SR)
    tt = np.arange(nn) / SR
    sig = _vowel(200 * 2 ** (-7 * tt / 1.2 / 12), np.clip(tt / 0.03, 0, 1) * np.exp(-tt / 0.45), 'a', 'o', vrng,
                 growl=0.2, h=1.6)
    M.add('voice', np.vstack([sig, sig]), EXHALE, 1.1, mouth)
    M.add('brass', tbn_f.play(n('E3'), 110), EXHALE, 0.7, mouth)
    M.add('hit', crash_p.play(100), EXHALE, 0.6)
    M.add('fx', whoosh(1.3, 500, 2500, 0.5, seed=33), EXHALE, 0.6)
    pad += [(EXHALE, m - 12, 60, 1.4) for m in CHORDS['Em']]
    # 57.4 hic again; a sad muted horn
    for i, m in enumerate(('D4', 'C#4', 'C4', 'B3')):
        M.add('brass', horn_m.play(n(m), 95, dur=0.25 if i < 3 else 0.7, release=0.1), 57.75 + 0.3 * i, 0.8, mouth)

    # ---- 58.5-64.3: a tissue flutters in from the right end; the flute follows it; HONK, HOOONK ----
    tune = ['B4', 'E5', 'G#5', 'F#5', 'E5', 'C#5', 'B4', 'E5']
    for i, m in enumerate(tune):
        t = TISSUE_IN[0] + 0.3 + 0.42 * i
        p = float(pan_d(tissue_pd(t, L, dM)))
        M.add('winds', flute.play(n(m), 90), t, 0.8, p)
    for i in range(8):
        t = TISSUE_IN[0] + 0.05 * i
        M.add('perc', harp.play(n('E4') + (0, 4, 7, 11, 12, 16, 19, 24)[i], 70), t, 0.5, span['Right'])
    for t, c in ((58.8, 'E'), (59.64, 'E'), (60.48, 'B7'), (61.32, 'E')):
        for j, m in enumerate(CHORDS[c]):
            M.add('perc', harp.play(m - 12, 65), t + 0.12 * j, 0.5, 0.3)
    pad += [(58.8, m - 12, 48, 3.3) for m in CHORDS['E']]
    for (th, d), pitch in zip(HONKS, (n('Bb2'), n('A2'))):
        nn = int((d + 0.12) * SR)
        tt = np.arange(nn) / SR
        env = np.clip(tt / 0.04, 0, 1) * np.clip((d + 0.12 - tt) / 0.12, 0, 1)
        f0 = 440 * 2 ** ((pitch + 12 - 69) / 12) * (1 - 0.08 * tt / d + 0.02 * np.sin(2 * np.pi * 9 * tt))
        sig = _vowel(f0, env, 'ae', 'ae', vrng, growl=0.9)
        M.add('voice', np.vstack([sig, sig]), th, 1.0, mouth)
        M.add('brass', tbn_b.play(pitch, 120, dur=d, release=0.1), th, 0.9, mouth)
        M.add('bass', tuba_s.play(pitch - 12, 110, dur=d, release=0.1), th, 0.8)
        M.add('hit', timp.play(100, pitch=-6), th, 0.5)
    M.add('fx', cabasa.play(90, dur=1.0), HONKS[1][0], 0.5, 0.0)
    M.add('hit', crash_p.play(90), HONKS[1][0], 0.4)
    # the toss: off the right end
    nn = int((TOSS[1] - TOSS[0]) * SR)
    ta = TOSS[0] + np.arange(nn) / SR
    w = whoosh(TOSS[1] - TOSS[0], 600, 3000, 0.7, seed=41)[0]
    M.add('fx', _stereo(w, pan_d(np.array([tissue_pd(t, L, dM) for t in ta]))), TOSS[0], 0.8)
    M.add('fx', slide(0.0, 0.6, 500, 1400, 0.65, 0.3, 0.6), TOSS[0], 0.5, 0.5)
    M.add('perc', wood.play(70), TOSS[1], 0.5, 0.85)
    M.add('perc', glock.play(n('E5'), 50), TOSS[1] + 0.05, 0.4, 0.85)

    # ---- 65.4-69.6: relief. E major, a sigh, his theme on the clarinet in the major ----
    for i, m in enumerate(('E3', 'G#3', 'B3', 'E4', 'G#4', 'B4')):
        M.add('perc', harp.play(n(m), 85), 65.4 + 0.08 * i, 0.6, -0.2 + 0.08 * i)
    for smp, ms, v, p in ((c_sus, ('E2', 'B2'), 75, -0.3), (va_sus, ('G#3', 'B3'), 70, 0.0), (v_sus, ('E4', 'G#4'), 65, 0.3)):
        for m in ms:
            M.add('strings', gate(smp.play(n(m), v, dur=4.2, release=0.04), 0, [(0, 0), (0.8, 1), (99, 1)]), 65.4, 0.6, p)
    for m in ('E3', 'B3'):
        M.add('brass', gate(horn.play(n(m), 70, dur=4.2, release=0.04), 0, [(0, 0), (1.0, 1), (99, 1)]), 65.4, 0.5, 0.0)
    nn = int(2.2 * SR)
    tt = np.arange(nn) / SR
    sig = _vowel(160 * 2 ** ((4 - 7 * tt / 2.2) / 12), np.sin(np.pi * tt / 2.2) ** 0.8, 'a', 'o', vrng, growl=0.1, h=1.5)
    M.add('voice', np.vstack([sig, sig]) * 0.6, SIGH[0], 1.0, mouth)
    theme = [(66.2, 'B4', 0.55), (66.8, 'G#4', 0.55), (67.4, 'C#5', 0.55), (68.0, 'A4', 0.55), (68.6, 'D#5', 0.4),
             (69.0, 'E5', 0.6)]
    for t, m, d in theme:
        M.add('winds', clar.play(n(m), 85, dur=min(d, 69.6 - t), release=0.05), t, 0.8, 0.1)
    pad += [(65.4, m - 12, 60, 4.2) for m in CHORDS['E']]
    # 69.6: one tiny hic, and everything stops
    M.add('perc', glock.play(n('E6'), 70), 69.6, 0.5, mouth)
    M.add('bass', pizz.play(n('E3'), 100), 69.6, 0.5)
    # glances left and right, a blink, a little button
    M.add('winds', bsn.play(n('E3'), 100), 70.6, 0.9, span['Left'])
    M.add('winds', bsn.play(n('D#3'), 100), 71.6, 0.9, span['Right'])
    for k in ('Left', 'Right'):
        M.add('perc', thup.play(80, pitch=-4), BLINKS[-1][0] - 0.03, 0.6, span[k])
    M.add('perc', harp.play(n('E4'), 70), BLINKS[-1][0] + 0.1, 0.6, span['Left'])
    M.add('perc', harp.play(n('B4'), 65), BLINKS[-1][0] + 0.16, 0.5, span['Right'])
    for j, m in enumerate(('E3', 'G#3', 'B3', 'E4')):
        M.add('perc', harp.play(n(m), 75), 73.2 + 0.06 * j, 0.6)
    M.add('bass', cb_pizz.play(n('E1'), 100), 73.2, 0.9)
    M.add('bass', tuba.play(n('E2'), 90), 73.2, 0.6)
    pad += [(73.2, m - 12, 50, 2.6) for m in CHORDS['E']]

    padsig = M.synth('Pads/Ghost Pad').render(pad, D)
    M.add('pad', gate(padsig, 0, [(0, 1), (CHOO, 1), (CHOO + 0.03, 0), (EXHALE - 0.02, 0), (EXHALE, 1), (57.6, 1), (58.0, 0), (58.6, 0), (58.8, 1), (69.6, 1), (69.63, 0),
                                  (73.1, 0), (73.2, 1), (99, 1)]), 0.0)
