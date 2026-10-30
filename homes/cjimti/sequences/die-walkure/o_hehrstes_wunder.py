"""O hehrstes Wunder!: on the summit of the rock, in the middle of Porch Front, Brünnhilde stands silver with
gold glints beside Sieglinde's amber, which is sunk low and wrapped in indigo: she wants only to die. The
sisters, too afraid of Wotan to help, have shrunk away to the edges of the rock, shivering.

The music is Wagner's own: Act III, bars 494 to 510 and 526 to 566, as Solti's 1958 Vienna Philharmonic
recording takes them. Brünnhilde tells her she carries "den hehrsten Helden der Welt", the greatest hero in
the world, and Siegfried's motif is heard for the first time; she gives her the pieces of the sword and names
the child ("Siegfried erfreu' sich des Siegs!"); Sieglinde sings "O hehrstes Wunder!", thanks her, says
farewell ("Lebe wohl!") and flees, and the orchestra sweeps her away. The notes come from the Wagner Ring
Dataset's piano reduction (pixelhome/ring.py): the hero's motif on horns and trumpets, Sieglinde's soaring line
on violins doubled by oboe over horns and cellos, the rest on the full orchestra. The stage is heard too: a
shimmer of cymbal and glockenspiel on every ring of gold, the sword's pieces whistling through the air and ringing
as they land, a boom and a cymbal swell under the wonder, Sieglinde's running feet as she flees, and wind and
far-off thunder as Wotan's storm gathers, its first lightning cracking nearer. The effects lead as the shards fly
and again as the storm gathers at the end; they back far off for "O hehrstes Wunder" and her farewell, which
belong to the music.

With the first notes the indigo lifts and a seed of gold-white light pulses inside her amber; every accent of
the hero's motif sends a ring of gold out from her across the whole house. On "Verwahr ihm die starken
Schwertesstücken" the pieces of Nothung fly as white steel glints from the silver into the amber and stay
there, circling. Then "O hehrstes Wunder!": a golden-amber blaze rolls out from her in waves over the whole
house and holds it, brighter on every high note of her melody, until her farewell. She flees east toward the
forest, out along the Left wing and Side with the glints round her; the sisters creep back to their places,
and at the free end of Right a blue-black storm begins to gather and flicker.

compose() tags every note of the excerpt, choreography() every position; render() and score() read both."""
import numpy as np
from pixelhome.fx import DT, hexc, light, smoothstep, nframes, Flicker
from pixelhome.audio import whoosh
from pixelhome.ring import Orchestra, excerpt

CODE = 'WK22'
TITLE = 'O hehrstes Wunder!'
KIND = 'show'
DESCRIPTION = ('Sieglinde wants to die, until Brünnhilde tells her she is carrying Siegmund\'s child, the greatest '
               'hero in the world. Her cry of joy turns the whole house to gold, and she flees into the forest with '
               'the pieces of his father\'s sword.')
VOICEOVER = ('A woman who has lost everything learns that she is going to have a child. '
             'Listen to her answer.')

EX = excerpt(__file__)                      # Act III, bars 494-510 and 526-566, Solti 1958
BAR = {int(m): t for m, t in EX['bars']}
SING = EX['singing']
D = EX['seconds']
line = lambda w: next(x for x in SING if x[3].startswith(w))
SON = [(line('den hehrsten')[0] - 0.6, line('hegst du')[1]),       # Siegfried's motif: the son she carries
       (line('Siegfried')[0], line('Siegfried')[1])]
T_SHARDS = line('Verwahr')[0] - 2.0         # the pieces of Nothung
T_WUNDER = line('O hehrstes')[0]            # "O hehrstes Wunder!"
T_FAREWELL = line('Lebe wohl')[0]
T_FLEE = BAR[561]                           # Sieglinde flees east
T_GONE = T_FLEE + 7.0
T_STORM = BAR[564]                          # Wotan's storm gathering at the free end of Right
CLOCK = 80.0 * 21

NAMES = ['Gerhilde', 'Ortlinde', 'Waltraute', 'Schwertleite', 'Helmwige', 'Siegrune', 'Grimgerde', 'Rossweisse']
COLS = [hexc(h) for h in ('#ff4040', '#ff9a20', '#f0e040', '#40e070', '#40d0ff', '#6060ff', '#c050ff', '#ff60c0')]
SPOTS = [('Porch Left', 0.25), ('Porch Left', 0.65), ('Porch Front', 0.12), ('Porch Front', 0.37),
         ('Porch Front', 0.63), ('Porch Front', 0.88), ('Porch Right', 0.35), ('Porch Right', 0.75)]
BACK = [('Porch Left', 0.12), ('Porch Left', 0.45), ('Porch Left', 0.8), ('Porch Front', 0.13),
        ('Porch Front', 0.9), ('Porch Right', 0.2), ('Porch Right', 0.55), ('Porch Right', 0.85)]
SILVER = hexc('#f4f8ff')
GOLD = hexc('#ffd060')
AMBER = hexc('#ffa860')
BLAZE = hexc('#ffb030')
STEEL = hexc('#e8f8ff')
FATE = hexc('#2a1a5a')
WBLUE = hexc('#1a3cff')
THUNDER = hexc('#060a24')
CLOUD = hexc('#2a3448')
STORM = hexc('#5a6a8a')
ROCK = hexc('#343c50')
NAVY = hexc('#0c1438')
PALE = hexc('#a0b0c0')
FLASH = hexc('#e0e8ff')
WHITE = hexc('#ffffff')


def at(G, seg, u):
    s = G.pd[G.seg[seg]]
    return float(s.min() + u * (s.max() - s.min()))


def onsets(notes, win=0.06):
    """Chords: (time, weight) where weight is the summed velocity of the notes struck together."""
    out = []
    for t, d, m, v, h in notes:
        if out and t - out[-1][0] < win:
            out[-1][1] += v / 127
        else:
            out.append([t, v / 127])
    return np.array(out)


def bolt_time():
    """The first lightning of Wotan's storm: the hardest accent of the closing bars."""
    ons = onsets(EX['notes'])
    sel = ons[(ons[:, 0] > T_STORM) & (ons[:, 0] < D - 1.2)]
    return float(sel[np.argmax(sel[:, 1]), 0])


def compose():
    """Every note of the excerpt, tagged: (time, seconds, midi, velocity, part, who). Parts: 'son' (the hero's motif,
    the left hand's held notes from C3 to B4 while Brünnhilde tells of him), 'wunder' (the right hand while Sieglinde
    sings), 'flight' (the orchestra sweeping her away), 'note' otherwise. Silent markers (velocity 0): 'ring' on the
    accented chords of the hero's motif, 'shard' as each piece of the sword flies to her."""
    N = []
    for t, d, m, v, h in EX['notes']:
        if any(a <= t < b for a, b in SON) and h == 1 and 48 <= m < 72 and d >= 0.3:
            part = 'son'
        elif T_WUNDER <= t < T_FLEE and h == 0:
            part = 'wunder'
        elif t >= T_FLEE:
            part = 'flight'
        else:
            part = 'note'
        N.append((t, d, m, v, part, 'b' if part == 'son' else 's' if part != 'note' else None))
    ons = onsets(EX['notes'])
    med = np.median(ons[:, 1])
    last = -9.0
    for t, w in ons:
        if any(a <= t < b for a, b in SON) and w > med and t - last > 0.7:
            N.append((float(t), 0.5, 60, 0, 'ring', 's'))
            last = t
    sh = [t for t, w in ons if T_SHARDS <= t < T_SHARDS + 4.0]
    for t in sh[::max(1, len(sh) // 7)][:7]:
        N.append((float(t), 0.5, 60, 0, 'shard', 'b'))
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


def sway(G, k, tt):
    """Where a sister wheels on the rock, in her place (shared with the scenes either side)."""
    return at(G, *SPOTS[k]) + 9 * np.sin(2 * np.pi * (0.31 * tt + k / 8)) + 4 * np.sin(2 * np.pi * (0.73 * tt + k / 3))


def choreography(G):
    """Per frame: the sisters, Brünnhilde and Sieglinde (path distance)."""
    F = nframes(D)
    t = np.arange(F) * DT
    home = np.array([sway(G, k, t + CLOCK) for k in range(8)])
    pos = home.copy()
    for k in range(8):                                                          # shrunk back, then creeping home
        back = at(G, *BACK[k]) + 6 * np.sin(2 * np.pi * (4.0 * t + k))          # shivering
        w = 1 - smoothstep(T_FLEE + 1 + 0.4 * k, T_STORM + 0.4 * k, t)
        pos[k] = home[k] + (back - home[k]) * w
    B = at(G, 'Porch Front', 0.55)
    S = at(G, 'Porch Front', 0.4)
    bpos = np.full(F, B)
    smarks = [(0.0, S), (T_FLEE, S), (T_FLEE + 1.5, at(G, 'Porch Left', 0.6)),
              (T_FLEE + 3.8, at(G, 'Left', 0.4)), (T_GONE, -140.0), (D, -140.0)]
    ts, ds = zip(*smarks)
    spos = follow(np.interp(t, ts, ds), np.full(F, 8.0))
    return dict(t=t, pos=pos, bpos=bpos, spos=spos)


def rock_bed(d, tt, porch, stone):
    """Act III: storm clouds billowing over the wings and Side, the still, dark rock on the porch (shared by WK19-WK24)."""
    c1 = 0.5 + 0.5 * np.cos(2 * np.pi * (d / 430 - 0.03 * tt))
    c2 = 0.5 + 0.5 * np.cos(2 * np.pi * (d / 160 + 0.055 * tt) + 1)
    billow = 0.6 * c1 + 0.4 * c1 * c2
    wing = 1 - porch
    return (light(CLOUD, (0.38 + 0.62 * billow ** 1.5) * wing) + light(STORM, 0.6 * billow ** 3 * wing)
            + light(NAVY, 0.4 * wing) + light(ROCK, 0.6 * stone * porch) + light(NAVY, 0.4 * porch))


def thunderhead(fr, d, tt, front, amt):
    """Wotan's storm: a blue-black mass rolling in past `front` (path distance), a roaring blue edge (WK22-WK24)."""
    if amt <= 0:
        return fr
    inside = 1 / (1 + np.exp(-(d - front) / 45))
    churn = (0.5 + 0.5 * np.cos(2 * np.pi * (d / 330 + 0.17 * tt))) * (0.6 + 0.4 * np.cos(2 * np.pi * (d / 140 - 0.29 * tt)))
    edge = np.exp(-((d - front) / 70) ** 2)
    fr = fr * (1 - 0.75 * amt * inside)[:, None]
    return (fr + light(THUNDER, 0.9 * amt * inside) + light(WBLUE, amt * (0.1 + 0.55 * churn ** 2) * inside)
            + light(WBLUE, 0.7 * amt * edge * (0.7 + 0.3 * churn)))


def render(G, seed=22):
    rng = np.random.default_rng(seed)
    F = nframes(D)
    out = np.zeros((F, G.N, 3))
    d = G.pd
    L = G.length
    C = choreography(G)
    N = compose()
    porch = np.isin(G.seg_of, ['Porch Left', 'Porch Front', 'Porch Right']).astype(float)
    stone = 0.8 + 0.2 * np.interp(d / 18, np.arange(int(L / 18) + 2), np.random.default_rng(30).uniform(-1, 1, int(L / 18) + 2))
    jag = [0.55 + 0.45 * np.random.default_rng(100 + k).random(G.N) for k in range(8)]
    son = np.array(sorted({e[0] for e in N if e[4] == 'son'}))
    rings = [e[0] for e in N if e[4] == 'ring']
    wunder = sorted((e[0], e[2]) for e in N if e[4] == 'wunder' and e[1] >= 0.2)
    wt = np.array([w[0] for w in wunder])
    shard_t = [e[0] for e in N if e[4] == 'shard']
    flight = np.array(sorted({e[0] for e in N if e[4] == 'flight' and e[3] >= 80}))
    tw = Flicker(rng, G.N, 2.0, 6.0)
    sh_off = rng.uniform(-26, 26, len(shard_t))
    sh_ph = rng.uniform(0, 1, len(shard_t))
    T_BOLT = bolt_time()
    ons = onsets(EX['notes'])                                                   # the music's loudness, 0..1
    env = np.zeros(F)
    for t0, w in ons:
        f0 = int(t0 / DT)
        n = min(F - f0, nframes(1.5))
        env[f0:f0 + n] += w * np.exp(-np.arange(n) * DT / 0.4)
    env = np.clip(env / np.percentile(env, 95), 0, 1.2)

    def blob(p, w):
        return np.exp(-((d - p) / w) ** 2)

    def last(arr, t, tau, span=2.0):
        i = int(np.searchsorted(arr, t, side='right')) - 1
        return float(np.exp(-(t - arr[i]) / tau)) if i >= 0 and t - arr[i] < span else 0.0

    def bolt(age, a, b, k):
        """A fork of lightning from a to b: grows in 60 ms, flickers three times, gone in a second."""
        if not 0 <= age < 1.0:
            return np.zeros(G.N)
        reach = a + (b - a) * min(1.0, age / 0.06)
        lo, hi = min(a, reach), max(a, reach)
        fl = sum(np.exp(-((age - s) / 0.04) ** 2) for s in (0.0, 0.12, 0.3)) + 0.45 * np.exp(-age / 0.3)
        return ((d >= lo) & (d <= hi)) * jag[k % len(jag)] * min(fl, 1.2)

    for f in range(F):
        t = f * DT
        tt = t + CLOCK
        fr = rock_bed(d, tt, porch, stone)
        pb, ps = C['bpos'][f], C['spos'][f]

        # despair: indigo over everything while Sieglinde wants to die, lifting as the hero's motif sounds
        dark = 1 - smoothstep(0.5, SON[0][0] + 4.0, t)
        if dark > 0:
            fr = fr * (1 - 0.35 * dark) + light(FATE, 0.6 * dark * (0.7 + 0.3 * np.cos(2 * np.pi * (d / 400 - 0.05 * tt))))

        # the hero's motif: every accent a ring of gold rolling out from her over the whole house
        for tr in rings:
            if tr <= t < tr + 2.2:
                age = t - tr
                r = 20 + 900 * age ** 0.8
                fr += light(GOLD, 1.0 * (1 - age / 2.2) * np.exp(-((np.abs(d - ps) - r) / 150) ** 2))
                fr += light(WHITE * 0.3 + GOLD * 0.7, 0.5 * (1 - age / 2.2) * np.exp(-((np.abs(d - ps) - r) / 30) ** 2))

        # hope: a warm glow over the clouds, breathing with the music, growing toward the wonder
        hope = smoothstep(SON[0][0], T_WUNDER, t) * (1 - smoothstep(T_WUNDER, T_WUNDER + 3, t))
        fr += light(AMBER * 0.5 + GOLD * 0.5, (0.12 + 0.45 * hope) * (0.35 + 0.65 * env[f]) * (1 - 0.5 * porch)
                    * (1 - dark) * (0.6 + 0.4 * np.cos(2 * np.pi * (d / 300 - 0.2 * tt))))

        # O hehrstes Wunder: golden-amber waves rolling out from her over the whole house, holding at the height
        blaze = smoothstep(T_WUNDER - 0.5, T_WUNDER + 3.0, t) * (1 - smoothstep(T_FAREWELL + 4, T_FLEE + 3, t))
        if blaze > 0:
            i = int(np.searchsorted(wt, t, side='right')) - 1
            hi = (wunder[i][1] - 66) / 15.0 if i >= 0 else 0.0
            wav = 0.5 + 0.5 * np.cos(2 * np.pi * (np.abs(d - ps) / 380 - 0.45 * tt))
            fr = fr * (1 - 0.8 * blaze)
            fr += light(BLAZE, blaze * (0.5 + 0.4 * np.clip(hi, 0, 1)) * (0.6 + 0.4 * wav))
            fr += light(AMBER, blaze * 0.35 * (1 - wav))
            fr += light(GOLD, blaze * 0.6 * wav ** 4 * (0.7 + 0.3 * tw(t)))
            fr += light(WHITE * 0.4 + GOLD * 0.6, 0.45 * blaze * last(wt, t, 0.3) * blob(ps, 200))

        # at the end Wotan's storm begins to gather at the free end of Right
        amt = 0.6 * smoothstep(T_STORM - 1, D - 1.0, t)
        fr = thunderhead(fr, d, tt, L - 60 - 60 * smoothstep(T_STORM - 1, D - 1.0, t), amt)
        if T_BOLT <= t < T_BOLT + 1.0:
            fr += light(WHITE, 0.8 * bolt(t - T_BOLT, L, L - 260, 3))

        # the sisters: shrunk back and shivering, a little braver in the blaze; home again at the end
        for k in range(8):
            p = C['pos'][k][f]
            fear = (1 - 0.6 * blaze) * (1 - smoothstep(T_FLEE + 1, T_STORM, t)) + 0.3 * smoothstep(T_STORM - 1, D - 1, t)
            b = 0.85 - 0.3 * fear + 0.15 * blaze
            fr += light(COLS[k], b * blob(p, 16) + 0.35 * b * blob(p, 75))

        # Brünnhilde on the summit, flaring as she sings of the hero
        sn = last(son, t, 0.3, 1.5)
        bb = 0.8 + 0.25 * sn
        fr += light(SILVER, bb * blob(pb, 18) + 0.3 * bb * blob(pb, 80))
        for kg in range(3):
            q = pb + 18 * np.sin(2 * np.pi * (0.8 * tt + kg / 2))
            fr += light(GOLD, 0.65 * blob(q, 5))

        # Sieglinde: sunk toward death; the child; the wonder; fleeing with the shards
        sv = smoothstep(-120, 20, ps)
        seed_ = smoothstep(SON[0][0], SON[0][0] + 0.4, t)
        sb = sv * (0.6 - 0.3 * dark + 0.35 * blaze + 0.15 * seed_)
        sb *= 1 - 0.35 * dark * max(0.0, np.sin(2 * np.pi * 1.3 * t)) ** 4
        fr += light(AMBER, sb * blob(ps, 15 + 3 * blaze) + 0.35 * sb * blob(ps, 70))
        if seed_ > 0:                                                           # the child: a gold-white seed in her light
            sr = max(last(son, t, 0.25, 1.0), 0.8 * max((last(np.array([r]), t, 0.3, 1.0) for r in rings), default=0))
            fr += light(GOLD * 0.6 + WHITE * 0.4, sv * seed_ * (0.4 + 0.5 * sr) * blob(ps, 5 + 3 * sr))
        for j, ts_ in enumerate(shard_t):                                       # the shards: flying from her to Sieglinde
            if ts_ <= t < ts_ + 0.5:
                u = (t - ts_) / 0.5
                q = pb + (ps - pb) * u
                fr += light(STEEL, 0.9 * blob(q, 7)) + light(WHITE, 0.5 * blob(q, 3))
                fr += light(WHITE, 0.4 * (1 - u) * blob(pb, 40))
                fr += light(STEEL, 0.5 * (1 - u) * porch * (0.6 + 0.4 * jag[j % 8]))
            elif t >= ts_ + 0.5:
                q = ps + sh_off[j] * np.sin(2 * np.pi * (0.6 * tt + sh_ph[j]))
                fr += light(STEEL, 0.6 * sv * blob(q, 4) * (0.7 + 0.3 * np.sin(2 * np.pi * (2.1 * tt + sh_ph[j]))))
        if T_FLEE <= t:                                                         # her flight, a gust on every accent
            fl = last(flight, t, 0.25, 1.0)
            if abs(ps - C['spos'][max(f - 4, 0)]) > 4:
                trail = np.zeros(G.N)
                for j, lag in enumerate(range(2, 26, 2)):
                    trail = np.maximum(trail, blob(C['spos'][max(f - lag, 0)], 20) * (1 - j / 12.5))
                fr += light(AMBER, 0.8 * sv * trail + 0.25 * sv * blob(ps, 150))
            fr += light(AMBER * 0.6 + GOLD * 0.4, 0.4 * fl * (1 - porch) * smoothstep(T_GONE + 2, T_FLEE, t))
        out[f] = fr
    return np.clip(out, 0, 1)


def score(M, G):
    """Wagner's notes, orchestrated from the piano reduction: the hero's motif on horns and trumpets, Sieglinde's
    melody on violins and oboe over horns and cellos, the rest on the full orchestra."""
    order = np.argsort(G.pd)
    xs, ds = G.pos[order, 0], G.pd[order]
    x0, x1 = xs.min(), xs.max()

    def pan_at(dd):
        x = np.interp(dd, ds, xs)
        return float(0.85 * (2 * (x - x0) / (x1 - x0) - 1))

    C = choreography(G)
    ps = lambda t: pan_at(float(np.clip(np.interp(t, C['t'], C['spos']), 0, G.length)))
    o = Orchestra(M, level=LEVEL)

    def role(t, d, m, v, h):
        if any(a <= t < b for a, b in SON) and h == 1 and 48 <= m < 72 and d >= 0.3:
            parts = [('horns', 0, 4, 0.9), ('horns', -12, -6, 0.4)]
            return parts + ([('trumpets', 0, -10, 0.45)] if v >= 80 else [])
        if T_WUNDER <= t < T_FLEE:
            if h == 0:
                parts = [('violins', 0, 0, 0.75), ('violins', 0, -6, 0.45)]
                if d >= 0.3:
                    parts += [('oboes', 0, -8, 0.6)] if m < 84 else [('flutes', 0, -10, 0.5)]
                return parts
            if m >= 54 and d >= 0.3:
                return [('horns', 0, -4, 0.6), ('cellos', -12 if m >= 60 else 0, -8, 0.5)]
        return None

    o.tutti(EX['notes'], size=lambda t: 0.45 + 0.55 * smoothstep(T_WUNDER - 3, T_WUNDER + 2, t),
            role=role, pan=lambda t, m: ps(t) if t >= T_FLEE else None)
    o.hit('crash', T_WUNDER, 100, gain=0.5, pan=ps(T_WUNDER))
    o.hit('timpani roll', T_WUNDER - 2.0, 90, gain=0.4)
    o.hit('timpani roll', T_STORM, 84, gain=0.5, pan=0.8)
    o.hit('bass drum', bolt_time(), 96, gain=0.6, pan=0.85, fx=True)
    o.hit('timpani', bolt_time(), 96, pitch=-9, gain=0.6, pan=0.85, fx=True)
    # the stage: what the lights show, heard
    N = compose()
    pb = pan_at(C['bpos'][0])
    for tr in [e[0] for e in N if e[4] == 'ring']:                             # each ring of gold: a shimmer
        o.hit('crash', tr, 70, gain=0.22, pan=ps(tr), fx=True)
        o.play('glock', 84, tr, 0.3, 70, ps(tr), 0.25)
    for k, ts_ in enumerate(e[0] for e in N if e[4] == 'shard'):               # the shards ring as they fly to her
        o.hit('metal', ts_ + 0.45, 96, gain=0.45, pan=ps(ts_), fx=True)
        o.play('glock', [88, 91, 86, 93, 89, 84, 95][k % 7], ts_ + 0.45, 0.5, 92, ps(ts_), 0.4)
        o.M.add('fx', whoosh(0.5, 2500, 7000, 0.5, seed=k + 1), ts_, 0.35, pb)
    o.hit('cymbal swell', T_WUNDER - 2.5, 90, gain=0.3, pan=ps(T_WUNDER))   # the wonder: the music's own
    o.gallop(T_FLEE + 0.3, T_GONE + 1.0, beat=0.36, pan=ps, v=92, gain=0.9)   # she runs for the forest
    o.wind(T_STORM - 2.0, D, level=lambda tt: smoothstep(T_STORM - 2.0, D - 1.0, tt), pan=0.75)
    o.thunder(T_STORM, near=0.15, pan=0.85, gain=0.8)                          # far off, the storm gathers
    o.thunder(bolt_time(), near=0.6, pan=0.85, gain=1.0)                       # and its first lightning
    # the fader: the shards lead; the wonder and her farewell are the music's alone; the storm leads at the end
    o.effects([(0.0, -4), (T_SHARDS - 1.0, -4), (T_SHARDS, 0), (T_SHARDS + 4.5, 0), (T_WUNDER - 3.0, -14),
               (T_FAREWELL + 3.0, -14), (T_FLEE, -5), (T_STORM - 1.0, -3), (T_STORM + 2.0, 0), (D, 2)])


LEVEL = 1.75
