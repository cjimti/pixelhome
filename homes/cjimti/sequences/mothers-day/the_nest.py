"""The Nest: A nest of three chicks sits in the front-left corner of the house. Mother bird flies
real 3-D routes to fetch food: a worm from the right wing (crossing the open porch she vanishes in
mid-air and lands on the far side), a firefly that dodges her along the back of the porch, a berry
from the far end of the Side. Each chick cheeps until fed and grows a little. Then they fledge:
the first flies straight off, the second wobbles and hesitates at the edge of the gap, the third
will not go until Mum flies over and nudges it, and they all leave together off the free end."""
import numpy as np
from pixelhome.fx import DT, hexc, light, smoothstep, keys, Flicker, heartbeat, nframes

CODE = 'MO06'
TITLE = 'The Nest'
KIND = 'show'
DESCRIPTION = 'Mother bird flies real 3-D routes round the house (vanishing over the porch gap) to feed three cheeping chicks, then each one fledges in its own way.'

MUM = hexc('#ff6ab8')
CHICK = hexc('#ffd040')
BEAK = hexc('#ff7a60')
NEST = hexc('#ff5a10')
WORM = hexc('#ff3a5a')
FIREFLY = hexc('#c8ff30')
BERRY = hexc('#8a50ff')
GLOW = hexc('#ffb890')


class Track:
    """Linear 3-D waypoints with times; positions between are interpolated."""

    def __init__(self, t0, p0):
        self.ts, self.ps = [t0], [np.asarray(p0, float)]

    def hold(self, dt):
        self.ts.append(self.ts[-1] + dt)
        self.ps.append(self.ps[-1])
        return self

    def fly(self, pts, speed):
        for p in pts:
            p = np.asarray(p, float)
            d = np.linalg.norm(p - self.ps[-1])
            self.ts.append(self.ts[-1] + max(d / speed, 0.05))
            self.ps.append(p)
        return self

    @property
    def end(self):
        return self.ts[-1]

    def __call__(self, t):
        ts = np.array(self.ts)
        ps = np.array(self.ps)
        return np.array([np.interp(t, ts, ps[:, k]) for k in range(3)])


def render(G, seed=26):
    rng = np.random.default_rng(seed)
    n = G.N
    P = G.pos
    pp = G.pos[G.path]
    x = G.pd[G.path]
    L = G.length

    def at(d):
        return np.array([np.interp(d, x, pp[:, k]) for k in range(3)])

    corner = 0.5 * (G.pd[G.seg['Side']].max() + G.pd[G.seg['Left']].min())
    chicks = corner + np.array([-15.0, 0.0, 15.0])
    perch = at(corner + 36)
    WORM_AT, FF_AT, BERRY_AT = 2290.0, 1440.0, 45.0
    left_end, right_start = at(880), at(2040)
    pl_front, pl_back = at(898), at(1305)
    SP = 340.0

    mum = Track(0, perch).hold(6.0)
    mum.fly([at(700), left_end, right_start, at(WORM_AT)], SP)      # trip 1: over the porch gap
    t_worm = mum.end
    mum.hold(2.2)
    t_back1 = mum.end
    mum.fly([right_start, left_end, at(700), at(chicks[0] + 4)], SP)
    t_feed1 = mum.end
    mum.hold(1.2).fly([perch], 120).hold(1.0)
    mum.fly([left_end, pl_front, pl_back, at(FF_AT + 60)], SP)      # trip 2: the firefly dodges
    t_ff = mum.end
    mum.fly([at(FF_AT - 70)], 220).fly([at(FF_AT + 40)], 240).fly([at(FF_AT - 30)], 200).hold(0.8)
    t_back2 = mum.end
    mum.fly([pl_back, pl_front, left_end, at(chicks[2] + 4)], SP)
    t_feed2 = mum.end
    mum.hold(1.2).fly([perch], 120).hold(0.8)
    mum.fly([at(corner), at(BERRY_AT + 20)], SP)                    # trip 3: berry at the far end
    t_berry = mum.end
    mum.hold(1.5)
    t_back3 = mum.end
    mum.fly([at(corner - 2), at(chicks[1] - 3)], SP)
    t_feed3 = mum.end
    mum.hold(1.2).fly([perch], 120)
    t_fledge = mum.end + 2.0
    feeds = [(t_feed1, 0), (t_feed2, 2), (t_feed3, 1)]

    off = np.array([760.0, 150.0, -191.0])
    routes = []
    c1 = Track(0, at(chicks[0])).hold(t_fledge).fly([at(corner + 20), left_end, right_start, at(L), off], 260)
    c2 = Track(0, at(chicks[2])).hold(t_fledge + 4).fly([at(820)], 200).hold(1.8).fly(
        [at(860)], 60).hold(0.6).fly([left_end, right_start, at(L), off], 240)
    t_nudge = c2.end - 1.5
    mum.hold(max(0.0, t_nudge - mum.end)).fly([at(chicks[1] - 12)], 200).hold(0.8)
    t_go = mum.end
    c3 = Track(0, at(chicks[1])).hold(t_go - 0.3).fly([at(chicks[1] + 4)], 50).fly(
        [at(corner + 20), left_end, right_start, at(L), off], 230)
    mum.fly([at(corner + 8), left_end, right_start, at(L), off], 225)
    routes = [(c1, t_fledge, 0), (c2, t_fledge + 4, 2), (c3, t_go, 1)]
    D = float(np.ceil(mum.end + 7))
    out = np.zeros((nframes(D), n, 3))
    trail = np.zeros((n, 3))

    # cheeps
    cheeps = []
    for k in range(3):
        tt = 4.0 + rng.uniform(0, 1)
        while tt < D:
            cheeps.append((tt, k))
            tt += rng.uniform(0.25, 1.1)
    nest_tex = 0.6 + 0.4 * np.abs(np.sin(x * 0.9) * np.sin(x * 0.37))
    fl = Flicker(rng, n, 1.0, 3.0)

    def bird(pos, vel, c, I, size, flap_t, flap_hz):
        d = np.linalg.norm(P - pos, axis=1)
        sp = np.linalg.norm(vel)
        body = np.exp(-(d / (8 * size)) ** 2)
        img = light(c, I * body)
        if sp > 5:
            w = vel / sp
            fl_ = np.sin(2 * np.pi * flap_hz * flap_t)
            span = (10 + 6 * fl_) * size
            for s in (-1, 1):
                dw = np.linalg.norm(P - (pos + s * span * w), axis=1)
                img += light(c, I * 0.75 * (0.55 + 0.45 * fl_) * np.exp(-(dw / (5 * size)) ** 2))
        return img

    for f in range(len(out)):
        t = f * DT
        fr = np.zeros((n, 3))
        env = keys(t, [(0, 0), (1.5, 1), (D - 2.5, 1), (D, 0)])
        # dawn sky, a leafy branch, the nest
        fr += light(hexc('#9070ff'), env * 0.045 * np.ones(n))
        fr[G.path] += light(hexc('#40ff30'), env * 0.11 * (0.7 + 0.3 * np.sin(x * 0.21 + 0.6 * np.sin(0.5 * t))) * smoothstep(130, 60, np.abs(x - corner)))
        fr[G.path] += light(NEST, env * 0.22 * nest_tex * smoothstep(45, 25, np.abs(x - corner)))
        # chicks
        for k in range(3):
            fed = [tf for tf, kk in feeds if kk == k and t > tf]
            size = 1.0 + 0.35 * len(fed) + 0.15 * smoothstep(t_fledge - 3, t_fledge, t)
            gone = [r for r in routes if r[2] == k and t > r[1]]
            if gone:
                tr, t0, _ = gone[0]
                pos = tr(t)
                vel = (tr(t + DT) - tr(t - DT)) / (2 * DT)
                wob = np.array([0, 22 * np.sin(2 * np.pi * 0.9 * (t - t0)) * (k == 2), 0])
                fr += bird(pos + wob, vel, CHICK, 0.75 * env, 1.1, t, 5.5)
                continue
            hungry = 1.0 if not fed else 0.0
            if k == 1 and t_fledge < t < t_go:
                hungry = 0.6                                     # the reluctant one
            open_ = 0.0
            for tc, kk in cheeps:
                if kk == k and 0 < t - tc < 0.14:
                    open_ = np.sin(np.pi * (t - tc) / 0.14)
            open_ *= hungry * (t > 4)
            awake = smoothstep(3, 4.5, t)
            dd = x - chicks[k]
            I = (0.3 + 0.3 * awake + 0.4 * open_) * np.exp(-(dd / (5.5 * size)) ** 2)
            fr[G.path] += light(CHICK, env * I) + light(BEAK, env * 0.6 * open_ * np.exp(-(dd / 2.5) ** 2))
            for tf, kk in feeds:
                if kk == k and 0 < t - tf < 1.5:
                    fr[G.path] += light(GLOW, 0.7 * np.exp(-(t - tf) / 0.4) * np.exp(-(dd / 12) ** 2))
        # food
        if t < t_back1:
            wig = WORM_AT + 4 * np.sin(2 * np.pi * 1.6 * t)
            seg_ = np.exp(-((x - wig) / 3) ** 2) + 0.7 * np.exp(-((x - wig - 7 * np.sin(2 * np.pi * 1.6 * t + 1.2)) / 3) ** 2)
            fr[G.path] += light(WORM, env * 0.5 * seg_)
        if t < t_back2:
            if t < t_ff:
                ffp = FF_AT + 25 * np.sin(0.7 * t)
            else:
                ffp = mum(t)[0] * 0 + np.interp(t, [t_ff, t_back2 - 0.8], [FF_AT + 25 * np.sin(0.7 * t_ff), 0])
                ffp = G.pd[G.path][np.argmin(np.linalg.norm(pp - mum(t), axis=1))] + 25 * np.sin(4 * t) * (t < t_back2 - 1.2)
            blink = np.clip(fl(t)[0] + 0.6, 0, 1)
            fr[G.path] += light(FIREFLY, env * 0.6 * blink * np.exp(-((x - ffp) / 4) ** 2))
        if t < t_back3:
            fr[G.path] += light(BERRY, env * 0.55 * np.exp(-((x - BERRY_AT) / 4) ** 2))
        # mother bird
        pm = mum(t)
        vm = (mum(t + DT) - mum(t - DT)) / (2 * DT)
        fr += bird(pm, vm, MUM, 0.9 * env, 1.45, t, 3.2)
        carrying = (t_worm < t < t_feed1, t_back2 - 0.8 < t < t_feed2, t_berry < t < t_feed3)
        for c, on in zip((WORM, FIREFLY, BERRY), carrying):
            if on:
                sp = np.linalg.norm(vm)
                ahead = pm + (vm / sp * 9 if sp > 5 else 0)
                fr += light(c, 0.6 * env * np.exp(-(np.linalg.norm(P - ahead, axis=1) / 4) ** 2))
        # empty nest, warm
        if t > mum.end - 2:
            e = smoothstep(mum.end - 2, mum.end + 1, t) * env
            fr[G.path] += light(GLOW, e * (0.25 + 0.2 * heartbeat(t, mum.end, 1.2)) * np.exp(-((x - corner) / 60) ** 2))
        trail = np.maximum(trail * 0.88, fr * 0.5)
        out[f] = np.maximum(fr, trail)
    return out
