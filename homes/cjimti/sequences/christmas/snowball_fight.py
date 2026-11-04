"""Snowball Fight: The Left and Right wings are two snow forts, white blocks with blue gaps, a red-mittened
team behind the Left one and a green-mittened team behind the Right, each with its pennant at the outer end;
the porch is the night sky over the yard. The forts are packed up block by block, and the volleys start:
every snowball leaves a kid's hands, climbs the Porch Left (or Porch Right), hangs over the Porch Front with
the sky lighting under it, drops down the far side and splats in a white burst on the other fort, knocking
out a block, hitting a kid (who flashes and ducks) or falling short in the yard. Knocked-out blocks are
patted back. It escalates: a beat each, two balls that meet over the porch and burst, then rapid fire from
both sides until two kids go down on the same beat. A lull: both sides are out of snow, one feeble lob
plops just past its own fort, the blocks are patted back. The green team slips away off the free end of
Right and comes back pushing a giant snowball that eats their own fort as it rolls, grows up the Porch
Right, stalls at the top and rolls back, takes three heaves to tip over, then thunders down the Porch Left
and along the Left wing; the red team flees down the Side and it bursts on the red fort at the front-left
corner: a white front races out over the whole house and a blizzard blows, gust after gust. The snow
settles, red, white and green stripes march round the roof, and one red kid gets the last word.

Music, 120 bpm in G major: a bouncy march on staccato clarinet and pizzicato strings for the volleys, every
snowball a slide whistle that climbs and falls with its height on the porch and is panned along its flight,
every splat a soft burst of noise (a slapstick and a bassoon "oof" when it hits a kid, a muted drum when it
breaks a block, a low plop when it falls short), wood clicks as blocks are patted back. The tune tightens to
eighths for the escalation and becomes a driving pizzicato ostinato over a snare roll for the rapid fire.
The lull is a flute alone over soft strings. The giant snowball rolls in on a low rumble and a bassoon
ostinato that climbs a semitone a bar; tremolo strings hold their breath at the stall, three brass "hup"
stabs heave it over, a xylophone run falls with it into the crash. The blizzard is shimmering strings,
choir and wind chimes with a whoosh for each gust and the tune slowed down on the horns; the finale plays it
in full on trumpets with sleigh bells, and the last snowball lands on the final chord."""
import numpy as np
from pixelhome.fx import DT, hexc, perc, light, keys, smoothstep, Flicker, nframes

CODE = 'CH11'
TITLE = 'Snowball Fight'
KIND = 'show'
DESCRIPTION = ('Two snow forts, red mittens against green, and the porch is the sky: volleys arc over it and splat '
               'on the other side until a giant snowball rolls the whole roof and bursts in a blizzard.')
VOICEOVER = "Build your fort, pack them tight, and keep your head down: it's a snowball fight!"

RED = hexc('#ff1018')
GREEN = hexc('#08d838')
SNOW = hexc('#d8ecff')
ICE = hexc('#3a78ff')
WHITE = hexc('#ffffff')
SKY = hexc('#0a2490')
NIGHT = hexc('#1030a8')
GLOW = hexc('#9cc8ff')

D = 86.0
SEED = 41
BEAT = 0.5                                        # 120 bpm
BAR = 4 * BEAT


def at(bar, beat=0.0):
    return bar * BAR + beat * BEAT


NL, NR = 10, 12                                    # fort blocks: chunks of the Left and Right wings
KID_L = (80.0, 200.0, 330.0)                       # red kids, distance in from the front-left corner
KID_R = (70.0, 210.0, 370.0)                       # green kids, distance in from the Right corner
T_BUILT = 3.4                                      # the forts are up
T_LULL = at(22)                                    # out of snow
T_FEEBLE = at(23, 2)
T_SLIP = at(26)                                    # the green team slips away off the free end
T_ROLL = at(27)                                    # the giant snowball rolls in
HEAVES = (at(32), at(32, 2), at(33))               # three heaves at the top of the Porch Right
T_TIP = at(33, 0.6)
T_FLEE = at(34, 1)
T_CRASH = at(35)                                   # it bursts on the red fort
GUSTS = ((at(35, 3), 1), (at(36, 3), -1), (at(37, 3), 1), (at(38, 2), -1))
GUST_V = 1100.0
T_FINALE = at(38)
T_LAST = at(41, 2)                                 # one red kid gets the last word
T_BUTTON = at(42)


def geom(G):
    x = G.pd[G.path]
    c = [float((x[i] + x[i + 1]) / 2) for i in (80, 178, 260, 331, 380)]
    return dict(c1=c[0], c2=c[1], c3=c[2], c4=c[3], c5=c[4], L=float(G.length))


def height(g, p):
    """How high a snowball is: the porch sides climb, the Porch Front is the top of the sky."""
    return np.clip(np.interp(p, [g['c2'], g['c3'], g['c4'], g['c5']], [0, 1, 1, 0]), 0, 1)


def ball_at(th, t):
    """Where a thrown snowball is at time(s) t: fast off the hand, slowest at the top of its arc."""
    u = np.clip((np.asarray(t, float) - th['t0']) / (th['t1'] - th['t0']), 0, 1)
    if th['out'] == 'clash':
        e = u ** 0.85
    else:
        e = u + 0.42 * np.sin(2 * np.pi * u) / (2 * np.pi)
    return th['p0'] + (th['p1'] - th['p0']) * e


def throws(g, rng):
    """Every snowball: (throw time, flight in beats, side +1 red / -1 green, thrower, outcome, target)."""
    S = [(at(2), 3, 1, 2, 'wall', 3), (at(3), 3, -1, 0, 'wall', 6), (at(4), 3, 1, 1, 'kid', 1),
         (at(5), 3, -1, 1, 'short', 0.45), (at(6), 3, 1, 0, 'wall', 8), (at(6, 2), 3, -1, 2, 'wall', 2),
         (at(7, 2), 3, 1, 2, 'short', 0.35), (at(8), 3, -1, 0, 'kid', 2), (at(9), 3, 1, 1, 'wall', 5),
         (at(9, 2), 3, -1, 1, 'wall', 7), (at(10), 3, 1, 0, 'wall', 10), (at(10, 2), 3, -1, 2, 'kid', 0),
         (at(11), 3, 1, 2, 'wall', 1), (at(11, 1), 3, -1, 0, 'wall', 4)]
    for k in range(8):                                             # a beat each
        side = 1 if k % 2 == 0 else -1
        out = ('wall', 'wall', 'kid', 'wall', 'short', 'wall', 'kid', 'wall')[k]
        S.append((at(12, k), 2, side, k % 3, out, int(rng.integers(0, NR if side > 0 else NL)) if out == 'wall'
                  else (int(rng.integers(0, 3)) if out == 'kid' else float(rng.uniform(0.25, 0.6)))))
    S += [(at(14), 2, 1, 1, 'clash', 0), (at(14), 2, -1, 1, 'clash', 0)]   # they meet over the porch
    S += [(at(20), 2, 1, 0, 'clash', 0), (at(20), 2, -1, 2, 'clash', 0)]

    def pick(side):
        out = rng.choice(['wall', 'kid', 'short'], p=[0.58, 0.24, 0.18])
        if out == 'wall':
            return out, int(rng.integers(0, NR if side > 0 else NL))
        if out == 'kid':
            return out, int(rng.integers(0, 3))
        return out, float(rng.uniform(0.2, 0.6))
    for b in np.arange(at(14, 2), at(18), 2 * BEAT):               # each side every other beat, interleaved
        for side, off in ((1, 0.0), (-1, BEAT)):
            out, tg = pick(side)
            S.append((b + off, 2, side, int(rng.integers(0, 3)), out, tg))
    for b in np.arange(at(18), at(21, 2), BEAT):                   # rapid fire: both sides every beat
        if abs(b - at(20)) < 1e-6:
            continue
        for side, off in ((1, 0.0), (-1, BEAT / 2)):
            out, tg = pick(side)
            S.append((b + off, 2, side, int(rng.integers(0, 3)), out, tg))
    S += [(at(21, 2), 2, 1, 1, 'kid', 1), (at(21, 2), 2, -1, 1, 'kid', 1)]  # two kids down on the same beat
    S.append((T_FEEBLE, 2, -1, 1, 'plop', 0))
    S.append((T_LAST - 2 * BEAT, 2, 1, 2, 'kid', 0))
    return sorted(S, key=lambda s: s[0])


def kid_pos(g, side, k):
    return g['c1'] + KID_L[k] if side > 0 else g['c5'] + KID_R[k]


def chunk_centres(g):
    wl, wr = (g['c2'] - g['c1']) / NL, (g['L'] - g['c5']) / NR
    return g['c1'] + wl * (np.arange(NL) + 0.5), g['c5'] + wr * (np.arange(NR) + 0.5), wl, wr


def giant_track(g, F):
    """The giant snowball's path distance and radius per frame (NaN outside its roll)."""
    c1, c2, c3, c4, c5, L = (g[k] for k in ('c1', 'c2', 'c3', 'c4', 'c5', 'L'))
    pts = [(T_ROLL, L + 40), (T_ROLL + 3.0, L - 190), (at(30), c5), (at(31), c4 + 110), (at(31, 2.4), c4 + 38),
           (HEAVES[0], c4 + 100), (HEAVES[0] + 0.3, c4 + 58), (HEAVES[1], c4 + 84), (HEAVES[1] + 0.3, c4 + 32),
           (HEAVES[2], c4 + 44), (HEAVES[2] + 0.3, c4 - 8), (T_TIP + 1.2, c3 + 190), (at(34, 0.6), c3),
           (at(34, 2.6), c2), (T_CRASH, c1)]
    t = np.arange(F) * DT
    x = np.interp(t, [p[0] for p in pts], [p[1] for p in pts])
    k = 4
    w = np.exp(-0.5 * (np.arange(-k, k + 1) / 2.0) ** 2)
    w /= w.sum()
    x = np.convolve(np.pad(x, k, mode='edge'), w, 'valid')
    trav = np.clip(L + 40 - x, 0, None)
    trav = np.maximum.accumulate(np.where(t >= T_ROLL, trav, 0))     # it only grows
    r = 9 + 56 * (trav / (L - c1)) ** 0.6
    x[(t < T_ROLL) | (t >= T_CRASH)] = np.nan
    return x, r


def plan(G, seed=SEED):
    """Everything render() and score() share: the snowballs with their paths, block health, the giant ball."""
    rng = np.random.default_rng(seed)
    g = geom(G)
    F = nframes(D)
    cl, cr, wl, wr = chunk_centres(g)
    TH = []
    for t0, beats, side, kid, out, tg in throws(g, rng):
        p0 = kid_pos(g, side, kid)
        if out == 'wall':
            p1 = float((cr if side > 0 else cl)[tg])
        elif out == 'kid':
            p1 = kid_pos(g, -side, tg)
        elif out == 'short':
            p1 = g['c5'] - tg * (g['c5'] - g['c4']) if side > 0 else g['c2'] + tg * (g['c3'] - g['c2'])
        elif out == 'clash':
            p1 = 0.5 * (g['c3'] + g['c4'])
        else:                                                      # plop: barely past its own fort
            p1 = g['c5'] - 70
        TH.append(dict(t0=t0, t1=t0 + beats * BEAT, side=side, kid=kid, out=out, tg=tg, p0=p0, p1=p1))

    # block health: built at the start, broken by hits, patted back later
    t = np.arange(F) * DT
    events = [[] for _ in range(NL + NR)]
    lull = []
    for th in TH:
        if th['out'] == 'wall':
            c = th['tg'] + (NL if th['side'] > 0 else 0)
            events[c].append((th['t1'], 0))
            if th['t1'] < at(14):
                events[c].append((th['t1'] + 2.5 + 0.25 * (c % 3), 1))
            else:
                lull.append(c)
    fixes = []
    seen = []
    for c in lull:
        if c not in seen:
            seen.append(c)
    for j, c in enumerate(seen):                                   # patted back in the lull, a block a half beat
        tf = at(23) + j * BEAT * 0.5 * min(1.0, 14 / max(len(seen), 1))
        events[c].append((tf, 1))
        fixes.append((tf, c))
    early_fixes = [(e[0], c) for c in range(NL + NR) for e in events[c] if e[1] == 1 and e[0] < at(14) + 3]
    H = np.zeros((F, NL + NR))
    for c in range(NL + NR):
        k = c if c < NL else c - NL
        tb = 0.3 + k * (2.6 / (NL if c < NL else NR))
        h = smoothstep(tb, tb + 0.25, t)
        for te, kind in sorted(events[c]):
            if kind == 0:
                h = np.where(t >= te, 0.0, h)
            else:
                h = np.where(t >= te, np.maximum(h, smoothstep(te, te + 0.35, t)), h)
        H[:, c] = h
    gx, gr = giant_track(g, F)
    seen_x = np.where(np.isnan(gx), np.inf, gx)
    eaten = np.minimum.accumulate(np.where(t >= T_ROLL, seen_x, np.inf))
    H[:, NL:] *= (eaten[:, None] > cr[None] - 4)                   # the giant ball packs up the green fort
    H[:, :NL] *= (t < T_CRASH)[:, None]
    builds = [(0.3 + k * (2.6 / NL), cl[k]) for k in range(NL)] + [(0.3 + k * (2.6 / NR), cr[k]) for k in range(NR)]
    return dict(g=g, TH=TH, H=H, cl=cl, cr=cr, wl=wl, wr=wr, gx=gx, gr=gr, fixes=early_fixes + fixes, builds=builds)


def render(G, seed=SEED):
    P = plan(G, seed)
    g, TH, H, cl, cr, wl, wr, gx, gr = (P[k] for k in ('g', 'TH', 'H', 'cl', 'cr', 'wl', 'wr', 'gx', 'gr'))
    c1, c2, c3, c4, c5, L = (g[k] for k in ('c1', 'c2', 'c3', 'c4', 'c5', 'L'))
    rng = np.random.default_rng(seed + 1)
    F = nframes(D)
    out = np.zeros((F, G.N, 3))
    d = G.pd[G.path]
    n = G.N
    side_m, left_m, right_m = d < c1, (d >= c1) & (d < c2), d >= c5
    porch_m = (d >= c2) & (d < c5)
    chunk = np.full(n, -1)
    chunk[left_m] = np.clip(((d[left_m] - c1) / wl).astype(int), 0, NL - 1)
    chunk[right_m] = NL + np.clip(((d[right_m] - c5) / wr).astype(int), 0, NR - 1)
    fort_m = chunk >= 0
    block = np.where(left_m, (d - c1) % 40 < 27, (d - c5) % 40 < 27)
    flake = Flicker(rng, n, 0.2, 0.9)
    star = Flicker(rng, n, 0.3, 1.2)
    hgt = height(g, d)

    # every splat throws flecks of snow
    FT, FP, FV = [], [], []
    for th in TH:
        if th['out'] == 'clash' and th['side'] < 0:
            continue
        m = 26 if th['out'] == 'clash' else 12
        FT += [th['t1']] * m
        FP += [th['p1']] * m
        FV += list(rng.uniform(80, 420 if th['out'] == 'clash' else 300, m) * rng.choice([-1, 1], m))
    FT, FP, FV = np.array(FT), np.array(FP), np.array(FV)

    hits = {(s, k): [th['t1'] for th in TH if th['out'] == 'kid' and th['side'] == -s and th['tg'] == k]
            for s in (1, -1) for k in range(3)}
    pops = {(s, k): [th['t0'] for th in TH if th['side'] == s and th['kid'] == k] for s in (1, -1) for k in range(3)}

    def dot(x, col, lvl, w):
        return light(col, lvl * np.exp(-((d - x) / w) ** 2))

    for f in range(F):
        t = f * DT
        buf = np.zeros((n, 3))
        master = keys(t, [(0, 0), (0.8, 1), (D - 1.4, 1), (D, 0)])
        fin = smoothstep(T_FINALE - 2, T_FINALE + 1, t)            # fresh snow over everything after the blizzard

        # the yard and the sky: a cold night, falling snow sparkling on every run
        buf += light(NIGHT, 0.2 * (side_m | fort_m))
        buf += light(SKY, (0.24 + 0.05 * star(t)) * porch_m)
        buf += light(WHITE, 0.75 * np.clip(star(t) - 1.55, 0, None) * porch_m)
        buf += light(SNOW, 0.8 * np.clip(flake(t) - 1.5, 0, None) * (1 - porch_m))

        # the forts: white blocks, blue gaps, broken blocks dark
        h = H[f][np.clip(chunk, 0, None)] * fort_m
        buf += light(SNOW, np.where(block, 0.45, 0.0) * h * (1 - fin))
        team = np.where(left_m[:, None], RED, GREEN)
        buf += perc(np.where(block, 0.0, 0.2) * h * (1 - fin))[:, None] * team
        buf += light(ICE, np.where(block, 0.0, 0.12) * h * (1 - fin))
        # pennants at the outer ends
        wave = 0.75 + 0.25 * np.sin(2 * np.pi * 1.3 * t)
        if t < T_CRASH:
            buf += dot(c1 + 8, RED, 0.85 * wave * smoothstep(0.2, 1.0, t), 7)
        if t < T_ROLL + 1.0:
            buf += dot(L - 8, GREEN, 0.85 * wave * smoothstep(0.4, 1.2, t), 7)

        # the kids: crouched behind the wall, popping up to throw, flashing and ducking when hit
        for s in (1, -1):
            for k in range(3):
                x0 = kid_pos(g, s, k)
                col = RED if s > 0 else GREEN
                lv = 0.5 * smoothstep(2.8 + 0.4 * k, 3.2 + 0.4 * k, t)
                x = x0
                for tp in pops[(s, k)]:
                    a = t - tp
                    if -0.35 < a < 0.4:
                        lv = max(lv, 1.0 - 0.5 * abs(a + 0.05) / 0.4)
                white = 0.0
                for th_ in hits[(s, k)]:
                    a = t - th_
                    if 0 <= a < 1.6:
                        white = max(white, np.exp(-a / 0.15))
                        lv = min(lv, 0.15 + 0.35 * smoothstep(1.2, 1.6, a))
                if T_LULL + 0.6 < t < T_SLIP:                      # rummaging for snow
                    lv = 0.35 + 0.2 * np.sin(2 * np.pi * (2.2 + 0.3 * k) * t + k)
                if s < 0 and t >= T_SLIP:                          # slip away, then push the giant ball
                    if t < T_ROLL:
                        u = smoothstep(T_SLIP + 0.2 * k, T_SLIP + 1.4 + 0.2 * k, t)
                        x = x0 + (L + 30 - x0) * u
                        lv = 0.45
                    elif t < T_TIP + 0.4:
                        x = gx[f] + gr[f] + 14 + 16 * k
                        push = max([np.exp(-max(0, t - hv) / 0.2) if t >= hv - 0.05 else 0 for hv in HEAVES] + [0])
                        lv = 0.75 + 0.25 * push
                    elif t < T_FINALE:
                        x = c4 + 14 + 16 * k
                        lv = (0.6 + 0.4 * (np.sin(2 * np.pi * 2 * t + k) > 0)) * (1 - smoothstep(T_CRASH, T_CRASH + 0.6, t))
                    else:
                        lv = 0.0
                if s > 0 and t >= T_FLEE - 0.6:                    # the red team sees it coming and runs for the Side
                    if t < T_FLEE:
                        lv = 0.5 + 0.5 * (np.sin(2 * np.pi * 6 * t) > 0)
                    elif t < T_FINALE:
                        u = smoothstep(T_FLEE + 0.05 * k, T_FLEE + 0.8 + 0.05 * k, t)
                        x = x0 + (c1 - 120 - 60 * k - x0) * u
                        lv = 0.9 * (1 - smoothstep(T_CRASH - 0.1, T_CRASH + 0.3, t))
                    else:
                        lv = 0.0
                if lv > 0:
                    buf += dot(x, col, lv, 15) + dot(x, col, 0.5 * lv, 26)
                if white > 0:
                    buf += dot(x, WHITE, white, 12)

        # snowballs in the air, the sky lighting under them
        for th in TH:
            if th['t0'] <= t < th['t1']:
                x = float(ball_at(th, t))
                buf += dot(x, WHITE, 1.0, 9) + dot(x, ICE, 0.6, 22)
                for k in range(1, 9):
                    tk = t - k * DT
                    if tk >= th['t0']:
                        buf += dot(float(ball_at(th, tk)), GLOW, 0.5 * (1 - k / 9), 9)
                hh = float(height(g, x))
                if hh > 0:
                    buf += light(GLOW, 0.22 * hh * porch_m * np.exp(-((d - x) / 220) ** 2))

        # splats: a white burst where it lands, and its flecks
        for th in TH:
            a = t - th['t1']
            if 0 <= a < 0.7 and not (th['out'] == 'clash' and th['side'] < 0):
                big = 1.6 if th['out'] == 'clash' else 1.0
                buf += light(WHITE, big * np.exp(-a / 0.13) * np.exp(-((d - th['p1']) / (14 + 160 * a * big)) ** 2))
                buf += light(GLOW, 0.5 * np.exp(-a / 0.3) * np.exp(-((d - th['p1']) / 45) ** 2))
        if len(FT):
            a = t - FT
            live = (a >= 0) & (a < 0.9)
            if live.any():
                al = a[live]
                xs = FP[live] + FV[live] * 0.35 * (1 - np.exp(-al / 0.35))
                I = np.exp(-al / 0.3)[:, None] * np.exp(-((d[None] - xs[:, None]) / 4.5) ** 2)
                buf += light(SNOW, np.clip(I.sum(0), 0, 1))

        # the giant snowball, rolling: a big white ball with a turning stripe and an icy rim
        if not np.isnan(gx[f]):
            x, r = gx[f], gr[f]
            u = (d - x) / r
            inside = np.clip(1 - u ** 2, 0, 1)
            turn = 0.5 + 0.5 * np.cos(np.pi * u * 1.5 + x / r * 2.0)
            buf += light(SNOW, (0.6 + 0.35 * turn) * inside ** 0.2)
            buf += light(ICE, 0.6 * np.exp(-((np.abs(u) - 1) / 0.18) ** 2))
            buf += light(GLOW, 0.2 * porch_m * float(height(g, x)) * np.exp(-((d - x) / 300) ** 2))

        # the crash: a white front racing out over the whole house, then the blizzard
        if t >= T_CRASH:
            a = t - T_CRASH
            R = 1300 * a
            dist = np.abs(d - c1)
            if a < 2.2:
                buf += light(WHITE, 1.0 * np.exp(-a / 0.6) * np.exp(-((dist - R) / 60) ** 2))
                buf += light(SNOW, 0.75 * np.exp(-a / 0.35) * (dist < R))
            bl = keys(t, [(T_CRASH, 0), (T_CRASH + 0.4, 1), (T_FINALE - 1.5, 0.8), (T_FINALE + 1.5, 0)])
            if bl > 0:
                buf += light(SNOW, bl * (0.3 + 0.75 * np.clip(flake(3 * t) - 0.9, 0, None)))
                for tg_, dr in GUSTS:
                    ag = t - tg_
                    if 0 <= ag < 3.0:
                        front = ag * GUST_V if dr > 0 else L - ag * GUST_V
                        band = np.exp(-((d - front) / 110) ** 2)
                        buf += light(WHITE, 0.75 * bl * band)

        # finale: fresh snow, red, white and green stripes marching round on the beat
        if fin > 0:
            beat = np.exp(-((t - T_FINALE) % BEAT) / 0.18)
            ph = (d - 220 * (t - T_FINALE)) % 160
            stripe = np.select([ph < 40, ph < 80, ph < 120], [0, 1, 2], 3)
            cols = np.array([RED, SNOW, GREEN, SNOW])[stripe]
            lv = fin * (0.5 + 0.25 * beat) * (1 - smoothstep(T_LAST - 0.6, T_LAST, t)) * np.where(stripe % 2, 0.8, 1.0)
            buf += perc(lv)[:, None] * cols
            buf += light(SNOW, 0.3 * fin * smoothstep(T_LAST - 0.6, T_LAST, t))
            if t >= T_LAST - 0.6:                                  # the last word: a red kid pops up on Left, a green one on Right
                buf += dot(kid_pos(g, 1, 2), RED, 0.9, 7) + dot(kid_pos(g, -1, 0), GREEN, 0.9 * (t < T_BUTTON + 0.1) + 0.3, 7)
            if t >= T_BUTTON:
                a = t - T_BUTTON
                buf += light(SNOW, 0.35 * np.exp(-a / 0.8) * np.ones(n))
                stripe_b = np.array([RED, SNOW, GREEN, SNOW])[((d / 40).astype(int)) % 4]
                buf += perc(0.55 * smoothstep(0, 0.3, a))[..., None] * stripe_b
        out[f][G.path] = np.clip(buf, 0, 1) * master
    return out


# ---- music ----
THEME = 'G4 B4 D5 B4 | C5:2 A4:2 | F#4 A4 D5 C5 | B4:2 G4:2 | E4 G4 C5 B4 | A4 F#4 D4 E4 | F#4 A4 C5 A4 | G4:4'
THEME_CH = [('G', 'B', 'D'), ('C', 'E', 'G'), ('D', 'F#', 'A'), ('G', 'B', 'D'), ('C', 'E', 'G'), ('D', 'F#', 'A'),
            ('D', 'F#', 'A', 'C'), ('G', 'B', 'D')]
TIGHT = ('D5:0.5 B4:0.5 D5:0.5 B4:0.5 C5 A4 | B4:0.5 G4:0.5 B4:0.5 G4:0.5 A4 F#4 | '
         'G4:0.5 A4:0.5 B4:0.5 C5:0.5 D5 B4 | A4:0.5 B4:0.5 A4:0.5 G4:0.5 F#4 D4')
TIGHT_CH = [('G', 'B', 'D'), ('E', 'G', 'B'), ('C', 'E', 'G'), ('D', 'F#', 'A')]
RAPID_CH = [('E', 'G', 'B'), ('C', 'E', 'G'), ('D', 'F#', 'A'), ('D', 'F#', 'A', 'C')]
LULL = 'B4:2 A4:2 | G4:4 | E4:2 F#4:2 | D4:4'
LULL_CH = [('E', 'G', 'B'), ('C', 'E', 'G'), ('A', 'C', 'E'), ('D', 'F#', 'A')]
ROLL_ROOTS = ('G2', 'G#2', 'A2', 'A#2')


def phrase(s, t0):
    """'G4 B4:2 r ...' -> [(time, note or None, seconds)] from t0, one beat unless :beats is given."""
    outl, b = [], 0.0
    for tok in s.replace('|', ' ').split():
        nm, _, bt = tok.partition(':')
        bt = float(bt) if bt else 1.0
        outl.append((t0 + b * BEAT, None if nm == 'r' else nm, bt * BEAT))
        b += bt
    return outl


def score(M, G):
    from pixelhome.audio import SR, note, slide, whoosh
    n = note
    P = plan(G)
    g, TH, gx, gr = P['g'], P['TH'], P['gx'], P['gr']
    c1, c4, L = g['c1'], g['c4'], g['L']

    clar = M.sampler('Woodwinds/Clarinet/stac/*.wav', tune=-12)
    flute = M.sampler('Woodwinds/Flute/susvib/*.wav', tune=-12)
    fl_st = M.sampler('Woodwinds/Flute/stac/*.wav', tune=-12)
    bsn = M.sampler('Woodwinds/Bassoon/stac/*.wav', tune=-12)
    cello = M.sampler('Strings/Cello Section/pizzT/*.wav', tune=-12)
    vln_p = M.sampler('Strings/Violin Section/Pizz/*.wav', tune=-12)
    viola = M.sampler('Strings/Viola Section/pizz/*.wav', tune=-12)
    cbass = M.sampler('Strings/Solo Contrabass/Pizz/*.wav', tune=-12)
    vln = M.sampler('Strings/Violin Section/susVib/*.wav', tune=-12)
    vla = M.sampler('Strings/Viola Section/susvib/*.wav', tune=-12)
    vc = M.sampler('Strings/Cello Section/susvib/*.wav', tune=-12)
    trem = M.sampler('Strings/Violin Section/Trem/*.wav', tune=-12)
    horn = M.sampler('Brass/F Horn/sus/*.wav', tune=-12)
    horn_st = M.sampler('Brass/F Horn/stac/*.wav', tune=-12)
    tbn = M.sampler('Brass/Tenor Trombone/stac/*.wav', tune=-12)
    tpt = M.sampler('Brass/Trumpet/stac/*.wav', tune=-12)
    tpt_s = M.sampler('Brass/Trumpet/sus/*.wav', tune=-12)
    tuba = M.sampler('Brass/Tuba/stac/*.wav', tune=-12)
    glock = M.sampler('Percussion/Glock/*.wav', tune=-12)
    xylo = M.sampler('Percussion/Xylo/*.wav', tune=-12)
    harp = M.sampler('Strings/Harp/*.wav')
    choir = M.synth('Pads/Ooh')
    click = M.hits('VSCO 1 Percussion/varWood/wood_click_pp*.wav')
    snare = M.hits('Percussion/Snare2-HitSN_v[35]*.wav')
    snare_soft = M.hits('Percussion/Snare2-HitSN_v1*.wav')
    sroll = M.hits('Percussion/Snare2-rollSN_v5*.wav')
    slap = M.hits('VSCO 1 Percussion/varWood/slapstick[12].wav')
    bd_m = M.hits('VSCO 1 Percussion/drums/bass/bdrum_muted_mf*.wav')
    bd_pp = M.hits('VSCO 1 Percussion/drums/bass/bdrum_muted_pp*.wav')
    bd = M.hits('VSCO 1 Percussion/drums/bass/bdrum_f_*.wav')
    bd_big = M.hits('VSCO 1 Percussion/drums/bass/bdrum_fff_*.wav')
    crash = M.hits('VSCO 1 Percussion/varMetal/Cymbals/clash/crash_hit_ff*.wav')
    crash_mf = M.hits('Percussion/cymbal-crash1_mf*.wav')
    timp = M.hits('Percussion/Timpani/Timpani1_Hit_v[13]*.wav')
    troll = M.hits('Percussion/Timpani/Rolls/Timpani1_Roll_v3*.wav')
    chimes = M.hits('VSCO 1 Percussion/varMetal/various/windchimes_random.wav')
    chimes_up = M.hits('VSCO 1 Percussion/varMetal/various/windchimes_fastAsc1.wav')
    sleigh = M.hits('Percussion/Sleighbells_Hit*.wav')
    sleigh_sh = M.hits('Miscellania Raw/Misc 2/sleighbell*_shake*.wav')

    for name, gain, rev in (('tune', 0.4, 0.15), ('pizz', 0.44, 0.1), ('harm', 0.34, 0.3), ('perc', 0.4, 0.12),
                            ('fx', 0.28, 0.15), ('sparkle', 0.25, 0.3)):
        M.bus(name, gain=gain, reverb=rev)

    order = np.argsort(G.pd)
    xs, ds = G.pos[order, 0], G.pd[order]
    x0, x1 = xs.min(), xs.max()

    def pan_at(dd):
        x = np.interp(np.clip(dd, 0, L), ds, xs)
        return 0.85 * (2 * (x - x0) / (x1 - x0) - 1)

    def mono(sig, pans):
        a = (np.clip(pans, -1, 1) + 1) * np.pi / 4
        return np.vstack([sig * np.cos(a), sig * np.sin(a)]) * np.sqrt(2)

    def chord(names, octave):
        outl, last = [], -1
        for c in names:
            m = n(c + str(octave))
            while m <= last:
                m += 12
            outl.append(m)
            last = m
        return outl

    def pff(seconds=0.35, amp=0.5, bright=0.3, seed=0):        # a soft burst of noise: snow hitting something
        k = int(seconds * SR)
        r = np.random.default_rng(seed)
        x = r.normal(0, 1, k)
        y = np.zeros(k)
        a = 1 - bright
        z = 0.0
        for i in range(0, k):
            z = (1 - a) * x[i] + a * z
            y[i] = z
        tt = np.arange(k) / SR
        env = np.clip(tt / 0.004, 0, 1) * np.exp(-tt / (seconds / 4))
        y = amp * env * y / (np.abs(y).max() + 1e-9)
        return y

    def melody(s, t0, insts, vel=96, short=True):
        for t, m, dur in phrase(s, t0):
            if m is None:
                continue
            for inst, bus, gn, pn, dv in insts:
                d_ = dur * (0.55 if short else 0.95)
                M.add(bus, inst.play(n(m) + dv, vel, dur=d_, release=0.1 if short else 0.3), t, gn, pn)

    def oompah(chs, t0, bars, vel=95, inst=None, gain=0.85):
        inst = inst or cello
        for b in range(bars):
            ch = chs[b % len(chs)]
            root, fifth = n(ch[0] + '2'), n(ch[2 if len(ch) > 2 else 1] + '2')
            if fifth < root:
                fifth += 12
            for k in range(4):
                tb = t0 + b * BAR + k * BEAT
                if k % 2 == 0:
                    M.add('pizz', inst.play(root if k == 0 else fifth - 12 if fifth - 12 >= root - 5 else fifth, vel), tb, gain)
                else:
                    for m in chord(ch[:3], 3):
                        M.add('pizz', viola.play(m, vel - 25), tb, 0.35, 0.2)

    # ---- 0-4: the forts are packed up, block by block ----
    M.add('perc', sleigh_sh.play(80), 0.05, 0.5, -0.2)
    for i, m in enumerate(chord(('G', 'B', 'D'), 3) + chord(('G', 'B', 'D'), 4)):
        M.add('harm', harp.play(m, 75), 0.1 + 0.22 * i, 0.6, -0.5 + 0.18 * i)
    for tb, x in P['builds']:
        M.add('perc', click.play(int(M.rng.integers(70, 95)), pitch=float(M.rng.uniform(-2, 2))), tb, 0.55, pan_at(x))
    for m in ('G3', 'D4', 'B4'):
        M.add('harm', vln.play(n(m), 55, dur=2.2, release=0.5), 1.4, 0.3)
    M.add('perc', timp.play(80, pitch=-2), 3.0, 0.6)
    M.add('perc', sroll.play(70, dur=1.0), 2.0, 0.3)

    # ---- 4-28: the volleys, a bouncy march ----
    for k in range(12):
        t0 = at(2 + k)
        s = THEME.split('|')[k % 8]
        melody(s, t0, [(clar, 'tune', 0.8, -0.15, 0), (fl_st, 'tune', 0.45 if k >= 4 else 0.0, 0.2, 0)])
        if k >= 8:
            melody(s, t0, [(glock, 'sparkle', 0.35, 0.3, 12)])
        oompah([THEME_CH[k % 8]], t0, 1)
        for b in (1, 3):
            M.add('perc', snare_soft.play(70), t0 + b * BEAT, 0.35, 0.1)

    # ---- 28-36: tighter ----
    for k in range(4):
        t0 = at(14 + k)
        melody(TIGHT.split('|')[k], t0, [(clar, 'tune', 0.8, -0.15, 0), (tpt, 'tune', 0.45, 0.15, 0),
                                         (xylo, 'sparkle', 0.35, 0.3, 0)])
        oompah([TIGHT_CH[k]], t0, 1, vel=105)
        for b in range(4):
            M.add('perc', (snare if b % 2 else snare_soft).play(85), t0 + b * BEAT, 0.4, 0.1)
        M.add('perc', bd_m.play(90), t0, 0.6)

    # ---- 36-44: rapid fire: a pizzicato ostinato in eighths over a snare roll ----
    for k in range(4):
        t0 = at(18 + k)
        ch = RAPID_CH[k]
        tones = chord(ch[:3], 4)
        pat = [0, 1, 2, 1, 0, 2, 1, 2]
        for e in range(8):
            M.add('pizz', vln_p.play(tones[pat[e]] + (2 if k == 3 and e >= 4 else 0), 100), t0 + e * BEAT / 2, 0.55,
                  -0.3 if e % 2 else 0.3)
            if e % 2 == 0:
                M.add('pizz', cello.play(n(ch[0] + '2'), 108), t0 + e * BEAT / 2, 0.8)
        for m in chord(ch, 3):
            M.add('harm', horn_st.play(m, 110, dur=0.3), t0, 0.55, -0.2)
            M.add('harm', horn_st.play(m, 100, dur=0.25), t0 + 1.5 * BEAT, 0.45, -0.2)
        M.add('perc', bd.play(100), t0, 0.7)
        melody(['B4:0.5 E5:0.5 r:1 B4:0.5 E5:0.5 r:1', 'C5:0.5 E5:0.5 r:1 C5:0.5 E5:0.5 r:1',
                'D5:0.5 F#5:0.5 r:1 D5:0.5 F#5:0.5 r:1', 'D5:0.5 F#5:0.5 A5:0.5 F#5:0.5 D5:0.5 C5:0.5 A4:0.5 F#4:0.5'][k],
               t0, [(tpt, 'tune', 0.55, 0.1, -12), (clar, 'tune', 0.6, -0.1, 0)])
    r = sroll.play(105, dur=8.0)
    M.add('perc', r * np.linspace(0.15, 1.0, r.shape[1]) ** 1.5, at(18), 0.5, 0.0)
    for m in ('E2', 'B2'):
        M.add('pizz', tuba.play(n(m), 115, dur=0.5), T_LULL, 0.9)
    M.add('perc', bd_big.play(115), T_LULL, 0.8)
    M.add('perc', crash_mf.play(100), T_LULL, 0.5)

    # ---- 44-52: the lull: a flute alone, blocks patted back ----
    melody(LULL, at(22, 1), [(flute, 'tune', 0.7, 0.0, 0)], vel=70, short=False)
    for k, ch in enumerate(LULL_CH):
        for m in chord(ch, 3):
            M.add('harm', vla.play(m, 50, dur=BAR * 0.98, release=0.5), at(22 + k), 0.3, 0.15)
        M.add('pizz', cbass.play(n(ch[0] + '2'), 80), at(22 + k), 0.7)
    for tf, c in P['fixes']:
        x = (P['cl'][c] if c < NL else P['cr'][c - NL])
        for j in range(2):
            M.add('perc', click.play(int(M.rng.integers(65, 90)), pitch=float(M.rng.uniform(-1, 1))), tf + 0.12 * j,
                  0.5, pan_at(x))

    # ---- 52-54: the green team slips away ----
    for j, m in enumerate(('D3', 'E3', 'F#3', 'A3', 'D3', 'E3', 'F#3', 'C4')):
        M.add('tune', bsn.play(n(m), 85, dur=0.15), T_SLIP + j * BEAT / 2, 0.75, pan_at(L - 100 + 20 * j))
        M.add('pizz', viola.play(n(m) + 12, 60), T_SLIP + j * BEAT / 2 + 0.12, 0.4, pan_at(L - 100 + 20 * j))

    # ---- 54-66: the giant snowball: a low rumble and a climbing ostinato ----
    t_arr = np.arange(int((T_CRASH - T_ROLL) * SR)) / SR + T_ROLL
    fr = np.clip(((t_arr - T_ROLL) / DT).astype(int) + int(T_ROLL / DT), 0, len(gx) - 1)
    xr = np.nan_to_num(gx[fr], nan=L)
    rr = gr[fr]
    rng_r = np.random.default_rng(5)
    nz = rng_r.normal(0, 1, len(t_arr))
    rum = np.zeros_like(nz)
    z = 0.0
    a_ = np.exp(-2 * np.pi * 90 / SR)
    for i in range(len(nz)):
        z = (1 - a_) * nz[i] + a_ * z
        rum[i] = z
    rum /= np.abs(rum).max() + 1e-9
    spd = np.abs(np.gradient(xr)) * SR
    lvl = np.clip(rr / 42, 0, 1) * (0.35 + 0.65 * np.clip(spd / 300, 0, 1))
    M.add('fx', mono(1.1 * rum * lvl, pan_at(xr)), T_ROLL, 1.0)
    for k in range(4):                                             # a semitone higher every bar
        t0 = at(27 + k)
        root = n(ROLL_ROOTS[k])
        for e in range(8):
            m = root + (0, 4, 7, 4, 0, 4, 7, 12)[e]
            M.add('tune', bsn.play(m, 100, dur=0.18), t0 + e * BEAT / 2, 0.8, 0.5 * pan_at(xr[min(len(xr) - 1, int((t0 - T_ROLL + e * BEAT / 2) * SR))]))
            if e % 2 == 0:
                M.add('pizz', cello.play(root, 105), t0 + e * BEAT / 2, 0.8)
        M.add('perc', timp.play(80 + 8 * k, pitch=-5 + k), t0, 0.7, pan_at(xr[int((t0 - T_ROLL) * SR)]))
        if k >= 2:
            for m in chord(('C', 'E', 'G'), 4):
                M.add('harm', vln.play(m + k - 1, 60 + 8 * k, dur=BAR, release=0.3), t0, 0.25, 0.1)
    for m in ('B3', 'D#4', 'F#4'):                                 # the stall: strings hold their breath
        M.add('harm', trem.play(n(m), 75, dur=at(32) - at(31), release=0.2), at(31), 0.5, pan_at(c4 + 40))
    M.add('perc', troll.play(70, dur=at(32) - at(31)), at(31), 0.4, pan_at(c4 + 40))
    for j, hv in enumerate(HEAVES):                                # hup! hup! hup!
        for m in chord(('D', 'F#', 'A', 'C'), 3):
            M.add('harm', horn_st.play(m + 2 * j, 115, dur=0.25), hv, 0.6, pan_at(c4 + 60))
            M.add('harm', tbn.play(m - 12 + 2 * j, 110, dur=0.25), hv, 0.5, pan_at(c4 + 60))
        M.add('perc', bd.play(110), hv, 0.75, pan_at(c4 + 60))
        M.add('perc', timp.play(105, pitch=-2 + 2 * j), hv, 0.6, pan_at(c4 + 60))
    tip = slide(0.0, 0.5, 1300, 500, 0.6, 0.35, 0.6)
    M.add('fx', tip, T_TIP, 0.7, pan_at(c4))
    # down it comes: a falling run that speeds up into the crash
    scale = [n(m) for m in ('G5', 'F#5', 'E5', 'D5', 'C5', 'B4', 'A4', 'G4', 'F#4', 'E4', 'D4', 'C4', 'B3', 'A3', 'G3')]
    times = T_TIP + 0.2 + (T_CRASH - T_TIP - 0.3) * (1 - (1 - np.linspace(0, 1, len(scale) * 2)) ** 0.6)
    for j, tj in enumerate(times):
        m = scale[min(j // 2 + (j % 2), len(scale) - 1)]
        fr_j = min(len(gx) - 1, int(tj / DT))
        p = pan_at(gx[fr_j]) if not np.isnan(gx[fr_j]) else pan_at(c1)
        M.add('sparkle', xylo.play(m, 100), tj, 0.6, p)
        M.add('pizz', vln_p.play(m - 12, 95), tj, 0.4, p)
    r = sroll.play(110, dur=T_CRASH - T_TIP)
    M.add('perc', r * np.linspace(0.1, 1.0, r.shape[1]) ** 2, T_TIP, 0.6, pan_at(1100))

    # ---- 70: the crash, and the blizzard ----
    pc = pan_at(c1)
    M.add('perc', crash.play(120), T_CRASH, 0.75, pc * 0.6)
    M.add('perc', bd_big.play(122), T_CRASH, 1.0, pc * 0.5)
    M.add('perc', timp.play(120, pitch=-5), T_CRASH, 0.9, pc)
    M.add('fx', mono(pff(1.2, 0.9, 0.5, 70), np.full(int(1.2 * SR), pc)), T_CRASH, 0.9)
    for m in chord(('G', 'B', 'D'), 3):
        M.add('harm', horn.play(m, 112, dur=1.6, release=0.6), T_CRASH, 0.6, -0.2)
        M.add('tune', tpt_s.play(m + 12, 108, dur=1.2, release=0.5), T_CRASH, 0.4, 0.2)
    M.add('pizz', tuba.play(n('G1') + 12, 118, dur=1.0), T_CRASH, 0.9)
    bl = whoosh(2.2, 300, 4000, 0.9, seed=70)
    M.add('fx', mono(bl[0], np.linspace(pc, 0.85, bl.shape[1])), T_CRASH + 0.05, 0.8)
    for tg_, dr in GUSTS:
        w = whoosh(2.6, 400, 2500, 0.8, seed=int(tg_ * 10))
        M.add('fx', mono(w[0], np.linspace(-0.85 * dr, 0.85 * dr, w.shape[1])), tg_, 0.7)
    M.add('sparkle', chimes.play(95), T_CRASH + 0.4, 0.6, -0.3)
    M.add('sparkle', chimes.play(85), T_CRASH + 3.2, 0.5, 0.4)
    for k, ch in enumerate((('G', 'B', 'D'), ('E', 'G', 'B'), ('C', 'E', 'G'))):
        t0 = T_CRASH + 0.4 + k * BAR
        for m in chord(ch, 4):
            M.add('harm', trem.play(m, 70, dur=BAR, release=0.4), t0, 0.35, 0.15)
        M.add('harm', vc.play(n(ch[0] + '2') + 12, 70, dur=BAR, release=0.4), t0, 0.4, -0.2)
    a = choir.render([(0.0, m, 64, 5.5) for m in chord(('G', 'B', 'D'), 3)], 7.5)
    M.add('harm', a, T_CRASH + 0.6, 0.9)
    melody('G4:2 B4:2 | D5:2 B4:2 | C5:3 D5:1', at(35, 0.8) - 0.4 + BEAT * 0.0, [(horn, 'tune', 0.6, -0.1, 0)], vel=88,
           short=False)

    # ---- 76-84: the finale: the tune in full ----
    for k in range(4):
        t0 = T_FINALE + k * BAR
        s = THEME.split('|')[k]
        melody(s, t0, [(tpt, 'tune', 0.75, 0.1, 0), (clar, 'tune', 0.55, -0.15, 0), (glock, 'sparkle', 0.35, 0.3, 12)],
               vel=108)
        oompah([THEME_CH[k]], t0, 1, vel=108, inst=tuba, gain=0.7)
        for m in chord(THEME_CH[k], 3):
            M.add('harm', horn.play(m, 90, dur=BAR * 0.95, release=0.3), t0, 0.35, -0.25)
        for e in range(8):
            M.add('perc', sleigh.play(105 if e % 2 == 0 else 80), t0 + e * BEAT / 2, 0.45, 0.35 if e % 2 else -0.35)
        for b in (1, 3):
            M.add('perc', snare.play(85), t0 + b * BEAT, 0.4)
    M.add('perc', crash_mf.play(105), T_FINALE, 0.5)

    # every snowball: a whistle that climbs and falls with its height, panned along its flight, and its splat
    for i, th in enumerate(TH):
        dur = th['t1'] - th['t0']
        k = int(dur * SR)
        ta = th['t0'] + np.arange(k) / SR
        p = ball_at(th, ta)
        h = height(g, p)
        f = 560 * 2 ** (1.25 * h + 0.25 * np.arange(k) / k * (th['out'] != 'clash'))
        ph = 2 * np.pi * np.cumsum(f) / SR
        env = np.clip((ta - th['t0']) / 0.03, 0, 1) * np.clip((th['t1'] - ta) / 0.05, 0, 1)
        rapid = at(18) <= th['t0'] < at(22)
        amp = 0.06 if rapid else 0.1
        sig = amp * env * (np.sin(ph) + 0.1 * np.sin(2 * ph))
        M.add('fx', mono(sig, pan_at(p)), th['t0'], 1.0)
        M.add('perc', click.play(55), th['t0'], 0.3, pan_at(th['p0']))
        pl = pan_at(th['p1'])
        if th['out'] == 'clash':
            if th['side'] > 0:
                M.add('perc', crash_mf.play(105), th['t1'], 0.6, pl)
                M.add('fx', mono(pff(0.5, 0.8, 0.5, i), np.full(int(0.5 * SR), pl)), th['t1'], 0.8)
                for j, m in enumerate(chord(('G', 'B', 'D'), 5) + [n('G6')]):
                    M.add('sparkle', glock.play(m - 12, 95), th['t1'] + 0.05 * j, 0.6, pl + 0.15 * (j - 1.5))
            continue
        M.add('fx', mono(pff(0.3, 0.7, 0.35, i), np.full(int(0.3 * SR), pl)), th['t1'], 0.8)
        if th['out'] == 'wall':
            M.add('perc', bd_m.play(95 if not rapid else 80), th['t1'], 0.6, pl)
            M.add('perc', snare_soft.play(80), th['t1'], 0.3, pl)
        elif th['out'] == 'kid':
            M.add('perc', slap.play(90), th['t1'], 0.55, pl)
            M.add('tune', bsn.play(n('D3'), 105, dur=0.12), th['t1'] + 0.05, 0.7, pl)
            M.add('tune', bsn.play(n('A2'), 100, dur=0.25), th['t1'] + 0.17, 0.7, pl)
        elif th['out'] in ('short', 'plop'):
            M.add('perc', bd_pp.play(85), th['t1'], 0.7, pl)
            M.add('pizz', cbass.play(n('G2'), 85), th['t1'], 0.6, pl)
            if th['out'] == 'plop':
                M.add('fx', slide(0.0, 0.7, 900, 300, 0.8, 0.3, 0.7), th['t1'] - 0.75, 0.6, pl)

    # ---- 84: the last word, on the final chord ----
    pb = pan_at(kid_pos(g, -1, 0))
    M.add('perc', crash.play(110), T_BUTTON, 0.6)
    M.add('perc', bd.play(115), T_BUTTON, 0.8)
    for m in chord(('G', 'B', 'D'), 3):
        M.add('harm', horn.play(m, 105, dur=1.4, release=0.6), T_BUTTON, 0.5, -0.2)
        M.add('tune', tpt_s.play(m + 12, 105, dur=1.2, release=0.6), T_BUTTON, 0.45, 0.2)
    M.add('pizz', tuba.play(n('G1') + 12, 115, dur=1.0), T_BUTTON, 0.8)
    M.add('perc', sleigh_sh.play(100), T_BUTTON, 0.5, pb)
    M.add('sparkle', chimes_up.play(90), T_BUTTON + 0.1, 0.5, pb)
