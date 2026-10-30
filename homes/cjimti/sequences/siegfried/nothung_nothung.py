"""Nothung! Nothung!: Siegfried takes the anvil and Mime scuttles back down the porch to the far end of Left to
brew a sleeping draught, his poison seething sickly green. Siegfried sings his Sword Song, and every "Nothung!"
flashes the shards on the anvil steel white. On "Zu Spreu nun schuf ich die scharfe Pracht" he files them to
dust: white streaks rasp back and forth across Porch Front on every beat, throwing grey-white grit, and on "im
Tiegel brat' ich die Späne" the crucible starts to glow. Then the refrain, "Hoho! Hahei!", and "Blase, Balg!":
with every breath of the bellows the fire surges up the chimney walls and floods out across the whole house in
orange, sparks flying to both ends. After the third verse the refrain comes round once more as the steel melts,
the crucible going from red to orange to white-hot, and the forge ends roaring.

The music is Wagner's own: Act I, bars 2430 to 2456 (the Sword Song's first verse and refrain) and 2504 to 2512
(its third refrain), as Solti's 1958 Vienna Philharmonic recording takes them. The notes come from the Wagner Ring
Dataset's piano reduction (pixelhome/ring.py), orchestrated by hand and register; the bellows' surging figure in
the bass on cellos, basses and tuba, the trills on violins and flutes. Siegfried's own line is not in the
reduction, so it comes from the Breitkopf & Härtel vocal score (Leipzig 1914, archive.org 31761034115105, pp.
113-114 and 118) and is played as he sings it, a tenor an octave below the written notes, on horns doubled by a
trumpet. On stage: the file's rasp on every stroke, a whoosh for every breath of the bellows, the forge roaring
up with it and crackling, the crucible sizzling as the steel melts; they back off under "Nothung! Nothung!" and
lead in the bellows refrains.

compose() holds every note; stage(), cave(), figure() and sparks() are the cave, shared word for word by Act I's
scenes on a clock that runs on from scene to scene."""
import numpy as np
from pixelhome.audio import note, whoosh
from pixelhome.fx import DT, hexc, light, smoothstep, nframes, keys, Flicker, smooth_noise
from pixelhome.ring import Orchestra, excerpt, tidy

CODE = 'SF09'
TITLE = 'Nothung! Nothung!'
KIND = 'show'
DESCRIPTION = ('Siegfried sings his Sword Song, files the broken sword to dust, and works the bellows until the '
               'forge roars across the whole house and the steel melts, while the dwarf brews poison in the corner.')
VOICEOVER = ('Nobody can mend the sword, so Siegfried makes it new himself. '
             'Nothung! Nothung!')

K = 8                                       # this scene's place on Act I's shared clock: T = t + 80 K
EX = excerpt(__file__)                      # Act I, bars 2430-2456 and 2504-2512, Solti 1958
D = EX['seconds']
_M = np.array([m for m, _ in EX['bars']], float)
_T = np.array([t for _, t in EX['bars']])


def bt(m):
    """Seconds into the scene of measure position m (bar plus fraction)."""
    return float(np.interp(m, _M, _T))


# Siegfried's Sword Song, from the vocal score: (bar, beat, beats, written note); 3/4, a quarter to the beat
_BLASE = [(0, 'G5'), (0.5, 'F5'), (1, 'Eb5'), (1.5, 'D5'), (2, 'C5'), (2.5, 'Bb4')]
_HOHO = lambda b: [(b, 2, 1, 'A4'), (b + 1, 0, 2, 'D5'), (b + 1, 2, 1, 'E5'), (b + 2, 0, 0.5, 'A4'),
                   (b + 2, 0.5, 0.5, 'E5'), (b + 2, 1, 1, 'A4'), (b + 3, 0.5, 0.5, 'E5'), (b + 3, 1, 1, 'A4'),
                   (b + 3, 2, 1, 'E5'), (b + 4, 0, 2.5, 'A5')] + [(b + 5, x, 0.5, n) for x, n in _BLASE] + \
                  [(b + 6, 0, 2, 'A4')]
VOICE = ([(2434, 0, 2, 'F5'), (2434, 2, 1, 'F4'), (2435, 0, 2, 'F5'), (2435, 2, 1, 'F4'), (2436, 0, 1.5, 'E5'),
          (2436, 1.5, 0.5, 'F5'), (2436, 2, 1, 'E5'), (2437, 0, 2, 'D5'), (2437, 2, 1, 'C5'), (2438, 0, 0.75, 'B4'),
          (2438, 0.75, 0.25, 'B4'), (2438, 1, 1.5, 'B4'), (2438, 2.5, 0.5, 'E5'), (2439, 0, 1, 'E5'),
          (2439, 1, 1, 'G4'), (2440, 2, 1, 'A4'), (2441, 0, 2, 'D5'), (2441, 2, 1, 'D5'), (2442, 0, 2, 'C5'),
          (2442, 2, 0.5, 'C5'), (2442, 2.5, 0.5, 'C5'), (2443, 0, 2, 'Bb4'), (2443, 2, 1, 'Bb4'), (2444, 0, 1, 'A4'),
          (2444, 2, 1, 'A4'), (2445, 0, 2, 'D5'), (2445, 2, 1, 'D4'), (2446, 0, 2, 'A4'), (2446, 2, 0.5, 'B4'),
          (2446, 2.5, 0.5, 'C#5'), (2447, 0, 1, 'D5'), (2447, 1, 1, 'D4')] + _HOHO(2448) +
         [(2455, x, 0.5, n) for x, n in _BLASE] + [(2456, 0, 2, 'A4')] + _HOHO(2504)[:-7] +
         [(2509, x, 0.5, n) for x, n in _BLASE] + [(2510, 0, 2, 'A4')] +
         [(2511, x, 0.5, n) for x, n in zip((0, 0.5, 1, 1.5, 2, 2.5), ('A5', 'G5', 'F5', 'E5', 'D5', 'C#5'))] +
         [(2512, 0, 2, 'D5')])

T_MOVE = 0.5                                # Siegfried to the anvil, Mime off down the porch
T_SING = bt(2434)                           # "Nothung! Nothung!"
T_FILE = (bt(2440.6), bt(2448))             # "Zu Spreu nun schuf ich die scharfe Pracht": the file
T_CRUCIBLE = bt(2444.6)                     # "im Tiegel brat' ich die Späne": the shards in the fire
T_BELLOWS = [bt(b) for b in range(2449, 2457)] + [bt(b) for b in range(2505, 2513)]   # a breath a bar
T_MELT = bt(2504)                           # the third refrain: the steel melts
T_MIME = [bt(b) for b in (2441, 2443, 2445, 2447, 2505.5, 2507.5, 2509.5)]       # his poison bubbling

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
SIEGFRIED = hexc('#00ff40')
HEAD = hexc('#e8ffe8')
STEEL = hexc('#e8f8ff')
GRIT = hexc('#a8b0b8')
REDHOT = hexc('#ff3000')
POISON = hexc('#a0d000')

START = dict(bed=0.28, forge=0.55, walls=0.45, mouth=0.55)        # where SF08 left the cave
END = dict(bed=0.28, forge=0.8, walls=0.7, mouth=0.55)            # where SF10 picks it up
MIME_FROM, SIEG_FROM = 0.32, 0.7            # on Porch Front, where SF08 left them
MIME_AT = 0.7                               # Mime's place on Left, at his pot


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


def voice():
    """Siegfried's Sword Song in seconds: (time, seconds, sounding midi)."""
    return [(bt(b + x / 3), bt(b + (x + n) / 3) - bt(b + x / 3), note(name) - 12) for b, x, n, name in VOICE]


def compose():
    """Every note: (time, seconds, midi, velocity, part, k). The excerpt's notes are 'orch' (k the hand, or 'trem'
    for a tremolo); Siegfried's line is 'sing'; 'name', 'file', 'breath' and 'surge' mark the lights' moments."""
    N = []
    for n in tidy(EX['notes']):
        N.append((n[0], n[1], n[2], n[3], 'orch', 'trem' if n[5] else n[4]))
    for t, d, m in voice():
        N.append((t, d, m, 112, 'sing', None))
    for t, d, m in voice()[:4]:
        if d > 0.5:
            N.append((t, 1.0, m, 0, 'name', None))
    t, k = T_FILE[0], 0
    beat = (bt(2441) - bt(2440)) / 3
    while t < T_FILE[1] - 0.1:
        N.append((t, beat * 0.9, 0, 0, 'file', k))
        t += beat
        k += 1
    for k, t0 in enumerate(T_BELLOWS):
        N.append((t0, 1.6, 0, 0, 'breath', k))
    for k, t0 in enumerate(T_MIME):
        N.append((t0, 0.3, 0, 0, 'mime', k))
    lows = [n for n in EX['notes'] if n[4] == 1 and n[3] >= 105 and (n[0] >= bt(2448) or n[0] < T_SING)]
    seen = []
    for n in sorted(lows):
        if not seen or n[0] - seen[-1] > 0.6:
            seen.append(n[0])
            N.append((n[0], 0.5, n[2], n[3], 'surge', None))
    return sorted(N, key=lambda e: e[0])


def blows(S):
    """The forge's surges on the orchestra's accents: [(time, strength, where)]."""
    return [(t, 0.8 if t < T_MELT else 1.0, S['anvil']) for t, _, m, v, part, k in compose() if part == 'surge']


def render(G, seed=9):
    F = nframes(D)
    out = np.zeros((F, G.N, 3))
    S = stage(G)
    d, anvil = S['d'], S['anvil']
    N = compose()
    hits = blows(S)
    hit_t = np.array([h[0] for h in hits])
    names = np.array([e[0] for e in N if e[4] == 'name'])
    files = [e for e in N if e[4] == 'file']
    breaths = np.array([e[0] for e in N if e[4] == 'breath'])
    melt_on = np.array(sorted({e[0] for e in N if e[4] == 'sing' and e[0] >= T_MELT}))
    mimes = np.array([e[0] for e in N if e[4] == 'mime'])
    sung = [(e[0], e[1]) for e in N if e[4] == 'sing' and T_SING + 4 <= e[0] < T_BELLOWS[0] - 1]
    rng = np.random.default_rng(seed)
    bubble = Flicker(rng, G.N, 1.5, 4.0)
    pf = at(G, 'Porch Front', 0.0), at(G, 'Porch Front', 1.0)
    blade = np.exp(-((d - anvil) / 55) ** 6)
    p_pot = at(G, 'Left', MIME_AT)
    pot = np.exp(-((d - p_pot) / 60) ** 2)
    m0, s0 = at(G, 'Porch Front', MIME_FROM), at(G, 'Porch Front', SIEG_FROM)
    b0 = T_BELLOWS[0]

    for f in range(F):
        t = f * DT
        T = t + 80 * K
        lv = {k: keys(t, [(0, START[k]), (b0, START[k]), (T_MELT, 0.5 * (START[k] + END[k])), (D - 4, END[k])])
              for k in START}

        # the bellows: every breath the fire surges up the chimney and floods the house in orange
        j = int(np.searchsorted(breaths, t, side='right')) - 1
        surge = 0.0
        if j >= 0 and t - breaths[j] < 1.6:
            surge = np.sin(np.pi * (t - breaths[j]) / 1.6) ** 2 * (0.8 + 0.03 * j)
        lv['forge'] += 0.3 * surge
        lv['walls'] += 0.35 * surge
        roaring = smoothstep(T_MELT - 1, T_MELT + 2, t)
        fr = cave(S, T, lv)
        fr += light(FORGE, 0.85 * surge * S['spill'])
        fr += light(SPARK, 0.45 * surge * S['spill'] ** 3 * np.clip(S['lick'](T), 0, 1))
        fr += light(FORGE, 0.3 * roaring * S['spill'])

        # "Nothung!": the shards flash steel white, a white sweep across the porch
        i = int(np.searchsorted(names, t, side='right')) - 1
        if i >= 0 and t - names[i] < 1.4:
            a = t - names[i]
            fr += light(STEEL, 0.95 * np.exp(-a / 0.25) * blade)
            fr += light(STEEL, 0.85 * np.exp(-a / 0.7) * np.exp(-((np.abs(d - anvil) - 1200 * a) / 120) ** 2))

        # his song stirs the forge: every sung note sends a ripple of embers out from the anvil
        for t0, dd in sung:
            a = t - t0
            if 0 <= a < 2.0:
                w = min(1.0, 0.45 + 0.4 * dd)
                fr += light(FORGE, w * np.exp(-a / 0.7) * np.exp(-((np.abs(d - anvil) - 700 * a) / 90) ** 2))

        # the file: white streaks rasping back and forth across Porch Front, grit thrown off
        for t0, dd, m, v, part, k in files:
            a = t - t0
            if 0 <= a < 0.7:
                u = min(1.0, a / max(dd, 0.3))
                x = pf[0] + 30 + (pf[1] - pf[0] - 60) * (u if k % 2 == 0 else 1 - u)
                fr += light(STEEL, 0.9 * np.exp(-a / 0.4) * np.exp(-((d - x) / 18) ** 2))
                fr += light(GRIT, 0.45 * np.exp(-a / 0.2) * ((d > pf[0]) & (d < pf[1])))
                fr += light(GRIT, 0.6 * np.exp(-a / 0.3) * ((d - x) * (1 if k % 2 == 0 else -1) < 0) *
                            np.exp(-np.abs(d - x) / 70))

        # the crucible: the shards glow in the fire, then melt red, orange, white-hot on the last refrain
        heat = keys(t, [(T_CRUCIBLE, 0.0), (T_CRUCIBLE + 3, 0.25), (T_MELT, 0.35), (T_MELT + 8, 0.7), (D - 3, 1.0)])
        if heat > 0:
            col = REDHOT * (1 - heat) + HEAT * heat if heat < 0.8 else HEAT
            k = int(np.searchsorted(melt_on, t, side='right')) - 1
            flare = np.exp(-(t - melt_on[k]) / 0.3) if k >= 0 else 0.0
            fr = fr * (1 - 0.8 * min(1, heat * 3) * blade)[:, None]
            fr += light(col, (0.6 + 0.4 * heat + 0.2 * flare) * blade)
            fr += light(REDHOT, 0.5 * (heat + flare) * np.exp(-((d - anvil) / 260) ** 2))
            fr += light(FORGE, 0.6 * flare * S['spill'])

        # the forge's surges on the orchestra's accents: a flash on the anvil, a shockwave and sparks
        i = int(np.searchsorted(hit_t, t, side='right')) - 1
        if i >= 0 and t - hit_t[i] < 1.2:
            a, s = t - hit_t[i], hits[i][1]
            fr += light(HEAT, min(1.0, 0.8 * s * np.exp(-a / 0.12)) * S['heat'] ** 0.5)
            fr += light(FORGE, 0.75 * s * np.exp(-a / 0.5) * np.exp(-((np.abs(d - anvil) - 1500 * a) / 90) ** 2))
        fr += light(SPARK, np.clip(sparks(S, hits, t, 90, n=18) + sparks(S, [(b, 0.6, anvil) for b in breaths],
                                                                         t, 91, n=10), 0, 1.0))

        # Mime at his pot at the end of Left: the poison seethes sickly green, bubbling as he mutters
        k = int(np.searchsorted(mimes, t, side='right')) - 1
        bub = np.exp(-(t - mimes[k]) / 0.25) if k >= 0 else 0.0
        brew = smoothstep(T_MOVE + 4, T_MOVE + 8, t)
        fr += light(POISON, brew * (0.45 + 0.2 * np.clip(bubble(T), 0, 1) + 0.45 * bub) * pot)
        u = smoothstep(T_MOVE, T_MOVE + 5, t)
        pm = m0 + u * (p_pot - m0) + 10 * bub * np.sin(2 * np.pi * 5 * t)
        fr = figure(fr, S, pm, MIME, 0.6 + 0.15 * bub)

        # Siegfried at the anvil, flaring as he sings and with every surge
        ps = s0 + smoothstep(T_MOVE, T_MOVE + 3, t) * (anvil + 4 - s0)
        blow = np.exp(-(t - hit_t[i]) / 0.2) if i >= 0 else 0.0
        lvl = 0.8 * (1 + 0.3 * blow + 0.25 * surge)
        fr = figure(fr, S, ps, SIEGFRIED, lvl, 18.0)
        fr += light(HEAD, lvl * np.exp(-((d - ps) / 6) ** 2))
        out[f] = fr
    return np.clip(out, 0, 1)


def score(M, G):
    """The real Sword Song: the excerpt orchestrated from the piano reduction, Siegfried's line on horns and a
    trumpet, and the forge's sounds: the file, the bellows, the fire, the melting steel."""
    order = np.argsort(G.pd)
    xs, ds = G.pos[order, 0], G.pd[order]
    x0, x1 = xs.min(), xs.max()

    def pan_at(dd):                         # path distance -> left/right across the facade, from the street
        x = np.interp(dd, ds, xs)
        return float(0.85 * (2 * (x - x0) / (x1 - x0) - 1))

    forge = pan_at(at(G, 'Porch Front', 0.5))
    o = Orchestra(M, level=1.5)
    guiro = M.hits('Percussion/Guiro-Hit*.wav')
    N = compose()

    def size(t):
        if t < T_SING:
            return 0.9
        return 1.0 if t >= bt(2448) else 0.55

    def role(t, d, m, v, hand):
        if T_SING <= t < bt(2448) and hand == 1 and m >= 54 and d >= 0.3:       # under the verse: soft horns
            return [('horns', 0, -16, 0.45), ('violas', 0, -10, 0.35)]
        return None

    o.tutti([e[:4] + (e[5] if e[5] != 'trem' else 0, e[5] == 'trem') for e in N if e[4] == 'orch'],
            size=size, role=role)
    for t, d, m, v, part, k in N:
        if part == 'sing':                                                      # Siegfried: horns and a trumpet
            o.play('horns', m, t, max(d, 0.15), v, forge, 0.95)
            o.play('trumpets', m, t, max(d, 0.15), v - 18, forge, 0.4)
        elif part == 'file':
            M.add('fx', guiro.play(96 + 6 * (k % 2)), t, 0.9, forge + (0.15 if k % 2 else -0.15))
        elif part == 'breath':
            M.add('fx', whoosh(1.4, 180, 1300, 0.7, seed=90 + k), t - 0.1, 0.8, forge)
            o.hit('timpani roll', t, 70, pitch=-6, gain=0.25, pan=forge)
        elif part == 'surge':
            o.hit('timpani', t, min(127, v), pitch=-4, gain=0.35, pan=forge)
    level = lambda tt: (0.25 + 0.35 * smoothstep(T_BELLOWS[0] - 2, T_BELLOWS[0], tt) +
                        0.3 * smoothstep(T_MELT, D - 4, tt))
    o.fire(0.0, D + 0.5, level, forge, crackle=10, seed=909)
    o.fire(T_CRUCIBLE, D + 0.5, lambda tt: 0.15 + 0.35 * smoothstep(T_MELT, D - 3, tt), forge, crackle=25, seed=910)
    o.effects([(0, -4), (T_SING - 0.5, -4), (T_SING, -11), (T_FILE[0] - 0.3, -11), (T_FILE[0], -3),
               (T_FILE[1] - 0.5, -3), (T_FILE[1], -6), (T_BELLOWS[0] - 0.3, -6), (T_BELLOWS[0], -1),
               (T_MELT, -2), (D, 0)])
