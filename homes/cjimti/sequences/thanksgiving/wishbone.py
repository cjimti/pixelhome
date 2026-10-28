"""Wishbone: The porch is the wishbone. Porch Left and Porch Right are its two prongs, the Porch Front
is the keel where they join. The wings are two people gripping the ends: Left in cranberry, Right in
gold. As they pull, the bone shifts toward whoever leads, and the light along it shows the stress in
the bone: dim ivory where it is thick, amber and then white-hot where it is thin and at the roots of
the prongs. Stress above a threshold builds fatigue damage, which crackles. In round one the right
hand slips and the left one flies backwards. In round two the damage piles up at a flaw near the root
of the left prong until the bone snaps there. Both halves recoil, and gold, holding the keel, wins
the wish."""
import numpy as np
from pixelhome.fx import DT, hexc, light, keys, smoothstep, lerp, Flicker, colormap, nframes

CODE = 'TG01'
TITLE = 'Wishbone'
KIND = 'show'
DESCRIPTION = ('The porch is the wishbone and the wings pull it. Light shows the stress in the bone as it creaks and '
               'crackles; one hand slips, they grip again, and it snaps at the weakest spot. Gold makes the wish.')

IVORY = hexc('#ffb070')
CRANBERRY = hexc('#c0102a')
GOLD = hexc('#ffb000')
AMBER = hexc('#ff8a18')
WARM = hexc('#ffe0b8')
BROWN = hexc('#4a1604')
D = 62.0
B0, B1 = 897.0, 2030.0            # bone ends: the grips at the two porch-side corners
FLAW = 1286.0                     # a thin spot near the root of the left prong
T_SLIP, T_SNAP = 18.0, 41.0

stress_map = colormap([(0.0, (1.0, 0.69, 0.44)), (0.35, (1.0, 0.45, 0.12)), (0.6, (1.0, 0.3, 0.03)),
                       (0.85, (1.0, 0.55, 0.15)), (1.0, (1.0, 0.8, 0.55))])
SEED = 31
JOLT = 1200                       # how fast the slip's jolt runs out along the left wing, units/s
WISH_AT, SPREAD = 3, 650          # after the snap the wish leaves the keel at WISH_AT s and spreads SPREAD units/s
COUNT1, COUNT2 = (6.8, 7.4, 8.0), (22.2, 22.8, 23.4)    # the countdown squeezes before each round
SGRID = np.arange(B0 - 200, B1 + 200, 1.0)               # bone coordinates
# the tug: tension and how far the bone has been dragged (+ toward the right person)
T_KEYS = [(0, 0), (8.4, 0), (9.2, 0.55), (11, 0.7), (12.5, 0.5), (14, 0.8), (16, 0.65), (17.6, 0.85),
          (T_SLIP, 0.9), (T_SLIP + 0.05, 0), (23.5, 0), (24.5, 0.6), (27, 0.75), (28, 0.6), (30, 0.85),
          (32.5, 0.8), (34, 0.95), (35.5, 0.85), (37.5, 1.0), (39, 0.92), (40.4, 1.08), (T_SNAP, 1.12)]
X_KEYS = [(0, 0), (8.4, 0), (10, 9), (11.5, -6), (13, -12), (14.5, 5), (16.2, 14), (17.6, 3), (T_SLIP, 0),
          (T_SLIP + 0.35, -75), (T_SLIP + 0.9, -52), (T_SLIP + 1.5, -63), (21.5, -40), (23.5, 0),
          (26, -8), (28.5, 6), (31, 14), (33, 4), (35, 16), (37.5, 22), (39.5, 18), (T_SNAP, 26)]


def weakness(s):
    """Thickness: prongs thin, keel thick, roots of the prongs where stress concentrates, one flaw."""
    w = np.where((s > 1311) & (s < 1660), 0.3, 0.55)
    w = w + 0.35 * np.exp(-((s - 1311) / 80) ** 2) + 0.3 * np.exp(-((s - 1660) / 80) ** 2)
    return w + 0.4 * np.exp(-((s - FLAW) / 14) ** 2)


def tension(t):
    T = keys(t, T_KEYS) if t < T_SNAP else 0.0
    return T * (1 + 0.06 * np.sin(2 * np.pi * 1.3 * t) * (T > 0))


def drag(t, T):
    return keys(t, X_KEYS) + (2.5 * np.sin(2 * np.pi * 2.1 * t) * T if t < T_SNAP else 0)


def materials(G, seed=SEED):
    """Everything render() draws from the rng: flicker, bone grain, and the crackle (time, bone coordinate)
    wherever stress above a threshold builds fatigue."""
    rng = np.random.default_rng(seed)
    tremble = Flicker(rng, G.N, 4.0, 7.0)
    slow = Flicker(rng, G.N, 0.2, 0.8)
    grain = 0.82 + 0.1 * np.sin(SGRID * 0.37) * np.sin(SGRID * 0.061) + 0.08 * np.interp(
        SGRID, SGRID[::9], rng.uniform(-1, 1, len(SGRID[::9])))
    w, ok = weakness(SGRID), (SGRID > B0 + 10) & (SGRID < B1 - 10)
    pops = []
    for f in range(nframes(D)):
        t = f * DT
        rate = np.clip(tension(t) * w - 0.5, 0, None) * ok
        cr = rate.sum() * DT * 2.2
        for _ in range(rng.poisson(cr) if t < T_SNAP and cr > 0 else 0):
            pops.append((t, rng.choice(SGRID, p=rate / rate.sum())))
    return tremble, slow, grain, pops


def render(G, seed=SEED):
    F = nframes(D)
    out = np.zeros((F, G.N, 3))
    n = G.N
    pdp = G.pd[G.path]
    LW = pdp < 893                 # Side + Left wing: the left person
    RW = pdp > 2034                # Right wing: the right person
    tremble, slow, grain, pops = materials(G, seed)
    sgrid = SGRID
    pop_t = np.array([p[0] for p in pops])
    pop_s = np.array([p[1] for p in pops])
    gripL_keys = [(0, 0), (4, 0), (6, 0.2), (T_SLIP, 0.22), (T_SLIP + 0.4, 0.6), (19.5, 0.2), (50, 0.2),
                  (58, 0)]

    for f in range(F):
        t = f * DT
        buf = np.zeros((n, 3))
        buf += light(BROWN, keys(t, [(0, 0), (2, 0.08), (58, 0.08), (62, 0)]) * (1 + 0.2 * slow(t)))
        T = tension(t)
        x = drag(t, T)
        appear = smoothstep(0.5, 3.5, t)

        sigma = T * weakness(sgrid)

        # the bone, drawn in its own coordinates s = pd - offset
        if t < T_SNAP:
            s = pdp - x
            inside = np.clip((s - B0) / 3 + 0.5, 0, 1) * np.clip((B1 - s) / 3 + 0.5, 0, 1)
            st = np.interp(s, sgrid, sigma)
            g = np.interp(s, sgrid, grain)
            base = (0.3 * appear) * g
            heat = np.clip(st, 0, 1)
            col = lerp(IVORY, stress_map(heat), np.clip(heat * 1.6, 0, 1)[:, None])
            buf += light(1.0, inside * (base + 0.45 * heat ** 1.5)) * col
        else:
            u = t - T_SNAP
            # two pieces recoil, each a damped spring overshooting and settling
            xl = x - 70 * (1 - np.exp(-u / 0.25) * np.cos(9 * u)) * 1.0
            xr = x + 45 * (1 - np.exp(-u / 0.3) * np.cos(8 * u))
            for lo, hi_, off, who in ((B0, FLAW, xl, 0), (FLAW, B1, xr, 1)):
                s = pdp - off
                inside = np.clip((s - lo) / 3 + 0.5, 0, 1) * np.clip((hi_ - s) / 3 + 0.5, 0, 1)
                g = np.interp(s, sgrid, grain)
                if who == 1:
                    wish = smoothstep(1.2, 4.5, u)
                    gc = lerp(IVORY, GOLD, wish)
                    I = inside * g * (0.3 + 0.25 * wish * (0.7 + 0.3 * np.sin(s * 0.03 - 2.2 * t)))
                    buf += light(1.0, I * keys(t, [(T_SNAP, 1), (55, 1), (61, 0)])) * gc
                else:
                    sulk = keys(t, [(T_SNAP, 0.3), (T_SNAP + 3, 0.22), (50, 0.12), (58, 0)])
                    buf += light(lerp(IVORY, CRANBERRY, smoothstep(0.5, 3, u)), inside * g * sulk)
            # the snap: a hot flash at the break and splinters flying both ways
            buf += light(WARM, np.exp(-u / 0.12) * np.exp(-((pdp - FLAW - x) / 30) ** 2))
            for k in range(14):
                sgn = 1 if k % 2 else -1
                v = 200 + 45 * k
                p = FLAW + x + sgn * v * u
                buf += light(IVORY, 0.7 * np.exp(-u / 0.35) * np.exp(-((pdp - p) / 3) ** 2))
            # the wish: gold spreads out of the keel to the whole house, then fades
            dist = np.abs(pdp - 1486)
            reach = SPREAD * max(0, u - WISH_AT)
            spread = np.clip((reach - dist) / 300, 0, 1)
            tw = (0.5 + 0.5 * slow(t)) ** 3
            buf += light(GOLD, 0.22 * spread * (0.7 + 0.3 * tw) * keys(t, [(T_SNAP, 1), (54, 1), (61, 0)]))

        # crackle where the bone is fatigued
        for i in np.nonzero((t - pop_t >= 0) & (t - pop_t < 0.25))[0]:
            uu = t - pop_t[i]
            buf += light(WARM, 0.8 * np.exp(-uu / 0.06) * np.exp(-((pdp - pop_s[i] - x) / 2.5) ** 2))

        # the two people: wings glow with their grip, straining with the tension
        effort = T * (1 + 0.12 * tremble(t))
        gl = keys(t, gripL_keys)
        grR = keys(t, [(0, 0), (4, 0), (6, 0.2), (50, 0.2), (58, 0)])
        left_lag = np.clip((893 - pdp) / 500, 0, 1)
        right_lag = np.clip((pdp - 2034) / 480, 0, 1)
        if t >= 0:
            # the Left person: strain gathers toward the grip
            Lw = gl * (1 - 0.5 * left_lag) + 0.5 * effort * np.exp(-left_lag * 4)
            if T_SLIP <= t < T_SLIP + 2:                       # falls backwards: a jolt runs to the far end
                uu = t - T_SLIP
                Lw = Lw + 0.6 * np.exp(-((left_lag * 893 - JOLT * uu) / 90) ** 2) * np.exp(-uu / 0.8)
            buf += light(CRANBERRY, Lw * LW)
            Rw = grR * (1 - 0.5 * right_lag) + 0.5 * effort * np.exp(-right_lag * 4)
            if T_SLIP <= t < T_SLIP + 1.6:                     # the slip: the grip slides out along the wing
                uu = t - T_SLIP
                gp = 2040 + 520 * uu
                Rw = Rw * (1 - smoothstep(0, 0.2, uu) * 0.6) + 0.7 * np.exp(-((pdp - gp) / 20) ** 2) * np.exp(-uu / 0.5)
            if t >= T_SNAP:                                    # the winner's wing lights up with the wish
                uu = t - T_SNAP
                Rw = Rw + 0.35 * smoothstep(0.5, 2.5, uu) * keys(t, [(T_SNAP, 1), (55, 1), (60, 0)])
            buf += light(GOLD, Rw * RW)
        # round two: grip, then three countdown squeezes
        for tc in COUNT2:
            uu = t - tc
            if 0 <= uu < 0.4:
                pulse = np.exp(-uu / 0.1)
                buf += light(CRANBERRY, 0.6 * pulse * np.exp(-((pdp - 893) / 25) ** 2))
                buf += light(GOLD, 0.6 * pulse * np.exp(-((pdp - 2034) / 25) ** 2))
        for tc in COUNT1:
            uu = t - tc
            if 0 <= uu < 0.4:
                pulse = np.exp(-uu / 0.1)
                buf += light(CRANBERRY, 0.6 * pulse * np.exp(-((pdp - 893) / 25) ** 2))
                buf += light(GOLD, 0.6 * pulse * np.exp(-((pdp - 2034) / 25) ** 2))
        out[f][G.path] = buf
    return out


# ---------------------------------------------------------------- music ----------------------------------------------
# A tug of war in F major and 6/8, on the lights' own countdown pulse (a dotted quarter is the gap between squeezes).
# A clarinet sings the wishbone's tune while it appears. In each round a tuba and pizzicato oom-pa-pa leans toward
# whoever is winning, a horn heaves on every rise in tension, violins tremble higher as it builds, and every fatigue
# crack in the lights crackles where it happens. The slip is a slide whistle and a pratfall, the snap a slapstick with
# xylophone splinters, the loser sulks on a trombone, and the wish is the tune again, on horn, as the gold spreads.

BEAT = COUNT1[1] - COUNT1[0]                # 0.6 s, a dotted quarter
E8, BAR = BEAT / 3, 2 * BEAT
CH = {'F': (53, 57, 60), 'Bb': (50, 53, 58), 'C': (48, 52, 55), 'Dm': (50, 53, 57), 'Gm': (50, 55, 58),
      'C7': (48, 52, 58)}
ROOT = {'F': (29, 36), 'Bb': (34, 29), 'C': (36, 31), 'Dm': (38, 33), 'Gm': (31, 38), 'C7': (36, 31)}
TUNE = [(0, 0, 'A4', 2), (0, 2, 'G4', 1), (0, 3, 'F4', 2), (0, 5, 'C4', 1), (1, 0, 'F4', 2), (1, 2, 'A4', 1),
        (1, 3, 'C5', 3), (2, 0, 'D5', 2), (2, 2, 'C5', 1), (2, 3, 'Bb4', 2), (2, 5, 'G4', 1)]
OPEN = [(3, 0, 'A4', 3), (3, 3, 'G4', 2)]   # (bar, eighth, note, eighths); this ending leaves it on the dominant
HOME = [(3, 0, 'G4', 2), (3, 2, 'E4', 1), (3, 3, 'F4', 3)]
TUNE_CH = ['F', 'F', 'F', 'F', 'Bb', 'C', 'F', 'C']                  # by half bar
ROUND1 = ['F', 'F', 'Bb', 'C', 'F', 'Dm', 'Bb', 'C']
ROUND2 = ['F', 'F', 'Bb', 'C', 'F', 'Dm', 'Gm', 'C', 'Bb', 'C', 'Dm', 'Bb', 'Gm', 'C7', 'C7', 'C7']
SCALE = [53, 55, 57, 58, 60, 62, 64, 65]    # F major from F3


def score(M, G):
    from pixelhome.audio import SR, note, slide, whoosh
    n = note
    clar = M.sampler('Woodwinds/Clarinet/susLong/*.wav', tune=-12)
    horn = M.sampler('Brass/F Horn/sus/*.wav', tune=-12)
    bsn = M.sampler('Woodwinds/Bassoon/stac/*.wav', tune=-12)
    tuba = M.sampler('Brass/Tuba/stac/*.wav', tune=-12)
    pizz = M.sampler('Strings/Cello Section/pizzT/*.wav', tune=-12)
    vpizz = M.sampler('Strings/Solo Violin/Pizz/*.wav')
    cello = M.sampler('Strings/Cello Section/susvib/*.wav', tune=-12)
    trem = M.sampler('Strings/Violin Section/Trem/*.wav', tune=-12)
    harp = M.sampler('Strings/Harp/*.wav')
    mar = M.sampler('Percussion/Marimba/*.wav', tune=-12)
    xylo = M.sampler('Percussion/Xylo/*.wav', tune=-12)
    glock = M.sampler('Percussion/Glock/*.wav', tune=-12)
    bone = M.sampler('Brass/OldTrombone/Fall/*.wav', tune=-12)
    wood = M.hits('VSCO 1 Percussion/varWood/wood_click*.wav')
    clave = M.hits('Percussion/Claves1_Hit*.wav')
    slap = M.hits('VSCO 1 Percussion/varWood/slapstick[0-9].wav')
    guiro = M.hits('VSCO 1 Percussion/varWood/guiro_short*.wav')
    vibra = M.hits('VSCO 1 Percussion/varWood/vibraslap*.wav')
    crash = M.hits('Percussion/cymbal-crash1_f*.wav')
    bd = M.hits('Percussion/BDrumNewhit_v[4-7]*.wav')
    timp = M.hits('Percussion/Timpani/Timpani1_Hit*.wav')
    troll = M.hits('Percussion/Timpani/Rolls/*.wav')

    for name, gain, rev in (('melody', 0.32, 0.25), ('brass', 0.24, 0.25), ('bass', 0.42, 0.08), ('pizz', 0.26, 0.15),
                            ('strings', 0.22, 0.3), ('harp', 0.3, 0.3), ('mallet', 0.36, 0.2), ('perc', 0.55, 0.12),
                            ('drums', 0.55, 0.18), ('crackle', 1.3, 0.12), ('fx', 0.16, 0.25)):
        M.bus(name, gain=gain, reverb=rev)

    order = np.argsort(G.pd)
    xs, ds = G.pos[order, 0], G.pd[order]
    x0, x1 = xs.min(), xs.max()

    def pan_at(d):                          # path distance -> left/right across the facade, as seen from the street
        x = np.interp(d, ds, xs)
        return 0.85 * (2 * (x - x0) / (x1 - x0) - 1)

    def travel(sig, d0, d1):                # a sound that moves along the roofline from d0 to d1 while it plays
        a = (np.linspace(pan_at(d0), pan_at(d1), sig.shape[1]) + 1) * np.pi / 4
        return sig * np.sqrt(2) * np.vstack([np.cos(a), np.sin(a)])

    def tones(chord, centre):               # the chord's tones, in any octave, nearest a pitch
        allm = [m + 12 * o for m in CH[chord] for o in (-1, 0, 1)]
        return min(allm, key=lambda m: abs(m - centre))

    keel, gl, gr = float(pan_at((B0 + B1) / 2)), float(pan_at(B0)), float(pan_at(B1))
    g1 = COUNT1[0] - 5 * BAR                # the intro's bars lead straight into the first countdown

    def tune(t0, phrase, inst, bus, vel, gain=1.0, pan=0.0):
        for b, e, m, ln in phrase:
            M.add(bus, inst.play(n(m), vel, dur=ln * E8 * 0.95, release=0.15), t0 + b * BAR + e * E8, gain, pan)

    def accomp(t0, bars, chords, vel=80):   # harp on the half bars, pizz bass on the beats
        for h in range(2 * bars):
            c, t = chords[h % len(chords)], t0 + h * BEAT
            M.add('bass', pizz.play(ROOT[c][h % 2] + 12, vel), t, 0.8, -0.2)
            for i, m in enumerate(CH[c]):
                M.add('harp', harp.play(m + 12, vel - 10), t + 0.03 * i, 0.7, 0.25)

    # ---- 0-6.8: the bone appears, the tune; the two people take hold ----
    M.add('strings', cello.play(n('F2'), 60, dur=6.2, release=0.8), g1, 0.9, keel)
    M.add('strings', cello.play(n('C3'), 50, dur=6.2, release=0.8), g1, 0.7, keel)
    for i in range(12):                     # a harp rolls up as the bone fades in, grip to grip
        m = [41, 48, 53, 57, 60, 65][i % 6] + 12 * (i // 6)
        M.add('harp', harp.play(m, 70 + 2 * i), g1 + i * E8, 0.9, gl + (gr - gl) * i / 11)
    tune(g1 + BAR, TUNE + OPEN, clar, 'melody', 70)
    accomp(g1 + BAR, 4, TUNE_CH, 58)
    M.add('pizz', vpizz.play(n('F4'), 90), g1 + 3 * BAR, 1.0, gl)            # cranberry takes hold
    M.add('pizz', vpizz.play(n('C5'), 90), g1 + 3 * BAR + BEAT, 1.0, gr)     # then gold

    # ---- the countdowns: three squeezes at the grips, then the pull ----
    def countdown(times, notes):
        for i, (tc, m) in enumerate(zip(times, notes)):
            for p in (gl, gr):
                M.add('perc', clave.play(100 + 10 * i), tc, 1.0, p)
            M.add('mallet', mar.play(n(m), 108 + 8 * i), tc, 1.0, keel)
            M.add('drums', timp.play(90 + 12 * i, pitch=2 * i), tc, 0.7)

    countdown(COUNT1, ('C4', 'D4', 'E4'))
    countdown(COUNT2, ('F4', 'G4', 'A4'))

    # ---- the rounds: oom-pa-pa leaning to whoever leads, violins rising with the tension ----
    def rnd(t0, start, end, chords, hush=None):   # t0 is a bar line on the round's grid; the band stops at hush
        k = int(np.ceil((start - t0) / BEAT))
        while t0 + k * BEAT < end:
            t = t0 + k * BEAT
            T = tension(t)
            c = chords[min(len(chords) - 1, k // 2)]
            lean = float(np.clip(drag(t, T) / 40, -0.6, 0.6))
            if k % 2 == 0:
                Tm = tension(t + BEAT)
                M.add('strings', trem.play(tones(c, 62 + 14 * Tm), int(45 + 55 * Tm), dur=min(BAR, end - t),
                                           release=0.1), t, 1.0, keel)
            if not (hush and t >= hush):
                M.add('bass', tuba.play(ROOT[c][k % 2], int(58 + 42 * T)), t, 1.0, lean)
                for e in (1, 2):
                    for m in CH[c] if t + e * E8 < end else ():
                        M.add('pizz', pizz.play(m, int(48 + 36 * T)), t + e * E8, 0.6, lean)
            k += 1

    rnd(COUNT1[-1], T_KEYS[1][0], T_SLIP, ROUND1)
    rnd(COUNT2[-1], T_KEYS[10][0], T_SNAP, ROUND2, hush=T_KEYS[-2][0])   # all hold their breath for the last heave
    heaves = []                             # every rise in tension, back-to-back rises taken as one
    for (ta, va), (tb, vb) in zip(T_KEYS, T_KEYS[1:]):
        if vb > va:
            heaves[-1:] = [(heaves[-1][0], tb, vb)] if heaves and heaves[-1][1] == ta else heaves[-1:] + [(ta, tb, vb)]
    for ta, tb, vb in heaves:               # a horn swells over each and is cut off by the slip or the snap; a bassoon grunts
        p = float(np.clip(drag(tb, vb) / 40, -0.6, 0.6))
        cut = tb in (T_SLIP, T_SNAP)
        M.add('brass', horn.play(SCALE[min(7, int(vb * 7))] - 12 + 12 * (ta > T_SLIP and vb > 0.9), int(42 + 50 * vb),
                                 dur=tb - ta + (0 if cut else 0.15), release=0.04 if cut else 0.3), ta, 1.0, p)
        M.add('melody', bsn.play(n('F2') + (ta > T_SLIP) * 2, 100, dur=0.3), ta, 0.8, p)
    M.add('drums', troll.play(70, dur=T_SNAP - 38.6), 38.6, 0.7, keel)

    # ---- the crackle: every fatigue crack in the lights, where it is on the house ----
    pops = materials(G)[3]
    buf = np.zeros((2, int(T_SNAP * SR) + SR))
    k = np.arange(int(0.004 * SR))
    for i, (tp, sp) in enumerate(pops):
        T = tension(tp)
        b = np.diff(M.rng.normal(0, 1, len(k) + 1)) * np.exp(-k / (0.0006 * SR)) * M.rng.uniform(0.3, 1.0)
        s, a = int(tp * SR), (pan_at(sp + drag(tp, T)) + 1) * np.pi / 4
        buf[0, s:s + len(k)] += b * np.cos(a) * 0.25
        buf[1, s:s + len(k)] += b * np.sin(a) * 0.25
        if i % 6 == 0:
            M.add('perc', wood.play(int(M.rng.uniform(40, 70))), tp, 0.35, float(pan_at(sp + drag(tp, T))))
    M.add('crackle', buf, 0.0)

    # ---- the slip: gold's grip slides out along the wing, cranberry falls over backwards ----
    M.add('fx', travel(slide(0.0, 0.5, 1600, 420, 0.6), 2040, 2040 + 520 * 0.6), T_SLIP, 1.0)
    M.add('perc', guiro.play(127), T_SLIP, 1.6, gr)
    M.add('perc', clave.play(127), T_SLIP, 1.4, gr)
    M.add('fx', travel(whoosh(893 / JOLT, 2500, 300, 0.6, seed=5), 893, 0), T_SLIP, 1.4)
    th = T_SLIP + 893 / JOLT                # the jolt reaches the far end: he lands
    M.add('drums', bd.play(120), th, 1.0, -0.85)
    M.add('drums', timp.play(115, pitch=-3), th, 0.8, -0.85)
    M.add('perc', slap.play(110), th, 0.9, -0.85)
    M.add('bass', tuba.play(n('F1'), 115), th, 1.0, -0.6)
    mid = (B0 + B1) / 2
    for (ta, xa), (tb, xb) in zip(X_KEYS[9:12], X_KEYS[10:13]):   # the bone wobbles where it was flung
        f0, f1 = (500, 850) if xb > xa else (850, 560)
        M.add('fx', slide(0.0, tb - ta, f0, f1, tb - ta, 0.4), ta, 0.6, float(pan_at(mid + xa)))
    t = X_KEYS[11][0] + 0.1                 # he gets up, dusts off, grumbles
    for i, m in enumerate(('A2', 'Bb2', 'B2', 'C3')):
        M.add('melody', bsn.play(n(m), 90), t + i * E8, 0.9, gl)
    M.add('melody', bsn.play(n('F3'), 100), t + 1.0, 0.9, gl)
    M.add('melody', bsn.play(n('C3'), 90), t + 1.0 + 2 * E8, 0.9, gl)
    for i, m in enumerate(('C5', 'A4')):    # gold: tsk tsk
        M.add('pizz', vpizz.play(n(m), 80), t + 1.9 + i * E8, 1.0, gr)
    for i, m in enumerate(('F2', 'C3', 'A3', 'F4')):
        M.add('harp', harp.play(n(m), 60), t + 2.3 + 0.05 * i, 0.8, keel)

    # ---- the snap: a slapstick at the flaw, splinters both ways, the halves spring back ----
    xs_ = drag(T_SNAP, 0.0)
    ps = float(pan_at(FLAW + xs_))
    M.add('perc', slap.play(127), T_SNAP, 1.0, ps)
    k = np.arange(int(0.05 * SR))                 # the crack itself: the crackle's voice, enormous
    crack = np.diff(M.rng.normal(0, 1, len(k) + 1)) * np.exp(-k / (0.008 * SR))
    M.add('crackle', np.vstack([crack, crack]) * 0.5, T_SNAP, 1.0, ps)
    M.add('drums', crash.play(118), T_SNAP, 0.8, ps)
    M.add('drums', bd.play(125), T_SNAP, 1.0, ps)
    M.add('drums', timp.play(120, pitch=-2), T_SNAP, 0.8, ps)
    M.add('bass', tuba.play(n('F1'), 120), T_SNAP)
    M.add('bass', tuba.play(n('C2'), 115), T_SNAP, 0.7)
    for m in CH['F']:
        M.add('pizz', pizz.play(m, 120), T_SNAP, 0.8, ps)
    for k in range(14):
        sgn, u = (1 if k % 2 else -1), 0.03 * k + 0.02
        M.add('mallet', xylo.play(SCALE[7 - k // 2] + 12, 115 - 4 * k), T_SNAP + u, 0.8,
              float(pan_at(FLAW + xs_ + sgn * (200 + 45 * k) * u)))
    pl, pr = float(pan_at((B0 + FLAW) / 2 + xs_ - 70)), float(pan_at((FLAW + B1) / 2 + xs_ + 45))
    M.add('perc', vibra.play(100), T_SNAP + 0.05, 0.7, pl)
    M.add('perc', vibra.play(100), T_SNAP + 0.08, 0.7, pr)
    M.add('fx', slide(0.0, 0.25, 950, 480, 0.4, 0.5), T_SNAP + 0.1, 0.7, pl)
    M.add('fx', slide(0.0, 0.3, 800, 520, 0.45, 0.5), T_SNAP + 0.15, 0.7, pr)
    M.add('brass', bone.play(n('D3'), 100), T_SNAP + 0.9, 0.9, pl)            # cranberry sulks
    for i in range(15):                     # the gold half becomes the wish: a harp sweeps up through it
        M.add('harp', harp.play(SCALE[i % 7] + 12 * (i // 7), 70 + 2 * i), T_SNAP + 1.2 + 0.12 * i, 0.8, pr)

    # ---- the wish: gold spreads out of the keel to the whole house; the tune comes home on the horn ----
    tw = T_SNAP + WISH_AT
    keel_d = 1486.0
    for sgn, far in ((-1, keel_d), (1, G.length - keel_d)):
        steps = int(far / SPREAD / E8)
        for i in range(steps + 1):          # harp runs out with the gold, both ways, one note per eighth
            m = SCALE[i % 7] + 12 + 12 * (i // 7)
            M.add('harp', harp.play(min(m, n('F6')), 72), tw + i * E8, 0.6, float(pan_at(keel_d + sgn * SPREAD * i * E8)))
    M.add('mallet', glock.play(n('C6'), 60), tw, 0.5, keel)
    tune(tw, TUNE + OPEN, clar, 'melody', 86)
    tune(tw + 4 * BAR, TUNE + HOME, horn, 'brass', 100, 1.1)
    for b, e, m, ln in TUNE + HOME:         # the clarinet a third under the horn's second time
        low = [k for k in range(n(m) - 1, n(m) - 5, -1) if k % 12 in {5, 7, 9, 10, 0, 2, 4}][1]
        M.add('melody', clar.play(low, 70, dur=ln * E8 * 0.95), tw + (4 + b) * BAR + e * E8, 0.6, -0.15)
    accomp(tw, 8, TUNE_CH, 84)
    for b in (2, 6):                        # the loser grumbles on the left, off the beat
        M.add('melody', bsn.play(n('C3'), 80), tw + b * BAR + 4 * E8, 0.8, gl)
        M.add('melody', bsn.play(n('F2'), 80), tw + b * BAR + 5 * E8, 0.8, gl)
    tf = tw + 8 * BAR                       # the last chord holds while the gold fades
    hold = D - tf - 1.0
    for m, inst, bus, v in ((n('F2'), cello, 'strings', 70), (n('C3'), cello, 'strings', 62),
                            (n('A3'), horn, 'brass', 70), (n('F4'), clar, 'melody', 70)):
        M.add(bus, inst.play(m, v, dur=hold, release=1.5), tf, 1.0, 0.15)
    M.add('bass', pizz.play(n('F2'), 90), tf, 0.9)
    for i, m in enumerate(('F2', 'C3', 'F3', 'A3', 'C4', 'F4', 'A4', 'C5')):
        M.add('harp', harp.play(n(m), 75), tf + 0.06 * i, 0.8, gl + (gr - gl) * i / 7)
    M.add('mallet', glock.play(n('F5'), 55), tf + 2 * BAR, 0.5, keel)
    M.add('harp', harp.play(n('F3'), 60), tf + 4 * BAR, 0.7, keel)
