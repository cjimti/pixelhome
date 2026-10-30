"""The Web: the roofline is a spider web strung across the house. The five corners are its anchor
points and the six runs are its strands, and every strand is a real string: a 1-D wave equation runs
along the roof, each run with its own wave speed so it rings at its own rate (longer runs lower), and
each corner is a stiff spring that holds a node but lets sharp flicks leak round to the next run. The
back end of Side is tied off to the fence; the right end of Right is a loose bridge line.

A spider abseils in at the front corner of the porch (bouncing on her line) and spins the web strand
by strand: Left, out along Side to tie off, back and round the porch rails, and last a bridge line
floated out on the breeze to the free end. Each new strand is plucked as it is anchored and tunes up
into its note (Side D, Right F, Porch Left A, Left C, Porch Right D, Porch Front E: a D minor ninth).
Dew forms and a moonbeam sweeps the web. She plays it like a harp, hopping corner to corner and
plucking the two strands that meet there, walking the tune down from the right of the house to the
left. A moth flutters in at the free end and blunders into the bridge line; its struggling buzzes the
strand, the flicks travel corner to corner until they reach her, and she races across the whole house
to it. The moth unfolds: it is enormous, and it has eyes on its wings. Three wingbeats, and it flies
off out of the free end with the whole web streaming behind it, each anchor popping in turn, the spider
riding along on the porch strand. A moment later she abseils back in and starts again with one strand."""
import numpy as np
from pixelhome.fx import DT, hexc, perc, smoothstep, keys, nframes

CODE = 'HW17'
TITLE = 'The Web'
KIND = 'show'
DESCRIPTION = ('A spider strings her web across the roof, one strand to a run, and every strand rings its own note '
               'when plucked. She plays a tune while she waits, until a moth blunders in, and it is far too big for the web.')
VOICEOVER = ('A spider has strung her web across the roof, and every strand plays a note. '
             'Listen closely... and hope nothing big flies by.')

BED = hexc('#1a2470')
MOTE = hexc('#8aa0ff')
SILK = hexc('#6f8cff')
WHITE = hexc('#e6fbff')
VIOLET = hexc('#9a3cff')
DEW = hexc('#d8fbff')
KNOT = hexc('#e8eeff')
SPIDER = hexc('#ff5010')
LEG = hexc('#ff8c28')
MOTH = hexc('#ffd8a0')
WING = hexc('#e07a28')
EYE = hexc('#ffc020')

MIDI = {'Side': 50, 'Right': 53, 'Porch Left': 57, 'Left': 60, 'Porch Right': 62, 'Porch Front': 64}
D = 75.0
FV0 = 0.9                   # visible fundamental of the lowest strand (Hz); the others in proportion to pitch
CELL = 5.0                  # wave grid spacing, layout units
SUB = 12                    # wave substeps per frame
KAPPA = 0.5                 # corner spring stiffness (dimensionless): fundamentals reflect, sharp flicks leak
GAM = 0.6                  # strand damping (1/s)
NU = 400.0                  # viscous damping of the finest ripples
ACC, V0 = 700.0, 150.0     # how a popped strand accelerates out of the free end
BED_I, SILK_I, WAVE_I = 0.11, 0.19, 0.7

T_TUNE, BEAT = 29.0, 0.5    # the harp tune: 120 BPM, 32 beats
T_MOTH, T_HIT, T_FEEL, T_RACE, T_POUNCE = 46.0, 49.0, 50.6, 51.0, 54.5
T_UNFOLD, T_EYES, T_BLINK, T_BACK = 54.8, 56.0, 56.7, 56.4
WINGBEATS = (57.4, 58.3, 59.2)
POPS = {'Right': 59.2, 'Porch Right': 59.7, 'Porch Front': 60.15, 'Porch Left': 60.55, 'Left': 60.95, 'Side': 61.4}
T_CODA = 66.0
BURSTS = ((49.0, 1.1), (50.4, 0.8), (51.6, 1.0), (52.9, 1.1), (54.1, 0.35))

# the tune: (beat, strand, accent). She sits on a corner and plucks the two strands that meet there.
MELODY = [(0, 'Right', .7), (1, 'Porch Right', .6), (2, 'Right', .65), (3, 'Porch Right', .6),
          (4, 'Right', .65), (4.5, 'Porch Right', .5), (5, 'Right', .6), (6, 'Porch Right', .8), (6, 'Right', .5),
          (8, 'Porch Front', .7), (9, 'Porch Right', .6), (10, 'Porch Front', .65), (11, 'Porch Right', .55),
          (11.5, 'Porch Front', .5), (12, 'Porch Right', .8), (12, 'Porch Front', .45),
          (16, 'Porch Front', .7), (17, 'Porch Left', .6), (18, 'Porch Front', .65), (18.5, 'Porch Left', .5),
          (19, 'Porch Front', .6), (20, 'Porch Left', .8), (20, 'Porch Front', .5),
          (24, 'Left', .7), (25, 'Porch Left', .6), (26, 'Left', .65), (26.5, 'Porch Left', .5),
          (27, 'Left', .6), (28, 'Porch Left', .8), (28, 'Left', .5),
          (30, 'Side', .75), (31, 'Left', .6), (32, 'Side', .9)]
BASS = ['D2', 'D2', 'Bb1', 'Bb1', 'A1', 'A1', 'F2', 'A1']


def _ease(u):
    u = np.clip(u, 0, 1)
    return u * u * (3 - 2 * u)


def _shift(t, tpop):
    """How far a popped strand has been dragged toward the free end."""
    if tpop is None or t < tpop:
        return 0.0
    tau = t - tpop
    return V0 * tau + 0.5 * ACC * tau * tau


def _out_time(dist):
    return (-V0 + np.sqrt(V0 * V0 + 2 * ACC * dist)) / ACC


def _head(lay, t):
    """Where the end of a strand being laid has got to."""
    u = np.clip((t - lay['t0']) / (lay['t1'] - lay['t0']), 0, 1)
    if lay.get('float'):                        # a bridge line drifting out on the breeze
        e = 1 - (1 - u) ** 2 + 0.04 * np.sin(2 * np.pi * 0.9 * (t - lay['t0'])) * u * (1 - u) * 4
    else:
        e = u
    return lay['a'] + (lay['b'] - lay['a']) * float(np.clip(e, 0, 1))


def _abseil(tau):
    """Height on her line (1 up high .. 0 on the roof): a drop, then bounces that die away."""
    if tau < 1.0:
        return 1 - tau * tau
    return 0.32 * np.exp(-1.6 * (tau - 1)) * abs(np.sin(np.pi * (tau - 1) / 0.55))


def _plan(G, seed=17):
    """Everything both render() and score() need, from one seed."""
    rng = np.random.default_rng(seed)
    ppd = G.pd[G.path].astype(float)
    L = float(ppd[-1])
    names = [nm for nm, _ in G.path_segments()]
    K = {nm: i for i, nm in enumerate(names)}
    cpi = [80, 178, 260, 331, 380]
    corner = {c: (ppd[c] + ppd[c + 1]) / 2 for c in cpi}
    cuts = np.array([corner[c] for c in cpi])
    lo = np.concatenate([[0.0], cuts])
    hi = np.concatenate([cuts, [L]])
    lens = hi - lo
    midi = np.array([MIDI[nm] for nm in names])
    c0 = 2 * lens * FV0 * 2 ** ((midi - 50) / 12)
    Mc = int(round(L / CELL)) + 1
    xs = np.linspace(0, L, Mc)
    rid = np.searchsorted(cuts, xs)
    pins = [int(np.argmin(np.abs(xs - corner[c]))) for c in cpi]
    pf_mid = (lo[K['Porch Front']] + hi[K['Porch Front']]) / 2
    pd_m = corner[380] + 190.0                  # where the moth hits the bridge line
    c80, c178, c260, c331, c380 = (corner[c] for c in cpi)
    T, B = T_TUNE, BEAT

    # ---- strands as they are laid (a: anchored end, b: far end), when they pop and when they are gone
    lays = [dict(run=K['Left'], t0=5.0, t1=6.8, a=c178, b=c80),
            dict(run=K['Side'], t0=8.4, t1=10.6, a=c80, b=0.0),
            dict(run=K['Porch Left'], t0=13.8, t1=15.7, a=c178, b=c260),
            dict(run=K['Porch Front'], t0=16.8, t1=18.4, a=c260, b=c331),
            dict(run=K['Porch Right'], t0=19.6, t1=21.3, a=c331, b=c380),
            dict(run=K['Right'], t0=22.0, t1=24.6, a=c380, b=L, float=True)]
    for lay in lays:
        lay['tpop'] = POPS[names[lay['run']]]
        lay['gone'] = lay['tpop'] + _out_time(L - lo[lay['run']] + 40)
    lays.append(dict(run=K['Left'], t0=68.5, t1=70.3, a=c178, b=c80, tpop=None, gone=1e9))

    # ---- anchors: (path distance, anchored, popped)
    anchors = [(c178, 5.0, POPS['Porch Left']), (c80, 6.8, POPS['Left']), (0.0, 10.6, POPS['Side']),
               (c260, 15.7, POPS['Porch Front']), (c331, 18.4, POPS['Porch Right']), (c380, 21.3, POPS['Right']),
               (c178, 68.5, None), (c80, 70.3, None)]

    # ---- the spider's way round the roof
    W = [(0, c178), (5.0, c178), (6.8, c80), (8.4, c80), (10.6, 3.0), (12.0, 3.0), (13.8, c178), (15.7, c260),
         (16.8, c260), (18.4, c331), (19.6, c331), (21.3, c380),
         (T + 7 * B, c380), (T + 8 * B, c331), (T + 15 * B, c331), (T + 16 * B, c260), (T + 23 * B, c260),
         (T + 24 * B, c178), (T + 29 * B, c178), (T + 30 * B, c80), (T_RACE, c80), (T_POUNCE, pd_m - 28),
         (T_BACK, pd_m - 28), (T_BACK + 0.8, pf_mid), (POPS['Porch Front'], pf_mid)]
    WC = [(T_CODA, c178), (68.5, c178), (70.3, c80), (D + 1, c80)]
    wt, wp = np.array([w[0] for w in W]), np.array([w[1] for w in W])
    wct, wcp = np.array([w[0] for w in WC]), np.array([w[1] for w in WC])

    def spider(t):
        """(path distance, visibility, height on her line)."""
        if t < 2.0:
            return c178, 0.0, 1.0
        if t < 5.0:
            return c178, 1.0, _abseil(t - 2.0)
        if t < POPS['Porch Front']:
            return float(np.interp(t, wt, wp)), 1.0, 0.0
        if t < T_CODA:                          # riding the porch strand out of the free end
            s = pf_mid + _shift(t, POPS['Porch Front'])
            return s, float(s < L + 25), 0.0
        h = _abseil(t - T_CODA) if t < 68.5 else 0.0
        return float(np.interp(t, wct, wcp)), 1.0, h

    # ---- plucks: (time, strand, apex distance, amplitude, kind)
    plucks = []

    def pluck_at(t, k, at, A, kind='pluck'):
        side = 1.0 if abs(lo[k] - at) < 1 else -1.0
        plucks.append((t, k, at + side * 0.2 * lens[k], A, kind))

    for t, nm, at in ((6.8, 'Left', c80), (10.6, 'Side', 0.0), (15.7, 'Porch Left', c260),
                      (18.4, 'Porch Front', c331), (21.3, 'Porch Right', c380), (24.6, 'Right', c380),
                      (70.3, 'Left', c80)):
        pluck_at(t, K[nm], at, 0.15, 'anchor')          # the line snaps taut
    for t, nm, at in ((7.2, 'Left', c80), (11.0, 'Side', 0.0), (16.0, 'Porch Left', c260),
                      (18.8, 'Porch Front', c331), (21.6, 'Porch Right', c380), (25.0, 'Right', c380),
                      (70.8, 'Left', c80)):
        pluck_at(t, K[nm], at, 0.8, 'tune')             # first pluck: it tunes up into its note
    pluck_at(72.2, K['Left'], c80, 0.55)
    for b, nm, A in MELODY:
        t = T + b * B
        at = float(np.interp(t, wt, wp))
        pluck_at(t, K[nm], at, A, 'melody')
    race = {}
    for c, nm in ((178, 'Porch Left'), (260, 'Porch Front'), (331, 'Porch Right'), (380, 'Right')):
        tc = float(np.interp(corner[c], [c80, pd_m - 28], [T_RACE, T_POUNCE]))
        race[c] = tc
        k = K[nm]
        plucks.append((tc, k, corner[c] + 0.12 * lens[k], 0.35, 'race'))
    for i, tb in enumerate(WINGBEATS):
        plucks.append((tb, K['Right'], pd_m, 0.9, 'wing'))
        plucks.append((tb, K['Porch Right'], (lo[K['Porch Right']] + hi[K['Porch Right']]) / 2, 0.6, 'wing'))
        plucks.append((tb + 0.05, K['Porch Front'], pf_mid, 0.35, 'wing'))
    for nm, tp in POPS.items():
        k = K[nm]
        plucks.append((tp, k, lo[k] + 0.15 * lens[k], 0.8, 'pop'))

    # ---- velocity kicks: (time, distance, velocity, width): the moth hitting and struggling, the pounce
    kicks = [(T_HIT, pd_m, 70.0, 8.0)]
    for t0, dur in BURSTS:
        t, sg = t0 + 0.05, 1.0
        while t < t0 + dur:
            kicks.append((t, pd_m + rng.normal(0, 4), sg * rng.uniform(14, 34), 6.0))
            sg = -sg
            t += rng.uniform(0.04, 0.11)
    kicks.append((T_POUNCE, pd_m - 20, 60.0, 8.0))

    # ---- tension: each strand sits a little slack until its first pluck, then tunes up over 1.2 s
    tension = {k: [(0, 0.88)] for k in range(6)}
    for t, k, at, A, kind in plucks:
        if kind == 'tune':
            if t > 60:
                tension[k] += [(T_CODA, tension[k][-1][1]), (T_CODA + 0.05, 0.88)]
            tension[k] += [(t, 0.88), (t + 1.2, 1.0)]
    F = nframes(D)
    tens_f = np.array([[keys(f * DT, tension[k]) for k in range(6)] for f in range(F)])

    # ---- the moth on its way in: wanders along the bridge line from the free end
    def moth_small(t):
        u = (t - T_MOTH) / (T_HIT - T_MOTH)
        base = L + 40 + (pd_m - L - 40) * _ease(u) ** 0.8
        wob = (45 * np.sin(2 * np.pi * 0.7 * t) + 20 * np.sin(2 * np.pi * 1.9 * t + 1)) * np.sin(np.pi * np.clip(u, 0, 1))
        return base + wob

    beads = []                                  # dew: (strand, distance, appears, twinkle freq, phase)
    for lay in lays[:6]:
        k = lay['run']
        nb = int(lens[k] / 26)
        for d in np.sort(rng.uniform(lo[k] + 8, hi[k] - 8, nb)):
            beads.append((k, d, 25.0 + rng.uniform(0, 2.2), rng.uniform(0.3, 1.1), rng.uniform(0, 6.3)))
    motes = (rng.uniform(0, L, 70), rng.uniform(-14, 14, 70), rng.uniform(0.08, 0.3, 70), rng.uniform(0, 6.3, 70))

    return dict(ppd=ppd, L=L, names=names, K=K, corner=corner, cuts=cuts, lo=lo, hi=hi, lens=lens, c0=c0,
                xs=xs, dx=xs[1] - xs[0], rid=rid, pins=pins, lays=lays, anchors=anchors, spider=spider,
                plucks=plucks, kicks=kicks, tens_f=tens_f, pd_m=pd_m, pf_mid=pf_mid, moth_small=moth_small,
                beads=beads, motes=motes, race=race)


def _silk(P, t):
    """Which wave cells carry silk at time t (the sim's view; pops don't move the grid)."""
    xs = P['xs']
    s = np.zeros(len(xs))
    for lay in P['lays']:
        if t < lay['t0'] or t >= lay['gone']:
            continue
        a0, a1 = sorted((lay['a'], _head(lay, t)))
        s[(xs >= a0 - 1e-6) & (xs <= a1 + 1e-6)] = 1.0
    return s


def _simulate(G, P):
    """The wave equation along the roof: u_tt = c(x,t)^2 u_xx - K(x) u - gamma u_t + nu u_xxt.
    Returns displacement per frame (F, cells) and how much of each strand is strung (F, 6)."""
    xs, rid, dx, lo, hi, c0 = P['xs'], P['rid'], P['dx'], P['lo'], P['hi'], P['c0']
    Mc = len(xs)
    F = nframes(D)
    h = DT / SUB
    U = np.zeros((F, Mc), np.float32)
    laid = np.zeros((F, 6))
    Kpin = np.zeros(Mc)
    for i, p in enumerate(P['pins']):
        Kpin[p] = KAPPA * (c0[i] ** 2 + c0[i + 1] ** 2) / 2 / dx
    hk = h * h * Kpin
    nu = NU * h / dx ** 2
    pl, kk = {}, {}
    for ev in P['plucks']:
        pl.setdefault(int(round(ev[0] / DT)), []).append(ev)
    for ev in P['kicks']:
        kk.setdefault(int(round(ev[0] / DT)), []).append(ev)
    runmask = [rid == k for k in range(6)]
    u = np.zeros(Mc)
    up = np.zeros(Mc)
    lap_prev = np.zeros(Mc)
    for f in range(F):
        t = f * DT
        r2 = (c0 * P['tens_f'][f] * h / dx)[rid] ** 2
        silk = _silk(P, t)
        for k in range(6):
            laid[f, k] = silk[runmask[k]].mean()
        gam = GAM + 80 * (1 - silk)
        for _, k, at, A, kind in pl.get(f, ()):
            q = xs
            tri = np.where(q < at, (q - lo[k]) / (at - lo[k]), (hi[k] - q) / (hi[k] - at))
            tri = np.clip(tri, 0, 1) * runmask[k] * silk * A
            u += tri
            up += tri
        for _, at, v, w in kk.get(f, ()):
            up -= v * h * np.exp(-((xs - at) / w) ** 2) * silk
        s, vis, hgt = P['spider'](t)
        s2 = P['spider'](t + DT)[0]
        speed = abs(s2 - s) / DT
        if vis and speed > 20 and s < P['L']:   # her footsteps tremble the strand under her
            up -= (1 if f % 2 else -1) * 9.0 * min(1.0, speed / 400) * h * np.exp(-((xs - s) / 6) ** 2) * silk
        a1 = 1 / (1 + gam * h / 2)
        a2 = 1 - gam * h / 2
        for _ in range(SUB):
            lap = np.empty(Mc)
            lap[1:-1] = u[2:] - 2 * u[1:-1] + u[:-2]
            lap[0] = 0.0
            lap[-1] = 2 * (u[-2] - u[-1])       # the bridge line's end is loose
            un = (2 * u - a2 * up + r2 * lap - hk * u + nu * (lap - lap_prev)) * a1
            un[0] = 0.0                         # Side is tied off at the back
            un *= silk
            lap_prev = lap
            up, u = u, un
        U[f] = u
    return U, laid


def render(G, seed=17):
    P = _plan(G, seed)
    U, _ = _simulate(G, P)
    n = G.N
    F = nframes(D)
    out = np.zeros((F, n, 3))
    ppd, xs, lo, hi, L = P['ppd'], P['xs'], P['lo'], P['hi'], P['L']
    xp = G.pos[G.path, 0]
    rng = np.random.default_rng(seed + 1)
    bk = np.array([b[0] for b in P['beads']])
    bd = np.array([b[1] for b in P['beads']])
    ba = np.array([b[2] for b in P['beads']])
    bf = np.array([b[3] for b in P['beads']])
    bph = np.array([b[4] for b in P['beads']])
    bx = np.interp(bd, ppd, xp)
    first_lay = {lay['run']: lay for lay in P['lays'][:6]}
    m0, mv, mf, mph = P['motes']
    pd_m = P['pd_m']
    bed_tex = rng.uniform(0.85, 1.15, n)
    omega = np.pi * P['c0'][None, :] * P['tens_f'] / P['lens'][None, :]
    omega = omega[:, P['rid']]                    # each cell's fundamental (rad/s), per frame

    for f in range(F):
        t = f * DT
        u = U[f]
        buf = np.zeros((n, 3))

        # night: a dim blue roof with gossamer motes drifting in the moonlight
        bedI = float(keys(t, [(0, 0), (1.8, BED_I), (73.5, BED_I), (D, 0)]))
        endf = 1 - float(smoothstep(73.3, D, t))
        buf += perc(bedI * bed_tex)[:, None] * BED
        mp = (m0 + mv * t) % L
        mI = (0.2 + 0.15 * float(smoothstep(61, 64, t))) * np.clip(np.sin(2 * np.pi * mf * t + mph), 0, 1) ** 4 * (bedI / BED_I)
        mot = (mI[:, None] * np.exp(-((ppd[None, :] - mp[:, None]) / 6) ** 2)).sum(0)
        buf += perc(np.clip(mot, 0, 0.3))[:, None] * MOTE

        # the moonbeam, right to left across the web
        xb = float(np.interp(t, [25.6, 28.6], [760, -760]))
        beam_on = 25.6 <= t <= 28.6
        beam = np.exp(-((xp - xb) / 70) ** 2) if beam_on else np.zeros(n)

        # ... and then it unfolds. It is enormous, and the web behind it goes dark where its wings cover it.
        cover = 0.0
        big = None
        if T_UNFOLD <= t < POPS['Right'] + 1.2:
            cm = pd_m + _shift(t, POPS['Right'])
            R = float(keys(t, [(T_UNFOLD, 12), (T_UNFOLD + 1.6, 400)]))
            fold = sum(np.exp(-((t - tb) / 0.2) ** 2) for tb in WINGBEATS)
            R *= 1 - 0.3 * fold
            d = ppd - cm
            ad = np.abs(d)
            shape = (1 - smoothstep(0.82 * R, R, ad))
            wing = (0.42 + 0.25 * fold) * shape * (0.8 + 0.2 * np.cos(ad / 22))
            body = 0.8 * np.exp(-(d / 16) ** 2)
            eo = float(smoothstep(T_EYES, T_EYES + 0.3, t))
            for tb in (T_BLINK, 58.0):
                eo *= 1 - float(np.exp(-((t - tb) / 0.06) ** 2))
            ring = np.exp(-((ad - 0.55 * R) / 16) ** 2) - 1.2 * np.exp(-((ad - 0.55 * R) / 5) ** 2)
            eyes = eo * 1.0 * np.clip(ring, 0, 1)
            gone = 1 - float(smoothstep(POPS['Right'] + 0.3, POPS['Right'] + 1.2, t))
            on = ppd <= L + 1
            cover = 0.8 * shape * gone * on
            big = (wing * gone * on, body * gone * on, eyes * gone * on, fold * gone)

        # silk strands, each piece where it is (popped pieces stream toward the free end)
        silk = np.zeros(n)
        uv = np.zeros(n)
        av = np.zeros(n)
        vel = (u - U[f - 1]) / DT if f else np.zeros_like(u)
        amp_c = np.sqrt(u * u + (vel / omega[f]) ** 2)
        for lay in P['lays']:
            if t < lay['t0'] or t >= lay['gone']:
                continue
            k = lay['run']
            q = ppd - _shift(t, lay['tpop'])
            a0, a1 = sorted((lay['a'], _head(lay, t)))
            m = (q >= max(lo[k], a0) - 0.5) & (q <= min(hi[k], a1) + 0.5)
            if not m.any():
                continue
            silk[m] = 1.0
            uv[m] = np.interp(q[m], xs, u)
            av[m] = np.interp(q[m], xs, amp_c)
        # brightness follows how hard the strand is ringing there; the colour swings white/violet with the
        # displacement itself, so the vibration shows as colour sliding along the strand, not as flicker
        w = np.tanh(av / 0.55)
        ph = np.clip(uv / (av + 1e-6), -1, 1)
        sI = silk * (SILK_I * (1 + 1.3 * beam) + WAVE_I * w) * endf * (1 - cover)
        cp = np.clip(ph, 0, 1)[:, None]
        cn = np.clip(-ph, 0, 1)[:, None]
        col = SILK + np.minimum(1, 1.6 * w)[:, None] * (cp * (WHITE - SILK) + cn * (VIOLET - SILK))
        buf += perc(sI)[:, None] * col

        # dew beads: catch the moonbeam, shiver when their strand rings
        live = np.zeros(len(bd), bool)
        bpos = np.zeros(len(bd))
        for k, lay in first_lay.items():
            sel = bk == k
            if t < lay['gone']:
                live[sel] = True
                bpos[sel] = bd[sel] + _shift(t, lay['tpop'])
        fade = np.clip((t - ba) / 0.8, 0, 1) * live
        if fade.any():
            ub = np.abs(np.interp(bd, xs, u))
            bb = np.exp(-((bx - xb) / 60) ** 2) if beam_on else 0.0
            bI = fade * (0.12 + 0.8 * bb + 0.1 * np.clip(np.sin(2 * np.pi * bf * t + bph), 0, 1) ** 6
                         + 0.55 * np.tanh(ub / 0.3))
            bI *= bpos < L + 3
            bI *= endf
            dew = (bI[:, None] * np.exp(-((ppd[None, :] - bpos[:, None]) / 3) ** 2)).max(0)
            buf += perc(np.clip(dew * (1 - cover), 0, 1))[:, None] * DEW

        # anchor knots at the corners: flash when tied, flare as energy passes through, pop when torn loose
        knot = np.zeros(n)
        for at, ta, tp in P['anchors']:
            if t < ta or (tp is not None and t > tp + 0.6):
                continue
            ci = int(np.argmin(np.abs(xs - at)))
            flare = float(np.tanh(np.abs(u[max(0, ci - 4):ci + 5]).max() / 0.25))
            if tp is not None and t >= tp:
                kI = 1.1 * np.exp(-(t - tp) / 0.12)
            else:
                kI = 0.32 + 0.8 * np.exp(-(t - ta) / 0.3) + 0.6 * flare
            knot = np.maximum(knot, kI * np.exp(-((ppd - at) / 4) ** 2))
        buf += perc(np.clip(knot * endf, 0, 1.1))[:, None] * KNOT

        # the spider: a hot body with four legs a side that step as she runs
        s, vis, hgt = P['spider'](t)
        if vis:
            s2 = P['spider'](t + DT)[0]
            moving = abs(s2 - s) / DT > 20
            near = 1 - 0.8 * hgt
            d = ppd - s
            jolt = np.exp(-(t - T_FEEL) / 0.35) if t >= T_FEEL else 0.0
            body = 0.95 * near * np.exp(-(d / 5) ** 2)
            legs = np.zeros(n)
            gph = s / 9.0
            for i, off in enumerate((9, 13, 17, 21)):
                for sd in (-1, 1):
                    lv = 0.5 + 0.4 * np.sin(gph + i * np.pi / 2 + (sd > 0) * np.pi) if moving else 0.55
                    lv = lv + 0.6 * jolt
                    legs += lv * near ** 2 * np.exp(-((d - sd * off * (1 + 0.3 * jolt)) / 2.4) ** 2)
            if hgt > 0:                         # her dragline glints at the corner while she is still up high
                legs += 0.25 * hgt * np.exp(-(d / 3) ** 2)
            body, legs = body * endf, legs * endf
            buf += perc(np.clip(body, 0, 1))[:, None] * SPIDER + perc(np.clip(legs, 0, 0.9))[:, None] * LEG
            buf += perc(0.6 * jolt * np.exp(-(d / 6) ** 2))[:, None] * WHITE

        # the moth: small and fluttering on the way in, frantic in the web
        if T_MOTH <= t < T_UNFOLD:
            mpos = P['moth_small'](t) if t < T_HIT else pd_m
            fr = 9.0
            if t >= T_HIT:
                fr = 4.0
                for b0, dur in BURSTS:
                    if b0 <= t < b0 + dur:
                        fr = 17.0
            flap = 0.5 + 0.5 * np.sin(2 * np.pi * fr * t)
            if t >= T_POUNCE:
                flap = 0.3
            wdt = 5 + 7 * flap
            mI = (0.55 + 0.25 * flap) * float(smoothstep(T_MOTH, T_MOTH + 0.6, t))
            buf += perc(mI * np.exp(-((ppd - mpos) / wdt) ** 2))[:, None] * MOTH

        if big is not None:
            wing, body, eyes, fold = big
            buf += perc(wing)[:, None] * WING + perc(body)[:, None] * MOTH + perc(eyes)[:, None] * EYE
            buf += perc(0.16 * fold) * MOTH             # each wingbeat washes over the whole house
        if POPS['Right'] + 0.5 <= t < 65.0:            # flying off into the night beyond the free end
            tt = t - POPS['Right'] - 0.5
            away = np.exp(-tt / 1.6) * (0.5 + 0.5 * np.sin(2 * np.pi * 1.3 * tt) ** 2)
            buf += perc(0.5 * away * np.exp(-((ppd - L) / (30 + 25 * tt)) ** 2))[:, None] * WING

        out[f][G.path] = buf
    return np.clip(out, 0, 1)


# ---- soundtrack ---------------------------------------------------------------------------------------
# The strands are the instrument. Every pluck in render() is a harp note at its strand's pitch, panned to
# where it was plucked; a strand's first pluck bends up from slack into tune exactly as its wave speed does.
# Under the harp each strand also sings a soft glassy tone whose loudness is read straight off the wave
# simulation, so the chord builds as the web is spun, and when the moth struggles you hear the vibration
# pass from strand to strand the way you see it. D minor, 120 BPM for the tune; contrabass pizzicato
# underneath; violin pizzicato for the spider's dash; slide whistles for her line; whooshes for the moth.

def score(M, G):
    from pixelhome.audio import SR, slide, whoosh
    P = _plan(G)
    U, laid = _simulate(G, P)
    F = U.shape[0]
    NS = M.n
    names, lo, hi, L = P['names'], P['lo'], P['hi'], P['L']
    tf = np.arange(F) * DT
    ta = np.arange(NS) / SR
    rng = np.random.default_rng(71)

    for name, gain, rev in (('harp', 0.4, 0.3), ('silk', 0.04, 0.4), ('bass', 0.36, 0.15), ('pizz', 0.3, 0.2),
                            ('bells', 0.5, 0.45), ('fx', 0.22, 0.25), ('perc', 0.35, 0.18), ('moth', 0.22, 0.25),
                            ('air', 0.05, 0.3), ('low', 0.3, 0.3)):
        M.bus(name, gain=gain, reverb=rev)

    harp = M.sampler('Strings/Harp/*.wav')
    bass = M.sampler('Strings/Solo Contrabass/Pizz/*.wav', tune=-12)
    vpz = M.sampler('Strings/Violin Section/Pizz/*.wav', tune=-12)
    glock = M.sampler('Percussion/Glock/*.wav', tune=-12)
    trem = M.sampler('Strings/Cello Section/trem/*.wav', tune=-12)
    bsn = M.sampler('Woodwinds/Bassoon/stac/*.wav', tune=-12)
    click = M.hits('VSCO 1 Percussion/varWood/wood_click_pp_*.wav')
    tri = M.hits('Percussion/Triangle3-Hit_v1_*.wav')
    clave = M.hits('Percussion/Claves1_Hit_v1_*.wav')
    timp = M.hits('Percussion/Timpani/Timpani1_Hit_v1_*.wav')
    bdrum = M.hits('Percussion/BDrumNewhit_v3_*.wav')

    order = np.argsort(G.pd)
    xs_, ds = G.pos[order, 0], G.pd[order]
    x0, x1 = xs_.min(), xs_.max()

    def pan_at(d):
        x = np.interp(np.clip(d, 0, L), ds, xs_)
        return 0.85 * (2 * (x - x0) / (x1 - x0) - 1)

    def put(bus, mono, t, gain=1.0, pan=0.0):
        a = (np.asarray(pan, float) + 1) * np.pi / 4
        M.add(bus, np.vstack([mono * np.cos(a), mono * np.sin(a)]) * np.sqrt(2), t, gain)

    def band(sec, lo_f, hi_f, seed):
        m = max(16, int(sec * SR))
        X = np.fft.rfft(np.random.default_rng(seed).normal(0, 1, m))
        fr = np.fft.rfftfreq(m, 1 / SR)
        X *= np.clip((fr - lo_f * 0.7) / (lo_f * 0.3), 0, 1) * np.clip((hi_f * 1.3 - fr) / (hi_f * 0.3), 0, 1)
        y = np.fft.irfft(X, m)
        return y / (np.abs(y).max() + 1e-9)

    def shift_of(k, t):
        if t >= T_CODA:
            return 0.0
        lay = next(ly for ly in P['lays'] if ly['run'] == k)
        return _shift(t, lay['tpop'])

    # ---- every pluck, as a harp note (first plucks bend up into tune with the strand) -------------------
    for t, k, at, A, kind in sorted(P['plucks']):
        m = MIDI[names[k]]
        vel = int(np.clip(40 + 90 * A, 30, 125))
        y = harp.play(m, vel)
        if kind in ('tune', 'anchor'):
            nn = y.shape[1]
            ratio = np.interp(t + np.arange(nn) / SR, tf, P['tens_f'][:, k])
            idx = np.cumsum(ratio)
            idx = idx[idx < nn - 1]
            y = np.vstack([np.interp(idx, np.arange(nn), y[c]) for c in range(2)])
        g = {'anchor': 0.35, 'race': 0.6, 'wing': 0.7, 'pop': 0.9}.get(kind, 1.0)
        M.add('harp', y, t, g, float(pan_at(at + shift_of(k, t))))
        if kind == 'anchor':                    # tied off: a little tink at the knot
            M.add('perc', tri.play(70), t, 0.35, float(pan_at(at)))
        if kind == 'pop':                       # the anchor tears loose: a twang that sags
            f0 = 440 * 2 ** ((m - 69) / 12)
            put('fx', slide(0.0, 0.4, f0, f0 / 2, 0.5, amp=0.5)[0], t, 0.4, float(pan_at(lo[k])))
            M.add('perc', clave.play(110), t, 0.5, float(pan_at(lo[k])))

    # ---- each strand sings, as loud as the simulation says it is ringing --------------------------------
    for k in range(6):
        cells = P['rid'] == k
        E = np.abs(U[:, cells]).max(1)
        env = np.zeros(F)
        e = 0.0
        for f in range(F):
            e = max(E[f], e * np.exp(-DT / 0.5))
            env[f] = e
        amp_f = 0.9 * np.tanh(env / 0.35) + 0.12 * (laid[:, k] > 0.95) * (P['tens_f'][:, k] > 0.99)
        amp = np.interp(ta, tf, amp_f)
        f0 = 440 * 2 ** ((MIDI[names[k]] - 69) / 12)
        fr = f0 * np.interp(ta, tf, P['tens_f'][:, k]) * (1 + 0.0025 * np.sin(2 * np.pi * 4.6 * ta + k))
        ph = 2 * np.pi * np.cumsum(fr) / SR
        y = (np.sin(ph) + 0.35 * np.sin(2 * ph + 0.3) + 0.12 * np.sin(3 * ph) + 0.4 * np.sin(ph * 1.003)) * amp
        mid = (lo[k] + hi[k]) / 2
        pan_f = np.array([pan_at(mid + shift_of(k, t)) for t in tf])
        put('silk', y, 0.0, 1.0, np.interp(ta, tf, pan_f))

    # ---- the night air: a soft wind that never stops ----------------------------------------------------
    wind = band(D, 180, 900, 5) * (0.6 + 0.4 * np.sin(2 * np.pi * ta[:int(D * SR)] / 9.0))
    wind *= np.clip(ta[:len(wind)] / 3, 0, 1) * np.clip((D - ta[:len(wind)]) / 2, 0, 1)
    put('air', wind, 0.0, 1.0, 0.0)

    # ---- before the web: a hushed low tremolo under the night air
    y = trem.play(int(_n('D2')), 60)
    tt = np.arange(y.shape[1]) / SR
    M.add('low', y * (np.clip(tt / 1.5, 0, 1) * np.clip((6.5 - tt) / 2.5, 0, 1))[None, :], 0.3, 0.5, 0.0)

    # ---- the spider: down her line, scurrying feet, silk drawn out as she spins ------------------------
    for t0 in (2.0, T_CODA):
        p = float(pan_at(P['corner'][178]))
        put('fx', slide(0.0, 0.95, 1300, 420, 1.05, amp=0.5)[0], t0, 0.35, p)
        for j, tb in enumerate((1.0 + 0.275, 1.0 + 0.825, 1.0 + 1.375)):
            sec = 0.3
            put('fx', slide(0.0, 0.14, 420, 560 - 30 * j, sec, amp=0.5)[0] * 0.7 ** j, t0 + tb - 0.14, 0.3, p)
    last_tick = -1.0
    for f in range(F):
        t = f * DT
        s, vis, hgt = P['spider'](t)
        if not vis or s > L:
            continue
        sp = abs(P['spider'](t + DT)[0] - s) / DT
        if sp > 20 and t - last_tick > 0.085:
            M.add('perc', click.play(60, pitch=7), t, 0.18 * min(1.0, sp / 300), float(pan_at(s)))
            last_tick = t
    for lay in P['lays']:                       # silk paying out
        sec = lay['t1'] - lay['t0']
        tt = np.arange(int(sec * SR)) / SR
        hd = np.array([_head(lay, lay['t0'] + x) for x in tt[::480]]).repeat(480)[:len(tt)]
        y = band(sec, 3500, 9000, 11 + int(lay['t0'])) * np.clip(tt / 0.1, 0, 1) * np.clip((sec - tt) / 0.15, 0, 1)
        if lay.get('float'):
            y = band(sec, 500, 3000, 3) * np.sin(np.pi * tt / sec) ** 1.5
        put('fx', y, lay['t0'], 0.12, pan_at(hd))

    # ---- the tune's bass, and dew in the moonbeam -------------------------------------------------------
    for b, nm in enumerate(BASS):
        t = T_TUNE + 4 * b * BEAT
        M.add('bass', bass.play(int(_n(nm)), 100), t, 1.0, 0.0)
        M.add('bass', bass.play(int(_n(nm)) + 7, 70), t + 2 * BEAT, 0.7, 0.0)
    M.add('bass', bass.play(int(_n('D2')), 110), T_TUNE + 32 * BEAT, 1.0, 0.0)
    M.add('bass', bass.play(int(_n('D2')), 80), 72.2, 1.0, 0.0)
    dew_notes = [_n(x) for x in ('A5', 'C6', 'D6', 'E6', 'F6', 'A6')]
    for i, (k, d, appear, fq, ph) in enumerate(P['beads']):
        if i % 3:
            continue
        x = float(np.interp(d, P['ppd'], G.pos[G.path, 0]))
        tg = float(np.interp(x, [-760, 760], [28.6, 25.6]))
        M.add('bells', glock.play(int(dew_notes[int(rng.integers(6))]), int(rng.integers(40, 70)), dur=1.2),
              tg, 0.6, float(pan_at(d)))

    # ---- the moth -----------------------------------------------------------------------------------
    pd_m = P['pd_m']
    sec = T_HIT - T_MOTH
    tt = np.arange(int(sec * SR)) / SR
    mp = np.array([pan_at(P['moth_small'](T_MOTH + x)) for x in tt[::480]]).repeat(480)[:len(tt)]
    flutter = band(sec, 300, 2500, 21) * (0.5 + 0.5 * np.sin(2 * np.pi * 9 * tt)) ** 2 * np.clip(tt / 0.6, 0, 1)
    put('moth', flutter, T_MOTH, 0.8, mp)
    pm = float(pan_at(pd_m))
    M.add('perc', clave.play(115), T_HIT, 0.6, pm)
    put('fx', slide(0.0, 0.25, 900, 300, 0.3, amp=0.5)[0], T_HIT, 0.3, pm)
    for i, (t, at, v, wd) in enumerate(P['kicks'][1:-1]):
        if i % 3 == 0:                          # each hard tug plucks the bridge line
            M.add('harp', harp.play(MIDI['Right'], int(45 + abs(v))), t, 0.6, pm)
    for i, (b0, dur) in enumerate(BURSTS):     # struggling: buzzing wings
        tt = np.arange(int(dur * SR)) / SR
        y = band(dur, 200, 3000, 30 + i) * (0.5 + 0.5 * np.sin(2 * np.pi * 17 * tt)) ** 2
        y *= np.clip(tt / 0.05, 0, 1) * np.clip((dur - tt) / 0.1, 0, 1)
        put('moth', y, b0, 1.0, pm)

    # ---- she feels it, and runs ----------------------------------------------------------------------
    p80 = float(pan_at(P['corner'][80]))
    M.add('pizz', vpz.play(int(_n('A4')), 110), T_FEEL, 1.0, p80)
    M.add('pizz', vpz.play(int(_n('D5')), 120), T_FEEL + 0.12, 1.0, p80)
    scale = [_n(x) for x in ('D4', 'E4', 'F4', 'G4', 'A4', 'Bb4', 'C5', 'D5')]
    t, i = T_RACE, 0
    while t < T_POUNCE - 0.05:
        s = P['spider'](t)[0]
        M.add('pizz', vpz.play(int(scale[i % 8]), int(70 + 45 * (t - T_RACE) / (T_POUNCE - T_RACE))), t, 0.8,
              float(pan_at(s)))
        t += 0.11
        i += 1
    M.add('perc', timp.play(110), T_POUNCE, 0.8, pm)
    M.add('pizz', vpz.play(int(_n('D4')), 120), T_POUNCE, 1.0, pm)
    M.add('pizz', vpz.play(int(_n('A4')), 120), T_POUNCE, 1.0, pm)

    # ---- it unfolds: low tremolo swelling, eyes opening, a blink, and she backs off fast ----------------
    for nm in ('D2', 'A2'):
        y = trem.play(int(_n(nm)), 100)
        tt = np.arange(y.shape[1]) / SR
        y = y * (np.clip(tt / 2.4, 0, 1) ** 2 * np.clip((4.4 - tt) / 0.4, 0, 1))[None, :]
        M.add('low', y, T_UNFOLD, 1.0, pm)
    M.add('low', bsn.play(int(_n('A2')), 110, dur=0.22), T_EYES, 0.9, pm)
    M.add('low', bsn.play(int(_n('D2')), 115, dur=0.5), T_EYES + 0.25, 0.9, pm)
    for tb in (T_BLINK, 58.0):
        M.add('perc', clave.play(80, pitch=-5), tb - 0.05, 0.4, pm)
        M.add('perc', clave.play(80, pitch=-7), tb + 0.05, 0.4, pm)
    put('fx', slide(0.0, 0.7, 500, 1700, 0.8, amp=0.5)[0], T_BACK, 0.3,
        np.linspace(pan_at(pd_m), pan_at(P['pf_mid']), int(0.8 * SR)))
    for i, tb in enumerate(WINGBEATS):
        y = whoosh(0.9, 70, 800, amp=1.0, seed=i)[0]
        put('moth', y, tb - 0.45, 1.6, pm)
        M.add('perc', bdrum.play(100 + 10 * i), tb, 0.7, pm)
        M.add('perc', timp.play(90 + 10 * i, pitch=-3), tb, 0.5, pm)
    # away it goes: wingbeats fading off past the free end
    pe = float(pan_at(L))
    for i in range(5):
        y = whoosh(0.8, 70, 600, amp=1.0, seed=10 + i)[0]
        put('moth', y, POPS['Right'] + 0.5 + i * 0.77, 1.2 * 0.6 ** i, pe)
    # and she rides out on the porch strand
    tp = POPS['Porch Front']
    put('fx', slide(0.0, 1.3, 520, 1500, 1.5, amp=0.5)[0], tp, 0.28,
        np.linspace(pan_at(P['pf_mid']), pe, int(1.5 * SR)))


def _n(name):
    from pixelhome.audio import note
    return note(name)
