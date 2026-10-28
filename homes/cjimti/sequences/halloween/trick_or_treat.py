"""Trick or Treat: costumed kids walk in from the two free ends of the roofline to the front door
(the middle of Porch Front, the back of the notch), ring, get candy and leave. The house plays a
different gentle trick on each one: pretends nobody is home, throws the candy too far, sneezes,
copies the robot. The last kid is fearless: the house does its big red scare, the kid shouts BOO
back, and the whole roofline flinches away toward the far end of Side, where it trembles until it
hands over the entire bowl.

Kids are agents on the path (distance units), each a few pixels in costume colours with its own
gait; candy flies on 1-D ballistic arcs from the door; the BOO is a shock sphere in 3-D around the
kid, so it reaches across the notch to both porch runs at the same moment."""
import numpy as np
from pixelhome.fx import DT, hexc, perc, light, smoothstep, keys, lerp, Flicker, nframes

CODE = 'HW05'
TITLE = 'Trick or Treat'
KIND = 'show'
DESCRIPTION = ('Costumed kids walk up to the front door one by one, and the house plays a gentle trick '
               'on each of them. The last kid is not scared at all, and scares the house right back.')
VOICEOVER = 'Ring the bell, little ones. The house has a trick for every one of you... well. Almost every one.'

NIGHT = hexc('#2a0070')
LAMP = hexc('#ffa030')
SPILL = hexc('#ffc060')
DING = hexc('#fff0d0')
CANDY = [hexc(h) for h in ('#ff2080', '#00e0ff', '#80ff00', '#ffd000', '#ff6000', '#c040ff')]
RED = hexc('#ff0000')
SHY = hexc('#6000ff')
GUST = hexc('#a0d0ff')
WHITE = hexc('#ffffff')
GOLD = hexc('#ffc040')

D = 86.0
BIG = 1.5
L0, R0 = -40.0, 2552.0          # off-path start points beyond the two free ends


def C(h, i):
    return perc(i) * hexc(h)


# Costumes: (offset from centre toward the face, half width, PWM colour). Drawn back to front.
GHOST = [(-2, 17, C('#b8c8ff', 0.72)), (3, 2.4, C('#000000', 0)), (11, 2.4, C('#000000', 0))]
WITCH = [(-23, 5, C('#c06010', 0.45)), (-5, 11, C('#7a00ff', 0.75)), (11, 4.5, C('#30ff10', 0.8))]
PUMPKIN = [(0, 13, C('#ff4800', 0.8))]
ROBOT = [(0, 17, C('#7090c0', 0.42))]
DRAGON = [(-34, 6, C('#0a7010', 0.45)), (-8, 20, C('#10b020', 0.6)), (18, 6, C('#40ff30', 0.75)),
          (-22, 2.6, C('#ffc000', 0.85)), (-10, 2.6, C('#ffc000', 0.85)), (2, 2.6, C('#ffc000', 0.85))]
BEE = [(0, 6, C('#ffd000', 0.85)), (0, 1.6, C('#000000', 0))]
CAPE = [(-20, 3, C('#ffa000', 0.7)), (-6, 12, C('#d00010', 0.75)), (10, 4, C('#ffe8d0', 0.75))]


class Kid:
    """A walker on the path. legs: [(t0, t1, s0, s1, gait, period)]; holds between legs."""

    def __init__(self, parts, legs):
        self.parts, self.legs = parts, legs
        self.t_in, self.t_out = legs[0][0], legs[-1][1]
        self.face = None            # optional keyframes overriding facing

    def at(self, t):
        """(s, dir, moving, phase in cycle 0..1)."""
        s, d, mv, ph = self.legs[0][2], 1.0, False, 0.0
        for t0, t1, s0, s1, gait, per in self.legs:
            if t < t0:
                break
            d = 1.0 if s1 >= s0 else -1.0
            if t >= t1:
                s = s1
                continue
            u = (t - t0) / (t1 - t0)
            n = max(1, round((t1 - t0) / per))
            x = u * n
            k, fr = np.floor(x), x - np.floor(x)
            if gait == 'hop':
                g = (k + smoothstep(0, 0.62, fr)) / n
            elif gait == 'step':
                g = (k + smoothstep(0, 0.35, fr)) / n
            elif gait == 'smooth':
                g = smoothstep(0, 1, u)
            else:                    # surge: speed swings between (1-A) and (1+A)
                A = {'float': 0.45, 'stride': 0.7, 'stomp': 0.85, 'swagger': 0.45, 'dash': 0.3}[gait]
                g = u - A * np.sin(2 * np.pi * x) / (2 * np.pi * n)
            s, mv, ph = s0 + (s1 - s0) * g, True, fr
            break
        if self.face is not None:
            d = float(np.sign(keys(t, self.face)) or d)
        return s, d, mv, ph


def render(G, seed=5):
    rng = np.random.default_rng(seed)
    F = nframes(D)
    out = np.zeros((F, G.N, 3))
    sp = G.pd[G.path]                       # distance along the path, in path order
    P = G.pos[G.path]
    N = G.N
    DOOR = float(np.mean(G.pd[G.seg['Porch Front']]))
    LS, RS = DOOR - 66, DOOR + 66           # where kids from the left / right stand
    flick = Flicker(rng, N, 0.4, 2.5)
    rumble = Flicker(rng, N, 3.0, 9.0)

    def soft(d, hw, edge=3.0):
        return np.clip((hw - np.abs(d)) / edge + 0.5, 0, 1)

    def comp(buf, a, col):
        a = np.clip(a, 0, 1)[:, None]
        return buf * (1 - a) + col * a

    def draw(buf, parts, s, d, scale=1.0, gain=1.0, extra=()):
        scale = scale * BIG                 # costumes are designed small; drawn big enough for the street
        for off, hw, col in list(parts) + list(extra):
            buf = comp(buf, soft(sp - (s + d * off * scale), max(2.2, hw * scale)), col * gain)
        return buf

    # ---------------------------------------------------------------- the cast
    ghost = Kid(GHOST, [(1.5, 9.2, L0, LS, 'float', 1.3),
                        (11.3, 11.8, LS, LS + 10, 'smooth', 1),          # leans in to ring again
                        (12.9, 13.7, LS + 10, LS - 40, 'smooth', 1),     # gives up, turns away
                        (13.85, 14.2, LS - 40, LS - 8, 'smooth', 1),     # spins back: door!
                        (15.9, 21.5, LS - 8, L0, 'float', 1.1)])
    ghost.face = [(0, 1), (12.95, 1), (13.0, -1), (13.85, -1), (13.9, 1), (15.85, 1), (15.9, -1)]

    witch = Kid(WITCH, [(12.5, 18.8, R0, RS, 'stride', 0.42),
                        (21.9, 24.0, RS, 2080, 'dash', 0.25),           # chases the long throw
                        (24.9, 26.6, 2080, R0, 'stride', 0.3)])

    pump = Kid(PUMPKIN, [(19.0, 27.6, L0, LS, 'hop', 0.55),
                         (29.55, 30.7, LS, LS - 150, 'smooth', 1),       # blown back by the sneeze
                         (31.2, 32.9, LS - 150, LS, 'hop', 0.42),
                         (34.6, 41.8, LS, L0, 'hop', 0.5)])
    pump.face = [(0, 1), (29.5, 1), (29.55, -1), (32.9, -1), (32.95, 1)]   # rolls backwards

    robot = Kid(ROBOT, [(29.5, 36.8, R0, RS, 'step', 0.38),
                        (43.4, 49.4, RS, R0, 'step', 0.3)])

    dragon = Kid(DRAGON, [(39.0, 47.4, L0 - 20, LS - 12, 'stomp', 0.75),
                          (53.6, 61.0, LS - 12, L0 - 60, 'stomp', 0.7)])
    dragon.face = [(0, 1), (51.2, 1), (51.25, -1), (51.9, -1), (51.95, 1), (53.55, 1), (53.6, -1)]

    cape = Kid(CAPE, [(55.0, 61.6, R0, RS, 'swagger', 0.85),
                      (78.4, 83.6, RS, R0, 'swagger', 0.75)])

    # bee: follows the dragon with a gap that stretches and snaps shut (it dashes to catch up)
    def bee_at(t):
        if t < 53.6:
            s, _, _, _ = dragon.at(t)
            ph = ((t - 39.0) / 2.6) % 1
            gap = 66 + 120 * ph ** 1.6 * (1 - smoothstep(0.82, 1.0, ph)) if t < 47.4 else 40
            gap = lerp(gap, 84, smoothstep(47.4, 48.6, t))
            return s - gap, 1.0
        s, _, _, _ = dragon.at(t)
        lead = 60 * smoothstep(53.6, 55.0, t)
        return s - lead - 20, -1.0

    # ---------------------------------------------------------------- candy
    candy = []          # (t launch, duration, s0, s1, colour, half width, lands?)

    def toss(t0, n, gap, s1, spread=10, dur=0.55, hw=3.2):
        for k in range(n):
            candy.append((t0 + k * gap, dur + rng.uniform(-0.05, 0.05), DOOR,
                          s1 + rng.uniform(-spread, spread), CANDY[rng.integers(len(CANDY))], hw))

    toss(14.25, 4, 0.32, LS - 8)                     # ghost
    toss(20.1, 2, 0.4, RS)                           # witch: two good ones...
    candy.append((21.0, 1.1, DOOR, 2080, CANDY[3], 3.6))   # ...and one thrown way too far
    toss(33.1, 3, 0.35, LS)                          # pumpkin
    toss(42.0, 4, 0.28, RS)                          # robot
    toss(49.0, 3, 0.35, LS - 12)                     # dragon
    candy.append((50.7, 1.5, DOOR, LS - 96, CANDY[0], 9.0))   # the giant one for the little bee
    toss(62.0, 2, 0.45, RS, dur=0.5)                 # fearless kid, before anything happens
    toss(75.6, 16, 0.13, RS, spread=16, dur=0.5)     # the whole bowl

    def catches(t):
        """sparkle at each landing point."""
        e = np.zeros(N)
        for t0, dur, s0, s1, col, hw in candy:
            dt = t - (t0 + dur)
            if 0 <= dt < 0.35:
                e = np.maximum(e, np.exp(-dt / 0.1) * soft(sp - s1, 6 + hw))
        return e

    # ---------------------------------------------------------------- door
    rings = [9.5, 9.85, 11.9, 12.1, 12.3, 19.1, 19.45, 28.0, 28.35, 47.7, 48.05, 61.9, 62.25]
    open_k = [(0, 0), (14.0, 0), (14.1, 1.15), (14.4, 1), (15.7, 1), (16.2, 0),
              (19.7, 0), (20.0, 1), (21.6, 1), (22.2, 0),
              (28.6, 0), (28.8, 0.6), (29.1, 0.35), (29.4, 0.2), (29.5, 1.2), (30.2, 1), (33.9, 1), (34.4, 0),
              (41.6, 0), (41.9, 1), (43.3, 1), (43.8, 0),
              (48.5, 0), (48.8, 1), (52.4, 1), (52.9, 0),
              (61.6, 0), (61.9, 1), (62.9, 1), (63.3, 0),
              (74.7, 0), (75.0, 0.25), (75.3, 0.25), (75.5, 1.0), (77.9, 1), (78.4, 0)]
    lamp_k = [(0, 0), (1.0, 0.3), (10.3, 0.3), (10.4, 0), (13.95, 0), (14.0, 0.24),
              (28.6, 0.24), (29.3, 0.5), (29.45, 0.1), (30.5, 0.24),        # breath in, ACHOO
              (63.6, 0.24), (63.7, 0.05), (63.8, 0.24), (64.0, 0.06), (64.1, 0.24), (64.4, 0),
              (75.0, 0), (75.4, 0.24), (83.5, 0.24), (84.6, 0)]

    # robot copycat: robot blinks a pattern, the house echoes it outward from the door
    rob_cols = [hexc('#ff0010'), hexc('#00ff40'), hexc('#00c0ff')]
    rob_pat = [(37.2, 0), (37.5, 1), (37.8, 2),
               (39.2, 2), (39.4, 0), (39.6, 2), (39.8, 1),
               (40.9, 1), (41.0, 1), (41.1, 0), (41.2, 2), (41.3, 0)]
    echo = [(t + (0.7 if t < 39 else 0.6 if t < 40.5 else 0.45), c) for t, c in rob_pat]
    echo.append((41.95, 2))                            # the house adds one more, showing off
    rob_lights = [-10, 0, 10]

    # big scare and recoil
    front_k = [(0, 2512), (71.0, 2512), (71.25, 260), (71.4, 420), (71.6, 170), (72.0, 240), (74.5, 220),
               (75.5, 260), (79.0, 300), (81.5, 300), (83.0, 900), (84.0, 860), (86, 900)]
    kid_i = int(np.argmin(np.abs(sp - RS)))
    kid_p = P[kid_i]
    r3 = np.linalg.norm((P - kid_p)[:, [0, 2]], axis=1)

    for f in range(F):
        t = f * DT
        # night bed, faint indigo
        nightI = keys(t, [(0, 0.06), (1.5, 0.13), (63.6, 0.13), (64.2, 0), (83.5, 0), (85, 0.13)])
        buf = light(NIGHT, nightI * (1 + 0.15 * flick(t)))

        # door: porch lamp, light spilling out, doorbell
        dd = np.abs(sp - DOOR)
        op = keys(t, open_k)
        lamp = keys(t, lamp_k)
        buf += light(LAMP, lamp * soft(dd, 22, 8))
        if op > 0:
            reach = 30 + 150 * min(op, 1.2)
            buf += light(SPILL, 0.75 * op * (1 - smoothstep(0, reach, dd)) ** 1.5)
        ding = max([np.exp(-((t - r - 0.06) / 0.07) ** 2) for r in rings])
        buf += light(DING, 0.6 * ding * soft(dd, 16, 6))

        # pumpkin's sneeze: a cold puff out of the door both ways
        if 29.4 < t < 31.0:
            fr = (t - 29.45) * 900
            buf += light(GUST, 0.9 * np.exp(-((dd - fr) / 70) ** 2) * np.exp(-dd / 900) * (dd < fr + 90))

        # robot copycat echo
        if 37.8 < t < 45.0:
            ew = np.zeros((N, 3))
            for te, c in echo:
                ft = (t - te) * 380              # slow enough to read light for light
                if 0 < ft < 950:
                    ew += light(rob_cols[c], 0.5 * np.exp(-((dd - ft) / 15) ** 2) * (1 - ft / 950) ** 0.7)
            buf += ew

        # the big scare: red crawls in from both free ends, then roars
        red = np.zeros(N)
        if 64.6 < t < 71.3:
            crawl = keys(t, [(64.6, 0), (68.0, 1)])
            fromL = 1 - smoothstep(crawl * (DOOR - 60) - 120, crawl * (DOOR - 60), sp)
            fromR = smoothstep(2512 - crawl * (2512 - RS - 60), 2512 - crawl * (2512 - RS - 60) + 120, sp)
            ramp = keys(t, [(64.6, 0.15), (68.0, 0.45), (68.3, 0.45)])
            red = np.maximum(fromL, fromR) * ramp * (1 + 0.35 * rumble(t))
            if t >= 68.3:
                closed = 1 - smoothstep(30, 80, np.abs(sp - RS))  # keep the kid visible
                roar = 0.55 + 0.4 * max(np.exp(-((t - p) / 0.09) ** 2) for p in (68.4, 68.85, 69.3))
                hold = keys(t, [(69.6, 1), (70.2, 0.55), (71.0, 0.5)])
                red = (roar if t < 69.6 else 0.5 * hold) * (1 + 0.2 * rumble(t)) * (1 - 0.6 * closed)
        if t >= 71.0:
            # recoil: everything the house has is shoved toward the back end of Side
            front = keys(t, front_k)
            tremble = 1 + 0.25 * np.sin(2 * np.pi * 11 * t) * keys(t, [(71.4, 1), (79, 0.4), (82, 0.1)])
            fade = keys(t, [(71.0, 0.75), (72.0, 0.6), (76, 0.4), (80, 0.3), (83, 0.22), (86, 0.14)])
            red = fade * (1 - smoothstep(front * tremble * 0.75, front * tremble, sp))
            col = lerp(RED, SHY, smoothstep(72.5, 76.0, t))
            buf += light(col, red)
        else:
            buf = buf * (1 - np.clip(red * 1.8, 0, 1))[:, None] + light(RED, red)

        # candy in flight
        for t0, dur, s0, s1, col, hw in candy:
            u = (t - t0) / dur
            if 0 <= u < 1:
                s = lerp(s0, s1, u)
                hgt = np.sin(np.pi * u)
                a = soft(sp - s, hw * (1.25 - 0.45 * hgt), 2.5)
                buf = comp(buf, a, col * (0.55 + 0.45 * hgt))
        buf += light(WHITE, 0.55 * catches(t))
        if 22.1 <= t < 24.1:                             # the long throw lies there, twinkling, until fetched
            buf = comp(buf, soft(sp - 2080, 4.5, 2.5), CANDY[3] * (0.6 + 0.4 * np.sin(2 * np.pi * t * 2.5)))

        # kids
        def put(buf, kid, scale=1.0, gain=1.0, extra=()):
            if not (kid.t_in <= t <= kid.t_out + 0.01):
                return buf
            s, d, mv, ph = kid.at(t)
            return draw(buf, kid.parts, s, d, scale, gain, extra)

        # ghost: bobs while floating, droops when nobody answers
        s, d, mv, ph = ghost.at(t)
        gbob = 1 + 0.08 * np.sin(2 * np.pi * t / 1.3)
        droop = 1 - 0.3 * keys(t, [(12.8, 0), (13.4, 1), (13.85, 1), (13.9, 0)])
        joy = 1 + 0.5 * np.exp(-max(0, t - 13.9) / 0.4) * (t > 13.85)
        buf = put(buf, ghost, gain=gbob * droop * joy)

        # witch: stride bounce
        buf = put(buf, witch, gain=1 + 0.12 * np.sin(2 * np.pi * t / 0.42))

        # pumpkin: squashes on landing, stem spins while rolling
        if pump.t_in <= t <= pump.t_out:
            s, d, mv, ph = pump.at(t)
            air = mv and ph < 0.62 and not (29.55 <= t < 30.7)
            sc = 0.85 if air else (1.0 + 0.18 * np.exp(-max(0, ph - 0.62) / 0.06) if mv else 1.0)
            stem_off = 9 if not (29.55 <= t < 30.7) else 9 * np.cos(2 * np.pi * (t - 29.55) * 2.6)
            stem = [(stem_off, 3, C('#30d000', 0.85 * (0.5 + 0.5 * (stem_off > -3))))]
            buf = draw(buf, PUMPKIN, s, d, sc, 1.1 if air else 1.0, stem)

        # robot: three lights; blinks its pattern at the door, then confused flicker
        if robot.t_in <= t <= robot.t_out:
            s, d, mv, ph = robot.at(t)
            lit = []
            for k, o in enumerate(rob_lights):
                on = 0.5 + 0.5 * (int(t * 3 + k) % 3 == 0)
                if 37.0 < t < 43.4:
                    on = 0.12
                    for tp, c in rob_pat:
                        if c == k and 0 <= t - tp < 0.16:
                            on = 1.0
                    if 42.05 < t < 42.9:
                        on = 0.25 + 0.75 * (int(t * 18 + k * 2) % 3 == 0)   # does not compute
                lit.append((o, 4.7, rob_cols[k] * perc(0.9) * on))
            jolt = 1.0 + 0.5 * (mv and ph < 0.35)
            buf = draw(buf, ROBOT, s, d, 1.0, jolt, lit)

        # dragon: heavy stomps thump
        if dragon.t_in <= t <= dragon.t_out:
            s, d, mv, ph = dragon.at(t)
            thump = 1 + 0.25 * np.exp(-((ph - 0.0) / 0.08) ** 2) if mv else 1.0
            buf = draw(buf, DRAGON, s, d, 1.0, thump)

        # bee: tiny quick bounce, then lugs the giant candy
        if 39.0 <= t <= 61.0:
            s, d = bee_at(t)
            extra = []
            if t >= 52.2:
                extra = [(14, 9 + 1.5 * np.sin(2 * np.pi * t * 1.3), CANDY[0] * 0.8)]
            squash = 1 + 0.6 * np.exp(-max(0, t - 52.2) / 0.25) * (t > 52.2)
            buf = draw(buf, BEE, s, d, squash, 1 + 0.15 * np.sin(2 * np.pi * t * 3.2), extra)

        # the fearless kid
        if cape.t_in <= t <= cape.t_out:
            s, d, mv, ph = cape.at(t)
            boo = np.exp(-max(0.0, t - 70.6) / 0.5) * (t >= 70.6) + 0.5 * smoothstep(69.9, 70.6, t) * (t < 70.6)
            hop = (75.6 < t < 78.3) * 0.25 * abs(np.sin(2 * np.pi * t * 1.6))
            buf = draw(buf, CAPE, s, d, 1 + 0.6 * boo + hop, 1 + boo)
            if boo > 0.01:
                buf += light(WHITE, min(1.0, boo) * soft(sp - s, 70, 20))

        # BOO: a shock sphere around the kid, in 3-D
        if 70.6 <= t < 72.2:
            r = (t - 70.6) * 1500
            ring = np.exp(-((r3 - r) / 90) ** 2) * (1 - (t - 70.6) / 1.6)
            buf += light(GOLD, 1.0 * ring)

        out[f][G.path] = np.clip(buf, 0, 1)
    return out


# ---------------------------------------------------------------- music ----------------------------------------------
# A cartoon woodwind band in F major, where every kid is an instrument walking to its own gait: the ghost is a flute in
# a slow waltz (one bar per float), the witch a cackling staccato oboe, the pumpkin a hopping bassoon, the robot a
# square wave, the dragon a trombone with a bass drum in each stomp and its bee a buzzing synth that dashes to catch up,
# the fearless kid a muted trumpet strutting over a walking bass. The house has a voice of its own (a little percussive
# organ) for its tricks: the hide, the chuckle, the sneeze, copying the robot; its big scare is low brass, gong and
# timpani; it yelps on a slide whistle and trembles on a flexatone. Every sound is a moment in render() (footfalls,
# doorbells, candy launches and landings, the gust, the echo, the roars, the BOO), from the same legs, keys and seed,
# panned to where it happens on the house as seen from the street.

CH = {'F': 'F A C', 'Dm': 'D F A', 'Bb': 'Bb D F', 'C7': 'C E G Bb', 'Gm': 'G Bb D', 'A7': 'A C# E G',
      'D7': 'D F# A C', 'Bbm': 'Bb Db F', 'Fm': 'F Ab C', 'Db': 'Db F Ab', 'Bo7': 'B D F Ab'}
GHOST_TUNE = [('A5', 'G5'), ('F5', 'E5'), ('D5', 'F5'), ('E5', 'Bb5'), ('A5', 'C6'), ('Bb5', 'G5')]
GHOST_CHORDS = ['F', 'Dm', 'Bb', 'C7', 'F', 'C7']
CAPE_TUNE = ['A4', 'C5', 'D5', 'C5', 'Bb4', 'D5', 'E5', 'G5', 'F5']   # two steps a chord: F D7 Gm C7, then F
CAPE_CHORDS = ['F', 'D7', 'Gm', 'C7']
ROBOT_NOTE = {0: 'F5', 1: 'A5', 2: 'C6'}                               # red, green, blue


def score(M, G):
    from pixelhome.audio import note, slide, whoosh, SR
    n = note
    PCS = {k: [n(p + '4') % 12 for p in v.split()] for k, v in CH.items()}

    def tone(ch, i, lo):                    # the i-th chord tone at or above midi note lo
        ms = [m for m in range(lo, lo + 72) if m % 12 in PCS[ch]]
        return ms[i]

    def root(ch, lo):
        return next(m for m in range(lo, lo + 12) if m % 12 == PCS[ch][0])

    # ---- where things are: the same legs, seed and timings as render() ----
    rng = np.random.default_rng(5)
    Flicker(rng, G.N, 0.4, 2.5)             # render() draws these first; keeps the candy throws identical
    Flicker(rng, G.N, 3.0, 9.0)
    DOOR = float(np.mean(G.pd[G.seg['Porch Front']]))
    LS, RS = DOOR - 66, DOOR + 66
    ghost = Kid(GHOST, [(1.5, 9.2, L0, LS, 'float', 1.3), (11.3, 11.8, LS, LS + 10, 'smooth', 1),
                        (12.9, 13.7, LS + 10, LS - 40, 'smooth', 1), (13.85, 14.2, LS - 40, LS - 8, 'smooth', 1),
                        (15.9, 21.5, LS - 8, L0, 'float', 1.1)])
    witch = Kid(WITCH, [(12.5, 18.8, R0, RS, 'stride', 0.42), (21.9, 24.0, RS, 2080, 'dash', 0.25),
                        (24.9, 26.6, 2080, R0, 'stride', 0.3)])
    pump = Kid(PUMPKIN, [(19.0, 27.6, L0, LS, 'hop', 0.55), (29.55, 30.7, LS, LS - 150, 'smooth', 1),
                         (31.2, 32.9, LS - 150, LS, 'hop', 0.42), (34.6, 41.8, LS, L0, 'hop', 0.5)])
    robot = Kid(ROBOT, [(29.5, 36.8, R0, RS, 'step', 0.38), (43.4, 49.4, RS, R0, 'step', 0.3)])
    dragon = Kid(DRAGON, [(39.0, 47.4, L0 - 20, LS - 12, 'stomp', 0.75), (53.6, 61.0, LS - 12, L0 - 60, 'stomp', 0.7)])
    cape = Kid(CAPE, [(55.0, 61.6, R0, RS, 'swagger', 0.85), (78.4, 83.6, RS, R0, 'swagger', 0.75)])

    candy = []

    def toss(t0, k, gap, s1, spread=10, dur=0.55):
        for j in range(k):
            candy.append((t0 + j * gap, dur + rng.uniform(-0.05, 0.05), s1 + rng.uniform(-spread, spread)))
            rng.integers(len(CANDY))

    toss(14.25, 4, 0.32, LS - 8)
    toss(20.1, 2, 0.4, RS)
    LONG = (21.0, 1.1, 2080.0)
    candy.append(LONG)
    toss(33.1, 3, 0.35, LS)
    toss(42.0, 4, 0.28, RS)
    toss(49.0, 3, 0.35, LS - 12)
    GIANT = (50.7, 1.5, LS - 96)
    candy.append(GIANT)
    toss(62.0, 2, 0.45, RS, dur=0.5)
    BOWL = len(candy)
    toss(75.6, 16, 0.13, RS, spread=16, dur=0.5)
    rings = [9.5, 9.85, 11.9, 12.1, 12.3, 19.1, 19.45, 28.0, 28.35, 47.7, 48.05, 61.9, 62.25]
    rob_pat = [(37.2, 0), (37.5, 1), (37.8, 2), (39.2, 2), (39.4, 0), (39.6, 2), (39.8, 1),
               (40.9, 1), (41.0, 1), (41.1, 0), (41.2, 2), (41.3, 0)]
    echo = [(t + (0.7 if t < 39 else 0.6 if t < 40.5 else 0.45), c) for t, c in rob_pat] + [(41.95, 2)]
    roars = (68.4, 68.85, 69.3)
    BOO = 70.6

    def falls(kid, legs=None):
        """Footfalls (t, s, period) of a kid: surge gaits put a foot down where the speed dips (each cycle
        start and the arrival), hops land at 0.62 of a cycle, robot steps jolt at the start of each."""
        out = []
        for i, (t0, t1, s0, s1, gait, per) in enumerate(kid.legs):
            if gait == 'smooth' or (legs is not None and i not in legs):
                continue
            k = max(1, round((t1 - t0) / per))
            T = (t1 - t0) / k
            off = 0.62 if gait == 'hop' else 0.0
            ts = [t0 + (j + off) * T for j in range(k)] + ([] if gait in ('hop', 'step') else [t1])
            out += [(t, kid.at(t)[0], T) for t in ts]
        return out

    order = np.argsort(G.pd)
    xs, ds = G.pos[order, 0], G.pd[order]
    x0, x1 = xs.min(), xs.max()
    L = G.length

    def pan_at(d):                          # path distance -> left/right across the facade, as seen from the street
        x = np.interp(np.clip(d, 0, L), ds, xs)
        return 0.85 * (2 * (x - x0) / (x1 - x0) - 1)

    PD = float(pan_at(DOOR))

    def track(bus, sig, t, where, gain=1.0):
        """Add sig at time t, panned sample by sample along where(times) (path distances)."""
        m = sig.mean(0)
        tt = t + np.arange(0, len(m) + 960, 960) / SR
        p = np.interp(np.arange(len(m)), np.arange(0, len(m) + 960, 960), pan_at(np.array([where(x) for x in tt])))
        a = (p + 1) * np.pi / 4
        M.add(bus, np.vstack([m * np.cos(a), m * np.sin(a)]) * np.sqrt(2), t, gain)

    # ---- chords, from the same moments ----
    Tg = (9.2 - 1.5) / round(7.7 / 1.3)
    wf = falls(witch, [0])
    cf = falls(cape, [0])
    xf = falls(cape, [1])
    chart = [(0.0, 'F')] + [(1.5 + k * Tg, c) for k, c in enumerate(GHOST_CHORDS)] + [
        (9.5, 'F'), (10.4, 'Bbm'), (11.9, 'C7'), (12.9, 'Bbm'), (13.4, 'Fm'), (13.85, 'C7'), (14.0, 'F'),
        (wf[6][0], 'Dm'), (wf[10][0], 'Gm'), (wf[14][0], 'A7'), (18.8, 'Dm'), (19.1, 'F'), (20.0, 'Bb'),
        (20.6, 'F'), (21.0, 'C7'), (22.1, 'F'), (23.0, 'Dm'), (24.0, 'A7'), (24.9, 'Dm'), (26.6, 'F'),
        (27.6, 'C7'), (28.0, 'F'), (28.6, 'Bo7'), (29.45, 'C7'), (30.7, 'F'), (32.05, 'C7'), (32.9, 'F'),
        (34.6, 'Bb'), (35.8, 'C7'), (37.0, 'F'), (42.05, 'Bo7'), (42.9, 'F'), (43.4, 'Bb'), (44.93, 'F'),
        (46.46, 'C7'), (47.4, 'F'), (48.8, 'Bb'), (49.6, 'F'), (50.7, 'Db'), (51.2, 'C7'), (52.2, 'F'),
        (54.3, 'Bb'), (55.0, 'F')] + [(cf[2 * j][0], CAPE_CHORDS[j % 4]) for j in range(4)] + [
        (61.6, 'F'), (63.3, 'C7'), (63.6, 'Fm'), (66.3, 'Db'), (67.2, 'Bo7'), (69.6, 'Fm'), (BOO, 'F'),
        (71.0, 'Bo7'), (71.4, 'Fm'), (72.5, 'Db'), (73.6, 'Bbm'), (74.7, 'C7'), (75.5, 'F')] + [
        (xf[2 * j][0], CAPE_CHORDS[j % 4]) for j in range(4)] + [(83.6, 'F')]
    chart.sort()
    cts = np.array([c[0] for c in chart])

    def chord(t):
        return chart[max(0, int(np.searchsorted(cts, t + 1e-6)) - 1)][1]

    # ---- instruments ----
    flute = M.sampler('Woodwinds/Flute/susvib/*.wav')
    oboe = M.sampler('Woodwinds/Oboe/Stacc/*.wav')
    bsn = M.sampler('Woodwinds/Bassoon/stac/*.wav')
    tbn = M.sampler('Brass/Tenor Trombone/stac/*.wav')
    horn = M.sampler('Brass/F Horn/stac/*.wav')
    mute = M.sampler('Brass/Trumpet/straightM-sus/*.wav')
    tpt = M.sampler('Brass/Trumpet/stac/*.wav')
    blat = M.sampler('Brass/OldTrombone/Buzz/*.wav')
    fall = M.sampler('Brass/OldTrombone/Fall/*.wav')
    vpizz = M.sampler('Strings/Violin Section/Pizz/*.wav')
    vtrem = M.sampler('Strings/Violin Section/Trem/*.wav')
    cb = M.sampler('Strings/Solo Contrabass/Pizz/*.wav')
    cbtrem = M.sampler('Strings/Solo Contrabass/Trem/*.wav')
    harp = M.sampler('Strings/Harp/*.wav')
    glock = M.sampler('Percussion/Glock/*.wav')
    tbell = M.sampler('Percussion/TB_hit_*.wav')
    bd = M.hits('VSCO 1 Percussion/drums/bass/bdrum_f*.wav')
    bd_soft = M.hits('VSCO 1 Percussion/drums/bass/bdrum_mp*.wav')
    timp = M.hits('Percussion/Timpani/Timpani3_Hit*.wav')
    troll = M.hits('Percussion/Timpani/Rolls/*.wav')
    gong = M.hits('VSCO 1 Percussion/varMetal/Gong/gong_hit_ff*.wav')
    cym = M.hits('Percussion/susCymb1-hit_f_*.wav')
    swell = M.hits('Percussion/susCymb1-cresc-Long*.wav')
    snare = M.hits('VSCO 1 Percussion/drums/snare/drum1/snare1_mp_[12].wav')
    rim = M.hits('VSCO 1 Percussion/drums/snare/drum1/snare1_rimshot_mf.wav')
    sroll = M.hits('Percussion/Snare2-rollSN_v5*.wav')
    tamb = M.hits('VSCO 1 Percussion/varWood/tambourine_up_*.wav')
    logd = M.hits('Percussion/LogDrumHi*.wav')
    brake = M.hits('Percussion/BrakeDrum1_Hammer_v1*.wav')
    click = M.hits('VSCO 1 Percussion/varWood/wood_click_pp*.wav')
    flex = M.hits('VSCO 1 Percussion/varMetal/various/flexatone_extralong.wav')
    vslap = M.hits('VSCO 1 Percussion/varWood/vibraslap*.wav')
    guiro = M.hits('VSCO 1 Percussion/varWood/guiro_superlong.wav')
    zap = M.hits('Miscellania Raw/Misc 1/zap[1-4].wav')
    chimes = M.hits('VSCO 1 Percussion/varMetal/various/windchimes_slowAsc1.wav')
    gliss = M.hits('Miscellania Raw/Misc 2/glock_glisses/glock_fx_up_pentatonic*.wav')

    for name, gain, rev in (('winds', 0.24, 0.25), ('brass', 0.42, 0.2), ('strings', 0.24, 0.25), ('bass', 0.34, 0.08),
                            ('harp', 0.26, 0.35), ('bells', 0.24, 0.32), ('synth', 0.17, 0.18), ('house', 0.26, 0.3),
                            ('bee', 0.07, 0.1), ('perc', 0.34, 0.15), ('drums', 0.5, 0.2), ('fx', 0.28, 0.25)):
        M.bus(name, gain=gain, reverb=rev)
    house = []                              # the house's own voice at its door: (t, note, vel, dur)
    hiding = []                             # ... and from the far end of Side, where it hides after the BOO

    def kidpan(kid):
        return lambda t: kid.at(t)[0]

    def plink(t, s, k=0, vel=90):            # candy lands: a glock note climbing the chord, a triangle glint
        c = chord(t)
        M.add('bells', glock.play(tone(c, 3 + k, n('C5')), vel), t, 1.0, pan_at(s))

    def launch(t, vel=60):
        M.add('harp', harp.play(tone(chord(t), 4, n('C4')), vel), t, 0.6, PD)

    def ding(t, m, vel=100):
        M.add('bells', tbell.play(n(m), vel), t, 1.0, PD)

    def bar_bass(t, c, alt, vel=88, pan=-0.1):
        m = root(c, n('F1')) if alt % 2 == 0 else tone(c, 2, root(c, n('F1')))
        M.add('bass', cb.play(m, vel), t, 1.0, pan)

    def pizz_chord(t, c, vel=70, lo='C4'):
        for m in [tone(c, i, n(lo)) for i in range(3)]:
            M.add('strings', vpizz.play(m, vel), t, 0.5, 0.3)

    # ---- 0-1.5: night; the porch lamp comes on ----
    M.add('fx', chimes.play(70), 0.1, 0.35, -0.3)
    for i, m in enumerate(('F3', 'C4', 'A4', 'C5', 'F5')):
        M.add('harp', harp.play(n(m), 70 + 5 * i), 0.62 + 0.08 * i, 0.8, PD)

    # ---- 1.5-9.2: the ghost floats in, a slow waltz on the flute, one bar per float ----
    gf = falls(ghost, [0])
    for k, (t, s, T) in enumerate(gf[:-1]):
        c = GHOST_CHORDS[k]
        lng, pick = GHOST_TUNE[k]
        p = float(pan_at(s))
        M.add('winds', flute.play(n(lng), 84, dur=T * 0.7, release=0.25), t, 1.0, p)
        M.add('winds', flute.play(n(pick), 74, dur=T * 0.3, release=0.15), t + 2 * T / 3, 1.0, p)
        bar_bass(t, c, k)
        pizz_chord(t + T / 3, c, 58)
        pizz_chord(t + 2 * T / 3, c, 52)
        M.add('harp', harp.play(tone(c, 3, n('C5')), 55), t, 0.5, p)

    # ---- 9.5-14.0: nobody home. Ding-dong; the lamp clicks off; the ghost waits, rings again, gives up ----
    ding(9.5, 'F5')
    ding(9.85, 'C5')
    M.add('perc', click.play(80), 10.32, 0.8, PD)
    for i, m in enumerate(('F4', 'E4', 'Eb4', 'D4', 'Db4')):  # the house tiptoes away from its own door
        M.add('strings', vpizz.play(n(m), 66 - 3 * i), 10.45 + 0.28 * i, 0.8, PD + 0.1)
    M.add('winds', flute.play(n('E5'), 60, dur=0.22), 11.3, 0.9, pan_at(LS))   # leaning in: hello?
    M.add('winds', flute.play(n('G5'), 66, dur=0.35), 11.55, 0.9, pan_at(LS))
    for t in (11.9, 12.1, 12.3):
        ding(t, 'F5', 104)
    M.add('brass', fall.play(n('Bb2'), 90), 12.95, 0.8, pan_at(LS - 20))          # gives up, turns away
    M.add('winds', flute.play(n('Db5'), 56, dur=0.4), 13.0, 0.6, pan_at(LS - 30))
    M.add('winds', flute.play(n('C5'), 50, dur=0.4), 13.4, 0.6, pan_at(LS - 40))
    for i, m in enumerate(('C4', 'E4', 'G4', 'Bb4', 'C5')):                       # spins back: the door!
        M.add('harp', harp.play(n(m) + 12, 90), 13.85 + 0.03 * i, 0.8, PD)
    # 14.0: SURPRISE. The door bursts open past full
    for m in ('F3', 'C4', 'F4', 'A4', 'C5'):
        house.append((14.0, n(m), 118, 0.5))
    M.add('drums', cym.play(100), 14.0, 0.5, PD)
    M.add('drums', bd_soft.play(100), 14.0, 0.6, PD)
    M.add('winds', flute.play(n('F6'), 96, dur=0.5), 13.92, 0.8, pan_at(LS - 8))  # the ghost jumps for joy
    house += [(14.35, n('C6'), 90, 0.1), (14.5, n('A5'), 90, 0.1), (14.65, n('C6'), 80, 0.1)]  # hee hee hee
    for j in range(4):
        t0, dur, s1 = candy[j]
        launch(t0)
        plink(t0 + dur, s1, j)
        M.add('bass', cb.play(root('F', n('F1')) + [0, 7, 12, 7][j], 80), t0 + dur, 0.7, pan_at(s1))

    # ---- 12.5-18.8: the witch strides in from the right end on a cackling oboe ----
    for k, (t, s, T) in enumerate(wf):
        c = chord(t)
        near = 1 - abs(s - RS) / (R0 - RS)
        v = int(58 + 50 * near)
        M.add('winds', oboe.play(tone(c, [0, 2, 1, 2][k % 4], n('A4')), v), t, 0.9, pan_at(s))
        if k % 4 == 3:                     # heh-heh-heh
            top = tone(c, 3, n('A4'))
            for i, m in enumerate((top + 1, top, top + 1)):
                M.add('winds', oboe.play(m, v - 10), t + 0.12 + 0.065 * i, 0.7, pan_at(s))
        if t > 14.9:
            bar_bass(t, c, k, 70 + int(15 * near), 0.2)
            M.add('strings', vpizz.play(tone(c, 1, n('D4')), 55), t + T / 2, 0.5, 0.3)

    # ---- 15.9-21.5: the ghost floats away left, softer each bar ----
    for k, (t, s, T) in enumerate(falls(ghost, [4])[:-1]):
        M.add('winds', flute.play(tone(chord(t), 4 - k, n('C5')), 70 - 8 * k, dur=T * 0.9, release=0.3), t, 0.8,
              pan_at(s))

    # ---- 19.1-24.1: her candy, the one thrown way too far, and the dash to fetch it ----
    ding(19.1, 'F5')
    ding(19.45, 'C5')
    for m in ('F2', 'C3', 'A3'):
        M.add('harp', harp.play(n(m), 80), 20.0, 0.6, PD)
    for j in (4, 5):
        t0, dur, s1 = candy[j]
        launch(t0)
        plink(t0 + dur, s1, j - 4)
    t0, dur, s1 = LONG
    up = slide(0.0, dur / 2, 700, 2100, dur / 2, 0.32, 0.5)
    dn = slide(0.0, dur / 2, 2100, 500, dur / 2 + 0.05, 0.32, 0.6)
    track('fx', up, t0, lambda t: lerp(DOOR, s1, (t - t0) / dur), 0.9)
    track('fx', dn, t0 + dur / 2, lambda t: lerp(DOOR, s1, (t - t0) / dur), 0.9)
    M.add('perc', logd.play(100), t0 + dur, 0.8, pan_at(s1))
    for i, tw in enumerate(np.arange(22.1, 24.1, 0.4)):       # it lies there twinkling until fetched
        M.add('bells', glock.play(n('C7') if i % 2 == 0 else n('A6'), 80), tw, 0.6, pan_at(s1))
    house += [(22.25, n('A4'), 96, 0.12), (22.42, n('F4'), 96, 0.12), (22.6, n('C4'), 90, 0.2)]  # ho ho ho
    for k, (t, s, T) in enumerate(falls(witch, [1])):         # dash: a scurrying run up D minor
        M.add('winds', oboe.play(n('D5') + [0, 2, 3, 5, 7, 8, 11, 12, 14][k], 96), t, 0.9, pan_at(s))
        M.add('perc', snare.play(60), t, 0.4, pan_at(s))
    M.add('bells', glock.play(n('D7'), 100), 24.0, 0.8, pan_at(2080))   # got it
    for i, m in enumerate(('C#6', 'D6', 'C#6', 'D6', 'C#6', 'D6')):    # and a proper cackle
        M.add('winds', oboe.play(n(m), 100 - 6 * i), 24.15 + 0.07 * i, 0.8, pan_at(2080))
    for k, (t, s, T) in enumerate(falls(witch, [2])):
        c = chord(t)
        M.add('winds', oboe.play(tone(c, [0, 2, 1, 2][k % 4], n('A4')), 92 - 8 * k), t, 0.8, pan_at(s))

    # ---- 19.0-27.6: the pumpkin hops in on the bassoon; a pizzicato spring on each take-off ----
    def hops(legs, vel=96):
        for k, (t, s, T) in enumerate(falls(pump, legs)):
            c = chord(t)
            p = pan_at(s)
            M.add('winds', bsn.play(tone(c, [0, 2, 3, 2][k % 4], n('F2')), vel), t, 1.0, p)
            M.add('perc', logd.play(70), t, 0.45, p)
            M.add('strings', vpizz.play(tone(c, 4, n('C4')), 60), t - 0.62 * T, 0.45, p)

    hops([0])
    ding(28.0, 'F5')
    ding(28.35, 'C5')

    # ---- 28.6-30.7: the house sneezes. Ah... ah... AH... CHOO; the gust blows the pumpkin back ----
    M.add('fx', whoosh(0.85, 300, 1800, 0.35, seed=11), 28.6, 0.7, PD)            # breathing in
    house += [(28.62, n('B4'), 80, 0.3), (28.95, n('D5'), 92, 0.25), (29.2, n('F5'), 104, 0.22)]
    for m in ('C3', 'G3', 'C4', 'E4', 'Bb4', 'C5'):
        house.append((29.45, n(m), 127, 0.4))
    M.add('drums', cym.play(118), 29.45, 0.9, PD)
    M.add('drums', bd.play(120), 29.45, 0.9, PD)
    M.add('perc', vslap.play(110), 29.5, 0.6, PD)
    far_l, far_r = DOOR / 900, (L - DOOR) / 900           # the cold puff runs out of the door both ways
    track('fx', whoosh(far_l + 0.3, 2500, 400, 0.6, seed=12), 29.45, lambda t: DOOR - (t - 29.45) * 900)
    track('fx', whoosh(far_r + 0.3, 2500, 400, 0.6, seed=13), 29.45, lambda t: DOOR + (t - 29.45) * 900)
    for i, m in enumerate(('F3', 'C3', 'A2', 'F2', 'C2', 'A1')):      # the pumpkin rolls backwards
        M.add('winds', bsn.play(n(m), 104 - 6 * i), 29.58 + 0.19 * i, 1.0, pan_at(pump.at(29.58 + 0.19 * i)[0]))
    hops([2], 100)
    for j in range(7, 10):
        t0, dur, s1 = candy[j]
        launch(t0)
        plink(t0 + dur, s1, j - 7)
    house += [(33.75, n('A5'), 70, 0.1), (33.9, n('F5'), 70, 0.15)]                # bless... me
    hops([3], 84)

    # ---- 29.5-36.8: the robot clanks in, a square-wave beep on every step ----
    sq = []
    rf = falls(robot)
    for k, (t, s, T) in enumerate(rf):
        c = chord(t)
        sq.append((t, tone(c, k % 2 * 2, n('F4')), 80, 0.06))
        M.add('perc', brake.play(52), t, 0.5, pan_at(s))
        if t < 37 and k % 2 == 0 and t > 30.6:
            bar_bass(t, c, k // 2, 76, 0.2)

    # ---- 37.0-43.4: copycat. The robot blinks its colours, the house echoes each one back ----
    for t, c in rob_pat:
        sq.append((t, n(ROBOT_NOTE[c]), 112, 0.15))
    for t, c in echo:
        house.append((t, n(ROBOT_NOTE[c]), 100, 0.18))
        house.append((t, n(ROBOT_NOTE[c]) - 12, 80, 0.18))
    house += [(41.75, n('A5'), 90, 0.08), (41.85, n('Bb5'), 90, 0.08), (41.95, n('C6'), 120, 0.3),
              (41.95, n('F6'), 110, 0.3)]                                     # showing off
    for m in ('F2', 'C3', 'F3', 'A3'):
        M.add('harp', harp.play(n(m), 80), 41.9, 0.6, PD)
    for j in range(10, 14):
        t0, dur, s1 = candy[j]
        launch(t0)
        plink(t0 + dur, s1, j - 10)
    for i, tt in enumerate(np.arange(42.05, 42.9, 1 / 18)):               # does not compute
        sq.append((tt, tone('Bo7', int(M.rng.integers(0, 8)), n('B4')), 90, 0.04))
    M.add('fx', zap.play(70), 42.85, 0.4, pan_at(RS))

    # ---- 39.0-47.4: the dragon stomps in on trombone and bass drum; the bee buzzes behind ----
    def stomps(legs, vel):
        for k, (t, s, T) in enumerate(falls(dragon, legs)):
            c = chord(t)
            p = pan_at(s)
            loud = vel if t > 43.3 or t < 37 else vel - 30        # under the copycat it steps quietly
            M.add('brass', tbn.play(tone(c, [0, 2, 1, 2][k % 4], n('F2')), loud), t, 1.0, p)
            M.add('drums', bd_soft.play(loud), t, 0.8, p)

    stomps([0], 108)
    ding(47.7, 'F5')
    ding(48.05, 'C5')
    for m in ('Bb2', 'F3', 'D4'):
        M.add('harp', harp.play(n(m), 80), 48.8, 0.6, PD)
    for j in range(14, 17):
        t0, dur, s1 = candy[j]
        launch(t0)
        plink(t0 + dur, s1, j - 14)
    # 50.7: the giant one for the little bee, a long heavy lob ... THUD
    t0, dur, s1 = GIANT
    track('fx', slide(0.0, dur / 2, 260, 520, dur / 2, 0.4, 0.5), t0, lambda t: lerp(DOOR, s1, (t - t0) / dur))
    track('fx', slide(0.0, dur / 2, 520, 180, dur / 2 + 0.05, 0.4, 0.6), t0 + dur / 2,
          lambda t: lerp(DOOR, s1, (t - t0) / dur))
    M.add('drums', troll.play(50, dur=1.4), t0 + 0.1, 0.4, PD)
    M.add('brass', tbn.play(n('C3'), 90), 51.25, 0.9, pan_at(dragon.at(51.25)[0]))    # the dragon looks back: huh?
    M.add('brass', tbn.play(n('E3'), 96), 51.95, 0.9, pan_at(dragon.at(51.95)[0]))
    M.add('drums', bd.play(124), t0 + dur, 1.0, pan_at(s1))
    M.add('drums', timp.play(110, pitch=-3), t0 + dur, 0.8, pan_at(s1))
    M.add('bells', glock.play(n('F6'), 70), t0 + dur + 0.25, 0.6, pan_at(s1))
    stomps([1], 100)

    # the bee: one long buzz that follows it, pitched up as it sprints to close the gap, down when it lugs the candy
    def bee_at(t):
        if t < 53.6:
            s = dragon.at(t)[0]
            ph = ((t - 39.0) / 2.6) % 1
            gap = 66 + 120 * ph ** 1.6 * (1 - smoothstep(0.82, 1.0, ph)) if t < 47.4 else 40
            gap = lerp(gap, 84, smoothstep(47.4, 48.6, t))
            return s - gap
        return dragon.at(t)[0] - 60 * smoothstep(53.6, 55.0, t) - 20

    bends = []
    for t in np.arange(39.0, 61.0, 0.02):
        ph = ((t - 39.0) / 2.6) % 1
        dash = (smoothstep(0.78, 0.86, ph) * (1 - smoothstep(0.95, 1.0, ph))) if t < 47.4 else 0.0
        lug = smoothstep(52.2, 52.5, t)
        v = 3000 * dash - 2500 * lug + 600 * np.sin(2 * np.pi * (3.2 if t < 52.2 else 1.3) * t)
        if 52.2 <= t < 52.45:
            v -= 5000 * (1 - (t - 52.2) / 0.25)                 # squashed
        bends.append((t - 39.0, int(np.clip(v, -8192, 8191))))
    buzz = M.synth('Leads/Bee').render([(0.0, n('A4'), 70, 22.0)], 22.5, bends=bends)
    track('bee', buzz, 39.0, bee_at)

    # ---- 55.0-61.6: the fearless kid struts in: muted trumpet, walking bass, a rimshot on every step ----
    def strut(fl, big=False):
        for k, (t, s, T) in enumerate(fl):
            c = chord(t)
            p = pan_at(s)
            m = n(CAPE_TUNE[-1] if k == len(fl) - 1 else CAPE_TUNE[k])
            last = k == len(fl) - 1
            if big:                         # open trumpet with a horn a chord tone below, glock on top
                M.add('brass', tpt.play(m, 116), t, 0.9, p)
                M.add('brass', horn.play(max(x for x in range(m - 12, m) if x % 12 in PCS[c]), 104), t, 0.7, 0.15)
                M.add('bells', glock.play(m + 12, 80), t, 0.5, p)
                M.add('drums', bd_soft.play(90), t, 0.6)
                if not last:
                    M.add('drums', snare.play(96), t + T / 2, 0.6)
            else:
                M.add('brass', mute.play(m, 100, dur=T * (0.75 if k % 2 == 0 else 0.4), release=0.1), t, 0.55, p)
            r = root(c, n('F1'))
            M.add('bass', cb.play(r if k % 2 == 0 else r + 7, 92), t, 1.0, p * 0.5)
            M.add('perc', rim.play(90 if big else 70), t, 0.5, p)
            if not last:
                M.add('strings', vpizz.play(tone(c, 1, n('E4')), 66), t + T / 2, 0.55, 0.3)

    strut(cf)
    ding(61.9, 'F5', 110)
    ding(62.25, 'C5', 110)
    for j in range(17, 19):
        t0, dur, s1 = candy[j]
        launch(t0)
        plink(t0 + dur, s1, j - 17)
    M.add('drums', bd_soft.play(60), 63.3, 0.5, PD)                       # door shuts

    # ---- 63.6-64.6: the lamp fizzes out and the night goes with it ----
    for t in (63.65, 63.95, 64.35):
        M.add('fx', zap.play(76), t, 0.45, PD)
    M.add('bass', cbtrem.play(n('F1'), 60, dur=4.0, release=0.4), 64.6, 0.8)

    # ---- 64.6-68.3: red crawls in from both free ends ----
    crawl = lambda t: keys(t, [(64.6, 0), (68.0, 1)])
    for m, edge in (('F3', lambda t: crawl(t) * (DOOR - 60) - 60),
                    ('Ab3', lambda t: 2512 - crawl(t) * (2512 - RS - 60) + 60)):
        tr = vtrem.play(n(m), 100, dur=3.8)
        tr *= np.linspace(0.25, 1.2, tr.shape[1]) ** 1.5      # louder as it gets closer
        track('strings', tr, 64.6, edge, 0.9)
    for i, m in enumerate(('F2', 'Gb2', 'G2', 'Ab2')):            # creeping up a semitone at a time
        M.add('brass', tbn.play(n(m), 70 + 10 * i), 64.6 + 0.85 * i, 0.9, -0.2)
        M.add('brass', horn.play(n(m) + 12, 60 + 10 * i), 64.6 + 0.85 * i, 0.6, 0.2)
    M.add('drums', troll.play(90, dur=3.6), 64.7, 0.8)
    M.add('drums', swell.play(100, dur=3.7), 64.6, 0.6)

    # ---- 68.3-71.0: the roar, three times, then a low growl ----
    for i, p in enumerate(roars):
        t = p - 0.04
        for m in ('B1', 'F2', 'Ab2', 'B2', 'D3', 'F3'):
            M.add('brass', tbn.play(n(m), 124), t, 0.55, -0.15)
            M.add('brass', horn.play(n(m) + 12, 120), t, 0.4, 0.15)
        M.add('drums', bd.play(127), t, 1.0)
        M.add('drums', timp.play(124, pitch=-4 - 2 * i), t, 0.9)
        if i == 0:
            M.add('drums', gong.play(127), t, 1.0)
    M.add('strings', vtrem.play(n('B3'), 90, dur=1.4), 69.4, 0.6, -0.4)
    M.add('strings', vtrem.play(n('D4'), 90, dur=1.4), 69.4, 0.6, 0.4)
    M.add('bass', cbtrem.play(n('F1'), 100, dur=1.4), 69.4, 1.0)

    # ---- 69.9-71.0: the kid winds up ... BOO! The house yelps and leaps away to the end of Side ----
    M.add('drums', sroll.play(100, dur=0.75), 69.9, 0.7, pan_at(RS))
    M.add('fx', slide(0.0, 0.7, 300, 900, 0.7, 0.4, 0.8), 69.9, 0.6, pan_at(RS))
    for m in ('F2', 'C3'):
        M.add('brass', blat.play(n(m), 127), BOO, 1.0, pan_at(RS))
    for m in ('F4', 'A4', 'C5', 'F5'):
        M.add('brass', tpt.play(n(m), 124), BOO, 0.6, pan_at(RS))
    M.add('drums', bd.play(127), BOO, 1.0, pan_at(RS))
    M.add('drums', cym.play(124), BOO, 0.9, pan_at(RS))
    M.add('fx', whoosh(1.6, 300, 3500, 0.5, seed=21), BOO, 0.6)               # the shock ring goes everywhere
    M.add('fx', slide(0.0, 0.14, 650, 2900, 0.42, 0.6, 0.4), 71.0, 1.0, pan_at(1000))   # EEK
    track('fx', whoosh(0.3, 3000, 600, 0.6, seed=22), 71.0, lambda t: keys(t, [(71.0, 2512), (71.25, 260)]))
    M.add('perc', vslap.play(120), 71.05, 0.9, -0.5)
    M.add('drums', timp.play(110, pitch=-1), 71.25, 0.8, pan_at(260))        # slams into the far end
    M.add('drums', timp.play(80, pitch=1), 71.6, 0.5, pan_at(170))

    # ---- 71.4-75.5: it trembles there, shy and purple; the door peeks open ----
    M.add('fx', flex.play(100, dur=4.0), 71.4, 0.8, pan_at(240))
    M.add('strings', vtrem.play(n('C5'), 50, dur=3.8, release=0.8), 71.5, 0.5, pan_at(240))
    shy = [(72.5, 'Db', 'F5'), (73.6, 'Bbm', 'Db5'), (74.7, 'C7', 'E5')]
    for t, c, m in shy:                                       # the house, very quietly: please don't
        for i in range(3):
            hiding.append((t + 0.18 * i, tone(c, i, n('F4')), 54, 0.25))
        M.add('winds', flute.play(n(m), 50, dur=0.9, release=0.3), t + 0.5, 0.5, pan_at(300))
    M.add('perc', guiro.play(70, dur=0.6), 74.7, 0.6, PD)                    # creak
    # ---- 75.5-78.3: the whole bowl ----
    for i, m in enumerate(('F3', 'A3', 'C4', 'F4', 'A4', 'C5')):
        M.add('harp', harp.play(n(m), 96), 75.45 + 0.025 * i, 0.8, PD)
    M.add('bells', gliss.play(90), 75.6, 0.5, PD)
    scale = [0, 2, 4, 5, 7, 9, 10, 12, 14, 16, 17, 19, 21, 22, 24, 26]
    for j in range(16):
        t0, dur, s1 = candy[BOWL + j]
        launch(t0, 70)
        M.add('bells', glock.play(n('F5') + scale[j], 90), t0 + dur, 0.75, pan_at(s1))
    for t in np.arange(75.6 + 1 / 3.2, 78.3, 1 / 3.2):          # the kid hops for joy
        M.add('perc', tamb.play(80), t, 0.5, pan_at(RS))
    for k, t in enumerate(np.arange(75.6, 78.3, 1 / 3.2 * 2)):
        M.add('bass', cb.play(root('F', n('F1')) + [0, 7][k % 2], 90), t, 1.0)
        pizz_chord(t + 1 / 3.2, 'F', 70, 'F4')

    # ---- 78.4-83.6: the kid struts off with the whole band; the house creeps back out behind ----
    strut(xf, big=True)
    for i, m in enumerate(('C5', 'D5', 'E5', 'F5')):            # is it gone?
        hiding.append((81.6 + 0.4 * i, n(m), 52 + 4 * i, 0.2))
    M.add('drums', cym.play(90), 83.6, 0.6)
    M.add('drums', timp.play(100), 83.6, 0.7)
    for m in ('F2', 'C3', 'A3', 'F4'):
        M.add('brass', horn.play(n(m), 96), 83.6, 0.6)
    # ---- 83.6-86: night again; the ghost's first bar, very far away ----
    for i, m in enumerate(('F3', 'C4', 'G4', 'A4', 'C5', 'E5', 'F5')):
        M.add('harp', harp.play(n(m), 64), 84.0 + 0.1 * i, 0.6)
    M.add('winds', flute.play(n('A5'), 54, dur=1.2, release=0.5), 84.3, 0.45, -0.6)

    track('synth', M.synth('Leads/Square').render(sq, D), 0.0, kidpan(robot))
    M.add('house', M.synth('Keys/House Organ').render(house, D), 0.0, 1.0, PD)
    hid = [(71.25, 260), (79.0, 300), (81.5, 300), (83.0, 900)]     # where the shoved-back house is, as in render()
    track('house', M.synth('Keys/House Organ').render(hiding, D), 0.0, lambda t: 0.6 * keys(t, hid))
