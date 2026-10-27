"""Toy Train: A wind-up train runs the whole roofline from the free back end of Side to the free end
of Right: engine with a headlight beam and firebox, tender, four lit coaches and a caboose with a red
tail lamp. The cars are masses on spring couplers, so when the engine brakes for each of the five
corners the train bunches up and stretches out again like a slinky; smoke puffs chuff out of the
stack in time with the wheels. It runs off the right end, comes back round from the back of the
house, and pulls into a stop on the Left wing with a bump that ripples down the train."""
import numpy as np
from pixelhome.fx import DT, hexc, perc, light, keys, smoothstep, lerp, Flicker, nframes

CODE = 'XM02'
TITLE = 'Toy Train'
KIND = 'show'
DESCRIPTION = ('A toy train runs the whole roofline, slowing for every corner so the cars bunch up and '
               'stretch out, chuffing smoke. It leaves at the right end and comes round again from the back.')

RAIL = hexc('#8090b0')
HEAD = hexc('#fff0c8')
ENGINE = hexc('#c01808')
BRASS = hexc('#ffb030')
FIRE = hexc('#ff4000')
WINDOW = hexc('#ffc060')
TAIL = hexc('#ff0800')
SMOKE = hexc('#c0c8d8')
COACH = [hexc(c) for c in ('#108030', '#a01010', '#1840a0', '#a06a08')]
CABOOSE = hexc('#d01008')


def render(G, seed=22):
    rng = np.random.default_rng(seed)
    D = 64.0
    F = nframes(D)
    out = np.zeros((F, G.N, 3))
    x = G.pd[G.path]                                    # track coordinate of each pixel, path order
    Ltr = G.length
    corners = np.array([(x[i] + x[i + 1]) / 2 for i in (80, 178, 260, 331, 380)])
    fire = Flicker(rng, 1, 2, 7)

    # the consist: (kind, body length); fronts are kept apart by springs of rest length body + gap
    cars = [('engine', 48), ('tender', 22)] + [('coach', 34)] * 4 + [('caboose', 30)]
    GAP = 6.0
    rest = np.array([cars[i][1] + GAP for i in range(len(cars) - 1)])
    TRAIN = rest.sum() + cars[-1][1]
    K, C = 60.0, 7.0                                     # coupler stiffness, damping (per unit mass)
    VMAX, VCORNER, ACC = 145.0, 38.0, 60.0

    def vlim(s):
        s = np.atleast_1d(s)
        lim = VMAX - (VMAX - VCORNER) * np.exp(-((s[:, None] - corners[None]) / 45) ** 2).max(1)
        return lim.min()

    def start(front):
        return front - np.concatenate([[0], np.cumsum(rest)]), np.zeros(len(cars))

    pos, vel = start(-20.0)
    run, STOP = 1, 640.0
    puffs = []                                          # [s, t0, size]
    chuff_phase = 0.0
    sleepers = 0.5 + 0.5 * np.cos(2 * np.pi * x / 14)
    t_off = None
    t_stop = None
    loose = False
    whistles = []

    for f in range(F):
        t = f * DT
        fr = np.zeros((G.N, 3))
        # track bed
        rail = keys(t, [(0, 0), (1.5, 0.085), (62, 0.085), (65.5, 0)])
        fr += light(RAIL, rail * (0.75 + 0.25 * sleepers))

        # engine control: speed limit for the corners anywhere under the train, accel limited
        go = t > 2.5 if run == 1 else t > t_off + 3.0
        if go:
            span = np.linspace(pos[0] - 30, pos[0] + 50, 5)
            target = vlim(span)
            if run == 2:
                target = min(target, np.sqrt(max(0.0, 2 * 30 * (STOP - pos[0]))))
        else:
            target = 0.0
        for _ in range(4):
            h = DT / 4
            dv = np.clip(target - vel[0], -ACC * 1.6 * h, ACC * h)
            vel[0] += dv
            if run == 2 and pos[0] >= STOP and vel[0] < 4:
                vel[0] = 0.0
            stretch = (pos[:-1] - pos[1:]) - rest
            rel = vel[:-1] - vel[1:]
            force = K * stretch + C * rel
            if loose:
                force[-1] = 0.0                          # the caboose's coupler has let go
            acc = -0.8 * vel                             # rolling friction
            acc[1:] += force
            acc[1:-1] -= force[1:]
            if loose:
                acc[-1] = -9.0 - 0.3 * vel[-1]           # ...and it rolls back down the grade
            vel[1:] += acc[1:] * h
            pos += vel * h
        if run == 1 and pos[-1] > Ltr + 40 and t_off is None:
            t_off = t
            run = 2
            pos, vel = start(-20.0)

        speed = vel[0]
        if run == 2 and t_stop is None and pos[0] >= STOP - 1 and speed == 0:
            t_stop = t
        if t_stop is not None and not loose and t > t_stop + 3.5:
            loose = True
            whistles += [t + 0.8, t + 2.6, t + 3.2]
        # chuffs: four per wheel turn, a puff of smoke from the stack
        chuff_phase += speed * DT / 22.0
        if chuff_phase >= 1 and speed > 2:
            chuff_phase -= 1
            puffs.append([pos[0] - 10, t, rng.uniform(0.7, 1.1)])
        if run == 2 and t > 50 and speed < 1 and rng.random() < 0.02:
            puffs.append([pos[0] - 10, t, rng.uniform(0.4, 0.7)])

        # toot-toot: two swells of the headlight beam as the engine nears each corner
        for c in list(corners) + [STOP - 60]:
            if pos[0] < c - 110 <= pos[0] + speed * DT:
                whistles.append(t)
        toot = sum(np.exp(-((t - w - d) / 0.09) ** 2) for w in whistles for d in (0.0, 0.32))

        # cars
        for i, (kind, ln) in enumerate(cars):
            a, b = pos[i] - ln, pos[i]
            body = smoothstep(a - 1.5, a + 1.5, x) * (1 - smoothstep(b - 1.5, b + 1.5, x))
            if not body.any():
                continue
            u = np.clip((x - a) / ln, 0, 1)
            if kind == 'engine':
                rod = 0.5 + 0.5 * np.sin(2 * np.pi * (x - a) / 12 - pos[0] / 6)
                fr += light(ENGINE, 0.45 * body * (u < 0.62))
                fr += light(BRASS, 0.3 * body * (u >= 0.62) + 0.12 * body * rod * (u < 0.62))
                fl = 0.75 + 0.25 * fire(t)[0]
                fr += light(FIRE, 0.7 * fl * np.exp(-((x - (a + 7)) / 4) ** 2))
                fr += light(HEAD, 1.0 * np.exp(-((x - (b - 1)) / 2.2) ** 2))
                ahead = x - b
                beam = np.where(ahead > 0, np.exp(-ahead / 55) * (0.5 + 0.5 * smoothstep(0, 6, ahead)), 0)
                fr += light(HEAD, (0.38 + 0.5 * toot) * beam)
            elif kind == 'tender':
                fr += light(BRASS, 0.22 * body)
            elif kind == 'coach':
                c = COACH[(i - 2) % 4]
                fr += light(c, 0.42 * body)
                win = sum(np.exp(-((x - (a + ln * w)) / 2.6) ** 2) for w in (0.22, 0.5, 0.78))
                fr += light(WINDOW, 0.6 * win * body)
            else:
                fr += light(CABOOSE, 0.42 * body)
                fr += light(WINDOW, 0.45 * np.exp(-((x - (a + ln * 0.5)) / 3) ** 2) * body)
                lamp = 0.85 + 0.15 * np.sin(2 * np.pi * 1.5 * t)
                fr += light(TAIL, lamp * np.exp(-((x - (a + 1)) / 2.2) ** 2))
            # couplers: a little brass glint when they are pulled taut or crushed
            if i > 0:
                st = abs((pos[i - 1] - pos[i]) - rest[i - 1])
                fr += light(BRASS, min(1, st / 4) * 0.5 * np.exp(-((x - (b + GAP / 2)) / 2) ** 2))

        # smoke: drifts back, swells, fades
        keep = []
        for p in puffs:
            age = t - p[1]
            if age > 2.8:
                continue
            keep.append(p)
            p[0] -= 6 * DT
            w = 5 + 9 * age
            amp = p[2] * 0.42 * np.exp(-age / 0.9) * smoothstep(0, 0.12, age)
            cloud = amp * np.exp(-((x - p[0]) / w) ** 2)
            fr *= 1 - 0.9 * cloud[:, None]             # smoke hides the cars under it
            fr += light(SMOKE, cloud)
        puffs = keep

        out[f][G.path] = fr * keys(t, [(D - 3, 1), (D - 0.5, 0)])
    return out
