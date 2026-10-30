"""Three Riddles: the Wanderer, deep blue on Right, has wagered his head that he can answer any three questions
Mime puts to him, and Mime, yellow at the anvil, asks. Who lives in the depths of the earth? The Nibelungs: the
whole house drops into the red dark of Nibelheim in a wipe out from the Wanderer, and anvils ring in the
Nibelungs' dotted rhythm all over it, every blow a red flash and a spray of red sparks on a different part of the
roofline. Who lives on the face of the earth? The giants: a wipe to stone and ochre, and every stamp of their
motif lights one whole run of the house as a block of stone in turn. Who lives on the cloudy heights? The gods: a
wipe to sky blue, and Valhalla rises in the brass, a chord to a bar, while gold climbs from both ends of the house
to the castle in the middle of Porch Front; then the spear strikes the floor, a blue-white flash, and thunder.

Now the Wanderer asks. Who will forge Nothung anew? The strings tremble, the sword's motif climbs, Mime flickers
in panic, and the Wanderer's blue swells over the whole house until the answer crashes out on the full brass:
"Nur wer das Fürchten nie erfuhr, schmiedet Nothung neu." Mime's head is forfeit to him. The Wanderer goes, a blue
sweep out through the cave mouth, and Mime collapses, shaking, at the anvil.

The music is Wagner's own, six moments of Act I as Solti's 1958 Vienna Philharmonic recording takes them: bars
1440 to 1445 (the Nibelungs), 1498 to 1501 (the giants), 1577 to 1585 (the gods and the spear), 1801 to 1807 (the
question), 1880 to 1884 (the answer) and 1896 to 1903 (his going). The notes come from the Wagner Ring Dataset's
piano reduction (pixelhome/ring.py), orchestrated by hand and register: the Nibelungs' rhythm on cellos and
bassoons, the giants on tubas and basses, Valhalla on trombones and horns, the answer on the full brass. On stage:
anvils ringing on every Nibelung blow, the giants' stamping on drum and timpani, a rushing wipe into each world,
the spear's blow and a soft roll of thunder; the effects stand back under Valhalla and the answer.

compose() holds every note; stage(), cave(), figure() and sparks() are the cave, shared word for word by Act I's
scenes on a clock that runs on from scene to scene."""
import numpy as np
from pixelhome.audio import whoosh
from pixelhome.fx import DT, hexc, light, smoothstep, nframes, keys, Flicker, smooth_noise
from pixelhome.ring import Orchestra, accents, excerpt, tidy

CODE = 'SF07'
TITLE = 'Three Riddles'
KIND = 'show'
DESCRIPTION = ('A wager of heads: the dwarf asks the stranger three riddles, and the house becomes the dark '
               'Nibelung forges, the giants\' land and the gods\' castle in turn. Then the stranger asks the one '
               'question the dwarf cannot answer.')
VOICEOVER = ('Three riddles, and the loser forfeits his head. '
             'The Wanderer answers them all, and then asks his own.')

K = 6                                       # this scene's place on Act I's shared clock: T = t + 80 K
EX = excerpt(__file__)                      # six moments of Act I, Solti 1958
D = EX['seconds']
SEG = [(g['start'], g['start'] + g['seconds']) for g in EX['segments']]
_M = np.array([m for m, _ in EX['bars']], float)
_T = np.array([t for _, t in EX['bars']])


def bt(m):
    """Seconds into the scene of measure position m (bar plus fraction)."""
    return float(np.interp(m, _M, _T))


R = SEG[:3]                                 # the three riddles: Nibelungs, giants, gods
T_STRIKE = bt(1585)                         # the spear strikes the floor
T_Q = SEG[3][0]                             # who will forge Nothung anew?
T_ANSWER = bt(1884)                         # "schmiedet Nothung neu"
T_LEAVE = SEG[5][0]                         # he goes out through the cave mouth
T_GONE = T_LEAVE + 6.0

ROCK = hexc('#3a1608')
EMBER = hexc('#a01a00')
FORGE = hexc('#ff4a08')
HEAT = hexc('#fff0a0')
SPARK = hexc('#ffb020')
FOREST = hexc('#18a020')
GOLD = hexc('#ffaa00')
MIME = hexc('#e0c800')
MIME_DIM = hexc('#6a5a00')
WHITE = hexc('#ffffff')
WOTAN = hexc('#1a3cff')
WOTAN_SOFT = hexc('#5a78ff')
SPEAR = hexc('#c8d8ff')
DEPTHS = hexc('#5a0800')
RED = hexc('#ff1000')
STONE = hexc('#6a5a48')
OCHRE = hexc('#c88a20')
SKY = hexc('#2050ff')
VALHALLA = hexc('#ffb000')

LV = dict(bed=0.28, forge=0.55, walls=0.45, mouth=0.55)     # the cave at every cut in Act I
MIME_AT = 0.32                              # Mime's place on Porch Front, beside the anvil
WAND_AT = 0.4                               # where the Wanderer stands, on Right
RUNS = ['Left', 'Right', 'Porch Left', 'Porch Right', 'Side', 'Porch Front']    # the giants' stamping order

def at(G, seg, u):
    """Path distance u of the way along a segment."""
    s = G.pd[G.seg[seg]]
    return float(s.min() + u * (s.max() - s.min()))


def stage(G):
    """Mime's cave as profiles over the house: the anvil in the middle of Porch Front, the forge fire across Porch
    Front, the chimney walls on Porch Left and Right, rock everywhere else, the mouth at the free end of Right."""
    d = G.pd
    anvil = at(G, 'Porch Front', 0.5)
    rng = np.random.default_rng(1876)       # the same fire and rock in every scene, so the cuts match
    seg = G.seg_of
    return dict(
        d=d, anvil=anvil,
        heat=np.exp(-((d - anvil) / 22) ** 2),
        forge=(seg == 'Porch Front') * (0.55 + 0.45 * np.exp(-((d - anvil) / 120) ** 2)),
        walls=np.isin(seg, ['Porch Left', 'Porch Right']) * (0.35 + 0.65 * smoothstep(
            at(G, 'Porch Left', 0.0), at(G, 'Porch Left', 1.0), d) * (1 - smoothstep(
                at(G, 'Porch Right', 0.0), at(G, 'Porch Right', 1.0), d))),
        rock=0.75 + 0.25 * smooth_noise(rng, d, 60.0),
        spill=np.exp(-np.clip(np.maximum(at(G, 'Porch Left', 0.0) - d, d - at(G, 'Porch Right', 1.0)), 0, None) / 450),
        mouth=smoothstep(at(G, 'Right', 0.72), at(G, 'Right', 1.0), d),
        fire=Flicker(rng, G.N, 0.8, 3.5),
        lick=Flicker(rng, G.N, 2.5, 7.0),
        leaf=Flicker(rng, G.N, 0.1, 0.5),
    )


def cave(S, T, lv):
    """The cave at shared time T with levels lv (bed, forge, walls, mouth)."""
    fire, lick = S['fire'](T), S['lick'](T)
    fr = light(ROCK, lv['bed'] * S['rock'])
    fr += light(FORGE, lv['forge'] * S['forge'] * (0.8 + 0.2 * fire))
    fr += light(EMBER, 0.6 * lv['forge'] * S['heat'] * (0.7 + 0.3 * fire))
    fr += light(FORGE, lv['walls'] * S['walls'] * (0.7 + 0.3 * np.clip(lick, -1, 1)))
    fr += light(EMBER, 0.8 * lv['walls'] * S['spill'] * (1 - S['walls'] - S['forge']).clip(0) * (0.8 + 0.2 * fire))
    fr += light(FOREST, lv['mouth'] * S['mouth'] * (0.85 + 0.15 * S['leaf'](T)))
    return fr


def figure(fr, S, p, col, lvl, w=16.0):
    """A person at path distance p: a body that stands in front of the cave, and a halo."""
    body = np.exp(-((S['d'] - p) / w) ** 2)
    fr = fr * (1 - 0.85 * min(1.0, lvl / 0.2) * body)[:, None]
    return fr + light(col, lvl * body) + light(col, 0.35 * lvl * np.exp(-((S['d'] - p) / (3 * w)) ** 2))


def sparks(S, hits, t, seed, n=14, reach=1.0):
    """Hammer blows [(time, strength, where)]: each throws n sparks both ways along the roofline, -> perceptual."""
    d = S['d']
    out = np.zeros_like(d)
    for i, (th, s, p0) in enumerate(hits):
        a = t - th
        if not 0 <= a < 1.6:
            continue
        rng = np.random.default_rng(seed * 1000 + i)
        v = rng.uniform(500, 2600, n) * rng.choice([-1, 1], n) * reach
        ps = p0 + v * (1 - np.exp(-a / 0.6)) * 0.6
        life = np.exp(-a / rng.uniform(0.35, 0.9, n))
        out += (s * life[:, None] * np.exp(-((d[None, :] - ps[:, None]) / 7) ** 2)).sum(0)
    return out


def compose():
    """Every note: (time, seconds, midi, velocity, part, k). The excerpt's notes are 'orch' (k the hand, or 'trem');
    the Nibelungs' hammer rhythm is 'nib', the giants' stamps 'giants', Valhalla's chords 'valhalla' (k the chord);
    'strike', 'answer' and 'shake' mark the lights' moments."""
    N = []
    for n in tidy(EX['notes']):
        N.append((n[0], n[1], n[2], n[3], 'orch', 'trem' if n[5] else n[4]))
    for t, d, m, v, hand in EX['notes']:
        if R[0][0] <= t < R[0][1] and hand == 1 and m == 43:
            N.append((t, d, m, 110 if d >= 0.03 else 90, 'nib', None))
    last = -9.0
    for t, d, m, v, hand in sorted(EX['notes']):
        if R[1][0] <= t < R[1][1] and hand == 1 and d >= 0.15 and t - last > 0.4:
            N.append((t, max(d, 0.3), m, v, 'giants', None))
            last = t
    chords = sorted({round(t, 3) for t, d, m, v, hand in EX['notes'] if R[2][0] <= t < T_STRIKE and d >= 0.8})
    for k, t in enumerate(chords):
        N.append((t, 0.5, 0, 100, 'valhalla', k))
    N.append((T_STRIKE, 0.1, 0, 120, 'strike', None))
    N.append((T_ANSWER, 0.1, 0, 125, 'answer', None))
    for k, t in enumerate(accents(EX['notes'], T_GONE, D - 1, n=3, space=0.9)):
        N.append((t, 0.6, 0, 90, 'shake', k))
    return sorted(N, key=lambda e: e[0])


def where_wanderer(G, t):
    """His path distance: standing on Right, then out through the cave mouth."""
    return keys(t, [(T_LEAVE, at(G, 'Right', WAND_AT)), (T_GONE, G.pd.max() + 60)])


def riddle_weight(i, t):
    """How far the house has turned into riddle i's world, 0..1, before the wipe's spread."""
    t0, t1 = R[i]
    return (smoothstep(t0, t0 + 0.2, t) if i else 1.0) * (1 - smoothstep(t1 - 0.3, t1 + (0.3 if i < 2 else 1.5), t))


def render(G, seed=7):
    F = nframes(D)
    out = np.zeros((F, G.N, 3))
    S = stage(G)
    d, anvil = S['d'], S['anvil']
    L = d.max()
    seg = G.seg_of
    N = compose()
    stand = at(G, 'Right', WAND_AT)
    p_mime = at(G, 'Porch Front', MIME_AT)
    rng = np.random.default_rng(seed)
    nib = [e for e in N if e[4] == 'nib']
    nib_at = rng.uniform(at(G, 'Side', 0.1), L - 60, len(nib))
    nib_hits = [(e[0], 0.75 + 0.25 * (e[3] > 110), p) for e, p in zip(nib, nib_at)]
    stomps = [e for e in N if e[4] == 'giants']
    vh = sorted({e[0] for e in N if e[4] == 'valhalla'})
    t_strike = T_STRIKE
    shakes = [e for e in N if e[4] == 'shake']
    mid = at(G, 'Porch Front', 0.5)
    half = max(mid - d.min(), L - mid)

    for f in range(F):
        t = f * DT
        T = t + 80 * K
        fr = cave(S, T, dict(LV))
        p = where_wanderer(G, t)

        # the three worlds, each wiping out from the Wanderer over the whole house
        worlds = []
        for i in range(3):
            w = riddle_weight(i, t)
            if w <= 0:
                continue
            spread = smoothstep(0, 1, (1700 * (t - R[i][0]) - np.abs(d - stand)) / 150) if t < R[i][0] + 2 else 1.0
            if i == 0 and t < R[0][0] + 2:          # the scene opens as Nibelheim spreads out from him
                spread = smoothstep(0, 1, (1100 * (t + 0.3) - np.abs(d - stand)) / 150)
            worlds.append((i, w * spread))
        for i, w in worlds:
            if i == 0:
                world = light(DEPTHS, 0.75 * S['rock'] * (0.85 + 0.15 * S['fire'](T)))
                for th, s, p0 in nib_hits:
                    a = t - th
                    if 0 <= a < 0.6:
                        world += light(RED, min(1.0, 1.2 * s * np.exp(-a / 0.15)) * np.exp(-((d - p0) / 90) ** 2))
                        if s > 0.9:
                            run = seg == seg[np.argmin(np.abs(d - p0))]
                            world += light(RED, 0.75 * np.exp(-a / 0.3) * run)
                world += light(RED, np.clip(sparks(S, [h for h in nib_hits if 0 <= t - h[0] < 1.6], t, 71,
                                                   n=8, reach=0.5), 0, 1.0))
            elif i == 1:
                world = light(STONE, 0.3 * S['rock']) + light(OCHRE, 0.12)
                for j, e in enumerate(stomps):
                    a = t - e[0]
                    if 0 <= a < 1.6:
                        block = seg == RUNS[j % len(RUNS)]
                        world += light(OCHRE, min(1.0, 0.55 + 0.6 * np.exp(-a / 0.25)) * block * np.exp(-a / 1.2))
                        world += light(STONE, 0.35 * np.exp(-a / 0.1))
            else:
                n = sum(1 for c in vh if c <= t)
                c = vh[n - 1] if n else t
                height = min(1.0, n / len(vh) * 1.15)
                rise = (1 - np.abs(d - mid) / half) > 1 - height
                world = light(SKY, 0.5 * (0.9 + 0.1 * S['leaf'](T)) * (1 - rise))
                world += light(VALHALLA, (0.6 + 0.35 * np.exp(-(t - c) / 0.3)) * rise)
                world += light(WHITE, 0.4 * np.exp(-(t - c) / 0.15) * np.exp(-((d - mid) / 25) ** 2) * (n > 0))
            w = (w * np.ones_like(d))[:, None]
            fr = fr * (1 - 0.9 * w) + world * w

        # the spear strikes after Valhalla
        if t_strike <= t < t_strike + 1.5:
            a = t - t_strike
            fr += light(SPEAR, min(1.0, np.exp(-a / 0.15)))
            fr += light(WOTAN, 0.9 * np.exp(-a / 0.5) * np.exp(-((np.abs(d - stand) - 1600 * a) / 120) ** 2))

        # the question: his blue swells over the house; the answer crashes out
        q = smoothstep(T_Q, T_ANSWER, t) * (1 - smoothstep(T_ANSWER + 0.5, T_LEAVE + 3, t))
        fr += light(WOTAN, 0.85 * q * np.exp(-np.abs(d - p) / (200 + 1400 * q)))
        if T_ANSWER <= t < T_ANSWER + 2.5:
            a = t - T_ANSWER
            fr += light(WHITE, 0.7 * np.exp(-a / 0.12))
            fr += light(WOTAN, np.exp(-a / 0.9) * np.exp(-((np.abs(d - p) - 1800 * a) / 200) ** 2))

        # his going: a blue sweep out through the cave mouth
        if T_LEAVE <= t < T_GONE + 3:
            trail = smoothstep(p - 700, p, d) * (d <= p + 20) * (1 - smoothstep(T_GONE, T_GONE + 3, t))
            fr += light(WOTAN, 0.95 * trail)
            fr += light(WOTAN_SOFT, 0.5 * np.exp(-((d - p) / 40) ** 2) * (t < T_GONE))
        if T_GONE <= t < T_GONE + 2:
            fr += light(WOTAN_SOFT, 0.8 * np.exp(-(t - T_GONE) / 0.4) * S['mouth'])

        # Mime: asking, then flickering in panic, then shaking alone
        panic = smoothstep(T_Q, T_Q + 2, t)
        flick = panic * (0.25 * np.sin(2 * np.pi * 9 * t) + 0.12 * np.sin(2 * np.pi * 13.7 * t))
        for t0, dur, m, v, part, k in shakes:
            a = t - t0
            if 0 <= a < 1.2:                                    # Mime collapsing: yellow bursts, the forge flaring
                fr += light(MIME, 0.9 * np.exp(-a / 0.4) * np.exp(-((np.abs(d - p_mime) - 650 * a) / 90) ** 2))
                fr += light(FORGE, 0.45 * np.exp(-a / 0.3) * (S['forge'] + 0.6 * S['walls']))
        mlvl = keys(t, [(0, 0.6), (T_Q, 0.6), (T_ANSWER, 0.45), (T_ANSWER + 0.3, 0.3), (T_GONE, 0.5), (D, 0.55)])
        fr = figure(fr, S, p_mime + 5 * np.sin(2 * np.pi * 6 * t) * panic, MIME, mlvl + flick * (t < D - 3))

        # the Wanderer, flaring on the answers
        if t < T_GONE + 0.5:
            lvl = 0.8 + 0.2 * sum(riddle_weight(i, t) for i in range(3)) + 0.2 * q
            fr = figure(fr, S, p, WOTAN, lvl, 22.0)
            fr += light(SPEAR, 0.6 * lvl * np.exp(-((d - p + 24) / 5) ** 2))
        out[f] = fr
    return np.clip(out, 0, 1)


def score(M, G):
    """The real music: the excerpt orchestrated from the piano reduction, and the staging: the Nibelungs' anvils, the
    giants' stamping, a wipe into each world, the spear's blow and its thunder."""
    order = np.argsort(G.pd)
    xs, ds = G.pos[order, 0], G.pd[order]
    x0, x1 = xs.min(), xs.max()

    def pan_at(dd):                         # path distance -> left/right across the facade, from the street
        x = np.interp(dd, ds, xs)
        return float(0.85 * (2 * (x - x0) / (x1 - x0) - 1))

    stand = pan_at(at(G, 'Right', WAND_AT))
    forge = pan_at(at(G, 'Porch Front', MIME_AT))
    o = Orchestra(M, level=2.1)
    N = compose()

    def role(t, d, m, v, hand):
        if R[0][0] <= t < R[0][1] and hand == 1:                                # the Nibelungs: cellos, bassoons
            return [('cellos', 0, 0, 0.6), ('bassoons', 0, -6, 0.45)]
        if R[1][0] <= t < R[1][1] and hand == 1:                                # the giants: tuba and basses
            return [('tuba', 0, 0, 0.75), ('basses', -12 if m >= 40 else 0, -6, 0.55), ('cellos', 0, -8, 0.4)]
        if R[2][0] <= t < T_STRIKE and d >= 0.8:                                # Valhalla: trombones and horns
            return [('trombones' if m < 60 else 'horns', 0, 0, 0.75), ('horns', -12 if m >= 60 else 0, -10, 0.4)]
        if SEG[4][0] + 3 <= t < SEG[4][1] and d >= 0.2 and v >= 98:            # the answer: the full brass
            return [('trumpets' if m >= 60 else 'trombones', 0, 0, 0.7), ('horns', 0, -6, 0.5)]
        return None

    o.tutti([e[:4] + (e[5] if e[5] in (0, 1) else 0, e[5] == 'trem') for e in N if e[4] == 'orch'],
            size=lambda t: 1.0 if t >= T_Q else 0.8, role=role)
    rng = np.random.default_rng(7)
    for t, d, m, v, part, k in N:
        if part == 'nib':                                                       # anvils all over the house
            o.hit('anvil', t, v, gain=0.4 if v > 100 else 0.25, pan=float(rng.uniform(-0.8, 0.8)))
        elif part == 'giants':                                                  # the giants stamp
            o.hit('bass drum', t, min(127, v + 10), gain=0.6, pan=float(rng.uniform(-0.6, 0.6)))
            o.hit('timpani', t, min(127, v), pitch=-6, gain=0.5)
    for i, (t0, t1) in enumerate(SEG[1:], 1):                                   # a rush into each new world
        M.add('fx', whoosh(1.0, 2500, 300, 0.6, seed=70 + i), t0 - 0.5, 0.7, stand)
    o.boom(T_STRIKE, stand, 0.9)                                                # the spear strikes the floor
    o.thunder(T_STRIKE + 0.15, 0.35, stand, 0.8)
    o.hit('crash', T_ANSWER, 118, gain=0.5)
    o.hit('timpani', T_ANSWER, 124, pitch=-5, gain=0.7)
    o.hit('gong scrape', T_LEAVE + 1, 100, gain=0.4, pan=pan_at(G.pd.max()))
    o.fire(0.0, D + 0.5, 0.25, forge, crackle=6, seed=707)
    o.effects([(0, -1), (R[0][1], -1), (R[1][1], -1), (R[2][0] + 0.5, -10), (T_STRIKE - 0.3, -1),
               (T_STRIKE + 2.5, -1), (T_Q + 1, -8), (T_ANSWER - 0.2, -10), (T_LEAVE, -6), (D, -6)])
