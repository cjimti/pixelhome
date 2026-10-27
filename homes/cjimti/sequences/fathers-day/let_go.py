"""Let Go: Dad teaches the kid to ride, starting from the garage at the free end of Right. The bike
is simulated: speed eases toward what the rider can manage, slows for every corner, and wobbles. The
track it leaves shows the wobble (a weaving front wheel lays down a broken, dashed track; a steady
one a clean streak). First try, a fall and a hug. Second, round the first corner. Third, half way
along the porch, Dad lets go and stops; the kid doesn't notice, rides on, looks back, wobbles,
steadies, and goes all the way round the house and out the back end of Side. Dad glows. Then the
bell, and the kid rides back in to him."""
import numpy as np
from pixelhome.fx import DT, hexc, perc, light, smoothstep, keys, lerp, heartbeat, Flicker, nframes

CODE = 'FA06'
TITLE = 'Let Go'
KIND = 'show'
DESCRIPTION = ('Learning to ride: Dad runs alongside holding the seat, the track wobbles, there is a fall. '
               'Then he lets go on the porch, and the kid rides all the way round the house without him.')

KID = hexc('#70e8e0')
WHEEL = hexc('#e8f4ff')
DAD = hexc('#ffb060')
TRACK = hexc('#ffd890')
DUSK = hexc('#3a2c60')
OUCH = hexc('#ff5040')


def render(G, seed=26):
    rng = np.random.default_rng(seed)
    D = 66.0
    n = G.N
    F = nframes(D)
    out = np.zeros((F, n, 3))
    x = G.pd[G.path]
    corners = np.array([x[80], x[178], x[260], x[331], x[380]])
    garage = x[500] - 14
    let_go_at = x[296]

    # ---- pass 1: the ride, simulated
    s = np.zeros(F); dadp = np.zeros(F); wob = np.zeros(F); hold = np.zeros(F, bool)
    vis = np.ones(F)
    pos, v, dpos, dv = garage, 0.0, garage + 16, 0.0
    phase = 0.0
    released, t_rel, t_look, gone_t = False, None, None, None
    crash = 8.6
    for f in range(F):
        t = f * DT
        if t < 4.0:
            vt, A = 0.0, 0.0
        elif t < crash:
            vt, A = 55.0, 0.9
        elif t < 12.5:
            vt, A = 0.0, 0.0
            v = 0.0 if t < crash + DT * 1.5 else v
        elif t < 19.5:
            vt, A = 85.0, 0.55
        elif t < 22.5:
            vt, A = 0.0, 0.2
        elif not released:
            vt, A = lerp(100, 150, smoothstep(22.5, 27, t)), lerp(0.4, 0.16, smoothstep(22.5, 27, t))
        else:
            u = t - t_rel
            vt = lerp(150, 270, smoothstep(1, 9, u))
            A = 0.12 * (1 - smoothstep(0, 3, u))
            if t_look is not None:
                A += 0.7 * np.exp(-((t - t_look - 0.6) / 0.7) ** 2)
        dc = np.min(np.abs(corners - pos))
        vt *= 1 - 0.6 * np.exp(-(dc / 70) ** 2)
        v += (vt - v) * min(1, DT / 0.9)
        if gone_t is None:
            pos -= v * DT
        phase += 2 * np.pi * lerp(1.1, 1.6, min(1, v / 150)) * DT
        if not released and t > 22.5 and pos <= let_go_at:
            released, t_rel = True, t
        if released and t_look is None and pos < x[200]:
            t_look = t
        if gone_t is None and pos < -30:
            gone_t = t
        # Dad holds the seat until he lets go, then slows to a stop
        if not released:
            dpos = pos + 16
            dv = v
        else:
            dv *= np.exp(-DT / 0.5)
            dpos -= dv * DT
        s[f], dadp[f], wob[f], hold[f] = pos, dpos, A * np.sin(phase), not released
        if gone_t is not None:
            vis[f] = 0.0
    # ---- the return: in from the back end of Side, steady and quick, braking beside Dad
    t_ret = gone_t + 7.0
    stop_at = dadp[-1] - 26
    dur = (stop_at + 30) / 210 * 1.45
    for f in range(F):
        t = f * DT
        if t >= t_ret:
            u = min(1.0, (t - t_ret) / dur)
            e = 1 - (1 - u) ** 2.2
            s[f] = -30 + (stop_at + 30) * e
            vis[f] = 1.0
            wob[f] = 0.0
    t_home = t_ret + dur
    assert t_home < D - 8, (gone_t, t_home)

    # ---- pass 2: draw it
    trail = np.zeros(n)
    tw = Flicker(rng, n, 0.05, 0.3)
    for f in range(F):
        t = f * DT
        buf = np.zeros((n, 3))
        fade = keys(t, [(0, 0), (2.5, 1), (D - 4, 1), (D, 0)])
        buf += light(DUSK, 0.1 * fade * (1 + 0.1 * tw(t)))

        # the track: laid where the bike is, broken by the wobble
        dep = np.exp(-((x - s[f]) / 5) ** 2) * vis[f] * (t > 4)
        lay = 0.4 * (1 - 0.95 * np.clip(np.abs(wob[f]) / 0.35, 0, 1))
        trail = np.maximum(trail * np.exp(-DT / 5.0), dep * lay)
        buf += light(TRACK, trail)

        # Dad
        dI = 0.55
        dw = 16.0
        if crash <= t < 12.5:                         # the fall, and the hug
            u = t - crash
            dI = 0.55 + 0.3 * smoothstep(0.4, 1.0, u) * (1 - smoothstep(3.0, 3.9, u))
            dw = 16 + 14 * smoothstep(0.4, 1.0, u) * (1 - smoothstep(3.0, 3.9, u))
        if t_rel is not None and t > t_rel + 2:      # watching: pride, a slow warm heartbeat
            pr = smoothstep(t_rel + 2, t_rel + 6, t)
            dI = 0.55 + pr * (0.15 + 0.2 * heartbeat(t, t_rel + 4, 1.6))
            dw = 16 + 8 * pr
            spread = pr * 0.12 * np.exp(-((x - dadp[f]) / 140) ** 2) * (1 - smoothstep(t_home, t_home + 3, t))
            buf += light(DAD, spread)
        dpx = dadp[f] if (t_rel is None or t < t_home - 0.5) else dadp[f]
        buf += light(DAD, dI * np.exp(-((x - dpx) / dw) ** 2) * fade)

        # the bike: rider and two wheels; the front wheel weaves with the wobble
        if vis[f] > 0 and t > 2.5:
            kI = 0.8 * fade
            kc = KID
            spread = 9.0
            if crash <= t < 11.2:
                u = t - crash
                kI = 0.8 * (0.35 + 0.65 * smoothstep(1.2, 2.6, u))
                spread = 9 + 8 * np.exp(-u / 0.5)
                kc = lerp(KID, OUCH, np.exp(-u / 0.35))
            fw = s[f] - 9 - 4 * wob[f]
            buf += light(kc, kI * np.exp(-((x - s[f]) / spread) ** 2))
            buf += light(WHEEL, 0.45 * kI * (np.exp(-((x - fw) / 3.5) ** 2) + np.exp(-((x - s[f] - 9) / 3.5) ** 2)))
            if t_look is not None and t_look <= t < t_look + 0.5:   # looks back: where's Dad?
                buf += light(WHEEL, 0.6 * np.exp(-(t - t_look) / 0.15) * np.exp(-((x - s[f] - 20) / 5) ** 2))
            if t >= t_ret:                            # headlamp on the way back
                buf += light(WHEEL, 0.15 * np.exp(-np.clip(x - s[f], 0, None) / 60) * (x > s[f]))
        # the bell: ring-ring as the kid pulls up
        for tb in (t_home - 0.9, t_home - 0.55):
            if tb <= t < tb + 0.3:
                buf += light(WHEEL, 0.8 * np.exp(-(t - tb) / 0.07) * np.exp(-((x - s[f]) / 14) ** 2))
        # together at the end
        if t > t_home:
            tg = smoothstep(t_home, t_home + 2, t)
            mid = (s[f] + dadp[f]) / 2
            buf += light(lerp(DAD, KID, 0.3), 0.25 * tg * fade * np.exp(-((x - mid) / 90) ** 2))

        out[f][G.path] = np.clip(buf * keys(t, [(D - 4, 1), (D - 0.5, 0)]), 0, 1)
    return out
