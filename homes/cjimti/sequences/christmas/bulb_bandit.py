"""The Bulb Bandit: The roof is strung with bulbs. A green figure with yellow eyes peeks out of the free
back end of Side and tiptoes along the roofline, reeling the string in behind him: every bulb he
passes is pulled along the wire into his sack, segment by segment, pausing at each corner to look
round. A kid in pyjamas catches him on the porch; he shoos her back to bed. At the far right end, with
the whole house dark and his sack bulging, the house starts to sing anyway; something warm swells
in him and every bulb flies home."""
import numpy as np
from pixelhome.fx import DT, hexc, perc, light, keys, smoothstep, lerp, Flicker, nframes

CODE = 'XM03'
TITLE = 'The Bulb Bandit'
KIND = 'show'
DESCRIPTION = ('A green sneak with yellow eyes tiptoes along the roof reeling every bulb into his sack, '
               'corner by corner. The dark house sings anyway, something warm swells in him, and the lights fly home.')

BULBS = [hexc(c) for c in ('#ff2010', '#10b838', '#ffa018', '#2850ff', '#ff5a20', '#ff3060')]
GREEN = hexc('#38c008')
DARK_GREEN = hexc('#105800')
EYE = hexc('#d8ff10')
KID = hexc('#ffd0e0')
SING = hexc('#ffb040')
HEART = hexc('#ff1030')
WHITE = hexc('#fff4e0')

# bandit walk along the path (distance units): (t, position); corners at 490, 890, 1304, 1648, 2016
WALK = [(3.0, -6), (4.5, 12), (12.0, 470), (13.6, 470), (18.6, 875), (20.0, 875), (25.0, 1290),
        (26.0, 1290), (29.0, 1470), (33.2, 1470), (35.4, 1635), (36.4, 1635), (39.4, 2005),
        (40.4, 2005), (47.0, 2400), (60.5, 2400)]


def walk(t):
    """Tiptoe: progress between waypoints goes in quick steps with little holds between."""
    for (t0, a), (t1, b) in zip(WALK, WALK[1:]):
        if t0 <= t < t1:
            if a == b:
                return float(a)
            n = max(2, int(abs(b - a) / 34))
            v = (t - t0) / (t1 - t0) * n
            k = np.floor(v)
            return a + (b - a) * (k + smoothstep(0.05, 0.75, v - k)) / n
    return float(WALK[-1][1]) if t >= WALK[-1][0] else float(WALK[0][1])


SEED = 23
D = 72.0
REEL = 0.55                                       # seconds a bulb takes to be reeled into the sack
T_BURST = 61.0                                    # every bulb leaves the sack at once
T_BURST_X = 2385.0
FLY = 2.0
EYE_BLINKS = [5.2, 9.0, 16.9, 23.4, 31.0, 31.35, 44.0]
LOOKS = [(12.0, 13.6), (18.6, 20.0), (25.0, 26.0), (35.4, 36.4), (39.4, 40.4)]
STAGES = ((52.5, 9), (55.0, 20), (57.5, 42))      # the warmth swells in him: (start, radius)


def steps():
    """Every tiptoe step of the walk: (time the foot lifts, time it lands, position landed on)."""
    out = []
    for (t0, a), (t1, b) in zip(WALK, WALK[1:]):
        if a != b:
            n = max(2, int(abs(b - a) / 34))
            for k in range(n):
                out.append((t0 + (k + 0.05) / n * (t1 - t0), t0 + (k + 0.75) / n * (t1 - t0), a + (b - a) * (k + 1) / n))
    return out


def plan(G, seed=SEED):
    """The bulbs and the rng draws render() makes, in its order: colours, twinkle, when each is stolen and sent home."""
    rng = np.random.default_rng(seed)
    F = nframes(D)
    home = np.arange(6.0, G.length - 3, 12.5)       # one mini bulb every 12.5 units
    nb = len(home)
    perm = rng.permutation(nb)
    bcol = np.array([BULBS[i % len(BULBS)] for i in range(nb)])
    bcol = bcol[perm]
    kind = (np.arange(nb) % len(BULBS))[perm]
    tw = Flicker(rng, nb, 0.08, 0.4)
    # when the bandit's sack passes each bulb it is reeled in
    tt = np.arange(F) * DT
    gpath = np.array([walk(t) for t in tt])
    t_pass = np.array([tt[np.argmax(gpath >= h + 16)] if (gpath >= h + 16).any() else 99 for h in home])
    t_steal = t_pass + rng.uniform(0.0, 0.25, nb)
    # on the way home every bulb leaves the sack at once and lands within a moment of the others
    t_home = T_BURST + 0.1 + rng.uniform(0, 0.35, nb)
    return home, nb, bcol, kind, tw, gpath, t_steal, t_home


def render(G, seed=SEED):
    F = nframes(D)
    out = np.zeros((F, G.N, 3))
    x = G.pd[G.path]
    home, nb, bcol, kind, tw, gpath, t_steal, t_home = plan(G, seed)
    eye_blinks, looks = EYE_BLINKS, LOOKS

    for f in range(F):
        t = f * DT
        g = gpath[f]
        sack_x = g - 15
        fr = np.zeros((G.N, 3))
        master = keys(t, [(0, 0), (1.5, 1), (D - 3, 1), (D - 0.3, 0)])

        # bulbs: at home, being reeled in, in the sack, or flying home
        bp = home.copy()
        bI = 0.55 * (1 + 0.12 * tw(t))
        u_reel = np.clip((t - t_steal) / REEL, 0, 1)
        reeling = (u_reel > 0) & (u_reel < 1)
        bp = np.where(u_reel > 0, lerp(home, sack_x, u_reel ** 2), bp)
        gone = (u_reel >= 1) & (t < t_home)
        u_fly = np.clip((t - t_home) / FLY, 0, 1)
        flying = (u_fly > 0) & (u_fly < 1)
        e = 1 - (1 - u_fly) ** 3
        bp = np.where(t >= t_home, lerp(T_BURST_X, home, e), bp) if t >= T_BURST else bp
        bI = np.where(gone, 0.0, bI)
        bI = np.where(reeling, bI * (1 + 0.5 * u_reel), bI)
        bI = np.where(t >= t_home, bI * (1 + 0.8 * (1 - u_fly)) + 0.25 * smoothstep(0.85, 1, u_fly) * np.exp(-np.clip(t - t_home - FLY, 0, None) / 0.6), bI)
        bI = np.where((t >= T_BURST) & (t < t_home), 0.0, bI)
        wid = np.where(flying, 2.4 + 10 * (1 - u_fly) * u_fly, 2.4)
        near = np.abs(x[:, None] - bp[None]) < 60
        kern = np.where(near, np.exp(-((x[:, None] - bp[None]) / wid[None]) ** 2), 0)
        fr += (kern * perc(bI)[None]) @ bcol

        # the sack: everything he has stolen, a shimmering multicolour bundle
        n_in = gone.sum() if t < T_BURST else 0
        if n_in:
            frac = n_in / nb
            sw = 5 + 15 * np.sqrt(frac)
            shimmer = 0.5 + 0.5 * np.sin(x * 0.5 + 7 * t)
            mix = lerp(bcol[gone].mean(0), BULBS[(int(t * 3)) % len(BULBS)], 0.25 * shimmer[:, None])
            teeter = 0.0
            if 47.5 < t < T_BURST:
                teeter = 9 * np.sin(2 * np.pi * (t - 47.5) / 1.3) * np.exp(-(t - 47.5) / 4)
            sk = np.exp(-((x - (sack_x + teeter)) / sw) ** 2) * (0.35 + 0.5 * np.sqrt(frac))
            fr += perc(sk)[:, None] * mix

        # the bandit himself
        vis = keys(t, [(3.0, 0), (3.6, 1), (51.5, 1), (53.0, 0.4), (D - 3, 0.55), (D - 0.3, 0)])
        if vis > 0 and t < D:
            body = np.exp(-((x - g) / 9) ** 2)
            fr += light(DARK_GREEN, 0.5 * vis * np.exp(-((x - g) / 16) ** 2))
            fr += light(GREEN, 0.55 * vis * body)
            look = 0.0
            for a, b in looks:
                if a <= t < b:
                    look = 3.5 * np.sin(2 * np.pi * (t - a) / (b - a))
            if 29.0 < t < 33.2:                     # caught: eyes wide and fixed on the kid
                look = keys(t, [(29.5, 0), (30.0, 3), (32.8, 3), (33.2, 0)])
            wide = keys(t, [(29.6, 1), (29.9, 1.6), (32.6, 1.6), (33.2, 1)])
            blink = 1 - max([max(0.0, 1 - abs(t - b) / 0.12) for b in eye_blinks])
            for side in (-1, 1):
                ex = g + 3 + side * 3.6 * wide + look
                fr += light(EYE, 1.0 * vis * blink * np.exp(-((x - ex) / 1.6) ** 2))

        # a kid, up past her bedtime, just ahead of him on the porch
        cl = keys(t, [(29.6, 0), (30.2, 0.55), (32.0, 0.55), (33.0, 0)])
        if cl > 0:
            cx = 1470 + keys(t, [(29.6, 30), (32.0, 30), (33.0, 60)])
            fr += light(KID, cl * np.exp(-((x - cx) / 5) ** 2))

        # the house sings in the dark: slow warm swells rising out of the porch, phrase by phrase
        if 48.0 < t < 63.0:
            ts = t - 48.0
            amp = keys(t, [(48, 0), (50, 1), (60, 1), (63, 0)])
            d0 = np.abs(x - 1476)
            swell = 0.5 + 0.5 * np.sin(2 * np.pi * (ts * 0.9 - d0 / 700))
            fr += light(SING, amp * 0.22 * swell ** 2 * (0.6 + 0.4 * np.exp(-d0 / 900)))

        # the warmth swells in him
        stages = STAGES
        for k, (t0, r) in enumerate(stages):
            t1 = stages[k + 1][0] if k < 2 else T_BURST + 1.5
            if t0 <= t < t1:
                beat = sum(np.exp(-((t - t0 - j * 0.8 - 0.03) / 0.06) ** 2) +
                           0.7 * np.exp(-((t - t0 - j * 0.8 - 0.25) / 0.07) ** 2) for j in range(3))
                grow = smoothstep(t0, t0 + 0.3, t)
                hold = 0.6 if t < T_BURST else 0.6 * np.exp(-(t - T_BURST) / 0.5)
                size = r * (0.6 + 0.4 * grow) * (1 + 0.15 * beat)
                fr += light(HEART, (hold + 0.4 * beat) * np.exp(-((x - g) / size) ** 2))

        # the burst
        if T_BURST <= t < T_BURST + 0.8:
            tb = t - T_BURST
            fr += light(WHITE, 0.9 * np.exp(-tb / 0.15) * np.exp(-((x - T_BURST_X) / (20 + 300 * tb)) ** 2))

        # finale: every bulb home and a little brighter, a warm glow under them
        fin = keys(t, [(63, 0), (64.5, 1)])
        if fin > 0:
            fr += light(SING, 0.08 * fin * np.ones(G.N))
        out[f][G.path] = fr * master
    return out



# ---- music: a pizzicato sneak in D minor, one note per tiptoe step; the house sings a chorale in D major ----
SNEAK = ['D4', 'F4', 'A4', 'F4', 'G#4', 'A4', 'F4', 'D4', 'G4', 'Bb4', 'D5', 'Bb4', 'C#5', 'A4', 'G4', 'E4']
SNEAK_BASS = ['D2', 'A2', 'D2', 'A2', 'D2', 'A2', 'D2', 'A1', 'G2', 'D2', 'G2', 'D2', 'A1', 'E2', 'A1', 'C#2']
SNEAK_CHORD = [('D', 'F', 'A'), ('D', 'F', 'A'), ('G', 'Bb', 'D'), ('A', 'C#', 'E', 'G')]
SNEAK_LIFT = [('F3', 'A3'), ('A3', 'F3'), ('Bb3', 'D4'), ('C#4', 'G3')]
T_CAUGHT = 29.6                                   # the kid appears; his eyes go wide
T_SING = 48.0
BAR_S = 2.5                                       # the chorale's bars: the heart stages fall on its downbeats
CHORALE = [  # (start, beats, melody, bass, chord); bar 3 broadens to four beats so the burst lands on its downbeat
    (50.0, 3 * [BAR_S / 3], ['F#4', 'F#4', 'A4'], ['D2'] * 3, ['D3', 'A3', 'F#3']),
    (52.5, 3 * [BAR_S / 3], ['B4', 'B4', 'A4'], ['G2'] * 3, ['D3', 'G3', 'B3']),
    (55.0, 3 * [BAR_S / 3], ['G4', 'F#4', 'E4'], ['E2', 'E2', 'A2'], ['E3', 'G3', 'B3']),
    (57.5, 4 * [0.875], ['F#4', 'G4', 'A4', 'B4'], ['G2', 'G2', 'A2', 'A2'], ['D3', 'G3', 'B3']),
]
T_FINALE = 63.5                                   # every bulb is home: the sneak's tune in D major, 120 bpm
FIN_BEAT = 0.5
FINALE = [['D4', 'F#4', 'A4', 'F#4'], ['B4', 'A4', 'G4', 'E4'], ['D5']]


def score(M, G):
    from pixelhome.audio import SR, note, slide, whoosh
    n = note
    home, nb, bcol, kind, tw, gpath, t_steal, t_home = plan(G)
    st = steps()

    clar = M.sampler('Woodwinds/Clarinet/stac/*.wav', tune=-12)
    bsn = M.sampler('Woodwinds/Bassoon/stac/*.wav', tune=-12)
    cello = M.sampler('Strings/Cello Section/pizzT/*.wav', tune=-12)
    viola = M.sampler('Strings/Viola Section/pizz/*.wav', tune=-12)
    vln_p = M.sampler('Strings/Violin Section/Pizz/*.wav', tune=-12)
    cbass = M.sampler('Strings/Solo Contrabass/Pizz/*.wav', tune=-12)
    glock = M.sampler('Percussion/Glock/*.wav', tune=-12)
    xylo = M.sampler('Percussion/Xylo/*.wav', tune=-12)
    harp = M.sampler('Strings/Harp/*.wav')
    flute = M.sampler('Woodwinds/Flute/susvib/*.wav', tune=-12)
    vln = M.sampler('Strings/Violin Section/susVib/*.wav', tune=-12)
    vla = M.sampler('Strings/Viola Section/susvib/*.wav', tune=-12)
    vc = M.sampler('Strings/Cello Section/susvib/*.wav', tune=-12)
    trem = M.sampler('Strings/Violin Section/Trem/*.wav', tune=-12)
    horn = M.sampler('Brass/F Horn/sus/*.wav', tune=-12)
    horn_st = M.sampler('Brass/F Horn/stac/*.wav', tune=-12)
    tpt = M.sampler('Brass/Trumpet/stac/*.wav', tune=-12)
    tpt_s = M.sampler('Brass/Trumpet/sus/*.wav', tune=-12)
    tuba = M.sampler('Brass/Tuba/sus/*.wav', tune=-12)
    choir = M.synth('Pads/Ooh')
    tick = M.hits('VSCO 1 Percussion/varWood/claves_pp1.wav')
    sleigh = M.hits('Percussion/Sleighbells_Hit*.wav')
    sleigh_sh = M.hits('Miscellania Raw/Misc 2/sleighbell*_shake*.wav')
    chimes = M.hits('VSCO 1 Percussion/varMetal/various/windchimes_fastAsc1.wav')
    choke = M.hits('Percussion/cymbal-crashshort*.wav')
    crash = M.hits('VSCO 1 Percussion/varMetal/Cymbals/clash/crash_hit_ff*.wav')
    bd = M.hits('VSCO 1 Percussion/drums/bass/bdrum_f_*.wav')
    timp = M.hits('Percussion/Timpani/Timpani1_Hit_v[13]*.wav')
    troll = M.hits('Percussion/Timpani/Rolls/Timpani1_Roll_v3*.wav')
    tri = M.hits('Percussion/Triangle3-Hit_v1*.wav')

    for name, gain, rev in (('tune', 0.34, 0.16), ('pizz', 0.38, 0.1), ('harm', 0.3, 0.3), ('perc', 0.36, 0.14),
                            ('fx', 0.24, 0.2), ('sparkle', 0.22, 0.3), ('sing', 0.3, 0.35)):
        M.bus(name, gain=gain, reverb=rev)

    order = np.argsort(G.pd)
    xs, ds = G.pos[order, 0], G.pd[order]
    x0, x1 = xs.min(), xs.max()
    L = G.length

    def pan_at(dd):                          # path distance -> left/right across the facade, as seen from the street
        x = np.interp(np.clip(dd, 0, L), ds, xs)
        return float(0.85 * (2 * (x - x0) / (x1 - x0) - 1))

    def mono(sig, pans):                     # a mono signal panned sample by sample
        a = (np.clip(pans, -1, 1) + 1) * np.pi / 4
        return np.vstack([sig * np.cos(a), sig * np.sin(a)]) * np.sqrt(2)

    def tone(fr, amp, buzz=0.12):            # a whistle (or with buzz up, a kazoo) along a frequency curve
        ph = 2 * np.pi * np.cumsum(fr) / SR
        return amp * (np.sin(ph) + buzz * np.sin(2 * ph) + 0.6 * buzz * np.sin(3 * ph))

    def chord(names, octave):                # chord letters -> notes stacked upward from the octave given
        out, last = [], -1
        for c in names:
            m = n(c + str(octave))
            while m <= last:
                m += 12
            out.append(m)
            last = m
        return out

    pos = lambda t: float(walk(t))

    # ---- 0-3: the house is lit and all is well ----
    M.add('perc', sleigh_sh.play(95), 0.05, 0.7, -0.3)
    for i, m in enumerate(chord(('D', 'F#', 'A'), 3) + chord(('D', 'F#', 'A'), 4) + [n('D5')]):
        M.add('harm', harp.play(m, 80), 0.1 + 0.18 * i, 0.7, -0.6 + 0.2 * i)
    for i, m in enumerate(('A5', 'F#5', 'D6', 'A5')):
        M.add('sparkle', glock.play(n(m), 88), 0.6 + 0.45 * i, 0.9, [-0.5, 0.3, 0.6, -0.2][i])
    for m in ('F#4', 'A4', 'D5'):
        M.add('harm', vln.play(n(m), 60, dur=1.1, release=0.4), 1.5, 0.35)
    for m in ('D3', 'A3'):
        M.add('harm', vc.play(n(m), 60, dur=1.1, release=0.4), 1.5, 0.4)

    # ---- 3-47: the sneak. Every step a note: the tune lands with his foot, a pizz on the lift ----
    M.add('perc', timp.play(70, pitch=-2), 3.0, 0.6, pan_at(0))
    for i, (lift, land, p) in enumerate(st):
        pn = pan_at(p)
        M.add('perc', tick.play(70, pitch=float(M.rng.uniform(-1, 1))), land, 0.45, pn)
        if i < 2:                            # the peek: two heavy-footed low notes before he finds his tiptoes
            for inst, m in ((bsn, ('D2', 'A1')[i]), (cbass, ('D2', 'A1')[i])):
                M.add('tune' if inst is bsn else 'pizz', inst.play(n(m), 95), land, 0.9, pn * 0.5)
            continue
        k = (i - 2) % 16
        last = i == len(st) - 1
        mel, bas = ('D4', 'D2') if last else (SNEAK[k], SNEAK_BASS[k])
        M.add('tune', clar.play(n(mel), 96, dur=0.18), land, 0.8, 0.55 * pn)
        M.add('tune', bsn.play(n(mel) - 12, 100, dur=0.2), land, 0.75, 0.55 * pn)
        M.add('pizz', cello.play(n(bas), 105), land, 0.9, 0.3 * pn)
        if not last:
            M.add('pizz', viola.play(n(SNEAK_LIFT[k // 4][k % 2]), 70), lift, 0.5, 0.4 * pn)
        else:                                # all the way to the end: a satisfied low cadence
            M.add('pizz', cbass.play(n('D1') + 12, 115), land, 0.9, 0.5)
            M.add('perc', timp.play(90, pitch=-2), land, 0.6, pn)
            M.add('tune', bsn.play(n('A1'), 100, dur=0.2), land - 0.3, 0.7, 0.55 * pn)

    def chord_at(t):                         # which sneak chord is sounding at t
        landed = [i for i, (_, land, _) in enumerate(st) if land <= t and i >= 2]
        return SNEAK_CHORD[((landed[-1] - 2) % 16) // 4] if landed else SNEAK_CHORD[0]

    # every bulb reeled in: a little zip along the wire and a plink into the sack, a tone of the chord
    for b in np.argsort(t_steal):
        ta = t_steal[b] + REEL
        if ta > T_BURST:
            continue
        sx = pos(ta) - 15
        ch = chord_at(ta)
        m = n(ch[kind[b] % len(ch)] + '5')
        M.add('fx', slide(0.0, REEL, 700 + 60 * kind[b], 1600 + 90 * kind[b], REEL, 0.05, 0.8), t_steal[b], 1.0,
              pan_at(0.5 * (home[b] + sx)))
        M.add('sparkle', glock.play(m, int(M.rng.integers(62, 80))), ta, 0.7, pan_at(sx))

    # eyes blink: a tiny wooden blip where he is
    for tb in EYE_BLINKS:
        M.add('perc', xylo.play(n('A5'), 58, dur=0.1), tb - 0.04, 0.5, pan_at(pos(tb) + 3))

    # each corner: he stops and looks round. Tremolo strings hold their breath; a glance each way
    for a, b in LOOKS:
        p = pan_at(pos(a))
        for m in ('A3', 'E4'):
            M.add('harm', trem.play(n(m), 55, dur=b - a, release=0.15), a, 0.5, p * 0.5)
        M.add('perc', xylo.play(n('E5'), 75, dur=0.15), a + 0.25 * (b - a), 0.7, max(-1, p - 0.25))
        M.add('perc', xylo.play(n('C#5'), 75, dur=0.15), a + 0.75 * (b - a), 0.7, min(1, p + 0.25))

    # ---- 29-33: caught. A stab and wide eyes, the kid's lullaby, shooed back to bed ----
    pk = pan_at(1500)
    for m in ('C#4', 'E4', 'G4', 'Bb4'):
        M.add('harm', horn_st.play(n(m) - 12, 115, dur=0.25), T_CAUGHT, 0.6, -0.1)
        M.add('tune', tpt.play(n(m), 110, dur=0.25), T_CAUGHT, 0.45, 0.1)
        M.add('pizz', vln_p.play(n(m), 120), T_CAUGHT, 0.6)
    M.add('pizz', cello.play(n('C#2'), 120), T_CAUGHT, 1.0)
    M.add('perc', choke.play(110), T_CAUGHT, 0.6, pk)
    M.add('fx', slide(0.0, 0.3, 550, 1400, 0.36, 0.5), T_CAUGHT, 0.8, pan_at(1473))
    for t, m, d in ((30.3, 'A4', 0.45), (30.75, 'F#4', 0.45), (31.2, 'G4', 0.3), (31.5, 'E4', 0.3), (31.8, 'D4', 0.6)):
        M.add('sing', flute.play(n(m), 70, dur=d, release=0.3), t, 0.9, pk)
    for t, m in ((30.3, 'D3'), (30.5, 'A3'), (30.7, 'F#4'), (31.2, 'G3'), (31.4, 'B3'), (31.8, 'D3'), (32.0, 'A3')):
        M.add('harm', harp.play(n(m), 70), t, 0.6, pk)
    whistle = slide(0.0, 0.9, 1000, 420, 1.0, 0.35, 0.6)
    M.add('fx', mono(whistle[0], np.linspace(pk, pan_at(1530), whistle.shape[1])), 32.0, 0.6)
    M.add('perc', tri.play(60), 33.0, 0.4, pk)

    # ---- 47-61: a heavy sack teeters; the dark house begins to sing; something swells in him ----
    tt = np.arange(int(5.5 * SR)) / SR
    teeter = np.sin(2 * np.pi * tt / 1.3) * np.exp(-tt / 4)
    wob = tone(260 * 2 ** (teeter * 2.5 / 12), 0.25, 0.35) * np.exp(-tt / 2.5) * np.clip(tt / 0.05, 0, 1) * \
        np.clip((5.5 - tt) / 0.5, 0, 1)
    M.add('fx', mono(wob, np.full(len(tt), pan_at(2385))), 47.5, 0.9)

    # the house: an "ooh" rising out of the porch, swelling with the lights' slow ripples
    seg = int((63.0 - T_SING) * SR)
    pad = np.zeros((2, seg))
    pchords = [(T_SING, ('D3', 'A3', 'F#4')), (52.5, ('D3', 'G3', 'B3')), (55.0, ('E3', 'G3', 'B3')),
               (56.67, ('E3', 'G3', 'C#4')), (57.5, ('D3', 'G3', 'B3')), (59.25, ('E3', 'A3', 'C#4')),
               (61.0, ('D3', 'F#3', 'A3', 'D4'))]
    for j, (t0, ms) in enumerate(pchords):
        t1 = pchords[j + 1][0] if j + 1 < len(pchords) else 63.0
        a = choir.render([(0.0, n(m), 70, t1 - t0) for m in ms], t1 - t0 + 1.5)
        s0 = int((t0 - T_SING) * SR)
        k = min(a.shape[1], seg - s0)
        pad[:, s0:s0 + k] += a[:, :k]
    ts = np.arange(seg) / SR
    amp = np.interp(ts + T_SING, [48, 50, 60, 63], [0, 1, 1, 0])
    swell = 0.5 + 0.5 * np.sin(2 * np.pi * ts * 0.9)
    M.add('sing', pad * amp * (0.7 + 0.3 * swell ** 2), T_SING, 1.6, pan_at(1476))
    for i, m in enumerate(('D3', 'A3', 'D4', 'F#4', 'A4')):            # the first stirrings: a soft harp roll
        M.add('harm', harp.play(n(m), 55), 48.3 + 0.35 * i, 0.5, pan_at(1476) + 0.1 * (i - 2))
    for t0, beats, mel, bas, chd in CHORALE:
        t = t0
        for j, (dur, m, bm) in enumerate(zip(beats, mel, bas)):
            if j == 0 or m != mel[j - 1]:            # a repeated note is held through
                same = 1
                while j + same < len(mel) and mel[j + same] == m:
                    same += 1
                hold = sum(beats[j:j + same])
                M.add('sing', flute.play(n(m), 82, dur=hold * 0.95, release=0.25), t, 0.9, 0.1)
                M.add('harm', vln.play(n(m), 70, dur=hold * 0.95, release=0.3), t, 0.4, -0.1)
            M.add('harm', vc.play(n(bm), 72, dur=dur * 0.95, release=0.3), t, 0.55, -0.2)
            t += dur
        for m in chd:
            M.add('harm', vla.play(n(m), 60, dur=sum(beats) * 0.97, release=0.4), t0, 0.35, 0.2)
        M.add('harm', horn.play(n(chd[0]), 60, dur=sum(beats) * 0.95, release=0.4), t0, 0.3, 0.3)

    # his heart: lub-dub on the timpani, where he stands, louder at each stage
    ph = pan_at(2400)
    for s, (t0, r) in enumerate(STAGES):
        for j in range(3):
            M.add('perc', timp.play(78 + 14 * s, pitch=-2), t0 + j * 0.8 + 0.03, 0.8, ph)
            M.add('perc', timp.play(60 + 12 * s, pitch=-2), t0 + j * 0.8 + 0.25, 0.6, ph)
        M.add('sparkle', glock.play(n(('D5', 'F#5', 'A5')[s]), 70), t0 + 0.03, 0.5, ph)
    r = troll.play(90, dur=1.6)
    M.add('perc', r * np.linspace(0.05, 1, r.shape[1]) ** 2, T_BURST - 1.5, 0.7, ph)

    # ---- 61: the burst. Every bulb flies home ----
    pb_ = pan_at(T_BURST_X)
    M.add('perc', crash.play(118), T_BURST, 0.7, pb_ * 0.6)
    M.add('perc', bd.play(118), T_BURST, 0.9, pb_ * 0.5)
    M.add('perc', timp.play(115, pitch=-2), T_BURST, 0.8, pb_)
    for m in ('D4', 'F#4', 'A4'):
        M.add('tune', tpt_s.play(n(m), 110, dur=1.2, release=0.5), T_BURST, 0.5, 0.3)
    for m in ('D3', 'A3', 'F#3'):
        M.add('harm', horn.play(n(m), 110, dur=1.4, release=0.6), T_BURST, 0.6, 0.2)
    M.add('pizz', tuba.play(n('D2'), 110, dur=1.4, release=0.5), T_BURST, 0.8)
    for i, m in enumerate(chord(('D', 'F#', 'A'), 5) + [n('D6')]):
        M.add('sparkle', glock.play(m, 100), T_BURST + 0.07 * i, 0.7, pb_)
    fly = whoosh(2.4, 500, 3500, 0.9, seed=61)
    M.add('fx', mono(fly[0], np.linspace(pb_, -0.7, fly.shape[1])), T_BURST + 0.1, 0.8)
    gl = chord(('D', 'F#', 'A'), 3) + chord(('D', 'F#', 'A'), 4) + chord(('D', 'F#', 'A'), 5)
    for i, m in enumerate(gl):                                         # the harp rides them home
        M.add('harm', harp.play(m, 85), T_BURST + 0.2 + 1.9 * i / len(gl), 0.7, pb_ - 1.4 * i / len(gl))
    land = t_home + FLY
    M.add('sparkle', chimes.play(100), float(land.min()) - 0.1, 0.7)
    M.add('perc', sleigh_sh.play(110), float(land.min()), 0.7)
    for b in np.argsort(land)[::7]:                                     # landings: a shower of glass all along the roof
        M.add('sparkle', glock.play(n(('D5', 'F#5', 'A5', 'D6', 'E5', 'B5')[kind[b]]), 72), float(land[b]), 0.35,
              pan_at(home[b]))

    # ---- 63.5-72: every bulb home and the sneak's tune in D major, sleigh bells on ----
    fchords = [[('D', 'F#', 'A')], [('G', 'B', 'D'), ('A', 'C#', 'E', 'G')], [('D', 'F#', 'A')]]
    fbass = [['D2', 'A1'], ['G2', 'A1'], ['D2']]
    for k, bar in enumerate(FINALE):
        t0 = T_FINALE + 4 * FIN_BEAT * k
        for j, m in enumerate(bar):
            d = FIN_BEAT if len(bar) > 1 else 4 * FIN_BEAT
            inst = tpt if len(bar) > 1 else tpt_s
            M.add('tune', inst.play(n(m), 108, dur=d * 0.9, release=0.6 if len(bar) == 1 else 0.12), t0 + j * FIN_BEAT,
                  0.9)
            M.add('tune', clar.play(n(m), 90, dur=d * 0.6), t0 + j * FIN_BEAT, 0.5, -0.2)
            M.add('sparkle', glock.play(n(m) + 12, 80), t0 + j * FIN_BEAT, 0.4, 0.25)
        for h, ch in enumerate(fchords[k]):
            th = t0 + h * 2 * FIN_BEAT
            dh = 4 * FIN_BEAT / len(fchords[k])
            for m in chord(ch, 3):
                M.add('harm', horn.play(m, 95, dur=dh * (0.95 if k < 2 else 1.5), release=0.5), th, 0.45, -0.25)
                M.add('harm', vln.play(m + 12, 80, dur=dh * (0.95 if k < 2 else 1.5), release=0.5), th, 0.3, 0.25)
        for h, bm in enumerate(fbass[k]):
            M.add('pizz', tuba.play(n(bm), 104, dur=0.8 if k < 2 else 2.6, release=0.4), t0 + h * 2 * FIN_BEAT, 0.8)
        if k < 2:
            for e in range(8):
                tb = t0 + e * FIN_BEAT / 2
                M.add('perc', sleigh.play(105 if e % 2 == 0 else 80), tb, 0.5, 0.35 if e % 2 else -0.35)
                if e % 2 == 0:
                    M.add('pizz', cello.play(n(fbass[k][(e // 4) % len(fbass[k])]) + 12, 90), tb + FIN_BEAT / 2, 0.5)
    tf = T_FINALE + 4 * FIN_BEAT * 2
    r = troll.play(95, dur=0.6)
    M.add('perc', r * np.linspace(0.1, 1, r.shape[1]) ** 2, tf - 0.55, 0.6)
    M.add('perc', crash.play(110), tf, 0.6)
    M.add('perc', bd.play(110), tf, 0.8)
    M.add('perc', sleigh_sh.play(100), tf, 0.6)
    for i, m in enumerate(chord(('D', 'F#', 'A'), 5) + [n('D6')]):
        M.add('sparkle', glock.play(m, 85), tf + 0.12 * i, 0.5, -0.4 + 0.27 * i)
