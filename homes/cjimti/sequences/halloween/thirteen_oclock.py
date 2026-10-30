"""Thirteen O'Clock: the house is the inside of an old clock tower at midnight. A key at the free end of
Right winds the mainspring, a pendulum swings across Porch Front, and every tick of its escapement steps
the whole train forward: power runs from the key across the house to the bell rope on Side and the bell
at its free end. Each of the five corners is a gear (its own tooth count, size and speed, a rotating comb
of teeth that wraps round the corner from one run onto the next) and each run between them is a belt,
shaft, chain or rope with its own pattern and its own ratio, so the motion steps up or down at every
corner. The mechanism comes alive gear by gear, the hour and minute hands climb the two porch rails
toward twelve at the top, the ticking speeds up and the gears race. Midnight: a chime, then twelve
strikes, each a bell that rings out across the house in 3-D from its own hour on the roofline (going
clockwise as seen from the street: 1 at the back-right porch corner, 6 at the key, 7 at the front-left
corner, 12 in the middle of the porch), leaving a lit numeral behind until the house is a clock face.
Then a thirteenth. Everything stops dead, the pendulum stuck at the end of its swing. The mainspring goes
boing out of the key end, a cuckoo pops out of the porch and squawks, the gears pop off their corners
and roll down the runs (one off the end of the house, one spinning down like a coin), then everything
zips back, the numerals recount to twelve, and the clock gives one small sheepish ding and ticks on."""
import numpy as np
from pixelhome.fx import DT, hexc, light, smoothstep, keys, nframes

CODE = 'HW18'
TITLE = "Thirteen O'Clock"
KIND = 'show'
DESCRIPTION = ('The house is a clock tower at midnight: the corners are gears, the runs are belts and chains, '
               'and the pendulum ticks on the porch. It strikes twelve... and then thirteen, and the whole clock '
               'falls apart.')
VOICEOVER = ("Up in the old clock tower, it's almost midnight. Count the bells with me... "
             "all twelve of them. Just twelve. Right?")

MOON = hexc('#28357a')
DUST = hexc('#9fb4ff')
BRASS = hexc('#ffa938')
COPPER = hexc('#ff6e2a')
STEEL = hexc('#a8c4ff')
SILVER = hexc('#d6e2ff')
HEMP = hexc('#e8a050')
BRONZE = hexc('#ff8c30')
GOLD = hexc('#ffc860')
IVORY = hexc('#fff0d0')
FLASH = hexc('#fff6e0')
RING = hexc('#ffb848')
CHIME = hexc('#8fb8ff')
SOUR = hexc('#b4ff8a')
CUCKOO = hexc('#ffd21c')
BEAK = hexc('#ff5a10')
AXLE = hexc('#ff3010')

# ---- the story's clock (shared by render() and score()) ----------------------------------------------
T_WIND = [0.6 + 0.8 * k for k in range(6)]          # six half-turns of the key, three ratchet clicks each
T_NUDGE = 5.8                                       # the pendulum is nudged
T_TICK0 = 6.5
ENGAGE = {'Right': 6.5, 'C5': 7.5, 'Porch Right': 8.5, 'C4': 9.5, 'Porch Front': 10.5, 'C3': 11.5,
          'Porch Left': 12.5, 'C2': 13.5, 'Left': 14.5, 'C1': 15.5, 'Side': 16.5, 'bell': 17.5}
T_HANDS = 18.5
T_RUSH = 22.5
CORNER_PI = {'C1': 80, 'C2': 178, 'C3': 260, 'C4': 331, 'C5': 380}
# hour -> fractional path index of its numeral (clockwise from the street, 12 at the top: the porch)
HOUR_PI = [331.5, 356.0, 380.5, 421.0, 461.0, 500.0, 80.5, 130.0, 178.5, 220.0, 260.5, 296.0]
CHIME_NOTES = ['A4', 'F4', 'G4', 'D4', 'D4', 'G4', 'A4', 'F4']    # an original two-phrase quarter chime
CHIME_AT = ['C4', 'C2', 'C3', 'C1', 'C1', 'C3', 'C4', 'C2']        # the gear that rings each note


def _timeline():
    run, t = [], T_TICK0
    while t < 45.0:
        run.append(t)
        t += 1.0 if t < T_RUSH else float(keys(t, [(T_RUSH, 1.0), (31, 0.72), (38, 0.46), (42.5, 0.3), (45, 0.23)]))
    t_mid = run[-1]
    post = [t_mid + 0.9 + 0.6 * j for j in range(36)]
    chime = post[:8]
    strikes = post[10:33:2]
    t13 = post[35]
    boing = t13 + 1.7
    cuck = boing + 1.4
    cuck2 = cuck + 1.15
    pop = cuck2 + 1.8
    reset = pop + 4.4
    pend2 = reset + 3.7
    again = [pend2 + 0.6 * j for j in range(1, 6)]
    end = reset + 7.2
    w = [float(keys(tk, [(T_RUSH, 1.0), (45.0, 2.4)])) for tk in run] + [0.8] * len(post) + [0.6] * len(again)
    return dict(run=run, post=post, ticks=run + post + again, w=w, again=again, t_mid=t_mid, chime=chime,
                strikes=strikes, t13=t13, boing=boing, cuck=cuck, cuck2=cuck2, pop=pop, reset=reset,
                pend2=pend2, D=end)


TL = _timeline()
D = round(TL['D'], 2)
GEAR_ORDER = ['C3', 'C4', 'C2', 'C5', 'C1']            # the order they pop off
# gear: tooth count, offset of its axle inside the corner, radius on the roof, colour
GEARS = {'C1': (12, 34, 105, GOLD), 'C2': (8, 40, 120, BRONZE), 'C3': (16, 30, 100, COPPER),
         'C4': (14, 30, 95, STEEL), 'C5': (10, 36, 110, BRASS)}
# run: flow speed (roof units per tick), pattern period, colour; everything flows from the key to the bell
RUNS = {'Right': (8.0, 44.0, BRASS), 'Porch Right': (18.0, 20.0, STEEL), 'Porch Front': (26.0, 26.0, COPPER),
        'Porch Left': (12.0, 24.0, COPPER), 'Left': (22.0, 52.0, SILVER), 'Side': (6.0, 16.0, HEMP)}
NEXT = {'C1': ('Left', 'Side'), 'C2': ('Porch Left', 'Left'), 'C3': ('Porch Front', 'Porch Left'),
        'C4': ('Porch Right', 'Porch Front'), 'C5': ('Right', 'Porch Right')}


def _step(u):
    """One escapement step: a snap forward with a little recoil."""
    u = np.asarray(u, float)
    a = np.clip(u / 0.07, 0, 1)
    rec = np.clip((u - 0.07) / 0.14, 0, 1)
    return (1 - (1 - a) ** 3) - 0.07 * np.sin(np.pi * rec)


def _phi(ts):
    """The train's position (in ticks) at times ts."""
    ts = np.asarray(ts, float)
    out = np.zeros_like(ts)
    for tk, w in zip(TL['ticks'], TL['w']):
        out += w * _step(ts - tk)
    return out


def _pend_psi(ts):
    """Pendulum phase: an extreme on every tick, frozen from the thirteenth until it is restarted."""
    tk = TL['run'] + TL['post']
    kt = [T_NUDGE] + tk
    kp = [0.0] + [np.pi / 2 + i * np.pi for i in range(len(tk))]
    p13 = kp[-1]
    kt += [TL['pend2']] + TL['again']
    kp += [p13] + [p13 + (j + 1) * np.pi for j in range(len(TL['again']))]
    ts = np.asarray(ts, float)
    psi = np.interp(ts, kt, kp)
    late = ts > kt[-1]
    psi[late] = kp[-1] + (ts[late] - kt[-1]) / 0.6 * np.pi
    return psi


def _pend_amp(t):
    tl = TL
    if t < tl['t13'] + 0.01:
        return float(keys(t, [(T_NUDGE, 0), (T_TICK0 + 0.6, 95), (T_RUSH, 105), (tl['t_mid'], 150),
                              (tl['t_mid'] + 2, 125), (tl['t13'], 130)]))
    return float(keys(t, [(tl['pend2'], 130), (tl['pend2'] + 1.2, 60)]))


def _roll(name, tt, dist, dur):
    """Distance a popped gear has rolled `tt` seconds after it left its corner (with a bounce at the stop)."""
    if name == 'C5':                                     # off the end of the house, speeding up
        return dist * (tt / dur) ** 1.8
    if name == 'C1':
        return 0.0
    u = min(1.0, tt / dur)
    pos = dist * u ** 1.7
    if tt > dur:
        q = tt - dur
        pos -= 0.12 * dist * abs(np.sin(np.pi * q / 0.32)) * np.exp(-q / 0.35)
    return pos


def _gear_paths(ppd):
    """For each gear: (start distance, direction, distance, duration, pop time)."""
    tl = TL
    cs = {c: (ppd[a] + ppd[a + 1]) / 2 for c, a in CORNER_PI.items()}
    end = ppd[-1]
    spec = {'C3': (-1, cs['C3'] - (ppd[178] + 30), 2.2), 'C4': (1, (ppd[380] - 28) - cs['C4'], 1.5),
            'C2': (-1, cs['C2'] - (ppd[80] + 34), 2.4), 'C5': (1, end + 80 - cs['C5'], 1.9), 'C1': (1, 0.0, 2.6)}
    out = {}
    for i, c in enumerate(GEAR_ORDER):
        d, dist, dur = spec[c]
        out[c] = (cs[c], d, dist, dur, tl['pop'] + 0.3 * i)
    return out


def _returns():
    """When each gear zips home during the reset (the one that fell off the end comes back first)."""
    return {c: TL['reset'] + 0.3 * i for i, c in enumerate(['C5', 'C2', 'C4', 'C3', 'C1'])}


def render(G, seed=13):
    rng = np.random.default_rng(seed)
    tl = TL
    n = G.N
    F = nframes(D)
    out = np.zeros((F, n, 3))
    P = G.pos
    pd = G.pd
    ppd = pd[G.path]
    end_pd = ppd[-1]
    pxz = P[:, [0, 2]]
    path_xyz = P[G.path]

    def at_pi(x):
        i = int(np.clip(np.floor(x), 0, n - 2))
        f = x - i
        return path_xyz[i] * (1 - f) + path_xyz[i + 1] * f, ppd[i] * (1 - f) + ppd[i + 1] * f

    seg_mask = {name: np.isin(np.arange(n), G.seg[name]) for name in RUNS}
    tf = np.arange(F) * DT
    PHI = _phi(tf)
    PSI = _pend_psi(tf)

    def phi_at(t):
        return float(np.interp(t, tf, PHI))

    eng_phi = {k: phi_at(v) for k, v in ENGAGE.items()}

    # ---- corner gears: teeth on a wheel whose axle sits inside the corner, seen where it meets the roof
    gears = {}
    for c, a in CORNER_PI.items():
        nt, r0, R, col = GEARS[c]
        corner = (path_xyz[a] + path_xyz[a + 1])[[0, 2]] / 2
        lo = path_xyz[a - 6][[0, 2]] - corner
        hi = path_xyz[a + 7][[0, 2]] - corner
        lo, hi = lo / np.linalg.norm(lo), hi / np.linalg.norm(hi)
        bis = (lo + hi) / np.linalg.norm(lo + hi)
        O = corner + r0 * bis
        v = pxz - O
        ref = np.arctan2(*(corner - O)[::-1])
        ang = np.angle(np.exp(1j * (np.arctan2(v[:, 1], v[:, 0]) - ref)))
        if ang[G.path[a - 6]] < 0:                      # teeth travel from the higher run onto the lower
            ang = -ang
        s = (ppd[a] + ppd[a + 1]) / 2
        d = np.abs(pd - s)
        win = smoothstep(R * 1.15, R * 0.65, d)
        vin, vout = RUNS[NEXT[c][0]][0], RUNS[NEXT[c][1]][0]
        omega = 0.5 * (vin + vout) / (r0 * np.sqrt(2))
        gears[c] = dict(ang=ang, d=d, win=win, s=s, omega=omega, nt=nt, col=col)
    gpaths = _gear_paths(ppd)
    rets = _returns()

    # ---- pendulum on Porch Front
    pf = G.seg['Porch Front']
    pf_lo, pf_hi = pd[pf].min(), pd[pf].max()
    pf_mid = (pf_lo + pf_hi) / 2
    pfm = seg_mask['Porch Front']

    # ---- hands: minute up Porch Right (from the street end, C5, to the back, C4); hour up Porch Left
    pr_street, pr_top = ppd[380], ppd[332]
    pl_street, pl_top = ppd[179], ppd[260]
    prm, plm = seg_mask['Porch Right'], seg_mask['Porch Left']
    tocks = [tk for i, tk in enumerate(tl['run']) if tk > T_HANDS and i % 2 == 1]

    # ---- strikes
    hours = [at_pi(x) for x in HOUR_PI]
    chime_src = [at_pi(CORNER_PI[c] + 0.5) for c in CHIME_AT]

    # ---- dust motes drifting in the moonlight
    m_n = 34
    m_s = rng.uniform(0, end_pd, m_n)
    m_v = rng.uniform(-9, 9, m_n)
    m_f = rng.uniform(0.15, 0.5, m_n)
    m_p = rng.uniform(0, 2 * np.pi, m_n)

    # ---- cuckoo feathers (path distance, velocity, life)
    fe_n = 18
    fe_v = rng.uniform(120, 420, fe_n) * rng.choice([-1, 1], fe_n)
    fe_life = rng.uniform(0.7, 1.6, fe_n)
    t_sq = tl['cuck2'] + 0.3

    def tick_env(t, tau=0.09):
        ks = [tk for tk in tl['ticks'] if tk <= t]
        return float(np.exp(-(t - ks[-1]) / tau)) if ks else 0.0

    for f in range(F):
        t = f * DT
        buf = np.zeros((n, 3))
        phi = PHI[f]
        tick = tick_env(t)

        # moonlight through the tower window, and dust
        bedI = keys(t, [(0, 0.0), (1.2, 0.1), (tl['t13'], 0.1), (tl['t13'] + 0.3, 0.075), (D - 1.5, 0.08), (D, 0)])
        buf += light(MOON, bedI)
        ms = m_s + m_v * t
        tw = 0.5 + 0.5 * np.sin(2 * np.pi * m_f * t + m_p)
        dust = (tw[:, None] ** 3 * np.exp(-((pd[None] - ms[:, None]) / 7) ** 2)).sum(0)
        buf += light(DUST, 0.16 * np.clip(dust, 0, 1) * min(1, t / 2) * (t < D - 1))

        # overall level of the mechanism through the story
        mech = float(keys(t, [(0, 0.0), (0.8, 0.55), (T_TICK0, 0.6), (tl['t13'] + 0.3, 1.0),
                              (tl['boing'], 0.8), (tl['pop'], 0.7), (tl['reset'], 0.6),
                              (tl['reset'] + 2.2, 1.0), (D - 1.6, 0.9), (D, 0.0)]))
        rush = float(keys(t, [(T_RUSH, 1.0), (tl['t_mid'], 1.45), (tl['t_mid'] + 1.0, 0.85),
                              (tl['strikes'][0] - 0.3, 0.5), (tl['t13'], 0.55), (tl['t13'] + 0.4, 1.0)]))
        slack = float(smoothstep(tl['pop'], tl['pop'] + 1.2, t) * (1 - smoothstep(tl['reset'] + 1.4, tl['reset'] + 1.9, t)))
        retension = np.exp(-max(0.0, t - tl['reset'] - 1.7) / 0.25) * (t > tl['reset'] + 1.7)

        # ---- runs: belts, shaft, chain, rope; each steps with the train at its own ratio
        present = [c for c in gears if not (gpaths[c][4] <= t < rets[c] + 0.35)]
        gwin = np.clip(sum((gears[c]['win'] for c in present), np.zeros(n)), 0, 1)
        for name, (v, per, col) in RUNS.items():
            m = seg_mask[name]
            te = ENGAGE[name]
            on = t >= te
            X = v * max(0.0, phi - eng_phi[name]) if on else 0.0
            X -= 26 * slack                                      # the belts slip back when the gears go
            u = np.mod((pd[m] + X) / per, 1.0)
            k = np.floor((pd[m] + X) / per)
            if name == 'Right':                                  # drive belt with lugs
                I = 0.1 + 0.32 * smoothstep(0.0, 0.08, u) * smoothstep(0.42, 0.32, u)
            elif name == 'Porch Right':                          # spinning shaft: a screw thread
                I = 0.08 + 0.42 * (1 - u) ** 2.2
            elif name == 'Porch Front':                          # escape wheel teeth behind the pendulum
                I = 0.07 + 0.2 * np.clip(1 - np.abs(u - 0.5) * 2.6, 0, 1)
            elif name == 'Porch Left':                           # chain: plates with pins, alternating links
                plate = smoothstep(0.04, 0.14, u) * smoothstep(0.96, 0.86, u)
                pins = np.exp(-((u - 0.25) / 0.07) ** 2) + np.exp(-((u - 0.75) / 0.07) ** 2)
                I = 0.06 + plate * np.where(k % 2 == 0, 0.3, 0.17) + 0.12 * pins
            elif name == 'Left':                                 # flat belt with a bright splice
                I = 0.09 + 0.22 * smoothstep(0.0, 0.05, u) * smoothstep(0.62, 0.55, u) \
                    + 0.3 * np.exp(-((u - 0.04) / 0.025) ** 2)
            else:                                                # bell rope: two twisted strands
                I = 0.07 + 0.24 * (0.5 + 0.5 * np.cos(2 * np.pi * u)) ** 2 + 0.1 * (0.5 + 0.5 * np.cos(4 * np.pi * u + 1))
            lvl = (1.0 if on else 0.35) * mech * (rush if name != 'Porch Front' else min(rush, 1.0))
            lvl *= 1 - 0.45 * slack
            I = I * lvl * (1 + 0.35 * tick * on) + 0.3 * retension * I
            buf[m] += light(col, I * (1 - 0.85 * gwin[m]))
            if on and t - te < 0.9:                              # power arrives: a pulse runs the length
                q = (t - te) / 0.9
                lo_, hi_ = pd[m].min(), pd[m].max()
                head = hi_ - (hi_ - lo_) * q
                buf[m] += light(FLASH, 0.85 * (1 - q) * np.exp(-((pd[m] - head) / 26) ** 2))

        # ---- the gears
        for c, g in gears.items():
            te = ENGAGE[c]
            on = t >= te
            sel = g['win'] > 0
            theta = g['omega'] * max(0.0, phi - eng_phi[c]) if on else 0.0
            tooth = smoothstep(-0.15, 0.6, np.cos(g['nt'] * (g['ang'][sel] - theta)))
            gp = gpaths[c]
            gone = gp[4] <= t < rets[c] + 0.35
            hub = np.exp(-(g['d'][sel] / 9) ** 2)
            if gone:
                buf[sel] += light(AXLE, 0.22 * hub * g['win'][sel])
                continue
            lvl = (1.0 if on else 0.35) * mech * rush
            flare = 0.0
            if on and t - te < 0.6:                              # clunk: it engages
                flare = np.exp(-(t - te) / 0.18)
            if t < tl['t13'] + 0.01 and abs(t - tl['t_mid']) < 1.5 and c in ('C3', 'C4'):   # midnight: hands meet
                flare = max(flare, float(np.exp(-abs(t - tl['t_mid']) / 0.3)))
            I = (0.08 + 0.75 * tooth) * lvl * (1 + 0.3 * tick * on) + 0.9 * flare * (0.4 + 0.6 * tooth)
            I = I + (0.7 * lvl + 0.8 * flare) * hub
            if rets[c] <= t < rets[c] + 0.6:                      # snaps back on
                I = I + 0.9 * np.exp(-(t - rets[c] - 0.35) / 0.15) * (t > rets[c] + 0.35)
            buf[sel] += light(g['col'], I * g['win'][sel])

        # ---- the winding key at the free end of Right, and the mainspring
        dk = end_pd - pd
        key = dk < 46
        wind_turn = 0.0
        click = 0.0
        for tw_ in T_WIND:
            u = t - tw_
            wind_turn += float(smoothstep(0, 0.6, u))
            for c_ in (0.0, 0.2, 0.4):
                if u >= c_:
                    click = max(click, float(np.exp(-(u - c_) / 0.07)))
        if t >= ENGAGE['Right']:
            wind_turn -= 0.08 * max(0.0, phi - eng_phi['Right'])     # slowly unwinding while it runs
        keyI = (0.25 + 0.45 * (0.5 + 0.5 * np.cos(2 * np.pi * (dk[key] / 30 - 0.5 * wind_turn)))) * \
            float(keys(t, [(0.2, 0.0), (0.6, 1.0), (tl['boing'], 1.0), (tl['boing'] + 0.2, 0.3)]))
        buf[key] += light(BRASS, keyI * (1 + 0.8 * click))
        coils = min(6.0, wind_turn)
        Lm = 60 * coils if t < T_TICK0 else 360 - 150 * float(smoothstep(T_TICK0, tl['t_mid'], t))
        if t < tl['boing']:
            rm = seg_mask['Right']
            pitch = 40 - 4 * coils if t < T_TICK0 else 16 + 10 * float(smoothstep(T_TICK0, tl['t_mid'], t))
            fill = smoothstep(Lm + 8, Lm - 8, dk[rm])
            spring = 0.5 + 0.5 * np.cos(2 * np.pi * dk[rm] / pitch)
            sI = fill * (0.08 + 0.3 * spring ** 2) * (1.0 if t < T_TICK0 else 0.45) * mech / 0.6
            buf[rm] += light(BRASS, sI * min(1.0, t / 0.8))
            for tw_ in T_WIND:                                    # each click shoots a little wave in
                for c_ in (0.0, 0.2, 0.4):
                    q = t - tw_ - c_
                    if 0 <= q < 0.4:
                        buf[rm] += light(IVORY, 0.55 * np.exp(-q / 0.2) * np.exp(-((dk[rm] - 900 * q) / 18) ** 2))

        # ---- the pendulum
        A = _pend_amp(t)
        if A > 0.5 and t < D - 0.5:
            bob = pf_mid + A * np.sin(PSI[f])
            db = pd[pfm] - bob
            lit = float(keys(t, [(T_NUDGE, 0.3), (ENGAGE['Porch Front'], 0.75), (ENGAGE['Porch Front'] + 0.5, 1.0)]))
            lit *= float(keys(t, [(tl['t13'] + 0.3, 1.0), (tl['boing'], 0.6), (tl['reset'] + 2.0, 0.6),
                                  (tl['pend2'], 1.0), (D - 1.5, 1.0), (D, 0.0)]))
            rod_lo, rod_hi = min(pf_mid, bob), max(pf_mid, bob)
            rod = ((pd[pfm] >= rod_lo) & (pd[pfm] <= rod_hi)) * 0.12
            I = 0.95 * np.exp(-(db / 14) ** 2) + 0.35 * np.exp(-(db / 38) ** 2) + rod
            I += 0.3 * np.exp(-((pd[pfm] - pf_mid) / 6) ** 2)     # the pivot
            buf[pfm] += light(GOLD, I * lit)
            # the escapement catches at each end of the swing
            ks = [tk for tk in tl['ticks'] if tk <= t]
            if ks and t - ks[-1] < 0.25 and t < tl['t13'] + 0.4:
                side = np.sign(np.sin(float(np.interp(ks[-1], tf, PSI))))
                buf[pfm] += light(FLASH, 0.8 * np.exp(-(t - ks[-1]) / 0.07)
                                  * np.exp(-((pd[pfm] - (pf_mid + side * (A + 14))) / 7) ** 2))

        # ---- the hands climb the porch rails toward twelve
        if T_HANDS <= t < tl['pop'] + 0.5 or t > tl['reset'] + 3.2:
            if t < tl['t_mid']:
                mm = 0.04 + 0.96 * sum(float(_step(t - tk)) for tk in tocks) / len(tocks)
                hh = float(keys(t, [(T_HANDS, 0.6), (tl['t_mid'], 1.0)]))
            else:
                mm = hh = 1.0
            hl = float(keys(t, [(T_HANDS, 0), (T_HANDS + 1.0, 1.0), (tl['t13'] + 0.3, 1.0), (tl['boing'], 0.7),
                                (tl['pop'] + 0.5, 0.0)]))
            if t > tl['reset'] + 3.2:
                hl = float(keys(t, [(tl['reset'] + 3.2, 0.0), (tl['reset'] + 3.6, 0.8), (D - 1.5, 0.8), (D, 0)]))
            for msk, base, top, frac, wid in ((prm, pr_street, pr_top, mm, 12), (plm, pl_street, pl_top, hh, 16)):
                tip = base + (top - base) * frac
                dd = pd[msk]
                along = np.clip((dd - base) / (tip - base + 1e-9), 0, 1)
                inside = (along > 0) & (along < 1)
                I = inside * (0.06 + 0.16 * along) + 0.85 * np.exp(-((dd - tip) / wid) ** 2)
                buf[msk] += light(IVORY, I * hl)

        # ---- the chime: each note rings a small ring off a gear
        for k, (tc, (src, s_src)) in enumerate(zip(tl['chime'], chime_src)):
            tt = t - tc
            if 0 <= tt < 1.6:
                r3 = np.linalg.norm(P - src, axis=1)
                ring = np.exp(-((r3 - 480 * tt) / (18 + 40 * tt)) ** 2) * np.exp(-tt / 0.5)
                core = np.exp(-((pd - s_src) / 24) ** 2) * np.exp(-tt / 0.35)
                buf += light(CHIME, 0.6 * ring + 0.8 * core)

        # ---- the strikes: a bell rings out from each hour's place on the roof and leaves a numeral
        if tl['strikes'][0] <= t < tl['reset']:
            numI = float(keys(t, [(tl['t13'], 1.0), (tl['t13'] + 0.2, 1.4), (tl['t13'] + 0.6, 0.8), (tl['boing'], 0.7),
                                  (tl['pop'], 0.35), (tl['reset'], 0.0)]))
            for h, (ts, (src, s_src)) in enumerate(zip(tl['strikes'], hours)):
                tt = t - ts
                if tt < 0:
                    continue
                if tt < 2.2 and t < tl['t13'] + 0.35:
                    r3 = np.linalg.norm(P - src, axis=1)
                    hum = 0.75 + 0.25 * np.cos(2 * np.pi * 5.0 * tt)
                    ring = np.exp(-((r3 - 620 * tt) / (30 + 80 * tt)) ** 2) * np.exp(-tt / 0.8) * hum
                    ring2 = np.exp(-((r3 - 430 * tt) / (16 + 40 * tt)) ** 2) * np.exp(-tt / 0.45)
                    core = np.exp(-((pd - s_src) / 34) ** 2) * np.exp(-tt / 0.4)
                    swell = 0.22 * np.exp(-tt / 0.4)
                    big = 1.25 if h == 11 else 1.0
                    buf += light(RING, big * (1.15 * ring + 0.5 * ring2 + swell)) + light(FLASH, big * 1.05 * core)
                    # the bell rope on Side jerks up toward the bell, and the bell at its end glows
                    q = tt / 0.35
                    if q < 1:
                        buf += light(HEMP, 0.7 * (1 - q) * np.exp(-((pd - (ppd[80] - ppd[80] * q)) / 30) ** 2)
                                     * seg_mask['Side'])
                    buf += light(BRONZE, 0.9 * np.exp(-tt / 0.8) * np.exp(-(pd / 40) ** 2))
                pip = 0.85 * np.exp(-((pd - s_src) / 13) ** 2) * min(1.0, tt / 0.15)
                buf += light(GOLD, pip * numI)

        # bell at the free end of Side, alive once the rope engages
        if t >= ENGAGE['bell']:
            bl = float(keys(t, [(ENGAGE['bell'], 0), (ENGAGE['bell'] + 0.5, 1), (tl['t13'] + 0.3, 1),
                                (tl['boing'], 0.5), (D - 1.5, 0.5), (D, 0)]))
            fl = np.exp(-(t - ENGAGE['bell']) / 0.4)
            buf += light(BRONZE, bl * (0.28 + 0.06 * np.sin(2 * np.pi * 0.7 * t) + 0.7 * fl) * np.exp(-(pd / 30) ** 2))

        # ---- the thirteenth: every numeral and every gear at once, the wrong colour; then nothing moves
        tt = t - tl['t13']
        if 0 <= tt < 1.5:
            for src, s_src in hours:
                buf += light(SOUR, 1.1 * np.exp(-((pd - s_src) / 40) ** 2) * np.exp(-tt / 0.35))
            buf += light(SOUR, 0.55 * np.exp(-tt / 0.16))
            for c, g in gears.items():
                buf += light(SOUR, 0.6 * g['win'] * np.exp(-tt / 0.5))

        # ---- boing: the mainspring jumps out of the key end
        tt = t - tl['boing']
        if 0 <= tt and t < tl['reset'] + 1.0:
            E = (130 + 95 * np.exp(-tt / 0.55) * np.sin(2 * np.pi * 4.2 * tt)) * min(1.0, tt / 0.04)
            if t > tl['reset']:
                E *= 1 - smoothstep(tl['reset'], tl['reset'] + 0.6, t)
            E = max(E, 1.0)
            dk2 = end_pd - pd
            coil = 0.5 + 0.5 * np.cos(2 * np.pi * dk2 / (E / 6.5))
            inside = smoothstep(E + 6, E - 6, dk2) * seg_mask['Right']
            bI = inside * (0.12 + 0.7 * coil ** 2) * (0.5 + 0.5 * np.exp(-tt / 1.2))
            buf += light(BRASS, bI) + light(FLASH, 0.9 * np.exp(-tt / 0.12) * np.exp(-(dk2 / 30) ** 2))

        # ---- the cuckoo pops out of the middle of the porch, twice
        for tc, squawk in ((tl['cuck'], False), (tl['cuck2'], True)):
            tt = t - tc
            if 0 <= tt < 1.5:
                out_ = float(keys(tt, [(0, 0), (0.1, 1.25), (0.18, 1.0), (1.0 if not squawk else 1.15, 1.0),
                                       (1.25 if not squawk else 1.45, 0.0)]))
                dc = pd - pf_mid
                door = smoothstep(10 + 40 * out_, 6 + 34 * out_, np.abs(dc)) * pfm
                buf *= (1 - 0.8 * door)[:, None]
                call = np.exp(-tt / 0.1) + 0.8 * (tt > 0.3) * np.exp(-max(0.0, tt - 0.3) / 0.15)
                if squawk and tt > 0.3:
                    call = 1.2 * (0.5 + 0.5 * np.sign(np.sin(tt * 70))) * np.exp(-(tt - 0.3) / 0.4)
                bird = np.exp(-(dc / (6 + 20 * out_)) ** 2) * out_
                buf += light(CUCKOO, 0.95 * bird) + light(BEAK, 0.9 * call * np.exp(-(dc / 7) ** 2) * out_)
        tt = t - t_sq
        if 0 <= tt < 2.0:                                         # feathers everywhere
            age = tt
            live = age < fe_life
            if live.any():
                s = pf_mid + fe_v[live] * age * (1 - 0.4 * age / fe_life[live])
                b = (1 - age / fe_life[live]) ** 1.3
                acc = (b[:, None] * np.exp(-((pd[None] - s[:, None]) / 6) ** 2)).sum(0)
                buf += light(CUCKOO, 0.8 * np.clip(acc, 0, 1))

        # ---- the gears pop off and roll
        for c in GEAR_ORDER:
            s0, d, dist, dur, tp = gpaths[c]
            tt = t - tp
            tr = rets[c]
            if tt < 0 or t >= tr + 0.35:
                continue
            nt, col = GEARS[c][0], GEARS[c][3]
            rr = 22.0
            if t >= tr:                                           # zipping home
                q = (t - tr) / 0.35
                pos = _roll(c, 9.0, dist, dur) * (1 - q * q * (3 - 2 * q))
            else:
                pos = _roll(c, tt, dist, dur)
            sg = s0 + d * pos
            pop_fl = np.exp(-tt / 0.12)
            dg = pd - sg
            disc = smoothstep(rr + 4, rr - 4, np.abs(dg))
            if c == 'C1':                                         # spinning down like a coin
                wf = 2.5 + 22 * min(1.0, tt / 2.6) ** 2
                wob_ph = 2 * np.pi * (2.5 * tt + 22 * min(tt, 2.6) ** 3 / (3 * 2.6 ** 2))
                flat = smoothstep(2.6, 2.75, tt) if t < tr else 0.0
                side = 0.5 + 0.5 * np.cos(wob_ph) * np.sign(dg) * (1 - flat)
                I = disc * (0.3 + 0.6 * side) * (1 - 0.6 * flat)
                I = I * (1 + 0.15 * np.sin(2 * np.pi * wf * tt))
            else:
                teeth = 0.5 + 0.5 * np.cos(nt * (dg / rr + pos / rr))
                I = disc * (0.3 + 0.6 * teeth ** 2)
            buf += light(col, I * 1.1) + light(FLASH, 0.9 * pop_fl * np.exp(-(dg / 20) ** 2))

        # ---- the reset: the numerals recount to twelve, then one small ding at the top
        tr0 = tl['reset'] + 2.0
        if tr0 <= t < D:
            for h, (src, s_src) in enumerate(hours):
                th = tr0 + 0.1 * h
                if t >= th:
                    k = np.exp(-(t - th) / 0.25) * 0.7 + 0.25 * (h == 11)
                    k *= float(keys(t, [(tr0, 1), (D - 2.5, 1), (D - 1, 0)]))
                    buf += light(GOLD, k * np.exp(-((pd - s_src) / 10) ** 2))
            tt = t - (tl['reset'] + 3.4)
            if 0 <= tt < 1.5:
                src, s_src = hours[11]
                r3 = np.linalg.norm(P - src, axis=1)
                buf += light(RING, 0.35 * np.exp(-((r3 - 300 * tt) / 20) ** 2) * np.exp(-tt / 0.5)
                             + 0.6 * np.exp(-((pd - s_src) / 20) ** 2) * np.exp(-tt / 0.3))

        out[f] = buf
    return np.clip(out, 0, 1)


# ---- soundtrack ---------------------------------------------------------------------------------------
# D minor, and the beat is the escapement: every tick of the pendulum is a beat, so as the ticking speeds
# up, the music does too. The key is wound with a ratchet and a rising pizzicato; then the band assembles
# gear by gear, each part entering exactly as its piece of the mechanism engages, panned to where it is
# (bassoon oom-pah for the key's belt, pizzicato cellos for the first gear, marimba for the shaft, glock,
# violas, the clarinet tune on the chain, strings on the belt, timpani on the front corner, the creak of
# the bell rope). The rush to midnight builds with cello tremolo and a snare roll; the hands meet with a
# crash. An original quarter chime rings off the gears; then twelve big bells, each panned to its hour
# on the roof, while the strings climb a step with every strike to a D major twelfth. The thirteenth is a
# sour E-flat, and everything is choked dead. Then the comedy: a boing at the key end, a cuckoo that
# squawks, gears that pop, rattle down the runs (one off the end, one spinning down like a coin), zip
# home, a quick recount to twelve, one sheepish ding, and the ticking starts again.

BEATS_PER_BAR = 4
PROG = ['Dm', 'Dm', 'Dm', 'Dm', 'Bb', 'A', 'Dm', 'Gm', 'Bb', 'A', 'Dm', 'Bb', 'Gm', 'Bb', 'A7', 'A7']
VO = {'Dm': ('D2', ['D4', 'F4', 'A4']), 'Bb': ('Bb1', ['D4', 'F4', 'Bb4']), 'A': ('A1', ['C#4', 'E4', 'A4']),
      'A7': ('A1', ['C#4', 'G4', 'A4']), 'Gm': ('G1', ['D4', 'G4', 'Bb4'])}
MEL = [[(0, 'A4', 1), (1, 'D5', .5), (1.5, 'E5', .5), (2, 'F5', 1), (3, 'E5', 1)],
       [(0, 'D5', 1), (1, 'C5', .5), (1.5, 'A4', .5), (2, 'D5', 2)],
       [(0, 'F5', 1), (1, 'E5', .5), (1.5, 'D5', .5), (2, 'Bb4', 1), (3, 'D5', 1)],
       [(0, 'C#5', 1.5), (1.5, 'A4', .5), (2, 'E5', 2)],
       [(0, 'A4', 1), (1, 'D5', 1), (2, 'F5', 1), (3, 'A5', 1)],
       [(0, 'G5', 1.5), (1.5, 'F5', .5), (2, 'D5', 1), (3, 'Bb4', 1)],
       [(0, 'F5', 1), (1, 'D5', .5), (1.5, 'F5', .5), (2, 'Bb5', 1), (3, 'A5', 1)],
       [(0, 'E5', 1), (1, 'C#5', 1), (2, 'A4', 2)]]
MEL_BARS = {2: 0, 3: 1, 4: 2, 5: 3, 6: 4, 7: 5, 8: 6, 9: 7, 10: 4, 11: 6, 12: 5, 13: 6, 14: 7}
CLIMB = ['D4', 'E4', 'F4', 'G4', 'A4', 'Bb4', 'C#5', 'D5', 'E5', 'F5', 'G5', 'A5']


def score(M, G):
    from pixelhome.audio import SR, note, slide, whoosh
    n = note
    tl = TL
    rng = np.random.default_rng(1313)
    ppd = G.pd[G.path]
    end_pd = ppd[-1]
    T_CUT = tl['t13'] + 0.32                   # the moment everything is choked dead

    for name, gain, rev in (('tick', 0.32, 0.12), ('band', 0.3, 0.2), ('mel', 0.3, 0.25), ('str', 0.26, 0.35),
                            ('bell', 0.5, 0.3), ('perc', 0.38, 0.2), ('fx', 0.34, 0.18)):
        M.bus(name, gain=gain, reverb=rev)

    order = np.argsort(G.pd)
    xs, ds = G.pos[order, 0], G.pd[order]
    x0, x1 = xs.min(), xs.max()

    def pan_at(d):
        return float(0.85 * (2 * (np.interp(d, ds, xs) - x0) / (x1 - x0) - 1))

    def pan_pi(x):
        return pan_at(float(np.interp(x, np.arange(len(ppd)), ppd)))

    def put(bus, sig, t, gain=1.0, pan=None, choke=True):
        """Into a bus; anything still sounding at the thirteenth's choke is cut off with it."""
        if sig.ndim == 1:
            sig = np.vstack([sig, sig])
        if choke and t < T_CUT < t + sig.shape[1] / SR:
            k = int((T_CUT - t) * SR)
            sig = sig[:, :k + int(0.03 * SR)].copy()
            sig[:, k:] *= np.linspace(1, 0, sig.shape[1] - k)
        M.add(bus, sig, t, gain, pan)

    def tone(f, sec, harm=6, tilt=1.0):
        m = int(sec * SR)
        f = np.broadcast_to(np.asarray(f, float), (m,))
        ph = 2 * np.pi * np.cumsum(f) / SR
        return sum(np.sin(k * ph) / k ** tilt * (k * f < 16000) for k in range(1, harm + 1))

    def band(sec, lo, hi, seed):
        m = max(16, int(sec * SR))
        X = np.fft.rfft(np.random.default_rng(seed).normal(0, 1, m))
        fr = np.fft.rfftfreq(m, 1 / SR)
        X *= np.clip((fr - lo * 0.7) / (lo * 0.3 + 1e-9), 0, 1) * np.clip((hi * 1.3 - fr) / (hi * 0.3), 0, 1)
        y = np.fft.irfft(X, m)
        return y / (np.abs(y).max() + 1e-9)

    def bigbell(nm, sec=5.0, sour=False):
        """A tower bell: hum, prime, minor-third tierce, quint, nominal and the rest, each with its own decay."""
        m = int(sec * SR)
        tt = np.arange(m) / SR
        f0 = 440 * 2 ** ((n(nm) - 69) / 12)
        x = np.zeros(m)
        parts = ((0.5, 0.8, 4.0), (1.0, 1.0, 2.6), (1.19 if not sour else 1.27, 0.55, 1.8), (1.5, 0.35, 1.4),
                 (2.0, 0.6, 1.2), (2.52, 0.2, 0.7), (3.0, 0.15, 0.5), (4.16, 0.08, 0.3))
        for r, a, d in parts:
            x += a * np.sin(2 * np.pi * f0 * r * tt * (1 + 0.0015 * r) + r) * np.exp(-tt / d)
        x *= 1 + 0.12 * np.sin(2 * np.pi * 1.6 * tt)            # the slow beat of a big bell
        clang = band(0.06, 500, 6000, int(f0))
        x[:len(clang)] += 0.5 * clang * np.exp(-np.arange(len(clang)) / SR / 0.012)
        return x / (np.abs(x).max() + 1e-9)

    # ---- instruments
    bsn = M.sampler('Woodwinds/Bassoon/stac/*.wav', tune=-12)
    cpz = M.sampler('Strings/Cello Section/pizzT/*.wav', tune=-12)
    vpz = M.sampler('Strings/Viola Section/pizz/*.wav', tune=-12)
    mar = M.sampler('Percussion/Marimba/*.wav', tune=-12)
    glk = M.sampler('Percussion/Glock/*.wav', tune=-12)
    cla = M.sampler('Woodwinds/Clarinet/stac/*.wav', tune=-12)
    vln = M.sampler('Strings/Violin Section/susVib/*.wav', tune=-12)
    vla = M.sampler('Strings/Viola Section/susvib/*.wav', tune=-12)
    cel = M.sampler('Strings/Cello Section/susvib/*.wav', tune=-12)
    ctr = M.sampler('Strings/Cello Section/trem/*.wav', tune=-12)
    hrn = M.sampler('Brass/F Horn/sus/*.wav', tune=-12)
    tub = M.sampler('Percussion/TB_hit*.wav', tune=-12)
    xyl = M.sampler('Percussion/Xylo/*.wav', tune=-12)
    tick = M.hits('VSCO 1 Percussion/varWood/wood_click_f*.wav')
    tock = M.hits('Percussion/LogDrumLo_MedM_v2*.wav')
    ratchet = M.hits('Percussion/Ratchet1-Crank*.wav')
    metal = M.hits('Miscellania Raw/Misc 1/metal_hit1[0-1].wav')
    clank = M.hits('Miscellania Raw/Misc 1/metal_hit[2-6].wav')
    timp = M.hits('Percussion/Timpani/Timpani1_Hit_v3_*.wav')
    timp_lo = M.hits('Percussion/Timpani/Timpani1_Hit_v1_*.wav')
    troll = M.hits('Percussion/Timpani/Rolls/Timpani1_Roll_v5*.wav')
    sroll = M.hits('Percussion/Snare2-rollNS_v5*.wav')
    crash = M.hits('Percussion/cymbal-crash1_ff*.wav')
    gong = M.hits('VSCO 1 Percussion/varMetal/Gong/gong_hit_fff.wav')
    bd = M.hits('VSCO 1 Percussion/drums/bass/bdrum_fff_*.wav')

    run = tl['run']
    K = len(run)

    def tt_of(x):                               # time of fractional tick index x (ticks are the beats)
        if x <= K - 1:
            return float(np.interp(x, np.arange(K), run))
        return run[-1] + (x - (K - 1)) * (run[-1] - run[-2])

    def beat_len(x):
        return tt_of(x + 1) - tt_of(x)

    def first_tick(t):
        return int(np.searchsorted(run, t - 1e-6))

    pf_mid = (ppd[261] + ppd[331]) / 2
    seg_pan = {name: pan_at(float(G.pd[G.seg[name]].mean())) for name in RUNS}
    cs = {c: (ppd[a] + ppd[a + 1]) / 2 for c, a in CORNER_PI.items()}
    el_pan = dict(seg_pan, **{c: pan_at(s) for c, s in cs.items()}, bell=pan_at(0.0))
    swell = lambda t: float(keys(t, [(0, 0.8), (T_RUSH, 0.85), (tl['t_mid'], 1.25)]))

    # ---- winding: three ratchet clicks a half-turn, a pizzicato climbing with the tension ----------------
    pk = pan_at(end_pd)
    for k, tw in enumerate(T_WIND):
        for c in (0.0, 0.2, 0.4):
            put('fx', ratchet.play(105, pitch=2 * k * 0.5, dur=0.12), tw + c, 0.55, pk)
        put('band', cpz.play(n(['D3', 'E3', 'F3', 'G3', 'A3', 'Bb3'][k]), 80 + 6 * k), tw, 0.8, pk * 0.6)
    put('str', cel.play(n('D2'), 60, dur=6.0), 0.4, 0.7, 0.0)
    put('str', vla.play(n('A3'), 45, dur=5.0), 1.5, 0.4, 0.2)
    put('fx', whoosh(0.6, 200, 900, 0.5, seed=3), T_NUDGE, 0.5, el_pan['Porch Front'])

    # ---- the escapement: tick, tock, panned to where the pendulum catches ------------------------------
    psi = _pend_psi(np.array(tl['ticks']))
    for i, tk in enumerate(tl['ticks']):
        if tk > tl['t13'] + 0.01 and tk < tl['pend2']:
            continue
        side = float(np.sign(np.sin(psi[i])))
        p = 0.25 * side
        late = tk > tl['t13']
        g = 0.5 if late else (0.9 if tk < tl['t_mid'] + 0.1 else 0.55)
        if late:
            g *= 0.9 ** (tl['ticks'].index(tk) - len(tl['run']) - len(tl['post']))
        if i % 2 == 0:
            put('tick', tick.play(110, dur=0.15), tk, g, p)
        else:
            put('tick', tock.play(105, dur=0.25), tk, g, p)

    # ---- gear by gear: a clunk, and that element's part in the band ------------------------------------
    for el, te in ENGAGE.items():
        p = el_pan[el]
        put('perc', metal.play(100, pitch=-9, dur=0.5), te, 0.45, p)
        put('perc', timp.play(70, pitch=-3, dur=0.6), te, 0.3, p)

    def chord_at(i):
        return PROG[min(len(PROG) - 1, i // BEATS_PER_BAR)]

    e = {el: first_tick(te) for el, te in ENGAGE.items()}
    for i in range(K + 1):
        if i >= K:
            break
        ch = chord_at(i)
        root, tri = VO[ch]
        bt = i % BEATS_PER_BAR
        t = tt_of(i)
        sw = swell(t)
        # bassoon oom-pah: the key's belt
        if i >= e['Right']:
            m = n(root) if bt % 2 == 0 else n(root) + 7
            put('band', bsn.play(m, 95, dur=min(0.3, 0.6 * beat_len(i))), t, 0.9 * sw, seg_pan['Right'])
        # pizzicato cellos on the off-beats: the first gear
        if i >= e['C5']:
            m = n(tri[(bt + 1) % 3]) - 12
            put('band', cpz.play(m, 85), tt_of(i + 0.5), 0.7 * sw, el_pan['C5'])
        # marimba eighths: the shaft
        if i >= e['Porch Right']:
            for h, idx in enumerate(((0, 1), (2, 1))[bt % 2]):
                put('band', mar.play(n(tri[idx]), 70 + 10 * (h == 0)), tt_of(i + 0.5 * h), 0.45 * sw,
                    seg_pan['Porch Right'])
        # glock on the downbeat: the back-right gear
        if i >= e['C4'] and bt == 0:
            put('band', glk.play(n(tri[-1]) + 12, 55), t, 0.3, el_pan['C4'])
        # violas pizz on beats 2 and 4: the back-left gear
        if i >= e['C3'] and bt in (1, 3):
            put('band', vpz.play(n(tri[1]) - 12, 80), t, 0.55 * sw, el_pan['C3'])
        # strings hold the chord: the left belt; timpani on the downbeats: the front-left corner
        if i >= e['Left'] and bt == 0:
            dur = tt_of(i + 4) - t
            vel = float(keys(t, [(ENGAGE['Left'], 45), (T_RUSH, 55), (tl['t_mid'], 95)]))
            for m in tri:
                put('str', vla.play(n(m) - 12, vel, dur=dur + 0.1), t, 0.45, seg_pan['Left'] * 0.6)
            put('str', cel.play(n(root) + 12, vel, dur=dur + 0.1), t, 0.5, seg_pan['Left'] * 0.6)
        if i >= e['C1'] and bt == 0:
            put('perc', timp_lo.play(90, pitch=-2), t, 0.45 * sw, el_pan['C1'])
        # the bell rope creaks on every tock
        if i >= e['Side'] and i % 2 == 1:
            sec = min(0.35, beat_len(i) * 0.8)
            tt = np.arange(int(sec * SR)) / SR
            creak = band(sec, 180, 900, 50 + i) * (0.5 + 0.5 * np.sin(2 * np.pi * 31 * tt)) ** 4 * np.sin(np.pi * tt / sec)
            put('fx', creak, t, 0.18, seg_pan['Side'])
        # the clarinet tune on the chain
        b = i // BEATS_PER_BAR
        if bt == 0 and b in MEL_BARS and i >= e['Porch Left']:
            for bb, m, ln in MEL[MEL_BARS[b]]:
                t0 = tt_of(i + bb)
                d = tt_of(i + bb + ln) - t0
                put('mel', cla.play(n(m), 100, dur=max(0.08, d * 0.85)), t0, 0.8, seg_pan['Porch Left'] * 0.5)
                if b >= 10:
                    put('mel', vpz.play(n(m), 90), t0, 0.5, -seg_pan['Porch Left'] * 0.5)
    put('bell', tub.play(n('D4'), 45, dur=4.0), ENGAGE['bell'], 0.4, el_pan['bell'])

    # ---- the rush to midnight ----------------------------------------------------------------------------
    t_mid = tl['t_mid']
    rush0 = tt_of(4 * 10)
    put('str', ctr.play(n('D2'), 70, dur=t_mid - rush0), rush0, 0.5, 0.0)
    put('str', ctr.play(n('A2'), 60, dur=t_mid - rush0), rush0, 0.4, 0.0)
    for j, m in enumerate(['A4', 'Bb4', 'B4', 'C5', 'C#5', 'D5', 'D#5', 'E5']):   # the last two bars climb
        t0 = tt_of(K - 8 + j)
        put('str', vln.play(n(m), 70 + 6 * j, dur=beat_len(K - 8 + j) + 0.05), t0, 0.6, 0.0)
    put('perc', sroll.play(70, dur=3.0), t_mid - 3.0, 0.5, 0.0)
    put('perc', troll.play(95, dur=2.0), t_mid - 2.0, 0.55, 0.0)
    # the hands meet
    put('perc', crash.play(120), t_mid, 0.6, 0.0)
    put('perc', timp_lo.play(127, pitch=-5), t_mid, 0.9, 0.0)
    put('perc', bd.play(120), t_mid, 0.7, 0.0)
    put('perc', metal.play(127, pitch=-12, dur=1.2), t_mid, 0.6, 0.0)
    for m in ('D2', 'D3', 'A3', 'D4', 'F4'):
        put('str', vla.play(n(m), 110, dur=0.5), t_mid, 0.5, 0.0)
    put('band', bsn.play(n('D2'), 120, dur=0.4), t_mid, 1.0, 0.0)

    # ---- the chime, then twelve -------------------------------------------------------------------------
    hush = tl['chime'][0] - 0.3
    put('str', cel.play(n('D2'), 50, dur=tl['strikes'][0] - hush + 0.2), hush, 0.6, 0.0)
    put('str', vla.play(n('A3'), 40, dur=tl['strikes'][0] - hush + 0.2), hush, 0.4, 0.0)
    for tc, nm, c in zip(tl['chime'], CHIME_NOTES, CHIME_AT):
        put('bell', tub.play(n(nm), 100, dur=3.0), tc, 0.55, el_pan[c])

    strikes = tl['strikes']
    for h, ts in enumerate(strikes):
        p = pan_pi(HOUR_PI[h])
        g = 1.25 if h == 11 else 1.0
        put('bell', bigbell('D3'), ts, 0.9 * g, p)
        put('bell', tub.play(n('D4'), 115, dur=4.0), ts, 0.35 * g, p)
        put('perc', timp_lo.play(85 + 3 * h, pitch=-5), ts, 0.4 + 0.03 * h, p)
        nxt = strikes[h + 1] if h + 1 < len(strikes) else tl['t13']
        put('str', vln.play(n(CLIMB[h]), 60 + 4 * h, dur=nxt - ts + 0.1), ts, 0.45, 0.0)
        put('str', cel.play(n('D2'), 55 + 4 * h, dur=nxt - ts + 0.1), ts, 0.4, 0.0)
        if h >= 6:
            put('str', hrn.play(n('A3'), 60 + 6 * (h - 6), dur=nxt - ts + 0.1), ts, 0.4, 0.0)
            put('str', hrn.play(n('D3'), 60 + 6 * (h - 6), dur=nxt - ts + 0.1), ts, 0.4, 0.0)
    t12 = strikes[-1]
    for m in ('D3', 'F#3', 'A3', 'D4', 'F#4', 'A4'):          # twelve: a bright D major, held
        put('str', vla.play(n(m), 105, dur=4.0), t12, 0.4, 0.0)
        put('str', hrn.play(n(m) - 12, 100, dur=4.0), t12, 0.25, 0.0)
    put('perc', crash.play(100), t12, 0.35, 0.0)

    # ---- the thirteenth: a sour E-flat, and everything stops dead ---------------------------------------
    t13 = tl['t13']
    put('bell', bigbell('Eb3', sour=True), t13, 1.3, 0.0)
    put('bell', tub.play(n('Eb4'), 127, dur=2.0), t13, 0.5, 0.0)
    put('perc', gong.play(127), t13, 1.0, 0.0)
    put('perc', crash.play(127), t13, 0.6, 0.0)
    put('perc', timp_lo.play(127, pitch=-4), t13, 1.0, 0.0)
    put('perc', bd.play(127), t13, 0.9, 0.0)
    for m in ('Eb3', 'E3', 'Bb3', 'Eb4'):
        put('str', vla.play(n(m), 120, dur=1.0), t13, 0.45, 0.0)
        put('str', hrn.play(n(m) - 12, 120, dur=1.0), t13, 0.3, 0.0)

    # ---- boing: the mainspring jumps out of the key end -------------------------------------------------
    tb = tl['boing']
    sec = 2.2
    tt = np.arange(int(sec * SR)) / SR
    fr = 150 * (1 + 0.45 * np.exp(-tt / 0.55) * np.sin(2 * np.pi * 4.2 * tt))
    y = np.tanh(1.8 * tone(fr, sec, harm=10, tilt=0.9)) * np.exp(-tt / 0.8) * np.clip(tt / 0.004, 0, 1)
    put('fx', y, tb, 0.5, pk, choke=False)
    put('fx', slide(0.0, 0.25, 500, 1400, 0.6, 0.4, 0.5)[0] * 1.0, tb, 0.4, pk, choke=False)
    put('perc', clank.play(110, pitch=3), tb, 0.4, pk, choke=False)

    # ---- the cuckoo: one fine call, then a squawk, and feathers -----------------------------------------
    pc = pan_at(pf_mid)

    def ocarina(nm, sec, vel=1.0):
        tt = np.arange(int(sec * SR)) / SR
        f = 440 * 2 ** ((n(nm) - 69) / 12) * (1 + 0.004 * np.sin(2 * np.pi * 5 * tt))
        y = tone(f, sec, harm=3, tilt=2.2) + 0.15 * band(sec, 1000, 4000, 9) * 0.3
        return vel * y * np.clip(tt / 0.02, 0, 1) * np.clip((sec - tt) / 0.05, 0, 1)

    tc = tl['cuck']
    put('fx', ocarina('F5', 0.22), tc, 0.5, pc, choke=False)
    put('fx', ocarina('D5', 0.4), tc + 0.3, 0.5, pc, choke=False)
    put('perc', tick.play(120, pitch=-5), tc, 0.6, pc, choke=False)               # the door
    put('perc', tick.play(110, pitch=-8), tc + 1.1, 0.5, pc, choke=False)
    tc2 = tl['cuck2']
    put('perc', tick.play(120, pitch=-5), tc2, 0.6, pc, choke=False)
    put('fx', ocarina('F5', 0.22), tc2, 0.5, pc, choke=False)
    sec = 0.55
    tt = np.arange(int(sec * SR)) / SR
    fsq = np.interp(tt, [0, 0.12, 0.3, 0.55], [620, 1250, 900, 430])
    sq = np.tanh(2.5 * tone(fsq, sec, harm=14, tilt=0.7)) * (0.55 + 0.45 * np.sign(np.sin(tt * 70)))
    sq += 0.35 * band(sec, 1500, 6000, 77)
    sq *= np.clip(tt / 0.01, 0, 1) * np.exp(-tt / 0.3)
    put('fx', sq, tc2 + 0.3, 0.45, pc, choke=False)
    for k in range(10):                                       # feathers
        t0 = tc2 + 0.35 + rng.uniform(0, 1.2)
        put('fx', band(0.15, 2000, 8000, 300 + k) * np.hanning(int(0.15 * SR)), t0, 0.06, pc + rng.uniform(-0.4, 0.4),
            choke=False)
    for j, m in enumerate(('Bb2', 'A2', 'Ab2')):              # uh-oh
        put('band', bsn.play(n(m), 100, dur=0.25 if j < 2 else 0.6), tc2 + 1.3 + 0.3 * j, 1.0, 0.0, choke=False)

    # ---- the gears pop off and roll down the runs ---------------------------------------------------------
    gp = _gear_paths(ppd)
    rets = _returns()
    ar = 1000                                                 # roll motion sampled at 1 kHz for the rattle
    for c in GEAR_ORDER:
        s0, d, dist, dur, tp = gp[c]
        nt = GEARS[c][0]
        # pop
        tt = np.arange(int(0.08 * SR)) / SR
        put('fx', np.sin(2 * np.pi * np.cumsum(300 * 4 ** (tt / 0.04)) / SR) * np.exp(-tt / 0.03), tp, 0.45,
            pan_at(s0), choke=False)
        put('perc', metal.play(90, pitch=6, dur=0.4), tp, 0.3, pan_at(s0), choke=False)
        span = rets[c] - tp
        ts = np.arange(0, span, 1 / ar)
        if c == 'C1':                                         # a coin spinning down: ever faster rattles
            ph = 2.5 * ts + 22 * np.minimum(ts, 2.6) ** 3 / (3 * 2.6 ** 2)
            ph[ts > 2.6] = ph[ts <= 2.6][-1]
            hits = np.nonzero(np.diff(np.floor(ph * 2)) > 0)[0]
            for h_ in hits:
                put('fx', band(0.03, 1500, 7000, int(h_)) * np.exp(-np.arange(int(0.03 * SR)) / SR / 0.006),
                    tp + ts[h_], 0.32, pan_at(s0), choke=False)
            put('perc', clank.play(100), tp + 2.65, 0.4, pan_at(s0), choke=False)
            put('perc', clank.play(70, pitch=2), tp + 2.8, 0.25, pan_at(s0), choke=False)
            continue
        pos = np.array([_roll(c, float(x), dist, dur) for x in ts])
        teeth = np.floor(nt * pos / (2 * np.pi * 22.0))
        hits = np.nonzero(np.diff(teeth) != 0)[0]
        for h_ in hits:
            sp = s0 + d * pos[h_]
            if c == 'C5' and sp > end_pd:
                continue
            put('fx', band(0.025, 2500, 9000, int(h_) + nt) * np.exp(-np.arange(int(0.025 * SR)) / SR / 0.005),
                tp + ts[h_], 0.3, pan_at(min(sp, end_pd)), choke=False)
        if c == 'C5':                                         # off the end of the house ... and down
            t_off = tp + float(ts[np.argmax(s0 + d * pos > end_pd)])
            put('fx', slide(0.0, 0.9, 1100, 220, 1.0, 0.35, 0.6)[0], t_off, 0.45, pk, choke=False)
            put('perc', clank.play(80, pitch=-6), t_off + 1.05, 0.25, pk, choke=False)
            put('perc', clank.play(60, pitch=-3), t_off + 1.3, 0.15, pk, choke=False)
        else:
            for q in (0.0, 0.32, 0.64):
                put('perc', clank.play(int(100 - 40 * q), pitch=4 - 4 * q), tp + dur + q, 0.35 - 0.3 * q,
                    pan_at(s0 + d * dist), choke=False)
        # a xylophone run down with each roll
        notes = ['A5', 'F5', 'D5', 'A4', 'F4', 'D4']
        for j, m in enumerate(notes):
            put('band', xyl.play(n(m), 90), tp + 0.1 + j * min(dur, 1.8) / len(notes), 0.35,
                pan_at(s0 + d * min(dist, end_pd - s0 if d > 0 else dist) * j / len(notes)), choke=False)

    # the chime tune again on a music box that is running down: slower and flatter with every note
    t, gap = tl['pop'] + 0.2, 0.22
    for j, nm in enumerate(CHIME_NOTES + CHIME_NOTES[:4]):
        if t > tl['reset'] - 0.3:
            break
        put('band', glk.play(n(nm) - j // 3, 70 - 2 * j), t, 0.35, 0.0, choke=False)
        put('band', cpz.play(n(nm) - 24 - j // 3, 70), t, 0.35, 0.0, choke=False)
        t += gap
        gap *= 1.17

    # ---- the reset: gears zip home, the spring goes back in, a recount to twelve, one small ding -----------
    for j, c in enumerate(['C5', 'C2', 'C4', 'C3', 'C1']):
        tr = rets[c]
        put('fx', whoosh(0.35, 2500, 400, 0.4, seed=40 + j), tr, 0.4, pan_at(cs[c]), choke=False)
        put('band', glk.play(n(['D5', 'F5', 'A5', 'C6', 'D6'][j]), 80), tr + 0.35, 0.4, pan_at(cs[c]), choke=False)
        put('perc', tick.play(110, pitch=4), tr + 0.35, 0.4, pan_at(cs[c]), choke=False)
    put('fx', slide(0.0, 0.5, 1200, 300, 0.6, 0.35, 0.6)[0], tl['reset'], 0.3, pk, choke=False)
    tr0 = tl['reset'] + 2.0
    for h, m in enumerate(['D4', 'E4', 'F#4', 'G4', 'A4', 'B4', 'C#5', 'D5', 'E5', 'F#5', 'G5', 'A5']):
        put('band', mar.play(n(m), 75 + 2 * h), tr0 + 0.1 * h, 0.45, pan_pi(HOUR_PI[h]), choke=False)
    put('bell', tub.play(n('D5'), 55, dur=3.0), tl['reset'] + 3.4, 0.4, pc, choke=False)
    put('band', bsn.play(n('A2'), 90, dur=0.12), tl['reset'] + 4.0, 0.9, 0.0, choke=False)     # ahem
    put('band', bsn.play(n('D2'), 95, dur=0.22), tl['reset'] + 4.2, 0.9, 0.0, choke=False)
    last = tl['again'][-1]
    for m in ('D3', 'A3', 'D4', 'F4'):
        put('band', cpz.play(n(m), 70), last, 0.5, 0.0, choke=False)
