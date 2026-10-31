"""Turkey Trot: The morning 5K, run round the whole house. In a cool dawn sixteen runners in bright colours jog in from
the free end of Right and line up behind a white start line at its porch end; three red lamps, a green flash and the
horn, and the pack heads left along the roofline: Porch Right, Porch Front, Porch Left, past a water station on Left
(where the runner in the turkey costume stops for a drink and gets soaked) and out the back of Side. The course goes
round the block behind the house and comes back in at the free end of Right. The lime leader comes home first, but
the turkey, who made up ground behind the house, catches her on Porch Right; they trade the lead along Porch Front
and the turkey breaks the gold tape at the porch by a beak. Confetti; the rest of the field finishes one by one, two
little turkeys and finally a walker in pumpkin orange, who gets the biggest cheer of all as the sun comes up.

The house is never still: bunting in the runners' colours steps along the roofline with the march; the crowd does the
wave end to end before the start and again while the leaders are round the block, as the free end of Right shimmers
faster and faster until they burst back in. Each red lamp floods more of the house, and GO pours green down the whole
course. In the sprint the house pulses in the colour of whoever leads, harder toward the tape; half a second before
it, everything holds its breath, then the tape breaks in gold. Every finisher sweeps their colour out to both ends,
the walker is clapped in wing by wing, and the field's colours parade round the house to the last chord."""
import numpy as np
from pixelhome.fx import DT, hexc, light, keys, smoothstep, lerp, Flicker, nframes

CODE = 'TG11'
TITLE = 'Turkey Trot'
KIND = 'show'
DESCRIPTION = ('The morning 5K, all the way round the house. A pack in bright colours races past the water station, '
               'round the block and back, and a runner in a turkey costume sprints for the tape at the porch.')
VOICEOVER = "On your marks, get set, gobble: it's the Thanksgiving morning turkey trot!"

D = 90.0
SEED = 11
NIGHT = hexc('#0a1e78')
DAWN = hexc('#ff7a20')
WHITE = hexc('#fff0dc')
GOLD = hexc('#ffb000')
RED = hexc('#ff1000')
GREEN = hexc('#20ff30')
WATER = hexc('#40d8ff')
BRONZE = hexc('#c04a08')
CRANBERRY = hexc('#d0001c')
AMBER = hexc('#ff8a18')

# the course, in course distance c: c = 0 at the start line (path distance 2060, porch end of Right), running toward
# lower path distance along the whole roofline and out the back of Side at c = 2060; round the block for BEHIND; back in
# at the free end of Right (path distance 2512) and on to the finish at the middle of the Porch Front
START, FREE, FINISH = 2060.0, 2512.0, 1486.0
BEHIND = 700.0
C_OUT = START                                   # out the back of Side
C_IN = START + BEHIND                           # back in at the free end of Right
C_FIN = C_IN + (FREE - FINISH)                  # the tape
STATION = (580.0, 800.0)                        # the water station, on Left
T_GO = 11.5
COUNT = (8.5, 9.5, 10.5)
TAPE_UP = 40.0
T_DOUSE = (31.4, 33.4)                          # the turkey stops at the water station

# the field: colour, finish time (None: keyframed), kind. Grid order is list order, from the start line back.
FIELD = [('#a0ff00', None, 'lime'), ('#00e0ff', 57.5, 'run'), ('#ff1080', 58.5, 'run'), ('#ffa000', 60.0, 'run'),
         ('#ffe000', 61.5, 'run'), ('#c04a08', None, 'turkey'), ('#9030ff', 62.5, 'run'), ('#ff1010', 64.0, 'run'),
         ('#00ff70', 65.5, 'run'), ('#2050ff', 66.5, 'run'), ('#ff00d0', 68.0, 'run'), ('#ffe8c8', 69.5, 'run'),
         ('#60c0ff', 71.0, 'run'), ('#c04a08', 76.5, 'kid'), ('#c04a08', 77.0, 'kid'), ('#ff4a00', 80.5, 'walk')]
R = len(FIELD)
GRID = START + 18 + 24 * np.arange(R)           # where each lines up, in path distance
# the two who matter, as (time, course distance), smoothed into a run
LIME = [(T_GO, -18), (T_GO + 1.2, 30), (35.0, 2040), (43.6, C_IN), (53.0, 3600), (53.8, 3655), (54.6, 3712),
        (56.0, C_FIN), (57.5, C_FIN + 30)]
TURKEY = [(T_GO, -114), (T_GO + 1.5, -60), (T_DOUSE[0], 1360), (T_DOUSE[1], 1368), (42.0, 2052), (47.6, C_IN),
          (53.0, 3612), (53.8, 3662), (54.6, 3702), (55.5, C_FIN), (57.0, C_FIN + 20)]
T_WIN = 55.5
MARCH = 0.5                                     # the march's beat, from the GO
HUSH = (T_WIN - 0.4, T_WIN)                     # a held breath before the tape: the house and the band go quiet
WAVES = [(2.6, 1), (5.4, -1), (36.4, 1), (38.4, -1), (40.0, 1), (41.3, -1), (42.4, 1)]   # the crowd does the wave
WAVE_T = 2.2                                    # seconds for a wave to run the length of the house


def clap_times(t_walk):
    """The crowd clap the walker in, faster and faster."""
    c = 66.0 + np.cumsum(np.linspace(0.5, 0.22, 40))
    return c[c < t_walk - 0.1]


def course_to_pd(c):
    """Course distance -> path distance; NaN while round the back of the block."""
    c = np.asarray(c, float)
    pd = np.where(c <= C_OUT, START - c, FREE - (c - C_IN))
    return np.where((c > C_OUT) & (c < C_IN), np.nan, pd)


def smooth(x, sigma):
    k = np.exp(-0.5 * (np.arange(-3 * sigma, 3 * sigma + 1) / sigma) ** 2)
    k /= k.sum()
    pad = np.concatenate([np.full(3 * sigma, x[0]), x, np.full(3 * sigma, x[-1])])
    return np.convolve(pad, k, 'valid')


def field(seed=SEED):
    """Every runner's path distance for every frame (NaN off the house), their finish times and finishing order."""
    rng = np.random.default_rng(seed)
    F = nframes(D)
    t = np.arange(F) * DT
    c = np.zeros((F, R))
    fin = np.zeros(R)
    for i, (_, tf, kind) in enumerate(FIELD):
        off = GRID[i] - START
        if kind in ('lime', 'turkey'):
            kf = LIME if kind == 'lime' else TURKEY
            ci = smooth(np.interp(t, [k[0] for k in kf], [k[1] for k in kf]), 10)
            ci = np.where(t < T_GO, -off, ci)
            fin[i] = T_WIN if kind == 'turkey' else 56.0
        else:
            ph, per = rng.uniform(0, 2 * np.pi), rng.uniform(5, 9)
            shape = smoothstep(T_GO, T_GO + 2.0 + 0.1 * i, t) * (1 + 0.1 * np.sin(2 * np.pi * t / per + ph))
            prof = np.cumsum(shape) * DT
            k = (C_FIN + off) / np.interp(tf, t, prof)
            ci = -off + k * prof
            fin[i] = tf
        c[:, i] = ci
    order = np.argsort(fin)
    rank = np.empty(R, int)
    rank[order] = np.arange(R)
    for i, (_, tf, kind) in enumerate(FIELD):    # through the tape, everyone slows to a stop on the porch, in order
        rest = 26 + 10 * rank[i]
        u = np.clip(t - fin[i], 0, None)
        settle = u / 1.2 if kind in ('lime', 'turkey') else u * 80 / rest
        c[:, i] = np.where(t > fin[i], C_FIN + rest * (1 - np.exp(-settle)), c[:, i])
    pd = course_to_pd(c)
    # before the start: jog in from beyond the free end of Right to the grid, then bounce in place
    for i in range(R):
        t_in = 1.5 + 0.35 * i
        arrive = t_in + (2600 - GRID[i]) / 170
        jog = np.where(t < t_in, np.nan, np.where(t < arrive, 2600 - 170 * (t - t_in), GRID[i]))
        jog = np.where(jog > FREE + 20, np.nan, jog)
        pd[:, i] = np.where(t < T_GO, jog, pd[:, i])
    return pd, fin, rank


def render(G, seed=SEED):
    rng = np.random.default_rng(seed)
    F = nframes(D)
    out = np.zeros((F, G.N, 3))
    n = G.N
    pdp = G.pd[G.path]
    crowd = Flicker(rng, n, 0.6, 3.5)
    slow = Flicker(rng, n, 0.15, 0.6)
    pos, fin, rank = field(seed)
    cols = np.array([hexc(f[0]) for f in FIELD])
    kinds = [f[2] for f in FIELD]
    cad = rng.uniform(2.6, 3.2, R)
    cups = np.arange(STATION[0] + 10, STATION[1], 20)
    seg_lo = np.array([0, 492, 894, 1311, 1660, 2033])
    seg_hi = np.array([491, 893, 1310, 1659, 2032, 2513])
    conf_p = rng.uniform(0, G.length, 220)
    conf_c = cols[rng.integers(0, R, 220)]
    conf_ph = rng.uniform(0, 2 * np.pi, 220)
    lead_i = [k for k, f in enumerate(FIELD) if f[2] == 'lime'][0]
    turk_i = [k for k, f in enumerate(FIELD) if f[2] == 'turkey'][0]
    last_t = max(fin)
    claps = clap_times(last_t)
    t_end = T_GO + int(round(last_t - T_GO)) + 6     # the band's last chord

    for f in range(F):
        t = f * DT
        buf = np.zeros((n, 3))
        sun = smoothstep(8, 85, t)
        sky = lerp(NIGHT, DAWN, sun ** 0.8)
        bed = keys(t, [(0, 0), (2.5, 0.2), (86, 0.24), (90, 0)])
        buf += light(sky, bed * (0.9 + 0.2 * slow(t)))

        # bunting round the house in the runners' colours, stepping along with the march
        kb = (t - T_GO) / MARCH
        bp = kb % 1.0
        pulse = np.exp(-bp * MARCH / 0.1)
        bunt = keys(t, [(0, 0.0), (3, 0.2), (T_GO, 0.2), (T_GO + 0.5, 0.36), (86, 0.36), (89.8, 0)])
        bunt *= 1 - 0.85 * (HUSH[0] <= t < HUSH[1])
        shift = 64 * (np.floor(kb) + smoothstep(0, 0.75, bp)) if t > T_GO else 0.0
        fl = (pdp + shift) / 64
        idx = np.floor(fl).astype(int)
        flag = np.clip(1 - (fl - idx) * 1.25, 0, 1)
        buf += light(1.0, bunt * flag * (0.7 + 0.5 * pulse)) * cols[idx % R]

        p = pos[f]
        on = ~np.isnan(p)
        pp = np.where(on, p, -1e4)
        moving = (t > T_GO) & (t < fin + 1.5)

        # the crowd along the route cheers where the runners are; louder at the start, the sprint, and each finish
        near = np.exp(-((pdp[:, None] - pp[None, :]) / 170) ** 2).sum(1)
        roar = keys(t, [(0, 0.15), (T_GO, 0.15), (T_GO + 0.1, 0.8), (T_GO + 3, 0.3), (50, 0.4), (T_WIN, 0.9),
                        (T_WIN + 4, 0.35), (last_t - 3, 0.4), (last_t, 0.9), (last_t + 4, 0.4), (90, 0.3)])
        sparkle = np.clip(crowd(t), 0, 1) ** 4
        buf += light(lerp(WHITE, GOLD, 0.4), roar * np.clip(0.25 + near, 0, 1.4) * 0.5 * sparkle)
        for tw, dr in WAVES:                        # the wave: a bright band of cheering runs the whole house
            u = (t - tw) / WAVE_T
            if 0 <= u < 1.1:
                x = u * (G.length + 200) - 100
                x = x if dr > 0 else G.length - x
                buf += light(lerp(WHITE, GOLD, 0.35), 0.9 * np.exp(-((pdp - x) / 90) ** 2) * (0.6 + 0.4 * sparkle))
        if 38.5 <= t < 43.8:                        # here they come: the free end of Right shimmers, faster and faster
            a = smoothstep(38.5, 43.5, t)
            buf += light(GOLD, 0.75 * a * (0.5 + 0.5 * np.sin(2 * np.pi * (2 + 6 * a) * t)) *
                         np.exp(-(FREE - pdp) / 160))

        # start line, countdown lamps, GO
        line = keys(t, [(0, 0), (3, 0.7), (T_GO, 0.7), (T_GO + 2, 0.15), (40, 0.1), (42, 0)])
        buf += light(WHITE, line * np.exp(-((pdp - START) / 4) ** 2))
        for tc in COUNT:
            u = t - tc
            if 0 <= u < 0.8:
                g = np.exp(-u / 0.25)
                buf += light(RED, 0.9 * g * np.exp(-((pdp - START) / 30) ** 2))
                reach = (2033, 1660, 1311)[COUNT.index(tc)]
                buf += light(RED, 0.55 * g * ((pdp > reach) & (pdp < FREE + 1)))
        u = t - T_GO
        if 0 <= u < 2.0:                            # GO: green floods down the course, the length of the house
            fr_ = START - 2400 * u
            buf += light(GREEN, 0.5 * np.exp(-u / 0.25) + 0.95 * np.exp(-((pdp - fr_) / 70) ** 2) +
                         0.45 * np.exp(-u / 0.6) * (pdp > fr_))

        # the water station on Left: a row of cups, a splash wherever a runner goes through
        st = keys(t, [(0, 0), (3, 0.38), (45, 0.38), (48, 0.12), (86, 0.12), (90, 0)])
        cupI = np.exp(-((pdp[:, None] - cups[None, :]) / 3) ** 2).sum(1)
        buf += light(WATER, st * cupI * (0.85 + 0.15 * crowd(t)))
        at_st = on & (pp > STATION[0]) & (pp < STATION[1]) & moving
        for i in np.nonzero(at_st)[0]:
            buf += light(WATER, 0.55 * np.exp(-((pdp - pp[i]) / 14) ** 2) * (0.4 + 0.6 * sparkle))
        u = t - T_DOUSE[0]
        if 0 <= u < 3.0:                        # the turkey gets the cup over his head: a fountain
            ring = np.exp(-((np.abs(pdp - pp[turk_i]) - 140 * u) / 16) ** 2) * np.exp(-u / 0.7)
            buf += light(WATER, 0.9 * np.exp(-u / 0.6) * np.exp(-((pdp - pp[turk_i]) / 35) ** 2) + 0.7 * ring)

        # the sprint: the whole house pulses in the colour of whoever leads, harder and faster to the tape
        if 44.0 <= t < HUSH[0]:
            a_, b_ = pp[lead_i], pp[turk_i]
            if on[lead_i] and on[turk_i] and a_ < FREE and b_ < FREE:
                col = cols[lead_i] if a_ < b_ else GOLD
                lv = keys(t, [(44, 0.12), (50, 0.22), (HUSH[0], 0.42)])
                buf += light(col, lv * (0.35 + 0.65 * np.exp(-bp * MARCH / 0.09)))
        if HUSH[0] <= t < HUSH[1]:
            buf *= 0.15

        # the finish tape and a chequered banner across the Porch Front before the sprint
        tape = keys(t, [(TAPE_UP, 0), (TAPE_UP + 1, 0.85), (T_WIN, 0.85), (T_WIN + 0.05, 0)])
        buf += light(lerp(GOLD, WHITE, 0.5), tape * (0.85 + 0.15 * np.sin(9 * t)) * np.exp(-((pdp - FINISH) / 4) ** 2))
        chk = keys(t, [(48, 0), (50, 0.3), (HUSH[0] - 0.1, 0.4), (HUSH[0], 0)])
        if chk > 0:
            blocks = ((np.floor((pdp - 1311) / 24) + np.floor(t * 2)) % 2) * ((pdp > 1311) & (pdp < 1660))
            buf += light(WHITE, chk * blocks)

        # the leader floods its run; in the sprint, both of them do
        lead = [lead_i] if t < 46 else [lead_i, turk_i]
        for i in lead:
            if on[i] and moving[i]:
                s = np.searchsorted(seg_hi, pp[i])
                s = min(s, 5)
                runI = keys(t, [(T_GO, 0), (T_GO + 2, 0.3), (46, 0.3), (50, 0.38), (T_WIN, 0.42), (T_WIN + 0.5, 0)])
                runI *= 1 - (HUSH[0] <= t < HUSH[1])
                col = cols[i] if i != turk_i else GOLD
                buf += light(col, runI * ((pdp >= seg_lo[s]) & (pdp <= seg_hi[s])))

        # the runners: a bright body, a comet of colour behind, bouncing with their stride
        for i in np.nonzero(on)[0]:
            x = pp[i]
            stride = 0.85 + 0.15 * np.abs(np.sin(np.pi * cad[i] * t + i)) if (moving[i] or t < T_GO) else 1.0
            done = t > fin[i] + 1.5
            hop = 0.0
            if done:
                hop = 3 * np.abs(np.sin(np.pi * 1.6 * t + i))
                stride = 0.75 + 0.15 * np.abs(np.sin(np.pi * 1.6 * t + i))
            d = pdp - x + hop
            behind = np.clip(d, 0, None)
            if kinds[i] in ('turkey', 'kid'):
                big = 1.0 if kinds[i] == 'turkey' else 0.6
                dous = 0.0
                if T_DOUSE[0] <= t < T_DOUSE[1] + 1 and kinds[i] == 'turkey':
                    dous = 1.0
                body = np.exp(-(d / (9 * big)) ** 2)
                head = np.exp(-((d + 15 * big) / (4.5 * big)) ** 2)
                tu = (d - 8 * big) / (42 * big)
                fan = (tu > 0) & (tu < 1)
                shake = 1 + 0.4 * dous * np.sin(40 * t)
                band = np.floor(tu * 4 + 0.6 * np.sin(3 * t + i)) % 3
                fanc = np.where((band == 0)[:, None], GOLD, np.where((band == 1)[:, None], AMBER, CRANBERRY))
                fanI = fan * (0.75 - 0.35 * np.clip(tu, 0, 1)) * stride * shake
                buf += light(BRONZE, 0.95 * body * stride) + light(CRANBERRY, 1.0 * head)
                buf += light(GOLD, 0.4 * big * np.exp(-(d / 50) ** 2))
                buf += light(1.0, np.clip(fanI, 0, 1)) * fanc
                if kinds[i] == 'turkey' and t > T_WIN:       # the winner glows gold
                    buf += light(GOLD, 0.5 * np.exp(-(d / 30) ** 2) * keys(t, [(T_WIN, 1), (T_WIN + 5, 0.4)]))
            else:
                body = np.exp(-(d / 8) ** 2)
                tail = np.exp(-behind / (45 if moving[i] else 8)) * (d > 0) * 0.45
                halo = 0.4 * np.exp(-(d / 34) ** 2)
                buf += light(cols[i], np.clip(0.95 * body * stride + tail * stride + halo, 0, 1))

        # finishes: the tape breaks in a gold burst and confetti; each finisher sends a wave of their colour out
        for i in range(R):
            u = t - fin[i]
            if 0 <= u < 3.0:
                big = 1.0 if (i == turk_i or fin[i] == last_t) else 0.75
                dist = np.abs(pdp - FINISH) - 650 * u
                wave = (np.exp(-(dist / 60) ** 2) + 0.6 * (dist < 0)) * np.exp(-u / 1.2)
                if big == 1.0:
                    buf += light(GOLD, 0.55 * np.exp(-u / 0.35))
                col = GOLD if i == turk_i else cols[i]
                buf += light(col, big * 0.8 * wave)
                buf += light(WHITE, big * 0.9 * np.exp(-u / 0.12) * np.exp(-((pdp - FINISH) / 60) ** 2))
        for t0, life in ((T_WIN, 5.0), (last_t, 4.0)):
            u = t - t0
            if 0 <= u < life:
                k = int(220 * (1 if t0 == T_WIN else 0.6))
                tw = (0.5 + 0.5 * np.cos(conf_ph[:k] + 2 * np.pi * 2.5 * u)) ** 2
                fade = np.clip(1 - u / life, 0, 1) * smoothstep(0, 0.4, u)
                g = np.exp(-((pdp[:, None] - conf_p[None, :k] - 15 * u) / 4) ** 2) * tw[None, :] * fade
                buf += (g[:, :, None] * conf_c[None, :k, :]).sum(1) * 0.8

        # the walker comes in to clapping: each clap a beat of gold on one wing, then the other
        for j, tc in enumerate(claps):
            u = t - tc
            if 0 <= u < 0.3:
                wing = (pdp < 893) if j % 2 == 0 else (pdp > 2033)
                buf += light(lerp(GOLD, WHITE, 0.4), 0.45 * np.exp(-u / 0.08) * wing)
        # the finale: every runner's colour parades round the house to the band, and a flash on the last chord
        if t > last_t + 0.8:
            a = smoothstep(last_t + 0.8, last_t + 2.5, t)
            ph = (pdp - 380 * (t - last_t)) / 90
            k_ = np.floor(ph).astype(int)
            stripe = np.sin(np.pi * (ph - k_)) ** 2
            buf += light(1.0, a * 0.85 * stripe * (0.75 + 0.35 * pulse)) * cols[k_ % R]
            u = t - t_end
            if 0 <= u < 2:
                buf += light(GOLD, 0.6 * np.exp(-u / 0.4))

        out[f][G.path] = np.clip(buf * keys(t, [(87.5, 1.0), (89.8, 0.0)]), 0, 1)
    return out


# ---------------------------------------------------------------- music ----------------------------------------------
# A march band at 120 bpm in 2/4, a bar to the second, with the downbeat on the GO. Dawn is strings and a flute's
# morning call; beeps count down from the start line, an air horn starts the race and the band strikes up in G. Each
# runner who goes through the water station splashes there, and the turkey's soaking stops the band for two bars. While
# the leaders are round the block the band drops to the drum cadence; when they come back in at the free end of Right
# it goes up to A and the sprint builds on a timpani roll to the tape. The trio in C carries the rest of the field home,
# a glockenspiel chime and a patter of applause for each finisher, two little gobbles for the kids, then the crowd clap
# the walker in and the band plays the tune once more, full. Every wave in the crowd is a rush of cheering that runs
# across the stereo with the light, and nothing starts in the held breath before the tape.

BAR = 1.0
E8 = BAR / 4
CH = {'G': (55, 59, 62), 'C': (55, 60, 64), 'D': (54, 57, 62), 'D7': (54, 60, 62), 'Am': (57, 60, 64),
      'A': (57, 61, 64), 'E': (56, 59, 64), 'Bm': (54, 59, 62), 'Dm': (57, 62, 65), 'F': (57, 60, 65),
      'G7': (55, 59, 65), 'E7': (56, 62, 64)}
BASS = {'G': (43, 38), 'C': (36, 43), 'D': (38, 45), 'D7': (38, 45), 'Am': (45, 40), 'A': (45, 40), 'E': (40, 47),
        'Bm': (47, 42), 'Dm': (38, 45), 'F': (41, 36), 'G7': (43, 38), 'E7': (40, 47)}
TUNE_A = [[(0, 'D4', 1), (1, 'G4', 1), (2, 'B4', 1), (3, 'G4', 1)], [(0, 'D5', 2), (2, 'B4', 1), (3, 'G4', 1)],
          [(0, 'A4', 1), (1, 'B4', 1), (2, 'C5', 1), (3, 'A4', 1)], [(0, 'B4', 2), (2, 'G4', 2)],
          [(0, 'E5', 1), (1, 'D5', 1), (2, 'C5', 1), (3, 'B4', 1)], [(0, 'A4', 1), (1, 'G4', 1), (2, 'F#4', 1),
                                                                     (3, 'A4', 1)],
          [(0, 'G4', 1), (1, 'B4', 1), (2, 'A4', 1), (3, 'F#4', 1)], [(0, 'G4', 3), (3, 'D4', 1)]]
CH_A = ['G', 'G', 'D', 'G', 'C', 'D', 'D7', 'G']
TUNE_B = [[(0, 'E4', 1), (1, 'A4', 1), (2, 'C#5', 1), (3, 'E5', 1)], [(0, 'D5', 1), (1, 'C#5', 1), (2, 'B4', 2)],
          [(0, 'D4', 1), (1, 'F#4', 1), (2, 'B4', 1), (3, 'D5', 1)], [(0, 'C#5', 1), (1, 'B4', 1), (2, 'A4', 2)],
          [(0, 'F#4', 1), (1, 'A4', 1), (2, 'D5', 1), (3, 'F#5', 1)], [(0, 'E5', 2), (2, 'C#5', 1), (3, 'A4', 1)],
          [(0, 'B4', 1), (1, 'C#5', 1), (2, 'D5', 1), (3, 'B4', 1)], [(0, 'A4', 3), (3, 'E4', 1)]]
CH_B = ['A', 'E', 'Bm', 'A', 'D', 'A', 'E7', 'A']
TRIO = [[(0, 'E4', 2), (2, 'G4', 1), (3, 'C5', 1)], [(0, 'B4', 2), (2, 'A4', 2)],
        [(0, 'F4', 2), (2, 'A4', 1), (3, 'D5', 1)], [(0, 'C5', 2), (2, 'B4', 2)],
        [(0, 'A4', 1), (1, 'B4', 1), (2, 'C5', 1), (3, 'E5', 1)], [(0, 'D5', 2), (2, 'G4', 2)],
        [(0, 'F4', 1), (1, 'E4', 1), (2, 'D4', 1), (3, 'B3', 1)], [(0, 'C4', 4)]]
CH_T = ['C', 'G', 'F', 'C', 'Am', 'G', 'G7', 'C']
MORNING = [(0.0, 'D5', 0.9), (1.0, 'B4', 0.45), (1.5, 'G4', 0.45), (2.0, 'A4', 0.45), (2.5, 'B4', 0.45),
           (3.0, 'D5', 1.4), (4.6, 'E5', 0.45), (5.1, 'D5', 0.45), (5.6, 'B4', 0.45), (6.1, 'A4', 1.6)]


def score(M, G):
    from pixelhome.audio import SR, note, slide, whoosh
    n = note
    tpt = M.sampler('Brass/Trumpet/stac/*.wav', tune=-12)
    tpt_s = M.sampler('Brass/Trumpet/sus/*.wav', tune=-12)
    horn = M.sampler('Brass/F Horn/stac/*.wav', tune=-12)
    horn_s = M.sampler('Brass/F Horn/sus/*.wav', tune=-12)
    bone = M.sampler('Brass/Tenor Trombone/sus/*.wav', tune=-12)
    tuba = M.sampler('Brass/Tuba/stac/*.wav', tune=-12)
    tuba_s = M.sampler('Brass/Tuba/sus/*.wav', tune=-12)
    picc = M.sampler('Woodwinds/Piccolo/Stac/*.wav', tune=-12)
    flute = M.sampler('Woodwinds/Flute/susvib/*.wav', tune=-12)
    clar = M.sampler('Woodwinds/Clarinet/stac/*.wav', tune=-12)
    clar_s = M.sampler('Woodwinds/Clarinet/susLong/*.wav', tune=-12)
    vln = M.sampler('Strings/Violin Section/susVib/*.wav', tune=-12)
    vla = M.sampler('Strings/Viola Section/susvib/*.wav', tune=-12)
    cello = M.sampler('Strings/Cello Section/susvib/*.wav', tune=-12)
    trem = M.sampler('Strings/Violin Section/Trem/*.wav', tune=-12)
    pizz = M.sampler('Strings/Violin Section/Pizz/*.wav', tune=-12)
    harp = M.sampler('Strings/Harp/*.wav')
    glock = M.sampler('Percussion/Glock/*.wav', tune=-12)
    xylo = M.sampler('Percussion/Xylo/*.wav', tune=-12)
    snare = M.hits('VSCO 1 Percussion/drums/snare/drum3_marching/snare3_[mp]*.wav')
    snare_f = M.hits('VSCO 1 Percussion/drums/snare/drum3_marching/snare3_f*.wav')
    sroll = M.hits('Percussion/Snare2-rollSN_v[35]*.wav')
    bd = M.hits('VSCO 1 Percussion/drums/bass/bdrum_f_*.wav')
    bd_ff = M.hits('VSCO 1 Percussion/drums/bass/bdrum_fff_*.wav')
    tenor = M.hits('VSCO 1 Percussion/drums/tenor/tenor_higher/*.wav')
    clash = M.hits('VSCO 1 Percussion/varMetal/Cymbals/clash/crash_hit_ff*.wav')
    timp = M.hits('Percussion/Timpani/Timpani1_Hit*.wav')
    troll = M.hits('Percussion/Timpani/Rolls/Timpani1_Roll*.wav')
    wood = M.hits('VSCO 1 Percussion/varWood/claves_m*.wav')
    tri = M.hits('Percussion/Triangle3-Hit_v1*.wav')
    slap = M.hits('VSCO 1 Percussion/varWood/slapstick[0-9].wav')
    bubbles = M.hits('Miscellania Raw/Misc 1/bubbles*.wav')

    for name, gain, rev in (('tune', 0.26, 0.18), ('horns', 0.17, 0.2), ('bass', 0.34, 0.06), ('drums', 0.26, 0.12),
                            ('wind', 0.22, 0.22), ('strings', 0.2, 0.3), ('bells', 0.22, 0.25), ('fx', 0.2, 0.2),
                            ('crowd', 0.12, 0.3), ('signal', 0.09, 0.15), ('gobble', 0.2, 0.15)):
        M.bus(name, gain=gain, reverb=rev)
    M.fader('crowd', [(0, -6), (T_GO - 0.5, -6), (T_GO, 0), (34, -2), (36, -6), (43, -3), (44, 0), (HUSH[0] - 0.1, 0),
                      (HUSH[0], -14), (HUSH[1] - 0.02, -14), (HUSH[1], 0), (D, 0)])
    add = M.add

    def hushed(bus, sig, t=0.0, gain=1.0, pan=None):     # the held breath before the tape: nothing starts in it
        if HUSH[0] - 0.02 <= t < HUSH[1] - 0.02 and bus != 'crowd':
            return
        add(bus, sig, t, gain, pan)
    M.add = hushed

    L = G.length
    order = np.argsort(G.pd)
    xs, ds = G.pos[order, 0], G.pd[order]
    x0, x1 = xs.min(), xs.max()

    def pan_at(d):
        x = np.interp(np.clip(d, 0, L), ds, xs)
        return float(0.85 * (2 * (x - x0) / (x1 - x0) - 1))

    def moving(sig, t0, ts, ps):            # constant-power pan that follows (time, pan) points
        tt = t0 + np.arange(sig.shape[1]) / SR
        a = (np.clip(np.interp(tt, ts, ps), -1, 1) + 1) * np.pi / 4
        return sig * np.vstack([np.cos(a), np.sin(a)]) * np.sqrt(2)

    def mono(sig):
        return np.vstack([sig, sig])

    def gobble(dur=0.75, f0=480.0, rate=11.0, seed=0):
        """A turkey's gobble: a buzzy, fast warble of syllables falling in pitch."""
        r = np.random.default_rng(seed)
        tt = np.arange(int(dur * SR)) / SR
        ph = (tt * rate * (1 + 0.15 * tt / dur)) % 1
        f = f0 * (1 + 0.32 * np.sin(2 * np.pi * ph)) * (1 - 0.22 * tt / dur)
        phase = 2 * np.pi * np.cumsum(f) / SR
        sig = sum(np.exp(-((k * f - 1400) / 1100) ** 2) / k ** 0.5 * np.sin(k * phase) for k in range(1, 10))
        syl = np.sin(np.pi * ph) ** 0.6 * r.uniform(0.6, 1.0, int(dur * rate * 1.2) + 2)[(tt * rate).astype(int)]
        rasp = np.convolve(r.normal(0, 1, len(tt)), np.ones(6) / 6, 'same') * 0.25
        env = np.clip(tt / 0.02, 0, 1) * np.clip((dur - tt) / 0.12, 0, 1)
        out = (sig / 3 + rasp) * syl * env
        return mono(out / (np.abs(out).max() + 1e-9))

    def beep(f, dur):
        tt = np.arange(int(dur * SR)) / SR
        env = np.clip(tt / 0.005, 0, 1) * np.clip((dur - tt) / 0.02, 0, 1)
        return mono(env * (np.sin(2 * np.pi * f * tt) + 0.3 * np.sign(np.sin(2 * np.pi * f * tt)) * 0.3))

    def air_horn(dur):
        tt = np.arange(int(dur * SR)) / SR
        sig = np.zeros_like(tt)
        for f in (233.1, 234.4, 293.7, 295.0, 349.2):
            ph = 2 * np.pi * f * tt * (1 + 0.004 * np.sin(2 * np.pi * 5 * tt))
            sig += sum(np.sin(k * ph) / k for k in range(1, 12))
        env = np.clip(tt / 0.03, 0, 1) * np.clip((dur - tt) / 0.08, 0, 1)
        spec = np.fft.rfft(sig * env)
        fq = np.fft.rfftfreq(len(tt), 1 / SR)
        spec *= np.exp(-((fq - 1100) / 1300) ** 2) + 0.3
        out = np.fft.irfft(spec, len(tt))
        return mono(out / np.abs(out).max())

    def noise_band(N, lo, hi, seed):
        r = np.random.default_rng(seed)
        spec = np.fft.rfft(r.normal(0, 1, (2, N)), axis=1)
        fq = np.fft.rfftfreq(N, 1 / SR)
        spec *= (fq / lo) ** 2 / (1 + (fq / lo) ** 2) / (1 + (fq / hi) ** 2)
        x = np.fft.irfft(spec, N, axis=1)
        return x / np.abs(x).max()

    def applause(dur, rate, seed):
        """Many hands: short noise bursts at random, banded like claps."""
        r = np.random.default_rng(seed)
        N = int(dur * SR)
        out = np.zeros((2, N))
        k = np.arange(int(0.012 * SR))
        for ch in range(2):
            times = r.uniform(0, dur, int(rate * dur))
            for tc in times:
                s = int(tc * SR)
                b = r.normal(0, 1, len(k)) * np.exp(-k / (0.0025 * SR)) * r.uniform(0.3, 1)
                e = min(N, s + len(k))
                out[ch, s:e] += b[:e - s]
        spec = np.fft.rfft(out, axis=1)
        fq = np.fft.rfftfreq(N, 1 / SR)
        spec *= np.exp(-((np.log2(fq + 1) - np.log2(1600)) / 1.2) ** 2)
        out = np.fft.irfft(spec, N, axis=1)
        env = np.clip(np.arange(N) / (0.1 * SR), 0, 1) * np.clip((N - np.arange(N)) / (0.6 * SR), 0, 1)
        return out * env / (np.abs(out).max() + 1e-9)

    def at(k, e=0.0):
        return T_GO + k * BAR + e * E8

    def tune(bars, k0, inst, bus='tune', vel=100, pan=0.0, long=None, gain=1.0, shift=0):
        for j, b in enumerate(bars):
            for e, m, ln in b:
                pl = long if (long is not None and ln >= 2) else inst
                M.add(bus, pl.play(n(m) + shift, vel, dur=ln * E8 * 0.92), at(k0 + j, e), gain, pan)

    def band(k0, chords, vel=100, drums=True, horns=True, gain=1.0):
        for j, c in enumerate(chords):
            k = k0 + j
            for b in (0, 1):
                M.add('bass', tuba.play(BASS[c][b], vel - 6 * b), at(k, 2 * b), gain)
                if horns:
                    for m in CH[c]:
                        M.add('horns', horn.play(m, vel - 18), at(k, 2 * b + 1), 0.5 * gain, -0.25)
            if drums:
                M.add('drums', bd.play(vel), at(k), 0.9 * gain)
                M.add('drums', bd.play(vel - 20), at(k, 2), 0.7 * gain)
                pat = (0, 1, 1.5, 2, 3) if j % 4 == 3 else (0, 1, 2, 3)
                for e in pat:
                    M.add('drums', (snare_f if e in (0, 2) else snare).play(vel + 5 if e in (0, 2) else vel - 25),
                          at(k, e), 0.7 * gain, 0.15)

    pos, fin, rank = field()
    tf = np.arange(len(pos)) * DT
    kinds = [f[2] for f in FIELD]
    turk = kinds.index('turkey')
    lime = kinds.index('lime')

    def pan_of(i, t):
        p = np.interp(t, tf, np.nan_to_num(pos[:, i], nan=-1))
        return pan_at(p) if p >= 0 else -0.9

    # ---- the crowd: a bed of voices all morning, a cheer that follows the leaders, roars for the big moments ----
    N = int(D * SR)
    voices = noise_band(N, 350, 2200, 3)
    tt = np.arange(N) / SR
    babble = 1 + 0.3 * np.sin(2 * np.pi * 1.3 * tt) * np.sin(2 * np.pi * 0.27 * tt + 1)
    lvl = [(0, 0.0), (2.5, 0.25), (T_GO, 0.3), (T_GO + 0.3, 1.2), (T_GO + 4, 0.5), (34, 0.5), (50, 0.65),
           (T_WIN - 0.3, 1.0), (T_WIN + 0.3, 1.6), (T_WIN + 5, 0.6), (fin.max() - 4, 0.7), (fin.max() + 0.2, 1.6),
           (fin.max() + 4, 0.7), (D, 0.6)]
    env = np.interp(tt, tt[::480], [keys(t, lvl) for t in tt[::480]])
    M.add('crowd', voices * babble * env, 0.0)
    for t0, dur, sd in ((T_GO, 3.0, 4), (T_WIN, 6.0, 5), (fin.max(), 6.0, 6)):
        M.add('crowd', whoosh(dur, 400, 2600, 1.2, seed=sd), t0 - 0.2, 1.0)
        M.add('crowd', applause(dur + 2, 160, sd), t0 + 0.3, 1.3)
    M.add('crowd', applause(D - 4, 25, 9) * 0.5, 2.0, 1.0)              # some clap the whole way

    # ---- the wave: each one a rush of cheering that runs across the stereo with the light ----
    for j, (tw, dr) in enumerate(WAVES):
        w = whoosh(WAVE_T + 0.3, 500, 2600, 1.0, seed=40 + j) + applause(WAVE_T + 0.3, 500, 40 + j) * 0.8
        ps_ = [pan_at(0), pan_at(L)] if dr > 0 else [pan_at(L), pan_at(0)]
        M.add('crowd', moving(w, tw, [tw, tw + WAVE_T], ps_), tw, 1.1)
        M.add('drums', tenor.play(95), tw, 0.4, ps_[0])
    # here they come: a rising roar and a snare build at the free end of Right
    r = sroll.play(80, dur=43.6 - 39.0)
    M.add('drums', r * np.linspace(0.05, 1, r.shape[1]) ** 2, 39.0, 0.5, pan_at(FREE))
    M.add('crowd', whoosh(4.6, 300, 2400, 1.0, seed=41) * np.linspace(0.1, 1, int(4.6 * SR)) ** 2, 39.0, 1.0,
          pan_at(FREE))

    # ---- 0-8.5: dawn. Strings, the flute's morning call; runners jog in from the free end of Right ----
    for m, inst, v in ((n('G2'), cello, 55), (n('D3'), cello, 50), (n('B3'), vla, 48), (n('D4'), vln, 46)):
        M.add('strings', inst.play(m, v, dur=8.0, release=1.2), 0.5, 1.0)
    for b, m, d in MORNING:
        M.add('wind', flute.play(n(m), 78, dur=d, release=0.25), 1.2 + b, 1.0, 0.1)
    for i in range(16):
        M.add('strings', harp.play([43, 50, 55, 59, 62, 67][i % 6] + 12 * (i // 6 % 2), 62), 0.6 + 0.48 * i, 0.6, 0.3)
    for i in range(R):                       # jogging footsteps as each arrives
        t_in = 1.5 + 0.35 * i
        arrive = t_in + (2600 - GRID[i]) / 170
        for s in np.arange(max(t_in, t_in + (2600 - FREE) / 170), arrive, 0.32):
            M.add('fx', wood.play(int(M.rng.integers(40, 70))), s, 0.25, pan_of(i, s))
    M.add('gobble', gobble(0.7, 470, seed=1), 6.2, 0.8, pan_of(turk, 6.2))

    # ---- countdown and the horn ----
    ps = pan_at(START)
    for tc in COUNT:
        M.add('signal', beep(784, 0.3), tc, 1.0, ps)
        M.add('drums', timp.play(80), tc, 0.4, ps)
    M.add('signal', beep(1568, 0.6), T_GO, 1.0, ps)
    M.add('fx', air_horn(1.3), T_GO, 0.9, ps)
    M.add('drums', clash.play(120), T_GO, 0.8)
    M.add('drums', bd_ff.play(120), T_GO, 0.9)

    # ---- the march in G, from the GO until the leaders go round the back (bars 0-23) ----
    band(0, ['G', 'G'], horns=False)
    band(2, CH_A + CH_A)
    tune(TUNE_A, 2, tpt, long=tpt_s)
    tune(TUNE_A, 2, glock, 'bells', 80, 0.1, gain=0.4)
    tune(TUNE_A, 10, tpt, long=tpt_s)
    tune(TUNE_A, 10, picc, 'wind', 84, -0.1, gain=0.7, shift=12)
    # bars 18-23: the water station; the turkey's soaking stops the band at bar 20 for two bars
    band(18, ['C', 'D'])
    tune(TUNE_A[4:6], 18, tpt, long=tpt_s)
    band(22, ['G', 'D'], vel=95)
    tune([TUNE_A[6], TUNE_A[7]], 22, tpt, long=tpt_s)
    dous = T_DOUSE[0]
    pt = pan_of(turk, dous)
    M.add('bass', tuba_s.play(n('G1'), 110, dur=0.8), dous, 1.0, pt)
    M.add('fx', slide(0.0, 0.7, 1300, 380, 0.8, 0.5), dous + 0.05, 0.9, pt)
    M.add('fx', bubbles.play(110, dur=1.6), dous + 0.1, 0.9, pt)
    M.add('fx', noise_band(int(0.6 * SR), 900, 6000, 12) * np.exp(-np.arange(int(0.6 * SR)) / (0.12 * SR)),
          dous, 0.9, pt)
    M.add('gobble', gobble(0.9, 430, rate=13, seed=2), dous + 0.9, 1.0, pt)
    M.add('drums', slap.play(110), dous + 1.8, 0.8, pt)
    for i in range(R):                       # every runner through the station: a splash and a plink
        p = np.nan_to_num(pos[:, i], nan=-1)
        hit = np.nonzero((p > 0) & (p < 700) & (tf > T_GO))[0]
        if len(hit) and i != turk:
            t = tf[hit[0]]
            pp = pan_at(700)
            M.add('strings', pizz.play(n('G5') + [0, 2, 4, 7, 9][i % 5], 90), t, 0.9, pp)
            M.add('fx', noise_band(int(0.25 * SR), 1500, 7000, 20 + i) * np.exp(-np.arange(int(0.25 * SR)) /
                                                                                  (0.04 * SR)), t, 0.35, pp)

    # ---- bars 24-31: round the block; the band drops to the drum cadence ----
    for k in range(24, 32):
        for e in range(4):
            M.add('drums', (snare_f if e == 0 else snare).play(100 if e == 0 else 75), at(k, e), 0.7, 0.1)
            if k % 2:
                M.add('drums', snare.play(60), at(k, e + 0.5), 0.5, 0.1)
        M.add('drums', bd.play(95), at(k), 0.8)
        M.add('drums', bd.play(80), at(k, 2), 0.6)
        for e, v in ((0, 100), (1.5, 80), (2, 90), (3, 70)) if k % 2 else ((0, 100), (2, 90)):
            M.add('drums', tenor.play(v), at(k, e), 0.5, -0.3)
    for k in range(28, 32):                  # clarinets creep in under it
        M.add('wind', clar_s.play(n('E4') + (k - 28), 60 + 6 * (k - 28), dur=0.95), at(k), 0.8, 0.0)

    # ---- bars 32-43: back in at the free end of Right; up to A for the sprint ----
    M.add('drums', clash.play(115), at(32), 0.7, pan_at(FREE))
    for i, m in enumerate(('E4', 'A4', 'C#5', 'E5')):
        M.add('tune', tpt.play(n(m), 115, dur=0.2), at(31, 2 + 0.5 * i), 0.9, pan_at(FREE))
    band(32, CH_B + CH_B[:4], vel=108, gain=1.05)
    tune(TUNE_B, 32, tpt, long=tpt_s, vel=110)
    tune(TUNE_B[:4], 40, tpt, long=tpt_s, vel=115)
    tune(TUNE_B, 32, glock, 'bells', 86, 0.1, gain=0.4)
    for k in range(36, 44):                  # strings saw away underneath, louder toward the tape
        c = (CH_B + CH_B[:4])[k - 32]
        for m in CH[c]:
            M.add('strings', trem.play(m + 12, 60 + 6 * (k - 36), dur=BAR), at(k), 0.6)
    t_back = TURKEY[5][0]
    M.add('gobble', gobble(0.8, 520, rate=12, seed=3), t_back + 0.3, 1.1, pan_at(FREE - 40))
    M.add('horns', bone.play(n('A2'), 110, dur=0.8), t_back + 0.2, 0.9, pan_at(FREE))
    M.add('crowd', whoosh(1.8, 300, 1800, 1.0, seed=8), t_back, 0.9, pan_at(FREE - 100))
    r = troll.play(90, dur=HUSH[0] - 51)
    M.add('drums', r * np.linspace(0.15, 1, r.shape[1]) ** 2, 51.0, 0.6, pan_at(1600))
    r = sroll.play(90, dur=HUSH[0] - 52)
    M.add('drums', r * np.linspace(0.1, 1, r.shape[1]) ** 2, 52.0, 0.4)
    for t in (53.0, 53.8, 54.6):             # the lead changes hands
        M.add('wind', xylo.play(n('A5'), 100), t, 0.6, pan_of(turk, t))
        M.add('wind', xylo.play(n('E5'), 100), t + 0.12, 0.6, pan_of(lime, t))

    # ---- the tape: bar 44 ----
    pf = pan_at(FINISH)
    M.add('drums', clash.play(127), T_WIN, 1.0, pf)
    M.add('drums', bd_ff.play(127), T_WIN, 1.0, pf)
    M.add('drums', timp.play(127), T_WIN, 0.9, pf)
    M.add('bass', tuba_s.play(n('A1'), 120, dur=1.8), T_WIN, 1.0)
    for m in CH['A']:
        M.add('tune', tpt_s.play(m + 12, 118, dur=1.8), T_WIN, 0.5)
        M.add('horns', horn_s.play(m, 112, dur=1.8), T_WIN, 0.6)
    M.add('gobble', gobble(1.0, 560, rate=12, seed=4), T_WIN + 0.5, 1.2, pf)
    sparkle = [n(m) for m in ('A5', 'C#6', 'E6', 'A6')]
    for j in range(24):
        M.add('bells', glock.play(sparkle[j % 4], 80), T_WIN + 0.1 + 0.11 * j, 0.5, float(M.rng.uniform(-0.8, 0.8)))

    # ---- bars 46-68: the trio carries the rest of the field home; a chime and a patter for each finisher ----
    trio_chords = CH_T + CH_T + CH_T[:6]
    band(46, trio_chords[:16], vel=88, horns=False, gain=0.85)
    band(62, trio_chords[16:22], vel=80, drums=False, horns=False, gain=0.8)
    tune(TRIO, 46, clar, 'wind', 96, -0.1, long=clar_s)
    tune(TRIO, 46, flute, 'wind', 70, 0.1, gain=0.5, shift=12)
    tune(TRIO, 54, tpt, 'tune', 92, long=tpt_s, gain=0.8)
    tune(TRIO[:6], 62, clar, 'wind', 84, -0.1, long=clar_s)
    for k in range(46, 68):
        c = trio_chords[k - 46]
        for e in (1, 3):
            for m in CH[c]:
                M.add('strings', pizz.play(m, 70), at(k, e), 0.5, 0.2)
    chimes = [n(m) for m in ('C5', 'D5', 'E5', 'G5', 'A5', 'C6')]
    for i in range(R):
        if kinds[i] in ('turkey', 'lime') or fin[i] >= fin.max():
            continue
        M.add('bells', glock.play(chimes[rank[i] % 6], 95), fin[i], 0.8, pf)
        M.add('crowd', applause(2.5, 90, 30 + i), fin[i], 0.7, pf)
    M.add('bells', glock.play(n('E5'), 95), fin[lime], 0.8, pf)
    for i in range(R):
        if kinds[i] == 'kid':
            M.add('gobble', gobble(0.45, 760, rate=14, seed=10 + i), fin[i] + 0.2, 0.8, pf)

    # ---- bars 66-69: the crowd clap the walker in, faster and faster ----
    t_walk = fin.max()
    claps = clap_times(t_walk)
    for tc in claps:
        M.add('crowd', applause(0.25, 1400, int(tc * 100)), tc, 1.2, 0.0)
        M.add('drums', snare.play(70), tc, 0.4, 0.1)
    walker = kinds.index('walk')
    for s in np.arange(68.0, t_walk, 0.6):   # slow, steady steps
        M.add('fx', wood.play(60), s, 0.3, pan_of(walker, s))

    # ---- bar 69 on: the walker crosses the line; the tune once more, full, and the last chord ----
    M.add('drums', clash.play(120), t_walk, 0.9, pf)
    M.add('drums', bd_ff.play(120), t_walk, 0.9, pf)
    k0 = int(round((t_walk - T_GO) / BAR))
    band(k0, CH_A[2:], vel=110)
    tune(TUNE_A[2:], k0, tpt, long=tpt_s, vel=112)
    tune(TUNE_A[2:], k0, picc, 'wind', 80, -0.1, gain=0.6, shift=12)
    tune(TUNE_A[2:], k0, glock, 'bells', 86, 0.1, gain=0.4)
    for k in range(k0, k0 + 6):
        for m in CH[CH_A[2 + k - k0]]:
            M.add('strings', vln.play(m + 12, 75, dur=BAR), at(k), 0.5)
    tend = at(k0 + 6)
    for m in CH['G']:
        M.add('tune', tpt_s.play(m + 12, 115, dur=2.0), tend, 0.5)
        M.add('horns', horn_s.play(m, 110, dur=2.2), tend, 0.6, -0.2)
        M.add('strings', vln.play(m + 12, 85, dur=2.2), tend, 0.5)
    M.add('bass', tuba_s.play(n('G1'), 118, dur=2.4), tend)
    M.add('drums', clash.play(118), tend, 0.8)
    M.add('drums', bd_ff.play(118), tend, 0.9)
    M.add('bells', glock.play(n('G5'), 100), tend, 0.6)
    M.add('gobble', gobble(0.7, 500, seed=5), tend + 0.8, 0.8, pf)
    M.add('fx', tri.play(90), tend + 0.05, 0.4)
