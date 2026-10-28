"""Parade: Giant balloons float through the house in true 3-D. The roofline is a flat slice at one
height, so each balloon shows as its cross-section: a big ribbed pumpkin rolls along the front of the
wings (its ribs turn as it spins, and it shrinks and swells as it bobs up and down through the roof
plane); an ear of corn comes down the Side like a street, turns the corner and cuts across the porch
sides at mid-depth; a turkey with a fanned tail waddles along the Porch Front, stops in the middle,
over-inflates and pops. Its head, untied, zips off around the corner and out the end of the roof."""
import numpy as np
from pixelhome.fx import DT, hexc, light, keys, smoothstep, lerp, Flicker, nframes

CODE = 'TG04'
TITLE = 'Parade'
KIND = 'show'
DESCRIPTION = ('Giant parade balloons float through the house in 3-D: a spinning pumpkin, an ear of corn that turns '
               'the corner, and a turkey that over-inflates in front of the porch and pops.')

PUMPKIN = hexc('#ff5200')
AMBER = hexc('#ff8a18')
GOLD = hexc('#ffb000')
CRANBERRY = hexc('#c0102a')
WARM = hexc('#ffc27a')
BROWN = hexc('#8a3208')
DEEP = hexc('#4a1604')
D = 64.0
Y = 150.0
TP0, TP1, PX0, PV, PBOB = 1.5, 26, -1050, 92, 5.5     # pumpkin: launch, gone, start x, speed, bob period
TC0, TC1, CV = 15, 42, 88                              # corn: launch, gone, speed along its route
TT0, WADDLE, TSTOP, TPOP = 32, 1.4, 49, 55.05          # turkey: enters, waddle period, stops, pops
GOBBLE, TBOB = 2.2, 3.2                                # head-bob and body-bob periods
SWELL = [(49.5, 150), (51, 175), (52, 175), (53.6, 260), (54, 255), (55.05, 330)]   # body radius
POP_D, RUN = 1486, 1150                                # the pop on the path, and how far the head runs


def ball(P, c, R, soft=7.0):
    """Shading of a sphere's slice: thick in the middle, thin at the rim, anti-aliased edge."""
    d = np.linalg.norm(P - c, axis=1)
    chord = np.sqrt(np.clip(1 - (d / R) ** 2, 0, 1))
    edge = np.clip((R - d) / soft, 0, 1)
    return edge * (0.3 + 0.7 * chord), d


def path_point(pts, s):
    """Point and unit tangent at arc length s along an open polyline route."""
    seg = np.diff(pts, axis=0)
    ln = np.linalg.norm(seg, axis=1)
    cum = np.concatenate([[0], np.cumsum(ln)])
    s = np.clip(s, 0, cum[-1] - 1e-6)
    i = int(np.searchsorted(cum, s, side='right') - 1)
    u = (s - cum[i]) / ln[i]
    return pts[i] + u * seg[i], seg[i] / ln[i], cum[-1]


def corn_route():
    """The corn's route: down the Side, round the corner, across the middle depth."""
    ang = np.linspace(np.pi, np.pi / 2, 8)                 # a rounded corner, radius 110
    corner = np.stack([-486 + 110 * np.cos(ang), np.full(8, Y), -470 + 110 * np.sin(ang)], 1)
    return np.vstack([[(-596, Y, -1150)], corner, [(1100, Y, -360)]])


def turkey_x(t):
    return keys(t, [(TT0, -1000), (TSTOP, -30), (TSTOP + 1, -12)]) if t < TSTOP + 1 else -12.0


def head_s(u):
    """Path distance of the untied head u seconds after the pop."""
    return POP_D + RUN * smoothstep(0.2, 6.0, u) + 45 * np.sin(2 * np.pi * 1.7 * u) * (u < 5.5)


def confetti(G, rng):
    p = rng.uniform(0, G.length, 140)
    return p, TPOP + np.abs(p - POP_D) / 1400 + rng.uniform(0, 0.4, 140), rng.integers(0, 5, 140)


def render(G, seed=24):
    rng = np.random.default_rng(seed)
    F = nframes(D)
    out = np.zeros((F, G.N, 3))
    n = G.N
    P = G.pos[G.path].copy()
    P[:, 1] = Y
    pdp = G.pd[G.path]
    crowd = Flicker(rng, n, 0.2, 1.0)
    conf_p, conf_t, conf_k = confetti(G, rng)
    conf_c = [GOLD, CRANBERRY, WARM, PUMPKIN, AMBER]
    route = corn_route()

    for f in range(F):
        t = f * DT
        buf = np.zeros((n, 3))
        street = keys(t, [(0, 0), (2.5, 0.09), (61, 0.09), (64, 0)])
        buf += light(DEEP, street * (1 + 0.25 * crowd(t)))

        # 1. the pumpkin: ribbed, spinning, bobbing through the roof plane
        if TP0 < t < TP1:
            u = t - TP0
            c = np.array([PX0 + PV * u, Y + 70 * np.sin(2 * np.pi * u / PBOB), -178.0])
            I, d = ball(P, c, 215)
            phi = np.arctan2(P[:, 2] - c[2], P[:, 0] - c[0])
            rib = 0.62 + 0.38 * np.cos(10 * phi + 0.9 * u) ** 2
            hl = np.exp(-np.sum((P - (c + np.array([-60, 60, 110]))) ** 2, 1) / 90 ** 2)
            buf += light(PUMPKIN, 0.95 * I * rib) + light(GOLD, 0.45 * hl * (I > 0))
            # a stem on top shows only when the balloon dips low enough
            sc = c + np.array([0, 205, 0])
            Is, _ = ball(P, sc, 40)
            buf += light(BROWN, 0.7 * Is)

        # 2. the corn: a capsule oriented along its route, kernels in a grid
        if TC0 < t < TC1:
            s = (t - TC0) * CV
            c, tan, total = path_point(route, s)
            a, b = c - tan * 150, c + tan * 150
            ab = b - a
            w = np.clip(((P - a) @ ab) / (ab @ ab), 0, 1)
            near = a + w[:, None] * ab
            d = np.linalg.norm(P - near, axis=1)
            R = 70 * (0.55 + 0.45 * np.sin(np.pi * w) ** 0.5)               # tapered cob
            bob = 18 * np.sin(2 * np.pi * t / 4.0)
            R = np.sqrt(np.clip(R ** 2 - bob ** 2, 0, None))
            inside = np.clip((R - d) / 6, 0, 1)
            chord = np.sqrt(np.clip(1 - (d / np.maximum(R, 1)) ** 2, 0, 1))
            along = w * 300
            side = np.arctan2(*(P - near)[:, [2, 0]].T)
            kern = (0.5 + 0.5 * np.sin(along * 0.21)) * (0.5 + 0.5 * np.sin(side * 7 + 1.3 * t))
            I = inside * (0.35 + 0.65 * chord) * (0.55 + 0.45 * kern)
            buf += light(GOLD, 0.95 * I)
            # husk leaves trailing behind
            hk = c - tan * 215
            Ih, _ = ball(P, hk, 60)
            buf += light(AMBER, 0.45 * Ih)

        # 3. the turkey: body, head, a tail fan in the vertical plane, along the Porch Front
        if TT0 < t < TPOP:
            u = t - TT0
            x = turkey_x(t)
            waddle = 10 * np.sin(2 * np.pi * u / WADDLE) * (t < TSTOP)
            Rb = keys(t, SWELL)
            c = np.array([x, Y + 25 * np.sin(2 * np.pi * u / TBOB), -560.0 + waddle])
            I, _ = ball(P, c, Rb)
            strain = smoothstep(52, 55, t)
            body = light(lerp(BROWN, PUMPKIN, strain), 0.9 * I) + light(WARM, 0.5 * strain * I ** 3 *
                                                                        (0.5 + 0.5 * np.sin(30 * t)))
            buf += body
            gob = 25 * max(0, np.sin(2 * np.pi * u / GOBBLE)) ** 6
            hc = c + np.array([Rb * 0.85 + 35 + gob, 70, 0])
            Ih, _ = ball(P, hc, 62)
            buf += light(CRANBERRY, 0.95 * Ih)
            fan = [GOLD, AMBER, CRANBERRY, PUMPKIN, GOLD, AMBER, CRANBERRY]
            for k, ang in enumerate(np.linspace(-1.2, 1.2, 7)):
                fc = c + np.array([-np.cos(ang) * Rb * 1.15, np.sin(ang) * Rb * 1.15, 0])
                If, _ = ball(P, fc, 0.55 * Rb * (1 - 0.3 * strain))
                buf += light(fan[k], 0.75 * If * (1 - 0.6 * strain))

        # 4. POP: a flash, a ring, confetti; the untied head zips off around the corner
        if t >= TPOP:
            u = t - TPOP
            dist = np.abs(pdp - POP_D)
            buf += light(WARM, 0.95 * np.exp(-u / 0.09) * np.exp(-(dist / 500) ** 2))
            buf += light(GOLD, 0.8 * np.exp(-((dist - 1500 * u) / 60) ** 2) * np.exp(-u / 0.7))
            live = (t > conf_t) & (t < conf_t + 2.2)
            for k in np.where(live)[0]:
                v = t - conf_t[k]
                tw = 0.5 + 0.5 * np.cos(2 * np.pi * (3 + k % 3) * v) ** 2
                buf += light(conf_c[conf_k[k]], 0.75 * tw * np.exp(-v / 0.9) *
                             np.exp(-((pdp - conf_p[k] - 20 * v) / 3.5) ** 2))
            # head: pfffft, zig-zagging along the path from the porch to the right free end
            s = head_s(u)
            hv = keys(t, [(TPOP, 0.9), (60, 0.9), (61.5, 0)])
            buf += light(CRANBERRY, hv * np.exp(-((pdp - s) / 14) ** 2))
            for k in range(6):                                     # puffs of air behind it
                sk = POP_D + RUN * smoothstep(0.2, 6.0, u - 0.08 * (k + 1))
                buf += light(WARM, 0.22 * hv * (1 - k / 6) * np.exp(-((pdp - sk + 8 * k) / 6) ** 2))
        out[f][G.path] = buf
    return out


# ---------------------------------------------------------------- music ----------------------------------------------
# A street brass band in 6/8, Bb major, one bar to the turkey's waddle (dotted crotchet 0.7 s): tuba oom on 1 and 4,
# horns pah on the afterbeats, marching snare and bass drum, trumpets and glock on the tune. Each balloon has its own
# motif, panned to where it lights the roof: the pumpkin a spinning marimba roll, the corn a clarinet strain in F that
# walks down the Side (a slide whistle round the corner, a bump at each porch side it cuts across), the turkey a trio
# in Eb with bassoon gobbles and log-drum footsteps. The band halts when he stops, a whistle follows his radius as he
# swells (hiccup included), the pop is a full hit and a raspberry that chases his head off the end of the roof; then
# the band picks back up for the last two bars.

T0 = TT0 - WADDLE * ((TT0 - TP0) // WADDLE)     # the band's bar 1: a whole number of waddles before the turkey
E = WADDLE / 6                                  # an eighth
CH = {'Bb': (58, 62, 65), 'Eb': (58, 63, 67), 'F': (57, 60, 65), 'C7': (55, 58, 64), 'Gm': (58, 62, 67),
      'Bb7': (56, 62, 65), 'Ab': (56, 60, 63), 'C': (55, 60, 64)}
BASS = {'Bb': (34, 41), 'Eb': (39, 34), 'F': (41, 36), 'C7': (36, 43), 'Gm': (43, 38), 'Bb7': (34, 41),
        'Ab': (44, 39), 'C': (36, 43)}
# tunes: per bar, (eighth, note, eighths)
TUNE_A = [[(0, 'Bb4', 2), (2, 'F4', 1), (3, 'Bb4', 1), (4, 'C5', 1), (5, 'D5', 1)],
          [(0, 'Eb5', 2), (2, 'D5', 1), (3, 'C5', 3)],
          [(0, 'D5', 2), (2, 'Bb4', 1), (3, 'G4', 1), (4, 'A4', 1), (5, 'Bb4', 1)],
          [(0, 'C5', 3), (3, 'F4', 3)],
          [(0, 'Bb4', 2), (2, 'F4', 1), (3, 'Bb4', 1), (4, 'D5', 1), (5, 'F5', 1)],
          [(0, 'G5', 2), (2, 'F5', 1), (3, 'Eb5', 1), (4, 'D5', 1), (5, 'C5', 1)],
          [(0, 'D5', 2), (2, 'Eb5', 1), (3, 'C5', 2), (5, 'A4', 1)],
          [(0, 'Bb4', 3), (3, 'F4', 1), (4, 'Bb4', 2)]]
CHORDS_A = ['Bb', 'Eb', 'Bb', 'F', 'Bb', 'Eb', 'F', 'Bb']
TUNE_B = [[(0, 'C5', 1), (1, 'A4', 1), (2, 'F4', 1), (3, 'C5', 1), (4, 'A4', 1), (5, 'F4', 1)],
          [(0, 'G4', 2), (2, 'A4', 1), (3, 'Bb4', 2), (5, 'G4', 1)],
          [(0, 'A4', 1), (1, 'F4', 1), (2, 'C4', 1), (3, 'A4', 1), (4, 'F4', 1), (5, 'C4', 1)],
          [(0, 'D4', 2), (2, 'E4', 1), (3, 'F4', 3)],
          [(0, 'D5', 1), (1, 'Bb4', 1), (2, 'G4', 1), (3, 'D5', 1), (4, 'Bb4', 1), (5, 'G4', 1)],
          [(0, 'C5', 2), (2, 'A4', 1), (3, 'F4', 2), (5, 'A4', 1)],
          [(0, 'G4', 2), (2, 'Bb4', 1), (3, 'E4', 2), (5, 'G4', 1)],
          [(0, 'F4', 3), (3, 'C5', 3)]]
CHORDS_B = ['F', 'C7', 'F', 'C', 'Gm', 'F', 'C7', 'F']
TUNE_T = [[(0, 'Bb4', 2), (2, 'G4', 1), (3, 'Eb4', 2), (5, 'G4', 1)],
          [(0, 'Bb4', 2), (2, 'C5', 1), (3, 'Bb4', 3)],
          [(0, 'Ab4', 2), (2, 'F4', 1), (3, 'D4', 2), (5, 'F4', 1)],
          [(0, 'Ab4', 2), (2, 'Bb4', 1), (3, 'Ab4', 2), (5, 'G4', 1)],
          [(0, 'G4', 2), (2, 'Eb4', 1), (3, 'G4', 1), (4, 'Bb4', 1), (5, 'Eb5', 1)],
          [(0, 'D5', 2), (2, 'C5', 1), (3, 'Bb4', 2), (5, 'Ab4', 1)],
          [(0, 'G4', 2), (2, 'F4', 1), (3, 'Bb4', 2), (5, 'D4', 1)],
          [(0, 'Eb4', 3), (3, 'Bb3', 3)]]
CHORDS_T = ['Eb', 'Eb', 'Bb7', 'Bb7', 'Eb', 'Bb7', 'Bb7', 'Eb']
CLIMB = [(i, m, 1) for i, m in enumerate(('Eb4', 'F4', 'G4', 'Ab4', 'A4', 'Bb4'))]
PLAN = ['Bb'] * 2 + CHORDS_A + ['Bb', 'C7'] + CHORDS_B + ['Bb7'] + CHORDS_T + CHORDS_T[4:7] + ['Eb']


def score(M, G):
    from pixelhome.audio import SR, note
    n = note
    tpt = M.sampler('Brass/Trumpet/stac/*.wav', tune=-12)
    tpt_s = M.sampler('Brass/Trumpet/sus/*.wav', tune=-12)
    horn = M.sampler('Brass/F Horn/stac/*.wav', tune=-12)
    horn_s = M.sampler('Brass/F Horn/sus/*.wav', tune=-12)
    bone = M.sampler('Brass/Tenor Trombone/sus/*.wav', tune=-12)
    tuba = M.sampler('Brass/Tuba/stac/*.wav', tune=-12)
    tuba_s = M.sampler('Brass/Tuba/sus/*.wav', tune=-12)
    glock = M.sampler('Percussion/Glock/*.wav', tune=-12)
    mar = M.sampler('Percussion/Marimba/*.wav', tune=-12)
    xylo = M.sampler('Percussion/Xylo/*.wav', tune=-12)
    clar = M.sampler('Woodwinds/Clarinet/stac/*.wav', tune=-12)
    bsn = M.sampler('Woodwinds/Bassoon/stac/*.wav', tune=-12)
    trem = M.sampler('Strings/Cello Section/trem/*.wav', tune=-12)
    snare = M.hits('VSCO 1 Percussion/drums/snare/drum3_marching/snare3_[fmp]*.wav')
    snare_f = M.hits('VSCO 1 Percussion/drums/snare/drum3_marching/snare3_f*.wav')
    rim = M.hits('VSCO 1 Percussion/drums/snare/drum3_marching/snare3_rimshot*.wav')
    sroll = M.hits('Percussion/Snare2-rollSN_v[35]*.wav')
    bd = M.hits('VSCO 1 Percussion/drums/bass/bdrum_f_*.wav')
    bd_ff = M.hits('VSCO 1 Percussion/drums/bass/bdrum_fff_*.wav')
    clash = M.hits('VSCO 1 Percussion/varMetal/Cymbals/clash/crash_hit_ff*.wav')
    clash_f = M.hits('VSCO 1 Percussion/varMetal/Cymbals/clash/crash_hit_fff*.wav')
    choke = M.hits('Percussion/cymbal-crashshort*.wav')
    ccresc = M.hits('Percussion/susCymb1-cresc-Short*.wav')
    timp = M.hits('Percussion/Timpani/Timpani1_Hit*.wav')
    troll = M.hits('Percussion/Timpani/Rolls/Timpani1_Roll*.wav')
    wood = M.hits('VSCO 1 Percussion/varWood/claves_m*.wav')
    log = M.hits('Percussion/LogDrum*_MedM_v2*.wav')
    slap = M.hits('VSCO 1 Percussion/varWood/slapstick[0-9].wav')
    fall = M.hits('Brass/OldTrombone/Fall/Trombone_Fall_F2*.wav')
    tri = M.hits('Percussion/Triangle3-Hit_v1*.wav')

    for name, gain, rev in (('tune', 0.24, 0.18), ('horns', 0.17, 0.2), ('bass', 0.32, 0.06), ('drums', 0.24, 0.12),
                            ('motif', 0.26, 0.2), ('perc', 0.32, 0.12), ('fx', 0.21, 0.2), ('hold', 0.16, 0.3)):
        M.bus(name, gain=gain, reverb=rev)

    P = G.pos[G.path].copy()
    P[:, 1] = Y
    pdp = G.pd[G.path]
    order = np.argsort(G.pd)
    xs, ds = G.pos[order, 0], G.pd[order]
    x0, x1 = xs.min(), xs.max()

    def pan_at(d):                          # path distance -> left/right across the facade, as seen from the street
        x = np.interp(d, ds, xs)
        return 0.85 * (2 * (x - x0) / (x1 - x0) - 1)

    def lit(I):                             # how much of the roof a balloon lights, and the pan of where
        w = float(I.sum())
        return w, float(pan_at((I * pdp).sum() / w)) if w > 1e-6 else 0.0

    def at(k, e=0.0):                       # bar k, eighth e
        return T0 + k * WADDLE + e * E

    def mono(sig, pans):                    # a mono signal panned sample by sample
        a = (np.clip(pans, -1, 1) + 1) * np.pi / 4
        return np.vstack([sig * np.cos(a), sig * np.sin(a)]) * np.sqrt(2)

    def tone(f, amp, buzz=0.12):            # a whistle (or a raspberry, with buzz up) at frequency curve f
        ph = 2 * np.pi * np.cumsum(f) / SR
        noise = np.convolve(M.rng.normal(0, 1, len(f)), np.ones(24) / 24, 'same')
        sig = np.sin(ph) + buzz * np.sin(2 * ph) + 0.6 * buzz * np.sin(3 * ph) + 0.08 * noise * (1 + np.sin(ph))
        return amp * sig

    def tune(bars, k0, inst, bus='tune', vel=100, pan=0.0, long=None, gain=1.0):
        for j, b in enumerate(bars):
            for e, m, ln in b:
                pl = long if (long is not None and ln >= 2) else inst
                M.add(bus, pl.play(n(m), vel, dur=ln * E * 0.92), at(k0 + j, e), gain,
                      pan(at(k0 + j, e)) if callable(pan) else pan)

    # ---- the band: oom-pah and drums from bar 0 to the halt, then again for the last two bars ----
    r = sroll.play(90, dur=T0 - 0.6)                            # the snare rolls in out of the dark
    M.add('drums', r * np.linspace(0.2, 1, r.shape[1]) ** 2, 0.6, 0.8)
    nbar = len(PLAN)
    for k, c in enumerate(PLAN):
        big = 1.15 if k >= nbar - 4 else 1.0
        for e in (0, 3):
            M.add('bass', tuba.play(BASS[c][e // 3], 100 if e == 0 else 88), at(k, e), big)
            M.add('drums', bd.play(105 if e == 0 else 80), at(k, e), 0.9 * big)
        for e in (1, 2, 4, 5):
            if e in (2, 5) or k % 2:
                for m in CH[c]:
                    M.add('horns', horn.play(m, 84 if e in (2, 5) else 64), at(k, e), 0.5, -0.25)
        pat = (0, 1, 2, 3, 4, 5) if k % 4 == 3 else (0, 2, 3, 5)
        for e in pat:
            M.add('drums', (snare_f if e in (0, 3) else snare).play(110 if e in (0, 3) else 78), at(k, e),
                  0.7 * big, 0.15)
    M.add('drums', clash.play(110), T0, 0.6)

    # ---- 2.6-21.5: the pumpkin rolls across the wings; the A strain on trumpets and glock ----
    tune(TUNE_A, 2, tpt, long=tpt_s)
    tune(TUNE_A, 2, glock, 'motif', 86, 0.1, gain=0.5)
    spin = [0, 1, 2, 1]
    for i, t in enumerate(np.arange(TP0, TP1, E)):
        u = t - TP0
        c = np.array([PX0 + PV * u, Y + 70 * np.sin(2 * np.pi * u / PBOB), -178.0])
        w, p = lit(ball(P, c, 215)[0])
        if w < 2:
            continue
        k = int((t - T0) // WADDLE)
        ch = CH[PLAN[k]] if 0 <= k < nbar else CH['Bb']
        m = ch[spin[i % 4]] + 12 * ((i // 4) % 2)          # round and round, up an octave and back
        M.add('motif', mar.play(m, int(min(115, 50 + w))), t, 0.9, p)

    # ---- 15-34.5: the corn comes down the Side, turns the corner, and cuts across both porch sides ----
    route = corn_route()
    seg = np.linalg.norm(np.diff(route, axis=0), axis=1)
    cum = np.concatenate([[0], np.cumsum(seg)])
    t_turn = TC0 + cum[1] / CV, TC0 + cum[-2] / CV          # into and out of the rounded corner

    def corn_lit(t):
        c, tan, _ = path_point(route, (t - TC0) * CV)
        a, b = c - tan * 150, c + tan * 150
        w = np.clip(((P - a) @ (b - a)) / ((b - a) @ (b - a)), 0, 1)
        d = np.linalg.norm(P - (a + w[:, None] * (b - a)), axis=1)
        return lit(np.clip((70 - d) / 6, 0, 1)), c

    def corn_pan(t):                        # where it lights the roof, or where it is when it lights none
        (w, p), c = corn_lit(t)
        return p if w > 0.5 else float(np.clip(0.85 * (2 * (c[0] - x0) / (x1 - x0) - 1), -0.85, 0.85))

    tune(TUNE_B, 12, clar, 'motif', 104, corn_pan, gain=1.1)
    tune(TUNE_B, 12, xylo, 'motif', 80, corn_pan, gain=0.4)
    uu = np.linspace(0, 1, int((t_turn[1] - t_turn[0]) * SR))
    sw = tone(700 * 2 ** (uu * 1.2 + 0.15 * np.sin(np.pi * uu)), 0.5)
    sw *= np.clip(uu / 0.05, 0, 1) * np.clip((1 - uu) / 0.05, 0, 1)
    pans = np.array([corn_pan(t) for t in np.linspace(*t_turn, 64)])
    M.add('fx', mono(sw, np.interp(uu, np.linspace(0, 1, 64), pans)), t_turn[0], 0.9)
    M.add('perc', wood.play(120), t_turn[1], 1.4, pans[-1])
    M.add('drums', choke.play(90), t_turn[1], 0.4, pans[-1])
    xc = np.array([path_point(route, (t - TC0) * CV)[0][0] for t in np.arange(TC0, TC1, 0.01)])
    for name in ('Porch Left', 'Porch Right'):              # the cob's middle crosses each porch side
        xp = float(G.pos[G.seg[name], 0].mean())
        tx = TC0 + 0.01 * int(np.argmax(xc >= xp))
        p = float(pan_at(G.pd[G.seg[name]].mean()))
        M.add('perc', log.play(118), tx, 1.0, p)
        M.add('drums', timp.play(110), tx, 0.6, p)
        for m in CH['F']:
            M.add('horns', horn.play(m + 12, 110, dur=0.3), tx, 0.6, p)
        M.add('motif', xylo.play(n('C6'), 110), tx, 0.6, p)
    for i, t in enumerate(np.arange(t_turn[1], TC1, E / 2)):  # kernels popping as it crosses
        (w, p), _ = corn_lit(t)
        if w > 0.5 and M.rng.random() < 0.3:
            M.add('perc', wood.play(int(M.rng.integers(60, 95)), pitch=float(M.rng.uniform(2, 9))), t, 0.4, p)

    # ---- 32-49: the trio in Eb; the turkey waddles in on the footsteps, gobbling ----
    tune(TUNE_T, 21, horn, 'tune', 100, -0.1, long=horn_s, gain=0.75)
    tune(TUNE_T, 21, bone, 'horns', 84, 0.2, gain=0.6)
    tune(TUNE_T[4:7], 29, tpt, long=tpt_s, gain=0.9)
    tune(TUNE_T[4:7], 29, glock, 'motif', 86, 0.1, gain=0.5)
    tune([CLIMB], 32, tpt, gain=0.9)
    tune([CLIMB], 32, horn, 'horns', 100, -0.2)

    def turkey(t):                          # body, head centre and radius as render() places them
        u = t - TT0
        waddle = 10 * np.sin(2 * np.pi * u / WADDLE) * (t < TSTOP)
        Rb = keys(t, SWELL)
        c = np.array([turkey_x(t), Y + 25 * np.sin(2 * np.pi * u / TBOB), -560.0 + waddle])
        gob = 25 * max(0, np.sin(2 * np.pi * u / GOBBLE)) ** 6
        return c, c + np.array([Rb * 0.85 + 35 + gob, 70, 0]), Rb

    for i, t in enumerate(np.arange(TT0, TSTOP, WADDLE / 2)):  # a footfall at each end of the waddle
        c, _, Rb = turkey(t)
        w, p = lit(ball(P, c, Rb)[0])
        if w > 1:
            M.add('perc', log.play(100, pitch=-3 if i % 2 else 0), t, 0.8, p)
    for t in np.arange(TT0 + GOBBLE / 4, TPOP, GOBBLE):     # gobbles at the top of each head bob, higher as he swells
        _, h, Rb = turkey(t)
        w, p = lit(ball(P, h, 62)[0])
        if w < 0.5:
            continue
        up = int(round(12 * np.log2(Rb / 150)))
        for j, s in enumerate((0, 3, 0, 3, -2, 0)):
            M.add('motif', bsn.play(n('Eb3') + up + s, 112, dur=0.07), t + 0.065 * j, 1.0, p)

    # ---- 49: he stops dead; the band halts on a Bb7 ----
    for m in CH['Bb7']:
        M.add('tune', tpt.play(m + 12, 120, dur=0.25), TSTOP, 0.8)
        M.add('horns', horn.play(m, 118, dur=0.25), TSTOP, 0.8)
    M.add('bass', tuba.play(n('Bb1'), 122), TSTOP)
    M.add('drums', bd_ff.play(118), TSTOP, 1.0)
    M.add('drums', rim.play(120), TSTOP, 0.8)
    M.add('drums', choke.play(110), TSTOP, 0.7)

    # ---- 49.5-55.05: he swells; the whistle follows his radius, the band holds its breath underneath ----
    t1 = SWELL[0][0]
    tt = t1 + np.arange(int((TPOP - t1) * SR)) / SR
    Rb = np.array([keys(t, SWELL) for t in tt[::480]])
    Rb = np.interp(np.arange(len(tt)), np.arange(len(Rb)) * 480, Rb)
    strain = smoothstep(52, 55, tt)
    fw = 330 * (Rb / 150) ** 1.8 * (1 + 0.025 * strain * np.sin(30 * tt))
    whistle = tone(fw, 0.2) * np.clip((tt - t1) / 0.3, 0, 1)
    M.add('fx', mono(whistle, np.full(len(tt), pan_at(POP_D))), t1, 0.8)
    M.add('hold', trem.play(n('Bb2'), 70, dur=TPOP - t1), t1, 0.8, -0.2)
    M.add('hold', trem.play(n('F3'), 70, dur=TPOP - t1), t1, 0.6, 0.2)
    for (ta, ra), (tb, rb) in zip(SWELL, SWELL[1:]):         # a horn note for each stage of swelling, a step higher
        if rb > ra:
            m = n('F3') + int(round(12 * np.log2(rb / 150)))
            M.add('horns', horn_s.play(m, 50 + int(rb / 8), dur=tb - ta), ta, 0.7, pan_at(POP_D))
        elif rb < ra:                       # the hiccup
            M.add('fx', fall.play(90, dur=tb - ta + 0.3), ta, 0.6, pan_at(POP_D))
            M.add('perc', wood.play(100, pitch=7), ta, 0.6, pan_at(POP_D))
    ts = SWELL[3][0]                         # the strain: rolls build from the big swell to the pop
    r = troll.play(90, dur=TPOP - ts)
    M.add('drums', r * np.linspace(0.15, 1, r.shape[1]) ** 2, ts, 0.3)
    r = sroll.play(90, dur=TPOP - ts)
    M.add('drums', r * np.linspace(0.1, 1, r.shape[1]) ** 2, ts, 0.25)
    r = ccresc.play(100, dur=TPOP - ts + 0.05)
    M.add('drums', r * np.linspace(0.1, 1, r.shape[1]) ** 2, ts - 0.05, 0.2)

    # ---- 55.05: POP; confetti; the untied head pffffts off around the corner and out the end ----
    pp = float(pan_at(POP_D))
    M.add('drums', clash_f.play(127), TPOP, 1.8, pp)
    M.add('drums', bd_ff.play(127), TPOP, 2.2, pp)
    M.add('drums', timp.play(127, pitch=-3), TPOP, 1.6, pp)
    M.add('perc', slap.play(127), TPOP, 1.5, pp)
    burst = M.rng.normal(0, 1, int(0.25 * SR)) * np.exp(-np.arange(int(0.25 * SR)) / SR / 0.03)
    M.add('fx', mono(1.5 * burst, np.full(len(burst), pp)), TPOP, 1.0)
    for m in (n('Bb2'), n('F3'), n('Bb3'), n('D4')):
        M.add('horns', horn.play(m, 125, dur=0.3), TPOP, 0.7, pp)
    rng = np.random.default_rng(24)                           # the same confetti render() throws
    Flicker(rng, G.N, 0.2, 1.0)
    conf_p, conf_t, _ = confetti(G, rng)
    sparkle = [n(m) for m in ('Bb5', 'C6', 'D6', 'F6', 'G6', 'Bb6')]
    for j in np.argsort(conf_t)[::3]:
        M.add('motif', glock.play(sparkle[int(M.rng.integers(len(sparkle)))], 70), conf_t[j], 0.3,
              float(pan_at(conf_p[j])))
    uu = np.arange(0, 6.0, 0.005)
    hs = head_s(uu)
    gone = float(uu[np.argmax(hs >= G.length)])               # the head flies off the free end
    tu = np.arange(int((gone + 0.3) * SR)) / SR
    fr = 520 * 2 ** (-2.3 * smoothstep(0, gone, tu)) * (1 + 0.18 * np.sin(2 * np.pi * 1.7 * tu) * (tu < 5.5))
    fr *= 1 + 0.04 * np.sin(2 * np.pi * 23 * tu)              # the flapping neck
    rasp = tone(fr, 0.26, buzz=0.9) * np.clip(tu / 0.04, 0, 1) * np.clip((gone + 0.3 - tu) / 0.3, 0, 1)
    M.add('fx', mono(rasp, pan_at(np.clip(head_s(tu), 0, G.length))), TPOP + 0.02, 0.9)
    M.add('perc', slap.play(110), TPOP + gone, 0.8, float(pan_at(G.length)))
    M.add('perc', tri.play(100), TPOP + gone, 0.5, float(pan_at(G.length)))

    # ---- after: the band picks back up for two bars and a last chord ----
    k1 = int(np.ceil((TPOP + 1.5 - T0) / WADDLE))
    for e in (3, 4, 5):                      # pickup
        M.add('drums', snare_f.play(90 + 10 * e), at(k1 - 1, e), 0.8, 0.15)
    for j, c in enumerate(CHORDS_A[5:7]):
        k = k1 + j
        for e in (0, 3):
            M.add('bass', tuba.play(BASS[c][e // 3], 108), at(k, e), 1.1)
            M.add('drums', bd.play(110 if e == 0 else 90), at(k, e), 1.0)
        for e in (2, 5):
            for m in CH[c]:
                M.add('horns', horn.play(m, 92), at(k, e), 0.55, -0.25)
        for e in (0, 2, 3, 4, 5):
            M.add('drums', (snare_f if e in (0, 3) else snare).play(110 if e in (0, 3) else 82), at(k, e), 0.8,
                  0.15)
    M.add('drums', clash.play(110), at(k1), 0.6)
    tune(TUNE_A[5:7], k1, tpt, long=tpt_s, gain=1.1)
    tune(TUNE_A[5:7], k1, glock, 'motif', 90, 0.1, gain=0.5)
    tend = at(k1 + 2)
    for m in CH['Bb']:
        M.add('tune', tpt_s.play(m + 12, 112, dur=2.2), tend, 0.55)
        M.add('horns', horn_s.play(m, 110, dur=2.4), tend, 0.55, -0.2)
    M.add('motif', glock.play(n('Bb5'), 100), tend, 0.6)
    M.add('bass', tuba_s.play(n('Bb1'), 115, dur=2.5), tend)
    M.add('drums', clash_f.play(120), tend, 0.8)
    M.add('drums', bd_ff.play(120), tend, 1.0)
    r = troll.play(80, dur=2.0)
    M.add('drums', r * np.linspace(1, 0.2, r.shape[1]), tend + 0.1, 0.5)
    M.add('drums', bd_ff.play(120), tend + 2.1, 0.9)
    M.add('drums', timp.play(120, pitch=-5), tend + 2.1, 0.8)
