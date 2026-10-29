"""The Workshop: the whole town making toys, and the toys have ideas of their own. A conveyor runs the
length of the roof from the free right end toward the back of Side, carrying blocks of colour, and
a hammer swings down on every beat at each corner of the house in turn. More and more of the blocks
come out wrong (purple, orange, sickly green) and jiggle as they ride.

The live ones: a teddy bear wobbles on the beat, topples flat on his face, and bounces back up. A
striped toy snake slithers along, lunges at the block in front of it and gulps it whole; the lump
travels down its body and it burps. A wind-up mouse zips off backwards against the belt, gets wound
up again, races forwards, and flips over. A jack-in-the-box pops out on the first beat of each bar,
higher every time; the box rattles, and the last one goes BOING and stays out. The line stops, three
big hammer blows, a gold ribbon wraps the house from the porch out, red and green stripes behind it,
and a big bow pops onto the porch with a burst of sparkles.

Everything lives in path distance. Belt slots are GAP apart and move at V; each toy owns a slot chosen
so it is in view at its gag. Times are on the 132 BPM grid (bt(bar, beat)) that score() shares."""
import numpy as np
from pixelhome.fx import DT, hexc, light, perc, smoothstep, keys, lerp, nframes

CODE = 'NB06'
TITLE = 'The Workshop'
KIND = 'show'
DESCRIPTION = ('Toys ride a conveyor along the roof while hammers ring the tune at every corner. A teddy falls '
               'over, a snake gulps a block, a wind-up mouse runs backwards and a jack-in-the-box goes BOING.')

BPM = 132
BEAT = 60 / BPM
BAR = 4 * BEAT


def bt(bar, beat=0.0):
    return (4 * bar + beat) * BEAT


WARM = hexc('#401400')
GOOD = [hexc(c) for c in ('#ff1a10', '#10d040', '#ffb020', '#2a60ff')]
WRONG = [hexc(c) for c in ('#7a10ff', '#ff5a00', '#80ff10')]
HAMMER = hexc('#fff0c0')
STEEL = hexc('#c8d0e0')
WELD = hexc('#c0d8ff')
GOLD = hexc('#ffb020')
RED = hexc('#ff1a10')
GREEN = hexc('#10d040')
FUR = hexc('#c06418')
EAR = hexc('#ffa050')
SNAKE = [hexc('#30e040'), hexc('#8020ff')]
SNAKE_HEAD = hexc('#c0ff40')
TONGUE = hexc('#ff1020')
MOUSE = hexc('#a8b0c8')
PINK = hexc('#ff6aa0')
BOX = hexc('#ff2010')
SPRING = hexc('#d8e0f0')
FACE = hexc('#ffe8c8')
HAT = [hexc('#a020ff'), hexc('#20d060')]
CORNERS = (80.5, 178.5, 260.5, 331.5, 380.5)      # path indices between the runs

V, GAP, BLOCK = 110.0, 70.0, 38.0           # belt speed, slot spacing, block length
BELT_ON = bt(2)                             # the hammers start; the band is in
WOBBLE = (bt(4), bt(9))                     # the teddy wobbles on the beat
TOPPLE, UP = bt(7, 3), bt(9)                # ...falls flat, bounces back up
LUNGE, BURP = bt(13), bt(14, 2)             # the snake gulps the block ahead; the lump reaches its tail
ZIP1, WIND, ZIP2, FLIP = bt(18), bt(19, 2), bt(20), bt(21, 3)   # the wind-up mouse
JACKS = [(bt(22), 38.0), (bt(23), 52.0), (bt(24), 66.0), (bt(25, 2), 125.0)]   # pops: (time, height)
RATTLE = (bt(25), bt(25, 2))                # the box rattles before the big one
WELDING = (bt(10), bt(18))
STOP = bt(26)                               # the line stops
BLOWS = (bt(26, 0), bt(26, 1), bt(26, 2))   # three big blows
WRAP, WRAP_V = bt(27), 420.0                # the ribbon leaves the porch, and its speed
BOW_T = bt(29)                              # the bow pops on
D = 57.0


def _back(u, c1=1.7):
    u = np.clip(u, 0, 1)
    return 1 + (c1 + 1) * (u - 1) ** 3 + c1 * (u - 1) ** 2


def belt(t):
    """How far the belt has moved: V a second, easing to a stop over the last half second before STOP."""
    s0 = STOP - 0.5
    if t < s0:
        return V * t
    u = min((t - s0) / 0.5, 1.0)
    return V * s0 + V * 0.5 * (u - u * u / 2)


def slot_x(G, i, t):
    """Centre of belt slot i at time t. The belt runs from the free right end toward Side, so higher slots
    come in later off the right end; the low ones leave along Side."""
    return GAP * (i + 0.5) - belt(t)


def slots(G):
    """Which slot each live toy rides in, chosen so its gag happens on a front run."""
    c0 = float(G.pd[G.seg['Porch Front']].mean())

    def at(t, x):
        return int(round((x + belt(t)) / GAP - 0.5))
    snake = at(LUNGE, c0 + 100) - 1         # the snake takes slots i and i+1, head first; its victim is i-1
    return dict(teddy=at(TOPPLE, 1050.0), snake=snake, victim=snake - 1, mouse=at(ZIP1, c0 - 200),
                jack=at(bt(23, 2), c0))


def snake_ends(G, i, t):
    """The snake's head (leading, toward Side) and tail, lunging LUNGE..BURP."""
    xs = GAP * (i + 1) - belt(t)
    ext = keys(t, [(LUNGE - BEAT, 0), (LUNGE, 46), (LUNGE + 2 * BEAT, 46), (BURP + BEAT, 0)])
    return xs - 60 - ext, xs + 60


def toys(G, seed=61):
    """The random parts: for each slot whether its block came out wrong, its colour index and wiggle phase;
    and the welding sparks' times and pixels."""
    rng = np.random.default_rng(seed)
    d = G.pd[G.path]
    corner = np.interp(CORNERS, np.arange(G.N), d)
    NB = int((belt(D) + G.length) / GAP) + 2
    spawn = (GAP * np.arange(NB) - G.length) / V            # about when slot i passes d=0
    wrong = rng.random(NB) < np.clip((spawn - 6) / 30, 0, 0.6)
    ci = np.array([rng.integers(3 if w else 4) for w in wrong])
    wig = rng.uniform(0, 2 * np.pi, NB)
    W = 220
    w0 = rng.uniform(*WELDING, W)
    wpx = np.array([np.argmin(np.abs(d - corner[k])) + rng.integers(-6, 7) for k in rng.integers(0, 5, W)])
    return wrong, ci, wig, w0, np.clip(wpx, 0, G.N - 1)


def hammer_beats():
    """(time, corner index) for every hammer stroke: a count-in in bar one, then every beat to the stop."""
    out = [(bt(1, b), b % 5) for b in range(4)]
    nb = int(round(BELT_ON / BEAT))
    while nb * BEAT < STOP - 1e-6:
        out.append((nb * BEAT, nb % 5))
        nb += 1
    return out


def mouse_x(G, t, i):
    """The wind-up mouse: rides its slot, zips back 700 units against the belt, is wound, races forward 600,
    flips."""
    x = slot_x(G, i, min(t, ZIP1))
    if t >= ZIP1:
        x -= belt(t) - belt(ZIP1)
        x += 700 * smoothstep(0, 1, np.clip((t - ZIP1) / 2.6, 0, 1) ** 0.8)
    if t >= ZIP2:
        x -= 600 * smoothstep(0, 1, np.clip((t - ZIP2) / 2.4, 0, 1)) ** 1.3
    return x


def jack_height(t):
    """How far the jack is out of his box."""
    h = 0.0
    for k, (tj, a) in enumerate(JACKS):
        if t < tj:
            continue
        u = t - tj
        last = k == len(JACKS) - 1
        up = a * _back(u / 0.2) * (1 + 0.12 * np.sin(2 * np.pi * 6 * u) * np.exp(-3 * u))
        if not last:
            up *= 1 - smoothstep(2 * BEAT, 3 * BEAT, u)
        else:
            up *= 1 - 0.3 * smoothstep(STOP, STOP + 1.0, t)
        h = max(h, up)
    return h


def render(G, seed=61):
    F = nframes(D)
    out = np.zeros((F, G.N, 3))
    L = G.length
    d = G.pd[G.path]
    w = np.gradient(d)
    e0, e1 = d - w / 2, d + w / 2
    mid = G.pd[G.seg['Porch Front']].mean()
    r = np.abs(d - mid)
    corner = np.interp(CORNERS, np.arange(G.N), d)
    wrong, ci, wig, w0, wpx = toys(G, seed)
    NB = len(wrong)
    col = np.array([(WRONG if wr else GOOD)[c] for wr, c in zip(wrong, ci)])
    S = slots(G)
    special = {S['teddy'], S['snake'], S['snake'] + 1, S['mouse'], S['jack']}
    HB = hammer_beats()
    rng = np.random.default_rng(seed + 1)
    bow_sp = rng.uniform(-1, 1, 40) * rng.uniform(150, 600, 40)
    bow_c = rng.integers(0, 4, 40)

    def paint(spans):
        """Spans (a, z, intensity, colour) -> PWM by exact span-over-pixel coverage, and the coverage."""
        if not spans:
            return np.zeros((G.N, 3)), np.zeros(G.N)
        A, Z, Ks, C = (np.array([s[k] for s in spans]) for k in range(4))
        ov = np.clip(np.minimum(Z[:, None], e1) - np.maximum(A[:, None], e0), 0, None) / w
        return (perc(np.clip(Ks, 0, 1.2))[:, None] * ov).T @ C, np.clip(ov.sum(0), 0, 1)

    for f in range(F):
        t = f * DT
        spans = []
        lev = keys(t, [(0.5, 0), (2.5, 1), (D - 2, 1), (D - 0.2, 0)])

        def put(a, z, I, c):
            spans.append((a, z, I * lev, c))

        # the plain blocks
        for i in range(NB):
            if i in special or (i == S['victim'] and t >= LUNGE + 0.08):
                continue
            x = slot_x(G, i, t)
            if -40 < x < L + 40:
                I = 0.5 * (0.75 + 0.25 * np.sin(2 * np.pi * 3 * t + wig[i]) if wrong[i] else 1.0)
                if wrong[i]:
                    x += 3 * np.sin(2 * np.pi * 5 * t + wig[i])
                put(x - BLOCK / 2, x + BLOCK / 2, I, col[i])

        # the teddy: wobbles on the beat, falls flat, bounces up
        x = slot_x(G, S['teddy'], t)
        st, I = 1.0, 0.75
        if WOBBLE[0] <= t < TOPPLE or UP + 0.4 <= t < WOBBLE[1]:
            x += 6 * np.sin(np.pi * t / BEAT)
        if TOPPLE <= t:
            down = smoothstep(TOPPLE, TOPPLE + 0.18, t) * (1 - _back((t - UP) / 0.35, 2.2) if t >= UP else 1)
            st = 1 + 0.6 * down
            x -= 14 * down
            I = 0.75 - 0.25 * down + 0.4 * np.exp(-max(t - TOPPLE - 0.18, 0) / 0.12) * (t >= TOPPLE + 0.18)
        a = x - 22 * st
        put(a, a + 26 * st, I, FUR)
        put(a + 26 * st, a + 30 * st, I, RED)
        put(a + 30 * st, a + 33 * st, I, EAR)
        put(a + 33 * st, a + 41 * st, I, FUR)
        put(a + 41 * st, a + 44 * st, I, EAR)

        # the snake: two slots long, slithering; lunges, gulps, the lump travels back, burps
        head, tail = snake_ends(G, S['snake'], t)
        n = int((tail - head - 14) // 12)
        for k in range(n):
            v1 = tail - 12 * k
            wave = 0.7 + 0.3 * np.sin(2 * np.pi * (k / 3.2 - 2.2 * t))
            put(max(v1 - 12, head + 14), v1, 0.7 * wave, SNAKE[k % 2])
        put(head + 8, head + 14, 0.85, SNAKE_HEAD)
        put(head, head + 5, 0.85, SNAKE_HEAD)
        if np.sin(2 * np.pi * 4.5 * t) > 0.3 and not (LUNGE - 0.1 < t < LUNGE + 0.3):
            put(head - 7, head, 0.8, TONGUE)
        if LUNGE <= t < BURP:                     # the lump, in the swallowed block's colour
            u = (t - LUNGE) / (BURP - LUNGE)
            lx = lerp(head + 20, tail - 12, smoothstep(0, 1, u))
            put(lx - 13, lx + 13, 0.85, col[S['victim']])
        if LUNGE - 0.05 <= t < LUNGE + 0.08:     # the victim, being swallowed
            vx = slot_x(G, S['victim'], t)
            put(vx - BLOCK / 2, vx + BLOCK / 2, 0.6, col[S['victim']])
        if t >= BURP:
            u = t - BURP
            put(head - 6, head + 6, 0.9 * np.exp(-u / 0.2), WELD)
            for k in range(3):
                bx = head - 14 - 18 * k - 40 * u
                if u < 1.2:
                    put(bx - 2.5, bx + 2.5, 0.6 * (1 - u / 1.2), SNAKE[0])

        # the wind-up mouse: runs backwards, gets wound, races forwards, flips
        x = mouse_x(G, t, S['mouse'])
        dead = smoothstep(FLIP, FLIP + 0.15, t)
        I = 0.8 - 0.3 * dead + 0.5 * np.exp(-max(t - FLIP, 0) / 0.15) * (t >= FLIP)
        stt = 1 + 0.3 * dead
        key_on = ((t * (14 if WIND <= t < ZIP2 else 4)) % 1) < 0.5
        put(x + 12 * stt, x + 24 * stt, 0.35 * I, PINK)                 # tail (it faces down the belt)
        put(x - 6 * stt, x + 12 * stt, I, MOUSE)
        put(x - 9 * stt, x - 6 * stt, I, PINK)                          # ear
        put(x - 12 * stt, x - 9 * stt, I, MOUSE)
        put(x - 15 * stt, x - 12 * stt, I, PINK)                        # nose
        if key_on and dead < 0.5:
            put(x + 2, x + 6, 0.9 * I, STEEL)
        if (ZIP1 < t < ZIP1 + 2.6) or (ZIP2 < t < ZIP2 + 2.4):           # speed lines
            v = (x - mouse_x(G, t - DT, S['mouse'])) / DT
            if abs(v) > 150:
                sgn = -np.sign(v)
                for q, k in enumerate((0.45, 0.25, 0.1)):
                    a0 = x + sgn * (16 + 14 * q)
                    put(min(a0, a0 + sgn * 14), max(a0, a0 + sgn * 14), k, MOUSE)

        # the jack-in-the-box
        x = slot_x(G, S['jack'], t)
        if RATTLE[0] <= t < RATTLE[1]:
            x += 3 * np.sin(2 * np.pi * 13 * t)
        put(x - 17, x - 2, 0.75, BOX)
        put(x - 2, x + 2, 0.85, GOLD)
        put(x + 2, x + 17, 0.75, BOX)
        h = jack_height(t)
        if h > 1:
            base = x + 17
            nz = max(1, int(h // 5))
            for k in range(nz):
                put(base + k * h / nz, base + (k + 0.6) * h / nz, 0.7, SPRING)
            hx = base + h
            put(hx, hx + 4, 0.85, FACE)
            put(hx + 7, hx + 9, 0.85, FACE)
            put(hx + 12, hx + 16, 0.85, FACE)
            put(hx + 16, hx + 21, 0.85, HAT[0])
            put(hx + 21, hx + 26, 0.85, HAT[1])
            put(hx + 26, hx + 29, 1.0, GOLD)

        # the hammer heads swinging down onto the corners
        flash = np.zeros(G.N)
        for th, k in HB:
            u = (t - th) / BEAT
            c = corner[k]
            sgn = 1 if k % 2 else -1
            if -0.5 <= u < 0:
                hx = c + sgn * 55 * (-u / 0.5) ** 2
                put(hx - 10, hx + 10, 0.95, STEEL)
            elif 0 <= u < 0.4:
                hx = c + sgn * 16 * (u / 0.4)
                put(hx - 10, hx + 10, 0.95 * (1 - u / 0.4), STEEL)
                flash = np.maximum(flash, 0.95 * np.exp(-u * BEAT / 0.09) * np.exp(-((d - c) / 42) ** 2))

        buf, cov = paint(spans)

        # the bow on the porch, over the wrapping
        spans = []
        if t >= BOW_T:
            s = _back((t - BOW_T) / 0.3, 2.0)
            put(mid - 46 * s, mid - 6, 0.95, RED)
            put(mid - 6, mid + 6, 1.0, GOLD)
            put(mid + 6, mid + 46 * s, 0.95, RED)
            u = t - BOW_T
            if u < 1.6:
                for v, c in zip(bow_sp, bow_c):
                    bx = mid + v * 0.6 * (1 - np.exp(-u / 0.6))
                    put(bx - 2.5, bx + 2.5, 0.9 * (1 - u / 1.6), GOOD[c])
        top, tcov = paint(spans)

        bg = light(WARM, 0.1 * lev * np.ones(G.N))
        if WELDING[0] <= t < WELDING[1]:
            live = (w0 <= t) & (t < w0 + 0.1)
            wk = np.zeros(G.N)
            wk[wpx[live]] = 0.75
            bg += light(WELD, wk)
        for tb in BLOWS:
            if tb <= t < tb + 1.5:
                big = 0.8 if tb == BLOWS[-1] else 0.55
                bg += light(HAMMER, big * np.exp(-(t - tb) / 0.18) * np.ones(G.N))
        if t >= WRAP:                           # wrapped: stripes behind a gold ribbon
            front = WRAP_V * (t - WRAP)
            fade = keys(t, [(D - 2, 1), (D - 0.2, 0)])
            bg += light(GOLD, 0.85 * fade * np.exp(-((r - front) / 30) ** 2))
            stripe = (d // 40).astype(int) % 2
            behind = smoothstep(front, front - 40, r) * fade
            bg += light(RED, 0.42 * behind * (stripe == 0)) + light(GREEN, 0.42 * behind * (stripe == 1))
            if t >= BOW_T:
                bg += light(HAMMER, 0.7 * np.exp(-(t - BOW_T) / 0.4) * np.ones(G.N))
            buf *= (1 - 0.85 * behind)[:, None]
            cov = cov * (1 - 0.85 * behind)
        out[f][G.path] = np.clip((buf + bg * (1 - cov)[:, None]) * (1 - tcov)[:, None] + top + light(HAMMER, flash), 0, 1)
    return out


# ---------------------------------------------------------------- music ----------------------------------------------
# An assembly-line swing at 132 (swung eighths). The verse is a busy little G minor figure for bassoon and clarinet;
# the chorus is TUNE in Bb, and in the chorus the hammers play it: every stroke that lands on a note of the hook
# rings that note on the glockenspiel as well as the anvil, panned to its corner. The toys get their own sounds:
# the teddy tocks as he wobbles and goes down with a slide and a thud, the snake hisses, gulps and burps on a
# buzz trombone, the mouse runs a xylophone glissando backwards and forwards and squeaks when it flips, and the
# jack goes BOING, bigger each time. Three blows, a harp glissando with the ribbon, and a big Bb for the bow.

TUNE = [                                    # (beat, note, beats): the hook, eight bars of 4/4
    (0, 'Bb4', .5), (.5, 'D5', .5), (1, 'F5', 1), (2, 'Eb5', .5), (2.5, 'D5', .5), (3, 'C5', 1),
    (4, 'D5', .5), (4.5, 'C5', .5), (5, 'Bb4', .5), (5.5, 'G4', .5), (6, 'F4', 2),
    (8, 'Bb4', .5), (8.5, 'D5', .5), (9, 'F5', 1), (10, 'G5', .5), (10.5, 'F5', .5), (11, 'Eb5', 1),
    (12, 'D5', .5), (12.5, 'C5', .5), (13, 'D5', .5), (13.5, 'Eb5', .5), (14, 'F5', 2),
    (16, 'Bb4', .5), (16.5, 'D5', .5), (17, 'F5', 1), (18, 'Eb5', .5), (18.5, 'D5', .5), (19, 'C5', 1),
    (20, 'D5', .5), (20.5, 'C5', .5), (21, 'Bb4', .5), (21.5, 'G4', .5), (22, 'F4', 2),
    (24, 'Eb5', 1), (25, 'G5', 1), (26, 'F5', .5), (26.5, 'Eb5', .5), (27, 'D5', .5), (27.5, 'C5', .5),
    (28, 'Bb4', 3)]
VERSE = [                                   # four bars in G minor, twice; the second time turns toward the chorus
    (0, 'G4', .5), (.5, 'G4', .5), (1, 'Bb4', .5), (1.5, 'G4', .5), (2, 'D5', 1), (3, 'C5', 1),
    (4, 'Bb4', .5), (4.5, 'A4', .5), (5, 'G4', .5), (5.5, 'F#4', .5), (6, 'G4', 2),
    (8, 'G4', .5), (8.5, 'G4', .5), (9, 'Bb4', .5), (9.5, 'G4', .5), (10, 'D5', 1), (11, 'Eb5', 1),
    (12, 'D5', .5), (12.5, 'C5', .5), (13, 'Bb4', .5), (13.5, 'A4', .5), (14, 'D4', 2)]
TURN = [(12, 'A4', .5), (12.5, 'Bb4', .5), (13, 'C5', .5), (13.5, 'D5', .5), (14, 'Eb5', 1), (15, 'F5', 1)]
TUNE_CHORDS = ['Bb', 'F', 'Bb', 'F7', 'Bb', 'F', 'Eb', 'Bb']
VERSE_CHORDS = ['Gm', 'D7', 'Gm', 'D7']
CH = {'Bb': ('F3', 'Bb3', 'D4'), 'F': ('F3', 'A3', 'C4'), 'F7': ('Eb3', 'A3', 'C4'), 'Eb': ('Eb3', 'G3', 'Bb3'),
      'Gm': ('D3', 'G3', 'Bb3'), 'D7': ('D3', 'F#3', 'C4')}
ROOT = {'Bb': ('Bb1', 'F2'), 'F': ('F1', 'C2'), 'F7': ('F1', 'C2'), 'Eb': ('Eb2', 'Bb1'), 'Gm': ('G1', 'D2'),
        'D7': ('D2', 'A1')}
PLAN = [(2, VERSE_CHORDS + VERSE_CHORDS[:3] + ['F7']), (10, TUNE_CHORDS), (18, VERSE_CHORDS),
        (22, TUNE_CHORDS[:4]), (26, ['Bb']), (27, TUNE_CHORDS[6:8]), (29, ['Bb'])]
CHORUS = (10, 18)                           # bars where the hammers ring the hook
REPRISE = (22, 26)


def score(M, G):
    from pixelhome.audio import note as n, slide, whoosh, SR
    tuba = M.sampler('Brass/Tuba/stac/*.wav', tune=-12)
    tuba_s = M.sampler('Brass/Tuba/sus/*.wav', tune=-12)
    bsn = M.sampler('Woodwinds/Bassoon/stac/*.wav', tune=-12)
    clar = M.sampler('Woodwinds/Clarinet/stac/*.wav', tune=-12)
    tpt = M.sampler('Brass/Trumpet/stac/*.wav', tune=-12)
    tpt_s = M.sampler('Brass/Trumpet/sus/*.wav', tune=-12)
    horn = M.sampler('Brass/F Horn/stac/*.wav', tune=-12)
    horn_s = M.sampler('Brass/F Horn/sus/*.wav', tune=-12)
    mute = M.sampler('Brass/F Horn/mute/*.wav', tune=-12)
    buzz = M.sampler('Brass/OldTrombone/Buzz/*.wav', tune=-12)
    pizz = M.sampler('Strings/Cello Section/pizzT/*.wav', tune=-12)
    xylo = M.sampler('Percussion/Xylo/*.wav', tune=-12)
    glock = M.sampler('Percussion/Glock/*.wav', tune=-12)
    harp = M.sampler('Strings/Harp/*.wav')
    anvil = M.hits('Percussion/Anvil_Hit1*.wav')
    brake = M.hits('Percussion/BrakeDrum1_Hammer*.wav')
    snare = M.hits('VSCO 1 Percussion/drums/snare/drum3_marching/snare3_[mp]*.wav')
    sroll = M.hits('Percussion/Snare2-rollSN_v[35]*.wav')
    bd = M.hits('Percussion/BDrumNewhit_v[4-7]*.wav')
    timp = M.hits('Percussion/Timpani/Timpani1_Hit*.wav')
    crash = M.hits('VSCO 1 Percussion/varMetal/Cymbals/clash/crash_hit_ff*.wav')
    crash_s = M.hits('Percussion/cymbal-crashshort*.wav')
    wood = M.hits('VSCO 1 Percussion/varWood/wood_click*.wav')
    clave = M.hits('Percussion/Claves1_Hit*.wav')
    slap = M.hits('VSCO 1 Percussion/varWood/slapstick[0-9].wav')
    guiro = M.hits('Percussion/Guiro-Fast*.wav')
    ratchet = M.hits('Percussion/Ratchet1-Fast*.wav')
    crank = M.hits('Percussion/Ratchet1-Crank*.wav')
    sleigh = M.hits('Percussion/Sleighbells_Hit*.wav')
    btree = M.hits('Percussion/BellTree_Stroke*.wav')
    for name, gain, rev in (('tune', 0.3, 0.18), ('band', 0.24, 0.14), ('bass', 0.4, 0.06), ('hammer', 0.26, 0.12),
                            ('ring', 0.2, 0.25), ('drums', 0.3, 0.1), ('toys', 0.26, 0.15), ('fx', 0.16, 0.2)):
        M.bus(name, gain=gain, reverb=rev)

    L = G.length
    d = G.pd[G.path]
    xs = G.pos[G.path, 0]
    x0, x1 = xs.min(), xs.max()
    corner = np.interp(CORNERS, np.arange(G.N), d)
    mid = float(G.pd[G.seg['Porch Front']].mean())
    S = slots(G)

    def pan_at(q):
        return float(0.85 * (2 * (np.interp(q, d, xs) - x0) / (x1 - x0) - 1))

    def swing(b):                           # straight beat -> swung beat
        k, f = divmod(b, 1)
        return k + (2 / 3 if abs(f - 0.5) < 1e-6 else f)

    def chord_at(t):
        k = int(t // BAR + 1e-6)
        for b0, prog in reversed(PLAN):
            if k >= b0:
                return prog[min(k - b0, len(prog) - 1)]
        return 'Bb'

    def melody(seq, inst, bar0, bus, vel, shift=0, gain=1.0, p=0.0, beats=(0, 999), legato=0.85):
        for b, m, ln in seq:
            if beats[0] <= b < beats[1]:
                t = bt(bar0) + swing(b - beats[0]) * BEAT
                M.add(bus, inst.play(n(m) + shift, vel, dur=ln * BEAT * legato), t, gain, p)

    def band(k0, k1, full=True, stop=False):
        for k in range(k0, k1):
            c = chord_at(bt(k) + 0.01)
            for j in range(4):
                t = bt(k, j)
                if stop and j:              # stop-time: only the one
                    continue
                if j in (0, 2):
                    M.add('bass', tuba.play(n(ROOT[c][j // 2]), 104 if j == 0 else 92), t, 1.0)
                    M.add('drums', bd.play(92 if j == 0 else 74), t, 0.6)
                if j in (1, 3) or stop:
                    for m in CH[c]:
                        M.add('band', (horn if full else pizz).play(n(m), 84, dur=0.18), t, 0.4, -0.3)
                    M.add('drums', snare.play(92), t, 0.55, 0.2)
                if full and not stop:       # swung offbeat comp
                    for m in CH[c]:
                        M.add('band', pizz.play(n(m) + 12, 64), t + 2 / 3 * BEAT, 0.3, 0.3)

    # ---- the factory whistle, the count-in on the hammers ----
    M.add('fx', slide(0.0, 0.05, 880, 880, 0.45, 0.25), 0.4, 0.8)
    M.add('fx', slide(0.0, 0.05, 1100, 1100, 0.6, 0.25), 0.95, 0.8)

    # ---- every hammer stroke: an anvil (or brake drum) at its corner; in the chorus it rings the hook ----
    hook = {}
    for k0, k1 in (CHORUS, REPRISE):
        for b, m, ln in TUNE:
            if float(b).is_integer() and bt(k0) + b * BEAT < bt(k1) - 1e-6:
                hook[round(bt(k0) + b * BEAT, 3)] = m
    for th, k in hammer_beats():
        nb = int(round(th / BEAT))
        p = pan_at(corner[k])
        M.add('hammer', (anvil if nb % 2 == 0 else brake).play(112 if nb % 4 == 0 else 92), th, 1.0, p)
        m = hook.get(round(th, 3))
        if m:
            M.add('ring', glock.play(n(m), 104), th, 1.0, p)
            M.add('ring', xylo.play(n(m), 96), th, 0.6, p)

    # ---- verse: the line starts; bassoon, then clarinet; the teddy wobbles and falls ----
    band(2, 10, full=False)
    melody(VERSE, bsn, 2, 'tune', 104, gain=1.0)
    melody(VERSE[:-5] + TURN, clar, 6, 'tune', 100, gain=0.9)
    tx = lambda t: pan_at(slot_x(G, S['teddy'], t))
    for k in range(int(round((TOPPLE - WOBBLE[0]) / BEAT))):
        t = WOBBLE[0] + k * BEAT
        M.add('toys', wood.play(84, pitch=3 if k % 2 else 0), t, 0.7, tx(t))
    M.add('fx', slide(0.0, 0.3, 900, 300, 0.32, 0.3), TOPPLE - 0.05, 1.0, tx(TOPPLE))
    M.add('drums', bd.play(120), TOPPLE + 0.18, 1.0, tx(TOPPLE))
    M.add('toys', bsn.play(n('E2'), 110, dur=0.3), TOPPLE + 0.25, 0.9, tx(TOPPLE))      # oof
    M.add('fx', slide(0.0, 0.25, 350, 1200, 0.3, 0.3), UP - 0.05, 1.0, tx(UP))
    M.add('toys', slap.play(100), UP + 0.3, 0.6, tx(UP))

    # ---- chorus: the hook on trumpet and clarinet; the snake hisses, gulps, the lump goes down, it burps ----
    band(10, 18)
    M.add('drums', crash.play(110), bt(10), 0.7)
    melody(TUNE, tpt, 10, 'tune', 106, gain=0.85, p=0.1)
    melody(TUNE, clar, 10, 'tune', 96, shift=-12, gain=0.55, p=-0.15)
    sx = lambda t: pan_at(snake_ends(G, S['snake'], t)[0])
    for k in range(6):                      # a hiss as it slithers up to its prey
        t = LUNGE - 6 * BEAT + k * BEAT
        M.add('toys', guiro.play(70), t, 0.5, sx(t))
    M.add('fx', slide(0.0, BEAT * 0.9, 500, 1500, BEAT, 0.3), LUNGE - BEAT, 0.9, sx(LUNGE))
    M.add('drums', timp.play(118), LUNGE, 0.8, sx(LUNGE))
    M.add('toys', bsn.play(n('C3'), 118, dur=0.15), LUNGE, 1.0, sx(LUNGE))           # GULP
    M.add('toys', bsn.play(n('G2'), 118, dur=0.25), LUNGE + 0.17, 1.0, sx(LUNGE))
    steps = int((BURP - LUNGE) / (BEAT / 2))
    for k in range(steps):                  # the lump going down, a step at a time, panned along the snake
        t = LUNGE + 0.4 + k * BEAT / 2
        u = (t - LUNGE) / (BURP - LUNGE)
        hd, tl = snake_ends(G, S['snake'], t)
        x = lerp(hd + 20, tl - 12, u)
        M.add('toys', pizz.play(n('D3') - k, 90), t, 0.7, pan_at(x))
    M.add('toys', buzz.play(n('F2'), 124, dur=0.45), BURP, 1.1, sx(BURP))             # BRAP
    for k in range(3):
        M.add('toys', wood.play(90, pitch=8 + 3 * k), BURP + 0.3 + 0.18 * k, 0.6, sx(BURP))

    # ---- bridge: stop-time, the verse on muted horn; the mouse zips back, is wound, races off, flips ----
    band(18, 22, stop=True)
    melody(VERSE, mute, 18, 'tune', 110, gain=1.0)
    mx = lambda t: pan_at(mouse_x(G, t, S['mouse']))
    for t0, dur, up in ((ZIP1, 2.6, False), (ZIP2, 2.4, True)):
        M.add('toys', ratchet.play(90, dur=dur * 0.7), t0, 0.5, mx(t0 + 0.3))
        notes = ['C5', 'Bb4', 'A4', 'G4', 'F4', 'Eb4', 'D4', 'C4', 'Bb3', 'A3', 'G3', 'F3']
        if up:
            notes = notes[::-1]
        for k, m in enumerate(notes):       # a glissando that runs with it
            t = t0 + dur * 0.8 * (k / len(notes)) ** (1.25 if up else 0.8)
            M.add('toys', xylo.play(n(m) + 12, 96), t, 0.7, mx(t))
        M.add('fx', whoosh(dur * 0.8, 400, 2500, 0.3, seed=int(t0)), t0, 0.5, mx(t0 + dur / 2))
    M.add('toys', crank.play(100, dur=ZIP2 - WIND), WIND, 0.9, mx(WIND))
    M.add('toys', slap.play(118), FLIP, 0.9, mx(FLIP))
    M.add('drums', crash_s.play(100), FLIP, 0.5, mx(FLIP))
    M.add('fx', slide(0.0, 0.12, 1500, 2600, 0.18, 0.25), FLIP + 0.12, 0.9, mx(FLIP))  # squeak

    # ---- reprise: the hook again with the whole band; the jack goes BOING, bigger every time ----
    band(22, 26)
    melody(TUNE, tpt, 22, 'tune', 112, gain=0.9, beats=(0, 16), p=0.1)
    melody(TUNE, horn, 22, 'tune', 100, shift=-12, gain=0.6, beats=(0, 16), p=-0.1)

    def boing(height):
        dur = 0.5 + height / 200
        tt = np.arange(int(dur * SR)) / SR
        f0 = 260 + 2.2 * height
        f = f0 * (1 + 0.6 * np.exp(-tt / 0.04)) * (1 + 0.08 * np.sin(2 * np.pi * 17 * tt) * np.exp(-tt / 0.3))
        ph = 2 * np.pi * np.cumsum(f) / SR
        sig = (np.sin(ph) + 0.3 * np.sin(2 * ph)) * np.exp(-tt / (dur / 3)) * np.clip(tt / 0.005, 0, 1)
        return np.vstack([sig, sig]) * 0.35
    jx = lambda t: pan_at(slot_x(G, S['jack'], t) + 17 + jack_height(t))
    for k, (tj, a) in enumerate(JACKS):
        M.add('toys', boing(a), tj, 0.7 + 0.25 * k, jx(tj + 0.2))
        M.add('fx', slide(0.0, 0.15, 500, 900 + 8 * a, 0.2, 0.3), tj, 0.8, jx(tj + 0.2))
        if k == len(JACKS) - 1:
            M.add('drums', crash.play(120), tj, 0.9, jx(tj + 0.2))
            M.add('drums', timp.play(124), tj, 0.9, jx(tj + 0.2))
    for t in np.arange(*RATTLE, BEAT / 4):  # the lid rattling
        M.add('toys', clave.play(80), t, 0.6, jx(t))
    r = sroll.play(90, dur=RATTLE[1] - RATTLE[0])
    M.add('drums', r * np.linspace(0.3, 1, r.shape[1]), RATTLE[0], 0.6)

    # ---- stop, three blows ----
    M.add('toys', ratchet.play(100, dur=0.6), STOP - 0.6, 0.6)
    for j, tb in enumerate(BLOWS):
        c = ('Eb', 'F', 'Bb')[j]
        M.add('hammer', anvil.play(127), tb, 1.3)
        M.add('drums', timp.play(124), tb, 1.0)
        M.add('drums', bd.play(124), tb, 1.0)
        for m in CH[c]:
            M.add('band', horn.play(n(m), 120, dur=0.3), tb, 0.8)
            M.add('tune', tpt.play(n(m) + 12, 116, dur=0.3), tb, 0.6)
        M.add('bass', tuba.play(n(ROOT[c][0]), 124), tb, 1.1)
    M.add('drums', crash.play(124), BLOWS[-1], 1.0)

    # ---- wrapped: harp glissandos out both ways with the ribbon, the end of the hook, the bow ----
    for p in (-0.6, 0.6):
        for k, m in enumerate(('Bb3', 'D4', 'F4', 'Bb4', 'D5', 'F5', 'Bb5', 'D6')):
            M.add('band', harp.play(n(m), 92), WRAP + k * 0.22, 0.6, p * (k + 1) / 8)
    for k in range(8):
        M.add('drums', sleigh.play(100), WRAP + k * BEAT, 0.6)
    band(27, 29)
    melody(TUNE, tpt, 27, 'tune', 118, beats=(24, 32), gain=1.0, p=0.1)
    melody(TUNE, clar, 27, 'tune', 104, beats=(24, 32), gain=0.6, p=-0.15)
    melody(TUNE, glock, 27, 'ring', 100, beats=(24, 32), gain=0.7)
    M.add('drums', bd.play(124), BOW_T, 1.2)
    M.add('drums', crash.play(124), BOW_T, 1.0)
    M.add('drums', timp.play(124), BOW_T, 0.9)
    M.add('fx', btree.play(115), BOW_T + 0.1, 3.0)
    for m in ('Bb2', 'F3', 'Bb3', 'D4'):
        M.add('band', horn_s.play(n(m), 118, dur=3.0), BOW_T, 0.6)
    for m in ('D4', 'F4', 'Bb4'):
        M.add('tune', tpt_s.play(n(m), 118, dur=2.5), BOW_T, 0.5)
    M.add('bass', tuba_s.play(n('Bb1'), 124, dur=3.0), BOW_T, 1.1)
    for k, m in enumerate(('Bb5', 'D6', 'F6', 'Bb5', 'F5', 'D6')):
        M.add('ring', glock.play(n(m), 96), BOW_T + 0.15 * k, 0.6, (k % 3 - 1) * 0.5)
