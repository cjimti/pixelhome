"""Alberich's Curse: Loge unties him. The steel-blue bindings unwind off his red in a widening spiral to a
falling harp, and Alberich, free and with nothing left, laughs bitterly in the bassoon. Then the grey morning
drains away into red and black, Valhalla and the meadow sinking out of sight, and he swears that the ring will
bring ruin and death to whoever holds it.

The Curse motif (Donington 13), twice: timpani and basses hammer F sharp underneath; the line climbs through
the half-diminished chord (F sharp, A, C, E) in low clarinets and trombones and falls an octave onto a murky
low C major. Every note of the climb sends a red ring out from Alberich, wider as it rises, and the ring's red
glint on Wotan's hand pulses with it; the fall drops a muddy wash over the whole house. The second time is
slower and louder, trombones and tubas in full, and a tam-tam at the fall. The Ring motif murmurs once more,
low, in the bassoons (Donington 8a), as an oath kept, not a ritual: no magic, only a promise of what greed for
the ring will do.

Then he slinks off: back along Porch Left, the length of Left, and out along Side to its far dark end, in
halting steps to a creeping bassoon and pizzicato, his red trailing mud, the curse muttering on a muted horn,
until he is gone. The red-black lifts, the grey dawn and the dim battlements of Valhalla come back, and the
gods (Fricka, Donner and Froh, all faded toward grey) appear on the wings. Wotan gazes at the ring (its
motif soft in the clarinets, his red glint pulsing) while Loge flickers. In the last seconds the giants'
heavy tread sounds in the tubas and timpani, and at the free end of Right the giants appear, Fasolt stone
grey and Fafner ochre, with Freia's pink between them.

compose() holds every note, choreography() every position; render() and score() read both."""
import numpy as np
from pixelhome.audio import note
from pixelhome.fx import DT, hexc, light, smoothstep, nframes, Flicker
from pixelhome.leitmotifs import play, MOTIFS

CODE = 'RG20'
TITLE = "Alberich's Curse"
KIND = 'show'
DESCRIPTION = ("Set free with nothing left, Alberich swears that the ring will bring ruin and death to whoever "
               "holds it, and the whole house turns red and black. Then he slinks away into the dark, and the "
               "giants come back for their payment.")
VOICEOVER = ('They took his gold, his helmet, and his ring. '
             'So before he goes, he makes them a promise.')

T_UNTIE = 0.8                               # Loge unwinds the bindings
T_LAUGH = 5.0                               # free: a bitter laugh
T_DARK = 8.5                                # red and black
CURSES = [(11.0, 0.6, 0), (25.0, 0.7, 1)]   # (start, beat, which)
T_OATH = 39.8                               # the Ring, low, in the bassoons
T_EXIT = 45.0                               # he slinks off
STEPS = 14
T_GONE = 58.0
T_CLEAR = 57.0                              # the mist begins to clear
T_GAZE = 61.0                               # Wotan gazes at the ring
T_LOGE = 67.5
T_GIANTS = 72.0                             # their tread; they appear at the end of Right
D = 80.0

ALB = hexc('#ff1000')
MUD = hexc('#5a1200')
BLOOD = hexc('#ff0800')
GOLD = hexc('#ffaa00')
HOT = hexc('#fff0a0')
RED = hexc('#ff1800')
WOTAN = hexc('#1a3cff')
SPEAR = hexc('#c8d8ff')
LOGE1 = hexc('#ff5000')
LOGE2 = hexc('#ffb020')
TARN = hexc('#5a4a8a')
STEEL = hexc('#5a88d0')
DAWN1 = hexc('#2a3a6a')
DAWN2 = hexc('#6a5a8a')
VAL = hexc('#fff0c0')
FRICKA = hexc('#ff9ad0')
DONNER = hexc('#a0c0ff')
FASOLT = hexc('#8090a0')
FAFNER = hexc('#c07a10')
FREIA = hexc('#ff5a9a')
WHITE = hexc('#ffffff')
GODS = [('Left', 0.6, 'fricka'), ('Left', 0.3, 'donner'), ('Right', 0.3, 'froh')]
GIANTS = [('Right', 0.78, FASOLT, 20), ('Right', 0.865, FREIA, 13), ('Right', 0.95, FAFNER, 20)]


def at(G, seg, u):
    s = G.pd[G.seg[seg]]
    return float(s.min() + u * (s.max() - s.min()))


def grey(c, k):
    return c * (1 - k) + (c @ np.array([0.3, 0.59, 0.11])) * k


def compose():
    """Every note: (time, seconds, midi, velocity, part, who). who: the curse (0, 1) and, for its melody, the step."""
    N = []

    def add(t, d, m, v, part, who=None):
        N.append((float(t), float(d), note(m) if isinstance(m, str) else int(m), int(v), part, who))

    for m in ('Db3', 'Ab3', 'F4'):
        add(0.0, T_DARK + 1.0, m, 60, 'dawn')
    for k in range(12):                                     # the knots undone
        add(T_UNTIE + k * 0.28, 0.5, note('Bb5') - (0, 2, 3, 5, 7, 9, 10, 12, 14, 15, 17, 19)[k], 88 - 2 * k, 'untie')
    for t, m, v, d in play('loge_flicker', T_UNTIE + 0.2, 0.2, 0, 80):
        add(t, d, m, v, 'loge')
    for j, m in enumerate(('F3', 'E3', 'Eb3', 'D3', 'Db3', 'C3', 'B2', 'Bb2')):
        add(T_LAUGH + j * 0.2, 0.12, m, 100 - 3 * j, 'laugh')
    add(T_LAUGH + 1.8, 1.4, 'Gb2', 104, 'scorn')
    add(T_DARK, T_CLEAR + 3 - T_DARK, 'Gb1', 64, 'darkpedal')

    for t0, cb, which in CURSES:                            # the Curse
        mel = sorted((b, d, note(n)) for b, d, n in MOTIFS['curse']['notes'] if note(n) >= note('C3') and b < 16)
        for i, (b, d, m) in enumerate(mel):
            add(t0 + b * cb, d * cb, m, 100 + 14 * which, 'curse', (which, i))
        for b in (0, 4, 8, 12, 16):
            add(t0 + b * cb, 4 * cb, 'Gb1', 104 + 14 * which, 'pedal', (which, -1))
        for m in ('C3', 'E3', 'G3'):                       # the fall onto murky C major
            add(t0 + 16 * cb, 4 * cb, m, 96 + 14 * which, 'fall', (which, -1))
        add(t0 + 16 * cb, 4 * cb, 'C2', 100 + 14 * which, 'fallbass', (which, -1))
        if which:
            add(t0 + 16 * cb, 4.0, 'C2', 120, 'gong', (which, -1))
    for t, m, v, d in play('ring_under', T_OATH, 0.6, -12, 92):
        add(t, d, m, v, 'oath')

    for k in range(STEPS):                                  # slinking off
        ts = T_EXIT + k * (T_GONE - T_EXIT) / STEPS
        add(ts, 0.35, note('E3') - k, 84 - 2 * k, 'slink')
        add(ts + 0.45, 0.2, note('E2') - k, 70, 'creep')
    for t, m, v, d in play('curse', T_EXIT + 5.0, 0.55, 0, 70, line='melody'):
        if note('C3') <= m and t < T_EXIT + 5.0 + 12 * 0.55:
            add(t, d, m, v, 'mutter')

    for m in ('Db3', 'Ab3', 'F4'):                          # the morning comes back
        add(T_CLEAR, D - T_CLEAR, m, 58, 'dawn')
    for t, m, v, d in play('ring', T_GAZE, 0.7, 0, 74):
        if m > note('C3'):
            add(t, d, m, v, 'gaze')
    for t, m, v, d in play('loge_flicker', T_LOGE, 0.22, 0, 76):
        add(t, d, m, v, 'loge')
    for t, m, v, d in play('giants', T_GIANTS, 0.5, -12, 70):
        add(t, d, m, v, 'giants')
    for b in range(0, 8, 1):                                # their tread
        add(T_GIANTS + b * 1.0, 0.6, 'C2', 70 + 6 * b, 'tread')
    for t, m, v, d in play('freia', T_GIANTS + 4.5, 0.4, 12, 60, line='melody'):
        if t < D - 0.5:
            add(t, d, m, v, 'freia')
    return sorted(N, key=lambda e: e[0])


def follow(target, rate):
    x = np.empty_like(target)
    x[0], v = target[0], 0.0
    for f in range(1, len(target)):
        w = rate[f]
        v += (w * w * (target[f] - x[f - 1]) - 2 * w * v) * DT
        x[f] = x[f - 1] + v * DT
    return x


def choreography(G):
    """Per frame: Alberich, Wotan, Loge (path distance)."""
    F = nframes(D)
    t = np.arange(F) * DT
    tgt = np.zeros((3, F))
    rate = np.full((3, F), 3.0)

    def set_(k, a, b, where, r):
        m = (t >= a) & (t < b)
        tgt[k][m] = where if np.ndim(where) == 0 else where[m]
        rate[k][m] = r

    A = at(G, 'Porch Front', 0.2) - 14
    set_(0, 0, D, A, 2.0)
    set_(0, T_LAUGH, T_EXIT, A + 8 + 4 * np.sin(2 * np.pi * t / 2.0), 3.0)
    for k in range(STEPS):                                  # halting steps out to the far end of Side
        ts = T_EXIT + k * (T_GONE - T_EXIT) / STEPS
        set_(0, ts, D, A + (-60 - A) * (k + 1) / STEPS, 6.0)
    W, Lg = at(G, 'Porch Front', 0.4), at(G, 'Porch Front', 0.75)
    set_(1, 0, D, W + 6 * np.sin(2 * np.pi * t / 3.1), 2.0)
    jit = 9 * np.sin(2 * np.pi * t / 0.7) + 6 * np.sin(2 * np.pi * t / 0.37)
    set_(2, 0, D, Lg + jit, 4.0)
    set_(2, T_UNTIE - 0.5, T_LAUGH, A + 40 + 25 * np.sin(2 * np.pi * t / 0.8), 8.0)      # untying him
    set_(2, T_LAUGH, D, Lg + jit, 1.5)
    pos = np.array([follow(tgt[k], rate[k]) for k in range(3)])
    return dict(t=t, alb=pos[0], wot=pos[1], loge=pos[2])


def render(G, seed=20):
    rng = np.random.default_rng(seed)
    F = nframes(D)
    out = np.zeros((F, G.N, 3))
    d = G.pd
    L = G.length
    pf = at(G, 'Porch Front', 0.5)
    C = choreography(G)
    N = compose()
    curse = [(e[0], e[2], e[5]) for e in N if e[4] == 'curse']
    falls = sorted({e[0] for e in N if e[4] == 'fall'})
    pedals = np.array([e[0] for e in N if e[4] == 'pedal'])
    cnotes = np.array([e[0] for e in N if e[4] == 'curse'])
    gaze = np.array([e[0] for e in N if e[4] == 'gaze'])
    oath = np.array([e[0] for e in N if e[4] == 'oath'])
    tread = np.array([e[0] for e in N if e[4] == 'tread'])
    steps = np.array([e[0] for e in N if e[4] == 'slink'])
    laugh = np.array([e[0] for e in N if e[4] == 'laugh'])
    tw = Flicker(rng, G.N, 2.0, 7.0)
    fl = Flicker(rng, G.N, 3.0, 11.0)
    smoulder = Flicker(rng, G.N, 0.6, 2.4)
    drift = Flicker(rng, G.N, 0.08, 0.3)
    churn = Flicker(rng, G.N, 0.15, 0.6)
    porch = np.isin(G.seg_of, ['Porch Left', 'Porch Front', 'Porch Right'])
    wings = ~porch
    po = np.zeros(G.N)
    po[porch] = d[porch] - d[porch].min()
    merlon = np.where((po // 24) % 2 == 0, 1.0, 0.3) * porch
    huey = np.clip(1 - np.minimum(d, L - d) / (0.45 * L), 0, 1)
    dc = DAWN1[None, :] * (1 - huey[:, None]) + DAWN2[None, :] * huey[:, None]
    dc = dc * 0.9 + (dc @ np.array([0.3, 0.59, 0.11]))[:, None] * 0.1
    wc = grey(WOTAN, 0.4)
    side = G.seg_of == 'Side'
    gpos = [at(G, s, u) for s, u, _ in GODS]
    hw = 22.0                                               # the heap, full

    def blob(p, w):
        return np.exp(-((d - p) / w) ** 2)

    def last(arr, t, tau, span=2.0):
        i = int(np.searchsorted(arr, t, side='right')) - 1
        return float(np.exp(-(t - arr[i]) / tau)) if i >= 0 and t - arr[i] < span else 0.0

    for f in range(F):
        t = f * DT
        fr = np.zeros((G.N, 3))
        ap, wp, lp = C['alb'][f], C['wot'][f], C['loge'][f]
        dark = smoothstep(T_DARK, T_DARK + 2.5, t) * (1 - smoothstep(T_CLEAR, T_CLEAR + 9, t))
        clear = 1 - dark
        pd_ = last(pedals, t, 0.4, 3.0)
        cn = last(cnotes, t, 0.3)

        # the grey morning and Valhalla, sinking under red and black, coming back as the mist clears
        swell = 0.5 + 0.5 * np.cos(2 * np.pi * (d / 900 - 0.05 * (t + 54)))
        lev = (0.36 + 0.1 * swell + 0.06 * drift(t)) * (wings + 0.5 * porch) * (0.12 + 0.88 * clear)
        fr += (np.clip(lev, 0, None) ** 2.2)[:, None] * dc
        fr += light(grey(VAL, 0.15), 0.34 * merlon * (0.1 + 0.9 * clear))
        if dark > 0:
            gaps = np.clip(0.55 + 0.45 * churn(t), 0, 1) ** 2
            fr += light(BLOOD, dark * (0.26 + 0.06 * pd_) * gaps)
            fr += light(MUD, dark * 0.3 * (1 - gaps))
        for tc, m, (which, i) in curse:                     # each climbing note: a red ring out from him
            if tc <= t < tc + 2.5:
                a = t - tc
                rr = (300 + 55 * (m - 54)) * a ** 0.6 * (1 + 0.3 * which)
                fr += light(BLOOD, (0.6 + 0.15 * which) * (1 - a / 2.5) * np.exp(-((np.abs(d - ap) - rr) / (60 + 6 * (m - 54))) ** 2))
        for tf in falls:                                    # the fall: a muddy wash sinking over the house
            if tf <= t < tf + 3.5:
                a = t - tf
                fr += light(MUD, 0.75 * np.exp(-a / 1.2) * np.ones(G.N))
                fr += light(BLOOD, 0.5 * np.exp(-a / 0.3) * np.ones(G.N))

        # the hoard, helmet on top
        fr += light(GOLD, 0.9 * blob(pf, hw) + 0.25 * blob(pf, 2 * hw))
        fr += light(HOT, 0.6 * blob(pf, 0.5 * hw) * (0.5 + 0.5 * tw(t)) * (tw(t) > 0))
        fr += light(TARN, 0.55 * blob(pf, hw + 8) * (0.6 + 0.4 * tw(t)))

        # Loge, untying him, then back by the heap
        fk = 0.5 + 0.5 * np.tanh(fl(t))
        lb = blob(lp, 22)
        fr += light(LOGE1, 0.7 * lb * (1 - 0.5 * fk) + 0.25 * blob(lp, 70))
        fr += light(LOGE2, 0.55 * lb * fk)

        # Wotan, with the ring: its red glint pulsing with every note of the curse, gold point steady
        fr += light(wc, 0.85 * blob(wp, 22) + 0.3 * blob(wp, 90))
        fr += light(grey(SPEAR, 0.3), 0.25 * blob(wp, 7))
        gz = last(gaze, t, 0.4)
        glint = 0.6 + 0.9 * cn + 0.5 * last(oath, t, 0.4) + 0.4 * gz + 0.3 * dark
        fr += light(GOLD, (0.95 + 0.3 * gz) * blob(wp, 6))
        fr += light(RED, glint * blob(wp + 9, 6 + 6 * cn) * (0.6 + 0.4 * tw(t)))

        # Alberich: unbound, laughing, swelling with every note of the curse; then slinking off into the dark
        free = smoothstep(T_UNTIE, T_UNTIE + 3.5, t)
        if t < T_UNTIE + 4.5:
            wrap = (0.5 + 0.5 * np.cos(2 * np.pi * (d - ap) / 16 + 3 * t)) ** 2 * blob(ap, 34)
            fr += light(STEEL, 0.8 * (1 - free) * wrap)
            R = 30 + 320 * free
            th = 2 * np.pi * (np.arange(6) / 6 - 0.8 * (t - T_UNTIE))
            q, depth = ap + R * np.cos(th), np.sin(th)
            g = np.exp(-((d[:, None] - q[None, :]) / 14) ** 2) * (0.5 + 0.5 * depth)[None, :]
            fr += light(STEEL, 0.8 * free * (1 - smoothstep(T_UNTIE + 3, T_UNTIE + 4.5, t)) * g.max(axis=1))
        lg = last(laugh, t, 0.15, 0.5)
        oathing = smoothstep(CURSES[0][0] - 1, CURSES[0][0], t) * (1 - smoothstep(T_EXIT - 1, T_EXIT + 1, t))
        gone = smoothstep(T_GONE - 4, T_GONE + 0.5, t)
        st = last(steps, t, 0.2, 1.0)
        ab = (0.45 + 0.25 * free + 0.25 * lg + 0.25 * oathing + 0.45 * cn * oathing + 0.15 * st) * (1 - gone)
        if ab > 0.01:
            fr += light(MUD, (0.35 + 0.15 * oathing) * (1 - gone) * blob(ap, 90 + 60 * oathing) * (1 + 0.15 * smoulder(t)))
            fr += light(ALB, ab * blob(ap, 24 + 14 * oathing * cn) * (1 + 0.2 * smoulder(t)))
            if T_EXIT <= t < T_GONE + 1:                    # trailing mud as he goes
                trail = smoothstep(ap + 200, ap, d) * (d > ap)
                fr += light(MUD, 0.4 * (1 - gone) * trail)
        if T_EXIT <= t:                                     # Side darkens behind him as he disappears
            fr *= 1 - 0.3 * (side * smoothstep(T_GONE - 3, T_GONE, t) * (1 - smoothstep(T_GONE + 2, T_GONE + 6, t)))[:, None]

        # the gods, greyed, on the wings as the mist clears
        gods = smoothstep(T_CLEAR + 3, T_CLEAR + 9, t)
        if gods > 0:
            for (s, u, who), gp in zip(GODS, gpos):
                if who == 'froh':
                    hue = (0.1 * t + d / 400) % 1.0
                    c = np.stack([np.clip(np.abs(hue * 6 - 3) - 1, 0, 1), np.clip(2 - np.abs(hue * 6 - 2), 0, 1),
                                  np.clip(2 - np.abs(hue * 6 - 4), 0, 1)], -1)
                    c = c * 0.45 + (c @ np.array([0.3, 0.59, 0.11]))[:, None] * 0.55
                    fr += (np.clip(gods * 0.6 * blob(gp, 26), 0, None) ** 2.2)[:, None] * c
                else:
                    c = grey(FRICKA if who == 'fricka' else DONNER, 0.55)
                    fr += light(c, gods * (0.6 * blob(gp, 20) + 0.15 * blob(gp, 70)))

        # the giants and Freia, appearing at the free end of Right; every tread a thud of their colour
        gi = smoothstep(T_GIANTS + 1, D - 1.5, t)
        if gi > 0:
            tr = last(tread, t, 0.25, 1.0)
            for s, u, col, w in GIANTS:
                p = at(G, s, u)
                b = gi * (0.75 + (0.3 * tr if col is not FREIA else 0.0))
                fr += light(col, b * blob(p, w) + 0.2 * gi * blob(p, 2.5 * w))
            fr += light(FASOLT, 0.25 * tr * gi * smoothstep(at(G, 'Right', 0.7), L, d))
        out[f] = fr
    return np.clip(out, 0, 1)


def score(M, G):
    from pixelhome.audio import SR
    order = np.argsort(G.pd)
    xs, ds = G.pos[order, 0], G.pd[order]
    x0, x1 = xs.min(), xs.max()

    def pan_at(dd):
        x = np.interp(dd, ds, xs)
        return float(0.85 * (2 * (x - x0) / (x1 - x0) - 1))

    C = choreography(G)
    pg = pan_at(at(G, 'Right', 0.865))
    pv = pan_at(at(G, 'Porch Front', 0.5))

    def pan_of(k, t):
        return pan_at(np.interp(t, C['t'], C[k]))

    for name, gain, rev in (('winds', 0.22, 0.35), ('strings', 0.19, 0.3), ('low', 0.24, 0.18), ('brass', 0.22, 0.3),
                            ('perc', 0.24, 0.25), ('harp', 0.2, 0.4)):
        M.bus(name, gain=gain, reverb=rev)
    bsn = M.sampler('Woodwinds/Bassoon/stac/*.wav', tune=-12)
    bsus = M.sampler('Woodwinds/Bassoon/sus/*.wav', tune=-12)
    clar = M.sampler('Woodwinds/Clarinet/susLong/*.wav', tune=-12)
    pic = M.sampler('Woodwinds/Piccolo/Stac/*.wav', tune=-12)
    vn = M.sampler('Strings/Violin Section/susVib/*.wav', tune=-12)
    vns = M.sampler('Strings/Violin Section/Spic/*.wav', tune=-12)
    vatrem = M.sampler('Strings/Viola Section/trem/*.wav', tune=-12)
    trem = M.sampler('Strings/Cello Section/trem/*.wav', tune=-12)
    vc = M.sampler('Strings/Cello Section/susvib/*.wav', tune=-12)
    cb = M.sampler('Strings/Solo Contrabass/SusNV/*.wav', tune=-12)
    pizz = M.sampler('Strings/Solo Contrabass/Pizz/*.wav', tune=-12)
    mute = M.sampler('Brass/F Horn/mute/*.wav', tune=-12)
    horn = M.sampler('Brass/F Horn/sus/*.wav', tune=-12)
    tbn = M.sampler('Brass/Tenor Trombone/sus/*.wav', tune=-12)
    tuba = M.sampler('Brass/Tuba/sus/*.wav', tune=-12)
    harp = M.sampler('Strings/Harp/*.wav')
    timp = M.hits('Percussion/Timpani/Timpani1_Hit*.wav')
    roll = M.hits('Percussion/Timpani/Rolls/*.wav')
    gong = M.hits('Percussion/gongHit_f*.wav')
    bd = M.hits('Percussion/BDrumNewhit_v[3-6]*.wav')

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
        pa, pw = pan_of('alb', t), pan_of('wot', t)
        if part == 'dawn':
            hold('strings', vatrem, m, t, t + d, v, {note('Db3'): -0.4, note('Ab3'): 0.4}.get(m, 0.0),
                 rise=1.0 if t == 0 else 5.0, fall=2.0, gain=0.6)
        elif part == 'untie':
            M.add('harp', harp.play(m - 12, v), t, 1.0, pan_of('loge', t))
        elif part == 'loge':
            M.add('winds', pic.play(m, v), t, 0.8, pan_of('loge', t))
            M.add('strings', vns.play(m - 12, v - 15), t, 0.5, pan_of('loge', t))
        elif part == 'laugh':
            M.add('winds', bsn.play(m - 12, v), t, 1.0, pa)
        elif part == 'scorn':
            M.add('brass', tbn.play(m, v, dur=d, release=0.3), t, 0.9, pa)
        elif part == 'darkpedal':
            hold('low', trem, m + 12, t, t + d, v, 0.0, rise=2.5, fall=3.0, gain=1.0)
        elif part == 'curse':
            which = who[0]
            M.add('winds', clar.play(m - 12, v, dur=d * 1.02, release=0.3), t, 1.0, pa)
            M.add('brass', tbn.play(m - 12 * (m > note('C4')), v - 10 + 10 * which, dur=d, release=0.3), t,
                  0.6 + 0.4 * which, pa)
            if which:
                M.add('brass', horn.play(m, v - 14, dur=d, release=0.3), t, 0.5, pa - 0.15)
        elif part == 'pedal':
            M.add('perc', timp.play(v, pitch=-6), t, 1.0, 0.0)
            M.add('perc', roll.play(v - 30, dur=d * 0.9), t + 0.1, 0.4, 0.0)
            hold('low', cb, m + 12, t, t + d, v, 0.0, rise=0.05, fall=0.5, gain=0.8)
        elif part == 'fall':
            M.add('brass', tbn.play(m, v, dur=d, release=0.6), t, 0.8, pa + 0.2 * (m % 3 - 1))
            M.add('winds', clar.play(m, v - 10, dur=d, release=0.6), t, 0.6, pa)
        elif part == 'fallbass':
            M.add('low', tuba.play(m, v, dur=d, release=0.6), t, 1.0, 0.0)
            hold('low', cb, m + 12, t, t + d, v, 0.0, rise=0.05, fall=1.0, gain=0.8)
            M.add('perc', bd.play(v), t, 0.7, 0.0)
        elif part == 'gong':
            M.add('perc', gong.play(v), t, 0.9, pa)
        elif part == 'oath':
            if m < note('C3'):
                hold('low', vc, m + 12, t, t + d, v, 0.0, rise=0.3, fall=1.0, gain=0.7)
            else:
                M.add('winds', bsus.play(m, v, dur=d, release=0.3), t, 1.0, pa)
        elif part == 'slink':
            M.add('winds', bsus.play(m - 12, v, dur=d, release=0.15), t, 1.0, pa)
        elif part == 'creep':
            M.add('low', pizz.play(m + 12, v), t, 0.9, pa)
        elif part == 'mutter':
            M.add('brass', mute.play(m, v, dur=d, release=0.4), t, 0.8, pa)
        elif part == 'gaze':
            M.add('winds', clar.play(m, v, dur=d * 1.05, release=0.3), t, 1.0, pw)
        elif part == 'giants':
            M.add('brass', tuba.play(m, v, dur=d * 1.1, release=0.3), t, 1.0, pg)
            M.add('brass', tbn.play(m + 12, v - 16, dur=d * 1.1, release=0.3), t, 0.6, pg)
        elif part == 'tread':
            M.add('perc', timp.play(v, pitch=-8), t, 0.9, pg)
            M.add('perc', bd.play(v), t, 0.6, pg)
        elif part == 'freia':
            M.add('strings', vn.play(m, v, dur=d * 1.05, release=0.3), t, 0.7, pg)
