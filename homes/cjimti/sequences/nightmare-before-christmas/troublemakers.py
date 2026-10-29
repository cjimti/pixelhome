"""Three Little Troublemakers: three small trick-or-treaters (a pumpkin, a bat and a ghost) scurry in from
the free right end through a moonlit neighbourhood (a warm porch light, a few jack-o'-lanterns) and
tiptoe along the right wing in a line, a step a beat. Twice a lamp sweeps the wing and they freeze
mid-step, eyes wide; the second time the ghost is a step late and bumps the other two along. They scurry
up to the porch and squabble: the bat shoves the pumpkin, the pumpkin shoves back and knocks the bat into
the ghost, then hops over and lands on the ghost, who goes flat as a pancake and pops back up. Over on
the left wing they build a cage a part a beat (a wall, seven bars, a gate held up), the bat fetches a
wrapped present from under the porch light, and they put it in the cage and hide outside it with only
their eyes showing. Nothing comes. They peek, one by one. Then they creep into the cage themselves to
look at the present, the gate slams, and they ricochet off the walls until the present goes off like a
party popper and blows the cage apart. Victory dance; the pumpkin and the bat race the length of the
house and off the free right end while the ghost slips away round the side; two peek back in at the
right end, the ghost pops up on the porch, and everything flashes their three colours.

Characters live in path distance and are drawn with exact span-over-pixel coverage (as in Bone Yard):
each is a stack of lit spans with eye holes, stretched as it hops and squashed as it is sat on. Times are
beats on a 120 BPM grid (BEAT, beat 0 at T0) that score() shares."""
import numpy as np
from pixelhome.fx import DT, hexc, light, smoothstep, keys, lerp, nframes

CODE = 'NB07'
TITLE = 'Three Little Troublemakers'
KIND = 'show'
DESCRIPTION = ('Three trick-or-treaters tiptoe along the roof, freeze in the lamplight, squabble, and build a '
               'trap baited with a present. Then they spring it on themselves.')

BPM = 120
BEAT = 60 / BPM
T0 = 2.0                                    # beat 0

# the story, in beats from T0
SCURRY_IN = (0, 8)
SNEAK = (8, 24)
FREEZES = ((12, 15), (20, 23))              # the lamp sweeps; the second time the ghost is a step late
SCURRY_UP = (24, 28)
BICKER = (28, 40)
SHOVE1, SHOVE2 = 30, 33
HOP, SQUASH, UNSQUASH = 35, 36, 39
SCURRY_R = (40, 44)
BUILD = 44                                  # one cage part a beat: the wall, seven bars, the gate held up
PRESENT = (56, 60)
HIDE = (60, 68)
PEEKS = (64, 65, 66)
CREEP = ((68, 70), (70, 72), (72, 74))      # one by one into the cage
SNAP = 76
POP = 84
DANCE = (84, 96)
SCAMPER = (96, 104)
PEEK = 104
TADA = 106
D = T0 + TADA * BEAT + 3.0

LINE = (70.0, 0.0, -70.0)                   # pumpkin leads, then the bat, then the ghost
STEP = 32.0                                 # a tiptoe step
HW = 150.0                                  # half the cage

NIGHT = hexc('#2a48b0')                     # moonlight
PORCH = hexc('#ffb060')
COL = {
    'orange': hexc('#ff5000'), 'stem': hexc('#30d020'), 'purple': hexc('#8020ff'), 'white': hexc('#e8eeff'),
    'mint': hexc('#30ffa0'), 'yellow': hexc('#ffc020'), 'pink': hexc('#ff60c0'), 'steel': hexc('#b0c0e0'),
    'red': hexc('#ff1020'), 'gold': hexc('#ffb020'), 'lamp': hexc('#fff0c0'), 'blue': hexc('#2050ff'),
}
CONFETTI = ['red', 'gold', 'stem', 'blue', 'pink', 'white']
KIDS = [
    dict(L=46.0, parts=[(0, 40, 1.0, 'orange'), (40, 46, 0.9, 'stem')], body='orange',
         eyes=[(22, 27), (31, 36)], glow='yellow'),
    dict(L=60.0, parts=[(0, 20, 0.5, 'purple'), (20, 40, 1.0, 'purple'), (40, 60, 0.5, 'purple')], body='purple',
         eyes=[(26, 30), (33, 37)], glow='pink'),
    dict(L=48.0, parts=[(0, 48, 0.85, 'white'), (2, 5, -0.4, 'white'), (8, 11, -0.4, 'white'), (-6, 54, 0.12, 'mint')],
         body='white', eyes=[(29, 34), (37, 42)], glow=None),
]


def _back(u, c1=1.4):
    u = np.clip(u, 0, 1)
    return 1 + (c1 + 1) * (u - 1) ** 3 + c1 * (u - 1) ** 2


def bt(b):
    """Seconds at beat b."""
    return T0 + b * BEAT


def hump(b, b0, b1):
    """0 -> 1 -> 0 between beats b0 and b1."""
    return float(np.sin(np.pi * np.clip((b - b0) / (b1 - b0), 0, 1)))


def stepped(b, b0, b1, d0, d1, n, rise=0.45):
    """From d0 to d1 in n quick steps between beats b0 and b1; also how high the current step lifts."""
    if b <= b0:
        return d0, 0.0
    if b >= b1:
        return d1, 0.0
    s = (b - b0) / (b1 - b0) * n
    i, f = int(s), s - int(s)
    return d0 + (d1 - d0) * (i + smoothstep(0, rise, f)) / n, float(np.sin(np.pi * min(f / rise, 1)))


SNEAK_STEPS = [b for b in range(*SNEAK) if not any(a <= b < z for a, z in FREEZES)]


class Show:
    """Where everything is at any moment; render() draws it and score() listens to it."""

    def __init__(self, G):
        self.L = G.length
        self.CX = float(G.pd[G.seg['Right']].mean())
        CX = self.CX
        self.items = [CX - HW] + [CX - HW + j * 2 * HW / 8 for j in range(1, 8)] + [CX + HW]
        self.home0 = 490.0                  # where the line's middle is when the tiptoeing starts
        self.top = self.home0 + STEP * len(SNEAK_STEPS)
        self.bick = (1560.0, 1490.0, 1420.0)
        self.mid_r = CX - HW - 70.0         # line middle at the end of the run to the right wing
        self.hide = (CX - HW - 44, CX - HW - 94, CX - HW - 144)
        self.inside = (CX - 80, CX - 40, CX + 45)
        self.dance = (CX - 110, CX, CX + 110)
        lo, hi = CX - HW + 22, CX + HW - 22
        self.box = (lo, hi)
        self.speed = (330.0, 410.0, 480.0)  # ricochet speeds in the cage
        self.u0 = [(p - lo) / (hi - lo) / 2 for p in self.inside]
        # the cage's parts fly off when the present pops
        self.fly = [(-1 if x < CX else 1) * (520 + 900 * abs(x - CX) / HW) if abs(x - CX) > 1 else 700.0
                    for x in self.items]
        # The staging above is worked out as if they walked toward the free right end. On the house they
        # come in from the free right end instead: the way in maps onto the right wing, the porch is the
        # porch, and the cage goes up on the left wing (a mirror about M2). Nothing enters along Side.
        r0, r1 = float(G.pd[G.seg['Right']].min()), float(G.pd[G.seg['Right']].max())
        self.r0, self.r1 = r0, r1
        self.cx = float(G.pd[G.seg['Left']].mean())
        self.M2 = self.cx + CX
        self.porch = float(G.pd[G.seg['Porch Front']].mean())
        self.cage = [self.M2 - x for x in self.items]
        self.flyv = [-v for v in self.fly]
        self.route = ([-160.0, self.home0, self.top, self.bick[1]],
                      [self.L + 160, r1 - 110, r0 + 85, self.M2 - self.bick[1]])
        self.beams = ((r0 - 120, r1 + 60), (r1 + 60, r0 - 120))      # the lamp's two sweeps
        self.lanterns = (self.L - 22, r0 - 8, float(G.pd[G.seg['Porch Left']].min()) + 8,
                         float(G.pd[G.seg['Left']].min()) + 20)

    # ---- the line, before it breaks up ----
    def line_mid(self, b):
        if b < SCURRY_IN[1]:
            return stepped(b, *SCURRY_IN, -160.0, self.home0, 16)
        if b < SNEAK[1]:
            done = sum(1 for s in SNEAK_STEPS if s + 1 <= b)
            cur = [s for s in SNEAK_STEPS if s <= b < s + 1]
            f = smoothstep(0, 0.45, b - cur[0]) if cur else 0.0
            lift = float(np.sin(np.pi * min((b - cur[0]) / 0.45, 1))) if cur else 0.0
            return self.home0 + STEP * (done + f), lift
        if b < SCURRY_UP[1]:
            return stepped(b, *SCURRY_UP, self.top, self.bick[1], 8)
        return self.bick[1], 0.0

    def ricochet(self, k, t):
        """Position and heading of kid k bouncing round the shut cage."""
        lo, hi = self.box
        u = self.u0[k] + self.speed[k] * (t - bt(SNAP + 0.5)) / (2 * (hi - lo))
        ph = u % 1
        return lo + (hi - lo) * (1 - abs(2 * ph - 1)), (1.0 if ph < 0.5 else -1.0)

    def hits(self, k):
        """(time, path distance) of each wall kid k hits while trapped, on the house."""
        return [(t, self.M2 - x) for t, x in self.wall_hits(k)]

    def kid(self, k, t):
        """(centre, heading, stretch, brightness, eye size, hiding, wing flap) of kid k at time t, on the house."""
        b = (t - T0) / BEAT
        c, dr, g, I, eye, hid, flap = self._kid0(k, t)
        if b < BICKER[0]:                    # in from the free right end, along the right wing, up to the porch
            m = self.line_mid(b)[0]
            return float(np.interp(m, *self.route)) - (c - m), -dr, g, I, eye, hid, flap
        if PRESENT[0] <= b < HIDE[0] and k == 1:   # the bat fetches the present from under the porch light
            flap = 0.7 + 0.5 * np.sin(2 * np.pi * 7 * t)
            if b < PRESENT[0] + 1.5:
                return lerp(self.cx + 40, self.porch, smoothstep(PRESENT[0], PRESENT[0] + 1.5, b)), 1.0, 1, 1, 1, 0, flap
            if b < PRESENT[0] + 2:
                return self.porch, -1.0, 1.0, 1.0, 1.0, 0.0, flap
            c = lerp(self.porch, self.cx + 34, smoothstep(PRESENT[0] + 2, PRESENT[1] - 0.5, b))
            return c, -1.0, 1.0, 1.0, 1.0, 0.0, flap
        if SCAMPER[0] <= b < PEEK:           # the pumpkin and the bat run the length of the house and off the
            d0 = self.M2 - self.dance[k]     # free right end; the ghost slips out along Side
            g = 1 + 0.12 * abs(np.sin(2 * np.pi * 5 * t))
            if k == 2:
                return lerp(d0, -90.0, smoothstep(SCAMPER[0], SCAMPER[0] + 4, b)), -1.0, g, 1.0, 1.0, 0.0, 1.0
            a = SCAMPER[0] + k
            return lerp(d0, self.L + 90, smoothstep(a, a + 6, b) ** 1.3), 1.0, g, 1.0, 1.0, 0.0, \
                0.75 + 0.35 * np.sin(2 * np.pi * 6 * t)
        if b >= PEEK:                        # two peek back in at the free right end; the ghost pops up on the porch
            enter = smoothstep(PEEK, PEEK + 1, b)
            hid = 1 - smoothstep(TADA - 0.2, TADA, b)
            g = 1 + 0.6 * hump(b, TADA, TADA + 0.6)
            I = 1 + 0.4 * hump(b, TADA, TADA + 1)
            if k == 2:
                return self.porch, 1.0, g * (0.3 + 0.7 * enter), I * enter, 1.0, hid, 1.0
            return lerp(self.L + 40, self.L - 30 - 60 * k, enter), -1.0, g, I, 1.0, hid, 1.0
        return self.M2 - c, -dr, g, I, eye, hid, flap

    def wall_hits(self, k):
        """(time, path distance) of each wall kid k hits while trapped."""
        lo, hi = self.box
        out = []
        per = 2 * (hi - lo) / self.speed[k]
        for j in range(1, 40):
            t = bt(SNAP + 0.5) + (j * 0.5 - self.u0[k]) * per
            if bt(SNAP + 0.5) < t < bt(POP):
                out.append((t, hi if j % 2 else lo))
        return out

    def _kid0(self, k, t):
        """The same, as staged toward the free right end (see __init__)."""
        b = (t - T0) / BEAT
        dr, g, I, eye, hid, flap = 1.0, 1.0, 1.0, 1.0, 0.0, 1.0
        if b < BICKER[0]:
            m, lift = self.line_mid(b)
            c = m + LINE[k]
            g = 1 + 0.18 * lift
            for a, z in FREEZES:
                if a <= b < z + 0.5:
                    eye = 1 + 0.5 * smoothstep(a, a + 0.3, b) * (1 - smoothstep(z, z + 0.5, b))
                    c += 1.2 * np.sin(2 * np.pi * 11 * t) * (b < z)
            late = FREEZES[1][0]
            if k == 2:                       # the ghost's late step, and back into line
                c += STEP * smoothstep(late, late + 0.45, b) * (1 - smoothstep(late + 3, late + 4, b))
            if k == 1:
                c += 18 * _back((b - late - 0.15) / 0.3) * (1 - smoothstep(late + 3, late + 4, b)) * (b > late)
            if k == 0:
                c += 12 * _back((b - late - 0.3) / 0.3) * (1 - smoothstep(late + 3, late + 4, b)) * (b > late)
            if SNEAK[0] <= b < SNEAK[1]:
                flap = 0.7 + 0.15 * np.sin(2 * np.pi * 2 * b)
            elif b < SNEAK[0] or b >= SNEAK[1]:
                flap = 0.75 + 0.35 * np.sin(2 * np.pi * 6 * t)
        elif b < SCURRY_R[0]:
            c = self.bick[k]
            if k == 0:
                dr = -1.0 if b < UNSQUASH + 0.5 else 1.0
                c += 45 * _back((b - SHOVE1) / 0.35) * (1 - smoothstep(SHOVE1 + 0.6, SHOVE1 + 2, b)) * (b > SHOVE1)
                c -= 22 * smoothstep(SHOVE2 - 0.4, SHOVE2, b) * (1 - smoothstep(SHOVE2, SHOVE2 + 1, b))
                if b >= HOP:                 # hop over the bat and land on the ghost
                    land = self.bick[2]
                    c = lerp(self.bick[0], land, smoothstep(HOP, SQUASH, b))
                    g = 1 + 0.35 * hump(b, HOP, SQUASH)
                    I = 1 + 0.3 * hump(b, HOP, SQUASH)
                    if b >= UNSQUASH:        # bounced off when the ghost pops up
                        c = lerp(land, self.bick[0], _back((b - UNSQUASH) / 0.7))
                        g = 1 + 0.3 * hump(b, UNSQUASH, UNSQUASH + 0.6)
            elif k == 1:
                dr = 1.0 if b < SHOVE2 else (-1.0 if b < UNSQUASH + 0.5 else 1.0)
                c += 22 * smoothstep(SHOVE1 - 0.4, SHOVE1, b) * (1 - smoothstep(SHOVE1, SHOVE1 + 1, b))
                c -= 30 * _back((b - SHOVE2) / 0.3) * (1 - smoothstep(SHOVE2 + 0.6, SHOVE2 + 2, b)) * (b > SHOVE2)
                if SQUASH <= b < UNSQUASH:   # laughing
                    flap = 1 + 0.4 * np.sin(2 * np.pi * 8 * t)
                    c += 4 * np.sin(2 * np.pi * 4 * t)
            else:
                c -= 45 * _back((b - SHOVE2 - 0.2) / 0.35) * (1 - smoothstep(SHOVE2 + 0.8, SHOVE2 + 2, b)) * \
                    (b > SHOVE2 + 0.2)
                if SQUASH <= b < UNSQUASH:   # flat as a pancake
                    s = smoothstep(SQUASH, SQUASH + 0.12, b)
                    g, I, eye = 1 + 1.3 * s, 1 - 0.5 * s, 1 - 0.6 * s
                elif b >= UNSQUASH:
                    g = 1 + 0.6 * np.exp(-(b - UNSQUASH) * 3) * np.cos(2 * np.pi * 2.5 * (b - UNSQUASH))
            if b >= SCURRY_R[0] - 0.5:
                dr = 1.0
            if b >= SCURRY_R[0]:
                pass
        elif b < BUILD:
            m, lift = stepped(b, *SCURRY_R, self.bick[1], self.mid_r, 16)
            c, g = m + LINE[k], 1 + 0.15 * lift
        elif b < PRESENT[0]:
            spots = [(BUILD + i, self.items[i]) for i in range(9) if i % 3 == k]
            c = self.mid_r + LINE[k]
            prev_b = BUILD
            for pb, x in spots:
                if b < pb:
                    c = lerp(c, x, smoothstep(prev_b, pb, b))
                    break
                c, prev_b = x, pb + 0.5
                g = 1 + 0.3 * hump(b, pb - 0.1, pb + 0.4)
            else:
                c = lerp(c, self.inside[k] - 20 * (1 - k), smoothstep(prev_b, BUILD + 10, b))
                if b > BUILD + 10:
                    g = 1 + 0.3 * hump((b - BUILD - 10) % 1, 0, 0.5)
            dr = 1.0 if k != 2 else (1.0 if b < BUILD + 8.5 else -1.0)
        elif b < HIDE[0]:
            if k == 1:                       # off the end for the present and back with it
                if b < PRESENT[0] + 1.5:
                    c = lerp(self.CX, self.L + 90, smoothstep(PRESENT[0], PRESENT[0] + 1.5, b))
                elif b < PRESENT[0] + 2:
                    c = self.L + 90
                else:
                    c = lerp(self.L + 90, self.CX + 32, smoothstep(PRESENT[0] + 2, PRESENT[1] - 0.5, b))
                    dr = -1.0
                flap = 0.7 + 0.5 * np.sin(2 * np.pi * 7 * t)
            else:
                x0 = self.inside[k] - 20 * (1 - k)
                c = lerp(x0, self.CX + (-90 if k == 0 else 90), smoothstep(PRESENT[0], PRESENT[0] + 1, b))
                dr = 1.0 if k == 0 else -1.0
        elif b < CREEP[0][0]:
            start = self.CX + (-90 if k == 0 else (-34 if k == 1 else 90))
            c = lerp(start, self.hide[k], smoothstep(HIDE[0], HIDE[0] + 1.5, b))
            hid = smoothstep(HIDE[0] + 1, HIDE[0] + 2, b)
            pk = PEEKS[k]
            p = hump(b, pk, pk + 1)
            c += 26 * p
            hid *= 1 - p
            g = 1 + 0.2 * p
        elif b < SNAP:
            a, z = CREEP[k]
            c, lift = stepped(b, a, z, self.hide[k], self.inside[k], 2)
            hid = 1 - smoothstep(a - 0.5, a, b)
            g = 1 + 0.18 * lift
            if b > CREEP[2][1]:              # leaning in to look
                c += 6 * np.sin(np.pi * (b - CREEP[2][1]) / 2) * (1 if k < 2 else -1)
            dr = 1.0 if k < 2 else -1.0
        elif b < POP:
            if b < SNAP + 0.5:
                c = self.inside[k]
                g = 1 + 0.5 * hump(b, SNAP, SNAP + 0.5)
                eye = 1.6
            else:
                c, dr = self.ricochet(k, t)
                eye = 1.4
            I = 1.1
        elif b < SCAMPER[0]:
            x, _ = self.ricochet(k, bt(POP))
            c = lerp(x, self.dance[k], _back((b - POP) / 1.0))
            g = 1 + 0.6 * hump(b, POP, POP + 0.6)
            I = 1 + 0.4 * hump(b, POP, POP + 0.8)
            q = b - DANCE[0]
            j, f = int(q), q - int(q)
            if 1 <= q < 4:                   # hops, the bat answering
                if (j % 2 == 0) == (k == 1):
                    g = 1 + 0.4 * hump(f, 0, 0.6)
            elif 4 <= q < 8:                 # mirrored sway; the bat flaps big
                sw = 24 * (1 if j % 2 == 0 else -1) * (1 if k == 0 else -1)
                c += sw * smoothstep(0, 0.3, f) if k != 1 else 0
                if k == 1:
                    flap = 1 + 0.5 * hump(f, 0, 0.5)
            elif 8 <= q < 11:
                g = 1 + 0.35 * hump(f, 0, 0.55)
            elif q >= 11:                    # the big kick
                g = 1 + 0.7 * hump(f, 0, 0.7)
                I = 1.2
            dr = -1.0 if k == 2 else 1.0
        else:                                # the getaway and the peeks are staged in kid()
            c = self.dance[k]
        return c, dr, g, I, eye, hid, flap

    def present(self, t):
        """Where the present is (None if nowhere): under the porch light, carried, then in the cage."""
        b = (t - T0) / BEAT
        if b < PRESENT[0] + 1 or b >= POP:
            return None
        if b < PRESENT[0] + 2:
            return self.porch
        if b < PRESENT[1] - 0.5:
            c, dr = self.kid(1, t)[:2]
            return c + dr * 34
        return self.cx


def render(G, seed=17):
    rng = np.random.default_rng(seed)
    S = Show(G)
    L = G.length
    pdp = G.pd[G.path]
    w = np.gradient(pdp)
    e0, e1 = pdp - w / 2, pdp + w / 2
    names = list(COL)
    ci = {k: i for i, k in enumerate(names)}
    NC = 90
    cv = rng.uniform(150, 950, NC) * rng.choice([-1, 1], NC)
    clife = rng.uniform(1.6, 3.2, NC)
    ccol = rng.integers(0, len(CONFETTI), NC)
    ctw = rng.uniform(0, 2 * np.pi, NC)
    tp = bt(POP)
    hits = [S.hits(k) for k in range(3)]
    F = nframes(D)
    out = np.zeros((F, G.N, 3))

    for fi in range(F):
        t = fi * DT
        b = (t - T0) / BEAT
        spans = []

        def put(a, z, I, col):
            spans.append((min(a, z), max(a, z), I, ci[col]))

        # the three of them
        for k, kd in enumerate(KIDS):
            c, dr, g, I, eye, hid, flap = S.kid(k, t)
            if not (-80 < c < L + 80) or t < T0:
                continue
            half = kd['L'] / 2
            body_I = I * (1 - 0.88 * hid)
            for q, (v0, v1, wt, col) in enumerate(kd['parts']):
                if k == 1 and q != 1:        # wings flap: they grow and shrink from the body
                    if q == 0:
                        v0 = 20 - (20 - v0) * flap
                    else:
                        v1 = 40 + (v1 - 40) * flap
                a, z = c + dr * g * (v0 - half), c + dr * g * (v1 - half)
                put(a, z, body_I * wt, col)
            for v0, v1 in kd['eyes']:
                vm, vh = (v0 + v1) / 2, (v1 - v0) / 2 * eye
                a, z = c + dr * g * (vm - vh - half), c + dr * g * (vm + vh - half)
                blink = ((t + 0.37 * k) % 3.1) < 0.12
                put(a, z, -1.2 * body_I, kd['body'])
                if hid > 0.05 and not blink:
                    put(a, z, 0.9 * hid, 'white')
                elif kd['glow'] and not blink:
                    put(a, z, 0.55 * I, kd['glow'])

        # the cage: built a part a beat, the gate held up, slammed, rattled, blown apart
        for i, x in enumerate(S.cage):
            tb = bt(BUILD + i)
            if t < tb or t > tp + 2.0:
                continue
            gate = i == len(S.cage) - 1
            hw = 5.0 if i in (0, len(S.cage) - 1) else 2.6
            I = 0.75 if hw > 3 else 0.55
            I += 0.6 * np.exp(-(t - tb) / 0.15)
            if gate and t < bt(SNAP):
                I = 0.22 + 0.08 * np.sin(2 * np.pi * 1.5 * t)
            if bt(SNAP) <= t < tp:
                I = (0.85 if hw > 3 else 0.6) + 0.5 * np.exp(-(t - bt(SNAP)) / 0.2)
                I *= 0.85 + 0.15 * np.sin(37 * t + 2.1 * i)
            xx = x
            if t >= tp:
                u = t - tp
                xx = x + S.flyv[i] * 0.45 * (1 - np.exp(-u / 0.45))
                I *= max(0.0, 1 - u / 2.0)
            put(xx - hw, xx + hw, I, 'steel')
        for hk in hits:                      # walls flash where they are hit
            for th, xw in hk:
                if th <= t < th + 0.3:
                    put(xw - 8, xw + 8, 0.7 * np.exp(-(t - th) / 0.08), 'white')

        # the present
        px = S.present(t)
        if px is not None:
            sp = 0.25 * (1 + np.sin(2 * np.pi * 1.7 * t)) if b >= PRESENT[1] - 0.5 else 0.0
            put(px - 15, px + 15, 0.85, 'red')
            put(px - 2.5, px + 2.5, 0.9 + sp, 'gold')
            put(px - 2.5, px + 2.5, -0.85, 'red')
        if tp <= t < tp + 3.5:               # it goes off like a party popper
            u = t - tp
            put(S.cx - 40 - 250 * u, S.cx + 40 + 250 * u, 0.8 * np.exp(-u / 0.12), 'white')
            x = S.cx + cv / 1.6 * (1 - np.exp(-1.6 * u))
            for j in range(NC):
                if u < clife[j]:
                    a = (1 - u / clife[j]) * (0.65 + 0.35 * np.sin(14 * u + ctw[j]))
                    put(x[j] - 4, x[j] + 4, a, CONFETTI[ccol[j]])

        # paint
        sp = np.array(spans) if spans else np.zeros((0, 4))
        ov = np.clip(np.minimum(sp[:, 1:2], e1) - np.maximum(sp[:, 0:1], e0), 0, None) / w
        buf = np.zeros((G.N, 3))
        lit = np.zeros(G.N)
        for i, name in enumerate(names):
            m = sp[:, 3] == i
            if m.any():
                Ii = sp[m, 2] @ ov[m]
                buf += light(COL[name], np.clip(Ii, 0, 1))
                lit += np.clip(Ii, 0, 1)

        # the neighbourhood at night: moonlight on the whole roof, the porch light, a few jack-o'-lanterns;
        # the lamp sweeps, the party, the ta-da
        night = keys(t, [(0, 0), (1.5, 1), (D - 2.5, 1), (D, 0)])
        free = 1 - np.clip(lit, 0, 1)
        moon = 0.14 * (1 + 0.12 * np.sin(pdp / 180 + 0.2 * t))
        porch = 0.2 * np.exp(-((pdp - S.porch) / 150) ** 2)
        jack = sum(0.22 * (1 + 0.2 * np.sin(2 * np.pi * (1.3 + 0.4 * j) * t + j)) * np.exp(-((pdp - x) / 6) ** 2)
                   for j, x in enumerate(S.lanterns))
        buf += (light(NIGHT, night * moon * free) + light(PORCH, night * porch * free) +
                light(COL['orange'], night * jack * free))
        for (a, z), (x0, x1) in zip(FREEZES, S.beams):
            ta, tz = bt(a + 0.3), bt(z - 0.3)
            if ta - 0.5 <= t < tz + 0.5:
                env = smoothstep(ta - 0.5, ta, t) * (1 - smoothstep(tz, tz + 0.5, t))
                bx = lerp(x0, x1, smoothstep(ta, tz, t))
                buf += light(COL['lamp'], 0.5 * env * np.exp(-((pdp - bx) / 60) ** 2))
        if DANCE[0] <= b < DANCE[1]:
            q = b - DANCE[0]
            wash = 0.1 * np.exp(-(q % 1) * BEAT / 0.15) * smoothstep(0, 1, q)
            col = [COL['orange'], COL['purple'], COL['mint']][int(q) % 3]
            buf += light(col, wash * np.ones(G.N))
        if b >= TADA:
            u = t - bt(TADA)
            fl = 0.8 * np.exp(-u / 0.5)
            third = np.minimum((pdp / L * 3).astype(int), 2)
            for j, name in enumerate(('purple', 'orange', 'white')):
                buf += light(COL[name], fl * (third == j))
            buf *= keys(t, [(D - 2.0, 1), (D, 0)])
        out[fi][G.path] = np.clip(buf, 0, 1)
    return out


# ---------------------------------------------------------------- music ----------------------------------------------
# A schoolyard taunt in E minor at the lights' 120 BPM, swung. TUNE is the hook (pumpkin on clarinet, the bat on a
# kazoo-ish buzz trombone, the ghost on flute). The tiptoeing is pizzicato a pluck a step, and the band stops dead when
# the lamp sweeps. Every gag below is a moment in Show: shoves, the hop, the squash and pop, the cage parts going up
# (each bar a note), the present, the peeks, the snap, the ricochets off the walls, the party popper, the victory
# dance in E major, the getaway and the ta-da. Sounds are panned to where they happen.

TUNE = [                                    # (beat, note, beats): the hook, four bars
    (0, 'E5', .5), (.5, 'D5', .5), (1, 'B4', 1), (2, 'E5', .5), (2.5, 'D5', .5), (3, 'B4', 1),
    (4, 'G4', .5), (4.5, 'A4', .5), (5, 'B4', .5), (5.5, 'D5', .5), (6, 'C5', 1), (7, 'B4', 1),
    (8, 'E5', .5), (8.5, 'D5', .5), (9, 'B4', 1), (10, 'E5', .5), (10.5, 'D5', .5), (11, 'B4', .5), (11.5, 'G4', .5),
    (12, 'A4', .5), (12.5, 'B4', .5), (13, 'G4', .5), (13.5, 'F#4', .5), (14, 'E4', 2)]
HALVES = ['Em', 'Em', 'Am', 'C', 'Em', 'Em', 'B7', 'Em']     # a chord every half bar under TUNE
CHORD = {'Em': ('E3', 'G3', 'B3'), 'Am': ('E3', 'A3', 'C4'), 'C': ('E3', 'G3', 'C4'), 'B7': ('D#3', 'F#3', 'A3'),
         'E': ('E3', 'G#3', 'B3'), 'A': ('E3', 'A3', 'C#4'), 'B': ('D#3', 'F#3', 'B3')}
ROOT = {'Em': ('E2', 'B1'), 'Am': ('A1', 'E2'), 'C': ('C2', 'G1'), 'B7': ('B1', 'F#2'), 'E': ('E2', 'B1'),
        'A': ('A1', 'E2'), 'B': ('B1', 'F#2')}
MAJOR = {'G': 'G#', 'C': 'C#', 'D': 'D#'}  # the hook in E major for the victory dance
BARS = ['E4', 'G4', 'A4', 'B4', 'D5', 'E5', 'G5']   # the cage's bars, a note each


def swing(b):
    """Swung eighths: the off-beat eighth lands two thirds of the way through the beat."""
    j, f = int(np.floor(b)), b - np.floor(b)
    return j + (f * 4 / 3 if f < 0.5 else 2 / 3 + (f - 0.5) * 2 / 3)


def score(M, G):
    from pixelhome.audio import SR, note, slide, whoosh
    n = note
    S = Show(G)
    clar = M.sampler('Woodwinds/Clarinet/stac/*.wav', tune=-12)
    clar_l = M.sampler('Woodwinds/Clarinet/susLong/*.wav', tune=-12)
    buzz = M.sampler('Brass/OldTrombone/Buzz/*.wav', tune=-12)
    flute = M.sampler('Woodwinds/Flute/stac/*.wav', tune=-12)
    bsn = M.sampler('Woodwinds/Bassoon/stac/*.wav', tune=-12)
    pizz = M.sampler('Strings/Cello Section/pizzT/*.wav', tune=-12)
    bass = M.sampler('Strings/Solo Contrabass/Pizz/*.wav', tune=-12)
    tuba = M.sampler('Brass/Tuba/stac/*.wav', tune=-12)
    bone = M.sampler('Brass/Tenor Trombone/stac/*.wav', tune=-12)
    trem = M.sampler('Strings/Violin Section/Trem/*.wav', tune=-12)
    glock = M.sampler('Percussion/Glock/*.wav', tune=-12)
    xylo = M.sampler('Percussion/Xylo/*.wav', tune=-12)
    snare = M.hits('Percussion/Snare2-HitSN_v[13]*.wav')
    snare_f = M.hits('VSCO 1 Percussion/drums/snare/drum3_marching/snare3_f*.wav')
    sroll = M.hits('Percussion/Snare2-rollSN_v[35]*.wav')
    shaker = M.hits('VSCO 1 Percussion/varWood/maraca[1-5].wav')
    bd = M.hits('VSCO 1 Percussion/drums/bass/bdrum_f_*.wav')
    bd_ff = M.hits('VSCO 1 Percussion/drums/bass/bdrum_fff_*.wav')
    crash = M.hits('VSCO 1 Percussion/varMetal/Cymbals/clash/crash_hit_ff*.wav')
    choke = M.hits('Percussion/cymbal-crashshort*.wav')
    timp = M.hits('Percussion/Timpani/Timpani1_Hit*.wav')
    troll = M.hits('Percussion/Timpani/Rolls/*.wav')
    wood = M.hits('VSCO 1 Percussion/varWood/wood_click*.wav')
    clave = M.hits('Percussion/Claves1_Hit*.wav')
    slap = M.hits('VSCO 1 Percussion/varWood/slapstick[0-9].wav')
    brake = M.hits('Percussion/BrakeDrum1_Hammer*.wav')
    cow = M.hits('Percussion/Cowbell1_Hit*.wav')
    ratchet = M.hits('Percussion/Ratchet1-Crank*.wav')
    belltree = M.hits('Percussion/BellTree_Stroke*.wav')

    for name, gain, rev in (('lead', 0.3, 0.18), ('kazoo', 0.2, 0.15), ('pizz', 0.34, 0.12), ('bass', 0.42, 0.06),
                            ('drums', 0.3, 0.12), ('mallet', 0.26, 0.2), ('fx', 0.2, 0.2), ('perc', 0.4, 0.12),
                            ('hold', 0.16, 0.3)):
        M.bus(name, gain=gain, reverb=rev)

    order = np.argsort(G.pd)
    xs, ds = G.pos[order, 0], G.pd[order]
    x0, x1 = xs.min(), xs.max()

    def pan_at(d):                          # path distance -> left/right across the facade, from the street
        x = np.interp(np.clip(d, 0, G.length), ds, xs)
        return float(0.85 * (2 * (x - x0) / (x1 - x0) - 1))

    def kid_pan(k, t):
        return pan_at(S.kid(k, t)[0])

    def at(b):                              # swung beat -> seconds
        return bt(swing(b))

    def mono(sig, pans):                    # a mono signal panned sample by sample
        a = (np.clip(pans, -1, 1) + 1) * np.pi / 4
        return np.vstack([sig * np.cos(a), sig * np.sin(a)]) * np.sqrt(2)

    def hook(inst, b0, bus, vel, gain=1.0, pan=None, shift=0, major=False, skip=(), dur=0.9):
        for b, m, ln in TUNE:
            if any(a <= b0 + b < z for a, z in skip):
                continue
            if major and m[:-1] in MAJOR:
                m = MAJOR[m[:-1]] + m[-1]
            t = at(b0 + b)
            p = pan(t) if callable(pan) else (0.0 if pan is None else pan)
            M.add(bus, inst.play(n(m) + shift, vel, dur=ln * BEAT * dur), t, gain, p)

    def half_chord(b, b0, major=False):
        c = HALVES[int((b - b0) // 2) % 8]
        return {'Em': 'E', 'Am': 'A', 'C': 'A', 'B7': 'B'}.get(c, c) if major else c

    def groove(b0, b1, chords, vel=96, snare_on=True):
        """The shuffle: bass on one and three, offbeat pizz chords, brushes on two and four, a swung shaker."""
        for b in range(b0, b1):
            c = chords(b)
            M.add('bass', (tuba if b % 2 == 0 else bass).play(n(ROOT[c][(b // 2) % 2]), vel), at(b), 0.9)
            for m in CHORD[c]:
                M.add('pizz', pizz.play(n(m), vel - 22), at(b + 0.5), 0.4, -0.3)
            if snare_on and b % 2 == 1:
                M.add('drums', snare.play(vel), at(b), 0.8, 0.15)
            M.add('perc', shaker.play(64), at(b), 0.35, 0.3)
            M.add('perc', shaker.play(80), at(b + 0.5), 0.45, 0.3)

    # ---- the pickup and the scurry in: a pizz run with them ----
    M.add('pizz', bass.play(n('B1'), 100), 1.0, 1.0)
    M.add('drums', snare.play(80), 1.5, 0.7)
    for i, m in enumerate(('E3', 'F#3', 'G3', 'A3', 'B3', 'C4', 'B3', 'A3', 'G3', 'A3', 'B3', 'D4', 'E4', 'D4', 'B3', 'G3')):
        t = bt(i / 2)
        M.add('pizz', pizz.play(n(m), 84), t, 0.8, kid_pan(0, t))
    for b in range(0, 8, 2):
        M.add('bass', bass.play(n('E2'), 90), bt(b), 0.8)

    # ---- tiptoeing: a pluck a step, the hook down low, the band stopping dead for the lamp ----
    for s in SNEAK_STEPS:
        t = bt(s)
        M.add('pizz', pizz.play(n(['E3', 'G3', 'B3', 'G3'][s % 4]), 92), t, 0.9, kid_pan(1, t))
        M.add('bass', bass.play(n('E2' if s % 2 == 0 else 'B1'), 88), t, 0.8)
    hook(clar, SNEAK[0], 'lead', 78, 0.8, pan=lambda t: kid_pan(0, t), shift=-12, skip=FREEZES)
    for a, z in FREEZES:
        M.add('lead', bsn.play(n('G3'), 96, dur=0.22), bt(a), 0.9, kid_pan(1, bt(a)))
        M.add('lead', bsn.play(n('E3'), 90, dur=0.5), bt(a + 0.5), 0.9, kid_pan(1, bt(a)))
        M.add('hold', trem.play(n('B4'), 40, dur=(z - a - 0.6) * BEAT), bt(a + 0.6), 0.6)
        ta, tz = bt(a + 0.3), bt(z - 0.3)
        tt = np.linspace(0, 1, int((tz - ta) * SR))
        sweep = whoosh(tz - ta, 500, 900, 0.5, seed=a)[0]
        x = S.beams[0] if a == FREEZES[0][0] else S.beams[1]
        M.add('fx', mono(sweep, np.array([pan_at(lerp(*x, smoothstep(0, 1, u))) for u in tt])), ta, 0.7)
        M.add('mallet', glock.play(n('E5'), 70), bt(z), 0.5, kid_pan(0, bt(z)))
    late = FREEZES[1][0]                     # the ghost's late step bumps them along
    M.add('perc', wood.play(110, pitch=-4), bt(late + 0.15), 1.0, kid_pan(1, bt(late)))
    M.add('perc', wood.play(100, pitch=3), bt(late + 0.3), 0.8, kid_pan(0, bt(late)))
    M.add('fx', slide(0.0, 0.12, 900, 1500, 0.14, 0.5), bt(late + 0.15), 0.6, kid_pan(1, bt(late)))

    # ---- the scurry up to the porch: xylophone up the scale under them, into a snare roll ----
    for i, m in enumerate(('E4', 'F#4', 'G4', 'A4', 'B4', 'C5', 'D5', 'E5')):
        t = bt(SCURRY_UP[0] + i / 2)
        M.add('mallet', xylo.play(n(m), 96), t, 0.8, kid_pan(0, t))
    r = sroll.play(80, dur=1.0)
    M.add('drums', r * np.linspace(0.2, 1, r.shape[1]) ** 2, bt(SCURRY_UP[1] - 2), 0.4)

    # ---- the squabble: the hook traded between them over the shuffle; shoves, the hop, the squash ----
    groove(BICKER[0], BICKER[1], lambda b: half_chord(b, BICKER[0]))
    trades = [(0, clar, 'lead', 0), (4, buzz, 'kazoo', 1), (8, clar, 'lead', 0)]
    for off, inst, bus, k in trades:
        for b, m, ln in TUNE:
            if off <= b < off + 4:
                t = at(BICKER[0] + b)
                M.add(bus, inst.play(n(m) - (12 if inst is buzz else 0), 100, dur=ln * BEAT * 0.9), t, 1.0,
                      kid_pan(k, t))
    for b, k in ((SHOVE1, 0), (SHOVE2, 1), (SHOVE2 + 0.2, 2)):
        t = bt(b)
        p = kid_pan(k, t)
        M.add('fx', slide(0.0, 0.1, 700, 1400, 0.24, 0.5), t, 0.7, p)
        M.add('fx', slide(0.12, 0.24, 1400, 600, 0.24, 0.5), t, 0.5, p)
        M.add('perc', wood.play(115, pitch=-3 * k), t, 1.0, p)
    th, ts = bt(HOP), bt(SQUASH)            # the hop over: up and down a slide whistle
    M.add('fx', slide(0.0, (ts - th) / 2, 600, 1600, ts - th, 0.5), th, 0.8, kid_pan(0, (th + ts) / 2))
    M.add('fx', slide((ts - th) / 2, ts - th, 1600, 500, ts - th + 0.02, 0.5), th, 0.8, kid_pan(0, ts))
    p = kid_pan(2, ts)
    M.add('perc', slap.play(127), ts, 1.0, p)
    M.add('drums', bd_ff.play(120), ts, 0.9, p)
    M.add('kazoo', buzz.play(n('E2'), 120, dur=0.7), ts, 1.0, p)
    for i in range(10):                     # the bat laughs
        t = ts + 0.15 + i * BEAT / 3
        M.add('mallet', glock.play(n(['B5', 'G5'][i % 2]), 80), t, 0.4, kid_pan(1, t))
    tu = bt(UNSQUASH)                        # the ghost pops back up and the pumpkin goes flying
    M.add('fx', slide(0.0, 0.18, 300, 2000, 0.2, 0.4), tu, 0.8, kid_pan(2, tu))
    M.add('drums', choke.play(100), tu, 0.6, kid_pan(2, tu))
    M.add('perc', clave.play(118), tu + 0.35, 0.8, kid_pan(0, tu + 0.35))

    # ---- the dash to the right wing ----
    for i, m in enumerate(('B3', 'D4', 'E4', 'G4', 'A4', 'B4', 'D5', 'E5')):
        t = bt(SCURRY_R[0] + i / 2)
        M.add('mallet', xylo.play(n(m), 96), t, 0.8, kid_pan(0, t))
    for b in range(*SCURRY_R):
        M.add('bass', bass.play(n(['E2', 'G2', 'A2', 'B2'][b % 4]), 96), bt(b), 0.9)

    # ---- the chorus: building the cage, the hook in full; each part is a hit where it goes up ----
    groove(BUILD, PRESENT[1], lambda b: half_chord(b, BUILD), vel=104)
    hook(clar, BUILD, 'lead', 108, 1.0, 0.1)
    hook(buzz, BUILD, 'kazoo', 104, 1.0, -0.1, shift=-12)
    hook(glock, BUILD, 'mallet', 70, 0.35, 0.2)
    for i, x in enumerate(S.cage):
        t = bt(BUILD + i)
        p = pan_at(x)
        if i in (0, len(S.cage) - 1):
            M.add('perc', brake.play(110), t, 0.9, p)
            if i:
                M.add('perc', ratchet.play(90, dur=0.4), t + 0.05, 0.7, p)
        else:
            M.add('mallet', xylo.play(n(BARS[i - 1]), 112), t, 1.0, p)
    for b in (BUILD + 10, BUILD + 11):       # proud of it
        M.add('perc', cow.play(100), bt(b), 0.7, pan_at(S.cx))
    # the bat goes to the porch light for the present and brings it back
    tb0, tb1 = bt(PRESENT[0]), bt(PRESENT[0] + 1.5)
    M.add('fx', whoosh(tb1 - tb0, 600, 2400, 0.5, seed=7), tb0, 0.6, pan_at((S.cx + S.porch) / 2))
    M.add('perc', belltree.play(100), bt(PRESENT[0] + 1), 0.6, pan_at(S.porch))
    tr0, tr1 = bt(PRESENT[0] + 2), bt(PRESENT[1] - 0.5)
    M.add('fx', whoosh(tr1 - tr0, 2400, 700, 0.5, seed=8), tr0, 0.6, pan_at((S.cx + S.porch) / 2))
    for m in ('E5', 'G5', 'B5', 'E6'):
        M.add('mallet', glock.play(n(m), 90), tr1, 0.5, pan_at(S.cx))

    # ---- hiding: the band drops out to a tick-tock; each peek is a little "hm?" ----
    for b in range(HIDE[0], CREEP[0][0]):
        M.add('perc', wood.play(70 if b % 2 else 85, pitch=0 if b % 2 else 5), bt(b), 0.6, pan_at(S.cx + HW))
    for i in range(3):
        t = bt(HIDE[0] + i / 2)
        M.add('pizz', pizz.play(n(['B3', 'G3', 'E3'][i]), 80), t, 0.8, kid_pan(i, t))
    M.add('hold', trem.play(n('E4'), 38, dur=7 * BEAT), bt(HIDE[0] + 1), 0.6, pan_at(S.cx + HW))
    for k, (inst, base) in enumerate(((clar, 'B4'), (buzz, 'B3'), (flute, 'B4'))):
        t = bt(PEEKS[k])
        M.add('lead' if k != 1 else 'kazoo', inst.play(n(base), 90, dur=0.2), t, 0.9, kid_pan(k, t))
        M.add('lead' if k != 1 else 'kazoo', inst.play(n(base) + 5, 96, dur=0.35), t + 0.25, 0.9, kid_pan(k, t))
    M.add('pizz', bass.play(n('E2'), 90), bt(PEEKS[2] + 1), 0.8)
    M.add('pizz', bass.play(n('B1'), 80), bt(PEEKS[2] + 1.5), 0.8)

    # ---- creeping in, one by one: rising plucks, a snare roll to the snap ----
    j = 0
    for k, (a, z) in enumerate(CREEP):
        for s in (a, a + 1):
            t = bt(s)
            M.add('pizz', pizz.play(n('E3') + j, 96), t, 1.0, kid_pan(k, t))
            M.add('bass', bass.play(n('E2') + j, 90), t, 0.7)
            j += 1
    r = sroll.play(90, dur=bt(SNAP) - bt(CREEP[2][0]))
    M.add('drums', r * np.linspace(0.1, 1, r.shape[1]) ** 2, bt(CREEP[2][0]), 0.6)
    r = troll.play(80, dur=bt(SNAP) - bt(CREEP[2][1]))
    M.add('drums', r * np.linspace(0.1, 1, r.shape[1]) ** 2, bt(CREEP[2][1]), 0.6)

    # ---- SNAP: the gate; they ricochet off the walls; a panicky half-step in the bass ----
    tsn = bt(SNAP)
    pg = pan_at(S.cage[-1])
    M.add('perc', brake.play(127), tsn, 1.2, pg)
    M.add('perc', slap.play(127), tsn, 1.0, pg)
    M.add('drums', crash.play(118), tsn, 0.8, pg)
    M.add('drums', bd_ff.play(127), tsn, 1.0)
    for m in ('E2', 'F2', 'A#2'):
        M.add('kazoo', bone.play(n(m), 120, dur=0.5), tsn, 0.7)
    for k in range(3):
        for i, (th, xw) in enumerate(S.hits(k)):
            M.add('perc', (wood if i % 2 else clave).play(105, pitch=2 * k - (i % 3)), th, 0.8, pan_at(xw))
    for b in range(SNAP + 1, POP):
        M.add('bass', tuba.play(n('E2') + (b % 2), 100), bt(b), 0.9)
        M.add('drums', snare.play(90), bt(b + 0.5), 0.6)
    for i in range(int((POP - SNAP - 1) * 4)):
        t = bt(SNAP + 1 + i / 4)
        M.add('lead', clar.play(n('B4') + [0, 1, 0, -1][i % 4] + (i // 8) * 2, 84, dur=0.1), t, 0.6, 0.1)

    # ---- POP: the present goes off, the cage flies apart ----
    tp = bt(POP)
    pc = pan_at(S.cx)
    M.add('drums', crash.play(127), tp, 1.0, pc)
    M.add('drums', bd_ff.play(127), tp, 1.1, pc)
    M.add('drums', timp.play(127), tp, 0.9, pc)
    M.add('fx', slide(0.0, 0.25, 500, 2200, 0.3, 0.4), tp, 0.8, pc)
    for i in range(16):                     # confetti
        side = -1 if i % 2 else 1
        M.add('mallet', glock.play(n('E6') - 2 * (i // 2) - int(M.rng.integers(0, 2)), 100 - 3 * i), tp + 0.05 * i,
              0.5, pan_at(S.cx + side * 70 * i))
    for i, x in enumerate(S.cage):           # cage bars clattering off
        M.add('perc', wood.play(90, pitch=float(M.rng.uniform(-4, 6))), tp + 0.1 + 0.05 * i, 0.5,
              pan_at(x + S.flyv[i] * 0.3))

    # ---- the victory dance: the hook in E major, everyone together ----
    groove(DANCE[0], DANCE[1], lambda b: half_chord(b, DANCE[0], True), vel=110)
    hook(clar, DANCE[0], 'lead', 112, 1.0, 0.0, major=True)
    hook(buzz, DANCE[0], 'kazoo', 108, 1.0, -0.2, shift=-12, major=True)
    hook(flute, DANCE[0], 'lead', 96, 0.6, 0.25, major=True)
    hook(glock, DANCE[0], 'mallet', 80, 0.4, 0.2, major=True)
    for b in range(DANCE[0], DANCE[1]):
        M.add('drums', bd.play(100), bt(b), 0.6)
        q = b - DANCE[0]
        if 1 <= q < 4:
            k = 1 if q % 2 else 0
            M.add('perc', cow.play(96), bt(b), 0.5, kid_pan(k, bt(b)))
            if k == 0:
                M.add('perc', cow.play(96), bt(b), 0.5, kid_pan(2, bt(b)))
        elif 8 <= q < 11:
            M.add('perc', clave.play(110), bt(b), 0.6)
    tk = bt(DANCE[0] + 11)
    M.add('drums', crash.play(118), tk, 0.8)
    M.add('perc', slap.play(120), tk, 0.9)

    # ---- the getaway: giggles that run with them; a slide whistle as the ghost slips away round the side ----
    for k in range(3):
        a = SCAMPER[0] + (k if k < 2 else 0)
        z = a + 6 if k < 2 else SCAMPER[0] + 4
        t = bt(a)
        while t < bt(z):
            d = S.kid(k, t)[0]
            if not (-30 < d < G.length + 30):
                break
            for q, m in enumerate(('E6', 'C#6', 'E6')):
                M.add('mallet', glock.play(n(m) - 5 * k, 74), t + q * 0.08, 0.35, pan_at(d))
            t += 0.55 + 0.1 * k
    t0, t1 = bt(SCAMPER[0]), bt(SCAMPER[0] + 4)
    tt = np.linspace(t0, t1, int((t1 - t0) * SR))
    f = 1500 * 2 ** (-1.2 * (tt - t0) / (t1 - t0)) * (1 + 0.03 * np.sin(2 * np.pi * 6 * (tt - t0)))
    ph = 2 * np.pi * np.cumsum(f) / SR
    sig = 0.25 * np.sin(ph) * np.clip((tt - t0) / 0.05, 0, 1) * np.clip((t1 - tt) / 0.1, 0, 1)
    pans = np.array([kid_pan(2, x) for x in np.linspace(t0, t1, 64)])
    M.add('fx', mono(sig, np.interp(np.linspace(0, 1, len(tt)), np.linspace(0, 1, 64), pans)), t0, 0.5)
    for b in range(*SCAMPER):
        c = ['E', 'A', 'B', 'E'][(b - SCAMPER[0]) // 2 % 4]
        M.add('bass', tuba.play(n(ROOT[c][b % 2]), 96), bt(b), 0.8)
        M.add('drums', snare.play(84), bt(b + 0.5), 0.5)

    # ---- peek, and ta-da ----
    for k in range(3):
        t = bt(PEEK + 0.5 + 0.25 * k)
        M.add('mallet', glock.play(n(['B5', 'G#5', 'E5'][k]), 90), t, 0.6, kid_pan(k, t))
    tt = bt(TADA)
    M.add('fx', slide(0.0, 0.2, 700, 1800, 0.22, 0.4), tt - 0.22, 0.6)
    for m in ('E4', 'G#4', 'B4', 'E5'):
        M.add('lead', clar_l.play(n(m), 110, dur=2.2), tt, 0.5)
    for m in ('E3', 'B3'):
        M.add('kazoo', buzz.play(n(m) - 12, 116, dur=1.2), tt, 0.8)
    M.add('bass', tuba.play(n('E2'), 124), tt, 1.2)
    M.add('mallet', glock.play(n('E5'), 110), tt, 0.7)
    M.add('mallet', xylo.play(n('E5'), 110), tt, 0.7)
    M.add('drums', crash.play(124), tt, 1.0)
    M.add('drums', bd_ff.play(124), tt, 1.0)
    M.add('drums', timp.play(120), tt, 0.8)
