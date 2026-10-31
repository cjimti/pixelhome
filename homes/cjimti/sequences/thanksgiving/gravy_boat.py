"""Gravy Boat: The porch is a plate and the wings are a cranberry-and-gold tablecloth whose checks waltz outward a
step on every downbeat. Eight dollops of mashed potato plop onto the porch, each sending a ripple out to both ends of
the house, and pile into a mountain; a spoon presses a well into the top. The good-china gravy boat, in blue, sails in
from the free end of Right leaving a wake, and pours: every glug sends a ring of gloss round the roof, and the well
fills and keeps filling. Overfull, the rims bulge on the beat, faster and faster, the checks crowd in toward the porch
and the wings flash back and forth; everything holds its breath, and the left side bursts: potato flies out to the
free end of the Side and a gravy flood races after it, rolling in galloping chevrons. Then the right rim goes, and a
second river races for the end of Right until bread rolls tumble in and stack into a levee, bouncing on the beat. A
giant silver spoon pops up at the far end of Left and sweeps the gravy back up the slope; two dollops patch the dam,
the spoon pours it back in, and a pat of butter melts on top: a gold wave rolls out to both ends, the whole plate
waltzes in rings of gold, and a last sweep of gold runs the length of the roof."""
import numpy as np
from pixelhome.fx import DT, hexc, light, keys, smoothstep, lerp, Flicker, nframes

CODE = 'TG13'
TITLE = 'Gravy Boat'
KIND = 'show'
DESCRIPTION = ('A mashed-potato mountain fills the porch and the gravy boat pours into the well, and keeps pouring. '
               'The dam breaks, gravy floods the roof, and a levee of bread rolls and a giant spoon come to the rescue.')
VOICEOVER = "Careful with that gravy boat: the mashed potatoes can only hold so much."

D = 90.0
SEED = 13
BAR = 1.5                                       # a waltz bar, three beats of half a second
IVORY = hexc('#ffe2b4')
GRAVY = hexc('#b04004')
GLOSS = hexc('#ff9a30')
CHINA = hexc('#3a80ff')
SILVER = hexc('#d8e6ff')
ROLL = hexc('#ffa018')
TOAST = hexc('#c04a06')
BUTTER = hexc('#ffe000')
CRANBERRY = hexc('#c0102a')
GOLD = hexc('#ffb000')

MID = 1486.0                                    # top of the mountain
BASE_L, BASE_R = 894.0, 2032.0                  # the foot of each slope (the porch's front corners)
WELL = 70.0                                     # the well's half-width
RIM_L, RIM_R = MID - WELL - 10, MID + WELL + 10
DOLLOPS = [(1.5, MID, 150, 0.8), (3.0, 1330, 140, 0.7), (4.5, 1640, 140, 0.7), (6.0, 1160, 160, 0.6),
           (7.5, 1810, 160, 0.6), (9.0, 1000, 150, 0.45), (10.5, 1950, 150, 0.45), (12.0, MID, 120, 0.6)]
T_WELL = 13.0
T_BOAT_OFF = 73.5                               # the boat sails home off the end of Right
T_ROLLS_OFF = 70.5                              # job done, the rolls tumble back out
BOAT = [(14.0, 2580), (15.5, 2420), (20.5, 1720), (22.0, 1600), (46.5, 1600), (47.2, 1790), (T_BOAT_OFF, 1790),
        (T_BOAT_OFF + 4.5, 2640), (90, 2640)]
T_POUR0, T_FULL, T_BREAK_L, T_BREAK_R = 24.0, 38.0, 46.5, 52.5
T_HUSH = T_BREAK_L - 0.6                        # everything holds its breath before the burst
FILL = [(0, 0), (T_POUR0 + 0.5, 0), (T_FULL, 1.0), (T_BREAK_L, 1.3), (T_BREAK_L + 1.5, 0.45), (T_BREAK_R, 0.4),
        (T_BREAK_R + 1.5, 0.1), (66.0, 0.1), (68.0, 1.0), (90, 1.0)]
ROLLS = [(53.0 + 0.55 * k, 2240 + 32 * k) for k in range(5)]   # (lands at, where): the levee
LEVEE = 2225.0
T_SPOON, T_SCOOPED, T_POUR_BACK = 58.5, 65.5, 66.0
T_PATCH = (69.0, 69.75)
T_BUTTER = 72.0
T_SWEEP = 84.0                                  # the last chord: gold runs the length of the roof
GB = 0.375                                      # a galop beat
GRID = [(0.0, 0.5, 3), (T_BREAK_L + GB, GB, 2), (T_SPOON + 0.75, 0.5, 3), (T_BUTTER, 0.5, 3)]


def grid(t):
    """(beat length, phase in the beat 0..1, beat in the bar, beat count) of the music at t."""
    s, b, per = [g for g in GRID if g[0] <= t][-1]
    k = int((t - s) / b)
    return b, (t - s) / b - k, k % per, k


def tight(t):
    """0..1: how hard the well is straining (the beat doubles, then doubles again, before the burst)."""
    return smoothstep(T_FULL, T_HUSH, t) * (t < T_BREAK_L)


def strain_beats():
    """The beats the rims bulge on while overfull: halves, then quarters, then eighths up to the hush."""
    ts, t = [], T_FULL
    while t < T_HUSH - 1e-6:
        ts.append(t)
        t += 0.5 if t < 42.0 else 0.25 if t < 44.5 else 0.125
    return ts


def front_left(t):
    """Path distance reached by the left flood (lower is farther): out to the free end of the Side."""
    if t <= T_BREAK_L:
        return RIM_L
    return float(keys(t, [(T_BREAK_L, RIM_L), (T_BREAK_L + 1.0, BASE_L), (T_BREAK_L + 2.0, 492.0),
                          (T_BREAK_L + 3.0, -20.0)]))


def front_right(t):
    if t <= T_BREAK_R:
        return RIM_R
    return float(keys(t, [(T_BREAK_R, RIM_R), (T_BREAK_R + 1.4, BASE_R), (T_BREAK_R + 3.0, LEVEE - 40),
                          (T_BREAK_R + 3.8, LEVEE - 30), (T_BREAK_R + 5.0, LEVEE)]))


def spoon_at(t):
    return float(keys(t, [(T_SPOON, 540), (T_SPOON + 0.6, 560), (T_SCOOPED, RIM_L - 30), (T_POUR_BACK + 2.2, RIM_L - 30),
                          (T_POUR_BACK + 3.2, 1100), (T_POUR_BACK + 4.0, 1060)]))


def rings():
    """Every ripple that runs along the roof: (start, origin, speed, life, colour, amp, width)."""
    r = []
    for t0, p, w, a in DOLLOPS:                 # each plop ripples out to both ends
        r.append((t0, p, 520.0, 2.6, lerp(IVORY, GOLD, 0.5), 0.85, 40.0))
    for t in (14.4, 14.85, 22.2, 22.65):         # the ship's horn
        r.append((t, float(keys(t, BOAT)), 1300.0, 1.6, CHINA, 0.8, 40.0))
    for t in list(np.arange(15.0, 22.0, 0.5)) + list(np.arange(T_BOAT_OFF + 0.5, T_BOAT_OFF + 4.0, 0.5)):   # the wake
        r.append((float(t), float(keys(t, BOAT)) + 20, 280.0, 1.3, CHINA, 0.45, 16.0))
    for t in np.arange(T_POUR0 + 0.5, T_HUSH, 0.5):   # every glug rings gloss round the roof
        r.append((float(t), MID, 420.0, 2.8, GLOSS, 0.7 + 0.25 * tight(t), 34.0))
    for t in strain_beats():
        r.append((t, MID, 700.0, 1.4, lerp(GLOSS, CRANBERRY, 0.4), 0.4 + 0.5 * tight(t), 24.0))
    r.append((T_BUTTER, MID, 620.0, 3.0, BUTTER, 1.0, 60.0))
    for k in range(1, 8):                        # the reprise: a ring of gold on every downbeat
        r.append((T_BUTTER + k * BAR, MID, 480.0, 2.8, GOLD if k % 2 else BUTTER, 0.85, 45.0))
    return r


def render(G, seed=SEED):
    rng = np.random.default_rng(seed)
    F = nframes(D)
    out = np.zeros((F, G.N, 3))
    n = G.N
    pdp = G.pd[G.path]
    slow = Flicker(rng, n, 0.15, 0.6)
    fizz = Flicker(rng, n, 2.0, 6.0)
    d = pdp - MID
    table = (pdp < BASE_L) | (pdp > BASE_R)
    q = np.where(pdp < MID, BASE_L - pdp, pdp - BASE_R)             # distance out along the cloth from the plate
    left_wing = pdp < MID
    drips = [(rng.uniform(40, T_BREAK_L), rng.choice([-1, 1])) for _ in range(16)]
    cracks = np.sort(rng.uniform(42, T_BREAK_L, 30))
    chunks = rng.uniform(-1, 1, 12)
    R = rings()
    r_t = np.array([x[0] for x in R])
    r_life = np.array([x[3] for x in R])
    sb = np.array(strain_beats())

    cloth_pos, cloth_target, last_k = 0.0, 0.0, -1
    ridge_pos, ridge_target = 0.0, 0.0

    for f in range(F):
        t = f * DT
        buf = np.zeros((n, 3))
        fade = keys(t, [(0, 0), (1.0, 1.0), (88, 1.0), (90, 0.0)])
        b, ph, kb, k = grid(t)
        acc = np.exp(-ph * b / 0.11) * (1.0 if kb == 0 else 0.5)          # the waltz's oom-pah-pah
        tg = tight(t)
        hush = 1 - 0.7 * smoothstep(T_HUSH, T_HUSH + 0.15, t) * (t < T_BREAK_L)

        # the tablecloth: checks that step outward on every downbeat (inward, every beat, while the well strains)
        cell = 40 - 18 * tg
        if k != last_k:
            last_k = k
            if tg > 0.02:
                cloth_target -= cell * 0.5
            elif kb == 0:
                cloth_target += cell
            ridge_target += 30 if (kb == 0 or T_BREAK_L <= t < T_SPOON) else 0
            ridge_target += 15 * (tg > 0.02)
        cloth_pos += (cloth_target - cloth_pos) * 0.3
        ridge_pos += (ridge_target - ridge_pos) * 0.3
        sq = np.clip(2.5 * np.cos(np.pi * (q - cloth_pos) / cell), -1, 1) * 0.5 + 0.5
        cl = (0.36 + 0.22 * acc) * (0.9 + 0.2 * slow(t)) * (1 + 0.5 * tg)
        base = light(1.0, cl * table) * (sq[:, None] * CRANBERRY + (1 - sq[:, None]) * GOLD)
        base += light(GOLD, 0.2 * table)
        if tg > 0:                                # the wings answer each other, left on one beat and right on the next
            side = left_wing if (k % 2 == 0) else ~left_wing
            base += light(lerp(CRANBERRY, GLOSS, 0.3), 0.75 * tg * np.exp(-ph * b / 0.1) * table * side)
        cover = np.zeros(n)

        # the mountain: dollops pile up; a well at the top; patches on the rims after the break
        h = np.zeros(n)
        for t0, p, w, a in DOLLOPS + [(T_PATCH[0], RIM_L - 20, 70, 0.5), (T_PATCH[1], RIM_R + 20, 70, 0.5)]:
            if t >= t0 - 0.35:
                u = t - t0
                fall = smoothstep(-0.35, 0.0, u)
                squash = 1 + 0.3 * np.exp(-max(u, 0) / 0.25) * np.sin(14 * max(u, 0))
                h += a * fall * np.exp(-(d - (p - MID)) ** 2 / (w * squash) ** 2)
                if 0 <= u < 0.5:                   # the plop
                    buf += light(IVORY, 0.95 * np.exp(-u / 0.12) * np.exp(-((pdp - p) / (w * 0.7)) ** 2))
        h = np.minimum(h, 0.2 + 0.8 * np.clip(1 - np.abs(d) / 600, 0, 1) ** 1.6) * ((pdp >= BASE_L - 30) & (pdp <= BASE_R + 30))
        dug = smoothstep(T_WELL - 0.4, T_WELL + 0.4, t)
        well = np.clip((WELL - np.abs(d)) / 8, 0, 1) * dug
        rim = np.exp(-((np.abs(d) - WELL - 8) / 10) ** 2) * dug
        bulge = 0.0
        if len(sb) and T_FULL <= t < T_BREAK_L:   # the rims bulge on every strain beat
            u = t - sb[np.searchsorted(sb, t, side='right') - 1]
            bulge = (0.4 + 0.8 * tg) * np.exp(-u / 0.07)
        broken_l = smoothstep(T_BREAK_L, T_BREAK_L + 0.3, t) * (1 - smoothstep(T_PATCH[0], T_PATCH[0] + 0.3, t))
        broken_r = smoothstep(T_BREAK_R, T_BREAK_R + 0.3, t) * (1 - smoothstep(T_PATCH[1], T_PATCH[1] + 0.3, t))
        rim_l, rim_r = (d < 0) * rim, (d > 0) * rim
        rimI = rim_l * (1 - 0.8 * broken_l) + rim_r * (1 - 0.8 * broken_r)
        ridge = 0.55 + 0.45 * np.clip(2 * np.cos(2 * np.pi * (np.abs(d) - ridge_pos) / 120), -1, 1)   # swirls down the slopes
        potI = (0.12 + 0.62 * h * ridge) * (1 - 0.85 * well) * (1 + 0.22 * acc * (t < T_BREAK_L or t > T_SPOON))
        potI = potI + 0.5 * rimI * (1 + bulge)
        base += light(IVORY, potI)

        # the gravy in the well: wider and brighter as it fills, glossy, rising over the rims before the break
        fill = float(keys(t, FILL))
        if fill > 0.01:
            wv = WELL * min(fill, 1.0) + 25 * max(0.0, fill - 1.0) * (1 + 0.3 * bulge)
            pool = np.clip((wv - np.abs(d)) / 6, 0, 1)
            sheen = 0.5 + 0.5 * np.sin(0.09 * d - 1.7 * t) * np.sin(0.05 * d + 0.9 * t)
            buf += light(GRAVY, 0.95 * pool * (0.8 + 0.2 * min(fill, 1)))
            cover = np.maximum(cover, pool)
            buf += light(GLOSS, 0.6 * pool * sheen ** 3 + 0.4 * pool * acc)

        # the gravy boat, in good-china blue, with a white glint; it bobs on the beat and jerks back at the break
        bp = float(keys(t, BOAT))
        boat = np.exp(-((pdp - bp) / (26 * (1 + 0.15 * acc))) ** 2)
        if t >= BOAT[0][0]:
            tilt = smoothstep(T_POUR0 - 1, T_POUR0, t) * (1 - smoothstep(T_BREAK_L, T_BREAK_L + 0.3, t))
            glug = 1 + 0.25 * tilt * max(0, np.sin(2 * np.pi * t / 0.5)) ** 4
            buf += light(CHINA, (0.85 + 0.15 * acc) * boat * glug) + light(SILVER, 0.6 * np.exp(-((pdp - bp + 14) / 6) ** 2))
            buf += light(CHINA, 0.25 * np.exp(-((pdp - bp) / 90) ** 2))
            if tilt > 0:                          # glints running down from the spout into the well
                for j in range(6):
                    s = ((t * 1.6 + j / 6) % 1.0)
                    p = bp - 30 - s * (bp - 30 - MID)
                    buf += light(GLOSS, 0.85 * tilt * np.exp(-((pdp - p) / 7) ** 2))
                stream = tilt * ((pdp > MID) & (pdp < bp - 30))
                buf += light(GRAVY, 0.45 * stream)
                cover = np.maximum(cover, 0.6 * stream)

        # overflow: drips down the slopes; cracks in the rims
        for t0, sgn in drips:
            u = t - t0
            if 0 <= u < 3.0:
                p = MID + sgn * (WELL + 12 + 90 * u)
                buf += light(GLOSS, 0.75 * np.exp(-u / 1.5) * np.exp(-((pdp - p) / 9) ** 2))
        for tc in cracks:
            u = t - tc
            if 0 <= u < 0.3:
                buf += light(IVORY, np.exp(-u / 0.05) * np.exp(-((pdp - RIM_L + 4 * (tc % 1)) / 5) ** 2))

        # the bursts: a flash, and potato flung out toward the free end on that side
        for tb, rimp, sgn in ((T_BREAK_L, RIM_L, -1), (T_BREAK_R, RIM_R, 1)):
            u = t - tb
            if 0 <= u < 2.4:
                buf += light(lerp(IVORY, GLOSS, 0.4), 1.2 * np.exp(-u / 0.2) * np.exp(-((pdp - rimp) / 120) ** 2))
                for j, c in enumerate(chunks):
                    p = rimp + sgn * (450 + 650 * abs(c)) * u
                    buf += light(IVORY, 0.95 * np.exp(-u / 1.0) * np.exp(-((pdp - p) / 7) ** 2))
        spoon = spoon_at(t) if t >= T_SPOON else 0.0
        galop = np.exp(-ph * b / 0.1) * (1.0 if kb == 0 else 0.6) if T_BREAK_L <= t < T_SPOON + 0.75 else 0.0
        if t >= T_BREAK_L:
            fl = front_left(t)
            river = (pdp < RIM_L) & (pdp > fl)
            if t >= T_SPOON:                       # the spoon scoops everything behind it
                river &= pdp > spoon_at(min(t, T_SCOOPED)) + 12
                drain = 492 * (1 - smoothstep(T_SPOON + 0.3, T_SPOON + 2.5, t))  # the Side runs off its free end
                river = river & ~((pdp < 492) & (pdp > drain))
            chev = np.clip(2.2 * np.cos(2 * np.pi * (pdp / 110 + (t - T_BREAK_L) / GB)), -1, 1) * 0.5 + 0.5
            depth = 0.62 + 0.18 * galop
            buf += light(GRAVY, river * depth * (0.7 + 0.3 * (1 - chev))) + light(GLOSS, river * (0.3 + 0.45 * galop) * chev)
            cover = np.maximum(cover, river * 1.0)
            if fl > -15 and t < T_SPOON:
                buf += light(GLOSS, 1.0 * np.exp(-((pdp - fl) / 18) ** 2) * (0.75 + 0.25 * fizz(t)))
                buf += light(IVORY, 0.8 * np.exp(-((pdp - fl + 40) / 10) ** 2) * (t < T_BREAK_L + 3.0))
        if t >= T_BREAK_R:
            fr = front_right(t)
            soak = smoothstep(T_BREAK_R + 5.5, 64.0, t)            # the rolls drink it up from the levee back
            reach = fr - soak * (fr - RIM_R)
            river = (pdp > RIM_R) & (pdp < reach)
            chev = np.clip(2.2 * np.cos(2 * np.pi * (pdp / 110 - (t - T_BREAK_L) / GB)), -1, 1) * 0.5 + 0.5
            buf += light(GRAVY, (0.62 + 0.18 * galop) * river * (0.7 + 0.3 * (1 - chev))) + light(GLOSS, river * (0.3 + 0.45 * galop) * chev)
            cover = np.maximum(cover, river * 1.0)
            froth = np.exp(-((pdp - fr) / 16) ** 2) * (1 - soak)
            buf += light(GLOSS, 1.0 * froth * (0.7 + 0.3 * fizz(t)))

        # the bread rolls: tumble in from the free end of Right, stack into the levee, then bounce on the beat
        for j, (tl, rp) in enumerate(ROLLS):
            t_in = tl - 1.6
            if t < t_in:
                continue
            p = float(keys(t, [(t_in, 2560), (tl, rp)])) if t < tl else rp
            t_out = T_ROLLS_OFF + 0.3 * (4 - j)
            if t > t_out:
                p = rp + (t - t_out) ** 1.6 * 260
                if p > 2620:
                    continue
            bounce = 1 + 0.4 * np.exp(-max(0, t - tl) / 0.2) * (t >= tl)
            if t > tl + 0.5 and T_BREAK_R < t < T_BUTTER + 12 * BAR:
                beat_on = (k + j) % 2 == 0 if t < T_SPOON + 0.75 else kb == j % 3
                bounce += 0.45 * beat_on * np.exp(-ph * b / 0.12)
            toast = smoothstep(T_BREAK_R + 5.5 + 0.4 * j, 64 + 0.4 * j, t)
            w = 15 * (1 + 0.3 * toast)
            col = lerp(ROLL, TOAST, toast * 0.6)
            buf += light(col, 0.9 * np.exp(-((pdp - p) / w) ** 2) * min(bounce, 1.45))
            buf += light(ROLL, 0.22 * np.exp(-((pdp - p) / 60) ** 2))
            if 0 <= t - tl < 0.4:
                buf += light(GOLD, 0.8 * np.exp(-(t - tl) / 0.1) * np.exp(-((pdp - rp) / 40) ** 2))

        # the spoon: a silver bowl with its handle trailing, filling with gravy as it scoops, pouring it back
        if T_SPOON <= t:
            sp = spoon
            pop = smoothstep(T_SPOON, T_SPOON + 0.3, t) * (1 - smoothstep(T_POUR_BACK + 3.6, T_POUR_BACK + 4.2, t))
            full = smoothstep(T_SPOON + 0.5, T_SCOOPED, t) * (1 - smoothstep(T_POUR_BACK, T_POUR_BACK + 2.0, t))
            bowl = np.exp(-((pdp - sp) / 22) ** 2)
            handle = np.clip((sp - pdp) / 150, 0, 1) * (pdp < sp) * (pdp > sp - 150)
            buf += light(SILVER, pop * (0.95 * bowl * (1 - 0.6 * full) + 0.55 * handle))
            buf += light(GRAVY, pop * 0.9 * full * np.exp(-((pdp - sp) / 12) ** 2))
            buf += light(SILVER, pop * 0.25 * np.exp(-((pdp - sp) / 80) ** 2))
            if t < T_SCOOPED:                     # a polished, sparkling trail behind the spoon, glinting on the beat
                trail = (pdp < sp - 20) * np.exp(-(sp - pdp) / 260) * pop
                glint = np.clip(np.cos(2 * np.pi * (pdp / 60 - 2 * t)), 0, 1) ** 6
                buf += light(SILVER, trail * (0.25 + 0.5 * glint + 0.35 * acc))
            if T_POUR_BACK <= t < T_POUR_BACK + 2.0:
                for j in range(5):
                    s = (t * 1.8 + j / 5) % 1.0
                    p = sp + 20 + s * (MID - sp - 20)
                    buf += light(GLOSS, 0.85 * np.exp(-((pdp - p) / 7) ** 2))
            if 0 <= t - T_SPOON < 0.5:
                buf += light(SILVER, np.exp(-(t - T_SPOON) / 0.12) * np.exp(-((pdp - sp) / 90) ** 2))

        # butter: a yellow pat drops on top and melts into the gravy
        u = t - T_BUTTER
        if u >= 0:
            pat = np.exp(-(d / (10 + 30 * smoothstep(0, 6, u))) ** 2) * keys(t, [(T_BUTTER, 1.0), (T_BUTTER + 8, 0.45)])
            buf += light(BUTTER, 0.95 * pat * (0.85 + 0.15 * fizz(t)))
            if u < 0.4:
                buf += light(BUTTER, np.exp(-u / 0.1) * np.exp(-(d / 120) ** 2))

        # ripples: plops, the horn, the wake, glugs, strain, butter and the reprise's rings
        for i in np.nonzero((t >= r_t) & (t < r_t + r_life))[0]:
            t0, o, sp_, life, col, amp, w = R[i]
            u = t - t0
            env = amp * (1 - u / life) ** 1.5
            for s in (-1, 1):
                buf += light(col, env * np.exp(-((pdp - o - s * sp_ * u) / w) ** 2))

        # the finish: the plate glows and pulses with the waltz, and gold sweeps the length of the roof
        glow = smoothstep(T_BUTTER + 2, T_BUTTER + 5, t)
        if glow > 0:
            buf += light(GOLD, 0.24 * glow * (0.8 + 0.2 * slow(t) + 0.5 * acc) * (np.abs(d) > 600))
            buf += light(IVORY, 0.18 * glow * h * (1 + acc))
        u = t - T_SWEEP
        if u >= 0:
            head = -60 + 1500 * u
            buf += light(lerp(GOLD, IVORY, 0.4), 1.1 * np.exp(-((pdp - head) / 50) ** 2))
            buf += light(GOLD, 0.45 * np.clip((head - pdp) / 200, 0, 1) * np.exp(-u / 2.5))

        buf += base * (1 - cover)[:, None]
        out[f][G.path] = np.clip(buf * fade * hush, 0, 1)
    return out


# ---------------------------------------------------------------- music ----------------------------------------------
# A dinner-table waltz in D, a bar to a second and a half. Each dollop is a plop on the downbeat where it lands; the
# spoon digs the well on a slide whistle. The gravy boat sails in on an oboe tune with a two-note ship's horn, and as it
# pours, bassoon glugs climb in pitch like a bottle filling, over bubbles. Overfull: tremolo strings, creaks and cracks
# where the rim is splitting. The dam bursts on a crash and the waltz falls into a galop in D minor, the flood rushing
# across the house as filtered noise with the front. The rolls bonk into place one by one at the end of Right under
# a trumpet call, and soak up the river with a slurp; the spoon pops up with a clink, scrapes the gravy back up the
# slope to a horn tune in 3/4, and pours it back in on a harp. Two plops patch the dam, the butter melts on the
# glockenspiel, and the waltz comes back, warm and full. While the well strains, a woodblock knocks on every bulge of
# the rims, quicker and quicker, over the tremolo, which cuts off for the held breath before the burst. The rolls
# tumble home on log drums, the boat toots and sails off, and the last chord's harp runs the length of the roof with
# the sweep of gold.

CH = {'D': (57, 62, 66), 'G': (55, 59, 62), 'A7': (55, 61, 64), 'A': (57, 61, 64), 'Bm': (54, 59, 62),
      'Em': (55, 59, 64), 'Dm': (57, 62, 65), 'Gm': (55, 58, 62), 'Bb': (58, 62, 65), 'F': (57, 60, 65),
      'E7': (56, 62, 64)}
ROOT = {'D': 38, 'G': 43, 'A7': 45, 'A': 45, 'Bm': 47, 'Em': 40, 'Dm': 38, 'Gm': 43, 'Bb': 46, 'F': 41, 'E7': 40}
# the waltz tune, a bar each: (beat, note, beats)
WALTZ = [[(0, 'F#4', 2), (2, 'A4', 1)], [(0, 'D5', 2), (2, 'C#5', 1)], [(0, 'B4', 1), (1, 'A4', 1), (2, 'G4', 1)],
         [(0, 'F#4', 3)], [(0, 'E4', 2), (2, 'G4', 1)], [(0, 'B4', 2), (2, 'A4', 1)],
         [(0, 'G4', 1), (1, 'F#4', 1), (2, 'E4', 1)], [(0, 'D4', 3)]]
WALTZ_CH = ['D', 'D', 'G', 'D', 'A7', 'A7', 'A7', 'D']
BOATS = [[(0, 'A4', 1), (1, 'D5', 1), (2, 'D5', 1)], [(0, 'C#5', 1), (1, 'B4', 1), (2, 'A4', 1)],
         [(0, 'B4', 1), (1, 'G4', 1), (2, 'E4', 1)], [(0, 'A4', 3)]]
BOATS_CH = ['D', 'A', 'Em', 'A']
GALOP = [[(0, 'D5', 0.5), (0.5, 'A4', 0.5), (1, 'F4', 0.5), (1.5, 'A4', 0.5)],
         [(0, 'D5', 0.5), (0.5, 'E5', 0.5), (1, 'F5', 1)],
         [(0, 'E5', 0.5), (0.5, 'C#5', 0.5), (1, 'A4', 0.5), (1.5, 'C#5', 0.5)],
         [(0, 'E5', 0.5), (0.5, 'F5', 0.5), (1, 'E5', 1)]]
GALOP_CH = ['Dm', 'Dm', 'A7', 'A7']


def score(M, G):
    from pixelhome.audio import SR, note, slide, whoosh
    n = note
    clar = M.sampler('Woodwinds/Clarinet/susLong/*.wav', tune=-12)
    clar_st = M.sampler('Woodwinds/Clarinet/stac/*.wav', tune=-12)
    flute = M.sampler('Woodwinds/Flute/susvib/*.wav', tune=-12)
    oboe = M.sampler('Woodwinds/Oboe/Sus/*.wav', tune=-12)
    bsn = M.sampler('Woodwinds/Bassoon/stac/*.wav', tune=-12)
    horn = M.sampler('Brass/F Horn/sus/*.wav', tune=-12)
    tpt = M.sampler('Brass/Trumpet/sus/*.wav', tune=-12)
    tpt_st = M.sampler('Brass/Trumpet/stac/*.wav', tune=-12)
    tuba = M.sampler('Brass/Tuba/stac/*.wav', tune=-12)
    tuba_s = M.sampler('Brass/Tuba/sus/*.wav', tune=-12)
    cpizz = M.sampler('Strings/Cello Section/pizzT/*.wav', tune=-12)
    vpizz = M.sampler('Strings/Violin Section/Pizz/*.wav', tune=-12)
    spic = M.sampler('Strings/Violin Section/Spic/*.wav', tune=-12)
    vln = M.sampler('Strings/Violin Section/susVib/*.wav', tune=-12)
    cello = M.sampler('Strings/Cello Section/susvib/*.wav', tune=-12)
    trem = M.sampler('Strings/Cello Section/trem/*.wav', tune=-12)
    vtrem = M.sampler('Strings/Violin Section/Trem/*.wav', tune=-12)
    harp = M.sampler('Strings/Harp/*.wav')
    glock = M.sampler('Percussion/Glock/*.wav', tune=-12)
    xylo = M.sampler('Percussion/Xylo/*.wav', tune=-12)
    timp = M.hits('Percussion/Timpani/Timpani1_Hit*.wav')
    troll = M.hits('Percussion/Timpani/Rolls/Timpani1_Roll*.wav')
    crash = M.hits('Percussion/cymbal-crash1_f*.wav')
    bd = M.hits('Percussion/BDrumNewhit_v[4-7]*.wav')
    snare = M.hits('Percussion/Snare2-HitSN_v[579]*.wav')
    log = M.hits('Percussion/LogDrumLo_MedM_v[23]*.wav')
    wood = M.hits('VSCO 1 Percussion/varWood/claves_m*.wav')
    guiro = M.hits('VSCO 1 Percussion/varWood/guiro_long*.wav')
    slap = M.hits('VSCO 1 Percussion/varWood/slapstick[0-9].wav')
    bubbles = M.hits('Miscellania Raw/Misc 1/bubbles*.wav')
    clink = M.hits('Miscellania Raw/Misc 1/metal_hit[1-5].wav')
    scrape = M.hits('Miscellania Raw/Misc 1/brick_scrape*.wav')
    tri = M.hits('Percussion/Triangle3-Hit_v1*.wav')

    for name, gain, rev in (('tune', 0.24, 0.22), ('brass', 0.22, 0.22), ('bass', 0.38, 0.08), ('pizz', 0.26, 0.15),
                            ('strings', 0.22, 0.3), ('harp', 0.28, 0.3), ('bells', 0.24, 0.25), ('drums', 0.3, 0.12),
                            ('fx', 0.22, 0.2), ('flood', 0.16, 0.2), ('glug', 0.16, 0.15)):
        M.bus(name, gain=0.85 * gain, reverb=rev)

    L = G.length
    order = np.argsort(G.pd)
    xs, ds = G.pos[order, 0], G.pd[order]
    x0, x1 = xs.min(), xs.max()

    def pan_at(d):
        x = np.interp(np.clip(d, 0, L), ds, xs)
        return float(0.85 * (2 * (x - x0) / (x1 - x0) - 1))

    def mono(sig):
        return np.vstack([sig, sig])

    def moving(sig, t0, ts, ps):
        tt = t0 + np.arange(sig.shape[1]) / SR
        a = (np.clip(np.interp(tt, ts, ps), -1, 1) + 1) * np.pi / 4
        return sig * np.vstack([np.cos(a), np.sin(a)]) * np.sqrt(2)

    def plop(f0=260.0, dur=0.35, seed=0):
        """Something soft landing: a falling sine with a thump of noise."""
        r = np.random.default_rng(seed)
        tt = np.arange(int(dur * SR)) / SR
        f = f0 * np.exp(-tt / 0.06) + 70
        sig = np.sin(2 * np.pi * np.cumsum(f) / SR) * np.exp(-tt / 0.09)
        thump = np.convolve(r.normal(0, 1, len(tt)), np.ones(30) / 30, 'same') * np.exp(-tt / 0.03) * 2
        return mono(sig + thump)

    def blub(f0, dur=0.18):
        """One glug: a bubble's rising chirp."""
        tt = np.arange(int(dur * SR)) / SR
        f = f0 * (1 + 1.2 * tt / dur)
        return mono(np.sin(2 * np.pi * np.cumsum(f) / SR) * np.sin(np.pi * tt / dur) ** 2)

    def rush(dur, seed, lo=200, hi=1800):
        r = np.random.default_rng(seed)
        N = int(dur * SR)
        spec = np.fft.rfft(r.normal(0, 1, N))
        fq = np.fft.rfftfreq(N, 1 / SR)
        spec *= (fq / lo) ** 2 / (1 + (fq / lo) ** 2) / (1 + (fq / hi) ** 2)
        x = np.fft.irfft(spec, N)
        x /= np.abs(x).max()
        tt = np.arange(N) / SR
        x *= (1 + 0.4 * np.sin(2 * np.pi * 3.1 * tt) * np.sin(2 * np.pi * 0.7 * tt))
        return x * np.clip(tt / 0.1, 0, 1) * np.clip((dur - tt) / 0.8, 0, 1)

    def slurp(dur=0.5, seed=0):
        tt = np.arange(int(dur * SR)) / SR
        f = 300 * 2 ** (2 * tt / dur)
        r = np.random.default_rng(seed)
        nz = np.convolve(r.normal(0, 1, len(tt)), np.ones(10) / 10, 'same')
        return mono((0.6 * np.sin(2 * np.pi * np.cumsum(f) / SR) + 0.6 * nz) * np.sin(np.pi * tt / dur))

    def tune(bars, t0, inst, bus, vel, beat=BAR / 3, per_bar=3, shift=0, gain=1.0, pan=0.0):
        for j, bar in enumerate(bars):
            for e, m, ln in bar:
                M.add(bus, inst.play(n(m) + shift, vel, dur=ln * beat * 0.95, release=0.2),
                      t0 + (per_bar * j + e) * beat, gain, pan)

    def oom(t0, chords, vel=80, beat=BAR / 3):
        """The waltz accompaniment: bass on one, pizzicato chords on two and three."""
        for j, c in enumerate(chords):
            t = t0 + 3 * j * beat
            M.add('bass', cpizz.play(ROOT[c] + 12, vel), t, 0.9, -0.15)
            M.add('bass', tuba.play(ROOT[c], vel - 10), t, 0.5)
            for e in (1, 2):
                for m in CH[c]:
                    M.add('pizz', vpizz.play(m, vel - 15), t + e * beat, 0.5, 0.2)

    pm = pan_at(MID)

    # ---- 0-13: the dollops pile up on the waltz; the spoon digs the well ----
    oom(0.0, ['D'] + WALTZ_CH + ['D'], vel=72)
    tune(WALTZ, BAR, clar, 'tune', 85, pan=-0.1)
    for i, (t0, p, w, a) in enumerate(DOLLOPS):
        M.add('fx', plop(240 - 10 * i, seed=i), t0, 0.9, pan_at(p))
        M.add('drums', timp.play(70, pitch=-i % 5), t0, 0.35, pan_at(p))
    M.add('fx', slide(0.0, 0.6, 1200, 300, 0.7, 0.4), T_WELL - 0.3, 0.8, pm)
    M.add('fx', slurp(0.4, 1), T_WELL + 0.2, 0.6, pm)
    M.add('harp', harp.play(n('D3'), 70), T_WELL + 0.4, 0.6, pm)

    # ---- 14-24: the gravy boat sails in from the free end of Right ----
    tb = np.linspace(14, 22, 30)
    pb = [pan_at(keys(t, BOAT)) for t in tb]
    hornL = lambda t: pan_at(keys(t, BOAT))
    for t, m in ((14.4, 'A3'), (14.85, 'D3')):
        M.add('brass', horn.play(n(m), 105, dur=0.4), t, 0.9, hornL(t))
    oom(15.0, BOATS_CH + BOATS_CH, vel=75)
    tune(BOATS + BOATS, 15.0, oboe, 'tune', 92, pan=0.35)
    w = whoosh(8.0, 250, 900, 0.4, seed=3)
    M.add('fx', moving(w, 14.0, tb, pb), 14.0, 0.5)
    for t, m in ((22.2, 'A3'), (22.65, 'D3')):
        M.add('brass', horn.play(n(m), 100, dur=0.4), t, 0.8, hornL(t))

    # ---- 24-46.5: the pour; glugs climb as the well fills; then it overfills ----
    oom(T_POUR0, WALTZ_CH + WALTZ_CH, vel=78)
    tune(WALTZ, T_POUR0, flute, 'tune', 80, pan=0.1)
    tune(WALTZ, T_POUR0 + 8 * BAR, clar, 'tune', 88, pan=-0.1)
    for t in np.arange(T_POUR0 + 0.5, T_BREAK_L, 0.5):
        fl = float(keys(t, FILL))
        M.add('glug', blub(140 * 2 ** (1.4 * min(fl, 1.3))), t, 0.8, pan_at(1560))
        if int(t * 2) % 3 == 0:
            M.add('glug', bsn.play(n('D2') + int(round(12 * min(fl, 1.3))), 80, dur=0.2), t, 0.5, pan_at(1560))
    for t in (T_POUR0 + 1, T_POUR0 + 8, T_POUR0 + 15):
        M.add('fx', bubbles.play(90, dur=5.0), t, 0.5, pm)
    t_over = T_FULL                     # past the full mark: tremolo, creaks, cracks
    for k, c in enumerate(['A7', 'A7', 'Bb', 'Bb', 'E7', 'E7']):
        t = t_over + k * 1.3
        ln = min(1.3, T_HUSH - t)
        for m in CH[c]:
            M.add('strings', vtrem.play(m + 12 * (k > 3), 60 + 7 * k, dur=ln, release=0.05), t, 0.6, pm)
        M.add('strings', trem.play(ROOT[c], 70 + 6 * k, dur=ln, release=0.05), t, 0.7)
    for i, t in enumerate(strain_beats()):          # every bulge of the rims, quicker and quicker
        M.add('drums', wood.play(int(70 + 50 * tight(t)), pitch=4 * (i % 2)), t, 0.8, pan_at(RIM_L if i % 2 else RIM_R))
        if i % 2 == 0:
            M.add('pizz', spic.play(n('A3') + (i // 2) % 12, int(70 + 40 * tight(t))), t, 0.6, pm)
    rng = np.random.default_rng(SEED)              # the cracks render() draws, in the same order
    Flicker(rng, G.N, 0.15, 0.6)
    Flicker(rng, G.N, 2.0, 6.0)
    for _ in range(16):
        rng.uniform(40, T_BREAK_L), rng.choice([-1, 1])
    cracks = np.sort(rng.uniform(42, T_BREAK_L, 30))
    for tc in cracks:
        M.add('fx', wood.play(int(60 + 60 * (tc - 42) / 4.5), pitch=float(rng.uniform(-3, 5))), tc, 0.5, pan_at(RIM_L))
    for t in (40.5, 43.0, 45.0):
        M.add('fx', guiro.play(80, dur=1.2), t, 0.5, pan_at(RIM_L))
    r = troll.play(80, dur=T_HUSH - 43)
    M.add('drums', r * np.linspace(0.1, 1, r.shape[1]) ** 2, 43.0, 0.6, pm)
    M.add('fx', guiro.play(70, dur=0.35), T_HUSH + 0.15, 0.4, pan_at(RIM_L))      # the held breath: one creak

    # ---- 46.5: the left side gives way; a galop in D minor while it floods ----
    def burst(t, p):
        M.add('drums', crash.play(120), t, 0.8, p)
        M.add('drums', bd.play(127), t, 1.0, p)
        M.add('drums', timp.play(125, pitch=-2), t, 0.9, p)
        M.add('drums', slap.play(120), t, 0.8, p)
        M.add('fx', plop(400, 0.5, seed=50), t, 1.0, p)
        M.add('fx', whoosh(1.0, 2500, 300, 0.9, seed=int(t)), t, 0.8, p)

    burst(T_BREAK_L, pan_at(RIM_L))
    gb = 0.375                                      # a galop beat; two to a bar
    t_g = T_BREAK_L + 0.375
    nb = int((T_SPOON - t_g) / (2 * gb))
    for j in range(nb):
        t = t_g + 2 * j * gb
        c = GALOP_CH[j % 4]
        M.add('bass', tuba.play(ROOT[c], 105), t, 0.9)
        M.add('bass', cpizz.play(ROOT[c] + 19, 90), t + gb, 0.8, -0.1)
        for e in (0.5, 1.5):
            for m in CH[c]:
                M.add('pizz', spic.play(m, 80), t + e * gb, 0.5, 0.2)
        M.add('drums', snare.play(90), t + gb, 0.6, 0.1)
        M.add('drums', bd.play(95), t, 0.6)
    for j in range(0, nb, 4):
        tune(GALOP, t_g + 2 * j * gb, tpt_st if j >= 8 else xylo, 'tune' if j >= 8 else 'bells',
             100, beat=gb, per_bar=2, gain=0.8)
        tune(GALOP, t_g + 2 * j * gb, clar_st, 'tune', 90, beat=gb, per_bar=2, gain=0.6, shift=-12)
    # the floods: rushing water that runs with each front
    for tb_, fn, dur in ((T_BREAK_L, front_left, 11.0), (T_BREAK_R, front_right, 5.5)):
        ts = np.linspace(tb_, tb_ + dur, 60)
        ps = [pan_at(fn(t)) for t in ts]
        x = rush(dur, int(tb_))
        M.add('flood', moving(mono(x), tb_, ts, ps), tb_, 1.0)
        M.add('fx', bubbles.play(100, dur=dur), tb_ + 0.3, 0.5, ps[len(ps) // 2])
    M.add('fx', slide(0.0, 2.5, 900, 250, 3.0, 0.3), T_BREAK_L + 4.5, 0.6, pan_at(400))   # trickling down the Side

    # ---- 52.5: the right side goes too; the rolls tumble in and stack into a levee ----
    burst(T_BREAK_R, pan_at(RIM_R))
    for k, (tl, rp) in enumerate(ROLLS):
        ts = np.linspace(tl - 1.6, tl, 10)
        M.add('fx', moving(whoosh(1.6, 300, 1200, 0.5, seed=60 + k), tl - 1.6, ts,
                           [pan_at(keys(t, [(tl - 1.6, 2560), (tl, rp)])) for t in ts]), tl - 1.6, 0.4)
        M.add('drums', log.play(115, pitch=k), tl, 1.0, pan_at(rp))
        M.add('drums', timp.play(90, pitch=k), tl, 0.4, pan_at(rp))
    t_call = ROLLS[-1][0] + 0.2                     # the trumpet call: the levee holds
    for i, (dt, m, ln) in enumerate(((0, 'D4', 0.25), (0.25, 'F4', 0.25), (0.5, 'A4', 0.5), (1.0, 'D5', 1.2))):
        M.add('brass', tpt.play(n(m), 115, dur=ln), t_call + dt, 0.9, pan_at(LEVEE + 60))
    M.add('drums', crash.play(100), t_call + 1.0, 0.5, pan_at(LEVEE))
    for k in range(5):                              # the rolls soak it up
        M.add('fx', slurp(0.6, 70 + k), T_BREAK_R + 5.7 + 0.9 * k, 0.6, pan_at(ROLLS[k][1]))

    # ---- 58.5: the spoon pops up at the end of Left and scoops the gravy back up the slope ----
    ps = pan_at(spoon_at(T_SPOON))
    M.add('fx', clink.play(115), T_SPOON, 0.9, ps)
    M.add('bells', glock.play(n('D6'), 100), T_SPOON, 0.6, ps)
    ts = np.linspace(T_SPOON + 0.6, T_SCOOPED, 30)
    sc = scrape.play(90)
    sc = sc[:, :int((T_SCOOPED - T_SPOON - 0.6) * SR)]
    M.add('fx', moving(sc, T_SPOON + 0.6, ts, [pan_at(spoon_at(t)) for t in ts]), T_SPOON + 0.6, 0.5)
    hero = [[(0, 'D4', 1), (1, 'F#4', 1), (2, 'A4', 1)], [(0, 'D5', 2), (2, 'A4', 1)],
            [(0, 'B4', 1), (1, 'G4', 1), (2, 'B4', 1)], [(0, 'A4', 3)],
            [(0, 'G4', 1), (1, 'B4', 1), (2, 'D5', 1)], [(0, 'C#5', 2), (2, 'B4', 1)]]
    hero_ch = ['D', 'D', 'G', 'D', 'G', 'A']
    t_h = T_SPOON + 0.75
    for j, bar in enumerate(hero):
        for e, m, ln in bar:
            t = t_h + (3 * j + e) * 0.5
            M.add('brass', horn.play(n(m), 108, dur=ln * 0.5 * 0.95), t, 1.0, pan_at(spoon_at(t)) * 0.6)
    oom(t_h, hero_ch, vel=88)
    for j, c in enumerate(hero_ch):
        for m in CH[c]:
            M.add('strings', vln.play(m + 12, 62, dur=BAR), t_h + j * BAR, 0.4)
    # pours it back in
    for i in range(14):
        M.add('harp', harp.play([62, 66, 69, 74, 78, 81, 86][i % 7] - 12 * (i // 7), 80), T_POUR_BACK + 0.13 * i, 0.7,
              pan_at(RIM_L))
    for k, t in enumerate(np.arange(T_POUR_BACK, T_POUR_BACK + 2.0, 0.25)):
        M.add('glug', blub(180 * 2 ** (k / 8)), t, 0.7, pan_at(RIM_L))
    M.add('fx', bubbles.play(90, dur=2.0), T_POUR_BACK, 0.4, pm)

    # ---- 70.5: the rolls tumble home; 73.5: the boat sails off the end of Right ----
    for j in range(5):
        t = T_ROLLS_OFF + 0.3 * (4 - j)
        M.add('drums', log.play(100, pitch=4 - j), t, 0.7, pan_at(ROLLS[j][1]))
        M.add('fx', slide(0.0, 0.5, 700 - 60 * j, 300, 0.5, 0.25), t, 0.5, pan_at(2400))
    for t, m in ((T_BOAT_OFF, 'A3'), (T_BOAT_OFF + 0.45, 'D3')):
        M.add('brass', horn.play(n(m), 95, dur=0.4), t, 0.7, pan_at(1900))
    tb = np.linspace(T_BOAT_OFF, T_BOAT_OFF + 4.5, 30)
    M.add('fx', moving(whoosh(4.5, 250, 900, 0.35, seed=4), T_BOAT_OFF, tb, [pan_at(keys(t, BOAT)) for t in tb]),
          T_BOAT_OFF, 0.4)

    # ---- 69: two dollops patch the dam; 72: the butter melts; the waltz comes home ----
    for i, (t, p) in enumerate(zip(T_PATCH, (RIM_L - 20, RIM_R + 20))):
        M.add('fx', plop(220, seed=80 + i), t, 1.0, pan_at(p))
        M.add('drums', timp.play(95), t, 0.5, pan_at(p))
    M.add('bells', glock.play(n('A5'), 90), T_BUTTER, 0.7, pm)
    for i in range(10):
        M.add('bells', glock.play([74, 78, 81, 86, 81, 78, 74, 69, 66, 62][i], 70 - 3 * i), T_BUTTER + 0.3 + 0.22 * i,
              0.5, pm)
    M.add('fx', tri.play(80), T_BUTTER, 0.4, pm)
    t_r = T_BUTTER                                  # 72 = bar 48: the reprise
    oom(t_r, WALTZ_CH + WALTZ_CH[:2], vel=88)
    tune(WALTZ, t_r, vln, 'strings', 95, gain=1.3)
    tune(WALTZ, t_r, clar, 'tune', 85, pan=-0.15)
    tune(WALTZ, t_r, flute, 'tune', 75, gain=0.5, shift=12, pan=0.15)
    for j, c in enumerate(WALTZ_CH):
        M.add('strings', cello.play(ROOT[c] + 12, 70, dur=BAR), t_r + j * BAR, 0.6)
        M.add('brass', horn.play(CH[c][0], 75, dur=BAR), t_r + j * BAR, 0.4, -0.2)
    tend = t_r + 8 * BAR
    hold = D - tend - 0.5
    for m, inst, bus, v in ((n('D2'), cello, 'strings', 80), (n('A3'), horn, 'brass', 85), (n('F#4'), clar, 'tune', 80),
                            (n('D5'), vln, 'strings', 80), (n('A4'), flute, 'tune', 65)):
        M.add(bus, inst.play(m, v, dur=hold, release=1.5), tend, 1.0)
    M.add('bass', tuba_s.play(n('D2'), 95, dur=hold), tend, 0.8)
    for i, m in enumerate((50, 57, 62, 66, 69, 74, 78, 81, 86, 90)):     # gold runs the length of the roof
        M.add('harp', harp.play(m, 85), tend + 0.17 * i, 0.9, pan_at(-60 + 1500 * 0.17 * i))
    ts = np.linspace(T_SWEEP, T_SWEEP + 1.8, 20)
    M.add('fx', moving(whoosh(1.8, 400, 3000, 0.4, seed=8), T_SWEEP, ts, [pan_at(-60 + 1500 * (t - T_SWEEP)) for t in ts]),
          T_SWEEP, 0.6)
    M.add('drums', crash.play(100), T_SWEEP + 1.7, 0.6, pan_at(2500))
    M.add('drums', timp.play(110), T_SWEEP, 0.7)
    M.add('bells', glock.play(n('D6'), 70), tend + 1.5, 0.5, pm)
