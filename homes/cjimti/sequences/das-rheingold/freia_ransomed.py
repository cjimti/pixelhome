"""Freia Ransomed: the giants bring Freia back up the mountain. They stamp in from the free end of Right to
their own motif (Donington 58) in the tubas, Freia's pink between them while her joyful theme (Donington 7)
floats over them in the violins, and as she comes near, the grey gods on the wings get a little of their
colour back. Wotan steps aside, Loge slips off to Porch Left, and she is set down on the hoard at the back of
the porch. Two thuds: the giants plant their staves on either side of her, one grey, one ochre.

Then the gold is heaped up to hide her. The Gold's call (Donington 44) sounds six times, climbing, on horns
and then trumpets, and every note is a lump of gold that Loge, Donner or Froh flings across the house: a comet
along the roofline that lands on the pile with a flash and a clink. The heap grows round the pink, from the
edges in, until only flecks of her show; twice Fafner stamps up and orders it packed tighter (the giants'
authority, Donington 59), and the pile flares as it is pressed down. Loge throws on the last thing in the
hoard, the helmet Mime forged (the Tarnhelm, Donington 18), and a violet-grey shimmer settles on top.

But Fasolt, coming close, can still see her eye through a gap: one pink glint inside the gold, pulsing with
Freia's love music (Donington 6) on a solo violin. Fafner points at the only gold left to fill it, the ring on
Wotan's hand, and the Ring motif (Donington 8) grinds out in the tubas while the small gold point on Wotan
throbs. Wotan refuses: the ring flares red across the porch and his spear's descending scale (Donington 73)
comes down on the trombones, a steel line striking out along Porch Left note by note. The giants stamp in
outrage, the gods' colours shrink back toward grey, and the standoff hangs on a tremolo.

compose() holds every note, choreography() every position; render() and score() read both."""
import numpy as np
from pixelhome.audio import note
from pixelhome.fx import DT, hexc, light, smoothstep, nframes, Flicker
from pixelhome.leitmotifs import MOTIFS, play

CODE = 'RG21'
TITLE = 'Freia Ransomed'
KIND = 'show'
DESCRIPTION = ('The giants bring Freia back and plant their staves around her, and the gods heap up the gold '
               'until she is hidden. But one giant can still see her eye through a gap, and there is only one '
               'thing left to fill it: the ring on Wotan\'s hand.')
VOICEOVER = ('Freia comes home, but only as far as the gold. '
             'Pile it high enough to hide her, the giants say, and she is yours again.')

BEAT = 0.5                                  # a quarter note at 120
GSTEP = 0.6                                 # the giants' tread
T_WALK = 0.4
T_FREIA = [1.0, 5.4]
T_PLANT = [9.4, 10.6]
GOLD_CALLS = [(13.0, 0), (17.5, 2), (22.0, 4), (30.0, 5), (34.5, 7), (39.0, 7)]
FAF = [26.2, 43.4]                          # Fafner: pack it tighter!
T_HELM = 48.0                               # the helmet on top
T_EYE = 53.4                                # Fasolt sees her eye
T_RING = 61.0                               # Fafner demands the ring
T_REFUSE = 66.6                             # Wotan refuses: the spear
T_RAGE = 71.6
STAMPS_RAGE = [71.6, 72.6, 73.6, 74.4]
T_HANDOVER = 5.0                            # seconds to grow out of the last scene's look
D = 80.0
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
    """Every note: (time, seconds, midi, velocity, part, who). who names the thrower for 'gold' notes."""
    N = []

    def add(t, d, m, v, part, who=None):
        N.append((float(t), float(d), note(m) if isinstance(m, str) else int(m), int(v), part, who))

    # the giants tread in, Freia's theme over them (in C, as the giants are)
    for t, m, v, d in play('giants', T_WALK, GSTEP, -12, 100):
        add(t, d, m, v, 'giants')
    for k in range(12):
        add(T_WALK + k * GSTEP, 0.4, 'C2' if k % 2 == 0 else 'G1', 104 if k % 2 == 0 else 92, 'stamp',
            'fafner' if k % 2 == 0 else 'fasolt')
    for i, t0 in enumerate(T_FREIA):
        for t, m, v, d in play('freia', t0, 0.55, -2, 84 + 8 * i):
            add(t, d, m, v, 'freia' if m >= note('C4') else 'freialow')
    add(0.0, T_PLANT[0], 'C2', 62, 'pedal')
    for i, tp in enumerate(T_PLANT):
        add(tp, 0.8, 'C1' if i == 0 else 'G0', 124, 'plant', ('fasolt', 'fafner')[i])

    # the gold heaped up: each note of its call is one lump, flung by Loge, Donner or Froh in turn
    k = 0
    for i, (t0, tr) in enumerate(GOLD_CALLS):
        inst = 'horn' if i < 3 else 'trumpet'
        for t, m, v, d in play('gold', t0, BEAT, tr, 86 + 5 * i):
            add(t, d, m + (12 if inst == 'trumpet' else 0), v, inst, THROWERS[k % 3])
            if inst == 'trumpet':
                add(t, d, m, v - 14, 'horn')
            add(t, 0.3, m + 24, 60 + 4 * i, 'clink')
            k += 1
        root = note('G2') + tr
        for m in (root, root + 7, root + 12, root + 16):
            add(t0 - 0.2, 4.2, m, 64 + 4 * i, 'chord')
        add(t0 - 0.9, 0.8, root + 12, 84, 'gliss')
        for j in range(7):                                  # the pile's pulse: low strings in the giants' rhythm
            add(t0 + j * BEAT, BEAT * 0.6, root - 12, 80 + 6 * (j % 2 == 0), 'pulse')
    for t0 in FAF:
        for t, m, v, d in play('giants_authority', t0, BEAT, -12, 108):
            if t < t0 + 4.0:
                add(t, d, m, v, 'faf')
        for b in (0, 2, 4):
            add(t0 + b * BEAT, 0.5, 'C2', 118, 'stamp', 'fafner')

    # the last of the hoard: Loge tosses on the helmet
    for t, m, v, d in play('loge_flicker', T_HELM - 1.6, 0.4, -12, 90):
        add(t, d, m, v, 'loge')
    for t, m, v, d in play('tarnhelm', T_HELM, 0.6, 0, 76):
        if t < T_HELM + 4.6:
            add(t, d, m, v, 'tarn')

    # her eye through a gap: Freia's love, on a solo violin
    for t, m, v, d in play('freia_love', T_EYE, 0.8, -2, 82):
        add(t, d, m, v, 'love' if m >= note('C4') else 'lovelow')
    for b, d, m in ((0, 1, 'E3'), (1, .5, 'D3'), (1.5, .5, 'C3'), (2, 2, 'G2'), (4, 1, 'A2'), (5, 3, 'C3')):
        add(T_EYE + 5.2 + b * 0.5, d * 0.5, m, 70, 'fasolt')

    # Fafner wants the ring; Wotan's refusal on the spear
    for t, m, v, d in play('ring', T_RING, 0.55, -12, 104):
        add(t, d, m, v, 'ring')
    for t, m, v, d in play('spear', T_REFUSE, 0.42, 0, 116):
        add(t, d, m, v, 'spear')
    add(T_REFUSE, 1.5, 'Bb1', 124, 'flare')

    # the giants' outrage, and the standoff
    for t, m, v, d in play('giants', T_RAGE - 8 * 0.5, 0.5, -12, 110):
        if t >= T_RAGE:
            add(t, d, m, v, 'giants')
    for i, ts in enumerate(STAMPS_RAGE):
        add(ts, 0.5, 'C2', 120, 'stamp', ('fafner', 'fasolt')[i % 2])
    for m in ('C3', 'Eb3', 'G3', 'C4'):
        add(75.0, D - 75.0, m, 74, 'trem')
    add(76.5, D - 76.5, 'C2', 86, 'roll')
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
        if part in ('horn', 'trumpet') and who is not None:
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
        fr *= 1 - 0.55 * hush

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
    from pixelhome.audio import SR, whoosh
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

    for name, gain, rev in (('strings', 0.14, 0.32), ('solo', 0.2, 0.35), ('low', 0.16, 0.15),
                            ('brass', 0.16, 0.28), ('winds', 0.15, 0.3), ('perc', 0.2, 0.22), ('harp', 0.17, 0.4),
                            ('glock', 0.07, 0.4), ('fx', 0.08, 0.25)):
        M.bus(name, gain=gain, reverb=rev)
    vn = M.sampler('Strings/Violin Section/susVib/*.wav', tune=-12)
    va = M.sampler('Strings/Viola Section/susvib/*.wav', tune=-12)
    vc = M.sampler('Strings/Cello Section/susvib/*.wav', tune=-12)
    vcs = M.sampler('Strings/Cello Section/spic/*.wav', tune=-12)
    vtrem = M.sampler('Strings/Violin Section/Trem/*.wav', tune=-12)
    trem = M.sampler('Strings/Cello Section/trem/*.wav', tune=-12)
    cb = M.sampler('Strings/Solo Contrabass/SusNV/*.wav', tune=-12)
    pizz = M.sampler('Strings/Solo Contrabass/Pizz/*.wav', tune=-12)
    solo = M.sampler('Strings/Solo Violin/Arco Vib/*.wav', tune=-12)
    fl = M.sampler('Woodwinds/Flute/susvib/*.wav', tune=-12)
    pic = M.sampler('Woodwinds/Piccolo/Stac/*.wav', tune=-12)
    horn = M.sampler('Brass/F Horn/sus/*.wav', tune=-12)
    mute = M.sampler('Brass/F Horn/mute/*.wav', tune=-12)
    tpt = M.sampler('Brass/Trumpet/sus/*.wav', tune=-12)
    tbn = M.sampler('Brass/Tenor Trombone/sus/*.wav', tune=-12)
    tuba = M.sampler('Brass/Tuba/sus/*.wav', tune=-12)
    glock = M.sampler('Percussion/Glock/*.wav', tune=-12)
    harp = M.sampler('Strings/Harp/*.wav')
    timp = M.hits('Percussion/Timpani/Timpani1_Hit*.wav')
    roll = M.hits('Percussion/Timpani/Rolls/*.wav')
    bd = M.hits('Percussion/BDrumNewhit_v[4-7]*.wav')
    crash = M.hits('Percussion/cymbal-crash1_f*.wav')
    gong = M.hits('Percussion/gongHit_f*.wav')

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

    for t, d, m, v, part, who in compose():
        if part == 'giants':
            pg = pan_of('fafner', t)
            M.add('brass', tuba.play(m, v, dur=d * 1.05, release=0.2), t, 1.2, pg)
            M.add('brass', tbn.play(m + 12, v - 8, dur=d * 1.05, release=0.2), t, 0.8, pan_of('fasolt', t))
        elif part == 'stamp':
            p = pan_of(who, t)
            M.add('perc', timp.play(v, pitch=-4 if who == 'fafner' else -1), t, 0.9, p)
            M.add('perc', bd.play(v - 10), t, 0.6, p)
            M.add('low', pizz.play(m + 12, v), t, 0.7, p)
        elif part == 'freia':
            p = pan_of('freia', t)
            M.add('strings', vn.play(m + 12, v, dur=d * 1.05, release=0.25), t, 0.9, p)
            M.add('winds', fl.play(m + 12, v - 16, dur=d * 1.05, release=0.25), t, 0.5, p)
        elif part == 'freialow':
            M.add('low', pizz.play(m + 12, v - 10), t, 0.6, pan_of('freia', t))
        elif part == 'pedal':
            hold('low', cb, m, t, t + d, v, 0.0, rise=1.5, fall=1.0, gain=0.7)
        elif part == 'plant':
            p = pan_of(who, t)
            M.add('perc', timp.play(v, pitch=-6), t, 1.0, p)
            M.add('perc', bd.play(v), t, 0.9, p)
            M.add('brass', tuba.play(m + 12, v, dur=d, release=0.3), t, 0.9, p)
        elif part == 'horn':
            M.add('brass', horn.play(m, v, dur=d, release=0.35), t, 0.95, hc - 0.15)
            if who is not None:
                M.add('fx', whoosh(FLIGHT, 600, 3000, 0.4, seed=int(t * 10)), t - FLIGHT, 0.5,
                      pan_of(who, t - FLIGHT))
        elif part == 'trumpet':
            M.add('brass', tpt.play(m, v, dur=d, release=0.35), t, 0.9, hc + 0.15)
            M.add('fx', whoosh(FLIGHT, 600, 3000, 0.4, seed=int(t * 10)), t - FLIGHT, 0.5, pan_of(who, t - FLIGHT))
        elif part == 'clink':
            M.add('glock', glock.play(m, v), t, 1.0, hc)
        elif part == 'chord':
            s = vn if m >= note('G4') else va if m >= note('C3') else vc
            hold('strings', s, m, t, t + d, v, 0.0, rise=0.5, fall=0.8, gain=0.6)
        elif part == 'gliss':
            gl = [x for x in range(m - 12, m + 13) if (x - m) % 12 in (0, 4, 7)]
            for i, x in enumerate(gl):
                M.add('harp', harp.play(x, 86 + i), t + i * d / len(gl), 1.0, -0.6 + 1.2 * i / len(gl))
        elif part == 'pulse':
            M.add('low', vcs.play(m + 12, v), t, 0.7, hc)
            M.add('low', pizz.play(m + 12, v - 10), t, 0.6, hc)
        elif part == 'faf':
            p = pan_of('fafner', t)
            M.add('brass', tuba.play(m, v, dur=d * 1.05, release=0.2), t, 1.0, p)
            M.add('brass', tbn.play(m + 12, v - 10, dur=d * 1.05, release=0.2), t, 0.7, p)
        elif part == 'loge':
            M.add('winds', pic.play(m, v), t, 0.9, pan_of('loge', t))
        elif part == 'tarn':
            M.add('brass', mute.play(m, v, dur=d, release=0.6), t, 0.8, hc)
            hold('strings', vtrem, m, t, t + d, v - 10, hc, rise=0.6, fall=0.8, gain=0.4)
        elif part == 'love':
            M.add('solo', solo.play(m + 12, v, dur=d * 1.1, release=0.35), t, 1.0, hc + 0.1)
            M.add('winds', fl.play(m, v - 20, dur=d * 1.1, release=0.35), t, 0.4, hc + 0.1)
        elif part == 'lovelow':
            hold('strings', va if m >= note('C3') else vc, m, t, t + d, v - 14, hc, rise=0.4, fall=0.6, gain=0.6)
        elif part == 'fasolt':
            M.add('brass', tbn.play(m, v, dur=d, release=0.3), t, 0.8, pan_of('fasolt', t))
        elif part == 'ring':
            p = pan_of('fafner', t)
            if m >= note('C3'):
                M.add('brass', tbn.play(m, v, dur=d * 1.05, release=0.3), t, 1.1, p)
                M.add('brass', horn.play(m + 12, v - 10, dur=d * 1.05, release=0.3), t, 0.8, p)
            else:
                M.add('brass', tuba.play(m, v, dur=d, release=0.4), t, 1.2, p)
                hold('low', cb, m + 12, t, t + d, v - 10, p, rise=0.5, fall=0.8, gain=0.9)
        elif part == 'spear':
            p = pan_of('wotan', t)
            M.add('brass', tbn.play(m, v, dur=d * 1.05, release=0.25), t, 1.4, p)
            M.add('brass', horn.play(m + 12, v - 8, dur=d * 1.05, release=0.25), t, 0.9, p)
            M.add('brass', tuba.play(m - 12, v - 6, dur=d * 1.05, release=0.25), t, 1.1, p)
            M.add('low', vc.play(m, v, dur=d, release=0.2), t, 0.9, p)
        elif part == 'flare':
            p = pan_of('wotan', t)
            M.add('perc', gong.play(v), t, 0.8, p)
            M.add('perc', crash.play(v), t, 0.7, p)
            M.add('perc', timp.play(v, pitch=-5), t, 0.9, p)
        elif part == 'trem':
            hold('strings', vtrem if m >= note('C4') else trem, m, t, t + d, v, 0.0, rise=1.0, fall=1.2, gain=1.1)
        elif part == 'roll':
            M.add('perc', roll.play(v, dur=d + 0.5), t, 0.9, 0.0)
