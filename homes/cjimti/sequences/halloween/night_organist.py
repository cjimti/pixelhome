"""The Night Organist: the roofline is the front of a grand old pipe organ. Seen from the street, the
two wing fronts are its ranks of pipes, one chromatic pipe per note from C2 (fat pipes at the far
left of Left) to C6 (thin ones at the free end of Right); the porch is the console. Moonlit pewter
pipes fade in low to high, the blower starts, two candles light on the console (the ends of Porch
Front) and a pair of pale green ghostly hands float in over the keyboard, crack their knuckles, and
play an original toccata in C minor at 100 BPM: a thundering opening flourish, racing broken-chord
figuration with syncopated left-hand stabs, a pedal solo (the hands wave about while two glowing
feet dance along Porch Left, the pedal board), scale runs in octaves that race the whole facade up
and down, hammered chords, a long trill, a grand pause and a huge final C major chord.

Every note is one entry in compose(); render() lights each note's pipe from it and score() plays
the same list, so the house literally plays the music (and each note is panned to its pipe). The
hands sit over the key each note is played on, and pedal notes light Left's fat pipes in ember.

The payoff: when everyone lets go of the last chord, the top pipe keeps sounding. The hands tap its
key three times (it hiccups and carries on), thump the console, and the pipe swells, whines sharper
and sharper, and pops like a cork. The cork flies the whole length of the roof and out the back of
Side, and lands with a distant clonk. A sheepish, very quiet Amen; the candles go out."""
import numpy as np
from pixelhome.fx import DT, hexc, perc, smoothstep, lerp, Flicker, nframes

CODE = 'HW14'
TITLE = 'The Night Organist'
KIND = 'show'
DESCRIPTION = ('The roofline becomes a grand pipe organ, low pipes on the left and high on the right, and a '
               'pair of ghostly hands plays a thundering toccata where every note lights its pipe. The big '
               'finish goes perfectly, except for one pipe that will not stop.')
VOICEOVER = ('At midnight the old organ wakes, and every pipe on the roof gets a note. '
             'Let\'s hope they all know when to stop.')

BEAT = 0.6                                   # 100 BPM
Q = BEAT / 4                                 # a sixteenth
LO, HI = 36, 84                              # C2 .. C6, one pipe per semitone
NP = HI - LO + 1
TOP = NP - 1                                 # the pipe that sticks

BLOWER = 1.2
CANDLES = (2.7, 3.05)
HANDS_IN = 3.5
KNUCKLES = (4.5, 4.85, 5.2)
T0 = 6.6                                     # the opening chord
TB = T0 + 14 * BEAT                          # toccata
TC = TB + 32 * BEAT                          # pedal solo
TD = TC + 8 * BEAT                           # runs in octaves
TF = TD + 16 * BEAT                          # the dominant and its trill
TFIN = TF + 5.5 * BEAT                       # the last chord, after a grand pause
TREL = TFIN + 6 * BEAT                       # everyone lets go ... nearly
TAPS = (TREL + 1.5, TREL + 1.85, TREL + 2.2)
THUMP = TREL + 3.1
TPOP = TREL + 5.4
FLY = 2.2                                    # the cork's trip down the roof
CLONK = TPOP + FLY + 0.55
TAMEN = TPOP + 4.6
TSNUFF = TAMEN + 5.2
D = TSNUFF + 3.0

MINOR = (0, 2, 3, 5, 7, 8, 11)               # C harmonic minor
CHORDS = {'Cm': (0, 3, 7), 'Ab': (8, 0, 3), 'Fm': (5, 8, 0), 'G7': (7, 11, 2, 5), 'Eb': (3, 7, 10)}
ROOT = {'Cm': 36, 'Ab': 44, 'Fm': 41, 'G7': 43, 'Eb': 39}

STEEL = hexc('#7080ff')
GOLD = hexc('#ffb020')
EMBER = hexc('#ff5208')
HOT = hexc('#fff0c8')
WIND = hexc('#6a18ff')
WIND_HOT = hexc('#ff2050')
GHOST = hexc('#90ffc0')
FLAME = hexc('#ff9028')
WOOD = hexc('#ff5a18')
CORK = hexc('#ffe4a8')
TRAIL = hexc('#ff7010')
WHITE = hexc('#ffffff')


def tones(ch, lo, hi):
    return [x for x in range(lo, hi + 1) if x % 12 in CHORDS[ch]]


def scale(lo, hi):
    return [x for x in range(lo, hi + 1) if x % 12 in MINOR]


def compose():
    """Every note of the piece: (time, duration, midi, velocity, part). Parts: 'ped' pedal, 'lh'/'rh' the
    hands, 'cipher' the top pipe of the last chord that won't stop, 'qp'/'qm' the quiet Amen."""
    N = []

    def add(t, d, notes, vel, part):
        for x in np.atleast_1d(notes):
            N.append((float(t), float(d), int(x), int(vel), part))

    def b(k):
        return T0 + k * BEAT

    # ---- exordium: chord, run up, chord, run down, the dominant with a trill, home ----
    add(b(0), 2 * BEAT, 36, 120, 'ped')
    add(b(0), 2 * BEAT, [48, 55], 118, 'lh')
    add(b(0), 2 * BEAT, [60, 63, 67, 72], 120, 'rh')
    for i, x in enumerate([67, 68, 71, 72, 74, 75, 77, 79]):
        add(b(2.5) + i * Q, Q * 1.1, x, 104 + 2 * i, 'rh')
    add(b(4.5), 1.5 * BEAT, 41, 118, 'ped')
    add(b(4.5), 1.5 * BEAT, [53, 56], 116, 'lh')
    add(b(4.5), 1.5 * BEAT, [60, 65, 68, 80], 120, 'rh')
    for i, x in enumerate([79, 77, 75, 74, 72, 71, 68, 67, 65, 63, 62, 60]):
        add(b(6) + i * Q, Q * 1.1, x, 118 - 2 * i, 'rh')
    add(b(9), 2 * BEAT, 43, 118, 'ped')
    add(b(9), 2 * BEAT, [55, 59], 112, 'lh')
    add(b(9), 2 * BEAT, [62, 65, 68], 110, 'rh')
    for i in range(8):
        add(b(9) + i * Q, Q * 1.05, 71 if i % 2 == 0 else 72, 100, 'rh')
    add(b(11), 2 * BEAT, 36, 122, 'ped')
    add(b(11), 2 * BEAT, [48, 55], 120, 'lh')
    add(b(11), 2 * BEAT, [60, 63, 67, 72, 75], 122, 'rh')

    # ---- toccata: broken chords up and down the right wing in a 3-beat swing against 4-beat bars ----
    j = 0
    for bar, ch in enumerate(['Cm', 'Ab', 'Fm', 'G7', 'Cm', 'Eb', 'Ab', 'G7']):
        t0 = TB + bar * 4 * BEAT
        T = tones(ch, 40, HI)[-7:]
        for s in range(16):
            tri = 1 - abs(2 * (j % 12) / 12 - 1)
            add(t0 + s * Q, Q * 1.15, T[int(round(tri * 6))], 94 + 10 * (s % 4 == 0), 'rh')
            j += 1
        r = ROOT[ch]
        add(t0, 2 * BEAT, r, 112, 'ped')
        add(t0 + 2 * BEAT, 2 * BEAT, r + 7, 104, 'ped')
        for s in (0, 6, 8, 14):
            add(t0 + s * Q, Q * 1.6, tones(ch, 48, 59)[:3], 102 + 8 * (s == 0), 'lh')

    # ---- pedal solo: eighths, then sixteenths round a G pedal point ----
    for i, x in enumerate([36, 39, 43, 48, 47, 43, 44, 41]):
        add(TC + i * BEAT / 2, BEAT / 2 * 0.95, x, 116, 'ped')
    for i, x in enumerate([43, 50, 47, 50, 43, 51, 48, 51, 43, 53, 50, 53, 55, 53, 51, 50]):
        add(TC + 4 * BEAT + i * Q, Q * 0.95, x, 112 + (i == 12) * 10, 'ped')

    # ---- climax: chord on the downbeat, then a run in octaves the length of the facade ----
    up = scale(48, HI)
    for bar, (ch, rise) in enumerate((('Cm', True), ('Fm', False), ('Ab', True))):
        t0 = TD + bar * 4 * BEAT
        add(t0, 4 * BEAT, ROOT[ch], 122, 'ped')
        add(t0, BEAT * 0.9, tones(ch, 48, 59)[:3], 122, 'lh')
        add(t0, BEAT * 0.9, tones(ch, 60, 72)[:4], 124, 'rh')
        run = up if rise else up[::-1]
        step = 3 * BEAT / len(run)
        for i, x in enumerate(run):
            v = 100 + int(24 * i / len(run)) if rise else 124 - int(20 * i / len(run))
            add(t0 + BEAT + i * step, step * 1.3, x, v, 'rh')
            add(t0 + BEAT + i * step, step * 1.3, x - 12, v - 6, 'lh')
    t0 = TD + 12 * BEAT                       # hammered chords over a G pedal, climbing
    add(t0, 4 * BEAT, 43, 124, 'ped')
    for i, c in enumerate([[56, 60, 63]] * 2 + [[57, 60, 63]] * 2 + [[58, 62, 65]] * 2 + [[59, 62, 65, 68]] * 2):
        v = 100 + 3 * i
        add(t0 + i * BEAT / 2, BEAT / 2 * 0.75, c, v, 'lh')
        add(t0 + i * BEAT / 2, BEAT / 2 * 0.75, [x + 12 for x in c], v + 2, 'rh')

    # ---- the dominant, a long trill, a grand pause, and the last chord (in C major) ----
    add(TF, 4 * BEAT, 43, 124, 'ped')
    add(TF, 4 * BEAT, [55, 59], 120, 'lh')
    add(TF, 4 * BEAT, [62, 65], 118, 'rh')
    for i, x in enumerate([80, 79] * 7 + [77, 79]):
        add(TF + i * Q, Q * 1.05, x, 108, 'rh')
    add(TFIN, TREL - TFIN, 36, 127, 'ped')
    add(TFIN, TREL - TFIN, [48, 55, 60], 124, 'lh')
    add(TFIN, TREL - TFIN, [64, 67, 72, 76, 79], 124, 'rh')
    add(TFIN, TPOP - TFIN, HI, 124, 'cipher')

    # ---- the sheepish Amen, on the quietest stop ----
    add(TAMEN, 6 * BEAT, 36, 62, 'qp')
    add(TAMEN, 2 * BEAT, [53, 56, 60], 64, 'qm')
    add(TAMEN + 2 * BEAT, 4 * BEAT, [52, 55, 60], 60, 'qm')
    return sorted(N)


class Organ:
    """Where the pipes, the console, the pedal board and the feet are on this house."""

    def __init__(self, G):
        self.G = G
        L, R = G.seg['Left'], G.seg['Right']
        xl, xr = G.pos[L, 0], G.pos[R, 0]
        wl, wr = xl.max() - xl.min(), xr.max() - xr.min()
        raw = 30.0 * (12.0 / 30.0) ** (np.arange(NP) / (NP - 1))       # fat low pipes, thin high ones
        cum = np.cumsum(raw) / raw.sum()
        nl = int(np.argmin(np.abs(cum - wl / (wl + wr)))) + 1            # pipes on Left, the rest on Right
        self.nl = nl
        edges = np.empty(NP + 1)
        edges[:nl + 1] = xl.min() + wl * np.concatenate([[0], np.cumsum(raw[:nl]) / raw[:nl].sum()])
        edges[nl:] = xr.min() + wr * np.concatenate([[0], np.cumsum(raw[nl:]) / raw[nl:].sum()])
        self.edges = edges
        self.centre = np.concatenate([(edges[:nl] + edges[1:nl + 1]) / 2, (edges[nl:-1] + edges[nl + 1:]) / 2])
        self.pix = np.concatenate([L, R])
        x = G.pos[self.pix, 0]
        pipe = np.empty(len(x), int)
        u = np.empty(len(x))
        for side, idx, lo, hi in ((0, slice(0, len(L)), 0, nl), (1, slice(len(L), None), nl, NP)):
            e = edges[lo:hi + 1] if side == 0 else edges[nl:]
            k = np.clip(np.searchsorted(e, x[idx], side='right') - 1, 0, hi - lo - 1)
            pipe[idx] = lo + k
            u[idx] = (x[idx] - e[k]) / (e[k + 1] - e[k])
        self.pipe = pipe
        self.prof = 0.3 + 0.7 * np.sin(np.pi * np.clip(u, 0, 1)) ** 0.6   # dark seams between pipes
        x0, x1 = G.pos[:, 0].min(), G.pos[:, 0].max()
        self.pan = 0.85 * (2 * (self.centre - x0) / (x1 - x0) - 1)
        F = G.seg['Porch Front']
        self.front = F
        fx = G.pos[F, 0]
        self.fx = fx
        self.ka, self.kb = fx.min() + 30, fx.max() - 30               # the keyboard, inside the candles
        PL = G.seg['Porch Left']
        self.pl = PL
        self.pld = G.pd[PL]
        self.pd0, self.pd1 = self.pld.min(), self.pld.max()

    def key_x(self, m):
        return self.ka + (np.asarray(m, float) - LO) / (HI - LO) * (self.kb - self.ka)

    def pedal_d(self, m):
        return self.pd0 + 40 + (np.clip(m, 36, 55) - 36) / 19 * (self.pd1 - self.pd0 - 80)

    def pan_x(self, x):
        G = self.G
        x0, x1 = G.pos[:, 0].min(), G.pos[:, 0].max()
        return float(0.85 * (2 * (x - x0) / (x1 - x0) - 1))


def render(G, seed=14):
    rng = np.random.default_rng(seed)
    O = Organ(G)
    notes = compose()
    nf = nframes(D)
    out = np.zeros((nf, G.N, 3))
    tt = np.arange(nf) * DT

    # ---- per-pipe light from the note list: sustain and attack, manual (gold) and pedal (ember) ----
    Em, Ep, At = np.zeros((nf, NP)), np.zeros((nf, NP)), np.zeros((nf, NP))
    for t, d, m, v, part in notes:
        k = m - LO
        f0 = int(round(t / DT))
        tail = 0.0 if part == 'cipher' else 0.45
        f1 = min(nf, int(round((t + d + tail) / DT)) + 1)
        s = tt[f0:f1] - t
        g = (v / 127) ** 1.4
        held = s < d
        e = np.where(held, 0.72 + 0.28 * np.exp(-s / 0.14),
                     (0.72 + 0.28 * np.exp(-d / 0.14)) * np.exp(-(s - d) / 0.09)) * g
        a = np.exp(-s / 0.07) * g
        if part == 'cipher':
            e = np.where(held, e, 0)
        tgt = Ep if part in ('ped', 'qp') else Em
        np.maximum(tgt[f0:f1, k], e, out=tgt[f0:f1, k])
        np.maximum(At[f0:f1, k], a, out=At[f0:f1, k])

    # the swell: how much organ is sounding, slowly followed
    raw = np.clip((Em.sum(1) + 1.6 * Ep.sum(1)) / 7.0, 0, 1.3)
    W = np.zeros(nf)
    w = 0.0
    for f in range(nf):
        tau = 0.35 if raw[f] > w else 1.1
        w += (raw[f] - w) * (1 - np.exp(-DT / tau))
        W[f] = w

    # ---- hands: each onset group moves its hand over the keys it plays ----
    groups = {}
    for t, d, m, v, part in notes:
        if part in ('lh', 'rh', 'qm', 'cipher'):
            hand = 1 if part in ('rh', 'cipher') else 0
            groups.setdefault((round(t, 4), hand), []).append((m, d))
    for (t, hand), ms in list(groups.items()):   # the Amen: lowest note left hand, the rest right
        if t >= TAMEN - 0.01 and hand == 0:
            lo = min(ms)
            groups[(t, 1)] = [x for x in ms if x != lo]
            groups[(t, 0)] = [lo]
    hx = np.zeros((2, nf))
    hw = np.zeros((2, nf))
    hf = np.zeros((2, nf))
    hh = np.zeros((2, nf))
    tgt_x = np.full((2, nf), np.nan)
    tgt_w = np.full((2, nf), np.nan)
    for (t, hand), ms in groups.items():
        f0 = int(round(t / DT))
        xs = O.key_x([m for m, _ in ms])
        tgt_x[hand, f0] = xs.mean()
        tgt_w[hand, f0] = max(26.0, xs.max() - xs.min() + 18)
        hf[hand, f0] = max(hf[hand, f0], 1.0)
        f1 = min(nf, int(round((t + max(d for _, d in ms)) / DT)) + 1)
        if t < TREL - 0.01 or hand == 0:
            hh[hand, f0:f1] = 1.0
    # gestures that aren't notes: knuckle cracks, the taps on the stuck key, the thump
    rest = (O.key_x(54), O.key_x(66))
    for tk in KNUCKLES:
        for hnd in range(2):
            hf[hnd, int(round(tk / DT))] = 1.0
    stuck_x = float(O.key_x(HI))
    for tk in TAPS:
        hf[1, int(round(tk / DT))] = 1.0
    hf[:, int(round(THUMP / DT))] = 1.3
    cx, cw = np.array(rest, float), np.array([28.0, 28.0])
    fl = np.zeros(2)
    for f in range(nf):
        t = tt[f]
        for hnd in range(2):
            if not np.isnan(tgt_x[hnd, f]):
                cx[hnd], cw[hnd] = tgt_x[hnd, f], tgt_w[hnd, f]
            gx, gw = cx[hnd], cw[hnd]
            if t < T0 - 0.05:                   # together in the middle for the knuckles
                gx, gw = O.key_x(60) + (hnd - 0.5) * 34, 26.0
            elif TC <= t < TD - 0.15:           # look, no hands: they wave while the feet play
                gx = rest[hnd] + 26 * np.sin(2 * np.pi * (t - TC) / (2 * BEAT) + hnd * np.pi)
                gw = 30.0
            elif TREL + 0.8 <= t < TPOP + 0.6:  # both hands go after the stuck key
                gx = stuck_x - (1 - hnd) * 40
                gw = 26.0
                if t >= THUMP - 0.15 and t < THUMP + 0.4:
                    gx, gw = O.key_x(60) + (hnd - 0.5) * 60, 40.0
            elif t >= TPOP + 0.6 and t < TAMEN - 0.3:
                gx, gw = rest[hnd], 26.0
            a = 1 - np.exp(-DT / 0.035)
            hx[hnd, f] = hx[hnd, f - 1] + (gx - hx[hnd, f - 1]) * a if f else gx
            hw[hnd, f] = hw[hnd, f - 1] + (gw - hw[hnd, f - 1]) * a if f else gw
            fl[hnd] = max(fl[hnd] * np.exp(-DT / 0.09), hf[hnd, f])
            hf[hnd, f] = fl[hnd]

    # ---- feet on the pedal board (Porch Left), alternating ----
    fd = np.zeros((2, nf))
    fh = np.zeros((2, nf))
    ffl = np.zeros((2, nf))
    pos = [O.pedal_d(36), O.pedal_d(43)]
    peds = [(t, d, m) for t, d, m, v, p in notes if p in ('ped', 'qp')]
    for i, (t, d, m) in enumerate(peds):
        foot = i % 2
        if i and abs(peds[i - 1][0] - t) < 1e-6:
            continue
        f0, f1 = int(round(t / DT)), min(nf, int(round((t + d) / DT)) + 1)
        fd[foot, f0:] = O.pedal_d(m)
        fh[foot, f0:f1] = 1.0
        ffl[foot, f0] = 1.0
    for foot in range(2):
        z = fd[foot] == 0
        fd[foot, z] = pos[foot]
        e = 0.0
        for f in range(nf):
            e = max(e * np.exp(-DT / 0.1), ffl[foot, f])
            ffl[foot, f] = e

    L = G.length

    side = G.seg['Side']
    PR = G.seg['Porch Right']
    flick = Flicker(rng, G.N, 2.0, 7.0)
    slow = Flicker(rng, G.N, 0.1, 0.5)
    fpx = O.fx
    cand = [np.argsort(fpx)[:4], np.argsort(fpx)[-4:]]
    stuck_pix = O.pix[O.pipe == TOP]
    stuck_near = O.pix[(O.pipe >= TOP - 2)]
    xs_pipes = G.pos[O.pix, 0]
    v_pipe = O.pipe / (NP - 1)
    ped_glow_side = np.clip((G.pd[side] - G.pd[side].min()) / (G.pd[side].max() - G.pd[side].min()), 0, 1)

    for f in range(nf):
        t = tt[f]
        fr = out[f]
        endfade = 1 - smoothstep(TSNUFF + 0.3, D - 0.3, t)

        # pipes
        blaze = smoothstep(TFIN, TREL - 0.3, t) if t < TREL else 0.0     # the whole case rings on the last chord
        idle = (0.28 + 0.3 * blaze) * smoothstep(0.2 + 2.0 * v_pipe, 0.9 + 2.0 * v_pipe, t) * endfade
        if t >= TPOP:
            idle = np.where(O.pipe == TOP, 0.0, idle)
        em, ep, at = Em[f, O.pipe], Ep[f, O.pipe], At[f, O.pipe]
        jolt = 0.4 * np.exp(-max(0.0, t - THUMP) / 0.12) if t >= THUMP else 0.0
        e = np.maximum(em, ep)
        hue = (ep > em).astype(float)[:, None]
        lit = GOLD * (1 - hue) + EMBER * hue
        base = lerp(STEEL, GOLD * 0.8 + STEEL * 0.2, min(1.0, W[f] * 0.7 + blaze))
        col = base * (1 - np.clip(e, 0, 1)[:, None]) + lit * np.clip(e, 0, 1)[:, None]
        inten = (idle + 0.85 * e + jolt * (t < TREL + 6)) * O.prof
        c = perc(inten)[:, None] * col + perc(0.9 * at * O.prof)[:, None] * HOT * 0.6
        fr[O.pix] = c

        # the stuck pipe: hiccups on each tap, then swells and whines until it pops
        if TREL <= t < TPOP:
            p = smoothstep(THUMP, TPOP, t)
            dip = sum(np.exp(-((t - tk - 0.06) / 0.05) ** 2) for tk in TAPS)
            wob = 0.5 + 0.5 * np.sin(2 * np.pi * (5 + 4 * p) * t)
            ii = (0.8 + 0.5 * p + 0.15 * p * wob) * (1 - 0.75 * min(1.0, dip))
            colr = lerp(GOLD, WHITE, p ** 1.5)
            fr[stuck_pix] = perc(ii) * colr
            bulge = np.clip(1 - np.abs(G.pos[stuck_near, 0] - O.centre[TOP]) / (8 + 26 * p), 0, 1)
            fr[stuck_near] = np.maximum(fr[stuck_near],
                                        perc(0.9 * p * bulge * (1 - 0.7 * min(1.0, dip)))[:, None] * colr)
        if TPOP <= t < TPOP + 0.5:
            fl_ = np.exp(-(t - TPOP) / 0.12)
            near = np.clip(1 - np.abs(xs_pipes - O.centre[TOP]) / 90, 0, 1)
            fr[O.pix] += perc(near * fl_)[:, None] * WHITE

        # Side: the wind in the big case, glowing with the swell, warmer with the pedal
        sw = (0.13 + 0.32 * W[f]) * smoothstep(BLOWER, BLOWER + 3.0, t) * endfade
        pedal_now = Ep[f].max()
        shim = 1 + 0.12 * slow(t)[side]
        sc = lerp(WIND, WIND_HOT, min(1.0, 0.6 * W[f] ** 2 + 0.3 * pedal_now))
        fr[side] = perc(sw * shim * (0.85 + 0.15 * ped_glow_side))[:, None] * sc

        # Porch Right: the swell box
        pr = (0.12 + 0.3 * W[f]) * smoothstep(BLOWER + 0.5, BLOWER + 3.0, t) * endfade
        fr[PR] = perc(pr * (1 + 0.1 * slow(t)[PR]))[:, None] * lerp(WIND, WIND_HOT, min(1.0, 0.7 * W[f] ** 2))

        # Porch Left: the pedal board, with two glowing feet
        pl = 0.1 * smoothstep(BLOWER + 0.5, BLOWER + 3.0, t) * endfade
        fr[O.pl] = perc(pl) * WIND
        fvis = smoothstep(HANDS_IN, HANDS_IN + 1.0, t) * (1 - smoothstep(TSNUFF - 1.0, TSNUFF - 0.3, t))
        for foot in range(2):
            prof = np.clip(1 - np.abs(O.pld - fd[foot, f]) / 26, 0, 1) ** 0.7
            b = fvis * (0.28 + 0.35 * fh[foot, f] + 0.4 * ffl[foot, f])
            fr[O.pl] = np.maximum(fr[O.pl], perc(b * prof)[:, None] * GHOST)

        # Porch Front: the console. Candles at the ends, hands over the keys.
        fr[O.front] = perc(0.09 * smoothstep(CANDLES[0], CANDLES[0] + 1.0, t) * endfade) * WOOD
        for i, tc in enumerate(CANDLES):
            if t >= tc:
                lv = smoothstep(tc, tc + 0.25, t) * (1 - smoothstep(TSNUFF + 0.15 * i, TSNUFF + 0.15 * i + 0.15, t))
                strike = 0.6 * np.exp(-(t - tc) / 0.1)
                ci = cand[i]
                fr[O.front[ci]] = perc(lv * (0.55 + 0.08 * flick(t)[O.front[ci]]) + strike)[:, None] * FLAME
                if t > TSNUFF + 0.15 * i:      # a wisp of smoke
                    sm = 0.12 * np.exp(-(t - TSNUFF - 0.15 * i) / 0.8)
                    fr[O.front[ci]] += perc(sm) * hexc('#a0a0c0')
        hvis = smoothstep(HANDS_IN, HANDS_IN + 0.9, t) * (1 - smoothstep(TSNUFF - 1.2, TSNUFF - 0.4, t))
        if hvis > 0:
            for hnd in range(2):
                prof = np.clip(1 - np.abs(fpx - hx[hnd, f]) / (hw[hnd, f] / 2), 0, 1) ** 0.6
                lift = 0.75 if TC <= t < TD - 0.15 else 1.0
                b = hvis * lift * (0.32 + 0.22 * hh[hnd, f] + 0.45 * min(1.0, hf[hnd, f]))
                fr[O.front] = np.maximum(fr[O.front], perc(b * prof)[:, None] * GHOST)

        # the cork: out of the top pipe, the whole length of the roof, and off the back of Side
        if TPOP <= t < TPOP + FLY + 0.1:
            u = min(1.0, (t - TPOP) / FLY)
            dh = L * (1 - u ** 0.85)
            rel = G.pd - dh                      # behind the cork is toward the end it came from
            head = np.clip(1 - np.abs(rel) / 9, 0, 1)
            trail = np.where(rel > 0, np.exp(-rel / 70), 0) * (rel < 300)
            np.maximum(out[f], perc(1.0 * head)[:, None] * CORK + perc(0.55 * trail)[:, None] * TRAIL, out=out[f])
        if CLONK <= t < CLONK + 0.4:
            k = np.exp(-(t - CLONK) / 0.1) * np.clip(1 - G.pd[side] / 40, 0, 1)
            fr[side] += perc(0.5 * k)[:, None] * CORK

    return np.clip(out, 0, 1)


def score(M, G):
    import glob
    import os
    import re
    from pixelhome.audio import SR, VSCO, slide, whoosh, _Voice, _load, _fade_out

    class Pipes(_Voice):
        """The VSCO2 pipe organ (Ivy Audio): samples are numbered, not named, every third key."""

        def __init__(self, pattern, first):
            self.zones = {}
            for p in sorted(glob.glob(os.path.join(VSCO, pattern))):
                num = int(re.search(r'_(\d+)(?:_rr\d+)?\.wav$', p).group(1))
                self.zones[first + num] = p
            self.keys = np.array(sorted(self.zones))

        def play(self, n, vel=100, dur=1.0, release=0.16, bend=None):
            n = self._place(n)
            k = int(self.keys[np.argmin(np.abs(self.keys - n))])
            a = _load(self.zones[k])[:, int(0.04 * SR):]       # skip the pre-roll
            r = 2 ** ((n - k) / 12)
            need = int((dur + release) * SR)
            if bend is None:
                idx = np.arange(need) * r
            else:
                idx = np.cumsum(r * 2 ** (bend[:need] / 12))
            idx = idx[idx < a.shape[1] - 1]
            out = np.vstack([np.interp(idx, np.arange(a.shape[1]), a[c]) for c in range(2)])
            out *= (vel / 127) ** 1.3
            return _fade_out(out, dur, release)

    O = Organ(G)
    notes = compose()
    man = M._voice(Pipes('Keys/Organ/Loud/Rode_Man3Open_*.wav', 35), 'Keys/Organ/Loud manual', 'auto')
    ped = M._voice(Pipes('Keys/Organ/Loud/Rode_Pedal_*.wav', 35), 'Keys/Organ/Loud pedal', 'auto')
    qman = M._voice(Pipes('Keys/Organ/Quiet/NT5_Man3Quiet_*.wav', -86), 'Keys/Organ/Quiet manual', 'auto')
    qped = M._voice(Pipes('Keys/Organ/Quiet/NT5_PedalQuiet_*.wav', -28), 'Keys/Organ/Quiet pedal', 'auto')
    blower = M.hits('Keys/Organ/Rode_Blower.wav')
    wood = M.hits('VSCO 1 Percussion/varWood/wood_click*.wav')
    ctap = M.hits('Percussion/Conga-Tap1*.wav')
    timp = M.hits('Percussion/Timpani/Timpani1_Hit*.wav')
    troll = M.hits('Percussion/Timpani/Rolls/*.wav')
    bd = M.hits('Percussion/BDrumNewhit_v[5-7]*.wav')
    slap = M.hits('VSCO 1 Percussion/varWood/slapstick[0-9].wav')
    crash = M.hits('Percussion/cymbal-crash1_mf*.wav')
    clonk = M.hits('Miscellania Raw/Misc 1/metal_hit[2-5].wav')

    for name, gain, rev in (('organ', 0.25, 0.42), ('pedal', 0.36, 0.32), ('quiet', 0.12, 0.5),
                            ('cipher', 0.25, 0.35), ('drums', 0.42, 0.25), ('fx', 0.5, 0.22),
                            ('blower', 2.0, 0.15), ('perc', 0.5, 0.18)):
        M.bus(name, gain=gain, reverb=rev)

    # ---- the blower spins up; the candles; the knuckles ----
    bl = blower.play(127)[:, :int(14 * SR)].copy()
    tb = np.arange(bl.shape[1]) / SR
    bl *= np.clip(tb / 0.6, 0, 1) * (0.35 + 0.65 * np.clip((tb - 2.5) / -2.0 + 1, 0, 1)) * np.clip((14 - tb) / 6, 0, 1)
    M.add('blower', bl, BLOWER)
    for i, tc in enumerate(CANDLES):
        M.add('fx', whoosh(0.35, 1800, 5200, 0.3, seed=11 + i), tc - 0.08, 0.35, -0.12 if i == 0 else 0.1)
    for i, tk in enumerate(KNUCKLES):
        M.add('perc', wood.play(110, pitch=6 + 3 * i), tk, 0.9, 0.0)
        M.add('perc', wood.play(80, pitch=11 + 3 * i), tk + 0.035, 0.6, 0.0)

    # ---- the organ: the same notes that light the pipes, each panned to its pipe ----
    cip = None
    for t, d, m, v, part in notes:
        pan = float(O.pan[m - LO])
        if part == 'rh' or part == 'lh':
            M.add('organ', man.play(m, v, d), t - 0.04, 1.0, pan)
        elif part == 'ped':
            M.add('pedal', ped.play(m, v, d, release=0.22), t - 0.04, 1.0, pan)
            if v >= 120 and d >= 2 * BEAT:          # the big ones get the 16-foot an octave under
                M.add('pedal', ped.play(m - 12 if m - 12 >= 24 else m, v, d, release=0.25), t - 0.04, 0.5, pan)
        elif part == 'qm':
            M.add('quiet', qman.play(m, v, d, release=0.3), t - 0.04, 1.0, pan)
        elif part == 'qp':
            M.add('quiet', qped.play(m, v, d, release=0.3), t - 0.04, 1.0, pan)
        elif part == 'cipher':
            cip = (t, d, m, v, pan)

    # ---- the stuck pipe: hiccups on the taps, rises after the thump, pops ----
    t, d, m, v, pan = cip
    n = int((d + 0.05) * SR)
    ta = t + np.arange(n) / SR
    p = np.clip((ta - THUMP) / (TPOP - THUMP), 0, 1)
    bend = np.where(ta >= THUMP, 0.6 + 3.4 * p ** 1.6, 0.0)
    bend += (0.08 + 0.45 * p) * np.sin(2 * np.pi * (5 + 4 * p) * ta) * (ta >= THUMP)
    for tk in TAPS:
        bend -= 0.7 * np.exp(-((ta - tk - 0.06) / 0.05) ** 2)
    sig = man.play(m, v, d, release=0.012, bend=bend)
    ts = t + np.arange(sig.shape[1]) / SR
    g = np.where(ts < TREL, 1.0, 1.0 - 0.4 * np.clip((ts - TREL) / 0.4, 0, 1) + 0.5 * np.clip((ts - THUMP) / 2.3, 0, 1))
    for tk in TAPS:
        g *= 1 - 0.8 * np.exp(-((ts - tk - 0.06) / 0.05) ** 2)
    M.add('cipher', sig * g, t - 0.04, 1.0, pan)

    # ---- drums with the big chords ----
    M.add('drums', troll.play(70, dur=1.3), T0 - 1.3, 0.6, -0.1)
    for tk in (T0, T0 + 4.5 * BEAT, T0 + 9 * BEAT, T0 + 11 * BEAT):
        M.add('drums', timp.play(118, pitch=-2), tk, 0.8, -0.2)
    for bar in range(3):
        M.add('drums', timp.play(112, pitch=-2), TD + bar * 4 * BEAT, 0.7, -0.2)
    for i in range(8):
        M.add('drums', timp.play(80 + 5 * i, pitch=-2), TD + 12 * BEAT + i * BEAT / 2, 0.45 + 0.04 * i, -0.2)
    M.add('drums', timp.play(120, pitch=-2), TF, 0.8, -0.2)
    M.add('drums', troll.play(70, dur=3.4), TFIN + 0.1, 0.55, -0.1)
    for tk in (TFIN,):
        M.add('drums', timp.play(127, pitch=-2), tk, 0.9, -0.2)
        M.add('drums', bd.play(120), tk, 0.8)
        M.add('drums', crash.play(110), tk, 0.45, 0.3)

    # ---- the taps, the thump, the pop, the cork, the clonk ----
    kpan = O.pan_x(float(O.key_x(HI)))
    for tk in TAPS:
        M.add('perc', ctap.play(95), tk, 0.9, kpan)
    M.add('drums', bd.play(124), THUMP, 1.0, 0.0)
    M.add('perc', slap.play(120), THUMP, 0.8, 0.0)

    k = int(0.09 * SR)
    tp = np.arange(k) / SR
    rngp = np.random.default_rng(5)
    fpop = 1400 * (220 / 1400) ** np.clip(tp / 0.03, 0, 1)
    pop = np.sin(2 * np.pi * np.cumsum(fpop) / SR) * np.exp(-tp / 0.018)
    pop += 0.8 * rngp.normal(0, 1, k) * np.exp(-tp / 0.004)
    pop *= 0.8 / np.abs(pop).max()
    M.add('fx', np.vstack([pop, pop]), TPOP, 1.2, float(O.pan[TOP]))

    wh = slide(0.0, FLY, 1900, 380, FLY + 0.12, amp=0.32, shape=0.55)[0]
    tw = TPOP + np.arange(len(wh)) / SR
    order = G.path
    u = np.clip((tw - TPOP) / FLY, 0, 1)
    dh = G.length * (1 - u ** 0.85)
    xw = np.interp(dh, G.pd[order], G.pos[order, 0])
    x0, x1 = G.pos[:, 0].min(), G.pos[:, 0].max()
    pw = 0.85 * (2 * (xw - x0) / (x1 - x0) - 1)
    a = (pw + 1) * np.pi / 4
    far = 1 - 0.5 * u                          # getting farther away as it goes round the back
    M.add('fx', np.vstack([wh * np.cos(a), wh * np.sin(a)]) * np.sqrt(2) * far, TPOP + 0.02, 0.9)
    M.add('perc', clonk.play(70), CLONK, 0.35, -0.85)

    # ---- the candles go out ----
    for i in range(2):
        M.add('fx', whoosh(0.3, 900, 250, 0.25, seed=21 + i), TSNUFF + 0.15 * i - 0.1, 0.35, -0.12 if i == 0 else 0.1)
