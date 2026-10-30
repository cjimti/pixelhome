"""Freia's Flight: the meadow is quiet at dawn, the castle gleams across the porch, Wotan (blue) stands
turned away on Left and Fricka (rose) a little apart from him. Then Freia bursts in from the free end of Right,
apple-blossom pink with her golden apples bobbing round her and flecks of leaf green, running for her life in
bursts, stumbling and glancing back, and the castle's walls blush pink as she runs under them, petals falling
behind her. She reaches Fricka and Wotan on "Hilf mir, Schwester!" and shelters between them, Fricka's rose
round her.

The music is Wagner's own, as Solti's 1958 Vienna Philharmonic recording takes it: Freia's flight, from her
motif bursting into the end of Wotan's line through "Hilf mir, Schwester! Schütze mich, Schwäher!" to "Vom
Felsen drüben drohte mir Fasolt" (bars 912-932); then Fricka's "Wo harren meine Brüder" and "Zu Hilfe, Donner!"
over Freia's frightened music, and the giants' motif breaking out as Fasolt and Fafner come in (966-988). The
notes come from the Wagner Ring Dataset's piano reduction (pixelhome/ring.py): Freia's motif on violins and
flute over scrambling violas and cellos, the shelter on violins and flute over the harp, the giants' motif on
trombones, horns and tubas over basses and timpani. The reduction carries the giants' dynamics in one hand
only, so their whole motif is played fortissimo. Far off, before their motif, the giants' tread is heard coming
closer, and every heavy beat of the motif is a stamp on the bass drum.

Far off at the right end of the house something starts stamping: each a dull flash of grey and ochre and a
shudder through the whole roof, coming closer. The giants' motif breaks out and the giants arrive from the free
end of Right, Fasolt in stone grey and Fafner in ochre, two big heavy masses that lurch forward one step for
every stamp, and plant themselves on the Right wing while Freia cowers, trembling, between her sister and Wotan.

compose() holds every note, choreography() every position; render() and score() read both."""
import numpy as np
from pixelhome.fx import DT, hexc, light, smoothstep, nframes, Flicker
from pixelhome.ring import Orchestra, accents, excerpt

CODE = 'RG08'
TITLE = "Freia's Flight"
KIND = 'show'
DESCRIPTION = ('Freia, goddess of youth with her golden apples, runs the whole length of the house to hide '
               'behind her sister. Then the ground starts to shake, and the two giants who built the castle '
               'come stamping in to collect their wages.')
VOICEOVER = ('Here comes Freia, running as fast as she can. Listen to what is following her.')

EX = excerpt(__file__)                      # bars 912-932, 966-988, Solti 1958
BAR = {int(m): t for m, t in EX['bars']}
SEG = [sg['start'] for sg in EX['segments']] + [EX['seconds']]
RUNS = [BAR[912], BAR[915], BAR[921]]       # her motif, breathless, three times
T_SHELTER = BAR[925]                        # "Hilf mir, Schwester!"
T_LOVE = [BAR[928], BAR[931]]               # sheltered, as Fricka holds her
T_FAR = 50.0                                # the first far-off stamps
FAR_STAMPS = [50.0, 51.8, 53.4, 54.8, 56.1, 57.3, 58.4, 59.4, 60.3, 61.1, 61.8, 62.5, 63.2, 63.9, 64.6, 65.3]
T_GIANTS = 66.15                            # their motif, as they come in
T_GIANTS2 = BAR[986]                        # again, louder, planted
D = EX['seconds']
LEVEL = 2.65

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
    """Every footfall: (time, who, strength 0..1). Far off first, then theirs on the heavy beats of their motif."""
    out = [(t, FASOLT, 0.25 + 0.45 * i / len(FAR_STAMPS)) for i, t in enumerate(FAR_STAMPS)]
    beats = sorted({round(n[0], 3) for n in EX['notes'] if n[0] >= T_GIANTS - 0.05 and n[4] == 1 and n[2] <= 43
                    and n[1] >= 0.4})
    for k, t in enumerate(beats):
        out.append((t, (FASOLT, FAFNER)[k % 2], 0.85 if t < T_GIANTS2 else 1.0))
    return sorted(out)


def compose():
    """Every note of the excerpt, tagged: (time, seconds, midi, velocity, part, who). Freia's flight is 'run' (her
    motif, the right hand) over 'chase'; sheltered she is 'love' over Fricka's 'lovepad'; then 'fear' over 'dread',
    and from the giants' entrance everything is 'giants'. 'stamp' marks each footfall."""
    N = []
    for t, d, m, v, h in EX['notes']:
        if t < T_SHELTER:
            N.append((t, d, m, v, 'run' if h == 0 else 'chase', FREIA if h == 0 else None))
        elif t < SEG[1]:
            N.append((t, d, m, v, 'love' if h == 0 else 'lovepad', FREIA if h == 0 else FRICKA))
        elif t < T_GIANTS - 0.05:
            N.append((t, d, m, v, 'fear' if h == 0 else 'dread', FREIA if h == 0 else None))
        else:
            N.append((t, d, m, 113, 'giants', (FASOLT, FAFNER)[int(t >= T_GIANTS2)]))
    for t, who, st in stamps():
        N.append((t, 0.6, 36, int(60 + 64 * st), 'stamp', who))
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
    marks = [(0.0, L + 60), (RUNS[0] + 0.8, L + 40), (RUNS[1] - 0.6, at(G, 'Right', 0.5)),
             (RUNS[1], at(G, 'Right', 0.56)), (RUNS[2] - 0.8, at(G, 'Porch Right', 0.2)),
             (RUNS[2], at(G, 'Porch Right', 0.28)), (T_SHELTER - 2.6, at(G, 'Porch Left', 0.3)),
             (T_SHELTER - 1.2, at(G, 'Left', 0.85)), (T_SHELTER + 0.5, Fy - 15), (T_FAR, Fy - 6), (D, Fy)]
    ts, ds = zip(*marks)
    set_(FREIA, 0, D, np.interp(t, ts, ds), 9.0)
    set_(FREIA, T_FAR, D, Fy + 3 * np.sin(2 * np.pi * t * 2.3), 6.0)            # hiding, trembling
    # the giants: a lurch forward on every one of their own stamps
    for k, home, start in ((FASOLT, at(G, 'Right', 0.55), L + 90), (FAFNER, at(G, 'Right', 0.8), L + 190)):
        mine = [s for s in stamps() if s[1] == k and s[0] >= T_GIANTS - 0.1 and s[0] < T_GIANTS2]
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
    panic = accents([e for e in N if e[4] in ('love', 'fear')], n=1, space=0.9, vmin=80)
    calls = [x[0] for x in EX['singing'] if x[2] == 'Fricka' and x[0] >= SEG[1] - 0.1]
    tw = Flicker(rng, G.N, 0.3, 1.2)
    grass = Flicker(rng, G.N, 0.1, 0.5)
    sp = Flicker(rng, G.N, 3.0, 9.0)
    np_ = 60                                                    # petals she sheds
    pet_t = np.sort(rng.uniform(RUNS[0] + 1.0, T_SHELTER, np_))
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

        # her terror: a pink ripple out from her on every accent of her frightened music
        for tp in panic:
            if tp <= t < tp + 1.3:
                age = t - tp
                r = 30 + 700 * smoothstep(0, 1.3, age)
                ring = np.exp(-((np.abs(d - fy) - r) / 80) ** 2) * (1 - age / 1.3)
                fr += light(PINK, 0.75 * ring) + light(WHITE, 0.25 * ring ** 3)
        # Fricka calling for her brothers: rose streaks racing to the far end of the house
        for tc in calls:
            if tc <= t < tc + 2.0:
                age = t - tc
                q = C['pos'][FRICKA][f] - 900 * smoothstep(0, 1.6, age)
                fr += light(ROSE, 0.9 * np.exp(-((d - q) / 90) ** 2) * (1 - age / 2.0))
                fr += light(WHITE, 0.5 * np.exp(-((d - q) / 25) ** 2) * (1 - age / 2.0))

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
    """Wagner's notes: Freia's flight on violins and flute over scrambling low strings, the giants' motif on brass
    over basses and timpani; the giants' tread on the bass drum, far off at first."""
    order = np.argsort(G.pd)
    xs, ds = G.pos[order, 0], G.pd[order]
    x0, x1 = xs.min(), xs.max()

    def pan_at(dd):
        x = np.interp(dd, ds, xs)
        return float(0.85 * (2 * (x - x0) / (x1 - x0) - 1))

    C = choreography(G)

    def pan_of(who, t):
        return pan_at(min(np.interp(t, C['t'], C['pos'][who]), G.length))

    o = Orchestra(M, level=LEVEL)
    N = compose()
    # the reduction carries the dynamics in one hand: give each note the loudest velocity sounding around it
    tv = np.array([(e[0], e[3]) for e in N if e[4] != 'stamp'])

    def loud(t, v):
        near = tv[np.abs(tv[:, 0] - t) < 0.6, 1]
        return int(max(v, near.max() - 8)) if len(near) else v

    for t, d, m, v, part, who in N:
        if part == 'stamp':
            continue
        v = loud(t, v)
        if part == 'run':                                   # Freia's motif, breathless
            o.play('violins' if m >= 55 else 'violas', m, t, d, v, pan_of(FREIA, t), 0.6)
            if m >= 72:
                o.play('flutes', m, t, d, v - 8, pan_of(FREIA, t), 0.45)
        elif part == 'chase':                               # scrambling under her
            o.play('cellos' if m < 55 else 'violas', m, t, d, v - 2, -0.2, 0.55)
            if m < 45 and d >= 0.3:
                o.play('basses', m - 12 if m >= 40 else m, t, d, v - 8, 0.2, 0.4)
        elif part == 'love':
            o.play('violins', m, t, d, v - 4, pan_of(FREIA, t), 0.55)
            if d >= 0.3 and m >= 67:
                o.play('flutes', m, t, d, v - 12, pan_of(FREIA, t), 0.4)
        elif part == 'lovepad':
            o.play('harp', m, t, d, v, pan_of(FRICKA, t), 0.5)
            o.play('cellos', m, t, max(d, 0.3), v - 10, -0.2, 0.35)
        elif part == 'fear':
            o.play('violins' if m >= 55 else 'violas', m, t, d, v, pan_of(FREIA, t), 0.55)
            if d >= 0.3 and m >= 67:
                o.play('oboes', m, t, d, v - 10, pan_of(FREIA, t), 0.4)
        elif part == 'dread':
            o.play('cellos' if m < 55 else 'violas', m, t, d, v - 4, -0.2, 0.55)
            if m < 45:
                o.play('basses', m - 12 if m >= 40 else m, t, d, v - 8, 0.2, 0.4)
        elif part == 'giants':                              # the giants' strength
            gp = pan_of(who, t)
            if m >= 55:
                o.play('horns', m, t, d, v, gp, 0.65)
                o.play('violins', m, t, d, v - 10, gp, 0.3)
            elif m >= 45:
                o.play('trombones', m, t, d, v, gp, 0.75)
                o.play('horns', m + 12, t, d, v - 10, gp, 0.4)
            else:
                o.play('tuba', m + 12 if m < 33 else m, t, d, v, gp, 0.7)
                o.play('basses', m, t, d, v - 6, gp, 0.55)
    for t, who, st in stamps():                             # their tread: far off, then on their heavy beats
        p = pan_of(who, t)
        if t < T_GIANTS - 0.1:
            o.hit('bass drum', t, int(70 + 50 * st), gain=0.25 + 0.5 * st, pan=0.8)
        else:
            o.hit('bass drum', t, 124, gain=0.7 * st, pan=p)
            o.hit('timpani', t, 112, pitch=-8, gain=0.45 * st, pan=p)
    o.hit('crash', T_GIANTS + 0.2, 110, gain=0.5, pan=0.6)
    o.hit('timpani roll', T_GIANTS - 2.5, 96, pitch=-6, gain=0.4, pan=0.7)
