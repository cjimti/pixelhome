"""Fifty Stars: The house plan is laid over a map of the country (west at the left, north at the back,
Alaska off the back of Side, Hawaii off the front-left corner). Over the loop the states join in
order of statehood, each as a star on the roofline pixel nearest its place on the map. A faint
brass thread runs along the roof from the last star to the new one, the new star blooms and sends a
soft ring outward, then settles to a slow shimmer, so the Union fills in from the east toward the west.
When all fifty are lit, they glow together, then dissolve back to Delaware as the loop wraps."""
import numpy as np
from pixelhome.fx import DT, hexc, light, smoothstep, Flicker, nframes, looped

CODE = 'PR10'
TITLE = 'Fifty Stars'
KIND = 'ambient'
DESCRIPTION = ('The country mapped onto the roof: states join in order of statehood, each a star where it sits '
               'on the map, so the Union fills in from the east to the west over the loop.')

NAVY = hexc('#1e2e9c')
STAR = hexc('#fff0dc')
BRASS = hexc('#ffa030')
FLOOR_COLOR = hexc('#1e2c90')
FLOOR = 0.1
LOOP = 180.0

# (lon, lat) in order of statehood; Alaska and Hawaii placed off the west coast like an inset
STATES = [(-75.5, 39.0), (-77.6, 40.9), (-74.5, 40.1), (-83.4, 32.7), (-72.7, 41.6), (-71.8, 42.3),
          (-76.8, 39.0), (-80.9, 33.9), (-71.6, 43.7), (-78.8, 37.5), (-75.5, 42.9), (-79.4, 35.6),
          (-71.5, 41.7), (-72.7, 44.0), (-85.3, 37.5), (-86.3, 35.9), (-82.8, 40.3), (-92.0, 31.0),
          (-86.3, 39.9), (-89.7, 32.7), (-89.2, 40.0), (-86.8, 32.8), (-69.2, 45.4), (-92.5, 38.4),
          (-92.4, 34.9), (-85.4, 44.3), (-81.7, 28.6), (-99.3, 31.5), (-93.5, 42.1), (-89.8, 44.6),
          (-119.6, 37.2), (-94.3, 46.3), (-120.5, 43.9), (-98.4, 38.5), (-80.6, 38.6), (-116.6, 39.3),
          (-99.8, 41.5), (-105.5, 39.0), (-100.5, 47.5), (-100.2, 44.4), (-109.6, 47.0), (-120.4, 47.4),
          (-114.6, 44.4), (-107.5, 43.0), (-111.7, 39.3), (-97.5, 35.6), (-106.1, 34.4), (-111.7, 34.3),
          (-127.0, 50.5), (-125.0, 26.0)]


def render(G, seed=32):
    rng = np.random.default_rng(seed)
    s = G.pd[G.path]
    P = G.pos[G.path]
    x, z = P[:, 0], P[:, 2]
    lon = np.array([a for a, _ in STATES])
    lat = np.array([b for _, b in STATES])
    mx = np.interp(lon, [-127, -67], [x.min() - 20, x.max() + 20])
    mz = np.interp(lat, [25, 50], [z.max() + 40, z.min() - 30])
    used = np.zeros(G.N, bool)
    slot = []
    for k in range(50):                                   # nearest free pixel, keeping stars apart
        d = np.hypot(x - mx[k], z - mz[k]) + np.where(used, 1e6, 0)
        i = int(np.argmin(d))
        slot.append(i)
        used[max(0, i - 3):i + 4] = True
    ss = s[slot]
    T0, STEP = 3.0, 3.3
    arrive = T0 + STEP * np.arange(50) + 1.6               # bloom time (after the thread arrives)
    prev = np.concatenate([[ss[0] - 150], ss[:-1]])
    dur = np.clip(np.abs(ss - prev) / 700, 0.8, 2.6)       # long threads take longer, never fast
    shim = Flicker(rng, 50, 0.04, 0.15)
    bed = Flicker(rng, G.N, 0.02, 0.08)

    def draw(D):
        out = np.zeros((nframes(D), G.N, 3), np.float32)
        for f in range(len(out)):
            t = f * DT
            buf = light(NAVY, 0.13 * (0.9 + 0.1 * bed(t)))
            all_lit = smoothstep(arrive[-1] + 2, arrive[-1] + 8, t)
            for k in range(50):
                tau = t - arrive[k]
                if tau < -dur[k]:
                    continue
                if tau < 0:                                   # the thread from the previous star
                    a = prev[k]
                    p = a + (ss[k] - a) * smoothstep(-dur[k], 0, tau)
                    trail = np.exp(-((s - p) / 10) ** 2) + 0.4 * np.exp(-((s - p) / 40) ** 2)
                    buf += light(BRASS, 0.2 * trail)
                    continue
                bloom = 0.3 + 0.08 * np.exp(-tau / 1.5) * smoothstep(0, 0.4, tau)
                I = bloom * (0.92 + 0.08 * shim(t)[k]) * (1 + 0.1 * all_lit * np.sin(2 * np.pi * t / 9 + k * 0.4))
                buf += light(STAR, I * np.exp(-((s - ss[k]) / 4) ** 2))
                if tau < 6:                                   # soft ring travelling out along the roof
                    ring = np.exp(-((np.abs(s - ss[k]) - 45 * tau) / 25) ** 2) * np.exp(-tau / 2)
                    buf += light(BRASS, 0.2 * ring)
            out[f][G.path] = buf
        return out
    return looped(draw, LOOP, floor=(FLOOR, FLOOR_COLOR))
