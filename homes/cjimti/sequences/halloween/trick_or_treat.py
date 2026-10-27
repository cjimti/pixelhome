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
