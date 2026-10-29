"""Experiments in the Tower: a comic laboratory number to a fast patter song. The lab sputters on (a
scanner sweeping the porch sides, meters on both wings, a clock ticking along Side) and a pale figure
(bright head, two dark eyes, dimmer body) stands at a bench over the porch, trying to work out
Christmas one experiment at a time, eight bars each, every move on the beat:

1. An ornament: he taps it, tink, tink, tink, lifts it, lets go, and it shatters into red and gold
   sparkles that fly both ways; he jumps back and shrugs.
2. A snowflake drifts in; he holds a candle under it; it glows, trembles and poofs away. He looks
   left, right, left for it, and slumps.
3. A teddy bear: he squeezes it, squeak, squeak, squeak, then SQUEAK: it bounces off down the porch
   and bounces back into his arms.
4. A candy cane: he measures it tick by tick, pulls it out long, lets go, and it boings back and
   smacks him into a spin.
5. A jack-in-the-box: he winds it, eight cranks, leans in close... nothing... POP: the clown on its
   spring bonks him clear across the porch, and he sits seeing stars.

Then the idea: a gold bulb lights over his head, DING, he springs up and zooms back, and the song goes
from G minor to G major. Red and green bands march out from the bench while every experiment comes
back right, one by one along the front of the house (the ornament and the snowflake on the left wing,
the bear on the porch, the cane and the box on the right wing),
and on the last bar he leaps in a gold flash.

Characters and props are spans in path distance with exact span-over-pixel coverage, like Bone Yard;
every time is on the song's 2/4 grid (bar(k, beat)) that score() shares."""
import numpy as np
from pixelhome.fx import DT, hexc, light, smoothstep, keys, lerp, nframes

CODE = 'NB04'
TITLE = 'Experiments in the Tower'
KIND = 'show'
DESCRIPTION = ('A mad little lab number: an ornament shatters, a snowflake melts, a teddy squeaks off, a candy '
               'cane boings and a jack-in-the-box bonks him, until the light bulb goes on and it all comes right.')

LAB = hexc('#106a80')
FIGURE = hexc('#eef2ff')
RED = hexc('#ff1a10')
GOLD = hexc('#ffb020')
WHITE = hexc('#f0f4ff')
FLAME = hexc('#ff6a10')
BROWN = hexc('#d06818')
BLUE = hexc('#2a50ff')
SPRING = hexc('#40ff60')
CLOWN = hexc('#ffe040')
METER = hexc('#30ff60')
SCAN = hexc('#a0d8ff')
GREEN = hexc('#10d040')
PAL = [FIGURE, RED, GOLD, WHITE, FLAME, BROWN, BLUE, SPRING, CLOWN]
FIG, RD, GD, WH, FL, BR, BL, SG, CL = range(9)

BPM = 144
BEAT = 60 / BPM                             # 2/4: two beats a bar
BAR = 2 * BEAT
ON = 2                                      # bars 0-1 the lab sputters on; he appears at bar ON
ORN, FLAKE, TEDDY, CANE, JACK = 4, 12, 20, 28, 36       # each experiment's first bar; eight bars each
FAIL = {ORN: 9, FLAKE: 8, TEDDY: 8, CANE: 9, JACK: 12}  # the beat (from its first bar) where it goes wrong
EUREKA = 44                                 # the idea
PAYOFF = 46                                 # G major: the bands march, the experiments come back right
BACK_AT = (46, 48, 50, 52, 54)              # bars where each experiment comes back, along the house
FINAL = 61                                  # the leap and the gold flash
D = (FINAL + 1) * BAR + 2.0

HEAD, NECK, BODY = 20.0, 4.0, 32.0
BOOT = 470.0                                # how far the jack-in-the-box knocks him


def bar(k, beat=0.0):
    return k * BAR + beat * BEAT


def stage(G):
    d = G.pd[G.path]
    mid = float(G.pd[G.seg['Porch Front']].mean())
    runs = {n: (float(d[idx].min()), float(d[idx].max())) for n, idx in G.path_segments()}
    hx = mid - 50                           # where he stands, facing the bench
    ix = mid + 25                           # where each experiment sits
    lerp_run = lambda n, u: runs[n][0] + u * (runs[n][1] - runs[n][0])
    back = [lerp_run('Left', 0.3), lerp_run('Left', 0.7), mid + 105,       # where each comes back: front runs
            lerp_run('Right', 0.3), lerp_run('Right', 0.7)]
    rng = np.random.default_rng(53)
    shards = np.column_stack([rng.uniform(-1, 1, 18), rng.uniform(0, 2 * np.pi, 18), rng.integers(0, 2, 18)])
    return dict(d=d, mid=mid, runs=runs, hx=hx, ix=ix, back=back, shards=shards, L=G.length)


def beats(t, k):
    """Beats since bar k."""
    return (t - bar(k)) / BEAT


def blob(x, c, w):
    return np.exp(-((x - c) / w) ** 2)


def span(sp, a, z, I, c):
    sp.append((min(a, z), max(a, z), I, c))


def figure(sp, x, dr, g, I):
    body = BODY * (1 + 0.25 * (g - 1))
    tot = HEAD + NECK * g + body
    base = x - dr * tot / 2
    span(sp, base, base + dr * body, 0.5 * I, FIG)
    h0 = base + dr * (body + NECK * g)
    span(sp, h0, h0 + dr * HEAD, 1.0 * I, FIG)
    for e0, e1 in ((4.5, 8.5), (11.5, 15.5)):
        span(sp, h0 + dr * e0, h0 + dr * e1, -0.95 * I, FIG)
    return h0 + dr * HEAD                   # the top of his head


def nod(b, k=0.12):
    return np.exp(-(b % 1) * BEAT / k)


def scientist(t, S):
    """His centre, head direction, stretch and brightness."""
    hx = S['hx']
    if t < bar(ON):
        return None
    I = smoothstep(bar(ON), bar(ON) + 0.4, t)
    for E in (ORN, FLAKE, TEDDY, CANE):
        if bar(E) <= t < bar(E + 8):
            b = beats(t, E)
            x, dr, g = hx, 1.0, 1 + 0.15 * nod(b)
            if E == ORN:
                if b < 5 and b >= 2:
                    x += 8 * nod(b, 0.1)
                if 9 <= b < 12:
                    x -= 30 * smoothstep(9, 9.3, b) * (1 - smoothstep(10.5, 12, b))
                    g = 1 + 0.9 * np.exp(-(b - 9) * BEAT / 0.2)
                if 12 <= b < 14 and (b % 1) > 0.5:
                    dr = -1.0               # a shrug: a look each way
            elif E == FLAKE:
                if 2.5 <= b < 3.2:
                    dr = -1.0
                if 9 <= b < 12:
                    j = int(b - 9)
                    x += (-22, 22, -22)[j] * smoothstep(0, 0.4, b % 1)
                    dr = -1.0 if j % 2 == 0 else 1.0
                if b >= 12:
                    g = 0.72 + 0.08 * np.sin(np.pi * (b - 12) / 4)
            elif E == TEDDY:
                if b < 8 and b >= 2 and int(b) % 2 == 0:
                    x += 10 * nod(b, 0.1)
                if 8 <= b < 10:
                    g = 1 + 1.3 * np.exp(-(b - 8) * BEAT / 0.25)
                if b >= 14:
                    x += 10 * smoothstep(14, 14.5, b)
            else:
                if 6 <= b < 8:
                    x -= 16 * smoothstep(6, 8, b)
                if 9 <= b < 12:
                    dr = 1.0 if int((b - 9) * 4) % 2 == 0 else -1.0
                    x -= 16 + 8 * np.sin(2 * np.pi * (b - 9))
                    g = 1 + 0.4 * abs(np.sin(np.pi * 2 * (b - 9)))
                elif b >= 12:
                    x -= 16 * (1 - smoothstep(12, 13, b))
                    g = 1 + 0.15 * np.sin(2 * np.pi * (b - 12))
            return x, dr, g, I
    if bar(JACK) <= t < bar(EUREKA):
        b = beats(t, JACK)
        if b < 10:
            return hx, 1.0, 1 + 0.15 * nod(b), I
        if b < 12:
            return hx + 12 * smoothstep(10, 11, b), 1.0, 1.0, I
        u = b - 12
        x = hx + 12 - BOOT * (1 - np.exp(-u / 0.6))
        dr = 1.0 if (u > 2 or int(u * 6) % 2 == 0) else -1.0
        return x, dr, 0.8 if u > 2 else 1 + 0.5 * abs(np.sin(np.pi * 3 * u)), I
    if bar(EUREKA) <= t < bar(PAYOFF):
        b = beats(t, EUREKA)
        far = hx + 12 - BOOT * (1 - np.exp(-((EUREKA - JACK) * 2 - 12) / 0.6))
        if b < 2:
            return far, 1.0, 0.8 + 1.4 * smoothstep(1, 1.2, b) * np.exp(-max(b - 1.2, 0) * 2), I
        return lerp(far, hx, smoothstep(2, 3.6, b)), 1.0, 1 + 1.2 * np.sin(np.pi * np.clip(b - 2, 0, 1)), I
    b = beats(t, PAYOFF)
    if t < bar(FINAL):
        side = 1 if int(b) % 2 else -1
        return hx + 18 * side * smoothstep(0, 0.35, b % 1) - 18 * side * (1 - smoothstep(0, 0.35, b % 1)), \
            1.0, 1 + 0.6 * nod(b, 0.15), I
    return hx, 1.0, 1 + 2.4 * np.sin(np.pi * np.clip(beats(t, FINAL) / 1.6, 0, 1)), I


def props(sp, t, S):
    """The experiments on the bench, their gags, and the stars round his head."""
    ix = S['ix']
    if bar(ORN) <= t < bar(ORN + 8):
        b = beats(t, ORN)
        lift = 40 * smoothstep(6, 8, b) - 40 * smoothstep(8, 9, b) if b < 9 else 0
        if b < 9:
            x = ix + lift
            I = 0.7 + (0.4 * nod(b, 0.08) if b >= 2 and b < 5 else 0)
            span(sp, x - 7, x + 7, I, RD)
            span(sp, x - 11, x - 7, 0.8, GD)
            span(sp, x - 3, x - 1, 0.5 * I, WH)
            if 2 <= b < 5:
                span(sp, x - 2, x + 2, 0.8 * nod(b, 0.08), GD)
        else:
            u = b - 9
            for a, ph, c in S['shards']:
                xq = ix + a * 170 * (1 - np.exp(-u / 0.6))
                tw = 0.5 + 0.5 * np.sin(18 * u + ph)
                span(sp, xq - 1.8, xq + 1.8, max(0, 1 - u / 6) * tw, RD if c else GD)
    if bar(FLAKE) <= t < bar(FLAKE + 8):
        b = beats(t, FLAKE)
        if b < 8:
            x = ix + 60 * (1 - smoothstep(0, 2, b)) + (1.5 * np.sin(40 * t) if b > 6 else 0)
            tw = 0.75 + 0.25 * np.sin(9 * t)
            warm = smoothstep(4, 8, b)
            span(sp, x - 3, x + 3, tw * (0.8 + 0.3 * warm), WH)
            span(sp, x - 1, x + 1, 0.5 * warm, GD)
        if 4 <= b < 9.5:
            fl = smoothstep(4, 4.3, b) * (1 - smoothstep(8.6, 9.5, b)) * (0.7 + 0.3 * np.sin(23 * t) * np.sin(31 * t))
            span(sp, ix - 16, ix - 8, fl * (0.6 + 0.4 * smoothstep(4, 8, b)), FL)
        if 8 <= b < 9.5:
            u = (b - 8) / 1.5
            span(sp, ix - 10 - 50 * u, ix + 10 + 50 * u, 0.8 * (1 - u) ** 2, WH)
    if bar(TEDDY) <= t < bar(TEDDY + 8):
        b = beats(t, TEDDY)
        x, s, I = ix, 1.0, 0.65
        if b < 8 and b >= 2 and int(b) % 2 == 0:
            s = 1 - 0.3 * nod(b, 0.1)
        if 8 <= b < 14:
            u = b - 8                       # bounces away three beats, back three
            out = 1 - abs(1 - u / 3)
            x = ix + 260 * out
            s = 1 - 0.25 * np.exp(-(u % 1) * BEAT / 0.08)
            I = 0.65 + 0.3 * np.exp(-(u % 1) * BEAT / 0.08)
        if b >= 8 and b < 8.3:
            s = 0.55
        span(sp, x - 11 * s, x + 11 * s, 0.6 * I / 0.65, BR)
        h0 = x + 11 * s + 2
        span(sp, h0, h0 + 13, 0.75 * I / 0.65, BR)
        for e0, e1 in ((3, 5), (8, 10)):
            span(sp, h0 + e0, h0 + e1, -0.7, BR)
    if bar(CANE) <= t < bar(CANE + 8):
        b = beats(t, CANE)
        ln = 56.0
        if 6 <= b < 8:
            ln *= 1 + 0.6 * smoothstep(6, 8, b)
        elif 8 <= b < 10:
            ln *= 1 + 0.6 * np.exp(-(b - 8) * 1.4) * np.cos(2 * np.pi * 2.2 * (b - 8))
        fade = 1 - smoothstep(14, 16, b)
        a0 = ix - 4 - (16 * smoothstep(6, 8, b) if b < 8 else 16 * np.exp(-(b - 8) * 3))
        nst = 10
        for q in range(nst):
            lo, hi = a0 + ln * q / nst, a0 + ln * (q + 1) / nst
            span(sp, lo, hi, 0.65 * fade, RD if q % 2 == 0 else WH)
        if 2 <= b < 6:
            n = int((b - 2) * 2) + 1
            for q in range(min(n, 8)):
                tk = ix - 4 + 56 * q / 7
                span(sp, tk - 1, tk + 1, 0.9 * (0.5 + 0.5 * (q == n - 1)), GD)
    if bar(JACK) <= t < bar(EUREKA):
        b = beats(t, JACK)
        jig = (0.5 * min(b, 10) / 10) * np.sin(2 * np.pi * 6 * t) if b < 12 else 0
        x = ix + 4 + jig
        span(sp, x - 11, x + 11, 0.5, BL)
        span(sp, x - 11, x - 9, 0.65, RD)
        span(sp, x + 9, x + 11, 0.65, RD)
        if 2 <= b < 10:
            span(sp, x + 13, x + 16, 0.4 + 0.6 * nod(b, 0.1), GD)
        else:
            span(sp, x + 13, x + 16, 0.4, GD)
        if b >= 12:
            u = b - 12
            reach = 70 * smoothstep(0, 0.12, u) + 14 * np.sin(2 * np.pi * 1.6 * u) * np.exp(-u * 0.9)
            for q in range(6):
                zq = x - 12 - reach * (q + 0.5) / 6
                span(sp, zq - 1.6, zq + 1.6, 0.6 + 0.3 * (q % 2), SG)
            span(sp, x - 12 - reach - 12, x - 12 - reach, 0.95, CL)
            span(sp, x - 12 - reach - 9, x - 12 - reach - 7, -0.8, CL)


def render(G, seed=53):
    S = stage(G)
    d, mid, runs, L = S['d'], S['mid'], S['runs'], S['L']
    r = np.abs(d - mid)
    w = np.gradient(d)
    e0, e1 = d - w / 2, d + w / 2
    inrun = {n: (d >= a - 1) & (d <= b + 1) for n, (a, b) in runs.items()}
    l0, l1 = runs['Left']
    r0, r1 = runs['Right']
    side1 = runs['Side'][1]
    p0, p1 = runs['Porch Left']
    q0, q1 = runs['Porch Right']

    def meter(t, lag=0.0):
        t = t - lag * BEAT
        for E, fb in FAIL.items():
            if bar(E) <= t < bar(E + 8):
                b = beats(t, E)
                if b < fb:
                    return 0.12 + 0.68 * b / fb
                return 0.8 * np.exp(-(b - fb) * BEAT / 0.12) + 0.04
        return 0.0

    F = nframes(D)
    out = np.zeros((F, G.N, 3))
    for f in range(F):
        t = f * DT
        fr = np.zeros((G.N, 3))
        sp = []
        end = keys(t, [(D - 1.2, 1), (D, 0)])
        k = int(t / BAR)
        # the lab sputters on, flickering on the eighths
        on = 1.0
        if t < bar(ON):
            e = int(t / (BEAT / 2))
            on = (0.0, 1.0, 0.0, 1.0, 1.0, 0.0, 1.0, 1.0)[min(e, 7)]
        lab = 0.14 * on * (t < bar(PAYOFF) + 0.5)
        fr += light(LAB, lab * np.ones(G.N))
        if t < bar(PAYOFF):
            # the scanner on both porch sides, mirrored
            ph = 0.5 - 0.5 * np.cos(2 * np.pi * t / (4 * BAR))
            fr += light(SCAN, 0.3 * on * (inrun['Porch Left'] * blob(d, lerp(p0, p1, ph), 18) +
                                         inrun['Porch Right'] * blob(d, lerp(q1, q0, ph), 18)))
            # meters on the wings, filling from the outer ends
            lf = l0 + (l1 - l0) * meter(t)
            rf = r1 - (r1 - r0) * meter(t, 0.5)
            fr += light(METER, 0.17 * on * (inrun['Left'] * smoothstep(lf + 6, lf - 6, d) +
                                            inrun['Right'] * smoothstep(rf - 6, rf + 6, d)))
            # the lab clock along Side
            b = t / BEAT
            pos = (int(b) * 30.0) % side1
            fr += light(SCAN, inrun['Side'] * 0.3 * on * (0.5 + nod(b, 0.08)) * blob(d, pos, 8))
        props(sp, t, S)
        s = scientist(t, S)
        if s is not None:
            x, dr, g, I = s
            top = figure(sp, x, dr, g, I * end * (0.8 + 0.2 * min(g, 2) / 2))
            if bar(JACK) + 14 * BEAT <= t < bar(EUREKA):           # seeing stars
                for q in range(3):
                    a = 2 * np.pi * (q / 3 + 1.3 * t)
                    xs = top + 9 * np.sin(a)
                    span(sp, xs - 1.5, xs + 1.5, 0.7 * (0.5 + 0.5 * np.cos(a)), GD)
            if bar(EUREKA) <= t < bar(EUREKA) + 3 * BEAT:          # the idea
                u = beats(t, EUREKA)
                span(sp, top + dr * 6, top + dr * 14, 1.0 * (0.7 + 0.3 * np.exp(-u * 2)), GD)

        # the payoff: bands march out from the bench, the experiments come back right along the house
        if t >= bar(PAYOFF):
            u = t - bar(PAYOFF)
            fade = end
            front = 380 * u
            band = ((r - 380 * u) // 80).astype(int) % 2
            behind = smoothstep(front + 30, front - 30, r) * fade
            fr += light(RED, 0.4 * behind * (band == 0)) + light(GREEN, 0.4 * behind * (band == 1))
            fr += light(GOLD, 0.9 * np.exp(-u / 0.8) * blob(r, 0, 200 + 900 * u))
            for j, (kb, x) in enumerate(zip(BACK_AT, S['back'])):
                if t < bar(kb):
                    continue
                v = t - bar(kb)
                pop = 0.5 * np.exp(-v / 0.3)
                span(sp, x - 26, x + 26, 0.45 * pop / 0.5, GD)
                if j == 0:
                    span(sp, x - 7, x + 7, 0.75 + pop, RD)
                    span(sp, x - 11, x - 7, 0.8, GD)
                elif j == 1:
                    span(sp, x - 3, x + 3, 0.8 + 0.2 * np.sin(9 * t) + pop, WH)
                elif j == 2:
                    span(sp, x - 11, x + 11, 0.6 + pop, BR)
                    span(sp, x + 13, x + 26, 0.75 + pop, BR)
                    for a, z in ((x + 16, x + 18), (x + 21, x + 23)):
                        span(sp, a, z, -0.7, BR)
                elif j == 3:
                    for q in range(10):
                        span(sp, x - 28 + 5.6 * q, x - 28 + 5.6 * (q + 1), 0.65 + pop, RD if q % 2 == 0 else WH)
                else:
                    span(sp, x - 11, x + 11, 0.55 + pop, BL)
                    span(sp, x - 24, x - 12, 0.9 * (0.8 + 0.2 * np.sin(2 * np.pi * t / BEAT)), CL)
            if t >= bar(FINAL):
                v = t - bar(FINAL)
                fr += light(GOLD, (0.95 * np.exp(-v / 0.6) + 0.25) * fade * np.ones(G.N))
            elif int(beats(t, PAYOFF)) >= (FINAL - PAYOFF - 4) * 2:   # the last bars pulse on every beat
                fr += light(GOLD, 0.25 * nod(beats(t, PAYOFF), 0.15) * fade * np.ones(G.N))

        if sp:
            a = np.array(sp)
            ov = np.clip(np.minimum(a[:, 1:2], e1) - np.maximum(a[:, 0:1], e0), 0, None) / w
            for c in np.unique(a[:, 3]).astype(int):
                m = a[:, 3] == c
                fr += light(PAL[c], np.clip(a[m, 2] @ ov[m], 0, 1))
        out[f][G.path] = np.clip(fr, 0, 1) * end ** 2.2
    return out


# ---- music: a patter song in 2/4 at BPM, G minor until the idea, then G major. TUNE is the verse (eight bars of
# eighth-note patter), sung by a different instrument each experiment (bassoon, clarinet, oboe over bassoon,
# xylophone, clarinet and bassoon together); CHORUS is the big G major tune after the DING. Pizz oom-pah and a
# woodblock tick-tock on the offbeats (the lab clock on Side) under all of it. Every gag has its own sound at
# its beat, panned to the bench (or wherever it ends up): tinks and a shatter, a candle crackle and a poof, toy
# squeaks and bounces, ruler ticks and a spring, cranks, a held breath, a POP and a bonk, a twittering of
# stars, a ding. In the payoff each experiment comes back with its own sound where it reappears. ----

TUNE = [                                    # (beat, note, beats): the verse, eight bars of two
    (0, 'G4', .5), (.5, 'G4', .5), (1, 'Bb4', .5), (1.5, 'A4', .5), (2, 'G4', .5), (2.5, 'F#4', .5), (3, 'G4', 1),
    (4, 'C5', .5), (4.5, 'C5', .5), (5, 'Bb4', .5), (5.5, 'A4', .5), (6, 'Bb4', .5), (6.5, 'A4', .5), (7, 'G4', 1),
    (8, 'D5', .5), (8.5, 'D5', .5), (9, 'C5', .5), (9.5, 'Bb4', .5), (10, 'A4', .5), (10.5, 'Bb4', .5),
    (11, 'C5', .5), (11.5, 'A4', .5), (12, 'Bb4', .5), (12.5, 'G4', .5), (13, 'F#4', .5), (13.5, 'A4', .5),
    (14, 'G4', 1), (15, 'D4', .5), (15.5, 'D4', .5)]
MAJOR = {'Bb4': 'B4', 'Bb3': 'B3'}          # the verse in G major
CHORUS = [
    (0, 'D5', 1), (1, 'B4', .5), (1.5, 'G4', .5), (2, 'C5', 1), (3, 'A4', 1),
    (4, 'B4', .5), (4.5, 'C5', .5), (5, 'D5', .5), (5.5, 'E5', .5), (6, 'D5', 2),
    (8, 'E5', 1), (9, 'C5', .5), (9.5, 'A4', .5), (10, 'D5', 1), (11, 'B4', 1),
    (12, 'C5', .5), (12.5, 'B4', .5), (13, 'A4', .5), (13.5, 'F#4', .5), (14, 'G4', 2)]
MINOR_CH = ['Gm', 'D', 'Cm', 'Gm', 'Bb', 'F', 'D', 'Gm']
MAJOR_CH = ['G', 'D', 'C', 'G', 'G', 'D', 'D', 'G']
CHORUS_CH = ['G', 'C', 'G', 'D', 'C', 'G', 'D', 'G']
VOICE = {'Gm': ('G3', 'Bb3', 'D4'), 'D': ('F#3', 'A3', 'D4'), 'Cm': ('G3', 'C4', 'Eb4'), 'Bb': ('F3', 'Bb3', 'D4'),
         'F': ('F3', 'A3', 'C4'), 'G': ('G3', 'B3', 'D4'), 'C': ('G3', 'C4', 'E4')}
ROOT = {'Gm': 'G2', 'D': 'D2', 'Cm': 'C2', 'Bb': 'Bb1', 'F': 'F2', 'G': 'G2', 'C': 'C2'}


def score(M, G):
    from pixelhome.audio import SR, note as n, slide, whoosh
    S = stage(G)
    d, ix = S['d'], S['ix']
    xs = G.pos[G.path, 0]
    x0, x1 = xs.min(), xs.max()

    def pan_at(q):
        return float(0.85 * (2 * (np.interp(q, d, xs) - x0) / (x1 - x0) - 1))

    pb = pan_at(ix)
    pizz = M.sampler('Strings/Solo Contrabass/Pizz/*.wav', tune=-12)
    cpizz = M.sampler('Strings/Cello Section/pizzT/*.wav', tune=-12)
    bsn = M.sampler('Woodwinds/Bassoon/stac/*.wav', tune=-12)
    clar = M.sampler('Woodwinds/Clarinet/stac/*.wav', tune=-12)
    oboe = M.sampler('Woodwinds/Oboe/Stacc/*.wav', tune=-12)
    xylo = M.sampler('Percussion/Xylo/*.wav', tune=-12)
    glock = M.sampler('Percussion/Glock/*.wav', tune=-12)
    tpt = M.sampler('Brass/Trumpet/stac/*.wav', tune=-12)
    tpt_s = M.sampler('Brass/Trumpet/sus/*.wav', tune=-12)
    horn = M.sampler('Brass/F Horn/sus/*.wav', tune=-12)
    vln = M.sampler('Strings/Violin Section/susVib/*.wav', tune=-12)
    fall = M.sampler('Brass/OldTrombone/Fall/*.wav', tune=-12)
    box = M.synth('Plucks/Magic Music Box')
    wood = M.hits('VSCO 1 Percussion/varWood/wood_click*.wav')
    clave = M.hits('Percussion/Claves1_Hit*.wav')
    slap = M.hits('VSCO 1 Percussion/varWood/slapstick[0-9].wav')
    log = M.hits('VSCO 1 Percussion/varWood/log_drum/*.wav')
    ratchet = M.hits('Percussion/Ratchet1-Crank*.wav')
    guiro = M.hits('Percussion/Guiro-Slow*.wav')
    zap = M.hits('Percussion/zap*.wav')
    tree = M.hits('Percussion/BellTree_Stroke*.wav')
    tri = M.hits('Percussion/Triangle3-Hit_v1*.wav')
    crash = M.hits('VSCO 1 Percussion/varMetal/Cymbals/clash/crash_hit_ff*.wav')
    choke = M.hits('Percussion/cymbal-crashshort*.wav')
    snare = M.hits('VSCO 1 Percussion/drums/snare/drum3_marching/snare3_[fmp]*.wav')
    bd = M.hits('VSCO 1 Percussion/drums/bass/bdrum_f_*.wav')
    timp = M.hits('Percussion/Timpani/Timpani1_Hit*.wav')
    for name, gain, rev in (('bass', 0.22, 0.06), ('pah', 0.12, 0.1), ('tune', 0.17, 0.15), ('tick', 0.12, 0.08),
                            ('fx', 0.13, 0.18), ('gag', 0.17, 0.15), ('band', 0.12, 0.2), ('drums', 0.13, 0.12)):
        M.bus(name, gain=gain, reverb=rev)
    boxn = []

    def mono(sig, p):
        a = (np.clip(p, -1, 1) + 1) * np.pi / 4
        return np.vstack([sig * np.cos(a), sig * np.sin(a)]) * np.sqrt(2)

    def tone(f, amp, harm=(1.0, 0.3, 0.12)):  # a pitched blip along a frequency curve
        ph = 2 * np.pi * np.cumsum(f) / SR
        return amp * sum(h * np.sin((i + 1) * ph) for i, h in enumerate(harm))

    def squeak(t, p, big=1.0):              # a squeaky toy: up, then down
        sec = 0.16 * big + 0.06
        u = np.arange(int(sec * SR)) / SR
        f = (1000 / big) * (1 + 0.6 * np.sin(np.pi * u / sec))
        env = np.sin(np.pi * u / sec) ** 0.6
        M.add('gag', mono(tone(f, 0.3, (1.0, 0.5, 0.3, 0.15)) * env, p), t)

    def boing(t, p, f0=180.0, sec=1.2):     # a spring
        u = np.arange(int(sec * SR)) / SR
        f = f0 * (1 + 0.8 * np.minimum(u / 0.05, 1)) * (1 + 0.25 * np.sin(2 * np.pi * 7 * u) * np.exp(-u * 2.5))
        M.add('gag', mono(tone(f, 0.35) * np.exp(-u * 2.2) * np.clip(u / 0.005, 0, 1), p), t)

    def noise(t, sec, p, amp, tau, smooth=1):
        u = np.arange(int(sec * SR)) / SR
        x = M.rng.normal(0, 1, len(u))
        if smooth > 1:
            x = np.convolve(x, np.ones(smooth) / smooth, 'same')
        M.add('fx', mono(amp * x * np.exp(-u / tau) * np.clip(u / 0.003, 0, 1), p), t)

    def verse(tune, k0, inst, bus, vel, gain=1.0, shift=0, p=0.0, skip=()):
        for b, m, ln in tune:
            if any(a <= b < z for a, z in skip):
                continue
            M.add(bus, inst.play(n(m) + shift, vel, dur=ln * BEAT * 0.75), bar(k0, b), gain, p)

    # ---- the band: oom-pah and tick-tock, minor until the idea, major after ----
    for k in range(FINAL + 1):
        if k < ORN - 2:
            c = 'Gm'
        elif k < EUREKA:
            c = MINOR_CH[(k - ORN) % 8] if k >= ORN else 'D'
        elif k < PAYOFF:
            c = 'D'
        else:
            c = (CHORUS_CH if k < PAYOFF + 8 else MAJOR_CH)[(k - PAYOFF) % 8]
        quiet = bar(JACK, 10) <= bar(k) < bar(JACK, 12)                    # the held breath
        if k >= ON and not quiet:
            M.add('bass', pizz.play(n(ROOT[c]), 104), bar(k), 1.0, -0.1)
            for m in VOICE[c]:
                M.add('pah', cpizz.play(n(m), 84), bar(k, 1), 0.6, 0.2)
        for e in range(4):
            if not quiet or e % 2:
                M.add('tick', wood.play(92 if e % 2 else 60), bar(k, e / 2), 0.7, -0.75)
    for e in range(8):                                                      # the lights sputtering on
        if (0, 1, 0, 1, 1, 0, 1, 1)[e] and (e == 0 or not (0, 1, 0, 1, 1, 0, 1, 1)[e - 1]):
            M.add('fx', zap.play(70), e * BEAT / 2, 0.4, float(M.rng.uniform(-0.6, 0.6)))
    M.add('tune', bsn.play(n('D3'), 90, dur=0.2), bar(ORN - 1), 0.8, pb)
    M.add('tune', bsn.play(n('D3'), 90, dur=0.2), bar(ORN - 1, 1), 0.8, pb)

    # ---- 1: the ornament ----
    verse(TUNE, ORN, bsn, 'tune', 104)
    for b in (2, 3, 4):
        M.add('gag', glock.play(n('G6'), 100), bar(ORN, b), 0.7, pb)
    M.add('fx', slide(0.0, 2 * BEAT, 600, 1000, 2 * BEAT, 0.25), bar(ORN, 6), 0.6, pb)
    M.add('fx', slide(0.0, BEAT, 1000, 500, BEAT, 0.25), bar(ORN, 8), 0.6, pb)
    ts = bar(ORN, FAIL[ORN])
    M.add('drums', choke.play(115), ts, 0.9, pb)
    M.add('gag', tree.play(110), ts, 0.8, pb)
    for j, (a, ph, c) in enumerate(S['shards']):
        M.add('gag', glock.play(n('C7') - int(M.rng.integers(0, 14)), 90 - 3 * j), ts + 0.03 * j, 0.5,
              pan_at(ix + a * 170))
    for b in (12.5, 13.5):                                                  # a shrug
        M.add('tune', bsn.play(n('A2'), 90, dur=0.15), bar(ORN, b), 0.7, pb)

    # ---- 2: the snowflake ----
    verse(TUNE, FLAKE, clar, 'tune', 100)
    for j, m in enumerate(('D6', 'A5', 'F#5', 'D5', 'A5', 'D6')):
        boxn.append((bar(FLAKE) + 0.12 * j, n(m), 70, 0.4))
    noise(bar(FLAKE, 4), 0.25, pb, 0.25, 0.08, 4)                           # the match
    for j in range(40):                                                     # the candle crackles
        tq = bar(FLAKE, 4.2) + j * 4 * BEAT / 40 + float(M.rng.uniform(0, 0.03))
        noise(tq, 0.02, pb, 0.25 * float(M.rng.uniform(0.3, 1)), 0.004)
    M.add('fx', whoosh(0.5, 2500, 500, 0.5, seed=5), bar(FLAKE, 8), 0.7, pb)
    noise(bar(FLAKE, 8), 0.5, pb, 0.35, 0.15, 30)
    for j, b in enumerate((9, 10, 11)):                                     # hm? hm? hm?
        M.add('gag', bsn.play(n(('D3', 'G3', 'D3')[j]), 96, dur=0.25), bar(FLAKE, b), 0.9, pan_at(S['hx']))
    M.add('gag', fall.play(n('G3'), 100), bar(FLAKE, 12), 0.6, pan_at(S['hx']))

    # ---- 3: the teddy ----
    verse(TUNE, TEDDY, oboe, 'tune', 100)
    verse(TUNE, TEDDY, bsn, 'tune', 92, gain=0.6, shift=-12)
    for b in (2, 4, 6):
        squeak(bar(TEDDY, b), pb)
    squeak(bar(TEDDY, 8), pb, big=2.0)
    for j in range(6):                                                      # bouncing away and back
        u = j + 1
        x = ix + 260 * (1 - abs(1 - u / 3))
        M.add('gag', log.play(100), bar(TEDDY, 8 + u), 0.8, pan_at(x))
        M.add('fx', slide(0.0, BEAT * 0.8, 500 + 80 * (3 - abs(3 - u)), 900, BEAT * 0.8, 0.2), bar(TEDDY, 8 + u - 1),
              0.5, pan_at(x))
    for j, m in enumerate(('G5', 'B5', 'D6')):                             # the hug
        M.add('gag', glock.play(n(m), 80), bar(TEDDY, 14) + 0.07 * j, 0.6, pb)

    # ---- 4: the candy cane ----
    verse(TUNE, CANE, xylo, 'tune', 108)
    for q in range(8):
        M.add('gag', clave.play(85, pitch=q), bar(CANE, 2 + q / 2), 0.6, pan_at(ix - 4 + 8 * q))
    M.add('gag', guiro.play(90, dur=2 * BEAT), bar(CANE, 6), 0.7, pb)
    M.add('fx', slide(0.0, 2 * BEAT, 400, 900, 2 * BEAT, 0.25), bar(CANE, 6), 0.6, pb)
    boing(bar(CANE, 8), pb)
    M.add('drums', slap.play(124), bar(CANE, FAIL[CANE]), 1.0, pan_at(S['hx']))
    M.add('fx', slide(0.0, 3 * BEAT, 1400, 500, 3 * BEAT, 0.3), bar(CANE, 9), 0.7, pan_at(S['hx']))

    # ---- 5: the jack-in-the-box ----
    verse(TUNE, JACK, clar, 'tune', 104, skip=((10, 12),))
    verse(TUNE, JACK, bsn, 'tune', 98, shift=-12, gain=0.7, skip=((10, 12),))
    for b in range(2, 10):                                                  # eight cranks, climbing
        M.add('gag', ratchet.play(80, dur=0.25), bar(JACK, b), 0.6, pan_at(ix + 15))
        M.add('gag', xylo.play(n('G4') + (b - 2), 90), bar(JACK, b), 0.6, pan_at(ix + 15))
    tp = bar(JACK, FAIL[JACK])
    M.add('drums', slap.play(127), tp, 1.0, pb)
    M.add('drums', crash.play(120), tp, 0.8, pb)
    boing(tp, pb, f0=240.0, sec=1.6)
    M.add('drums', bd.play(120), tp + 0.12, 1.0, pan_at(S['hx']))
    M.add('gag', log.play(127, pitch=-5), tp + 0.12, 1.0, pan_at(S['hx']))
    land = S['hx'] - BOOT
    M.add('fx', whoosh(1.0, 2500, 400, 0.5, seed=8), tp + 0.1, 0.8, (pan_at(S['hx']) + pan_at(land)) / 2)
    for j in range(16):                                                     # tweet tweet: stars
        M.add('gag', glock.play(n('E6') if j % 2 else n('G6'), 70), bar(JACK, 14) + j * BEAT / 2, 0.4, pan_at(land))

    # ---- the idea, and the payoff in G major ----
    te = bar(EUREKA)
    M.add('gag', tri.play(120), te, 1.0, pan_at(land))
    M.add('gag', glock.play(n('G6'), 120), te, 0.9, pan_at(land))
    M.add('gag', tree.play(110), te + 0.1, 0.8, pan_at(land))
    M.add('fx', slide(0.0, 0.25, 500, 1500, 0.3, 0.3), bar(EUREKA, 1), 0.7, pan_at(land))
    M.add('fx', whoosh(2 * BEAT, 500, 2500, 0.4, seed=12), bar(EUREKA, 2), 0.6, 0.0)
    r = M.hits('Percussion/Snare2-rollSN_v[35]*.wav').play(90, dur=2 * BEAT)
    M.add('drums', r * np.linspace(0.2, 1, r.shape[1]) ** 2, bar(EUREKA, 2), 0.6)
    tp = bar(PAYOFF)
    M.add('drums', crash.play(118), tp, 1.0)
    M.add('drums', timp.play(118), tp, 0.8)
    verse(CHORUS, PAYOFF, tpt, 'band', 112, gain=1.0)
    for b, m, ln in CHORUS:
        if ln >= 2:
            M.add('band', tpt_s.play(n(m), 108, dur=ln * BEAT), bar(PAYOFF, b), 0.7)
    verse(CHORUS, PAYOFF, glock, 'gag', 80, gain=0.4)
    verse(CHORUS, PAYOFF, vln, 'band', 92, gain=0.6, shift=-12)
    major = [(b, MAJOR.get(m, m), ln) for b, m, ln in TUNE]
    verse(major, PAYOFF + 8, clar, 'tune', 108)
    verse(major, PAYOFF + 8, xylo, 'gag', 96, gain=0.5)
    verse(major, PAYOFF + 8, tpt, 'band', 100, gain=0.6, shift=-12)
    for k in range(PAYOFF, FINAL):
        for e in range(4):
            M.add('drums', snare.play(100 if e == 0 else 70), bar(k, e / 2), 0.5, 0.15)
        M.add('drums', bd.play(96), bar(k), 0.6)
    sounds = [lambda t, p: M.add('gag', glock.play(n('G6'), 110), t, 0.8, p),
              lambda t, p: boxn.extend((t + 0.1 * j, n(m), 90, 0.4) for j, m in enumerate(('G5', 'B5', 'D6'))),
              lambda t, p: squeak(t, p),
              lambda t, p: boing(t, p, sec=0.8),
              lambda t, p: M.add('drums', slap.play(120), t, 0.9, p)]
    for f, kb, x in zip(sounds, BACK_AT, S['back']):
        f(bar(kb), pan_at(x))
        M.add('gag', tri.play(90), bar(kb), 0.5, pan_at(x))

    # ---- the leap ----
    tf = bar(FINAL)
    M.add('drums', crash.play(124), tf, 1.1)
    M.add('drums', timp.play(124), tf, 1.0)
    M.add('drums', bd.play(124), tf, 1.0)
    M.add('gag', tree.play(120), tf + 0.1, 0.9)
    for m in ('G3', 'B3', 'D4', 'G4'):
        M.add('band', horn.play(n(m), 112, dur=D - tf - 0.5), tf, 0.8)
        M.add('band', tpt_s.play(n(m) + 12, 104, dur=D - tf - 0.5), tf, 0.5)
    M.add('bass', pizz.play(n('G2'), 124), tf, 1.2)
    M.add('gag', glock.play(n('G6'), 110), tf + 0.25, 0.8)

    M.add('fx', box.render(boxn, D), 0.0, 1.2)
