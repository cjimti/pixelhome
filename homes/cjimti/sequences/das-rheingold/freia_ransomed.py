"""Freia Ransomed: the giants bring Freia back up the mountain, the gods heap the gold round her until she is
hidden, Fasolt still sees her eye through a gap, and Wotan refuses to give up the ring that would close it.

The music is Wagner's own: four passages of the last scene of Das Rheingold (bars 3226-3231, 3326-3339, 3396-3403
and 3446-3455) as Solti's 1958 Vienna Philharmonic recording takes them, from the Wagner Ring Dataset's piano
reduction (pixelhome/ring.py). The giants come in over their tread, a G pounding on every beat in the tubas,
basses and timpani, with Freia's music above it in the violins; the gold is heaped up to the falling octaves of
the bassoons, cellos and horns, a lump for each; Fasolt's "Weh! noch blitzt ihr Blick" swells into Freia's love
music over trembling strings; and Donner's "Spende den Ring doch!" and Wotan's "Laßt mich in Ruh': den Reif
geb' ich nicht!" break into the full orchestra, trumpets on top and the spear's falling scale in the trombones and
tubas. The staging's sounds go over it: the giants' footfalls, a great double thud as their staves are planted,
gold clinking on the pile, Fafner's stamp as he orders it packed tighter, a gong scraped as the helmet lands on
top, the boom and crash of Wotan's refusal and the giants stamping in outrage. They back off for Freia's eye.

The giants stamp in from the free end of Right on that tread, Freia's pink between them, and as she comes near
the grey gods on the wings get a little of their colour back. She is set down on the hoard at the back of the
porch and the staves go in on either side of her, one grey, one ochre. Then the gold flies: every falling octave
is a lump that Loge, Donner or Froh flings across the house, a comet along the roofline landing on the pile with a
flash; the heap grows round the pink from the edges in, Fafner twice stamps up and presses it down, and the helmet
settles on top in a violet-grey shimmer. Through one gap a pink glint still shows, pulsing with the love music.
Donner begs for the ring; Wotan refuses: the ring flares red across the porch, the spear's scale strikes out along
Porch Left note by note, and the giants stamp in outrage.

compose() tags the music's moments, choreography() every position; render() and score() read both."""
import numpy as np
from pixelhome.fx import DT, hexc, light, smoothstep, nframes, Flicker
from pixelhome.ring import Orchestra, excerpt, tidy

CODE = 'RG21'
TITLE = 'Freia Ransomed'
KIND = 'show'
DESCRIPTION = ('The giants bring Freia back and plant their staves around her, and the gods heap up the gold '
               'until she is hidden. But one giant can still see her eye through a gap, and there is only one '
               'thing left to fill it: the ring on Wotan\'s hand.')
VOICEOVER = ('Freia comes home, but only as far as the gold. '
             'Pile it high enough to hide her, the giants say, and she is yours again.')

EX = excerpt(__file__)                      # bars 3226-3231, 3326-3339, 3396-3403, 3446-3455, Solti 1958
BAR = {int(m): t for m, t in EX['bars']}
SEG = [g['start'] for g in EX['segments']] + [EX['seconds']]
GSTEP = 0.8                                 # the giants' tread: the G on every beat
T_WALK = 0.0
T_FREIA = [0.0, 6.54]
T_PLANT = [BAR[3231], 17.72]                # the low G, then the chord: the staves go in
FAF = [37.68, 47.3]                         # Fafner: "Nicht so leicht und locker gefügt!", "Fest und dicht"
T_HELM = BAR[3339] + 0.1                    # the helmet on top
T_EYE = SEG[2]                              # Fasolt sees her eye: the love music swells
T_RING = SEG[3]                             # "Spende den Ring doch!"
T_PLEA = 73.5                               # its fortissimo chords
T_REFUSE = BAR[3452]                        # after "den Reif geb' ich nicht!": the full orchestra
T_RAGE = 86.26
STAMPS_RAGE = [86.26, 88.02, 88.45, 88.89]
T_HANDOVER = 5.0                            # seconds to grow out of the last scene's look
D = EX['seconds']
T0 = 0.0                                  # the opera's clock at our start: steady motion carries across the cuts

FLIGHT = 0.85                               # seconds a lump of gold flies
HEAP = 92                                   # half-width of the finished pile (between the staves)
THROWERS = ['loge', 'donner', 'froh']

GOLD = hexc('#ffaa00')
HOT = hexc('#fff0a0')
FREIA = hexc('#ff5a9a')
APPLE = hexc('#ffd040')
LEAF = hexc('#60d020')
WOTAN = hexc('#1a3cff')
STEEL = hexc('#c8d8ff')
RED = hexc('#ff1800')
FASOLT = hexc('#8090a0')
FAFNER = hexc('#c07a10')
FRICKA = hexc('#ff9ad0')
DONNER = hexc('#ffffff')
BOLT = hexc('#a0c0ff')
LOGE0, LOGE1 = hexc('#ff5000'), hexc('#ffb020')
TARN = hexc('#5a4a8a')
CASTLE = hexc('#fff0c0')
DAWN0, DAWN1 = hexc('#2a3a6a'), hexc('#6a5a8a')
WHITE = hexc('#ffffff')


def at(G, seg, u):
    s = G.pd[G.seg[seg]]
    return float(s.min() + u * (s.max() - s.min()))


def grey(c, g):
    """A god's colour drained toward grey by g (0 = full colour, 1 = stone)."""
    lum = float(c @ np.array([0.3, 0.59, 0.11]))
    return c + (np.full(3, 0.15 + 0.75 * lum) - c) * g


def hue(h):
    """Rainbow colours for hue h (any shape, 0..1 wraps) -> (..., 3)."""
    h = np.asarray(h) % 1.0
    return np.stack([np.clip(np.abs(h * 6 - 3) - 1, 0, 1), np.clip(2 - np.abs(h * 6 - 2), 0, 1),
                     np.clip(2 - np.abs(h * 6 - 4), 0, 1)], -1)


def faded(t):
    """How grey the gods are: Freia's coming brings a little colour back; Wotan's refusal drains it again."""
    return 1.0 - 0.4 * smoothstep(1, 9, t) + 0.2 * smoothstep(T_REFUSE, T_REFUSE + 4, t)


def compose():
    """The music's moments, from the excerpt's real notes: (time, seconds, midi, velocity, part, who). 'stamp' is
    the giants' tread (the low G on every beat), 'freia' her music above it, 'plant' the staves, 'lump' each falling
    octave of the heaping (who throws it), 'faf' Fafner's orders, 'tarn' the helmet, 'love' the love music under
    her eye, 'ring' Donner's plea, 'spear' each step of the falling scale after Wotan's refusal."""
    N = []
    seen = set()
    k = 0
    for t, d, m, v, h in EX['notes']:
        if t < SEG[1]:
            if h == 1 and m in (31, 43) and d >= 0.5 and t < T_PLANT[0] and t not in seen:
                seen.add(t)
                N.append((t, d, m, v, 'stamp', ('fafner', 'fasolt')[k % 2]))
                k += 1
            elif h == 0 and m >= 60:
                N.append((t, d, m, v, 'freia', None))
        elif t < SEG[2]:
            if h == 1 and d >= 0.3 and t not in seen:
                seen.add(t)
                if T_HELM - 0.2 > t:
                    N.append((t, d, m, v, 'lump', ['loge', 'donner', 'froh'][len(seen) % 3]))
            if any(f0 <= t < f0 + 2.6 for f0 in FAF) and h == 1 and d >= 0.3:
                N.append((t, d, m, v, 'faf', 'fafner'))
            if t >= T_HELM - 0.2 and h == 0:
                N.append((t, d, m, v, 'tarn', None))
        elif t < SEG[3]:
            if h == 1 and d >= 0.3:
                N.append((t, d, m, v, 'love', None))
        else:
            if T_PLEA <= t < T_PLEA + 1.8 and h == 0:
                N.append((t, d, m, v, 'ring', None))
            if (h == 0 and 82.8 <= t < 85.9 or h == 1 and 86.0 <= t < 89.2) and d >= 0.2:
                if (round(t, 2), 'spear') not in seen:
                    seen.add((round(t, 2), 'spear'))
                    N.append((t, d, m, v, 'spear', None))
    for i, tp in enumerate(T_PLANT):
        N.append((tp, 0.8, 31, 0, 'plant', ('fasolt', 'fafner')[i]))
    for i, ts in enumerate(STAMPS_RAGE):
        N.append((ts, 0.5, 36, 0, 'stamp', ('fafner', 'fasolt')[i % 2]))
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


def choreography(G):
    """Per frame: where everyone is (path distance)."""
    F = nframes(D)
    t = np.arange(F) * DT
    hc = at(G, 'Porch Front', 0.5)
    who = ['wotan', 'loge', 'freia', 'fasolt', 'fafner', 'donner', 'fricka', 'froh']
    tgt = {k: np.zeros(F) for k in who}
    rate = {k: np.full(F, 3.0) for k in who}

    def set_(k, a, b, where, r):
        m = (t >= a) & (t < b)
        tgt[k][m] = where if np.ndim(where) == 0 else where[m]
        rate[k][m] = r

    set_('wotan', 0, D, at(G, 'Porch Front', 0.4), 3.0)
    set_('wotan', 3.0, D, at(G, 'Porch Front', 0.12), 1.2)
    jit = 8 * np.sin(2 * np.pi * (t + T0) * 1.7) + 5 * np.sin(2 * np.pi * (t + T0) * 3.1)
    set_('loge', 0, D, at(G, 'Porch Front', 0.75), 6.0)
    set_('loge', 2.0, D, at(G, 'Porch Left', 0.75), 2.2)
    set_('donner', 0, D, at(G, 'Left', 0.3), 3.0)
    set_('fricka', 0, D, at(G, 'Left', 0.6), 3.0)              # where Alberich's Curse left them
    set_('fricka', 3.0, D, at(G, 'Left', 0.7), 0.8)
    set_('froh', 0, D, at(G, 'Right', 0.3), 3.0)
    set_('froh', 5.0, D, at(G, 'Right', 0.7), 0.9)              # Froh steps aside once the giants are past

    # the giants bring her in: Fasolt leading, Fafner behind, each tread a lurch
    end = at(G, 'Right', 0.865) + 20
    u = np.clip((t - T_WALK) / (T_PLANT[0] - 0.4 - T_WALK), 0, 1)
    lurch = np.floor((t - T_WALK) / GSTEP) * GSTEP + T_WALK
    ul = np.clip((lurch + GSTEP * smoothstep(0, 0.35, (t - lurch)) - T_WALK) / (T_PLANT[0] - 0.4 - T_WALK), 0, 1)
    walk = end - 20 + (hc - end + 20) * (0.5 * u + 0.5 * ul)
    set_('freia', 0, D, walk, 8.0)
    set_('freia', T_PLANT[0], D, hc, 4.0)
    gap = 41 + 44 * smoothstep(0, 3, t)
    set_('fasolt', 0, T_PLANT[0], walk - gap, 8.0)
    set_('fafner', 0, T_PLANT[0], walk + gap, 8.0)
    FS, FF = at(G, 'Porch Right', 0.2), at(G, 'Porch Right', 0.55)
    set_('fasolt', T_PLANT[0], T_PLANT[0] + 1.0, hc - 100, 5.0)
    set_('fafner', T_PLANT[0], T_PLANT[1] + 1.0, hc + 100, 5.0)
    set_('fasolt', T_PLANT[0] + 1.0, D, FS, 1.6)
    set_('fafner', T_PLANT[1] + 1.0, D, FF, 1.6)
    for t0 in FAF:                                          # Fafner stamps up to the pile and back
        set_('fafner', t0 - 0.6, t0 + 3.6, hc + 140, 3.0)
        set_('fafner', t0 + 3.6, t0 + 6.0, FF, 2.0)
    set_('fasolt', T_EYE - 1.0, T_RING, hc + 125, 0.9)       # Fasolt bends close to the gap
    set_('fafner', T_RING - 0.5, T_REFUSE, hc + 150, 2.0)   # Fafner looms toward Wotan
    set_('fasolt', T_RING, D, FS, 1.5)
    set_('fafner', T_REFUSE, D, FF, 1.5)
    for i, ts in enumerate(STAMPS_RAGE):                    # outrage: lunges at each stamp
        k = ('fafner', 'fasolt')[i % 2]
        base = FF if k == 'fafner' else FS
        set_(k, ts - 0.15, ts + 0.35, base - 40, 10.0)
        set_(k, ts + 0.35, ts + 1.0, base, 4.0)
    pos = {k: follow(tgt[k], rate[k]) for k in who}
    pos['loge'] = pos['loge'] + jit                        # the flicker on top of where he stands
    pos['t'] = t
    return pos


def throws(G, C):
    """The lumps of gold: (landing time, launch place)."""
    out = []
    for t, d, m, v, part, who in compose():
        if part == 'lump':
            out.append((t, float(np.interp(t - FLIGHT, C['t'], C[who]))))
    return out


def render(G, seed=21):
    rng = np.random.default_rng(seed)
    F = nframes(D)
    out = np.zeros((F, G.N, 3))
    d = G.pd
    C = choreography(G)
    N = compose()
    hc = at(G, 'Porch Front', 0.5)
    porch = np.isin(G.seg_of, ['Porch Left', 'Porch Front', 'Porch Right'])
    wings = ~porch
    block = np.floor(d / 34).astype(int)
    mason = np.where((d % 34) < 22, 1.0, 0.35) * (0.8 + 0.2 * rng.random(block.max() + 1)[block])
    tw = Flicker(np.random.default_rng(2101), G.N, 2.0, 7.0)    # shared by RG21-24
    fl = Flicker(np.random.default_rng(2102), G.N, 4.0, 11.0)
    slow = Flicker(np.random.default_rng(2103), G.N, 0.1, 0.4)
    lumps = throws(G, C)
    land = np.array([a for a, _ in lumps])
    stamps = [(e[0], e[5]) for e in N if e[4] in ('stamp', 'plant')]
    faf = np.array([e[0] for e in N if e[4] == 'faf'])
    loves = np.array([e[0] for e in N if e[4] == 'love'])
    rings = np.array([e[0] for e in N if e[4] == 'ring'])
    spears = np.array([e[0] for e in N if e[4] == 'spear'])
    freias = np.array([e[0] for e in N if e[4] == 'freia'])
    tarn = np.array([e[0] for e in N if e[4] == 'tarn'])

    # the heap: which pixels the gold covers first (the edges), and the one gap that never closes
    rel = np.abs(d - hc) / HEAP
    thr = np.clip(0.72 * (1 - rel) + 0.28 * rng.random(G.N), 0, 0.97)
    eye = int(np.argmin(np.abs(d - (hc + 12))))
    thr[eye] = 2.0
    pl1 = at(G, 'Porch Left', 0.0)

    def recent(ts, t, tau, span=2.0):
        i = int(np.searchsorted(ts, t, side='right')) - 1
        return float(np.exp(-(t - ts[i]) / tau)) if i >= 0 and t - ts[i] < span else 0.0

    # how Alberich's Curse leaves the mountain, drawn at this scene's positions so the cut is seamless
    po = np.zeros(G.N)
    po[porch] = d[porch] - d[porch].min()
    merlon = np.where((po // 24) % 2 == 0, 1.0, 0.3) * porch
    huey = np.clip(1 - np.minimum(d, G.length - d) / (0.45 * G.length), 0, 1)
    dc = DAWN0[None, :] * (1 - huey[:, None]) + DAWN1[None, :] * huey[:, None]
    dc = dc * 0.9 + (dc @ np.array([0.3, 0.59, 0.11]))[:, None] * 0.1

    def mix(c, k):
        return c * (1 - k) + (c @ np.array([0.3, 0.59, 0.11])) * k

    def blob(p, w):
        return np.exp(-((d - p) / w) ** 2)

    def curse_look(t, f):
        out_ = np.zeros((G.N, 3))
        swell = 0.5 + 0.5 * np.cos(2 * np.pi * (d / 900 - 0.05 * (t + 134)))
        out_ += (((0.36 + 0.1 * swell) * (wings + 0.5 * porch)) ** 2.2)[:, None] * dc
        out_ += light(mix(CASTLE, 0.15), 0.34 * merlon)
        out_ += light(GOLD, 0.9 * blob(hc, 22) + 0.25 * blob(hc, 44))
        out_ += light(HOT, 0.6 * blob(hc, 11) * (0.5 + 0.5 * tw(t)) * (tw(t) > 0))
        out_ += light(TARN, 0.55 * blob(hc, 30) * (0.6 + 0.4 * tw(t)))
        p = C['loge'][f]
        fk = 0.5 + 0.5 * np.tanh(fl(t))
        out_ += light(LOGE0, 0.7 * blob(p, 22) * (1 - 0.5 * fk) + 0.25 * blob(p, 70)) + light(LOGE1, 0.55 * blob(p, 22) * fk)
        p = C['wotan'][f]
        out_ += light(mix(WOTAN, 0.4), 0.85 * blob(p, 22) + 0.3 * blob(p, 90)) + light(mix(STEEL, 0.3), 0.25 * blob(p, 7))
        out_ += light(GOLD, 0.95 * blob(p, 6)) + light(RED, 0.6 * blob(p + 9, 6) * (0.6 + 0.4 * tw(t)))
        for k, col in (('fricka', FRICKA), ('donner', BOLT)):
            p = C[k][f]
            out_ += light(mix(col, 0.55), 0.6 * blob(p, 20) + 0.15 * blob(p, 70))
        p = C['froh'][f]
        hh = (0.1 * (t + 80) + d / 400) % 1.0
        c = hue(hh)
        c = c * 0.45 + (c @ np.array([0.3, 0.59, 0.11]))[:, None] * 0.55
        out_ += ((0.6 * blob(p, 26)) ** 2.2)[:, None] * c
        for k, col, w in (('fasolt', FASOLT, 20), ('freia', FREIA, 13), ('fafner', FAFNER, 20)):
            p = C[k][f]
            out_ += light(col, 0.75 * blob(p, w) + 0.2 * blob(p, 2.5 * w))
        return out_

    for f in range(F):
        t = f * DT
        fr = np.zeros((G.N, 3))
        g = faded(t)
        landed = int(np.searchsorted(land, t, side='right'))
        heaped = landed / len(land)

        # the mountain: a dim dawn meadow on the wings, the castle's battlements across the porch
        u = 0.5 + 0.5 * np.sin(2 * np.pi * (d / 700 - 0.02 * (t + T0)))
        fr += light(DAWN0 + (DAWN1 - DAWN0) * u[:, None], (0.55 + 0.06 * slow(t + T0)) * wings)
        fr += light(CASTLE, (0.3 + 0.05 * slow(t + T0)) * mason * porch)

        # the gods on the wings, grey, warming a little as Freia comes; each tints its stretch of meadow
        for k, col, w in (('donner', DONNER, 24), ('fricka', FRICKA, 24)):
            p = C[k][f]
            c = grey(col, g)
            fr += light(c, 0.7 * np.exp(-((d - p) / w) ** 2) + 0.3 * np.exp(-((d - p) / 90) ** 2)
                        + (0.34 - 0.12 * g) * np.exp(-((d - p) / 170) ** 2))
        p = C['donner'][f]
        fr += light(grey(BOLT, g), 0.35 * np.exp(-((d - p) / 60) ** 2))
        p = C['froh'][f]
        bow = hue((d - p) / 90 + 0.15 * (t + T0)) * (1 - g) + np.full((G.N, 3), 0.55) * g
        fr += light(bow, 0.7 * np.exp(-((d - p) / 28) ** 2) + 0.3 * np.exp(-((d - p) / 90) ** 2)
                    + (0.34 - 0.12 * g) * np.exp(-((d - p) / 170) ** 2))

        # stamps: the giant who stamps flares, and the ground shakes out from him
        for ts, who in stamps:
            if ts <= t < ts + 1.2:
                p = C[who][int(ts / DT)]
                r = 30 + 420 * (t - ts) ** 0.7
                col = FAFNER if who == 'fafner' else FASOLT
                fr += light(col, 0.65 * (1 - (t - ts) / 1.2) * np.exp(-((np.abs(d - p) - r) / 45) ** 2))

        # the giants: big, slow lights
        for k, col in (('fasolt', FASOLT), ('fafner', FAFNER)):
            p = C[k][f]
            jolt = sum(np.exp(-(t - ts) / 0.2) for ts, w in stamps if w == k and ts <= t < ts + 1.0)
            fr += light(col, (0.75 + 0.3 * jolt) * np.exp(-((d - p) / 48) ** 2) + 0.3 * np.exp(-((d - p) / 130) ** 2))

        # Loge, flickering
        p = C['loge'][f]
        flick = 0.5 + 0.5 * np.sin(2 * np.pi * 3.3 * (t + T0)) * np.sin(2 * np.pi * 1.3 * (t + T0) + 1)
        lc = LOGE0 + (LOGE1 - LOGE0) * np.clip(0.5 + 0.4 * fl(t + T0), 0, 1)[:, None]
        fr += light(lc, (0.8 + 0.2 * flick) * np.exp(-((d - p) / 32) ** 2) * (0.75 + 0.25 * fl(t + T0))
                    + 0.25 * np.exp(-((d - p) / 100) ** 2))

        # while Fasolt looks for her eye, the world holds its breath
        hush = smoothstep(T_EYE - 1.0, T_EYE + 0.5, t) * (1 - smoothstep(T_RING - 0.5, T_RING + 0.5, t))
        fr *= 1 - 0.3 * hush

        # the heap and Freia in it; its gold warms the whole porch as it grows
        cov = 0.12 + 0.88 * heaped ** 0.85 + 0.2 * smoothstep(T_HELM, T_HELM + 2, t)
        fp = smoothstep(T_PLANT[0] - 1.2, T_PLANT[0] + 0.3, t)
        H = 32 + (HEAP - 32) * min(1.0, heaped * 1.25)
        band = smoothstep(H + 6, H - 6, np.abs(d - hc))
        covered = (thr < cov).astype(float)
        hit = recent(land, t, 0.25)
        press = recent(faf, t, 0.3)
        glint = (tw(t + T0) > 1.1).astype(float)
        hm = smoothstep(T_HELM - 0.3, T_HELM + 1.5, t)
        helm = hm * np.exp(-((d - hc) / 40) ** 4)
        heap = band * (covered + (1 - covered) * (1 - fp)) * (1 - 0.75 * helm)
        warm = (0.2 + 0.3 * heaped) * (1 - 0.5 * hush)
        fr += light(GOLD, (0.75 + 0.25 * hit + 0.3 * press) * heap + warm * np.exp(-((d - hc) / 260) ** 2) * porch)
        fr += light(HOT, (0.45 * hit + 0.45 * press) * heap * np.exp(-((d - hc) / 60) ** 2) + 0.55 * glint * heap)
        pinkb = 0.9 + 0.15 * recent(freias, t, 0.25)
        fr += light(FREIA, pinkb * band * (1 - covered) * fp)
        for tl in land:                                     # every lump sends a ripple of gold out over the porch
            if tl <= t < tl + 1.0:
                r = H + 420 * (t - tl) ** 0.6
                fr += light(GOLD, 0.55 * (1 - (t - tl)) * np.exp(-((np.abs(d - hc) - r) / 35) ** 2))
        ey = smoothstep(T_EYE - 0.5, T_EYE + 0.5, t)
        if ey > 0:
            lv = recent(loves, t, 0.35)
            beat = 0.75 + 0.25 * np.sin(2 * np.pi * t / 1.6)
            fr[eye] += light(FREIA, ey * (1.0 + 0.3 * lv) * beat)
            fr += light(FREIA, ey * (0.25 + 0.4 * lv) * np.exp(-((d - d[eye]) / 16) ** 2))
            for tl in loves:                                # each note of the love music: a pink ring from her eye
                if tl <= t < tl + 1.6:
                    r = 10 + 520 * ((t - tl) / 1.6) ** 0.7
                    fr += light(FREIA, ey * 0.55 * (1 - (t - tl) / 1.6) * np.exp(-((np.abs(d - d[eye]) - r) / 30) ** 2))

        # the helmet on top: a violet-grey shimmer settling over the pile
        if hm > 0:
            th = recent(tarn, t, 0.6, 5)
            sh = 0.5 + 0.5 * np.sin(2 * np.pi * (d / 26 - 0.6 * (t + T0)))
            fr += light(TARN, (0.75 + 0.25 * sh + 0.3 * th) * helm)
            fr += light(TARN, 0.7 * th * np.exp(-((d - hc) / (60 + 260 * (1 - th))) ** 2))

        # Freia, walking in between the giants (before she is set down)
        if fp < 1:
            p = C['freia'][f]
            fl_ = recent(freias, t, 0.2)
            fr += light(FREIA, (1 - fp) * ((0.85 + 0.25 * fl_) * np.exp(-((d - p) / 24) ** 2)
                                            + 0.35 * np.exp(-((d - p) / 80) ** 2)))
            for off, col in ((-16, APPLE), (14, LEAF)):
                fr += light(col, (1 - fp) * 0.55 * np.exp(-((d - p - off) / 6) ** 2))

        # the staves, planted at the ends of the pile
        for tp, off, col in ((T_PLANT[0], -HEAP - 8, FASOLT), (T_PLANT[1], HEAP + 8, FAFNER)):
            s = smoothstep(tp - 0.05, tp + 0.05, t)
            if s > 0:
                fr += light(col, s * (1.0 + 0.6 * np.exp(-(t - tp) / 0.3)) * np.exp(-((d - hc - off) / 5) ** 2))
                fr += light(WHITE, s * 0.7 * np.exp(-(t - tp) / 0.25) * np.exp(-((d - hc - off) / 40) ** 2))
        if press > 0:                                       # Fafner's demand: his ochre presses in on the pile
            p = C['fafner'][f]
            fr += light(FAFNER, 0.6 * press * np.exp(-((d - p) / 260) ** 2) * (np.abs(d - hc) > H))

        # the lumps of gold in flight: comets along the roofline
        for tl, p0 in lumps:
            s = (t - (tl - FLIGHT)) / FLIGHT
            if not 0 <= s <= 1.0:
                continue
            tgt = hc + np.sign(p0 - hc) * H
            for j in range(7):
                sj = max(s - 0.045 * j, 0)
                q = p0 + (tgt - p0) * (sj * sj * (3 - 2 * sj))
                fr += light(GOLD if j else HOT, (1.0 - 0.13 * j) * np.exp(-((d - q) / (11 + 3 * j)) ** 2))

        # Wotan and the ring on his hand; the refusal floods the house red, and the spear strikes out
        p = C['wotan'][f]
        fr += light(WOTAN, 0.8 * np.exp(-((d - p) / 28) ** 2) + 0.3 * np.exp(-((d - p) / 90) ** 2))
        rp = recent(rings, t, 0.3)
        rf = smoothstep(T_REFUSE - 0.05, T_REFUSE + 0.05, t) * (1 - smoothstep(T_REFUSE + 1.0, T_REFUSE + 5.0, t))
        rr = p + 10
        fr += light(GOLD, (0.95 + 0.35 * rp) * np.exp(-((d - rr) / 6) ** 2))
        fr += light(RED, (0.55 + 0.35 * rp + 0.45 * rf) * np.exp(-((d - rr - 6) / 4) ** 2))
        if T_RING <= t < T_REFUSE:
            fr += light(GOLD, 0.45 * rp * np.exp(-((d - rr) / 70) ** 2))
        if rf > 0.01:
            spread = 80 + 520 * smoothstep(T_REFUSE, T_REFUSE + 1.2, t)
            fr += light(RED, rf * (0.95 * np.exp(-((d - rr) / spread) ** 2) + 0.4 + 0.25 * porch))
            fr += light(HOT, 0.8 * np.exp(-(t - T_REFUSE) / 0.2) * np.exp(-((d - rr) / 120) ** 2))
        if T_REFUSE <= t < T_RAGE + 4:
            ns = int(np.searchsorted(spears, t, side='right'))
            far = p - (p - pl1) * ns / len(spears)          # down Porch Left toward the street, a note at a time
            line = ((d <= p) & (d >= far)).astype(float)
            fade_ = 1 - smoothstep(T_RAGE + 1, T_RAGE + 4, t)
            sp = recent(spears, t, 0.18)
            fr += light(STEEL, fade_ * (0.6 + 0.35 * sp) * line)
            fr += light(WHITE, fade_ * sp * np.exp(-((d - far) / 14) ** 2))
        if t < T_HANDOVER:                                  # the first seconds still look like Alberich's Curse
            s = smoothstep(0.0, T_HANDOVER, t)
            fr = s * fr + (1 - s) * curse_look(t, f)
        out[f] = fr
    return np.clip(out, 0, 1)


def score(M, G):
    """Wagner's notes, orchestrated from the piano reduction, with the staging's sounds over them."""
    order = np.argsort(G.pd)
    xs, ds = G.pos[order, 0], G.pd[order]
    x0, x1 = xs.min(), xs.max()

    def pan_at(dd):
        x = np.interp(dd, ds, xs)
        return float(0.85 * (2 * (x - x0) / (x1 - x0) - 1))

    C = choreography(G)
    hc = pan_at(at(G, 'Porch Front', 0.5))

    def pan_of(who, t):
        return pan_at(np.interp(t, C['t'], C[who]))

    o = Orchestra(M, level=2.6)

    def role(t, d, m, v, h):
        if t < SEG[1]:                                  # the giants' tread under Freia's music
            if h == 1:
                return [('tuba', 0, 6, 0.8), ('trombones', 12, -4, 0.45), ('basses', 0, 0, 0.5)]
            return [('violins', 0, 10, 0.55), ('flutes', 0, -4, 0.35)] if m >= 60 else None
        if t < SEG[2]:                                  # the heaping: falling octaves
            if h == 1:
                return [('cellos', 0, 34, 0.6), ('bassoons', 0, 26, 0.45), ('horns', 0, 22, 0.45 if m >= 41 else 0)]
            return [('violins' if m >= 55 else 'violas', 0, 28, 0.45), ('clarinets', 0, 18, 0.3)]
        if t < SEG[3]:                                  # the love music under her eye
            if h == 1:
                return [('cellos', 0, 26, 0.7), ('horns', 0, 16, 0.5)]
            return [('violins', 0, 26, 0.55), ('flutes', 0, 6, 0.3 if m >= 72 else 0)]
        if t >= T_REFUSE - 0.05 and h == 1:             # the spear's falling scale
            return [('trombones', 0, 30, 0.8), ('tuba', 0, 26, 0.6 if m < 48 else 0), ('basses', 0, 20, 0.4)]
        if T_PLEA <= t < T_PLEA + 1.8 and h == 0:       # Donner's plea: trumpets on top
            return [('trumpets', 0, 0, 0.6), ('horns', -12, -4, 0.5), ('violins', 0, 0, 0.45)]
        return None

    o.tutti(tidy(EX['notes']), size=lambda t: 1.0 if t >= SEG[3] else 0.6, role=role)

    N = compose()
    o.effects([(0.0, 0.0), (SEG[2] - 1.0, 0.0), (SEG[2] + 0.5, -14.0), (SEG[3] - 0.5, -14.0), (SEG[3] + 0.5, -2.0)])
    for t, d, m, v, part, who in N:
        if part == 'stamp':                             # the giants' footfalls
            big = t >= T_RAGE
            o.hit('bass drum', t, 116 if big else 100, gain=0.5 if big else 0.32, pan=pan_of(who, t))
            if big or who == 'fafner':
                o.hit('timpani', t, 110, pitch=-7, gain=0.35, pan=pan_of(who, t))
        elif part == 'plant':                           # the staves driven in
            o.boom(t, pan_of(who, t), 0.8)
            o.hit('brake drum', t + 0.01, 104, gain=0.25, pan=pan_of(who, t))
        elif part == 'lump':                            # gold landing on the pile
            o.play('glock', 84 + (int(t * 7) % 5) * 2, t, 0.1, 70, hc, 0.28)
            o.hit('metal', t, 64, gain=0.12, pan=hc)
    for t0 in FAF:                                      # Fafner stamps up and packs it down
        for k in range(3):
            o.hit('bass drum', t0 + 0.5 * k, 118, gain=0.5, pan=pan_of('fafner', t0))
        o.hit('scrape', t0 + 1.0, 96, gain=0.25, pan=hc)
    o.hit('gong scrape', T_HELM, 108, gain=0.5, pan=hc)      # the helmet on top
    o.hit('triangle', T_HELM + 0.6, 80, gain=0.3, pan=hc)
    pw = pan_of('wotan', T_REFUSE)
    o.boom(T_REFUSE, pw, 1.0)                           # Wotan refuses
    o.hit('crash', T_REFUSE, 122, gain=0.6, pan=pw)
    o.clash(T_REFUSE + 0.02, pw, 110, 0.6)
