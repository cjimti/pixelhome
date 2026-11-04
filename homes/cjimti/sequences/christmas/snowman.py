"""Snowman: Left and Right lie under fresh snow. A kid in a cyan hat pops up at the corner of Left and rolls a
snowball toward the porch, and a kid in orange comes in from the free end of Right with another: each ball eats
the snow in front of it and grows as it goes, leaving bare night behind. They push them up the porch sides onto
Porch Front, the second is heaved up against the first, and the orange kid rolls a smaller third one for the
head. Coal buttons, a carrot nose, two coal eyes, a red scarf and a top hat pop on one by one. Gold sparkle
streams in from both wings and swirls round him, and he comes alive: he bounces, wiggles, hops off the porch
and along Left, and does a little dance. Then the sun comes up over the end of Right and warm gold creeps across
the house toward him: he droops, drips and shivers, smaller and smaller, nearly gone. A fresh flurry sweeps the
whole house from the back of the Side to the end of Right, chasing the sun away, and he springs back bigger than
before, leaps back to the porch with the kids running in to meet him, and tips his hat for the last chord.

Music: an original bouncy tune in F at 120 crotchets a minute (a bar is two seconds). Each snowball rolls on a
marimba that ticks under it on the quavers, panned with it, lower and louder as it grows; the clarinet has the
tune. Thumps for each ball set down, a pop for every button, nose, eye, scarf and hat. A cymbal swell and glass
glissandi for the sparkle, then the tune on bassoon and tuba (his voice) over an oom-pah, a bass drum on every
bounce, a slide whistle and woodblock on every hop, xylophone and claps for the dance. The sun gets slow, sagging
horns in F minor, a slide whistle melting down, a pizzicato plink for every drip and a xylophone chattering for
the shivers; a hush; then a rushing whoosh with sleigh bells across the house for the flurry, a boing as he
springs back, timpani under the leaps and the whole band for the finish."""
import numpy as np
from pixelhome.fx import DT, hexc, light, keys, smoothstep, lerp, Flicker, nframes

CODE = 'XM15'
TITLE = 'Snowman'
KIND = 'show'
DESCRIPTION = ('Two kids roll snowballs along the wings and stack a snowman on the porch. A sparkle brings him to life, '
               'he hops and dances along the roof, nearly melts when the sun comes out, and a fresh flurry brings him back.')
VOICEOVER = "Fresh snow on the roof. Grab your mittens, we're building a snowman."

D = 86.0
SEED = 15

NIGHT = hexc('#0c2aa8')
FLAKE = hexc('#e8f0ff')
SNOW = hexc('#c8d8ff')
BODY = hexc('#f4f6ff')
KID_A = hexc('#00d8ff')                 # cyan bobble hat
KID_B = hexc('#ff6400')                 # orange coat
CARROT = hexc('#ff5a00')
SCARF = hexc('#ff0a10')
HAT = hexc('#3a10a0')
GOLD = hexc('#ffb020')
SUN = hexc('#ff9a10')
DRIP = hexc('#60b0ff')

# the path: Side 0-490, Left 492-892, Porch Left 896-1309, Porch Front 1314-1658, Porch Right 1662-2030, Right 2036-2512
LEFT0, LEFT1, PL1, PF0, PF1, PR1, END = 492.0, 892.0, 1309.0, 1314.0, 1658.0, 2030.0, 2512.0

# ---- the beat grid: 120 crotchets a minute, bar 0 at 1 s ----
T0, BEAT = 1.0, 0.5
BAR = 4 * BEAT


def bt(bar, beat=0.0):
    return T0 + bar * BAR + beat * BEAT


# the snowman: three balls in path order (bottom, middle, head), then the hat. REF is the bottom ball's centre
R = (55.0, 40.0, 26.0)
HAT_W = 44.0
HOME = PF0 + R[0] + 4                    # on the porch
AWAY = LEFT0 + R[0] + 6                  # on Left, for the dance

KID_A_IN, KID_B_IN = bt(1), bt(2)
ROLL = [  # (ball, t0, t1, p0, p1, r0, r1): each ball rolled from p0 to p1, growing from r0 to r1
    (0, bt(1), bt(6), LEFT0 + 20, LEFT1 - 10, 4.0, 46.0),
    (0, bt(6), bt(9), LEFT1 - 10, HOME, 46.0, R[0]),
    (1, bt(2), bt(6, 2), END + 6, PR1 + 10, 4.0, 34.0),
    (1, bt(6, 2), bt(10), PR1 + 10, HOME + R[0] + R[1], 34.0, R[1]),
    (2, bt(11), bt(13), PR1 - 4, HOME + R[0] + 2 * R[1] + R[2], 4.0, R[2]),
]
T_SET = (bt(9), bt(10), bt(13))          # each ball set in place: a thump
POPS = [('button', bt(13, 1)), ('button', bt(13, 2)), ('button', bt(13, 3)), ('nose', bt(14)), ('eye', bt(14, 1)),
        ('eye', bt(14, 1.5)), ('scarf', bt(14, 2.5)), ('hat', bt(15))]
T_SPARK, T_ALIVE = bt(16), bt(18)
T_HOP, T_DANCE = bt(22), bt(25)
HOPS = [T_HOP + k * BEAT for k in range(12)]
T_SUN, T_MELT, T_SHIVER, T_GONE = bt(28), bt(29, 2), bt(31), bt(32, 2)
SUN_V = (END - (AWAY + 240)) / (T_GONE - T_SUN)     # the gold front reaches him as he is nearly gone
T_SPRING = bt(34)
FLURRY_V = 1100.0
T_FLURRY = T_SPRING - AWAY / FLURRY_V               # the flurry, from the back of the Side, reaches him on the downbeat
LEAPS = [bt(35, 2 * k) for k in range(4)]          # four big leaps back to the porch, one every two beats
T_LANDED = bt(37)
T_FINALE, T_TIP, T_FINAL = bt(37), bt(40, 2), bt(41)


def ref(t):
    """Where his bottom ball is, and his squash (1 = round), wiggle and scale."""
    if t < T_HOP:
        p = HOME
        if t >= T_ALIVE:                               # bounce on every beat, wiggle on the off-beats
            p += 12 * np.sin(2 * np.pi * (t - T_ALIVE) / (2 * BEAT)) * smoothstep(T_ALIVE, T_ALIVE + 1, t)
        return p
    if t < HOPS[-1] + BEAT:
        k = min(int((t - T_HOP) / BEAT), len(HOPS) - 1)
        u = smoothstep(0.0, 0.6, (t - HOPS[k]) / BEAT)
        a = lerp(HOME, AWAY, k / len(HOPS))
        b = lerp(HOME, AWAY, (k + 1) / len(HOPS))
        return a + (b - a) * u
    if t < LEAPS[0]:                                   # the dance: side-steps on the beats
        if t < T_SUN:
            ph = (t - T_DANCE) / BEAT
            step = [0, 28, 0, -28][int(ph) % 4]
            nxt = [0, 28, 0, -28][(int(ph) + 1) % 4]
            return AWAY + step + (nxt - step) * smoothstep(0.6, 1.0, ph % 1)
        return AWAY
    if t < T_LANDED:
        k = min(int((t - LEAPS[0]) / (2 * BEAT)), 3)
        u = smoothstep(0.0, 0.75, (t - LEAPS[k]) / (2 * BEAT))
        a = lerp(AWAY, HOME, k / 4)
        b = lerp(AWAY, HOME, (k + 1) / 4)
        return a + (b - a) * u
    return HOME + 8 * np.sin(2 * np.pi * (t - T_FINALE) / (2 * BEAT))


def size(t):
    """His scale: shrinking as he melts, springing back past full size."""
    melt = smoothstep(T_MELT, T_GONE, t)
    s = 1 - 0.68 * melt
    if t >= T_SPRING:
        a = t - T_SPRING
        s = max(1.06 + (0.32 - 1.06) * np.exp(-a / 0.12) + 0.2 * np.exp(-a / 0.5) * np.sin(2 * np.pi * a * 2.5), 0.32)
    return s


def squash(t):
    """Bounce: shorter and wider on the beat, taller in between."""
    if T_ALIVE <= t < T_HOP or t >= T_FINALE:
        ph = ((t - T_ALIVE) / BEAT) % 1
        return 1 + 0.18 * np.exp(-ph / 0.12) - 0.06
    if T_HOP <= t < HOPS[-1] + BEAT:
        ph = ((t - T_HOP) / BEAT) % 1
        return 1 - 0.15 * np.sin(np.pi * min(ph / 0.6, 1)) + 0.2 * np.exp(-max(ph - 0.6, 0) / 0.1) * (ph > 0.6)
    return 1.0


def balls_at(t):
    """Centres and radii of the three balls: rolling, set, or part of him."""
    if t < T_SET[2]:
        cs, rs = [np.nan] * 3, [0.0] * 3
        for b, t0, t1, p0, p1, r0, r1 in ROLL:
            if t >= t0:
                u = np.clip((t - t0) / (t1 - t0), 0, 1)
                cs[b] = p0 + (p1 - p0) * u
                rs[b] = r0 + (r1 - r0) * u
        return cs, rs
    s, q, p = size(t), squash(t), ref(t)
    rs = [r * s * q for r in R]
    cs = [p, p + rs[0] + rs[1], p + rs[0] + 2 * rs[1] + rs[2]]
    return cs, rs


def kids(t):
    """Where the two kids are (nan when away)."""
    cs, rs = balls_at(t) if t < T_SET[2] else ([np.nan] * 3, [0] * 3)
    a = b = np.nan
    if KID_A_IN <= t < T_SET[0] + 0.3:
        a = cs[0] - rs[0] - 9
    elif KID_A_IN <= t < T_ALIVE:                         # pats the snowman into shape
        a = HOME - R[0] - 10 + 4 * np.sin(2 * np.pi * t * 2)
    elif T_ALIVE <= t < T_HOP + 3:                       # backs off, then runs ahead of him round the corner and out
        a = float(keys(t, [(T_ALIVE, HOME - R[0] - 10), (T_ALIVE + 1.5, LEFT0 + 30), (T_HOP + 1.0, LEFT0 + 30),
                           (T_HOP + 3, -20)]))
    elif LEAPS[0] <= t:                                   # back in from the free end of Right for the finish
        a = float(keys(t, [(LEAPS[0], END + 20), (T_LANDED, HOME + 300), (D, HOME + 300)]))
        a += 6 * np.sin(2 * np.pi * (t - T_FINALE) / (2 * BEAT)) * (t > T_FINALE)
    if KID_B_IN <= t < T_SET[1] + 0.3:
        b = cs[1] + rs[1] + 9
    elif T_SET[1] + 0.3 <= t < T_SET[2] + 0.3 and t >= ROLL[4][1]:
        b = cs[2] + rs[2] + 9
    elif T_SET[1] + 0.3 <= t < ROLL[4][1]:
        b = float(keys(t, [(T_SET[1] + 0.3, HOME + R[0] + 2 * R[1] + 12), (ROLL[4][1], PR1 + 5)]))
    elif T_SET[2] + 0.3 <= t < T_SUN + 1.5:
        b = float(keys(t, [(T_SET[2] + 0.3, HOME + 260), (T_ALIVE, HOME + 260), (T_ALIVE + 2, 2300),
                           (T_SUN, 2300), (T_SUN + 1.5, END + 20)]))
    elif LEAPS[0] <= t:
        b = float(keys(t, [(LEAPS[0] + 0.4, END + 20), (T_LANDED + 0.3, HOME + 340), (D, HOME + 340)]))
        b += 6 * np.sin(2 * np.pi * (t - T_FINALE) / (2 * BEAT) + 1) * (t > T_FINALE)
    return a, b


def plan(seed=SEED):
    """The random draws render() and score() share: drips off him as he melts, the sparkle's paths, the flakes."""
    rng = np.random.default_rng(seed)
    drips = []
    t = T_MELT
    while t < T_GONE + 0.8:
        rate = 2 + 8 * smoothstep(T_MELT, T_GONE, t)
        t += rng.exponential(1 / rate)
        drips.append((t, rng.uniform(-1, 1), rng.choice([-1, 1]) * rng.uniform(40, 120)))
    spark = rng.uniform(0, 1, (60, 3))
    return drips, spark


def render(G, seed=SEED):
    rng = np.random.default_rng(seed)
    F = nframes(D)
    out = np.zeros((F, G.N, 3))
    x = G.pd[G.path]
    drips, spark = plan(seed)
    flakes = Flicker(rng, G.N, 0.08, 0.5)
    field = ((x >= LEFT0) & (x <= PL1)) | (x >= PF1)      # where the fresh snow lies at the start (not the Side)
    cover = field.astype(float)                           # how much snow is still on the ground
    porch = (x >= PF0) & (x <= PF1)

    for f in range(F):
        t = f * DT
        fr = np.zeros((G.N, 3))
        master = keys(t, [(0, 0), (0.8, 1), (D - 1.6, 1), (D - 0.1, 0)])

        # the snowballs eat the snow in front of them
        cs, rs = balls_at(t)
        if t < T_SET[2] + 0.1:
            for c, r in zip(cs, rs):
                if not np.isnan(c):
                    cover = np.minimum(cover, 1 - np.exp(-((x - c) / max(r, 4)) ** 4))
        flurry = T_FLURRY + x / FLURRY_V
        covered = t >= flurry                             # the flurry lays new snow everywhere behind its front
        sun_front = END - SUN_V * (t - T_SUN)
        sunny = smoothstep(sun_front - 40, sun_front + 80, x) * (t >= T_SUN) * (~covered)

        # the bed: night blue, flakes twinkling, fresh snow where it lies
        tw = np.clip(flakes(t), 0, None) ** 4
        snow_lvl = np.where(covered, 0.36 * (1 - 0.6 * smoothstep(T_FINALE, T_FINALE + 0.5, t)), 0.4 * cover * (1 - 0.6 * sunny) + 0.12 * porch * (t < T_SUN))
        bed = 0.22
        fr += light(NIGHT, bed * (1 - sunny)) + light(SNOW, snow_lvl) + light(FLAKE, 0.35 * tw * (1 - sunny))
        fr += light(SUN, 0.5 * sunny * (0.9 + 0.1 * np.sin(x / 30 - 2 * t)))
        if T_SUN <= t < T_FLURRY + 2.5:                   # the sun itself, rising over the free end of Right
            rise = smoothstep(T_SUN, T_SUN + 3, t) * (1 - smoothstep(T_FLURRY + END / FLURRY_V - 0.6,
                                                                       T_FLURRY + END / FLURRY_V, t))
            fr += light(GOLD, 0.95 * rise * np.exp(-((x - END) / 70) ** 2))

        # the flurry: a dense band of flakes racing from the back of the Side to the end of Right
        if T_FLURRY - 0.2 <= t < T_FLURRY + END / FLURRY_V + 1.0:
            front = FLURRY_V * (t - T_FLURRY)
            band = np.exp(-((x - front) / 90) ** 2) + 0.4 * np.exp(-np.clip(front - x, 0, None) / 250) * (x < front)
            fr += light(FLAKE, 0.95 * band * (0.6 + 0.4 * np.clip(flakes(5 * t), 0, None)))

        # the kids
        ka, kb = kids(t)
        for k, col in ((ka, KID_A), (kb, KID_B)):
            if not np.isnan(k):
                fr += light(col, 1.0 * np.exp(-((x - k) / 8) ** 2))

        # the snowballs and the snowman
        s = size(t)
        melt = smoothstep(T_MELT, T_GONE, t) * (t < T_SPRING)
        shiver = 4 * np.sin(2 * np.pi * 11 * t) * smoothstep(T_SHIVER, T_SHIVER + 1, t) * (t < T_SPRING)
        white = lerp(BODY, hexc('#ffe0a0'), 0.5 * melt)
        lvl = 0.8 - 0.25 * melt
        if T_SPRING <= t < T_SPRING + 0.6:
            lvl += 0.4 * np.exp(-(t - T_SPRING) / 0.2)
        I = np.zeros(G.N)
        for c, r in zip(cs, rs):
            if np.isnan(c) or r <= 0:
                continue
            d = np.abs(x - c - shiver) / max(r, 2)
            I = np.maximum(I, lvl * np.sqrt(np.clip(1 - d ** 2, 0, 1)) ** 0.6)
        if t >= T_SET[2]:
            mid, head = cs[1] + shiver, cs[2] + shiver
            neck = cs[1] + rs[1] + shiver
            sc = s * squash(t)

            def on(kind, k=0):
                ts = [p[1] for p in POPS if p[0] == kind][k]
                return float(smoothstep(ts - 0.02, ts + 0.05, t))

            def pop(kind, k=0):
                ts = [p[1] for p in POPS if p[0] == kind][k]
                return float(np.exp(-max(t - ts, 0) / 0.15) * (t >= ts))

            for k, dx in enumerate((-15, 0, 15)):          # coal buttons: dark gaps in the middle ball
                I *= 1 - 0.95 * on('button', k) * np.exp(-((x - mid - dx * sc) / (3.2 * sc)) ** 2)
            blink = 1.0
            if T_ALIVE <= t:
                for tb in (T_ALIVE + 0.3, T_ALIVE + 0.6, T_ALIVE + 4.1, bt(24, 1), bt(30, 1), T_SPRING + 0.4):
                    blink = min(blink, abs(t - tb) / 0.1) if abs(t - tb) < 0.1 else blink
            for k, dx in enumerate((-9, 9)):               # coal eyes
                I *= 1 - 0.95 * on('eye', k) * blink * np.exp(-((x - head - dx * sc) / (3.0 * sc)) ** 2)
            fr += I[:, None] ** 2.2 * white
            fr += light(CARROT, on('nose') * (1.0 + 0.5 * pop('nose')) * np.exp(-((x - head) / (5.5 * sc)) ** 2))
            sc_w = np.exp(-((x - neck) / (10 * sc)) ** 2) + 0.8 * np.exp(-((x - neck + 18 * sc) / (6 * sc)) ** 2)
            fr += light(SCARF, on('scarf') * (0.95 + 0.4 * pop('scarf')) * np.clip(sc_w, 0, 1))
            hat0 = cs[2] + rs[2] + shiver
            lift = 0.0
            if T_TIP - 0.5 <= t < T_FINAL:                 # he tips his hat
                lift = 60 * np.sin(np.pi * (t - (T_TIP - 0.5)) / (T_FINAL - T_TIP + 0.5))
            hx = x - hat0 - lift
            crown = ((hx > 6 * sc) & (hx < HAT_W * sc)).astype(float)
            brim = np.exp(-((hx - 3 * sc) / (3 * sc)) ** 2)
            band = np.exp(-((hx - 10 * sc) / (3 * sc)) ** 2)
            hat_on = on('hat') * (1 - 0.3 * melt)
            fr += light(HAT, hat_on * (0.75 * crown + 0.4 * pop('hat')))
            fr += light(BODY, hat_on * 0.35 * brim) + light(SCARF, hat_on * 0.9 * band)
        else:
            fr += I[:, None] ** 2.2 * white

        # patting him into shape: puffs where the cyan kid pats
        if T_SET[0] + 0.3 <= t < T_ALIVE and not np.isnan(ka):
            ph = (t * 2) % 1
            fr += light(FLAKE, 0.6 * np.exp(-ph / 0.15) * np.exp(-((x - ka - 14) / 8) ** 2))

        # set down: a puff of snow both ways
        for ts in T_SET:
            a = t - ts
            if 0 <= a < 0.8:
                c = balls_at(ts + 0.01)[0][T_SET.index(ts)]
                ring = np.exp(-((np.abs(x - c) - 40 - 200 * a) / 18) ** 2) * np.exp(-a / 0.25)
                fr += light(FLAKE, 0.8 * ring)

        # the sparkle: gold glitter streams in from both wings and swirls round him
        if T_SPARK <= t < T_ALIVE + 1.2:
            u = np.clip((t - T_SPARK) / (T_ALIVE - T_SPARK), 0, 1)
            centre = HOME + R[0] + R[1]
            for j, (a0, ph, sp) in enumerate(spark):
                side = -1 if j % 2 else 1
                start = LEFT0 + 20 + a0 * 300 if side < 0 else END - 20 - a0 * 300
                p = lerp(start, centre + 150 * np.sin(2 * np.pi * (ph + 3 * u)) * (1 - u) * 0.6, u ** (0.6 + sp))
                e = (0.5 + 0.5 * np.sin(2 * np.pi * (6 + 4 * sp) * t + ph * 6)) * (t < T_ALIVE)
                fr += light(GOLD, 0.9 * e * np.exp(-((x - p) / 7) ** 2))
            if t >= T_ALIVE:                               # he comes alive: a burst
                a = t - T_ALIVE
                fr += light(GOLD, 1.0 * np.exp(-a / 0.3) * np.exp(-((x - centre) / (60 + 700 * a)) ** 2))

        # landings: snow bursts, small for hops, big for leaps
        for k, th in enumerate(HOPS + LEAPS):
            big = k >= len(HOPS)
            tl = th + (0.6 * BEAT if not big else 0.75 * 2 * BEAT)
            a = t - tl
            if 0 <= a < 1.0:
                c = ref(tl) + (R[0] + R[1]) * size(tl)
                reach = 300 if big else 60
                ring = np.exp(-((np.abs(x - c) - 150 * size(tl) - reach * a / 0.5) / 20) ** 2) * np.exp(-a / (0.35 if big else 0.2))
                fr += light(FLAKE, (0.9 if big else 0.6) * ring)

        # drips running off him as he melts
        for td, off, v in drips:
            a = t - td
            if 0 <= a < 0.9:
                c = ref(td) + 120 * size(td) + off * 140 * size(td) + v * a
                fr += light(DRIP, 0.8 * (1 - a / 0.9) * np.exp(-((x - c) / 5) ** 2))

        # the finish: colour rings out from the porch on every beat, the hat tip flashes the house
        if T_FINALE <= t:
            ph = (t - T_FINALE) / BEAT
            k = int(ph)
            a = (ph % 1) * BEAT
            cols = (SCARF, KID_A, CARROT, GOLD, KID_B, FLAKE)
            d = np.abs(x - (PF0 + PF1) / 2)
            fill = smoothstep(170 + 2600 * a, 110 + 2600 * a, d) * (0.6 - 0.25 * a / BEAT)
            head = np.exp(-((d - 140 - 2600 * a) / 40) ** 2) * (1 - a / BEAT)
            prev = smoothstep(170 + 2600 * a, 230 + 2600 * a, d) * 0.35
            fr += light(cols[k % len(cols)], fill * (t < T_FINAL)) + light(FLAKE, 0.7 * head * (t < T_FINAL))
            fr += light(cols[(k - 1) % len(cols)], prev * (t < T_FINAL) * (k > 0))
            if t >= T_FINAL:
                fr += light(BODY, 0.9 * np.exp(-(t - T_FINAL) / 0.4) * np.ones(G.N))
                fr += light(GOLD, 0.35 * np.exp(-(t - T_FINAL) / 1.5) * np.ones(G.N))

        out[f][G.path] = np.clip(fr, 0, 1) * master ** 2.2
    return out


# ---- music ----
CHORDS = {
    'F': ('F2', 'C3', ('A3', 'C4', 'F4')), 'Bb': ('Bb1', 'F2', ('Bb3', 'D4', 'F4')),
    'C7': ('C2', 'G2', ('Bb3', 'E4', 'G4')), 'Dm': ('D2', 'A2', ('A3', 'D4', 'F4')),
    'Gm': ('G1', 'D2', ('Bb3', 'D4', 'G4')), 'Fm': ('F2', 'C3', ('Ab3', 'C4', 'F4')),
    'Bbm': ('Bb1', 'F2', ('Bb3', 'Db4', 'F4')), 'Db': ('Db2', 'Ab2', ('Ab3', 'Db4', 'F4')),
    'C': ('C2', 'G2', ('C4', 'E4', 'G4')), 'A7': ('A1', 'E2', ('C#4', 'E4', 'G4')),
}
TUNE = [
    [(0, 'C5', 1), (1, 'A4', .5), (1.5, 'F4', .5), (2, 'G4', .5), (2.5, 'A4', .5), (3, 'C5', 1)],
    [(0, 'D5', 1), (1, 'C5', .5), (1.5, 'A4', .5), (2, 'G4', 2)],
    [(0, 'A4', .5), (.5, 'Bb4', .5), (1, 'C5', 1), (2, 'F5', 1), (3, 'E5', .5), (3.5, 'D5', .5)],
    [(0, 'C5', 2), (2, 'Bb4', .5), (2.5, 'A4', .5), (3, 'G4', 1)],
    [(0, 'C5', 1), (1, 'A4', .5), (1.5, 'F4', .5), (2, 'G4', .5), (2.5, 'A4', .5), (3, 'C5', 1)],
    [(0, 'D5', 1), (1, 'F5', .5), (1.5, 'D5', .5), (2, 'C5', 1), (3, 'A4', 1)],
    [(0, 'G4', .5), (.5, 'A4', .5), (1, 'Bb4', .5), (1.5, 'G4', .5), (2, 'E4', 1), (3, 'G4', 1)],
    [(0, 'F4', 2), (2, 'C4', .5), (2.5, 'D4', .5), (3, 'E4', 1)],
]
HARM = [('F', 'F'), ('Bb', 'C7'), ('F', 'Dm'), ('C7', 'C7'), ('F', 'F'), ('Bb', 'F'), ('C7', 'C7'), ('F', 'C7')]
SUN_TUNE = [[(0, 'C5', 2), (2, 'Ab4', 1), (3, 'F4', 1)], [(0, 'Db5', 2), (2, 'C5', 1), (3, 'Bb4', 1)],
            [(0, 'Ab4', 2), (2, 'G4', 1), (3, 'F4', 1)], [(0, 'E4', 4)]]
SUN_HARM = [('Fm', 'Fm'), ('Bbm', 'Db'), ('Fm', 'Fm'), ('C', 'C')]
POP_NOTES = {'button': ('F3', 'A3', 'C4'), 'nose': ('F5',), 'eye': ('C6', 'A5'), 'scarf': ('F4',), 'hat': ('F4',)}


def score(M, G):
    from pixelhome.audio import SR, note, slide, whoosh
    n = note
    drips, spark = plan()

    clar = M.sampler('Woodwinds/Clarinet/susLong/*.wav', tune=-12)
    clar_st = M.sampler('Woodwinds/Clarinet/stac/*.wav', tune=-12)
    flute = M.sampler('Woodwinds/Flute/susvib/*.wav', tune=-12)
    flute_st = M.sampler('Woodwinds/Flute/stac/*.wav', tune=-12)
    bsn = M.sampler('Woodwinds/Bassoon/stac/*.wav', tune=-12)
    bsn_s = M.sampler('Woodwinds/Bassoon/sus/*.wav', tune=-12)
    tuba = M.sampler('Brass/Tuba/stac/*.wav', tune=-12)
    tuba_s = M.sampler('Brass/Tuba/sus/*.wav', tune=-12)
    horn = M.sampler('Brass/F Horn/sus/*.wav', tune=-12)
    horn_st = M.sampler('Brass/F Horn/stac/*.wav', tune=-12)
    tpt = M.sampler('Brass/Trumpet/sus/*.wav', tune=-12)
    tpt_st = M.sampler('Brass/Trumpet/stac/*.wav', tune=-12)
    bone = M.sampler('Brass/Tenor Trombone/sus/*.wav', tune=-12)
    vln = M.sampler('Strings/Violin Section/susVib/*.wav', tune=-12)
    trem = M.sampler('Strings/Violin Section/Trem/*.wav', tune=-12)
    vla = M.sampler('Strings/Viola Section/susvib/*.wav', tune=-12)
    vc = M.sampler('Strings/Cello Section/susvib/*.wav', tune=-12)
    pizz = M.sampler('Strings/Violin Section/Pizz/*.wav', tune=-12)
    cb = M.sampler('Strings/Solo Contrabass/Pizz/*.wav', tune=-12)
    harp = M.sampler('Strings/Harp/*.wav')
    glock = M.sampler('Percussion/Glock/*.wav', tune=-12)
    xylo = M.sampler('Percussion/Xylo/*.wav', tune=-12)
    marimba = M.sampler('Percussion/Marimba/*.wav', tune=-12)
    bd = M.hits('VSCO 1 Percussion/drums/bass/bdrum_f_*.wav')
    timp = M.hits('Percussion/Timpani/Timpani1_Hit_v[13]*.wav')
    troll = M.hits('Percussion/Timpani/Rolls/Timpani1_Roll_v3*.wav')
    crash = M.hits('Percussion/cymbal-crash1_ff*.wav')
    swell = M.hits('Percussion/susCymb1-cresc-Median*.wav')
    tri = M.hits('Percussion/Triangle3-Hit_v1*.wav')
    block = M.hits('VSCO 1 Percussion/varWood/wood_click_f*.wav')
    claves = M.hits('Percussion/Claves1_Hit_v[23]*.wav')
    shake = M.hits('VSCO 1 Percussion/varMetal/various/sleighbell[12]_shake1.wav')
    bells = M.hits('Percussion/Sleighbells_Hit*.wav')
    chimes = M.hits('VSCO 1 Percussion/varMetal/various/windchimes_asc1.wav')
    chimes_f = M.hits('VSCO 1 Percussion/varMetal/various/windchimes_fastAsc1.wav')
    pop_ = M.hits('VSCO 1 Percussion/varWood/wood_click3_loud.wav')
    guiro = M.hits('VSCO 1 Percussion/varWood/guiro_short*.wav')

    for name, gain, rev in (('tune', 0.34, 0.16), ('counter', 0.26, 0.2), ('bass', 0.36, 0.08), ('chords', 0.26, 0.16),
                            ('pad', 0.24, 0.3), ('perc', 0.34, 0.14), ('fx', 0.3, 0.18), ('sparkle', 0.24, 0.3),
                            ('roll', 0.22, 0.1)):
        M.bus(name, gain=gain, reverb=rev)

    order = np.argsort(G.pd)
    xs, ds = G.pos[order, 0], G.pd[order]
    x0, x1 = xs.min(), xs.max()

    def pan_at(dd):
        x = np.interp(np.clip(dd, 0, G.length), ds, xs)
        return float(0.85 * (2 * (x - x0) / (x1 - x0) - 1))

    def mono(sig, pans):
        a = (np.clip(pans, -1, 1) + 1) * np.pi / 4
        return np.vstack([sig * np.cos(a), sig * np.sin(a)]) * np.sqrt(2)

    def line(bars, k0, sus, st=None, bus='tune', vel=96, pan=0.0, gain=1.0, octave=0):
        for j, bar in enumerate(bars):
            for b, m, ln in bar:
                inst = st if (st is not None and ln <= 0.5) else sus
                M.add(bus, inst.play(n(m) + octave, vel, dur=ln * BEAT * 0.92, release=0.15), bt(k0 + j, b), gain, pan)

    def oompah(k0, harm, vel=88, gain=1.0, low=cb, chord=pizz):
        for j, (c1, c2) in enumerate(harm):
            for half, c in ((0, c1), (1, c2)):
                root, fifth, ch = CHORDS[c]
                M.add('bass', low.play(n(root if half == 0 or c1 != c2 else fifth), vel + 8), bt(k0 + j, 2 * half), 0.9 * gain)
                for m in ch:
                    M.add('chords', chord.play(n(m), vel - 12, dur=0.2), bt(k0 + j, 2 * half + 1), 0.4 * gain, 0.15)

    def held(k0, harm, inst, vel=60, gain=1.0, bus='pad', pan=0.0):
        for j, (c1, c2) in enumerate(harm):
            for half, c in ((0, c1), (1, c2)) if c1 != c2 else ((0, c1),):
                ln = 2 if c1 != c2 else 4
                for m in CHORDS[c][2]:
                    M.add(bus, inst.play(n(m), vel, dur=ln * BEAT * 0.98, release=0.3), bt(k0 + j, 2 * half), 0.35 * gain, pan)

    # ---- bar 0: snow on the roof ----
    for k, m in enumerate(('F4', 'A4', 'C5', 'F5', 'A5', 'C6')):
        M.add('sparkle', glock.play(n(m), 70), 0.2 + 0.25 * k, 0.5, -0.6 + 0.24 * k)
    for m in ('F3', 'C4', 'A4'):
        M.add('pad', vln.play(n(m), 55, dur=2.4, release=0.6), 0.3, 0.5)
    M.add('sparkle', chimes.play(70), 0.1, 0.4)

    # ---- bars 1-12: the snowballs roll, a marimba ticking under each on the quavers, lower as it grows ----
    for b, t0, t1, p0, p1, r0, r1 in ROLL:
        e = int(np.ceil((t0 - T0) / (BEAT / 2)))
        while T0 + e * BEAT / 2 < t1:
            t = T0 + e * BEAT / 2
            u = (t - t0) / (t1 - t0)
            r = r0 + (r1 - r0) * u
            p = p0 + (p1 - p0) * u
            chord = CHORDS[HARM[int((t - bt(1)) / BAR) % 8][int(((t - bt(1)) / BAR % 1) * 2)]]
            ch = [n(chord[0]) + 24, n(chord[2][1]), n(chord[2][2])]
            m = ch[e % 3] + (12 if r < 20 else 0)
            M.add('roll', marimba.play(m, int(70 + 40 * r / 55)), t, 0.4 + 0.6 * r / 55, pan_at(p))
            e += 1
    line(TUNE, 1, clar, clar_st, vel=90)
    oompah(1, HARM, vel=80)
    line(TUNE[:4], 9, flute, flute_st, vel=86)
    oompah(9, HARM[:4], vel=78)
    for k, ts in enumerate(T_SET):                       # each ball set down: a thump, the third a bigger one
        c = balls_at(ts + 0.01)[0][k]
        M.add('perc', timp.play(100 + 10 * k), ts, 0.6, pan_at(c))
        M.add('perc', bd.play(90 + 10 * k), ts, 0.6, pan_at(c))
        M.add('sparkle', shake.play(70, dur=0.6), ts, 0.3, pan_at(c))
    for k in range(int((T_ALIVE - T_SET[0] - 0.3) * 2)):  # the cyan kid patting him into shape
        t = T_SET[0] + 0.3 + k * 0.5
        if t > T_SPARK:
            break
        M.add('perc', block.play(60, pitch=-5), t, 0.25, pan_at(HOME - R[0]))

    # ---- bars 13-15: buttons, nose, eyes, scarf, hat ----
    held(13, [('F', 'F'), ('Bb', 'C7'), ('F', 'F')], vla, vel=58)
    for k, (c1, c2) in enumerate([('F', 'F'), ('Bb', 'C7'), ('F', 'F')]):
        M.add('bass', cb.play(n(CHORDS[c1][0]), 90), bt(13 + k), 0.8)
        M.add('bass', cb.play(n(CHORDS[c2][1]), 80), bt(13 + k, 2), 0.7)
    count = {}
    for kind, ts in POPS:
        i = count.get(kind, 0)
        count[kind] = i + 1
        cs, rs = balls_at(ts + 0.01)
        where = {'button': cs[1] + (-15, 0, 15)[min(i, 2)], 'nose': cs[2], 'eye': cs[2] + (-9, 9)[min(i, 1)],
                 'scarf': cs[1] + rs[1], 'hat': cs[2] + rs[2] + 20}[kind]
        p = pan_at(where)
        m = n(POP_NOTES[kind][min(i, len(POP_NOTES[kind]) - 1)])
        if kind == 'button':
            M.add('perc', pop_.play(100), ts, 0.6, p)
            M.add('counter', marimba.play(m, 100), ts, 0.7, p)
        elif kind == 'nose':
            M.add('perc', pop_.play(110, pitch=4), ts, 0.6, p)
            M.add('tune', flute_st.play(m, 100), ts, 0.7, p)
        elif kind == 'eye':
            M.add('sparkle', glock.play(m, 96), ts, 0.7, p)
        elif kind == 'scarf':
            for j, mm in enumerate(('F4', 'A4', 'C5', 'F5', 'A5')):
                M.add('counter', harp.play(n(mm), 80), ts + 0.04 * j, 0.5, p)
        else:                                            # the hat: ta-da
            for j, mm in enumerate(('C4', 'F4', 'A4', 'C5')):
                M.add('chords', horn_st.play(n(mm) - 12, 104, dur=0.2), ts - 0.25 + (0.12 * j if j < 2 else 0.25), 0.4, p)
            M.add('tune', tpt.play(n('C5'), 104, dur=0.9, release=0.4), ts, 0.6, p)
            M.add('perc', crash.play(90), ts, 0.4, p)
            M.add('perc', tri.play(80), ts, 0.4, p)

    # ---- bars 16-17: the sparkle streams in and swirls; bar 18 he comes alive ----
    s = swell.play(90)
    M.add('perc', s, T_ALIVE - s.shape[1] / SR, 0.5)
    for m in ('C4', 'E4', 'G4', 'Bb4'):
        a = trem.play(n(m), 70, dur=T_ALIVE - T_SPARK, release=0.05)
        M.add('pad', a * np.linspace(0.2, 1, a.shape[1])[None], T_SPARK, 0.45)
    M.add('bass', tuba_s.play(n('C2'), 80, dur=T_ALIVE - T_SPARK, release=0.1), T_SPARK, 0.5)
    rng = np.random.default_rng(SEED + 7)
    gl = ['C5', 'E5', 'G5', 'Bb5', 'C6', 'E6']
    for k in range(32):                                  # glitter converging from both wings
        t = T_SPARK + (T_ALIVE - T_SPARK) * k / 32
        side = -1 if k % 2 else 1
        u = k / 32
        M.add('sparkle', glock.play(n(gl[k % 6]), int(rng.integers(55, 85))), t, 0.4, side * 0.85 * (1 - u))
    M.add('sparkle', chimes_f.play(90), T_SPARK + 0.5, 0.4, -0.7)
    M.add('sparkle', chimes_f.play(90), T_SPARK + 1.5, 0.4, 0.7)
    pc = pan_at(HOME + R[0] + R[1])
    for m in ('F3', 'A3', 'C4', 'F4'):
        M.add('chords', horn.play(n(m), 110, dur=1.0, release=0.6), T_ALIVE, 0.45)
        M.add('pad', vln.play(n(m) + 12, 100, dur=1.0, release=0.6), T_ALIVE, 0.35)
    M.add('perc', crash.play(118), T_ALIVE, 0.6, pc)
    M.add('perc', timp.play(118), T_ALIVE, 0.7, pc)
    M.add('bass', cb.play(n('F2'), 127), T_ALIVE, 1.0)
    for k, m in enumerate(('F4', 'A4', 'C5', 'F5', 'A5', 'C6')):
        M.add('sparkle', glock.play(n(m), 95), T_ALIVE + 0.06 * k, 0.6, pc)
    for tb in (T_ALIVE + 0.3, T_ALIVE + 0.6):            # the first blinks
        M.add('perc', xylo.play(n('C6'), 70, dur=0.1), tb, 0.4, pc)

    # ---- bars 18-21: he bounces (a bass drum on each beat) and wiggles (a guiro on the off-beats) ----
    voice = [list(b) for b in TUNE[:7]]
    line(voice, 18, bsn_s, bsn, vel=100, pan=pc * 0.5)
    line(voice, 18, tuba_s, tuba, 'counter', vel=90, gain=0.6, octave=-12, pan=pc * 0.5)
    oompah(18, HARM[:7], vel=88, low=tuba)
    for k in range(int((T_HOP - T_ALIVE) / BEAT)):
        t = T_ALIVE + k * BEAT
        M.add('perc', bd.play(80), t, 0.4, pc)
        M.add('perc', guiro.play(70), t + BEAT / 2, 0.25, pc + (0.15 if k % 2 else -0.15))

    # ---- bars 22-24: the hops along Porch Left and Left: a slide whistle up and a woodblock landing ----
    for k, th in enumerate(HOPS):
        p = pan_at(ref(th + 0.6 * BEAT))
        M.add('fx', slide(0.0, 0.3 * BEAT, 600 + 20 * k, 1100 + 20 * k, 0.6 * BEAT, 0.35), th, 0.5, p)
        M.add('perc', block.play(100), th + 0.6 * BEAT, 0.5, p)
        M.add('perc', bd.play(70), th + 0.6 * BEAT, 0.3, p)

    # ---- bars 25-27: the dance: tune on xylophone and trumpet, claps from Right ----
    line(TUNE[5:8], 25, xylo, None, 'counter', vel=90, gain=0.55, pan=-0.3)
    line(TUNE[5:8], 25, tpt, tpt_st, vel=96, pan=-0.2)
    oompah(25, HARM[5:8], vel=90, low=tuba)
    for k in range(int((T_SUN - T_DANCE) / BEAT)):
        t = T_DANCE + k * BEAT
        if k % 2:
            M.add('perc', claves.play(100), t, 0.35, pan_at(2300))
        if k % 4 in (1, 3):
            M.add('perc', pop_.play(70, pitch=-3), t, 0.25, pan_at(ref(t)))

    # ---- bars 28-32: the sun. F minor, horns sagging, a slide whistle melting, drips, shivers ----
    line(SUN_TUNE, 28, bone, None, vel=84, pan=0.2)
    line(SUN_TUNE, 28, horn, None, 'counter', vel=70, gain=0.6, octave=-12, pan=-0.2)
    held(28, SUN_HARM, vc, vel=66, gain=1.2)
    held(28, SUN_HARM, vla, vel=56, gain=0.8, pan=0.3)
    for k, (c1, _) in enumerate(SUN_HARM):
        M.add('bass', tuba_s.play(n(CHORDS[c1][0]), 72, dur=BAR * 0.95, release=0.4), bt(28 + k), 0.6)
    M.add('sparkle', chimes.play(80), T_SUN, 0.45, 0.95)
    for m in ('F4', 'Ab4', 'C5'):
        a = vln.play(n(m), 60, dur=3.0, release=0.8)
        M.add('pad', a * np.linspace(0.1, 1, a.shape[1])[None], T_SUN, 0.35, 0.8)
    mel = slide(0.0, T_GONE - T_MELT, 900, 260, T_GONE - T_MELT + 0.2, 0.3, 0.8)
    M.add('fx', mel, T_MELT, 0.45, pan_at(AWAY + 120))
    drip_notes = [n(m) for m in ('C6', 'Ab5', 'F5', 'Eb5', 'C5', 'Bb4')]
    for i, (td, off, v) in enumerate(drips):
        M.add('sparkle', pizz.play(drip_notes[i % 6], 80), td, 0.5, pan_at(ref(td) + 120 + off * 140))
    t = T_SHIVER
    k = 0
    while t < T_GONE + 0.3:                              # teeth chattering
        M.add('perc', xylo.play(n(('E5', 'F5')[k % 2]), 64 + 20 * smoothstep(T_SHIVER, T_GONE, t), dur=0.08), t, 0.35,
              pan_at(AWAY + 120))
        t += 0.09
        k += 1
    for m in ('E3', 'G3', 'Bb3', 'Db4'):
        M.add('pad', trem.play(n(m), 62, dur=T_GONE - T_SHIVER, release=0.4), T_SHIVER, 0.3)
    M.add('bass', bsn_s.play(n('C3'), 70, dur=T_FLURRY - T_GONE, release=0.5), T_GONE, 0.4, pan_at(AWAY))

    # ---- the flurry: a rushing whoosh with sleigh bells from the back of the Side to the end of Right ----
    dur = END / FLURRY_V + 0.6
    w = whoosh(dur, 400, 4000, 0.9, seed=68)
    M.add('fx', mono(w[0], np.linspace(pan_at(0), pan_at(END), w.shape[1])), T_FLURRY - 0.2, 0.7)
    for k in range(int(dur / 0.12)):
        t = T_FLURRY + k * 0.12
        M.add('perc', bells.play(90 if k % 2 == 0 else 70), t, 0.35, pan_at(FLURRY_V * (t - T_FLURRY)))
    for k, m in enumerate(('C5', 'D5', 'F5', 'G5', 'A5', 'C6', 'D6', 'F6')):
        t = T_FLURRY + k * (END / FLURRY_V) / 8
        M.add('sparkle', glock.play(n(m), 80), t, 0.4, pan_at(FLURRY_V * (t - T_FLURRY)))
    M.add('sparkle', chimes_f.play(100), T_FLURRY + 0.2, 0.5, -0.5)

    # ---- bar 34: he springs back; bars 35-36 the leaps; bars 37-41 the finish, the whole band ----
    pa = pan_at(AWAY + 120)
    M.add('fx', slide(0.0, 0.35, 300, 1500, 0.4, 0.5), T_SPRING - 0.05, 0.8, pa)
    M.add('perc', crash.play(120), T_SPRING, 0.6, pa)
    M.add('perc', timp.play(120), T_SPRING, 0.7, pa)
    for m in ('F3', 'A3', 'C4', 'F4'):
        M.add('chords', horn.play(n(m), 110, dur=0.8, release=0.4), T_SPRING, 0.45)
    M.add('bass', cb.play(n('F2'), 127), T_SPRING, 1.0)
    M.add('tune', tpt.play(n('C5'), 104, dur=0.8, release=0.3), T_SPRING, 0.6)
    for k, tl in enumerate(LEAPS):
        land = tl + 0.75 * 2 * BEAT
        p = pan_at(ref(land))
        M.add('fx', slide(0.0, 0.4, 500, 1400, 0.75 * 2 * BEAT, 0.4, 0.6), tl, 0.5, p)
        M.add('perc', timp.play(110), land, 0.7, p)
        M.add('perc', bd.play(110), land, 0.6, p)
        M.add('sparkle', shake.play(80, dur=0.5), land, 0.3, p)
    for k in range(4):                                   # the kids run back in from the end of Right
        M.add('perc', bells.play(80), LEAPS[0] + 0.25 * k, 0.3, 0.9)
    big = [list(b) for b in TUNE]
    line(big[4:6], 35, tpt, tpt_st, vel=104, pan=0.1)
    line(big[4:6], 35, flute, flute_st, 'counter', vel=90, gain=0.5, pan=-0.2)
    oompah(35, HARM[4:6], vel=96, low=tuba)
    line(big[:4], 37, tpt, tpt_st, vel=106, pan=0.1)
    line(big[:4], 37, clar, clar_st, 'counter', vel=92, gain=0.5, pan=-0.2)
    line(big[:4], 37, bsn_s, bsn, 'counter', vel=92, gain=0.5, octave=-12, pan=0.25)
    oompah(37, HARM[:3] + [('C7', 'C7')], vel=100, low=tuba)
    held(37, HARM[:3] + [('C7', 'C7')], horn, vel=74)
    rings = [n(m) for m in ('F5', 'A5', 'C6', 'A5', 'G5', 'E5')]
    for k in range(int((T_FINAL - T_FINALE) / BEAT)):
        t = T_FINALE + k * BEAT
        M.add('sparkle', glock.play(rings[k % 6], 80), t, 0.35, -0.6 if k % 2 else 0.6)
        M.add('perc', bells.play(95), t, 0.3, 0.6 if k % 2 else -0.6)
    ph = pan_at(HOME + R[0] + 2 * R[1] + 2 * R[2] + 20)
    M.add('fx', slide(0.0, 0.5, 700, 1600, 0.55, 0.4), T_TIP - 0.5, 0.6, ph)
    M.add('fx', slide(0.0, 0.45, 1600, 600, 0.5, 0.4), T_TIP + 0.05, 0.5, ph)
    r = troll.play(100, dur=1.0)
    M.add('perc', r * np.linspace(0.05, 1, r.shape[1])[None] ** 2, T_FINAL - 1.0, 0.6)
    for m in ('F3', 'A3', 'C4', 'F4'):
        M.add('chords', horn.play(n(m), 112, dur=2.4, release=1.0), T_FINAL, 0.45)
        M.add('pad', vln.play(n(m) + 12, 100, dur=2.4, release=1.0), T_FINAL, 0.4)
    M.add('tune', tpt.play(n('F5'), 106, dur=2.2, release=1.0), T_FINAL, 0.6)
    M.add('tune', flute.play(n('F5'), 90, dur=2.4, release=1.0), T_FINAL, 0.4)
    M.add('bass', cb.play(n('F2'), 127), T_FINAL, 1.0)
    M.add('bass', tuba_s.play(n('F1'), 120, dur=2.2, release=0.8), T_FINAL, 0.7)
    M.add('perc', crash.play(120), T_FINAL, 0.6, ph)
    M.add('perc', timp.play(120), T_FINAL, 0.8)
    M.add('perc', shake.play(110), T_FINAL, 0.5)
    for k, m in enumerate(('F4', 'A4', 'C5', 'F5', 'A5', 'C6')):
        M.add('sparkle', glock.play(n(m), 86), T_FINAL + 0.1 * k, 0.5, -0.5 + 0.2 * k)
