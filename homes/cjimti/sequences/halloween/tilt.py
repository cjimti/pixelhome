"""Tilt: the house is a haunted pinball table. Street side is the bottom of the table and the back of
the house is the top, so balls slow down climbing the porch rails and the Side and speed up coming
back toward the street. Attract-mode lights chase out from the porch until a coin drops. The free end
of Right is the plunger lane: a spring pulls back and fires a glowing jack-o'-lantern ball up the
right wing and the porch rail. The three corners nearest the porch top and the house's front-left
corner are pop bumpers, each with its own look and sound (A, Side|Left: red double rings; C, back-
left of the porch: green sparkle spinner; D, back-right of the porch: violet ripples); the two front
porch corners are the flippers, whose bats lie along the porch rails and catch, cradle and fire the
ball back up. The Porch Front is the target bank (four drop targets) with a saucer in the middle;
every other run is a lane of rollover lamps that chase ahead of a passing ball and stay lit once
collected. The free back end of Side is the drain: balls kicked up there slow, nearly fall in and
roll back. The saucer locks the first ball, two more come off the plunger for multiball (an eyeball
and a ghost ball), the house fills with light as the score climbs, and the saucer pays a jackpot.
Then the player shakes the table: one nudge, a red warning, a big shove, TILT. Everything dies dead
with a buzz. In the dark one ball wakes up, tiptoes to the drain and drops out on its own; the
machine knocks for a free game and the attract lights come back.

All the motion is in path distance, so a ball has the same size and speed rules on every run. The
balls are simulated: constant rolling friction plus the table's tilt (height is distance from the
street), kicks from bumpers and flippers, with the decisions drawn from the seed. _plan() is shared
by render() and score(), so every hit lands where and when the light does."""
import heapq

import numpy as np
from pixelhome.fx import DT, hexc, light, smoothstep, nframes

CODE = 'HW16'
TITLE = 'Tilt'
KIND = 'show'
DESCRIPTION = ('The house is a haunted pinball table: bumpers on the corners, flippers on the porch, a jack-o\'-lantern '
               'ball off the plunger, then multiball and a jackpot, until somebody shakes it too hard.')
VOICEOVER = ("Insert one coin, and the whole house is a pinball machine. Bumpers, flippers, three balls at once... "
             "just don't shake it.")

# ---- colours (PWM) ----
PLAY = hexc('#3a10b0')        # playfield GI
RED = hexc('#ff1a10')
GREEN = hexc('#38ff20')
VIOLET = hexc('#9a30ff')
ORANGE = hexc('#ff6a00')
AMBER = hexc('#ffa020')
GOLD = hexc('#ffc838')
WARM = hexc('#fff0c8')
WHITE = hexc('#ffffff')
LIME = hexc('#90ff30')
CYAN = hexc('#30d8ff')
STEEL = hexc('#b8d0ff')
EYE = hexc('#ff2050')
GHOST = hexc('#70ffb0')
PUMPKIN_CORE = hexc('#ffe070')

BEAT = 0.4                    # 150 BPM
BAR = 4 * BEAT
T_START = 9.6                 # coin in
T_PULL = 10.4                 # the plunger pulls back for a bar
T_LAUNCH = 12.0
T_LOCK_LIT = 24.0             # the saucer lights for a lock
GRAV = 420.0                  # table tilt (units/s^2 per unit of rise)
FRIC = 55.0                   # rolling friction (units/s^2)

RUN_COL = {'Side': RED, 'Left': ORANGE, 'Porch Left': AMBER, 'Porch Right': AMBER, 'Right': ORANGE}
BUMPERS = {'A': RED, 'C': GREEN, 'D': VIOLET}
SCORE_PTS = dict(collect=10, reroll=2, bump=100, target=250, bank=1000, lane=500, lock=1500, jackpot=5000)


class _Ball:
    """A ball's motion as legs of constant acceleration along the path: (t0, dur, s0, dir, v0, a)."""

    def __init__(self, geo, t, s, who):
        self.g, self.t, self.s, self.who = geo, t, s, who
        self.legs, self.events = [], []
        self.node, self.came, self.v = None, None, 0.0

    def mark(self, kind, **kw):
        self.events.append(dict(t=self.t, kind=kind, s=self.s, ball=self.who, **kw))

    def _leg(self, dur, s0, d, v0, a):
        if dur > 0:
            self.legs.append((self.t, dur, s0, d, v0, a))
            self.t += dur

    def hold(self, dur):
        self._leg(dur, self.s, 1.0, 0.0, 0.0)

    def lin(self, s_to, dur):
        L = s_to - self.s
        self._leg(dur, self.s, 1.0 if L >= 0 else -1.0, abs(L) / dur, 0.0)
        self.s = s_to

    def _piece(self, s_to, v0):
        L = abs(s_to - self.s)
        if L < 1e-6:
            return v0
        d = 1.0 if s_to > self.s else -1.0
        a = -GRAV * (self.g['h'](s_to) - self.g['h'](self.s)) / L - FRIC
        v1sq = v0 * v0 + 2 * a * L
        if v1sq <= 400:
            raise ValueError(f'ball {self.who} cannot reach {s_to:.0f} from {self.s:.0f} at {v0:.0f}')
        v1 = float(np.sqrt(v1sq))
        self._leg(2 * L / (v0 + v1), self.s, d, v0, a)
        self.s = s_to
        return v1

    def go(self, s_to, v0):
        """Roll to s_to starting at speed v0 (splitting at corners where the slope changes); returns arrival speed."""
        lo, hi = sorted((self.s, s_to))
        cuts = [b for b in self.g['brk'] if lo + 1e-6 < b < hi - 1e-6]
        if s_to < self.s:
            cuts = cuts[::-1]
        v = v0
        for c in cuts + [s_to]:
            v = self._piece(c, v)
        return v

    def apex(self, s_lim, v0):
        """Kicked uphill toward s_lim: slows, stops short, rolls back to where it started. Returns the speed back."""
        s_from = self.s
        d = 1.0 if s_lim > s_from else -1.0
        slope = (self.g['h'](s_lim) - self.g['h'](s_from)) / abs(s_lim - s_from)
        a_up = -GRAV * slope - FRIC
        L = v0 * v0 / (-2 * a_up)
        assert L < abs(s_lim - s_from), 'apex would pass the limit'
        self._leg(v0 / -a_up, s_from, d, v0, a_up)
        self.s = s_from + d * L
        self.mark('apex')
        a_dn = GRAV * slope - FRIC
        vb = float(np.sqrt(2 * a_dn * L))
        self._leg(2 * L / vb, self.s, -d, 0.0, a_dn)
        self.s = s_from
        return vb

    def cut(self, T):
        keep = []
        for lg in self.legs:
            t0, dur = lg[0], lg[1]
            if t0 >= T:
                break
            keep.append(lg if t0 + dur <= T else (t0, T - t0) + lg[2:])
        self.legs = keep
        self.events = [e for e in self.events if e['t'] < T]

    def sample(self, tf):
        S = np.full(len(tf), np.nan)
        for t0, dur, s0, d, v0, a in self.legs:
            i0, i1 = np.searchsorted(tf, [t0, t0 + dur])
            if i1 > i0:
                tau = tf[i0:i1] - t0
                S[i0:i1] = s0 + d * (v0 * tau + 0.5 * a * tau * tau)
        return S


def _geo(G):
    ppd = G.pd[G.path]
    zz = G.pos[G.path, 2]
    cp = {'A': (80, 81), 'B': (178, 179), 'C': (260, 261), 'D': (331, 332), 'E': (380, 381)}
    P = {k: float((ppd[a] + ppd[b]) / 2) for k, (a, b) in cp.items()}
    END = float(ppd[-1])
    P['END'] = END - 34.0                                  # the plunger tip at rest
    brk = [P[k] for k in 'ABCDE']
    return dict(P=P, END=END, brk=brk, h=lambda s: float(np.interp(s, ppd, -zz)),
                PFC=(P['C'] + P['D']) / 2, ppd=ppd)


class _State:
    def __init__(self, geo):
        self.geo = geo
        P = geo['P']
        self.tpos = [P['C'] + f * (P['D'] - P['C']) for f in (0.17, 0.33, 0.67, 0.83)]
        self.tdown = [None] * 4                            # time each target dropped (None: up)
        self.reset_at = None
        self.lock_ball, self.locked = None, False
        self.jp_lit, self.jp_done = 1e9, False
        self.side_last = -1e9

    def target_up(self, i, t):
        if self.reset_at is not None and t >= self.reset_at:
            self.tdown, self.reset_at = [None] * 4, None
        return self.tdown[i] is None


def _flipper(b, st, rng, X, up, pas, catch_p=0.3, pass_p=0.15):
    """Ball at flipper corner X. `up` is the rail's far corner, `pas` the wing it can roll out onto."""
    P = b.g['P']
    downhill = b.came == up
    r = rng.random()
    if downhill and r < pass_p:                            # misses the flipper and rolls out onto the wing
        b.mark('pass', node=X)
        return pas, max(420.0, b.v * 0.85)
    side = 1.0 if P[up] > P[X] else -1.0
    if downhill and r < pass_p + catch_p:                  # caught and cradled on the bat
        b.mark('catch', node=X)
        b.lin(P[X] + side * 15, 0.09)
        b.lin(P[X] + side * 7, 0.12)
        b.hold(float(rng.uniform(0.35, 0.8)))
    b.mark('flip', node=X)
    return up, float(rng.uniform(800, 900))


def _advance(b, st, rng):
    P = b.g['P']
    X = b.node
    if X == 'A':
        b.mark('bump', node='A')
        if b.came != 'SIDE' and rng.random() < 0.6 and b.t - st.side_last > 2.0:
            st.side_last = b.t                             # kicked up the Side toward the drain: nearly
            b.v = b.apex(0.0, float(rng.uniform(570, 650)))
            b.came = 'SIDE'
            return
        nxt, v0 = 'B', float(rng.uniform(650, 820))
    elif X == 'B':
        nxt, v0 = _flipper(b, st, rng, 'B', 'C', 'A', catch_p=0.25, pass_p=0.35)
    elif X == 'E':
        nxt, v0 = _flipper(b, st, rng, 'E', 'D', 'END')
    elif X == 'END':
        b.mark('kick', node='END')
        nxt, v0 = 'E', float(rng.uniform(600, 740))
    elif X == 'C':
        b.mark('bump', node='C')
        pf = rng.random() < (0.72 if b.came == 'B' else 0.45)
        nxt, v0 = ('D', float(rng.uniform(650, 820))) if pf else ('B', float(rng.uniform(420, 620)))
    else:                                                  # D
        b.mark('bump', node='D')
        pf = rng.random() < (0.72 if b.came == 'E' else 0.45)
        nxt, v0 = ('C', float(rng.uniform(650, 820))) if pf else ('E', float(rng.uniform(420, 620)))

    if {X, nxt} == {'C', 'D'}:                             # along the Porch Front: saucer, targets, jackpot
        d = 1.0 if P[nxt] > P[X] else -1.0
        c = b.g['PFC']
        if st.lock_ball is b and b.t >= T_LOCK_LIT and not st.locked:
            v = b.go(c, v0)
            b.lin(c + d * 6, 0.07)
            b.lin(c, 0.1)
            b.mark('lock')
            st.locked = True
            b.node = 'SAUCER'
            return
        ahead = sorted([i for i in range(4) if (st.tpos[i] - b.s) * d > 0], key=lambda i: (st.tpos[i] - b.s) * d)
        up = [i for i in ahead if st.target_up(i, b.t)]
        if up and rng.random() < 0.4:
            i = up[0]
            v = b.go(st.tpos[i] - d * 5, v0)
            b.mark('target', i=i)
            st.tdown[i] = b.t
            if all(x is not None for x in st.tdown):
                b.mark('bank')
                st.reset_at = b.t + 1.6
            b.v = b.go(P[X], 0.8 * v)
            b.came = nxt
            return
        if b.t >= st.jp_lit and not st.jp_done:
            v = b.go(c, v0)
            b.mark('jackpot')
            st.jp_done = True
            b.v = b.go(P[nxt], v)
        else:
            b.v = b.go(P[nxt], v0)
    else:
        b.v = b.go(P[nxt], v0)
    b.came, b.node = X, nxt


def _launch(b, t_pull, t_rel, P, END):
    """Sit at the plunger tip, get pulled back, fire up the right wing and the porch rail to bumper D."""
    b.hold(t_pull - b.t)
    b.lin(END - 14, t_rel - t_pull)
    b.mark('launch', node='END')
    b.lin(END - 34, 0.025)
    v = b.go(P['E'], 900.0)
    b.v = b.go(P['D'], v)
    b.node, b.came = 'D', 'E'


def _grid(t, t0, step):
    return t0 + step * np.ceil((t - t0) / step - 1e-6)


def _plan(G, seed=18):
    rng = np.random.default_rng(seed)
    geo = _geo(G)
    P, END = geo['P'], geo['END']
    st = _State(geo)

    # ---- ball 1 alone until it locks in the saucer
    b1 = _Ball(geo, T_START, END - 40, 0)
    _launch(b1, T_PULL, T_LAUNCH, P, END)
    st.lock_ball = b1
    while not st.locked:
        _advance(b1, st, rng)
        assert b1.t < 40, 'ball 1 never locked'
    T_LOCK = b1.t

    # ---- multiball: two more off the plunger, then the saucer kicks ball 1 out
    T_P2 = float(_grid(T_LOCK + 2.0, T_LAUNCH, BEAT))
    L2 = T_P2 + 2 * BEAT
    L3 = L2 + 3 * BEAT
    K1 = L3 + 2 * BEAT
    b2 = _Ball(geo, T_LOCK + 0.6, END - 40, 1)
    _launch(b2, T_P2, L2, P, END)
    b3 = _Ball(geo, L2 + 0.1, END - 40, 2)
    _launch(b3, L2 + BEAT, L3, P, END)
    b1.hold(K1 - b1.t)
    b1.mark('kickout')
    b1.v = b1.go(P['C'], 700.0)
    b1.node, b1.came = 'C', 'D'
    st.jp_lit = K1 + 11.0
    balls = [b1, b2, b3]
    heap = [(b.t, b.who) for b in balls]
    heapq.heapify(heap)
    while heap:
        t, w = heapq.heappop(heap)
        if t > K1 + 34:
            continue
        _advance(balls[w], st, rng)
        heapq.heappush(heap, (balls[w].t, w))
    events = sorted([e for b in balls for e in b.events], key=lambda e: e['t'])
    T_JP = next(e['t'] for e in events if e['kind'] == 'jackpot')
    T_TILT = float(_grid(T_JP + 8.0, L2, BEAT))
    for b in balls:
        b.cut(T_TILT)
    events = [e for e in events if e['t'] < T_TILT]
    nudges = [(T_TILT - 6 * BEAT, 2.0), (T_TILT - 3 * BEAT, 3.0), (T_TILT - BEAT, 5.0)]

    D0 = T_TILT + 30.0
    F0 = nframes(D0)
    tf = np.arange(F0) * DT
    S = np.array([b.sample(tf) for b in balls])
    fT = int(np.floor(T_TILT / DT)) - 1

    # ---- rollover lamps on the five lanes; crossings from the sampled motion
    ins_s, ins_run = [], []
    for run, (a, z) in {'Side': (40, P['A']), 'Left': (P['A'], P['B']), 'Porch Left': (P['B'] + 110, P['C']),
                        'Porch Right': (P['D'], P['E'] - 110), 'Right': (P['E'], END - 175)}.items():
        k = max(3, int(round((z - a - 50) / 46)))
        for s in np.linspace(a + 25, z - 25, k):
            ins_s.append(float(s))
            ins_run.append(run)
    ins_s = np.array(ins_s)
    crossings = []                                          # (t, insert, ball, dir)
    for w in range(3):
        a, bq = S[w, :-1], S[w, 1:]
        ok = np.isfinite(a) & np.isfinite(bq)
        for k, p in enumerate(ins_s):
            hit = np.nonzero(ok & ((a - p) * (bq - p) < 0))[0]
            for f in hit:
                crossings.append((tf[f + 1], k, w, float(np.sign(bq[f] - a[f]))))
    crossings.sort()
    collect_t = np.full(len(ins_s), np.inf)
    rolls = []
    for t, k, w, d in crossings:
        first = not np.isfinite(collect_t[k])
        if first:
            collect_t[k] = t
        rolls.append(dict(t=t, k=k, ball=w, dir=d, first=first, s=ins_s[k], run=ins_run[k]))
    lanes = []
    for run in RUN_COL:
        ks = [k for k in range(len(ins_s)) if ins_run[k] == run]
        tc = collect_t[ks].max()
        if np.isfinite(tc):
            lanes.append(dict(t=float(tc), run=run))

    pts = [(e['t'], SCORE_PTS[e['kind']]) for e in events if e['kind'] in SCORE_PTS]
    pts += [(r['t'], SCORE_PTS['collect' if r['first'] else 'reroll']) for r in rolls]
    pts += [(ln['t'], SCORE_PTS['lane']) for ln in lanes]
    pts.sort()
    score_t = np.array([p[0] for p in pts])
    score_c = np.cumsum([p[1] for p in pts])

    # ---- after the tilt: the ball nearest the drain wakes up and tiptoes out
    pos_tilt = S[:, fT]
    sw = int(np.nanargmin(np.where(np.isfinite(pos_tilt), pos_tilt, np.inf)))
    s_from = float(pos_tilt[sw])
    T_WAKE = T_TILT + 3.4
    sn = _Ball(geo, T_WAKE, s_from, sw)
    sn.hold(1.0)                                            # wakes up
    for dx in (9, -9, 0):                                   # looks both ways
        sn.lin(s_from + dx, 0.22)
        sn.hold(0.12)
    hops = []
    dist = s_from - 22.0
    nh = int(np.clip(round(dist / 75), 6, 15))
    for i in range(nh):
        s_to = s_from - dist * (i + 1) / nh
        hops.append((sn.t, s_to))
        sn.lin(s_to, 0.17)
        sn.hold(0.21 if i < nh - 1 else 0.6)
    T_PEEK = sn.t
    sn.lin(30.0, 0.18)                                      # peeks over the edge
    sn.hold(0.25)
    sn.lin(22.0, 0.15)
    sn.hold(0.35)
    T_PLOP = sn.t
    sn.lin(0.0, 0.16)                                       # and drops out
    T_KNOCK = T_PLOP + 1.1
    D = T_KNOCK + 7.4

    return dict(geo=geo, balls=balls, S=S[:, :nframes(D)], events=events, rolls=rolls, lanes=lanes,
                ins_s=ins_s, ins_run=ins_run, collect_t=collect_t, tpos=st.tpos,
                score_t=score_t, score_c=score_c, T_LOCK=T_LOCK, T_P2=T_P2, L2=L2, L3=L3, K1=K1, T_JP=T_JP,
                T_TILT=T_TILT, nudges=nudges, sneak=sn, sneak_ball=sw, hops=hops, T_WAKE=T_WAKE, T_PEEK=T_PEEK,
                T_PLOP=T_PLOP, T_KNOCK=T_KNOCK, D=D,
                plungers=[(T_START, T_PULL, T_LAUNCH), (T_LOCK + 0.6, T_P2, L2), (L2 + 0.1, L2 + BEAT, L3)])


def render(G, seed=18):
    pl = _plan(G, seed)
    geo = pl['geo']
    P, END, PFC = geo['P'], geo['END'], geo['PFC']
    D = pl['D']
    F = nframes(D)
    n = G.N
    pd = G.pd
    out = np.zeros((F, n, 3))
    rng = np.random.default_rng(seed + 100)
    S = pl['S']
    ev = pl['events']
    T_TILT, T_JP, T_LOCK = pl['T_TILT'], pl['T_JP'], pl['T_LOCK']
    score_t, score_c = pl['score_t'], pl['score_c']
    total = score_c[-1]
    ins_s, ins_run, collect_t = pl['ins_s'], pl['ins_run'], pl['collect_t']
    NI = len(ins_s)
    ins_col = np.array([RUN_COL[r] for r in ins_run])
    tpos = pl['tpos']

    def g(s, w):
        return np.exp(-((pd - s) / w) ** 2)

    run_of = G.seg_of
    run_mask = {r: (run_of == r) for r in G.seg}
    dPFC = np.abs(pd - PFC)
    ins_dc = np.abs(ins_s - PFC)
    ins_lamp = np.exp(-((pd[None, :] - ins_s[:, None]) / 5.5) ** 2)           # (NI, n)
    tgt_lamp = np.array([np.exp(-((pd - s) / 6.5) ** 2) for s in tpos])
    corner_d = {k: np.abs(pd - P[k]) for k in 'ABCDE'}
    flip_bar = {'B': np.clip((pd - P['B']) / 110, -1, 2), 'E': np.clip((P['E'] - pd) / 110, -1, 2)}
    shooter = (pd > END - 175) & (pd < END - 40)
    sparkle_seed = rng.uniform(0, 1, n)

    bumps = [(e['t'], e['node']) for e in ev if e['kind'] == 'bump']
    flips = [(e['t'], e['node']) for e in ev if e['kind'] == 'flip']
    catches = [(e['t'], e['node']) for e in ev if e['kind'] == 'catch']
    kicks = [e['t'] for e in ev if e['kind'] == 'kick']
    targets = [(e['t'], e['i']) for e in ev if e['kind'] == 'target']
    banks = [e['t'] for e in ev if e['kind'] == 'bank']
    lanes = pl['lanes']
    rolls = pl['rolls']
    roll_t = np.array([r['t'] for r in rolls])
    roll_k = np.array([r['k'] for r in rolls])
    last_roll = np.full(NI, -1e9)
    ri = 0
    trails = np.zeros((3, n))
    plungers = pl['plungers']
    nudges = pl['nudges']
    sn = pl['sneak']
    sn_S = sn.sample(np.arange(F) * DT)

    def attract(tl, buf, reveal=True):
        step = int(np.floor(tl / (BEAT / 2)))
        on = np.clip((750 * (tl + 0.35) - dPFC) / 120, 0, 1) if reveal else np.ones(n)
        bar = int(tl / BAR) % 3
        if bar < 2:
            ins_on = ((np.floor(ins_dc / 46).astype(int) - step) % 3 == 0) * 0.85 + 0.1
        else:
            left = ins_s < PFC
            ins_on = np.where(left == ((step // 2) % 2 == 0), 0.85, 0.1)
        buf += light(PLAY, 0.07 * on)
        acc = np.zeros((n, 3))
        for k in range(NI):
            acc += ins_lamp[k][:, None] * perc1(ins_on[k]) * ins_col[k]
        buf += acc * (on[:, None] ** 2)
        who = ['A', 'C', 'D', 'E', 'B'][step // 2 % 5]
        for k, col in BUMPERS.items():
            lv = 0.85 if k == who else 0.25
            buf += light(col, lv * np.exp(-(corner_d[k] / 16) ** 2) * on)
        for k in 'BE':
            lv = 0.9 if k == who else 0.2
            fb = flip_bar[k]
            buf += light(WARM, lv * ((fb >= 0) & (fb <= 1)) * (1 - 0.4 * fb) * on)
        for i in range(4):
            lit = (step + i) % 4 < 2
            buf += light(LIME, (0.7 if lit else 0.12) * tgt_lamp[i] * on)
        buf += light(GOLD, 0.5 * (0.5 + 0.5 * np.cos(2 * np.pi * tl / BAR * 2)) * g(PFC, 7) * on)
        ch = 0.5 + 0.5 * np.cos(2 * np.pi * ((END - pd) / 30 + tl * 2.5))
        buf += light(CYAN, 0.45 * shooter * ch ** 3 * on)

    def perc1(x):
        return np.clip(x, 0, None) ** 2.2

    for f in range(F):
        t = f * DT
        buf = np.zeros((n, 3))

        # ================= attract mode =================
        if t < T_START + 0.25:
            if t < T_START:
                attract(t, buf)
            fl = max(0.0, 1 - abs(t - T_START) / 0.25) if t > T_START - 0.25 else 0.0
            buf += light(WARM, 0.5 * fl * (0.4 + 0.6 * (dPFC < 2000)))
            out[f] = buf
            if t < T_START:
                continue

        # ================= the game =================
        if t < T_TILT:
            k_s = np.searchsorted(score_t, t, side='right')
            frac = (score_c[k_s - 1] / total) if k_s else 0.0
            frac = float(frac) ** 0.7
            gi_on = float(smoothstep(T_START, T_START + 0.5, t))
            # GI bed: the playfield brightens as the score climbs
            gi = gi_on * (0.17 + 0.28 * frac)
            if t >= pl['L2']:                              # multiball: the playfield throbs on the beat
                ph = ((t - pl['L2']) / BEAT) % 1.0
                gi *= 1 + 0.35 * np.exp(-ph / 0.18)
            buf += light(PLAY, gi * np.ones(n))
            for ln in lanes:                               # a completed lane keeps a warm bed
                if t >= ln['t']:
                    u = t - ln['t']
                    blink = 1.0 + 1.6 * (u < 0.75) * (np.sin(2 * np.pi * 4 * u) > 0)
                    buf += light(RUN_COL[ln['run']], 0.2 * blink * run_mask[ln['run']])

            # rollover lamps: dim until collected, flash as a ball crosses, chase ahead of passing balls
            while ri < len(roll_t) and roll_t[ri] <= t:
                last_roll[roll_k[ri]] = roll_t[ri]
                ri += 1
            lv = np.where(collect_t <= t, 0.45 + 0.15 * frac, 0.2)
            lv = lv + 0.75 * np.exp(-(t - last_roll) / 0.22)
            for w in range(3):
                s = S[w, f]
                if not np.isfinite(s) or f == 0 or not np.isfinite(S[w, f - 1]):
                    continue
                v = (s - S[w, f - 1]) / DT
                if abs(v) < 60:
                    continue
                ah = (ins_s - s) * np.sign(v)
                near = (ah > 0) & (ah < 170)
                lv = lv + near * 0.5 * np.clip(np.cos(2 * np.pi * (ah / 46 - t * 7)), 0, 1) ** 2 * (1 - ah / 170)
            buf += ins_lamp.T @ (perc1(lv)[:, None] * ins_col)

            # pop bumpers: idle lamps and hits, each its own way
            for k, col in BUMPERS.items():
                buf += light(col, (0.28 + 0.3 * frac) * (1 + 0.15 * np.sin(t * 3 + ord(k))) * np.exp(-(corner_d[k] / 14) ** 2))
            for th, k in bumps:
                u = t - th
                if u < 0 or u > 0.9:
                    continue
                d = corner_d[k]
                col = BUMPERS[k]
                core = np.exp(-u / 0.09) * np.exp(-(d / 14) ** 2)
                buf += light(WHITE, 0.9 * core) + light(col, 1.0 * np.exp(-u / 0.2) * np.exp(-(d / 30) ** 2))
                if k == 'A':                               # two red rings out along Side and Left
                    for lag in (0.0, 0.12):
                        uu = u - lag
                        if uu > 0:
                            r = 520 * uu
                            buf += light(RED, 0.85 * np.exp(-uu / 0.28) * np.exp(-((d - r) / 13) ** 2))
                elif k == 'C':                             # green sparkle spinner
                    spin = (np.sin(2 * np.pi * (sparkle_seed * 7 + u * 11)) > 0.55) * (d < 85)
                    buf += light(GREEN, 0.9 * np.exp(-u / 0.32) * spin * np.exp(-d / 70))
                else:                                      # violet ripples
                    rip = 0.5 + 0.5 * np.cos(2 * np.pi * (d / 26 - u * 5))
                    buf += light(VIOLET, 0.85 * np.exp(-u / 0.32) * rip ** 2 * np.exp(-d / 85))
                # score flash: every collected lamp blinks
                if u < 0.12:
                    buf += ins_lamp.T @ (perc1(0.25 * (collect_t <= t))[:, None] * WARM[None, :])

            # flippers: bats along the porch rails
            for k in 'BE':
                fb = flip_bar[k]
                bat = ((fb >= 0) & (fb <= 1)).astype(float)
                lvb = 0.22 + 0.1 * frac
                for th, kk in catches:
                    if kk == k and 0 <= t - th < 1.0:
                        lvb = max(lvb, 0.45)
                for th, kk in flips:
                    u = t - th
                    if kk != k or u < 0 or u > 0.5:
                        continue
                    head = np.clip(u / 0.06, 0, 1)
                    lvb = lvb + 0.9 * np.exp(-u / 0.14)
                    buf += light(AMBER, 0.9 * np.exp(-u / 0.1) * np.exp(-((fb - head) / 0.12) ** 2) * (fb >= 0))
                buf += light(WARM, lvb * bat * (1 - 0.45 * np.clip(fb, 0, 1)))

            # plunger lane at the free end of Right
            tip = END - 34.0
            armed = False
            for ta, tp, tr in plungers:
                if ta <= t < tp:
                    armed = True
                elif tp <= t < tr:
                    armed = True
                    tip = END - 34 + 20 * (t - tp) / (tr - tp)
                elif tr <= t < tr + 0.6:
                    u = t - tr
                    tip = END - 34 + 20 * np.exp(-u / 0.06) * np.cos(2 * np.pi * 6 * u)
                    buf += light(CYAN, 0.8 * np.exp(-u / 0.15) * np.exp(-((pd - (END - 120 - 900 * u)) / 40) ** 2) * shooter)
            for c in range(5):
                sc = tip + (END - tip) * (c + 0.5) / 5
                buf += light(STEEL, 0.6 * np.exp(-((pd - sc) / 2.6) ** 2))
            buf += light(STEEL, 0.4 * np.exp(-((pd - tip) / 4) ** 2))
            ch = 0.5 + 0.5 * np.cos(2 * np.pi * ((END - pd) / 30 + t * (3.5 if armed else 0.6)))
            buf += light(CYAN, (0.55 if armed else 0.18) * shooter * ch ** 3)
            for tk in kicks:                               # a ball off the plunger tip
                u = t - tk
                if 0 <= u < 0.4:
                    buf += light(WHITE, 0.8 * np.exp(-u / 0.08) * np.exp(-((pd - tip) / 18) ** 2))

            # the drain: a red glow at the back of the Side that wakes when a ball climbs toward it
            near = 0.0
            for w in range(3):
                s = S[w, f]
                if np.isfinite(s) and s < P['A']:
                    near = max(near, 1 - s / P['A'])
            dr = 0.16 + 0.75 * near ** 2 * (0.6 + 0.4 * np.sin(t * 2 * np.pi * 6))
            buf += light(RED, dr * np.exp(-(pd / 32) ** 2))

            # target bank and saucer on the Porch Front
            for i in range(4):
                down = None
                for th, ii in targets:
                    if ii == i and th <= t:
                        down = th
                reset = [b + 1.6 for b in banks if b + 1.6 <= t]
                up = down is None or (reset and reset[-1] > down)
                if up:
                    rs = (t - reset[-1]) if reset else 9
                    buf += light(LIME, (0.55 + 0.6 * np.exp(-rs / 0.2)) * tgt_lamp[i])
                else:
                    u = t - down
                    buf += light(WHITE, 1.0 * np.exp(-u / 0.08) * tgt_lamp[i]) + light(LIME, 0.06 * tgt_lamp[i])
            for tb in banks:
                u = t - tb
                if 0 <= u < 1.2:
                    pf = (pd > P['C']) & (pd < P['D'])
                    buf += light(LIME, 0.7 * np.exp(-u / 0.4) * pf * (np.sin(2 * np.pi * 5 * u) > 0))
            sau = 0.3
            if T_LOCK_LIT <= t < T_LOCK:
                sau = 0.85 * (np.sin(2 * np.pi * 2.5 * t) > 0) + 0.2
            buf += light(GOLD, sau * g(PFC, 8))
            if pl['K1'] + 11.0 <= t < T_JP:                  # jackpot lit: lamps race in to the saucer
                q = np.clip(1 - np.abs(pd - PFC) / (0.5 * (P['D'] - P['C'])), 0, 1)
                cc = 0.5 + 0.5 * np.cos(2 * np.pi * (np.abs(pd - PFC) / 28 + t * 4))
                buf += light(ORANGE, 0.75 * (q > 0) * cc ** 4 * (0.4 + 0.6 * q))

            # the lock: the saucer swallows ball 1, a gold wave runs to both ends of the house
            u = t - T_LOCK
            if 0 <= u < 2.6:
                for lag in (0.0, 0.55, 1.1):
                    uu = u - lag
                    if uu > 0:
                        buf += light(GOLD, 0.8 * np.exp(-uu / 0.9) * np.exp(-((dPFC - 1100 * uu) / 45) ** 2))
                buf += light(GOLD, 0.6 * np.exp(-u / 1.2) * g(PFC, 24) * (0.6 + 0.4 * np.sin(t * 25)))

            # the jackpot
            u = t - T_JP
            if 0 <= u < 3.5:
                for lag, col in ((0.0, GOLD), (0.3, ORANGE), (0.6, VIOLET), (0.9, GREEN), (1.2, GOLD)):
                    uu = u - lag
                    if uu > 0:
                        buf += light(col, 1.0 * np.exp(-uu / 1.2) * np.exp(-((dPFC - 1300 * uu) / 55) ** 2))
                buf += light(WARM, 0.6 * np.exp(-u / 0.12))
                for k, col in BUMPERS.items():
                    buf += light(col, 0.9 * (np.sin(2 * np.pi * 3 * u + ord(k)) > 0) * np.exp(-u / 1.5) *
                                 np.exp(-(corner_d[k] / 40) ** 2))
                spk = (rng.random(n) < 0.04 * np.exp(-u / 1.0))
                buf += light(GOLD, 0.9 * spk)

            # danger warning on the second nudge
            tn, _ = nudges[1]
            u = t - tn
            if 0 <= u < 0.6:
                buf += light(RED, 0.9 * np.exp(-u / 0.25) * ((pd > P['C']) & (pd < P['D'])))
                buf += ins_lamp.T @ (perc1(0.8 * np.exp(-u / 0.3) * np.ones(NI))[:, None] * RED[None, :])

            # the balls
            for w in range(3):
                s = S[w, f]
                trails[w] *= 0.72
                if not np.isfinite(s):
                    continue
                d = pd - s
                if w == 0:                                  # jack-o'-lantern
                    fl = 1 + 0.12 * np.sin(t * 31) + 0.08 * np.sin(t * 17)
                    I = np.exp(-(d / 15) ** 2)
                    buf += light(ORANGE, 0.95 * fl * I) + light(PUMPKIN_CORE, 0.8 * np.exp(-(d / 6) ** 2))
                    tcol = ORANGE
                elif w == 1:                                # eyeball: white, red iris
                    I = np.exp(-(d / 15) ** 2)
                    iris = np.exp(-(d / 5) ** 2)
                    buf += light(WHITE, 0.85 * I * (1 - iris)) + light(EYE, 1.0 * iris)
                    tcol = WHITE
                else:                                       # ghost ball
                    I = np.exp(-(d / 15) ** 2)
                    buf += light(GHOST, 0.95 * I) + light(WHITE, 0.6 * np.exp(-(d / 5) ** 2))
                    tcol = GHOST
                trails[w] = np.maximum(trails[w], 0.6 * I)
                buf += light(tcol, 0.55 * trails[w] * (1 - I))

            # the shake: the whole table slides along the roofline
            sh = 0.0
            for tn, amp in nudges:
                u = t - tn
                if 0 <= u < 0.8:
                    sh += amp * np.exp(-u / 0.18) * np.sin(2 * np.pi * 7 * u)
            if abs(sh) > 0.2:
                pb = buf[G.path]
                x = np.arange(n)
                sb = np.stack([np.interp(x - sh, x, pb[:, c]) for c in range(3)], -1)
                buf[G.path] = sb

        # ================= tilt =================
        elif t < pl['T_KNOCK']:
            u = t - T_TILT
            if u < 2.3:                                     # the TILT lamp buzzes
                bz = 0.55 + 0.45 * np.sin(2 * np.pi * 15 * t)
                buf += light(RED, 0.75 * bz * g(PFC, 10))
            # in the dark, one ball wakes and tiptoes for the drain (which glows, faintly, the only lamp left)
            if t >= pl['T_WAKE']:
                buf += light(RED, 0.16 * float(smoothstep(pl['T_WAKE'], pl['T_WAKE'] + 2, t)) *
                             (0.8 + 0.2 * np.sin(t * 3)) * np.exp(-(pd / 30) ** 2) * (t < pl['T_PLOP'] + 0.15))
            s = sn_S[f]
            if np.isfinite(s) and t >= pl['T_WAKE']:
                d = pd - s
                wake = float(smoothstep(pl['T_WAKE'], pl['T_WAKE'] + 0.8, t))
                drop = 1 - float(smoothstep(pl['T_PLOP'], pl['T_PLOP'] + 0.17, t))
                lvl = 0.5 * wake * drop
                w = pl['sneak_ball']
                col = (ORANGE, WHITE, GHOST)[w]
                buf += light(col, lvl * np.exp(-(d / 13) ** 2))
                if w == 1:
                    buf += light(EYE, lvl * 1.4 * np.exp(-(d / 5) ** 2))
                else:
                    buf += light(PUMPKIN_CORE if w == 0 else WHITE, 0.8 * lvl * np.exp(-(d / 5) ** 2))
            u = t - pl['T_PLOP']
            if 0.12 <= u < 1.0:                              # plop
                uu = u - 0.12
                buf += light(RED, 0.7 * np.exp(-uu / 0.18) * np.exp(-(pd / 30) ** 2))
                buf += light(ORANGE, 0.5 * np.exp(-uu / 0.3) * np.exp(-((pd - 300 * uu) / 14) ** 2))

        # ================= free game: knock, and the attract lights come back =================
        else:
            u = t - pl['T_KNOCK']
            buf += light(WARM, 0.6 * np.exp(-u / 0.12))
            if u > 0.25:
                fade = 1 - float(smoothstep(D - 1.6, D - 0.05, t))
                tmp = np.zeros((n, 3))
                attract(u - 0.25, tmp)
                buf += tmp * fade
        out[f] = buf
    return np.clip(out, 0, 1)


# ---- soundtrack ---------------------------------------------------------------------------------------
# A surf-organ arcade number in E minor at 150 BPM (the attract chase steps on its eighths). Attract mode
# has its own little marimba jingle; a coin dings; the snare rolls while the plunger pulls back and the
# band crashes in on the launch: drums, a picked bass, combo-organ stabs on the off-beats and a tremolo-
# picked surf guitar tune. Over it, the table: each pop bumper rings its own bell of the E minor chord
# (A low E, C the G, D the B) with a solenoid thwack, flippers clack, every rollover lamp collected plays
# the next note up a pentatonic run, targets knock, the bank and finished lanes run arpeggios, and a slide
# whistle rides the ball up the Side toward the drain and back. The saucer gulps the lock, the band stops,
# a drum fill pulls the next plunger and multiball kicks the tune up; the jackpot crashes and the band
# moves up a whole step. Nudges thump on the beat. TILT: the music dies on the spot under a mains buzz.
# The sneaking ball tiptoes on pizzicato, peeks, and plops out with a slide whistle; the knocker bangs
# for a free game and the attract jingle starts over.

CHORDS = {'Em': (52, 55, 59), 'C': (52, 55, 60), 'G': (50, 55, 59), 'A': (52, 57, 61), 'B7': (51, 54, 57, 59),
          'Am': (52, 57, 60)}
ROOTS = {'Em': 40, 'C': 36, 'G': 43, 'A': 45, 'B7': 35, 'Am': 45}
MEL_A = [(0, 'E4', 1, 0), (1, 'G4', .5, 0), (1.5, 'A4', .5, 0), (2, 'B4', 2, 1),
         (4, 'D5', .5, 0), (4.5, 'B4', .5, 0), (5, 'A4', .5, 0), (5.5, 'G4', .5, 0), (6, 'E4', 2, 1),
         (8, 'E4', .5, 0), (8.5, 'G4', .5, 0), (9, 'C5', 1, 0), (10, 'B4', .5, 0), (10.5, 'A4', .5, 0), (11, 'G4', 1, 0),
         (12, 'F#4', 2, 1), (14, 'D#4', .5, 0), (14.5, 'F#4', .5, 0), (15, 'B3', 1, 0)]
MEL_B = [(0, 'B4', .5, 0), (.5, 'B4', .5, 0), (1, 'E5', 1, 0), (2, 'D5', .5, 0), (2.5, 'B4', .5, 0), (3, 'G4', 1, 0),
         (4, 'D5', 2, 1), (6, 'B4', .5, 0), (6.5, 'G4', .5, 0), (7, 'D4', 1, 0),
         (8, 'C#5', .5, 0), (8.5, 'E5', .5, 0), (9, 'A4', 1, 0), (10, 'C#5', 1.5, 1), (11.5, 'E5', .5, 0),
         (12, 'D#5', 2, 1), (14, 'F#4', .5, 0), (14.5, 'A4', .5, 0), (15, 'B4', 1, 0)]
PENTA = [64, 67, 69, 71, 74, 76, 79, 81, 83, 86]           # E minor pentatonic from E4
BELL = {'A': 'E4', 'C': 'G4', 'D': 'B4'}


def score(M, G):
    from pixelhome.audio import SR, note, slide, whoosh
    n = note
    pl = _plan(G)
    geo = pl['geo']
    P, END = geo['P'], geo['END']
    ev, D = pl['events'], pl['D']
    T_LOCK, L2, K1, T_JP, T_TILT = pl['T_LOCK'], pl['L2'], pl['K1'], pl['T_JP'], pl['T_TILT']
    T_KNOCK = pl['T_KNOCK']

    for name, gain, rev in (('drums', 0.5, 0.12), ('bass', 0.42, 0.06), ('organ', 0.42, 0.25), ('lead', 0.24, 0.3),
                            ('jingle', 0.35, 0.25), ('pins', 0.5, 0.15), ('chime', 0.32, 0.25), ('fx', 0.4, 0.2)):
        M.bus(name, gain=gain, reverb=rev)
    MUSIC = ('drums', 'bass', 'organ', 'lead', 'jingle', 'chime')

    order = np.argsort(G.pd)
    xs, ds = G.pos[order, 0], G.pd[order]
    x0, x1 = xs.min(), xs.max()

    def pan_at(s):
        return float(0.85 * (2 * (np.interp(s, ds, xs) - x0) / (x1 - x0) - 1))

    tb = M.sampler('Percussion/TB_hit*.wav')
    xylo = M.sampler('Percussion/Xylo/*.wav')
    glock = M.sampler('Percussion/Glock/*.wav')
    mar = M.sampler('Percussion/Marimba/*.wav')
    pizz = M.sampler('Strings/Cello Section/pizzT/*.wav')
    bassoon = M.sampler('Woodwinds/Bassoon/stac/*.wav')
    tpt = M.sampler('Brass/Trumpet/stac/*.wav')
    trb = M.sampler('Brass/Tenor Trombone/sus/*.wav', tune=-12)
    kick = M.hits('VSCO 1 Percussion/drums/bass/bdrum_f_*.wav')
    kick_b = M.hits('VSCO 1 Percussion/drums/bass/bdrum_fff_*.wav')
    snare = M.hits('VSCO 1 Percussion/drums/snare/drum1/snare1_f_*.wav')
    ride = M.hits('VSCO 1 Percussion/varMetal/Cymbals/susp/susp_hit_metal_2_mf.wav')
    tamb = M.hits('Percussion/Tamb1-Hit*.wav')
    crash = M.hits('Percussion/cymbal-crash1_f*.wav')
    sroll = M.hits('Percussion/Snare2-rollNS_v5*.wav')
    gong = M.hits('VSCO 1 Percussion/varMetal/Gong/gong_hit_fff.wav')
    thwack = M.hits('Percussion/Snare2-HitSN_v7*.wav')
    metal = M.hits('Miscellania Raw/Misc 1/metal_hit1[0-1].wav')
    clave = M.hits('Percussion/Claves1_Hit*.wav')
    thunk = M.hits('Percussion/BDrumNewhit_v[3-4]*.wav')
    slap = M.hits('VSCO 1 Percussion/varWood/slapstick[0-9].wav')
    logd = M.hits('Percussion/LogDrumLo*.wav')
    logh = M.hits('Percussion/LogDrumHi*.wav')
    cow = M.hits('Percussion/Cowbell1_Hit*.wav')
    ratchet = M.hits('Percussion/Ratchet1-Slow*.wav')
    timp = M.hits('Percussion/Timpani/Timpani1_Hit*.wav')
    shake = M.hits('Percussion/Tamb1-Shake*.wav')

    def sine_env(sec, f, tau, harm=1):
        tt = np.arange(int(sec * SR)) / SR
        f = np.broadcast_to(np.asarray(f, float), tt.shape)
        ph = 2 * np.pi * np.cumsum(f) / SR
        y = sum(np.sin(k * ph) / k for k in range(1, harm + 1))
        return y * np.exp(-tt / tau) * np.clip(tt / 0.004, 0, 1)

    def put(bus, mono, t, gain=1.0, pan=0.0):
        a = (pan + 1) * np.pi / 4
        M.add(bus, np.vstack([mono * np.cos(a), mono * np.sin(a)]) * np.sqrt(2), t, gain)

    organ, lead, bass, jingle_org = [], [], [], []

    # ---- the band ----
    def band(t0, t1, prog, mel, tr=0, busy=False):
        nb = int(np.ceil((t1 - t0) / BAR - 1e-6))
        for b in range(nb):
            tb0 = t0 + b * BAR
            ch = prog[b % len(prog)]
            for e in range(8):
                te = tb0 + e * BEAT / 2
                if te >= t1 - 0.02:
                    break
                if e in (0, 4) or (busy and e == 5):
                    M.add('drums', kick.play(110 if e == 0 else 95), te, 0.9)
                if e in (2, 6):
                    M.add('drums', snare.play(108), te, 0.75)
                M.add('drums', ride.play(70 if e % 2 else 90, dur=0.35), te, 0.22, 0.25)
                if busy:
                    M.add('drums', tamb.play(70 if e % 2 else 95), te, 0.35, -0.3)
                    M.add('drums', tamb.play(55), te + BEAT / 4, 0.25, -0.3)
                off = [0, 0, 12, 0, 7, 7, 10, 7][e]
                bass.append((te, ROOTS[ch] + tr + off, 100 if e % 2 == 0 else 84, min(BEAT / 2 - 0.03, t1 - te - 0.01)))
                if e % 2 == 1:
                    for m in CHORDS[ch]:
                        organ.append((te, m + tr, 92, min(0.13, t1 - te - 0.01)))
        for p in np.arange(t0, t1, 4 * BAR):
            for bt, nm, ln, trem in mel:
                t = p + bt * BEAT
                if t >= t1 - 0.02:
                    break
                dur = min(ln * BEAT, t1 - t - 0.01)
                if trem:                                  # surf tremolo picking in sixteenths
                    for k in range(int(round(dur / (BEAT / 4)))):
                        lead.append((t + k * BEAT / 4, n(nm) + tr, 100 if k == 0 else 82, BEAT / 4 - 0.02))
                else:
                    lead.append((t, n(nm) + tr, 104, dur - 0.02))

    # ---- attract jingle (start and end) ----
    def attract_music(t0, t1, gain=1.0):
        prog = ['Em', 'C', 'Am', 'B7', 'Em', 'B7']
        b = 0
        for tb0 in np.arange(t0, t1 - 0.05, BAR):
            ch = CHORDS[prog[b % 6]]
            arp = [ch[0], ch[1], ch[2], ch[0] + 12, ch[2] + 12, ch[0] + 12, ch[2], ch[1]]
            for e, m in enumerate(arp):
                te = tb0 + e * BEAT / 2
                if te < t1:
                    M.add('jingle', mar.play(m, 92 if e % 4 == 0 else 74), te, 0.7 * gain, 0.2 * np.sin(e))
            for m in ch:
                jingle_org.append((tb0, m, 58, min(BAR - 0.05, t1 - tb0)))
            M.add('drums', tamb.play(60), tb0 + BEAT, 0.25 * gain, -0.3)
            M.add('drums', tamb.play(60), tb0 + 3 * BEAT, 0.25 * gain, -0.3)
            b += 1

    attract_music(0.0, T_START)
    M.add('chime', tb.play(n('B4'), 110), T_START, 0.6)          # coin in
    M.add('chime', tb.play(n('E5'), 110), T_START + 0.12, 0.6)
    for m in CHORDS['Em']:
        organ.append((T_START, m, 96, 0.7))

    # ---- plungers: ratchet as the spring pulls back, a boing and a whoosh on release ----
    pe = pan_at(END)
    for i, (ta, tp, tr_) in enumerate(pl['plungers']):
        M.add('fx', ratchet.play(90, dur=tr_ - tp), tp, 0.45, pe)
        tt = np.arange(int(0.6 * SR)) / SR
        boing = sine_env(0.6, 150 * (1 + 0.35 * np.exp(-tt / 0.15) * np.sin(2 * np.pi * 13 * tt)), 0.22, harm=3)
        put('fx', boing, tr_, 0.5, pe)
        M.add('fx', whoosh(0.9, 400, 2600, 0.45, seed=5 + i), tr_, 0.5, 0.4)
        M.add('pins', metal.play(100, pitch=4, dur=0.3), tr_, 0.35, pe)
    M.add('drums', sroll.play(70, dur=T_LAUNCH - T_PULL), T_PULL, 0.55)
    M.add('drums', crash.play(118), T_LAUNCH, 0.6)
    M.add('drums', kick_b.play(120), T_LAUNCH, 0.8)

    band(T_LAUNCH, T_LOCK, ['Em', 'Em', 'C', 'B7'], MEL_A)

    # ---- the lock: a gulp, the band stops on a hit, bells climb the chord ----
    pc = pan_at(geo['PFC'])
    M.add('drums', crash.play(115), T_LOCK, 0.55, pc)
    M.add('drums', kick_b.play(124), T_LOCK, 0.9, pc)
    M.add('pins', timp.play(120, pitch=-5), T_LOCK, 0.8, pc)
    tt = np.arange(int(0.5 * SR)) / SR
    put('fx', sine_env(0.5, 420 * (110 / 420) ** (tt / 0.5), 0.2, harm=2), T_LOCK + 0.05, 0.5, pc)
    for m in (40, 47, 52, 55, 59):
        organ.append((T_LOCK, m, 100, 1.3))
    for i, m in enumerate(('E4', 'G4', 'B4', 'E5')):
        M.add('chime', tb.play(n(m), 105), T_LOCK + 0.5 + 0.25 * i, 0.55, pc)
    T_P2 = pl['T_P2']
    for k in range(8):                                    # the fill that pulls plunger two
        M.add('drums', snare.play(80 + 5 * k), T_P2 + k * BEAT / 4, 0.6, 0.2 * (k % 2 * 2 - 1))
    M.add('drums', crash.play(120), L2, 0.6)
    M.add('drums', kick_b.play(124), L2, 0.8)
    M.add('pins', metal.play(110, pitch=-3), K1, 0.5, pc)          # the saucer kicks ball one out
    M.add('pins', thunk.play(110), K1, 0.6, pc)

    # ---- multiball, and up a whole step after the jackpot ----
    t_up = float(_grid(T_JP, L2, BAR))
    band(L2, t_up, ['Em', 'G', 'A', 'B7'], MEL_B, busy=True)
    band(t_up, T_TILT, ['Em', 'G', 'A', 'B7'], MEL_B, tr=2, busy=True)

    # ---- the table ----
    for e in ev:
        t, k, p = e['t'], e['kind'], pan_at(e['s'])
        nd = e.get('node')
        if k == 'bump':
            M.add('chime', tb.play(n(BELL[nd]), 100), t, 0.45, p)
            M.add('pins', thwack.play(100), t, 0.45, p)
            M.add('pins', metal.play(80, pitch=6, dur=0.18), t, 0.2, p)
            M.add('pins', thunk.play(90), t, 0.35, p)
        elif k == 'flip':
            M.add('pins', clave.play(110), t, 0.4, p)
            M.add('pins', thunk.play(100), t, 0.5, p)
        elif k == 'catch':
            M.add('pins', clave.play(60, pitch=-5), t, 0.25, p)
        elif k == 'pass':
            M.add('fx', slide(0.0, 0.35, 900, 500, 0.4, 0.4), t, 0.35, p)
        elif k == 'kick':
            M.add('pins', metal.play(105, pitch=2, dur=0.3), t, 0.4, p)
            M.add('pins', thunk.play(110), t, 0.5, p)
        elif k == 'target':
            M.add('pins', slap.play(110), t, 0.5, p)
            M.add('pins', logh.play(100), t, 0.5, p)
        elif k == 'bank':
            for i, m in enumerate((64, 67, 71, 76, 79)):
                M.add('chime', xylo.play(m, 110), t + 0.07 * (i + 1), 0.45, p)
            M.add('pins', cow.play(110), t, 0.35, p)
        elif k == 'jackpot':
            M.add('drums', crash.play(127), t, 0.8, pc)
            M.add('drums', gong.play(120), t, 0.6, pc)
            M.add('drums', kick_b.play(127), t, 0.9, pc)
            for m in ('E4', 'G4', 'B4'):
                M.add('fx', tpt.play(n(m), 120, dur=0.6), t, 0.6, pc)
                M.add('fx', tpt.play(n(m), 115, dur=0.9), t + 0.3, 0.5, pc)
            M.add('fx', trb.play(n('E3'), 115, dur=1.4), t, 0.6, pc)
            for i in range(10):
                M.add('chime', xylo.play(PENTA[i], 100), t + 0.5 + 0.05 * i, 0.4, -0.8 + 0.16 * i)
        elif k == 'apex':                                  # the slide whistle climbs the Side and comes back
            prev = [q['t'] for q in ev if q['ball'] == e['ball'] and q['kind'] == 'bump' and q['t'] < t]
            nxt = [q['t'] for q in ev if q['ball'] == e['ball'] and q['kind'] == 'bump' and q['t'] > t]
            t0 = prev[-1] if prev else t - 0.8
            t2 = nxt[0] if nxt else t + (t - t0)
            sec = t2 - t0
            M.add('fx', slide(0.0, t - t0, 330, 820, sec, 0.45, shape=1.6), t0, 0.32, pan_at(P['A'] * 0.6))
            M.add('fx', slide(t - t0, sec, 820, 330, sec, 0.45, shape=0.6), t0, 0.32, pan_at(P['A'] * 0.6))

    # rollovers: each new lamp is the next note up its lane's run; old lamps just tick
    counts = {}
    for r in pl['rolls']:
        p = pan_at(r['s'])
        if r['first']:
            c = counts.get(r['run'], 0)
            counts[r['run']] = c + 1
            M.add('chime', xylo.play(PENTA[min(c, 9)], 96), r['t'], 0.4, p)
        else:
            M.add('pins', clave.play(45, pitch=7), r['t'], 0.08, p)
    for ln in pl['lanes']:
        p = pan_at(float(G.pd[G.seg[ln['run']]].mean()))
        for i, m in enumerate((76, 79, 83, 88)):
            M.add('chime', glock.play(m, 90), ln['t'] + 0.12 * i, 0.3, p)

    # nudges: the cabinet thumps on the beat; the second one gets a warning bell
    for i, (tn, amp) in enumerate(pl['nudges']):
        M.add('pins', kick_b.play(110 + 5 * i), tn, 0.7 + 0.1 * i)
        M.add('pins', shake.play(100), tn, 0.4 + 0.1 * i)
        M.add('pins', metal.play(90, pitch=-6, dur=0.4), tn, 0.25 * amp / 3)
    M.add('chime', tb.play(n('F4'), 120), pl['nudges'][1][0], 0.6, pc)
    M.add('chime', tb.play(n('F4'), 120), pl['nudges'][1][0] + 0.2, 0.5, pc)

    # ---- render the synths, then TILT: everything musical dies on the spot ----
    M.add('organ', M.synth('Keys/Organ 2').render(organ, D), 0.0)
    M.add('lead', M.synth('Plucks/E-Guitar').render(lead, D), 0.0)
    M.add('bass', M.synth('Basses/Fingered').render(bass, D), 0.0)
    M.add('jingle', M.synth('Keys/Organ 2').render(jingle_org, D), 0.0, 0.5)
    s1 = int(T_TILT * SR)
    for b in MUSIC + ('pins', 'fx'):
        sig = M.buses[b]['sig']
        sig[:, s1:] = 0
        sig[:, s1 - 48:s1] *= np.linspace(1, 0, 48)
    tt = np.arange(int(2.3 * SR)) / SR
    buzz = np.tanh(3 * np.sin(2 * np.pi * 120 * tt)) + 0.5 * np.sin(2 * np.pi * 60 * tt)
    buzz += 0.3 * np.random.default_rng(3).normal(0, 1, len(tt)) * (np.sin(2 * np.pi * 15 * tt) > 0)
    buzz *= np.clip(tt / 0.005, 0, 1) * np.clip((2.3 - tt) / 0.02, 0, 1) * (1 - 0.25 * np.sin(2 * np.pi * 15 * tt))
    put('fx', buzz, T_TILT, 0.17, pc)
    M.add('pins', metal.play(120, pitch=-10), T_TILT, 0.6, pc)
    M.add('pins', kick_b.play(110), T_TILT, 0.6, pc)

    # ---- the sneak: wakes, looks both ways, tiptoes on pizzicato, peeks, plops out the drain ----
    sn = pl['sneak']
    sb = sn.legs[0][2]
    tw = pl['T_WAKE']
    M.add('chime', xylo.play(n('B4'), 60), tw + 1.0, 0.3, pan_at(sb + 9))
    M.add('chime', xylo.play(n('A#4'), 60), tw + 1.34, 0.3, pan_at(sb - 9))
    hop_notes = [40, 43, 45, 46, 47, 50, 52, 55, 57, 58, 59, 62, 64, 67, 69]
    for i, (th, s_to) in enumerate(pl['hops']):
        M.add('jingle', pizz.play(hop_notes[i % len(hop_notes)], 95), th, 0.8, pan_at(s_to))
    tpk = pl['T_PEEK']
    M.add('fx', bassoon.play(n('E2'), 100, dur=0.16), tpk, 0.6, pan_at(30))
    M.add('fx', bassoon.play(n('D#2'), 95, dur=0.3), tpk + 0.45, 0.6, pan_at(30))
    tp = pl['T_PLOP']
    M.add('fx', slide(0.0, 0.45, 1100, 260, 0.5, 0.5), tp, 0.7, pan_at(0))
    tt = np.arange(int(0.4 * SR)) / SR
    put('fx', sine_env(0.4, 600 * (180 / 600) ** (tt / 0.15), 0.12), tp + 0.18, 0.5, pan_at(0))
    M.add('pins', timp.play(80, pitch=-3), tp + 0.2, 0.4, pan_at(0))

    # ---- the knocker: a free game, and the attract jingle starts over ----
    M.add('pins', kick_b.play(127), T_KNOCK, 1.0)
    M.add('pins', logd.play(127, pitch=-4), T_KNOCK, 0.9)
    M.add('pins', slap.play(127), T_KNOCK, 0.6)
    M.add('pins', metal.play(110, pitch=-8, dur=0.5), T_KNOCK, 0.4)
    for i in range(3):
        M.add('chime', tb.play(n('E5'), 100), T_KNOCK + 0.5 + 0.18 * i, 0.4, 0.0)
    jingle_org.clear()
    attract_music(T_KNOCK + 0.25, D)
    M.add('jingle', M.synth('Keys/Organ 2').render(jingle_org, D), 0.0, 0.5)
