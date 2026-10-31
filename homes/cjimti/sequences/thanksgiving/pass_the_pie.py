"""Pass the Pie: Dessert at a 120 BPM barn-dance. The dinner bell rings and seven places pop up round the
table (both wings and the porch sides), a ripple each, while the pie fills the Porch Front a chunk per
beat. It spins on the lazy Susan, cream squiggles back and forth across it, the knife glints, and seven
chops on the eighth notes cut it. Then it is passed: slices leave the pie left and right and hop seat to
seat on the beat until everyone has one, and the table starts passing them on, the whole row sliding
right, then left, faster and faster, the end slices flying off past the free end of Right and the Side
corner and bouncing back, until STOP. Chomps run round the table in waves, faster each time, to one big
gulp. The last slice glows on the porch like a heartbeat. Two hands creep toward it, freezing whenever
the other moves, the beat quickening, until they are a step apart and everything holds still. The dog
streaks in from the end of Right, snatches it and runs out up the Side, and the hands bonk. The family
chases him round the house three times; he skids to a stop on the porch with them piled up behind, and
the oven timer dings: a second pie, so big it fills the whole house and spins to the end."""
import numpy as np
from pixelhome.fx import DT, hexc, light, perc, keys, smoothstep, Flicker, nframes

CODE = 'TG06'
TITLE = 'Pass the Pie'
KIND = 'show'
DESCRIPTION = ('The porch is a pumpkin pie, cut and passed hand to hand round the table. Two hands creep toward the '
               'last slice, the dog snatches it, everyone chases him round the house, and out comes a second pie.')
VOICEOVER = "Save room, everyone: the pie is out, and the dog has plans."

PUMPKIN = hexc('#ff5200')
CRUST = hexc('#ffa030')
CREAM = hexc('#ffd8a8')
AMBER = hexc('#ff8a18')
CRANBERRY = hexc('#c0102a')
GOLD = hexc('#ffb000')
BROWN = hexc('#5a1c04')
WHITE = hexc('#fff0d8')
DOG = hexc('#ffe0a0')
FAMILY = np.array([CRANBERRY, GOLD, AMBER, hexc('#ff3020'), CREAM, PUMPKIN, GOLD])
D = 90.0
SEED = 26
BEAT = 0.5                                  # 120 BPM
BAR = 4 * BEAT


def at(bar, beat=0.0):
    return bar * BAR + beat * BEAT


P0, P1 = 1320.0, 1652.0                     # the pie on the Porch Front
MID = (P0 + P1) / 2
W = (P1 - P0) / 8
CENTRES = P0 + W * (np.arange(8) + 0.5)
SEATS = [600.0, 800.0, 1050.0, 1220.0, MID, 1790.0, 2100.0, 2380.0]   # seat index 4 is the pie
SEAT_X = [-2, -1, 0, 1, 2, 3, 4, 5, 6, 7, 8, 9]
SEAT_D = [190.0, 400.0] + SEATS + [2640.0, 2900.0]                    # past the ends: the Side corner, off Right
HOME = {0: 0, 1: 1, 2: 2, 3: 3, 5: 5, 6: 6, 7: 7}                    # slice k ends at seat k; slice 4 is the last

PLATES = [at(0, 1 + k * 0.5) for k in range(7)]                       # places pop up round the table
T_FILL, T_SPIN, T_CREAM, T_GLINT, T_CHOP = at(2), at(4), at(6), at(7), at(8)
CHOPS = [T_CHOP + k * BEAT / 2 for k in range(7)]
T_PASS = at(9)
LEAVE = {0: at(9), 7: at(9.5), 1: at(10), 6: at(10.5), 2: at(11), 5: at(11.5), 3: at(12)}   # off the plate
HOP = BEAT                                  # a seat a beat
T_SHIFT = at(13)
SHIFTS = ([(at(13, k), d) for k, d in enumerate((1, 1, -1, -1))] +
          [(at(14, k), d) for k, d in enumerate((-1, -1, 1, 1))] +
          [(at(15, k / 2), d) for k, d in enumerate((1, 1, -1, -1, -1, -1, 1, 1))] +
          [(at(16, k / 2), d) for k, d in enumerate((1, 1, 1, -1, -1, -1, -1, 1))])
T_STOP = at(17)
ORDER = [0, 1, 2, 3, 5, 6, 7]               # occupied seats, left to right
BITES = ([(at(17, 1) + 0.25 * j, s) for j, s in enumerate(ORDER)] +
         [(at(18, 1) + 0.25 * j, s) for j, s in enumerate(ORDER[::-1])] +
         [(at(19, 1) + 0.25 * j, s) for j, s in enumerate(ORDER)] +
         [(at(20, 1) + 0.125 * j, s) for j, s in enumerate(ORDER[::-1])] +
         [(at(21), s) for s in ORDER])
NBITES = 5
T_GULP, T_LAST = at(21, 2), at(23)
# the two hands for the last slice: (time, path distance), a step per beat, freezing while the other moves
LH = [(T_LAST, 1220), (at(24), 1220), (at(24, 0.25), 1250), (at(24, 1.25), 1280), (at(24, 2.25), 1310),
      (at(24, 3.25), 1340), (at(25, 2), 1340), (at(25, 2.5), 1300), (at(26), 1300), (at(27), 1300),
      (at(27, 0.25), 1325), (at(27, 1), 1325), (at(27, 1.25), 1350), (at(27, 2), 1350), (at(27, 2.25), 1375),
      (at(27, 3), 1375), (at(27, 3.25), 1400), (at(28), 1400), (at(28, 3.5), 1435), (at(29, 3.6), 1435),
      (at(30), 1478), (at(30, 0.3), 1478), (at(30, 1.5), 1300)]
RH = [(T_LAST, 1790), (at(25), 1790), (at(25, 0.2), 1770), (at(25, 1.5), 1770), (at(25, 1.7), 1790), (at(26), 1790), (at(26, 0.25), 1755), (at(26, 1.25), 1720), (at(26, 2.25), 1685),
      (at(26, 3.25), 1650), (at(27), 1650), (at(27, 0.75), 1625), (at(27, 1.5), 1625), (at(27, 1.75), 1600),
      (at(27, 2.5), 1600), (at(27, 2.75), 1575), (at(27, 3.5), 1575), (at(27, 3.75), 1560), (at(28), 1560),
      (at(28, 3.5), 1537), (at(29, 3.6), 1537), (at(30), 1494), (at(30, 0.3), 1494), (at(30, 1.5), 1680)]
LH_FREEZE = at(25)                          # the left hand freezes when the right one twitches
T_STILL = at(29)                            # nose to nose: a beat of stillness
T_DOG, T_GRAB, T_BONK = at(29, 2), at(30) - 0.04, at(30) + 0.06
T_DOGOUT = at(30.65)
LAPS = [(at(31), at(32.5), 0.0), (at(32.75), at(34.25), 0.0), (at(34.5), at(35.25), MID)]   # in from Right, to
T_SKID, T_DING, T_PIE2, T_SPIN2, T_END = at(35.25), at(36), at(36), at(38), at(44)
def heart_times():
    """Heartbeats of the last slice: one a beat, two a beat from bar 27."""
    t, out = T_LAST, []
    while t < T_STILL:
        out.append(t)
        t += BEAT if t < at(27) else BEAT / 2
    return out


HEARTS = heart_times()


def seat_d(x):
    return np.interp(x, SEAT_X, SEAT_D)


def slice_index(k, t):
    """Seat coordinate of slice k at time t (4 = the pie)."""
    if k == 4:
        return 4.0
    dest, side = HOME[k], (-1 if k < 4 else 1)
    hops = abs(dest - 4)
    t0 = LEAVE[k]
    done = sum(smoothstep(t0 + j * HOP, t0 + j * HOP + 0.32, t) for j in range(hops))
    x = 4 + side * done
    for ts, dd in SHIFTS:
        e = 0.2 if ts >= at(15) else 0.36
        x += dd * smoothstep(ts, ts + e, t)
    return x


def slice_pos(k, t):
    x = slice_index(k, t)
    off = (CENTRES[k] - MID) * (1 - min(1.0, max(0.0, (t - LEAVE.get(k, 1e9)) / 0.32))) if k != 4 else CENTRES[4] - MID
    return float(seat_d(x)) + off


def dog_x(t):
    """The dog: in from the end of Right to the pie, out up the Side; then three laps, in from Right each time."""
    if t < T_DOG:
        return np.nan
    if t < T_DOGOUT:
        return float(np.interp(t, [T_DOG, T_GRAB, T_GRAB + 0.12, T_DOGOUT], [2650, MID + 6, MID - 6, -60]))
    for t0, t1, end in LAPS:
        if t0 <= t < t1 + (0 if end == 0 else 100):
            if end == 0:
                return float(np.interp(t, [t0, t1], [2650, -60]))
            return float(2650 + (end - 2650) * (1 - (1 - min(1.0, (t - t0) / (t1 - t0))) ** 2))
    return np.nan


def render(G, seed=SEED):
    rng = np.random.default_rng(seed)
    F = nframes(D)
    out = np.zeros((F, G.N, 3))
    n = G.N
    d = G.pd[G.path]
    idx = np.arange(n)
    side, left, right = idx < 81, (idx >= 81) & (idx < 179), idx >= 381
    shimmer = Flicker(rng, n, 0.3, 1.5)
    crumbs = rng.uniform(150, 450, (len(BITES), 2))
    bites_done = lambda s, t: sum(1 for tb, ss in BITES if ss == s and tb <= t)

    def slice_px(c, k, eaten=0.0, lvl=1.0):
        """Slice k centred at c: crust at the rim end, filling, a dab of cream; bites come off the tip end."""
        rim = 1 if CENTRES[k] < MID else -1
        o = (d - c) * -rim                                   # o<0 toward the crust
        half = W / 2 - 1.0
        keep = half - eaten * 2 * half
        inside = np.clip((half + o) / 2.5 + 0.5, 0, 1) * np.clip((keep - o) / 2.5 + 0.5, 0, 1)
        crust = np.exp(-((o + half - 3) / 5) ** 2)
        return (light(PUMPKIN, lvl * inside * 0.85) + light(CRUST, lvl * inside * 0.85 * crust) +
                light(CREAM, lvl * inside * 0.8 * np.exp(-((o - 3) / 4) ** 2) * (eaten < 0.4)))

    def flash_at(x, t, t0, col=WHITE, lvl=0.9, w=18.0, decay=0.1):
        a = t - t0
        if not 0 <= a < 6 * decay:
            return 0
        return light(col, lvl * np.exp(-a / decay) * np.exp(-((d - x) / w) ** 2))

    def ripple(x, t, t0, col, lvl=0.8, speed=700.0, life=0.6):
        a = t - t0
        if not 0 <= a < life:
            return 0
        return light(col, lvl * np.exp(-a / (life / 3)) * np.exp(-((np.abs(d - x) - speed * a) / 22) ** 2))

    def giant_pie(t, R, spin, lvl=1.0):
        """A pie so big it covers |d - MID| < R: wedges with crust ridges and cream, turning by `spin`."""
        u = d - MID + spin
        wedge = (u / 120) % 1
        inside = np.clip((R - np.abs(d - MID)) / 20, 0, 1)
        ridge = np.exp(-(np.minimum(wedge, 1 - wedge) / 0.06) ** 2)
        dab = np.exp(-((wedge - 0.5) / 0.08) ** 2)
        return (light(PUMPKIN, lvl * inside * (0.7 + 0.1 * shimmer(t))) + light(CRUST, lvl * inside * ridge) +
                light(CREAM, 0.85 * lvl * inside * dab))

    for f in range(F):
        t = f * DT
        beat = np.exp(-((t % BEAT) / 0.14))
        fade_all = smoothstep(0, 0.5, t) * (1 - smoothstep(D - 1.2, D, t))
        bed = 0.15 * (1 + 0.15 * shimmer(t))
        if T_STILL <= t < T_GRAB:
            bed *= 0.2
        elif T_LAST <= t < T_GRAB:
            bed *= 0.5
        buf = light(BROWN, bed * np.ones(n))
        seat_lvl = keys(t, [(0, 0), (PLATES[0], 0.3), (T_LAST, 0.3), (T_LAST + 1, 0.12), (T_GRAB, 0.12),
                            (T_GRAB + 1, 0.0), (T_END, 0.0)])

        # ---- 0-8: the dinner bell; places pop up round the table; the pie fills a chunk per beat ----
        for j, tp in enumerate(PLATES):
            s = ORDER[j]
            buf += ripple(SEATS[s], t, tp, AMBER, 0.9, 500, 0.8) + flash_at(SEATS[s], t, tp, GOLD, 0.9, 14, 0.15)
        for j, s in enumerate(ORDER):                        # a warm pool of table round every place, breathing
            pool = smoothstep(PLATES[j], PLATES[j] + 0.3, t) * (seat_lvl / 0.3) * (0.36 + 0.12 * beat)
            buf += light(GOLD, pool * np.exp(-((d - SEATS[s]) / 95) ** 2))
            buf += light(AMBER, seat_lvl * np.exp(-((d - SEATS[s]) / 9) ** 2))
        whole = T_FILL <= t < T_PASS
        if whole:
            k = (t - T_FILL) / BEAT
            r = (P1 - P0) / 2 * min(1.0, (np.floor(k) + smoothstep(0, 0.4, k % 1)) / 8)
            spin = 0.0
            if T_SPIN <= t:                                  # the lazy Susan: up to speed and back
                spin = 520 * (t - T_SPIN) - 260 * (t - T_SPIN) ** 2 / (T_CREAM - T_SPIN) if t < T_CREAM else 260 * (T_CREAM - T_SPIN)
            on = np.clip((r - np.abs(d - MID)) / 4, 0, 1)
            u = (d - P0 + spin) % (P1 - P0)
            wedge = (u / W) % 1
            ridge = np.exp(-(np.minimum(wedge, 1 - wedge) / 0.1) ** 2) * (T_SPIN <= t < T_CREAM)
            rim = np.exp(-((np.abs(d - MID) - r + 4) / 6) ** 2)
            buf *= (1 - on)[:, None]
            buf += light(PUMPKIN, on * (0.7 + 0.1 * shimmer(t))) + light(CRUST, on * np.maximum(0.85 * rim, 0.8 * ridge))
            if t < T_SPIN:                                   # heat shimmer rising out of the oven
                buf += light(GOLD, 0.35 * on * (0.5 + 0.5 * np.sin((d - MID) / 12 - 9 * t)) ** 4)
            if T_CREAM <= t:                                 # cream squiggles back and forth on the eighths
                for j in range(8):
                    tj = T_CREAM + j * BEAT / 2
                    xj = CENTRES[j if j % 2 == 0 else 7 - j]
                    if t >= tj:
                        sq = 1 + 0.6 * np.exp(-(t - tj) / 0.15) * np.cos(25 * (t - tj))
                        buf += light(CREAM, on * 0.85 * np.exp(-((d - xj) / (4 * sq)) ** 2))
                if t < T_GLINT:
                    a = (t - T_CREAM) / (BEAT / 2)
                    x = np.interp(a % 2, [0, 1, 2], [P0, P1, P0])
                    buf += light(WHITE, 0.8 * np.exp(-((d - x) / 10) ** 2))
            if T_GLINT <= t < T_CHOP:                        # the knife: a glint scanning, the wings hold their breath
                a = (t - T_GLINT) / BAR
                x = P0 + (P1 - P0) * (0.5 - 0.5 * np.cos(2 * np.pi * 2 * a))
                buf += light(WHITE, 0.9 * np.exp(-((d - x) / 7) ** 2))
                buf += light(WHITE, 0.5 * np.exp(-((d - x) / 40) ** 2))
            for j, tc in enumerate(CHOPS):                   # chop: a slash, a dark gap, the house jolts
                a = t - tc
                gap = P0 + W * (j + 1)
                if a >= 0:
                    buf *= 1 - 0.95 * smoothstep(0, 0.06, a) * np.exp(-((d - gap) / 2.2) ** 2)[:, None]
                    if a < 0.25:
                        buf += light(WHITE, np.exp(-a / 0.05) * np.exp(-((d - gap) / 8) ** 2))
                        buf += light(WHITE, 0.35 * np.exp(-a / 0.07) * (left | right))
        # ---- 18-34: passing, then the whole table passing right and left ----
        if T_PASS <= t < T_GRAB:
            for k in range(8):
                if k == 4:
                    continue
                c = slice_pos(k, t)
                s = HOME[k]
                eaten = min(1.0, bites_done(s, t) / NBITES)
                if eaten < 1:
                    trail = 0
                    for j in range(1, 7):                    # a smear while it moves
                        cj = slice_pos(k, t - j * 0.03)
                        if abs(cj - c) > 3:
                            trail = trail + light(CRUST, 0.65 * (1 - j / 7) * np.exp(-((d - cj) / 12) ** 2))
                    buf += slice_px(c, k, eaten) + trail
            buf += slice_px(CENTRES[4], 4, 0.0, 1.0)
            # landings: the seat it lands on flashes
            for k in range(8):
                if k == 4 or t < LEAVE[k]:
                    continue
                hops = abs(HOME[k] - 4)
                for j in range(hops):
                    tj = LEAVE[k] + j * HOP + 0.32
                    buf += flash_at(seat_d(4 + (-1 if k < 4 else 1) * (j + 1)), t, tj, GOLD, 0.7, 14, 0.12)
            for ts, dd in SHIFTS:                            # the whole row slides: that wing flashes
                a = t - ts
                if 0 <= a < 0.4:
                    wing = right if dd > 0 else (left | side)
                    buf += light(GOLD if dd > 0 else AMBER, 0.75 * np.exp(-a / 0.12) * wing)
            if T_STOP <= t < T_STOP + 0.5:                   # STOP
                buf += light(WHITE, 0.6 * np.exp(-(t - T_STOP) / 0.12) * np.ones(n))
            for j, (tb, s) in enumerate(BITES):              # chomps, and crumbs flying both ways
                a = t - tb
                if 0 <= a < 0.6:
                    x = SEATS[s]
                    buf += flash_at(x, t, tb, CREAM, 1.0, 26, 0.1)
                    buf += ripple(x, t, tb, AMBER, 0.7, 600, 0.5)
                    for e in (-1, 1):
                        buf += light(CRUST, 0.75 * np.exp(-a / 0.2) * np.exp(-((d - x - e * crumbs[j, (e + 1) // 2] * (1 - np.exp(-a / 0.2))) / 5) ** 2))
            if T_GULP <= t < T_LAST + 1:                     # mmm: the table glows, breathing
                a = t - T_GULP
                buf += light(AMBER, (0.45 * np.exp(-a / 0.3) + 0.2 * (0.5 + 0.5 * np.cos(2 * np.pi * a / BAR))) *
                             (1 - smoothstep(T_LAST, T_LAST + 1, t)) * (np.abs(d - MID) > 200))
            # the last slice: a heartbeat, faster as the hands close in
            if T_LAST <= t:
                hb = min(1.0, sum(np.exp(-(t - h) / 0.09) for h in HEARTS if 0 <= t - h < 0.5))
                buf += light(GOLD, (0.25 + 0.6 * hb) * np.exp(-((d - MID) / 60) ** 2))
                lx, rx = keys(t, LH), keys(t, RH)
                buf += light(CRANBERRY, 0.95 * np.exp(-((d - lx) / 11) ** 2)) + light(GOLD, 0.95 * np.exp(-((d - rx) / 11) ** 2))
                for x in (lx, rx):                           # fingers
                    buf += light(CREAM, 0.5 * np.exp(-((d - x - (14 if x == lx else -14)) / 5) ** 2))
                if T_LAST + 0.5 <= t < T_STILL:              # the family leans in: stripes crawl toward the porch
                    conv = np.where(d < 1100, 892 - d, d - 2036)
                    ph = (t - T_LAST) * (1.0 if t < at(27) else 2.0) + (at(27) - T_LAST) * (0.0 if t < at(27) else -1.0)
                    stripes = (0.5 + 0.5 * np.cos(2 * np.pi * (conv / 110 + ph))) ** 3 * (conv > 0)
                    lean = smoothstep(T_LAST + 0.5, T_LAST + 2, t) * (0.25 + 0.3 * smoothstep(T_LAST, T_STILL, t))
                    buf += light(AMBER, lean * (0.6 + 0.4 * hb) * stripes)
                a = t - LH_FREEZE                            # caught! a flicker of the hand that froze
                if 0 <= a < 0.5:
                    buf += light(WHITE, 0.6 * np.exp(-a / 0.12) * np.exp(-((d - lx) / 25) ** 2))
        # ---- the dog ----
        x = dog_x(t)
        if not np.isnan(x):
            buf += light(DOG, 1.0 * np.exp(-((d - x) / 14) ** 2))
            for j in range(1, 14):                           # a speed streak
                xj = dog_x(t - j * DT)
                if not np.isnan(xj) and abs(xj - x) < 400:
                    buf += light(GOLD, 0.7 * (1 - j / 14) * np.exp(-((d - xj) / 10) ** 2))
            if t >= T_GRAB:                                  # the slice in his mouth, ahead of him
                v = dog_x(t + 0.02) - x if not np.isnan(dog_x(t + 0.02)) else -1
                buf += slice_px(x + (22 if v >= 0 else -22), 4, 0.0, 1.0)
            if t >= LAPS[-1][1]:                             # he sits and wags
                buf += light(DOG, 0.5 * np.exp(-((d - x - 25 - 8 * np.sin(2 * np.pi * 4 * t)) / 6) ** 2))
        buf += flash_at(MID, t, T_BONK, WHITE, 1.0, 40, 0.12)
        buf += ripple(MID, t, T_BONK, CREAM, 0.9, 1400, 1.0)
        # ---- the chase: the family runs after him, a train of colours, the house thumping on the beat ----
        if LAPS[0][0] - 0.5 <= t < T_DING:
            buf += light(AMBER, (0.14 + 0.2 * beat) * smoothstep(LAPS[0][0] - 0.5, LAPS[0][0], t) * np.ones(n))
        for t0, t1, end in LAPS:
            for j in range(7):
                tj = t - 0.35 - 0.16 * j
                if t0 <= tj < t1 + (0 if end == 0 else 100):
                    if end == 0:
                        xj = float(np.interp(tj, [t0, t1], [2650, -60]))
                    else:
                        xj = max(dog_x(tj) if not np.isnan(dog_x(tj)) else MID, MID + 45 + 30 * j)
                    buf += light(FAMILY[j], 1.0 * np.exp(-((d - xj) / 16) ** 2))
            if end == 0:                                     # every lap the wing it leaves from flashes
                buf += flash_at(2500, t, t0, GOLD, 0.8, 120, 0.2)
        buf += flash_at(MID + 120, t, T_SKID + 0.4, WHITE, 0.9, 120, 0.15)     # the pile-up behind him
        # ---- 72: ding! a second pie, so big it fills the house, spinning to the end ----
        if T_DING <= t:
            a = t - T_DING
            buf += flash_at(MID, t, T_DING, GOLD, 0.9, 200, 0.2)
            k = (t - T_PIE2) / BEAT
            R = 1400 * min(1.0, (np.floor(k) + smoothstep(0, 0.4, k % 1)) / 8)
            spin = 0.0 if t < T_SPIN2 else 160 * (t - T_SPIN2) + 30 * np.sin(2 * np.pi * (t - T_SPIN2) / BAR)
            lvl = (0.85 + 0.15 * beat) * (1 - smoothstep(T_END + 0.5, D, t))
            pie = giant_pie(t, R, spin, lvl)
            cover = np.clip((R - np.abs(d - MID)) / 20, 0, 1)[:, None]
            buf = buf * (1 - cover) + pie
            buf += light(DOG, np.exp(-((d - MID) / 12) ** 2) * (t < T_SPIN2 + 2))
            for j in range(7):                               # everyone cheers on the beat
                tj = T_PIE2 + j * BEAT
                buf += ripple(SEATS[ORDER[j]], t, tj, WHITE, 0.6, 900, 0.6)
            if t >= T_SPIN2:                                 # laughter: the wings bounce in turn
                b = int((t - T_SPIN2) / BEAT)
                wing = right if b % 2 else (left | side)
                buf += light(CREAM, 0.35 * beat * wing * (t < T_END))
            if t >= T_END:
                buf += light(GOLD, 0.6 * np.exp(-(t - T_END) / 0.4) * np.ones(n))
        out[f][G.path] = np.clip(buf * fade_all, 0, 1)
    return out


# ---------------------------------------------------------------- music ----------------------------------------------
# A barn-dance rag in Bb at 120 BPM: upright piano oom-pah (bass on 1 and 3, chords on 2 and 4), contrabass pizz, a
# clarinet on the tune, xylophone and glock. The dinner bell is a triangle; each place that pops up a marimba note up
# the scale; the pie fills on a harp, a note a beat. The lazy Susan spins on the A strain, the cream is eight squirts
# (bloops climbing), the knife glint a tremolo and a ting, the chops seven claves down the scale. Passing is plucked:
# a marimba (left) or violin pizz (right) where each slice lands, over the B strain. The table's sliding is slide
# whistles, up for right and down for left, each panned to the wing that flashes; STOP is a chord. Every chomp is a
# clave where it happens, the gulp a bassoon. The last slice: a cello tremolo, a heartbeat on timpani, the two hands
# tiptoeing on cello and violin pizz; a beat of silence; the dog scrabbles in on woodblocks, snatches (slapstick),
# bonk. The chase is a galop at full tilt, woodblock claws panned with the dog, a whistle each time he comes round;
# the skid and pile-up, a ding, a harp up for the second pie, and the A strain tutti to the end.

CH = {'Bb': (46, 50, 53), 'Eb': (46, 51, 55), 'F7': (45, 48, 51), 'F': (45, 48, 53), 'C7': (46, 48, 52),
      'Gm': (46, 50, 55), 'Cm': (48, 51, 55)}
ROOT = {'Bb': ('Bb1', 'F2'), 'Eb': ('Eb2', 'Bb1'), 'F7': ('F1', 'C2'), 'F': ('F1', 'C2'), 'C7': ('C2', 'G1'),
        'Gm': ('G1', 'D2'), 'Cm': ('C2', 'G1')}
SCALE = [58, 60, 62, 63, 65, 67, 69, 70, 72, 74, 75, 77]     # Bb major from Bb3
TUNE_A = [[(0, 'D5', 0.5), (0.5, 'Eb5', 0.5), (1, 'E5', 0.5), (1.5, 'F5', 1), (2.5, 'D5', 0.5), (3, 'Bb4', 1)],
          [(0, 'C5', 0.5), (0.5, 'D5', 0.5), (1, 'Eb5', 1), (2, 'C5', 0.5), (2.5, 'A4', 0.5), (3, 'F4', 1)],
          [(0, 'D5', 0.5), (0.5, 'Eb5', 0.5), (1, 'E5', 0.5), (1.5, 'F5', 1), (2.5, 'G5', 0.5), (3, 'F5', 1)],
          [(0, 'Eb5', 0.5), (0.5, 'C5', 0.5), (1, 'A4', 0.5), (1.5, 'C5', 0.5), (2, 'Bb4', 2)]]
CHORDS_A = [('Bb', 'Bb'), ('F7', 'F7'), ('Bb', 'Eb'), ('F7', 'Bb')]
TUNE_B = [[(0, 'F4', 1), (1, 'A4', 0.5), (1.5, 'Bb4', 0.5), (2, 'C5', 1), (3, 'A4', 1)],
          [(0, 'Bb4', 1), (1, 'G4', 0.5), (1.5, 'A4', 0.5), (2, 'Bb4', 2)],
          [(0, 'F4', 1), (1, 'A4', 0.5), (1.5, 'Bb4', 0.5), (2, 'C5', 1), (3, 'Eb5', 1)],
          [(0, 'D5', 1), (1, 'C5', 1), (2, 'Bb4', 2)]]
CHORDS_B = [('F7', 'F7'), ('Bb', 'Eb'), ('F7', 'F7'), ('Bb', 'Bb')]
TUNE_C = [[(e / 2, m, 0.5) for e, m in enumerate(('F5', 'E5', 'F5', 'D5', 'Bb4', 'D5', 'F5', 'Bb5'))],
          [(e / 2, m, 0.5) for e, m in enumerate(('A5', 'G5', 'F5', 'Eb5', 'D5', 'C5', 'Bb4', 'A4'))],
          [(e / 2, m, 0.5) for e, m in enumerate(('G4', 'A4', 'Bb4', 'C5', 'D5', 'Eb5', 'E5', 'F5'))],
          [(0, 'F5', 0.5), (0.5, 'C5', 0.5), (1, 'A4', 0.5), (1.5, 'C5', 0.5), (2, 'F5', 1), (3, 'F4', 1)]]
CHORDS_C = [('Bb', 'Bb'), ('Eb', 'F7'), ('Eb', 'C7'), ('F7', 'F7')]
TUNE_E = [[(0, 'Bb4', 0.5), (0.5, 'D5', 0.5), (1, 'F5', 1), (2, 'Eb5', 0.5), (2.5, 'C5', 0.5), (3, 'A4', 1)],
          [(0, 'Bb4', 0.5), (0.5, 'C5', 0.5), (1, 'D5', 0.5), (1.5, 'Eb5', 0.5), (2, 'F5', 2)],
          [(0, 'G5', 0.5), (0.5, 'F5', 0.5), (1, 'Eb5', 0.5), (1.5, 'D5', 0.5), (2, 'C5', 1), (3, 'A4', 1)],
          [(0, 'Bb4', 1), (1, 'F4', 1), (2, 'Bb4', 1)]]
CHORDS_E = [('Bb', 'Eb'), ('Bb', 'F7'), ('Eb', 'F7'), ('Bb', 'Bb')]


def score(M, G):
    from pixelhome.audio import SR, note, slide, whoosh
    n = note
    clar = M.sampler('Woodwinds/Clarinet/susLong/*.wav', tune=-12)
    clst = M.sampler('Woodwinds/Clarinet/stac/*.wav', tune=-12)
    bsn = M.sampler('Woodwinds/Bassoon/stac/*.wav', tune=-12)
    cello = M.sampler('Strings/Cello Section/susvib/*.wav', tune=-12)
    trem = M.sampler('Strings/Cello Section/trem/*.wav', tune=-12)
    cpizz = M.sampler('Strings/Cello Section/pizzT/*.wav', tune=-12)
    vpizz = M.sampler('Strings/Violin Section/Pizz/*.wav', tune=-12)
    bass = M.sampler('Strings/Solo Contrabass/Pizz/*.wav', tune=-12)
    piano = M.sampler('Keys/Upright Nr1/*.wav')
    harp = M.sampler('Strings/Harp/*.wav')
    mar = M.sampler('Percussion/Marimba/*.wav', tune=-12)
    xylo = M.sampler('Percussion/Xylo/*.wav', tune=-12)
    glock = M.sampler('Percussion/Glock/*.wav', tune=-12)
    wood = M.hits('VSCO 1 Percussion/varWood/wood_click*.wav')
    clave = M.hits('Percussion/Claves1_Hit*.wav')
    tri = M.hits('Percussion/Triangle3-Hit_v*.wav')
    slap = M.hits('VSCO 1 Percussion/varWood/slapstick[0-9].wav')
    log = M.hits('VSCO 1 Percussion/varWood/log_drum/*.wav')
    timp = M.hits('Percussion/Timpani/Timpani1_Hit*.wav')
    troll = M.hits('Percussion/Timpani/Rolls/*.wav')
    bd = M.hits('Percussion/BDrumNewhit_v[4-7]*.wav')
    crash_s = M.hits('Percussion/cymbal-crashshort*.wav')

    for name, gain, rev in (('melody', 0.34, 0.22), ('pluck', 0.42, 0.2), ('bass', 0.5, 0.08), ('keys', 0.28, 0.18),
                            ('strings', 0.24, 0.3), ('harp', 0.34, 0.3), ('mallet', 0.36, 0.2), ('perc', 0.5, 0.12),
                            ('drums', 0.45, 0.18), ('fx', 0.2, 0.25)):
        M.bus(name, gain=0.78 * gain, reverb=rev)

    order = np.argsort(G.pd)
    xs, ds = G.pos[order, 0], G.pd[order]
    x0, x1 = xs.min(), xs.max()
    L = G.length

    def pan_at(dd):                          # path distance -> left/right across the facade, as seen from the street
        x = np.interp(np.clip(dd, 0, L), ds, xs)
        return float(0.85 * (2 * (x - x0) / (x1 - x0) - 1))

    def travel(sig, d0, d1):                # a sound that moves along the roofline from d0 to d1 while it plays
        a = (np.linspace(pan_at(d0), pan_at(d1), sig.shape[1]) + 1) * np.pi / 4
        return sig * np.sqrt(2) * np.vstack([np.cos(a), np.sin(a)])

    def bloop(seconds=0.12, f0=260.0):      # a dollop landing: a quick rising sine
        tt = np.arange(int(seconds * SR)) / SR
        ph = 2 * np.pi * np.cumsum(f0 * (3.2 ** np.clip(tt / 0.07, 0, 1))) / SR
        s = np.sin(ph) * np.clip(tt / 0.004, 0, 1) * np.exp(-tt / 0.045)
        return np.vstack([s, s])

    pie = pan_at(MID)

    def rag(k0, chords, vel=80, offbeats=False, gain=1.0):
        """Upright piano oom-pah and contrabass from bar k0: chords is [(first half, second half)] per bar."""
        for j, (c1, c2) in enumerate(chords):
            for h, c in enumerate((c1, c2)):
                t = at(k0 + j, 2 * h)
                r = ROOT[c][h]
                M.add('bass', bass.play(n(r) + 12, vel + 15), t, gain, -0.1)
                M.add('keys', piano.play(n(r) + 12, vel), t, 0.8 * gain, -0.1)
                for e in ((0.5, 1, 1.5) if offbeats else (1,)):
                    for m in CH[c]:
                        M.add('keys', piano.play(m + 12, vel - 8), t + e * BEAT, 0.6 * gain, 0.15)

    def tune(bars, k0, inst, bus='melody', vel=100, pan=-0.1, gain=1.0, long=None):
        for j, b in enumerate(bars):
            for e, m, ln in b:
                pl = long if (long is not None and ln >= 1) else inst
                M.add(bus, pl.play(n(m), vel, dur=ln * BEAT * 0.9, release=0.12), at(k0 + j, e), gain, pan)

    def kit(k0, bars, vel=90):              # brushes of a barn dance: a bass drum on 1 and 3, woodblock offbeats
        for j in range(bars):
            for e in range(4):
                t = at(k0 + j, e)
                if e % 2 == 0:
                    M.add('drums', bd.play(vel), t, 0.7)
                else:
                    M.add('perc', wood.play(vel - 10), t, 0.35, 0.3)
                M.add('perc', wood.play(vel - 35), t + BEAT / 2, 0.2, -0.3)

    # ---- 0-8: the dinner bell, places round the table, the pie fills ----
    for k in range(3):
        M.add('perc', tri.play(105 - 10 * k), 0.05 + 0.25 * k, 0.7, pie)
    for j, tp in enumerate(PLATES):
        M.add('mallet', mar.play(SCALE[j], 96), tp, 0.9, pan_at(SEATS[ORDER[j]]))
        M.add('perc', wood.play(80), tp, 0.4, pan_at(SEATS[ORDER[j]]))
    rag(1, [('Bb', 'Bb')], 70)
    for k in range(8):                       # a harp note a beat as the pie fills out from the middle
        M.add('harp', harp.play(SCALE[k] - 12, 80 + 3 * k), T_FILL + k * BEAT, 0.9, pie)
    rag(2, [('Bb', 'Eb'), ('F7', 'F7')], 72)
    M.add('strings', cello.play(n('Bb2'), 60, dur=4.0, release=0.5), T_FILL, 0.8, pie)

    # ---- 8-12: the lazy Susan spins on the A strain; 12-14 the cream; 14-18 the knife ----
    rag(4, CHORDS_A[:2], 82)
    kit(4, 2, 88)
    tune(TUNE_A[:2], 4, clst, vel=105)
    tune(TUNE_A[:2], 4, xylo, 'mallet', 80, 0.15, 0.4)
    for k in range(16):                      # the spin: a glock arpeggio sliding across the porch
        t = T_SPIN + k * BEAT / 4
        M.add('mallet', glock.play(CH['Bb'][k % 3] + 24, 70), t, 0.3, pan_at(P0 + (P1 - P0) * ((k % 4) / 3)))
    rag(6, [('Bb', 'Eb')], 82)
    kit(6, 1, 88)
    for j in range(8):                       # cream: eight squirts, climbing
        tj = T_CREAM + j * BEAT / 2
        xj = CENTRES[j if j % 2 == 0 else 7 - j]
        M.add('fx', whoosh(0.18, 2500, 800, 0.6, seed=10 + j), tj - 0.1, 0.6, pan_at(xj))
        M.add('fx', bloop(0.12, 220 * 2 ** (j / 12)), tj, 2.0, pan_at(xj))
        M.add('mallet', mar.play(SCALE[j] + 12, 90), tj, 0.6, pan_at(xj))
    M.add('strings', trem.play(n('F2'), 70, dur=BAR, release=0.05), T_GLINT, 1.0, pie)    # the knife glints
    M.add('strings', trem.play(n('C3'), 65, dur=BAR, release=0.05), T_GLINT, 0.8, pie)
    for k in range(4):
        M.add('mallet', glock.play(n('F5') + 2 * k, 70), T_GLINT + k * BEAT, 0.35, pan_at(P0 if k % 2 else P1))
    for j, tc in enumerate(CHOPS):           # chop!
        p = pan_at(P0 + W * (j + 1))
        M.add('fx', whoosh(0.15, 1500, 5000, 0.5, seed=20 + j), tc - 0.12, 0.8, p)
        M.add('perc', clave.play(120), tc, 1.1, p)
        M.add('mallet', xylo.play(SCALE[11 - j], 110), tc, 0.9, p)
        M.add('drums', bd.play(100), tc, 0.5, p)
    tc = CHOPS[-1] + BEAT / 2                # cut: ta-da
    for i, m in enumerate(CH['Bb']):
        M.add('harp', harp.play(m + 24, 95), tc + 0.04 * i, 0.9, pie)
        M.add('pluck', cpizz.play(m + 12, 100), tc, 0.7, pie)
    M.add('perc', tri.play(90), tc, 0.5, pie)

    # ---- 18-26: passing, a pluck where every slice lands; 26-34: the table slides right and left ----
    rag(9, CHORDS_B + CHORDS_B[:0], 80)
    kit(9, 4, 86)
    tune(TUNE_B, 9, clar, vel=96, gain=0.9)
    for k, t0 in LEAVE.items():
        side = -1 if k < 4 else 1
        M.add('harp', harp.play(CH['Bb'][k % 3] + 24, 85), t0, 0.6, pan_at(CENTRES[k]))
        for j in range(abs(HOME[k] - 4)):
            tj = t0 + j * HOP + 0.32
            x = float(seat_d(4 + side * (j + 1)))
            m = SCALE[2 + j * 2 + (k % 2)]
            M.add('pluck', (mar if side < 0 else vpizz).play(m, 100), tj, 1.0, pan_at(x))
            M.add('perc', wood.play(75), tj, 0.4, pan_at(x))
    rag(13, [('Bb', 'Bb'), ('Eb', 'Eb')], 86, offbeats=False)
    rag(15, [('F7', 'F7'), ('F7', 'F7')], 92, offbeats=True)
    kit(13, 4, 94)
    tune(TUNE_A, 13, clst, vel=110)
    shift = 0
    for ts, dd in SHIFTS:                    # whistle up for right, down for left, from the wing that flashes
        shift += dd
        p = 0.7 if dd > 0 else -0.7
        quick = ts >= at(15)
        ln = 0.16 if quick else 0.28
        f0 = 600 * 2 ** (0.25 * shift)
        M.add('fx', slide(0.0, ln, f0, f0 * (1.5 if dd > 0 else 0.67), ln + 0.05, 0.5), ts, 0.8, p)
        M.add('pluck', (vpizz if dd > 0 else cpizz).play(n('F4') + 2 * shift, 105), ts + ln, 0.8, p)
        if abs(shift) == 2:                   # the end slices fly off and bounce back
            far = 2640 if shift > 0 else 400
            M.add('perc', slap.play(100), ts + ln, 0.6, pan_at(far))
            M.add('mallet', xylo.play(n('C6') if shift > 0 else n('F5'), 100), ts + ln, 0.7, pan_at(far))
    for m in ('Bb3', 'D4', 'F4', 'Bb4'):     # STOP
        M.add('keys', piano.play(n(m), 115), T_STOP, 0.8)
        M.add('pluck', cpizz.play(n(m) - 12, 110), T_STOP, 0.6)
    M.add('bass', bass.play(n('Bb2'), 120), T_STOP)
    M.add('drums', crash_s.play(100), T_STOP, 0.5)
    M.add('drums', bd.play(115), T_STOP, 0.8)

    # ---- 34-46: chomps in waves, a gulp, mmm ----
    rag(17, CHORDS_E, 76)
    kit(17, 4, 84)
    tune(TUNE_E, 17, bsn, vel=96, pan=0.15, gain=0.8)
    tune(TUNE_E, 17, clst, vel=90, pan=-0.15, gain=0.5)
    for j, (tb, s) in enumerate(BITES):
        p = pan_at(SEATS[s])
        M.add('perc', clave.play(115), tb, 0.9, p)
        M.add('perc', wood.play(120), tb + 0.01, 1.0, p)
        if tb >= at(21):
            M.add('perc', slap.play(110), tb, 0.3, p)
    M.add('drums', bd.play(120), at(21), 0.9)
    M.add('melody', bsn.play(n('F2'), 110), T_GULP, 1.0, pie)                     # gulp
    M.add('melody', bsn.play(n('Bb1'), 110), T_GULP + 0.18, 1.0, pie)
    M.add('fx', slide(0.0, 0.3, 500, 250, 0.35, 0.45), T_GULP, 0.5, pie)
    for m, v in (('Bb2', 70), ('F3', 62), ('D4', 58)):                             # mmm
        M.add('strings', cello.play(n(m), v, dur=T_LAST - at(22) + 0.5, release=0.5), at(22), 1.0, 0.0)
    M.add('melody', clar.play(n('D5'), 75, dur=1.5, release=0.4), at(22), 0.8)
    M.add('melody', clar.play(n('Bb4'), 70, dur=1.2, release=0.4), at(22, 3), 0.8)

    # ---- 46-60: the last slice; two hands tiptoe; a beat of stillness ----
    M.add('strings', trem.play(n('F2'), 60, dur=T_STILL - T_LAST, release=0.05), T_LAST, 1.0, pie)
    M.add('strings', trem.play(n('C3'), 55, dur=T_STILL - T_LAST, release=0.05), T_LAST, 0.8, pie)
    M.add('strings', trem.play(n('Gb3'), 50, dur=T_STILL - at(27), release=0.05), at(27), 0.7, pie)
    for h in HEARTS:                         # the heartbeat
        M.add('drums', timp.play(85 + int(20 * (h - T_LAST) / (T_STILL - T_LAST)), pitch=-5), h, 0.6, pie)
    for kf, inst, base, who in ((LH, cpizz, n('F3'), 'L'), (RH, vpizz, n('C4'), 'R')):
        last = kf[0][1]
        for (ta, xa), (tb, xb) in zip(kf, kf[1:]):
            if tb >= T_STILL or abs(xb - xa) < 1 or tb - ta > 1.2:
                continue
            m = base + int(abs(xb - kf[0][1]) / 25)
            p = pan_at(xb)
            M.add('pluck', inst.play(m, 90), ta, 0.8, p)
            M.add('melody', (bsn if who == 'L' else clst).play(m + (0 if who == 'L' else 12), 85), ta, 0.6, p)
    M.add('perc', wood.play(115, pitch=5), LH_FREEZE, 0.8, pan_at(1340))          # caught!
    M.add('fx', slide(0.0, 0.15, 900, 1300, 0.2, 0.4), LH_FREEZE, 0.5, pan_at(1340))
    r = troll.play(80, dur=T_STILL - at(28))
    M.add('drums', r * np.linspace(0.1, 1, r.shape[1]) ** 2, at(28), 0.5, pie)

    # ---- 59-61: the dog: in from Right, snatched, out up the Side; bonk ----
    ts = np.arange(T_DOG, T_DOGOUT, 0.055)
    for i, t in enumerate(ts):               # claws on the woodblocks, the length of the house
        x = dog_x(t)
        if not np.isnan(x) and -40 < x < L + 20:
            M.add('perc', wood.play(75 + 20 * (i % 2)), t, 0.4, pan_at(x))
    M.add('fx', travel(whoosh(T_GRAB - T_DOG, 300, 2500, 0.6, seed=7), 2600, MID), T_DOG, 0.7)
    for i in range(10):                      # a xylophone run in with him
        t = T_DOG + (T_GRAB - T_DOG) * i / 10
        M.add('mallet', xylo.play(SCALE[i % 8] + 12 * (i // 8), 80 + 3 * i), t, 0.6, pan_at(dog_x(t)))
    M.add('perc', slap.play(127), T_GRAB, 1.2, pie)                               # snatched
    M.add('fx', slide(0.0, 0.12, 600, 1900, 0.16, 0.6), T_GRAB, 0.9, pie)
    M.add('drums', timp.play(125, pitch=3), T_BONK, 1.2, pie)                     # bonk
    M.add('perc', log.play(127), T_BONK, 1.4, pie)
    M.add('drums', bd.play(120), T_BONK, 1.0, pie)
    M.add('drums', crash_s.play(90), T_BONK, 0.4, pie)
    M.add('fx', travel(whoosh(T_DOGOUT - T_GRAB, 2500, 500, 0.6, seed=8), MID, 0), T_GRAB + 0.1, 0.9)

    # ---- 62-72: the chase: a galop; claws panned with the dog; a whistle each time he comes round ----
    rag(31, CHORDS_C + CHORDS_C, 92, offbeats=True)
    kit(31, 8, 100)
    tune(TUNE_C + TUNE_C, 31, clst, vel=112, gain=1.0)
    tune(TUNE_C + TUNE_C, 31, xylo, 'mallet', 90, 0.15, 0.45)
    for t0, t1, end in LAPS:
        M.add('fx', slide(0.0, 0.4, 700, 1700, 0.45, 0.5), t0 - 0.2, 0.7, pan_at(2500))
        for i, t in enumerate(np.arange(t0, t1, 0.11)):
            x = dog_x(t)
            if not np.isnan(x) and 0 < x < L:
                M.add('perc', wood.play(70 + 15 * (i % 2)), t, 0.35, pan_at(x))
    M.add('fx', slide(0.0, 0.5, 1500, 400, 0.55, 0.5), T_SKID - 0.5, 0.8, pie)   # the skid
    M.add('drums', crash_s.play(115), T_SKID + 0.4, 0.7, pan_at(MID + 120))      # the pile-up
    M.add('perc', slap.play(120), T_SKID + 0.4, 0.9, pan_at(MID + 120))
    M.add('drums', timp.play(115), T_SKID + 0.4, 0.8, pan_at(MID + 120))
    for k in range(3):
        M.add('perc', log.play(110 - 10 * k), T_SKID + 0.55 + 0.12 * k, 0.6, pan_at(MID + 150 + 40 * k))

    # ---- 72: ding! the second pie; the A strain tutti to the end ----
    M.add('perc', tri.play(120), T_DING, 0.9, pie)
    M.add('mallet', glock.play(n('Bb5'), 110), T_DING, 0.7, pie)
    for k in range(8):                       # the pie grows a beat at a time: harp up two octaves
        for e in (0, 0.5):
            M.add('harp', harp.play(SCALE[k] - 12 + (12 if e else 0), 90), T_PIE2 + k * BEAT + e * BEAT, 0.7,
                  pan_at(MID + (k + 1) * 170 * (1 if (2 * k + e * 2) % 2 else -1)))
    rag(36, [('Bb', 'Bb'), ('Eb', 'F7')], 90, offbeats=True)
    kit(36, 2, 100)
    rag(38, CHORDS_A + CHORDS_E[:2], 96, offbeats=True)
    kit(38, 6, 104)
    tune(TUNE_A + TUNE_E[:2], 38, clst, vel=115, gain=1.1)
    tune(TUNE_A + TUNE_E[:2], 38, xylo, 'mallet', 92, 0.15, 0.45)
    tune(TUNE_A + TUNE_E[:2], 38, vpizz, 'pluck', 95, -0.2, 0.5)
    for k in range(int((T_END - T_SPIN2) / BEAT)):           # laughter, bouncing wing to wing
        t = T_SPIN2 + k * BEAT
        p = 0.6 if k % 2 else -0.6
        M.add('melody', (bsn if k % 2 else clst).play(n('F4') - 2 * (k % 4), 70), t, 0.4, p)
    for m in ('Bb2', 'F3', 'Bb3', 'D4', 'F4', 'Bb4'):          # the last chord
        M.add('keys', piano.play(n(m), 115), T_END, 0.7)
    for i, m in enumerate(('Bb2', 'F3', 'Bb3', 'D4', 'F4', 'Bb4', 'D5')):
        M.add('harp', harp.play(n(m), 90), T_END + 0.05 * i, 0.8, -0.6 + 0.2 * i)
    M.add('bass', bass.play(n('Bb2'), 120), T_END)
    M.add('melody', clar.play(n('Bb4'), 100, dur=1.6, release=0.5), T_END, 0.8)
    M.add('strings', cello.play(n('Bb2'), 80, dur=1.6, release=0.6), T_END, 1.0)
    M.add('drums', crash_s.play(110), T_END, 0.6)
    M.add('drums', bd.play(120), T_END, 0.9)
    M.add('mallet', glock.play(n('Bb5'), 90), T_END + 0.4, 0.5, pie)
