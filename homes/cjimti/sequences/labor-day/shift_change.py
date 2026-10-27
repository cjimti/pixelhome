"""Shift Change: The porch is the factory; each worker is one small light.

The day shift (warm amber) works the porch. The steam whistle on the Porch Front blows twice; its
sound rolls out over the house as a ring in 3-D. The day shift files out both porch sides and along
the wings to the two free ends, queueing at the corners like a real crowd (each walker keeps its
distance from the one ahead and slows to turn), and bobs with its stride. The night shift (cool
blue) walks in from both ends at the same time; every time two workers pass, they high-five. One
day worker has fallen asleep on Porch Right, z's floating up the run. A night worker nudges him,
twice, nothing. The whistle toots once; he jolts awake and sprints out off the right end."""
import numpy as np
from pixelhome.fx import DT, hexc, light, smoothstep, keys, Flicker, nframes

CODE = 'LB04'
TITLE = 'Shift Change'
KIND = 'show'
DESCRIPTION = ('The porch is the factory. The whistle blows, the day shift files out to both ends while the night '
               'shift files in, high-fiving as they pass. One worker slept through it.')

DAY = hexc('#ffa23c')
NIGHT = hexc('#8cb6ff')
STEAM = hexc('#e6edf5')
RING = hexc('#ffe2a8')
FIVE = hexc('#ffd040')
WASH_DAY = hexc('#ff8a30')
WASH_NIGHT = hexc('#5f84d8')


class Walkers:
    """A file of walkers moving one way along the path; nobody overtakes. Leader is index 0."""

    def __init__(self, x0, direction, v_want, t_go, target=None):
        self.x = np.array(x0, float)
        self.d = direction
        self.v_want = np.array(v_want, float)
        self.t_go = np.array(t_go, float)
        self.target = None if target is None else np.array(target, float)
        self.v = np.zeros(len(self.x))
        self.stride = np.zeros(len(self.x))

    def step(self, t, corners, gap=11.0, headway=0.5):
        n = len(self.x)
        for i in range(n):
            if t < self.t_go[i]:
                self.v[i] = 0
                continue
            v = self.v_want[i]
            if np.min(np.abs(self.x[i] - corners)) < 14:       # slow to turn a corner
                v *= 0.55
            if i > 0:
                room = (self.x[i - 1] - self.x[i]) * self.d - gap
                v = min(v, max(0.0, room / headway))
            if self.target is not None:
                to_go = (self.target[i] - self.x[i]) * self.d
                v = min(v, max(0.0, to_go * 1.4))
            self.v[i] += np.clip(v - self.v[i], -160 * DT, 120 * DT)
            self.x[i] += self.d * self.v[i] * DT
            self.stride[i] += self.v[i] * DT


def blob(s, x, w):
    return np.exp(-((s[None] - np.atleast_1d(x)[:, None]) / w) ** 2)


def render(G, seed=24):
    rng = np.random.default_rng(seed)
    D = 56.0
    F = nframes(D)
    out = np.zeros((F, G.N, 3))
    s = G.pd[G.path]
    L = G.length
    P3 = G.pos[G.path]
    corners = np.array([(s[a] + s[a + 1]) / 2 for a in (80, 178, 260, 331, 380)])
    porch = (s > s[179] - 2) & (s < s[380] + 2)
    mid = s[296]
    whistle_pos = G.pos[G.path[296]]

    spots = np.linspace(s[184], s[376], 15)
    i_sleep = 13                                  # the spot nearest the front of Porch Right
    sleeper_x = spots[i_sleep] + 12
    left_spots = spots[spots < mid]
    right_spots = [x for k, x in enumerate(spots) if x >= mid and k != i_sleep]
    right_spots = np.array(right_spots)

    # day shift: leaders are the ones nearest their exit
    dl = np.sort(left_spots)                       # moving to s = 0, leader = smallest
    dr = np.sort(right_spots)[::-1]                # moving to s = L, leader = largest
    day_l = Walkers(dl, -1, rng.uniform(62, 88, len(dl)), 7.2 + rng.uniform(0, 2.5, len(dl)))
    day_r = Walkers(dr, +1, rng.uniform(62, 88, len(dr)), 7.2 + rng.uniform(0, 2.5, len(dr)))
    # night shift: enter from the free ends, deepest spot first
    nl_t = np.sort(left_spots)[::-1]
    nr_t = np.sort(np.append(right_spots, sleeper_x - 30))
    night_l = Walkers(np.full(len(nl_t), -15.0), +1, rng.uniform(70, 95, len(nl_t)),
                      10.0 + 1.3 * np.arange(len(nl_t)) + rng.uniform(0, 0.5, len(nl_t)), nl_t)
    night_r = Walkers(np.full(len(nr_t), L + 15.0), -1, rng.uniform(70, 95, len(nr_t)),
                      11.0 + 1.3 * np.arange(len(nr_t)) + rng.uniform(0, 0.5, len(nr_t)), nr_t)
    jitter_ph = rng.uniform(0, 2 * np.pi, 60)
    blasts = [(5.5, 1.6), (7.6, 1.8), (43.5, 0.45)]
    fives = []                                    # (t, s)
    met = set()
    steam_fl = Flicker(rng, G.N, 1.5, 5.0)
    zs = [(t0, sleeper_x) for t0 in np.arange(14.0, 43.0, 2.6)]
    nudger = int(np.argmin(np.abs(nr_t - (sleeper_x - 30))))   # parked next to the sleeper

    sprint_x, sprint_v = sleeper_x, 0.0
    trail = np.zeros(G.N)

    for f in range(F):
        t = f * DT
        buf = np.zeros((G.N, 3))
        end = 1 - smoothstep(52.5, 55.8, t)

        for w in (day_l, day_r, night_l, night_r):
            w.step(t, corners)
        # the nudger walks over to the sleeper and back
        if 36.5 < t < 42.5:
            nx = keys(t, [(36.5, nr_t[nudger]), (38.0, sleeper_x - 9), (38.6, sleeper_x - 9), (38.75, sleeper_x - 5),
                          (38.95, sleeper_x - 9), (39.6, sleeper_x - 9), (39.75, sleeper_x - 5),
                          (39.95, sleeper_x - 9), (41.0, sleeper_x - 9), (42.4, nr_t[nudger])])
            night_r.x[nudger] = nx

        # factory wash: warm while the day shift works, cool once the night shift is in
        warm = keys(t, [(0, 0.0), (1.5, 0.11), (8, 0.11), (14, 0.0)])
        cool = keys(t, [(16, 0.0), (30, 0.1)])
        buf += light(WASH_DAY, warm * porch) + light(WASH_NIGHT, cool * porch)

        def draw(w, col, k0):
            for i in range(len(w.x)):
                x = w.x[i]
                if x < -30 or x > L + 30:
                    continue
                bob = 0.85 + 0.15 * np.cos(2 * np.pi * w.stride[i] / 38.0) if w.v[i] > 3 else 1.0
                idle = 0.0
                if w.v[i] < 3:                     # at work: small shuffles
                    idle = 2.2 * np.sin(0.7 * t + jitter_ph[k0 + i])
                fade = smoothstep(-25, 0, x) * smoothstep(L + 25, L, x)
                buf[:] += light(col, 0.78 * bob * fade * blob(s, x + idle, 6.0)[0])

        if t < 52:
            draw(day_l, DAY, 0)
            draw(day_r, DAY, 15)
            draw(night_l, NIGHT, 30)
            draw(night_r, NIGHT, 45)

        # high fives where opposite walkers meet
        for a_name, A, B in (('l', day_l, night_l), ('r', day_r, night_r)):
            for i in range(len(A.x)):
                for j in range(len(B.x)):
                    if (a_name, i, j) in met or A.v[i] < 3 or B.v[j] < 3:
                        continue
                    if abs(A.x[i] - B.x[j]) < 3.0:
                        met.add((a_name, i, j))
                        fives.append((t, 0.5 * (A.x[i] + B.x[j])))
        for t0, x0 in fives:
            u = t - t0
            if 0 <= u < 0.6:
                buf += light(FIVE, 1.0 * np.exp(-u / 0.2) * blob(s, x0, 5.0)[0])
                buf += light(FIVE, 0.5 * np.exp(-u / 0.25) * (blob(s, x0 - 60 * u, 2.5)[0] + blob(s, x0 + 60 * u, 2.5)[0]))

        # the sleeper
        if t < 44.2:
            breath = 0.32 + 0.12 * np.sin(2 * np.pi * t / 4.2)
            nudge = sum(np.exp(-((t - tn) / 0.12) ** 2) for tn in (38.85, 39.85)) * 0.25
            buf += light(DAY, (breath + nudge) * blob(s, sleeper_x, 6.0)[0])
            if t > 12:
                for t0, x0 in zs:                 # z's drift up the run (away from the street)
                    u = t - t0
                    if 0 <= u < 3.5 and t0 < 43.5:
                        zx = x0 - 18 - 26 * u + 5 * np.sin(3 * u)
                        buf += light(NIGHT * 0.5 + DAY * 0.5, 0.3 * np.sin(np.pi * u / 3.5) * blob(s, zx, 2.6)[0])
        else:                                     # awake! jolt, then sprint off the right end
            u = t - 44.2
            if u < 0.5:
                buf += light(DAY, (1.0 - u) * blob(s, sleeper_x, 6.0)[0])
            else:
                a = 900.0
                near_corner = np.min(np.abs(sprint_x - corners)) < 18
                v_cap = 160.0 if near_corner else 420.0
                sprint_v = min(sprint_v + a * DT, v_cap)
                sprint_x += sprint_v * DT
                stride_bob = 0.8 + 0.2 * np.cos(2 * np.pi * (sprint_x / 30.0))
                cur = 0.8 * stride_bob * blob(s, sprint_x, 4.5)[0] * (sprint_x < L + 20)
                trail = np.maximum(trail * 0.86, cur * 0.5)
                buf += light(DAY, np.maximum(cur, trail))

        # the whistle: steam at the porch front centre, a sound ring through the house
        for t0, dur in blasts:
            u = t - t0
            if -0.1 < u < dur + 2.5:
                on = smoothstep(0, 0.12, u) * (1 - smoothstep(dur, dur + 0.5, u))
                plume = np.exp(-((s - mid) / (14 + 22 * min(u, dur))) ** 2)
                buf += light(STEAM, 0.75 * on * plume * (0.8 + 0.2 * steam_fl(t)))
                r = np.linalg.norm(P3 - whistle_pos, axis=1)
                for k in range(3):                # pressure fronts, emitted while it blows
                    ue = u - k * dur / 3
                    if ue > 0 and k * dur / 3 < dur:
                        front = 520 * ue
                        buf += light(RING, 0.38 * np.exp(-ue / 1.6) * np.exp(-((r - front) / 30) ** 2))
        out[f][G.path] = np.clip(buf * end, 0, 1)
    return out
