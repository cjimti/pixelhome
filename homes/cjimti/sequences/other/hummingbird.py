"""Hummingbird: Trumpet flowers open along the roofline over a dim green garden. A hummingbird darts
in from the Right wing's free end and works the flowers one by one: quick darts that overshoot and
settle, hovering with a tiny jitter, backing away (hummingbirds fly backward) while still facing the
flower. Each flower it drinks from dims and slowly refills. Its throat is iridescent: the gorget
only flashes ruby when the bird turns to face the street, so it winks on and off as the bird turns
its head, and on the porch walls whenever it faces out. A rival comes in at the Side's free end; they
square off, then the owner chases it out of the garden. In victory it does the U-shaped display
dive, swinging back and forth through the U of the house (Left wing, down the porch, back up to the
Right wing) with a bright chirp at the bottom of each swing, then drinks once more and zips away."""
import numpy as np
from pixelhome.fx import DT, hexc, light, smoothstep, keys, lerp, Flicker, nframes

CODE = 'OT27'
TITLE = 'Hummingbird'
KIND = 'show'
DESCRIPTION = ('A hummingbird works the flowers along the roof, darting, hovering and backing up, its '
               'throat flashing ruby when it faces you. It chases off a rival and does its U-shaped dive through the porch.')

LEAF = hexc('#1f5a2a')
FLOWERS = [hexc('#ff3020'), hexc('#ff7a1a'), hexc('#d02a8a')]
BODY = hexc('#3ae07a')
WINGS = hexc('#9ad8c0')
GORGET = hexc('#ff1a4a')
RIVAL_GORGET = hexc('#ff7a10')
RIVAL_BODY = hexc('#c88a3a')
CHIRP = hexc('#ffd0e0')


def render(G, seed=31):
    rng = np.random.default_rng(seed)
    D = 67.0
    F = nframes(D)
    out = np.zeros((F, G.N, 3))
    d = G.pd
    L = G.length
    pp = G.pos[G.path]
    pdp = G.pd[G.path]
    tang = np.gradient(pp, pdp, axis=0)
    tang /= np.linalg.norm(tang, axis=1, keepdims=True)

    def tz(s):
        """How much the path direction at s points toward the street (+z)."""
        return np.interp(s, pdp, tang[:, 2])

    def tx(s):
        return np.interp(s, pdp, tang[:, 0])

    flower_s = np.array([150, 420, 640, 960, 1200, 1485, 1780, 2150, 2400], float)
    flower_c = np.array([FLOWERS[i % 3] for i in range(len(flower_s))])
    flower_open = np.array([5.5, 4.8, 4.2, 3.6, 3.0, 2.4, 3.3, 3.9, 4.5])
    nectar = np.ones(len(flower_s))
    sway = Flicker(rng, G.N, 0.1, 0.4)

    def at(i, side=1):           # hover spot just off flower i, on the given side, facing it
        return flower_s[i] + 7 * side, -side

    # hero schedule: (time, target, facing)  facing 0 = face the way it flies
    H = [(0.0, 2620, 0)]
    H += [(8.0, *at(8)), (10.8, 2432, -1), (11.4, *at(7)), (14.2, *at(6)), (17.2, *at(5)), (20.4, *at(4)),
          (23.4, *at(3)), (25.8, 990, -1), (26.4, *at(2)), (29.2, *at(1)), (32.0, *at(0)),
          (34.4, 185, -1), (36.9, -140, 0), (38.6, 40, -1), (40.0, 640, 0), (41.6, 1210, 0),
          (56.3, *at(5)), (61.0, 1520, -1), (61.6, 2640, 0)]
    R = [(0.0, -150, 0), (33.6, 112, 1), (35.2, 128, 1), (35.9, 105, 1), (36.7, -200, 0)]
    DIVE0, DIVE1 = 43.5, 55.5
    centre = G.pd[G.seg['Porch Front']].mean()

    class Bird:
        def __init__(self, sched, w):
            self.sched = sched
            self.s = float(sched[0][1])
            self.v = 0.0
            self.w = w
            self.yaw_p = rng.uniform(0, 6.3)

        def target(self, t):
            cur = self.sched[0]
            for e in self.sched:
                if e[0] <= t:
                    cur = e
            return cur

        def update(self, t):
            _, tgt, face = self.target(t)
            w, z = self.w, 0.55                     # a little under-damped: darts overshoot and settle
            a = w * w * (tgt - self.s) - 2 * z * w * self.v
            self.v += a * DT
            self.s += self.v * DT
            return face

    hero, rival = Bird(H, 7.5), Bird(R, 8.5)
    jit = Flicker(rng, 2, 2.0, 6.0)
    prev_draw = {}
    chirps = []
    trail = {}

    def draw_bird(fr, key, s, v, face, t, body_c, gorget_c, scale=1.0):
        # facing in 3-D: along the path, plus a head-turning yaw while hovering
        hovering = abs(v) < 60
        dirn = face if (face != 0 and abs(v) < 400) else (np.sign(v) or 1)
        off = 0.0 if key == 'h' else 2.1
        yaw = (0.75 * np.sin(2 * np.pi * 0.45 * t + off) + 0.3 * np.sin(2 * np.pi * 1.3 * t + off)) \
            if hovering else 0.0
        fx_, fz_ = dirn * tx(s), dirn * tz(s)
        fz = fz_ * np.cos(yaw) + fx_ * np.sin(yaw)       # rotate the facing about the vertical
        flash = smoothstep(0.35, 0.85, fz)
        s0 = prev_draw.get(key, s)
        prev_draw[key] = s
        # motion blur: a short streak from the previous position when fast
        lo, hi = min(s0, s), max(s0, s)
        dist = np.where(d < lo, lo - d, np.where(d > hi, d - hi, 0))
        core = np.exp(-(dist / 4.5) ** 2) * (1 / (1 + (hi - lo) / 40))
        haze = np.exp(-(dist / 12) ** 2) * (0.5 + 0.5 * np.sin(2 * np.pi * 7 * t)) * hovering
        fr += light(body_c, 0.75 * scale * core) + light(WINGS, 0.26 * scale * haze)
        fr += light(gorget_c, 0.95 * scale * flash * np.exp(-(dist / 4.0) ** 2))
        trail[key] = np.maximum(trail.get(key, 0) * 0.9, 0.5 * scale * core * (hi - lo > 3))
        fr += light(body_c, 0.5 * trail[key])

    for f in range(F):
        t = f * DT
        fr = out[f]
        master = keys(t, [(0, 0), (2, 1), (64, 1), (67, 0)])
        col = light(LEAF, 0.13 * (1 + 0.2 * sway(t)))

        # -- the birds
        hf = hero.update(t)
        if DIVE0 <= t < DIVE1:                     # the display dive: a pendulum through the U
            u = t - DIVE0
            amps = [(0.0, 0.0), (1.0, 800.0), (5.0, 650.0), (8.5, 480.0), (11.0, 250.0), (12.0, 0.0)]
            A = float(np.interp(u, [p[0] for p in amps], [p[1] for p in amps]))
            ph = 2 * np.pi * u / 4.0
            s_new = centre - A * np.cos(ph) * smoothstep(0, 1.0, u) + (1 - smoothstep(0, 1.0, u)) * (1210 - centre)
            hero.v = (s_new - hero.s) / DT
            hero.s = s_new
            if abs(np.sin(ph)) > 0.999 and A > 300 and (not chirps or t - chirps[-1] > 1.0):
                chirps.append(t)
            hf = 0
        rival.update(t)
        jj = jit(t)
        draw_bird(fr, 'h', hero.s + 1.2 * jj[0] * (abs(hero.v) < 60), hero.v, hf, t, BODY, GORGET)
        if 33 < t < 39:
            draw_bird(fr, 'r', rival.s + 1.2 * jj[1] * (abs(rival.v) < 60), rival.v, rival.target(t)[2], t,
                      RIVAL_BODY, RIVAL_GORGET, 0.9)
        for tc in chirps:
            u = t - tc
            if 0 <= u < 0.8:
                fr += light(CHIRP, 0.55 * np.exp(-((d - centre) / (20 + 300 * u)) ** 2) * np.exp(-u / 0.2))

        # -- drinking: a hovering bird right at a flower empties it; flowers refill slowly
        for i, fs in enumerate(flower_s):
            if abs(hero.s - fs) < 10 and abs(hero.v) < 40:
                nectar[i] = max(0.25, nectar[i] - 0.35 * DT)
            else:
                nectar[i] = min(1.0, nectar[i] + 0.03 * DT)
        opn = smoothstep(flower_open, flower_open + 2.0, t) * (1 - smoothstep(60, 64, t - 0.3 * np.arange(9)))
        rel = d[None, :] - flower_s[:, None]
        g = np.exp(-(rel / (3 + 13 * opn[:, None])) ** 2) * (0.55 + 0.45 * np.cos(rel / 4.5) ** 2)
        I_f = (g * (opn * (0.18 + 0.32 * nectar))[:, None])
        k = I_f.argmax(0)
        col = col + light(flower_c[k], I_f.max(0))
        fr[:] = (fr + col) * master
    return out
