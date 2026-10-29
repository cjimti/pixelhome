"""Fog on Christmas Eve: grey fog rolls over the whole house, thick and moving, with a few lanterns
glowing faintly in it. A small red-orange nose lights up at the free right end and the fog thins
around it. It leads the team in along the right wing (pale bone-white reindeer behind it, then the sleigh
and its driver), slowly at first; then the sleigh jingles, a ring of gold bursts off it and it takes
off, streaking round the porch and the left wing and away along Side, leaving a lane of clear air and
gold sparkle. It comes round again in from the right end, faster and brighter, blowing the fog back as
it goes, and pulls up over the porch on the anthem's last chord: a starburst runs out to both ends and
the whole house is left glittering gold under a clear night, the nose shining in the middle.

From lift-off the anthem's beat grid (BPM) times everything: the second pass and the last chord land on
its beats, and score() takes every hit from these constants."""
import numpy as np
from pixelhome.fx import DT, hexc, light, keys, nframes, Flicker

CODE = 'NB09'
TITLE = 'Fog on Christmas Eve'
KIND = 'show'
DESCRIPTION = ('Thick fog over the house until a little glowing nose lights the way. The sleigh takes off, '
               'streaks round the roof, comes round again to blow the fog away, and leaves the house glittering.')

FOG = hexc('#7f8ca0')
LANTERN = hexc('#ff6a10')
NOSE = hexc('#ff2a08')
BONE = hexc('#e8e0c8')
DRIVER = hexc('#f2f4ff')
GOLD = hexc('#ffc040')
WHITE = hexc('#fff4dc')
NIGHT = hexc('#0a1440')

BPM = 84
BEAT = 60 / BPM
NOSE_ON = 10.0                              # the nose lights at the free right end
LIFT = 24.0                                 # the team takes off: the anthem's first beat
GONE = 41.0                                 # gone along Side
BELLS = (23.5, 25.5)
PASS = 26                                   # beats after LIFT: back in from the right end
HIT = 32                                    # beats after LIFT: it stops over the porch, the last chord
D = LIFT + HIT * BEAT + 7.0
TEAM = [(0, 'nose')] + [(45 + 32 * k, 'deer') for k in range(4)] + [(210, 'sleigh')]
SEED = 71


def tb(k):
    """Seconds at beat k of the anthem."""
    return LIFT + k * BEAT


def lead_at(t, G):
    """Where the nose is along the path at t: a slow walk in the fog, the flight, the second pass."""
    L = G.length
    if t < tb(PASS):
        return keys(t, [(NOSE_ON, L - 40), (16, L - 170), (LIFT, L - 300), (40, -320)])
    mid = G.pd[G.seg['Porch Front']].mean()
    u = min(1.0, (t - tb(PASS)) / (tb(HIT) - tb(PASS)))
    return L + 40 - (L + 40 - mid) * (1 - (1 - u) ** 2.2)


def blob(x, c, w):
    return np.exp(-((x - c) / w) ** 2)


def render(G, seed=SEED):
    rng = np.random.default_rng(seed)
    F = nframes(D)
    out = np.zeros((F, G.N, 3))
    d = G.pd[G.path]
    L = G.length
    mid = G.pd[G.seg['Porch Front']].mean()
    lan_at = rng.uniform(150, L - 150, 6)
    flick = Flicker(rng, G.N, 2, 7)
    clear = np.zeros(G.N)
    P = 800
    pt = np.full(P, -99.0)
    px = np.zeros(P)
    pl = rng.uniform(1.0, 2.2, P)
    nxt = 0
    glit = rng.uniform(0, 2 * np.pi, G.N)
    gfr = rng.uniform(0.6, 1.8, G.N)
    hit = tb(HIT)

    for f in range(F):
        t = f * DT
        fr = np.zeros((G.N, 3))
        lead = lead_at(t, G)
        on = keys(t, [(NOSE_ON, 0), (NOSE_ON + 1.5, 1)])
        flying = LIFT <= t < GONE or t >= tb(PASS)
        visible = on > 0 and (t < GONE or t >= tb(PASS))

        clear *= np.exp(-DT / 4)
        if visible:
            clear = np.maximum(clear, on * blob(d, lead, 110 if flying else 80))
        # the fog stays on the wings until the last chord's starburst rolls it back to a faint haze
        reach = np.clip((900 * (t - hit) - np.abs(d - mid)) / 200, 0, 1) if t >= hit else 0
        fog = keys(t, [(0, 0), (3, 1)]) * (1 - 0.8 * reach)
        roll = (0.5 + 0.2 * np.sin(d / 110 - 0.35 * t) + 0.15 * np.sin(d / 47 + 0.6 * t + 1) +
                0.15 * np.sin(d / 230 + 0.15 * t + 2))
        fr += light(FOG, fog * 0.3 * roll * (1 - 0.6 * clear))
        lans = sum(blob(d, a, 9) for a in lan_at)
        fr += light(LANTERN, keys(t, [(0, 0), (3, 1), (hit, 1), (D - 2, 0)]) * 0.22 * lans *
                    (1 + 0.2 * flick(t)) * (1 - 0.6 * clear * fog))

        sleigh = None
        if visible:
            bright = 1.25 if t >= tb(PASS) else 1.0
            for off, kind in TEAM:
                q = lead + off
                if q < -20 or q > L + 20:
                    continue
                if kind == 'nose':
                    pulse = 1 + 0.15 * np.sin(2 * np.pi * 1.2 * t)
                    fr += light(NOSE, on * 0.9 * pulse * blob(d, q, 9))
                    fr += light(NOSE, on * 0.2 * bright * blob(d, q, 60))
                elif kind == 'deer':
                    fr += light(BONE, on * 0.45 * bright * blob(d, q, 6))
                else:
                    fr += light(DRIVER, on * 0.55 * bright * blob(d, q, 10))
                    sleigh = q
        if BELLS[0] <= t < BELLS[1]:                 # bells as it lifts off
            u = t - BELLS[0]
            sh = np.clip(np.sin(d * 1.7 + 40 * t), 0, 1) ** 6
            fr += light(GOLD, 0.6 * (1 - u / 2) * sh * blob(d, lead_at(LIFT, G) + 100, 160))
        if LIFT <= t < LIFT + 1.5:                   # the lift-off ring
            u = t - LIFT
            fr += light(GOLD, 0.75 * np.exp(-u / 0.45) * blob(np.abs(d - (lead_at(LIFT, G) + 100)), 500 * u, 40))
        if flying and sleigh is not None and 0 < sleigh < L and t < hit:
            for _ in range(6 if t >= tb(PASS) else 4):
                k = nxt % P
                nxt += 1
                pt[k], px[k] = t, sleigh + rng.normal(10, 12)
        lv = (t - pt) < pl
        if lv.any():
            u = (t - pt[lv]) / pl[lv]
            tw = 0.6 + 0.4 * np.sin(30 * u + px[lv])
            g = np.zeros(G.N)
            idx = np.clip(np.searchsorted(d, px[lv]), 0, G.N - 1)
            np.maximum.at(g, idx, 0.6 * (1 - u) * tw)
            fr += light(GOLD, g)

        # the last chord: a starburst from the porch and the house left glittering under a clear sky
        if t >= hit:
            u = t - hit
            fr += light(WHITE, 0.9 * np.exp(-u / 0.5) * blob(np.abs(d - mid), 900 * u, 60))
            fr += light(GOLD, 0.7 * np.exp(-u / 0.8) * blob(d, mid, 120))
            fr += light(NIGHT, keys(t, [(hit, 0), (hit + 1, 0.1)]) * np.ones(G.N))
            sp = np.clip(np.sin(2 * np.pi * gfr * t + glit), 0, 1) ** 4
            fr += light(GOLD, reach * (0.22 + 0.3 * sp))
        out[f][G.path] = fr * keys(t, [(D - 2.5, 1), (D - 0.2, 0)])
    return out


# ---- music: an original anthem in F, 84 BPM. Hushed under the fog (wind, a low drone, far lantern bells, a
# harp turning over); the nose plays the anthem's hook on a music box as it comes forward, with soft hooves.
# A timpani roll lifts it off: the full ANTHEM on horns and strings with pizz bass, timpani on the bar lines,
# sleigh bells running eighths, a whoosh following the team and a glockenspiel sparkling in its trail. The
# second half goes up a notch (violins an octave up, choir, trumpets), a harp glissando brings the team in
# again from the right end, and the last chord lands as it stops over the porch. ----

TUNE = [(0, 'C4', 1), (1, 'F4', 1), (2, 'G4', 1), (3, 'A4', 1), (4, 'C5', 2), (6, 'Bb4', 1), (7, 'A4', 1),
        (8, 'G4', 1.5), (9.5, 'A4', .5), (10, 'F4', 1), (11, 'D4', 1), (12, 'C4', 3)]
ANTHEM = TUNE + [(16, 'C4', 1), (17, 'F4', 1), (18, 'G4', 1), (19, 'A4', 1), (20, 'D5', 2), (22, 'C5', 1),
                 (23, 'Bb4', 1), (24, 'A4', 1), (25, 'G4', .5), (25.5, 'A4', .5), (26, 'Bb4', 1), (27, 'G4', 1),
                 (28, 'F4', 4)]
CHORDS = ['F', 'Bb', 'Gm', 'C', 'F', 'Bb', 'C7', 'F']        # one a bar of four beats
VOICE = {'F': ('F3', 'A3', 'C4'), 'Bb': ('F3', 'Bb3', 'D4'), 'Gm': ('G3', 'Bb3', 'D4'), 'C': ('E3', 'G3', 'C4'),
         'C7': ('E3', 'Bb3', 'C4')}
ROOT = {'F': ('F2', 'C2'), 'Bb': ('Bb1', 'F2'), 'Gm': ('G1', 'D2'), 'C': ('C2', 'G1'), 'C7': ('C2', 'G1')}


def score(M, G):
    from pixelhome.audio import SR, note as n, whoosh
    box = M.synth('Plucks/Magic Music Box')
    bell = M.synth('Plucks/Bell 1')
    choir = M.synth('Pads/Synth Choir MW O-Ah')
    trem = M.sampler('Strings/Cello Section/trem/*.wav', tune=-12)
    vtrem = M.sampler('Strings/Violin Section/Trem/*.wav', tune=-12)
    vln = M.sampler('Strings/Violin Section/susVib/*.wav', tune=-12)
    cello = M.sampler('Strings/Cello Section/susvib/*.wav', tune=-12)
    horn = M.sampler('Brass/F Horn/sus/*.wav', tune=-12)
    tpt = M.sampler('Brass/Trumpet/sus/*.wav', tune=-12)
    clar = M.sampler('Woodwinds/Clarinet/susLong/*.wav', tune=-12)
    pizz = M.sampler('Strings/Solo Contrabass/Pizz/*.wav', tune=-12)
    harp = M.sampler('Strings/Harp/*.wav')
    glock = M.sampler('Percussion/Glock/*.wav', tune=-12)
    sleigh = M.hits('Percussion/Sleighbells_Hit*.wav')
    clop = M.hits('VSCO 1 Percussion/varWood/wood_click*.wav')
    timp = M.hits('Percussion/Timpani/Timpani1_Hit*.wav')
    troll = M.hits('Percussion/Timpani/Rolls/*.wav')
    crash = M.hits('VSCO 1 Percussion/varMetal/Cymbals/clash/crash_hit_ff*.wav')
    ccresc = M.hits('Percussion/susCymb1-cresc-Short*.wav')
    tree = M.hits('Percussion/BellTree_Stroke*.wav')
    for name, gain, rev in (('wind', 0.2, 0.1), ('drone', 0.24, 0.3), ('bells', 0.12, 0.6), ('box', 0.26, 0.4),
                            ('hooves', 0.16, 0.2), ('tune', 0.3, 0.3), ('strings', 0.24, 0.3), ('bass', 0.32, 0.1),
                            ('drums', 0.26, 0.2), ('fx', 0.24, 0.2), ('sparkle', 0.12, 0.4), ('choir', 0.15, 0.4)):
        M.bus(name, gain=0.66 * gain, reverb=rev)

    L = G.length
    order = np.argsort(G.pd)
    xs, ds = G.pos[order, 0], G.pd[order]
    x0, x1 = xs.min(), xs.max()

    def pan_at(d):                          # path distance -> left/right across the facade, from the street
        return 0.85 * (2 * (np.interp(np.clip(d, 0, L), ds, xs) - x0) / (x1 - x0) - 1)

    def mono(sig, pans):
        a = (np.clip(pans, -1, 1) + 1) * np.pi / 4
        return np.vstack([sig * np.cos(a), sig * np.sin(a)]) * np.sqrt(2)

    def chord(k):                           # by anthem beat
        return CHORDS[int(k // 4) % len(CHORDS)]

    # ---- the fog: low wind (filtered noise breathing with the fog) and a drone on F ----
    N = int(D * SR)
    tt = np.arange(N) / SR
    wind = M.rng.normal(0, 1, (2, N))
    spec = np.fft.rfft(wind, axis=1)
    fr = np.fft.rfftfreq(N, 1 / SR)
    spec *= 1 / np.sqrt(1 + (fr / 380) ** 4) * np.clip(fr / 50, 0, 1)
    wind = np.fft.irfft(spec, N, axis=1)
    wind /= np.abs(wind).max()
    fog = np.interp(tt, [0, 3, tb(HIT), tb(HIT) + 1.5, D], [0, 1, 1, 0.3, 0.2])
    wind *= fog * (0.7 + 0.3 * np.sin(2 * np.pi * tt / 9.0) * np.sin(2 * np.pi * tt / 4.1 + 1))
    M.add('wind', wind, 0.0)
    for m, p in (('F2', -0.3), ('C3', 0.3)):
        s = trem.play(n(m), 55, dur=LIFT + 1.0, release=1.5)
        M.add('drone', s * np.clip(np.arange(s.shape[1]) / SR / 3, 0, 1), 0.0, 1.0, p)
    for k, t in enumerate(np.arange(2.0, LIFT - 2, 2.0)):                 # a harp turning over in the fog
        for j, m in enumerate(VOICE[['F', 'Bb', 'Gm', 'C'][k % 4]]):
            M.add('drone', harp.play(n(m) + 12, 40 + k * 2), t + 0.18 * j, 0.6, -0.2 + 0.2 * j)

    # ---- far-off lanterns: the same six render() hangs, a muffled bell now and then where each is ----
    lan_at = np.random.default_rng(SEED).uniform(150, L - 150, 6)
    for a in lan_at:
        t = float(M.rng.uniform(1, 6))
        while t < LIFT:
            m = n(['F5', 'C5', 'A4', 'G4'][int(M.rng.integers(4))])
            M.add('bells', bell.render([(0.0, m, int(M.rng.integers(25, 45)), 0.6)], 5.0), t, 1.0,
                  float(pan_at(a)))
            t += float(M.rng.uniform(5, 11))

    # ---- the nose comes forward: the hook on a music box, growing, following it ----
    on = NOSE_ON + 1.0
    beat = (LIFT - 1.0 - on) / 15
    for b, m, ln in TUNE:
        t = on + b * beat
        v = int(40 + 45 * b / 15)
        M.add('box', box.render([(0.0, n(m) + 12, v, ln * beat * 0.9)], ln * beat + 3), t, 1.0,
              float(pan_at(lead_at(t, G))))
    s = vtrem.play(n('C4'), 70, dur=LIFT - 16.0)
    M.add('strings', s * np.linspace(0.05, 1, s.shape[1]) ** 2, 16.0, 0.7)
    for i, t in enumerate(np.arange(NOSE_ON + 1.5, LIFT, 0.26)):
        q = lead_at(t, G) + TEAM[1 + i % 4][0]
        if 0 < q < L:
            M.add('hooves', clop.play(int(M.rng.integers(45, 70)), pitch=float(M.rng.uniform(-3, 3))), t, 0.8,
                  float(pan_at(q)))

    # ---- lift-off: the roll, the hit, the anthem ----
    r = troll.play(100, dur=2.0)
    M.add('drums', r * np.linspace(0.05, 1, r.shape[1]) ** 2, LIFT - 2.0, 0.7)
    r = ccresc.play(100, dur=2.0)
    M.add('drums', r * np.linspace(0.05, 1, r.shape[1]) ** 2, LIFT - 2.0, 0.4)
    M.add('drums', crash.play(110), LIFT, 0.7, float(pan_at(lead_at(LIFT, G) + 100)))
    M.add('fx', tree.play(110), LIFT, 0.7, float(pan_at(lead_at(LIFT, G) + 100)))
    for b, m, ln in ANTHEM:
        t, dur = tb(b), ln * BEAT * 0.95
        M.add('tune', horn.play(n(m), 108 if b < 16 else 116, dur=dur), t, 0.9, -0.2)
        M.add('tune', vln.play(n(m) + (12 if b >= 16 else 0), 96, dur=dur), t, 0.5 if b < 16 else 0.45, 0.25)
        if b >= 16:
            M.add('tune', tpt.play(n(m), 96, dur=dur), t, 0.35, 0.05)
        if b < 16:
            M.add('tune', clar.play(n(m) - 12, 80, dur=dur), t, 0.3, 0.3)
    for k in range(0, HIT, 1):
        c = chord(k)
        if k % 4 == 0:
            for m in VOICE[c]:
                M.add('strings', cello.play(n(m), 82, dur=4 * BEAT * 0.98, release=0.4), tb(k), 0.55)
            M.add('drums', timp.play(108 if k % 16 == 0 else 92), tb(k), 0.55)
        M.add('bass', pizz.play(n(ROOT[c][k % 2]), 108 if k % 2 == 0 else 92), tb(k), 1.0)
    hums = [(tb(k), n(m) + 12, 80, 4 * BEAT * 0.95) for k in range(16, HIT, 4) for m in VOICE[chord(k)]]
    M.add('choir', choir.render(hums, D), 0.0)
    for t in np.arange(BELLS[0], tb(HIT), BEAT / 2):
        if t < GONE or t >= tb(PASS) - 1:
            q = lead_at(t, G) + 100
            M.add('fx', sleigh.play(90 if t < BELLS[1] else 70), t, 0.45, float(pan_at(q)))
    tw = np.arange(int((GONE - LIFT) * SR)) / SR + LIFT
    sw = whoosh(GONE - LIFT, 250, 2200, 0.5, seed=9)[0]
    M.add('fx', mono(sw, pan_at(np.array([lead_at(t, G) + 100 for t in tw]))), LIFT, 0.8)
    T2 = tb(HIT) - tb(PASS)
    tw = np.arange(int(T2 * SR)) / SR + tb(PASS)
    sw = whoosh(T2, 400, 3200, 0.6, seed=11)[0]
    M.add('fx', mono(sw, pan_at(np.array([lead_at(t, G) + 100 for t in tw]))), tb(PASS), 0.9)
    for j, m in enumerate(('F3', 'A3', 'C4', 'F4', 'A4', 'C5', 'F5', 'A5', 'C6')):   # the glissando in
        M.add('sparkle', harp.play(n(m), 90), tb(PASS) - 0.6 + 0.06 * j, 2.4, float(pan_at(L - 60 * j)))
    sparkle = [n(m) for m in ('F5', 'G5', 'A5', 'C6', 'D6', 'F6')]
    for t in np.arange(LIFT, tb(HIT), 0.14):
        if GONE <= t < tb(PASS):
            continue
        q = lead_at(t, G) + 210
        if 0 < q < L and M.rng.random() < 0.7:
            M.add('sparkle', glock.play(sparkle[int(M.rng.integers(len(sparkle)))], int(M.rng.integers(50, 85))),
                  t, 1.0, float(pan_at(q)))

    # ---- the last chord as it stops over the porch ----
    th = tb(HIT)
    ring = D - th - 0.5
    for m in ('F3', 'A3', 'C4', 'F4'):
        M.add('tune', horn.play(n(m), 120, dur=ring), th, 0.75)
        M.add('tune', tpt.play(n(m) + 12 if m == 'F3' else n(m), 110, dur=ring), th, 0.3)
    for m in ('F3', 'C4', 'A4', 'F5'):
        M.add('strings', vln.play(n(m), 100, dur=ring), th, 0.45)
    M.add('bass', pizz.play(n('F1'), 127), th, 1.3)
    M.add('choir', choir.render([(th, n(m) + 12, 110, ring) for m in VOICE['F']], D), 0.0, 1.3)
    M.add('drums', crash.play(124), th, 1.0)
    M.add('drums', timp.play(127), th, 1.0)
    r = troll.play(90, dur=3.0)
    M.add('drums', r * np.linspace(1, 0.1, r.shape[1]), th + 0.2, 0.4)
    M.add('fx', tree.play(120), th + 0.1, 0.8)
    for k in range(24):                                   # glitter running out to both ends
        t = th + 0.08 * k
        M.add('sparkle', glock.play(sparkle[k % len(sparkle)], 80 - k), t, 0.8, float((-1) ** k * min(1, k / 10)))
    for t in np.arange(th, D - 1.5, BEAT / 2):
        M.add('fx', sleigh.play(int(70 * (1 - (t - th) / (D - th)))), t, 0.4)
