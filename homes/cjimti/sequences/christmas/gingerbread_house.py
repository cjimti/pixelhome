"""Gingerbread House: The roofline is a warm gingerbread eave and a piping bag ices it. The bag's
bright nozzle travels the whole path from the back of Side, laying a thin bead of royal icing with a
fat piped dot at every squeeze; it slows at each corner and pipes a swirled rosette there.
Wet icing is glossy and slumps a little before it sets. Gumdrops plop onto the icing one by one,
a sprinkle shaker sweeps across the house by real x position, the sugar glitters, and then someone
takes two bites out of the free right end, crumbs and all."""
import numpy as np
from pixelhome.fx import DT, hexc, perc, light, keys, smoothstep, lerp, smooth_noise, nframes

CODE = 'CH05'
TITLE = 'Gingerbread House'
KIND = 'show'
DESCRIPTION = ('A piping bag ices the whole roofline, swirling rosettes into the corners. Gumdrops plop on, '
               'sprinkles rain across, and then somebody takes a bite out of the end.')
VOICEOVER = 'Get out the icing and the gumdrops: tonight the whole house is gingerbread.'

GINGER = hexc('#b04408')
GINGER_DARK = hexc('#601800')
ICING = hexc('#fff4e6')
NOZZLE = hexc('#ffffff')
GUMDROPS = [hexc(c) for c in ('#ff1828', '#18c040', '#ffb010', '#b020ff', '#ff5a10')]
SPRINKLES = [hexc(c) for c in ('#ff3050', '#30d060', '#4070ff', '#ffd020', '#ff80c0')]
CRUMB = hexc('#ff8a30')


D = 68.0
SEED = 35
T_START, T_END = 3.0, 33.0                               # the nozzle sets off; its window closes 8 s after T_END
CORNER_AT = (80, 178, 260, 331, 380)                     # path indices just before each corner
BITES = [(57.5, 55.0), (60.6, 120.0)]                    # (time, depth from the free right end)


def corners_of(G):
    x = G.pd[G.path]
    return np.array([(x[i] + x[i + 1]) / 2 for i in CORNER_AT])


def nozzle(G):
    """The nozzle's path distance per frame (speed limited near corners, a rosette pause at each) and the
    rosettes [(corner distance, time)] in the order it reaches them."""
    F = nframes(D)
    Ltr = G.length
    corners = corners_of(G)
    tt = np.arange(F) * DT
    tip = np.full(F, -40.0)
    s, v = -30.0, 0.0
    pause = {}
    for f, t in enumerate(tt):
        if T_START <= t:
            near = np.abs(corners - s)
            ahead = corners[corners > s - 1]
            vmax = 105.0
            if len(ahead):
                vmax = min(vmax, 25 + 1.4 * (ahead[0] - s))
            c = int(np.argmin(near))
            if near[c] < 2 and c not in pause:
                pause[c] = t
            if c in pause and t - pause[c] < 1.4:
                v = 0.0
            else:
                v += np.clip(max(vmax, 25) - v, -200 * DT, 120 * DT)
            s = min(s + v * DT, Ltr + 60)
        tip[f] = s
    return tip, [(corners[c], t0) for c, t0 in pause.items()]


def setup(G, rng):
    """Every random draw before the frame loop, in render()'s order: bake, bead, squeeze phase, gumdrops,
    sprinkles, glints. The loop then draws the crumbs at each bite."""
    x = G.pd[G.path]
    Pp = G.pos[G.path]
    n = G.N
    Ltr = G.length
    S = {}
    S['bake'] = smooth_noise(rng, x, 25)                 # baked colour varies along the eave
    S['bead_noise'] = smooth_noise(rng, x, 40)
    S['squeeze_ph'] = rng.uniform(0, 6.28)
    # gumdrops every so often along the icing, landing in a shuffled order
    gx = np.arange(70, Ltr - 60, 95) + rng.uniform(-20, 20, len(np.arange(70, Ltr - 60, 95)))
    S['gx'] = gx
    S['gt'] = 35.0 + np.sort(rng.uniform(0, 8.5, len(gx)))[rng.permutation(len(gx))]
    S['gc'] = rng.integers(len(GUMDROPS), size=len(gx))
    # sprinkles: shaker sweeps left->right across real x; each sprinkle lands when it passes
    sp_idx = rng.choice(n, 70, replace=False)
    S['sp_idx'] = sp_idx
    S['sp_col'] = np.array([SPRINKLES[i % 5] for i in range(70)])
    xs_min, xs_max = Pp[:, 0].min() - 20, Pp[:, 0].max() + 20
    S['xs_min'], S['xs_max'] = xs_min, xs_max
    S['sp_t'] = 45.0 + (Pp[sp_idx, 0] - xs_min) / (xs_max - xs_min) * 5.5 + rng.uniform(0, 0.5, 70)
    S['glint_ph'] = rng.uniform(0, 6.28, n)
    S['glint_f'] = rng.uniform(0.15, 0.45, n)
    return S


def render(G, seed=SEED):
    rng = np.random.default_rng(seed)
    F = nframes(D)
    out = np.zeros((F, G.N, 3))
    x = G.pd[G.path]
    Pp = G.pos[G.path]
    n = G.N
    Ltr = G.length
    S = setup(G, rng)
    bake = S['bake']
    gap = np.diff(x, prepend=x[0] - 4).clip(3.5, 8)      # local pixel pitch
    tip, rosettes = nozzle(G)

    icing = np.zeros(n)
    dots = np.exp(-(((x % 22) - 11) / 2.6) ** 2)
    bead = 0.2 + 0.05 * S['bead_noise'] + 0.75 * dots
    age = np.full(n, 99.0)                               # time since this pixel was last iced
    squeeze_ph = S['squeeze_ph']
    gx, gt, gc = S['gx'], S['gt'], S['gc']
    sp_idx, sp_col, sp_t = S['sp_idx'], S['sp_col'], S['sp_t']
    xs_min, xs_max = S['xs_min'], S['xs_max']
    glint_ph, glint_f = S['glint_ph'], S['glint_f']
    # bites from the free right end
    bites = BITES
    teeth = 1 + 0.5 * np.abs(np.sin((Ltr - x) * np.pi / 8))
    crumbs = []

    for f in range(F):
        t = f * DT
        fr = np.zeros((n, 3))
        base = keys(t, [(0, 0), (2.5, 1), (D - 3, 1), (D - 0.3, 0)])
        warm = keys(t, [(50, 1), (53, 1.35), (D, 1.35)])

        # icing laid by the nozzle: a thin bead with a fat piped dot every 22 units (a squeeze of
        # the bag at each), the bead wavering with the baker's hand; a swirled rosette at corners
        p = tip[f]
        if T_START < t < T_END + 8 and -10 < p < Ltr + 10:
            for cx, t0 in rosettes:
                if 0 <= t - t0 < 1.4:
                    p = p + 7 * np.sin(2 * np.pi * 2.2 * (t - t0))   # the swirl
                    ros = 1.2 * smoothstep(0, 1.4, t - t0) * np.exp(-((x - cx) / 9) ** 2)
                    icing = np.maximum(icing, ros)
                    age = np.where(ros > 0.1, 0.0, age)
            laid = smoothstep(p + 3, p - 3, x) * (x > p - 30)
            prof = bead * laid
            fresh = prof > icing + 0.01
            icing = np.maximum(icing, prof)
            age = np.where(fresh, 0.0, age)
        age += DT
        # wet icing slumps a little (spreads along the eave) until it sets
        wet = np.exp(-age / 2.5)
        lap = np.zeros(n)
        lap[1:-1] = icing[2:] - 2 * icing[1:-1] + icing[:-2]
        icing += 0.03 * wet * lap

        # bites: the eave beyond the bite line goes, with a toothy edge
        eaten = np.zeros(n)
        for tb, depth in bites:
            k = smoothstep(tb, tb + 0.25, t)
            eaten = np.maximum(eaten, k * ((Ltr - x) < depth * teeth))
            if abs(t - (tb + 0.2)) < DT / 2:
                for _ in range(16):
                    crumbs.append([Ltr - rng.uniform(0, depth), t, rng.uniform(-60, 60), rng.uniform(1.0, 2.2)])
        keep = 1 - eaten

        ice = np.clip(icing, 0, 1.15)
        gb = base * keep * (0.26 + 0.05 * bake) * warm * (1 - 0.6 * np.clip(ice, 0, 1))
        fr += perc(gb)[:, None] * lerp(GINGER_DARK, GINGER, 0.6 + 0.4 * bake[:, None])
        gloss = 0.25 * wet
        fr += light(ICING, base * keep * (0.5 * ice ** 1.1 + gloss * np.clip(ice * 3, 0, 1)))

        # the nozzle itself
        if T_START < t < T_END + 8 and -10 < tip[f] < Ltr + 10:
            fr += light(NOZZLE, 0.95 * np.exp(-((x - p) / 2.2) ** 2))

        # gumdrops: drop in, squash on landing, then sit glowing
        for gxi, gti, gci in zip(gx, gt, gc):
            u = t - gti
            if u < 0:
                continue
            squash = 1 + 0.9 * np.exp(-u / 0.12) * (u < 0.6)
            I = 0.62 * smoothstep(0, 0.05, u) * (1 + 0.6 * np.exp(-u / 0.15))
            w = 5.5 * squash
            fr += light(GUMDROPS[gci], base * I * np.exp(-((x - gxi) / w) ** 2) * keep)

        # sprinkles and, once everything's on, glittering sugar
        landed = (t >= sp_t)
        if landed.any():
            k = sp_idx[landed]
            pop = 1 + 1.2 * np.exp(-(t - sp_t[landed]) / 0.1)
            fr[k] += perc(base * 0.55 * pop * keep[k])[:, None] * sp_col[landed]
        if 44 < t < 52.5:                                   # the shaker, by real x position
            sx = lerp(xs_min, xs_max, smoothstep(45, 51, t))
            fr += light(NOZZLE, 0.35 * np.exp(-((Pp[:, 0] - sx) / 12) ** 2))
        sug = keys(t, [(50, 0), (52, 1), (57, 1), (58, 0.5)])
        if sug > 0:
            g = np.clip(np.sin(2 * np.pi * glint_f * t + glint_ph), 0, 1) ** 12
            fr += light(NOZZLE, base * sug * 0.6 * g * np.clip(ice, 0, 1) * keep)

        # crumbs tumble off the bitten end
        live = []
        for c in crumbs:
            a = t - c[1]
            if a > c[3]:
                continue
            live.append(c)
            c[0] += c[2] * DT * np.exp(-a)
            fr += light(CRUMB, 0.7 * (1 - a / c[3]) * np.exp(-((x - c[0]) / 2.5) ** 2))
        crumbs = live
        # the crunch: a little flash at each bite line
        for tb, depth in bites:
            u = t - tb - 0.15
            if 0 < u < 0.6:
                fr += light(ICING, 0.6 * np.exp(-u / 0.12) * np.exp(-(((Ltr - x) - depth) / 10) ** 2))
        out[f][G.path] = fr
    return out


# ---- music: a bakery waltz in F, 3/4. Its bar lines are pinned to the show (a tempo map, about 120 bpm):
# the nozzle sets off on bar 2, every corner rosette lands on a downbeat, the nozzle runs off the end on bar 26,
# the sprinkle sweep starts on bar 30, the music holds its breath on bar 37 and the first bite is bar 38.
BARS = [(0, 0.0), (2, T_START), (6, 8.8), (10, 14.875), (14, 21.1), (18, 26.675), (22, 32.5), (26, 38.9),
        (30, 45.0), (34, 51.0), (38, BITES[0][0]), (40, BITES[1][0]), (43, 65.0), (45, D)]
CHORDS = {0: 'F', 1: 'C7', 2: 'F', 3: 'F', 4: 'Gm', 5: 'C7', 6: 'F', 7: 'F7', 8: 'Bb', 9: 'C7',
          10: 'F', 11: 'Dm', 12: 'Gm', 13: 'C7', 14: 'F', 15: 'D7', 16: 'Gm', 17: 'C7',
          18: 'F', 19: 'Bb', 20: 'G7', 21: 'C7', 22: 'F', 23: 'Bb', 24: 'C7', 25: 'C7',
          26: 'F', 27: 'Dm', 28: 'Gm', 29: 'C7', 30: 'F', 31: 'Bb', 32: 'C7', 33: 'F',
          34: 'Bb', 35: 'F', 36: 'G7', 37: 'C7', 40: 'F', 41: 'C7', 42: 'C7', 43: 'F'}
VOICE = {'F': ('F2', 'A3 C4 F4'), 'C7': ('C2', 'G3 Bb3 E4'), 'Gm': ('G2', 'G3 Bb3 D4'), 'F7': ('F2', 'A3 Eb4 F4'),
         'Bb': ('Bb1', 'Bb3 D4 F4'), 'Dm': ('D2', 'A3 D4 F4'), 'D7': ('D2', 'A3 C4 F#4'), 'G7': ('G2', 'G3 B3 F4')}
# the tune, bar by bar: (beat, note, beats)
TUNE = {
    2: [(0, 'C5', 2), (2, 'A4', 1)], 3: [(0, 'F4', 1), (1, 'A4', 1), (2, 'C5', 1)],
    4: [(0, 'D5', 2), (2, 'Bb4', 1)], 5: [(0, 'G4', 1), (1, 'A4', 1), (2, 'Bb4', 1)],
    6: [(0, 'A4', 3)], 7: [(0, 'C5', 1), (1, 'Eb5', 1), (2, 'C5', 1)],
    8: [(0, 'D5', 1.5), (1.5, 'C5', 0.5), (2, 'Bb4', 1)], 9: [(0, 'G4', 1), (1, 'Bb4', 1), (2, 'E4', 1)],
    10: [(0, 'F4', 3)], 11: [(0, 'A4', 1), (1, 'D5', 1), (2, 'F5', 1)],
    12: [(0, 'D5', 1), (1, 'Bb4', 1), (2, 'G4', 1)], 13: [(0, 'C5', 2), (2, 'E4', 1)],
    14: [(0, 'A4', 2), (2, 'C5', 1)], 15: [(0, 'F#4', 1), (1, 'A4', 1), (2, 'D5', 1)],
    16: [(0, 'D5', 1), (1, 'Bb4', 1), (2, 'G4', 1)], 17: [(0, 'Bb4', 1), (1, 'A4', 1), (2, 'G4', 1)],
    18: [(0, 'F4', 2), (2, 'C5', 1)], 19: [(0, 'D5', 1), (1, 'F5', 1), (2, 'D5', 1)],
    20: [(0, 'B4', 2), (2, 'G4', 1)], 21: [(0, 'Bb4', 1), (1, 'C5', 1), (2, 'E5', 1)],
    22: [(0, 'F5', 2), (2, 'C5', 1)], 23: [(0, 'D5', 1), (1, 'Bb4', 1), (2, 'F4', 1)],
    24: [(0, 'E4', 1), (1, 'G4', 1), (2, 'Bb4', 1)], 25: [(0, 'E5', 1), (1, 'D5', 1), (2, 'C5', 1)],
}
GUMDROP_TUNE = {   # the bassoon hops while the gumdrops plop
    26: [(0, 'C4', 1), (1, 'F3', 0.5), (1.5, 'A3', 0.5), (2, 'C4', 1)],
    27: [(0, 'D4', 1), (1, 'A3', 0.5), (1.5, 'F3', 0.5), (2, 'A3', 1)],
    28: [(0, 'Bb3', 1), (1, 'D4', 0.5), (1.5, 'G3', 0.5), (2, 'Bb3', 1)],
    29: [(0, 'C4', 1), (1, 'E3', 0.5), (1.5, 'G3', 0.5), (2, 'Bb3', 1)],
}
SPRINKLE_TUNE = {  # the flute skips across with the shaker
    30: [(0, 'A4', .5), (.5, 'C5', .5), (1, 'F5', .5), (1.5, 'C5', .5), (2, 'A4', 1)],
    31: [(0, 'Bb4', .5), (.5, 'D5', .5), (1, 'F5', .5), (1.5, 'D5', .5), (2, 'Bb4', 1)],
    32: [(0, 'G4', .5), (.5, 'Bb4', .5), (1, 'E5', .5), (1.5, 'C5', .5), (2, 'G4', .5), (2.5, 'E4', .5)],
    33: [(0, 'F4', 1), (1, 'A4', 1), (2, 'C5', 1)],
}
SUGAR_TUNE = {     # a music box over the glitter, held on the last bar before the bite
    34: [(0, 'D5', 2), (2, 'F5', 1)], 35: [(0, 'C5', 2), (2, 'A4', 1)],
    36: [(0, 'B4', 1), (1, 'D5', 1), (2, 'F5', 1)], 37: [(0, 'E5', 3)],
}
FINALE_TUNE = {
    40: [(1, 'A4', 1), (2, 'C5', 1)],
    41: [(0, 'E4', .5), (.5, 'G4', .5), (1, 'Bb4', .5), (1.5, 'C5', .5), (2, 'E5', 1)],
    42: [(0, 'D5', 1), (1, 'C5', 1), (2, 'E5', 1)],
    43: [(0, 'F5', 3)],
}


def at(bar, beat=0.0):
    """Bar (and beat of three) -> seconds, through the tempo map."""
    b, t = zip(*BARS)
    return float(np.interp(bar + beat / 3, b, t))


def score(M, G):
    from pixelhome.audio import SR, note
    n = note
    rng = np.random.default_rng(SEED)          # render()'s draws, then the crumbs it draws at each bite
    S = setup(G, rng)
    crumbs = []
    for tb, depth in BITES:
        for _ in range(16):
            crumbs.append((tb + 0.2, G.length - rng.uniform(0, depth), rng.uniform(-60, 60), rng.uniform(1.0, 2.2)))
    tip, rosettes = nozzle(G)

    clar = M.sampler('Woodwinds/Clarinet/stac/*.wav', tune=-12)
    clar_s = M.sampler('Woodwinds/Clarinet/susLong/*.wav', tune=-12)
    flute = M.sampler('Woodwinds/Flute/stac/*.wav', tune=-12)
    flute_s = M.sampler('Woodwinds/Flute/susvib/*.wav', tune=-12)
    bsn = M.sampler('Woodwinds/Bassoon/stac/*.wav', tune=-12)
    glock = M.sampler('Percussion/Glock/*.wav', tune=-12)
    mar = M.sampler('Percussion/Marimba/*.wav', tune=-12)
    harp = M.sampler('Strings/Harp/*.wav')
    bass = M.sampler('Strings/Solo Contrabass/Pizz/*.wav', tune=-12)
    vla = M.sampler('Strings/Viola Section/pizz/*.wav', tune=-12)
    vln_s = M.sampler('Strings/Violin Section/susVib/*.wav', tune=-12)
    vln_t = M.sampler('Strings/Violin Section/Trem/*.wav', tune=-12)
    box = M.synth('Plucks/Magic Music Box')
    shaker = M.hits("VSCO 1 Percussion/varWood/Camo's Shaker/shake*.wav")
    sleigh = M.hits('Percussion/Sleighbells_Hit*.wav')
    sleigh_shake = M.hits('Miscellania Raw/Misc 2/sleighbell*_shake*.wav')
    tri = M.hits('Percussion/Triangle3-Hit_v1*.wav')
    belltree = M.hits('Percussion/BellTree_Stroke*.wav')
    chimes = M.hits('VSCO 1 Percussion/varMetal/various/windchimes_asc1.wav')
    click = M.hits('VSCO 1 Percussion/varWood/wood_click*.wav')
    slap = M.hits('VSCO 1 Percussion/varWood/slapstick_quiet*.wav')
    cym = M.hits('Percussion/susCymb1-hit_mp*.wav')
    timp = M.hits('Percussion/Timpani/Timpani1_Hit*.wav')

    for name, gain, rev in (('tune', 0.42, 0.2), ('accomp', 0.36, 0.14), ('bass', 0.5, 0.06), ('pad', 0.22, 0.3),
                            ('icing', 0.3, 0.2), ('sparkle', 0.26, 0.3), ('fx', 0.5, 0.12), ('perc', 0.3, 0.15)):
        M.bus(name, gain=0.8 * gain, reverb=rev)

    order = np.argsort(G.pd)
    xs, ds = G.pos[order, 0], G.pd[order]
    x0, x1 = xs.min(), xs.max()
    L = G.length

    def pan_at(dd):                              # path distance -> left/right across the facade, from the street
        x = np.interp(np.clip(dd, 0, L), ds, xs)
        return float(0.85 * (2 * (x - x0) / (x1 - x0) - 1))

    def pan_x(x):
        return float(0.85 * (2 * (x - x0) / (x1 - x0) - 1))

    def beats(bar):                              # seconds per beat in this bar
        return (at(bar + 1) - at(bar)) / 3

    def tune(bars, inst, long=None, bus='tune', vel=100, gain=1.0, pan=0.0, octave=0):
        for k, notes in bars.items():
            for b, m, ln in notes:
                pl = long if (long is not None and ln >= 2) else inst
                M.add(bus, pl.play(n(m) + octave, vel, dur=ln * beats(k) * 0.92), at(k, b), gain, pan)

    def waltz(k, vel=88, gain=1.0):              # oom-pah-pah: bass on one, a pizzicato chord on two and three
        c = CHORDS[k]
        lo, ch = VOICE[c]
        M.add('bass', bass.play(n(lo) + 12 * (lo[-1] == '1'), vel), at(k), gain)
        for b in (1, 2):
            for m in ch.split():
                M.add('accomp', vla.play(n(m), vel - 14), at(k, b), 0.45 * gain, 0.15)

    def chord_tones(k, lo=72, hi=86):
        ch = [n(m) % 12 for m in VOICE[CHORDS.get(k, 'F')][1].split()]
        return [m for m in range(lo, hi) if m % 12 in ch]

    # ---- 0-3: the eave warms; a harp rolls up, the waltz tips in ----
    for i, m in enumerate(('F3', 'A3', 'C4', 'F4', 'A4', 'C5', 'F5')):
        M.add('accomp', harp.play(n(m), 78), 0.15 + 0.12 * i, 0.9, -0.3 + 0.1 * i)
    M.add('sparkle', glock.play(n('C6'), 70), 1.0, 0.6, 0.0)
    for k in range(0, 26):
        waltz(k, 84 if k < 2 else 90)

    # ---- 3-39: the piping bag. A squeeze of the bag at every piped dot: a soft marimba plip of the chord,
    # climbing through it, panned to the nozzle; the music takes its downbeats from the rosettes ----
    tt = np.arange(len(tip)) * DT
    dots = np.arange(11, L, 22)
    for i, dd in enumerate(dots):
        t = float(tt[np.argmax(tip >= dd)])
        k = int(np.searchsorted([at(b) for b in range(44)], t, 'right') - 1)
        tones = chord_tones(k)
        m = tones[(i % len(tones))] if (i // len(tones)) % 2 == 0 else tones[-1 - (i % len(tones))]
        M.add('icing', mar.play(m, 64 + 10 * (i % 3 == 0)), t, 0.8, pan_at(dd))
        M.add('icing', click.play(50, pitch=9), t, 0.25, pan_at(dd))
    # each rosette: the harp swirls round the chord with the nozzle (2.2 turns a second), a glock on the downbeat
    for cx, t0 in rosettes:
        k = int(round(np.interp(t0, [t for _, t in BARS], [b for b, _ in BARS])))
        tones = chord_tones(k, 60, 86)
        span = tones[len(tones) // 3:]
        steps = list(range(len(span))) + list(range(len(span) - 2, 0, -1))
        dt = 1 / 2.2 / len(steps)
        for j in range(int(1.4 / dt)):
            M.add('accomp', harp.play(span[steps[j % len(steps)]], 82 - 20 * j * dt), t0 + j * dt, 0.75, pan_at(cx))
        M.add('sparkle', glock.play(tones[-1], 92), t0, 0.9, pan_at(cx))
        M.add('sparkle', tri.play(80), t0, 0.35, pan_at(cx))
    tune({k: v for k, v in TUNE.items() if k < 14}, clar, clar_s, vel=100)
    tune({k: v for k, v in TUNE.items() if k >= 14}, flute, flute_s, vel=100)
    tune({k: v for k, v in TUNE.items() if k >= 18}, clar, clar_s, vel=86, gain=0.5, octave=-12)
    tune({k: v for k, v in TUNE.items() if k >= 18}, glock, bus='sparkle', vel=72, gain=0.4)
    # the nozzle runs off the free end: a little glock flourish there
    t_off = float(tt[np.argmax(tip >= L)])
    for i, m in enumerate(('F5', 'A5', 'C6', 'F6')):
        M.add('sparkle', glock.play(n(m), 84), t_off - 0.24 + 0.08 * i, 0.7, pan_at(L))

    # ---- 35-44: gumdrops plop on, one by one: a plop where each lands and a marimba note for its colour ----
    def plop(f0, f1, seconds=0.09):
        k = int(seconds * SR)
        u = np.arange(k) / SR
        f = f0 * (f1 / f0) ** (u / seconds)
        s = np.sin(2 * np.pi * np.cumsum(f) / SR) * np.exp(-u / 0.03) * np.clip(u / 0.003, 0, 1)
        return np.vstack([s, s])

    pitch = {0: 'F4', 1: 'A4', 2: 'C5', 3: 'D5', 4: 'G4'}
    for gxi, gti, gci in zip(S['gx'], S['gt'], S['gc']):
        p = pan_at(gxi)
        M.add('fx', plop(260 + 30 * gci, 900 + 60 * gci), gti, 0.4, p)
        M.add('perc', mar.play(n(pitch[int(gci)]) - 12, 100), gti, 0.6, p)
    for k in range(26, 34):
        waltz(k, 92)
        M.add('perc', sleigh.play(70), at(k), 0.6, 0.0)
    tune(GUMDROP_TUNE, bsn, vel=108, gain=0.8, pan=-0.1)

    # ---- 44-52: the sprinkle shaker sweeps left to right (a shaker on every half beat, panned with it);
    # every sprinkle that lands pings a glock ----
    t = 44.0
    while t < 52.5:
        sx = lerp(S['xs_min'], S['xs_max'], smoothstep(45, 51, t))
        lvl = keys(t, [(44, 0.4), (45, 1), (51, 1), (52.5, 0.3)])
        M.add('perc', shaker.play(int(70 + 30 * lvl)), t, 0.8 * lvl, pan_x(sx))
        k = int(np.interp(t, [tb for _, tb in BARS], [b for b, _ in BARS]))
        t += beats(k) / 2
    Pp = G.pos[G.path]
    sprink = [n(m) for m in ('A5', 'C6', 'D6', 'F6', 'G5')]
    for i, (si, st) in enumerate(zip(S['sp_idx'], S['sp_t'])):
        M.add('sparkle', glock.play(sprink[i % 5], int(50 + 30 * ((i * 7) % 5) / 4)), st, 0.55, pan_x(Pp[si, 0]))
    tune(SPRINKLE_TUNE, flute, vel=104, gain=0.9, pan=0.1)

    # ---- 50-57.5: the sugar glitters (bell tree, chimes), the gingerbread glows warmer (strings swell) and a
    # music box plays; on bar 37 everything holds its breath ----
    M.add('sparkle', chimes.play(90), 50.0, 0.5, 0.2)
    M.add('sparkle', belltree.play(100), 52.0, 0.7, -0.2)
    for k in range(34, 37):
        waltz(k, 88)
    for k in range(34, 38):
        lo, ch = VOICE[CHORDS[k]]
        for m in ch.split():
            M.add('pad', vln_s.play(n(m) + 12, 90, dur=3 * beats(k) * 0.98), at(k), 0.8)
    notes = [(at(k, b), n(m), 70, ln * beats(k) * 0.95) for k, v in SUGAR_TUNE.items() for b, m, ln in v]
    M.add('tune', box.render(notes, D), 0.0, 4.0, 0.0)
    tune(SUGAR_TUNE, glock, bus='sparkle', vel=74, gain=0.6)
    tune(SUGAR_TUNE, clar_s, bus='tune', vel=70, gain=0.45, octave=-12)
    for g in np.arange(52.3, 57.0, 0.55):           # glints
        M.add('sparkle', tri.play(50), g, 0.12, float(np.sin(g * 3.1)) * 0.6)
    lo, ch = VOICE['C7']
    for m in ch.split():                            # the held breath: violins tremble
        M.add('pad', vln_t.play(n(m) + 12, 84, dur=at(38) - at(37)), at(37), 0.8)

    # ---- 57.5 and 60.6: two bites out of the free right end. A crunch where the bite line flashes, the crumbs
    # skitter where they fall; a bassoon "uh-oh" between ----
    def crunch(seconds=0.28, grains=34, amp=1.0):
        k = int(seconds * SR)
        sig = np.zeros(k)
        for _ in range(grains):
            s0 = int(M.rng.uniform(0, 0.75) ** 1.6 * k)
            ln = int(M.rng.uniform(0.002, 0.009) * SR)
            g = M.rng.normal(0, 1, ln) * np.hanning(ln) * (1 - s0 / k) * M.rng.uniform(0.4, 1)
            sig[s0:s0 + ln] += g[:max(0, min(ln, k - s0))]
        sig = np.diff(np.concatenate([[0], sig]))           # crisp
        sig = amp * sig / (np.abs(sig).max() + 1e-9)
        return np.vstack([sig, sig])

    for j, (tb, depth) in enumerate(BITES):
        p = pan_at(L - depth)
        M.add('fx', crunch(amp=0.9 + 0.1 * j), tb + 0.05, 0.9, p)
        M.add('fx', crunch(0.2, 22), tb + 0.13, 0.6, p)
        M.add('perc', slap.play(90 + 15 * j), tb + 0.15, 0.6, p)
        M.add('perc', timp.play(70 + 20 * j, pitch=-2), tb + 0.15, 0.5, p)
    for t0, c0, v, life in crumbs:                 # each crumb: a tiny click as it skitters off
        a = 0.15 + 0.25 * life * M.rng.uniform(0.3, 1)
        M.add('fx', click.play(int(60 + 20 * M.rng.random()), pitch=12 + 6 * M.rng.random()), t0 + a, 0.35,
              pan_at(c0 + v * (1 - np.exp(-a))))
    M.add('tune', bsn.play(n('C4'), 112, dur=0.35), at(38, 1), 1.2, 0.2)
    M.add('tune', bsn.play(n('A3'), 108, dur=0.7), at(38, 2), 1.2, 0.2)
    M.add('pad', vln_t.play(n('F#4'), 64, dur=at(40) - at(39)), at(39), 0.4)
    M.add('pad', vln_t.play(n('C5'), 64, dur=at(40) - at(39)), at(39), 0.4)

    # ---- 60.6-68: a cheeky run up and the last chord, the whole bakery together ----
    for k in (40, 41, 42):
        waltz(k, 96)
    tune(FINALE_TUNE, clar, clar_s, vel=108)
    tune(FINALE_TUNE, flute, flute_s, vel=100, gain=0.6, octave=0)
    tune(FINALE_TUNE, glock, bus='sparkle', vel=80, gain=0.45)
    tf = at(43)
    M.add('bass', bass.play(n('F2'), 110), tf, 1.2)
    M.add('bass', timp.play(100), tf, 0.6)
    for m in ('A3', 'C4', 'F4', 'A4'):
        M.add('pad', vln_s.play(n(m) + 12, 92, dur=D - tf), tf, 0.6)
    for i, m in enumerate(('F3', 'A3', 'C4', 'F4', 'A4', 'C5', 'F5', 'A5')):
        M.add('accomp', harp.play(n(m), 90), tf - 0.4 + 0.05 * i, 0.8, -0.4 + 0.1 * i)
    for m in ('F5', 'A5', 'C6'):
        M.add('sparkle', glock.play(n(m), 96), tf, 0.6)
    M.add('perc', cym.play(90), tf, 0.5)
    M.add('perc', sleigh_shake.play(100), tf, 0.7, 0.2)
    M.add('sparkle', tri.play(100), tf, 0.4)
