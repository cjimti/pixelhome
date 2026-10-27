"""Salmon Run: The roofline is a river. It flows from the back of the house (the headwaters, path
start) around every corner and out the free end of the Right wing (the sea). Each corner is a small
waterfall with foam below it. Sockeye (red bodies, green heads) come in from the sea and swim
upstream against the current, holding in the foam below each fall before they leap it; some miss and
slide back. A small late fish fails the last fall three times while the others wait on the Side,
then clears it with a big splash. At the headwaters they spawn: eggs glow in the gravel, the fish
fade into the river, and the eggs are left glowing."""
import numpy as np
from pixelhome.fx import DT, hexc, light, smoothstep, keys, lerp, Flicker, nframes

CODE = 'IP02'
TITLE = 'Salmon Run'
KIND = 'show'
DESCRIPTION = ('The roof is a river and every corner a waterfall. Salmon swim up from the sea, leap '
               'the falls (not always on the first try) and reach the headwaters to spawn.')

DEEP = hexc('#08384a')
WATER = hexc('#1f7f9a')
GLINT = hexc('#b8eef6')
FOAM = hexc('#d8f0f4')
RED = hexc('#e0281e')
HEAD = hexc('#4f8a2a')
SILVER = hexc('#e8d8d0')
EGG = hexc('#ff8a40')
GRAVEL = hexc('#7a4a2a')


class Fish:
    def __init__(self, t_in, speed, size, target, fails, rng):
        self.p = 2530.0
        self.t_in = t_in
        self.speed = speed
        self.size = size
        self.target = target
        self.fails = fails           # {corner index: number of misses}
        self.state = 'wait'
        self.ci = 0
        self.clock = 0.0
        self.p0 = self.p1 = 0.0
        self.miss = False
        self.phase = rng.uniform(0, 6.3)
        self.hold = lambda: rng.uniform(0.6, 2.2)
        self.arrived = None
        self.queue = rng.uniform(0, 22)


def render(G, seed=22):
    rng = np.random.default_rng(seed)
    D = 76.0
    out = np.zeros((nframes(D), G.N, 3))
    d = G.pd
    pp = G.pd[G.path]
    corners = [(pp[k] + pp[k + 1]) / 2 for k in (380, 331, 260, 178, 80)]   # upstream order

    # water: a few travelling ripples with slightly different speeds (no two crests stay together)
    K = 6
    wk = rng.uniform(2 * np.pi / 220, 2 * np.pi / 60, K)
    wv = rng.uniform(42, 70, K)
    wp = rng.uniform(0, 2 * np.pi, K)
    gk = rng.uniform(2 * np.pi / 40, 2 * np.pi / 18, 3)
    gp = rng.uniform(0, 2 * np.pi, 3)
    foam_fl = Flicker(rng, G.N, 1.5, 5.0)
    egg_tw = Flicker(rng, G.N, 0.2, 0.9)

    fish = []
    n_big = 11
    targets = np.linspace(60, 430, n_big + 1)
    order = rng.permutation(n_big)
    for i in range(n_big):
        fails = {}
        for c in range(5):
            if rng.random() < 0.22:
                fails[c] = 1
        fish.append(Fish(3.0 + i * 1.05 + rng.uniform(0, 0.5), rng.uniform(78, 98), rng.uniform(0.95, 1.15),
                         targets[order[i]], fails, rng))
    little = Fish(13.5, 74.0, 0.62, targets[-1], {0: 0, 1: 1, 2: 0, 3: 0, 4: 3}, rng)
    little.hold = lambda: 1.3
    fish.append(little)

    sprays = []                       # (pd, velocity, t0, strength)
    eggs = np.zeros(G.N)
    cheer_t = None

    for f in range(len(out)):
        t = f * DT
        fr = out[f]
        master = keys(t, [(0, 0), (2.5, 1), (72, 1), (76, 0)])
        calm = keys(t, [(60, 1), (70, 0.6)])

        # -- the river
        ph = np.zeros(G.N)
        for k in range(K):
            ph += np.sin(wk[k] * (d - wv[k] * t) + wp[k])
        ph /= np.sqrt(K)
        glint = np.ones(G.N)
        for k in range(3):
            glint *= 0.5 + 0.5 * np.sin(gk[k] * (d - 60 * t) + gp[k] + 0.7 * k * t)
        water_I = 0.13 + 0.05 * ph * calm
        col = lerp(DEEP, WATER, np.clip(0.5 + 0.4 * ph, 0, 1)[:, None])
        fr += light(col, water_I) + light(GLINT, 0.5 * glint ** 3 * calm)
        for c in corners:
            below = d - c
            foam = np.where(below > -3, np.exp(-np.clip(below, 0, None) / 16), 0) * smoothstep(-6, 0, below)
            fr += light(FOAM, foam * (0.22 + 0.12 * foam_fl(t)) * calm)

        # -- the fish (where two overlap, the brighter one is drawn)
        fishI = np.zeros(G.N)
        fishC = np.zeros((G.N, 3))
        for fi in fish:
            if t < fi.t_in:
                continue
            if fi.state == 'wait':
                fi.state = 'swim'
            if fi.state == 'swim':
                goal = corners[fi.ci] + 12 + fi.queue if fi.ci < 5 else fi.target
                burst = 0.75 + 0.45 * np.sin(2 * np.pi * 0.9 * t + fi.phase) ** 2
                step = fi.speed * burst * DT
                if fi.ci == 5:
                    step *= np.clip((fi.p - goal) / 60, 0.08, 1)
                fi.p -= step
                if fi.p <= goal:
                    fi.p = goal
                    if fi.ci < 5:
                        fi.state, fi.clock = 'hold', fi.hold()
                    else:
                        fi.state, fi.arrived = 'home', t
                        if fi is little:
                            cheer_t = t
            elif fi.state == 'hold':
                fi.clock -= DT
                if fi.clock <= 0:
                    misses = fi.fails.get(fi.ci, 0)
                    fi.miss = misses > 0
                    if fi.miss:
                        fi.fails[fi.ci] = misses - 1
                    fi.state, fi.clock = 'leap', 0.0
                    fi.p0 = fi.p
                    for _ in range(5):
                        sprays.append((fi.p + 4, rng.uniform(-50, 60), t, 0.5 * fi.size))
            elif fi.state == 'leap':
                big = fi is little and fi.ci == 4 and not fi.miss
                dur = 1.0 if big else 0.75
                fi.clock += DT / dur
                q = min(fi.clock, 1.0)
                c = corners[fi.ci]
                if fi.miss:
                    if fi is little and fi.ci == 4:
                        k = fi.fails[4]                       # 2, 1, 0 on the three tries
                        reach, back = (8, 6) if k == 2 else ((20, 12) if k == 1 else (12, 60))
                    else:
                        reach, back = 18, 10
                    if q < 0.6:
                        fi.p = fi.p0 - reach * np.sin(np.pi * q / 0.6 * 0.5)
                    else:
                        fi.p = lerp(fi.p0 - reach, fi.p0 + back, smoothstep(0.6, 1.0, q))
                else:
                    fi.p = lerp(fi.p0, c - 32, q)
                if q >= 1:
                    if fi.miss:
                        fi.state, fi.clock = 'swim', 0
                        for _ in range(4):
                            sprays.append((fi.p, rng.uniform(-40, 40), t, 0.4 * fi.size))
                    else:
                        n_sp = 18 if big else 4
                        for _ in range(n_sp):
                            sprays.append((fi.p, rng.uniform(-90, 90) * (2 if big else 1), t,
                                           (0.9 if big else 0.4)))
                        fi.ci += 1
                        fi.state = 'swim'

            # draw: head first (upstream = smaller pd), body trails downstream
            x = (d - fi.p) / fi.size
            body = smoothstep(-7, 0, x) * np.exp(-np.clip(x, 0, None) / 7) * (x < 22)
            wig = 1 + 0.18 * np.sin(0.9 * x - 14 * t + fi.phase)
            leap_glow = 1.0
            if fi.state == 'leap':
                leap_glow = 1 + 0.35 * np.sin(np.pi * min(fi.clock, 1))
            fade = 1.0
            if fi.state == 'home':
                fade = 1 - smoothstep(62 + 0.6 * (fi.target / 60), 67 + 0.6 * (fi.target / 60), t)
                wig = 1 + 0.25 * np.sin(0.6 * x - 5 * t + fi.phase)
                if cheer_t is not None and fi is not little:
                    wig = wig * (1 + 0.6 * np.exp(-((t - cheer_t - 0.2 - 0.04 * fi.target / 10) / 0.25) ** 2))
            I = 0.85 * body * wig * leap_glow * fade * fi.size ** 0.3
            headness = 0.8 * smoothstep(2.5, -1, x)[:, None]
            c_ = lerp(RED, HEAD, headness)
            if fi.state == 'leap':
                c_ = lerp(c_, SILVER, 0.35 * np.sin(np.pi * min(fi.clock, 1)))
            m = I > fishI
            fishI = np.where(m, I, fishI)
            fishC[m] = c_[m]
            if fi.state == 'home' and t > 58:
                eggs = np.maximum(eggs, smoothstep(58, 63, t) * np.exp(-((d - fi.p - 9) / 22) ** 2)
                                  * (0.5 + 0.5 * np.cos(d * 0.9 + fi.phase)) ** 2)

        fr += light(fishC, fishI)

        # -- spray
        alive = []
        spr = np.zeros(G.N)
        for (p0, v, t0, s) in sprays:
            u = t - t0
            if u < 1.2:
                p = p0 + v * u * np.exp(-u * 1.5)
                spr = np.maximum(spr, s * np.exp(-u / 0.35) * smoothstep(0, 0.05, u) * np.exp(-((d - p) / 4) ** 2))
                alive.append((p0, v, t0, s))
        sprays = alive
        fr += light(FOAM, spr)

        # -- the headwaters: gravel beds warm, eggs glow, they outlast the fish
        side = smoothstep(500, 470, d)
        fr += light(GRAVEL, side * 0.12 * smoothstep(55, 62, t))
        fr += light(EGG, eggs * 0.5 * (0.85 + 0.15 * egg_tw(t)))
        fr *= master
    return out
