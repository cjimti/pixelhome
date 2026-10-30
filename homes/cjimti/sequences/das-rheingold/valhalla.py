"""Valhalla: out of the river's mist the faint circle of the Ring's beads still turns over the porch, and the
Ring motif (Donington 8, then its undercurrent, 8a) goes on in the horns, slower each time, its notes
smoothing out until they become something else: the Valhalla motif (63), in D flat, on trombones and tubas.
As it sounds the beads stop turning and settle into towers, and the castle gleams across the porch: Porch
Left, Porch Front and Porch Right lit as white-gold battlements, each chord of the brass a pulse through the
masonry, the walls spreading out from the keep and growing brighter as the brass grows.

Dawn comes up over a mountain meadow on the wings, the mist thinning into a blue-violet morning, and two
sleepers show in it on Left: Wotan, deep royal blue, and Fricka, rose silver, breathing slowly. Fricka wakes
first to her own call on oboe and violas, rises, sees the castle and goes to shake him: three nudges of rose
against blue. Wotan stirs, still dreaming it, the motif on a muted horn; then he sees it finished, stands,
and hails it in a full statement of Valhalla for the whole brass with timpani: every chord sends a sweep of
white-gold from the castle out over the meadow to both ends of the house, and his blue rises to meet it.

compose() holds every note, choreography() every position; render() and score() read both."""
import numpy as np
from pixelhome.audio import note
from pixelhome.fx import DT, hexc, light, smoothstep, nframes, Flicker
from pixelhome.leitmotifs import MOTIFS, play

CODE = 'RG06'
TITLE = 'Valhalla'
KIND = 'show'
DESCRIPTION = ('Out of the mist the shape of the Ring becomes a castle, gleaming across the porch at dawn. '
               'Wotan, king of the gods, sleeps in the meadow below it until Fricka wakes him, and he greets '
               'his new fortress with the brass at full strength.')
VOICEOVER = ('High on a mountain, morning comes up over a castle that was not there yesterday. '
             'Two giants built it. Nobody has paid them yet.')

T_RING = 0.3                                # the Ring, going on, round D flat
T_UNDER = 8.5                               # its undercurrent, slower, smoothing out
T_VAL = [15.0, 22.0]                        # Valhalla, soft, then fuller
VBEAT = 0.8
T_FRICKA = 29.0                             # Fricka wakes
NUDGES = [35.5, 36.5, 37.5]                 # she shakes him
T_DREAM = 39.0                              # Wotan stirs, dreaming of it
T_HAIL = 48.0                               # "Vollendet das ewige Werk!"
HBEAT = 0.85
T_CADENCE = T_HAIL + 16 * HBEAT
D = 80.0

WOTAN, FRICKA = 0, 1
BLUE = hexc('#1a3cff')
ROSE = hexc('#ff9ad0')
STONE = hexc('#fff0c0')
GOLD = hexc('#ffaa00')
RED = hexc('#ff1800')
DAWN_LO = hexc('#2a3a6a')
DAWN_HI = hexc('#6a5a8a')
GLOW = hexc('#ff9070')
NEAR = hexc('#a05a96')                      # the meadow near the castle, rosy at dawn
FAR = hexc('#2638a0')                       # and far from it, still blue
MIST = hexc('#6c70b8')
DUSK = hexc('#1c1c70')
WHITE = hexc('#ffffff')


def at(G, seg, u):
    s = G.pd[G.seg[seg]]
    return float(s.min() + u * (s.max() - s.min()))


def chords(key, t0, beat, transpose=0):
    """The motif's chords: [(time, seconds, [midi])], one per onset."""
    ev = {}
    for b, d, n in MOTIFS[key]['notes']:
        ev.setdefault(b, []).append((d, note(n) + transpose))
    return [(t0 + b * beat, max(d for d, _ in ev[b]) * beat, sorted(m for _, m in ev[b])) for b in sorted(ev)]


def compose():
    """Every note: (time, seconds, midi, velocity, part, who)."""
    N = []

    def add(t, d, m, v, part, who=None):
        N.append((float(t), float(d), note(m) if isinstance(m, str) else int(m), int(v), part, who))

    for t, m, v, d in play('ring', T_RING, 0.85, -6, 74):                      # RG05's Ring once more, slower
        add(t, d, m, v, 'ring' if m > note('C3') else 'ringbass')
    for t, m, v, d in play('ring_under_eb', T_UNDER, 0.8, -2, 70):              # smoothing out, in D flat
        add(t, d * 1.1, m, v, 'ring' if m > note('C3') else 'ringbass')
    add(0.0, T_VAL[0] + 1, 'Db2', 60, 'pedal')
    for m in ('Ab4', 'Db5', 'F5'):
        add(4.0, T_HAIL - 4.0, m, 50, 'dawn')
    for k, tv in enumerate(T_VAL):                                              # Valhalla, soft, then fuller
        for t, d, ms in chords('valhalla', tv, VBEAT):
            for m in ms:
                add(t, d * 1.05, m, (72, 86)[k], 'val', k)
    for k in range(int((T_HAIL - T_FRICKA) / 1.2)):                             # the meadow at morning: harp
        for j, m in enumerate(('Db3', 'Ab3', 'F4', 'Ab3')):
            add(T_FRICKA - 1 + k * 1.2 + j * 0.3, 1.0, note(m) + (0, 0, 5, 7, 0, 0)[k % 6] * (j == 2), 60, 'harp')
    call = [(0, .5, 'Ab3'), (.5, .5, 'Db4'), (1, 1.5, 'F4'), (3, .5, 'Eb4'), (3.5, 1.5, 'Db4'),
            (5.5, .5, 'F4'), (6, .5, 'Gb4'), (6.5, 2, 'Ab4'), (9, 1, 'Bb4'), (10, 1, 'Ab4'), (11, 2, 'F4')]
    for b, d, n in call:                                                        # "Wotan, husband, wake up!"
        add(T_FRICKA + b * 0.5, d * 0.5, n, 92, 'fricka', FRICKA)
    for t0, ch in ((0, ('Db3', 'F3')), (3, ('Gb2', 'Bb3')), (6, ('Db3', 'Ab3')), (9, ('Gb2', 'Db4'))):
        for m in ch:
            add(T_FRICKA + t0 * 0.5, 3 * 0.5 * 1.1, m, 66, 'fpad')
    for i, tn in enumerate(NUDGES):
        add(tn, 0.4, ('F4', 'Ab4', 'Db5')[i], 96, 'fricka', FRICKA)
        add(tn, 0.3, 'Db2', 80, 'nudge')
    for t, m, v, d in play('valhalla', T_DREAM, 0.95, 0, 70, line='melody'):   # dreaming of it
        add(t, d, m, v, 'dream', WOTAN)
    add(T_DREAM + 4, T_HAIL - T_DREAM - 4, 'Ab1', 70, 'roll')
    for k in range(2):                                                          # the full statement, twice
        for t, d, ms in chords('valhalla', T_HAIL + k * 8 * HBEAT, HBEAT, 0 if k == 0 else 0):
            for m in ms:
                add(t, d * 1.02, m, 104 + 8 * k, 'hail', WOTAN)
            add(t, 0.6, ms[0], 100 + 8 * k, 'timp')
    cad = [(0, 2, ('Gb2', 'Db3', 'Bb3', 'Gb4')), (2, 2, ('Ab2', 'Eb3', 'C4', 'Ab4')),
           (4, 6, ('Db2', 'Ab2', 'F3', 'Db4', 'F4', 'Ab4'))]
    for b, dd, ch in cad:                                                       # and a cadence that glows
        for m in ch:
            add(T_CADENCE + b * HBEAT, dd * HBEAT, m, 100, 'hail', WOTAN)
            if b == 4:
                add(T_CADENCE + b * HBEAT, D - T_CADENCE - b * HBEAT, m, 84, 'glow')
        add(T_CADENCE + b * HBEAT, 0.6, ch[0], 96, 'timp')
    add(T_CADENCE + 4 * HBEAT, 1.5, 'Db5', 92, 'cym')
    for m in ('Db4', 'F4', 'Ab4', 'Db5'):
        add(T_CADENCE + 4 * HBEAT, D - T_CADENCE - 4 * HBEAT, m, 60, 'shine')
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
    """Per frame: where Wotan and Fricka are (path distance)."""
    F = nframes(D)
    t = np.arange(F) * DT
    tgt = np.zeros((2, F))
    rate = np.full((2, F), 3.0)

    def set_(k, a, b, where, r):
        m = (t >= a) & (t < b)
        tgt[k][m] = where if np.ndim(where) == 0 else where[m]
        rate[k][m] = r

    W, Fr = at(G, 'Left', 0.7), at(G, 'Left', 0.45)
    set_(WOTAN, 0, D, W, 3.0)
    set_(FRICKA, 0, D, Fr, 3.0)
    set_(FRICKA, T_FRICKA + 3.0, NUDGES[0] - 1.0, Fr + 30, 1.5)                # up, looking at the castle
    set_(FRICKA, NUDGES[0] - 1.0, T_DREAM + 2, W - 28, 2.0)                     # over to him
    for tn in NUDGES:
        set_(FRICKA, tn, tn + 0.25, W - 14, 18.0)
    set_(FRICKA, T_HAIL - 4, D, Fr, 1.0)
    set_(WOTAN, T_HAIL, D, W + 6 * np.sin(2 * np.pi * t / 5.0), 2.0)
    pos = np.array([follow(tgt[k], rate[k]) for k in range(2)])
    return dict(t=t, pos=pos)


def render(G, seed=6):
    rng = np.random.default_rng(seed)
    F = nframes(D)
    out = np.zeros((F, G.N, 3))
    d = G.pd
    pf = at(G, 'Porch Front', 0.5)
    C = choreography(G)
    N = compose()
    porch = np.isin(G.seg_of, ['Porch Left', 'Porch Front', 'Porch Right']).astype(float)
    wing = 1 - porch
    p0, p1 = at(G, 'Porch Left', 0.0), at(G, 'Porch Right', 1.0)
    reach = np.maximum(np.abs(d - pf), 1)                   # how far from the keep, along the walls
    merlon = 0.5 + 0.5 * np.cos(2 * np.pi * (d - pf) / 46)
    merlon = smoothstep(0.25, 0.55, merlon)
    stone = 0.88 + 0.12 * rng.uniform(-1, 1, G.N)           # masonry: every block a little different
    rings = np.array([e[0] for e in N if e[4] == 'ring'])
    far = np.clip(np.where(d < p0, p0 - d, np.where(d > p1, d - p1, 0.0)) / 520, 0, 1)   # meadow: away from the castle
    vchords = sorted({round(e[0], 4) for e in N if e[4] == 'val'})
    hchords = sorted({round(e[0], 4) for e in N if e[4] == 'hail'})
    fr_notes = np.array([e[0] for e in N if e[4] == 'fricka'])
    dream = np.array([e[0] for e in N if e[4] == 'dream'])
    tw = Flicker(rng, G.N, 0.3, 1.2)
    grass = Flicker(rng, G.N, 0.1, 0.5)

    for f in range(F):
        t = f * DT
        fr = np.zeros((G.N, 3))

        # RG05's mist, thinning into a dawn over the meadow on the wings
        mist = 1 - smoothstep(4.0, 26.0, t)
        dawn = smoothstep(5.0, 40.0, t)
        tt = t + 80
        m1 = 0.5 + 0.5 * np.cos(2 * np.pi * (d / 520 + 0.05 * tt))
        m2 = 0.5 + 0.5 * np.cos(2 * np.pi * (d / 230 - 0.09 * tt) + 2)
        m3 = 0.5 + 0.5 * np.cos(2 * np.pi * (d / 900 - 0.03 * tt) + 4)
        fr += light(DUSK, (0.2 + 0.06 * m3) * mist)
        fr += light(MIST, (0.04 + 0.26 * (m1 * m2) ** 1.5 + 0.08 * m3) * mist)
        sky = DAWN_LO * (1 - dawn) + DAWN_HI * dawn
        sky = sky[None, :] * (1 - dawn * 0.6) + dawn * 0.6 * (NEAR[None, :] * (1 - far[:, None]) + FAR[None, :] * far[:, None])
        roll = 0.5 + 0.5 * np.cos(2 * np.pi * (d / 300 - 0.04 * t))
        fr += light(sky, (0.2 + 0.14 * dawn) * (1 - mist) * (0.85 + 0.1 * roll + 0.05 * grass(t)) * (wing + 0.6 * porch))
        c1 = 0.5 + 0.5 * np.cos(2 * np.pi * (d / 380 - 0.02 * t))
        c2 = 0.5 + 0.5 * np.cos(2 * np.pi * (d / 170 + 0.035 * t) + 1)
        cloud = smoothstep(0.35, 1.0, c1 * c2)              # dawn cloud drifting over the meadow
        fr += light(DAWN_HI, 0.3 * cloud * dawn * wing)
        horizon = np.exp(-((d - pf) / 750) ** 2)            # first light behind the castle, rosy
        fr += light(GLOW, (0.12 + 0.16 * cloud) * dawn * (1 - 0.5 * mist) * horizon * (0.9 + 0.1 * roll))

        # the Ring's beads: turning slower, then still, then they are towers
        settle = smoothstep(T_VAL[0] - 2, T_VAL[0] + 3, t)
        rs = 0.32 * (1 - settle)
        if rs > 0:
            ri = int(np.searchsorted(rings, t, side='right')) - 1
            rp = np.exp(-(t - rings[ri]) / 0.5) if ri >= 0 and t - rings[ri] < 2.5 else 0.0
            ph = 0.12 * (t + 12) - 0.12 * t ** 2 / (2 * (T_VAL[0] + 3)) * (t < T_VAL[0] + 3)
            th = 2 * np.pi * (np.arange(14) / 14 + ph)
            q, depth = pf + 420 * np.cos(th), np.sin(th)
            g = np.exp(-((d[:, None] - q[None, :]) / 26) ** 2)
            front = (g * np.clip(depth, 0, 1)[None, :]).max(axis=1)
            back = (g * np.clip(-depth, 0, 1)[None, :]).max(axis=1)
            fr += light(GOLD, rs * (1 + 0.5 * rp) * front) + light(RED, 0.6 * rs * (1 + 0.4 * rp) * back)

        # Valhalla: battlements spreading out from the keep, brighter as the brass grows
        grow = 0.2 * smoothstep(T_VAL[0] - 1, T_VAL[0] + 5, t) + 0.15 * smoothstep(T_VAL[1], T_VAL[1] + 6, t) \
            + 0.65 * smoothstep(T_HAIL - 1, T_HAIL + 4, t)
        extent = 120 + 520 * smoothstep(T_VAL[0] - 1, T_VAL[1] + 6, t)
        walls = smoothstep(extent + 60, extent - 60, reach) * porch
        pulse = 0.0
        for arr, w, tau in ((vchords, 0.35, 0.5), (hchords, 0.5, 0.35)):
            i = int(np.searchsorted(arr, t, side='right')) - 1
            if i >= 0 and t - arr[i] < 2:
                pulse = max(pulse, w * np.exp(-(t - arr[i]) / tau))
        gleam = 0.5 + 0.5 * np.cos(2 * np.pi * ((d - p0) / 260 - 0.18 * t))
        lvl = (0.22 * smoothstep(T_VAL[0] - 4, T_VAL[0], t) + 0.6 * grow + 0.4 * pulse) * walls * stone
        fr += light(STONE, lvl * (0.42 + 0.58 * merlon) * (0.85 + 0.15 * gleam ** 4))
        fr += light(WHITE, 0.35 * grow * walls * merlon * gleam ** 12 * (0.7 + 0.3 * tw(t)))

        # the hail: every chord sends white-gold out from the castle over the meadow to both ends
        for tc in hchords:
            if not tc <= t < tc + 2.0:
                continue
            age = t - tc
            dist = np.where(d < p0, p0 - d, np.where(d > p1, d - p1, 0.0))
            rf = 900 * smoothstep(0, 1.3, age)
            band = np.exp(-((dist - rf) / 200) ** 2) * wing * (1 - smoothstep(1.0, 2.0, age))
            fr += light(STONE, 0.65 * band)
        cad = smoothstep(T_CADENCE + 4 * HBEAT - 0.2, T_CADENCE + 4 * HBEAT + 0.3, t)
        if cad > 0:
            age = t - T_CADENCE - 4 * HBEAT
            fr += light(STONE, (0.55 * np.exp(-max(age, 0) / 0.5)) * np.ones(G.N))

        # the sleepers: breathing slowly, showing as the light comes; Fricka wakes, Wotan rises
        seen = smoothstep(6.0, 18.0, t)
        for k, col in ((WOTAN, BLUE), (FRICKA, ROSE)):
            p = C['pos'][k][f]
            breath = 0.5 + 0.5 * np.sin(2 * np.pi * t / (4.2 + 0.7 * k) + k)
            if k == FRICKA:
                awake = smoothstep(T_FRICKA - 0.5, T_FRICKA + 2.0, t)
                i = int(np.searchsorted(fr_notes, t, side='right')) - 1
                flare = np.exp(-(t - fr_notes[i]) / 0.25) if i >= 0 and t - fr_notes[i] < 1.2 else 0.0
            else:
                awake = 0.35 * smoothstep(T_DREAM - 0.5, T_DREAM + 2, t) + 0.65 * smoothstep(T_HAIL - 1, T_HAIL + 1.5, t)
                i = int(np.searchsorted(dream, t, side='right')) - 1
                flare = 0.6 * np.exp(-(t - dream[i]) / 0.5) if i >= 0 and t - dream[i] < 2 else 0.0
                flare = max(flare, pulse * smoothstep(T_HAIL - 1, T_HAIL, t))
            b = seen * (0.38 + 0.12 * breath * (1 - awake) + 0.4 * awake + 0.3 * flare)
            width = 18 + 10 * awake + 8 * flare
            fr += light(col, b * np.exp(-((d - p) / width) ** 2) + 0.35 * b * np.exp(-((d - p) / (70 + 60 * awake)) ** 2))
            fr += light(WHITE, 0.3 * seen * flare * np.exp(-((d - p) / 12) ** 2))
        for tn in NUDGES:                                   # rose against blue
            if tn <= t < tn + 0.8:
                age = t - tn
                wp = C['pos'][WOTAN][f]
                fr += light(ROSE, 0.7 * np.exp(-age / 0.25) * np.exp(-((d - wp) / 40) ** 2))
        if t > T_HAIL - 1:                                  # his blue rising to meet the castle's light
            up = smoothstep(T_HAIL - 1, T_HAIL + 3, t)
            wp = C['pos'][WOTAN][f]
            fr += light(BLUE, 0.4 * up * np.exp(-((d - wp) / 260) ** 2) * wing * (0.8 + 0.4 * pulse))
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
    pf = pan_at(at(G, 'Porch Front', 0.5))

    def pan_of(who, t):
        return pan_at(np.interp(t, C['t'], C['pos'][who]))

    for name, gain, rev in (('strings', 0.13, 0.35), ('low', 0.16, 0.2), ('brass', 0.16, 0.32), ('winds', 0.17, 0.35),
                            ('perc', 0.18, 0.3), ('harp', 0.16, 0.45), ('choir', 0.08, 0.5)):
        M.bus(name, gain=gain, reverb=rev)
    vtrem = M.sampler('Strings/Violin Section/Trem/*.wav', tune=-12)
    vn = M.sampler('Strings/Violin Section/susVib/*.wav', tune=-12)
    va = M.sampler('Strings/Viola Section/susvib/*.wav', tune=-12)
    vc = M.sampler('Strings/Cello Section/susvib/*.wav', tune=-12)
    cb = M.sampler('Strings/Solo Contrabass/SusNV/*.wav', tune=-12)
    mute = M.sampler('Brass/F Horn/mute/*.wav', tune=-12)
    horn = M.sampler('Brass/F Horn/sus/*.wav', tune=-12)
    tpt = M.sampler('Brass/Trumpet/sus/*.wav', tune=-12)
    tbn = M.sampler('Brass/Tenor Trombone/sus/*.wav', tune=-12)
    tuba = M.sampler('Brass/Tuba/sus/*.wav', tune=-12)
    ob = M.sampler('Woodwinds/Oboe/Vib/*.wav', tune=-12)
    cl = M.sampler('Woodwinds/Clarinet/susLong/*.wav', tune=-12)
    harp = M.sampler('Strings/Harp/*.wav')
    timp = M.hits('Percussion/Timpani/Timpani1_Hit*.wav')
    roll = M.hits('Percussion/Timpani/Rolls/*.wav')
    crash = M.hits('Percussion/cymbal-crash1_mf*.wav')
    susc = M.hits('Percussion/susCymb1-cresc-Median*.wav')

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

    pl, pr = pan_at(at(G, 'Porch Left', 0.5)), pan_at(at(G, 'Porch Right', 0.5))
    for t, d, m, v, part, who in compose():
        if part == 'ring':
            M.add('brass', horn.play(m, v, dur=d * 1.05, release=0.5), t, 0.85, pf)
            M.add('winds', cl.play(m, v - 16, dur=d * 1.05, release=0.5), t, 0.5, pf + 0.2)
        elif part == 'ringbass':
            hold('low', vc, m, t, t + d, v, 0.0, rise=1.0, fall=1.0, gain=0.7)
        elif part == 'pedal':
            hold('low', cb, m, t, t + d, v, 0.0, rise=2.0, fall=2.0, gain=0.7)
        elif part == 'dawn':
            hold('strings', vtrem, m, t, t + d, v, {68: -0.4, 73: 0.0, 77: 0.4}.get(m, 0.0), rise=10.0, fall=2.0,
                 gain=0.4)
        elif part in ('val', 'hail'):
            loud = part == 'hail'
            pan = (pl, pf, pr)[m % 3]
            if m >= note('Ab3'):
                M.add('brass', horn.play(m, v, dur=d, release=0.5), t, 0.75, pan)
                if loud and m >= note('Db4'):
                    M.add('brass', tpt.play(m, v - 12, dur=d, release=0.5), t, 0.45, pan)
                    M.add('strings', vn.play(m + 12, v - 20, dur=d, release=0.5), t, 0.35, -pan)
            elif m >= note('Db3'):
                M.add('brass', tbn.play(m, v, dur=d, release=0.5), t, 0.8, pan)
                if loud:
                    M.add('strings', va.play(m + 12, v - 16, dur=d, release=0.5), t, 0.35, pan)
            else:
                M.add('low', tuba.play(m + (12 if m < note('Db2') else 0), v, dur=d, release=0.6), t, 0.85, 0.0)
                M.add('low', cb.play(m, v - 10, dur=d, release=0.5), t, 0.6, 0.0)
                if loud or who == 1:
                    M.add('low', tbn.play(m + 12, v - 10, dur=d, release=0.5), t, 0.5, 0.0)
        elif part == 'harp':
            M.add('harp', harp.play(m, v), t, 1.0, pan_at(at(G, 'Left', 0.2)) + 0.5 * (m - 49) / 20)
        elif part == 'fricka':
            M.add('winds', ob.play(m, v, dur=d * 1.05, release=0.25), t, 1.0, pan_of(who, t))
            M.add('strings', va.play(m, v - 12, dur=d * 1.05, release=0.3), t, 0.6, pan_of(who, t))
        elif part == 'fpad':
            hold('strings', vc if m < note('C3') else va, m, t, t + d, v, -0.3, rise=0.4, fall=0.8, gain=0.5)
        elif part == 'nudge':
            M.add('low', cb.play(m, v, dur=d, release=0.1), t, 0.8, pan_of(WOTAN, t))
        elif part == 'dream':
            M.add('brass', mute.play(m, v, dur=d * 1.05, release=0.5), t, 1.0, pan_of(who, t))
            M.add('choir', M.synth('Pads/Ooh').render([(0.0, m, v - 20, d)], d + 1.5), t, 0.6, pan_of(who, t))
        elif part == 'roll':
            M.add('perc', roll.play(v, dur=d), t, 0.6, pf)
        elif part == 'glow':
            s = horn if m >= note('Ab3') else tbn if m >= note('Db3') else tuba
            hold('brass', s, m + (12 if m < note('Db2') else 0), t, t + d - 1.5, v, (pl, pf, pr)[m % 3], rise=1.5,
                 fall=1.5, gain=0.5)
        elif part == 'timp':
            M.add('perc', timp.play(v, pitch=(m % 12) - 7), t, 0.8, pf)
        elif part == 'cym':
            M.add('perc', crash.play(v), t, 0.8, 0.0)
        elif part == 'shine':
            hold('strings', vtrem, m, t, t + d, v, {61: -0.4, 65: -0.1, 68: 0.1, 73: 0.4}.get(m, 0.0), rise=1.0,
                 fall=1.0, gain=0.4)
    M.add('perc', susc.play(90), T_HAIL - 3.2, 0.5, 0.0)
