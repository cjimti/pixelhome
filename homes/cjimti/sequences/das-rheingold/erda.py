"""Erda: the standoff over the ring hangs on a C minor tremolo, and then the light goes out of the mountain.
Everything sinks to a deep dusk; only the gold keeps a dull glow. Out of the back corner of the porch (the
deepest point of the scene) a deep earth light seeps up: moss green, churning slowly like soil turning over, on
a contrabass D flat so low it is more felt than heard. This is Erda, the ancient earth itself, rising to warn
Wotan, and nothing else on the mountain moves while she is there.

Her motif (Donington 3, the Nature arpeggio turned into C sharp minor) climbs twice in the low winds, the first
time in the bassoons and clarinets, the second with horns, and every chord of it swells her light up and out
along the porch until it fills the battlements and seeps across the meadow. Then her warning, the downfall of
the gods (Donington 4), on soft trombones over a G flat pedal: a shadow sweeps out from the castle to both ends
of the house and the gods on the wings go grey to the bone. Her light draws back into the corner and sinks
away with the first chords of her motif, very low, and the dark holds for a breath.

Wotan has heard. The light comes back to the mountain and he gives up the ring: the Ring motif (Donington 8),
quiet now in the woodwinds and a horn, as the small gold point with its red glint travels from his hand along
Porch Front and drops into the gap where Freia's eye showed. The gap closes with a flash. The giants pull out
their staves, the heap bursts open, and Freia leaps out in a spray of pink to her joyful music (Donington 7),
running down Porch Left and along Left to the gods. As she reaches them their colours come flooding back, bold
and bright, in a wave across the whole house, to a full orchestral statement of Freia's love (Donington 6)
with harps and cymbals, while the giants push their gold back into one pile with the ring on top.

compose() holds every note, choreography() every position; render() and score() read both."""
import numpy as np
from pixelhome.audio import note
from pixelhome.fx import DT, hexc, light, smoothstep, nframes, Flicker
from pixelhome.leitmotifs import MOTIFS, play

CODE = 'RG22'
TITLE = 'Erda'
KIND = 'show'
DESCRIPTION = ('The mountain goes dark, and the ancient earth itself rises out of the porch in a deep green '
               'light to warn Wotan: the ring brings only ruin. He listens, and gives it up. The heap opens, '
               'Freia runs free, and the gods get their colour back.')
VOICEOVER = ('Something older than the gods is waking under the mountain. '
             'When the earth itself tells you to let go, you let go.')

T_DARK = 2.5                                # the light drains out of the mountain
T_RISE = 7.0                                # the earth light seeps up
T_ERDA = [12.0, 21.0]                       # her motif, twice
EBEAT = 1.0
T_DOWN = 30.0                               # the downfall of the gods
DBEAT = 0.95
T_SINK = 38.0                               # she sinks back
T_LIGHT = 46.0                              # light returns
T_YIELD = 47.5                              # Wotan gives up the ring
RBEAT = 0.6
T_LAND = 53.2                               # the ring fills the gap
T_PULL = [54.3, 54.9]                       # the staves pulled out
T_FREE = 55.2                               # the heap bursts, Freia runs
T_ARRIVE = 59.4                             # she reaches the gods: colour floods back
T_LOVE = 60.0                               # Freia's love, full orchestra
T_CODA = 65.5
T_CLOSE = 66.0                              # the giants push the gold back into one pile
D = 80.0
T0 = 80.0                                  # the opera's clock at our start: steady motion carries across the cuts

HEAP = 92                                   # half-width of the pile (as in Freia Ransomed)

GOLD = hexc('#ffaa00')
HOT = hexc('#fff0a0')
FREIA = hexc('#ff5a9a')
APPLE = hexc('#ffd040')
LEAF = hexc('#60d020')
WOTAN = hexc('#1a3cff')
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
ERDA = hexc('#3a8a20')
SOIL = hexc('#4a3a10')
DEEPMOSS = hexc('#1a5010')
SHADE = hexc('#141830')
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
    """How grey the gods are: grey with fear, greyer at the downfall, and then all their colour back at once."""
    return (0.8 + 0.15 * smoothstep(T_DOWN, T_DOWN + 5, t)) * (1 - smoothstep(T_ARRIVE - 1.0, T_ARRIVE + 2.0, t))


def dusk(t):
    """How much light the mountain keeps (1 = all of it)."""
    return 1 - 0.68 * smoothstep(T_DARK, T_RISE, t) + 0.68 * smoothstep(T_LIGHT, T_LIGHT + 4, t)


def sep(t):
    """Half the gap between the two halves of the heap: closed, burst open round Freia, pushed back together."""
    return (HEAP / 2 + 75 * smoothstep(T_FREE - 0.1, T_FREE + 0.4, t)
            - 85 * smoothstep(T_CLOSE, T_CLOSE + 6, t))


def compose():
    """Every note: (time, seconds, midi, velocity, part, who)."""
    N = []

    def add(t, d, m, v, part, who=None):
        N.append((float(t), float(d), note(m) if isinstance(m, str) else int(m), int(v), part, who))

    for m in ('C3', 'Eb3', 'G3', 'C4'):                    # the standoff's tremolo, dying away
        add(0.0, T_RISE - 1.5, m, 70, 'trem')
    add(T_DARK, 4.0, 'C2', 70, 'roll')
    add(T_RISE - 1.0, T_SINK + 6.0 - T_RISE, 'Db1', 82, 'earth')
    add(T_RISE, 6.0, 'C2', 60, 'scrape')

    for i, t0 in enumerate(T_ERDA):                         # Erda: low winds, the second time with horns
        for t, m, v, d in play('erda', t0, EBEAT, -12 if i == 0 else 0, 84 + 10 * i):
            if d >= 7:
                add(t, d, m - (0 if i == 0 else 12), v, 'pedal')
            else:
                add(t, d, m, v, 'erda', i)
        add(t0, 0.1, 'C2', 50, 'swell')
    for b, d, m in ((0, 1.5, 'Ab3'), (1.5, .5, 'Gb3'), (2, 1, 'E3'), (3, 1, 'Eb3'), (4, 3, 'Db3')):
        add(T_ERDA[1] + 8.0 + b * 0.5, d * 0.5, m, 92, 'warn')       # "Weiche, Wotan!"
    for t, m, v, d in play('downfall', T_DOWN, DBEAT, -12, 92):
        add(t, d, m, v, 'down' if m >= note('C3') else 'downpedal')
    for t, m, v, d in play('erda', T_SINK + 0.5, 1.2, -12, 70):
        if t < T_SINK + 6.0 and d < 7:
            add(t, d, m - 12, v - 6 * int((t - T_SINK) / 1.5), 'sink')
    add(T_SINK + 6.5, 1.5, 'Db2', 50, 'roll')

    # Wotan yields the ring
    for t, m, v, d in play('ring', T_YIELD, RBEAT, 0, 78):
        add(t, d, m, v, 'ring' if m >= note('C3') else 'ringbass')
    add(T_LAND, 1.0, 'G5', 96, 'land')
    for i, tp in enumerate(T_PULL):
        add(tp, 0.6, 'C2' if i == 0 else 'G1', 112, 'pull', ('fafner', 'fasolt')[i])
    add(T_FREE, 1.2, 'D3', 116, 'burst')
    for k, t0 in enumerate((T_FREE + 0.3, T_FREE + 0.3 + 8 * 0.45)):
        for t, m, v, d in play('freia', t0, 0.45, 0, 96 + 6 * k):
            add(t, d, m, v, 'freia' if m >= note('C4') else 'freialow')
    add(T_ARRIVE - 0.8, 0.8, 'D3', 100, 'gliss')
    add(T_ARRIVE, 1.5, 'D2', 120, 'crash')
    for t, m, v, d in play('freia_love', T_LOVE, 0.75, 0, 112):
        add(t, d, m, v, 'love' if m >= note('D4') else 'lovemid' if m >= note('D3') else 'lovebass')
    for t, m, v, d in play('freia', T_CODA, 0.6, 0, 90):
        add(t, d, m, v, 'freia' if m >= note('C4') else 'freialow')
    for k in range(6):
        add(T_CODA + 4.8 + k * 0.5, 0.4, ('D4', 'Gb4', 'A4', 'D5', 'A4', 'Gb4')[k], 80, 'harp')
    for m in ('D3', 'A3', 'D4', 'Gb4', 'A4'):
        add(70.5, D - 70.5, m, 72, 'chord')
    add(70.5, D - 70.5, 'D2', 74, 'chordbass')
    for t, m, v, d in play('giants', 75.5, 0.55, -12, 84):     # Fafner grumbles: the gold is theirs now
        if t < D - 0.8:
            add(t, d, m, v, 'giants')
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
    """Per frame: where everyone is (path distance), and the ring's track to the heap."""
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

    W = at(G, 'Porch Front', 0.12)
    set_('wotan', 0, D, W, 3.0)
    jit = 8 * np.sin(2 * np.pi * (t + T0) * 1.7) + 5 * np.sin(2 * np.pi * (t + T0) * 3.1)
    set_('loge', 0, D, at(G, 'Porch Left', 0.75), 3.0)
    set_('donner', 0, D, at(G, 'Left', 0.3), 3.0)
    set_('fricka', 0, D, at(G, 'Left', 0.7), 3.0)
    set_('froh', 0, D, at(G, 'Right', 0.7), 3.0)
    FS, FF = at(G, 'Porch Right', 0.2), at(G, 'Porch Right', 0.55)
    set_('fasolt', 0, D, FS, 3.0)
    set_('fafner', 0, D, FF, 3.0)
    for i, (tp, k) in enumerate(zip(T_PULL, ('fafner', 'fasolt'))):       # each giant strides to his staff
        set_(k, tp - 1.4, tp + 0.6, hc + (HEAP + 30) * (-1 if i else 1), 3.5)
        set_(k, tp + 0.6, T_CLOSE, (FF, FS)[i], 1.6)
    set_('fafner', T_CLOSE, T_CLOSE + 6, hc + HEAP + 50, 1.2)            # and shoves the gold back together
    set_('fasolt', T_CLOSE, T_CLOSE + 6, hc + HEAP + 110, 1.2)
    set_('fafner', T_CLOSE + 6, D, FF - 30, 1.8)
    set_('fasolt', T_CLOSE + 6, D, FS + 20, 1.8)

    # the ring: on Wotan's hand, then along Porch Front to the gap, in step with its motif
    u = smoothstep(T_YIELD + 0.4, T_LAND, t)
    set_('ring', 0, D, W + 10 + (hc + 12 - W - 10) * u, 30.0)
    # Freia: hidden at the heap, then out and away to the gods on Left
    set_('freia', 0, D, hc, 3.0)
    set_('freia', T_FREE + 0.3, D, at(G, 'Left', 0.5), 1.25)
    pos = {k: follow(tgt[k], rate[k]) for k in who}
    pos['loge'] = pos['loge'] + jit                        # the flicker on top of where he stands
    pos['t'] = t
    return pos


def render(G, seed=22):
    rng = np.random.default_rng(seed)
    F = nframes(D)
    out = np.zeros((F, G.N, 3))
    d = G.pd
    C = choreography(G)
    N = compose()
    hc = at(G, 'Porch Front', 0.5)
    E0 = at(G, 'Porch Left', 1.0)                           # the back corner of the porch, where the earth opens
    porch = np.isin(G.seg_of, ['Porch Left', 'Porch Front', 'Porch Right'])
    wings = ~porch
    block = np.floor(d / 34).astype(int)
    mason = np.where((d % 34) < 22, 1.0, 0.35) * (0.8 + 0.2 * rng.random(block.max() + 1)[block])
    tw = Flicker(np.random.default_rng(2101), G.N, 2.0, 7.0)    # shared by RG21-24
    fl = Flicker(np.random.default_rng(2102), G.N, 4.0, 11.0)
    slow = Flicker(np.random.default_rng(2103), G.N, 0.1, 0.4)
    soil = Flicker(rng, G.N, 0.08, 0.35)
    chords = np.array(sorted({e[0] for e in N if e[4] == 'erda'}))
    downs = np.array(sorted({e[0] for e in N if e[4] == 'down'}))
    rings = np.array([e[0] for e in N if e[4] == 'ring'])
    freias = np.array([e[0] for e in N if e[4] == 'freia'])
    loves = np.array(sorted({e[0] for e in N if e[4] == 'love'}))
    pulls = [(e[0], e[5]) for e in N if e[4] == 'pull']
    rel = np.abs(d - hc) / HEAP
    thr = np.clip(0.72 * (1 - rel) + 0.28 * rng.random(G.N), 0, 0.97)
    eye = int(np.argmin(np.abs(d - (hc + 12))))
    sprays = dict(p=np.full(70, hc), v=rng.choice([-1, 1], 70) * rng.uniform(150, 1300, 70),
                  c=rng.integers(3, size=70), w=rng.uniform(10, 22, 70))

    def recent(ts, t, tau, span=2.0):
        i = int(np.searchsorted(ts, t, side='right')) - 1
        return float(np.exp(-(t - ts[i]) / tau)) if i >= 0 and t - ts[i] < span else 0.0

    for f in range(F):
        t = f * DT
        fr = np.zeros((G.N, 3))
        g = faded(t)
        lit = dusk(t)
        bloom = smoothstep(T_ARRIVE - 0.5, T_ARRIVE + 1.5, t)

        # the mountain: meadow on the wings, battlements on the porch; the downfall's shadow sweeps the castle
        u = 0.5 + 0.5 * np.sin(2 * np.pi * (d / 700 - 0.02 * (t + T0)))
        fr += light(DAWN0 + (DAWN1 - DAWN0) * u[:, None], (0.55 + 0.06 * slow(t + T0) + 0.1 * bloom) * wings)
        sweep = 0.0
        if T_DOWN <= t < T_SINK + 2:
            r = 900 * smoothstep(T_DOWN, T_DOWN + 6, t)
            sweep = smoothstep(r, r - 250, np.abs(d - hc)) * (1 - smoothstep(T_SINK, T_SINK + 2, t))
        fr += light(CASTLE, (0.3 + 0.05 * slow(t + T0) + 0.18 * bloom) * mason * porch * (1 - 0.6 * sweep))

        # the gods on the wings; their colour floods back at the end
        for k, col in (('donner', DONNER), ('fricka', FRICKA)):
            p = C[k][f]
            c = grey(col, g)
            fr += light(c, (0.7 + 0.1 * bloom) * np.exp(-((d - p) / 24) ** 2) + 0.3 * np.exp(-((d - p) / 90) ** 2)
                        + (0.34 - 0.12 * g + 0.12 * bloom) * np.exp(-((d - p) / 170) ** 2))
        p = C['donner'][f]
        fr += light(grey(BOLT, g), (0.35 + 0.2 * bloom) * np.exp(-((d - p) / 60) ** 2))
        p = C['froh'][f]
        bow = hue((d - p) / 90 + 0.15 * (t + T0)) * (1 - g) + np.full((G.N, 3), 0.55) * g
        fr += light(bow, (0.7 + 0.1 * bloom) * np.exp(-((d - p) / 28) ** 2) + 0.3 * np.exp(-((d - p) / 90) ** 2)
                    + (0.34 - 0.12 * g + 0.15 * bloom) * np.exp(-((d - p) / 200) ** 2))

        # the giants
        for k, col in (('fasolt', FASOLT), ('fafner', FAFNER)):
            p = C[k][f]
            jolt = sum(np.exp(-(t - tp) / 0.2) for tp, w in pulls if w == k and tp <= t < tp + 1.0)
            fr += light(col, (0.75 + 0.3 * jolt) * np.exp(-((d - p) / 48) ** 2) + 0.3 * np.exp(-((d - p) / 130) ** 2))

        # Loge, flickering
        p = C['loge'][f]
        flick = 0.5 + 0.5 * np.sin(2 * np.pi * 3.3 * (t + T0)) * np.sin(2 * np.pi * 1.3 * (t + T0) + 1)
        lc = LOGE0 + (LOGE1 - LOGE0) * np.clip(0.5 + 0.4 * fl(t + T0), 0, 1)[:, None]
        fr += light(lc, (0.8 + 0.2 * flick) * np.exp(-((d - p) / 32) ** 2) * (0.75 + 0.25 * fl(t + T0))
                    + 0.25 * np.exp(-((d - p) / 100) ** 2))

        # the heap: closed round her (the helmet on top, her eye in the gap); burst open; pushed back together
        s_ = sep(t)
        hw = HEAP / 2
        halves = np.maximum(smoothstep(hw + 6, hw - 6, np.abs(d - (hc - s_))),
                            smoothstep(hw + 6, hw - 6, np.abs(d - (hc + s_))))
        heapc = hc
        opened = smoothstep(T_FREE - 0.1, T_FREE + 0.4, t)
        halves = np.maximum(halves, (1 - opened) * smoothstep(HEAP + 6, HEAP - 6, np.abs(d - hc)))
        helm_at = hc - s_ + hw * (1 - opened)                # on top of her, then riding the left half
        helm = np.exp(-((d - helm_at) / 40) ** 4) * (1 - 0.6 * smoothstep(T_FREE, T_FREE + 0.5, t)) * halves
        land = np.exp(-(t - T_LAND) / 0.3) if t >= T_LAND else 0.0
        burst = np.exp(-(t - T_FREE) / 0.35) if t >= T_FREE else 0.0
        glint = (tw(t + T0) > 1.1).astype(float)
        warm = 0.5 * (1 - 0.3 * smoothstep(T_FREE, T_FREE + 2, t))
        fr += light(GOLD, (0.75 + 0.4 * land) * halves * (1 - 0.75 * helm)
                    + warm * np.exp(-((d - heapc) / 260) ** 2) * porch)
        fr += light(HOT, 0.55 * glint * halves + 0.6 * land * np.exp(-((d - hc) / 70) ** 2))
        sh = 0.5 + 0.5 * np.sin(2 * np.pi * (d / 26 - 0.6 * (t + T0)))
        fr += light(TARN, (0.75 + 0.25 * sh) * helm)
        if t < T_LAND:                                      # her eye, still showing through
            beat = 0.75 + 0.25 * np.sin(2 * np.pi * t / 1.6)
            fr[eye] += light(FREIA, beat * (1 - 0.3 * (1 - lit)))
        for tp, k in pulls:                                 # the staves, pulled out
            off, col = (HEAP + 8, FAFNER) if k == 'fafner' else (-HEAP - 8, FASOLT)
            gone = smoothstep(tp, tp + 0.3, t)
            fr += light(col, (1 - gone) * 1.0 * np.exp(-((d - hc - off) / 5) ** 2))
            if tp <= t < tp + 1:
                fr += light(WHITE, 0.6 * np.exp(-(t - tp) / 0.25) * np.exp(-((d - hc - off) / 40) ** 2))

        # the whole scene sinks into dusk while the earth speaks (Erda's light is added after, undimmed)
        fr *= (lit * (1 - 0.35 * sweep) * np.ones(G.N))[:, None] ** 2.2

        # Erda: the ancient earth, rising out of the back corner of the porch, swelling with every chord
        rise = smoothstep(T_RISE, T_ERDA[0] + 1, t) * (1 - smoothstep(T_SINK, T_SINK + 6, t))
        if rise > 0:
            ch = recent(chords, t, 1.2, 3)
            W = 60 + 380 * smoothstep(T_RISE, T_ERDA[1] + 4, t) * (1 - smoothstep(T_SINK, T_SINK + 6, t)) + 60 * ch
            dd = np.abs(d - E0)
            body = np.exp(-(dd / W) ** 1.6)
            churn = 0.5 + 0.5 * soil(t + dd / 400)
            col = DEEPMOSS + (ERDA - DEEPMOSS) * churn[:, None]
            fr += light(col, rise * (1.0 + 0.3 * ch) * body)
            fr += light(SOIL, rise * 0.35 * body * (1 - churn))
            fr += light(ERDA, rise * 0.4 * np.exp(-(dd / (W * 2.2)) ** 2) * wings)
            for tc in chords:                               # each chord rises up through her as a ring of light
                if tc <= t < tc + 2.2:
                    r = 20 + (W + 200) * ((t - tc) / 2.2) ** 0.7
                    fr += light(ERDA, rise * 0.75 * (1 - (t - tc) / 2.2) * np.exp(-((dd - r) / 45) ** 2))
            fr += light(hexc('#a0e070'), rise * (0.4 + 0.4 * ch) * np.exp(-(dd / 25) ** 2))

        # Wotan (brighter once he has decided) and the ring, then the ring's journey into the gap
        p = C['wotan'][f]
        resolve = smoothstep(T_SINK + 6, T_YIELD, t)
        fr += light(WOTAN, (0.8 + 0.15 * resolve) * max(lit, 0.55) * np.exp(-((d - p) / 28) ** 2)
                    + 0.3 * max(lit, 0.5) * np.exp(-((d - p) / 90) ** 2))
        rq = C['ring'][f]
        rp = recent(rings, t, 0.3)
        if t < T_LAND:
            fr += light(GOLD, (0.95 + 0.35 * rp) * np.exp(-((d - rq) / 6) ** 2))
            fr += light(RED, (0.55 + 0.35 * rp) * np.exp(-((d - rq - 6) / 4) ** 2))
            if t > T_YIELD:
                fr += light(GOLD, 0.4 * rp * np.exp(-((d - rq) / 50) ** 2))
        else:                                               # on the heap now: the giants' gold
            ra = hc + s_ - hw * (1 - opened) + 8 * opened + 12 * (1 - opened)
            fr += light(GOLD, 0.95 * np.exp(-((d - ra) / 6) ** 2))
            fr += light(RED, 0.6 * np.exp(-((d - ra - 6) / 4) ** 2))
        if land > 0.01:
            fr += light(GOLD, 0.7 * land * np.exp(-((d - hc) / 200) ** 2))

        # Freia bursts out and runs to the gods; a spray of pink and apple blossom where she broke free
        if t >= T_FREE:
            p = C['freia'][f]
            fl_ = recent(freias, t, 0.2)
            fr += light(FREIA, (0.95 + 0.25 * fl_) * np.exp(-((d - p) / 24) ** 2) + 0.35 * np.exp(-((d - p) / 80) ** 2))
            for off, col in ((-16, APPLE), (14, LEAF)):
                fr += light(col, 0.6 * np.exp(-((d - p - off) / 6) ** 2))
            fr += light(FREIA, 0.9 * burst * np.exp(-((d - hc) / 60) ** 2))
            fr += light(WHITE, 0.7 * burst * np.exp(-((d - hc) / 30) ** 2))
            age = t - T_FREE
            if age < 3.5:
                q = sprays['p'] + sprays['v'] * (1 - np.exp(-age / 0.7)) * 0.7
                fade = np.exp(-age / 1.2)
                for c, col in enumerate((FREIA, APPLE, WHITE)):
                    sel = sprays['c'] == c
                    gq = np.exp(-((d[:, None] - q[sel][None, :]) / sprays['w'][sel][None, :]) ** 2).max(axis=1)
                    fr += light(col, 0.9 * fade * gq)

        # the colour comes flooding back: a wave of the gods' colours from where she arrives to both ends
        if T_ARRIVE - 0.3 <= t < T_ARRIVE + 3.5:
            age = t - (T_ARRIVE - 0.3)
            pa = C['freia'][int(T_ARRIVE / DT)]
            r = 1600 * smoothstep(0, 2.2, age)
            band = np.exp(-((np.abs(d - pa) - r) / 160) ** 2) * (1 - smoothstep(2.0, 3.8, age))
            wave = hue(d / 500 + 0.3 * t)
            fr += light(wave, 0.85 * band)
            fr += light(FREIA, 0.5 * band)
        lv = recent(loves, t, 0.4)
        if lv > 0 and t >= T_LOVE:
            fr += light(FREIA, 0.3 * lv * np.exp(-((d - C['freia'][f]) / 200) ** 2))
            fr += light(CASTLE, 0.25 * lv * mason * porch)
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
    pe = pan_at(at(G, 'Porch Left', 1.0))

    def pan_of(who, t):
        return pan_at(np.interp(t, C['t'], C[who]))

    for name, gain, rev in (('strings', 0.14, 0.32), ('low', 0.18, 0.2), ('winds', 0.17, 0.35),
                            ('brass', 0.16, 0.3), ('perc', 0.2, 0.25), ('harp', 0.18, 0.4), ('glock', 0.08, 0.4)):
        M.bus(name, gain=gain, reverb=rev)
    vn = M.sampler('Strings/Violin Section/susVib/*.wav', tune=-12)
    va = M.sampler('Strings/Viola Section/susvib/*.wav', tune=-12)
    vc = M.sampler('Strings/Cello Section/susvib/*.wav', tune=-12)
    vtrem = M.sampler('Strings/Violin Section/Trem/*.wav', tune=-12)
    trem = M.sampler('Strings/Cello Section/trem/*.wav', tune=-12)
    cb = M.sampler('Strings/Solo Contrabass/SusNV/*.wav', tune=-12)
    cbtrem = M.sampler('Strings/Solo Contrabass/Trem/*.wav', tune=-12)
    pizz = M.sampler('Strings/Solo Contrabass/Pizz/*.wav', tune=-12)
    fl = M.sampler('Woodwinds/Flute/susvib/*.wav', tune=-12)
    ob = M.sampler('Woodwinds/Oboe/Vib/*.wav', tune=-12)
    cl = M.sampler('Woodwinds/Clarinet/susLong/*.wav', tune=-12)
    bsn = M.sampler('Woodwinds/Bassoon/sus/*.wav', tune=-12)
    horn = M.sampler('Brass/F Horn/sus/*.wav', tune=-12)
    tbn = M.sampler('Brass/Tenor Trombone/sus/*.wav', tune=-12)
    tpt = M.sampler('Brass/Trumpet/sus/*.wav', tune=-12)
    tuba = M.sampler('Brass/Tuba/sus/*.wav', tune=-12)
    glock = M.sampler('Percussion/Glock/*.wav', tune=-12)
    harp = M.sampler('Strings/Harp/*.wav')
    timp = M.hits('Percussion/Timpani/Timpani1_Hit*.wav')
    roll = M.hits('Percussion/Timpani/Rolls/*.wav')
    bd = M.hits('Percussion/BDrumNewhit_v[4-7]*.wav')
    crash = M.hits('Percussion/cymbal-crash1_f*.wav')
    scrape = M.hits('Percussion/gongscrape_pp.wav')
    gong = M.hits('Percussion/gongHit_p.wav')

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
        if part == 'trem':
            hold('strings', vtrem if m >= note('C4') else trem, m, t, t + d, v, 0.0, rise=0.05, fall=2.5, gain=1.0)
        elif part == 'roll':
            M.add('perc', roll.play(v, dur=d + 0.5), t, 0.7, 0.0)
        elif part == 'earth':
            hold('low', cbtrem, m + 12, t, t + d, v, pe, rise=4.0, fall=4.0, gain=0.7)
            hold('low', cb, m + 12, t, t + d, v - 10, pe, rise=5.0, fall=4.0, gain=0.55)
        elif part == 'scrape':
            M.add('perc', scrape.play(100), t, 0.8, pe)
        elif part == 'pedal':
            hold('low', cb, m, t, t + d, v, pe, rise=1.0, fall=1.5, gain=0.7)
            hold('low', vc, m + 12, t, t + d, v - 10, pe, rise=1.0, fall=1.5, gain=0.45)
            M.add('brass', tuba.play(m, v - 16, dur=d, release=1.0), t, 0.4, pe)
        elif part == 'erda':
            if who == 0:
                s = bsn if m < note('Ab3') else cl
                M.add('winds', s.play(m, v, dur=d * 1.05, release=0.4), t, 0.7, pe)
            else:
                M.add('brass', horn.play(m, v, dur=d * 1.05, release=0.4), t, 0.65, pe)
                M.add('winds', cl.play(m, v - 10, dur=d * 1.05, release=0.4), t, 0.6, pe)
                M.add('winds', bsn.play(m - 12, v - 6, dur=d * 1.05, release=0.4), t, 0.55, pe)
        elif part == 'swell':
            M.add('perc', gong.play(90), t, 0.6, pe)
        elif part == 'warn':
            M.add('winds', bsn.play(m, v, dur=d, release=0.3), t, 1.0, pe)
            M.add('brass', horn.play(m, v - 14, dur=d, release=0.3), t, 0.7, pe)
        elif part == 'down':
            M.add('brass', tbn.play(m - 12, v, dur=d * 1.05, release=0.5), t, 0.9, hc)
            M.add('brass', horn.play(m, v - 8, dur=d * 1.05, release=0.5), t, 0.7, hc)
            hold('strings', va, m, t, t + d, v - 18, hc, rise=0.4, fall=0.8, gain=0.4)
        elif part == 'downpedal':
            hold('low', cb, m, t, t + d, v, hc, rise=1.0, fall=1.5, gain=0.9)
            M.add('brass', tuba.play(m, v - 10, dur=d, release=1.0), t, 0.8, hc)
        elif part == 'sink':
            M.add('winds', bsn.play(m + 12, v, dur=d, release=0.5), t, 0.9, pe)
            hold('low', cb, m + 12, t, t + d, v, pe, rise=0.3, fall=1.0, gain=0.7)
        elif part == 'ring':
            p = pan_at(np.interp(t, C['t'], C['ring']))
            M.add('winds', (cl if m < note('E4') else ob).play(m, v, dur=d * 1.05, release=0.3), t, 0.9, p)
            M.add('brass', horn.play(m - 12, v - 16, dur=d * 1.05, release=0.3), t, 0.4, p)
        elif part == 'ringbass':
            hold('low', vc, m + 12, t, t + d, v - 8, hc, rise=0.6, fall=1.0, gain=0.7)
        elif part == 'land':
            M.add('glock', glock.play(m, v), t, 1.0, hc)
            M.add('perc', timp.play(100, pitch=-3), t, 0.7, hc)
            M.add('harp', harp.play(m - 12, v), t, 0.8, hc)
        elif part == 'pull':
            p = pan_of(who, t)
            M.add('perc', timp.play(v, pitch=-5), t, 0.9, p)
            M.add('perc', bd.play(v - 8), t, 0.7, p)
            M.add('brass', tuba.play(m + 12, v, dur=d, release=0.3), t, 0.8, p)
        elif part == 'burst':
            M.add('perc', crash.play(v), t, 0.8, hc)
            M.add('perc', timp.play(v, pitch=-1), t, 0.8, hc)
            gl = [x for x in range(m, m + 31) if (x - m) % 12 in (0, 4, 7)]
            for i, x in enumerate(gl):
                M.add('harp', harp.play(x, 90 + i), t + i * 0.06, 1.0, hc - 0.8 * i / len(gl))
            M.add('winds', whoosh(0.9, 500, 5000, 0.4, seed=5), t, 0.6, hc)
        elif part == 'freia':
            p = pan_of('freia', t)
            M.add('strings', vn.play(m + 12, v, dur=d * 1.05, release=0.25), t, 1.0, p)
            M.add('winds', fl.play(m + 12, v - 14, dur=d * 1.05, release=0.25), t, 0.6, p)
        elif part == 'freialow':
            M.add('low', pizz.play(m + 12, v - 6), t, 0.8, pan_of('freia', t))
            M.add('strings', va.play(m + 12, v - 20, dur=d, release=0.2), t, 0.5, pan_of('freia', t))
        elif part == 'gliss':
            gl = [x for x in range(m, m + 31) if (x - m) % 12 in (2, 6, 9)]
            for i, x in enumerate(gl):
                M.add('harp', harp.play(x, 92 + i), t + i * d / len(gl), 1.0, -0.7 + 1.4 * i / len(gl))
        elif part == 'crash':
            M.add('perc', crash.play(v), t, 0.9, 0.0)
            M.add('perc', timp.play(v, pitch=-2), t, 0.9, 0.0)
            M.add('perc', bd.play(v), t, 0.6, 0.0)
        elif part == 'love':
            M.add('strings', vn.play(m, v, dur=d * 1.05, release=0.4), t, 1.5, -0.3)
            M.add('strings', vn.play(m - 12, v - 6, dur=d * 1.05, release=0.4), t, 1.1, 0.3)
            M.add('winds', fl.play(m, v - 10, dur=d * 1.05, release=0.4), t, 0.8, 0.0)
            M.add('brass', tpt.play(m - 12, v - 14, dur=d * 1.05, release=0.4), t, 0.5, 0.1)
        elif part == 'lovemid':
            M.add('brass', horn.play(m, v, dur=d * 1.05, release=0.4), t, 1.1, -0.1)
            hold('strings', va, m, t, t + d, v - 8, 0.1, rise=0.2, fall=0.6, gain=0.8)
        elif part == 'lovebass':
            M.add('low', tuba.play(m, v - 6, dur=d, release=0.5), t, 1.0, 0.0)
            hold('low', cb, m, t, t + d, v, 0.0, rise=0.2, fall=0.8, gain=1.0)
        elif part == 'harp':
            M.add('harp', harp.play(m, v), t, 1.0, -0.4 + 0.15 * (m % 7))
        elif part == 'chord':
            hold('strings', vn if m >= note('D4') else va, m, t, t + d, v, 0.0, rise=1.0, fall=2.0, gain=0.6)
            M.add('winds', (fl if m >= note('D4') else cl).play(m, v - 20, dur=3.0, release=1.0), t, 0.4, 0.0)
        elif part == 'chordbass':
            hold('low', cb, m, t, t + d, v, 0.0, rise=1.0, fall=2.0, gain=0.7)
        elif part == 'giants':
            p = pan_of('fafner', t)
            M.add('brass', tuba.play(m, v, dur=d * 1.05, release=0.2), t, 0.9, p)
            M.add('brass', tbn.play(m + 12, v - 16, dur=d * 1.05, release=0.2), t, 0.5, p)
