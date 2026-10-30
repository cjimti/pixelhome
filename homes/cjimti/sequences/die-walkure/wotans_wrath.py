"""Wotan's Wrath: the storm that gathered at the free end of Right comes on. A roaring blue-black thunderhead
churns in along the Right wing, over the rock and on across the Left wing and Side until it holds the whole
house, its leading edge a seething band of deep blue, lightning forking through it on the music's hardest
accents.

The music is Wagner's own: Act III, bars 568 to 624, as Solti's 1958 Vienna Philharmonic recording takes it, from
Wotan's voice in the storm ("Steh! Brünnhild'!") through the sisters hiding her ("Hieher, Verlorne!"), their
terror as he leaps from his horse and the storm climbs to its height, to his arrival ("Wo ist Brünnhild', wo die
Verbrecherin?") and the sisters' plea ("Schrecklich ertost dein Toben!"), stopping just before he answers. The
notes come from the Wagner Ring Dataset's piano reduction (pixelhome/ring.py): its bass races in cellos, basses
and tuba, the left hand's chords groan in trombones and horns, and the right hand's cries are violins with piccolo
on top, softened to violins and horns for the sisters' plea. The stage is heard too: the storm's wind howls
throughout, each bolt of lightning has its thunder, nearer and sooner as he comes, the surges racing in from the
storm whoosh past, the sisters' hooves clatter as they rush together, Wotan's horse gallops in from the right and
he lands with a thunderclap and a great boom. The storm leads, swelling to its height as he arrives; it eases
while the sisters huddle and backs well off for their plea.

His distant cry is a flash of blue at the storm's front. On "Hieher!" the terrified sisters rush together on
Porch Front and close round her, a huddled, trembling knot of eight colours with her silver dimmed at its
heart, each flaring on the cries above them. Then, on the storm's last great chord, a stroke of lightning
across the whole house and Wotan is there, rising out of the left of the rock in deep blue, his spear a steel
line beside him; every word he sings a surge of blue rolling out over the knot, every word that names her a
crack of thunder so that the silver inside it flickers. The sisters plead, their colours swelling on each
phrase, while the storm holds, roaring.

compose() tags every note of the excerpt, choreography() every position; render() and score() read both."""
import numpy as np
from pixelhome.fx import DT, hexc, light, smoothstep, nframes, Flicker
from pixelhome.audio import whoosh
from pixelhome.ring import Orchestra, excerpt

CODE = 'WK23'
TITLE = "Wotan's Wrath"
KIND = 'show'
DESCRIPTION = ('Wotan comes in a storm that swallows the whole house. The terrified Valkyries hide Brünnhilde in '
               'the middle of a huddle on their rock, and every time their father calls for her, the thunder '
               'cracks.')
VOICEOVER = ('Here comes the storm, and the god inside it is furious. '
             'Her sisters have hidden her, but they cannot hide her for long.')

EX = excerpt(__file__)                      # Act III, bars 568-624.5, Solti 1958
BAR = {int(m): t for m, t in EX['bars']}
SING = EX['singing']
D = EX['seconds']
T_SWEEP = BAR[576]                          # the thunderhead has the whole house
T_HUDDLE = next(x[0] for x in SING if x[3].startswith('Hieher, Verlorne'))   # the sisters close round her
T_WOTAN = BAR[610]                          # he is there, in a stroke of lightning
T_SOOTHE = next(x[0] for x in SING if x[3].startswith('Schrecklich'))       # the sisters plead
WOTAN = [(x[0], x[1]) for x in SING if x[2] == 'Wotan']
CALLS = [w[0] for w in WOTAN]               # his lines: "Steh! Brünnhild'!", "Wo ist Brünnhild'?", "Wagt ihr ..."
SISTERS = [(x[0], x[1]) for x in SING if x[2] not in ('Wotan', 'Brünnhilde')]
CLOCK = 80.0 * 22

COLS = [hexc(h) for h in ('#ff4040', '#ff9a20', '#f0e040', '#40e070', '#40d0ff', '#6060ff', '#c050ff', '#ff60c0')]
SPOTS = [('Porch Left', 0.25), ('Porch Left', 0.65), ('Porch Front', 0.12), ('Porch Front', 0.37),
         ('Porch Front', 0.63), ('Porch Front', 0.88), ('Porch Right', 0.35), ('Porch Right', 0.75)]
KNOT = ('Porch Front', 0.66)                # where they hide her
RING = [-60, -44, -28, -12, 12, 28, 44, 60]  # each sister's place in the knot, in path order
WHERE = ['Right', 'Left', 'Side', 'Porch Right', 'Right', 'Left', 'Porch Left', 'Side']
SILVER = hexc('#f4f8ff')
GOLD = hexc('#ffd060')
WBLUE = hexc('#1a3cff')
SPEAR = hexc('#c8d8ff')
THUNDER = hexc('#060a24')
CLOUD = hexc('#2a3448')
STORM = hexc('#5a6a8a')
ROCK = hexc('#343c50')
NAVY = hexc('#0c1438')
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


def inside(spans, t):
    return any(a <= t < b for a, b in spans)


def compose():
    """Every note of the excerpt, tagged: (time, seconds, midi, velocity, part, who). The bass below C3 is the storm
    ('storm'), the left hand above it the brass ('brass'), the right hand the cries ('cry' while the sisters sing,
    who = a sister; 'soothe' for their plea; 'high' otherwise). Silent markers (velocity 0): 'thunder' (who = where)
    on the hardest accent of every few seconds, 'word' on his accented chords while Wotan sings, 'call' at each of
    his lines."""
    N = []
    k = 0
    for t, d, m, v, h in EX['notes']:
        if h == 1:
            N.append((t, d, m, v, 'storm' if m < 48 else 'brass', None))
        elif t >= T_SOOTHE:
            N.append((t, d, m, v, 'soothe', None))
        elif inside(SISTERS, t) and m >= 71:
            N.append((t, d, m, v, 'cry', k % 8))
            k += 3
        else:
            N.append((t, d, m, v, 'high', None))
    ons = onsets(EX['notes'])
    j = 0
    w0 = 0.8
    while w0 < D - 2.0:                                                         # lightning on the hardest accents,
        span = 2.2 if T_HUDDLE + 8 <= w0 < T_WOTAN else 4.4                     # faster as he comes
        sel = (ons[:, 0] >= w0) & (ons[:, 0] < w0 + span)
        sel &= np.array([min(abs(x - c) for c in CALLS + [T_WOTAN]) > 1.2 for x in ons[:, 0]])
        if sel.any():
            t = float(ons[sel][np.argmax(ons[sel, 1]), 0])
            N.append((t, 2.0, 26, 0, 'thunder', 'Right' if t < 6 else WHERE[j % len(WHERE)]))
            j += 1
        w0 += span
    med = np.median(ons[:, 1])
    for t, w in ons:
        if t >= T_WOTAN and inside(WOTAN, t) and w > med:
            N.append((float(t), 0.3, 50, 0, 'word', None))
    for c in CALLS:
        N.append((c, 2.5, 26, 0, 'call', None))
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


def tremble(k, tt):
    """A sister shaking in the knot (shared with the next scene)."""
    return 3.5 * np.sin(2 * np.pi * (5.3 * tt + k / 8)) + 2.0 * np.sin(2 * np.pi * (8.1 * tt + k / 3))


def choreography(G):
    """Per frame: the sisters, Brünnhilde, Wotan, and the storm's leading edge (path distance)."""
    F = nframes(D)
    t = np.arange(F) * DT
    L = G.length
    tt = t + CLOCK
    K = at(G, *KNOT)
    pos = np.zeros((8, F))
    for k in range(8):
        go = T_HUDDLE + 0.25 * abs(k - 3.5)
        knot = K + RING[k] + tremble(k, tt)
        w = smoothstep(go, go + 2.2, t)
        pos[k] = sway(G, k, tt) + (knot - sway(G, k, tt)) * w
    B0 = at(G, 'Porch Front', 0.55)
    bpos = B0 + (K - B0) * smoothstep(T_HUDDLE + 0.5, T_HUDDLE + 3.0, t)
    wpos = np.full(F, at(G, 'Porch Front', 0.3))
    front = np.interp(t, (0.0, 4.5, T_SWEEP), (L - 120, at(G, 'Porch Right', 0.2), -120.0))
    return dict(t=t, pos=pos, bpos=bpos, wpos=wpos, front=front)


def rock_bed(d, tt, porch, stone):
    """Act III: storm clouds billowing over the wings and Side, the still, dark rock on the porch (shared by WK19-WK24)."""
    c1 = 0.5 + 0.5 * np.cos(2 * np.pi * (d / 430 - 0.03 * tt))
    c2 = 0.5 + 0.5 * np.cos(2 * np.pi * (d / 160 + 0.055 * tt) + 1)
    billow = 0.6 * c1 + 0.4 * c1 * c2
    wing = 1 - porch
    return (light(CLOUD, (0.38 + 0.62 * billow ** 1.5) * wing) + light(STORM, 0.6 * billow ** 3 * wing)
            + light(NAVY, 0.4 * wing) + light(ROCK, 0.6 * stone * porch) + light(NAVY, 0.4 * porch))


def thunderhead(fr, d, tt, front, amt):
    """Wotan's storm: a blue-black mass rolling in past `front` (path distance), a roaring blue edge (WK22-WK24).
    amt may be per pixel."""
    inside = 1 / (1 + np.exp(-(d - front) / 45))
    churn = (0.5 + 0.5 * np.cos(2 * np.pi * (d / 330 + 0.17 * tt))) * (0.6 + 0.4 * np.cos(2 * np.pi * (d / 140 - 0.29 * tt)))
    edge = np.exp(-((d - front) / 70) ** 2)
    fr = fr * (1 - 0.75 * amt * inside)[:, None]
    return (fr + light(THUNDER, 0.9 * amt * inside) + light(WBLUE, amt * (0.1 + 0.55 * churn ** 2) * inside)
            + light(WBLUE, 0.7 * amt * edge * (0.7 + 0.3 * churn)))


def render(G, seed=23):
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
    seg_d = {s: (G.pd[G.seg[s]].min(), G.pd[G.seg[s]].max()) for s in G.seg}
    K = at(G, *KNOT)
    words = np.array([e[0] for e in N if e[4] in ('word', 'call')])
    calls = np.array([e[0] for e in N if e[4] == 'call'])
    panic = [np.array([e[0] for e in N if e[4] == 'cry' and e[5] == k]) for k in range(8)]
    soothe = np.array(sorted({e[0] for e in N if e[4] == 'soothe'}))
    strikes = sorted([(T_WOTAN, 'all')] + [(e[0], e[5]) for e in N if e[4] == 'thunder'])
    bars = np.array([b for _, b in EX['bars']])
    ons = onsets(EX['notes'])                                                   # the music's loudness, 0..1
    env = np.zeros(F)
    for t0, w in ons:
        f0 = int(t0 / DT)
        n = min(F - f0, nframes(1.5))
        env[f0:f0 + n] += w * np.exp(-np.arange(n) * DT / 0.3)
    env = np.clip(env / np.percentile(env, 95), 0, 1.2)
    fl_ = Flicker(rng, 1, 4.0, 9.0)

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
        pw, pb = C['wpos'][f], C['bpos'][f]

        # the thunderhead: rolling in from the free end of Right until it has the whole house, lighter on the rock
        amt = ((0.45 + 0.4 * smoothstep(0, T_SWEEP, t) + 0.35 * env[f]) * (1 - 0.5 * porch * smoothstep(3.0, 7.0, t)))
        fr = thunderhead(fr, d, tt, C['front'][f], amt)

        # Wotan: rising out of the rock in lightning; every word a surge of blue rolling out over the knot
        wv = smoothstep(T_WOTAN - 0.1, T_WOTAN + 0.4, t)
        if wv > 0:
            wd = last(words, t, 0.3, 1.5)
            wb = wv * (0.85 + 0.25 * wd)
            fr += light(WBLUE, wb * blob(pw, 34 + 8 * wd) + 0.35 * wb * blob(pw, 180))
            fr += light(SPEAR, wv * (0.55 + 0.35 * wd) * smoothstep(pw + 20, pw + 40, d) * smoothstep(pw + 150, pw + 120, d))
            fr += light(WHITE, 0.3 * wd * wv * blob(pw, 10))
            for tw_ in words:
                if tw_ <= t < tw_ + 1.4 and tw_ >= T_WOTAN:
                    age = t - tw_
                    r = 30 + 700 * smoothstep(0, 1.2, age)
                    fr += light(WBLUE, 0.6 * (1 - age / 1.4) * np.exp(-((np.abs(d - pw) - r) / 80) ** 2))
        if CALLS[0] <= t < CALLS[0] + 1.5:                                      # his voice far off in the storm
            age = t - CALLS[0]
            fr += light(WBLUE, 0.9 * np.exp(-age / 0.4) * blob(C['front'][f], 160))
            fr += light(WHITE, 0.5 * np.exp(-age / 0.12) * blob(C['front'][f], 40))
        if T_WOTAN <= t < T_WOTAN + 1.5:                                        # his arrival
            age = t - T_WOTAN
            fr += light(WHITE, 1.0 * np.exp(-age / 0.15) * blob(pw, 60)) + light(FLASH, 0.5 * np.exp(-age / 0.2) * np.ones(G.N))

        # the knot: eight colours closed round her silver, trembling; her silver dimmed, flickering when he calls
        cl = last(calls, t, 0.6, 3.0)
        hide = smoothstep(T_HUDDLE + 0.5, T_HUDDLE + 3.0, t)
        bb = 0.8 - 0.35 * hide - 0.15 * cl * max(0.0, float(fl_(t)[0]))
        fr += light(SILVER, bb * blob(pb, 18 - 9 * hide) + 0.3 * bb * blob(pb, 80 - 50 * hide))
        for kg in range(3):
            q = pb + 18 * np.sin(2 * np.pi * (0.8 * tt + kg / 2))
            fr += light(GOLD, (0.65 - 0.35 * hide) * blob(q, 5))
        sh = last(soothe, t, 0.5, 1.5)
        for k in range(8):
            p = C['pos'][k][f]
            pn = last(panic[k], t, 0.15, 0.6)
            b = 0.66 + 0.04 * hide + 0.3 * pn + 0.1 * sh - 0.15 * cl + 0.25 * env[f]
            fr += light(COLS[k], b * blob(p, 16 - 8 * hide) + (0.35 - 0.2 * hide) * b * blob(p, 75 - 45 * hide))
            fr += light(WHITE, 0.4 * pn * blob(p, 6))
        if hide > 0.5:                                                          # the knot's glow on the rock round it
            fr += light(SILVER * 0.4 + WBLUE * 0.2, 0.2 * hide * blob(K, 90) * (1 - 0.5 * cl))
        ib = int(np.clip(np.searchsorted(bars, t, side='right') - 1, 0, len(bars) - 2))
        sw = (t - bars[ib]) / (bars[ib + 1] - bars[ib])                         # a swell of the storm on every bar
        if wv > 0:
            fr += light(WBLUE, 0.5 * (1 - sw) * np.exp(-((np.abs(d - pw) - 1600 * sw) / 160) ** 2) * (1 - 0.6 * porch))
        else:                                                                   # he is coming: surges race in from the storm
            g = 0.5 + 0.6 * smoothstep(T_HUDDLE, T_WOTAN, t)
            q = L + 100 - (L + 300) * sw
            fr += light(WBLUE, g * (1 - 0.5 * sw) * np.exp(-((d - q) / 140) ** 2) * (1 - 0.6 * porch))
            fr += light(SPEAR, 0.45 * g * (1 - sw) * np.exp(-((d - q) / 40) ** 2) * (1 - porch))
            fr += light(STORM * 0.5 + WBLUE * 0.5, 0.55 * g * env[f] * np.exp(-sw * 4) * (1 - porch))

        # lightning
        for i, (ts, where) in enumerate(strikes):
            age = t - ts
            if not 0 <= age < 1.0:
                continue
            if where == 'all':
                fr += light(WHITE, 0.8 * bolt(age, pw, 0.0, i) + 0.8 * bolt(age, pw, L, i + 1))
                continue
            a, b = seg_d[where]
            mid = 0.5 * (a + b)
            fr += light(WHITE, 0.95 * bolt(age, b if i % 2 else a, mid, i))
            fr += light(FLASH * 0.5 + WBLUE * 0.5, 0.45 * np.exp(-age / 0.2) * blob(mid, 0.7 * (b - a)))
        out[f] = fr
    return np.clip(out, 0, 1)


def score(M, G):
    """Wagner's notes, orchestrated from the piano reduction: the storm in the low strings and tuba, the left hand's
    chords in trombones and horns, the cries in violins and piccolo; thunder on the real accents."""
    order = np.argsort(G.pd)
    xs, ds = G.pos[order, 0], G.pd[order]
    x0, x1 = xs.min(), xs.max()

    def pan_at(dd):
        x = np.interp(dd, ds, xs)
        return float(0.85 * (2 * (x - x0) / (x1 - x0) - 1))

    C = choreography(G)

    def front_pan(t):
        return pan_at(float(np.clip(np.interp(t, C['t'], C['front']), 0, G.length)))

    o = Orchestra(M, level=1.6)
    seg_mid = {s: float(G.pd[G.seg[s]].mean()) for s in G.seg}
    wp = pan_at(at(G, 'Porch Front', 0.3))
    kp = pan_at(at(G, *KNOT))
    grow = lambda t: 0.75 + 0.25 * smoothstep(30.0, T_WOTAN, t)
    for t, d, m, v, part, who in compose():
        pa = front_pan(t) if t < T_SWEEP else (wp if t >= T_WOTAN else 0.0)
        if part == 'storm':
            o.play('cellos', m + 12 if m < 36 else m, t, d, v, pa - 0.15, 0.75)
            o.play('basses', m, t, d, v - 6, pa + 0.15, 0.6)
            if d > 0.4:
                o.play('tuba', m, t, d, v - 8, pa, 0.5 * grow(t))
        elif part == 'brass':
            if d >= 0.3:
                o.play('trombones', m, t, d, v, pa, 0.75 * grow(t))
                o.play('horns', m, t, d, v - 8, -pa, 0.55)
            else:
                o.play('violas' if m >= 60 else 'cellos', m, t, d, v - 6, pa, 0.5)
        elif part == 'cry':
            pc = pan_at(np.interp(t, C['t'], C['pos'][who]))
            o.play('violins', m, t, d, v - 4, pc, 0.55)
            o.play('piccolo' if m >= 83 else 'flutes', m, t, 0.1, v - 12, pc, 0.45)
        elif part == 'high':
            o.play('violins', m, t, d, v - 6, 0.2, 0.55)
            if d >= 0.4:
                o.play('violas', m - 12, t, d, v - 14, -0.2, 0.3)
            if m >= 84:
                o.play('piccolo', m, t, 0.1, v - 14, -0.3, 0.35)
        elif part == 'soothe':
            o.play('violins', m, t, d, v, kp, 0.6)
            if d >= 0.3:
                o.play('horns', m - 12, t, d, v - 10, kp, 0.45)
        elif part == 'thunder':                                         # each bolt's thunder, nearer as he comes
            o.thunder(t, near=0.35 + 0.65 * smoothstep(0.0, T_WOTAN, t), pan=pan_at(seg_mid[who]), gain=0.9)
        elif part == 'call':
            o.hit('timpani roll', t, 100, gain=0.5, pan=pa)
            o.hit('timpani', t, 118, pitch=-6, gain=0.8, pan=pa)
    o.hit('crash', T_WOTAN, 124, gain=0.9, pan=wp, fx=True)                     # he is there
    o.hit('gong', T_WOTAN, 120, gain=0.7, pan=wp, fx=True)
    o.hit('timpani', T_WOTAN, 124, pitch=-5, gain=1.0, pan=wp, fx=True)
    # the stage: the storm howls, the surges race in, the sisters rush together, he gallops in and lands
    o.wind(0.0, D, level=lambda tt: 0.55 + 0.45 * smoothstep(0.0, T_SWEEP, tt), pan=lambda t: 0.5 * front_pan(t))
    bars = [b for _, b in EX['bars']]
    for k, (b0, b1) in enumerate(zip(bars, bars[1:])):
        if T_HUDDLE <= b0 < T_WOTAN - 0.5 and k % 2 == 0:
            o.M.add('fx', whoosh(min(1.4, b1 - b0 + 0.4), 1600, 220, 0.6, seed=k),
                    b0, 0.2 + 0.25 * smoothstep(T_HUDDLE, T_WOTAN, b0), 0.6)
    for k, side in enumerate((-0.7, 0.7, 0.2)):
        o.gallop(T_HUDDLE + 0.1 * k, T_HUDDLE + 2.3, beat=0.3, pan=side, v=90, gain=0.55)
    o.gallop(T_WOTAN - 7.0, T_WOTAN - 0.4, beat=0.4, v=104, gain=1.1,
             pan=lambda t: 0.85 + (wp - 0.85) * smoothstep(T_WOTAN - 7.0, T_WOTAN - 0.4, t))
    o.thunder(T_WOTAN, near=1.0, pan=wp, gain=1.2)
    o.boom(T_WOTAN + 0.05, wp, gain=0.9)
    # the fader: the storm leads, swelling as he arrives; it eases for the sisters' huddle and backs right off
    # for their plea
    o.effects([(0.0, 0), (T_HUDDLE - 1.0, 0), (T_HUDDLE + 1.0, -4), (T_WOTAN - 8.0, -3), (T_WOTAN - 1.0, 2),
               (T_WOTAN + 2.0, 2), (T_WOTAN + 5.0, -6), (T_SOOTHE - 1.0, -6), (T_SOOTHE + 1.0, -12), (D, -12)])
