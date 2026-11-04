"""Carolers: A snowy night, every window dark. Three carolers with warm lanterns walk in from the free end of
Right and stop at the first window; when they sing it lights up warm, little sparks of song flying out from
them on every note, and a neighbour steps out of it with a lantern of her own colour and joins in. Window by
window along Right, Porch Right and across the porch the group grows and so do its colours. A dog trots out of
the front door and howls along, off-key; the second time the whole group stops dead and glares at him. They move
on along Porch Left and Left, louder at every stop and quicker between them, and at the last window the final
chorus breaks out of them and runs both ways across the whole house: every window blazes, colour ripples out on
every beat, the key lifts, it hushes for one bar of only lanterns and windows, and the amen fills the house.

Music: an original carol in D at 96 crotchets a minute, four two-bar phrases, sung at each window. The group's
sound grows with it: a lone choir voice and a handbell at the first window, then flute, clarinet, a brass quartet
and strings as neighbours join, each joining on a handbell note; a chime as each window lights; pizzicato walking
bass, sleigh bells and crunching footsteps between stops. The dog's howls are a wobbling, off-key slide; the
second one stops the band dead for a glare and a yip. The final chorus is the whole lot with timpani and bells,
up a step to E for the last phrases, a hushed bar, and a big amen."""
import numpy as np
from pixelhome.fx import DT, hexc, light, keys, smoothstep, lerp, Flicker, nframes

CODE = 'XM16'
TITLE = 'Carolers'
KIND = 'show'
DESCRIPTION = ('Lantern-carrying carolers walk in from the end of the house; every window they sing to lights up and '
               'a neighbour joins in, a dog howls along off-key, and the final chorus sets every window blazing.')
VOICEOVER = "Listen. Carolers are coming down the street, and every window they sing to lights up."

D = 86.0
SEED = 16

NIGHT = hexc('#0a1c90')
FLAKE = hexc('#dce8ff')
FRAME = hexc('#4060c0')
WARM = hexc('#ffa030')
BLAZE = hexc('#ffc060')
LANTERN = hexc('#ffc050')
DOG = hexc('#ff7010')
HOWL = hexc('#fff0a0')
JOINERS = [hexc(c) for c in ('#ff1010', '#10e040', '#2050ff', '#ff10a0', '#00d0ff', '#ff6000', '#9020ff', '#c0ff10')]

END = 2512.0
T0, BEAT = 1.0, 0.625                       # 96 crotchets a minute; a bar is 2.5 s
BAR = 4 * BEAT


def bt(bar, beat=0.0):
    return T0 + bar * BAR + beat * BEAT


# the windows along the path (Side 0-490, Left 492-892, Porch Left 896-1309, Porch Front 1314-1658,
# Porch Right 1662-2030, Right 2036-2512); the Side's two only light in the final chorus
WINDOWS = [2420, 2250, 2100, 1850, 1560, 1410, 1100, 800, 620, 330, 130]
WIN_W = 22.0
# the stops: (window, first bar of singing, bars sung, phrase(s)); the group walks between them
STOPS = [(0, 2, 2, 0), (1, 5, 2, 1), (2, 8, 2, 2), (3, 11, 2, 3), (4, 14, 2, 0), (5, 17, 2, 1), (6, 20, 2, 2),
         (7, 23, 1, 3), (8, 24.5, 0.5, 3.5)]
T_DOG = bt(13)                              # the dog trots out of the front door
HOWLS = [(bt(15), 0.9), (bt(15, 2), 0.9), (bt(18), 2.1)]   # (time, length); the last one stops the song
T_GLARE, T_YIP = bt(18, 2), bt(18, 3.4)
T_CHORUS, T_LIFT, T_HUSH, T_AMEN = bt(25), bt(29), bt(31), bt(32)
CHORUS_V = 700.0                            # the final chorus runs out from the group this fast
DOOR = 1486.0
SPACING = 15.0


def stop_t(i):
    w, b, nb, _ = STOPS[i]
    return bt(b), bt(b + nb)


def centre(t):
    """The middle of the group: walking from the end of Right, standing at each window while they sing."""
    pts = [(T0 - 0.2, END + 40)]
    for i, (w, b, nb, _) in enumerate(STOPS):
        s0, s1 = stop_t(i)
        pts += [(s0 - 0.15, WINDOWS[w]), (s1, WINDOWS[w])]
    return float(keys(t, pts))


def members(t):
    """How many in the group at t: three, and one more after each of the first eight windows."""
    n = 3
    for i in range(min(8, len(STOPS))):
        if t >= joined(i):
            n += 1
    return n


def joined(i):
    """A neighbour steps out of window i in the last bar of the song there."""
    s0, s1 = stop_t(i)
    return s1 - BAR * 0.5 if STOPS[i][2] >= 1 else s1 - 0.3


def dog_pos(t):
    """The dog waits by the front door for the group, then trots along at its front."""
    def front(tt):
        return centre(tt) - (SPACING * (members(tt) - 1) / 2 + 10) - 24
    if t < bt(13, 2):
        return DOOR
    if t < bt(14):
        return float(lerp(DOOR, front(bt(14)), smoothstep(bt(13, 2), bt(14), t)))
    return front(t)


def walking(t):
    for i in range(len(STOPS)):
        s0, s1 = stop_t(i)
        if s0 - 0.15 <= t < s1:
            return False
    return t < T_CHORUS


# ---- the carol: four two-bar phrases in D, (beat, note, beats) ----
PHRASES = [
    [[(0, 'A4', 1), (1, 'D5', 1), (2, 'C#5', 1), (3, 'B4', 1)], [(0, 'A4', 1.5), (1.5, 'G4', .5), (2, 'F#4', 2)]],
    [[(0, 'G4', 1), (1, 'B4', 1), (2, 'A4', 1), (3, 'F#4', 1)], [(0, 'E4', 1), (1, 'F#4', .5), (1.5, 'G4', .5), (2, 'A4', 2)]],
    [[(0, 'B4', 1), (1, 'B4', 1), (2, 'C#5', 1), (3, 'D5', 1)], [(0, 'E5', 1.5), (1.5, 'D5', .5), (2, 'B4', 2)]],
    [[(0, 'A4', 1), (1, 'F#4', 1), (2, 'G4', 1), (3, 'E4', 1)], [(0, 'D4', 4)]],
]
HARMONY = [  # two chords a bar
    [('D', 'A'), ('D', 'D')], [('G', 'D'), ('A', 'A7')], [('G', 'A'), ('Bm', 'G')], [('D', 'A7'), ('D', 'D')],
]
CHORDS = {   # bass, then the upper voices (alto, tenor) under the tune
    'D': ('D2', ('F#3', 'A3', 'D4')), 'A': ('A1', ('E3', 'A3', 'C#4')), 'A7': ('A1', ('E3', 'G3', 'C#4')),
    'G': ('G1', ('D3', 'G3', 'B3')), 'Bm': ('B1', ('F#3', 'B3', 'D4')), 'E7': ('E2', ('B2', 'D3', 'G#3')),
}


def sung():
    """Every melody note the carolers sing: (time, note name, beats, transpose, stop or -1 for the chorus)."""
    out = []
    for i, (w, b, nb, ph) in enumerate(STOPS):
        if nb >= 1:
            bars = PHRASES[ph][:int(nb)]
            for j, bar in enumerate(bars):
                for beat, m, ln in bar:
                    t = bt(b + j, beat)
                    if i == 5 and j == 1 and beat >= 2:            # the glare: the song stops dead
                        continue
                    out.append((t, m, ln, 0, i))
        else:                                                      # the last stop: just the closing note
            out.append((bt(b), 'D4', 2, 0, i))
    for k, ph in enumerate((0, 0, 1, 1, 2, 2, 3, 3)):              # the chorus: bars 25-32
        bar = PHRASES[ph][k % 2]
        tr = 2 if k >= 4 else 0
        for beat, m, ln in bar:
            out.append((bt(25 + k, beat), m, ln, tr, -1))
    return out


def plan(seed=SEED):
    rng = np.random.default_rng(seed)
    notes = sung()
    sparks = rng.uniform(0, 1, (len(notes), 4))
    steps = []                                                     # footsteps in the snow while walking
    t = T0
    while t < T_CHORUS:
        if walking(t):
            steps.append(t)
        t += BEAT / 2
    return notes, sparks, steps


def render(G, seed=SEED):
    rng = np.random.default_rng(seed)
    F = nframes(D)
    out = np.zeros((F, G.N, 3))
    x = G.pd[G.path]
    notes, sparks, steps = plan(seed)
    flakes = Flicker(rng, G.N, 0.06, 0.4)
    candle = Flicker(rng, len(WINDOWS), 0.4, 1.6)
    lant = Flicker(rng, 12, 0.8, 2.5)
    wx = np.array(WINDOWS, float)
    win_d = x[:, None] - wx[None]
    pane = (np.abs(win_d) < WIN_W) * (1 - 0.85 * np.exp(-(win_d / 2.5) ** 2))   # a window with a bar down the middle
    frame = np.exp(-((np.abs(win_d) - WIN_W) / 3) ** 2)
    lit_at = np.full(len(WINDOWS), 1e9)
    for i, (w, b, nb, _) in enumerate(STOPS):
        lit_at[w] = bt(b)
    # in the chorus, each window still dark blazes as the chorus reaches it
    c_from = WINDOWS[STOPS[-1][0]]
    chorus_at = T_CHORUS + np.abs(wx - c_from) / CHORUS_V
    lit_at = np.minimum(lit_at, chorus_at)
    cols = [LANTERN, LANTERN, LANTERN] + JOINERS

    for f in range(F):
        t = f * DT
        fr = np.zeros((G.N, 3))
        master = keys(t, [(0, 0), (0.8, 1), (D - 1.6, 1), (D - 0.1, 0)])
        c = centre(t)
        n = members(t)
        chorus = t >= T_CHORUS
        hush = smoothstep(T_HUSH - 0.2, T_HUSH + 0.3, t) * (1 - smoothstep(T_AMEN - 0.05, T_AMEN, t))
        reached = chorus * smoothstep(CHORUS_V * (t - T_CHORUS) + 40, CHORUS_V * (t - T_CHORUS) - 40, np.abs(x - c_from))

        # the night: blue with snow glittering, warming to gold behind the chorus
        tw = np.clip(flakes(t), 0, None) ** 4
        fr += light(NIGHT, 0.2 * (1 - reached)) + light(FLAKE, 0.3 * tw)
        fr += light(BLAZE, reached * (0.32 - 0.18 * hush - 0.17 * (T_CHORUS + 0.8 <= t < T_HUSH)))

        # windows: a cool frame while dark; warm, candle-flickering panes once sung to; blazing in the chorus
        on = smoothstep(lit_at, lit_at + 0.8, t)
        flash = np.exp(-np.clip(t - lit_at, 0, None) / 0.35) * (t >= lit_at)
        blaze = smoothstep(chorus_at, chorus_at + 0.4, t)
        lvl = on * (0.62 + 0.05 * candle(t)) + 0.4 * flash + 0.3 * blaze
        fr += light(WARM, (pane * lvl[None]).max(1))
        fr += light(FRAME, (frame * (0.32 * (1 - on))[None]).max(1))
        fr += light(BLAZE, (frame * (0.7 * on * (0.4 + 0.6 * blaze))[None]).max(1))

        # the group's song: a warm halo while they sing, wider and more colourful as the group grows
        singing = not walking(t) and t >= stop_t(0)[0] and not (T_GLARE <= t < bt(19))
        width = SPACING * (n - 1) / 2 + 10
        if singing and not chorus:
            k_loud = 0.5 + 0.5 * n / 11
            halo = np.exp(-((x - c) / (width + 30 + 40 * k_loud)) ** 2)
            mix = np.mean(cols[:n], axis=0)
            fr += light(lerp(LANTERN, mix, 0.6), 0.45 * k_loud * halo)

        # sparks of song: every sung note throws two sparks out from the singers, in the singers' colours
        for (tn, m, ln, tr, stop), (a0, a1, a2, a3) in zip(notes, sparks):
            a = t - tn
            if not (0 <= a < 1.2):
                continue
            cc = centre(tn)
            nn = members(tn)
            col = cols[int(a0 * nn) % len(cols)]
            reach = 90 + 160 * a1 + (250 if stop < 0 else 0)
            for side in (-1, 1):
                p = cc + side * (width * 0.5 + reach * (1 - np.exp(-a / 0.4)))
                e = (1 - a / 1.2) ** 1.5
                fr += light(col, 0.85 * e * np.exp(-((x - p) / 6) ** 2))

        # the carolers: lanterns swinging as they walk, bobbing gently as they sing
        for j in range(n):
            off = (j - (n - 1) / 2) * SPACING
            if j >= 3:                                   # a neighbour steps out of the window and the group spreads
                tj = joined(j - 3)
                u = smoothstep(tj, tj + 0.8, t)
                off *= u
                pop = np.exp(-(t - tj) / 0.2)
            else:
                pop = 0.0
            bob = 3 * np.sin(2 * np.pi * (t / (2 * BEAT) + 0.3 * j)) if walking(t) else 0.0
            p = c + off + bob
            glare = 0.6 * np.exp(-max(t - T_GLARE, 0) / 0.5) * (T_GLARE <= t < bt(19))
            lv = 0.85 * (1 + 0.08 * lant(t)[j % 12]) + 0.6 * pop + glare
            if chorus:
                lv += 0.25 * (0.5 + 0.5 * np.cos(2 * np.pi * (t - T_CHORUS) / BEAT))
            fr += light(cols[j], lv * np.exp(-((x - p) / 5.5) ** 2))
            fr += light(cols[j], 0.35 * lv * np.exp(-((x - p) / 14) ** 2))

        # footsteps: a soft crunch of snow under them on every quaver they walk
        for ts in steps:
            a = t - ts
            if 0 <= a < 0.25:
                fr += light(FLAKE, 0.35 * np.exp(-a / 0.08) * np.exp(-((x - centre(ts) - width - 8) / 6) ** 2))

        # the dog: out of the front door, trotting to the group's front, howling, then tagging along at the front
        if t >= T_DOG:
            dp = dog_pos(t)
            wag = 0.5 + 0.5 * np.sin(2 * np.pi * 4 * t)
            fr += light(DOG, 0.95 * np.exp(-((x - dp) / 6) ** 2))
            fr += light(DOG, 0.5 * wag * np.exp(-((x - dp - 11) / 3.5) ** 2))     # the tail
            for th, ln in HOWLS + [(T_YIP, 0.25)]:
                a = t - th
                if 0 <= a < ln + 0.5:
                    e = np.clip(a / 0.15, 0, 1) * np.clip((ln + 0.5 - a) / 0.5, 0, 1)
                    wob = 0.75 + 0.25 * np.sin(2 * np.pi * 7 * a)
                    r = 20 + 120 * min(a, ln) / ln * (ln / 2.1) ** 0.5
                    fr += light(HOWL, 1.1 * e * wob * np.exp(-((x - dp + 4) / 9) ** 2))
                    fr += light(HOWL, 0.8 * e * wob * np.exp(-((np.abs(x - dp) - r) / 18) ** 2))

        # the chorus breaks out of the group and runs both ways across the house; colour ripples out on every beat
        if chorus:
            a = t - T_CHORUS
            frontd = CHORUS_V * a
            d = np.abs(x - c_from)
            fr += light(BLAZE, 0.9 * np.exp(-((d - frontd) / 50) ** 2) * (frontd < 2100))
            ph = (t - T_CHORUS) / BEAT
            k = int(ph)
            b = (ph % 1) * BEAT
            fd = 40 + 3200 * b                           # each beat a new colour pours out of the group
            now = smoothstep(fd + 30, fd - 30, d) * (0.55 - 0.15 * b / BEAT)
            was = smoothstep(fd - 30, fd + 30, d) * 0.4 * (k > 0)
            on_ = reached * (1 - hush) * (t < T_LIFT)
            fr += light(JOINERS[k % len(JOINERS)], now * on_) + light(JOINERS[(k - 1) % len(JOINERS)], was * on_)
            if t >= T_LIFT:                              # the key lifts: a second wave of every colour
                a2 = t - T_LIFT
                fd = CHORUS_V * 1.5 * a2
                band = ((d - fd) / 45) % len(JOINERS)
                i0 = np.floor(band).astype(int) % len(JOINERS)
                colr = np.array(JOINERS)[i0]
                fr += colr * (0.62 * (d < fd) * (1 - hush) * (t < T_AMEN))[:, None] ** 2.2
            if t >= T_AMEN:                              # amen: the whole house warm and bright
                a3 = t - T_AMEN
                fr += light(BLAZE, (0.95 * np.exp(-a3 / 0.6) + 0.35) * np.ones(G.N))
                fr += light(WARM, 0.5 * np.ones(G.N) * smoothstep(0, 0.3, a3))

        out[f][G.path] = np.clip(fr, 0, 1) * master ** 2.2
    return out


def score(M, G):
    from pixelhome.audio import SR, note, slide
    n = note
    notes, sparks, steps = plan()

    choir = M.synth('Pads/Synth Choir MW O-Ah')
    ooh = M.synth('Pads/Ooh')
    flute = M.sampler('Woodwinds/Flute/susvib/*.wav', tune=-12)
    clar = M.sampler('Woodwinds/Clarinet/susLong/*.wav', tune=-12)
    tpt = M.sampler('Brass/Trumpet/sus/*.wav', tune=-12)
    horn = M.sampler('Brass/F Horn/sus/*.wav', tune=-12)
    bone = M.sampler('Brass/Tenor Trombone/sus/*.wav', tune=-12)
    tuba = M.sampler('Brass/Tuba/sus/*.wav', tune=-12)
    vln = M.sampler('Strings/Violin Section/susVib/*.wav', tune=-12)
    vla = M.sampler('Strings/Viola Section/susvib/*.wav', tune=-12)
    vc = M.sampler('Strings/Cello Section/susvib/*.wav', tune=-12)
    cb = M.sampler('Strings/Solo Contrabass/Pizz/*.wav', tune=-12)
    vc_p = M.sampler('Strings/Cello Section/pizzT/*.wav', tune=-12)
    harp = M.sampler('Strings/Harp/*.wav')
    glock = M.sampler('Percussion/Glock/*.wav', tune=-12)
    hymn = M.synth('Pads/Ooh')
    bells = M.hits('Percussion/Sleighbells_Hit*.wav')
    shake = M.hits('VSCO 1 Percussion/varMetal/various/sleighbell[12]_shake1.wav')
    chimes = M.hits('VSCO 1 Percussion/varMetal/various/windchimes_asc1.wav')
    crunch = M.hits('VSCO 1 Percussion/varWood/Camo\'s Shaker/*.wav')
    tri = M.hits('Percussion/Triangle3-Hit_v1*.wav')
    timp = M.hits('Percussion/Timpani/Timpani1_Hit_v[13]*.wav')
    troll = M.hits('Percussion/Timpani/Rolls/Timpani1_Roll_v3*.wav')
    crash = M.hits('Percussion/cymbal-crash1_ff*.wav')
    choke = M.hits('Percussion/cymbal-crashshort*.wav')
    tree = M.hits('Percussion/BellTree_Stroke*.wav')
    door = M.hits('VSCO 1 Percussion/varWood/wood_click_mp.wav')

    for name, gain, rev in (('tune', 0.32, 0.25), ('voices', 0.36, 0.3), ('brass', 0.3, 0.25), ('strings', 0.26, 0.28),
                            ('bass', 0.34, 0.12), ('perc', 0.32, 0.18), ('fx', 0.32, 0.2), ('sparkle', 0.22, 0.32)):
        M.bus(name, gain=gain, reverb=rev)

    order = np.argsort(G.pd)
    xs, ds = G.pos[order, 0], G.pd[order]
    x0, x1 = xs.min(), xs.max()

    def pan_at(dd):
        x = np.interp(np.clip(dd, 0, G.length), ds, xs)
        return float(0.85 * (2 * (x - x0) / (x1 - x0) - 1))

    def mono(sig, pans):
        a = (np.clip(pans, -1, 1) + 1) * np.pi / 4
        return np.vstack([sig * np.cos(a), sig * np.sin(a)]) * np.sqrt(2)

    def chord_at(t):
        """The chord under the tune at t, and its transposition (the chorus lifts to E at bar 29)."""
        bar = (t - T0) / BAR
        tr = 2 if t >= T_LIFT else 0
        for i, (w, b, nb, ph) in enumerate(STOPS):
            if b <= bar < b + max(nb, 0.5):
                j = int(bar - b) if nb >= 1 else 1
                return HARMONY[int(ph)][min(j, 1)][int((bar % 1) * 2)], tr
        if bar >= 25:
            k = int(bar - 25)
            ph = (0, 0, 1, 1, 2, 2, 3, 3, 3, 3)[min(k, 9)]
            return HARMONY[ph][k % 2 if k < 8 else 1][int((bar % 1) * 2) if k < 8 else 1], tr
        return 'D', 0

    # who sings at each stop: the sound grows as the group does
    LAYERS = {0: ('choir',), 1: ('choir', 'flute'), 2: ('choir', 'flute', 'clar'), 3: ('choir', 'flute', 'brass'),
              4: ('choir', 'flute', 'brass', 'strings'), 5: ('choir', 'flute', 'brass', 'strings'),
              6: ('choir', 'tpt', 'brass', 'strings', 'clar'), 7: ('choir', 'tpt', 'brass', 'strings', 'flute'),
              8: ('choir', 'tpt', 'brass', 'strings', 'flute'), -1: ('choir', 'tpt', 'brass', 'strings', 'flute', 'clar')}

    # ---- the tune, on whatever has joined, panned to where the group stands ----
    cnotes, onotes = [], []
    for tn, m, ln, tr, stop in notes:
        p = pan_at(centre(tn)) * (0.4 if stop < 0 else 1.0)
        d = ln * BEAT * 0.95
        mm = n(m) + tr
        loud = 86 + 3 * max(stop, 0) if stop >= 0 else 106
        lay = LAYERS[stop]
        if stop < 0 and T_HUSH <= tn < T_AMEN:         # the hushed bar: the choir and a flute, softly
            loud, lay = 72, ('choir', 'flute')
        cnotes.append((tn, mm, min(127, loud + 6), d))
        if 'flute' in lay:
            M.add('tune', flute.play(mm, loud, dur=d, release=0.3), tn, 0.6, p)
        if 'tpt' in lay:
            M.add('tune', tpt.play(mm, loud, dur=d, release=0.3), tn, 0.7, p)
        if 'clar' in lay:
            M.add('tune', clar.play(mm - 12, loud - 10, dur=d, release=0.3), tn, 0.4, p)
        if stop >= 0 and stop < 3:                    # the first stops: a handbell on the first note of each bar
            if abs(((tn - T0) / BAR) % 1) < 1e-6:
                M.add('sparkle', glock.play(mm, 70), tn, 0.4, p)
    M.add('voices', choir.render(cnotes, D + 1), 0.0, 0.9)

    # the harmony under each stop and the chorus: brass quartet, strings, an ooh, and the bass
    def harmonise(t0, t1, stop, gain=1.0):
        lay = LAYERS[stop]
        p = pan_at(centre(t0)) * (0.4 if stop < 0 else 1.0)
        t = t0
        while t < t1 - 1e-6:
            c, tr = chord_at(t + 0.01)
            bass, mid = CHORDS[c]
            d = 2 * BEAT * 0.97
            vel = (80 + 3 * max(stop, 0)) if stop >= 0 else 102
            onotes.extend((t, n(m) + tr, vel - 10, d) for m in mid)
            if 'brass' in lay:
                for inst, m in ((horn, mid[1]), (horn, mid[2]), (bone, mid[0])):
                    M.add('brass', inst.play(n(m) + tr, vel, dur=d, release=0.3), t, 0.4 * gain, p)
                M.add('brass', tuba.play(n(bass) + tr + 12, vel, dur=d, release=0.3), t, 0.5 * gain, p)
            if 'strings' in lay:
                for m in mid:
                    M.add('strings', vla.play(n(m) + tr, vel - 6, dur=d, release=0.4), t, 0.35 * gain, p + 0.1)
                M.add('strings', vc.play(n(bass) + tr + 12, vel - 4, dur=d, release=0.4), t, 0.45 * gain, p)
            M.add('bass', cb.play(n(bass) + tr + 12, vel + 10), t, 0.7 * gain, p)
            t += 2 * BEAT

    for i, (w, b, nb, ph) in enumerate(STOPS):
        s0, s1 = stop_t(i)
        if i == 5:                                    # the glare cuts the harmony off too
            s1 = T_GLARE
        harmonise(s0, s1, i)
    harmonise(T_CHORUS, T_HUSH, -1)
    M.add('voices', ooh.render(onotes, D + 1), 0.0, 0.6)

    # every window lights on a chime where it is; a neighbour steps out on a door click and a handbell
    for i, (w, b, nb, ph) in enumerate(STOPS):
        s0, _ = stop_t(i)
        p = pan_at(WINDOWS[w])
        M.add('sparkle', chimes.play(70 + 4 * i), s0 - 0.05, 0.35, p)
        c, tr = chord_at(s0 + 0.01)
        for k, m in enumerate(CHORDS[c][1]):
            M.add('sparkle', harp.play(n(m) + 12, 80), s0 + 0.05 * k, 0.5, p)
        if i < 8:
            tj = joined(i)
            M.add('perc', door.play(90), tj - 0.1, 0.5, p)
            M.add('sparkle', glock.play(n(('D5', 'F#5', 'A5', 'D6', 'E5', 'G5', 'B5', 'C#6')[i]), 92), tj, 0.55, p)
    # the Side's windows blaze as the chorus reaches them
    c_from = WINDOWS[STOPS[-1][0]]
    for w in (9, 10):
        ta = T_CHORUS + abs(WINDOWS[w] - c_from) / CHORUS_V
        M.add('sparkle', glock.play(n(('A5', 'D6')[w - 9]), 90), ta, 0.5, pan_at(WINDOWS[w]))

    # ---- walking: footsteps in the snow, pizzicato walking bass, sleigh bells ----
    for k, ts in enumerate(steps):
        p = pan_at(centre(ts))
        M.add('perc', crunch.play(60 + 10 * (k % 2)), ts, 0.3, p)
        if k % 2 == 0:
            c, tr = chord_at(ts)
            bass = CHORDS[c][0]
            walk = [0, 4, 7, 9][(k // 2) % 4]
            M.add('bass', vc_p.play(n(bass) + 12 + walk, 84), ts, 0.6, p)
            M.add('perc', bells.play(80), ts, 0.25, p)
    M.add('perc', shake.play(70), T0, 0.3, pan_at(END))
    M.add('perc', tree.play(80), 0.2, 0.3, 0.8)
    for k, m in enumerate(('D5', 'A4', 'F#4', 'D4')):     # a handbell intro from the end of Right
        M.add('sparkle', glock.play(n(m), 80), 0.3 + 0.35 * k, 0.5, 0.9)

    # ---- the dog: out of the door, howls off-key, a glare, a yip ----
    pd_ = pan_at(DOOR)
    M.add('perc', door.play(100), T_DOG, 0.6, pd_)
    for k in range(6):
        M.add('perc', door.play(50, pitch=6), T_DOG + 1.2 + 0.12 * k, 0.25, pd_)        # paws on the boards

    def howl(t0, ln, f0, f1, amp):
        tt = np.arange(int((ln + 0.3) * SR)) / SR
        u = np.clip(tt / ln, 0, 1)
        f = f0 * (f1 / f0) ** np.sin(np.pi * 0.5 * np.minimum(u * 1.6, 1)) * (1 - 0.25 * smoothstep(0.7, 1.0, u))
        f *= 2 ** (0.4 * np.sin(2 * np.pi * 6 * tt) / 12)
        ph = 2 * np.pi * np.cumsum(f) / SR
        env = np.clip(tt / 0.08, 0, 1) * np.clip((ln + 0.3 - tt) / 0.35, 0, 1)
        sig = amp * env * (np.sin(ph) + 0.35 * np.sin(2 * ph) + 0.15 * np.sin(3 * ph))
        return sig

    for k, (th, ln) in enumerate(HOWLS):
        p = pan_at(dog_pos(th))
        # aimed between the notes of the chord: a quarter-tone flat of a fifth above the tune
        f0 = 440 * 2 ** ((n('A4') - 69 - 0.5) / 12)
        sig = howl(th, ln, f0 * 0.8, f0 * (1.4 if k < 2 else 1.6), 0.35 if k < 2 else 0.45)
        M.add('fx', mono(sig, np.full(len(sig), p)), th, 0.8)
    pg = pan_at(centre(T_GLARE))
    M.add('perc', choke.play(110), T_GLARE, 0.5, pg)
    for m in ('D3', 'A3'):
        M.add('brass', bone.play(n(m), 100, dur=0.25, release=0.1), T_GLARE, 0.5, pg)
    yip = howl(T_YIP, 0.2, 700, 1100, 0.3)
    M.add('fx', mono(yip, np.full(len(yip), pan_at(dog_pos(T_YIP)))), T_YIP, 0.7)

    # ---- the final chorus: timpani, bells, cymbal, the key lifts, a hushed bar, amen ----
    r = troll.play(100, dur=BAR)
    M.add('perc', r * np.linspace(0.05, 1, r.shape[1])[None] ** 2, T_CHORUS - BAR, 0.5)
    M.add('perc', crash.play(115), T_CHORUS, 0.55, pan_at(c_from))
    M.add('perc', timp.play(115), T_CHORUS, 0.7, pan_at(c_from))
    M.add('sparkle', chimes.play(100), T_CHORUS, 0.5, pan_at(c_from))
    for k in range(int((T_HUSH - T_CHORUS) / BEAT)):
        t = T_CHORUS + k * BEAT
        M.add('perc', bells.play(100 if k % 2 == 0 else 80), t, 0.35, -0.5 if k % 2 else 0.5)
        if k % 4 == 0:
            M.add('perc', timp.play(90), t, 0.45)
    for m in ('D4', 'F#4', 'A4', 'D5'):                    # strings rise into the lift
        a = vln.play(n(m), 80, dur=BAR, release=0.1)
        M.add('strings', a * np.linspace(0.3, 1, a.shape[1])[None], T_LIFT - BAR, 0.3)
    M.add('perc', crash.play(110), T_LIFT, 0.5)
    M.add('perc', tri.play(90), T_LIFT, 0.4)
    # the hush: lanterns and windows only, the choir and an ooh quiet over E and B7
    quiet = [(0.0, n(m), 64, 2 * BEAT) for m in ('E3', 'G#3', 'B3')] + \
        [(2 * BEAT, n(m), 64, 2 * BEAT) for m in ('D#3', 'F#3', 'A3')]
    M.add('voices', hymn.render(quiet, BAR + 2), T_HUSH, 0.7)
    for k, m in enumerate(('E3', 'B2')):
        M.add('strings', vc.play(n(m), 60, dur=2 * BEAT * 0.97, release=0.4), T_HUSH + 2 * BEAT * k, 0.4)
        M.add('bass', cb.play(n(m) - 12, 70), T_HUSH + 2 * BEAT * k, 0.6)
    # amen: E major, everything, held to the end
    r = troll.play(90, dur=0.8)
    M.add('perc', r * np.linspace(0.1, 1, r.shape[1])[None] ** 2, T_AMEN - 0.8, 0.5)
    hold = D - T_AMEN - 0.6
    for m in ('E3', 'G#3', 'B3', 'E4'):
        M.add('brass', horn.play(n(m), 110, dur=hold, release=1.2), T_AMEN, 0.4)
        M.add('strings', vla.play(n(m), 100, dur=hold, release=1.2), T_AMEN, 0.35)
    M.add('tune', tpt.play(n('E5'), 106, dur=hold, release=1.2), T_AMEN, 0.6)
    M.add('tune', flute.play(n('E5'), 92, dur=hold, release=1.2), T_AMEN, 0.4)
    M.add('brass', tuba.play(n('E1') + 12, 110, dur=hold, release=1.2), T_AMEN, 0.6)
    M.add('bass', cb.play(n('E2'), 127), T_AMEN, 0.9)
    M.add('voices', hymn.render([(0.0, n(m), 100, hold) for m in ('E3', 'G#3', 'B3', 'E4')], hold + 2), T_AMEN, 0.7)
    M.add('perc', crash.play(120), T_AMEN, 0.55)
    M.add('perc', timp.play(120), T_AMEN, 0.75)
    M.add('perc', shake.play(110), T_AMEN, 0.5)
    for k, m in enumerate(('E4', 'G#4', 'B4', 'E5', 'G#5', 'B5', 'E6')):
        M.add('sparkle', glock.play(n(m), 84), T_AMEN + 0.12 * k, 0.5, -0.6 + 0.2 * k)
        M.add('sparkle', harp.play(n(m) - 12, 84), T_AMEN + 0.07 * k, 0.5, 0.6 - 0.2 * k)
