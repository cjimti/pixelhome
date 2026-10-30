"""Fricka: the castle stands gleaming across the porch, the meadow lies in dawn light on the wings, and Wotan
(deep blue) and Fricka (rose silver) stand on Left. She rounds on him: the price of the castle is her own
sister Freia, promised to the giants who built it. The argument takes the whole house. Her rose floods in
from the far ends of both wings and his blue holds the ground by the castle, and the front between them
surges back and forth, sparking where they meet. Her reproaches are agitated oboe and violas over driving
cellos, each phrase shoving the rose toward the porch.

He answers with his treaties (Donington 14), slow and heavy in trombones and tubas, and the blue pushes her
back. She softens and tells him why she wanted the castle at all: a home that would keep him by her. That is
her own tune here, warm, on violas and oboe over the harp, and the front melts into a wide mauve blend while
she comes close to him. He shrugs it off, she flares up again (would he really give Freia away?), and he says
the contract will be kept in other ways: his spear (73), its long descending scale on the trombones, drawn as
a steel white-blue line out from him toward the castle, one step for every note, the treaties glinting along
it. The argument drains out of the wings; she steps back, uneasy, he turns away, and from far off to the right
a flute catches a scrap of Freia's tune.

compose() holds every note, choreography() every position; render() and score() read both."""
import numpy as np
from pixelhome.audio import note
from pixelhome.fx import DT, hexc, light, smoothstep, nframes, Flicker
from pixelhome.leitmotifs import play

CODE = 'RG07'
TITLE = 'Fricka'
KIND = 'show'
DESCRIPTION = ('Fricka reminds Wotan what the castle cost: her sister Freia, promised to the giants as their '
               'wages. Watch their colours fight for the house, his blue against her rose, until he lays down '
               'the law with his spear.')
VOICEOVER = ('Fricka has a question for her husband. The castle is finished, so who exactly is going to pay '
             'for it?')

BEAT = 0.5
REPROACH = [2.5, 7.0, 11.5]                 # her reproaches, each a shove of rose
T_TREATY = 17.0                             # his treaties
TBEAT = 0.6
T_HOME = 28.0                               # her longing: a home to keep him by her
HBEAT = 0.6
T_SHRUG = 41.0
T_FLARE = 44.0                              # "you would give Freia away?"
T_SPEAR = 50.0                              # the contract will be kept in other ways
SBEAT = 0.5
T_TREATY2 = T_SPEAR + 6.0
T_UNEASE = 64.0
T_FREIA = 74.5                              # far off, a scrap of Freia's tune
D = 80.0

WOTAN, FRICKA = 0, 1
BLUE = hexc('#1a3cff')
ROSE = hexc('#ff9ad0')
MAUVE = hexc('#a050e0')
STEEL = hexc('#c8d8ff')
STONE = hexc('#fff0c0')
DAWN_HI = hexc('#6a5a8a')
GLOW = hexc('#ff9070')
NEAR = hexc('#a05a96')
FAR = hexc('#2638a0')
WHITE = hexc('#ffffff')


def at(G, seg, u):
    s = G.pd[G.seg[seg]]
    return float(s.min() + u * (s.max() - s.min()))


def compose():
    """Every note: (time, seconds, midi, velocity, part, who)."""
    N = []

    def add(t, d, m, v, part, who=None):
        N.append((float(t), float(d), note(m) if isinstance(m, str) else int(m), int(v), part, who))

    for m in ('Db4', 'F4', 'Ab4'):                                              # RG06's last chord, dying away
        add(0.0, 2.5, m, 70, 'glow')
    add(0.0, 2.5, 'Db2', 70, 'glow')
    phrases = [
        [(0, .5, 'D4'), (.5, .5, 'F4'), (1, 1, 'A4'), (2, .5, 'Bb4'), (2.5, .5, 'A4'), (3, .5, 'G4'), (3.5, .5, 'F4'),
         (4, 1, 'E4'), (5, .5, 'F4'), (5.5, .5, 'G4'), (6, 1.5, 'A4')],
        [(0, .5, 'F4'), (.5, .5, 'A4'), (1, 1, 'C5'), (2, .5, 'D5'), (2.5, .5, 'C5'), (3, .5, 'Bb4'), (3.5, .5, 'A4'),
         (4, 1, 'G4'), (5, .5, 'A4'), (5.5, .5, 'Bb4'), (6, 1.5, 'C5')],
        [(0, .5, 'A4'), (.5, .5, 'C5'), (1, 1, 'Eb5'), (2, .5, 'D5'), (2.5, .5, 'C5'), (3, .5, 'Bb4'), (3.5, .5, 'A4'),
         (4, 1, 'G4'), (5, .5, 'F#4'), (5.5, .5, 'G4'), (6, 2, 'D4')]]
    for k, (t0, ph) in enumerate(zip(REPROACH, phrases)):                     # her reproaches, agitated
        for b, d, n in ph:
            add(t0 + b * BEAT, d * BEAT, n, 96 + 4 * k, 'fricka', FRICKA)
        for j, ch in enumerate((('D3', 'A3', 'F4'), ('G2', 'D3', 'Bb3'), ('A2', 'E3', 'C#4'))):
            for m in ch:
                add(t0 + j * 1.4, 1.5, note(m) + 3 * (k == 2) * (j == 0), 76 + 4 * k, 'trem')
    for k in range(int((T_TREATY - REPROACH[0]) / (BEAT / 2))):                # the cellos driving under her
        m = ('D2', 'D2', 'F2', 'D2', 'A1', 'D2', 'Bb1', 'A1')[k % 8]
        add(REPROACH[0] + k * BEAT / 2, BEAT / 2 * 0.8, m, 88 + 8 * (k % 4 == 0), 'drive')
    for t, m, v, d in play('treaties', T_TREATY, TBEAT, 0, 100):              # his treaties
        add(t, d, m, v, 'treaty', WOTAN)
    sweet = [(0, 1.5, 'Bb3'), (1.5, .5, 'Db4'), (2, 2, 'Gb4'), (4, 1, 'F4'), (5, 1, 'Eb4'), (6, 2, 'Db4'),
             (8, 1.5, 'Eb4'), (9.5, .5, 'F4'), (10, 1, 'Gb4'), (11, 1, 'Ab4'), (12, 2, 'Bb4'), (14, 1, 'Ab4'),
             (15, 1, 'F4'), (16, 1.5, 'Gb4'), (17.5, .5, 'Ab4'), (18, 2, 'Gb4')]
    for b, d, n in sweet:                                                       # a home to keep him by her
        add(T_HOME + b * HBEAT, d * HBEAT, n, 90, 'home', FRICKA)
    for b, ch in ((0, ('Gb2', 'Db3', 'Bb3')), (4, ('Cb3', 'Eb3', 'Ab3')), (8, ('Ab2', 'Eb3', 'C4')),
                  (12, ('Gb2', 'Db3', 'Bb3')), (16, ('Db3', 'Ab3', 'F4')), (18, ('Gb2', 'Db3', 'Bb3'))):
        for m in ch:
            add(T_HOME + b * HBEAT, (4 if b < 16 else 2.2) * HBEAT * 1.08, m, 70, 'hpad')
        for j, m in enumerate(ch + (ch[1],)):
            add(T_HOME + b * HBEAT + j * HBEAT / 2, 1.0, note(m) + 12, 66, 'harp')
    for b, d, n in ((4, 2, 'Db3'), (6, 2, 'Eb3'), (8, 2, 'Ab2'), (12, 2, 'Bb2'), (14, 2, 'Db3')):
        add(T_HOME + b * HBEAT, d * HBEAT, n, 74, 'soft', WOTAN)                # he softens, a little
    for b, d, n in ((0, .5, 'D3'), (.5, .5, 'F3'), (1, 1.5, 'Bb2')):
        add(T_SHRUG + b * BEAT, d * BEAT, n, 90, 'shrug', WOTAN)
    for b, d, n in ((0, .25, 'Eb5'), (.25, .25, 'D5'), (.5, .5, 'C5'), (1, .5, 'Bb4'), (1.5, .5, 'A4'), (2, 1, 'D5'),
                    (3, .5, 'C5'), (3.5, .5, 'Bb4'), (4, 1.5, 'G4'), (6, .5, 'A4'), (6.5, .5, 'Bb4'), (7, 1.5, 'D5')):
        add(T_FLARE + b * BEAT, d * BEAT, n, 108, 'fricka', FRICKA)              # would he give Freia away?
    for j in range(8):
        add(T_FLARE + j * 0.5, 0.45, ('G2', 'G2', 'Bb2', 'G2', 'D2', 'G2', 'Eb2', 'D2')[j], 100, 'drive')
    for t, m, v, d in play('spear', T_SPEAR, SBEAT, 0, 116):                   # the spear
        add(t, d, m, v, 'spear', WOTAN)
    add(T_SPEAR, 0.8, 'Bb1', 118, 'hit')
    for t, m, v, d in play('treaties', T_TREATY2, TBEAT * 0.75, 0, 84):        # the treaties, carved on it
        add(t, d, m, v, 'treaty2', WOTAN)
    for m in ('D3', 'F3', 'A3'):
        add(T_UNEASE, D - T_UNEASE, m, 70, 'uneasy')
        add(T_SHRUG - 0.5, T_FLARE - T_SHRUG + 0.5, note(m) - 2, 66, 'uneasy')
    add(T_UNEASE, D - T_UNEASE, 'D2', 72, 'pedal')
    add(T_SPEAR + 4, T_UNEASE - T_SPEAR - 3, 'Bb1', 76, 'pedal')
    for b, d, n in ((0, 1, 'A4'), (1, 1, 'Bb4'), (2, 2, 'A4'), (5, 1, 'F4'), (6, 1, 'E4'), (7, 3, 'D4')):
        add(T_UNEASE + 1.5 + b * BEAT, d * BEAT, n, 80, 'fricka', FRICKA)
    for t, m, v, d in play('freia', T_FREIA, 0.42, 12, 64, line='melody'):    # far off: Freia
        if t < D - 0.8:
            add(t, d, m, v, 'distant')
    return sorted(N, key=lambda e: e[0])


def follow(target, rate):
    x = np.empty_like(target)
    x[0], v = target[0], 0.0
    for f in range(1, len(target)):
        w = rate[f]
        v += (w * w * (target[f] - x[f - 1]) - 2 * w * v) * DT
        x[f] = x[f - 1] + v * DT
    return x


def push(t):
    """Who holds the wings: 0 all his blue, 1 all her rose (fraction of each wing from its far end)."""
    marks = [(0.0, 0.0), (2.5, 0.12)]
    for k, t0 in enumerate(REPROACH):
        marks += [(t0 + 0.2, (0.3, 0.5, 0.7)[k] - 0.1), (t0 + 1.2, (0.3, 0.5, 0.7)[k] + 0.08),
                  (t0 + 4.2, (0.3, 0.5, 0.7)[k])]
    marks += [(T_TREATY, 0.72), (T_TREATY + 2.4, 0.6), (T_TREATY + 4.8, 0.48), (T_TREATY + 7.2, 0.36),
              (T_TREATY + 9.6, 0.3), (T_HOME + 3, 0.5), (T_HOME + 11, 0.55), (T_SHRUG, 0.5), (T_SHRUG + 1.2, 0.4),
              (T_FLARE + 0.3, 0.55), (T_FLARE + 2.0, 0.78), (T_FLARE + 4.5, 0.82), (T_SPEAR, 0.8),
              (T_SPEAR + 5.5, 0.15), (T_UNEASE, 0.15), (T_UNEASE + 6, 0.2)]
    ts, us = zip(*marks)
    return np.interp(t, ts, us)


def choreography(G):
    """Per frame: where Wotan and Fricka are, and how far her rose has pushed into each wing."""
    F = nframes(D)
    t = np.arange(F) * DT
    tgt = np.zeros((2, F))
    rate = np.full((2, F), 3.0)

    def set_(k, a, b, where, r):
        m = (t >= a) & (t < b)
        tgt[k][m] = where if np.ndim(where) == 0 else where[m]
        rate[k][m] = r

    W, Fr = at(G, 'Left', 0.7), at(G, 'Left', 0.45)
    set_(WOTAN, 0, D, W + 4.3 * np.sin(2 * np.pi * (t + 80) / 5.0 - 1.12), 8.0)     # his sway, as RG06 left it
    set_(FRICKA, 0, D, Fr, 3.0)
    for k, t0 in enumerate(REPROACH):                                           # stepping at him
        set_(FRICKA, t0, t0 + 4.4, Fr + 25 + 12 * k, 4.0)
    set_(WOTAN, T_TREATY, T_HOME, W + 10, 1.5)
    set_(FRICKA, T_TREATY, T_HOME, Fr - 10, 1.5)
    set_(FRICKA, T_HOME + 2, T_SHRUG, W - 35, 0.6)                             # close to him
    set_(WOTAN, T_SHRUG, D, at(G, 'Left', 0.75), 1.2)                          # he turns away
    set_(FRICKA, T_FLARE, T_SPEAR, Fr + 60, 3.0)
    set_(FRICKA, T_SPEAR, D, Fr, 1.0)
    pos = np.array([follow(tgt[k], rate[k]) for k in range(2)])
    u = follow(push(t), np.full(F, 4.0))
    return dict(t=t, pos=pos, push=u)


def render(G, seed=7):
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
    L0, R0 = at(G, 'Left', 1.0), at(G, 'Right', 0.0)
    reach = np.maximum(np.abs(d - pf), 1)
    merlon = smoothstep(0.25, 0.55, 0.5 + 0.5 * np.cos(2 * np.pi * (d - pf) / 46))
    stone = 0.88 + 0.12 * np.random.default_rng(6).uniform(-1, 1, G.N)        # the same stones as RG06
    walls = smoothstep(700, 580, reach) * porch
    far = np.clip(np.where(d < p0, p0 - d, np.where(d > p1, d - p1, 0.0)) / 520, 0, 1)
    sky = 0.4 * DAWN_HI[None, :] + 0.6 * (NEAR[None, :] * (1 - far[:, None]) + FAR[None, :] * far[:, None])
    # each wing as 0 at the castle .. 1 at its far end; her rose holds the far part
    wfrac = np.where(d <= L0, 1 - d / L0, np.where(d >= R0, (d - R0) / (G.length - R0), -1.0))
    sung = {k: np.array([e[0] for e in N if e[4] in ('fricka', 'home', 'treaty', 'spear', 'shrug', 'soft')
                         and e[5] == k]) for k in (WOTAN, FRICKA)}
    shoves = np.array([e[0] for e in N if e[4] == 'fricka' and e[1] >= BEAT])
    spear = np.array([e[0] for e in N if e[4] == 'spear'])
    treaty2 = np.array([e[0] for e in N if e[4] == 'treaty2'])
    tw = Flicker(rng, G.N, 0.3, 1.2)
    grass = Flicker(rng, G.N, 0.1, 0.5)
    edge_n = Flicker(rng, G.N, 1.5, 4.0)

    for f in range(F):
        t = f * DT
        tt = t + 80
        fr = np.zeros((G.N, 3))
        wp = C['pos'][WOTAN][f]
        argue = smoothstep(1.0, 4.0, t) * (1 - smoothstep(T_UNEASE - 2, T_UNEASE + 6, t))
        warmth = smoothstep(T_HOME, T_HOME + 4, t) * (1 - smoothstep(T_SHRUG - 1, T_SHRUG + 1.5, t))

        # the meadow at dawn and the castle behind (as RG06 left them)
        roll = 0.5 + 0.5 * np.cos(2 * np.pi * (d / 300 - 0.04 * tt))
        bed = (0.34 * (0.85 + 0.1 * roll + 0.05 * grass(t)) * (wing + 0.6 * porch))
        fr += light(sky, bed * (1 - 0.6 * argue * wing))
        c1 = 0.5 + 0.5 * np.cos(2 * np.pi * (d / 380 - 0.02 * tt))
        c2 = 0.5 + 0.5 * np.cos(2 * np.pi * (d / 170 + 0.035 * tt) + 1)
        cloud = smoothstep(0.35, 1.0, c1 * c2)
        fr += light(DAWN_HI, 0.3 * cloud * wing * (1 - argue))
        fr += light(GLOW, (0.12 + 0.16 * cloud) * np.exp(-((d - pf) / 750) ** 2) * (0.9 + 0.1 * roll))
        gleam = 0.5 + 0.5 * np.cos(2 * np.pi * ((d - p0) / 260 - 0.18 * tt))
        castle = 0.82 - 0.15 * argue + 0.12 * warmth
        fr += light(STONE, castle * walls * stone * (0.42 + 0.58 * merlon) * (0.85 + 0.15 * gleam ** 4))
        fr += light(WHITE, 0.35 * walls * merlon * gleam ** 12 * (0.7 + 0.3 * tw(t)))

        # the argument: her rose from the far ends, his blue from the castle, a sparking front between
        if argue > 0:
            u = C['push'][f]
            edge = 0.035 + 0.1 * warmth
            front = (1 - u) + 0.025 * edge_n(t)
            rose = smoothstep(front - edge, front + edge, wfrac) * (wfrac >= 0)
            blue = (1 - rose) * (wfrac >= 0)
            seam = np.exp(-((wfrac - front) / (0.03 + 0.12 * warmth)) ** 2) * (wfrac >= 0)
            si = int(np.searchsorted(shoves, t, side='right')) - 1
            jolt = np.exp(-(t - shoves[si]) / 0.2) if si >= 0 and t - shoves[si] < 1 else 0.0
            wave = 0.5 + 0.5 * np.cos(2 * np.pi * (wfrac * 6 + 0.6 * t))
            fr += light(ROSE, argue * (0.46 + 0.12 * wave + 0.15 * jolt) * rose * (1 - 0.6 * warmth * seam))
            fr += light(BLUE, argue * (0.42 + 0.1 * (1 - wave)) * blue * (1 - 0.6 * warmth * seam))
            fr += light(MAUVE, argue * 0.6 * warmth * seam)
            fr += light(WHITE, argue * (1 - warmth) * (0.25 + 0.45 * jolt) * seam ** 4 * (0.6 + 0.4 * tw(t)))

        # the spear: a steel line drawn out from him toward the castle, a step for every note
        if t >= T_SPEAR - 0.1:
            n = int(np.searchsorted(spear, t, side='right'))
            if n > 0:
                grown = (n - 1 + smoothstep(spear[n - 1], spear[n - 1] + 0.25, t)) / len(spear)
                tip = wp + (pf - 60 - wp) * grown
                fade = 1 - smoothstep(T_UNEASE, T_UNEASE + 4, t)
                shaft = smoothstep(wp - 10, wp + 10, d) * smoothstep(tip + 12, tip - 12, d)
                ti = int(np.searchsorted(treaty2, t, side='right')) - 1
                rune = 0.0
                if ti >= 0 and t - treaty2[ti] < 1.5:   # the treaties glinting along it
                    q = wp + (tip - wp) * ((ti * 0.37) % 1)
                    rune = np.exp(-((d - q) / 20) ** 2) * np.exp(-(t - treaty2[ti]) / 0.4)
                hit = np.exp(-(t - spear[n - 1]) / 0.25)
                fr += light(STEEL, fade * (0.75 * shaft + 0.6 * hit * np.exp(-((d - tip) / 18) ** 2)))
                fr += light(WHITE, fade * (0.8 * rune + 0.3 * hit * shaft))
                if t < T_SPEAR + 1.2:
                    fr += light(STEEL, 0.5 * np.exp(-(t - T_SPEAR) / 0.3) * np.ones(G.N) * wing)

        # the two of them
        for k, col in ((WOTAN, BLUE), (FRICKA, ROSE)):
            p = C['pos'][k][f]
            arr = sung[k]
            i = int(np.searchsorted(arr, t, side='right')) - 1
            flare = np.exp(-(t - arr[i]) / 0.25) if i >= 0 and t - arr[i] < 1.2 else 0.0
            b = 0.78 + 0.25 * flare
            fr += light(col, b * np.exp(-((d - p) / (28 + 6 * flare)) ** 2) + 0.35 * b * np.exp(-((d - p) / 130) ** 2))
            fr += light(WHITE, 0.35 * flare * np.exp(-((d - p) / 12) ** 2))
        fr += light(BLUE, 0.32 * (1 - argue) * np.exp(-((d - wp) / 260) ** 2) * wing)
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

    for name, gain, rev in (('strings', 0.16, 0.32), ('low', 0.18, 0.18), ('brass', 0.18, 0.3), ('winds', 0.19, 0.32),
                            ('perc', 0.18, 0.28), ('harp', 0.16, 0.45)):
        M.bus(name, gain=gain, reverb=rev)
    vtrem = M.sampler('Strings/Violin Section/Trem/*.wav', tune=-12)
    vatrem = M.sampler('Strings/Viola Section/trem/*.wav', tune=-12)
    va = M.sampler('Strings/Viola Section/susvib/*.wav', tune=-12)
    vc = M.sampler('Strings/Cello Section/susvib/*.wav', tune=-12)
    vcs = M.sampler('Strings/Cello Section/spic/*.wav', tune=-12)
    cb = M.sampler('Strings/Solo Contrabass/SusNV/*.wav', tune=-12)
    cbs = M.sampler('Strings/Solo Contrabass/Spic/*.wav', tune=-12)
    horn = M.sampler('Brass/F Horn/sus/*.wav', tune=-12)
    tbn = M.sampler('Brass/Tenor Trombone/sus/*.wav', tune=-12)
    tuba = M.sampler('Brass/Tuba/sus/*.wav', tune=-12)
    ob = M.sampler('Woodwinds/Oboe/Vib/*.wav', tune=-12)
    fl = M.sampler('Woodwinds/Flute/susvib/*.wav', tune=-12)
    harp = M.sampler('Strings/Harp/*.wav')
    timp = M.hits('Percussion/Timpani/Timpani1_Hit*.wav')
    crash = M.hits('Percussion/cymbal-crash1_mf*.wav')

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
        if part == 'glow':
            s = horn if m >= note('Ab3') else tuba
            hold('brass', s, m + (12 if m < note('Db2') else 0), t, t + d - 1.5, v, (pl, pf, pr)[m % 3], rise=0.05,
                 fall=1.5, gain=0.5)
        elif part in ('fricka', 'home'):
            pa = pan_of(who, t)
            M.add('winds', ob.play(m, v, dur=d * 1.05, release=0.25), t, 1.0 if part == 'fricka' else 0.8, pa)
            M.add('strings', va.play(m, v - 8, dur=d * 1.05, release=0.35), t, 0.7 if part == 'fricka' else 0.9, pa)
        elif part == 'trem':
            M.add('strings', (vtrem if m >= note('A3') else vatrem).play(m, v, dur=d, release=0.2), t, 0.6,
                  pan_at(at(G, 'Left', 0.2)) if m % 2 else pan_at(at(G, 'Right', 0.8)))
        elif part == 'drive':
            M.add('low', cbs.play(m + 12, v), t, 0.8, -0.2)
            M.add('low', vcs.play(m + 12, v - 10), t, 0.6, 0.1)
        elif part in ('treaty', 'treaty2'):
            pa = pan_of(who, t)
            if m >= note('Gb3'):
                M.add('brass', (tbn if part == 'treaty' else horn).play(m, v, dur=d, release=0.5), t, 0.8, pa + 0.15)
            elif m >= note('Bb2'):
                M.add('brass', tbn.play(m, v, dur=d, release=0.5), t, 0.8, pa)
            else:
                M.add('low', tuba.play(m + 12, v, dur=d, release=0.5), t, 0.8, pa)
                M.add('low', cb.play(m + 12, v - 10, dur=d, release=0.5), t, 0.6, pa)
        elif part == 'hpad':
            hold('strings', va if m >= note('C3') else vc, m, t, t + d, v, 0.0, rise=0.5, fall=0.8, gain=0.5)
        elif part == 'harp':
            M.add('harp', harp.play(m, v), t, 1.0, -0.4 + 0.8 * (m - 55) / 24)
        elif part == 'soft':
            M.add('strings', vc.play(m, v, dur=d * 1.05, release=0.4), t, 0.8, pan_of(who, t))
        elif part == 'shrug':
            M.add('brass', tbn.play(m, v, dur=d, release=0.3), t, 0.8, pan_of(who, t))
        elif part == 'spear':
            pa = pan_of(who, t)
            M.add('brass', tbn.play(m, v, dur=d, release=0.4), t, 1.0, pa)
            M.add('brass', tbn.play(m + 12, v - 10, dur=d, release=0.4), t, 0.6, pa + 0.1)
            M.add('low', tuba.play(m, v - 6, dur=d, release=0.4), t, 0.7, pa)
            M.add('low', cb.play(m, v - 16, dur=d, release=0.4), t, 0.5, pa)
        elif part == 'hit':
            M.add('perc', timp.play(v, pitch=-4), t, 1.0, pan_of(WOTAN, t))
            M.add('perc', crash.play(v), t, 0.7, 0.0)
        elif part == 'uneasy':
            hold('strings', vatrem, m, t, t + d, v, {50: -0.3, 53: 0.0, 57: 0.3}.get(m, 0.0), rise=2.0, fall=1.2,
                 gain=0.9)
        elif part == 'pedal':
            hold('low', cb, m + 12, t, t + d, v, 0.0, rise=1.5, fall=1.5, gain=0.8)
        elif part == 'distant':
            M.add('winds', fl.play(m, v, dur=d * 1.05, release=0.3), t, 0.6, 0.85)
