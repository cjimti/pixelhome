"""Toy Soldiers: The Porch Front is a toy box. Its lid splits open in gold light and a drum major (white plume,
twirling gold mace) high-steps out, a corps of twenty tin soldiers behind him (red coats, white crossbelts, gold
shakos), a step on every beat, each glinting as it turns a corner, round the porch and out along Right. Company,
halt: two stamps, an about-face, and the drum major scampers back down the line to the new front. They march
back round the porch to the Left wing, where a little green box is waiting. It cranks, they mark time, and a
jack-in-the-box springs out in rainbow coils: the whole column jumps back and trembles. The jack sinks away; the
soldiers fall in, spreading out to stand at attention all round the house, and salute in a ripple. A toy cannon
rolls in from the free end of Right; its fuse fizzes and it fires: a puff of smoke, and a cork that knocks the
last soldier over, and the whole line topples like dominoes round the porch, along Left and up Side. Silence,
a twitch, then the drum major springs up with a whistle and the soldiers pop back up one by one, faster and
faster. About face, and they quick-march off down Side in the grand finale, red, white and gold bunting filling
the house behind them, the drum major the last to go, and the cannon fires a salvo of confetti.

The music is an original march at 120 bpm in B flat: a drum corps cadence, then the first strain on fife-like
flute and xylophone over tuba oom-pahs and off-beat horns, every step a bass drum. Every soldier who comes out of
the box is a glock pop, every corner a rim click; the halt and the about-face are stamps. The second strain is on
trumpets. The jack gets a wind-up ratchet and a little crank tune, a pop, a boing and a startled brass stab over
tremolo strings. The fall-in is a sixteenth-note snare fill under a rising xylophone; the salute is a trumpet
fanfare; the cannon is a fizz, a bass-drum boom and a cork pop, and the dominoes are a run of wood clicks down a
falling xylophone line, with a trombone wah at the end. Each soldier springing up is the next note of a rising
scale, and the finale is the trio in E flat, full band and cymbals, to a cannon boom on the last downbeat."""
import numpy as np
from pixelhome.fx import DT, hexc, perc, light, keys, smoothstep, lerp, nframes

CODE = 'XM17'
TITLE = 'Toy Soldiers'
KIND = 'show'
DESCRIPTION = ('Tin soldiers march out of the toy box and round the roof in step, until a jack-in-the-box startles '
               'them and a toy cannon topples the whole line like dominoes. Up they spring, one by one, for the '
               'grand march off.')
VOICEOVER = "Left, right, left! The tin soldiers are on parade, so everybody stand up straight."

RED = hexc('#ff1006')
WHITE = hexc('#fff2e0')
GOLD = hexc('#ffa800')
GREEN = hexc('#08a822')
DEEP = hexc('#033c0c')
BRONZE = hexc('#e07010')
TAN = hexc('#ffb860')
SMOKE = hexc('#b0b4c8')
SPRING = np.array([hexc('#ff1880'), hexc('#ffd000'), hexc('#10b8ff'), hexc('#30ff30')])
CONF = np.array([RED, GOLD, WHITE, GREEN, hexc('#10b8ff')])
BUNT = np.array([RED, WHITE, GOLD])

D = 86.5
SEED = 17
BEAT = 0.5                                       # 120 bpm
BAR = 4 * BEAT


def at(bar, beat=0.0):
    return bar * BAR + beat * BEAT


CORNERS = (490.0, 892.0, 1311.0, 1660.0, 2033.0)
BOX = 1485.0                                     # the toy box: the middle of the Porch Front
JACK = 540.0                                     # the jack-in-the-box, on the Left wing
NS = 20                                          # soldiers; troupe index 0 is the drum major
OFF = np.r_[0.0, 55 + 47 * np.arange(NS)]        # how far each one marches behind the drum major
T_OUT = at(2)                                    # out of the box, a step a beat, 30 units a step
T_HALT = at(10)                                  # company, halt: stamps on beats 1 and 2
T_FACE = at(10, 2)                               # about face; the drum major runs back to the front
T_BACK = at(12)                                  # march back left, 33 units a step
T_MARK = at(18)                                  # mark time at the jack's box while it cranks
T_POP = at(20)                                   # the jack springs out
T_SINK = at(21, 2)                               # and sinks away
T_FALLIN = at(22)                                # spread out round the house, 16 half-beat steps
T_ATTN = at(24)                                  # attention; the cannon rolls in on the four beats
T_FUSE = at(25)
T_BOOM = at(26)
CORK_FLY = 0.35
V_DOM = 650.0                                    # how fast the dominoes run round the house
T_DM_UP = at(29)
T_UP0 = at(30)
UP_GAPS = [4, 4, 3, 3, 3, 3, 2, 2, 2, 2, 2, 2, 1, 1, 1, 1, 1, 1, 1]     # in sixteenths: faster and faster
T_TURN = at(32, 3)                               # about face
T_MARCH = at(33)                                 # quick march off down Side: 33 units every half beat
T_END = at(42)                                   # the last downbeat: confetti
SLOTS = np.linspace(130, 2265, NS + 1)
DM_SLOT = int(np.argmin(np.abs(SLOTS - BOX)))
SALUTES = (at(24), at(25))


def stepper(t, t0, period, n):
    """Steps taken: n steps of `period` from t0, each a quick move then a hold."""
    b = np.clip((t - t0) / period, 0, n)
    k = np.floor(b)
    return np.minimum(n, k + smoothstep(0.0, 0.6, b - k))


def troupe():
    """The drum major and soldiers frame by frame: position along the path, facing, visibility, how far fallen,
    white flashes and gold glints; and the events the score needs."""
    F = nframes(D)
    S = NS + 1
    P, FACE, VIS, FALL = (np.zeros((F, S)) for _ in range(4))
    end1 = 2445 - OFF
    end2 = end1.copy()
    end2[0] = 1442.0
    end3 = end2 - 33 * 24
    rank = np.argsort(np.argsort(np.abs(end3 - JACK)))
    t_jolt = T_POP + 0.03 * rank
    end4 = end3 + 36
    tgt = np.zeros(S)
    tgt[0] = SLOTS[DM_SLOT]
    tgt[1 + np.argsort(end4[1:])] = np.delete(SLOTS, DM_SLOT)
    face5 = np.sign(tgt - end4)
    t_fall = T_BOOM + CORK_FLY + (tgt.max() - tgt) / V_DOM
    order_up = 1 + np.argsort(tgt[1:])
    t_up = np.zeros(S)
    t_up[0] = T_DM_UP
    t_up[order_up] = T_UP0 + np.r_[0, np.cumsum(UP_GAPS)] * BEAT / 4
    last = int(np.argmax(tgt))
    for f in range(F):
        t = f * DT
        if t < T_HALT:
            p = 1485 + 30 * stepper(t, T_OUT, BEAT, 32) - OFF
            fc = np.ones(S)
            vis = smoothstep(BOX, BOX + 16, p)
        elif t < T_BACK:
            p = end1.copy()
            p[0] = 2445 + (1442 - 2445) * stepper(t, T_FACE, BEAT / 4, 10) / 10
            fc = np.where(t < T_FACE, 1.0, -1.0) * np.ones(S)
            vis = np.ones(S)
        elif t < T_POP:
            p = end2 - 33 * stepper(t, T_BACK, BEAT, 24)
            fc, vis = -np.ones(S), np.ones(S)
        elif t < T_FALLIN:
            shake = 3.0 * np.sin(2 * np.pi * 9 * t + np.arange(S)) * keys(t, [(T_POP, 1.0), (T_POP + 1.8, 0.0)])
            p = end3 + 36 * smoothstep(t_jolt, t_jolt + 0.12, t) + np.where(t > t_jolt, shake, 0)
            fc, vis = -np.ones(S), np.ones(S)
        elif t < T_MARCH:
            p = lerp(end4, tgt, stepper(t, T_FALLIN, BEAT / 2, 16) / 16)
            fc = face5.copy() if t < T_ATTN else np.ones(S)
            if t >= T_TURN:
                fc = -np.ones(S)
            vis = np.ones(S)
        else:
            m = stepper(t, T_MARCH, BEAT / 2, 80)
            p = tgt - 33 * m
            p[0] = min(tgt[0], p[last] + 60)
            fc = -np.ones(S)
            vis = smoothstep(-12, 8, p)
        fall = np.clip((t - t_fall) / 0.22, 0, 1) ** 2
        fall = np.where(t >= t_up, 1 - smoothstep(t_up, t_up + 0.1, t), fall)
        P[f], FACE[f], VIS[f], FALL[f] = p, fc, vis, fall
    tt = np.arange(F)[:, None] * DT
    # white flashes: the about-faces, the startle, the salutes, each landing on the floor
    FLASH = np.zeros((F, S))
    for t0, who in ((T_FACE, np.arange(S) > 0), (T_ATTN, face5 < 0), (T_TURN, np.ones(S, bool))):
        FLASH += who[None] * np.where(tt >= t0, np.exp(-(tt - t0) / 0.15), 0)
    FLASH += np.where(tt >= t_jolt, 1.2 * np.exp(-(tt - t_jolt) / 0.3), 0)
    for ts in SALUTES:
        t0 = ts + np.abs(tgt - tgt[0]) / 2400
        FLASH += 0.8 * np.exp(-((tt - t0) / 0.07) ** 2)
    land = t_fall + 0.22
    FLASH += np.where((tt >= land) & (tt < t_up), 0.9 * np.exp(-(tt - land) / 0.12), 0)
    # gold glints: turning a corner, springing back up
    GLINT = np.where(tt >= t_up, 1.4 * np.exp(-(tt - t_up) / 0.3), 0)
    turns = []
    for c in CORNERS:
        side = np.sign(P - c)
        for f, i in zip(*np.nonzero((side[1:] != side[:-1]) & (VIS[1:] > 0.5))):
            tc = (f + 1) * DT
            turns.append((tc, i, c))
            GLINT[f + 1:] += np.exp(-(tt[f + 1:, 0] - tc) / 0.25)[:, None] * (np.arange(S) == i)
    turns.sort()
    return dict(P=P, FACE=FACE, VIS=VIS, FALL=FALL, FLASH=FLASH, GLINT=GLINT, tgt=tgt, t_jolt=t_jolt,
                t_fall=t_fall, t_up=t_up, turns=turns, end1=end1, order_up=order_up, last=last)


def cannon(t):
    """Where the cannon's middle is: four squeaky rolls in from past the free end of Right, a kick at each shot."""
    c = 2575 - 26 * stepper(t, T_ATTN, BEAT, 4)
    for tb in (T_BOOM, T_END):
        if t > tb:
            c += 22 * np.exp(-(t - tb) / 0.3)
    return float(c)


def cork(t):
    """The cork: out of the mouth, onto the last soldier, then three little bounces back."""
    hit = T_BOOM + CORK_FLY
    x0 = cannon(T_BOOM) - 34
    pts = [(T_BOOM, x0), (hit, SLOTS[-1] + 12), (hit + 0.4, SLOTS[-1] + 70), (hit + 0.7, SLOTS[-1] + 105),
           (hit + 0.9, SLOTS[-1] + 122)]
    return float(np.interp(t, [p[0] for p in pts], [p[1] for p in pts]))


CORK_BOUNCES = [T_BOOM + CORK_FLY + d for d in (0.0, 0.4, 0.7, 0.9)]


def inside(r, a, b, soft=1.5):
    return smoothstep(a - soft, a + soft, r) * (1 - smoothstep(b - soft, b + soft, r))


def render(G, seed=SEED):
    rng = np.random.default_rng(seed)
    F = nframes(D)
    out = np.zeros((F, G.N, 3))
    x = G.pd[G.path]
    tr = troupe()
    P, FACE, VIS, FALL, FLASH, GLINT = (tr[k] for k in ('P', 'FACE', 'VIS', 'FALL', 'FLASH', 'GLINT'))
    S = NS + 1
    scale = np.r_[1.35, np.ones(NS)]
    gold_dot = ((x + 24) % 96) < 9
    porch = (x > 1311) & (x < 1660)
    fuse_fl = rng.uniform(0.5, 1.0, F)
    nconf = 240
    cv = rng.uniform(250, 2600, nconf)
    cc = CONF[rng.integers(0, len(CONF), nconf)]
    clife = rng.uniform(1.4, 2.6, nconf)
    ctw = rng.uniform(0, 2 * np.pi, nconf)

    for f in range(F):
        t = f * DT
        fr = np.zeros((G.N, 3))
        master = keys(t, [(0, 0.0), (0.6, 1.0), (D - 1.8, 1.0), (D - 0.2, 0.0)])

        # the toy room: green shelves with gold studs, lifting a little on every beat
        lvl = keys(t, [(0, 0.0), (1.5, 0.26), (55.0, 0.26), (56.5, 0.14), (58.0, 0.14), (60.0, 0.26),
                       (T_MARCH, 0.26), (T_END + 1, 0.14)])
        pulse = np.exp(-(t % BEAT) / 0.12) * (1.6 if (t % BAR) < BEAT else 1.0)
        if 52.0 < t < 60.0:
            pulse = 0.0
        bed_i = lvl * (1 + 0.22 * pulse) * np.where(gold_dot, 1.4, 1.0)
        bed = light(GREEN, bed_i * ~gold_dot) + light(GOLD, bed_i * gold_dot)

        # the toy box on the Porch Front: a gold glow, then the lid splits open from the middle
        bx = keys(t, [(0, 0.0), (1.0, 1.0), (19.0, 1.0), (23.0, 0.0)])
        if bx > 0:
            bed = np.where(porch[:, None], light(GOLD, 0.4 * bx * np.ones(G.N)) + 0.4 * bed, bed)
            u = smoothstep(2.4, T_OUT, t)
            w = 4 + 46 * u
            glow = keys(t, [(2.4, 0.0), (T_OUT, 1.0), (T_OUT + 1, 0.55), (19.0, 0.55), (22.0, 0.0)])
            bed = bed + light(WHITE, glow * np.exp(-((x - BOX) / w) ** 2))

        # the troupe
        p, fc, vis, fall = P[f], FACE[f], VIS[f], FALL[f]
        fd = -1.0                                            # they all fall toward the back of the house
        cen = p + fd * 11 * fall * scale
        stretch = scale * (1 + 0.7 * fall)
        r = (x[:, None] - cen[None]) * fc[None] / stretch[None]
        br = vis * (1 - 0.55 * fall)
        if t < T_BOOM:                                       # every step lands with a little lift
            br = br * (0.82 + 0.18 * np.exp(-(t % BEAT) / 0.1))
        belt = inside(r, -2.2, 2.2)
        coat = inside(r, -11, 6) * (1 - belt)
        shako = inside(r, 6, 12)
        plume = inside(r, 12, 17) * (np.arange(S) == 0)[None]
        foot = inside(r, -15, 16, 3)
        mask = np.clip((foot * (vis > 0.01)[None]).sum(1), 0, 1)
        fr = bed * (1 - mask)[:, None]
        fr += (perc(0.85 * coat * br[None]) @ np.ones((S, 1))) * RED
        fr += (perc(0.9 * shako * br[None]) @ np.ones((S, 1))) * GOLD
        fr += (perc((0.75 * belt + 0.9 * plume) * br[None]) @ np.ones((S, 1))) * WHITE
        fl = (np.clip(FLASH[f], 0, 1.3) * vis)[None]
        fr += perc(np.clip((foot * fl).sum(1), 0, 1.2)) [:, None] * WHITE * 0.8
        gl = (np.clip(GLINT[f], 0, 1.5) * vis)[None]
        fr += perc(np.clip((inside(r, -14, 14, 3) * gl).sum(1), 0, 1.2) * 0.9)[:, None] * GOLD
        # the drum major's mace: a gold spark twirling ahead of him while he leads
        if vis[0] > 0.01 and fall[0] < 0.1 and not (40.0 < t < 42.0):
            twirl = np.sin(2 * np.pi * t / (2 * BEAT))
            mx = p[0] + fc[0] * (26 + 10 * twirl)
            fr += light(GOLD, vis[0] * (0.6 + 0.4 * abs(np.cos(2 * np.pi * t / BEAT))) * np.exp(-((x - mx) / 3) ** 2))
        if 40.0 < t < 41.6:                                  # the startle: the mace flies up and away
            mx = p[0] + 30 + 260 * (t - 40)
            fr += light(GOLD, 0.9 * np.exp(-((x - mx) / 3) ** 2) * (1 - smoothstep(41.0, 41.6, t)))

        # the jack-in-the-box
        jb = keys(t, [(33.0, 0.0), (34.0, 1.0), (44.0, 1.0), (45.0, 0.0)])
        if jb > 0:
            d0 = np.abs(x - JACK)
            box = inside(d0, -1, 10) * jb
            fr = fr * (1 - inside(d0, -1, 14))[:, None]
            fr += light(GREEN, 0.75 * box) + light(GOLD, 0.9 * jb * inside(d0, 10, 14, 1))
            if T_MARK <= t < T_POP:                          # the crank going round
                cx = JACK + 20 + 5 * np.sin(2 * np.pi * 2 * t)
                fr += light(GOLD, 0.9 * np.exp(-((x - cx) / 2.5) ** 2))
            if T_POP <= t < T_SINK + 0.7:
                tp = t - T_POP
                e = 80 * smoothstep(0, 0.06, tp) * (1 + 0.45 * np.exp(-tp / 0.55) * np.sin(2 * np.pi * 3 * tp))
                e *= 1 - smoothstep(T_SINK, T_SINK + 0.6, t)
                coil = SPRING[((d0 + 30 * tp) // 9).astype(int) % len(SPRING)]
                on = d0 < e
                fr = np.where(on[:, None], perc(0.95) * coil, fr)
                fr += light(WHITE, 0.95 * inside(d0, -1, 6) * (e > 8))
                fr = np.where((d0 < 2.5)[:, None] & (e > 8), perc(1.0) * RED, fr)

        # the toy cannon, its fuse, the shot, the cork
        if t >= T_ATTN:
            c = cannon(t)
            fr = fr * (1 - inside(x, c - 40, c + 22, 3))[:, None]
            fr += light(BRONZE, 0.8 * inside(x, c - 32, c + 14))
            fr += light(RED, 0.95 * np.exp(-((x - (c + 4)) / 5) ** 2))
            if T_FUSE <= t < T_BOOM:
                fx_ = c + 20 - 6 * (t - T_FUSE) / (T_BOOM - T_FUSE)
                fr += light(hexc('#ffe060'), fuse_fl[f] * np.exp(-((x - fx_) / 3) ** 2))
            for tb in (T_BOOM, T_END):
                if tb <= t < tb + 0.15:
                    fr += light(hexc('#fff0c0'), np.exp(-(t - tb) / 0.06) * np.exp(-((x - (c - 40)) / 22) ** 2))
                if tb <= t < tb + 1.8:
                    u = (t - tb) / 1.8
                    sx = c - 50 - 70 * u
                    fr += light(SMOKE, 0.65 * (1 - u) ** 1.5 * np.exp(-((x - sx) / (14 + 90 * u)) ** 2))
            if T_BOOM <= t < CORK_BOUNCES[-1] + 1.5:
                fade = 1 - smoothstep(CORK_BOUNCES[-1] + 0.6, CORK_BOUNCES[-1] + 1.5, t)
                fr += light(TAN, 0.95 * fade * np.exp(-((x - cork(t)) / 3.5) ** 2))

        # a lone twitch in the stillness
        if 57.3 < t < 57.8:
            i = 1 + int(np.argmin(np.abs(tr['tgt'][1:] - 700)))
            fr += light(GOLD, 0.6 * np.exp(-((t - 57.45) / 0.06) ** 2) * np.exp(-((x - P[f, i] + 11) / 10) ** 2))

        # the finale: bunting fills the house behind the column, scrolling with the march
        if t >= T_MARCH:
            seen = VIS[f] > 0.05
            edge = (P[f][seen].max() + 28) if seen.any() else -50.0
            fill = smoothstep(edge, edge + 25, x) * keys(t, [(T_MARCH, 0.0), (T_MARCH + 1.0, 1.0)])
            fill *= 1 - inside(x, cannon(t) - 40, cannon(t) + 22, 3)       # the cannon stays in view
            k = (np.floor((x + 132 * (t - T_MARCH)) / 26) % 3).astype(int)
            bi = np.array([0.62, 0.42, 0.62])[k] * (1 + 0.15 * np.exp(-(t % BEAT) / 0.1))
            bi = bi * keys(t, [(T_END, 1.0), (T_END + 0.3, 0.45)])     # let the confetti shine
            fr = fr * (1 - fill)[:, None] + perc(bi * fill)[:, None] * BUNT[k]

        # the last shot: a salvo of confetti over the whole house
        if t >= T_END:
            tc = t - T_END
            cx = cannon(T_END) - 40 - cv * (1 - np.exp(-1.6 * tc)) / 1.6
            ci = np.clip(1 - tc / clife, 0, 1) ** 1.2 * (0.7 + 0.3 * np.sin(14 * tc + ctw))
            near = np.abs(x[:, None] - cx[None]) < 20
            kern = np.where(near, np.exp(-((x[:, None] - cx[None]) / 5) ** 2), 0)
            fr += (kern * perc(ci)[None]) @ cc

        out[f][G.path] = fr * master
    return out


# ---- music: an original march in B flat, 120 bpm; the trio in E flat ----
TUNE_A = [  # (beat, note, beats) per bar
    [(0, 'F4', 0.75), (0.75, 'F4', 0.25), (1, 'Bb4', 1), (2, 'D5', 1), (3, 'Bb4', 1)],
    [(0, 'C5', 0.75), (0.75, 'D5', 0.25), (1, 'Eb5', 1), (2, 'C5', 1), (3, 'A4', 1)],
    [(0, 'Bb4', 0.5), (0.5, 'C5', 0.5), (1, 'D5', 0.5), (1.5, 'Eb5', 0.5), (2, 'F5', 1), (3, 'D5', 1)],
    [(0, 'C5', 1), (1, 'A4', 0.5), (1.5, 'Bb4', 0.5), (2, 'C5', 2)],
    [(0, 'F4', 0.75), (0.75, 'F4', 0.25), (1, 'Bb4', 1), (2, 'D5', 1), (3, 'Bb4', 1)],
    [(0, 'C5', 0.75), (0.75, 'D5', 0.25), (1, 'Eb5', 1), (2, 'G5', 1), (3, 'Eb5', 1)],
    [(0, 'D5', 0.5), (0.5, 'F5', 0.5), (1, 'C5', 0.5), (1.5, 'Eb5', 0.5), (2, 'A4', 1), (3, 'C5', 1)],
    [(0, 'Bb4', 1), (1, 'F4', 1), (2, 'Bb4', 2)],
]
CHORDS_A = ['Bb', 'F7', 'Bb', 'F', 'Bb', 'Eb', 'F7', 'Bb']
TRIO = [
    [(0, 'G4', 1.5), (1.5, 'Ab4', 0.5), (2, 'Bb4', 1), (3, 'Eb5', 1)],
    [(0, 'D5', 1.5), (1.5, 'C5', 0.5), (2, 'Bb4', 2)],
    [(0, 'C5', 1.5), (1.5, 'D5', 0.5), (2, 'Eb5', 1), (3, 'C5', 1)],
    [(0, 'Bb4', 1), (1, 'G4', 1), (2, 'F4', 2)],
    [(0, 'G4', 1.5), (1.5, 'Ab4', 0.5), (2, 'Bb4', 1), (3, 'G5', 1)],
    [(0, 'F5', 1.5), (1.5, 'Eb5', 0.5), (2, 'D5', 1), (3, 'C5', 1)],
    [(0, 'Bb4', 1), (1, 'Eb5', 1), (2, 'D5', 1), (3, 'F5', 1)],
    [(0, 'Eb5', 2), (2, 'Bb4', 1), (3, 'G4', 1)],
]
CHORDS_T = ['Eb', 'Bb7', 'Ab', 'Eb', 'Eb', 'Bb7', 'Bb7', 'Eb']
CH = {'Bb': ('Bb3', 'D4', 'F4'), 'F7': ('A3', 'C4', 'Eb4'), 'F': ('A3', 'C4', 'F4'), 'Eb': ('G3', 'Bb3', 'Eb4'),
      'Ab': ('Ab3', 'C4', 'Eb4'), 'Bb7': ('Ab3', 'D4', 'F4')}
BASS = {'Bb': ('Bb1', 'F2'), 'F7': ('F2', 'C2'), 'F': ('F2', 'C2'), 'Eb': ('Eb2', 'Bb1'), 'Ab': ('Ab1', 'Eb2'),
        'Bb7': ('Bb1', 'F2')}
CRANK = ['F4', 'Bb4', 'D5', 'C5', 'A4', 'F4', 'G4', 'A4', 'Bb4', 'D5', 'F5', 'Eb5', 'C5', 'A4', 'C5']
SCALE_UP = ['F3', 'G3', 'A3', 'Bb3', 'C4', 'D4', 'Eb4', 'F4', 'G4', 'A4', 'Bb4', 'C5', 'D5', 'Eb5', 'F5', 'G5',
            'A5', 'Bb5', 'C6', 'D6']


def score(M, G):
    from pixelhome.audio import SR, note, whoosh, slide
    n = note
    tr = troupe()
    P, VIS = tr['P'], tr['VIS']

    flute = M.sampler('Woodwinds/Flute/stac/*.wav', tune=-12)
    clar = M.sampler('Woodwinds/Clarinet/stac/*.wav', tune=-12)
    tpt = M.sampler('Brass/Trumpet/stac/*.wav', tune=-12)
    tpt_s = M.sampler('Brass/Trumpet/sus/*.wav', tune=-12)
    horn = M.sampler('Brass/F Horn/stac/*.wav', tune=-12)
    horn_s = M.sampler('Brass/F Horn/sus/*.wav', tune=-12)
    bone = M.sampler('Brass/Tenor Trombone/sus/*.wav', tune=-12)
    tuba = M.sampler('Brass/Tuba/stac/*.wav', tune=-12)
    tuba_s = M.sampler('Brass/Tuba/sus/*.wav', tune=-12)
    glock = M.sampler('Percussion/Glock/*.wav', tune=-12)
    xylo = M.sampler('Percussion/Xylo/*.wav', tune=-12)
    trem = M.sampler('Strings/Violin Section/Trem/*.wav', tune=-12)
    ctrem = M.sampler('Strings/Cello Section/trem/*.wav', tune=-12)
    pizz = M.sampler('Strings/Violin Section/Pizz/*.wav', tune=-12)
    mbox = M.synth('Plucks/Magic Music Box')
    snare = M.hits('VSCO 1 Percussion/drums/snare/drum3_marching/snare3_[mp]*.wav')
    snare_f = M.hits('VSCO 1 Percussion/drums/snare/drum3_marching/snare3_f*.wav')
    rim = M.hits('VSCO 1 Percussion/drums/snare/drum3_marching/snare3_rimshot*.wav')
    sroll = M.hits('Percussion/Snare2-rollSN_v[35]*.wav')
    bd = M.hits('VSCO 1 Percussion/drums/bass/bdrum_f_*.wav')
    bd_ff = M.hits('VSCO 1 Percussion/drums/bass/bdrum_fff_*.wav')
    tenor = M.hits('VSCO 1 Percussion/drums/tenor/tenor_lower/tenor_f*.wav')
    clash = M.hits('VSCO 1 Percussion/varMetal/Cymbals/clash/crash_hit_ff*.wav')
    choke = M.hits('Percussion/cymbal-crashshort*.wav')
    timp = M.hits('Percussion/Timpani/Timpani1_Hit*.wav')
    troll = M.hits('Percussion/Timpani/Rolls/Timpani1_Roll*.wav')
    click = M.hits('VSCO 1 Percussion/varWood/wood_click*.wav')
    slap = M.hits('VSCO 1 Percussion/varWood/slapstick[0-9].wav')
    ratchet = M.hits('Percussion/Ratchet1-Crank*.wav')
    guiro = M.hits('Percussion/Guiro-Hit*.wav')
    fall = M.hits('Brass/OldTrombone/Fall/*.wav')
    tri = M.hits('Percussion/Triangle3-Hit_v1*.wav')

    for name, gain, rev in (('tune', 0.38, 0.16), ('horns', 0.25, 0.18), ('bass', 0.44, 0.06), ('drums', 0.37, 0.1),
                            ('motif', 0.34, 0.2), ('perc', 0.4, 0.12), ('fx', 0.3, 0.18)):
        M.bus(name, gain=gain, reverb=rev)

    order = np.argsort(G.pd)
    xs, ds = G.pos[order, 0], G.pd[order]
    x0, x1 = xs.min(), xs.max()
    L = G.length

    def pan_at(dd):
        x = np.interp(np.clip(dd, 0, L), ds, xs)
        return float(0.85 * (2 * (x - x0) / (x1 - x0) - 1))

    def mono(sig, pans):
        a = (np.clip(pans, -1, 1) + 1) * np.pi / 4
        return np.vstack([sig * np.cos(a), sig * np.sin(a)]) * np.sqrt(2)

    def tone(fr, amp, buzz=0.12):
        ph = 2 * np.pi * np.cumsum(fr) / SR
        return amp * (np.sin(ph) + buzz * np.sin(2 * ph) + 0.6 * buzz * np.sin(3 * ph))

    def head(t):                                     # where the troupe is, for panning the band with it
        f = min(int(t / DT), len(P) - 1)
        seen = VIS[f] > 0.5
        return pan_at(P[f][seen].mean()) if seen.any() else 0.0

    def tune(bars, k0, inst, bus='tune', vel=100, pan=0.0, gain=1.0, octave=0, long=None):
        for j, b in enumerate(bars):
            for e, m, ln in b:
                pl = long if (long is not None and ln >= 1.5) else inst
                t = at(k0 + j, e)
                M.add(bus, pl.play(n(m) + octave, vel, dur=ln * BEAT * 0.9), t, gain, pan(t) if callable(pan) else pan)

    def band(k0, chords, vel=100, horns=True, snares=True, steps=True, gain=1.0, pan=0.0):
        for j, c in enumerate(chords):
            k = k0 + j
            for e in (0, 2):
                M.add('bass', tuba.play(n(BASS[c][e // 2]), vel), at(k, e), gain)
            for e in range(4):                       # a step on every beat
                if steps:
                    pp = pan(at(k, e)) if callable(pan) else pan
                    M.add('drums', bd.play(vel - (0 if e % 2 == 0 else 15)), at(k, e), 0.8 * gain, 0.6 * pp)
            if horns:
                for e in (1, 3):
                    for mm in CH[c]:
                        M.add('horns', horn.play(n(mm), vel - 12), at(k, e), 0.5 * gain, -0.25)
            if snares:
                pat = (0, 1, 2, 3, 4, 5, 6, 7) if j % 4 == 3 else (0, 2, 3, 4, 6, 7)
                for e in pat:
                    M.add('drums', (snare_f if e % 2 == 0 else snare).play(vel if e % 4 == 0 else vel - 25),
                          at(k, e / 2), 0.55 * gain, 0.15)
            if j % 4 == 0:
                M.add('drums', clash.play(vel), at(k), 0.4 * gain)

    def cadence(k, vel=100, pan=0.0):                # a bar of drum corps: rat-a-tat, rat-a-tat, tat tat
        hits = [0, 0.25, 0.5, 1, 1.25, 1.5, 2, 3]
        for e in hits:
            M.add('drums', (snare_f if e in (0, 1, 2, 3) else snare).play(vel if e in (0, 2) else vel - 20),
                  at(k, e), 0.65, pan + 0.1)
        for e in (0, 2, 3):
            M.add('drums', tenor.play(vel - 5), at(k, e), 0.6, pan - 0.2)
        for e in (0, 1, 2, 3):
            M.add('drums', bd.play(vel - 10), at(k, e), 0.7, pan)

    # ---- 0-4: the toy box glows, a snare roll, the lid opens ----
    r = sroll.play(80, dur=2.4)
    M.add('drums', r * np.linspace(0.05, 1, r.shape[1]) ** 2, 0.2, 0.6, pan_at(BOX))
    for i, m in enumerate(('Bb3', 'D4', 'F4', 'Bb4', 'D5', 'F5')):
        M.add('motif', glock.play(n(m), 80), 2.4 + 0.2 * i, 0.6, pan_at(BOX) + 0.1 * (i - 3))
    M.add('perc', choke.play(100), at(1), 0.4, pan_at(BOX))
    cadence(1, 105, pan_at(BOX))

    # ---- 4-20: out of the box and round to the right: first strain on fife and xylophone ----
    band(2, CHORDS_A, 98, pan=head)
    tune(TUNE_A, 2, flute, 'tune', 108, head)
    tune(TUNE_A, 2, xylo, 'motif', 82, head, gain=0.45)
    tune(TUNE_A, 2, clar, 'tune', 92, head, gain=0.5, octave=-12)
    for i in range(1, NS + 1):                       # each soldier out of the box: a glock pop
        f = int(np.argmax(VIS[:, i] > 0.5))
        M.add('motif', glock.play(n(('Bb4', 'D5', 'F5', 'D5')[i % 4]), 70), f * DT, 0.45, pan_at(BOX + 15))

    # every soldier turning a corner: a rim click where it is
    for tc, i, c in tr['turns']:
        if tc < T_MARCH:
            M.add('perc', rim.play(int(M.rng.integers(60, 80))), tc, 0.35, pan_at(c))

    # ---- 20-24: halt, about face, the drum major scampers back to the front ----
    pr = pan_at(2100)
    for e, v in ((0, 115), (1, 115)):
        M.add('drums', bd_ff.play(v), at(10, e), 0.9, pr)
        M.add('drums', snare_f.play(v), at(10, e), 0.7, pr)
        for mm in CH['Bb']:
            M.add('horns', horn.play(n(mm), 110), at(10, e), 0.5, pr)
    M.add('perc', rim.play(115), T_FACE, 0.8, pr)
    M.add('perc', clash.play(100), T_FACE, 0.3, pr)
    for k in range(10):                              # the drum major's run: down the xylophone, right to left
        tk = T_FACE + k * BEAT / 4
        M.add('motif', xylo.play(n(('F5', 'D5', 'Bb4', 'F4', 'D5', 'Bb4', 'F4', 'D4', 'F4', 'Bb4')[k]), 92), tk, 0.7,
              pan_at(float(P[min(int(tk / DT), len(P) - 1), 0])))
    cadence(11, 100, pan_at(1900))
    band(11, ['F7'], 96, snares=False, steps=False)
    M.add('fx', slide(0.0, 0.25, 900, 1500, 0.3, 0.4), at(11, 3) + 0.1, 0.5, pan_at(1442))  # fweet: forward!

    # ---- 24-36: march back round the porch: the strain again on trumpets ----
    second = TUNE_A[:4] + TUNE_A[6:]
    band(12, CHORDS_A[:4] + CHORDS_A[6:], 102, pan=head)
    tune(second, 12, tpt, 'tune', 104, head, long=tpt_s)
    tune(second, 12, glock, 'motif', 78, head, gain=0.35)

    # ---- 36-40: mark time at the box while it cranks ----
    pj = pan_at(JACK)
    for e in range(8):
        M.add('drums', snare.play(70), at(18, e / 2), 0.4, head(at(18)))
        M.add('perc', ratchet.play(70, dur=0.2), at(18, e / 2), 0.4, pj + 0.1)
    for k, m in enumerate(CRANK):
        tk = at(18) + k * BEAT / 2
        a = mbox.render([(0, n(m), 100, BEAT / 2)], 1.2)
        M.add('motif', a, tk, 0.8, pj)
    for m in ('Bb2', 'F3'):
        M.add('horns', horn_s.play(n(m), 80, dur=3.5, release=0.3), at(18), 0.5, pj)
    for k in range(2):                               # the crank's bass: a pizzicato tuba, step by step
        for e in range(4):
            M.add('bass', tuba.play(n(('Bb1', 'F2', 'Bb1', 'F2', 'C2', 'F2', 'A1', 'F2')[4 * k + e]), 85), at(18 + k, e),
                  0.7)
            M.add('motif', pizz.play(n(('D4', 'F4', 'Eb4', 'C4')[(4 * k + e) % 4]), 70),
                  at(18 + k, e + 0.5), 0.5, pj)

    # ---- 40-44: POP. A boing, a startled stab, trembling, the jack sinks away ----
    M.add('perc', slap.play(120), T_POP, 0.9, pj)
    M.add('perc', clash.play(115), T_POP, 0.5, pj)
    tt = np.arange(int(1.6 * SR)) / SR
    boing = tone(330 * 2 ** (np.sin(2 * np.pi * 3 * tt) * np.exp(-tt / 0.55) * 5 / 12) * (1 + 0.8 * np.exp(-tt / 0.05)),
                 0.35, 0.3) * np.exp(-tt / 0.7) * np.clip(tt / 0.005, 0, 1)
    M.add('fx', mono(boing, np.full(len(tt), pj)), T_POP, 0.9)
    for m in ('E4', 'G4', 'Bb4', 'Db5'):
        M.add('tune', tpt.play(n(m), 118, dur=0.3), T_POP + 0.05, 0.5, head(T_POP))
        M.add('horns', horn.play(n(m) - 12, 115, dur=0.3), T_POP + 0.05, 0.6)
    for i in range(NS + 1):                          # the jump back ripples down the column
        if i % 3 == 0:
            M.add('perc', click.play(90), float(tr['t_jolt'][i]), 0.4, pan_at(float(P[int(T_POP / DT) + 10, i])))
    for m in ('E4', 'Bb4', 'Db5'):
        M.add('horns', trem.play(n(m), 70, dur=2.0, release=0.4), T_POP + 0.2, 0.6, head(T_POP))
    M.add('horns', ctrem.play(n('E2'), 75, dur=2.0, release=0.4), T_POP + 0.2, 0.7)
    for k in range(4):
        M.add('motif', glock.play(n(('G5', 'E5', 'G5', 'Db5')[k]), 70), T_POP + 0.8 + 0.4 * k, 0.4, pj)
    M.add('fx', slide(0.0, 0.6, 1300, 300, 0.7, 0.45, 0.7), T_SINK, 0.7, pj)
    M.add('perc', guiro.play(80), T_SINK + 0.6, 0.6, pj)
    M.add('perc', slap.play(80), T_SINK + 0.62, 0.5, pj)

    # ---- 44-48: fall in! A snare fill as they spread round the house, the xylophone climbing with each step ----
    for e in range(16):
        M.add('drums', snare_f.play(int(70 + 40 * e / 15)), at(22, e / 4), 0.55, 0.1)
        M.add('drums', snare.play(int(60 + 40 * e / 15)), at(22, e / 4 + 0.125), 0.4, -0.1)
        M.add('motif', xylo.play(n(SCALE_UP[e % 16 + 1]) - 12 if e < 8 else n(SCALE_UP[e - 4]), 90), at(22, e / 2),
              0.6, -0.8 + 1.6 * e / 15)
    for e in (0, 2, 4, 6):
        M.add('drums', tenor.play(100), at(22, e), 0.6, -0.3 if e % 4 else 0.3)
    band(22, ['F', 'F7'], 96, snares=False, steps=False)

    # ---- 48-52: attention, salute (a fanfare), the cannon rolls in and its fuse fizzes ----
    M.add('drums', bd_ff.play(115), T_ATTN, 0.9)
    M.add('drums', clash.play(110), T_ATTN, 0.5)
    fan = [(0, 'Bb4', 0.5), (0.5, 'Bb4', 0.25), (0.75, 'Bb4', 0.25), (1, 'D5', 1), (2, 'F5', 1.5), (3.5, 'D5', 0.5),
           (4, 'Eb5', 0.5), (4.5, 'Eb5', 0.25), (4.75, 'Eb5', 0.25), (5, 'C5', 1), (6, 'F5', 2)]
    for e, m, ln in fan:
        inst = tpt_s if ln >= 1 else tpt
        M.add('tune', inst.play(n(m), 108, dur=ln * BEAT * 0.9), at(24, e), 0.9, -0.2)
        M.add('horns', horn_s.play(n(m) - 12, 96, dur=ln * BEAT * 0.9), at(24, e), 0.5, 0.2)
    for k, c in ((24, 'Bb'), (25, 'F')):
        M.add('bass', tuba_s.play(n(BASS[c][0]), 100, dur=1.9, release=0.2), at(k), 0.8)
    for ts in SALUTES:
        M.add('perc', tri.play(95), ts, 0.5)
    for e in range(4):                               # four squeaky rolls of its wheels
        M.add('perc', guiro.play(85), at(24, e), 0.5, pan_at(2470))
    fz = np.random.default_rng(5).normal(0, 1, int(2 * SR))
    fz = np.convolve(fz, [1, -1], 'same') * np.linspace(0.3, 1, len(fz)) * 0.05
    fz *= 1 + 0.5 * np.sin(2 * np.pi * 23 * np.arange(len(fz)) / SR)
    M.add('fx', mono(fz, np.full(len(fz), pan_at(2490))), T_FUSE, 1.0)
    r = sroll.play(90, dur=1.9)
    M.add('drums', r * np.linspace(0.1, 1, r.shape[1]) ** 2, T_FUSE + 0.1, 0.6, 0.4)

    # ---- 52: BOOM, the cork, and the dominoes all the way round ----
    pc = pan_at(2450)
    M.add('drums', bd_ff.play(127), T_BOOM, 1.0, pc)
    M.add('perc', timp.play(120, pitch=-3), T_BOOM, 0.9, pc)
    M.add('perc', clash.play(120), T_BOOM, 0.6, pc)
    M.add('fx', whoosh(1.5, 1500, 250, 0.9, seed=52), T_BOOM, 0.6, pc)
    M.add('fx', slide(0.0, CORK_FLY, 600, 1800, CORK_FLY + 0.05, 0.4, 0.4), T_BOOM + 0.02, 0.6, pc)
    for k, tb in enumerate(CORK_BOUNCES):
        M.add('motif', xylo.play(n(('C6', 'A5', 'F5', 'D5')[k]), 100 - 12 * k), tb, 0.7, pan_at(cork(tb)))
    for m in ('Bb3', 'D4', 'F4'):
        M.add('horns', horn_s.play(n(m), 108, dur=0.4), T_BOOM, 0.5)
    tf = tr['t_fall'] + 0.22
    down = np.argsort(tf)
    for k, i in enumerate(down):
        p = float(tr['tgt'][i])
        M.add('perc', click.play(95 + int(25 * (i == 0))), float(tf[i]), 0.8, pan_at(p))
        m = n('D6') - [0, 1, 3, 5, 7, 8, 10, 12][k % 8] - 12 * (k // 8)
        M.add('motif', xylo.play(max(m, n('F3')), 85), float(tf[i]), 0.55, pan_at(p))
    end = float(tf.max())
    M.add('perc', timp.play(100, pitch=-5), end, 0.8, pan_at(130))
    M.add('perc', tenor.play(100), end, 0.6, pan_at(130))
    M.add('tune', fall.play(95), end + 0.6, 0.55, 0.0)

    # ---- 56-60: still. A twitch; the drum major springs up and blows his whistle ----
    M.add('perc', click.play(60), 57.45, 0.4, pan_at(700))
    M.add('motif', pizz.play(n('Bb4'), 70), 57.45, 0.4, pan_at(700))
    M.add('perc', slap.play(100), T_DM_UP, 0.7, pan_at(tr['tgt'][0]))
    M.add('motif', xylo.play(n('Bb4'), 100), T_DM_UP, 0.7, pan_at(tr['tgt'][0]))
    for k in range(2):
        M.add('fx', slide(0.0, 0.08, 1900, 2300, 0.3 if k == 0 else 0.55, 0.32), T_DM_UP + 0.55 + 0.5 * k, 0.6,
              pan_at(tr['tgt'][0]))

    # ---- 60-65: up they spring, one by one: a rising scale ----
    for k, i in enumerate(tr['order_up']):
        tu = float(tr['t_up'][i])
        p = float(tr['tgt'][i])
        M.add('motif', xylo.play(n(SCALE_UP[k]), 95), tu, 0.7, pan_at(p))
        M.add('motif', glock.play(n(SCALE_UP[k]), 70), tu, 0.3, pan_at(p))
        M.add('perc', click.play(80), tu, 0.4, pan_at(p))
    band(30, ['Bb', 'Bb', 'Bb7'], 92, snares=False)
    r = sroll.play(85, dur=1.8)
    M.add('drums', r * np.linspace(0.05, 1, r.shape[1]) ** 2, T_UP0 + 3.0, 0.5)
    M.add('drums', bd_ff.play(118), T_TURN, 0.9)
    M.add('drums', snare_f.play(118), T_TURN, 0.7)
    M.add('perc', rim.play(118), T_TURN + 0.01, 0.6)

    # ---- 66-86: the trio in E flat, full band, as they quick-march off down Side ----
    band(33, CHORDS_T, 110)
    tune(TRIO, 33, tpt, 'tune', 112, -0.15, long=tpt_s)
    tune(TRIO, 33, flute, 'tune', 100, 0.25, gain=0.6, octave=12)
    tune(TRIO, 33, glock, 'motif', 85, 0.0, gain=0.35)
    for j, c in enumerate(CHORDS_T):                 # trombones on the long notes underneath
        for m in CH[c][:2]:
            M.add('horns', bone.play(n(m) - 12, 96, dur=BAR * 0.95, release=0.3), at(33 + j), 0.45, 0.2)
    for j in range(8):                               # quick-step: snare on every half beat
        for e in range(8):
            M.add('drums', snare.play(78 if e % 2 else 96), at(33 + j, e / 2), 0.35, 0.1)
    # the coda: the drum major goes, two bars of cadence and the cannon's last word
    cadence(41, 112)
    for e, c in ((0, 'Eb'), (2, 'Bb7')):
        for mm in CH[c]:
            M.add('horns', horn_s.play(n(mm), 110, dur=BEAT * 1.8), at(41, e), 0.5)
        M.add('bass', tuba.play(n(BASS[c][0]), 110), at(41, e), 0.9)
    for m in ('G4', 'Bb4', 'Eb5'):
        M.add('tune', tpt_s.play(n(m), 115, dur=2.0, release=0.6), T_END, 0.7)
    for m in ('Eb3', 'G3', 'Bb3'):
        M.add('horns', horn_s.play(n(m), 115, dur=2.0, release=0.6), T_END, 0.6)
    M.add('bass', tuba_s.play(n('Eb2'), 115, dur=2.0, release=0.6), T_END, 0.9)
    r = troll.play(100, dur=1.0)
    M.add('perc', r * np.linspace(0.1, 1, r.shape[1]) ** 2, T_END - 1.0, 0.6)
    M.add('drums', bd_ff.play(127), T_END, 1.0, pan_at(2450))
    M.add('perc', timp.play(120, pitch=-3), T_END, 0.8, pan_at(2450))
    M.add('drums', clash.play(122), T_END, 0.6)
    M.add('fx', whoosh(2.0, 400, 3500, 0.9, seed=84), T_END + 0.05, 0.6, 0.0)
    for i, m in enumerate(('Eb5', 'G5', 'Bb5', 'Eb6', 'G5', 'Bb5', 'Eb6')):
        M.add('motif', glock.play(n(m), 85), T_END + 0.1 + 0.11 * i, 0.5, 0.8 - 0.25 * i)
