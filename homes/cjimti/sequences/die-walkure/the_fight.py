"""The Fight: storm clouds hang over the pass, dark grey with grey-blue banks driving along the roofline, and
Sieglinde sleeps on Left. Siegmund hears Hunding's call: "Der dort mich ruft", and he strides up from Left onto
Porch Front, Nothung's white steel at his side. "Nothung zahl' ihm den Zoll!": the sword's fanfare blazes out in
C major and every chord of it is a white flare of the blade thrown out over the porch. Then the storm breaks:
thunder rolls up the whole roofline in a long crescendo and lightning cracks over the house. Sieglinde cries out
in her sleep, "Siegmund! Siegmund!", and the sky tears open again and again. Out of it, from the free end of
Right, Hunding calls, "Wehwalt! Wehwalt!", a red flash for each, and comes on, blood red in a pool of black,
along Right and up onto the porch. They meet on the heights and fight: at every blow of the orchestra the two
lights lunge together and a blue-white spark bursts where they meet. High over Porch Right a silver glint has
begun to circle, and a red glow smoulders in the storm over Side: a goddess on one side, her father on the other.

The music is Wagner's own: Act II, scene 5, bars 1892 to 1915 (Siegmund's call to Nothung, the sword's fanfare and
the storm breaking) and bars 1936 to 1959 (Sieglinde's dream, the storm at its height, Hunding's challenge and the
fight on the heights), spliced, as Solti's 1958 Vienna Philharmonic recording takes them. The notes come from the
Wagner Ring Dataset's piano reduction of the score (pixelhome/ring.py): the sword's fanfare on trumpets, Hunding's
calls on horns and trombones, the tremolos of the storm on tremolo strings, and the rest on the full orchestra. Over
the score, as a staging would: his footsteps and the blade scraping out, a ring of steel on every chord of the
fanfare, wind over the pass and thunder with every bolt, where it strikes, a thud and gong with each of Hunding's
calls and his heavy tread, steel on steel at every blow of the fight, and triangles and a gong scrape for the glint
of the goddess and the glow of her father. The effects back off for the sword's fanfare, then the storm leads; they
recede for Sieglinde's dream and Hunding's horn calls, and the clashes lead the fight.

compose() tags every note of the excerpt, choreography() every position; render() and score() read both."""
import numpy as np
from pixelhome.fx import DT, hexc, light, smoothstep, nframes, Flicker
from pixelhome.ring import Orchestra, excerpt

CODE = 'WK18'
TITLE = 'The Fight'
KIND = 'show'
DESCRIPTION = ('In a storm on the mountain pass, Siegmund calls on his sword and Hunding answers out of the '
               'thunder, and the two men rush at each other and fight on the heights.')
VOICEOVER = ('Thunder, horns, and two men with swords on a mountain top. '
             'One of them has a goddess on his side. The other has her father.')

EX = excerpt(__file__)                      # Act II, bars 1892-1915 + 1936-1959, Solti 1958
BAR = {int(m): t for m, t in EX['bars']}
D = EX['seconds']
T_STRIDE = BAR[1893]                        # "Der dort mich ruft": he strides up onto the porch
T_SWORD = BAR[1898]                         # "Nothung zahl' ihm den Zoll!": the sword's fanfare
T_STORM = BAR[1905]                         # the storm breaks
T_BURST = BAR[1913]
T_DREAM = BAR[1936]                         # Sieglinde: "Siegmund! Siegmund!"
T_HIGH = BAR[1943]                          # the storm at its height
HORNS = [BAR[1946], BAR[1947]]              # Hunding: "Wehwalt! Wehwalt!"
T_MEET = BAR[1950]                          # they meet on the heights
T_OMEN = BAR[1955]                          # a silver glint, a red glow
K = 17
GLINTS = (-24, -9, 10, 23)

SLATE = hexc('#3a3a4a')
DAWN = hexc('#ff9a5a')
DAWNHI = hexc('#ffc890')
STORM = hexc('#5a6a8a')
STORMDARK = hexc('#2a2e38')
BOLT = hexc('#c8d8ff')
WHITE = hexc('#ffffff')
REDGLOW = hexc('#ff2000')
BRUNN = hexc('#f4f8ff')
BGOLD = hexc('#ffd060')
SIEGMUND = hexc('#30a8ff')
SIEGLINDE = hexc('#ffa860')
STEEL = hexc('#e8f8ff')
HILT = hexc('#ffcc40')
HUNDC = hexc('#8a0020')
HSPEAR = hexc('#a07070')


def at(G, seg, u):
    """Path distance u of the way along a segment."""
    s = G.pd[G.seg[seg]]
    return float(s.min() + u * (s.max() - s.min()))


def pass_bed(G):
    """The rocky pass at dawn: slate ridges on the wings and Side, warm light on the porch heights.
    Returns f(T, wings, porch) -> (N,3), T on the shared clock."""
    d, z = G.pd, G.pos[:, 2]
    porch = np.isin(G.seg_of, ['Porch Left', 'Porch Front', 'Porch Right'])
    ridge = 0.5 + 0.5 * np.cos(2 * np.pi * (d / 170 + 0.35 * np.sin(d / 430)))
    crag = 0.5 + 0.5 * np.cos(2 * np.pi * d / 61 + 2.0 * np.sin(d / 97))
    height = 0.55 + 0.45 * smoothstep(-160, -560, z)

    def f(T, wings=1.0, porch_lvl=1.0):
        cloud = 0.85 + 0.15 * np.cos(2 * np.pi * (d / 900 - T / 40))
        sl = (0.62 + 0.22 * ridge + 0.1 * crag) * cloud * ~porch * wings
        glow = 0.5 + 0.5 * np.cos(2 * np.pi * (d / 300 - T / 25))
        dw = (0.44 + 0.08 * glow) * height * porch * porch_lvl
        return light(SLATE, sl) + light(DAWN, dw) + light(DAWNHI, 0.2 * glow * height * porch * porch_lvl)
    return f


def storm_bed(G):
    """Storm clouds over the pass: dark grey with grey-blue cloud banks rolling along. f(T, level) -> (N,3)."""
    d = G.pd

    def f(T, lvl=1.0):
        c1 = 0.5 + 0.5 * np.cos(2 * np.pi * (d / 520 - T / 9))
        c2 = 0.5 + 0.5 * np.cos(2 * np.pi * (d / 230 + T / 13) + 1.3)
        return light(STORMDARK, lvl * 0.45) + light(STORM, lvl * (0.1 + 0.42 * c1 ** 2 * (0.5 + 0.5 * c2)))
    return f


def tremolos(notes, gap=0.09, short=0.12, least=3):
    """Merge the piano reduction's repeated-note tremolos (the same note struck again and again, each shorter than
    `short`) into single long notes: [t, d, midi, vel, hand, n] with n the number of strokes merged."""
    out, runs = [], {}
    for t, d, m, v, h in sorted(notes):
        r = runs.get((h, m))
        if r and d < short and r[1] < short * r[5] and t - (r[0] + r[1]) < gap:
            r[1] = t + d - r[0]
            r[3] = max(r[3], v)
            r[5] += 1
            continue
        r = [t, d, m, v, h, 1]
        runs[(h, m)] = r
        out.append(r)
    return [r if r[5] >= least or r[5] == 1 else r for r in out]


def compose():
    """Every note of the excerpt (tremolos merged), tagged: (time, seconds, midi, velocity, part, hand). Parts:
    'trem' a merged tremolo; 'sword' the sword's motif in the left hand under the fanfare; 'call' Hunding's calls; otherwise
    'note'."""
    N = []
    for t, d, m, v, h, n in tremolos(EX['notes']):
        if n >= 3:
            part = 'trem'
        elif BAR[1899] - 0.01 <= t < T_STORM and h == 1 and d >= 0.3 and m >= 48:
            part = 'sword'
        elif HORNS[0] - 0.01 <= t < BAR[1948] and h == 0 and d >= 0.5:
            part = 'call'
        else:
            part = 'note'
        N.append((t, d, m, v, part, h))
    return sorted(N, key=lambda e: e[0])


def accents(N, t0, t1, vmin, n, space):
    """Times in [t0, t1) where n or more notes louder than vmin strike together, at least `space` apart."""
    c = {}
    for e in N:
        if t0 <= e[0] < t1 and e[3] >= vmin:
            c[round(e[0], 2)] = c.get(round(e[0], 2), 0) + 1
    out = []
    for k in sorted(k for k, v in c.items() if v >= n):
        if not out or k - out[-1] >= space:
            out.append(k)
    return out


def events():
    """The lightning, the sword's flares and the clashes, from the music's accents."""
    N = [(t, d, m, v) for t, d, m, v, h in EX['notes']]
    bolts = sorted(set(accents(N, T_STORM, D, 98, 3, 1.0) + [T_BURST, T_HIGH]))
    flares = accents(N, T_SWORD, T_STORM, 80, 2, 0.45)
    clashes = accents(N, T_MEET - 0.5, D - 0.3, 61, 2, 0.7)
    return bolts, flares, clashes


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
    """Per frame: Siegmund and Hunding (path distance); Sieglinde stays on Left."""
    F = nframes(D)
    t = np.arange(F) * DT
    P = lambda s, u: at(G, s, u)
    rend = P('Right', 1.0) + 40
    _, _, clashes = events()

    def track(keys):
        return np.interp(t, [k[0] for k in keys], [k[1] for k in keys])

    sm_t = track([(0, P('Left', 0.55)), (T_STRIDE, P('Left', 0.55)), (T_SWORD, P('Porch Left', 0.5)),
                  (T_STORM, P('Porch Front', 0.3)), (T_MEET - 1.0, P('Porch Front', 0.3)),
                  (T_MEET + 1.0, P('Porch Front', 0.4)), (D, P('Porch Front', 0.4))])
    hd_t = track([(0, rend), (HORNS[0] + 0.3, rend), (HORNS[1] + 1.6, P('Right', 0.5)),
                  (T_MEET - 1.0, P('Porch Right', 0.4)), (T_MEET + 1.0, P('Porch Front', 0.62)),
                  (D, P('Porch Front', 0.6))])
    sm = follow(sm_t, np.full(F, 4.0))
    hd = follow(hd_t, np.full(F, 4.0))
    mid = 0.5 * (sm + hd)
    for k, tc in enumerate(clashes):           # each clash: both lunge to the middle and spring back
        a = np.exp(-((t - tc) / 0.12) ** 2)
        sm = sm + (mid - 6 - sm) * a
        hd = hd + (mid + 6 - hd) * a
    return dict(t=t, mund=sm, hund=hd, linde=np.full(F, P('Left', 0.7)))


def render(G, seed=18):
    rng = np.random.default_rng(seed)
    F = nframes(D)
    out = np.zeros((F, G.N, 3))
    d = G.pd
    L = G.length
    porch = np.isin(G.seg_of, ['Porch Left', 'Porch Front', 'Porch Right'])
    bed = pass_bed(G)
    storm = storm_bed(G)
    C = choreography(G)
    N = compose()
    ln = C['linde'][0]
    rend = at(G, 'Right', 1.0)
    side = np.isin(G.seg_of, ['Side'])
    bolts, flares, clashes = events()
    trem = [(e[0], e[0] + e[1], e[3]) for e in N if e[4] == 'trem']
    tw = Flicker(rng, G.N, 2.0, 8.0)
    bolt_at = rng.uniform(0, L, len(bolts))
    bolt_w = rng.uniform(150, 350, len(bolts))
    omen = at(G, 'Porch Right', 0.7)

    def last(on, t):
        i = int(np.searchsorted(on, t, side='right')) - 1
        return t - on[i] if i >= 0 else 99.0

    for f in range(F):
        t = f * DT
        T = t + 80 * K
        s = 0.35 + 0.65 * smoothstep(T_SWORD, T_STORM + 2.0, t)
        fr = bed(T, 1 - s, 1 - s) + storm(T, s)
        sm, hd = C['mund'][f], C['hund'][f]

        # thunder: the storm's tremolos roll a grey-blue swell up the roofline, louder brighter
        roll = max([v / 127 * smoothstep(a, a + 0.6, t) * (1 - smoothstep(b, b + 0.8, t)) for a, b, v in trem
                    if a - 0.1 <= t < b + 0.9] or [0.0])
        if roll > 0:
            wave = 0.5 + 0.5 * np.cos(2 * np.pi * (d / 400 - 1.6 * T))
            fr += light(BOLT, 0.6 * roll * wave * (0.5 + 0.5 * (1 - porch)))

        # lightning on the accents: a double flicker, a bolt along the roofline, a glow on the wings
        for k, tl in enumerate(bolts):
            if tl <= t < tl + 0.8:
                a = np.exp(-(t - tl) / 0.1) + 0.8 * np.exp(-max(t - tl - 0.22, 0) / 0.12) * (t > tl + 0.22)
                big = 1.0 if tl in (T_BURST, T_HIGH) else 0.0
                fr += light(BOLT, a * (0.85 * np.exp(-((d - bolt_at[k]) / bolt_w[k]) ** 2) + (0.4 + 0.35 * big)))
                fr += light(WHITE, 0.7 * a * np.exp(-((d - bolt_at[k]) / 25) ** 2))

        # Hunding's calls: red at the free end of Right
        for k, th in enumerate(HORNS):
            if th <= t < th + 2.5:
                a = np.exp(-(t - th) / 0.6)
                fr += light(HUNDC, 1.2 * a * np.exp(-((d - rend) / (140 + 100 * k)) ** 2))
                fr += light(REDGLOW, 0.5 * a * np.exp(-((d - rend) / 30) ** 2))

        # the sword's fanfare: every chord a white flare of the blade thrown out over the porch
        if T_SWORD - 0.1 <= t < T_STORM + 1.0:
            for tf in [x for x in flares if x <= t < x + 0.9]:
                age = t - tf
                r = 20 + 420 * age
                fr += light(STEEL, 0.75 * np.exp(-age / 0.3) * np.exp(-((np.abs(d - sm) - r) / 45) ** 2))
                fr += light(WHITE, 0.8 * np.exp(-age / 0.12) * np.exp(-((d - sm) / 30) ** 2))

        # the clashes: a blue-white spark where they meet, flung out along the porch
        for tc in clashes:
            if tc <= t < tc + 0.8:
                age = t - tc
                c = np.interp(tc, C['t'], 0.5 * (C['mund'] + C['hund']))
                fr += light(WHITE, 0.95 * np.exp(-age / 0.1) * np.exp(-((d - c) / 14) ** 2))
                r = 30 + 450 * age
                fr += light(SIEGMUND, 0.65 * np.exp(-age / 0.25) * np.exp(-((np.abs(d - c) - r) / 28) ** 2))
                fr += light(HUNDC, 0.5 * np.exp(-age / 0.3) * np.exp(-((np.abs(d - c) - 0.7 * r) / 25) ** 2))
                fr += light(BOLT, 0.3 * np.exp(-age / 0.15) * porch)

        # the battle glow: his blue and Hunding's red pushing at each other over the porch
        war = smoothstep(T_MEET - 1.0, T_MEET + 1.0, t)
        if war > 0:
            c = 0.5 * (sm + hd)
            hit = np.exp(-last(clashes, t) / 0.35)
            reach = np.exp(-((d - c) / 260) ** 2) * (0.35 + 0.35 * hit)
            fr += light(SIEGMUND, war * reach * (d < c))
            fr += light(REDGLOW, 0.8 * war * reach * (d >= c))

        # the omen: a silver glint circling high over Porch Right, a red glow smouldering over Side
        om = smoothstep(T_OMEN, T_OMEN + 3.0, t)
        if om > 0:
            q = omen + 40 * np.sin(2 * np.pi * T / 2.2)
            fr += light(BRUNN, om * 0.8 * np.exp(-((d - q) / 10) ** 2))
            fr += light(BGOLD, om * 0.4 * np.exp(-((d - q - 12) / 6) ** 2))
            fr += light(REDGLOW, om * (0.35 + 0.15 * np.sin(2 * np.pi * T / 2.3)) * side)

        # Hunding: blood red in a pool of black, his spear held up
        on = smoothstep(HORNS[0] - 0.3, HORNS[0] + 0.6, t)
        fr = fr * (1 - 0.75 * on * np.exp(-((d - hd) / 38) ** 2))[:, None]
        fr += light(HUNDC, on * 1.1 * np.exp(-((d - hd) / 15) ** 2))
        hs = smoothstep(hd + 12, hd + 16, d) * smoothstep(hd + 40, hd + 34, d)
        fr += light(HSPEAR, on * 0.45 * hs)

        # Siegmund and Nothung, blazing through the fanfare
        blaze = smoothstep(T_SWORD - 0.5, T_SWORD + 0.5, t) * (1 - smoothstep(T_STORM, T_STORM + 3.0, t))
        fl = np.exp(-last(flares, t) / 0.25) if flares else 0.0
        fr = fr * (1 - 0.5 * np.exp(-((d - sm) / 30) ** 2))[:, None]
        fr += light(SIEGMUND, 0.9 * np.exp(-((d - sm) / 16) ** 2) + 0.25 * np.exp(-((d - sm) / 60) ** 2))
        blade = smoothstep(sm - 34, sm - 30, d) * smoothstep(sm - 12, sm - 16, d)
        fr += light(STEEL, (0.75 + 0.25 * blaze + 0.3 * fl * blaze) * blade * (0.85 + 0.15 * tw(t)))
        fr += light(HILT, 0.7 * np.exp(-((d - sm + 12) / 3.5) ** 2))

        # Sieglinde asleep on Left, starting up at her dream
        dream = np.exp(-max(t - T_DREAM, 0) / 4.0) * (t >= T_DREAM)
        sl = 0.33 + 0.35 * dream
        fr += light(SIEGLINDE, sl * np.exp(-((d - ln) / 15) ** 2) + 0.25 * sl * np.exp(-((d - ln) / 55) ** 2))
        out[f] = fr
    return np.clip(out, 0, 1)


def score(M, G):
    """Wagner's notes: the full orchestra, the sword's fanfare on trumpets, Hunding's calls on horns, the storm's
    tremolos on tremolo strings, timpani and cymbals on the lightning."""
    o = Orchestra(M, level=2.4)
    order = np.argsort(G.pd)
    xs, ds = G.pos[order, 0], G.pd[order]
    x0, x1 = xs.min(), xs.max()

    def pan_at(dd):                         # path distance -> left/right across the facade, from the street
        x = np.interp(dd, ds, xs)
        return float(0.85 * (2 * (x - x0) / (x1 - x0) - 1))

    size = lambda t: 0.55 if t < T_SWORD else 1.0
    plain = []
    for t, d, m, v, part, h in compose():
        if part == 'trem':
            o.play('cellos trem' if m < 55 else 'violins trem', m, t, d, v, gain=0.7)
            if m < 43:
                o.play('basses', m, t, d, v - 10, gain=0.45)
        elif part == 'sword':
            o.play('trumpets', m + 12, t, d, v, gain=0.6)
            o.play('horns', m, t, d, v, gain=0.7)
            o.play('trombones', m - 12, t, d, v - 10, gain=0.45)
        elif part == 'call':
            rp = pan_at(at(G, 'Right', 1.0))
            o.play('horns', m - 12, t, d, v + 10, rp, 0.9)
            o.play('trombones', m - 24, t, d, v, rp, 0.6)
        else:
            plain.append([t, d, m, v, h])
    o.tutti(plain, size=size)
    o.effects([(0.0, -4), (T_SWORD - 0.5, -4), (T_SWORD + 0.3, -9), (T_STORM - 0.8, -9), (T_STORM, 0),
               (T_DREAM - 0.5, 0), (T_DREAM + 0.5, -6), (T_HIGH - 0.5, -6), (T_HIGH, 0), (HORNS[0] - 0.3, -5),
               (HORNS[1] + 1.5, -5), (T_MEET - 0.5, 1), (D, 1)])
    bolts, flares, clashes = events()
    C = choreography(G)
    pt = lambda key: (lambda t: pan_at(np.interp(t, C['t'], C[key])))
    rng = np.random.default_rng(18)                     # the same bolts render() draws, in the same places
    Flicker(rng, G.N, 2.0, 8.0)
    bolt_at = rng.uniform(0, G.length, len(bolts))
    bolt_w = rng.uniform(150, 350, len(bolts))
    tri = M.hits('Percussion/Triangle3-Hit*.wav')
    # he strides up and draws: the blade from its sheath, every chord of the fanfare a ring of steel
    for k in range(int((T_SWORD - T_STRIDE) / 0.75)):
        o.hit('hoof soft', T_STRIDE + 0.75 * k, 70, gain=0.35, pan=pt('mund')(T_STRIDE + 0.75 * k), fx=True)
    o.hit('scrape', T_SWORD - 0.6, 110, gain=0.7, pan=pt('mund')(T_SWORD), fx=True)
    for tf in flares:
        o.hit('metal', tf, 96, gain=0.4, pan=pt('mund')(tf), fx=True)
        o.hit('anvil', tf, 80, gain=0.2, pan=pt('mund')(tf), fx=True)
    # the storm: wind over the pass, thunder with every bolt where it strikes, the big ones right overhead
    o.wind(T_STORM - 3.0, D, level=lambda tt: 0.5 + 0.5 * smoothstep(T_STORM, T_HIGH, tt), pan=0.0)
    o.thunder(T_STORM, near=0.35, pan=-0.5, gain=1.0)
    for k, tl in enumerate(bolts):
        big = tl in (T_BURST, T_HIGH)
        o.thunder(tl, near=1.0 if big else float(np.clip(0.45 + bolt_w[k] / 700, 0, 0.95)),
                  pan=pan_at(bolt_at[k]), gain=1.1 if big else 0.85)
    # Hunding: a low thud and gong with each red flash of his call, then his heavy tread along Right
    for th in HORNS:
        o.hit('bass drum', th, 118, gain=0.6, pan=pt('hund')(th), fx=True)
        o.hit('gong', th, 100, gain=0.35, pan=pt('hund')(th), fx=True)
    t = HORNS[1] + 0.3
    while t < T_MEET - 0.5:
        o.hit('bass drum', t, 100, gain=0.4, pan=pt('hund')(t), fx=True)
        o.hit('hoof', t + 0.02, 80, gain=0.3, pan=pt('hund')(t), fx=True)
        t += 0.62
    # the fight: steel on steel at every blow, where they meet
    for tc in clashes:
        o.clash(tc, pt('mund')(tc) * 0.5 + pt('hund')(tc) * 0.5, 120, 1.1)
        o.hit('timpani', tc, 105, pitch=-1, gain=0.45)
    o.hit('crash', BAR[1903], 120, gain=0.55)
    # the omens: a silver glint circling over Porch Right, a red glow smouldering over Side
    for k in range(10):
        o.M.add('fx', tri.play(70), T_OMEN + 0.55 * k, 0.113, pan_at(at(G, 'Porch Right', 0.7)))
    o.hit('gong scrape', T_OMEN, 100, gain=0.5, pan=pan_at(at(G, 'Side', 0.5)), fx=True)
