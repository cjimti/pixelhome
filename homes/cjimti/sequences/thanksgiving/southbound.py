"""Southbound: a waltz at 120 (a bar is 1.5 s). The roofline is a sunset sky, gold over the Right wing, through
orange and rose to violet over the Left wing and the Side, with streaks of cloud drifting through it. Honks off
past the free end of Right flash its tip, and a V of nine geese flies in: each bird a bright cream body whose
wings flap open and shut on every beat, a ripple of downstrokes running back through the line, a golden
slipstream streaming out behind. Over the porch a headwind hits: cloud streaks rush at them, gusts slam through
on every bar, the V is pushed into a tight, struggling knot flapping double time, and the leader tires, dims and
drifts back to the tail while the second bird takes the point with a honk. The V snaps back into order with a
shared flash and a band of light thrown out to both ends. While they cruise the Left wing practising, a honk
rippling down the line every bar, a late straggler bursts in off the free end of Right on a long bright wake,
honking, sprints the length of the house, overshoots the whole V, and sheepishly drops back to the tail. The V
wheels round on the Left wing in a spinning burst of gold, crosses back with the wind behind it, and over the
porch spreads out until birds fill the whole house, flashing down the line on the beat; then it closes up,
sprints, and is gone off the free end of Right. The sunset flares: rose sweeps round the whole outline and back
in gold, and as the dusk settles stars pop out one to a beat, and a shooting star crosses the house."""
import numpy as np
from pixelhome.fx import DT, hexc, light, keys, smoothstep, lerp, colormap, nframes

CODE = 'TG17'
TITLE = 'Southbound'
KIND = 'show'
DESCRIPTION = ('A V of geese crosses the sunset. A headwind knocks them into a knot, the leader drops back, a late '
               'straggler overshoots the whole flock, and they wheel round and fill the house before flying off.')
VOICEOVER = "The geese are heading south for the winter, and somebody is running late."

D = 90.0
SEED = 17
BEAT, BAR = 0.5, 1.5                   # 3/4 at 120


def bt(b):
    return b * BAR


N_V = 9                                # the V; the straggler is bird N_V
LAG = 0.6                              # each bird is this many seconds behind the one ahead, on the leader's path
T_IN = bt(4)                           # 6: the V comes in off the Right end
T_WIND, T_CALM = bt(12), bt(20)        # 18-30: the headwind
T_TIRE = (bt(14), bt(18))              # the leader drops back through the line
T_POINT = bt(18)                       # the second bird takes the point
T_REFORM = bt(20)                      # 30
T_STRAG, T_OVER, T_BACK, T_JOIN = bt(24), 41.0, bt(28), bt(30)
T_TURN = bt(32)                        # 48: the V wheels round on the Left wing
T_SPREAD = (bt(38), bt(42))            # 57-63: spread out over the whole house
T_GONE = bt(47)                        # 70.5: the sunset flares
T_DUSK = bt(51)                        # 76.5
T_SHOOT = 84.0

GOOSE = hexc('#fff4e0')
HALO = hexc('#ffd890')
WAKE = hexc('#ffa828')
GOLD = hexc('#ffb020')
ROSE = hexc('#ff3a70')
SUN = hexc('#fff0b0')
STAR = hexc('#e8f0ff')
EARLY = colormap([(-0.1, hexc('#4a0890')), (0.0, hexc('#7010a0')), (0.3, hexc('#e01060')),
                  (0.6, hexc('#ff4010')), (0.85, hexc('#ff9a10')), (1.0, hexc('#ffc040'))])
LATE = colormap([(-0.1, hexc('#0c0850')), (0.0, hexc('#200c70')), (0.3, hexc('#6a1080')),
                 (0.6, hexc('#c01848')), (0.85, hexc('#ff4a08')), (1.0, hexc('#ff6a10'))])

# the leader's path: in off the Right end, slowed to a crawl by the headwind over the porch, easing to a stop on the
# Left wing, then back at 120, and a sprint out
TAU = np.arange(-30.0, 100.0, 0.01)
VK = [(-30, -85.0), (T_WIND, -85.0), (T_WIND + 3, -22.0), (bt(19), -22.0), (bt(21), -55.0), (T_TURN, 0.0),
      (T_TURN + 2.5, 120.0), (63.0, 120.0), (68.0, 330.0), (100, 330.0)]


def _traj():
    v = np.interp(TAU, [k[0] for k in VK], [k[1] for k in VK])
    p = np.concatenate([[0.0], np.cumsum((v[1:] + v[:-1]) / 2 * 0.01)])
    return p + 2560.0 - np.interp(T_IN, TAU, p), v


TRAJ, VEL = _traj()


def at(tau):
    return np.interp(tau, TAU, TRAJ)


def heading(tau):
    return np.sign(np.interp(tau, TAU, VEL) + 1e-9)


def lag_step(t):
    """Seconds between birds: wide over the whole house while they show off, tight for the sprint out."""
    return LAG + 0.7 * smoothstep(T_SPREAD[0], T_SPREAD[0] + 3, t) * (1 - smoothstep(T_SPREAD[1], T_SPREAD[1] + 3, t)) \
        - 0.1 * smoothstep(T_SPREAD[1] + 2, T_SPREAD[1] + 4, t)


def birds(seed=SEED):
    rng = np.random.default_rng(seed)
    return rng.uniform(0.6, 1.4, N_V), rng.uniform(0, 2 * np.pi, N_V)


def straggler(t):
    """The straggler: the sprint in, the overshoot past the leader, the drop back to its place at the tail."""
    slot = at(t - lag_step(t) * N_V)
    if t < T_STRAG:
        return 2700.0
    sprint = 2620 - 360 * (t - T_STRAG)
    over = at(t) - 90
    if t < T_OVER:
        return max(sprint, over)
    if t < T_BACK:
        return over
    if t < T_JOIN:
        return float(lerp(over, slot, smoothstep(T_BACK, T_JOIN, t)))
    return slot


def lags(t, jf, jp):
    """How far behind the leader's path each bird of the V is, in seconds."""
    step = lag_step(t)
    L = step * np.arange(N_V, dtype=float)
    L[0] = step * (N_V - 1) * smoothstep(*T_TIRE, t)
    L[1:] -= step * smoothstep(T_TIRE[0] + 1, T_TIRE[1], t)
    mess = smoothstep(T_WIND, T_WIND + 2, t) * (1 - smoothstep(T_REFORM - 1.5, T_REFORM, t))
    L += mess * 0.5 * np.sin(2 * np.pi * jf * t + jp) * (L > 0.4)
    return np.maximum(L, 0)


def positions(t, jf, jp):
    """Every bird's path position and heading; the straggler last."""
    L = lags(t, jf, jp)
    p = np.append(at(t - L), straggler(t))
    h = np.append(heading(t - L), -1.0 if t < T_JOIN else heading(t - lag_step(t) * N_V))
    return p, h, L


def calls(seed=SEED):
    """Every honk: (time, bird, loudness). Bird -1 is the flock out of sight past the Right end."""
    rng = np.random.default_rng(seed + 1)
    out = [(1.5, -1, 0.4), (2.5, -1, 0.5), (3.5, -1, 0.6), (4.25, -1, 0.65), (5.0, -1, 0.75)]

    def chatter(t, t1, lo, hi, who):
        while t < t1:
            out.append((round(t, 2), int(rng.choice(who)), rng.uniform(0.55, 0.85)))
            t += rng.uniform(lo, hi)

    chatter(7.0, T_WIND, 0.8, 1.6, range(N_V))
    out += [(T_WIND + 0.5 + k * 0.4, int(rng.integers(N_V)), 0.8) for k in range(6)]   # the wind hits: alarm
    out += [(T_TIRE[0] + 0.5, 0, 0.45), (T_TIRE[0] + 2.5, 0, 0.35)]                   # the leader, tiring
    out += [(T_POINT, 1, 1.0), (T_POINT + 0.25, 1, 0.95)]                             # the second takes the point
    out += [(T_REFORM, k, 0.75) for k in (1, 2, 3)]
    for b in range(2):                                                                 # practising: down the line
        out += [(bt(22 + b) + 0.12 * k, (k + 1) % N_V, 0.6) for k in range(N_V)]
    out += [(T_STRAG + 0.6 * k, N_V, 0.95) for k in range(9)]
    out += [(T_STRAG + 1.5, 0, 0.7), (T_STRAG + 3.0, 0, 0.75)]                       # the tail answers
    out += [(T_OVER, N_V, 1.0), (T_OVER + 0.25, N_V, 1.0), (T_OVER + 0.3, 1, 0.9), (T_OVER + 0.5, 2, 0.9)]
    out += [(T_BACK + 1.0, N_V, 0.4)]                                                  # sorry
    out += [(T_JOIN + 0.12 * k, k % N_V, 0.85) for k in range(10)]                     # it's in: everyone
    chatter(T_TURN + 3, T_SPREAD[0], 0.6, 1.2, range(N_V + 1))
    out += [(T_SPREAD[1] + 2.5, -2, 0.0)]
    chatter(T_SPREAD[1] + 2, 67.0, 0.5, 1.0, range(N_V + 1))
    out += [(69.0, -1, 0.7), (71.0, -1, 0.6), (74.0, -1, 0.45), (80.0, -1, 0.3), (86.0, -1, 0.2)]
    return sorted(o for o in out if o[1] != -2)


def ripple_times():
    """While spread out, a flash runs down the line on every beat."""
    return list(np.arange(T_SPREAD[0] + 2 * BEAT, T_SPREAD[1] + 1.0, BEAT))


def stars(seed=SEED):
    rng = np.random.default_rng(seed + 5)
    t = T_DUSK + np.arange(18) * BEAT
    return list(zip(t, rng.uniform(520, 2480, 18), rng.uniform(0, 2 * np.pi, 18)))


def render(G, seed=SEED):
    F = nframes(D)
    out = np.zeros((F, G.N, 3))
    pdp = G.pd[G.path]
    xp = G.pos[G.path, 0]
    u = np.clip((xp - xp.min()) / (xp.max() - xp.min()), 0, 1)
    u = np.where(pdp < 490, -0.1 * (490 - pdp) / 490, u)          # the Side: deeper violet toward the back
    sky_early, sky_late = EARLY(u), LATE(u)
    jf, jp = birds(seed)
    honks = calls(seed)
    ht = np.array([h[0] for h in honks])
    rip = np.array(ripple_times())
    st = stars(seed)
    wind_p = 0.0
    tw = np.arange(F) * DT
    wind_v = np.interp(tw, [0, T_WIND - 0.5, T_WIND + 0.5, T_CALM - 1, T_CALM + 1, T_TURN + 1, T_TURN + 3, 66, 70, 90],
                       [70, 70, 520, 520, 70, 70, -380, -380, 60, 40])

    for f in range(F):
        t = f * DT
        wind_p += wind_v[f] * DT
        dusk = smoothstep(8, 82, t)
        sky_col = lerp(sky_early, sky_late, dusk)
        I_sky = keys(t, [(0, 0.0), (2, 0.36), (66, 0.34), (T_GONE, 0.32), (T_DUSK, 0.3), (88, 0.24), (90, 0.08)])
        strong = abs(wind_v[f]) / 520
        streak = 0.5 + 0.5 * np.cos(2 * np.pi * (pdp - wind_p) / (260 - 90 * strong))
        streak2 = 0.5 + 0.5 * np.cos(2 * np.pi * (pdp - 0.6 * wind_p) / 410 + 1.3)
        sky = I_sky * (0.65 + (0.35 + 0.45 * strong) * streak ** 2 + 0.2 * streak2)
        gust = 0.0
        if T_WIND <= t < T_CALM:                                     # a gust slams through on every bar
            ub = ((t - T_WIND) / BAR) % 1.0
            head = 492 + 2600 * ub
            gust = 0.45 * np.exp(-((pdp - head) / 160) ** 2) * (pdp > 400)

        p, hd, L = positions(t, jf, jp)
        d = pdp[None, :] - p[:, None]                                 # (birds, pixels)
        on = (p > -150) & (p < 2650)
        rank = np.append(L / max(lag_step(t), 0.1), N_V)
        lead = int(np.argmin(L))

        # wings: open and shut on every beat, a ripple of downstrokes back down the line; double time in the wind
        rate = 1.0 + 1.0 * smoothstep(T_WIND, T_WIND + 1, t) * (1 - smoothstep(T_CALM - 1, T_CALM, t))
        ph = t / BEAT * rate - 0.09 * rank
        ph[N_V] = t / BEAT * (2.0 if T_STRAG <= t < T_OVER else 1.0)
        wing = 0.5 + 0.5 * np.cos(2 * np.pi * ph)
        bright = np.full(N_V + 1, 0.9)
        bright[0] = keys(t, [(0, 0.9), (T_TIRE[0], 0.9), (T_TIRE[0] + 2, 0.45), (T_REFORM, 0.5), (T_REFORM + 2, 0.9)])
        wing[0] = lerp(wing[0], 0.3 + 0.2 * np.cos(2 * np.pi * t / (2 * BEAT)),
                       smoothstep(T_TIRE[0], T_TIRE[0] + 2, t) * (1 - smoothstep(T_REFORM, T_REFORM + 2, t)))
        flash = np.zeros(N_V + 1)
        rings = np.zeros(G.N)
        for i in np.nonzero((t - ht >= 0) & (t - ht < 0.7))[0]:
            th, who, amp = honks[i]
            uu = t - th
            if who < 0:                                              # out of sight: the Right end glows
                rings += amp * 0.7 * np.exp(-uu / 0.2) * np.exp(-((pdp - 2512) / 90) ** 2)
                continue
            flash[who] += amp * 0.6 * np.exp(-uu / 0.12)
            r = np.abs(pdp - p[who])
            rings += amp * 0.4 * np.exp(-((r - 300 * uu) / 24) ** 2) * np.exp(-uu / 0.3)
        for tr in rip[(t - rip >= 0) & (t - rip < 1.2)]:              # spread out: a flash runs down the line
            for k in range(N_V + 1):
                flash[k] += 0.7 * np.exp(-max(0.0, t - tr - 0.06 * rank[k]) / 0.1) * (t - tr >= 0.06 * rank[k])
        if T_REFORM <= t < T_REFORM + 1.5:
            flash[:N_V] += 0.7 * np.exp(-(t - T_REFORM) / 0.2)

        span = 7 + 15 * wing                                          # wingtips out from the body
        body = (bright + flash)[:, None] * np.exp(-(d / 6.5) ** 2)
        tips = (0.55 + 0.3 * flash)[:, None] * (np.exp(-((d - span[:, None]) / 5) ** 2)
                                                 + np.exp(-((d + span[:, None]) / 5) ** 2))
        halo = (0.3 + 0.1 * (np.arange(N_V + 1) == lead))[:, None] * np.exp(-(d / 34) ** 2)
        behind = -d * hd[:, None]
        wk = np.full(N_V + 1, 0.16)
        wk[N_V] = 0.6 if T_STRAG <= t < T_BACK else 0.16
        wlen = np.full(N_V + 1, 70.0)
        wlen[N_V] = 260.0 if T_STRAG <= t < T_BACK else 70.0
        trail = np.exp(-behind / wlen[:, None]) * (1 - np.exp(-(behind / 12) ** 2))
        wake = wk[:, None] * np.where(behind > 0, trail, 0)
        body, tips, halo, wake = (a * on[:, None] for a in (body, tips, halo, wake))
        notch = 1 - 0.8 * np.max(np.exp(-(d / 26) ** 2) * on[:, None], 0)

        # the slipstream: golden ripples streaming out behind the tail of the V
        tail = p[:N_V][np.argmax(L)] if t < T_JOIN else p[N_V]
        hdt = heading(t - L.max())
        bt_ = (tail - pdp) * (-hdt)                                    # distance behind the tail
        slip = np.where(bt_ > 0, np.exp(-bt_ / 420) * (0.5 + 0.5 * np.cos(2 * np.pi * (bt_ / 80 - 2.2 * t))), 0)
        slip *= keys(t, [(0, 0), (T_IN, 0), (T_IN + 2, 0.3), (T_WIND, 0.3), (T_WIND + 1, 0.1), (T_CALM, 0.1),
                         (T_CALM + 1, 0.3), (68, 0.3), (70, 0)]) * float(-200 < tail < 2700)

        buf = light(1.0, sky * notch) * sky_col
        buf += light(SUN, keys(t, [(0, 0.0), (2, 0.8), (40, 0.65), (64, 0.35), (72, 0.0)])
                     * np.exp(-((pdp - 2505) / (30 + 50 * (1 - smoothstep(10, 70, t)))) ** 2))
        buf += light(1.0, gust * np.ones(G.N))[:, :] * sky_col * 1.4
        buf += light(WAKE, slip)
        # the reform: a band of light thrown out to both ends
        if T_REFORM <= t < T_REFORM + 3:
            uu = t - T_REFORM
            c = p[:N_V].mean()
            buf += light(GOLD, 0.6 * np.exp(-((np.abs(pdp - c) - 900 * uu) / 110) ** 2) * np.exp(-uu / 1.2))
        # the wheel: a spinning burst of gold round the turn
        if T_TURN - 1.5 <= t < T_TURN + 4:
            uu = t - (T_TURN - 1.5)
            c = at(T_TURN)
            rr = np.abs(pdp - c)
            reach = 120 + 340 * smoothstep(0, 2.5, uu)
            spin = 0.5 + 0.5 * np.cos(2 * np.pi * (rr / 70 - 3.0 * uu) + np.sign(pdp - c) * 2 * np.pi * pdp / 180)
            env = smoothstep(0, 1.0, uu) * (1 - smoothstep(3.5, 5.5, uu))
            buf += light(GOLD, env * 0.75 * spin * np.exp(-(rr / reach) ** 4))
            if T_TURN <= t < T_TURN + 1.5:
                buf += light(SUN, 0.8 * np.exp(-(t - T_TURN) / 0.25) * np.exp(-(rr / 90) ** 2))
        buf += light(HALO, np.clip(halo.sum(0), 0, 0.6))
        buf += light(WAKE, np.clip(wake.sum(0), 0, 0.7))
        buf += light(GOOSE, np.clip((body + tips).sum(0), 0, 1.0))
        buf += light(GOOSE, np.clip(rings, 0, 0.7))
        # the sunset flares: rose round the whole outline, and back in gold
        if T_GONE <= t < T_DUSK + 1:
            uu = t - T_GONE
            h1 = 2560 - 1000 * uu
            h2 = -100 + 1000 * (uu - 2 * BAR)
            buf += light(ROSE, 0.8 * np.exp(-((pdp - h1) / 200) ** 2) + 0.35 * np.clip((pdp - h1) / 300, 0, 1)
                         * (1 - smoothstep(2 * BAR, 3 * BAR, uu)))
            if uu > 2 * BAR:
                buf += light(GOLD, 0.8 * np.exp(-((pdp - h2) / 200) ** 2) + 0.3 * np.clip((h2 - pdp) / 300, 0, 1)
                             * (1 - smoothstep(4 * BAR - 1, 4 * BAR, uu)))
        # dusk: stars pop out one to a beat and twinkle; a shooting star
        for ts, ps, pp in st:
            if t >= ts:
                a = t - ts
                twk = 0.7 + 0.3 * np.sin(2 * np.pi * 0.8 * t + pp)
                lvl = 0.9 * np.exp(-a / 0.15) + 0.6 * twk * smoothstep(0, 0.4, a)
                buf += light(STAR, lvl * np.exp(-((pdp - ps) / 4.5) ** 2) * keys(t, [(88.5, 1.0), (90, 0.3)]))
                if a < 0.6:
                    buf += light(STAR, 0.3 * np.exp(-a / 0.2) * np.exp(-((np.abs(pdp - ps) - 250 * a) / 15) ** 2))
        if T_SHOOT <= t < T_SHOOT + 1.4:
            uu = t - T_SHOOT
            hp = 600 + 2100 * uu
            tr = pdp - hp
            buf += light(STAR, np.where(tr < 0, 0.95 * np.exp(tr / 160), np.exp(-(tr / 6) ** 2)) * (1 - uu / 1.4)
                         * (pdp < 2512))
        out[f][G.path] = buf
    return np.clip(out, 0, 1)


# ---------------------------------------------------------------- music ----------------------------------------------
# A brisk waltz in D, 3/4 at 120, the bar the lights' story is cut to: an oom-pah-pah of basses, pizzicato and harp
# under a violin tune while the V crosses. The headwind is the tune in B minor on oboe over a tremolo storm, a
# howl of wind and a timpani stroke on every gust; a horn calls when the new leader takes the point and the strings
# swell as the V reforms. Practising, a xylophone runs down the line. The straggler is a flute scrambling over
# pizzicato, every honk of its answered; the overshoot is a slide whistle and a cymbal, the drop back a bassoon
# shrugging down. Timpani and a cymbal swell carry the wheel into E major, and the whole orchestra sings the tune
# crossing back, the xylophone and glockenspiel flashing down the line with the birds; a snare drives the sprint out,
# the flare is a crash on a big E major chord, and harp and glockenspiel pop the stars out. Every honk is synthesised
# (a nasal formant voice) where the bird is, and the wings beat on the beat round the flock.

CH = {'D': (50, 54, 57), 'Bm': (47, 50, 54), 'A': (45, 49, 52), 'G': (43, 47, 50), 'Em': (40, 43, 47),
      'F#m': (42, 45, 49), 'F#': (42, 46, 49), 'E': (40, 44, 47), 'B7': (47, 51, 54, 57), 'C#m': (49, 52, 56),
      'B': (47, 51, 54), 'Asus': (45, 50, 52), 'A7': (45, 49, 52, 55)}
# (bar, beat, note, beats)
THEME = [(0, 0, 'F#4', 2), (0, 2, 'A4', 1), (1, 0, 'D5', 3), (2, 0, 'C#5', 2), (2, 2, 'B4', 1), (3, 0, 'A4', 3),
         (4, 0, 'G4', 2), (4, 2, 'B4', 1), (5, 0, 'A4', 2), (5, 2, 'F#4', 1), (6, 0, 'E4', 2), (6, 2, 'F#4', 1),
         (7, 0, 'D4', 3)]
THEME_CH = ['D', 'Bm', 'A', 'D', 'G', 'D', 'A', 'D']
TIRED = [(0, 0, 'B4', 2), (0, 2, 'A4', 1), (1, 0, 'F#4', 3), (2, 0, 'G4', 2), (2, 2, 'E4', 1), (3, 0, 'F#4', 3)]
TIRED_CH = ['Bm', 'F#m', 'Em', 'F#']
CALL = [(0, 0, 'A3', 1), (0, 1, 'D4', 1), (0, 2, 'F#4', 1), (1, 0, 'A4', 2.5)]
CODA_B = [(0, 0, 'C#5', 2), (0, 2, 'B4', 1), (1, 0, 'G#4', 2), (1, 2, 'A4', 1), (2, 0, 'B4', 2), (2, 2, 'C#5', 1),
          (3, 0, 'E5', 3)]
CODA_B_CH = ['A', 'E', 'B7', 'E']


def score(M, G):
    from pixelhome.audio import SR, note as n, slide
    vln = M.sampler('Strings/Violin Section/susVib/*.wav', tune=-12)
    vla = M.sampler('Strings/Viola Section/susvib/*.wav', tune=-12)
    cel = M.sampler('Strings/Cello Section/susvib/*.wav', tune=-12)
    cbs = M.sampler('Strings/Solo Contrabass/SusVib/*.wav', tune=-12)
    cbp = M.sampler('Strings/Solo Contrabass/Pizz/*.wav', tune=-12)
    vpz = M.sampler('Strings/Violin Section/Pizz/*.wav', tune=-12)
    trem = M.sampler('Strings/Violin Section/Trem/*.wav', tune=-12)
    harp = M.sampler('Strings/Harp/*.wav')
    horn = M.sampler('Brass/F Horn/sus/*.wav', tune=-12)
    tpt = M.sampler('Brass/Trumpet/sus/*.wav', tune=-12)
    oboe = M.sampler('Woodwinds/Oboe/Vib/*.wav', tune=-12)
    flute = M.sampler('Woodwinds/Flute/susvib/*.wav', tune=-12)
    fst = M.sampler('Woodwinds/Flute/stac/*.wav', tune=-12)
    bsn = M.sampler('Woodwinds/Bassoon/stac/*.wav', tune=-12)
    glock = M.sampler('Percussion/Glock/*.wav', tune=-12)
    xylo = M.sampler('Percussion/Xylo/*.wav', tune=-12)
    timp = M.hits('Percussion/Timpani/Timpani1_Hit*.wav')
    troll = M.hits('Percussion/Timpani/Rolls/*.wav')
    swell = M.hits('Percussion/susCymb1-cresc-Median*.wav')
    crash = M.hits('Percussion/cymbal-crash1_mf*.wav')
    tri = M.hits('Percussion/Triangle3-Hit_v1*.wav')
    snare = M.hits('Percussion/Snare2-HitSN*.wav')
    sroll = M.hits('Percussion/Snare2-rollSN*.wav')
    bd = M.hits('Percussion/BDrumNewhit_v[4-7]*.wav')

    for name, gain, rev in (('melody', 0.4, 0.3), ('strings', 0.26, 0.32), ('bass', 0.3, 0.12), ('harp', 0.3, 0.3),
                            ('brass', 0.28, 0.28), ('winds', 0.34, 0.28), ('pizz', 0.3, 0.18), ('mallet', 0.32, 0.3),
                            ('drums', 0.5, 0.22), ('honk', 0.5, 0.2), ('wings', 0.12, 0.12), ('air', 0.1, 0.2),
                            ('fx', 0.35, 0.2)):
        M.bus(name, gain=0.62 * gain, reverb=rev)
    M.fader('air', [(0, -2), (T_WIND - 0.5, -6), (T_WIND + 0.3, 6), (T_CALM - 1, 6), (T_CALM + 1, -8), (T_TURN + 2, -8),
                    (T_TURN + 4, 0), (66, 0), (70, -6), (D, -4)])
    M.fader('wings', [(0, -6), (T_IN, 0), (66, 0), (70, -20)])

    order = np.argsort(G.pd)
    xs, ds = G.pos[order, 0], G.pd[order]
    x0, x1 = xs.min(), xs.max()

    def pan_at(d):
        x = np.interp(d, ds, xs)
        return float(0.85 * (2 * (x - x0) / (x1 - x0) - 1))

    def away(d):
        return float(np.clip(1 - (d - 2512) / 400, 0.25, 1)) if d > 2512 else 1.0

    def tones(c, lo, hi):
        return [m + 12 * o for o in range(-3, 4) for m in CH[c] if lo <= m + 12 * o <= hi]

    def root(c):
        return CH[c][0] % 12

    def tune(t0, phrase, inst, bus, vel, up=0, gain=1.0, pan=0.0, legato=1.0):
        for b, e, m, ln in phrase:
            M.add(bus, inst.play(n(m) + up, vel, dur=ln * BEAT * legato, release=0.3), t0 + b * BAR + e * BEAT,
                  gain, pan)

    def waltz(t0, chords, vel, up=0, harp_on=True, drums=False, pan=0.0):
        """Oom-pah-pah: the bass on one, pizzicato and violas on two and three, the harp rolling in eighths."""
        for i, c in enumerate(chords):
            t = t0 + i * BAR
            r = 36 + (root(c) + up) % 12
            M.add('bass', cbp.play(r, vel + 5), t, 1.0, pan)
            M.add('bass', cbs.play(r, vel - 15, dur=BEAT, release=0.2), t, 0.6, pan)
            for e in (1, 2):
                for m in tones(c, 55 - up, 67 - up)[:3]:
                    M.add('pizz', vpz.play(m + up, vel - 5), t + e * BEAT, 0.55, 0.25)
                    M.add('strings', vla.play(m + up - 12, vel - 25, dur=BEAT * 0.6, release=0.1), t + e * BEAT, 0.4)
            if harp_on:
                ar = tones(c, 50 - up, 72 - up)[:4]
                seq = ar + ar[-2:0:-1]
                for k in range(6):
                    M.add('harp', harp.play(seq[k % len(seq)] + up, vel - 15), t + k * BEAT / 2, 0.7,
                          pan + 0.3 * np.sin(k))
            if drums:
                M.add('drums', bd.play(vel + 10), t, 0.6)
                for e in (1, 2):
                    M.add('drums', snare.play(vel - 20), t + e * BEAT, 0.4)
                M.add('mallet', tri.play(70), t, 0.25, 0.4)

    # ---- the honk: a nasal voice that rises and drops, two formants and a buzz ----
    vrng = np.random.default_rng(SEED + 9)

    def honk(f0, dur):
        nn = int((dur + 0.06) * SR)
        tt = np.arange(nn) / SR
        uu = np.clip(tt / dur, 0, 1)
        f = f0 * (0.86 + 0.2 * np.sin(np.pi * np.clip(uu * 1.6, 0, 1)) - 0.12 * np.clip(uu - 0.55, 0, 1) / 0.45)
        f *= 1 + 0.01 * np.sin(2 * np.pi * 31 * tt)
        ph = 2 * np.pi * np.cumsum(f) / SR
        sig = np.zeros(nn)
        for k in range(1, 22):
            fk = k * f0
            if fk > 9000:
                break
            a = (np.exp(-((np.log(fk / 850)) / 0.35) ** 2) + 0.7 * np.exp(-((np.log(fk / 1550)) / 0.25) ** 2)
                 + 0.25 * np.exp(-((np.log(fk / 2900)) / 0.2) ** 2) + 0.15 / k)
            sig += a * np.sin(k * ph)
        sig += 0.25 * np.abs(sig).max() * vrng.normal(0, 1, nn) * np.exp(-tt / 0.03)
        env = np.clip(tt / 0.012, 0, 1) * np.clip((dur + 0.05 - tt) / 0.06, 0, 1) ** 1.5
        sig = sig * env
        sig = 0.5 * sig / (np.abs(sig).max() + 1e-9)
        return np.vstack([sig, sig])

    def thump(seed):                        # a wing's downstroke: a puff of low air
        r = np.random.default_rng(seed)
        nn = int(0.16 * SR)
        x = np.fft.rfft(r.normal(0, 1, nn))
        fr = np.fft.rfftfreq(nn, 1 / SR)
        x *= np.exp(-(fr / 420) ** 2) * (fr > 60)
        y = np.fft.irfft(x, nn)
        tt = np.arange(nn) / SR
        y *= np.clip(tt / 0.02, 0, 1) * np.exp(-tt / 0.05)
        y = 0.5 * y / (np.abs(y).max() + 1e-9)
        return np.vstack([y, y])

    jf, jp = birds()
    thumps = [thump(k) for k in range(6)]
    honks = {}
    for k in range(N_V + 1):
        f0 = 330 + 22 * (k % 5) + (60 if k == N_V else 0)          # the straggler is a youngster: higher
        honks[k] = [honk(f0 * s, d) for s, d in ((1.0, 0.2), (0.97, 0.26), (1.03, 0.17))]

    for i, (th, who, amp) in enumerate(calls()):
        if who < 0:
            M.add('honk', honks[i % N_V][i % 3], th, amp * 0.6, 0.95)
            continue
        gp = positions(th, jf, jp)[0][who]
        M.add('honk', honks[who][i % 3], th, amp * away(gp), pan_at(gp))
        if who == N_V or amp > 0.9:
            M.add('honk', honks[who][(i + 1) % 3], th + 0.22, amp * 0.6 * away(gp), pan_at(gp))

    # ---- wingbeats: the flock's downstrokes on the beat (double time in the wind), round the flock ----
    t = T_IN
    k = 0
    while t < 69.0:
        gp = positions(t, jf, jp)[0][:N_V]
        vis = gp[(gp > -100) & (gp < 2700)]
        if len(vis):
            M.add('wings', thumps[k % 6], t, 0.9 * away(float(vis.mean())), pan_at(float(vis.mean())))
            M.add('wings', thumps[(k + 3) % 6], t + 0.06, 0.6 * away(float(vis.mean())), pan_at(float(vis.min())))
        windy = T_WIND <= t < T_CALM
        t += BEAT / 2 if windy else BEAT
        k += 1
    # the air: a soft wind, a howl in the headwind, rushing behind them on the way back
    nn = int(D * SR)
    x = np.fft.rfft(vrng.normal(0, 1, nn))
    fr = np.fft.rfftfreq(nn, 1 / SR)
    x *= np.exp(-(fr / 900) ** 2) * (fr > 80)
    wind = np.fft.irfft(x, nn)
    wind /= np.abs(wind).max() + 1e-9
    tt = np.arange(nn) / SR
    wind *= 0.5 * (1 + 0.5 * np.sin(2 * np.pi * tt / 3.1))
    gusts = np.zeros(nn)
    for b in range(8):                                    # a gust on every bar of the headwind
        tg = T_WIND + b * BAR
        gusts += np.exp(-np.clip(tt - tg, 0, None) / 0.5) * (tt >= tg) * np.clip((tt - tg) / 0.08 + 1, 0, 1)
    wind *= 1 + 1.4 * gusts
    M.add('air', np.vstack([wind, np.roll(wind, 2400)]), 0.0)

    gR = pan_at(2400)
    # ---- 0-6: sunset; the flock heard before it's seen ----
    waltz(0.0, ['D', 'D', 'G', 'A'], 66, harp_on=False)
    for k, m in enumerate(('D3', 'A3', 'D4', 'F#4', 'A4', 'D5', 'A4', 'F#4', 'D4', 'A3', 'F#4', 'A4')):
        M.add('harp', harp.play(n(m), 66), 0.25 + k * BEAT / 2, 0.8, gR * k / 11)
    tune(bt(2), [(0, 0, 'A3', 3), (1, 0, 'C#4', 3)], horn, 'brass', 70, pan=gR)

    # ---- 6-18: the V comes in; violins ----
    t0 = T_IN
    M.add('mallet', glock.play(n('A5'), 70), t0, 0.5, gR)
    waltz(t0, THEME_CH, 82)
    tune(t0, THEME, vln, 'melody', 92)
    tune(t0 + 4 * BAR, [(b - 4, e, m, ln) for b, e, m, ln in THEME[6:]], flute, 'winds', 76, up=12, gain=0.5)

    # ---- 18-30: the headwind: the tune in B minor on oboe over a tremolo storm, timpani on every gust ----
    t0 = T_WIND
    M.add('drums', crash.play(100), t0, 0.6, pan_at(1500))
    for rep in range(2):
        waltz(t0 + rep * 4 * BAR, TIRED_CH, 84, harp_on=False)
        tune(t0 + rep * 4 * BAR, TIRED, oboe if rep == 0 else vln, 'winds' if rep == 0 else 'melody', 96)
    for b in range(8):
        M.add('drums', timp.play(95 + 3 * b), t0 + b * BAR, 0.6, pan_at(500 + 300 * b))
        c = (TIRED_CH * 2)[b]
        for m in tones(c, 55, 66)[:2]:
            M.add('strings', trem.play(m, 70 + 3 * b, dur=BAR, release=0.1), t0 + b * BAR, 0.6)
    # the leader tires: a sagging bassoon; the new leader: a horn call
    tune(T_TIRE[0], [(0, 0, 'F#3', 1), (0, 1, 'E3', 1), (0, 2, 'D3', 1), (1, 0, 'C#3', 3)], bsn, 'winds', 90,
         pan=pan_at(at(T_TIRE[0])))
    tune(T_POINT, CALL, horn, 'brass', 104, pan=pan_at(at(T_POINT)))
    tune(T_POINT, CALL, tpt, 'brass', 86, pan=pan_at(at(T_POINT)), gain=0.6)
    M.add('drums', troll.play(70, dur=2 * BAR - 0.1), T_POINT + 0.1, 0.5)

    # ---- 30-33: the V reforms: everyone swells together ----
    t0 = T_REFORM
    M.add('drums', crash.play(110), t0, 0.7, pan_at(at(t0)))
    M.add('drums', timp.play(115), t0, 0.8)
    for m in tones('D', 38, 74):
        inst = cel if m < 55 else (vla if m < 62 else vln)
        M.add('strings', inst.play(m, 96, dur=2 * BAR, release=0.6), t0, 0.8)
    tune(t0, [(0, 0, 'D5', 2), (0, 2, 'A4', 1), (1, 0, 'F#5', 3)], vln, 'melody', 100)
    waltz(t0, ['D', 'D'], 88)

    # ---- 33-36: practising: a xylophone down the line every bar ----
    t0 = bt(22)
    waltz(t0, ['G', 'A'], 86)
    for b in range(2):
        for k in range(N_V):
            tl = sorted(tones('G' if b == 0 else 'A', 62, 86))[::-1]
            m = tl[k % len(tl)]
            M.add('mallet', xylo.play(m, 90), t0 + b * BAR + 0.12 * k, 0.6,
                  pan_at(positions(t0 + b * BAR, jf, jp)[0][(k + 1) % N_V]))

    # ---- 36-45: the straggler: a flute scrambling over pizzicato; overshoot; drop back ----
    t0 = T_STRAG
    chs = ['D', 'A', 'Bm', 'G', 'D', 'A']
    waltz(t0, chs, 90, harp_on=False, drums=True)
    run = ['A4', 'B4', 'C#5', 'D5', 'E5', 'D5', 'C#5', 'B4', 'A4', 'F#4', 'G4', 'A4']
    t = t0 + 0.25
    k = 0
    while t < T_OVER - 0.1:
        gp = straggler(t)
        M.add('winds', fst.play(n(run[k % len(run)]), 84 + min(k, 30) // 2), t, 0.9, pan_at(gp))
        t += BEAT / 2
        k += 1
    po = pan_at(straggler(T_OVER))
    M.add('fx', slide(0.0, 0.45, 500, 1500, 0.55, amp=0.3), T_OVER - 0.4, 0.8, po)
    M.add('drums', crash.play(105), T_OVER, 0.6, po)
    M.add('drums', bd.play(120), T_OVER, 0.8, po)
    tune(T_BACK, [(0, 0, 'A3', 1), (0, 1, 'G#3', 1), (0, 2, 'G3', 1), (1, 0, 'F#3', 3)], bsn, 'winds', 96,
         pan=pan_at(straggler(T_BACK + 1)))
    M.add('fx', slide(0.0, 1.2, 1100, 500, 1.4, amp=0.2), T_BACK + 0.2, 0.6, pan_at(straggler(T_BACK + 1)))
    # it's in: a hit for everyone
    M.add('drums', timp.play(118), T_JOIN, 0.8)
    M.add('drums', crash.play(100), T_JOIN, 0.5)
    for m in tones('A7', 45, 76):
        M.add('strings', (cel if m < 55 else vln).play(m, 92, dur=BAR, release=0.3), T_JOIN, 0.7)
    tune(T_JOIN, [(0, 0, 'E5', 1), (0, 1, 'C#5', 1), (0, 2, 'A4', 1), (1, 0, 'G4', 3)], vln, 'melody', 96)
    waltz(T_JOIN, ['A', 'A7'], 92, drums=True)

    # ---- 48-52.5: the V wheels round: G, B7, timpani, a cymbal swell ----
    t0 = T_TURN
    turn_p = pan_at(at(T_TURN))
    sw = swell.play(110)
    M.add('drums', sw, t0 - sw.shape[1] / SR + 0.05, 0.6, turn_p)
    M.add('drums', crash.play(118), t0, 0.7, turn_p)
    waltz(t0, ['G', 'B7', 'B7'], 94, pan=turn_p * 0.5)
    M.add('drums', troll.play(95, dur=2 * BAR - 0.05), t0 + BAR, 0.7, turn_p)
    for k, m in enumerate(('B3', 'D#4', 'F#4', 'A4', 'B4', 'D#5', 'F#5', 'A5')):
        M.add('harp', harp.play(n(m), 86), t0 + BAR + k * 0.12, 0.8, turn_p)
    tune(t0, [(0, 0, 'G4', 1), (0, 1, 'B4', 1), (0, 2, 'D5', 1), (1, 0, 'D#5', 2), (1, 2, 'F#4', 1),
              (2, 0, 'B4', 3)], vln, 'melody', 104)
    tune(t0, [(0, 0, 'D4', 3), (1, 0, 'B3', 6)], horn, 'brass', 96)

    # ---- 52.5-64.5: back across, everyone, in E; flashes down the line as they spread ----
    t0 = bt(35)
    M.add('drums', crash.play(118), t0, 0.7)
    M.add('drums', timp.play(118, pitch=2), t0, 0.8)
    waltz(t0, THEME_CH, 98, up=2, drums=True)
    tune(t0, THEME, vln, 'melody', 108, up=2)
    tune(t0, THEME, horn, 'brass', 96, up=2 - 12, gain=0.9)
    tune(t0, THEME, tpt, 'brass', 90, up=2, gain=0.5)
    for i, tr in enumerate(ripple_times()):
        if tr > bt(43):
            break
        gp = positions(tr, jf, jp)[0]
        for k in (0, 4, 9):
            M.add('mallet', (glock if k == 0 else xylo).play(n('E5') + (0, 4, 7, 12)[(i + k) % 4], 80), tr + 0.06 * k,
                  0.4, pan_at(gp[k]))
    # ---- 64.5-70.5: the sprint out: the coda over a snare roll ----
    t0 = bt(43)
    waltz(t0, CODA_B_CH, 100, drums=True)
    tune(t0, CODA_B, vln, 'melody', 108)
    tune(t0, CODA_B, flute, 'winds', 90, gain=0.6)
    M.add('drums', sroll.play(90, dur=4 * BAR - 0.1), t0, 0.5, gR)
    M.add('drums', troll.play(90, dur=BAR), t0 + 3 * BAR, 0.6)

    # ---- 70.5-76.5: the flare: a crash on a big E major chord, a harp sweeping round and back ----
    t0 = T_GONE
    M.add('drums', crash.play(124), t0, 0.8, 0.8)
    M.add('drums', timp.play(124), t0, 0.9)
    M.add('drums', bd.play(124), t0, 0.8)
    for m, inst, v in ((n('E2'), cbs, 100), (n('B2'), cel, 96), (n('E3'), cel, 96), (n('G#3'), vla, 92),
                       (n('B3'), horn, 96), (n('E4'), vln, 98), (n('G#4'), vln, 94), (n('B4'), tpt, 90)):
        M.add('strings' if inst not in (horn, tpt) else 'brass', inst.play(m, v, dur=4 * BAR - 0.4, release=1.2), t0,
              0.75)
    for k, m in enumerate(('E5', 'B4', 'G#4', 'E4', 'B3', 'G#3', 'E3', 'B2')):
        M.add('harp', harp.play(n(m), 90), t0 + k * 0.36, 0.8, pan_at(2560 - 1000 * k * 0.36))
    for k, m in enumerate(('B2', 'E3', 'G#3', 'B3', 'E4', 'G#4', 'B4', 'E5')):
        M.add('harp', harp.play(n(m), 90), t0 + 2 * BAR + k * 0.36, 0.8, pan_at(-100 + 1000 * k * 0.36))
    M.add('drums', crash.play(100), t0 + 2 * BAR, 0.5, -0.8)
    tune(t0, [(0, 0, 'E5', 3), (1, 0, 'D#5', 2), (1, 2, 'C#5', 1), (2, 0, 'B4', 3), (3, 0, 'G#4', 3)], vln, 'melody',
         100)

    # ---- 76.5-90: dusk; a star to every beat ----
    t0 = T_DUSK
    for m, inst, v in ((n('E2'), cbs, 64), (n('B2'), cel, 60), (n('E3'), cel, 58), (n('G#3'), vla, 54),
                       (n('B3'), vla, 52)):
        M.add('strings' if inst is not cbs else 'bass', inst.play(m, v, dur=D - t0 - 1.5, release=1.5), t0, 0.8)
    waltz(t0, ['E', 'C#m', 'A', 'B', 'E', 'A', 'E'], 62, harp_on=False)
    tune(t0 + 2 * BAR, [(0, 0, 'B4', 2), (0, 2, 'G#4', 1), (1, 0, 'E4', 3), (2, 0, 'F#4', 2), (2, 2, 'A4', 1),
                        (3, 0, 'G#4', 3)], flute, 'winds', 76, pan=0.3)
    pent = [n(x) for x in ('E5', 'G#5', 'B5', 'C#6', 'E6', 'F#5')]
    for i, (ts, ps, _) in enumerate(stars()):
        M.add('mallet', glock.play(pent[i % 6] - 12, 70), ts, 0.6, pan_at(ps))
        M.add('harp', harp.play(pent[(i + 2) % 6] - 12, 60), ts + 0.03, 0.5, pan_at(ps))
    M.add('fx', slide(0.0, 1.0, 1800, 900, 1.3, amp=0.12), T_SHOOT, 0.5, 0.0)
    for k, m in enumerate(('E2', 'B2', 'E3', 'G#3', 'B3', 'E4')):
        M.add('harp', harp.play(n(m), 66), D - 4.0 + 0.1 * k, 0.7)
