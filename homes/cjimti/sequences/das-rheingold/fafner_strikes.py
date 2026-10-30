"""Fafner Strikes: the gold is the giants' now, and they quarrel over the ring until Fafner strikes his brother
dead with one blow: the curse on the ring has claimed its first.

The music is Wagner's own: bars 3584-3615 of the last scene of Das Rheingold, as Solti's 1958 Vienna Philharmonic
recording takes them, from the Wagner Ring Dataset's piano reduction (pixelhome/ring.py). The giants' quarrel
("Halt, du Gieriger! Gönne mir auch was!") over their own heavy rhythm in the tubas, trombones and low strings;
Fasolt seizes the ring, they wrestle for it, and after "Halt ihn fest, daß er nicht fall'!" the full orchestra
strikes, the trombones plunge down and the timpani beat on a single F; then the curse motif, quiet and terrible,
in the horns and bassoons, and Fafner's own heavy steps as he gathers the hoard and goes ("Nun blinzle nach
Freias Blick! An den Reif rührst du nicht mehr!"). The staging's sounds: gold rattling into Fafner's sack, the
shoves and thuds of the quarrel, the ring snatched, the blow with a crash and a gong and two more thuds where
Fasolt fell, a deep gong as the curse rises, the ring wrenched off his hand, and Fafner's footfalls going away.
They pull back under the curse.

Fafner stuffs the gold into his sack, a lump flying off the heap into his ochre light on every heavy note, and the
two giants shove each other back and forth over the pile, their lights slamming together in grey and ochre.
Fasolt snatches the ring (the small gold point with its red glint jumps to his grey light). Fafner draws back and
strikes: a flash across the whole house, and Fasolt's grey light shatters into fragments that spray along the
roofline and go out, then two more blows where he fell. With every note of the curse a pulse of deep red runs out
from the ring across the house while the mountain shadows; Fafner wrenches the ring from his brother, gathers the
rest of the hoard and the helmet into his light, and stamps off down Porch Right and out of the free end of
Right, a trail of gold glinting behind him. The gods stand horrified as storm air begins to gather.

compose() tags the music's moments, choreography() every position; render() and score() read both."""
import numpy as np
from pixelhome.fx import DT, hexc, light, smoothstep, nframes, Flicker
from pixelhome.ring import Orchestra, excerpt, tidy

CODE = 'RG23'
TITLE = 'Fafner Strikes'
KIND = 'show'
DESCRIPTION = ('The giants quarrel over the ring, and Fafner strikes his brother dead with one blow. The curse '
               'on the ring has claimed its first victim. Fafner carries off the gold, and the gods are left '
               'staring after him as a storm gathers.')
VOICEOVER = ('Two brothers, one ring, and only one of them walks away. '
             'Alberich said the ring would bring death. He was right.')

EX = excerpt(__file__)                      # bars 3584-3615, Solti 1958
BAR = {int(m): t for m, t in EX['bars']}
T_GATHER = 0.5
T_GRAB = 42.3                               # "Zurück! Du Frecher! Mein ist der Ring": Fasolt snatches it
# every line a giant sings in the quarrel is a shove; after the grab, every line a lunge for the ring
QUARREL = [(t0, 0, 0, who.lower()) for t0, t1, who, text in EX['singing'] if who in ('Fasolt', 'Fafner') and t0 < T_GRAB]
T_WIND = 55.3                               # Fafner draws back, on the rising chords
TUSSLE = [(t0, who.lower()) for t0, t1, who, text in EX['singing'] if who in ('Fasolt', 'Fafner') and T_GRAB < t0 < T_WIND]
STRIKES = [BAR[3608], BAR[3609], 60.47]     # the blow (the fortissimo), and two more where he fell
T_CURSE = 63.59                             # the curse rises
T_TAKE = 68.75                              # "Nun blinzle nach Freias Blick!": he wrenches the ring away
T_HOARD = BAR[3613]                         # he gathers the rest
T_EXIT = BAR[3614]                          # and stamps off
STEPS = [T_EXIT + 0.7 * k for k in range(12)]
T_HORROR = 82.0
T_STORM = 83.0
D = EX['seconds']
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
    """The music's moments, from the excerpt's real notes: (time, seconds, midi, velocity, part, who). 'scoop' is
    gold flying into Fafner's sack (the left hand's long notes), 'stamp' the giants' heavy rhythm (its low notes),
    'shove' a turn of the quarrel, 'strike'/'blow' the killing, 'curse' each note of the curse, 'fafmotif' the music
    of his going."""
    N = []
    seen = set()
    for t, d, m, v, h in EX['notes']:
        key = round(t, 2)
        if t < T_GRAB and h == 1:
            if d >= 0.4 and (key, 's') not in seen:
                seen.add((key, 's'))
                N.append((t, d, m + 24, v, 'scoop', 'fafner'))
            if m < 45 and d >= 0.3 and (key, 't') not in seen:
                seen.add((key, 't'))
                N.append((t, d, m, v, 'stamp', 'fafner'))
        elif T_CURSE <= t < T_HOARD and d >= 0.15 and (key, 'c') not in seen:
            seen.add((key, 'c'))
            N.append((t, d, m, v, 'curse', None))
        elif t >= T_HOARD and d >= 0.3 and (key, 'f') not in seen:
            seen.add((key, 'f'))
            N.append((t, d, m, v, 'fafmotif', 'fafner'))
    for t0, b, tr, who in QUARREL:
        N.append((t0, 0.5, 36, 0, 'shove', who))
    for i, ts in enumerate(STRIKES):
        N.append((ts, 1.5, 30, 0, 'strike' if i == 0 else 'blow', 'fafner'))
    for k in range(10):
        N.append((T_HOARD + k * 0.4, 0.4, 79 + (k * 5) % 12, 0, 'scoop', 'fafner'))
    for i, ts in enumerate(STEPS):
        N.append((ts, 0.5, 36, 0, 'stamp', 'fafner'))
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
    for t0, w in TUSSLE:                                    # wrestling for the ring
        set_('fafner', t0, t0 + 0.5, S - 40, 8.0)
        set_('fasolt', t0, t0 + 0.5, S + (25 if w == 'fafner' else -25), 8.0)
        set_('fafner', t0 + 0.5, t0 + 1.6, hc + 70, 3.0)
        set_('fasolt', t0 + 0.5, t0 + 1.6, S, 3.0)
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

    o = Orchestra(M, level=3.8)

    def role(t, d, m, v, h):
        if t < STRIKES[0] - 0.05:                       # the quarrel: the giants' rhythm in the low brass
            if h == 1:
                return [('tuba', 0, 10, 0.7 if m < 52 else 0.0), ('trombones', 0 if m >= 45 else 12, 6, 0.55),
                        ('cellos', 0, 6, 0.5), ('basses', 0, 0, 0.4 if m < 45 else 0.0)]
            return None
        if t < T_CURSE - 0.05:                          # the blow: the full brass, then the trombones plunging
            if h == 1:
                return [('trombones', 0, 70, 0.7), ('tuba', 0, 70, 0.6), ('basses', 0, 60, 0.5)]
            return [('trumpets', 0, 0, 0.55), ('horns', -12, 0, 0.6), ('violins', 0, 0, 0.5)]
        if t < T_HOARD:                                 # the curse, quiet: horns and bassoons
            if h == 1:
                return [('cellos', 0, 30, 0.55), ('basses', -12 if m >= 40 else 0, 30, 0.45)]
            return [('horns', 0, 20, 0.7), ('bassoons', -12, 16, 0.45)]
        if h == 1 or m < 50:                            # Fafner's heavy going
            return [('tuba', 0, 20, 0.6), ('bassoons', 0, 16, 0.45), ('basses', 0, 10, 0.4)]
        return [('horns', 0, 10, 0.55), ('clarinets', 0, 4, 0.35)]

    o.tutti(tidy(EX['notes']), size=lambda t: 1.0 if STRIKES[0] - 0.1 <= t < T_CURSE else 0.6, role=role)

    N = compose()
    o.effects([(0.0, -4.0), (STRIKES[0] - 1.0, -4.0), (STRIKES[0], 0.0), (T_CURSE + 1.0, -10.0),
               (T_HOARD - 1.0, -10.0), (T_HOARD, -2.0)])
    for t, d, m, v, part, who in N:
        if part == 'scoop':                             # gold rattling into his sack
            o.play('glock', 84 + (int(t * 11) % 6) * 2, t, 0.1, 62, pan_of('fafner', t), 0.22)
            o.hit('metal', t + 0.02, 58, gain=0.08, pan=pan_of('fafner', t))
        elif part == 'stamp' and t >= T_EXIT:           # his footfalls going away
            far = (t - T_EXIT) / (D - T_EXIT)
            o.hit('bass drum', t, 116, gain=0.55 * (1 - 0.6 * far), pan=pan_of('fafner', t))
            o.hit('timpani', t, 104, pitch=-7, gain=0.3 * (1 - 0.6 * far), pan=pan_of('fafner', t))
        elif part == 'shove':                           # bodies slamming together over the pile
            o.hit('bass drum', t, 112, gain=0.4, pan=hc + 0.15)
            o.hit('scrape', t + 0.05, 96, gain=0.25, pan=hc + 0.15)
    for t, who in TUSSLE:
        o.hit('bass drum', t, 110, gain=0.45, pan=pan_of(who, t))
        o.hit('brake drum', t, 90, gain=0.18, pan=pan_of(who, t))
    pg = pan_of('fasolt', T_GRAB)
    o.play('glock', 91, T_GRAB, 0.1, 96, pg, 0.4)       # the ring snatched
    o.hit('scrape', T_GRAB, 104, gain=0.3, pan=pg)
    ps = pan_of('fasolt', STRIKES[0])
    o.hit('timpani roll', T_WIND, 90, pitch=-4, gain=0.4, pan=ps)
    o.boom(STRIKES[0], ps, 1.1)                         # the blow
    o.hit('crash', STRIKES[0], 124, gain=0.7, pan=ps)
    o.shatter(STRIKES[0] + 0.02, ps, 0.7)
    for ts in STRIKES[1:]:                              # two more, where he fell
        o.hit('bass drum', ts, 120, gain=0.6, pan=ps)
        o.hit('timpani', ts, 116, pitch=-8, gain=0.45, pan=ps)
    o.hit('gong', T_CURSE, 110, gain=0.5, pan=ps)       # the curse rises
    o.hit('gong scrape', T_TAKE, 100, gain=0.4, pan=ps)  # the ring torn off his hand
    o.play('glock', 85, T_TAKE + 0.3, 0.1, 90, ps, 0.35)
    o.hit('gong scrape', T_HOARD + 2.0, 96, gain=0.35, pan=pan_of('fafner', T_HOARD + 2.0))   # the helmet
    o.thunder(T_STORM + 0.5, near=0.1, pan=-0.4, gain=0.6)   # storm air, far off
