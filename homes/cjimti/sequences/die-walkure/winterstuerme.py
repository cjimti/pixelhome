"""Winterstürme: the wind presses at the door, and the great door of the hut (the free end of Right) swings open by
itself. A bright edge sweeps round as it opens, the storm's grey is simply gone, and moonlight pours in: a cool
white front of it runs from the door across the whole house, and behind it everything turns to a spring night,
moon-white over fresh green that ripples like grass in the wind, the ash tree's leaves coming out on the porch,
and blossoms drifting in on the breeze, pale pink sparks floating along the roof toward the hearth. A harp
glissando and shimmering violins carry it in. "Who went out?" "No one went: someone came in. Look, it is Spring."

Siegmund sings his love song, "Winterstürme wichen dem Wonnemond" (Donington 86), in full: four verses on the
horns and cellos over harp arpeggios and lilting pizzicato in B flat, the violins joining for the last. Every
phrase sends a wave of green and blossom in from the door, and his blue brightens on every note. Sieglinde
answers him, "Du bist der Lenz": the love of the twins (Donington 37) on oboe and cellos, her amber flaring;
then Bliss (Donington 38), three times, each higher, a warm glow growing between them. The two lights walk
together along Left and up Porch Left to the ash tree as the love music climbs to its height in the full
strings and horns, their colours blooming into one warm light that ripples over the house while the blossoms
fall thick. It settles into the moonlit spring night with the lovers beside the tree, its hidden hilt glowing.

compose() holds every note, choreography() every position; render() and score() read both."""
import numpy as np
from pixelhome.audio import note
from pixelhome.fx import DT, hexc, light, smoothstep, nframes, Flicker
from pixelhome.leitmotifs import play

CODE = 'WK09'
TITLE = 'Winterstürme'
KIND = 'show'
DESCRIPTION = ('The door of the hut swings open by itself and moonlight and spring pour in across the whole house. '
               'Siegmund sings his love song, Sieglinde answers, and the two of them find each other at last.')
VOICEOVER = ('A gust of wind, and the door swings open. Outside, winter is over. '
             'And inside, two people are falling in love.')

K = 8                                       # this scene's place in the shared clock (t + 80 * K)
T_DOOR = 1.5                                # the door swings open
T_FLOOD = 2.6                               # moonlight runs in from the door
FLOOD_S = 9.0
BEAT = 0.62
VERSES = [(10.0, 0), (17.6, 0), (25.2, 2), (32.8, 0)]   # the love song, start and transposition
T_LENZ = 41.0                               # "Du bist der Lenz"
LBEAT = 0.6
BLISS = [(50.5, 0), (52.8, 2), (55.1, 4)]
T_HEIGHT = 58.0                             # the love music at its height
HBEAT = 0.68
T_SETTLE = 72.0
D = 80.0

BLUE = hexc('#30a8ff')
AMBER = hexc('#ffa860')
EMBER = hexc('#ff6a10')
HOT = hexc('#ffb040')
HUT = hexc('#a05a28')
TRUNK = hexc('#5a3010')
LEAF = hexc('#50b030')
HILT = hexc('#ffcc40')
STORM = hexc('#5a6a8a')
MOON = hexc('#c8dcff')
GREEN = hexc('#80ff60')
BLOSSOM = hexc('#ffa8d8')
WARM = hexc('#ffc0a0')
TOGETHER = hexc('#a0a8ff')
WHITE = hexc('#ffffff')

BED, TRUNK_L, LEAF_L, STORM_L, SIEG_L, LINDE_L = 0.26, 0.55, 0.3, 0.32, 0.5, 0.55
EMBER_L = 0.18
GLINT_IN, GLINT_OUT = 0.42, 0.5
# the spring night, as WK10 picks it up
HUT_S, MOON_S, GREEN_S, LEAF_S, DOOR_S, BLOSSOM_S = 0.12, 0.2, 0.34, 0.5, 0.55, 1.0


def at(G, seg, u):
    s = G.pd[G.seg[seg]]
    return float(s.min() + u * (s.max() - s.min()))


def compose():
    """Every note: (time, seconds, midi, velocity, part, who)."""
    N = []

    def add(t, d, m, v, part, who=None):
        N.append((float(t), float(d), note(m) if isinstance(m, str) else int(m), int(v), part, who))

    add(0.0, T_DOOR + 0.5, 'F1', 70, 'wind')
    add(T_DOOR, 1.2, 'Bb2', 80, 'creak')
    gl = [x for x in range(note('Bb2'), note('F6') + 1) if x % 12 in (10, 2, 5)]  # B flat major, up the harp
    for i, m in enumerate(gl):
        add(T_DOOR + 0.3 + i * 1.6 / len(gl), 1.2, m, 84, 'harp')
    for m in ('F5', 'Bb5', 'D6'):
        add(T_DOOR + 0.3, VERSES[0][0] - T_DOOR, m, 60, 'shimmer')
    for m in ('Bb2', 'F3', 'D4'):
        add(T_FLOOD, VERSES[0][0] - T_FLOOD, m, 62, 'pad')

    chords = {0: [('Bb1', 'F3', 'Bb3', 'D4'), ('Bb1', 'F3', 'Bb3', 'D4'), ('Eb2', 'G3', 'Bb3', 'Eb4'), ('F2', 'F3', 'A3', 'C4')],
              2: [('C2', 'G3', 'C4', 'E4'), ('C2', 'G3', 'C4', 'E4'), ('F2', 'A3', 'C4', 'F4'), ('G2', 'G3', 'B3', 'D4')]}
    for k, (t0, tr) in enumerate(VERSES):                                       # Winterstürme, four verses
        for t, m, v, d in play('spring_song', t0, BEAT, tr, 96 + 4 * k):
            add(t, d, m, v, 'song', 'sieg')
            if k == 3:
                add(t, d, m + 12, v - 16, 'song_vn')
        for bar in range(4):                                                    # the lilt: bass, harp, pizz
            tb = t0 + bar * 3 * BEAT
            ch = chords[tr][bar]
            add(tb, 3 * BEAT, ch[0], 82, 'bass')
            for j, m in enumerate(ch[1:] + (ch[2],)):
                add(tb + j * BEAT * 0.75, 1.2, note(m) + 12, 70 + 4 * k, 'harp')
            for j in (1, 2):
                add(tb + j * BEAT, BEAT * 0.5, ch[1], 70, 'pizz')
                add(tb + j * BEAT, BEAT * 0.5, ch[3], 66, 'pizz')
            for m in ch[1:]:
                add(tb, 3 * BEAT * 1.05, m, 58 + 4 * k, 'pad')

    for t, m, v, d in play('twins_love', T_LENZ, LBEAT, 0, 96):                # "Du bist der Lenz"
        add(t, d, m, v, 'lenz' if m >= note('Eb4') else 'lenz_low', 'linde')
    for k, (t0, tr) in enumerate(BLISS):                                        # Bliss, three times, higher
        for t, m, v, d in play('bliss', t0, LBEAT, tr, 90 + 6 * k):
            add(t, d, m, v, 'bliss' if m >= note('F4') else 'bliss_low')
        for j in range(5):
            add(t0 + j * 0.12, 1.0, note('Db5') + tr + (0, 3, 7, 10, 12)[j], 70, 'harp')

    for t, m, v, d in play('twins_love', T_HEIGHT, HBEAT, 0, 110):             # at its height
        if m >= note('Eb4'):
            add(t, d, m, v, 'height', 'linde')
            add(t, d, m - 12, v - 8, 'height_horn', 'sieg')
        else:
            add(t, d, m, v - 6, 'height_low')
    for t, m, v, d in play('spring_song', T_HEIGHT + 4 * HBEAT, HBEAT * 0.9, -12, 86, line='melody'):
        add(t, d, m, v, 'counter', 'sieg')
    add(T_HEIGHT, 1.0, 'F2', 100, 'roll')
    for j in range(16):
        add(T_HEIGHT + 6.5 + j * 0.11, 1.4, note('F3') + (0, 4, 7, 10, 12, 16, 19, 22, 24, 28, 31, 34, 36, 40, 43, 46)[j],
            86, 'harp')
    for m in ('Bb2', 'F3', 'D4', 'F4'):
        add(T_SETTLE - 2.0, D - T_SETTLE + 2.0, m, 66, 'pad_end')
    add(T_SETTLE - 2.0, D - T_SETTLE + 2.0, 'Bb1', 70, 'bass_end')
    for t, m, v, d in play('spring_song', T_SETTLE + 0.5, 0.7, 12, 66, line='melody'):  # a flute, the song far off
        if t < D - 1.5:
            add(t, d, m, v, 'flute')
    return sorted(N, key=lambda e: e[0])


def follow(target, rate):
    """Critically damped chase of a target track (per frame), `rate` in 1/s per frame."""
    x = np.empty_like(target)
    x[0], v = target[0], 0.0
    for f in range(1, len(target)):
        w = rate[f]
        v += (w * w * (target[f] - x[f - 1]) - 2 * w * v) * DT
        x[f] = x[f - 1] + v * DT
    return x


def choreography(G):
    """Per frame: Siegmund and Sieglinde (path distance). They walk together to the tree."""
    F = nframes(D)
    t = np.arange(F) * DT
    s0, l0 = at(G, 'Left', 0.48), at(G, 'Left', 0.4)
    s1, l1 = at(G, 'Porch Front', 0.3), at(G, 'Porch Front', 0.2)
    u = smoothstep(T_LENZ + 3, T_SETTLE - 2, t)
    s_t = s0 + (s1 - s0) * u
    l_t = l0 + (l1 - l0) * u
    s_t = s_t + 14 * smoothstep(VERSES[0][0], VERSES[0][0] + 2, t) * (1 - u)   # he turns to the open door
    sieg = follow(s_t, np.full(F, 2.5))
    linde = follow(l_t, np.full(F, 2.5))
    return dict(t=t, sieg=sieg, linde=linde)


def room(G):
    """The hut's fixed parts: the same flicker for every scene of the act, so the cuts line up."""
    rng = np.random.default_rng(606)
    d = G.pd
    pf = at(G, 'Porch Front', 0.5)
    hc = at(G, 'Left', 0.6)
    return dict(
        pf=pf, hc=hc, door=G.length,
        trunk=np.exp(-((d - pf) / 20) ** 2),
        canopy=np.clip(np.exp(-((d - pf) / 300) ** 2) - 0.8 * np.exp(-((d - pf) / 26) ** 2), 0, 1),
        hearth=np.exp(-((d - hc) / 120) ** 2),
        coals=np.exp(-((d - hc) / 45) ** 2),
        cast=np.exp(-np.abs(d - hc) / 700),
        storm=np.exp(-((G.length - d) / 110) ** 2),
        fl=Flicker(rng, G.N, 0.6, 2.2), fast=Flicker(rng, G.N, 2.5, 6.0), leaf=Flicker(rng, G.N, 0.1, 0.5),
        gust=Flicker(rng, G.N, 0.2, 0.9))


def draw_room(G, R, tt, bed, ember, glint, storm, trunk=TRUNK_L, leaves=LEAF_L):
    d = G.pd
    roll = 0.5 + 0.5 * np.cos(2 * np.pi * (d / 420 - 0.03 * tt))
    fr = light(HUT, bed * (0.85 + 0.15 * roll))
    fr += light(EMBER, ember * R['hearth'] * (0.8 + 0.12 * R['fl'](tt) + 0.06 * R['fast'](tt)))
    dance = 0.5 + 0.5 * np.cos(2 * np.pi * (d / 230 - 0.11 * tt) + 1.5 * np.sin(2 * np.pi * 0.07 * tt))
    fr += light(EMBER, 0.55 * ember * R['cast'] * (0.3 + 0.7 * dance) * (0.85 + 0.15 * R['fl'](tt)))
    fr += light(HOT, 0.8 * ember * R['coals'] * (0.7 + 0.2 * R['fast'](tt)))
    fr += light(TRUNK, trunk * R['trunk'])
    fr += light(LEAF, leaves * R['canopy'] * (0.85 + 0.15 * R['leaf'](tt)))
    fr += light(HILT, glint * np.exp(-((d - R['pf']) / 9) ** 2))
    fr += light(STORM, storm * R['storm'] * (0.85 + 0.15 * R['gust'](tt)))
    return fr


def blossoms(G):
    """Petals on the breeze, on the shared clock so they carry across the cut into WK10: (birth, start, speed,
    life, width) for each, drifting from the door end toward the hearth."""
    rng = np.random.default_rng(909)
    n = 2400
    birth = np.sort(rng.uniform(80 * 8, 80 * 10 + 5, n))
    start = G.length - rng.exponential(700, n)
    speed = rng.uniform(40, 140, n)
    life = rng.uniform(3.0, 7.0, n)
    width = rng.uniform(7, 14, n)
    return birth, start, speed, life, width


def draw_blossoms(G, B, tt):
    birth, start, speed, life, width = B
    lo = int(np.searchsorted(birth, tt - 7.0))
    hi = int(np.searchsorted(birth, tt))
    if hi <= lo:
        return np.zeros(G.N)
    age = tt - birth[lo:hi]
    ok = age < life[lo:hi]
    a, l_ = age[ok], life[lo:hi][ok]
    q = start[lo:hi][ok] - speed[lo:hi][ok] * a + 20 * np.sin(2 * np.pi * a / 2.3)
    env = np.sin(np.pi * a / l_) ** 2
    g = np.exp(-((G.pd[:, None] - q[None, :]) / width[lo:hi][ok][None, :]) ** 2) * env[None, :]
    return g.max(axis=1)


def render(G, seed=9):
    rng = np.random.default_rng(seed)
    F = nframes(D)
    out = np.zeros((F, G.N, 3))
    d = G.pd
    R = room(G)
    pf, L = R['pf'], G.length
    C = choreography(G)
    N = compose()
    B = blossoms(G)
    song = np.array([e[0] for e in N if e[5] == 'sieg'])
    linde_n = np.array([e[0] for e in N if e[5] == 'linde' or e[4] in ('bliss',)])
    verses = [t0 for t0, _ in VERSES] + [T_LENZ, T_HEIGHT]
    bliss = [t0 for t0, _ in BLISS]
    tw = Flicker(rng, G.N, 2.0, 6.0)
    grass = Flicker(rng, G.N, 0.1, 0.4)

    for f in range(F):
        t = f * DT
        tt = t + 80 * K
        # the moonlight's front, running in from the door; everything behind it is spring
        front = L - (L + 300) * smoothstep(T_FLOOD, T_FLOOD + FLOOD_S, t) ** 0.8
        spring = smoothstep(front - 150, front + 150, d)
        sp_all = smoothstep(T_FLOOD, T_FLOOD + FLOOD_S, t)
        opened = smoothstep(T_DOOR, T_DOOR + 1.2, t)
        hut = BED + (HUT_S - BED) * spring
        glint = GLINT_IN + (GLINT_OUT - GLINT_IN) * smoothstep(T_LENZ, T_SETTLE, t)
        fr = draw_room(G, R, tt, hut, EMBER_L, glint, STORM_L * 1.5 * (1 - opened),
                       leaves=LEAF_L + (LEAF_S - LEAF_L) * spring)

        # the spring night: moon over rippling green, and the open door at the end of Right
        wind = 0.5 + 0.5 * np.cos(2 * np.pi * (d / 260 + 0.09 * tt))
        wind2 = 0.5 + 0.5 * np.cos(2 * np.pi * (d / 110 + 0.21 * tt) + 2)
        fr += light(MOON, MOON_S * spring * (0.85 + 0.15 * wind2))
        fr += light(GREEN, GREEN_S * spring * (0.55 + 0.45 * wind * (0.7 + 0.3 * wind2)) * (0.9 + 0.1 * grass(tt)))
        fr += light(MOON, DOOR_S * opened * np.exp(-((L - d) / 200) ** 2))
        if T_DOOR <= t < T_DOOR + 1.6:                                          # the door swinging round
            u = smoothstep(T_DOOR, T_DOOR + 1.2, t)
            e = L - 260 * u
            fr += light(WHITE, 0.9 * (1 - smoothstep(T_DOOR + 1.0, T_DOOR + 1.6, t)) * np.exp(-((d - e) / 18) ** 2))
            fr += light(MOON, 0.6 * smoothstep(e - 10, e + 10, d))
        if T_FLOOD <= t < T_FLOOD + FLOOD_S + 1.5:                               # the edge of the flood
            fr += light(MOON, 0.55 * (1 - smoothstep(T_FLOOD + FLOOD_S - 1, T_FLOOD + FLOOD_S + 1.5, t)) *
                        np.exp(-((d - front) / 60) ** 2))

        # every phrase a wave of green and blossom in from the door
        for t0 in verses:
            if t0 <= t < t0 + 6:
                a = t0 + 0.0
                q = L - 520 * (t - a)
                fr += light(GREEN, 0.65 * (1 - (t - a) / 6) * np.exp(-((d - q) / 190) ** 2))
                fr += light(MOON, 0.3 * (1 - (t - a) / 6) * np.exp(-((d - q - 150) / 60) ** 2))

        # blossoms on the breeze
        density = BLOSSOM_S * smoothstep(T_FLOOD + 1, T_FLOOD + 6, t) * (1 + 0.8 * smoothstep(T_HEIGHT, T_HEIGHT + 4, t)
                                                                       * (1 - smoothstep(T_SETTLE - 2, T_SETTLE + 3, t)))
        if density > 0:
            fr += light(BLOSSOM, 0.45 * density * spring * draw_blossoms(G, B, tt) * (0.8 + 0.2 * tw(tt)))

        # the lovers
        sp, lp = C['sieg'][f], C['linde'][f]
        mid = (sp + lp) / 2
        i = int(np.searchsorted(song, t, side='right')) - 1
        sf = np.exp(-(t - song[i]) / 0.3) if i >= 0 and t - song[i] < 1.2 else 0.0
        j = int(np.searchsorted(linde_n, t, side='right')) - 1
        lf = np.exp(-(t - linde_n[j]) / 0.3) if j >= 0 and t - linde_n[j] < 1.2 else 0.0
        singing = smoothstep(VERSES[0][0] - 1, VERSES[0][0] + 1, t)
        height = smoothstep(T_HEIGHT - 1, T_HEIGHT + 2, t) * (1 - smoothstep(T_SETTLE - 2, D - 2, t))
        for p, col, base, fl in ((sp, BLUE, SIEG_L, sf), (lp, AMBER, LINDE_L, lf)):
            b = base * (1.25 + 0.15 * singing + 0.3 * fl + 0.25 * height) * (0.96 + 0.04 * np.sin(2 * np.pi * tt / 4.0))
            fr += light(col, b * np.exp(-((d - p) / 26) ** 2) + 0.3 * b * np.exp(-((d - p) / 110) ** 2))
        a, b_ = sorted((sp, lp))
        between = smoothstep(a - 5, a + 15, d) * smoothstep(b_ + 5, b_ - 15, d)
        warmth = smoothstep(BLISS[0][0] - 1, BLISS[-1][0] + 2, t)
        fr += light(TOGETHER, 0.3 * (1 - warmth) * between)
        k = int(np.searchsorted(bliss, t, side='right')) - 1
        bl = np.exp(-(t - bliss[k]) / 0.8) if k >= 0 and t - bliss[k] < 3 else 0.0
        fr += light(WARM, (0.45 * warmth + 0.25 * bl) * between + (0.3 * warmth + 0.4 * bl + 0.25 * height) *
                    np.exp(-((d - mid) / (60 + 40 * bl + 80 * height)) ** 2))
        if height > 0:                                                          # one light, rippling over the house
            r = (t - T_HEIGHT) * 260 % 900
            ring = np.exp(-((np.abs(d - mid) - r) / 90) ** 2) * (1 - r / 900)
            fr += light(WARM, 0.6 * height * ring)
            fr += light(WHITE, 0.25 * height * np.exp(-((d - mid) / 14) ** 2))
        out[f] = fr
    return np.clip(out, 0, 1)


def score(M, G):
    from pixelhome.audio import SR, whoosh
    order = np.argsort(G.pd)
    xs, ds = G.pos[order, 0], G.pd[order]
    x0, x1 = xs.min(), xs.max()

    def pan_at(dd):
        x = np.interp(dd, ds, xs)
        return float(0.85 * (2 * (x - x0) / (x1 - x0) - 1))

    C = choreography(G)
    pdoor = pan_at(G.length)

    def pt(key, t):
        return pan_at(np.interp(t, C['t'], C[key]))

    for name, gain, rev in (('strings', 0.19, 0.34), ('low', 0.19, 0.22), ('brass', 0.2, 0.32), ('winds', 0.22, 0.32),
                            ('perc', 0.2, 0.3), ('harp', 0.15, 0.45), ('fx', 0.12, 0.3)):
        M.bus(name, gain=gain, reverb=rev)
    vc = M.sampler('Strings/Cello Section/susvib/*.wav', tune=-12)
    va = M.sampler('Strings/Viola Section/susvib/*.wav', tune=-12)
    vn = M.sampler('Strings/Violin Section/susVib/*.wav', tune=-12)
    vtrem = M.sampler('Strings/Violin Section/Trem/*.wav', tune=-12)
    vpizz = M.sampler('Strings/Violin Section/Pizz/*.wav', tune=-12)
    cb = M.sampler('Strings/Solo Contrabass/SusNV/*.wav', tune=-12)
    cbp = M.sampler('Strings/Solo Contrabass/Pizz/*.wav', tune=-12)
    horn = M.sampler('Brass/F Horn/sus/*.wav', tune=-12)
    ob = M.sampler('Woodwinds/Oboe/Vib/*.wav', tune=-12)
    cl = M.sampler('Woodwinds/Clarinet/susLong/*.wav', tune=-12)
    fl = M.sampler('Woodwinds/Flute/susvib/*.wav', tune=-12)
    harp = M.sampler('Strings/Harp/*.wav')
    roll = M.hits('Percussion/Timpani/Rolls/*_v3_*.wav')
    cym = M.hits('Percussion/susCymb1-cresc-Short_v1.wav')

    def hold(bus, s, m, t0, t1, vel, pan=0.0, step=2.5, rise=0.8, fall=1.0, gain=1.0):
        a0 = s.play(m, vel)
        step = min(step, (a0.shape[1] / SR - 0.35) / 2)
        w = int(2 * step * SR)
        win = np.hanning(w)
        t = t0 - step
        while t < t1 + fall:
            a = s.play(m, vel)[:, int(0.25 * SR):int(0.25 * SR) + w]
            a = a * win[:a.shape[1]]
            tt = t + np.arange(a.shape[1]) / SR
            e = np.clip((tt - t0) / rise, 0, 1) * np.clip(1 - (tt - t1) / fall, 0, 1)
            M.add(bus, a * e, t, gain, pan)
            t += step

    for t, d, m, v, part, who in compose():
        if part == 'wind':
            M.add('fx', whoosh(d + 0.5, 250, 1200, 0.6, seed=8), t, 1.0, pdoor)
            hold('low', vtrem, m + 36, t, t + d, v, pdoor, rise=1.0, fall=0.5, gain=0.3)
        elif part == 'creak':
            M.add('low', cb.play(m, v, dur=d, release=0.3), t, 0.6, pdoor)
            M.add('fx', whoosh(1.4, 3000, 500, 0.5, seed=4), t, 0.8, pdoor)
            M.add('perc', cym.play(80), t - 0.8, 0.5, pdoor)
        elif part == 'harp':
            u = (m - 46) / 44
            M.add('harp', harp.play(m, v), t, 1.0, pdoor + (pan_at(0) - pdoor) * np.clip(u, 0, 1) * 0.6)
        elif part == 'shimmer':
            hold('strings', vtrem, m, t, t + d, v, 0.3, rise=2.0, fall=2.0, gain=0.4)
        elif part == 'pad':
            hold('strings', va if m >= note('C3') else vc, m, t, t + d, v, -0.2 + 0.2 * (m % 3), rise=0.6, fall=0.8,
                 gain=0.45)
        elif part == 'song':
            pa = pt('sieg', t)
            M.add('brass', horn.play(m, v, dur=d * 1.05, release=0.4), t, 1.0, pa)
            M.add('strings', vc.play(m, v - 10, dur=d * 1.05, release=0.4), t, 0.7, pa + 0.1)
        elif part == 'song_vn':
            M.add('strings', vn.play(m, v, dur=d * 1.05, release=0.4), t, 0.6, 0.0)
        elif part == 'bass':
            M.add('low', cbp.play(m + 12, v), t, 0.9, -0.1)
            M.add('low', cb.play(m + 12, v - 14, dur=d, release=0.4), t, 0.5, 0.1)
        elif part == 'pizz':
            M.add('strings', vpizz.play(m, v), t, 0.6, 0.2 if m % 2 else -0.2)
        elif part in ('lenz', 'height'):
            pa = pt('linde', t)
            M.add('winds', ob.play(m, v, dur=d * 1.05, release=0.4), t, 0.9, pa)
            M.add('strings', vn.play(m, v - 6, dur=d * 1.05, release=0.4), t, 0.5 if part == 'lenz' else 0.9, pa)
        elif part in ('lenz_low', 'height_low'):
            s = vc if m < note('C3') or m >= note('F3') else va
            M.add('strings', s.play(m, v - 6, dur=d * 1.02, release=0.4), t, 0.6, -0.2 + 0.4 * (m % 2))
            if m < note('C2'):
                M.add('low', cb.play(m + 12, v - 10, dur=d, release=0.4), t, 0.6, 0.0)
        elif part == 'height_horn':
            M.add('brass', horn.play(m, v, dur=d * 1.05, release=0.4), t, 1.1, pt('sieg', t))
        elif part == 'bliss':
            pa = (pt('sieg', t) + pt('linde', t)) / 2
            M.add('winds', cl.play(m, v, dur=d * 1.05, release=0.4), t, 0.8, pa)
            M.add('strings', vn.play(m, v - 8, dur=d * 1.05, release=0.4), t, 0.6, pa)
        elif part == 'bliss_low':
            hold('strings', va if m >= note('C3') else vc, m, t, t + d, v - 10, -0.3 + 0.2 * (m % 4), rise=0.3,
                 fall=0.8, gain=0.5)
        elif part == 'counter':
            M.add('brass', horn.play(m, v, dur=d * 1.05, release=0.4), t, 0.6, pt('sieg', t))
        elif part == 'roll':
            M.add('perc', roll.play(v, dur=3.0), t, 0.6, 0.0)
        elif part == 'pad_end':
            hold('strings', vn if m >= note('D4') else va, m, t, t + d, v, -0.3 + 0.2 * (m % 4), rise=1.5, fall=1.5,
                 gain=0.45)
        elif part == 'bass_end':
            hold('low', cb, m + 12, t, t + d, v, 0.0, rise=1.5, fall=1.5, gain=0.6)
        elif part == 'flute':
            M.add('winds', fl.play(m, v, dur=d * 1.05, release=0.4), t, 0.6, pdoor)
