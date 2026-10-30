"""Fafner Strikes: Freia is free and the gods are bright again, but the gold is the giants' now. Fafner stamps
up to the pile to his motif (Donington 58) in the tubas and starts stuffing it into his sack: with every heavy
note a lump of gold flies off the heap into his ochre light, and the pile shrinks from the edges in.

Fasolt wants the ring. The two giants quarrel in the motif of their authority (Donington 59), Fasolt on the
trombones, Fafner on the tubas, each phrase a step higher and quicker, and each one a shove: their lights slam
together over the gold in a burst of grey and ochre. Fasolt snatches the ring (the small gold point with its red
glint jumps to his grey light). Fafner draws back, his light gathering over a timpani roll, and strikes him
with his staff: a flash across the whole house, a gong, and Fasolt's grey light shatters into fragments that
spray along the roofline and go out. Two more blows, smaller, where he fell.

Then the Curse motif (Donington 13), fortissimo in the trombones over a G flat pedal: Alberich swore the ring
would bring death to whoever held it, and here is the first. Fafner wrenches the ring from his brother, and with
every note of the curse a pulse of deep red runs out from the ring across the house while the mountain shadows
and the gods turn pale. Fafner gathers the rest of the hoard and the helmet into his light to his own creeping
chromatic motif (Donington 57), and stamps off down Porch Right and out of the free end of Right, a trail of
gold glinting behind him, each step shaking the roofline. The gods stand horrified; Fricka goes to Wotan,
Freia to the empty place where the gold was, and the curse sounds once more, softly, on a muted horn. Heavy
grey-blue storm air begins to gather over the mountain, and far off a horn hints at Donner's call.

compose() holds every note, choreography() every position; render() and score() read both."""
import numpy as np
from pixelhome.audio import note
from pixelhome.fx import DT, hexc, light, smoothstep, nframes, Flicker
from pixelhome.leitmotifs import MOTIFS, play

CODE = 'RG23'
TITLE = 'Fafner Strikes'
KIND = 'show'
DESCRIPTION = ('The giants quarrel over the ring, and Fafner strikes his brother dead with one blow. The curse '
               'on the ring has claimed its first victim. Fafner carries off the gold, and the gods are left '
               'staring after him as a storm gathers.')
VOICEOVER = ('Two brothers, one ring, and only one of them walks away. '
             'Alberich said the ring would bring death. He was right.')

GBEAT = 0.55                                # the giants' tread while Fafner fills his sack
T_GATHER = 2.0
QUARREL = [(11.4, 0.5, 0, 'fasolt'), (13.6, 0.48, 1, 'fafner'), (15.7, 0.45, 2, 'fasolt'),
           (17.6, 0.42, 3, 'fafner'), (19.4, 0.38, 5, 'fasolt'), (20.9, 0.35, 6, 'fafner')]
T_GRAB = 22.5                               # Fasolt snatches the ring
T_WIND = 23.6                               # Fafner draws back
STRIKES = [25.5, 26.4, 27.2]
T_CURSE = 28.5
CBEAT = 0.6
T_TAKE = 30.0                               # Fafner wrenches the ring from him
T_HOARD = 41.0                              # he gathers the rest
FBEAT = 0.7
T_EXIT = 47.0                               # and stamps off
STEPS = [T_EXIT + 0.72 * k for k in range(19)]
T_HORROR = 61.0
T_STORM = 63.0
D = 80.0
T0 = 160.0                                  # the opera's clock at our start: steady motion carries across the cuts

HEAP = 92

GOLD = hexc('#ffaa00')
HOT = hexc('#fff0a0')
FREIA = hexc('#ff5a9a')
APPLE = hexc('#ffd040')
LEAF = hexc('#60d020')
WOTAN = hexc('#1a3cff')
RED = hexc('#ff1800')
BLOOD = hexc('#600808')
FASOLT = hexc('#8090a0')
FAFNER = hexc('#c07a10')
FRICKA = hexc('#ff9ad0')
DONNER = hexc('#ffffff')
BOLT = hexc('#a0c0ff')
LOGE0, LOGE1 = hexc('#ff5000'), hexc('#ffb020')
TARN = hexc('#5a4a8a')
CASTLE = hexc('#fff0c0')
DAWN0, DAWN1 = hexc('#2a3a6a'), hexc('#6a5a8a')
MIST0, MIST1 = hexc('#2a3650'), hexc('#5a6a88')
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
    """The gods pale with horror at the killing."""
    return 0.5 * smoothstep(STRIKES[0], T_CURSE + 4, t) - 0.15 * smoothstep(T_HORROR, D, t)


def remains(t):
    """How much of the hoard is still on the heap."""
    return 1 - 0.4 * smoothstep(T_GATHER, T_GATHER + 9, t) - 0.6 * smoothstep(T_HOARD, T_HOARD + 5, t)


def storm(t):
    return smoothstep(T_STORM, D - 2, t)


def billow(d, t):
    """Storm air: slow, smooth banks of mist drifting along the roofline (t: seconds since it began to gather)."""
    return (0.5 + 0.3 * np.sin(2 * np.pi * (d / 330 - 0.035 * t)) + 0.2 * np.sin(2 * np.pi * (d / 140 + 0.06 * t) + 1.3))


def compose():
    """Every note: (time, seconds, midi, velocity, part, who)."""
    N = []

    def add(t, d, m, v, part, who=None):
        N.append((float(t), float(d), note(m) if isinstance(m, str) else int(m), int(v), part, who))

    for m in ('D3', 'A3', 'D4', 'Gb4'):                     # Freia's D major, still ringing as the giants move
        add(0.0, 3.0, m, 74, 'chord')
    for m in ('C2', 'G2'):                                  # and under the gathering, a low open fifth
        add(T_GATHER, QUARREL[0][0] - T_GATHER, m, 76, 'bed')
    # Fafner fills his sack: each long note of the giants' motif is a scoop of gold
    for t, m, v, d in play('giants', T_GATHER, GBEAT, -12, 100):
        add(t, d, m, v, 'giants', 'fafner')
        if d >= 0.3 * GBEAT:
            add(t, 0.4, m + 24, 70, 'scoop', 'fafner')
    for k in range(int((QUARREL[0][0] - T_GATHER) / (2 * GBEAT))):
        add(T_GATHER + k * 2 * GBEAT, 0.4, 'C2', 96, 'stamp', 'fafner')

    # the quarrel: phrases of the giants' authority, a step higher and quicker each time, each one a shove
    for t0, b, tr, who in QUARREL:
        for t, m, v, d in play('giants_authority', t0, b, tr - 12, 104 + 2 * tr):
            if t < t0 + 6 * b:
                add(t, d, m, v, 'quarrel', who)
        add(t0, 0.5, 'C2', 112 + tr, 'shove', who)
    for t, m, v, d in play('ring', T_GRAB, 0.4, -12, 108):
        if t < T_GRAB + 1.5 and m >= note('C3'):
            add(t, d, m, v, 'grab', 'fasolt')
    add(T_WIND, STRIKES[0] - T_WIND, 'Gb2', 100, 'wind')
    for k in range(10):
        add(T_WIND + k * 0.19, 0.2, note('Gb3') + k, 80 + 4 * k, 'rise')
    for i, ts in enumerate(STRIKES):
        add(ts, 1.5, 'Gb1', 127 - 10 * i, 'strike' if i == 0 else 'blow', 'fafner')

    # the curse
    for t, m, v, d in play('curse', T_CURSE, CBEAT, 0, 118):
        add(t, d, m, v, 'curse' if m >= note('C3') else 'cursepedal')
    for k in range(5):
        add(T_CURSE + k * 4 * CBEAT, 0.6, 'Gb2', 116, 'timp')

    # Fafner gathers the hoard and stamps away
    for t, m, v, d in play('fafner', T_HOARD, FBEAT, 0, 104):
        add(t, d, m, v, 'fafmotif', 'fafner')
    for k in range(10):
        add(T_HOARD + k * 0.5, 0.4, note('G5') + (k * 5) % 12, 64, 'scoop', 'fafner')
    for i, ts in enumerate(STEPS):
        add(ts, 0.5, 'C2' if i % 2 == 0 else 'G1', 110 - 2 * max(0, i - 10), 'stamp', 'fafner')

    # horror, and the storm air
    for t, m, v, d in play('curse', T_HORROR, 0.7, 0, 74):
        if t < T_HORROR + 8 * 0.7:
            add(t, d, m, v, 'echo' if m >= note('C3') else 'echopedal')
    for m in ('Bb1', 'Bb2', 'Db3', 'F3'):
        add(T_STORM, D - T_STORM, m, 60, 'mist')
    for ts in (68.0, 74.0):
        add(ts, 3.0, 'Bb1', 76, 'rumble')
    for t, m, v, d in play('donner', 76.4, 0.6, 0, 66):
        if t < 79.0:
            add(t, d, m, v, 'distant')
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
    """Per frame: where everyone is (path distance) and where the ring is."""
    F = nframes(D)
    t = np.arange(F) * DT
    hc = at(G, 'Porch Front', 0.5)
    who = ['wotan', 'loge', 'freia', 'fasolt', 'fafner', 'donner', 'fricka', 'froh', 'ring']
    tgt = {k: np.zeros(F) for k in who}
    rate = {k: np.full(F, 3.0) for k in who}

    def set_(k, a, b, where, r):
        m = (t >= a) & (t < b)
        tgt[k][m] = where if np.ndim(where) == 0 else where[m]
        rate[k][m] = r

    set_('wotan', 0, D, at(G, 'Porch Front', 0.12), 3.0)
    set_('wotan', T_HORROR + 1, D, at(G, 'Porch Front', 0.4), 1.2)
    jit = 8 * np.sin(2 * np.pi * (t + T0) * 1.7) + 5 * np.sin(2 * np.pi * (t + T0) * 3.1)
    set_('loge', 0, D, at(G, 'Porch Left', 0.75), 3.0)
    set_('donner', 0, D, at(G, 'Left', 0.3), 3.0)
    set_('donner', T_STORM, D, at(G, 'Left', 0.5), 1.1)
    set_('fricka', 0, D, at(G, 'Left', 0.7), 3.0)
    set_('fricka', T_HORROR, D, at(G, 'Porch Front', 0.25), 1.2)
    set_('freia', 0, D, at(G, 'Left', 0.5), 3.0)
    set_('freia', T_HORROR + 1.5, D, at(G, 'Porch Front', 0.6), 1.15)
    set_('froh', 0, D, at(G, 'Right', 0.7), 3.0)
    set_('froh', T_EXIT + 8, D, at(G, 'Right', 0.6), 1.2)
    FS0, FF0 = at(G, 'Porch Right', 0.2) + 20, at(G, 'Porch Right', 0.55) - 30

    # Fafner to the pile; the quarrel shoves them back and forth over it
    set_('fafner', 0, D, FF0, 3.0)
    set_('fasolt', 0, D, FS0, 3.0)
    set_('fafner', T_GATHER - 0.5, D, hc + HEAP + 20, 1.5)
    set_('fasolt', QUARREL[0][0] - 1.5, D, hc + HEAP + 80, 1.8)
    set_('fafner', QUARREL[0][0] - 1.5, D, hc + 40, 1.8)
    for t0, b, tr, w in QUARREL:
        push = 1 if w == 'fasolt' else -1                   # the one who sings shoves the other
        set_('fasolt', t0, t0 + 0.4, hc + 60 + 20 * push, 9.0)
        set_('fafner', t0, t0 + 0.4, hc + 10 + 30 * push, 9.0)
        set_('fasolt', t0 + 0.4, t0 + 1.8, hc + HEAP + 80 - 20 * push, 3.0)
        set_('fafner', t0 + 0.4, t0 + 1.8, hc + 30 - 20 * push, 3.0)
    S = hc + 175                                            # where Fasolt falls
    set_('fasolt', T_GRAB, D, S, 4.0)
    set_('fafner', T_GRAB, T_WIND, hc + 70, 3.0)
    set_('fafner', T_WIND, STRIKES[0] - 0.12, hc + 20, 1.5)  # drawing back
    for ts in STRIKES:
        set_('fafner', ts - 0.12, ts + 0.3, S - 45, 14.0)
        set_('fafner', ts + 0.3, ts + 0.75, S - 90, 6.0)
    set_('fafner', STRIKES[-1] + 0.6, T_HOARD, S - 60, 2.0)
    set_('fafner', T_HOARD, T_EXIT, hc + 60, 1.5)
    out_ = G.length + 90
    lurch = np.clip(np.searchsorted(np.array(STEPS), t, side='right') - 1, 0, len(STEPS) - 1)
    k_ = lurch + smoothstep(0, 0.3, t - np.array(STEPS)[lurch])
    walk = hc + 60 + (out_ - hc - 60) * np.clip(k_ / len(STEPS), 0, 1)
    set_('fafner', T_EXIT, D, walk, 9.0)

    # the ring: on the heap; snatched by Fasolt; wrenched away by Fafner; carried off
    pos = {k: follow(tgt[k], rate[k]) for k in who if k != 'ring'}
    ring = np.where(t < T_GRAB, hc + 44, np.where(t < T_TAKE, pos['fasolt'] + 8, pos['fafner'] + 10))
    pos['ring'] = follow(ring, np.full(F, 14.0))
    pos['loge'] = pos['loge'] + jit                        # the flicker on top of where he stands
    pos['t'] = t
    return pos


def render(G, seed=23):
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
    scoops = [e[0] for e in N if e[4] == 'scoop']
    stamps = np.array([e[0] for e in N if e[4] in ('stamp', 'shove')])
    shoves = [(e[0], e[5]) for e in N if e[4] == 'shove']
    curses = np.array(sorted({e[0] for e in N if e[4] == 'curse'}))
    fafm = np.array([e[0] for e in N if e[4] == 'fafmotif'])
    rel = np.abs(d - hc) / (HEAP - 10)
    thr = np.clip(0.6 * (1 - rel) + 0.4 * rng.random(G.N), 0.02, 1.0)
    pile = smoothstep(HEAP - 4, HEAP - 16, np.abs(d - hc))
    S = hc + 175
    shards = dict(v=rng.choice([-1, 1], 90) * rng.uniform(100, 1500, 90), w=rng.uniform(8, 20, 90),
                  life=rng.uniform(1.5, 4.0, 90))
    trail = rng.random(G.N)

    def recent(ts, t, tau, span=2.0):
        i = int(np.searchsorted(ts, t, side='right')) - 1
        return float(np.exp(-(t - ts[i]) / tau)) if i >= 0 and t - ts[i] < span else 0.0

    for f in range(F):
        t = f * DT
        fr = np.zeros((G.N, 3))
        g = faded(t)
        st = storm(t)
        cp = recent(curses, t, 0.45, 3)
        cursed = smoothstep(T_CURSE, T_CURSE + 2, t) * (1 - smoothstep(T_HOARD + 4, T_EXIT + 8, t))

        # the mountain: meadow and battlements, shadowed by the curse, then veiled in storm air
        u = 0.5 + 0.5 * np.sin(2 * np.pi * (d / 700 - 0.02 * (t + T0)))
        fr += light(DAWN0 + (DAWN1 - DAWN0) * u[:, None], (0.65 - 0.2 * cursed - 0.25 * st + 0.06 * slow(t + T0)) * wings)
        fr += light(CASTLE, (0.48 - 0.12 * smoothstep(T_GRAB, T_CURSE, t) - 0.1 * st + 0.05 * slow(t + T0)) * mason * porch)
        if st > 0:
            m_ = billow(d, t - T_STORM)
            col = MIST0 + (MIST1 - MIST0) * m_[:, None]
            fr += light(col, st * (0.6 + 0.3 * m_) * (0.75 + 0.25 * wings))

        # the gods: bold at first, paling at the killing
        for k, col in (('donner', DONNER), ('fricka', FRICKA)):
            p = C[k][f]
            c = grey(col, g)
            fr += light(c, 0.8 * np.exp(-((d - p) / 24) ** 2) + 0.3 * np.exp(-((d - p) / 90) ** 2)
                        + (0.46 - 0.2 * g) * np.exp(-((d - p) / 170) ** 2))
        p = C['donner'][f]
        fr += light(grey(BOLT, g), (0.55 - 0.2 * g) * np.exp(-((d - p) / 60) ** 2))
        p = C['froh'][f]
        bow = hue((d - p) / 90 + 0.15 * (t + T0)) * (1 - g) + np.full((G.N, 3), 0.55) * g
        fr += light(bow, 0.8 * np.exp(-((d - p) / 28) ** 2) + 0.3 * np.exp(-((d - p) / 90) ** 2)
                    + (0.49 - 0.2 * g) * np.exp(-((d - p) / 200) ** 2))
        p = C['freia'][f]
        fr += light(FREIA, (0.95 - 0.2 * g) * np.exp(-((d - p) / 24) ** 2) + 0.35 * np.exp(-((d - p) / 80) ** 2))
        for off, col in ((-16, APPLE), (14, LEAF)):
            fr += light(col, 0.6 * (1 - g) * np.exp(-((d - p - off) / 6) ** 2))

        # Loge, flickering
        p = C['loge'][f]
        flick = 0.5 + 0.5 * np.sin(2 * np.pi * 3.3 * (t + T0)) * np.sin(2 * np.pi * 1.3 * (t + T0) + 1)
        lc = LOGE0 + (LOGE1 - LOGE0) * np.clip(0.5 + 0.4 * fl(t + T0), 0, 1)[:, None]
        fr += light(lc, (0.8 + 0.2 * flick) * np.exp(-((d - p) / 32) ** 2) * (0.75 + 0.25 * fl(t + T0))
                    + 0.25 * np.exp(-((d - p) / 100) ** 2))

        # the heap, shrinking from the edges in as Fafner fills his sack; the helmet goes too
        rem = remains(t)
        heap = pile * (thr < rem)
        glint = (tw(t + T0) > 1.1).astype(float)
        hmk = np.exp(-((d - hc + 36) / 40) ** 4) * 0.4 * (1 - smoothstep(T_HOARD + 2, T_HOARD + 3, t))
        fr += light(GOLD, 0.75 * heap * (1 - 0.75 * hmk) + 0.35 * rem * np.exp(-((d - hc) / 260) ** 2) * porch)
        fr += light(HOT, 0.55 * glint * heap)
        hm = 1 - smoothstep(T_HOARD + 2, T_HOARD + 3, t)
        sh = 0.5 + 0.5 * np.sin(2 * np.pi * (d / 26 - 0.6 * (t + T0)))
        fr += light(TARN, hm * 0.4 * (0.75 + 0.25 * sh) * np.exp(-((d - hc + 36) / 40) ** 4) * heap)
        for ts in scoops:                                   # lumps flying off the pile into his light
            s = (t - ts) / 0.5
            if 0 <= s <= 1:
                p0 = hc + 60 * np.sin(ts * 7.3)
                p1 = C['fafner'][f]
                for j in range(5):
                    sj = max(s - 0.07 * j, 0)
                    q = p0 + (p1 - p0) * sj * sj * (3 - 2 * sj)
                    fr += light(GOLD if j else HOT, (0.95 - 0.16 * j) * np.exp(-((d - q) / 9) ** 2))
        if T_HOARD + 2 <= t < T_HOARD + 3.2:                 # the helmet, a violet streak into his sack
            s = (t - T_HOARD - 2) / 1.2
            q = hc - 36 + (C['fafner'][f] - hc + 36) * s
            fr += light(TARN, 0.9 * np.exp(-((d - q) / 16) ** 2))

        # stamps and shoves shake the roofline
        for ts, w in shoves:
            if ts <= t < ts + 0.9:
                q = 0.5 * (C['fasolt'][int(ts / DT)] + C['fafner'][int(ts / DT)])
                a = np.exp(-(t - ts) / 0.18)
                fr += light(FASOLT, 0.8 * a * np.exp(-((d - q - 15) / 50) ** 2))
                fr += light(FAFNER, 0.8 * a * np.exp(-((d - q + 15) / 50) ** 2))
                fr += light(WHITE, 0.6 * a * np.exp(-((d - q) / 18) ** 2))
                r = 30 + 500 * (t - ts) ** 0.7
                fr += light(FAFNER if w == 'fafner' else FASOLT, 0.5 * (1 - (t - ts) / 0.9)
                            * np.exp(-((np.abs(d - q) - r) / 40) ** 2))
        for ts in STEPS:
            if ts <= t < ts + 1.0:
                p = C['fafner'][int(ts / DT)]
                r = 30 + 450 * (t - ts) ** 0.7
                fr += light(FAFNER, 0.55 * (1 - (t - ts)) * np.exp(-((np.abs(d - p) - r) / 45) ** 2))

        # Fasolt: grey, flaring as he grabs the ring, shattered by the blow; an ember fades where he fell
        p = C['fasolt'][f]
        alive = t < STRIKES[0]
        if alive:
            jolt = sum(np.exp(-(t - ts) / 0.2) for ts, w in shoves if w == 'fasolt' and ts <= t < ts + 1.0)
            grab = np.exp(-(t - T_GRAB) / 0.5) if t >= T_GRAB else 0.0
            fr += light(FASOLT, (0.75 + 0.3 * jolt + 0.3 * grab) * np.exp(-((d - p) / 48) ** 2)
                        + 0.3 * np.exp(-((d - p) / 130) ** 2))
            fr += light(WHITE, 0.6 * grab * np.exp(-((d - p) / 30) ** 2))
        else:
            age = t - STRIKES[0]
            ember = np.exp(-age / 2.5) * (1 - smoothstep(4, 9, age))
            fr += light(FASOLT, 0.6 * ember * np.exp(-((d - S) / 30) ** 2))
            if age < 4.5:
                q = S + shards['v'] * (1 - np.exp(-age / 0.6)) * 0.6
                a = np.clip(1 - age / shards['life'], 0, 1)
                gq = (np.exp(-((d[:, None] - q[None, :]) / shards['w'][None, :]) ** 2) * a[None, :]).max(axis=1)
                fr += light(FASOLT, 1.0 * gq) + light(WHITE, 0.5 * gq * np.exp(-age / 0.4))

        # Fafner: ochre, gathering himself before the blow, golden with the hoard as he goes
        p = C['fafner'][f]
        jolt = recent(stamps, t, 0.2, 1.0)
        wind = smoothstep(T_WIND, STRIKES[0], t) * (t < STRIKES[0])
        laden = smoothstep(T_HOARD, T_HOARD + 5, t)
        body = FAFNER + (GOLD - FAFNER) * 0.35 * laden
        fr += light(body, (0.75 + 0.3 * jolt + 0.35 * wind) * np.exp(-((d - p) / (48 + 25 * wind + 12 * laden)) ** 2)
                    + (0.3 + 0.3 * wind) * np.exp(-((d - p) / (130 + 150 * wind)) ** 2))
        if t >= T_EXIT:                                     # gold glinting in his wake
            behind = (d < p) & (d > p - 400)
            fr += light(GOLD, 0.7 * behind * (trail > 0.93) * np.exp(-(p - d) / 200) * (tw(t + T0) > 0.3))

        # the blows: the first lights the whole house, the next two where he fell
        for i, ts in enumerate(STRIKES):
            if ts <= t < ts + 1.2:
                a = np.exp(-(t - ts) / (0.16 if i == 0 else 0.12))
                if i == 0:
                    fr += light(WHITE, 0.9 * a * np.ones(G.N)) + light(FAFNER, 0.8 * a * np.ones(G.N))
                fr += light(HOT, (0.9 if i == 0 else 0.7) * a * np.exp(-((d - S) / 120) ** 2))

        # the curse: deep red runs out from the ring with every note; the house darkens under it
        if cursed > 0:
            rq = C['ring'][f]
            fr += light(BLOOD, cursed * (0.5 + 0.25 * cp) * np.exp(-((d - rq) / 700) ** 2))
            for tc in curses:
                if tc <= t < tc + 2.0:
                    r = 20 + 1400 * ((t - tc) / 2.0) ** 0.8
                    fr += light(RED, cursed * 0.85 * (1 - (t - tc) / 2.0) * np.exp(-((np.abs(d - rq) - r) / 110) ** 2))
            fr += light(RED, cursed * 0.5 * cp * np.exp(-((d - rq) / 80) ** 2))

        # the ring
        rq = C['ring'][f]
        fr += light(GOLD, (0.95 + 0.3 * cp) * np.exp(-((d - rq) / 6) ** 2))
        fr += light(RED, (0.6 + 0.4 * cp) * np.exp(-((d - rq - 6) / 4) ** 2))

        # Wotan
        p = C['wotan'][f]
        fr += light(WOTAN, 0.95 * np.exp(-((d - p) / 28) ** 2) + 0.3 * np.exp(-((d - p) / 90) ** 2))
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

    for name, gain, rev in (('strings', 0.16, 0.3), ('low', 0.19, 0.18), ('winds', 0.15, 0.3),
                            ('brass', 0.18, 0.28), ('perc', 0.22, 0.25), ('glock', 0.07, 0.4), ('fx', 0.09, 0.3)):
        M.bus(name, gain=gain, reverb=rev)
    va = M.sampler('Strings/Viola Section/susvib/*.wav', tune=-12)
    vc = M.sampler('Strings/Cello Section/susvib/*.wav', tune=-12)
    vtrem = M.sampler('Strings/Violin Section/Trem/*.wav', tune=-12)
    vatrem = M.sampler('Strings/Viola Section/trem/*.wav', tune=-12)
    trem = M.sampler('Strings/Cello Section/trem/*.wav', tune=-12)
    cb = M.sampler('Strings/Solo Contrabass/SusNV/*.wav', tune=-12)
    cbtrem = M.sampler('Strings/Solo Contrabass/Trem/*.wav', tune=-12)
    pizz = M.sampler('Strings/Solo Contrabass/Pizz/*.wav', tune=-12)
    bsn = M.sampler('Woodwinds/Bassoon/sus/*.wav', tune=-12)
    horn = M.sampler('Brass/F Horn/sus/*.wav', tune=-12)
    mute = M.sampler('Brass/F Horn/mute/*.wav', tune=-12)
    tbn = M.sampler('Brass/Tenor Trombone/sus/*.wav', tune=-12)
    tuba = M.sampler('Brass/Tuba/sus/*.wav', tune=-12)
    tpt = M.sampler('Brass/Trumpet/sus/*.wav', tune=-12)
    glock = M.sampler('Percussion/Glock/*.wav', tune=-12)
    timp = M.hits('Percussion/Timpani/Timpani1_Hit*.wav')
    roll = M.hits('Percussion/Timpani/Rolls/*.wav')
    bd = M.hits('Percussion/BDrumNewhit_v[4-7]*.wav')
    crash = M.hits('Percussion/cymbal-crash1_f*.wav')
    gong = M.hits('Percussion/gongHit_fff.wav')

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

    S = pan_at(at(G, 'Porch Front', 0.5) + 175)
    for t, d, m, v, part, who in compose():
        if part == 'giants':
            p = pan_of(who, t)
            M.add('brass', tuba.play(m, v, dur=d * 1.05, release=0.2), t, 1.5, p)
            M.add('brass', tbn.play(m + 12, v - 8, dur=d * 1.05, release=0.2), t, 0.9, p)
        elif part == 'scoop':
            M.add('glock', glock.play(m, v), t + 0.45, 1.0, pan_of('fafner', t))
            M.add('fx', whoosh(0.5, 2500, 600, 0.3, seed=int(t * 10)), t, 0.5, hc)
        elif part == 'stamp':
            p = pan_of(who, t)
            M.add('perc', timp.play(v, pitch=-4), t, 0.85, p)
            M.add('perc', bd.play(v - 8), t, 0.75, p)
            M.add('low', pizz.play(m + 12, v - 10), t, 0.7, p)
        elif part == 'quarrel':
            p = pan_of(who, t)
            if who == 'fasolt':
                M.add('brass', tbn.play(m + 12, v, dur=d * 1.05, release=0.2), t, 1.1, p)
                M.add('low', vc.play(m + 12, v - 12, dur=d, release=0.2), t, 0.6, p)
            else:
                M.add('brass', tuba.play(m, v, dur=d * 1.05, release=0.2), t, 1.2, p)
                M.add('low', bsn.play(m, v - 10, dur=d, release=0.2), t, 0.7, p)
        elif part == 'shove':
            p = pan_of(who, t)
            M.add('perc', timp.play(v, pitch=-3), t, 0.9, p)
            M.add('perc', bd.play(v), t, 0.8, p)
            M.add('fx', whoosh(0.4, 3000, 500, 0.4, seed=int(t * 7)), t - 0.15, 0.6, p)
        elif part == 'grab':
            M.add('brass', tbn.play(m, v, dur=d * 1.05, release=0.3), t, 1.0, pan_of(who, t))
            M.add('brass', horn.play(m + 12, v - 10, dur=d * 1.05, release=0.3), t, 0.7, pan_of(who, t))
        elif part == 'wind':
            M.add('perc', roll.play(v, dur=d + 0.1), t, 0.9, pan_of('fafner', t))
            hold('strings', vatrem, m + 12, t, t + d, v, 0.0, rise=d, fall=0.1, gain=0.8)
        elif part == 'rise':
            M.add('strings', vtrem.play(m, v, dur=0.25, release=0.05), t, 0.6, pan_of('fafner', t))
        elif part in ('strike', 'blow'):
            p = S
            M.add('perc', timp.play(v, pitch=-6), t, 1.0, p)
            M.add('perc', bd.play(v), t, 1.0, p)
            if part == 'strike':
                M.add('perc', gong.play(127), t, 0.9, p)
                M.add('perc', crash.play(127), t, 0.9, p)
                for mm in ('Gb1', 'C2', 'Gb2', 'A2', 'C3', 'Eb3'):     # the blow: a diminished chord, full force
                    M.add('brass', (tuba if note(mm) < note('Gb2') else tbn).play(note(mm), 124, dur=1.4, release=0.6),
                          t, 1.0, p)
                M.add('fx', whoosh(0.5, 5000, 400, 0.6, seed=3), t - 0.25, 0.8, p)
        elif part == 'curse':
            M.add('brass', tbn.play(m, v, dur=d * 1.05, release=0.4), t, 1.2, hc)
            M.add('brass', horn.play(m, v - 10, dur=d * 1.05, release=0.4), t, 0.8, hc - 0.2)
            M.add('low', vc.play(m, v - 12, dur=d * 1.05, release=0.4), t, 0.6, hc + 0.2)
        elif part == 'cursepedal':
            hold('low', cbtrem, m + 12, t, t + d, v, hc, rise=0.2, fall=0.8, gain=0.8)
            M.add('brass', tuba.play(m + 12, v - 10, dur=d, release=0.6), t, 0.8, hc)
        elif part == 'timp':
            M.add('perc', timp.play(v, pitch=-1), t, 0.9, hc)
        elif part == 'fafmotif':
            p = pan_of(who, t)
            M.add('brass', tuba.play(m, v, dur=d * 1.05, release=0.25), t, 1.1, p)
            M.add('low', bsn.play(m, v - 6, dur=d * 1.05, release=0.25), t, 0.8, p)
            M.add('low', cb.play(m + 12, v - 12, dur=d, release=0.25), t, 0.6, p)
        elif part == 'echo':
            M.add('brass', mute.play(m, v, dur=d * 1.05, release=0.6), t, 1.4, pan_of('wotan', t))
            M.add('low', bsn.play(m - 12, v - 8, dur=d * 1.05, release=0.6), t, 1.0, pan_of('wotan', t))
        elif part == 'echopedal':
            hold('low', cb, m + 12, t, t + d, v, 0.0, rise=0.6, fall=1.5, gain=0.7)
        elif part == 'mist':
            s = trem if m <= note('Bb2') else vatrem
            hold('strings', s, m + 12 * (m == note('Bb1')), t, t + d, v, -0.3 + 0.2 * (m % 4), rise=5.0, fall=1.5,
                 gain=1.4)
        elif part == 'rumble':
            M.add('perc', roll.play(v, dur=d), t, 1.0, -0.4)
            M.add('fx', whoosh(d, 150, 600, 0.5, seed=int(t)), t, 0.6, -0.3)
        elif part == 'chord':
            hold('strings', va if m < note('D4') else vtrem, m, t, t + d, v, 0.0, rise=0.05, fall=2.0, gain=0.8)
        elif part == 'bed':
            hold('low', cb if m < note('C2') + 1 else vc, m + 12, t, t + d, v, hc, rise=1.0, fall=1.0, gain=0.8)
        elif part == 'distant':
            M.add('brass', mute.play(m, v, dur=d, release=0.6), t, 1.2, pan_of('donner', t))
