"""Gourd Quartet: two vines creep in from the free ends of the roofline, lunge by lunge, and meet in
the porch notch. Five pumpkins swell on them in three puffs each: a big Bass on Left, a Baritone on
Porch Left, the Lead in the middle of Porch Front, a Tenor on Porch Right and a runt on Right, off on
its own. A knife carves each face in four stabs (the runt's slips, and its candle takes two goes),
the candle lights, and each says hello in its own voice and flicker. The Lead blows a pitch pipe
and the four sing a barbershop number at 96 BPM: the Lead calls, the trio answers, the runt answers
half a beat late and sour, and the others' eyes swivel round to glare at it. In the close-harmony
chorus it drags, then rushes, then reaches for a high note and cracks.

A rumble at the far back of Side: a giant pumpkin rolls out of the dark toward the street, faster
and faster, and flattens the quartet one by one (each goes wide-eyed, gets squeezed against it and
bursts into pulp and seeds). The runt blows out its own candle and the giant rolls right over it
and off the end of the house. Silence. The runt relights, looks left, looks right and sings the tag
alone, in tune at last; on its long last note the seeds of each squashed pumpkin glow in that
pumpkin's candle colour and hum their old part of the chord with it. Then the runt winks.

Everything is drawn in path distance with exact pixel coverage, so faces keep their size on every
run. A pumpkin is a rind span with three holes (two eyes and a mouth) that open as it sings; its
eyes slide inside the face to look along the roof. The giant's features and ribs turn as it rolls."""
import numpy as np
from pixelhome.fx import DT, hexc, light, perc, smoothstep, keys, lerp, Flicker, nframes

CODE = 'HW08'
TITLE = 'Gourd Quartet'
KIND = 'show'
DESCRIPTION = ('Pumpkins grow on vines along the roof, get carved, and sing a barbershop number, '
               'except the runt, who can\'t keep up. Then a giant pumpkin rolls in and flattens '
               'the quartet, and the runt gets the last note.')

BEAT = 0.625                                 # 96 BPM
D = 82.0
NAMES = ['Bass', 'Baritone', 'Lead', 'Tenor', 'Runt']
SEGS = ['Left', 'Porch Left', 'Porch Front', 'Porch Right', 'Right']
WIDTH = [150.0, 112.0, 128.0, 112.0, 54.0]
BASS, BARI, LEAD, TENOR, RUNT = range(5)

VINE_A = (0.625, 7.5, 6)                     # start, duration, lunges: from the back of Side to the notch
VINE_B = (4.375, 5.0, 4)                     # from the free end of Right
SWELL = [10.0, 11.25, 12.5, 13.75, 15.0]
PUFFS = [0.0, BEAT / 2, BEAT]
CARVE = [16.25, 17.5, 18.75, 20.0, 21.25]
STABS = [0.0, BEAT / 4, BEAT / 2, 3 * BEAT / 4]
RUNT_SLIP = 21.25 + 0.55                     # a fifth stab that slips and widens its right eye
FIZZLE = 21.25 + 1.5 * BEAT                  # the runt's first match goes out
LIT = [c + 1.5 * BEAT for c in CARVE[:4]] + [22.65]
PIPE, HUM, TS = 23.75, 24.375, 25.0          # pitch pipe, hum, song
TCRACK = TS + 31 * BEAT                      # the runt cracks
TCUT = TS + 31.25 * BEAT                     # everyone stops
HARRUMPH = 45.3
RUMBLE = 46.25
GT = [47.5, 50.0, 51.875, 53.75, 55.0, 56.25, 57.5]    # giant keyframes: enter, four squashes, the runt, off
RG = 165.0                                   # giant radius
HIDE = 55.45                                 # the runt blows its candle out
CRASH = 58.4
STRIKE1, STRIKE2 = 61.0, 61.6
TAG = [(64.0, 0.9, 'F4'), (65.0, 0.55, 'A4'), (65.6, 0.55, 'G4'), (66.2, 0.55, 'F4'), (66.8, 0.75, 'D4'),
       (67.6, 1.0, 'C4'), (68.75, 6.25, 'F4')]
SEED_T = [71.25, 70.625, 70.0, 69.375]       # each pumpkin's seeds join the last note (nearest the runt first)
SEED_NOTE = ['F2', 'A3', 'C4', 'D4']
WINK = 78.5
BUTTON = 79.2

RIND = hexc('#ff5c00')
UNRIPE = hexc('#4f9a12')
VINE = hexc('#2c8a18')
TIP = hexc('#b8ff40')
CANDLE = [hexc('#ff8414'), hexc('#ffa830'), hexc('#ffcc40'), hexc('#ffe878'), hexc('#d4ff50')]
ANGRY = hexc('#ff2a08')
GIANT_RIND = hexc('#d03000')
GIANT_GLOW = hexc('#ffa018')
PULP = hexc('#ff6a08')
SEED = hexc('#fff0c8')
FLOOR = hexc('#2a1450')
WHITE = hexc('#ffffff')
SPARK = hexc('#ffe08a')

# ---- the song: (song beat, beats, notes) ----
CALL = [(0, 1, 'F4'), (1, .5, 'A4'), (1.5, .5, 'G4'), (2, .5, 'F4'), (2.5, .5, 'D4'), (3, 1, 'C4'),
        (8, 1, 'G4'), (9, .5, 'Bb4'), (9.5, .5, 'A4'), (10, .5, 'G4'), (10.5, .5, 'E4'), (11, 1, 'C4')]
ANSWER = [(4, 1.5, ('D3', 'C4', 'F#4')), (5.5, 2.5, ('G2', 'B3', 'F4')),          # (bass, bari, tenor)
          (12, 1.5, ('C3', 'Bb3', 'E4')), (13.5, 2.5, ('F2', 'C4', 'A4'))]
RUNT_A = [(4.5, 1.0, 66.45), (6.0, 1.5, 65.5), (12.5, 1.0, 63.6), (14.0, 1.5, 69.4)]   # late, and sour
CHORUS = [(16, 2, ('F2', 'C4', 'A4', 'C5')), (18, 1, ('D3', 'C4', 'A4', 'C5')), (19, 1, ('D3', 'C4', 'F#4', 'C5')),
          (20, 2, ('G2', 'F3', 'G4', 'B4')), (22, 1, ('C3', 'Bb3', 'E4', 'C5')), (23, 1, ('C3', 'Bb3', 'G4', 'Bb4')),
          (24, 2, ('F2', 'C4', 'F4', 'A4')), (26, 1, ('Bb2', 'Bb3', 'D4', 'F4')), (27, 1, ('Bb2', 'Db4', 'F4', 'G4')),
          (28, 3.25, ('F2', 'A3', 'A4', 'D5'))]
RUNT_LAG = [0.5, 0.5, 0.5, 0.25, 0.25, -0.25, -0.5, -0.5, None, 0.0]   # it drags, catches up, rushes, skips one
RUNT_SOUR = [0.0, 0.35, -0.4, 0.0, 0.3, 0.0, 0.45, -0.3, 0.0, -0.35]
HELLO = ['F2', 'C4', 'F4', 'A4', 68.0]
CRY = ['A2', 'E4', 'A4', 'C5']               # each one's last "oh!"


def _n(x):
    if isinstance(x, str):
        from pixelhome.audio import note
        return note(x)
    return x


def sb(b):
    return TS + b * BEAT


def _vine(t, v, total):
    t0, dur, k = v
    u = np.clip((t - t0) / dur, 0, 1)
    return total * (u - np.sin(2 * np.pi * k * u) / (2 * np.pi * k))


def lunges(v):
    t0, dur, k = v
    return [t0 + dur * (j + 0.5) / k for j in range(k)]


def _ease(u):
    u = np.clip(u, 0, 1)
    return 0.5 * u + 0.5 * u * u * (3 - 2 * u)


def _back(u, c1=1.6):
    u = np.clip(u, 0, 1)
    return 1 + (c1 + 1) * (u - 1) ** 3 + c1 * (u - 1) ** 2


class Plan:
    """Everything render() and score() share: where the pumpkins are, when things happen."""

    def __init__(self, G):
        L = self.L = float(G.length)
        r0, r1 = G.pd[G.seg['Right']].min(), G.pd[G.seg['Right']].max()
        self.c = [float(G.pd[G.seg[s]].mean()) for s in SEGS[:4]] + [float(r0 + 0.55 * (r1 - r0))]
        self.meet = self.c[LEAD]
        self.totA, self.totB = self.meet, L - self.meet
        self.gx = [-RG] + [self.c[i] + 0.25 * WIDTH[i] / 2 - RG for i in range(4)] + \
                  [self.c[RUNT] - RG, L + RG + 40]
        self.burst = GT[1:5]
        tt = np.arange(GT[0], GT[-1], 0.002)
        xg = np.array([self.giant(t) for t in tt])
        self.contact = [float(tt[np.argmax(xg + RG >= self.c[i] - WIDTH[i] / 2)]) for i in range(5)]
        self.over = float(tt[np.argmax(xg >= self.c[RUNT])])        # the giant's middle crosses the runt
        self.gone = float(tt[np.argmax(xg - RG > L)])
        tv = np.arange(0, 12, 0.002)
        a, b = _vine(tv, VINE_A, self.totA), L - _vine(tv, VINE_B, self.totB)
        self.bud = [float(tv[np.argmax(a >= self.c[i])]) for i in (BASS, BARI)] + [VINE_B[0] + VINE_B[1]] + \
                   [float(tv[np.argmax(b <= self.c[i])]) for i in (TENOR, RUNT)]
        self.voice = self._voices()

    def giant(self, t):
        if t <= GT[0]:
            return self.gx[0]
        if t >= GT[-1]:
            v = (self.gx[-1] - self.gx[-2]) / (GT[-1] - GT[-2])
            return self.gx[-1] + v * (t - GT[-1])
        i = int(np.searchsorted(GT, t, side='right')) - 1
        u = (t - GT[i]) / (GT[i + 1] - GT[i])
        if i == 0:                           # rolls out of the dark, picking up speed down Side
            u = u * u * (1.4 - 0.4 * u)
        else:
            u = _ease(u)
        return lerp(self.gx[i], self.gx[i + 1], u)

    def _voices(self):
        """Sung notes per pumpkin: (t, seconds, midi, velocity). They open its mouth and play its voice."""
        V = [[] for _ in range(5)]
        for i in range(5):
            V[i].append((LIT[i] + 0.05, 0.45, _n(HELLO[i]), 96))
        V[LEAD].append((PIPE + 0.05, 0.2, 65, 40))          # puckers for the pitch pipe
        for i, m in enumerate(('F2', 'A3', 'F4', 'C5')):
            V[i].append((HUM, BEAT * 0.9, _n(m), 60))
        V[RUNT].append((HUM + 0.1, BEAT * 0.7, 66.0, 60))
        for b, d, m in CALL:
            V[LEAD].append((sb(b), d * BEAT * 0.95, _n(m), 104))
        for b, d, ms in ANSWER:
            for i, m in zip((BASS, BARI, TENOR), ms):
                V[i].append((sb(b), d * BEAT * 0.95, _n(m), 100))
        for b, d, m in RUNT_A:
            V[RUNT].append((sb(b), d * BEAT * 0.8, m, 92))
        for k, (b, d, ms) in enumerate(CHORUS):
            for i, m in enumerate(ms):
                V[i].append((sb(b), d * BEAT * 0.95, _n(m), 104 if k < 9 else 112))
            if RUNT_LAG[k] is not None:
                rd = d * BEAT * (0.75 if k < 9 else 0.45)
                V[RUNT].append((sb(b + RUNT_LAG[k]), rd, _n(ms[2]) + RUNT_SOUR[k], 96))
        V[RUNT].append((sb(29.5), 1.5 * BEAT, 72.0, 104))   # reaching up for it
        V[RUNT].append((TCRACK, 0.16, 78.6, 120))            # crack
        V[BASS].append((HARRUMPH, 0.22, _n('C2'), 100))
        for i in range(4):
            V[i].append((self.contact[i] - 0.05, 0.4, _n(CRY[i]), 116))
        for t, d, m in TAG:
            V[RUNT].append((t, d, _n(m), 96))
        return V


def render(G, seed=8):
    rng = np.random.default_rng(seed)
    P = Plan(G)
    L, C = P.L, P.c
    pdp = G.pd[G.path]
    w = np.gradient(pdp)
    e0, e1 = pdp - w / 2, pdp + w / 2
    N = G.N

    def cov(a, b):
        """Exact coverage of [a, b] over each pixel (a, b scalars or (K,1) arrays)."""
        return np.clip(np.minimum(b, e1) - np.maximum(a, e0), 0, None) / w

    F = nframes(D)
    T = np.arange(F) * DT

    # mouths: how open each pumpkin's mouth is, frame by frame, from the same notes the score sings
    mouth = np.zeros((5, F))
    accent = np.zeros((5, F))
    onsets = []
    for i in range(5):
        for t0, d, m, v in P.voice[i]:
            env = smoothstep(t0 - 0.03, t0 + 0.06, T) * (1 - smoothstep(t0 + d - 0.05, t0 + d + 0.12, T))
            mouth[i] = np.maximum(mouth[i], env * (0.55 + 0.45 * v / 127))
            accent[i] += np.where(T >= t0, np.exp(-np.clip(T - t0, 0, None) / 0.12), 0)
            if TS <= t0 < TCUT + 0.1 or t0 >= TAG[0][0]:
                onsets.append((t0, C[i], 0.18 if i < 4 else 0.12))
    mouth = np.clip(mouth, 0, 1)
    accent = np.clip(accent, 0, 1)

    flick = [Flicker(rng, 1, 0.4, 1.2), Flicker(rng, 1, 1.0, 3.0), Flicker(rng, 1, 2.0, 4.0),
             Flicker(rng, 1, 4.0, 8.0), Flicker(rng, 1, 2.0, 6.0)]
    fdepth = [0.06, 0.10, 0.04, 0.12, 0.14]
    fear = Flicker(rng, 1, 8.0, 13.0)
    gutter = np.sort(rng.uniform(26, 44, 7))
    giant_fl = Flicker(rng, 1, 1.5, 5.0)

    # vine leaves pop at each lunge, just behind the tip
    leaves = []
    for v, tot, sgn in ((VINE_A, P.totA, 1), (VINE_B, P.totB, -1)):
        for tl in lunges(v):
            d = float(_vine(tl, v, tot)) - 18
            pos = d if sgn > 0 else L - d
            leaves.append((tl, pos, rng.uniform(10, 16)))

    # pulp and seeds from each burst
    parts = []                               # (t burst, x0, v, width, kind, owner)
    for i in range(4):
        x0 = C[i]
        for k in range(22):
            kind = 'seed' if k < 9 else 'pulp'
            sgn = 1 if rng.random() < 0.62 else -1
            v = sgn * rng.uniform(120, 720)
            wd = rng.uniform(3.5, 5) if kind == 'seed' else rng.uniform(5, 15)
            parts.append((P.burst[i], x0 + rng.uniform(-WIDTH[i] / 3, WIDTH[i] / 3), v, wd, kind, i))
    ptb = np.array([p[0] for p in parts])[:, None]
    px0 = np.array([p[1] for p in parts])[:, None]
    pv = np.array([p[2] for p in parts])[:, None]
    pwd = np.array([p[3] for p in parts])[:, None]
    pseed = np.array([p[4] == 'seed' for p in parts])
    pown = np.array([p[5] for p in parts])
    pph = rng.uniform(0, 2 * np.pi, len(parts))
    TAU = 0.3
    from pixelhome.fx import smooth_noise
    vtex = 0.7 + 0.3 * smooth_noise(rng, pdp, 40.0)       # the vine is lumpy, not a stripe

    def size(i, t):
        if t < P.bud[i]:
            return 0.0
        s = 0.1 * smoothstep(P.bud[i], P.bud[i] + 0.4, t)
        tg = [0.35, 0.6, 1.3] if i == RUNT else [0.4, 0.7, 1.0]
        prev = 0.1
        for k, dt in enumerate(PUFFS):
            tp = SWELL[i] + dt
            if t >= tp:
                s = lerp(prev, tg[k], _back((t - tp) / 0.25))
                prev = tg[k]
        if i == RUNT and t >= SWELL[i] + 1.0:   # pfft: it can't hold it
            s = lerp(1.3, 0.92, smoothstep(SWELL[i] + 1.0, SWELL[i] + 1.4, t))
        return s

    def gaze(i, t):
        g = 0.0
        windows = [(sb(6.5), sb(7.75)), (sb(14.5), sb(16.0)), (TCUT, RUMBLE)]
        for a, b in windows:
            if a - 0.15 <= t < b + 0.3:
                amt = smoothstep(a - 0.15, a + 0.05, t) * (1 - smoothstep(b, b + 0.3, t))
                g = (-1.0 if i == RUNT else 1.0) * amt          # they glare at the runt; it looks at them
        if t >= RUMBLE and t < GT[-1] + 1:
            g = -smoothstep(RUMBLE, RUMBLE + 0.3, t)          # everyone looks to the back of Side
        if i == RUNT and t >= STRIKE2:
            g = keys(t, [(61.9, 0.0), (62.1, -1.0), (62.5, -1.0), (62.7, 1.0), (63.1, 1.0), (63.4, 0.0)])
        return float(g)

    def angry(i, t):
        if i == RUNT:
            return 0.0
        a = 0.0
        for a0, b0 in ((sb(6.5), sb(7.75)), (sb(14.5), sb(16.0)), (TCUT, RUMBLE)):
            a = max(a, smoothstep(a0, a0 + 0.2, t) * (1 - smoothstep(b0, b0 + 0.3, t)))
        return a

    def pumpkin(i, t):
        """-> (pwm (N,3), coverage (N,)) or None."""
        if i < 4 and t >= P.burst[i]:
            return None
        s = size(i, t)
        if s <= 0:
            return None
        hw = WIDTH[i] / 2 * s
        c = C[i]
        m = float(mouth[i, min(F - 1, int(round(t / DT)))])
        ac = float(accent[i, min(F - 1, int(round(t / DT)))])
        if TS <= t < TCUT and m > 0.05:      # a bob on the beat while singing
            c += (3.5 if i == BASS else 2.0) * np.sin(np.pi * (t - TS) / BEAT) * m
        if RUMBLE <= t < GT[0] + 0.5:        # the ground shakes
            c += 1.8 * np.sin(2 * np.pi * 11 * t + i) * smoothstep(RUMBLE, RUMBLE + 1, t)
        es = 1.0
        terror = 0.0
        if i < 4:
            terror = smoothstep(P.contact[i] - 1.4, P.contact[i] - 0.6, t)
        elif HIDE - 0.5 <= t < HIDE:
            terror = smoothstep(HIDE - 0.5, HIDE - 0.3, t)
        if terror > 0:
            m = max(m, terror)
            es = 1 + 0.35 * terror
            c += 9 * terror
        # squeezed against the giant
        left, right = c - hw, c + hw
        if i < 4 and t >= P.contact[i]:
            front = P.giant(t) + RG
            push = max(0.0, front - left)
            left = max(left, front)
            right = right + 0.35 * push
        c, hw = (left + right) / 2, (right - left) / 2
        if hw < 1:
            return None
        col = lerp(UNRIPE, RIND, smoothstep(SWELL[i], SWELL[i] + 0.9, t))
        rI = 0.55 * (0.6 + 0.4 * smoothstep(SWELL[i], SWELL[i] + 0.6, t))
        rI *= 1 - 0.45 * smoothstep(LIT[i], LIT[i] + 0.3, t)
        tc = CARVE[i]
        g = gaze(i, t)
        # holes in face units: (centre, half width, opened)
        eyew = 0.11 * es
        holes = []
        cut = [t >= tc + STABS[k] for k in range(4)]
        if cut[0]:
            holes.append((-0.58 + 0.13 * g, eyew))
        if cut[1]:
            rw = eyew * (1.5 if (i == RUNT and t >= RUNT_SLIP) else 1.0)
            if i == RUNT and WINK <= t < WINK + 0.32:
                rw *= 0.15
            holes.append((0.58 + 0.13 * g, rw))
        if cut[2]:
            mw = (0.07 if not cut[3] else 0.13) + 0.2 * m
            holes.append((0.04 * g, mw))
        inside = cov(c - hw, c + hw)
        hole = np.zeros(N)
        for hc, hh in holes:
            hole += cov(c + (hc - hh) * hw, c + (hc + hh) * hw)
        hole = np.minimum(hole, inside)
        u = (pdp - c) / hw
        rib = 0.82 + 0.18 * np.cos(np.pi * u * (3 if WIDTH[i] > 60 else 2)) ** 2
        # candle
        cI = 0.0
        if i == RUNT:
            if FIZZLE <= t < FIZZLE + 0.35:
                cI = 0.7 * np.exp(-(t - FIZZLE) / 0.08)
            if t >= LIT[i]:
                cI = 0.8 * smoothstep(LIT[i], LIT[i] + 0.25, t)
            if t >= HIDE:                    # blown out, playing dead
                cI *= 1 - smoothstep(HIDE, HIDE + 0.12, t)
            if t >= STRIKE2:
                cI = 0.8 * smoothstep(STRIKE2, STRIKE2 + 0.3, t)
            for tg_ in gutter:
                cI *= 1 - 0.45 * np.exp(-((t - tg_) / 0.12) ** 2)
            if t >= HIDE and t < STRIKE2:
                rI *= 1 - 0.75 * smoothstep(HIDE, HIDE + 0.3, t)
            if t >= STRIKE2:
                rI = 0.3 * (0.25 + 0.75 * smoothstep(STRIKE2, STRIKE2 + 0.3, t))
            fade = 1 - smoothstep(79.6, 81.6, t)
            cI *= fade
            rI *= fade
        elif t >= LIT[i]:
            cI = 0.8 * smoothstep(LIT[i], LIT[i] + 0.25, t)
        if cI > 0:
            cI *= 1 + fdepth[i] * float(flick[i](t)[0])
            cI *= 0.85 + 0.25 * m + 0.1 * ac
            if terror:
                cI *= 1 + 0.25 * terror * float(fear(t)[0])
        ccol = lerp(CANDLE[i], ANGRY, 0.45 * angry(i, t))
        rI = rI * (1 + 0.12 * ac)
        pwm = (perc(rI * rib) * (inside - hole))[:, None] * col + (perc(min(cI, 1.0)) * hole)[:, None] * ccol
        return pwm, inside

    def giant(t):
        x = P.giant(t)
        if x < -RG - 5 or x - RG > L + 5:
            return None
        th = (x - P.gx[0]) / RG
        inside = cov(x - RG, x + RG)
        dark = np.zeros(N)
        glow = np.zeros(N)

        def feat(a, h):
            ca = (th + a + np.pi) % (2 * np.pi) - np.pi
            lo_c, hi_c = max(ca - h, -np.pi / 2), min(ca + h, np.pi / 2)
            if hi_c <= lo_c:
                return np.zeros(N)
            return cov(x + RG * np.sin(lo_c), x + RG * np.sin(hi_c))

        for k in range(8):                   # ribs
            dark += feat(k * np.pi / 4, 0.045)
        for a, h in ((-0.78, 0.13), (0.78, 0.13)):     # eyes
            glow += feat(a, h)
        glow += feat(0.0, 0.42)              # grin
        for a in (-0.2, 0.08, 0.3):          # teeth
            glow -= feat(a, 0.045)
        glow = np.clip(glow, 0, 1) * inside
        dark = np.clip(dark, 0, 1) * inside * (1 - glow)
        bump = 0.25 * np.exp(-((t - P.over) / 0.08) ** 2)
        rI = 0.7 * (1 + bump)
        gI = 0.92 * (1 + 0.08 * float(giant_fl(t)[0])) * (1 + bump)
        pwm = (perc(rI) * (inside - glow - 0.7 * dark))[:, None] * GIANT_RIND + (perc(min(gI, 1)) * glow)[:, None] * GIANT_GLOW
        return pwm, inside

    out = np.zeros((F, N, 3))
    lv_t = np.array([l[0] for l in leaves])[:, None]
    lv_x = np.array([l[1] for l in leaves])[:, None]
    lv_w = np.array([l[2] for l in leaves])[:, None]
    on_t = np.array([o[0] for o in onsets])
    on_c = np.array([o[1] for o in onsets])
    on_a = np.array([o[2] for o in onsets])
    for fi in range(F):
        t = fi * DT
        master = smoothstep(0, 1.5, t) * (1 - smoothstep(80.5, 81.9, t))
        base = light(FLOOR, np.full(N, 0.13 * master))
        # ---- vines ----
        a = float(_vine(t, VINE_A, P.totA))
        b = L - float(_vine(t, VINE_B, P.totB))
        vI = 0.15 * (1 - 0.35 * smoothstep(22, 25, t)) * (1 - smoothstep(76, 80, t)) * vtex
        trampled = 1.0
        xg = P.giant(t)
        if t >= GT[0]:
            trampled = np.where(pdp < xg - RG * 0.6, 0.35, 1.0)
        vcov = cov(-1, a) + cov(b, L + 1)
        vint = vI * trampled * np.ones(N)
        if len(on_t):                        # every sung onset sends a pulse out along the vine
            sel = (on_t <= t) & (on_t > t - 0.9)
            for t0, c0, amp in zip(on_t[sel], on_c[sel], on_a[sel]):
                r = 520 * (t - t0)
                vint = vint + amp * np.exp(-((np.abs(pdp - c0) - r) / 35) ** 2) * np.exp(-(t - t0) / 0.45)
        vint = np.clip(vint, 0, 1)
        base += (perc(vint) * np.clip(vcov, 0, 1))[:, None] * VINE
        if t < VINE_B[0] + VINE_B[1] + 0.8:  # bright growing tips
            tipI = 0.7 * (1 - smoothstep(VINE_A[0] + VINE_A[1], VINE_A[0] + VINE_A[1] + 0.8, t))
            if t > VINE_A[0]:
                base += light(TIP, tipI * np.exp(-((pdp - a) / 14) ** 2) * (pdp <= a + 6))
            tipI = 0.7 * (1 - smoothstep(VINE_B[0] + VINE_B[1], VINE_B[0] + VINE_B[1] + 0.8, t))
            if t > VINE_B[0]:
                base += light(TIP, tipI * np.exp(-((pdp - b) / 14) ** 2) * (pdp >= b - 6))
        meet = VINE_B[0] + VINE_B[1]
        if meet <= t < meet + 1.2:           # the vines knot together in the notch
            base += light(TIP, 0.6 * np.exp(-(t - meet) / 0.35) * np.exp(-((pdp - P.meet) / 40) ** 2))
        sl = lv_t[:, 0] <= t
        if sl.any():
            g = _back((t - lv_t[sl]) / 0.3)
            lw = lv_w[sl] * g
            lc = cov(lv_x[sl] - lw / 2, lv_x[sl] + lw / 2)
            lI = 0.42 * (1 - 0.4 * smoothstep(22, 25, t)) * (1 - smoothstep(76, 80, t))
            lt = trampled if np.ndim(trampled) else np.ones(N)
            base += (perc(lI) * np.clip(lc.sum(0), 0, 1) * lt)[:, None] * TIP * 0.55
        if RUMBLE <= t < GT[0] + 0.6:        # something red in the dark at the back of Side
            base += light(ANGRY, 0.4 * smoothstep(RUMBLE, GT[0], t) * np.exp(-(pdp / 110) ** 2))
        # ---- pulp and seeds ----
        alive = ptb[:, 0] <= t
        if alive.any():
            tt = t - ptb[alive]
            x = px0[alive] + pv[alive] * TAU * (1 - np.exp(-tt / TAU))
            if t >= CRASH:                   # the crash offstage makes everything jump
                x = x + 4 * np.sin(2 * np.pi * 9 * (t - CRASH) + pph[alive][:, None]) * np.exp(-(t - CRASH) / 0.3)
            pc = cov(x - pwd[alive] / 2, x + pwd[alive] / 2)
            sd = pseed[alive]
            own = pown[alive]
            hot = np.exp(-tt[:, 0] / 0.35)
            pI = np.where(sd, 0.2 + 0.6 * hot, 0.16 + 0.65 * hot)
            pI = pI * (1 - smoothstep(64, 76, t) * (~sd))
            sing = np.zeros(len(own))
            for k in range(4):
                tk = SEED_T[k]
                lit = smoothstep(tk, tk + 0.5, t) * (1 - smoothstep(75.0, 77.0, t))
                breath = 1 + 0.15 * np.sin(2 * np.pi * 0.8 * (t - tk) + pph[alive])
                sing = np.where(own == k, lit * breath, sing)
            pI = np.where(sd, pI * (1 - smoothstep(75.0, 77.5, t)) + 0.62 * sing, pI)
            pw = perc(np.clip(pI, 0, 1))[:, None] * pc
            seedcol = np.array([lerp(SEED, CANDLE[k], min(1.0, 0.8 * s)) for k, s in zip(own, sing)])
            col = np.where(sd[:, None], seedcol, PULP)
            base += pw.T @ col
        # ---- pumpkins, then the giant on top ----
        mid = np.zeros((N, 3))
        mcov = np.zeros(N)
        for i in range(5):
            r = pumpkin(i, t)
            if r is not None:
                mid += r[0]
                mcov = np.maximum(mcov, r[1])
        buf = mid + (1 - mcov)[:, None] * base
        gr = giant(t)
        if gr is not None:
            buf = gr[0] + (1 - gr[1])[:, None] * buf
        # ---- sparks on top: knife glints, matches, bursts ----
        for i in range(5):
            tc = CARVE[i]
            st = [tc + s for s in STABS] + ([RUNT_SLIP] if i == RUNT else [])
            hcs = [-0.58, 0.58, -0.06, 0.06] + ([0.7] if i == RUNT else [])
            for ts_, hc in zip(st, hcs):
                if ts_ - 0.02 <= t < ts_ + 0.12:
                    k = np.exp(-max(t - ts_, 0) / 0.04)
                    xk = C[i] + hc * WIDTH[i] / 2 + 10 * (t - ts_) / 0.12
                    buf += light(WHITE, 0.95 * k * np.exp(-((pdp - xk) / 4) ** 2))
            for tm in ([LIT[i]] if i < 4 else [FIZZLE, LIT[i], STRIKE1, STRIKE2]):
                if tm - 0.05 <= t < tm + 0.25:
                    k = np.exp(-max(t - tm, 0) / 0.07)
                    buf += light(SPARK, 0.85 * k * np.exp(-((pdp - C[i]) / 5) ** 2))
        for i in range(4):
            tb = P.burst[i]
            if tb <= t < tb + 0.6:
                k = np.exp(-(t - tb) / 0.12)
                buf += light(hexc('#ffb040'), 0.9 * k * np.exp(-((pdp - C[i]) / (WIDTH[i] * 0.9)) ** 2))
        out[fi][G.path] = np.clip(buf * (master if t > 80 else 1.0), 0, 1)
    return out


# ---------------------------------------------------------------- music ----------------------------------------------
# A barbershop number for four pumpkins and a runt in F major at the lights' 96 BPM. The pumpkins' voices are the
# same notes that open their mouths: Bass is a tuba, Baritone a horn, Lead Surge's Vocal Lead, Tenor a synth choir,
# the runt an oboe. Under them a pumpkin-patch band of bassoon and pizzicato oom-pah, woodblock, brushes and
# tambourine. The vines creep to pizzicato lunges and guiro creaks, the pumpkins swell in tuba and bassoon puffs,
# the knife is a scrape and a wooden stab, the giant has its own lumbering minor theme, and every squash is a squish,
# a slapstick and a trombone falling off. Everything is panned to where it happens on the house.

def score(M, G):
    from pixelhome.audio import note, slide, whoosh, SR
    n = note
    P = Plan(G)
    L, C = P.L, P.c

    tuba_s = M.sampler('Brass/Tuba/sus/*.wav', tune=-12)
    horn = M.sampler('Brass/F Horn/sus/*.wav', tune=-12)
    oboe = M.sampler('Woodwinds/Oboe/Stacc/*.wav', tune=-12)
    oboe_s = M.sampler('Woodwinds/Oboe/Sus/*.wav', tune=-12)
    bsn = M.sampler('Woodwinds/Bassoon/stac/*.wav', tune=-12)
    bsn_s = M.sampler('Woodwinds/Bassoon/sus/*.wav', tune=-12)
    tuba = M.sampler('Brass/Tuba/stac/*.wav', tune=-12)
    pizz = M.sampler('Strings/Cello Section/pizzT/*.wav', tune=-12)
    vpizz = M.sampler('Strings/Viola Section/pizz/*.wav', tune=-12)
    harp = M.sampler('Strings/Harp/*.wav')
    flute = M.sampler('Woodwinds/Flute/susNV/*.wav', tune=-12)
    trem = M.sampler('Strings/Cello Section/trem/*.wav', tune=-12)
    fall = M.sampler('Brass/OldTrombone/Fall/*.wav', tune=-12)
    wood = M.hits('VSCO 1 Percussion/varWood/wood_click*.wav')
    slap = M.hits('VSCO 1 Percussion/varWood/slapstick[0-9].wav')
    slapq = M.hits('VSCO 1 Percussion/varWood/slapstick_quiet*.wav')
    guiro = M.hits('VSCO 1 Percussion/varWood/guiro_short*.wav')
    guiro_l = M.hits('VSCO 1 Percussion/varWood/guiro_long*.wav')
    taps = M.hits('Percussion/Snare2-taps_v[1-3]*.wav')
    tamb = M.hits('Percussion/Tamb1-Hit*.wav')
    tri = M.hits('Percussion/Triangle3-Hit_v1*.wav')
    clave = M.hits('Percussion/Claves1_Hit_v[12]*.wav')
    ctap = M.hits('Percussion/Conga-Tap1*.wav')
    bd = M.hits('Percussion/BDrumNewhit_v[4-7]*.wav')
    timp = M.hits('Percussion/Timpani/Timpani1_Hit*.wav')
    troll = M.hits('Percussion/Timpani/Rolls/*.wav')
    crash = M.hits('Percussion/cymbal-crash1_f*.wav')
    glass = M.hits('Miscellania Raw/Misc 1/glass_break[3-5].wav')

    for name, gain, rev in (('bass_v', 0.6, 0.15), ('bari_v', 0.3, 0.2), ('lead_v', 1.2, 0.2),
                            ('tenor_v', 0.8, 0.22), ('runt_v', 0.32, 0.2), ('band', 0.4, 0.1),
                            ('pizz', 0.34, 0.14), ('perc', 0.5, 0.12), ('drums', 0.5, 0.16),
                            ('fx', 0.3, 0.2), ('giant', 0.55, 0.15), ('choir', 0.9, 0.45), ('harp', 0.3, 0.35)):
        M.bus(name, gain=gain, reverb=rev)

    order = np.argsort(G.pd)
    xs, ds = G.pos[order, 0], G.pd[order]
    x0, x1 = xs.min(), xs.max()

    def pan_at(d):
        x = np.interp(d, ds, xs)
        return float(0.85 * (2 * (x - x0) / (x1 - x0) - 1))

    pan = [pan_at(c) for c in C]
    VBUS = ['bass_v', 'bari_v', 'lead_v', 'tenor_v', 'runt_v']

    def squish(seed, sec=0.6):
        k = int(sec * SR)
        r = np.random.default_rng(seed)
        x = r.normal(0, 1, k)
        t = np.arange(k) / SR
        fc = 2600 * (110 / 2600) ** np.clip(t / (0.7 * sec), 0, 1)
        a = np.exp(-2 * np.pi * fc / SR)
        y = np.empty(k)
        z = 0.0
        for j in range(k):
            z = (1 - a[j]) * x[j] + a[j] * z
            y[j] = z
        y /= np.abs(y).max() + 1e-9
        glorp = np.exp(-t / 0.2) * (0.5 + 0.5 * np.sin(2 * np.pi * 11 * t) ** 2)
        f = 120 * (38 / 120) ** np.clip(t / 0.25, 0, 1)
        thump = np.sin(2 * np.pi * np.cumsum(f) / SR) * np.exp(-t / 0.11)
        sig = 0.55 * y * glorp + 0.6 * thump
        sig *= np.clip(t / 0.004, 0, 1)
        return np.vstack([sig, sig])

    # ---- voices: the same notes that open the mouths ----
    lead_notes, tenor_notes = [], []
    for i in range(5):
        for t, d, m, v in P.voice[i]:
            if i == BASS:
                M.add('bass_v', tuba_s.play(m, v, dur=d, release=0.15), t, 1.0, pan[i])
            elif i == BARI:
                M.add('bari_v', horn.play(m, v, dur=d, release=0.15), t, 1.0, pan[i])
            elif i == LEAD:
                lead_notes.append((t, int(round(m)), v, d))
            elif i == TENOR:
                tenor_notes.append((t, int(round(m)), v, d))
            else:
                ins = oboe_s if d > 0.5 else oboe
                M.add('runt_v', ins.play(m, v, dur=d, release=0.12), t, 1.0, pan[i])

    # ---- 0-9.4: the vines creep in, lunge by lunge ----
    M.add('fx', whoosh(6.0, 80, 300, 0.4, seed=2), 0.0, 0.35)
    for v, tot, sgn, ins, base in ((VINE_A, P.totA, 1, pizz, 'F2'), (VINE_B, P.totB, -1, vpizz, 'C4')):
        for j, tl in enumerate(lunges(v)):
            d = float(_vine(tl, v, tot))
            pos = d if sgn > 0 else L - d
            p = pan_at(pos)
            steps = [0, 2, 4, 5, 7, 9, 11, 12]
            M.add('pizz', ins.play(n(base) + steps[j], 100), tl, 1.0, p)
            M.add('perc', guiro.play(70), tl - 0.32, 0.45, p)
            M.add('perc', ctap.play(80), tl + 0.05, 0.5, p)
    crawl = ['F2', 'G2', 'Ab2', 'A2', 'C3', 'Bb2', 'A2', 'G2', 'F2', 'E2', 'F2', 'G2', 'A2', 'C3']
    for k, m in enumerate(crawl):           # a tiptoeing bassoon walking under it
        t = 0.625 + k * BEAT
        M.add('band', bsn.play(n(m), 92 if k % 2 == 0 else 78), t, 1.0, -0.1)
        if k % 2:
            M.add('perc', taps.play(60), t, 0.45, 0.2)
    meet = VINE_B[0] + VINE_B[1]
    M.add('perc', tri.play(80), meet, 0.5, pan_at(P.meet))
    for m in ('F3', 'A3', 'C4', 'F4'):
        M.add('pizz', vpizz.play(n(m), 96), meet, 0.7, pan_at(P.meet))
    M.add('band', bsn.play(n('F2'), 100), meet, 1.0)

    # ---- the band: bassoon oom, pizzicato pah, woodblock; one chord per beat pair ----
    TRI = {'F': ('F2', 'C3', ('A3', 'C4', 'F4')), 'Bb': ('Bb1', 'F2', ('Bb3', 'D4', 'F4')),
           'C7': ('C2', 'G2', ('Bb3', 'C4', 'E4')), 'D7': ('D2', 'A2', ('A3', 'C4', 'F#4')),
           'G7': ('G2', 'D2', ('B3', 'D4', 'F4')), 'Bbm': ('Bb1', 'F2', ('Bb3', 'Db4', 'F4'))}

    def band(t0, beats, chords, vel=92, wood_on=True, tambo=False):
        for k in range(beats):
            t = t0 + k * BEAT
            ch = chords[min(len(chords) - 1, k // 2)]
            r, f5, tri_ = TRI[ch]
            if k % 2 == 0:
                M.add('band', bsn.play(n(r if (k // 2) % 2 == 0 else f5), vel), t, 1.0, -0.15)
            else:
                for m in tri_:
                    M.add('pizz', pizz.play(n(m), vel - 14), t, 0.55, 0.25)
                if wood_on:
                    M.add('perc', wood.play(70), t, 0.5, 0.0)
                if tambo:
                    M.add('perc', tamb.play(66), t, 0.45, 0.3)
            if tambo:
                M.add('perc', taps.play(55), t + BEAT / 2, 0.35, -0.2)

    band(10.0, 22, ['F', 'F', 'Bb', 'Bb', 'C7', 'C7', 'F', 'F', 'F', 'F', 'C7'], vel=80)

    # ---- 10-16: the pumpkins swell in three puffs ----
    puffs = {BASS: ('F1', 'A1', 'C2'), BARI: ('C2', 'F2', 'A2'), LEAD: ('F2', 'A2', 'C3'), TENOR: ('A2', 'C3', 'F3')}
    for i in range(4):
        for k, dt in enumerate(PUFFS):
            ins = tuba if i == BASS else bsn
            M.add('band', ins.play(n(puffs[i][k]), 96 + 8 * k), SWELL[i] + dt, 0.9, pan[i])
        M.add('fx', slide(0.0, 0.7, 180 + 40 * i, 330 + 60 * i, 0.75, 0.35), SWELL[i], 0.5, pan[i])
    for k, (m, dt) in enumerate((('C4', 0.0), ('F4', PUFFS[1]), ('A4', PUFFS[2]))):
        M.add('runt_v', oboe.play(n(m), 90), SWELL[RUNT] + dt, 0.8, pan[RUNT])
    M.add('fx', slide(0.0, 0.4, 600, 260, 0.45, 0.5), SWELL[RUNT] + 1.0, 0.6, pan[RUNT])   # pfft

    # ---- 16-23: carving: four stabs, a match, hello ----
    for i in range(5):
        st = [CARVE[i] + s for s in STABS] + ([RUNT_SLIP] if i == RUNT else [])
        for k, ts_ in enumerate(st):
            M.add('fx', whoosh(0.1, 2500, 6000, 0.4, seed=100 + 7 * i + k), ts_ - 0.07, 0.35, pan[i])
            M.add('perc', wood.play(100), ts_, 0.7, pan[i])
        tm = [LIT[i]] if i < 4 else [FIZZLE, LIT[i]]
        for j, t in enumerate(tm):
            M.add('fx', whoosh(0.22, 1500, 400, 0.5, seed=200 + i + j), t - 0.12, 0.5, pan[i])
            if i == RUNT and j == 0:
                M.add('fx', slide(0.0, 0.3, 500, 200, 0.32, 0.4), t, 0.4, pan[i])
            else:
                M.add('perc', tri.play(50), t, 0.25, pan[i])
    M.add('perc', slapq.play(90), RUNT_SLIP, 0.6, pan[RUNT])

    # ---- the pitch pipe, a hum, and the song ----
    M.add('lead_v', flute.play(n('F4'), 80, dur=BEAT * 0.9, release=0.1), PIPE, 0.8, pan[LEAD])
    A = ['F', 'F', 'D7', 'G7', 'C7', 'C7', 'C7', 'F']
    band(TS, 16, A, vel=88)
    Bp = ['F', 'D7', 'G7', 'C7', 'F', 'Bb', 'F', 'F']
    band(TS + 16 * BEAT, 12, Bp, vel=94, tambo=True)
    M.add('drums', troll.play(70, dur=3.25 * BEAT), sb(28), 0.45)
    for m in ('F2', 'C3'):
        M.add('band', bsn_s.play(n(m), 90, dur=3.2 * BEAT, release=0.1), sb(28), 0.8, -0.1)
    # the crack: a squeal off the top
    M.add('fx', slide(0.0, 0.16, 620, 900, 0.3, 0.3, shape=0.4), TCRACK, 0.5, pan[RUNT])
    M.add('perc', slapq.play(70), TCUT + 0.05, 0.4, pan[RUNT])
    M.add('band', bsn.play(n('C2'), 90), HARRUMPH, 0.6, pan[BASS])

    # ---- the giant: a rumble at the back of Side, then its lumbering theme ----
    side_back = pan_at(0)
    M.add('drums', troll.play(55, dur=1.4), RUMBLE, 0.6, side_back)
    M.add('giant', trem.play(n('F2'), 70, dur=1.6, release=0.3), RUMBLE, 0.8, side_back)
    M.add('giant', trem.play(n('Gb2'), 64, dur=1.6, release=0.3), RUMBLE, 0.7, side_back)
    theme = ['F1', 'Ab1', 'C2', 'Db2', 'C2', 'Ab1', 'G1', 'C2']
    k = 0
    t = GT[0]
    while t < GT[-1] - 0.01:
        x = P.giant(t)
        p = pan_at(np.clip(x, 0, L))
        m = n(theme[k % len(theme)])
        M.add('giant', tuba.play(m, 112), t, 1.0, p)
        M.add('giant', bsn.play(m + 12, 96), t, 0.7, p)
        M.add('drums', bd.play(96 if k % 2 == 0 else 74), t, 0.6, p)
        if k % 2:
            M.add('pizz', pizz.play(m + 24, 90), t, 0.5, p)
        k += 1
        t += BEAT
    for j in range(int((GT[-1] - GT[0]) / 0.25)):   # the roll itself: low noise that follows it
        t = GT[0] + j * 0.25
        x = P.giant(t)
        M.add('fx', whoosh(0.35, 60, 180, 0.6, seed=300 + j), t, 0.55, pan_at(np.clip(x, 0, L)))
    for i in range(4):                       # squash
        tb, p = P.burst[i], pan[i]
        M.add('fx', squish(400 + i), tb - 0.02, 1.0, p)
        M.add('perc', slap.play(118), tb, 0.8, p)
        M.add('drums', bd.play(120), tb, 0.9, p)
        M.add('drums', timp.play(110, pitch=-3 - i), tb, 0.6, p)
        M.add('band', fall.play(n(['D2', 'F2', 'A2', 'C3'][i]), 110), tb + 0.05, 0.6, p)
        for s in range(8):                   # seeds pattering down
            ts_ = tb + 0.08 + 0.06 * s + float(M.rng.uniform(0, 0.04))
            M.add('perc', ctap.play(60 - 4 * s), ts_, 0.4, float(np.clip(p + M.rng.uniform(-0.25, 0.25), -1, 1)))
    M.add('runt_v', oboe.play(n('C4'), 60), HIDE - 0.4, 0.6, pan[RUNT])            # eep
    M.add('fx', whoosh(0.3, 900, 300, 0.4, seed=500), HIDE - 0.05, 0.7, pan[RUNT])   # blows it out
    M.add('perc', wood.play(80), P.over, 0.6, pan[RUNT])
    M.add('band', bsn.play(n('F2'), 80), P.over + 0.08, 0.6, pan[RUNT])
    M.add('drums', crash.play(110), CRASH, 0.6, 0.85)
    M.add('drums', bd.play(124), CRASH, 1.0, 0.85)
    M.add('fx', glass.play(90), CRASH + 0.05, 0.25, 0.9)
    M.add('perc', slap.play(110), CRASH, 0.6, 0.85)

    # ---- the runt relights and sings the tag alone; the seeds join in ----
    M.add('fx', whoosh(0.18, 2000, 700, 0.4, seed=600), STRIKE1 - 0.1, 0.5, pan[RUNT])
    M.add('fx', whoosh(0.28, 2400, 500, 0.5, seed=601), STRIKE2 - 0.12, 0.6, pan[RUNT])
    M.add('perc', tri.play(45), STRIKE2 + 0.05, 0.25, pan[RUNT])
    M.add('pizz', vpizz.play(n('C4'), 70), 62.1, 0.6, pan_at(C[LEAD]))
    M.add('pizz', vpizz.play(n('F4'), 70), 62.7, 0.6, 0.85)
    tag_chords = [(64.0, 'F'), (65.0, 'F'), (66.2, 'Bb'), (67.6, 'C7')]
    for t, ch in tag_chords:
        r, f5, tri_ = TRI[ch]
        M.add('band', bsn_s.play(n(r) + 12, 70, dur=1.0, release=0.3), t, 0.6, -0.1)
        for j, m in enumerate(tri_):
            M.add('harp', harp.play(n(m), 70), t + 0.08 * j, 0.8, 0.1)
    for j, m in enumerate(('F2', 'C3', 'F3', 'A3', 'C4', 'F4', 'A4')):     # harp spread under the last note
        M.add('harp', harp.play(n(m), 72), TAG[-1][0] + 0.11 * j, 0.8, 0.0)
    for k in range(4):                       # each pumpkin's seeds hum its part, from where it burst
        hum = [(SEED_T[k], n(SEED_NOTE[k]) + (12 if k == 0 else 0), 80, 75.2 - SEED_T[k])]
        M.add('choir', M.synth('Pads/Ooh').render(hum, D), 0.0, 1.0, pan[k])
        M.add('perc', tri.play(40), SEED_T[k], 0.2, pan[k])
    for t, ch in ((75.6, 'F'),):
        M.add('harp', harp.play(n('F3'), 60), t, 0.6)
    M.add('fx', slide(0.0, 0.1, 500, 700, 0.15, 0.3), WINK, 0.35, pan[RUNT])
    M.add('pizz', pizz.play(n('F3'), 100), BUTTON, 0.8, pan[RUNT])
    M.add('band', bsn.play(n('F2'), 104), BUTTON, 1.0, pan[RUNT])
    M.add('perc', wood.play(100), BUTTON, 0.7, pan[RUNT])

    M.add('lead_v', M.synth('Leads/Vocal Lead').render(lead_notes, D), 0.0, 1.0, pan[LEAD])
    M.add('tenor_v', M.synth('Pads/Synth Choir MW O-Ah').render(tenor_notes, D), 0.0, 1.0, pan[TENOR])
