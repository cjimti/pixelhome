"""Up from the Depths: the third interlude, the climb out of Nibelheim with Alberich bound between Wotan and
Loge. The Nibelung rhythm (9/8 in B flat minor, every beat long-short-long) drives in the violas and basses
and climbs a step every two bars while eighteen anvils join in one by one: each rings at its own place on the
house in a white-hot burst, and stripes of forge glow run down and away from the porch on every beat. At the
top of the climb the trombones hammer the Ring motif's first notes over all eighteen anvils at once.

Then the caverns fall away beneath them: the red-orange glow drains outward from the porch to both ends of the
house and off the free ends, the hoard left behind in the dark fades, the anvils thin out one at a time and
the rhythm dies away. In a grey mist Alberich's woe sounds in the bassoon and trombone (a falling cry, his
red pulsing in its bindings), the Ring motif (Donington 8) stirs twice in the clarinets as the gold point on
his finger flares and a ring of beads circles it, and the Renunciation of Love (Donington 76a) passes in the
cellos while a cold shadow crosses the house.

Grey dawn on the mountaintop: the wings fill with a dim dawn, every colour faded toward grey, because the gods
have grown old while Freia is away. Valhalla rises dim across the porch, its battlements a row of pale masonry
blocks, to the Valhalla motif (Donington 63) on muted horns and tubas; Wotan's blue has greyed with it, only
Loge's fire is undimmed, and the downfall motif (Donington 4) sighs once in the low winds. Wotan, Loge (the
helmet's violet still in his hand) and the bound Alberich stand on the porch.

compose() holds every note, choreography() every position; render() and score() read both."""
import numpy as np
from pixelhome.audio import note
from pixelhome.fx import DT, hexc, light, smoothstep, nframes, Flicker
from pixelhome.leitmotifs import play

CODE = 'RG18'
TITLE = 'Up from the Depths'
KIND = 'show'
DESCRIPTION = ('The long climb out of the caverns, with Alberich tied up and dragged along. Eighteen anvils '
               'hammer as the glow of the forges falls away beneath them, and they come out into a grey dawn '
               'where even the gods look old.')
VOICEOVER = ('Up through the rock, past every forge and every anvil, dragging the dwarf behind them. '
             'And at the top, a cold grey morning.')

NB = 0.45                                   # a dotted-quarter beat of the 9/8
CLIMB = [0, 0, 2, 2, 3, 3, 5, 5, 7, 7, 8, 8, 10, 10]      # a step up every two bars (semitones)
T_PEAK = 15.5                               # all eighteen anvils; the trombones hammer the Ring
T_DRAIN = 19.0                              # the caverns fall away
T_QUIET = 31.0                              # the rhythm gone
T_WOE = 32.0                                # Alberich's woe
RINGS = [38.0, 43.5]                        # the Ring stirs in the clarinets
T_REN = 48.0                                # the Renunciation passes in the cellos
T_DAWN = 53.0                               # grey dawn
T_VAL = [59.0, 67.0]                        # Valhalla, faded
VB = 0.75
T_DOWN = 74.0                               # the downfall motif, once
D = 80.0

CAVE = hexc('#b01c00')
EMBER = hexc('#ff5a10')
FORGE = hexc('#ff7a10')
ALB = hexc('#ff1000')
MUD = hexc('#5a1200')
GOLD = hexc('#ffaa00')
HOT = hexc('#fff0a0')
RED = hexc('#ff1800')
WOTAN = hexc('#1a3cff')
SPEAR = hexc('#c8d8ff')
LOGE1 = hexc('#ff5000')
LOGE2 = hexc('#ffb020')
TARN = hexc('#5a4a8a')
STEEL = hexc('#5a88d0')
MIST = hexc('#3c3c78')
SHADOW = hexc('#1c1880')
DAWN1 = hexc('#2a3a6a')
DAWN2 = hexc('#6a5a8a')
VAL = hexc('#fff0c0')

NIB = [('Bb3', 'A3', 'Bb3'), ('Db4', 'C4', 'Db4'), ('F4', 'E4', 'F4'),
       ('Gb4', 'F4', 'Gb4'), ('F4', 'E4', 'F4'), ('Db4', 'C4', 'Bb3')]
NANVIL = 18


def at(G, seg, u):
    s = G.pd[G.seg[seg]]
    return float(s.min() + u * (s.max() - s.min()))


def grey(c, k):
    """Colour c faded k of the way to grey (the gods growing old)."""
    return c * (1 - k) + (c @ np.array([0.3, 0.59, 0.11])) * k


def nibelung(t0, t1, beat, vel, tr):
    """The Nibelung rhythm from t0 to t1: each dotted-quarter beat long-short-long. vel(t) and tr(bar) give the
    loudness and the climb -> [(t, seconds, midi, velocity, beat index, j)]."""
    out, k = [], 0
    while t0 + k * beat < t1:
        for j, (off, dur) in enumerate(((0, 0.5), (0.5, 1 / 6), (2 / 3, 1 / 3))):
            t = t0 + (k + off) * beat
            out.append((t, dur * beat * 0.85, note(NIB[k % 6][j]) + tr(k // 6), int(vel(t)), k, j))
        k += 1
    return out


def anvils_at(t):
    """How many of the eighteen anvils are ringing at time t."""
    up = 6 + 12 * smoothstep(0, T_PEAK, t)
    return int(round(up * (1 - smoothstep(T_DRAIN, T_QUIET - 2, t))))


def compose():
    """Every note: (time, seconds, midi, velocity, part, who). who is an anvil for 'anvil'."""
    rng = np.random.default_rng(18)
    N = []

    def add(t, d, m, v, part, who=None):
        N.append((float(t), float(d), note(m) if isinstance(m, str) else int(m), int(v), part, who))

    def vel(t):
        return 104 + 18 * smoothstep(0, T_PEAK, t) - 70 * smoothstep(T_DRAIN, T_QUIET, t)

    def tr(bar):
        return CLIMB[min(bar, len(CLIMB) - 1)]

    order = rng.permutation(NANVIL)
    for t, d, m, v, k, j in nibelung(0.0, T_QUIET, NB, vel, tr):
        add(t, d, m, v, 'nib')
        if j == 0:
            add(t, d, m - 24, v - 6, 'nibbass')
        n = anvils_at(t)
        if j == 1:
            n = n // 2
        for a in order[:n]:
            add(t, 0.1, 0, int(min(124, v + rng.integers(-8, 6))), 'anvil', int(a))
        order = np.roll(order, 1) if j == 2 and t > T_DRAIN else order
    add(0.0, T_QUIET, 'Bb1', 80, 'climb')
    for t, m, v, d in play('ring', T_PEAK - 0.5, NB * 2 / 3 * 1.5, -2, 120):
        if t < T_DRAIN + 1.5:
            add(t, d, m, v, 'ringbrass')
    add(T_PEAK - 0.5, 0.8, 'Bb1', 124, 'peak')

    for b, d, m in ((0, 1.5, 'Db4'), (1.5, 2.5, 'C4'), (4, 1.5, 'Bb3'), (5.5, 2.5, 'A3'),      # woe! woe!
                    (8, 1, 'Gb3'), (9, 1, 'F3'), (10, 4, 'E3')):
        add(T_WOE + b * 0.42, d * 0.42, m, 96, 'woe')
        add(T_WOE + b * 0.42, d * 0.42, note(m) - 12, 90, 'woelow')
    add(T_QUIET - 1.0, T_DAWN - T_QUIET + 2.0, 'Bb1', 56, 'mistpedal')
    for i, t0 in enumerate(RINGS):
        for t, m, v, d in play('ring', t0, 0.6, -12 * i, 78):
            if t < t0 + 4.5 * 0.6 and m > note('C3'):
                add(t, d, m, v, 'ringwinds')
    for t, m, v, d in play('renunciation_low', T_REN, 0.7, -12, 88):
        add(t, d, m, v, 'renounce')

    for m in ('Db3', 'Ab3', 'F4'):                          # the grey morning chord
        add(T_DAWN, D - T_DAWN, m, 58, 'dawn')
    add(T_DAWN, D - T_DAWN, 'Db2', 56, 'dawnbass')
    for i, t0 in enumerate(T_VAL):
        for t, m, v, d in play('valhalla', t0, VB, 0, 70 + 6 * i):
            add(t, d, m, v, 'valhalla')
    for t, m, v, d in play('downfall', T_DOWN, 0.6, -12, 70, line='melody'):
        add(t, d, m, v, 'downfall')
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
    """Per frame: bound Alberich, Wotan, Loge (path distance). The three hold their places as they climb."""
    F = nframes(D)
    t = np.arange(F) * DT
    climb = 1 - smoothstep(T_DRAIN, T_QUIET, t)
    jog = 5 * np.sin(2 * np.pi * t / (6 * NB)) * climb      # jolted along by the climb
    jit = 9 * np.sin(2 * np.pi * t / 0.7) + 6 * np.sin(2 * np.pi * t / 0.37)
    return dict(t=t, alb=at(G, 'Porch Front', 0.2) + jog + 3 * np.sin(2 * np.pi * t / 2.3),
                wot=at(G, 'Porch Front', 0.4) + jog + 6 * np.sin(2 * np.pi * t / 3.1),
                loge=at(G, 'Porch Front', 0.75) + jit)


def anvil_spots(G):
    L = G.length
    return np.linspace(0.04 * L, 0.97 * L, NANVIL)[np.random.default_rng(5).permutation(NANVIL)]


def render(G, seed=18):
    rng = np.random.default_rng(seed)
    F = nframes(D)
    out = np.zeros((F, G.N, 3))
    d = G.pd
    L = G.length
    pf = at(G, 'Porch Front', 0.5)
    ph = at(G, 'Porch Front', 0.65)
    C = choreography(G)
    N = compose()
    nibs = np.array([e[0] for e in N if e[4] == 'nib'])
    anvils = [(e[0], e[5], e[3]) for e in N if e[4] == 'anvil']
    woes = np.array([e[0] for e in N if e[4] == 'woe'])
    rings = np.array([e[0] for e in N if e[4] == 'ringwinds'])
    brass = np.array([e[0] for e in N if e[4] == 'ringbrass'])
    vals = np.array([e[0] for e in N if e[4] == 'valhalla'])
    spots = anvil_spots(G)
    tw = Flicker(rng, G.N, 2.0, 7.0)
    fl = Flicker(rng, G.N, 3.0, 11.0)
    smoulder = Flicker(rng, G.N, 0.6, 2.4)
    drift = Flicker(rng, G.N, 0.08, 0.3)
    spark = np.zeros(G.N)
    porch = np.isin(G.seg_of, ['Porch Left', 'Porch Front', 'Porch Right'])
    wings = ~porch
    po = np.zeros(G.N)
    po[porch] = d[porch] - d[porch].min()
    merlon = np.where((po // 24) % 2 == 0, 1.0, 0.3) * porch
    edge = np.abs(d - pf)
    huey = np.clip(1 - np.minimum(d, L - d) / (0.45 * L), 0, 1)       # dawn: violet toward the porch

    def blob(p, w):
        return np.exp(-((d - p) / w) ** 2)

    def last(arr, t, tau, span=2.0):
        i = int(np.searchsorted(arr, t, side='right')) - 1
        return float(np.exp(-(t - arr[i]) / tau)) if i >= 0 and t - arr[i] < span else 0.0

    for f in range(F):
        t = f * DT
        fr = np.zeros((G.N, 3))
        ap, wp, lp = C['alb'][f], C['wot'][f], C['loge'][f]
        old = smoothstep(T_DAWN, T_DAWN + 8, t)
        beat = last(nibs, t, 0.12, 0.5) * (1 - smoothstep(T_DRAIN, T_QUIET, t))

        # the caverns: red-orange, stripes running down and away on the beat, draining out from the porch
        front = (L * 0.62) * smoothstep(T_DRAIN, T_QUIET + 1, t) ** 1.3
        keep = smoothstep(front - 60, front + 160, edge) * (1 - smoothstep(T_QUIET - 1, T_QUIET + 2, t))
        tt = t + 80.0                                       # the cavern's breathing carries on from The Toad
        w1 = 0.5 + 0.5 * np.cos(2 * np.pi * (d / 320 - 0.07 * tt))
        w2 = 0.5 + 0.5 * np.cos(2 * np.pi * (d / 130 + 0.21 * tt) + 1)
        fr += light(CAVE, (0.27 + 0.1 * w1) * keep) + light(EMBER, (0.05 + 0.14 * w1 * w2) * keep)
        speed = 0.9 + 0.8 * smoothstep(0, T_PEAK, t) + 1.2 * smoothstep(T_DRAIN, T_QUIET, t)
        stripe = (0.5 + 0.5 * np.cos(2 * np.pi * (edge / 170 - speed * t + 0.7))) ** 3
        fr += light(FORGE, (0.3 + 0.18 * beat) * stripe * keep)
        rim = np.exp(-((edge - front) / 70) ** 2) * (T_DRAIN < t < T_QUIET + 1)       # the falling edge
        fr += light(EMBER, 0.5 * rim * keep.max(initial=0))
        spark *= np.exp(-DT / 0.12)
        spark[rng.random(G.N) < 0.014 * keep] = 1.0
        fr += light(FORGE, 0.75 * spark)
        for ta, a, v in anvils:
            if ta <= t < ta + 0.5:
                g = (v / 115) * keep[np.argmin(np.abs(d - spots[a]))] ** 0.5
                fr += light(HOT, g * np.exp(-(t - ta) / 0.09) * blob(spots[a], 16))
                fr += light(FORGE, 0.7 * g * np.exp(-(t - ta) / 0.25) * blob(spots[a], 45))
        pk = last(brass, t, 0.3)
        if T_PEAK - 0.6 <= t < T_DRAIN + 2:
            fr += light(FORGE, 0.55 * pk * np.ones(G.N)) + light(GOLD, 0.35 * pk * blob(ap, 200))
        hoard = 1 - smoothstep(T_DRAIN, T_DRAIN + 6, t)
        if hoard > 0:
            fr += light(GOLD, hoard * (0.62 * blob(ph, 30) + 0.2 * blob(ph, 80)))
            fr += light(HOT, 0.45 * hoard * blob(ph, 14) * (0.6 + 0.4 * tw(t)) * (tw(t) > 0.3))

        # the mist between: grey-violet, drifting; a cold shadow while the renunciation passes
        mist = smoothstep(T_DRAIN + 4, T_QUIET, t) * (1 - 0.6 * old)
        fr += light(MIST, mist * (0.22 + 0.1 * drift(t)))
        for tw0 in woes:                                    # each cry of woe a red ripple out through the mist
            if tw0 <= t < tw0 + 2.5:
                rr = 900 * (t - tw0) ** 0.7
                fr += light(ALB, 0.45 * (1 - (t - tw0) / 2.5) * np.exp(-((np.abs(d - ap) - rr) / 90) ** 2))
        stir = sum(smoothstep(r0, r0 + 0.5, t) * (1 - smoothstep(r0 + 2.5, r0 + 4.5, t)) for r0 in RINGS)
        if stir > 0:                                        # the Ring's glints scattered through the mist
            fr += light(GOLD, 0.6 * stir * (rng.random(G.N) < 0.035))
        cold = smoothstep(T_REN, T_REN + 1.5, t) * (1 - smoothstep(T_REN + 4.0, T_REN + 6.5, t))
        if cold > 0:
            reach = (L / 2 + 300) * smoothstep(T_REN, T_REN + 4.5, t)
            shade = np.maximum(smoothstep(reach, reach - 300, d), smoothstep(L - reach, L - reach + 300, d)) * cold
            fr += light(SHADOW, 0.35 * shade)

        # grey dawn on the meadow; Valhalla dim across the porch, each Valhalla chord a breath of light
        if old > 0:
            dc = DAWN1[None, :] * (1 - huey[:, None]) + DAWN2[None, :] * huey[:, None]
            dc = dc * 0.9 + (dc @ np.array([0.3, 0.59, 0.11]))[:, None] * 0.1
            swell = 0.5 + 0.5 * np.cos(2 * np.pi * (d / 900 - 0.05 * (t - T_DAWN)))
            lev = (0.36 + 0.1 * swell + 0.06 * drift(t)) * old * (wings + 0.5 * porch)
            fr += (np.clip(lev, 0, None) ** 2.2)[:, None] * dc
            vb = last(vals, t, 0.5)
            castle = smoothstep(T_DAWN + 3, T_VAL[0] + 2, t)
            fr += light(grey(VAL, 0.15), castle * (0.34 + 0.1 * vb) * merlon)

        # Loge, undimmed; the helmet's violet in his hand
        fk = 0.5 + 0.5 * np.tanh(fl(t))
        lb = blob(lp, 22)
        fr += light(LOGE1, 0.7 * lb * (1 - 0.5 * fk) + 0.25 * blob(lp, 70))
        fr += light(LOGE2, 0.55 * lb * fk)
        fr += light(TARN, 0.6 * blob(lp, 34) * (0.7 + 0.3 * tw(t)))

        # Wotan, greying with the dawn
        wc = grey(WOTAN, 0.4 * old)
        fr += light(wc, (0.85 + 0.15 * beat) * blob(wp, 22) + 0.3 * blob(wp, 90))
        fr += light(grey(SPEAR, 0.3 * old), 0.25 * blob(wp, 7))

        # Alberich, bound: red under steel-blue bands, his woe pulsing through them; the ring on his finger
        wo = last(woes, t, 0.5)
        fr += light(MUD, 0.32 * blob(ap, 90) * (1 + 0.15 * smoulder(t)))
        fr += light(ALB, (0.72 + 0.35 * wo) * blob(ap, 24 + 10 * wo) * (1 + 0.2 * smoulder(t)))
        wrap = (0.5 + 0.5 * np.cos(2 * np.pi * (d - ap) / 16 + 3 * t)) ** 2 * blob(ap, 34)
        fr += light(STEEL, (0.8 + 0.2 * beat) * wrap)
        rp = last(rings, t, 0.4)
        fr += light(GOLD, (0.9 + 0.4 * rp) * blob(ap, 6)) + light(RED, 0.7 * blob(ap + 9, 6) * (0.6 + 0.4 * tw(t)))
        ring = sum(smoothstep(r0, r0 + 0.5, t) * (1 - smoothstep(r0 + 2.5, r0 + 3.5, t)) for r0 in RINGS)
        if ring > 0:
            th = 2 * np.pi * (np.arange(12) / 12 + 0.3 * t)
            q, depth = ap + 160 * np.cos(th), np.sin(th)
            g = np.exp(-((d[:, None] - q[None, :]) / 18) ** 2)
            fr += light(GOLD, ring * (0.8 + 0.3 * rp) * (g * np.clip(depth, 0, 1)[None, :]).max(axis=1))
            fr += light(RED, ring * 0.55 * (g * np.clip(-depth, 0, 1)[None, :]).max(axis=1))
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
    spots = anvil_spots(G)
    pa = pan_at(C['alb'][0])
    pw = pan_at(C['wot'][0])
    pv = pan_at(at(G, 'Porch Front', 0.5))

    for name, gain, rev in (('winds', 0.18, 0.35), ('strings', 0.16, 0.3), ('low', 0.18, 0.18), ('brass', 0.17, 0.3),
                            ('perc', 0.2, 0.22), ('anvil', 0.24, 0.25)):
        M.bus(name, gain=gain, reverb=rev)
    bsus = M.sampler('Woodwinds/Bassoon/sus/*.wav', tune=-12)
    clar = M.sampler('Woodwinds/Clarinet/susLong/*.wav', tune=-12)
    vn = M.sampler('Strings/Violin Section/Spic/*.wav', tune=-12)
    vas = M.sampler('Strings/Viola Section/spic/*.wav', tune=-12)
    vatrem = M.sampler('Strings/Viola Section/trem/*.wav', tune=-12)
    vcs = M.sampler('Strings/Cello Section/spic/*.wav', tune=-12)
    vc = M.sampler('Strings/Cello Section/susvib/*.wav', tune=-12)
    trem = M.sampler('Strings/Cello Section/trem/*.wav', tune=-12)
    cb = M.sampler('Strings/Solo Contrabass/SusNV/*.wav', tune=-12)
    cbs = M.sampler('Strings/Solo Contrabass/Spic/*.wav', tune=-12)
    mute = M.sampler('Brass/F Horn/mute/*.wav', tune=-12)
    horn = M.sampler('Brass/F Horn/sus/*.wav', tune=-12)
    tbn = M.sampler('Brass/Tenor Trombone/sus/*.wav', tune=-12)
    tuba = M.sampler('Brass/Tuba/sus/*.wav', tune=-12)
    timp = M.hits('Percussion/Timpani/Timpani1_Hit*.wav')
    crash = M.hits('Percussion/cymbal-crash1_f*.wav')
    anvil = M.hits('Percussion/Anvil_Hit1_v*.wav')

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

    pitch = np.random.default_rng(3).uniform(-7, 5, NANVIL)
    for t, d, m, v, part, who in compose():
        if part == 'nib':
            M.add('strings', vas.play(m, v), t, 1.0, -0.3)
            M.add('strings', vn.play(m + 12, v - 15), t, 0.7, 0.3)
        elif part == 'nibbass':
            M.add('low', cbs.play(m + 12, v), t, 1.0, 0.0)
            M.add('low', vcs.play(m + 12, v - 10), t, 0.8, 0.0)
        elif part == 'anvil':
            M.add('anvil', anvil.play(v, pitch=pitch[who]), t, 1.0, pan_at(spots[who]))
        elif part == 'climb':
            hold('low', trem, m + 12, t, t + d, v, 0.0, rise=0.3, fall=3.0, gain=0.8)
        elif part == 'ringbrass':
            if m >= note('C4'):
                M.add('brass', horn.play(m, v, dur=d, release=0.3), t, 0.9, pa - 0.1)
            elif m >= note('C3'):
                M.add('brass', tbn.play(m, v, dur=d, release=0.3), t, 1.0, pa + 0.1)
            else:
                M.add('low', tuba.play(m, v, dur=d, release=0.3), t, 0.9, 0.0)
        elif part == 'peak':
            M.add('perc', timp.play(v, pitch=-2), t, 1.0, 0.0)
            M.add('perc', crash.play(v), t, 0.8, 0.0)
        elif part == 'woe':
            M.add('winds', bsus.play(m, v, dur=d, release=0.25), t, 1.0, pa)
        elif part == 'woelow':
            M.add('brass', tbn.play(m, v, dur=d, release=0.25), t, 0.7, pa)
        elif part == 'mistpedal':
            hold('low', cb, m, t, t + d, v, 0.0, rise=2.0, fall=2.5, gain=0.8)
        elif part == 'ringwinds':
            M.add('winds', clar.play(m, v, dur=d * 1.05, release=0.3), t, 1.0, pa)
        elif part == 'renounce':
            M.add('strings', vc.play(m, v, dur=d, release=0.5), t, 1.0, -0.1)
        elif part == 'dawn':
            hold('strings', vatrem, m, t, t + d, v, {note('Db3'): -0.4, note('Ab3'): 0.4}.get(m, 0.0),
                 rise=4.0, fall=1.0, gain=0.6)
        elif part == 'dawnbass':
            hold('low', cb, m, t, t + d, v, 0.0, rise=4.0, fall=1.0, gain=0.7)
        elif part == 'valhalla':
            if m >= note('F3'):
                M.add('brass', mute.play(m, v, dur=d * 1.05, release=0.5), t, 0.9, pv + (m % 3 - 1) * 0.25)
            else:
                M.add('low', tuba.play(m, v, dur=d * 1.05, release=0.5), t, 0.7, pv)
        elif part == 'downfall':
            M.add('winds', clar.play(m, v, dur=d, release=0.4), t, 0.9, pw)
            M.add('winds', bsus.play(m - 12, v - 10, dur=d, release=0.4), t, 0.7, pw)
