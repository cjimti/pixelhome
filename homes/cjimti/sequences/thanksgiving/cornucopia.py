"""Cornucopia: The Right wing is a woven horn of plenty, narrow at its free end and opening at the porch corner,
a wave of light pumping down it on every beat. Harvest spills out of its mouth: pumpkins, gourds, apples, corn and
cranberries, each a body with its own size and mass, rolling with real momentum along the porch to the Left wing,
leaving a wake of colour, knocking into each other and packing up in a row that grows back along the porch, every
knock a ripple running up the row. The jig speeds up and the horn gushes, two at a time. Then it slows to a last few
plinks and stops: a false ending. A rumble, and a pumpkin too big for the mouth sticks in it. It rocks and strains,
lurches half out and sucks back, twice, the house holds its breath, and it pops free, thunders down the porch and
slams into the back of the row; like a Newton's cradle the shock runs the length of the pile and fires the little
cranberry at the front off along the Left wing and out the back of the house. A moment later the cranberry drops back
in at the free end of Right, rattles down the horn, and the horn, unplugged at last, erupts: the whole pile is blown
off the end of the house and a torrent of harvest pours round the roofline, then dances out from the porch to both
ends, to the band's last strain.

Everything runs on course distance x = path length - path distance: x = 0 at the free end of Right, increasing
toward the back of the Side."""
import numpy as np
from pixelhome.fx import DT, hexc, light, keys, smoothstep, lerp, Flicker, nframes

CODE = 'TG08'
TITLE = 'Cornucopia'
KIND = 'show'
DESCRIPTION = ('A horn of plenty pours pumpkins, apples, corn and cranberries across the house until one pumpkin '
               'gets stuck. It pops, a cranberry flies out the far end, sneaks back in, and the horn erupts.')
VOICEOVER = "The harvest is in, and there's more than enough for everyone."

PUMPKIN = hexc('#ff5200')
APPLE = hexc('#c0102a')
GOLD = hexc('#ffb000')
AMBER = hexc('#ff8a18')
CRAN = hexc('#d0183a')
WARM = hexc('#ffc27a')
BROWN = hexc('#7a2c06')
DEEP = hexc('#4a1604')
CORN = hexc('#ffd000')
HARVEST = np.array([PUMPKIN, GOLD, APPLE, AMBER, CRAN, CORN])
D = 90.0
END = 2512.0
MOUTH = 470.0                       # course distance of the horn's mouth (path distance 2042, by the porch corner)
TABLE = 1450.0                      # the row packs up centred here (path distance 1062, on Porch Left)
KINDS = {'pumpkin': (15, PUMPKIN), 'gourd': (10, GOLD), 'apple': (8, APPLE), 'corn': (13, CORN),
         'cran': (3.5, CRAN), 'pear': (8, AMBER)}         # radius, colour
BAR = 1.2                           # the jig: 6/8, a bar of two dotted-quarter beats
BEAT = BAR / 2
T0 = 4 * BAR                        # the first spill, after four bars of the horn filling


def bar(k):
    return T0 + k * BAR


GUSH = bar(16)                      # the second round: faster, two at a time
STOP = bar(29)                      # the false ending: the band stops, a few last plinks
BIG = bar(33)                       # the big pumpkin sticks in the mouth
STRAIN = (bar(34.5), bar(36))       # it starts to strain, and is at full strain
LURCH = (bar(37), bar(40))          # it lurches half out and is sucked back
HOLD = (bar(42.3), bar(43))         # the held breath
POP = bar(43)
T_BACK = bar(47)                    # the cranberry drops back in at the free end of Right
ERUPT = bar(48)                     # it reaches the mouth: the horn erupts
DANCE = bar(56)                     # the torrent turns to a dance out from the porch
CAD = bar(64)                       # the cadence
FIN = bar(66)                       # the last chord
SHAKE = 1 / BEAT                    # Hz: the stuck pumpkin rocks on the beat


def schedule(rng):
    """(time, kind) of every spill before the big pumpkin."""
    out = [(T0, 'cran')]
    t = T0
    pool = ['pumpkin', 'gourd', 'apple', 'corn', 'cran', 'pear', 'apple', 'cran']
    while True:                                     # round one: on the beat, the gaps closing up
        t += BEAT * (rng.choice([3, 2, 2]) if t < bar(8) else rng.choice([2, 1, 1]))
        if t >= GUSH:
            break
        out.append((t, str(rng.choice(pool))))
    t = GUSH
    while t < STOP - BEAT:                          # the gush: on the beat and the half beat
        out.append((t, str(rng.choice(pool))))
        t += BEAT * rng.choice([0.5, 0.5, 1.0])
    for dt in (1.0, 1.8, 3.0):                      # the false ending: a few last plinks, slowing
        out.append((STOP + dt, 'cran'))
    return out


def lurch(t):
    """How far the stuck pumpkin is out of the mouth on its two lurches."""
    v = 0.0
    for k, (tl, h) in enumerate(zip(LURCH, (34.0, 52.0))):
        u = t - tl
        if 0 <= u < 0.9:
            v += h * (smoothstep(0, 0.22, u) - smoothstep(0.3, 0.9, u))
    return v


def render(G, seed=28, log=None):
    """log, a list, collects what score() plays to: ('spill', t, kind), ('pos', t, [x of each item]),
    ('knock', t, x, impulse, a, b), ('pop', t), ('shock', t), ('fire', t), ('out', t)."""
    rng = np.random.default_rng(seed)
    F = nframes(D)
    out = np.zeros((F, G.N, 3))
    n = G.N
    xp = END - G.pd[G.path]                        # course distance of each pixel in path order
    weave = Flicker(rng, n, 0.05, 0.2)
    sched = schedule(rng)
    items = []
    for tt, k in sched:
        R, col = KINDS[k]
        v = rng.uniform(380, 520) * (1.25 if tt >= GUSH else 1.0)
        items.append(dict(R=R, col=col, m=R ** 2, t0=tt, x=MOUTH - 30.0, v=v, on=False, big=False, kind=k,
                          i=len(items)))
    BIGI = dict(R=24, col=PUMPKIN, m=24 ** 2, t0=BIG, x=MOUTH - 45.0, v=0.0, on=False, big=True, kind='big',
                i=len(items))
    items.append(BIGI)
    shock_t = None
    shot = None                      # the cranberry that gets fired
    out_t = None
    slope, visc, coulomb = 150.0, 0.55, 25.0
    SUB = 3
    dt = DT / SUB
    ripples = []                     # (time, x, strength): a knock running up the row
    blast_v = rng.uniform(700, 1600, len(items))
    blasted = False
    hx = np.clip(xp / MOUTH, 0, 1)
    horn = xp < MOUTH + 6

    for f in range(F):
        t = f * DT
        kb = (t - T0) / BEAT
        bp = kb % 1.0
        beat = np.exp(-bp * BEAT / 0.1)
        for it in items:
            if not it['on'] and t >= it['t0']:
                it['on'] = True
                if log is not None:
                    log.append(('spill', it['t0'], it['kind']))
        live = [it for it in items if it['on'] and it is not shot]
        if t >= ERUPT and not blasted:              # the eruption blows the whole row off the end of the house
            blasted = True
            for it in live:
                it['v'] = blast_v[it['i']] * (0.6 + 0.4 * (it['x'] - 800) / 900)
        if blasted:
            for it in live:
                it['v'] -= 0.3 * it['v'] * DT
                it['x'] += it['v'] * DT
        else:
            for _ in range(SUB):
                for it in live:
                    if it['big'] and t < POP:
                        strain = smoothstep(*STRAIN, t)
                        it['x'] = MOUTH - 24 + 5 * np.sin(2 * np.pi * SHAKE * t) * strain + lurch(t)
                        it['v'] = 0.0
                        continue
                    if it['big'] and t >= POP and it.get('popped') is None:
                        it['v'] = 900.0
                        it['popped'] = True
                        if log is not None:
                            log.append(('pop', t))
                    d = TABLE - it['x']
                    a = slope * np.sign(d) * min(1, abs(d) / 40) - visc * it['v']
                    if abs(it['v']) > 1e-3:
                        a -= coulomb * np.sign(it['v'])
                    it['v'] += a * dt
                    if abs(it['v']) < 2 and abs(d) < 400:
                        it['v'] *= 0.9
                    it['x'] += it['v'] * dt
                live.sort(key=lambda z: z['x'])
                for _ in range(2):                      # contacts between neighbours
                    for a_, b_ in zip(live[:-1], live[1:]):
                        gap = b_['x'] - a_['x'] - (a_['R'] + b_['R'])
                        if gap < 0:
                            if a_['big'] and a_.get('popped') and shock_t is None and a_['v'] > 200:
                                shock_t = t
                                a_['v'] = 0.0
                                if log is not None:
                                    log.append(('shock', t))
                            ma, mb = a_['m'], b_['m']
                            rel = a_['v'] - b_['v']
                            if rel > 0:
                                e = 0.25
                                j = (1 + e) * rel / (1 / ma + 1 / mb)
                                if log is not None:
                                    log.append(('knock', t, a_['x'] + a_['R'], j, a_['i'], b_['i']))
                                if j > 300 and (not ripples or t - ripples[-1][0] > 0.12) and shock_t is None:
                                    ripples.append((t, a_['x'] + a_['R'], min(1.0, 0.35 + 0.3 * np.log10(j / 300))))
                                a_['v'] -= j / ma
                                b_['v'] += j / mb
                            corr = -gap / (ma + mb)
                            if not (a_['big'] and t < POP):
                                a_['x'] -= corr * mb
                            b_['x'] += corr * ma
        if shot is not None:
            shot['v'] -= 0.35 * shot['v'] * DT
            shot['x'] += shot['v'] * DT
        # the shock reaches the front of the row: fire the front cranberry
        if shock_t is not None and shot is None:
            row = sorted([it for it in items if it['on']], key=lambda z: z['x'])
            span = row[-1]['x'] - row[0]['x']
            if t >= shock_t + span / 2600:
                shot = row[-1]
                shot['v'] = 1350.0
                shot['fired'] = t
                if log is not None:
                    log.append(('fire', t))
        row_now = [it for it in items if it['on'] and it is not shot]
        row_front = max([it['x'] + it['R'] for it in row_now], default=0.0)
        row_back = min([it['x'] - it['R'] for it in row_now if not it['big'] or t >= POP], default=TABLE)

        buf = np.zeros((n, 3))
        # ---- the horn on the Right wing: woven, narrow at the free end, wide at the mouth; a pulse pumps down it ----
        tex = 0.6 + 0.4 * np.sin(xp * 0.42 + 3 * np.sin(xp * 0.05) - 2.0 * t) ** 2
        hI = keys(t, [(0, 0), (2.5, 0.6), (HOLD[0], 0.65), (HOLD[0] + 0.2, 0.4), (POP, 0.65), (86, 0.65), (90, 0)])
        hI = hI * (0.3 + 0.7 * hx ** 1.4) * tex * (1 + 0.12 * weave(t))
        strain = smoothstep(*STRAIN, t) * (t < POP)
        hI = hI * (1 + strain * 0.5 * np.sin(2 * np.pi * SHAKE * 2 * t) * hx ** 3)
        buf += light(1.0, hI * horn) * lerp(BROWN, AMBER, (0.25 + 0.45 * hx * tex)[:, None])
        buf += light(GOLD, 0.5 * hI * horn * hx ** 4)
        if t < BIG or t >= ERUPT:                    # a wave of light pumps down the horn on every beat
            per = BEAT if t < GUSH else (BEAT / 2 if t < STOP or t >= ERUPT else BEAT)
            ph = ((t - T0) / per) % 1.0
            px = ph * (MOUTH + 60)
            pump = 0.7 if t >= ERUPT else keys(t, [(0, 0), (2.5, 0.5), (STOP, 0.6), (STOP + 1, 0.0), (BIG, 0)])
            buf += light(GOLD, pump * np.exp(-((xp - px) / 40) ** 2) * horn * (0.4 + 0.6 * hx))
        # each spill: the mouth coughs a puff of light
        for it in items:
            u = t - it['t0']
            if 0 <= u < 0.5 and not it['big']:
                buf += light(WARM, 0.6 * np.exp(-u / 0.15) * np.exp(-((xp - MOUTH) / 25) ** 2))

        # ---- bunting in harvest colours on the rest of the house, stepping toward the table on the beat ----
        bunt = keys(t, [(0, 0), (3, 0.32), (STOP, 0.36), (STOP + 1.5, 0.14), (BIG, 0.14), (HOLD[0], 0.26),
                        (HOLD[0] + 0.15, 0.04), (POP, 0.04), (POP + 0.3, 0.26), (ERUPT, 0.26), (ERUPT + 0.5, 0.0)])
        if bunt > 0:
            step = np.floor(kb) + smoothstep(0, 0.75, bp) if t < BIG else np.floor(kb)
            fl = (xp - 60 * step) / 60
            idx = np.floor(fl).astype(int)
            flag = np.clip(1 - (fl - idx) * 1.25, 0, 1)
            sway = 0.7 + 0.5 * (beat if t < BIG else (0.5 + 0.5 * np.sin(2 * np.pi * SHAKE * t)) * (0.4 + strain))
            buf += light(1.0, bunt * flag * sway * (~horn)) * HARVEST[idx % 6]
        # the table glows warm under the row
        if t < ERUPT and row_now:
            under = (xp > row_back - 10) & (xp < row_front + 10) & ~horn
            buf += light(WARM, 0.3 * (0.8 + 0.4 * beat * (t < BIG)) * under)

        # ---- the harvest: each body with a turning highlight and a wake of colour behind it ----
        for it in items:
            if not it['on']:
                continue
            x, R = it['x'], it['R']
            if x - R > END + 5:
                continue
            body = np.clip((R - np.abs(xp - x)) / 2.5 + 0.5, 0, 1)
            roll = 0.72 + 0.28 * np.cos((xp - x) / R * 1.6 + x / R)
            emerge = smoothstep(it['t0'], it['t0'] + 0.25, t)
            I = (0.85 if R > 4 else 1.0) * body * roll * emerge
            buf += light(it['col'], I)
            sp = abs(it['v']) if (it is shot or blasted or not it['big'] or t >= POP) else 0.0
            if sp > 60:
                behind = np.clip(x - R - xp, 0, None)
                wake = np.exp(-behind / (0.12 * sp)) * (behind > 0) * (xp > MOUTH - 10)
                buf += light(it['col'], 0.75 * min(1.0, sp / 350) * wake)
        # knocks: each one a ripple running up the row to its front
        for t0, x0, amp in ripples[-12:]:
            u = t - t0
            if 0 <= u < 0.6:
                fr = x0 + 1800 * u
                if fr < row_front + 15:
                    buf += light(WARM, 0.75 * amp * np.exp(-u / 0.35) * np.exp(-((xp - fr) / 22) ** 2))

        # ---- the big one: stuck, rocking on the beat, lurching; the house holds its breath ----
        if BIG <= t < POP:
            bx = BIGI['x']
            buf += light(AMBER, (0.3 + 0.6 * strain) * np.exp(-((xp - bx) / 60) ** 2) *
                         (0.6 + 0.4 * np.sin(2 * np.pi * SHAKE * t) ** 2))
            for tl in LURCH:
                u = t - tl
                if 0 <= u < 1.0:                     # a near miss: the whole porch flashes and dies back
                    buf += light(GOLD, 0.45 * np.exp(-u / 0.25) * (xp > MOUTH) * (xp < 1220))
            if HOLD[0] <= t:
                buf *= (0.35 + 0.65 * (np.abs(xp - bx) < 40))[:, None]
        # the shock wave through the row, then the whole row blazes
        if shock_t is not None and t - shock_t < 1.4:
            u = t - shock_t
            row = sorted([it for it in items if it['on'] and it is not shot], key=lambda z: z['x'])
            x0 = row[0]['x']
            fr = x0 + 2600 * u
            buf += light(WARM, 1.0 * np.exp(-((xp - fr) / 34) ** 2) * (xp < row[-1]['x'] + 40) * np.exp(-u / 0.7))
            buf += light(WARM, 0.8 * np.exp(-u / 0.15) * np.exp(-((xp - x0) / 40) ** 2))
            buf += light(GOLD, 0.35 * np.exp(-u / 0.5) * ((xp > x0 - 20) & (xp < row[-1]['x'] + 20)))
        if shot is not None and out_t is None:       # the cranberry's comet tail as it flies
            x = shot['x']
            behind = np.clip(x - xp, 0, None)
            buf += light(CRAN, 0.85 * np.exp(-behind / 120) * (behind > 0) * (xp > TABLE - 60))
        # plink: the cranberry leaves through the free end at the back of the Side
        if shot is not None and shot['x'] > END:
            if out_t is None:
                out_t = t
                if log is not None:
                    log.append(('out', t))
            u = t - out_t
            buf += light(WARM, 0.9 * np.exp(-u / 0.2) * np.exp(-((xp - END) / 30) ** 2))

        # ---- it drops back in at the free end of Right and rattles down the horn ----
        if T_BACK <= t < ERUPT:
            u = (t - T_BACK) / (ERUPT - T_BACK)
            cx = MOUTH * u ** 1.3
            hop = np.abs(np.sin(np.pi * 6 * u))
            buf += light(CRAN, np.exp(-((xp - cx) / 5) ** 2) * (0.7 + 0.3 * hop))
            buf += light(GOLD, 0.4 * hop * np.exp(-((xp - cx) / 30) ** 2))
            buf += light(WARM, 0.8 * np.exp(-(t - T_BACK) / 0.15) * np.exp(-(xp / 30) ** 2))

        # ---- the eruption: a white-gold burst rolls out of the mouth to the end, then the torrent pours ----
        if ERUPT <= t:
            u = t - ERUPT
            if u < 2.0:
                fr = MOUTH + 1600 * u
                buf += light(WARM, 1.0 * np.exp(-((xp - fr) / 80) ** 2) * (xp > MOUTH - 20) * np.exp(-u / 1.2))
                buf += light(GOLD, 0.6 * np.exp(-u / 0.25) * np.exp(-((xp - MOUTH) / 200) ** 2))
            lv = keys(t, [(ERUPT, 0.0), (ERUPT + 0.3, 0.75), (DANCE - 0.3, 0.75), (DANCE, 0.0)])
            if lv > 0:                               # the torrent: harvest stripes streaming down the whole house
                reach = MOUTH + 1300 * u
                ph = (xp - 700 * u) / 75
                k_ = np.floor(ph).astype(int)
                stripe = np.sin(np.pi * (ph - k_)) ** 2
                fast = (bp * 2) % 1.0
                I = lv * stripe * (xp > MOUTH) * (xp < reach) * (0.75 + 0.35 * np.exp(-fast * BEAT / 0.06))
                buf += light(1.0, I) * HARVEST[k_ % 6]
            lv = keys(t, [(DANCE - 0.3, 0.0), (DANCE, 0.8), (FIN, 0.8), (FIN + 1.0, 0.5), (88, 0.45), (90, 0)])
            if lv > 0:                               # the dance: chevrons step out from the porch to both ends
                dd = np.abs(G.pd[G.path] - 1486)
                step = np.floor(kb) + smoothstep(0, 0.75, bp)
                ph = (dd - 70 * step) / 70
                k_ = np.floor(ph).astype(int)
                chev = np.clip(1 - (ph - k_) * 1.2, 0, 1)
                if t < FIN + 1.0:
                    I = lv * chev * (0.7 + 0.4 * beat)
                else:                                # after the last chord: the harvest flows slowly out to the ends
                    ph = (dd - 90 * (t - FIN)) / 110
                    k_ = np.floor(ph).astype(int)
                    I = lv * (0.35 + 0.65 * np.sin(np.pi * (ph - k_)) ** 2)
                buf += light(1.0, I * (~horn | (t >= FIN))) * HARVEST[k_ % 6]
            for tc in (CAD, CAD + BEAT, CAD + 2 * BEAT, CAD + 3 * BEAT, FIN):   # cadence hits: gold sweeps
                uu = t - tc
                if 0 <= uu < 1.2:
                    fr = MOUTH + 2400 * uu
                    big = 1.0 if tc == FIN else 0.6
                    buf += light(GOLD, big * np.exp(-((xp - fr) / 90) ** 2) * np.exp(-uu / 0.8))
        if log is not None:
            log.append(('pos', t, [it['x'] if it['on'] else np.nan for it in items]))
        out[f][G.path] = np.clip(buf * keys(t, [(88, 1), (90, 0)]), 0, 1)
    return out


# ---------------------------------------------------------------- music ----------------------------------------------
# A harvest jig in Bb, 6/8 at 1.2 s a bar from the first spill: pizzicato bass and upright piano, a bassoon then a
# clarinet with the tune, a fiddle joining for the gush with tambourine on every beat. Every item that rolls out
# tumbles down a marimba (xylophone for the small ones), a note for each half turn it actually makes, so the runs slow
# as it slows; the bigger it is the lower and heavier. Each spill is a log-drum cough at the mouth, each arrival a
# woodblock knock where it hits the row. The false ending is a cadence and three lonely plinks; a timpani rumble brings
# in the stuck pumpkin, grunting on a bassoon with every rock, whooping up a slide whistle on each lurch and sliding
# back down; a roll, a breath of silence, and it pops with a slide whistle, thunders down, and the shock ripples the
# length of the pile in claves before the cranberry flies out on a slide whistle and lands with a plink. It scampers
# back offstage on pizzicato, rattles down the horn on the xylophone, and the eruption brings the whole band in on
# the tune: horns, clarinet, fiddle, glockenspiel sparkle for the torrent; the second strain for the dance, a cadence
# of hits, and the last chord.

PROG = ['Bb', 'Eb', 'Bb', 'F', 'Bb', 'Eb', 'F', 'Bb'] * 2 + ['Gm', 'Eb', 'Bb', 'F', 'Gm', 'Eb', 'F', 'Bb']
CHORD = {'Bb': (34, 41, (62, 65, 70)), 'Eb': (39, 46, (63, 67, 70)), 'F': (41, 36, (60, 63, 65, 69)),
         'Gm': (43, 38, (62, 67, 70))}      # root, fifth, chord (F with its seventh)
TUNE_A = [[(0, 'F4', 2), (2, 'Bb4', 1), (3, 'D5', 2), (5, 'C5', 1)], [(0, 'Bb4', 2), (2, 'G4', 1), (3, 'Eb5', 3)],
          [(0, 'D5', 2), (2, 'C5', 1), (3, 'Bb4', 2), (5, 'A4', 1)], [(0, 'C5', 3), (3, 'F4', 3)],
          [(0, 'F4', 2), (2, 'Bb4', 1), (3, 'D5', 2), (5, 'F5', 1)], [(0, 'G5', 2), (2, 'F5', 1), (3, 'Eb5', 2), (5, 'C5', 1)],
          [(0, 'D5', 2), (2, 'C5', 1), (3, 'A4', 2), (5, 'C5', 1)], [(0, 'Bb4', 6)]]
TUNE_B = [[(0, 'D5', 1), (1, 'D5', 1), (2, 'G5', 1), (3, 'F5', 2), (5, 'D5', 1)], [(0, 'Eb5', 2), (2, 'C5', 1), (3, 'G4', 3)],
          [(0, 'Bb4', 1), (1, 'C5', 1), (2, 'D5', 1), (3, 'F5', 2), (5, 'D5', 1)], [(0, 'C5', 3), (3, 'A4', 2), (5, 'C5', 1)],
          [(0, 'Bb4', 2), (2, 'D5', 1), (3, 'G5', 2), (5, 'F5', 1)], [(0, 'Eb5', 2), (2, 'G5', 1), (3, 'Bb4', 2), (5, 'C5', 1)],
          [(0, 'D5', 2), (2, 'F4', 1), (3, 'A4', 2), (5, 'C5', 1)], [(0, 'Bb4', 3)]]
TUMBLE = {'pumpkin': ('mar', 'Bb3', 112), 'big': ('mar', 'F3', 124), 'corn': ('mar', 'A4', 92),
          'gourd': ('mar', 'F4', 96), 'apple': ('mar', 'C5', 86), 'pear': ('xylo', 'D5', 72), 'cran': ('xylo', 'F5', 60)}


def score(M, G):
    from pixelhome.audio import note, slide, whoosh
    n = note
    ev = []
    render(G, log=ev)                       # the same simulation: every spill, half turn, knock, the pop and the shot
    spill = [(t, k) for e, t, *k in ev if e == 'spill']
    kinds = [k[0] for _, k in spill]
    T = np.array([e[1] for e in ev if e[0] == 'pos'])
    P = np.array([e[2] for e in ev if e[0] == 'pos'])
    t_of = {e[0]: e[1] for e in ev if e[0] in ('pop', 'shock', 'fire', 'out')}
    SHOCK, FIRE, OUT = t_of['shock'], t_of['fire'], t_of['out']

    mar = M.sampler('Percussion/Marimba/*.wav', tune=-12)
    xylo = M.sampler('Percussion/Xylo/*.wav', tune=-12)
    bass = M.sampler('Strings/Solo Contrabass/Pizz/*.wav', tune=-12)
    piano = M.sampler('Keys/Upright Nr1/*.wav')
    bsn = M.sampler('Woodwinds/Bassoon/stac/*.wav', tune=-12)
    bsn_s = M.sampler('Woodwinds/Bassoon/sus/*.wav', tune=-12)
    clar = M.sampler('Woodwinds/Clarinet/susLong/*.wav', tune=-12)
    fid = M.sampler('Strings/Solo Violin/Arco Vib/*.wav')
    vpizz = M.sampler('Strings/Solo Violin/Pizz/*.wav')
    horn = M.sampler('Brass/F Horn/sus/*.wav', tune=-12)
    tpt = M.sampler('Brass/Trumpet/stac/*.wav', tune=-12)
    tuba = M.sampler('Brass/Tuba/stac/*.wav', tune=-12)
    harp = M.sampler('Strings/Harp/*.wav')
    glock = M.sampler('Percussion/Glock/*.wav', tune=-12)
    wood = M.hits('VSCO 1 Percussion/varWood/wood_click*.wav')
    clave = M.hits('Percussion/Claves1_Hit*.wav')
    log = M.hits('VSCO 1 Percussion/varWood/log_drum/slitdrum1_mp*.wav')
    slap = M.hits('VSCO 1 Percussion/varWood/slapstick[0-9].wav')
    tamb = M.hits('Percussion/Tamb1-Hit*.wav')
    timp = M.hits('Percussion/Timpani/Timpani1_Hit*.wav')
    troll = M.hits('Percussion/Timpani/Rolls/*.wav')
    sroll = M.hits('Percussion/Snare2-rollSN_v[35]*.wav')
    snare = M.hits('Percussion/Snare2-HitSN_v[57]*.wav')
    bd = M.hits('Percussion/BDrumNewhit_v[4-7]*.wav')
    crash = M.hits('Percussion/cymbal-crashshort*.wav')

    for name, gain, rev in (('bass', 0.21, 0.1), ('piano', 0.17, 0.18), ('tune', 0.18, 0.25), ('tumble', 0.09, 0.18),
                            ('perc', 0.5, 0.15), ('drums', 0.5, 0.2), ('brass', 0.24, 0.25), ('fx', 0.3, 0.25)):
        M.bus(name, gain=gain, reverb=rev)

    order = np.argsort(G.pd)
    xs, ds = G.pos[order, 0], G.pd[order]
    x0, x1 = xs.min(), xs.max()

    def pan_at(c):                          # course distance -> left/right across the facade, as seen from the street
        x = np.interp(END - c, ds, xs)
        return float(0.85 * (2 * (x - x0) / (x1 - x0) - 1))

    def chord_at(t):
        k = int((t - T0) // BAR)
        if t >= ERUPT:
            k = int((t - ERUPT) // BAR) % 16
        return PROG[min(max(k, 0), len(PROG) - 1)] if t < BIG or t >= ERUPT else 'Bb'

    def tones(c, top):                      # the chord's notes from top down an octave and a half
        pcs = {m % 12 for m in CHORD[c][2]}
        return [m for m in range(top, top - 19, -1) if m % 12 in pcs]

    def groove(t0, bars, prog, vel=90, tamb_on=False, gain=1.0):
        for k in range(bars):
            t, c = t0 + k * BAR, prog[k % len(prog)]
            root, fifth, ch = CHORD[c]
            M.add('bass', bass.play(root, vel), t, 1.0 * gain, -0.1)
            M.add('bass', bass.play(fifth, vel - 12), t + BAR / 2, 0.8 * gain, -0.1)
            for e in (2, 5):
                for m in ch:
                    M.add('piano', piano.play(m - 12 * (m > 66), vel - 30 + 6 * (e == 2)), t + e * BAR / 6,
                          0.6 * gain, 0.15)
            if tamb_on:
                for e in (0, 3):
                    M.add('perc', tamb.play(55 + 10 * (e == 3)), t + e * BAR / 6, 0.4 * gain, 0.3)

    def tune(inst, bars, t0, bus, vel, pan, shift=0, gain=1.0):
        for i, b in enumerate(bars):
            for e, m, dur in b:
                M.add(bus, inst.play(n(m) + shift, vel, dur=dur * BAR / 6 * 0.9, release=0.15),
                      t0 + i * BAR + e * BAR / 6, gain, pan)

    # ---- the horn fills with light; the jig from the first spill; the gush; the false ending ----
    groove(T0 - 4 * BAR, 4, ['Bb', 'F', 'Bb', 'F'], 72)
    for i, m in enumerate(('Bb2', 'F3', 'Bb3', 'D4', 'F4', 'Bb4')):
        M.add('tune', harp.play(n(m), 70), 0.3 + 0.12 * i, 0.7, pan_at(MOUTH * i / 5))
    for k in range(4):                      # the horn pumps on the beat
        for e in (0, 3):
            M.add('perc', log.play(70), T0 - 4 * BAR + k * BAR + e * BAR / 6, 0.4, pan_at(MOUTH * 0.5))
    groove(T0, 16, PROG)
    groove(GUSH, 13, PROG[16:] + PROG[:8], 98, True)
    tune(bsn, TUNE_A, T0, 'tune', 96, -0.25, -12)
    tune(clar, TUNE_A, T0 + 8 * BAR, 'tune', 84, 0.0)
    tune(clar, TUNE_B, GUSH, 'tune', 90, 0.0)
    tune(fid, TUNE_B, GUSH, 'tune', 80, 0.2, gain=0.8)
    tune(fid, TUNE_A[:5], GUSH + 8 * BAR, 'tune', 86, 0.2)
    tune(clar, TUNE_A[:5], GUSH + 8 * BAR, 'tune', 76, -0.1, -12)
    for k in range(13):                     # a snare on the second beat of every bar in the gush
        M.add('drums', snare.play(70), GUSH + k * BAR + BAR / 2, 0.4, 0.1)
    for m in (34, 41, 62, 65, 70):          # the false ending: a cadence, then nothing
        M.add('brass', horn.play(m, 90, dur=1.4, release=0.6), STOP, 0.5)
    M.add('bass', bass.play(n('Bb1'), 110), STOP, 1.0)
    M.add('drums', timp.play(90), STOP, 0.6)

    # ---- spills, tumbles and knocks, all from the simulation ----
    for (t, _), k in zip(spill, kinds):
        M.add('perc', log.play(96 + 31 * (k in ('pumpkin', 'big'))), t, 0.8, pan_at(MOUTH))
    for i, k in enumerate(kinds):
        inst, top, vel = TUMBLE[k]
        inst = mar if inst == 'mar' else xylo
        R = KINDS[k][0] if k in KINDS else 24
        x = P[:, i]
        live = ~np.isnan(x)
        t0 = T[live][0]
        tt, xx = T[live], x[live]
        end = (POP, SHOCK + 0.05) if k == 'big' else (t0, min(FIRE, SHOCK))
        sel = (tt >= end[0]) & (tt <= end[1])
        tt, xx = tt[sel], xx[sel]
        if len(tt) < 3:
            continue
        v = np.abs(np.gradient(xx, DT))
        still = np.nonzero((v < 20) & (tt > tt[0] + 0.5))[0]
        if len(still):
            tt, xx, v = tt[:still[0]], xx[:still[0]], v[:still[0]]
        if len(tt) < 3:
            continue
        s = np.concatenate([[0], np.cumsum(np.abs(np.diff(xx)))])
        step = max(np.pi * R, 28.0) * 1.6
        marks = np.arange(step, s[-1], step)
        when = np.interp(marks, s, tt)
        last = -1.0
        for j, (w, mk) in enumerate(zip(when, marks)):
            if w - last < 0.09:
                continue
            last = w
            sp = float(np.interp(w, tt, v))
            tn = tones(chord_at(w), n(top))
            m = tn[(j % 3 + j // 3) % len(tn)]
            M.add('tumble', inst.play(m, int(np.clip(vel * (sp / 450) ** 0.4, 30, 127))), w, 0.9,
                  pan_at(np.interp(w, tt, xx)))
    knocks = sorted((e[1], e[2], e[3]) for e in ev if e[0] == 'knock' and e[3] > 300 and e[1] < SHOCK)
    group = []
    for t, x, j in knocks + [(1e9, 0, 0)]:  # an arrival pushes the whole row in one instant: one knock per instant
        if group and t - group[0][0] > 0.15:
            _, xk, jk = max(group, key=lambda g: g[2])
            M.add('perc', wood.play(int(np.clip(76 + 30 * np.log10(jk / 300), 70, 127))), group[0][0], 1.0,
                  pan_at(xk))
            group = []
        group.append((t, x, j))

    # ---- the big one: a rumble, stuck in the mouth, rocking on the beat, lurching twice; the house holds its breath ----
    pm = pan_at(MOUTH)
    r = troll.play(80, dur=BIG - (STOP + 3.4))
    M.add('drums', r * np.linspace(0.1, 1, r.shape[1]), STOP + 3.4, 0.6, pm)
    M.add('brass', tuba.play(n('Bb1'), 115), BIG, 1.0, pm)
    M.add('drums', timp.play(110, pitch=-3), BIG, 0.8, pm)
    M.add('tune', clar.play(n('D5'), 72, dur=0.35), BIG + 0.6, 0.8, 0.0)      # "uh..."
    M.add('tune', clar.play(n('Db5'), 68, dur=0.6), BIG + 1.0, 0.8, 0.0)      # "...oh"
    for k in range(int(BIG / BEAT) + 2, int(HOLD[0] / BEAT) + 1):   # a grunt at every rock, a step up every other
        t = k * BEAT + 0.25 / SHAKE
        if t >= HOLD[0]:
            break
        g = smoothstep(STRAIN[0] - 1.5, STRAIN[1], t)
        M.add('tune', bsn.play(n('Bb2') + (k - int(BIG / BEAT)) // 2, int(60 + 50 * g)), t, 0.4 + 0.6 * g, pm)
        M.add('perc', wood.play(int(50 + 40 * g)), t, 0.4 * g, pm)
        M.add('bass', bass.play(n('Bb1') + ((k - int(BIG / BEAT)) // 2) % 12, 90), t, 0.7 * g)
    M.add('brass', bsn_s.play(n('F2'), 90, dur=HOLD[0] - STRAIN[0], release=0.1), STRAIN[0], 0.6, pm)
    for tl, f1 in zip(LURCH, (1300, 1700)):           # each lurch: whoop up, and slide sadly back
        M.add('fx', slide(0.0, 0.22, 500, f1, 0.25, 0.5), tl, 0.9, pm)
        M.add('fx', slide(0.0, 0.6, f1, 400, 0.65, 0.4), tl + 0.3, 0.8, pm)
        M.add('drums', crash.play(80), tl + 0.2, 0.4, pm)
        M.add('drums', timp.play(105), tl + 0.2, 0.6, pm)
        M.add('perc', slap.play(80), tl + 0.85, 0.5, pm)
    r = sroll.play(100, dur=HOLD[0] - LURCH[1] - 1.0)
    M.add('drums', r * np.linspace(0.1, 1, r.shape[1]) ** 2, LURCH[1] + 1.0, 0.6, pm)
    r = troll.play(100, dur=HOLD[0] - LURCH[1] - 1.0)
    M.add('drums', r * np.linspace(0.1, 1, r.shape[1]) ** 2, LURCH[1] + 1.0, 0.6, pm)

    # ---- POP; it thunders down to the row; the shock runs the pile; the cranberry flies ----
    M.add('fx', slide(0.0, 0.14, 500, 1500, 0.18, 0.5), POP - 0.02, 1.0, pm)
    M.add('perc', slap.play(120), POP, 0.9, pm)
    M.add('drums', crash.play(100), POP, 0.5, pm)
    M.add('fx', whoosh(SHOCK - POP + 0.1, 150, 900, 0.6, seed=8), POP, 0.8, pan_at((MOUTH + 1000) / 2))
    M.add('drums', troll.play(90, dur=SHOCK - POP), POP + 0.05, 0.7, pan_at((MOUTH + 1000) / 2))
    xs_row = np.sort(P[np.searchsorted(T, SHOCK)])
    xs_row = xs_row[~np.isnan(xs_row)]
    M.add('drums', bd.play(124), SHOCK, 1.0, pan_at(xs_row[0]))
    M.add('drums', timp.play(124, pitch=-5), SHOCK, 0.9, pan_at(xs_row[0]))
    M.add('drums', crash.play(118), SHOCK, 0.7, pan_at(xs_row[0]))
    M.add('brass', tuba.play(n('Bb1'), 124), SHOCK, 1.0, pan_at(xs_row[0]))
    up = [m for m in range(n('Bb3'), n('Bb6')) if m % 12 in (10, 0, 2, 3, 5, 7, 9)]
    for i, x in enumerate(xs_row[::2]):     # click, click, click: the shock through the pile to the front
        t = SHOCK + (x - xs_row[0]) / 2600
        M.add('perc', clave.play(90 + int(30 * i / len(xs_row))), t, 0.6, pan_at(x))
        M.add('tumble', xylo.play(up[min(i, len(up) - 1)], 90), t, 0.7, pan_at(x))
    xc = P[:, kinds.index('cran')]          # the shot is the front cranberry: the first one out
    for i, t in enumerate(np.arange(FIRE, OUT, 0.1)):         # a slide whistle that follows it along the house
        u0, u1 = (t - FIRE) / (OUT - FIRE), min(1, (t + 0.1 - FIRE) / (OUT - FIRE))
        f0, f1 = 700 * 2.6 ** u0, 700 * 2.6 ** u1
        M.add('fx', slide(0.0, 0.1, f0, f1, 0.11, 1.0), t, 0.9, pan_at(np.interp(t, T, xc)))
    M.add('tumble', glock.play(n('F6'), 80), OUT, 0.8, pan_at(END))
    M.add('tumble', glock.play(n('Bb5'), 60), OUT + 0.12, 0.5, pan_at(END))

    # ---- it scampers round the block (offstage), drops back in at the free end of Right and rattles down the horn ----
    for i, t in enumerate(np.arange(OUT + 0.5, T_BACK - 0.1, 0.15)):
        u = (t - OUT) / (T_BACK - OUT)
        M.add('tune', vpizz.play(n(('F5', 'D5', 'Bb4', 'C5', 'D5', 'Eb5', 'F5', 'G5')[i % 8]), int(40 + 40 * u)), t,
              0.6, float(-0.9 + 1.8 * u))
    M.add('tumble', glock.play(n('Bb5'), 90), T_BACK, 0.8, pan_at(0))
    for i, t in enumerate(np.linspace(T_BACK, ERUPT - 0.05, 9)):
        M.add('tumble', xylo.play(n('F5') - i, 100), t, 0.8, pan_at(MOUTH * ((t - T_BACK) / (ERUPT - T_BACK)) ** 1.3))
    M.add('tune', bsn.play(n('F2'), 110), ERUPT - 0.25, 0.9, pm)                         # a hiccup

    # ---- the eruption: the whole band; the torrent; the dance; the cadence and the last chord ----
    M.add('drums', crash.play(127), ERUPT, 1.0, pm)
    M.add('drums', bd.play(127), ERUPT, 1.0, pm)
    M.add('drums', timp.play(127, pitch=-5), ERUPT, 1.0, pm)
    M.add('brass', tuba.play(n('Bb1'), 127), ERUPT, 1.0)
    M.add('fx', whoosh(2.0, 120, 2400, 1.0, seed=12), ERUPT, 0.9, pan_at(1500))
    M.add('fx', slide(0.0, 1.0, 400, 1600, 1.1, 0.5), ERUPT, 0.8, pan_at(1500))
    groove(ERUPT, 8, PROG[:8], 104, True)
    groove(DANCE, 8, PROG[16:], 106, True)
    tune(horn, TUNE_A, ERUPT, 'brass', 100, -0.1)
    tune(clar, TUNE_A, ERUPT, 'tune', 84, 0.15)
    tune(fid, TUNE_A, ERUPT, 'tune', 84, 0.3, gain=0.8)
    tune(fid, TUNE_B, DANCE, 'tune', 92, 0.2)
    tune(clar, TUNE_B, DANCE, 'tune', 84, -0.2, -12)
    tune(horn, TUNE_B, DANCE, 'brass', 92, -0.1, -12, gain=0.7)
    tune(glock, TUNE_A, ERUPT, 'tumble', 90, 0.0, gain=0.6)
    for k in range(16):                     # a snare and bass drum march under the last two strains
        M.add('drums', bd.play(100), ERUPT + k * BAR, 0.6)
        M.add('drums', snare.play(85), ERUPT + k * BAR + BAR / 2, 0.5, 0.1)
    fr = np.random.default_rng(3)
    for t in np.arange(ERUPT, DANCE, 0.15):                # the torrent sparkles down the house
        m = tones(chord_at(t), n('F6'))[int(fr.integers(0, 4))]
        M.add('tumble', glock.play(m, int(fr.integers(50, 85))), t, 0.4,
              pan_at(MOUTH + (END - MOUTH) * ((t - ERUPT) * 0.6 % 1.0)))
    for i, tc in enumerate((CAD, CAD + BEAT, CAD + 2 * BEAT, CAD + 3 * BEAT)):   # the cadence: four hits
        c = ('Eb', 'F', 'F', 'F')[i]
        for m in CHORD[c][2]:
            M.add('brass', tpt.play(m, 118, dur=0.25), tc, 0.6)
        M.add('brass', tuba.play(CHORD[c][0] - 12 * (CHORD[c][0] > 40), 118), tc, 0.9)
        M.add('drums', bd.play(120), tc, 0.9)
        M.add('drums', crash.play(90 + 8 * i), tc, 0.45)
    fin = FIN
    for i, m in enumerate(('Bb2', 'F3', 'Bb3', 'D4', 'F4', 'Bb4', 'D5')):
        M.add('tune', harp.play(n(m), 95), fin + 0.06 * i, 0.9, -0.5 + 0.15 * i)
    M.add('bass', bass.play(n('Bb1'), 115), fin, 1.0)
    M.add('brass', tuba.play(n('Bb1'), 120), fin, 0.9)
    M.add('brass', horn.play(n('D4'), 100, dur=3.0, release=1.2), fin, 0.9, -0.1)
    M.add('brass', horn.play(n('F3'), 100, dur=3.0, release=1.2), fin, 0.8, 0.1)
    M.add('tune', clar.play(n('F4'), 86, dur=3.0, release=1.2), fin, 0.8, 0.15)
    M.add('tune', fid.play(n('Bb4'), 90, dur=3.0, release=1.2), fin, 0.8, 0.25)
    M.add('drums', timp.play(110), fin, 0.7)
    M.add('drums', crash.play(110), fin, 0.7)
    M.add('perc', wood.play(110), fin, 0.6, pan_at(TABLE))
