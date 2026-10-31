"""Hayride: Dusk falls over the farm (the sky slides from sunset orange through violet to night blue) and rows of
corn grow along the roof between glowing pumpkins. The corn sways a step on every beat of the hoedown and the
pumpkins answer, odd ones on 1 and 3, even ones on 2 and 4. A red tractor coughs to life at the free end of Right,
its headlight snaps on, and it pulls a gold hay wagon along Right, round the porch and into the pumpkin patch on the
Porch Front, a gust running through the corn ahead of it each bar; every bump throws hay and sends a jolt down the
length of the house. At the patch the wings trade dance steps while eight pumpkins hop into the wagon; it revs, the
rows crowd tight and shiver, and it lurches off along Porch Left and Left, the bumps getting bigger until the last
throws hay out to both ends of the roof, and putters out along Side into the dark. Fireflies blink; a match is
struck. It comes back the other way with two lanterns swinging on the wagon, lighting a lantern at every post, each
one flaring and swinging on the beat; on the run home light chases down the posts after it, and as it leaves off
the end of Right a flash races back the whole length of the roof and the house glows gold."""
import numpy as np
from pixelhome.fx import DT, hexc, light, keys, smoothstep, lerp, Flicker, nframes

CODE = 'TG14'
TITLE = 'Hayride'
KIND = 'show'
DESCRIPTION = ('A tractor pulls a hay wagon around the house at dusk, past glowing pumpkins and corn. It bumps, '
               'stops at the pumpkin patch to load up, and comes home lit by lanterns.')
VOICEOVER = "Grab some hay and hold on tight, the hayride leaves at sundown."

SUNSET = hexc('#ff4010')
DUSK = hexc('#7a28ff')
NIGHT = hexc('#3048ff')
PUMPKIN = hexc('#ff5000')
CORN = hexc('#ffc020')
VINE = hexc('#105000')
TRACTOR = hexc('#ff0c06')
HEAD = hexc('#fff0c8')
HAY = hexc('#ffb000')
RAIL = hexc('#c02800')
LANTERN = hexc('#ffa828')
SMOKE = hexc('#b8c0d0')
GOLD = hexc('#ffb000')
FIREFLY = hexc('#c8ff30')

D = 90.0
SEED = 14
BEAT, BAR = 0.5, 2.0                      # 120 bpm, 4/4: the hoedown's grid; every event below sits on it
PUMPKINS = [2440, 2300, 2160, 1940, 1760, 1180, 1010, 830, 690, 560]        # along the route (pd)
CORN_AT = [2480, 2370, 2230, 2090, 1990, 1850, 1700, 1250, 1100, 950, 760, 620, 420, 260, 110]
PATCH = [1530, 1575, 1620, 1700, 1780, 1860, 1930, 1995]                   # the pumpkin patch, revealed at the stop
POP0 = 1.0                                # dusk pumpkins pop in on eighths from here
T_COUGH = (8.0, 8.5, 9.0)
T_GO1, T_STOP, T_REV, T_GO2, T_GONE, T_GO3, T_HOME = 10.0, 24.0, 36.0, 40.0, 56.0, 60.0, 86.0
X_START, X_PATCH = 2490.0, 1360.0
HOPS = [28.0 + k for k in range(8)]       # one pumpkin into the wagon every other beat
HOP_T = 0.6
BUMPS = [(13.0, 1.0), (16.5, 1.0), (20.0, 1.0), (43.0, 1.0), (46.5, 1.0), (49.0, 1.0), (52.0, 2.0),
         (66.0, 0.6), (74.0, 0.6)]
POSTS = np.arange(70.0, 2500.0, 150.0)    # lantern posts lit on the way home
T_MATCH = 59.0
T_RUN_HOME = 76.0                        # everyone back in for the run home
WAGON = (30.0, 130.0)                     # wagon span behind the tractor


def leg(t, t0, t1, x0, x1, ein, eout):
    """Trapezoidal-velocity move from x0 at t0 to x1 at t1, accelerating over ein s and braking over eout s."""
    T, dist = t1 - t0, x1 - x0
    v = dist / (T - ein / 2 - eout / 2)
    u = min(max(t - t0, 0.0), T)
    if u < ein:
        return x0 + 0.5 * v * u * u / ein
    if u < T - eout:
        return x0 + v * ein / 2 + v * (u - ein)
    return x1 - 0.5 * v * (T - u) ** 2 / eout


def tractor(t):
    """(position along the path, direction of travel, visible)."""
    if t < 7.5:
        return X_START, -1, False
    if t < T_GO1:
        return X_START, -1, True
    if t < T_STOP:
        return leg(t, T_GO1, T_STOP, X_START, X_PATCH, 1.5, 2.0), -1, True
    if t < T_GO2:
        jit = 2.0 * np.sin(2 * np.pi * 9 * t) * smoothstep(T_REV, T_REV + 1, t)
        return X_PATCH + jit, -1, True
    if t < T_GONE + 1:
        return leg(t, T_GO2, T_GONE + 1, X_PATCH, -230.0, 1.5, 0.01), -1, True
    if t < T_GO3:
        return -400.0, 1, False
    if t < T_HOME:
        return leg(t, T_GO3, T_HOME, -150.0, 2700.0, 0.6, 0.01), 1, True
    return 3000.0, 1, False


def engine_pulses():
    """Every putt of the engine: (time, strength). The exhaust puffs and the putt-putt both come from these."""
    p = [(T_COUGH[0], 0.9), (T_COUGH[1], 0.6), (T_COUGH[2], 0.7)]
    for a, b, step, s in ((9.5, T_STOP, 0.25, 1.0), (T_STOP, T_REV, 0.5, 0.55), (T_REV, T_GO2, 0.125, 1.0),
                          (T_GO2, T_GONE + 1, 0.25, 1.0), (T_GO3, T_HOME, 0.25, 0.8)):
        p += [(float(t), s) for t in np.arange(a, b - 1e-6, step)]
    return p


def lantern_times():
    """When the wagon's middle passes each lantern post on the way home."""
    ts = np.arange(T_GO3, T_HOME, DT)
    mid = np.array([tractor(t)[0] for t in ts]) - (WAGON[0] + WAGON[1]) / 2
    return np.interp(POSTS, mid, ts)


def render(G, seed=SEED):
    F = nframes(D)
    out = np.zeros((F, G.N, 3))
    n = G.N
    pdp = G.pd[G.path]
    rng = np.random.default_rng(seed)
    flick = Flicker(rng, n, 0.6, 2.5)
    slow = Flicker(rng, n, 0.1, 0.5)
    hay_grain = 0.75 + 0.25 * np.sin(pdp * 0.9) * np.sin(pdp * 0.23)
    span = (pdp - pdp.min()) / (pdp.max() - pdp.min())
    pulses = engine_pulses()
    pt = np.array([p[0] for p in pulses])
    ps = np.array([p[1] for p in pulses])
    puff_x = np.array([tractor(t)[0] - 6 * tractor(t)[1] for t in pt])
    specks = {tb: (rng.uniform(0, 1, 18), rng.choice([-1, 1], 18) * rng.uniform(90, 420, 18)) for tb, _ in BUMPS}
    lt = lantern_times()
    fly_x = rng.uniform(500, 2480, 40)
    fly_f = rng.uniform(0.4, 0.9, 40)
    fly_p = rng.uniform(0, 1, 40)
    pop_t = POP0 + 0.5 * np.arange(len(PUMPKINS))
    patch_t = T_STOP + 0.25 + 0.2 * np.arange(len(PATCH))

    def g(c, w):
        return np.exp(-((pdp - c) / w) ** 2)

    def pumpkin(c, level, t, k):
        kb = int(t / BEAT)                      # odd pumpkins glow up on 1 and 3, even ones on 2 and 4
        f = 0.7 + 0.55 * (kb % 2 == k % 2) * np.exp(-(t - kb * BEAT) / 0.15)
        return light(PUMPKIN, level * f * (0.8 * g(c, 13) + 0.25 * g(c, 30)))

    for f in range(F):
        t = f * DT
        buf = np.zeros((n, 3))
        x, dr, vis = tractor(t)
        back = -dr

        # ---- the sky: sunset sliding to violet and night; brighter toward the sunset at the left early on ----
        sky = keys(t, [(0, SUNSET), (7, lerp(SUNSET, DUSK, 0.8)), (14, DUSK), (40, lerp(DUSK, NIGHT, 0.6)),
                       (56, NIGHT)])
        lvl = keys(t, [(0, 0.0), (1.0, 0.4), (7, 0.34), (20, 0.3), (56, 0.28), (86, 0.3), (90, 0.0)])
        tilt = 1 + keys(t, [(0, 0.6), (14, 0.0)]) * (1 - span)
        buf += light(sky, lvl * tilt * (1 + 0.1 * slow(t)))
        # a harvest-amber glow off the field along the front runs, once the pumpkins are lit
        field = ((pdp > 492) & (pdp < 1310) | (pdp > 1660)) * smoothstep(2, 7, t) * keys(t, [(0, 1), (87, 1), (90, 0)])
        buf += light(PUMPKIN, 0.16 * field * (1 + 0.15 * slow(t)))

        # ---- the field: pumpkins and corn ----
        fade = keys(t, [(0, 1), (87, 1), (90, 0)])
        warm = keys(t, [(T_GO3, 1.0), (T_HOME, 1.35)])
        for k, (c, tp) in enumerate(zip(PUMPKINS, pop_t)):
            u = t - tp
            if u > 0:
                buf += pumpkin(c, fade * warm * smoothstep(0, 0.06, u) * (1 + 1.2 * np.exp(-u / 0.25)), t, k)
        # the corn: rows of stalks along the field that sway a step on every beat of the hoedown, with a gust running
        # through them each bar in the way the tractor is going; in the barn dance the wings trade steps, Left on 1
        # and 3, Right on 2 and 4; while it revs the rows crowd tight and shiver
        kb = int(t / BEAT)
        ph = (t - kb * BEAT) / BEAT
        beat_acc = np.exp(-ph * BEAT / 0.12) * (1.0 if kb % 4 == 0 else 0.6)
        rev = smoothstep(T_REV, T_GO2, t) * (t < T_GO2 + 0.5)
        lam = 64 - 24 * rev
        dance = T_STOP <= t < T_GO2
        step = smoothstep(0, 0.35, ph)
        if dance:
            lw = (kb % 2 == 0)
            sl = (kb // 2 + (step if lw else 1)) * lam / 2
            sr = -(kb // 2 + (step if not lw else 0)) * lam / 2
            sway = np.where(pdp < 1300, sl, sr)
        else:
            sway = 12 * np.cos(np.pi * (kb + step)) + 3 * rev * np.sin(2 * np.pi * 9 * t)
        rows = np.clip(2.5 * np.cos(2 * np.pi * (pdp + sway) / lam), 0, 1)
        gust = 0.0
        if vis and (T_GO1 <= t < T_STOP or T_GO2 <= t < T_GONE or T_GO3 <= t < T_HOME):
            u = (t % BAR)
            gust = np.exp(-((pdp - (x + dr * (60 + 550 * u))) / 170) ** 2) * np.exp(-u / 1.5)
        grow = smoothstep(2.0, 6.0, t)
        patch_on = smoothstep(T_STOP - 0.5, T_STOP, t) * (1 - smoothstep(T_GO2 + 2, T_GO2 + 6, t))
        cornfield = np.where((pdp > 1310) & (pdp < 1660), 1 - patch_on, np.where(pdp < 492, 0.55, 1.0)) * grow * fade
        side_beat = 1.0
        if dance:
            side_beat = np.where((pdp < 1300) == (kb % 2 == 0), 1.0 + 1.2 * np.exp(-ph * BEAT / 0.15), 0.8)
        lvl_c = (0.4 + 0.25 * beat_acc + 0.25 * rev) * side_beat + 0.75 * gust
        buf += light(CORN, cornfield * rows * lvl_c)
        buf += light(VINE, 0.3 * cornfield * (1 - rows))
        buf += light(HAY, 0.45 * gust * cornfield)
        if dance:                               # keep the wings warm while the porch has the stage
            wings = ((pdp < 892) | (pdp > 2036)) * smoothstep(T_STOP, T_STOP + 1, t)
            buf += light(GOLD, 0.14 * wings)

        # the patch: a vine bed and eight pumpkins that pop up at the stop and hop into the wagon
        if t >= T_STOP:
            patch = ((pdp > 1500) & (pdp < 2030)) * smoothstep(T_STOP, T_STOP + 0.6, t) * (1 - smoothstep(42, 46, t))
            buf += light(VINE, 0.2 * patch)
        loaded = 0
        for k, (c, tp, th) in enumerate(zip(PATCH, patch_t, HOPS)):
            if t < tp:
                continue
            if t < th:
                buf += pumpkin(c, smoothstep(0, 0.06, t - tp) * (1 + np.exp(-(t - tp) / 0.25)), t, k)
            elif t < th + HOP_T:
                u = (t - th) / HOP_T
                slot = X_PATCH + back * (WAGON[0] + (WAGON[1] - WAGON[0]) * (k + 0.5) / 8)
                p = lerp(c, slot, smoothstep(0, 1, u))
                buf += light(PUMPKIN, (0.7 + 0.5 * np.sin(np.pi * u)) * g(p, 12) + 0.35 * np.sin(np.pi * u) * g(p, 60))
                buf += light(CORN, 0.4 * np.sin(np.pi * u) * g(p + (c - slot) * 0.08, 14))
            else:
                loaded += 1
                ul = t - th - HOP_T                    # landing: a burst of gold across the porch
                if ul < 0.6:
                    buf += light(GOLD, 0.55 * np.exp(-ul / 0.2) * g(X_PATCH + 80, 300))

        # ---- the tractor and its wagon ----
        if vis:
            run_glow = 0.4 * g(x + back * 80, 380)
            buf += light(HAY, run_glow)
            # headlight beam ahead
            if t >= T_COUGH[2] + 0.5:
                s = (pdp - x) * dr
                hl = keys(t, [(9.5, 0.0), (9.6, 1.0), (T_REV, 1.0), (T_REV + 1, 1.25), (T_GO2 + 2, 1.0)])
                buf += light(HEAD, hl * (0.65 * np.exp(-np.clip(s, 0, None) / 170) * (s > 0) + 0.9 * g(x + dr * 9, 3)))
            buf += light(TRACTOR, 0.95 * np.clip((14 - np.abs(pdp - x)) / 2, 0, 1) + 0.3 * g(x, 30))
            lo, hi = sorted((x + back * WAGON[0], x + back * WAGON[1]))
            inside = np.clip((pdp - lo) / 2 + 0.5, 0, 1) * np.clip((hi - pdp) / 2 + 0.5, 0, 1)
            jolt = 0.0
            for tb, size in BUMPS:
                u = t - tb
                if 0 <= u < 0.6:
                    jolt += size * np.exp(-u / 0.14)
            bounce = 0.62 * hay_grain * (1 + 0.15 * flick(t)) + 0.4 * jolt
            buf += light(HAY, inside * bounce)
            buf += light(RAIL, 0.7 * (g(lo, 3) + g(hi, 3)))
            buf += light(RAIL, 0.35 * np.clip((WAGON[0] - 2 - np.abs(pdp - x - back * WAGON[0] / 2)) / 2, 0, 1)
                         * (np.abs(pdp - x) > 14))             # the hitch
            # the load: pumpkins riding in the wagon
            w0 = x + back * WAGON[0]
            for k in range(loaded):
                buf += light(PUMPKIN, 0.55 * g(w0 + back * (WAGON[1] - WAGON[0]) * (k + 0.5) / 8, 4.5))
            # the way home: two lanterns swinging on the wagon
            if t >= T_GO3 - 1:
                for k, off in enumerate((50.0, 112.0)):
                    sw = 5 * np.sin(2 * np.pi * 1.1 * t + k * 1.3) * (1 + 2 * jolt)
                    c = x + back * off + sw
                    buf += light(LANTERN, 1.0 * g(c, 5) + 0.4 * g(c, 40))

        # exhaust puffs: one per putt, left where the stack was, growing and fading
        for i in np.nonzero((t - pt >= 0) & (t - pt < 0.9))[0]:
            u = t - pt[i]
            w = 4 + 14 * u
            buf += light(SMOKE, 0.38 * ps[i] * np.exp(-u / 0.28) * g(puff_x[i] + 10 * u * (-tractor(pt[i])[1]), w))

        # bumps: hay flies off the wagon both ways and the run jumps
        for tb, size in BUMPS:
            u = t - tb
            if 0 <= u < 2.6:
                xb, db, _ = tractor(tb)
                lo, hi = sorted((xb - db * WAGON[0], xb - db * WAGON[1]))
                fr, vel = specks[tb]
                p0 = lo + fr * (hi - lo)
                far = 5.0 if size > 1.5 else 1.0            # the big one throws hay to both ends of the roof
                for p, v in zip(p0, vel):
                    pp = p + v * size ** 0.5 * 0.3 * far * (1 - np.exp(-u / (0.3 * far ** 0.5)))
                    buf += light(HAY, 0.85 * np.exp(-u / (0.45 * far ** 0.5)) * g(pp, 4))
                for sgn in (-1, 1):                          # the jolt runs the length of the house
                    buf += light(GOLD, 0.55 * min(size, 1.5) * np.exp(-u / 0.9) * g((lo + hi) / 2 + sgn * 950 * u, 60))
                buf += light(GOLD, 0.6 * min(size, 1.4) * np.exp(-u / 0.3) * g((lo + hi) / 2, 420 * size))
                if size > 1.5:
                    buf += light(GOLD, 0.22 * np.exp(-u / 0.25))

        # the match: a lantern struck at the back of the house before the return
        u = t - T_MATCH
        if 0 <= u < 1.5:
            buf += light(LANTERN, (0.9 * np.exp(-u / 0.15) + 0.3 * smoothstep(0, 0.4, u)) * g(30, 25))
        # lantern posts: each lights as the wagon passes and stays lit
        for k, (c, tl) in enumerate(zip(POSTS, lt)):
            u = t - tl
            if u > 0:
                lv = (0.62 + 0.5 * np.exp(-u / 0.3)) * (1 + 0.1 * flick(t)[min(k * 30, n - 1)]) * fade
                lv *= 0.85 + 0.35 * (int(t / BEAT) % 2 == k % 2) * np.exp(-(t % BEAT) / 0.15)   # they swing on the beat
                if t >= T_RUN_HOME:                          # the run home: light chases down the posts after the wagon
                    lv *= 0.7 + 0.9 * np.clip(np.cos(2 * np.pi * (c / 600 - (t - T_RUN_HOME) * 2)), 0, 1) ** 3
                sw = 10 * np.sin(np.pi * t / BEAT + k)
                buf += light(LANTERN, lv * (0.95 * g(c + 0.3 * sw, 5) + 0.4 * g(c + sw, 28) + 0.2 * g(c + sw, 75)))
                if u < 0.8:                                  # each lights with a flare that spreads
                    buf += light(LANTERN, 0.6 * np.exp(-u / 0.3) * (g(c - 300 * u, 25) + g(c + 300 * u, 25)))

        # fireflies blink in the dark while the tractor is out of sight
        ff = smoothstep(T_GONE - 1, T_GONE + 0.5, t) * (1 - smoothstep(T_GO3 + 1, T_GO3 + 4, t))
        if ff > 0:
            blink = np.clip(np.sin(2 * np.pi * (fly_f * t + fly_p)), 0, 1) ** 12
            buf += light(FIREFLY, 0.9 * ff * (blink[:, None] * np.exp(-((pdp[None] - fly_x[:, None]) / 6) ** 2)).sum(0))

        # home: the wagon leaves off the end of Right and a flash races back the whole length of the roof
        u = t - T_HOME
        if u >= 0:
            head = 2520 - 1000 * u
            buf += light(lerp(GOLD, HEAD, 0.5), 1.0 * g(head, 60) * (head > -100))
            buf += light(GOLD, 0.3 * np.clip((pdp - head) / 300, 0, 1) * (1 + 0.5 * np.exp(-((t - T_HOME) % BEAT) / 0.12)
                                                                         * (u > 2.5)))

        # home: a warm swell over the whole roof on the last chord
        buf += light(GOLD, 0.26 * keys(t, [(T_HOME - 0.2, 0), (T_HOME, 1), (T_HOME + 1.5, 0.75), (89.5, 0)]))
        out[f][G.path] = buf
    return out


# ---------------------------------------------------------------- music ----------------------------------------------
# A hoedown in G, 120 bpm, on the lights' own grid. Dusk is a slow fiddle air over harp and cello with crickets and
# a marimba note for each pumpkin that lights. The tractor coughs and catches, and from then on every putt of its
# engine (the same pulses that puff the smoke) chugs where the tractor is on the house. The ride is fiddle and banjo
# (a plucked-string model rolling the chords) over a walking pizz bass and a brushy chuck; each bump is a thump, a
# shaker of hay and a slide whistle. At the patch the band plays the B tune with claps while the corn dances, and each
# pumpkin hops into the wagon on a slide whistle and a xylophone note climbing the scale. After a quiet moment and a
# struck match, the lantern-lit return takes the tune at a lope with a glockenspiel ping for every lantern,
# then everyone piles back in for the run home and a big G chord as the house glows gold, a harp running down the
# roof with the flash.

E8 = BEAT / 2
CH = {'G': (55, 59, 62), 'C': (55, 60, 64), 'D': (54, 57, 62), 'Em': (55, 59, 64), 'D7': (54, 57, 60)}
ROOT = {'G': (43, 50), 'C': (48, 43), 'D': (50, 45), 'Em': (40, 47), 'D7': (50, 45)}
A_TUNE = ['G4 B4 D5 B4 G4 B4 D5 E5', 'D5 B4 G4 B4 A4 G4 E4 D4', 'E4 G4 C5 E5 D5 C5 B4 A4',
          'B4 A4 G4 A4 B4 A4 F#4 D4']
A_END = ['C5 E5 G5 E5 D5 B4 G4 B4', 'A4 F#4 D4 F#4 G4 - G4 .']
B_TUNE = ['E5 - E5 D5 C5 D5 E5 G5', 'D5 - D5 B4 G4 A4 B4 D5', 'C5 B4 A4 B4 C5 D5 E5 F#5',
          'G5 F#5 G5 D5 B4 G4 G4 .']
A_CH = ['G', 'G', 'G', 'G', 'C', 'C', 'D', 'D']
AEND_CH = ['C', 'G', 'D', 'G']
B_CH = ['C', 'C', 'G', 'G', 'D', 'D', 'G', 'G']
DUSK_AIR = [(0, 'D5', 4), (4, 'B4', 2), (6, 'G4', 2), (8, 'C5', 4), (12, 'E5', 2), (14, 'D5', 2), (16, 'B4', 4),
            (20, 'G4', 2), (22, 'A4', 2), (24, 'B4', 4), (28, 'A4', 4)]                 # (eighth, note, eighths)
SCALE = [55, 57, 59, 60, 62, 64, 66, 67, 69, 71, 72, 74, 76, 78, 79]


def score(M, G):
    from pixelhome.audio import SR, note, slide, whoosh
    n = note
    fid = M.sampler('Strings/Solo Violin/Arco Vib/*_f.wav', tune=-12)
    fidp = M.sampler('Strings/Solo Violin/Arco Vib/*_p.wav', tune=-12)
    clar = M.sampler('Woodwinds/Clarinet/stac/*.wav', tune=-12)
    clarl = M.sampler('Woodwinds/Clarinet/susLong/*.wav', tune=-12)
    horn = M.sampler('Brass/F Horn/sus/*.wav', tune=-12)
    bass = M.sampler('Strings/Solo Contrabass/Pizz/*.wav', tune=-12)
    cello = M.sampler('Strings/Cello Section/susvib/*.wav', tune=-12)
    harp = M.sampler('Strings/Harp/*.wav')
    mar = M.sampler('Percussion/Marimba/*.wav', tune=-12)
    xylo = M.sampler('Percussion/Xylo/*.wav', tune=-12)
    glock = M.sampler('Percussion/Glock/*.wav', tune=-12)
    snare = M.hits('Percussion/Snare2-HitNS_v1*.wav')
    tamb = M.hits('Percussion/Tamb1-Hit*.wav')
    clave = M.hits('Percussion/Claves1_Hit*.wav')
    maraca = M.hits('VSCO 1 Percussion/varWood/maraca[0-9].wav')
    shake = M.hits('VSCO 1 Percussion/varWood/maraca_shake.wav')
    log = M.hits('Percussion/LogDrumLo*.wav')
    bd = M.hits('Percussion/BDrumNewhit_v[4-7]*.wav')
    timp = M.hits('Percussion/Timpani/Timpani1_Hit*.wav')
    crash = M.hits('Percussion/cymbal-crash1_mf*.wav')
    tri = M.hits('Percussion/Triangle3-Hit*.wav')

    for name, gain, rev in (('fiddle', 0.34, 0.2), ('banjo', 0.5, 0.12), ('wind', 0.26, 0.2), ('bass', 0.5, 0.06),
                            ('harp', 0.28, 0.3), ('strings', 0.2, 0.3), ('mallet', 0.32, 0.2), ('perc', 0.42, 0.1),
                            ('drums', 0.5, 0.15), ('engine', 0.3, 0.08), ('fx', 0.2, 0.2), ('night', 1.6, 0.35)):
        M.bus(name, gain=gain * 0.8, reverb=rev)
    M.fader('engine', [(9, 0), (10, 0), (23.5, 0), (24.5, -5), (36, -5), (36.5, 0), (56, 0), (59, -12),
                       (60, -6), (75, -6), (76, -2)])

    order = np.argsort(G.pd)
    xs, ds = G.pos[order, 0], G.pd[order]
    x0, x1 = xs.min(), xs.max()

    def pan_at(d):
        return float(0.85 * (2 * (np.interp(d, ds, xs) - x0) / (x1 - x0) - 1))

    def pan_tr(t):
        return pan_at(tractor(t)[0])

    # ---- sounds made here ----
    banjo_cache = {}

    def banjo(m, vel):
        """A plucked string (Karplus-Strong) picked near the bridge: bright, short, a little twangy."""
        if m not in banjo_cache:
            f0 = 440 * 2 ** ((m - 69) / 12)
            P = int(round(SR / f0))
            N = int(0.7 * SR)
            r = np.random.default_rng(m)
            y = np.zeros(N + P + 1)
            y[1:P + 1] = r.uniform(-1, 1, P)
            dec = np.exp(-1 / (0.28 * f0))
            for i in range(P + 1, N + P + 1, P):
                j = min(i + P, N + P + 1)
                y[i:j] = dec * 0.5 * (y[i - P:j - P] + y[i - P - 1:j - P - 1])
            y = y[1:N + 1]
            y = y - 0.7 * np.concatenate([np.zeros(P // 6), y[:-(P // 6)]])     # pick position
            y *= np.clip((N - np.arange(N)) / (0.05 * SR), 0, 1)
            y /= np.abs(y).max() + 1e-9
            banjo_cache[m] = np.vstack([y, y])
        return banjo_cache[m] * (vel / 127) ** 1.5

    tt = np.arange(int(0.11 * SR)) / SR
    pr = np.random.default_rng(5)

    def putt(s):
        lp = np.convolve(pr.normal(0, 1, len(tt)), np.ones(30) / 30, 'same')
        y = np.sin(2 * np.pi * (52 + 8 * s) * tt) * np.exp(-tt / 0.035) + 1.4 * lp * np.exp(-tt / 0.018)
        return np.vstack([y, y]) * 0.5 * s

    def chirp():
        k = np.arange(int(0.16 * SR)) / SR
        env = sum(np.exp(-((k - 0.02 - 0.045 * i) / 0.008) ** 2) for i in range(3))
        y = 0.035 * env * np.sin(2 * np.pi * 3600 * k)
        return np.vstack([y, y])

    def parse(bars):
        notes, i = [], 0
        for bar in bars:
            for tok in bar.split():
                if tok == '-':
                    notes[-1][2] += 1
                elif tok != '.':
                    notes.append([i, n(tok), 1])
                i += 1
        return notes

    def fiddle(t0, bars, vel=96, inst=None, gain=1.0, pan=0.05, lope=False):
        for i, m, ln in parse(bars):
            if lope and i % 2:
                continue
            ln = 2 if lope else ln
            M.add('fiddle', (inst or fid).play(m, vel, dur=ln * E8 * 0.92, release=0.07), t0 + i * E8, gain, pan)

    def harmony(t0, bars, vel=70):           # clarinet a third under the fiddle, on the beats
        for i, m, ln in parse(bars):
            if i % 2 == 0:
                low = [k for k in range(m - 1, m - 6, -1) if k % 12 in {7, 9, 11, 0, 2, 4, 6}][1]
                M.add('wind', clar.play(low, vel), t0 + i * E8, 0.8, -0.2)

    def band(t0, chords, vel=90, banj=True, chuck=True, roll_vel=None):
        """Bass on 1 and 3, chuck on 2 and 4, banjo rolling sixteenths; chords by half bar."""
        for h, c in enumerate(chords):
            t = t0 + h * BAR / 2
            M.add('bass', bass.play(ROOT[c][h % 2], vel), t, 1.0, -0.1)
            M.add('bass', bass.play(ROOT[c][(h + 1) % 2], vel - 15), t + BEAT, 0.7, -0.1)
            if chuck:
                M.add('perc', snare.play(70), t + BEAT, 0.6, 0.1)
            if banj:
                lo, mid, hi = CH[c]
                pat = [lo, mid, 67, hi, mid, 67, hi, lo]
                for k, m in enumerate(pat):
                    v = (roll_vel or vel) - 12 * (k % 2)
                    M.add('banjo', banjo(m, v), t + k * E8 / 2, 1.0, 0.3 - 0.1 * (k % 3))

    # ---- 0-8: dusk. A slow air on the fiddle, crickets, a marimba note for each pumpkin that lights ----
    for b, c in enumerate(['G', 'C', 'G', 'D']):
        M.add('strings', cello.play(ROOT[c][0], 55, dur=BAR, release=0.6), b * BAR, 0.9)
        for i in range(8):
            M.add('harp', harp.play(CH[c][i % 3] + 12 * (i // 3 % 2) - 12, 58), b * BAR + i * E8, 0.7, -0.2 + 0.05 * i)
    for i, m, ln in DUSK_AIR:
        M.add('fiddle', fidp.play(n(m), 70, dur=ln * E8 * 0.95, release=0.4), i * E8, 1.8, 0.0)
    pent = [62, 64, 67, 69, 71, 74, 76, 79]
    for k, c in enumerate(PUMPKINS):
        M.add('mallet', mar.play(pent[k % 8], 85), POP0 + 0.5 * k, 1.0, pan_at(c))
    cr = np.random.default_rng(3)
    for t in np.concatenate([np.arange(0.5, 9, 0.9), np.arange(56.5, 60.5, 0.7)]):
        M.add('night', chirp(), t + cr.uniform(0, 0.3), cr.uniform(0.5, 1.0), cr.uniform(-0.8, 0.8))

    # ---- the engine: every putt where the tractor is ----
    for k, (tp, s) in enumerate(engine_pulses()):
        x, _, vis = tractor(tp)
        p = pan_at(np.clip(x, 0, G.length))
        cough = tp < 9.4
        M.add('engine', putt(s * (1.6 if cough else 1.0) * (0.85 + 0.3 * (k % 2 == 0))), tp, 1.0, p)
        if cough:
            M.add('engine', whoosh(0.25, 900, 300, 0.3, seed=k), tp + 0.04, 0.8, p)
    M.add('fx', slide(0.0, 0.4, 300, 700, 0.5, 0.4), 9.5, 0.7, pan_tr(9.5))       # it catches
    M.add('fiddle', fid.play(n('D4'), 90, dur=0.45, release=0.05), 9.5, 0.9)       # the fiddle kicks off
    M.add('fiddle', fid.play(n('G4'), 100, dur=0.2, release=0.05), 9.75, 0.9)

    # ---- 10-24: the ride out ----
    band(T_GO1, ['G', 'G'] + A_CH + AEND_CH, 92)
    fiddle(T_GO1 + BAR, A_TUNE + A_END)

    # ---- the bumps ----
    for tb, size in BUMPS:
        p = pan_at(np.clip(tractor(tb)[0] - tractor(tb)[1] * 80, 0, G.length))
        M.add('drums', bd.play(int(min(127, 95 + 15 * size))), tb, 0.9, p)
        M.add('perc', shake.play(110), tb + 0.03, 0.7 * size, p)
        M.add('perc', maraca.play(100), tb + 0.12, 0.6, p)
        M.add('fx', slide(0.0, 0.18, 500, 1100 + 300 * size, 0.42, 0.5, 0.6), tb, 0.6 * size ** 0.5, p)
        if size > 1.5:
            M.add('drums', crash.play(110), tb, 0.8, p)
            M.add('drums', timp.play(118, pitch=-5), tb, 0.8, p)
            M.add('fx', slide(0.18, 0.7, 1500, 420, 0.75, 0.5), tb + 0.1, 0.8, p)

    # ---- 24: whoa, the patch ----
    ps = pan_at(X_PATCH)
    M.add('fx', slide(0.0, 0.6, 1100, 380, 0.7, 0.4), T_STOP - 0.6, 0.8, ps)
    M.add('drums', timp.play(100, pitch=-5), T_STOP, 0.6, ps)
    for i, m in enumerate((43, 55, 59, 62, 67)):
        M.add('banjo', banjo(m, 110), T_STOP + 0.02 * i, 1.0, ps)
    for k, c in enumerate(PATCH):
        M.add('mallet', mar.play(pent[k % 8] - 12 + 12 * (k // 4), 90), T_STOP + 0.25 + 0.2 * k, 0.9, pan_at(c))

    # ---- 24-40: the barn dance, claps, eight pumpkins hop into the wagon ----
    band(T_STOP, B_CH + B_CH, 90, roll_vel=72)
    fiddle(T_STOP, B_TUNE + B_TUNE)
    harmony(T_STOP + 4 * BAR, B_TUNE)
    for b in range(8):
        for k in (1, 3):
            M.add('perc', clave.play(105), T_STOP + b * BAR + k * BEAT, 0.8, -0.45)
            M.add('perc', tamb.play(90), T_STOP + b * BAR + k * BEAT, 0.6, 0.45)
    for k, (c, th) in enumerate(zip(PATCH, HOPS)):
        slot = X_PATCH + (WAGON[0] + (WAGON[1] - WAGON[0]) * (k + 0.5) / 8)
        M.add('fx', slide(0.0, 0.3, 500 + 40 * k, 1300 + 60 * k, 0.4, 0.4, 0.6), th, 0.7, pan_at(c))
        M.add('mallet', xylo.play(SCALE[k + 2], 105), th + HOP_T * 0.5, 0.9, pan_at((c + slot) / 2))
        M.add('perc', log.play(115), th + HOP_T, 1.0, pan_at(slot))
    for k in range(8):                         # the rev
        M.add('fx', slide(0.0, 0.5, 200 + 60 * k, 260 + 90 * k, 0.5, 0.15), T_REV + 0.5 * k, 0.6, ps)

    # ---- 40-56: the ride on, with clarinet harmony and tambourine ----
    band(T_GO2, A_CH + A_CH[:4] + AEND_CH, 98)
    fiddle(T_GO2, A_TUNE + A_TUNE[:2] + A_END, 104)
    harmony(T_GO2 + 4 * BAR, A_TUNE[:2] + A_END, 78)
    for k in range(64):
        M.add('perc', tamb.play(60 + 25 * (k % 2 == 0)), T_GO2 + k * E8, 0.5, 0.35)

    # ---- 56-60: gone into the dark; a struck match ----
    for m, v in ((43, 60), (50, 55), (59, 45)):
        M.add('strings', cello.play(m, v, dur=3.5, release=1.0), T_GONE, 0.8)
    M.add('harp', harp.play(n('G3'), 60), T_GONE, 0.8)
    M.add('fx', whoosh(0.3, 1500, 6000, 0.5, seed=9), T_MATCH - 0.1, 1.0, pan_at(30))
    M.add('mallet', glock.play(n('D6'), 70), T_MATCH + 0.15, 0.6, pan_at(30))
    M.add('wind', clarl.play(n('D4'), 60, dur=1.5, release=0.5), T_MATCH + 0.2, 0.8)

    # ---- 60-76: the lantern-lit return at an easy lope; a glock for every lantern ----
    band(T_GO3, A_CH + AEND_CH + ['G', 'G', 'D', 'D'], 90, roll_vel=72)
    fiddle(T_GO3, A_TUNE + A_END, 96, lope=True)
    fiddle(T_GO3 + 6 * BAR, ['G4 - - - B4 - D5 -', 'D5 - - - B4 - G4 -'], 80, inst=fidp)
    lt = lantern_times()
    for k, (c, tl) in enumerate(zip(POSTS, lt)):
        M.add('mallet', glock.play(SCALE[k % len(SCALE)], 78), tl, 0.7, pan_at(c))
        M.add('harp', harp.play(SCALE[k % len(SCALE)] - 12, 70), tl, 0.6, pan_at(c))

    # ---- 76-84: everyone back in for the run home ----
    band(T_GO3 + 8 * BAR, B_CH, 100)
    fiddle(T_GO3 + 8 * BAR, B_TUNE, 108)
    harmony(T_GO3 + 8 * BAR, B_TUNE, 82)
    for k in range(32):
        M.add('perc', tamb.play(60 + 25 * (k % 2 == 0)), T_GO3 + 8 * BAR + k * E8, 0.5, 0.35)

    # ---- 84-86: a run up; 86: the big G chord as the house glows ----
    t0 = T_HOME - BAR
    for i, m in enumerate(('G4', 'A4', 'B4', 'C5', 'D5', 'E5', 'F#5', 'G5')):
        M.add('fiddle', fid.play(n(m), 100 + 2 * i, dur=E8 * 0.9, release=0.05), t0 + i * E8, 1.0)
    for i, c in enumerate(('G', 'D', 'G')):
        M.add('bass', bass.play(ROOT[c][0], 110), t0 + i * BEAT, 1.0)
        M.add('drums', bd.play(100), t0 + i * BEAT, 0.6)
        for m in CH[c]:
            M.add('banjo', banjo(m, 105), t0 + i * BEAT, 0.8, 0.2)
    hold = D - T_HOME - 0.8
    M.add('fiddle', fid.play(n('G5'), 110, dur=hold, release=1.2), T_HOME, 1.0)
    M.add('fiddle', fid.play(n('B4'), 95, dur=hold, release=1.2), T_HOME, 0.6, -0.2)
    for m in (n('G3'), n('D4'), n('B4')):
        M.add('wind', horn.play(m, 100, dur=hold, release=1.2), T_HOME, 0.9)
    for m in (n('G2'), n('D3')):
        M.add('strings', cello.play(m, 100, dur=hold, release=1.2), T_HOME, 1.0)
    M.add('bass', bass.play(n('G2'), 120), T_HOME, 1.2)
    M.add('drums', timp.play(120, pitch=-5), T_HOME, 0.9)
    M.add('drums', crash.play(115), T_HOME, 0.8)
    M.add('drums', bd.play(120), T_HOME, 0.9)
    M.add('perc', tri.play(100), T_HOME, 0.6, 0.3)
    for k in range(16):                        # the banjo rolls the G chord out under the hold
        M.add('banjo', banjo([55, 59, 62, 67][k % 4], 100 - 4 * k), T_HOME + k * E8 / 2, 1.0, 0.2)
    for i, m in enumerate(('D5', 'B4', 'G4', 'D4', 'B3', 'G3', 'D3', 'G2')):   # the flash racing back along the roof
        M.add('harp', harp.play(n(m), 85), T_HOME + 0.3 * i, 0.9, pan_at(2520 - 1000 * 0.3 * i))
    ts = np.linspace(T_HOME, T_HOME + 2.5, 20)
    w = whoosh(2.5, 2500, 400, 0.4, seed=12)
    a = (np.clip(np.interp(T_HOME + np.arange(w.shape[1]) / SR, ts, [pan_at(2520 - 1000 * (t - T_HOME)) for t in ts]),
                 -1, 1) + 1) * np.pi / 4
    M.add('fx', w * np.vstack([np.cos(a), np.sin(a)]) * np.sqrt(2), T_HOME, 0.7)
