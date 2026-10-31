"""Cranberry Bog: Harvest morning, to a work song in 6/8 (a bar is 1.2 s). The roof is a dry bog: green vines
with a breeze running through them and red berries that sing along with the fiddle, the Left side on the call
and the Right side on the answer. Three knocks on the sluice gate at the middle of the Porch Front, a held
breath, and it bursts: two white foam fronts race out to both free ends, bounce back, and the flooded bog
sloshes, crests rolling out from the sluice every bar and back off the ends, crossing each other, quicker as
the flood rises. Two beaters start at the porch and churn out, a block of whirling white paddles each, heaving
forward one at a time, left on the first beat and right on the second, knocking berries loose as they go (each
pops up bright red). They spin at the ends, then race back, two heaves a bar, stop nose to nose at the porch,
tremble in a held beat, and slam together: the berries burst out of the water and fly to both ends of the house
behind a red wave, and the bog is a sea of red. Swells roll through it on the beat, out and back, then one big
swell sweeps the whole roof every bar. Two yellow booms close in, one popping up at the front-left corner and
one coming in off the free end of Right: a heave every bar and a slip back on the off-beat, the crop between
them tightening into closer, brighter stripes, the water left behind rippling blue. Nearly there, the crop
bulges and shoves the booms back out; a held beat; one last heave snaps them round the porch, and the harvest
goes off: a crimson flash at the porch and a red and gold wave that rolls out to both ends, the whole house
dancing in red and gold stripes to the last chord."""
import numpy as np
from pixelhome.fx import DT, hexc, light, keys, smoothstep, lerp, Flicker, nframes

CODE = 'TG16'
TITLE = 'Cranberry Bog'
KIND = 'show'
DESCRIPTION = ('Harvest at the cranberry bog. The sluice bursts and water sloshes the length of the house, two beaters '
               'collide and burst the berries free, and yellow booms heave a sea of red into the porch.')
VOICEOVER = "Open the sluice, crash the beaters, and heave in a sea of cranberries."

VINE = hexc('#0c5000')
LEAF = hexc('#40c010')
BERRY = hexc('#ff0610')
CRIMSON = hexc('#e00006')
WATER = hexc('#0028ff')
FOAM = hexc('#b8ecff')
CHURN = hexc('#e8f4ff')
BOOM = hexc('#ffc400')
GOLD = hexc('#ffa000')
WHITE = hexc('#ffffff')

D = 90.0
SEED = 16
BAR = 1.2                                  # 6/8, a dotted quarter at 100
BEAT = BAR / 2
E8 = BAR / 6
L_TOTAL = 2512.0
SLUICE = 1486.0
LCORNER = 492.0                            # Side|Left: the front-left corner of the house


def bt(b):
    return b * BAR


T_KNOCK = [bt(6.0), bt(6.5), bt(7.0)]
T_SLUICE = bt(8)                           # 9.6
T_BEAT0, T_BEAT_TURN, T_BEAT_BACK, T_HOLD, T_COL = bt(20), bt(28), bt(30), bt(36), bt(37)
T_SEA, T_SWEEP = bt(38), bt(50)
T_BOOM, T_BULGE, T_STILL, T_SNAP = bt(54), bt(66), bt(67), bt(68)
T_CHORD = bt(72)
FLOOD_V = 520.0
CREST_V = 420.0
NB = 240


def stepped(t, t0, period, n, p0, p1, phase=0.0):
    """A heave every period: each step lunges in the first part of its period and holds."""
    u = (t - t0 - phase) / period
    if u <= 0:
        return p0
    k = min(int(u), n)
    s = k + (float(smoothstep(0.0, 0.4, u - k)) if k < n else 0.0)
    return p0 + (p1 - p0) * s / n


def beater(k, t):
    """The two beaters' positions: out in heaves (left on the beat, right on the half bar), a spin at the ends,
    back two heaves a bar, nose to nose at the porch, then the slam."""
    if k == 0:
        a, b, c, d = 1420.0, 260.0, 1420.0, SLUICE - 6
        ph = 0.0
    else:
        a, b, c, d = 1552.0, 2470.0, 1552.0, SLUICE + 6
        ph = BEAT
    if t < T_BEAT_TURN:
        return stepped(t, T_BEAT0, BAR, 8, a, b, ph)
    if t < T_BEAT_BACK:
        return b
    if t < T_HOLD:
        return stepped(t, T_BEAT_BACK, BEAT, 12, b, c, ph / 2)
    if t < T_COL - 0.12:
        return c + (1 if k else -1) * 3 * np.sin(2 * np.pi * 9 * t)
    return float(lerp(c, d, smoothstep(T_COL - 0.12, T_COL, t)))


def booms(t):
    """The booms: a heave every bar and a slip back on the off-beat; the bulge, the hold, the snap."""
    L0, L1, R0, R1 = LCORNER, 1180.0, L_TOTAL + 30, 1790.0
    if t < T_BOOM:
        return -30.0, R0
    if t < T_BOOM + 0.4:                   # the left boom surfaces at the corner and the Side drains behind it
        return float(lerp(-30.0, L0, smoothstep(T_BOOM, T_BOOM + 0.4, t))), R0
    if t < T_BULGE:
        u = (t - T_BOOM) / BAR
        k = int(u)
        f = u - k
        mv = 1.35 * smoothstep(0.0, 0.3, f) - 0.35 * smoothstep(0.5, 0.8, f)
        s = (k + mv) / 12
        return L0 + (L1 - L0) * s, R0 + (R1 - R0) * s
    if t < T_SNAP:
        b = 140 * smoothstep(T_BULGE, T_BULGE + 0.4, t) * (1 - 0.3 * smoothstep(T_STILL, T_SNAP, t))
        tr = 4 * np.sin(2 * np.pi * 11 * t) * (t >= T_STILL)
        return L1 - b + tr, R1 + b - tr
    s = smoothstep(T_SNAP, T_SNAP + 0.25, t)
    return float(lerp(L1 - 98, 1290.0, s)), float(lerp(R1 + 98, 1682.0, s))


def berries(seed=SEED):
    """Each berry's place, and when a beater knocks it loose (inf: still under at the collision)."""
    rng = np.random.default_rng(seed)
    B = np.sort(rng.uniform(15, L_TOTAL - 15, NB))
    loose = np.full(NB, np.inf)
    for t in np.arange(T_BEAT0, T_COL, DT):
        for k in range(2):
            hit = (np.abs(B - beater(k, t)) < 60) & np.isinf(loose)
            loose[hit] = t
    return B, loose, rng.uniform(0, 2 * np.pi, NB)


def crests(t, emit, d):
    """Crests sent out from the sluice at the emit times, and their reflections off both free ends."""
    out = np.zeros_like(d)
    for te in emit:
        u = t - te
        if u <= 0 or u > 6:
            continue
        r = CREST_V * u
        a = np.exp(-u / 3.0)
        for src in (np.abs(d - SLUICE), d + SLUICE, 2 * L_TOTAL - SLUICE - d):
            out += a * np.exp(-((src - r) / 45) ** 2)
    return out


def render(G, seed=SEED):
    F = nframes(D)
    out = np.zeros((F, G.N, 3))
    n = G.N
    pdp = G.pd[G.path]
    xp = G.pos[G.path, 0]
    rng = np.random.default_rng(seed + 1)
    flick = Flicker(rng, n, 2.0, 6.0)
    slow = Flicker(rng, n, 0.15, 0.5)
    B, loose, phase = berries(seed)
    berry_x = np.interp(B, G.pd[G.path], xp)
    pop = rng.integers(0, 4, NB)
    glint_t = np.sort(rng.uniform(T_SEA, D, 700))
    glint_s = rng.uniform(0, L_TOTAL, 700)
    shard_v = rng.uniform(500, 1700, 60) * np.repeat([-1, 1], 30)
    shard_l = rng.uniform(0.6, 1.4, 60)
    emit = list(np.arange(T_SLUICE + BAR, bt(14), BAR)) + list(np.arange(bt(14), T_BEAT0 + 2, BEAT))
    pf = (pdp > 1313) & (pdp < 1658)

    def g(c, w):
        return np.exp(-((pdp - c) / w) ** 2)

    for f in range(F):
        t = f * DT
        buf = np.zeros((n, 3))
        fade = keys(t, [(0, 0), (1.0, 1), (88.5, 1), (90, 0)])
        bar_ph = (t / BAR) % 1.0
        down = np.exp(-bar_ph / 0.08) + 0.5 * np.exp(-((bar_ph - 0.5) % 1.0) / 0.08)    # 6/8: ONE and four
        d0 = np.abs(pdp - SLUICE)

        # ---- the dry bog: a breeze rippling through the vines, berries singing the call and answer ----
        r = max(0.0, FLOOD_V * (t - T_SLUICE)) if t >= T_SLUICE else -1.0
        dry = np.clip((d0 - r) / 30, 0, 1) if t < T_SLUICE + 4 else np.zeros(n)
        if dry.any():
            breeze = 0.5 + 0.5 * np.sin(2 * np.pi * (pdp / 180 + 0.9 * t))
            hold = 1 - 0.55 * smoothstep(T_KNOCK[2] + 0.2, T_KNOCK[2] + 0.5, t) * (t < T_SLUICE)
            buf += light(VINE, dry * fade * hold * (0.14 + 0.06 * slow(t)))
            buf += light(LEAF, dry * fade * hold * 0.22 * breeze ** 3)
            sing = np.where(berry_x < 0, (t % (2 * 2 * BAR)) < 2 * BAR, (t % (2 * 2 * BAR)) >= 2 * BAR) * (t < bt(6))
            beat_i = int(t / BEAT) % 4
            lvl = 0.3 + 0.5 * sing * (0.6 + 0.4 * down) + 0.35 * (pop == beat_i) * down
            lvl = lvl * hold * np.clip((np.abs(B - SLUICE) - r) / 30, 0, 1)
            buf += light(BERRY, np.clip((lvl[None, :] * np.exp(-((pdp[:, None] - B[None, :]) / 5) ** 2)).sum(1), 0, 1)
                         * fade)
        for i, tk in enumerate(T_KNOCK):                                      # knock, knock, KNOCK
            u = t - tk
            if 0 <= u < 0.6:
                buf += light(WHITE, (0.45 + 0.25 * i) * np.exp(-u / 0.12) * pf)
                buf += light(FOAM, (0.3 + 0.2 * i) * np.exp(-((d0 - 500 * u) / 40) ** 2) * np.exp(-u / 0.2))

        # ---- the flood: two foam fronts out to the ends, then crests sloshing back and forth ----
        water = np.zeros(n)
        if t >= T_SLUICE:
            wet = np.clip((r - d0) / 30, 0, 1)
            water = wet * (0.22 + 0.12 * smoothstep(T_SLUICE, T_SLUICE + 6, t))
            if t < T_SLUICE + 4:
                front = np.exp(-((d0 - r) / 25) ** 2) * (d0 - r < 60)
                buf += light(FOAM, 0.95 * front * fade)
                u = t - T_SLUICE
                buf += light(WHITE, 0.95 * np.exp(-u / 0.25) * g(SLUICE, 90))
                # the fronts hit the ends and bounce
                for end, dist in ((0.0, SLUICE), (L_TOTAL, L_TOTAL - SLUICE)):
                    ub = u - dist / FLOOD_V
                    if 0 <= ub < 1.5:
                        buf += light(WHITE, 0.8 * np.exp(-ub / 0.15) * g(end, 50))
                        rb = FLOOD_V * ub
                        buf += light(FOAM, 0.6 * np.exp(-ub / 0.8) * np.exp(-((np.abs(pdp - end) - rb) / 30) ** 2))
            cr = crests(t, emit, pdp)
            calm = 1 - smoothstep(T_SEA - 2, T_SEA, t)
            buf += light(FOAM, np.clip(0.7 * cr, 0, 0.85) * wet * calm * fade)
            water = water * (1 + 0.6 * np.clip(cr, 0, 1.5)) + 0.04 * down * wet

        # ---- the beaters: whirling white paddles, a churned wake ----
        if T_BEAT0 - 0.5 <= t < T_COL + 0.1:
            on = smoothstep(T_BEAT0 - 0.5, T_BEAT0, t)
            spin = 6.0 if t < T_BEAT_TURN or t >= T_BEAT_BACK else 10.0
            spin = 14.0 if t >= T_HOLD else spin
            for kb in range(2):
                x = beater(kb, t)
                sgn = -1 if kb == 0 else 1
                rel = pdp - x
                block = np.clip((70 - np.abs(rel)) / 8, 0, 1)
                paddles = 0.5 + 0.5 * np.cos(2 * np.pi * (rel / 24 - spin * t * sgn))
                buf += light(CHURN, on * fade * block * (0.25 + 0.7 * paddles ** 2))
                buf += light(WATER, on * 0.4 * g(x, 220))
                wake = np.where(rel * -sgn > 0, np.exp(-np.abs(rel) / 260), 0) * (1 - block)
                buf += light(FOAM, on * 0.22 * wake * (0.5 + 0.5 * flick(t)))
                if T_BEAT_TURN <= t < T_BEAT_BACK:                           # a spin at the end, spraying
                    buf += light(FOAM, 0.5 * (0.5 + 0.5 * np.sin(2 * np.pi * (rel / 40 - 3 * t))) * g(x, 140))
            if t >= T_HOLD:                                                   # nose to nose: a held breath
                water = water * (1 - 0.6 * smoothstep(T_HOLD, T_HOLD + 0.3, t))

        buf += light(WATER, water * fade * (1 - smoothstep(T_SEA, T_SEA + 3, t) * 0.3))

        # ---- the berries knocked loose: each pops up bright, then floats bobbing ----
        if T_BEAT0 <= t < T_COL + 1:
            u = t - loose
            lvl = np.where(u > 0, 0.55 + 0.45 * np.exp(-u / 0.25) + 0.1 * np.sin(3 * t + phase), 0.12)
            lvl = lvl * (1 - 0.5 * smoothstep(T_HOLD, T_HOLD + 0.3, t))
            k = np.exp(-((pdp[:, None] - B[None, :]) / 6) ** 2)
            buf += light(BERRY, np.clip((k * lvl[None, :]).sum(1), 0, 1) * fade)

        # ---- the collision: berries burst out to both ends behind a red wave; the sea of red ----
        if t >= T_COL:
            u = t - T_COL
            fill = np.clip((1250 * u - d0) / 160, 0, 1)
            if u < 2.5:
                buf += light(WHITE, 0.9 * np.exp(-u / 0.2) * g(SLUICE, 140))
                buf += light(BERRY, 0.5 * np.exp(-u / 0.15))                         # the house flashes red
                front = np.exp(-((d0 - 1250 * u) / 60) ** 2)
                buf += light(lerp(BERRY, WHITE, 0.35), 0.9 * front * (u < 2.1))
                ps = SLUICE + shard_v * shard_l * (1 - np.exp(-u / shard_l))
                life = np.exp(-u / (1.2 * shard_l))
                sh = (life[None, :] * np.exp(-((pdp[:, None] - ps[None, :]) / 7) ** 2)).sum(1)
                buf += light(lerp(BERRY, WHITE, 0.5), np.clip(sh, 0, 1))
            L, R = booms(t)
            inside = np.clip((pdp - L) / 6 + 0.5, 0, 1) * np.clip((R - pdp) / 6 + 0.5, 0, 1)
            squeeze = L_TOTAL / max(R - L, 300.0) if t >= T_BOOM else 1.0
            s = (pdp - L) / (R - L) * L_TOTAL if t >= T_BOOM else pdp
            # swells: out from the porch on the beat, back in, then one big swell round the house each bar
            if t < bt(42):
                sw = 0.5 + 0.5 * np.cos(2 * np.pi * (d0 / 260 - t / BEAT))
            elif t < bt(46):
                sw = 0.5 + 0.5 * np.cos(2 * np.pi * (d0 / 260 + t / BEAT))
            elif t < T_SWEEP:
                sw = 0.5 + 0.5 * np.cos(2 * np.pi * (pdp / 300 - (t / BEAT) * np.sign(np.sin(np.pi * t / BAR))))
            elif t < T_BOOM:
                head = ((t - T_SWEEP) / (2 * BAR) % 1.0) * (L_TOTAL + 600) - 300
                if int((t - T_SWEEP) / (2 * BAR)) % 2:
                    head = L_TOTAL - head
                sw = 0.3 + 0.7 * np.exp(-((pdp - head) / 300) ** 2)
            else:                                                             # inside the booms: tightening stripes
                sw = 0.5 + 0.5 * np.cos(2 * np.pi * (s / 210 - 0.6 * t))
            base = 0.26 + 0.1 * down
            if T_SWEEP <= t < T_BOOM:
                base = 0.2 + 0.06 * down
            if t >= T_BOOM:
                base = 0.24 + 0.1 * np.sqrt(squeeze) + 0.1 * down
            lvl = fill * (base + 0.5 * sw ** 2) * inside
            col = lerp(BERRY, CRIMSON, smoothstep(T_BOOM, T_SNAP, t))
            buf += light(col, np.clip(lvl, 0, 1.0) * fade)
            for i in np.nonzero((t - glint_t >= 0) & (t - glint_t < 0.2))[0]:
                ug = t - glint_t[i]
                gp = L + glint_s[i] / squeeze if t >= T_BOOM else glint_s[i]
                buf += light(WHITE, 0.75 * np.exp(-ug / 0.06) * g(gp, 3) * fade * fill[min(int(gp / 5.02), n - 1)])

            # ---- the booms and the water they leave ----
            if t >= T_BOOM - 0.3:
                bon = smoothstep(T_BOOM - 0.3, T_BOOM, t) * fade
                outside = 1 - inside
                u = (t - T_BOOM) / BAR
                heave = np.exp(-(u % 1.0) / 0.12) if t < T_BULGE else 0.0
                rip = 0.5 + 0.5 * np.cos(2 * np.pi * ((np.minimum(np.abs(pdp - L), np.abs(pdp - R))) / 120 - 1.5 * t))
                buf += light(WATER, outside * (0.24 + 0.12 * rip) * fade)
                if t < T_BOOM + 0.6:                                        # pop: the left boom surfaces at the corner
                    buf += light(WHITE, 0.8 * np.exp(-(t - T_BOOM) / 0.15) * g(LCORNER, 40))
                for x in (L, R):
                    buf += light(BOOM, bon * ((0.85 + 0.15 * heave) * g(x, 6) + 0.3 * g(x, 30)))
                    buf += light(WHITE, bon * 0.6 * heave * g(x, 10))
                if T_STILL <= t < T_SNAP:                                   # the held beat: all but the crop dims
                    buf *= 1 - 0.5 * smoothstep(T_STILL, T_STILL + 0.2, t) * outside[:, None]

        # ---- the harvest goes off: crimson flash at the porch, a red and gold wave to both ends ----
        if t >= T_SNAP:
            u = t - T_SNAP
            buf += light(lerp(CRIMSON, WHITE, 0.5), 0.95 * np.exp(-u / 0.3) * g(SLUICE, 220))
            front = 1400 * u
            reached = np.clip((front - d0) / 120, 0, 1)
            if u < 2.5:
                buf += light(GOLD, 0.9 * np.exp(-((d0 - front) / 70) ** 2))
            stripes = 0.5 + 0.5 * np.cos(2 * np.pi * (d0 / 150 - t / BEAT))
            lv = reached * (1 - inside) * keys(t, [(T_SNAP, 1.0), (T_CHORD, 1.0), (88, 0.7), (90, 0.3)])
            buf += light(GOLD, lv * (0.22 + 0.6 * stripes ** 2 + 0.12 * down) * fade)
            buf += light(BERRY, lv * 0.5 * (1 - stripes) ** 2 * fade)
            if t >= T_CHORD:
                buf += light(WHITE, 0.5 * np.exp(-(t - T_CHORD) / 0.25) * reached * 0.6)
        out[f][G.path] = buf
    return np.clip(out, 0, 1)


# ---------------------------------------------------------------- music ----------------------------------------------
# An original work song in D dorian, 6/8 at 100 (a bar is 1.2 s, the lights' bar). A leader calls a line and the crew
# answers, the way a shanty goes. The dry bog is the call on a fiddle over pizzicato, three timpani knocks and a
# held breath. The sluice is a gong, timpani and crash, and the flood runs out both ways as a wash of water that
# follows its fronts, a splash on every crest. The beaters are the crew at full stamp, each heave a chug and a splash
# where it is; the race back doubles the stamps under a climbing tremolo, a bar of silence, and the slam is a crash
# with marimba berries flying out to both sides. The sea of red is the refrain for full band; the booms heave a bar
# at a time (stamp, trombone grunt, creak) and slip on a slide whistle; the bulge is a trombone fall, the held beat
# a timpani roll, and the snap the refrain once more, landing on D major.

CH = {'Dm': (57, 62, 65), 'C': (55, 60, 64), 'F': (57, 60, 65), 'Am': (57, 60, 64), 'G': (55, 59, 62),
      'D': (57, 62, 66), 'Bb': (58, 62, 65)}
ROOT = {'Dm': 38, 'C': 36, 'F': 41, 'Am': 45, 'G': 43, 'D': 38, 'Bb': 34}
CALL_A = ['A4 - A4 D5 - E5', 'F5 - E5 D5 - A4']
RESP_A = ['C5 - C5 E5 - C5', 'G4 - - - - .']
CALL_B = ['A4 - A4 D5 - E5', 'F5 - G5 F5 - D5']
RESP_B = ['E5 - D5 C5 - E5', 'D5 - - - - .']
VERSE_CH = ['Dm', 'Dm', 'C', 'C', 'Dm', 'F', 'C', 'Dm']
REFRAIN = ['F5 - - E5 - D5', 'C5 - D5 E5 - C5', 'D5 - - A4 - -', 'C5 - - D5 - .']
REFRAIN_END = ['F5 - - E5 - D5', 'C5 - D5 E5 - C5', 'D5 - - A4 - -', 'D5 - - F#5 - .']
REFRAIN_CH = ['F', 'C', 'Dm', 'Dm']
PENT = [62, 64, 65, 69, 71, 74, 76, 77, 81]


def score(M, G):
    from pixelhome.audio import SR, note, slide
    n = note
    fid = M.sampler('Strings/Solo Violin/Arco Vib/*_f.wav', tune=-12)
    horn = M.sampler('Brass/F Horn/sus/*.wav', tune=-12)
    tpt = M.sampler('Brass/Trumpet/sus/*.wav', tune=-12)
    bone = M.sampler('Brass/Tenor Trombone/sus/*.wav', tune=-12)
    bstac = M.sampler('Brass/Tenor Trombone/stac/*.wav', tune=-12)
    fall = M.sampler('Brass/OldTrombone/Fall/*.wav', tune=-12)
    tuba = M.sampler('Brass/Tuba/stac/*.wav', tune=-12)
    clar = M.sampler('Woodwinds/Clarinet/stac/*.wav', tune=-12)
    clarl = M.sampler('Woodwinds/Clarinet/susLong/*.wav', tune=-12)
    oboe = M.sampler('Woodwinds/Oboe/Stacc/*.wav', tune=-12)
    bsn = M.sampler('Woodwinds/Bassoon/stac/*.wav', tune=-12)
    cello = M.sampler('Strings/Cello Section/susvib/*.wav', tune=-12)
    vsus = M.sampler('Strings/Violin Section/susVib/*.wav', tune=-12)
    vpz = M.sampler('Strings/Violin Section/Pizz/*.wav', tune=-12)
    trem = M.sampler('Strings/Violin Section/Trem/*.wav', tune=-12)
    cb = M.sampler('Strings/Solo Contrabass/Pizz/*.wav', tune=-12)
    harp = M.sampler('Strings/Harp/*.wav')
    mar = M.sampler('Percussion/Marimba/*.wav', tune=-12)
    glock = M.sampler('Percussion/Glock/*.wav', tune=-12)
    ooh = M.synth('Pads/Ooh')
    bd = M.hits('VSCO 1 Percussion/drums/bass/bdrum_f_*.wav')
    clave = M.hits('Percussion/Claves1_Hit*.wav')
    tamb = M.hits('Percussion/Tamb1-Hit*.wav')
    snare = M.hits('Percussion/Snare2-HitSN*.wav')
    timp = M.hits('Percussion/Timpani/Timpani1_Hit*.wav')
    troll = M.hits('Percussion/Timpani/Rolls/*.wav')
    crash = M.hits('Percussion/cymbal-crash1_ff*.wav')
    bubbles = M.hits('Miscellania Raw/Misc 1/bubbles*.wav')
    creak = M.hits('VSCO 1 Percussion/varWood/guiro_long*.wav')
    ratchet = M.hits('Percussion/Ratchet1-Slow*.wav')
    gong = M.hits('VSCO 1 Percussion/varMetal/Gong/gong_hit_p.wav')
    wood = M.hits('VSCO 1 Percussion/varWood/wood_click_f*.wav')

    for name, gain, rev in (('lead', 0.5, 0.25), ('crew', 0.3, 0.28), ('choir', 0.36, 0.35), ('box', 0.22, 0.15),
                            ('bass', 0.32, 0.08), ('strings', 0.26, 0.3), ('harp', 0.26, 0.35), ('mallet', 0.42, 0.3),
                            ('perc', 0.45, 0.12), ('drums', 0.5, 0.18), ('water', 0.5, 0.25), ('churn', 0.3, 0.1),
                            ('fx', 0.4, 0.15)):
        M.bus(name, gain=gain * 0.46, reverb=rev)
    M.fader('water', [(0, -30), (T_SLUICE - 0.2, -30), (T_SLUICE, 0), (T_SLUICE + 4, -3), (T_BEAT0, -8),
                      (T_COL, -10), (T_SEA + 2, -18), (T_BOOM, -14), (D, -20)])

    order = np.argsort(G.pd)
    xs, ds = G.pos[order, 0], G.pd[order]
    x0, x1 = xs.min(), xs.max()

    def pan_at(d):
        return float(0.85 * (2 * (np.interp(np.clip(d, 0, L_TOTAL), ds, xs) - x0) / (x1 - x0) - 1))

    nr = np.random.default_rng(21)

    def lp_noise(N, k):
        y = np.convolve(nr.normal(0, 1, N + k), np.ones(k) / k, 'valid')[:N]
        return y / (np.abs(y).max() + 1e-9)

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

    def line(t0, bars, inst, bus, vel, gain=1.0, pan=0.0, shift=0):
        for i, m, ln in parse(bars):
            M.add(bus, inst.play(m + shift, vel, dur=ln * E8 * 0.95, release=0.15), t0 + i * E8, gain, pan)

    choir_notes = []

    def answer(t0, bars, vel=100, full=True):
        """The crew answers: trombones and cellos in octaves, the choir singing the tune."""
        for i, m, ln in parse(bars):
            d = ln * E8 * 0.95
            M.add('crew', bone.play(m - 12, vel, dur=d, release=0.15), t0 + i * E8, 0.9, -0.15)
            if full:
                M.add('crew', cello.play(m - 12, vel - 10, dur=d, release=0.15), t0 + i * E8, 0.8, 0.15)
            choir_notes.append((t0 + i * E8, m, 90, d))
            choir_notes.append((t0 + i * E8, m - 12, 80, d))

    def accomp(t0, chords, work=True, box=True, harp_ripple=False, vel=88, double=False):
        for b, c in enumerate(chords):
            t = t0 + b * BAR
            r = ROOT[c]
            M.add('bass', cb.play(r, vel), t, 1.0, -0.1)
            M.add('bass', cb.play(r + 7, vel - 12), t + 3 * E8, 0.8, -0.1)
            M.add('bass', tuba.play(r, vel - 10), t, 0.5)
            if box:
                for e in (1, 2, 4, 5):
                    for m in CH[c]:
                        M.add('box', (clar if e in (2, 5) else oboe).play(m, vel - 24 + 6 * (e in (2, 5))), t + e * E8,
                              0.6, 0.25)
            if work:
                M.add('drums', bd.play(112), t, 1.0, 0.0)
                M.add('drums', bd.play(90), t + 3 * E8, 0.75, 0.0)
                M.add('perc', clave.play(100), t + 3 * E8, 0.8, -0.35)
                M.add('perc', tamb.play(85), t + 2 * E8, 0.5, 0.35)
                M.add('perc', tamb.play(85), t + 5 * E8, 0.5, 0.35)
                if double:
                    for e in (1, 2, 4, 5):
                        M.add('drums', snare.play(70 + 10 * (e % 3 == 2)), t + e * E8, 0.5)
            if harp_ripple:
                for e in range(6):
                    m = CH[c][[0, 1, 2, 1, 2, 0][e]] + (12 if e in (2, 4) else 0)
                    M.add('harp', harp.play(m - 12, 66), t + e * E8, 0.7, -0.4 + 0.16 * e)

    def verse(t0, lead, lead_vel=96, **kw):
        line(t0, CALL_A, lead, 'lead', lead_vel)
        answer(t0 + 2 * BAR, RESP_A)
        line(t0 + 4 * BAR, CALL_B, lead, 'lead', lead_vel)
        answer(t0 + 6 * BAR, RESP_B)
        accomp(t0, VERSE_CH, **kw)

    # ---- 0-9.6: the dry bog: the fiddle calls over pizzicato, the crew hums back; three knocks and a breath ----
    line(0.0, CALL_A, fid, 'lead', 92)
    answer(2 * BAR, RESP_A, 80, full=False)
    line(4 * BAR, CALL_B, fid, 'lead', 96)
    for b, c in enumerate(['Dm', 'Dm', 'C', 'C', 'Dm', 'F']):
        t = b * BAR
        M.add('bass', cb.play(ROOT[c], 88), t, 1.0)
        M.add('bass', cb.play(ROOT[c] + 7, 76), t + 3 * E8, 0.8)
        for e in (1, 2, 4, 5):
            for m in CH[c]:
                M.add('box', vpz.play(m, 66), t + e * E8, 0.6, 0.3 if e < 3 else -0.3)
        M.add('perc', clave.play(80), t + 3 * E8, 0.5, -0.3)
    for i, tk in enumerate(T_KNOCK):
        M.add('drums', timp.play(100 + 10 * i), tk, 0.9, pan_at(SLUICE))
        M.add('fx', wood.play(110), tk, 0.7, pan_at(SLUICE))
    M.add('strings', trem.play(n('A3'), 55, dur=T_SLUICE - T_KNOCK[2] - 0.1, release=0.05), T_KNOCK[2] + 0.05, 0.5)

    # ---- 9.6: the sluice bursts; the flood follows its fronts and every crest splashes ----
    M.add('drums', timp.play(125), T_SLUICE, 0.9, pan_at(SLUICE))
    M.add('drums', gong.play(110), T_SLUICE, 0.6, pan_at(SLUICE))
    M.add('drums', crash.play(115), T_SLUICE, 0.7, pan_at(SLUICE))
    N = int((D - T_SLUICE) * SR)
    tt = np.arange(N) / SR + T_SLUICE
    wl, wr = lp_noise(N, 14), lp_noise(N, 14)
    surge = np.exp(-(tt - T_SLUICE) / 1.2) * 1.5
    am = 0.75 + 0.25 * np.sin(2 * np.pi * 0.31 * tt) * np.sin(2 * np.pi * 0.17 * tt + 1)
    rr = np.minimum(FLOOD_V * (tt - T_SLUICE), L_TOTAL)
    pl = np.array([pan_at(SLUICE - x) for x in rr[::SR // 50]])
    pr = np.array([pan_at(SLUICE + x) for x in rr[::SR // 50]])
    pl, pr = np.interp(tt, tt[::SR // 50], pl), np.interp(tt, tt[::SR // 50], pr)
    al, ar = (pl + 1) * np.pi / 4, (pr + 1) * np.pi / 4
    left, right = wl * (am + surge), wr * (am + surge)
    sig = np.vstack([left * np.cos(al) + right * np.cos(ar), left * np.sin(al) + right * np.sin(ar)]) * 0.35
    M.add('water', sig, T_SLUICE)
    for end, dist in ((0.0, SLUICE), (L_TOTAL, L_TOTAL - SLUICE)):        # the fronts slap the ends
        th = T_SLUICE + dist / FLOOD_V
        M.add('fx', bubbles.play(110, pitch=-3, dur=0.6), th, 0.8, pan_at(end))
        M.add('drums', timp.play(95), th, 0.5, pan_at(end))
    emit = list(np.arange(T_SLUICE + BAR, bt(14), BAR)) + list(np.arange(bt(14), T_BEAT0 + 2, BEAT))
    for k, te in enumerate(emit):
        spl = lp_noise(int(0.3 * SR), 3) * np.exp(-np.arange(int(0.3 * SR)) / (0.06 * SR))
        M.add('water', np.vstack([spl, spl]) * 0.35, te, 1.0, pan_at(SLUICE))
        M.add('harp', harp.play(PENT[k % 6] - 12, 70), te, 0.6, pan_at(SLUICE + (300 if k % 2 else -300)))

    # ---- 9.6-24: the verse at full stamp over harp ripples, then the refrain ----
    verse(T_SLUICE, horn, 98, harp_ripple=True, vel=92)
    t0 = T_SLUICE + 8 * BAR
    line(t0, REFRAIN, vsus, 'strings', 98, 1.2)
    line(t0, REFRAIN, fid, 'lead', 96, 0.8)
    accomp(t0, REFRAIN_CH, harp_ripple=True, vel=96, double=True)

    # ---- 24-44.4: the beaters: the crew at work, a chug and a splash on every heave ----
    verse(T_BEAT0, fid, 104, vel=98)
    t0 = T_BEAT0 + 8 * BAR
    line(t0, ['A4 - - D5 - -', 'A4 - - D5 - -'], tpt, 'lead', 100)        # the spin at the ends: a fanfare
    accomp(t0, ['Dm', 'Dm'], vel=100, double=True)
    M.add('perc', ratchet.play(90, dur=2 * BAR), t0, 0.5, pan_at(260))
    M.add('perc', ratchet.play(90, dur=2 * BAR), t0, 0.5, pan_at(2470))
    t0 = T_BEAT_BACK
    line(t0, CALL_A + CALL_B + ['A4 - A4 D5 - E5', 'F5 - G5 A5 - -'], fid, 'lead', 108)
    accomp(t0, VERSE_CH[:6], vel=104, double=True)
    for k in range(12):                                   # the tremolo climbs as they race back
        M.add('strings', trem.play(n('D3') + k, 62 + 4 * k, dur=BEAT, release=0.05), t0 + k * BEAT, 0.8)
    k = np.arange(int(0.14 * SR)) / SR
    chug = np.sin(2 * np.pi * (70 - 120 * k) * k) * np.exp(-k / 0.05)
    heaves = [(T_BEAT0 + kb * BEAT + k * BAR, kb) for kb in range(2) for k in range(8)]
    heaves += [(T_BEAT_BACK + kb * BEAT / 2 + k * BEAT, kb) for kb in range(2) for k in range(12)]
    for t, kb in heaves:
        p = pan_at(beater(kb, t + 0.2))
        M.add('churn', np.vstack([chug, chug]) * 0.6, t, 1.0, p)
        M.add('churn', bubbles.play(95, pitch=nr.uniform(-3, 3), dur=0.35), t + 0.05, 0.6, p)
        spl = lp_noise(int(0.3 * SR), 3) * np.exp(-np.arange(int(0.3 * SR)) / (0.06 * SR))
        M.add('churn', np.vstack([spl, spl]) * 0.3, t + 0.08, 1.0, p)
    B, loose, _ = berries()
    for i in np.argsort(loose)[::3]:                     # a marimba bloop for every third berry knocked loose
        if loose[i] < T_HOLD:
            M.add('mallet', mar.play(PENT[i % len(PENT)], 72), loose[i], 0.6, pan_at(B[i]))
    # nose to nose: a bar of held breath, then the slam
    M.add('drums', troll.play(80, dur=T_COL - T_HOLD - 0.05), T_HOLD, 0.6, pan_at(SLUICE))
    M.add('strings', trem.play(n('A3'), 80, dur=T_COL - T_HOLD, release=0.05), T_HOLD, 0.7)
    M.add('strings', trem.play(n('D#4'), 80, dur=T_COL - T_HOLD, release=0.05), T_HOLD, 0.6)
    M.add('drums', crash.play(127), T_COL, 0.9, pan_at(SLUICE))
    M.add('drums', timp.play(127), T_COL, 0.9, pan_at(SLUICE))
    M.add('drums', bd.play(127), T_COL, 1.0)
    M.add('fx', bubbles.play(120, pitch=-5), T_COL, 0.9, pan_at(SLUICE))
    for j in range(16):                                   # berries flying out to both sides
        sgn = -1 if j % 2 else 1
        M.add('mallet', mar.play(PENT[(j * 2) % len(PENT)], 95 - 2 * j), T_COL + 0.05 * j, 0.6,
              pan_at(SLUICE + sgn * 1250 * 0.05 * j))
        M.add('mallet', glock.play(PENT[(j * 3) % len(PENT)] + 12, 70), T_COL + 0.05 * j + 0.025, 0.35,
              pan_at(SLUICE - sgn * 1250 * 0.05 * j))
    t0 = T_COL
    line(t0, ['D5 - - A4 - -'], horn, 'lead', 110)
    accomp(t0, ['Dm'], vel=106, double=True)

    # ---- 45.6-64.8: the sea of red: fiddle and clarinet in thirds, then the refrain twice for everyone ----
    verse(T_SEA, fid, 108, vel=100, double=True)
    line(T_SEA, CALL_A, clar, 'box', 88, 0.9, shift=-3)
    line(T_SEA + 4 * BAR, CALL_B, clar, 'box', 88, 0.9, shift=-3)
    for rep in range(2):
        t0 = T_SEA + 8 * BAR + rep * 4 * BAR
        M.add('drums', crash.play(110), t0, 0.7)
        M.add('drums', timp.play(118), t0, 0.8)
        line(t0, REFRAIN, horn, 'lead', 112, 1.0)
        line(t0, REFRAIN, tpt, 'lead', 104, 0.75, 0.2)
        line(t0, REFRAIN, vsus, 'strings', 105, 1.0, -0.2)
        answer(t0, REFRAIN, 108)
        accomp(t0, REFRAIN_CH, vel=104, double=True)
        for b in range(2):                                # the big swell round the house: a glock run that follows
            if rep == 1:
                for j in range(12):
                    head = (j / 12) * (L_TOTAL + 600) - 300
                    if b % 2:
                        head = L_TOTAL - head
                    M.add('mallet', glock.play(PENT[(j + 3 * b) % len(PENT)], 66), t0 + 2 * b * BAR + j * E8, 0.4,
                          pan_at(head))

    # ---- 64.8-79.2: the booms: a heave a bar (stamp, grunt, rope) and a slip on a slide whistle ----
    verse(T_BOOM, horn, 104, vel=100)
    t0 = T_BOOM + 8 * BAR
    line(t0, REFRAIN, fid, 'lead', 110)
    line(t0, REFRAIN, horn, 'lead', 102, 0.7)
    answer(t0, REFRAIN, 110)
    accomp(t0, REFRAIN_CH, vel=104, double=True)
    for b in range(12):
        t = T_BOOM + b * BAR
        L, R = booms(t + 0.4)
        for x in (L, R):
            p = pan_at(x)
            M.add('perc', creak.play(90, pitch=-4, dur=0.6), t + 0.05, 0.55, p)
        M.add('crew', bstac.play(n('D3'), 112), t, 0.9, -0.2)
        M.add('crew', bsn.play(n('D2'), 112), t, 0.8, 0.2)
        M.add('drums', bd.play(120), t, 0.8)
        sl = slide(0.0, 0.3, 900, 620, 0.36, amp=0.22)
        M.add('fx', sl, t + 0.5 * BAR, 0.6, pan_at(R if b % 2 else L))
        choir_notes.append((t, n('D4'), 100, 0.25))            # "HEAVE"
        choir_notes.append((t, n('A3'), 95, 0.25))
    # the bulge: a trombone fall; the held beat: a timpani roll
    M.add('crew', fall.play(n('D3'), 118), T_BULGE, 1.0)
    M.add('crew', fall.play(n('A3'), 110), T_BULGE, 0.8, 0.3)
    M.add('fx', slide(0.0, 0.5, 400, 1300, 0.6, amp=0.25), T_BULGE + 0.1, 0.7, 0.0)
    M.add('drums', troll.play(100, dur=T_SNAP - T_STILL - 0.05), T_STILL, 0.8, pan_at(SLUICE))
    M.add('strings', trem.play(n('A3'), 90, dur=T_SNAP - T_STILL, release=0.05), T_STILL, 0.8)
    M.add('strings', trem.play(n('C#4'), 90, dur=T_SNAP - T_STILL, release=0.05), T_STILL, 0.7)

    # ---- 81.6: the snap: the refrain once more for everyone, landing on D major ----
    t0 = T_SNAP
    M.add('drums', crash.play(127), t0, 0.9, pan_at(SLUICE))
    M.add('drums', timp.play(127), t0, 0.9, pan_at(SLUICE))
    for j in range(10):
        sgn = -1 if j % 2 else 1
        M.add('mallet', glock.play(PENT[(j * 2) % len(PENT)], 80), t0 + 0.06 * j, 0.5, pan_at(SLUICE + sgn * 84 * j))
    line(t0, REFRAIN_END, horn, 'lead', 116)
    line(t0, REFRAIN_END, tpt, 'lead', 108, 0.8)
    line(t0, REFRAIN_END, fid, 'lead', 108, 0.8)
    answer(t0, REFRAIN_END, 112)
    accomp(t0, REFRAIN_CH[:3] + ['D'], vel=108, double=True)
    hold = D - T_CHORD - 0.6
    for m, inst, bus, v, gn in ((n('D2'), cello, 'strings', 108, 1.0), (n('A2'), cello, 'strings', 104, 0.8),
                                (n('D3'), bone, 'crew', 108, 0.9), (n('F#3'), horn, 'lead', 104, 0.8),
                                (n('A3'), horn, 'lead', 104, 0.8), (n('D4'), clarl, 'box', 98, 0.9),
                                (n('F#4'), vsus, 'strings', 104, 0.9), (n('D5'), fid, 'lead', 104, 0.8)):
        M.add(bus, inst.play(m, v, dur=hold, release=1.5), T_CHORD, gn)
    for m, v in ((n('D4'), 100), (n('F#4'), 95), (n('A4'), 95), (n('D3'), 90)):
        choir_notes.append((T_CHORD, m, v, hold))
    M.add('bass', cb.play(n('D2'), 124), T_CHORD, 1.2)
    M.add('bass', tuba.play(n('D2'), 120), T_CHORD, 0.8)
    M.add('drums', bd.play(124), T_CHORD, 1.0)
    M.add('drums', timp.play(124), T_CHORD, 0.9)
    M.add('drums', crash.play(118), T_CHORD, 0.8)
    for i, m in enumerate(('D3', 'F#3', 'A3', 'D4', 'F#4', 'A4', 'D5')):
        M.add('harp', harp.play(n(m), 90), T_CHORD + 0.06 * i, 0.8, -0.6 + 0.2 * i)
    for b in range(2):                                    # the stamps go on under the chord
        M.add('drums', bd.play(110), T_CHORD + (b + 1) * BAR, 0.7)
        M.add('perc', tamb.play(90), T_CHORD + (b + 1) * BAR + 3 * E8, 0.6)

    M.add('choir', ooh.render(choir_notes, D), 0.0, 1.0)
