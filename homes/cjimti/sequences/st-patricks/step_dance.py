"""Step Dance: the house is an Irish step dancer seen from the street. The Porch Front is the torso
and the porch sides are the arms held rigid at its sides; they do not move at all. The two wing
fronts, nearest the street, are the stage under the left and right foot. Side is the fiddler's bow,
sawing in time. The feet dance a reel: taps, shuffles, trebles and a travelling run, every strike a
sharp flash with a shock ripple along its wing. Then the music stops dead, one arm twitches, snaps
back, and the dancer finishes with three stamps and a bow."""
import numpy as np
from pixelhome.fx import DT, hexc, perc, light, keys, lerp, smoothstep, nframes

CODE = 'SP05'
TITLE = 'Step Dance'
KIND = 'show'
DESCRIPTION = ('The house dances a reel: the wings are flying feet, the porch a perfectly still upper body, '
               'the side a fiddler\'s bow. Until one arm twitches.')

TORSO = hexc('#00b048')
EMBROIDERY = hexc('#ffb020')
ARM = hexc('#0a7030')
STAGE = hexc('#ff6a10')
SHOE = hexc('#ffb840')
STRIKE = hexc('#fff2d0')
BOW = hexc('#ffa040')
FLASH = hexc('#ffd890')


def render(G, seed=53):
    rng = np.random.default_rng(seed)
    t0, e = 4.0, 60 / 116 / 2                  # a reel at 116 bpm, in eighths
    at = lambda bar, q: t0 + (bar * 8 + q) * e
    D = at(18, 0) + 5.5
    F = nframes(D)
    out = np.zeros((F, G.N, 3))
    n = G.N
    x = G.pd[G.path]
    seg = G.seg_of[G.path]
    wing = {'L': seg == 'Left', 'R': seg == 'Right'}
    lo = {'L': x[wing['L']].min(), 'R': x[wing['R']].min()}
    hi = {'L': x[wing['L']].max(), 'R': x[wing['R']].max()}
    home = {'L': (lo['L'] + hi['L']) / 2, 'R': (lo['R'] + hi['R']) / 2}
    outward = {'L': -1, 'R': 1}                  # toward each wing's outer end
    torso, arms = seg == 'Porch Front', (seg == 'Porch Left') | (seg == 'Porch Right')
    arm_l = seg == 'Porch Left'
    side = seg == 'Side'
    u_t = G.span_u(G.path[torso])
    stitch = np.zeros(n)
    stitch[torso] = np.exp(-((((u_t + 1) * 6) % 1 - 0.5) / 0.12) ** 2)   # gold embroidery, static

    strikes = []                                 # (time, foot, amp, position)
    pos = dict(home)

    def hit(t, f, a, p=None):
        if p is not None:
            pos[f] = float(np.clip(p, lo[f] + 12, hi[f] - 12))
        strikes.append((t, f, a, pos[f]))

    other = {'L': 'R', 'R': 'L'}
    # A: the basic reel, alternate feet on every eighth, drifting
    for k in range(32):
        f = 'L' if k % 2 == 0 else 'R'
        hit(at(2, k), f, 1.0 if k % 8 == 0 else 0.7, home[f] + outward[f] * 40 * np.sin(k * np.pi / 6))
    # B: shuffles, brush out, brush back, tap; alternate foot per beat
    for b in range(16):
        f = 'L' if b % 2 == 0 else 'R'
        tb = at(6, 2 * b)
        hit(tb, f, 0.45, home[f] + outward[f] * 70)
        hit(tb + 0.5 * e, f, 0.45, home[f] + outward[f] * 10)
        hit(tb + e, f, 0.9)
    # C: trebles, three quick strikes per eighth, alternating, travelling outward
    for k in range(32):
        f = 'L' if k % 2 == 0 else 'R'
        travel = home[f] + outward[f] * (120 * k / 31)
        for j, a in enumerate((0.5, 0.5, 0.95)):
            hit(at(10, k) + j * e / 3, f, a, travel + outward[f] * 12 * (j - 1))
    # D: the run, sixteenths, feet sweep out to the far ends and back
    for k in range(32):
        f = 'L' if k % 2 == 0 else 'R'
        u = np.sin(np.pi * k / 31)
        p = lerp(home[f] + outward[f] * 120, (lo[f] if f == 'L' else hi[f]), u)
        hit(at(14, k / 2), f, 0.6 + 0.4 * (k % 4 == 0), p)
    for f in 'LR':
        pos[f] = home[f]
    # bar 16: silence (the twitch); bar 17: three stamps
    T_STOP = at(16, 0)
    T_TWITCH = at(16, 3)
    stamps = [(at(17, 0), 'L'), (at(17, 2), 'R'), (at(17, 4), 'B')]
    for ts, f in stamps:
        for ff in ('LR' if f == 'B' else f):
            strikes.append((ts, ff, 1.3, home[ff]))
    T_FINAL = at(17, 4)
    T_BOW = T_FINAL + 1.2

    S = {f: sorted([s for s in strikes if s[1] == f]) for f in 'LR'}
    fkeys = {f: [(0, home[f])] + [(s[0], s[3]) for s in S[f]] for f in 'LR'}
    st = {f: np.array([s[0] for s in S[f]]) for f in 'LR'}
    sa = {f: np.array([s[2] for s in S[f]]) for f in 'LR'}
    sp = {f: np.array([s[3] for s in S[f]]) for f in 'LR'}

    for fi in range(F):
        t = fi * DT
        fade = keys(t, [(0, 0), (1.5, 1), (D - 2.5, 1), (D - 0.3, 0)])
        fr = np.zeros((n, 3))

        # upper body: perfectly still (except the bow at the end)
        bowd = keys(t, [(T_BOW, 1), (T_BOW + 0.9, 0.35), (T_BOW + 1.6, 0.35), (T_BOW + 2.5, 1)])
        fr += light(TORSO, 0.42 * bowd * fade * torso)
        fr += light(EMBROIDERY, 0.28 * bowd * fade * stitch)
        twitch = keys(t, [(T_TWITCH - 0.01, 0), (T_TWITCH + 0.06, 1), (T_TWITCH + 0.32, 1), (T_TWITCH + 0.38, 0)])
        arm_I = 0.28 * bowd + 0.6 * twitch * arm_l
        fr += light(lerp(ARM, TORSO, twitch * arm_l[:, None]), arm_I * fade * arms)

        # the fiddler's bow on Side: one stroke per beat, frozen when the music stops
        tb = min(t, T_STOP)
        ph = max(tb - (t0 - 2 * e), 0) / (2 * e)
        tri = 2 * np.abs((ph % 2) / 2 - 0.5)        # 1 -> 0 -> 1 over two beats
        tri = tri * tri * (3 - 2 * tri)
        bc = lerp(140, 360, tri)
        bon = keys(t, [(t0 - 2.5, 0), (t0 - 1, 1), (T_FINAL, 1), (T_FINAL + 2, 0.3), (D - 0.5, 0)])
        bow = smoothstep(85, 55, np.abs(x - bc)) * side
        fr += light(BOW, 0.4 * bon * bow + 0.08 * fade * side)

        # the stage and the feet
        for f in 'LR':
            w = wing[f]
            p = float(keys(t, fkeys[f]))
            dt_s = t - st[f]
            past = dt_s >= 0
            flash = (sa[f] * np.exp(-np.where(past, dt_s, 1e3) / 0.09)).max() if past.any() else 0.0
            # time to the next strike: the foot is in the air between strikes
            since = dt_s[past].min() if past.any() else 9.0
            until = -dt_s[~past].max() if (~past).any() else 9.0
            air = float(smoothstep(0.06, 0.22, min(since, until)))
            I_shoe = (0.7 - 0.3 * air + 0.6 * flash)
            fr += light(SHOE, I_shoe * fade * np.exp(-((x - p) / 10) ** 2) * w)
            fr += light(STRIKE, 0.9 * flash * np.exp(-((x - p) / 7) ** 2) * w)
            # shock ripples along the boards from recent strikes
            rec = past & (dt_s < 0.45)
            if rec.any():
                d = np.abs(x[None, :] - sp[f][rec][:, None]) - 700 * dt_s[rec][:, None]
                r = (sa[f][rec][:, None] * np.exp(-(d / 18) ** 2) * np.exp(-dt_s[rec][:, None] / 0.12)).max(0)
                fr += light(STAGE, 0.85 * r * w)
            fr += light(STAGE, 0.1 * fade * w)

        if t >= T_FINAL:                          # the last stamp: one warm flash through the house
            tf = t - T_FINAL
            fr += light(FLASH, 0.7 * np.exp(-tf / 0.25) * np.ones(n))
        out[fi][G.path] = fr
    return out
