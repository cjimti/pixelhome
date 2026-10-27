"""The Last Train: a whistle far off behind the house, a headlight growing at the back end of Side, and
a spectral locomotive rolls in pulling four carriages of flickering ghost passengers and a caboose. It
brakes into the porch notch (the station), its headlight down the Right wing where ghosts wait under
the gas lamps. Three passengers hop off through the back of the train and wander home along Left;
four hop on through the engine and take their seats; the conductor steps down with his lantern, rings
the bell, and the train pulls out, chuffing slower than walking and then faster and faster, round
and round the house (off the right end, back in at the far end of Side). A late little ghost with a
pumpkin lantern comes running from the back of the house, gets bowled along by every lap, until the
caboose scoops him up and he rides one lap on the back, lantern swinging, before the whole train
dives into a fog tunnel at the right end and is gone.

Everything is in path distance. The train is a list of parts in train coordinates (distance behind the
nose); its nose follows one analytic motion (cruise in, brake, stop, constant acceleration out) and
wraps round a lap of the roofline plus a hidden stretch beyond the free ends. Chuffs are where the
nose crosses each CHUFF units of travel, so smoke puffs, the side rods and the music all keep the
same time. _plan() holds the motion, the station's hop schedule and the late ghost's run, and is shared
by render() and score()."""
import numpy as np
from pixelhome.fx import DT, hexc, light, smoothstep, Flicker, nframes

CODE = 'HW10'
TITLE = 'The Last Train'
KIND = 'show'
DESCRIPTION = ('A ghost train rolls into the porch station, swaps passengers and rings its bell, then '
               'laps the house faster and faster. A late little ghost chases it until the caboose '
               'scoops him up, and the whole train dives into a fog tunnel.')

D = 76.5

# ---- motion: nose position s(t) in path distance; the house is 0..L, laps are L + 2*OFF ----
OFF = 180.0                  # hidden run beyond each free end (the "tunnel" between laps)
V0 = 280.0                   # arrival speed
TE = 9.0                     # the nose reaches path 0 (back end of Side)
S_STOP = 2015.0              # nose stops just short of the Porch Right / Right corner
DBR = 700.0                  # braking distance
A = 26.0                     # departure acceleration
CHUFF = 90.0                 # travel per chuff (four per wheel turn)

SB = S_STOP - DBR
TB = TE + SB / V0            # brakes on
AB = V0 ** 2 / (2 * DBR)
TS = TB + 2 * DBR / V0       # stopped

# ---- the station: a waltz beat; hops, bell and whistle are on it ----
T_ST = 19.0
BEAT = 0.5


def sb(k):
    return T_ST + BEAT * k


TD = sb(30)                  # departure (34.0)
BELL = [sb(18), sb(19), sb(21), sb(22)]
WHISTLE_ALL = [(sb(26), 0.85), (sb(28), 0.3)]   # all aboard: long, short
JOLT = 0.16                  # couplings take up the slack one after another at departure
HOP = 0.32                   # flight time of a hop, inside its beat

# train parts in train coordinates u (distance behind the nose)
LOCO = 130.0
TENDER = (136.0, 186.0)
NCAR, CAR0, CARL, CARG = 4, 196.0, 150.0, 10.0
WIN = [22.0, 48.0, 75.0, 102.0, 128.0]      # window centres inside a carriage
WINW = 13.0
CAB0 = CAR0 + NCAR * (CARL + CARG)          # caboose
CABL = 104.0
TRAIN = CAB0 + CABL
STACK = 26.0
CAB_U = 112.0

GHOSTC = [hexc('#9dffcf'), hexc('#a8e8ff'), hexc('#d8b8ff'), hexc('#e6fff2')]


def windows():
    """Train coordinate of every window, carriage by carriage."""
    return [CAR0 + c * (CARL + CARG) + w for c in range(NCAR) for w in WIN]


def nose(t):
    t = np.asarray(t, float)
    tau = np.clip(t - TB, 0, TS - TB)
    s = np.where(t < TB, V0 * (t - TE), SB + V0 * tau - 0.5 * AB * tau ** 2)
    s = np.where((t >= TS) & (t < TD), S_STOP, s)
    return np.where(t >= TD, S_STOP + 0.5 * A * (t - TD) ** 2, s)


def speed(t):
    t = np.asarray(t, float)
    v = np.where(t < TB, V0, np.clip(V0 - AB * (t - TB), 0, None))
    v = np.where((t >= TS) & (t < TD), 0.0, v)
    return np.where(t >= TD, A * (t - TD), v)


def _wrap(p, C):
    return ((p + OFF) % C) - OFF


def _plan(G):
    """Everything render() and score() share: laps, chuffs, the station hops, the late ghost."""
    L = G.length
    C = L + 2 * OFF
    P = dict(L=L, C=C)
    # laps: the nose leaves the right end at s = L + k*C (k = 0, 1, ...) and comes back in at path 0
    # at s = (k+1)*C. The train goes into the fog tunnel instead of round again at lap K_END.
    def t_at(sv):
        return TD + np.sqrt(2 * max(sv - S_STOP, 0) / A)
    K_END = 5
    P['exits'] = [t_at(L + k * C) for k in range(K_END + 1)]
    P['entries'] = [t_at((k + 1) * C) for k in range(K_END)]
    P['K_END'] = K_END
    P['S_END'] = L + K_END * C                       # nose value at the tunnel mouth
    P['T_TUN'] = t_at(P['S_END'])                    # nose into the fog
    P['T_GONE'] = t_at(P['S_END'] + TRAIN)           # tail into the fog

    # chuffs: the nose crossing each multiple of CHUFF (fine grid), until the train is in the tunnel
    tf = np.arange(0, P['T_GONE'] + 0.6, 0.0005)
    k = np.floor(nose(tf) / CHUFF)
    i = np.nonzero(np.diff(k) > 0)[0] + 1
    P['chuffs'] = tf[i]
    P['chuff_s'] = k[i] * CHUFF

    # ---- the station ----
    wins = windows()
    rng = np.random.default_rng(10)
    occ = np.zeros(len(wins), bool)
    occ[[0, 2, 3, 6, 7, 9, 11, 12, 14, 15, 17, 18, 19]] = True
    colour = rng.integers(0, len(GHOSTC), len(wins))
    seat_t = np.where(occ, -1.0, np.inf)            # occupied from this time
    leave_t = np.full(len(wins), np.inf)            # empty from this time
    ghosts = []                                     # (colour id, [(t_start, x0, x1)], fade start, fade end)

    def hops(x0, x1, k0, step):
        n = max(1, int(np.ceil(abs(x1 - x0) / step)))
        xs = np.linspace(x0, x1, n + 1)
        return [(sb(k0 + j), xs[j], xs[j + 1]) for j in range(n)]

    for j, (w, home) in enumerate(((14, 640.0), (7, 760.0), (17, 560.0))):   # alighting: out the back, home along Left
        x0 = S_STOP - wins[w]
        hp = hops(x0, home, 4 + 2 * j, 72.0)
        leave_t[w] = hp[0][0]
        ghosts.append(dict(c=int(colour[w]), hops=hp, fade=(hp[-4][0], hp[-1][0] + 0.6), off=True))
    boarders = [(2150.0, 1), (2228.0, 4), (2306.0, 5), (2384.0, 8)]           # waiting on Right, under the lamps
    for j, (x0, w) in enumerate(boarders):
        hp = hops(x0, S_STOP - wins[w], 9 + j, 70.0)
        seat_t[w] = hp[-1][0] + HOP
        colour[w] = j % len(GHOSTC)
        ghosts.append(dict(c=int(colour[w]), hops=hp, fade=None, off=False, wait=x0))
    P['wins'], P['seat_t'], P['leave_t'], P['wcol'] = wins, seat_t, leave_t, colour
    P['ghosts'] = ghosts
    # the conductor: out of the cab, two hops forward, back in two hops after the bell
    cab = S_STOP - CAB_U
    P['cond'] = [(sb(2), cab, cab + 85), (sb(3), cab + 85, cab + 170),
                 (sb(24), cab + 170, cab + 85), (sb(25), cab + 85, cab)]

    # ---- the late ghost: runs from the back of the house to the platform; laps bowl him along ----
    TW, PLAT = 35.0, 1485.0
    F = nframes(D)
    t = np.arange(F) * DT
    s = nose(t)
    v = speed(t)
    w = np.full(F, np.nan)
    state = np.zeros(F, int)                         # 0 run, 1 wait, 2 carried, 3 dazed, 4 aboard
    x, mode, daze = -10.0, 0, 0.0
    T_SCOOP = None
    bumps, runs, lands = [], [TW], []
    for f in range(F):
        if t[f] < TW:
            continue
        if mode == 4:
            w[f], state[f] = _wrap(s[f] - (TRAIN - 6), C), 4
            continue
        d = (_wrap(s[f], C) - x) % C if t[f] >= TD else -1
        on = t[f] >= TD and 0 <= d <= TRAIN and s[f] - d < P['S_END'] and v[f] > 0
        if on and s[f] >= (K_END - 1) * C and d >= TRAIN - 14:
            mode, T_SCOOP = 4, t[f]                  # the caboose's back step: grabbed
            w[f], state[f] = x, 4
            continue
        if on:
            if mode != 2:
                bumps.append(t[f])
            mode = 2
            x += 0.22 * v[f] * DT
        elif mode == 2:
            mode, daze = 3, t[f] + 0.7
            lands.append((t[f], x))
        elif mode == 3 and t[f] >= daze:
            mode = 0
            runs.append(t[f])
        if mode in (0, 1):
            gap = PLAT - x
            if abs(gap) < 4:
                mode = 1
            else:
                mode = 0
                x += np.sign(gap) * min(abs(gap), (150.0 if gap > 0 else 110.0) * DT)
        w[f], state[f] = x, mode
    P['wisp'], P['wstate'], P['bumps'], P['T_SCOOP'], P['TW'], P['PLAT'] = w, state, bumps, T_SCOOP, TW, PLAT
    P['runs'], P['lands'] = runs, lands
    # whistles (start, length, kind): far off, nearer, coming in, the stop, all aboard, every lap, the scoop, the tunnel
    wh = [(2.2, 1.3, 'far'), (5.6, 1.5, 'near'), (TE - 0.4, 1.7, 'in'), (TS - 0.9, 0.4, 'toot')]
    wh += [(t0, d0, 'aboard') for t0, d0 in WHISTLE_ALL]
    wh += [(te - 0.1, 0.35, 'lap') for te in P['entries'][:-1]]
    wh += [(T_SCOOP + 0.05, 0.9, 'scoop'), (P['T_TUN'] - 0.3, 2.6, 'tunnel')]
    P['whistles'] = wh
    return P


FOG = hexc('#2c4a6a')
HEAD = hexc('#fff3d6')
BEAM = hexc('#ffe0a0')
BOILER = hexc('#30e09a')
BRASS = hexc('#b8ffe0')
FIRE = hexc('#ff8a2a')
CAR = hexc('#6a58c8')
CABOOSE = hexc('#c8402a')
TAIL = hexc('#ff2008')
SMOKE = hexc('#a49cd8')
STEAM = hexc('#e8f0ff')
LAMP = hexc('#ffb060')
LANT = hexc('#ffa030')
WISP = hexc('#f6eeff')
WLANT = hexc('#ff7410')
TFOG = hexc('#8fd8d0')
SPARK = hexc('#ffc070')
TRAIL = hexc('#5a48c0')
COLS = [HEAD, BOILER, BRASS, FIRE, CAR, CABOOSE, TAIL, LAMP, LANT, WISP, WLANT, SPARK] + GHOSTC
(cHEAD, cBOIL, cBRASS, cFIRE, cCAR, cCAB, cTAIL, cLAMP, cLANT, cWISP, cWLANT, cSPARK) = range(12)
cGHOST = 12
LAMPS = [2160.0, 2300.0, 2440.0]
LAMP_OUT = [75.0, 74.5, 74.0]


def _hop_x(hops, t):
    """Position and hop arc (0..1) of a hopping ghost at time t; None before its first hop."""
    if t < hops[0][0]:
        return None, 0.0, -1.0
    for ts, x0, x1 in hops:
        if t < ts + BEAT:
            u = np.clip((t - ts) / HOP, 0, 1)
            return x0 + (x1 - x0) * smoothstep(0, 1, u), float(np.sin(np.pi * u)), t - ts - HOP
    return hops[-1][2], 0.0, t - hops[-1][0] - HOP


def render(G, seed=10):
    rng = np.random.default_rng(seed)
    P = _plan(G)
    L, C = P['L'], P['C']
    pdp = G.pd[G.path]
    wpx = np.gradient(pdp)
    e0, e1 = pdp - wpx / 2, pdp + wpx / 2
    wins = P['wins']
    wfl = Flicker(rng, len(wins), 0.3, 1.6)
    lfl = Flicker(rng, 3, 0.8, 3.0)
    ffl = Flicker(rng, 2, 4.0, 11.0)
    fog_n = Flicker(rng, G.N, 0.02, 0.12)
    fog_sp = np.sin(pdp / 150) * np.sin(pdp / 67 + 1.3)
    blink = rng.uniform(0, 7, len(wins))
    ch, ch_s = P['chuffs'], P['chuff_s']
    S_END, T_TUN, T_GONE, T_SCOOP = P['S_END'], P['T_TUN'], P['T_GONE'], P['T_SCOOP']
    wisp, wst = P['wisp'], P['wstate']
    trail = np.zeros(G.N)
    tdec = np.exp(-DT / 0.45)

    F = nframes(D)
    out = np.zeros((F, G.N, 3))
    for fi in range(F):
        t = fi * DT
        s = float(nose(t))
        v = float(speed(t))
        dep = t >= TD
        spans = []

        def add(a, z, I, c):
            spans.append((a, z, I, c))

        def tun(q, p):
            """Fade of a train part at house position q (fog tunnel on the last pass)."""
            if dep and p > S_END - L:
                return 1 - smoothstep(L - 240, L - 20, q)
            return 1.0

        def part(u0, u1, I, c):
            front = s - u0
            if dep and front - (u1 - u0) >= S_END:
                return
            qf = ((front + OFF) % C) - OFF if dep else front
            if qf < -2 or qf - (u1 - u0) > L + 2:
                return
            I = I * tun(qf - (u1 - u0) / 2, front)
            if I > 0.002 or I < -0.002:
                add(qf - (u1 - u0), qf, I, c)

        wk = max([smoothstep(0, 0.08, t - w0) * (1 - smoothstep(d0, d0 + 0.25, t - w0))
                  for w0, d0, _ in P['whistles'] if w0 <= t < w0 + d0 + 0.3] + [0.0])
        flash_sc = 0.6 * np.exp(-(t - T_SCOOP) / 0.35) if T_SCOOP and t >= T_SCOOP else 0.0
        # ---- the train ----
        if s > -40 and t < T_GONE + 0.2:
            fl = ffl(t)
            part(0, 5, 0.85 + 0.15 * wk, cHEAD)
            part(5, 22, 0.22, cBOIL)
            part(22, 30, 0.34, cBRASS)                       # stack
            part(30, 95, 0.2, cBOIL)
            for b in (44, 64, 84):
                part(b, b + 2.5, 0.42, cBRASS)
            ph = 2 * np.pi * s / (4 * CHUFF)
            rod = 62 + 16 * np.sin(ph)
            part(rod - 2, rod + 2, 0.5, cBRASS)              # the side rod, one turn per four chuffs
            part(95, LOCO, 0.18, cBOIL)
            cond_in = not (P['cond'][0][0] + 0.1 <= t < P['cond'][3][0] + HOP)
            part(104, 120, (0.4 + 0.08 * fl[0]) * (1.25 if cond_in and t > 5 else 1.0), cFIRE)
            part(TENDER[0], TENDER[1], 0.15, cBOIL)
            part(150, 176, 0.11 + 0.04 * fl[1], cFIRE)       # coal glow
            for c in range(NCAR):
                c0 = CAR0 + c * (CARL + CARG)
                part(c0, c0 + CARL, 0.2, cCAR)
                jolt = 0.5 * np.exp(-(t - TD - JOLT * (c + 2)) / 0.15) if t >= TD + JOLT * (c + 2) else 0.0
                part(c0, c0 + 2.5, 0.32 + jolt, cCAR)
                part(c0 + CARL - 2.5, c0 + CARL, 0.32, cCAR)
            for k, u in enumerate(wins):
                a, z = u - WINW / 2, u + WINW / 2
                seated = P['seat_t'][k] <= t < P['leave_t'][k]
                if seated:
                    I = 0.5 + 0.1 * wfl(t)[k]
                    if ((t + blink[k]) % 7.0) < 0.18:
                        I *= 0.35                            # a passenger turns away
                    st = P['seat_t'][k]
                    if st > 0 and t >= st:
                        I += 0.5 * np.exp(-(t - st) / 0.25)
                    part(a, z, I, cGHOST + int(P['wcol'][k]))
                part(a, z, -0.16, cCAR)                      # window: the coach body is cut out
            part(CAB0, CAB0 + CABL, 0.2 + flash_sc * 0.5, cCAB)
            part(CAB0 + 30, CAB0 + 44, 0.3 + 0.05 * fl[1] + flash_sc, cFIRE)   # cupola lamp
            part(TRAIN - 5, TRAIN, 0.75, cTAIL)
            # brakes: sparks under the wheels
            if TB + 0.6 <= t < TS:
                for c in range(NCAR):
                    for wu in (18.0, CARL - 18.0):
                        if rng.random() < 0.35:
                            u = CAR0 + c * (CARL + CARG) + wu + rng.uniform(-4, 4)
                            part(u - 1.5, u + 1.5, rng.uniform(0.3, 0.7) * smoothstep(TB + 0.6, TB + 1.4, t), cSPARK)

        # ---- station people ----
        for gh in P['ghosts']:
            x, arc, after = _hop_x(gh['hops'], t)
            if x is None:
                if gh['off'] or t < 2.0:
                    continue
                x = gh['wait']
                I = 0.4 * smoothstep(2.0, 5.0, t) * (1 + 0.15 * np.sin(2 * np.pi * 0.45 * t + x))
            else:
                if not gh['off'] and after > 0:
                    continue                                  # seated: the window has him now
                I = 0.48 + 0.25 * arc + (0.35 * np.exp(-after / 0.15) if after > -HOP else 0)
                if gh['fade']:
                    I *= 1 - smoothstep(gh['fade'][0], gh['fade'][1], t)
            if I > 0.003:
                add(x - 5.5, x + 5.5, I, cGHOST + gh['c'])
        cs = P['cond']
        if cs[0][0] <= t < cs[3][0] + HOP:
            x, arc, after = _hop_x(cs, t)
            I = 0.7 + 0.2 * arc
            sw = 4.5 * np.sin(2 * np.pi * 0.8 * t)
            for bt in BELL:
                if t >= bt:
                    k = np.exp(-(t - bt) / 0.22)
                    I += 0.4 * k
                    sw += 9 * k * np.sin(2 * np.pi * 3.0 * (t - bt))
            add(x + sw - 2.5, x + sw + 2.5, I, cLANT)
        # gas lamps on the platform
        bell_k = sum(np.exp(-(t - bt) / 0.3) for bt in BELL if t >= bt)
        for j, x in enumerate(LAMPS):
            I = (0.26 + 0.035 * lfl(t)[j]) * smoothstep(0.5, 3.5, t) * (1 + 0.25 * bell_k)
            I *= (1 - smoothstep(LAMP_OUT[j], LAMP_OUT[j] + 0.3, t)) * (1 + 0.5 * np.exp(-((t - LAMP_OUT[j]) / 0.08) ** 2))
            add(x - 3, x + 3, I, cLAMP)

        # ---- the late ghost ----
        x = wisp[fi]
        if not np.isnan(x) and t < T_GONE + 0.1:
            m = wst[fi]
            pop = smoothstep(P['TW'], P['TW'] + 0.4, t)
            if m == 0:
                prev = wisp[fi - 1] if fi else x
                dr = 1.0 if x >= prev else -1.0
                I, lx = 0.72 + 0.12 * np.sin(2 * np.pi * t / 0.3), x + dr * 8
            elif m == 1:
                I, lx = 0.7 + 0.15 * np.sin(2 * np.pi * 2.2 * t), x + 8 + 2 * np.sin(2 * np.pi * 2.2 * t)
            elif m == 2:
                I, lx = 0.55 + 0.3 * (np.sin(2 * np.pi * 9 * t) > 0), x + 8 * np.sign(np.sin(2 * np.pi * 6 * t))
            elif m == 3:
                I, lx = 0.42, x + 6 + 3 * np.sin(2 * np.pi * 1.2 * t)
            else:
                lx = x - 9 - 4 * np.sin(2 * np.pi * 1.6 * t)  # aboard: lantern swung out behind
                I = 0.8 + flash_sc
                I *= tun(x, s - (TRAIN - 6))
            if 0 <= x <= L:
                add(x - 6, x + 6, I * pop, cWISP)
            if 0 <= lx <= L:
                add(lx - 2.5, lx + 2.5, (0.75 if m != 3 else 0.35) * pop * (I / max(I, 1e-3) if m != 4 else tun(x, s - TRAIN)), cWLANT)
        # goodbye from inside the fog
        for tb in (T_GONE + 4.2, T_GONE + 4.75):
            if tb <= t < tb + 0.35:
                add(L - 46, L - 41, 0.55 * np.sin(np.pi * (t - tb) / 0.35), cWLANT)

        # ---- coverage ----
        sp = np.array(spans) if spans else np.zeros((0, 4))
        ov = np.clip(np.minimum(sp[:, 1:2], e1) - np.maximum(sp[:, 0:1], e0), 0, None) / wpx
        cid = sp[:, 3].astype(int)
        buf = np.zeros((G.N, 3))
        cov = np.zeros(G.N)
        for c in np.unique(cid):
            m = cid == c
            Ic = np.clip(sp[m, 2] @ ov[m], 0, 1)
            buf += light(COLS[c], Ic)
            if c != cTAIL:
                cov = np.maximum(cov, np.clip(Ic * 3, 0, 1))
        train_cov = np.zeros(G.N)
        m = (cid == cCAR) | (cid == cBOIL) | (cid == cCAB)
        if m.any():
            train_cov = np.clip(np.abs(sp[m, 2]) @ ov[m], 0, 1)

        # ---- light, smoke and fog ----
        beam = np.zeros(G.N)
        if t < T_GONE:
            if not dep:
                dd = pdp - s
                if s < 0:                                   # still out beyond the back of the house
                    beam += (0.22 + 0.2 * wk) * smoothstep(1.5, 6, t) / (1 + (-s) / 450) * np.exp(-pdp / 70) * (1 + 0.1 * ffl(t)[0])
            else:
                dd = (pdp - ((s + OFF) % C - OFF)) % C
            fwd = (dd > 0) & (dd < 460)
            bI = np.where(fwd, (0.36 + 0.14 * wk) * np.exp(-np.clip(dd, 0, None) / 150), 0)
            if dep and s > S_END - 40:
                bI *= 1 - smoothstep(S_END - 40, S_END + 30, s)
            beam += bI * (1 - smoothstep(L - 240, L - 20, pdp) * (dep and s > S_END - L))
        smoke = np.zeros(G.N)
        live = (ch <= t) & (ch > t - 1.8)
        for tc, sc in zip(ch[live], ch_s[live]):
            age = t - tc
            q = sc - STACK
            if tc >= TD:
                if q >= S_END:
                    continue
                q = (q + OFF) % C - OFF
            q -= 14 * age * (1 if tc >= TD or tc < TB else 0.4)
            if -60 < q < L + 60:
                sg = 9 + 38 * age
                smoke += 0.3 * np.exp(-age / 0.55) * np.exp(-0.5 * ((pdp - q) / sg) ** 2) * (1 - smoothstep(L - 240, L - 20, q) * (tc >= TD and sc > S_END - L))
        steam = np.zeros(G.N)
        for t0, dur, amp in [(TS - 0.15, 2.6, 0.42)] + [(w0, d0 + 1.2, 0.3) for w0, d0 in WHISTLE_ALL] + [(TD - 0.3, 2.4, 0.38)]:
            if t0 <= t < t0 + dur:
                age = t - t0
                env = smoothstep(0, 0.2, age) * (1 - smoothstep(0.35 * dur, dur, age))
                sg = 25 + 60 * age
                steam += amp * env * np.exp(-0.5 * ((pdp - (S_STOP - STACK)) / sg) ** 2)
        trail = np.maximum(trail * tdec, train_cov * 0.12 * smoothstep(300, 900, v))
        fog = 0.065 * smoothstep(0, 3, t) * (1 + 0.3 * fog_sp * np.sin(0.21 * t) + 0.2 * fog_n(t))
        fog *= 1 - 0.55 * smoothstep(D - 3.5, D, t)
        tf = 0.3 * smoothstep(T_TUN - 3.2, T_TUN - 0.8, t) * (1 - smoothstep(T_GONE + 2.5, T_GONE + 8.5, t))
        tf += 0.18 * np.exp(-(t - T_GONE) / 0.6) * (t >= T_GONE)
        tunnel = tf * smoothstep(L - 330, L - 50, pdp) * (1 + 0.35 * fog_n(t * 2.3) * np.sin(pdp / 23 + 1.7 * t))
        free = 1 - cov
        buf += (light(BEAM, beam * free) + light(SMOKE, smoke * free) + light(STEAM, steam * free) +
                light(TRAIL, trail * free) + light(TFOG, tunnel * free) + light(FOG, fog * free))
        out[fi][G.path] = np.clip(buf, 0, 1)
    return out


# ---------------------------------------------------------------- music ----------------------------------------------
# G minor. The train is the rhythm section: every chuff in _plan() is a steam chuff, a brush tap and a cello stroke,
# so the band slows into the station and speeds up round the house with the lights. The tune rides that grid with a
# beat of one, two or four chuffs (shifted at bar lines) so it stays singable while the chuffs blur. At the station
# the music is a waltz on the hop beat: harp notes where ghosts land, marimba where they sit down, the conductor's
# bell, the steam whistle. Each lap adds a part; the scoop turns the tune major. Whistles, bell, chuffs and steam
# are synthesised here; everything else is VSCO2 CE and Surge XT. Sounds are panned to where they happen.

CH = {'Gm': (55, 58, 62), 'Cm': (55, 60, 63), 'D7': (54, 57, 60, 62), 'Eb': (55, 58, 63),
      'G': (55, 59, 62), 'C': (55, 60, 64)}
ROOT = {'Gm': 43, 'Cm': 36, 'D7': 38, 'Eb': 39, 'G': 43, 'C': 36}
MAJOR = {'Gm': 'G', 'Cm': 'C', 'D7': 'D7', 'Eb': 'C', 'G': 'G', 'C': 'C'}
THEME = [('Gm', [(0, 'D4', 1), (1, 'G4', .5), (1.5, 'A4', .5), (2, 'Bb4', 1), (3, 'A4', .5), (3.5, 'G4', .5)]),
         ('D7', [(0, 'F#4', 1), (1, 'A4', 1), (2, 'D5', 1.5), (3.5, 'C5', .5)]),
         ('Cm', [(0, 'Bb4', .5), (.5, 'A4', .5), (1, 'G4', 1), (2, 'Eb5', 1), (3, 'D5', .5), (3.5, 'C5', .5)]),
         ('D7', [(0, 'D5', 1), (1, 'A4', .5), (1.5, 'F#4', .5), (2, 'G4', 2)]),
         ('Eb', [(0, 'G4', 1), (1, 'Bb4', 1), (2, 'Eb5', 1), (3, 'D5', 1)]),
         ('Cm', [(0, 'C5', 1.5), (1.5, 'Bb4', .5), (2, 'G4', 1), (3, 'Eb4', 1)]),
         ('D7', [(0, 'D4', .5), (.5, 'F#4', .5), (1, 'A4', .5), (1.5, 'C5', .5), (2, 'D5', 1), (3, 'C5', .5),
                 (3.5, 'A4', .5)]),
         ('Gm', [(0, 'G4', 1), (1, 'D4', 1), (2, 'G4', 2)])]
WALTZ = ['Gm', 'Gm', 'Cm', 'D7', 'Gm', 'Eb', 'Cm', 'D7', 'D7', 'D7']
WALTZ_TUNE = [(1, 'D4', 1), (2, 'G4', 1), (3, 'Bb4', 2), (5, 'A4', 1), (6, 'C5', 2), (8, 'Bb4', 1),
              (9, 'A4', 1.5), (10.5, 'G4', .5), (11, 'F#4', 1), (12, 'G4', 2), (14, 'D4', 1),
              (15, 'G4', 1), (16, 'Bb4', 1), (17, 'Eb5', 1), (18, 'D5', 3), (21, 'C5', 1), (22, 'A4', 2),
              (24, 'F#4', 2), (27, 'D4', 2.5)]


def _fft_shape(x, lo, hi, order=2):
    """Band-limit a mono signal with smooth Butterworth-like edges (FFT; lo/hi in Hz, None for open)."""
    from pixelhome.audio import SR
    X = np.fft.rfft(x)
    f = np.fft.rfftfreq(len(x), 1 / SR) + 1e-6
    g = np.ones_like(f)
    if lo:
        g /= np.sqrt(1 + (lo / f) ** (2 * order))
    if hi:
        g /= np.sqrt(1 + (f / hi) ** (2 * order))
    return np.fft.irfft(X * g, len(x))


def _st(x):
    return np.vstack([x, x])


def score(M, G):
    from pixelhome.audio import SR, note, slide, whoosh
    n = note
    P = _plan(G)
    L, C = P['L'], P['C']
    rng = np.random.default_rng(3)

    # ---- instruments ----
    bsn = M.sampler('Woodwinds/Bassoon/stac/*.wav', tune=-12)
    cbp = M.sampler('Strings/Solo Contrabass/Pizz/*.wav', tune=-12)
    cbt = M.sampler('Strings/Solo Contrabass/Trem/*.wav', tune=-12)
    vcs = M.sampler('Strings/Cello Section/spic/*.wav', tune=-12)
    vcl = M.sampler('Strings/Cello Section/susvib/*.wav', tune=-12)
    vas = M.sampler('Strings/Viola Section/spic/*.wav', tune=-12)
    vap = M.sampler('Strings/Viola Section/pizz/*.wav', tune=-12)
    clar = M.sampler('Woodwinds/Clarinet/susLong/*.wav', tune=-12)
    oboe = M.sampler('Woodwinds/Oboe/Stacc/*.wav', tune=-12)
    horn = M.sampler('Brass/F Horn/sus/*.wav', tune=-12)
    harp = M.sampler('Strings/Harp/*.wav')
    mar = M.sampler('Percussion/Marimba/*.wav', tune=-12)
    taps = M.hits('Percussion/Snare2-taps*.wav')
    snare = M.hits('VSCO 1 Percussion/drums/snare/drum2/snare2_p_*.wav')
    bd = M.hits('Percussion/BDrumNewhit_v[3-5]*.wav')
    timp = M.hits('Percussion/Timpani/Timpani1_Hit*.wav')
    troll = M.hits('Percussion/Timpani/Rolls/*.wav')
    swell = M.hits('Percussion/susCymb1-cresc-Short*.wav')
    crash = M.hits('Percussion/cymbal-crash1_mp*.wav')
    gong = M.hits('Percussion/gongscrape_pp*.wav')
    clank = M.hits('Miscellania Raw/Misc 1/metal_hit*.wav')

    for name, gain, rev in (('chuff', 0.42, 0.08), ('brush', 0.9, 0.1), ('bass', 0.24, 0.08), ('strings', 0.32, 0.15),
                            ('organ', 0.3, 0.4), ('calliope', 1.2, 0.25), ('clar', 0.3, 0.3), ('harp', 0.38, 0.3),
                            ('brass', 0.17, 0.3), ('bell', 0.28, 0.35), ('whistle', 0.3, 0.3), ('fx', 0.26, 0.25),
                            ('drums', 0.42, 0.18)):
        M.bus(name, gain=0.7 * gain, reverb=rev)

    order = np.argsort(G.pd)
    xs, ds = G.pos[order, 0], G.pd[order]
    x0, x1 = xs.min(), xs.max()

    def pan_at(d):                          # path distance -> left/right across the facade, from the street
        x = np.interp(np.clip(d, 0, L), ds, xs)
        return float(0.85 * (2 * (x - x0) / (x1 - x0) - 1))

    def where(sv):                          # a train position s - u -> house position (beyond the ends: the ends)
        return ((sv + OFF) % C) - OFF if sv >= S_STOP else sv

    # ---- synthesised sounds ----
    def chuff(amp, tone):
        m = int(0.24 * SR)
        t = np.arange(m) / SR
        x = _fft_shape(rng.normal(0, 1, m), 110, 500 + 1500 * tone)
        env = np.clip(t / 0.004, 0, 1) * (np.exp(-t / 0.045) + 0.35 * np.exp(-t / 0.13))
        x = x * env
        return _st(amp * x / (np.abs(x).max() + 1e-9))

    def hiss(dur, amp):
        m = int(dur * SR)
        t = np.arange(m) / SR
        x = _fft_shape(rng.normal(0, 1, m), 900, 5000)
        env = np.clip(t / 0.05, 0, 1) * np.exp(-t / (0.35 * dur))
        return _st(amp * env * x / (np.abs(x).max() + 1e-9))

    def whistle(dur, notes, amp, far=0.0, dop=None):
        """A chime steam whistle: a chord of hollow pipes with breath, a scoop up at the start and a sag at the end.
        far: 0 near .. 1 distant (duller, quieter). dop: (t0, ratio) the pitch falls by ratio after t0."""
        m = int((dur + 0.2) * SR)
        t = np.arange(m) / SR
        bend = 1 - 0.05 * np.exp(-t / 0.07) - 0.035 * smoothstep(dur - 0.12, dur + 0.1, t)
        bend *= 1 + 0.003 * np.sin(2 * np.pi * 5.3 * t)
        if dop:
            bend *= 1 - (1 - dop[1]) * smoothstep(dop[0] - 0.25, dop[0] + 0.25, t)
        x = np.zeros(m)
        for k, nm in enumerate(notes):
            f = 440 * 2 ** ((n(nm) - 69) / 12) * (1 + 0.002 * (k - 1))
            ph = 2 * np.pi * np.cumsum(f * bend) / SR
            x += np.sin(ph) + 0.3 * np.sin(2 * ph) + 0.12 * np.sin(3 * ph)
        x += 0.5 * _fft_shape(rng.normal(0, 1, m), 250, 1500) * (1 + 0.5 * np.sin(2 * np.pi * 9 * t))
        env = np.clip(t / 0.05, 0, 1) * np.clip((dur + 0.15 - t) / 0.18, 0, 1)
        x *= env
        if far:
            x = _fft_shape(x, None, 2200 - 1600 * far)
        return _st(amp * (1 - 0.65 * far) * x / (np.abs(x).max() + 1e-9))

    def bell(nm, amp, dur=2.6):
        m = int(dur * SR)
        t = np.arange(m) / SR
        f0 = 440 * 2 ** ((n(nm) - 69) / 12)
        x = np.zeros(m)
        for r, a, d in ((0.5, 0.45, 1.8), (1, 1.0, 1.3), (1.2, 0.5, 0.9), (1.5, 0.3, 0.7), (2.0, 0.35, 0.6),
                        (2.52, 0.12, 0.4), (3.0, 0.06, 0.25)):
            x += a * np.sin(2 * np.pi * f0 * r * t + r) * np.exp(-t / d)
        x += 0.4 * _fft_shape(rng.normal(0, 1, m), 600, 3000) * np.exp(-t / 0.006)
        return _st(amp * x / (np.abs(x).max() + 1e-9))

    def squeal(dur, amp):
        m = int(dur * SR)
        t = np.arange(m) / SR
        f = 660 * (1 - 0.08 * t / dur)
        ph = 2 * np.pi * np.cumsum(f) / SR
        x = (np.sin(ph) + 0.4 * np.sin(1.5 * ph)) * (0.6 + 0.4 * np.sin(2 * np.pi * 7 * t)) ** 2
        env = smoothstep(0, 0.5, t) * (1 - smoothstep(dur - 0.6, dur, t))
        return _st(amp * env * x)

    organ, calliope = [], []
    ch, ch_s = P['chuffs'], P['chuff_s']
    T_TUN, T_GONE, T_SCOOP = P['T_TUN'], P['T_GONE'], P['T_SCOOP']
    entries = P['entries']

    def lap(t):
        return int(np.searchsorted(entries, t, side='right'))

    def tone(c, i, lo):                     # i-th chord tone at or above lo
        pcs = [m % 12 for m in CH[c]]
        return [m for m in range(lo, lo + 60) if m % 12 in pcs][i]

    # ---- every chuff: steam, brush, a cello stroke ----
    for i, (tc, sc) in enumerate(zip(ch, ch_s)):
        sv = sc - STACK
        if tc < TE:
            g = 1 / (1 + max(-sv, 0) / 380)
        else:
            g = 1.0
        if tc >= T_TUN:
            g *= 1 - smoothstep(T_TUN, T_GONE + 0.4, tc)
        rate = 1 / max(ch[i + 1] - tc, 1e-3) if i + 1 < len(ch) else 10
        heavy = 1.0 + 0.6 * (TD <= tc < TD + 6)           # pulling away: big slow chuffs
        p = pan_at(where(sv)) if sv > 0 else -0.85
        tn = min(1.0, 0.25 + 0.06 * rate) * (0.5 + 0.5 * g)
        M.add('chuff', chuff(0.8 * g * heavy * (1 - 0.35 * min(rate / 12, 1)), tn), tc, 1.0, p)
        M.add('brush', taps.play(int(55 + 25 * (i % 2 == 0))), tc + 0.01, 0.8 * g, p * 0.6)

    # ---- 0-9: fog; far off behind the house, a whistle, another, and the chuffs getting closer ----
    organ += [(0.3, n('G2'), 44, 8.6), (0.3, n('D3'), 40, 8.6), (3.5, n('Bb3'), 34, 5.4)]
    M.add('strings', vcl.play(n('G2'), 70, dur=8.5, release=0.8), 0.4, 0.8, -0.3)
    M.add('strings', vcl.play(n('D3'), 60, dur=4.5, release=0.8), 4.2, 0.7, -0.2)
    M.add('strings', cbt.play(n('G1'), 64, dur=8.5, release=0.6), 0.6, 0.6, -0.5)
    M.add('fx', whoosh(9.0, 90, 380, 0.5, seed=11), 0.0, 0.5, -0.4)

    WH = {'far': (['D4', 'G4', 'Bb4'], 0.6, 0.95), 'near': (['D4', 'G4', 'Bb4'], 0.8, 0.6),
          'in': (['D4', 'G4', 'Bb4'], 1.0, 0.0), 'toot': (['D4', 'G4', 'Bb4'], 0.8, 0.0),
          'aboard': (['D4', 'G4', 'Bb4'], 1.0, 0.0), 'lap': (['D4', 'G4', 'Bb4'], 0.8, 0.0),
          'scoop': (['D4', 'G4', 'B4'], 1.0, 0.0), 'tunnel': (['D4', 'G4', 'Bb4'], 1.0, 0.0)}
    for w0, d0, kind in P['whistles']:
        nts, amp, far = WH[kind]
        s0 = float(nose(w0 + 0.1))
        p = -0.85 if s0 < 0 else pan_at(where(s0))
        if kind == 'lap':
            p = -0.85                        # it comes back in at the far end of Side
        dop = (d0 * 0.5, 0.93) if kind in ('tunnel', 'scoop') else None
        M.add('whistle', whistle(d0, nts, amp, far, dop), w0, 1.0, p)
    M.add('fx', whoosh(2.8, 1200, 200, 0.5, seed=12), T_TUN - 0.4, 0.6, 0.85)

    # ---- 9-18.7: the train comes in; the tune on low clarinet, slowing with the chuffs into the station ----
    def bars(i0, steps, nbars, end=None):
        """Bars of 4 beats on the chuff grid from chuff i0; steps(rate) -> chuffs per beat (fixed per bar)."""
        out, i = [], i0
        for _ in range(nbars):
            if i + 1 >= len(ch):
                break
            k = steps(1 / (ch[i + 1] - ch[i]))
            idx = [i + k * b for b in range(5)]
            bt = [ch[j] if j < len(ch) else None for j in idx]
            if bt[4] is None or (end is not None and bt[4] > end):
                if end is None:
                    break
                bt = [b if b is not None and b <= end else end for b in bt]
            out.append(bt)
            i += 4 * k
        return out

    def at(bar, pos):
        b = int(pos)
        return bar[b] + (pos - b) * (bar[min(b + 1, 4)] - bar[b])

    i0 = int(np.nonzero(ch_s >= 0)[0][0])
    arr = bars(i0, lambda r: 2, 3, end=TS)
    for bi, bar in enumerate(arr):
        c = ['Gm', 'D7', 'Gm'][bi]
        for b in range(4):
            r = ROOT[c] + (0 if b % 2 == 0 else 7)
            M.add('bass', bsn.play(r, 92), bar[b], 0.9)
            M.add('bass', cbp.play(r, 96), bar[b], 0.8)
        organ.append((bar[0], ROOT[c] + 12, 50, bar[4] - bar[0]))
        for m in CH[c]:
            organ.append((bar[0], m - 12, 44, bar[4] - bar[0]))
        if bi < 2:
            for pos, nm, du in THEME[bi][1]:
                M.add('clar', clar.play(n(nm), 96, dur=(at(bar, pos + du) - at(bar, pos)) * 0.95), at(bar, pos), 1.0, 0.1)
    M.add('clar', clar.play(n('G4'), 90, dur=TS + 0.6 - arr[2][0]), arr[2][0], 1.0, 0.1)
    for j in i0 + np.arange(0, 2 * 4 * len(arr), 1):
        if j < len(ch) and ch[j] <= TS:
            c = ['Gm', 'D7', 'Gm'][min(2, (j - i0) // 8)]
            M.add('strings', vcs.play(ROOT[c] + 12 + 7 * ((j - i0) % 2), 80), ch[j], 0.7, pan_at(ch_s[j] - STACK))
    M.add('fx', squeal(TS - TB - 0.6, 0.16), TB + 0.6, 1.0, pan_at(S_STOP - 500))
    M.add('fx', hiss(2.6, 0.5), TS - 0.1, 1.0, pan_at(S_STOP - STACK))

    # ---- 19-34: the station, a waltz on the hop beat ----
    def wchord(t):
        return WALTZ[min(len(WALTZ) - 1, max(0, int((t - T_ST) // (3 * BEAT))))]

    for k in range(30):
        t, c = sb(k), WALTZ[k // 3]
        if k % 3 == 0:
            M.add('bass', cbp.play(ROOT[c] + (12 if ROOT[c] < 40 else 0), 98), t, 0.9)
            organ.append((t, ROOT[c] + 12, 46, 3 * BEAT))
        else:
            for m in CH[c][:3]:
                M.add('strings', vap.play(m, 70), t, 0.45, -0.3)
    for pos, nm, du in WALTZ_TUNE:
        M.add('clar', clar.play(n(nm), 92, dur=du * BEAT * 0.95, release=0.2), sb(pos), 1.0, 0.15)
    for gh in P['ghosts']:                  # every landing a harp note, down for those going home, up for those boarding
        for j, (ts, xa, xb) in enumerate(gh['hops']):
            tl = ts + HOP
            c = wchord(tl)
            if gh['off']:
                m = tone(c, max(0, 5 - j), n('G3'))
                g = 1 - smoothstep(gh['fade'][0], gh['fade'][1], tl)
            else:
                m = tone(c, 2 + min(j, 4), n('G3'))
                g = 1.0
            if g > 0.02:
                M.add('harp', harp.play(m, 84), tl, 0.8 * g, pan_at(xb))
    for k, st in enumerate(P['seat_t']):
        if np.isfinite(st) and st > 0:
            c = wchord(st)
            x = S_STOP - P['wins'][k]
            M.add('harp', mar.play(tone(c, 0, n('G4')), 96), st, 0.9, pan_at(x))
            M.add('harp', mar.play(tone(c, 2, n('G4')), 80), st + 0.06, 0.6, pan_at(x))
    for ts, xa, xb in P['cond']:            # the conductor's heavy little hops
        M.add('bass', bsn.play(n('D3') if xb > xa else n('G2'), 100), ts + HOP, 0.9, pan_at(xb))
    for bt in BELL:
        M.add('bell', bell('G4', 0.9), bt, 1.0, pan_at(P['cond'][1][2]))
    M.add('fx', hiss(1.6, 0.3), WHISTLE_ALL[0][0], 0.6, pan_at(S_STOP - STACK))

    # ---- 34-: pulling out. Couplings clank down the train, then the slow heavy chuffs ----
    M.add('fx', hiss(2.4, 0.55), TD - 0.3, 1.0, pan_at(S_STOP - STACK))
    for c in range(NCAR + 2):
        u = TENDER[1] + c * (CARL + CARG) if c < NCAR + 1 else CAB0
        M.add('fx', clank.play(90 - 6 * c, pitch=-7), TD + JOLT * (c + 1), 0.55, pan_at(S_STOP - u))
    M.add('drums', troll.play(60, dur=4.5), TD + 0.4, 0.5)
    dep0 = int(np.nonzero(ch >= TD)[0][0])
    for j in range(dep0, len(ch)):
        if ch[j] > TD + 5.2:
            break
        M.add('bass', cbp.play(n('G1'), 110), ch[j], 1.0)
        M.add('bass', bsn.play(n('G2'), 100), ch[j], 0.8)
        M.add('drums', timp.play(80, pitch=-2), ch[j], 0.5)
        M.add('strings', vcs.play(n('G2'), 110), ch[j], 0.8)
        M.add('strings', vcs.play(n('D3'), 100), ch[j], 0.6)
    organ += [(TD, n('G2'), 54, 5.0), (TD, n('D3'), 50, 5.0), (TD + 1.5, n('Bb3'), 46, 3.5)]

    # ---- laps: the tune on the chuff grid, a part added every lap ----
    j0 = int(np.nonzero(ch >= TD + 5.0)[0][0])
    deps = bars(j0, lambda r: 1 if r < 2.6 else (2 if r < 5.2 else 4), 60)
    deps = [b for b in deps if b[0] < T_TUN]
    for bi, bar in enumerate(deps):
        t0 = bar[0]
        lp = lap(t0)
        ride = T_SCOOP is not None and t0 >= T_SCOOP - 0.2
        c, mel = THEME[bi % 8]
        if ride:
            c = MAJOR[c]
        blen = bar[4] - bar[0]
        organ.append((t0, ROOT[c] + 12, 52, blen))
        for m in CH[c]:
            organ.append((t0, m - 12 * (m > 57), 46, blen))
        for b in range(4):
            if bar[b] >= T_GONE:
                break
            r = ROOT[c] + (0 if b % 2 == 0 else 7)
            M.add('bass', bsn.play(r, 96), bar[b], 0.9)
            M.add('bass', cbp.play(r, 100), bar[b], 0.9)
            if lp >= 2 and b in (1, 3):
                M.add('drums', snare.play(78), bar[b], 0.55)
            if lp >= 3 and b in (0, 2):
                M.add('drums', bd.play(95), bar[b], 0.6)
            if lp >= 3:                     # violas on the off-beats
                for m in CH[c][:3]:
                    M.add('strings', vas.play(m, 74), at(bar, b + 0.5), 0.4, 0.35)
        # cellos chug on the chuffs inside the bar (every other one when they blur)
        cj = [j for j in range(len(ch)) if bar[0] <= ch[j] < min(bar[4], T_GONE)]
        for q, j in enumerate(cj):
            rate = 1 / max(ch[min(j + 1, len(ch) - 1)] - ch[j], 1e-3)
            if rate > 7.5 and q % 2:
                continue
            M.add('strings', vcs.play(ROOT[c] + 12 + 7 * (q % 2), 84), ch[j], 0.6, -0.2)
        if lp >= 1:
            for pos, nm, du in mel:
                m = n(nm)
                if ride and m % 12 in (10, 3):   # Bb -> B, Eb -> E: major for the ride home
                    m += 1
                tn = at(bar, pos)
                if tn < T_GONE:             # into the fog: the calliope goes with it
                    calliope.append((tn, m, int(100 - 45 * smoothstep(T_TUN, T_GONE, tn)),
                                     max(0.08, (at(bar, pos + du) - tn) * 0.9)))
        if lp >= 2:                         # horns hold the chord's third and fifth underneath
            for m in CH[c][1:3]:
                M.add('brass', horn.play(m - 12 * (m > 60), 78, dur=blen * 0.95, release=0.25), t0, 0.55, 0.0)
        if ride:
            for pos, nm, du in mel:
                m = n(nm) - 12
                if m % 12 in (10, 3):
                    m += 1
                if at(bar, pos) >= T_GONE:
                    continue
                M.add('brass', horn.play(m, 96, dur=(at(bar, pos + du) - at(bar, pos)) * 0.9), at(bar, pos), 0.7)

    # the train passes out of the right end every lap: a rush
    for te in P['exits'][:-1]:
        M.add('fx', whoosh(0.9, 300, 1400, 0.35, seed=int(te * 10)), te - 0.55, 0.5, 0.85)

    # ---- the late ghost: "wait for me!" on oboe each time he sets off; whee and a bump each time he's bowled ----
    for k, tr in enumerate(P['runs']):
        x = P['wisp'][min(int(tr / DT) + 2, len(P['wisp']) - 1)]
        for q, (dt, nm) in enumerate(((0, 'G4'), (0.16, 'A4'), (0.32, 'Bb4'))):
            M.add('clar', oboe.play(n(nm) + min(k, 3), 100), tr + dt, 0.85, pan_at(x))
    for tb_, (tl, xl) in zip(P['bumps'], P['lands']):
        xb = P['wisp'][int(tb_ / DT)]
        M.add('fx', slide(0.0, 0.25, 500, 1150, tl - tb_ + 0.05, 0.5), tb_, 0.7, pan_at(xb))
        M.add('drums', bd.play(70), tl, 0.4, pan_at(xl))
        M.add('harp', mar.play(n('D3'), 90), tl, 0.6, pan_at(xl))
    if T_SCOOP:
        M.add('drums', swell.play(80), T_SCOOP - 1.6, 0.6, pan_at(P['wisp'][int(T_SCOOP / DT)]))
        M.add('drums', crash.play(90), T_SCOOP, 0.6, pan_at(P['wisp'][int(T_SCOOP / DT)]))
        for q, m in enumerate(('G3', 'B3', 'D4', 'G4', 'B4', 'D5')):
            M.add('harp', harp.play(n(m), 96), T_SCOOP + 0.05 * q, 0.8, pan_at(P['wisp'][int(T_SCOOP / DT)]))

    # ---- the tunnel: a roll into it, the whistle bending away into the fog, and it is gone ----
    M.add('drums', troll.play(80, dur=T_GONE - T_TUN + 2.6), T_TUN - 2.2, 0.6, 0.6)
    M.add('fx', gong.play(80), T_TUN - 0.5, 0.6, 0.85)
    M.add('drums', bd.play(110), T_GONE, 0.8, 0.85)
    M.add('drums', timp.play(110), T_GONE, 0.7, 0.85)
    M.add('bass', cbp.play(n('G1'), 120), T_GONE, 1.0)
    for m in ('G2', 'D3', 'G3', 'B3'):
        M.add('strings', vcl.play(n(m), 70, dur=6.5, release=1.5), T_GONE + 0.3, 0.5, 0.4)
    organ += [(T_GONE + 0.3, n('G2'), 46, 7.0), (T_GONE + 0.3, n('D3'), 42, 7.0), (T_GONE + 0.3, n('B3'), 38, 7.0)]
    for tw in (T_GONE + 4.2, T_GONE + 4.75):        # goodbye, from somewhere inside the fog
        M.add('whistle', whistle(0.28, ['D4', 'G4', 'B4'], 0.6, 0.9), tw, 1.0, 0.85)
    for j, (to, x) in enumerate(zip(LAMP_OUT, LAMPS)):
        M.add('harp', harp.play(n(['G2', 'B2', 'D3'][j]), 80), to, 0.7, pan_at(x))
    M.add('harp', harp.play(n('G2'), 70), LAMP_OUT[0] + 0.8, 0.6, 0.0)

    M.add('organ', M.synth('Keys/House Organ').render(organ, D), 0.0)
    M.add('calliope', M.synth('Keys/Circus 2').render(calliope, D), 0.0)
