"""Erda: the light goes out of the mountain and the ancient earth itself rises out of the back corner of the porch
to warn Wotan; then he gives up the ring, Freia bursts out of the gold, and colour floods back over the gods.

The music is Wagner's own: three passages of the last scene of Das Rheingold (bars 3458-3464, 3499-3504 and
3564-3575) as Solti's 1958 Vienna Philharmonic recording takes them, from the Wagner Ring Dataset's piano
reduction (pixelhome/ring.py). Erda's motif climbs bar after bar in the bassoons, clarinets and horns over the
low strings, and her own voice sings over it, played on a horn doubled by a clarinet: "Weiche, Wotan! Weiche! Flieh'
des Ringes Fluch!" and, after her vision, "Alles was ist, endet! Ein düstrer Tag dämmert den Göttern", the
downfall of the gods on soft trombones beneath the monotone. Her lines come from the printed vocal score (Schott,
archive.org dasrheingold00wagn2, pp. 192-194). Then the full orchestra with harps for Freia's release. The
staging's sounds: the earth groaning as she rises, a gong for the end of all things, a scrape and a rumble as she
sinks; then the ring clinking down, the staves wrenched out, the heap bursting with a rush and a cymbal as Freia
reaches the gods. They stay low under her voice.

Out of the back corner of the porch a deep earth light seeps up, moss green and churning like soil turning over,
and every chord of her motif and every note she sings swells it out along the porch in rings until it fills the
battlements and seeps across the meadow. At "Alles was ist, endet" a shadow sweeps out from the castle to both
ends of the house and the gods go grey to the bone; on "den Göttern" her light draws back into the corner and
sinks away. The light comes back to the mountain and Wotan gives up the ring: the small gold point travels from
his hand along Porch Front and drops into the gap where Freia's eye showed. The staves come out, the heap bursts
open, and Freia leaps out in a spray of pink and runs down Porch Left and along Left to the gods; as she reaches
them their colours flood back in a wave across the whole house, while the giants push the gold back into a pile.

compose() tags the music's moments, choreography() every position; render() and score() read both."""
import numpy as np
from pixelhome.audio import note
from pixelhome.fx import DT, hexc, light, smoothstep, nframes, Flicker
from pixelhome.ring import Orchestra, excerpt, tidy

CODE = 'RG22'
TITLE = 'Erda'
KIND = 'show'
DESCRIPTION = ('The mountain goes dark, and the ancient earth itself rises out of the porch in a deep green '
               'light to warn Wotan: the ring brings only ruin. He listens, and gives it up. The heap opens, '
               'Freia runs free, and the gods get their colour back.')
VOICEOVER = ('Something older than the gods is waking under the mountain. '
             'When the earth itself tells you to let go, you let go.')

EX = excerpt(__file__)                      # bars 3458-3464, 3499-3504, 3564-3575, Solti 1958
BAR = {int(m): t for m, t in EX['bars']}
SEG = [g['start'] for g in EX['segments']] + [EX['seconds']]
T_DARK = 0.0                                # the light drains out of the mountain
T_RISE = 3.0                                # the earth light has seeped up
T_ERDA = [0.0, BAR[3459]]                   # her motif climbing, bar after bar
T_DOWN = SEG[1]                             # "Alles was ist, endet!": the downfall of the gods
T_SINK = BAR[3504]                          # "...den Göttern": she sinks back
T_LIGHT = SEG[2]                            # light returns
T_YIELD = SEG[2]                            # Wotan gives up the ring
T_LAND = 68.69                              # the ring fills the gap
T_PULL = [BAR[3566], 70.3]                  # the staves pulled out
T_FREE = 70.3                               # the heap bursts, Freia runs
T_ARRIVE = 74.24                            # she reaches the gods: colour floods back
T_LOVE = BAR[3569]                          # Freia's love, full orchestra
T_CODA = BAR[3572]
T_CLOSE = BAR[3572] + 0.6                   # the giants push the gold back into one pile
D = EX['seconds']
T0 = 80.0                                  # the opera's clock at our start: steady motion carries across the cuts

# Erda's two lines, from the vocal score: (bar, beat, beats, note), 4/4
VOICE = [(3461, 0, 1.5, 'G#4'), (3461, 1.5, 0.5, 'E4'), (3461, 2, 1, 'E4'), (3461, 3, 1, 'C#4'),
         (3462, 0, 2, 'C#5'), (3462, 2, 0.5, 'C#4'),
         (3463, 0, 1.5, 'C#5'), (3463, 1.5, 0.5, 'C#5'), (3463, 2, 1.5, 'A4'), (3463, 3.5, 0.5, 'F#4'),
         (3464, 0, 2, 'C5'),
         (3499, 0, 1, 'G#4'), (3499, 1, 0.5, 'G#4'), (3499, 1.5, 0.5, 'G#4'), (3499, 2, 2, 'E5'),
         (3500, 0, 2, 'C#5'), (3500, 2, 1, 'C#4'), (3501, 3, 1, 'A4'), (3502, 0, 3, 'A4'), (3502, 3, 1, 'A4'),
         (3503, 0, 2, 'A4'), (3503, 2, 1, 'A4'), (3503, 3, 0.5, 'A4'), (3503, 3.5, 0.5, 'A4'),
         (3504, 0, 2, 'A4'), (3504, 2, 1, 'A#3')]

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


def voice():
    """Erda's lines in seconds: (time, seconds, midi)."""
    out = []
    for b, x, n, name in VOICE:
        seg = next(g for g in EX['segments'] if g['measures'][0] <= b < g['measures'][1])
        bars = [(m, t) for m, t in EX['bars'] if seg['measures'][0] <= m <= seg['measures'][1]]
        bars = sorted({m: t for m, t in bars if t >= seg['start'] - 1e-6}.items())
        when = lambda pos: float(np.interp(pos, [q[0] for q in bars], [q[1] for q in bars]))
        t0 = when(b + x / 4)
        out.append((t0, when(b + (x + n) / 4) - t0, note(name)))
    return out


def compose():
    """The music's moments, from the excerpt's real notes and Erda's voice: (time, seconds, midi, velocity, part,
    who). 'erda' is a chord of her motif or a note she sings (her light swells), 'down' a chord of the downfall,
    'ring' the ring on its way, 'pull' a staff pulled out, 'freia' her running music, 'love' the love music."""
    N = []
    seen = set()
    for t, d, m, v, h in EX['notes']:
        key = round(t, 2)
        if t < SEG[1]:
            if d >= 0.3 and (key, 'e') not in seen:
                seen.add((key, 'e'))
                N.append((t, d, m, v, 'erda', 0 if t < T_ERDA[1] else 1))
        elif t < SEG[2]:
            if d >= 0.3 and (key, 'd') not in seen:
                seen.add((key, 'd'))
                N.append((t, d, m, v, 'down', None))
        elif t < T_FREE:
            if h == 0 and d >= 0.3:
                N.append((t, d, m, v, 'ring', None))
        elif t < T_LOVE:
            if h == 0:
                N.append((t, d, m, v, 'freia', None))
        elif d >= 0.3 and (key, 'l') not in seen:
            seen.add((key, 'l'))
            N.append((t, d, m, v, 'love', None))
    for t, d, m in voice():
        N.append((t, d, m, 0, 'erda', 1))
    for i, tp in enumerate(T_PULL):
        N.append((tp, 0.6, 36, 0, 'pull', ('fafner', 'fasolt')[i]))
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
        rise = smoothstep(T_DARK, T_RISE, t) * (1 - smoothstep(T_SINK, T_SINK + 6, t))
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
    """Wagner's notes, orchestrated from the piano reduction, Erda's voice on a horn, the staging's sounds over it."""
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

    o = Orchestra(M, level=2.6)

    def role(t, d, m, v, h):
        if t < SEG[1]:                                  # her motif: low winds and horns over the low strings
            if h == 1 or m < 52:
                return [('cellos', 0, 10, 0.6), ('bassoons', 0, 8, 0.5), ('basses', -12 if m >= 40 else 0, 0, 0.4)]
            return [('clarinets', 0, 14, 0.55), ('horns', 0, 6, 0.45 if t >= T_ERDA[1] else 0.0),
                    ('violas', 0, 4, 0.35)]
        if t < SEG[2]:                                  # the downfall: soft trombones, the strings trembling
            if h == 1 or m < 52:
                return [('trombones', 0, 12, 0.55), ('tuba', 0, 4, 0.4 if m < 48 else 0.0), ('cellos', 0, 6, 0.45)]
            return [('violas', 0, 8, 0.45), ('clarinets', 0, 4, 0.35)]
        if h == 0 and t >= T_FREE:                      # Freia free: the harps with the violins
            return [('violins', 0, 0, 0.55), ('harp', 0, 4, 0.4), ('flutes', 0, -8, 0.35 if m >= 72 else 0.0)]
        return None

    o.tutti(tidy(EX['notes']), size=lambda t: 1.0 if t >= T_FREE else 0.55, role=role)
    for t, d, m in voice():                             # Erda: a horn, a clarinet with it
        o.play('horns', m, t, d, 100, pe, 0.85)
        o.play('clarinets', m, t, d, 84, pe, 0.4)

    o.effects([(0.0, 0.0), (12.0, -2.0), (15.0, -14.0), (SEG[2] - 4.0, -14.0), (SEG[2] - 1.0, 0.0)])
    o.thunder(0.2, near=0.05, pan=pe, gain=0.9)        # the earth groans as she rises
    o.hit('gong scrape', 0.5, 100, gain=0.45, pan=pe)
    o.hit('gong', T_DOWN, 96, gain=0.45, pan=hc)        # the end of all things
    o.hit('timpani roll', T_DOWN, 84, pitch=-5, gain=0.35)
    o.hit('gong scrape', T_SINK, 92, gain=0.4, pan=pe)  # she sinks
    o.thunder(T_SINK + 1.0, near=0.0, pan=pe, gain=0.6)
    o.play('glock', 88, T_LAND, 0.1, 96, hc, 0.4)      # the ring drops into the gap
    o.hit('triangle', T_LAND, 92, gain=0.35, pan=hc)
    for i, tp in enumerate(T_PULL):                     # the staves wrenched out
        o.hit('bass drum', tp, 112, gain=0.5, pan=pan_of(('fafner', 'fasolt')[i], tp))
        o.hit('brake drum', tp, 96, gain=0.2, pan=pan_of(('fafner', 'fasolt')[i], tp))
    from pixelhome.audio import whoosh
    o._sfx(whoosh(0.9, 400, 4000, 0.6, seed=22)[0], T_FREE - 0.2, 0.9, hc)   # the heap bursts
    o.hit('crash', T_FREE, 112, gain=0.45, pan=hc)
    o.hit('crash', T_ARRIVE, 118, gain=0.55, pan=pan_of('freia', T_ARRIVE))  # she reaches the gods
    o.hit('timpani', T_ARRIVE, 112, pitch=-3, gain=0.5)
    o.hit('scrape', T_CLOSE, 96, gain=0.35, pan=pan_of('fafner', T_CLOSE))   # the gold pushed back together
