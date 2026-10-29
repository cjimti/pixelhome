"""The Lair: a blacklit gambling den under the town, run by a big lumpy burlap sack who dances on every
beat. He grows up out of the porch, opens his eyes, and the band strikes up. With a swipe of his arm (a
streak down Porch Left) he sets the roulette wheel on the left wing spinning: violet and lime pockets slide
past, slowing, while a white ball swings through them in shorter and shorter arcs and drops into a
pocket; he laughs till he shakes. He flings two dice down Porch Right onto the right wing: they tumble
and come up six and five, and he jumps for joy. Bugs pour out to dance the whole roof for the chorus.
His second throw comes up snake eyes: he sags, sulks, stomps twice, and spins the wheel again with a
bigger swipe; it comes up his, and he dances it off. Then a loose lime thread shows at his edge. A bug
grabs it and runs for the back of Side, and he unravels as it goes, bugs spilling out of him both ways,
until he is a little empty rag that deflates with a raspberry and flops. One eye opens, he winks, and the
whole den flashes lime.

Characters and props are drawn with exact span-over-pixel coverage in path distance (as in Bone Yard):
the sack is a row of lumps with stitched seams, two eye holes and a mouth that opens when he laughs.
Times are beats on a 120 BPM grid (BEAT, beat 0 at T0) that score() shares."""
import numpy as np
from pixelhome.fx import DT, hexc, light, smoothstep, keys, lerp, nframes

CODE = 'NB08'
TITLE = 'The Lair'
KIND = 'show'
DESCRIPTION = ('A big burlap sack runs a blacklit den: he spins the roulette wheel, throws dice and dances on '
               'every beat, until a bug pulls his loose thread and he unravels with a raspberry.')

BPM = 120
BEAT = 60 / BPM
T0 = 2.0                                    # beat 0

# the story, in beats from T0
RISE = (0, 4)                               # he grows up out of the porch; the band comes in at the end
SPINS = [(20, 32), (68, 78)]                # swipe at the first beat, the ball drops at the second
LAUGH = (32, 36)
THROWS = [37, 61]                           # dice land a beat and 1.4 beats later, settle two beats after that
FACES = [(6, 5), (1, 1)]                    # a big roll, then snake eyes
JOY = (40, 42)
CHORUS = (44, 60)
SULK = (64, 66)
STOMPS = (66, 67)
JUBILEE = (78, 84)
THREAD = 84                                 # a loose thread shows
GRAB = 85                                   # a bug takes it
PULL = (86, 92)                             # and runs it to the back of Side as he unravels
SPILL = (88, 92)                            # bugs pour out of him
DEFLATE = (92, 95.5)
FLOP = 95.5
WINK = 97
FLASH = 98
D = T0 + FLASH * BEAT + 3.5

HW = 150.0                                  # half his width
SWIPE = 0.6                                 # beats for the swipe to reach the wheel
WHEEL_POCKETS = 12
LAND_POCKET = (4, 7)                        # where each spin's ball drops (counting from the Side end)

UV = hexc('#4a00ff')
COL = {
    'sack': hexc('#b8c848'), 'lime': hexc('#9aff00'), 'ball': hexc('#ffffff'), 'pip': hexc('#e8ff90'),
    'bug': hexc('#60ff20'), 'thread': hexc('#d0ff80'), 'frame': hexc('#a080ff'), 'uv': UV,
}


def _back(u, c1=1.4):
    u = np.clip(u, 0, 1)
    return 1 + (c1 + 1) * (u - 1) ** 3 + c1 * (u - 1) ** 2


def bt(b):
    """Seconds at beat b."""
    return T0 + b * BEAT


def hump(b, b0, b1):
    return float(np.sin(np.pi * np.clip((b - b0) / (b1 - b0), 0, 1)))


class Den:
    """Where everything is at any moment; render() draws it and score() listens to it."""

    def __init__(self, G, seed=67):
        rng = np.random.default_rng(seed)
        self.L = G.length
        pd = G.pd
        self.MID = float(pd[G.seg['Porch Front']].mean())
        self.W0, self.W1 = float(pd[G.seg['Left']].min()) + 8, float(pd[G.seg['Left']].max()) - 8
        self.POCKET = (self.W1 - self.W0) / WHEEL_POCKETS
        r0, r1 = float(pd[G.seg['Right']].min()), float(pd[G.seg['Right']].max())
        self.DC = (r0 + (r1 - r0) * 0.27, r0 + (r1 - r0) * 0.73)       # the two dice
        self.DH = (r1 - r0) * 0.2                                       # half a die
        self.porch_l = (float(pd[G.seg['Porch Left']].min()), float(pd[G.seg['Porch Left']].max()))
        self.porch_r = (float(pd[G.seg['Porch Right']].min()), float(pd[G.seg['Porch Right']].max()))
        side = float(pd[G.seg['Side']].max())
        # bugs: a few crawling all night, a dancing swarm for the chorus, and the ones that spill out of him
        self.crawl = [(lo, hi, rng.uniform(0, 1), rng.uniform(0.04, 0.1) * rng.choice([-1, 1]))
                      for lo, hi in [(0, side)] * 6 + [self.porch_l] * 4 + [self.porch_r] * 4]
        NS = 56
        self.swarm = (rng.uniform(0, self.L, NS), rng.uniform(70, 190, NS) * rng.choice([-1, 1], NS),
                      rng.uniform(0, 2 * np.pi, NS))
        NP = 48
        self.spill = (bt(SPILL[0]) + np.sort(rng.uniform(0, (SPILL[1] - SPILL[0]) * BEAT, NP)),
                      rng.uniform(-0.9, 0.9, NP), rng.uniform(450, 950, NP) * rng.choice([-1, 1], NP))
        self.spin_rate = (4.0, 6.5)                                     # pockets a second at the start

    # ---- the wheel ----
    def spin(self, k, t):
        """How far spin k has turned (in pockets) and how far through it is."""
        a, b = SPINS[k]
        ta, tb = bt(a + SWIPE), bt(b)
        u = np.clip((t - ta) / (tb - ta), 0, 1)
        return self.spin_rate[k] * (tb - ta) * (u - u * u / 2), float(u)

    def landing(self, k):
        """Path distance where spin k's ball drops: the middle of a lime pocket."""
        s_end, _ = self.spin(k, bt(SPINS[k][1]))
        j = LAND_POCKET[k]
        if (j + int(np.floor(s_end))) % 2 == 0:
            j += 1
        return self.W0 + self.POCKET * (j + 0.5 - (s_end % 1))

    def ball(self, k, t):
        a, b = SPINS[k]
        ta, tb = bt(a + SWIPE), bt(b)
        u = np.clip((t - ta) / (tb - ta), 0, 1)
        land = self.landing(k)
        amp = min(land - self.W0, self.W1 - land) * (1 - u) ** 1.6
        return land + amp * np.sin(2 * np.pi * (t - ta) / 1.1)

    def ball_turns(self, k):
        """Times the ball turns round at the end of a swing (where it rattles)."""
        a, b = SPINS[k]
        ta, tb = bt(a + SWIPE), bt(b)
        return [t for t in ta + 1.1 * (0.25 + 0.5 * np.arange(40)) if t < tb]

    def pockets_passing(self, k):
        """Times a pocket edge passes a fixed point: the wheel's ticks."""
        a, b = SPINS[k]
        ta, tb = bt(a + SWIPE), bt(b)
        out, last = [], 0
        for t in np.arange(ta, tb, 0.005):
            s, _ = self.spin(k, t)
            if int(s) > last:
                out.append(t)
                last = int(s)
        return out

    # ---- the dice ----
    def die(self, j, k, t):
        """Die j of throw k: (position, face, flying?) or None before the throw."""
        b = (t - T0) / BEAT
        th = THROWS[k]
        if b < th:
            return None
        land = th + 1 + 0.4 * j
        x0 = self.MID + HW
        if b < land:
            return lerp(x0, self.DC[j], smoothstep(th, land, b) ** 0.8), 0, True
        settle = th + 3
        if b < settle:
            face = 1 + int(t / 0.07 * (1.3 + 0.4 * j)) % 6
            jit = 10 * (1 - (b - land) / (settle - land)) * np.sin(2 * np.pi * 9 * t + j)
            return self.DC[j] + jit, face, False
        return self.DC[j], FACES[k][j], False

    def swipe(self, k, t):
        """Where the swipe streak is, running down Porch Left to the wheel (None if not swiping)."""
        a = SPINS[k][0]
        b = (t - T0) / BEAT
        if not a <= b < a + SWIPE:
            return None
        return lerp(self.MID - HW, self.W1, (b - a) / SWIPE)

    def bug_runner(self, t):
        """The bug that runs off with the thread (None before it comes for it)."""
        b = (t - T0) / BEAT
        c, hw = self.sack(t)[:2]
        edge = c - hw
        if b < GRAB:
            return None
        if b < PULL[0]:
            return lerp(self.porch_l[0], edge - 6, smoothstep(GRAB, PULL[0], b))
        return lerp(edge - 6, -40.0, smoothstep(PULL[0], PULL[1], b) ** 1.2)

    # ---- him ----
    def sack(self, t):
        """(centre, half width, brightness, eye opening, mouth, wink): the big fellow at time t."""
        b = (t - T0) / BEAT
        c, hw, I, eye, mouth, wink = self.MID, HW, 0.8, 1.0, 0.0, 1.0
        if b < RISE[1]:
            hw = HW * _back((b - RISE[0]) / (RISE[1] - RISE[0])) if b > 0 else 0.0
            eye = smoothstep(RISE[1] - 1, RISE[1], b)
            return c, max(hw, 0.0), I * smoothstep(0, 1.5, b), eye, 0.0, 1.0
        f = b - int(b)
        if b < THREAD:                       # dancing: sway every two beats, puff on every beat
            c += 18 * np.sin(np.pi * b)
            hw *= 1 + 0.06 * np.exp(-f * BEAT / 0.12)
            I += 0.12 * np.exp(-f * BEAT / 0.12)
        if CHORUS[0] <= b < CHORUS[1]:
            c += 9 * np.sin(2 * np.pi * 2 * b)
        for k, (a, _) in enumerate(SPINS):    # wind up, then swipe toward the wheel (down the path)
            big = 1.0 + 0.5 * k
            c += big * (30 * smoothstep(a - 1, a - 0.2, b) * (1 - smoothstep(a - 0.2, a + 0.05, b)) -
                        40 * smoothstep(a - 0.2, a + 0.05, b) * (1 - smoothstep(a + 0.6, a + 1.6, b)))
        for th in THROWS:                     # lean back, then fling toward the dice
            c += -28 * smoothstep(th - 1, th - 0.2, b) * (1 - smoothstep(th - 0.2, th + 0.05, b)) + \
                34 * smoothstep(th - 0.2, th + 0.05, b) * (1 - smoothstep(th + 0.6, th + 1.6, b))
        if LAUGH[0] <= b < LAUGH[1]:
            c += 5 * np.sin(2 * np.pi * 9 * t)
            mouth = hump(b, LAUGH[0], LAUGH[1]) ** 0.3
            I += 0.1
        if JOY[0] <= b < JOY[1] or JUBILEE[0] <= b < JUBILEE[1]:
            hw *= 1 + 0.22 * hump(f, 0, 0.6)
            I += 0.15 * hump(f, 0, 0.6)
            mouth = 0.6
        if SULK[0] <= b < STOMPS[1] + 1:
            s = smoothstep(SULK[0], SULK[0] + 0.5, b) * (1 - smoothstep(STOMPS[1], STOMPS[1] + 0.6, b))
            hw *= 1 - 0.2 * s
            I *= 1 - 0.3 * s
            eye *= 1 - 0.45 * s
        for st in STOMPS:
            if st <= b < st + 1:
                hw *= 1 + 0.3 * hump(b, st, st + 0.5)
                I += 0.25 * hump(b, st, st + 0.4)
        if PULL[0] <= b < DEFLATE[0]:         # unravelling
            u = smoothstep(PULL[0], PULL[1], b)
            hw = lerp(HW, 30.0, u)
            I = lerp(0.8, 0.45, u)
            eye = 1.5
            c += 4 * np.sin(2 * np.pi * 7 * t)
        elif b >= DEFLATE[0]:                 # an empty rag, letting the air out
            u = smoothstep(DEFLATE[0], DEFLATE[1], b)
            hw = lerp(30.0, 12.0, u) * (1 + 0.3 * np.sin(2 * np.pi * 18 * t) * (1 - u))
            I = 0.42
            eye = 0.8 * (1 - u)
            if b >= FLOP:
                c += 14 * _back((b - FLOP) / 0.5)
                eye = 0.0
            if b >= WINK:                     # the eyes open again, and one winks
                eye = 1.0
                wink = 0.0 if WINK + 0.6 <= b < WINK + 0.9 else 1.0
            if b >= FLASH:
                hw = 12.0 * (1 + 0.8 * hump(b, FLASH, FLASH + 0.6)) + 8 * smoothstep(FLASH, FLASH + 0.6, b)
                I = 0.42 + 0.4 * hump(b, FLASH, FLASH + 1.5)
        blink = ((t + 0.5) % 3.3) < 0.12 and b < THREAD
        return c, hw, I, 0.0 if blink else eye, mouth, wink


def render(G, seed=67):
    S = Den(G, seed)
    L = G.length
    pdp = G.pd[G.path]
    w = np.gradient(pdp)
    e0, e1 = pdp - w / 2, pdp + w / 2
    names = list(COL)
    ci = {k: i for i, k in enumerate(names)}
    lumps = np.random.default_rng(seed + 1).uniform(0, 2 * np.pi, 3)
    glow_rng = np.random.default_rng(seed + 2)
    glow_at, glow_v = glow_rng.uniform(0, L, 7), glow_rng.uniform(-25, 25, 7)
    F = nframes(D)
    out = np.zeros((F, G.N, 3))

    for fi in range(F):
        t = fi * DT
        b = (t - T0) / BEAT
        spans = []

        def put(a, z, I, col):
            if z < a:
                a, z = z, a
            spans.append((a, z, I, ci[col]))

        def blob(x, half, I, col):
            put(x - half, x + half, I, col)

        # him: a row of lumps, stitches, two eyes and a mouth
        c, hw, I, eye, mouth, wink = S.sack(t)
        if hw > 1:
            NSEG = 22
            edges = np.linspace(c - hw, c + hw, NSEG + 1)
            for q in range(NSEG):
                v = (q + 0.5) / NSEG * 2 - 1
                lump = 0.82 + 0.1 * np.sin(9 * v + lumps[0] + 1.3 * t) + 0.08 * np.sin(23 * v + lumps[1] - 0.7 * t)
                lump *= 1 - 0.45 * max(0.0, abs(v) - 0.8) / 0.2
                put(edges[q], edges[q + 1], I * lump, 'sack')
            for sv in (-0.62, 0.58):         # stitched seams
                for s in range(-2, 3):
                    x = c + sv * hw + s * 0.05 * hw
                    put(x - 0.012 * hw, x + 0.012 * hw, -0.7 * I, 'sack')
            for side, open_ in ((-1, eye * wink), (1, eye)):
                ex, eh = c + side * 0.3 * hw, max(0.07 * hw * open_, 0.0)
                if eh > 0.5:
                    put(ex - eh, ex + eh, -1.2 * I, 'sack')
                    put(ex - eh, ex + eh, 0.55, 'lime')
            if mouth > 0.02:
                mh = 0.12 * hw * mouth
                put(c - mh, c + mh, -1.1 * I, 'sack')
                put(c - mh, c + mh, 0.4 * mouth, 'lime')

        # the wheel: always there; it spins and the ball runs on it
        spin_s, hot = 0.0, 0.0
        for k, (a, z) in enumerate(SPINS):
            s, u = S.spin(k, t)
            if b >= a + SWIPE:
                spin_s = s
            if a + SWIPE <= b < z + 3:
                hot = max(hot, smoothstep(a + SWIPE, a + SWIPE + 0.5, b) * (1 - smoothstep(z + 2, z + 3, b)))
        wheel_I = 0.12 + 0.22 * hot
        for q in range(WHEEL_POCKETS + 2):
            a0 = S.W0 + S.POCKET * (q - (spin_s % 1))
            idx = q + int(np.floor(spin_s))
            if a0 < S.W1 and a0 + S.POCKET > S.W0:
                put(max(a0, S.W0), min(a0 + S.POCKET, S.W1), wheel_I, 'lime' if idx % 2 else 'uv')
        put(S.W0 - 6, S.W0, 0.4, 'frame')
        put(S.W1, S.W1 + 6, 0.4, 'frame')
        for k, (a, z) in enumerate(SPINS):
            if a + SWIPE <= b < z + 3:
                blob(S.ball(k, t), 3.5, 0.85, 'ball')
                if z <= b < z + 2 and ((b - z) * 2) % 1 < 0.5:    # the winning pocket flashes four times
                    land = S.landing(k)
                    put(land - S.POCKET / 2, land + S.POCKET / 2, 0.8, 'lime')
            x = S.swipe(k, t)
            if x is not None:
                for q in range(5):
                    blob(x + q * 18, 6, 0.8 * (1 - q / 5), 'thread')

        # the dice: frames always, pips once thrown; the last throw stays on the table
        for j in range(2):
            put(S.DC[j] - S.DH - 4, S.DC[j] - S.DH + 4, 0.35, 'frame')
            put(S.DC[j] + S.DH - 4, S.DC[j] + S.DH + 4, 0.35, 'frame')
            st = None
            for k in range(len(THROWS)):
                st = S.die(j, k, t) or st
            if st is None:
                continue
            x, face, flying = st
            if flying:
                blob(x, 10, 0.9 if (t * 20) % 1 < 0.6 else 0.5, 'pip')
                continue
            for q in range(face):
                blob(x - S.DH * 0.75 + 2 * S.DH * 0.75 * (q + 0.5) / face, 6, 0.8, 'pip')

        # bugs: crawling, dancing, spilling out of him, and the one with the thread
        if b < CHORUS[0] or CHORUS[1] <= b < PULL[0]:
            for lo, hi, u0, v in S.crawl:
                u = (u0 + v * t) % 1
                blob(lo + (hi - lo) * (1 - abs(2 * u - 1)), 2.5, 0.4, 'bug')
        if CHORUS[0] <= b < CHORUS[1]:
            env = smoothstep(CHORUS[0], CHORUS[0] + 1, b) * (1 - smoothstep(CHORUS[1] - 1, CHORUS[1], b))
            x0, v, wg = S.swarm
            pulse = np.exp(-(b % 1) * BEAT / 0.12)
            for x in (x0 + v * (t - bt(CHORUS[0])) + 14 * np.sin(np.pi * b + wg)) % L:
                blob(x, 3, env * (0.5 + 0.35 * pulse), 'bug')
        for t0, v0, vel in zip(*S.spill):
            if t >= t0:
                cc, hh = S.sack(t0)[:2]
                x = cc + v0 * hh + vel * (t - t0)
                if -10 < x < L + 10:
                    blob(x, 3, 0.65, 'bug')
        if THREAD <= b < PULL[1] + 0.5:
            edge = c - hw
            x = S.bug_runner(t)
            if x is None or b < PULL[0]:
                put(edge - 22 - 3 * np.sin(2 * np.pi * 1.5 * t), edge, 0.75, 'thread')
                if x is not None:
                    blob(x, 3, 0.8, 'bug')
            else:
                put(x, edge, 0.45, 'thread')
                blob(x, 3.5, 0.9, 'bug')

        # paint
        sp = np.array(spans) if spans else np.zeros((0, 4))
        ov = np.clip(np.minimum(sp[:, 1:2], e1) - np.maximum(sp[:, 0:1], e0), 0, None) / w
        buf = np.zeros((G.N, 3))
        lit = np.zeros(G.N)
        for i, name in enumerate(names):
            m = sp[:, 3] == i
            if m.any():
                Ii = np.clip(sp[m, 2] @ ov[m], 0, 1)
                buf += light(COL[name], Ii)
                lit += Ii

        # the den: blacklight with drifting lime glows, lime on the beat for the chorus, the final flash
        lev = keys(t, [(0, 0), (3, 1), (D - 2.5, 1), (D, 0)])
        uv = 0.17 + 0.04 * np.sin(2 * np.pi * t / 4.3 + pdp / 160)
        glow = sum(np.exp(-((pdp - (g + v * t) % L) / 70) ** 2) for g, v in zip(glow_at, glow_v))
        free = 1 - np.clip(lit, 0, 1)
        buf += light(UV, lev * uv * free) + light(COL['lime'], lev * 0.12 * np.clip(glow, 0, 1) * free)
        if CHORUS[0] <= b < CHORUS[1]:
            buf += light(COL['lime'], 0.14 * np.exp(-(b % 1) * BEAT / 0.12) * np.ones(G.N))
        if b >= FLASH:
            u = t - bt(FLASH)
            buf += light(COL['lime'], 0.85 * np.exp(-u / 0.6) * np.ones(G.N))
            buf += light(UV, 0.25 * np.exp(-u / 1.5) * np.ones(G.N))
        buf *= keys(t, [(0, 0), (1.5, 1), (D - 2.0, 1), (D, 0)])
        out[fi][G.path] = np.clip(buf, 0, 1)
    return out


# ---------------------------------------------------------------- music ----------------------------------------------
# A big-band boogie in A at the lights' 120 BPM, swung: upright piano boogie in the left hand, walking contrabass pizz,
# bass drum, brushes and a ride ping, muted brass stabs on the off-beats. TUNE is the hook (clarinet and muted horn,
# then trumpets for the chorus). Every gag below is a moment in Den: the rise, the swipes, the wheel's ticks, the
# ball's rattle and drop, the dice tumbling and the pips they come up, the laugh, the sulk and stomps, the thread,
# the spill, the raspberry and the flop, the wink and the flash. Sounds are panned to where they happen.

TUNE = [                                    # (beat, note, beats): the hook, four bars over A7 D7 A7 E7
    (0, 'E4', .5), (.5, 'G4', .5), (1, 'A4', 1), (2, 'C5', .5), (2.5, 'A4', .5), (3, 'G4', 1),
    (4, 'F#4', .5), (4.5, 'A4', .5), (5, 'C5', .5), (5.5, 'D5', .5), (6, 'C5', 1), (7, 'A4', 1),
    (8, 'E5', .5), (8.5, 'D5', .5), (9, 'C5', .5), (9.5, 'A4', .5), (10, 'G4', 1), (11, 'A4', 1),
    (12, 'C5', .5), (12.5, 'A4', .5), (13, 'G4', .5), (13.5, 'E4', .5), (14, 'A4', 2)]
PROG = ['A7', 'D7', 'A7', 'E7']             # a bar each
ROOTS = {'A7': 'A2', 'D7': 'D2', 'E7': 'E2'}
VOICE = {'A7': ('C#4', 'E4', 'G4'), 'D7': ('C4', 'F#4', 'A4'), 'E7': ('D4', 'G#4', 'B4')}
BOOGIE = [0, 4, 7, 9, 10, 9, 7, 4]          # left-hand eighths up from the root
WALK = [0, 4, 7, 9]                         # the bass walks a bar


def swing(b):
    """Swung eighths: the off-beat eighth lands two thirds of the way through the beat."""
    j, f = int(np.floor(b)), b - np.floor(b)
    return j + (f * 4 / 3 if f < 0.5 else 2 / 3 + (f - 0.5) * 2 / 3)


def score(M, G):
    from pixelhome.audio import SR, note, slide, whoosh
    n = note
    S = Den(G)
    piano = M.sampler('Keys/Upright Nr1/*_mf_*.wav')
    bass = M.sampler('Strings/Solo Contrabass/Pizz/*.wav', tune=-12)
    clar = M.sampler('Woodwinds/Clarinet/stac/*.wav', tune=-12)
    mute = M.sampler('Brass/F Horn/mute/*.wav', tune=-12)
    tpt = M.sampler('Brass/Trumpet/stac/*.wav', tune=-12)
    tpt_s = M.sampler('Brass/Trumpet/sus/*.wav', tune=-12)
    bone = M.sampler('Brass/Tenor Trombone/stac/*.wav', tune=-12)
    bone_s = M.sampler('Brass/Tenor Trombone/sus/*.wav', tune=-12)
    buzz = M.sampler('Brass/OldTrombone/Buzz/*.wav', tune=-12)
    tuba = M.sampler('Brass/Tuba/stac/*.wav', tune=-12)
    spic = M.sampler('Strings/Violin Section/Spic/*.wav', tune=-12)
    trem = M.sampler('Strings/Cello Section/trem/*.wav', tune=-12)
    pizz = M.sampler('Strings/Violin Section/Pizz/*.wav', tune=-12)
    glock = M.sampler('Percussion/Glock/*.wav', tune=-12)
    xylo = M.sampler('Percussion/Xylo/*.wav', tune=-12)
    fall = M.hits('Brass/OldTrombone/Fall/Trombone_Fall_A2*.wav')
    bd = M.hits('VSCO 1 Percussion/drums/bass/bdrum_f_*.wav')
    bd_ff = M.hits('VSCO 1 Percussion/drums/bass/bdrum_fff_*.wav')
    snare = M.hits('Percussion/Snare2-HitSN_v[35]*.wav')
    ride = M.hits('Percussion/susCymb1-hit_pp*.wav')
    crash = M.hits('VSCO 1 Percussion/varMetal/Cymbals/clash/crash_hit_ff*.wav')
    choke = M.hits('Percussion/cymbal-crashshort*.wav')
    timp = M.hits('Percussion/Timpani/Timpani1_Hit*.wav')
    troll = M.hits('Percussion/Timpani/Rolls/*.wav')
    clave = M.hits('Percussion/Claves1_Hit*.wav')
    wood = M.hits('VSCO 1 Percussion/varWood/wood_click*.wav')
    maraca = M.hits('VSCO 1 Percussion/varWood/maraca[1-5].wav')
    guiro = M.hits('Percussion/Guiro-Fast*.wav')
    cow = M.hits('Percussion/Cowbell1_Hit*.wav')
    brake = M.hits('Percussion/BrakeDrum1_Hammer*.wav')
    slap = M.hits('VSCO 1 Percussion/varWood/slapstick[0-9].wav')
    ratchet = M.hits('Percussion/Ratchet1-Slow*.wav')
    belltree = M.hits('Percussion/BellTree_Stroke*.wav')

    for name, gain, rev in (('piano', 0.22, 0.12), ('bass', 0.34, 0.06), ('drums', 0.22, 0.12), ('lead', 0.23, 0.18),
                            ('brass', 0.2, 0.18), ('fx', 0.17, 0.2), ('perc', 0.3, 0.12), ('bugs', 0.09, 0.2),
                            ('hold', 0.12, 0.3)):
        M.bus(name, gain=gain, reverb=rev)

    order = np.argsort(G.pd)
    xs, ds = G.pos[order, 0], G.pd[order]
    x0, x1 = xs.min(), xs.max()

    def pan_at(d):                          # path distance -> left/right across the facade, from the street
        x = np.interp(np.clip(d, 0, G.length), ds, xs)
        return float(0.85 * (2 * (x - x0) / (x1 - x0) - 1))

    def at(b):
        return bt(swing(b))

    def mono(sig, pans):
        a = (np.clip(pans, -1, 1) + 1) * np.pi / 4
        return np.vstack([sig * np.cos(a), sig * np.sin(a)]) * np.sqrt(2)

    def tone(f, amp, buzz_=0.12):           # a whistle, or a raspberry with buzz up, at frequency curve f
        ph = 2 * np.pi * np.cumsum(f) / SR
        noise = np.convolve(M.rng.normal(0, 1, len(f)), np.ones(24) / 24, 'same')
        sig = np.sin(ph) + buzz_ * np.sin(2 * ph) + 0.6 * buzz_ * np.sin(3 * ph) + 0.08 * noise * (1 + np.sin(ph))
        return amp * sig

    pc = pan_at(S.MID)
    pw = pan_at((S.W0 + S.W1) / 2)

    def band(b0, b1, stabs=False, vel=96):
        """The rhythm section from beat b0 to b1 (whole beats), bars counted from b0."""
        for b in range(int(b0), int(b1)):
            q = b - int(b0)
            c = PROG[(q // 4) % 4]
            r = n(ROOTS[c])
            M.add('bass', bass.play(r + WALK[q % 4], vel), at(b), 1.0, -0.1)
            for e in (0, 1):                 # the boogie: eighths up and back down from the root
                M.add('piano', piano.play(r + 12 + BOOGIE[(q % 4) * 2 + e], vel - 10), at(b + e / 2), 0.8, -0.3)
            M.add('drums', bd.play(vel if q % 2 == 0 else vel - 20), at(b), 0.7)
            if q % 2:
                M.add('drums', snare.play(vel), at(b), 0.8, 0.15)
            M.add('drums', ride.play(80), at(b), 0.5, 0.35)
            if q % 2:
                M.add('drums', ride.play(64), at(b + 0.5), 0.4, 0.35)
            if stabs and q % 2:
                for m in VOICE[c]:
                    M.add('brass', mute.play(n(m), vel, dur=0.18), at(b + 0.5), 0.7, 0.2)

    def hook(inst, b0, bus, vel, gain=1.0, pan=0.0, shift=0, beats=(0, 16), dur=0.9):
        for b, m, ln in TUNE:
            if beats[0] <= b < beats[1]:
                M.add(bus, inst.play(n(m) + shift, vel, dur=ln * BEAT * dur), at(b0 + b), gain, pan)

    # ---- he grows up out of the porch; the band strikes up with a shout ----
    r = troll.play(70, dur=bt(RISE[1]) - 0.8)
    M.add('drums', r * np.linspace(0.1, 1, r.shape[1]) ** 2, 0.8, 0.5, pc)
    M.add('hold', trem.play(n('A2'), 60, dur=bt(RISE[1]) - 0.5), 0.5, 0.8, pc)
    for i in range(14):                     # a piano glissando up as he swells
        t = bt(RISE[1]) - 1.2 + i * 0.08
        M.add('piano', piano.play(n('A2') + [0, 3, 5, 7, 10][i % 5] + 12 * (i // 5), 70 + 3 * i), t, 0.7, pc)
    tb = bt(RISE[1])
    for m in ('A3', 'C#4', 'E4', 'G4'):
        M.add('brass', tpt_s.play(n(m), 118, dur=0.6), tb, 0.6, pc)
    M.add('brass', fall.play(110), tb + 0.5, 0.8, pc)
    M.add('drums', crash.play(118), tb, 0.8, pc)
    M.add('drums', bd_ff.play(120), tb, 0.8, pc)

    # ---- the band, and where it stops ----
    band(RISE[1], CHORUS[0])
    band(CHORUS[0], CHORUS[1], stabs=True, vel=104)
    band(CHORUS[1], SULK[0])                 # stop-time for the sulk and the stomps
    band(SPINS[1][0], THREAD, stabs=True, vel=100)
    hook(clar, RISE[1], 'lead', 100, 1.0, 0.1)
    hook(mute, RISE[1], 'brass', 96, 0.8, -0.1, shift=-12)

    # ---- the swipes and the wheel: a whoosh down Porch Left, a tick a pocket, the ball's rattle, the drop ----
    for k, (a, z) in enumerate(SPINS):
        t0, t1 = bt(a), bt(a + SWIPE)
        tt = np.linspace(0, 1, int((t1 - t0) * SR))
        sw = whoosh(t1 - t0 + 0.1, 400, 2600, 0.6, seed=20 + k)[0][:len(tt)]
        M.add('fx', mono(sw, np.array([pan_at(lerp(S.MID - HW, S.W1, u)) for u in tt])), t0, 1.0 + 0.3 * k)
        for i, t in enumerate(S.pockets_passing(k)):
            M.add('perc', clave.play(80 if i % 2 else 96, pitch=3 * k), t, 0.45, pw)
        for t in S.ball_turns(k):
            M.add('perc', maraca.play(90), t, 0.5, pan_at(S.ball(k, t)))
        land = S.landing(k)
        tz = bt(z)
        M.add('brass', mute.play(n('E4'), 112, dur=0.15), tz, 0.9, pan_at(land))
        M.add('brass', mute.play(n('A4'), 118, dur=0.5), tz + 0.2, 0.9, pan_at(land))
        M.add('drums', choke.play(100), tz, 0.6, pan_at(land))
        for q in range(4):
            M.add('perc', cow.play(100), bt(z + q / 2), 0.6, pan_at(land))

    # ---- the laugh ----
    for i in range(12):
        t = bt(LAUGH[0]) + i * BEAT / 3
        m = n(['E3', 'C#3', 'A2'][i % 3]) - (i // 6) * 2
        M.add('brass', bone.play(m, 110 - 3 * i, dur=0.12), t, 0.9, pc)
        M.add('lead', buzz.play(m - 12, 90, dur=0.1), t, 0.5, pc)

    # ---- the dice: a fling, two landings, a tumble on the right wing, a knock for each pip ----
    for k, th in enumerate(THROWS):
        M.add('fx', slide(0.0, 0.45, 500, 900, 0.5, 0.6), bt(th - 1), 0.5, pc)
        t0, t1 = bt(th), bt(th + 1.4)
        tt = np.linspace(0, 1, int((t1 - t0) * SR))
        sw = whoosh(t1 - t0 + 0.1, 900, 2200, 0.6, seed=30 + k)[0][:len(tt)]
        M.add('fx', mono(sw, np.array([pan_at(lerp(S.MID + HW, S.DC[1], u)) for u in tt])), t0, 0.9)
        for j in range(2):
            land = th + 1 + 0.4 * j
            p = pan_at(S.DC[j])
            M.add('perc', wood.play(118, pitch=-2 * j), bt(land), 1.0, p)
            g = guiro.play(96, dur=bt(th + 3) - bt(land))
            M.add('perc', g, bt(land) + 0.05, 0.6, p)
            for q in range(FACES[k][j]):
                M.add('perc', wood.play(110, pitch=4 + q), bt(th + 3) + 0.07 * q + 0.25 * j, 0.8, p)
    for b in range(*JOY):                    # six and five: he jumps for joy
        for m in ('A4', 'C#5', 'E5'):
            M.add('brass', tpt.play(n(m), 116, dur=0.2), bt(b), 0.6, pc)
        M.add('perc', cow.play(110), bt(b), 0.6, pc)

    # ---- the chorus: the hook on trumpets, the bugs skittering on violins all over the roof ----
    hook(tpt, CHORUS[0], 'lead', 112, 0.8, 0.1)
    hook(clar, CHORUS[0], 'lead', 104, 0.7, -0.1)
    hook(mute, CHORUS[0], 'brass', 100, 0.8, 0.2, shift=-12)
    x0b, vb, _ = S.swarm
    scale = [n(m) for m in ('A3', 'C4', 'D4', 'D#4', 'E4', 'G4', 'A4')]
    for i in range(int((CHORUS[1] - CHORUS[0]) * 4)):
        t = bt(CHORUS[0]) + i * BEAT / 4
        j = int(M.rng.integers(len(x0b)))
        d = (x0b[j] + vb[j] * (t - bt(CHORUS[0]))) % G.length
        M.add('bugs', spic.play(scale[int(M.rng.integers(len(scale)))], 70), t, 1.0, pan_at(d))

    # ---- snake eyes: stop-time, a sad trombone, two stomps ----
    for i, m in enumerate(('E3', 'D#3', 'D3', 'C#3')):
        dur = 0.4 if i < 3 else 1.2
        t = bt(SULK[0]) + 0.45 * i
        s = bone_s.play(n(m), 100, dur=dur)
        wob = 1 + 0.15 * np.sin(2 * np.pi * 6 * np.arange(s.shape[1]) / SR) * (i == 3)
        M.add('brass', s * wob, t, 0.9, pc)
    for st in STOMPS:
        M.add('drums', bd_ff.play(127), bt(st), 1.0, pc)
        M.add('drums', timp.play(120), bt(st), 0.8, pc)
        M.add('perc', brake.play(115), bt(st), 0.7, pc)
        for m in ('A2', 'E3'):
            M.add('brass', bone.play(n(m), 120, dur=0.3), bt(st), 0.7, pc)

    # ---- the second spin comes up his: the jubilee ----
    hook(tpt, JUBILEE[0] - 10, 'lead', 116, 0.9, 0.1, beats=(10, 16))
    hook(clar, JUBILEE[0] - 10, 'lead', 108, 0.7, -0.1, beats=(10, 16))
    M.add('perc', belltree.play(110), bt(SPINS[1][1]), 0.7, pan_at(S.landing(1)))
    M.add('drums', crash.play(110), bt(SPINS[1][1]), 0.6, pan_at(S.landing(1)))

    # ---- the loose thread: the band stops; a bug runs it off and he unravels; bugs spill both ways ----
    edge = S.MID - HW
    M.add('lead', pizz.play(n('E5'), 100), bt(THREAD), 0.8, pan_at(edge))
    M.add('lead', pizz.play(n('E5'), 80), bt(THREAD + 0.5), 0.6, pan_at(edge))
    M.add('perc', xylo.play(n('A5'), 100), bt(GRAB), 0.6, pan_at(S.porch_l[0]))
    t0, t1 = bt(PULL[0]), bt(PULL[1])
    tt = np.linspace(t0, t1, int((t1 - t0) * SR))
    f = 1400 * 2 ** (-2.2 * (tt - t0) / (t1 - t0))
    sig = tone(f, 0.22) * np.clip((tt - t0) / 0.05, 0, 1) * np.clip((t1 - tt) / 0.1, 0, 1)
    pans = np.array([pan_at(S.bug_runner(x)) for x in np.linspace(t0, t1, 64)])
    M.add('fx', mono(sig, np.interp(np.linspace(0, 1, len(tt)), np.linspace(0, 1, 64), pans)), t0, 0.7)
    t = t0
    while t < t1:                            # the ratchet of a seam coming undone
        M.add('perc', ratchet.play(80, dur=0.3), t, 0.4, pan_at(edge))
        t += 0.33
    for i, m in enumerate(('A2', 'G#2', 'G2', 'F#2', 'F2', 'E2', 'D#2', 'D2', 'C#2', 'C2', 'B1', 'A#1')):
        M.add('bass', bass.play(n(m), 100 - 3 * i), bt(PULL[0] + i / 2), 0.9, pc)
    for t0s, v0, vel in list(zip(*S.spill))[::2]:
        cc, hh = S.sack(t0s)[:2]
        x = cc + v0 * hh
        M.add('bugs', spic.play(scale[int(M.rng.integers(len(scale)))] + 12, 80), t0s, 1.2, pan_at(x))
        M.add('bugs', spic.play(scale[int(M.rng.integers(len(scale)))] + 12, 70), t0s + 0.12, 1.0,
              pan_at(x + vel * 0.12))

    # ---- deflating: a raspberry that flaps as he does; the flop ----
    t0, t1 = bt(DEFLATE[0]), bt(DEFLATE[1])
    tt = np.arange(int((t1 - t0) * SR)) / SR
    u = tt / (t1 - t0)
    f = 240 * 2 ** (-1.8 * u) * (1 + 0.12 * np.sin(2 * np.pi * 18 * tt) * (1 - u))
    rasp = tone(f, 0.32, buzz_=0.9) * np.clip(tt / 0.04, 0, 1) * np.clip((1 - u) / 0.08, 0, 1)
    M.add('fx', mono(rasp, np.full(len(rasp), pc)), t0, 1.0)
    M.add('perc', slap.play(90), bt(FLOP), 0.6, pc)
    M.add('bass', tuba.play(n('A1'), 100), bt(FLOP), 0.9, pc)

    # ---- the wink, and the flash ----
    M.add('perc', glock.play(n('E6'), 100), bt(WINK + 0.6), 0.7, pc)
    M.add('fx', slide(0.0, 0.1, 1200, 2000, 0.12, 0.5), bt(WINK + 0.6), 0.5, pc)
    tf = bt(FLASH)
    for i in range(10):
        M.add('piano', piano.play(n('A3') + [0, 4, 7, 9, 10][i % 5] + 12 * (i // 5), 90 + 3 * i), tf - 0.5 + i * 0.05, 0.6)
    for m in ('A3', 'C#4', 'E4', 'G4', 'B4'):
        M.add('brass', tpt_s.play(n(m), 122, dur=1.6), tf, 0.55)
    for m in ('A2', 'E3', 'G3'):
        M.add('brass', bone_s.play(n(m), 120, dur=1.6), tf, 0.6)
    M.add('bass', tuba.play(n('A1'), 124), tf, 1.1)
    M.add('bass', bass.play(n('A1'), 124), tf, 0.9)
    M.add('drums', crash.play(124), tf, 1.0)
    M.add('drums', bd_ff.play(124), tf, 1.0)
    M.add('drums', timp.play(124), tf, 0.8)
    M.add('brass', fall.play(110), tf + 1.2, 0.6)
