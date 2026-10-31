"""Special Delivery: the Pumpkin King's Christmas Eve rounds over the human world, and how it goes down.

A snowy night over a sleeping town: deep blue sky, snow twinkling, four houses glowing a sleepy warm along the front
(two on the right wing, one on the porch, one on the left wing). The coffin sleigh gallops in from the free end of
Right behind the ghost dog's nose, sleigh bells on every beat and the citizens' march turned into a gleeful drive.
At each house it pulls up: a present drops down the chimney (a gold streak and a thump), the house lights up
warm, the present jiggles, and pops open: a green snake slithers out along the roof, a jack-in-the-box springs a
leering green head up and down on its spring, a bat flaps off toward the back of the house, a hungry wreath chomps.
Each house screams, flashing red and white, and the red runs along its run. Then the alarm spreads: sirens wail, the
houses flash police red and blue, and three searchlights sweep the sky back and forth. The sleigh comes round
again from the right end on a victory lap, the king throwing gold sparks on every downbeat, sure they're all
delighted, while the beams chase after him, and he heads away down Side as the first flak bursts behind him.

compose() lays the music end to end (pixelhome/nightmare.py); render() and score() read its marks and events, and
the deliveries' times (HOUSES) are shared by both."""
import numpy as np
from pixelhome.fx import DT, nframes, light, smoothstep, keys, hexc
from pixelhome.nightmare import (Chart, Band, Stage, pulse, PUMPKIN, SLIME, VIOLET, BONE, WHITE, GOLD, RED, WARM,
                                 NIGHT, ICE, BLUE, GREEN, MOON)

CODE = 'NM15'
TITLE = 'Special Delivery'
KIND = 'show'
DESCRIPTION = ('The Pumpkin King drops presents down four chimneys along the roof, and each one pops open and the '
               'house screams. Then the sirens start and searchlights sweep the house, while he waves, delighted.')
VOICEOVER = ('Over the sleeping houses, the Pumpkin King made his rounds, with a very special present for '
             'every child.')

BPM = 150
BEAT = 60 / BPM
POLICE_BLUE = hexc('#1030ff')
BEAM = hexc('#d8e8ff')
SNAKE = hexc('#40ff30')
WREATH = hexc('#00c040')
GLOW = {'snake': SNAKE, 'jack': SLIME, 'bat': VIOLET, 'wreath': WREATH}



class Offstage(Stage):
    """The shared Stage, but a sprite whose centre is past either free end is drawn partly or not at all instead of
    being clamped onto the end pixel, so things can walk in and out of the ends."""

    def sprite(self, fr, p, pixels, lvl=1.0, facing=1, cut=True):
        if lvl <= 0:
            return fr
        if p < self.pp[0]:
            k0 = int(np.floor((p - self.pp[0]) / 6.1))
        elif p > self.pp[-1]:
            k0 = self.N - 1 + int(np.ceil((p - self.pp[-1]) / 4.0))
        else:
            k0 = self.k(p)
        offs = [o for o, _, _ in pixels]
        if cut:
            for o in range(min(offs) - 1, max(offs) + 2):
                k = k0 + facing * o
                if 0 <= k < self.N:
                    fr[self.path[k]] *= 1 - min(1.0, lvl * 1.5) * (0.9 if min(offs) <= o <= max(offs) else 0.5)
        for o, col, v in pixels:
            k = k0 + facing * o
            if 0 <= k < self.N and col is not None:
                fr[self.path[k]] += light(col, lvl * v)
        return fr


def compose():
    C = Chart()
    C.rest(0.8)
    C.mark('sleep')
    C.play('wonder', style='arp', bars=(0, 2), bpm=300, tag='sleep')     # the town asleep under the snow
    C.mark('fly1')
    C.play('town', style='drive', bpm=BPM, tag='fly1')                 # two houses on the right wing
    C.mark('fly2')
    C.play('town', style='drive', bpm=BPM, transpose=2, tag='fly2')    # the porch and the left wing
    C.mark('alarm')
    C.play('town', style='drive', bpm=160, transpose=2, tag='alarm')   # sirens, searchlights, a victory lap
    C.play('town', style='drive', bars=(4, 8), bpm=160, transpose=2, tag='alarm')
    C.rest(2.2)
    C.mark('end')
    return C


C = compose()
M = C.marks
D = M['end']
# the deliveries: (run, u along it, arrives, gift); the present pops 6 beats after he arrives
HOUSES = [('Right', 0.72, M['fly1'] + 5 * BEAT, 'snake'), ('Right', 0.25, M['fly1'] + 17 * BEAT, 'jack'),
          ('Porch Front', 0.5, M['fly2'] + 3 * BEAT, 'bat'), ('Left', 0.55, M['fly2'] + 17 * BEAT, 'wreath')]
POP = 6 * BEAT
DROP = 1.2 * BEAT
LAP = (M['alarm'] + 4.5, M['end'] - 1.6)        # the victory lap: in from the right end, away down Side


def track(S, t):
    """Where the sleigh's nose is (or None while it is off the house)."""
    L = S.L
    hp = [S.at(r, u) for r, u, _, _ in HOUSES]
    if t < M['fly1']:
        return None
    if t < M['alarm']:
        pts = [(M['fly1'], L + 20)]
        for (r, u, ta, _), p in zip(HOUSES, hp):
            pts += [(ta, p), (ta + 2 * BEAT, p - 15)]
        pts.append((M['alarm'] - 0.3, -260))
        return float(keys(t, pts))
    if LAP[0] <= t <= LAP[1]:
        u = (t - LAP[0]) / (LAP[1] - LAP[0])
        return float(L + 20 - (L + 280) * (0.6 * u + 0.4 * u * u))
    return None


def render(G, seed=15):
    S = Offstage(G)
    d, mid, L = S.d, S.mid, S.L
    F = nframes(D)
    out = np.zeros((F, G.N, 3))
    rng = np.random.default_rng(seed)
    beats = np.array([b[0] for b in C.beats])
    downs = np.array(C.downbeats('alarm'))
    hp = [S.at(r, u) for r, u, _, _ in HOUSES]
    HW = 34.0                                           # half a house
    stars = (rng.random(G.N) < 0.2) * rng.uniform(0.3, 1.0, G.N)
    sph = rng.uniform(0, 2 * np.pi, G.N)
    beams = [(S.at('Right', 0.5), 260, 0.31, 0.0), (S.mid, 330, 0.23, 1.7), (S.at('Left', 0.45), 280, 0.27, 3.1)]
    flak = [(M['end'] - 2.6, S.at('Side', 0.55)), (M['end'] - 2.0, S.at('Side', 0.3)), (M['end'] - 1.5, S.at('Left', 0.2))]

    for f in range(F):
        t = f * DT
        up = smoothstep(0, 1.0, t)
        beat = pulse(t, beats, 0.12)
        alarm = smoothstep(M['alarm'] - 0.5, M['alarm'] + 1.0, t)
        # the sleeping town: blue night, snow, stars
        fr = light(NIGHT, (0.34 + 0.06 * beat) * up * np.ones(G.N))
        fr += S.snowfall(t, 0.35 * up)
        fr += light(MOON, 0.4 * up * stars * (0.5 + 0.5 * np.sin(2.5 * t + sph)))

        # ---- the houses: asleep, lit when he calls, screaming when the gift pops, then police lights
        for i, ((run, u, ta, gift), p) in enumerate(zip(HOUSES, hp)):
            body = S.span(p - HW, p + HW, 6)
            door = np.exp(-((d - p) / 4) ** 2)
            lit = smoothstep(ta + DROP, ta + DROP + 0.2, t)
            fr = fr * (1 - 0.6 * body)[:, None]
            fr += light(WARM, (0.3 + 0.6 * lit) * body * (1 - 0.8 * door))
            fr += light(WARM, 0.3 * lit * (1 - smoothstep(ta + POP, ta + POP + 0.5, t)) * S.run[run])
            tp = ta + POP
            if ta <= t < ta + DROP + 0.3:              # a present drops down the chimney
                a = t - ta
                fall = np.clip(a / DROP, 0, 1)
                fr += light(GOLD, 0.9 * np.exp(-((d - p) / (40 * (1 - fall) + 6)) ** 2))
            if ta + DROP <= t < tp:                     # it sits there, jiggling
                a = t - ta - DROP
                jig = 3 * np.sin(2 * np.pi * 5 * t) * smoothstep(0.5, tp - ta - DROP, a)
                fr = S.present(fr, p + jig, [RED, GREEN, VIOLET, BLUE][i], 1.0)
                if a < 0.3:
                    fr += light(WHITE, 0.7 * np.exp(-a / 0.08) * body)
            if tp <= t < tp + 3.5:                      # the gift pops out
                a = t - tp
                if a < 0.5:
                    fr += light(WHITE, 0.9 * np.exp(-a / 0.12) * S.blob(p, 90))
                fr += light(GLOW[gift], 0.4 * smoothstep(3.5, 2.5, a) * S.run[run])
                fr = gift_draw(S, fr, gift, p, a, t)
            sc = t - (tp + 0.35)                        # the house screams
            if 0 <= sc < 1.2:
                flash = WHITE if int(sc * 8) % 2 else RED
                fr += light(flash, 0.85 * np.exp(-sc / 0.6) * body)
                spread = 120 + 700 * sc
                fr += light(RED, 0.85 * np.exp(-sc / 0.5) * S.run[run] * smoothstep(spread + 40, spread - 40, np.abs(d - p)))
                fr += light(RED, 0.4 * np.exp(-sc / 0.4) * np.ones(G.N))
            if alarm > 0 and t >= tp:                   # police lights at every house that's had its present
                ph = (t * 2.5 + i * 0.5) % 1
                fr += light(RED if ph < 0.5 else POLICE_BLUE, 0.8 * alarm * body)
                fr += light(RED if ph < 0.5 else POLICE_BLUE, 0.3 * alarm * S.blob(p, 120))

        # ---- searchlights sweep the sky
        if alarm > 0:
            for k, (c, amp, rate, ph) in enumerate(beams):
                bp = c + amp * np.sin(2 * np.pi * rate * (t - M['alarm']) + ph)
                tp_ = track(S, t)
                if tp_ is not None and t > M['alarm'] + 3.0:      # they swing after him
                    bp = bp + (tp_ + 60 - bp) * 0.35
                fr += light(BEAM, 0.9 * alarm * np.exp(-((d - bp) / 28) ** 2))
                fr += light(ICE, 0.35 * alarm * np.exp(-((d - bp) / 90) ** 2))

        # ---- the sleigh
        p = track(S, t)
        if p is not None:
            fr += light(GOLD, 0.4 * S.blob(p + 80, 160))
            fr = S.sleigh(fr, p, 1.0, facing=-1, t=t)
            if t >= M['alarm']:                         # he waves, delighted: gold sparks on each downbeat
                fr += S.burst([(tb, 1.0, p + 140) for tb in downs], t, seed=7, n=16, reach=0.6, colors=(GOLD, WHITE))
                fr += light(GOLD, 0.5 * pulse(t, downs, 0.25) * S.blob(p + 120, 200))
                trail = smoothstep(p + 400, p + 160, d) * (d > p + 160)
                fr += light(GOLD, 0.35 * trail * (0.6 + 0.4 * np.sin(29 * t + 3 * sph)))

        # ---- flak bursts behind him as he heads away down Side
        for tf, pf in flak:
            a = t - tf
            if 0 <= a < 1.0:
                fr += light(WHITE, 0.9 * np.exp(-a / 0.1) * S.blob(pf, 50))
                fr += light(PUMPKIN, 0.7 * np.exp(-a / 0.3) * S.blob(pf, 110))
        out[f] = fr * float(smoothstep(D, D - 1.0, t))
    return np.clip(out, 0, 1)


def gift_draw(S, fr, gift, p, a, t):
    """What comes out of each present, a seconds after it pops."""
    d = S.d
    if gift == 'snake':                                 # slithers out along the roof toward the free end
        head = p + 40 + 160 * a
        body = smoothstep(head - 110, head - 70, d) * smoothstep(head + 4, head - 4, d)
        wave = 0.6 + 0.4 * np.sin((d - head) / 9 - 10 * t)
        fr = fr * (1 - 0.7 * body)[:, None] + light(SNAKE, 0.95 * body * wave)
        fr += light(RED, 0.9 * np.exp(-((d - head - 8) / 4) ** 2) * (np.sin(2 * np.pi * 6 * t) > 0))
    elif gift == 'jack':                                # a leering head on a spring, bobbing up and down
        fr = S.present(fr, p, RED, 1.0)
        spring = abs(np.sin(2 * np.pi * 2.2 * a)) * np.exp(-a / 1.6) * 0.8 + 0.2
        head = p + 10 + 70 * spring
        fr = S.sprite(fr, head, [(2, SLIME, 1.0), (1, None, 0), (0, WHITE, 1.0), (-1, None, 0), (-2, SLIME, 1.0)], 1.0)
        fr += light(SLIME, 0.5 * S.blob(head, 40))
        coil = smoothstep(p + 6, p + 10, d) * smoothstep(head - 6, head - 10, d)
        fr += light(GOLD, 0.5 * coil * (np.sin(d / 3) > 0))
    elif gift == 'bat':                                 # flaps off toward the back of the house
        x = p - 30 - 260 * a
        flap = 0.4 + 0.6 * abs(np.sin(2 * np.pi * 4 * t))
        fr = S.sprite(fr, x, [(3, VIOLET, flap), (2, VIOLET, 0.7), (1, None, 0), (0, RED, 1.0), (-1, None, 0),
                              (-2, VIOLET, 0.7), (-3, VIOLET, flap)], 1.0)
        fr += light(VIOLET, 0.45 * S.blob(x, 60))
    elif gift == 'wreath':                              # a hungry wreath, chomping
        chomp = 0.5 + 0.5 * np.sin(2 * np.pi * 3 * t)
        ring = np.exp(-((np.abs(d - p) - 26) / 8) ** 2)
        mouth = np.exp(-((d - p) / (4 + 10 * chomp)) ** 2)
        fr = fr * (1 - 0.8 * mouth)[:, None]
        fr += light(WREATH, 1.0 * ring)
        fr += light(RED, 0.9 * ring * (np.sin(d / 4) > 0.7))
        fr += light(GREEN, 0.4 * S.blob(p, 70) * (1 - mouth))
    return fr


def score(M_, G):
    S = Offstage(G)
    B = Band(M_, level=2.1)
    from pixelhome.audio import slide
    hp = [S.at(r, u) for r, u, _, _ in HOUSES]
    parts = {
        ('sleep', 'tune'): [('celesta', 0, -4, 0.45), ('flutes', 0, -10, 0.35)],
        ('sleep', 'arp'): [('harp', 0, -8, 0.4)],
        ('sleep', 'pedal'): [('cellos', 0, -14, 0.3)],
        ('fly1', 'tune'): [('xylo', 12, -4, 0.45), ('violins', 0, 0, 0.6), ('clarinets', 0, -4, 0.45)],
        ('fly1', 'bass'): [('tuba', -12, -4, 0.6), ('basses pizz', 0, -6, 0.45)],
        ('fly1', 'chord'): [('pizz', 0, -6, 0.4)],
        ('fly1', 'snare'): [('snare', 0, -14, 0.3)],
        ('fly2', 'tune'): [('horns', 0, 4, 0.75), ('violins', 0, 0, 0.55), ('xylo', 12, -6, 0.35)],
        ('fly2', 'bass'): [('tuba', -12, 0, 0.65), ('basses pizz', 0, -6, 0.45)],
        ('fly2', 'chord'): [('pizz', 0, -6, 0.4), ('trumpets', 0, -18, 0.25)],
        ('fly2', 'snare'): [('snare', 0, -12, 0.3)],
        ('alarm', 'tune'): [('trumpets', 0, 4, 0.65), ('trombones', 0, 4, 0.65), ('violins', 12, -2, 0.5),
                            ('choir', 0, -2, 0.55)],
        ('alarm', 'bass'): [('tuba', -12, 4, 0.75), ('basses', 0, -4, 0.5)],
        ('alarm', 'chord'): [('horns', 0, -10, 0.4), ('pizz', 0, -6, 0.35)],
        ('alarm', 'snare'): [('snare', 0, -8, 0.35)],
    }
    B.perform(C.events, parts)
    B.effects([(0, -4), (M['fly1'], -2), (M['alarm'], -5), (M['end'] - 3, -1)])

    def at(t):
        p = track(S, t)
        return S.pan(p + 80) if p is not None else -0.9
    # sleigh bells on every eighth while the sleigh is over the house
    B.sleigh_bells(M['fly1'], M['alarm'] - 0.3, beat=BEAT / 2, pan=at, v=88, gain=0.8)
    B.sleigh_bells(LAP[0], LAP[1], beat=BEAT / 2 * 150 / 160, pan=at, v=96, gain=0.9)
    for i, ((run, u, ta, gift), p) in enumerate(zip(HOUSES, hp)):
        pp = S.pan(p)
        tp = ta + POP
        M_.add('fx', slide(0, DROP * 0.9, 1400, 350, DROP, amp=0.18), ta, 1.0, pp)     # down the chimney
        B.hit('bass drum', ta + DROP, 110, gain=0.5, pan=pp, fx=True)
        B.hit('wood', ta + DROP + 0.02, 120, gain=0.8, pan=pp, fx=True)
        B.hit('slapstick', tp, 124, gain=0.8, pan=pp)
        if gift == 'snake':
            B.whoosh(tp + 0.05, 1.2, False, pan=pp, gain=0.6)
            B.hit('guiro', tp + 0.2, 100, gain=0.5, pan=pp)
        elif gift == 'jack':
            M_.add('fx', slide(0, 0.25, 300, 1500, 0.35, amp=0.3), tp, 1.0, pp)
            for k in range(5):
                M_.add('fx', slide(0, 0.1, 700, 1100, 0.15, amp=0.12 * 0.8 ** k), tp + 0.45 + 0.227 * k, 1.0, pp)
        elif gift == 'bat':
            for k in range(10):
                B.hit('wood', tp + 0.12 * k, 70, gain=0.4, pan=float(np.clip(pp - 0.07 * k, -1, 1)), fx=True)
        else:
            for k in range(6):
                B.hit('slapstick', tp + 0.333 * k + 0.1, 100, gain=0.5, pan=pp, fx=True)
        B.scream(tp + 0.35, pan=pp, high=0.8 + 0.15 * i)
        B.scream(tp + 0.6, pan=float(np.clip(pp + 0.15, -1, 1)), gain=0.7, high=1.2)
    # the alarm: sirens from both sides, a cymbal; flak behind him at the end
    B.siren(M['alarm'] - 0.5, M['end'], pan=0.5, gain=0.6)
    B.siren(M['alarm'] + 1.5, M['end'], pan=-0.5, gain=0.45)
    B.hit('crash', M['alarm'], 118, gain=0.5)
    for tf, pf in ((M['end'] - 2.6, -0.85), (M['end'] - 2.0, -0.85), (M['end'] - 1.5, -0.6)):
        B.flak(tf, pan=pf, gain=0.8)
    B.hit('crash', M['end'] - 2.2, 110, gain=0.3)
    B.finish()
