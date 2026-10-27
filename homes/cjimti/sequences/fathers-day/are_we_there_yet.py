"""Are We There Yet?: one road trip along the whole roofline, from the free back end of Side to the
porch light at the free end of Right. The sky goes from afternoon through a sunset that burns at the
destination end into night with stars; headlights come on and pick the dashed centre line out of the
dark; towns light up at each corner as the car goes by. From the back seat: are-we-there-yet, four
syllables rising, again and again, closer and closer together, each answered by Dad's flat "No."
Then he pulls over, hazards on, and turns the car around. Silence. The kid falls asleep, and wakes
up just as they arrive."""
import numpy as np
from pixelhome.fx import DT, hexc, perc, light, smoothstep, keys, lerp, Flicker, nframes

CODE = 'FA07'
TITLE = 'Are We There Yet?'
KIND = 'show'
DESCRIPTION = ('A road trip along the whole roof, afternoon to night. Are we there yet? No. Are we there yet? '
               'No. Faster and faster, until Dad pulls over and turns the car around.')

DAY = hexc('#6aa8f0')
SUNSET = hexc('#ff6a30')
NIGHT = hexc('#101848')
STAR = hexc('#e0e8ff')
HEAD = hexc('#fff4e0')
TAIL = hexc('#ff1000')
ASK = hexc('#ff70d0')
NO = hexc('#ffa040')
HAZARD = hexc('#ff9000')
ROAD = hexc('#ffd040')
TOWN = hexc('#ffb860')
SLEEP = hexc('#8060ff')
CAR = hexc('#c0d0e0')


def render(G, seed=27):
    rng = np.random.default_rng(seed)
    D = 78.0
    n = G.N
    out = np.zeros((nframes(D), n, 3))
    x = G.pd[G.path]
    L = G.length
    dest = x[500] - 6

    car = [(2.0, -25), (31.2, 1150), (33.8, 1150), (35.3, 1085), (36.4, 1085), (38.0, 1140), (67.5, dest - 30),
           (68.6, dest - 22)]
    turn = [(0, 1.0), (33.3, 1.0), (33.7, -1.0), (35.4, -1.0), (35.8, 1.0)]
    hazards = (31.3, 35.9)
    asks = [6.0, 13.5, 19.5, 23.8, 26.6, 28.3, 29.4, 30.1, 30.6, 31.0]
    nos = [(7.4, 0.5), (14.9, 0.45), (20.8, 0.4), (25.0, 0.3), (27.7, 0.25)]
    stub = 37.6                                        # "are we-" ... (a look from the front seat)
    glare = 38.2
    asleep = (40.0, 69.2)
    wake = 69.6
    yes = 71.6

    stars = (rng.uniform(0, 1, n) > 0.9).astype(float)
    star_tw = Flicker(rng, n, 0.05, 0.25)
    dashes = (((x / 28.0) % 1) < 0.45).astype(float)
    windows = (rng.uniform(0, 1, n) > 0.55).astype(float) * rng.uniform(0.5, 1.0, n)
    towns = [x[80], x[178], x[260], x[331], x[380]]
    town_mask = sum(np.exp(-((x - c) / 55) ** 2) for c in towns) * windows
    town_lit = np.zeros(n)
    flick = Flicker(rng, n, 0.2, 0.7)

    def syll(t, t0, k=4, step=0.17, dur=0.12, rise=True):
        e = 0.0
        for i in range(k):
            ts = t0 + i * step
            if ts <= t < ts + dur:
                a = (0.55 + 0.45 * i / (k - 1)) if rise else 0.6
                e = max(e, a * np.sin(np.pi * (t - ts) / dur))
        return e

    for f in range(len(out)):
        t = f * DT
        buf = np.zeros((n, 3))
        fade = keys(t, [(0, 0), (2.0, 1), (74.5, 1), (78, 0)])
        s = keys(t, car)
        d = keys(t, turn)

        # the sky: afternoon, a sunset burning at the destination end, night
        day = keys(t, [(0, 1), (16, 1), (26, 0)])
        sun = keys(t, [(14, 0), (22, 1), (28, 0.6), (33, 0)])
        night = keys(t, [(22, 0), (32, 1)])
        sky = light(DAY, 0.2 * day * np.ones(n))
        sky += light(SUNSET, 0.4 * sun * np.exp(-(L - x) / 1100) + 0.08 * sun)
        sky += light(NIGHT, 0.12 * night * np.ones(n))
        sky += light(STAR, 0.25 * night * stars * np.clip(0.6 + 0.6 * star_tw(t), 0, 1))
        buf += sky * fade

        # towns at the corners, lit while the car goes through them
        near = np.exp(-((x - s) / 260) ** 2)
        town_lit = np.maximum(town_lit * np.exp(-DT / 6), near * (1 - day))
        buf += light(TOWN, 0.42 * town_mask * town_lit * (1 + 0.08 * flick(t)))

        # headlights after dusk: a beam ahead along the road, dashes picked out
        lights_on = smoothstep(21, 23, t)
        ahead = (x - s) * np.sign(d)
        beam = np.exp(-np.clip(ahead, 0, None) / 110) * (ahead > 4) * lights_on
        buf += light(HEAD, 0.22 * beam * (1 - 0.6 * dashes))
        buf += light(ROAD, 0.4 * beam * dashes)
        # the car: headlamps in front, tail lamps behind; a body you can see by daylight
        front = s + 9 * d
        back = s - 9 * d
        buf += light(CAR, 0.35 * day * np.exp(-((x - s) / 10) ** 2))
        buf += light(HEAD, (0.35 + 0.5 * lights_on) * np.exp(-((x - front) / 3.5) ** 2))
        brake = 1.0 + 1.5 * (hazards[0] - 0.6 < t < hazards[0] + 0.3) + 1.2 * (67.4 < t < 69)
        buf += light(TAIL, (0.3 + 0.25 * lights_on) * min(brake, 2.2) / 2.2 * 1.6 * np.exp(-((x - back) / 3.5) ** 2))

        # are we there yet? four rising syllables from the back seat, and an echo
        for ta in asks + [wake]:
            slow = ta == wake
            e = syll(t, ta, step=0.3 if slow else 0.17, dur=0.22 if slow else 0.12)
            if e > 0:
                buf += light(ASK, 1.0 * e * np.exp(-((x - s) / 18) ** 2))
            age = t - (ta + (0.9 if slow else 0.51))
            if 0 <= age < 1.2:
                r = 18 + 520 * age
                ring = np.exp(-((np.abs(x - s) - r) / 30) ** 2)
                buf += light(ASK, 0.45 * np.exp(-age / 0.5) * ring)
        e = syll(t, stub, k=2, step=0.17, dur=0.12)
        if e:
            buf += light(ASK, 0.5 * e * np.exp(-((x - s) / 12) ** 2))
        # "No." flat and low, from the front seat
        for tn, a in nos:
            if tn <= t < tn + 0.5:
                e = np.sin(np.pi * (t - tn) / 0.5)
                buf += light(NO, a * 1.4 * e * np.exp(-((x - s) / 40) ** 4))
        if glare <= t < glare + 1.2:                  # a look in the mirror
            e = np.sin(np.pi * (t - glare) / 1.2)
            buf += light(NO, 0.55 * e * np.exp(-((x - s) / 60) ** 2))

        # pulled over: hazards, and then he turns the car around
        if hazards[0] <= t < hazards[1]:
            on = ((t - hazards[0]) * 1.6) % 1 < 0.5
            halo = np.exp(-((x - s) / 26) ** 2)
            buf += light(HAZARD, 0.75 * on * halo)

        # asleep: a slow violet breath in the back seat
        if asleep[0] <= t < asleep[1]:
            z = smoothstep(asleep[0], asleep[0] + 2, t) * (1 - smoothstep(asleep[1] - 0.5, asleep[1], t))
            br = 0.5 + 0.5 * np.sin(2 * np.pi * (t - asleep[0]) / 4.5)
            buf += light(SLEEP, 0.3 * z * (0.4 + 0.6 * br) * np.exp(-((x - s) / 16) ** 2))

        # the destination: a porch light at the end of the road, then YES
        pl = keys(t, [(50, 0), (62, 0.5), (71.6, 0.6)])
        buf += light(TOWN, pl * np.exp(-((x - x[500]) / 12) ** 2))
        if t >= yes:
            u = t - yes
            wave = np.clip((520 * u - (x[500] - x)) / 200, 0, 1)
            warm = 0.32 * wave * keys(t, [(yes, 1), (75, 1), (78, 0.4)])
            buf += light(TOWN, warm * (1 + 0.05 * flick(t)))
            buf += light(hexc('#ffffff'), 0.6 * np.exp(-u / 0.25) * np.exp(-((x - x[500]) / 60) ** 2))

        out[f][G.path] = np.clip(buf * keys(t, [(D - 4, 1), (D - 0.5, 0)]), 0, 1)
    return out
