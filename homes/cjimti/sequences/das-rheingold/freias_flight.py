"""Freia's Flight: the meadow is quiet at dawn, the castle gleams across the porch, Wotan (blue) stands
turned away on Left and Fricka (rose) a little apart from him. Then Freia bursts in from the free end of Right,
apple-blossom pink with her golden apples bobbing round her and flecks of leaf green, running for her life:
her motif (Donington 7), joyful by nature but here breathless, on violins and flute, three times and higher
each time, over scrambling cellos. She streaks the length of the house, stumbling and glancing back, and the
castle's walls blush pink as she runs under them, petals falling behind her.

She reaches Fricka and Wotan and shelters between them. Fricka holds her: Freia in love (6), warm, on violins
and flute over the harp, and their rose and pink glow together over the wing. But far off at the right end of
the house something is stamping: thuds in the bass drum, each a dull flash of grey and ochre and a shudder
through the whole roof, coming closer. The giants' motif (58) breaks out on tubas, trombones and timpani and
the giants arrive from the free end of Right, Fasolt in stone grey and Fafner in ochre, two big heavy masses
that lurch forward one step for every beat. They plant themselves on the Right wing; their motif comes again,
louder, every stamp shaking the house, while Freia cowers, trembling, between her sister and Wotan.

compose() holds every note, choreography() every position; render() and score() read both."""
import numpy as np
from pixelhome.audio import note
from pixelhome.fx import DT, hexc, light, smoothstep, nframes, Flicker
from pixelhome.leitmotifs import MOTIFS, play

CODE = 'RG08'
TITLE = "Freia's Flight"
KIND = 'show'
DESCRIPTION = ('Freia, goddess of youth with her golden apples, runs the whole length of the house to hide '
               'behind her sister. Then the ground starts to shake, and the two giants who built the castle '
               'come stamping in to collect their wages.')
VOICEOVER = ('Here comes Freia, running as fast as she can. Listen to what is following her.')

RUNS = [1.0, 4.0, 7.0]                      # her motif, breathless, three times
RBEAT = 0.36
T_SHELTER = 11.0
T_LOVE = [12.5, 17.0]                       # Freia in love, as Fricka holds her
LBEAT = 0.62
T_FAR = 23.0                                # the first far-off stamps
FAR_STAMPS = [23.0, 25.0, 26.8, 28.4, 29.8, 31.0, 32.0, 32.9, 33.7, 34.4, 35.0]
T_GIANTS = 35.6                             # their motif, as they come in
GBEAT = 0.75
T_GIANTS2 = 48.0                            # again, louder, planted
G2BEAT = 0.8
T_STANDOFF = T_GIANTS2 + 12 * G2BEAT
T_TAIL = 68.0
D = 80.0

WOTAN, FRICKA, FREIA, FASOLT, FAFNER = range(5)
BLUE = hexc('#1a3cff')
ROSE = hexc('#ff9ad0')
PINK = hexc('#ff5a9a')
APPLE = hexc('#ffd040')
LEAF = hexc('#60d020')
GREY = hexc('#8090a0')
OCHRE = hexc('#c07a10')
STONE = hexc('#fff0c0')
DAWN_HI = hexc('#6a5a8a')
GLOW = hexc('#ff9070')
NEAR = hexc('#a05a96')
FAR = hexc('#2638a0')
DUST = hexc('#5a4a30')
WHITE = hexc('#ffffff')


def at(G, seg, u):
    s = G.pd[G.seg[seg]]
    return float(s.min() + u * (s.max() - s.min()))


def stamps():
    """Every footfall: (time, who, strength 0..1). Far off first, then theirs on the giants' beats."""
    out = [(t, FASOLT, 0.25 + 0.45 * i / len(FAR_STAMPS)) for i, t in enumerate(FAR_STAMPS)]
    for k in range(8):
        out.append((T_GIANTS + k * GBEAT, (FASOLT, FAFNER)[k % 2], 0.85))
    for k in range(8):
        out.append((T_GIANTS2 + k * G2BEAT, (FASOLT, FAFNER)[k % 2], 1.0))
    out.append((T_TAIL + 6 * 0.7, FAFNER, 1.0))
    out.append((T_TAIL + 6 * 0.7, FASOLT, 1.0))
    return sorted(out)


def compose():
    """Every note: (time, seconds, midi, velocity, part, who)."""
    N = []

    def add(t, d, m, v, part, who=None):
        N.append((float(t), float(d), note(m) if isinstance(m, str) else int(m), int(v), part, who))

    for m in ('D3', 'F3', 'A3'):                                                # RG07's unease, cut off by her
        add(0.0, 1.2, m, 66, 'uneasy')
    for k, t0 in enumerate(RUNS):                                               # Freia, running
        tr = (0, 3, 5)[k]
        for t, m, v, d in play('freia', t0, RBEAT, tr, 100 + 6 * k, line='melody'):
            add(t, d, m, v, 'run', FREIA)
        for t, m, v, d in play('freia', t0, RBEAT, tr, 92, line='bass'):
            add(t, d, m, v, 'chase')
        for j in range(16):
            add(t0 + j * RBEAT / 2, RBEAT / 2 * 0.8, note('A2') + tr + (0, 3, 5, 7, 5, 3, 0, -2)[j % 8], 90, 'scramble')
    add(RUNS[0], T_SHELTER - RUNS[0], 'A2', 70, 'trem')
    add(T_SHELTER - 0.4, 0.8, 'D5', 104, 'gasp', FREIA)                        # "help me, sister!"
    add(T_SHELTER + 0.4, 1.0, 'A4', 96, 'gasp', FREIA)
    for k, t0 in enumerate(T_LOVE):                                             # Freia in love; Fricka holds her
        for t, m, v, d in play('freia_love', t0, LBEAT, 0 if k == 0 else -5, 86):
            if m >= note('D4'):
                add(t, d, m, v, 'love', FREIA)
            else:
                add(t, d * 1.1, m, v - 10, 'lovepad', FRICKA)
        for j, m in enumerate(('D3', 'A3', 'D4', 'F#4', 'A4', 'D5')):
            add(t0 + j * 0.18, 1.5, note(m) - 5 * k, 70, 'harp')
    for b, d, n in ((0, 1.5, 'F#4'), (1.5, .5, 'E4'), (2, 1, 'D4'), (3, 1, 'A3'), (4, 2, 'D4'), (6, 1, 'B3'),
                    (7, 1, 'C#4'), (8, 3, 'D4')):                               # Fricka, soothing her
        add(T_LOVE[1] + 4.0 + b * 0.55, d * 0.55, n, 84, 'soothe', FRICKA)
    for m in ('D3', 'A3', 'F#4'):
        add(T_LOVE[1] + 4.0, 5.5, m, 64, 'lovepad', FRICKA)
    add(T_FAR - 1.0, T_GIANTS - T_FAR + 1.0, 'D2', 80, 'dread')
    for m in ('A4', 'Bb4'):
        add(T_FAR + 1.0, T_GIANTS - T_FAR - 1.0, m, 70, 'shiver')
    for t, who, s in stamps():
        add(t, 0.6, 'C2', int(60 + 64 * s), 'stamp', who)
    for k, (t0, gb, vel) in enumerate(((T_GIANTS, GBEAT, 104), (T_GIANTS2, G2BEAT, 116))):
        for t, m, v, d in play('giants', t0, gb, 0, vel):                      # the giants' strength
            add(t, d, m, v, 'giants', (FASOLT, FAFNER)[k])
        for j in range(4):
            for m in ('C2', 'G2'):
                add(t0 + j * 2 * gb, 2 * gb * 1.05, m, vel - 14, 'weight')
    add(T_GIANTS + 12 * GBEAT, T_GIANTS2 - T_GIANTS - 12 * GBEAT, 'C2', 90, 'roll')
    for m in ('C3', 'G3', 'Db4'):
        add(T_GIANTS + 12 * GBEAT - 0.2, T_GIANTS2 - T_GIANTS - 12 * GBEAT, m, 80, 'menace')
    for m in ('C3', 'Eb3', 'G3', 'Db4'):
        add(T_STANDOFF, T_TAIL - T_STANDOFF + 0.5, m, 64, 'menace')
    add(T_STANDOFF, T_TAIL - T_STANDOFF, 'C2', 66, 'roll')
    for b, d, n in ((0, 1.5, 'D4'), (1.5, .5, 'E4'), (2, 1, 'F4'), (3, 1, 'D4'), (4, 2, 'C#4')):
        add(T_STANDOFF + 2.0 + b * 0.6, d * 0.6, n, 76, 'fear', FREIA)          # her tune, in the minor, afraid
    for b, d, n in [x for x in MOTIFS['giants']['notes'] if x[0] >= 8]:         # their tail, a heavy cadence
        add(T_TAIL + (b - 8) * 0.7, d * 0.7 * 1.3, n, 112, 'giants', FAFNER)
    add(T_TAIL + 6 * 0.7, D - T_TAIL - 6 * 0.7, 'C2', 90, 'endchord')
    add(T_TAIL + 6 * 0.7, D - T_TAIL - 6 * 0.7, 'G2', 84, 'endchord')
    add(T_TAIL + 6 * 0.7, D - T_TAIL - 6 * 0.7, 'C3', 80, 'endchord')
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
    """Per frame: where Wotan, Fricka, Freia, Fasolt and Fafner are (path distance)."""
    F = nframes(D)
    t = np.arange(F) * DT
    L = G.length
    tgt = np.zeros((5, F))
    rate = np.full((5, F), 3.0)

    def set_(k, a, b, where, r):
        m = (t >= a) & (t < b)
        tgt[k][m] = where if np.ndim(where) == 0 else where[m]
        rate[k][m] = r

    W, Fr, Fy = at(G, 'Left', 0.75), at(G, 'Left', 0.45), at(G, 'Left', 0.55)
    set_(WOTAN, 0, D, W, 1.2)
    set_(FRICKA, 0, D, Fr, 1.0)
    set_(WOTAN, T_SHELTER, T_FAR, W - 8, 1.5)                                   # turning to her
    set_(FRICKA, T_SHELTER - 1, T_FAR, Fr + 14, 2.0)
    # Freia: a run in bursts, with stumbles and a glance back, from beyond the end of Right to between them
    marks = [(0.0, L + 60), (1.0, L + 40), (3.6, at(G, 'Right', 0.5)), (4.0, at(G, 'Right', 0.56)),
             (6.6, at(G, 'Porch Right', 0.2)), (7.0, at(G, 'Porch Right', 0.28)), (9.4, at(G, 'Porch Left', 0.3)),
             (10.2, at(G, 'Left', 0.85)), (T_SHELTER + 0.5, Fy - 15), (T_FAR, Fy - 6), (D, Fy)]
    ts, ds = zip(*marks)
    set_(FREIA, 0, D, np.interp(t, ts, ds), 9.0)
    set_(FREIA, T_FAR, D, Fy + 3 * np.sin(2 * np.pi * t * 2.3), 6.0)            # hiding, trembling
    # the giants: a lurch forward on every one of their own stamps
    for k, home, start in ((FASOLT, at(G, 'Right', 0.55), L + 90), (FAFNER, at(G, 'Right', 0.8), L + 190)):
        mine = [s for s in stamps() if s[1] == k and s[0] >= T_GIANTS and s[0] < T_GIANTS2]
        set_(k, 0, D, start, 3.0)
        for i, (ts_, _, _) in enumerate(mine):
            set_(k, ts_, D, start + (home - start) * (i + 1) / len(mine), 7.0)
    pos = np.array([follow(tgt[k], rate[k]) for k in range(5)])
    return dict(t=t, pos=pos)


def render(G, seed=8):
    rng = np.random.default_rng(seed)
    F = nframes(D)
    out = np.zeros((F, G.N, 3))
    d = G.pd
    L = G.length
    pf = at(G, 'Porch Front', 0.5)
    C = choreography(G)
    N = compose()
    porch = np.isin(G.seg_of, ['Porch Left', 'Porch Front', 'Porch Right']).astype(float)
    wing = 1 - porch
    p0, p1 = at(G, 'Porch Left', 0.0), at(G, 'Porch Right', 1.0)
    reach = np.maximum(np.abs(d - pf), 1)
    merlon = smoothstep(0.25, 0.55, 0.5 + 0.5 * np.cos(2 * np.pi * (d - pf) / 46))
    stone = 0.88 + 0.12 * np.random.default_rng(6).uniform(-1, 1, G.N)        # the same stones as RG06
    walls = smoothstep(700, 580, reach) * porch
    far = np.clip(np.where(d < p0, p0 - d, np.where(d > p1, d - p1, 0.0)) / 520, 0, 1)
    sky = 0.4 * DAWN_HI[None, :] + 0.6 * (NEAR[None, :] * (1 - far[:, None]) + FAR[None, :] * far[:, None])
    runs = np.array([e[0] for e in N if e[5] == FREIA])
    love = np.array([e[0] for e in N if e[4] == 'love'])
    gnotes = np.array([e[0] for e in N if e[4] == 'giants'])
    steps = stamps()
    tw = Flicker(rng, G.N, 0.3, 1.2)
    grass = Flicker(rng, G.N, 0.1, 0.5)
    sp = Flicker(rng, G.N, 3.0, 9.0)
    np_ = 60                                                    # petals she sheds
    pet_t = np.sort(rng.uniform(RUNS[0] + 0.5, T_SHELTER, np_))
    pet_d = np.interp(pet_t, C['t'], C['pos'][FREIA]) + rng.uniform(-15, 15, np_)
    pet_c = rng.random(np_)

    for f in range(F):
        t = f * DT
        tt = t + 160
        fr = np.zeros((G.N, 3))
        fy = C['pos'][FREIA][f]

        # the meadow at dawn and the castle behind (as RG07 left them)
        roll = 0.5 + 0.5 * np.cos(2 * np.pi * (d / 300 - 0.04 * tt))
        fr += light(sky, 0.34 * (0.85 + 0.1 * roll + 0.05 * grass(t)) * (wing + 0.6 * porch))
        c1 = 0.5 + 0.5 * np.cos(2 * np.pi * (d / 380 - 0.02 * tt))
        c2 = 0.5 + 0.5 * np.cos(2 * np.pi * (d / 170 + 0.035 * tt) + 1)
        cloud = smoothstep(0.35, 1.0, c1 * c2)
        fr += light(DAWN_HI, 0.3 * cloud * wing)
        fr += light(GLOW, (0.12 + 0.16 * cloud) * np.exp(-((d - pf) / 750) ** 2) * (0.9 + 0.1 * roll))
        gleam = 0.5 + 0.5 * np.cos(2 * np.pi * ((d - p0) / 260 - 0.18 * tt))
        blush = np.exp(-((d - fy) / 140) ** 2) * (t < T_SHELTER + 1)
        fr += light(STONE, 0.82 * walls * stone * (0.42 + 0.58 * merlon) * (0.85 + 0.15 * gleam ** 4) * (1 - 0.5 * blush))
        fr += light(PINK, 0.7 * walls * blush * (0.5 + 0.5 * merlon))
        fr += light(WHITE, 0.35 * walls * merlon * gleam ** 12 * (0.7 + 0.3 * tw(t)))

        # the giants coming: a darkening, dusty end of Right that spreads as they arrive
        menace = smoothstep(T_FAR - 2, T_GIANTS, t)
        if menace > 0:
            gp = min(C['pos'][FASOLT][f], C['pos'][FAFNER][f])
            fr *= 1 - 0.4 * menace * smoothstep(gp - 250, gp + 50, d)[:, None]
            fr += light(DUST, 0.3 * menace * smoothstep(gp - 250, gp + 50, d))

        # Freia: pink, running in bursts, her apples bobbing round her, petals falling behind
        here = smoothstep(L + 30, L - 20, fy)
        i = int(np.searchsorted(runs, t, side='right')) - 1
        flare = np.exp(-(t - runs[i]) / 0.15) if i >= 0 and t - runs[i] < 0.8 else 0.0
        li = int(np.searchsorted(love, t, side='right')) - 1
        held = smoothstep(T_SHELTER, T_SHELTER + 2, t) * (1 - smoothstep(T_FAR, T_FAR + 3, t))
        fear = smoothstep(T_FAR, T_GIANTS, t)
        quiver = 1 - 0.3 * fear * (0.5 + 0.5 * np.sin(2 * np.pi * 7 * t))
        b = here * (0.85 + 0.3 * flare - 0.2 * fear) * quiver
        width = 16 + 6 * flare - 4 * fear
        fr += light(PINK, b * np.exp(-((d - fy) / width) ** 2) + 0.35 * b * np.exp(-((d - fy) / 80) ** 2))
        fr += light(WHITE, 0.4 * here * flare * np.exp(-((d - fy) / 10) ** 2))
        if abs(fy - C['pos'][FREIA][max(f - 6, 0)]) > 20:       # a comet of pink behind her as she runs
            trail = np.zeros(G.N)
            for j, lag in enumerate(range(2, 30, 2)):
                q = C['pos'][FREIA][max(f - lag, 0)]
                trail = np.maximum(trail, np.exp(-((d - q) / 26) ** 2) * (1 - j / 14.5))
            fr += light(PINK, 0.75 * here * trail)
        for k in range(3):                                      # the golden apples
            q = fy + (26 - 8 * fear) * np.sin(2 * np.pi * (1.3 * t + k / 3))
            fr += light(APPLE, 0.85 * here * np.exp(-((d - q) / 6) ** 2) * (1 - 0.4 * fear))
        for k in range(2):                                      # and their leaves
            q = fy + 38 * np.sin(2 * np.pi * (0.9 * t + k / 2 + 0.25))
            fr += light(LEAF, 0.6 * here * (1 - 0.6 * fear) * np.exp(-((d - q) / 5) ** 2))
        age = t - pet_t
        on = (age > 0) & (age < 2.5)
        if on.any():
            g = np.exp(-((d[:, None] - pet_d[on][None, :]) / 9) ** 2) * (1 - age[on] / 2.5)[None, :]
            fr += light(WHITE * 0.4 + PINK * 0.6, 0.9 * (g * (pet_c[on] < 0.7)[None, :]).max(axis=1) * (0.6 + 0.4 * sp(t)))
            fr += light(APPLE, 0.6 * (g * (pet_c[on] >= 0.7)[None, :]).max(axis=1))
        if held > 0:                                            # Fricka's rose round her
            lp = np.exp(-(t - love[li]) / 0.4) if li >= 0 and t - love[li] < 2 else 0.0
            fr += light(ROSE, held * (0.3 + 0.2 * lp) * np.exp(-((d - fy) / 110) ** 2))
            fr += light(PINK, held * (0.2 + 0.15 * lp) * np.exp(-((d - fy) / 200) ** 2) * wing)

        # Wotan and Fricka
        for k, col in ((WOTAN, BLUE), (FRICKA, ROSE)):
            p = C['pos'][k][f]
            bb = 0.78 + 0.1 * held * (k == FRICKA)
            fr += light(col, bb * np.exp(-((d - p) / 28) ** 2) + 0.35 * bb * np.exp(-((d - p) / 130) ** 2))
        wp = C['pos'][WOTAN][f]
        fr += light(BLUE, 0.32 * np.exp(-((d - wp) / 260) ** 2) * wing * (1 - 0.5 * held))

        # the giants: big heavy masses, lurching in on their stamps
        gi = int(np.searchsorted(gnotes, t, side='right')) - 1
        gpulse = np.exp(-(t - gnotes[gi]) / 0.3) if gi >= 0 and t - gnotes[gi] < 1.5 else 0.0
        for k, col in ((FASOLT, GREY), (FAFNER, OCHRE)):
            p = C['pos'][k][f]
            vis = smoothstep(L + 60, L - 40, p)
            body = smoothstep(48, 34, np.abs(d - p))
            core = np.exp(-((d - p) / 16) ** 2)
            fr *= 1 - 0.6 * vis * smoothstep(80, 50, np.abs(d - p))[:, None] * (1 - body)[:, None]   # the shadow round them
            fr += light(col, vis * ((0.5 + 0.2 * gpulse) * body + 0.2 * core + 0.18 * np.exp(-((d - p) / 140) ** 2)))
            fr += light(DUST, vis * 0.25 * np.exp(-((d - p) / 200) ** 2))

        # every stamp: a dull flash where it lands, a ripple running out from it, and a shudder through the house
        shudder = 0.0
        for ts, who, s in steps:
            if not ts <= t < ts + 1.6:
                continue
            age = t - ts
            p = np.interp(ts, C['t'], C['pos'][who])
            col = GREY if who == FASOLT else OCHRE
            land = min(p, L - 10)
            fr += light(col, 0.8 * s * np.exp(-age / 0.2) * np.exp(-((d - land) / 240) ** 2))
            r = 1100 * smoothstep(0, 1.4, age)
            fr += light(col, 0.55 * s * np.exp(-((land - d - r) / 110) ** 2) * (1 - age / 1.6) * (d < land))
            shudder = max(shudder, s * np.exp(-age / 0.09))
        fr *= 1 - 0.3 * shudder
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

    def pan_of(who, t):
        return pan_at(min(np.interp(t, C['t'], C['pos'][who]), G.length))

    for name, gain, rev in (('strings', 0.23, 0.3), ('low', 0.3, 0.18), ('brass', 0.3, 0.28), ('winds', 0.23, 0.32),
                            ('perc', 0.28, 0.25), ('harp', 0.2, 0.45)):
        M.bus(name, gain=gain, reverb=rev)
    vn = M.sampler('Strings/Violin Section/susVib/*.wav', tune=-12)
    vtrem = M.sampler('Strings/Violin Section/Trem/*.wav', tune=-12)
    vatrem = M.sampler('Strings/Viola Section/trem/*.wav', tune=-12)
    va = M.sampler('Strings/Viola Section/susvib/*.wav', tune=-12)
    vc = M.sampler('Strings/Cello Section/susvib/*.wav', tune=-12)
    vcs = M.sampler('Strings/Cello Section/spic/*.wav', tune=-12)
    trem = M.sampler('Strings/Cello Section/trem/*.wav', tune=-12)
    cb = M.sampler('Strings/Solo Contrabass/SusNV/*.wav', tune=-12)
    horn = M.sampler('Brass/F Horn/sus/*.wav', tune=-12)
    tbn = M.sampler('Brass/Tenor Trombone/sus/*.wav', tune=-12)
    tuba = M.sampler('Brass/Tuba/sus/*.wav', tune=-12)
    bsn = M.sampler('Woodwinds/Bassoon/sus/*.wav', tune=-12)
    fl = M.sampler('Woodwinds/Flute/susvib/*.wav', tune=-12)
    harp = M.sampler('Strings/Harp/*.wav')
    timp = M.hits('Percussion/Timpani/Timpani1_Hit*.wav')
    roll = M.hits('Percussion/Timpani/Rolls/*.wav')
    bd = M.hits('Percussion/BDrumNewhit_v[3-7]*.wav')
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

    right = pan_at(G.length)
    for t, d, m, v, part, who in compose():
        if part == 'uneasy':
            hold('strings', vatrem, m, t, t + d, v, 0.0, rise=0.05, fall=0.5, gain=0.9)
        elif part == 'run':
            pa = pan_of(who, t)
            M.add('strings', vn.play(m + 12, v, dur=d * 1.05, release=0.12), t, 0.8, pa)
            M.add('winds', fl.play(m + 12, v - 6, dur=d * 1.05, release=0.12), t, 0.8, pa)
        elif part == 'chase':
            M.add('low', vc.play(m + 12, v, dur=d, release=0.15), t, 0.6, pan_of(FREIA, t))
        elif part == 'scramble':
            M.add('low', vcs.play(m, v), t, 0.7, pan_of(FREIA, t))
        elif part == 'trem':
            hold('strings', vtrem, m + 24, t, t + d, v, 0.3, rise=1.5, fall=0.8, gain=0.5)
        elif part == 'gasp':
            M.add('winds', fl.play(m, v, dur=d, release=0.2), t, 1.0, pan_of(who, t))
            M.add('strings', vn.play(m, v - 10, dur=d, release=0.2), t, 0.6, pan_of(who, t))
        elif part == 'love':
            pa = pan_of(FREIA, t)
            M.add('strings', vn.play(m, v, dur=d * 1.05, release=0.4), t, 0.8, pa)
            M.add('winds', fl.play(m, v - 10, dur=d * 1.05, release=0.4), t, 0.6, pa)
        elif part == 'lovepad':
            hold('strings', va if m >= note('C3') else vc, m, t, t + d, v, pan_of(who, t), rise=0.3, fall=0.8, gain=0.5)
        elif part == 'harp':
            M.add('harp', harp.play(m, v), t, 1.0, pan_of(FREIA, t) + 0.3 * (m - 55) / 20)
        elif part == 'dread':
            hold('low', trem, m + 12, t, t + d, v, 0.5, rise=4.0, fall=0.5, gain=1.0)
        elif part == 'shiver':
            hold('strings', vtrem, m, t, t + d, v, -0.2 if m % 2 else 0.2, rise=4.0, fall=0.2, gain=0.6)
        elif part == 'soothe':
            M.add('strings', va.play(m, v, dur=d * 1.05, release=0.35), t, 0.9, pan_of(who, t))
        elif part == 'stamp':
            pa = pan_of(who, t) if t >= T_GIANTS else right
            M.add('perc', bd.play(v), t, 1.0, pa)
            M.add('perc', timp.play(v, pitch=-5), t, 0.7, pa)
            if v > 110:
                M.add('low', tuba.play(note('C2'), v - 20, dur=0.4, release=0.2), t, 0.5, pa)
        elif part == 'giants':
            pa = pan_of(who, t)
            M.add('brass', tbn.play(m, v, dur=d, release=0.3), t, 0.9, pa)
            M.add('low', tuba.play(m - 12, v, dur=d, release=0.3), t, 0.9, pa)
            M.add('low', bsn.play(m - 12, v - 10, dur=d, release=0.3), t, 0.5, pa)
            if v > 110:
                M.add('brass', horn.play(m, v - 12, dur=d, release=0.3), t, 0.5, pa)
        elif part == 'weight':
            hold('low', cb, m + 12, t, t + d, v, right * 0.8, rise=0.1, fall=0.4, gain=0.6)
        elif part == 'menace':
            s = horn if m >= note('G3') else tbn
            hold('brass', s, m, t, t + d, v, 0.6 if m % 2 else 0.3, rise=2.0, fall=1.0, gain=0.8)
        elif part == 'roll':
            M.add('perc', roll.play(v, dur=d), t, 0.6, right * 0.7)
        elif part == 'fear':
            M.add('winds', fl.play(m, v, dur=d * 1.05, release=0.3), t, 0.9, pan_of(who, t))
        elif part == 'endchord':
            s = tuba if m < note('G2') else tbn
            hold('brass', s, m + (12 if m < note('C2') else 0), t, t + d - 1.0, v, right * 0.7, rise=0.05, fall=1.0,
                 gain=0.6)
            if m == note('C2'):
                M.add('perc', crash.play(96), t, 0.6, right * 0.7)
