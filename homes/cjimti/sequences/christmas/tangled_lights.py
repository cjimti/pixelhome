"""Tangled Lights: A box glows on the Porch Front and the lid comes off. A string of big old-fashioned bulbs,
dark glass in red, green, blue, orange, pink and gold, is pulled out of it: first the plug end, out along the
Porch Front, down the Porch Right and out to the free end of Right, where the outlet is; then the other end,
up the Porch Left, along the Left and all the way down the Side. Knots come out with it, bunched-up clumps of
bulbs that snag at the corners: the string is tugged, tugged, tugged, and the knot snaps free and springs
out, the biggest one at the front-left corner. Plugged in, the string flickers on section by section from the
outlet, run by run round the house, until a bad bulb on the Left wing pops and everything goes dark. A
jiggle of the plug brings it back; it dies again; a tap, it's back for a moment, and the dark spreads out from
the dud. A little tester light comes out of the box and hunts along the string, every good bulb blinking as
it is tested and left glowing faintly behind it: it goes the wrong way first, comes back, slows down on the
Left, goes right past the dud and backs up. Found: the dud flashes, is popped out, a new bulb flies in from the
box and clicks in. A spark at the outlet, and a white front runs the whole roofline from the outlet to the
back of the Side and leaves every bulb blazing; the colours march along the string on the beat with bright
chases going round the house, faster and both ways, to a full blaze at the end.

Music, 120 bpm in C major: a jaunty pizzicato and bassoon tune while the string unspools, every bulb out of the
box a soft glass clink; at each snag the music stops for three tuba-and-timpani tugs, the snap is a slapstick
crack, a slide whistle and a harp spring. Each run that flickers on buzzes and lands a chord that climbs; each
failure is an electric zap and a sad trombone fall. The tester walks to a sneaking pizzicato bass in A minor
with a beep for each bulb it tests and a muted-trumpet "wah-wah" and a buzzer when it finds the dud; a squeak,
a pop and a rising glockenspiel for the swap. The blaze is a tutti chord, then an original galop with
xylophone eighths that step with the colours and a harp glissando for every chase round the house."""
import numpy as np
from pixelhome.fx import DT, hexc, perc, light, keys, smoothstep, nframes

CODE = 'CH12'
TITLE = 'Tangled Lights'
KIND = 'show'
DESCRIPTION = ('A string of big bulbs comes out of the box in knots and is untangled along the roof. It flickers on, '
               'one bad bulb kills it all, a tester hunts down the dud, and the whole house blazes.')
VOICEOVER = "Every year, the same box, the same knots, and the same one bulb that ruins everything."

BULBS = [hexc(c) for c in ('#ff1808', '#10c830', '#2040ff', '#ff7010', '#ff2a90', '#ffc018')]
NIGHT = hexc('#0c1a70')
BOX = hexc('#ff9a30')
PLUG = hexc('#ffd890')
WHITE = hexc('#fff6ea')
TESTER = hexc('#fff070')
ALARM = hexc('#ff0800')

D = 86.0
SEED = 52
BEAT = 0.5
BAR = 4 * BEAT
SP = 24.0                                          # bulb spacing along the roof
GLASS = 0.24                                       # an unlit bulb's glass


def at(bar, beat=0.0):
    return bar * BAR + beat * BEAT


T_LID = at(0, 3)
T_RIGHT, T_RIGHT_END = at(1, 2), at(5, 2)          # the plug end comes out to the outlet
T_LEFT, T_LEFT_END = at(5, 2), at(12)              # the other end goes round to the back of the Side
SNAGS = [  # (side, first, last bulb of the knot from the lead, snag start, snap); tugs on the beats between
    ('R', 6, 13, at(3, 1), at(4)),
    ('L', 4, 10, at(7, 1), at(8, 2)),
    ('L', 14, 24, at(9, 2), at(11)),
]
T_PLUG = at(13)
RUNS_ON = [at(13, 0.5), at(13, 3), at(14, 2), at(15, 1), at(16), at(16, 2)]  # Right, PR, PF, PL, Left, Side
T_OUT1 = at(17)
WIGGLE1 = [(at(17, 2.3), 0.12), (at(17, 3.2), 0.07), (at(18, 0.1), 0.18)]
T_BACK1 = at(18, 1)
T_OUT2 = at(20)
WIGGLE2 = [(at(20, 2), 0.1), (at(20, 2.8), 0.1)]
T_BACK2 = at(21)
T_CASCADE = at(21, 2)
CASCADE_V = 1300.0
T_TESTER = at(22, 1)
T_FOUND = at(28, 3)
T_POP, T_NEW, T_CLICK = at(30), at(30, 1.5), at(31)
T_SPARK = at(31, 3)
T_BLAZE = at(32)
BLAZE_V = 2100.0
T_FAST = at(36)                                    # the chases speed up
T_FULL = at(40)
T_END = at(42)


def geom(G):
    x = G.pd[G.path]
    c = [float((x[i] + x[i + 1]) / 2) for i in (80, 178, 260, 331, 380)]
    return dict(c1=c[0], c2=c[1], c3=c[2], c4=c[3], c5=c[4], L=float(G.length), B=0.5 * (c[2] + c[3]))


def lead_keys(g):
    """Where each lead end is, by time: it stalls at a snag and is tugged on the beats."""
    B, L = g['B'], g['L']
    homes = np.arange(12.0, L, SP)
    right_home, left_home = homes[-1], homes[0]
    s0 = SNAGS[0]
    eR = s0[3]
    R = [(T_RIGHT, B), (eR, 2150.0)]
    for k, tb in enumerate(np.arange(eR + BEAT, s0[4], BEAT)):
        R += [(tb - 0.04, 2150.0 + 6 * k), (tb + 0.08, 2172.0 + 6 * k), (tb + 0.3, 2160.0 + 6 * k)]
    R += [(s0[4], 2180.0), (T_RIGHT_END, right_home), (D, right_home)]
    Lk = [(T_LEFT, B)]
    stops = (g['c2'] - SP * SNAGS[1][1], g['c1'] - SP * SNAGS[2][1] - 4 * 0)
    for (side, a, b, ts, tsn), e in zip(SNAGS[1:], stops):
        Lk.append((ts, e))
        for k, tb in enumerate(np.arange(ts + BEAT, tsn, BEAT)):
            Lk += [(tb - 0.04, e - 6 * k), (tb + 0.08, e - 22 - 6 * k), (tb + 0.3, e - 10 - 6 * k)]
        Lk.append((tsn, e - 30))
    Lk += [(T_LEFT_END, left_home), (D, left_home)]
    return R, Lk


def plan(G):
    """The string: home of every bulb, its colour, which half it is in and its rank from that half's lead end;
    the lead ends and each bulb's position through the pull; the dud; the tester's route and when it checks
    each bulb."""
    g = geom(G)
    B, L = g['B'], g['L']
    F = nframes(D)
    t = np.arange(F) * DT
    homes = np.arange(12.0, L, SP)
    nb = len(homes)
    col = np.array([BULBS[i % len(BULBS)] for i in range(nb)])
    kind = np.arange(nb) % len(BULBS)
    right = homes > B
    rank = np.where(right, np.cumsum(right[::-1])[::-1] - 1, np.cumsum(~right) - 1)
    R, Lk = lead_keys(g)
    eR = np.interp(t, [p[0] for p in R], [p[1] for p in R])
    eL = np.interp(t, [p[0] for p in Lk], [p[1] for p in Lk])
    # spacing behind each lead: knots stay bunched until they snap, then spring out
    pos = np.zeros((F, nb))
    for half, e, sgn in (('R', eR, -1), ('L', eL, 1)):
        m = right if half == 'R' else ~right
        idx = np.where(m)[0]
        order = idx[np.argsort(rank[idx])]
        sp = np.full((F, len(order)), SP)
        for side, a, b, ts, tsn in SNAGS:
            if side != half:
                continue
            u = t - tsn
            spring = np.where(u < 0, 4.0, SP + (4.0 - SP) * np.exp(-np.clip(u, 0, None) / 0.12) *
                              np.cos(2 * np.pi * 2.2 * np.clip(u, 0, None)))
            sp[:, a + 1:b + 1] = spring[:, None]
        off = np.concatenate([np.zeros((F, 1)), np.cumsum(sp[:, 1:], axis=1)], axis=1)
        pos[:, order] = e[:, None] + sgn * off
    pos[t < T_RIGHT] = B
    out_box = np.where(right[None], pos > B + 2, pos < B - 2)
    out_box[t >= T_LEFT_END + 1] = True
    pos[t >= T_LEFT_END + 1] = homes
    dud = int(np.argmin(np.abs(homes - (g['c1'] + 236))))
    # the tester's route: the wrong way first, back, slowly along the Left, past the dud and back
    hd = homes[dud]
    TR = [(T_TESTER, B), (T_TESTER + 0.6, B + 30), (at(24), 1900), (at(24, 2), 1915), (at(25, 2), B),
          (at(26, 3), g['c2'] - 40), (at(27, 3), hd + 40), (at(28, 1), hd - 55), (at(28, 2.4), hd - 55),
          (T_FOUND, hd), (T_POP, hd)]
    tx = np.interp(t, [p[0] for p in TR], [p[1] for p in TR])
    k = 4
    w = np.exp(-0.5 * (np.arange(-k, k + 1) / 2.0) ** 2)
    w /= w.sum()
    tx = np.convolve(np.pad(tx, k, mode='edge'), w, 'valid')
    tx[(t < T_TESTER) | (t >= T_POP + 0.3)] = np.nan
    checks = np.full(nb, np.inf)
    for i in range(nb):
        if i == dud:
            continue
        near = np.where(np.abs(tx - homes[i]) < 5)[0]
        if len(near):
            checks[i] = t[near[0]]
    return dict(g=g, homes=homes, nb=nb, col=col, kind=kind, right=right, rank=rank, eR=eR, eL=eL, pos=pos,
                out=out_box, dud=dud, tx=tx, checks=checks)


def section_of(g, p):
    """0 Right, 1 Porch Right, 2 Porch Front, 3 Porch Left, 4 Left, 5 Side: in order from the outlet."""
    return np.select([p >= g['c5'], p >= g['c4'], p >= g['c3'], p >= g['c2'], p >= g['c1']], [0, 1, 2, 3, 4], 5)


def lit_level(P, t, rng_on):
    """How lit each bulb is at t (0 dark .. 1 full), before the blaze."""
    g, homes, nb, dud = P['g'], P['homes'], P['nb'], P['dud']
    sec = section_of(g, homes)
    lv = np.zeros(nb)
    if T_PLUG <= t < T_OUT1:
        for s, ts in enumerate(RUNS_ON):
            a = t - ts
            m = sec == s
            if 0 <= a < 0.7:
                lv[m] = np.where(rng_on[int(a / 0.06) % rng_on.shape[0], m] > 0.45 + 0.4 * (0.7 - a), 1.0, 0.25)
            elif a >= 0.7:
                lv[m] = 1.0
    for t0, t1, back in ((T_OUT1, T_BACK1, WIGGLE1), (T_OUT2, T_BACK2, WIGGLE2)):
        if t0 <= t < t1:
            for tw, dw in back:
                if tw <= t < tw + dw:
                    lv[:] = 0.55
    if T_BACK1 <= t < T_OUT2 or T_BACK2 <= t < T_CASCADE + 3:
        lv[:] = 1.0
        if t >= T_CASCADE:
            lv[np.abs(homes - homes[dud]) < CASCADE_V * (t - T_CASCADE)] = 0.0
    if T_TESTER <= t < T_BLAZE:                                     # tested: a blink, then a faint glow
        a = t - P['checks']
        lv = np.maximum(lv, np.where(a >= 0, 0.5 + 0.5 * np.exp(-np.clip(a, 0, None) / 0.18), 0))
    if t >= T_OUT1 and t < T_BLAZE:
        lv[dud] = 0.0
    if t >= T_CLICK and t < T_BLAZE:
        lv[dud] = 0.3 + 0.7 * np.exp(-(t - T_CLICK) / 0.25)
    return lv


def render(G, seed=SEED):
    P = plan(G)
    g, homes, nb, col, kind, pos, outb, dud, tx = (P[k] for k in ('g', 'homes', 'nb', 'col', 'kind', 'pos', 'out',
                                                                    'dud', 'tx'))
    B, L = g['B'], g['L']
    rng = np.random.default_rng(seed)
    rng_on = rng.uniform(0, 1, (40, nb))
    tw = rng.uniform(0, 2 * np.pi, nb)
    F = nframes(D)
    out = np.zeros((F, G.N, 3))
    d = G.pd[G.path]
    n = G.N

    def dot(x, c, lvl, w):
        return light(c, lvl * np.exp(-((d - x) / w) ** 2))

    for f in range(F):
        t = f * DT
        master = keys(t, [(0, 0), (0.8, 1), (D - 1.5, 1), (D, 0)])
        buf = light(NIGHT, 0.14 * np.ones(n))

        # the box on the porch: warm, the lid coming off, emptying as the string comes out
        box = keys(t, [(0, 0.55), (T_LID, 0.55), (T_LID + 0.1, 1.0), (T_LID + 0.6, 0.6), (T_LEFT_END, 0.4),
                       (T_PLUG, 0.0), (T_TESTER - 1.0, 0.0), (T_TESTER, 0.6), (T_TESTER + 1.5, 0.2), (T_POP, 0.2),
                       (T_NEW, 0.6), (T_CLICK, 0.0)])
        if box > 0:
            jig = 6 * np.sin(2 * np.pi * 5 * t) * (t < T_LID + 1.0) * (t > 0.6)
            buf += dot(B + jig, BOX, box, 26) + dot(B, WHITE, 0.6 * np.exp(-max(0, t - T_LID) / 0.15) * (t >= T_LID), 40)

        # the bulbs
        if t < T_BLAZE:
            lv = lit_level(P, t, rng_on)
            glass = GLASS + 0.08 * (t < T_PLUG)
            I = np.where(outb[f], glass + (0.82 - glass) * lv, 0.0)
            p = pos[f]
        else:
            a = t - T_BLAZE
            front = L - BLAZE_V * a
            reached = homes >= front
            step = int((t - T_BLAZE) / BEAT) if t < T_FAST else int((T_FAST - T_BLAZE) / BEAT) + int((t - T_FAST) / (BEAT / 2))
            if t < T_FULL:
                kind_now = (kind + step) % len(BULBS)
            else:
                kind_now = (kind + int((T_FULL - T_FAST) / (BEAT / 2)) + int((T_FAST - T_BLAZE) / BEAT)) % len(BULBS)
            col_now = np.array(BULBS)[kind_now]
            I = np.where(reached, 0.62, GLASS)
            # chases round the house: from the outlet to the back of the Side, then both ways
            if t < T_FULL:
                period = 2 * BAR if t < T_FAST else BAR
                ph = ((t - T_BLAZE) % period) / period
                head = L + 200 - ph * (L + 400)
                I = I + 0.38 * reached * np.exp(-((homes - head) / 110) ** 2)
                heads = [head]
                if t >= T_FAST:
                    head2 = -200 + ph * (L + 400)
                    I = I + 0.38 * np.exp(-((homes - head2) / 110) ** 2)
                    heads.append(head2)
            else:
                I = I + 0.3 * smoothstep(T_FULL, T_FULL + 0.5, t) + 0.08 * np.sin(2 * np.pi * 0.7 * t + tw)
            p = homes
        if t < T_BLAZE:
            col_now = col
        I = np.clip(I, 0, 1)
        near = np.abs(d[:, None] - p[None]) < 30
        k1 = np.where(near, np.exp(-((d[:, None] - p[None]) / 5.5) ** 2), 0)
        k2 = np.where(near, np.exp(-((d[:, None] - p[None]) / 11.0) ** 2), 0)
        buf += (k1 * perc(I)[None]) @ col_now + (k2 * perc(0.55 * I)[None]) @ col_now

        if T_BLAZE + 1.0 <= t < T_FULL:                              # the chases' white highlights
            for h_ in heads:
                buf += light(WHITE, 0.4 * np.exp(-((d - h_) / 55) ** 2))

        # the lead ends while it is pulled: the plug (gold) and the end cap
        if T_RIGHT <= t < T_LEFT_END + 1.5:
            fade = 1 - smoothstep(T_LEFT_END, T_LEFT_END + 1.5, t)
            buf += dot(P['eR'][f] + 8, PLUG, 0.85 * fade, 6)
            if t >= T_LEFT:
                buf += dot(P['eL'][f] - 8, WHITE, 0.55 * fade, 5)

        # knots: shimmering while they snag, a white crack when they snap
        for side, a_, b_, ts, tsn in SNAGS:
            m = np.where((P['right'] if side == 'R' else ~P['right']) & (P['rank'] >= a_) & (P['rank'] <= b_))[0]
            if ts - 1.5 <= t < tsn:
                cx = pos[f][m].mean()
                tug = sum(np.exp(-((t - tb) / 0.08) ** 2) for tb in np.arange(ts + BEAT, tsn, BEAT))
                buf += dot(cx, WHITE, 0.25 + 0.45 * tug, 10 + 2 * len(m))
            if tsn <= t < tsn + 0.5:
                cx = pos[min(F - 1, int(tsn / DT))][m].mean()
                a = t - tsn
                buf += dot(cx, WHITE, np.exp(-a / 0.1), 20 + 200 * a)

        # sparks: at the outlet when it is plugged in, at the dud when it pops
        for ts_, x_, big in ((T_PLUG, L - 8, 1.0), (T_SPARK, L - 8, 1.0), (T_OUT1, homes[dud], 1.0), (T_OUT2, homes[dud], 0.8),
                             (T_CASCADE, homes[dud], 0.8)):
            a = t - ts_
            if 0 <= a < 0.4:
                buf += dot(x_, WHITE, big * np.exp(-a / 0.07), 14) + dot(x_, TESTER, 0.6 * np.exp(-a / 0.15), 30)

        # the tester
        if not np.isnan(tx[f]):
            pulse = 0.75 + 0.25 * np.sin(2 * np.pi * 4 * t)
            buf += dot(tx[f], TESTER, pulse, 6) + dot(tx[f], TESTER, 0.35 * pulse, 18)
        if T_FOUND <= t < T_POP:                                    # found it: the dud flashes red
            on = ((t - T_FOUND) % 0.3) < 0.15
            buf += dot(homes[dud], ALARM, 1.0 * on, 9)

        # the swap: the dud falls away toward the Side, a new bulb flies in from the box
        if T_POP <= t < T_POP + 1.2:
            a = t - T_POP
            buf += dot(homes[dud] - 160 * a - 120 * a * a, WHITE, 0.55 * (1 - a / 1.2), 6)
            buf += dot(homes[dud], WHITE, 0.8 * np.exp(-a / 0.1), 10)
        if T_NEW <= t < T_CLICK:
            u = smoothstep(T_NEW, T_CLICK, t)
            x = B + (homes[dud] - B) * u
            buf += dot(x, BULBS[kind[dud]], 1.0, 7) + dot(x, TESTER, 0.6, 18)
            for k in range(1, 8):
                uk = smoothstep(T_NEW, T_CLICK, t - k * DT)
                buf += dot(B + (homes[dud] - B) * uk, TESTER, 0.4 * (1 - k / 8), 7)

        # the blaze: a white front from the outlet to the back of the Side
        if T_BLAZE <= t < T_BLAZE + 2.0:
            a = t - T_BLAZE
            front = L - BLAZE_V * a
            buf += light(WHITE, np.exp(-((d - front) / 70) ** 2) * (1 - a / 2.0))
            buf += light(WHITE, 0.35 * np.exp(-a / 0.3) * np.ones(n))
        if t >= T_END - 0.05:
            a = t - T_END
            buf += light(WHITE, 0.4 * np.exp(-a / 0.35) * np.ones(n))
        out[f][G.path] = np.clip(buf, 0, 1) * master
    return out


# ---- music ----
PULL = ('C4 E4 G4 E4 | F4 A4 G4:2 | E4 G4 C5 G4 | A4 F4 D4:2 | C4 E4 G4 E4 | F4 A4 C5:2 | B4 G4 D5 B4 | C5:2 G4:2')
PULL_CH = [('C', 'E', 'G'), ('F', 'A', 'C'), ('C', 'E', 'G'), ('D', 'F', 'A'), ('C', 'E', 'G'), ('F', 'A', 'C'),
           ('G', 'B', 'D'), ('C', 'E', 'G')]
RUN_CH = [('C', 'E', 'G'), ('D', 'F', 'A'), ('E', 'G', 'B'), ('F', 'A', 'C'), ('G', 'B', 'D'), ('A', 'C', 'E')]
HUNT_BASS = ['A2', 'C3', 'E3', 'C3', 'A2', 'C3', 'E3', 'G#2', 'D3', 'F3', 'A3', 'F3', 'E3', 'G#2', 'B2', 'E2']
HUNT_TUNE = 'r:2 E4 F4 | E4:2 r:2 | r:2 E4 F4 | G#4:2 r:2 | r:2 F4 G4 | A4:2 r:2 | r:2 B3 C4 | B3:2 r:2'
GALOP = ('C5 G4 E4 G4 | A4:2 F4:2 | D4 E4 F4 A4 | G4:4 | C5 G4 E4 G4 | A4 B4 C5 D5 | E5 D5 C5 B4 | C5:4')
GALOP_CH = [('C', 'E', 'G'), ('F', 'A', 'C'), ('D', 'F', 'A'), ('G', 'B', 'D', 'F'), ('C', 'E', 'G'),
            ('F', 'A', 'C'), ('G', 'B', 'D'), ('C', 'E', 'G')]


def phrase(s, t0):
    outl, b = [], 0.0
    for tok in s.replace('|', ' ').split():
        nm, _, bt = tok.partition(':')
        bt = float(bt) if bt else 1.0
        outl.append((t0 + b * BEAT, None if nm == 'r' else nm, bt * BEAT))
        b += bt
    return outl


def score(M, G):
    from pixelhome.audio import SR, note, slide, whoosh
    n = note
    P = plan(G)
    g, homes, nb, kind, dud, pos, outb = P['g'], P['homes'], P['nb'], P['kind'], P['dud'], P['pos'], P['out']
    B, L = g['B'], g['L']

    clar = M.sampler('Woodwinds/Clarinet/stac/*.wav', tune=-12)
    bsn = M.sampler('Woodwinds/Bassoon/stac/*.wav', tune=-12)
    fl_st = M.sampler('Woodwinds/Flute/stac/*.wav', tune=-12)
    cello = M.sampler('Strings/Cello Section/pizzT/*.wav', tune=-12)
    viola = M.sampler('Strings/Viola Section/pizz/*.wav', tune=-12)
    vln_p = M.sampler('Strings/Violin Section/Pizz/*.wav', tune=-12)
    cbass = M.sampler('Strings/Solo Contrabass/Pizz/*.wav', tune=-12)
    vln = M.sampler('Strings/Violin Section/susVib/*.wav', tune=-12)
    vla = M.sampler('Strings/Viola Section/susvib/*.wav', tune=-12)
    vc = M.sampler('Strings/Cello Section/susvib/*.wav', tune=-12)
    trem = M.sampler('Strings/Violin Section/Trem/*.wav', tune=-12)
    horn = M.sampler('Brass/F Horn/sus/*.wav', tune=-12)
    tpt = M.sampler('Brass/Trumpet/stac/*.wav', tune=-12)
    tpt_s = M.sampler('Brass/Trumpet/sus/*.wav', tune=-12)
    wah = M.sampler('Brass/Trumpet/harmonM-sus/*.wav', tune=-12)
    fall = M.sampler('Brass/OldTrombone/Fall/*.wav', tune=-12)
    tuba = M.sampler('Brass/Tuba/stac/*.wav', tune=-12)
    glock = M.sampler('Percussion/Glock/*.wav', tune=-12)
    xylo = M.sampler('Percussion/Xylo/*.wav', tune=-12)
    harp = M.sampler('Strings/Harp/*.wav')
    zap = M.hits('Percussion/zap[12]_v1.wav')
    slap = M.hits('VSCO 1 Percussion/varWood/slapstick[12].wav')
    clave = M.hits('Percussion/Claves1_Hit_v2*.wav')
    ratchet = M.hits('VSCO 1 Percussion/varWood/ratchet1.wav')
    timp = M.hits('Percussion/Timpani/Timpani1_Hit_v[13]*.wav')
    troll = M.hits('Percussion/Timpani/Rolls/Timpani1_Roll_v3*.wav')
    crash = M.hits('VSCO 1 Percussion/varMetal/Cymbals/clash/crash_hit_ff*.wav')
    crash_mf = M.hits('Percussion/cymbal-crash1_mf*.wav')
    bd = M.hits('VSCO 1 Percussion/drums/bass/bdrum_f_*.wav')
    snare = M.hits('Percussion/Snare2-HitSN_v[35]*.wav')
    sroll = M.hits('Percussion/Snare2-rollSN_v5*.wav')
    sleigh = M.hits('Percussion/Sleighbells_Hit*.wav')
    chimes = M.hits('VSCO 1 Percussion/varMetal/various/windchimes_fastAsc1.wav')
    tri = M.hits('Percussion/Triangle3-Hit_v1*.wav')

    for name, gain, rev in (('tune', 0.47, 0.15), ('pizz', 0.52, 0.1), ('harm', 0.4, 0.3), ('perc', 0.46, 0.12),
                            ('fx', 0.34, 0.15), ('sparkle', 0.28, 0.3)):
        M.bus(name, gain=gain, reverb=rev)

    order = np.argsort(G.pd)
    xs, ds = G.pos[order, 0], G.pd[order]
    x0, x1 = xs.min(), xs.max()

    def pan_at(dd):
        x = np.interp(np.clip(dd, 0, L), ds, xs)
        return 0.85 * (2 * (x - x0) / (x1 - x0) - 1)

    def mono(sig, pans):
        a = (np.clip(pans, -1, 1) + 1) * np.pi / 4
        return np.vstack([sig * np.cos(a), sig * np.sin(a)]) * np.sqrt(2)

    def chord(names, octave):
        outl, last = [], -1
        for c in names:
            m = n(c + str(octave))
            while m <= last:
                m += 12
            outl.append(m)
            last = m
        return outl

    def melody(s, t0, insts, vel=96, short=True):
        for t, m, dur in phrase(s, t0):
            if m is None:
                continue
            for inst, bus, gn, pn, dv in insts:
                M.add(bus, inst.play(n(m) + dv, vel, dur=dur * (0.55 if short else 0.95),
                                     release=0.1 if short else 0.3), t, gn, pn)

    def oompah(ch, t0, vel=95, inst=None, gain=0.85, beats=4):
        inst = inst or cello
        root, fifth = n(ch[0] + '2'), n(ch[2] + '2')
        if fifth < root:
            fifth += 12
        for k in range(beats):
            tb = t0 + k * BEAT
            if k % 2 == 0:
                M.add('pizz', inst.play(root if k % 4 == 0 else fifth - 12 if fifth - 12 >= root - 5 else fifth, vel), tb, gain)
            else:
                for m in chord(ch[:3], 3):
                    M.add('pizz', viola.play(m, vel - 25), tb, 0.35, 0.2)

    def buzz(seconds, gate, f0=120.0, amp=0.25):            # mains hum through a loose connection
        k = int(seconds * SR)
        tt = np.arange(k) / SR
        ph = 2 * np.pi * f0 * tt
        s = np.sign(np.sin(ph)) * 0.5 + np.sin(2 * ph) * 0.3 + np.sin(3 * ph) * 0.2
        g_ = np.interp(tt, np.arange(len(gate)) * 0.06, gate)
        return amp * s * g_ * np.clip(tt / 0.01, 0, 1) * np.clip((seconds - tt) / 0.03, 0, 1)

    def beep(f=1250.0, seconds=0.07, amp=0.2):
        tt = np.arange(int(seconds * SR)) / SR
        s_ = amp * np.sin(2 * np.pi * f * tt) * np.clip(tt / 0.004, 0, 1) * np.clip((seconds - tt) / 0.015, 0, 1)
        return np.vstack([s_, s_])

    # ---- 0-3: the box ----
    for i, m in enumerate(('C4', 'E4', 'G4')):
        M.add('pizz', viola.play(n(m), 70), 0.3 + 0.25 * i, 0.5, pan_at(B))
    M.add('perc', ratchet.play(55), 0.7, 0.3, pan_at(B))
    M.add('perc', slap.play(75), T_LID, 0.5, pan_at(B))
    for i, m in enumerate(chord(('C', 'E', 'G'), 3) + chord(('C', 'E', 'G'), 4) + [n('C5')]):
        M.add('harm', harp.play(m, 80), T_LID + 0.05 + 0.07 * i, 0.6, pan_at(B))
    M.add('sparkle', chimes.play(80), T_LID, 0.4, pan_at(B))

    # ---- 3-24: the pull: a jaunty tune that stops at every snag ----
    snag_spans = [(ts, tsn) for _, _, _, ts, tsn in SNAGS]
    def snagged(t):
        return any(ts <= t < tsn for ts, tsn in snag_spans)
    bar0 = 1
    for k in range(11):                                            # bars 1..11, the tune skipping the snag beats
        t0 = at(bar0 + k)
        s = PULL.split('|')[k % 8]
        for t, m, dur in phrase(s, t0):
            if m is None or snagged(t) or t < T_RIGHT - 0.01:
                continue
            M.add('tune', clar.play(n(m), 95, dur=dur * 0.5), t, 0.75, -0.15)
            M.add('tune', bsn.play(n(m) - 12, 85, dur=dur * 0.5), t, 0.5, 0.15)
        ch = PULL_CH[k % 8]
        for b in range(4):
            tb = t0 + b * BEAT
            if snagged(tb) or tb < T_RIGHT - 0.01:
                continue
            if b % 2 == 0:
                M.add('pizz', cello.play(n(ch[0] + '2') + (7 if b == 2 else 0), 100), tb, 0.8)
            else:
                for m in chord(ch, 3):
                    M.add('pizz', viola.play(m, 70), tb, 0.35, 0.2)
    # every bulb out of the box: a soft clink of glass, panned to the box side it leaves by
    first = np.argmax(outb, axis=0)
    pent = [n(m) for m in ('C5', 'D5', 'E5', 'G5', 'A5', 'C6')]
    for i in range(nb):
        if first[i] == 0 or first[i] * DT > T_LEFT_END + 0.5:
            continue
        tf = first[i] * DT
        M.add('sparkle', glock.play(pent[(i * 7) % 6] - 12, int(M.rng.integers(40, 58))), tf, 0.45,
              pan_at(B + (60 if P['right'][i] else -60)))
    # the snags: tug, tug, tug; then the snap
    for side, a_, b_, ts, tsn in SNAGS:
        m = np.where((P['right'] if side == 'R' else ~P['right']) & (P['rank'] >= a_) & (P['rank'] <= b_))[0]
        fts = min(nframes(D) - 1, int(ts / DT))
        px = pan_at(float(pos[fts][m].mean()))
        for j, tb in enumerate(np.arange(ts + BEAT, tsn, BEAT)):
            M.add('pizz', tuba.play(n('G1') + 12 + j, 110, dur=0.25), tb, 0.8, px * 0.5)
            M.add('perc', timp.play(95, pitch=-3 + j), tb, 0.6, px)
            M.add('harm', trem.play(n('G3') + j, 60, dur=0.4, release=0.1), tb, 0.3, px)
        M.add('perc', slap.play(110), tsn, 0.8, px)
        M.add('fx', slide(0.0, 0.35, 450, 1500, 0.4, 0.35, 0.5), tsn, 0.7, px)
        big = b_ - a_ > 8
        for i, mm in enumerate(chord(('G', 'B', 'D'), 3) + chord(('G', 'B', 'D'), 4) + ([n('G5'), n('B5')] if big else [])):
            M.add('harm', harp.play(mm, 85), tsn + 0.03 * i, 0.6, px)
        if big:
            M.add('perc', crash_mf.play(95), tsn, 0.5, px)

    # ---- 24-26: laid out ----
    M.add('perc', tri.play(80), T_LEFT_END, 0.5, pan_at(0))
    for m in ('C3', 'G3', 'E4'):
        M.add('harm', vln.play(n(m) + 12, 75, dur=1.8, release=0.4), T_LEFT_END, 0.4)
        M.add('harm', vc.play(n(m), 70, dur=1.8, release=0.4), T_LEFT_END, 0.4)
    melody('E4 G4 C5:2', T_LEFT_END, [(clar, 'tune', 0.7, 0.0, 0), (fl_st, 'tune', 0.4, 0.1, 0)], vel=90)
    M.add('pizz', cbass.play(n('C2'), 100), T_LEFT_END, 0.8)

    # ---- 26-34: plugged in: each run buzzes, lands, and the chords climb ----
    M.add('perc', zap.play(70), T_PLUG, 0.5, pan_at(L))
    M.add('perc', clave.play(90), T_PLUG, 0.5, pan_at(L))
    sec_mid = [(g['c5'] + L) / 2, (g['c4'] + g['c5']) / 2, B, (g['c2'] + g['c3']) / 2, (g['c1'] + g['c2']) / 2, g['c1'] / 2]
    for s, ts in enumerate(RUNS_ON):
        gate = (np.random.default_rng(s).uniform(0, 1, 13) > 0.4).astype(float)
        M.add('fx', mono(buzz(0.7, gate, 120, 0.12), np.full(int(0.7 * SR), pan_at(sec_mid[s]))), ts, 1.0)
        ch = RUN_CH[s]
        for m in chord(ch, 3):
            M.add('harm', vln.play(m + 12, 70 + 5 * s, dur=RUNS_ON[s + 1] - ts if s < 5 else T_OUT1 - ts, release=0.1),
                  ts + 0.7, 0.3, pan_at(sec_mid[s]) * 0.5)
            M.add('harm', horn.play(m, 70 + 5 * s, dur=0.9, release=0.3), ts + 0.7, 0.35, pan_at(sec_mid[s]) * 0.5)
        M.add('pizz', cbass.play(n(ch[0] + '2'), 100), ts + 0.7, 0.8)
        M.add('sparkle', glock.play(n(ch[0] + '5'), 85), ts + 0.7, 0.5, pan_at(sec_mid[s]))
        M.add('perc', timp.play(80 + 6 * s, pitch=-5 + 2 * s), ts + 0.7, 0.5, pan_at(sec_mid[s]))

    # ---- 34-44: the dud: out, back, out, back, and out from the dud ----
    pd_ = pan_at(homes[dud])
    for t0, big in ((T_OUT1, 1.0), (T_OUT2, 1.1)):
        M.add('perc', zap.play(int(100 * big)), t0, 0.7, pd_)
        M.add('tune', fall.play(n('D3') if big < 1.05 else n('C3'), 105, dur=1.4, release=0.3), t0 + 0.15, 0.8, 0.0)
        M.add('pizz', cbass.play(n('C2'), 90), t0 + 0.15, 0.6)
    for back in (WIGGLE1, WIGGLE2):
        for tw_, dw in back:
            M.add('perc', ratchet.play(60), tw_ - 0.15, 0.3, pan_at(L))
            M.add('fx', mono(buzz(dw + 0.05, np.ones(5), 120, 0.14), np.full(int((dw + 0.05) * SR), 0.0)), tw_, 1.0)
    for t0 in (T_BACK1, T_BACK2):
        for m in chord(('C', 'E', 'G'), 3):
            M.add('harm', vln.play(m + 12, 80, dur=1.5, release=0.3), t0, 0.35)
            M.add('tune', tpt.play(m, 100, dur=0.3), t0, 0.4)
        M.add('pizz', cbass.play(n('C2'), 105), t0, 0.8)
        M.add('perc', crash_mf.play(85), t0, 0.35)
        if t0 == T_BACK1:                                          # and a hopeful bar of the tune
            melody('C5 G4 E4 G4 | A4:2 F4:2', t0 + BAR / 2, [(clar, 'tune', 0.7, -0.1, 0), (fl_st, 'tune', 0.4, 0.1, 0)])
    # the dark spreading out from the dud: a falling run either side
    for j in range(10):
        tj = T_CASCADE + j * 0.11
        M.add('sparkle', xylo.play(n('C6') - [0, 2, 4, 5, 7, 9, 11, 12, 14, 16][j], 95), tj, 0.55, pd_ + 0.08 * j)
    M.add('perc', zap.play(100), T_CASCADE, 0.6, pd_)
    M.add('tune', fall.play(n('C3') - 2, 110, dur=1.8, release=0.4), T_CASCADE + 0.4, 0.9, 0.0)

    # ---- 44-60: the tester hunts: a sneaking walk in A minor and a beep per bulb ----
    for k in range(int((T_FOUND - at(22)) / BAR) + 1):
        t0 = at(22 + k)
        for b in range(4):
            tb = t0 + b * BEAT
            if tb >= T_FOUND:
                break
            M.add('pizz', cbass.play(n(HUNT_BASS[(4 * k + b) % 16]), 92), tb, 0.85)
            if b % 2 == 1:
                M.add('pizz', viola.play(n(HUNT_BASS[(4 * k + b) % 16]) + 12, 55), tb + BEAT / 2, 0.35)
        for t, m, dur in phrase(HUNT_TUNE.split('|')[k % 8], t0):
            if m is not None and t < T_FOUND:
                M.add('tune', clar.play(n(m), 80, dur=dur * 0.5), t, 0.7, -0.1)
                M.add('tune', bsn.play(n(m) - 12, 75, dur=dur * 0.5), t, 0.45, 0.1)
    for i in np.argsort(P['checks']):
        tc = P['checks'][i]
        if not np.isfinite(tc):
            continue
        M.add('fx', beep(1050 + 60 * kind[i], 0.06, 0.16), tc, 1.0, pan_at(homes[i]))
    tx = P['tx']
    M.add('perc', clave.play(80), T_TESTER, 0.5, pan_at(B))
    M.add('fx', slide(0.0, 0.3, 500, 1300, 0.35, 0.25, 0.5), T_TESTER, 0.6, pan_at(B))
    # it overshoots: a quizzical pair, then backs up
    M.add('tune', wah.play(n('E4'), 90, dur=0.3), at(28, 1), 0.6, pd_)
    M.add('tune', wah.play(n('F4'), 90, dur=0.4), at(28, 2), 0.6, pd_)
    # found: buzzer and wah-wah
    k = int((T_POP - T_FOUND) * SR)
    tt = np.arange(k) / SR
    bz = 0.22 * np.sign(np.sin(2 * np.pi * 110 * tt)) * (((tt % 0.3) < 0.15) * 1.0)
    M.add('fx', mono(bz, np.full(k, pd_)), T_FOUND, 0.6)
    for j, m in enumerate(('A4', 'G#4', 'G4', 'F#4')):
        M.add('tune', wah.play(n(m) - 12, 100, dur=0.3 if j < 3 else 0.6), T_FOUND + 0.3 * j, 0.7, pd_)
    M.add('perc', timp.play(100, pitch=-4), T_FOUND, 0.6, pd_)

    # ---- 60-64: the swap ----
    M.add('fx', slide(0.0, 0.4, 900, 1400, 0.45, 0.18, 0.5), T_POP - 0.45, 0.6, pd_)     # unscrewing squeak
    M.add('perc', zap.play(60), T_POP, 0.4, pd_)
    M.add('perc', slap.play(80), T_POP, 0.5, pd_)
    M.add('fx', slide(0.0, 1.1, 1000, 300, 1.2, 0.25, 0.7), T_POP + 0.05, 0.5, pan_at(homes[dud] - 200))
    for j in range(8):                                             # the new bulb flies in, glockenspiel rising
        uj = j / 7
        M.add('sparkle', glock.play(n(('C5', 'D5', 'E5', 'G5', 'A5', 'C6', 'D6', 'E6')[j]) - 12, 85),
              T_NEW + (T_CLICK - T_NEW) * uj, 0.6, pan_at(B + (homes[dud] - B) * uj))
    M.add('perc', clave.play(110), T_CLICK, 0.7, pd_)
    M.add('sparkle', tri.play(90), T_CLICK, 0.5, pd_)
    r = sroll.play(100, dur=T_BLAZE - T_CLICK)
    M.add('perc', r * np.linspace(0.05, 1.0, r.shape[1]) ** 2, T_CLICK + 0.2, 0.6)
    for m in ('G3', 'B3', 'D4', 'F4'):
        M.add('harm', trem.play(n(m), 70, dur=T_BLAZE - T_CLICK - 0.2, release=0.1), T_CLICK + 0.2, 0.35)
    M.add('perc', zap.play(90), T_SPARK, 0.6, pan_at(L))
    M.add('perc', clave.play(100), T_SPARK, 0.6, pan_at(L))

    # ---- 64: the blaze ----
    M.add('perc', crash.play(120), T_BLAZE, 0.75)
    M.add('perc', bd.play(120), T_BLAZE, 0.9)
    M.add('perc', timp.play(118, pitch=-5), T_BLAZE, 0.8)
    for m in chord(('C', 'E', 'G'), 3):
        M.add('harm', horn.play(m, 112, dur=1.5, release=0.5), T_BLAZE, 0.55, -0.2)
        M.add('tune', tpt_s.play(m + 12, 108, dur=1.2, release=0.4), T_BLAZE, 0.4, 0.2)
    bl = whoosh(1.4, 400, 4000, 0.9, seed=64)
    M.add('fx', mono(bl[0], np.linspace(pan_at(L), pan_at(0), bl.shape[1])), T_BLAZE, 0.7)

    # ---- 64-84: the galop: xylophone eighths step with the colours, a harp glissando for every chase ----
    for k in range(10):
        t0 = T_BLAZE + k * BAR
        s = GALOP.split('|')[k % 8] if k < 8 else ('E5 D5 C5 B4', 'C5:4')[k - 8]
        ch = GALOP_CH[k % 8] if k < 8 else (('G', 'B', 'D'), ('C', 'E', 'G'))[k - 8]
        melody(s, t0, [(tpt, 'tune', 0.75, 0.1, 0), (clar, 'tune', 0.55, -0.15, 0), (glock, 'sparkle', 0.3, 0.3, 12)],
               vel=106 if k < 8 else 112)
        oompah(ch, t0, vel=105, inst=tuba, gain=0.7)
        for m in chord(ch[:3], 3):
            M.add('harm', horn.play(m, 85, dur=BAR * 0.95, release=0.3), t0, 0.3, -0.25)
        step = BEAT if t0 < T_FAST else BEAT / 2
        tones = chord(ch[:3], 4) + [chord(ch[:3], 5)[0]]
        e = 0
        while e * step < BAR - 1e-6:
            tb = t0 + e * step
            M.add('sparkle', xylo.play(tones[e % 4], 80), tb, 0.45, (-0.4, 0.4)[e % 2])
            M.add('perc', sleigh.play(100 if e % 2 == 0 else 75), tb, 0.4, (0.35, -0.35)[e % 2])
            e += 1
        for b in (1, 3):
            M.add('perc', snare.play(85), t0 + b * BEAT, 0.35)
    # every chase round the house: a harp glissando following it from the outlet to the back of the Side
    for t0 in list(np.arange(T_BLAZE, T_FAST, 2 * BAR)) + list(np.arange(T_FAST, T_FULL, BAR)):
        period = 2 * BAR if t0 < T_FAST else BAR
        notes = chord(('C', 'E', 'G'), 4)[::-1] + chord(('C', 'E', 'G'), 3)[::-1]
        for j, m in enumerate(notes):
            tj = t0 + period * (200 + j / len(notes) * L) / (L + 400)
            M.add('harm', harp.play(m, 80), tj, 0.5, pan_at(L - j / len(notes) * L))
            if t0 >= T_FAST:
                M.add('harm', harp.play(m + 12 if m < n('C4') else m, 70), tj, 0.4, pan_at(j / len(notes) * L))
    M.add('perc', crash_mf.play(100), T_FAST, 0.5)
    M.add('perc', crash.play(110), T_FULL, 0.6)
    M.add('perc', bd.play(110), T_FULL, 0.7)
    M.add('sparkle', chimes.play(95), T_FULL, 0.5)
    # ---- 84: the last chord ----
    M.add('perc', crash.play(118), T_END, 0.7)
    M.add('perc', bd.play(118), T_END, 0.9)
    M.add('perc', timp.play(115, pitch=-5), T_END, 0.7)
    for m in chord(('C', 'E', 'G'), 3):
        M.add('harm', horn.play(m, 110, dur=1.6, release=0.5), T_END, 0.55, -0.2)
        M.add('tune', tpt_s.play(m + 12, 108, dur=1.5, release=0.5), T_END, 0.45, 0.2)
    M.add('pizz', tuba.play(n('C2'), 115, dur=1.2), T_END, 0.8)
    for i, m in enumerate(chord(('C', 'E', 'G'), 4) + [n('C5') + 12]):
        M.add('sparkle', glock.play(m, 95), T_END + 0.06 * i, 0.5, -0.3 + 0.2 * i)
